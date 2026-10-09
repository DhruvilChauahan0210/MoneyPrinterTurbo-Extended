#!/usr/bin/env python3
"""
Source candidate media PER BEAT of a short, rank them, and contact-sheet them for picking.

Usage:
    .venv/bin/python beat_source.py batch_x.json [--video 0] [--beats 3,5] [--autopick]

Each entry of videos[i].beat_plan:
    {"says":   "Ronaldo named her Bella",                  # exact slice of video_script
     "visual": "a toddler girl with dark curly hair, Ronaldo's daughter",   # CLIP prompt
     "images": ["Bella Esmeralda Ronaldo daughter"],      # DuckDuckGo photo searches
     "clips":  ["Ronaldo Bella Esmeralda video"],         # YouTube searches
     "urls":   ["https://www.instagram.com/reel/..."]}    # direct video links (any yt-dlp site)

For every beat this downloads its own candidates into storage/beats/<slug>/bNN/, ranks
them against `visual` with CLIP (near-duplicate photos collapsed), writes
storage/beats/<slug>/sheet_bNN.jpg, and stores the ranked list as beat["candidates"].
Pick by setting beat["media"] to one of them (or --autopick takes the top one); once every
beat has media the normal batch_generator.py run renders the beat plan.
"""

import argparse
import glob
import hashlib
import json
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor

from loguru import logger

from app.services import auto_footage, image_ranker, material

ROOT = os.path.dirname(os.path.abspath(__file__))
W, H = 1080, 1920
SHEET_TOP = 8
VIDEO_EXTS = (".mp4", ".mov", ".webm", ".mkv", ".avi")


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")[:40] or "short"


def _record_sources(out_dir, mapping):
    """basename -> original URL, so a picked candidate can be written down as a link."""
    path = os.path.join(out_dir, "sources.json")
    cur = {}
    if os.path.exists(path):
        with open(path) as f:
            cur = json.load(f)
    cur.update(mapping)
    with open(path, "w") as f:
        json.dump(cur, f, indent=1)


def _photos(queries, out_dir, per_query=12):
    paths = []
    for q in queries:
        hits = material.search_images_duckduckgo(q, max_results=per_query)
        with ThreadPoolExecutor(max_workers=8) as pool:
            got = list(pool.map(lambda m: (m.url, material.save_image(m.url, out_dir, q)), hits))
        _record_sources(out_dir, {os.path.basename(p): u for u, p in got if p})
        paths += [p for _, p in got if p]
    from PIL import Image
    keep = []
    for p in dict.fromkeys(paths):
        try:
            with Image.open(p) as im:
                if min(im.size) >= 360:          # thumbnails upscale to mush on 1080x1920
                    keep.append(p)
        except Exception:
            pass
    return keep


def _search_clips(queries, max_videos=2):
    clips = []
    for q in queries:
        clips += auto_footage.fetch_clips(
            task_id="beats", queries=[q], video_width=W, video_height=H,
            max_videos=max_videos, clip_len=4.0, clips_per_video=8,
            max_clips=8 * max_videos, max_height=1080, retries=1)
    return clips


def _url_clips(urls, out_dir):
    use_node = bool(auto_footage._which("node") or auto_footage._which("deno"))
    clips = []
    for url in urls:
        src_dir = os.path.join(out_dir, "src_" + hashlib.md5(url.encode()).hexdigest()[:10])
        os.makedirs(src_dir, exist_ok=True)
        src = auto_footage._download_url(url, src_dir, 1080, 200, use_node, timeout=300, retries=1)
        if not src:
            logger.warning(f"beat_source: could not download {url} "
                           f"(Instagram/X usually need a cookies file, see _cookies_args)")
            continue
        _record_sources(out_dir, {os.path.basename(src_dir): url})
        base = os.path.splitext(os.path.basename(src))[0]
        clips += auto_footage._cut_vertical_clips(src, out_dir, base, 4.0, 6, W, H,
                                                  head_skip=0.3, tail_skip=0.3)
    return clips


def _rank(paths, visual):
    """CLIP-rank against the beat's visual; collapse the same photo re-hosted on many sites."""
    if not paths or not image_ranker._try_load_clip():
        return [(p, 0.0) for p in paths]
    import torch
    txt = image_ranker._embed_texts([visual])
    img = image_ranker._embed_images(paths)
    sims = torch.mm(txt, img.T)[0].tolist()
    order = sorted(range(len(paths)), key=lambda i: -sims[i])
    kept, out = [], []
    for i in order:
        if any(float(torch.dot(img[i], img[k])) > 0.95 for k in kept):
            continue
        score = sims[i] - (0.05 if image_ranker.is_graphic_image(paths[i]) else 0.0)
        kept.append(i)
        out.append((paths[i], round(score, 4)))
    return sorted(out, key=lambda t: -t[1])


