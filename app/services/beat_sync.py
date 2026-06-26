"""
Lightweight beat / drop detection for the phonk comparison series.

No librosa — decodes audio with ffmpeg and analyses it with numpy + scipy only
(both already in this repo's venv). Phonk has huge, clean kick/cowbell transients,
so a spectral-flux onset envelope + peak picking tracks beats reliably, and a
short-time energy jump finds the DROP (where the beat slams in).

Public API:
    analyze(audio_path) -> {
        "duration": float,           # seconds
        "bpm": float | None,         # estimated tempo
        "beats": [float, ...],       # beat onset times (seconds)
        "drop_time": float,          # time the beat drops / energy slams in
    }
    nearest_beat(beats, t) -> float  # snap a time to the closest detected beat
"""
import io
import subprocess
import shutil
from typing import List, Optional

import numpy as np
from loguru import logger

try:
    from scipy.signal import find_peaks
except Exception:  # pragma: no cover
    find_peaks = None

SR = 22050
HOP = 512
WIN = 1024


def _decode_mono(audio_path: str, sr: int = SR) -> np.ndarray:
    """Decode any audio file to a mono float32 numpy array at `sr` via ffmpeg."""
    if not shutil.which("ffmpeg"):
        raise RuntimeError("ffmpeg not found")
    cmd = [
        "ffmpeg", "-v", "error", "-i", audio_path,
        "-ac", "1", "-ar", str(sr), "-f", "f32le", "-",
    ]
    r = subprocess.run(cmd, capture_output=True, timeout=120)
    if r.returncode != 0 or not r.stdout:
        raise RuntimeError(f"ffmpeg decode failed: {r.stderr[-160:]!r}")
    return np.frombuffer(r.stdout, dtype=np.float32).copy()


def _onset_envelope(y: np.ndarray, sr: int = SR):
    """Spectral-flux onset strength envelope + its frame times (seconds)."""
    n = 1 + (len(y) - WIN) // HOP if len(y) >= WIN else 0
    if n <= 1:
        return np.zeros(1), np.zeros(1)
    window = np.hanning(WIN).astype(np.float32)
    mags = np.empty((n, WIN // 2 + 1), dtype=np.float32)
    for i in range(n):
        frame = y[i * HOP: i * HOP + WIN] * window
        mags[i] = np.abs(np.fft.rfft(frame))
    # Positive spectral flux: sum of positive frame-to-frame magnitude increases.
    flux = np.maximum(0.0, np.diff(mags, axis=0)).sum(axis=1)
    flux = np.concatenate([[0.0], flux])
    if flux.max() > 0:
        flux = flux / flux.max()
    times = (np.arange(n) * HOP) / float(sr)
    return flux, times


def _estimate_bpm(flux: np.ndarray, sr: int = SR) -> Optional[float]:
    """Rough tempo via autocorrelation of the onset envelope (60–200 BPM)."""
    if len(flux) < 4:
        return None
    f = flux - flux.mean()
    ac = np.correlate(f, f, mode="full")[len(f) - 1:]
    fps = sr / HOP
    lo = int(fps * 60.0 / 200.0)   # fastest 200 BPM
    hi = int(fps * 60.0 / 60.0)    # slowest 60 BPM
    if hi <= lo or hi >= len(ac):
        return None
    lag = lo + int(np.argmax(ac[lo:hi]))
    if lag <= 0:
        return None
    return round(60.0 * fps / lag, 1)


def _detect_drop(y: np.ndarray, sr: int = SR, search_max: float = 45.0) -> float:
    """The drop = the biggest sustained jump in short-time energy within the first
    `search_max` seconds. Phonk intros are quiet/sparse then SLAM — that jump is
    the moment to align the football→comparison cut to."""
    win = int(sr * 0.25)
    if win < 1 or len(y) < win * 2:
        return 0.0
    n = len(y) // win
    rms = np.sqrt(np.maximum(1e-9, np.array([
        np.mean(y[i * win:(i + 1) * win] ** 2) for i in range(n)
    ])))
    # smooth a touch
    k = 3
    kernel = np.ones(k) / k
    sm = np.convolve(rms, kernel, mode="same")
    t_per = win / float(sr)
    limit = min(n - 1, int(search_max / t_per))
    if limit < 2:
        return 0.0
    # derivative of smoothed energy; biggest rise = the drop
    d = np.diff(sm[:limit + 1])
    if len(d) == 0 or d.max() <= 0:
        return 0.0
    idx = int(np.argmax(d)) + 1
    return round(idx * t_per, 3)


def analyze(audio_path: str) -> dict:
    """Return {duration, bpm, beats, drop_time}. Best-effort; on any failure
    returns zeros so callers can fall back to manual timing."""
    out = {"duration": 0.0, "bpm": None, "beats": [], "drop_time": 0.0}
    try:
        y = _decode_mono(audio_path)
        out["duration"] = round(len(y) / float(SR), 3)
        flux, times = _onset_envelope(y)
        out["bpm"] = _estimate_bpm(flux)
        if find_peaks is not None and len(flux) > 4:
            thresh = float(flux.mean() + 0.6 * flux.std())
            # min beat spacing ~0.18s (≤ ~330 BPM) so we don't double-count
            distance = max(1, int((0.18 * SR) / HOP))
            peaks, _ = find_peaks(flux, height=thresh, distance=distance)
            out["beats"] = [round(float(times[p]), 3) for p in peaks]
        out["drop_time"] = _detect_drop(y)
        logger.info(
            f"beat_sync: dur={out['duration']}s bpm={out['bpm']} "
            f"beats={len(out['beats'])} drop={out['drop_time']}s"
        )
    except Exception as e:
        logger.warning(f"beat_sync.analyze failed ({e}); falling back to manual timing")
    return out


def nearest_beat(beats: List[float], t: float) -> float:
    """Snap time `t` to the nearest detected beat (returns t unchanged if none)."""
    if not beats:
        return t
    arr = np.asarray(beats, dtype=float)
    return float(arr[int(np.argmin(np.abs(arr - t)))])
