#!/usr/bin/env python3
"""news-23 b9 numbers-led: draws THE WORLD TODAY, Monday 23 November 2026.
Numbers are the hero: a 2x5 grid of giant figures on top, then 3 hero
scenes, 10 small cards, world map + 31 numbered pins, ALSO list, DATE CHECK.
Drawn with PIL only. Output: entry.png 1024x1024, < 1 MiB."""
import math
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
M = 14  # margin
PAPER = (247, 242, 231)
INK = (26, 26, 26)
RED = (176, 30, 36)
NAVY = (16, 32, 64)
GRAY = (110, 108, 100)
LIGHT = (232, 226, 210)
MAP_BG = (206, 224, 232)
LAND = (232, 220, 188)
LAND_LINE = (190, 175, 140)

F_SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
F_SERIF_IT = "/usr/share/fonts/truetype/liberation/LiberationSerif-BoldItalic.ttf"
F_SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
F_SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

REGIONS = [
    ("NORTH AMERICA", 8, (43, 94, 167)),
    ("EUROPE", 6, (201, 106, 30)),
    ("MIDDLE EAST", 6, (122, 63, 160)),
    ("ASIA-PACIFIC", 6, (30, 138, 110)),
    ("AFRICA", 3, (138, 109, 30)),
    ("WORLD", 2, (85, 85, 85)),
]
CHIP = {
    "REPORTED": (30, 122, 52),
    "CLAIM": (185, 127, 16),
    "ONGOING": (43, 94, 167),
    "DENIAL": (110, 110, 110),
}

def font(path, size):
    return ImageFont.truetype(path, size)

def tw(draw, text, f):
    b = draw.textbbox((0, 0), text, font=f)
    return b[2] - b[0]

def wrap(draw, text, f, width):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if tw(draw, t, f) <= width:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

def draw_lines(draw, lines, x, y, f, fill, lh, max_lines=None):
    if max_lines is not None:
        lines = lines[:max_lines]
    for ln in lines:
        draw.text((x, y), ln, font=f, fill=fill)
        y += lh
    return y

def chip(draw, x, y, label):
    f = font(F_SANS_B, 9)
    w = tw(draw, label, f) + 10
    c = CHIP[label]
    draw.rounded_rectangle([x, y, x + w, y + 13], radius=3, fill=c)
    draw.text((x + 5, y + 2), label, font=f, fill=(255, 255, 255))
    return w

# ---------------- world map ----------------
CONTINENTS = [
    # North America
    [(-168, 66), (-155, 71), (-140, 70), (-125, 71), (-110, 73), (-95, 80),
     (-85, 76), (-80, 73), (-76, 62), (-70, 58), (-65, 50), (-70, 44),
     (-75, 39), (-80, 32), (-81, 26), (-85, 29), (-90, 21), (-97, 26),
     (-105, 20), (-110, 23), (-117, 33), (-125, 40), (-125, 49),
     (-132, 58), (-145, 60), (-158, 58), (-168, 60)],
    # South America
    [(-80, 10), (-75, 11), (-70, 12), (-62, 9), (-55, 6), (-50, 0),
     (-44, -5), (-38, -8), (-35, -15), (-40, -22), (-48, -28),
     (-55, -35), (-62, -41), (-68, -50), (-70, -54), (-73, -45),
     (-73, -35), (-72, -20), (-75, -15), (-80, -5), (-81, 0)],
    # Europe
    [(-10, 36), (-9, 43), (-2, 44), (0, 46), (3, 51), (5, 53), (8, 57),
     (12, 55), (18, 56), (21, 55), (24, 58), (28, 60), (30, 62),
     (25, 65), (20, 68), (15, 70), (10, 70), (6, 62), (5, 60),
     (-2, 57), (-6, 58), (-10, 54), (-10, 50), (-10, 43)],
    # Africa
    [(-17, 15), (-16, 20), (-13, 27), (-10, 31), (-5, 35), (0, 36),
     (10, 37), (15, 32), (20, 32), (25, 31), (30, 31), (32, 28),
     (35, 27), (39, 21), (43, 12), (48, 11), (51, 10), (48, 2),
     (42, -3), (40, -10), (36, -18), (33, -26), (28, -33), (20, -35),
     (17, -30), (15, -25), (13, -18), (12, -10), (10, -5), (9, 0),
     (9, 4), (5, 4), (-8, 5), (-13, 8), (-17, 11)],
    # Asia
    [(30, 62), (35, 65), (45, 68), (55, 69), (65, 70), (75, 72),
     (90, 75), (105, 77), (120, 73), (135, 72), (150, 70), (162, 68),
     (170, 66), (178, 65), (170, 60), (162, 58), (156, 51), (150, 45),
     (142, 42), (140, 38), (132, 34), (127, 33), (122, 28), (118, 24),
     (110, 20), (108, 15), (105, 9), (100, 6), (97, 10), (92, 16),
     (90, 22), (86, 20), (80, 13), (77, 8), (75, 12), (72, 20),
     (66, 25), (60, 25), (56, 26), (52, 27), (50, 29), (48, 30),
     (44, 29), (42, 31), (38, 34), (36, 36), (33, 36), (30, 36),
     (28, 40), (27, 41), (23, 40), (26, 45), (28, 48), (30, 55)],
    # Australia
    [(113, -22), (118, -20), (122, -14), (127, -14), (132, -12),
     (137, -12), (142, -11), (146, -19), (150, -22), (153, -27),
     (153, -32), (150, -37), (145, -38), (140, -38), (135, -35),
     (130, -32), (125, -32), (120, -34), (115, -32), (113, -26)],
]

