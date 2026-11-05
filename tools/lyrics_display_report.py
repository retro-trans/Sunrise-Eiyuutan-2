"""Package the verified two-tier lyric display change; English-only exports."""
import argparse,hashlib,json
from pathlib import Path
from elf import ROOT,Elf
import lyrics_display_patch as b
import movie_lyrics_native as n
from iso import records
from afs import index

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');a=ap.parse_args();dest=ROOT/'work/output/v0.2.23';info=json.loads((dest/'build_info.json').read_text('utf8'));native_file=ROOT/'work/ui/lyrics-display-0.2.23/native_validation.json';native=json.loads(native_file.read_text('utf8'));verify=json.loads((dest/'verification.json').read_text('utf8'));data=(dest/'SLPS_250.70').read_bytes();base=(ROOT/'work/output/v0.2.22/SLPS_250.70').read_bytes();expected,display=b.patch(base)
 if data!=expected or not native['complete']or not native['settings_restored_exactly']or verify['files_verified']!=20:raise ValueError('Final guarded validation incomplete')
 language,_,_=b.movies.language();m,ass=b.opening();folder=b.SAFE/'00488';meta=json.loads((folder/'encode.json').read_text('utf8'));image=Path(info['iso_path']);h=hashlib.sha256()
 with image.open('rb')as f:
  while block:=f.read(8*1024*1024):h.update(block)
  rec=next(r for r in records(image)if r['path']=='/MOVIE.AFS');ent=index(f,rec['lba']*2048,rec['size'])[488];f.seek(rec['lba']*2048+ent['offset']);movie_sha=b.digest(f.read(ent['size']))
 report=dict(version='0.2.23',date='2026-11-05',based_on='0.2.22',scope='Opening and ending lyric display preference only.',display=display,language_review='Reuse the unchanged source-reviewed, editorial/glossary/proofread0.2.19 lyric manifest; no new wording.',language_sha256=b.movies.LANGUAGE_SHA,iso_sha256=h.hexdigest(),iso_size=image.stat().st_size,elf_sha256=b.digest(data),opening_encoding=meta,opening_patched_movie_sha256=movie_sha,validation=dict(focused_tests=13,test_modules=['test_lyrics_display','test_movie_subtitles'],tests_result='pass',opening_decoded_frames=2752,expected_opening_frames=2752,disc_verification=verify,native_report=str(native_file),native=native),preservation=dict(ending_sample_table_bytes_exact=True,ending_strings_unchanged=True,previous_resource_packs=43,previous_event_overlays=45,other_movie_members_unchanged=488,original_audio_exact=True),limitations=['Native ending probe exercises70 seconds, including a two-line romaji cue, an instrumental gap, reuse and stop cleanup. Actual credit composition is not played.','Original IPU decoder reports its trailing packet warning; the complete2752-frame count and native return are verified.','This change does not expand translation coverage beyond0.2.22.'])
 export=dict(version='0.2.23',based_on='0.2.22',display_languages=['romaji','English'],japanese_lyric_tier=False,wording_and_timing_unchanged=True,language_sha256=b.movies.LANGUAGE_SHA,opening=m['lyrics'],ending=language['ending']['cues'])
 print(json.dumps(dict(version=report['version'],display=display['display_languages'],sample=next(c for c in export['opening']if 'Tamashii'in c['romaji']),iso_sha256=report['iso_sha256'],native_complete=native['complete'],outputs=['build_info.json','docs/lyrics_display_0.2.23.md/json','work/translation/en/lyrics-display.en.json','CHANGELOG.md']),indent=1),flush=True)
 if not a.write:print('DRY no reports/exports updated.');return
 native_meta=info['movie_subtitles']['native_ending'];native_meta.update(code_size=display['code_size'],code_sha256=display['code_sha256'],windows='Two flat windows: romaji17 at top y8/height48; English20 bottom unchanged; Japanese tier omitted; original cue table, gaps and cleanup retained.')
 info['movie_encoding']=[dict(r,**{k:v for k,v in info['lyrics_opening_encoding'].items()},patched_movie_sha256=movie_sha)if r['member']==488 else r for r in info['movie_encoding']]
 info.update(iso_sha256=report['iso_sha256'],native_validation_report=str(native_file),in_game_validation='Complete opening native playback; ending cue1/3/5(two-line)/8, gap, reuse and stop cleanup; exact private settings restored. Actual credits unplayed.')
 (dest/'build_info.json').write_text(json.dumps(info,indent=1)+'\n','utf8');(ROOT/'docs/lyrics_display_0.2.23.json').write_text(json.dumps(report,indent=1)+'\n','utf8');(ROOT/'work/translation/en/lyrics-display.en.json').write_text(json.dumps(export,indent=1)+'\n','utf8')
 screens={s['label']:s['path']for s in native['screens']}
 doc=f'''# v0.2.23: song lyrics in romaji and English

The opening and ending now omit the Japanese lyric tier, following the user's preference. Romaji occupies the top position; English remains below. All21 opening and34 ending cue texts and timestamps are unchanged. Original Japanese audio is byte-for-byte intact.

The opening is encoded from the original uncaptioned source. It retains640x448,2752 frames, intra VLC format1 and the original movie extent. Each independent picture is at most29,996 bytes within the30,000-byte refill limit. Picture/sample-time interleaving preserves exact ADX audio. The ending reuses the original34 cue rows and string pointers, drawing only romaji17 and English20. Its compact top window accommodates the two-line cue. No translation wording, gameplay or other media is changed.

All13 focused/native-instruction checks pass. Complete ISO verification covers20 files,5,614 resource packs,80 event members and489 movie members. The previous43 changed packs,45 overlays and488 other movie members are retained. Full opening decode returns2752 frames; its known trailing-packet warning remains. Fresh muted native playback completes the opening and returns to the ending probe. The probe captures cues1/3/5/8, a gap, reused windows and cleanup. Both windows are deleted after stop. The exact private emulator settings are restored. Actual ending credit composition remains unplayed; this does not claim whole-game translation completion.

![Opening romaji and English]({screens['opening_720']})

![Ending complete two-line romaji and English]({screens['ending_cue_5']})

ISO SHA-256: `{report['iso_sha256']}`

ELF SHA-256: `{report['elf_sha256']}`

See the adjacent JSON for cue-language guards, encoding details, original-audio hash and complete native evidence. The earlier relative-path encoder attempt is preserved in work/movie_captions_0.2.23_safe; the admitted output is work/movie_captions_0.2.23_safe_r1. No release or commit was made.
'''
 (ROOT/'docs/lyrics_display_0.2.23.md').write_text(doc,'utf8')
 log=ROOT/'CHANGELOG.md';old=log.read_text('utf8');heading='## v0.2.23 — romaji and English song subtitles — 2026-11-05'
 if heading in old:raise ValueError('Preserve existing changelog entry')
 entry=heading+'\n\n- Remove the Japanese lyric tier from both songs. Move romaji to the top position and retain English below, with all55 cue texts/times and original Japanese audio unchanged. Retain complete0.2.22.\n- All13 focused checks, complete disc verification and2752-frame opening decode pass. Fresh muted native playback verifies the complete opening plus ending two-line cue, instrumental gap, reuse and stop cleanup. Exact private settings restored; actual credits unplayed. See docs/lyrics_display_0.2.23.md/json.\n\n'
 if not old.startswith('# Changelog\n\n'):raise ValueError('Changelog structure changed')
 log.write_text('# Changelog\n\n'+entry+old[len('# Changelog\n\n'):],'utf8');print('Reports and changelog written.')

if __name__=='__main__':main()
