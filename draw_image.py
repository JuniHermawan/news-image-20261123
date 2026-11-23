#!/usr/bin/env python3
"""Render the 23 November 2026 world-news image as one 1024x1024 PNG.

Six verified stories of the day, each in its own panel: a region tag,
a headline, a short detail paragraph and a small pictogram drawn from
plain PIL shapes. The header globe is drawn from arcs and ellipses —
no photos, no copied artwork, no generated assets, no network.
Run:

    python3 draw_image.py          # writes entry.png next to this file
"""

import math
import os

from PIL import Image, ImageDraw, ImageFont

BASE = os.path.dirname(os.path.abspath(__file__))
TARGET = os.path.join(BASE, "entry.png")

SIDE = 1024

# --- palette: deep teal header, copper accent, warm paper panels --------
TEAL_DEEP = (10, 38, 48)
TEAL_MID = (22, 70, 80)
TEAL_GLOW = (52, 128, 138)
COPPER = (192, 122, 58)
COPPER_SOFT = (216, 164, 102)
PAPER_LIGHT = (245, 238, 224)
PAPER_DARK = (236, 227, 209)
INK = (35, 40, 46)
SOFT_INK = (92, 102, 95)
RULE = (203, 192, 170)
WHITE = (255, 255, 255)
MIST = (178, 198, 205)

CLIMATE_GREEN = (46, 110, 72)
LIBYA_NAVY = (36, 86, 132)
USA_COPPER = (172, 96, 32)
JAVA_RED = (166, 58, 36)
KYIV_SLATE = (78, 92, 110)
KOREA_PLUM = (108, 64, 116)
FLAME = (214, 96, 32)

BOLD_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
PLAIN_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def face(bold, size):
    return ImageFont.truetype(BOLD_PATH if bold else PLAIN_PATH, size)


def fit_lines(canvas, text, typeface, width):
    """Greedy wrap: split text into lines no wider than width."""
    out, current = [], ""
    for word in text.split():
        candidate = word if not current else current + " " + word
        if canvas.textlength(candidate, font=typeface) <= width:
            current = candidate
        else:
            if current:
                out.append(current)
            current = word
    if current:
        out.append(current)
    return out


def header_band(img, canvas):
    """150px header: teal gradient, drawn globe, title."""
    for y in range(150):
        blend = y / 149.0
        colour = tuple(
            int(TEAL_DEEP[i] + (TEAL_MID[i] - TEAL_DEEP[i]) * blend)
            for i in range(3))
        canvas.line([(0, y), (1024, y)], fill=colour)
    # drawn globe, right side, half off the edge
    gx, gy, gr = 905, 75, 118
    canvas.ellipse([gx - gr, gy - gr, gx + gr, gy + gr],
                   outline=TEAL_GLOW, width=4)
    for k in (0.45, 0.8):
        w = int(gr * k)
        canvas.ellipse([gx - w, gy - gr, gx + w, gy + gr],
                       outline=TEAL_GLOW, width=2)
    for dy in (-52, 0, 52):
        hw = int(math.sqrt(max(gr * gr - dy * dy, 0)))
        canvas.line([(gx - hw, gy + dy), (gx + hw, gy + dy)],
                    fill=TEAL_GLOW, width=2)
    # small orbiting dots
    for ang in (35, 140, 250):
        rad = math.radians(ang)
        px = gx + int(150 * math.cos(rad))
        py = gy + int(150 * math.sin(rad)) - 40
        canvas.ellipse([px - 4, py - 4, px + 4, py + 4], fill=COPPER_SOFT)
    canvas.line([(0, 150), (1024, 150)], fill=COPPER, width=4)
    canvas.text((26, 18), "23 NOVEMBER 2026",
                font=face(True, 48), fill=WHITE)
    canvas.text((28, 82), "THE WORLD IN ONE DAY",
                font=face(True, 24), fill=COPPER_SOFT)
    right = "6 STORIES \u00b7 1 IMAGE"
    canvas.text((700 - canvas.textlength(right, font=face(True, 20)),
                 96), right, font=face(True, 20), fill=MIST)


def story_panel(canvas, rect, tag, tag_colour, headline, detail, glyph):
    """One panel: tag chip, copper rule, headline, detail, pictogram."""
    x0, y0, x1, y1 = rect
    shade = PAPER_LIGHT if (x0 + y0) % 2 == 0 else PAPER_DARK
    canvas.rounded_rectangle(rect, radius=16, fill=shade,
                             outline=RULE, width=2)
    chip = face(True, 19)
    chip_w = canvas.textlength(tag, font=chip) + 24
    canvas.rounded_rectangle([x0 + 16, y0 + 14, x0 + 16 + chip_w, y0 + 44],
                             radius=9, fill=tag_colour)
    canvas.text((x0 + 28, y0 + 19), tag, font=chip, fill=WHITE)
    head = face(True, 28)
    text_w = (x1 - x0) - 36
    y = y0 + 58
    for line in fit_lines(canvas, headline, head, text_w)[:2]:
        canvas.text((x0 + 18, y), line, font=head, fill=INK)
        y += 35
    canvas.line([(x0 + 18, y + 4), (x0 + 118, y + 4)], fill=COPPER, width=3)
    y += 16
    body = face(False, 18)
    for line in fit_lines(canvas, detail, body, text_w - 108)[:5]:
        canvas.text((x0 + 18, y + 2), line, font=body, fill=SOFT_INK)
        y += 24
    glyph(canvas, x1 - 106, y1 - 100)


