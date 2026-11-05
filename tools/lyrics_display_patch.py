"""v0.2.23: display romaji and English, without the Japanese lyric tier."""
import argparse,json,hashlib
from elf import ROOT,Elf
from iso import ISO,records
from afs import index
from build import make_iso
import battle_effects_patch as prior
import movie_patch as movies
import movie_subtitles as captions
import movie_lyrics_native as native
import movie_pss

BASE_SHA='f7be29aba99ed3bbb9c494b3032e4eab5a722cdbd913c699cf4f06f76606530d'
RAW=ROOT/'work/movie_captions_0.2.23_ivf1'
SAFE=ROOT/'work/movie_captions_0.2.23_safe_r1'
digest=movies.digest

def opening():
 d,jp,_=movies.language()
 m=next(m for m in d['movies']if m['member']==488)
 return m,captions.movie_ass(m,jp['cues'],include_japanese=False)

def patch(data):
 if digest(data)!=BASE_SHA:raise ValueError('Complete0.2.22 baseline changed')
 d,_,_=movies.language();e=Elf(data);old=native.code(len(d['ending']['cues']));new=native.code(len(d['ending']['cues']),include_japanese=False)
 if e.at(native.BASE,len(old))!=old:raise ValueError('Ending helper revision changed')
 if len(new)>len(old):raise ValueError('Replacement exceeds existing helper')
 out=bytearray(data);out[e.offset(native.BASE):e.offset(native.BASE)+len(old)]=new+bytes(len(old)-len(new))
 return bytes(out),dict(display_languages=['romaji','English'],japanese_lyric_tier=False,opening_cues=21,ending_cues=34,wording_and_timing_unchanged=True,code_va=hex(native.BASE),previous_code_size=len(old),code_size=len(new),code_sha256=digest(new),table_sha256=digest(e.at(native.TABLE,34*20)),ending_top_window=dict(y=8,height=48,font_size=17),english_bottom_unchanged=True)

def inputs():
 data,packs,overlays,report=prior.inputs();data,display=patch(data)
 subtitles=dict(report['movie_subtitles']);subtitles['native_ending']=dict(subtitles['native_ending'],code_size=display['code_size'],code_sha256=display['code_sha256'],windows='Two flat windows: romaji17 top y8/height48; English20 bottom unchanged; Japanese tier omitted; original cue table, gaps and cleanup retained.')
 return data,packs,overlays,dict(report,movie_subtitles=subtitles,lyrics_display=display)

def movie_bytes(m):
 if m['member']!=488:return movies.movie_bytes(m)
 _,ass=opening();folder=SAFE/'00488';meta=json.loads((folder/'encode.json').read_text('utf8'));video=(folder/'captioned.ipu').read_bytes()
 if (folder/'captions.ass').read_text('utf-8-sig')!=ass or meta['ass_sha256']!=digest((folder/'captions.ass').read_bytes()):raise ValueError('Two-tier caption revision changed')
 frames=movie_pss.frames(video)
 if digest(video)!=meta['video_sha256']or meta['frame_byte_limit']!=30000 or max(map(len,frames))>30000:raise ValueError('Capped movie guard failed')
 if len(frames)!=m['frames']or not all(p[0]&0x20 for p in frames):raise ValueError('Native picture format changed')
 rec=next(r for r in records(ISO)if r['path']=='/MOVIE.AFS')
 with ISO.open('rb')as f:
  entry=index(f,rec['lba']*2048,rec['size'])[488];f.seek(rec['lba']*2048+entry['offset']);source=f.read(entry['size'])
 if digest(source)!=m['source_movie_sha256']:raise ValueError('Original opening changed')
 return movie_pss.remux_video(source,video),dict(**meta,original_adx_sha256=digest(movie_pss.streams(source)[1]))

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--encode',action='store_true');ap.add_argument('--write',action='store_true');a=ap.parse_args();m,ass=opening()
 print(json.dumps(dict(version='0.2.23',display=['romaji','English'],opening_ass_events=ass.count('Dialogue:'),sample=[s for s in ass.splitlines()if 'Tamashii' in s],lyrics_language_sha256=movies.LANGUAGE_SHA,mode='encode'if a.encode else'build'),indent=1),flush=True)
 if a.encode:
  if not a.write:print('DRY: encode original opening into a new folder; preserve55 lyric cue texts/times.');return
  dest=RAW/'00488';dest.mkdir(parents=True,exist_ok=False);r=captions.encode(m,ass,dest);(dest/'encode.json').write_text(json.dumps(r,indent=1)+'\n','utf8');print('ENCODED',json.dumps(r),flush=True);return
 data,packs,overlays,report=inputs();body,media=movie_bytes(m)
 print(json.dumps(dict(elf_sha256=digest(data),ending=report['lyrics_display'],opening=media,retained_packs=len(packs),retained_overlays=len(overlays)),indent=1),flush=True)
 if not a.write:print('DRY: no game files or ISO written.');return
 dest=ROOT/'work/output/v0.2.23';dest.mkdir(exist_ok=False);(dest/'SLPS_250.70').write_bytes(data)
 for i,b in packs.items():(dest/f'{i:05d}.pack').write_bytes(b)
 for i,b in overlays.items():(dest/f'{i:05d}.evemap').write_bytes(b)
 image=dest/'Sunrise Eiyuutan 2 EN v0.2.23.iso';make_iso(image,data,packs,overlays)
 previous=ROOT/'work/output/v0.2.22/Sunrise Eiyuutan 2 EN v0.2.22.iso'
 src=next(r for r in records(previous)if r['path']=='/MOVIE.AFS');dst=next(r for r in records(image)if r['path']=='/MOVIE.AFS')
 if src['size']!=dst['size']:raise ValueError('Movie archive extent changed')
 with previous.open('rb')as f,image.open('r+b')as g:
  f.seek(src['lba']*2048);g.seek(dst['lba']*2048);left=src['size']
  while left:
   block=f.read(min(left,4*1024*1024))
   if not block:raise ValueError('Truncated baseline archive')
   g.write(block);left-=len(block)
  entry=index(g,dst['lba']*2048,dst['size'])[488]
  if len(body)!=entry['size']:raise ValueError('Opening extent changed')
  g.seek(dst['lba']*2048+entry['offset']);g.write(body)
 info=json.loads((ROOT/'work/output/v0.2.22/build_info.json').read_text('utf8'));info.update(version='0.2.23',based_on='0.2.22',**report,elf_sha256=digest(data),iso_path=str(image),iso_size=image.stat().st_size,lyrics_opening_encoding=media,in_game_validation='pending two-tier lyric playback',scope='Remove Japanese lyric tier from opening/ending; keep romaji, English, exact cue text/timing, original audio and complete0.2.22.')
 info['movie_encoding']=[dict(r,**media,patched_movie_sha256=digest(body))if r['member']==488 else r for r in info['movie_encoding']]
 for key in('iso_sha256','native_validation_report','movie_archive_retained'):info.pop(key,None)
 (dest/'build_info.json').write_text(json.dumps(info,indent=1)+'\n','utf8');print('WRITE',image)

if __name__=='__main__':main()
