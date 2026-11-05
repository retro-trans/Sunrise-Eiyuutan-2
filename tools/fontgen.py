"""Render proportional ASCII glyphs in the game's 4bpp outlined style.

Pixel values index the text palette ramp: 0 transparent, 1-4 outline colour,
5-14 blends from outline to fill, 15 fill colour. Glyphs are left-aligned in the
cell; the advance is the ink width (outline included).

Source font: Noto Sans JP (SIL Open Font License), variable weight.

usage: py -3.11 tools/fontgen.py preview   -> work/ui/vwf_preview.png
"""
import os, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_PATH = r'C:\Windows\Fonts\NotoSansJP-VF.ttf'

# per cell size: (pixel size, baseline row, weight, letter gap)
STYLE = {
    26: dict(size=19, baseline=20, weight=700, gap=0),
    22: dict(size=16, baseline=17, weight=700, gap=0),
}


def _font(size, weight):
    f = ImageFont.truetype(FONT_PATH, size)
    try:
        f.set_variation_by_axes([weight])
    except Exception:
        pass
    return f


def render_glyph(ch, n, style=None):
    """Return (list of n*n values, advance)."""
    st = style or STYLE[n]
    f = _font(st['size'], st['weight'])
    S = 4  # supersample
    big = _font(st['size'] * S, st['weight'])
    W = n * 2
    img = Image.new('L', (W * S, n * S), 0)
    d = ImageDraw.Draw(img)
    # baseline at st['baseline']; PIL anchor 'ls' = left, baseline
    d.text((2 * S, st['baseline'] * S), ch, font=big, fill=255, anchor='ls')
    fill = img.resize((W, n), Image.LANCZOS)
    # outline: dilate the hard (binarised) fill by 1 px in 8 directions
    hard = fill.point(lambda v: 255 if v >= 80 else 0)
    outline = hard.filter(ImageFilter.MaxFilter(3))
    fp = fill.load(); op = outline.load()
    vals = [[0] * W for _ in range(n)]
    for y in range(n):
        for x in range(W):
            fv = fp[x, y] / 255.0
            if fv >= 0.12:
                vals[y][x] = max(5, min(15, int(round(4 + fv * 11))))
            elif op[x, y]:
                vals[y][x] = 4
    cols = [x for x in range(W) if any(vals[y][x] for y in range(n))]
    if not cols:
        return [0] * (n * n), None
    left, right = cols[0], cols[-1]
    width = right - left + 1
    out = [0] * (n * n)
    for y in range(n):
        for x in range(left, min(right + 1, left + n)):
            out[y * n + (x - left)] = vals[y][x]
    return out, width + st['gap']


def pack4(vals):
    b = bytearray(len(vals) // 2)
    for k, v in enumerate(vals):
        if k % 2 == 0:
            b[k // 2] |= v
        else:
            b[k // 2] |= v << 4
    return bytes(b)


def build_ascii(n):
    """{code: (packed glyph bytes, advance)} for 0x21..0x7E"""
    out = {}
    for c in range(0x21, 0x7F):
        vals, w = render_glyph(chr(c), n)
        out[c] = (pack4(vals), w or 1)
    return out


PAL = [(0, 0, 0, 0)] + [(8, 8, 8, 255)] * 4 + [(48, 48, 48, 255)] * 4 + [(99, 99, 99, 255)] * 3 + \
      [(148, 148, 148, 255)] * 2 + [(205, 205, 205, 255), (255, 255, 255, 255)]


def preview(lines, n=26, space=6, out=None, scale=2):
    g = build_ascii(n)
    W = 470
    img = Image.new('RGBA', (W, n * len(lines) + 8), (70, 60, 70, 255))
    px = img.load()
    for li, line in enumerate(lines):
        x = 4
        for ch in line:
            c = ord(ch)
            if c == 0x20:
                x += space; continue
            data, w = g[c]
            for k in range(n * n):
                b = data[k // 2]
                v = (b & 15) if k % 2 == 0 else (b >> 4)
                if v:
                    xx, yy = x + k % n, 4 + li * n + k // n
                    if xx < W:
                        px[xx, yy] = PAL[v]
            x += w
        print('%3d px  %s' % (x - 4, line))
    img = img.resize((img.width * scale, img.height * scale), Image.NEAREST)
    img.save(out or os.path.join(ROOT, 'work', 'ui', 'vwf_preview.png'))


if __name__ == '__main__':
    preview(["Professor Rond's an old friend of my dad's.",
             "He treats Rie and me like family. Quick, jumpy",
             "WAVE 1234567890 (illicit) \"Yes?\" - Kanji, Kyo!"])
