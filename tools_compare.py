#!/usr/bin/env python
"""Measure two shorts against each other on everything that was changed today.

usage: python tools_compare.py NEW.mp4 REFERENCE.mp4
env:   FFMPEG_BIN, ELAPSED (build seconds), BUILD_LOG (path to the build log)
"""
import json, os, re, subprocess, sys

FF = os.environ.get("FFMPEG_BIN") or "ffmpeg"
# Only rewrite the BINARY name, not the path. static_ffmpeg ships both binaries in
# the same package dir, so a blind replace() invented a static_ffprobe/ that is not there.
FP = os.environ.get("FFPROBE_BIN") or (
    os.path.join(os.path.dirname(FF), "ffprobe") if os.path.dirname(FF) else "ffprobe")
if not (os.path.dirname(FP) and os.path.exists(FP)):
    FP = "ffprobe"


def sh(cmd, t=180):
    return subprocess.run(cmd, capture_output=True, text=True, timeout=t)


def shb(cmd, t=180):
    """Binary variant -- frame grabs return PNG bytes, which text mode cannot decode."""
    return subprocess.run(cmd, capture_output=True, timeout=t)


def probe(p, entries, stream=None):
    c = [FP, "-v", "error"]
    if stream:
        c += ["-select_streams", stream]
    c += ["-show_entries", entries, "-of", "default=nw=1:nk=1", p]
    return sh(c).stdout.strip().splitlines()


def audio(p):
    d = float(probe(p, "format=duration")[0])
    j = sh([FF, "-hide_banner", "-nostats", "-i", p, "-af",
            "loudnorm=I=-14:TP=-1.5:print_format=json", "-f", "null", "-"], 240).stderr
    m = re.search(r"\{[^{}]*input_i[^{}]*\}", j, re.S)
    lufs = tp = float("nan")
    if m:
        o = json.loads(m.group(0)); lufs = float(o["input_i"]); tp = float(o["input_tp"])
    s = sh([FF, "-hide_banner", "-nostats", "-i", p, "-af",
            "silencedetect=noise=-45dB:d=0.20", "-f", "null", "-"], 240).stderr
    gaps = [float(x) for x in re.findall(r"silence_duration: ([\d.]+)", s)]
    starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", s)]
    def peak(a, b):
        r = sh([FF, "-hide_banner", "-nostats", "-ss", str(a), "-i", p, "-t", str(b),
                "-af", "volumedetect", "-f", "null", "-"], 120).stderr
        mm = re.search(r"max_volume: ([-\d.]+)", r)
        return float(mm.group(1)) if mm else float("nan")
    return dict(dur=d, lufs=lufs, tp=tp, dead=sum(gaps), deadpct=100*sum(gaps)/d,
                firstgap=(min(starts) if starts else None), ngaps=len(gaps),
                p0=peak(0, 0.4), pmid=peak(max(0, d/2 - 1), 2))


def frames(p, n=14):
    """Grab n evenly spaced frames, return per-frame brightness."""
    d = float(probe(p, "format=duration")[0])
    out = []
    for i in range(n):
        t = d * (i + 0.5) / n
        r = shb([FF, "-hide_banner", "-nostats", "-ss", f"{t:.2f}", "-i", p, "-frames:v", "1",
                 "-vf", "scale=120:-1", "-f", "image2pipe", "-vcodec", "png", "-"], 120)
        if r.returncode or not r.stdout:
            continue
        import io
        from PIL import Image
        import numpy as np
        im = Image.open(io.BytesIO(r.stdout)).convert("L")
        out.append(float(np.asarray(im, dtype="float32").mean()))
    return out


def scenecuts(p):
    r = sh([FF, "-hide_banner", "-nostats", "-i", p, "-vf",
            "select=gt(scene\\,0.25),showinfo", "-f", "null", "-"], 240).stderr
    return r.count("pts_time")


def row(label, a, b, fmt="{:.2f}", better=None):
    fa = fmt.format(a) if isinstance(a, (int, float)) else str(a)
    fb = fmt.format(b) if isinstance(b, (int, float)) else str(b)
    verdict = ""
    if better and isinstance(a, (int, float)) and isinstance(b, (int, float)):
        good = (a < b) if better == "low" else (a > b)
        verdict = "  BETTER" if good else ("  same" if abs(a - b) < 1e-9 else "  worse")
    print(f"  {label:<30}{fb:<18}{fa:<18}{verdict}")


new, ref = sys.argv[1], sys.argv[2]
an, ar = audio(new), audio(ref)
fn, fr = frames(new), frames(ref)
jump = lambda x: max(abs(x[i+1]-x[i]) for i in range(len(x)-1)) if len(x) > 1 else 0

print("=" * 78)
print(f"  {'METRIC':<30}{'REFERENCE (old)':<18}{'NEW':<18}")
print("=" * 78)
print("\n  AUDIO")
row("duration (s)", an["dur"], ar["dur"], "{:.2f}")
row("dead air (s)", an["dead"], ar["dead"], "{:.2f}", "low")
row("dead air (%)", an["deadpct"], ar["deadpct"], "{:.1f}", "low")
row("silent gaps", an["ngaps"], ar["ngaps"], "{:.0f}", "low")
row("first gap at (s)", an["firstgap"] or 0, ar["firstgap"] or 0, "{:.2f}", "high")
row("integrated LUFS", an["lufs"], ar["lufs"], "{:.2f}", "high")
row("true peak (dB)", an["tp"], ar["tp"], "{:.2f}", "high")
row("peak first 0.4s (dB)", an["p0"], ar["p0"], "{:.1f}", "high")
row("peak mid-clip (dB)", an["pmid"], ar["pmid"], "{:.1f}")
row("hook louder than body?", "YES" if an["p0"] > an["pmid"] else "no",
    "YES" if ar["p0"] > ar["pmid"] else "no")

print("\n  PICTURE")
row("brightness spread", max(fn)-min(fn), max(fr)-min(fr), "{:.0f}", "low")
row("largest adjacent jump", jump(fn), jump(fr), "{:.0f}", "low")
row("scene cuts", scenecuts(new), scenecuts(ref), "{:.0f}")
row("resolution", "x".join(probe(new, "stream=width,height", "v")),
    "x".join(probe(ref, "stream=width,height", "v")))

el = os.environ.get("ELAPSED")
lg = os.environ.get("BUILD_LOG", "")
print("\n  BUILD")
if el:
    print(f"  {'wall clock':<30}{'~18 min (EP12, from logs)':<18}{int(el)//60}m {int(el)%60}s")
if lg and os.path.exists(lg):
    t = open(lg, errors="ignore").read()
    for label, pat in [("parallel downloads", r"after wave of"),
                       ("subject reframe", r"reframe (saliency|face|centre)"),
                       ("chyron rejections", r"REJECTED.*burned-in"),
                       ("gap compression", r"gap compression: removed"),
                       ("shot matching", r"shot matching: \d+"),
                       ("audio mastering", r"audio mastered:"),
                       ("editorial gate", r"editorial gate:"),
                       ("J/L cuts", r"J/L cuts:"),
                       ("reuse cap relaxed", r"raising the per-clip reuse cap"),
                       ("BUILD FAILED", r"BUILD FAILED")]:
        n = len(re.findall(pat, t))
        print(f"  {label:<30}{'-':<18}{n} hit(s)")
print("=" * 78)
