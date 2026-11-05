"""Capture every page of selected built English library rows and verify all bytes.

Dry run by default. --run sends guarded input and writes fresh timestamped evidence.
Screenshots still require visual review; successful byte checks are not fit approval.
Uses one PINE client. Do not run another PINE command while this tool is active.
"""
import argparse,hashlib,json,struct,sys,time
from pathlib import Path
from datetime import datetime,timezone
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from elf import ROOT,Elf,PATH
from extract import pack_members
from textcodec import decode,encode,controls,parse_table
import encyclopedia as page
import preview,control
from pine import Pine

def sha(b):return hashlib.sha256(b).hexdigest()

def ready(p,table=None,row=None,min_page=1,completed=None,timeout=15):
    deadline=time.monotonic()+timeout
    while time.monotonic()<deadline:
        state=preview.status(p);pg=state.get('pagination',{})
        if not state['running']:raise RuntimeError('Native preview driver exited before the requested page: '+str(state))
        if pg.get('error'):raise RuntimeError('Native pagination error '+str(pg))
        match=pg.get('active') and pg.get('page',0)>=min_page
        match=match and (table is None or pg.get('table')==table) and (row is None or pg.get('row')==row)
        match=match and (completed is None or state['completed']>=completed)
        cg=p.read32(0x237BF8) # _gp - 0x7978, native illustration pointer
        if match and p.read32(0x51D71C)==0 and cg and p.read(cg+0x2C,4)==struct.pack('<f',128.0):
            time.sleep(.15);return preview.status(p)
        time.sleep(.03)
    raise TimeoutError('Native library page did not settle: '+str(preview.status(p)))

def advance(p,old,timeout=15):
    control.press(p,'CIRCLE');deadline=time.monotonic()+timeout
    while time.monotonic()<deadline:
        now=preview.status(p)
        if now['completed']!=old['completed'] or now.get('pagination',{}).get('page')!=old['pagination']['page']:
            return now
        time.sleep(.03)
    raise TimeoutError('Circle did not advance or close the native page')

