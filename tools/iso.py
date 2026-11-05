"""Read primary ISO9660 records; extract explicitly with --extract (no ISO writes)."""
import argparse
import hashlib
import json
from pathlib import Path
import struct

ROOT = Path(__file__).resolve().parents[1]
ISO = ROOT / 'Sunrise Eiyuutan 2 (Japan).iso'
SECTOR = 2048


def records(image):
    with open(image, 'rb') as f:
        f.seek(16 * SECTOR)
        pvd = f.read(SECTOR)
        if pvd[:7] != b'\x01CD001\x01':
            raise ValueError('Expected primary ISO9660 descriptor at sector 16')
        def directory(lba, size, parent):
            f.seek(lba * SECTOR)
            data = f.read(size)
            pos = 0
            while pos < len(data):
                n = data[pos]
                if not n:
                    pos = (pos // SECTOR + 1) * SECTOR
                    continue
                rec = data[pos:pos+n]
                if n < 34 or len(rec) != n:
                    raise ValueError('Truncated directory record')
                name = rec[33:33+rec[32]]
                child_lba, child_size = struct.unpack_from('<I', rec, 2)[0], struct.unpack_from('<I', rec, 10)[0]
                if name not in (b'\x00', b'\x01'):
                    path = parent + '/' + name.decode('ascii').split(';')[0]
                    item = dict(path=path, lba=child_lba, size=child_size,
                                record_offset=lba*SECTOR+pos, directory=bool(rec[25] & 2))
                    yield item
                    if item['directory']:
                        yield from directory(child_lba, child_size, path)
                pos += n
        root = pvd[156:190]
        return list(directory(struct.unpack_from('<I', root, 2)[0], struct.unpack_from('<I', root, 10)[0], ''))


def read_record(image, record):
    with open(image, 'rb') as f:
        f.seek(record['lba'] * SECTOR)
        data = f.read(record['size'])
    if len(data) != record['size']:
        raise ValueError('Truncated extent')
    return data


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--iso', type=Path, default=ISO)
    ap.add_argument('--extract', action='store_true')
    args = ap.parse_args()
    inventory = records(args.iso)
    selected = [r for r in inventory if not r['directory'] and
                (r['path'].startswith('/DATA/') or r['path'].startswith('/SLPS') or r['path']=='/SYSTEM.CNF')]
    print(json.dumps(selected, indent=2))
    print('EXTRACT' if args.extract else 'DRY RUN: use --extract for ELF, CNF and DATA only')
    if args.extract:
        out = ROOT / 'work/source/iso'
        for r in selected:
            dest = out / r['path'].lstrip('/')
            dest.parent.mkdir(parents=True, exist_ok=True)
            data = read_record(args.iso, r)
            dest.write_bytes(data)
            r['sha256'] = hashlib.sha256(data).hexdigest()
        (out.parent / 'iso_inventory.json').write_text(json.dumps(inventory, indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()
