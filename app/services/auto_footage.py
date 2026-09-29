"""
Automatic REAL-footage sourcing via yt-dlp + ffmpeg.

Given a topic and a list of YouTube search queries, this:
  1. searches YouTube and downloads a few highlight videos (video-only, 720p,
     H.264, capped size — we use the pipeline's own TTS so no audio is needed),
  2. cuts each into short action clips, reframed to vertical 9:16,
  3. returns local clip paths.

These clips are injected into the existing image_search pool, so they flow
through the same CLIP photo/relevance/subject gates and timed-sync — only real,
on-subject MOTION footage survives. This is what replaces Ken-Burns stills with
actual highlight motion (the real retention unlock for Shorts).

Requires `yt-dlp` and `ffmpeg` on PATH (both ship with this repo's env). A JS
runtime (node) is auto-used when present to unlock HD formats.
"""
import os
import json
import shutil
import hashlib
import subprocess
from typing import List

from loguru import logger

VIDEO_EXTS = (".mp4", ".mov", ".webm", ".mkv", ".avi")


def _which(name: str) -> str:
    return shutil.which(name) or ""


def _ytdlp_bin() -> str:
    # Prefer the venv's yt-dlp, fall back to PATH.
    here = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    cand = os.path.join(here, ".venv", "bin", "yt-dlp")
    if os.path.exists(cand):
        return cand
    return _which("yt-dlp")


def _cookies_args() -> List[str]:
    """YouTube's bot-wall now requires authenticated cookies for downloads.
    Use the exported cookies.txt (see project notes) if present. Env override:
    YT_DLP_COOKIES=<path>."""
    cand = os.environ.get("YT_DLP_COOKIES") or os.path.expanduser("~/Desktop/.yt_cookies.txt")
    return ["--cookies", cand] if cand and os.path.exists(cand) else []


def _run(cmd: List[str], timeout: int = 240) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


def _ffprobe_duration(path: str) -> float:
    try:
        out = _run([
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", path,
        ], timeout=30).stdout.strip()
        return float(out)
    except Exception:
        return 0.0


# Concurrent query downloads. Capped at 5: yt-dlp's bot-wall workaround is fragile
# and more parallelism risks rate-limiting for no real gain.
DOWNLOAD_WORKERS = 4


def _download_one(query: str, dest_dir: str, max_height: int, max_filesize_mb: int,
                  use_node: bool, timeout: int, retries: int = 3) -> List[str]:
    """Search YouTube for `query` and download the top match (video-only, mp4/h264)."""
    ytdlp = _ytdlp_bin()
    if not ytdlp:
        logger.error("auto_footage: yt-dlp not found")
        return []
    before = set(os.listdir(dest_dir)) if os.path.isdir(dest_dir) else set()
    # Prefer H.264 (avc1) video-only at <=max_height; fall back to muxed mp4.
    fmt = (
        f"bestvideo[height<={max_height}][vcodec^=avc1][ext=mp4]/"
        f"bestvideo[height<={max_height}][ext=mp4]/"
        f"best[height<={max_height}][ext=mp4]/best[ext=mp4]/best"
    )
    # Pull the top 2 matches per query (not 1). Strict one-shot callers set
    # retries=0; legacy callers retain the old network retry behaviour.
    # after a few rapid searches, so a single result per query leaves most queries
    # empty and the footage pool tiny (→ the same clips repeat). 2 distinct source
    # matches per working query is the cheapest way to raise visual variety.
    cmd = [
        ytdlp, "--no-playlist", "--socket-timeout", "20",
        "--no-warnings", "--ignore-errors",
        "--retries", str(retries), "--extractor-retries", str(retries),
        "--match-filter", "duration < 1200 & duration > 12" + _claim_filter() + _title_filter(),
        "-f", fmt,
        "--max-filesize", f"{max_filesize_mb}M",
        "-o", os.path.join(dest_dir, "%(id)s.%(ext)s"),
        *_cookies_args(),
        f"ytsearch{max(2, min(int(os.environ.get('MPT_SEARCH_DEPTH', '5')), 10))}:{query}",
    ]
    if use_node:
        cmd[1:1] = ["--extractor-args", "youtube:player_client=default,web_safari;jsi=Deno"]
    try:
        r = _run(cmd, timeout=timeout)
        if r.returncode != 0:
            logger.warning(f"auto_footage: yt-dlp non-zero for '{query[:40]}': {r.stderr.strip()[-180:]}")
    except subprocess.TimeoutExpired:
        logger.warning(f"auto_footage: yt-dlp timed out for '{query[:40]}'")
    after = set(os.listdir(dest_dir)) if os.path.isdir(dest_dir) else set()
    new = [os.path.join(dest_dir, f) for f in (after - before) if f.lower().endswith(VIDEO_EXTS)]
    return new


