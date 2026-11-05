"""English title/name UI and Latin name keyboard. Dry run unless --write.

The focused image retains the integrated translations of v0.1.139. Reviewed
language proposals outside that build are not silently admitted by this tool.
Original images and extracted source files remain untouched.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import struct
from elf import ROOT, Elf, PATH
from iso import records, read_record
from afs import index
from build import align, update_record

BASE = 0x9B8000
BASE_VERSION = '0.1.139'
BASE_ELF_SHA = 'ba999b798d6871e787851d018e1e11d80ea8cd1a9058fdc385db0a1fdd153494'
SOURCE_ELF_SHA = '00c598e051bd1287ec4523dc757ae2326fb5af28f2dc6c92a2450d6f290290a3'
TITLE_SHA = '5dd806f27a5a26bc5c5afd5c731db2301f8c27625d34750249f9f5e3bd27eee9'
GRID = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.,!?-+:/()[]&*'
LABELS = ('ABC/123', 'Symbols', '←', '→', 'Delete', 'OK')


def digest(b):
    return hashlib.sha256(b).hexdigest()


def fullwidth(s):
    return ''.join(chr(ord(c) + 0xFEE0) if '!' <= c <= '~' else '　' if c == ' ' else c for c in s)


def patch_elf(data):
    original = PATH.read_bytes()
    if digest(original) != SOURCE_ELF_SHA:
        raise ValueError('Unsupported original executable')
    source = Elf(original)
    elf = Elf(data)
    out = bytearray(data)
    payload = bytearray(56 * 4 + 52 * 4 + 53 * 2)
    groups = BASE + 56 * 4
    ranges = groups + 52 * 4
    edits = []

    def string(s, encoding='cp932'):
        address = BASE + len(payload)
        payload.extend(s.encode(encoding) + b'\0')
        return address

    def patch(va, expected, replacement, purpose):
        off = elf.offset(va)
        if bytes(out[off:off + len(expected)]) != expected or len(expected) != len(replacement):
            raise ValueError('Unexpected UI patch site: ' + purpose)
        out[off:off + len(expected)] = replacement
        edits.append(dict(va=hex(va), old=expected.hex(), new=replacement.hex(), purpose=purpose))

    def word(va, expected, replacement, purpose):
        patch(va, struct.pack('<I', expected), struct.pack('<I', replacement), purpose)

    def address(high_site, low_site, expected, replacement, purpose):
        # Both instructions use a signed low half (addiu).
        oldhi, oldlo = struct.unpack('<I', source.at(high_site, 4))[0], struct.unpack('<I', source.at(low_site, 4))[0]
        assert oldhi & 0xFFFF == ((expected + 0x8000) >> 16) & 0xFFFF
        assert oldlo & 0xFFFF == expected & 0xFFFF
        word(high_site, oldhi, (oldhi & 0xFFFF0000) | (((replacement + 0x8000) >> 16) & 0xFFFF), purpose + '/high')
        word(low_site, oldlo, (oldlo & 0xFFFF0000) | (replacement & 0xFFFF), purpose + '/low')

    assert len(GRID) == 50 and len(set(GRID)) == 50
    for i, char in enumerate(GRID):
        label = string(fullwidth(char))
        choices = string(fullwidth(char + char.lower() if char.isupper() else char))
        struct.pack_into('<I', payload, i * 4, label)
        struct.pack_into('<I', payload, groups - BASE + i * 4, choices)
    controls = [string(s) for s in LABELS]
    for i, pointer in enumerate(controls):
        struct.pack_into('<I', payload, (50 + i) * 4, pointer)
    alphabet = string(fullwidth('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'))
    # Retain every original symbol choice (stars, shapes, currency, etc.).
    # Only the default alphabet and visible category labels are localized.
    symbols = 0x231370
    struct.pack_into('<2I', payload, groups - BASE + 50 * 4, alphabet, symbols)
    # All 53 range boundaries are zero: explicit Latin/symbol choices alone.
    # The original implicit kanji-range expansion is intentionally disabled.
    default = string(fullwidth('Kanji'))
    complete_name = string('Kanji Akatsuki')
    address(0x16A4B0, 0x16A4BC, 0x1FBE28, BASE, 'Latin keyboard labels/left')
    address(0x16A54C, 0x16A554, 0x1FBE28, BASE, 'Latin keyboard labels/right')
    address(0x16A5C8, 0x16A5D0, 0x1FBE28, BASE, 'English name controls')
    address(0x16AE30, 0x16AE58, 0x1FBF08, groups, 'Latin upper/lower and symbol choices')
    address(0x16AEDC, 0x16AEE0, 0x1FBFD8, ranges, 'Remove implicit Japanese character ranges')
    address(0x12BC0C, 0x12BC18, 0x237A00, default, 'Default runtime name Kanji')
    for va in (0x1D5854, 0x1D5858):
        word(va, 0x2387E8, default, 'Default pilot short/display name Kanji')
    word(0x1D5850, 0x22AD48, complete_name, 'Default pilot full name Kanji Akatsuki')
    # Widen the control column/window rather than shorten English labels.
    for va, old, new in [(0x16A484, 0x24080064, 0x2408004C),
                         (0x16A490, 0x240A01A6, 0x240A01D6),
                         (0x16A5FC, 0x24080036, 0x24080064),
                         (0x16A638, 0x24080036, 0x24080064),
                         (0x16A6E0, 0x24080036, 0x24080064),
                         (0x16A718, 0x24080036, 0x24080064)]:
        word(va, old, new, 'English name UI geometry')

    phoff = struct.unpack_from('<I', out, 28)[0]
    phsize = struct.unpack_from('<H', out, 42)[0]
    segment_index, segment = next((i, s) for i, s in enumerate(elf.segments) if s[0] == 1 and s[2] == 0x9A0000)
    _, offset, va, _, size, memory_size, flags, alignment = segment
    assert va + max(size, memory_size) <= BASE and BASE + len(payload) <= 0x9C0000
    assert source.symbol('_evefunc_size')['va'] == 0x20000
    for s in elf.segments:
        if s[0] == 1 and s[2] != va:
            assert not max(va, s[2]) < min(BASE + len(payload), s[2] + s[5])
    combined = out[offset:offset + size] + bytes(BASE - va - size) + payload
    new_offset = align(len(out), 4096)
    out.extend(bytes(new_offset - len(out)))
    out.extend(combined)
    struct.pack_into('<8I', out, phoff + phsize * segment_index, 1, new_offset, va, va, len(combined), len(combined), flags, alignment)
    return bytes(out), dict(patches=edits, payload_va=hex(BASE), payload_size=len(payload),
                           label_table=hex(BASE), choices_table=hex(groups), ranges_table=hex(ranges),
                           default_name_va=hex(default), default_name='Kanji',
                           storage='Two-byte fullwidth CP932 Latin per native editable-name cell.',
                           grid=GRID, controls=list(LABELS),
                           keyboard='Latin initial grid; letter keys offer upper/lower case; ABC/123 opens all letters/digits.',
                           source_elf_sha256=SOURCE_ELF_SHA)


def patch_title(data):
    if digest(data) != TITLE_SHA:
        raise ValueError('Unsupported title overlay')
    out = bytearray(data)
    entries = [(0x798, 16, '始めから', 'New Game'), (0x7A8, 16, '続きから', 'Continue'),
               (0x7B8, 8, '対戦', 'Versus'), (0x7C0, 8, 'おまけ', 'Extras'),
               (0x7C8, 16, 'オプション', 'Options')]
    for off, capacity, jp, en in entries:
        old = jp.encode('cp932')
        assert data[off:off + capacity] == old + bytes(capacity - len(old))
        new = en.encode('ascii') + b'\0'
        assert len(new) <= capacity
        out[off:off + capacity] = new + bytes(capacity - len(new))
    return bytes(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('version')
    ap.add_argument('--write', action='store_true')
    args = ap.parse_args()
    import re
    if not re.fullmatch(r'0\.\d+\.\d+', args.version):
        raise ValueError('Expected 0.x.y')
    base = ROOT / 'work/output' / ('v' + BASE_VERSION)
    report = json.loads((base / 'build_info.json').read_text('utf-8'))
    old_elf = (base / 'SLPS_250.70').read_bytes()
    if digest(old_elf) != BASE_ELF_SHA or report['elf_sha256'] != BASE_ELF_SHA:
        raise ValueError('Integrated baseline changed')
    elf, ui = patch_elf(old_elf)
    source_title = (ROOT / 'work/source/afs/EVEMAP/00001.bin').read_bytes()
    title = patch_title(source_title)
    source_iso = Path(report['iso_path'])
    inventory = records(source_iso)
    boot = next(r for r in inventory if r['path'] == '/SLPS_250.70')
    if read_record(source_iso, boot) != old_elf:
        raise ValueError('Baseline ISO executable differs')
    event = next(r for r in inventory if r['path'] == '/EVEMAP.AFS')
    with source_iso.open('rb') as f:
        member = index(f, event['lba'] * 2048, event['size'])[1]
        f.seek(event['lba'] * 2048 + member['offset'])
        if f.read(member['size']) != source_title:
            raise ValueError('Baseline title overlay differs')
    dest = ROOT / 'work/output' / ('v' + args.version)
    if dest.exists():
        raise FileExistsError(dest)
    print(json.dumps(dict(version=args.version, based_on=BASE_VERSION, title_menu=['New Game', 'Continue', 'Versus', 'Options'], ui=ui, elf_sha256=digest(elf)), indent=1))
    print('New local ISO only; retain baseline integrated dialogue; voices unchanged. No runtime test yet.')
    if not args.write:
        print('DRY: --write creates the focused menu/name-entry image.')
        return
    dest.mkdir(parents=True)
    image = dest / ('Sunrise Eiyuutan 2 EN v' + args.version + '.iso')
    shutil.copyfile(source_iso, image)
    with image.open('r+b') as f:
        f.seek(event['lba'] * 2048 + member['offset'])
        f.write(title)
        f.seek(0, 2)
        elf_position = align(f.tell())
        f.write(bytes(elf_position - f.tell()))
        f.write(elf)
        end = align(f.tell())
        f.write(bytes(end - f.tell()))
        update_record(f, boot, elf_position // 2048, len(elf))
        sector = 16
        while True:
            f.seek(sector * 2048)
            head = f.read(7)
            assert head[1:6] == b'CD001'
            if head[0] in (1, 2):
                f.seek(sector * 2048 + 80)
                f.write(struct.pack('<I', end // 2048) + struct.pack('>I', end // 2048))
            if head[0] == 255:
                break
            sector += 1
    (dest / 'SLPS_250.70').write_bytes(elf)
    (dest / '00001.evemap').write_bytes(title)
    report.update(version=args.version, based_on=BASE_VERSION, iso_path=str(image), iso_size=image.stat().st_size,
                  elf_sha256=digest(elf), menu_name_ui=ui, in_game_validation='pending',
                  scope='Focused UI integration; later reviewed language proposals remain separate.',
                  source_audio='Original Japanese voices unchanged; no new subtitles for uncaptioned speech.')
    (dest / 'build_info.json').write_text(json.dumps(report, indent=1), 'utf-8')
    print('WRITE:', image)


if __name__ == '__main__':
    main()
