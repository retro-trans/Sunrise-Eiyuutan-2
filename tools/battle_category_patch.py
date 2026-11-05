"""Include every reviewed shared battle bark and remaining battle input format.

Inventory the complete6519-row bank, preserving56 source-language holds. Use
the exact same reviewed row mapping in both original identical physical copies.
"""
import argparse,json,hashlib,struct,re
from elf import ROOT,PATH,Elf
from extract import pack_members
from build import replace_pack,make_iso
from iso import records
from textcodec import encode,decode,controls,parse_table,build_table
from message_pages import pages
from travel_items_patch import stage_row
import card_dialog_patch as prior
import battle_bank,vwf,fontgen
from mips import *

BASE_SHA='59f23cb249f6fabfabd87467c38406aae9ddf98075b18727f8760a48116c23b5'
LANGUAGE=ROOT/'work/translation/en/battle-category.en.json'
LANGUAGE_SHA='bace0a8b437517424b9050f6a5b50e07257388f6e706d48fb4842872b4fd0989'
TEXT=0x9B7AC0;END=0x9B7B00
UI_REFS=((0x231ED0,0x16D8D0,0x16D8D8,'s0'),(0x231EE8,0x16DACC,0x16DAD0,'s0'),(0x232020,0x16EA24,0x16EA2C,'a1'))
digest=prior.digest

def language():
 raw=LANGUAGE.read_bytes();d=json.loads(raw)
 if digest(raw)!=LANGUAGE_SHA or d['translated_rows']!=6463 or d['held_rows']!=56:raise ValueError('Reviewed battle category changed')
 if set(r['id']for r in d['rows'])|{r['id']for r in d['unresolved']}!=set(range(6519)):raise ValueError('Incomplete category inventory')
 return d

def glyph():
 vals,width=fontgen.render_glyph('ū',26)
 if width!=12:raise ValueError('Registered macron glyph font/metrics changed')
 return fontgen.pack4(vals),width

