#!/usr/bin/env python3
"""Write app/glyphbook.js from Noto CJK faces.

Cell 16, 4-bit, faces sans, sans-bold, serif. Alphabet is GB2312 level 1
(bytes B0A1 through D7F9) plus ASCII 33 through 126. Noto Sans CJK and
Noto Serif CJK are SIL Open Font License faces. This script does not ship
the font files.
"""
import base64
import os
import struct
import sys

from fontTools.ttLib import TTCollection
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'app', 'glyphbook.js')
FONT_DIR = '/usr/share/fonts/opentype/noto'
FACES = (
    ('sans', os.path.join(FONT_DIR, 'NotoSansCJK-Regular.ttc'), 'Noto Sans CJK SC'),
    ('sans-bold', os.path.join(FONT_DIR, 'NotoSansCJK-Bold.ttc'), 'Noto Sans CJK SC'),
    ('serif', os.path.join(FONT_DIR, 'NotoSerifCJK-Regular.ttc'), 'Noto Serif CJK SC'),
)
RENDER = 96
B64_ALPHABET = set('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=')


def face_index(path, family):
    ttc = TTCollection(path)
    for i, font in enumerate(ttc.fonts):
        names = []
        for rec in font['name'].names:
            if rec.nameID not in (1, 16):
                continue
            try:
                names.append(rec.toUnicode())
            except Exception:
                continue
        if family in names:
            return i
    raise SystemExit('missing face %s in %s' % (family, path))


def alphabet():
    chars = []
    for b1 in range(0xB0, 0xD8):
        last = 0xF9 if b1 == 0xD7 else 0xFE
        for b2 in range(0xA1, last + 1):
            chars.append(bytes((b1, b2)).decode('gb2312'))
    for code in range(33, 127):
        chars.append(chr(code))
    return chars


def tight_bits(font, ch):
    box = font.getbbox(ch)
    if not box:
        return None
    w = max(1, box[2] - box[0] + 4)
    h = max(1, box[3] - box[1] + 4)
    im = Image.new('L', (w, h), 255)
    ImageDraw.Draw(im).text((2 - box[0], 2 - box[1]), ch, font=font, fill=0)
    raw = im.tobytes()
    x0, y0, x1, y1 = w, h, -1, -1
    bits = bytearray(w * h)
    for i, v in enumerate(raw):
        if v >= 160:
            continue
        bits[i] = 1
        x, y = i % w, i // w
        if x < x0:
            x0 = x
        if y < y0:
            y0 = y
        if x > x1:
            x1 = x
        if y > y1:
            y1 = y
    if x1 < x0:
        return None
    tw, th = x1 - x0 + 1, y1 - y0 + 1
    crop = bytearray(tw * th)
    for y in range(th):
        src = (y0 + y) * w + x0
        crop[y * tw:(y + 1) * tw] = bits[src:src + tw]
    return crop, tw, th


def prefix(bits, w, h):
    stride = w + 1
    pref = [0] * (stride * (h + 1))
    for y in range(h):
        row = 0
        base = y * w
        for x in range(w):
            row += bits[base + x]
            pref[(y + 1) * stride + (x + 1)] = pref[y * stride + (x + 1)] + row
    return pref


def rect_sum(pref, w, x0, y0, x1, y1):
    stride = w + 1
    return pref[y1 * stride + x1] - pref[y0 * stride + x1] - pref[y1 * stride + x0] + pref[y0 * stride + x0]


def js_floor(v):
    iv = int(v)
    if v < 0 and v != iv:
        return iv - 1
    return iv


def js_ceil(v):
    iv = int(v)
    if v > 0 and v != iv:
        return iv + 1
    return iv


def pack_grid(bits, bw, bh):
    side = bw if bw > bh else bh
    ox = (side - bw) / 2.0
    oy = (side - bh) / 2.0
    pref = prefix(bits, bw, bh)
    grid = [0] * 256
    for gy in range(16):
        ya = js_floor(-oy + (gy / 16.0) * side)
        yb = js_ceil(-oy + ((gy + 1) / 16.0) * side)
        for gx in range(16):
            xa = js_floor(-ox + (gx / 16.0) * side)
            xb = js_ceil(-ox + ((gx + 1) / 16.0) * side)
            tot = (xb - xa) * (yb - ya)
            if tot <= 0:
                continue
            ix0 = xa if xa > 0 else 0
            iy0 = ya if ya > 0 else 0
            ix1 = xb if xb < bw else bw
            iy1 = yb if yb < bh else bh
            ink = rect_sum(pref, bw, ix0, iy0, ix1, iy1) if ix0 < ix1 and iy0 < iy1 else 0
            nibble = int(ink / tot * 15 + 0.5)
            if nibble > 15:
                nibble = 15
            grid[gy * 16 + gx] = nibble
    out = bytearray(128)
    for i, v in enumerate(grid):
        if i & 1:
            out[i >> 1] |= v & 15
        else:
            out[i >> 1] = (v & 15) << 4
    return out


def main():
    chars = alphabet()
    if len(chars) != 3755 + 94:
        raise SystemExit('alphabet %d' % len(chars))
    blob = bytearray()
    blob += b'JWGB1'
    blob += struct.pack('<HHHH', 1, 16, len(FACES), len(chars))
    for name, _path, _family in FACES:
        blob += name.encode('ascii') + b'\0'
    for ch in chars:
        blob += struct.pack('<H', ord(ch))
    grids = []
    for name, path, family in FACES:
        idx = face_index(path, family)
        font = ImageFont.truetype(path, RENDER, index=idx)
        face_grids = bytearray()
        for i, ch in enumerate(chars):
            got = tight_bits(font, ch)
            if not got:
                face_grids += bytes(128)
            else:
                bits, bw, bh = got
                face_grids += pack_grid(bits, bw, bh)
            if i and i % 800 == 0:
                print(name, i, file=sys.stderr)
        grids.append(face_grids)
        print(name, 'index', idx, file=sys.stderr)
    for face in grids:
        blob += face
    text = base64.b64encode(blob).decode('ascii')
    if set(text) - B64_ALPHABET:
        raise SystemExit('base64 alphabet')
    credit = (
        '/* Noto Sans CJK SC and Noto Serif CJK SC densities. '
        'Those faces are SIL Open Font License. */\n'
    )
    js = credit + 'window.__imgBook = "' + text + '";\n'
    with open(OUT, 'w', encoding='ascii', newline='\n') as f:
        f.write(js)
    print(len(chars), 'chars', len(blob), 'bytes', os.path.getsize(OUT), 'js')


if __name__ == '__main__':
    main()
