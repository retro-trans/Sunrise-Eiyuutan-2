"""Complete31 native passive-ability records and the battle reward heading.

Relocate complete English strings and use a taller, scoped status panel while
retaining normal26px glyphs, all native callers, values and combat behavior.
"""
import argparse,hashlib,json,re,struct
from elf import ROOT,PATH,Elf
from build import make_iso
from mips import addiu,jal
import battle_readability_patch as prior

BASE_SHA='3d0e43691bee27487ae56d8bedcec08077aef8a1250cb2dc86d8617859635ce1'
LANGUAGE=ROOT/'work/translation/en/battle-effects.en.json'
LANGUAGE_SHA='21b142f04add89ac005baa011199805d396bb350b6482b6974a137870f78607a'
TEXT=0x9A3000;TEXT_END=0x9A4000
INIT=0x9A61D0;TEXTWIN=0x9A6210;FRAME=0x9A62B0;FACTORY=0x9A6340;CODE_END=0x9A6400
CLONES=((0x12DC70,60,INIT),(0x12DF30,160,TEXTWIN),(0x12E040,136,FRAME),(0x12DA40,120,FACTORY))
digest=prior.digest

def language():
 raw=LANGUAGE.read_bytes();d=json.loads(raw)
 if digest(raw)!=LANGUAGE_SHA or d['review']!=dict(accuracy='independent-reviewed',editorial='complete',glossary='complete',proofreading='complete'):raise ValueError('Ability language revision/review changed')
 if len(d['rows'])!=65 or sum(r['translation_required']for r in d['rows'])!=63:raise ValueError('Ability inventory changed')
 return d

def wrap(text,widths,limit=504):
 lines=[];line=''
 metric=lambda s:sum((widths[ord(c)]if ord(c)<128 else 26)+2 for c in s)
 for word in text.split(' '):
  trial=(line+' '+word).strip()
  if line and metric(trial)>limit:lines.append(line);line=word
  else:line=trial
 if line:lines.append(line)
 if not lines:return text,[]
 if len(lines)>3 or any(metric(s)>limit for s in lines):raise ValueError('Full ability wording requires more display room')
 if ' '.join(lines).split()!=text.split():raise ValueError('Ability words changed')
 return '\n'.join(lines),[metric(s)for s in lines]

def clones(e):
 out=bytearray(CODE_END-INIT);blocks=[]
 edits={0x12DC90:(addiu('v0','zero',336),addiu('v0','zero',280)),
  0x12DF7C:(addiu('t0','zero',84),addiu('t0','zero',140)),
  0x12E050:(jal(0x12DA40),jal(FACTORY)),
  0x12DA6C:(addiu('t1','zero',96),addiu('t1','zero',152))}
 for old,size,new in CLONES:
  raw=bytearray(e.at(old,size))
  for off in range(0,size,4):
   w=struct.unpack_from('<I',raw,off)[0];op=w>>26
   if op in (1,4,5,6,7,20,21,22,23)or(op==17 and(w>>21)&31==8):
    imm=w&65535;imm=imm-65536 if imm&32768 else imm
    if not old<=old+off+4+imm*4<old+size:raise ValueError('Clone has external relative branch')
   if op in(2,3):
    target=((old+off+4)&0xf0000000)|((w&0x3ffffff)<<2)
    if old<=target<old+size:struct.pack_into('<I',raw,off,(op<<26)|((new+target-old)>>2))
  for site,(before,after)in edits.items():
   if old<=site<old+size:
    if int.from_bytes(raw[site-old:site-old+4],'little')!=before:raise ValueError('Scoped status geometry changed')
    struct.pack_into('<I',raw,site-old,after)
  if new+size>CODE_END:raise ValueError('Status code reservation overflow')
  out[new-INIT:new-INIT+size]=raw;blocks.append(dict(source=hex(old),va=hex(new),size=size,source_sha256=digest(e.at(old,size)),sha256=digest(raw)))
 return bytes(out),blocks

