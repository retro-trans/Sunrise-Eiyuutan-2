"""Formation submenu translation, pilot proportions and equipment readability."""
import argparse,json,struct,shutil,hashlib
from elf import ROOT,Elf
import formation_readability_patch as prior
from iso import records
from mips import *
BASE_SHA='1722f35ebe17fe1b07c0b82e267923827eedbdcd54b7d4595f79d23ea7a56b9d'
BASE=0x9a3aa0;MEASURE=BASE+0x180;PILOT=BASE+0x240;TEXT=BASE+0x360;END=0x9a4000
MENUS={0x1f8830:'Attack',0x1f8834:'Defend',0x1f8838:'Special',0x1f8840:'Equipment 1',0x1f8844:'Equipment 2',0x1f8848:'Equipment 3',0x1f884c:'Equipment S',0x238c84:'Captain'}
UNMANNED=(32,34,38,40,42,44,46,48)
digest=lambda b:hashlib.sha256(b).hexdigest()

def code(fmt):
 a=Asm(BASE);a(addiu('sp','sp',-0x300),sd('ra',0x2f8,'sp'),sd('s0',0x2f0,'sp'),sd('s1',0x2e8,'sp'),sd('s2',0x2e0,'sp'),sd('s3',0x2d8,'sp'),sd('s4',0x2d0,'sp'),sd('s5',0x2c8,'sp'),move('s0','a0'),jal(0x15c058),NOP,jal(0x154f88),move('a0','v0'),move('s1','v0'),addiu('s2','zero',1),addiu('s4','sp',0x20),move('s5','s4'),sb('zero',0,'s4'))
 a.br('beqz','s1','finish');a(NOP,sltiu('v0','s1',4));a.br('bnez','v0','line');a(NOP,addiu('s1','zero',3))
 a.label('line');a(move('a0','s0'),jal(0x15cbd0),move('a1','s2'),jal(0x156090),move('a0','v0'),move('a3','v0'),addiu('a0','sp',0x140),la('a1',fmt),jal(0x19f1c0),move('a2','s2'),addiu('a0','sp',0x142),jal(MEASURE),addiu('a1','zero',26),sltiu('v0','v0',505));a.br('bnez','v0','large');a(NOP,addiu('a0','sp',0x142),jal(MEASURE),addiu('a1','zero',20),sltiu('v0','v0',505));a.br('bnez','v0','medium');a(NOP,addiu('v0','zero',48));a.br('b','chosen');a(NOP)
 a.label('large');a.br('b','chosen');a(addiu('v0','zero',50));a.label('medium');a(addiu('v0','zero',49));a.label('chosen');a(sb('v0',0x141,'sp'),sltiu('v0','s2',2));a.br('bnez','v0','copy');a(addiu('s3','sp',0x140),addiu('v0','zero',10),sb('v0',0,'s4'),addiu('s4','s4',1))
 a.label('copy');a(lbu('v0',0,'s3'),sb('v0',0,'s4'));a.br('beqz','v0','next');a(addiu('s3','s3',1));a.br('b','copy');a(addiu('s4','s4',1));a.label('next');a(sltu('v0','s2','s1'));a.br('bnez','v0','line');a(addiu('s2','s2',1))
 a.label('finish');a.br('beqz','s1','set');a(NOP,addiu('t0','zero',35),sb('t0',0,'s4'),addiu('t0','zero',50),sb('t0',1,'s4'),sb('zero',2,'s4'));a.label('set');a(lw('a0',-0x690c,'gp'),jal(0x1687e8),move('a1','s5'),ld('ra',0x2f8,'sp'),ld('s0',0x2f0,'sp'),ld('s1',0x2e8,'sp'),ld('s2',0x2e0,'sp'),ld('s3',0x2d8,'sp'),ld('s4',0x2d0,'sp'),ld('s5',0x2c8,'sp'),jr('ra'),addiu('sp','sp',0x300));body=a.assemble()
 if BASE+len(body)>MEASURE:raise ValueError('Equipment helper exceeds proven free gap')
 out=bytearray(TEXT-BASE);out[:len(body)]=body
 # The message parser advances by glyph width PLUS two pixels. Its ordinary
 # string measurer omits that inter-character advance. Mirror the actual
 # parser instead of underestimating the final rendered line.
 a=Asm(MEASURE);a(addiu('sp','sp',-0x30),sd('ra',0x28,'sp'),sd('s0',0x20,'sp'),sd('s1',0x18,'sp'),sd('s2',0x10,'sp'),move('s0','a0'),move('s1','a1'),move('s2','zero'));a.label('glyph');a(lbu('a0',0,'s0'));a.br('beqz','a0','done');a(sltiu('v0','a0',128));a.br('beqz','v0','wide');a(NOP,jal(0x9a4100),move('a1','s1'),addu('s2','s2','v0'));a.br('b','advance');a(addiu('s0','s0',1));a.label('wide');a(addu('s2','s2','s1'),addiu('s0','s0',2));a.label('advance');a.br('b','glyph');a(addiu('s2','s2',2));a.label('done');a(move('v0','s2'),ld('ra',0x28,'sp'),ld('s0',0x20,'sp'),ld('s1',0x18,'sp'),ld('s2',0x10,'sp'),jr('ra'),addiu('sp','sp',0x30));body=a.assemble()
 if MEASURE+len(body)>PILOT:raise ValueError('Glyph measure overlaps pilot wrapper')
 out[MEASURE-BASE:MEASURE-BASE+len(body)]=body
 pilot=bytearray(prior.code()[:0x100]);old=pack([jal(0x10e510)])
 if pilot.count(old)!=1:raise ValueError('Pilot wrapper measure changed')
 pilot=pilot.replace(old,pack([jal(MEASURE)]));out[PILOT-BASE:PILOT-BASE+len(pilot)]=pilot
 return bytes(out)

