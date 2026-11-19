#!/usr/bin/env python3
"""NewsCut shot check: suggest a 9:16 crop for every shot of a spec and flag overlays inside the crop.

Usage (repo root, after the sources are cached, e.g. by `gen_newscut.py <spec> --no-render` or a manual download):
  python nc_shotcheck.py prototypes/newscut/<spec>.json            # report + annotated sheet, spec unchanged
  python nc_shotcheck.py prototypes/newscut/<spec>.json --apply    # also write x/y/h into shots that have no "x"
  python nc_shotcheck.py prototypes/newscut/<spec>.json --apply --overwrite   # replace every shot's x/y/h

What it does (Mirage via app/services/mirage_vision.py; ~1.3 s per frame on CPU, results cached):
  1. Per source video: 6 probe frames -> overlays that persist across frames (captions, corner logos, header
     bars). Ad boards and shirt numbers move with the camera and drop out.
  2. Crop rows: y / h chosen to keep persistent top bars and bottom captions out of the frame.
  3. Per shot: 3 probe frames over the shot's own window -> main subject box -> suggested crop "x".
     Corner logos inside the window are dodged by shifting x when the subject still fits.
  4. Prints current vs suggested x/y/h with warnings, and writes prototypes/newscut/out/<key>/shotcheck.jpg:
     red = the spec's current window, green = suggested, cyan = overlays, label = shot class.
Mirage cannot tell WHICH player is on screen: the right person is still your call on the sheet.
"""
import hashlib
import json
import os
import shutil
import statistics
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
from app.services import mirage_vision as mv  # noqa: E402

CACHE_VID = os.path.join(ROOT, "storage", "cache_videos", "comparison")
OUTDIR = os.path.join(ROOT, "prototypes", "newscut", "out")
FF = shutil.which("ffmpeg") or "ffmpeg"
FP = shutil.which("ffprobe") or "ffprobe"
PAD = 6  # px kept between the crop and an overlay


def source_path(vid):
    url = f"https://www.youtube.com/watch?v={vid}"
    d = os.path.join(CACHE_VID, hashlib.md5(url.encode()).hexdigest()[:12])
    if os.path.isdir(d):
        for f in sorted(os.listdir(d)):
            if f.startswith(vid + ".") and f.lower().endswith((".mp4", ".mkv", ".webm", ".mov")):
                return os.path.join(d, f)
    return None


def probe(path):
    r = subprocess.run([FP, "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height:format=duration",
                        "-of", "json", path], capture_output=True, text=True)
    j = json.loads(r.stdout)
    s = j["streams"][0]
    return int(s["width"]), int(s["height"]), float(j["format"]["duration"])


def grab(path, t, tmp, tag):
    out = os.path.join(tmp, f"{tag}_{t:.2f}.jpg")
    if not os.path.exists(out):
        subprocess.run([FF, "-v", "error", "-y", "-ss", f"{max(0.0, t):.3f}", "-i", path, "-frames:v", "1", "-q:v", "2", out],
                       capture_output=True)
    return out if os.path.exists(out) else None


def window_w(h):
    return int(round(h * 9 / 16 / 2) * 2)


def shot_times(spec, key):
    """(start, dur) in the Short for each shot, from the spec's chunk timing (gen_newscut --tts-only writes it)."""
    cj = os.path.join(OUTDIR, key, "chunks.json")
    shots = sorted(spec["shots"], key=lambda s: s["at"])
    if not os.path.exists(cj):
        return shots, [(i * 1.2, 1.2) for i in range(len(shots))]
    ch = json.load(open(cj, encoding="utf-8"))
    total = ch[-1]["t"] + 1.0
    st = [0.0 if i == 0 else ch[s["at"]]["t"] + float(s.get("shift", 0.0)) for i, s in enumerate(shots)]
    return shots, [(a, (st[i + 1] if i + 1 < len(st) else total) - a) for i, a in enumerate(st)]


def source_overlays(vid, path, W, H, dur, tmp):
    """-> (persistent overlay boxes, per-frame overlay candidates) from 6 probe frames of the whole source."""
    frames = [grab(path, dur * (0.05 + 0.9 * k / 5), tmp, vid) for k in range(6)]
    per = [mv.text_furniture(mv.describe(f)) for f in frames if f]
    return mv.persistent_furniture(per), per


