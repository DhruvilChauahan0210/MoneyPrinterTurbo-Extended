#!/usr/bin/env python
"""Post-build ship gate: does this render actually meet the quality bar?

Why this exists: `check_config.py` runs BEFORE the build and can only guess. Its pool
heuristic assumes "each source video yields roughly one usable distinct clip", and on
7 Sep 2026 that guess passed EP33 cleanly while the render came out with 7 distinct
media across 21 segments, one clip on screen 4x, and every single shot a close-up.
Two builds either side make it clear the guess cannot be rescued with a better constant:

    EP31  16 segments   8 distinct   most-reused 8x   from 8 source videos
    EP32  17 segments  17 distinct   most-reused 1x   from 3 source videos
    EP33  21 segments   7 distinct   most-reused 4x   from 4 source videos

EP32 got 17 distinct clips out of THREE source videos; EP33 got 7 out of four. Yield per
source is not predictable from the config, so predicting it is the wrong move. But the
build log states the achieved numbers exactly, so checking them afterwards is reliable.

This matters because of WHY the scripts got longer in the first place. The 7 Sep RCA
traced the channel's collapse (views 180K->80.6K, swipe-away 51.9%->67.2%) to a hook and
runtime problem, and lengthening scripts to reach the 18-38s band raises the caption
segment count, which raises how much distinct media a build needs. Fixing the hook while
letting the same four clips cycle four times would just trade one retention defect for
another. Run this before anything ships.

usage: check_render.py <video.mp4> <BUILDLOG.log> [batch_config.json]
"""
import json, os, re, subprocess, sys

# Runtime band. Rebased 9 Sep 2026 to match check_config.py WORDS_MIN/WORDS_MAX
# (42-81 words at the measured 2.261 words/sec = 19.6s-36.8s). Until now this file still
# carried the old 12.0/15.0 band from the 7 Sep standard while check_config.py had already
# moved, so the two gates contradicted each other: any short written to the new word band
# was hard-failed here for "exceeding the 15s cap", and the only renders that could pass
# were the 8-11s ones the 9 Sep channel audit identified as the worst-performing bucket
# on the channel (<=11s: 149 shorts, median 1046 views, vs 1467 for the 23-35s bucket).
DUR_MIN, DUR_MAX = 18.0, 38.0

# How much DISTINCT media a render needs. This used to be a flat 12, which is not
# reachable at all under the current shot grammar: with min_shot_seconds=3.2 a 30s short
# only holds about 10 shots, so a flat 12 fails every conforming build. Scale it to the
# shots the runtime can actually hold instead, and keep a floor so short renders are not
# let off. MEDIA_REUSE_MAX is a HARD fail, not a warning: the 9 Sep review called repeated
# clips the most annoying visible defect on the channel, and the soft segment_reuse_penalty
# demonstrably does not stop a clip landing 4x (EP33: 7 distinct across 21 segments).
DISTINCT_FLOOR = 6
DISTINCT_SHOT_FRACTION = 0.75
MEDIA_REUSE_MAX = 2
DEFAULT_MIN_SHOT = 3.2


def _ffprobe(path):
    for exe in (os.path.join(os.path.dirname(__file__), ".venv", "bin", "ffprobe"), "ffprobe"):
        try:
            out = subprocess.run(
                [exe, "-v", "error", "-show_entries", "format=duration",
                 "-of", "default=nw=1:nk=1", path],
                capture_output=True, text=True, timeout=60).stdout.strip()
            if out:
                return float(out)
        except Exception:
            continue
    return None


