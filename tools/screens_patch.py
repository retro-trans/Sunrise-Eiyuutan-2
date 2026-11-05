"""Focused town/save/phase UI integration on0.2.4; dry run by default.

Relocate complete strings, guard every native address consumer and preserve
original overlays' lengths. Help text retains each native call and choice.
"""
import argparse,json,struct,re
from elf import ROOT,PATH,Elf
from extract import pack_members
from build import replace_pack,make_iso
from textcodec import encode,decode,controls,TOKEN,parse_table,build_table
from message_pages import pages
from story_layout import pieces
import battle_icons_patch as prior

BASE=0x9BB000
LANGUAGE=ROOT/'work/translation/en/screens.en.json'
LANGUAGE_SHA='f1cadf6a42cc9105e22ae4ebac4b2f132736fb94c250c5315b9e8e1be4a3aee2'
BASE_SHA='915f1e45627fe111994b886c914b0e1cbb062d75231b9f54a7dede6b0f1e4380'
digest=prior.digest
GEOMETRY=((0x12F99C,0x240A00A8,0x240A00D8),(0x12F9B8,0x241E0054,0x241E006C),(0x12FAA0,0x240200A8,0x240200D8))

def language():
    if digest(LANGUAGE.read_bytes())!=LANGUAGE_SHA:raise ValueError('Screens wording review changed')
    d=json.loads(LANGUAGE.read_text('utf8'))
    if d['review']!=dict(accuracy='independent-reviewed',editorial='complete',glossary='complete',proofreading='complete'):
        raise ValueError('Incomplete language review')
    if [len(d[k]) for k in ('rows','help_rows','overlays','references')]!=[68,23,21,81]:raise ValueError('Inventory changed')
    return d

def measure(text,widths,runtime=504):
    value=0;pos=0
    for m in TOKEN.finditer(text):
        value+=sum((widths[ord(c)] if ord(c)<128 else 26)+2 for c in text[pos:m.start()])
        t=m.group().upper()
        if t=='{C:819782960100}':value+=runtime
        elif t not in ('{C:819782830000}','{C:819782830100}','{C:819782830400}'):
            raise ValueError('Unprofiled help body control '+t)
        pos=m.end()
    return value+sum((widths[ord(c)] if ord(c)<128 else 26)+2 for c in text[pos:])

def stage_help(text,row,widths):
    raw=encode(text);before=pages(raw);out=bytearray();layout=[]
    for i,p in enumerate(before):
        if not p['flags']&1:out+=raw[p['start']:p['end']];continue
        prefix,body,tail=pieces(raw,p);runtime=224 if row==0 else 504
        old=body
        if row!=16:
            lines=[];line=''
            for word in body.replace('\n',' ').split(' '):
                if not word:continue
                candidate=(line+' '+word) if line else word
                if measure(word,widths,runtime)>504:raise ValueError('Unbreakable help token')
                if line and measure(candidate,widths,runtime)>504:lines.append(line);line=word
                else:line=candidate
            if line:lines.append(line)
            body='\n'.join(lines)
        lines=body.split('\n');sizes=[measure(s,widths,runtime) for s in lines]
        if len(lines)>3 or max(sizes,default=0)>504 or len(encode(body))>=400:
            raise ValueError(f'Help row{row} call{i} needs a larger display: {sizes}; complete wording retained')
        if old.split()!=body.split():raise ValueError('Help words changed')
        out+=prefix+encode(body)+tail
        layout.append(dict(call=i,lines=lines,widths=sizes,runtime_reserve=runtime))
    out+=b'\0';after=pages(bytes(out))
    if len(before)!=len(after) or controls(decode(out))!=controls(text):raise ValueError('Help native boundaries changed')
    signature=lambda p:{k:v for k,v in p.items() if k not in ('start','end','body')}
    if any(signature(a)!=signature(b) for a,b in zip(before,after)):raise ValueError('Help native context changed')
    return bytes(out),layout

def patch_help(pack,widths):
    source=(ROOT/'work/source/afs/RESOURCE/00023.bin').read_bytes()
    if digest(source)!='892a27aa27e5d7137060ac9af68416c9d20f54e08bf705d04002dfbdd6ba0bcf':raise ValueError('Help source changed')
    member=next(m for m in pack_members(source) if m['id']==1233)
    rows=parse_table(source[member['offset']:member['offset']+member['size']]);fitting=[]
    for proposal in language()['help_rows']:
        i=proposal['id'];old=rows[i]
        if len(old)!=proposal['source_size'] or digest(old)!=proposal['source_sha256']:raise ValueError('Help row guard failed')
        if controls(decode(old))!=controls(proposal['en']):raise ValueError('Source control order changed')
        rows[i],fit=stage_help(proposal['en'],i,widths)
        if len(pages(old))!=len(pages(rows[i])):raise ValueError('Source page count changed')
        fitting.append(dict(id=i,layout=fit))
    return replace_pack(pack,{1233:build_table(rows)}),fitting

