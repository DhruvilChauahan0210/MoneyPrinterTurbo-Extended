"""Craft helpers: the judgements a human editor makes that the builder could not.

Every function here degrades gracefully. OpenCV (face detection) and imagehash
(perceptual hashing) sharpen the results when installed, but nothing requires them --
the PIL + numpy paths are the default and are what runs today:

    ./.venv/bin/pip install opencv-python-headless imagehash

Written 28 Aug 2026 after looking at EP12 frame by frame and finding: a broadcaster's
chyron across ~8 of 18 frames, five interchangeable ICU monitors, a 2023 shot in an
age-15 story, and a centre crop that had thrown away 68% of every broadcast frame.
"""
from __future__ import annotations
import math, os
from typing import Optional, Tuple, List

import numpy as np
from PIL import Image
from loguru import logger

try:                       # optional, materially better when present
    import cv2             # type: ignore
    _HAS_CV2 = True
except Exception:
    cv2 = None
    _HAS_CV2 = False

try:
    import imagehash       # type: ignore
    _HAS_IMAGEHASH = True
except Exception:
    imagehash = None
    _HAS_IMAGEHASH = False


def capabilities() -> str:
    return (f"craft: cv2={'yes' if _HAS_CV2 else 'no (saliency fallback)'}, "
            f"imagehash={'yes' if _HAS_IMAGEHASH else 'no (dhash fallback)'}")


# ---------------------------------------------------------------- loading ----

def _load_gray(src, max_w: int = 320):
    """Return (gray float array, (orig_w, orig_h)) from a path or PIL image."""
    im = Image.open(src) if isinstance(src, (str, os.PathLike)) else src
    im = im.convert("RGB")
    ow, oh = im.size
    if ow > max_w:
        im = im.resize((max_w, max(1, int(oh * max_w / ow))), Image.BILINEAR)
    return np.asarray(im.convert("L"), dtype=np.float32), (ow, oh), im


# ------------------------------------------------- burned-in text / chyrons ----

def detect_text_bands(src, min_score: float = 5.0) -> List[dict]:
    """Find burned-in horizontal text bars: chyrons, lower thirds, hardcoded subtitles.

    A broadcast caption bar has a signature no photograph has: a band of rows whose
    horizontal edge energy spikes far above the rest of the frame, spanning most of the
    width, sitting in the title-safe zones. That is what the CLIP subject gate cannot
    see -- it scores content, not furniture -- and it is why the same documentary kept
    coming back under new video ids with 'MEMORIAS DO MELHOR 2001' across frame one.

    Returns one dict per band: y0, y1 (fractions of height), score, width_frac.

    Default threshold 5.0 comes from a sweep over EP12's twelve source frames: the real
    furniture (the MEMORIAS bar, a source's burned-in subtitles) scores 11.3 and 19.5,
    while the strongest innocent structure (an ECG printout, all horizontal lines) tops
    out at 3.3. Anything from 3.5 to 11 separates them perfectly; 5.0 sits mid-band.
    """
    try:
        g, (ow, oh), _ = _load_gray(src)
        h, w = g.shape
        if h < 40 or w < 40:
            return []

        dx = np.abs(np.diff(g, axis=1))                 # horizontal gradient
        row_energy = dx.mean(axis=1)
        med = float(np.median(row_energy)) or 1e-6
        ratio = row_energy / med

        # Title-safe zones: text furniture lives at the top or bottom, not mid-frame.
        zone = np.zeros(h, dtype=bool)
        zone[: int(h * 0.30)] = True
        zone[int(h * 0.66):] = True

        hot = (ratio > min_score) & zone
        bands, run = [], None
        for y in range(h):
            if hot[y] and run is None:
                run = y
            elif not hot[y] and run is not None:
                bands.append((run, y)); run = None
        if run is not None:
            bands.append((run, h))

        out = []
        for y0, y1 in bands:
            frac = (y1 - y0) / h
            if not (0.020 <= frac <= 0.30):             # too thin = noise, too tall = scene
                continue
            strip = dx[y0:y1]
            # A real bar runs across the frame; a face's eyes do not.
            col_hot = (strip.mean(axis=0) > med * min_score)
            width_frac = float(col_hot.mean())
            if width_frac < 0.35:
                continue
            hot_idx = np.flatnonzero(col_hot)
            out.append({
                "y0": round(y0 / h, 3), "y1": round(y1 / h, 3),
                "score": round(float(ratio[y0:y1].mean()), 2),
                "width_frac": round(width_frac, 3),
                "x0": round(float(hot_idx[0] / w), 3) if hot_idx.size else 0.0,
                "x1": round(float(hot_idx[-1] / w), 3) if hot_idx.size else 1.0,
            })
        return out
    except Exception as e:
        logger.debug(f"detect_text_bands failed: {e}")
        return []


