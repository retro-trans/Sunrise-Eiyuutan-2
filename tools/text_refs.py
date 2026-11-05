"""Bounded MIPS/static-pointer references to explicit reviewed string addresses.

This does not scan arbitrary byte substrings or replace address-like literals.
Each immediate reference requires the closest register definition to be a LUI.
"""
import struct


def signed(n):return n-65536 if n&32768 else n


def writes(word):
    op=word>>26;rt=(word>>16)&31;rd=(word>>11)&31
    if not op:
        fn=word&63
        return {rd} if fn not in (8,12,13,0x11,0x13,0x19,0x1A,0x1B) and rd else set()
    if op==3:return {31}
    if op in (1,2,4,5,6,7,20,21,22,23,0x1F,0x28,0x29,0x2A,0x2B,0x2C,0x2D,0x2E,0x2F,0x39,0x3F):return set()
    if op in (0x10,0x11,0x12,0x13):return {rt} if ((word>>21)&31) in (0,1,2) else set()
    if op==0x1C:return {rd} if rd else set()
    return {rt} if rt else set()


def code_refs(blob,base,targets,weak=False,include_memory=False):
    words=list(struct.unpack('<%dI'%(len(blob)//4),blob[:len(blob)//4*4]));result=[]
    low={x&65535 for x in targets}
    for i,w in enumerate(words):
        op=w>>26;rs=(w>>21)&31;rt=(w>>16)&31
        eligible=(9,13)+tuple(range(0x20,0x40)) if include_memory else (9,13)
        if op not in eligible or not rs or w&65535 not in low:continue
        for j in range(i-1,max(-1,i-97),-1):
            prev=words[j]
            # A call's delay slot executes before caller-saved values clobber.
            if not weak and prev>>26==3 and j!=i-1 and rs not in range(16,24) and rs!=28:break
            if rs not in writes(prev):continue
            if prev>>26==15 and (prev>>16)&31==rs:
                target=((prev&65535)<<16)+(signed(w&65535) if op==9 else w&65535)
                if target in targets:
                    result.append(dict(site=base+i*4,lui=base+j*4,target=target,register=rt,base_register=rs,
                                       lui_word=prev,word=w,adjacent=j==i-1))
            if not weak or prev>>26==15:break
    return result


def pointer_refs(blob,base,targets):
    return [dict(site=base+i,target=v) for i in range(0,len(blob)-3,4)
            if (v:=struct.unpack_from('<I',blob,i)[0]) in targets]
