"""Sample unframed automatic narration; visual completeness is reviewed separately.
No code/text/context/input writes. Uses scratch state slot9, retains PNGs only.
"""
import argparse,hashlib,json,struct,sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from elf import ROOT,Elf
from message_pages import pages
from message_state import built_table,CONTEXT
from textcodec import parse_table
from pine import Pine
from sstate import State
import control


def capture_png(p,path):
    states=ROOT/'work/emulator/pcsx2/sstates'
    old={f:f.stat().st_mtime_ns for f in states.glob('SLPS-25070*.09.p2s')}
    p.save_state(9);end=time.monotonic()+10
    while time.monotonic()<end:
        for f in states.glob('SLPS-25070*.09.p2s'):
            if old.get(f)!=f.stat().st_mtime_ns:
                try:
                    png=State(f).screenshot();path.write_bytes(png)
                    return hashlib.sha256(png).hexdigest()
                except (OSError,ValueError,KeyError):pass
        time.sleep(.03)
    raise TimeoutError('Same-build framebuffer not ready')


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('version');ap.add_argument('--run',action='store_true');ap.add_argument('--timeout',type=int,default=180);ap.add_argument('--tag',default='ready');a=ap.parse_args()
    folder=ROOT/'work/output'/('v'+a.version)
    expected={p['voice']:(i,p['body']) for i,raw in enumerate(parse_table(built_table(folder,'04904_10382'))) for p in pages(raw) if p['flags']&1}
    assert set(expected)==set(range(15027,15038))
    print('Sample all11 automatic narration bodies; retain PNGs and exact source-context matches. No input/text/code/context writes. Visual proof remains separate.',flush=True)
    if not a.run:print('DRY: --run observes the original sequence from its beginning.');return
    assert a.tag.isalnum()
    report_path=folder/('narration-native-'+a.tag+'.json');assert not report_path.exists()
    captures=ROOT/'work/ui'/('narration-v'+a.version+'-'+a.tag);captures.mkdir(parents=True,exist_ok=False)
    report=dict(version=a.version,kind='Original unframed automatic narration; source-context matched framebuffer samples',samples=[],rows=[],complete=False,visual_review='pending separate actual image inspection')
    p=None;latest={};deadline=time.monotonic()+a.timeout
    try:
        while True:
            try:
                p=Pine()
                if p.game_id()=='SLPS-25070' and p.read32(control.BASE)==0x32474253:break
            except OSError:pass
            if p:p.close();p=None
            if time.monotonic()>deadline:raise TimeoutError('Game not ready')
            time.sleep(.2)
        elf=Elf((folder/'SLPS_250.70').read_bytes());assert p.read(0x9B8000,1073)==elf.at(0x9B8000,1073)
        last_print=None
        while time.monotonic()<deadline:
            raw=p.read(CONTEXT,440);voice=struct.unpack_from('<I',raw,8)[0];body=raw[40:].split(b'\0')[0]
            if voice in expected and body:
                row,wanted=expected[voice]
                if body!=wanted:raise ValueError('Built/source context mismatch row'+str(row))
                if row!=last_print:print('Sampling narration row',row,flush=True);last_print=row
                image=captures/('row%02d_sample%04d.png'%(row,len(report['samples'])));h=capture_png(p,image)
                sample=dict(id=row,voice=voice,screenshot=str(image),screenshot_sha256=h,body_sha256=hashlib.sha256(body).hexdigest())
                report['samples'].append(sample);latest[row]=sample
            elif len(latest)==11:report['complete']=True;break
            time.sleep(.2)
        if not report['complete']:raise TimeoutError('Incomplete source sequence sample coverage')
    except Exception as exc:
        report['stop_reason']=type(exc).__name__+': '+str(exc);print(report['stop_reason'],flush=True)
    finally:
        if p:p.close()
        report['rows']=[latest[k] for k in sorted(latest)];report_path.write_text(json.dumps(report,indent=1)+'\n','utf-8')
        print('Saved',report_path,'rows',len(latest),'samples',len(report['samples']),flush=True)
    if not report['complete']:raise SystemExit(2)


if __name__=='__main__':main()
