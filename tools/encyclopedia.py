"""Bounded native encyclopedia pagination for SLPS-25070.

The row stays intact in ATMB. Native control decoding runs once; decoded text,
including native runtime-value commands, is copied to reserved storage. Pages use the original
display/illustration/input/cleanup routine. Only library tables are intercepted.
"""
import struct,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent/'dbg'))
from mips import *

ORIGINAL=0x13FFA0
ORIGINAL_SIZE=0x228
BASE=CLONE=0x9AA000
WRAPPER=0x9AA300
GET_PAGE=0x9AA800
FOOT_NEXT=0x9AA840
FOOT_CLOSE=0x9AA880
MAIL=0x9AA900
GET_MESSAGE=0x9AAA00
FULL=0x9AB000
FULL_SIZE=0x4000
PAGE=0x9AF000
PAGE_SIZE=0x2000
CONTEXT=PAGE+PAGE_SIZE
CONTEXT_SIZE=0x4100
END=CONTEXT+CONTEXT_SIZE
LINES=9
MAGIC=0x32474150 # PAG2
NEXT=b'^0,252,Circle: Next page\0'
CLOSE=b'^0,252,Circle: Close\0'


def font_mode(raw,initial=2):
    """Read renderer font state without mistaking a CP932 trail for ASCII."""
    mode=initial;i=0
    while i<len(raw):
        c=raw[i]
        if c==0x23:
            if i+1>=len(raw) or raw[i+1] not in (0x32,0x35):raise ValueError('Unprofiled native font directive')
            mode=raw[i+1]-0x30;i+=2
        else:i+=2 if 0x81<=c<=0x9f or 0xe0<=c<=0xfc else 1
    return mode


def source_page_body(body,start_mode,end_mode):
    """Remove only identified synthetic page-state directives, retaining source ones."""
    if start_mode not in (2,5) or end_mode not in (2,5):raise ValueError('Unprofiled page font state')
    if start_mode!=2:
        prefix=b'#'+bytes([start_mode+0x30])
        if not body.startswith(prefix):raise ValueError('Missing carried page font')
        body=body[2:]
    if end_mode!=2:
        if not body.endswith(b'#2'):raise ValueError('Footer did not restore normal font')
        body=body[:-2]
    if font_mode(body,start_mode)!=end_mode:raise ValueError('Source/font-state mismatch')
    return body

def native_clone(elf):
    raw=bytearray(elf.at(ORIGINAL,ORIGINAL_SIZE))
    if raw[0x34:0x38]!=pack([jal(0x12CA18)]):raise ValueError('Unexpected encyclopedia message lookup')
    # Relative branches retain their displacement only if their targets move
    # with the copied routine. Absolute internal calls/jumps need relocation.
    for off in range(0,len(raw),4):
        word=struct.unpack_from('<I',raw,off)[0];op=word>>26;pc=ORIGINAL+off
        if op in (2,3):
            target=((pc+4)&0xf0000000)|((word&0x3ffffff)<<2)
            if ORIGINAL<=target<ORIGINAL+ORIGINAL_SIZE:
                struct.pack_into('<I',raw,off,(op<<26)|(((CLONE+target-ORIGINAL)>>2)&0x3ffffff))
        elif op in (1,4,5,6,7,20,21,22,23) or (op==17 and (word>>21)&31==8):
            imm=word&65535;imm=imm-65536 if imm&32768 else imm
            target=pc+4+imm*4
            if not ORIGINAL<=target<ORIGINAL+ORIGINAL_SIZE:
                raise ValueError('External relative branch in native encyclopedia routine')
    raw[0x34:0x38]=pack([jal(GET_PAGE)])
    return raw

def get_page_code():
    a=Asm(GET_PAGE);a(la('v0',MAIL),lw('v0',4,'v0'))
    a.br('beqz','v0','original');a(NOP)
    a(la('v0',PAGE),jr('ra'),NOP)
    a.label('original');a(j(0x12CA18),NOP);return a.assemble()

def get_message_code(elf):
    # The original context at 0x515C70 has only 400 bytes of text before
    # _mesvalA (0x515E28). A long English description must never decode there.
    # Preserve native lookup/decoding, replacing only this routine's context.
    symbol=elf.symbol('mesGetMessageLabel')
    if symbol['va']!=0x12CA18 or symbol['size']!=0x6C:raise ValueError('Unexpected message lookup layout')
    raw=bytearray(elf.at(symbol['va'],symbol['size']))
    for off,old,new in ((0x18,lui('s1',0x51),lui('s1',hi(CONTEXT))),
                        (0x28,addiu('s0','s1',0x5C70),addiu('s0','s1',lo(CONTEXT))),
                        (0x38,lw('v1',0x5C70,'s1'),lw('v1',lo(CONTEXT),'s1'))):
        if raw[off:off+4]!=pack([old]):raise ValueError('Unexpected native message context reference')
        raw[off:off+4]=pack([new])
    return raw

