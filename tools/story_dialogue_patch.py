"""Integrate complete later story tables on0.2.19, retaining its captioned movies.

Dry run by default. Rebuild every table with new offsets and every containing
resource pack; update the game's cached pack lengths. No runtime code hooks.
"""
import argparse,hashlib,json,re,struct
from elf import ROOT,Elf
from extract import pack_members
from build import replace_pack,make_iso
from textcodec import encode,decode,controls,parse_table,build_table
from message_pages import pages
from story_layout import pieces,measure
from travel_items_patch import stage_row
from iso import records
import movie_patch as prior

BASE_SHA='a7854805f3c9a293e5330bd6543dfe6acd26b614f7fb093cba24356d67c8181d'
LANGUAGE=ROOT/'work/translation/en/story_dialogue.en.json'
LANGUAGE_SHA='dffac7def5204e9487b83a0780f0e5a8e9cbb5526658703286fd998de86ac10f'
digest=lambda b:hashlib.sha256(b).hexdigest()

def language():
    raw=LANGUAGE.read_bytes();d=json.loads(raw)
    if digest(raw)!=LANGUAGE_SHA:raise ValueError('Reviewed story language revision changed')
    if d['review']!=dict(accuracy='independent-reviewed',editorial='complete',glossary='complete',proofreading='complete'):raise ValueError('Story language pipeline incomplete')
    if [t['table']for t in d['tables']]!=[f'{p:05d}_{p+5478:05d}'for p in range(4906,4937)]:raise ValueError('Story category inventory changed')
    return d

def stage_choice(text,source,widths):
    # Function2 consumes a question followed by exactly two option lines. It
    # must not be word-wrapped as ordinary dialogue. Keep the dynamic name and
    # prove the new suffix is no wider than the original for ANY same value.
    raw=encode(text);old=pages(source);new=pages(raw)
    a=next(p for p in old if p['flags']&1);b=next(p for p in new if p['flags']&1)
    before=pieces(source,a)[1].splitlines();after=pieces(raw,b)[1].splitlines()
    token='{C:819782960100}'
    if len(before)!=3 or len(after)!=3 or before[0].count(token)!=1 or after[0].count(token)!=1:raise ValueError('Dynamic choice structure changed')
    suffix=after[0].replace(token,'');old_suffix=before[0].replace(token,'')
    width=measure(suffix,widths);old_width=len(old_suffix)*28
    if width>old_width or after[1:]!=['Yes','No'] or len(b['body'])>=400:raise ValueError('Choice expands beyond original suffix/buffer')
    return raw,[dict(native_call=new.index(b),lines=after,widths=[None,measure('Yes',widths),measure('No',widths)],voice=0,dynamic_name='Original value1; native slot36bytes plus NUL. Absolute caller expansion unverified.',suffix_px=width,original_suffix_px=old_width,profile='Original3-line function2 choice; question suffix no wider for any identical runtime name')]

