"""v0.2.24: finish memory-card warning text and restore ordinary status/help boxes.

The shared status box defaults to stock geometry. Only complete text exceeding
three lines expands it, using the already allocated five-line text surface.
"""
import argparse,json,struct,hashlib
from elf import ROOT,PATH,Elf
from build import make_iso
from iso import records
from mips import *
import lyrics_display_patch as prior

BASE_SHA='cf5c19161a226ad355ef2fffacbd8ce6ecfe1fbfc1cfcdf2e87b71e9d0897f5f'
BASE=0x9B78C0;TEXT=0x9B79C0;END=0x9B7AC0
LANGUAGE=ROOT/'work/translation/en/card-dialog.en.json'
DRAWS=(0x168838,0x168978,0x168B14,0x168CD0,0x168E50,0x168F24,0x168FF4,0x169124,0x1691BC,0x16931C,0x1695B4)
REFS=((0x224E98,0x152248,0x152250),(0x224E98,0x15229C,0x1522A4),(0x224EB0,0x152260,0x15226C),(0x224ED0,0x1522B4,0x1522BC))
digest=prior.digest

def export():
 source=json.loads((ROOT/'work/source/candidates/ELF/rodata.json').read_text('utf8'))
 if isinstance(source,dict):source=source['rows']
 rows=[];wording={0x224E98:'Sunrise Eiyuutan 2',0x224EB0:'There is no save data.',0x224ED0:'The save data is corrupted.'};e=Elf(PATH.read_bytes())
 for va,en in wording.items():
  row=next(r for r in source if r.get('va')==va);raw=e.at(va,row['size'])
  if raw.hex()!=row['raw']:raise ValueError('Memory warning source corpus mismatch')
  rows.append(dict(id=row['id'],va=va,source_size=row['size'],source_sha256=digest(raw),en=en))
 return dict(version='0.2.24',review=dict(accuracy='independent-reviewed',editorial='complete',glossary='complete',proofreading='complete'),review_scope='Three target rows; independent reviewer examined15 adjacent corpus rows187..201. Separately drawn title label removes dangling possessive; absent/corrupt complete sentences retained from reviewed proposals.',reviewer='memory_card_language',uncertainty='Both title references confirmed in memcPutWarningMes no-save/corrupt branches; no inline title consumer found.',rows=rows)

def language():
 d=json.loads(LANGUAGE.read_text('utf8'))
 if d!=export():raise ValueError('Reviewed card wording/source revision changed')
 return d

def code():
 a=Asm(BASE)
 # Preserve a0/a1/v0/v1/ra and the caller's delay slot. Bound scanning to the
 # native256-byte status string buffer; all current complete bodies fit it.
 a(move('t0','a1'),addiu('t1','zero',1),addiu('t2','zero',10),addiu('t3','zero',256))
 a.label('scan');a(lbu('t4',0,'t0'));a.br('beqz','t4','layout');a(addiu('t0','t0',1))
 a.br('bne','t4','t2','next');a(NOP);a(addiu('t1','t1',1))
 a.label('next');a(addiu('t3','t3',-1));a.br('bnez','t3','scan');a(NOP)
 a.label('layout');a(sltiu('t0','t1',4),addiu('t1','zero',336),addiu('t2','zero',96),addiu('t3','zero',84))
 a.br('bnez','t0','apply');a(NOP);a(addiu('t1','zero',280),addiu('t2','zero',152),addiu('t3','zero',140))
 a.label('apply');a(sw('t1',0x30,'a0'),lw('t0',0x18,'a0'));a.br('beqz','t0','text');a(NOP)
 a(sw('t1',0x1c,'t0'),sw('t2',0x24,'t0'))
 a.label('text');a(lw('t0',4,'a0'));a.br('beqz','t0','return');a(NOP);a(lw('t0',0,'t0'));a.br('beqz','t0','return');a(NOP)
 a(addiu('t1','t1',6),sw('t1',0x1c,'t0'),sw('t3',0x24,'t0'))
 a.label('return');a(j(0x12E120),NOP);raw=a.assemble()
 if BASE+len(raw)>TEXT:raise ValueError('Status helper reservation overflow')
 return raw

