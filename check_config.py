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
import json, sys, os, re

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

# Runtime band in words. Set 7 Sep 2026 from the analytics RCA; see the note at the
# n_words check for the derivation and for why this is a band and not a point target.
# Rebased 8 Sep 2026 against @_simplesports (796K subs, 694 shorts). Its top-40 shorts
# have a 31s duration median, a range of 18-48s and NOTHING under 18s, because 2026
# Shorts ranking weights watch time over swipe rate. The old 40-48 word / 12-15s band
# was tuned to a swipe-rate model that no longer holds and capped our watch time at
# roughly a third of the benchmark's. MEASURED on the first EP39 render: 113 words gave
# 49.97s of narration at voice_rate 1.0, i.e. 2.26 words/sec -- NOT the 4.2 w/s first
# assumed from finished-short totals (those include tight trim and a hook card).
WORDS_MIN    = 42                    # ~19s -- below the benchmark's own 18s floor
WORDS_TARGET = 68                    # ~30s -- the benchmark's 31s median
WORDS_MAX    = 81                    # ~36s -- past this, completion rate starts to fall

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
    hold = float(df.get("min_shot_seconds") or 0.0)
    if words and per_cap > 0 and reuse > 0:
        segments = -(-words // per_cap)                 # ceil
        # With min_shot_seconds the picture no longer changes once per caption segment,
        # so the pool has to cover SHOTS, not segments. Runtime ~= words/2.261 + 1.0s.
        if hold > 0:
            shots = max(1, int((words / 2.261 + 1.0) / hold + 0.999))
        else:
            shots = segments
        need_distinct = -(-shots // reuse)              # ceil
        # The subject gate historically keeps ~60% of candidates ("kept 9/15" in the
        # 25 Aug log), and each source video yields roughly one usable distinct clip
        # after de-duplication.
        supply = int(maxvid * 0.6) + len(df.get("pinned_image_paths") or [])
        if supply < need_distinct:
            warn.append(f"pool too thin: {words} words -> {shots} shots "
                        f"need {need_distinct} distinct clips at reuse {reuse}, but "
                        f"youtube_max_videos={maxvid} supplies about {supply} after the "
                        f"gate -- raise youtube_max_videos to "
                        f"{max(16, min(30, -(-need_distinct * 5 // 2)))} or raise max_video_reuse")
        elif maxvid > max(16, min(30, -(-need_distinct * 5 // 2))) * 1.4:
            warn.append(f"pool oversized: needs about {need_distinct} distinct clips but "
                        f"youtube_max_videos={maxvid}. Downloads dominate build time -- "
                        f"{max(16, min(30, -(-need_distinct * 5 // 2)))} would do "
                        f"(sized at need x2.5, floor 16, ceiling 30)")

    # --- the hook must not answer itself ---
    # Shorts hold a viewer with an UNRESOLVED question. A channel-wide audit found 84 of
    # 142 narrated configs stating the payoff in hook_text and then restating it in the
    # first spoken line, which closes the loop about 1.5s in and leaves every later second
    # with less reason to watch. It is the single biggest retention defect that is visible
    # from the config alone, so it is checked here rather than left to review.
    hook = (df.get("hook_text") or "").strip()
    if hook and script:
        first = re.split(r"(?<=[.!?])\s+", script.strip())[0]
        hw = {w for w in re.findall(r"[a-z]{4,}", hook.lower())}
        fw = {w for w in re.findall(r"[a-z]{4,}", first.lower())}
        if hw:
            overlap = len(hw & fw) / len(hw)
            if overlap >= 0.5:
                warn.append(
                    f"hook answers itself ({overlap:.0%} of its words are in the first "
                    f"spoken line): hook={hook!r} line1={first!r} -- pose the tension in "
                    f"the hook and let the payoff land last")

    # --- the script must actually finish ---
    # batch_ronaldo_5ucl shipped a test build whose narration ended "Which makes you
    # wonder," -- a dangling clause with no payoff, which the pipeline happily voiced.
    # The channel's circular scripts END on a dangling clause ON PURPOSE: the last words
    # flow back into the hook when the Short auto-replays, which is what the looping
    # format relies on (documented across three separate memory entries, e.g. Mbappe
    # "...Which makes you wonder," looping into "This man might be faster than Usain
    # Bolt."). A truncated script is still a real bug, so the check stays -- it just has
    # to recognise the deliberate ending rather than flag the convention as a fault.
    LOOP_ENDINGS = ("which makes you wonder,", "and that makes you wonder,",
                    "which is why,", "and somehow,")
    if script:
        _tail = script.rstrip().lower()
        _is_loop = any(_tail.endswith(e) for e in LOOP_ENDINGS)
        if not _is_loop and not script.rstrip().endswith((".", "!", "?")):
            warn.append(f'script does not end in terminal punctuation: "...{script[-45:]}" '
                        f"-- it will be voiced as an unfinished sentence")
        # --- runtime band, checked from BOTH sides ---
        # This check used to warn only when a script ran LONG ("over ~40 risks breaching
        # the 15s cap, target ~30"). Nothing ever warned when one ran short, so the
        # channel drifted down unchallenged: measured 7 Sep 2026 across all 24 September
        # shorts, median runtime was 9.74s on 31-38 word scripts. Meanwhile the 90-day
        # top performers were 0:12-0:15 (the two 15K breakouts were 0:12 and 0:13). A
        # 9.7s short is not a shorter version of a 13s short -- it is one story beat
        # instead of three, and the swipe-away rate went 51.9% -> 67.2% over the same
        # window. Too short is now the defect that actually happens, so it is a warning.
        #
        # Word count alone does NOT determine runtime. Regressing the 16 built EP17-EP32
        # renders against their scripts (voice_rate 1.2) gives
        #     duration ~= 0.394*words + 0.524*commas - 0.040*sentences - 4.66
        # i.e. a comma costs about as much as 1.3 extra words, because each one is a
        # pause. But R^2 is only 0.414 and the max error is 2.26s (EP22 and EP26 both
        # ran ~2s longer than predicted, most likely timed-sync stretching segments to
        # the captions), so this is a sighting shot, not a guarantee. Hence a BAND, and
        # hence the target sits at ~13.4s rather than 14s: with +2s of observed noise
        # against a hard 15s ceiling, anything higher risks shipping an over-cap short.
        # ALWAYS verify the rendered duration -- run_series_ep.sh prints it.
        n_words = len(script.split())
        n_commas = script.count(",")
        est = 0.3941 * n_words + 0.5239 * n_commas - 0.0396 * max(
            1, len([x for x in re.split(r"(?<=[.!?])\s+", script.strip()) if x.strip()])
        ) - 4.6640
        # The old EP17-EP32 regression was fitted on 31-47 word scripts at voice_rate 1.2
        # and does not extrapolate to 115 words; use a flat rate for the new band.
        est = n_words / 2.261 + 1.0
        if n_words > WORDS_MAX:
            warn.append(f"script is {n_words} words (+{n_commas} commas); over "
                        f"{WORDS_MAX} it is predicted at ~{est:.1f}s, past the ~36s point "
                        f"where completion rate falls (target ~{WORDS_TARGET})")
        elif n_words < WORDS_MIN:
            warn.append(f"script is only {n_words} words (+{n_commas} commas); predicted "
                        f"~{est:.1f}s, under the 18s floor that @_simplesports' top 40 "
                        f"never goes below (target ~{WORDS_TARGET} words / ~29s)")

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
    # --- there must be something under the voice at t=0 ---
    # bgm_type was set "" channel-wide on 4 Aug 2026. video.py already carries a note that
    # this silenced the t=0 hook impact, and the fix at the time was to move the boom out
    # of the `if bgm_file:` block -- but that left a boom and 0.07 room tone as the entire
    # audio bed. Swipe-away went 51.9% (Jul) -> 62.8% (Aug) -> 67.2% (Sep) and the Shorts
    # feed is 94.7% of this channel's traffic, so second zero is the whole funnel.
    # Restored 7 Sep 2026 to bgm_volume 0.10, which sits well under the -14 LUFS voice.
    if (df.get("bgm_type") or "") == "" and not float(df.get("bgm_volume") or 0):
        warn.append("no music bed: bgm_type=\"\" and bgm_volume=0, so frame 1 is only a "
                    "boom + room tone -- set bgm_type \"random\" / bgm_volume 0.10 "
                    "(swipe-away rose 51.9%->67.2% while this was off)")

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
