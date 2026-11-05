"""Complete battle-entry messages and restore normal battle-window font widths.

Extends0.2.20; dry run by default. Native selectors, callbacks, combat logic,
voices and row boundaries remain. Rebuild the entire172-row message member.
"""
import argparse,json,re,struct
from elf import ROOT,Elf
from extract import pack_members
from build import replace_pack,make_iso
from textcodec import decode,controls,parse_table,build_table
from message_pages import pages
from travel_items_patch import stage_row
from mips import addiu,move,jal,NOP
import story_dialogue_patch as prior

BASE_SHA='0356ea9a95e4a84f0001299844cfe0d7014744d87e5ed8f58cb02b25a80fcbaa'
LANGUAGE=ROOT/'work/translation/en/dat/04970_10511.en.json'
LANGUAGE_SHA='4a4875fd78daaa07ea763f894ba9d77bec0d1dad1c0a7ebf597fdfacbb7b98ed'
digest=prior.digest

# Each instruction is guarded against its complete old word, including register.
SELECTORS=(
 ('launch',0x146574,0x146614,0x146698,0x1466C0,0x1466F0,'v1','v1'),
 ('item',0x146EA4,0x146F34,0x146FC0,0x146FEC,0x147014,'v1','a1'),
 ('repair',0x147CD4,0x147D48,0x147D94,0x147DB8,0x147DEC,'v1','v1'),
)

def language():
 raw=LANGUAGE.read_bytes()
 if digest(raw)!=LANGUAGE_SHA:raise ValueError('Reviewed battle-entry language revision changed')
 d=json.loads(raw);checkpoint=json.loads((ROOT/'docs/review_field172_parent174.json').read_text('utf8'))
 if d['table']!='04970_10511' or [r['id']for r in d['rows']]!=list(range(172)):raise ValueError('Incomplete battle-entry category')
 for r,c in zip(d['rows'],checkpoint['rows']):
  if (r['id'],r['source_sha256'],digest(r['en'].encode('utf8')))!=(c['id'],c['source_sha256'],c['en_sha256']):raise ValueError('Completed language checkpoint differs')
 return d

