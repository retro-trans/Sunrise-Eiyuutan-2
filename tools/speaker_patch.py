"""Relocate every native dialogue speaker label; dry run unless --write.

Only pilot record+8 pointers change. The native chosen-player-name branch,
portraits, gameplay records and auto-sized nameplate geometry stay intact.
"""
import argparse
import hashlib
import json
import re
import struct
from elf import ROOT, PATH, Elf

TABLE = 0x1D5810
COUNT = 860
STRIDE = 64
BASE = 0x9B9000
LIMIT = 0x9C0000
SOURCE_SHA = '00c598e051bd1287ec4523dc757ae2326fb5af28f2dc6c92a2450d6f290290a3'
BASE_SHA = '177b6e3f86efba6f7e2220961ea7e77aa56450b1d50aa397ddc94b6f1574cebb'
LANGUAGE = ROOT / 'work/translation/en/speaker-names.en.json'
LANGUAGE_SHA = '95f5146f695070eadc119a99bc24aae0669a7a02ca4e47f467c7d523bb1726ca'
digest = lambda b: hashlib.sha256(b).hexdigest()


def name_width(text, widths):
    # ttxtGetStrW calls fontGetSP (0x108CA0): one-pixel spacing for ASCII,
    # two for fullwidth glyphs. Dialogue's typewriter uses a different spacing.
    return sum(widths[ord(c)] + 1 for c in text)


def read_names():
    raw = LANGUAGE.read_bytes()
    if digest(raw) != LANGUAGE_SHA:
        raise ValueError('Speaker language revision requires review')
    document = json.loads(raw)
    rows = document['rows']
    if document['source_elf_sha256'] != SOURCE_SHA or [r['id'] for r in rows] != list(range(1, COUNT)):
        raise ValueError('Incomplete or reordered speaker inventory')
    if document['review'] != {'accuracy':'independent-reviewed', 'editorial':'complete', 'glossary':'complete', 'proofreading':'complete'}:
        raise ValueError('Speaker wording has not completed review')
    return rows


def patch_elf(data, widths):
    original = PATH.read_bytes()
    if digest(original) != SOURCE_SHA:
        raise ValueError('Unsupported original executable')
    source, elf = Elf(original), Elf(data)
    if source.symbol('plt_info')['va'] != TABLE or source.symbol('plt_info')['size'] != COUNT * STRIDE:
        raise ValueError('Unexpected pilot table')
    out = bytearray(data)
    payload = bytearray()
    strings = {}
    edits = []
    for row in read_names():
        number = row['id']
        va = TABLE + number * STRIDE
        record = source.at(va, STRIDE)
        ptr = struct.unpack_from('<I', record, 8)[0]
        raw = source.at(ptr, 256).split(b'\0', 1)[0]
        if digest(record) != row['source_record_sha256'] or digest(raw) != row['source_short_sha256']:
            raise ValueError('Speaker source changed: ' + str(number))
        text = row['en']
        if not text or any(not 32 <= ord(c) < 127 or c in '#@%^|' for c in text):
            raise ValueError('Unsupported speaker text: ' + str(number))
        width = name_width(text, widths)
        # Source x=18, native sloped frame adds margins. Retain ample right edge.
        if width > 540:
            raise ValueError('Speaker requires a larger frame profile; wording retained')
        before = elf.at(va, STRIDE)
        if number == 1:
            # v0.2.0 already redirects all three static player pointers. Keep the
            # +8 default in two-byte Latin for the native name editor; the normal
            # nameplate getter returns mesGetMESVAL(0), not this static pointer.
            if before[12:] != record[12:] or struct.unpack_from('<3I', before) != (0x9B8422, 0x9B8417, 0x9B8417):
                raise ValueError('Unexpected player-name baseline')
            if elf.at(0x9B8417, 11) != 'Ｋａｎｊｉ'.encode('cp932') + b'\0' or text != 'Kanji':
                raise ValueError('Unexpected player default')
            edits.append(dict(id=number, en=text, pointer='runtime mesGetMESVAL(0)', width_px=224,
                              scope='Chosen name retained; worst-case eight fullwidth cells'))
            continue
        if before != record:
            raise ValueError('Unexpected pilot baseline: ' + str(number))
        if text not in strings:
            strings[text] = BASE + len(payload)
            payload.extend(text.encode('ascii') + b'\0')
        pointer = strings[text]
        struct.pack_into('<I', out, elf.offset(va + 8), pointer)
        edits.append(dict(id=number, en=text, pointer=hex(pointer), width_px=width))
    i, segment = next((i, s) for i, s in enumerate(elf.segments) if s[0] == 1 and s[2] == 0x9A0000)
    typ, offset, va, pa, size, memory_size, flags, alignment = segment
    if va + max(size, memory_size) > BASE or BASE + len(payload) > LIMIT:
        raise ValueError('Speaker strings collide with reserved event memory')
    if source.symbol('_evefunc_size')['va'] != LIMIT - va or source.symbol('_evescen_start')['va'] != LIMIT:
        raise ValueError('Unexpected event reservation')
    for other in elf.segments:
        if other[0] == 1 and other[2] != va and max(va, other[2]) < min(BASE + len(payload), other[2] + other[5]):
            raise ValueError('Speaker segment collision')
    combined = out[offset:offset + size] + bytes(BASE - va - size) + payload
    position = (len(out) + 4095) // 4096 * 4096
    out.extend(bytes(position - len(out)))
    out.extend(combined)
    phoff = struct.unpack_from('<I', out, 28)[0]
    phsize = struct.unpack_from('<H', out, 42)[0]
    struct.pack_into('<8I', out, phoff + phsize * i, typ, position, va, pa, len(combined), len(combined), flags, alignment)
    return bytes(out), dict(valid_speaker_slots=859, relocated_slots=858, dynamic_player_slots=1,
                           unique_relocated_strings=len(strings), payload_va=hex(BASE), payload_size=len(payload),
                           language_sha256=LANGUAGE_SHA, records=edits,
                           scope='All short-name fields used by dialogue and other native getter callers. Full/display pilot fields outside this focused patch.')


