"""Finalize reviewed Trade UI, native evidence and exact disc retention."""
import argparse,json,hashlib
from pathlib import Path
from elf import ROOT
from iso import records
import trade_patch as b

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');ap.add_argument('--attempt',type=int,default=1);args=ap.parse_args();folder=ROOT/'work/output/v0.2.31';info=json.loads((folder/'build_info.json').read_text('utf8'));verify=json.loads((folder/'verification.json').read_text('utf8'));nf=ROOT/'work/ui/trade-0.2.31'
 if args.attempt!=1:nf=nf/f'attempt-{args.attempt}'
 nf=nf/'native_validation.json';native=json.loads(nf.read_text('utf8'));data=(folder/'SLPS_250.70').read_bytes();expected,patch=b.patch((ROOT/'work/output/v0.2.30/SLPS_250.70').read_bytes())
 if data!=expected or info['elf_sha256']!=b.digest(data)or native['delivery_elf_sha256']!=b.digest(data):raise ValueError('Final executable evidence mismatch')
 if not native['complete']or not native['settings_restored_exactly']or len(native['screens'])!=5 or verify['files_verified']!=20:raise ValueError('Trade verification incomplete')
 image=Path(info['iso_path']);old=ROOT/'work/output/v0.2.30/Sunrise Eiyuutan 2 EN v0.2.30.iso';oldinfo=json.loads((old.parent/'build_info.json').read_text('utf8'));rec=next(r for r in records(image)if r['path']=='/SLPS_250.70');begin=rec['lba']*2048;end=begin+rec['size'];previous=hashlib.sha256();desired=hashlib.sha256();actual=hashlib.sha256();pos=0
 if image.stat().st_size!=old.stat().st_size or rec['size']!=len(data):raise ValueError('Same-size executable replacement required')
 with old.open('rb')as first,image.open('rb')as second:
  while raw:=first.read(8*1024*1024):
   previous.update(raw);block=bytearray(raw);lo=max(begin,pos);hi=min(end,pos+len(block))
   if lo<hi:block[lo-pos:hi-pos]=data[lo-begin:hi-begin]
   desired.update(block);actual.update(second.read(len(raw)));pos+=len(raw)
 digest=actual.hexdigest()
 if digest!=desired.hexdigest()or previous.hexdigest()!=oldinfo['iso_sha256']:raise ValueError('Unexpected disc delta')
 report=dict(version='0.2.31',date='2026-11-05',based_on='0.2.30',elf_sha256=b.digest(data),iso_sha256=digest,patch=patch,tests=dict(passed=5,scope='All 128 real recipe list formatters and requirement callbacks with counts0/1/99, full item names, None, required/owned values, explicit row positions and buffer bounds; actual square-font column renderer; every caption reference including shared capacity alert; ordinary subtitle fallback; exact allowed executable delta with recipe/rule/help bytes retained.'),native=native,disc_verification=verify,disc_delta=dict(previous_sha256=previous.hexdigest(),expected_replacement_sha256=desired.hexdigest(),outside_executable='Every byte equals v0.2.30.'),limitations=['Native preview uses three synthetic available recipe IDs after cold New Game initialization; original shop-unlock route and full progression are not replayed.','Confirmation and capacity captions are exercised through their original common modal functions directly; no successful transaction is performed in the preview.','Inherited 56 unresolved battle-dialogue holds and prior startup automation limitations remain documented.'])
 print(json.dumps(dict(version='0.2.31',iso_sha256=digest,tests=5,native_panels=5,recipes_checked=128,source_objects=8,normal_help_geometry='unchanged',outside_executable='exact v0.2.30',outputs=['build_info.json','ISO.sha256','docs/trade_0.2.31.md/json','CHANGELOG.md']),indent=1),flush=True)
 if not args.write:print('DRY no reports written.');return
 log=ROOT/'CHANGELOG.md';oldlog=log.read_text('utf8');heading='## v0.2.31 — Trade translation and font proportions — 2026-11-05'
 if heading in oldlog or not oldlog.startswith('# Changelog\n\n'):raise ValueError('Changelog guard')
 info.update(iso_sha256=digest,native_validation_report=str(nf),in_game_validation='Five cold native Trade panels pass: original list/requirement consumers and failed-condition branch, longest item, common confirmation and capacity modals. Three synthetic available recipe IDs; original unlock route and successful trade not replayed.')
 (folder/'build_info.json').write_text(json.dumps(info,indent=1)+'\n','utf8');(folder/'Sunrise Eiyuutan 2 EN v0.2.31.iso.sha256').write_text(digest+'  Sunrise Eiyuutan 2 EN v0.2.31.iso\n','ascii');(ROOT/'docs/trade_0.2.31.json').write_text(json.dumps(report,indent=1)+'\n','utf8')
 doc=f'''# v0.2.31: Trade translation and font proportions

The complete compiled Trade category now displays English: Trade / Exchange items, Item / Owned, required-item owned counts, the exchange explanation, unmet requirements, confirmation and inventory-limit messages. Eight distinct source objects and all nine address-reference pairs are covered, including the inventory-limit alert shared with an item-award consumer. The empty requirement slot displays None through a Trade-only name wrapper; the general item getter remains unchanged.

Independent accuracy review examined the native confirmation's add/subtract operations. The selected item is received and the two displayed requirements are consumed. The explanation therefore reads **Trade the items above for this item.** Editorial review and final proofreading cover all eight rows. The title separator and newline, confirmation's two clauses and newline, numeric arguments, row coordinates and font reset controls are retained. Byte padding and squeezed-font control are deliberately replaced for the layout correction.

All 128 recipes have been checked. Every required-item name fits at the normal **26×26** font within 312 pixels; the widest is Armored Soldier Parts LvA at 309 pixels including message-parser spacing. The quantity/owned column moves to x=320 and fits within its remaining 184 pixels, including counts of 99. Requirement rows remain at y=0 and 28, with the complete explanation at y=56. The ordinary bottom frame stays x=18, y=336, width=604, height=96; its portrait allocation and other help consumers are preserved.

The Trade item list grows to 608 pixels at x=16, y=92, retaining its 224-pixel height. Names and owned counts use explicit columns, with quantities anchored at 600. Normal names use 26×26. The single exceptionally long Improved Ultra-Compact Nuclear Fusion Engine label uses 22×22, keeping both dimensions proportional. A marker used only by Trade routes these rows through a private copy of the established column renderer. Existing Information rows and ordinary subtitles delegate to their prior rendering paths. All item IDs, recipe IDs, row pitch, selection behavior and owned quantities remain intact.

The Trade list formatter's old 48-byte temporary buffer cannot hold the longest complete English name plus a two-digit count and terminator. Its two address instructions now select a proven unused 64-byte tail. All 128 outputs at counts 0/1/99 fit, as do the original 65-byte requirement buffers and 512-byte combined description buffer. The 128 recipe records, availability conditions, carry limit, equipped-item checks, add/subtract operations and confirmation behavior remain unchanged. New code and complete strings occupy 916 bytes in a proven free tail; source strings are preserved.

Five focused tests execute the native item formatter and requirement callback for every recipe, check all complete names/values/control positions and buffer bounds, execute the square-font column renderer, verify all nine caption reference pairs and ordinary subtitle fallback, and restore the exact allowed changes to require a byte-identical v0.2.30 executable. Five cold muted native panels exercise the original Trade menu and failed-condition branch, longest label, confirmation and capacity text. The available-recipe array contains three synthetic IDs after New Game initialization. Confirmation and capacity captions use their original common modals directly; no successful trade is performed. The original shop unlock route and full progression remain unverified. Emulator settings are restored exactly.

Full disc verification covers 20 files, 5,614 resource packs, 80 event members and 489 movies. Whole-image hashing proves every byte outside the executable equals v0.2.30. Prior formation fixes, movie subtitles, romaji/English song lyrics and original audio remain intact. Inherited 56 unresolved battle-dialogue holds and prior startup automation limitations remain documented.

ISO SHA-256: `{digest}`

ELF SHA-256: `{b.digest(data)}`

Restart the game and load a normal memory-card save. Older emulator savestates retain old UI code and pointers. No commit or release was made.
'''
 for row in native['screens']:doc+='\n![%s](<%s>)\n'%(row['label'],Path(row['screen']).as_posix())
 (ROOT/'docs/trade_0.2.31.md').write_text(doc,'utf8');entry=heading+'\n\n- Translate the complete Trade caption/prompt category and empty requirement slots, including confirmation, unmet requirements and both references to the shared inventory-limit alert. Review the exchange direction against native item add/subtract operations.\n- Restore 26×26 requirement names; separate counts/owned values at x320. Widen the item list to 608 pixels with explicit name/quantity columns and 22×22 fitting for its longest label. Preserve normal help geometry.\n- Relocate the temporary list formatter to a 64-byte buffer so the longest complete name and owned count remain safe. Retain all 128 recipe records and transaction rules.\n- Five focused checks across all 128 recipes, five native panels and full disc verification pass. Synthetic available recipe IDs; original unlock route/full progression and successful trade unverified. Every ISO byte outside the executable equals v0.2.30. See docs/trade_0.2.31.md/json.\n\n';log.write_text('# Changelog\n\n'+entry+oldlog[len('# Changelog\n\n'):],'utf8');print('Trade reports and changelog written.')
if __name__=='__main__':main()