def has_burned_in_text(src, min_score: float = 5.0) -> bool:
    return bool(detect_text_bands(src, min_score=min_score))


# ---------------------------------------------------------- subject window ----

# Edge energy alone is a trap: scoreboards, sponsor boards and chyrons are the
# highest-contrast things in a broadcast frame, so a naive saliency crop is pulled
# straight onto the furniture. Skin dominates; edges only break ties.
_SKIN_W, _EDGE_W = 5.0, 0.6
_FURNITURE_PENALTY = 6.0   # per-pixel cost of keeping a scoreboard or chyron in frame
_SUBJECT_SKIN_FLOOR = 0.045  # below this there is not enough person in frame to reframe for


def _skin_mask(rgb: np.ndarray) -> np.ndarray:
    """Classic YCbCr skin range. On football footage this is effectively 'where the
    people are' -- faces, arms, legs -- which is exactly what the crop must keep."""
    r = rgb[..., 0].astype(np.float32)
    g = rgb[..., 1].astype(np.float32)
    b = rgb[..., 2].astype(np.float32)
    cb = 128 - 0.168736 * r - 0.331264 * g + 0.5 * b
    cr = 128 + 0.5 * r - 0.418688 * g - 0.081312 * b
    y = 0.299 * r + 0.587 * g + 0.114 * b
    return ((cb >= 77) & (cb <= 127) & (cr >= 133) & (cr <= 173) & (y > 40)).astype(np.float32)


def _cv2_faces(pil_im, min_size: int = 28) -> List[Tuple[int, int, int, int]]:
    """Haar needs pixels. At 240px wide a broadcast face is ~20px and is missed, so
    callers pass a larger image and scale the result back themselves."""
    if not _HAS_CV2:
        return []
    try:
        arr = cv2.cvtColor(np.asarray(pil_im), cv2.COLOR_RGB2GRAY)
        arr = cv2.equalizeHist(arr)
        found = []
        for name in ("haarcascade_frontalface_default.xml", "haarcascade_profileface.xml"):
            path = os.path.join(cv2.data.haarcascades, name)
            if not os.path.exists(path):
                continue
            c = cv2.CascadeClassifier(path)
            for (x, y, w, h) in c.detectMultiScale(arr, 1.08, 4, minSize=(min_size, min_size)):
                found.append((int(x), int(y), int(w), int(h)))
        return found
    except Exception:
        return []


