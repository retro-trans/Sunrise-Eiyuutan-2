"""Export the original opening with current romaji/English captions to MP4."""
import argparse,json,hashlib,subprocess,math,shutil
from pathlib import Path
from elf import ROOT
from iso import ISO,records
from afs import index
import movie_pss,movie_subtitles,lyrics_display_patch

DEST=ROOT/'work/output/opening-mp4'
WORK=ROOT/'work/media_export/opening-mp4'
NAME='Sunrise Eiyuutan 2 - Opening - Romaji and English.mp4'
sha=lambda data:hashlib.sha256(data).hexdigest()

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--write',action='store_true')
    args=ap.parse_args()
    movie,ass=lyrics_display_patch.opening()
    source=movie_subtitles.SOURCE/'00488.ipu'
    if sha(source.read_bytes())!=movie['source_video_sha256']:
        raise ValueError('Original opening video changed')
    current=ROOT/'work/movie_captions_0.2.23_safe_r1/00488/captions.ass'
    if current.read_text('utf-8-sig')!=ass or ass.count('Dialogue:')!=42:
        raise ValueError('Current two-tier opening captions changed')
    rec=next(r for r in records(ISO)if r['path']=='/MOVIE.AFS')
    with ISO.open('rb')as f:
        entry=index(f,rec['lba']*2048,rec['size'])[488]
        f.seek(rec['lba']*2048+entry['offset'])
        original=f.read(entry['size'])
    if sha(original)!=movie['source_movie_sha256']:
        raise ValueError('Original opening movie changed')
    video,audio=movie_pss.streams(original)
    if sha(video)!=movie['source_video_sha256']:
        raise ValueError('Original video stream mismatch')
    rate=int.from_bytes(audio[8:12],'big')
    samples=int.from_bytes(audio[12:16],'big')
    seconds=samples/rate
    frames=movie['frames']
    output_frames=max(frames,math.ceil(seconds*30))
    pad=output_frames-frames
    command=['ffmpeg','-hide_banner','-loglevel','warning','-n','-r','30','-i',str(source),'-i',str(WORK/'original.adx'),'-map','0:v:0','-map','1:a:0','-vf',f'ass=captions.ass,tpad=stop_mode=clone:stop={pad},setsar=1','-c:v','libx264','-preset','slow','-crf','16','-pix_fmt','yuv420p','-r','30','-c:a','aac','-b:a','320k','-ar','48000','-ac','2','-movflags','+faststart','-metadata','title=Sunrise Eiyuutan 2 - Opening (Romaji and English)',str(DEST/NAME)]
    report=dict(source_movie_sha256=sha(original),source_video_sha256=sha(video),source_audio_sha256=sha(audio),captions_sha256=sha(current.read_bytes()),source_frames=frames,output_frames=output_frames,held_final_frames=pad,resolution=[movie['width'],movie['height']],fps=30,audio_seconds=seconds,subtitle_languages=['romaji','English'],video_codec='H.264',audio_codec='AAC 320kbps stereo 48kHz',output=str(DEST/NAME),command=command)
    print(json.dumps(report,indent=1),flush=True)
    if not args.write:
        print('DRY no files written. Final picture held for the original audio tail; all source frames and song audio retained.')
        return
    if DEST.exists()or WORK.exists():
        raise FileExistsError('Preserve existing export and evidence')
    DEST.mkdir(parents=True)
    WORK.mkdir(parents=True)
    (WORK/'original.adx').write_bytes(audio)
    shutil.copyfile(current,WORK/'captions.ass')
    result=subprocess.run(command,cwd=WORK,capture_output=True,text=True)
    (WORK/'encode.log').write_text(result.stderr,'utf8')
    if result.returncode:
        raise RuntimeError(result.stderr)
    probe=subprocess.run(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(DEST/NAME)],capture_output=True,text=True,check=True)
    metadata=json.loads(probe.stdout)
    v=next(s for s in metadata['streams']if s['codec_type']=='video')
    a=next(s for s in metadata['streams']if s['codec_type']=='audio')
    if v['codec_name']!='h264'or a['codec_name']!='aac'or int(v['nb_read_frames'])!=output_frames or v['avg_frame_rate']!='30/1'or(v['width'],v['height'])!=(640,384)or a['channels']!=2:
        raise ValueError('Export stream verification failed')
    check=subprocess.run(['ffmpeg','-hide_banner','-v','error','-i',str(DEST/NAME),'-f','null','-'],capture_output=True,text=True)
    if check.returncode or check.stderr.strip():
        raise ValueError('MP4 decode failed: '+check.stderr)
    report.update(mp4_sha256=sha((DEST/NAME).read_bytes()),bytes=(DEST/NAME).stat().st_size,probe=metadata,full_decode='passed',source_decoder_stderr=result.stderr)
    (DEST/'export.json').write_text(json.dumps(report,indent=1)+'\n','utf8')
    (DEST/(NAME+'.sha256')).write_text(report['mp4_sha256']+'  '+NAME+'\n','ascii')
    print('EXPORTED',str(DEST/NAME),flush=True)

if __name__=='__main__':
    main()