# story number -> (lon, lat, color key)
PINS = {
    1: (127, 37.5, "R"), 2: (-59.6, 13.1, "R"), 3: (-150, -35, "R"),
    4: (-74, 40.7, "R"), 5: (-122, 37.8, "R"), 6: (19, 52, "C"),
    7: (37.6, 55.7, "C"), 8: (2.35, 48.85, "R"), 9: (-2.24, 53.48, "R"),
    10: (30.5, 50.45, "C"), 11: (30.7, 36.9, "R"), 12: (20.07, 32.1, "C"),
    13: (34.8, 31, "O"), 14: (34.45, 31.5, "R"), 15: (35.2, 31.9, "R"),
    16: (51.4, 35.7, "R"), 17: (35.5, 33.9, "R"), 18: (50.55, 26.2, "R"),
    19: (32.5, 15.6, "R"), 20: (30, 1, "R"), 21: (-77, 38.9, "R"),
    22: (90.4, 23.8, "R"), 23: (127, 37.5, "R"), 24: (127, 37.5, "R"),
    25: (116.4, 39.9, "R"), 26: (127, 37.5, "R"), 27: (-77, 38.9, "R"),
    28: (-77, 38.9, "R"), 29: (-77, 38.9, "R"), 30: (-74, 40.7, "R"),
    31: (-105, 39.7, "R"),
}
# manual cluster offsets (dx, dy) in px
OFF = {1: (-8, -8), 4: (-20, -14), 7: (8, -8), 9: (-10, -6), 11: (6, 10),
       13: (-18, 12), 14: (14, -8), 15: (16, 8), 16: (8, -8),
       17: (-14, -10), 18: (6, 6), 21: (6, -12), 23: (10, -6),
       24: (-10, 8), 26: (12, 10), 27: (-16, 2), 28: (18, -2),
       29: (-2, 12), 30: (24, 14), 25: (-14, 10)}
PIN_FILL = {"R": (176, 30, 36), "C": (185, 127, 16), "O": (43, 94, 167)}

def project(mx0, my0, mw, mh, lon, lat):
    x = mx0 + (lon + 180) / 360.0 * mw
    y = my0 + (75 - lat) / 130.0 * mh
    return x, y