def patch_elf(data,new_pack_size,old_pack_size):
    if digest(data)!=BASE_SHA:raise ValueError('0.2.4 executable baseline changed')
    source=Elf(PATH.read_bytes());elf=Elf(data);out=bytearray(data);d=language();payload=bytearray();addresses={}
    def allocate(key,text,minimum=0):
        while len(payload)%8:payload.append(0)
        va=BASE+len(payload);raw=text.encode('cp932')+b'\0'
        payload.extend(raw);payload.extend(bytes(max(0,minimum-len(raw))))
        addresses[key]=va
    for r in d['rows']:
        old=source.at(r['va'],r['source_size'])
        if digest(old)!=r['source_sha256'] or elf.at(r['va'],len(old))!=old:raise ValueError('Source UI string changed')
        # Keep source-size padding for native LD/fixed-copy consumers.
        allocate(r['va'],r['en'],r['source_size'])
    for r in d['overlays']:allocate(r['id'],r['en'])
    changes={}
    def word(va,expected,new):
        if int.from_bytes(elf.at(va,4),'little')!=expected:raise ValueError(f'UI reference guard failed at{va:X}')
        if va in changes and changes[va]!=new:raise ValueError('Conflicting shared LUI')
        changes[va]=new
    for r in d['references']:
        address=addresses[r['target']]
        if r['kind']=='pointer':word(r['site'],r['word'],address);continue
        w=r['word'];op=w>>26
        high=(address>>16) if op==13 else ((address+0x8000)>>16)
        word(r['lui'],r['lui_word'],r['lui_word']&0xFFFF0000|high)
        word(r['site'],w,w&0xFFFF0000|(address&0xFFFF))
    for va,old,new in GEOMETRY:word(va,old,new)
    size_va=elf.symbol('_pacfileA')['va']+23*8+4
    word(size_va,old_pack_size,new_pack_size)
    for va,value in changes.items():struct.pack_into('<I',out,elf.offset(va),value)
    i,seg=next((i,s) for i,s in enumerate(elf.segments) if s[0]==1 and s[2]==0x9A0000)
    typ,off,va,pa,size,mem,flags,alignment=seg
    if va+max(size,mem)>BASE or BASE+len(payload)>0x9C0000:raise ValueError('UI payload collides with live memory')
    combined=data[off:off+size]+bytes(BASE-va-size)+payload
    position=(len(out)+4095)//4096*4096;out.extend(bytes(position-len(out)));out.extend(combined)
    phoff=struct.unpack_from('<I',out,28)[0];phsize=struct.unpack_from('<H',out,42)[0]
    struct.pack_into('<8I',out,phoff+i*phsize,typ,position,va,pa,len(combined),len(combined),flags,alignment)
    return bytes(out),addresses,changes,len(payload)

def patch_overlays(addresses):
    import menu_patch
    result={1:menu_patch.patch_title((ROOT/'work/source/afs/EVEMAP/00001.bin').read_bytes())}
    for r in language()['overlays']:
        n=int(r['id'].split('/')[1].split(':')[0]);path=ROOT/f'work/source/afs/EVEMAP/{n:05d}.bin'
        old=path.read_bytes()
        if digest(old)!=r['original_binary_sha256']:raise ValueError('Overlay source changed')
        off=r['offset'];raw=old[off:].split(b'\0',1)[0]+b'\0'
        if digest(raw)!=r['source_nul_terminated_sha256']:raise ValueError('Overlay source string changed')
        out=bytearray(result.get(n,old));hits=0
        # All selected overlays reference these labels through aligned data
        # tables before the first string (0x4D0); no executable consumers.
        for p in range(0,min(x['offset'] for x in language()['overlays'] if x['id'].startswith(f'EVEMAP/{n:05d}:')),4):
            if int.from_bytes(old[p:p+4],'little')==r['va']:
                struct.pack_into('<I',out,p,addresses[r['id']]);hits+=1
        expected=3 if n in (29,35,60) and off==0x4D0 else 1
        if hits!=expected:raise ValueError('Overlay reference inventory changed')
        result[n]=bytes(out)
    return result

def inputs():
    data,packs,_,_=prior.inputs()
    info=json.loads((ROOT/'work/output/v0.2.4/build_info.json').read_text('utf8'))
    old_size=len(packs[23]);packs[23],fit=patch_help(packs[23],bytes(info['font_widths']))
    data,addresses,changes,size=patch_elf(data,len(packs[23]),old_size)
    overlays=patch_overlays(addresses)
    return data,packs,overlays,dict(language_sha256=LANGUAGE_SHA,compiled_strings=68,overlay_strings=21,help_rows=23,
        payload_va=hex(BASE),payload_size=size,addresses={str(k):hex(v) for k,v in addresses.items()},patched_words={hex(k):hex(v) for k,v in changes.items()},help_layout=fit,
        menu_width=216,retained='All0.2.4 speaker, menu/name, narration, battle labels and icon changes retained.')

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('version');ap.add_argument('--write',action='store_true');a=ap.parse_args()
    if not re.fullmatch(r'0\.\d+\.\d+',a.version):raise ValueError('Expected0.x.y')
    data,packs,overlays,report=inputs()
    print(json.dumps({k:v for k,v in report.items() if k not in ('addresses','patched_words','help_layout')},indent=1))
    print('ELF',digest(data),'overlay members',sorted(overlays))
    if not a.write:print('DRY: no game files/ISO written.');return
    dest=ROOT/'work/output'/('v'+a.version)
    if dest.exists():raise FileExistsError(dest)
    dest.mkdir(parents=True);(dest/'SLPS_250.70').write_bytes(data)
    for n,p in packs.items():(dest/f'{n:05d}.pack').write_bytes(p)
    for n,p in overlays.items():(dest/f'{n:05d}.evemap').write_bytes(p)
    image=dest/('Sunrise Eiyuutan 2 EN v'+a.version+'.iso');make_iso(image,data,packs,overlays)
    info=json.loads((ROOT/'work/output/v0.2.4/build_info.json').read_text('utf8'))
    info.update(version=a.version,based_on='0.2.4',screens_ui=report,elf_sha256=digest(data),iso_path=str(image),iso_size=image.stat().st_size,
        in_game_validation='pending consolidated checks',scope='Town navigation, system/save UI, phase labels and23 help rows, retaining0.2.4. Other game text remains outside this focused build.')
    info.pop('native_validation_report',None)
    (dest/'build_info.json').write_text(json.dumps(info,indent=1)+'\n','utf8')
    print('WRITE:',image)

if __name__=='__main__':main()
