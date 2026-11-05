"""Use consistent English glyphs for all player-facing item-name variants."""
import argparse,json,struct,hashlib,shutil
from elf import ROOT,Elf
from iso import records
import episode_titles_patch as prior
from prepare_item_typography import MAP
BASE_SHA='1d067807afb8056636eab1419a0dc395045af87a645f742044c9601c84c8b6e0'
LANGUAGE=ROOT/'work/translation/en/item-typography.en.json'
LANGUAGE_SHA='9fa40c50dc9fb54068d895fbc3ee398ebac3686f9e3aa5c3a961593fc142195e'
RANGES=((0x9a7b00,0x9a7f80),(0x9b7e00,0x9b8000))
digest=lambda b:hashlib.sha256(b).hexdigest()
def language():
 raw=LANGUAGE.read_bytes();d=json.loads(raw)
 if digest(raw)!=LANGUAGE_SHA or d['records']!=335 or d['fields']!=1005 or d['changed_strings']!=126 or d['changed_fields']!=378:raise ValueError('Item typography inventory changed')
 return d
def patch(data):
 if digest(data)!=BASE_SHA:raise ValueError('Complete 0.2.27 baseline changed')
 e=Elf(data);d=language();out=bytearray(data);blocks=[];changed={};expected={};fields=[];addresses={};index=0;start,end=RANGES[0];payload=bytearray();widths=json.loads((ROOT/'work/output/v0.2.27/build_info.json').read_text('utf8'))['font_widths']
 for start0,end0 in RANGES:
  if e.at(start0,end0-start0)!=bytes(end0-start0):raise ValueError('Typography pool occupied')
 for t in d['tables']:
  if digest(e.at(t['va'],t['size']))!=t['sha256']:raise ValueError('Native item table changed')
 def flush():
  if payload:out[e.offset(start):e.offset(start)+len(payload)]=payload;blocks.append(dict(va=start,size=len(payload),sha256=digest(payload)))
 for r in d['rows']:
  raw=r['before'].encode('cp932')+b'\0'
  if digest(raw)!=r['sha256'] or e.at(r['pointer'],r['size'])!=raw or r['en']!=r['before'].translate(MAP):raise ValueError('Typography source or exact mapping changed')
  if r['en']==r['before']:addresses[r['pointer']]=r['pointer'];continue
  new=r['en'].encode('cp932')+b'\0'
  if start+len(payload)+len(new)>end:
   flush();index+=1
   if index>=len(RANGES):raise ValueError('Typography relocation pool exhausted')
   start,end=RANGES[index];payload=bytearray()
  ptr=start+len(payload);payload.extend(new);addresses[r['pointer']]=ptr
  for f in r['refs']:
   if e.at(f['site'],4)!=struct.pack('<I',r['pointer']):raise ValueError('Name reference changed')
   struct.pack_into('<I',out,e.offset(f['site']),ptr);expected[hex(f['site'])]=hex(r['pointer']);changed[hex(f['site'])]=hex(ptr)
   fields.append(dict(**f,pointer=ptr,en=r['en']))
 flush()
 return bytes(out),dict(language_sha256=LANGUAGE_SHA,records=335,inspected_name_fields=1005,distinct_labels=len(d['rows']),changed_strings=126,changed_name_fields=len(fields),fields=fields,addresses={hex(k):hex(v)for k,v in addresses.items()},payloads=blocks,patched_words=changed,expected_words=expected,font=dict(size=[26,26],style='Existing proportional English ASCII glyphs; remove mixed legacy fullwidth Latin/digits/punctuation.',renderer_code='Unchanged',reward_geometry='Unchanged',reported_label='HM Parts LvB',reported_width=sum(widths[ord(c)]+2 for c in'HM Parts LvB')),scope=d['scope'])
def inputs():
 data,packs,overlays,report=prior.inputs();data,typo=patch(data);return data,packs,overlays,dict(report,item_typography=typo)
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');a=ap.parse_args();old=ROOT/'work/output/v0.2.27';data,typo=patch((old/'SLPS_250.70').read_bytes());info=json.loads((old/'build_info.json').read_text('utf8'));print(json.dumps(dict(version='0.2.28',elf_sha256=digest(data),records=335,changed_strings=126,changed_fields=typo['changed_name_fields'],payloads=typo['payloads'],font=typo['font']),indent=1),flush=True)
 if not a.write:print('DRY no game files written.');return
 dest=ROOT/'work/output/v0.2.28';dest.mkdir(exist_ok=False);(dest/'SLPS_250.70').write_bytes(data)
 for pattern in('*.pack','*.evemap'):
  for f in old.glob(pattern):shutil.copyfile(f,dest/f.name)
 image=dest/'Sunrise Eiyuutan 2 EN v0.2.28.iso';shutil.copyfile(old/'Sunrise Eiyuutan 2 EN v0.2.27.iso',image);rec=next(x for x in records(image)if x['path']=='/SLPS_250.70')
 if rec['size']!=len(data):raise ValueError('Same-size ELF required')
 with image.open('r+b')as f:f.seek(rec['lba']*2048);f.write(data)
 info.update(version='0.2.28',based_on='0.2.27',item_typography=typo,elf_sha256=digest(data),iso_path=str(image),iso_size=image.stat().st_size,scope='Consistent English glyphs in all six item-name tables; 335 records inventoried, 126 affected strings and 378 name pointers normalized. Original font size, reward frame/rows, descriptions and all 0.2.27 content retained.',in_game_validation='pending focused native item reward preview')
 for k in('iso_sha256','native_validation_report'):info.pop(k,None)
 (dest/'build_info.json').write_text(json.dumps(info,indent=1)+'\n','utf8');print('WRITE',image)
if __name__=='__main__':main()
