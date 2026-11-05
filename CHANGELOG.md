# Changelog

## v0.8.0 — first public release — 2026-11-05

- Correct Automatic-patching compatibility after the initial upload: supply Retro Trans's standard manifest/validation/checksum contract and register SLPS-25070 in its shared game library/catalog. Preserve the exact published patch, game output, version and source tag; retain original provenance and disc-verification reports separately.
- Hosted catalog validation and 46 focused shared-tool checks pass. A real-ISO Automatic run with a fresh cache downloads the published patch and reproduces the exact target in 109.656 seconds, then recognizes it as already-current. See docs/automatic_patching_0.8.0.md/json. This verifies the backend, not GUI interaction, CHD conversion or gameplay.
- Package the verified cumulative local v0.2.31 image as public v0.8.0. Game bytes are identical; the public version is not a completion percentage.
- Publish an original-Japanese-disc xdelta patch, complete source/output fingerprints, instructions, validation records and checksums. Decode the patch with source verification enabled and require an exact full-image reconstruction.
- Add a public README and release notes following retro-trans/SRW-Z, with this project's own coverage, model-assisted translation disclosure, credits and remaining 56 battle holds/testing limits.
- Prepare a source repository under retro-trans/Sunrise-Eiyuutan-2 containing tools, English-only exports, glossary, documentation and the social banner. Original images, extracted game data, Japanese script dumps and local caches remain excluded. Historical inputs are not a portable one-command rebuild kit.

## v0.2.31 — Trade translation and font proportions — 2026-11-05

- Create a Sunrise Eiyuutan 2 GitHub social preview matching the supplied navy/cream banner, using the original cover as a reference. Save a 1280×640 upload JPEG (260,253 bytes), generated PNG master, prompt and source notes under work/output/social-preview. Built-in image generation; no repository settings changed.
- Export the opening as a standalone H.264/AAC MP4 with the current romaji/English captions, original video source and complete song audio. Retain 640×384 at 30 fps; hold the final picture for the 23-frame audio tail. Full MP4 decode and subtitle-frame inspection pass. See docs/opening_mp4_export.md.
- Translate the complete Trade caption/prompt category and empty requirement slots, including confirmation, unmet requirements and both references to the shared inventory-limit alert. Review the exchange direction against native item add/subtract operations.
- Restore 26×26 requirement names; separate counts/owned values at x320. Widen the item list to 608 pixels with explicit name/quantity columns and 22×22 fitting for its longest label. Preserve normal help geometry.
- Relocate the temporary list formatter to a 64-byte buffer so the longest complete name and owned count remain safe. Retain all 128 recipe records and transaction rules.
- Five focused checks across all 128 recipes, five native panels and full disc verification pass. Synthetic available recipe IDs; original unlock route/full progression and successful trade unverified. Every ISO byte outside the executable equals v0.2.30. See docs/trade_0.2.31.md/json.

## v0.2.30 — formation submenu and font polish — 2026-11-05

- Shorten Unmanned Unit to Unmanned across eight machines and all 24 name references. Restore normal square pilot-list proportions.
- Translate all three action and four equipment submenu entries. Align Ship/Captain by removing Captain padding.
- Enlarge equipment summaries to normal 26px text with complete per-line fitting at 20/13px when needed; include the native parser advance in measurement and use safe local buffers. Preserve normal help geometry.
- Four focused checks, six cold native previews and full disc verification pass. Synthetic stack-local preview data; original unlocked route/full progression unverified. All ISO bytes outside the executable equal v0.2.29. See docs/formation_polish_0.2.30.md/json.

## v0.2.29 — formation fonts, stats and remaining text — 2026-11-05

- Restore normal text proportions in five formation list consumers; preserve complete labels with uniform fitting and replace byte-padding with compact spacing in four name/size formats.
- Widen the unit stats panel from 256 to 312 pixels, separate class and size fields and fit full stat lines. Exclude invisible class erasure padding from measurement while restoring it before drawing. Normal dialogue/help box and portrait geometry remain unchanged.
- Translate all 33 unit-type records, 364 non-player captain full/display name references and the missed Ship/Captain submenu pointers. Preserve dynamic player names and qualified/provisional terminology.
- Five focused checks, four actual native formation fixtures and full disc verification pass. Synthetic deck/list data; original unlocked route/full progression remain unverified. Preflight evidence retained. All ISO bytes outside the executable equal v0.2.28. See docs/formation_readability_0.2.29.md/json.

## v0.2.28 — consistent item-name font — 2026-11-05

- Replace mixed legacy fullwidth Latin/digits/punctuation with matching proportional English glyphs in item names. HM Parts LvB now matches Repair Materials Lv2 in style and apparent size. Inventory all 335 records/1,005 name pointers; normalize 126 captions across 378 full/display/omission fields.
- Preserve all wording, case, spaces, class/level values, item IDs and descriptions. Original reward renderer, font size, frame, rows, quantity format, gameplay and every unrelated byte remain exact v0.2.27.
- Four focused tests, two actual native reward previews and full disc verification pass. Synthetic reward lists after New Game initialization; original battle triggers/full progression remain unverified. Whole ISO outside executable equals v0.2.27. See docs/item_typography_0.2.28.md/json.

## v0.2.27 — save/load episode titles — 2026-11-05

- Translate all 19 save/load title entries, including Heroes of Light Gather; preserve approved prefixes and title punctuation. Existing numeric saved headers resolve through the updated lookup without save rewrites.
- Relocate the formatter buffer to 64 bytes and remove the old 36-byte truncation limit. Fit long labels with uniform font sizes inside the original list frame; reported title retains normal 26×26 font. All 361 prefix/title combinations fit completely.
- Four focused checks, native Save and Load previews and full disc verification pass. Private preview uses synthetic numeric saved headers and card I/O stubs; physical persistence and full progression remain unverified. Every ISO byte outside the executable equals v0.2.26; inherited limitations retained. See docs/episode_titles_0.2.27.md/json.

## v0.2.26 — special-attack names and readable selector — 2026-11-05

- Translate all 50 distinct captions across 118 special-attack records and 354 full/display/omission fields, including Pile Bunker Surprise Attack. Retain registered names and distinct shortened variants; normalize registered V-MAX typography.
- Restore the special selector to normal 26×26 proportions and widen it to 400 pixels on both sides. Keep full/display names complete; use Omni. only in the native omission field. Original dialogue/help geometry and all costs, stats, IDs, callbacks and voices stay exact.
- Three focused checks, six actual native selector previews and full disc verification pass. Synthetic one-choice/side fixtures; original battlefield triggers and full progression remain unverified. All ISO bytes outside the executable equal 0.2.25. Inherited 56 dialogue holds and startup automation limits remain documented. See docs/special_names_0.2.26.md/json.

## v0.2.25 — shared battle dialogue and input prompts — 2026-11-05

- Integrate 6,463 reviewed shared battle lines in both physical tables, adding 4,895 rows per copy. Inventory all 6,519 source rows and list 56 unresolved language holds explicitly. Include the reported Rie support orders and Posaydal Soldier defeat response.
- Translate the three remaining direct battle input formats; widen the SP popup around its original centre for all 110 device titles. Add native ū font/codec/width support for 59 registered Bakuryū calls. Preserve original normal dialogue boxes, speakers, voices and runtime fields.
- Sixteen checks and full disc verification pass. Native SP prompt and separate macron fixture checked. Automated first-dialogue startup timed out on delivery and prior baseline. Forced new-bark previews did not complete; in-game battle rendering and original battlefield triggers remain unverified. Retain failed evidence and exact private settings. See docs/battle_category_0.2.25.md/json.

## v0.2.24 — card warnings and restored help boxes — 2026-11-05

- Translate the remaining no-save/corrupt warning title and predicates, retaining native slot headings, warning frames and save behavior. Relocate three complete source-reviewed English strings.
- Restore original normal help/status geometry. Fix the0.2.22 shared-constructor regression: extra height is used only for text longer than three lines, and returning to Repair help restores its original box and portrait position. Retain full ability descriptions, fonts and complete0.2.23.
- Five focused checks, full disc verification and fresh muted native warning/help/detail/help preview pass. Exact private settings restored. Synthetic card mode/detail numeric prefix; ordinary menu/battle triggers not replayed. See docs/card_dialog_0.2.24.md/json.

## v0.2.23 — romaji and English song subtitles — 2026-11-05

- Remove the Japanese lyric tier from both songs. Move romaji to the top position and retain English below, with all55 cue texts/times and original Japanese audio unchanged. Retain complete0.2.22.
- All13 focused checks, complete disc verification and2752-frame opening decode pass. Fresh muted native playback verifies the complete opening plus ending two-line cue, instrumental gap, reuse and stop cleanup. Exact private settings restored; actual credits unplayed. See docs/lyrics_display_0.2.23.md/json.

## v0.2.22 — passive abilities and battle rewards — 2026-11-05

- Translate all31 native passive-ability records and the Acquired Items reward heading:63 language objects/122 typed fields, preserving two empty/NULL sentinels. Keep attack/defense phase assignments, percentages, recovery resources and original combat behavior. Cover the complete related ability table rather than only the reported line.
- Reflow complete comments into up to three lines at normal26px width. Use scoped native constructor copies for a five-line status panel, preserving its bottom edge and all original shared factory paths. Retain complete0.2.21, all43 RESOURCE packs,45 overlays and exact captioned movie archive/Japanese audio.
- Independent source review, separate editorial, actual glossary audit and final saved-English proofreading complete. All47 combined checks and full20-file/5,614-pack/80-overlay/489-movie verification pass. Fresh, muted native previews capture the reported ability, longest comment and actual reward renderer/getter with synthetic stats/items. Ordinary battle triggers remain separate. The earlier stalled preview and all final evidence are preserved; private settings restored exactly. See docs/battle_effects_0.2.22.md/json. No release, commit or whole-game completion claim.

## v0.2.21 — battle-entry translations and interactive battle fonts — 2026-11-05

- Include all172 reviewed battle-entry messages in04970_10511, including Rie's combat/launch announcement. Preserve171 original voice cues and the originally unvoiced row11. Rebuild the complete member and pack with new offsets and cached size; retain every0.2.20 translation and captioned movie/audio.
- Fix the separate interactive launch, item and repair lists at26×26 in400-pixel windows on both sides. Restore26-pixel width in Cannon/Support/Repair amount prompts, measure their centering in proportional pixels and reposition numeric children with the widened windows. Preserve selection IDs, availability, callbacks and combat logic.
- Language checkpoint, source guards, glossary audit and saved-English proofreading complete. All40 regression checks and full20-file/5,614-pack/80-overlay/489-movie verification pass. Validation and exact coverage are recorded in docs/battle_readability_0.2.21.md/json. Fresh final boot verifies loaded instructions and font metrics; reported battle panels are not yet replayed in normal gameplay. No whole-game completion claim, release or commit.

## v0.2.20 — integrate later story dialogue — 2026-11-05

- Fix the reported Yellow/Blue Ganba scene by including all31 later story tables:1,135 source rows/5,749 body calls,1,134 additional rows versus0.2.19. All33 inventoried main-story tables now have1,195 rows included. Retain speaker/voice/function/call boundaries, all previous UI and exact captioned movie archive/audio. Rebuild table/pack offsets and update11 cached-size bytes; no production code hook changes.
- Complete source-reviewed editorial fitting, three pending promotions, post-agent names audit and saved-English proof.37 regression checks and full20-file/5,614-pack/80-overlay/489-movie verification pass. See docs/story_dialogue_0.2.20.md/json for native preview evidence, dynamic-name limits and explicit remaining battle-bank coverage. No whole-game completion claim, release or commit.

## v0.2.19 — movie captions, preview cards and song lyrics — 2026-11-05

- Add 116 Whisper-derived English voice cues across 23 attack movies and 16 previews. Translate all 16 main title cards, two extra cards/six labels and 16 preview headings. The reported title is Heroes of Light Gather. Add Japanese lyrics, romaji and English translations for 21 opening and 34 ending cues. Retain complete v0.2.18 and original Japanese audio.
- Limit independent encoded pictures to 30,000 bytes and rebuild PSS interleaving around picture/sample time, preserving original extents and exact ADX streams. Add a bounded native ending overlay driven by ADXT_GetTimeSfreq2, avoiding the game's zero-time clock stub. Hide gaps and clean up on stop/track change. Preserve prior 12 changed packs and 45 overlays.
- Accuracy, separate editorial, substantive source rechecks, post-agent glossary audit and saved-English proof complete. All 25 combined checks, full 20-file/5,614-pack/80-event verification, 40 complete decode counts and 187 visual samples pass. Fresh muted playback covers final previews470/476, attack263, the complete opening and ending cue/gap/reuse/cleanup behavior. Actual credit composition remains unplayed. Five unclear tracks remain unchanged. See docs/movies_0.2.19.md/json for exact scope, hashes, ASR/quality limits and evidence. Original emulator settings restored; no release or commit.

## v0.2.18 — default squad name — 2026-11-04

- Translate the remaining default squad label as Retake Norstan. Cover new-game initialization and existing saved defaults through an exact-match mapping in the shared display getter. Preserve stored squad records, custom names and complete v0.2.17.
- Relocate the 15-byte label, add an 84-byte helper in a proven zero gap and change three guarded words. Independent accuracy, separate editorial, actual glossary audit and saved-English proof complete. Four focused native-instruction/preservation checks pass. Full disc and fresh-boot evidence, hashes and live-panel limits are recorded in docs/squad_name_0.2.18.json.

## v0.2.17 — Information inventory and item-list layout — 2026-11-04

- Translate 228 unique text objects across all 161 unit-device, 21 salvage and one event-placeholder records; repoint 732 typed fields while preserving every non-text record byte. Retain complete v0.2.16 and Japanese voices, including the already translated Information headers and Name/Owned labels.
- Fix clipped item names and drifting quantities with measured 608-pixel columns and complete original arguments. Preserve native selection and scrolling. Fit the long equipment name in its narrow picker, use scoped native small-font controls for four status formats, and measure the equipment-removal prompt in pixels. Relocate 4,497 text bytes; use 1,792 reserved code bytes and 752 guarded word changes.
- Independent accuracy, separate English editorial, actual 1,705-entry glossary audit and saved-English proofreading complete. All 92 combined checks and full 20-file/5,614-pack/80-event verification pass. Fresh final boot validates 3,449 merged words and 1,277 typed strings in memory. The normal-input attempt remained in the opening; affected panels were not individually reached in gameplay. Muted settings restored. See docs/information_0.2.17.md/json for exact scope, hashes and limits.

## v0.2.16 — Modification, Combine/Separate, Recovery and Information — 2026-11-04

- Translate 57 interface objects and 136 unique names/descriptions from all 71 native modification-part records: 193 objects, 284 typed part fields and all 20 combination/separation labels. Include related help, unavailable messages, headers, columns, before/after statistics and six shared attribute captions. Retain complete v0.2.15 and Japanese voices.
- Relocate 4,554 bytes and patch 364 guarded words. Preserve original text, every non-text part field, all prior 12 modified resource packs and 45 overlays. Reflow 18 complete descriptions without word loss. Keep native selector/list geometry; use 22×26 only for the two stat panels' HP rows. Broader CFG companion audit finds no unpatched consumers of changed LUI words.
- Independent accuracy, separate English editorial, compact source rechecks, actual unchanged 1,697-entry glossary audit and saved-English proof complete. All 79 combined checks and full 20-file/5,614-pack/80-event verification pass. Fresh final boot reaches English title commands and validates 2,708 words, 21,669 pool bytes, the 16-byte font tail and 1,053 typed strings in RAM. Original muted settings restored. New service panels were not individually reached in gameplay; the normal-save attempt remained in the opening/title sequence. See docs/services_0.2.16.md/json for exact scope, hashes and limits. No release or whole-game completion claim.

## v0.2.15 — complete compiled Squad Setup category — 2026-11-04

- Translate93 formation source objects plus3shared caption dependencies, covering squad creation/change/copy/deletion, ship/captain/unit/pilot/equipment/item selection, availability, statistics and help. Retain complete0.2.14 and Japanese voices; repair one saved-fp consumer of its existing destroyed-unit message.
- Relocate2,686 bytes and patch223 guarded words. Preserve original text, all prior12 resource packs and45 event overlays. Three short warning-copy branches pass complete English directly to their existing renderer. Fit fixed headers at26px with a160px left box and438px right box, preserving frame separation and the right edge. Resolve branch-delay/saved-register references and scope three shared-caption changes to formation consumers.
- Independent source accuracy, separate root English editorial, compact source rechecks, actual unchanged1697-entry glossary audit and saved-English proof complete. Final71 combined checks and full20-file/5,614-pack/80-overlay verification pass. Fresh final boot validates2,344 patched words,17,115 pool bytes and862 unique typed strings in memory, with original muted settings. Early project save disables Squad Formation; new panels and battle interactions were not individually reached in gameplay. See docs/formation_0.2.15.md/json for delivery hashes and limits. Preserved fit preflight is not the delivery artifact. No release or whole-game completion claim.

## v0.2.14 — complete native battle details and unit/item tables — 2026-11-04

- Translate66 shared battle UI objects, all532 unit-name records,66 equipment records and15 consumable records:838 reviewed source objects and81 complete item paragraphs. Include ship/unit summaries, item names/effects, Cannon/Support EN prompts, repair warnings, Escape and action-plan labels. Retain complete0.2.13 and Japanese voices.
- Relocate14,429 bytes and repoint2,121 guarded words. Preserve every non-text record field and original string. Draw unit/equipment selectors at26×26 in400px mirrored windows; keep all complete short labels and fit every item paragraph into two504px lines. Preserve the actual aligned27-byte confirmation-copy consumer.
- Independent accuracy, separate English editorial, source rechecks of compact wording, actual1697-entry glossary audit and saved-English proof complete. Final64 combined checks and20-file/5,614-pack/80-overlay disc verification pass. Fresh final boot shows English startup/title; all2,121 patched words,14,429 payload bytes and775 typed strings match memory with original muted settings. Battle panels are code/layout checked but were not individually reached in gameplay. Details and delivery hashes are in docs/battle_details_0.2.14.md/json. No release or whole-game completion claim.

## v0.2.13 — complete inventoried travel/tutorial category — 2026-11-04

- Integrate 77 additional source rows and 282 text bodies: the alternate first battle lesson, cannon/support/interception and repair lesson, Cloud Sea warnings and all associated companion/delivery/final-continent travel scenes. All ten inventoried tables now contain 133 English rows, 1,242 original calls and 855 translated bodies, with zero Japanese bodies remaining in this category. Retain the complete0.2.12 content and Japanese voices.
- Preserve both distinct first-tutorial source versions and document the older version's inconsistent attribute relation. Independent accuracy776, separate English editorial, independent accuracy778 for seven compact body edits, actual24-variant glossary audit and saved-English proofreading complete. Rebuild three packs with guarded native cached sizes; apply all four shared travel-member replacements together. Preserve every original message boundary, voice, control and unrelated asset.
- All56 combined checks and full20-file/5,614-pack/80-overlay verification pass, including original-machine-code parsing of every1,242 category call. Fresh final boot passes the English startup card warning and reaches title artwork; cached sizes and prior UI guards match, with original muted settings retained. Later category scenes were not individually played. Coverage, qualifications, delivery hashes and remaining unrelated content are documented in docs/travel_tutorials_0.2.13.md and its evidence JSON. No release or whole-game completion claim.

## v0.2.12 — arrival notices and ship-item tutorial — 2026-11-04

- Integrate all 14 rows of the shared/separate travel tables and seven-row item tutorial: 433 complete text bodies, 529 original calls and 432 voice cues. The reported arrival and Nelfea question are now included in the playable build. Preserve all0.2.11 content and Japanese voices.
- Relocate rebuilt resource tables and update guarded cached pack sizes. Fit complete English within each original body without merging calls, shortening endings or changing source metadata. A separate travel-color profile admits the source warning's color1 while keeping existing story admission unchanged.
- Independent accuracy773 found one learning/teaching agency correction; retain its unusual-source qualification and all source-specific travel place names. Separate English editorial, actual glossary-variant audit and saved-English proof complete. All 51 combined checks and full 20-file/5,614-pack/80-overlay disc verification pass, including the actual native parser for all 529 calls. Fresh native boot reaches English departure and arrival through normal Deon story/flight input; exact registered-resource matching and normal-speed arrival capture pass. Original settings are restored. The item tutorial is parser/layout checked but not reached in gameplay. Scope and final validation are documented in docs/travel_items_0.2.12.md and its evidence JSON. No release or whole-game completion claim.

## v0.2.11 — all inventoried native location labels — 2026-11-04

