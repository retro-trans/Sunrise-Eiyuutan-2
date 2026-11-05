"""Fresh-boot encyclopedia preview; guarded request and runtime-name data updates.

The debug build calls normal story initialization, then normal encyclopedia window
setup and infoDispPilMch with the original per-row illustration resources, except
the explicitly documented earlier-Hana artwork for unlisted pilot text row 134. No live
code rewrite or generic event call is offered. Close an entry with Circle to consume
the next request. In paginated builds, advance every page before closing the entry.
"""
import argparse,json,struct
from pathlib import Path
from mips import *

MAIL=0x9A8020
MAGIC=0x3242494C # LIB2
ENTRY=0x9A9000
DRIVER=ENTRY+0x80
TABLES={'pilot':(10515,308,0x1C3380,307),'machine':(10516,280,0x1C46B0,280)}
DESCRIPTOR_FALLBACKS={'pilot':{134:125},'machine':{}}
NAME_SLOT=0x515E28 # mesSetMESVAL: index * 37, up to 36 bytes plus NUL

def descriptor_fallbacks(elf=None):
    """Validate complete debug coverage; never infer artwork for an unknown row."""
    if elf is None:
        from elf import Elf,PATH
        elf=Elf(PATH.read_bytes())
    result=[]
    for kind,(table,count,base,records) in TABLES.items():
        native={}
        raw=elf.at(base,records*16)
        for slot in range(records):
            character,row,resource,cg=struct.unpack_from('<4I',raw,slot*16)
            if row in native or not 0<=row<count:raise ValueError('Invalid native '+kind+' descriptor rows')
            native[row]=(slot,resource,cg)
        registered=DESCRIPTOR_FALLBACKS[kind]
        if set(range(count))-set(native)!=set(registered):raise ValueError('Unexpected missing '+kind+' descriptor')
        for row,source in registered.items():
            if source not in native:raise ValueError('Fallback illustration source absent')
            slot,resource,cg=native[source]
            result.append(dict(kind=kind,table=table,row=row,source_row=source,source_slot=slot,
                               descriptor_address=base+slot*16,resource_pack=resource,cg_asset=cg,
                               scope='Earlier Hana artwork only; row 134 text is retained. Later artwork and ordinary library availability remain unverified.'))
    return result

def name_bytes(value):
    if not 1<=len(value)<=8 or any(ord(c)<32 or ord(c)==127 or c in '#@%^|' for c in value):
        raise ValueError('Test name must be 1-8 printable characters without renderer commands')
    raw=value.encode('cp932')
    if len(raw)>16:raise ValueError('Name exceeds native eight-character byte bound')
    return raw+bytes(37-len(raw))

def set_test_name(p,value):
    state=status(p)
    if not state['running'] or not state.get('pagination',{}).get('active'):
        raise RuntimeError('Test-name updates require an active paginated preview entry')
    cg=p.read32(0x237BF8)
    if p.read32(0x51D71C) or not cg or p.read(cg+0x2C,4)!=struct.pack('<f',128.0):
        raise RuntimeError('Wait for the native text task and illustration fade to finish before changing a test name')
    # Current glyphs are already built. The native @0 command reads the value
    # again on a later page draw; no executable code or pointer is changed.
    if p.read(0x12C620,8)!=pack([addiu('sp','sp',-0x50),sd('s3',0x30,'sp')]):
        raise RuntimeError('Unexpected native runtime-value implementation')
    previous=p.read(NAME_SLOT,37);p.write(NAME_SLOT,name_bytes(value));return previous

def initial(kind,row):
    table,count,_,_=TABLES[kind]
    if not 0<=row<count:raise ValueError('Preview row outside table')
    return struct.pack('<7I',MAGIC,table,row,0xffffffff,0,0,0)

def entry_code():
    return pack([addiu('sp','sp',-16),sd('ra',0,'sp'),jal(0x102530),NOP,
                 jal(0x13F5D8),NOP,ld('ra',0,'sp'),jr('ra'),addiu('sp','sp',16)])