def check(video, log, config=None):
    fail, warn = [], []

    dur = _ffprobe(video)
    if dur is None:
        warn.append("could not probe duration")
    elif dur > DUR_MAX:
        fail.append(f"duration {dur:.2f}s exceeds the HARD {DUR_MAX:.0f}s cap")
    elif dur < DUR_MIN:
        fail.append(f"duration {dur:.2f}s is under the {DUR_MIN:.0f}s floor -- the "
                    f"channel's 90-day top performers were all 0:12-0:15")

    text = open(log, errors="replace").read() if os.path.exists(log) else ""

    # The assigner logs one summary line; it is the only trustworthy source for what
    # actually landed on screen, as opposed to what the pool theoretically held.
    # The "from N source videos" and "most-reused media Nx" clauses are OPTIONAL. The old
    # pattern required them, and real build logs do not emit them -- the actual line is
    # `assigned 13 distinct media across 13 segments (13 real video clips, 0 photos)`.
    # So this check silently degraded to "no assigner summary" on every build and the media
    # diversity bar has never once been enforced. Found 9 Sep 2026.
    m = None
    for m in re.finditer(
        r"assigned (\d+) distinct media across (\d+) segments"
        r"(?:.*?from (\d+) source videos)?"
        r"(?:.*?most-reused media (\d+)x)?(?=\s|$|\x1b|\))", text):
        pass
    if not m:
        warn.append("no assigner summary in the log -- cannot verify media diversity")
    else:
        distinct, segments = int(m.group(1)), int(m.group(2))
        sources = int(m.group(3)) if m.group(3) else None
        reused = int(m.group(4)) if m.group(4) else None

        # Shots, not caption segments, are the unit the pool has to cover: with
        # min_shot_seconds set the picture holds across several segments, so `segments`
        # badly overstates how many distinct clips the edit can possibly show.
        min_shot = DEFAULT_MIN_SHOT
        if config and os.path.exists(config):
            try:
                min_shot = float(json.load(open(config)).get("defaults", {}).get(
                    "min_shot_seconds") or DEFAULT_MIN_SHOT)
            except Exception:
                pass
        shots = max(1, int((dur or DUR_MIN) / max(min_shot, 0.1) + 0.999))
        need = max(DISTINCT_FLOOR, int(shots * DISTINCT_SHOT_FRACTION + 0.999))
        if distinct < need:
            fail.append(f"only {distinct} distinct media across {segments} segments "
                        f"(~{shots} shots at min_shot_seconds={min_shot}; bar is "
                        f">={need})" + (f" -- from {sources} source videos" if sources else ""))
        # Which knob actually governs this number matters, and it is easy to get wrong.
        # `assign_images_to_segments` (the function that emits the line we just parsed)
        # takes max_media_reuse from `segment_max_media_reuse` and a SOFT linear brake
        # from `segment_reuse_penalty` (task.py:745-750). `max_video_reuse` goes to a
        # different selection path in semantic_video.py and does not constrain this at
        # all -- an earlier version of this check compared against it and reported EP34
        # as a cap violation when no cap was in force.
        #
        # The series configs run `segment_max_media_reuse: 0`, i.e. deliberately no hard
        # cap, because the build standard records that any hard cap aborts the build in
        # one-shot mode. So with the cap off there is nothing to "violate": report the
        # observed reuse against the soft penalty instead, and let the distinct-media
        # check above be the thing that actually fails a render.
        cap = pen = None
        if config and os.path.exists(config):
            cdf = json.load(open(config)).get("defaults", {})
            cap = cdf.get("segment_max_media_reuse")
            pen = cdf.get("segment_reuse_penalty")
        if reused is not None:
            if cap and reused > int(cap):
                fail.append(f"most-reused media {reused}x exceeds the hard "
                            f"segment_max_media_reuse={cap}")
            elif reused > MEDIA_REUSE_MAX:
                # Deliberately a fail. segment_reuse_penalty is soft and cannot abort, so
                # leaving this as a warning is what let EP33 ship with one clip on screen
                # four times. Re-run with a wider pool (youtube_max_videos) rather than
                # nudging the penalty, which the 30 Aug notes show does not rescue a thin pool.
                fail.append(f"one clip used {reused}x, over the {MEDIA_REUSE_MAX}x limit "
                            f"(segment_reuse_penalty={pen} is soft and cannot abort) -- "
                            f"widen the footage pool and rebuild")

    # All-one-shot-size reads as a slideshow of the same face, which is the monotony the
    # RCA flagged. Variety is a soft call, so this warns rather than fails.
    shots = re.findall(r"shot sizes (\{[^}]*\})", text)
    if shots:
        s = shots[-1]
        kinds = re.findall(r"'(\w+)':\s*(\d+)", s)
        if len(kinds) == 1:
            warn.append(f"every shot is one size {s} -- no framing variety")

    if re.search(r"below the sharpness floor", text):
        n = re.search(r"(\d+) shot\(s\) below the sharpness floor", text)
        warn.append(f"{n.group(1) if n else 'some'} shot(s) shipped below the sharpness floor")
    return fail, warn


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    fail, warn = check(*sys.argv[1:4])
    name = os.path.basename(sys.argv[1])
    for f in fail:
        print(f"  ❌  {f}")
    for w in warn:
        print(f"  ⚠️   {w}")
    if not fail:
        print(f"  ✅  {name} meets the ship bar"
              + (" (with warnings)" if warn else ""))
    sys.exit(1 if fail else 0)
