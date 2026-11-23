#!/usr/bin/env python3
"""THE WORLD IN ONE PAGE -- Monday 23 November 2026.

A single-file, stdlib-only program that draws a newspaper front page
summing up the world's news of Monday 23 November 2026 and writes it
to /output/entry.png as a 1024x1024 PNG.

Everything is drawn programmatically: a hand-built 5x7 bitmap font,
rectangles, circles and lines, plus a hand-rolled PNG encoder
(zlib + struct). No network, no external files, no randomness, so
every run produces byte-identical output.

Stories (all first reported on Monday 23 November 2026):
  Lead   Democrats clinch at least 258 US House seats (AP) -- the
         largest House majority for either party since 1992.
  Markets  AI rout: S&P 500 -3.7%, Nasdaq -5.3% on Friday; KOSPI -5%
         on Monday; Dow futures +700; Asian regulators step in.
  Iran   Trump warns Iranian ships running the blockade will be sunk;
         inclined to resume strikes if no deal by the New Year.
  Ukraine  Ukrainian naval drone severely damages Russian corvette
         Merkury off Libya; cargo ship MV Angara also hit.
  Indonesia  Banten candy-factory fire: 24 confirmed dead, ~30 missing.
  Sport  FIFA set to confirm the UK as host of the 2035 Women's
         World Cup.
  Tech   US seeks answers from Nvidia over chip sales to China;
         Anthropic shares slide after its record IPO.
  Mexico  Cartel leader Fausto Isidro "Chapo Isidro" Meza-Flores
         captured in Sinaloa.
"""

import binascii
import os
import struct
import zlib

W, H = 1024, 1024
OUT_PATH = "/output/entry.png"

# ---------------------------------------------------------------- palette
PAPER = (247, 242, 231)   # newsprint cream
PANEL = (238, 232, 214)   # slightly darker cream for the art box
INK = (26, 26, 26)        # near-black ink
RED = (176, 42, 30)       # headline red
BLUE = (31, 78, 121)      # Democrat blue
NAVY = (20, 40, 70)       # markets strip
GREY = (120, 112, 96)     # hairlines
WHITE = (255, 255, 255)
SKY = (214, 226, 236)     # art-box sky

# ------------------------------------------------------- 5x7 bitmap font
# Each glyph is 7 rows of 5 bits, written out by hand for this program.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "—": ("00000", "00000", "00000", "11111", "00000", "00000", "00000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "+": ("00000", "00100", "00100", "01110", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    "*": ("00000", "00100", "10101", "01110", "10101", "00100", "00000"),
    "#": ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    "•": ("00000", "00000", "01100", "01100", "01100", "00000", "00000"),
}
BLANK = ("00000",) * 7


def text_width(text, scale):
    """Pixel width of text drawn at the given scale."""
    return len(text) * 6 * scale - scale if text else 0


