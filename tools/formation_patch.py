"""Complete reviewed squad-formation UI on the full0.2.14 build."""
import argparse,json,re,struct
from elf import ROOT,PATH,Elf
from build import make_iso
import battle_details_patch as prior
import encyclopedia,tutorial_preview

BASE=0x9B5200
LIMIT=0x9B6000
BASE_SHA='89d471695b856e7bede1a8e92141204bd3f5ee045f7b6be9eb36335904b8aef0'
LANGUAGE=ROOT/'work/translation/en/formation.en.json'
LANGUAGE_SHA='4f401a58f6e6f1ea6c5d9a09a97f035cbb54c11d9386aedb6c232a9c9ce52e58'
digest=prior.digest
COPY_CASES={0x161C34:0x161C2C,0x161C50:0x161C48,0x161C80:0x161C78}

def language():
    if digest(LANGUAGE.read_bytes())!=LANGUAGE_SHA:raise ValueError('Formation language revision changed')
    d=json.loads(LANGUAGE.read_text('utf8'))
    if len(d['rows'])!=96 or d['review']!=dict(accuracy='independent-reviewed',editorial='complete',glossary='complete',proofreading='complete'):raise ValueError('Formation review/inventory incomplete')
    return d

def patch(data):
    if digest(data)!=BASE_SHA:raise ValueError('Complete0.2.14 baseline changed')
    e=Elf(data);src=Elf(PATH.read_bytes());out=bytearray(data);d=language();payload=bytearray();strings={};addresses={};changes={};expected={}
    if encyclopedia.END>BASE or LIMIT>tutorial_preview.BASE or e.at(BASE,LIMIT-BASE)!=bytes(LIMIT-BASE):raise ValueError('Formation gap is reserved or not empty')
    if digest(src.data)!=d['source_elf_sha256']:raise ValueError('Formation original changed')
    for r in d['rows']:
        raw=src.at(r['va'],r['source_size'])
        if digest(raw)!=r['source_sha256'] or e.at(r['va'],len(raw))!=raw or raw[-1:]!=b'\0':raise ValueError('Formation source text changed')
        text=r['en']
        if text not in strings:strings[text]=BASE+len(payload);payload.extend(text.encode('cp932')+b'\0')
        addresses[r['va']]=strings[text]
    if BASE+len(payload)>LIMIT:raise ValueError('Formation text pool exceeds proven gap')
    out[e.offset(BASE):e.offset(BASE)+len(payload)]=payload
    def word(site,old,new):
        if int.from_bytes(e.at(site,4),'little')!=old:raise ValueError('Formation word guard failed at%08X'%site)
        expected[site]=old
        if site in changes and changes[site]!=new:raise ValueError('Conflicting formation word')
        if old!=new:changes[site]=new;struct.pack_into('<I',out,e.offset(site),new)
    for r in d['code']:
        if r['site'] in COPY_CASES:continue
        a=addresses[r['target']]
        word(r['lui'],r['lui_word'],r['lui_word']&0xffff0000|((a+0x8000)>>16))
        word(r['site'],r['word'],r['word']&0xffff0000|(a&65535))
    for r in d['pointers']:word(r['site'],r['target'],addresses[r['target']])
    for g in d['geometry']:word(g['site'],g['old'],g['new'])
    # Three original warning paths copy only29/19 source bytes into a local
    # string. Supply the complete relocated text directly to the same existing
    # renderer, preserving window selection and every draw argument.
    for site,start in COPY_CASES.items():
        r=next(r for r in d['code'] if r['site']==site);a=addresses[r['target']]
        code=[0x3C050000|((a+0x8000)>>16),0x24A50000|(a&65535),0x08000000|(0x161CA4>>2),0x02131021]
        for i,w in enumerate(code):word(start+i*4,int.from_bytes(src.at(start+i*4,4),'little'),w)
    # The old lexical scanner missed a saved-fp reference to the already
    # reviewed destroyed-unit message. Its wording is unchanged.
    for r in d['battle_repair']:
        a=r['wanted'];word(r['lui'],r['expected_lui'],r['lui_word']&0xffff0000|((a+0x8000)>>16));word(r['site'],r['expected_word'],r['word']&0xffff0000|(a&65535))
    return bytes(out),dict(language_sha256=LANGUAGE_SHA,payload_va=hex(BASE),payload_size=len(payload),payload_sha256=digest(payload),addresses={hex(k):hex(v)for k,v in addresses.items()},patched_words={hex(k):hex(v)for k,v in changes.items()},expected_words={hex(k):hex(v)for k,v in expected.items()},coverage=dict(source_objects=96,category_source_objects=93,shared_dependencies=3,code_reference_pairs=len(d['code']),static_pointers=len(d['pointers']),fixed_copy_consumers=3,retained_battle_reference_repairs=len(d['battle_repair'])),reference_method=d['reference_method'])

def inputs():
    data,packs,overlays,report=prior.inputs();data,formation=patch(data)
    return data,packs,overlays,dict(**report,formation_ui=formation)

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('version');ap.add_argument('--write',action='store_true');a=ap.parse_args()
    if not re.fullmatch(r'0\.\d+\.\d+',a.version):raise ValueError('Expected0.x.y')
    data,packs,overlays,report=inputs();r=report['formation_ui']
    print(json.dumps(dict(version=a.version,elf_sha256=digest(data),payload_size=r['payload_size'],patched_words=len(r['patched_words']),coverage=r['coverage'],sample={k:r['addresses'][k]for k in ('0x230710','0x2307c8','0x230890')}),indent=1))
    if not a.write:print('DRY: no game files/ISO written.');return
    dest=ROOT/'work/output'/('v'+a.version)
    if dest.exists():raise FileExistsError(dest)
    dest.mkdir(parents=True);(dest/'SLPS_250.70').write_bytes(data)
    for n,p in packs.items():(dest/f'{n:05d}.pack').write_bytes(p)
    for n,p in overlays.items():(dest/f'{n:05d}.evemap').write_bytes(p)
    image=dest/('Sunrise Eiyuutan 2 EN v'+a.version+'.iso');make_iso(image,data,packs,overlays)
    info=json.loads((ROOT/'work/output/v0.2.14/build_info.json').read_text('utf8'))
    info.update(version=a.version,based_on='0.2.14',**report,elf_sha256=digest(data),iso_path=str(image),iso_size=image.stat().st_size,in_game_validation='pending consolidated formation validation',scope='Complete compiled squad-formation category, retaining complete0.2.14 and Japanese voices.')
    info.pop('native_validation_report',None);(dest/'build_info.json').write_text(json.dumps(info,indent=1)+'\n','utf8');print('WRITE:',image)

if __name__=='__main__':main()
