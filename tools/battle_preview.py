"""Fresh, bounded native preview of reviewed battle rows at one physical destination.

Replace the first exact tutorial file4950/member10472/row0 request once. Each
bark uses the original file-load/message/cleanup routine; there are no live hooks.
This verifies rendering and physical resources, not the original battle triggers.
"""
import hashlib,re,struct,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent/'dbg'))
from mips import *
from tutorial_preview import HOOK,NATIVE,EXPECTED
import encyclopedia,battle_bank

BASE=0x9B7000
MAIL=BASE+0x300
END=MAIL+64
MAGIC=0x31504B42 # BKP1
LIST_MAGIC=0x32504B42 # BKP2: explicit reviewed row selection
ROW_LIST=BASE+0x200 # 80 uint16 IDs, protected with the rest of the build payload
FIRST=0
COUNT=80
SOURCE=(4950,10472,0)
PROFILES={'canonical':(1,23,10512,battle_bank.CANONICAL),'alias':(2,4972,11849,battle_bank.ALIAS)}


def bounds(first=FIRST,count=COUNT):
    if type(first) is not int or type(count) is not int or not 1<=count<=80 or not 0<=first<=battle_bank.SOURCE_ROWS-count:
        raise ValueError('Battle preview requires a valid source range of1-80 rows')
    return first,count


def selection(first=FIRST,count=COUNT,rows=None):
    if rows is None:
        bounds(first,count);return first,count,tuple(range(first,first+count))
    if not isinstance(rows,(list,tuple)) or not 1<=len(rows)<=80 or any(type(i) is not int or not 0<=i<battle_bank.SOURCE_ROWS for i in rows):
        raise ValueError('Explicit battle preview requires1-80 valid row IDs')
    ids=tuple(rows)
    if any(a>=b for a,b in zip(ids,ids[1:])):raise ValueError('Explicit battle rows must be strictly increasing and unique')
    if type(first) is not int or type(count) is not int or (first,count) not in ((FIRST,COUNT),(ids[0],len(ids))):
        raise ValueError('Explicit battle rows conflict with range limits')
    return ids[0],len(ids),ids


def parse_rows(text):
    ids=[]
    for part in text.split(','):
        if not re.fullmatch(r'\d+(?:-\d+)?',part):raise ValueError('Battle rows use IDs or inclusive ranges separated by commas')
        ends=list(map(int,part.split('-')));first,last=ends[0],ends[-1]
        if not 0<=first<=last<battle_bank.SOURCE_ROWS or len(ids)+last-first+1>80:raise ValueError('Invalid or oversized explicit battle selection')
        ids.extend(range(first,last+1))
    return list(selection(rows=ids)[2])


def row_signature(rows):
    return int.from_bytes(hashlib.sha256(struct.pack('<'+'H'*len(rows),*rows)).digest()[:4],'little')


def validate(elf,profile,first=FIRST,count=COUNT):
    bounds(first,count)
    if profile not in PROFILES:raise ValueError('Unsupported battle preview profile')
    if elf.symbol('_evefunc_start')['va']!=0x9A0000 or elf.symbol('_evefunc_size')['va']!=0x20000 or elf.symbol('_evescen_start')['va']!=0x9C0000:
        raise ValueError('Unexpected event reservation')
    if BASE<encyclopedia.END or END>0x9C0000:raise ValueError('Battle preview reservation collision')
    for typ,off,addr,pa,fs,ms,flags,al in elf.segments:
        if typ==1 and max(BASE,addr)<min(END,addr+max(fs,ms)):raise ValueError('Battle preview original segment overlap')
    for s in elf.symbols:
        if s['section'] not in (0,0xfff1) and s['size'] and max(BASE,s['va'])<min(END,s['va']+s['size']):
            raise ValueError('Battle preview original symbol overlap')
    if elf.at(HOOK,8)!=EXPECTED or elf.symbol('mesSpeakMessageFileLabel')['va']!=NATIVE or elf.at(NATIVE,8)!=bytes.fromhex('c0ffbd272000b2ff'):
        raise ValueError('Unexpected native event message bridge')


