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

    # --- pool feasibility: the arithmetic behind the commonest build failure ---
    # "all evidence clips reached the per-clip reuse cap before segment N" was five of
    # the seven recorded failures, each costing a 9-15 minute rebuild. It is pure
    # arithmetic and knowable here, in a second, before anything downloads.
    script = (df.get("video_script") or
              ((d.get("videos") or [{}])[0].get("video_script") if d.get("videos") else "") or "")
    words = len(script.split())
    per_cap = int(df.get("max_words_per_subtitle") or 2)
    reuse = int(df.get("max_video_reuse") or 2)
    maxvid = int(df.get("youtube_max_videos") or 3)
    if words and per_cap > 0 and reuse > 0:
        segments = -(-words // per_cap)                 # ceil
        need_distinct = -(-segments // reuse)           # ceil
        # The subject gate historically keeps ~60% of candidates ("kept 9/15" in the
        # 25 Aug log), and each source video yields roughly one usable distinct clip
        # after de-duplication.
        supply = int(maxvid * 0.6) + len(df.get("pinned_image_paths") or [])
        if supply < need_distinct:
            warn.append(f"pool too thin: {words} words / {per_cap} = {segments} segments "
                        f"need {need_distinct} distinct clips at reuse {reuse}, but "
                        f"youtube_max_videos={maxvid} supplies about {supply} after the "
                        f"gate -- raise youtube_max_videos to "
                        f"{max(16, min(30, -(-need_distinct * 5 // 2)))} or raise max_video_reuse")
        elif maxvid > max(16, min(30, -(-need_distinct * 5 // 2))) * 1.4:
            warn.append(f"pool oversized: needs about {need_distinct} distinct clips but "
                        f"youtube_max_videos={maxvid}. Downloads dominate build time -- "
                        f"{max(16, min(30, -(-need_distinct * 5 // 2)))} would do "
                        f"(sized at need x2.5, floor 16, ceiling 30)")

    # --- EVERY text field that drives media selection, not just the footage queries ---
    # Caught by a local review on 28 Aug: a config copied from another episode passed this
    # linter with zero warnings while still carrying the SOURCE episode's video_subject,
    # video_terms, visual_evidence_prompts and curated_image_paths. The footage queries had
    # been rewritten; these four had not, and they are consumed independently (task.py:374
    # and :574). A Champions League short would have pulled in hospital ECG imagery.
    # Copying a config is the normal workflow, so the linter has to check all of them.
    subject_check = _subject_terms(df)
    if subject_check:
        for field in ("video_subject", "video_terms", "hook_cover_term"):
            val = (df.get(field) or (d.get("videos") or [{}])[0].get(field) or "")
            if isinstance(val, str) and val.strip():
                hits = [k for k in STOCK_WORDS if k in val.lower()]
                if hits:
                    warn.append(f'{field} contains stock terms {hits}: "{val[:70]}..."')
        for field in ("visual_evidence_prompts", "youtube_footage_queries"):
            for item in (df.get(field) or []):
                hits = [k for k in STOCK_WORDS if k in str(item).lower()]
                if hits and field == "visual_evidence_prompts":
                    warn.append(f'{field} stock entry {hits}: "{str(item)[:60]}..."')

    # Curated images must belong to THIS short, not the config it was copied from.
    slug = os.path.basename(path)[len("batch_"):-len(".json")]
    for cimg in (df.get("curated_image_paths") or []):
        tag = os.path.basename(os.path.dirname(str(cimg)))
        if tag and tag not in slug and tag not in ("series_assets", "resource"):
            warn.append(f"curated_image_paths points at '{tag}' assets but this config is "
                        f"'{slug}' -- leftover from a copied config?")
            break

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
