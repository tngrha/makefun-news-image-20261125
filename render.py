#!/usr/bin/env python3
"""The World on One Page — Wednesday 25 November 2026 (full-day edition).

Draws a 1024x1024 serif broadsheet of the day's verified news with PIL.
No network, no randomness, no timestamps: two runs write identical bytes.

Layout (1024 x 1024, margin 14):
  masthead -> 20-field strip -> 3 heroes -> 12 picture panels ->
  38 briefs in 3 columns -> schematic world map (15 pins) + numbers ->
  UTC timeline -> DATE CHECK + footer.
"""
import os
import textwrap

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
M = 14  # margin

PAPER = (247, 242, 231)
INK = (26, 26, 26)
RED = (139, 26, 26)
NAVY = (31, 58, 95)
GOLD = (150, 105, 20)
GREY = (90, 86, 78)
LIGHT = (232, 226, 212)
SKY = (176, 205, 224)
SEA = (64, 110, 150)
DARKSEA = (38, 74, 110)

SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SERIF_B = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SERIF_I = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"

_cache = {}


def F(size, bold=False, italic=False):
    key = (size, bold, italic)
    if key not in _cache:
        path = SERIF_B if bold else (SERIF_I if italic else SERIF)
        _cache[key] = ImageFont.truetype(path, size)
    return _cache[key]