def select(p,table,row):
    old=ready(p);target=old['completed']+1;p.write(preview.MAIL+4,struct.pack('<II',table,row))
    while preview.status(p)['completed']<target:
        old=ready(p);advance(p,old)
    return ready(p,table,row,completed=target)

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('version');ap.add_argument('--start',type=int,default=0)
    ap.add_argument('--limit',type=int);ap.add_argument('--rows',nargs='+',help='Explicit pilot:ID or machine:ID, including untranslated native source rows')
    ap.add_argument('--run',action='store_true');args=ap.parse_args()
    requested=None
    if args.rows:
        if args.start or args.limit is not None:raise ValueError('Choose an explicit row list or translated-row slicing')
        aliases={'pilot':'04973_10515','machine':'04973_10516'};requested=[]
        for item in args.rows:
            kind,index=item.split(':');requested.append((aliases[kind],int(index)))
        if len(set(requested))!=len(requested):raise ValueError('Duplicate explicit row')
    build=ROOT/'work/output'/('v'+args.version);info=json.loads((build/'build_info.json').read_text(encoding='utf-8'))
    if not info.get('preview_request') or not info.get('encyclopedia_pagination'):raise ValueError('A paginated preview build is required')
    expected=Elf((build/'SLPS_250.70').read_bytes())
    private_getter=page.get_message_code(Elf(PATH.read_bytes()))
    if expected.at(page.GET_MESSAGE,len(private_getter))!=private_getter:
        raise ValueError('This audit requires the corrected private native message context')
    selected=[]
    for table in ('04973_10515','04973_10516'):
        raw=(build/'04973.pack').read_bytes();member=next(m for m in pack_members(raw) if m['id']==int(table.split('_')[1]))
        rows=parse_table(raw[member['offset']:member['offset']+member['size']])
        ids=sorted(i for t,i in requested if t==table) if requested is not None else sorted(int(key.split(':')[1]) for key in info['translated_rows'] if key.startswith(table+':'))
        if any(not 0<=i<len(rows) for i in ids):raise ValueError('Explicit native row outside table bounds')
        for i in ids:selected.append((table,i,rows[i]))
    selected=selected[args.start:args.start+args.limit if args.limit is not None else None]
    if not selected:raise ValueError('No selected built rows')
    print('Selected built entries',len(selected),'sample',[(t,i,sha(b)) for t,i,b in selected[:4]],flush=True)
    if not args.run:print('DRY RUN: --run captures all pages, compares bytes and leaves visual review pending.');return
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ');dest=ROOT/'work/ui/audits'/('v'+args.version+'_'+stamp);dest.mkdir(parents=True)
    fallbacks={(f['table'],f['row']):f for f in info.get('preview_descriptor_fallbacks',[])}
    report=dict(build=args.version,complete=False,selected_entries=len(selected),selection='explicit source/draft rows' if requested is not None else 'built translated rows',visual_review='pending',preview_descriptor_fallbacks=list(fallbacks.values()),entries=[])
    def save():(dest/'audit.json').write_text(json.dumps(report,indent=1),encoding='utf-8')
    p=Pine()
    try:
        live=preview.status(p)
        if not live['running']:raise RuntimeError('Start the same-build preview first')
        for va,n in ((preview.DRIVER,len(preview.driver_code())),(page.ORIGINAL,8),(page.CLONE,page.ORIGINAL_SIZE),(page.WRAPPER,len(page.wrapper_code())),(page.GET_PAGE,len(page.get_page_code())),(page.GET_MESSAGE,len(private_getter)),(0x9A4000,128)):
            if p.read(va,n)!=expected.at(va,n):raise RuntimeError('Live build code/font metrics mismatch')
        name=p.read(preview.NAME_SLOT,37).split(b'\0')[0]
        values_before=p.read(preview.NAME_SLOT,9*37)
        report['runtime_name_hex']=name.hex();report['runtime_values_sha256_before']=sha(values_before)
        print('Evidence:',dest,flush=True);save()
        for table,row,raw in selected:
            allowed={'{x00}','{C:819782960000}','{C:2332}','{C:2335}'}
            if set(controls(decode(raw)))-allowed:raise ValueError('Unprofiled runtime control in '+table+':'+str(row))
            # GetMessagePage converts this binary record into the native @0
            # command; mesPutS expands that runtime value when drawing the page.
            expected_text=encode(decode(raw).replace('{C:819782960000}','@0').replace('{x00}','')).strip(b'\n')
            state=select(p,int(table.split('_')[1]),row);pg=state['pagination']
            native=p.read(page.FULL,pg['source_bytes'])
            if native.strip(b'\n')!=expected_text:raise ValueError('Expanded built row differs from native full message')
            entry=dict(table=table,id=row,language='English draft' if table+':'+str(row) in info['translated_rows'] else 'untranslated native source',source_bytes=len(native),native_sha256=sha(native),built_row_sha256=sha(raw),pages=[]);bodies=[];font_mode=2
            if (int(table.split('_')[1]),row) in fallbacks:
                entry['illustration_fallback']=fallbacks[(int(table.split('_')[1]),row)]
            while True:
                state=ready(p,pg['table'],row,min_page=pg['page']);pg=state['pagination']
                blob=p.read(page.PAGE,page.PAGE_SIZE).split(b'\0')[0]
                body,footer=blob.split(b'^0,252,',1)
                if footer!=(b'Circle: Next page' if pg['more'] else b'Circle: Close'):raise ValueError('Incorrect native footer')
                if body.count(b'\n')>page.LINES:raise ValueError('Native body exceeds page line budget')
                start_mode=pg['font_start']-0x30;end_mode=pg['font_end']-0x30
                if start_mode!=font_mode:raise ValueError('Page did not carry the preceding source font mode')
                source_body=page.source_page_body(body,start_mode,end_mode);font_mode=end_mode
                label='v'+args.version.replace('.','')+'_audit_'+str(pg['table'])+'_'+str(row)+'_p'+str(pg['page'])
                shot=control.shot(p,label)
                entry['pages'].append(dict(page=pg['page'],more=pg['more'],body_sha256=sha(body),source_body_sha256=sha(source_body),font_start=start_mode,font_end=end_mode,screenshot=str(shot),snapshot=str(shot.with_name(label+'.p2s'))))
                bodies.append(source_body)
                if not pg['more']:break
                advance(p,state);pg=ready(p,pg['table'],row,min_page=pg['page']+1)['pagination']
            if b''.join(bodies).strip(b'\n')!=native.strip(b'\n'):raise ValueError('Pages lost or duplicated native text')
            if p.read(preview.NAME_SLOT,9*37)!=values_before:
                raise ValueError('Native description decoding corrupted runtime-value storage; no fit approval is valid')
            entry['byte_result']='all words retained';entry['visual_review']='pending';report['entries'].append(entry);save()
            print(table,row,'pages',len(entry['pages']),'complete text retained',flush=True)
        report['runtime_values_sha256_after']=sha(p.read(preview.NAME_SLOT,9*37))
        report['complete']=True;save();print('Saved',dest/'audit.json',flush=True)
    finally:p.close()
if __name__=='__main__':main()
