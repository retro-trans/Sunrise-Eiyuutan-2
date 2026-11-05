"""Readable formation lists, complete right-panel stats and remaining category text."""
import argparse,json,struct,hashlib,shutil
from elf import ROOT,PATH,Elf
from iso import records
import item_typography_patch as prior
from mips import *
BASE_SHA='84797729967d4c4d0e15d0aeb1f8f9eec549babe4dc01b94bcba0f20c1cf30f4'
LANGUAGE=ROOT/'work/translation/en/formation-readability.en.json'
LANGUAGE_SHA='c290c5ef7d59da6bdc803c8b0dee505bbca597a3062610332ea37c030e369c42'
BASE=0x9b6700;LIST=BASE;ROW=BASE+0x100;CLASS=BASE+0x120;SIZE=BASE+0x130;DRAW=BASE+0x140;CODE_END=BASE+0x300
RANGES=((0x9b6a00,0x9b7000),(0x9a3900,0x9a4000))
LIST_CALLS=(0x1657a8,0x165e40,0x166424,0x1673cc,0x166eec)
FORMAT_REFS=((0x165774,0x165780),(0x165e0c,0x165e18),(0x1663b0,0x1663fc),(0x167358,0x1673a4))
digest=lambda b:hashlib.sha256(b).hexdigest()
def language():
 raw=LANGUAGE.read_bytes();d=json.loads(raw)
 if digest(raw)!=LANGUAGE_SHA or len(d['rows'])!=372:raise ValueError('Reviewed formation snapshot changed')
 return d
def code():
 out=bytearray(CODE_END-BASE)
 def put(at,data,limit):
  if at+len(data)>limit:raise ValueError('Formation helper overlap')
  out[at-BASE:at-BASE+len(data)]=data
 a=Asm(LIST);a(addiu('sp','sp',-0x60),sd('ra',0x58,'sp'),sd('s0',0x50,'sp'),sd('s1',0x48,'sp'),sd('s2',0x40,'sp'))
 for i,r in enumerate(('a0','a1','a2','a3','t0','t1','t2','t3')):a(sw(r,i*4,'sp'))
 a(move('s1','a1'),lw('s2',0x20,'a0'),addiu('s2','s2',-8),addiu('s0','zero',26));a.label('measure');a(move('a0','s1'),jal(0x10e510),move('a1','s0'),sltu('v0','s2','v0'));a.br('beqz','v0','done');a(slti('v0','s0',11));a.br('beqz','v0','shrink');a(NOP);a.br('b','done');a(NOP);a.label('shrink');a.br('b','measure');a(addiu('s0','s0',-1));a.label('done')
 for i,r in enumerate(('a0','a1','a2','a3','t0','t1','t2','t3')):a(lw(r,i*4,'sp'))
 a(move('a2','s0'),jal(0x112868),move('a3','s0'),ld('ra',0x58,'sp'),ld('s0',0x50,'sp'),ld('s1',0x48,'sp'),ld('s2',0x40,'sp'),jr('ra'),addiu('sp','sp',0x60));put(LIST,a.assemble(),ROW)
 put(ROW,pack([move('t2','t0'),move('t4','zero'),addiu('t3','zero',308),subu('t3','t3','a2'),j(DRAW),NOP]),CLASS)
 put(CLASS,pack([addiu('t4','zero',1),j(DRAW),addiu('t3','zero',228)]),SIZE)
 put(SIZE,pack([move('t4','zero'),j(DRAW),addiu('t3','zero',64)]),DRAW)
 a=Asm(DRAW);a(addiu('sp','sp',-0x50),sd('ra',0x48,'sp'),sd('s0',0x40,'sp'),sd('s1',0x38,'sp'),sd('s2',0x30,'sp'))
 for i,r in enumerate(('a0','a1','a2','a3','t2')):a(sw(r,i*4,'sp'))
 a(move('s1','a1'),move('s2','t3'),addiu('s0','zero',26),sw('zero',0x14,'sp'));a.br('beqz','t4','measure');a(move('t0','s1'))
 # Native class formats append fullwidth blanks to erase the previous label.
 # Exclude only that trailing padding from measurement, then restore it before
 # drawing. Complete caption and original erasure semantics are retained.
 a.label('end');a(lbu('t1',0,'t0'));a.br('bnez','t1','scan');a(NOP);a.br('b','trim');a(NOP);a.label('scan');a.br('b','end');a(addiu('t0','t0',1))
 a.label('trim');a.br('beq','t0','s1','trimmed');a(lbu('t1',-1,'t0'),addiu('t2','zero',32));a.br('beq','t1','t2','ascii');a(addiu('t2','zero',64));a.br('bne','t1','t2','trimmed');a(subu('t2','t0','s1'),sltiu('t2','t2',2));a.br('bnez','t2','trimmed');a(NOP,lbu('t1',-2,'t0'),addiu('t2','zero',0x81));a.br('bne','t1','t2','trimmed');a(NOP);a.br('b','trim');a(addiu('t0','t0',-2));a.label('ascii');a.br('b','trim');a(addiu('t0','t0',-1))
 a.label('trimmed');a(lbu('t1',0,'t0'),sw('t0',0x14,'sp'),sw('t1',0x18,'sp'),sb('zero',0,'t0'))
 a.label('measure');a(move('a0','s1'),jal(0x10e510),move('a1','s0'),sltu('v0','s2','v0'));a.br('beqz','v0','done');a(slti('v0','s0',11));a.br('beqz','v0','shrink');a(NOP);a.br('b','done');a(NOP);a.label('shrink');a.br('b','measure');a(addiu('s0','s0',-1));a.label('done')
 a(lw('t0',0x14,'sp'));a.br('beqz','t0','restore');a(lw('t1',0x18,'sp'));a(sb('t1',0,'t0'));a.label('restore')
 for i,r in enumerate(('a0','a1','a2','a3','t2')):a(lw(r,i*4,'sp'))
 a(move('t0','s0'),move('t1','s0'),ld('ra',0x48,'sp'),ld('s0',0x40,'sp'),ld('s1',0x38,'sp'),ld('s2',0x30,'sp'),j(0x110ea0),addiu('sp','sp',0x50));put(DRAW,a.assemble(),CODE_END);return out
