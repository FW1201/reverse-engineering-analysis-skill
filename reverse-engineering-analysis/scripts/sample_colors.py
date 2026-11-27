#!/usr/bin/env python3
"""Measure colors in a screenshot (PNG) — for DESIGN.md, especially native apps with no DOM.

Usage:
    python3 scripts/sample_colors.py <png> [--top 12]            dominant colors with share of pixels
    python3 scripts/sample_colors.py <png> --at 120,48 300,200   exact color at x,y points
    python3 scripts/sample_colors.py <png> --contrast "#1F2937" "#FFFFFF"   WCAG contrast ratio

Standard library only (zlib PNG decoder: 8-bit, non-interlaced, RGB/RGBA/gray). Screenshots
from chrome-devtools, macOS screencapture and computer-use tools all qualify.
Colors are quantized to --bits (default 5) per channel buckets for the palette, then reported as the
average real color of each bucket, so antialiasing noise does not explode the list.
"""
import argparse
import collections
import struct
import sys
import zlib


def read_png(path):
    data = open(path, "rb").read()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise SystemExit("not a PNG file")
    pos, idat, w = 8, b"", None
    while pos < len(data):
        ln, typ = struct.unpack(">I4s", data[pos:pos + 8])
        chunk = data[pos + 8:pos + 8 + ln]
        if typ == b"IHDR":
            w, h, depth, ctype, _, _, inter = struct.unpack(">IIBBBBB", chunk)
            if depth != 8 or inter != 0 or ctype not in (0, 2, 4, 6):
                raise SystemExit(f"unsupported PNG (depth {depth}, color type {ctype}, interlace {inter})")
        elif typ == b"IDAT":
            idat += chunk
        elif typ == b"IEND":
            break
        pos += 12 + ln
    bpp = {0: 1, 2: 3, 4: 2, 6: 4}[ctype]
    raw = zlib.decompress(idat)
    stride = w * bpp
    rows, prev, i = [], bytearray(stride), 0
    for _ in range(h):
        f = raw[i]; line = bytearray(raw[i + 1:i + 1 + stride]); i += 1 + stride
        for x in range(stride):
            a = line[x - bpp] if x >= bpp else 0
            b = prev[x]
            c = prev[x - bpp] if x >= bpp else 0
            if f == 1: line[x] = (line[x] + a) & 255
            elif f == 2: line[x] = (line[x] + b) & 255
            elif f == 3: line[x] = (line[x] + ((a + b) >> 1)) & 255
            elif f == 4:
                p = a + b - c; pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                line[x] = (line[x] + (a if pa <= pb and pa <= pc else b if pb <= pc else c)) & 255
        rows.append(line); prev = line

    def px(x, y):
        r = rows[y]; o = x * bpp
        if ctype in (0, 4):
            return (r[o], r[o], r[o])
        return (r[o], r[o + 1], r[o + 2])
    return w, h, px


def hexc(c):
    return "#%02X%02X%02X" % c


def lum(c):
    def ch(v):
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (ch(v) for v in c)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def parse_hex(s):
    s = s.lstrip("#")
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("png", nargs="?")
    ap.add_argument("--top", type=int, default=12)
    ap.add_argument("--bits", type=int, default=5, choices=range(2, 9), help="bits per channel for palette buckets")
    ap.add_argument("--at", nargs="*", default=[])
    ap.add_argument("--contrast", nargs=2, metavar=("FG", "BG"))
    a = ap.parse_args()

    if a.contrast:
        fg, bg = parse_hex(a.contrast[0]), parse_hex(a.contrast[1])
        r = contrast(fg, bg)
        print(f"{a.contrast[0]} on {a.contrast[1]}: {r:.2f}:1  "
              f"AA-text {'pass' if r >= 4.5 else 'fail'}  AA-large {'pass' if r >= 3 else 'fail'}")
        if not a.png:
            return 0
    if not a.png:
        ap.error("png path required")

    w, h, px = read_png(a.png)
    if a.at:
        for pt in a.at:
            x, y = (int(v) for v in pt.split(","))
            print(f"{x},{y}: {hexc(px(min(x, w - 1), min(y, h - 1)))}")
        return 0

    step = max(1, int((w * h / 400_000) ** 0.5))  # sample ~400k px max
    buckets, sums, total = collections.Counter(), {}, 0
    for y in range(0, h, step):
        for x in range(0, w, step):
            c = px(x, y)
            sh = 8 - a.bits
            k = (c[0] >> sh, c[1] >> sh, c[2] >> sh)
            buckets[k] += 1
            s = sums.setdefault(k, [0, 0, 0]); s[0] += c[0]; s[1] += c[1]; s[2] += c[2]
            total += 1
    print(f"{a.png}: {w}x{h}, sampled every {step}px")
    print("share   color    luminance")
    for k, n in buckets.most_common(a.top):
        s = sums[k]; c = (s[0] // n, s[1] // n, s[2] // n)
        print(f"{100 * n / total:5.1f}%  {hexc(c)}  {lum(c):.3f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
