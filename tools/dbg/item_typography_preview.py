"""Cold native reward windows with the reported items and related glyph cases."""
import argparse,json,struct,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from elf import ROOT,Elf
import item_typography_patch as b
from mips import *
BASE=0x9b6000;FAKE=0x9b6140;DATA=0x9b6200;MAIL=0x9b62c0;END=0x9b6300;HOOK=0x9a0550
DEST=ROOT/'work/ui/item-typography-0.2.28'
LABELS=(('HM Parts LvB','Repair Materials Lv2'),('HM Parts LvA','AB Parts LvB','General-Purpose Materials Lv4','PMD-J','Repair Materials Lv2'))
ID_BASE={'it_devi_info':0x5d2,'it_expend_info':0x6b3,'it_mchdev_info':0x613,'it_parts_info':0x6c1,'it_junk_info':0x707}
def cases():
 d=b.language();result=[]
 for phase,labels in enumerate(LABELS,1):
  items=[]
  for label in labels:
   matches=[(r,f)for r in d['rows']for f in r['refs']if r['en']==label and f['field']==8];r,f=matches[0];items.append(dict(id=ID_BASE[f['table']]+f['row'],en=label,quantity=4 if phase==1 and label=='HM Parts LvB'else 1))
  result.append(items)
 return result
def payload():
 groups=cases();out=bytearray(END-BASE);a=Asm(BASE);a(addiu('sp','sp',-32),sd('ra',24,'sp'),sd('s0',16,'sp'),jal(0x102530),NOP,jal(0x1022c0),NOP,jal(0x12a838),NOP,la('s0',MAIL))
 for phase in(1,2):a(addiu('v0','zero',phase),sw('v0',0,'s0'),jal(0x170170),NOP)
 a(addiu('v0','zero',3),sw('v0',0,'s0'));a.label('end');a(jal(0x10cd78),NOP);a.br('b','end');a(NOP);code=a.assemble()
 if BASE+len(code)>FAKE:raise ValueError('Preview driver overflow')
 out[:len(code)]=code;a=Asm(FAKE);a(la('t0',MAIL),lw('t0',0,'t0'),addiu('t1','zero',1));a.br('beq','t0','t1','first');a(NOP,la('t0',DATA+32),addiu('v0','zero',len(groups[1])));a.br('b','copy');a(NOP)
 a.label('first');a(la('t0',DATA),addiu('v0','zero',len(groups[0])));a.label('copy');a(move('t1','v0'));a.label('loop');a(lw('t2',0,'t0'),sw('t2',0,'a0'),addiu('t0','t0',4),addiu('a0','a0',4),addiu('t1','t1',-1));a.br('bnez','t1','loop');a(NOP,jr('ra'),NOP);code=a.assemble()
 if FAKE+len(code)>DATA:raise ValueError('Preview provider overflow')
 out[FAKE-BASE:FAKE-BASE+len(code)]=code
 for phase,group in enumerate(groups):
  for i,item in enumerate(group):struct.pack_into('<HH',out,DATA-BASE+phase*32+i*4,item['id'],item['quantity'])
 return out
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');a=ap.parse_args();folder=ROOT/'work/output/v0.2.28';data=(folder/'SLPS_250.70').read_bytes();info=json.loads((folder/'build_info.json').read_text('utf8'));e=Elf(data)
 if b.digest(data)!=info['elf_sha256'] or e.at(BASE,END-BASE)!=bytes(END-BASE) or e.at(HOOK,8)!=pack([j(0x102530),NOP]):raise ValueError('Cold reward fixture guard changed')
 out=bytearray(data);body=payload();out[e.offset(BASE):e.offset(BASE)+len(body)]=body;changes=[]
 for va,new in((HOOK,pack([j(BASE),NOP])),(0x1702f8,pack([j(FAKE),NOP]))):changes.append(dict(va=va,original=e.at(va,8).hex(),new=new.hex()));out[e.offset(va):e.offset(va)+8]=new
 r=dict(delivery_elf_sha256=b.digest(data),debug_elf_sha256=b.digest(out),cases=cases(),private_changes=changes,scope='Actual reward constructor, item dispatch/getters, formatter, glyph renderer, wait/cleanup and in-memory inventory grants. Synthetic reward lists after New Game initialization; original battle victory triggers and physical saves not replayed.')
 print(json.dumps(r,indent=1),flush=True)
 if not a.write:print('DRY no preview written.');return
 DEST.mkdir(exist_ok=False);(DEST/'SLPS_250.70').write_bytes(out);(DEST/'manifest.json').write_text(json.dumps(r,indent=1)+'\n','utf8')
if __name__=='__main__':main()
