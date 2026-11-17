"""Build beat-plan configs for the 13-27 Nov 2026 Shorts from the research agents' JSON.

Usage: .venv/bin/python gen_nov13_27.py build      # writes batch_<name>.json for every candidate (primary + spare), validates
       .venv/bin/python gen_nov13_27.py dryrun     # Jev dry-run of every config -> topics_nov13_27/dryrun.json
       .venv/bin/python gen_nov13_27.py assign     # picks the final 45 (Jev-clean, priority order), writes plan_nov13_27.json
"""
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, ".claude/skills/football-shorts/scripts")
from shortbuild import build  # noqa: E402

D = "topics_nov13_27"
DONOR = "batch_ronaldo_wolfsburg_hattrick.json"
FILES = {"ronaldo": f"{D}/ronaldo.json", "messi": f"{D}/messi.json", "other": f"{D}/other.json"}
DAYS = list(range(13, 28))
MON = "NOV"


def load():
    out = {}
    for k, p in FILES.items():
        out[k] = json.load(open(p)) if os.path.exists(p) else []
    out["whatif"] = json.load(open(f"{D}/whatif.json")) if os.path.exists(f"{D}/whatif.json") else []
    return out


def check(t):
    w = []
    says = " ".join(b["says"] for b in t["beats"])
    n = len(says.split())
    if not 62 <= n <= 80:
        w.append(f"{n} words")
    if not 8 <= len(t["beats"]) <= 9:
        w.append(f"{len(t['beats'])} beats")
    if re.search(r"\d", says):
        w.append("digits in says")
    hook_words = {x.strip("?!.,'").lower() for x in t["hook"].split()} - {"the", "a", "of", "to", "in", "and", "his", "he", "it", "is", "was", "for"}
    first = {x.strip("?!.,'").lower() for x in t["beats"][0]["says"].split()}
    ov = hook_words & first
    if len(hook_words) and len(ov) / len(hook_words) >= 0.5:
        w.append(f"hook overlaps beat1 {sorted(ov)}")
    if len(t["hook"].split()) > 6:
        w.append("hook >6 words")
    if not t["cta"].endswith(" 👇"):
        w.append("cta format")
    if re.match(r"^(in|on|at)?\s*(january|february|march|april|may|june|july|august|september|october|november|december|\w+ twenty|\w+ nineteen)", t["beats"][0]["says"].lower()):
        w.append("beat1 starts with a date?")
    return n, w


def cmd_build():
    data = load()
    bad = 0
    for k in ("ronaldo", "messi", "other"):
        for t in data[k]:
            n, w = check(t)
            build(DONOR, f"batch_{t['name']}.json", subject=t["subject"], beats=t["beats"], hook=t["hook"], cta=t["cta"],
                  terms=t["terms"], cover=t["cover"], positives=t["positives"])
            if w:
                bad += 1
                print("  WARN", t["name"], w)
    print("built; configs with warnings:", bad)


def cmd_dryrun():
    data = load()
    res = {}
    for k in ("ronaldo", "messi", "other"):
        for t in data[k]:
            f = f"batch_{t['name']}.json"
            r = subprocess.run([".venv/bin/python", "batch_generator.py", f, "--dry-run"], capture_output=True, text=True, timeout=300)
            txt = re.sub(r"\x1b\[[0-9;]*m", "", r.stdout + r.stderr)
            blocks = [l.split("|")[-1].strip()[:160] for l in txt.splitlines() if "PREFLIGHT FAILED" in l or "Jev gate blocked" in l]
            res[t["name"]] = {"ok": "DRY_RUN_OK=1" in txt, "blocks": blocks}
            print(("OK  " if res[t["name"]]["ok"] else "FAIL"), t["name"], blocks[:1])
    json.dump(res, open(f"{D}/dryrun.json", "w"), indent=1)


def cmd_assign():
    data = load()
    dry = json.load(open(f"{D}/dryrun.json"))
    ok = lambda t: dry.get(t["name"], {}).get("ok")  # noqa: E731
    pools = {k: [t for t in data[k] if ok(t)] for k in ("ronaldo", "messi", "other")}
    skip = {"whatif_bellingham_slovakia_euro2024", "whatif_neymar_barcelona_remontada_2017"}  # same event as a normal Short
    wf = [x for x in data["whatif"] if x["name"] not in skip]
    plan = []
    ri = mi = oi = wi = 0
    for d in DAYS:
        odd = d % 2 == 1
        slots = [(1, "13:00", "messi" if odd else "ronaldo"), (2, "17:00", "whatif" if odd else "other"), (3, "21:00", "ronaldo" if odd else "messi")]
        for n, tm, kind in slots:
            if kind == "ronaldo":
                t = pools["ronaldo"][ri]; ri += 1
            elif kind == "messi":
                t = pools["messi"][mi]; mi += 1
            elif kind == "other":
                t = pools["other"][oi]; oi += 1
            else:
                t = wf[wi]; wi += 1
            out = f"{d}{MON}_slot{n}_{tm.replace(':','')}_{'WHATIF_' if kind=='whatif' else ''}{t['name'].replace('whatif_','')}"
            plan.append({"day": d, "slot": n, "time": tm, "kind": kind, "name": t["name"], "out": out,
                         "cfg": None if kind == "whatif" else f"batch_{t['name']}.json"})
    json.dump(plan, open(f"{D}/plan_nov13_27.json", "w"), indent=1)
    print(len(plan), "planned;", "used ron", ri, "messi", mi, "other", oi, "whatif", wi)
    print("spare left: ron", len(pools["ronaldo"]) - ri, "messi", len(pools["messi"]) - mi, "other", len(pools["other"]) - oi)


if __name__ == "__main__":
    {"build": cmd_build, "dryrun": cmd_dryrun, "assign": cmd_assign}[sys.argv[1]]()
