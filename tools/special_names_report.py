"""Package focused special-name evidence, checksum and changelog."""
import argparse,json,hashlib
from pathlib import Path
from elf import ROOT
from iso import records
import special_names_patch as b

def sha_file(path):
 h=hashlib.sha256()
 with path.open('rb')as f:
  while block:=f.read(8*1024*1024):h.update(block)
 return h.hexdigest()

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');a=ap.parse_args();folder=ROOT/'work/output/v0.2.26';info=json.loads((folder/'build_info.json').read_text('utf8'));verify=json.loads((folder/'verification.json').read_text('utf8'));nf=ROOT/'work/ui/special-names-0.2.26/native_validation.json';native=json.loads(nf.read_text('utf8'));d=b.language();data=(folder/'SLPS_250.70').read_bytes()
 if not native['complete']or not native['settings_restored_exactly']or len(native['screens'])!=6 or verify['files_verified']!=20 or b.digest(data)!=info['elf_sha256']:raise ValueError('Focused verification incomplete')
 image=Path(info['iso_path']);previous=ROOT/'work/output/v0.2.25/Sunrise Eiyuutan 2 EN v0.2.25.iso';oldinfo=json.loads((previous.parent/'build_info.json').read_text('utf8'));rec=next(r for r in records(image)if r['path']=='/SLPS_250.70');begin=rec['lba']*2048;end=begin+rec['size'];expected=hashlib.sha256();priorhash=hashlib.sha256();pos=0
 if image.stat().st_size!=previous.stat().st_size or rec['size']!=len(data):raise ValueError('Same-size disc replacement required')
 with previous.open('rb')as f:
  while raw:=f.read(8*1024*1024):
   priorhash.update(raw);block=bytearray(raw);lo=max(begin,pos);hi=min(end,pos+len(block))
   if lo<hi:block[lo-pos:hi-pos]=data[lo-begin:hi-begin]
   expected.update(block);pos+=len(block)
 digest=sha_file(image)
 if digest!=expected.hexdigest()or priorhash.hexdigest()!=oldinfo['iso_sha256']:raise ValueError('Disc differs beyond the exact new executable')
 report=dict(version='0.2.26',date='2026-11-05',based_on='0.2.25',iso_sha256=digest,elf_sha256=info['elf_sha256'],category=dict(records=118,distinct_labels=50,full_display_omission_fields=354,unresolved_in_this_category=0),language_sha256=b.LANGUAGE_SHA,language_inputs=d['inputs'],language_review=d['review'],patch=info['special_names'],tests=dict(passed=3,scope='All 354 actual native getters, all 118 omission labels through the actual selector instructions on both sides (236 cases), and exact permitted executable changes only.'),native=native,disc_verification=verify,disc_delta=dict(previous_sha256=priorhash.hexdigest(),expected_replacement_sha256=expected.hexdigest(),outside_executable='Byte-exact whole-image SHA guard; all resources, event overlays, movies, audio, directory records and padding retained.'),limitations=['Six native selector previews use synthetic one-choice lists and side flags after New Game initialization; original battle triggers and a full playthrough are unverified.','Normal dialogue/help geometry and all gameplay words outside the name pointers and five selector layout/font instructions remain byte-exact 0.2.25.','The 56 prior unresolved battle dialogue lines and prior startup automation limitations remain as recorded in docs/battle_category_0.2.25.md. This focused selector validation does not resolve those.','Mighty Sword and Large Scythe are independently checked literal captions, not asserted official English named attacks.','Only the native omission field abbreviates Omnidirectional to Omni.; full/display names remain complete. Registered V-MAX typography is normalized after language review.'])
 print(json.dumps(dict(version='0.2.26',names=50,records=118,fields=354,payload_bytes=757,selector_previews=6,tests=3,iso_sha256=digest,outside_executable='exact previous image',outputs=['build_info.json','ISO.sha256','docs/special_names_0.2.26.md/json','CHANGELOG.md']),indent=1),flush=True)
 if not a.write:print('DRY no documentation or metadata written.');return
 log=ROOT/'CHANGELOG.md';old=log.read_text('utf8');heading='## v0.2.26 — special-attack names and readable selector — 2026-11-05'
 if heading in old or not old.startswith('# Changelog\n\n'):raise ValueError('Changelog changed')
 info.update(iso_sha256=digest,native_validation_report=str(nf),in_game_validation='Six native special-name selector previews pass: actual getters, font, measurement, selection and cleanup; synthetic one-choice list and side flags. Both sides checked. Original battle triggers and full progression unverified; inherited 0.2.25 limitations retained.')
 (folder/'build_info.json').write_text(json.dumps(info,indent=1)+'\n','utf8');(folder/'Sunrise Eiyuutan 2 EN v0.2.26.iso.sha256').write_text(digest+'  Sunrise Eiyuutan 2 EN v0.2.26.iso\n','ascii');(ROOT/'docs/special_names_0.2.26.json').write_text(json.dumps(report,indent=1)+'\n','utf8')
 pictures={s['phase']:Path(s['screen']).as_posix()for s in native['screens']}
 doc=f"""# v0.2.26: special-attack names and readable selector

The reported label is **Pile Bunker Surprise Attack**. All **118 special-attack records** are inventoried, with **50 distinct captions** translated in all **354 full/display/omission name fields**. No untranslated label remains in this table. Existing independently reviewed compiled language is reused. Nine missing captions received a separate source/context accuracy review, editorial pass and proofreading; that audit examined every record and name variant. Registered names are retained. V-MAX uses its registered ASCII typography. Mighty Sword and Large Scythe are scoped literal captions rather than claims of canonical named English attacks.

The special selector now uses a **26 × 26 proportional font**, replacing its horizontally compressed 13 × 26 setting. Its width is 400 pixels, with left/right origins 16 and 224 and the original 28-pixel row pitch. All shortened names measure at most 349 pixels within the 384-pixel text area. Complete names remain in the full/display fields; only Omnidirectional Mega-Particle Cannon becomes **Omni. Mega-Particle Cannon** in the native omission field. The reported name stays complete at 323 pixels. Normal dialogue/help boxes keep their previous size and position.

Three focused checks pass: execute all 354 real native name getters; execute the original selector for all 118 omission names on both sides, verifying font, measurement, centering, selection and geometry; restore every allowed changed interval and require the executable to equal v0.2.25 exactly. Only name pointers, five selector font/layout words and a 757-byte relocated string pool change. Costs, stats, IDs, callbacks, battle logic and voices remain exact.

Six fresh muted native previews pass through the original selector, getters, renderer, measurement, selection and cleanup. They cover the reported label, the abbreviated longest full name, the longest list name, V-MAX typography, the distinct omission caption Full Power, and the mirrored selector. The requests use synthetic one-choice lists and side flags after New Game initialization; original battlefield triggers and full progression are not replayed. Settings are restored exactly.

![Reported attack name with normal font](<{pictures[1]}>)

![Native omission field with complete weapon components](<{pictures[2]}>)

![Longest list name fits](<{pictures[3]}>)

![Mirrored selector](<{pictures[6]}>)

Full disc verification covers 20 files, 5,614 resource packs, 80 event members and 489 movies. A whole-image SHA comparison also proves that every byte outside the executable equals v0.2.25, retaining all translated resources, movie subtitles, lyrics and original audio. The 56 unresolved battle dialogue lines and startup automation limits from [v0.2.25](battle_category_0.2.25.md) remain explicitly unchanged. This is focused selector validation, not a whole-game completion claim.

ISO SHA-256: `{digest}`

ELF SHA-256: `{info['elf_sha256']}`

Use a fresh game boot to load the new executable; an older savestate carries old name pointers and layout code. No release or commit was made.
"""
 (ROOT/'docs/special_names_0.2.26.md').write_text(doc,'utf8');entry=heading+'\n\n- Translate all 50 distinct captions across 118 special-attack records and 354 full/display/omission fields, including Pile Bunker Surprise Attack. Retain registered names and distinct shortened variants; normalize registered V-MAX typography.\n- Restore the special selector to normal 26×26 proportions and widen it to 400 pixels on both sides. Keep full/display names complete; use Omni. only in the native omission field. Original dialogue/help geometry and all costs, stats, IDs, callbacks and voices stay exact.\n- Three focused checks, six actual native selector previews and full disc verification pass. Synthetic one-choice/side fixtures; original battlefield triggers and full progression remain unverified. All ISO bytes outside the executable equal 0.2.25. Inherited 56 dialogue holds and startup automation limits remain documented. See docs/special_names_0.2.26.md/json.\n\n';log.write_text('# Changelog\n\n'+entry+old[len('# Changelog\n\n'):],'utf8');print('Special-name reports and changelog written.')
if __name__=='__main__':main()
