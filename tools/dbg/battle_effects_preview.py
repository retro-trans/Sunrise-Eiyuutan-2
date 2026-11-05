"""Cold-boot-only native status/reward preview, separate from delivery.

Intercept New Game initialization once; use the actual scoped status constructor,
getters, renderer, input and reward window. Synthetic stats/items are preview
fixtures, not proof of ordinary battle triggers. No old state or live text writes.
"""
import argparse,json,struct,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from elf import ROOT,Elf
from mips import *
import battle_effects_patch as b

BASE=0x9B78C0;FAKE=BASE+0x280;STRINGS=BASE+0x300;MAIL=0x9B7FC0;END=0x9B8000
DEST=ROOT/'work/ui/battle-effects-preview-0.2.22-r2'
HOOK=0x9A0550

def payload(e):
 out=bytearray(END-BASE);body=[];pool=bytearray()
 # Native stats prefix plus each exact comment loaded through the production
 # getter's rebuilt table pointer. Only the numeric values are synthetic.
 prefix='%3HP%0 45/45 %4EN%0 29/45  %6SP%0 4 Sz 3\nAtk[%1AT%0 39 %4EN%0 18] Def[%2DF%0 31 %4EN%0 29]\n'
 for index in(20,25):
  va=int.from_bytes(e.at(0x1e2f10+index*16+12,4),'little');text=e.at(va,150).split(b'\0')[0].decode('cp932');ptr=STRINGS+len(pool);pool.extend((prefix+text).encode('cp932')+b'\0');body.append(ptr)
 if STRINGS+len(pool)>MAIL:raise ValueError('Native preview text overflow')
 a=Asm(BASE);a(addiu('sp','sp',-0x40),sd('ra',0x30,'sp'),sd('s0',0x20,'sp'),sd('s1',0x10,'sp'),sd('s2',0,'sp'),
  jal(0x102530),NOP,la('s1',MAIL),addiu('v0','zero',1),sw('v0',0,'s1'),
  jal(0x1686A8),NOP,jal(0x1686C8),NOP,move('s0','v0'),sw('v0',8,'s1'),
  move('a0','s0'),jal(0x168798),NOP,
  jal(0x1022C0),NOP,jal(0x12A838),NOP)
 for index,ptr in enumerate(body,1):
  a(move('a0','s0'),la('a1',ptr),jal(0x1687E8),NOP,addiu('v0','zero',index),sw('v0',4,'s1'),jal(0x142F30),addiu('a0','zero',4))
 a(jal(0x168720),move('a0','s0'),addiu('v0','zero',3),sw('v0',4,'s1'),jal(0x170170),NOP,
  addiu('v0','zero',4),sw('v0',4,'s1'),ld('ra',0x30,'sp'),ld('s0',0x20,'sp'),ld('s1',0x10,'sp'),ld('s2',0,'sp'),jr('ra'),addiu('sp','sp',0x40))
 raw=a.assemble()
 if len(raw)>FAKE-BASE:raise ValueError('Native preview driver overflow')
 out[:len(raw)]=raw
 # Native reward records are uint16 item ID/count. HM parts row11 and EN
 # Charger row6 use the real item getters and the original native formatter.
 a=Asm(FAKE);a(addiu('v0','zero',0x712),sh('v0',0,'a0'),addiu('v0','zero',3),sh('v0',2,'a0'),
  addiu('v0','zero',0x6B9),sh('v0',4,'a0'),addiu('v0','zero',1),sh('v0',6,'a0'),jr('ra'),addiu('v0','zero',2))
 raw=a.assemble();out[FAKE-BASE:FAKE-BASE+len(raw)]=raw;out[STRINGS-BASE:STRINGS-BASE+len(pool)]=pool
 return bytes(out)

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');a=ap.parse_args()
 raw=(ROOT/'work/output/v0.2.22/SLPS_250.70').read_bytes();e=Elf(raw);out=bytearray(raw)
 if b.digest(raw)!=json.loads((ROOT/'work/output/v0.2.22/build_info.json').read_text('utf8'))['elf_sha256']:raise ValueError('Final build changed')
 if e.at(BASE,END-BASE)!=bytes(END-BASE):raise ValueError('Preview reservation occupied')
 expected=pack([j(0x102530),NOP])
 if e.at(HOOK,8)!=expected:raise ValueError('Native new-game trampoline changed')
 changes=[(HOOK,expected,pack([j(BASE),NOP])),(0x1702F8,e.at(0x1702F8,8),pack([j(FAKE),NOP]))]
 for va,old,new in changes:out[e.offset(va):e.offset(va)+len(new)]=new
 body=payload(e);out[e.offset(BASE):e.offset(BASE)+len(body)]=body
 report=dict(source_elf_sha256=b.digest(raw),preview_elf_sha256=b.digest(out),code_va=hex(BASE),mail_va=hex(MAIL),size=len(body),words=[dict(va=hex(va),old=old.hex(),new=new.hex())for va,old,new in changes],scope='Native window/rendering preview after New Game initialization; synthetic stats and reward list, no ordinary battle-trigger claim.')
 print(json.dumps(report,indent=1))
 if not a.write:print('DRY: no preview files written.');return
 DEST.mkdir(exist_ok=False);(DEST/'SLPS_250.70').write_bytes(out);(DEST/'build_info.json').write_text(json.dumps(report,indent=1)+'\n','utf8')

if __name__=='__main__':main()
