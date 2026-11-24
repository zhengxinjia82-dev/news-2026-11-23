#!/usr/bin/env python3
"""Draw the 23 Nov 2026 front page: 32 stories, newspaper style. Fresh code."""
import json, math
from PIL import Image, ImageDraw, ImageFont

ROOT = "/home/hatch/workspace/makefun/news-2026-11-23"
W, H = 1024, 1024
MX = 24                      # side margin
CW = W - 2 * MX              # 976 content width
PAPER = (247, 243, 232)
CARD = (255, 253, 246)
INK = (17, 17, 17)
GREY = (85, 85, 85)
RED = (185, 28, 28)
LINE = (201, 194, 174)
MAPDOT = (148, 138, 116)
BADGE = {"CONFIRMED": (21, 128, 61), "REPORTED": (29, 78, 216),
         "CLAIM": (180, 83, 9), "FORECAST": (109, 40, 217),
         "OFFICIAL": (14, 116, 144)}
FD = "/usr/share/fonts/truetype/dejavu/"

def font(name, size):
    return ImageFont.truetype(FD + name, size)

SERIF_B = lambda s: font("DejaVuSerif-Bold.ttf", s)
SERIF = lambda s: font("DejaVuSerif.ttf", s)
SANS = lambda s: font("DejaVuSans.ttf", s)
SANS_B = lambda s: font("DejaVuSans-Bold.ttf", s)

data = json.load(open(f"{ROOT}/stories.json"))

img = Image.new("RGB", (W, H), PAPER)
d = ImageDraw.Draw(img)

def tw(text, f):
    return d.textlength(text, font=f)

def fit(text, f, maxw):
    """Truncate with ellipsis to pixel width."""
    if tw(text, f) <= maxw:
        return text
    while text and tw(text + "…", f) > maxw:
        text = text[:-1]
    return text + "…"

