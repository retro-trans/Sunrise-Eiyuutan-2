"""Complete Trade captions and normal-proportion requirement/item columns."""
import argparse,json,struct,hashlib,shutil
from elf import ROOT,PATH,Elf
from iso import records
import formation_polish_patch as prior
import information_patch as columns
from mips import *
BASE_SHA='2b8cdf5c09e8b23e2558e325a50e18294344520f0d3a75572d21bb87edb26581'
BASE=0x9a4460;ROW=BASE;DEFAULT=BASE+0x30;MEASURE=BASE+0x60;NONE=BASE+0x90;RENDER=BASE+0xb0;TEXT=BASE+0x2b0;END=0x9a4800
BUFFER=0x9a7810
ROWS=(
 (0x221bc8,'Trade\u3000Exchange items.\n',((0x13d494,0x13d49c),)),
 (0x221be8,'\x1eItem\tOwned',((0x13d4dc,0x13d4e4),)),
 (0x221c18,'\x1e%s\t%d',((0x13d568,0x13d570),)),
 (0x221c30,'#2%s#2^%d,%d,%2d (Owned %2d)',((0x13d654,0x13d6b8),)),
 (0x221c58,'^0,0,%s^0,28,%s^0,56,Trade the items above for this item.',((0x13d6e8,0x13d6ec),)),
 (0x221c88,'You cannot carry any more.',((0x13dacc,0x13dad4),(0x13dc0c,0x13dc14))),
 (0x221ca0,'Trade requirements are not met.',((0x13db38,0x13db40),)),
 (0x221cc0,"We'll make the trade.\nIs that OK?",((0x13db4c,0x13db58),)),
)
digest=lambda x:hashlib.sha256(x).hexdigest()

def code(e,none):
 out=bytearray(TEXT-BASE)
 def put(at,body,limit):
  if at+len(body)>limit:raise ValueError('Trade code overlap')
  out[at-BASE:at-BASE+len(body)]=body
 a=Asm(ROW);a(lbu('v0',0,'a1'),addiu('v1','zero',30));a.br('beq','v0','v1','trade');a(NOP,j(columns.RENDER),NOP);a.label('trade');a(j(RENDER),NOP);put(ROW,a.assemble(),DEFAULT)
 a=Asm(DEFAULT);a(lbu('v0',0,'a1'),addiu('v1','zero',30));a.br('bne','v0','v1','plain');a(NOP,move('t2','t0'),addiu('t1','zero',26),j(RENDER),addiu('t0','zero',26));a.label('plain');a(j(columns.DEFAULT_RENDER),NOP);put(DEFAULT,a.assemble(),MEASURE)
 a=Asm(MEASURE);a(lbu('v0',0,'a0'),addiu('v1','zero',30));a.br('bne','v0','v1','plain');a(NOP,jr('ra'),addiu('v0','zero',608));a.label('plain');a(j(columns.MEASURE),NOP);put(MEASURE,a.assemble(),NONE)
 a=Asm(NONE);a.br('bnez','a0','normal');a(NOP,la('v0',none),jr('ra'),NOP);a.label('normal');a(j(0x156858),NOP);put(NONE,a.assemble(),RENDER)
 # Private copy of the established two-column renderer, scoped by marker1E.
 # Both dimensions of a long name use22; quantities retain normal26.
 renderer=bytearray(e.at(columns.RENDER,0x200))
 def change(at,old,new):
  off=at-columns.RENDER
  if int.from_bytes(renderer[off:off+4],'little')!=old:raise ValueError('Trade renderer clone guard')
  struct.pack_into('<I',renderer,off,new)
 change(0x9a6484,addiu('v1','zero',31),addiu('v1','zero',30))
 change(0x9a6524,lw('t1',0x14,'sp'),move('t1','t0'))
 for at in(0x9a64f4,0x9a6540):change(at,jal(0x10e510),jal(prior.MEASURE))
 put(RENDER,renderer,TEXT);return out