- Translate all 26 town and nine region table entries, plus 262 location/area/exit captions in 44 event files: 86 source labels, 83 distinct English labels. Cover local destination thumbnails and headers, travel markers, destination choices and dynamic help. Preserve separate kingdom and capital labels and complete glossary spellings.
- Relocate 1,025 new bytes; update 30 compiled table words and 298 overlay words with original/current-baseline guards. Reuse approved English and retain every unrelated loaded byte, destination order, availability, coordinates, prior translation and Japanese voices.
- Independent accuracy771, separate editorial, actual 24-variant glossary audit and saved-English proof complete. All 47 combined checks and the 20-file/5,614-pack/80-overlay disc verification pass. Fresh native boot loads the project Deon save; town header/help and all four Airport-picker captions fit, with normal-speed captures and original emulator settings restored. All 192 guarded words, 35 loaded name entries and 83 complete English labels match the final build. Native evidence, source coverage and remaining work are documented in docs/locations_0.2.11.md and its validation JSON. No release or whole-game completion claim.

## v0.2.10 — destinations and Deon Town — 2026-11-04

- Translate Set Destination and None, shared Deon Town/Astante Fortress Ruins names, all three map61 destination names, and six local Deon area labels. Preserve existing Cloud City translations and use the full glossary spellings. Deon Town now supplies English to the dynamic town header and help substitution; Bar is its actual local venue.
- Relocate complete English into139 new bytes, changing6 guarded executable/data words and11 overlay-pointer words across map36/61. Preserve native picker width measurement, list IDs/order/availability, map coordinates and game behavior. Retain complete0.2.9 and Japanese voices.
- Independent accuracy769 plus map-copy addendum, separate English editorial, actual24-variant glossary audit and saved-English proofreading complete. A dry-run guard caught previously translated Cloud City pointers; retain those and patch the distinct map copies.43 consolidated checks and the20-file/5614-pack/80-overlay disc check pass. Fresh final boot reaches all three requested views by normal story/flight input; full list, Deon marker and town header/help fit at normal speed. All162 guarded words/new payloads and active map/town pointers match. Original settings restored; a new project-owned Deon checkpoint is saved in card1/save slot2 for future tests. Evidence and remaining content are recorded in docs/destination_0.2.10.json. No release or whole-game completion claim.

## v0.2.9 — Astante deck labels — 2026-11-04

- Translate the remaining screenshot labels as Select Destination and Sail, and the current ship name as glossary-approved Astante. Relocate three complete labels into43 guarded bytes; repoint the destination menu entry, sailing branch and both shared ship name pointers. Retain the long ship description, numeric ship fields, dispatch functions, menu geometry and all0.2.8 content.
- Source accuracy767 examined three targets and ten context strings, including the actual travel-radar dispatch and dynamic ship-name getter. Separate editorial,24-variant glossary audit and saved-English proofreading complete.39 combined checks and the20-file/5614-pack/80-overlay disc check pass. Fresh native boot loads the project test save and reaches the sailing deck through normal play; all three labels fit. Original speed/audio/card settings restored, normal-speed capture and156 patched words/new payloads verified. Evidence and remaining content are recorded in docs/deck_0.2.9.json. No release or whole-game completion claim.

## v0.2.8 — Options and message-speed UI — 2026-11-04

- Translate twelve compiled labels: the Options heading, five message/audio settings, five speed grades and the separate ship-system Options label. Retain BGM, SE and source B.E.S abbreviations without inventing an expansion. Preserve native choice order and all Japanese voices.
- Relocate complete English into163 guarded bytes at0x9BBA00. Widen the speed popup and its button areas from112 to192px, keeping center320 and five28px rows. Retain the complete0.2.7 content, including reviewed exit/unsaved warnings and Yes/No.
- Independent source accuracy765, separate editorial, actual24-variant glossary audit and saved-English proof complete.36 combined checks and whole20-file/5,614-pack/80-overlay verification pass. Native final evidence is recorded in docs/options_0.2.8.json. Focused local build; no release or whole-game completion claim.

## v0.2.7 — correct memory-card text centering — 2026-11-04

- Finish the requested town/save/phase translation build with a28-byte guarded ASCII width hook in std1WinPrintf. Native testing found this separate routine still measured every ASCII byte as15px, clipping longer English despite earlier padding. Use the actual proportional font width plus the original2px spacing; retain Japanese/wide-character handling and source-byte advance.
-33 consolidated checks pass, including execution of the real native centering function for narrow/wide English, Yes/No and original Japanese. All previous translations, packs and overlays remain intact. Final disc/native checks and remaining Japanese are recorded in docs/screens_0.2.7.json. This supersedes0.2.5/0.2.6 candidates; no release.

## v0.2.6 — final town/save UI and native choice fixes — 2026-11-04

- Retain all0.2.5 translations; translate four separately stored Yes/No labels used by battle and memory-card selectors. Preserve native choice order. Add display-only left padding to four confirmations and the Last Updated format after native frame-edge clipping was observed. Later native testing showed padding alone was insufficient;0.2.7 corrects the underlying centering routine.
- Independent source follow-up approved all four additional literals; separate editorial, actual24-variant audit and saved-English proof complete. Add guarded choices_patch.py and native reference/padding/retention checks. Native save testing uses a newly created project-owned card, with no personal cards imported or changed. Final evidence and remaining untranslated screens are recorded in docs/screens_0.2.6.json.

## v0.2.5 — town, save and phase UI — 2026-11-04

- Integrate68 compiled menu/save/phase strings,21 location-label occurrences across six town overlays and23 shared help entries. Preserve native message/choice/voice/function boundaries. Relocate complete English into guarded event memory; retain all0.2.4 content and Japanese voices.
- Widen the maintenance-deck menu to216px for Squad Formation. Guard hoisted address pairs, the empty-save-slot branch delay slot and native fixed-length caption copies; use reviewed Load Game, New Save and Overwrite Save captions.
- Independent accuracy760/761, separate English editorial, actual24-variant glossary audit and saved-English proof complete. Consolidated validation tracked in docs/screens_0.2.5.md. This is a focused local build, not a claim that every game screen is translated; no release.

## v0.2.4 — English unit attribute icons — 2026-11-04

- Replace all eight Japanese icon cells in pack22/member10051 with reviewed S/L/P, FL/AA/G, AT/DF codes, with complete English meanings in the accompanying legend. Preserve punctuation, arrows, category colours, alpha silhouette and all native CEL geometry.
- Keep executable byte-exact0.2.3 and every previous integrated change. Add guarded focused builder and future translated-pipeline integration.23 consolidated targeted checks and whole-disc verification pass. Fresh native tutorial shows S/G and L/AA on both units; complete loaded atlas bytes match the build. Original speed settings restored and same-build normal-speed replay checked. Other four codes reviewed as atlas cells. Delivery verified; evidence in docs/battle_icons_0.2.4.json. No release.

## v0.2.3 — readable ship battle menu — 2026-11-04

- Translate the requested ship-status format with reviewed compact Cannon, Support, Repair, Vs Ships and Vs Units captions. Relocate the complete format; preserve numeric arguments, color selectors, percentages and line boundaries.
- Replace all seven orange ship-command labels with clear white Noto Sans lettering; spell End Turn naturally. Preserve palettes, bevels, selection sprites, CEL geometry and resource sizes. Retain all0.2.2 content and original voices.
- Add guarded focused builder and standard pipeline integration.19 targeted checks and complete disc verification pass. Fresh boot reaches the user's exact tutorial line: all five headings/values and all seven white labels fit; red selection marker and Kyo name remain correct. Native pixel/text bytes match the delivered build. See docs/battle_ui_0.2.3.md and the paired native validation report. Other battle interfaces remain outside this focused patch; no release.

## v0.2.2 — all dialogue speaker names integrated — 2026-11-04

- Inventory all860 native pilot records and translate all859 valid dialogue short-name slots. Relocate858 static labels into guarded unused event memory; preserve dynamic chosen player1. Kyo now reads Kyo. Preserve source metadata, portraits and existing full/display fields. Native frame already auto-sizes; longest English278px.
- Complete source-first accuracy751/752/753 across516 contextual groups including excluded sentinel; fix17 misleading offers, fill189 missing groups, register18 qualified terms (1681 total). Separate full515 English editorial, actual24-variant audit and final saved515-label/859-slot proof complete. Preserve unknown identity and written titles.
- Add guarded speaker_patch.py on0.2.1 and wire future translated builds. Retain English menus/Latin keyboard/all11 narration entries and prior integrated dialogue.15 targeted checks pass, including all858 native width-instruction executions and player getter behavior; whole20-file/5,614-pack/80-overlay disc check passes. Initial test-symbol typo corrected with no product change.
- Fresh native boot: six complete story pages visually inspected, including Kyo and custom KanjiA entered through Latin keyboard. All859 loaded pointers/payload match the tested ELF. Other names not individually shown; no whole-game or save/reload approval. Delivery byte-exact. See docs/speaker_names_0.2.2.json. Full/display pilot fields and later dialogue/UI/graphics integration remain unfinished; no release.

## v0.2.1 — opening narration integrated — 2026-11-04

- Insert all11 reviewed04904_10382 narration entries into RESOURCE pack4904, including the Cloud Stream/matter breakdown scene. Preserve47 native calls,11 original voice cues,6 function commands and row7 fullwidth blank. Reflow overlong English inside original calls; no shortening or row merging.
- Guarded reproducible tools/narration_patch.py layers on0.2.0; standard builder admits the same bounded narration profile. ELF remains byte-exact0.2.0, retaining English menus/default Kanji/Latin keyboard. Voices remain original Japanese.
- Independent accuracy749, separate full11 editorial, actual11/24 glossary audit and saved-pack proofreading complete. All11 complete native captions actually inspected via369 context-matched framebuffer samples.11 safety regressions and full20-file/5,614-pack/80-overlay disc verification pass. Same-build replay used for finite automatic-sequence captures; no live text/code edits. Delivery executable/narration pack verified.
- Later reviewed dialogue proposals remain outside this focused build; no whole-game/save-reload approval or release. See docs/narration_0.2.1.json.

## v0.2.0 — requested title/name UI integration — 2026-11-04

- Put New Game, Continue, Versus, Options and the conditional Extras caption into the actual title overlay.
- Seed editable player name with Latin Kanji; default pilot labels use Kanji/Kanji Akatsuki. Preserve native two-byte character storage and dynamic name substitution.
- Open name entry with a Latin/digit/punctuation grid; preserve all upper/lower letters, full alphanumeric and original Symbols pickers; translate controls and widen their window/hit areas.
- Add guarded reproducible focused image builder tools/menu_patch.py on integrated0.1.139; normal translated builds also apply the UI changes. Later language-only proposals are not silently included. Original Japanese audio stays unchanged.
- Independent accuracy748, separate English editorial and actual glossary audit complete. Final saved11-label proof complete. Consolidated validation passed:8 safety regressions, all20 disc files/5,614 resource packs/80 event overlays, fresh native title/name display, case insertion, deletion, arrows and confirmation. Save/reload not tested; old savestates are not converted. No release.

## Translation pipeline checkpoint 723 — 2026-11-03

- Finalize four qualified ability descriptions at718 after713 and Rest Area at722 after717; separate editorial, actual glossary audits and saved-English proofreading complete. Preserve explicit source ambiguities and conditional static-background evidence. Compiled totals: 2,775 whole translations + four formats + four isolated suffixes; five recorded meaning holds now zero.
- Collect all 51 extracted structured tables into a separate English-only language artifact720: 15,154 stored rows, 8,594 distinct source hashes, zero missing extracted rows. Fill 241 stored occurrences from125 reviewed outside-export proposals without changing active/native exports. Preserve duplicate storage/provenance and existing wording; no fresh whole-corpus semantic review claimed.
- Complete CPU machine-source transcription716 of80 audio clips and larger-model724 of8 matching clips; keep all hypotheses unapproved, with source hashes and recognition limits. Preserve failed715 extraction (missing CUDA library, zero transcripts). Continue source graphics/use inventory719. No game builds, native admission, technical/in-game tests or release.

## Translation pipeline checkpoint 712 — 2026-11-03

- Complete the final extracted battle dialogue entry3676 at709 after independent706, separate English editorial, actual glossary audit and separate saved-English proofreading. Preserve a qualified reversal-based joke; do not claim recovery of a unique Japanese homophone payoff. Extracted story/battle meaning holds nowzero; outside-export language proposals124 to125. Original pending records/active exports unchanged.
- Map original VOICE archive/control associations at711 and hash all15,085 audio members at714. Record12,648 associated clips,83 additional exact associated duplicates and2,313 distinct remaining audio payloads across2,354 members. These are review candidates, not confirmed untranslated dialogue or fresh semantic reviews of all catalog rows.
- Start source audio transcription;715 CUDA attempt terminated on missing cublas64_12.dll before any transcript, CPU716 ongoing. Machine hypotheses remain unapproved. Copy complete source inventories and save English-only wordplay review copy. No game build, native admission, tests or release.

## Translation pipeline checkpoint 708 — 2026-11-03

- Complete 50 battle entries in language candidates 702 (13), 705 (20) and 707 (17), after independent accuracy reviews 698/699/697, separate English editing, actual glossary audits and separate saved-English proofreading. Preserve source controls and explicit qualified interpretations; original pending files and active exports remain unchanged.
- Extracted dialogue meaning backlog: 51 to one, Himiko wordplay 3676. Story backlog remains zero. Language-complete proposals outside exports: 74 to 124. Audio-only dialogue coverage remains open.
- Save an English-only review copy and refresh current documentation. Compiled counts/glossary unchanged. No builds, native admission, tests or release; full game remains incomplete.

## Translation pipeline checkpoint 701 — 2026-11-02

- Finalize three story entries at 678 after independent review 673, one independently rechecked English idiom repair, glossary audit and separate saved-English proofreading. Finalize five battle entries at 689 after 685/686; preserve three written prolongations and explicit remaining source uncertainty. Recorded dialogue backlog: 59→51; active exports unchanged.
- Complete 32 whole UI/weapon translations and one isolated acquired-item caption at 688 after 683. Since 657, 322 whole translations are complete at 663/664/671/676/688/700; totals: 2,770 translated whole entries, four unchanged formats and four isolated suffixes. Preserve 40 protected whole objects in 688 and two internal English banner references.
- Register four scoped terms at 681, glossary 1,663. Inventory five new data save/menu labels at 694, then finish independent review 695 and language passes 700. Record finite numeric/tail reviews 674/675 without converting binary fragments into language or claiming full media/ASCII coverage.
- Refresh documentation and English-only proposal inventory; provide 322 new compiled translations, eight finalized dialogue records and one bounded suffix as a review copy. Whole game remains incomplete. No technical tests, builds or release.

## Terminology registration681 — 2026-11-02

- Register four scoped equipment keys after research672: Linear Cannon, Heat Shotel, Twin Buster Rifle and explicitly qualified Bazooka. Preserve competing forms/source anomalies, prior1,659 entries and24 variants; glossary1,663. Select seven scoped component/existing-term dispositions without global aliases.
- Finish three story language proposals at678 after independent673, one independently rechecked idiom repair and separate saved-English proofreading. Recorded dialogue meaning backlog falls from59 to56 battle entries; native integration remains deferred.
- Bind eleven null668 captions separately; independent whole-caption review still required. No builds or technical tests.

## Language review checkpoint 676 — 2026-11-02

- Complete independent accuracy, separate English editing, scripted glossary checks and saved-English proofreading for conversion/parts batches 663 (80) and 664 (78), menu batch 671 (48 translations and two unchanged formats), and materials/menu batch 676 (79 translations and one unchanged format). These add 285 whole translations since checkpoint 657; reviewed compiled language totals are 2,733 whole translations, four unchanged formats and three isolated suffixes.
- Preserve 30 character tables and 80 numeric interiors as protected data; they are not untranslated dialogue. Keep qualified labels, runtime placeholders, source controls and acquisition-tail boundaries documented in the individual reports.
- Story adjudication 670 now has independent support at 673 for three complete English drafts. Parent final editorial/proof adoption remains pending; the recorded dialogue backlog remains 59 entries (three story and 56 battle). Structured exports remain 8,469, including 588 library entries.
- All builds, technical tests, native integration and in-game validation remain deferred until the translation pipeline is complete. No release.

## Translation pipeline checkpoint 657 — 2026-11-02

- Complete 206 whole text translations since 644 at 647/653/659: 2,448 reviewed translations total, plus one unchanged format and three suffixes. The generic inventory counts 2,449 reviewed whole proposals. Preserve the 1962 numeric exclusion and source controls/anomalies.
- Register 22 qualified ship-name keys at 652; glossary 1,659. Bind 35 ship/menu captions at 641, then complete independent review 655 and separate English editing, names and proofreading at 659. Complete 73 equipment/ship entries at 653 after review 650.
- Publish 158 fully drafted conversion/parts/color captions at 651/654 for independent review 660/658. Record three scoped existing-term dispositions at 656 without aliases or new keys. Preserve 75 initial 651 and 79 initial 654 whole defined records during null binding.
- Record the three unresolved story meanings after context review 648. Structured exports remain 8,469, including 588 library entries; 59 dialogue meanings remain held. All technical tests/builds remain deferred; no release.


## Ship-name registration652 — 2026-11-02

- Add22 scoped researched ship-name keys; glossary1,659. Preserve competing reference forms and provisional Zaahatto; no new aliases or changes to prior1,637 entries.
- Keep source codes/class qualifiers exact.35 pending641 captions can now be bound; independent language review remains required. No builds or tests.


## Equipment and ship-name registration649 — 2026-11-02

- Register40 qualified equipment/ship keys after638; glossary1,637. Record8explicit reference fleet-title choices and complete source-shaped alternatives; source DIVISION IDs stay exact. Preserve provisional Marus, competing Falmel/Falmer and other reference limits.
- Two Le Caine ship captions reuse fixed metadata without a new key.636 actual45null bindings and independent review remain required; initial28whole records stay unchanged. No builds or tests.


## Translation pipeline checkpoint644 — 2026-11-02

- Complete240 further whole item/support captions at629/635/642:2,242distinctwhole reviewed entries plus3suffixes. Structured8,469exported/588library unchanged;3story+56battle meanings remain unresolved. No dialogue-completion claim.
- Apply22finite subject/auxiliary repairs at629, six scoped accuracy repairs at635 and one scripted fixedEpsilon correction at642 after whole-corpus name search. Preserve original author/reviewer artifacts.
- Register32series-title keys at640 (glossary1,597), explicitly record source/reference differences, then bind630all62drafts while preserving30initialwhole records exactly. Independent645 remains pending. Workspace636/641 have146selectedobjects in preparation; names638/646 ongoing.
- Record finite facility-context632 nonresolution, bilingual Atelier-Sai artwork retention after parent source-frame inspection, and a bounded uncatalogued literal placeholder observation. All technical testing remains deferred; no build/release.


## Series-title registration640 — 2026-11-02

- Register32 scoped series-caption keys after633; glossary1,597, all previous1,565 records preserved. Record primary/wiki alternatives and two explicit established-title normalization decisions. Original Japanese source remains exact.
- Two existing full-title dispositions recorded;630 actual binding and independent review still required. No new build or tests.


## Translation pipeline checkpoint628 — 2026-11-02

- Complete193 further names at620,255 overlay captions and one isolatedYes suffix at626, and80 item proposals at625 after independent627 nomenclature update. Total2,002 distinct whole reviewed entries plus3suffixes. Structured8,469 exported sources/588library unchanged.
- Register two equipment keys at619 and Jewel of Life/Musoku Naginata at624; glossary1,565. Preserve source足reading, positive alternate names and all old registry records. Original613/615 remain immutable; naming change is scoped in derived625.
- Save two further80-item drafts618/622 for independent review; actual621 review is repairing finite English subject omissions without joining deliberate fragments. Continue62 remaining type/series captions630 and source-context/asset audits.
- Refresh current documentation, English-only reviewed copy and proposal inventory. Entire translation pipeline first; no builds, technical tests, native patch or release.


## Item-name registration624 — 2026-11-02

- Register Jewel of Life and Musoku Naginata; glossary1,565. Preserve positive alternate names, primary足spelling/reading and scoped Arago disposition.
- Author622final binding and guarded prior6131490name update remain required. Original613/615 unchanged; no builds or tests.


## Item terminology registration619 — 2026-11-02

- Register I-Field and Minovsky Particle Dispersal Device; glossary1,563. Select ordinary Radio-Intercept Bombing with explicit lexical limits and positive alternative.
- Preserve all previous entries/variants. Final613binding and independent615review still required; no builds or tests.


## Translation pipeline checkpoint 614 — 2026-11-02

