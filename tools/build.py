"""Build a local v0.x.y test image. Dry run unless --write; --iso also creates ISO.

Text tables receive fresh offsets; packets and the AFS are rebuilt in index order.
The ELF's cached packet sizes follow the rebuilt files.
Original ISO and extracted source files are never modified.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import struct
from elf import ROOT, PATH, Elf
from iso import ISO, records
from extract import pack_members
from textcodec import decode,encode,controls,parse_table,build_table
import vwf
import layout
import encyclopedia
import story_layout
import battle_bank

ELF_SHA='00c598e051bd1287ec4523dc757ae2326fb5af28f2dc6c92a2450d6f290290a3'


def align(n,a=2048):return (n+a-1)//a*a
def digest(data):return hashlib.sha256(data).hexdigest()


def replace_pack(original,replacements):
    out=bytearray(original); count=struct.unpack_from('<I',out)[0]
    # Keep packet members in their original order, with monotonic offsets.
    # A growing member gets space by rebuilding the packet, not by adding a
    # backwards jump in the member-offset table.
    if any(len(replacements[m['id']])!=m['size'] for m in pack_members(original) if m['id'] in replacements):
        cursor=align(4+count*16,128);out=bytearray(original[:cursor])
        for i in range(count):
            mid,off,size,flag=struct.unpack_from('<4I',original,4+i*16)
            blob=replacements.get(mid,original[off:off+size]) if size else b''
            struct.pack_into('<4I',out,4+i*16,mid,cursor,len(blob),flag)
            if blob:
                out.extend(blob);cursor=align(len(out),128);out.extend(bytes(cursor-len(out)))
        out.extend(bytes(align(len(out))-len(out)));pack_members(out)
        return bytes(out)
    for i in range(count):
        mid,off,size,flag=struct.unpack_from('<4I',out,4+i*16)
        if not size or mid not in replacements:continue
        blob=replacements[mid]
        if len(blob)!=size:
            off=align(len(out),128);out.extend(bytes(off-len(out)));out.extend(blob)
        else:out[off:off+size]=blob
        struct.pack_into('<II',out,4+i*16+4,off,len(blob))
    # This game's resource headers end in a zero-sized sentinel.
    end=align(max(m['offset']+m['size'] for m in pack_members(out)),128)
    if struct.unpack_from('<I',out,4+(count-1)*16+8)[0]!=0:raise ValueError('Missing sentinel')
    struct.pack_into('<I',out,4+(count-1)*16+4,end)
    out.extend(bytes(align(len(out))-len(out)))
    # Every resource extent is checked again after rebuilding.
    pack_members(out)
    return bytes(out)


def inputs(enable_vwf=True,enable_translations=True,preview_request=None,paginate=True,tutorial_preview_request=None,battle_preview_request=None,battle_preview_first=0,battle_preview_count=80,battle_preview_rows=None):
    if sum(x is not None for x in (preview_request,tutorial_preview_request,battle_preview_request))>1:raise ValueError('Choose one native preview mode')
    if battle_preview_request is not None and (not enable_vwf or not enable_translations):raise ValueError('Battle preview requires translation/VWF')
    if battle_preview_request is None and ((battle_preview_first,battle_preview_count)!=(0,80) or battle_preview_rows is not None):raise ValueError('Battle selection requires an explicit battle preview')
    if tutorial_preview_request is not None:
        if preview_request is not None:raise ValueError('Choose one native preview mode')
        if not enable_vwf or not enable_translations:raise ValueError('Tutorial preview requires translation/VWF')
    original=PATH.read_bytes()
    if digest(original)!=ELF_SHA:raise ValueError('Unsupported ELF revision')
    elf=Elf(original)
    pack23=(ROOT/'work/source/afs/RESOURCE/00023.bin').read_bytes()
    fm=next(m for m in pack_members(pack23) if m['id']==vwf.FONT_MEMBER)
    font,widths=vwf.font(pack23[fm['offset']:fm['offset']+fm['size']])
    payload,patches=vwf.patches(original);payload[:128]=widths
    payload.extend(bytes(vwf.MONITOR-vwf.BASE-len(payload)))
    payload+=struct.pack('<4I',0x32474253,0,0,0) # SBG2, input, frame clock, last buttons
    payload.extend(bytes(0x100-16));payload+=vwf.monitor_code()
    preview_descriptor_fallbacks=[]
    if preview_request:
        import preview
        preview_descriptor_fallbacks=preview.descriptor_fallbacks(elf)
        kind,row=preview_request
        if not enable_vwf or not enable_translations:raise ValueError('Preview requires the translation/VWF build')
        off=preview.MAIL-vwf.BASE;payload[off:off+28]=preview.initial(kind,row)
        payload.extend(bytes(preview.ENTRY-vwf.BASE-len(payload)));payload+=preview.payload()
        patches+=preview.patches()
    pagination=bool(paginate and enable_vwf and enable_translations)
    if pagination:
        payload.extend(bytes(encyclopedia.BASE-vwf.BASE-len(payload)))
        payload+=encyclopedia.payload(elf);patches+=encyclopedia.patches(elf)
    if tutorial_preview_request is not None:
        import tutorial_preview
        if len(payload)>tutorial_preview.BASE-vwf.BASE:raise ValueError('Tutorial preview payload collision')
        payload.extend(bytes(tutorial_preview.BASE-vwf.BASE-len(payload)))
        payload+=tutorial_preview.payload(elf,tutorial_preview_request)
        patches+=tutorial_preview.patches(elf,tutorial_preview_request)
    if battle_preview_request is not None:
        import battle_preview
        battle_preview_first,battle_preview_count,ids=battle_preview.selection(battle_preview_first,battle_preview_count,battle_preview_rows)
        if battle_preview_rows is not None:battle_preview_rows=list(ids)
        if len(payload)>battle_preview.BASE-vwf.BASE:raise ValueError('Battle preview payload collision')
        payload.extend(bytes(battle_preview.BASE-vwf.BASE-len(payload)))
        payload+=battle_preview.payload(elf,battle_preview_request,battle_preview_first,battle_preview_count,battle_preview_rows);patches+=battle_preview.patches(elf,battle_preview_request,battle_preview_first,battle_preview_count)
    output=bytearray(original)
    if not enable_vwf:
        patches=[p for p in patches if p[3].startswith('input/')]
    for va,old,new,purpose in patches:
        pos=elf.offset(va)
        if output[pos:pos+len(old)]!=old:raise ValueError('Patch overlap: '+purpose)
        output[pos:pos+len(new)]=new
    phoff=struct.unpack_from('<I',output,28)[0];phsize,phcount=struct.unpack_from('<2H',output,42)
    segment_index=next(i for i,s in enumerate(elf.segments) if s[0]==1 and s[2]==0x9A0000)
    existing=elf.segments[segment_index]
    if elf.symbol('_evefunc_size')['va']!=0x20000:raise ValueError('Unexpected event function reservation')
    combined=bytearray(output[existing[1]:existing[1]+existing[4]]);combined.extend(bytes(vwf.BASE-existing[2]-len(combined)));combined+=payload
    if len(combined)>0x20000:raise ValueError('Event function reservation overflow')
    for typ,off,addr,pa,fs,ms,flags,al in elf.segments:
        if typ==1 and addr!=existing[2] and max(existing[2],addr)<min(existing[2]+len(combined),addr+ms):raise ValueError('Segment collision')
    fileoff=align(len(output),4096);output.extend(bytes(fileoff-len(output)));output+=combined
    struct.pack_into('<8I',output,phoff+phsize*segment_index,1,fileoff,existing[2],existing[2],len(combined),len(combined),7,4096)
    elf_rows=[]
    ef=ROOT/'work/translation/en/elf.en.json'
    if enable_translations and ef.exists():
        for row in json.loads(ef.read_text(encoding='utf-8'))['rows']:
            va,size=row['va'],row['source_size'];old=elf.at(va,size);en=row['en'].encode('ascii')
            if digest(old)!=row['source_sha256'] or elf.at(va+size,1)!=b'\0':raise ValueError('ELF source changed')
            if len(en)>size:raise ValueError('ELF literal requires relocation; no shortening applied')
            if re.findall(rb'%[a-zA-Z]',old)!=re.findall(rb'%[a-zA-Z]',en):raise ValueError('ELF printf changed')
            off=elf.offset(va);output[off:off+size+1]=en+bytes(size+1-len(en));elf_rows.append(row['id'])
    replacements={23:{vwf.FONT_MEMBER:font}} if enable_vwf else {};translated=[];fitting=[]
    export_files=sorted((ROOT/'work/translation/en/dat').glob('*.en.json')) if enable_translations else []
    exports={}
    for tr in export_files:
        obj=json.loads(tr.read_text(encoding='utf-8'));name=obj['table']
        if name in exports or tr.name!=name+'.en.json':raise ValueError('Duplicate/mismatched English export')
        exports[name]=obj
    if enable_translations:battle_bank.validate_alias_exports(exports)
    if battle_preview_request is not None:battle_preview.require_translations(exports,battle_preview_first,battle_preview_count,battle_preview_rows)
    for name,obj in sorted(exports.items()):
        pn,mid=map(int,name.split('_'))
        pack=(ROOT/'work/source/afs/RESOURCE'/('%05d.bin'%pn)).read_bytes()
        member=next(m for m in pack_members(pack) if m['id']==mid)
        raw=pack[member['offset']:member['offset']+member['size']];rows=parse_table(raw)
        if name in battle_bank.TABLES:battle_bank.validate_table(raw,name)
        seen=set()
        for row in obj['rows']:
            i=row['id'];en=row['en']
            if i in seen or not isinstance(i,int) or not 0<=i<len(rows):raise ValueError('Duplicate/invalid row ID')
            seen.add(i)
            jp=decode(rows[i])
            if row['source_sha256']!=digest(rows[i]):raise ValueError('Source changed: %s:%d'%(name,i))
            if controls(jp)!=controls(en):raise ValueError('Control changed: %s:%d'%(name,i))
            if re.search(r'[\u3040-\u30ff\u3400-\u9fff\uff61-\uff9f]',en):raise ValueError('Japanese in English row')
            if name not in ('04973_10515','04973_10516','00023_01233','04904_10382','04905_10383','04949_10472')+battle_bank.TABLES:
                raise ValueError('No display profile for '+name+'; inspect its scene before building translations')
            if name in battle_bank.TABLES:
                if not enable_vwf:raise ValueError('Battle bark requires the measured VWF')
                battle_profile=battle_bank.validate_row(jp,en)
                en,staging=story_layout.wrap_row(en,widths,profile='battle-barks')
                battle_bank.validate_row(jp,en)
                fitting.append(dict(table=name,id=i,max_line_px=max((p['max_line_px'] for p in staging),default=0),
                    profile='Battle bark:504px/3 lines,26px font,2px spacing,478px final line; one original body, exact original calls; native fit approval remains separate',staging_profile=battle_profile,native_pages=staging))
            elif name=='04949_10472':
                if not enable_vwf:raise ValueError('Battle tutorial requires the measured VWF')
                if digest(raw)!='ddf2bffc6e963527aea56d520b54e5cc0da2d525d47a76b28325e9552778ec2e' or len(rows)!=42:
                    raise ValueError('Unsupported first-battle tutorial source revision')
                en,staging=story_layout.wrap_row(en,widths,profile='battle-tutorial')
                fitting.append(dict(table=name,id=i,max_line_px=max((p['max_line_px'] for p in staging),default=0),
                    profile='First-battle tutorial:504px/3 lines,26px font,2px spacing; colors0/4/6 and all native call/voice boundaries retained; native fit approval remains separate',
                    native_pages=staging))
            elif name=='04904_10382':
                import narration_patch
                if not enable_vwf:raise ValueError('Opening narration requires VWF')
                if digest(raw)!=narration_patch.SOURCE_TABLE_SHA or len(rows)!=11:
                    raise ValueError('Unsupported opening narration source revision')
                en,staging=narration_patch.stage_row(en,widths)
                fitting.append(dict(table=name,id=i,max_line_px=max((max(p['widths']) for p in staging),default=0),
                    profile='Opening narration:504px/3 lines; all native row/call/voice/function boundaries and blank calls retained',native_pages=staging))
            elif name=='04905_10383':
                if not enable_vwf:raise ValueError('Story layout requires the measured VWF')
                if digest(raw)!='fc3cd07ccc3e16a1c55a9c0380644f16778f34d19e5a0de5ac20f100b4248d64' or len(rows)!=49:
                    raise ValueError('Unsupported opening-story source revision')
                en,staging=story_layout.wrap_row(en,widths,centered_calls={33:(3,),40:(1,)}.get(i,()))
                fitting.append(dict(table=name,id=i,max_line_px=max((p['max_line_px'] for p in staging),default=0),
                    profile='Opening story:504px/3 lines,26px font,2px spacing; original native call/voice/function boundaries retained; native fit approval remains separate',
                    native_pages=staging))
            else:
                en=layout.wrap(en,widths,504)
                fitting.append(dict(table=name,id=i,max_line_px=max(layout.line_widths(en,widths)),
                                    profile='504px, 26px font, 2px spacing; encyclopedia dimensions from infoCirculation; menu fit pending'))
            built=encode(en)
            if not built.endswith(b'\0'):raise ValueError('Missing row terminator')
            if any(ch in en for ch in '#@%^|'):raise ValueError('Reserved renderer character')
            rows[i]=built;translated.append('%s:%d'%(name,i))
        table=build_table(rows)
        if pagination and name in ('04973_10515','04973_10516') and max(map(len,rows))>=encyclopedia.FULL_SIZE-128:
            raise ValueError('Encyclopedia row exceeds bounded native decoding capacity')
        if parse_table(table)!=rows:raise ValueError('Built table validation failed')
        replacements.setdefault(pn,{})[mid]=table
    packs={pn:replace_pack((ROOT/'work/source/afs/RESOURCE'/('%05d.bin'%pn)).read_bytes(),ms) for pn,ms in replacements.items()}
    # The game allocates/reads packs using its own cached sizes, independent
    # of the AFS index. Updating only the container truncates growing packs.
    cache=elf.symbol('_pacfileA')
    if cache['size']!=5614*8:raise ValueError('Unexpected cached resource table')
    for pn,blob in packs.items():
        va=cache['va']+pn*8+4;old=elf.at(va,4)
        if struct.unpack('<I',old)[0]!=(ROOT/'work/source/afs/RESOURCE'/('%05d.bin'%pn)).stat().st_size:
            raise ValueError('Cached size disagrees with original AFS')
        new=struct.pack('<I',len(blob));off=elf.offset(va);output[off:off+4]=new
        patches.append((va,old,new,'cached pack size %05d'%pn))
    menu_name_ui=None;speaker_names=None;battle_ui=None;battle_icons=None
    if enable_translations:
        import menu_patch
        output,menu_name_ui=menu_patch.patch_elf(bytes(output))
        import speaker_patch
        if not enable_vwf:raise ValueError('English speaker names require VWF')
        output,speaker_names=speaker_patch.patch_elf(bytes(output),widths)
        import battle_ui_patch
        output,packs,battle_ui,_=battle_ui_patch.patch(bytes(output),packs)
        import battle_icons_patch
        packs[22],_=battle_icons_patch.patch_pack(packs[22])
        battle_icons=dict(language_sha256=battle_icons_patch.LANGUAGE_SHA,pack=22,member=10051,cells=battle_icons_patch.language()['rows'])
    return bytes(output),packs,dict(vwf_enabled=enable_vwf,encyclopedia_pagination=pagination,preview_request=preview_request,tutorial_preview=tutorial_preview_request,battle_preview=battle_preview_request,battle_preview_first=battle_preview_first,battle_preview_count=battle_preview_count,battle_preview_rows=battle_preview_rows,preview_descriptor_fallbacks=preview_descriptor_fallbacks,translated_rows=translated,elf_translated_rows=elf_rows,fitting=fitting,menu_name_ui=menu_name_ui,
                                  patches=[dict(va=hex(a),old=o.hex(),new=n.hex(),purpose=s) for a,o,n,s in patches],
                                  speaker_names=speaker_names,battle_ui=battle_ui,battle_icons=battle_icons,elf_sha256=digest(output),font_widths=list(widths),source_elf_sha256=ELF_SHA)


def update_record(stream,rec,lba,size):
    stream.seek(rec['record_offset']+2);stream.write(struct.pack('<I',lba)+struct.pack('>I',lba))
    stream.seek(rec['record_offset']+10);stream.write(struct.pack('<I',size)+struct.pack('>I',size))


def make_iso(dest,elfdata,packs,event_overlays=None):
    inventory=records(ISO);resource=next(r for r in inventory if r['path']=='/RESOURCE.AFS')
    boot=next(r for r in inventory if r['path']=='/SLPS_250.70')
    from afs import index,validate_partition
    def copy_n(src,out,n):
        while n:
            b=src.read(min(n,4*1024*1024))
            if not b:raise ValueError('Truncated source ISO')
            out.write(b);n-=len(b)
    # Keep the game's AFS near its original LBA; preserve its location where
    # possible rather than relying on CRI's handling of high archive bases.
    start=resource['lba']*2048;old_end=start+resource['size']
    if old_end%2048:raise ValueError('Expected sector-aligned RESOURCE extent')
    with open(ISO,'rb') as src,open(dest,'w+b') as out:
        original_entries=index(src,start,resource['size'])
        first=original_entries[0]['offset']
        src.seek(0);copy_n(src,out,start+first)
        archive_end=start+first
        for pn,old in enumerate(original_entries):
            # ADXF_LoadPartitionNw compacts the AFS directory into a first
            # sector plus per-file sector counts. It therefore requires files
            # to remain contiguous and in index order, even if raw AFS permits gaps.
            off=archive_end-start;out.seek(archive_end)
            if pn in packs:
                blob=packs[pn];out.write(blob);size=len(blob)
            else:
                src.seek(start+old['offset']);copy_n(src,out,old['size']);size=old['size']
            archive_end=align(out.tell());out.write(bytes(archive_end-out.tell()))
            out.seek(start+8+pn*8);out.write(struct.pack('<II',off,size))
        resource_size=archive_end-start
        delta=archive_end-old_end
        src.seek(old_end);out.seek(archive_end);copy_n(src,out,ISO.stat().st_size-old_end)
        elfpos=align(out.tell());out.write(bytes(elfpos-out.tell()));out.write(elfdata)
        end=align(out.tell());out.write(bytes(end-out.tell()))
        update_record(out,resource,start//2048,resource_size);update_record(out,boot,elfpos//2048,len(elfdata))
        for rec in inventory:
            if rec['lba']*2048>=old_end:
                update_record(out,rec,rec['lba']+delta//2048,rec['size'])
        if event_overlays:
            event=next(r for r in inventory if r['path']=='/EVEMAP.AFS')
            event_base=event['lba']*2048+(delta if event['lba']*2048>=old_end else 0)
            event_entries=index(src,event['lba']*2048,event['size'])
            for number,blob in event_overlays.items():
                member=event_entries[number]
                if len(blob)!=member['size']:raise ValueError('Event overlay must retain its extent')
                out.seek(event_base+member['offset']);out.write(blob)
        # Update all ISO9660 primary/supplementary volume descriptors present.
        sec=16
        while True:
            out.seek(sec*2048);head=out.read(7)
            if head[1:6]!=b'CD001':raise ValueError('Bad volume descriptor')
            if head[0] in (1,2):
                out.seek(sec*2048+80);out.write(struct.pack('<I',end//2048)+struct.pack('>I',end//2048))
            if head[0]==255:break
            sec+=1
    # Re-read through the finished image's own directory and AFS index.
    from iso import read_record
    built=records(dest)
    if read_record(dest,next(r for r in built if r['path']==boot['path']))!=elfdata:raise ValueError('ISO ELF mismatch')
    rec=next(r for r in built if r['path']==resource['path'])
    with open(dest,'rb') as f:
        entries=index(f,rec['lba']*2048,rec['size'])
        validate_partition(entries)
        for pn,data in packs.items():
            f.seek(rec['lba']*2048+entries[pn]['offset'])
            if f.read(entries[pn]['size'])!=data:raise ValueError('ISO resource mismatch')
        if event_overlays:
            event=next(r for r in built if r['path']=='/EVEMAP.AFS')
            entries=index(f,event['lba']*2048,event['size'])
            for number,blob in event_overlays.items():
                f.seek(event['lba']*2048+entries[number]['offset'])
                if f.read(entries[number]['size'])!=blob:raise ValueError('ISO event overlay mismatch')


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('version');ap.add_argument('--write',action='store_true');ap.add_argument('--iso',action='store_true')
    ap.add_argument('--debug-only',action='store_true',help='Isolate the monitor: original fonts/text and renderer')
    ap.add_argument('--font-only',action='store_true',help='VWF and monitor, original text')
    ap.add_argument('--preview',choices=['pilot','machine'],help='Intrusive debug build: encyclopedia after New Game initialization')
    ap.add_argument('--preview-row',type=int,default=0)
    ap.add_argument('--tutorial-preview',choices=['missing','row1','row33'],help='Fresh debug build: single-use exact tutorial request overrides; not normal progression')
    ap.add_argument('--battle-preview',choices=['canonical','alias'],help='Fresh debug build: preview a bounded reviewed battle range through one physical resource; not original battle triggers')
    ap.add_argument('--battle-first',type=int,default=0);ap.add_argument('--battle-count',type=int,default=80)
    ap.add_argument('--battle-rows',help='Explicit reviewed IDs/ranges, e.g.480-502,504-524,526-559; omitted IDs stay untouched')
    args=ap.parse_args()
    if not re.fullmatch(r'0\.\d+\.\d+',args.version):raise ValueError('Expected 0.x.y')
    if args.debug_only and args.font_only:raise ValueError('Choose one diagnostic mode')
    request=(args.preview,args.preview_row) if args.preview else None
    selected=None
    if args.battle_rows is not None:
        import battle_preview
        selected=battle_preview.parse_rows(args.battle_rows)
    data,packs,report=inputs(not args.debug_only,not args.debug_only and not args.font_only,request,tutorial_preview_request=args.tutorial_preview,battle_preview_request=args.battle_preview,battle_preview_first=args.battle_first,battle_preview_count=args.battle_count,battle_preview_rows=selected)
    print('Version',args.version,'ELF bytes',len(data),'patched packs',[(i,len(p)) for i,p in packs.items()],
          'translated rows',len(report['translated_rows']))
    if request:print('DEBUG PREVIEW:',request,'normal game flow is interrupted after New Game initialization')
    if args.tutorial_preview:print('DEBUG TUTORIAL PREVIEW:',args.tutorial_preview,'exact request overrides only; original conditional reachability is not tested')
    if args.battle_preview:print('DEBUG BATTLE PREVIEW:',args.battle_preview,'native rows',selected if selected is not None else list(range(report['battle_preview_first'],report['battle_preview_first']+report['battle_preview_count'])),'original battle triggers are not tested')
    if not args.write:print('DRY RUN: --write saves the build; --iso additionally creates and verifies a test ISO');return
    dest=ROOT/'work/output'/('v'+args.version);dest.mkdir(parents=True,exist_ok=False)
    (dest/'SLPS_250.70').write_bytes(data)
    for pn,blob in packs.items():(dest/('%05d.pack'%pn)).write_bytes(blob)
    report.update(version=args.version,in_game_validation='pending')
    if args.iso:
        event_overlays=None
        if report.get('menu_name_ui'):
            import menu_patch
            event_overlays={1:menu_patch.patch_title((ROOT/'work/source/afs/EVEMAP/00001.bin').read_bytes())}
        image=dest/('Sunrise Eiyuutan 2 EN v'+args.version+'.iso');make_iso(image,data,packs,event_overlays)
        report['iso_path']=str(image);report['iso_size']=image.stat().st_size
    (dest/'build_info.json').write_text(json.dumps(report,indent=1),encoding='utf-8')
    print('Verified build:',dest)


if __name__=='__main__':main()
