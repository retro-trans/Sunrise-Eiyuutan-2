"""Inventory every AFS; --extract unpacks only resources and event overlays."""
import argparse
import collections
import json
import struct
from pathlib import Path
from iso import ROOT, ISO, records


def index(stream, base, size):
    stream.seek(base)
    magic, count = struct.unpack('<4sI', stream.read(8))
    if magic != b'AFS\0' or not 0 < count < 100000:
        raise ValueError('Invalid AFS header')
    table = stream.read(count*8)
    entries = []
    for i in range(count):
        off, length = struct.unpack_from('<II', table, i*8)
        if off < 8+count*8 or off+length > size:
            raise ValueError('Invalid AFS extent %d' % i)
        entries.append(dict(id=i, offset=off, size=length))
    return entries


def validate_partition(entries):
    """The game's ADXF_LoadPartitionNw path stores contiguous sector counts."""
    cursor=entries[0]['offset']
    for e in entries:
        if e['offset']!=cursor or e['offset']%2048 or (e['size']+2047)//2048>65535:
            raise ValueError('AFS is incompatible with the game partition loader')
        cursor=((e['offset']+e['size']+2047)//2048)*2048


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--extract', action='store_true')
    args = ap.parse_args()
    all_entries = []
    with open(ISO, 'rb') as stream:
        for rec in records(ISO):
            if not rec['path'].endswith('.AFS'):
                continue
            entries = index(stream, rec['lba']*2048, rec['size'])
            selected = rec['path'] in ('/RESOURCE.AFS', '/EVEMAP.AFS', '/EVESCEN.AFS')
            magic = collections.Counter()
            for ent in entries:
                stream.seek(rec['lba']*2048+ent['offset'])
                head = stream.read(min(16, ent['size']))
                ent['magic'] = head[:4].hex()
                magic[ent['magic']] += 1
                if args.extract and selected:
                    stream.seek(rec['lba']*2048+ent['offset'])
                    data = stream.read(ent['size'])
                    if len(data) != ent['size']:
                        raise ValueError('Truncated member')
                    dest = ROOT/'work/source/afs'/rec['path'][1:-4]/('%05d.bin' % ent['id'])
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    dest.write_bytes(data)
            all_entries.append(dict(**rec, entries=entries))
            print(rec['path'], 'entries', len(entries), 'extract', selected, 'top magic', magic.most_common(8))
    if args.extract:
        (ROOT/'work/source/afs_index.json').write_text(json.dumps(all_entries, indent=1), encoding='utf-8')
    else:
        print('DRY RUN: pass --extract to write resource/event members and inventory')


if __name__ == '__main__':
    main()