# --- Claim safety -------------------------------------------------------------
# Measured 8 Sep 2026: EP39 pulled 12 sources, ALL Standard YouTube License (no
# Creative Commons), of which 4 were FIFA, 1 LALIGA and 1 DAZN. Those rightsholders
# run Content ID aggressively and issue worldwide blocks, which for a channel chasing
# the YPP Shorts-view threshold is the worst possible outcome: a blocked Short earns
# nothing AND its views stop counting. Skipping them at SEARCH time costs a little
# pool breadth and removes the largest single monetization risk in the pipeline.
# Fan re-upload channels are left in: the underlying rights are the same, but they do
# not themselves file claims, so the exposure is one step further away.
# --- Source TYPE filter ------------------------------------------------------
# Measured 8 Sep 2026 on the Salah build: 12 queries collapsed to 8 source videos,
# and every one was a fan edit, a commentary channel or a documentary -- a TIME
# interview piece and The Redmen TV, which is exactly where the Wikipedia-page
# screenshots, the burned-in subtitles and the "LFC TV" watermark in the render came
# from. CLIP scores content, so an article screenshot inside a documentary still reads
# as "about Mohamed Salah" and passes the subject gate. The only reliable place to
# reject this material is at search time, by what the upload IS.
NON_FOOTAGE_TITLE_TERMS = [
    "clips for edits", "free clips", "clip pack", "edit pack", "4k upscaled",
    "reaction", "reacts", "review", "podcast", "explained", "analysis",
    "documentary", "interview", "talks", "press conference", "kit",
    "top 10", "top 5", "tier list", "fifa", "efootball", "career mode",
]


# Channels that only ever publish talk, not football.
NON_FOOTAGE_CHANNELS = [
    "Redmen TV", "TIME", "Sky Sports News", "talkSPORT", "ESPN FC",
    "The Athletic", "Tifo", "COPA90", "Football Daily",
]


def _title_filter() -> str:
    """yt-dlp match-filter clauses skipping uploads that are not match footage.

    yt-dlp's `title!*=` is CASE-SENSITIVE -- verified 8 Sep 2026: "Clips For Edits"
    rejected the offending upload while "clips for edits" let it straight through,
    which is why the first version of this filter changed nothing at all. Emit a
    clause per casing variant rather than pretending one form is enough.
    """
    out = []
    for t in NON_FOOTAGE_TITLE_TERMS:
        for v in {t.lower(), t.upper(), t.title(), t.capitalize()}:
            out.append(f" & title!*={v}")
    for c in NON_FOOTAGE_CHANNELS:
        out.append(f" & channel!*={c}")
    return "".join(out)


CLAIM_HEAVY_CHANNELS = [
    "FIFA", "UEFA", "LALIGA", "La Liga", "DAZN", "Premier League", "beIN",
    "ESPN", "Sky Sports", "CBS Sports", "TNT Sports", "Eurosport", "Bundesliga",
    "Serie A", "Ligue 1", "Amazon Prime Video Sport", "Optus Sport",
]


def _claim_filter() -> str:
    """yt-dlp match-filter clauses that skip the aggressive rightsholders."""
    return "".join(f" & channel!*={c}" for c in CLAIM_HEAVY_CHANNELS)


def _clip_is_dark(path: str, thresh: float = 22.0, black_floor: float = 9.0) -> bool:
    """True if the clip is mostly dark OR contains a near-black frame (a fade /
    cut-to-black transition). Highlight reels are full of fades between plays;
    even a brief black flash looks broken under captions and spikes swipe-away,
    so we sample densely and drop the clip if ANY frame goes near-black."""
    import io
    try:
        from PIL import Image
        import numpy as np
        dur = _ffprobe_duration(path) or 1.0
        vals = []
        for frac in (0.08, 0.22, 0.36, 0.5, 0.64, 0.78, 0.92):
            r = subprocess.run([
                "ffmpeg", "-v", "error", "-ss", f"{dur*frac:.2f}", "-i", path,
                "-frames:v", "1", "-f", "image2pipe", "-vcodec", "png", "-",
            ], capture_output=True, timeout=30)   # binary stdout (no text=True)
            if r.returncode == 0 and r.stdout:
                arr = np.asarray(Image.open(io.BytesIO(r.stdout)).convert("L"))
                vals.append(float(arr.mean()))
        if not vals:
            return False
        # Drop if: a near-black frame appears anywhere (fade), the whole clip is
        # dark, or the average is low.
        return (min(vals) < black_floor) or (max(vals) < thresh) or \
               ((sum(vals) / len(vals)) < thresh * 0.8)
    except Exception:
        return False


