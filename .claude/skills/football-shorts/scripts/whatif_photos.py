"""Source candidate era photos for a What-If Short and write a numbered pick sheet.

Usage (from the repo root):
  PYTHONPATH=. .venv/bin/python <skill>/scripts/whatif_photos.py OUTDIR KEY "query 1" "query 2" ...
Writes OUTDIR/KEY/ (images + list.json) and OUTDIR/wi_KEY.jpg (sheet; label = index + width).
Pick an index, then save that image as whatif-remotion/public/wi_<name>.jpg (prefer portrait, >= 500px wide).
"""
import json
import os
import sys

from PIL import Image, ImageDraw

from app.services import material

out, key, queries = sys.argv[1], sys.argv[2], sys.argv[3:]
d = os.path.join(out, key)
os.makedirs(d, exist_ok=True)
paths = []
for q in queries:
    for h in material.search_images_duckduckgo(q, max_results=10):
        try:
            p = material.save_image(h.url, d, q)
            if p:
                paths.append(p)
        except Exception:
            pass
ims = []
for p in paths[:16]:
    try:
        im = Image.open(p).convert("RGB")
        if im.width >= 500:
            ims.append((p, im))
    except Exception:
        pass
json.dump([p for p, _ in ims], open(os.path.join(d, "list.json"), "w"), indent=1)
W, H = 220, 300
c = Image.new("RGB", (W * 8, H * 2 + 40), "black")
dr = ImageDraw.Draw(c)
for i, (p, im) in enumerate(ims[:16]):
    im.thumbnail((W, H))
    x, y = (i % 8) * W, (i // 8) * (H + 20) + 20
    c.paste(im, (x, y))
    dr.text((x + 4, y - 16), f"{i} {im.width}", fill="yellow")
c.save(os.path.join(out, f"wi_{key}.jpg"), quality=80)
print(key, len(ims), "candidates ->", os.path.join(out, f"wi_{key}.jpg"))
