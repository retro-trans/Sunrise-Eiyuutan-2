"""Observe native special-name panels, input only, restore private settings."""
import argparse,json,time,hashlib,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from elf import ROOT,Elf
from pine import Pine
import emu,control,special_names_preview as preview

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--run',action='store_true');a=ap.parse_args();folder=preview.DEST;manifest=json.loads((folder/'manifest.json').read_text('utf8'));e=Elf((folder/'SLPS_250.70').read_bytes());ini=ROOT/'work/emulator/pcsx2/inis/PCSX2.ini';before=ini.read_bytes()
 if emu.pids():raise ValueError('Private emulator already running')
 for key in(b'OutputMuted = true',b'StandardVolume = 0',b'Slot1_Enable = false',b'Slot2_Enable = false'):
  if key not in before:raise ValueError('Muted/card-disabled settings required')
 print('PLAN final0.2.26 ISO plus separate cold selector ELF; six native panels, both sides,150s bound, no live code/text writes; restore exact settings.',flush=True)
 if not a.run:print('DRY no mutation.');return
 if(folder/'native_validation.json').exists():raise FileExistsError('Preserve previous evidence')
 (folder/'settings_before.ini').write_bytes(before);r=dict(**manifest,complete=False,screens=[],settings_before_sha256=hashlib.sha256(before).hexdigest());p=None
 try:
  emu.start(ROOT/'work/output/v0.2.26/Sunrise Eiyuutan 2 EN v0.2.26.iso',elf=folder/'SLPS_250.70');deadline=time.monotonic()+30
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
  if not p.read32(preview.MAIL):raise TimeoutError('Selector preview not reached')
  fields=json.loads((ROOT/'work/output/v0.2.26/build_info.json').read_text('utf8'))['special_names']['fields']
  for phase,(row,flag)in enumerate(preview.CASES,1):
   deadline=time.monotonic()+10
   while time.monotonic()<deadline and p.read32(preview.MAIL)!=phase:time.sleep(.05)
   if p.read32(preview.MAIL)!=phase:raise TimeoutError('Selector phase missing')
   time.sleep(.6);f=next(f for f in fields if f['row']==row and f['field']==12);expected=f['en'].encode('ascii')+b'\0'
   if p.read(f['pointer'],len(expected))!=expected:raise ValueError('Runtime name differs from final delivery')
   r['screens'].append(dict(phase=phase,row=row,flag=flag,en=f['en'],width=f['width'],screen=str(control.shot(p,'v0226_special_'+str(phase)))));print('Captured',phase,f['en'],flush=True);control.press(p,'CIRCLE',hold=8)
  deadline=time.monotonic()+10
  while time.monotonic()<deadline and p.read32(preview.MAIL)!=len(preview.CASES)+1:time.sleep(.05)
  r['complete']=p.read32(preview.MAIL)==len(preview.CASES)+1;r['native_selection_results']=[p.read32(preview.MAIL+16+i*4)for i in range(len(preview.CASES))]
 except Exception as exc:
  r['stop_reason']=type(exc).__name__+': '+str(exc)
  if p:
   try:r['stopped_screen']=str(control.shot(p,'v0226_preview_stop'))
   except Exception:pass
 finally:
  if p:p.close()
  emu.stop();ini.write_bytes(before);r['settings_restored_exactly']=ini.read_bytes()==before;(folder/'native_validation.json').write_text(json.dumps(r,indent=1)+'\n','utf8');print('Native selector complete',r['complete'],flush=True)
 if not r['complete']:raise SystemExit(2)
if __name__=='__main__':main()