def _cut_vertical_clips(src: str, out_dir: str, base: str, clip_len: float,
                        n_clips: int, video_width: int, video_height: int,
                        head_skip: float = 6.0, tail_skip: float = 4.0) -> List[str]:
    """Cut `n_clips` evenly-spaced clips of `clip_len`s from src, reframed to 9:16."""
    dur = _ffprobe_duration(src)
    if dur <= 0:
        return []
    usable_start = head_skip
    usable_end = max(usable_start + clip_len, dur - tail_skip)
    span = usable_end - usable_start
    if span <= clip_len:
        offsets = [usable_start]
    else:
        # Evenly spaced, non-overlapping where possible.
        step = max(clip_len, span / n_clips)
        offsets = []
        t = usable_start
        while t + clip_len <= usable_end and len(offsets) < n_clips:
            offsets.append(t)
            t += step
    W, H = video_width, video_height

    # Subject-aware reframe on the MAINLINE path. craft.subject_window was only ever
    # wired into fetch_exact_clip (comparison mode), so every series short was still
    # cropped dead centre -- 68% of a 1920px broadcast frame discarded blind, which is
    # the defect 74da959 set out to fix. Same for burned-in text: rejecting it here, while
    # the pool can still supply a replacement, is far cheaper than meeting it at the gate.
    def _centre_vf() -> str:
        return (
            f"crop='min(iw,ih*{W}/{H})':'min(ih,iw*{H}/{W})',"
            f"scale={W}:{H}:force_original_aspect_ratio=increase,"
            f"crop={W}:{H},setsar=1"
        )

    def _vf_from(crop_expr: str) -> str:
        return (
            f"{crop_expr},"
            f"scale={W}:{H}:force_original_aspect_ratio=increase,"
            f"crop={W}:{H},setsar=1"
        )

    vf = _centre_vf()
    reject_text = bool(globals().get("_REJECT_BURNED_IN_TEXT", True))

    def _analyse(off: float):
        """Return (vf, has_text). Any failure degrades to the old centre crop."""
        probe = os.path.join(out_dir, f"{base}_p{int(off * 100)}.jpg")
        try:
            from app.services import craft
            pr = _run(["ffmpeg", "-y", "-loglevel", "error",
                       "-ss", f"{off + clip_len / 2:.2f}", "-i", src,
                       "-frames:v", "1", "-q:v", "3", probe], timeout=60)
            if pr.returncode != 0 or not os.path.exists(probe):
                return _centre_vf(), False
            has_text = bool(reject_text and craft.all_text_furniture(probe))
            win = craft.subject_window(probe, W, H)
            if win and win.get("w"):
                logger.info(f"auto_footage: reframe {win['method']} x={win['x']} "
                            f"(drift {win.get('drift', 0):+.1%})")
                return _vf_from(f"crop={win['w']}:{win['h']}:{win['x']}:{win['y']}"), has_text
            return _centre_vf(), has_text
        except Exception as e:
            logger.debug(f"auto_footage: reframe unavailable, centring ({e})")
            return _centre_vf(), False
        finally:
            try:
                os.remove(probe)
            except OSError:
                pass

    made = []
    # Clips carrying burned-in text are held back rather than binned outright: if a source
    # yields nothing else, one chyron shot still beats starving the pool (the editorial
    # gate can drop it later). Starvation is what cost 11 minutes earlier tonight.
    spares = []
    for i, off in enumerate(offsets):
        out = os.path.join(out_dir, f"{base}_c{i}.mp4")
        clip_vf, has_text = _analyse(off)
        cmd = [
            "ffmpeg", "-y", "-loglevel", "error",
            "-ss", f"{off:.2f}", "-i", src, "-t", f"{clip_len:.2f}",
            "-an", "-vf", clip_vf,
            "-c:v", "libx264", "-preset", "fast", "-crf", "16",
            "-pix_fmt", "yuv420p", out,
        ]
        try:
            r = _run(cmd, timeout=120)
            if r.returncode == 0 and os.path.exists(out) and os.path.getsize(out) > 10000:
                # Drop clips that landed on a fade/black transition — they look
                # broken under captions and spike swipe-away.
                if _clip_is_dark(out):
                    logger.debug(f"auto_footage: dropping dark/fade clip @{off:.1f}s")
                    try: os.remove(out)
                    except OSError: pass
                elif has_text:
                    logger.info(f"auto_footage: burned-in text @{off:.1f}s "
                                f"- held back as a spare")
                    spares.append(out)
                else:
                    made.append(out)
            else:
                logger.debug(f"auto_footage: ffmpeg cut failed @{off:.1f}s: {r.stderr.strip()[-120:]}")
        except subprocess.TimeoutExpired:
            logger.warning(f"auto_footage: ffmpeg cut timed out @{off:.1f}s")
    if not made and spares:
        logger.warning(f"auto_footage: {base} yielded only text-carrying clips "
                       f"- keeping {len(spares)} rather than starving the pool")
        made = spares
        spares = []
    for extra in spares:
        try:
            os.remove(extra)
        except OSError:
            pass
    return made


