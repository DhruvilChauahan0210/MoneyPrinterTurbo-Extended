"""Channel logo (800x800) and banner (2560x1440, text inside the 1546x423 safe area) for the NewsCut channel.
Colours and fonts match the NewsCut Shorts (yellow #ffe400, red #ff2d2d, Impact). Run: .venv/bin/python make_brand.py"""
import math
import os

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
IMPACT = "/System/Library/Fonts/Supplemental/Impact.ttf"
BLACK_F = "/System/Library/Fonts/Supplemental/Arial Black.ttf"
YEL, RED, WHITE = (255, 228, 0), (255, 45, 45), (255, 255, 255)


def bg(w, h):
    """Near-black radial background with faint pitch lines."""
    im = Image.new("RGB", (w, h))
    px = im.load()
    cx, cy, R = w / 2, h / 2, math.hypot(w, h) / 2
    for y in range(h):
        for x in range(0, w):
            d = math.hypot(x - cx, (y - cy) * 1.15) / R
            v = max(0.0, 1 - d)
            px[x, y] = (int(8 + 22 * v), int(10 + 24 * v), int(18 + 40 * v))
    return im


def outlined(draw, xy, text, font, fill, stroke, sw, anchor="mm"):
    draw.text(xy, text, font=font, fill=fill, stroke_width=sw, stroke_fill=stroke, anchor=anchor)


def logo():
    S = 1600                                     # draw at 2x, downscale for clean edges
    im = bg(S, S)
    d = ImageDraw.Draw(im, "RGBA")
    c = S / 2
    d.ellipse([c - 560, c - 560, c + 560, c + 560], outline=(255, 255, 255, 40), width=10)   # centre circle
    d.line([(0, c), (S, c)], fill=(255, 255, 255, 28), width=10)                              # halfway line
    # red speed bar behind the letters
    d.polygon([(130, 980), (1470, 840), (1470, 960), (130, 1100)], fill=RED + (255,))
    glow = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    f = ImageFont.truetype(IMPACT, 820)
    gd.text((c, c - 40), "CD", font=f, fill=YEL + (150,), anchor="mm")
    glow = glow.filter(ImageFilter.GaussianBlur(40))
    im.paste(glow, (0, 0), glow)
    d = ImageDraw.Draw(im, "RGBA")
    outlined(d, (c + 14, c - 26), "CD", f, (0, 0, 0), (0, 0, 0), 34)                   # drop shadow
    outlined(d, (c, c - 40), "CD", f, YEL, (0, 0, 0), 26)
    fn = ImageFont.truetype(BLACK_F, 120)
    tw = d.textlength("NEWS", font=fn)
    d.rounded_rectangle([c - tw / 2 - 50, 1200, c + tw / 2 + 50, 1370], radius=26, fill=WHITE)
    d.text((c, 1287), "NEWS", font=fn, fill=(12, 14, 22), anchor="mm")
    im = im.resize((800, 800), Image.LANCZOS)
    im.save(os.path.join(HERE, "logo_800.png"))


def banner():
    W, H = 2560, 1440
    im = bg(W, H)
    d = ImageDraw.Draw(im, "RGBA")
    # diagonal stripes on both sides (seen on TV / desktop width)
    for x0, wd, col in [(-260, 70, YEL + (255,)), (-150, 46, RED + (255,)), (-60, 22, YEL + (110,))]:
        d.polygon([(x0, H), (x0 + wd, H), (x0 + wd + 520, 0), (x0 + 520, 0)], fill=col)
        d.polygon([(W - x0, 0), (W - x0 - wd, 0), (W - x0 - wd - 520, H), (W - x0 - 520, H)], fill=col)
    # pitch halfway line + centre circle, faint
    d.ellipse([W / 2 - 330, H / 2 - 330, W / 2 + 330, H / 2 + 330], outline=(255, 255, 255, 22), width=8)
    cx, cy = W / 2, H / 2                      # safe area: 1546 x 423 centred
    f1 = ImageFont.truetype(IMPACT, 190)
    f2 = ImageFont.truetype(IMPACT, 130)
    fs = ImageFont.truetype(BLACK_F, 44)
    outlined(d, (cx + 8, cy - 92 + 8), "FOOTBALL NEWS", f1, (0, 0, 0), (0, 0, 0), 10)
    outlined(d, (cx, cy - 92), "FOOTBALL NEWS", f1, WHITE, (0, 0, 0), 8)
    outlined(d, (cx + 6, cy + 62 + 6), "IN 30 SECONDS", f2, (0, 0, 0), (0, 0, 0), 8)
    outlined(d, (cx, cy + 62), "IN 30 SECONDS", f2, YEL, (0, 0, 0), 7)
    tag = "NEW SHORTS EVERY DAY"
    tw = d.textlength(tag, font=fs)
    d.rounded_rectangle([cx - tw / 2 - 34, cy + 150, cx + tw / 2 + 34, cy + 208], radius=14, fill=RED)
    d.text((cx, cy + 179), tag, font=fs, fill=WHITE, anchor="mm")
    im.save(os.path.join(HERE, "banner_2560x1440.png"))
    # preview of what phones show (the safe area)
    im.crop((int(cx - 773), int(cy - 212), int(cx + 773), int(cy + 211))).save(os.path.join(HERE, "banner_safe_preview.png"))


logo()
banner()
print("done")
