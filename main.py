#!/usr/bin/env python3
"""One image summing up the world news of Monday 23 November 2026.

Draws a newspaper front page with six panels, one per story, using
Pillow only. No network, no files read, fully deterministic output.
Writes to $MAKEFUN_OUTPUT_DIR/entry.png (default /output/entry.png).
"""

import math
import os

from PIL import Image, ImageDraw, ImageFont

CANVAS = (1024, 1024)
OUT_NAME = "entry.png"

# --- palette -------------------------------------------------------------
PAPER = (246, 241, 231)      # warm newsprint
INK = (18, 38, 63)           # deep navy ink
NAVY = (16, 34, 56)          # header band
GOLD = (198, 148, 52)        # masthead rule + accents
CARD = (255, 255, 255)       # panel background
MUTED = (92, 96, 104)        # caption grey
RED = (178, 44, 36)
TEAL = (18, 122, 110)
ORANGE = (214, 104, 26)
BLUE = (38, 96, 164)
GREEN = (46, 125, 62)
PURPLE = (106, 68, 150)

SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SERIF_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"


def font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


def wrap(draw, text, face, max_w):
    """Greedy word wrap returning a list of lines that fit max_w."""
    lines, current = [], ""
    for word in text.split():
        trial = (current + " " + word).strip()
        if draw.textlength(trial, font=face) <= max_w:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def centred(draw, cx, y, text, face, fill):
    w = draw.textlength(text, font=face)
    draw.text((cx - w / 2, y), text, font=face, fill=fill)


# --- glyphs: each draws one story's picture inside a box -----------------

def glyph_climate(d, x0, y0, x1, y1):
    """Thermometer running hot under a harsh sun (COP31 fails)."""
    cx = (x0 + x1) // 2
    # sun, top right
    sx, sy, sr = x1 - 34, y0 + 30, 16
    for ang in range(0, 360, 45):
        dx = int(26 * math.cos(math.radians(ang)))
        dy = int(26 * math.sin(math.radians(ang)))
        ex = int(34 * math.cos(math.radians(ang)))
        ey = int(34 * math.sin(math.radians(ang)))
        d.line([(sx + dx, sy + dy), (sx + ex, sy + ey)], fill=GOLD, width=4)
    d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(240, 178, 44))
    # thermometer tube
    tx0, tx1 = cx - 16, cx + 16
    ty0, ty1 = y0 + 14, y1 - 34
    d.rounded_rectangle([tx0, ty0, tx1, ty1], radius=16, fill=(255, 255, 255),
                        outline=INK, width=4)
    d.rounded_rectangle([tx0 + 5, ty0 + 26, tx1 - 5, ty1 - 6], radius=10,
                        fill=(232, 84, 66))
    # tick marks
    for frac in (0.25, 0.5, 0.75):
        yy = ty0 + int((ty1 - ty0) * frac)
        d.line([(tx1 + 2, yy), (tx1 + 14, yy)], fill=INK, width=3)
    # bulb
    d.ellipse([cx - 30, ty1 - 16, cx + 30, ty1 + 40], fill=(232, 84, 66),
              outline=INK, width=4)
    # ground crack
    d.line([(x0 + 18, y1 - 6), (x0 + 60, y1 - 18), (x0 + 96, y1 - 8),
            (x0 + 140, y1 - 20)], fill=RED, width=4)


def glyph_ship(d, x0, y0, x1, y1):
    """Capsized corvette, bow only above the water (Benghazi)."""
    cx = (x0 + x1) // 2
    water_y = y0 + 100
    # sea first, so the hull sits in it
    d.rectangle([x0, water_y, x1, y1], fill=(196, 222, 240))
    # smoke puffs
    for px, py, pr in ((cx - 52, y0 + 26, 14), (cx - 30, y0 + 12, 18),
                       (cx - 6, y0 + 24, 12)):
        d.ellipse([px - pr, py - pr, px + pr, py + pr], fill=(150, 150, 150))
    # hull, tilted and half sunk: bow sticking up on the right
    hull = [(cx - 92, water_y - 2), (cx - 40, water_y - 30),
            (cx + 8, water_y - 48), (cx + 58, water_y - 78),
            (cx + 78, water_y - 58), (cx + 40, water_y - 26),
            (cx - 30, water_y + 8)]
    d.polygon(hull, fill=(90, 96, 104), outline=INK)
    d.line([(cx - 40, water_y - 30), (cx + 8, water_y - 48)], fill=RED, width=4)
    # mast poking out
    d.line([(cx + 58, water_y - 78), (cx + 72, water_y - 98)], fill=INK, width=5)
    # wave crests breaking over the hull's waterline
    for wx in range(x0 + 8, x1 - 8, 34):
        d.arc([wx, water_y - 8, wx + 34, water_y + 20], 0, 180, fill=BLUE, width=4)


