"""Cold native formation consumers for the four reported panels."""
import argparse,json,sys,struct
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from elf import ROOT,Elf
import formation_readability_patch as b
from mips import *
BASE=0x9b5c80;MAIN=BASE+0x60;MAIL=0x9b62c0;END=0x9b6300;HOOK=0x9a0550
DEST=ROOT/'work/ui/formation-readability-0.2.29'
def payload(e):
 out=bytearray(END-BASE);a=Asm(BASE);a(jal(0x102530),NOP,jal(0x1022c0),NOP,jal(0x12a838),NOP,jal(0x1618d8),NOP,la('t0',MAIL),addiu('v0','zero',5),sw('v0',0,'t0'));a.label('end');a(jal(0x10cd78),NOP);a.br('b','end');a(NOP);body=a.assemble()
 if BASE+len(body)>MAIN:raise ValueError('Preview entry overflow')
 out[:len(body)]=body;a=Asm(MAIN);a(addiu('sp','sp',-0x500),sd('ra',0x4f8,'sp'),sd('s0',0x4f0,'sp'),sd('s1',0x4e8,'sp'),sd('s2',0x4e0,'sp'),sd('s3',0x4d8,'sp'),addiu('a0','sp',0x20),move('a1','zero'),jal(0x19ecbc),addiu('a2','zero',0x4b0),addiu('s1','sp',0x20),addiu('s2','sp',0x360),la('s3',MAIL),addiu('t0','zero',1),sh('t0',0x1a,'s1'),addiu('t0','zero',3),sh('t0',0x1c,'s1'))
 def left():
  a(move('a0','zero'),addiu('a1','zero',1),addiu('a2','zero',0x300),addiu('a3','zero',1),addiu('t0','zero',16),addiu('t1','zero',100),addiu('t2','zero',272),jal(0x1112f8),addiu('t3','zero',224),move('s0','v0'))
 def ids(values):
  a(move('a0','s2'),move('a1','zero'),jal(0x19ecbc),addiu('a2','zero',0x170))
  for i,v in enumerate(values):a(addiu('t0','zero',v),sh('t0',i*2,'s2'))
 def show_list(fn,values,selected=2):
  ids(values);a(move('a0','s1'),move('a1','s0'),jal(fn),move('a2','s2'),move('a0','s0'),jal(0x113c40),addiu('a1','zero',selected))
 def wait(phase):a(addiu('t0','zero',phase),sw('t0',0,'s3'),jal(0x142f30),addiu('a0','zero',4))
 def visible(off,show):a(lw('a0',off,'gp'),move('a1','zero')if show else lui('a1',0x8000),jal(0x110fd8),lui('a2',0x8000)if show else move('a2','zero'))
 left()
 visible(-0x5d3c,True);visible(-0x5d38,True)
 for i,machine in enumerate((1,2,2)):
  at=0x24+i*16;a(addiu('t0','zero',1),sw('t0',at,'s1'),addiu('t0','zero',machine),sh('t0',at+4,'s1'),addiu('t0','zero',2),sh('t0',at+6,'s1'))
 show_list(0x165688,(9999,1,2,3));a(move('a0','zero'),jal(0x162978),addiu('a1','zero',2),move('a0','s1'),jal(0x1657f8),addiu('a1','zero',1));wait(1)
 a(jal(0x111c90),move('a0','s0'),lw('a0',-0x5d38,'gp'),jal(0x1523a0),move('a1','zero'))
 visible(-0x5d38,False)
 labels=('S-EN Tank Lv1','S-EN Tank Lv1','S-EN Booster Lv1','S-EN Booster Lv1','EN Pack Lv1','EN Pack Lv1','Air-to-Ground Missile Cannon');table=e.symbol('it_devi_info');items=[]
 for label in labels:
  found=[i for i in range(66)if e.at(int.from_bytes(e.at(table['va']+i*60+8,4),'little'),200).split(b'\0')[0].decode('cp932')==label];items.append(found[0])
 for i,item in enumerate(items):
  at=0x24+i*16;a(addiu('t0','zero',3),sw('t0',at,'s1'),addiu('t0','zero',item),sh('t0',at+4,'s1'))
 show_list(0x165d20,(9999,1,2,3,4,5,6,7));a(move('a0','s1'),jal(0x165e90),addiu('a1','zero',1));wait(2)
 a(jal(0x111c90),move('a0','s0'),jal(0x10ef50),move('a0','s0'),jal(0x162990),addiu('a0','zero',1));visible(-0x5d3c,False)
 a(addiu('t0','zero',3),sw('t0',0,'s3'),la('a0',0x238c80),move('a1','zero'),addiu('a2','zero',2),addiu('a3','zero',4),addiu('t0','zero',16),addiu('t1','zero',54),move('t2','zero'),jal(0x158be8),move('t3','zero'))
 left();visible(-0x5d3c,True);show_list(0x165170,(3,),selected=1);a(lw('a0',-0x5d3c,'gp'),jal(0x1523a0),move('a1','zero'),move('a0','zero'),jal(0x162978),addiu('a1','zero',3),move('a0','s1'),jal(0x165228),addiu('a1','zero',3));wait(4)
 a(jal(0x111c90),move('a0','s0'),jal(0x10ef50),move('a0','s0'),ld('ra',0x4f8,'sp'),ld('s0',0x4f0,'sp'),ld('s1',0x4e8,'sp'),ld('s2',0x4e0,'sp'),ld('s3',0x4d8,'sp'),jr('ra'),addiu('sp','sp',0x500));body=a.assemble()
 if MAIN+len(body)>MAIL:raise ValueError('Preview main overlaps mailbox')
 out[MAIN-BASE:MAIN-BASE+len(body)]=body;return out
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');ap.add_argument('--attempt',type=int,default=1);a=ap.parse_args();folder=ROOT/'work/output/v0.2.29';data=(folder/'SLPS_250.70').read_bytes();info=json.loads((folder/'build_info.json').read_text('utf8'));e=Elf(data);dest=DEST if a.attempt==1 else DEST/f'attempt-{a.attempt}'
 if b.digest(data)!=info['elf_sha256']or e.at(BASE,END-BASE)!=bytes(END-BASE)or e.at(HOOK,8)!=pack([j(0x102530),NOP]):raise ValueError('Cold fixture guard changed')
 out=bytearray(data);body=payload(e);out[e.offset(BASE):e.offset(BASE)+len(body)]=body;changes=[]
 for va,new in((HOOK,pack([j(BASE),NOP])),(0x161994,pack([jal(MAIN)]))):changes.append(dict(va=va,original=e.at(va,len(new)).hex(),new=new.hex()));out[e.offset(va):e.offset(va)+len(new)]=new
 r=dict(delivery_elf_sha256=b.digest(data),debug_elf_sha256=b.digest(out),private_changes=changes,scope='Actual formation window constructor/cleanup, MunitList/MunitInfo, DunitList/DunitInfo, Ship/Captain submenu and CaptainList/CaptainInfo using synthetic stack-local deck/list data after New Game. Original unlocked formation route and gameplay progression not replayed.',cases=['unit list and widened translated class/stats','equipment list with long item','Ship/Captain submenu','Rie captain full-name detail'])
 print(json.dumps(r,indent=1),flush=True)
 if not a.write:print('DRY no preview written.');return
 dest.mkdir(exist_ok=False);(dest/'SLPS_250.70').write_bytes(out);(dest/'manifest.json').write_text(json.dumps(r,indent=1)+'\n','utf8')
if __name__=='__main__':main()
