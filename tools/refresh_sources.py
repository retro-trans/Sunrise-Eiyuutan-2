"""Refresh changed editor representations after verifying every original source byte.

Default is a dry run. Writes only cached rows whose representation changed;
original archives, source hashes, IDs and table inventories are never rewritten.
"""
import argparse
import hashlib
import json
from elf import ROOT
from extract import pack_members
from textcodec import decode, encode, parse_table, build_table, controls


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--write', action='store_true')
    args = ap.parse_args()
    inventory = json.loads((ROOT/'work/source/text_inventory.json').read_text(encoding='utf-8'))
    packs = {}
    updates = {}
    changes = []
    examined = 0
    for table in inventory:
        pack = table['pack']
        if pack not in packs:
            data = (ROOT/'work/source/afs/RESOURCE'/('%05d.bin' % pack)).read_bytes()
            packs[pack] = (data, pack_members(data))
        data, members = packs[pack]
        member = next(m for m in members if m['id'] == table['member'])
        raw_table = data[member['offset']:member['offset']+member['size']]
        if hashlib.sha256(raw_table).hexdigest() != table['sha256']:
            raise ValueError('Original table hash changed: ' + table['table'])
        rows = parse_table(raw_table)
        if build_table(rows) != raw_table:
            raise ValueError('Table roundtrip failed')
        path = ROOT/'work/source/text'/(table['table']+'.json')
        obj = json.loads(path.read_text(encoding='utf-8'))
        if obj['table'] != table['table'] or len(obj['rows']) != len(rows):
            raise ValueError('Cached table identity/count changed')
        changed = False
        for i, (old, raw) in enumerate(zip(obj['rows'], rows)):
            examined += 1
            digest = hashlib.sha256(raw).hexdigest()
            if old['id'] != i or old['sha256'] != digest or old['size'] != len(raw) or encode(old['jp']) != raw:
                raise ValueError('Cached source differs from original: ' + table['table'] + ':' + str(i))
            new = decode(raw)
            if encode(new) != raw:
                raise ValueError('New representation lost bytes')
            if old['jp'] != new:
                changes.append(dict(table=table['table'], id=i, source_sha256=digest,
                                    old_controls=controls(old['jp']), new_controls=controls(new)))
                old['jp'] = new
                changed = True
        if changed:
            updates[path] = obj
    print(json.dumps(dict(tables_examined=len(inventory), rows_examined=examined,
                          changed_rows=len(changes), changed_files=len(updates), changes=changes), indent=1))
    if args.write:
        # All original/cached/new rows must pass before any cached file is touched.
        for path, obj in updates.items():
            path.write_text(json.dumps(obj, ensure_ascii=False, indent=1), encoding='utf-8')
    else:
        print('DRY RUN: --write refreshes only the listed representations; every raw byte/hash stays unchanged.')


if __name__ == '__main__':
    main()
