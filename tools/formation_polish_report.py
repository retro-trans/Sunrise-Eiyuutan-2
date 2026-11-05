"""Finalize evidence, disc checksum and changelog for formation polish."""
import argparse,json,hashlib
from pathlib import Path
from elf import ROOT
from iso import records
import formation_polish_patch as b

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');args=ap.parse_args();folder=ROOT/'work/output/v0.2.30';info=json.loads((folder/'build_info.json').read_text('utf8'));verify=json.loads((folder/'verification.json').read_text('utf8'));nf=ROOT/'work/ui/formation-polish-0.2.30/attempt-4/native_validation.json';native=json.loads(nf.read_text('utf8'));data=(folder/'SLPS_250.70').read_bytes();expected,patch=b.patch((ROOT/'work/output/v0.2.29/SLPS_250.70').read_bytes())
 if data!=expected or info['elf_sha256']!=b.digest(data)or native['delivery_elf_sha256']!=b.digest(data):raise ValueError('Final executable evidence mismatch')
 if not native['complete']or not native['settings_restored_exactly']or len(native['screens'])!=6 or verify['files_verified']!=20:raise ValueError('Verification incomplete')
 image=Path(info['iso_path']);old=ROOT/'work/output/v0.2.29/Sunrise Eiyuutan 2 EN v0.2.29.iso';oldinfo=json.loads((old.parent/'build_info.json').read_text('utf8'));rec=next(r for r in records(image)if r['path']=='/SLPS_250.70');begin=rec['lba']*2048;end=begin+rec['size'];previous=hashlib.sha256();desired=hashlib.sha256();actual=hashlib.sha256();pos=0
 if image.stat().st_size!=old.stat().st_size or rec['size']!=len(data):raise ValueError('Same-size executable replacement required')
 with old.open('rb')as first,image.open('rb')as second:
  while raw:=first.read(8*1024*1024):
   previous.update(raw);block=bytearray(raw);lo=max(begin,pos);hi=min(end,pos+len(block))
   if lo<hi:block[lo-pos:hi-pos]=data[lo-begin:hi-begin]
   desired.update(block);actual.update(second.read(len(raw)));pos+=len(raw)
 digest=actual.hexdigest()
 if digest!=desired.hexdigest()or previous.hexdigest()!=oldinfo['iso_sha256']:raise ValueError('Unexpected disc delta')
 report=dict(version='0.2.30',date='2026-11-05',based_on='0.2.29',elf_sha256=b.digest(data),iso_sha256=digest,patch=patch,tests=dict(passed=4,scope='All seven action/equipment captions and unindented Captain, eight machine records across 24 name fields and every unchanged machine field; actual pilot-list consumer and IDs; equipment helper with all 161 names at zero through three slots, actual glyph metrics, complete text, font choice, final normal-font restore, stack and buffer bounds; exact allowed executable delta and unchanged normal help/player.'),native=native,preflight=dict(candidates=[str(ROOT/'work/output/preflight-v0.2.30-r1'),str(ROOT/'work/output/preflight-v0.2.30-r2')],evidence=[str(nf.parent.parent/'native_validation.json'),str(nf.parent.parent/'attempt-2/native_validation.json'),str(nf.parent.parent/'attempt-3/native_validation.json')],findings='Initial native long-name panel exposed the native string measurer omitting the two-pixel advance used by the message parser. Final helper sums actual glyph width plus that advance. The pilot fixture ID buffer was also enlarged to the full native pilot-list extent; unrelated stack IDs are no longer displayed. Final candidate also restores normal font after every nonempty equipment summary, with the longest small-font item placed last in the final native fixture.'),disc_verification=verify,disc_delta=dict(previous_sha256=previous.hexdigest(),expected_replacement_sha256=desired.hexdigest(),outside_executable='Every byte equals v0.2.29.'),limitations=['Cold native fixtures use synthetic stack-local deck/list data after New Game initialization; original unlocked formation gameplay route and full progression are not replayed.','Equipment details use normal 26px square text, 20px when necessary and 13px for the one exceptionally long name. Complete wording remains visible within the original help box.','Inherited 56 unresolved battle-dialogue holds and prior startup automation limitations remain documented.'])
 print(json.dumps(dict(version='0.2.30',iso_sha256=digest,tests=4,native_panels=6,machine_records=8,translated_submenu_entries=7,normal_help_geometry='unchanged',outside_executable='exact v0.2.29',outputs=['build_info.json','ISO.sha256','docs/formation_polish_0.2.30.md/json','CHANGELOG.md']),indent=1),flush=True)
 if not args.write:print('DRY no reports written.');return
 log=ROOT/'CHANGELOG.md';oldlog=log.read_text('utf8');heading='## v0.2.30 — formation submenu and font polish — 2026-11-05'
 if heading in oldlog or not oldlog.startswith('# Changelog\n\n'):raise ValueError('Changelog guard')
 info.update(iso_sha256=digest,native_validation_report=str(nf),in_game_validation='Six cold native formation fixtures pass, including long equipment names at all three supported font sizes. Actual window/list/menu/detail consumers with synthetic stack-local deck and IDs; original unlocked gameplay route/full progression unverified.')
 (folder/'build_info.json').write_text(json.dumps(info,indent=1)+'\n','utf8');(folder/'Sunrise Eiyuutan 2 EN v0.2.30.iso.sha256').write_text(digest+'  Sunrise Eiyuutan 2 EN v0.2.30.iso\n','ascii');(ROOT/'docs/formation_polish_0.2.30.json').write_text(json.dumps(report,indent=1)+'\n','utf8')
 text=f'''# v0.2.30: formation submenu and font polish

Eight machine records now use **(Unmanned)** in their full, display and omission captions: Meisarge, Thunderbolt, Thunderchief, Deege, Gandor, Gun Elephant, Aqua Wolf and Aqua Centaur. All 24 pointers target relocated complete captions; names, machine IDs and statistics remain unchanged.

The pilot list now requests normal **26×26** proportional lettering, uniformly reduced only if a complete name exceeds the original list width. Domon stays at the normal size. Original row IDs, spacing, selection and pilot data remain intact.

The missed static action submenu displays **Attack / Defend / Special**. All four related equipment entries display **Equipment 1 / Equipment 2 / Equipment 3 / Equipment S**. The independent accuracy, editorial and proofreading review examined all seven source entries; S is retained without an unsupported expansion. The Captain caption loses its source padding so **Ship** and **Captain** start at the same horizontal position.

The bottom equipment summary uses **26px** square text for ordinary names and None, **20px** when needed, and **13px** for the exceptionally long Improved Ultra-Compact Nuclear Fusion Engine label. All 161 equipment captions are checked at zero through three slots, retaining complete names and slot numbers. The largest output remains below the existing 256-byte help buffer. A separate 768-byte local frame prevents the old short formatter buffer from overflowing with three long labels. Every line fits the existing 504-pixel text area, and three normal rows fit its 84-pixel height. The ordinary frame stays at x=18, y=336, width=604, height=96, with the original portrait allocation.

Native preview exposed a difference between the string measurer and the message parser: the parser adds two pixels between characters. The new scoped measure sums the actual proportional glyph width plus that advance. Both the equipment summary and the pilot list use this calculation. The summary restores the normal font afterward, including when its final label uses a smaller font. Other dialogue/help consumers and the existing scoped long-detail frame remain unchanged. New code and complete strings occupy a proven free tail of the previous constant pool; no original text is overwritten.

Four focused tests execute the native pilot-list consumer and the assembled equipment helper, including actual proportional glyph calculations. They verify all 161 names, all slot counts, the largest fitting font, row IDs, exact complete output, stack restoration, buffer bounds, every machine name field and the exact permitted executable delta. Six cold muted native previews cover the shortened name, Domon, both translated submenus, ordinary and longest equipment details, and Ship/Captain alignment. They use real native constructors and consumers with synthetic stack-local data after New Game initialization. They do not replay the original unlocked formation route or certify full progression. Emulator settings are restored exactly. Both earlier preview sets and their candidate remain preserved.

Full disc verification covers 20 files, 5,614 resource packs, 80 event members and 489 movies. Whole-image hashing proves every byte outside the executable equals v0.2.29. Prior subtitles, romaji/English song lyrics, normal help geometry and original audio remain intact. Inherited 56 unresolved battle-dialogue holds and prior startup automation limitations remain documented.

ISO SHA-256: `{digest}`

ELF SHA-256: `{b.digest(data)}`

Restart the game and load a normal memory-card save; older emulator savestates contain old UI code and pointers. No commit or release was made.
'''
 for row in native['screens']:text+='\n![%s](<%s>)\n'%(row['label'],Path(row['screen']).as_posix())
 (ROOT/'docs/formation_polish_0.2.30.md').write_text(text,'utf8')
 entry=heading+'\n\n- Shorten Unmanned Unit to Unmanned across eight machines and all 24 name references. Restore normal square pilot-list proportions.\n- Translate all three action and four equipment submenu entries. Align Ship/Captain by removing Captain padding.\n- Enlarge equipment summaries to normal 26px text with complete per-line fitting at 20/13px when needed; include the native parser advance in measurement and use safe local buffers. Preserve normal help geometry.\n- Four focused checks, six cold native previews and full disc verification pass. Synthetic stack-local preview data; original unlocked route/full progression unverified. All ISO bytes outside the executable equal v0.2.29. See docs/formation_polish_0.2.30.md/json.\n\n'
 log.write_text('# Changelog\n\n'+entry+oldlog[len('# Changelog\n\n'):],'utf8');print('Formation polish reports and changelog written.')
if __name__=='__main__':main()
