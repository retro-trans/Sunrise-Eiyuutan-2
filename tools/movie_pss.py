"""Bounded PS2 PSS tools with exact ADX audio and fixed member extents.

The native-safe delivery uses picture-limited, time-interleaved remux_video.
replace_video retains the earlier byte-slot experiment for diagnosis only.
"""
import struct,bisect,re

def packets(data):
    p=0
    while p+4<=len(data):
        if data[p:p+3]!=b'\0\0\1':raise ValueError('Bad PSS packet prefix at %x'%p)
        kind=data[p+3]
        if kind==0xB9:
            yield p,p+4,kind,None,None
            return
        end=p+14+(data[p+13]&7) if kind==0xBA else p+6+int.from_bytes(data[p+4:p+6],'big')
        if end>len(data):raise ValueError('PSS packet overruns member')
        sub=body=None
        if kind==0xBD:
            if data[p+6]&0xC0!=0x80:raise ValueError('Unsupported PES header')
            body=p+9+data[p+8]
            while body<end and data[body]==0xFF:body+=1
            if body+3>end:raise ValueError('Short private PES subheader')
            sub=data[body];body+=3
        yield p,end,kind,sub,body
        p=end

def streams(data):
    video=[];audio=[]
    for p,end,kind,sub,body in packets(data):
        if sub==0xC0:video.append(data[body:end])
        elif sub==0x90:audio.append(data[body:end])
    return b''.join(video),b''.join(audio)

def ipu_header(data):
    h=struct.unpack_from('<4sIHHI',data)
    if h[0]!=b'ipum' or h[1]+8!=len(data):raise ValueError('IPU declared length mismatch')
    return h

def normalize_encoder_length(data):
    """IPUenc f91537e writes total size; this game's header excludes eight bytes."""
    magic,length,w,h,n=struct.unpack_from('<4sIHHI',data)
    if magic!=b'ipum' or length!=len(data):raise ValueError('Unexpected IPUenc header convention')
    out=bytearray(data);struct.pack_into('<I',out,4,len(out)-8)
    ipu_header(out)
    return bytes(out)

def replace_video(source,video):
    old,audio=streams(source)
    if ipu_header(old)[2:]!=ipu_header(video)[2:]:raise ValueError('Movie dimensions/frame count changed')
    if len(video)>len(old):raise ValueError('New IPU exceeds original private-video capacity')
    out=bytearray(source);pos=0
    for start,end,kind,sub,body in packets(source):
        if sub!=0xC0:continue
        capacity=end-body;take=min(capacity,len(video)-pos)
        if not take:
            out[start:end]=b'\0\0\1\xBE'+(end-start-6).to_bytes(2,'big')+b'\xFF'*(end-start-6)
            continue
        spare=capacity-take;header=bytearray(source[start:body])
        if 0<spare<6:
            # Optional PES header stuffing absorbs fewer than six spare bytes.
            n=header[8]
            if n+spare>255:raise ValueError('PES stuffing length overflow')
            header[8]+=spare;header[9+n:9+n]=b'\xFF'*spare;spare=0
        total=len(header)+take;header[4:6]=(total-6).to_bytes(2,'big')
        new=header+video[pos:pos+take];pos+=take
        if spare:new+=b'\0\0\1\xBE'+(spare-6).to_bytes(2,'big')+b'\xFF'*(spare-6)
        if len(new)!=end-start:raise ValueError('Replacement packet extent changed')
        out[start:end]=new
    result=bytes(out)
    if pos!=len(video) or len(result)!=len(source):raise ValueError('Video replacement incomplete')
    new_video,new_audio=streams(result)
    if new_video!=video or new_audio!=audio:raise ValueError('Exact video/audio round trip failed')
    # Every non-video original packet and its byte offset remain untouched.
    for start,end,kind,sub,body in packets(source):
        if sub!=0xC0 and result[start:end]!=source[start:end]:raise ValueError('Non-video packet changed')
    return result