- Finish 52 whole ability proposals plus one isolated suffix at 599, and 240 name labels at 611. Total 1,474 distinct whole language-reviewed proposals plus 2 suffixes; structured 8,469 exported sources/588 library unchanged.
- Register qualified names at 598/603/607/609/617; glossary 1,561. Preserve old entries, variants, source spelling distinctions and positive alternatives. Final 193-name and 268-object overlay drafts now provide 448 complete whole drafts for independent review;13 overlay nulls remain protected/held.
- Save source-only ability-context 600 and finite asset-text audit 612 evidence. Continue item descriptions, unresolved meanings and asset/source inventories.
- Refresh current documentation, provenance inventory and English-only reviewed copy. No build, technical test, native patch or release. Full translation pipeline before one consolidated test phase.


## Scoped overlay naming registration617 — 2026-11-02

- Register19 scoped place/group/music-title keys and two existing-name dispositions from610; glossary1,561. Full song titles, source spelling differences and provisional forms remain explicit.
- Root604 can complete21naming gates before independent268-object review. No builds, native patches or tests.


## Naming registration609 — 2026-11-02

- Register44 source keys from research605/606; glossary now1,542. Preserve prior entries and competing/provisional spelling qualifications. No global alias or source-byte correction.
- Author601 can bind the actual607/609 records before independent193-label review. No builds, patches or tests.


## Source-name dispositions607 — 2026-11-02

- Add three qualified exact source keys for existing Bouleuse Gotho, Chirico Cuvie and Shot Weapon; retain raw spelling discrepancies and all previous entries. Glossary now 1,498. Bind source1194 to existing603 Hayato Kobayashi without a new key.
- Author601 still needs the remaining66 researched name labels and complete193 language review. No global replacement, build or tests.


## Naming registration603 — 2026-11-02

- Register25 lexical keys from research595; glossary now1,495. Preserve all previous entries, fixed Fraw Bow and positive competing spellings. Raiga/Reo, source-order Carla Ejil and the remaining qualified project names are now selected after parent evidence reading.
- All240 author582labels can proceed to actual final binding and independent review. No build, patch, global replacement or tests.


## Static ability source context600 — 2026-11-02

- Record the31-row exskill_info pointer table, corroborating the protected description suffix boundary and separating Charge from Self-Destruct. Four semantic holds remain unresolved; no translation or native adoption.
- Read-only source inspection only; no execution or tests.



## Ability language review599 — 2026-11-02

- Complete independent accuracy, English editing, glossary audit and saved-text proofreading for 52 ability labels/descriptions plus one isolated text suffix. Four unresolved-meaning descriptions remain null; one mixed binary/text whole object stays protected.
- Compiled reviewed total is now 1,234 distinct whole proposals plus two isolated suffixes. This adds 52 whole proposals beyond checkpoint592; structured counts remain unchanged.
- No builds, regression, native admission, font/layout or in-game tests. Complete the entire translation pipeline before one consolidated technical phase.



## Naming registration598 — 2026-11-02



- Register 63 lexical keys from research593/594; glossary now 1,470. Preserve all previous entries and positive naming alternatives, provisional Fritz Manon/Giro Bull, source initials/shortness and fixed surnames. Parent selections are qualified project forms.

- Author582 final binding and independent review remain pending. No global replacement, native build or tests.





## Translation pipeline checkpoint592 — 2026-11-02



- Complete independent accuracy/editorial/glossary/proof passes for 160 further compiled labels at586/591. Total 1,182 distinct reviewed whole proposals plus one isolated suffix. Structured coverage remains 8,469 exported sources, including 588 library entries.

- Register 30 names at580 and 28 at589, preserving old entries/variants and explicit positive alternatives. Glossary 1,407. Required Chinatsu Yūki stays UTF8 with native encoding pending.

- Save 57 ability objects at 596: 52 complete whole drafts, four meaning holds and one protected mixed object with a separate suffix draft. Next 240 names remain in local initial drafting/research; reviewed count excludes them.

- Refresh proposal inventory, English-only review copy and current documentation. Translation pipeline first; no builds or technical tests. No release or native patch produced.





## Terminology update589 — 2026-11-02



- Add28 scoped keys from research584 (26 new lexical names and2 source-spelling associations), bringing the glossary from1,379 to1,407; all old full entries and24 variants remain unchanged. Preserve Chinatsu Yūki in UTF8 with native encoding pending, literal middle initials/source-short names, provisional Kresta and unusual positively paired Vifam names.

- Parent selects the documented wiki-attested Hekkeru/Gotoh/Tomeniku forms as qualified project spellings; conflicting Heckel/Heckle/Goto/Tomenic evidence remains explicit, with no unique official-English claim. Norman Burg/Gellpock associations are contextual, not verified aliases or source repairs. No global replacements, builds or tests.





## Terminology update580 — 2026-11-02



- Add30 scoped lexical entries from577/578, bringing the glossary from1,349 to1,379 without changing earlier entries or24 existing variants. Four game-original unit names remain provisional. Preserve source-short names, fixed nicknames and literal Gunblaze letters; document Miki Jounouchi wiki/primary/sibling differences and Japanese Anubis/Shuten scope. No global replacements, source repair, builds or tests.





## Translation pipeline checkpoint 576 — 2026-11-02



- Complete independent accuracy/editorial/name/proof passes for 433 executable glossary proposals (81 overlaps), 80 additional unit labels and ten further names. Compiled total: 1,022 distinct reviewed whole proposals plus one isolated suffix; 442 additional distinct IDs since 565. Correct Exit/Votoms context errors and scope unidentified Rei provisionally.

- Register 32 names at 568, preserving all old entries and variants. Preserve unusual source glyphs and literal identifiers. Correct a saved preparation-file hash reference in new provenance 572; ten whole translation records unchanged and independently rebound.

- Refresh compiled English-only export and coverage/current documentation. Structured coverage remains 8,469 exported sources, 66 completed integration proposals and 59 meaning holds. Whole-game work continues; no builds or tests.





## Terminology update568 — 2026-11-02



- Register32 scoped names from independent research563 and parent564, preserving all1,317 prior full entries and variants. Keep Masquerade Kong, Grantly Dog and Hermine qualified as provisional project forms; document positive naming alternatives, source-spelling inferences and restricted/indexed access. Add exact Bal-Bud Kayzess source key without changing the earlier key. No builds or tests.





## Translation pipeline checkpoint565 — 2026-11-02



- Complete all language passes for another240 executable unit labels and115 overlay labels since545, bringing compiled whole proposals to580 plus one isolated suffix. Preserve unknown symbols, literal model identifiers and explicitly qualified name choices. No active/native patch promotion.

- Add tools/compiled_coverage.py and an English-only proposal export to count932 unique source IDs across overlapping artifacts (580 language-ready,352 mechanical). Source/data provenance only; no build or tests.

- Glossary1,317 after546/555. Refresh current README/remaining-work status; structured coverage remains8,469 distinct exported entries,66 language-ready integration proposals and59 meaning holds. Continue remaining labels and image/media audit.





## Terminology update555 — 2026-11-02



- Register57 scoped unit-name components and named variants for the executable roster from research549/552/553. Preserve all1,260 prior entries and variants. Document Big Foot source-spelling inference, wiki/primary naming alternatives and restricted/indexed access limits. Anomalous source symbols and literal manufacturer/model identifiers remain protected. No builds or tests.





## Compiled overlay language checkpoint547 — 2026-11-02



- Complete accuracy, English editorial, glossary audit and saved-text proof for115 map/scene-overlay labels (32 distinct names). Save separate reviewed proposals; original548 candidate queue remains unchanged. No caller, live player visibility or native replacement approval.

- Terminology546 adds27 scoped Dragonar name components, bringing the glossary to1,260 entries. Preserve all previous entries/variants. Structured coverage remains8,469 distinct translated/exported entries. No builds or tests.





## Terminology update546 — 2026-11-02



- Register27 scoped Dragonar naming components and variants from research541. Preserve all1,233 previous entries and name variants. Select Geizum as the documented project form; flag three secondary-attested pilot forms as provisional. No builds or tests.





## Compiled translation pipeline545 — 2026-11-02



- Complete all language passes for225 whole executable proposals plus one isolated Imakarum suffix across first240 candidates; preserve12 pointer artifacts, two numeric artifacts and one mixed boundary. Five records overlap existing executable text. No native or display approval.

- Stage548 exact glossary candidates with all four passes pending; keep reviewed coverage separate. Complete battle949 language correction outside active exports. All66 technical integration proposals and59 genuine meaning holds remain explicitly tracked.

- Glossary1,233 after535/543; all prior entries/variants preserved. Structured coverage remains8,469distinct; no builds or tests.





## Terminology update543 — 2026-11-02



- Register9 scoped Eldran/Dougram machine labels from licensed product and dedicated-reference naming: Great Gambaruger, Gekiryuger, Revolger, Jaku Satan, qualified source-short Great Jaku, and four Gunner names. Preserve source-short components, ABITATE F44A and all1,224 previous complete entries/variants. No builds or tests.





## Terminology update535 — 2026-11-02



- Register11 scoped compiled labels: title Sunrise Eiyuutan 2, lexical Shadow, GT-Custom, five Gunblaze labels, bare Lost Number, George and Chibodee. Preserve unexpanded codes and all1,213 prior complete entries/variants. Raw Mk－〒 remains uncorrected and qualified. No builds or tests.





## 0.1.184 language — 2026-11-02



- Add17 entries of04930_10408,31 of04931_10409,25 of04932_10410,28 of04933_10411,23 of04934_10412,one192-body navigation record of04935_10413,7 of04950_10473 and21 of04951_10474 after independent meaning review, separate English editing, glossary audit and complete saved-text proofreading. Preserve874 voiced passages. Nine scoped source repairs applied; native/rendered status pending.

- Six developer/story proposals509 and59 Unicode battle proposals525 complete all language passes separately; technical integration outside active exports remains pending. No native parser relaxation or ASCII replacement of required Bakuryū names.

- Register4 scoped terms through515/522/529: Chibodee Gals, bare Astragius/Crescent and King of the Braves. Glossary1,213 preserves all previous completeentries/variants and documented authority/access limits.

- Coverage8,469 distinct translated /125distinct and241stored remain. Physical drafts14,913=8,510canonical+6,403aliases. Seven prior executable literals separately;77new compiled drafts outsidecounts. Historical native approval3,780 unchanged.

- Remaining whole-game work includes executable/overlay classification and translation, held meanings/encoding integration, images/movies/audio audits. No builds or tests run; all testing deferred until the entirepipeline is complete.





## Terminology update529 — 2026-11-02



- Register scoped King of the Braves epithet from the primary Sunrise bilingual series title for the compiled chapter heading. Standalone shortening is qualified; all1,212 prior complete entries/variants remain unchanged. No builds or tests.





## Terminology update522 — 2026-11-02



- Add scoped bare location labels Astragius and Crescent from compiled menu strings and unchanged full continent entries. Preserve all1,210 previous complete entries and variants; no galaxy/geography import or global alias changes. Translation pipeline only; no builds or tests.





## Terminology update515 — 2026-11-02



- Register Chibodee Gals from the dedicated bilingual reference with direct-access limits recorded. Preserve all1,209 previous complete entries and variants. No extra member names, relationships or biography enter the dialogue. Translation pipeline only; no builds or tests.





## 0.1.183 language — 2026-11-02



- Add47 entries of04927_10405,62 of04928_10406,58 of04929_10407 and6 of00023_01234 after independent meaning review, separate English editing, glossary audit and complete saved-text proofreading. Preserve1,061 voiced passages, including192 travel announcements in three voice variants.

- Record ten meaning/grammar/delivery repairs and one highlighted-address punctuation correction. Keep all current native/rendered status pending.

- Register10 scoped terms through501/505/511: glossary1,209, preserving priorcompleteentries/variants. Gyre Garing follows primary/reference spelling despite sibling difference; Mediator remains qualified lexical project form.

- Coverage8,316 distinct translated /278 distinct and394 stored remain. Physical drafts14,760=8,357canonical+6,403aliases. Seven executable literals separately; historical native approval3,780 unchanged.

- Next153 story entries are drafted or underway. Six developer/story entries remain outsideactiveexports with unusualnativeformat flagged. No builds or tests run; all testing deferred until the entirepipeline is complete.





## Terminology update511 — 2026-11-02



- Register Gyre Garing from the primary bilingual heading and Mediator as a qualified lexical project form agreeing with the sibling. Record sibling ship-spelling differences and access limits. Faye-Faye remains repeated dialogue address, with no new nickname or alias. Preserve all1,207 previous entries and variants. Translation pipeline only; no builds or tests.





## Terminology update505 — 2026-11-02



- Register Serene Mind with indexed bilingual reference and direct-access limits, and Grados Tower as a qualified compound of the fixed name. Preserve all1,205 previous entries and variants. No imported skill effects or original-anime geography/chronology. Translation pipeline only; no builds or tests.





## Terminology update501 — 2026-11-02



- Add Cloud City, Astante Fortress and four scoped bare destination stems A/Ku/Lau/Na from source navigation and fixed full names; Cloud City agrees with the sibling glossary. Preserve all1,199 prior complete entries and variants. No one-kana global substitutions, ship/fortress conflation or new official-English claims. No whole-line approval, builds or tests.





## 0.1.182 language — 2026-11-02



- Add25 entries of04924_10402,58 of04925_10403 and33 of04926_10404 after independent meaning review, separate English editing, glossary audit and complete saved-text proofreading. Preserve575 voiced passages.

- Record six meaning/grammar repairs, independently rechecked help-offer wording, and three punctuation repairs. Retain native/rendered status pending and historical planned-defeat inference expressly qualified.

- Register17 scoped terms through486/492/496: glossary1,199, preserving all1,182 earlier complete entries and variants. Source-short forms retain their limits; Siruna and Tilfy remain openly provisional project spellings.

- Coverage8,143 distinct translated /451 distinct and567 stored remain. Physical drafts14,587=8,184canonical+6,403aliases. Seven executable literals separately; historical native approval3,780 unchanged.

- Six additional developer/story entries are drafted and independently compared outside active exports; unusual native formatting remains pending. No builds or tests run; all testing deferred until the entire pipeline is complete.





## Terminology update496 — 2026-11-02



- Add Chiron Castle and Goraon from directly read dedicated bilingual reference fields, with scope and variant limits recorded; add source-short Foizon without Gow. Preserve all1,196 previous complete entries and variants. No other-game routes or ship specifications imported. No whole-line approval, builds or tests.





## Terminology update492 — 2026-11-02



- Register Shuffle Alliance and four title calls using direct Japanese primary and qualified English reference evidence; normalize the source Queen variant to Queen the Spade. Keep King of Hearts unchanged.

- Add provisional Siruna/Tilfy from explicit local mother/childhood-friend context, plus scoped Shuud/Siegel/Shuten and Gon Jem Squad source forms. Preserve all1,185 prior complete entries and variants. Ordinary dock remains common vocabulary. No whole-line approval, builds or tests.





## Terminology update486 — 2026-11-02



- Add source-short Amonduul and Mian from fixed full project entries, plus scoped Musai from direct official bilingual name stems. Preserve all1,182 earlier complete entries and variants. Ordinary assembly hall remains common vocabulary. No added surnames, ship suffixes, alternate-continuity biography or whole-line approval. No builds or tests.





## 0.1.181 language — 2026-11-02



- Add52 entries of04919_10397,21 of04920_10398,55 of04921_10399,16 of04922_10400,49 of04923_10401,10 remaining00023_01233 menu/system entries and14 side-scene entries across05611_01235/01236/01237/01238. Preserve1,176 voiced passages and1 function command.

- Complete independent accuracy, separate English editing, shared glossary audit and all217 final saved-text proofreading; keep native/rendered status pending. Keep04922_10400:2 inactive with both full conditional alternatives.

- Register6 scoped terms through463/469/480/481; glossary1,182 with all1,176 earlier complete entries and variants unchanged. Distinguish project labels and provisional source-short names from attested official English.

- Coverage8,027 distinct translated /567 distinct and683 stored remain. Physical drafts14,471=8,068canonical+6,403aliases. Seven executable literals separately; historical native approval3,780 unchanged.

- No builds or tests run; all testing deferred until entire translation pipeline completion.





## Terminology update481 — 2026-11-02



- Register scoped short Binzvanker from the existing provisional Redros Binzvanker project spelling, retaining all 1,181 earlier complete entries and variants. Source-short references retain their scope and unknown gender. Ordinary highlighted teahouse remains common vocabulary. No whole-line approval, build or tests.





## Terminology update480 — 2026-11-02



- Add scoped short Defense Class for source防衛組, retaining the full Earth Defense Class entry unchanged. Direct primary English synopsis confirms the full name; the short label is a documented project construction. Preserve all1,180 prior complete entries/variants. No dialogue approval, global replacement, build or tests.





## Terminology update469 — 2026-11-02



- Register scoped Ryo-group Troopers and Arago Castle from source and naming review. Preserve Trooper machine classes and all1,178 prior complete entries/variants. Indexed authority and failed direct relevant-page access remain documented; no biography or mechanics imported. No whole-line approval, build or tests.





## Terminology update463 — 2026-11-02



- Register Heroic Tales Mode and Heroic Tales: Run 1 as qualified project UI labels. Target-game wiki search text corroborates Japanese mode identity; direct page search did not expose the matching passage. English is a documented semantic choice, not verified official localization. Preserve all1,176 prior full entries and variants. No global substitution, build or tests.





## 0.1.180 language — 2026-11-02



- Add all73 entries of04914_10392,6 of04915_10393,59 of04916_10394,8 of04917_10395,10 of04918_10396 and11 opening entries of04904_10382 after accuracy, editorial, glossary and full saved-text proofreading. Preserve798 voiced passages and6 function commands.

- Document meaning repairs, independently rechecked editorial changes and unchanged deliberate fragments; keep native/rendered review pending.

- Register28 scoped terms through research425/434/436/450/455, preserving all1,148 previous complete entries/variants; current glossary1,176. Record project forms, reference-continuity limits and ordinary excavation-site prose.

- Coverage7,811 distinct translated /783 distinct and900 stored remain; physical drafts14,254=7,851canonical+6,403aliases. Seven executable literals separately; historical native approval3,780 unchanged.

- No build or tests run; all testing deferred until the entire translation pipeline is complete.





## Terminology update455 — 2026-11-02



- Add nine scoped names/addresses for the next scenes: VOTOMS rider wordplay, Heloram Kanjelman III, Pota, Tora-chan, Mobile Trace System, Sayla, Artesia, Zanzibar and Iron Castle. Keep excavation site ordinary prose. Preserve all prior1,167 complete entries and variants. Qualified short forms and external continuity limits recorded. No dialogue approval, global replacement, build or tests.





## Terminology update450 — 2026-11-02



- Register Terra, Terra continent, Bask Om and the unfinished Zeta stem after source and naming review. Terra remains a qualified project form; Bask spelling follows the dedicated reference without importing alternate-continuity rank; Zeta does not complete the interrupted reference. Preserve all previous1,163 full entries and variants. No dialogue approval, global substitution, build or tests.





## Terminology update436 — 2026-11-02



- Record Astante II as the existing fixed Astante stem plus the source Roman numeral. Explicitly qualify this project construction and keep the original ship distinct. Preserve all1,162 previous full entries and variants. No dialogue approval, global substitution, source, MAIN, export, build or test changes.





## Terminology update434 — 2026-11-02



- Register the ship Whale and short place key Mizun after source/context and naming review. Reuse the existing fixed Mizun spelling without importing planet geography. Preserve all previous1,160 full glossary entries and variants. No dialogue approval, global substitution, source, MAIN, export, build or test changes.





## Terminology update425 — 2026-11-02



- Register eight story labels and four separately timed chant fragments from research422, preserving all previous1,148 complete glossary entries and variants. Explicitly qualify project romanization, indexed-only evidence and one chant reading normalization. No dialogue approval, global substitution, source, MAIN, export, build or test changes.





## 0.1.179 language — 2026-11-02



- Add 69 selected entries from04910_10388, all2 from04911_10389, all55 from04912_10390 and all9 from04913_10391 after independent accuracy review, separate English editing, glossary audit and full saved-text proofreading; preserve790 voiced passages.

- Keep04910:24/26 as semantic holds with four full alternatives; name research does not resolve moon/month timing or the subsequent power bearer.

- Restore04912:0 personal potential to guide evolution through conflict. Improve04911:0 grateful uptake and04912:16 suspicion phrasing after independent renewed source review. Correct04913:3/7 attribution notes and shared qualification only; English unchanged.

- Register five407 and five419 terms, preserving all1,138 previous full glossary entries and variants. Current glossary1,148; qualified unattested forms and indexed-only authority remain explicitly documented.