def patch(data,packs):
 if digest(data)!=BASE_SHA:raise ValueError('Complete0.2.24 baseline changed')
 e=Elf(data);source=Elf(PATH.read_bytes());out=bytearray(data);result=dict(packs);d=language();changes={};expected={};fitting=[];sizes={};staged={};originals=battle_bank.original_tables();widths=json.loads((ROOT/'work/output/v0.2.24/build_info.json').read_text('utf8'))['font_widths'];g,gw=glyph();widths[127]=gw
 def word(at,old,new):
  if int.from_bytes(e.at(at,4),'little')!=old:raise ValueError('Native instruction guard changed at'+hex(at))
  expected[hex(at)]=hex(old);changes[hex(at)]=hex(new);struct.pack_into('<I',out,e.offset(at),new)
 # A reviewed spelling needs ū. Retain all original ASCII and all source-used
 # Japanese glyphs. Source ATMB/catalog audits found no literal DEL and no 犾
 # (EE40), the previously unused cell at this serial index.
 word(0x108BA0,sltiu('v0','a0',127),sltiu('v0','a0',128))
 word(vwf.SCALE+16,sltiu('at','a0',127),sltiu('at','a0',128))
 if e.at(vwf.TABLE+127,1)!=bytes([13]):raise ValueError('Unused glyph width changed')
 out[e.offset(vwf.TABLE+127)]=gw
 pack=result[23];m=next(m for m in pack_members(pack)if m['id']==77);font=bytearray(pack[m['offset']:m['offset']+m['size']]);slot=(vwf.ASCII_BASE+127)*338;oldglyph=bytes(font[slot:slot+338]);font[slot:slot+338]=g;result[23]=replace_pack(pack,{77:bytes(font)})
 if len(result[23])!=len(pack):raise ValueError('Same-size font must retain pack extent')
 signature=lambda p:{k:v for k,v in p.items()if k not in('start','end','body')}
 rows=originals[battle_bank.CANONICAL][:]
 for r in d['rows']:
  i=r['id'];raw=rows[i]
  if digest(raw)!=r['source_sha256']or controls(decode(raw))!=controls(r['en']):raise ValueError('Battle source/control mismatch'+str(i))
  row,fit=stage_row(r['en'],widths,'battle-barks')
  if list(map(signature,pages(raw)))!=list(map(signature,pages(row))):raise ValueError('Battle native speaker/voice/function changed')
  rows[i]=row;staged[i]=row;fitting.append(dict(id=i,row_sha256=digest(row),native_layout=fit))
 for r in d['unresolved']:
  if digest(rows[r['id']])!=r['source_sha256']:raise ValueError('Held source row changed')
 table=build_table(rows)
 if parse_table(table)!=rows:raise ValueError('Complete battle table roundtrip failed')
 for name in battle_bank.TABLES:
  pn,mid=map(int,name.split('_'));baseline=result[pn];old=next(m for m in pack_members(baseline)if m['id']==mid);before=parse_table(baseline[old['offset']:old['offset']+old['size']]);retained=0
  for i,r in enumerate(before):
   if r!=originals[name][i]:
    if i not in staged:raise ValueError('Previously translated row omitted')
    for oldp,newp in zip(pages(r),pages(rows[i])):
     if oldp['body'].split()!=newp['body'].split():raise ValueError('Previously translated words changed'+str(i))
    retained+=1
  result[pn]=replace_pack(baseline,{mid:table});site=e.symbol('_pacfileA')['va']+pn*8+4;word(site,len(baseline),len(result[pn]));sizes[name]=dict(pack=pn,member=mid,before=len(baseline),after=len(result[pn]),table_size=len(table),table_sha256=digest(table),pack_sha256=digest(result[pn]),previous_rows_retained=retained)
 if e.at(TEXT,END-TEXT)!=bytes(END-TEXT):raise ValueError('Small input format pool occupied')
 payload=bytearray();addresses={}
 for r in d['ui']:
  raw=bytes.fromhex(r['source_raw']);va=r['va'];en=r['recommended_en']
  if digest(raw)!=r['source_sha256']or source.at(va,len(raw))!=raw or e.at(va,len(raw))!=raw:raise ValueError('UI source string changed')
  if re.findall(r'%(?:\d+)?[ds]',en)!=r['format_tokens']:raise ValueError('UI runtime formats changed')
  addresses[va]=TEXT+len(payload);payload+=encode(en)+b'\0'
 if TEXT+len(payload)>END:raise ValueError('Input format pool overflow')
 for va,hi,lo,reg in UI_REFS:
  oldhi=int.from_bytes(e.at(hi,4),'little');oldlo=int.from_bytes(e.at(lo,4),'little');a=addresses[va]
  if oldhi!=lui(reg,0x23)or oldlo!=addiu(reg,reg,va&65535):raise ValueError('UI address load changed')
  word(hi,oldhi,lui(reg,(a+0x8000)>>16));word(lo,oldlo,addiu(reg,reg,a&65535))
 out[e.offset(TEXT):e.offset(TEXT)+len(payload)]=payload
 # All110 device titles fit a448px centred parent. Keep its centre and the
 # numeric child's centre at x320; preserve amounts, limits and callbacks.
 word(0x16E9D4,addiu('a1','zero',160),addiu('a1','zero',96));word(0x16EA00,addiu('a3','zero',320),addiu('a3','zero',448))
 titles=json.loads((ROOT/'work/output/v0.2.24/build_info.json').read_text('utf8'))['battle_details']['resolved_fields'];title_widths=[sum((widths[ord(c)]if ord(c)<128 else 26)+2 for c in r['en'])for r in titles if r['table']=='it_devi_info'and r['field']==8]
 if max(title_widths)>432:raise ValueError('Complete device title exceeds widened SP window')
 return bytes(out),result,dict(language_sha256=LANGUAGE_SHA,source_rows=6519,translated_rows=6463,new_rows_per_copy=6463-1568,held_rows=d['unresolved'],physical_tables=sizes,body_calls=sum(len(r['native_layout'])for r in fitting),native_layout=fitting,glyph=dict(character='ū',encoded_byte='7f',serial=vwf.ASCII_BASE+127,width=gw,pixel_sha256=digest(g),previous_cell_sha256=digest(oldglyph),font_pack=23,font_member=77,font_offset=slot),ui=dict(addresses={hex(k):hex(v)for k,v in addresses.items()},payload_va=hex(TEXT),payload_size=len(payload),payload_sha256=digest(payload),rows=[dict(id=r['id'],en=r['recommended_en'])for r in d['ui']],sp_window=dict(x=96,width=448,maximum_device_title_width=max(title_widths),centre=320,numeric_child_unchanged=True)),patched_words=changes,expected_words=expected)