def patch(data):
 if digest(data)!=BASE_SHA:raise ValueError('Complete0.2.21 baseline changed')
 e=Elf(data);src=Elf(PATH.read_bytes());d=language();out=bytearray(data);payload=bytearray();addresses={};layout=[];changes={};expected={}
 for a,z in((TEXT,TEXT_END),(INIT,CODE_END)):
  if e.at(a,z-a)!=bytes(z-a):raise ValueError('Ability reserved interval occupied')
 if digest(src.data)!=d['source_elf_sha256']:raise ValueError('Original ability source changed')
 widths=json.loads((ROOT/'work/output/v0.2.21/build_info.json').read_text('utf8'))['font_widths']
 def word(site,old,new):
  if int.from_bytes(e.at(site,4),'little')!=old:raise ValueError('Ability reference changed at'+hex(site))
  if hex(site)in changes and changes[hex(site)]!=hex(new):raise ValueError('Conflicting ability reference')
  expected[hex(site)]=hex(old);changes[hex(site)]=hex(new);struct.pack_into('<I',out,e.offset(site),new)
 for r in d['rows']:
  raw=src.at(r['va'],r['source_size'])
  if digest(raw)!=r['source_sha256']or e.at(r['va'],len(raw))!=raw:raise ValueError('Original ability string changed')
  if not r['translation_required']:addresses[r['va']]=r['va'];continue
  text=r['en'];comment=any(s['field_index']==3 for s in r['sites'])
  fitted,sizes=wrap(text,widths)if comment else(text,[sum((widths[ord(c)]if ord(c)<128 else 26)+2 for c in text)])
  if re.search('[ぁ-ゖァ-ヺ一-鿿]',text):raise ValueError('Untranslated ability text')
  a=TEXT+len(payload);addresses[r['va']]=a;payload.extend(fitted.encode('cp932')+b'\0')
  layout.append(dict(source_va=hex(r['va']),va=hex(a),en=text,display=fitted,widths=sizes,comment=comment))
  for s in r['sites']:word(int(s['pointer_site'],16),r['va'],a)
 if TEXT+len(payload)>TEXT_END:raise ValueError('Ability string pool overflow')
 a=addresses[0x232388]
 word(0x1701E4,0x3C050023,0x3C050000|((a+0x8000)>>16));word(0x1701E8,0x24A52388,0x24A50000|(a&65535))
 body,blocks=clones(e)
 for at,old,new in((0x1686F0,0x12DC70,INIT),(0x1686F8,0x12DF30,TEXTWIN),(0x168700,0x12E040,FRAME)):word(at,jal(old),jal(new))
 out[e.offset(TEXT):e.offset(TEXT)+len(payload)]=payload;out[e.offset(INIT):e.offset(INIT)+len(body)]=body
 return bytes(out),dict(language_sha256=LANGUAGE_SHA,objects=65,translated_objects=63,records=31,translated_fields=122,payload_va=hex(TEXT),payload_size=len(payload),payload_sha256=digest(payload),layout=layout,code_va=hex(INIT),code_size=len(body),code_sha256=digest(body),clones=blocks,patched_words=changes,expected_words=expected,status_panel=dict(y=280,frame_height=152,text_height=140,lines=5,font=[26,26],bottom=432),original_factory_paths_retained=True)

def inputs():
 data,packs,overlays,report=prior.inputs();data,effects=patch(data)
 return data,packs,overlays,dict(**report,battle_effects=effects)

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('version');ap.add_argument('--write',action='store_true');a=ap.parse_args()
 if a.version!='0.2.22':raise ValueError('Guarded ability package is0.2.22')
 data,packs,overlays,report=inputs();r=report['battle_effects']
 print(json.dumps(dict(version=a.version,elf_sha256=digest(data),objects=r['translated_objects'],records=31,payload=r['payload_size'],words=len(r['patched_words']),sample=[x for x in r['layout']if x['source_va']=='0x22af90'],panel=r['status_panel']),indent=1))
 if not a.write:print('DRY: no game files/ISO written.');return
 dest=ROOT/'work/output/v0.2.22';dest.mkdir(exist_ok=False);(dest/'SLPS_250.70').write_bytes(data)
 for n,b in packs.items():(dest/f'{n:05d}.pack').write_bytes(b)
 for n,b in overlays.items():(dest/f'{n:05d}.evemap').write_bytes(b)
 image=dest/'Sunrise Eiyuutan 2 EN v0.2.22.iso';make_iso(image,data,packs,overlays);retained=prior.prior.retain_movies(image)
 info=json.loads((ROOT/'work/output/v0.2.21/build_info.json').read_text('utf8'));info.update(version=a.version,based_on='0.2.21',**report,elf_sha256=digest(data),iso_path=str(image),iso_size=image.stat().st_size,movie_archive_retained=retained,in_game_validation='pending; separate from binary checks',scope='Complete31 passive ability records and battle reward heading; readable five-line scoped status panel; retain complete0.2.21 and original audio.')
 for key in('iso_sha256','native_validation_report'):info.pop(key,None)
 (dest/'build_info.json').write_text(json.dumps(info,indent=1)+'\n','utf8');print('WRITE',image)

if __name__=='__main__':main()
