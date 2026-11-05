"""Cold native formation fixtures for the five current reports plus long names."""
import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from elf import ROOT,Elf
import formation_polish_patch as b
from mips import *
BASE=0x9b5c80;MAIN=BASE+0x60;MAIL=0x9b62c0;END=0x9b6300;HOOK=0x9a0550
DEST=ROOT/'work/ui/formation-polish-0.2.30'
CASES=['Aqua Wolf (Unmanned) list and heading','Domon pilot list at normal proportions','Attack / Defend / Special submenu','Equipment 1/2/3 and larger None details','Full equipment names fitted individually','Aligned Ship / Captain submenu']

def payload(e):
 out=bytearray(END-BASE);a=Asm(BASE);a(jal(0x102530),NOP,jal(0x1022c0),NOP,jal(0x12a838),NOP,jal(0x1618d8),NOP,la('t0',MAIL),addiu('v0','zero',7),sw('v0',0,'t0'));a.label('end');a(jal(0x10cd78),NOP);a.br('b','end');a(NOP);out[:len(a.assemble())]=a.assemble()
 a=Asm(MAIN);a(addiu('sp','sp',-0x1000),sd('ra',0xff8,'sp'),sd('s0',0xff0,'sp'),sd('s1',0xfe8,'sp'),sd('s2',0xfe0,'sp'),sd('s3',0xfd8,'sp'),addiu('a0','sp',0x20),move('a1','zero'),jal(0x19ecbc),addiu('a2','zero',0xfb0),addiu('s1','sp',0x20),addiu('s2','sp',0x360),la('s3',MAIL),addiu('t0','zero',1),sh('t0',0x1a,'s1'),addiu('t0','zero',3),sh('t0',0x1c,'s1'))
 def visible(off,show):a(lw('a0',off,'gp'),move('a1','zero')if show else lui('a1',0x8000),jal(0x110fd8),lui('a2',0x8000)if show else move('a2','zero'))
 def left():a(move('a0','zero'),addiu('a1','zero',1),addiu('a2','zero',0x300),addiu('a3','zero',1),addiu('t0','zero',16),addiu('t1','zero',100),addiu('t2','zero',272),jal(0x1112f8),addiu('t3','zero',224),move('s0','v0'))
 def cleanup():a(jal(0x111c90),move('a0','s0'),jal(0x10ef50),move('a0','s0'))
 def unit(machine,pilot=2):a(addiu('t0','zero',1),sw('t0',0x24,'s1'),addiu('t0','zero',machine),sh('t0',0x28,'s1'),addiu('t0','zero',pilot),sh('t0',0x2a,'s1'),move('a0','s1'),jal(0x1657f8),addiu('a1','zero',1))
 def wait(phase):a(addiu('t0','zero',phase),sw('t0',0,'s3'),jal(0x142f30),addiu('a0','zero',4))
 def show_list(fn,ids,selected=1):
  a(move('a0','s2'),move('a1','zero'),jal(0x19ecbc),addiu('a2','zero',0x6c0))
  for i,v in enumerate(ids):a(addiu('t0','zero',v),sh('t0',i*2,'s2'))
  a(move('a0','s1'),move('a1','s0'),jal(fn),move('a2','s2'),move('a0','s0'),jal(0x113c40),addiu('a1','zero',selected))
 def menu(table,count,phase,y=100):a(addiu('t0','zero',phase),sw('t0',0,'s3'),la('a0',table),move('a1','zero'),addiu('a2','zero',count),addiu('a3','zero',4),addiu('t0','zero',16),addiu('t1','zero',y),move('t2','zero'),jal(0x158be8),move('t3','zero'))
 visible(-0x5d3c,True);visible(-0x5d38,True);left();unit(46);show_list(0x165688,(9999,1),2);wait(1);cleanup()
 left();unit(316,437);show_list(0x1669a0,(437,));wait(2);cleanup()
 unit(1);menu(0x1f8830,3,3)
 a(jal(0x162e78),addiu('a0','s1',0x24));menu(0x1f8840,3,4)
 labels=('None','Slower SP, Lower EN, Higher AT','Improved Ultra-Compact Nuclear Fusion Engine');items=[]
 for label in labels:
  found=[i for i in range(161)if e.at(int.from_bytes(e.at(0x1e46a0+i*64+8,4),'little'),180).split(b'\0')[0].decode('cp932')==label];items.append(found[0])
 for i,item in enumerate(items):a(addiu('t0','zero',item),sh('t0',0x2e+i*2,'s1'))
 a(jal(0x162e78),addiu('a0','s1',0x24));menu(0x1f8840,4,5)
 visible(-0x5d38,False);visible(-0x5d3c,False);a(jal(0x162990),addiu('a0','zero',1));menu(0x238c80,2,6,y=54)
 a(ld('ra',0xff8,'sp'),ld('s0',0xff0,'sp'),ld('s1',0xfe8,'sp'),ld('s2',0xfe0,'sp'),ld('s3',0xfd8,'sp'),jr('ra'),addiu('sp','sp',0x1000));body=a.assemble()
 if MAIN+len(body)>MAIL:raise ValueError('Private preview overflow '+str(len(body)))
 out[MAIN-BASE:MAIN-BASE+len(body)]=body;return out

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');ap.add_argument('--attempt',type=int,default=1);args=ap.parse_args();folder=ROOT/'work/output/v0.2.30';data=(folder/'SLPS_250.70').read_bytes();info=json.loads((folder/'build_info.json').read_text('utf8'));e=Elf(data);dest=DEST if args.attempt==1 else DEST/f'attempt-{args.attempt}'
 if b.digest(data)!=info['elf_sha256']or e.at(BASE,END-BASE)!=bytes(END-BASE)or e.at(HOOK,8)!=pack([j(0x102530),NOP]):raise ValueError('Cold fixture baseline changed')
 out=bytearray(data);body=payload(e);out[e.offset(BASE):e.offset(BASE)+len(body)]=body;changes=[]
 for va,new in((HOOK,pack([j(BASE),NOP])),(0x161994,pack([jal(MAIN)]))):changes.append(dict(va=va,original=e.at(va,len(new)).hex(),new=new.hex()));out[e.offset(va):e.offset(va)+len(new)]=new
 report=dict(delivery_elf_sha256=b.digest(data),debug_elf_sha256=b.digest(out),private_changes=changes,cases=CASES,scope='Cold New Game with actual formation window constructor and original list, info, generic menu and equipment-detail consumers; synthetic stack-local deck and IDs. Original unlocked formation gameplay route not replayed.')
 print(json.dumps(report,indent=1),flush=True)
 if not args.write:print('DRY no preview written.');return
 dest.mkdir(exist_ok=False);(dest/'SLPS_250.70').write_bytes(out);(dest/'manifest.json').write_text(json.dumps(report,indent=1)+'\n','utf8')
if __name__=='__main__':main()
