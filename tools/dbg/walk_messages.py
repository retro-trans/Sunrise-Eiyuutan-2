"""Capture complete native story pages and advance only after text finishes.

Input data only; no code/context/text writes. Default is a dry run. This bounded
walker stops when the specified built table is absent, a page is unprofiled, or
no complete manual dialogue arrives. It does not select branches or navigate.
"""
import argparse,hashlib,json,struct,time
from datetime import datetime,timezone
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from elf import ROOT
from pine import Pine
import control
from message_state import inspect,built_table,CONTEXT,VALUE_POOL,SPEAK_WINDOW,PARSER_CURSOR,ACTIVE


def end_position(body,widths,values,font=2):
    if font not in (2,5):raise ValueError('Unprofiled message font')
    x=y=0;i=0
    while i<len(body):
        c=body[i]
        if c in (35,37,64,124):
            if i+1>=len(body) or not 48<=body[i+1]<=57:raise ValueError('Unprofiled renderer command')
            v=body[i+1]-48;i+=2
            if c==35:
                if v not in (2,5):raise ValueError('Unprofiled font mode')
                font=v
            elif c==64:
                if v>=9:raise ValueError('Unprofiled runtime value')
                value=values[v*37:(v+1)*37].split(b'\0')[0]
                vx,vy,_=end_position(value,widths,values,font)
                if vy:raise ValueError('Multiline runtime value')
                x+=vx
            continue
        if c==10:
            i+=1
            if i<len(body):x=0;y+=28
            continue
        n=2 if 0x81<=c<=0x9f or 0xe0<=c<=0xfc else 1
        full=26 if font==2 else 13
        x+=(widths[c]*full//26 if c<128 else full)+2;i+=n
    return x,y,font


def prompt_ready(p,window,x,y):
    # mesSpeakWaitKey waits for the native voice handle before initializing the
    # prompt. A complete text cursor alone does not establish prompt readiness.
    obj=p.read32(0x239594)
    if not 0<obj<0x2000000-0x28 or not p.read32(0x239598):return False
    text=window[0]
    if not 0<text<0x2000000-0x20:return False
    ox,oy=struct.unpack('<II',p.read(text+0x18,8))
    px,py=struct.unpack('<II',p.read(obj+0x18,8))
    return (px,py)==(ox+x,oy+y)


def current(p,widths,require_prompt=False):
    if not p.read32(ACTIVE):return None
    wp=p.read32(SPEAK_WINDOW)
    if not 0<wp<0x2000000-0x48:return None
    raw=p.read(CONTEXT,VALUE_POOL-CONTEXT);body=raw[40:].split(b'\0')[0]
    if not body or not struct.unpack_from('<I',raw)[0]&1:return None
    win=struct.unpack('<18I',p.read(wp,72));values=p.read(VALUE_POOL,9*37)
    if win[2]!=0 or win[1]&1:raise ValueError('Automatic or nonmanual message mode')
    x,y,font=end_position(body,widths,values,win[4])
    if win[5:7]!=(x,y):return None
    if require_prompt and not prompt_ready(p,win,x,y):return None
    # Separate units may reopen the same voiced bark at the same source cursor.
    # The new native window identifies a new display even when the text is exact.
    key=(p.read32(PARSER_CURSOR),hashlib.sha256(raw).hexdigest(),wp)
    return key


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('version');ap.add_argument('--count',type=int,default=20)
    ap.add_argument('--table',default='04905_10383');ap.add_argument('--timeout',type=float,default=25)
    ap.add_argument('--allow-interleaved-barks',action='store_true',help='Also match the exact duplicate battle-line pair; physical pack origin remains ambiguous')
    ap.add_argument('--allow-opening-story',action='store_true',help='Also match opening table04905_10383 when normal story flow resumes')
    ap.add_argument('--prompt',action='store_true',help='Wait for the native continuation prompt after voice completion, and record guarded read-only triangle coordinates')
    ap.add_argument('--stable-seconds',type=float,default=.3,help='Complete-page stability interval; shorter explicit interval supports accelerated visual-only walks')
    ap.add_argument('--allow-tutorial-preview',action='store_true',help='Explicitly admit a fresh debug tutorial override build; no natural-trigger claim')
    ap.add_argument('--allow-battle-preview',action='store_true',help='Explicitly admit a fresh bounded native battle preview; no original-trigger claim')
    ap.add_argument('--run',action='store_true');a=ap.parse_args()
    if not 1<=a.count<=250:raise ValueError('Count must be1-250')
    if not .01<=a.stable_seconds<=1:raise ValueError('Stability interval must be0.01–1 seconds')
    info=json.loads((ROOT/f'work/output/v{a.version}/build_info.json').read_text())
    if info['preview_request']:raise ValueError('Standard flow required')
    if info.get('tutorial_preview') and not a.allow_tutorial_preview:raise ValueError('Explicit tutorial preview opt-in required')
    if info.get('battle_preview') and not a.allow_battle_preview:raise ValueError('Explicit battle preview opt-in required')
    allowed=[a.table];folder=ROOT/f'work/output/v{a.version}'
    if a.allow_interleaved_barks:
        if built_table(folder,'00022_10512')!=built_table(folder,'04971_11849'):raise ValueError('Battle pair no longer byte-identical; select each destination explicitly')
        if '00022_10512' not in allowed:allowed.append('00022_10512')
    if a.allow_opening_story and '04905_10383' not in allowed:allowed.append('04905_10383')
    print(f'Capture up to {a.count} complete manual pages on standard v{a.version}; allowed tables {allowed}. Verify context and advance Circle once per captured page. No branch selection.',flush=True)
    if a.allow_interleaved_barks:print('Identical battle-line bytes identify a logical row only; physical00022/04971 origin is NOT proven.',flush=True)
    if not a.run:print('DRY RUN: --run creates a new audit and presses Circle only after complete typed text.');return
    out=ROOT/'work/ui/message-audits'/('v'+a.version+'_'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'));out.mkdir(parents=True)
    report=dict(build=a.version,table=a.table,allowed_tables=allowed,kind='standard built-message observation',complete=False,pages=[],visual_review='pending',limitations=['Does not approve English wording/fit or unseen pages.','Input sampling ticks are not video frames.','Interleaved battle-line matches do not prove which identical physical table was loaded.'])
    report['stability_seconds']=a.stable_seconds
    if info.get('tutorial_preview'):
        report['kind']='fresh debug tutorial preview observation';report['tutorial_preview']=info['tutorial_preview']
        report['limitations'].append('Exact request overrides force these rows; their original conditional reachability is unverified.')
    if info.get('battle_preview'):
        report['kind']='fresh physical battle preview observation';report['battle_preview']=info['battle_preview']
        report['battle_first']=info.get('battle_preview_first',0);report['battle_count']=info.get('battle_preview_count',80)
        first,count=report['battle_first'],report['battle_count']
        selected=info.get('battle_preview_rows')
        if selected is not None:report['battle_rows']=selected
        selection_text=str(selected) if selected is not None else f'{first}-{first+count-1}'
        report['limitations'].append(f'The first tutorial request forces battle rows {selection_text} at one physical destination; original battle triggers are unverified.')
    p=Pine();last=None;stable=None;since=0;deadline=time.monotonic()+a.timeout
    try:
        control.check(p)
        while len(report['pages'])<a.count:
            key=current(p,info['font_widths'],require_prompt=a.prompt)
            if key is None and not p.read32(ACTIVE):last=None
            if key is not None and key!=last:
                if key!=stable:stable=key;since=time.monotonic()
                elif time.monotonic()-since>=a.stable_seconds:
                    label=f'v{a.version.replace(".","")}_story_p{len(report["pages"]):03d}'
                    screenshot=control.shot(p,label);state=next(screenshot.parent.glob('*.p2s'))
                    meta=None
                    for table in allowed:
                        candidate=inspect(state,a.version,table,include_prompt=a.prompt,allow_tutorial_preview=a.allow_tutorial_preview,allow_battle_preview=a.allow_battle_preview)
                        if meta is None:meta=candidate
                        if candidate['source_matches']:
                            meta=candidate
                            if table in ('00022_10512','04971_11849') and a.allow_interleaved_barks:
                                meta['indistinguishable_tables']=['00022_10512','04971_11849']
                                meta['physical_table_origin']='Unresolved; exact duplicate bytes/cursor match both logical destinations.'
                            break
                    meta.update(screenshot=str(screenshot),screenshot_sha256=hashlib.sha256(screenshot.read_bytes()).hexdigest())
                    if meta['active']!=1 or len(meta['source_matches'])!=1:
                        report['boundary_capture']=meta
                        raise ValueError('Captured page is outside the requested table or its proven grammar; inspect the same live scene')
                    report['pages'].append(meta);last=key;stable=None;deadline=time.monotonic()+a.timeout
                    source=meta['source_matches'][0];print(f'Captured {len(report["pages"])} {source["table"]}:{source["row"]} native-call{source["native_call"]} speaker{meta["context"]["speaker"]} voice{meta["context"]["voice"]}',flush=True)
                    if len(report['pages'])==a.count:report['complete']=True;break
                    control.press(p,'CIRCLE');continue
            else:stable=None
            if time.monotonic()>deadline:raise TimeoutError('No new complete manual dialogue; inspect same live scene. No restart performed.')
            time.sleep(.05)
    except Exception as exc:
        report['stop_reason']=type(exc).__name__+': '+str(exc);print(report['stop_reason'],flush=True)
    finally:
        p.close();(out/'audit.json').write_text(json.dumps(report,indent=1));print('Saved',out/'audit.json',flush=True)
    if not report['complete']:raise SystemExit(2)


if __name__=='__main__':main()