# --- pictograms: fresh plain-shape glyphs, one per story -------------------

def glyph_globe_crack(canvas, x, y):
    # small globe with a jagged crack: the climate deal breaking apart
    cx, cy, r = x + 50, y + 46, 34
    canvas.ellipse([cx - r, cy - r, cx + r, cy + r],
                   outline=CLIMATE_GREEN, width=4)
    canvas.ellipse([cx - 15, cy - r, cx + 15, cy + r],
                   outline=CLIMATE_GREEN, width=2)
    canvas.line([(cx - r, cy), (cx + r, cy)], fill=CLIMATE_GREEN, width=2)
    canvas.line([(cx + 6, cy - 34), (cx - 4, cy - 12), (cx + 10, cy + 6),
                 (cx - 6, cy + 22), (cx + 4, cy + 34)],
                fill=JAVA_RED, width=4)
    canvas.line([(x + 8, y + 88), (x + 92, y + 88)], fill=RULE, width=3)


def glyph_capsized(canvas, x, y):
    # warship tipped on its side, bow above the waterline
    canvas.polygon([(x + 12, y + 30), (x + 88, y + 58), (x + 78, y + 72),
                    (x + 22, y + 52)], fill=LIBYA_NAVY)
    canvas.rectangle([x + 40, y + 34, x + 58, y + 48], fill=LIBYA_NAVY)
    canvas.line([x + 52, y + 20, x + 52, y + 34], fill=INK, width=3)
    canvas.polygon([(x + 52, y + 20), (x + 68, y + 26), (x + 52, y + 32)],
                   fill=COPPER)
    for wy in (80, 90):
        canvas.arc([x + 4, y + wy - 8, x + 34, y + wy + 8], 0, 180,
                   fill=LIBYA_NAVY, width=3)
        canvas.arc([x + 40, y + wy - 8, x + 70, y + wy + 8], 0, 180,
                   fill=LIBYA_NAVY, width=3)
    canvas.arc([x + 70, y + 8, x + 96, y + 34], 180, 360, fill=JAVA_RED,
               width=3)


def glyph_capitol(canvas, x, y):
    # capitol dome on columns with a small flag
    canvas.polygon([(x + 30, y + 40), (x + 70, y + 40), (x + 50, y + 12)],
                   fill=USA_COPPER)
    canvas.arc([x + 28, y + 22, x + 72, y + 58], 180, 360,
               fill=USA_COPPER, width=5)
    canvas.rectangle([x + 24, y + 56, x + 76, y + 62], fill=USA_COPPER)
    for cx in (30, 43, 57, 70):
        canvas.line([(x + cx, y + 62), (x + cx, y + 86)], fill=USA_COPPER,
                    width=4)
    canvas.rectangle([x + 18, y + 86, x + 82, y + 94], fill=USA_COPPER)
    canvas.line([x + 50, y + 2, x + 50, y + 14], fill=INK, width=2)
    canvas.polygon([(x + 50, y + 2), (x + 64, y + 6), (x + 50, y + 10)],
                   fill=JAVA_RED)


def glyph_flame(canvas, x, y):
    # flame over a factory roofline
    canvas.polygon([(x + 50, y + 6), (x + 74, y + 44), (x + 64, y + 60),
                    (x + 76, y + 52), (x + 66, y + 78), (x + 34, y + 78),
                    (x + 24, y + 52), (x + 36, y + 60), (x + 26, y + 44)],
                   fill=FLAME)
    canvas.polygon([(x + 50, y + 34), (x + 62, y + 56), (x + 38, y + 56)],
                   fill=(240, 170, 60))
    canvas.rectangle([x + 10, y + 80, x + 90, y + 94], fill=JAVA_RED)
    canvas.rectangle([x + 22, y + 68, x + 30, y + 80], fill=JAVA_RED)
    canvas.rectangle([x + 66, y + 68, x + 74, y + 80], fill=JAVA_RED)


