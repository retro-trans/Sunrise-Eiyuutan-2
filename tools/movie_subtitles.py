"""Prepare complete timed captions and encode PS2 IPU movies.

No media is touched on a dry run. Original ADX remains byte-for-byte intact.
The language manifest is English-only; Japanese song text stays in ignored
local source files. The native ending overlay uses the same reviewed cue IDs.
"""
import argparse,json,hashlib,subprocess,struct,re,sys
from pathlib import Path
from PIL import ImageFont
from elf import ROOT
import movie_pss

LANGUAGE=ROOT/'work/translation/en/movies.en.json'
JAPANESE=ROOT/'work/source/movie_lyrics_jp.json'
FONT=Path('C:/Windows/Fonts/arial.ttf')
FONT_BOLD=Path('C:/Windows/Fonts/arialbd.ttf')
ENCODER=Path('C:/Users/Binh/Documents/Codex/2026-10-31/referenced-chatgpt-conversation-this-is-an/work/IPUenc861/IPUenc.dll')
SOURCE=Path('C:/Users/Binh/Documents/Codex/2026-10-31/referenced-chatgpt-conversation-this-is-an/work/movie729')
sha=lambda b:hashlib.sha256(b).hexdigest()

def stamp(t):
    c=round(t*100);return f'{c//360000}:{c//6000%60:02d}:{c//100%60:02d}.{c%100:02d}'

def wrap(text,size,width,bold=False):
    font=ImageFont.truetype(str(FONT_BOLD if bold else FONT),size)
    lines=[]
    for para in text.splitlines():
        line=''
        for word in para.split():
            q=(line+' '+word).strip()
            if font.getlength(q)>width and line:lines.append(line);line=word
            else:line=q
        if line:lines.append(line)
    if any(font.getlength(s)>width for s in lines):raise ValueError('Unbreakable caption word exceeds width')
    return lines

