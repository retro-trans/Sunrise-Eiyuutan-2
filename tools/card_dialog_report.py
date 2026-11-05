"""Record final card warning/layout correction and its preserved baseline."""
import argparse,json,hashlib
from pathlib import Path
from elf import ROOT,Elf
import card_dialog_patch as b

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');a=ap.parse_args();dest=ROOT/'work/output/v0.2.24';info=json.loads((dest/'build_info.json').read_text('utf8'));vf=json.loads((dest/'verification.json').read_text('utf8'));nf=ROOT/'work/ui/card-dialog-0.2.24/native_validation.json';native=json.loads(nf.read_text('utf8'));data=(dest/'SLPS_250.70').read_bytes();expected,fix=b.patch((ROOT/'work/output/v0.2.23/SLPS_250.70').read_bytes())
 if data!=expected or not native['complete']or not native['settings_restored_exactly']or vf['files_verified']!=20:raise ValueError('Final verification incomplete')
 h=hashlib.sha256()
 with Path(info['iso_path']).open('rb')as f:
  while block:=f.read(8*1024*1024):h.update(block)
 report=dict(version='0.2.24',based_on='0.2.23',date='2026-11-05',iso_sha256=h.hexdigest(),iso_size=Path(info['iso_path']).stat().st_size,elf_sha256=b.digest(data),card_dialog=fix,language=b.language(),cause='v0.2.22 expanded stasCreate, a shared status/help constructor, for five-line ability details. Ordinary Repair help therefore inherited the taller frame and upward portrait/text position.',correction='Restore stock y336/96px frame by default; scoped submissions select stock geometry for1..3 lines or existing five-line geometry for longer details. Returning from details to help restores stock frame, text position and portrait context.',tests=dict(passed=5,module='test_card_dialog',checks=['Actual native no-save/corrupt warning branches, both card slots, exact source title and full English predicates','Native original-size constructor with full-size backing allocation','Short/long/short transitions, original word pointers, return values, arguments and stack','Exact changed-word/unused-pool boundaries; original generic dialogue factories and all submission delay slots retained','Full translated warnings fit original native window widths']),native=native,disc_verification=vf,preservation=dict(previous_resource_packs=43,previous_event_overlays=45,movie_archive=info['movie_archive_retained'],song_display='Romaji and English retained from0.2.23',all_original_audio_unchanged=True),qualifications=['Native preview uses synthetic card mode and long-detail numeric prefix; normal Load Game and battle triggers are not replayed. Production no-save/corrupt renderer, repair string and status constructor/text consumer are exercised.','New language comprises three UI objects; independent source review examined15 adjacent rows. Native composition and both title references were checked before dropping the dangling English possessive. No gameplay or save-format changes.'])
 print(json.dumps(dict(version='0.2.24',iso_sha256=report['iso_sha256'],wording=[r['en']for r in b.language()['rows']],normal_box=fix['normal_box'],native_complete=native['complete'],outputs=['build_info.json','docs/card_dialog_0.2.24.md/json','CHANGELOG.md']),indent=1),flush=True)
 if not a.write:print('DRY no reports/changelog updated.');return
 log=ROOT/'CHANGELOG.md';old=log.read_text('utf8');heading='## v0.2.24 — card warnings and restored help boxes — 2026-11-05'
 if heading in old or not old.startswith('# Changelog\n\n'):raise ValueError('Changelog revision changed')
 effects=info['battle_effects'];e=Elf(data);effects['code_sha256']=b.digest(e.at(int(effects['code_va'],16),effects['code_size']));effects['clones']=[dict(c,sha256=b.digest(e.at(int(c['va'],16),c['size'])))for c in effects['clones']]
 info.update(iso_sha256=report['iso_sha256'],native_validation_report=str(nf),in_game_validation='Fresh muted native no-save/corrupt warning views and original-size Repair help, long detail and restored Repair help; exact settings restored. Synthetic card mode/detail fixture; ordinary menu/battle triggers and in-battle portrait composition not replayed.')
 (dest/'build_info.json').write_text(json.dumps(info,indent=1)+'\n','utf8');(ROOT/'docs/card_dialog_0.2.24.json').write_text(json.dumps(report,indent=1)+'\n','utf8')
 screens={r['label']:Path(r['screen']).as_posix()for r in native['panels']}
 doc=f'''# v0.2.24: memory-card warnings and original help boxes

The missing warning now reads **Sunrise Eiyuutan 2 / There is no save data.** Its related corruption warning reads **Sunrise Eiyuutan 2 / The save data is corrupted.** The slot heading, native warning style, input handling and save format remain unchanged. Three complete English UI objects are relocated; original Japanese source strings remain untouched. Both title references belong to the confirmed title-and-predicate warning layout. Accuracy, editorial, glossary and final proofreading are complete; the independent reviewer examined15 adjacent source rows.

The oversized Repair help was caused by the0.2.22 change to the shared status/help constructor. It made the frame taller and moved its text and portrait upward for long ability comments; Repair help inherited that geometry. The default frame is restored to its original y336 and96px height. Three-line help uses84px text height at y342. Only longer complete detail text selects the existing five-line frame. Switching back to help restores the original frame, text and portrait context. Font size, full text and generic dialogue factories are preserved.

All five focused checks pass, including both warning modes in both slots, actual native constructor execution, short/long/short transitions and precise preservation boundaries. Full disc verification covers20 files,5,614 resource packs,80 event members and489 movie members. All43 prior changed packs,45 overlays and the complete0.2.23 movie archive/audio remain exact.

Fresh muted native preview captures the no-save and corruption warnings, Repair help in its original box, the longest ability comment and Repair help restored afterward. Card mode and the numeric long-detail prefix are preview fixtures; ordinary Load Game/battle triggers are not replayed. The diagnostic uses the title background and does not draw a portrait; the portrait's restored native position context and unchanged placement code are checked, while in-battle portrait composition remains unplayed. The private emulator is stopped and its exact original settings restored.

![Translated no-save warning](<{screens['no_save']}>)

![Restored original Repair help box](<{screens['repair_stock_box']}>)

![Repair help after leaving long details](<{screens['repair_restored_after_detail']}>)

ISO SHA-256: `{report['iso_sha256']}`

ELF SHA-256: `{report['elf_sha256']}`

The adjacent JSON contains complete language/source guards, native coordinates and evidence. This build retains the romaji-and-English song display, previous translations and original voices. No release or commit was made.
'''
 (ROOT/'docs/card_dialog_0.2.24.md').write_text(doc,'utf8')
 entry=heading+'\n\n- Translate the remaining no-save/corrupt warning title and predicates, retaining native slot headings, warning frames and save behavior. Relocate three complete source-reviewed English strings.\n- Restore original normal help/status geometry. Fix the0.2.22 shared-constructor regression: extra height is used only for text longer than three lines, and returning to Repair help restores its original box and portrait position. Retain full ability descriptions, fonts and complete0.2.23.\n- Five focused checks, full disc verification and fresh muted native warning/help/detail/help preview pass. Exact private settings restored. Synthetic card mode/detail numeric prefix; ordinary menu/battle triggers not replayed. See docs/card_dialog_0.2.24.md/json.\n\n'
 log.write_text('# Changelog\n\n'+entry+old[len('# Changelog\n\n'):],'utf8');print('Reports/changelog written.')

if __name__=='__main__':main()
