"""Document focused save-title validation and exact disc delta."""
import argparse,json,hashlib
from pathlib import Path
from elf import ROOT
from iso import records
import episode_titles_patch as b
def sha_file(path):
 h=hashlib.sha256()
 with path.open('rb')as f:
  while raw:=f.read(8*1024*1024):h.update(raw)
 return h.hexdigest()
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');a=ap.parse_args();folder=ROOT/'work/output/v0.2.27';info=json.loads((folder/'build_info.json').read_text('utf8'));verify=json.loads((folder/'verification.json').read_text('utf8'));nf=ROOT/'work/ui/episode-titles-0.2.27/native_validation_2.json';native=json.loads(nf.read_text('utf8'));data=(folder/'SLPS_250.70').read_bytes()
 if not native['complete']or not native['settings_restored_exactly']or len(native['screens'])!=2 or verify['files_verified']!=20 or b.digest(data)!=info['elf_sha256']:raise ValueError('Focused verification incomplete')
 image=Path(info['iso_path']);previous=ROOT/'work/output/v0.2.26/Sunrise Eiyuutan 2 EN v0.2.26.iso';oldinfo=json.loads((previous.parent/'build_info.json').read_text('utf8'));rec=next(r for r in records(image)if r['path']=='/SLPS_250.70');begin=rec['lba']*2048;end=begin+rec['size'];expected=hashlib.sha256();priorhash=hashlib.sha256();pos=0
 if image.stat().st_size!=previous.stat().st_size or rec['size']!=len(data):raise ValueError('Same-size disc replacement required')
 with previous.open('rb')as f:
  while raw:=f.read(8*1024*1024):
   priorhash.update(raw);block=bytearray(raw);lo=max(begin,pos);hi=min(end,pos+len(block))
   if lo<hi:block[lo-pos:hi-pos]=data[lo-begin:hi-begin]
   expected.update(block);pos+=len(block)
 digest=sha_file(image)
 if digest!=expected.hexdigest()or priorhash.hexdigest()!=oldinfo['iso_sha256']:raise ValueError('Disc differs beyond exact executable replacement')
 report=dict(version='0.2.27',date='2026-11-05',based_on='0.2.26',iso_sha256=digest,elf_sha256=info['elf_sha256'],language_sha256=b.LANGUAGE_SHA,patch=info['episode_titles'],tests=dict(passed=4,scope='Execute native concatenator for all 361 independent index pairs, execute fit helper for each pair and native font argument words, exact allowed executable delta, and unaligned-doubleword CPU fixture validation.'),native=native,initial_preview_attempt=dict(path=str(nf.parent/'native_validation.json'),result='Save list rendered correctly; runner incorrectly used Triangle to cancel and timed out waiting for Load phase. Cross cancellation in attempt 2 succeeds with the same debug and delivery ELF hashes; initial evidence preserved.'),disc_verification=verify,disc_delta=dict(previous_sha256=priorhash.hexdigest(),expected_replacement_sha256=expected.hexdigest(),outside_executable='Every byte equals v0.2.26.'),limitations=['Native Save/Load preview uses synthetic numeric saved headers with private card I/O stubs and suppressed bottom date/player panel; physical card persistence not exercised.','Normal full story startup and playthrough remain unverified; 56 inherited battle dialogue holds remain.','Title and prefix indices are independent; maximum font-fit checks intentionally include all 361 pairs rather than assuming story chapter order.'])
 print(json.dumps(dict(version='0.2.27',titles=19,combinations=361,tests=4,native_lists=2,iso_sha256=digest,outside_executable='exact v0.2.26',sample='Episode 2: Heroes of Light Gather',outputs=['build_info.json','ISO.sha256','docs/episode_titles_0.2.27.md/json','CHANGELOG.md']),indent=1),flush=True)
 if not a.write:print('DRY no reports or metadata written.');return
 log=ROOT/'CHANGELOG.md';old=log.read_text('utf8');heading='## v0.2.27 — save/load episode titles — 2026-11-05'
 if heading in old or not old.startswith('# Changelog\n\n'):raise ValueError('Changelog changed')
 info.update(iso_sha256=digest,native_validation_report=str(nf),in_game_validation='Native Save and Load list render/cancel/cleanup pass with six synthetic numeric headers including reported Episode 2/title 6 and worst-length pair. Card I/O stubbed in private ELF only; bottom metadata suppressed. Full progression not certified.')
 (folder/'build_info.json').write_text(json.dumps(info,indent=1)+'\n','utf8');(folder/'Sunrise Eiyuutan 2 EN v0.2.27.iso.sha256').write_text(digest+'  Sunrise Eiyuutan 2 EN v0.2.27.iso\n','ascii');(ROOT/'docs/episode_titles_0.2.27.json').write_text(json.dumps(report,indent=1)+'\n','utf8')
 pictures=[Path(s['screen']).as_posix()for s in native['screens']]
 doc=f"""# v0.2.27: save/load episode titles

The reported saved-game title is **Heroes of Light Gather**. All **19 title-table entries** now use reviewed English in the shared save/load formatter. Sixteen reuse existing independently reviewed translations; Encounter, Transfer Voyage and Dark Power received separate source accuracy, editorial and proofreading review, consistent with reviewed preview captions. All source title and prefix targets were examined. Existing approved title punctuation and prefix values remain exact.

Saved headers contain independent numeric prefix/title indices. The shown combination is prefix 2 and title 6. Existing saves display the translated lookup strings without rewriting saved data. No chapter-order mapping is inferred from adjacent table entries.

The old formatter capped labels at 36 bytes and used a small static buffer. It now uses a relocated 64-byte buffer, capped at 63 bytes, matching the existing per-row caller slots. All **361 combinations** retain their complete text; maximum length is 56 bytes. The original 478-pixel frame, position, height and 28-pixel row pitch remain unchanged. Labels normally use proportional 26×26 text; only long labels receive a uniform size reduction to fit the 462-pixel interior. The reported title uses the normal 26×26 setting at 402 pixels; the worst pair uses 17×17 at 453 pixels. No horizontal compression or text truncation is used.

Four focused tests pass: execute the actual native concatenator for every pair with buffer canaries and preserved old buffer/callee registers; execute the fit helper and actual save-list font argument instructions for every pair; prove that only 19 title pointers, nine instructions and the new 494-byte pool change; validate all unaligned doubleword offsets used by the test interpreter. Prefix pointers and strings, save format, card I/O, gameplay, ordinary help/dialogue boxes and all other executable bytes remain exact v0.2.26.

Two cold native previews exercise the real Save and Load list constructor, saved-header extraction, title getter, fit helper, row renderer, cancellation and cleanup. Six synthetic numeric headers include two copies of the reported title, the longest prefix/title combination and three other labels. Private-only stubs suppress card I/O and the unrelated bottom date/player metadata panel; these stubs are absent from delivery. Physical card save/load persistence is not exercised. Emulator audio is muted and settings restored exactly. An initial runner attempt used Triangle to cancel and stalled after the correctly rendered Save list. Cross cancellation passes both phases with the same executable hashes; the failed attempt remains preserved alongside the successful evidence.

![Native Save list](<{pictures[0]}>)

![Native Load list](<{pictures[1]}>)

Full disc verification covers 20 files, 5,614 resource packs, 80 event members and 489 movies. Whole-image hashing proves every byte outside the executable equals v0.2.26. All translated resources, event overlays, movie subtitles, romaji/English song subtitles and original audio remain intact. The 56 inherited battle-dialogue holds and previous startup automation limitations remain; this focused UI check does not certify a full playthrough.

ISO SHA-256: `{digest}`

ELF SHA-256: `{info['elf_sha256']}`

Restart the game to load the new executable, then use the normal memory-card load menu. Older emulator savestates contain old code and tables. No release or commit was made.
"""
 (ROOT/'docs/episode_titles_0.2.27.md').write_text(doc,'utf8');entry=heading+'\n\n- Translate all 19 save/load title entries, including Heroes of Light Gather; preserve approved prefixes and title punctuation. Existing numeric saved headers resolve through the updated lookup without save rewrites.\n- Relocate the formatter buffer to 64 bytes and remove the old 36-byte truncation limit. Fit long labels with uniform font sizes inside the original list frame; reported title retains normal 26×26 font. All 361 prefix/title combinations fit completely.\n- Four focused checks, native Save and Load previews and full disc verification pass. Private preview uses synthetic numeric saved headers and card I/O stubs; physical persistence and full progression remain unverified. Every ISO byte outside the executable equals v0.2.26; inherited limitations retained. See docs/episode_titles_0.2.27.md/json.\n\n';log.write_text('# Changelog\n\n'+entry+old[len('# Changelog\n\n'):],'utf8');print('Episode-title reports and changelog written.')
if __name__=='__main__':main()