def _sheet(beat_no, beat, ranked, out_path):
    from PIL import Image, ImageDraw, ImageFont
    tw, th, pad, head = 216, 384, 6, 70
    top = ranked
    rows = 2 if any(p.lower().endswith(VIDEO_EXTS) for p, _ in top) else 1
    cols = max(1, max(sum(1 for p, _ in top if p.lower().endswith(VIDEO_EXTS) == bool(r))
                      for r in range(rows)))
    sheet = Image.new("RGB", (pad + (tw + pad) * cols, head + (th + pad) * rows), "black")
    d = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 20)
    except Exception:
        font = ImageFont.load_default()
    d.text((pad, 6), f"B{beat_no:02d}  \"{beat['says'][:70]}\"", fill="white", font=font)
    d.text((pad, 36), f"want: {beat.get('visual', '')[:80]}", fill="#9cf", font=font)
    col = [0, 0]
    for k, (p, score) in enumerate(top):
        is_vid = p.lower().endswith(VIDEO_EXTS)
        r = 1 if (is_vid and rows == 2) else 0
        try:
            im = image_ranker._load_media_as_image(p)
        except Exception:
            continue
        im = im.copy()
        im.thumbnail((tw, th))
        x = pad + col[r] * (tw + pad)
        y = head + r * (th + pad)
        col[r] += 1
        sheet.paste(im, (x + (tw - im.width) // 2, y + (th - im.height) // 2))
        tag = f"{k}{' V' if is_vid else ''} {score:.2f}"
        d.rectangle([x, y, x + 92, y + 26], fill="black")
        d.text((x + 4, y + 2), tag, fill="#0f0" if is_vid else "yellow", font=font)
    sheet.save(out_path, quality=88)


def _offsets(dur, clip_len, n, head, tail):
    """Same arithmetic as auto_footage._cut_vertical_clips, so clip _cN maps to a second."""
    start, end = head, max(head + clip_len, dur - tail)
    span = end - start
    if span <= clip_len:
        return [start]
    step, out, t = max(clip_len, span / n), [], start
    while t + clip_len <= end and len(out) < n:
        out.append(t)
        t += step
    return out


def _clip_origin(path):
    """(url, start_seconds) of a cut candidate clip, or (None, None) if untraceable."""
    m = re.match(r"(.+)_c(\d+)\.mp4$", os.path.basename(path))
    if not m:
        return None, None
    vid, i = m.group(1), int(m.group(2))
    clip_dir = os.path.dirname(path)
    srcs = glob.glob(os.path.join(os.path.dirname(clip_dir), "src", vid + ".*"))
    if srcs:      # fetch_clips search cache: <key>/src/<id>.ext, cut 8 per video, 6s/4s skips
        url, (n, head, tail) = f"https://www.youtube.com/watch?v={vid}", (8, 6.0, 4.0)
    else:         # direct `urls`: <beat>/src_<hash>/<id>.ext, cut 6 per video, 0.3s skips
        srcs = glob.glob(os.path.join(clip_dir, "src_*", vid + ".*"))
        if not srcs:
            return None, None
        mapping = {}
        if os.path.exists(os.path.join(clip_dir, "sources.json")):
            with open(os.path.join(clip_dir, "sources.json")) as f:
                mapping = json.load(f)
        url = mapping.get(os.path.basename(os.path.dirname(srcs[0])))
        n, head, tail = 6, 0.3, 0.3
    offs = _offsets(auto_footage._ffprobe_duration(srcs[0]), 4.0, n, head, tail)
    return (url, round(offs[i], 2)) if url and i < len(offs) else (None, None)


def _photo_origin(path):
    src = os.path.join(os.path.dirname(path), "sources.json")
    if os.path.exists(src):
        with open(src) as f:
            return json.load(f).get(os.path.basename(path))
    return None


def _ytdlp(*args):
    cmd = [auto_footage._ytdlp_bin(), "--no-playlist", "--no-warnings", "--socket-timeout", "20",
           *auto_footage._cookies_args(), *args]
    if auto_footage._which("deno") or auto_footage._which("node"):
        cmd[1:1] = ["--extractor-args", "youtube:player_client=default,web_safari;jsi=Deno"]
    return auto_footage._run(cmd, timeout=300)


def _find(query, depth=10):
    """Search results as text only (no download): pick a link, then --scan it."""
    use_node = bool(auto_footage._which("deno") or auto_footage._which("node"))
    print(f"\n### {query}\n| link | length | channel | title |\n|---|---|---|---|")
    for r in auto_footage._search_metadata(query, depth, use_node):
        print(f"| https://www.youtube.com/watch?v={r['id']} | {r['duration_seconds']}s | "
              f"{r['channel'][:24]} | {r['title'][:70]} |")


def _section(url, start, length, out, fill="cover"):
    """Download ONLY [start, start+length] of a video at 1080p and reframe it to 9:16.

    Whole-video downloads were the bottleneck: search hits run up to 20 minutes, and on
    8 Oct a single query hit yt-dlp's 240s timeout. A shot list already knows the second
    it wants, so fetch just that window (seconds, not minutes)."""
    # Short sources (Shorts, reposted stories): download once whole and cut every shot
    # locally. Measured 8 Oct: a 2s --download-sections fetch took ~5 min per shot (yt-dlp
    # pipes the DASH stream through ffmpeg), while a whole <3 min video takes seconds.
    scan = glob.glob(os.path.join(ROOT, "storage", "cache_videos", "scan",
                                  hashlib.md5(url.encode()).hexdigest()[:12], "low.*"))
    if scan and auto_footage._ffprobe_duration(scan[0]) <= 180:
        full_dir = os.path.join(ROOT, "storage", "cache_videos", "comparison",
                                hashlib.md5(url.encode()).hexdigest()[:12])
        os.makedirs(full_dir, exist_ok=True)
        if not glob.glob(os.path.join(full_dir, "full.*")):
            _ytdlp("-f", "bv*[height<=1080][ext=mp4]/bv*[height<=1080]/best",
                   "-o", os.path.join(full_dir, "full.%(ext)s"), url)
        if glob.glob(os.path.join(full_dir, "full.*")):
            return auto_footage.fetch_exact_clip(url, start, start + length, W, H, out,
                                                 max_height=1080, fill=fill, retries=1)
    key = f"{url}#t={start:.2f}+{length:.2f}"
    src_dir = os.path.join(ROOT, "storage", "cache_videos", "comparison",
                           hashlib.md5(key.encode()).hexdigest()[:12])
    os.makedirs(src_dir, exist_ok=True)
    if not glob.glob(os.path.join(src_dir, "sec.*")):
        r = _ytdlp("-f", "bestvideo[height<=1080][ext=mp4]/best[height<=1080][ext=mp4]/best",
                   "--download-sections", f"*{start:.2f}-{start + length + 0.3:.2f}",
                   "--force-keyframes-at-cuts", "-o", os.path.join(src_dir, "sec.%(ext)s"), url)
        if not glob.glob(os.path.join(src_dir, "sec.*")):
            logger.warning(f"section download failed for {url} @{start}: {r.stderr.strip()[-200:]}")
            return ""
    # fetch_exact_clip reuses whatever video sits in its cache dir for this key, so it
    # performs the subject-aware 9:16 reframe on the section we just fetched.
    return auto_footage.fetch_exact_clip(key, 0.0, length, W, H, out, max_height=1080,
                                         fill=fill, retries=1)


def _fetch_shot(n, beat, root):
    """Download + cut ONE beat's shot from its url/start. Returns the media path or ''."""
    url = beat.get("url")
    if not url:
        return beat.get("media", "")
    out_dir = os.path.join(root, f"b{n:02d}")
    os.makedirs(out_dir, exist_ok=True)
    if beat.get("start") is None:                    # a photo link
        return material.save_image(url, out_dir, beat["says"])
    start, length = float(beat["start"]), float(beat.get("len", 4.0))
    out = os.path.join(out_dir, f"shot_{hashlib.md5(f'{url}@{start}'.encode()).hexdigest()[:10]}.mp4")
    if os.path.exists(out):
        return out
    return _section(url, start, length, out, fill=beat.get("fill", "cover"))


def _timeline_path(script):
    return os.path.join(ROOT, "storage", "beats",
                        "timeline_" + hashlib.md5(script.encode()).hexdigest()[:10] + ".json")


def _shotlist(plan, script):
    times = []
    if os.path.exists(_timeline_path(script)):
        with open(_timeline_path(script)) as f:
            times = json.load(f)
    print("| # | Time | Words | Type | Source | Cut |\n|---|---|---|---|---|---|")
    for n, b in enumerate(plan, 1):
        t = (f"{times[n - 1][0]:.1f}-{times[n - 1][0] + times[n - 1][1]:.1f}s"
             if len(times) >= n else "-")
        kind = "clip" if b.get("start") is not None else "photo"
        src = b.get("url") or (f"local: {os.path.basename(b['media'])}" if b.get("media") else "(none)")
        cut = (f"{float(b['start']):.1f}s -> {float(b['start']) + float(b.get('len', 4.0)):.1f}s"
               if b.get("start") is not None else "-")
        print(f"| {n} | {t} | {b['says']} | {kind} | {src} | {cut} |")


def _scan(url, root, t0, t1, every):
    """Timestamped frame strip of one video, to choose the exact second by eye."""
    from PIL import Image, ImageDraw, ImageFont
    src_dir = os.path.join(ROOT, "storage", "cache_videos", "scan",
                           hashlib.md5(url.encode()).hexdigest()[:12])
    os.makedirs(src_dir, exist_ok=True)
    srcs = glob.glob(os.path.join(src_dir, "low.*"))
    if not srcs:                     # 480p video-only is plenty to choose a second by eye, and fast
        _ytdlp("-f", "bv*[height<=480][ext=mp4]/bv*[height<=480]/best[height<=480]/worst",
               "-o", os.path.join(src_dir, "low.%(ext)s"), url)
        srcs = glob.glob(os.path.join(src_dir, "low.*"))
    if not srcs:
        sys.exit(f"could not download {url}")
    src = srcs[0]
    dur = auto_footage._ffprobe_duration(src)
    t1 = min(t1 or dur, dur)
    font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 22)
    tiles, t = [], t0
    while t < t1 and len(tiles) < 60:
        jpg = os.path.join(src_dir, f"scan_{t:.1f}.jpg")
        auto_footage._run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{t:.2f}", "-i", src,
                           "-frames:v", "1", "-vf", "scale=240:-2", jpg], timeout=60)
        if os.path.exists(jpg):
            im = Image.open(jpg).convert("RGB")
            ImageDraw.Draw(im).text((4, 4), f"{t:.1f}s", fill="yellow", font=font)
            tiles.append(im)
        t += every
    if not tiles:
        sys.exit("no frames extracted")
    cols, tw, th = 6, tiles[0].width, tiles[0].height
    sheet = Image.new("RGB", (cols * tw, -(-len(tiles) // cols) * th))
    for k, im in enumerate(tiles):
        sheet.paste(im, ((k % cols) * tw, (k // cols) * th))
    out = os.path.join(root, f"scan_{hashlib.md5(url.encode()).hexdigest()[:8]}.jpg")
    os.makedirs(root, exist_ok=True)
    sheet.save(out, quality=85)
    print(f"SCAN={out}  (duration {dur:.1f}s)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("batch")
    ap.add_argument("--video", type=int, default=0)
    ap.add_argument("--beats", default="", help="comma list of 1-based beats to (re)source")
    ap.add_argument("--autopick", action="store_true", help="set media = top candidate")
    ap.add_argument("--pick", default="", help='"3=10,5=0": beat=candidate index from its sheet; '
                    "records the exact link + second")
    ap.add_argument("--fetch", action="store_true", help="download+cut every linked shot, one by one")
    ap.add_argument("--replace", type=int, default=0, help="beat to swap; with --url/--start")
    ap.add_argument("--url", default="")
    ap.add_argument("--start", type=float, default=None)
    ap.add_argument("--len", type=float, default=None)
    ap.add_argument("--shotlist", action="store_true", help="print the shot list table")
    ap.add_argument("--find", default="", help='"query1|query2": list results as text, no download')
    ap.add_argument("--scan", default="", help="URL: timestamped frame strip for choosing seconds")
    ap.add_argument("--scan-from", type=float, default=0.0)
    ap.add_argument("--scan-to", type=float, default=0.0)
    ap.add_argument("--scan-every", type=float, default=1.0)
    a = ap.parse_args()
    # Shots here are chosen by eye, so the cutter must not veto a picked moment for
    # carrying a source caption (burned-in text is acceptable, CD 9 Sep).
    auto_footage._REJECT_BURNED_IN_TEXT = False

    with open(a.batch, encoding="utf-8") as f:
        data = json.load(f)
    entry = data["videos"][a.video]
    plan = entry.get("beat_plan") or data.get("defaults", {}).get("beat_plan")
    if not plan:
        sys.exit("no beat_plan in this video entry")

    script = entry.get("video_script", "")
    joined = " ".join(b["says"] for b in plan)
    norm = lambda t: re.sub(r"[^a-z0-9]+", " ", t.lower()).split()
    if norm(joined) != norm(script):
        logger.warning("beat `says` slices do not concatenate to video_script exactly; "
                       "beat boundaries may drift. Fix the plan if timing looks off.")

    slug = _slug(entry.get("video_subject", "short"))
    root = os.path.join(ROOT, "storage", "beats", slug)

    def _save():
        with open(a.batch, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    if a.find:
        for q in a.find.split("|"):
            _find(q.strip())
        return
    if a.scan:
        return _scan(a.scan, root, a.scan_from, a.scan_to, a.scan_every)
    if a.shotlist:
        return _shotlist(plan, script)
    if a.pick:
        for item in a.pick.split(","):
            n, k = (int(x) for x in item.split("="))
            beat = plan[n - 1]
            media = beat["candidates"][k]
            beat["media"] = media
            if media.lower().endswith(VIDEO_EXTS):
                url, start = _clip_origin(media)
                beat.update(url=url, start=start, len=4.0) if url else beat.pop("url", None)
            else:
                beat["url"] = _photo_origin(media)
                beat.pop("start", None)
            logger.info(f"beat {n} <- candidate {k}: {beat.get('url')} @ {beat.get('start')}")
        _save()
        return _shotlist(plan, script)
    if a.replace:
        beat = plan[a.replace - 1]
        if a.url:
            beat["url"] = a.url
            beat["start"] = a.start          # None = the link is a photo
        elif a.start is not None:
            beat["start"] = a.start          # same video, different second
        if a.len is not None:
            beat["len"] = a.len
        media = _fetch_shot(a.replace, beat, root)
        if not media:
            sys.exit(f"beat {a.replace}: download/cut failed, beat left unchanged")
        beat["media"] = media
        _save()
        logger.success(f"beat {a.replace} replaced -> {media}")
        return _shotlist(plan, script)
    if a.fetch:
        for n, beat in enumerate(plan, 1):
            if beat.get("start") is None:
                print(f"[{n}/{len(plan)}] {'photo' if beat.get('url') else 'kept'}: {beat['says']}")
                if beat.get("url") and not (beat.get("media") and os.path.exists(beat["media"])):
                    beat["media"] = _fetch_shot(n, beat, root) or beat.get("media", "")
                continue
            media = _fetch_shot(n, beat, root)
            print(f"[{n}/{len(plan)}] {'OK  ' if media else 'FAIL'} {beat['says']}  "
                  f"<- {beat['url']} @{beat['start']}s")
            if media:
                beat["media"] = media
            _save()                          # after every shot: a crash loses nothing
        return
    only = {int(x) for x in a.beats.split(",") if x.strip()}
    # One family-footage pool for the whole short (e.g. re-uploaded Instagram stories),
    # offered to every beat on top of that beat's own searches.
    shared = _search_clips(entry.get("beat_shared_clips", []), max_videos=3)
    logger.info(f"beat_source: {len(shared)} shared clips offered to every beat")
    for n, beat in enumerate(plan, 1):
        if only and n not in only:
            continue
        out_dir = os.path.join(root, f"b{n:02d}")
        os.makedirs(out_dir, exist_ok=True)
        logger.info(f"\n== beat {n}/{len(plan)}: {beat['says']}")
        cands = (_photos(beat.get("images", []), out_dir)
                 + _search_clips(beat.get("clips", []))
                 + _url_clips(beat.get("urls", []), out_dir)
                 + [p for p in beat.get("extra", []) if os.path.exists(p)])
        ranked = _rank(cands + shared, beat.get("visual") or beat["says"])
        # Photos out-score motion-blurred clip frames on CLIP every time, so one merged
        # top-N hides every clip. Keep the best of each kind; index k is stable.
        vids = [t for t in ranked if t[0].lower().endswith(VIDEO_EXTS)][:SHEET_TOP]
        stills = [t for t in ranked if not t[0].lower().endswith(VIDEO_EXTS)][:SHEET_TOP]
        ranked = stills + vids
        beat["candidates"] = [p for p, _ in ranked]
        if a.autopick and ranked:
            beat["media"] = ranked[0][0]
        sheet = os.path.join(root, f"sheet_b{n:02d}.jpg")
        _sheet(n, beat, ranked, sheet)
        logger.success(f"beat {n}: {len(cands)} candidates -> {sheet}")

    with open(a.batch, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"SHEETS_DIR={root}")


if __name__ == "__main__":
    main()
