"""Inspect a standard-build message from a same-build savestate, without writes.

Default stdout omits Japanese prose. --text is local console inspection only.
Exact current built table, context, parser cursor and native window are checked.
"""
import argparse,hashlib,json,struct,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from elf import ROOT,Elf
from extract import pack_members
from textcodec import parse_table
from message_pages import pages
from sstate import State

GP=0x23F570
CONTEXT=0x515C70
VALUE_POOL=0x515E28
SPEAK_WINDOW=GP-0x5ff0
PARSER_CURSOR=GP-0x5f84
ACTIVE=GP-0x5fc4


def built_table(folder,table):
    pn,mid=map(int,table.split('_'));packpath=folder/f'{pn:05d}.pack'
    pack=packpath.read_bytes() if packpath.exists() else (ROOT/f'work/source/afs/RESOURCE/{pn:05d}.bin').read_bytes()
    member=next(m for m in pack_members(pack) if m['id']==mid)
    return pack[member['offset']:member['offset']+member['size']]


def prompt_state(ee):
    """Read native prompt coordinates; no live writes or visual approval."""
    def word(a):
        if not 0<=a<=len(ee)-4:raise ValueError('Invalid native prompt address')
        return struct.unpack_from('<I',ee,a)[0]
    obj=word(GP-0x5fdc)
    if not obj:return None
    if not 0<obj<=len(ee)-0x28:raise ValueError('Invalid native prompt object')
    x,y,width,height=(word(obj+n) for n in (0x18,0x1c,0x20,0x24))
    return dict(object=hex(obj),enabled=word(GP-0x5fd8),object_flags=word(obj+8),
                origin=[x,y],last_glyph_size=[width,height],
                triangle_left=x+8,triangle_right=x+26,triangle_tip_x=x+17,
                triangle_top=y+height-18,triangle_bottom=y+height-2,
                scope='Coordinates follow original native triangle overrides; screenshot review is separate.')


