"""Clear ship command sprites and translated ship stats; dry run by default.

Layer on the complete focused speaker build. Retain native button geometry,
CLUTs, selection artwork, printf arguments, colours and stat window geometry.
"""
import argparse
import hashlib
import json
import re
import struct
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from elf import ROOT, PATH, Elf
from extract import pack_members
from build import replace_pack, make_iso
import fontgen
import speaker_patch

BASE = 0x9BA000
FORMAT = 0x2226B8
LANGUAGE = ROOT / 'work/translation/en/battle-ui.en.json'
LANGUAGE_SHA = '993074af9ba504b313d820270df645d71f8683ceaecad6f74d8b0155ce59c8e8'
SOURCE_FORMAT_SHA = '529d475c38666340b5fd81e3749fa700786e84202bd5ffb9cbc0687b9adfbe2e'
BASE_SHA = '1376defbcd2debc34c751d0392602db56a9779da6cda21539d657f4df3e420c2'
digest = lambda b: hashlib.sha256(b).hexdigest()


def language():
    if digest(LANGUAGE.read_bytes()) != LANGUAGE_SHA:
        raise ValueError('Battle UI wording revision requires review')
    obj = json.loads(LANGUAGE.read_text('utf-8'))
    if obj['review'] != {'accuracy':'independent-reviewed', 'editorial':'complete', 'glossary':'complete', 'proofreading':'complete'}:
        raise ValueError('Battle UI language review incomplete')
    if [r['member'] for r in obj['buttons']] != list(range(10059, 10066)):
        raise ValueError('Unexpected command inventory')
    return obj


def signature(text):
    return (re.findall(r'%%[012]|%3d|%03d|%s', text), text.count('\n'), text.count('％'), text.count('　'))


def patch_elf(data):
    source = Elf(PATH.read_bytes())
    elf = Elf(data)
    old = source.at(FORMAT, 136)
    if old[-1] or digest(old[:-1]) != SOURCE_FORMAT_SHA or elf.at(FORMAT, 136) != old:
        raise ValueError('Unexpected source stat format')
    text = language()['status']['en']
    if signature(text) != signature(old[:-1].decode('cp932')):
        raise ValueError('Stat printf/control signature changed')
    payload = text.encode('cp932') + b'\0'
    out = bytearray(data)
    for va, expected, value in [(0x1497B8, 0x3C050022, 0x3C050000 | ((BASE + 0x8000) >> 16)),
                                (0x1497C0, 0x24A526B8, 0x24A50000 | (BASE & 0xFFFF))]:
        if elf.at(va, 4) != struct.pack('<I', expected):
            raise ValueError('Stat reference changed')
        struct.pack_into('<I', out, elf.offset(va), value)
    i, segment = next((i, s) for i, s in enumerate(elf.segments) if s[0] == 1 and s[2] == 0x9A0000)
    typ, off, va, pa, size, mem, flags, alignment = segment
    if va + max(size, mem) > BASE or BASE + len(payload) > 0x9C0000:
        raise ValueError('Battle text memory collision')
    combined = data[off:off+size] + bytes(BASE-va-size) + payload
    position = (len(out)+4095)//4096*4096
    out.extend(bytes(position-len(out)))
    out.extend(combined)
    phoff = struct.unpack_from('<I', out, 28)[0]
    phsize = struct.unpack_from('<H', out, 42)[0]
    struct.pack_into('<8I', out, phoff+i*phsize, typ, position, va, pa, len(combined), len(combined), flags, alignment)
    return bytes(out)


