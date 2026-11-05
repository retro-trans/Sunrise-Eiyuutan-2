"""Guarded standard boot navigation and optional temporary maximum-name test.

Only input and a single37-byte runtime-value name slot are ever written. No
code/text/interpreter pointer writes or old-state loading. --restore restores
the recorded name after the bounded native test. Default is a dry run.
"""
import argparse,hashlib,json,time
from datetime import datetime,timezone
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from elf import ROOT,Elf
from textcodec import parse_table
from message_pages import pages
from message_state import built_table,CONTEXT,VALUE_POOL,ACTIVE
from walk_messages import current
from pine import Pine
import control

NAME_BYTES=bytes.fromhex('8276')*8+bytes(21)


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('version');ap.add_argument('--maximum-name',action='store_true');ap.add_argument('--restore');ap.add_argument('--timeout',type=float,default=100);ap.add_argument('--run',action='store_true')
    ap.add_argument('--allow-tutorial-preview',action='store_true');ap.add_argument('--allow-battle-preview',action='store_true');a=ap.parse_args()
    if not 5<=a.timeout<=600:raise ValueError('Timeout must be5-600 seconds')
    folder=ROOT/f'work/output/v{a.version}';info=json.loads((folder/'build_info.json').read_text())
    if info['preview_request']:raise ValueError('Requires standard build')
    if info.get('tutorial_preview') and not a.allow_tutorial_preview:raise ValueError('Explicit tutorial preview opt-in required')
    if info.get('battle_preview') and not a.allow_battle_preview:raise ValueError('Explicit battle preview opt-in required')
    target=next(p for p in pages(parse_table(built_table(folder,'04905_10383'))[0]) if p['flags']&1)
    print('Restore recorded runtime name only.' if a.restore else 'Navigate fresh standard boot to first complete opening-story caption; stop before advancing it. Maximum-name test: '+str(a.maximum_name),flush=True)
    if not a.run:print('DRY RUN: --run performs guarded input/name actions.');return
    p=Pine();report=dict(build=a.version,muted='project configuration',map_stages=[],maximum_name=a.maximum_name,timeout_seconds=a.timeout,complete=False)
    if info.get('tutorial_preview'):report['tutorial_preview']=info['tutorial_preview']
    if info.get('battle_preview'):report['battle_preview']=info['battle_preview']
    try:
        control.check(p);elf=Elf((folder/'SLPS_250.70').read_bytes())
        for va,n in ((0x12e9a0,0x314),(0x9a4000,128)):
            if p.read(va,n)!=elf.at(va,n):raise ValueError('Live message code/metrics do not match selected build')
        if info.get('tutorial_preview'):
            import tutorial_preview as preview
            for va,n in ((preview.HOOK,8),(preview.BASE,preview.MAIL-preview.BASE)):
                if p.read(va,n)!=elf.at(va,n):raise ValueError('Live tutorial override differs from selected build')
        if info.get('battle_preview'):
            import battle_preview as preview
            for va,n in ((preview.HOOK,8),(preview.BASE,preview.MAIL-preview.BASE)):
                if p.read(va,n)!=elf.at(va,n):raise ValueError('Live battle preview differs from selected build')
        if a.restore:
            before=json.loads(Path(a.restore).read_text());assert before['build']==a.version and before['complete'] and before['maximum_name']
            original=bytes.fromhex(before['name_before_hex']);values=p.read(VALUE_POOL,9*37)
            if values[:37]!=NAME_BYTES or hashlib.sha256(values[37:]).hexdigest()!=before['other_values_sha256']:raise ValueError('Runtime values changed outside the bounded name test')
            p.write(VALUE_POOL,original);assert p.read(VALUE_POOL,37)==original
            report.update(complete=True,name_restored=True,source_report=str(Path(a.restore).resolve()))
        else:
            deadline=time.monotonic()+a.timeout;last=None;stable=None;since=0
            while time.monotonic()<deadline:
                if p.read32(ACTIVE):
                    raw=p.read(CONTEXT,440);body=raw[40:].split(b'\0')[0]
                    if body and body!=target['body']:raise ValueError('Already in another message; no further input injected')
                    key=current(p,info['font_widths']) if body else None
                    if key is not None:
                        if key!=stable:stable=key;since=time.monotonic()
                        elif time.monotonic()-since>=.3:
                            values=p.read(VALUE_POOL,9*37)
                            report.update(name_before_hex=values[:37].hex(),other_values_sha256=hashlib.sha256(values[37:]).hexdigest())
                            if a.maximum_name:p.write(VALUE_POOL,NAME_BYTES)
                            after=p.read(VALUE_POOL,9*37);assert after[37:]==values[37:]
                            if a.maximum_name:assert after[:37]==NAME_BYTES
                            report.update(complete=True,at_first_caption=True,runtime_values_sha256=hashlib.sha256(after).hexdigest());break
                    time.sleep(.05);continue
                stage=p.read32(0x23955c)
                if stage!=last:report['map_stages'].append(stage);print('Native map',stage,flush=True);last=stage
                for button in (('CIRCLE','CIRCLE') if stage==1 else ('TRIANGLE','START','CIRCLE')):
                    if p.read32(ACTIVE):break
                    control.press(p,button,hold=30 if button=='TRIANGLE' else 12);time.sleep(.25)
            if not report['complete']:raise TimeoutError('First caption not reached; inspect same live instance. No restart performed.')
    except Exception as exc:
        report['stop_reason']=type(exc).__name__+': '+str(exc);print(report['stop_reason'],flush=True)
    finally:
        p.close();out=ROOT/'work/ui/story-starts'/('v'+a.version+'_'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'));out.mkdir(parents=True)
        (out/'report.json').write_text(json.dumps(report,indent=1));print(json.dumps(report,indent=1));print('Saved',out/'report.json',flush=True)
    if not report['complete']:raise SystemExit(2)


if __name__=='__main__':main()
