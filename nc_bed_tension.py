#!/usr/bin/env python3
"""NewsCut "tension" bed: a dark E minor underscore with a ticking ostinato, synthesised here (no samples, nothing
downloaded). Built 20 Nov 2026 to the measured profile of the beds CD pointed at (@ballstory90), copying the
character, not any track.

Usage (repo root):  python nc_bed_tension.py [out.wav] [--seconds=42.67] [--bpm=90] [--fc=1800] [--tick-db=0]
                    [--thump-db=0] [--seed=11]
Default out: whatif-remotion/public/nc_bed_tension.wav (48 kHz stereo, 24-bit).

Target profile (measured on 7 of 10 of their Shorts, same track each time):
  - E minor; a steady E2 drone (~81 Hz) under everything, chord roots in the bass;
  - chords change every 2 beats: Em Bm Am C | D Bm Em Em | Em Bm Am D | Em G F# Em (16 chords, then repeats);
  - a ticking eighth-note ostinato (~0.33 s at 90 BPM) on chord tones: the "busy, tense" feel;
  - a soft low thump on each chord change (~every 1.33 s);
  - dark: most energy 250 Hz-1 kHz, little above 1 kHz (low-pass ~1.8 kHz), no bright string shimmer;
  - flat level, no build; in the mix about 20 dB under the voice with no ducking.
Mix: in a NewsCut spec use "music": "nc_bed_tension.wav", "duck": 1, "musicFadeIn": 0.01, "musicFadeOut": 0 and
"musicVol": 0.095 for the reference level (music ~20 dB RMS under the voice) or 0.053 for ~25 dB. Measured 20 Nov 2026
on the Haaland spec from the mix ingredients: the old nc_bed_em106 at 0.012 sat ~36 dB under the voice, far quieter
than the reference. The bed is normalised to nc_bed_em106's pre-build RMS, so these numbers compare directly.
The default length is two passes of the 16-chord cycle, so the file loops on a bar line.
"""
import os
import sys

import numpy as np
import soundfile as sf
from scipy import signal

from nc_bed import SR, add, boom, db, hz, reverb_ir, strings

ROOT = os.path.dirname(os.path.abspath(__file__))
CH = {
    "Em": ["E3", "B3", "E4", "G4"],
    "Bm": ["D3", "F#3", "B3", "D4"],
    "Am": ["E3", "A3", "C4", "E4"],
    "C": ["E3", "G3", "C4", "E4"],
    "D": ["D3", "F#3", "A3", "D4"],
    "G": ["D3", "G3", "B3", "D4"],
    "F#": ["F#3", "A#3", "C#4", "F#4"],
}
ROOTS = {"Em": "E2", "Bm": "B1", "Am": "A1", "C": "C2", "D": "D2", "G": "G1", "F#": "F#1"}
PROG = ["Em", "Bm", "Am", "C", "D", "Bm", "Em", "Em", "Em", "Bm", "Am", "D", "Em", "G", "F#", "Em"]
TICK = [0, 2, 1, 2]  # chord-tone index per eighth note (low, high, mid, high)