def patch(data,packs):
 if digest(data)!=BASE_SHA:raise ValueError('Complete0.2.20 baseline changed')
 e=Elf(data);out=bytearray(data);expected={};changed={}
 def word(at,old,new):
  if int.from_bytes(e.at(at,4),'little')!=old:raise ValueError('Battle font instruction changed at'+hex(at))
  struct.pack_into('<I',out,e.offset(at),new);expected[hex(at)]=hex(old);changed[hex(at)]=hex(new)
 for name,mirror,window,measure,font,row,mreg,rreg in SELECTORS:
  for at,reg,old,new in ((mirror,mreg,392,224),(window,'a3',224,400),(measure,'a1',13,26),(font,'a2',13,26),(row,rreg,224,400)):
   word(at,addiu(reg,'zero',old),addiu(reg,'zero',new))
 # Cannon/Support amount dialog and its matching Repair dialog. The numeric
 # child keeps the same position relative to the enlarged parent's centre.
 for at,reg,old,new in ((0x147414,'a1',392,224),(0x1474EC,'a3',224,400),
  (0x14754C,'t0',14,26),(0x147568,'t0',14,26),
  (0x147FF4,'a3',224,400),(0x14800C,'a1',392,224),
  (0x14806C,'t0',14,26),(0x148088,'t0',14,26),(0x1480A4,'t0',14,26)):
  word(at,addiu(reg,'zero',old),addiu(reg,'zero',new))
 word(0x1475A8,addiu('a1','a1',70),addiu('a1','a1',158))
 word(0x14811C,addiu('a1','a1',70),addiu('a1','a1',158))
 # All six callers use ordinary strings (five battle prompts and the native
 # save summary). Replace the two-byte-character estimate with the same
 # proportional pixel measurement used by the renderer and native selectors.
 old=(jal(0x19F7D8),move('a0','s1'),0x00021042,addiu('v1','s2',2),0x00621818)
 new=(move('a0','s1'),move('a1','s2'),jal(0x10E510),NOP,move('v1','v0'))
 for i,(a,b)in enumerate(zip(old,new)):word(0x1524A8+i*4,a,b)
 pn,mid=4970,10511;source=(ROOT/f'work/source/afs/RESOURCE/{pn:05d}.bin').read_bytes();baseline=packs.get(pn,source)
 m=next(m for m in pack_members(source)if m['id']==mid);original=source[m['offset']:m['offset']+m['size']]
 bm=next(m for m in pack_members(baseline)if m['id']==mid)
 if baseline[bm['offset']:bm['offset']+bm['size']]!=original:raise ValueError('Unanticipated preexisting battle-entry translation')
 rows=parse_table(original);widths=json.loads((ROOT/'work/output/v0.2.20/build_info.json').read_text('utf8'))['font_widths'];layout=[]
 signature=lambda p:{k:v for k,v in p.items()if k not in('start','end','body')}
 for r in language()['rows']:
  old=rows[r['id']]
  if digest(old)!=r['source_sha256'] or controls(decode(old))!=controls(r['en']):raise ValueError('Battle-entry source/control guard failed')
  if re.search(r'[\u3040-\u30ff\u3400-\u9fff\uff61-\uff9f]',r['en']):raise ValueError('Untranslated battle-entry text')
  new,fit=stage_row(r['en'],widths,'story')
  if list(map(signature,pages(old)))!=list(map(signature,pages(new))):raise ValueError('Battle-entry native speaker/voice/call changed')
  rows[r['id']]=new;layout.append(dict(id=r['id'],native_layout=fit))
 table=build_table(rows)
 if parse_table(table)!=rows:raise ValueError('Battle-entry table rebuild mismatch')
 result=dict(packs);result[pn]=replace_pack(baseline,{mid:table});va=e.symbol('_pacfileA')['va']+pn*8+4
 word(va,len(baseline),len(result[pn]))
 report=dict(language_sha256=LANGUAGE_SHA,source_rows=172,table='04970_10511',native_layout=layout,
  patched_words=changed,expected_words=expected,selector_font=[26,26],selector_width=400,mirrored_x=[16,224],
  prompt_font=[26,26],prompt_measurement='native proportional pixels',
  resource_pack=dict(id=pn,member=mid,before=len(baseline),after=len(result[pn]),table_sha256=digest(table),pack_sha256=digest(result[pn])))
 return bytes(out),result,report

def inputs():
 data,packs,overlays,report=prior.inputs();data,packs,entry=patch(data,packs)
 return data,packs,overlays,dict(**report,battle_readability=entry)

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('version');ap.add_argument('--write',action='store_true');a=ap.parse_args()
 if a.version!='0.2.21':raise ValueError('Guarded battle readability package is0.2.21')
 data,packs,overlays,report=inputs();r=report['battle_readability']
 print(json.dumps(dict(version=a.version,elf_sha256=digest(data),source_rows=r['source_rows'],packs=len(packs),overlays=len(overlays),font=r['selector_font'],window_width=400,patches=r['patched_words'],sample=language()['rows'][2]['en']),indent=1))
 if not a.write:print('DRY: no game files/ISO written.');return
 dest=ROOT/'work/output/v0.2.21';dest.mkdir(exist_ok=False);(dest/'SLPS_250.70').write_bytes(data)
 for n,b in packs.items():(dest/f'{n:05d}.pack').write_bytes(b)
 for n,b in overlays.items():(dest/f'{n:05d}.evemap').write_bytes(b)
 image=dest/'Sunrise Eiyuutan 2 EN v0.2.21.iso';make_iso(image,data,packs,overlays);retained=prior.retain_movies(image)
 info=json.loads((ROOT/'work/output/v0.2.20/build_info.json').read_text('utf8'));info.update(version=a.version,based_on='0.2.20',**report,elf_sha256=digest(data),iso_path=str(image),iso_size=image.stat().st_size,movie_archive_retained=retained,in_game_validation='pending; independent of binary checks',scope='All172 battle-entry messages and normal-width interactive launch/item/repair selectors and Cannon/Support/Repair amount prompts; retains complete0.2.20 content.')
 info['translated_rows']=sorted(set(info['translated_rows'])|{f'04970_10511:{i}'for i in range(172)})
 for key in('iso_sha256','native_validation_report'):info.pop(key,None)
 (dest/'build_info.json').write_text(json.dumps(info,indent=1)+'\n','utf8');print('WRITE',image)

if __name__=='__main__':main()
