"""Separate cold-boot lyric playback probe; never edits the delivery image."""
import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from elf import ROOT,Elf
from mips import *
import lyrics_display_patch as b
BASE=0x9B78C0;MAIL=0x9B7FC0;END=0x9B8000;HOOK=0x9A0510
DEST=ROOT/'work/ui/lyrics-display-0.2.23'

def payload():
 a=Asm(BASE);a(addiu('t0','zero',488));a.br('bne','a0','t0','normal');a(NOP)
 a(addiu('sp','sp',-0x40),sd('ra',0x30,'sp'),sd('s0',0x20,'sp'),sd('s1',0x10,'sp'),la('s1',MAIL),addiu('t0','zero',1),sw('t0',0,'s1'),jal(0x102330),addiu('a0','zero',488),sw('v0',0,'sp'),addiu('t0','zero',2),sw('t0',0,'s1'),addiu('a0','zero',5),jal(0x154A80),addiu('a1','zero',1),sw('v0',4,'s1'),ori('s0','zero',4200))
 a.label('wait');a(jal(0x10CD78),NOP,addiu('s0','s0',-1));a.br('bnez','s0','wait');a(NOP)
 a(lw('a0',4,'s1'),jal(0x154C20),NOP,ori('s0','zero',60))
 a.label('cleanup');a(jal(0x10CD78),NOP,addiu('s0','s0',-1));a.br('bnez','s0','cleanup');a(NOP)
 a(addiu('t0','zero',3),sw('t0',0,'s1'),lw('v0',0,'sp'),ld('s1',0x10,'sp'),ld('s0',0x20,'sp'),ld('ra',0x30,'sp'),jr('ra'),addiu('sp','sp',0x40))
 a.label('normal');a(j(0x102330),NOP);raw=a.assemble()
 if BASE+len(raw)>MAIL:raise ValueError('Preview driver overflow')
 return raw

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');args=ap.parse_args();source=ROOT/'work/output/v0.2.23';data=(source/'SLPS_250.70').read_bytes();info=json.loads((source/'build_info.json').read_text('utf8'));e=Elf(data);raw=payload()
 if b.digest(data)!=info['elf_sha256']or e.at(HOOK,4)!=pack([jal(0x102330)])or e.at(BASE,END-BASE)!=bytes(END-BASE):raise ValueError('Cold preview baseline or allocation changed')
 print('PLAN: final0.2.23 ISO + separate guarded ELF; complete OP488, native ending STREAM0 for70s, stop/cleanup. Read/input/capture only. No old state; actual credits not loaded. Driver',hex(BASE),len(raw))
 if not args.write:print('DRY no files written.');return
 DEST.mkdir(exist_ok=False);out=bytearray(data);out[e.offset(BASE):e.offset(BASE)+len(raw)]=raw;out[e.offset(HOOK):e.offset(HOOK)+4]=pack([jal(BASE)])
 (DEST/'SLPS_250.70').write_bytes(out);(DEST/'manifest.json').write_text(json.dumps(dict(delivery_elf_sha256=b.digest(data),debug_elf_sha256=b.digest(out),driver_va=hex(BASE),driver_bytes=len(raw),hook_va=hex(HOOK),mail_va=hex(MAIL),scope='Complete opening playback and70s ending clock/display/gap/reuse/cleanup; actual credit composition unplayed.'),indent=1)+'\n','utf8')

if __name__=='__main__':main()
