"""Relocate reviewed Options UI labels and widen the five-grade speed selector."""
import argparse,json,re,struct
from elf import ROOT,PATH,Elf
from build import make_iso
import mc_font_patch as prior

BASE=0x9BBA00
BASE_SHA='496a2055dec53b1778192c821dc824e954e3432f1283712dbf90b00b3e85e0af'
LANGUAGE=ROOT/'work/translation/en/options.en.json'
LANGUAGE_SHA='69938cea96ad6bd6675441789245e0c42b66b1c06ed525f1cb3da01aa4f69060'
GEOMETRY={0x13EC64:(0x24080108,0x240800E0),0x13EC74:(0x240A0070,0x240A00C0),
          0x13EC84:(0x24170070,0x241700C0),0x13ECD0:(0x24160038,0x24160060)}
digest=prior.digest

def language():
    if digest(LANGUAGE.read_bytes())!=LANGUAGE_SHA:raise ValueError('Options language revision changed')
    d=json.loads(LANGUAGE.read_text('utf8'))
    if d['review']!=dict(accuracy='independent-reviewed',editorial='complete',glossary='complete',proofreading='complete'):raise ValueError('Options review incomplete')
    if len(d['rows'])!=12 or len(d['references'])!=12:raise ValueError('Options inventory changed')
    return d

def patch(data):
    if digest(data)!=BASE_SHA:raise ValueError('Complete0.2.7 baseline changed')
    e=Elf(data);source=Elf(PATH.read_bytes());out=bytearray(data);payload=bytearray();addresses={};changes={};d=language()
    for r in d['rows']:
        raw=source.at(r['va'],r['source_size'])
        if digest(raw)!=r['source_sha256'] or e.at(r['va'],len(raw))!=raw:raise ValueError('Options source guard failed')
        while len(payload)%8:payload.append(0)
        addresses[r['va']]=BASE+len(payload);raw=r['en'].encode('ascii')+b'\0'
        payload.extend(raw);payload.extend(bytes(max(0,r['source_size']-len(raw))))
    def word(va,expected,new):
        if int.from_bytes(e.at(va,4),'little')!=expected:raise ValueError(f'Options reference changed at{va:X}')
        if va in changes and changes[va]!=new:raise ValueError('Options reference conflict')
        changes[va]=new
    for r in d['references']:
        address=addresses[r['target']]
        if r['kind']=='pointer':word(r['site'],r['target'],address)
        else:
            # Heading low half is the call delay slot, using this exact LUI.
            word(r['lui'],r['lui_word'],r['lui_word']&0xFFFF0000|((address+0x8000)>>16))
            word(r['site'],r['word'],r['word']&0xFFFF0000|(address&65535))
    for va,(old,new) in GEOMETRY.items():word(va,old,new)
    for va,w in changes.items():struct.pack_into('<I',out,e.offset(va),w)
    i,s=next((i,s) for i,s in enumerate(e.segments) if s[0]==1 and s[2]==0x9A0000)
    typ,off,va,pa,size,mem,flags,alignment=s
    if va+max(size,mem)>BASE or BASE+len(payload)>0x9C0000:raise ValueError('Options payload collision')
    combined=data[off:off+size]+bytes(BASE-va-size)+payload;position=(len(out)+4095)//4096*4096
    out.extend(bytes(position-len(out)));out.extend(combined)
    phoff=struct.unpack_from('<I',out,28)[0];phsize=struct.unpack_from('<H',out,42)[0]
    struct.pack_into('<8I',out,phoff+i*phsize,typ,position,va,pa,len(combined),len(combined),flags,alignment)
    return bytes(out),dict(language_sha256=LANGUAGE_SHA,payload_va=hex(BASE),payload_size=len(payload),addresses={str(k):hex(v) for k,v in addresses.items()},patched_words={hex(k):hex(v) for k,v in changes.items()},additional_labels=12,speed_popup=dict(x=224,width=192,center=320,choices=5),retained_exit='Complete reviewed exit/unsaved warnings and Yes/No retained from0.2.7')

def inputs():
    data,packs,overlays,report=prior.inputs();data,options=patch(data)
    return data,packs,overlays,dict(**report,options_ui=options)

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('version');ap.add_argument('--write',action='store_true');a=ap.parse_args()
    if not re.fullmatch(r'0\.\d+\.\d+',a.version):raise ValueError('Expected0.x.y')
    data,packs,overlays,report=inputs();print(json.dumps(dict(version=a.version,elf_sha256=digest(data),**report['options_ui']),indent=1))
    if not a.write:print('DRY: no game files/ISO written.');return
    dest=ROOT/'work/output'/('v'+a.version)
    if dest.exists():raise FileExistsError(dest)
    dest.mkdir(parents=True);(dest/'SLPS_250.70').write_bytes(data)
    for n,p in packs.items():(dest/f'{n:05d}.pack').write_bytes(p)
    for n,p in overlays.items():(dest/f'{n:05d}.evemap').write_bytes(p)
    image=dest/('Sunrise Eiyuutan 2 EN v'+a.version+'.iso');make_iso(image,data,packs,overlays)
    info=json.loads((ROOT/'work/output/v0.2.7/build_info.json').read_text('utf8'))
    info.update(version=a.version,based_on='0.2.7',**report,elf_sha256=digest(data),iso_path=str(image),iso_size=image.stat().st_size,in_game_validation='pending consolidated final Options/exit check',scope='Twelve Options labels plus wider speed popup; retains complete0.2.7 translations and Japanese voices.')
    info['elf_translated_rows']=sorted(set(info['elf_translated_rows'])|{'E%X'%r['va'] for r in language()['rows']})
    info.pop('native_validation_report',None)
    (dest/'build_info.json').write_text(json.dumps(info,indent=1)+'\n','utf8');print('WRITE:',image)

if __name__=='__main__':main()
