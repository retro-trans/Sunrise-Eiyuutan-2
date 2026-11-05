"""Profile untouched library148 percent prose; default is a dry run.

Requires an already-running same-build encyclopedia preview. This diagnostic never
edits executable code, source representations or English translation approvals.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
import encyclopedia as page
import preview
import control
import audit_library as audit
from pine import Pine
from textcodec import encode
from elf import Elf, PATH


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('version')
    ap.add_argument('--table', choices=('machine', 'pilot'), default='machine')
    ap.add_argument('--run', action='store_true')
    args = ap.parse_args()
    table = '04973_10516' if args.table == 'machine' else '04973_10515'
    table_id = int(table.split('_')[1])
    source = json.loads((ROOT / 'work/source/text' / (table+'.json')).read_text(encoding='utf-8'))['rows'][148]
    raw = encode(source['jp']).rstrip(b'\0')
    if raw.count(b'\x81\x93\x82\xf0') != 1:
        raise ValueError('Expected the original single percent-plus-particle sequence')
    build = ROOT / 'work/output' / ('v' + args.version)
    info = json.loads((build / 'build_info.json').read_text())
    if not info.get('preview_request') or table+':148' in info['translated_rows']:
        raise ValueError('An untranslated-row148 debug preview build is required')
    expected = Elf((build / 'SLPS_250.70').read_bytes())
    print('Original', args.table, '148 source SHA:', source['sha256'])
    print('Capture native full/page bytes, percent-plus-particle prose and runtime pool; no English fit granted.')
    if not args.run:
        print('DRY RUN: --run selects', args.table, '148 in the already-running same-build preview.')
        return
    result = dict(build=args.version, table=table, id=148,
                  language='untranslated source', source_sha256=source['sha256'], pages=[])
    p = Pine()
    try:
        if not preview.status(p)['running']:
            raise RuntimeError('Start the same-build preview first')
        getter = page.get_message_code(Elf(PATH.read_bytes()))
        for va, size in ((page.WRAPPER, len(page.wrapper_code())),
                         (page.GET_MESSAGE, len(getter)), (0x9A4000, 128)):
            if p.read(va, size) != expected.at(va, size):
                raise RuntimeError('Live code/font metrics differ from the expected build')
        values = p.read(preview.NAME_SLOT, 9 * 37)
        state = audit.select(p, table_id, 148)
        pg = state['pagination']
        native = p.read(page.FULL, pg['source_bytes'])
        if native.strip(b'\n') != raw.strip(b'\n') or b'\x81\x93\x82\xf0' not in native:
            raise ValueError('Native full message differs from original prose')
        result.update(native_sha256=sha(native), native_source_exact=True,
                      percent_and_following_particle_retained=True,
                      runtime_values_sha256=sha(values))
        bodies = []
        while True:
            state = audit.ready(p, table_id, 148, min_page=pg['page'])
            pg = state['pagination']
            blob = p.read(page.PAGE, page.PAGE_SIZE).split(b'\0')[0]
            body, footer = blob.split(b'^0,252,', 1)
            if footer != (b'Circle: Next page' if pg['more'] else b'Circle: Close'):
                raise ValueError('Incorrect page footer')
            bodies.append(page.source_page_body(body, pg['font_start'] - 48, pg['font_end'] - 48))
            label = 'v' + args.version.replace('.', '') + '_percent148_' + args.table + '_p' + str(pg['page'])
            shot = control.shot(p, label)
            result['pages'].append(dict(page=pg['page'], screenshot=str(shot), sha256=sha(shot.read_bytes())))
            if not pg['more']:
                break
            audit.advance(p, state)
            pg = audit.ready(p, table_id, 148, min_page=pg['page'] + 1)['pagination']
        if b''.join(bodies).strip(b'\n') != native.strip(b'\n'):
            raise ValueError('Page bodies lost or duplicated prose')
        if p.read(preview.NAME_SLOT, 9 * 37) != values:
            raise ValueError('Runtime-value pool changed')
        result.update(all_pages_exact=True, runtime_pool_unchanged=True, visual_review='pending',
                      scope='One original '+args.table+'148. Mid-line percent and following particle retained as ordinary native bytes; no English approval or complete command-grammar claim.')
        suffix = '' if args.table == 'machine' else '_pilot'
        dest = ROOT / 'docs' / ('percent148' + suffix + '_v' + args.version + '.json')
        dest.write_text(json.dumps(result, indent=1), encoding='utf-8')
        print(json.dumps(result, indent=1))
    finally:
        p.close()


if __name__ == '__main__':
    main()
