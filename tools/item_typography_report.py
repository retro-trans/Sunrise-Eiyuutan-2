"""Package item glyph consistency evidence, checksum and changelog."""
import argparse,json,hashlib
from pathlib import Path
from elf import ROOT
from iso import records
import item_typography_patch as b
def sha_file(path):
 h=hashlib.sha256()
 with path.open('rb')as f:
  while raw:=f.read(8*1024*1024):h.update(raw)
 return h.hexdigest()
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');a=ap.parse_args();folder=ROOT/'work/output/v0.2.28';info=json.loads((folder/'build_info.json').read_text('utf8'));verify=json.loads((folder/'verification.json').read_text('utf8'));nf=ROOT/'work/ui/item-typography-0.2.28/native_validation.json';native=json.loads(nf.read_text('utf8'));data=(folder/'SLPS_250.70').read_bytes();d=b.language()
 if not native['complete']or not native['settings_restored_exactly']or len(native['screens'])!=2 or verify['files_verified']!=20 or b.digest(data)!=info['elf_sha256']:raise ValueError('Focused verification incomplete')
 image=Path(info['iso_path']);previous=ROOT/'work/output/v0.2.27/Sunrise Eiyuutan 2 EN v0.2.27.iso';oldinfo=json.loads((previous.parent/'build_info.json').read_text('utf8'));rec=next(r for r in records(image)if r['path']=='/SLPS_250.70');begin=rec['lba']*2048;end=begin+rec['size'];expected=hashlib.sha256();priorhash=hashlib.sha256();pos=0
 if image.stat().st_size!=previous.stat().st_size or rec['size']!=len(data):raise ValueError('Same-size disc replacement required')
 with previous.open('rb')as f:
  while raw:=f.read(8*1024*1024):
   priorhash.update(raw);block=bytearray(raw);lo=max(begin,pos);hi=min(end,pos+len(block))
   if lo<hi:block[lo-pos:hi-pos]=data[lo-begin:hi-begin]
   expected.update(block);pos+=len(block)
 digest=sha_file(image)
 if digest!=expected.hexdigest()or priorhash.hexdigest()!=oldinfo['iso_sha256']:raise ValueError('Disc differs beyond exact executable replacement')
 report=dict(version='0.2.28',date='2026-11-05',based_on='0.2.27',iso_sha256=digest,elf_sha256=info['elf_sha256'],language_sha256=b.LANGUAGE_SHA,review=d['review'],patch=info['item_typography'],tests=dict(passed=4,scope='Execute all 1005 real native full/display/omit item getters across six tables; reported generic item dispatch and nine-item reward pagination/quantity/grants; exact character mapping with nonincreasing rendered widths; exact allowed executable delta.'),native=native,disc_verification=verify,disc_delta=dict(previous_sha256=priorhash.hexdigest(),expected_replacement_sha256=expected.hexdigest(),outside_executable='Every byte equals v0.2.27.'),limitations=['Native reward previews use synthetic item lists after New Game initialization; original victory triggers and physical saves not replayed.','Full progression remains unverified; inherited 56 battle dialogue holds and startup automation limitations remain.','This typography pass changes the three player-facing item-name fields only. Existing descriptions and unrelated editable-name cells are deliberately unchanged.'])
 print(json.dumps(dict(version='0.2.28',item_records=335,name_fields_examined=1005,changed_labels=126,changed_fields=378,tests=4,native_panels=2,iso_sha256=digest,renderer_and_box_layout='byte-exact v0.2.27',outside_executable='exact v0.2.27',sample='HM Parts LvB',outputs=['build_info.json','ISO.sha256','docs/item_typography_0.2.28.md/json','CHANGELOG.md']),indent=1),flush=True)
 if not a.write:print('DRY no reports or metadata written.');return
 log=ROOT/'CHANGELOG.md';old=log.read_text('utf8');heading='## v0.2.28 — consistent item-name font — 2026-11-05'
 if heading in old or not old.startswith('# Changelog\n\n'):raise ValueError('Changelog changed')
 info.update(iso_sha256=digest,native_validation_report=str(nf),in_game_validation='Two native Acquired Items previews pass: exact reported HM Parts LvB ×4 / Repair Materials Lv2 ×1, and related class/level/code labels. Actual getters, formatter, renderer, input, cleanup and grants; synthetic rewards after New Game initialization. Full victory-trigger replay unverified.')
 (folder/'build_info.json').write_text(json.dumps(info,indent=1)+'\n','utf8');(folder/'Sunrise Eiyuutan 2 EN v0.2.28.iso.sha256').write_text(digest+'  Sunrise Eiyuutan 2 EN v0.2.28.iso\n','ascii');(ROOT/'docs/item_typography_0.2.28.json').write_text(json.dumps(report,indent=1)+'\n','utf8')
 pictures=[Path(s['screen']).as_posix()for s in native['screens']]
 doc=f"""# v0.2.28: consistent item-name font

The pictured HM parts caption mixed the original fullwidth Latin glyphs with the proportional English font. Its visible size, spacing, stroke and style consequently differed within the same label. It now reads **HM Parts LvB** entirely in the same English glyphs as **Repair Materials Lv2**. The native reward renderer remains at its original default size (26-pixel cells), so the existing English style and apparent size match across both labels. No new font face or image overlay is introduced.

This pass inventories all **335 item records** in six native tables and all **1,005 full/display/omission name pointers**, covering 349 distinct stored labels. It converts **126 affected labels** across **378 pointers**. The mapping changes only fullwidth ASCII-range characters U+FF01..U+FF5E into the exact corresponding ASCII characters. Case, spelling, spaces, class letters, levels, leading zeros and nonmapped symbols remain exact. Descriptions, editable-name cells and internal item IDs are unchanged. No broad Unicode normalization or wording edits are applied.

All changed strings are relocated into 1,598 bytes of proven free mapped memory. Original English objects stay intact. Only the 378 name-pointer words and the new pools change; renderer instructions, font atlas, costs, stats, inventory IDs, item grants, quantities and every box's geometry remain byte-exact v0.2.27. The Acquired Items frame, 28-pixel row pitch, native quantity format and pagination are unchanged. Every normalized label measures no wider than before; the reported name is 150 pixels at normal size.

Four focused tests pass. They execute all 1,005 real native item-name getters, execute the reported generic item dispatch and a nine-item reward sequence across two pages with exact quantities/grants, check exact per-character substitutions and nonincreasing proportional widths for all 349 labels, and restore all allowed changes to require a byte-exact v0.2.27 executable. The reward sequence keeps the original white color and renderer path.

Two muted cold native previews exercise the actual reward constructor, item dispatch/getters, formatter, renderer, wait, cleanup and in-memory inventory grants. The first uses the screenshot's exact pair and counts: HM Parts LvB ×4 and Repair Materials Lv2 ×1. The second checks related class, level and code labels alongside the unchanged Repair Materials caption. These are synthetic reward lists after New Game initialization; original victory triggers and physical saves are not replayed. The private preview patches are absent from delivery, and emulator settings are restored exactly.

![Reported acquired items with matching English glyphs](<{pictures[0]}>)

![Related class, level and code labels](<{pictures[1]}>)

Full disc verification covers 20 files, 5,614 resource packs, 80 event members and 489 movies. Whole-image hashing proves every byte outside the executable equals v0.2.27. Prior translations, save/load titles, movie/preview subtitles, romaji/English song subtitles and original voices remain intact. The inherited 56 battle-dialogue holds and previous startup automation limitations remain; this is focused reward UI validation rather than a full playthrough claim.

ISO SHA-256: `{digest}`

ELF SHA-256: `{info['elf_sha256']}`

Restart the game to load the new executable and use the normal memory-card load menu. Older emulator savestates contain old pointers and text. No release or commit was made.
"""
 (ROOT/'docs/item_typography_0.2.28.md').write_text(doc,'utf8');entry=heading+'\n\n- Replace mixed legacy fullwidth Latin/digits/punctuation with matching proportional English glyphs in item names. HM Parts LvB now matches Repair Materials Lv2 in style and apparent size. Inventory all 335 records/1,005 name pointers; normalize 126 captions across 378 full/display/omission fields.\n- Preserve all wording, case, spaces, class/level values, item IDs and descriptions. Original reward renderer, font size, frame, rows, quantity format, gameplay and every unrelated byte remain exact v0.2.27.\n- Four focused tests, two actual native reward previews and full disc verification pass. Synthetic reward lists after New Game initialization; original battle triggers/full progression remain unverified. Whole ISO outside executable equals v0.2.27. See docs/item_typography_0.2.28.md/json.\n\n';log.write_text('# Changelog\n\n'+entry+old[len('# Changelog\n\n'):],'utf8');print('Item typography reports and changelog written.')
if __name__=='__main__':main()
