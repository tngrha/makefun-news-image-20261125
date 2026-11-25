#!/usr/bin/env python3
"""Render 'The World on One Page' — Wednesday 25 November 2026.

Original serif broadsheet renderer, written in this session for
news-image-20261125. PIL + Noto Serif. One 1024x1024 PNG.
Usage: python3 render.py [out.png]
"""
import math
import sys
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (247, 243, 232)
INK = (26, 26, 26)
RED = (176, 30, 36)
GREEN = (46, 125, 50)
AMBER = (166, 110, 0)
GREY = (110, 105, 95)
RULE = (180, 172, 155)
NAVY = (46, 64, 87)
BRICK = (166, 58, 46)
OCHRE = (192, 138, 44)

FDIR = "/usr/share/fonts/truetype/noto/"
def font(name, size):
    return ImageFont.truetype(FDIR + name, size)

F_TITLE = lambda s: font("NotoSerifDisplay-Black.ttf", s)
F_HEAD = lambda s: font("NotoSerif-Bold.ttf", s)
F_BODY = lambda s: font("NotoSerif-Regular.ttf", s)
F_TAG = lambda s: font("NotoSans-Bold.ttf", s)
F_SMALL = lambda s: font("NotoSans-Regular.ttf", s)

WARN = []

def wrap(draw, text, fnt, maxw):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=fnt) <= maxw:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

def draw_lines(draw, lines, x, y, fnt, fill, lh):
    for ln in lines:
        draw.text((x, y), ln, font=fnt, fill=fill)
        y += lh
    return y

def spaced(draw, cx, y, text, fnt, fill, spacing=3):
    widths = [draw.textlength(c, font=fnt) for c in text]
    total = sum(widths) + spacing * (len(text) - 1)
    x = cx - total / 2
    for c, w in zip(text, widths):
        draw.text((x, y), c, font=fnt, fill=fill)
        x += w + spacing
    return total

def badge(draw, cx, cy, r, num, fill=RED):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill, outline=(255, 255, 255), width=1)
    f = F_TAG(11 if r >= 10 else 9)
    tw = draw.textlength(str(num), font=f)
    th = f.getbbox(str(num))[3]
    draw.text((cx - tw / 2, cy - th / 2 - 1), str(num), font=f, fill=(255, 255, 255))

TIER_FILL = {"CONFIRMED": GREEN, "REPORTED": AMBER, "CLAIM": RED}

