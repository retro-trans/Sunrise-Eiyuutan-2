"""Read-only model of native GetMessagePage for profiled control records.

Offsets are raw byte positions, including blank/control-only native calls.
This does not execute function/voice records or grant a display profile.
"""
import struct


def parse_page(raw, start=0):
    pos=start; body=bytearray(); column=0; flags=0; speaker=0; voice=0; parameter=0
    function=0; arguments=[]

    def take(n):
        nonlocal pos
        if pos+n>len(raw):raise ValueError('Truncated message record')
        b=raw[pos:pos+n];pos+=n;return b

    def sjis():
        if pos>=len(raw):raise ValueError('Missing message terminator')
        c=raw[pos]
        return take(2 if 0x81<=c<=0x9f or 0xe0<=c<=0xfc else 1)

    def u16():return struct.unpack('<H',take(2))[0]
    def u32():return struct.unpack('<I',take(4))[0]

    while pos<len(raw) and raw[pos]:
        ch=sjis()
        if not column:
            if ch in (b'\x81\x90',b'\x81\x93'):
                speaker=u16();flags|=0x20 if ch==b'\x81\x90' else 0x10;continue
            if ch==b'\x81\x95':
                sub=sjis()
                if sub==b'\x82\x96':voice=u32();parameter=u16();flags|=0x40;continue
                if sub==b'\x82\x86':
                    function=u16();count=u16()
                    if count>4:raise ValueError('Native context has only four function argument slots')
                    arguments=[u32() for _ in range(count)];flags|=0x80;continue
                raise ValueError('Unprofiled header subtype '+sub.hex())
            if ch==b'\n':break
        if ch==b'\x81\x97':
            sub=sjis();value=u16()
            prefixes={b'\x82\x93':b'#',b'\x82\x97':b'|',b'\x82\x83':b'%',b'\x82\x96':b'@'}
            if sub not in prefixes or value>9:raise ValueError('Unprofiled native formatting record')
            body+=prefixes[sub]+bytes([value+48])
            if sub==b'\x82\x96':column+=2
        elif ch==b'\x81\x8f':
            ch=sjis();body+=ch;column+=2
        else:
            body+=ch;column=0 if ch==b'\n' else column+len(ch)
    if pos>=len(raw):raise ValueError('Missing message terminator')
    if body:flags|=1
    return dict(start=start,end=pos,flags=flags,speaker=speaker,voice=voice,
                voice_parameter=parameter,function=function,arguments=arguments,body=bytes(body))


def pages(raw):
    result=[];pos=0
    while pos<len(raw) and raw[pos]:
        page=parse_page(raw,pos)
        if page['end']<=pos:raise ValueError('Parser did not advance')
        result.append(page);pos=page['end']
    if pos!=len(raw)-1 or raw[pos:]!=b'\0':raise ValueError('Unexpected bytes after message terminator')
    return result
