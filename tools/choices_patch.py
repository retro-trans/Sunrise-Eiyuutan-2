"""Finish separately stored native Yes/No choices after0.2.5 UI validation."""
import argparse,json,re,struct
from elf import ROOT,PATH,Elf
from build import make_iso
import screens_patch as prior

BASE=0x9BB800
LANGUAGE=ROOT/'work/translation/en/choices.en.json'
LANGUAGE_SHA='087ff052bcac94a772d505603a8dd818c0ec920f07571e683bbc32db5ec70914'
BASE_SHA='1de8371f9c17281249123e3007dacd2333ba324ac2e7a9ae68fca7540368f558'
digest=prior.digest

def language():
    if digest(LANGUAGE.read_bytes())!=LANGUAGE_SHA:raise ValueError('Choice language revision changed')
    d=json.loads(LANGUAGE.read_text('utf8'))
    if d['review']!=dict(accuracy='independent-reviewed',editorial='complete',glossary='complete',proofreading='complete'):raise ValueError('Incomplete choice review')
    if len(d['rows'])!=4 or len(d['references'])!=6:raise ValueError('Choice inventory changed')
    return d

def patch(data):
    if digest(data)!=BASE_SHA:raise ValueError('Complete0.2.5 baseline changed')
    e=Elf(data);source=Elf(PATH.read_bytes());out=bytearray(data);payload=bytearray();addresses={};changes={};d=language()
    def allocate(key,text,minimum=8):
        while len(payload)%8:payload.append(0)
        addresses[key]=BASE+len(payload);raw=text.encode('cp932')+b'\0';payload.extend(raw);payload.extend(bytes(max(0,minimum-len(raw))))
    for r in d['rows']:
        raw=source.at(r['va'],r['source_size'])
        if digest(raw)!=r['source_sha256'] or e.at(r['va'],len(raw))!=raw:raise ValueError('Choice source guard failed')
        allocate(r['va'],(' ' if r['left_padding'] else '')+r['en'])
    for target in d['padded_confirmations']:
        r=next(r for r in prior.language()['rows'] if r['va']==target)
        # Native memory-card text starts at x0 behind a4px frame bevel. Add
        # leading whitespace while retaining the complete approved wording.
        allocate(target,' '+r['en'].replace('\n','\n '))
    def word(va,expected,new):
        if int.from_bytes(e.at(va,4),'little')!=expected:raise ValueError(f'Choice reference changed at{va:X}')
        if va in changes and changes[va]!=new:raise ValueError('Choice high-half conflict')
        changes[va]=new
    for r in d['references']:
        address=addresses[r['target']]
        if r['kind']=='pointer':word(r['site'],r['target'],address)
        else:
            word(r['lui'],r['lui_word'],r['lui_word']&0xFFFF0000|((address+0x8000)>>16))
            word(r['site'],r['word'],r['word']&0xFFFF0000|(address&65535))
    for r in prior.language()['references']:
        if r['target'] not in d['padded_confirmations']:continue
        if r['kind']!='code':raise ValueError('Unexpected confirmation pointer')
        old=int.from_bytes(e.at(r['site'],4),'little');address=addresses[r['target']]
        if old>>16!=r['word']>>16:raise ValueError('Confirmation instruction changed')
        word(r['site'],old,old&0xFFFF0000|(address&65535))
        if int.from_bytes(e.at(r['lui'],4),'little')&65535!=(address+0x8000)>>16:raise ValueError('Confirmation signed high changed')
    for va,w in changes.items():struct.pack_into('<I',out,e.offset(va),w)
    i,s=next((i,s) for i,s in enumerate(e.segments) if s[0]==1 and s[2]==0x9A0000)
    typ,off,va,pa,size,mem,flags,alignment=s
    if va+max(size,mem)>BASE or BASE+len(payload)>0x9C0000:raise ValueError('Choice payload collision')
    combined=data[off:off+size]+bytes(BASE-va-size)+payload;position=(len(out)+4095)//4096*4096
    out.extend(bytes(position-len(out)));out.extend(combined)
    phoff=struct.unpack_from('<I',out,28)[0];phsize=struct.unpack_from('<H',out,42)[0]
    struct.pack_into('<8I',out,phoff+i*phsize,typ,position,va,pa,len(combined),len(combined),flags,alignment)
    return bytes(out),dict(language_sha256=LANGUAGE_SHA,payload_va=hex(BASE),payload_size=len(payload),addresses={str(k):hex(v) for k,v in addresses.items()},patched_words={hex(k):hex(v) for k,v in changes.items()},additional_labels=4,padded_confirmations=4,padded_date_formats=1)

def inputs():
    data,packs,overlays,ui=prior.inputs();data,choices=patch(data)
    return data,packs,overlays,dict(screens_ui=ui,choices_ui=choices)

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('version');ap.add_argument('--write',action='store_true');a=ap.parse_args()
    if not re.fullmatch(r'0\.\d+\.\d+',a.version):raise ValueError('Expected0.x.y')
    data,packs,overlays,report=inputs();print(json.dumps(dict(version=a.version,compiled_records=72,help_rows=23,overlay_occurrences=21,elf_sha256=digest(data),choices=report['choices_ui']),indent=1))
    if not a.write:print('DRY: no game files/ISO written.');return
    dest=ROOT/'work/output'/('v'+a.version)
    if dest.exists():raise FileExistsError(dest)
    dest.mkdir(parents=True);(dest/'SLPS_250.70').write_bytes(data)
    for n,p in packs.items():(dest/f'{n:05d}.pack').write_bytes(p)
    for n,p in overlays.items():(dest/f'{n:05d}.evemap').write_bytes(p)
    image=dest/('Sunrise Eiyuutan 2 EN v'+a.version+'.iso');make_iso(image,data,packs,overlays)
    info=json.loads((ROOT/'work/output/v0.2.5/build_info.json').read_text('utf8'))
    info.update(version=a.version,based_on='0.2.5',**report,elf_sha256=digest(data),iso_path=str(image),iso_size=image.stat().st_size,in_game_validation='pending final choice validation',scope='Complete town/save/phase patch plus separate native Yes/No copies and confirmation padding. Retains all0.2.4 content.')
    info.pop('native_validation_report',None)
    (dest/'build_info.json').write_text(json.dumps(info,indent=1)+'\n','utf8');print('WRITE:',image)

if __name__=='__main__':main()
