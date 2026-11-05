"""Capture native Save/Load lists, cancel both, restore exact private settings."""
import argparse,json,time,hashlib,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from elf import ROOT,Elf
from pine import Pine
import emu,control,episode_titles_preview as preview
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--run',action='store_true');ap.add_argument('--attempt',type=int,default=1);a=ap.parse_args();folder=preview.DEST;manifest=json.loads((folder/'manifest.json').read_text('utf8'));e=Elf((folder/'SLPS_250.70').read_bytes());ini=ROOT/'work/emulator/pcsx2/inis/PCSX2.ini';before=ini.read_bytes();record=folder/('native_validation.json'if a.attempt==1 else f'native_validation_{a.attempt}.json')
 if emu.pids():raise ValueError('Private emulator already running')
 for key in(b'OutputMuted = true',b'StandardVolume = 0',b'Slot1_Enable = false',b'Slot2_Enable = false'):
  if key not in before:raise ValueError('Muted/card-disabled settings required')
 print('PLAN final 0.2.27 ISO with separate cold debug ELF. Native Save and Load list using six synthetic numeric headers; cancel each; no card writes or live code/text writes; restore exact settings.',flush=True)
 if not a.run:print('DRY no mutation.');return
 if record.exists():raise FileExistsError('Preserve evidence')
 (folder/f'settings_before_{a.attempt}.ini').write_bytes(before);r=dict(**manifest,complete=False,screens=[],attempt=a.attempt,cancel_input='CROSS',settings_before_sha256=hashlib.sha256(before).hexdigest());p=None
 try:
  emu.start(ROOT/'work/output/v0.2.27/Sunrise Eiyuutan 2 EN v0.2.27.iso',elf=folder/'SLPS_250.70');deadline=time.monotonic()+30
  while time.monotonic()<deadline:
   try:
    p=Pine(timeout=1);control.check(p)
    if p.read(preview.BASE,64)==e.at(preview.BASE,64) and p.read32(control.BASE+8)>5:break
   except(OSError,RuntimeError):pass
   if p:p.close();p=None
   time.sleep(.2)
  if p is None:raise TimeoutError('Cold monitor unavailable')
  deadline=time.monotonic()+70
  while time.monotonic()<deadline and not p.read32(preview.MAIL):
   stage=p.read32(0x23955c)
   for button in(('CIRCLE',)if stage==1 else('TRIANGLE','START','CIRCLE')):
    if p.read32(preview.MAIL):break
    control.press(p,button,hold=30 if button=='TRIANGLE'else 12);time.sleep(.3)
  if not p.read32(preview.MAIL):raise TimeoutError('Save-list fixture not reached')
  for phase in(1,2):
   deadline=time.monotonic()+10
   while time.monotonic()<deadline and p.read32(preview.MAIL)!=phase:time.sleep(.05)
   if p.read32(preview.MAIL)!=phase:raise TimeoutError('List phase missing')
   time.sleep(1.2)
   r['screens'].append(dict(phase=phase,mode='save'if phase==1 else'load',screen=str(control.shot(p,'v0227_titles_'+str(phase)))))
   print('Captured native list',phase,flush=True);control.press(p,'CROSS',hold=8)
  deadline=time.monotonic()+10
  while time.monotonic()<deadline and p.read32(preview.MAIL)!=3:time.sleep(.05)
  r['complete']=p.read32(preview.MAIL)==3;r['native_cancel_results']=[p.read32(preview.MAIL+4),p.read32(preview.MAIL+8)]
 except Exception as exc:
  r['stop_reason']=type(exc).__name__+': '+str(exc)
  if p:
   try:r['stopped_screen']=str(control.shot(p,'v0227_preview_stop'))
   except Exception:pass
 finally:
  if p:p.close()
  emu.stop();ini.write_bytes(before);r['settings_restored_exactly']=ini.read_bytes()==before;record.write_text(json.dumps(r,indent=1)+'\n','utf8');print('Native list complete',r['complete'],flush=True)
 if not r['complete']:raise SystemExit(2)
if __name__=='__main__':main()
