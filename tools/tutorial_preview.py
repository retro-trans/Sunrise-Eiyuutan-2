"""Fresh-build, single-use overrides for the two unseen tutorial records.

Only explicit file/member/source-row requests through the original event bridge
are intercepted. Native lookup, parsing, portraits, voices, windows and cleanup
remain in charge. This does not establish the original conditional triggers.
"""
import struct,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent/'dbg'))
from mips import *
import encyclopedia

HOOK=0x9A1708
NATIVE=0x12C940
BASE=0x9B6000
MAIL=BASE+0x200
END=MAIL+0x40
MAGIC=0x3150534D # MSP1
FILE=4950
MEMBER=10472
PROFILES={'missing':((0,1),(2,33)),'row1':((0,1),),'row33':((0,33),)}
PROFILE_IDS={'missing':1,'row1':2,'row33':3}
EXPECTED=bytes.fromhex('50b2040800000000')


def validate(elf,profile):
    if profile not in PROFILES:raise ValueError('Unsupported tutorial preview profile')
    start=elf.symbol('_evefunc_start')['va'];size=elf.symbol('_evefunc_size')['va']
    if start!=0x9A0000 or size!=0x20000 or elf.symbol('_evescen_start')['va']!=start+size:
        raise ValueError('Unexpected event-function reservation')
    if BASE<encyclopedia.END or END>start+size:raise ValueError('Tutorial preview overlaps reserved data')
    for typ,off,addr,pa,fs,ms,flags,al in elf.segments:
        if typ==1 and addr==start:
            if addr+max(fs,ms)>BASE:raise ValueError('Tutorial preview overlaps original event code')
        elif typ==1 and max(BASE,addr)<min(END,addr+ms):raise ValueError('Tutorial preview segment collision')
    for s in elf.symbols:
        if s['section'] not in (0,0xfff1) and s['size'] and max(BASE,s['va'])<min(END,s['va']+s['size']):
            raise ValueError('Tutorial preview overlaps original symbol')
    if elf.at(HOOK,8)!=EXPECTED or elf.symbol('mesSpeakMessageFileLabel')['va']!=NATIVE:
        raise ValueError('Unexpected event message bridge')
    if elf.at(NATIVE,8)!=bytes.fromhex('c0ffbd272000b2ff'):raise ValueError('Unexpected native message entry')


def code(profile):
    if profile not in PROFILES:raise ValueError('Unsupported tutorial preview profile')
    a=Asm(BASE)
    a(addiu('t0','zero',FILE));a.br('bne','a0','t0','original');a(NOP)
    a(addiu('t0','zero',MEMBER));a.br('bne','a1','t0','original');a(NOP)
    a(la('t0',MAIL),lw('t1',0,'t0'),la('t2',MAGIC))
    a.br('bne','t1','t2','original');a(NOP)
    a(lw('t1',4,'t0'),addiu('t2','zero',PROFILE_IDS[profile]))
    a.br('bne','t1','t2','original');a(NOP)
    a(lw('t1',8,'t0'),sltiu('t2','t1',1<<len(PROFILES[profile])))
    a.br('beqz','t2','original');a(NOP)
    for i,(source,target) in enumerate(PROFILES[profile]):
        a(addiu('t2','zero',source));a.br('beq','a2','t2','request'+str(i));a(NOP)
    a.label('original');a(j(NATIVE),NOP)
    for i,(source,target) in enumerate(PROFILES[profile]):
        a.label('request'+str(i));a(andi('t2','t1',1<<i));a.br('bnez','t2','original');a(NOP)
        a(ori('t1','t1',1<<i),sw('t1',8,'t0'),lw('t1',12,'t0'),addiu('t1','t1',1),sw('t1',12,'t0'),
          sw('a0',16,'t0'),sw('a1',20,'t0'),sw('a2',24,'t0'),addiu('t2','zero',target),sw('t2',28,'t0'),
          sw('a2',32+i*16,'t0'),sw('t2',36+i*16,'t0'),sw('ra',40+i*16,'t0'),sw('t1',44+i*16,'t0'),
          addiu('a2','zero',target),j(NATIVE),NOP)
    out=a.assemble()
    if BASE+len(out)>MAIL:raise ValueError('Tutorial preview code overlaps telemetry')
    return out


def payload(elf,profile):
    validate(elf,profile);out=bytearray(END-BASE);body=code(profile);out[:len(body)]=body
    struct.pack_into('<16I',out,MAIL-BASE,MAGIC,PROFILE_IDS[profile],0,0,*([0]*12))
    return out


def patches(elf,profile):
    validate(elf,profile)
    return [(HOOK,EXPECTED,pack([j(BASE),NOP]),'debug/tutorial preview '+profile)]


def telemetry(raw,profile):
    if profile not in PROFILES or len(raw)!=64:raise ValueError('Invalid tutorial preview telemetry')
    w=struct.unpack('<16I',raw);requests=PROFILES[profile]
    if w[:2]!=(MAGIC,PROFILE_IDS[profile]) or w[2]>=1<<len(requests) or w[3]!=w[2].bit_count():
        raise ValueError('Corrupt tutorial preview telemetry')
    records=[]
    for i,(source,target) in enumerate(requests):
        if w[2]&(1<<i):
            record=w[8+i*4:12+i*4]
            if record[:2]!=(source,target):raise ValueError('Unexpected tutorial preview record')
            records.append(dict(source_row=source,target_row=target,return_address=hex(record[2]),sequence=record[3]))
    if records and (w[4:6]!=(FILE,MEMBER) or sorted(r['sequence'] for r in records)!=list(range(1,len(records)+1))):
        raise ValueError('Unexpected tutorial preview request provenance')
    return dict(profile=profile,hit_mask=w[2],redirects=w[3],last_file=w[4],last_member=w[5],last_source_row=w[6],last_target_row=w[7],records=records,
                scope='Forced exact-request preview; original conditional reachability is unverified.')