def crop_rows(per_frame, H):
    """Rows clear of top header bars and bottom captions -> (y, h) in px.
    Judged per row band, not per box: word-by-word captions change text and x every frame (so they never
    'persist' as a box) but always sit in the same bottom band. A band counts when it has text in >= half the
    probe frames. Top band = text starting at the left edge or spanning >= 30% (header bars), so a lone
    corner logo is dodged with x instead of costing crop height."""
    n = max(1, len(per_frame))
    tops, bots = [], []
    for items in per_frame:
        tb = [i["box"] for i in items if i["kind"] == "text" and i["box"][3] <= 0.13
              and (i["box"][0] <= 0.25 or i["box"][2] - i["box"][0] >= 0.3)]
        bb = [i["box"] for i in items if i["kind"] == "text" and i["box"][1] >= 0.78]
        if tb:
            tops.append(max(b[3] for b in tb))
        if bb:
            bots.append(min(b[1] for b in bb))
    top = int(max(tops) * H) + PAD + int(0.02 * H) if len(tops) * 2 >= n else 0  # header bars run past their text
    bot = int(min(bots) * H) - PAD if len(bots) * 2 >= n else H
    return top, (bot - top) // 2 * 2


def overlaps(win, box, W, H):
    x, y, w, h = win
    bx0, by0, bx1, by1 = box[0] * W, box[1] * H, box[2] * W, box[3] * H
    return bx0 < x + w and bx1 > x and by0 < y + h and by1 > y