- Coverage7,644 distinct translated /950 distinct and1,067 stored remain. Physical drafts14,087=7,684 canonical+6,403aliases; seven executable literals separately. Historical native approval3,780 unchanged;10,307 physical drafts await final tests.

- No build or tests run; all testing deferred until the entire translation pipeline is complete.





## Terminology update419 — 2026-11-02



- Register Mt. Soukai, Iron City, Kurakku, Omuga and Senjinmaru with naming evidence/access limits. City/creature/destination project forms remain explicitly qualified; no outside world or unit mechanics added. Preserve all previous1,143 complete entries, aliases and variants. No dialogue, source, MAIN, export, build or test changes.





## Terminology update407 — 2026-11-02



- Register Ferario, Pradon, Laas Wau, Furaon and Elf Castle with bounded naming evidence and access limits. Pradon is explicitly a project transliteration; unresolved identity metadata stays unknown. Preserve all previous1,138 full entries, aliases and variants. Moon/month timing and the power-bearing actor remain separate meaning holds. No dialogue, source, MAIN, export, build or test changes.





## 0.1.178 language — 2026-11-02



- Add all47 entries of04908_10386 and all14 entries of04909_10387 after independent meaning review, separate English editing, shared terminology check and complete final proofreading. Preserve560 source calls,335 text bodies/voices,383 literal segments, all controls/LFs and raw speaker headers.

- Apply two guarded meaning repairs at04909:0/6 and five punctuation-only corrections at04909:1/6 and04908:4/7/8. Preserve full bargain, snake-proverb completion, lethal commands, directional debt and explicit death statement. Unknown actors/referents remain qualified.

- Register LCT as source-preserved acronym only and Phantom Lady as the existing qualified Fyana nickname; all prior1136 complete glossary entries/variants remain exact. Local human-recruitment ATpilot decisions at04908:2/04909:5 do not change the global VOTOMS entry or add a variant.

- Export13952 physical drafts covering7509 distinct structured entries;1085 distinct/1202 stored entries remain. Historical native approval stays3780. No builds or tests ran; all testing remains deferred until entire translation pipeline completion.





## Terminology update396 — 2026-11-02



- Register source-preserved LCT and the established Phantom Lady epithet, with research limits. Preserve all previous1,136 complete entries and aliases. Record source-specific AT pilot wording for two human recruitment scenes; do not change the profile-scoped bareterm entry or globally replace machine/series uses. No dialogue, source, MAIN, export, build or test changes.





## 0.1.177 language — 2026-11-02



- Add all 69 entries of 04906_10384 and all 15 entries of 04907_10385 after independent meaning review, separate English editing, shared glossary audit and complete final proofreading. Preserve 689 source calls, 402 text bodies, 401 voiced passages, 445 literal segments, every control/LF and raw speaker header.

- Apply eight guarded corrections at 04906:0/8/9/10/20/21/34/45. Preserve the other 61 complete records there and all 15 complete records in 04907. Keep the unvoiced pause at row31 and raw0 continuations unchanged; keep the row63 patient inference explicitly qualified with its grammatical alternative. No invented plot, technical outcome or complete reaction.

- Register Karaba from source and dedicated-wiki naming research, with authority/access limits; preserve all prior 1,135 full glossary entries and variants.

- Export 13,891 physical drafts covering 7,448 distinct structured entries; 1,146 distinct/1,263 stored entries remain. Historical native approval stays 3,780. No builds or tests ran; all testing remains deferred until entire translation pipeline completion.





## Terminology update393 — 2026-11-02



- Register Karaba as a qualified project organization name after actual source and two direct dedicated-wiki reads. Preserve all previous1,135 complete entries and spelling variants. Retain the speaker’s full denunciation without importing external ideology, membership or mechanics. No dialogue/source/MAIN/export/native/build/test changes.





## 0.1.176 language — 2026-11-02



- Add the complete 42-entry/140-voice combat tutorial after independent meaning review, separate English editing, actual glossary audit and complete final proofreading. Keep all 167 literal segments, controls, line feeds, voices and raw speaker headers.

- Apply guarded meaning corrections at0,11,21,28,32,36; preserve the other36 complete candidate records. Retain and flag original8 duplicate attribute relation,17 action/order uncertainty and34 malformed EN wording; no silent source, parallel-table or runtime-mechanics repair.

- Register9 qualified terms: Von Braun, Audhumla, Hong Kong, Hong Kong City, elecar, Kilimanjaro, Fraw Bow (spoken Fraw), Main Street and unnumbered Green Noa. Preserve every previous glossary entry/variant and old Green Noa1 wording. Record actual primary/wiki/indexed/failed-access limits and compositional Titans fortress policy.

- Export13,807 physical drafts covering7,364 distinct structured entries;1,230 distinct/1,347 stored entries remain. Historical native approval stays3,780. No builds or tests ran.





## Terminology update390 — 2026-11-02



- Append9 qualified project terms for upcoming story/navigation text: Von Braun, Audhumla, Hong Kong, Hong Kong City, elecar, Kilimanjaro, Fraw Bow (spoken Fraw), Main Street and unnumbered Green Noa. Preserve all previous1,126 complete entries and every variant.

- Record actual primary/wiki/indexed/failed access limits and retain target-only geography and source short forms. Titans fortress remains compositional fixed Titans plus ordinary fortress. No dialogue, source, export, native approval, build or test changes.





## 0.1.175 language — 2026-11-02



- Add all 95 shop/trade/gift story records after independent meaning review, separate English editing, actual terminology audit and complete final proofreading. Preserve all earlier full records and aliases.

- Apply guarded corrections only at 50 and 86; preserve the other 93 full candidate records. Retain all internal dialogue turns, row4 raw speaker0 continuation, row94 unvoiced function/argument/dynamic-name/Yes-No choice and every literal control/LF.

- Preserve complete historical author qualification groups within their respective context ranges. Final row decisions supersede explanations of replaced wording; row50 drops the obsolete pre-sent reference.

- Recheck the existing profile0 age decision: retain the documented wiki-priority age16 override against original18, with version discrepancy unresolved. No profile, glossary or historical native-approval mutation.

- Export 13,765 physical drafts covering 7,342 distinct structured entries; 1,252 distinct / 1,389 stored entries remain. Historical native approval stays3,780. No builds or tests ran.





## 0.1.174 language — 2026-11-02



- Add all 172 field/battle-transition rows with independent meaning review, separate English editing, actual glossary audit and complete final proofreading. Keep every literal source control, LF, speaker, voice, function and row boundary.

- Apply guarded source-reviewed corrections at 43, 158 and 159; keep the other 169 complete candidate records unchanged. Preserve the unvoiced format at 11 and all five distinct silence entries. Do not invent a battle-table alias or native trigger proof.

- Register Liberation Front and Liberation Front Base as qualified short project forms from actual source and researched context; preserve all previous 1,124 full glossary entries and all spelling variants.

- Export 13,670 physical drafts covering 7,247 distinct structured entries; 1,347 distinct / 1,484 stored entries remain. Historical native approval stays 3,780. No builds or tests ran.





## Terminology update 374 — 2026-11-02



- Register Liberation Front and Liberation Front Base as qualified project forms after original-source and official Japanese context review. Retain shortened source labels without importing Earth, branch or headquarters expansions. Preserve all prior 1,124 glossary entries exactly; no translation bodies, builds or tests changed.





## 0.1.173 language — 2026-11-02



- Add the final 39 battle-table entries after independent meaning review, separate English editing, the actual 7,102-unit glossary audit and complete final proofreading; preserve all 6,364 earlier full records and alias mappings.

- Document the finite 39-row tail exception ending at source row 6518. Retain ordinary full clauses, plural targets, strategic purpose, harsh threats, self-reference and deliberate interrupted disbelief. Unknown native speaker 740 retains null canonical English identity, gender and profile.

- Battle MAIN now contains 6,403 of 6,519 entries; 57 language gaps and 59 font/encoding holds remain excluded. Retain all original controls, LF, voices and functions, including four trailing LFs at 6502, 6505 and 6510.

- Export 13,498 physical drafts covering 7,079 distinct structured entries; 1,515 distinct entries remain. No builds or tests ran. Historical native approval stays 3,780; whole-game translation remains incomplete.





## 0.1.172 language — 2026-11-02



- Add 159 battle lines after independent meaning review, separate English editing, the actual 7,063-unit glossary audit and complete final proofreading; preserve every earlier full record and alias mapping.

- Improve 6424 to natural preparation-to-cover phrasing and 6457 to natural attack-preparation and finishing-intention commands after focused source review. Preserve agency, benefactive support, causal wait, intent and all source controls/LFs/voices.

- Keep malformed 6432 unresolved rather than selecting opposing positive/negative interpretations or a polarity-neutral omission. Preserve all three guarded alternatives and raw source.

- Export 13,420 physical drafts covering 7,040 distinct structured entries; 1,554 distinct entries remain. No builds or tests ran. Historical native approval stays 3,780.





## 0.1.171 language — 2026-11-02



- Add all 160 reviewed battle lines from rows 6160–6319 after independent meaning review, separate English editing, the actual 6,904-unit terminology audit with zero changes, and separate final proofreading of all saved lines. Preserve all 6,045 earlier full records and alias mappings.

- Register Taida as a researched character project spelling after reviewing five scoped facts and seven authority/access records. Prefer the directly observed bilingual wiki character row over indexed competing spellings; preserve all previous 1,123 entries and add no aliases. External identity metadata does not expand the full world-absence question or insult in 6217.

- Improve 6222 to the natural bare battle call Covering attack! after a focused source recheck. Preserve its nominal call and unresolved provider, with no invented recipient, own-only agent, firing mechanism or successful result. Keep the other 158 initial full candidate records exact.

- Preserve harsh threats, full repetitions, expense complaint, support directions, modal confidence, genuine cries/self-interruptions/unfinished conditional and all source controls, line breaks, headers and voices, including the nonmonotonic 6198–6199 voice IDs.

- Export 13,102 physical drafts covering 6,881 distinct structured entries; 1,713 distinct entries remain. Historical native approval stays 3,780. Save another complete 80-line draft through 6399 with all stages pending; review of subsequent text continues. No builds or tests ran.





## 0.1.170 language — 2026-11-02



- Add all 160 reviewed battle lines from rows 6000–6159 after independent meaning review, separate English editing, the actual 6,744-unit terminology audit with zero changes, and separate final proofreading of every saved line. Preserve all 5,885 earlier full records and alias mappings.

- Restore the supporting-attack predicate in 6046 and 6053 alongside ally withdrawal and the separate preparation request. Keep attack broader than gunfire and retain the qualified conventional military directive. Preserve distinct speaker headers for the repeated Zechs/Milliardo wording and voices.

- Register the researched short project form Maser Missile after full review of eight authority/access records. Acknowledge the indexed extended wiki headword and source short-form scope; add no unspoken modifier, alias, projectile count, effects or official-game-English claim. Keep 6002 a genuine noun cry.

- Retain the other 157 initial full candidate records exactly. Preserve full support requests versus offers, survival condition, pride oath, signal-fire/gift/wake-up/pounding/hell imagery, threats and genuine cries, self-interruptions and concessive fragments.

- Export 12,782 physical drafts covering 6,721 distinct structured entries; 1,873 distinct entries remain. Historical native approval stays 3,780. All 588 encyclopedia entries retain reviewed English. No builds or tests ran.





## 0.1.169 language — 2026-11-02



- Add 159 reviewed battle lines from rows 5840–5999 after independent meaning review, separate English editing, the actual 6,584-unit terminology audit with zero changes, and separate final proofreading of all saved lines. Preserve all 5,726 earlier complete records and alias mappings.

- Resolve 5979 as a qualified conventional Ready cue before its same-row preparation question. Preserve the full main-gun announcement and question; acknowledge the alternative Lady reading without inventing a female addressee or claiming heard delivery.

- Retain 5903 as a semantic hold: exact written perish/cease and possible intended hold out/endure are materially opposed. Keep both full guarded alternatives unselected and leave the Japanese source untouched. Retain the other 159 initial full candidate records exactly.

- Preserve full violent threats, repetitions, imagery, military permission/request distinctions, genuine causal and suspended fragments, original low voice numbers, extra line breaks and the positive stored voice-pool association for 5990 without guessing its runtime category.

- Export 12,462 physical drafts covering 6,561 distinct structured entries; 2,033 distinct entries remain. Historical native approval stays 3,780. Save two further 80-line drafts through 6159; their language review remains separate. No builds or tests ran.





## 0.1.168 language — 2026-11-02



- Add all 160 reviewed battle lines from rows 5680–5839 after independent accuracy review, separate English editing, the actual 6,425-unit terminology audit with zero changes, then separate final proofreading. Preserve all 5,566 earlier complete records and alias mappings.

- Register the qualified project epithet the Untouchable after full naming-evidence review. Preserve all previous 1,121 glossary entries, fixed character names and nicknames. Add no aliases, mechanics or assumed identity for the omitted subject in 5784; retain its full expectation, pause and question.

- Improve 5788 to a natural firing directive after a focused source recheck, retaining its broad as-is qualifier. Keep the other 158 initial complete records exact. Preserve source imagery, harsh threats, military acknowledgments, genuine vocatives and uncertainty about current events.

- Preserve the exact duplicate source records and voice at 5764 and 5766 as separate rows. Export 12,144 physical drafts covering 6,402 distinct structured entries; 2,192 distinct entries remain. Historical native approval stays 3,780. No builds or tests ran.

- Save two more 80-line drafts through row 5999 with 158 complete candidates and two full guarded holds. One concerns a possible Japanese source typo; the other concerns a readiness cue versus a form of address. Their independent meaning reviews remain separate from adoption. Preserve the positive stored voice-pool reference to 5990 without inventing its runtime category.





## 0.1.167 language — 2026-11-02



- Add all 160 reviewed battle lines from rows 5520–5679 after independent accuracy review, separate English editing, the actual 6,265-unit terminology audit with zero changes, then separate final proofreading. Preserve all 5,406 earlier complete records and alias mappings.

- Resolve temporary draft hold 5610 with a full neutral completed-deed reaction and own refusal to leave things there. Keep the unproved actor and celebratory/provoked delivery open; preserve all three original alternatives as historical evidence.

- Smooth 5673’s stiff purpose clause after a focused source recheck, retaining the full first-person firing declaration and qualified emphatic purpose. Preserve the other 158 initial complete records. Keep the complete Leccee-name joke as a qualified deliberately poor pun, without registering a new spelling.

- Retain original controls, all line breaks, voices and row boundaries. Record author-stage pending metadata separately from current language review; no native or display approval is implied.

- Export 11,824 physical drafts covering 6,243 distinct structured entries; 2,351 distinct entries remain. Historical native approval stays 3,780. No builds or tests ran.

- Save the next two 80-line drafts through row 5839: 159 complete candidates plus one terminology hold with a full conditional request. All four draft stages remain pending; separate naming research continues.





## 0.1.166 language — 2026-11-02



- Add all 160 reviewed battle lines from rows 5360–5519 after independent accuracy review, separate English editing, the actual 6,105-unit terminology audit with zero changes, then separate final proofreading. Preserve all 5,246 earlier complete records and alias mappings.

- At 5479, restore supporting attack without the unsupported restriction to firing. At 5516 and 5518, restore complete preparation commands. Improve 5459’s stiff submit-to collocation after a focused source reread, retaining rhetorical refusal and dismissive degree. The other 156 initial complete records remain exact.

- Keep all eight original unvoiced bodies at 5396–5403 with exact flags, speaker, zero voice and source hash, and record their separate future integration requirements. Preserve exceptional line-break tails, moral good/evil aura qualifiers, support direction, genuine volition and deliberate fragments. Do not infer current bridge roles from earlier standard pools.

- Adapt the independent reports to the existing adoption schema while preserving every original field and proposal. Verify both their original formatted-record hashes and the equivalent compact helper hashes; no translation is changed by this conversion. Clarify author-stage pending metadata separately from current language review.

- Export 11,504 physical drafts covering 6,083 distinct structured entries; 2,511 distinct entries remain. No new holds in this checkpoint. Historical native approval stays 3,780. No builds or tests ran.

- Save the next complete 80-line draft, including a provisional English adaptation of the Leccee-name joke, with all source frames and explicit language uncertainties. Its independent meaning review is saved; it has no final language or native approval yet.





## 0.1.165 language — 2026-11-02



- Add all 160 reviewed battle lines from rows 5200–5359 after independent accuracy review, separate English editing, the actual 5,945-unit terminology audit with zero changes, then separate final proofreading. Preserve all 5,086 earlier full records and alias mappings.

- Complete both clauses of 5234 with the registered project term Head Hunter and the full pride-as-my-shield image. Keep Headliner distinct; add no military-rank, unit or game-mechanic interpretation. Original author-stage unregistered metadata remains historical, with current naming chronology recorded separately.

- Correct 5291 from Thanks to Sorry after a focused source reread. The standalone formula supports a conventional apology without an invented cause or helper; grateful indebtedness remains a qualified pragmatic alternative. After a separate source recheck, improve 5304 from come on to then come, retaining its full conditional and firm command. The other 157 initial complete candidate records stay exact.

- Preserve all 24 voiced ellipsis bodies, six duplicate source frames as distinct rows, exceptional line-break tails including the five-call ending at 5308, and source voice 567 at 5273. Keep unknown identities, fixed null metadata, affectionate older-man address and unproved triggers qualified.

- Export 11,184 physical drafts covering 5,923 distinct structured entries; 2,671 distinct entries remain. No new holds in this batch. Historical native approval stays 3,780. No builds or tests ran; whole-game translation remains incomplete.





## 0.1.164 language — 2026-11-02



- Add 133 reviewed battle lines from rows 5040–5199 after independent accuracy review of all 160 assigned rows, separate English editing, the actual 5,785-unit terminology audit with zero changes, then final proofreading of every saved line. All 4,953 earlier complete records and alias mappings remain exact.

- After focused source rereads, replace the formal defeat question at 5056 with a complete conversational question that keeps the patient unspecified. Improve the coordination-and-attack directive at 5110. These two complete records change; the other 158 initial records remain exact. Retain exclamatory rhetorical boasts at 5125/5132 with their delivery qualifications.

- Preserve all 27 canonical Bakuryū English proposals and Cutter firing commands as encoding holds. Keep the exact trailing control at 5186, four-line-break endings at 5082/5193, header740/voice782, source spelling anomalies, genuine unfinished fragments, full threats and reporter wordplay. Unverified speaker740 identity/gender remain null.

- Allow an explicitly reviewed shared context fact when combining slices with different context schemas; reject contradictions and preserve both original range bases and all row guards. The first dry run stopped because there was no identical shared context field; no data was written. The corrected dry run showed the full intended changes before writing.

- Export 10,864 physical drafts covering 5,769 distinct structured entries; 2,825 distinct entries remain. Through 5199, 55 meaning gaps and 59 encoding holds remain excluded. Historical native approval stays 3,780. No builds or tests ran; the whole game remains incomplete.

- After the checkpoint164 terminology audit and final proofreading under 1,120 entries, register Head Hunter as a qualified researched project term. The glossary now contains 1,121 entries; all previous 1,120 remain exact. Keep Headliner distinct, preserve the full pride-as-my-shield clauses, and add no aliases or automatic dialogue changes. Evidence and access limits are recorded in research_registration312.json.





## 0.1.163 language — 2026-11-02



- Add 151 reviewed battle lines from rows 4880–5039 after independent accuracy review of all 160 assigned rows, separate English editing, the actual terminology audit of 5,652 units with zero changes, then final proofreading of every saved line. Restore seven declarative coordination undertakings and complete 15 former terminology holds with registered Set On spelling; 22 initial records changed and 138 stay exact.

- Preserve nine canonical Bakuryū English proposals, including full Fire-the-Cutter commands, as encoding holds. No ASCII substitutions, fake encoded hashes or native approval. Meaning/delivery qualifications, genuine cries and unfinished clauses, full causal connections and original controls/line breaks/voices/blank calls remain intact.

- Clarify current terminology registration in new Mic5–11 context metadata while retaining the author’s historical 1119/pending-registration account in immutable source candidates. Correct a report-only label at 4972 to Mic12 / header377 / profile160; actual candidate English and metadata were already correct. All 4,802 earlier complete working records and alias mappings remain exact.

- Export 10,598 physical drafts covering 5,636 distinct structured entries; 2,958 distinct entries remain. Through 5039, 55 meaning gaps and 32 encoding holds stay excluded. Historical native approval remains 3,780; 6,818 current physical drafts await final tests. No builds or tests ran. Whole game remains incomplete.





