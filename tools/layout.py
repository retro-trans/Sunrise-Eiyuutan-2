"""Word wrapping using the patched font's advances, including runtime names."""
import re
from textcodec import TOKEN,controls

# EVEMAP member 00007 at 0x9E00C8 passes 8 to nameEvEntryName.
# nameStdAddSjis stores two-byte characters; each may occupy 26+2 pixels.
RUNTIME_WIDTH={'{C:819782960000}':8*28}
FONT_SELECTORS={'{C:2332}':26,'{C:2335}':13}


def measure(text,widths,spacing=2,initial_mode=2):
    if initial_mode not in (2,5):raise ValueError('Unprofiled font height')
    n=0;pos=0;mode=initial_mode
    def literal(s):
        full=26 if mode==2 else 13
        return sum((widths[ord(ch)]*full//26 if ord(ch)<128 else full)+spacing for ch in s)
    for m in TOKEN.finditer(text):
        n+=literal(text[pos:m.start()]);token=m.group().upper()
        if token in FONT_SELECTORS:mode=2 if token=='{C:2332}' else 5
        elif token in RUNTIME_WIDTH:n+=8*((26 if mode==2 else 13)+spacing)
        elif token.startswith('{C:23'):raise ValueError('Unprofiled renderer selector')
        elif token!='{X00}':raise ValueError('Unprofiled layout control '+m.group())
        pos=m.end()
    n+=literal(text[pos:]);return n,mode


def width(text,widths,spacing=2,initial_mode=2):
    return measure(text,widths,spacing,initial_mode)[0]


def line_widths(text,widths):
    mode=2;result=[]
    for line in text.split('\n'):
        n,mode=measure(line,widths,initial_mode=mode);result.append(n)
    return result


def wrap(text,widths,max_width=504):
    out=[];mode=2
    for paragraph in text.split('\n'):
        words=paragraph.split(' ');line='';line_mode=mode
        for word in words:
            if not word:continue
            current_mode=measure(line,widths,initial_mode=line_mode)[1]
            if width(word,widths,initial_mode=current_mode)>max_width:raise ValueError('Unbreakable token exceeds display width')
            candidate=line+' '+word if line else word
            if line and width(candidate,widths,initial_mode=line_mode)>max_width:
                out.append(line);line=word;line_mode=current_mode
            else:line=candidate
        out.append(line);mode=measure(line,widths,initial_mode=line_mode)[1]
    result='\n'.join(out)
    if controls(text)!=controls(result):raise ValueError('Wrapping damaged controls')
    return result