def button(blob, text):
    # These assets contain a single 128x16 linear 4bpp plane; all CEL/native
    # origins and the side bevels stay byte-exact. Only orange text is erased.
    if len(blob) != 1440 or blob[:4] != b'PAL_' or blob[192:196] != b'TEX_' or blob[1344:1348] != b'CEL_':
        raise ValueError('Unexpected button chunks')
    if struct.unpack_from('<HHI', blob, 192+80) != (20,128,16):
        raise ValueError('Unexpected command texture layout')
    pal = [tuple(blob[128+4*i:132+4*i]) for i in range(16)]
    if pal[5] != (246,147,29,128) or pal[7] != (255,255,255,128):
        raise ValueError('Unexpected button palette')
    pixels = [v for b in blob[320:1344] for v in (b&15,b>>4)]
    if set(pixels)-set(range(8)):
        raise ValueError('Unexpected button palette indices')
    for i, v in enumerate(pixels):
        if v == 5:
            if not 24 <= i%128 <= 111:
                raise ValueError('Text overlaps protected button frame')
            pixels[i] = 0
    # Same freely licensed Noto Sans family as the proportional game font.
    scale = 4
    if digest(Path(fontgen.FONT_PATH).read_bytes()) != '5113756f8a3b5d01b2211025e267c50121e3b36f465b7bbaf3cdaf4c3430bfd0':
        raise ValueError('Reviewed menu typeface revision changed')
    f = fontgen._font(15*scale, 700)
    mask = Image.new('L',(128*scale,16*scale))
    draw = ImageDraw.Draw(mask)
    box = draw.textbbox((0,0),text,font=f)
    w,h = box[2]-box[0],box[3]-box[1]
    if w > 82*scale or h > 16*scale:
        raise ValueError('Button label needs a larger geometry; wording retained')
    draw.text(((128*scale-w)//2-box[0],(16*scale-h)//2-box[1]),text,font=f,fill=255)
    mask = mask.resize((128,16),Image.Resampling.LANCZOS)
    ramp = [0,1,2,3,6,7]
    for y in range(16):
        for x in range(24,110):
            value = mask.getpixel((x,y))
            if value >= 12:
                pixels[y*128+x] = min(ramp,key=lambda j:abs(pal[j][0]-value))
    out = bytearray(blob)
    out[320:1344] = fontgen.pack4(pixels)
    # Every non-pixel byte including palette and CEL is untouched.
    assert out[:320] == blob[:320] and out[1344:] == blob[1344:]
    preview = Image.frombytes('RGB',(128,16),bytes(c for p in pixels for c in pal[p][:3]))
    return bytes(out), preview


def patch_pack(pack):
    source = (ROOT/'work/source/afs/RESOURCE/00022.bin').read_bytes()
    src = {m['id']:source[m['offset']:m['offset']+m['size']] for m in pack_members(source)}
    current = {m['id']:pack[m['offset']:m['offset']+m['size']] for m in pack_members(pack)}
    replacements, previews = {}, []
    for row in language()['buttons']:
        number = row['member']
        if current[number] != src[number]:
            raise ValueError('Command source already modified')
        replacements[number], im = button(src[number], row['en'])
        previews.append(im)
    result = replace_pack(pack, replacements)
    if len(result) != len(pack):
        raise ValueError('Unexpected same-size command pack resize')
    return result, previews


def inputs():
    data, packs, info, fitting, speakers = speaker_patch.inputs()
    if digest(data) != BASE_SHA:
        raise ValueError('Speaker baseline changed')
    return patch(data,packs)


def patch(data,packs):
    data = patch_elf(data)
    if 22 not in packs:
        packs[22]=(ROOT/'work/source/afs/RESOURCE/00022.bin').read_bytes()
    packs[22], previews = patch_pack(packs[22])
    return data, packs, dict(language_sha256=digest(LANGUAGE.read_bytes()), status_va=hex(BASE),
        status_format=language()['status']['en'], command_members=list(range(10059,10066)),
        font='Noto Sans JP, weight700,15px; white with antialiased grayscale edges',
        protected='Native command frames, selection graphics, CEL geometry and palettes unchanged'), previews


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('version')
    ap.add_argument('--write',action='store_true')
    ap.add_argument('--preview',type=Path)
    a = ap.parse_args()
    if not re.fullmatch(r'0\.\d+\.\d+', a.version):
        raise ValueError('Expected0.x.y')
    data,packs,report,previews = inputs()
    print(json.dumps(dict(version=a.version, **report, elf_sha256=digest(data)),indent=1))
    if a.preview:
        im = Image.new('RGB',(128,16*7),(0,0,0))
        for i,p in enumerate(previews):im.paste(p,(0,16*i))
        im.resize((512,448),Image.Resampling.NEAREST).save(a.preview)
    if not a.write:
        print('DRY: no game data/ISO written.')
        return
    dest=ROOT/'work/output'/('v'+a.version)
    if dest.exists():raise FileExistsError(dest)
    dest.mkdir(parents=True)
    (dest/'SLPS_250.70').write_bytes(data)
    for n,b in packs.items():(dest/('%05d.pack'%n)).write_bytes(b)
    import menu_patch
    title=menu_patch.patch_title((ROOT/'work/source/afs/EVEMAP/00001.bin').read_bytes())
    image=dest/('Sunrise Eiyuutan 2 EN v'+a.version+'.iso')
    make_iso(image,data,packs,{1:title})
    info=json.loads((ROOT/'work/output/v0.2.2/build_info.json').read_text('utf-8'))
    info.update(version=a.version,based_on='0.2.2',battle_ui=report,elf_sha256=digest(data),iso_path=str(image),iso_size=image.stat().st_size,
        in_game_validation='pending consolidated battle UI checks',scope='Ship status panel and seven ship command sprites, retaining complete0.2.2 focus content. Other untranslated UI remains outside this patch.')
    (dest/'build_info.json').write_text(json.dumps(info,indent=1)+'\n','utf-8')
    print('WRITE:',image)


if __name__=='__main__':main()