def patch(data):
 if digest(data)!=BASE_SHA:raise ValueError('Complete 0.2.29 baseline changed')
 e=Elf(data);out=bytearray(data);payload=bytearray();strings={};words={};expected={};fields=[]
 if e.at(BASE,END-BASE)!=bytes(END-BASE):raise ValueError('Formation tail gap occupied')
 def allocate(text):
  if text not in strings:strings[text]=TEXT+len(payload);payload.extend(text.encode('cp932')+b'\0')
  return strings[text]
 def word(va,old,new):
  if int.from_bytes(e.at(va,4),'little')!=old:raise ValueError('Word guard '+hex(va))
  expected[hex(va)]=hex(old);words[hex(va)]=hex(new);struct.pack_into('<I',out,e.offset(va),new)
 for site,text in MENUS.items():
  old=int.from_bytes(e.at(site,4),'little');ptr=allocate(text);word(site,old,ptr);fields.append(dict(site=site,old_pointer=old,pointer=ptr,en=text,category='submenu'))
 for i in UNMANNED:
  site=0x1cd310+i*64;ptr=int.from_bytes(e.at(site,4),'little');old=e.at(ptr,120).split(b'\0')[0].decode('cp932')
  if not old.endswith(' (Unmanned Unit)'):raise ValueError('Unmanned label changed')
  text=old.replace(' (Unmanned Unit)',' (Unmanned)');new=allocate(text)
  for off in(0,4,8):word(site+off,ptr,new);fields.append(dict(site=site+off,old_pointer=ptr,pointer=new,en=text,category='machine',row=i))
 fmt=allocate('#2Equipment %d:%s');body=code(fmt)
 if TEXT+len(payload)>END:raise ValueError('Complete caption pool overflow')
 word(0x166a54,jal(0x112868),jal(PILOT))
 word(0x162e78,addiu('sp','sp',-0xd0),j(BASE));word(0x162e7c,sd('s3',0xb0,'sp'),NOP)
 out[e.offset(BASE):e.offset(BASE)+len(body)]=body;out[e.offset(TEXT):e.offset(TEXT)+len(payload)]=payload
 return bytes(out),dict(fields=fields,patched_words=words,expected_words=expected,payloads=[dict(va=BASE,size=len(body),sha256=digest(body)),dict(va=TEXT,size=len(payload),sha256=digest(payload))],review=dict(accuracy='independent seven-menu review',editorial='complete',proofreading='complete',unmanned='explicit user wording',captain='explicit user alignment'),equipment=dict(fonts=[26,20,13],limit=504,max_rows=3,buffer_bytes=256,normal_geometry=[18,336,604,96],format_va=fmt),pilot_call=0x166a54,unmanned_records=8)

def inputs():
 data,packs,overlays,report=prior.inputs();data,ui=patch(data);return data,packs,overlays,dict(report,formation_polish=ui)

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');args=ap.parse_args();old=ROOT/'work/output/v0.2.29';data,ui=patch((old/'SLPS_250.70').read_bytes());print(json.dumps(dict(version='0.2.30',elf_sha256=digest(data),sample=[r['en']for r in ui['fields'][:9]],fields=len(ui['fields']),payloads=ui['payloads'],equipment=ui['equipment']),indent=1),flush=True)
 if not args.write:print('DRY no game files written.');return
 dest=ROOT/'work/output/v0.2.30';dest.mkdir(exist_ok=False);(dest/'SLPS_250.70').write_bytes(data)
 for pattern in('*.pack','*.evemap'):
  for f in old.glob(pattern):shutil.copyfile(f,dest/f.name)
 image=dest/'Sunrise Eiyuutan 2 EN v0.2.30.iso';shutil.copyfile(old/'Sunrise Eiyuutan 2 EN v0.2.29.iso',image);rec=next(x for x in records(image)if x['path']=='/SLPS_250.70')
 if rec['size']!=len(data):raise ValueError('Same-size executable required')
 with image.open('r+b')as f:f.seek(rec['lba']*2048);f.write(data)
 info=json.loads((old/'build_info.json').read_text('utf8'));info.update(version='0.2.30',based_on='0.2.29',formation_polish=ui,elf_sha256=digest(data),iso_path=str(image),iso_size=image.stat().st_size,scope='Eight Unmanned machine captions, proportional pilot lists, all action/equipment submenu captions, larger fitted equipment details and aligned Ship/Captain.',in_game_validation='pending native formation polish previews')
 for k in('iso_sha256','native_validation_report'):info.pop(k,None)
 (dest/'build_info.json').write_text(json.dumps(info,indent=1)+'\n','utf8');print('WRITE',image)
if __name__=='__main__':main()
