"""Publish English-only v0.2.21 manifest and validation summary; dry by default."""
import argparse,hashlib,json
from elf import ROOT
import battle_readability_patch as b

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');a=ap.parse_args()
 folder=ROOT/'work/output/v0.2.21';info=json.loads((folder/'build_info.json').read_text('utf8'));rows=b.language()['rows']
 manifest=dict(version='0.2.21',table='04970_10511',review=dict(accuracy='independent-reviewed',editorial='complete',glossary='complete',proofreading='complete'),language_sha256=b.LANGUAGE_SHA,rows=[{k:r[k]for k in ('id','en','source_sha256')}for r in rows])
 print(json.dumps(dict(mode='write'if a.write else 'dry',export_rows=len(rows),sample=manifest['rows'][2],font=info['battle_readability']['selector_font'],destinations=['docs/battle_readability_0.2.21.en.json','docs/battle_readability_0.2.21.json']),indent=1))
 if not a.write:return
 verification=json.loads((folder/'verification.json').read_text('utf8'));native=json.loads((folder/'native_validation.json').read_text('utf8'));tests=(folder/'test_results.txt').read_text('utf8')
 if 'Ran 40 tests'not in tests or not tests.rstrip().endswith('OK'):raise ValueError('Complete40-test passing result required')
 image=folder/'Sunrise Eiyuutan 2 EN v0.2.21.iso';h=hashlib.sha256()
 with image.open('rb')as f:
  while block:=f.read(4*1024*1024):h.update(block)
 digest=h.hexdigest();info.update(iso_sha256=digest,native_validation_report='work/output/v0.2.21/native_validation.json',in_game_validation='Fresh final ISO boot verifies32 changed words/128 font metric bytes; affected battle panels not replayed; captured transition is not visual approval.')
 report=dict(version='0.2.21',date='2026-11-05',based_on='0.2.20',iso_sha256=digest,iso_size=image.stat().st_size,elf_sha256=info['elf_sha256'],review=manifest['review'],review_checkpoint='docs/review_field172_parent174.json',fresh_accuracy_report='work/field04970_accuracy_20261105.json',glossary=dict(entries=1705,registered_variants=24,changes=0,sha256=b.digest((ROOT/'work/glossary/glossary.json').read_bytes())),proofreading=dict(examined_rows=172,changed_rows=[]),tests=dict(passed=40,log='work/output/v0.2.21/test_results.txt',selector_scenarios=24),verification=verification,native_validation=native,battle_readability=info['battle_readability'],remaining_limit='Normal-gameplay replay of the reported battle windows; unrelated incomplete battle-bank dialogue remains outside this increment.')
 for path,obj in ((ROOT/'docs/battle_readability_0.2.21.en.json',manifest),(ROOT/'docs/battle_readability_0.2.21.json',report),(folder/'build_info.json',info)):
  if path.name!='build_info.json'and path.exists():raise FileExistsError(path)
  path.write_text(json.dumps(obj,indent=1)+'\n','utf8')
 print('Saved English manifest and validation report; ISO SHA256',digest)

if __name__=='__main__':main()