def fetch_clips(
    task_id: str,
    queries: List[str],
    video_width: int,
    video_height: int,
    max_videos: int = 3,
    clip_len: float = 3.0,
    clips_per_video: int = 5,
    max_clips: int = 24,
    max_height: int = 720,
    max_filesize_mb: int = 80,
    retries: int = 3,
) -> List[str]:
    """
    Download + cut real highlight footage for `queries`. Returns a list of local
    vertical .mp4 clip paths (already 9:16). Best-effort: failures are skipped,
    never raised, so the pipeline can fall back to image_search.
    """
    if not queries:
        return []
    if not _which("ffmpeg"):
        logger.error("auto_footage: ffmpeg not found, skipping real footage")
        return []
    use_node = bool(_which("node") or _which("deno"))

    root = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "storage", "cache_videos", "auto",
    )
    key = hashlib.md5(("|".join(queries)).encode()).hexdigest()[:10]
    dl_dir = os.path.join(root, key, "src")
    cut_dir = os.path.join(root, key, "clips")
    os.makedirs(dl_dir, exist_ok=True)
    os.makedirs(cut_dir, exist_ok=True)

    # Reuse already-cut clips if this exact query set ran before (fast re-runs).
    existing = [os.path.join(cut_dir, f) for f in sorted(os.listdir(cut_dir))
                if f.lower().endswith(".mp4")
                and ".seg" not in f.lower() and ".proc" not in f.lower()] if os.path.isdir(cut_dir) else []
    if len(existing) >= min(max_clips, 6):
        logger.info(f"auto_footage: reusing {len(existing)} cached clips for this query set")
        return existing[:max_clips]

    logger.info(f"auto_footage: fetching real footage for {len(queries)} queries "
                f"(node_js={use_node}, target {max_height}p, "
                f"jev_triage={'on' if _jev_enabled() else 'off'})")
    n_have = len([f for f in os.listdir(dl_dir) if f.lower().endswith(VIDEO_EXTS)])

    # Downloads used to run one query at a time. Measured on EP12: 16 minutes of a
    # 18-minute build with nothing written to disk, because yt-dlp spends nearly all of
    # that waiting on the network. Queries are dispatched in waves of DOWNLOAD_WORKERS
    # instead -- waves rather than one big pool so the max_videos cap is still honoured
    # and we stop as soon as there is enough footage, rather than fetching every query.
    workers = max(1, min(int(os.environ.get("MPT_DOWNLOAD_WORKERS", DOWNLOAD_WORKERS)), 10))
    pending = list(queries)
    while pending and n_have < max_videos:
        wave, pending = pending[:workers], pending[workers:]
        _fetch = _download_one_triaged if _jev_enabled() else _download_one
        if len(wave) == 1:
            results = [(wave[0], _fetch(wave[0], dl_dir, max_height,
                                        max_filesize_mb, use_node,
                                        240, retries))]
        else:
            from concurrent.futures import ThreadPoolExecutor
            with ThreadPoolExecutor(max_workers=len(wave)) as pool:
                futs = {pool.submit(_fetch, q, dl_dir, max_height,
                                    max_filesize_mb, use_node, 240, retries): q
                        for q in wave}
                results = [(futs[f], f.result()) for f in futs]
        for q, got in results:
            for g in got:
                logger.info(f"auto_footage: downloaded '{q[:42]}' → {os.path.basename(g)}")
        n_have = len([f for f in os.listdir(dl_dir) if f.lower().endswith(VIDEO_EXTS)])
        logger.info(f"auto_footage: {n_have}/{max_videos} source videos after wave of "
                    f"{len(wave)} ({len(pending)} queries left)")
    # Use every source video present in the cache dir (handles already-downloaded
    # files that yt-dlp skips on re-run).
    downloaded = sorted(os.path.join(dl_dir, f) for f in os.listdir(dl_dir)
                        if f.lower().endswith(VIDEO_EXTS))[:max_videos]
    if not downloaded:
        logger.warning("auto_footage: no source videos downloaded — falling back to image_search")
        return []

    # Cutting is N independent ffmpeg jobs, one per source, and ran serially -- about
    # half of auto_footage's share of a 580s build. Fan out, then reassemble in the
    # ORIGINAL source order: clip order feeds timed sync, so completion order would
    # quietly reshuffle which shot lands on which caption.
    clips: List[str] = []
    _cut_workers = max(1, min(int(os.environ.get("MPT_CUT_WORKERS", "6")), 8))
    if len(downloaded) > 1 and _cut_workers > 1:
        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=_cut_workers) as pool:
            _made = list(pool.map(
                lambda src: _cut_vertical_clips(
                    src, cut_dir, os.path.splitext(os.path.basename(src))[0],
                    clip_len, clips_per_video, video_width, video_height,
                ), downloaded))
        for src, made in zip(downloaded, _made):
            clips.extend(made)
            logger.info(f"auto_footage: cut {len(made)} clips from {os.path.basename(src)}")
            if len(clips) >= max_clips:
                break
    else:
        for src in downloaded:
            base = os.path.splitext(os.path.basename(src))[0]
            made = _cut_vertical_clips(
                src, cut_dir, base, clip_len, clips_per_video, video_width, video_height,
            )
            clips.extend(made)
            logger.info(f"auto_footage: cut {len(made)} clips from {os.path.basename(src)}")
            if len(clips) >= max_clips:
                break

    clips = clips[:max_clips]
    logger.success(f"auto_footage: produced {len(clips)} vertical highlight clips")
    return clips