def wrap(text, font, width):
    """Greedy word wrap to a pixel width; returns list of lines."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if font.getlength(trial) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(d, x, y, text, font, width, fill=INK, leading=None, max_lines=None):
    """Draw wrapped text; returns (lines_used, bottom_y). Warns on overflow."""
    lh = leading or int(font.size * 1.18)
    lines = wrap(text, font, width)
    if max_lines is not None and len(lines) > max_lines:
        lines = lines[:max_lines]
        print("OVERFLOW-WARN: %r truncated to %d lines" % (text[:40], max_lines))
    for i, ln in enumerate(lines):
        d.text((x, y + i * lh), ln, font=font, fill=fill)
    return len(lines), y + len(lines) * lh


def rule(d, x0, x1, y, fill=INK, width=1):
    d.line([(x0, y), (x1, y)], fill=fill, width=width)


def kicker(d, x, y, text, fill=RED):
    d.text((x, y), text, font=F(10, bold=True), fill=fill)
    return y + 13


# ---------------------------------------------------------------- scenes
def _flame(d, cx, cy, s):
    """A small flame: layered orange/yellow teardrops."""
    d.polygon([(cx - s, cy), (cx, cy - 2 * s), (cx + s, cy)], fill=(230, 120, 20))
    d.polygon([(cx - s * 0.55, cy), (cx, cy - 1.3 * s), (cx + s * 0.55, cy)],
              fill=(250, 200, 60))


def _smoke(d, cx, cy, s, col=(120, 118, 110)):
    for i, r in enumerate((s, s * 0.75, s * 0.55)):
        d.ellipse([cx - r + i * 2, cy - i * s * 0.9 - r, cx + r + i * 2,
                   cy - i * s * 0.9 + r], fill=col)


def _ship(d, x, y, w, h, hull=(40, 44, 52)):
    d.rectangle([x, y, x + w, y + h], fill=hull)
    d.rectangle([x + w * 0.15, y - h * 0.9, x + w * 0.3, y], fill=(200, 60, 40))
    d.rectangle([x + w * 0.6, y - h * 0.7, x + w * 0.75, y], fill=(230, 230, 220))
    for i in range(3):
        d.rectangle([x + w * (0.35 + i * 0.15), y + h * 0.25,
                     x + w * (0.45 + i * 0.15), y + h * 0.7], fill=(120, 130, 140))


def _scene_draw(d, box, kind):
    """Draw a small detailed scene inside box (x0, y0, x1, y1)."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    d.rectangle(box, outline=(120, 110, 95), width=1)
    if kind == "tankers":
        d.rectangle([x0, y0, x1, y0 + h * 0.55], fill=(226, 196, 150))  # dusk sky
        d.ellipse([x1 - w * 0.22, y0 + 4, x1 - w * 0.05, y0 + h * 0.22], fill=(240, 180, 90))
        d.rectangle([x0, y0 + h * 0.55, x1, y1], fill=SEA)
        for i in range(3):
            d.line([(x0, y0 + h * (0.62 + i * 0.12)), (x1, y0 + h * (0.62 + i * 0.12))],
                   fill=(140, 180, 205), width=1)
        _ship(d, x0 + w * 0.06, y0 + h * 0.52, w * 0.34, h * 0.13)
        _ship(d, x0 + w * 0.58, y0 + h * 0.58, w * 0.34, h * 0.13)
        _flame(d, x0 + w * 0.22, y0 + h * 0.52, 7)
        _flame(d, x0 + w * 0.75, y0 + h * 0.58, 6)
        _smoke(d, x0 + w * 0.22, y0 + h * 0.45, 5)
        _smoke(d, x0 + w * 0.75, y0 + h * 0.50, 5)
        d.ellipse([x0 + w * 0.42, y0 + h * 0.68, x0 + w * 0.46, y0 + h * 0.72], fill=(30, 30, 30))
        d.ellipse([x0 + w * 0.50, y0 + h * 0.75, x0 + w * 0.53, y0 + h * 0.78], fill=(30, 30, 30))
        d.text((x0 + 4, y1 - 13), "STRAIT OF HORMUZ", font=F(9, bold=True), fill=(255, 255, 255))
    elif kind == "market":
        d.rectangle(box, fill=(24, 32, 48))
        d.line([(x0 + 8, y0 + h - 14), (x1 - 6, y0 + h - 14)], fill=(200, 200, 200), width=1)
        d.line([(x0 + 8, y0 + 6), (x0 + 8, y0 + h - 14)], fill=(200, 200, 200), width=1)
        pts = [(0.05, 0.30), (0.18, 0.38), (0.30, 0.55), (0.42, 0.78),
               (0.55, 0.88), (0.68, 0.72), (0.82, 0.55), (0.95, 0.42)]
        xy = [(x0 + w * px, y0 + h * py) for px, py in pts]
        d.line(xy, fill=(220, 60, 50), width=3)
        d.line([(xy[4][0], xy[4][1]), (xy[-1][0], xy[-1][1])], fill=(80, 200, 120), width=3)
        for i in range(6):
            bx = x0 + w * (0.08 + i * 0.14)
            d.rectangle([bx, y0 + h * 0.80, bx + 8, y0 + h - 16],
                        fill=(90, 110, 140) if i < 4 else (80, 180, 120))
        d.text((x0 + 6, y0 + 4), "DOW -1,100 pts, THEN +164", font=F(9, bold=True),
               fill=(255, 220, 120))
        d.text((x0 + 6, y1 - 14), "50,183  +0.33%", font=F(10, bold=True), fill=(140, 230, 160))
    elif kind == "space":
        d.rectangle(box, fill=(12, 16, 34))
        for sx, sy, sr in [(0.12, 0.2, 1), (0.3, 0.12, 2), (0.5, 0.3, 1), (0.7, 0.15, 2),
                           (0.85, 0.35, 1), (0.2, 0.45, 1), (0.6, 0.5, 1), (0.9, 0.55, 2)]:
            d.ellipse([x0 + w * sx - sr, y0 + h * sy - sr, x0 + w * sx + sr,
                       y0 + h * sy + sr], fill=(255, 255, 255))
        d.ellipse([x0 - w * 0.25, y0 + h * 0.55, x0 + w * 0.45, y0 + h * 1.45],
                  fill=(50, 110, 170))
        d.ellipse([x0 - w * 0.25, y0 + h * 0.55, x0 + w * 0.45, y0 + h * 1.45],
                  outline=(140, 200, 240), width=2)
        d.arc([x0 + w * 0.1, y0 - h * 0.35, x1 + w * 0.15, y0 + h * 0.75],
              200, 330, fill=(240, 200, 90), width=2)
        for i, t in enumerate((0.15, 0.38, 0.62, 0.85)):
            sx = x0 + w * (0.18 + t * 0.7)
            sy = y0 + h * (0.28 + 0.35 * (1 - t) * t * 2.2)
            d.rectangle([sx - 5, sy - 3, sx + 5, sy + 3], fill=(220, 220, 220),
                        outline=(240, 200, 90))
        d.polygon([(x0 + w * 0.68, y0 + h * 0.62), (x0 + w * 0.72, y0 + h * 0.45),
                   (x0 + w * 0.76, y0 + h * 0.62)], fill=(230, 230, 230))
        d.polygon([(x0 + w * 0.68, y0 + h * 0.62), (x0 + w * 0.76, y0 + h * 0.62),
                   (x0 + w * 0.72, y0 + h * 0.72)], fill=(200, 60, 40))
        d.text((x0 + 5, y0 + 4), "1,000,000 SATELLITES", font=F(9, bold=True),
               fill=(255, 220, 120))
    elif kind == "refinery":
        d.rectangle([x0, y0, x1, y0 + h * 0.6], fill=(232, 200, 160))
        d.rectangle([x0, y0 + h * 0.6, x1, y1], fill=(120, 105, 85))
        for i, tx in enumerate((0.08, 0.30, 0.52)):
            d.rectangle([x0 + w * tx, y0 + h * 0.25, x0 + w * (tx + 0.12), y0 + h * 0.62],
                        fill=(90, 95, 100))
            d.rectangle([x0 + w * tx, y0 + h * 0.18, x0 + w * (tx + 0.04), y0 + h * 0.25],
                        fill=(70, 75, 80))
        d.ellipse([x0 + w * 0.70, y0 + h * 0.35, x0 + w * 0.95, y0 + h * 0.62],
                  fill=(180, 180, 175))
        _flame(d, x0 + w * 0.82, y0 + h * 0.38, 8)
        _smoke(d, x0 + w * 0.82, y0 + h * 0.28, 5)
        d.line([(x0 + w * 0.1, y0 + h * 0.75), (x1 - w * 0.1, y0 + h * 0.75)],
               fill=(60, 55, 50), width=2)
    elif kind == "gaza":
        d.rectangle([x0, y0, x1, y0 + h * 0.62], fill=(215, 190, 160))
        d.rectangle([x0, y0 + h * 0.62, x1, y1], fill=(110, 100, 88))
        for i, (bx, bw, bh) in enumerate(((0.05, 0.20, 0.42), (0.30, 0.18, 0.55),
                                          (0.52, 0.20, 0.38), (0.76, 0.18, 0.48))):
            d.rectangle([x0 + w * bx, y0 + h * (0.62 - bh), x0 + w * (bx + bw), y0 + h * 0.62],
                        fill=(150, 140, 125))
            for wy in range(2):
                for wx in range(2):
                    d.rectangle([x0 + w * (bx + 0.03 + wx * 0.07),
                                 y0 + h * (0.62 - bh + 0.06 + wy * 0.12),
                                 x0 + w * (bx + 0.06 + wx * 0.07),
                                 y0 + h * (0.62 - bh + 0.11 + wy * 0.12)],
                                fill=(240, 220, 170))
        d.polygon([(x0 + w * 0.42, y0 + h * 0.05), (x0 + w * 0.47, y0 + h * 0.18),
                   (x0 + w * 0.60, y0 + h * 0.18), (x0 + w * 0.50, y0 + h * 0.26),
                   (x0 + w * 0.55, y0 + h * 0.38), (x0 + w * 0.42, y0 + h * 0.30),
                   (x0 + w * 0.29, y0 + h * 0.38), (x0 + w * 0.34, y0 + h * 0.26),
                   (x0 + w * 0.24, y0 + h * 0.18), (x0 + w * 0.37, y0 + h * 0.18)],
                  fill=(250, 200, 60))
    elif kind == "odesa":
        d.rectangle([x0, y0, x1, y0 + h * 0.55], fill=(200, 215, 225))
        d.rectangle([x0, y0 + h * 0.55, x1, y1], fill=SEA)
        for cx in (0.15, 0.45, 0.75):
            d.line([(x0 + w * cx, y0 + h * 0.12), (x0 + w * cx, y0 + h * 0.58)],
                   fill=(60, 60, 60), width=3)
            d.line([(x0 + w * cx, y0 + h * 0.12), (x0 + w * (cx + 0.12), y0 + h * 0.30)],
                   fill=(60, 60, 60), width=2)
        _smoke(d, x0 + w * 0.6, y0 + h * 0.30, 6)
        _flame(d, x0 + w * 0.6, y0 + h * 0.42, 5)
        d.rectangle([x0 + w * 0.05, y0 + h * 0.62, x0 + w * 0.35, y0 + h * 0.72],
                    fill=(70, 70, 75))
    elif kind == "leak":
        d.rectangle(box, fill=(235, 228, 210))
        for i, (px, py, rot) in enumerate(((0.10, 0.15, 0), (0.38, 0.22, 0), (0.62, 0.12, 0))):
            d.rectangle([x0 + w * px, y0 + h * py, x0 + w * (px + 0.26), y0 + h * (py + 0.55)],
                        fill=(255, 255, 255), outline=(100, 100, 100))
            for li in range(4):
                d.line([(x0 + w * (px + 0.03), y0 + h * (py + 0.10 + li * 0.11)),
                        (x0 + w * (px + 0.23), y0 + h * (py + 0.10 + li * 0.11))],
                       fill=(150, 150, 150), width=1)
        d.text((x0 + 4, y0 + h * 0.78), "490,334", font=F(10, bold=True), fill=RED)
    elif kind == "drones":
        d.rectangle([x0, y0, x1, y0 + h * 0.5], fill=(190, 205, 220))
        d.rectangle([x0, y0 + h * 0.5, x1, y1], fill=(150, 135, 110))
        for hx in (0.12, 0.42, 0.72):
            d.polygon([(x0 + w * hx, y0 + h * 0.62), (x0 + w * (hx + 0.14), y0 + h * 0.62),
                       (x0 + w * (hx + 0.07), y0 + h * 0.52)], fill=(140, 60, 50))
            d.rectangle([x0 + w * hx, y0 + h * 0.62, x0 + w * (hx + 0.14), y0 + h * 0.78],
                        fill=(170, 150, 125))
        for dx, dy in ((0.25, 0.18), (0.65, 0.28)):
            cx, cy = x0 + w * dx, y0 + h * dy
            d.rectangle([cx - 6, cy - 3, cx + 6, cy + 3], fill=(50, 50, 55))
            for ox, oy in ((-10, -6), (10, -6), (-10, 6), (10, 6)):
                d.line([(cx, cy), (cx + ox, cy + oy)], fill=(50, 50, 55), width=1)
                d.ellipse([cx + ox - 5, cy + oy - 1, cx + ox + 5, cy + oy + 1],
                          fill=(120, 120, 120))
    elif kind == "court":
        d.rectangle([x0, y0, x1, y0 + h * 0.55], fill=(210, 205, 190))
        d.rectangle([x0, y0 + h * 0.55, x1, y1], fill=(140, 130, 115))
        d.polygon([(x0 + w * 0.08, y0 + h * 0.28), (x0 + w * 0.5, y0 + h * 0.08),
                   (x0 + w * 0.92, y0 + h * 0.28)], fill=(120, 110, 95))
        for i in range(4):
            cx = x0 + w * (0.16 + i * 0.23)
            d.rectangle([cx - 4, y0 + h * 0.30, cx + 4, y0 + h * 0.58], fill=(245, 240, 225))
        d.rectangle([x0 + w * 0.08, y0 + h * 0.58, x0 + w * 0.92, y0 + h * 0.66],
                    fill=(120, 110, 95))
        d.text((x0 + 4, y0 + h * 0.72), "GUILTY", font=F(11, bold=True), fill=RED)
    elif kind == "shenzhou":
        d.rectangle(box, fill=(14, 18, 38))
        d.ellipse([x0 + w * 0.05, y0 + h * 0.55, x0 + w * 0.35, y0 + h * 1.1],
                  fill=(60, 120, 180))
        d.rectangle([x0 + w * 0.45, y0 + h * 0.30, x0 + w * 0.75, y0 + h * 0.42],
                    fill=(220, 220, 220))
        d.rectangle([x0 + w * 0.38, y0 + h * 0.33, x0 + w * 0.45, y0 + h * 0.39],
                    fill=(180, 180, 180))
        d.rectangle([x0 + w * 0.75, y0 + h * 0.30, x0 + w * 0.82, y0 + h * 0.42],
                    fill=(200, 60, 40))
        d.rectangle([x0 + w * 0.50, y0 + h * 0.20, x0 + w * 0.70, y0 + h * 0.28],
                    fill=(90, 120, 180))
        for sx, sy in ((0.15, 0.15), (0.85, 0.2), (0.3, 0.08), (0.9, 0.5)):
            d.ellipse([x0 + w * sx - 1, y0 + h * sy - 1, x0 + w * sx + 1, y0 + h * sy + 1],
                      fill=(255, 255, 255))
    elif kind == "football":
        d.rectangle(box, fill=(70, 140, 70))
        d.rectangle([x0 + 4, y0 + 4, x1 - 4, y1 - 4], outline=(255, 255, 255), width=1)
        d.line([(x0 + w / 2, y0 + 4), (x0 + w / 2, y1 - 4)], fill=(255, 255, 255), width=1)
        d.ellipse([x0 + w * 0.38, y0 + h * 0.28, x0 + w * 0.62, y0 + h * 0.72],
                  outline=(255, 255, 255), width=1)
        d.ellipse([x0 + w * 0.68, y0 + h * 0.60, x0 + w * 0.82, y0 + h * 0.78],
                  fill=(255, 255, 255), outline=(30, 30, 30))
        d.polygon([(x0 + w * 0.73, y0 + h * 0.62), (x0 + w * 0.77, y0 + h * 0.68),
                   (x0 + w * 0.72, y0 + h * 0.72)], fill=(30, 30, 30))
    elif kind == "basketball":
        d.rectangle(box, fill=(200, 120, 60))
        d.ellipse([x0 + w * 0.25, y0 + h * 0.15, x0 + w * 0.75, y0 + h * 0.85],
                  fill=(220, 110, 40), outline=(120, 50, 10), width=2)
        d.arc([x0 + w * 0.25, y0 + h * 0.15, x0 + w * 0.75, y0 + h * 0.85], 20, 160,
              fill=(120, 50, 10), width=2)
        d.line([(x0 + w * 0.25, y0 + h * 0.5), (x0 + w * 0.75, y0 + h * 0.5)],
               fill=(120, 50, 10), width=2)
        d.line([(x0 + w * 0.5, y0 + h * 0.15), (x0 + w * 0.5, y0 + h * 0.85)],
               fill=(120, 50, 10), width=2)
    elif kind == "factory":
        d.rectangle([x0, y0, x1, y0 + h * 0.55], fill=(215, 200, 170))
        d.rectangle([x0, y0 + h * 0.55, x1, y1], fill=(130, 120, 100))
        d.rectangle([x0 + w * 0.08, y0 + h * 0.35, x0 + w * 0.65, y0 + h * 0.62],
                    fill=(160, 50, 50))
        d.polygon([(x0 + w * 0.08, y0 + h * 0.35), (x0 + w * 0.36, y0 + h * 0.18),
                   (x0 + w * 0.65, y0 + h * 0.35)], fill=(120, 40, 40))
        d.rectangle([x0 + w * 0.72, y0 + h * 0.15, x0 + w * 0.80, y0 + h * 0.62],
                    fill=(90, 85, 80))
        _smoke(d, x0 + w * 0.76, y0 + h * 0.12, 4)
        d.text((x0 + w * 0.12, y0 + h * 0.68), "$139/MO", font=F(9, bold=True),
               fill=(255, 255, 255))
    elif kind == "treaty":
        d.rectangle(box, fill=(190, 215, 230))
        d.ellipse([x0 + w * 0.05, y0 + h * 0.55, x0 + w * 0.55, y0 + h * 1.05],
                  fill=(90, 160, 110))
        d.ellipse([x0 + w * 0.55, y0 + h * 0.62, x0 + w * 0.95, y0 + h * 1.0],
                  fill=(70, 140, 100))
        d.rectangle([x0 + w * 0.52, y0 + h * 0.10, x0 + w * 0.92, y0 + h * 0.55],
                    fill=(255, 255, 255), outline=(100, 100, 100))
        for li in range(4):
            d.line([(x0 + w * 0.56, y0 + h * (0.17 + li * 0.09)),
                    (x0 + w * 0.88, y0 + h * (0.17 + li * 0.09))],
                   fill=(150, 150, 150), width=1)
        d.line([(x0 + w * 0.56, y0 + h * 0.48), (x0 + w * 0.72, y0 + h * 0.48)],
               fill=RED, width=2)
    elif kind == "train":
        d.rectangle([x0, y0, x1, y0 + h * 0.55], fill=(205, 215, 225))
        d.rectangle([x0, y0 + h * 0.55, x1, y1], fill=(110, 105, 95))
        d.rectangle([x0 + w * 0.10, y0 + h * 0.25, x0 + w * 0.90, y0 + h * 0.58],
                    fill=(30, 70, 140))
        d.rectangle([x0 + w * 0.10, y0 + h * 0.25, x0 + w * 0.90, y0 + h * 0.33],
                    fill=(240, 200, 60))
        for i in range(4):
            d.rectangle([x0 + w * (0.16 + i * 0.18), y0 + h * 0.37,
                         x0 + w * (0.28 + i * 0.18), y0 + h * 0.50],
                        fill=(200, 225, 240))
        d.line([(x0, y0 + h * 0.72), (x1, y0 + h * 0.72)], fill=(50, 50, 50), width=3)
        for i in range(6):
            d.line([(x0 + w * i / 5, y0 + h * 0.72), (x0 + w * (i / 5 + 0.03), y0 + h * 0.82)],
                   fill=(50, 50, 50), width=2)


