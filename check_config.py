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

# Concept queries are how stock footage gets in. EP12 asked for "hospital heart monitor
# beeping close up" and "electrocardiogram machine hospital", and shipped with five
# interchangeable ICU monitors, two ECG printouts and an empty hospital room in nine
# seconds -- roughly half the runtime. The editor's rule is cut to the SUBJECT, not to
# the concept: when the line is "his heart wouldn't slow down" you hold on his face.
STOCK_WORDS = (
    "hospital", "electrocardiogram", "ecg", "heart monitor", "stethoscope", "surgery room",
    "operating theatre", "medical chart", "x-ray", "ambulance", "laboratory", "microscope",
    "stock footage", "abstract", "background loop", "generic",
)

BUDGET = {
    "subject_negative_labels": 45,   # July baseline 35
    "hook_negative_labels":    18,   # July baseline 11
}
FLOOR_MIN   = 0.30                   # July baseline 0.35; lowering this lets junk through
LEDGER_MAX  = 20                     # rolling window, not an all-time ban
BANLIST_MAX = 160

def _subject_terms(df):
    """Names the short is about, taken from the positive labels."""
    terms = set()
    for lab in (df.get("subject_positive_labels") or []):
        for w in lab.split():
            w = w.strip(".,'\"").lower()
            if len(w) > 3 and w[0].isupper() is False and w.isalpha():
                continue
        for w in lab.replace("'s", "").split():
            w = w.strip(".,'\"")
            if len(w) > 3 and w[0].isupper():
                terms.add(w.lower())
    return terms


def check(path):
    d = json.load(open(path)); df = d.get("defaults", {}); warn = []

    # --- footage queries must name the subject ---
    queries = df.get("youtube_footage_queries") or []
    subject = _subject_terms(df)
    if queries and subject:
        anon = [q for q in queries
                if not any(t in q.lower() for t in subject)]
        stock = [q for q in queries if any(k in q.lower() for k in STOCK_WORDS)]
        for q in stock:
            warn.append(f'stock query: "{q}" -- cut to the subject, not the concept')
        for q in anon:
            if q not in stock:
                warn.append(f'query names no subject: "{q}" (expected one of: '
                            f'{", ".join(sorted(subject))})')
        if queries and len(anon) / len(queries) > 0.25:
            warn.append(f"{len(anon)}/{len(queries)} queries do not name the subject "
                        f"-- the pool will fill with stock and the edit will show it")
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
