"""Save English-only battle effects export and final validation; dry by default."""
import argparse,hashlib,json
from elf import ROOT
import battle_effects_patch as b

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');a=ap.parse_args();folder=ROOT/'work/output/v0.2.22';d=b.language();info=json.loads((folder/'build_info.json').read_text('utf8'))
 native_folder=ROOT/'work/ui/battle-effects-preview-0.2.22-r2';native=json.loads((native_folder/'native_validation.json').read_text('utf8'));tests=(folder/'test_results.txt').read_text('utf8')
 if 'Ran 47 tests'not in tests or not tests.rstrip().endswith('OK'):raise ValueError('Complete47-test passing log required')
 if not native['complete']or len(native['panels'])!=3 or not native['settings_restored_exactly']:raise ValueError('Complete native previews/settings restoration required')
 print(json.dumps(dict(mode='write'if a.write else'dry',objects=65,translated=63,records=31,checks=47,native_panels=[r['label']for r in native['panels']],sample=next(r['en']for r in d['rows']if r['va']==0x22af90)),indent=1))
 if not a.write:return
 image=folder/'Sunrise Eiyuutan 2 EN v0.2.22.iso';h=hashlib.sha256()
 with image.open('rb')as f:
  while raw:=f.read(4*1024*1024):h.update(raw)
 sha=h.hexdigest();verification=json.loads((folder/'verification.json').read_text('utf8'))
 info.update(iso_sha256=sha,in_game_validation='Fresh cold native previews visually pass phase ability, longest comment and reward getter/window; synthetic fixtures, not ordinary battle triggers.',native_validation_report='work/ui/battle-effects-preview-0.2.22-r2/native_validation.json')
 report=dict(version='0.2.22',date='2026-11-05',iso_sha256=sha,iso_size=image.stat().st_size,elf_sha256=info['elf_sha256'],language_sha256=b.LANGUAGE_SHA,language_review=d['review'],qualifications=d['qualifications'],glossary=d['name_audit'],tests=dict(passed=47,log='work/output/v0.2.22/test_results.txt'),verification=verification,native_validation=native,native_preview_build=json.loads((native_folder/'build_info.json').read_text('utf8')),earlier_preview_attempt=json.loads((ROOT/'work/ui/battle-effects-preview-0.2.22/native_validation.json').read_text('utf8')),visual_inspection=dict(examined_panels=3,clipping=False,complete_wording=True,normal_font=True,portrait_size_retained=True),battle_effects=info['battle_effects'],remaining_limit='Ordinary battle trigger replay and unrelated incomplete battle-bank dialogue.')
 for path,obj in((ROOT/'docs/battle_effects_0.2.22.en.json',d),(ROOT/'docs/battle_effects_0.2.22.json',report),(folder/'build_info.json',info)):
  if path.name!='build_info.json'and path.exists():raise FileExistsError(path)
  path.write_text(json.dumps(obj,indent=1)+'\n','utf8')
 print('Saved reports; ISO SHA256',sha)

if __name__=='__main__':main()
