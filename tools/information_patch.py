"""Information inventory completion and measured two-column item lists."""
import argparse,json,re,struct
from elf import ROOT,PATH,Elf
from build import make_iso
import services_patch as prior
import tutorial_preview,battle_preview,menu_patch
from mips import *

BASE=0x9A6400
MEASURE=BASE
MEASURE26=BASE+0x40
RENDER=BASE+0x80
DEFAULT_RENDER=BASE+0x280
FIT_PICKER=BASE+0x2C0
REMOVE=BASE+0x400
CODE_END=BASE+0x700
TEXT_RANGES=((0x9A6B00,0x9A7800),(0x9B7400,0x9B8000),(0x9B6300,0x9B7000))
WIDTH=608
NAME_X=8
NUMBER_RIGHT=600
NAME_LIMIT=520
BASE_SHA='f5388ef7a49cd18c09cc643ff8147e2a0e23fb25e99f731cd02216d133a672e5'
LANGUAGE=ROOT/'work/translation/en/information.en.json'
LANGUAGE_SHA='b7eb996b185576b22ac94a7642635c44270a483e559d4b3a2b86db9cc2a85fd4'
FORMAT='\x1f%s\t%d'
HEADER='\x1fName\tOwned'
digest=prior.digest

def code():
 out=bytearray(CODE_END-BASE)
 def put(at,data):
  if at<BASE or at+len(data)>CODE_END:raise ValueError('Information code overflow')
  off=at-BASE
  if any(out[off:off+len(data)]):raise ValueError('Information code overlap')
  out[off:off+len(data)]=data
 a=Asm(MEASURE);a(lbu('v0',0,'a0'),addiu('v1','zero',31));a.br('bne','v0','v1','plain');a(NOP)
 a(jr('ra'),addiu('v0','zero',WIDTH));a.label('plain');a(j(0x10E510),NOP);put(MEASURE,a.assemble())
 put(MEASURE26,pack([j(MEASURE),addiu('a1','zero',26)]))
 a=Asm(RENDER);a(lbu('v0',0,'a1'),addiu('v1','zero',31));a.br('beq','v0','v1','marked');a(NOP)
 a(j(0x110EA0),NOP);a.label('marked');a(addiu('sp','sp',-0x80),sd('ra',0x70,'sp'),sd('s0',0x40,'sp'),sd('s1',0x50,'sp'))
 for reg,off in [('a0',0),('a1',4),('a2',8),('a3',12),('t0',16),('t1',20),('t2',24)]:a(sw(reg,off,'sp'))
 a(addiu('s0','a1',1));a.label('scan');a(lbu('v0',0,'s0'));a.br('beqz','v0','fallback');a(addiu('v1','zero',9));a.br('beq','v0','v1','split');a(NOP);a.br('b','scan');a(addiu('s0','s0',1))
 a.label('split');a(addiu('s1','s0',1),sb('zero',0,'s0'),lw('a0',4,'sp'),lw('a1',16,'sp'),jal(0x10E510),addiu('a0','a0',1))
 a(sltiu('v0','v0',NAME_LIMIT+1),lw('t0',16,'sp'));a.br('bnez','v0','namefont');a(NOP);a(addiu('t0','zero',22));a.label('namefont')
 a(lw('a1',4,'sp'),lw('a2',8,'sp'),addiu('a1','a1',1),lw('a0',0,'sp'),lw('a3',12,'sp'),lw('t1',20,'sp'),lw('t2',24,'sp'),jal(0x110EA0),addiu('a2','a2',NAME_X))
 a(addiu('v0','zero',9),sb('v0',0,'s0'),move('a0','s1'),jal(0x10E510),lw('a1',16,'sp'))
 a(lw('a2',8,'sp'),lw('a0',0,'sp'),addiu('a2','a2',NUMBER_RIGHT),lw('a3',12,'sp'),subu('a2','a2','v0'),lw('t0',16,'sp'),lw('t1',20,'sp'),lw('t2',24,'sp'),jal(0x110EA0),move('a1','s1'))
 a(ld('ra',0x70,'sp'),ld('s0',0x40,'sp'),ld('s1',0x50,'sp'),jr('ra'),addiu('sp','sp',0x80))
 a.label('fallback')
 for reg,off in [('a0',0),('a1',4),('a2',8),('a3',12),('t0',16),('t1',20),('t2',24)]:a(lw(reg,off,'sp'))
 a(ld('ra',0x70,'sp'),ld('s0',0x40,'sp'),ld('s1',0x50,'sp'),j(0x110EA0),addiu('sp','sp',0x80));body=a.assemble()
 if RENDER+len(body)>DEFAULT_RENDER:raise ValueError('Information renderer overlaps wrapper')
 put(RENDER,body)
 a=Asm(DEFAULT_RENDER);a(lbu('v0',0,'a1'),addiu('v1','zero',31));a.br('beq','v0','v1','marked');a(NOP);a(j(0x110E98),NOP)
 a.label('marked');a(move('t2','t0'),addiu('t1','zero',26),j(RENDER),addiu('t0','zero',26));put(DEFAULT_RENDER,a.assemble())
 a=Asm(FIT_PICKER);a(addiu('sp','sp',-0x40),sd('ra',0x30,'sp'))
 args=[('a0',0),('a1',4),('a2',8),('a3',12),('t0',16),('t1',20),('t2',24),('t3',28)]
 for reg,off in args:a(sw(reg,off,'sp'))
 a(move('a0','a1'),jal(0x10E510),move('a1','a2'),sltiu('v0','v0',273));a.br('bnez','v0','restore');a(NOP)
 a(addiu('v0','zero',11),sw('v0',8,'sp'));a.label('restore')
 for reg,off in args:a(lw(reg,off,'sp'))
 a(ld('ra',0x30,'sp'),j(0x112868),addiu('sp','sp',0x40));put(FIT_PICKER,a.assemble())
 # Private modal for one equipment-removal caller. Relative branches and
 # all native operations remain; replace byte sizing with measured pixels.
 e=Elf((ROOT/'work/output/v0.2.16/SLPS_250.70').read_bytes())
 original=e.at(0x152590,540)
 if digest(original)!='b042f5fa91dcc65d454b91f50ae766e8d509b75894dc6fba94c9d8f497c5bdde':raise ValueError('Removal modal baseline changed')
 modal=bytearray(original)
 def at(site,w):struct.pack_into('<I',modal,site-0x152590,w)
 at(0x152610,jal(MEASURE26));at(0x152624,move('t2','s2'));at(0x15262C,NOP)
 put(REMOVE,modal)
 return bytes(out)

