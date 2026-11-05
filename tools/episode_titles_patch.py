"""Complete save/load episode titles with safe concatenation and proportional fit."""
import argparse,json,struct,hashlib,shutil
from elf import ROOT,PATH,Elf
from iso import records
import special_names_patch as prior
from mips import *
BASE_SHA='6e07322d5fe5441ae71d577f89f23b4a95699fba6a038a49cf827b396d6a4fe3'
LANGUAGE=ROOT/'work/translation/en/episode-titles.en.json'
LANGUAGE_SHA='7cd26b53f3f097057741e1db8b70ddff5907f05d28ac947f9afebbe843fcb705'
BASE=0x9a7900;TEXT=0x9a79c0;BUFFER=0x9a7f80;END=0x9a7fc0
digest=lambda b:hashlib.sha256(b).hexdigest()
def fit_code():
 a=Asm(BASE);a(addiu('sp','sp',-32),sd('ra',24,'sp'),sd('s0',16,'sp'),sd('s1',8,'sp'),move('s0','a1'),move('s1','a0'))
 a.label('measure');a(move('a0','s1'),jal(0x10e510),move('a1','s0'),slti('t0','v0',463));a.br('bnez','t0','done');a(NOP,slti('t0','s0',13));a.br('bnez','t0','done');a(NOP);a.br('b','measure');a(addiu('s0','s0',-1))
 a.label('done');a(move('t8','s0'),ld('ra',24,'sp'),ld('s0',16,'sp'),ld('s1',8,'sp'),jr('ra'),addiu('sp','sp',32));return a.assemble()
def width(text,size,widths):return sum((widths[ord(ch)]*size//26 if ord(ch)<128 else size)+2 for ch in text)
def patch(data):
 if digest(data)!=BASE_SHA:raise ValueError('Complete 0.2.26 baseline changed')
 raw=LANGUAGE.read_bytes();d=json.loads(raw)
 if digest(raw)!=LANGUAGE_SHA or len(d['rows'])!=19:raise ValueError('Reviewed language changed')
 e=Elf(data);source=Elf(PATH.read_bytes());out=bytearray(data);words={};expected={};payload=bytearray(TEXT-BASE);code=fit_code();payload[:len(code)]=code;fields=[]
 if len(code)>TEXT-BASE or e.at(BASE,END-BASE)!=bytes(END-BASE):raise ValueError('Reserved mapped pool changed')
 def word(va,old,new):
  if int.from_bytes(e.at(va,4),'little')!=old:raise ValueError('Word guard '+hex(va))
  expected[hex(va)]=hex(old);words[hex(va)]=hex(new);struct.pack_into('<I',out,e.offset(va),new)
 for r in d['rows']:
  if digest(source.at(r['va'],r['source_size']))!=r['source_with_nul_sha256']:raise ValueError('Source changed')
  ptr=BASE+len(payload);payload.extend(r['en'].encode('cp932')+b'\0');word(r['site'],r['expected_pointer'],ptr);fields.append(dict(index=r['index'],pointer=ptr,en=r['en']))
 if BASE+len(payload)>BUFFER:raise ValueError('Payload overlaps title buffer')
 out[e.offset(BASE):e.offset(BASE)+len(payload)]=payload
 for va in(0x13e6f4,0x13e768):word(va,lui('s4',0x52),lui('s4',hi(BUFFER)))
 word(0x13e880,addiu('s2','s4',-0x2940),addiu('s2','s4',lo(BUFFER)))
 word(0x13e8dc,addiu('v0','s4',-0x2940),addiu('v0','s4',lo(BUFFER)))
 word(0x13e8b0,slti('v0','v0',37),slti('v0','v0',64));word(0x13e8bc,addiu('v0','zero',36),addiu('v0','zero',63))
 word(0x14ffe0,jal(0x10e510),jal(BASE))
 for va,reg in((0x150004,'a2'),(0x150008,'a3')):word(va,addiu(reg,'zero',26),move(reg,'t8'))
 widths=json.loads((ROOT/'work/output/v0.2.26/build_info.json').read_text('utf8'))['font_widths'];combinations=[]
 for p in d['prefixes']:
  if e.at(p['site'],4)!=struct.pack('<I',p['pointer']) or e.at(p['pointer'],len(bytes.fromhex(p['raw_hex']))+1)!=bytes.fromhex(p['raw_hex'])+b'\0':raise ValueError('Existing prefix changed')
  for r in d['rows']:
   text=p['en']+r['en'];size=next(n for n in range(26,11,-1)if width(text,n,widths)<=462);nbytes=len(text.encode('cp932'))
   if nbytes>63:raise ValueError('Caller buffer overflow')
   combinations.append(dict(prefix=p['index'],title=r['index'],text=text,bytes=nbytes,font=size,width=width(text,size,widths)))
 return bytes(out),dict(language_sha256=LANGUAGE_SHA,title_count=19,fields=fields,patched_words=words,expected_words=expected,payload_va=BASE,payload_size=len(payload),payload_sha256=digest(payload),buffer=BUFFER,buffer_capacity=64,maximum_combined_bytes=max(x['bytes']for x in combinations),minimum_font=min(x['font']for x in combinations),combinations=combinations,geometry=dict(x=80,y=118,width=478,height=168,row_pitch=28,interior=462,default_font=[26,26]),save_format='Unchanged numeric prefix/title indices; existing saves resolve through updated lookup table.')
def inputs():
 data,packs,overlays,report=prior.inputs();data,titles=patch(data);return data,packs,overlays,dict(report,episode_titles=titles)
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');a=ap.parse_args();old=ROOT/'work/output/v0.2.26';data,titles=patch((old/'SLPS_250.70').read_bytes());info=json.loads((old/'build_info.json').read_text('utf8'));print(json.dumps(dict(version='0.2.27',elf_sha256=digest(data),titles=19,payload_size=titles['payload_size'],maximum_combined_bytes=titles['maximum_combined_bytes'],minimum_font=titles['minimum_font'],sample=[x for x in titles['combinations']if(x['prefix'],x['title'])in((2,6),(16,12))]),indent=1),flush=True)
 if not a.write:print('DRY no game files written.');return
 dest=ROOT/'work/output/v0.2.27';dest.mkdir(exist_ok=False);(dest/'SLPS_250.70').write_bytes(data)
 for pattern in('*.pack','*.evemap'):
  for f in old.glob(pattern):shutil.copyfile(f,dest/f.name)
 image=dest/'Sunrise Eiyuutan 2 EN v0.2.27.iso';shutil.copyfile(old/'Sunrise Eiyuutan 2 EN v0.2.26.iso',image);rec=next(x for x in records(image)if x['path']=='/SLPS_250.70')
 if rec['size']!=len(data):raise ValueError('Same-size ELF required')
 with image.open('r+b')as f:f.seek(rec['lba']*2048);f.write(data)
 info.update(version='0.2.27',based_on='0.2.26',episode_titles=titles,elf_sha256=digest(data),iso_path=str(image),iso_size=image.stat().st_size,scope='All 19 save/load episode titles; full English concatenation in relocated buffer and uniform font fitting in original save-list frame. All 0.2.26 resources and normal dialogue/help geometry retained.',in_game_validation='pending focused native save-list preview')
 for k in('iso_sha256','native_validation_report'):info.pop(k,None)
 (dest/'build_info.json').write_text(json.dumps(info,indent=1)+'\n','utf8');print('WRITE',image)
if __name__=='__main__':main()