def subject_window(src, out_w: int, out_h: int, centre_bias: float = 0.30) -> dict:
    """Choose the crop window that actually contains the subject.

    The pipeline cropped dead centre: on a 1920x1080 broadcast frame the 9:16 window is
    607px, so 68% of the width was discarded blind, every time. If the action sat
    anywhere but the middle it was simply gone -- which is how referees, grass and
    half-cropped heads reached the edit.

    Scores every candidate column by skin mass (weighted 3x) plus edge energy, takes the
    best window, then blends `centre_bias` back toward centre so the crop cannot swing
    wildly between shots. A detected face overrides the saliency pick and is placed on
    the upper thirds line, where a portrait wants to sit.

    Returns {x, y, w, h} in SOURCE pixels, plus how the decision was made.
    """
    try:
        im = Image.open(src) if isinstance(src, (str, os.PathLike)) else src
        im = im.convert("RGB")
        ow, oh = im.size
        target = out_w / out_h

        # The window: as large as fits at the target aspect.
        if ow / oh > target:
            cw, ch = int(round(oh * target)), oh
        else:
            cw, ch = ow, int(round(ow / target))
        cw, ch = min(cw, ow), min(ch, oh)
        if cw >= ow and ch >= oh:
            return {"x": 0, "y": 0, "w": ow, "h": oh, "method": "exact-fit"}

        # Face pass runs on a bigger image than the saliency pass -- Haar needs pixels.
        face_w = 560 if ow >= 560 else ow
        fim = im.resize((face_w, max(1, int(oh * face_w / ow))), Image.BILINEAR)
        faces = _cv2_faces(fim)
        method = "saliency"
        if faces:
            fscale = ow / fim.size[0]
            fx, fy, fw, fh = max(faces, key=lambda f: f[2] * f[3])
            cx = (fx + fw / 2) * fscale
            cy = (fy + fh / 2) * fscale
            method = "face"

        small_w = 240
        sm = im.resize((small_w, max(1, int(oh * small_w / ow))), Image.BILINEAR)
        arr = np.asarray(sm, dtype=np.uint8)
        sh, sw = arr.shape[:2]
        scale = ow / sw

        if not faces:
            skin = _skin_mask(arr)
            gray = np.asarray(sm.convert("L"), dtype=np.float32)
            edge = np.abs(np.gradient(gray)[1]) + np.abs(np.gradient(gray)[0])
            score = _SKIN_W * skin + _EDGE_W * (edge / (edge.max() or 1.0))
            # Furniture must REPEL the window, not merely fail to attract it. Zeroing the
            # band was not enough: on a wide stadium frame the crop still landed on the
            # players and dragged the "2-3 ESP 86:58" scoreboard in with them. Scoring the
            # band's own columns strongly negative makes any window containing it lose.
            for band in detect_text_bands(sm):
                by0, by1 = int(band["y0"] * sh), int(band["y1"] * sh) + 1
                bx0, bx1 = int(band["x0"] * sw), int(band["x1"] * sw) + 1
                score[by0:by1, bx0:bx1] = -_FURNITURE_PENALTY
            col = score.sum(axis=0)
            row = score.sum(axis=1)
            win = max(1, int(cw / scale))
            if win < sw:
                csum = np.concatenate([[0.0], np.cumsum(col)])
                sums = csum[win:] - csum[:-win]
                # Only move the window when there is a subject worth moving it to.
                # Skin mass is the honest confidence signal here. A best-window-versus-
                # average-window ratio was tried first and ranked a wide crowd shot ABOVE
                # a clean mid-shot of the player, because on a busy frame every window
                # scores alike and the winner is noise -- chasing it dragged a corner
                # scoreboard into frame (too compact for the band detector to catch on a
                # high-detail frame). Below the floor, stay centred: that is exactly
                # today's behaviour, so the fallback can never be worse than the status quo.
                if float(skin.mean()) >= _SUBJECT_SKIN_FLOOR:
                    cx = (int(np.argmax(sums)) + win / 2) * scale
                else:
                    cx = ow / 2
                    method = "centre (low confidence)"
            else:
                cx = ow / 2
            winr = max(1, int(ch / scale))
            if winr < sh:
                rsum = np.concatenate([[0.0], np.cumsum(row)])
                sumsr = rsum[winr:] - rsum[:-winr]
                cy = (int(np.argmax(sumsr)) + winr / 2) * scale
            else:
                cy = oh / 2

        # Blend back toward centre so consecutive shots do not lurch.
        cx = cx * (1 - centre_bias) + (ow / 2) * centre_bias
        cy = cy * (1 - centre_bias) + (oh / 2) * centre_bias

        if method == "face":
            # A face reads best on the upper thirds line, not dead centre.
            cy = cy + ch * 0.10

        x = int(round(max(0, min(ow - cw, cx - cw / 2))))
        y = int(round(max(0, min(oh - ch, cy - ch / 2))))
        return {"x": x, "y": y, "w": int(cw), "h": int(ch), "method": method,
                "drift": round((x + cw / 2 - ow / 2) / ow, 3)}
    except Exception as e:
        logger.debug(f"subject_window failed: {e}")
        return {}


# ------------------------------------------------------------- shot sizing ----

def subject_scale(src) -> float:
    """Roughly how much of the frame the subject occupies: 0 = wide, 1 = close-up.
    Used to spread shot sizes instead of clustering on whatever CLIP scored highest."""
    try:
        im = Image.open(src) if isinstance(src, (str, os.PathLike)) else src
        im = im.convert("RGB")
        sm = im.resize((160, max(1, int(im.size[1] * 160 / im.size[0]))), Image.BILINEAR)
        faces = _cv2_faces(sm)
        if faces:
            fx, fy, fw, fh = max(faces, key=lambda f: f[2] * f[3])
            return float(min(1.0, (fw * fh) / (sm.size[0] * sm.size[1]) * 12.0))
        return float(min(1.0, _skin_mask(np.asarray(sm, dtype=np.uint8)).mean() * 4.0))
    except Exception:
        return 0.0


def shot_size(src) -> str:
    s = subject_scale(src)
    return "close" if s >= 0.45 else ("medium" if s >= 0.18 else "wide")


# -------------------------------------------------------- perceptual hash ----

def frame_hash(src) -> str:
    """Perceptual hash of a frame.

    Banning by source id does not work: the documentary banned on 26 Aug walked straight
    back in under a different video id the same day. Content hashing survives re-upload,
    re-encode and rescale.
    """
    try:
        im = Image.open(src) if isinstance(src, (str, os.PathLike)) else src
        im = im.convert("RGB")
        if _HAS_IMAGEHASH:
            return str(imagehash.phash(im, hash_size=8))
        g = np.asarray(im.convert("L").resize((9, 8), Image.BILINEAR), dtype=np.float32)
        bits = (g[:, 1:] > g[:, :-1]).flatten()
        return "".join(f"{int(''.join('1' if b else '0' for b in bits[i:i + 4]), 2):x}"
                       for i in range(0, len(bits), 4))
    except Exception:
        return ""


