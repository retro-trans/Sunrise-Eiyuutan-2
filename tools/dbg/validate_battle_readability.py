"""Bounded fresh boot of the final image; no code/data writes or state loads.

Reads all changed words and font metrics from the loaded program, optionally
advances boot/title with controller input, then restores exact private settings.
This does not claim that the reported battle windows were reached in gameplay.
"""
import argparse,hashlib,json,time,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from elf import ROOT,Elf
from pine import Pine
import control,emu

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--run',action='store_true');a=ap.parse_args()
 folder=ROOT/'work/output/v0.2.21';info=json.loads((folder/'build_info.json').read_text('utf8'));elf=Elf((folder/'SLPS_250.70').read_bytes())
 image=folder/'Sunrise Eiyuutan 2 EN v0.2.21.iso';ini=ROOT/'work/emulator/pcsx2/inis/PCSX2.ini';before=ini.read_bytes()
 if emu.pids():raise ValueError('Project emulator already running')
 for setting in (b'OutputMuted = true',b'StandardVolume = 0',b'Slot1_Enable = false',b'Slot2_Enable = false'):
  if setting not in before:raise ValueError('Expected muted, card-disabled private configuration')
 print('Fresh final ISO; verify32 changed words and128 font bytes; bounded title input/capture; restore exact settings. No state load, override or live code/text writes.',flush=True)
 if not a.run:print('DRY RUN: no mutation.');return
 backup=folder/'native_settings_before.ini'
 if backup.exists():raise FileExistsError(backup)
 backup.write_bytes(before);report=dict(build='0.2.21',boot='fresh final ISO; no override or state load',battle_panels_replayed=False,settings_before_sha256=hashlib.sha256(before).hexdigest());p=None
 try:
  report['pid']=emu.start(image).pid;deadline=time.monotonic()+30
  while time.monotonic()<deadline:
   try:
    p=Pine(timeout=1);control.check(p)
    if p.read32(control.BASE+8)>5:break
   except (OSError,RuntimeError):pass
   if p:p.close();p=None
   time.sleep(.2)
  if p is None:raise TimeoutError('Final boot monitor unavailable')
  for site in info['battle_readability']['patched_words']:
   va=int(site,16)
   if p.read(va,4)!=elf.at(va,4):raise ValueError('Loaded final instruction differs at'+site)
  if p.read(0x9a4000,128)!=elf.at(0x9a4000,128):raise ValueError('Loaded font metrics differ')
  report.update(loaded_changed_words=32,font_metric_bytes=128,live_code_verified=True)
  deadline=time.monotonic()+40;stages=[]
  while time.monotonic()<deadline:
   stage=p.read32(0x23955c)
   if not stages or stages[-1]!=stage:stages.append(stage)
   if stage==1:break
   for button in ('TRIANGLE','START','CIRCLE'):
    control.press(p,button,hold=30 if button=='TRIANGLE' else 12)
    if p.read32(0x23955c)==1:break
   time.sleep(.2)
  report.update(native_map_stages=stages,screen=str(control.shot(p,'v0221_final_boot')))
 except Exception as exc:report['stop_reason']=type(exc).__name__+': '+str(exc)
 finally:
  if p:p.close()
  emu.stop();ini.write_bytes(before)
  report['settings_restored_exactly']=ini.read_bytes()==before
  report['settings_after_sha256']=hashlib.sha256(ini.read_bytes()).hexdigest()
  (folder/'native_validation.json').write_text(json.dumps(report,indent=1)+'\n','utf8');print(json.dumps(report,indent=1),flush=True)
 if not report.get('live_code_verified'):raise SystemExit(2)

if __name__=='__main__':main()
