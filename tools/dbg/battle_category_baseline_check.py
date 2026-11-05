"""Bounded previous baseline startup using the established navigation helper."""
import argparse,hashlib,json,sys,time,subprocess
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from elf import ROOT
from pine import Pine
import control,emu
from message_state import CONTEXT,built_table
from message_pages import pages
from textcodec import parse_table
DEST=ROOT/'work/ui/battle-category-0.2.25-baseline-024'
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--run',action='store_true');a=ap.parse_args();ini=ROOT/'work/emulator/pcsx2/inis/PCSX2.ini';before=ini.read_bytes();base=ROOT/'work/output/v0.2.24';r=dict(complete=False,scope='Prior 0.2.24 ISO, no override, state load or live code/text writes; existing story_start helper with 120s bound.')
 print('PLAN previous baseline cold boot; existing startup helper with 120s allowance, first complete opening caption source check, native capture; exact settings restored.',flush=True)
 if not a.run:print('DRY no mutation.');return
 if emu.pids()or DEST.exists():raise ValueError('Fresh isolated run required')
 for key in(b'OutputMuted = true',b'StandardVolume = 0',b'Slot1_Enable = false',b'Slot2_Enable = false'):
  if key not in before:raise ValueError('Muted/card-disabled settings required')
 DEST.mkdir();p=None
 try:
  emu.start(base/'Sunrise Eiyuutan 2 EN v0.2.24.iso');deadline=time.monotonic()+30
  while time.monotonic()<deadline:
   try:
    p=Pine(timeout=1);control.check(p)
    if p.read32(control.BASE+8)>5:break
   except(OSError,RuntimeError):pass
   if p:p.close();p=None
   time.sleep(.2)
  if p is None:raise TimeoutError('Cold monitor unavailable')
  p.close();p=None
  result=subprocess.run([sys.executable,'-X','utf8',str(ROOT/'tools/dbg/story_start.py'),'0.2.24','--timeout','120','--run'],cwd=ROOT,capture_output=True,text=True,encoding='utf8');r.update(helper_exit=result.returncode,helper_output=result.stdout);print(result.stdout,flush=True)
  if result.returncode:
   p=Pine();r['map']=p.read32(0x23955c);r['scene']=p.read32(0x239564);r['context_hex']=p.read(CONTEXT,440).hex();raise ValueError('Established startup helper did not pass')
  p=Pine();raw=p.read(CONTEXT,440);expected=next(x for x in pages(parse_table(built_table(base,'04905_10383'))[0])if x['flags']&1)
  if raw[40:].split(b'\0')[0]!=expected['body']:raise ValueError('First native caption differs from final table')
  r.update(screen=str(control.shot(p,'v0225_normal_startup')),context_hex=raw.hex(),complete=True)
 except Exception as exc:
  r['stop_reason']=type(exc).__name__+': '+str(exc)
  if p:
   try:r['stopped_screen']=str(control.shot(p,'v0225_startup_stop'))
   except Exception:pass
 finally:
  if p:p.close()
  emu.stop();ini.write_bytes(before);r['settings_restored_exactly']=ini.read_bytes()==before;r['settings_sha256']=hashlib.sha256(ini.read_bytes()).hexdigest();(DEST/'native_validation.json').write_text(json.dumps(r,indent=1)+'\n','utf8');print('Startup complete',r['complete'],flush=True)
 if not r['complete']:raise SystemExit(2)
if __name__=='__main__':main()