def scene_img(box, kind):
    """Render a scene onto its own image so nothing bleeds outside the box."""
    x0, y0, x1, y1 = box
    w, h = int(x1 - x0), int(y1 - y0)
    tmp = Image.new("RGB", (w, h), PAPER)
    _scene_draw(ImageDraw.Draw(tmp), (0, 0, w, h), kind)
    return tmp


def map_img(box):
    """Render the schematic map onto its own image so nothing bleeds out."""
    x0, y0, x1, y1 = box
    w, h = int(x1 - x0), int(y1 - y0)
    tmp = Image.new("RGB", (w, h), PAPER)
    _map_draw(ImageDraw.Draw(tmp), (0, 0, w, h))
    return tmp


# ---------------------------------------------------------------- data
HEROES = [
    ("tankers", "IRAN WAR", "Two tankers hit by mines, ablaze in Hormuz",
     "Iran's Revolutionary Guard said two oil tankers struck naval mines and "
     "exploded and caught fire in the Strait of Hormuz, after trying to transit "
     "an unauthorised route. Tehran said new systems now control the waterway.",
     "M. EAST | WAR | REUTERS | CONFIRMED"),
    ("market", "MARKETS", "Wall Street's wild Thanksgiving-eve whipsaw",
     "The Nasdaq fell as much as 4.6% and the Dow lost about 1,100 points in "
     "the morning AI sell-off, then buyers stepped in: the Dow closed UP 164 "
     "at 50,183, the S&P -0.25%, the Nasdaq -0.62%. Markets shut Thursday.",
     "N. AMERICA | MARKETS | REUTERS / AP | CONFIRMED"),
    ("space", "SPACE", "FCC clears SpaceX to fly 1m satellites",
     "The FCC authorised SpaceX to deploy up to one million 'Starmind' "
     "satellites as orbital data centres for AI computing, over objections "
     "from Amazon, Viasat and astronomers. First satellite due by 2033.",
     "N. AMERICA | SPACE | REUTERS | CONFIRMED"),
]

