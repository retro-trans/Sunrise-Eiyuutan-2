** Organize folder like this **
work - work folder
    output - contains the file for testing (iso, zip, etc...)
    glossary - contains the one or many json files for glossary
    ui - contains screenshot of actual UI element ingame with label on screenshot if possible, contains files (json,py,...) describe the coordinate, width and height, id and other attributes
    translation/<language code> - contains the target translation of ui element or dialogues or anything that need translation
docs - documents
tools - any tools help with translation
incoming - outside files that need agent to look into

** SOME RULES **
- Avoid contains extensive Japanese scripts (UI elements is fine)
- Identified each build with version 0.x.y (start at 0.1.0)
- Always write change log
- If user told you to remember anything write it down here, make sure to ask user if the new one conflict with old one
- Be conscious of subscription limit before creating sub-agents

** REMEMBER **
- Retro Trans Automatic requires its standard release manifest, manifest-bound validation report, canonical SHA256SUMS.txt and central game-library/catalog registration. Use registered PS2 disc ID SLPS-25070. Public v0.8.0 Automatic compatibility is verified; preserve its published patch and binary hashes. See docs/automatic_patching_0.8.0.md/json.
- Public repository: https://github.com/retro-trans/Sunrise-Eiyuutan-2, published using binhlt0402. The Git checkout is work/publish/v0.8.0/repo; the project root has no Git metadata. Public v0.8.0 packages byte-exact local v0.2.31. See docs/github_publication_0.8.0.json for release and asset verification. Later releases still require an explicit user request.
- Keep the original normal dialogue/help box size and position. Any extra height needed by long detail text must be scoped to that content, so ordinary help boxes return to the original layout (user preference, 2026-11-05).
- Opening and ending song subtitles should display romaji and English, with no Japanese lyric tier (user preference, 2026-11-05).
- Follow the editorial-pass workflow in `BASE_RULES.md` for translated scripts: accuracy review, editorial review for clarity and character voice, then final proofreading.
- Build debug tool using `debug_tools_guide.md`
- When using emulator disable audio
- Do not create or publish a GitHub release until the user explicitly requests a release for that build. Translation and local builds do not imply release permission.
- Japanese script text must never be committed to git. Keeping it in local working files is fine: `.gitignore` covers `work/source/` and the translation working files. Commit only the `*.en.json` copies written by `tools/strip_jp.py` (run it before committing). Names and UI terms in Japanese are allowed.
