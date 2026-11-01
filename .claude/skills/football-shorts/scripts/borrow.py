"""Fill a beat with no usable photo by borrowing a spare candidate from another beat: borrow.py cfg beat src_beat idx"""
import json, sys
cfg, beat, src, idx = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
d = json.load(open(cfg))
for bp in (d["videos"][0]["beat_plan"], d["defaults"]["beat_plan"]):
    if len(bp) >= beat:
        cand = d["videos"][0]["beat_plan"][src - 1]["candidates"][idx]
        bp[beat - 1]["media"] = cand
json.dump(d, open(cfg, "w"), indent=2, ensure_ascii=False)
print(cfg, f"b{beat} <- b{src}[{idx}]")