def draw_map(draw, mx0, my0, mw, mh):
    draw.rectangle([mx0, my0, mx0 + mw, my0 + mh], fill=MAP_BG,
                   outline=(160, 180, 190))
    for gx in range(0, 361, 30):
        x = mx0 + gx / 360.0 * mw
        draw.line([(x, my0), (x, my0 + mh)], fill=(190, 208, 218))
    for gy in range(0, 131, 30):
        y = my0 + gy / 130.0 * mh
        draw.line([(mx0, y), (mx0 + mw, y)], fill=(190, 208, 218))
    for poly in CONTINENTS:
        pts = [project(mx0, my0, mw, mh, lo, la) for lo, la in poly]
        draw.polygon(pts, fill=LAND, outline=LAND_LINE)
    # pins
    pts = {}
    for n, (lon, lat, k) in PINS.items():
        x, y = project(mx0, my0, mw, mh, lon, lat)
        dx, dy = OFF.get(n, (0, 0))
        pts[n] = (x + dx, y + dy)
    # distance check
    worst = 99
    for a in pts:
        for b in pts:
            if a < b:
                d = math.hypot(pts[a][0] - pts[b][0], pts[a][1] - pts[b][1])
                worst = min(worst, d)
                if d < 14:
                    print(f"PIN WARN: {a}-{b} only {d:.1f}px apart")
    print(f"pin min distance: {worst:.1f}px")
    f = font(F_SANS_B, 8)
    for n, (x, y) in pts.items():
        fill = PIN_FILL[PINS[n][2]]
        draw.ellipse([x - 7, y - 7, x + 7, y + 7], fill=fill,
                     outline=(255, 255, 255))
        t = str(n)
        draw.text((x - tw(draw, t, f) / 2, y - 5), t, font=f,
                  fill=(255, 255, 255))
    draw.text((mx0 + 2, my0 + mh - 12), "N \u2191", font=font(F_SANS_B, 9),
              fill=INK)

def scene_kospi(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=NAVY)
    # skyline
    import random
    rnd = random.Random(7)
    base = y + h - 8
    bx = x + 6
    while bx < x + w - 14:
        bw = rnd.randint(10, 18)
        bh = rnd.randint(18, 52)
        draw.rectangle([bx, base - bh, bx + bw, base], fill=(30, 48, 84))
        for wy in range(int(base - bh) + 4, int(base) - 4, 7):
            for wx in range(int(bx) + 2, int(bx + bw) - 2, 6):
                if rnd.random() < 0.5:
                    draw.rectangle([wx, wy, wx + 2, wy + 3],
                                   fill=(255, 214, 90))
        bx += bw + 3
    # falling chart
    pts = [(x + 12, y + 34), (x + 62, y + 26), (x + 112, y + 38),
           (x + 162, y + 30), (x + 212, y + 52), (x + 262, y + 66),
           (x + 308, y + 88)]
    draw.line(pts, fill=(255, 90, 80), width=3)
    for px, py in pts:
        draw.ellipse([px - 3, py - 3, px + 3, py + 3], fill=(255, 255, 255),
                     outline=(255, 90, 80))
    draw.text((x + 8, y + 6), "intraday -5.8%", font=font(F_SANS, 11),
              fill=(200, 210, 230))
    draw.text((x + w - 118, y + 4), "-3.3%", font=font(F_SANS_B, 34),
              fill=(255, 90, 80))

def scene_guterres(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=NAVY)
    # globe
    cx, cy, r = x + 78, y + 58, 42
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(70, 130, 200),
                 outline=(180, 210, 240))
    for k in range(-2, 3):
        rx = r * abs(k) / 3.0
        draw.ellipse([cx - rx, cy - r, cx + rx, cy + r],
                     outline=(180, 210, 240))
    draw.line([(cx - r, cy), (cx + r, cy)], fill=(180, 210, 240))
    draw.line([(cx, cy - r), (cx, cy + r)], fill=(180, 210, 240))
    # network
    import random
    rnd = random.Random(11)
    nodes = []
    for _ in range(9):
        nodes.append((x + 150 + rnd.randint(0, 150),
                      y + 12 + rnd.randint(0, 84)))
    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            if math.hypot(nodes[i][0] - nodes[j][0],
                          nodes[i][1] - nodes[j][1]) < 62:
                draw.line([nodes[i], nodes[j]], fill=(120, 160, 210))
    for nx, ny in nodes:
        draw.ellipse([nx - 4, ny - 4, nx + 4, ny + 4],
                     fill=(255, 214, 90), outline=(255, 255, 255))
    # podium silhouette
    draw.rectangle([x + w - 52, y + h - 34, x + w - 14, y + h - 6],
                   fill=(10, 18, 36))
    draw.ellipse([x + w - 40, y + h - 52, x + w - 26, y + h - 34],
                 fill=(10, 18, 36))
    draw.rectangle([x + 8, y + 6, x + 122, y + 24], fill=(255, 214, 90))
    draw.text((x + 13, y + 9), "150 DELEGATES", font=font(F_SANS_B, 11),
              fill=(26, 26, 26))

