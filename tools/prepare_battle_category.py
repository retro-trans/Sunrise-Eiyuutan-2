"""Freeze all reviewed battle barks and the remaining native input formats."""
import argparse,json,re
from elf import ROOT,PATH,Elf
from textcodec import controls,encode
import hashlib

DEST=ROOT/'work/translation/en/battle-category.en.json'
sha=lambda b:hashlib.sha256(b).hexdigest()

def collect():
 src=json.loads((ROOT/'work/source/text/00022_10512.json').read_text('utf8'))['rows'];mainfile=ROOT/'work/translation/en/dat/00022_10512.en.json';main=json.loads(mainfile.read_text('utf8'))['rows'];holdsfile=ROOT/'work/source/battle_holds_audit_025.json';namesfile=ROOT/'work/source/battle_names_ui_audit_025.json';holds=json.loads(holdsfile.read_text('utf8'));names=json.loads(namesfile.read_text('utf8'));rows={}
 for r in main:
  review=r['review']
  if review['accuracy']!='independent-reviewed'or review['editorial']!='self-reviewed'or review['proofread']!='self-reviewed':raise ValueError('Unreviewed MAIN language')
  rows[r['id']]=dict(id=r['id'],source_sha256=r['source_sha256'],en=r['en'],language_evidence='Reviewed MAIN accuracy/editorial/glossary/final proof; wording unchanged.')
 for r in holds['rows']:
  if r['recommended_en'] is not None:rows[r['id']]=dict(id=r['id'],source_sha256=r['source_sha256'],en=r['recommended_en'],language_evidence='Independent025 held-row source review; exact existing English retained.')
 extra=holds['extra_editorial_recommendation'];rows[extra['id']].update(en=extra['recommended_en'],language_evidence='Independent025 source/editorial review removes repeated locative scaffolding; all images, clauses and glossary names retained.')
 for r in names['battle_candidates']:
  rows[r['id']]=dict(id=r['id'],source_sha256=r['source_sha256'],en=r['en'],language_evidence='Independent025 registered-name/source/editorial/proof audit; macron preserved, no ASCII fallback.')
 for i,r in rows.items():
  original=src[i]
  if r['source_sha256']!=original['sha256']or sha(encode(original['jp']))!=original['sha256']or controls(r['en'])!=controls(original['jp']):raise ValueError('Source or control guard failed'+str(i))
  if re.search('[\u3040-\u30ff\u3400-\u9fff]',r['en']):raise ValueError('Untranslated language'+str(i))
 unresolved=[dict(id=r['id'],source_sha256=r['source_sha256'],reason=r['reason'])for r in holds['rows']if r['recommended_en'] is None]
 if set(rows)|{r['id']for r in unresolved}!=set(range(6519)):raise ValueError('Complete source inventory not accounted for')
 e=Elf(PATH.read_bytes());ui=[]
 for r in names['ui_rows']:
  ui.append(r)
 return dict(version='0.2.25',source_table='00022_10512',identical_alias='04971_11849',source_rows=6519,translated_rows=len(rows),held_rows=len(unresolved),review=dict(accuracy='independent-reviewed',editorial='complete-existing-plus025-recheck',glossary='complete-registered-spellings',proofreading='complete-existing-plus025-recheck'),inputs=dict(main_sha256=sha(mainfile.read_bytes()),held_audit_sha256=sha(holdsfile.read_bytes()),names_ui_audit_sha256=sha(namesfile.read_bytes())),rows=[rows[i]for i in sorted(rows)],unresolved=unresolved,ui=ui)

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');a=ap.parse_args();d=collect();print(json.dumps(dict(translated=d['translated_rows'],held=d['held_rows'],examples=[r for r in d['rows']if r['id']in(949,2244,3272,5328,5329,5641)],ui=d['ui']),indent=1),flush=True)
 if not a.write:print('DRY no language snapshot written.');return
 if DEST.exists():raise FileExistsError(DEST)
 DEST.write_text(json.dumps(d,ensure_ascii=False,indent=1)+'\n','utf8');print('WRITE',DEST,'SHA256',sha(DEST.read_bytes()))

if __name__=='__main__':main()