def patch(data):
 if digest(data)!=BASE_SHA:raise ValueError('Complete0.2.23 baseline changed')
 e=Elf(data);src=Elf(PATH.read_bytes());out=bytearray(data);d=language();payload=bytearray();addresses={};changes={};expected={}
 if e.at(BASE,END-BASE)!=bytes(END-BASE):raise ValueError('Unused ending pool reservation occupied')
 def word(at,old,new):
  if int.from_bytes(e.at(at,4),'little')!=old:raise ValueError('Native instruction guard changed at'+hex(at))
  expected[hex(at)]=hex(old);changes[hex(at)]=hex(new);struct.pack_into('<I',out,e.offset(at),new)
 for r in d['rows']:
  raw=src.at(r['va'],r['source_size'])
  if digest(raw)!=r['source_sha256']or e.at(r['va'],len(raw))!=raw:raise ValueError('Original card string changed')
  addresses[r['va']]=TEXT+len(payload);payload.extend(r['en'].encode('cp932')+b'\0')
 if TEXT+len(payload)>END:raise ValueError('Full warning strings exceed reserved pool')
 for va,hi,lo in REFS:
  oldhi=int.from_bytes(e.at(hi,4),'little');oldlo=int.from_bytes(e.at(lo,4),'little');new=addresses[va]
  if oldhi!=0x3C050022 or oldlo!=0x24A50000|(va&65535):raise ValueError('Unexpected warning address load')
  word(hi,oldhi,0x3C050000|((new+0x8000)>>16));word(lo,oldlo,0x24A50000|(new&65535))
 # Keep the full140px text backing allocation. Restore original initial box
 # and portrait position; the scoped text submissions select actual height.
 word(0x9A61F0,addiu('v0','zero',280),addiu('v0','zero',336))
 word(0x9A636C,addiu('t1','zero',152),addiu('t1','zero',96))
 for at in DRAWS:
  old=int.from_bytes(e.at(at,4),'little')
  if old not in(j(0x12E120),jal(0x12E120)):raise ValueError('Status submission tail changed')
  word(at,old,(jal if old>>26==3 else j)(BASE))
 body=code();out[e.offset(BASE):e.offset(BASE)+len(body)]=body;out[e.offset(TEXT):e.offset(TEXT)+len(payload)]=payload
 return bytes(out),dict(language_sha256=digest(LANGUAGE.read_bytes()),translated_card_rows=3,addresses={hex(k):hex(v)for k,v in addresses.items()},payload_va=hex(TEXT),payload_size=len(payload),payload_sha256=digest(payload),code_va=hex(BASE),code_size=len(body),code_sha256=digest(body),patched_words=changes,expected_words=expected,normal_box=dict(y=336,frame_height=96,text_height=84),long_details_box=dict(y=280,frame_height=152,text_height=140),policy='Original geometry for1..3 lines; extra height only for4..5 complete detail lines; bottom432 unchanged; portrait follows native context each frame; original generic dialogue factories untouched.')

def inputs():
 data,packs,overlays,report=prior.inputs();data,fix=patch(data)
 effects=dict(report['battle_effects'],status_panel=dict(normal=fix['normal_box'],long_details=fix['long_details_box'],font=[26,26],bottom=432),status_layout_policy=fix['policy'])
 e=Elf(data);effects['code_sha256']=digest(e.at(int(effects['code_va'],16),effects['code_size']));effects['clones']=[dict(c,sha256=digest(e.at(int(c['va'],16),c['size'])))for c in effects['clones']]
 return data,packs,overlays,dict(report,battle_effects=effects,card_dialog=fix)

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--export',action='store_true');ap.add_argument('--write',action='store_true');a=ap.parse_args()
 if a.export:
  d=export();print(json.dumps(d,indent=1))
  if a.write:
   if LANGUAGE.exists():raise FileExistsError(LANGUAGE)
   LANGUAGE.write_text(json.dumps(d,indent=1)+'\n','utf8')
  else:print('DRY no English export written.')
  return
 data,packs,overlays,report=inputs();print(json.dumps(report['card_dialog'],indent=1),flush=True)
 if not a.write:print('DRY no game files or ISO written.');return
 dest=ROOT/'work/output/v0.2.24';dest.mkdir(exist_ok=False);(dest/'SLPS_250.70').write_bytes(data)
 for i,b in packs.items():(dest/f'{i:05d}.pack').write_bytes(b)
 for i,b in overlays.items():(dest/f'{i:05d}.evemap').write_bytes(b)
 image=dest/'Sunrise Eiyuutan 2 EN v0.2.24.iso';make_iso(image,data,packs,overlays)
 previous=ROOT/'work/output/v0.2.23/Sunrise Eiyuutan 2 EN v0.2.23.iso';old=next(r for r in records(previous)if r['path']=='/MOVIE.AFS');new=next(r for r in records(image)if r['path']=='/MOVIE.AFS');h=hashlib.sha256()
 if old['size']!=new['size']:raise ValueError('Movie archive extent changed')
 with previous.open('rb')as f,image.open('r+b')as g:
  f.seek(old['lba']*2048);g.seek(new['lba']*2048);left=old['size']
  while left:
   block=f.read(min(left,4*1024*1024))
   if not block:raise ValueError('Truncated prior movie archive')
   g.write(block);h.update(block);left-=len(block)
 info=json.loads((ROOT/'work/output/v0.2.23/build_info.json').read_text('utf8'));info.update(version='0.2.24',based_on='0.2.23',**report,elf_sha256=digest(data),iso_path=str(image),iso_size=image.stat().st_size,movie_archive_retained=dict(based_on='0.2.23',size=new['size'],sha256=h.hexdigest()),scope='Translate missing no-save/corrupt card warning labels; restore original normal help/status box, expanding only longer details; retain complete0.2.23.',in_game_validation='pending native card/help/detail views')
 for key in('iso_sha256','native_validation_report'):info.pop(key,None)
 (dest/'build_info.json').write_text(json.dumps(info,indent=1)+'\n','utf8');print('WRITE',image)

if __name__=='__main__':main()