def hash_distance(a: str, b: str) -> int:
    """Hamming distance between two hashes; 64 (max) when incomparable."""
    if not a or not b or len(a) != len(b):
        return 64
    try:
        return bin(int(a, 16) ^ int(b, 16)).count("1")
    except Exception:
        return 64


def matches_any_hash(h: str, banned: List[str], threshold: int = 8) -> bool:
    """threshold 8/64 catches re-encodes and rescales without colliding unrelated shots."""
    return any(hash_distance(h, b) <= threshold for b in (banned or []))


# ------------------------------------------------------------- editorial QA ----

def audit_media_plan(paths: List[str], subject_floor: float = 0.60,
                     dupe_threshold: int = 6) -> dict:
    """Judge the selected media before the render, not after.

    `validate_media_plan` already checks that the files exist, decode and are portrait --
    structural questions. It cannot answer the editorial one, which is why EP12 passed
    with `distinct_source_videos: 12` while five of those twelve were interchangeable ICU
    monitors and a broadcaster's chyron ran across half the runtime. The metric counted
    sources; nothing judged them.

    Returns a report. `ok` is False when the plan would produce a short worth rejecting --
    checked here because the channel renders once and ships, so anything caught after the
    render costs a rebuild the workflow does not allow.
    """
    report = {"clips": len(paths or []), "subject_present": 0, "burned_in_text": 0,
              "near_duplicates": 0, "brightness_spread": 0.0, "shot_sizes": {},
              "ok": True, "problems": []}
    if not paths:
        report["ok"] = False
        report["problems"].append("no media")
        return report

    hashes, brights, sizes = [], [], []
    for p in paths:
        try:
            import subprocess as _sp, io as _io
            if str(p).lower().endswith((".mp4", ".mov", ".webm", ".mkv", ".avi")):
                try:
                    import imageio_ffmpeg
                    ff = imageio_ffmpeg.get_ffmpeg_exe()
                except Exception:
                    ff = "ffmpeg"
                r = _sp.run([ff, "-hide_banner", "-nostats", "-i", str(p), "-frames:v", "1",
                             "-f", "image2pipe", "-vcodec", "png", "-"],
                            capture_output=True, timeout=60)
                if r.returncode != 0 or not r.stdout:
                    continue
                im = Image.open(_io.BytesIO(r.stdout)).convert("RGB")
            else:
                im = Image.open(p).convert("RGB")
        except Exception:
            continue

        sm = im.resize((160, max(1, int(im.size[1] * 160 / im.size[0]))), Image.BILINEAR)
        skin = float(_skin_mask(np.asarray(sm, dtype=np.uint8)).mean())
        if skin >= 0.030:
            report["subject_present"] += 1
        if detect_text_bands(im):
            report["burned_in_text"] += 1
        brights.append(float(np.asarray(sm.convert("L"), dtype=np.float32).mean()))
        sizes.append(shot_size(sm))
        h = frame_hash(im)
        if h and matches_any_hash(h, hashes, threshold=dupe_threshold):
            report["near_duplicates"] += 1
        if h:
            hashes.append(h)

    n = max(1, len(brights))
    report["brightness_spread"] = round(max(brights) - min(brights), 1) if brights else 0.0
    for s in sizes:
        report["shot_sizes"][s] = report["shot_sizes"].get(s, 0) + 1
    frac = report["subject_present"] / n
    report["subject_fraction"] = round(frac, 2)

    if frac < subject_floor:
        report["ok"] = False
        report["problems"].append(
            f"only {report['subject_present']}/{n} shots contain a person "
            f"({frac:.0%} < {subject_floor:.0%}) -- the pool has filled with stock")
    if report["burned_in_text"]:
        # Hard fail: these are now rejected at cut time, so anything reaching the gate
        # means the detector was bypassed or the pool had no clean alternative. Either
        # way it must not render -- this is the exact defect that put a broadcaster's
        # chyron on frame 1 of a shipped short.
        report["ok"] = False
        report["problems"].append(
            f"{report['burned_in_text']} shot(s) carry burned-in text (chyron/subtitles)")
    if report["near_duplicates"] > n * 0.34:
        report["problems"].append(
            f"{report['near_duplicates']}/{n} shots are near-duplicates of earlier ones")
    if report["brightness_spread"] > 110:
        # Warning only: _match_shots corrects exposure during preprocess_video, which runs
        # after this gate. Worth surfacing so a genuinely extreme plan is visible.
        report["problems"].append(
            f"brightness spread {report['brightness_spread']:.0f}/255 before shot matching "
            f"(will be corrected at render; flag only if it persists)")
    return report
