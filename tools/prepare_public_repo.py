"""Prepare an explicit source-only publication snapshot; dry-run by default."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'work/publish/v0.8.0/repo'


def selected_files():
    files = {}
    def add(source, target=None):
        source = ROOT / source
        if not source.is_file():
            raise FileNotFoundError(source)
        files[target or source.relative_to(ROOT).as_posix()] = source
    for name in ('AGENTS.md', 'BASE_RULES.md', 'CHANGELOG.md', 'TRANSLATING.md',
                 'TOOLS.md', 'THIRD_PARTY_NOTICES.md', 'requirements.txt', 'debug_tools_guide.md'):
        add(name)
    add('docs/public_README.md', 'README.md')
    add('docs/public_STATUS.md', 'docs/STATUS.md')
    add('docs/release_0.8.0.md')
    add('docs/automatic_patching_0.8.0.md')
    add('docs/automatic_patching_0.8.0.json')
    add('licenses/OFL-NotoSansJP.txt')
    add('work/output/social-preview/sunrise-eiyuutan-2-social-preview.jpg', 'assets/social-preview.jpg')
    add('work/output/social-preview/prompt.txt', 'assets/social-preview-prompt.txt')
    for path in sorted((ROOT / 'tools').rglob('*.py')):
        add(path.relative_to(ROOT))
    for path in sorted((ROOT / 'work/translation/en').rglob('*.en.json')):
        add(path.relative_to(ROOT))
    for path in sorted((ROOT / 'docs').glob('*.en.json')):
        add(path.relative_to(ROOT))
    add('work/glossary/glossary.json')
    add('work/glossary/movie_terms.json')
    for name in ('BUILD-MANIFEST.json', 'BUILD-PROVENANCE.json', 'VALIDATION.json',
                 'DISC-VALIDATION.json', 'README-v0.8.0.txt', 'SHA256SUMS.txt',
                 'SHA256SUMS-v0.8.0.txt', 'SHA1SUMS-v0.8.0.txt', 'CHANGELOG-v0.8.0.txt'):
        add('work/output/v0.8.0/automatic-release/' + name, 'docs/releases/v0.8.0/' + name)
    return files


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--write', action='store_true')
    args = ap.parse_args()
    files = selected_files()
    forbidden = {'.iso', '.bin', '.afs', '.pack', '.p2s', '.exe', '.dll', '.xdelta', '.mp4', '.adx', '.ipu'}
    for name, path in files.items():
        if Path(name).suffix.lower() in forbidden or name.startswith(('work/source/', 'incoming/', 'work/emulator/')):
            raise ValueError('Game data or external binaries entered the publication plan')
        if name.startswith('work/translation/') and not name.endswith('.en.json'):
            raise ValueError('Only English exports may be published')
    report = dict(destination=str(DEST), files=len(files), bytes=sum(p.stat().st_size for p in files.values()),
                  top_level=sorted({n.split('/')[0] for n in files}),
                  examples=['README.md', 'tools/trade_patch.py', 'work/translation/en/dat/00022_10512.en.json',
                            'docs/STATUS.md', 'docs/releases/v0.8.0/BUILD-MANIFEST.json'],
                  excluded='Original/patched ISOs, extracted game data, original Japanese scripts, local raw drafts, review caches and external binaries')
    print(json.dumps(report, indent=2), flush=True)
    if not args.write:
        print('DRY RUN: no publication files copied.')
        return
    if DEST.exists():
        raise FileExistsError('Refusing to overwrite a publication snapshot')
    DEST.mkdir(parents=True)
    for name, source in files.items():
        target = DEST / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    (DEST / '.gitignore').write_text('*.iso\n*.bin\n*.afs\n*.pack\n*.p2s\n*.xdelta\n*.mp4\n__pycache__/\nwork/source/\nwork/output/\nwork/emulator/\nwork/ui/\nwork/publish/\nincoming/\nwork/translation/**/*.json\n!work/translation/**/*.en.json\nwork/translation/**/slices/\n', 'utf8')
    (DEST / 'assets/README.md').write_text(
        '# Social preview\n\nCreated with built-in image generation using the supplied A.C.E. banner as a style reference and the Sunrise Eiyuutan 2 cover as a subject reference. The cover in the banner is generated, not a byte-exact reproduction.\n\n'
        'Cover reference: https://gamesdb.launchbox-app.com/games/images/130934-sunrise-eiyuutan-2\n\n'
        'The exact prompt is in social-preview-prompt.txt. Upload social-preview.jpg in GitHub repository Settings > Social preview.\n', 'utf8')
    snapshot = {name: hashlib.sha256((DEST / name).read_bytes()).hexdigest() for name in files}
    report.update(sha256=snapshot)
    (DEST.parent / 'publication-plan.json').write_text(json.dumps(report, indent=2) + '\n', 'utf8')
    print('WRITE: explicit source-only snapshot prepared.')


if __name__ == '__main__':
    main()