def require_translations(exports,first=FIRST,count=COUNT,selected_rows=None):
    first,count,ids=selection(first,count,selected_rows)
    for name in battle_bank.TABLES:
        obj=exports.get(name)
        if obj is None:raise ValueError('Battle preview requires both reviewed physical exports')
        rows={r['id']:r for r in obj['rows']}
        for i in ids:
            review=rows.get(i,{}).get('review')
            if not isinstance(review,dict) or any(review.get(k)!=v for k,v in (('accuracy','independent-reviewed'),('editorial','self-reviewed'),('proofread','self-reviewed'))):
                raise ValueError('Battle preview row is absent or language review pending')


def code(profile,first=FIRST,count=COUNT):
    bounds(first,count)
    if profile not in PROFILES:raise ValueError('Unsupported battle preview profile')
    pid,file,member,table=PROFILES[profile];a=Asm(BASE)
    for reg,value in zip(('a0','a1','a2'),SOURCE):
        a(addiu('t0','zero',value));a.br('bne',reg,'t0','original');a(NOP)
    a(la('t0',MAIL),lw('t1',0,'t0'),la('t2',MAGIC));a.br('bne','t1','t2','original');a(NOP)
    a(lw('t1',4,'t0'),addiu('t2','zero',pid));a.br('bne','t1','t2','original');a(NOP)
    a(lw('t1',8,'t0'));a.br('bnez','t1','original');a(NOP)
    for off,value in ((44,first),(48,count)):
        a(lw('t1',off,'t0'),addiu('t2','zero',value));a.br('bne','t1','t2','original');a(NOP)
    a(addiu('sp','sp',-0x40),sd('s0',0,'sp'),sd('s1',0x10,'sp'),sd('s2',0x20,'sp'),sd('ra',0x30,'sp'),
      move('s1','t0'),move('s2','a3'),sw('ra',20,'s1'),sw('a0',24,'s1'),sw('a1',28,'s1'),sw('a2',32,'s1'),
      addiu('t0','zero',1),sw('t0',8,'s1'),sw('t0',52,'s1'),sw('zero',16,'s1'),addiu('s0','zero',first))
    a.label('loop');a(sw('s0',12,'s1'),addiu('a0','zero',file),addiu('a1','zero',member),move('a2','s0'),move('a3','s2'),jal(NATIVE),NOP,
      addiu('s0','s0',1),addiu('t0','s0',-first),sw('t0',16,'s1'),sltiu('t1','s0',first+count))
    a.br('bnez','t1','loop');a(NOP)
    a(addiu('t0','zero',2),sw('t0',8,'s1'),ld('ra',0x30,'sp'),ld('s2',0x20,'sp'),ld('s1',0x10,'sp'),ld('s0',0,'sp'),jr('ra'),addiu('sp','sp',0x40))
    a.label('original');a(j(NATIVE),NOP)
    out=a.assemble()
    if BASE+len(out)>MAIL:raise ValueError('Battle preview overlaps telemetry')
    return out