PANELS = [
    ("refinery", "HOUTHIS HIT SAUDI REFINERY",
     "Yemen's Houthis said they struck the Ras Tanura refinery, causing fires; "
     "Saudi defences intercepted four drones there.",
     "M. EAST | WAR | REUTERS"),
    ("gaza", "ISRAEL KILLS HAMAS SECURITY CHIEF",
     "Israel killed Hamas colonel Mohammad Abuelouf, who ran the militants' "
     "interior security, with his wife and two children in Gaza City.",
     "M. EAST | WAR | REUTERS"),
    ("odesa", "RUSSIA STRIKES ODESA AND KYIV",
     "A strike on Odesa region killed two and hurt three, including a child; "
     "Kyiv was hit too, a fire breaking out in an apartment block.",
     "EUROPE | WAR | REUTERS"),
    ("leak", "LEAK: 490,334 RUSSIAN SOLDIERS DEAD",
     "At least 490,334 Russian soldiers have died since 2022, leaked Russian "
     "statistics analysed by the BBC show.",
     "EUROPE | WAR | BBC"),
    ("drones", "SUDAN: RSF DRONES KILL 19 CIVILIANS",
     "Drone strikes by the Rapid Support Forces killed 19 civilians and "
     "wounded 20 in Damazin and Roseires, rights lawyers said.",
     "AFRICA | WAR | REUTERS"),
    ("court", "MALAYSIA SUES GOOGLE FOR $150M",
     "Malaysia's regulator sued Google for nearly $150 million over "
     "YouTube content, in a rare state action against a US tech giant.",
     "ASIA | LAW | DOW JONES"),
    ("shenzhou", "SHENZHOU-24 DOCKS, PAKISTANI ABOARD",
     "China's Shenzhou-24 docked at Tiangong carrying a Pakistani national, "
     "the first foreign astronaut on a Chinese mission.",
     "ASIA | SPACE | REUTERS"),
    ("football", "CHAMPIONS LEAGUE NIGHT",
     "Liverpool won 3-0 at Brugge (Isak twice), PSG held 2-2 by Roma, "
     "Lille stunned Bayern 2-1.",
     "EUROPE | SPORT | UEFA"),
    ("basketball", "76ERS BEAT HEAT 111-104",
     "Philadelphia beat Miami 111-104 in Wednesday's NBA action.",
     "N. AMERICA | SPORT | SPORTRADAR"),
    ("factory", "BANGLADESH RAISES GARMENT WAGE 36%",
     "Dhaka raised the minimum monthly garment wage by 36% to $139 after "
     "protests by workers.",
     "ASIA | LABOUR | REUTERS"),
    ("treaty", "SOLOMONS SIGN ANTI-BASE TREATY",
     "The Solomon Islands and Australia signed a treaty barring any foreign "
     "military base there; China pact will not be renewed.",
     "OCEANIA | DIPLOMACY | NYT"),
    ("train", "EUROSTAR STRIKE HALTS TRAINS",
     "A surprise strike by Paris-based staff cancelled Paris-London trains; "
     "four in five later ran as scheduled.",
     "EUROPE | TRANSPORT | AP"),
]

