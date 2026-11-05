"""Complete reviewed native location-name tables and map captions on0.2.10."""
import argparse,json,re,struct
from elf import ROOT,PATH,Elf
from build import make_iso
import destination_patch as prior

BASE=0x9BBD00
BASE_SHA='541ad8003ffdb7d7ce9699b48c952126ab0c00c2f0eb6069dfa11840db63262e'
LANGUAGE=ROOT/'work/translation/en/locations.en.json'
LANGUAGE_SHA='75ec997a13693ad15d0c610338ab93b5bc975752389b5b3973b4441d29f4baf8'
digest=prior.digest

def language():
    if digest(LANGUAGE.read_bytes())!=LANGUAGE_SHA:raise ValueError('Location language revision changed')
    d=json.loads(LANGUAGE.read_text('utf8'))
    if d['review']!=dict(accuracy='independent-reviewed',editorial='complete',glossary='complete',proofreading='complete'):raise ValueError('Location review incomplete')
    if len(d['tables'])!=35 or len(d['overlays'])!=262:raise ValueError('Location inventory changed')
    return d

def patch(data):
    if digest(data)!=BASE_SHA:raise ValueError('Complete0.2.10 baseline changed')
    e=Elf(data);source=Elf(PATH.read_bytes());out=bytearray(data);payload=bytearray();d=language();strings=dict(d['reuse']);addresses={};changes={}
    for text,va in strings.items():
        if e.at(va,100).split(b'\0')[0]!=text.encode('ascii'):raise ValueError('Earlier location text changed')
    for r in d['tables']+d['overlays']:
        text=r['en']
        if text not in strings:
            while len(payload)%8:payload.append(0)
            strings[text]=BASE+len(payload);payload.extend(text.encode('ascii')+b'\0')
        addresses[r.get('id',str(r.get('site')))]=strings[text]
    for r in d['tables']:
        raw=source.at(r['va'],r['source_size'])
        if digest(raw)!=r['source_sha256'] or e.at(r['va'],len(raw))!=raw:raise ValueError('Location source changed')
        if int.from_bytes(e.at(r['site'],4),'little')!=r['expected']:raise ValueError('Location table baseline changed')
        address=strings[r['en']]
        if address!=r['expected']:changes[r['site']]=address;struct.pack_into('<I',out,e.offset(r['site']),address)
    i,s=next((i,s) for i,s in enumerate(e.segments) if s[0]==1 and s[2]==0x9A0000)
    typ,off,va,pa,size,mem,flags,alignment=s
    if va+max(size,mem)>BASE or BASE+len(payload)>0x9C0000:raise ValueError('Location payload collision')
    combined=data[off:off+size]+bytes(BASE-va-size)+payload;position=(len(out)+4095)//4096*4096
    out.extend(bytes(position-len(out)));out.extend(combined)
    phoff=struct.unpack_from('<I',out,28)[0];phsize=struct.unpack_from('<H',out,42)[0]
    struct.pack_into('<8I',out,phoff+i*phsize,typ,position,va,pa,len(combined),len(combined),flags,alignment)
    return bytes(out),dict(language_sha256=LANGUAGE_SHA,payload_va=hex(BASE),payload_size=len(payload),addresses={k:hex(v) for k,v in addresses.items()},patched_words={hex(k):hex(v) for k,v in changes.items()},unique_english_labels=len(strings),coverage=d['coverage'])

def patch_overlays(previous,addresses):
    result=dict(previous);edits={};originals={};baselines={}
    for r in language()['overlays']:
        n=r['member']
        if n not in originals:
            originals[n]=(ROOT/f'work/source/afs/EVEMAP/{n:05d}.bin').read_bytes();baselines[n]=previous.get(n,originals[n])
        old=originals[n];baseline=baselines[n]
        if digest(old)!=r['original_binary_sha256'] or digest(baseline)!=r['baseline_sha256']:raise ValueError('Location overlay baseline changed')
        if digest(old[r['offset']:r['offset']+r['source_size']])!=r['source_sha256']:raise ValueError('Location overlay source changed')
        out=bytearray(result.get(n,baseline));address=int(addresses[r['id']],16)
        def word(site,expected,value):
            if int.from_bytes(baseline[site:site+4],'little')!=expected:raise ValueError('Location reference guard failed')
            if value!=expected:
                struct.pack_into('<I',out,site,value);edits.setdefault(str(n),{})[hex(site)]=hex(value)
        for site in r['sites']:
            if int.from_bytes(old[site:site+4],'little')!=0x9E0000+r['offset']:raise ValueError('Location original pointer changed')
            word(site,r['expected_words'][str(site)],address)
        for c in r['code']:
            word(c['lui'],c['lui_word'],c['lui_word']&0xFFFF0000|((address+0x8000)>>16))
            word(c['site'],c['word'],c['word']&0xFFFF0000|(address&65535))
        result[n]=bytes(out)
    return result,edits

def inputs():
    data,packs,overlays,report=prior.inputs();data,locations=patch(data)
    overlays,edits=patch_overlays(overlays,locations['addresses']);locations['overlay_patched_words']=edits
    return data,packs,overlays,dict(**report,locations_ui=locations)

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('version');ap.add_argument('--write',action='store_true');a=ap.parse_args()
    if not re.fullmatch(r'0\.\d+\.\d+',a.version):raise ValueError('Expected0.x.y')
    data,packs,overlays,report=inputs();r=report['locations_ui']
    print(json.dumps(dict(version=a.version,elf_sha256=digest(data),payload_size=r['payload_size'],unique_english_labels=r['unique_english_labels'],new_elf_words=len(r['patched_words']),new_overlay_words=sum(map(len,r['overlay_patched_words'].values())),coverage=r['coverage']),indent=1))
    if not a.write:print('DRY: no game files/ISO written.');return
    dest=ROOT/'work/output'/('v'+a.version)
    if dest.exists():raise FileExistsError(dest)
    dest.mkdir(parents=True);(dest/'SLPS_250.70').write_bytes(data)
    for n,p in packs.items():(dest/f'{n:05d}.pack').write_bytes(p)
    for n,p in overlays.items():(dest/f'{n:05d}.evemap').write_bytes(p)
    image=dest/('Sunrise Eiyuutan 2 EN v'+a.version+'.iso');make_iso(image,data,packs,overlays)
    info=json.loads((ROOT/'work/output/v0.2.10/build_info.json').read_text('utf8'))
    info.update(version=a.version,based_on='0.2.10',**report,elf_sha256=digest(data),iso_path=str(image),iso_size=image.stat().st_size,in_game_validation='pending consolidated locations validation',scope='All reviewed native town/region tables, local areas, destination and world-map location labels. Retains complete0.2.10 and Japanese voices.')
    info['elf_translated_rows']=sorted(set(info['elf_translated_rows'])|{'E%X'%r['va'] for r in language()['tables']})
    info.pop('native_validation_report',None)
    (dest/'build_info.json').write_text(json.dumps(info,indent=1)+'\n','utf8');print('WRITE:',image)

if __name__=='__main__':main()
