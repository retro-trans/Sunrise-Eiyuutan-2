# Status and known limits — v0.8.0

Public v0.8.0 is byte-identical to the verified local v0.2.31 image. The release number is not a completion percentage.

## Integrated coverage

| Category | Release coverage |
|---|---|
| Inventoried main-story tables | 33 tables / 1,195 stored rows; 31 later tables contain 5,749 body calls |
| Character/mech encyclopedia | 588 entries |
| Shared battle dialogue bank | 6,463 of 6,519 logical rows; both physical copies patched |
| Unresolved battle lines | 56 retain original Japanese; see the [hold inventory](battle_category_holds_0.2.25.en.json) |
| Movie voice captions | 116 cues across 23 attack movies and 16 episode previews |
| Captioned/rebuilt movies | 40, including the opening |
| Opening / ending lyrics | 21 / 34 timed cues, romaji and English |
| Menus, names and help | Title/options, travel, battle, formation, services, information, items, equipment, save/load titles and Trade have cumulative fixes; this is not a complete binary/graphics inventory claim |

Stored rows, spoken body calls and timed cues are different units. The battle table's two physical copies are one logical bank. Do not add duplicate counts or treat English working exports as proof that every line is integrated and tested.

## What remains

- The 56 battle holds remain Japanese because the available context does not settle the meaning. The hold inventory records each ID and reason.
- Five unclear movie tracks were left untouched. Subtitle transcription used Whisper screening and model-assisted review; full human listening certification is absent, and some cue timings remain qualified.
- Other spoken-only clips outside movies and previews were not subtitled. Branded Japanese artwork and some unclassified graphics/text can remain.
- The actual ending-credit composition was not played through. Native lyric-window timing, hiding, reuse and cleanup were tested separately.
- Full routes, choices, endings, all battle captions and every original menu/unlock path have not received a complete playthrough.
- Earlier automated startup/first-dialogue checks timed out on both an updated build and its baseline. Forced battle-dialogue previews did not complete. Those failures remain unresolved; later successful isolated menu previews do not establish complete startup/playthrough validation.
- Latest Trade and formation previews use synthetic fixture data after initialization. Original unlock conditions, full progression and a successful Trade transaction were not replayed.
- Physical PS2, OPL and real memory-card persistence have not been verified. Emulator save states can retain old code; restart and use an in-game save.
- Movie re-encoding is lossy; original encoded ADX audio and unrelated audio streams are retained.

## Verification

Full-disc verification checks 20 files, 5,614 resource packs, 80 event members and all 489 movie records against original/pinned expected bytes. Focused tests check the modified pointers, control arguments, font widths, complete labels and buffer bounds.

The public patch is decoded using the exact original Japanese source, with checksum verification enabled. The reconstructed 2,627,004,416-byte output must match SHA-256 `8fa9f17a838b4c22c591467ad343b7130d159efcd00b5cbb413c43175b8e2f7f`.

Automated checks and representative native probes do not replace a full playthrough or human language review. Release validation is in [docs/releases/v0.8.0](releases/v0.8.0/).
