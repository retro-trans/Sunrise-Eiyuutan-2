"""Document formation text/layout completion and exact prior-disc retention."""
import argparse,json,hashlib
from pathlib import Path
from elf import ROOT
from iso import records
import formation_readability_patch as b
def sha_file(path):
 h=hashlib.sha256()
 with path.open('rb')as f:
  while raw:=f.read(8*1024*1024):h.update(raw)
 return h.hexdigest()
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');a=ap.parse_args();folder=ROOT/'work/output/v0.2.29';info=json.loads((folder/'build_info.json').read_text('utf8'));verify=json.loads((folder/'verification.json').read_text('utf8'));nf=ROOT/'work/ui/formation-readability-0.2.29/attempt-4/native_validation.json';native=json.loads(nf.read_text('utf8'));data=(folder/'SLPS_250.70').read_bytes();d=b.language();expected_data,ui=b.patch((ROOT/'work/output/v0.2.28/SLPS_250.70').read_bytes())
 if data!=expected_data:raise ValueError('Reconstructed final executable differs')
 info['formation_readability']=ui
 if not native['complete']or not native['settings_restored_exactly']or len(native['screens'])!=4 or verify['files_verified']!=20 or b.digest(data)!=info['elf_sha256']:raise ValueError('Focused verification incomplete')
 image=Path(info['iso_path']);previous=ROOT/'work/output/v0.2.28/Sunrise Eiyuutan 2 EN v0.2.28.iso';oldinfo=json.loads((previous.parent/'build_info.json').read_text('utf8'));rec=next(r for r in records(image)if r['path']=='/SLPS_250.70');begin=rec['lba']*2048;end=begin+rec['size'];expected=hashlib.sha256();priorhash=hashlib.sha256();pos=0
 if image.stat().st_size!=previous.stat().st_size or rec['size']!=len(data):raise ValueError('Same-size disc replacement required')
 with previous.open('rb')as f:
  while raw:=f.read(8*1024*1024):
   priorhash.update(raw);block=bytearray(raw);lo=max(begin,pos);hi=min(end,pos+len(block))
   if lo<hi:block[lo-pos:hi-pos]=data[lo-begin:hi-begin]
   expected.update(block);pos+=len(block)
 digest=sha_file(image)
 if digest!=expected.hexdigest()or priorhash.hexdigest()!=oldinfo['iso_sha256']:raise ValueError('Disc differs beyond exact executable replacement')
 report=dict(version='0.2.29',date='2026-11-05',based_on='0.2.28',iso_sha256=digest,elf_sha256=info['elf_sha256'],language_sha256=b.LANGUAGE_SHA,review=d['review_order'],qualifications=d['qualifications'],patch=info['formation_readability'],tests=dict(passed=5,scope='All 99 real class getters and 364 non-player captain full/display getters plus static menu pointers; complete machine/device label fit with preserved row IDs/arguments; right-panel class/size/stat fit including restored native trailing padding and preserved colors; actual saved-fp machine/device list formatters; exact allowed executable delta and protected player/normal-help geometry.'),native=native,initial_previews=dict(paths=[str(nf.parent.parent/'native_validation.json'),str(nf.parent.parent/'attempt-2/native_validation.json'),str(nf.parent.parent/'attempt-3/native_validation.json')],candidate=str(ROOT/'work/output/preflight-v0.2.29-r1'),scope='Fixture 1 left constructor-hidden upper/detail windows hidden. Fixture 2 exposed the panel and revealed invisible trailing class padding causing unnecessary shrinkage. Production fitting now measures only the visible caption and restores all erasure padding before native drawing. Fixture 3 confirmed the corrected production helper; fixture 4 also matches the original list constructor mode and 224-pixel height. All preflight executable and screenshot evidence preserved.'),disc_verification=verify,disc_delta=dict(previous_sha256=priorhash.hexdigest(),expected_replacement_sha256=expected.hexdigest(),outside_executable='Every byte equals v0.2.28.'),limitations=['Four native fixtures use synthetic stack-local deck/list data after New Game initialization; the original unlocked formation route and full progression were not replayed.','Rare long list labels use a smaller uniform square font (minimum 10) to preserve complete wording within the original list width.','Armored Warrior is a qualified literal class caption; Naza retains the project provisional spelling supported by the same pilot/name variant.','Inherited 56 unresolved battle-dialogue lines and previous startup automation limitations remain.'])
 print(json.dumps(dict(version='0.2.29',class_records=33,captain_records=183,reviewed_objects=372,tests=5,native_panels=4,iso_sha256=digest,right_panel_width=312,normal_help_geometry='unchanged',outside_executable='exact v0.2.28',outputs=['build_info.json','ISO.sha256','docs/formation_readability_0.2.29.md/json','CHANGELOG.md']),indent=1),flush=True)
 if not a.write:print('DRY no reports or metadata written.');return
 log=ROOT/'CHANGELOG.md';old=log.read_text('utf8');heading='## v0.2.29 — formation fonts, stats and remaining text — 2026-11-05'
 if heading in old or not old.startswith('# Changelog\n\n'):raise ValueError('Changelog changed')
 info.update(iso_sha256=digest,native_validation_report=str(nf),in_game_validation='Four native formation previews pass using the real window constructor/cleanup and Munit, Dunit, Captain and static menu consumers. Synthetic stack-local deck/list data after New Game. Original unlocked route/full progression remain unverified.')
 (folder/'build_info.json').write_text(json.dumps(info,indent=1)+'\n','utf8');(folder/'Sunrise Eiyuutan 2 EN v0.2.29.iso.sha256').write_text(digest+'  Sunrise Eiyuutan 2 EN v0.2.29.iso\n','ascii');(ROOT/'docs/formation_readability_0.2.29.json').write_text(json.dumps(report,indent=1)+'\n','utf8')
 pictures=[Path(s['screen']).as_posix()for s in native['screens']]
 doc=f"""# v0.2.29: formation fonts, stats and remaining text

The reported unit and equipment lists no longer use horizontally compressed 14×26 lettering. Five related list callers now request a normal **26×26 proportional font**, uniformly reduced only when a complete label needs more room. Fixed byte-padding in four shared `name / Sz` formats is replaced with two spaces; names, values, item/unit IDs, numeric formats, row IDs, row pitch and selection semantics remain intact. The long machine-equipment picker uses the same uniform-fitting path rather than its older 11×26 fallback. No wording is abbreviated or truncated. Rare long captions can use a square size as small as 10; the reported short labels retain 26×26.

The unit stats panel grows from **256 to 312 pixels wide**, retaining x=316, y=100 and height=224. Its right edge is 628. The class heading, size field and stat rows use the normal English proportions with complete per-line fitting. The size field moves to x=244 inside the panel, leaving 228 pixels for the complete class caption and 64 pixels for size. The unit size caption reuses the existing English `Sz` format. Class fitting excludes native trailing erasure spaces from measurement, then restores those exact bytes before drawing. This keeps Flying Trooper at 26×26 while preserving native clearing behavior. Rows fit within the remaining 308-pixel text area, including their existing indentation. HPMax, terrain/range, ENMax, launch EN, S/L/P and attack/defense/special lines retain their original arguments and values. The ordinary bottom dialogue/help frame and portrait size do not change.

All **33 unit-type records** are translated across their **99 full/display/omission fields**, including **Flying Trooper**. The **183 captain records** resolve through the pilot table; all related **364 non-player full/display fields** use reviewed English, including **Rie Akatsuki**. The two player fields retain their exact original pointers and dynamic name handling. Short dialogue name fields and the captain gameplay records remain untouched. The previously missed static submenu pointers now display **Ship** and **Captain**, preserving the Captain caption's source-significant surrounding spaces.

The text audit examines all **372 distinct source objects**: 83 class targets, 287 captain name targets and two submenu captions. Existing independently reviewed compiled translations are retained. Missing phonetic aliases are bound to their exact same-record full or short captions; generic class/role labels receive separate source accuracy, editorial and proofreading. No character gender is inferred. Armored Warrior is a literal project caption rather than an asserted official English term; Naza retains its explicitly provisional project spelling. Complete source guards, record relations and qualifications remain in the ignored source audit and English snapshot.

English strings already loaded elsewhere are reused. New complete strings occupy 1,931 bytes in proven zero tails of prior constant-text pools. A 768-byte reserved code block contains the small fitting wrappers. The original strings are preserved. Five focused tests execute all native class and non-player captain name getters, fit all related machine/device labels while preserving row arguments, fit class/size/stat combinations with exact colors and restored padding, execute the saved-fp machine/device formatters, and restore every allowed change to require a byte-exact v0.2.28 executable. The dynamic player record and normal help constructors remain exact.

Four cold muted previews exercise the real formation window constructor/cleanup, MunitList/MunitInfo, DunitList/DunitInfo, Ship/Captain menu and CaptainList/CaptainInfo. Stack-local deck entries and list IDs are synthetic after New Game initialization. These previews verify the native consumers and appearance; they do not replay the original unlocked formation route or certify full story progression. Settings are restored exactly. Three earlier preview sets and the initial candidate are preserved: the first fixture omitted window visibility setup, the second exposed the trailing-padding fit issue fixed in the final candidate, and the third confirmed that correction before the fixture's list constructor was matched to the original mode and 224-pixel height.

![Unit list, translated type and widened stats](<{pictures[0]}>)

![Equipment list with normal proportions](<{pictures[1]}>)

![Ship and Captain submenu](<{pictures[2]}>)

![Rie Akatsuki captain detail](<{pictures[3]}>)

Full disc verification covers 20 files, 5,614 resource packs, 80 event members and 489 movies. Whole-image hashing proves every byte outside the executable equals v0.2.28. Prior item-font corrections, save/load titles, subtitles, songs and original audio remain intact. The inherited 56 battle-dialogue holds and previous startup automation limitations remain documented.

ISO SHA-256: `{digest}`

ELF SHA-256: `{info['elf_sha256']}`

Restart the game and load a normal memory-card save. Older emulator savestates contain old pointers and UI code. No release or commit was made.
"""
 (ROOT/'docs/formation_readability_0.2.29.md').write_text(doc,'utf8');entry=heading+'\n\n- Restore normal text proportions in five formation list consumers; preserve complete labels with uniform fitting and replace byte-padding with compact spacing in four name/size formats.\n- Widen the unit stats panel from 256 to 312 pixels, separate class and size fields and fit full stat lines. Exclude invisible class erasure padding from measurement while restoring it before drawing. Normal dialogue/help box and portrait geometry remain unchanged.\n- Translate all 33 unit-type records, 364 non-player captain full/display name references and the missed Ship/Captain submenu pointers. Preserve dynamic player names and qualified/provisional terminology.\n- Five focused checks, four actual native formation fixtures and full disc verification pass. Synthetic deck/list data; original unlocked route/full progression remain unverified. Preflight evidence retained. All ISO bytes outside the executable equal v0.2.28. See docs/formation_readability_0.2.29.md/json.\n\n';log.write_text('# Changelog\n\n'+entry+old[len('# Changelog\n\n'):],'utf8');print('Formation readability reports and changelog written.')
if __name__=='__main__':main()