def patch(data,packs):
    if digest(data)!=BASE_SHA:raise ValueError('Complete0.2.19 baseline changed')
    elf=Elf(data);out=bytearray(data);result=dict(packs);layout=[];translated=[];sizes={};changes={}
    widths=json.loads((ROOT/'work/output/v0.2.19/build_info.json').read_text('utf8'))['font_widths']
    signature=lambda p:{k:v for k,v in p.items()if k not in('start','end','body')}
    for t in language()['tables']:
        pn,mid=map(int,t['table'].split('_'));source=(ROOT/f'work/source/afs/RESOURCE/{pn:05d}.bin').read_bytes();baseline=packs.get(pn,source)
        m=next(m for m in pack_members(source)if m['id']==mid);raw=source[m['offset']:m['offset']+m['size']];rows=parse_table(raw)
        bm=next(m for m in pack_members(baseline)if m['id']==mid)
        if pn!=4935 and baseline[bm['offset']:bm['offset']+bm['size']]!=raw:raise ValueError('Unanticipated preexisting story translation')
        if [r['id']for r in t['rows']]!=list(range(len(rows))):raise ValueError('Incomplete story table')
        for r in t['rows']:
            i=r['id'];old=rows[i]
            if digest(old)!=r['source_sha256']or controls(decode(old))!=controls(r['en']):raise ValueError('Source row/control guard failed')
            if re.search(r'[\u3040-\u30ff\u3400-\u9fff\uff61-\uff9f]',r['en']):raise ValueError('Untranslated Japanese in story export')
            if (pn,i)==(4936,94):rows[i],fit=stage_choice(r['en'],old,widths)
            else:rows[i],fit=stage_row(r['en'],widths,'story')
            before,after=pages(old),pages(rows[i])
            if list(map(signature,before))!=list(map(signature,after)):raise ValueError('Native speaker/voice/function/call changed')
            layout.append(dict(table=t['table'],id=i,native_layout=fit));translated.append(f'{t["table"]}:{i}')
        table=build_table(rows)
        if parse_table(table)!=rows:raise ValueError('Story table rebuild mismatch')
        result[pn]=replace_pack(baseline,{mid:table});va=elf.symbol('_pacfileA')['va']+pn*8+4
        if int.from_bytes(elf.at(va,4),'little')!=len(baseline):raise ValueError('Cached resource size mismatch')
        struct.pack_into('<I',out,elf.offset(va),len(result[pn]));changes[hex(va)]=hex(len(result[pn]))
        sizes[str(pn)]=dict(before=len(baseline),after=len(result[pn]),member=mid,source_table_sha256=digest(raw),table_sha256=digest(table),pack_sha256=digest(result[pn]))
    return bytes(out),result,dict(language_sha256=LANGUAGE_SHA,source_rows=len(translated),manual_calls=sum(len(r['native_layout'])for r in layout),tables=31,translated_rows=translated,resource_packs=sizes,patched_words=changes,native_layout=layout)

def inputs():
    data,packs,overlays,report=prior.inputs();data,packs,story=patch(data,packs)
    return data,packs,overlays,dict(**report,story_dialogue=story)

def retain_movies(image):
    previous=ROOT/'work/output/v0.2.19/Sunrise Eiyuutan 2 EN v0.2.19.iso'
    a=next(r for r in records(previous)if r['path']=='/MOVIE.AFS');b=next(r for r in records(image)if r['path']=='/MOVIE.AFS')
    if a['size']!=b['size']:raise ValueError('Captioned movie archive size changed')
    h=hashlib.sha256()
    with previous.open('rb')as src,image.open('r+b')as dst:
        src.seek(a['lba']*2048);dst.seek(b['lba']*2048);left=a['size']
        while left:
            block=src.read(min(left,4*1024*1024))
            if not block:raise ValueError('Truncated prior movie archive')
            dst.write(block);h.update(block);left-=len(block)
    return dict(based_on='0.2.19',size=a['size'],sha256=h.hexdigest())

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('version');ap.add_argument('--write',action='store_true');a=ap.parse_args()
    if a.version!='0.2.20':raise ValueError('Guarded story package is0.2.20')
    data,packs,overlays,report=inputs();s=report['story_dialogue']
    print(json.dumps(dict(version=a.version,elf_sha256=digest(data),story_rows=s['source_rows'],bodies=s['manual_calls'],packs=s['resource_packs'],samples=language()['tables'][8]['rows'][:2]),indent=1))
    if not a.write:print('DRY: no game files/ISO written.');return
    dest=ROOT/'work/output/v0.2.20';dest.mkdir(exist_ok=False);(dest/'SLPS_250.70').write_bytes(data)
    for n,b in packs.items():(dest/f'{n:05d}.pack').write_bytes(b)
    for n,b in overlays.items():(dest/f'{n:05d}.evemap').write_bytes(b)
    image=dest/'Sunrise Eiyuutan 2 EN v0.2.20.iso';make_iso(image,data,packs,overlays);retained=retain_movies(image)
    info=json.loads((ROOT/'work/output/v0.2.19/build_info.json').read_text('utf8'));info.update(version=a.version,based_on='0.2.19',**report,elf_sha256=digest(data),iso_path=str(image),iso_size=image.stat().st_size,movie_archive_retained=retained,in_game_validation='pending bounded story preview',scope='Complete1135-row later story category4906..4936, retaining all0.2.19 UI, voices, movie captions and ending lyrics.')
    info['translated_rows']=sorted(set(info['translated_rows'])|set(s['translated_rows']))
    for key in('iso_sha256','native_validation_report'):info.pop(key,None)
    (dest/'build_info.json').write_text(json.dumps(info,indent=1)+'\n','utf8');print('WRITE',image)

if __name__=='__main__':main()
