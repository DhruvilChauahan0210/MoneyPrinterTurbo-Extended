"""Pin clips for the R1 prototype. beat_source --replace is broken for long sources (yt-dlp --download-sections leaves
261-byte sec.mp4 stubs), so download each source once and cut with auto_footage.fetch_exact_clip."""
import hashlib, json, os, re, sys
from app.services import auto_footage

CFG = "batch_proto_r1_ballondor2021.json"
# NOTE: the renderer plays the MIDDLE of each pinned 6 s clip (start + (6-beat_dur)/2), so start = wanted_first_second - (6-beat_dur)/2.
PINS = {  # beat: (video id, start)
    1: ("ETHUhf058N8", 99.77), 2: ("ETHUhf058N8", 35.03), 3: ("ETHUhf058N8", 39.5),
    4: ("-lj5evUDzK8", 206.05), 5: ("-lj5evUDzK8", 148.9), 6: ("yawKKBlWTyY", 267.8),
    7: ("yawKKBlWTyY", 19.8), 8: ("6tLxv5EsszA", 154.74), 9: ("6tLxv5EsszA", 191.5),
    10: ("ETHUhf058N8", 6.0), 11: ("ETHUhf058N8", 192.4), 12: ("ETHUhf058N8", 226.35),
}
LEN = 6.0
LEFT = {3: 506, 8: 1000}   # Lewandowski sits left of frame in the ceremony wide shot
CENTER = {1, 2, 11}   # craft.subject_window picked sequins/sleeve on the podium shots: force dead-centre crop
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
                                (lambda *a, **k: {"w": 606, "h": 1080, "x": LEFT[n], "y": 0, "method": "manual"}) if n in LEFT else _orig)
        got = auto_footage.fetch_exact_clip(url, st, st + LEN, 1080, 1920, out, max_height=1080,
                                            max_filesize_mb=600, fill="cover", retries=2)
        if not got:
            print(f"beat {n}: FAILED"); continue
    b = plan[n - 1]
    b.update(url=url, start=st, len=LEN, media=os.path.abspath(out))
    print(f"beat {n}: ok {out}")
    json.dump(data, open(CFG, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
