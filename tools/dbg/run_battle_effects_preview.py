"""Run bounded cold native previews with muted private emulator, no live patches."""
import argparse,hashlib,json,time,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from elf import ROOT,Elf
from pine import Pine
import control,emu
import battle_effects_preview as preview

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--run',action='store_true');a=ap.parse_args()
 folder=preview.DEST;elf=Elf((folder/'SLPS_250.70').read_bytes());info=json.loads((folder/'build_info.json').read_text('utf8'))
 ini=ROOT/'work/emulator/pcsx2/inis/PCSX2.ini';before=ini.read_bytes()
 if emu.pids():raise ValueError('Private project emulator already running')
 for setting in(b'OutputMuted = true',b'StandardVolume = 0',b'Slot1_Enable = false',b'Slot2_Enable = false'):
  if setting not in before:raise ValueError('Private muted/card-disabled settings required')
 print('Fresh final ISO plus explicitly separate cold preview ELF; input/read/capture only; three native panels; restore exact settings.',flush=True)
 if not a.run:print('DRY RUN: no mutation.');return
 if(folder/'native_validation.json').exists():raise FileExistsError('Preserve earlier preview run')
 (folder/'settings_before.ini').write_bytes(before);report=dict(scope=info['scope'],override_sha256=info['preview_elf_sha256'],panels=[],settings_before_sha256=hashlib.sha256(before).hexdigest(),complete=False);p=None
 try:
  report['pid']=emu.start(ROOT/'work/output/v0.2.22/Sunrise Eiyuutan 2 EN v0.2.22.iso',elf=folder/'SLPS_250.70').pid
  deadline=time.monotonic()+30
  while time.monotonic()<deadline:
   try:
    p=Pine(timeout=1);control.check(p)
    if p.read(preview.BASE,64)==elf.at(preview.BASE,64)and p.read32(control.BASE+8)>5:break
   except(OSError,RuntimeError):pass
   if p:p.close();p=None
   time.sleep(.2)
  if p is None:raise TimeoutError('Preview boot monitor unavailable')
  stages=[];deadline=time.monotonic()+70
  while time.monotonic()<deadline and not p.read32(preview.MAIL):
   stage=p.read32(0x23955c)
   if not stages or stages[-1]!=stage:stages.append(stage);print('Native map',stage,flush=True)
   for button in(('CIRCLE',)if stage==1 else('TRIANGLE','START','CIRCLE')):
    if p.read32(preview.MAIL):break
    control.press(p,button,hold=30 if button=='TRIANGLE' else 12);time.sleep(.3)
  report['native_map_stages']=stages
  if not p.read32(preview.MAIL):raise TimeoutError('Native new-game preview hook not reached')
  for phase,label in((1,'attack_priority'),(2,'longest_comment'),(3,'rewards')):
   deadline=time.monotonic()+15
   while time.monotonic()<deadline and p.read32(preview.MAIL+4)!=phase:time.sleep(.05)
   if p.read32(preview.MAIL+4)!=phase:raise TimeoutError('Native preview phase not reached'+str(phase))
   time.sleep(.6);row=dict(phase=phase,label=label,screen=str(control.shot(p,'v0222_'+label)))
   if phase<3:
    context=p.read32(preview.MAIL+8)
    if not context:raise ValueError('Native status allocation failed')
    text=p.read(context+0x3c,256).split(b'\0')[0].decode('cp932');row['native_text']=text
    if phase==1 and 'In the attack phase'not in text:raise ValueError('Native status text differs')
    if phase==2 and 'cannot be revived'not in text:raise ValueError('Native longest comment incomplete')
   report['panels'].append(row);print('Captured',label,flush=True);control.press(p,'CIRCLE',hold=8)
  deadline=time.monotonic()+10
  while time.monotonic()<deadline and p.read32(preview.MAIL+4)!=4:time.sleep(.05)
  report['complete']=p.read32(preview.MAIL+4)==4
 except Exception as exc:
  report['stop_reason']=type(exc).__name__+': '+str(exc)
  if p:
   try:
    report['mail_hex']=p.read(preview.MAIL,64).hex();report['stopped_screen']=str(control.shot(p,'v0222_preview_stop'))
   except Exception as capture_error:report['capture_error']=str(capture_error)
 finally:
  if p:p.close()
  emu.stop();ini.write_bytes(before);report['settings_restored_exactly']=ini.read_bytes()==before
  (folder/'native_validation.json').write_text(json.dumps(report,indent=1)+'\n','utf8');print(json.dumps(report,indent=1),flush=True)
 if not report['complete']:raise SystemExit(2)

if __name__=='__main__':main()
