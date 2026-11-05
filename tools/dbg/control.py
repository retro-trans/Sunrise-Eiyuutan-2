"""Verified build monitor: status, focus-free input, named state/screenshots.

Never installs a RAM hook into an unpatched game. No live code rewriting or halt.
"""
import argparse
import json
import re
from pathlib import Path
import shutil
import struct
import time
import zipfile
from datetime import datetime,timezone
import pine
from sstate import State

ROOT=Path(__file__).resolve().parents[2]
BASE=0x9A8000
# padMakeGAMEPAD combines raw pad bytes in reverse order to the standard mask.
BUTTONS=dict(L2=1,R2=2,L1=4,R1=8,TRIANGLE=16,CIRCLE=32,CROSS=64,SQUARE=128,
             SELECT=256,L3=512,R3=1024,START=2048,UP=4096,RIGHT=8192,DOWN=16384,LEFT=32768)


def check(p):
    if p.game_id()!='SLPS-25070':raise RuntimeError('Unexpected game serial')
    if p.read32(BASE)!=0x32474253:raise RuntimeError('Monitor absent: boot a project test ISO')


def frames(p,n,timeout=10):
    start=p.read32(BASE+8);end=time.monotonic()+timeout
    while True:
        elapsed=(p.read32(BASE+8)-start)&0xffffffff
        if elapsed>0x7fffffff:raise RuntimeError('Sampling clock reset during state load; wait for rendering and retry')
        if elapsed>=n:return
        if time.monotonic()>end:raise TimeoutError('Frame clock stopped')
        time.sleep(.01)


def press(p,button,hold=8):
    check(p)
    try:
        p.write32(BASE+4,BUTTONS[button]);frames(p,hold)
    finally:p.write32(BASE+4,0)
    frames(p,12)


def capture_directory():
    """Keep logical project paths while permitting a configured spillover junction."""
    base=ROOT/'work/ui/shots'
    config=ROOT/'work/ui/capture-storage.json'
    if not config.exists():return base
    value=json.loads(config.read_text(encoding='utf-8-sig'))
    if not isinstance(value,dict) or set(value)!={'shots_subdirectory'}:
        raise ValueError('Expected only shots_subdirectory in capture-storage.json')
    name=value['shots_subdirectory']
    if not isinstance(name,str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,63}',name):
        raise ValueError('Capture subdirectory must be a simple project-local name')
    dest=base/name
    if not dest.is_dir():raise FileNotFoundError('Configured capture directory must already exist: '+str(dest))
    return dest


def shot(p,label):
    check(p)
    capture_base=capture_directory()
    states=ROOT/'work/emulator/pcsx2/sstates'
    before={f:(f.stat().st_mtime_ns,f.stat().st_size) for f in states.glob('*.09.p2s')}
    p.save_state(9)
    deadline=time.monotonic()+15
    while time.monotonic()<deadline:
        for f in states.glob('SLPS-25070*.09.p2s'):
            if before.get(f)!=(f.stat().st_mtime_ns,f.stat().st_size):
                try:
                    png=State(f).screenshot()
                    run=capture_base/(datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')+'_'+label)
                    run.mkdir(parents=True)
                    shutil.copy2(f,run/(label+'.p2s'));(run/'screen.png').write_bytes(png)
                    return run/'screen.png'
                except (OSError,ValueError,KeyError,zipfile.BadZipFile,EOFError):pass
        time.sleep(.1)
    raise TimeoutError('Savestate screenshot unavailable')


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('action',choices=['status','press','shot','frames']);ap.add_argument('arg',nargs='?');ap.add_argument('--run',action='store_true');args=ap.parse_args()
    if args.action in ('press','shot') and not args.run:
        print('DRY RUN:',args.action,args.arg,'on project PINE 28026; --run performs it');return
    p=pine.Pine()
    try:
        check(p)
        if args.action=='status':print(json.dumps(dict(status=p.status(),serial=p.game_id(),frames=p.read32(BASE+8))))
        elif args.action=='press':press(p,args.arg.upper())
        elif args.action=='frames':frames(p,int(args.arg));print(p.read32(BASE+8))
        else:
            if not args.arg or not args.arg.replace('_','').replace('-','').isalnum():raise ValueError('Simple screenshot label required')
            print(shot(p,args.arg))
    finally:p.close()


if __name__=='__main__':main()
