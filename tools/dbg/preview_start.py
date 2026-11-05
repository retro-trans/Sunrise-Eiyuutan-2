"""Reach the encyclopedia preview from a fresh debug boot, using guarded input.

Map 2 includes the opening movie/title prompt; map 1 is the title menu. Attract playback can begin
again while tests run, so inspect native state between presses and stop as soon
as the preview driver starts. Never installs or changes executable code.
"""
import argparse,time
from pine import Pine
import control,preview

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--run',action='store_true');args=ap.parse_args()
    if not args.run:
        print('DRY RUN: verify preview monitor; skip movie with held Triangle; Start/Circle at title; stop on preview entry.');return
    p=Pine()
    try:
        state=preview.status(p)
        if state['completed'] and not state['running']:raise RuntimeError('Preview already exited; fresh-boot its ISO first')
        deadline=time.monotonic()+45;last=None
        while time.monotonic()<deadline:
            state=preview.status(p)
            if state['running']:
                print('Preview started:',state,flush=True);return
            stage=p.read32(0x23955C)
            if stage!=last:print('Native map',stage,flush=True);last=stage
            buttons=('CIRCLE','CIRCLE') if stage==1 else ('TRIANGLE','START','CIRCLE')
            for button in buttons:
                if preview.status(p)['running']:break
                control.press(p,button,hold=30 if button=='TRIANGLE' else 12);time.sleep(.3)
        raise TimeoutError('Preview not reached; inspect current screenshot and same live instance')
    finally:p.close()
if __name__=='__main__':main()
