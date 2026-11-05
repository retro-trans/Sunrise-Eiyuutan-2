"""Freeze display-only fullwidth Latin/digit substitutions in item names."""
import argparse,json,struct,hashlib
from elf import ROOT,Elf
TABLES=(('it_devi_info',60,'itdv'),('it_expend_info',40,'itex'),('it_mchdev_info',64,'itmd'),('it_parts_info',32,'itpa'),('it_junk_info',32,'itju'),('it_event_info',16,'itev'))
MAP=str.maketrans({chr(c):chr(c-0xfee0)for c in range(0xff01,0xff5f)})
DEST=ROOT/'work/translation/en/item-typography.en.json'
sha=lambda b:hashlib.sha256(b).hexdigest()
def collect():
 data=(ROOT/'work/output/v0.2.27/SLPS_250.70').read_bytes();e=Elf(data);names={};tables=[]
 for name,stride,prefix in TABLES:
  s=e.symbol(name);count=s['size']//stride
  if s['size']%stride:raise ValueError('Partial item record')
  tables.append(dict(name=name,va=s['va'],size=s['size'],stride=stride,count=count,prefix=prefix,sha256=sha(e.at(s['va'],s['size']))))
  for i in range(count):
   for off in(0,4,8):
    site=s['va']+i*stride+off;ptr=struct.unpack('<I',e.at(site,4))[0];raw=e.at(ptr,512).split(b'\0')[0];text=raw.decode('cp932');r=names.setdefault(ptr,dict(pointer=ptr,before=text,en=text.translate(MAP),size=len(raw)+1,sha256=sha(raw+b'\0'),refs=[]));r['refs'].append(dict(table=name,row=i,field=off,site=site))
 rows=list(names.values());changed=[r for r in rows if r['before']!=r['en']]
 return dict(version='0.2.28',baseline_elf_sha256=sha(data),scope='Display-only normalization of U+FF01..U+FF5E into their exact ASCII counterparts in the three player-facing item-name fields. Preserve case, spelling, spaces, levels, other symbols and all descriptions. No NFKC normalization, source-language change, name edit or editable-name cell change.',review=dict(accuracy='Identical Latin letters/digits/punctuation only; existing approved English retained.',editorial='No wording or spacing changes; consistent English glyphs requested by user.',proofreading='Exact per-character substitution and unchanged unmapped characters checked for every object.'),tables=tables,records=sum(t['count']for t in tables),fields=sum(len(r['refs'])for r in rows),changed_strings=len(changed),changed_fields=sum(len(r['refs'])for r in changed),rows=rows)
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');a=ap.parse_args();d=collect();print(json.dumps(dict(records=d['records'],fields=d['fields'],distinct_labels=len(d['rows']),changed_strings=d['changed_strings'],changed_fields=d['changed_fields'],samples=[dict(before=r['before'],after=r['en'])for r in d['rows']if 'ＨＭ Parts'in r['before']or'Titans Colors ０１'in r['before']]),indent=1),flush=True)
 if not a.write:print('DRY no typography snapshot written.');return
 if DEST.exists():raise FileExistsError(DEST)
 DEST.write_text(json.dumps(d,indent=1)+'\n','utf8');print('WRITE',DEST,'SHA',sha(DEST.read_bytes()))
if __name__=='__main__':main()