def inputs():
    import narration_patch
    data, packs, info, fitting = narration_patch.inputs()
    if digest(data) != BASE_SHA:
        raise ValueError('Focused narration baseline changed')
    data, speakers = patch_elf(data, bytes(info['font_widths']))
    return data, packs, info, fitting, speakers


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('version')
    ap.add_argument('--write', action='store_true')
    args = ap.parse_args()
    if not re.fullmatch(r'0\.\d+\.\d+', args.version):
        raise ValueError('Expected 0.x.y')
    data, packs, _, fitting, speakers = inputs()
    dest = ROOT / 'work/output' / ('v' + args.version)
    if dest.exists():
        raise FileExistsError(dest)
    print(json.dumps(dict(version=args.version, based_on='0.2.1',
                         **{k:v for k,v in speakers.items() if k != 'records'},
                         widest=sorted(speakers['records'], key=lambda r:r['width_px'], reverse=True)[:8],
                         sample=[r for r in speakers['records'] if r['id'] in (1,5,6,7,8)],
                         elf_sha256=digest(data)), indent=1))
    if not args.write:
        print('DRY: keep menus, Latin keyboard, opening narration and prior integrated dialogue. No ISO written.')
        return
    from build import make_iso
    import menu_patch
    base = ROOT / 'work/output/v0.2.1'
    info = json.loads((base / 'build_info.json').read_text('utf-8'))
    dest.mkdir(parents=True)
    (dest / 'SLPS_250.70').write_bytes(data)
    for number, blob in packs.items():
        (dest / ('%05d.pack' % number)).write_bytes(blob)
    title = menu_patch.patch_title((ROOT / 'work/source/afs/EVEMAP/00001.bin').read_bytes())
    image = dest / ('Sunrise Eiyuutan 2 EN v' + args.version + '.iso')
    make_iso(image, data, packs, {1:title})
    info.update(version=args.version, based_on='0.2.1', speaker_names=speakers,
                elf_sha256=digest(data), iso_path=str(image), iso_size=image.stat().st_size,
                in_game_validation='pending consolidated speaker checks',
                scope='All859 native dialogue speaker slots, existing English menus/name entry/opening narration and previous integrated dialogue. Later dialogue proposals remain separate.')
    (dest / 'build_info.json').write_text(json.dumps(info, indent=1) + '\n', 'utf-8')
    print('WRITE:', image)


if __name__ == '__main__':
    main()