BRIEFS = [
    ("Pope Leo XIV decried the failure of UN COP31 climate talks; extreme "
     "events are \"becoming increasingly frequent\".", "CLIMATE | AP"),
    ("US Q3 GDP revised up to a +4.3% annual rate, from +3.4%.", "ECONOMY | REUTERS"),
    ("US core PCE rose 0.3% on the month, in line; gold fell ~2% to $3,484.",
     "ECONOMY | AP"),
    ("Sen. Schumer accused Nvidia chief Jensen Huang of violating chip-export "
     "law; Huang told staff he broke the code of conduct.", "TECH | REUTERS"),
    ("US officials briefed Congress on Nvidia and Megaspeed; no evidence "
     "Alice Huang was directed by Beijing.", "TECH | NYT"),
    ("New US tariffs loom after a factory-capacity probe: 20% on China, 15% "
     "on the EU and others.", "TRADE | AP"),
    ("Kilmar Abrego Garcia, wrongfully deported in 2025, voluntarily left "
     "the US for Spain: \"I am leaving happy\".", "IMMIGRATION | NYT"),
    ("Sen. Dan Sullivan conceded to Mary Peltola in Alaska, a week after AP "
     "called the race; she won by 4+ points.", "POLITICS | NYT"),
    ("Trump awarded the Presidential Medal of Freedom to Rudy Giuliani in a "
     "closed-door White House ceremony.", "POLITICS | POLITICO"),
    ("The US has paused joint military operations with Ecuador while it "
     "probes a September raid that killed Carlos Munoz Jara.", "DIPLOMACY | ATLANTIC"),
    ("WHO chief Tedros urged lifting the US fuel blockade on Cuba, warning "
     "children's lives are at risk.", "HEALTH | REUTERS"),
    ("Chancellor Merz accused Russia of \"escalating\" threats as Berlin "
     "weighs a US military pullback from Europe.", "DIPLOMACY | REUTERS"),
    ("Libya vowed retaliation after a Ukrainian drone hit a Russian warship "
     "in Benghazi, killing two Libyan officers.", "WAR | AP"),
    ("The Justice Dept. apologised for a mix-up over its statement on "
     "the search of Rep. Omar's home.", "LAW | NYT"),
    ("Prosecutors dropped the charge against Rep.-elect LaKesha Womack over "
     "an unreturned rental car from 2019.", "LAW | AXIOS"),
    ("Anthropic and OpenAI staff believe some unreleased internal AI models "
     "are now too powerful to release safely.", "AI | AXIOS"),
    ("The CIA and the Director of National Intelligence suffered a breach "
     "of some unclassified information.", "SECURITY | REUTERS"),
    ("The UK financial watchdog warned on AI as Meta launched an adapted "
     "version of its Muse model.", "TECH | REUTERS"),
    ("New York moved the Macy's Thanksgiving Day Parade to Saturday as a "
     "nor'easter bore down on the city.", "CULTURE | EOPTION"),
    ("Deere's quarterly profit fell as sales of large farm equipment "
     "declined.", "BUSINESS | DOW JONES"),
    ("Shein's profit rose despite lower revenue as it adapted to trade "
     "pressures.", "BUSINESS | DOW JONES"),
    ("easyJet's profit slumped ahead of the Apollo takeover as fuel costs "
     "jumped.", "BUSINESS | DOW JONES"),
    ("Global airports court private capital to fund upgrades, raising "
     "cost concerns for travellers.", "BUSINESS | REUTERS"),
    ("Dodgers owner Todd Boehly clinched a deal for the overseas assets of "
     "Russia's Lukoil.", "BUSINESS | DOW JONES"),
    ("The FTC imposed strict board curbs on Beretta's 25% stake in rival "
     "Sturm Ruger.", "BUSINESS | DOW JONES"),
    ("Fragrance giants were handed $630m in EU and UK antitrust fines.",
     "BUSINESS | DOW JONES"),
    ("Jannik Sinner faces an extended spell out after knee surgery.",
     "SPORT | REUTERS"),
    ("World champion D. Gukesh held Javokhir Sindarov to a draw in Game 1 "
     "of their World Championship match.", "SPORT | PTI"),
    ("Jayson Tatum scored 41 as Boston beat Washington 131-116 in the NBA "
     "Cup (Tue night, 00:30 UTC).", "SPORT | PTI"),
    ("Green Bay beat the LA Rams 24-19 in the first ever Thanksgiving Eve "
     "NFL game, on Netflix from SoFi.", "SPORT | COVERS"),
    ("India thrashed Japan 4-0 to sweep the Women's Asian Champions Trophy "
     "league stage in hockey.", "SPORT | PTI"),
    ("Shavon Shields scored 26 as Fenerbahce beat Barcelona 83-77 in the "
     "EuroLeague.", "SPORT | EUROLEAGUE"),
    ("Alaska's lieutenant governor ended the state's deal sharing its voter "
     "list with the Justice Dept.", "POLITICS | AP"),
    ("Commerce chief Lutnick reassigned his own law-enforcement agents "
     "after some of his security detail quit.", "POLITICS | ATLANTIC"),
    ("A Philadelphia history group sued over a \"whitewashed depiction\" of "
     "slavery at George Washington's former home.", "LAW | AP"),
    ("Mexico reinforced Sinaloa after capturing FBI most-wanted 'El Chapo "
     "Isidro' with US intelligence help.", "SECURITY | WSJ"),
    ("Suspected militants killed at least 30 and burned homes in villages "
     "in Nigeria's Niger state.", "WAR | REUTERS"),
    ("At least 30 were killed when a fuel tanker exploded on Cairo's Ring "
     "Road, engulfing cars in flames.", "TRANSPORT | REUTERS"),
]

