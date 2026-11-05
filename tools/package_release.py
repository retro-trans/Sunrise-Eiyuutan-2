"""Package the verified cumulative build as public v0.8.0; dry-run by default.

Only patch/instruction/validation files are intended for release upload.
The decoded ISO stays local and proves the xdelta round trip.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
VERSION = '0.8.0'
BASE_VERSION = '0.2.31'
SOURCE_SHA256 = '5d6f96c972ac65bb5dddbadc832dc749a59b86b8c4507408231bed725b8524e8'
TARGET_SHA256 = '8fa9f17a838b4c22c591467ad343b7130d159efcd00b5cbb413c43175b8e2f7f'
TARGET_ELF_SHA256 = '0a2d1325e3f0779d14f52bb35ad60654fd1a932e87675b3dda07770612eba5f8'


def fingerprints(path):
    hashes = {a: hashlib.new(a) for a in ('sha256', 'sha1', 'md5')}
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            for value in hashes.values():
                value.update(block)
    return dict(size=path.stat().st_size, **{a: h.hexdigest() for a, h in hashes.items()})


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--xdelta', type=Path, required=True)
    ap.add_argument('--write', action='store_true')
    args = ap.parse_args()
    source = ROOT / 'Sunrise Eiyuutan 2 (Japan).iso'
    baseline = ROOT / 'work/output' / ('v' + BASE_VERSION)
    target = baseline / f'Sunrise Eiyuutan 2 EN v{BASE_VERSION}.iso'
    destination = ROOT / 'work/output' / ('v' + VERSION)
    release = destination / 'release'
    patch = release / f'Sunrise-Eiyuutan-2-English-v{VERSION}.xdelta'
    decoded = destination / f'Sunrise Eiyuutan 2 EN v{VERSION}.iso'
    encode = [str(args.xdelta.resolve()), '-e', '-9', '-B', '67108864', '-S', 'djw', '-s', str(source), str(target), str(patch)]
    decode = [str(args.xdelta.resolve()), '-d', '-s', str(source), str(patch), str(decoded)]
    info = json.loads((baseline / 'build_info.json').read_text('utf8'))
    verification = json.loads((baseline / 'verification.json').read_text('utf8'))
    if info['elf_sha256'] != TARGET_ELF_SHA256 or info['iso_sha256'] != TARGET_SHA256:
        raise ValueError('The verified baseline metadata changed')
    if verification['files_verified'] != 20 or verification['resource_packs_verified'] != 5614:
        raise ValueError('Missing complete baseline disc verification')
    print(json.dumps(dict(version=VERSION, baseline=BASE_VERSION, source=str(source),
                         source_sha256=SOURCE_SHA256, target_sha256=TARGET_SHA256,
                         release_directory=str(release), encode=encode, decode=decode,
                         note='Public version alias: game bytes remain identical to verified 0.2.31.'), indent=2), flush=True)
    if not args.write:
        print('DRY RUN: no files created; use --write after reviewing the plan.')
        return
    if destination.exists():
        raise FileExistsError('Refusing to overwrite a release directory')
    source_hashes = fingerprints(source)
    target_hashes = fingerprints(target)
    if source_hashes['sha256'] != SOURCE_SHA256 or target_hashes['sha256'] != TARGET_SHA256:
        raise ValueError('Full source or target image checksum mismatch')
    release.mkdir(parents=True)
    print('Encoding xdelta from original Japanese image...', flush=True)
    subprocess.run(encode, check=True)
    print('Decoding the patch with source verification enabled...', flush=True)
    subprocess.run(decode, check=True)
    decoded_hashes = fingerprints(decoded)
    if decoded_hashes != target_hashes:
        raise ValueError('Patch round trip is not the exact verified target')
    info.update(version=VERSION, public_release_baseline=BASE_VERSION,
                iso_path=str(decoded), iso_size=decoded_hashes['size'],
                release_note='Packaging/version alias only; no game bytes change from 0.2.31.')
    (destination / 'build_info.json').write_text(json.dumps(info, indent=1) + '\n', 'utf8')
    (destination / 'SLPS_250.70').write_bytes((baseline / 'SLPS_250.70').read_bytes())
    manifest = dict(
        version=VERSION, game='Sunrise Eiyuutan 2', edition='Japanese original, SLPS-25070',
        baseline=BASE_VERSION, game_bytes_unchanged_from_baseline=True,
        source=dict(name=source.name, **source_hashes),
        target=dict(name=decoded.name, **decoded_hashes),
        patch=dict(name=patch.name, **fingerprints(patch)),
        xdelta=dict(version='3.1.0', executable_sha256=fingerprints(args.xdelta)['sha256'],
                    options=['-e', '-9', '-B', '67108864', '-S', 'djw']),
        validation=dict(round_trip='passed: decoded size, SHA-256, SHA-1 and MD5 equal verified target',
                        files_verified=20, resource_packs_verified=5614,
                        event_members_verified=80, movie_members_verified=489,
                        original_audio_preserved=True,
                        full_playthrough=False, battle_dialogue_holds=56),
        source_code_note='Repository snapshot includes tools and English exports. Historical build inputs and local media caches are not distributed; the repository alone is not a one-command rebuild kit.'
    )
    (release / 'BUILD-MANIFEST.json').write_text(json.dumps(manifest, indent=2) + '\n', 'utf8')
    verification.update(version=VERSION, verified_byte_identical_baseline=BASE_VERSION,
                        patch_round_trip=manifest['validation']['round_trip'],
                        source_sha256=SOURCE_SHA256, target_sha256=TARGET_SHA256)
    (release / 'VALIDATION.json').write_text(json.dumps(verification, indent=2) + '\n', 'utf8')
    print(json.dumps(manifest, indent=2), flush=True)


if __name__ == '__main__':
    main()