def suggest_x(cx_px, w, W, overlays, y, h, H):
    x = int(min(max(cx_px - w / 2, 0), W - w))
    for o in overlays:
        if o["box"][2] - o["box"][0] >= 0.3 or not overlaps((x, y, w, h), o["box"], W, H):  # dodge narrow overlays (logos, watermarks)
            continue
        lx0, lx1 = o["box"][0] * W, o["box"][2] * W
        for nx in (int(lx0 - w - PAD), int(lx1 + PAD)):
            nx = int(min(max(nx, 0), W - w))
            if nx + w * 0.15 <= cx_px <= nx + w * 0.85 and not overlaps((nx, y, w, h), o["box"], W, H):
                x = nx
                break
    return x


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags = {a for a in sys.argv[1:] if a.startswith("--")}
    if not args:
        raise SystemExit(__doc__)
    if not mv.available():
        raise SystemExit("Mirage is not installed: pip install cactus-compute (then it downloads ~23 MB on first use)")
    spec_path = args[0]
    spec = json.load(open(spec_path, encoding="utf-8"))
    key = spec["key"]
    shots, times = shot_times(spec, key)
    tmp = tempfile.mkdtemp(prefix="shotcheck_")
    src_info, rows, sheet_items = {}, [], []
    try:
        for i, (s, (t0, dur)) in enumerate(zip(shots, times)):
            if not s.get("vid"):
                rows.append((i, s, None, ["graphic shot, skipped"]))
                continue
            vid = s["vid"]
            if vid not in src_info:
                p = source_path(vid)
                if not p:
                    src_info[vid] = None
                else:
                    W, H, D = probe(p)
                    ov, per = source_overlays(vid, p, W, H, D, tmp)
                    src_info[vid] = (p, W, H, ov, crop_rows(per, H))
            info = src_info[vid]
            if not info:
                rows.append((i, s, None, [f"source {vid} not cached: run gen_newscut --no-render or download it"]))
                continue
            p, W, H, ov, (sy, sh) = info
            st = float(s["start"])
            length = dur + 0.35
            frames = [grab(p, st + length * f, tmp, vid) for f in (0.15, 0.5, 0.85)]
            descs = [mv.describe(f) for f in frames if f]
            boxes = [b for b in (mv.subject_box(d) for d in descs) if b]
            classes = [mv.shot_class(d) for d in descs]
            cls = max(set(classes), key=classes.count) if classes else "?"
            sw = window_w(sh)
            warn = []
            if boxes:
                cx = statistics.median([(b[0] + b[2]) / 2 for b in boxes]) * W
                sx = suggest_x(cx, sw, W, ov, sy, sh, H)
            else:
                cx = None
                sx = int(s.get("x", (W - sw) / 2))
                warn.append("no person found by Mirage: kept the current x")
            cur_h = int(s.get("h", s.get("srcH", H)))
            cur = (int(s["x"]), int(s.get("y", 0)), window_w(cur_h), cur_h) if "x" in s else None
            if cur:
                hit = [o for o in ov if overlaps(cur, o["box"], W, H)]
                if hit:
                    warn.append("current crop includes overlay: " + ", ".join(f"{o['kind']} '{o['text'][:18]}'" for o in hit))
                if cx is not None and not (cur[0] + cur[2] * 0.15 <= cx <= cur[0] + cur[2] * 0.85):
                    warn.append("subject is off-centre or outside the current crop")
            if [o for o in ov if overlaps((sx, sy, sw, sh), o["box"], W, H)]:
                warn.append("suggested crop still touches an overlay (logo next to the subject)")
            sug = {"x": sx, "y": sy, "h": sh}
            rows.append((i, s, (cls, cur, sug, W, H), warn))
            sheet_items.append((i, frames[1] or frames[0], cls, cur, (sx, sy, sw, sh), ov, W, H))
    finally:
        sheet = make_sheet(key, sheet_items)
        shutil.rmtree(tmp, ignore_errors=True)

    print(f"{key}: {len(shots)} shots   (cur = spec now, sug = suggested; x/y/h in source px)")
    changed = 0
    for i, s, res, warn in rows:
        if res is None:
            print(f"  {i:2d} at {s['at']:>2}  {s.get('vid', s.get('gfx', '?'))}: " + "; ".join(warn))
            continue
        cls, cur, sug, W, H = res
        cur_s = f"x {cur[0]:4d} y {cur[1]:3d} h {cur[3]:4d}" if cur else "x  -   y  -  h   - "
        print(f"  {i:2d} at {s['at']:>2}  {s['vid']} @{float(s['start']):7.2f}  {cls:6s}  cur {cur_s}  ->  sug x {sug['x']:4d} y {sug['y']:3d} h {sug['h']:4d}"
              + ("   ! " + "; ".join(warn) if warn else ""))
        if "--apply" in flags and ("x" not in s or "--overwrite" in flags):
            s["x"], s["y"], s["h"] = sug["x"], sug["y"], sug["h"]
            changed += 1
    if "--apply" in flags:
        json.dump(spec, open(spec_path, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
        print(f"applied suggestions to {changed} shot(s) in {spec_path}")
    if sheet:
        print("sheet:", sheet)


def make_sheet(key, items):
    if not items:
        return None
    from PIL import Image, ImageDraw, ImageFont
    try:
        font = ImageFont.truetype("arialbd.ttf", 22)
    except Exception:
        font = ImageFont.load_default()
    tw = 480
    tiles = []
    for i, f, cls, cur, sug, ov, W, H in items:
        im = Image.open(f).convert("RGB")
        k = tw / W
        im = im.resize((tw, int(H * k)))
        d = ImageDraw.Draw(im)
        for o in ov:
            b = o["box"]
            d.rectangle([b[0] * tw, b[1] * H * k, b[2] * tw, b[3] * H * k], outline=(0, 230, 255), width=2)
        if cur:
            d.rectangle([cur[0] * k, cur[1] * k, (cur[0] + cur[2]) * k, (cur[1] + cur[3]) * k], outline=(255, 50, 50), width=3)
        d.rectangle([sug[0] * k, sug[1] * k, (sug[0] + sug[2]) * k, (sug[1] + sug[3]) * k], outline=(60, 255, 60), width=3)
        d.rectangle([0, 0, 150, 28], fill="black")
        d.text((4, 3), f"{i}  {cls}", fill="yellow", font=font)
        tiles.append(im)
    cols = 4
    th = max(t.height for t in tiles)
    rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * tw, rows * th), "black")
    for n, t in enumerate(tiles):
        sheet.paste(t, ((n % cols) * tw, (n // cols) * th))
    os.makedirs(os.path.join(OUTDIR, key), exist_ok=True)
    out = os.path.join(OUTDIR, key, "shotcheck.jpg")
    sheet.save(out, quality=85)
    return out


if __name__ == "__main__":
    main()