## 0.1.162 language — 2026-11-02



- Add 160 reviewed battle lines from rows 4720–4879 after independent source accuracy review, separate English editing, the actual terminology audit of 5,501 units with zero changes, and final proofreading of all saved lines. Six coordination statements now retain the speaker’s own undertaking instead of becoming joint invitations; fifteen Mic calls use registered Set On spelling. Twenty-one initial records changed;139 remain exact.

- Separately source-check and correct earlier row4695’s coordination statement and the capitalization in Mic13 calls2148/2151/2152. After these four fixes, run the actual terminology audit of 5,341 units with zero changes and separately proofread all four current records. All other4,638 earlier records and all alias mappings remain exact. Historical checkpoint161 reports remain unchanged.

- Preserve full sky-falling imagery, threats, conditioned Big Brother address, Rosammy’s third-person self-reference, unfinished source clauses, performance calls, distinct Mic headers/shared voices, controls, line breaks and blank calls. Qualification of unresolved delivery, defense, endurance and gratitude/apology shades remains explicit. Glossary1,120 unchanged; researched Set On spelling does not establish activation, effects or cross-franchise equivalence.

- Export10,296 physical drafts covering5,485 distinct structured entries;3,109 distinct entries remain. Historical native approvals stay3,780. Keep55 meaning gaps and23 encoding holds through4879 excluded. No builds or tests ran;whole game remains incomplete.





## 0.1.161 language — 2026-11-02



- Add 160 reviewed battle lines from rows 4560–4719; preserve all earlier 4,482 complete working records and alias mappings. Complete independent accuracy review, separate English editing, the actual 5,341-entry name audit with zero changes, then separate final proofreading of all 160 saved lines.

- Complete Boost On, Messer Wing, Phoenix Wing and Peacock Wing calls using the four terminology entries registered after checkpoint160. Source and naming-evidence limits remain explicit; glossary now 1,119 entries, with all earlier 1,115 entries exact.

- Repair row4628’s unsupported adverse-consequence implication; retain the bare completed acknowledgment with unresolved tone. Fix row4688’s unsupported shooting-specific insult to generic skill contempt. Naturalize the damage report4575 and cooperation offer4643 after bounded source rechecks. Eight initial records changed;152 remain exact.

- Preserve full imagery, threats, sound chains, deliberate fragments, repeated calls and source-specific controls, voices and blank calls. Export 9,976 physical drafts covering 5,325 distinct structured entries;3,269 distinct entries remain. Historical native approvals stay3,780. No builds or tests ran;whole game remains incomplete.

- After checkpoint161 language auditing/proofreading under1,119 entries, register Set On as a qualified Mic-context project formula supported by positive dedicated-wiki quoted captions. Current glossary1,120;all previous1,119 entries exact. No aliases, historical MAIN changes, cross-franchise equivalence or official-game-English claim. Track three earlier Mic calls for focused source-bound terminology review.





## 0.1.160 language — 2026-11-02



- Add 160 language-reviewed battle lines from rows 4400–4559. Preserve all initial draft records and all earlier 4,322 complete working records and alias mappings.

- Complete independent accuracy review, separate English editing, the actual 5,181-entry registered-name audit with zero changes, and separate final proofreading of all 160 saved lines. Retain row 4546 as an incredulous question about a neutral defeat result, recording its mild spoken-collocation qualification and avoiding an unsupported actor.

- Preserve full support and permission directions, the salt-and-eat threat, the deliberately absurd calendar taunt, row 4559’s unfinished complement, tail commands and voice IDs. Glossary 1,115 unchanged; row 4392’s prior native integration requirement remains intact.

- Export 9,656 physical drafts covering 5,165 distinct structured entries; 3,429 distinct entries remain. Historical native approvals stay 3,780. Continue the next two battle batches and racing-term research. No builds or tests ran; whole game incomplete.





## 0.1.159 language — 2026-11-02



- Add159 language-reviewed battle lines from4240–4399;prior4,163 complete records/mappings unchanged. Independent accuracy review, separate English editing,5,021-entry name audit with zerochanges,then all159 final saved-line proofreading.

- Complete Thunder Knuckle4264;naturalize4261 plural senior address with qualified senpais loanplural after bounded source recheck. Correct4320 metadata so Konoha is protectee and listener remains unknown;English unchanged. Keep4384 malformed power-transfer direction held with both complete alternatives.

- Preserve4392 unvoiced cry/speaker711/flags17/voice0 in the language draft and record a source-bound native integration requirement for the final phase. Keep4391 extra blank calls and4354 reused voice unchanged. Glossary1115 unchanged.

- Save drafts through4559;continue4560–4639. Export9,336 physical drafts covering5,005 distinct structured entries;3,589 distinct remain. Historical native approvals stay3,780. All builds/tests/game checks deferred;whole game incomplete.





## 0.1.158 language — 2026-11-02



- Add all160 language-reviewed battle lines in rows4080–4239; prior4,003 complete records/mappings unchanged. Independent accuracy review, separate English editing,4,862-entry name audit with zerochanges, then all160 final saved-line proofreading.

- Complete eight full terminology-held frames and repair4140 to a noncausative ending declaration. Preserve full support/permission direction, girl-rejection pain comparison, judo/breakfall claims, on-cue timing, stammers and source force. Motor/Water and Crush/Crusher naming normalizations retain explicit contextual-inference limits.

- Record late Shadow Kunai/Drill Crush registrations following157 snapshot and add Thunder Knuckle after158 languagepass. Glossary1115;prior entries exact. Thunder Knuckle is transparent project English backed by a positive Japanese wiki namedfield,not official-English or Eagle Attack equivalence.

- Save drafts through4479;continue drafting. Export9,018 physical drafts covering4,846 distinct structured entries;3,748 distinct remain. Historical native approvals stay3,780. All builds/tests/game checks deferred;whole game incomplete.





## 0.1.157 language — 2026-11-02



- Add 159 language-reviewed battle lines from rows 3920–4079; prior 3,844 complete records and mappings unchanged. Independent accuracy review, separate English editing, 4,702-entry name audit with zero changes, then all159 final saved-line proofreading.

- Complete five terminology-held frames, repair two genuine nominal fragments, and source-recheck natural Touchimou challenge wording separately. Retain one unresolved continuance-versus-appraisal line4058 with both complete alternatives.

- Register four Dagwon calls/designations before the language pass and three subsequent attack names after it. Glossary1,105→1,112;prior entries exact. Explicitly document Motor/Water normalization as contextual wiki-priority project inference, not verified alias/source typo/effect.

- Save drafts through row4319; continue drafting. Export8,698 physical drafts covering4,686 distinct structured entries;3,908 distinct remain. Historical native approvals stay3,780. No builds/tests/runtime work; whole game incomplete.





## 0.1.156 language — 2026-11-02



- Add all 160 language-reviewed battle lines in rows 3760–3919; prior 3,684 complete records and mappings unchanged. Independent accuracy review, separate English editing, 4,543-entry name audit with zero changes, then complete final proofreading.

- Complete 12 full terminology-held frames and resolve 3848 with a neutral endurance-extent/showdown challenge. Retain full group introductions, qualified Arago apposition, ordinary subjects/verbs/directions, source force and pauses. No new unresolved row in this batch.

- Register four attack/group terms before the language pass and Jaga Ken/Touchimou after it for the next batch. Glossary 1,099→1,105; prior entries exact. Preserve explicit raw/wiki spelling differences, the full darkness qualifier, and qualified project group-name status.

- Save drafts through row 4159; continue drafting. Export 8,380 physical drafts covering 4,527 distinct structured entries; 4,067 distinct entries remain. Historical native approvals stay 3,780. No builds/tests/runtime work; whole game incomplete.





## 0.1.155 language — 2026-11-02



- Add 159 language-reviewed battle lines within rows 3600–3759; prior 3,525 complete records and mappings unchanged. Independent accuracy review, separate English editing, 4,383-entry name audit with zero changes, then complete final proofreading.

- Complete 17 full registered-name proposals. Clarify explicit addressees at 3643/3656/3742 and qualified apology/indebtedness at 3739. Retain 3676 wordplay hold. Preserve all four two-body Wataru/Ryujinmaru records and actual solo Ryujinmaru headers.

- Register six Troopers/nickname terms before the language pass, then Chou Ryuu Ha and Gantessai for the next batch. Glossary 1,091→1,099 with prior entries exact. Preserve explicit raw/wiki Japanese discrepancy and fixed earlier names.

- Save drafts through row 3919 and continue drafting. Export 8,060 physical drafts covering 4,367 distinct structured entries; 4,227 distinct entries remain. Historical native approvals stay 3,780. No builds/tests/runtime work; whole game incomplete.





## 0.1.154 language — 2026-11-02



- Add 159 language-reviewed battle lines within rows 3440–3599; prior 3,366 complete records and mappings unchanged. Independent accuracy review, separate English editing, 4,224-entry name audit with zero changes, and final proofreading complete.

- Complete 39 full terminology-held lines. Repair 3521 source-fragment/direction, improve 3562 spoken acceptance after source recheck, correct explicit-addressee metadata at 3525/3530/3582. Retain meaning hold 3570.

- Register 21 researched Ganba/Brain/Big O and character terms, then eight Wataru terms after the language pass. Glossary 1,062→1,091 with all prior entries exact. Preserve the explicit source Sword/wiki Fist policy departure and literal-source alternative.

- Save the next 80-row draft 3600–3679; begin drafting 3680–3759. Export 7,742 physical drafts covering 4,208 distinct structured entries; 4,386 distinct entries remain. Historical native approvals stay 3,780. No builds/tests/runtime checks; whole game incomplete.





## 0.1.153 language — 2026-11-02



- Add139 language-reviewed battle lines within3280–3439; prior3227 records/mappings unchanged. Independent227/229 accuracy, separate139-line editing,4065-unit names audit/zero changes, separate139-line final proof completed.

- Complete7 researched equipment-name lines and register4 qualified Jaku terms, glossary1058→1062 with prior prefix exact. Preserve3409 apology/gratitude ambiguity and20 further canonical Bakuryū font/encoding holds; no ASCII fallback.

- Save a further80-row pending draft3440–3519. Draft3520–3599 also saved; terminology research and independent reviews continue.

- Export7424 physical drafts covering4049 distinct structured entries;4545 distinct remain. Historical3780 native approvals unchanged. No builds/tests/game checks; whole game incomplete.





## 0.1.152 language — 2026-11-02



- Add156 reviewed battle lines within3120-3279; prior3071 full records/mappings unchanged. Retain3143 meaning hold and3272-3274 encoding holds with full canonical English preserved separately.

- Complete independent217/222 accuracy, separate156-line editing, bounded225 source recheck,3926-unit actual names audit/zero changes, separate156-line final CURRENT MAIN proof.

- Adopt52 complete registered term proposals;3164 question/shout punctuation corrected. Explicit-listener metadata3191Koji/Asuka,3240Jin/Asuka,3260Jin corrected without actual presence/reply claims.

- Register14 researched nouns under220/223, glossary1044 to1058/prior prefix exact. Three NEW equipment names use exact wiki Bakuryū; fixed Bakuryu-Oh/Dragon remain unchanged. Eleven other new nouns explicitly project English. Encoder/font support for U+016B remains pending; no fallback or encoded-byte claim.

- Export7146 physical drafts:3910 distinct translated/4684 remain.3780 historical native approvals unchanged. No builds/tests/native/display/game checks; whole game incomplete.





## 0.1.151 language — 2026-11-02



- Add160 reviewed battle lines2960-3119, retain49 earlier gaps; prior2911 full records/mappings unchanged.

- Complete independent210/212 accuracy, separate160-line editing, bounded219 source recheck,3770-unit name audit/zero changes, separate160-line final CURRENT MAIN proof.

- Repair2963/3010 question-shout punctuation,2998 repeated attention challenge and3088 conditional sufficiency. Preserve3020 voiced596/4089 plus second unvoiced header0 body; native integration and testing still pending.

- Register14 researched names under216 after language passes, glossary1030 to1044/prior prefix exact. No dialogue changed by registration. Authority/access/fallback limits recorded.

- Export6834 physical drafts:3754 distinct translated/4840 remain.3780 historical native approvals unchanged. No builds/tests/native/display/game checks; whole game incomplete.





## 0.1.150 language — 2026-11-02



- Add160 reviewed battle lines2800-2959;49 prior unresolved battle gaps retained. Prior2751 full working records/mappings and all1030 glossary entries exact.

- Complete independent206/207 accuracy, separate160-line editing, bounded source recheck213,3610-unit name audit/zero changes and separate160-line final CURRENT MAIN proof.

- Restore2876 finite evaluation; improve2891 conditional challenge and2895 question/shout punctuation after source recheck. Correct explicit invoked addressees2812Yuu/2949Roddy in metadata only, English unchanged. No actual presence/hearing/reply inferred.

- Export6514 physical drafts:3594 distinct translated,5000 distinct remain.3780 historical native approvals unchanged. No builds/tests/native/display/game checks; whole game incomplete.





## 0.1.149 language — 2026-11-02



- Add239 reviewed battle lines2560-2799;2708 remains held,49 unresolved gaps through2799. Prior2512 full working records/mappings exact.

- Complete independent198/195/202 accuracy, separate239-line editing,3450-unit name audit/zero changes and separate239-line CURRENT MAIN proof. Correct2575 excessive solo advance and2642 finite acknowledgment.

- Register5 project Formation labels, glossary1030/prior1025 exact; complete20 full calls with literal fullwidth designations, original commands and framing. No official-English or mechanics claim.

- Export6194 physical drafts:3434 distinct translated,5160 distinct remain.3780 historical native approvals unchanged. No builds/tests/native/display/game checks; whole game incomplete.





## 0.1.148 language — 2026-11-02



- Add78 reviewed battle lines2480–2559; hold2489/2491,48 unresolved battle gaps through2559. Prior2434 full records/mappings exact.

- Complete independent191 accuracy, separate78-line English editing,3211-unit names audit/zero changes and separate78-line final CURRENT MAIN proof.1025 glossary entries unchanged.

- Retain489/490 separate headers despite reused voices,2514 raw vowel anomaly,2527 unfinished nominal dismissal and2552 armor-conditional setup.

- Export5716 physical drafts:3195 distinct translated,5399 distinct remain.3780 historical native approvals unchanged. All builds/tests/native/display/game checks deferred until pipeline completion. Whole game incomplete.





## 0.1.147 language — 2026-11-02



- Add79 reviewed battle lines2400–2479; preserve prior2355 full records/mappings. Hold2459,46 unresolved battle gaps through2479.

- Adopt independently source-reviewed2414 courteous invitation repair,2430 protected-object metadata correction and2452 gender-null metadata correction. Preserve every control/LF/voice/header and full life/shield imagery.

- Complete separate79-line English editing,3133-unit names audit/zero changes and separate79-line final CURRENT MAIN proof. All1025 glossary entries unchanged.

- Export5560 physical drafts:3117 distinct translated,5477 distinct remain. Historical native approvals3780 unchanged; all builds/tests/native/display/game checks deferred until pipeline completion. Whole game incomplete.





## 0.1.146 language — 2026-11-02



- Add157 fully language-reviewed battle lines2240–2399, preserving prior2198 full working records/mappings. Hold2281/2303 and retain2316,45 unresolved battle gaps through2399.

- Register16 researched names1009→1025, reuse2 forms, document wiki/licensed title differences and explicit2242 canonical-reading departure.2296/2297 Latin readings remain provisional with conflicting weak historical alternatives.

- Complete23 full term frames, separate157-line English editing,3054-unit names audit/zero changes and separate157-line final CURRENT MAIN proof. Preserve2286two bodies/voices in one row and2304–06 separate lexical fragments.

- Keep source-bearing185 reports in local CHAT/work with exact path/hash references. English-only exports updated. Export5402 physical drafts:3038 distinct translated,5556 remain.

- All builds/tests/native admission/display/in-game checks deferred until pipeline completion;3780 historical native approvals unchanged. Whole game incomplete.





## 0.1.145 language — 2026-11-02



- Add158 reviewed battle lines2080–2239; preserve prior2040 full records/mappings. Hold2166/2187,42 unresolved battle gaps through2239.

- Register24 researched names985→1009 with explicit wiki/project/primary evidence limits; prior985 glossary entries exact. Complete59 full term proposals and source-recheck the2197 conditional.

- Finish separate158 English editorial,2897-unit names audit/zero changes and separate158 final CURRENT MAIN proofreading. Expand source-slice context metadata and correct only human Domon2159 metadata.

- Preserve2085/2111/2170 trailing controls and2122/2130 unvoiced forms; native admission/fit pending. All builds/regression/display/in-game tests deferred until translation completion.

- Export5088 physical drafts:2881 distinct translated,5713 distinct remain. Historical native approval3780 unchanged. Whole game incomplete.





## 0.1.144 language — 2026-11-02



- Add157 reviewed battle lines1920–2079 from two80-row slices; preserve prior1883 full records/mappings. Hold1970/1985/1986,40 unresolved battle gaps through2079.

- Register27 researched names958→985 with explicit wiki/project dispositions; prior958 entries exact. Complete43 framed term proposals and six independently169 source-rechecked editorial/name changes.

- Finish separate157 English editorial,2739-unit names audit/zero changes and separate157 final CURRENT MAIN proofreading. Expand shared context metadata into new MAIN rows while preserving earlier records.

- Preserve1924 trailing flag32/speaker358; native integration/fit pending. All builds/regression/display/in-game tests deferred until translation completion.

- Export4772 physical drafts:2723 distinct translated,5871 distinct remain. Historical native approval3780 unchanged. Whole game incomplete.





## 0.1.143 language — 2026-11-02



- Add79 reviewed battle entries1840–1919 in both banks; preserve1804 prior full records/mappings.1892 remains held,37 unresolved battle gaps total through1919.

- Register nine researched GaoGaiGar nouns,949→958; explicitly adopt wiki/project Double Plasma Swords plural. Keep fire/launch commands and all original source fields separate.

- Apply independent155 accuracy corrections1867/1889 and exclusion1892; independent157 checks1871 and conditional-phrasing repairs1897/1917. Separate79 editorial,2582-unit names audit/zero changes and separate79 final CURRENT MAIN proofreading complete.

- Preserve1904 trailing flag32/speaker357 with native integration pending. No builds, regression, display-fit or in-game tests; defer until complete translation per user instruction.

- Export4458 physical drafts,2566 distinct drafted,6028 distinct remaining. Historical native approval3780 unchanged. Whole game incomplete.

- Clarify160's incorrect2106 year metadata without modifying immutable candidates/reports; fresh158 date fields were correct.





## 0.1.142 language — 2026-11-02



- Add80 reviewed battle entries1760–1839 in both banks, preserving prior1724 full records/mappings and36 older ambiguity gaps.

- Complete eight exact independently151-reviewed terminology proposals in immutable new153 candidate; update its current counts explicitly.949 glossary fixed forms unchanged.

- Complete parent full80 source comparison, separate80 editorial, actual2503-unit names audit/zero changes and separate80 final CURRENT MAIN proofreading.

- Preserve original unvoiced1804 with pending native-admission metadata; no new voice or runtime/tool admission change. All builds/regression/display/game tests remain deferred until complete translation by user instruction.

- Export4300 physical ATMB drafts,2487 distinct drafted,6107 distinct remaining. Native approval stays3780. Whole game unfinished.

- Clarify inherited stale summary counts in immutable candidate149 without changing its rows; authoritative141 review/current production counts are correct.





## 0.1.141 language — 2026-11-02



- Add80 reviewed battle entries1680–1759 to both banks; preserve all prior1644 full records/mappings and36 earlier ambiguity gaps.

- Resolve two term holds through researched Broken Phantom/Protect Wall registrations949 total; retain all prior947 entries. Apply source-rechecked Teamwork wording and comma-splice repair.

- Complete independent147 full80 accuracy plus bounded150 four-adoption review, separate final80 editorial, actual2423-unit names audit/zero changes and separate80 final CURRENT MAIN proof.

- Export4140 physical ATMB drafts,2407 distinct structured sources drafted,6187 distinct remaining. Native approval remains3780; all new tests/builds/fit/game checks deferred until complete translation, by user instruction.

- Continue pending148/152/154 slices. No new runtime/font patch, test suite execution, native fit or build claimed. Entire game unfinished.





## 0.1.140 language — 2026-11-02



- Follow explicit user instruction: finish translation pipeline first, then run builds/regression/display/in-game testing together after translation completion.

- Add76 language-reviewed battle entries1600–1679 to both banks; retain four new stance holds and all prior1568 complete records/mappings. No runtime or font changes.

