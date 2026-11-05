"""Cold native save/load list fixture using numeric saved-header indices only."""
import argparse,json,struct,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from elf import ROOT,Elf
import episode_titles_patch as b
from mips import *
BASE=0x9b6000;STUBS=0x9b6200;MAIL=0x9b62c0;END=0x9b6300;HOOK=0x9a0550
DEST=ROOT/'work/ui/episode-titles-0.2.27'
CASES=((2,6),(2,6),(16,12),(1,5),(7,11),(6,3))
STUB_TARGETS=((0x151be0,1,'FileCheck'),(0x1512a8,1,'ConnectCheck'),(0x151778,1,'LoadFile'),(0x1507a0,0,'LastUpdatedIndex'),(0x150280,0,'BottomSaveInfo'),(0x1808f0,0,'CardGetInfo'),(0x150ff8,0,'CardSync'),(0x1503c8,-10,'SelectDataNoWrite'))
def payload():
 a=Asm(BASE);a(addiu('sp','sp',-0x40),sd('ra',0x30,'sp'),sd('s0',0x20,'sp'),sd('s1',0x10,'sp'),jal(0x102530),NOP,jal(0x1022c0),NOP,jal(0x12a838),NOP,la('s0',0x54d610),addiu('t0','zero',30),addiu('t1','zero',1))
 a.label('free');a(sb('t1',0,'s0'),addiu('s0','s0',0x2760),addiu('t0','t0',-1));a.br('bnez','t0','free');a(NOP,la('s0',0x54d610))
 for i,(prefix,title)in enumerate(CASES):
  a(sb('zero',0,'s0'),addiu('t0','zero',prefix),sh('t0',0x1080,'s0'),addiu('t0','zero',title),sh('t0',0x1082,'s0'),addiu('s0','s0',0x2760))
 a(la('s1',MAIL),addiu('t0','zero',1),sw('t0',0,'s1'),addiu('a0','zero',1),jal(0x14fe10),move('a1','zero'),sw('v0',4,'s1'),addiu('t0','zero',2),sw('t0',0,'s1'),move('a0','zero'),jal(0x14fe10),move('a1','zero'),sw('v0',8,'s1'),addiu('t0','zero',3),sw('t0',0,'s1'))
 a.label('end');a(jal(0x10cd78),NOP);a.br('b','end');a(NOP)
 code=a.assemble()
 if len(code)>STUBS-BASE:raise ValueError('Driver overlaps stubs')
 out=bytearray(END-BASE);out[:len(code)]=code
 for i,(_,value,_)in enumerate(STUB_TARGETS):out[STUBS-BASE+i*12:STUBS-BASE+i*12+12]=pack([addiu('v0','zero',value),jr('ra'),NOP])
 return out
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');a=ap.parse_args();folder=ROOT/'work/output/v0.2.27';data=(folder/'SLPS_250.70').read_bytes();info=json.loads((folder/'build_info.json').read_text('utf8'));e=Elf(data)
 if b.digest(data)!=info['elf_sha256'] or e.at(BASE,END-BASE)!=bytes(END-BASE) or e.at(HOOK,8)!=pack([j(0x102530),NOP]):raise ValueError('Cold fixture guard changed')
 out=bytearray(data);body=payload();out[e.offset(BASE):e.offset(BASE)+len(body)]=body;patches=[]
 for i,(va,value,name)in enumerate(STUB_TARGETS):
  out[e.offset(va):e.offset(va)+8]=pack([j(STUBS+i*12),NOP]);patches.append(dict(va=va,name=name,result=value,original=e.at(va,8).hex()))
 out[e.offset(HOOK):e.offset(HOOK)+8]=pack([j(BASE),NOP]);r=dict(delivery_elf_sha256=b.digest(data),debug_elf_sha256=b.digest(out),cases=[dict(prefix=p,title=t)for p,t in CASES],private_stubs=patches,scope='Actual memcFileSelect saved-header extraction, native title getter, fit helper, renderer, row selection and cleanup in Save and Load modes. Numeric headers synthetic, first two duplicate reported indices 2/6, worst-length combination third. Bottom date/player panel suppressed. Private card probes and writes stubbed; physical card persistence and full story startup not certified.')
 print(json.dumps(r,indent=1),flush=True)
 if not a.write:print('DRY no preview written.');return
 DEST.mkdir(exist_ok=False);(DEST/'SLPS_250.70').write_bytes(out);(DEST/'manifest.json').write_text(json.dumps(r,indent=1)+'\n','utf8')
if __name__=='__main__':main()