def list_code(profile,ids):
    first,count,ids=selection(rows=ids)
    if profile not in PROFILES:raise ValueError('Unsupported battle preview profile')
    pid,file,member,table=PROFILES[profile];a=Asm(BASE)
    for reg,value in zip(('a0','a1','a2'),SOURCE):
        a(addiu('t0','zero',value));a.br('bne',reg,'t0','original');a(NOP)
    a(la('t0',MAIL),lw('t1',0,'t0'),la('t2',LIST_MAGIC));a.br('bne','t1','t2','original');a(NOP)
    for off,value in ((4,pid),(8,0),(44,first),(48,count),(56,row_signature(ids)),(60,2)):
        a(lw('t1',off,'t0'),la('t2',value));a.br('bne','t1','t2','original');a(NOP)
    a(addiu('sp','sp',-0x40),sd('s0',0,'sp'),sd('s1',0x10,'sp'),sd('s2',0x20,'sp'),sd('ra',0x30,'sp'),
      move('s1','t0'),move('s2','a3'),sw('ra',20,'s1'),sw('a0',24,'s1'),sw('a1',28,'s1'),sw('a2',32,'s1'),
      addiu('t0','zero',1),sw('t0',8,'s1'),sw('t0',52,'s1'),sw('zero',16,'s1'),move('s0','zero'))
    a.label('loop');a(la('t0',ROW_LIST),sll('t1','s0',1),addu('t0','t0','t1'),lhu('a2',0,'t0'),sw('a2',12,'s1'),
      addiu('a0','zero',file),addiu('a1','zero',member),move('a3','s2'),jal(NATIVE),NOP,
      addiu('s0','s0',1),sw('s0',16,'s1'),sltiu('t1','s0',count))
    a.br('bnez','t1','loop');a(NOP)
    a(addiu('t0','zero',2),sw('t0',8,'s1'),ld('ra',0x30,'sp'),ld('s2',0x20,'sp'),ld('s1',0x10,'sp'),ld('s0',0,'sp'),jr('ra'),addiu('sp','sp',0x40))
    a.label('original');a(j(NATIVE),NOP);out=a.assemble()
    if BASE+len(out)>ROW_LIST:raise ValueError('Explicit battle preview overlaps its row table')
    return out


def payload(elf,profile,first=FIRST,count=COUNT,selected_rows=None):
    first,count,ids=selection(first,count,selected_rows)
    validate(elf,profile,first,count);pid,file,member,table=PROFILES[profile]
    out=bytearray(END-BASE);body=code(profile,first,count) if selected_rows is None else list_code(profile,ids);out[:len(body)]=body
    if selected_rows is not None:struct.pack_into('<'+'H'*count,out,ROW_LIST-BASE,*ids)
    struct.pack_into('<16I',out,MAIL-BASE,MAGIC if selected_rows is None else LIST_MAGIC,pid,0,first,0,0,0,0,0,file,member,first,count,0,0 if selected_rows is None else row_signature(ids),0 if selected_rows is None else 2)
    return out


def patches(elf,profile,first=FIRST,count=COUNT):
    validate(elf,profile,first,count)
    return [(HOOK,EXPECTED,pack([j(BASE),NOP]),'debug/battle preview '+profile)]


def telemetry(raw,profile,first=FIRST,count=COUNT,selected_rows=None):
    first,count,ids=selection(first,count,selected_rows)
    if profile not in PROFILES or len(raw)!=64:raise ValueError('Invalid battle preview telemetry')
    w=struct.unpack('<16I',raw);pid,file,member,table=PROFILES[profile]
    tail=(0,0) if selected_rows is None else (row_signature(ids),2)
    if w[:2]!=(MAGIC if selected_rows is None else LIST_MAGIC,pid) or w[2] not in (0,1,2) or w[9:13]!=(file,member,first,count) or w[14:]!=tail:
        raise ValueError('Corrupt battle preview profile/limits')
    if w[2]==0:
        if w[3:9]!=(first,0,0,0,0,0) or w[13]!=0:raise ValueError('Corrupt unused battle preview state')
    else:
        if w[6:9]!=SOURCE or w[13]!=1 or w[3] not in ids:
            raise ValueError('Unexpected battle preview request provenance')
        if (w[2]==1 and (w[4]>=count or w[3]!=ids[w[4]])) or (w[2]==2 and (w[3],w[4])!=(ids[-1],count)):
            raise ValueError('Corrupt battle preview progress')
    out=dict(profile=profile,state=w[2],current_row=w[3],completed_rows=w[4],return_address=hex(w[5]),source_file=w[6],source_member=w[7],source_row=w[8],target_file=file,target_member=member,target_table=table,first=first,count=count,requests=w[13],scope='Forced native physical-destination preview; original battle triggers unverified.')
    if selected_rows is not None:out['selected_rows']=list(ids)
    return out