FIELDS = ["WAR", "MARKETS", "SPACE", "TECH", "DIPLOMACY", "CLIMATE", "ECONOMY",
          "TRADE", "IMMIGRATION", "POLITICS", "LAW", "AI", "SECURITY", "BUSINESS",
          "SPORT", "CULTURE", "LABOUR", "HEALTH", "TRANSPORT", "ENERGY"]

TIMELINE = [
    ("00:30", "Tatum 41: Celtics 131-116 Wizards"),
    ("07:00", "Eurostar strike halts Paris-London trains"),
    ("10:15", "Two tankers hit mines, burn in Hormuz"),
    ("13:30", "US Q3 GDP revised up to +4.3%"),
    ("14:30", "Wall St opens: Nasdaq -4% in AI sell-off"),
    ("20:00", "UCL: Liverpool 3-0 Brugge, PSG 2-2 Roma"),
    ("20:57", "FCC clears SpaceX 1m satellites"),
    ("21:00", "Dow closes +164 at 50,183 after -1,100 plunge"),
    ("23:30", "First Thanksgiving Eve NFL game (8pm ET)"),
]

# (label, x, y) in map-box coordinates; region of each pin
PINS = [
    ("1 NEW YORK", 95, 28, "N. AMERICA"),
    ("2 WASHINGTON", 102, 37, "N. AMERICA"),
    ("3 LOS ANGELES", 42, 40, "N. AMERICA"),
    ("4 QUITO", 178, 67, "S. AMERICA"),
    ("5 LONDON", 302, 15, "EUROPE"),
    ("6 BORGU", 318, 60, "AFRICA"),
    ("7 ODESA", 348, 27, "EUROPE"),
    ("8 DAMAZIN", 332, 59, "AFRICA"),
    ("9 BENGHAZI", 342, 43, "AFRICA"),
    ("10 GAZA", 366, 40, "M. EAST"),
    ("11 RAS TANURA", 382, 45, "M. EAST"),
    ("12 HORMUZ", 392, 49, "M. EAST"),
    ("13 DHAKA", 478, 45, "ASIA"),
    ("14 JIUQUAN", 500, 27, "ASIA"),
    ("15 HONIARA", 582, 81, "OCEANIA"),
]