def wrapper_code():
    a=Asm(WRAPPER)
    a(addiu('at','zero',10515));a.br('beq','a2','at','library');a(NOP)
    a(addiu('at','zero',10516));a.br('beq','a2','at','library');a(NOP)
    a(j(CLONE),NOP)
    a.label('library');a(addiu('sp','sp',-0x90),sd('ra',0x80,'sp'))
    for i in range(8):a(sd('s'+str(i),i*16,'sp'))
    a(move('s2','a0'),move('s3','a1'),move('s4','a2'),move('s5','a3'),
      la('t0',MAIL),addiu('t1','zero',1),sw('t1',4,'t0'),sw('zero',8,'t0'),
      sw('zero',12,'t0'),sw('s4',16,'t0'),sw('s5',20,'t0'),sw('zero',24,'t0'),
      move('a0','s4'),jal(GET_MESSAGE),move('a1','s5'))
    a(move('t0','v0'),la('t1',FULL),addiu('t2','zero',FULL_SIZE-1),move('t4','zero'))
    a.label('full_copy');a.br('beqz','t2','full_error');a(NOP)
    a(lbu('t3',0,'t0'),sb('t3',0,'t1'))
    a.br('beqz','t3','full_done');a(NOP)
    a(addiu('t0','t0',1),addiu('t1','t1',1),addiu('t4','t4',1))
    a.br('b','full_copy');a(addiu('t2','t2',-1))
    a.label('full_done');a(la('t0',MAIL),sw('t4',28,'t0'),la('s0',FULL),addiu('t2','zero',0x32),sw('t2',0x88,'sp'))
    a.label('page');a(la('s1',PAGE),addiu('s7','zero',LINES),la('t1',PAGE+PAGE_SIZE-64))
    # Each native display call starts afresh. Reapply a carried font mode;
    # footer-only resets below must not change the saved source-text mode.
    a(lw('t2',0x88,'sp'),la('t4',MAIL),sw('t2',36,'t4'),addiu('at','zero',0x32))
    a.br('beq','t2','at','body_copy');a(addiu('t0','zero',0x23))
    a(sb('t0',0,'s1'),sb('t2',1,'s1'),addiu('s1','s1',2))
    a.label('body_copy');a(lbu('t0',0,'s0'))
    a.br('beqz','t0','body_done');a(NOP)
    a(sltu('at','s1','t1'));a.br('beqz','at','page_error');a(NOP)
    a(sb('t0',0,'s1'),addiu('s0','s0',1),addiu('s1','s1',1),addiu('at','zero',10))
    a.br('beq','t0','at','newline');a(addiu('at','zero',0x23))
    a.br('bne','t0','at','body_copy');a(NOP)
    a(lbu('t2',0,'s0'))
    a.br('b','body_copy');a(sw('t2',0x88,'sp'))
    a.label('newline')
    a(addiu('s7','s7',-1));a.br('bnez','s7','body_copy');a(NOP)
    a.label('body_done');a(move('s6','s0'),lw('t2',0x88,'sp'),la('t4',MAIL),sw('t2',32,'t4'))
    a.label('trailing');a(lbu('t0',0,'s6'))
    a.br('beqz','t0','last');a(addiu('at','zero',10))
    a.br('bne','t0','at','more');a(NOP)
    a.br('b','trailing');a(addiu('s6','s6',1))
    a.label('last');a(move('s0','s6'),la('t0',FOOT_CLOSE),move('t3','zero'))
    a.br('b','footer');a(NOP)
    a.label('more');a(la('t0',FOOT_NEXT),addiu('t3','zero',1))
    a.label('footer');a(lw('t2',0x88,'sp'),addiu('at','zero',0x32))
    a.br('beq','t2','at','footer_copy');a(addiu('t2','zero',0x23))
    a(sb('t2',0,'s1'),addiu('t2','zero',0x32),sb('t2',1,'s1'),addiu('s1','s1',2))
    a.label('footer_copy');a(lbu('t2',0,'t0'),sb('t2',0,'s1'))
    a.br('beqz','t2','display');a(NOP)
    a(addiu('t0','t0',1));a.br('b','footer_copy');a(addiu('s1','s1',1))
    a.label('display');a(la('t0',MAIL),lw('t1',8,'t0'),addiu('t1','t1',1),sw('t1',8,'t0'),sw('t3',12,'t0'),
      move('a0','s2'),move('a1','s3'),move('a2','s4'),jal(CLONE),move('a3','s5'),lbu('v0',0,'s0'))
    a.br('bnez','v0','page');a(NOP)
    a.br('b','done');a(NOP)
    a.label('full_error');a(addiu('v0','zero',1));a.br('b','error');a(NOP)
    a.label('page_error');a(addiu('v0','zero',2))
    a.label('error');a(la('t0',MAIL),sw('v0',24,'t0'))
    a.label('done');a(la('t0',MAIL),sw('zero',4,'t0'),ld('ra',0x80,'sp'))
    for i in range(8):a(ld('s'+str(i),i*16,'sp'))
    a(jr('ra'),addiu('sp','sp',0x90))
    return a.assemble()

def payload(elf):
    out=bytearray(END-BASE)
    for va,data in ((CLONE,native_clone(elf)),(WRAPPER,wrapper_code()),(GET_PAGE,get_page_code()),(GET_MESSAGE,get_message_code(elf)),
                    (FOOT_NEXT,NEXT),(FOOT_CLOSE,CLOSE),(MAIL,struct.pack('<10I',MAGIC,0,0,0,0,0,0,0,0,0))):
        off=va-BASE
        if off<0 or off+len(data)>len(out):raise ValueError('Pagination region overflow')
        out[off:off+len(data)]=data
    if WRAPPER+len(wrapper_code())>GET_PAGE:raise ValueError('Pagination code overlaps helper')
    if GET_PAGE+len(get_page_code())>FOOT_NEXT:raise ValueError('Page getter overlaps footer')
    if GET_MESSAGE+len(get_message_code(elf))>FULL:raise ValueError('Message lookup overlaps full-text buffer')
    return out

def patches(elf):
    old=pack([addiu('sp','sp',-0x70),sd('s1',0x10,'sp')])
    if elf.at(ORIGINAL,len(old))!=old:raise ValueError('Unexpected encyclopedia entry bytes')
    return [(ORIGINAL,old,pack([j(WRAPPER),NOP]),'encyclopedia pagination')]