# --- Jev source triage ---------------------------------------------------------
# The only pre-download filter used to be _title_filter()/_claim_filter(): case-sensitive
# yt-dlp keyword blacklists. They cannot tell "Ronaldo's 2006 wink, broadcast footage"
# from "TOP 10 RONALDO MOMENTS (fan edit)" -- both pass, and the junk only gets caught
# much later by CLIP, after we have paid to download and cut it. yt-dlp can list the
# search results as TEXT (--flat-playlist --dump-json) before downloading anything, so
# a text model can read title/channel/description and judge them first.
#
# Opt-in: set MPT_JEV_TRIAGE=1. Without it (or without TYPESAFE_API_KEY, or on any API
# error) this falls back to the original _download_one path, so a Jev outage can never
# block a build.
JEV_MIN_SCORE = float(os.environ.get("MPT_JEV_MIN_SCORE", "0.45"))
# Hard disqualifiers, checked separately from the weighted score.
JEV_FOOTAGE_MIN = float(os.environ.get("MPT_JEV_FOOTAGE_MIN", "0.35"))
JEV_SUBJECT_MIN = float(os.environ.get("MPT_JEV_SUBJECT_MIN", "0.50"))


def _jev_enabled() -> bool:
    if os.environ.get("MPT_JEV_TRIAGE", "") != "1":
        return False
    if not os.environ.get("TYPESAFE_API_KEY"):
        _load_env_key()
    return bool(os.environ.get("TYPESAFE_API_KEY"))


def _load_env_key() -> None:
    """Pick TYPESAFE_API_KEY out of the repo .env if it is not already exported."""
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    path = os.path.join(root, ".env")
    if not os.path.isfile(path):
        return
    try:
        for line in open(path):
            line = line.strip()
            if line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            if k.strip() == "TYPESAFE_API_KEY":
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
    except Exception as e:
        logger.warning(f"auto_footage: could not read .env for Jev key: {e}")


def _search_metadata(query: str, depth: int, use_node: bool, timeout: int = 90) -> List[dict]:
    """List search results as metadata only -- no download, no video bytes."""
    ytdlp = _ytdlp_bin()
    if not ytdlp:
        return []
    cmd = [
        ytdlp, "--flat-playlist", "--dump-json", "--no-warnings", "--ignore-errors",
        "--socket-timeout", "20", *_cookies_args(), f"ytsearch{depth}:{query}",
    ]
    if use_node:
        cmd[1:1] = ["--extractor-args", "youtube:player_client=default,web_safari;jsi=Deno"]
    try:
        r = _run(cmd, timeout=timeout)
    except subprocess.TimeoutExpired:
        logger.warning(f"auto_footage: metadata search timed out for '{query[:40]}'")
        return []
    out = []
    for line in (r.stdout or "").splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            d = json.loads(line)
        except Exception:
            continue
        dur = d.get("duration") or 0
        try:
            dur = float(dur)
        except Exception:
            dur = 0.0
        # Same hard bounds the old --match-filter enforced. Duration is arithmetic:
        # it stays in code, the model never sees a number it has to compare.
        if not (12 < dur < 1200):
            continue
        chan = (d.get("channel") or d.get("uploader") or "")
        title = d.get("title") or ""
        # Rightsholder banlist is legal policy, not a judgement call -- keep it in code.
        if any(c.lower() in chan.lower() for c in CLAIM_HEAVY_CHANNELS):
            continue
        # Keep the proven keyword blacklist too. Triage replaces the JUDGEMENT calls,
        # not the deterministic ones: a free exact filter should never be handed to a
        # model. Matching here is case-INSENSITIVE, which also sidesteps the yt-dlp
        # `title!*=` case-sensitivity trap that made _title_filter() a no-op.
        if any(t in title.lower() for t in NON_FOOTAGE_TITLE_TERMS):
            continue
        if any(c.lower() in chan.lower() for c in NON_FOOTAGE_CHANNELS):
            continue
        if not d.get("id"):
            continue
        out.append({
            "id": d["id"],
            "title": d.get("title") or "",
            "channel": chan,
            "duration_seconds": int(dur),
            "description": (d.get("description") or "")[:400],
        })
    return out


