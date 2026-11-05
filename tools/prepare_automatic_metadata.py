"""Add Retro Trans standard metadata around the unchanged public v0.8.0 patch.

Dry-run by default. Preserve the original release directory and create a new
metadata staging directory; never re-encode or overwrite the published patch.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
COMMIT = '5fa6da9de30e0b96bfa8ea2406e5649d7b8e22a1'
PATCH_SHA = '4676e3558584621dd4d55227d7a7e245945cea757f1f0e686bc5853fbd082443'


def sha(path, algorithm='sha256'):
    result = hashlib.new(algorithm)
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            result.update(block)
    return result.hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--write', action='store_true')
    args = ap.parse_args()
    old = ROOT / 'work/output/v0.8.0/release'
    stage = ROOT / 'work/output/v0.8.0/automatic-release'
    provenance = json.loads((old / 'BUILD-MANIFEST.json').read_text('utf8'))
    patch = old / provenance['patch']['name']
    if provenance['patch']['sha256'] != PATCH_SHA:
        raise ValueError('Published patch identity changed')
    manifest = dict(schema_version=1, game_id='sunrise-eiyuutan-2',
                    game_name='Sunrise Eiyuutan 2', platform='PS2', version='0.8.0',
                    source_commit=COMMIT,
                    package_ids=[dict(platform='PS2', kind='disc-id', id='SLPS-25070')],
                    patches=[dict(patch=patch.name, edition='japan-slps-25070', language='en',
                                  source_version='original', source_format='iso', target_format='iso',
                                  source_sha256=provenance['source']['sha256'],
                                  source_sha1=provenance['source']['sha1'],
                                  source_bytes=provenance['source']['size'],
                                  target_sha256=provenance['target']['sha256'],
                                  target_sha1=provenance['target']['sha1'],
                                  target_bytes=provenance['target']['size'],
                                  patch_sha256=PATCH_SHA, patch_bytes=provenance['patch']['size'])])
    print(json.dumps(dict(destination=str(stage), manifest=manifest,
                         unchanged='Published patch bytes, source/output identities, release version and tag.'), indent=2), flush=True)
    if not args.write:
        print('DRY RUN: no files copied or uploaded.')
        return
    if stage.exists():
        raise FileExistsError('Refusing to overwrite an existing metadata staging directory')
    if patch.stat().st_size != provenance['patch']['size'] or sha(patch) != PATCH_SHA:
        raise ValueError('Published patch bytes do not match their complete checksum')
    if provenance['validation']['round_trip'] != 'passed: decoded size, SHA-256, SHA-1 and MD5 equal verified target':
        raise ValueError('Missing the original successful full-image round-trip evidence')
    stage.mkdir()
    try:
        os.link(patch, stage / patch.name)
    except OSError:
        shutil.copyfile(patch, stage / patch.name)
    shutil.copyfile(old / 'BUILD-MANIFEST.json', stage / 'BUILD-PROVENANCE.json')
    shutil.copyfile(old / 'VALIDATION.json', stage / 'DISC-VALIDATION.json')
    (stage / 'BUILD-MANIFEST.json').write_text(json.dumps(manifest, indent=2) + '\n', 'utf8')
    validation = dict(schema_version=1, manifest_sha256=sha(stage / 'BUILD-MANIFEST.json'),
                      patches=[dict(patch=patch.name, roundtrip_verified=True,
                                    target_sha256=provenance['target']['sha256'])],
                      evidence='Original complete xdelta reconstruction retained in BUILD-PROVENANCE.json; full-disc checks retained in DISC-VALIDATION.json.',
                      patch_bytes_unchanged=True)
    (stage / 'VALIDATION.json').write_text(json.dumps(validation, indent=2) + '\n', 'utf8')
    notes = (ROOT / 'docs/release_0.8.0.md').read_text('utf8')
    (stage / 'README-v0.8.0.txt').write_text(notes + '\n\nCOMPLETE SOURCE / OUTPUT FINGERPRINTS\n\n' +
        json.dumps({key: provenance[key] for key in ('source', 'target', 'patch')}, indent=2) + '\n', 'utf8')
    (stage / 'CHANGELOG-v0.8.0.txt').write_text(
        (ROOT / 'CHANGELOG.md').read_text('utf8').split('## v0.2.31')[0], 'utf8')
    files = sorted(stage.iterdir())
    for algorithm, name in (('sha256', 'SHA256SUMS.txt'), ('sha256', 'SHA256SUMS-v0.8.0.txt'), ('sha1', 'SHA1SUMS-v0.8.0.txt')):
        (stage / name).write_text(''.join(sha(p, algorithm) + '  ' + p.name + '\n' for p in files), 'ascii')
    print('WRITE: compatible metadata prepared; original patch and release folder preserved.', flush=True)


if __name__ == '__main__':
    main()
