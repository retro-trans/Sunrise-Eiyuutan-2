"""Run the bounded muted card/help preview and restore exact private settings."""
import argparse,json,sys,time,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from elf import ROOT,Elf
from pine import Pine
import emu,control,card_dialog_preview as preview
import card_dialog_patch as b

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--run',action='store_true');a=ap.parse_args();folder=preview.DEST;e=Elf((folder/'SLPS_250.70').read_bytes());manifest=json.loads((folder/'manifest.json').read_text('utf8'));ini=ROOT/'work/emulator/pcsx2/inis/PCSX2.ini';before=ini.read_bytes()
 if emu.pids():raise ValueError('Private emulator already running')
 for setting in(b'OutputMuted = true',b'StandardVolume = 0',b'Slot1_Enable = false',b'Slot2_Enable = false'):
  if setting not in before:raise ValueError('Muted/card-disabled private settings required')
 print('PLAN final0.2.24 ISO + separate cold ELF; normal input/read/capture only, five native panels,120s bound; exact settings restored.',flush=True)
 if not a.run:print('DRY no mutation.');return
 if(folder/'native_validation.json').exists():raise FileExistsError('Preserve earlier run')
 (folder/'settings_before.ini').write_bytes(before);report=dict(**manifest,complete=False,panels=[],settings_before_sha256=hashlib.sha256(before).hexdigest());p=None
 try:
  report['pid']=emu.start(ROOT/'work/output/v0.2.24/Sunrise Eiyuutan 2 EN v0.2.24.iso',elf=folder/'SLPS_250.70').pid;deadline=time.monotonic()+30
  while time.monotonic()<deadline:
   try:
    p=Pine(timeout=1);control.check(p)
    if p.read(preview.BASE,64)==e.at(preview.BASE,64)and p.read(b.BASE,64)==e.at(b.BASE,64)and p.read32(control.BASE+8)>5:break
   except(OSError,RuntimeError):pass
   if p:p.close();p=None
   time.sleep(.2)
  if p is None:raise TimeoutError('Cold boot monitor unavailable')
  deadline=time.monotonic()+70;stages=[]
  while time.monotonic()<deadline and not p.read32(preview.MAIL):
   stage=p.read32(0x23955c)
   if not stages or stage!=stages[-1]:stages.append(stage);print('Native map',stage,flush=True)
   for button in(('CIRCLE',)if stage==1 else('TRIANGLE','START','CIRCLE')):
    if p.read32(preview.MAIL):break
    control.press(p,button,hold=30 if button=='TRIANGLE' else 12);time.sleep(.3)
  report['native_maps']=stages
  if not p.read32(preview.MAIL):raise TimeoutError('New Game preview hook not reached')
  for phase,label in((1,'no_save'),(2,'corrupt_save'),(3,'repair_stock_box'),(4,'long_detail'),(5,'repair_restored_after_detail')):
   deadline=time.monotonic()+15
   while time.monotonic()<deadline and p.read32(preview.MAIL)!=phase:time.sleep(.05)
   if p.read32(preview.MAIL)!=phase:raise TimeoutError('Preview phase missing'+str(phase))
   time.sleep(.7);row=dict(phase=phase,label=label,screen=str(control.shot(p,'v0224_'+label)))
   if phase>=3:
    ctx=p.read32(preview.MAIL+4);frame=p.read32(ctx+4+0x18);text_context=p.read32(ctx+8);text_win=p.read32(text_context);row.update(native_text=p.read(ctx+0x3c,256).split(b'\0')[0].decode('cp932'),box_y=p.read32(ctx+0x34),frame_height=p.read32(frame+0x24),text_y=p.read32(text_win+0x1c),text_height=p.read32(text_win+0x24));expected=(280,152,286,140)if phase==4 else(336,96,342,84)
    if tuple(row[k]for k in('box_y','frame_height','text_y','text_height'))!=expected:raise ValueError('Native geometry differs'+str(row))
   report['panels'].append(row);print('Captured',label,flush=True);control.press(p,'CIRCLE',hold=8)
  deadline=time.monotonic()+10
  while time.monotonic()<deadline and p.read32(preview.MAIL)!=6:time.sleep(.05)
  report['complete']=p.read32(preview.MAIL)==6
 except Exception as exc:
  report['stop_reason']=type(exc).__name__+': '+str(exc)
  if p:
   try:report['stopped_screen']=str(control.shot(p,'v0224_preview_stop'))
   except Exception:pass
 finally:
  if p:p.close()
  emu.stop();ini.write_bytes(before);report['settings_restored_exactly']=ini.read_bytes()==before;(folder/'native_validation.json').write_text(json.dumps(report,indent=1)+'\n','utf8');print(json.dumps(report,indent=1),flush=True)
 if not report['complete']:raise SystemExit(2)

if __name__=='__main__':main()
