"""Compact pick sheet: one row per beat, top N candidates as 150px-tall thumbs."""
import json, sys
from PIL import Image, ImageDraw
cfg, out = sys.argv[1], sys.argv[2]
N = int(sys.argv[3]) if len(sys.argv) > 3 else 6
bp = json.load(open(cfg))["videos"][0]["beat_plan"]
TH, TW = 150, 140
rows = []
for i, b in enumerate(bp, 1):
    row = Image.new("RGB", (TW * N + 260, TH + 4), "black")
    d = ImageDraw.Draw(row)
    d.text((4, 4), f"B{i}", fill="red")
    words = b["says"].split(); line = ""; y = 20
    for w in words:
        if len(line + w) > 34: d.text((4, y), line, fill="white"); y += 12; line = ""
        line += w + " "
    d.text((4, y), line, fill="white")
    for j, p in enumerate((b.get("candidates") or [])[:N]):
        try:
            im = Image.open(p).convert("RGB"); im.thumbnail((TW - 4, TH))
            row.paste(im, (260 + j * TW, 2)); d.text((262 + j * TW, 2), str(j), fill="yellow")
        except Exception:
            pass
    rows.append(row)
H = sum(r.height for r in rows); W = rows[0].width
c = Image.new("RGB", (W, H), "black"); y = 0
for r in rows: c.paste(r, (0, y)); y += r.height
c.save(out, quality=82)