# ---------------------------------------------------------------- scenes
def scene(draw, box, theme):
    """Flat vector illustration inside box (x0,y0,x1,y1)."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    if theme == "chart":
        draw.rectangle(box, fill=NAVY)
        for i, bh in enumerate([0.55, 0.7, 0.45, 0.8, 0.35, 0.6]):
            bx = x0 + 8 + i * (w - 16) / 6
            bw = (w - 16) / 6 - 4
            draw.rectangle([bx, y1 - 6 - bh * (h - 18), bx + bw, y1 - 6], fill=(120, 140, 170))
        pts = [(x0 + 6, y0 + 12), (x0 + w * 0.3, y0 + 22), (x0 + w * 0.5, y0 + 15),
               (x0 + w * 0.7, y0 + 32), (x0 + w - 8, y0 + h - 10)]
        draw.line(pts, fill=(255, 90, 80), width=3, joint="curve")
        draw.ellipse([pts[-1][0] - 4, pts[-1][1] - 4, pts[-1][0] + 4, pts[-1][1] + 4], fill=(255, 90, 80))
    elif theme == "war":
        draw.rectangle(box, fill=(203, 196, 182))
        draw.rectangle([x0, y1 - 18, x1, y1], fill=(90, 82, 70))
        for bx, bw, bh in [(0.05, 0.16, 0.45), (0.25, 0.14, 0.62), (0.45, 0.18, 0.5), (0.68, 0.15, 0.7), (0.86, 0.12, 0.42)]:
            draw.rectangle([x0 + bx * w, y1 - 18 - bh * (h - 30), x0 + (bx + bw) * w, y1 - 18], fill=(70, 64, 55))
        for sx, sy, r in [(0.3, 0.32, 8), (0.36, 0.26, 10), (0.42, 0.32, 7)]:
            draw.ellipse([x0 + sx * w - r, y0 + sy * h - r, x0 + sx * w + r, y0 + sy * h + r], fill=(120, 112, 100))
        draw.ellipse([x0 + w * 0.78, y0 + 8, x0 + w * 0.78 + 12, y0 + 20], fill=(230, 200, 120))
    elif theme == "politics":
        draw.rectangle(box, fill=(58, 84, 120))
        draw.rectangle([x0 + w * 0.2, y1 - 8, x1 - w * 0.2, y1 - 4], fill=(240, 236, 224))
        for i in range(5):
            px = x0 + w * (0.24 + i * 0.13)
            draw.rectangle([px, y1 - 24, px + 5, y1 - 8], fill=(240, 236, 224))
        draw.rectangle([x0 + w * 0.2, y1 - 27, x1 - w * 0.2, y1 - 24], fill=(240, 236, 224))
        draw.pieslice([cx - 16, y1 - 41, cx + 16, y1 - 27], 180, 360, fill=(240, 236, 224))
        for sx in (0.12, 0.88):
            draw.ellipse([x0 + sx * w - 3, y0 + 10, x0 + sx * w + 3, y0 + 16], fill=(255, 220, 120))
    elif theme == "gaza":
        draw.rectangle(box, fill=(214, 200, 178))
        draw.rectangle([x0, y1 - 14, x1, y1], fill=(120, 108, 92))
        for bx, bw, bh in [(0.08, 0.22, 0.55), (0.36, 0.24, 0.75), (0.66, 0.26, 0.6)]:
            draw.rectangle([x0 + bx * w, y1 - 14 - bh * (h - 26), x0 + (bx + bw) * w, y1 - 14], fill=(96, 86, 72))
        for sx, sy, r in [(0.55, 0.28, 8), (0.6, 0.2, 11), (0.65, 0.3, 7)]:
            draw.ellipse([x0 + sx * w - r, y0 + sy * h - r, x0 + sx * w + r, y0 + sy * h + r], fill=(105, 98, 88))
    elif theme == "chip":
        draw.rectangle(box, fill=(38, 48, 66))
        draw.rectangle([cx - 16, cy - 16, cx + 16, cy + 16], fill=(70, 90, 120), outline=(180, 200, 220), width=2)
        draw.rectangle([cx - 8, cy - 8, cx + 8, cy + 8], fill=(180, 200, 220))
        for i in range(4):
            px = cx - 12 + i * 8
            draw.line([px, cy - 16, px, y0 + 4], fill=(180, 200, 220), width=2)
            draw.line([px, cy + 16, px, y1 - 4], fill=(180, 200, 220), width=2)
            py = cy - 12 + i * 8
            draw.line([cx - 16, py, x0 + 4, py], fill=(180, 200, 220), width=2)
            draw.line([cx + 16, py, x1 - 4, py], fill=(180, 200, 220), width=2)
        draw.line([(x0 + 6, y1 - 8), (x0 + w * 0.45, y0 + 12), (x0 + w * 0.7, y0 + 22), (x1 - 6, y0 + 8)], fill=(255, 90, 80), width=2)
    elif theme == "inflation":
        draw.rectangle(box, fill=(232, 214, 170))
        for i, bh in enumerate([0.35, 0.5, 0.65, 0.85]):
            bx = x0 + 10 + i * (w - 20) / 4
            bw = (w - 20) / 4 - 6
            draw.rectangle([bx, y1 - 8 - bh * (h - 20), bx + bw, y1 - 8], fill=(BRICK if i == 3 else OCHRE))
        draw.line([(x0 + 8, y0 + h * 0.55), (x1 - 8, y0 + 12)], fill=RED, width=3)
        draw.polygon([(x1 - 8, y0 + 12), (x1 - 20, y0 + 14), (x1 - 10, y0 + 24)], fill=RED)
    elif theme == "mine":
        draw.rectangle(box, fill=(70, 60, 50))
        draw.rectangle([x0, y1 - 16, x1, y1], fill=(40, 34, 28))
        draw.ellipse([cx - 14, cy - 12, cx + 14, cy + 12], fill=(240, 200, 80))
        draw.rectangle([cx - 16, cy - 4, cx + 16, cy + 2], fill=(240, 200, 80))
        draw.ellipse([cx - 4, cy - 18, cx + 4, cy - 10], fill=(255, 240, 180))
        for sx in (0.15, 0.85):
            draw.ellipse([x0 + sx * w - 2, y0 + 8, x0 + sx * w + 2, y0 + 12], fill=(255, 240, 180))
    elif theme == "court":
        draw.rectangle(box, fill=(96, 96, 110))
        draw.rectangle([cx - 2, y0 + 14, cx + 2, y1 - 10], fill=(235, 230, 215))
        draw.rectangle([cx - 16, y1 - 12, cx + 16, y1 - 8], fill=(235, 230, 215))
        draw.line([(cx - 20, y0 + 18), (cx + 20, y0 + 18)], fill=(235, 230, 215), width=2)
        for s in (-1, 1):
            draw.line([(cx + s * 20, y0 + 18), (cx + s * 13, y0 + 30)], fill=(235, 230, 215), width=2)
            draw.arc([cx + s * 13 - 8, y0 + 26, cx + s * 13 + 8, y0 + 42], 0, 180, fill=(235, 230, 215), width=2)
        draw.ellipse([cx - 3, y0 + 8, cx + 3, y0 + 14], fill=(235, 230, 215))
    elif theme == "rocket":
        draw.rectangle(box, fill=(24, 32, 52))
        for sx, sy in [(0.2, 0.25), (0.85, 0.15), (0.7, 0.7), (0.15, 0.75)]:
            draw.ellipse([x0 + sx * w - 2, y0 + sy * h - 2, x0 + sx * w + 2, y0 + sy * h + 2], fill=(255, 255, 255))
        draw.polygon([(cx, y0 + 6), (cx - 8, cy + 2), (cx + 8, cy + 2)], fill=(220, 60, 50))
        draw.rectangle([cx - 8, cy + 2, cx + 8, cy + 16], fill=(235, 235, 235))
        draw.rectangle([cx - 8, cy + 16, cx + 8, cy + 20], fill=(220, 60, 50))
        draw.polygon([(cx - 8, cy + 10), (cx - 14, cy + 20), (cx - 8, cy + 18)], fill=(220, 60, 50))
        draw.polygon([(cx + 8, cy + 10), (cx + 14, cy + 20), (cx + 8, cy + 18)], fill=(220, 60, 50))
        draw.polygon([(cx - 4, cy + 20), (cx + 4, cy + 20), (cx, cy + 30)], fill=(255, 190, 60))
    elif theme == "plane":
        draw.rectangle(box, fill=(150, 190, 210))
        draw.ellipse([x0 + w * 0.62, y0 + 6, x0 + w * 0.62 + 22, y0 + 24], fill=(250, 240, 190))
        draw.ellipse([cx - 26, cy - 6, cx + 26, cy + 6], fill=(255, 255, 255))
        draw.polygon([(cx + 26, cy), (cx + 40, cy - 8), (cx + 40, cy + 2)], fill=(255, 255, 255))
        draw.polygon([(cx - 6, cy - 6), (cx - 2, cy - 20), (cx + 6, cy - 6)], fill=(255, 255, 255))
        draw.polygon([(cx - 6, cy + 6), (cx - 2, cy + 18), (cx + 6, cy + 6)], fill=(255, 255, 255))
        for sx in (0.2, 0.5, 0.8):
            draw.ellipse([x0 + sx * w - 12, y1 - 14, x0 + sx * w + 12, y1 - 6], fill=(255, 255, 255))
    elif theme == "tariff":
        draw.rectangle(box, fill=(40, 90, 110))
        draw.rectangle([x0, y1 - 16, x1, y1], fill=(30, 70, 90))
        draw.rectangle([x0 + 8, y1 - 30, x1 - 8, y1 - 16], fill=(60, 60, 60))
        for i, col in enumerate([(200, 60, 50), (220, 160, 60), (60, 140, 90)]):
            bx = x0 + 10 + i * 18
            draw.rectangle([bx, y1 - 44, bx + 15, y1 - 30], fill=col)
        draw.rectangle([x0 + w * 0.68, y1 - 56, x0 + w * 0.68 + 16, y1 - 30], fill=(230, 230, 230))
        draw.rectangle([x0 + w * 0.68 + 4, y1 - 62, x0 + w * 0.68 + 12, y1 - 56], fill=(230, 230, 230))
    elif theme == "blast":
        draw.rectangle(box, fill=(60, 55, 48))
        for ang in range(0, 360, 30):
            r2 = 20
            a = math.radians(ang)
            draw.line([(cx, cy), (cx + r2 * math.cos(a), cy + r2 * math.sin(a))], fill=(255, 190, 60), width=4)
        draw.ellipse([cx - 9, cy - 9, cx + 9, cy + 9], fill=(255, 120, 40))
        draw.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=(255, 220, 120))
        for sx, sy, r in [(0.2, 0.2, 5), (0.85, 0.3, 4), (0.75, 0.8, 5)]:
            draw.ellipse([x0 + sx * w - r, y0 + sy * h - r, x0 + sx * w + r, y0 + sy * h + r], fill=(150, 140, 125))
    elif theme == "fashion":
        draw.rectangle(box, fill=(196, 164, 150))
        draw.polygon([(cx - 12, y0 + 10), (cx + 12, y0 + 10), (cx + 8, cy + 14), (cx - 8, cy + 14)], fill=(255, 255, 255))
        draw.ellipse([cx - 3, y0 + 12, cx + 3, y0 + 18], fill=(196, 164, 150))
        draw.text((cx - 6, cy - 2), "$", font=F_HEAD(16), fill=RED)
        draw.line([(x0 + 8, y1 - 8), (x1 - 8, y1 - 8)], fill=(120, 90, 80), width=2)
    elif theme == "spy":
        draw.rectangle(box, fill=(30, 34, 44))
        draw.ellipse([cx - 22, cy - 10, cx + 22, cy + 10], fill=(200, 210, 220))
        draw.ellipse([cx - 9, cy - 9, cx + 9, cy + 9], fill=(30, 34, 44))
        draw.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=(255, 80, 70))
        for i in range(5):
            draw.line([(cx - 22 + i * 11, cy - 14), (cx - 22 + i * 11, cy - 10)], fill=(200, 210, 220), width=2)
            draw.line([(cx - 22 + i * 11, cy + 10), (cx - 22 + i * 11, cy + 14)], fill=(200, 210, 220), width=2)
    elif theme == "trial":
        draw.rectangle(box, fill=(120, 100, 80))
        for i in range(4):
            px = x0 + 10 + i * (w - 20) / 4
            draw.rectangle([px, y0 + 14, px + 6, y1 - 10], fill=(235, 228, 210))
            draw.rectangle([px - 2, y0 + 10, px + 8, y0 + 14], fill=(235, 228, 210))
            draw.rectangle([px - 2, y1 - 10, px + 8, y1 - 6], fill=(235, 228, 210))
        draw.rectangle([x0 + 6, y0 + 6, x1 - 6, y0 + 10], fill=(235, 228, 210))
        draw.rectangle([x0 + 6, y1 - 6, x1 - 6, y1 - 2], fill=(235, 228, 210))
    else:
        draw.rectangle(box, fill=(200, 190, 170))
        draw.ellipse([cx - 10, y0 + 8, cx + 10, y0 + 28], fill=(230, 200, 120))
        draw.rectangle([x0, y1 - 12, x1, y1], fill=(90, 90, 90))

# ---------------------------------------------------------------- content
HEROES = [
    dict(n=1, tag="MARKETS · ASIA", theme="chart",
         head="Asian stocks rout as tariff threat returns",
         dek="MSCI Asia −2.3%; Seoul −5.3%, Taipei −5.1%, Nikkei −2.9%.",
         src="REUTERS", tier="CONFIRMED"),
    dict(n=2, tag="WAR · UKRAINE", theme="war",
         head="Russia's own figures count almost 500,000 war dead",
         dek="Moscow's own data: nearly half a million deaths.",
         src="BBC", tier="REPORTED"),
    dict(n=3, tag="POLITICS · USA", theme="politics",
         head="Democrats clinch 259 seats, biggest House majority since 1990",
         dek="Majority of at least 259 seats; largest in 30 years.",
         src="AP / NYT", tier="CONFIRMED"),
]
PANELS = [
    dict(n=4, tag="MIDDLE EAST · GAZA", theme="gaza",
         head="Israeli strike kills four of one family in Shati camp",
         dek="Strike hits an apartment west of Gaza City.",
         src="AL JAZEERA", tier="CONFIRMED"),
    dict(n=5, tag="TECH · NVIDIA", theme="chip",
         head="Attorney general dodges Nvidia questions as shares fall 7%",
         dek="Blanche downplays probe; Huang apologises.",
         src="BBC / NYT", tier="REPORTED"),
    dict(n=6, tag="ECONOMY · AUSTRALIA", theme="inflation",
         head="Australia inflation jumps to 4.9%",
         dek="CPI 4.9%; trimmed mean 3.8%; power +25%.",
         src="GUARDIAN", tier="CONFIRMED"),
    dict(n=7, tag="ASIA · INDONESIA", theme="mine",
         head="Rescuers hunt for 30 trapped in flooded Java mine",
         dek="Miners stuck 100 m down in Pongkor since Monday.",
         src="REUTERS", tier="REPORTED"),
    dict(n=8, tag="TECH · HUAWEI", theme="court",
         head="Huawei guilty of stealing trade secrets",
         dek="Trade-secret theft proven; racketeering acquitted.",
         src="BBC", tier="CONFIRMED"),
    dict(n=9, tag="SPACE · CHINA", theme="rocket",
         head="Chinese rocket lifts off with first Pakistani astronaut",
         dek="Pakistan's first astronaut rides a Chinese rocket.",
         src="BBC", tier="CONFIRMED"),
    dict(n=10, tag="USA · IMMIGRATION", theme="plane",
         head="Ábrego García to leave for Spain, ending 20-month ordeal",
         dek="Voluntary departure ends his 20-month ordeal.",
         src="BBC / NYT", tier="CONFIRMED"),
    dict(n=11, tag="TRADE · TARIFFS", theme="tariff",
         head="US set to unveil new tariffs on 16 trading partners",
         dek="Section 301 findings due; duties expected soon.",
         src="REUTERS", tier="REPORTED"),
    dict(n=12, tag="USA · IOWA", theme="blast",
         head="Army to blow up its lead azide stockpile on Wednesday",
         dek="Whole US stockpile detonated in Iowa Wednesday.",
         src="AP / NYT", tier="CONFIRMED"),
    dict(n=13, tag="BUSINESS · SHEIN", theme="fashion",
         head="Shein to pay $100m over FTC deception claims",
         dek="Settles claims it misled shoppers on shipping.",
         src="AP", tier="CONFIRMED"),
    dict(n=14, tag="SECURITY · CIA", theme="spy",
         head="Unclassified CIA system breached in cyberattack",
         dek="Unclassified information hit, AP source says.",
         src="AP / NYT", tier="REPORTED"),
    dict(n=15, tag="EUROPE · FRANCE", theme="trial",
         head="Sarkozy and Carla Bruni to face trial",
         dek="Ex-president and wife will stand trial.",
         src="BBC", tier="CONFIRMED"),
]
BRIEFS_A = [
    (16, "Sullivan concedes Alaska Senate race to Peltola", "NYT", "CONFIRMED"),
    (17, "Trump administration pauses joint operations with Ecuador", "NYT", "REPORTED"),
    (18, "Trump awards Rudy Giuliani the Presidential Medal of Freedom", "AP", "CONFIRMED"),
    (19, "Trump pardons turkeys Freedom and Feathers", "AP", "CONFIRMED"),
    (20, "Trump ballroom and other projects get $300m donation boost", "NYT", "REPORTED"),
    (21, "Appeals court gives Trump a path to erasing hush money conviction", "AP", "CONFIRMED"),
    (22, "House Democrat widens probe into Donald Trump Jr.'s investment firm", "AP", "REPORTED"),
    (23, "Senate passes bipartisan bill to speed power-plant permitting", "AP", "CONFIRMED"),
    (24, "Florida carries out its record 20th execution of the year", "AP", "CONFIRMED"),
    (25, "FAA pauses router installs linked to nationwide ground stop", "AP", "CONFIRMED"),
    (26, "Facebook, YouTube not liable for 2022 Buffalo shooting, court rules", "AP", "CONFIRMED"),
    (27, "US loses measles-free status as cases rise", "AP", "CONFIRMED"),
    (28, "Fiona the hippo dies at Cincinnati Zoo, aged 9", "AP", "CONFIRMED"),
    (29, "China-linked network used AI fakes to smear Taiwan election candidates", "BBC", "CLAIM"),
    (30, "Senegal reinstated as 2025 Africa Cup winners by court", "BBC", "CONFIRMED"),
    (31, "Nigerian monarch, 92, suspended after sexual assault claims", "BBC", "REPORTED"),
    (32, "Land mine casualties soar in Syria, two years after war", "BBC", "REPORTED"),
    (33, "Iran war costs put at $48.3bn, AP reports", "AP", "REPORTED"),
]
BRIEFS_B = [
    (34, "NATO chief vows defence against space threat after Russian satellite reports", "BBC", "REPORTED"),
    (35, "Record 5,200 heat-linked deaths estimated in England this year", "BBC", "REPORTED"),
    (36, "UK nuclear test veterans promised full truth; independent panel set up", "BBC", "CONFIRMED"),
    (37, "UK ministers ask public for views on changing age of consent", "BBC", "CONFIRMED"),
    (38, "Prince William meets Burnham on first Downing Street visit", "BBC", "CONFIRMED"),
    (39, "Huntley killer handed new whole-life jail term", "BBC", "CONFIRMED"),
    (40, "Firms backing Ukraine told to act now on sabotage risk", "BBC", "REPORTED"),
    (41, "German retirement reform could save 110,000 jobs, DIW study finds", "DIW", "REPORTED"),
    (42, "Climate Risk Index: extreme weather killed 800,000 in 30 years", "GERMANWATCH", "REPORTED"),
    (43, "Sinner has minor surgery on knee", "BBC", "REPORTED"),
    (44, "India Sensex jumps 1,382 to 83,818; Nifty up 408", "PTI", "CONFIRMED"),
    (45, "Rising food prices squeeze Indian households", "BBC", "REPORTED"),
    (46, "Hanoi hot-pot blast kills 6, injures more than a dozen", "NY POST", "REPORTED"),
    (47, "Russia sends home Chinese suspect in $2.3bn deposit case", "REUTERS", "REPORTED"),
    (48, "India and Netherlands agree shipping and green hydrogen pact", "PTI", "REPORTED"),
    (49, "Beau Lamarre guilty of Sydney double murder", "BBC", "CONFIRMED"),
    (50, "Gold $3,544.54 an ounce, down 0.3% ahead of US inflation data", "REUTERS", "CONFIRMED"),
    (51, "Brent crude $90.97 a barrel, down 0.5%", "REUTERS", "CONFIRMED"),
    (52, "Bitcoin $59,257, down 1%; ether $1,660", "REUTERS", "CONFIRMED"),
    (53, "Dollar steady; traders see 97% chance of December Fed hike", "REUTERS", "CONFIRMED"),
]
TIMELINE = [
    ("~00:30", "Australia inflation 4.9%", "6"),
    ("~00:56", "Russia's war dead ~500,000", "2"),
    ("~02:59", "Huawei guilty", "8"),
    ("~03:28", "China rocket lifts off", "9"),
    ("~04:13", "Shati strike kills four", "4"),
    ("~04:49", "Ábrego García leaves", "10"),
    ("~05:00", "Seoul −5.3% rout", "1"),
]
DATECHECK = [
    "Hamas security chief killed in Gaza strike — Tue 24 Nov",
    "Iran: four tankers hit mines in Hormuz — Tue 24 Nov",
    "China probes Politburo's Chen Jining — Tue 24 Nov",
    "US consumer confidence jumps to 103.3 — Tue 24 Nov",
    "Real Madrid 5–1 PSV; Arsenal 1–1 — Tue 24 Nov",
    "Microsoft declares 'Code Red' after outage — Tue 24 Nov",
    "Gaza meningitis alert, 272 cases in October — Tue 24 Nov",
    "UK sanctions Yemen's Houthis — Tue 24 Nov",
    "Pope Leo XIV hit by a rosary in Lima — Mon 24 Nov",
    "Robert Pattinson to play James Bond — Mon 24 Nov",
    "FIFA picks US bid for 2031 Women's Cup — Sun 23 Nov",
    "Macy's Thanksgiving Parade turns 100 — Thu 26 Nov",
]
PINS = [
    (1, 127, 37, 0, 0), (2, 32, 50, 0, 0), (3, -77, 39, 0, 0),
    (4, 34.5, 31.5, 0, 0), (5, -122, 37.4, 0, 0), (6, 149, -35, 0, 0),
    (7, 106.8, -6.6, 0, 0), (8, 114, 22.5, 0, -4), (9, 98.5, 41, 0, 0),
    (10, -3.7, 40.4, 0, 0), (11, 116, 39.9, 0, 5), (12, -93.6, 41.6, 0, 0),
    (13, 103.8, 1.35, 0, 0), (14, -77.15, 38.95, 8, -8), (15, 2.35, 48.85, 0, 0),
]
CONTINENTS = {
    "NAM": [(-168, 66), (-140, 70), (-125, 72), (-110, 73), (-95, 80), (-85, 70), (-75, 62), (-65, 60), (-55, 52), (-60, 47), (-70, 44), (-75, 39), (-80, 32), (-85, 30), (-90, 21), (-97, 16), (-95, 19), (-105, 20), (-110, 24), (-117, 33), (-125, 40), (-125, 49), (-135, 58), (-155, 58), (-165, 60)],
    "SAM": [(-80, 10), (-75, 11), (-70, 12), (-62, 10), (-52, 5), (-50, 0), (-44, -3), (-35, -8), (-40, -20), (-48, -28), (-58, -38), (-65, -45), (-70, -54), (-73, -50), (-73, -40), (-72, -30), (-70, -20), (-75, -15), (-80, -5), (-81, 0)],
    "EUR": [(-10, 36), (-9, 43), (-2, 48), (0, 50), (3, 52), (8, 55), (8, 58), (12, 56), (18, 56), (21, 55), (24, 58), (28, 60), (30, 62), (25, 66), (20, 70), (15, 70), (10, 64), (5, 60), (-5, 58), (-10, 52), (-10, 43)],
    "AFR": [(-17, 15), (-15, 20), (-10, 31), (0, 36), (10, 37), (20, 32), (30, 31), (32, 31), (35, 28), (40, 15), (43, 11), (48, 11), (51, 10), (44, 0), (40, -10), (35, -20), (32, -28), (26, -34), (19, -35), (15, -27), (12, -18), (13, -10), (9, 4), (-8, 4), (-13, 8), (-17, 12)],
    "ASI": [(30, 62), (40, 68), (55, 69), (70, 72), (90, 75), (110, 76), (130, 72), (150, 70), (170, 66), (178, 65), (170, 60), (162, 56), (158, 52), (142, 50), (140, 40), (130, 35), (127, 35), (122, 30), (120, 25), (110, 20), (108, 12), (105, 9), (100, 8), (98, 15), (95, 16), (92, 21), (88, 22), (80, 15), (77, 8), (75, 12), (72, 20), (66, 25), (60, 25), (57, 27), (52, 28), (48, 30), (44, 29), (40, 31), (36, 36), (33, 36), (30, 36), (27, 37), (23, 36), (26, 40), (28, 45), (30, 50), (30, 55), (28, 60)],
    "AUS": [(113, -22), (114, -30), (115, -35), (120, -34), (124, -33), (129, -32), (132, -32), (135, -35), (138, -35), (140, -38), (145, -38), (150, -37), (153, -32), (153, -27), (150, -22), (146, -19), (142, -15), (142, -11), (137, -12), (135, -15), (132, -12), (130, -13), (126, -14), (122, -17), (118, -20)],
    "IDN": [(95, 5), (100, 0), (104, -3), (106, -6), (110, -7), (114, -8), (119, -9), (120, -10), (119, -5), (120, -1), (122, 1), (126, 1), (128, -2), (131, -3), (136, -4), (140, -5), (141, -8), (138, -8), (135, -4), (132, -1), (128, 1), (124, 1), (120, 0), (117, -2), (114, -3), (110, -1), (106, 2), (102, 4), (98, 5)],
    "JPN": [(130, 31), (132, 33), (134, 34), (137, 35), (139, 36), (140, 38), (141, 41), (143, 42), (145, 44), (143, 44), (141, 40), (139, 37), (136, 35), (133, 34), (131, 32)],
    "GBR": [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (1, 53), (1, 51), (-2, 50)],
}

# ---------------------------------------------------------------- render
def render():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    MX = 10
    cw = (W - 2 * MX - 16) // 3  # 329

    # ---- masthead (0..100)
    d.line([(MX, 6), (W - MX, 6)], fill=INK, width=2)
    spaced(d, W // 2, 10, "THE DAY IN WORLD NEWS", F_TAG(11), RED, 4)
    d.text((W // 2, 22), "The World on One Page", font=F_TITLE(40), fill=INK, anchor="ma")
    d.line([(MX, 78), (W - MX, 78)], fill=RULE, width=1)
    d.text((MX, 82), "Wednesday 25 November 2026", font=F_HEAD(13), fill=INK)
    d.text((W - MX, 82), "53 STORIES  ·  7 REGIONS  ·  20 FIELDS  ·  ALL FROM WEDNESDAY",
           font=F_TAG(11), fill=RED, anchor="ra")
    d.line([(MX, 100), (W - MX, 100)], fill=INK, width=2)

    # ---- heroes (106..226, 120 tall)
    hy, hh = 106, 120
    for i, h in enumerate(HEROES):
        x0 = MX + i * (cw + 8)
        x1 = x0 + cw
        scene(d, (x0, hy, x1, hy + 44), h["theme"])
        badge(d, x0 + 14, hy + 13, 11, h["n"])
        d.text((x0 + 2, hy + 47), h["tag"], font=F_TAG(9), fill=RED)
        lines = wrap(d, h["head"], F_HEAD(15), cw - 4)
        if len(lines) > 2:
            WARN.append(f"hero {h['n']} headline {len(lines)} lines")
        y = draw_lines(d, lines[:2], x0 + 2, hy + 58, F_HEAD(15), INK, 17)
        dlines = wrap(d, h["dek"], F_BODY(11), cw - 4)
        if len(dlines) > 2:
            WARN.append(f"hero {h['n']} dek {len(dlines)} lines")
        draw_lines(d, dlines[:2], x0 + 2, y + 1, F_BODY(11), (60, 58, 52), 13)
        d.text((x0 + 2, hy + hh - 12), f"{h['tier']} · {h['src']}", font=F_TAG(9), fill=TIER_FILL[h["tier"]])
    d.line([(MX, 232), (W - MX, 232)], fill=RULE, width=1)

    # ---- panels (238..542, 4 rows x 74 tall, gap 4)
    py, ph = 238, 74
    for r in range(4):
        for c in range(3):
            p = PANELS[r * 3 + c]
            x0 = MX + c * (cw + 8)
            x1 = x0 + cw
            y0 = py + r * (ph + 4)
            d.rectangle([x0, y0, x1, y0 + ph], outline=RULE, width=1)
            scene(d, (x0 + 1, y0 + 1, x0 + 70, y0 + ph - 1), p["theme"])
            badge(d, x0 + 13, y0 + 13, 10, p["n"])
            tx = x0 + 76
            tw = cw - 80
            d.text((tx, y0 + 3), p["tag"], font=F_TAG(8), fill=RED)
            lines = wrap(d, p["head"], F_HEAD(12), tw)
            if len(lines) > 2:
                WARN.append(f"panel {p['n']} headline {len(lines)} lines: {lines}")
            y = draw_lines(d, lines[:2], tx, y0 + 14, F_HEAD(12), INK, 13)
            dlines = wrap(d, p["dek"], F_BODY(10), tw)
            if len(dlines) > 2:
                WARN.append(f"panel {p['n']} dek {len(dlines)} lines")
            draw_lines(d, dlines[:2], tx, y + 1, F_BODY(10), (60, 58, 52), 11)
            d.text((tx, y0 + ph - 12), f"{p['tier']} · {p['src']}", font=F_TAG(8), fill=TIER_FILL[p["tier"]])

    # ---- briefs (548..790)
    by = 548
    d.line([(MX, by), (W - MX, by)], fill=INK, width=2)
    d.text((MX, by + 4), "ALSO ON WEDNESDAY 25 NOVEMBER", font=F_TAG(11), fill=INK)
    d.text((W - MX, by + 4), "EVERY BRIEF CARRIES ITS SOURCE AND ITS TIER", font=F_TAG(9), fill=GREY, anchor="ra")
    colw = (W - 2 * MX - 16) // 2  # 494
    bh = by + 24
    ends = []
    for ci, (title, items) in enumerate([
            ("AMERICAS · AFRICA · MIDDLE EAST — 18", BRIEFS_A),
            ("EUROPE · ASIA · OCEANIA · MARKETS — 20", BRIEFS_B)]):
        x0 = MX + ci * (colw + 16)
        d.text((x0, bh), title, font=F_TAG(10), fill=RED)
        y = bh + 15
        f_b, f_s = F_BODY(10), F_TAG(8)
        for (n, txt, src, tier) in items:
            tf = TIER_FILL[tier]
            d.rectangle([x0, y + 1, x0 + 15, y + 12], fill=tf)
            tw = d.textlength(str(n), font=F_TAG(8))
            d.text((x0 + (15 - tw) / 2, y + 2), str(n), font=F_TAG(8), fill=(255, 255, 255))
            avail = colw - 19 - d.textlength(src, font=f_s) - 4
            lines = wrap(d, txt, f_b, avail)
            if len(lines) > 1:
                WARN.append(f"brief {n} wraps to {len(lines)} lines")
            d.text((x0 + 19, y), lines[0], font=f_b, fill=INK)
            d.text((x0 + 19 + d.textlength(lines[0], font=f_b) + 3, y + 1), src, font=f_s, fill=GREY)
            y += 10
        ends.append(y)
    briefs_end = max(ends)

    # ---- timeline strip (briefs_end+4 .. +58)
    ty = briefs_end + 4
    d.line([(MX, ty), (W - MX, ty)], fill=INK, width=1)
    d.text((MX, ty + 4), "THE DAY IN UTC", font=F_TAG(10), fill=INK)
    axis_y = ty + 30
    d.line([(MX + 30, axis_y), (W - MX - 10, axis_y)], fill=INK, width=1)
    d.text((MX + 30, axis_y + 3), "00:00", font=F_SMALL(8), fill=GREY)
    d.text((W - MX - 10, axis_y + 3), "05:00 UTC", font=F_SMALL(8), fill=GREY, anchor="ra")
    for i, (tm, label, num) in enumerate(TIMELINE):
        fx = MX + 60 + i * ((W - 2 * MX - 110) / 6)
        d.ellipse([fx - 3, axis_y - 3, fx + 3, axis_y + 3], fill=RED)
        d.text((fx, axis_y - 24), tm, font=F_TAG(8), fill=RED, anchor="ma")
        d.text((fx, axis_y + 13), label, font=F_BODY(9), fill=INK, anchor="ma")
    timeline_end = axis_y + 26

    # ---- map + date check (timeline_end+6 .. 992)
    my = timeline_end + 6
    map_w = 470
    d.line([(MX, my), (W - MX, my)], fill=INK, width=1)
    d.text((MX, my + 4), "WHERE IT HAPPENED", font=F_TAG(10), fill=INK)
    d.text((MX + map_w + 16, my + 4), "DATE CHECK — HELD BACK, WITH REAL DATES", font=F_TAG(10), fill=INK)
    map_y0 = my + 18
    map_y1 = 978
    map_box = (MX, map_y0, MX + map_w, map_y1)
    d.rectangle(map_box, outline=RULE, width=1, fill=(233, 230, 218))
    mw, mhh = map_w, map_y1 - map_y0
    def proj(lon, lat):
        return (map_box[0] + (lon + 180) / 360 * mw,
                map_box[1] + (75 - lat) / 132 * mhh)
    for name, pts in CONTINENTS.items():
        d.polygon([proj(lon, lat) for lon, lat in pts], fill=(196, 188, 168), outline=(150, 142, 126))
    for (n, lon, lat, nx, ny) in PINS:
        px, py2 = proj(lon, lat)
        px += nx
        py2 += ny
        if n == 14:
            ox, oy = proj(-77, 39)
            d.line([(ox, oy), (px, py2)], fill=GREY, width=1)
        badge(d, px, py2, 7, n)
    d.text((MX, 982), "PINS BY REGION — N. AMERICA 5 · S. AMERICA 1 · EUROPE 2 · AFRICA 0 · M. EAST 1 · ASIA 7 · OCEANIA 1",
           font=F_SMALL(8), fill=GREY)
    # date check, two columns of 6
    dx = MX + map_w + 16
    dcw = W - MX - dx
    half = dcw // 2
    f_dc = F_BODY(9)
    for i, item in enumerate(DATECHECK):
        col, row = i // 6, i % 6
        x = dx + col * half
        y = map_y0 + 2 + row * 13
        d.text((x, y), "×", font=F_BODY(10), fill=RED)
        lines = wrap(d, item, f_dc, half - 12)
        if len(lines) > 1:
            WARN.append(f"datecheck {i} wraps: {lines}")
        d.text((x + 11, y + 1), lines[0], font=f_dc, fill=(70, 66, 58))

    # ---- footer
    d.line([(MX, 996), (W - MX, 996)], fill=INK, width=1)
    d.text((MX, 1001), "Every story here happened or was first reported on Wednesday 25 November 2026.   "
                        "■ CONFIRMED   ■ REPORTED   ■ CLAIM = one side's account, not independently confirmed.",
             font=F_SMALL(9), fill=INK)
    d.text((MX, 1012), "Sources: Reuters, AP, BBC, NYT, Guardian, Al Jazeera, PTI, NY Post, Variety, DIW, Germanwatch.   Original drawings.",
             font=F_SMALL(9), fill=GREY)

    out = sys.argv[1] if len(sys.argv) > 1 else "entry.png"
    img.save(out, optimize=True)
    print("saved", out)
    for w in WARN:
        print("WARN:", w)
    print("briefs_end", briefs_end, "timeline_end", timeline_end, "map_y", my, "map_h", map_y1 - map_y0)

if __name__ == "__main__":
    render()