- Register ten GaoGaiGar terms947 total, documenting explicit Gemu and Plasma Hold named-form policy departures while preserving original source bytes.

- Complete independent full80 accuracy145, separate76 editorial, actual2343-unit names audit/zero changes and separate76 final CURRENT MAIN proofreading. Preserve all candidate/review histories.

- Export3980 physical ATMB drafts;6267 distinct structured sources remain. Native approval stays3780. No new build, regression suite, capture, native-fit approval or full-disc check for this language checkpoint.

- Continue pending146 and148 language slices. Whole-game translation remains active and incomplete.





## 0.1.137–0.1.139 — 2026-11-02



- Add 79 reviewed battle entries 1520–1599 except 1538 to both banks; preserve 32 gaps and all prior 1,489 FULL English records per bank.

- Register one-word Supercharge using official Japanese direct wording and official English product-search description; disclose direct English 503. Preserve all prior 936 glossary entries. Recheck two bounded 139 revisions and complete 1557 through independent full 141 accuracy, separate editorial, actual names and separate final CURRENT MAIN proof.

- Pass 89 tests/8,298 parser calls; update only existing corpus regression expectations. No new font, voice or preview patch.

- Review 158 physical displays, both ordinary cleanups and fresh normal 139 startup. All three full-disc checks pass; normal executable byte-exact 136.

- Coverage 3,828 drafts/3,780 native fits; 6,343 distinct structured sources remain. Whole game unfinished; future 1600–1679 has zero production approval.



## 0.1.134–0.1.136 — 2026-11-01



- Add 78 reviewed battle entries 1440–1519 except 1450/1457 to both banks; preserve 31 gaps and all prior 1,411 complete records per bank.

- Register distinct V-MAX/V-MAXIMUM labels from primary spelling evidence; preserve all previous 934 glossary entries. Recheck four wording revisions and two activation completions through full independent 137 accuracy, separate English editing, actual names and separate final CURRENT MAIN proof.

- Pass 89 tests/7,880 parser calls; update only existing corpus regression expectations. No new font, voice or preview patch.

- Review 156 physical displays, both ordinary cleanups and fresh normal 136 startup. All three full-disc checks pass; normal executable byte-exact 133.

- Retain initial 134 opening-navigation timeout, inspected CG and subsequent successful caption observation in the same process, without reset or state load.

- Coverage 3,670 drafts/3,622 native fits; 6,422 distinct structured sources remain. Whole game unfinished; future 1520–1599 has zero production approval.



## 0.1.131–0.1.133 — 2026-11-01



- Add 79 reviewed entries 1360–1439 except 1395 to both banks; preserve 29 gaps.

- Resolve 1369/1409/1417 through bounded 134 and final source checks. Retain qualified 1391 punctuation emendation; intended original punctuation remains unproved.

- Add exact-source unvoiced 1439 offline admission with independent staging/speaker guards and two original/English native-parser regression tests. Preserve older unvoiced guards; no added cue/runtime patch.

- Complete separate 79 editorial, actual terminology audit and separate 79 CURRENT MAIN proof; all 89 tests/7,470 parser calls pass.

- Review 158 physical bodies, both ordinary cleanups and fresh normal 133 startup. Full-disc checks pass; normal executable changes only one cached pack 22 size byte versus 130.

- Retain the failed initial 132 PINE check and subsequent successful navigation in the same process; no restart or state load.

- Coverage 3,514 drafts/3,466 native fits; whole game unfinished. Future 1440–1519 remains pending with zero production approval; glossary 934 frozen.



## 0.1.128–0.1.130 — 2026-11-01



- Add 77 reviewed battle entries 1280–1359 except 1305/1310/1352; preserve 28 gaps.

- Recheck 1352 idiom stance with full source context and bounded 132; exclude unresolved seriousness/protest rather than invent a refusal or commitment.

- Complete current full 80 comparison, separate 77 English editing, actual terminology audit and separate full 77 final proof.

- Pass 87 tests/7,042 parser calls, 154 physical displays, two ordinary cleanups and fresh normal startup.

- Full-disc checks pass; normal 130 entire executable byte-exact 127 and six pack sizes unchanged.

- Coverage 3,356 drafts/3,308 native fits; whole game unfinished. Future 1439 needs source-specific unvoiced tooling/tests before insertion.



## 0.1.125–0.1.127 — 2026-11-01



- Add 77 reviewed battle entries 1200–1279 except 1219/1230/1269; preserve 25 gaps.

- Repair 1251 as qualified genuine nominal Support prep!; retain agent/report/order uncertainty.

- Complete independent 129 accuracy, separate English editing, actual glossary audit and full final proof.

- Pass 87 tests/6,634 parser calls, 154 physical displays, two ordinary cleanups and fresh normal startup.

- Full-disc checks pass. Alias 4971 grows 2,048 bytes; only its cached-size byte changes in normal 127 versus 124, all other executable bytes exact.

- Future 1280 preparation excludes 1310 and corrects 1329 explicit-Jojo listener metadata; no production approval from that work.

- Coverage 3,202 drafts/3,154 native fits; whole game unfinished. Preserve old evidence and K routing.



## 0.1.122–0.1.124 — 2026-11-01



- Add 77 reviewed battle entries 1120–1199 except 1132/1163/1195; retain 22 gaps.

- Repair 1125/1147, explicitly qualify 1145/1150, and exclude 1195's unsupported completed judgment.

- Complete independent accuracy, separate English editing, actual names audit and full final proof.

- Pass 87 tests/6,234 parser calls, 154 physical displays, two ordinary cleanups and fresh normal startup.

- Full-disc checks pass; normal 124 executable is entirely exact 121. No game runtime patch.

- Add optional capture spillover, four routing tests and actual logical/physical state/PNG verification. New images and captures use K; old evidence preserved.

- Coverage 3,048 drafts/3,000 native fits; whole game unfinished. See validation 124.



## 0.1.119–0.1.121 — 2026-11-01



- Add 76 reviewed battle entries 1040–1119 except 1043/1060/1089/1102; retain 19 gaps.

- Compare all 80 source/English records and seven full profiles; separate 76 English editorial, actual names audit and final proofreading.

- Pass 83 tests/5,820 parser calls, 152 physical displays, two ordinary cleanups and fresh normal startup.

- Full-disc checks pass; normal 121 executable is exact 118. No runtime patch.

- Preserve three incomplete ENOSPC builds, rebuild on K and keep original project paths through junctions. Older evidence untouched.

- Coverage 2,894 drafts/2,846 native fits; whole game unfinished. See validation 121.







## 0.1.116-0.1.118 - 2026-11-01



- Add 78 reviewed battle entries 960-1039 except 992/1005; preserve 15 gaps.

- Re-compare all 80 source/current-English records and six full profiles; separate 78 English editorial, actual names audit and final proof.

- Pass 83 tests/5,414 source-English parser calls; preserve previous rows and members.

- Validate 156 physical displays, two ordinary cleanups and fresh normal startup.

- Full-disc checks pass; only cached pack 22 byte-size word differs from 115.

- Coverage 2,742 drafts/2,694 native fits. Whole game unfinished; see validation 118.







## 0.1.113-0.1.115 - 2026-11-01



- Add 77 reviewed battle entries 881-959, preserving 13 unresolved/provisional gaps.

- Source-recheck 915 attack collocation, then separate full editorial/names/proof.

- Pass 83 tests and 4,998 source-English parser calls; preserve prior rows and members.

- Validate 154 full physical displays, two ordinary cleanups and fresh normal startup.

- Full-disc checks pass; normal 115 ELF is byte-for-byte identical to 112.

- Coverage 2,586 drafts / 2,538 native fits. Whole game unfinished; see validation115.







## 0.1.110-0.1.112 - 2026-11-01



- Add 78 reviewed battle entries 800-879, preserving ten unresolved gaps.

- Complete accuracy, separate English editorial, source rechecks, names and full proof.

- Pass 83 tests / 4,610 source-English parser calls, prior/gap/member preservation.

- Validate 156 full physical bodies, two ordinary cleanups and fresh normal 112 startup.

- Full-disc checks pass; only normal ELF change vs109 is cached pack4971 size.

- Coverage 2,432 drafts / 2,384 native fits. Whole game unfinished; see validation112.







## 0.1.107-0.1.109 - 2026-11-01



- Add78 reviewed battle entries720-799; retain eight unresolved gaps.

- Complete accuracy, separate English editorial, source rechecks, names and full proof.

- Admit only exact original unvoiced720 staging; add two mutation/parser tests.

- Pass83 tests/4,196 source-English calls, preserving prior/gap bytes.

- Validate156 physical bodies, two ordinary cleanups and fresh normal109 startup.

- Full-disc checks pass; normal109 ELF exact106. Whole game unfinished.

- Coverage2,276 drafts/2,228 native fits. See validation-v0.1.109.md.







## 0.1.104-0.1.106 - 2026-11-01



- Add 78 reviewed battle entries 640-719, preserving six unresolved gaps.

- Complete separate accuracy, English editorial, substantive source rechecks,

  glossary 934 name audit and final proof before own physical display checks.

- Pass 81 tests / 3,776 source-English native parser calls; preserve prior/gap bytes.

- Validate 156 physical bodies, two ordinary cleanups and fresh normal 106 startup.

- Byte-check all three discs. Only normal ELF delta against 103: cached pack 22 size.

- Whole game unfinished: 2,120 drafts / 2,072 native fits. See validation-v0.1.106.md.







## 0.1.101-0.1.103 - 2026-11-01



- Add79 complete reviewed battle rows560-639, preserving four unresolved gaps.

- Register researched Beam Coat spelling in glossary934; no cross-game mechanics.

- Admit only exact unvoiced616/speaker88 source; retain original cue absence and

  legacy195-204 behavior. Add two native-parser and rejection regressions.

- Pass81 tests/3,370 original-parser comparisons; preserve prior/gap bytes.

- Check158 physical native displays, two ordinary cleanups and fresh normal103

  startup. Normal ELF exact 100; all three discs byte-verified.

- Whole game unfinished:1,964 drafts / 1,916 native fits. See validation-v0.1.103.md.







## 0.1.98-0.1.100 - 2026-11-01



- Insert78 complete reviewed battle rows480-559; preserve349/503/525 unresolved.

- Register Binder in glossary933, separate from Round Binder; no mechanics claim.

- Add bounded explicit reviewed-ID native previews, metadata/inspection/verification

  and four MIPS/build regressions; preserve exact legacy range payloads.

- Pass79 tests/2,948 original-parser comparisons; preserve earlier/gap bytes.

- Check156 own-physical complete native displays, two ordinary cleanups and fresh

  normal100 startup; normal ELF exact96. All three full discs byte-verified.

- Whole game unfinished;1,806 drafts/1,758 native fits. See validation-v0.1.100.md.





All builds below are local test artifacts. No release was created or published.

No Git repository existed at inspection; the change record is this file, source tools,

English exports and versioned build manifests under work/output/.



## v0.1.93–96 - 2026-11-01 - sixth battle slice



- Independently review and insert 80 complete lines 400–479; preserve unresolved 349.

- Recheck four substantive/editorial revisions, run glossary932 name audit and full

  final proof. Preserve unresolved coordination participants; no fit shortening.

- Bound extra-position code investigation without claiming unused/reachable status.

- Pass all 75 tests, 2,544 native parser calls; preserve earlier insertion bytes.

- Validate 160 own-resource native displays in 94/95 and both ordinary cleanup screens.

- Verify all three discs; fresh normal96 startup. Runtime code unchanged; cached

  pack4971 size follows the expanded data. 1,650 drafts / 1,602 fits; game unfinished.



## v0.1.87–92 - 2026-11-01 - fifth battle slice with explicit unresolved gap



- Register researched Aura Barrier (932 glossary terms) and complete 360/375.

- Independently review 79 of 80 assigned records 320–399. Preserve 349 original:

  apology versus indebted gratitude is unresolved despite bounded code checks.

- Apply source/English accuracy, separate editorial, actual name audit and final

  proof. Recheck substantive 382/384; no fit shortening or runtime-code change.

- All 75 tests pass: 2,128 source/English original-parser calls, 399 battle records,

  prior 320 exact against 86; 349/400-onward untouched and split-range review guards.

- Fresh 88–91 own-resource previews prove 158 complete physical displays across

  two reviewed subranges and four bounded native returns. All five discs verify.

- Normal 92 freshly boots to first caption; its executable is byte-identical to 86.

  Current 1,490 physical drafts / 1,442 fits; 13,664 stored / 7,512 distinct raw remain.

  Next 400–479 is author-pending only; ordinary triggers/full game remain unfinished.



## v0.1.83–86 - 2026-11-01 - fourth reviewed battle slice



- Research/register Aura Slash (glossary 930 -> 931), scan the entire extracted

  source/English corpus, and complete the missing attack declaration at 243.

- Independently review, edit-check, audit names and proof all 80 records 240–319;

  insert exact aliases while retaining qualified fragments/referents/312 tense.

- All 74 tests pass: 1,704 original-parser source/English calls across 320 records,

  exact prior 240 insertions and untouched later sources, both resource banks/ABIs.

- Fresh muted 84/85 runs prove all 160 new full displays, physical origins,

  original speaker/voice staging, prompt geometry and bounded return. All three

  rebuilt discs verify. No native font/runtime code change or fit shortening.

- Normal 86 fresh startup passes to held first opening caption; sole executable

  difference from 82 is cached pack 22 size data. Whole-game progression remains

  unverified. Current 1,332 ATMB drafts / 1,284 fits; 13,822 stored / 7,591 distinct

  raw texts remain, plus compiled/media work. Future 320–399 remains pending.



## v0.1.80–82 - 2026-11-01 - third reviewed battle slice



- Independently review and insert80 records160–239 plus exact-source aliases.

  Full source accuracy, separate English editorial, glossary audit and final proof

  retain the complete wording;183's open continuation and contextual hit readings

  remain qualified. Glossary930 unchanged.

- Admit only ten pinned unvoiced sources195–204, preserving speaker24 and absent

  voice cues. Existing voiced behavior remains exact. Build reports distinguish

  staging profiles; native runtime code is unchanged for the unvoiced profile.

- All74 tests pass, including1292 source/English original-parser calls across240

  battle records, source-drift/cue guards, both native preview destinations and ABI.

- Local debug80/81 preview160–239; normal82 has the same executable bytes as79.

  Separate80/81 evidence approves160 full bodies, both physical origins, original

  unvoiced headers, prompt fit and native return. Full disc checks pass all3.

  Normal82 is not boot-tested;1172 ATMB/1124 fits,13982stored/7671distinct remain.



## v0.1.77–79 - 2026-11-01 - second reviewed battle slice



- Independently review and insert80-159 with exact aliases;109 grateful acknowledgment,113 complete actor-neutral endurance question,142 idiom and151 clipped rebuke rechecked before full editorial/proof passes. Glossary930 unchanged; no fit shortening.

- Extend guarded fresh preview to1-80 reviewed source rows, absolute IDs/relative progress. Default payload exact74. All72 tests pass, including852 original/English parser calls; old0-79 and untranslated160 onward preserved.

- Visually read160 new native bodies and two cleanup screens in separate77/78 runs; prove both physical resource origins, fit and bounded return. Normal combat triggers/audio timing remain unverified.

- Normal79 has six packs exact78 and only the cached4971 size byte differs from normal76; no code/font change, no preview hook. Full20-file/5614-pack verification passes77/78/79. Normal79 not boot-tested.

- Main1012 ATMB+7 ELF,964 ATMB native fits; remaining14142 stored/7751 distinct raw entries. Next80 author candidates stay pending;10 unvoiced records require their own profile. Whole game unfinished.



## v0.1.74–76 - 2026-11-01 - reviewed battle bank and physical aliases



- Independently review and insert first80 battle records at two exact-source physical destinations. Full meaning, original native calls, voices and controls preserved; glossary930 unchanged. Add source-hashed alias exports with separate fit evidence/expiry.

- Add read-only resource-registry provenance, battle-specific layout guards and bounded fresh-build native preview. All70 tests pass;20-file/5,614-pack checks pass for74/75/76.

- Visually review all160 new native bodies plus two cleanup screens. Confirm both physical resources and return after80 calls. Original combat triggers, audio timing and maximum-name behavior remain unverified.

- Normal76 has no forced hook: executable exact standard72, six packs exact debug75. It is not boot-tested. Coverage852 ATMB+7 ELF,804 ATMB native-fit approvals. Remaining14,302 stored/7,831 distinct sources.

- Next80 author slice stays pending:79 candidates and unresolved/null113; not inserted or counted. Whole game, ordinary library route, later story, menus and most compiled/graphics/media text remain unfinished.



## v0.1.73 - 2026-11-01 - missing tutorial native preview



- Guarded fresh-build exact-request redirects expose tutorial 1/33 once each;

  original event conditions remain unverified. Standard 72 bytes remain unchanged.

- All 58 regressions and 20-file / 5,614-pack verification pass. Read all 34 debug

  captures and 15 additional standard 72 story pages. Approve ten complete entries

  / 21 bodies with native cues, proportional cursor, prompt and code checks.

- All 42 tutorial rows / 140 bodies now have versioned native evidence; story 0–13

  is observed. 644 total ATMB fit approvals. No new main wording/glossary changes.

- 80-row battle author draft remains pending review/insertion/fit and uncounted.

  Remaining 14,462 stored / 7,911 distinct structured sources; whole game unfinished.



## v0.1.72 - 2026-11-01 - native continuation margins



- Derive native26px triangle geometry; reserve final-line 478px. Reflow10calls in9rows.

  Independently recheck the single tutorial 22:2 wording change, then final proof.

- Add guarded read-only prompt coordinates and voice-gated prompt capture readiness.

  All 53 regressions and20-file / 5,614-pack verification pass; all 614 native call

  metadata/voices remain exact. Glossary 930/699 units unchanged; name audit 0 changes.

- Fresh standard route: 28 opening pages + 134 tutorial bodies, with same-build-state

  prompt recapture for0:21. Seven changed calls pass native margin checks; later

  story 21:6/37:1/43:14 and tutorial1/33 remain pending. Earlier evidence preserved.

- Independently prepare all 42 near-variant source rows (234calls/140 bodies), with

  source-typo/EN uncertainties explicit; no new translation or alias approval.

- Remaining 14,462 stored/ 7,911distinct structured sources; whole game unfinished.



## v0.1.71 - 2026-11-01 - first-battle tutorial



- Add all 42 tutorial rows / 140 voiced bodies and 23 glossary terms (930 total).

  Independent accuracy correction 34 precedes editorial changes 9/16/28; substantive

  rechecks and final proofreading are recorded. Total: 692 ATMB + 7 ELF units.

- Add exact-source-gated color 6 battle layout; preserve 246 calls and every cue.

  All 140 bodies fit 504px/three lines without font reduction or source-byte limit.

- Fresh muted standard flow: 28 opening pages recaptured; 40 complete English

  tutorial rows / 134 body pages visually approved. Pending tutorial rows: 1 and 33.

  Original source 134/140 and static references to 1/33 remain separately documented.

- Fix repeated-bark capture collision using native window identity; allow explicit

  guarded logical-bark/story fallbacks. All 49 regressions and 20-file / 5,614-pack

  checks pass. Earlier font/menu, story and encyclopedia packs are unchanged.

- Remaining 14,462 stored / 7,911 distinct raw ATMB sources; compiled/UI/graphics,

  movies, spoken-only text, ordinary library and later routes remain unfinished.

- Native continuation-arrow margins need correction on six near-full final lines;

  body approval records complete text visibility, not full prompt placement.



## v0.1.70 - 2026-11-01 - first opening-story table



- Add 49 complete story rows and five scoped glossary terms (907 entries).

  Independent accuracy, separate editorial, substantive recheck and final proof

  are recorded. Total: 650 reviewed ATMB rows plus seven compiled UI literals.

- Add original GetMessagePage model/native-code comparisons, a three-line story

  wrapper and guarded snapshot/page-walk/name-test tools. Preserve all 368 calls,

  215 text bodies, 202 voices, two functions and original per-cue boundaries.

  Rebuild ATMB/pack offsets and cached resource sizes without a row byte budget.

- All 28 opening pages, rows 0-5, pass full-size native English review with eight

  full-width W glyphs. Restore the original runtime name and enter the original

  battle tutorial. The other eight runtime values and immutable code stay intact.

  A 100-second boot-helper timeout during the original prologue was inspected;

  the same running game continued successfully with a 180-second bound.

- All 46 regressions pass; all 20 disc files / 5,614 packs verify. Font/menu and

  encyclopedia packs match v0.1.69; 588 earlier approvals keep their exact builds.