def patch(data):
 if digest(data)!=BASE_SHA:raise ValueError('Complete 0.2.30 baseline changed')
 e=Elf(data);src=Elf(PATH.read_bytes());out=bytearray(data);payload=bytearray();addresses={};words={};expected={};rows=[]
 if e.at(BASE,END-BASE)!=bytes(END-BASE):raise ValueError('Trade constant tail occupied')
 if e.at(BUFFER,64)!=bytes(64):raise ValueError('Trade formatter buffer tail occupied')
 for va,text,pairs in ROWS:
  raw=src.at(va,256).split(b'\0')[0]+b'\0'
  if e.at(va,len(raw))!=raw:raise ValueError('Trade source object changed')
  ptr=TEXT+len(payload);addresses[hex(va)]=ptr;payload.extend(text.encode('cp932')+b'\0');rows.append(dict(va=va,en=text,source_size=len(raw),source_sha256=digest(raw),pairs=pairs,pointer=ptr))
 none=TEXT+len(payload);payload.extend(b'None\0')
 if TEXT+len(payload)>END:raise ValueError('Trade complete text pool overflow')
 def word(va,old,new):
  if int.from_bytes(e.at(va,4),'little')!=old:raise ValueError('Trade word guard '+hex(va))
  expected[hex(va)]=hex(old);words[hex(va)]=hex(new);struct.pack_into('<I',out,e.offset(va),new)
 for r in rows:
  for high,low in r['pairs']:
   h=int.from_bytes(e.at(high,4),'little');l=int.from_bytes(e.at(low,4),'little')
   if h&65535!=0x22 or l&65535!=r['va']&65535:raise ValueError('Trade reference pair changed')
   word(high,h,h&0xffff0000|hi(r['pointer']));word(low,l,l&0xffff0000|lo(r['pointer']))
 # Reuse the existing marked two-column renderer. Plain subtitles still
 # tail-dispatch to the exact original default renderer.
 word(0x13bbe8,jal(0x110e98),jal(DEFAULT))
 word(0x11248c,jal(columns.RENDER),jal(ROW))
 word(0x112804,jal(columns.MEASURE),jal(MEASURE))
 word(0x13d7e4,move('s4','v0'),addiu('s4','zero',608))
 word(0x13d6bc,addiu('a3','zero',281),addiu('a3','zero',320))
 word(0x13d564,lui('s1',0x52),lui('s1',hi(BUFFER)));word(0x13d56c,addiu('s1','s1',-0x2f48),addiu('s1','s1',lo(BUFFER)))
 word(0x13d690,jal(0x156858),jal(NONE));body=code(e,none)
 out[e.offset(BASE):e.offset(BASE)+len(body)]=body;out[e.offset(TEXT):e.offset(TEXT)+len(payload)]=payload
 return bytes(out),dict(rows=rows,addresses=addresses,none_va=none,patched_words=words,expected_words=expected,payloads=[dict(va=BASE,size=len(body),sha256=digest(body)),dict(va=TEXT,size=len(payload),sha256=digest(payload))],runtime_buffer=dict(va=BUFFER,size=64,previous_size=48),review=dict(rows_examined=8,accuracy='independent native add/subtract direction review',editorial='complete',proofreading='complete',layout='Deliberately replace byte-padding with measured columns and #5 squeezed font with #2 normal font; retain numeric arguments, explicit positions and two-clause confirmation LF.'),geometry=dict(list=[16,92,608,224],name_x=8,quantity_right=600,list_fonts=[[26,26],[22,22]],requirement_name_limit=312,requirement_count_x=320,requirement_count_limit=184,requirement_font=[26,26],help=[18,336,604,96]),recipe_records=128)

def inputs():
 data,packs,overlays,report=prior.inputs();data,trade=patch(data);return data,packs,overlays,dict(report,trade_ui=trade)

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');args=ap.parse_args();old=ROOT/'work/output/v0.2.30';data,trade=patch((old/'SLPS_250.70').read_bytes());print(json.dumps(dict(version='0.2.31',elf_sha256=digest(data),source_objects=8,sample=[r['en']for r in trade['rows']],geometry=trade['geometry'],payloads=trade['payloads']),indent=1),flush=True)
 if not args.write:print('DRY no game files written.');return
 dest=ROOT/'work/output/v0.2.31';dest.mkdir(exist_ok=False);(dest/'SLPS_250.70').write_bytes(data)
 for pattern in('*.pack','*.evemap'):
  for f in old.glob(pattern):shutil.copyfile(f,dest/f.name)
 image=dest/'Sunrise Eiyuutan 2 EN v0.2.31.iso';shutil.copyfile(old/'Sunrise Eiyuutan 2 EN v0.2.30.iso',image);rec=next(x for x in records(image)if x['path']=='/SLPS_250.70')
 if rec['size']!=len(data):raise ValueError('Same-size executable required')
 with image.open('r+b')as f:f.seek(rec['lba']*2048);f.write(data)
 info=json.loads((old/'build_info.json').read_text('utf8'));info.update(version='0.2.31',based_on='0.2.30',trade_ui=trade,elf_sha256=digest(data),iso_path=str(image),iso_size=image.stat().st_size,scope='Complete Trade labels/prompts and normal-proportion requirement rows; wider two-column inventory list. Trade rules and ordinary help layout preserved.',in_game_validation='pending native Trade previews')
 for k in('iso_sha256','native_validation_report'):info.pop(k,None)
 (dest/'build_info.json').write_text(json.dumps(info,indent=1)+'\n','utf8');print('WRITE',image)
if __name__=='__main__':main()
