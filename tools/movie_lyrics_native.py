"""Ending lyric windows driven by the original ADX sample clock.

This module only assembles bounded code/data. The movie builder supplies reviewed
cue pointers and checks the complete previous ELF and every target gap.
"""
from mips import *

BASE=0x9A4200
STATE=BASE+0x600
TABLE=STATE+0x40
LIMIT=0x9A5000
PCM=0x5B764C
HOOK=0x154E58

def code(count,include_japanese=True):
    a=Asm(BASE)
    a(addiu('sp','sp',-0x80),sd('ra',0x70,'sp'),sd('v0',0x60,'sp'))
    for i,r in enumerate(('s0','s1','s2','s3')):a(sd(r,0x20+i*16,'sp'))
    a(la('s0',STATE),la('s1',PCM),lw('t0',0,'s1'),andi('t0','t0',1))
    a.br('beqz','t0','close');a(lhu('t0',4,'s1'))
    a(addiu('t1','zero',5));a.br('bne','t0','t1','close');a(lhu('t0',6,'s1'))
    a(addiu('t1','zero',1));a.br('bne','t0','t1','close');a(lw('a0',16,'s1'))
    a(jal(0x186FB0),NOP,addiu('t0','zero',3))
    a.br('bne','v0','t0','close');a(lw('a0',16,'s1'))
    # GetTimeSfreq routes to a zero-time PS2RNA stub in this game. Its native
    # Sfreq2 variant subtracts queued output from decoded samples instead.
    a(addiu('a1','sp',0),addiu('a2','sp',4),jal(0x1870A8),NOP)
    a(lw('t0',4,'sp'),ori('t1','zero',48000))
    a.br('bne','t0','t1','close');a(lw('s3',0,'sp'))
    a(la('s1',TABLE),addiu('s2','zero',1),addiu('t3','zero',count+1))
    a.label('find');a(lw('t0',0,'s1'),sltu('t1','s3','t0'))
    a.br('bnez','t1','blank');a(lw('t0',4,'s1'))
    a(sltu('t1','s3','t0'));a.br('bnez','t1','found');a(NOP)
    a(addiu('s1','s1',20),addiu('s2','s2',1))
    a.br('bne','s2','t3','find');a(NOP)
    a.label('blank');a(move('s2','zero'))
    a.label('found');a(lw('t0',8,'s0'))
    a.br('beq','t0','s2','return');a(NOP)
    a(sw('s2',8,'s0'));a.br('beqz','s2','hide');a(lw('s3',0,'s0'))
    a.br('bnez','s3','draw');a(NOP)
    # Two flat native lyric windows. Normal game font and VWF are reused.
    for off,y,h in ((0,8,104 if include_japanese else 48),(4,376,64)):
        a(lui('a0',0x3000),addiu('a1','zero',1),addiu('a2','zero',0x200),addiu('a3','zero',0x121),addiu('t0','zero',16),addiu('t1','zero',y),addiu('t2','zero',608),addiu('t3','zero',h),jal(0x1112F8),NOP,sw('v0',off,'s0'))
    a(lw('s3',0,'s0'))
    a.label('draw')
    for off in (0,4):
        a(lw('a0',off,'s0'),lw('t0',8,'a0'),lui('t1',0x7fff),ori('t1','t1',0xffff),and_('t0','t0','t1'),sw('t0',8,'a0'),jal(0x1523A0),move('a1','zero'))
    # Text is prepared as complete lines with measured line wrapping.
    draws=((0,8,0,22),(0,12,52,17),(4,16,0,20)) if include_japanese else ((0,12,0,17),(4,16,0,20))
    for win,ptr,y,size in draws:
        a(lw('a0',win,'s0'),lw('a1',ptr,'s1'),addiu('a2','zero',4),addiu('a3','zero',y),addiu('t0','zero',size),addiu('t1','zero',size),jal(0x110EA0),move('t2','zero'))
    a.br('b','return');a(NOP)
    a.label('hide')
    for off in (0,4):
        lab='hidden'+str(off);a(lw('a0',off,'s0'));a.br('beqz','a0',lab);a(NOP)
        a(lw('t0',8,'a0'),lui('t1',0x8000),or_('t0','t0','t1'),sw('t0',8,'a0'));a.label(lab)
    a.br('b','return');a(NOP)
    a.label('close')
    for off in (0,4):
        lab='closed'+str(off);a(lw('a0',off,'s0'));a.br('beqz','a0',lab);a(NOP)
        a(jal(0x10EF50),NOP,sw('zero',off,'s0'));a.label(lab)
    a(sw('zero',8,'s0'))
    a.label('return')
    for i,r in enumerate(('s0','s1','s2','s3')):a(ld(r,0x20+i*16,'sp'))
    a(ld('v0',0x60,'sp'),ld('ra',0x70,'sp'),jr('ra'),addiu('sp','sp',0x80))
    b=a.assemble()
    if len(b)>STATE-BASE:raise ValueError('Ending helper exceeds code allocation')
    if TABLE+count*20>LIMIT:raise ValueError('Ending cue table exceeds allocation')
    return b