def scene_power(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(238, 234, 222))
    draw.text((x + 10, y + 8), "ASIA POWER INDEX 2026",
              font=font(F_SANS_B, 13), fill=INK)
    rows = [("US", 78.9, (43, 94, 167)), ("CHINA", 73.6, (176, 30, 36)),
            ("INDIA", 40.5, (140, 140, 140))]
    yy = y + 30
    for name, val, col in rows:
        draw.text((x + 10, yy), name, font=font(F_SANS_B, 12), fill=INK)
        bx = x + 78
        bw = (w - 78 - 58) * val / 85.0
        draw.rectangle([bx, yy + 1, bx + bw, yy + 15], fill=col)
        draw.text((bx + bw + 5, yy), f"{val}", font=font(F_SANS_B, 12),
                  fill=INK)
        yy += 19
    draw.text((x + 10, y + h - 20), "GAP 5.3",
              font=font(F_SANS_B, 18), fill=RED)
    draw.text((x + 92, y + h - 16), "narrowest since 2018",
              font=font(F_SANS, 11), fill=INK)

def hero_block(draw, x, y, w, scene_fn, kicker, kcolor, title, body,
               source, chip_label):
    scene_fn(draw, x, y, w, 108)
    yy = y + 114
    draw.text((x, yy), kicker, font=font(F_SANS_B, 10), fill=kcolor)
    yy += 13
    tf = font(F_SANS_B, 13)
    tl = wrap(draw, title, tf, w)
    yy = draw_lines(draw, tl, x, yy, tf, INK, 15, max_lines=2)
    if len(tl) > 2:
        print(f"HERO TITLE OVERFLOW: {title}")
    bf = font(F_SANS, 10)
    bl = wrap(draw, body, bf, w)
    yy = draw_lines(draw, bl, x, yy + 2, bf, INK, 12, max_lines=2)
    if len(bl) > 2:
        print(f"HERO BODY OVERFLOW: {body[:40]}")
    yy += 3
    draw.text((x, yy), "Source: " + source, font=font(F_SANS, 9),
              fill=GRAY)
    chip(draw, x + w - 74, yy - 1, chip_label)

def card(draw, x, y, w, h, num, kicker, kcolor, title, body, source,
         chip_label):
    draw.rectangle([x, y, x + w, y + h], fill=(255, 255, 255),
                   outline=(200, 192, 172))
    draw.rectangle([x, y, x + w, y + 16], fill=kcolor)
    draw.text((x + 6, y + 3), f"#{num} {kicker}", font=font(F_SANS_B, 9),
              fill=(255, 255, 255))
    tf = font(F_SANS_B, 11)
    tl = wrap(draw, title, tf, w - 12)
    yy = draw_lines(draw, tl, x + 6, y + 20, tf, INK, 13, max_lines=2)
    if len(tl) > 2:
        print(f"CARD {num} TITLE OVERFLOW: {title}")
    bf = font(F_SANS, 10)
    bl = wrap(draw, body, bf, w - 12)
    yy = draw_lines(draw, bl, x + 6, yy + 1, bf, INK, 12, max_lines=2)
    if len(bl) > 2:
        print(f"CARD {num} BODY OVERFLOW: {body[:40]}")
    sy = y + h - 15
    draw.text((x + 6, sy), source, font=font(F_SANS, 8), fill=GRAY)
    chip(draw, x + w - 76, sy - 1, chip_label)