def glyph_cracked_block(canvas, x, y):
    # apartment block split by a jagged crack, rubble at the base
    canvas.rectangle([x + 22, y + 8, x + 78, y + 84], fill=KYIV_SLATE)
    for wy in (22, 42, 62):
        for wx in (32, 52):
            canvas.rectangle([x + wx, y + wy, x + wx + 10, y + wy + 8],
                             fill=PAPER_LIGHT)
    canvas.line([(x + 52, y + 8), (x + 44, y + 30), (x + 56, y + 48),
                 (x + 46, y + 66), (x + 54, y + 84)],
                fill=JAVA_RED, width=4)
    canvas.polygon([(x + 8, y + 94), (x + 24, y + 80), (x + 40, y + 94)],
                   fill=SOFT_INK)
    canvas.polygon([(x + 44, y + 94), (x + 62, y + 78), (x + 80, y + 94)],
                   fill=SOFT_INK)
    canvas.polygon([(x + 82, y + 94), (x + 92, y + 84), (x + 96, y + 94)],
                   fill=SOFT_INK)


def glyph_exam(canvas, x, y):
    # exam paper under a magnifier, pencil crossed over it
    canvas.rectangle([x + 14, y + 8, x + 70, y + 88], fill=WHITE,
                     outline=KOREA_PLUM, width=3)
    for ly in (24, 38, 52, 66):
        canvas.line([(x + 24, y + ly), (x + 60, y + ly)],
                    fill=RULE, width=3)
    canvas.ellipse([x + 48, y + 48, x + 92, y + 92],
                   outline=KOREA_PLUM, width=4)
    canvas.line([(x + 84, y + 84), (x + 98, y + 98)], fill=KOREA_PLUM,
                width=5)
    canvas.line([(x + 62, y + 58), (x + 78, y + 82)], fill=JAVA_RED,
                width=4)
    canvas.line([(x + 78, y + 58), (x + 62, y + 82)], fill=JAVA_RED,
                width=4)


PANELS = [
    ("CLIMATE", CLIMATE_GREEN,
     "COP31 collapses with no deal",
     "Record overtime in Antalya ends with no deal: the final text drops "
     "any mention of fossil fuels. The EU and island states refuse it "
     "\u2014 the longest COP ever.",
     glyph_globe_crack),
    ("LIBYA", LIBYA_NAVY,
     "Russian warship sunk at Benghazi",
     "Suspected Ukrainian sea drones hit the Russian corvette Merkury at "
     "Benghazi. Satellite images show it capsized, bow above water; "
     "10 hurt. A Maltese-flagged ship is hit too.",
     glyph_capsized),
    ("USA", USA_COPPER,
     "Democrats take biggest House majority since 1992",
     "Chuck Hubbard beats Virginia Foxx in North Carolina\u2019s 5th by "
     "about 330 votes, giving Democrats at least 258 seats. Four races "
     "are still uncalled.",
     glyph_capitol),
    ("INDONESIA", JAVA_RED,
     "Candy factory fire: 24 body bags, dozens missing",
     "A blaze tears through the Milkita candy factory in Cikande, "
     "Serang. 24 body bags recovered by Sunday evening; about 30 still "
     "missing. DNA tests will take weeks.",
     glyph_flame),
    ("UKRAINE", KYIV_SLATE,
     "Drone collapses Kyiv apartment block",
     "A Russian drone destroys part of a five-storey block in Dymer, "
     "45 km north of Kyiv. One dead, 14 unaccounted for; Zelensky says "
     "2,700 drones hit Ukraine this week.",
     glyph_cracked_block),
    ("SOUTH KOREA", KOREA_PLUM,
     "Minister quits over AI exam-cheating scandal",
     "Education minister Choi Kyo-jin resigns after last-minute "
     "anti-cheating chaos before the CSAT. 111 device cases caught; a "
     "top scorer admitted using a mini camera and AI.",
     glyph_exam),
]


def render():
    img = Image.new("RGB", (SIDE, SIDE), TEAL_DEEP)
    canvas = ImageDraw.Draw(img)
    header_band(img, canvas)

    margin, gap = 16, 12
    top = 164
    cell_w = (SIDE - 2 * margin - gap) // 2
    cell_h = 265
    for i, (tag, colour, head, detail, glyph) in enumerate(PANELS):
        col, row = i % 2, i // 2
        x0 = margin + col * (cell_w + gap)
        y0 = top + row * (cell_h + gap)
        story_panel(canvas, (x0, y0, x0 + cell_w, y0 + cell_h),
                    tag, colour, head, detail, glyph)

    canvas.text((28, 994),
                "Sources: AP \u00b7 Reuters \u00b7 BBC \u00b7 France 24 \u00b7 "
                "Korea JoongAng Daily \u00b7 Xinhua \u2014 reported 22 Nov 2026",
                font=face(False, 16), fill=MIST)
    img.save(TARGET, format="PNG")
    return TARGET


if __name__ == "__main__":
    print(render())