def inspect(state,version,table='04905_10383',include_text=False,include_prompt=False,allow_tutorial_preview=False,include_resource_origin=False,allow_battle_preview=False):
    ee=State(state).ee();folder=ROOT/'work/output'/('v'+version)
    info=json.loads((folder/'build_info.json').read_text());elf=Elf((folder/'SLPS_250.70').read_bytes())
    if info['preview_request']:raise ValueError('Standard-build profile required')
    tutorial=info.get('tutorial_preview')
    if tutorial and not allow_tutorial_preview:raise ValueError('Explicit tutorial preview opt-in required')
    battle=info.get('battle_preview')
    if battle and not allow_battle_preview:raise ValueError('Explicit battle preview opt-in required')
    # Existing VWF changes are allowed; these native staging/geometry routines
    # must match the selected built ELF, rather than an older loaded state.
    for va,size in ((0x12C820,0x11c),(0x12E9A0,0x314),(0x12C6E0,0xf0),(0x12DA40,0x78)):
        if ee[va:va+size]!=elf.at(va,size):raise ValueError('Loaded message code differs from this build')
    def word(a):
        if not 0<=a<=len(ee)-4:raise ValueError('Invalid EE word address')
        return struct.unpack_from('<I',ee,a)[0]
    context=ee[CONTEXT:VALUE_POOL];body=context[0x28:].split(b'\0')[0]
    if len(body)==400:raise ValueError('Native text lacks a bounded terminator')
    cursor=word(PARSER_CURSOR);window=word(SPEAK_WINDOW)
    raw=built_table(folder,table);rows=parse_table(raw)
    bases=[];off=ee.find(raw)
    while off!=-1:bases.append(off);off=ee.find(raw,off+1)
    matches=[]
    offsets=struct.unpack_from('<%dI'%len(rows),raw,8)
    flags,speaker,voice,parameter,function,count=struct.unpack_from('<6I',context)
    if count>4:raise ValueError('Invalid native function argument count')
    args=list(struct.unpack_from('<4I',context,0x18))[:count]
    native=dict(flags=flags,speaker=speaker,voice=voice,voice_parameter=parameter,function=function,arguments=args)
    for base in bases:
        for i,(row,start) in enumerate(zip(rows,offsets)):
            for n,page in enumerate(pages(row)):
                if base+start+page['end']==cursor and all(page[k]==v for k,v in native.items()) and page['body']==body:
                    matches.append(dict(table=table,row=i,native_call=n,start=page['start'],end=page['end'],
                                        row_sha256=hashlib.sha256(row).hexdigest(),table_base=hex(base)))
    out=dict(build=version,state=str(Path(state).resolve()),active=word(ACTIVE),parser_cursor=hex(cursor),
             context=native,effective_speaker=word(GP-0x5fe8),requested_speaker=word(GP-0x5fec),
             header_updates_speaker=bool(flags&0x30),body_bytes=len(body),body_sha256=hashlib.sha256(body).hexdigest(),source_matches=matches,
             runtime_values_sha256=hashlib.sha256(ee[VALUE_POOL:VALUE_POOL+9*37]).hexdigest(),
             live_window=None,scope='Same-build native staging observation; no English display approval.')
    if window:
        if not 0<window<len(ee)-0x48:raise ValueError('Invalid message window')
        obj=word(window)
        out['live_window']=dict(address=hex(window),object=hex(obj),font=word(window+0x10),
            cursor_x=word(window+0x14),cursor_y=word(window+0x18),glyph_width=word(window+0x38),
            glyph_height=word(window+0x3c),flags=word(window+4),input_mode=word(window+8))
        if obj:
            out['live_window']['text_origin']=[word(obj+0x18),word(obj+0x1c)]
    if include_text:out['local_body']=body.decode('cp932')
    if include_prompt:
        for va,size in ((0x12d268,68),(0x110a48,284)):
            if ee[va:va+size]!=elf.at(va,size):raise ValueError('Native prompt code differs from this build')
        out['native_prompt']=prompt_state(ee)
    if tutorial:
        import tutorial_preview as preview
        for va,n in ((preview.HOOK,8),(preview.BASE,preview.MAIL-preview.BASE)):
            if ee[va:va+n]!=elf.at(va,n):raise ValueError('Tutorial preview code differs from selected build')
        out['tutorial_preview']=preview.telemetry(ee[preview.MAIL:preview.END],tutorial)
        out['scope']='Fresh-build forced tutorial preview staging; no natural-trigger or English display approval.'
    if include_resource_origin:
        if len(matches)!=1:raise ValueError('Resource provenance needs one exact native table/cursor match')
        from resource_origin import origin
        pn=int(table.split('_')[0]);packpath=folder/f'{pn:05d}.pack'
        pack=packpath.read_bytes() if packpath.exists() else (ROOT/f'work/source/afs/RESOURCE/{pn:05d}.bin').read_bytes()
        out['resource_origin']=origin(ee,elf,pack,table,int(matches[0]['table_base'],16))
    if battle:
        import battle_preview as preview
        for va,n in ((preview.HOOK,8),(preview.BASE,preview.MAIL-preview.BASE)):
            if ee[va:va+n]!=elf.at(va,n):raise ValueError('Battle preview code differs from selected build')
        out['battle_preview']=preview.telemetry(ee[preview.MAIL:preview.END],battle,info.get('battle_preview_first',0),info.get('battle_preview_count',80),info.get('battle_preview_rows'))
        out['scope']='Fresh-build forced physical battle preview; no original-trigger or English display approval.'
    return out


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('version');ap.add_argument('state')
    ap.add_argument('--table',default='04905_10383');ap.add_argument('--text',action='store_true');ap.add_argument('--prompt',action='store_true')
    ap.add_argument('--allow-tutorial-preview',action='store_true');ap.add_argument('--resource-origin',action='store_true');ap.add_argument('--allow-battle-preview',action='store_true');a=ap.parse_args()
    print(json.dumps(inspect(a.state,a.version,a.table,a.text,a.prompt,a.allow_tutorial_preview,a.resource_origin,a.allow_battle_preview),ensure_ascii=True,indent=1))


if __name__=='__main__':main()
