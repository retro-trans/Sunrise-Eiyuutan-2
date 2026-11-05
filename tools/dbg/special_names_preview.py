"""Separate cold ELF exercising the original special-name selector renderer."""
import argparse,json,struct,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from elf import ROOT,Elf
import special_names_patch as b
from mips import *
BASE=0x9b7e00;DATA=0x9b7f60;FLAGS=0x9b7f80;MAIL=0x9b7fc0;END=0x9b8000;HOOK=0x9a0550
CASES=((1,0),(45,0),(116,0),(32,0),(94,0),(1,128))
DEST=ROOT/'work/ui/special-names-0.2.26'
def payload():
 a=Asm(BASE);a(addiu('sp','sp',-0x40),sd('ra',0x30,'sp'),sd('s0',0x20,'sp'),sd('s1',0x10,'sp'),jal(0x102530),NOP,jal(0x1022c0),NOP,jal(0x12a838),NOP,move('s0','zero'),la('s1',MAIL))
 a.label('loop');a(la('a0',DATA),sll('t0','s0',2),addu('a0','a0','t0'),lhu('t1',2,'a0'),la('a2',FLAGS),sw('t1',0,'a2'),addiu('t0','s0',1),sw('t0',0,'s1'),sw('s0',4,'s1'),addiu('a1','zero',1),jal(0x16f208),NOP,sll('t0','s0',2),addu('t0','s1','t0'),sw('v0',16,'t0'),addiu('s0','s0',1),sltiu('t0','s0',len(CASES)))
 a.br('bnez','t0','loop');a(NOP,addiu('t0','zero',len(CASES)+1),sw('t0',0,'s1'),ld('ra',0x30,'sp'),ld('s0',0x20,'sp'),ld('s1',0x10,'sp'),jr('ra'),addiu('sp','sp',0x40));code=a.assemble()
 if BASE+len(code)>DATA:raise ValueError('Preview code overlaps data')
 out=bytearray(END-BASE);out[:len(code)]=code
 for i,(row,flag)in enumerate(CASES):struct.pack_into('<2H',out,DATA-BASE+i*4,row,flag)
 return out

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');a=ap.parse_args();base=ROOT/'work/output/v0.2.26';data=(base/'SLPS_250.70').read_bytes();info=json.loads((base/'build_info.json').read_text('utf8'));e=Elf(data)
 if b.digest(data)!=info['elf_sha256']or e.at(BASE,END-BASE)!=bytes(END-BASE)or e.at(HOOK,8)!=pack([j(0x102530),NOP]):raise ValueError('Cold preview baseline changed')
 out=bytearray(data);body=payload();out[e.offset(BASE):e.offset(BASE)+len(body)]=body;out[e.offset(HOOK):e.offset(HOOK)+8]=pack([j(BASE),NOP]);report=dict(delivery_elf_sha256=b.digest(data),debug_elf_sha256=b.digest(out),base=hex(BASE),mail=hex(MAIL),cases=[dict(row=r,flag=f)for r,f in CASES],scope='Actual bspcSelSpcLst/getters/font/measurement/selection/cleanup on six synthetic one-choice requests after New Game initialization. Both selector sides; original battlefield triggers not replayed.')
 print(json.dumps(report,indent=1),flush=True)
 if not a.write:print('DRY no preview written.');return
 DEST.mkdir(exist_ok=False);(DEST/'SLPS_250.70').write_bytes(out);(DEST/'manifest.json').write_text(json.dumps(report,indent=1)+'\n','utf8')
if __name__=='__main__':main()
