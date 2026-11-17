#!/usr/bin/env python3
"""NewsCut music bed: an original dramatic string bed, synthesised here (no samples, nothing downloaded).

Usage (repo root):  .venv/bin/python nc_bed.py [out.wav] [--seconds=36.23] [--pad-db=0] [--boom-db=0] [--build-db=6.5]
                    [--fc=4800] [--seed=7]
Default out: whatif-remotion/public/nc_bed_em106.wav (48 kHz stereo).

Profile (measured from the reference format's music): 106 BPM, a 2-bar loop of 4.528 s, E minor, a deep E2 hit on
beat 1 of every loop (about 1.4 s decay), sustained string chords (Em | G D, Em | C D), B bass for most of loop 6,
sustained high E + B that enters half-way and builds about 6 dB, long reverb, no drums.
Mix level that matched the reference (music about 28 dB under the voice, 22 dB after the build): "musicVol": 0.012,
"duck": 1, "musicFadeIn": 0.01 in the NewsCut spec. The default length is 8 loops, so the file repeats on the beat.
"""
import os
import sys

import numpy as np
import soundfile as sf
from scipy import signal

SR = 48000
BPM = 106.0
BEAT = 60.0 / BPM
LOOP = 8 * BEAT
ROOT = os.path.dirname(os.path.abspath(__file__))
NOTE = {"C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5, "F#": 6, "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11}
CH = {
    "Em": ["E3", "B3", "E4", "G4", "B4"],
    "G": ["G3", "D4", "G4", "B4", "D5"],
    "D": ["D3", "A3", "D4", "F#4", "A4"],
    "C": ["C3", "G3", "C4", "E4", "G4"],
    "Bsus": ["B2", "F#3", "B3", "E4", "F#4"],
    "B": ["B2", "F#3", "B3", "D#4", "F#4"],
}
# one row per 8-beat loop: (chord, beats). Row 5 is the B loop (the boom drops to B1 there).
LOOPS = [
    [("Em", 8)],
    [("Em", 4), ("G", 2), ("D", 2)],
    [("Em", 4), ("C", 2), ("D", 2)],
    [("Em", 4), ("G", 2), ("D", 2)],
    [("Em", 4), ("C", 2), ("D", 2)],
    [("Bsus", 2), ("B", 4), ("Em", 2)],
    [("Em", 4), ("G", 2), ("D", 2)],
    [("Em", 4), ("C", 2), ("D", 2)],
]
HIGH = {"Em": ["E5", "B5"], "G": ["D5", "B5"], "D": ["D5", "A5"], "C": ["E5", "G5"], "Bsus": ["F#5", "B5"], "B": ["F#5", "B5"]}


def hz(name):
    return 440.0 * 2 ** ((NOTE[name[:-1]] + 12 * (int(name[-1]) + 1) - 69) / 12)


def strings(f0, dur, fc, rng, voices=4, vib=1.0, rel=0.7):
    """A small string section on one note: detuned band-limited saws with slow vibrato. Returns (n, 2)."""
    n = int((dur + rel) * SR)
    t = np.arange(n) / SR
    out = np.zeros((n, 2))
    ks = np.arange(1, max(1, int(min(44, 9000 / f0))) + 1)
    amp = (1.0 / ks) / np.sqrt(1 + (ks * f0 / fc) ** 4)
    for _ in range(voices):
        von = np.clip((t - 0.2) / 0.7, 0, 1)
        cents = rng.uniform(-10, 10) + rng.uniform(3, 7) * vib * von * np.sin(2 * np.pi * rng.uniform(4.6, 5.9) * t + rng.uniform(0, 6.28))
        ph = 2 * np.pi * np.cumsum(f0 * 2 ** (cents / 1200)) / SR
        sig = np.zeros(n)
        for k, a in zip(ks, amp):
            sig += a * np.sin(k * ph + rng.uniform(0, 6.28))
        sig *= 1 + 0.12 * np.sin(2 * np.pi * rng.uniform(0.15, 0.5) * t + rng.uniform(0, 6.28))
        pan = rng.uniform(0.25, 0.75)
        out[:, 0] += sig * np.cos(pan * np.pi / 2)
        out[:, 1] += sig * np.sin(pan * np.pi / 2)
    env = np.ones(n)
    na, nr = int(min(0.35, dur * 0.4) * SR), int(rel * SR)
    env[:na] = 0.5 - 0.5 * np.cos(np.pi * np.arange(na) / na)
    env[-nr:] = 0.5 + 0.5 * np.cos(np.pi * np.arange(nr) / nr)
    return out * env[:, None] / voices


def boom(f0, rng):
    """Deep hit: a sine that drops into f0 and rings ~1.4 s, a few harmonics so phones play it, and a short thump."""
    n = int(2.4 * SR)
    t = np.arange(n) / SR
    ph = 2 * np.pi * np.cumsum(f0 * (1 + 1.3 * np.exp(-t / 0.016))) / SR
    s = np.sin(ph) * np.exp(-t / 0.48)
    s += 0.40 * np.sin(2 * ph) * np.exp(-t / 0.34) + 0.18 * np.sin(3 * ph) * np.exp(-t / 0.24) + 0.08 * np.sin(4 * ph) * np.exp(-t / 0.18)
    noise = rng.standard_normal(n)
    s += 0.55 * signal.sosfilt(signal.butter(2, 170, fs=SR, output="sos"), noise) * np.exp(-t / 0.05)
    s += 0.10 * signal.sosfilt(signal.butter(2, [250, 1400], btype="band", fs=SR, output="sos"), noise) * np.exp(-t / 0.11)
    s *= 1 - np.exp(-t / 0.002)
    s[-2400:] *= np.linspace(1, 0, 2400)
    return np.stack([s, s], axis=1)


def reverb_ir(rng, rt60=2.6, length=3.2):
    n = int(length * SR)
    t = np.arange(n) / SR
    ir = rng.standard_normal((n, 2)) * np.exp(-6.908 * t / rt60)[:, None]
    ir = signal.sosfilt(signal.butter(2, [250, 4500], btype="band", fs=SR, output="sos"), ir, axis=0)
    ir[: int(0.012 * SR)] = 0
    return ir / np.sqrt((ir ** 2).sum(axis=0))


def add(buf, at, x):
    i = int(round(at * SR))
    if i >= len(buf):
        return
    x = x[: len(buf) - i]
    buf[i:i + len(x)] += x


def db(x):
    return 10 ** (x / 20)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    opt = dict(a[2:].split("=", 1) for a in sys.argv[1:] if a.startswith("--") and "=" in a)
    out = args[0] if args else os.path.join(ROOT, "whatif-remotion/public/nc_bed_em106.wav")
    seconds = float(opt.get("seconds", 8 * LOOP))
    fc0 = float(opt.get("fc", 4800))
    build_db = float(opt.get("build-db", 6.5))
    rng = np.random.default_rng(int(opt.get("seed", 7)))
    n = int(seconds * SR)
    nloops = int(np.ceil(seconds / LOOP - 1e-6))
    b0, b1 = 0.38 * seconds, 0.62 * seconds                 # build window
    hi_loop = int(round(0.5 * seconds / LOOP))              # the loop where the high line enters

    pad, high, hit = np.zeros((n, 2)), np.zeros((n, 2)), np.zeros((n, 2))
    for li in range(nloops):
        row = LOOPS[li % len(LOOPS)]
        t0, beat = li * LOOP, 0
        add(hit, t0, boom(hz("B1") if row[0][0] == "Bsus" else hz("E2"), rng))
        for chord, beats in row:
            at, dur = t0 + beat * BEAT, beats * BEAT
            fc = fc0 * (1 + 0.3 * np.clip((at - b0) / (b1 - b0), 0, 1))
            for i, name in enumerate(CH[chord]):
                add(pad, at, strings(hz(name), dur, fc, rng) * (1.0 if i < 2 else 0.8))
            if li >= hi_loop:
                for name in HIGH[chord]:
                    add(high, at, strings(hz(name), dur, fc * 1.5, rng, voices=3, vib=1.2) * 0.5)
                if li >= hi_loop + 2 and chord == "Em":
                    add(high, at, strings(hz("E6"), dur, fc * 1.5, rng, voices=3, vib=1.2) * 0.3)
            beat += beats

    t = np.arange(n) / SR
    high *= np.clip((t - hi_loop * LOOP) / 4.0, 0, 1)[:, None]          # the high line fades in over 4 s
    mus = (pad + high) * db(build_db * np.clip((t - b0) / (b1 - b0), 0, 1))[:, None]
    mus = signal.sosfilt(signal.butter(2, 110, btype="high", fs=SR, output="sos"), mus, axis=0)
    ir = reverb_ir(rng)
    wet = np.stack([signal.fftconvolve(mus[:, c], ir[:, c])[:n] for c in (0, 1)], axis=1)
    mus = mus + 0.55 * wet
    hit_wet = np.stack([signal.fftconvolve(hit[:, c], ir[:, c])[:n] for c in (0, 1)], axis=1)
    hit = hit + 0.12 * hit_wet

    half = int(min(n, b0 * SR))
    mus *= db(-24 + float(opt.get("pad-db", 0))) / np.sqrt((mus[:half] ** 2).mean())   # strings: -24 dBFS RMS before the build
    hit *= db(-4.5 + float(opt.get("boom-db", 0))) / np.abs(hit).max()                  # hit: -4.5 dBFS peak
    bed = mus + hit
    peak = np.abs(bed).max()
    if peak > db(-1):
        bed *= db(-1) / peak
    sf.write(out, bed.astype(np.float32), SR, subtype="PCM_24")
    print(f"bed: {out}  {seconds:.2f}s  {nloops} loops  peak {20 * np.log10(np.abs(bed).max()):.1f} dBFS  "
          f"rms {10 * np.log10((bed ** 2).mean()):.1f} dBFS")


if __name__ == "__main__":
    main()
