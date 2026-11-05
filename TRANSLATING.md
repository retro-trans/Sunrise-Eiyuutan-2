# Translating and contributing

Read [Status](docs/STATUS.md) before using the English working exports as a coverage estimate. The public release packages a verified local build; the exports also contain reviewed proposals that are not necessarily integrated.

## Report an issue

Include the release version, episode/location, speaker or menu, complete screenshot and proposed wording. Say whether you cold-booted the patched ISO or loaded an emulator save state. Keep copyrighted Japanese source dumps and game files out of issues and commits.

## Edit English

Structured English is in `work/translation/en/dat/*.en.json`. Each entry retains its native row ID, source SHA-256 and control tokens. Other `*.en.json` files cover compiled strings, names, movies and category-specific integration. Names and terminology are in `work/glossary/glossary.json`.

Treat public English exports as review/reference snapshots. The current local builders consume their associated working drafts and original extracted files. Importing an edited public export into that working pipeline is a maintainer step; merely changing an export does not rebuild the game.

Keep one source row to one English row. Preserve runtime placeholders, control bytes/tokens, deliberate interruptions, speaker identities and original call boundaries. Translate complete meaning before fitting the result. Do not cut the end of a sentence or remove a subject to save bytes. Relocate text and adjust layout within the engine's actual limits.

Read adjacent dialogue to establish who is speaking to whom, what a line answers and which omitted subjects English must restore. Do not infer a person's gender from their name. Keep ambiguous lines on hold when the available scene does not settle them.

## Review in three stages

1. Accuracy: compare against your own extracted Japanese source in scene order, preserving direction, tone, details and ambiguity.
2. Editorial: improve English clarity and character voice without changing meaning. Recheck substantive changes against the source.
3. Proofreading: inspect the final saved English, glossary spellings, controls, punctuation and formatting.

Model-assisted review is recorded as such. Do not label it human proofreading. Follow the full [BASE_RULES.md](BASE_RULES.md).

Run name corrections after language edits; agent proposals can contain older names. Measure final text against actual font advances and runtime substitutions. Ordinary dialogue/help frames must keep their original size and position; extra space for long detail text must remain scoped to that content.

## Local source and builds

Place your own original Japanese ISO at the project root and use the extraction tools described in [TOOLS.md](TOOLS.md). Source files belong under ignored `work/source/`. Public commits must not contain Japanese script dumps or game binaries. Japanese proper-name/lookup terms and short UI labels are allowed.

Inspect each tool's dry run before adding `--write` or `--run`. `tools/strip_jp.py` writes the structured English-only exports after checking source hashes, controls and review metadata. Its source/draft inputs are local; it cannot regenerate those exports from a clean public clone alone.

The cumulative build has historical local inputs, font paths and external movie caches. See [TOOLS.md](TOOLS.md) for the portability limitations. Use the release patch to play; do not assume a clean clone reproduces the release without restoring those inputs.
