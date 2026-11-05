# Tool inventory

The project uses Python 3.11 and `requirements.txt`. Original Japanese disc images, extracted source assets, fonts, emulator binaries, external encoders and historical local build outputs are not distributed.

Most Python tools are read-only or print a plan unless passed `--write`. Native debug runners may use `--run`. Always inspect the help and dry plan first; historical tools can depend on a specific previous local build.

| Tool/family | Purpose |
|---|---|
| `iso.py` | Inspect/extract the original SLPS-25070 ISO |
| `afs.py`, `extract.py` | AFS/resource indexing and extraction |
| `text.py`, `textcodec.py`, `text_refs.py` | Structured script extraction, controls and references |
| `elf.py`, `disasm.py`, `string_refs.py` | ELF mapping, instruction and pointer inspection |
| `strip_jp.py` | Validate working drafts and generate public English-only structured exports |
| `names.py`, `refresh_sources.py` | Glossary/name audits and source synchronization |
| `fontgen.py`, `vwf.py`, `layout.py`, `message_pages.py` | Proportional English font and native page layout |
| `build.py`, `*_patch.py` | Historical cumulative builders and category-specific code/text integration |
| `*_report.py` | Category validation and fit reports |
| `movie_pss.py`, `movie_subtitles.py`, `movie_frame_limit.py` | PSS/ADX handling, timed captions and bounded IPU encoding |
| `lyrics_display_patch.py`, `movie_lyrics_native.py` | Romaji/English lyric display and native ending timing |
| `export_opening_mp4.py` | Standalone opening-video export from local original media/caption caches |
| `verify.py` | Exact expected ELF, changed packs/overlays/movies and unchanged-disc verification |
| `package_release.py` | Guarded original-to-English xdelta encoding and full reconstruction hash check |
| `dbg/` | Cold-boot native UI probes and emulator helpers; user audio/cards remain protected |
| `tests/` | Focused source, instruction, control, width and buffer checks |

## Extraction example

With your original `Sunrise Eiyuutan 2 (Japan).iso` at the root:

```text
python tools/iso.py
python tools/iso.py --extract
python tools/afs.py
python tools/afs.py --extract
python tools/text.py
python tools/text.py --write
```

These commands inspect/extract source data; they do not build the released translation. Verify your original SHA-256 against the release instructions first.

## Rebuild limitations

The source snapshot includes the actual tools and English exports, but not all of the ignored working drafts, review inputs, historical build snapshots or prepared movie assets they consume. Several scripts intentionally require exact predecessor hashes. Paths in `movie_subtitles.py` still identify the original local source-IPU cache and pinned .NET/IPUenc checkout. `fontgen.py` expects a local Noto Sans JP font; movie rendering uses installed Windows fonts and FFmpeg. These need to be configured/restored before rebuilding.

`package_release.py` packages the verified local v0.2.31 image as public v0.8.0. It does not generate that cumulative baseline from an original disc alone. Its output ISO is a checksum-verified reconstruction used for validation and stays local. Upload only the release patch, instructions, manifests and checksums.

No downloaded game binaries or Japanese script dumps are necessary to read and review the published tools/English; they are required locally for source verification and native builds.
