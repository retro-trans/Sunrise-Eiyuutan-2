"""Correct the remaining memory-card fixed-width ASCII centering loop."""
import argparse,json,re,struct
from elf import ROOT,Elf
from build import make_iso
import choices_patch as prior
from mips import Asm,lb,lbu,lui,addu,j,NOP,pack
import vwf

BASE=0x9BB900
HOOK=0x152408
BASE_SHA='af8b2f5cc7fe57585a651f8e178a5ce8b2dc53a647a0af9a7e8ef356a0c1fdf0'
digest=prior.digest

def code():
    # ASCII branch only. Preserve the native wide-character path and its
    # extra source-byte advance. The shared+2px spacing remains at152414.
    return pack([lbu('v0',0,'v1'),lui('at',vwf.TABLE>>16),addu('at','at','v0'),
                 lbu('v0',vwf.TABLE&65535,'at'),addu('s1','s1','v0'),j(0x152414),NOP])

def patch(data):
    if digest(data)!=BASE_SHA:raise ValueError('Complete0.2.6 baseline changed')
    e=Elf(data);out=bytearray(data)
    if e.at(HOOK,8)!=struct.pack('<2I',0x10000002,0x2631000D):raise ValueError('MC fixed-width branch changed')
    out[e.offset(HOOK):e.offset(HOOK)+8]=pack([j(BASE),NOP])
    i,s=next((i,s) for i,s in enumerate(e.segments) if s[0]==1 and s[2]==0x9A0000)
    typ,off,va,pa,size,mem,flags,alignment=s
    if va+max(size,mem)>BASE or BASE+len(code())>0x9C0000:raise ValueError('MC width hook collision')
    combined=data[off:off+size]+bytes(BASE-va-size)+code();position=(len(out)+4095)//4096*4096
    out.extend(bytes(position-len(out)));out.extend(combined)
    phoff=struct.unpack_from('<I',out,28)[0];phsize=struct.unpack_from('<H',out,42)[0]
    struct.pack_into('<8I',out,phoff+i*phsize,typ,position,va,pa,len(combined),len(combined),flags,alignment)
    return bytes(out)

def inputs():
    data,packs,overlays,report=prior.inputs();return patch(data),packs,overlays,dict(**report,mc_font=dict(hook=hex(HOOK),payload=hex(BASE),bytes=len(code()),purpose='Native memory-card centering uses actual VWF widths plus original2px spacing; Japanese branch unchanged.'))

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('version');ap.add_argument('--write',action='store_true');a=ap.parse_args()
    if not re.fullmatch(r'0\.\d+\.\d+',a.version):raise ValueError('Expected0.x.y')
    data,packs,overlays,report=inputs();print(json.dumps(dict(version=a.version,elf_sha256=digest(data),**report['mc_font']),indent=1))
    if not a.write:print('DRY: no game files/ISO written.');return
    dest=ROOT/'work/output'/('v'+a.version)
    if dest.exists():raise FileExistsError(dest)
    dest.mkdir(parents=True);(dest/'SLPS_250.70').write_bytes(data)
    for n,p in packs.items():(dest/f'{n:05d}.pack').write_bytes(p)
    for n,p in overlays.items():(dest/f'{n:05d}.evemap').write_bytes(p)
    image=dest/('Sunrise Eiyuutan 2 EN v'+a.version+'.iso');make_iso(image,data,packs,overlays)
    info=json.loads((ROOT/'work/output/v0.2.6/build_info.json').read_text('utf8'))
    info.update(version=a.version,based_on='0.2.6',**report,elf_sha256=digest(data),iso_path=str(image),iso_size=image.stat().st_size,in_game_validation='pending final native centering check')
    info['translated_rows']=sorted(set(info['translated_rows'])|{f'00023_01233:{i}' for i in range(23)})
    info['elf_translated_rows']=sorted(set(info['elf_translated_rows'])|{'E%X'%r['va'] for r in prior.prior.language()['rows']}|{'E%X'%r['va'] for r in prior.language()['rows']})
    info.pop('native_validation_report',None)
    (dest/'build_info.json').write_text(json.dumps(info,indent=1)+'\n','utf8');print('WRITE:',image)

if __name__=='__main__':main()