- Remaining: 14,504 stored / 7,953 distinct raw ATMB rows; 43 new story rows and

  13 help drafts lack native fit. Compiled speaker labels, later story/battle,

  ordinary library, graphics, movies and spoken-only text remain unfinished.



## v0.1.69 - 2026-11-01 - standard game-flow build



- Restore original entry hooks; 601 ATMB drafts plus seven compiled literals.

  Pager/metrics/translated packs match v0.1.68. All 20 disc files / 5,614 packs verify;

  fresh muted startup fits. Native approvals keep their exact earlier build IDs.



## v0.1.68 - 2026-11-01 - encyclopedia batch 26



- Add 5 profiles (pilot 303-307) and 8 glossary entries (902 total).

  Independent accuracy and separate parent editorial/proofreading recorded.

- New 5 entries pass 5 native pages with widest name and intact runtime values.

  Every word/control survives; parent reads every page. English pilot 0, Square,

  name restoration and native exit pass. 583 earlier approvals stay version-bound;

  current old rows, pager/buffers, metrics and font/menu pack match v0.1.66.

- All 36 tests and all-disc checks pass. Remaining 14,553 stored /

  8,000 distinct raw ATMB sources, including 0 encyclopedia entries.

- All 583 earlier encyclopedia records retain exact version-bound text approvals. This native run covers only pilot 303-307; pager, font metrics and font/menu pack match v0.1.66. Since all 588 encyclopedia entries are translated, this run checks English pilot 0 with restored Kanji player-name substitution, Square hide/show and native name-entry return. It does not claim a fresh untranslated Japanese encyclopedia capture; the last such check remains v0.1.66. Earlier illustration/availability and biography-reference limits persist; ordinary library access remains unverified.



## v0.1.67 - 2026-11-01 - standard game-flow build



- Restore original entry hooks; 596 ATMB drafts plus seven compiled literals.

  Pager/metrics/translated packs match v0.1.66. All 20 disc files / 5,614 packs verify;

  fresh muted startup fits. Native approvals keep their exact earlier build IDs.



## v0.1.66 - 2026-11-01 - encyclopedia batch 25



- Add 25 profiles (pilot 278-302) and 16 glossary entries (894 total).

  Independent accuracy, parent editorial/proofreading and substantive rechecks recorded.

- New 25 entries pass 27 native pages with widest name and intact runtime values.

  Every word/control survives; parent reads every page. Japanese pilot 303, Square,

  name restoration and native exit pass. 558 earlier approvals stay version-bound;

  current old rows, pager/buffers, metrics and font/menu pack match v0.1.64.

- All 36 tests and all-disc checks pass. Remaining 14,558 stored /

  8,005 distinct raw ATMB sources, including 5 encyclopedia entries.

- All 558 earlier encyclopedia records retain exact version-bound text approvals. This native run covers only pilot 278-302; pager, font metrics and font/menu pack match v0.1.64. Earlier illustration/availability and biography-reference limits persist. Ordinary library access remains unverified.



## v0.1.65 - 2026-10-31 - standard game-flow build



- Restore original entry hooks; 571 ATMB drafts plus seven compiled literals.

  Pager/metrics/translated packs match v0.1.64. All 20 disc files / 5,614 packs verify;

  fresh muted startup fits. Native approvals keep their exact earlier build IDs.



## v0.1.64 - 2026-10-31 - encyclopedia batch 24



- Add 25 profiles (pilot 253-277) and 23 glossary entries (878 total).

  Independent accuracy, parent editorial/proofreading and substantive rechecks recorded.

- New 25 entries pass 28 native pages with widest name and intact runtime values.

  Every word/control survives; parent reads every page. Japanese pilot 278, Square,

  name restoration and native exit pass. 533 earlier approvals stay version-bound;

  current old rows, pager/buffers, metrics and font/menu pack match v0.1.62.

- All 36 tests and all-disc checks pass. Remaining 14,583 stored /

  8,028 distinct raw ATMB sources, including 30 encyclopedia entries.

- All 533 earlier encyclopedia records retain exact version-bound text approvals. This native run covers only pilot 253-277; pager, font metrics and font/menu pack match v0.1.62. Earlier illustration/availability and biography-reference limits persist. Ordinary library access remains unverified.



## v0.1.63 - 2026-10-31 - standard game-flow build



- Restore original entry hooks; 546 ATMB drafts plus seven compiled literals.

  Pager/metrics/translated packs match v0.1.62. All 20 disc files / 5,614 packs verify;

  fresh muted startup fits. Native approvals keep their exact earlier build IDs.



## v0.1.62 - 2026-10-31 - encyclopedia batch 23



- Add 25 profiles (pilot 228-252) and 26 glossary entries (855 total).

  Independent accuracy, parent editorial/proofreading and substantive rechecks recorded.

- New 25 entries pass 25 native pages with widest name and intact runtime values.

  Every word/control survives; parent reads every page. Japanese pilot 253, Square,

  name restoration and native exit pass. 508 earlier approvals stay version-bound;

  current old rows, pager/buffers, metrics and font/menu pack match v0.1.60.

- All 36 tests and all-disc checks pass. Remaining 14,608 stored /

  8,053 distinct raw ATMB sources, including 55 encyclopedia entries.

- All 508 earlier encyclopedia records retain exact version-bound text approvals. This native run covers only pilot 228-252; pager, font metrics and font/menu pack match v0.1.60. Earlier Hana134 representative-art scope, Fire En249 and TS-AI121 illustration expectations, and Char's Super Gundam272 ordinary availability remain unresolved under earlier evidence. Ordinary library access remains unverified.



## v0.1.61 - 2026-10-31 - standard game-flow build



- Restore original entry hooks; 521 ATMB drafts plus seven compiled literals.

  Pager/metrics/translated packs match v0.1.60. All 20 disc files / 5,614 packs verify;

  fresh muted startup fits. Native approvals keep their exact earlier build IDs.



## v0.1.60 - 2026-10-31 - encyclopedia batch 22



- Add 25 profiles (pilot 203-227) and 32 glossary entries (829 total).

  Independent accuracy, parent editorial/proofreading and substantive rechecks recorded.

- New 25 entries pass 26 native pages with widest name and intact runtime values.

  Every word/control survives; parent reads every page. Japanese pilot 228, Square,

  name restoration and native exit pass. 483 earlier approvals stay version-bound;

  current old rows, pager/buffers, metrics and font/menu pack match v0.1.58.

- All 36 tests and all-disc checks pass. Remaining 14,633 stored /

  8,078 distinct raw ATMB sources, including 80 encyclopedia entries.

- All 483 earlier encyclopedia records retain exact version-bound text approvals. This native run covers only pilot 203-227; pager, font metrics and font/menu pack match v0.1.58. Earlier Hana 134 representative-art scope, Fire En 249 and TS-AI 121 illustration expectations, and Char's Super Gundam 272 ordinary availability remain unresolved under their earlier evidence. Ordinary library access is still unverified.



## v0.1.59 - 2026-10-31 - standard game-flow build



- Restore original entry hooks; 496 ATMB drafts plus seven compiled literals.

  Pager/metrics/translated packs match v0.1.58. All 20 disc files / 5,614 packs verify;

  fresh muted startup fits. Native approvals keep their exact earlier build IDs.



## v0.1.58 - 2026-10-31 - encyclopedia batch 21



- Add 25 profiles (pilot 178-202) and 28 glossary entries (797 total).

  Independent accuracy, parent editorial/proofreading and substantive rechecks recorded.

- New 25 entries pass 27 native pages with widest name and intact runtime values.

  Every word/control survives; parent reads every page. Japanese pilot 203, Square,

  name restoration and native exit pass. 458 earlier approvals stay version-bound;

  current old rows, pager/buffers, metrics and font/menu pack match v0.1.56.

- All 36 tests and all-disc checks pass. Remaining 14,658 stored /

  8,103 distinct raw ATMB sources, including 105 encyclopedia entries.

- All 458 earlier encyclopedia records retain exact version-bound text approvals. This native run covers only pilot 178-202; pager, font metrics and font/menu pack match v0.1.56. Earlier Hana134 representative-art scope, Fire En249 and TS-AI121 illustration expectations, and Char's Super Gundam272 ordinary availability remain unresolved under their earlier evidence. Ordinary library access is still unverified.



## v0.1.57 - 2026-10-31 - standard game-flow build



- Restore original entry hooks; 471 ATMB drafts plus seven compiled literals.

  Pager/metrics/translated packs match v0.1.56. All 20 disc files / 5,614 packs verify;

  fresh muted startup fits. Native approvals keep their exact earlier build IDs.



## v0.1.56 - 2026-10-31 - encyclopedia batch 20



- Add 25 profiles (pilot 153-177) and 23 glossary entries (769 total).

  Independent accuracy, parent editorial/proofreading and substantive rechecks recorded.

- New 25 entries pass 25 native pages with widest name and intact runtime values.

  Every word/control survives; parent reads every page. Japanese pilot 178, Square,

  name restoration and native exit pass. 433 earlier approvals stay version-bound;

  current old rows, pager/buffers, metrics and font/menu pack match v0.1.54.

- All 36 tests and all-disc checks pass. Remaining 14,683 stored /

  8,128 distinct raw ATMB sources, including 130 encyclopedia entries.

- All 433 earlier encyclopedia records retain exact version-bound text approvals. The new native run covers pilot 153-177 only; the pager, font metrics and font/menu pack match v0.1.54. The explicit earlier-Hana artwork mapping remains confined to the debug preview; this batch does not recheck pilot134 artwork or ordinary availability. Fire En249, TS-AI121 illustration expectations and Char's Super Gundam272 ordinary availability remain unresolved under their earlier evidence. Ordinary library access is still unverified.



## v0.1.55 - 2026-10-31 - standard game-flow build



- Restore original entry hooks; 446 ATMB drafts plus seven compiled literals.

  Pager/metrics/translated packs match v0.1.54. All 20 disc files / 5,614 packs verify;

  fresh muted startup fits. Native approvals keep their exact earlier build IDs.



## v0.1.54 - 2026-10-31 - encyclopedia batch 19



- Add 25 profiles (pilot 128-152) and 12 glossary entries (746 total).

  Independent accuracy, parent editorial/proofreading and substantive rechecks recorded.

- New 25 entries pass 26 native pages with widest name and intact runtime values.

  Every word/control survives; parent reads every page. Japanese pilot 153, Square,

  name restoration and native exit pass. 408 earlier approvals stay version-bound;

  current old rows, pager/buffers, metrics and font/menu pack match v0.1.50.

- All 36 tests and all-disc checks pass. Remaining 14,708 stored /

  8,152 distinct raw ATMB sources, including 155 encyclopedia entries.

- All 280 machine encyclopedia records and pilot 0-127 retain their exact earlier text approvals; the new native checks apply only to pilot 128-152. TS-AI pilot 121 has no visible character illustration in its earlier preview; expected presence and ordinary source drawing path remain unverified. Fire En machine 249 still has an unverified flame-only illustration from v0.1.34. Ordinary library access remains unverified. Original pilot 148 percent prose was separately validated in v0.1.25; current English passes fresh v0.1.54 evidence. Pilot 134 is absent from the original 307-record pilot illustration list; this debug build explicitly uses earlier Hana 125 artwork while retaining complete text 134. Later artwork and ordinary availability remain unverified. The driver validates descriptor coverage and rejects unexpected gaps; two new regression tests cover the guarded mapping and native arguments. Preliminary v0.1.52/53 are superseded after the incomplete v0.1.52 audit; see docs/preview_unlisted_profiles.md.



## v0.1.51 - 2026-10-31 - standard game-flow build



- Restore original entry hooks; 421 ATMB drafts plus seven compiled literals.

  Pager/metrics/translated packs match v0.1.50. All 20 disc files / 5,614 packs verify;

  fresh muted startup fits. Native approvals keep their exact earlier build IDs.



## v0.1.50 - 2026-10-31 - encyclopedia batch 18



- Add 25 profiles (pilot 103-127) and 31 glossary entries (734 total).

  Independent accuracy, parent editorial/proofreading and substantive rechecks recorded.

- New 25 entries pass 28 native pages with widest name and intact runtime values.

  Every word/control survives; parent reads every page. Japanese pilot 128, Square,

  name restoration and native exit pass. 383 earlier approvals stay version-bound;

  current old rows, pager/buffers, metrics and font/menu pack match v0.1.48.

- All 34 tests and all-disc checks pass. Remaining 14,733 stored /

  8,176 distinct raw ATMB sources, including 180 encyclopedia entries.

- All 280 machine encyclopedia records and pilot0-102 retain their exact earlier text approvals; the new native checks apply only to pilot103-127. TS-AI pilot121 shows no character illustration in this preview; complete text/footer pass, while original illustration presence or ordinary source drawing path is unverified. Fire En machine249 still has an unverified flame-only illustration from v0.1.34. Ordinary library access remains unverified.



## v0.1.49 - 2026-10-31 - standard game-flow build



- Restore original entry hooks; 396 ATMB drafts plus seven compiled literals.

  Pager/metrics/translated packs match v0.1.48. All 20 disc files / 5,614 packs verify;

  fresh muted startup fits. Native approvals keep their exact earlier build IDs.



## v0.1.48 - 2026-10-31 - encyclopedia batch 17



- Add 25 profiles (pilot 78-102) and 34 glossary entries (703 total).

  Independent accuracy, parent editorial/proofreading and substantive rechecks recorded.

- New 25 entries pass 29 native pages with widest name and intact runtime values.

  Every word/control survives; parent reads every page. Japanese pilot 103, Square,

  name restoration and native exit pass. 358 earlier approvals stay version-bound;

  current old rows, pager/buffers, metrics and font/menu pack match v0.1.44.

- All 34 tests and all-disc checks pass. Remaining 14,758 stored /

  8,201 distinct raw ATMB sources, including 205 encyclopedia entries.

- All 280 machine encyclopedia records and pilot0-77 retain their exact earlier text approvals; the new native checks apply only to pilot78-102. Fire En machine249 still has an unverified flame-only illustration from v0.1.34. Ordinary library access remains unverified. Preliminary46/47 were superseded before native audit after the official Shulove correction; all new approvals require final48.



## v0.1.45 - 2026-10-31 - standard game-flow build



- Restore original entry hooks; 371 ATMB drafts plus seven compiled literals.

  Pager/metrics/translated packs match v0.1.44. All 20 disc files / 5,614 packs verify;

  fresh muted startup fits. Native approvals keep their exact earlier build IDs.



## v0.1.44 - 2026-10-31 - encyclopedia batch 16



- Add 25 profiles (pilot 53-77) and 34 glossary entries (669 total).

  Independent accuracy, parent editorial/proofreading and substantive rechecks recorded.

- New 25 entries pass 28 native pages with widest name and intact runtime values.

  Every word/control survives; parent reads every page. Japanese pilot 78, Square,

  name restoration and native exit pass. 333 earlier approvals stay version-bound;

  current old rows, pager/buffers, metrics and font/menu pack match v0.1.40.

- All 34 tests and all-disc checks pass. Remaining 14,783 stored /

  8,226 distinct raw ATMB sources, including 230 encyclopedia entries.

- All 280 machine encyclopedia records and pilot 0-52 retain their exact earlier text approvals; the new native checks apply only to pilot 53-77. Preliminary42/43 were superseded after the row 57 meaning correction; all25 entries have fresh v0.1.44 captures. Initial navigation hit an input-clock timeout during startup; the same project VM was verified running and then reached the preview without restart or state reload. See runtime_start_v0.1.42.json. Fire En (machine 249) still has an unverified flame-only illustration from v0.1.34. See fire_en_capture_v0.1.34.json. Ordinary library access remains unverified.



## v0.1.43 - 2026-10-31 - superseded preliminary standard build



- Standard-flow counterpart of v0.1.42; all20 disc files and 5,614 RESOURCE

  packs verified. Not used for final startup/display approval.

- Superseded after parent native proof found row 57's potentially reversed sister

  simile. Corrected wording requires new44/45 builds and fresh captures.



## v0.1.42 - 2026-10-31 - superseded preliminary encyclopedia batch16



- Draft25 profiles53-77 and add34 glossary entries (669 total). Initial independent

  accuracy and3 substantive editorial rechecks recorded;34 regressions passed in

  146.858s on preliminary wording. Both preliminary images passed binary checks.

- Capture25 entries/28 pages with widest name and intact runtime values. Parent

  read all 28 pages and4 Japanese/hide-show/native-keyboard return captures.

- No new display approval recorded: parent native proof returned row 57's sister

  simile to accuracy. Explicit nags wording accepted independently; recapture all25.

- Initial startup navigation timeout resolved after verifying the same VM running;

  no restart/state reload. See runtime_start_v0.1.42.json and

  docs/superseded_v0.1.42-v0.1.43.md. Earlier versioned approvals remain unchanged.



## v0.1.41 - 2026-10-31 - standard game-flow build



- Restore original entry hooks; 346 ATMB drafts plus seven compiled literals.

  Pager/metrics/translated packs match v0.1.40. All 20 disc files / 5,614 packs verify;

  fresh muted startup fits. Native approvals keep their exact earlier build IDs.



## v0.1.40 - 2026-10-31 - encyclopedia batch 15



- Add 25 profiles (pilot 28-52) and 36 glossary entries (635 total).

  Independent accuracy, parent editorial/proofreading and substantive rechecks recorded.

- New 25 entries pass 28 native pages with widest name and intact runtime values.

  Every word/control survives; parent reads every page. Japanese pilot 53, Square,

  name restoration and native exit pass. 308 earlier approvals stay version-bound;

  current old rows, pager/buffers, metrics and font/menu pack match v0.1.38.

- All 34 tests and all-disc checks pass. Remaining 14,808 stored /

  8,251 distinct raw ATMB sources, including 255 encyclopedia entries.

- All 280 machine encyclopedia records and pilot 0-27 retain their exact earlier text approvals; the new native checks apply only to pilot 28-52. Fire En (machine 249) still has an unverified flame-only illustration from v0.1.34. See fire_en_capture_v0.1.34.json. Ordinary library access remains unverified.



## v0.1.39 - 2026-10-31 - standard game-flow build



- Restore original entry hooks; 321 ATMB drafts plus seven compiled literals.

  Pager/metrics/translated packs match v0.1.38. All 20 disc files / 5,614 packs verify;

  fresh muted startup fits. Native approvals keep their exact earlier build IDs.



## v0.1.38 - 2026-10-31 - encyclopedia batch 14



- Add 25 profiles (pilot 3-27) and 33 glossary entries (599 total).

  Independent accuracy, parent editorial/proofreading and substantive rechecks recorded.

- New 25 entries pass 32 native pages with widest name and intact runtime values.

  Every word/control survives; parent reads every page. Japanese pilot 28, Square,

  name restoration and native exit pass. 283 earlier approvals stay version-bound;

  current old rows, pager/buffers, metrics and font/menu pack match v0.1.36.

- All 34 tests and all-disc checks pass. Remaining 14,833 stored /

  8,276 distinct raw ATMB sources, including 280 encyclopedia entries.

- All 280 machine encyclopedia records retain their exact earlier text approvals; the new native checks apply only to pilot 3-27. Fire En (machine 249) still has an unverified flame-only illustration from v0.1.34. See fire_en_capture_v0.1.34.json. Ordinary library access remains unverified.



## v0.1.37 - 2026-10-31 - standard game-flow build



- Restore original entry hooks; 296 ATMB drafts plus seven compiled literals.

  Pager/metrics/translated packs match v0.1.36. All 20 disc files / 5,614 packs verify;

  fresh muted startup fits. Native approvals keep their exact earlier build IDs.



## v0.1.36 - 2026-10-31 - encyclopedia batch 13



- Add 17 profiles 2 and 264-279 and 25 glossary entries (566 total).

  Independent accuracy, parent editorial/proofreading and substantive rechecks recorded.

- New 17 entries pass 18 native pages with widest name and intact runtime values.

  Every word/control survives; parent reads every page. Japanese pilot 3, Square,

  name restoration and native exit pass. 266 earlier approvals stay version-bound;

  current old rows, pager/buffers, metrics and font/menu pack match v0.1.34.

- All 34 tests and all-disc checks pass. Remaining 14,858 stored /

  8,301 distinct raw ATMB sources, including 305 encyclopedia entries.

- All machine encyclopedia records 0-279 now have reviewed English text, including previously deferred Impulse 4. Native approval remains bound to exact wording/build IDs. Fire En (row 249) still has an unverified flame-only illustration from v0.1.34; the current batch does not resolve it. See fire_en_capture_v0.1.34.json and machine_table_milestone_v0.1.37.json.



## v0.1.35 - 2026-10-31 - standard game-flow build