def wrap(text, scale, max_w):
    """Greedy word wrap; returns a list of lines fitting max_w pixels."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = word if not cur else cur + " " + word
        if text_width(trial, scale) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ------------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(w * h * 3)
        self.fill_rect(0, 0, w, h, bg)

    def set_pixel(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = color

    def fill_rect(self, x, y, w, h, color):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        r, g, b = color
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.px[i], self.px[i + 1], self.px[i + 2] = r, g, b

    def outline(self, x, y, w, h, color, t=1):
        self.fill_rect(x, y, w, t, color)
        self.fill_rect(x, y + h - t, w, t, color)
        self.fill_rect(x, y, t, h, color)
        self.fill_rect(x + w - t, y, t, h, color)

    def vline(self, x, y0, y1, color, t=1):
        self.fill_rect(x, min(y0, y1), t, abs(y1 - y0) + 1, color)

    def hline(self, x0, x1, y, color, t=1):
        self.fill_rect(min(x0, x1), y, abs(x1 - x0) + 1, t, color)

    def filled_circle(self, cx, cy, r, color):
        for dy in range(-r, r + 1):
            dx = int((r * r - dy * dy) ** 0.5)
            self.fill_rect(cx - dx, cy + dy, 2 * dx + 1, 1, color)

    def dome(self, cx, base_y, r, color):
        """Top half of a filled circle: a dome sitting on base_y."""
        for dy in range(-r, 1):
            dx = int((r * r - dy * dy) ** 0.5)
            self.fill_rect(cx - dx, base_y + dy, 2 * dx + 1, 1, color)

    def draw_text(self, x, y, text, scale, color):
        text = text.upper()  # the bitmap font only carries capitals
        cx = x
        for ch in text:
            glyph = FONT.get(ch, BLANK)
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits[col] == "1":
                        self.fill_rect(cx + col * scale, y + row * scale,
                                       scale, scale, color)
            cx += 6 * scale

    def draw_centered(self, cx, y, text, scale, color):
        self.draw_text(cx - text_width(text, scale) // 2, y, text, scale, color)

    def draw_right(self, right_x, y, text, scale, color):
        self.draw_text(right_x - text_width(text, scale), y, text, scale, color)


# ------------------------------------------------------------- PNG encoding
def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", binascii.crc32(kind + data) & 0xFFFFFFFF)
    return out


def write_png(path, w, h, px):
    raw = bytearray()
    for y in range(h):
        raw.append(0)  # filter: none
        raw += px[y * w * 3:(y + 1) * w * 3]
    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += _chunk(b"IHDR", ihdr)
    png += _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += _chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)


# ------------------------------------------------------------ illustrations
def draw_capitol(cv, cx, base_y):
    """A stylised US Capitol dome, drawn from shapes, in navy + red."""
    r = 48
    # flag pole and flag above the dome
    cv.vline(cx, base_y - r - 24, base_y - r, INK, 2)
    cv.fill_rect(cx + 2, base_y - r - 24, 24, 13, RED)
    # dome, drum, columns, steps
    cv.dome(cx, base_y, r, NAVY)
    cv.fill_rect(cx - 6, base_y - r - 8, 12, 8, NAVY)  # lantern
    cv.fill_rect(cx - 52, base_y, 104, 14, NAVY)       # drum
    for i in range(6):                                  # columns
        cv.fill_rect(cx - 48 + i * 18, base_y + 14, 8, 32, NAVY)
    cv.fill_rect(cx - 56, base_y + 46, 112, 8, NAVY)    # entablature
    cv.fill_rect(cx - 64, base_y + 54, 128, 6, NAVY)    # steps
    cv.fill_rect(cx - 72, base_y + 60, 144, 6, NAVY)


def draw_lead_art(cv, x, y, w, h):
    """Right-hand lead art box: the 258-seat House, a seat bar, a dome."""
    cx = x + w // 2
    cv.fill_rect(x, y, w, h, PANEL)
    cv.outline(x, y, w, h, INK, 2)
    cv.draw_centered(cx, y + 10, "THE NEW HOUSE", 2, INK)
    cv.draw_centered(cx, y + 32, "258", 8, RED)
    cv.draw_centered(cx, y + 96, "DEMOCRAT SEATS OF 435", 2, INK)
    # seat bar: 258 of 435 seats blue, the rest red
    bar_x, bar_y, bar_w, bar_h = x + 20, y + 122, w - 40, 20
    blue_w = bar_w * 258 // 435
    cv.fill_rect(bar_x, bar_y, blue_w, bar_h, BLUE)
    cv.fill_rect(bar_x + blue_w, bar_y, bar_w - blue_w, bar_h, RED)
    cv.outline(bar_x, bar_y, bar_w, bar_h, INK, 1)
    cv.draw_text(bar_x + 8, bar_y + 7, "DEM 258", 1, WHITE)
    cv.draw_text(bar_x + blue_w + 8, bar_y + 7, "REP 177", 1, WHITE)
    draw_capitol(cv, cx, y + 234)  # dome + steps must end inside the box


def draw_story(cv, x, y, w, h, accent, kicker, headline, body):
    cv.fill_rect(x, y, w, 6, accent)
    cv.draw_text(x, y + 14, kicker, 2, RED)
    hy = y + 38
    for line in wrap(headline, 2, w):
        cv.draw_text(x, hy, line, 2, INK)
        hy += 20
    cv.fill_rect(x, hy + 2, w, 1, GREY)
    by = hy + 12
    for line in wrap(body, 2, w)[:5]:
        cv.draw_text(x, by, line, 2, INK)
        by += 19


# ------------------------------------------------------------------- layout
def build():
    cv = Canvas(W, H, PAPER)
    cv.outline(16, 16, W - 32, H - 32, INK, 2)

    # ---- masthead
    cv.draw_centered(W // 2, 34, "THE WORLD IN ONE PAGE", 6, INK)
    cv.draw_text(28, 92, "VOL. I - NO. 327", 1, INK)
    cv.draw_right(996, 92, "PRICE: FREE", 1, INK)
    cv.draw_centered(W // 2, 88, "MONDAY 23 NOVEMBER 2026", 3, INK)
    cv.draw_centered(W // 2, 120, "ONE DAY  •  ONE PAGE  •  ONE PICTURE", 2, INK)
    cv.fill_rect(28, 146, 968, 2, INK)
    cv.fill_rect(28, 151, 968, 1, INK)

    # ---- lead story: Democrats' historic House majority
    cv.draw_text(28, 172, "UNITED STATES — POLITICS", 2, RED)
    for i, line in enumerate(("DEMOCRATS WIN",
                             "HISTORIC 258-SEAT",
                             "HOUSE MAJORITY")):
        cv.draw_text(28, 200 + i * 32, line, 4, INK)
    cv.fill_rect(28, 304, 532, 1, GREY)
    lead_p1 = ("Democrats clinched at least 258 seats in the US House of "
               "Representatives, the Associated Press reported on Monday "
               "— the largest majority for either party since 1992.")
    lead_p2 = ("The result hands the party control of the chamber when the "
               "new term begins on 3 January, with a funding deadline "
               "looming on 11 December.")
    by = 318
    for line in wrap(lead_p1, 2, 532):
        cv.draw_text(28, by, line, 2, INK)
        by += 18
    by += 6
    for line in wrap(lead_p2, 2, 532):
        cv.draw_text(28, by, line, 2, INK)
        by += 18
    draw_lead_art(cv, 576, 166, 420, 302)

    # ---- markets strip
    cv.fill_rect(28, 480, 968, 56, NAVY)
    cv.draw_text(44, 501, "MARKETS", 2, WHITE)
    cv.draw_text(164, 501,
                 "S&P 500 -3.7%  NASDAQ -5.3%  KOSPI -5.0%  "
                 "DOW FUT +700  GOLD $3,515", 2, WHITE)

    # ---- six more stories, 3 columns x 2 rows
    stories = [
        ("IRAN — GULF", "TRUMP: WE WILL SINK IRANIAN SHIPS",
         "Trump warned ships running the blockade will be sunk, and said "
         "he may resume strikes if no deal is reached by the New Year."),
        ("UKRAINE — WAR AT SEA", "KYIV DRONE HITS RUSSIAN WARSHIP",
         "A Ukrainian naval drone severely damaged the Russian corvette "
         "Merkury off Libya. The cargo ship MV Angara was also hit."),
        ("INDONESIA — DISASTER", "FACTORY FIRE TOLL REACHES 24",
         "Rescuers searched the ruins of a candy factory in Banten on "
         "Monday after the weekend blaze. 24 are dead, about 30 missing."),
        ("SPORT — FOOTBALL", "UK TO HOST 2035 WOMEN'S CUP",
         "FIFA is set to confirm the United Kingdom as host of the 2035 "
         "Women's World Cup on Monday, the first in the UK since 1966."),
        ("TECH — CHIPS", "NVIDIA PRESSED ON CHINA CHIPS",
         "The US is seeking answers from Nvidia over chip sales to China, "
         "Bessent said. Anthropic shares slid after its record IPO."),
        ("MEXICO — CARTELS", "'CHAPO ISIDRO' CAPTURED",
         "Mexican forces seized cartel leader Fausto Isidro Meza-Flores, "
         "wanted by the US on a $5m bounty, in a firefight in Sinaloa."),
    ]
    accents = (RED, BLUE, RED, BLUE, RED, BLUE)
    for i, (kicker, headline, body) in enumerate(stories):
        col, row = i % 3, i // 3
        draw_story(cv, 28 + col * 328, 548 + row * 216, 312, 200,
                   accents[i], kicker, headline, body)

    # ---- footer
    cv.fill_rect(28, 968, 968, 1, GREY)
    cv.draw_centered(W // 2, 978,
                     "SUMMING UP MONDAY 23 NOVEMBER 2026 — "
                     "SOURCES: AP • REUTERS • XINHUA • DOW JONES", 1, INK)
    return cv


def main():
    cv = build()
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    write_png(OUT_PATH, W, H, cv.px)
    print("wrote", OUT_PATH, "1024x1024")


if __name__ == "__main__":
    main()