DATE_CHECK = [
    "Houthi strike on Riyadh tower, 11 hurt - 24 Nov",
    "Putin: Ukraine keeps hitting refineries - 24 Nov",
    "Huawei verdict handed down - 24 Nov",
    "Real Madrid 5-1 PSV, UCL - 24 Nov",
    "Arsenal 1-1 Dortmund; Man City 2-2 Napoli - 24 Nov",
    "Washington 22-20 Cincinnati, MNF - 23 Nov",
    "AP calls Alaska race for Peltola - 17 Nov",
    "Abrego Garcia deported to El Salvador - Mar 2025",
    "Belgium national austerity strike - 23 Nov",
    "France budget protests - 5 Nov",
    "DOJ-Alaska voter-list deal signed - Dec 2025",
    "\"No Kings\" protest, Collins hurt - 28 Mar 2026",
]


def _map_draw(d, box):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(214, 228, 238), outline=(120, 110, 95))
    # schematic continents (rough equirectangular shapes)
    land = (196, 200, 170)
    d.polygon([(x0 + 25, y0 + 10), (x0 + 150, y0 + 7), (x0 + 165, y0 + 24),
               (x0 + 120, y0 + 38), (x0 + 90, y0 + 50), (x0 + 55, y0 + 44),
               (x0 + 30, y0 + 28)], fill=land, outline=(120, 115, 95))
    d.polygon([(x0 + 165, y0 + 50), (x0 + 215, y0 + 50), (x0 + 220, y0 + 68),
               (x0 + 200, y0 + 88), (x0 + 180, y0 + 80), (x0 + 168, y0 + 64)],
              fill=land, outline=(120, 115, 95))
    d.polygon([(x0 + 295, y0 + 7), (x0 + 350, y0 + 5), (x0 + 360, y0 + 22),
               (x0 + 340, y0 + 35), (x0 + 305, y0 + 32), (x0 + 292, y0 + 18)],
              fill=land, outline=(120, 115, 95))
    d.polygon([(x0 + 300, y0 + 38), (x0 + 365, y0 + 37), (x0 + 375, y0 + 60),
               (x0 + 350, y0 + 82), (x0 + 325, y0 + 77), (x0 + 305, y0 + 56)],
              fill=land, outline=(120, 115, 95))
    d.polygon([(x0 + 390, y0 + 8), (x0 + 600, y0 + 5), (x0 + 615, y0 + 28),
               (x0 + 580, y0 + 48), (x0 + 520, y0 + 57), (x0 + 460, y0 + 54),
               (x0 + 420, y0 + 44), (x0 + 392, y0 + 28)], fill=land,
              outline=(120, 115, 95))
    d.polygon([(x0 + 555, y0 + 72), (x0 + 605, y0 + 70), (x0 + 615, y0 + 84),
               (x0 + 580, y0 + 90), (x0 + 560, y0 + 84)], fill=land,
              outline=(120, 115, 95))
    d.text((x0 + 6, y0 + 3), "THE WORLD, 25 NOVEMBER", font=F(9, bold=True), fill=NAVY)
    for label, px, py, _reg in PINS:
        num = label.split()[0]
        cx, cy = x0 + px, y0 + py
        d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=RED, outline=(255, 255, 255))
        d.text((cx - 2 if len(num) == 1 else cx - 5, cy - 5), num,
               font=F(8, bold=True), fill=(255, 255, 255))


