"""Read-only physical resource provenance from a same-build EE snapshot.

A table-byte match alone cannot distinguish duplicate tables. The live resource
registry links its resource ID to a member header and packet descriptor. Require
that link, the entire expected packet header, member bytes and native lookup code.
"""
import argparse,hashlib,json,struct,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from elf import ROOT,Elf
from extract import pack_members
from sstate import State

HEAD=0x23D870
END=0x23D880
LOOKUP=((0x10C3A8,68),(0x10C538,48))


def origin(ee,elf,pack,table,table_base):
    """Return a proved expected destination, or None when it is not registered."""
    def take(a,n):
        if type(a) is not int or a<=0 or n<0 or a+n>len(ee):raise ValueError('Resource pointer outside EE memory')
        return ee[a:a+n]
    def words(a,n):return struct.unpack('<%dI'%n,take(a,n*4))
    for va,n in LOOKUP:
        if take(va,n)!=elf.at(va,n):raise ValueError('Resource lookup code differs from selected build')
    pn,mid=map(int,table.split('_'));members=pack_members(pack)
    member=next(m for m in members if m['id']==mid)
    count=struct.unpack_from('<I',pack)[0];header=pack[:4+16*count]
    expected=pack[member['offset']:member['offset']+member['size']]
    ptr=words(HEAD+4,1)[0];seen=set();matches=[]
    while ptr!=END:
        if ptr in seen or len(seen)>=4096:raise ValueError('Invalid or cyclic resource registry')
        seen.add(ptr);previous,nxt,head,descriptor=words(ptr,4)
        rid,off,size,flags=words(head,4)
        if rid==mid:
            packet_base=words(descriptor+12,1)[0]
            if packet_base+off==table_base and size==len(expected):
                if take(packet_base,len(header))!=header:raise ValueError('Live packet header differs from expected physical pack')
                index=(head-packet_base-4)//16
                if head!=packet_base+4+16*index or not 0<=index<count:
                    raise ValueError('Registered member header is outside expected packet header')
                if take(head,16)!=pack[4+index*16:20+index*16] or take(table_base,size)!=expected:
                    raise ValueError('Registered resource member differs from expected physical destination')
                matches.append(dict(table=table,pack=pn,member=mid,registry_node=hex(ptr),member_header=hex(head),packet_descriptor=hex(descriptor),packet_base=hex(packet_base),table_base=hex(table_base),header_bytes=len(header),header_sha256=hashlib.sha256(header).hexdigest(),member_sha256=hashlib.sha256(expected).hexdigest(),scope='Registered resource ID, packet/member header and exact current member bytes; no branch/trigger or display approval.'))
        ptr=nxt
    if len(matches)>1:raise ValueError('Multiple matching physical resource registrations')
    if matches:matches[0]['registry_nodes_checked']=len(seen)
    return matches[0] if matches else None


def inspect_origin(state,version,table,base):
    folder=ROOT/f'work/output/v{version}';pn=int(table.split('_')[0]);path=folder/f'{pn:05d}.pack'
    pack=path.read_bytes() if path.exists() else (ROOT/f'work/source/afs/RESOURCE/{pn:05d}.bin').read_bytes()
    return origin(State(state).ee(),Elf((folder/'SLPS_250.70').read_bytes()),pack,table,base)


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('version');ap.add_argument('state');ap.add_argument('--table',required=True);ap.add_argument('--table-base',required=True,type=lambda s:int(s,0));a=ap.parse_args()
    print(json.dumps(inspect_origin(a.state,a.version,a.table,a.table_base),indent=1))
