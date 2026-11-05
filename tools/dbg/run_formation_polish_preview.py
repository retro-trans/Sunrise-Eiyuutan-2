"""Observe six cold native panels using controller input only."""
import argparse,json,time,hashlib,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from elf import ROOT,Elf
from pine import Pine
import emu,control,formation_polish_preview as preview

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--run',action='store_true');ap.add_argument('--attempt',type=int,default=1);args=ap.parse_args();folder=preview.DEST if args.attempt==1 else preview.DEST/f'attempt-{args.attempt}';manifest=json.loads((folder/'manifest.json').read_text('utf8'));e=Elf((folder/'SLPS_250.70').read_bytes());ini=ROOT/'work/emulator/pcsx2/inis/PCSX2.ini';before=ini.read_bytes()
 if emu.pids():raise ValueError('Private emulator already running')
 for key in(b'OutputMuted = true',b'StandardVolume = 0',b'Slot1_Enable = false',b'Slot2_Enable = false'):
  if key not in before:raise ValueError('Muted/card-disabled settings required')
 print('PLAN 0.2.30 ISO with separate cold formation ELF; six native panels; no live code/text writes; restore exact settings.',flush=True)
 if not args.run:print('DRY no mutation.');return
 if(folder/'native_validation.json').exists():raise FileExistsError('Preserve evidence')
 (folder/'settings_before.ini').write_bytes(before);r=dict(**manifest,complete=False,screens=[],settings_before_sha256=hashlib.sha256(before).hexdigest());p=None
 try:
  emu.start(ROOT/'work/output/v0.2.30/Sunrise Eiyuutan 2 EN v0.2.30.iso',elf=folder/'SLPS_250.70');deadline=time.monotonic()+30
  while time.monotonic()<deadline:
   try:
    p=Pine(timeout=1);control.check(p)
    if p.read(preview.BASE,64)==e.at(preview.BASE,64)and p.read32(control.BASE+8)>5:break
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
  if not p.read32(preview.MAIL):raise TimeoutError('Formation fixture not reached')
  for phase in range(1,7):
   deadline=time.monotonic()+12
   while time.monotonic()<deadline and p.read32(preview.MAIL)!=phase:time.sleep(.05)
   if p.read32(preview.MAIL)!=phase:raise TimeoutError('Formation phase missing '+str(phase))
   time.sleep(.8);item=dict(phase=phase,label=manifest['cases'][phase-1],screen=str(control.shot(p,'v0230_formation_'+str(phase))))
   if phase in(4,5):
    gt=p.read32(0x23f570-0x690c);parser=p.read32(gt+4);win=p.read32(parser);item.update(raw_equipment=p.read(gt+0x3c,256).split(b'\0')[0].decode('cp932'),parser_fields=p.read(parser,0x44).hex(),window_fields=p.read(win,0x30).hex())
   r['screens'].append(item);print('Captured formation panel',phase,flush=True);control.press(p,'CROSS'if phase>=3 else'CIRCLE',hold=8)
  deadline=time.monotonic()+10
  while time.monotonic()<deadline and p.read32(preview.MAIL)!=7:time.sleep(.05)
  r['complete']=p.read32(preview.MAIL)==7
 except Exception as exc:
  r['stop_reason']=type(exc).__name__+': '+str(exc)
  if p:
   try:r['stopped_screen']=str(control.shot(p,'v0230_preview_stop'))
   except Exception:pass
 finally:
  if p:p.close()
  emu.stop();ini.write_bytes(before);r['settings_restored_exactly']=ini.read_bytes()==before;(folder/'native_validation.json').write_text(json.dumps(r,indent=1)+'\n','utf8');print('Native formation complete',r['complete'],flush=True)
 if not r['complete']:raise SystemExit(2)
if __name__=='__main__':main()
