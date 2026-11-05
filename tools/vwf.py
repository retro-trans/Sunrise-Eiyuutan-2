"""ASCII VWF for SLPS-25070's 26px texture font, including scaled layout paths.

Code uses the unused tail of the statically linked 128 KiB .evefunc reservation.
No RAM location is borrowed from Sunrise R. All hook sites have expected bytes.
"""
from pathlib import Path
import struct
import sys
sys.path.insert(0,str(Path(__file__).parent/'dbg'))
from mips import *
import fontgen

BASE=0x009A4000
TABLE=BASE
SCALE=BASE+0x100
MONITOR=0x009A8000
FONT_PACK=23
FONT_MEMBER=77
ASCII_BASE=0x208D
CELL=26
GLYPH_SIZE=338


def font(data):
    if len(data)!=94*94*GLYPH_SIZE:
        raise ValueError('Unexpected 26px JIS font length')
    out=bytearray(data); widths=bytearray([13]*128);widths[32]=5
    for c,(glyph,width) in fontgen.build_ascii(26).items():
        if not 1<=width<=26:raise ValueError('Glyph overflow')
        start=(ASCII_BASE+c)*GLYPH_SIZE
        out[start:start+GLYPH_SIZE]=glyph
        widths[c]=width
    return bytes(out),bytes(widths)


def scaled_width(code,full,widths):
    return widths[code]*full//26 if 32<=code<127 else full//2 if code<128 else full


def scale_code():
    # a0=character, a1=full (Japanese) cell width. Only v0/v1/at, HI/LO clobbered.
    a=Asm(SCALE)
    a(sltiu('at','a0',128))
    a.br('beqz','at','wide');a(sltiu('at','a0',32))
    a.br('bnez','at','half');a(sltiu('at','a0',127))
    a.br('beqz','at','half');a(lui('v0',hi(TABLE)))
    a(addu('v0','v0','a0'),lbu('v0',lo(TABLE),'v0'),mult3('v0','v0','a1'),
      addiu('v1','zero',26),div('v0','v1'),NOP,NOP,
      jr('ra'),r_type(0,0,'v0',0,0x12)) # mflo v0
    a.label('half');a(jr('ra'),sra('v0','a1',1))
    a.label('wide');a(jr('ra'),move('v0','a1'))
    return a.assemble()


def font_wh():
    # Replacement fits in the existing 0x60-byte function; optional output pointers.
    a=Asm(0x108C40)
    a(sltiu('at','a0',128),addiu('v0','zero',26))
    a.br('beqz','at','store');a(NOP)
    a(lui('v0',hi(TABLE)),addu('v0','v0','a0'),lbu('v0',lo(TABLE),'v0'))
    a.label('store');a.br('beqz','a1','height');a(NOP)
    a(sw('v0',0,'a1'))
    a.label('height');a.br('beqz','a2','return');a(addiu('v0','zero',26))
    a(sw('v0',0,'a2'))
    a.label('return');a(jr('ra'),NOP)
    return a.assemble()


def monitor_code():
    # Called at padMakeGAMEPAD's pressed-bit conversion; its RA was already saved.
    a=Asm(MONITOR+0x100)
    a(nor('v1','v1','v0'),lui('at',hi(MONITOR)),
      lw('v0',lo(MONITOR+4),'at'),or_('v1','v1','v0'),
      lw('v0',lo(MONITOR+8),'at'),addiu('v0','v0',1),sw('v0',lo(MONITOR+8),'at'),
      sh('v1',0,'s0'),
      jr('ra'),sw('v1',lo(MONITOR+12),'at'))
    return a.assemble()


def patches(original):
    """Return appended payload and guarded (VA, old, new, purpose) patch list."""
    from elf import Elf
    elf=Elf(original); payload=bytearray(0x100);payload+=scale_code()
    changes=[]
    def patch(va,new,purpose,expected=None):
        old=elf.at(va,len(new))
        if expected is not None and old!=expected:raise ValueError('Unexpected hook bytes: '+purpose)
        changes.append((va,old,new,purpose))
    def append(code):
        while len(payload)%16:payload.append(0)
        va=BASE+len(payload);payload.extend(code(va));return va
    wh=font_wh();patch(0x108C40,wh,'fontGetWH proportional crop')
    for site,code_reg,size_reg,dest,resume,expected in [
        (0x10E398,'s0','s5','s2',0x10E3B4,pack([lw('v0',12,'sp'),beq('zero','zero',5),sra('s2','v0',1)])),
        (0x10E56C,'a0','s3','s2',0x10E584,pack([beq('zero','zero',5),sra('s2','s5',1)])),
        (0x10E65C,'a0','s4','s1',0x10E674,pack([beq('zero','zero',5),sra('s1','s6',1)]))]:
        def wrapper(va,cr=code_reg,sr=size_reg,dr=dest,rs=resume):
            return pack([move('a0',cr),jal(SCALE),move('a1',sr),j(rs),move(dr,'v0')])
        target=append(wrapper)
        patch(site,pack([j(target),NOP])+bytes(len(expected)-8),'scaled layout at %08X'%site,expected)
    def message_width(va):
        return pack([lbu('a0',0,'s1'),sd('a0',0x30,'s0'),lw('a1',0x38,'s0'),
                     jal(SCALE),NOP,j(0x12C374),sw('v0',0x38,'s0')])
    target=append(message_width)
    patch(0x12C33C,pack([j(target),NOP]),'typewriter advance',pack([lw('v0',0x38,'s0'),lbu('a0',0,'s1')]))
    def message_blit(va):
        return pack([move('t8','a0'),move('t9','a1'),move('t7','ra'),move('a0','a1'),
                     jal(SCALE),move('a1','t0'),move('t0','v0'),move('a0','t8'),
                     move('a1','t9'),move('ra','t7'),j(0x110E90),NOP])
    target=append(message_blit)
    patch(0x12C2DC,pack([jal(target)]),'scaled typewriter glyph',pack([jal(0x110E90)]))
    patch(0x1044B0,pack([jal(MONITOR+0x100),NOP]),'input/frame monitor including store delay slot',
          pack([nor('v1','v1','v0'),sh('v1',0,'s0')]))
    return payload,changes
