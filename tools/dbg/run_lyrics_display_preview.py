"""Bounded muted cold playback, restoring exact private emulator settings."""
import argparse,json,sys,time,struct,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from elf import ROOT,Elf
from pine import Pine
import emu,control,lyrics_display_preview as preview
import movie_lyrics_native as n

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--run',action='store_true');a=ap.parse_args();folder=preview.DEST;e=Elf((folder/'SLPS_250.70').read_bytes());manifest=json.loads((folder/'manifest.json').read_text('utf8'));ini=ROOT/'work/emulator/pcsx2/inis/PCSX2.ini';before=ini.read_bytes()
 if emu.pids():raise ValueError('Private emulator already running')
 for setting in(b'OutputMuted = true',b'StandardVolume = 0',b'Slot1_Enable = false',b'Slot2_Enable = false'):
  if setting not in before:raise ValueError('Muted and card-disabled private settings required')
 print('PLAN muted final ISO + separate cold probe ELF; no live patches/state loads; capture OP cues and ED cue/gap/reuse/cleanup;260s bound; restore exact settings.',flush=True)
 if not a.run:print('DRY no changes.');return
 if(folder/'native_validation.json').exists():raise FileExistsError('Preserve previous run')
 (folder/'settings_before.ini').write_bytes(before);report=dict(**manifest,complete=False,events=[],screens=[],settings_before_sha256=hashlib.sha256(before).hexdigest());p=None;seen=set();started=time.monotonic();last_stage=-1;last_progress=started;attempt=0
 try:
  report['pid']=emu.start(ROOT/'work/output/v0.2.23/Sunrise Eiyuutan 2 EN v0.2.23.iso',elf=folder/'SLPS_250.70').pid
  while time.monotonic()-started<260:
   if p is None:
    try:p=Pine(timeout=1);control.check(p)
    except(OSError,RuntimeError):
     if p:p.close();p=None
     time.sleep(.3);continue
    if p.read(preview.BASE,64)!=e.at(preview.BASE,64)or p.read(n.BASE,64)!=e.at(n.BASE,64):raise ValueError('Loaded production/helper revision mismatch')
   now=time.monotonic();stage=p.read32(preview.MAIL);wins=struct.unpack('<III',p.read(n.STATE,12));total=p.read32(0x1C987C);fields=p.read32(0x1C9880)
   if stage!=last_stage:
    report['events'].append(dict(seconds=now-started,stage=stage,fields=fields,total=total,windows=wins));last_stage=stage;print('Native stage',stage,'fields',fields,'ending cue',wins[2],flush=True)
   if stage==0 and attempt<8 and now-started>6+attempt*6:
    control.press(p,'CIRCLE',hold=12);attempt+=1
   label=None
   if stage==1 and total==5504 and fields<total:
    for frame in(720,1200,2400,2700):
     key='opening_'+str(frame)
     if fields//2>=frame and key not in seen:label=key;break
   if stage==2:
    if wins[2]in(1,3,5,8):
     key='ending_cue_'+str(wins[2])
     if key not in seen:label=key
    if wins[2]==0 and 'ending_cue_3'in seen and 'ending_gap'not in seen:label='ending_gap'
   if stage==3:
    if wins!=(0,0,0):raise ValueError('Ending windows not cleaned after stop')
    label='ending_cleanup'
   if label:
    seen.add(label);path=control.shot(p,'v0223_'+label);row=dict(label=label,seconds=now-started,stage=stage,frame=fields//2,windows=wins,path=str(path));report['screens'].append(row);print('Captured',label,flush=True)
   if stage==3:
    required={'opening_720','opening_1200','opening_2400','opening_2700','ending_cue_1','ending_cue_3','ending_cue_5','ending_gap','ending_cue_8','ending_cleanup'};report['missing']=sorted(required-seen);report['complete']=not report['missing'];break
   if now-last_progress>20:print('Playback progress',stage,fields,'cue',wins[2],flush=True);last_progress=now
   time.sleep(.15)
  if last_stage!=3:report['stop_reason']='Bounded playback did not finish'
 except Exception as exc:
  report['stop_reason']=type(exc).__name__+': '+str(exc)
 finally:
  if p:p.close()
  emu.stop();ini.write_bytes(before);report['settings_restored_exactly']=ini.read_bytes()==before;report['elapsed']=time.monotonic()-started;(folder/'native_validation.json').write_text(json.dumps(report,indent=1)+'\n','utf8');print('Playback complete',report['complete'],'report',folder/'native_validation.json',flush=True)
 if not report['complete']:raise SystemExit(2)

if __name__=='__main__':main()
