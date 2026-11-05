# Retro Trans Automatic patching — v0.8.0

The existing release is now registered in the shared Retro Trans catalog. No application update or replacement game patch is needed. Click **Refresh catalog**, select the original Japanese SLPS-25070 ISO in **Automatic**, choose **Latest**, and click **Patch** to save a new output.

The initial upload used a project-specific provenance manifest and omitted central registration. The correction adds the standard schema-v1 manifest, SLPS-25070 package ID, manifest-bound validation report and canonical SHA256SUMS.txt. Original build/disc reports remain available as BUILD-PROVENANCE.json and DISC-VALIDATION.json. The published patch keeps asset ID 713256863, size 366,335,745 and SHA-256 `4676e3558584621dd4d55227d7a7e245945cea757f1f0e686bc5853fbd082443`. The v0.8.0 source tag and complete output image remain unchanged.

The [hosted catalog refresh](https://github.com/retro-trans/retro-trans-tools/actions/runs/42031724993) passes. It downloads and validates the published assets and adds exactly one record. All 110 earlier binary release records, Dreamcast DCP routes and withdrawn records are unchanged. Shared registration, catalog routing and catalog import tests pass: 46 focused checks in total. No app executable was rebuilt or published.

A fresh isolated Retro Trans 0.5.20 backend run against the actual original ISO passes the complete Automatic path: live catalog refresh, unique source recognition, Latest route selection, verified public patch download to an empty cache, decoding with the app's own bundled xdelta engine, complete target verification and recognition of the result as already-current v0.8.0. The source image and user settings are untouched. The test finishes in 109.656 seconds. See [the machine-readable evidence](automatic_patching_0.8.0.json).

Output: 2,627,004,416 bytes; SHA-256 `8fa9f17a838b4c22c591467ad343b7130d159efcd00b5cbb413c43175b8e2f7f`; SHA-1 `2e74d9e7711abca1806aa5bb6d2400eea255550b`.

This verifies the Automatic patching backend rather than GUI clicks, a CHD conversion, a game playthrough or physical-hardware behavior. Existing translation and gameplay limits still apply.
