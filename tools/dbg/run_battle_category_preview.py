"""Observe complete native battle pages and advance only after prompt readiness."""
import argparse,json,sys,time,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from elf import ROOT,Elf
from pine import Pine
import control,emu,battle_category_preview as preview
from walk_messages import current
from message_state import CONTEXT,SPEAK_WINDOW
from textcodec import decode,parse_table
from message_pages import pages
from extract import pack_members

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--run',action='store_true');a=ap.parse_args();folder=preview.DEST;e=Elf((folder/'SLPS_250.70').read_bytes());manifest=json.loads((folder/'manifest.json').read_text('utf8'));base=ROOT/'work/output/v0.2.25';info=json.loads((base/'build_info.json').read_text('utf8'));ini=ROOT/'work/emulator/pcsx2/inis/PCSX2.ini';before=ini.read_bytes()
 if emu.pids():raise ValueError('Private emulator already running')
 for setting in(b'OutputMuted = true',b'StandardVolume = 0',b'Slot1_Enable = false',b'Slot2_Enable = false'):
  if setting not in before:raise ValueError('Muted/card-disabled settings required')
 print('PLAN final0.2.25 ISO + separate cold ELF; read/input/capture only; six complete barks at each physical destination; no SP fixture in the current profile, restore exact settings.',flush=True)
 if not a.run:print('DRY no mutation.');return
 if(folder/'native_validation.json').exists():raise FileExistsError('Preserve previous native run')
 expected={}
 for profile,name in((1,'00022_10512'),(2,'04971_11849')):
  pn,mid=map(int,name.split('_'));pack=(base/f'{pn:05d}.pack').read_bytes();m=next(m for m in pack_members(pack)if m['id']==mid);rows=parse_table(pack[m['offset']:m['offset']+m['size']]);expected[profile]={i:next(p for p in pages(rows[i])if p['flags']&1)for i in preview.IDS}
 report=dict(**manifest,complete=False,screens=[],settings_before_sha256=hashlib.sha256(before).hexdigest());(folder/'settings_before.ini').write_bytes(before);p=None;seen=set();started=time.monotonic()
 try:
  report['pid']=emu.start(base/'Sunrise Eiyuutan 2 EN v0.2.25.iso',elf=folder/'SLPS_250.70').pid;deadline=time.monotonic()+30
  while time.monotonic()<deadline:
   try:
    p=Pine(timeout=1);control.check(p)
    if p.read(preview.BASE,64)==e.at(preview.BASE,64)and p.read32(control.BASE+8)>5:break
   except(OSError,RuntimeError):pass
   if p:p.close();p=None
   time.sleep(.2)
  if p is None:raise TimeoutError('Cold boot monitor unavailable')
  deadline=time.monotonic()+360;attempt=0
  while time.monotonic()<deadline and p.read32(preview.MAIL)==4:
   stage=p.read32(0x23955c)
   buttons=('CIRCLE',)if stage==1 else('TRIANGLE','START','CIRCLE')
   for button in buttons:
    if p.read32(preview.MAIL)!=4:break
    control.press(p,button,hold=30 if button=='TRIANGLE'else 12);time.sleep(.3)
   attempt+=1
  report['source_request']=[p.read32(preview.MAIL+i)for i in(20,24,28)]
  if p.read32(preview.MAIL)!=2:raise TimeoutError('Ordinary story message bridge not reached')
  deadline=time.monotonic()+160;stable=None;since=0
  while time.monotonic()<deadline:
   phase=p.read32(preview.MAIL);profile=p.read32(preview.MAIL+4);row=p.read32(preview.MAIL+8)
   if phase==3:break
   key=current(p,info['font_widths'],require_prompt=True)
   target=(profile,row)
   if phase==2 and key is not None and target not in seen:
    if key!=stable:stable=key;since=time.monotonic()
    elif time.monotonic()-since>.25:
     r=expected[profile][row];raw=p.read(CONTEXT,440);body=raw[40:].split(b'\0')[0];speaker=p.read32(CONTEXT+4);voice=p.read32(CONTEXT+8)
     if body!=r['body']or speaker!=r['speaker']or voice!=r['voice']:raise ValueError('Native page does not match exact selected built row')
     path=control.shot(p,f'v0225_bank{profile}_row{row}');report['screens'].append(dict(label='battle',profile=profile,row=row,speaker=speaker,voice=voice,body=decode(body),path=str(path)));seen.add(target);print('Captured bank',profile,'row',row,flush=True);control.press(p,'CIRCLE',hold=8);stable=None
   else:stable=None
   time.sleep(.05)
  report['complete']=p.read32(preview.MAIL)==3 and len(seen)==len(preview.IDS)*2
  if not report['complete']:raise TimeoutError('Selected battle pages did not complete')
 except Exception as exc:
  report['stop_reason']=type(exc).__name__+': '+str(exc)
  if p:
   try:report['stopped_screen']=str(control.shot(p,'v0225_preview_stop'));report['mail_hex']=p.read(preview.MAIL,32).hex();report['context_hex']=p.read(CONTEXT,64).hex()
   except Exception:pass
 finally:
  if p:p.close()
  emu.stop();ini.write_bytes(before);report['settings_restored_exactly']=ini.read_bytes()==before;report['elapsed']=time.monotonic()-started;(folder/'native_validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=1)+'\n','utf8');print('Native complete',report['complete'],'report',folder/'native_validation.json',flush=True)
 if not report['complete']:raise SystemExit(2)

if __name__=='__main__':main()