def pluck(f0, rng, dur=0.30, fc=1600):
    """A short bowed/plucked string note for the ostinato: band-limited saw, 6 ms attack, ~0.18 s decay."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    ks = np.arange(1, max(1, int(min(30, 6000 / f0))) + 1)
    amp = (1.0 / ks) / np.sqrt(1 + (ks * f0 / fc) ** 4)
    ph = 2 * np.pi * f0 * 2 ** (rng.uniform(-6, 6) / 1200) * t
    s = sum(a * np.sin(k * ph + rng.uniform(0, 6.28)) for k, a in zip(ks, amp))
    s *= (1 - np.exp(-t / 0.006)) * np.exp(-t / 0.18)
    s[-int(0.02 * SR):] *= np.linspace(1, 0, int(0.02 * SR))
    pan = rng.uniform(0.35, 0.65)
    return np.stack([s * np.cos(pan * np.pi / 2), s * np.sin(pan * np.pi / 2)], axis=1)


def thump(f0, rng):
    """Soft low hit: the nc_bed boom, shortened to ~0.5 s so it pulses instead of booming."""
    b = boom(f0, rng)
    t = np.arange(len(b)) / SR
    return b * np.exp(-t / 0.35)[:, None]


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    opt = dict(a[2:].split("=", 1) for a in sys.argv[1:] if a.startswith("--") and "=" in a)
    out = args[0] if args else os.path.join(ROOT, "whatif-remotion/public/nc_bed_tension.wav")
    bpm = float(opt.get("bpm", 90))
    beat = 60.0 / bpm
    chord_len = 2 * beat
    seconds = float(opt.get("seconds", 2 * len(PROG) * chord_len))
    fc = float(opt.get("fc", 1800))
    rng = np.random.default_rng(int(opt.get("seed", 11)))
    n = int(seconds * SR)
    nch = int(np.ceil(seconds / chord_len - 1e-6))

    pad, bass, tick, hit = (np.zeros((n, 2)) for _ in range(4))
    # E2 drone (+ B2 fifth) under the whole bed
    add(bass, 0, strings(hz("E2"), seconds, 500, rng, voices=4, vib=0.4, rel=0.01) * 0.9)
    add(bass, 0, strings(hz("B2"), seconds, 600, rng, voices=3, vib=0.4, rel=0.01) * 0.35)
    for ci in range(nch):
        ch = PROG[ci % len(PROG)]
        at = ci * chord_len
        for i, name in enumerate(CH[ch]):
            f0 = hz(name) * (1 if i == 0 else 2)   # root low, the rest an octave up: warm low-mids, not bass
            add(pad, at, strings(f0, chord_len, fc, rng, voices=4, vib=0.8, rel=0.5) * (1.0 if i < 2 else 0.7))
        add(bass, at, strings(hz(ROOTS[ch]), chord_len, 400, rng, voices=3, vib=0.3, rel=0.4) * 0.6)
        add(hit, at, thump(hz("E1") if ch == "Em" else hz(ROOTS[ch]), rng))
        notes = CH[ch]
        for e in range(4):  # 4 eighth notes per chord (2 beats)
            vel = 1.0 if e % 2 == 0 else 0.72
            add(tick, at + e * beat / 2, pluck(hz(notes[TICK[e]]) * 2, rng, fc=fc * 1.3) * vel)

    t = np.arange(n) / SR
    mus = pad + 1.1 * tick
    mus = signal.sosfilt(signal.butter(2, fc, btype="low", fs=SR, output="sos"), mus, axis=0)   # dark top
    mus = signal.sosfilt(signal.butter(2, 150, btype="high", fs=SR, output="sos"), mus, axis=0)
    ir = reverb_ir(rng, rt60=2.2, length=2.8)
    wet = np.stack([signal.fftconvolve(mus[:, c], ir[:, c])[:n] for c in (0, 1)], axis=1)
    mus = mus + 0.45 * wet
    bass = signal.sosfilt(signal.butter(2, 300, btype="low", fs=SR, output="sos"), bass, axis=0)

    mus *= db(-25 + float(opt.get("tick-db", 0))) / np.sqrt((mus ** 2).mean())
    bass *= db(-35) / np.sqrt((bass ** 2).mean())
    hit *= db(-18 + float(opt.get("thump-db", 0))) / np.abs(hit).max()
    bed = mus + bass + hit
    # same RMS as nc_bed_em106 before its build, so musicVol settings compare directly
    ref = os.path.join(ROOT, "whatif-remotion/public/nc_bed_em106.wav")
    if os.path.exists(ref):
        r, rsr = sf.read(ref)
        rr = np.sqrt((r[: int(0.38 * len(r))] ** 2).mean())
        bed *= rr / np.sqrt((bed ** 2).mean())
    fade = int(0.01 * SR)
    bed[:fade] *= np.linspace(0, 1, fade)[:, None]
    peak = np.abs(bed).max()
    if peak > db(-1):
        bed *= db(-1) / peak
    sf.write(out, bed.astype(np.float32), SR, subtype="PCM_24")
    print(f"bed: {out}  {seconds:.2f}s  {nch} chords at {bpm:g} BPM  peak {20 * np.log10(np.abs(bed).max()):.1f} dBFS  "
          f"rms {10 * np.log10((bed ** 2).mean()):.1f} dBFS")


if __name__ == "__main__":
    main()
