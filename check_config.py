#!/usr/bin/env python
"""Pre-flight budget check for batch configs.

Why this exists: on 28 Aug 2026 build failures spiked. The engine had not changed
(`git diff HEAD -- app/` was empty). The cause was config drift — negative labels had
grown 35->61 and hook negatives 11->33 versus the configs that shipped cleanly in July,
while the series ledger + banlist had permanently blocked 183 clips. Every negative and
every blocked clip is one more way for a candidate to be rejected, so the pool starved
and the gate either aborted or kept only junk (hands, backs, distant figures).

Budgets below are taken from configs that demonstrably shipped. Exceeding them is not
fatal, but it is the first thing to suspect when builds start failing.
"""
import json, sys, os

BUDGET = {
    "subject_negative_labels": 45,   # July baseline 35
    "hook_negative_labels":    18,   # July baseline 11
}
FLOOR_MIN   = 0.30                   # July baseline 0.35; lowering this lets junk through
LEDGER_MAX  = 20                     # rolling window, not an all-time ban
BANLIST_MAX = 160

def check(path):
    d = json.load(open(path)); df = d.get("defaults", {}); warn = []
    for key, cap in BUDGET.items():
        n = len(df.get(key) or [])
        if n > cap:
            warn.append(f"{key}={n} > {cap} (over budget; prune before adding more)")
    floor = df.get("subject_gate_abs_floor")
    if floor is not None and floor < FLOOR_MIN:
        warn.append(f"subject_gate_abs_floor={floor} < {FLOOR_MIN} (loosening the gate "
                    f"hides pool starvation instead of fixing it)")
    led = (df.get("series_ledger_path") or "").strip()
    if led and os.path.exists(led):
        n = len(json.load(open(led)))
        if n > LEDGER_MAX:
            warn.append(f"series ledger has {n} entries > {LEDGER_MAX} "
                        f"(trim to a rolling window or every episode starves the next)")
        bl = os.path.join(os.path.dirname(led), "series_media_banlist.json")
        if os.path.exists(bl):
            n = len(json.load(open(bl)))
            if n > BANLIST_MAX:
                warn.append(f"banlist has {n} entries > {BANLIST_MAX} "
                            f"(ban only true junk: watermarks/burned-in subs, never era mismatches)")
    return warn

rc = 0
for path in sys.argv[1:]:
    warn = check(path)
    name = os.path.basename(path)
    if warn:
        rc = 1
        print(f"  ⚠️  {name}")
        for w in warn:
            print(f"        {w}")
    else:
        print(f"  ✅  {name}")
sys.exit(rc)