def reuse_strings(e):
 result={}
 def add(ptr):
  try:raw=e.at(ptr,512).split(b'\0')[0];text=raw.decode('cp932')
  except(ValueError,UnicodeError):return
  result.setdefault(text,ptr)
 for name,stride in(('plt_info',64),('mch_info',64),('it_devi_info',60),('it_expend_info',40),('it_mchdev_info',64),('it_parts_info',32),('it_junk_info',32),('it_event_info',16)):
  s=e.symbol(name)
  for i in range(s['size']//stride):
   for off in(0,4,8):add(int.from_bytes(e.at(s['va']+i*stride+off,4),'little'))
 for ptr in json.loads((ROOT/'work/output/v0.2.28/build_info.json').read_text('utf8'))['formation_ui']['addresses'].values():add(int(ptr,16))
 return result
def patch(data):
 if digest(data)!=BASE_SHA:raise ValueError('Complete 0.2.28 baseline changed')
 e=Elf(data);source=Elf(PATH.read_bytes());d=language();out=bytearray(data);words={};expected={};fields=[];blocks=[];addresses={};strings=reuse_strings(e);idx=0;start,end=RANGES[0];payload=bytearray()
 for a,z in((BASE,CODE_END),*RANGES):
  if e.at(a,z-a)!=bytes(z-a):raise ValueError('Formation pool is occupied')
 def flush():
  if payload:out[e.offset(start):e.offset(start)+len(payload)]=payload;blocks.append(dict(va=start,size=len(payload),sha256=digest(payload)))
 def allocate(text):
  nonlocal idx,start,end,payload
  if text in strings:return strings[text]
  raw=text.encode('cp932')+b'\0'
  if start+len(payload)+len(raw)>end:
   flush();idx+=1
   if idx>=len(RANGES):raise ValueError('Formation complete text pool overflow')
   start,end=RANGES[idx];payload=bytearray()
  ptr=start+len(payload);payload.extend(raw);strings[text]=ptr;return ptr
 def word(va,old,new):
  if int.from_bytes(e.at(va,4),'little')!=old:raise ValueError('Word guard '+hex(va))
  if old==new:return
  expected[hex(va)]=hex(old);words[hex(va)]=hex(new);struct.pack_into('<I',out,e.offset(va),new)
 for r in d['rows']:
  if digest(source.at(r['va'],r['source_size']))!=r['source_with_nul_sha256']:raise ValueError('Source text changed')
  if not r['refs']:continue
  ptr=allocate(r['en']);addresses[hex(r['va'])]=ptr
  for f in r['refs']:word(f['site'],f['expected'],ptr);fields.append(dict(**f,en=r['en'],pointer=ptr,category=r['category']))
 fmt=allocate('%s  Sz %1d');flush();body=code();out[e.offset(BASE):e.offset(BASE)+len(body)]=body
 for high,low in FORMAT_REFS:
  oldhi=int.from_bytes(e.at(high,4),'little');oldlo=int.from_bytes(e.at(low,4),'little');word(high,oldhi,(oldhi&0xffff0000)|hi(fmt));word(low,oldlo,(oldlo&0xffff0000)|lo(fmt))
 for va in LIST_CALLS:word(va,jal(0x9a66c0 if va==0x166eec else 0x112868),jal(LIST))
 word(0x161980,addiu('t2','zero',256),addiu('t2','zero',312))
 right=[]
 for fn in('gdmkPrtUnitInfoTlt4','gdmkPrtMchInfoTlt4'):
  s=e.symbol(fn)
  for va in range(s['va'],s['va']+s['size'],4):
   if int.from_bytes(e.at(va,4),'little')==jal(0x110e98):word(va,jal(0x110e98),jal(ROW));right.append(va)
 for va in(0x167c0c,0x167f80):word(va,jal(0x110ea0),jal(CLASS))
 for va in(0x167c4c,0x167fc0):word(va,jal(0x110ea0),jal(SIZE))
 for va,old in((0x167c3c,184),(0x167fb0,210)):word(va,addiu('a2','zero',old),addiu('a2','zero',244))
 word(0x167c20,addiu('s0','s0',-0x72a0),addiu('s0','s0',-0x7298))
 for p in d['protected_player']:
  if e.at(p['site'],4)!=struct.pack('<I',p['pointer']):raise ValueError('Player name baseline changed')
 return bytes(out),dict(language_sha256=LANGUAGE_SHA,source_objects=372,class_records=33,captain_records=183,fields=fields,addresses=addresses,patched_words=words,expected_words=expected,payloads=blocks,code_va=BASE,code_size=len(body),code_sha256=digest(body),list_calls=LIST_CALLS,right_calls=right,format_va=fmt,geometry=dict(left=[16,100,272,224],right=[316,100,312,224],right_previous_width=256,default_font=[26,26],uniform_minimum=10,class_limit=228,size_x=244,size_limit=64,stats_limit=308,row_pitch=28),protected_player=d['protected_player'],qualifications=d['qualifications'])
def inputs():
 data,packs,overlays,report=prior.inputs();data,ui=patch(data);return data,packs,overlays,dict(report,formation_readability=ui)
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');a=ap.parse_args();old=ROOT/'work/output/v0.2.28';data,ui=patch((old/'SLPS_250.70').read_bytes());info=json.loads((old/'build_info.json').read_text('utf8'));print(json.dumps(dict(version='0.2.29',elf_sha256=digest(data),objects=372,fields=len(ui['fields']),patched_words=len(ui['patched_words']),payloads=ui['payloads'],geometry=ui['geometry']),indent=1),flush=True)
 if not a.write:print('DRY no game files written.');return
 dest=ROOT/'work/output/v0.2.29';dest.mkdir(exist_ok=False);(dest/'SLPS_250.70').write_bytes(data)
 for pattern in('*.pack','*.evemap'):
  for f in old.glob(pattern):shutil.copyfile(f,dest/f.name)
 image=dest/'Sunrise Eiyuutan 2 EN v0.2.29.iso';shutil.copyfile(old/'Sunrise Eiyuutan 2 EN v0.2.28.iso',image);rec=next(x for x in records(image)if x['path']=='/SLPS_250.70')
 if rec['size']!=len(data):raise ValueError('Same-size executable required')
 with image.open('r+b')as f:f.seek(rec['lba']*2048);f.write(data)
 info.update(version='0.2.29',based_on='0.2.28',formation_readability=ui,elf_sha256=digest(data),iso_path=str(image),iso_size=image.stat().st_size,scope='Formation lists with normal text proportions, wider fitted unit stats, all33 class records and183 captains full/display name references plus Ship/Captain menu; dynamic player names and normal help/dialogue preserved.',in_game_validation='pending focused native formation previews')
 for k in('iso_sha256','native_validation_report'):info.pop(k,None)
 (dest/'build_info.json').write_text(json.dumps(info,indent=1)+'\n','utf8');print('WRITE',image)
if __name__=='__main__':main()
