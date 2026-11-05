"""Reviewed compiled battle details, complete unit/item names and item effects."""
import argparse,json,re,struct
from elf import ROOT,PATH,Elf
from build import make_iso
import travel_tutorials_patch as prior

BASE=0x9BC200
BASE_SHA='a1ca6687bb46c8c33c81d8f2e463571f7762c357a35ec10790acddbc33b1bd10'
LANGUAGE=ROOT/'work/translation/en/battle-details.en.json'
LANGUAGE_SHA='216b16c644f0c01e36d4d46edb9de110618da67ea8c6033f0caf07a2aab1f181'
digest=prior.digest

def language():
    if digest(LANGUAGE.read_bytes())!=LANGUAGE_SHA:raise ValueError('Battle language revision changed')
    d=json.loads(LANGUAGE.read_text('utf8'))
    if d['review']!=dict(accuracy='independent-reviewed',editorial='complete',glossary='complete',proofreading='complete'):raise ValueError('Battle review incomplete')
    if len(d['rows'])!=838 or len(d['fields'])!=1986 or len(d['descriptions'])!=81:raise ValueError('Battle category inventory changed')
    return d

def patch(data):
    if digest(data)!=BASE_SHA:raise ValueError('Complete0.2.13 baseline changed')
    e=Elf(data);source=Elf(PATH.read_bytes());out=bytearray(data);d=language();payload=bytearray();strings={};addresses={};changes={};expected={}
    if digest(source.data)!=d['source_elf_sha256']:raise ValueError('Battle original changed')
    for r in d['rows']:
        raw=source.at(r['va'],r['source_size'])
        if digest(raw)!=r['source_sha256'] or e.at(r['va'],len(raw))!=raw or raw[-1:]!=b'\0':raise ValueError('Battle source string changed')
        if raw==r['en'].encode('cp932')+b'\0':strings.setdefault(r['en'],r['va'])
    # Reuse exact, already reviewed speaker names; all other payload is packed
    # bytewise, as native strings and the existing speaker pool are byte-read.
    previous=json.loads((ROOT/'work/output/v0.2.13/build_info.json').read_text('utf8'))
    for r in previous['speaker_names']['records']:
        if not isinstance(r.get('pointer'),str) or not r['pointer'].startswith('0x'):continue
        va=int(r['pointer'],16);raw=r['en'].encode('cp932')+b'\0'
        if e.at(va,len(raw))!=raw:raise ValueError('Reusable speaker text changed')
        strings.setdefault(r['en'],va)
    # batlShipEnd copies27bytes using LD/LHU/LBU before displaying this text.
    finish=next(r for r in d['rows'] if r['va']==0x2225c8)
    raw=finish['en'].encode('cp932')+b'\0'
    if len(raw)>27:raise ValueError('Fixed-copy confirmation exceeded27bytes')
    strings[finish['en']]=BASE;payload.extend(raw+bytes(27-len(raw)))
    def allocate(text):
        if text not in strings:
            strings[text]=BASE+len(payload);payload.extend(text.encode('cp932')+b'\0')
        return strings[text]
    def word(site,old,new):
        if int.from_bytes(e.at(site,4),'little')!=old:raise ValueError('Battle reference guard failed at%08X'%site)
        if site in changes and changes[site]!=new:raise ValueError('Conflicting battle reference')
        expected[site]=old
        if old!=new:changes[site]=new;struct.pack_into('<I',out,e.offset(site),new)
    ui={r['va']:r for r in d['rows'] if 'battle-ui' in r['groups']}
    for va,r in ui.items():addresses[va]=allocate(r['en'])
    for r in d['code']:
        a=addresses[r['target']]
        word(r['lui'],r['lui_word'],r['lui_word']&0xffff0000|((a+0x8000)>>16))
        word(r['site'],r['word'],r['word']&0xffff0000|(a&65535))
    r=d['manual_load'];a=addresses[r['target']];word(r['site'],r['expected'],r['expected']&0xffff0000|(a&65535))
    for r in d['pointers']:word(r['site'],r['target'],addresses[r['target']])
    resolved=[]
    for r in d['fields']:
        a=allocate(r['en']);word(r['site'],r['target'],a)
        resolved.append(dict(table=r['table'],row=r['row'],field=r['field'],site=hex(r['site']),pointer=hex(a),en=r['en']))
    for r in d['geometry']:word(r['site'],r['expected'],r['value'])
    i,s=next((i,s) for i,s in enumerate(e.segments) if s[0]==1 and s[2]==0x9A0000)
    typ,off,va,pa,size,mem,flags,alignment=s
    if va+max(size,mem)>BASE or BASE+len(payload)>0x9C0000:raise ValueError('Battle payload collision: %d bytes'%len(payload))
    combined=data[off:off+size]+bytes(BASE-va-size)+payload;position=(len(out)+4095)//4096*4096
    out.extend(bytes(position-len(out)));out.extend(combined)
    phoff=struct.unpack_from('<I',out,28)[0];phsize=struct.unpack_from('<H',out,42)[0]
    struct.pack_into('<8I',out,phoff+i*phsize,typ,position,va,pa,len(combined),len(combined),flags,alignment)
    return bytes(out),dict(language_sha256=LANGUAGE_SHA,payload_va=hex(BASE),payload_size=len(payload),payload_sha256=digest(payload),addresses={hex(k):hex(v) for k,v in addresses.items()},patched_words={hex(k):hex(v) for k,v in changes.items()},expected_words={hex(k):hex(v) for k,v in expected.items()},resolved_fields=resolved,coverage=d['coverage'],selector_font=[26,26],selector_width=400,mirrored_selector_x=[16,224],description_max_width=504)

def inputs():
    data,packs,overlays,report=prior.inputs();data,battle=patch(data)
    return data,packs,overlays,dict(**report,battle_details=battle)

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('version');ap.add_argument('--write',action='store_true');a=ap.parse_args()
    if not re.fullmatch(r'0\.\d+\.\d+',a.version):raise ValueError('Expected0.x.y')
    data,packs,overlays,report=inputs();r=report['battle_details']
    print(json.dumps(dict(version=a.version,elf_sha256=digest(data),payload_size=r['payload_size'],patched_words=len(r['patched_words']),coverage=r['coverage'],samples=[r['resolved_fields'][i] for i in (0,300,900,1596,1839)]),indent=1))
    if not a.write:print('DRY: no game files/ISO written.');return
    dest=ROOT/'work/output'/('v'+a.version)
    if dest.exists():raise FileExistsError(dest)
    dest.mkdir(parents=True);(dest/'SLPS_250.70').write_bytes(data)
    for n,p in packs.items():(dest/f'{n:05d}.pack').write_bytes(p)
    for n,p in overlays.items():(dest/f'{n:05d}.evemap').write_bytes(p)
    image=dest/('Sunrise Eiyuutan 2 EN v'+a.version+'.iso');make_iso(image,data,packs,overlays)
    info=json.loads((ROOT/'work/output/v0.2.13/build_info.json').read_text('utf8'))
    info.update(version=a.version,based_on='0.2.13',**report,elf_sha256=digest(data),iso_path=str(image),iso_size=image.stat().st_size,in_game_validation='pending consolidated battle-category validation',scope='Complete native battle details and unit/item tables, readable selection menus; retaining complete0.2.13 and Japanese voices.')
    info.pop('native_validation_report',None)
    (dest/'build_info.json').write_text(json.dumps(info,indent=1)+'\n','utf8');print('WRITE:',image)

if __name__=='__main__':main()
