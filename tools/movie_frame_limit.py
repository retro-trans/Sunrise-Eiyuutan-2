"""Keep captioned IPU pictures within the stock one-chunk refill envelope.

I-only pictures are independent. Reuse the best admitted whole-movie encode;
replace only oversized pictures with the first higher quantizer that fits.
Full text, timing, dimensions and picture count are unchanged.
"""
import argparse,json,subprocess,struct,shutil,collections
from pathlib import Path
import movie_subtitles as c,movie_pss as p

LIMIT=30000
def main():
 a=argparse.ArgumentParser(description=__doc__);a.add_argument('--write',action='store_true');a.add_argument('--members');a.add_argument('--source-dir',type=Path);a.add_argument('--output-dir',type=Path);args=a.parse_args()
 lang=json.loads(c.LANGUAGE.read_text('utf8'));movies=lang['movies'];old=(args.source_dir or c.ROOT/'work/movie_captions_0.2.19_ivf1').resolve();parent=(args.output_dir or c.ROOT/'work/movie_captions_0.2.19_safe').resolve()
 if args.members:ids={int(x)for x in args.members.split(',')};movies=[m for m in movies if m['member']in ids]
 for m in movies:
  v=(old/('%05d'%m['member'])/'captioned.ipu').read_bytes();parts=p.frames(v);print('PLAN',m['member'],'oversized',sum(len(x)>LIMIT for x in parts),'/',len(parts),'max',max(map(len,parts)),'->',LIMIT,flush=True)
 if not args.write:print('DRY no media written');return
 parent.mkdir(exist_ok=True)
 for m in movies:
  i=m['member'];base=old/('%05d'%i);dest=parent/('%05d'%i);dest.mkdir(exist_ok=False);meta=json.loads((base/'encode.json').read_text());shutil.copyfile(base/'captions.ass',dest/'captions.ass');video=(base/'captioned.ipu').read_bytes();parts=p.frames(video);chosen=[meta['quantizer']]*len(parts)
  for q in range(meta['quantizer']+2,32,2):
   bad=[n for n,x in enumerate(parts)if len(x)>LIMIT]
   if not bad:break
   mpeg=dest/('q%d.m2v'%q);ipu=dest/('q%d.ipu'%q)
   cmd=['ffmpeg','-hide_banner','-loglevel','error','-n','-r','30','-i',str(c.SOURCE/('%05d.ipu'%i)),'-vf','ass=captions.ass','-an','-c:v','mpeg2video','-intra_vlc','1','-g','1','-bf','0','-q:v',str(q),'-pix_fmt','yuv420p','-r','30',str(mpeg)]
   r=subprocess.run(cmd,cwd=dest,capture_output=True,text=True);assert r.returncode==0,r.stderr
   r=subprocess.run(['dotnet',str(c.ENCODER),'-encode','-mode1',str(mpeg),str(ipu)],capture_output=True,text=True);assert r.returncode==0,r.stderr
   trial=p.frames(p.normalize_encoder_length(ipu.read_bytes()));assert len(trial)==len(parts)
   for n in bad:
    if len(trial[n])<=LIMIT:parts[n]=trial[n];chosen[n]=q
  if any(len(x)>LIMIT for x in parts):raise ValueError('Unresolved oversized picture')
  out=bytearray(video[:16]+b''.join(parts)+b'\0\0\1\xb1');struct.pack_into('<I',out,4,len(out)-8);assert p.ipu_header(out)[2:]==p.ipu_header(video)[2:]
  assert len(out)<=len(video);assert all(x[0]&0x20 for x in parts)
  (dest/'captioned.ipu').write_bytes(out);meta.update(video_sha256=c.sha(out),encoded_video_bytes=len(out),base_video_sha256=c.sha(video),max_frame_bytes=max(map(len,parts)),frame_byte_limit=LIMIT,frame_quantizers=dict(sorted(collections.Counter(chosen).items())),pictures_requantized=sum(q!=meta['quantizer']for q in chosen))
  (dest/'encode.json').write_text(json.dumps(meta,indent=1)+'\n');print('LIMITED',i,meta['max_frame_bytes'],meta['frame_quantizers'],flush=True)

if __name__=='__main__':main()