- Restore original entry hooks; 279 ATMB drafts plus seven compiled literals.

  Pager/metrics/translated packs match v0.1.34. All 20 disc files / 5,614 packs verify;

  fresh muted startup fits. Native approvals keep their exact earlier build IDs.



## v0.1.34 - 2026-10-31 - encyclopedia batch 12



- Add 25 profiles 239-263 and 63 glossary entries (541 total).

  Independent accuracy, parent editorial/proofreading and substantive rechecks recorded.

- New 25 entries pass 30 native pages with widest name and intact runtime values.

  Every word/control survives; parent reads every page. Japanese 264, Square,

  name restoration and native exit pass. 241 earlier approvals stay version-bound;

  current old rows, pager/buffers, metrics and font/menu pack match v0.1.32.

- All 34 tests and all-disc checks pass. Remaining 14,875 stored /

  8,316 distinct raw ATMB sources, including 322 encyclopedia entries.

- Fire En (row 249) shows a flame effect in the native preview even after 240 additional input samples in its exact same-build snapshot. Complete text and all nine runtime values remain unchanged. The cause and character-illustration completeness remain unverified; ordinary library or source drawing-path checks are required. No claim of an original-game asset defect is made. See fire_en_capture_v0.1.34.json.



## v0.1.33 - 2026-10-31 - standard game-flow build



- Restore original entry hooks; 254 ATMB drafts plus seven compiled literals.

  Pager/metrics/translated packs match v0.1.32. All 20 disc files / 5,614 packs verify;

  fresh muted startup fits. Native approvals keep their exact earlier build IDs.



## v0.1.32 - 2026-10-31 - encyclopedia batch 11



- Add 25 profiles 214-238 and 72 glossary entries (478 total).

  Independent accuracy, parent editorial/proofreading and substantive rechecks recorded.

- New 25 entries pass 28 native pages with widest name and intact runtime values.

  Every word/control survives; parent reads every page. Japanese 239, Square,

  name restoration and native exit pass. 216 earlier approvals stay version-bound;

  current old rows, pager/buffers, metrics and font/menu pack match v0.1.30.

- All 34 tests and all-disc checks pass. Remaining 14,900 stored /

  8,341 distinct raw ATMB sources, including 347 encyclopedia entries.



## v0.1.31 - 2026-10-31 - standard game-flow build



- Restore original entry hooks; 229 ATMB drafts plus seven compiled literals.

  Pager, metrics and translated packs match 30. All 20 disc files / 5,614 packs verify;

  fresh muted startup warning fits. Native approvals remain bound to 26/28/30.



## v0.1.30 - 2026-10-31 - Maganac through Vifam encyclopedia increment



- Add 25 profiles 189-213 and 47 glossary entries (406 total). Independent accuracy,

  parent editorial/proofreading and accuracy rechecks of editorial 200/209 recorded.

- New 25 entries pass 29 native pages with the widest name and intact nine-value

  storage; every word/control survives. Parent reads all pages. Japanese 214, Square

  hide/show, name restoration and native exit pass. Earlier 191 keep 26/28 approvals;

  current old row bytes, pager/buffers, metrics and font/menu pack match baseline 28.

- All 34 tests and all-disc checks pass. Remaining 14,925 stored / 8,366 distinct raw

  ATMB sources, including 372 encyclopedia entries. Other categories stay unfinished.



## v0.1.29 - 2026-10-31 - standard game-flow build



- Restore original entry hooks; 204 ATMB drafts plus seven compiled literals.

  Pager, metrics and translated packs match 28. All 20 disc files / 5,614 packs verify;

  fresh muted startup warning fits. Native approvals remain bound to 26/28.



## v0.1.28 - 2026-10-31 - Zeon/Mic/Wing encyclopedia increment



- Add 25 profiles 164-188 and 44 glossary entries (359 total). Independent accuracy,

  parent editorial/proofreading, and an accuracy recheck of editorial 164 are recorded.

- New 25 entries pass 29 native pages with the widest name and intact nine-value

  storage; every word/control survives. Parent reads all pages. Japanese 189, Square

  hide/show, name restoration and native exit pass. Earlier 166 keep 26 approvals;

  current earlier row bytes, pager/buffers, metrics and font/menu pack match baseline.

- All 34 tests and all-disc checks pass. Remaining 14,950 stored / 8,391 distinct raw

  ATMB sources, including 397 encyclopedia entries. Other categories stay unfinished.



## v0.1.27 - 2026-10-31 - standard game-flow build



- Restore original entry hooks; retain 179 ATMB drafts and seven compiled literals.

  Pager/buffers, metrics and translated packs match 26. All 20 disc files / 5,614 packs

  verify; fresh muted startup warning fits. No automatic cross-build fit approval.



## v0.1.26 - 2026-10-31 - GaoGaiGar/Gundam encyclopedia increment



- Add 25 complete profiles 139-163 and 58 glossary entries (315 total), with independent

  accuracy, separate parent editorial/proofreading and explicit reference departures.

- All 166 translated entries pass 206 pages with the widest name: 176 exact-pixel

  matches and 30 parent full-size reviews. Every word/control and all nine runtime

  values survive. Original Japanese, Square hide/show and native exit also pass.

- All 34 regressions and all-disc checks pass. Remaining 14,975 stored / 8,416 distinct

  raw ATMB sources, including 422 encyclopedia entries; other categories unfinished.



## v0.1.25 - 2026-10-31 - context-aware source headers



- Distinguish line-start dollar/percent/voice headers from body glyphs; preserve opaque

  binary payloads and track character/runtime/font state. Add six focused tests,

  including execution of the original header-gate instructions. All 34 tests pass.

- Guarded source refresh verifies all 15,154 rows / 51 tables before updating only

  pilot/machine 148 cached representations. All original bytes/hashes remain unchanged.

- Both untouched source 148 displays pass native/full/page-byte, visual and nine-value

  storage checks; source 164, Square and native return pass. This is a bounded grammar

  repair, not full event coverage. No English approval inferred from source displays.



## v0.1.24 - 2026-10-31 - standard game-flow build



- Retain 154 ATMB drafts plus seven ELF literals; restore original entry hooks.

  Pager/buffers, metrics and translated packs match v0.1.23; all 20 disc files /

  5,614 packs verify. Fresh muted startup warning fits. No cross-build fit inference.



## v0.1.23 - 2026-10-31 - Galient/Layzner encyclopedia increment



- Add 21 full profiles 118-138 and 51 glossary entries (257 total). Independent accuracy

  supplies two meaning fixes before separate parent editorial/proofreading. Preserve

  source controls, game geography and explicitly documented reference uncertainties.

- All 141 translated entries pass 176 pages under the widest player name:

  154 exact-pixel references and 22 original-size manual reviews. Every word/control

  and all nine runtime values remain intact. Untouched Japanese/Square/exit also pass.

- Profile original machine 148 percent prose: native decode/full/page bytes and visual

  evidence establish mid-line punctuation, not a consumed header command. No codec

  refresh or English approval inferred; pilot 148 and context-aware extraction remain.

- All 28 tests and all-disc verification pass. Remaining 15,000 stored / 8,441 distinct raw

  ATMB rows, including 447 encyclopedia entries; other text categories remain unfinished.



## v0.1.22 - 2026-10-31 - standard game-flow build



- Retain 133 ATMB drafts and seven ELF literals; restore original entry hooks.

  Pager, font metrics and translated packs match v0.1.21. Full verification passes

  all 20 disc files / 5,614 resource packs; fresh muted startup warning fits.

- Fit approval remains explicitly bound to v0.1.21 and unchanged wording.



## v0.1.21 - 2026-10-31 - Votoms encyclopedia increment



- Add 19 full profiles 99-117 and 36 glossary entries (206 total). Independent accuracy

  finds no mandatory fixes; one editorial shoulder clarification is independently

  rechecked before parent proofreading. Preserve font controls, game geography and

  explicit heading/source-typo/equipment/chronology decisions. No R prose imported.

- All 120 encyclopedia entries pass 154 captured pages: 135 exact-pixel references,

  19 original-size new-page inspections, full source/control bytes and all nine

  runtime slots stable under the maximum-width name. Japanese, Square and cleanup pass.

- All 28 final-code regressions pass. Remaining: 15,021 stored / 8,462 distinct raw ATMB

  rows, including 468 encyclopedia entries. Menu, dialogue/battle, later lifetimes,

  compiled relocation and graphical/movie/spoken-only audits remain unfinished.



## v0.1.20 - 2026-10-31 - protected font selectors and native-state regression



- Protect raw renderer font selectors in the lossless codec. Refresh only five local

  source representations; preserve all 15,154 source hashes. Wrap with native scaled

  widths and runtime values; carry font state across page boundaries and restore normal

  footer size. Expose source font-state diagnostics and explicit-row native audits.

- Five Japanese profiles/six pages retain every byte and all runtime slots; mixed

  headings, ordinary-size prompts, Square and native exit pass. Full ISO verification

  passes. Cross-page compressed-mode stress uses emitted MIPS; no synthetic native

  fixture is claimed. The diagnostic build retains the prior 114 ATMB drafts.



## v0.1.19 - 2026-10-31 - standard build with 101 encyclopedia drafts



- Retain 114 ATMB drafts and seven ELF literals; omit intrusive encyclopedia preview

  hooks. Pager, VWF metrics and translated packs match v0.1.18 byte for byte.

- Full verification passes 20 disc files / 5,614 packs. Fresh muted startup displays

  the complete English warning. Fit approvals remain tied to unchanged wording in

  v0.1.18. Normal library access, menu/help, story/battle and later overlays remain open.



## v0.1.18 - 2026-10-31 - L-Gaim/Zeta encyclopedia increment



- Add 35 complete machine profiles 64-98 and 74 glossary entries (170 total). Resolve

  Zwauth's unnecessary deferral; document canonical spelling corrections, four wiki-

  precedence clarifications/deviations, uncertain names and source-specific claims.

- Apply independent meaning fixes to 80/81/96, three independently checked editorial

  edits, and separate parent proofreading. All 114 ATMB drafts plus seven ELF literals

  have independent accuracy review. Remaining: 15,040 stored / 8,481 distinct raw ATMB

  rows, including 487 encyclopedia entries. Graphics/audio/movies/compiled candidates

  remain outside this denominator.

- Unchanged engine; all 101 library drafts pass 135 pages in fresh muted native

  preview: 93 exact-pixel references, 42 new full-size page inspections, complete

  text bytes, maximum-width name and all nine runtime slots intact. Japanese, Square

  toggle and clean exit pass. Full ISO verification passes.



## v0.1.17 — 2026-10-31 — standard build with 66 encyclopedia drafts



- Keep the 79 ATMB drafts and seven ELF literals from v0.1.16. Omit intrusive preview

  entry hooks; translated packs, VWF metrics, pager code and buffers match that build.

- Full verification passes all 20 files / 5,614 resource packs. Fresh muted startup

  displays the complete English warning. Display approval remains explicitly tied to

  v0.1.16; broader normal gameplay, menu/help and later overlays remain pending.



## v0.1.16 — 2026-10-31 — Dunbine encyclopedia preview build



- Add 18 machine profiles, rows 46–63: Dunbine through the Botune variants. Add 30

  researched glossary entries, including mechanical spellings and character context.

  Coverage is now 79 ATMB drafts plus seven ELF literals, including 66 encyclopedia

  entries; 15,075 stored ATMB rows and 522 encyclopedia entries remain undrafted.

- Independent accuracy review covers every draft. Apply two precision corrections

  before the name audit; independently recheck two editorial clarity edits before

  parent proofreading. Weight/output ambiguity in 54 and provisional English forms

  remain explicit. Zwauth (64) stays deferred for its source/provenance conflict.

- Retain private-context native pagination and VWF without engine changes. Full

  display and runtime-value audits pass all 66 drafts / 93 pages: 70 exact-pixel matches

  plus 23 new full-size manual reviews, with all nine runtime string slots unchanged.

  Untouched Japanese machine 65, Square hide/show and clean native exit pass. Full ISO verification

  passes. Versioned hashes bind fit approval to unchanged wording and this executable.



## v0.1.15 — 2026-10-31 — standard game-flow build



- Omit intrusive preview hooks; keep VWF and corrected native encyclopedia pagination.

  The pager code/buffers and font metrics match v0.1.14 byte for byte.

- Full verification passes all 20 disc files and 5,614 resource packs. Fresh muted boot

  displays the complete English warning. Ordinary library gameplay access and later

  scene/battle testing remain pending; v0.1.14 display approvals stay version-specific.



## v0.1.14 — 2026-10-31 — private message-context test build



- Correct the additional native decoding limit discovered by the v0.1.13 audit:

  `_ctx` has only 400 text bytes before `_mesvalA`. A 409-byte English description

  displayed but overwrote the runtime name. v0.1.13 fit approval was withheld.

- Copy the native library message-lookup routine with its context references redirected

  to a private 16 KiB context buffer. Native runtime-value commands remain intact and

  expand during page drawing. Other message paths keep their original lookup.

- Guard the original context references, bound library input sizes, and add a regression

  that decodes a long description without changing runtime-value storage.

- The audit now checks all nine runtime string slots remain byte-identical after every

  tested entry. All 48 drafts / 70 pages were recaptured with an eight-full-width-W

  name; complete bytes, stable runtime storage and pixel comparisons pass. Fit approval

  is tied to this build and unchanged wording. Japanese 46, Square toggle and clean

  exit to name entry pass. All 23 regression tests and full ISO verification pass.

  v0.1.13 executable/states remain diagnostic.



## v0.1.13 — 2026-10-31 — pagination test build



- Add native encyclopedia pagination at the existing readable font size. ATMB row

  boundaries and wording stay intact. Native control expansion runs before bounded

  copies are divided at line breaks, with Circle prompts for next page or close.

- Reuse native illustration, opacity, input and cleanup logic on each page. Restrict

  interception to the pilot/machine library tables; unrelated table calls retain the

  original message lookup. Standard translation builds also include pagination.

- Bounds failures stop without displaying a partial description and record an error.

  Guard native entry/lookup bytes and copied relative branches; relocate internal

  absolute targets where needed. All new code/buffers remain within the static event

  reservation, ending at 0x009B1000 before the scene overlay at 0x009C0000.

- Add five instruction tests covering all text/final words across pages, mixed-byte

  text, exact page boundaries, buffer limits, register preservation and native fallback.

  Actual layout, Circle transitions and exit acceptance remain separate runtime checks.

- Native pagination displayed all 48 drafts across 70 captured pages, including an

  eight-full-width-character name. Final evidence checks exposed a 400-byte native

  decode-buffer overlap with runtime-name storage, so no display approval was recorded.

  This is a diagnostic build; use the corrected private-context build for further tests.



## v0.1.12 — 2026-10-31 — encyclopedia debug build



- Add 20 machine profiles, rows 26–45. All 61 ATMB drafts and seven ELF literals

  have independent accuracy review; parent editorial/proofreading are separate.

  Coverage is 48 encyclopedia entries, 13 menu/help rows and seven startup literals.

- Apply seven new accuracy fixes before the 68-row glossary audit. Keep energy,

  movement and targeting distinctions, numbered variants and unresolved mechanisms.

  Glossary contains 66 entries with project spellings and uncertainty recorded.

- Add a bounded, fresh-boot encyclopedia preview. This intrusive debug build calls

  original story initialization, native window setup and native per-row illustration

  and scrolling routines. Request changes affect mailbox data only, read between entries.

  Standard builds omit these debug hooks; this is not a normal gameplay/release build.

- Preserve patches inside the original static event segment when it is copied to its

  expanded ELF location. Check the loaded hooks, payload and mailbox against expected bytes.

- Add instruction-level preview tests for initialization order, native record lookup,

  table switching, bounds and exit. Runtime display acceptance is recorded separately.

- Fourteen tests and full disc/pack verification pass. Fresh-boot native preview reaches

  machine and pilot entries with correct illustrations; exit returns to name entry.

  Runtime reveals long-entry vertical clipping in machine 11. Its ending is present

  in RAM but invisible; pagination is required. This build has no broad display approval.



## v0.1.11 — 2026-10-31



- Add 18 machine encyclopedia drafts, rows 8–25. Coverage is now 28 encyclopedia

  entries, 13 menu/help rows and seven compiled UI literals (48 units).

- Independent accuracy review covers all 41 drafted ATMB rows and seven ELF literals.

  Apply six seed changes and four batch changes before the glossary audit. Preserve

  uncertain cannon ownership and source tensions instead of inventing explanations.

- Explicit wiki-precedence override changes the protagonist profile age to 16; the

  source says 18. The cause is unresolved and the deviation is documented, with no

  invented version-specific explanation. Original source and hash remain intact.

- Expand glossary to 43 entries; mark unverified equipment spellings provisional.

  Add dry-run glossary name audit and retain review stages in English exports/coverage.

- Add explicit statefile startup to isolated emulator control. v0.1.10 continuation

  reaches the title menu, name entry, opening story sequence and live dialogue.

- New build is still a test artifact. Encyclopedia/menu fit, translated live dialogue,

  battle VWF and later overlay lifetime remain unapproved.



## v0.1.10 — 2026-10-31



- Translate the blinking memory-card status variant identified by capturing three

  warning-screen phases. The original status message and this variant use separate

  literals. Seven startup/system literals are now drafted; six appear on this warning

  screen and one belongs to another memory-card path.

- ATMB drafts remain 10 encyclopedia entries and 13 menu/help rows. This is still an

  incomplete translation; encyclopedia/menu fit and story/battle testing remain open.

- Eleven regression tests pass. State-load counter resets now fail explicitly instead

  of reporting false progress; input hold/release uses eight/twelve sampling ticks.



## v0.1.9 — 2026-10-31



- Current translation test build: 10 encyclopedia entries, 13 menu/help rows and six

  startup UI literals. Drafts received accuracy, editorial and proofreading self-review;

  review limits and remaining rows are recorded separately.

- Original ISO9660/AFS inventory, 5,614 resource packs, 11,841 members and 51 ATMB tables

  extracted. All 15,154 ATMB rows and all tables pass byte-identical round trips.

- Inclusive compiled-string candidate scanner; raw bytes retained for noncanonical CP932.

- Comparison with Sunrise R: 18 exact shared assets, shared 26px font, exact Shift-JIS

  conversion routine, and 138 normalized text matches; no automatic prose import.

- Source-hashed English exports, terminology glossary, pixel wrapping with dynamic-name

  width, rebuilt ATMB offset tables, ordered packet rebuilding and cached ELF size updates.

- RESOURCE.AFS rebuilt contiguously in index order for the CRI partition reader; later

  disc files shifted as needed. ISO records/volume size and all pack extents verified.

- VWF texture font and measurement/typewriter/scaled drawing hooks, housed in the unused

  tail of the static event-function reservation. Original heap/arena sizes retained.

- Isolated muted emulator, PINE client, guarded input monitor, timestamped screenshots,

  offline savestate inspection, symbol disassembly, coverage and full disc verification.

- Ten regression tests pass, including generated MIPS execution with branch delay slots,

  null-bearing commands, source corpus round trips, growth/ordering and cached sizes.

- Emulator validation reached the English startup warning and the opening video.

  Encyclopedia/menu display fit, story/battle regression and independent review remain open.



## Diagnostic history — 2026-10-31



- v0.1.0: first VWF prototype; top-of-RAM payload was cleared by the resource allocator.

- v0.1.1–v0.1.4: top arena reservation and monitor experiments. Revealed the NOR/store

  delay-slot requirement and byte-swapped button masks. Arena reduction caused runtime

  allocation failures. These builds are diagnostic failures, not usable translation builds.

- v0.1.5: debug baseline using the unused static event-function tail; warning dismissed

  and opening video reached with original fonts/text.

- v0.1.6: VWF-only baseline; proportional Latin glyphs and source Japanese visible in-game.

- v0.1.7–v0.1.8: first translated-table tests. Binary container checks passed but the game

  failed during resource loading. Established two requirements: cached ELF pack sizes and

  contiguous CRI partition order. The loader compacted the directory and read the original

  packet location after an append-style replacement; this approach was removed.

- v0.1.9 replaces those experiments with ordered packet/archive rebuilding. Failed builds

  and their run evidence remain local for diagnosis; do not use their savestates as baselines.





## v0.1.46 / v0.1.47 (superseded preliminary builds)



Both preliminary images passed all20 file/5,614 RESOURCE pack dry-run byte checks.

The current34-test suite passed in213.154s before the name correction. Preview46

reached pilot78 after a fresh boot, but no new entries were audited or approved.

New official positive identity evidence then corrected provisional Shirab to

Shulove in pilot100. 48/49 supersede46/47; none of their native fit is transferable.

See returned stages in the batch17 source, independent and final reviews.

