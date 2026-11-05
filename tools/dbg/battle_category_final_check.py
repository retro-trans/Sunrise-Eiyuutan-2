"""Cold native macron fixture plus separate unmodified delivery startup."""
import argparse,hashlib,json,sys,time,subprocess
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from elf import ROOT,Elf
from pine import Pine
import control,emu
from walk_messages import current
from message_state import CONTEXT
from textcodec import encode
import battle_category_patch as b
DEST=ROOT/'work/ui/battle-category-0.2.25-final'
BASE=0x9b7b00;MAIL=0x9b7fc0

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');ap.add_argument('--run',action='store_true');a=ap.parse_args()
 base=ROOT/'work/output/v0.2.25';info=json.loads((base/'build_info.json').read_text('utf8'));data=bytearray((ROOT/'work/ui/battle-category-0.2.25-r2/SLPS_250.70').read_bytes());e=Elf(data)
 off=e.offset(0x9a1708);data[off:off+8]=bytes.fromhex('50b2040800000000')
 at=int(info['battle_category']['ui']['addresses']['0x232020'],16);off=e.offset(at);old=encode('Please set SP.')+b'\0';new=encode('Bakuryū Cannon')+b'\0'
 if len(old)!=len(new)or data[off:off+len(old)]!=old:raise ValueError('Fixture prompt guard')
 data[off:off+len(new)]=new
 print('PLAN separate muted SP glyph fixture, then fresh delivery ISO/ELF startup; no live code/text writes. Capture complete first original story caption. Restore exact private settings.',flush=True)
 if not(a.write or a.run):print('DRY no mutation.');return
 if a.write:
  DEST.mkdir(exist_ok=False);(DEST/'SLPS_250.70').write_bytes(data);return
 if (DEST/'native_validation.json').exists()or(DEST/'SLPS_250.70').read_bytes()!=data or emu.pids():raise ValueError('Fresh isolated run required')
 ini=ROOT/'work/emulator/pcsx2/inis/PCSX2.ini';before=ini.read_bytes();r=dict(complete=False,delivery_elf_sha256=info['elf_sha256'],fixture_elf_sha256=b.digest(data),screens=[],scope='Synthetic SP display tests the native supplemental glyph. Separate final delivery boot reaches the complete first original opening-story caption. New battle barks are verified offline only; attempted forced bark previews did not complete.')
 for key in(b'OutputMuted = true',b'StandardVolume = 0',b'Slot1_Enable = false',b'Slot2_Enable = false'):
  if key not in before:raise ValueError('Muted/card-disabled settings required')
 p=None
 try:
  for fixture in(True,False):
   emu.start(base/'Sunrise Eiyuutan 2 EN v0.2.25.iso',elf=DEST/'SLPS_250.70'if fixture else None);deadline=time.monotonic()+30
   while time.monotonic()<deadline:
    try:
     p=Pine(timeout=1);control.check(p)
     if p.read32(control.BASE+8)>5:break
    except(OSError,RuntimeError):pass
    if p:p.close();p=None
    time.sleep(.2)
   if p is None:raise TimeoutError('Cold monitor unavailable')
   deadline=time.monotonic()+100;last=None;since=0
   while time.monotonic()<deadline:
    if fixture and p.read32(MAIL)==1:
     time.sleep(.8);r['screens'].append(dict(label='glyph',path=str(control.shot(p,'v0225_macron_fixture'))));r['glyph_native']=True;break
    if not fixture:
     key=current(p,info['font_widths'])
     if key is not None:
      if key!=last:last=key;since=time.monotonic()
      elif time.monotonic()-since>.3:
       r['screens'].append(dict(label='delivery_startup',path=str(control.shot(p,'v0225_delivery_startup'))));r['startup_context_hex']=p.read(CONTEXT,440).hex();r['delivery_startup']=True;break
      time.sleep(.05);continue
    stage=p.read32(0x23955c)
    for button in(('CIRCLE',)if stage==1 else('TRIANGLE','START','CIRCLE')):
     if fixture and p.read32(MAIL)==1:break
     if not fixture and p.read32(0x2395ac):break
     control.press(p,button,hold=30 if button=='TRIANGLE'else 12);time.sleep(.3)
   else:raise TimeoutError('Native fixture/startup not reached')
   p.close();p=None;emu.stop();ini.write_bytes(before)
  r['complete']=r.get('glyph_native',False)and r.get('delivery_startup',False)
 except Exception as exc:
  r['stop_reason']=type(exc).__name__+': '+str(exc)
  if p:
   try:r['stopped_screen']=str(control.shot(p,'v0225_final_stop'))
   except Exception:pass
 finally:
  if p:p.close()
  emu.stop();ini.write_bytes(before);r['settings_restored_exactly']=ini.read_bytes()==before;r['settings_sha256']=hashlib.sha256(ini.read_bytes()).hexdigest();(DEST/'native_validation.json').write_text(json.dumps(r,indent=1)+'\n','utf8');print(json.dumps(r,indent=1),flush=True)
 if not r['complete']:raise SystemExit(2)
if __name__=='__main__':main()
