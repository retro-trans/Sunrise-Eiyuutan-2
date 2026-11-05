"""Relocate all special-attack name variants and restore readable selector font."""
import argparse,json,struct,hashlib,shutil
from elf import ROOT,PATH,Elf
from iso import records
import battle_category_patch as prior
from mips import addiu
BASE_SHA='7738a409a25deeb35b8ccf81e0d204e414e373930d95814b282b9e8cfab788da'
LANGUAGE=ROOT/'work/translation/en/special-names.en.json'
LANGUAGE_SHA='24d2d71af3d75c72296bddcd150bc7a8c8d6d115477b9a0600db7e4eff2a7970'
BASE=0x9b7b00;END=0x9b8000
GEOMETRY=((0x16f214,'a3',280,400),(0x16f224,'a1',336,224),(0x16f278,'s7',280,400),(0x16f298,'a1',13,26),(0x16f2b8,'a2',13,26))
digest=lambda b:hashlib.sha256(b).hexdigest()
def language():
 raw=LANGUAGE.read_bytes();d=json.loads(raw)
 if digest(raw)!=LANGUAGE_SHA or len(d['rows'])!=50:raise ValueError('Reviewed special-name snapshot changed')
 return d

def patch(data):
 if digest(data)!=BASE_SHA:raise ValueError('Complete 0.2.25 baseline changed')
 d=language();e=Elf(data);source=Elf(PATH.read_bytes());out=bytearray(data);payload=bytearray();strings={};changes={};expected={};fields=[];widths=json.loads((ROOT/'work/output/v0.2.25/build_info.json').read_text('utf8'))['font_widths']
 if digest(source.data)!=d['source_elf_sha256']or e.at(BASE,END-BASE)!=bytes(END-BASE)or e.at(0x1fd5e8,7080)!=source.at(0x1fd5e8,7080):raise ValueError('Source table or reserved pool changed')
 def alloc(t):
  raw=t.encode('ascii')+b'\0'
  if t not in strings:strings[t]=BASE+len(payload);payload.extend(raw)
  return strings[t]
 def word(va,old,new):
  if int.from_bytes(e.at(va,4),'little')!=old:raise ValueError('Word guard failed '+hex(va))
  expected[hex(va)]=hex(old);changes[hex(va)]=hex(new);struct.pack_into('<I',out,e.offset(va),new)
 for r in d['rows']:
  raw=source.at(r['va'],r['source_size'])
  if raw[-1:]!=b'\0'or digest(raw)!=r['source_with_nul_sha256']:raise ValueError('Name source changed')
  for f in r['refs']:
   text=r['omit_en']if f['field']==12 else r['en'];ptr=alloc(text);word(f['site'],r['va'],ptr);width=sum(widths[ord(c)]+2 for c in text)
   if f['field']==12 and width>384:raise ValueError('Omission name exceeds normal-width list')
   fields.append(dict(**f,source_va=r['va'],pointer=ptr,en=text,width=width))
 if BASE+len(payload)>END:raise ValueError('Special-name relocation pool overflow')
 out[e.offset(BASE):e.offset(BASE)+len(payload)]=payload
 for va,reg,old,new in GEOMETRY:word(va,addiu(reg,'zero',old),addiu(reg,'zero',new))
 return bytes(out),dict(language_sha256=LANGUAGE_SHA,distinct_source_names=50,records=118,fields=fields,payload_va=BASE,payload_size=len(payload),payload_end=BASE+len(payload),payload_sha256=digest(payload),patched_words=changes,expected_words=expected,selector=dict(font=[26,26],width=400,left_x=16,right_x=224,interior=384,maximum_omit_width=max(f['width']for f in fields if f['field']==12),row_pitch=28),abbreviation=d['abbreviation'])

def inputs():
 data,packs,overlays,report=prior.inputs();data,names=patch(data);return data,packs,overlays,dict(report,special_names=names)

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');a=ap.parse_args();old=ROOT/'work/output/v0.2.25';data,names=patch((old/'SLPS_250.70').read_bytes());info=json.loads((old/'build_info.json').read_text('utf8'));print(json.dumps(dict(version='0.2.26',elf_sha256=digest(data),names=50,records=118,name_fields=354,payload_size=names['payload_size'],selector=names['selector'],sample=[f for f in names['fields']if f['row']in(1,44)and f['field']==12]),indent=1),flush=True)
 if not a.write:print('DRY no game files or ISO written.');return
 dest=ROOT/'work/output/v0.2.26';dest.mkdir(exist_ok=False);(dest/'SLPS_250.70').write_bytes(data)
 for pattern in('*.pack','*.evemap'):
  for f in old.glob(pattern):shutil.copyfile(f,dest/f.name)
 image=dest/'Sunrise Eiyuutan 2 EN v0.2.26.iso';shutil.copyfile(old/'Sunrise Eiyuutan 2 EN v0.2.25.iso',image);rec=next(x for x in records(image)if x['path']=='/SLPS_250.70')
 if rec['size']!=len(data):raise ValueError('Same-size ELF extent required')
 with image.open('r+b')as f:f.seek(rec['lba']*2048);f.write(data)
 info.update(version='0.2.26',based_on='0.2.25',special_names=names,elf_sha256=digest(data),iso_path=str(image),iso_size=image.stat().st_size,scope='All 118 special-attack name records and all full/display/omission variants; normal-proportion special selector. Complete 0.2.25 resources, voices, movies and normal help/dialogue geometry retained.',in_game_validation='pending focused special-name selector preview')
 for k in('iso_sha256','native_validation_report'):info.pop(k,None)
 (dest/'build_info.json').write_text(json.dumps(info,indent=1)+'\n','utf8');print('WRITE',image)
if __name__=='__main__':main()
