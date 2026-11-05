"""Reviewed modification, combination, recovery and information menus/parts."""
import argparse,json,re,struct
from elf import ROOT,PATH,Elf
from build import make_iso
import formation_patch as prior
import vwf

BASE=0x9A5000
LIMIT=STATS_FONT=0x9A7800
BASE_SHA='5cfa3c2a2278d496cfabb94db30c9c37330cb58037b00da8ca807d0d297f94dd'
LANGUAGE=ROOT/'work/translation/en/services.en.json'
LANGUAGE_SHA='3c9741480311c5ab5bab474bc31b6f5b463bc8448b663441fdf84d9f0eb795ee'
digest=prior.digest

def language():
    if digest(LANGUAGE.read_bytes())!=LANGUAGE_SHA:raise ValueError('Services language revision changed')
    d=json.loads(LANGUAGE.read_text('utf8'))
    if len(d['rows'])!=193 or d['review']!=dict(accuracy='independent-reviewed',editorial='complete',glossary='complete',proofreading='complete'):raise ValueError('Services review/inventory incomplete')
    return d

def patch(data):
    if digest(data)!=BASE_SHA:raise ValueError('Complete0.2.15 baseline changed')
    e=Elf(data);src=Elf(PATH.read_bytes());out=bytearray(data);d=language();payload=bytearray();strings={};addresses={};changes={};expected={}
    # This gap is inside the existing reserved/file-backed evefunc image. The
    # complete VWF helpers end at9A4200; the input monitor starts at9A8000.
    if vwf.BASE+len(vwf.patches(src.data)[0])>BASE or STATS_FONT+16>vwf.MONITOR:raise ValueError('Services reserved-range collision')
    if e.at(BASE,STATS_FONT+16-BASE)!=bytes(STATS_FONT+16-BASE):raise ValueError('Services reserved gap is not empty')
    if digest(src.data)!=d['source_elf_sha256']:raise ValueError('Services source changed')
    for r in d['rows']:
        raw=src.at(r['va'],r['source_size'])
        if digest(raw)!=r['source_sha256']or e.at(r['va'],len(raw))!=raw or raw[-1:]!=b'\0':raise ValueError('Services original text changed')
        if r['en']not in strings:strings[r['en']]=BASE+len(payload);payload.extend(r['en'].encode('cp932')+b'\0')
        addresses[r['va']]=strings[r['en']]
    if BASE+len(payload)>LIMIT:raise ValueError('Services payload exceeds reserved gap')
    out[e.offset(BASE):e.offset(BASE)+len(payload)]=payload
    def word(site,old,new):
        if int.from_bytes(e.at(site,4),'little')!=old:raise ValueError('Services word guard failed at%08X'%site)
        expected[site]=old
        if site in changes and changes[site]!=new:raise ValueError('Conflicting services word')
        if old!=new:changes[site]=new;struct.pack_into('<I',out,e.offset(site),new)
    for r in d['code']:
        a=addresses[r['target']]
        word(r['lui'],r['lui_word'],r['lui_word']&0xffff0000|((a+0x8000)>>16))
        word(r['site'],r['word'],r['word']&0xffff0000|(a&65535))
    for r in d['pointers']:word(r['site'],r['target'],addresses[r['target']])
    resolved=[]
    for r in d['parts']['fields']:
        a=addresses[r['target']];word(r['site'],r['target'],a)
        resolved.append(dict(record=r['record'],offset=r['offset'],site=hex(r['site']),pointer=hex(a),en=next(x['en']for x in d['rows']if x['va']==r['target'])))
    # The before/after panels each have292px. Keep both complete runtime
    # attributes with a22x26 font only on their HP row; all other rows retain
    # their original fonts and positions. Tail dispatch preserves caller RA.
    stub=struct.pack('<4I',0x24080016,0x2409001A,0x08000000|(0x110EA0>>2),0x0000502D)
    out[e.offset(STATS_FONT):e.offset(STATS_FONT)+len(stub)]=stub
    word(0x16A118,0x0C000000|(0x110E98>>2),0x0C000000|(STATS_FONT>>2))
    return bytes(out),dict(language_sha256=LANGUAGE_SHA,payload_va=hex(BASE),payload_size=len(payload),payload_sha256=digest(payload),stats_font_stub_va=hex(STATS_FONT),stats_font_stub_size=len(stub),stats_font_stub_sha256=digest(stub),addresses={hex(k):hex(v)for k,v in addresses.items()},patched_words={hex(k):hex(v)for k,v in changes.items()},expected_words={hex(k):hex(v)for k,v in expected.items()},resolved_fields=resolved,coverage=d['coverage'],reference_method=d['reference_method'],stats_font=[22,26],stats_width=292)

def inputs():
    data,packs,overlays,report=prior.inputs();data,services=patch(data)
    return data,packs,overlays,dict(**report,services_ui=services)

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('version');ap.add_argument('--write',action='store_true');a=ap.parse_args()
    if not re.fullmatch(r'0\.\d+\.\d+',a.version):raise ValueError('Expected0.x.y')
    data,packs,overlays,report=inputs();r=report['services_ui']
    print(json.dumps(dict(version=a.version,elf_sha256=digest(data),payload_bytes=r['payload_size'],patched_words=len(r['patched_words']),coverage=r['coverage'],sample={k:r['addresses'][k]for k in('0x221778','0x2220a8','0x231230','0x231280','0x231e48')}),indent=1))
    if not a.write:print('DRY: no game files/ISO written.');return
    dest=ROOT/'work/output'/('v'+a.version)
    if dest.exists():raise FileExistsError(dest)
    dest.mkdir(parents=True);(dest/'SLPS_250.70').write_bytes(data)
    for n,p in packs.items():(dest/f'{n:05d}.pack').write_bytes(p)
    for n,p in overlays.items():(dest/f'{n:05d}.evemap').write_bytes(p)
    image=dest/('Sunrise Eiyuutan 2 EN v'+a.version+'.iso');make_iso(image,data,packs,overlays)
    info=json.loads((ROOT/'work/output/v0.2.15/build_info.json').read_text('utf8'))
    info.update(version=a.version,based_on='0.2.15',**report,elf_sha256=digest(data),iso_path=str(image),iso_size=image.stat().st_size,in_game_validation='pending consolidated service validation',scope='Compiled modification, combination/separation, recovery and information UI plus all native modification-part records, retaining complete0.2.15 and Japanese voices.')
    info.pop('native_validation_report',None);info.pop('iso_sha256',None);(dest/'build_info.json').write_text(json.dumps(info,indent=1)+'\n','utf8');print('WRITE:',image)

if __name__=='__main__':main()
