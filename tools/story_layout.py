"""Three-line native dialogue measurements; no insertion approval implied.

Keep every existing native call boundary. Reflow only the language within a
single call, leaving its original header, voice, function and ending LFs intact.
Unfitted pages fail; this module never truncates language or changes voice cues.
"""
import re
from functools import lru_cache
from textcodec import TOKEN,controls,control_size,decode,encode
from message_pages import pages

WIDTH=504
LINES=3
# winGTMakeDrawPacketPromptFrameWINDOW (original ELF 0x110A48) draws
# the triangle through cursor_x+26, independent of the last glyph's width.
PROMPT_RIGHT=26
FINAL_WIDTH=WIDTH-PROMPT_RIGHT
PROFILES={'story':(0,3,4),'battle-tutorial':(0,4,6),'battle-barks':(),'travel-notice':(0,1)}


def measure(text,widths,profile='story'):
    if profile not in PROFILES:raise ValueError('Unknown native dialogue profile')
    color_controls=tuple('{C:81978283%02X00}'%v for v in PROFILES[profile])
    value=0;pos=0
    for m in TOKEN.finditer(text):
        value+=sum((widths[127] if ch=='ū' else widths[ord(ch)] if ord(ch)<128 else 26)+2 for ch in text[pos:m.start()])
        token=m.group().upper()
        if token=='{C:819782960000}':value+=224
        elif token not in color_controls:
            raise ValueError('Unprofiled story body control '+m.group())
        pos=m.end()
    return value+sum((widths[127] if ch=='ū' else widths[ord(ch)] if ord(ch)<128 else 26)+2 for ch in text[pos:])


def wrap_body(text,widths,profile='story'):
    if '\n' in text:raise ValueError('Pass one unwrapped meaning-first body')
    out=[];line=''
    for word in text.split(' '):
        if not word:continue
        if measure(word,widths,profile)>WIDTH:raise ValueError('Unbreakable story token exceeds width')
        candidate=line+' '+word if line else word
        if line and measure(candidate,widths,profile)>WIDTH:out.append(line);line=word
        else:line=candidate
    if line:out.append(line)
    if out and measure(out[-1],widths,profile)>FINAL_WIDTH:
        # Only pages whose original greedy layout crowds the prompt change.
        # Balance the extra line to avoid a lone final word, preserving words,
        # inline commands and their order. Oversized pages still fail in wrap_row.
        words=text.split();count=len(out)+1
        @lru_cache(None)
        def partition(start,remaining):
            if not remaining:return (0,()) if start==len(words) else None
            limit=FINAL_WIDTH if remaining==1 else WIDTH
            best=None
            for end in range(start+1,len(words)-remaining+2):
                candidate=' '.join(words[start:end]);size=measure(candidate,widths,profile)
                if size>limit:break
                tail=partition(end,remaining-1)
                if tail is not None:
                    option=((limit-size)**2+tail[0],(candidate,)+tail[1])
                    if best is None or option[0]<best[0]:best=option
            return best
        balanced=partition(0,count)
        if balanced is None:raise ValueError('Unbreakable final token leaves no native prompt margin')
        out=list(balanced[1])
    result='\n'.join(out)
    if controls(result)!=controls(text) or result.split()!=text.split():raise ValueError('Story wrapping changed language or controls')
    return result


def pieces(raw,page):
    original=raw[page['start']:page['end']];pos=0
    while original[pos:pos+2] in (b'\x81\x90',b'\x81\x93',b'\x81\x95'):
        n=control_size(original,pos,True)
        if not n:raise ValueError('Unprofiled story header')
        pos+=n
    end=len(original.rstrip(b'\n'))
    return original[:pos],decode(original[pos:end]),original[end:]


def wrap_row(text,widths,require_fit=True,centered_calls=(),profile='story'):
    raw=encode(text);out=bytearray();report=[];before=pages(raw)
    for i,page in enumerate(before):
        if not page['flags']&1:out+=raw[page['start']:page['end']];continue
        prefix,body,tail=pieces(raw,page)
        # Meaning drafts retain source LFs. Reflow inside this single original
        # bark body only; never join separate native calls or change ending LFs.
        if profile=='battle-barks':body=' '.join(body.split('\n'))
        wrapped=wrap_body(body,widths,profile);lines=wrapped.split('\n')
        if i in centered_calls:
            if len(lines)!=1:raise ValueError('Tutorial heading needs a separate multiline profile')
            padding=(WIDTH-measure(wrapped,widths,profile))//(2*(widths[32]+2))
            wrapped=' '*padding+wrapped;lines=[wrapped]
        maxline=max(map(lambda line:measure(line,widths,profile),lines),default=0)
        final=measure(lines[-1],widths,profile) if lines else 0
        report.append(dict(native_call=i,lines=len(lines),max_line_px=maxline,final_line_px=final,prompt_right_px=final+PROMPT_RIGHT,body_bytes=len(encode(wrapped)),voice=page['voice'],centered=i in centered_calls))
        if final>FINAL_WIDTH:raise ValueError('Native continuation prompt exceeds body width')
        if require_fit and (len(lines)>LINES or len(encode(wrapped))>=400):raise ValueError(f'Story native call{i} needs {len(lines)} lines; complete wording retained for pagination work')
        out+=prefix+encode(wrapped)+tail
    out+=b'\0';result=decode(bytes(out));after=pages(bytes(out))
    if len(before)!=len(after) or controls(result)!=controls(text):raise ValueError('Native story boundary/control count changed')
    for a,b in zip(before,after):
        if {k:v for k,v in a.items() if k not in ('start','end','body')}!={k:v for k,v in b.items() if k not in ('start','end','body')}:
            raise ValueError('Native staging data changed')
    return result,report
