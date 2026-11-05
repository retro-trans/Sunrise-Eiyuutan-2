"""Cold-only native card warnings and short/long/short status layout preview."""
import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from elf import ROOT,Elf
import card_dialog_patch as b
from mips import *
BASE=0x9B7B00;TEXT=0x9B7D00;MAIL=0x9B7FC0;END=0x9B8000;HOOK=0x9A0550
DEST=ROOT/'work/ui/card-dialog-0.2.24'

def payload(e,info):
 repair=int(info['battle_details']['addresses']['0x22eb90'],16)
 expected="Restore a unit's HP.\nBy consuming more battleship EN,\nyou can restore more HP."
 if e.at(repair,120).split(b'\0')[0].decode('cp932')!=expected:raise ValueError('Production repair text changed')
 comment=int.from_bytes(e.at(0x1e2f10+25*16+12,4),'little');comment=e.at(comment,180).split(b'\0')[0].decode('cp932')
 prefix='%3HP%0 45/45 %4EN%0 29/45  %6SP%0 4 Sz 3\nAtk[%1AT%0 39 %4EN%0 18] Def[%2DF%0 31 %4EN%0 29]\n';text=(prefix+comment).encode('cp932')+b'\0'
 if len(text)>256 or len(text)+TEXT>MAIL:raise ValueError('Preview detail fixture exceeds native buffer')
 a=Asm(BASE);a(addiu('sp','sp',-0x40),sd('ra',0x30,'sp'),sd('s0',0x20,'sp'),sd('s1',0x10,'sp'),jal(0x102530),NOP,la('s1',MAIL),lw('v0',-0x776c,'gp'),sw('v0',0,'sp'),jal(0x1022C0),NOP,jal(0x12A838),NOP)
 for phase,mode in((1,1),(2,2)):
  a(addiu('v0','zero',phase),sw('v0',0,'s1'),addiu('v0','zero',mode),sw('v0',-0x776c,'gp'),move('a0','zero'),jal(0x152100),addiu('a1','zero',3))
 a(lw('v0',0,'sp'),sw('v0',-0x776c,'gp'),jal(0x1686A8),NOP,jal(0x1686C8),NOP,move('s0','v0'),sw('v0',4,'s1'),move('a0','s0'),jal(0x168798),NOP,move('a0','s0'),move('a1','zero'),jal(0x1687C8),addiu('a2','zero',3))
 for phase,ptr in((3,repair),(4,TEXT),(5,repair)):
  a(move('a0','s0'),la('a1',ptr),jal(0x1687E8),NOP,addiu('v0','zero',phase),sw('v0',0,'s1'),jal(0x142F30),addiu('a0','zero',4))
 a(jal(0x168720),move('a0','s0'),addiu('v0','zero',6),sw('v0',0,'s1'),ld('ra',0x30,'sp'),ld('s0',0x20,'sp'),ld('s1',0x10,'sp'),jr('ra'),addiu('sp','sp',0x40));body=a.assemble()
 if len(body)>TEXT-BASE:raise ValueError('Preview driver overflow')
 return body,text

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');a=ap.parse_args();folder=ROOT/'work/output/v0.2.24';raw=(folder/'SLPS_250.70').read_bytes();e=Elf(raw);info=json.loads((folder/'build_info.json').read_text('utf8'));body,text=payload(e,info)
 if b.digest(raw)!=info['elf_sha256']or e.at(BASE,END-BASE)!=bytes(END-BASE)or e.at(HOOK,8)!=pack([j(0x102530),NOP]):raise ValueError('Cold preview baseline changed')
 out=bytearray(raw);out[e.offset(BASE):e.offset(BASE)+len(body)]=body;out[e.offset(TEXT):e.offset(TEXT)+len(text)]=text;out[e.offset(HOOK):e.offset(HOOK)+8]=pack([j(BASE),NOP]);report=dict(delivery_elf_sha256=b.digest(raw),preview_elf_sha256=b.digest(out),driver_va=hex(BASE),driver_bytes=len(body),fixture_va=hex(TEXT),fixture_bytes=len(text),mail_va=hex(MAIL),scope='Native no-save/corrupt warning renderer with synthetic mode; production repair help, five-line ability fixture, repair help again; ordinary Load Game/battle triggers unplayed.')
 print(json.dumps(report,indent=1))
 if not a.write:print('DRY no preview written.');return
 DEST.mkdir(exist_ok=False);(DEST/'SLPS_250.70').write_bytes(out);(DEST/'manifest.json').write_text(json.dumps(report,indent=1)+'\n','utf8')

if __name__=='__main__':main()
