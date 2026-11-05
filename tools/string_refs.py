"""MIPS string-address uses with branch delay slots and saved-register calls.

Find reaching LUI definitions through native instruction predecessors. Calls
preserve the ABI saved registers, including fp. A low instruction in one arm
cannot borrow a LUI from another arm that jumps past it.
"""
import struct
from collections import defaultdict
from text_refs import writes,signed

SAVED={*range(16,24),28,29,30}

def code_refs(blob,base,targets,entries=(),indirect=None):
    ws=list(struct.unpack('<%dI'%(len(blob)//4),blob[:len(blob)//4*4]));end=base+len(ws)*4
    pred=defaultdict(list);nodes=defaultdict(list)
    def edge(a,z,clobber=False):
        if base<=z[0]<end:pred[z].append((a,clobber))
    for i,w in enumerate(ws):
        pc=base+i*4;normal=(pc,);nodes[pc].append(normal);op=w>>26;rs=w>>21&31;rt=w>>16&31;fn=w&63
        branch=op in (1,4,5,6,7,20,21,22,23) or (op in (0x10,0x11,0x12) and rs==8)
        call=op==3 or (op==0 and fn==9)
        if branch or op in (2,3) or (op==0 and fn in (8,9)):
            dest=pc+4+signed(w&65535)*4 if branch else ((pc+4)&0xf0000000)|((w&0x3ffffff)<<2)
            possibilities=[(pc+8,True)] if call else [(dest,False),(pc+8,False)] if branch else [(dest,False)] if op==2 else []
            if op==0 and fn==8 and indirect and pc in indirect:possibilities=[(x,False) for x in indirect[pc]]
            for n,(target,clobber) in enumerate(possibilities):
                # Pseudo-instruction b is beq zero,zero: its fallthrough arm
                # is unreachable and must not leak a delay-slot definition.
                if branch and rs==rt and op in (4,20) and n==1:continue
                if branch and rs==rt and op in (5,21) and n==0:continue
                if branch and rs==0 and op in (6,22) and n==1:continue
                if branch and rs==0 and op in (7,23) and n==0:continue
                likely=op in (20,21,22,23) or (op in (0x10,0x11,0x12) and rs==8 and rt&2)
                if branch and likely and n==1:edge(normal,(pc+8,));continue
                delay=(pc+4,pc,target,n);nodes[pc+4].append(delay);edge(normal,delay);edge(delay,(target,),clobber)
        else:edge(normal,(pc+4,))
    successors=defaultdict(list)
    for z,ps in pred.items():
        for a,_ in ps:successors[a].append(z)
    reachable=set();queue=[(a,) for a in (base,*entries) if base<=a<end]
    while queue:
        node=queue.pop()
        if node in reachable:continue
        reachable.add(node);queue.extend(successors[node])
    low={x&65535 for x in targets};result=[]
    for i,w in enumerate(ws):
        op=w>>26;rs=w>>21&31;rt=w>>16&31
        if op not in (9,13,0x20,0x21,0x23,0x24,0x25,0x37) or not rs or w&65535 not in low:continue
        site=base+i*4;definitions=set()
        for node in set(nodes[site]):
            if node not in reachable:continue
            queue=[node];seen=set()
            while queue:
                cur=queue.pop()
                if cur in seen:continue
                seen.add(cur)
                for prev,clobber in pred[cur]:
                    if prev not in reachable:continue
                    if clobber and rs not in SAVED:continue
                    p=ws[(prev[0]-base)//4]
                    if rs in writes(p):
                        if p>>26==15 and p>>16&31==rs:definitions.add((prev[0],p))
                    else:queue.append(prev)
        # An instruction that can form another high/low address on a different
        # arm needs a separate consumer rewrite, never an ambiguous low edit.
        found=[];other=[]
        for lui,p in definitions:
            target=(p&65535)*65536+(w&65535 if op==13 else signed(w&65535))
            if target in targets:found.append(dict(site=site,lui=lui,target=target,register=rt,base_register=rs,lui_word=p,word=w))
            else:other.append(target)
        if found and other:raise ValueError('Ambiguous native address use at%08X: %s'%(site,other))
        result.extend(found)
    return sorted(result,key=lambda x:(x['site'],x['lui']))
