"""Default squad label for new games and display of existing saved defaults."""
import argparse,json,re,struct
from elf import ROOT,PATH,Elf
import information_patch as prior
from build import make_iso
from mips import *
BASE=0x9B6300
TEXT=BASE+0x100
LIMIT=BASE+0x200
SOURCE=0x220608
BASE_SHA='0cff7521f5ac8b72b7757864bf006d2ffae47d7448499261e6d88c31b8928a8f'
LANGUAGE=ROOT/'work/translation/en/squad_name.en.json'
LANGUAGE_SHA='ac7b22087133049bb016733059071dce6af5f640aa0e0bf36b1ba971aad229ce'
digest=prior.digest
def language():
 raw=LANGUAGE.read_bytes()
 if digest(raw)!=LANGUAGE_SHA:raise ValueError('Squad language revision changed')
 d=json.loads(raw)
 if d['review']!=dict(accuracy='independent-reviewed',editorial='complete',glossary='complete',proofreading='complete'):raise ValueError('Squad review incomplete')
 return d
def code():
 a=Asm(BASE);a(move('t0','v0'),lui('t1',hi(SOURCE)),addiu('t1','t1',lo(SOURCE)))
 a.label('compare');a(lbu('t2',0,'t0'),lbu('t3',0,'t1'));a.br('bne','t2','t3','done');a(NOP);a.br('beqz','t2','match');a(addiu('t0','t0',1));a.br('b','compare');a(addiu('t1','t1',1))
 a.label('match');a(move('t0','v0'),lui('t1',hi(TEXT)),addiu('t1','t1',lo(TEXT)))
 a.label('copy');a(lbu('t2',0,'t1'),addiu('t1','t1',1),sb('t2',0,'t0'));a.br('bnez','t2','copy');a(addiu('t0','t0',1));a.label('done');a(jr('ra'),NOP)
 raw=a.assemble()
 if len(raw)>TEXT-BASE:raise ValueError('Squad helper overflow')
 return raw
def patch(data):
 if digest(data)!=BASE_SHA:raise ValueError('Complete0.2.17 baseline changed')
 e=Elf(data);d=language();r=d['rows'][0];source=e.at(SOURCE,r['source_size']);text=r['en'].encode('cp932')+b'\0'
 if digest(source)!=r['source_sha256']or source[-1:]!=b'\0':raise ValueError('Default source changed')
 if len(text)>16:raise ValueError('Default exceeds native name capacity')
 if e.at(BASE,LIMIT-BASE)!=bytes(LIMIT-BASE):raise ValueError('Squad gap occupied')
 out=bytearray(data);body=code();out[e.offset(BASE):e.offset(BASE)+len(body)]=body;out[e.offset(TEXT):e.offset(TEXT)+len(text)]=text;words={};expected={}
 for site,old,new in [(0x10259C,0x3c060022,0x3c060000|hi(TEXT)),(0x1025AC,0x24c60608,0x24c60000|lo(TEXT)),(0x167A1C,jr('ra'),j(BASE))]:
  if e.at(site,4)!=struct.pack('<I',old):raise ValueError('Squad guard %08X'%site)
  expected[hex(site)]=hex(old);words[hex(site)]=hex(new);struct.pack_into('<I',out,e.offset(site),new)
 return bytes(out),dict(language_sha256=LANGUAGE_SHA,patched_words=words,expected_words=expected,code_va=hex(BASE),code_size=len(body),code_sha256=digest(body),text_va=hex(TEXT),text_size=len(text),text_sha256=digest(text),source_va=hex(SOURCE),name_bytes_including_NUL=len(text),existing_save_behavior='Exact default name mapping in temporary display buffer only; saved records and custom names unchanged.')
def inputs():
 data,packs,overlays,report=prior.inputs();data,r=patch(data);return data,packs,overlays,dict(**report,squad_name_ui=r)
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('version');ap.add_argument('--write',action='store_true');a=ap.parse_args()
 if not re.fullmatch(r'0\.\d+\.\d+',a.version):raise ValueError('Version0.x.y required')
 data,packs,overlays,report=inputs();print(json.dumps(dict(version=a.version,elf_sha256=digest(data),squad_name=report['squad_name_ui']),indent=1))
 if not a.write:print('DRY: no game files/ISO written.');return
 dest=ROOT/'work/output'/('v'+a.version)
 if dest.exists():raise FileExistsError(dest)
 dest.mkdir();(dest/'SLPS_250.70').write_bytes(data)
 for n,p in packs.items():(dest/f'{n:05d}.pack').write_bytes(p)
 for n,p in overlays.items():(dest/f'{n:05d}.evemap').write_bytes(p)
 image=dest/('Sunrise Eiyuutan 2 EN v'+a.version+'.iso');make_iso(image,data,packs,overlays)
 info=json.loads((ROOT/'work/output/v0.2.17/build_info.json').read_text('utf8'));info.update(version=a.version,based_on='0.2.17',**report,elf_sha256=digest(data),iso_path=str(image),iso_size=image.stat().st_size,in_game_validation='pending squad-label validation',scope='Default squad name, retaining complete0.2.17 and Japanese voices.')
 for key in ('iso_sha256','native_validation_report','information_validation'):info.pop(key,None)
 (dest/'build_info.json').write_text(json.dumps(info,indent=1)+'\n','utf8');print('WRITE',image)
if __name__=='__main__':main()
