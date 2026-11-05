"""Exercise published Automatic refresh/recognition/download/patching on a real ISO.

Dry-run by default; --run uses a fresh isolated cache and a new output filename.
No user app settings, existing images or emulator data are changed.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--tools-dir', type=Path, required=True)
    ap.add_argument('--run', action='store_true')
    args = ap.parse_args()
    source = ROOT / 'Sunrise Eiyuutan 2 (Japan).iso'
    work = ROOT / 'work/automatic-0.8.0/live-test'
    output = work / 'Sunrise Eiyuutan 2 EN v0.8.0 - Automatic.iso'
    expected = json.loads((ROOT / 'work/output/v0.8.0/automatic-release/BUILD-MANIFEST.json').read_text('utf8'))
    print(json.dumps(dict(source=str(source), output=str(output), isolated_cache=str(work / 'cache'),
                         steps=['Refresh published catalog', 'Recognize complete original ISO hash',
                                'Plan Latest route', 'Download published patch to empty cache',
                                'Apply using Retro Trans engine and verify target',
                                'Recognize output as current v0.8.0']), indent=2), flush=True)
    if not args.run:
        print('DRY RUN: no download or output files created.')
        return
    if work.exists():
        raise FileExistsError('Refusing to reuse an integration-test cache/output')
    work.mkdir(parents=True)
    sys.path.insert(0, str(args.tools_dir.resolve()))
    from retro_trans import __version__
    from retro_trans.catalog import refresh_catalog, recognize, apply_plan, file_hashes
    from retro_trans.core import GitHubClient
    started = time.monotonic()
    catalog = refresh_catalog(cache=work / 'cache')
    records = [r for r in catalog.data['releases'] if r['repo'] == 'retro-trans/Sunrise-Eiyuutan-2' and r['tag'] == 'v0.8.0']
    if len(records) != 1 or records[0]['manifest'] != expected:
        raise ValueError('Published catalog does not contain the exact corrected manifest')
    print('Published catalog refresh passed.', flush=True)
    matches = [n for n in recognize(source, catalog) if n.id[0] == expected['game_id']]
    if len(matches) != 1 or matches[0].version != 'original':
        raise ValueError('Original ISO was not uniquely recognized')
    plan = catalog.plan(matches[0], 'Latest')
    if plan.target.version != '0.8.0' or len(plan.edges) != 1:
        raise ValueError('Latest did not select the single v0.8.0 patch')
    print('Recognized original; route:', plan.summary, flush=True)
    phases = set()
    def progress(message, fraction):
        phase = message.split(':', 1)[-1].strip()
        if phase not in phases:
            phases.add(phase)
            print(message, flush=True)
    apply_plan(source, output, plan, catalog, client=GitHubClient(), cache=work / 'cache', progress=progress)
    target_matches = [n for n in recognize(output, catalog) if n.id[0] == expected['game_id']]
    if len(target_matches) != 1 or target_matches[0].version != '0.8.0':
        raise ValueError('Patched image was not recognized as v0.8.0')
    current = catalog.plan(target_matches[0], 'Latest')
    if current.edges:
        raise ValueError('Already-current image incorrectly has another patch route')
    target_hashes = file_hashes(output, ('sha256', 'sha1'))
    patch = expected['patches'][0]
    if target_hashes['sha256'] != patch['target_sha256'] or target_hashes['sha1'] != patch['target_sha1']:
        raise ValueError('Completed Automatic output checksum mismatch')
    report = dict(status='passed', retro_trans_version=__version__, source_recognized='original',
                  target_recognized='0.8.0', route=plan.summary, patch_operations=len(plan.edges),
                  catalog_sha256=hashlib.sha256((work / 'cache/catalog.json').read_bytes()).hexdigest(),
                  patch_sha256=patch['patch_sha256'], patch_bytes=patch['patch_bytes'],
                  downloaded_from_published_release=True, cache_initially_empty=True,
                  target_bytes=output.stat().st_size, target_hashes=target_hashes,
                  already_current_route_operations=len(current.edges),
                  elapsed_seconds=round(time.monotonic() - started, 3),
                  game_playthrough=False, chd_tested=False)
    (work / 'verification.json').write_text(json.dumps(report, indent=2) + '\n', 'utf8')
    print(json.dumps(report, indent=2), flush=True)


if __name__ == '__main__':
    main()
