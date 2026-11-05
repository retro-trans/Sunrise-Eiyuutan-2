# Sunrise Eiyuutan 2 English — v0.8.0

English translation patch for **Sunrise Eiyuutan 2** on PlayStation 2, Japanese original edition **SLPS-25070**.

This is the first public release. It packages the cumulative, verified local v0.2.31 build under the public version **v0.8.0**. The game bytes are identical; the version number does not indicate a measured completion percentage. Translation and full-game testing remain in progress.

### Apply

**Automatic:** In [Retro Trans](https://github.com/retro-trans/retro-trans-tools), click **Refresh catalog**, open **Automatic**, select your original Japanese ISO, choose v0.8.0 (or Latest), then click **Patch** and select a new output file. Recognition uses the disc's complete hash, so its filename can differ.

Apply the `.xdelta` with [DeltaPatcher](https://github.com/marco-calautti/DeltaPatcher) or [xdelta3](https://github.com/jmacd/xdelta). You need your own unpacked Japanese disc image.

| Your source image | Patch |
|---|---|
| Sunrise Eiyuutan 2, Japanese original, SLPS-25070 | `Sunrise-Eiyuutan-2-English-v0.8.0.xdelta` |

```text
xdelta3 -d -s "Sunrise Eiyuutan 2 (Japan).iso" Sunrise-Eiyuutan-2-English-v0.8.0.xdelta "Sunrise Eiyuutan 2 EN v0.8.0.iso"
```

For manual patching of a CHD, extract it to an ISO first. This patch accepts the original Japanese image, not an older English test build. Keep checksum verification enabled.

Source SHA-256:
`5d6f96c972ac65bb5dddbadc832dc749a59b86b8c4507408231bed725b8524e8`

Patched image SHA-256:
`8fa9f17a838b4c22c591467ad343b7130d159efcd00b5cbb413c43175b8e2f7f`

**Boot the new image fresh and load an in-game memory-card save.** Old emulator save states can retain the old executable, text and graphics.

### What's included

- **Story and encyclopedia text.** Integrates all 1,195 rows in the 33 inventoried main-story tables and the 588 character/mech encyclopedia entries. Runtime names, speaker identities, original voices and choices are preserved.
- **Battle captions.** Includes 6,463 of the 6,519 logical rows in the shared battle bank, applied to both physical copies. Bridge orders, attack calls, covering fire, responses and defeat barks are included. The remaining 56 ambiguous lines retain their original Japanese; see [the hold inventory](https://github.com/retro-trans/Sunrise-Eiyuutan-2/blob/main/docs/battle_category_holds_0.2.25.en.json).
- **Movies, episode previews and songs.** Adds 116 English voice-caption cues across 23 attack movies and 16 episode previews, translated preview title cards, and opening lyrics. The opening has 21 timed lyric cues; the ending has 34. Both songs display romaji and English without a Japanese lyric tier. Original encoded audio is retained.
- **Menus and terminology.** English title/options, name entry, travel, battle help, formation, services, information, equipment, save/load episode titles and Trade text, with reviewed character, unit, item and ship terminology.
- **Font and layout repairs.** Proportional English lettering, readable item/pilot lists, consistent reward-item typography, larger equipment summaries, aligned Ship/Captain choices and a wider unit-stat panel. Ordinary dialogue/help boxes retain their original size and position; longer detail layouts are scoped to their content.
- **Latest Trade fixes.** Complete labels and prompts, normal-proportion requirement names, separate quantity columns, full long-item labels and a safer temporary text buffer. Recipes, costs, statistics and transaction rules are unchanged.

### Validation and testing status

The cumulative build passes complete disc verification: **20 files, 5,614 resource packs, 80 event members and 489 movie members**. The release patch was decoded from the exact original Japanese image and checked against the verified target's complete size, SHA-256, SHA-1 and MD5. Source and output fingerprints are supplied in `BUILD-MANIFEST.json` and `README-v0.8.0.txt`.

Focused native checks cover representative menus, formation, reward items, Trade panels, the opening, selected captioned movies and ending lyric-window timing. The newest Trade preview uses synthetic available recipe IDs; the original unlock route and a successful trade were not replayed.

**This is not a fully playtested or completely translated game.** Fifty-six battle rows remain Japanese; five unclear movie tracks were left untouched. Movie subtitles are reviewed machine-assisted transcriptions, with timing qualifications and no human listening certification. Movie re-encoding is lossy. The actual ending-credit composition, all routes, full battle-caption playback and physical PS2/OPL behavior remain unverified. Earlier automated startup/dialogue checks timed out, so successful full-game startup/playthrough is not established by those checks. Later successful isolated previews do not resolve that limitation.

### Downloads and source

Download the `.xdelta` patch, instructions, build manifest, validation report and checksum files from the release assets. No complete game image is distributed. There is no upgrade patch for the earlier local test builds.

Automatic-patching metadata was corrected after the initial upload. The standard manifest, validation report, canonical checksums and central SLPS-25070 registration now describe the existing patch. Its bytes, source/output hashes, v0.8.0 version and original source tag are unchanged. `BUILD-PROVENANCE.json` and `DISC-VALIDATION.json` retain the original reports; current release assets supply the corrected protocol metadata.

GitHub's automatic **Source code (zip)** contains the repository snapshot at this tag: tools, English translation exports, glossary and documentation. Historical build inputs, Japanese source dumps, fonts, external encoders and local movie caches are not bundled. This source snapshot alone is not a one-command rebuild kit. English working exports can include reviewed material beyond the playable build; the manifest and hold inventory describe release coverage.

### How it was translated

This is a **machine translation**, produced and edited with Codex/OpenAI models under binhlt0402's direction. Accuracy review, editorial review and final proofreading were performed with model assistance. These passes are separate from human proofreading or listening; no complete human-proofread line count is claimed. Names and terminology follow the project's glossary and cited references.

Thanks to the creators of [Noto Sans JP](https://github.com/notofonts/noto-cjk) and [IPUenc](https://github.com/ravenDS/IPUenc), and to the emulator and patching-tool communities. The README and release-note structure follows [retro-trans/SRW-Z](https://github.com/retro-trans/SRW-Z), adapted to this project's actual coverage and tests.

### Contribute

Bug reports, proofreading and playtesting are welcome through [GitHub Issues](https://github.com/retro-trans/Sunrise-Eiyuutan-2/issues) or [Discord](https://discord.gg/MssepShjmB). Include the release version, episode/location, a screenshot and whether you started the patched image fresh.

---

The patch is free. Do not sell it or anything made with it. Apply it to your own game image; no complete game images are included.


COMPLETE SOURCE / OUTPUT FINGERPRINTS

{
  "source": {
    "name": "Sunrise Eiyuutan 2 (Japan).iso",
    "size": 2622685184,
    "sha256": "5d6f96c972ac65bb5dddbadc832dc749a59b86b8c4507408231bed725b8524e8",
    "sha1": "599f231a70a33692c80cae9bbad79dc8c92576a3",
    "md5": "8d78fbad987edeeb37d63e4d21db81b2"
  },
  "target": {
    "name": "Sunrise Eiyuutan 2 EN v0.8.0.iso",
    "size": 2627004416,
    "sha256": "8fa9f17a838b4c22c591467ad343b7130d159efcd00b5cbb413c43175b8e2f7f",
    "sha1": "2e74d9e7711abca1806aa5bb6d2400eea255550b",
    "md5": "21e9187411ad70d1d9b2fe92521454fb"
  },
  "patch": {
    "name": "Sunrise-Eiyuutan-2-English-v0.8.0.xdelta",
    "size": 366335745,
    "sha256": "4676e3558584621dd4d55227d7a7e245945cea757f1f0e686bc5853fbd082443",
    "sha1": "89755a2bee8b533eac2e6bdcc89f376e66d49334",
    "md5": "3da6d7867a0232a6f7b3db2267f0b77f"
  }
}
