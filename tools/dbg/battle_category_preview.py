"""Cold-only physical battle-bank and native SP rendering probe."""
import argparse,json,struct,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from elf import ROOT,Elf
import battle_category_patch as b
from mips import *
from tutorial_preview import NATIVE
BASE=0x9B7B00;BRIDGE=BASE+0xC0;STUBS=0x9B7D40;SHIP=0x9B7E40;UNIT=0x9B7E80;ROWS=0x9B7EC0;MAIL=0x9B7FC0;END=0x9B8000;HOOK=0x9A0550;MESSAGE_HOOK=0x12C820
IDS=(5328,5329,5641,3272,3303,2244)
DEST=ROOT/'work/ui/battle-category-0.2.25-r5'

def payload(e):
 a=Asm(BASE);a(addiu('sp','sp',-0x60),sd('ra',0x50,'sp'),sd('s0',0x40,'sp'),sd('s1',0x30,'sp'),jal(0x102530),NOP,la('s1',MAIL),jal(0x1022C0),NOP,jal(0x12A838),NOP,addiu('t0','zero',1),sw('t0',0,'s1'),la('a0',SHIP),la('a1',UNIT),jal(0x16E950),NOP,sw('v0',16,'s1'),addiu('t0','zero',4),sw('t0',0,'s1'),ld('ra',0x50,'sp'),ld('s0',0x40,'sp'),ld('s1',0x30,'sp'),jr('ra'),addiu('sp','sp',0x60));start=a.assemble()
 if len(start)>BRIDGE-BASE:raise ValueError('SP driver overflow')
 a=Asm(BRIDGE);a(la('t0',MAIL),lw('t1',0,'t0'),addiu('t2','zero',4));a.br('bne','t1','t2','original');a(NOP)
 a(addiu('sp','sp',-0x60),sd('ra',0x50,'sp'),sd('s0',0x40,'sp'),sd('s1',0x30,'sp'),la('s1',MAIL),sw('a0',20,'s1'),sw('a1',24,'s1'),sw('a2',28,'s1'),sw('ra',32,'s1'),addiu('t0','zero',2),sw('t0',0,'s1'))
 for profile,file,member in((1,23,10512),(2,4972,11849)):
  a(addiu('t0','zero',profile),sw('t0',4,'s1'),move('s0','zero'))
  a.label('loop'+str(profile));a(la('t0',ROWS),sll('t1','s0',1),addu('t0','t0','t1'),lhu('a2',0,'t0'),sw('a2',8,'s1'),addiu('a0','zero',file),addiu('a1','zero',member),move('a3','zero'),jal(NATIVE),NOP,addiu('s0','s0',1),sw('s0',12,'s1'),sltiu('t0','s0',len(IDS)));a.br('bnez','t0','loop'+str(profile));a(NOP)
 a(addiu('t0','zero',3),sw('t0',0,'s1'),ld('ra',0x50,'sp'),ld('s0',0x40,'sp'),ld('s1',0x30,'sp'),jr('ra'),addiu('sp','sp',0x60));a.label('original');a(*struct.unpack('<2I',e.at(MESSAGE_HOOK,8)),j(MESSAGE_HOOK+8),NOP);code=a.assemble()
 if BRIDGE+len(code)>STUBS:raise ValueError('Preview code overflow')
 out=bytearray(END-BASE);out[:len(start)]=start;out[BRIDGE-BASE:BRIDGE-BASE+len(code)]=code;out[SHIP-BASE+8:SHIP-BASE+10]=struct.pack('<H',70);out[ROWS-BASE:ROWS-BASE+len(IDS)*2]=struct.pack('<6H',*IDS)
 blocks=((0x15C098,STUBS,addiu('v0','zero',34)),(0x16EB90,STUBS+64,move('v0','zero')),(0x145830,STUBS+128,NOP),(0x145808,STUBS+192,NOP))
 patches=[]
 for at,stub,fake_return in blocks:
  a=Asm(stub);a(la('at',MAIL),lw('at',0,'at'),addiu('v0','zero',1));a.br('bne','at','v0','normal');a(NOP);a(jr('ra'),fake_return);a.label('normal');a(*struct.unpack('<2I',e.at(at,8)),j(at+8),NOP);body=a.assemble()
  if len(body)>64:raise ValueError('Conditional fixture stub overflow')
  out[stub-BASE:stub-BASE+len(body)]=body;patches.append((at,e.at(at,8),pack([j(stub),NOP])))
 return out,patches

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');a=ap.parse_args();folder=ROOT/'work/output/v0.2.25';data=(folder/'SLPS_250.70').read_bytes();info=json.loads((folder/'build_info.json').read_text('utf8'));e=Elf(data)
 if b.digest(data)!=info['elf_sha256']or e.at(BASE,END-BASE)!=bytes(END-BASE)or e.at(HOOK,8)!=pack([j(0x102530),NOP])or e.at(MESSAGE_HOOK,8)!=bytes.fromhex('c0ffbd2701000224'):raise ValueError('Cold preview baseline changed')
 body,patches=payload(e);patches=[];struct.pack_into('<I',body,MAIL-BASE,4);out=bytearray(data);out[e.offset(BASE):e.offset(BASE)+len(body)]=body;patches.append((MESSAGE_HOOK,e.at(MESSAGE_HOOK,8),pack([j(BRIDGE),NOP])))
 for at,old,new in patches:out[e.offset(at):e.offset(at)+len(new)]=new
 report=dict(delivery_elf_sha256=b.digest(data),debug_elf_sha256=b.digest(out),driver_va=hex(BASE),mail_va=hex(MAIL),rows=list(IDS),profiles=['00022_10512','04971_11849'],patches=[dict(va=hex(at),old=old.hex(),new=new.hex())for at,old,new in patches],scope='Ordinary cold boot with original New Game and all getter/cost functions intact. A guarded native renderer entry forces six file/message/voice/portrait paths at both physical banks; ordinary battle triggers not replayed. SP rendering is separately recorded in r2.')
 print(json.dumps(report,indent=1))
 if not a.write:print('DRY no debug files written.');return
 DEST.mkdir(exist_ok=False);(DEST/'SLPS_250.70').write_bytes(out);(DEST/'manifest.json').write_text(json.dumps(report,indent=1)+'\n','utf8')

if __name__=='__main__':main()
