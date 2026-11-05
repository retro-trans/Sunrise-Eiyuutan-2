"""Relocate reviewed destination and Deon location labels on complete0.2.9."""
import argparse,json,re,struct
from elf import ROOT,PATH,Elf
from build import make_iso
import deck_patch as prior

BASE=0x9BBC00
BASE_SHA='96cac4403f4b86e347abdd53b2bd0b87905c4a14147118307b97232475920a5f'
CLOUD_PRIOR=0x9BB0D0
LANGUAGE=ROOT/'work/translation/en/destination.en.json'
LANGUAGE_SHA='b9106a59510722d7a845e809134e6effc47cf99bf125cf8b68a1f33aa64aebc5'
digest=prior.digest

def language():
    if digest(LANGUAGE.read_bytes())!=LANGUAGE_SHA:raise ValueError('Destination language revision changed')
    d=json.loads(LANGUAGE.read_text('utf8'))
    if d['review']!=dict(accuracy='independent-reviewed',editorial='complete',glossary='complete',proofreading='complete'):raise ValueError('Destination review incomplete')
    if [len(d[k]) for k in ('rows','references','overlays')]!=[5,6,9]:raise ValueError('Destination inventory changed')
    return d

def patch(data):
    if digest(data)!=BASE_SHA:raise ValueError('Complete0.2.9 baseline changed')
    e=Elf(data);source=Elf(PATH.read_bytes());out=bytearray(data);payload=bytearray();addresses={};strings={};changes={};d=language()
    def allocate(key,text,minimum):
        if text not in strings:
            while len(payload)%8:payload.append(0)
            strings[text]=BASE+len(payload);raw=text.encode('ascii')+b'\0'
            payload.extend(raw);payload.extend(bytes(max(0,minimum-len(raw))))
        addresses[key]=strings[text]
    if e.at(CLOUD_PRIOR,11)!=b'Cloud City\0':raise ValueError('Earlier approved Cloud City changed')
    strings['Cloud City']=CLOUD_PRIOR
    for r in d['rows']:
        raw=source.at(r['va'],r['source_size'])
        if digest(raw)!=r['source_sha256'] or e.at(r['va'],len(raw))!=raw:raise ValueError('Destination source guard failed')
        allocate(str(r['va']),r['en'],r['source_size'])
    for r in d['overlays']:allocate(r['id'],r['en'],r['source_size'])
    def word(va,expected,new):
        if int.from_bytes(e.at(va,4),'little')!=expected:raise ValueError(f'Destination reference changed at{va:X}')
        if va in changes and changes[va]!=new:raise ValueError('Destination reference conflict')
        changes[va]=new
    for r in d['references']:
        address=addresses[str(r['target'])]
        if r['kind']=='pointer':
            if r['target']==0x221688:
                if r['site'] not in (0x1C10F8,0x1C115C) or int.from_bytes(e.at(r['site'],4),'little')!=CLOUD_PRIOR:raise ValueError('Earlier Cloud City redirect changed')
                continue
            word(r['site'],r['target'],address)
        else:
            word(r['lui'],r['lui_word'],r['lui_word']&0xFFFF0000|((address+0x8000)>>16))
            word(r['site'],r['word'],r['word']&0xFFFF0000|(address&65535))
    for va,w in changes.items():struct.pack_into('<I',out,e.offset(va),w)
    i,s=next((i,s) for i,s in enumerate(e.segments) if s[0]==1 and s[2]==0x9A0000)
    typ,off,va,pa,size,mem,flags,alignment=s
    if va+max(size,mem)>BASE or BASE+len(payload)>0x9C0000:raise ValueError('Destination payload collision')
    combined=data[off:off+size]+bytes(BASE-va-size)+payload;position=(len(out)+4095)//4096*4096
    out.extend(bytes(position-len(out)));out.extend(combined)
    phoff=struct.unpack_from('<I',out,28)[0];phsize=struct.unpack_from('<H',out,42)[0]
    struct.pack_into('<8I',out,phoff+i*phsize,typ,position,va,pa,len(combined),len(combined),flags,alignment)
    return bytes(out),dict(language_sha256=LANGUAGE_SHA,payload_va=hex(BASE),payload_size=len(payload),addresses={str(k):hex(v) for k,v in addresses.items()},patched_words={hex(k):hex(v) for k,v in changes.items()},compiled_labels=5,new_compiled_labels=4,retained_compiled_labels=1,overlay_literals=9,retained_layout='Native picker measures the complete translated names before sizing; native IDs/order/availability unchanged.')

def patch_overlays(previous,addresses):
    result=dict(previous);edits={}
    for r in language()['overlays']:
        n=r['member'];old=(ROOT/f'work/source/afs/EVEMAP/{n:05d}.bin').read_bytes()
        if digest(old)!=r['original_binary_sha256']:raise ValueError('Deon overlay source changed')
        if n in previous and previous[n]!=old:raise ValueError('Unexpected existing Deon overlay edits')
        raw=old[r['offset']:r['offset']+r['source_size']]
        if digest(raw)!=r['source_sha256']:raise ValueError('Deon label source changed')
        out=bytearray(result.get(n,old));expected=0x9E0000+r['offset']
        for site in r['sites']:
            if int.from_bytes(old[site:site+4],'little')!=expected:raise ValueError('Deon pointer guard failed')
            address=int(addresses[r['id']],16);struct.pack_into('<I',out,site,address)
            edits.setdefault(str(n),{})[hex(site)]=hex(address)
        result[n]=bytes(out)
    return result,edits

def inputs():
    data,packs,overlays,report=prior.inputs();data,destination=patch(data)
    overlays,edits=patch_overlays(overlays,destination['addresses']);destination['overlay_patched_words']=edits
    return data,packs,overlays,dict(**report,destination_ui=destination)

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('version');ap.add_argument('--write',action='store_true');a=ap.parse_args()
    if not re.fullmatch(r'0\.\d+\.\d+',a.version):raise ValueError('Expected0.x.y')
    data,packs,overlays,report=inputs();print(json.dumps(dict(version=a.version,elf_sha256=digest(data),**report['destination_ui']),indent=1))
    if not a.write:print('DRY: no game files/ISO written.');return
    dest=ROOT/'work/output'/('v'+a.version)
    if dest.exists():raise FileExistsError(dest)
    dest.mkdir(parents=True);(dest/'SLPS_250.70').write_bytes(data)
    for n,p in packs.items():(dest/f'{n:05d}.pack').write_bytes(p)
    for n,p in overlays.items():(dest/f'{n:05d}.evemap').write_bytes(p)
    image=dest/('Sunrise Eiyuutan 2 EN v'+a.version+'.iso');make_iso(image,data,packs,overlays)
    info=json.loads((ROOT/'work/output/v0.2.9/build_info.json').read_text('utf8'))
    info.update(version=a.version,based_on='0.2.9',**report,elf_sha256=digest(data),iso_path=str(image),iso_size=image.stat().st_size,in_game_validation='pending consolidated destination validation',scope='Destination selector/location names and Deon town/map labels; retains complete0.2.9 and Japanese voices.')
    info['elf_translated_rows']=sorted(set(info['elf_translated_rows'])|{'E%X'%r['va'] for r in language()['rows']})
    info.pop('native_validation_report',None)
    (dest/'build_info.json').write_text(json.dumps(info,indent=1)+'\n','utf8');print('WRITE:',image)

if __name__=='__main__':main()