def language():
 if digest(LANGUAGE.read_bytes())!=LANGUAGE_SHA:raise ValueError('Information language revision changed')
 d=json.loads(LANGUAGE.read_text('utf8'))
 if len(d['rows'])!=228 or len(d['fields'])!=732 or d['review']!=dict(accuracy='independent-reviewed',editorial='complete',glossary='complete',proofreading='complete'):raise ValueError('Information language review/inventory incomplete')
 return d

def patch(data):
 if digest(data)!=BASE_SHA:raise ValueError('Complete0.2.16 baseline changed')
 e=Elf(data);src=Elf(PATH.read_bytes());d=language();out=bytearray(data);words={};expected={};addresses={};strings={};blocks=[]
 if prior.BASE+4554>BASE or CODE_END>TEXT_RANGES[0][0] or TEXT_RANGES[0][1]>prior.STATS_FONT:raise ValueError('Information services boundary collision')
 if battle_preview.END>TEXT_RANGES[1][0] or TEXT_RANGES[1][1]>menu_patch.BASE or tutorial_preview.END>TEXT_RANGES[2][0] or TEXT_RANGES[2][1]>battle_preview.BASE:raise ValueError('Information preview/menu boundary collision')
 for start,end in ((BASE,CODE_END),*TEXT_RANGES):
  if e.at(start,end-start)!=bytes(end-start):raise ValueError('Information reserved interval is occupied')
 if digest(src.data)!=d['source_elf_sha256']:raise ValueError('Information source changed')
 for r in d['rows']:
  raw=src.at(r['va'],r['source_size'])
  if digest(raw)!=r['source_sha256']or e.at(r['va'],len(raw))!=raw:raise ValueError('Information source text changed')
 # Complete NUL-terminated objects stay within an individual proven gap.
 index=0;payload=bytearray();start,end=TEXT_RANGES[index]
 def flush():
  if payload:
   out[e.offset(start):e.offset(start)+len(payload)]=payload
   blocks.append(dict(va=hex(start),size=len(payload),sha256=digest(payload)))
 def allocate(text):
  nonlocal index,payload,start,end
  if text in strings:return strings[text]
  raw=text.encode('cp932')+b'\0'
  if start+len(payload)+len(raw)>end:
   flush();index+=1
   if index>=len(TEXT_RANGES):raise ValueError('Information complete-object pools exhausted')
   start,end=TEXT_RANGES[index];payload=bytearray()
  address=start+len(payload);payload.extend(raw);strings[text]=address;return address
 for r in d['rows']:addresses[r['va']]=allocate(r['en'])
 fmt=allocate(FORMAT);header=allocate(HEADER)
 formats=[]
 for f in d['format_overrides']:
  old=f['current_v016_en'].encode('cp932')+b'\0'
  if e.at(f['current_v016_va'],len(old))!=old:raise ValueError('Equipment format baseline changed')
  formats.append((f,allocate(f['proposed_en'])))
 flush()
 body=code();out[e.offset(BASE):e.offset(BASE)+len(body)]=body
 def word(site,old,new):
  if int.from_bytes(e.at(site,4),'little')!=old:raise ValueError('Information word guard failed at%08X'%site)
  if site in words and words[site]!=new:raise ValueError('Information conflicting word')
  expected[site]=old;words[site]=new;struct.pack_into('<I',out,e.offset(site),new)
 for r in d['fields']:word(r['site'],r['target'],addresses[r['target']])
 for hi_site,lo_site,target in ((0x13FC58,0x13FC60,fmt),(0x13FD78,0x13FD80,header)):
  high=int.from_bytes(e.at(hi_site,4),'little');low=int.from_bytes(e.at(lo_site,4),'little')
  word(hi_site,high,high&0xffff0000|hi(target));word(lo_site,low,low&0xffff0000|lo(target))
 for f,target in formats:
  for pair in f['reference_pairs']:
   high=int(pair['current_v016_lui_word'],16);low=int(pair['current_v016_low_word'],16)
   word(pair['lui_va'],high,high&0xffff0000|hi(target));word(pair['low_va'],low,low&0xffff0000|lo(target))
 for site,old,new in [(0x13F738,0x19F7D8,MEASURE26),(0x13F76C,0x10E510,MEASURE),(0x112804,0x10E510,MEASURE),(0x11248C,0x110EA0,RENDER),(0x130558,0x110E98,DEFAULT_RENDER),(0x166EEC,0x112868,FIT_PICKER),(0x164938,0x152590,REMOVE)]:word(site,jal(old),jal(new))
 return bytes(out),dict(language_sha256=LANGUAGE_SHA,coverage=dict(source_objects=228,item_records=183,typed_fields=732),addresses={hex(k):hex(v)for k,v in addresses.items()},patched_words={hex(k):hex(v)for k,v in words.items()},expected_words={hex(k):hex(v)for k,v in expected.items()},payloads=blocks,code_va=hex(BASE),code_size=len(body),code_sha256=digest(body),format_va=hex(fmt),header_va=hex(header),list_width=WIDTH,name_x=NAME_X,name_limit=NAME_LIMIT,quantity_right=NUMBER_RIGHT,marker='1F',source_format='%-30s + four wide spaces + two spaces + %2d + space',replacement_format='marker + %s + tab separator + %d; both original arguments retained; padding replaced with exact pixel columns')

