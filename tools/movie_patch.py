"""Movies/preview captions and native ending lyrics, retaining complete v0.2.18."""
import argparse,json,hashlib,struct,re
from pathlib import Path
import squad_name_patch as prior
from elf import ROOT,Elf
from mips import *
from iso import records,read_record,ISO
from afs import index
from build import make_iso
import movie_lyrics_native as native
import movie_subtitles as captions
import movie_pss,vwf

BASE_SHA='ad99fe25326d032c6a64328a0f28eb7dbc9dc0c582c8f926cc24f924d1637816'
LANGUAGE_SHA='ed1b1e0b975a51838a62e999478372f1e3886bf44dc8bd57b3bd28ad68e0f959'
JAPANESE_SHA='0bed1fbaf3c8ae5b12f58a38e134cfd7f42e085270f577daefe32f07ea635151'
POOLS=((native.TABLE+34*20+8,0x9A5000),(0x9B6500,0x9B7000),(0x9B78B8,0x9B8000))
digest=lambda b:hashlib.sha256(b).hexdigest()

def language():
    raw=captions.LANGUAGE.read_bytes();d=json.loads(raw);jraw=captions.JAPANESE.read_bytes();jp=json.loads(jraw)
    if digest(raw)!=LANGUAGE_SHA or digest(jraw)!=JAPANESE_SHA:raise ValueError('Reviewed movie language revision changed')
    if d['review']!=dict(accuracy='independent-reviewed-asr',editorial='complete',glossary='complete',proofreading='complete'):raise ValueError('Movie language pipeline incomplete')
    for c in [*d['ending']['cues'],*[c for m in d['movies']for c in m.get('lyrics',[])]]:
        if digest(jp['cues'][c['id']].encode())!=c['jp_sha256']:raise ValueError('Japanese lyric source changed')
    return d,jp,dict(language_sha256=digest(raw),japanese_lyric_source_sha256=digest(jraw))

def native_text(s):
    for old,new in [('’',"'"),('‘',"'"),('“','"'),('”','"'),('—','--'),('–','-')]:s=s.replace(old,new)
    s.encode('cp932');return s

def wrap_native(s,size,widths,limit=596):
    def width(s):return sum(vwf.scaled_width(ord(c),size,widths)+2 for c in s)
    lines=[]
    for para in native_text(s).splitlines():
        # Japanese and mixed lyric lines are broken at character boundaries;
        # pure Latin remains word-wrapped without deleting any token.
        words=para.split(' ') if all(ord(c)<128 for c in para)else list(para)
        sep=' 'if all(ord(c)<128 for c in para)else '';line=''
        for word in words:
            candidate=line+sep+word if line else word
            if width(candidate)>limit and line:lines.append(line);line=word
            else:line=candidate
        lines.append(line)
    if len(lines)>2 or any(width(s)>limit for s in lines):raise ValueError('Native lyric exceeds complete two-line field')
    return '\n'.join(lines)

def patch_ending(data,d,jp):
    if digest(data)!=BASE_SHA:raise ValueError('Complete0.2.18 baseline changed')
    e=Elf(data);out=bytearray(data);cues=d['ending']['cues'];code=native.code(len(cues));widths=json.loads((ROOT/'work/output/v0.2.18/build_info.json').read_text('utf8'))['font_widths']
    if e.at(native.BASE,native.LIMIT-native.BASE)!=bytes(native.LIMIT-native.BASE):raise ValueError('Ending helper allocation occupied')
    for start,end in POOLS[1:]:
        if e.at(start,end-start)!=bytes(end-start):raise ValueError('Ending lyric pool occupied')
    pos=[start for start,end in POOLS];unique={};alloc=[]
    def store(text,size):
        text=wrap_native(text,size,widths);b=text.encode('cp932')+b'\0'
        if b in unique:return unique[b]
        for i,(start,end)in enumerate(POOLS):
            if pos[i]+len(b)<=end:
                va=pos[i];pos[i]+=len(b);out[e.offset(va):e.offset(va)+len(b)]=b;unique[b]=va;alloc.append(dict(va=hex(va),size=len(b),sha256=digest(b),font_size=size));return va
        raise ValueError('Ending lyric pools exhausted; no source-size squeezing allowed')
    table=bytearray()
    for c in cues:
        table+=struct.pack('<5I',round(c['start']*48000),round(c['end']*48000),store(jp['cues'][c['id']],22),store(c['romaji'],17),store(c['en'],20))
    out[e.offset(native.BASE):e.offset(native.BASE)+len(code)]=code;out[e.offset(native.TABLE):e.offset(native.TABLE)+len(table)]=table
    if e.at(native.HOOK,8)!=pack([jr('ra'),addiu('sp','sp',0x70)]):raise ValueError('PCM server return guard changed')
    out[e.offset(native.HOOK):e.offset(native.HOOK)+4]=pack([j(native.BASE)])
    return bytes(out),dict(code_va=hex(native.BASE),code_size=len(code),code_sha256=digest(code),table_va=hex(native.TABLE),table_size=len(table),table_sha256=digest(table),hook_va=hex(native.HOOK),hook_old=hex(jr('ra')),hook_new=hex(j(native.BASE)),allocations=alloc,pools=[dict(start=hex(s),end=hex(t),used=pos[i]-s)for i,(s,t)in enumerate(POOLS)],clock='Native ADXT_GetTimeSfreq2 decoded samples minus output queue at48000Hz; active STREAM member0 only; avoid zero-time PS2RNA stub',windows='Two flat native windows; Japanese22/romaji17 top and English20 bottom; hide in gaps, delete when stream ends or changes')

