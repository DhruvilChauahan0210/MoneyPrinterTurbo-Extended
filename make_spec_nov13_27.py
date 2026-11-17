"""Build the scheduling spec (for make_meta.py) and the chat metadata for the 13-27 Nov Shorts."""
import json
D = "topics_nov13_27"
plan = json.load(open(f"{D}/plan_nov13_27.json"))
src = {}
for k in ("ronaldo", "messi", "other", "whatif"):
    for t in json.load(open(f"{D}/{k}.json")):
        src[t["name"]] = t
spec = []
for p in plan:
    t = src[p["name"]]
    spec.append({"file": p["out"] + ".mp4", "date": f"{p['day']} Nov 2026", "time": p["time"], "hook": t["title_hook"],
                 "p1": t["p1"], "p2": t["p2"], "hashtags": t["hashtags"], "tags": t["tags"], "pinned": t["pinned"], "name": p["name"]})
json.dump(spec, open(f"{D}/spec_nov13_27.json", "w"), ensure_ascii=False, indent=1)
bad = []
for s in spec:
    nt = len([x for x in s["tags"].split(",") if x.strip()])
    nh = len(s["hashtags"].split())
    title = s["hook"] + " 😳 #halo try this sound #shorts"
    caps = [w for w in s["hook"].split() if w.isupper() and len(w) > 2 and not any(c.isdigit() for c in w)]
    if nt != 14 or not 5 <= nh <= 7 or len(title) > 100 or len(caps) != 1:
        bad.append((s["name"], f"tags={nt} hashtags={nh} titlelen={len(title)} caps={caps}"))
print(len(spec), "entries; issues:", len(bad))
for b in bad: print("  ", b)