def _jev_triage(cands: List[dict], query: str) -> List[dict]:
    """Score candidates on whether they really are broadcast footage of the subject.

    Returns candidate dicts filtered and sorted best-first, each carrying `jev_score`
    and the raw `jev` judgements. On any failure every candidate is returned with a
    just-below-threshold score, so triage can only ever reorder -- never starve -- the
    download step.
    """
    if not cands:
        return cands
    # Callers may reach this directly (tests, other modules), so never assume
    # _jev_enabled() already ran and loaded the key.
    if not os.environ.get("TYPESAFE_API_KEY"):
        _load_env_key()
    try:
        from typesafe_sdk import TypeSafeClient, Noul
    except ImportError:
        logger.warning("auto_footage: typesafe-sdk not installed, skipping Jev triage")
        return [dict(c, jev_score=JEV_MIN_SCORE - 0.01, jev=None) for c in cands]

    questions = {
        # This asks for PRIMARY footage, not "match action". A press conference or a
        # tunnel camera IS the real filmed event for some topics; a studio pundit
        # discussing that event afterwards is not. Asking for "match action" made the
        # model rate genuine farewell-press-conference video at 0.02.
        "is_primary_footage": Noul(instructions=(
            "Judging only from its title, channel and description, does this video show "
            "the real event actually happening on camera -- match play, a filmed incident, "
            "or the live press conference or ceremony itself -- rather than people "
            "discussing, analysing, reacting to or narrating the event after the fact, "
            "or a video-game recreation?")),
        "shows_subject": Noul(instructions=(
            "Does this video feature the specific player or team named in `search_intent` "
            "as its main subject, rather than merely mentioning them in passing or being "
            "about a different player?")),
        "matches_event": Noul(instructions=(
            "Does this video cover the particular match, moment or incident described in "
            "`search_intent`, rather than that player's career in general?")),
        "is_edit_or_compilation": Noul(instructions=(
            "Is this a fan edit, a 'top 10' countdown, a skills/goals compilation, or a "
            "montage set to music -- as opposed to continuous footage of one match or "
            "one incident?")),
    }

    client = TypeSafeClient()

    def judge(c):
        try:
            r = client.system_one(
                state={"search_intent": query, "video": {
                    "title": c["title"], "channel": c["channel"],
                    "description": c["description"],
                    "duration_seconds": c["duration_seconds"]}},
                questions=questions)
            a = r.answers
            return {
                "footage": a["is_primary_footage"].noul,
                "subject": a["shows_subject"].noul,
                "event": a["matches_event"].noul,
                "edit": a["is_edit_or_compilation"].noul,
            }
        except Exception as e:
            logger.warning(f"auto_footage: Jev triage failed for {c['id']}: {e}")
            return None

    from concurrent.futures import ThreadPoolExecutor
    try:
        with ThreadPoolExecutor(max_workers=8) as pool:
            judgements = list(pool.map(judge, cands))
    finally:
        try:
            client.close()
        except Exception:
            pass

    if all(j is None for j in judgements):
        logger.warning("auto_footage: Jev triage returned nothing usable, using raw search order")
        return [dict(c, jev_score=JEV_MIN_SCORE - 0.01, jev=None) for c in cands]

    scored = []
    for c, j in zip(cands, judgements):
        if j is None:
            # Unjudged candidates sit just below the pass mark rather than being dropped:
            # an API hiccup must not shrink the pool. Pool starvation is what puts the
            # wrong player on screen.
            c = dict(c, jev_score=JEV_MIN_SCORE - 0.01, jev=None, jev_ok=True)
        else:
            # Two HARD conditions, then a weighted rank among whatever survives them.
            # A plain weighted sum let a 0.99 subject score carry a clip whose footage
            # score was 0.02 -- the compensating-preferences trap. Wrong-person and
            # not-really-footage are disqualifying, not merely costly.
            disqualified = (j["footage"] < JEV_FOOTAGE_MIN) or (j["subject"] < JEV_SUBJECT_MIN)
            score = (0.40 * j["footage"] + 0.35 * j["subject"]
                     + 0.15 * j["event"] + 0.10 * (1.0 - j["edit"]))
            c = dict(c, jev_score=round(score, 3), jev=j, jev_ok=not disqualified)
        scored.append(c)

    scored.sort(key=lambda x: -x["jev_score"])
    kept = [c for c in scored if c.get("jev_ok", True) and c["jev_score"] >= JEV_MIN_SCORE]
    kept_ids = {c["id"] for c in kept}
    dropped = [c for c in scored if c["id"] not in kept_ids]
    for c in dropped[:4]:
        logger.info(f"auto_footage: Jev dropped {c['jev_score']:.2f} '{c['title'][:52]}' [{c['channel'][:22]}]")
    if not kept:
        # Everything failed the bar. Returning the best two anyway beats an empty pool.
        logger.warning(f"auto_footage: Jev rejected all {len(scored)} results for "
                       f"'{query[:40]}' -- keeping best 2 to protect the pool")
        return scored[:2]
    logger.info(f"auto_footage: Jev kept {len(kept)}/{len(scored)} for '{query[:40]}' "
                f"(best {kept[0]['jev_score']:.2f} '{kept[0]['title'][:44]}')")
    return kept


