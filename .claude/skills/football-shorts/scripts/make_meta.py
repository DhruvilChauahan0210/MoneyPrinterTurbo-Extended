"""Build meta.json for sched.js from a compact spec (same text as the chat metadata).

Usage: python3 make_meta.py spec.json OUT/meta.json
spec.json = [
  {"file": "12NOV_slot1_1300_ronaldo_x.mp4", "date": "12 Nov 2026", "time": "13:00",
   "hook": "Ronaldo SCORED 3 in 15 minutes",          # title = hook + " 😳 #halo try this sound #shorts"
   "p1": "...", "p2": "...",                          # the two description paragraphs
   "hashtags": "#CristianoRonaldo #Ronaldo #CR7 ...", # topic hashtags only (5-7); #halo + generic tail added
   "tags": "cristiano ronaldo, ronaldo, ..."},        # 14 topic tags; generic 6 appended
  ...]
Dates must look exactly like Studio shows them ("3 Nov 2026"), times are 24h IST ("17:00").
"""
import json
import sys

G = "#Football #Soccer #FootballShorts #Futbol #shorts #fyp #viral"
T = "football shorts, soccer shorts, football news, futbol, football edit, football facts"

spec = json.load(open(sys.argv[1]))
out = []
for s in spec:
    out.append({
        "file": s["file"], "date": s["date"], "time": s["time"],
        "title": s["hook"] + " 😳 #halo try this sound #shorts",
        "description": f"{s['p1']}\n\n{s['p2']}\n\nFollow for more football shorts ⚡\n\n#halo {s['hashtags']} {G}",
        "tags": f"{s['tags']}, {T}",
    })
json.dump(out, open(sys.argv[2], "w"), ensure_ascii=False, indent=1)
print(len(out), "entries ->", sys.argv[2])