def inputs():
    d,jp,guard=language();data,packs,overlays,report=prior.inputs();data,n=patch_ending(data,d,jp)
    return data,packs,overlays,dict(**report,movie_subtitles=dict(**guard,native_ending=n,members=[m['member']for m in d['movies']],held_members=d['held_movie_members']))

def movie_bytes(m):
    d=ROOT/'work/movie_captions_0.2.19_safe'/f'{m["member"]:05d}';meta=json.loads((d/'encode.json').read_text('utf8'));video=(d/'captioned.ipu').read_bytes()
    if meta.get('ipu_intra_vlc_format')!=1 or not video[16]&0x20:raise ValueError('Native-compatible intra VLC format1 required')
    if meta.get('frame_byte_limit')!=30000 or max(map(len,movie_pss.frames(video)))>30000:raise ValueError('Native picture refill limit required')
    if digest(video)!=meta['video_sha256']:raise ValueError('Encoded movie changed')
    original=next(r for r in records(ISO)if r['path']=='/MOVIE.AFS')
    with ISO.open('rb')as f:
        ent=index(f,original['lba']*2048,original['size'])[m['member']];f.seek(original['lba']*2048+ent['offset']);source=f.read(ent['size'])
    if digest(source)!=m['source_movie_sha256']:raise ValueError('Source movie changed')
    return movie_pss.remux_video(source,video),dict(**meta,source_movie_sha256=digest(source),original_adx_sha256=digest(movie_pss.streams(source)[1]),pss_mux='Picture/sample-time interleave; video prefetch0.5s, audio0.25s; original member extent; ADX payload exact, PES packaging rebuilt')

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('version');ap.add_argument('--write',action='store_true');a=ap.parse_args()
    if a.version!='0.2.19':raise ValueError('This guarded movie package is0.2.19')
    data,packs,overlays,report=inputs();d,_,_=language();movies={};movie_report=[]
    for m in d['movies']:
        b,r=movie_bytes(m);movies[m['member']]=b;movie_report.append(dict(**r,patched_movie_sha256=digest(b)))
    ending=report['movie_subtitles']['native_ending']
    print(json.dumps(dict(version=a.version,elf_sha256=digest(data),movies=[r['member']for r in movie_report],native_ending={k:ending[k]for k in('code_va','code_size','table_va','table_size','hook_va','hook_old','hook_new','pools','clock','windows')},ending_samples=d['ending']['cues'][:2]),indent=1))
    if not a.write:print('DRY no ELF, movie archive or ISO written.');return
    dest=ROOT/'work/output/v0.2.19';dest.mkdir(exist_ok=False);(dest/'SLPS_250.70').write_bytes(data)
    for i,b in packs.items():(dest/f'{i:05d}.pack').write_bytes(b)
    for i,b in overlays.items():(dest/f'{i:05d}.evemap').write_bytes(b)
    image=dest/'Sunrise Eiyuutan 2 EN v0.2.19.iso';make_iso(image,data,packs,overlays)
    record=next(r for r in records(image)if r['path']=='/MOVIE.AFS')
    with image.open('r+b')as f:
        ents=index(f,record['lba']*2048,record['size'])
        for i,b in movies.items():
            if len(b)!=ents[i]['size']:raise ValueError('Movie member extent changed')
            f.seek(record['lba']*2048+ents[i]['offset']);f.write(b)
    info=json.loads((ROOT/'work/output/v0.2.18/build_info.json').read_text('utf8'));info.update(version=a.version,based_on='0.2.18',**report,elf_sha256=digest(data),iso_path=str(image),iso_size=image.stat().st_size,movie_encoding=movie_report,in_game_validation='pending movie and ending playback',scope='Movie/preview titles, Whisper-derived voice captions, OP/ED lyrics and romaji; original voices retained.')
    for key in('iso_sha256','native_validation_report','information_validation'):info.pop(key,None)
    (dest/'build_info.json').write_text(json.dumps(info,indent=1)+'\n','utf8');print('WRITE',image)

if __name__=='__main__':main()