def _download_one_triaged(query: str, dest_dir: str, max_height: int, max_filesize_mb: int,
                          use_node: bool, timeout: int, retries: int = 3,
                          want: int = 2) -> List[str]:
    """Search -> judge the text metadata -> download only what survives."""
    depth = max(6, min(int(os.environ.get("MPT_JEV_SEARCH_DEPTH", "12")), 25))
    cands = _search_metadata(query, depth, use_node)
    if not cands:
        logger.info(f"auto_footage: no metadata for '{query[:40]}', falling back to direct download")
        return _download_one(query, dest_dir, max_height, max_filesize_mb, use_node, timeout, retries)
    kept = _jev_triage(cands, query)
    got, attempts = [], 0
    # Walk DOWN the ranked list on failure instead of stopping at `want`. Individual
    # videos die for reasons triage cannot see (removed, geo-blocked, no mp4 under the
    # size cap), and one dud link used to cost this query its entire contribution to
    # the pool. Attempts are capped so a run of dead links cannot stall the build.
    for c in kept:
        if len(got) >= want or attempts >= want + 3:
            break
        attempts += 1
        path = _download_url(f"https://www.youtube.com/watch?v={c['id']}", dest_dir,
                             max_height, max_filesize_mb, use_node, timeout, retries,
                             video_id=c["id"])
        if path and path not in got:
            got.append(path)
    if not got:
        logger.warning(f"auto_footage: triage found sources for '{query[:40]}' but none "
                       f"downloaded after {attempts} attempts")
    return got


def _download_url(url: str, dest_dir: str, max_height: int, max_filesize_mb: int,
                  use_node: bool, timeout: int, retries: int = 3,
                  video_id: str = "") -> str:
    """Download ONE specific YouTube URL (not a search). Returns the local path.

    `video_id` matters when dest_dir is a SHARED pool directory: without it the reuse
    shortcut below returns whatever video happens to be in the directory already, so a
    second call for a different id hands back the first file. That silently collapses
    the footage pool to one source -- caught 29 Sep 2026 when triage "downloaded" two
    clips and both were the same mp4.
    """
    ytdlp = _ytdlp_bin()
    if not ytdlp:
        logger.error("auto_footage: yt-dlp not found")
        return ""
    before = set(os.listdir(dest_dir)) if os.path.isdir(dest_dir) else set()
    # Existing download for this id? reuse it.
    existing = [os.path.join(dest_dir, f) for f in before
                if f.lower().endswith(VIDEO_EXTS)
                and (not video_id or f.startswith(video_id + "."))]
    if existing:
        return sorted(existing)[0]
    fmt = (
        f"bestvideo[height<={max_height}][vcodec^=avc1][ext=mp4]/"
        f"bestvideo[height<={max_height}][ext=mp4]/"
        f"best[height<={max_height}][ext=mp4]/best[ext=mp4]/best"
    )
    cmd = [
        ytdlp, "--no-playlist", "--socket-timeout", "20",
        "--no-warnings", "--ignore-errors",
        "--retries", str(retries), "--extractor-retries", str(retries),
        "-f", fmt,
        "--max-filesize", f"{max_filesize_mb}M",
        "-o", os.path.join(dest_dir, "%(id)s.%(ext)s"),
        *_cookies_args(),
        url,
    ]
    if use_node:
        cmd[1:1] = ["--extractor-args", "youtube:player_client=default,web_safari;jsi=Deno"]
    try:
        r = _run(cmd, timeout=timeout)
        if r.returncode != 0:
            logger.warning(f"auto_footage: yt-dlp non-zero for url: {r.stderr.strip()[-180:]}")
    except subprocess.TimeoutExpired:
        logger.warning("auto_footage: yt-dlp timed out for url")
    after = set(os.listdir(dest_dir)) if os.path.isdir(dest_dir) else set()
    new = [os.path.join(dest_dir, f) for f in (after - before) if f.lower().endswith(VIDEO_EXTS)]
    return sorted(new)[0] if new else ""


