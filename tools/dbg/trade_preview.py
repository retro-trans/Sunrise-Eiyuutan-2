"""Cold native Trade menu and common confirmation/alert fixtures."""
import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from elf import ROOT,Elf
import trade_patch as b
from mips import *
BASE=0x9b5c80;MAIN=BASE+0x60;ALERT=BASE+0x500;MAIL=0x9b62c0;END=0x9b6300;HOOK=0x9a0550
DEST=ROOT/'work/ui/trade-0.2.31'
CASES=['Native Trade item and owned columns with normal requirement rows','Native failed Trade requirements alert','Longest Trade item with square fitted font','Native Trade confirmation text','Native inventory-limit alert']

def payload(addresses):
 out=bytearray(END-BASE)
 def put(at,body,limit):
  if at+len(body)>limit:raise ValueError('Private Trade preview overlap')
  out[at-BASE:at-BASE+len(body)]=body
 a=Asm(BASE);a(jal(0x102530),NOP,jal(0x1022c0),NOP,jal(0x12a838),NOP,jal(MAIN),NOP,la('t0',MAIL),addiu('v0','zero',6),sw('v0',0,'t0'));a.label('end');a(jal(0x10cd78),NOP);a.br('b','end');a(NOP);put(BASE,a.assemble(),MAIN)
 a=Asm(MAIN);a(addiu('sp','sp',-0x20),sd('ra',0x18,'sp'),sd('s0',0x10,'sp'),la('s0',MAIL),la('t0',0x51d368))
 for i,v in enumerate((33,126,84)):a(addiu('t1','zero',v),sb('t1',i,'t0'))
 a(la('t0',0x239710),addiu('t1','zero',3),sb('t1',0,'t0'),addiu('t0','zero',1),sw('t0',0,'s0'),jal(0x13d738),NOP,addiu('t0','zero',4),sw('t0',0,'s0'),la('a0',addresses['0x221cc0']),jal(0x1146d0),move('a1','zero'),addiu('t0','zero',5),sw('t0',0,'s0'),la('a0',addresses['0x221c88']),jal(0x1117d0),NOP,ld('ra',0x18,'sp'),ld('s0',0x10,'sp'),jr('ra'),addiu('sp','sp',0x20));put(MAIN,a.assemble(),ALERT)
 a=Asm(ALERT);a(la('t1',MAIL),addiu('t0','zero',2),sw('t0',0,'t1'),j(0x1117d0),NOP);put(ALERT,a.assemble(),MAIL);return out

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');ap.add_argument('--attempt',type=int,default=1);args=ap.parse_args();folder=ROOT/'work/output/v0.2.31';data=(folder/'SLPS_250.70').read_bytes();info=json.loads((folder/'build_info.json').read_text('utf8'));e=Elf(data);dest=DEST if args.attempt==1 else DEST/f'attempt-{args.attempt}'
 if b.digest(data)!=info['elf_sha256']or e.at(BASE,END-BASE)!=bytes(END-BASE)or e.at(HOOK,8)!=pack([j(0x102530),NOP]):raise ValueError('Cold Trade fixture baseline changed')
 out=bytearray(data);body=payload(info['trade_ui']['addresses']);out[e.offset(BASE):e.offset(BASE)+len(body)]=body;changes=[]
 for va,new in((HOOK,pack([j(BASE),NOP])),(0x13db3c,pack([jal(ALERT)]))):changes.append(dict(va=va,original=e.at(va,len(new)).hex(),new=new.hex()));out[e.offset(va):e.offset(va)+len(new)]=new
 report=dict(delivery_elf_sha256=b.digest(data),debug_elf_sha256=b.digest(out),private_changes=changes,cases=CASES,scope='Cold New Game with original Trade menu, item/requirement consumers and failed-condition branch, using three synthetic available recipe IDs. Confirmation and inventory-limit captions use their original common modal functions directly; no game transaction is performed. Original shop-unlock route and full progression not replayed.')
 print(json.dumps(report,indent=1),flush=True)
 if not args.write:print('DRY no preview written.');return
 dest.mkdir(exist_ok=False);(dest/'SLPS_250.70').write_bytes(out);(dest/'manifest.json').write_text(json.dumps(report,indent=1)+'\n','utf8')
if __name__=='__main__':main()