def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 6], fill=RED)

    # ---- masthead ----
    d.text((M, 12), "THE WORLD TODAY", font=font(F_SERIF, 50), fill=INK)
    d.text((W - M - tw(d, "31 STORIES", font(F_SANS_B, 16)), 14),
           "31 STORIES", font=font(F_SANS_B, 16), fill=INK)
    d.text((W - M - tw(d, "6 REGIONS", font(F_SANS_B, 16)), 34),
           "6 REGIONS", font=font(F_SANS_B, 16), fill=INK)
    d.text((M, 66), "MONDAY 23 NOVEMBER 2026", font=font(F_SANS_B, 19),
           fill=RED)
    d.text((W - M - tw(d, "AI ROUT \u00b7 AI RULES \u00b7 POWER SHIFT",
                       font(F_SANS, 11)), 70),
           "AI ROUT \u00b7 AI RULES \u00b7 POWER SHIFT", font=font(F_SANS, 11),
           fill=GRAY)
    d.line([(M, 88), (W - M, 88)], fill=INK, width=2)

    # ---- giant number grid 2x5 ----
    nums = [
        ("-3.3%", "Kospi rout", "Seoul sheds 161 pts"),
        ("5.3", "US\u2013China gap", "narrowest since 2018"),
        ("11,762", "Ebola cases", "DRC outbreak"),
        ("10T won", "Seoul fund", "market stabilisation"),
        ("2%", "Billionaire tax", "Paris backs plan"),
        ("$450M", "Skubal deal", "Mets, nine years"),
        ("165", "Russian missiles", "fired in a week"),
        ("12,000", "Manchester", "cleared after scare"),
        ("264 kg", "Explosives", "seized in Lebanon"),
        ("$107.3B", "Anthropic IPO", "largest ever"),
    ]
    cw = (W - 2 * M) / 5.0
    nf = font(F_SANS_B, 28)
    cf = font(F_SANS_B, 11)
    sf = font(F_SANS, 10)
    for i, (num, cap, sub) in enumerate(nums):
        col, row = i % 5, i // 5
        x = M + col * cw
        y = 94 + row * 58
        d.text((x + 4, y), num, font=nf, fill=RED)
        d.text((x + 4, y + 32), cap, font=cf, fill=INK)
        d.text((x + 4, y + 45), sub, font=sf, fill=GRAY)
        if col:
            d.line([(x, y - 2), (x, y + 56)], fill=(210, 202, 182))
    d.line([(M, 210), (W - M, 210)], fill=(210, 202, 182))

    # ---- region bar ----
    total = sum(c for _, c, _ in REGIONS)
    x = M
    bw = W - 2 * M
    for name, cnt, col in REGIONS:
        wseg = bw * cnt / total
        d.rectangle([x, 214, x + wseg - 1, 232], fill=col)
        label = f"{name} {cnt}"
        f = font(F_SANS_B, 10)
        d.text((x + (wseg - tw(d, label, f)) / 2, 218), label, font=f,
               fill=(255, 255, 255))
        x += wseg

    # ---- UTC strip ----
    d.rectangle([M, 236, W - M, 254], fill=NAVY)
    utc = ("THE DAY IN UTC  \u00b7  ~00:00 ASIA OPENS  \u00b7  06:30 KOSPI -3.3%  "
           "\u00b7  ~09:00 SEOUL FUND  \u00b7  14:30 WALL ST +3%  \u00b7  "
           "~16:00 GUTERRES  \u00b7  ~21:00 FBI HACK  (~ = APPROX.)")
    uf = font(F_SANS, 11)
    d.text(((W - tw(d, utc, uf)) / 2, 240), utc, font=uf,
           fill=(255, 255, 255))

    # ---- 3 hero scenes ----
    hw = (W - 2 * M - 2 * 10) / 3.0
    hx = [M, M + hw + 10, M + 2 * (hw + 10)]
    hero_block(d, hx[0], 260, hw, scene_kospi, "#1 ASIA \u00b7 MARKETS",
               (43, 94, 167), "AI ROUT HITS ASIA",
               "Kospi closes 4,708.54, sheds 161 pts. Samsung -3.1%, "
               "SK Hynix -2.5%. AI sell-off spreads from Wall Street.",
               "Yonhap \u00b7 Korea JoongAng", "REPORTED")
    hero_block(d, hx[1], 260, hw, scene_guterres,
               "#2 WORLD \u00b7 UNITED NATIONS", (122, 63, 160),
               "GUTERRES: REGULATE AI BEFORE IT'S TOO LATE",
               "UN chief urges global AI safety rules at the Bridgetown "
               "summit; 150 delegates back a risk framework.",
               "UN News \u00b7 Reuters", "REPORTED")
    hero_block(d, hx[2], 260, hw, scene_power,
               "#3 ASIA-PACIFIC \u00b7 POWER", (30, 138, 110),
               "US LEAD OVER CHINA AT RECORD LOW",
               "Gap 5.3 narrowest since 2018. US diplomatic influence -6 "
               "to 76.7. India third at 40.5.",
               "Lowy Institute", "REPORTED")

    # ---- 10 small cards, 2 rows x 5 ----
    cards = [
        (4, "SPORT \u00b7 US", (43, 94, 167), "Skubal signs $450M Mets deal",
         "Two-time Cy Young winner, nine years \u2014 a record for a pitcher.", "ESPN", "REPORTED"),
        (5, "TECH \u00b7 US", (43, 94, 167),
         "Anthropic IPO: $107.3B, largest ever",
         "Claude maker raised at $83 a share on 19 Nov; debut close "
         "$97.17.", "Bloomberg", "REPORTED"),
        (6, "EUROPE \u00b7 WAR", (201, 106, 30),
         "Poland: 3 Russian missiles crossed airspace",
         "Kyiv says three Kh-101 entered Poland on Friday; Tusk: "
         "provocation.", "AP", "CLAIM"),
        (7, "EUROPE \u00b7 SECURITY", (201, 106, 30),
         "Intel warns of Russian nuclear satellite",
         "Moscow built a satellite to carry a nuclear warhead.", "Bloomberg", "CLAIM"),
        (8, "EUROPE \u00b7 ECONOMY", (201, 106, 30),
         "Paris: 100+ back 2% billionaire tax",
         "Economists, politicians, unions rally behind France's 2% "
         "wealth tax.", "AFP", "REPORTED"),
        (9, "EUROPE \u00b7 UK", (201, 106, 30),
         "Manchester: 12,000 cleared after scare",
         "Substance scare empties arena district; no casualties "
         "reported.", "AP", "REPORTED"),
        (10, "EUROPE \u00b7 WAR", (201, 106, 30),
         "Zelenskyy: 165 Russian missiles in a week",
         "Kyiv says Moscow fired 165 missiles in seven days as US delays "
         "Patriots.", "Kyiv", "CLAIM"),
        (11, "WORLD \u00b7 CLIMATE", (85, 85, 85), "COP31: the day after",
         "194 nations reject the Antalya pact; the collapse draws fury.", "CNN", "REPORTED"),
        (12, "AFRICA \u00b7 LIBYA", (138, 109, 30),
         "Benghazi: UN demands probe of port attacks",
         "Drones hit two Russian ships; UN calls for an investigation.",
         "UN News", "CLAIM"),
        (13, "MIDDLE EAST \u00b7 ISRAEL", (122, 63, 160),
         "Israel unity talks resume",
         "Likud and Gantz's Yesh Atid return to the table after Sunday's "
         "stall.", "Reuters", "ONGOING"),
    ]
    ch = 98
    for i, (num, kick, col, title, body, src, chp) in enumerate(cards):
        col_i, row_i = i % 5, i // 5
        x = M + col_i * cw
        y = 452 + row_i * (ch + 4)
        card(d, x, y, cw - 4, ch, num, kick, col, title, body, src, chp)

    # ---- map + ALSO ----
    d.text((M, 656), "THE WORLD \u2014 WHERE IT HAPPENED",
           font=font(F_SANS_B, 13), fill=RED)
    d.text((M + 268, 658), "PIN = STORY NUMBER", font=font(F_SANS, 9),
           fill=GRAY)
    d.text((586, 656), "ALSO ON MONDAY \u2014 18 MORE STORIES",
           font=font(F_SANS_B, 13), fill=RED)
    draw_map(d, M, 674, 556, 192)

    also = [
        ("MIDDLE EAST", (122, 63, 160), [
            (14, "Gaza: two killed in strike"),
            (15, "West Bank: settler attacks"),
            (16, "Iran war: no deal in sight"),
            (17, "Lebanon: 264 kg explosives"),
            (18, "Bahrain: plant hit, 2 hurt")]),
        ("AFRICA", (138, 109, 30), [
            (19, "Sudan: drones downed"),
            (20, "DRC: Ebola teams trapped")]),
        ("WORLD", (85, 85, 85), [
            (21, "States sue SpaceX")]),
        ("ASIA-PACIFIC", (30, 138, 110), [
            (22, "Bangladesh: Hasina jailed"),
            (23, "Seoul minister quits"),
            (24, "SK Telecom -7.3%"),
            (25, "China eases margin rules"),
            (26, "Seoul: 10T-won fund")]),
        ("NORTH AMERICA", (43, 94, 167), [
            (27, "Bessent: Nvidia answers"),
            (28, "FBI probes police hack"),
            (29, "Trump: Iran strikes?"),
            (30, "US futures jump 3%"),
            (31, "Tom Jackson dies at 75")]),
    ]
    af = font(F_SANS, 10)
    abf = font(F_SANS_B, 10)
    hf = font(F_SANS_B, 10)
    col_x = [586, 800]
    col_y = [674, 674]
    for ci, (region, col, items) in enumerate(also):
        target = 0 if ci < 3 else 1
        x = col_x[target]
        y = col_y[target]
        d.text((x, y), region, font=hf, fill=col)
        y += 15
        for n, txt in items:
            d.text((x, y), f"{n}", font=abf, fill=RED)
            d.text((x + 20, y), txt, font=af, fill=INK)
            y += 13
        col_y[target] = y + 4

    # ---- DATE CHECK ----
    d.rectangle([M, 876, W - M, 958], outline=RED, width=2)
    d.text((M + 8, 882), "DATE CHECK", font=font(F_SANS_B, 14), fill=RED)
    d.text((M + 112, 884),
           "Every story above happened or was first reported on Monday "
           "23 November 2026.", font=font(F_SANS, 10), fill=INK)
    d.text((W - M - tw(d, "WIRES READ UP TO 23:00 UTC",
                       font(F_SANS_B, 9)), 884), "WIRES READ UP TO 23:00 UTC",
           font=font(F_SANS_B, 9), fill=RED)
    lf = font(F_SANS, 10)
    left_out = ("LEFT OUT (not 23 Nov): Democrats reach 258 (22 Nov) \u00b7 "
                "Sparta II fire (22 Nov) \u00b7 El Chapo Isidro captured "
                "(22 Nov) \u00b7 EU\u2013Indonesia pact (21 Nov) \u00b7 "
                "Nigeria boat (21 Nov) \u00b7 ICJ Myanmar ruling (19 Nov).")
    lo = wrap(d, left_out, lf, W - 2 * M - 16)
    yy = draw_lines(d, lo, M + 8, 906, lf, INK, 13, max_lines=2)
    if len(lo) > 2:
        print(f"DATE CHECK LEFT OUT OVERFLOW: {len(lo)} lines")
    d.text((M + 8, yy + 2),
           "NOT YET: Dymer search continues (14 missing) \u00b7 4 House "
           "races uncalled \u00b7 COP32 venue not set \u00b7 WHO evacuating "
           "trapped Ebola staff.", font=lf, fill=INK)

    # ---- footer ----
    d.text((M, 966),
           "SOURCES: AP \u00b7 Reuters \u00b7 Bloomberg \u00b7 AFP \u00b7 CNN "
           "\u00b7 ESPN \u00b7 UN News \u00b7 WHO \u00b7 Kyiv \u00b7 Lowy "
           "Institute \u00b7 Korea JoongAng \u00b7 Morningstar",
           font=font(F_SANS, 9), fill=GRAY)
    d.text((M, 980),
           "CONFIRMED = 2+ outlets \u00b7 REPORTED = carried by a wire \u00b7 "
           "CLAIM = one side alleges \u00b7 ONGOING = developing. Red pin = "
           "reported \u00b7 Amber pin = claim (unverified).",
           font=font(F_SANS, 9), fill=GRAY)
    d.text((M, 996), "THE WORLD TODAY \u00b7 23 NOV 2026",
           font=font(F_SANS_B, 10), fill=INK)
    d.text((W - M - tw(d, "Scenes are drawn illustrations, not "
                       "photographs.", font(F_SERIF_IT, 10)), 996),
           "Scenes are drawn illustrations, not photographs.",
           font=font(F_SERIF_IT, 10), fill=GRAY)

    img.save("entry.png", optimize=True)
    print("saved entry.png")

if __name__ == "__main__":
    main()