def fetch_exact_clip(
    url: str, start: float, end: float, video_width: int, video_height: int,
    out_path: str, max_height: int = 720, max_filesize_mb: int = 200,
    fill: str = "cover", retries: int = 3,
) -> str:
    """
    Download ONE specific YouTube video by URL and cut the EXACT [start, end]
    window, reframed to vertical 9:16. This is the precise-moment path for the
    comparison/match-cut series (vs the search-based fetch_clips above).
    Returns the path to the cut clip (out_path) or "" on failure. Source videos
    are cached so re-runs / multiple cuts from the same video don't re-download.

    fill:
      "cover"   – crop-to-fill the 9:16 frame (good for vertical/centered sources;
                  on a WIDE landscape subject it zooms in and cuts the sides off).
      "contain" – fit the WHOLE frame inside 9:16 over a blurred zoomed copy of
                  itself, so a horizontal subject (e.g. a running cheetah) stays
                  fully in frame with no black bars.
    """
    if not _which("ffmpeg"):
        logger.error("auto_footage: ffmpeg not found")
        return ""
    use_node = bool(_which("node") or _which("deno"))
    root = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "storage", "cache_videos", "comparison",
    )
    key = hashlib.md5(url.encode()).hexdigest()[:12]
    src_dir = os.path.join(root, key)
    os.makedirs(src_dir, exist_ok=True)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    src = _download_url(
        url, src_dir, max_height, max_filesize_mb, use_node,
        timeout=300, retries=retries,
    )
    if not src:
        logger.warning(f"auto_footage: could not download {url}")
        return ""

    dur = max(0.1, float(end) - float(start))
    W, H = video_width, video_height
    if fill == "contain":
        # Whole subject visible: a blurred zoom-to-fill copy as the background,
        # the full (un-cropped) frame fit on top and centred.
        vf = (
            f"split=2[bg][fg];"
            f"[bg]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},gblur=sigma=24[bgb];"
            f"[fg]scale={W}:{H}:force_original_aspect_ratio=decrease[fgs];"
            f"[bgb][fgs]overlay=(W-w)/2:(H-h)/2,setsar=1"
        )
    else:
        # Subject-aware reframe. The old filter cropped dead centre: on a 1920x1080
        # broadcast frame the 9:16 window is 608px, so 68% of the width was discarded
        # blind on every clip. If the action sat anywhere but the middle it was simply
        # gone -- which is how referees, grass and half-cropped heads reached the edit.
        # craft.subject_window scores a probe frame and returns the window that actually
        # holds the subject; below its confidence floor it returns dead centre, so the
        # fallback is byte-identical to the previous behaviour.
        crop_expr = None
        reject_text = bool(globals().get("_REJECT_BURNED_IN_TEXT", True))
        try:
            from app.services import craft
            probe = f"{out_path}.probe.jpg"
            pr = _run(["ffmpeg", "-y", "-loglevel", "error",
                       "-ss", f"{float(start) + dur / 2:.3f}", "-i", src,
                       "-frames:v", "1", "-q:v", "3", probe], timeout=60)
            if pr.returncode == 0 and os.path.exists(probe):
                # Reject broadcast furniture HERE, while the caller can still choose a
                # different clip. The MEMORIAS DO MELHOR bar sat across ~8 of EP12's 18
                # frames because CLIP scores content, not furniture, and because the
                # source was banned by video id -- and the same documentary was
                # re-uploaded under a new id the same day.
                if reject_text:
                    bands = craft.all_text_furniture(probe)
                    if bands:
                        b = bands[0]
                        logger.warning(
                            f"auto_footage: REJECTED {os.path.basename(str(url))[:24]} "
                            f"[{start:.1f}-{end:.1f}] - burned-in text band at "
                            f"y={b['y0']:.2f}-{b['y1']:.2f} (score {b['score']}, "
                            f"{b['width_frac']:.0%} of width)")
                        try:
                            os.remove(probe)
                        except Exception:
                            pass
                        return ""
                win = craft.subject_window(probe, W, H)
                if win and win.get("w"):
                    crop_expr = f"crop={win['w']}:{win['h']}:{win['x']}:{win['y']}"
                    logger.info(f"auto_footage: reframe {win['method']} "
                                f"x={win['x']} (drift {win.get('drift', 0):+.1%})")
                try:
                    os.remove(probe)
                except Exception:
                    pass
        except Exception as e:
            logger.debug(f"auto_footage: reframe unavailable, centring ({e})")
        if not crop_expr:
            crop_expr = f"crop='min(iw,ih*{W}/{H})':'min(ih,iw*{H}/{W})'"
        vf = (
            f"{crop_expr},"
            f"scale={W}:{H}:force_original_aspect_ratio=increase,"
            f"crop={W}:{H},setsar=1"
        )
    cmd = [
        "ffmpeg", "-y", "-loglevel", "error",
        "-ss", f"{float(start):.3f}", "-i", src, "-t", f"{dur:.3f}",
        "-an", "-vf", vf,
        # This cut ALSO performs the crop+upscale to 1080x1920, so it is the worst
        # place to lose detail. Matches the intermediate cut above (was veryfast/CRF 18).
        "-c:v", "libx264", "-preset", "fast", "-crf", "16",
        "-pix_fmt", "yuv420p", out_path,
    ]
    try:
        r = _run(cmd, timeout=180)
        if r.returncode == 0 and os.path.exists(out_path) and os.path.getsize(out_path) > 10000:
            logger.success(f"auto_footage: cut exact clip [{start:.1f}-{end:.1f}] → {os.path.basename(out_path)}")
            return out_path
        logger.warning(f"auto_footage: exact cut failed: {r.stderr.strip()[-160:]}")
    except subprocess.TimeoutExpired:
        logger.warning("auto_footage: exact cut timed out")
    return ""