def glyph_capitol(d, x0, y0, x1, y1):
    """US Capitol dome on columns (Democrats take the House)."""
    cx = (x0 + x1) // 2
    base_y = y1 - 10
    # "258" badge, top left of the glyph zone, clear of the building
    badge = font(SANS_BOLD, 30)
    d.text((x0 + 2, y0 + 2), "258", font=badge, fill=BLUE)
    # steps
    for i, w in enumerate((150, 168, 186)):
        yy = base_y - i * 9
        d.rectangle([cx - w // 2, yy - 9, cx + w // 2, yy], fill=(200, 200, 196),
                    outline=INK)
    # columns
    for k in range(-2, 3):
        col_x = cx + k * 30
        d.rectangle([col_x - 8, base_y - 70, col_x + 8, base_y - 24],
                    fill=(240, 240, 236), outline=INK, width=2)
    # entablature + dome, kept inside the glyph zone
    d.rectangle([cx - 88, base_y - 84, cx + 88, base_y - 70],
                fill=(240, 240, 236), outline=INK, width=2)
    d.pieslice([cx - 56, base_y - 140, cx + 56, base_y - 84], 180, 360,
               fill=(240, 240, 236), outline=INK, width=3)
    # gold finial ball on the dome
    d.ellipse([cx - 8, base_y - 150, cx + 8, base_y - 138], fill=GOLD,
              outline=INK, width=2)


def glyph_fire(d, x0, y0, x1, y1):
    """Factory with sawtooth roof in flames (Cikande)."""
    cx = (x0 + x1) // 2
    base_y = y1 - 14
    # factory block with sawtooth roof
    roof = [(x0 + 22, base_y - 74), (x0 + 52, base_y - 104),
            (x0 + 82, base_y - 74), (x0 + 112, base_y - 104),
            (x0 + 142, base_y - 74), (x0 + 172, base_y - 104),
            (x0 + 202, base_y - 74)]
    d.polygon(roof + [(x0 + 202, base_y), (x0 + 22, base_y)], fill=(120, 118, 112),
              outline=INK)
    # chimney
    d.rectangle([x1 - 52, base_y - 128, x1 - 30, base_y - 60], fill=(96, 94, 90),
                outline=INK)
    # windows
    for wx in range(x0 + 36, x0 + 190, 44):
        d.rectangle([wx, base_y - 46, wx + 26, base_y - 18], fill=(255, 214, 120),
                    outline=INK, width=2)
    # flame tongues
    flame = [(cx - 46, y0 + 74), (cx - 34, y0 + 34), (cx - 16, y0 + 56),
             (cx - 4, y0 + 18), (cx + 12, y0 + 48), (cx + 26, y0 + 28),
             (cx + 34, y0 + 58), (cx + 48, y0 + 74)]
    d.polygon(flame, fill=ORANGE, outline=RED)
    inner = [(cx - 24, y0 + 74), (cx - 14, y0 + 48), (cx, y0 + 62),
             (cx + 12, y0 + 44), (cx + 24, y0 + 74)]
    d.polygon(inner, fill=(255, 214, 64))
    # smoke
    for px, py, pr in ((x1 - 40, y0 + 8, 13), (x1 - 62, y0 + 2, 10)):
        d.ellipse([px - pr, py - pr, px + pr, py + pr], fill=(140, 140, 140))


def glyph_collapse(d, x0, y0, x1, y1):
    """Apartment block sheared and leaning, drone overhead (Dymer, Kyiv)."""
    cx = (x0 + x1) // 2
    base_y = y1 - 12
    # leaning block, left half standing, right half sheared down
    d.polygon([(cx - 96, base_y), (cx - 96, y0 + 34), (cx - 8, y0 + 34),
               (cx - 8, base_y)], fill=(196, 186, 170), outline=INK)
    d.polygon([(cx - 8, y0 + 66), (cx + 88, y0 + 96), (cx + 88, base_y),
               (cx - 8, base_y)], fill=(150, 142, 128), outline=INK)
    # windows on the standing half
    for wy in range(y0 + 48, base_y - 20, 30):
        for wx in (cx - 82, cx - 48):
            d.rectangle([wx, wy, wx + 22, wy + 18], fill=(70, 90, 110),
                        outline=INK, width=2)
    # crack line
    d.line([(cx - 8, y0 + 34), (cx - 8, y0 + 66)], fill=RED, width=5)
    d.line([(cx - 8, y0 + 66), (cx + 20, y0 + 80)], fill=RED, width=4)
    # rubble
    for rx, ry, rr in ((cx + 30, base_y - 8, 10), (cx + 56, base_y - 6, 13),
                       (cx + 78, base_y - 10, 8)):
        d.polygon([(rx - rr, base_y), (rx, base_y - rr), (rx + rr, base_y)],
                  fill=(120, 114, 106), outline=INK)
    # drone above
    dx, dy = cx + 56, y0 + 16
    d.ellipse([dx - 12, dy - 7, dx + 12, dy + 7], fill=INK)
    d.line([(dx - 26, dy - 8), (dx + 26, dy - 8)], fill=INK, width=3)
    d.ellipse([dx - 30, dy - 12, dx - 22, dy - 4], fill=MUTED)
    d.ellipse([dx + 22, dy - 12, dx + 30, dy - 4], fill=MUTED)


def glyph_exam(d, x0, y0, x1, y1):
    """Exam paper crossed out beside a phone with a camera lens (CSAT)."""
    cx = (x0 + x1) // 2
    # exam sheet, tilted left
    sheet = [(x0 + 30, y0 + 22), (x0 + 118, y0 + 12), (x0 + 128, y1 - 24),
             (x0 + 40, y1 - 14)]
    d.polygon(sheet, fill=(255, 255, 255), outline=INK, width=3)
    for i in range(4):
        yy = y0 + 44 + i * 22
        d.line([(x0 + 46, yy), (x0 + 104, yy - 2)], fill=MUTED, width=3)
    # red X over the sheet
    d.line([(x0 + 44, y0 + 30), (x0 + 112, y1 - 30)], fill=RED, width=6)
    d.line([(x0 + 112, y0 + 24), (x0 + 44, y1 - 22)], fill=RED, width=6)
    # phone, right side
    px0, py0, px1, py1 = cx + 18, y0 + 18, cx + 92, y1 - 18
    d.rounded_rectangle([px0, py0, px1, py1], radius=12, fill=(30, 34, 40),
                        outline=INK, width=3)
    d.rounded_rectangle([px0 + 8, py0 + 16, px1 - 8, py1 - 12], radius=6,
                        fill=(210, 228, 240))
    # camera lens on the phone screen
    lx, ly = (px0 + px1) // 2, (py0 + py1) // 2 - 8
    d.ellipse([lx - 18, ly - 18, lx + 18, ly + 18], fill=INK)
    d.ellipse([lx - 10, ly - 10, lx + 10, ly + 10], fill=(80, 140, 200))
    d.ellipse([lx - 4, ly - 4, lx + 4, ly + 4], fill=(20, 30, 44))
    # "111" badge under the phone
    badge = font(SANS_BOLD, 26)
    centred(d, (px0 + px1) // 2, py1 - 2, "111", badge, RED)


# --- page furniture -------------------------------------------------------

def draw_globe(d, cx, cy, r):
    """Simple wireframe globe for the masthead."""
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(255, 255, 255), width=3)
    d.ellipse([cx - r // 2, cy - r, cx + r // 2, cy + r], outline=(255, 255, 255),
              width=2)
    d.line([(cx - r, cy), (cx + r, cy)], fill=(255, 255, 255), width=2)
    d.arc([cx - r, cy - r // 2, cx + r, cy + r // 2], 0, 360,
          fill=(255, 255, 255), width=2)


def draw_header(d, w):
    d.rectangle([0, 0, w, 168], fill=NAVY)
    d.rectangle([0, 164, w, 168], fill=GOLD)
    draw_globe(d, 78, 82, 52)
    title = font(SERIF_BOLD, 58)
    d.text((152, 26), "THE WORLD IN ONE DAY", font=title, fill=(255, 255, 255))
    date_f = font(SANS_BOLD, 30)
    d.text((154, 100), "MONDAY  \u00b7  23 NOVEMBER 2026", font=date_f,
           fill=(232, 196, 106))
    sub = font(SANS, 22)
    d.text((154, 136), "Six stories that defined the day", font=sub,
           fill=(200, 210, 220))


STORIES = [
    # (tag, accent, headline, caption, glyph)
    ("CLIMATE \u00b7 ANTALYA", TEAL, "COP31 COLLAPSES WITH NO DEAL",
     "Climate talks end in chaos: no fossil-fuel text, no finance deal \u2014 "
     "the first big failure since Copenhagen.",
     glyph_climate),
    ("LIBYA \u00b7 BENGHAZI", BLUE, "RUSSIAN WARSHIP SUNK BY DRONES",
     "The corvette Merkury capsizes after a drone attack at Benghazi naval "
     "base; ten crew slightly hurt.",
     glyph_ship),
    ("USA \u00b7 WASHINGTON", RED, "DEMOCRATS TAKE THE HOUSE",
     "At least 258 seats \u2014 the biggest House majority for either party "
     "since 1992.",
     glyph_capitol),
    ("INDONESIA \u00b7 CIKANDE", ORANGE, "CANDY FACTORY FIRE: 24 DEAD",
     "Blaze rips through the PT Fonusa Agung Mulia plant; 24 body bags "
     "recovered, dozens still missing.",
     glyph_fire),
    ("UKRAINE \u00b7 KYIV", PURPLE, "DRONE COLLAPSES KYIV FLAT BLOCK",
     "A Russian drone strike brings down a five-storey apartment block in "
     "Dymer; 14 people unaccounted for.",
     glyph_collapse),
    ("SOUTH KOREA \u00b7 SEOUL", GREEN, "MINISTER QUITS OVER EXAM SCANDAL",
     "Education chief resigns after 111 AI-cheating cases in the CSAT exam.",
     glyph_exam),
]


def draw_panel(d, x, y, w, h, story):
    tag, accent, headline, caption, glyph = story
    d.rounded_rectangle([x, y, x + w, y + h], radius=10, fill=CARD,
                        outline=(210, 205, 192), width=2)
    d.rounded_rectangle([x, y, x + w, y + 8], radius=4, fill=accent)
    tag_f = font(SANS_BOLD, 17)
    d.text((x + 14, y + 18), tag, font=tag_f, fill=accent)
    # glyph zone
    glyph(d, x + 14, y + 44, x + w - 14, y + 196)
    # headline
    head_f = font(SANS_BOLD, 25)
    lines = wrap(d, headline, head_f, w - 28)
    yy = y + 204
    for line in lines:
        d.text((x + 14, yy), line, font=head_f, fill=INK)
        yy += 30
    # caption
    cap_f = font(SANS, 18)
    for line in wrap(d, caption, cap_f, w - 28):
        d.text((x + 14, yy + 4), line, font=cap_f, fill=MUTED)
        yy += 23


def build_image():
    w, h = CANVAS
    img = Image.new("RGB", CANVAS, PAPER)
    d = ImageDraw.Draw(img)
    draw_header(d, w)

    margin, gap = 24, 17
    pw = (w - 2 * margin - 2 * gap) // 3          # 314
    ph = 378
    top = 184
    for i, story in enumerate(STORIES):
        col, row = i % 3, i // 3
        x = margin + col * (pw + gap)
        y = top + row * (ph + 16)
        draw_panel(d, x, y, pw, ph, story)

    foot = font(SANS, 18)
    centred(d, w // 2, 978, "Reported 22\u201323 November 2026  \u00b7  AP \u00b7 Reuters "
            "\u00b7 Xinhua \u00b7 Korea JoongAng Daily", foot, MUTED)
    return img


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    img = build_image()
    img.save(os.path.join(out_dir, OUT_NAME), format="PNG")


if __name__ == "__main__":
    main()
