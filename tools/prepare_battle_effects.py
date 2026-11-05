"""Freeze source-reviewed ability/reward language; dry run by default."""
import argparse,json,re,hashlib
from pathlib import Path
from elf import ROOT

SOURCE=Path('C:/Users/Binh/Documents/Codex/2026-10-31/referenced-chatgpt-conversation-this-is-an/work/exskill_accuracy_20261105.json')
SOURCE_SHA='8bd7d72312b31efaff8fcab1cd00d8f2b21ace0d88b3b612dc7040b9d238c80c'
DEST=ROOT/'work/translation/en/battle-effects.en.json'
digest=lambda b:hashlib.sha256(b).hexdigest()

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');a=ap.parse_args()
 raw=SOURCE.read_bytes()
 if digest(raw)!=SOURCE_SHA:raise ValueError('Independent meaning review changed')
 review=json.loads(raw);g=json.loads((ROOT/'work/glossary/glossary.json').read_text('utf8'));aliases={x:e['en']for e in g['entries']for x in e.get('english_variants',[])}
 rows=[]
 for r in review['mapping']:
  text=r['en']
  for alias,target in aliases.items():
   if re.search(r'(?<!\w)'+re.escape(alias)+r'(?!\w)',text):raise ValueError('Registered glossary variant needs explicit correction')
  rows.append(dict(va=r['va'],source_size=r['source_size_including_nul'],source_sha256=r['source_sha256'],en=text,translation_required=r['translation_required'],sites=r['sites'],provenance=r['provenance']))
 obj=dict(source_elf_sha256=review['guarded_inputs'][0]['sha256'],review=dict(accuracy='independent-reviewed',editorial='complete',glossary='complete',proofreading='complete'),rows=rows,qualifications=review['qualifications'],accuracy_report_sha256=SOURCE_SHA,editorial=dict(examined_objects=65,changed=[]),name_audit=dict(entries=len(g['entries']),registered_variants=len(aliases),changes=0,sha256=digest((ROOT/'work/glossary/glossary.json').read_bytes())),proofreading=dict(examined_objects=65,changed=[]))
 print(json.dumps(dict(mode='write'if a.write else 'dry',objects=len(rows),translatable=sum(r['translation_required']for r in rows),name_audit=obj['name_audit'],samples=[r for r in rows if r['va']in(0x22af90,0x232388)]),indent=1))
 if not a.write:return
 if DEST.exists():raise FileExistsError(DEST)
 DEST.write_text(json.dumps(obj,indent=1)+'\n','utf8');print('Saved',DEST,'SHA256',digest(DEST.read_bytes()))

if __name__=='__main__':main()
