"""Complete inventoried travel-event and battle-tutorial integration on0.2.12."""
import argparse,json,re,struct
from elf import ROOT,Elf
from extract import pack_members
from build import replace_pack,make_iso
from textcodec import decode,controls,parse_table,build_table
from message_pages import pages
import travel_items_patch as prior

BASE_SHA='266b21d617423b0fc9ee4dd03a1a648d6ad3dc7b978ca06f53f9278349a81bc7'
LANGUAGE=ROOT/'work/translation/en/travel_tutorials.en.json'
LANGUAGE_SHA='ffffa02fc0502fd9512c714a6ada756698a0a1c4f16012008242f60a3f2fbb2f'
digest=prior.digest
EXPECTED=(('04948_10471',42),('04951_10474',21),('05611_01235',4),('05611_01236',1),('05611_01237',7),('05611_01238',2))

stage_row=prior.stage_row

def language():
    if digest(LANGUAGE.read_bytes())!=LANGUAGE_SHA:raise ValueError('Travel/tutorial language revision changed')
    d=json.loads(LANGUAGE.read_text('utf8'))
    if d['review']!=dict(accuracy='independent-reviewed',editorial='complete',glossary='complete',proofreading='complete'):raise ValueError('Review incomplete')
    if tuple((t['table'],len(t['rows'])) for t in d['tables'])!=EXPECTED:raise ValueError('Category inventory changed')
    return d

def patch(data,packs):
    if digest(data)!=BASE_SHA:raise ValueError('Complete0.2.12 baseline changed')
    e=Elf(data);out=bytearray(data);result=dict(packs);fitting=[];translated=[];changes={};sizes={};groups={}
    widths=bytes(json.loads((ROOT/'work/output/v0.2.12/build_info.json').read_text('utf8'))['font_widths'])
    signature=lambda p:{k:v for k,v in p.items() if k not in ('start','end','body')}
    for t in language()['tables']:
        pn,mid=map(int,t['table'].split('_'))
        if pn not in groups:
            source=(ROOT/f'work/source/afs/RESOURCE/{pn:05d}.bin').read_bytes();baseline=packs.get(pn,source)
            groups[pn]=(source,baseline,{})
        source,baseline,replacements=groups[pn]
        if digest(source)!=t['source_pack_sha256'] or digest(baseline)!=t['baseline_pack_sha256']:raise ValueError('Category pack baseline changed')
        m=next(m for m in pack_members(source) if m['id']==mid);old=source[m['offset']:m['offset']+m['size']]
        bm=next(m for m in pack_members(baseline) if m['id']==mid)
        if old!=baseline[bm['offset']:bm['offset']+bm['size']] or digest(old)!=t['source_table_sha256']:raise ValueError('Category source table changed')
        rows=parse_table(old)
        if len(rows)!=len(t['rows']) or [r['id'] for r in t['rows']]!=list(range(len(rows))):raise ValueError('Incomplete category table')
        for r in t['rows']:
            i=r['id'];original=rows[i]
            if digest(original)!=r['source_sha256'] or controls(decode(original))!=controls(r['en']):raise ValueError('Category source row guard failed')
            rows[i],fit=stage_row(r['en'],widths,t['profile']);before,after=pages(original),pages(rows[i])
            if len(before)!=len(after) or list(map(signature,before))!=list(map(signature,after)):raise ValueError('Original category calls changed')
            fitting.append(dict(table=t['table'],id=i,native_layout=fit));translated.append(t['table']+':'+str(i))
        table=build_table(rows)
        if parse_table(table)!=rows or mid in replacements:raise ValueError('Category table rebuild failed')
        replacements[mid]=table
    # Several travel tables share pack5611: rebuild the pack once with every
    # replacement, so later members cannot discard earlier translated tables.
    for pn,(source,baseline,replacements) in groups.items():
        result[pn]=replace_pack(baseline,replacements);va=e.symbol('_pacfileA')['va']+pn*8+4
        if int.from_bytes(e.at(va,4),'little')!=len(baseline):raise ValueError('Category cached size changed')
        changes[hex(va)]=hex(len(result[pn]));struct.pack_into('<I',out,e.offset(va),len(result[pn]))
        sizes[str(pn)]=dict(before=len(baseline),after=len(result[pn]),members=sorted(replacements),pack_sha256=digest(result[pn]))
    return bytes(out),result,dict(language_sha256=LANGUAGE_SHA,translated_rows=translated,patched_words=changes,resource_packs=sizes,native_layout=fitting,source_rows=77,manual_calls=sum(len(r['native_layout']) for r in fitting),category=language()['category'])

def inputs():
    data,packs,overlays,report=prior.inputs();data,packs,category=patch(data,packs)
    return data,packs,overlays,dict(**report,travel_tutorials=category)

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('version');ap.add_argument('--write',action='store_true');a=ap.parse_args()
    if not re.fullmatch(r'0\.\d+\.\d+',a.version):raise ValueError('Expected0.x.y')
    data,packs,overlays,report=inputs();t=report['travel_tutorials']
    print(json.dumps(dict(version=a.version,elf_sha256=digest(data),new_rows=t['source_rows'],new_bodies=t['manual_calls'],resource_packs=t['resource_packs'],category=t['category']),indent=1))
    if not a.write:print('DRY: no game files/ISO written.');return
    dest=ROOT/'work/output'/('v'+a.version)
    if dest.exists():raise FileExistsError(dest)
    dest.mkdir(parents=True);(dest/'SLPS_250.70').write_bytes(data)
    for n,p in packs.items():(dest/f'{n:05d}.pack').write_bytes(p)
    for n,p in overlays.items():(dest/f'{n:05d}.evemap').write_bytes(p)
    image=dest/('Sunrise Eiyuutan 2 EN v'+a.version+'.iso');make_iso(image,data,packs,overlays)
    info=json.loads((ROOT/'work/output/v0.2.12/build_info.json').read_text('utf8'))
    info.update(version=a.version,based_on='0.2.12',**report,elf_sha256=digest(data),iso_path=str(image),iso_size=image.stat().st_size,in_game_validation='pending consolidated category validation',scope='All inventoried travel-event and battle-tutorial tables, retaining complete0.2.12 and Japanese voices.')
    info['translated_rows']=sorted(set(info['translated_rows'])|set(t['translated_rows']));info.pop('native_validation_report',None)
    (dest/'build_info.json').write_text(json.dumps(info,indent=1)+'\n','utf8');print('WRITE:',image)

if __name__=='__main__':main()
