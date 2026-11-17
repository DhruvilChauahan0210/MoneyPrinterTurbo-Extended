"""Pin clips for the R3 Yamal prototype (R1 approach: fetch_exact_clip, 6 s pins, middle window plays)."""
import hashlib, json, os, re, sys
from app.services import auto_footage

CFG = "batch_proto_r3_yamal_euro24_birthday.json"
E = "lBOS43RWfY0"      # England channel: Spain v England broadcast highlights
R = "O15L1ZzsKdw"      # RTBF trophy presentation
# renderer plays the MIDDLE of each 6 s pin: start = wanted_centre - 3
PINS = {
    2: (E, 2.0), 3: (E, 239.0), 4: (E, 293.0), 5: (E, 117.5), 6: (E, 123.0),
    7: (E, 333.5), 8: (E, 387.5), 9: (R, 226.5), 10: (R, 63.4), 11: (R, 233.0),
}
LEN = 6.0
MANUAL = {10: 790}   # Yamal walks mid-right on the podium; auto crop cut him out
CENTER = {2}
from app.services import craft
_orig = craft.subject_window
only = {int(x) for x in sys.argv[1].split(",")} if len(sys.argv) > 1 else set(PINS)
data = json.load(open(CFG, encoding="utf-8"))
plan = data["videos"][0]["beat_plan"]
slug = re.sub(r"[^a-z0-9]+", "_", data["videos"][0]["video_subject"].lower()).strip("_")[:40]
root = os.path.join("storage", "beats", slug)
for n, (vid, st) in PINS.items():
    if n not in only:
        continue
    url = f"https://www.youtube.com/watch?v={vid}"
    out_dir = os.path.join(root, f"b{n:02d}")
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, f"shot_{hashlib.md5(f'{url}@{st}'.encode()).hexdigest()[:10]}.mp4")
    if not (os.path.exists(out) and os.path.getsize(out) > 10000):
        auto_footage._REJECT_BURNED_IN_TEXT = False
        craft.subject_window = ((lambda *a, **k: None) if n in CENTER else
                                (lambda *a, **k: {"w": 606, "h": 1080, "x": MANUAL[n], "y": 0, "method": "manual"}) if n in MANUAL else _orig)
        got = auto_footage.fetch_exact_clip(url, st, st + LEN, 1080, 1920, out, max_height=1080,
                                            max_filesize_mb=600, fill="cover", retries=2)
        if not got:
            print(f"beat {n}: FAILED"); continue
    data = json.load(open(CFG, encoding="utf-8"))
    b = data["videos"][0]["beat_plan"][n - 1]
    b.update(url=url, start=st, len=LEN, media=os.path.abspath(out))
    json.dump(data, open(CFG, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    print(f"beat {n}: ok {out}")