def ass_header(w,h):
    return f'''[Script Info]
ScriptType: v4.00+
PlayResX: {w}
PlayResY: {h}
WrapStyle: 2
ScaledBorderAndShadow: yes
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Voice,Arial,22,&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,1.8,0,2,16,16,14,1
Style: Title,Arial,40,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,0,0,5,0,0,0,1
Style: Lyric,Meiryo,20,&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,1.5,0,8,12,12,10,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''

def event(start,end,style,text,layer=1):
    if not 0<=start<end:raise ValueError('Invalid subtitle interval')
    return f'Dialogue: {layer},{stamp(start)},{stamp(end)},{style},,0,0,0,,{text}\n'

def escape(s):return s.replace('\\','\\\\').replace('{','\\{').replace('}','\\}').replace('\n','\\N')

def cover(rect,start,end):
    x0,y0,x1,y1=rect
    return event(start,end,'Title',f'{{\\an7\\pos(0,0)\\p1\\c&H000000&}}m {x0} {y0} l {x1} {y0} {x1} {y1} {x0} {y1}',0)

def caption_box(text,rect,start,end,size=40):
    x0,y0,x1,y1=rect;size=min(size,40)
    while ImageFont.truetype(str(FONT_BOLD),size).getlength(text)>608 and size>18:size-=1
    return event(start,end,'Title',f'{{\\an5\\pos({(x0+x1)//2},{(y0+y1)//2})\\fs{size}}}'+escape(text))

def movie_ass(m,lyrics,include_japanese=True):
    w=m['width'];h=m['height'];ass=ass_header(w,h)
    size=22 if w==640 else 16
    for c in m.get('spoken',[]):
        lines=wrap(c['en'],size,w-32)
        if len(lines)>3:raise ValueError('Caption exceeds three complete lines')
        position=r'\an8\pos(320,100)' if any(c['end']>q['first_frame']/30 and c['start']<q['end_frame']/30 for q in m.get('cards',[]))else ''
        ass+=event(c['start'],min(c['end'],m['frames']/30),'Voice',f'{{\\fs{size}{position}}}'+escape('\n'.join(lines)))
    if 'episode_heading'in m:
        c=m['episode_heading']
        ass+=event(c['first_frame']/30,c['end_frame']/30,'Voice',r'{\an5\pos(320,280)\fs26}'+escape(c['en']))
    if 'title'in m:
        c=m['title'];start=(c['first_frame']*100//30)/100;end=(c['end_frame']*100//30)/100
        for field in ('title','heading'):
            if field=='heading' and c['heading']=='NEXT':continue
            rect=c[field+'_rect'];mask=[rect[0]-5,rect[1]-4,rect[2]+5,rect[3]+4]
            ass+=cover(mask,start,end)+caption_box(c['en']if field=='title'else c['heading'],rect,start,end,40 if field=='title'else 32)
    for c in m.get('cards',[]):
        start=(c['first_frame']*100//30)/100;end=(c['end_frame']*100//30)/100
        for q in c['labels']:
            ass+=cover(q['rect'],start,end)+caption_box(q['en'],q['rect'],start,end,q['size'])
    for c in m.get('lyrics',[]):
        jp=lyrics[c['id']];roman='\n'.join(wrap(c['romaji'],16,w-28));en='\n'.join(wrap(c['en'],22,w-32))
        if include_japanese:ass+=event(c['start'],c['end'],'Lyric',r'{\an8\pos(320,10)\fs20}'+escape(jp))
        roman_y=42 if include_japanese else 10
        ass+=event(c['start'],c['end'],'Lyric',f'{{\\an8\\pos(320,{roman_y})\\fnArial\\fs16\\c&H0099FFFF&}}'+escape(roman))
        ass+=event(c['start'],c['end'],'Voice',escape(en))
    return ass

def encode(m,ass,dest):
    """Keep every source frame; choose the least compression fitting source PES capacity."""
    src=SOURCE/f'{m["member"]:05d}.ipu';raw=src.read_bytes()
    if sha(raw)!=m['source_video_sha256']:raise ValueError('Source IPU changed')
    transcript=dest/'captions.ass';transcript.write_text(ass,'utf-8-sig')
    for q in (3,4,5,6):
        mpeg=dest/f'q{q}.m2v';ipu=dest/f'q{q}.ipu'
        command=['ffmpeg','-hide_banner','-loglevel','error','-n','-r','30','-i',str(src),'-vf','ass=captions.ass','-an','-c:v','mpeg2video','-intra_vlc','1','-g','1','-bf','0','-q:v',str(q),'-pix_fmt','yuv420p','-r','30',str(mpeg)]
        p=subprocess.run(command,cwd=dest,capture_output=True,text=True)
        if p.returncode:raise RuntimeError(p.stderr)
        p2=subprocess.run(['dotnet',str(ENCODER),'-encode','-mode1',str(mpeg),str(ipu)],capture_output=True,text=True)
        if p2.returncode:raise RuntimeError(p2.stderr)
        video=movie_pss.normalize_encoder_length(ipu.read_bytes())
        if movie_pss.ipu_header(video)[2:]!=movie_pss.ipu_header(raw)[2:]:raise ValueError('Frame count/dimensions changed during encoding')
        if not video[16]&0x20:raise ValueError('Native-compatible intra VLC format1 required')
        if len(video)<=len(raw):
            output=dest/'captioned.ipu';output.write_bytes(video)
            return dict(member=m['member'],quantizer=q,ipu_intra_vlc_format=1,source_video_bytes=len(raw),encoded_video_bytes=len(video),video_sha256=sha(video),ass_sha256=sha(transcript.read_bytes()),ffmpeg_source_decode_stderr=p.stderr)
    raise ValueError('Captioned video cannot fit original capacity at allowed quality')

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');ap.add_argument('--members');a=ap.parse_args()
    d=json.loads(LANGUAGE.read_text('utf8'));jp=json.loads(JAPANESE.read_text('utf8'));movies=d['movies']
    if a.members:ids={int(v)for v in a.members.split(',')};movies=[m for m in movies if m['member']in ids]
    for m in movies:
        ass=movie_ass(m,jp['cues']);print('PLAN',m['member'],m['width'],m['height'],m['frames'],'frames','ASS lines',ass.count('Dialogue:'))
    if not a.write:print('DRY: no captions or movie files written.');return
    parent=ROOT/'work/movie_captions_0.2.19_ivf1';parent.mkdir(exist_ok=True)
    for m in movies:
        dest=parent/f'{m["member"]:05d}';dest.mkdir(exist_ok=False)
        r=encode(m,movie_ass(m,jp['cues']),dest);(dest/'encode.json').write_text(json.dumps(r,indent=1)+'\n');print('ENCODED',r,flush=True)

if __name__=='__main__':main()