def inputs():
 data,packs,overlays,report=prior.inputs();data,info=patch(data)
 return data,packs,overlays,dict(**report,information_ui=info)

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('version');ap.add_argument('--write',action='store_true');a=ap.parse_args()
 if not re.fullmatch(r'0\.\d+\.\d+',a.version):raise ValueError('Expected0.x.y')
 data,packs,overlays,report=inputs();r=report['information_ui'];print(json.dumps(dict(version=a.version,elf_sha256=digest(data),coverage=r['coverage'],payloads=r['payloads'],patched_words=len(r['patched_words']),code_bytes=r['code_size']),indent=1))
 if not a.write:print('DRY: no game files/ISO written.');return
 dest=ROOT/'work/output'/('v'+a.version)
 if dest.exists():raise FileExistsError(dest)
 dest.mkdir(parents=True);(dest/'SLPS_250.70').write_bytes(data)
 for n,p in packs.items():(dest/f'{n:05d}.pack').write_bytes(p)
 for n,p in overlays.items():(dest/f'{n:05d}.evemap').write_bytes(p)
 image=dest/('Sunrise Eiyuutan 2 EN v'+a.version+'.iso');make_iso(image,data,packs,overlays)
 info=json.loads((ROOT/'work/output/v0.2.16/build_info.json').read_text('utf8'));info.update(version=a.version,based_on='0.2.16',**report,elf_sha256=digest(data),iso_path=str(image),iso_size=image.stat().st_size,in_game_validation='pending consolidated information validation',scope='Complete related Information item dependency tables and measured two-column selector, retaining complete0.2.16 and Japanese voices.')
 info.pop('native_validation_report',None);info.pop('iso_sha256',None);(dest/'build_info.json').write_text(json.dumps(info,indent=1)+'\n','utf8');print('WRITE:',image)

if __name__=='__main__':main()
