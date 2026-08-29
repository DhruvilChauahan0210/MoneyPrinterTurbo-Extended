#!/usr/bin/env python
"""Warm the footage cache for upcoming shorts, outside the build.

Measured on 29 Aug: a COLD build spends ~9 of its ~11 minutes downloading source video,
while a build whose cache is already warm finishes in about 3. The download is not slow
because the pipeline is inefficient -- it is slow because yt-dlp waits on the network,
and doing that inside the build is what makes the build long.

So do it beforehand. Run this against tomorrow's configs while today's shorts are
uploading and every build starts warm. Nothing here renders, scores or decides anything;
it only populates storage/cache_videos, so it is safe to run repeatedly and safe to
interrupt -- fetch_clips is best-effort by design and already reuses whatever it finds.

    ./.venv/bin/python tools_prefetch.py batch_ronaldo_ep13_surgery.json [...]
    ./.venv/bin/python tools_prefetch.py --all-upcoming
"""
import json, os, sys, time, glob

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def prefetch(path: str) -> tuple:
    from app.services import auto_footage
    d = json.load(open(path))
    df = d.get("defaults", {})
    vids = d.get("videos") or [{}]
    m = {**df, **vids[0]}
    queries = m.get("youtube_footage_queries") or []
    if not queries:
        return (0, 0.0, "no footage queries")
    t0 = time.time()
    clips = auto_footage.fetch_clips(
        task_id=f"prefetch_{os.path.basename(path)[:-5]}",
        queries=queries,
        video_width=1080, video_height=1920,
        max_videos=int(m.get("youtube_max_videos", 16) or 16),
        clip_len=float(m.get("footage_clip_len", 3.0) or 3.0),
        clips_per_video=int(m.get("youtube_clips_per_video", 8) or 8),
        max_clips=int(m.get("youtube_max_clips", 80) or 80),
        max_height=int(m.get("youtube_max_height", 1080) or 1080),
    )
    return (len(clips), time.time() - t0, "")


def main(argv):
    if not argv:
        print(__doc__); return 2
    if argv[0] == "--all-upcoming":
        argv = sorted(glob.glob("batch_ronaldo_ep*.json"))[-4:]
        print(f"prefetching the {len(argv)} most recent episode configs\n")
    total_t = 0.0
    for p in argv:
        if not os.path.exists(p):
            print(f"  {p}: not found"); continue
        n, secs, err = prefetch(p)
        total_t += secs
        name = os.path.basename(p)[:-5]
        if err:
            print(f"  {name:<34} skipped ({err})")
        else:
            print(f"  {name:<34} {n:3d} clips cached in {secs/60:5.1f} min")
    print(f"\n  total {total_t/60:.1f} min spent OUTSIDE the build window")
    print("  builds using these configs should now finish near the warm-cache time (~3 min)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