def render(out_path):
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    xL, xR = M, W - M

    # ---- masthead
    rule(d, xL, xR, 8, width=3)
    d.text((xL, 12), "THE WORLD ON ONE PAGE", font=F(44, bold=True), fill=INK)
    d.text((xR - 250, 20), "WEDNESDAY", font=F(16, bold=True), fill=RED)
    d.text((xR - 250, 38), "25 NOVEMBER 2026", font=F(16, bold=True), fill=INK)
    d.text((xL, 60), "53 STORIES  |  7 REGIONS  |  20 FIELDS  |  THE FULL DAY, 00:00-24:00 UTC",
           font=F(12, bold=True), fill=NAVY)
    d.text((xR - 250, 60), "FULL-DAY EDITION", font=F(11, bold=True), fill=GREY)
    rule(d, xL, xR, 78, width=2)

    # ---- field strip (20 chips, 2 rows of 10)
    y = 84
    cw = (xR - xL) / 10
    for i, f in enumerate(FIELDS):
        cx = xL + (i % 10) * cw
        cy = y + (i // 10) * 15
        d.rectangle([cx + 1, cy, cx + cw - 2, cy + 13], fill=LIGHT, outline=(180, 172, 155))
        tf = F(8, bold=True)
        tw = tf.getlength(f)
        d.text((cx + (cw - tw) / 2, cy + 2), f, font=tf, fill=NAVY)

    # ---- heroes
    y = 118
    hw = (xR - xL - 16) / 3
    rule(d, xL, xR, y - 4, width=1)
    for i, (kind, kick, head, body, tag) in enumerate(HEROES):
        hx = xL + i * (hw + 8)
        img.paste(scene_img((hx, y, hx + hw, y + 92), kind), (int(hx), y))
        yy = y + 96
        d.text((hx, yy), kick, font=F(10, bold=True), fill=RED)
        yy += 13
        _, yy = draw_wrapped(d, hx, yy, head, F(15, bold=True), hw, leading=17, max_lines=2)
        _, yy = draw_wrapped(d, hx, yy + 2, body, F(11), hw, leading=13, max_lines=3)
        d.text((hx, y + 164), tag, font=F(8, bold=True), fill=GREY)
        if i < 2:
            d.line([(hx + hw + 4, y), (hx + hw + 4, y + 178)], fill=(200, 192, 175))

    # ---- panels
    y = 300
    rule(d, xL, xR, y - 4, width=2)
    d.text((xL, y), "TWELVE STORIES IN PICTURES", font=F(12, bold=True), fill=INK)
    d.text((xR - 300, y), "EVERY PANEL VERIFIED 25 NOV 2026", font=F(10, bold=True), fill=GREY)
    pw = (xR - xL - 24) / 4
    ph = 68
    for i, (kind, head, body, tag) in enumerate(PANELS):
        col, row = i % 4, i // 4
        px = xL + col * (pw + 8)
        py = y + 14 + row * (ph + 4)
        img.paste(scene_img((px, py, px + 56, py + 56), kind), (int(px), py))
        tx = px + 64
        _, yy = draw_wrapped(d, tx, py, head, F(10, bold=True), pw - 64, leading=12,
                             max_lines=2)
        _, yy = draw_wrapped(d, tx, yy + 1, body, F(9), pw - 64, leading=11, max_lines=3)
        d.text((tx, py + 56), tag, font=F(7, bold=True), fill=GREY)

    # ---- briefs
    y = 538
    rule(d, xL, xR, y - 4, width=2)
    d.text((xL, y), "THE DAY IN BRIEF  —  38 MORE STORIES", font=F(12, bold=True), fill=INK)
    d.text((xR - 330, y), "TIER + SOURCE ON EVERY ITEM", font=F(10, bold=True), fill=GREY)
    bw = (xR - xL - 16) / 3
    per_col = 13
    for i, (text, tag) in enumerate(BRIEFS):
        col = i // per_col
        row = i % per_col
        bx = xL + col * (bw + 8)
        by = y + 16 + row * 19
        d.text((bx, by), "%d." % (i + 1), font=F(9, bold=True), fill=RED)
        n, _ = draw_wrapped(d, bx + 18, by, text, F(9), bw - 18 - 72, leading=10,
                            max_lines=2)
        d.text((bx + bw - 76, by), tag, font=F(7, bold=True), fill=GREY)
    y = y + 16 + per_col * 19 + 6

    # ---- map + numbers
    rule(d, xL, xR, y - 4, width=2)
    map_w = 640
    img.paste(map_img((xL, y, xL + map_w, y + 92)), (xL, y))
    nx = xL + map_w + 10
    nw = xR - nx
    d.text((nx, y), "15 PINS — BY REGION", font=F(11, bold=True), fill=INK)
    counts = [("N. AMERICA", 3), ("S. AMERICA", 1), ("EUROPE", 2), ("AFRICA", 3),
              ("M. EAST", 3), ("ASIA", 2), ("OCEANIA", 1)]
    yy = y + 16
    for name, n in counts:
        d.text((nx, yy), name, font=F(10), fill=INK)
        d.text((nx + nw - 20, yy), str(n), font=F(10, bold=True), fill=RED)
        yy += 11
    assert sum(n for _, n in counts) == len(PINS) == 15, "pin legend must sum to 15"
    y = y + 92 + 6

    # ---- timeline
    rule(d, xL, xR, y - 4, width=2)
    d.text((xL, y), "THE DAY IN TIME  —  UTC, 25 NOVEMBER 2026", font=F(11, bold=True), fill=INK)
    ty = y + 22
    d.line([(xL + 10, ty), (xR - 10, ty)], fill=NAVY, width=2)
    tw = (xR - xL - 20) / len(TIMELINE)
    for i, (t, ev) in enumerate(TIMELINE):
        cx = xL + 10 + i * tw + tw / 2
        d.ellipse([cx - 4, ty - 4, cx + 4, ty + 4], fill=RED, outline=(255, 255, 255))
        d.text((cx - 14, ty - 16), t, font=F(9, bold=True), fill=NAVY)
        _, _ = draw_wrapped(d, cx - tw / 2 + 2, ty + 7, ev, F(8), tw - 4, leading=9,
                            max_lines=2)
    y = ty + 7 + 2 * 9 + 4

    # ---- date check + footer
    rule(d, xL, xR, y - 4, width=2)
    d.text((xL, y), "DATE CHECK — NOT 25 NOVEMBER, SO NOT IN THIS PAPER:",
           font=F(10, bold=True), fill=RED)
    dc = "  |  ".join(DATE_CHECK)
    _, y2 = draw_wrapped(d, xL, y + 13, dc, F(9), xR - xL, leading=10, max_lines=2)
    rule(d, xL, xR, y2 + 4, width=1)
    d.text((xL, y2 + 8),
           "Sources: Reuters, AP, BBC, NYT, The Atlantic, Politico, Axios, UEFA, PTI, "
           "Dow Jones, Covers, Sportradar, EuroLeague, eOption. All 53 stories verified "
           "as 25 Nov 2026.",
           font=F(9, italic=True), fill=GREY)
    assert y2 + 22 <= H - 4, "layout overflow: footer at %d" % (y2 + 22)
    img.save(out_path, "PNG", optimize=True)
    print("wrote %s (%d bytes)" % (out_path, os.path.getsize(out_path)))


if __name__ == "__main__":
    out = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    os.makedirs(out, exist_ok=True)
    render(os.path.join(out, "entry.png"))