def frames(video):
    """Independent raster IPU pictures, including their original B0 delimiters."""
    _,_,_,_,count=ipu_header(video)
    ends=[m.end()for m in re.finditer(b'\x00\x00\x01\xb0',video)]
    if len(ends)!=count or video[ends[-1]:]!=b'\0\0\1\xb1':raise ValueError('IPU picture boundaries/end marker mismatch')
    starts=[16]+ends[:-1]
    return [video[a:z]for a,z in zip(starts,ends)]

def remux_video(source,video):
    """Interleave by picture/sample time, preserving exact ADX and member extent.

    Merely pouring a changed video into the old byte slots loses the original
    temporal interleave. Native audio backpressure can then starve IDEC. Limit
    each picture to one native32KiB chunk and prefetch video/audio by0.5/0.25s.
    Keep all frame payloads and ADX bytes exact; only PSS packaging is rebuilt.
    """
    old,audio=streams(source);pics=frames(video)
    if ipu_header(old)[2:]!=ipu_header(video)[2:]:raise ValueError('Movie dimensions/frame count changed')
    if max(map(len,pics))>30000:raise ValueError('Captioned picture exceeds native refill limit')
    if (len(source)-4)%16384:raise ValueError('Unexpected source PSS pack extent')
    h=audio;data_start=int.from_bytes(h[2:4],'big')+4;block=h[5];channels=h[7];rate=int.from_bytes(h[8:12],'big')
    if h[:2]!=b'\x80\x00' or h[4]!=3 or h[6]!=4 or not(block and channels and rate):raise ValueError('Unsupported ADX layout')
    ends=[];n=16
    for pic in pics:n+=len(pic);ends.append(n)
    items=[]
    for p in range(0,len(video),4073):
        frame=min(len(pics)-1,bisect.bisect_right(ends,p))
        items.append((frame/30-.5,0xC0,frame/30,video[p:p+4073]))
    for p in range(0,len(audio),4073):
        t=max(0,p-data_start)/(block*channels)*32/rate
        items.append((t-.25,0x90,t,audio[p:p+4073]))
    items.sort(key=lambda x:(x[0],x[1]!=0xC0))
    source_packets=list(packets(source));packs=[source[a:z]for a,z,k,_,_ in source_packets if k==0xBA]
    if any(len(p)!=14 for p in packs):raise ValueError('Unexpected MPEG pack header')
    system=next(source[a:z]for a,z,k,_,_ in source_packets if k==0xBB)
    out=bytearray();pack=bytearray(packs[0]+system);pack_index=0
    def pad(n):
        if n<6:raise ValueError('Short PSS padding')
        return b'\0\0\1\xBE'+(n-6).to_bytes(2,'big')+b'\xff'*(n-6)
    def flush():
        nonlocal pack,pack_index
        if len(pack)<16384:pack+=pad(16384-len(pack))
        out.extend(pack);pack_index+=1
        pack=bytearray(packs[pack_index])if pack_index<len(packs)else bytearray()
    def pts(t):
        v=max(0,round(t*90000))&((1<<33)-1)
        return bytes([0x21|((v>>29)&14),(v>>22)&255,((v>>14)&254)|1,(v>>7)&255,((v<<1)&254)|1])
    for _,sub,t,payload in items:
        while payload:
            if pack_index>=len(packs):raise ValueError('Remux exceeds original pack capacity')
            space=16384-len(pack)
            if space<29:flush();space=16384-len(pack)
            take=min(4073,space-23,len(payload));spare=space-23-take
            if 0<spare<6:take-=6-spare
            body=payload[:take];payload=payload[take:]
            head=b'\0\0\1\xBD'+(17+len(body)).to_bytes(2,'big')+b'\x83\x80\x0a'+pts(t)+b'\xff'*6+bytes([sub,0,0])
            if len(head)!=23:raise ValueError('Private PSS header length')
            pack+=head+body
            if len(pack)==16384:flush()
    if len(pack)>14:flush()
    while pack_index<len(packs):
        out.extend(packs[pack_index]+pad(16370));pack_index+=1
    out+=b'\0\0\1\xb9';result=bytes(out)
    if len(result)!=len(source)or streams(result)!=(video,audio):raise ValueError('Exact remux video/audio/extent round trip failed')
    return result
