"""Scan compiled ELF/overlay CP932 candidates; default is a dry run.

Candidates are evidence for review, not a claim that binary graphics contain prose.
All byte offsets are relative to the named file/member. Raw bytes are retained.
"""
import argparse
import collections
import hashlib
import json
from pathlib import Path
import re
import struct
from elf import ROOT, Elf, PATH

RUN = re.compile(rb'(?:[\x20-\x7e\x09\x0a\x0d\xa1-\xdf]|[\x81-\x9f\xe0-\xfc][\x40-\x7e\x80-\xfc])+')
JP = re.compile(r'[\u3040-\u30ff\u3400-\u9fff\uff61-\uff9f]')
KANA = re.compile(r'[\u3041-\u30fa\uff66-\uff9d]')


def pack_members(data):
    if len(data) < 20:
        raise ValueError('Short resource pack')
    count = struct.unpack_from('<I', data)[0]
    if not 1 <= count < 1000 or 4+count*16 > len(data):
        raise ValueError('Invalid resource pack count')
    entries = []
    for i in range(count):
        mid, off, size, flags = struct.unpack_from('<4I', data, 4+i*16)
        if off > len(data) or off+size > len(data):
            raise ValueError('Invalid resource member extent')
        if size:
            if off < 4+count*16:
                raise ValueError('Member overlaps header')
            entries.append(dict(id=mid, offset=off, size=size, flags=flags))
    return entries


def strings(data):
    for m in RUN.finditer(data):
        raw = m.group()
        # Avoid decoding multi-megabyte image runs; retain long candidates separately.
        try:
            text = raw.decode('cp932')
        except UnicodeDecodeError:
            continue
        jp_count=len(JP.findall(text))
        if jp_count<1:
            continue
        if m.end()==len(data) or data[m.end()]!=0:continue
        # CP932 duplicate mappings cannot always re-encode identically; raw is authoritative.
        yield dict(offset=m.start(), size=len(raw), jp=text, raw=raw.hex(),
                   terminated=m.end() < len(data) and data[m.end()] == 0,
                   roundtrip=text.encode('cp932') == raw)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--write', action='store_true')
    args = ap.parse_args()
    out = ROOT/'work/source'
    summary = collections.Counter()
    samples = []
    pack_index = []
    def process(label, data, va=None, kind='candidate'):
        rows = list(strings(data))
        for row in rows:
            row['id'] = '%s:%08X' % (label, row['offset'])
            if va is not None:
                row['va'] = va+row['offset']
        summary[kind+'_files'] += bool(rows)
        summary[kind+'_rows'] += len(rows)
        summary['cp932_roundtrip_fail'] += sum(not r['roundtrip'] for r in rows)
        for r in rows[:1]:
            if len(samples) < 12:
                samples.append(dict(id=r['id'], size=r['size'], preview=r['jp'][:70]))
        if args.write and rows:
            dest = out/'candidates'/(label+'.json')
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(json.dumps(dict(label=label, kind=kind, sha256=hashlib.sha256(data).hexdigest(), rows=rows),
                                       ensure_ascii=False, indent=1), encoding='utf-8')
    elf = Elf(PATH.read_bytes())
    for sec in elf.sections:
        if sec['type'] == 1 and sec['flags'] & 2 and not sec['flags'] & 4:
            process('ELF/'+sec['name'].lstrip('.'), elf.data[sec['offset']:sec['offset']+sec['size']], sec['va'], 'elf')
    for archive in ('EVEMAP','EVESCEN'):
        for path in sorted((out/'afs'/archive).glob('*.bin')):
            process(archive+'/'+path.stem, path.read_bytes(), 0x9e0000 if archive=='EVEMAP' else 0x9c0000, 'overlay')
    for path in sorted((out/'afs/RESOURCE').glob('*.bin')):
        data = path.read_bytes()
        members = pack_members(data)
        pack_index.append(dict(pack=int(path.stem), members=members))
        summary['resource_packs'] += 1
        summary['resource_members'] += len(members)
        for m in members:
            label = 'RESOURCE/%05d/%05d' % (int(path.stem),m['id'])
            blob = data[m['offset']:m['offset']+m['size']]
            # Structured ATMB extraction is performed by text.py, which handles
            # embedded NULs in control payloads. Scanning opaque assets here
            # produced 6.8 million false positives, so retain only inventory.
    print(json.dumps(dict(counts=summary,samples=samples), ensure_ascii=True,indent=1))
    if args.write:
        (out/'candidate_resource_index.json').write_text(json.dumps(pack_index,indent=1),encoding='utf-8')
        (out/'candidate_summary.json').write_text(json.dumps(summary,indent=1),encoding='utf-8')
    else:
        print('DRY RUN: use --write for local candidate catalogs; text.py handles ATMB tables')


if __name__ == '__main__':
    main()