def wrap(text, f, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if tw(t, f) <= maxw:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

def badge(x, y, label, f, h=13):
    w = tw(label, f) + 10
    d.rounded_rectangle([x, y, x + w, y + h], radius=3, fill=BADGE[label])
    d.text((x + 5, y + 1), label, font=f, fill=(255, 255, 255))
    return x + w

def rule(y, wdt=1):
    d.line([(MX, y), (W - MX, y)], fill=INK, width=wdt)

# ---- kicker ----
d.text((MX, 10), "THE WORLD'S NEWS IN ONE DAY", font=SANS_B(13), fill=RED)
r = data["kicker_right"]
d.text((W - MX - tw(r, SANS_B(13)), 10), r, font=SANS_B(13), fill=RED)
rule(32)

# ---- masthead ----
d.text((MX, 38), data["masthead"], font=SERIF_B(58), fill=INK)
rule(104, 2)
rule(107)
d.text((MX, 112), data["subtitle"], font=SERIF(15), fill=GREY)

# ---- UTC timeline ----
d.text((MX, 136), "THE DAY IN UTC", font=SANS_B(11), fill=INK)
TX0, TX1, TY = 150, 1000, 162
d.line([(TX0, TY), (TX1, TY)], fill=INK, width=1)
for i, ev in enumerate(data["timeline"]):
    hh, mm = map(int, ev["utc"].split(":"))
    frac = (hh * 60 + mm) / 1440.0
    x = TX0 + frac * (TX1 - TX0)
    d.ellipse([x - 4, TY - 4, x + 4, TY + 4], fill=RED)
    lab = f"{ev['utc']}  {ev['label']}"
    lw = tw(lab, SANS(10))
    lx = min(max(x - lw / 2, MX), W - MX - lw)
    if i % 2 == 1:
        d.text((lx, TY - 26), lab, font=SANS(10), fill=INK)
    else:
        d.text((lx, TY + 10), lab, font=SANS(10), fill=INK)
rule(190)

# ---- headline illustrations ----
def art_chip(x, y, w, h):
    d.rectangle([x + 90, y + 18, x + 150, y + 78], fill=(31, 41, 55), outline=INK)
    d.rectangle([x + 108, y + 36, x + 132, y + 60], outline=(255, 255, 255))
    for i in range(4):
        px = x + 102 + i * 14
        d.line([(px, y + 18), (px, y + 8)], fill=INK, width=3)
        d.line([(px, y + 78), (px, y + 88)], fill=INK, width=3)
    d.line([(x + 170, y + 80), (x + 210, y + 55), (x + 240, y + 62),
            (x + 290, y + 18)], fill=RED, width=4)
    d.polygon([(x + 290, y + 18), (x + 272, y + 20), (x + 288, y + 34)],
              fill=RED)
    d.text((x + 8, y + 88), "+31%", font=SANS_B(16), fill=(21, 128, 61))

def art_ship(x, y, w, h):
    for j in range(3):
        yy = y + 78 + j * 8
        d.arc([x + 10, yy - 6, x + 300, yy + 10], 0, 180, fill=(29, 78, 216))
    d.polygon([(x + 60, y + 52), (x + 250, y + 52), (x + 230, y + 78),
               (x + 80, y + 78)], fill=(100, 60, 40))
    d.rectangle([x + 130, y + 20, x + 136, y + 52], fill=INK)
    d.polygon([(x + 136, y + 20), (x + 168, y + 28), (x + 136, y + 36)],
              fill=RED)
    for i in range(7):
        dx = x + 40 + i * 34
        dy = y + 12 + (6 if i % 2 else 0)
        d.ellipse([dx - 3, dy - 3, dx + 3, dy + 3], fill=INK)

def art_tanker(x, y, w, h):
    d.polygon([(x + 40, y + 60), (x + 270, y + 60), (x + 250, y + 88),
               (x + 60, y + 88)], fill=(120, 40, 40))
    for i, c in enumerate([(200, 120, 40), (40, 120, 160), (60, 140, 80)]):
        d.rectangle([x + 70 + i * 56, y + 30, x + 118 + i * 56, y + 58],
                    fill=c, outline=INK)
    for xx in range(x + 20, x + 300, 16):
        d.line([(xx, y + 8), (xx + 8, y + 8)], fill=RED, width=3)
    d.text((x + 8, y + 92), "BLOCKADE", font=SANS_B(11), fill=RED)

ARTS = {"chip": art_chip, "ship": art_ship, "tanker": art_tanker}

# ---- 3 big headlines ----
COLW, GAP = 312, 20
for i, h in enumerate(data["headlines"]):
    x = MX + i * (COLW + GAP)
    y0 = 196
    d.rectangle([x, y0, x + COLW, y0 + 108], fill=CARD, outline=LINE)
    ARTS[h["art"]](x, y0, COLW, 108)
    d.ellipse([x, y0 + 118, x + 18, y0 + 136], fill=RED)
    d.text((x + 6, y0 + 119), str(h["n"]), font=SANS_B(11), fill=(255, 255, 255))
    d.text((x + 24, y0 + 120), h["region"], font=SANS_B(11), fill=RED)
    ty = y0 + 138
    for ln in wrap(h["title"], SERIF_B(21), COLW)[:3]:
        d.text((x, ty), ln, font=SERIF_B(21), fill=INK)
        ty += 25
    by = ty + 6
    for ln in wrap(h["body"], SANS(12), COLW)[:2]:
        d.text((x, by), ln, font=SANS(12), fill=(51, 51, 51))
        by += 16
    bx = badge(x, 440, h["badge"], SANS_B(9))
    d.text((bx + 6, 441), h["source"], font=SANS(9), fill=GREY)

# ---- numbers bar ----
d.text((MX, 458), "THE DAY IN NUMBERS", font=SANS_B(12), fill=INK)
for i, nb in enumerate(data["numbers"]):
    x = MX + i * 244
    d.text((x, 470), nb["big"], font=SERIF_B(24), fill=RED)
    d.text((x, 492), fit(nb["label"], SANS(10), 230), font=SANS(10), fill=GREY)
rule(506)

# ---- secondary illustrations (187 x 28) ----
def s_ballot(x, y):
    d.rectangle([x + 8, y + 8, x + 34, y + 24], outline=INK, width=2)
    d.line([(x + 12, y + 16), (x + 18, y + 21), (x + 30, y + 10)], fill=RED, width=2)

def s_building(x, y):
    d.rectangle([x + 10, y + 4, x + 34, y + 24], outline=INK, width=2)
    for wy in (9, 15):
        for wx in (14, 22, 28):
            d.rectangle([x + wx, y + wy, x + wx + 4, y + wy + 3], fill=GREY)
    d.line([(x + 20, y + 4), (x + 16, y + 14), (x + 24, y + 24)], fill=RED, width=2)

def s_drone(x, y):
    d.ellipse([x + 8, y + 6, x + 16, y + 14], outline=INK, width=2)
    d.ellipse([x + 28, y + 6, x + 36, y + 14], outline=INK, width=2)
    d.ellipse([x + 8, y + 18, x + 16, y + 26], outline=INK, width=2)
    d.ellipse([x + 28, y + 18, x + 36, y + 26], outline=INK, width=2)
    d.rectangle([x + 18, y + 12, x + 26, y + 20], fill=INK)

def s_flame(x, y):
    d.polygon([(x + 22, y + 2), (x + 32, y + 16), (x + 30, y + 24),
               (x + 14, y + 24), (x + 12, y + 16)], fill=(220, 90, 20))
    d.polygon([(x + 22, y + 12), (x + 27, y + 20), (x + 17, y + 20)],
              fill=(250, 200, 60))

def s_shield(x, y):
    d.polygon([(x + 10, y + 4), (x + 34, y + 4), (x + 34, y + 16),
               (x + 22, y + 26), (x + 10, y + 16)], fill=(29, 78, 216))
    d.line([(x + 16, y + 14), (x + 21, y + 19), (x + 29, y + 10)],
           fill=(255, 255, 255), width=2)

def s_barrel(x, y):
    d.ellipse([x + 12, y + 4, x + 32, y + 10], fill=(120, 120, 120), outline=INK)
    d.rectangle([x + 12, y + 7, x + 32, y + 24], fill=(150, 150, 150), outline=INK)
    d.ellipse([x + 12, y + 20, x + 32, y + 26], fill=(120, 120, 120), outline=INK)
    d.line([(x + 12, y + 15), (x + 32, y + 15)], fill=RED, width=2)

def s_scales(x, y):
    d.line([(x + 22, y + 4), (x + 22, y + 24)], fill=INK, width=2)
    d.line([(x + 8, y + 6), (x + 36, y + 6)], fill=INK, width=2)
    d.polygon([(x + 6, y + 12), (x + 14, y + 12), (x + 10, y + 20)], fill=GREY)
    d.polygon([(x + 30, y + 12), (x + 38, y + 12), (x + 34, y + 20)], fill=GREY)

def s_orbit(x, y):
    d.ellipse([x + 16, y + 9, x + 28, y + 21], fill=(180, 120, 40))
    d.arc([x + 4, y + 2, x + 40, y + 26], 200, 340, fill=INK)
    d.ellipse([x + 34, y + 4, x + 38, y + 8], fill=RED)

def s_flag(x, y):
    d.line([(x + 10, y + 4), (x + 10, y + 26)], fill=INK, width=2)
    d.rectangle([x + 10, y + 4, x + 36, y + 18], fill=(0, 51, 153))
    for k in range(6):
        a = math.radians(k * 60)
        d.ellipse([x + 23 + 5 * math.cos(a) - 1, y + 11 + 4 * math.sin(a) - 1,
                   x + 23 + 5 * math.cos(a) + 1, y + 11 + 4 * math.sin(a) + 1],
                  fill=(255, 204, 0))

def s_cuffs(x, y):
    d.ellipse([x + 8, y + 8, x + 20, y + 20], outline=INK, width=2)
    d.ellipse([x + 26, y + 8, x + 38, y + 20], outline=INK, width=2)
    d.line([(x + 20, y + 14), (x + 26, y + 14)], fill=INK, width=2)

SARTS = {"ballot": s_ballot, "building": s_building, "drone": s_drone,
         "flame": s_flame, "shield": s_shield, "barrel": s_barrel,
         "scales": s_scales, "orbit": s_orbit, "flag": s_flag, "cuffs": s_cuffs}

SCW, SGAP = 187, 10
for i, s in enumerate(data["secondary"]):
    col, row = i % 5, i // 5
    x = MX + col * (SCW + SGAP)
    y0 = 512 + row * 108
    d.rectangle([x, y0, x + SCW, y0 + 28], fill=CARD, outline=LINE)
    SARTS[s["art"]](x + 70, y0)
    d.text((x, y0 + 34), f"{s['n']} · {s['region']}", font=SANS_B(10), fill=RED)
    ty = y0 + 48
    for ln in wrap(s["title"], SANS_B(12), SCW)[:2]:
        d.text((x, ty), ln, font=SANS_B(12), fill=INK)
        ty += 13
    d.text((x, y0 + 76), fit(s["body"], SANS(10), SCW), font=SANS(10), fill=(51, 51, 51))
    bx = badge(x, y0 + 90, s["badge"], SANS_B(9), h=12)
    d.text((bx + 5, y0 + 91), fit(s["source"], SANS(9), SCW - (bx + 5 - x)),
           font=SANS(9), fill=GREY)
rule(724)

# ---- bottom band ----
# world map (dot grid)
MAP_X, MAP_Y, CELL = 34, 752, 4
LAND = [
"..............................................................",
"..............................................................",
"...##########.....##......######################..............",
"..#############...###..#####.#######################...........",
"..##############....########.#######################..........",
"...#############....########.######################...........",
"....############....######...###################....##.........",
".....###########....#####....#################.......##........",
"......##########....####.....###############..###..............",
".......########....#######...##########....####................",
"........######.....#######....######.....###...................",
".........####......#######.....####............................",
"..........##...####.#######....###.............................",
".............#####..######.....##..............................",
".............######.#####.....................................",
"..............#####.####......................................",
"..............####..###........................................",
"..............###...##..................######.................",
"..............##.......................#######................",
"..............##........................######................",
"...............#.........................####.................",
"...............#..............................................",
"..............................................................",
"..............................................................",
"..............................................................",
"..............................................................",
]
d.text((MX, 732), "WHERE IT HAPPENED", font=SANS_B(12), fill=INK)
for gy, rowstr in enumerate(LAND):
    for gx, ch in enumerate(rowstr):
        if ch == "#":
            d.ellipse([MAP_X + gx * CELL, MAP_Y + gy * CELL,
                       MAP_X + gx * CELL + 3, MAP_Y + gy * CELL + 3],
                      fill=MAPDOT)
for p in data["map_points"]:
    gx = (p["lon"] + 180) / 360 * 62
    gy = (90 - p["lat"]) / 180 * 26
    px = MAP_X + gx * CELL
    py = MAP_Y + gy * CELL
    d.ellipse([px - 7, py - 7, px + 7, py + 7], fill=RED, outline=(255, 255, 255))
    d.text((px - 3, py - 6), str(p["n"]), font=SANS_B(8), fill=(255, 255, 255))
d.text((MX, 864), "1 Santa Clara · 2 Benghazi · 3 Strait of Hormuz",
       font=SANS(10), fill=GREY)

# DATE CHECK box
BX0, BY0, BX1, BY1 = MX, 880, 316, 992
d.rectangle([BX0, BY0, BX1, BY1], outline=RED, width=2)
d.text((BX0 + 8, BY0 + 6), "DATE CHECK — LEFT OUT AS OLDER NEWS",
       font=SANS_B(11), fill=RED)
yy = BY0 + 20
for item in data["date_check"]:
    t = "✕ " + item["text"]
    d.text((BX0 + 8, yy), fit(t, SANS(10), 200), font=SANS(10), fill=INK)
    dw = tw(item["when"], SANS(10))
    d.text((BX1 - 8 - dw, yy), item["when"], font=SANS(10), fill=GREY)
    yy += 10
for ny in data["date_check_notyet"]:
    d.text((BX0 + 8, yy), fit(f"Not yet: {ny['text']}", SANS(10), 200),
           font=SANS(10), fill=RED)
    dw = tw(ny["when"], SANS(10))
    d.text((BX1 - 8 - dw, yy), ny["when"], font=SANS(10), fill=GREY)
    yy += 10

# briefs
d.text((332, 732), "ALSO ON MONDAY 23 NOVEMBER", font=SANS_B(12), fill=INK)
for i, b in enumerate(data["briefs"]):
    col, row = i // 10, i % 10
    x = 332 + col * 338
    y = 752 + row * 15
    line = f"{b['n']}. {b['place']}: {b['text']}"
    d.text((x, y), fit(line, SANS(11), 330), font=SANS(11), fill=INK)
d.text((332, 908), "HOW SURE — CONFIRMED: 2+ sources · REPORTED: one source · CLAIM: one-sided claim",
       font=SANS(10), fill=GREY)
d.text((332, 922), "FORECAST: prediction · OFFICIAL: official statement",
       font=SANS(10), fill=GREY)
rc = data["regions_count"]
order = ["N. AMERICA", "EUROPE", "ASIA", "M. EAST", "AFRICA", "S. AMERICA", "OCEANIA"]
rline = "  ·  ".join(f"{k} {rc[k]}" for k in order)
d.text((332, 946), rline, font=SANS_B(11), fill=INK)

# ---- footer ----
oath = "Every story here happened, or was first reported, on Monday 23 November 2026."
d.text(((W - tw(oath, SANS(10))) / 2, 1000), oath, font=SANS(10), fill=GREY)
src = data["footer_sources"]
d.text(((W - tw(src, SANS(10))) / 2, 1012), src, font=SANS(10), fill=GREY)

img.save(f"{ROOT}/entry.png")
print("saved", f"{ROOT}/entry.png", img.size)
