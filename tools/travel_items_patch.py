"""Integrate full reviewed travel notices and ship-item tutorial on0.2.11."""
import argparse,json,re,struct
from elf import ROOT,PATH,Elf
from extract import pack_members
from build import replace_pack,make_iso
from textcodec import encode,decode,controls,parse_table,build_table
from message_pages import pages
from story_layout import pieces,wrap_body,measure
import locations_patch as prior

BASE_SHA='4e7e2167694722265208c9bc0830c50f236bf1bd96098da63670fbc3aa491876'
LANGUAGE=ROOT/'work/translation/en/travel_items.en.json'
LANGUAGE_SHA='534f1b1bad0134c6324732792aab261b8687f3b6e56ea91291b6f2fd42314b66'
digest=prior.digest

def language():
    if digest(LANGUAGE.read_bytes())!=LANGUAGE_SHA:raise ValueError('Travel/items language revision changed')
    d=json.loads(LANGUAGE.read_text('utf8'))
    if d['review']!=dict(accuracy='independent-reviewed',editorial='complete',glossary='complete',proofreading='complete'):raise ValueError('Review incomplete')
    if [(t['table'],len(t['rows'])) for t in d['tables']]!=[('00023_01234',6),('04935_10413',1),('04950_10473',7)]:raise ValueError('Table inventory changed')
    return d

def stage_row(text,widths,profile):
    raw=encode(text);before=pages(raw);out=bytearray();fitting=[]
    for i,p in enumerate(before):
        if not p['flags']&1:out+=raw[p['start']:p['end']];continue
        prefix,body,tail=pieces(raw,p)
        # The existing LFs within one body are display layout. Preserve every
        # native call and its tail while fitting complete approved English.
        wrapped=wrap_body(' '.join(body.splitlines()),widths,profile)
        if body.split()!=wrapped.split():raise ValueError('Travel/items body words changed')
        lines=wrapped.split('\n');sizes=[measure(s,widths,profile) for s in lines]
        if len(lines)>3 or max(sizes,default=0)>504 or sizes[-1]>478 or len(encode(wrapped))>=400:raise ValueError(f'Complete {profile} call{i} requires a larger display: {sizes}')
        out+=prefix+encode(wrapped)+tail
        fitting.append(dict(native_call=i,lines=lines,widths=sizes,prompt_right_px=sizes[-1]+26,body_bytes=len(encode(wrapped)),voice=p['voice']))
    out+=b'\0';after=pages(bytes(out))
    if controls(decode(out))!=controls(text) or len(after)!=len(before):raise ValueError('Travel/items boundaries changed')
    signature=lambda p:{k:v for k,v in p.items() if k not in ('start','end','body')}
    if any(signature(a)!=signature(b) for a,b in zip(before,after)):raise ValueError('Travel/items native context changed')
    return bytes(out),fitting

def patch(data,packs):
    if digest(data)!=BASE_SHA:raise ValueError('Complete0.2.11 baseline changed')
    e=Elf(data);out=bytearray(data);result=dict(packs);changes={};fitting=[];sizes={};translated=[]
    widths=bytes(json.loads((ROOT/'work/output/v0.2.11/build_info.json').read_text('utf8'))['font_widths'])
    for t in language()['tables']:
        pn,mid=map(int,t['table'].split('_'));source=(ROOT/f'work/source/afs/RESOURCE/{pn:05d}.bin').read_bytes();baseline=packs.get(pn,source)
        if digest(source)!=t['source_pack_sha256'] or digest(baseline)!=t['baseline_pack_sha256']:raise ValueError('Travel/items pack baseline changed')
        m=next(m for m in pack_members(source) if m['id']==mid);old=source[m['offset']:m['offset']+m['size']]
        bm=next(m for m in pack_members(baseline) if m['id']==mid)
        if old!=baseline[bm['offset']:bm['offset']+bm['size']] or digest(old)!=t['source_table_sha256']:raise ValueError('Travel/items source table changed')
        rows=parse_table(old)
        for r in t['rows']:
            i=r['id'];original=rows[i]
            if digest(original)!=r['source_sha256'] or controls(decode(original))!=controls(r['en']):raise ValueError('Travel/items source row guard failed')
            rows[i],fit=stage_row(r['en'],widths,t['profile']);before,after=pages(original),pages(rows[i])
            signature=lambda p:{k:v for k,v in p.items() if k not in ('start','end','body')}
            if len(before)!=len(after) or any(signature(a)!=signature(b) for a,b in zip(before,after)):raise ValueError('Original travel/items calls changed')
            fitting.append(dict(table=t['table'],id=i,native_layout=fit));translated.append(t['table']+':'+str(i))
        table=build_table(rows)
        if parse_table(table)!=rows:raise ValueError('Travel/items table rebuild failed')
        result[pn]=replace_pack(baseline,{mid:table})
        va=e.symbol('_pacfileA')['va']+pn*8+4;expected=len(baseline)
        if int.from_bytes(e.at(va,4),'little')!=expected:raise ValueError('Travel/items cached size changed')
        changes[hex(va)]=hex(len(result[pn]));struct.pack_into('<I',out,e.offset(va),len(result[pn]))
        sizes[str(pn)]=dict(before=expected,after=len(result[pn]),member=mid,table_size=len(table),pack_sha256=digest(result[pn]))
    return bytes(out),result,dict(language_sha256=LANGUAGE_SHA,translated_rows=translated,patched_words=changes,resource_packs=sizes,native_layout=fitting,source_rows=14,manual_calls=sum(len(r['native_layout']) for r in fitting))

def inputs():
    data,packs,overlays,report=prior.inputs();data,packs,travel=patch(data,packs)
    return data,packs,overlays,dict(**report,travel_items=travel)

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('version');ap.add_argument('--write',action='store_true');a=ap.parse_args()
    if not re.fullmatch(r'0\.\d+\.\d+',a.version):raise ValueError('Expected0.x.y')
    data,packs,overlays,report=inputs();t=report['travel_items']
    print(json.dumps(dict(version=a.version,elf_sha256=digest(data),rows=t['source_rows'],manual_calls=t['manual_calls'],resource_packs=t['resource_packs']),indent=1))
    if not a.write:print('DRY: no game files/ISO written.');return
    dest=ROOT/'work/output'/('v'+a.version)
    if dest.exists():raise FileExistsError(dest)
    dest.mkdir(parents=True);(dest/'SLPS_250.70').write_bytes(data)
    for n,p in packs.items():(dest/f'{n:05d}.pack').write_bytes(p)
    for n,p in overlays.items():(dest/f'{n:05d}.evemap').write_bytes(p)
    image=dest/('Sunrise Eiyuutan 2 EN v'+a.version+'.iso');make_iso(image,data,packs,overlays)
    info=json.loads((ROOT/'work/output/v0.2.11/build_info.json').read_text('utf8'))
    info.update(version=a.version,based_on='0.2.11',**report,elf_sha256=digest(data),iso_path=str(image),iso_size=image.stat().st_size,in_game_validation='pending consolidated travel/items validation',scope='Complete travel-notice tables and seven-row ship-item tutorial; retains all0.2.11 content and Japanese voices.')
    info['translated_rows']=sorted(set(info['translated_rows'])|set(t['translated_rows']));info.pop('native_validation_report',None)
    (dest/'build_info.json').write_text(json.dumps(info,indent=1)+'\n','utf8');print('WRITE:',image)

if __name__=='__main__':main()
