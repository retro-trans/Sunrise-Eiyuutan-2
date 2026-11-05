"""Integrate the complete reviewed opening narration on the playable menu build.

Default is a dry run. Source voices, function calls, row boundaries and blank
calls remain intact. English bodies are reflowed without shortening wording.
"""
import argparse
import hashlib
import json
import struct
from elf import ROOT, Elf
from build import replace_pack, make_iso
from extract import pack_members
from textcodec import decode, encode, controls, parse_table, build_table
from message_pages import pages
from story_layout import pieces, measure, wrap_body
import menu_patch

TABLE = '04904_10382'
SOURCE_TABLE_SHA = '68d63728558574c236cdf3433fa124e1891b935aa17fa220e4a6f7f762f6324c'
SOURCE_PACK_SHA = '99676fbae4dacf931ca1d9dde9de18862e4c084f73b7bd7122b38ea3175e1b6d'
ENGLISH_SHA = 'ca4e61f9c479db0a74b30cfe32413a67add7a9d884835405e99c601d4dba237c'
BASE_ELF_SHA = '177b6e3f86efba6f7e2220961ea7e77aa56450b1d50aa397ddc94b6f1574cebb'
digest = lambda b: hashlib.sha256(b).hexdigest()


def stage_row(text, widths):
    raw = encode(text)
    before = pages(raw)
    result = bytearray()
    fitting = []
    for i, page in enumerate(before):
        if not page['flags'] & 1:
            result.extend(raw[page['start']:page['end']])
            continue
        prefix, body, tail = pieces(raw, page)
        lines = body.split('\n')
        # Keep the approved explicit lines, including row7's fullwidth blank,
        # whenever they fit. Reflow only an overlong body within its own call.
        if len(lines) > 3 or max(measure(s, widths) for s in lines) > 504 or measure(lines[-1], widths) > 478:
            body = wrap_body(' '.join(lines), widths)
            lines = body.split('\n')
        if len(lines) > 3 or len(encode(body)) >= 400:
            raise ValueError('Narration needs a larger display profile; wording retained')
        assert max(measure(s, widths) for s in lines) <= 504
        assert measure(lines[-1], widths) <= 478
        result.extend(prefix + encode(body) + tail)
        fitting.append(dict(native_call=i, lines=lines, widths=[measure(s, widths) for s in lines], voice=page['voice']))
    result.extend(b'\0')
    staged = decode(bytes(result))
    after = pages(bytes(result))
    assert len(after) == len(before) and controls(staged) == controls(text)
    for old, new in zip(before, after):
        assert {k:v for k,v in old.items() if k not in ('start', 'end', 'body')} == {k:v for k,v in new.items() if k not in ('start', 'end', 'body')}
        if old['flags'] & 1:
            assert old['body'].split() == new['body'].split()
    return staged, fitting


def translated_pack(widths):
    source = (ROOT / 'work/source/afs/RESOURCE/04904.bin').read_bytes()
    assert digest(source) == SOURCE_PACK_SHA
    member = next(m for m in pack_members(source) if m['id'] == 10382)
    raw = source[member['offset']:member['offset'] + member['size']]
    assert digest(raw) == SOURCE_TABLE_SHA
    rows = parse_table(raw)
    english = ROOT / 'work/translation/en/dat' / (TABLE + '.en.json')
    assert digest(english.read_bytes()) == ENGLISH_SHA
    document = json.loads(english.read_text('utf-8'))
    assert len(rows) == len(document['rows']) == 11
    fitting = []
    for i, proposal in enumerate(document['rows']):
        assert proposal['id'] == i and digest(rows[i]) == proposal['source_sha256']
        assert proposal['review']['accuracy'] == 'independent-reviewed'
        assert controls(decode(rows[i])) == controls(proposal['en'])
        staged, layout = stage_row(proposal['en'], widths)
        assert len(pages(rows[i])) == len(pages(encode(staged)))
        rows[i] = encode(staged)
        fitting.append(dict(id=i, native_layout=layout))
    rebuilt = build_table(rows)
    assert parse_table(rebuilt) == rows
    return replace_pack(source, {10382:rebuilt}), fitting


def inputs():
    base = ROOT / 'work/output/v0.2.0'
    info = json.loads((base / 'build_info.json').read_text('utf-8'))
    data = (base / 'SLPS_250.70').read_bytes()
    assert digest(data) == BASE_ELF_SHA
    pack, fitting = translated_pack(bytes(info['font_widths']))
    out = bytearray(data)
    elf = Elf(data)
    size_va = elf.symbol('_pacfileA')['va'] + 4904 * 8 + 4
    assert int.from_bytes(elf.at(size_va, 4), 'little') == (ROOT / 'work/source/afs/RESOURCE/04904.bin').stat().st_size
    struct.pack_into('<I', out, elf.offset(size_va), len(pack))
    packs = {int(p.stem):p.read_bytes() for p in (ROOT / 'work/output/v0.1.139').glob('*.pack')}
    packs[4904] = pack
    return bytes(out), packs, info, fitting


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('version')
    ap.add_argument('--write', action='store_true')
    a = ap.parse_args()
    import re
    if not re.fullmatch(r'0\.\d+\.\d+', a.version):
        raise ValueError('Expected 0.x.y')
    data, packs, info, fitting = inputs()
    dest = ROOT / 'work/output' / ('v' + a.version)
    if dest.exists():
        raise FileExistsError(dest)
    print(json.dumps(dict(version=a.version, narration_rows=11, native_layout=fitting, pack_size=len(packs[4904]), elf_sha256=digest(data)), indent=1))
    if not a.write:
        print('DRY: retain menu/name patch and previous integrated dialogue; add all11 narration entries. No ISO written.')
        return
    dest.mkdir(parents=True)
    (dest / 'SLPS_250.70').write_bytes(data)
    for number, blob in packs.items():
        (dest / ('%05d.pack' % number)).write_bytes(blob)
    title = menu_patch.patch_title((ROOT / 'work/source/afs/EVEMAP/00001.bin').read_bytes())
    image = dest / ('Sunrise Eiyuutan 2 EN v' + a.version + '.iso')
    make_iso(image, data, packs, {1:title})
    info.update(version=a.version, based_on='0.2.0', narration_integration=dict(table=TABLE, rows=11, English_sha256=ENGLISH_SHA, fitting=fitting),
                elf_sha256=digest(data), iso_path=str(image), iso_size=image.stat().st_size,
                in_game_validation='pending focused narration sequence check', scope='All11 opening narration entries plus existing0.2.0 menu/name UI; later dialogue proposals remain separate.')
    info['translated_rows'] = info['translated_rows'] + [TABLE + ':' + str(i) for i in range(11)]
    (dest / 'build_info.json').write_text(json.dumps(info, indent=1) + '\n', 'utf-8')
    print('WRITE:', image)


if __name__ == '__main__':
    main()