def driver_code():
    a=Asm(DRIVER)
    a(addiu('sp','sp',-0x60),sd('ra',0x50,'sp'))
    for i,r in enumerate(('s0','s1','s2','s3','s4')):a(sd(r,i*16,'sp'))
    a(la('s0',MAIL),addiu('v0','zero',1),sw('v0',24,'s0'))
    a.label('next');a(lw('s1',8,'s0'),lw('s2',4,'s0'),addiu('v0','zero',10515))
    a.br('bne','s2','v0','machine');a(NOP)
    a(sltiu('v0','s1',308),la('s3',0x1C3380),addiu('s4','zero',307))
    a.br('b','bounds');a(NOP)
    a.label('machine');a(addiu('v0','zero',10516))
    a.br('bne','s2','v0','exit');a(NOP)
    a(sltiu('v0','s1',280),la('s3',0x1C46B0),addiu('s4','zero',280))
    a.label('bounds');a.br('beqz','v0','exit');a(NOP)
    a.label('lookup');a(lw('v0',4,'s3'))
    a.br('beq','v0','s1','show');a(NOP)
    a(addiu('s4','s4',-1),addiu('s3','s3',16))
    a.br('bnez','s4','lookup');a(NOP)
    for i,fallback in enumerate(descriptor_fallbacks()):
        skip='fallback_next_'+str(i)
        a(addiu('v0','zero',fallback['table']))
        a.br('bne','s2','v0',skip);a(NOP)
        a(addiu('v0','zero',fallback['row']))
        a.br('bne','s1','v0',skip);a(NOP)
        a(la('s3',fallback['descriptor_address']))
        a.br('b','show');a(NOP)
        a.label(skip)
    a.br('b','exit');a(NOP)
    a.label('show');a(sw('s1',12,'s0'),sw('s2',16,'s0'),lw('a0',8,'s3'),lw('a1',12,'s3'),move('a2','s2'))
    a(jal(0x13FFA0),move('a3','s1'),lw('v0',20,'s0'),addiu('v0','v0',1),sw('v0',20,'s0'))
    a.br('b','next');a(NOP)
    a.label('exit');a(sw('zero',24,'s0'),ld('ra',0x50,'sp'))
    for i,r in enumerate(('s0','s1','s2','s3','s4')):a(ld(r,i*16,'sp'))
    a(jr('ra'),addiu('sp','sp',0x60));return a.assemble()

def payload():
    out=bytearray(entry_code());out.extend(bytes(DRIVER-ENTRY-len(out)));out+=driver_code();return out

def patches():
    return [(0x9A0550,pack([j(0x102530)]),pack([j(ENTRY)]),'debug preview after story initialization'),
            (0x13F690,pack([jal(0x13F6C8)]),pack([jal(DRIVER)]),'debug encyclopedia driver')]

def status(p):
    from control import check
    check(p)
    fields=struct.unpack('<7I',p.read(MAIL,28))
    if fields[0]!=MAGIC:raise RuntimeError('Preview absent: fresh-boot a --preview build')
    result=dict(zip(('magic','requested_table','requested_row','active_row','active_table','completed','running'),fields))
    pager=struct.unpack('<10I',p.read(0x9AA900,40))
    if pager[0]==0x32474150:
        result['pagination']=dict(zip(('active','page','more','table','row','error','source_bytes','font_end','font_start'),pager[1:]))
    return result

def main():
    from pine import Pine
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('action',choices=['status','show','exit','name'])
    ap.add_argument('--table',choices=TABLES,default='machine');ap.add_argument('--row',type=int,default=0)
    ap.add_argument('--value',help='Bounded runtime test name; consumed at next entry expansion')
    ap.add_argument('--wide-name-test',action='store_true',help='Eight full-width W glyphs, the maximum-width test')
    ap.add_argument('--run',action='store_true');args=ap.parse_args()
    value=chr(0xFF37)*8 if args.wide_name_test else args.value
    if args.action=='name':
        if value is None:ap.error('name requires --value or --wide-name-test')
        name_bytes(value)
    elif value is not None:ap.error('Name options require the name action')
    if args.action!='status' and not args.run:
        print('DRY RUN:',args.action,ascii(value) if args.action=='name' else (args.table,args.row),'bounded data only; consumed between entries.');return
    p=Pine()
    try:
        state=status(p)
        if args.action!='status':
            if not state['running']:raise RuntimeError('Preview is not active; select New Game first')
            if args.action=='name':
                previous=set_test_name(p,value)
                print('Runtime test name saved; previous 37-byte slot:',previous.hex())
            elif args.action=='show':
                table,count,_,_=TABLES[args.table]
                if not 0<=args.row<count:raise ValueError('Row outside table')
                p.write(MAIL+4,struct.pack('<II',table,args.row))
            else:p.write32(MAIL+8,0xffffffff)
            print('Request saved. Advance all pages, then close the current entry with Circle.')
        print(json.dumps(status(p)))
    finally:p.close()
if __name__=='__main__':main()