def inputs():
 data,packs,overlays,report=prior.inputs();data,packs,category=patch(data,packs)
 return data,packs,overlays,dict(report,battle_category=category)

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');a=ap.parse_args();data,packs,overlays,report=inputs();r=report['battle_category'];print(json.dumps(dict(version='0.2.25',elf_sha256=digest(data),translated_per_copy=r['translated_rows'],additional_per_copy=r['new_rows_per_copy'],held=len(r['held_rows']),tables=r['physical_tables'],glyph=r['glyph'],ui=r['ui'],samples=[x for x in r['native_layout']if x['id']in(3272,5328,5329,5641)]),indent=1),flush=True)
 if not a.write:print('DRY no game files or ISO written.');return
 dest=ROOT/'work/output/v0.2.25';dest.mkdir(exist_ok=False);(dest/'SLPS_250.70').write_bytes(data)
 for i,p in packs.items():(dest/f'{i:05d}.pack').write_bytes(p)
 for i,p in overlays.items():(dest/f'{i:05d}.evemap').write_bytes(p)
 image=dest/'Sunrise Eiyuutan 2 EN v0.2.25.iso';make_iso(image,data,packs,overlays);previous=ROOT/'work/output/v0.2.24/Sunrise Eiyuutan 2 EN v0.2.24.iso';old=next(r for r in records(previous)if r['path']=='/MOVIE.AFS');new=next(r for r in records(image)if r['path']=='/MOVIE.AFS');h=hashlib.sha256()
 if old['size']!=new['size']:raise ValueError('Retained movie extent changed')
 with previous.open('rb')as f,image.open('r+b')as g:
  f.seek(old['lba']*2048);g.seek(new['lba']*2048);left=old['size']
  while left:
   block=f.read(min(left,4*1024*1024))
   if not block:raise ValueError('Truncated prior movie archive')
   g.write(block);h.update(block);left-=len(block)
 info=json.loads((ROOT/'work/output/v0.2.24/build_info.json').read_text('utf8'));info.update(version='0.2.25',based_on='0.2.24',**report,elf_sha256=digest(data),iso_path=str(image),iso_size=image.stat().st_size,movie_archive_retained=dict(based_on='0.2.24',size=new['size'],sha256=h.hexdigest()),scope='Complete reviewed battle bank in both physical copies, three remaining battle input formats and macron glyph;56 source-meaning holds remain explicit; retain0.2.24 UI/layout/lyrics/audio.',in_game_validation='pending native battle-category preview')
 info['font_widths']=list(info['font_widths']);info['font_widths'][127]=r['glyph']['width'];info['translated_rows']=sorted(set(info['translated_rows'])|{name+':'+str(row['id'])for name in battle_bank.TABLES for row in language()['rows']})
 for key in('iso_sha256','native_validation_report'):info.pop(key,None)
 (dest/'build_info.json').write_text(json.dumps(info,indent=1)+'\n','utf8');print('WRITE',image)

if __name__=='__main__':main()
