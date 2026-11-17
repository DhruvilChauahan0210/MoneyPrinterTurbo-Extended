"""Build voice, timeline and audio mix for the 10-min Ronaldo retirement video.

Usage: .venv/bin/python make_ronaldo_retire.py [rate]      (rate like -3% / +4%, default +0%)
Outputs (all inside whatif-remotion/):
  public/ronaldo_retire/mix.mp3        voice + ducked music bed + sfx
  src/ronaldo_timeline.json            scenes with start/end seconds, ready for the Remotion composition
"""
import asyncio
import hashlib
import json
import os
import subprocess
import sys

import edge_tts

from ronaldo_retire_script import SCENES

ROOT = os.path.dirname(os.path.abspath(__file__))
W = os.path.join(ROOT, "whatif-remotion")
PUB = os.path.join(W, "public")
OUT = os.path.join(PUB, "ronaldo_retire")
CACHE = os.path.join("/tmp", "rr_voice")
os.makedirs(OUT, exist_ok=True)
os.makedirs(CACHE, exist_ok=True)
VOICE = "en-US-EricNeural"
RATE = sys.argv[1] if len(sys.argv) > 1 else "+0%"
FF = os.path.join(ROOT, ".venv", "bin", "ffmpeg")
FP = os.path.join(ROOT, ".venv", "bin", "ffprobe")


def dur(p):
    return float(subprocess.run([FP, "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p],
                                capture_output=True, text=True).stdout.strip())


async def tts_all():
    sem = asyncio.Semaphore(5)

    async def one(i, s):
        key = hashlib.md5(f"{VOICE}|{RATE}|{s['text']}".encode()).hexdigest()[:12]
        mp3 = os.path.join(CACHE, key + ".mp3")
        wav = os.path.join(CACHE, key + ".wav")
        if not os.path.exists(wav):
            async with sem:
                for attempt in range(4):
                    try:
                        await edge_tts.Communicate(s["text"], VOICE, rate=RATE).save(mp3)
                        break
                    except Exception as e:  # network hiccup
                        if attempt == 3:
                            raise
                        await asyncio.sleep(2 + attempt * 2)
            subprocess.run([FF, "-v", "error", "-y", "-i", mp3, "-ar", "44100", "-ac", "1", wav], check=True)
        s["wav"] = wav
        s["vd"] = dur(wav)

    await asyncio.gather(*[one(i, s) for i, s in enumerate(SCENES)])


asyncio.run(tts_all())

# ---- timeline ----
t = 0.25
TL = []
for i, s in enumerate(SCENES):
    ch = "ch" in s
    lead = 0.55 if ch else 0.08
    tail = 0.9 if ch else 0.3
    d = s["vd"]
    if ch:
        sd = max(2.7, lead + d + tail)
    else:
        sd = max(2.2, lead + d + tail)
    item = {k: v for k, v in s.items() if k not in ("wav", "vd")}
    item.update({"i": i, "start": round(t, 3), "end": round(t + sd, 3), "voice_at": round(t + lead, 3), "vd": round(d, 3)})
    TL.append(item)
    t += sd
TOTAL = round(t + 3.0, 3)  # outro tail
json.dump({"total": TOTAL, "scenes": TL}, open(os.path.join(W, "src", "ronaldo_timeline.json"), "w"), ensure_ascii=False, indent=1)
print(f"scenes={len(TL)} total={TOTAL:.1f}s = {TOTAL/60:.2f} min  (rate {RATE})")

# ---- audio ----
# 1) voice track
ins, filt, labs = [], [], []
for k, s in enumerate(TL):
    ins += ["-i", SCENES[k]["wav"]]
    ms = int(s["voice_at"] * 1000)
    filt.append(f"[{k}:a]adelay={ms}|{ms},volume=1.25[v{k}]")
    labs.append(f"[v{k}]")
filt.append("".join(labs) + f"amix=inputs={len(labs)}:normalize=0:dropout_transition=0,apad=whole_dur={TOTAL}[voice]")
subprocess.run([FF, "-v", "error", "-y", *ins, "-filter_complex", ";".join(filt), "-map", "[voice]", "-t", str(TOTAL),
                "-ar", "44100", "-ac", "2", "/tmp/rr_voice_track.wav"], check=True)

# 2) music bed: 4 tracks crossfaded
tracks = ["music3.mp3", "music4.mp3", "music5.mp3", "music2.mp3"]
args, cf = [], []
for tk in tracks:
    args += ["-i", os.path.join(PUB, tk)]
cur = "[0:a]"
for k in range(1, len(tracks)):
    cf.append(f"{cur}[{k}:a]acrossfade=d=4:c1=tri:c2=tri[m{k}]")
    cur = f"[m{k}]"
subprocess.run([FF, "-v", "error", "-y", *args, "-filter_complex", ";".join(cf), "-map", cur, "-t", str(TOTAL), "-ar", "44100", "-ac", "2",
                "/tmp/rr_music.wav"], check=True)

# 3) sfx track
SFX = {n: os.path.join(PUB, f"sfx_{n}.wav") for n in ("whoosh", "impact", "riser", "sparkle", "crash", "thud", "swish")}
sins, sfilt, slabs = [], [], []
n = 0
for s in TL:
    name = s.get("sfx")
    if not name:
        continue
    # also whoosh on every flash overlay
    at = s["start"] - (1.2 if name == "riser" else 0.0)
    ms = max(0, int(at * 1000))
    sins += ["-i", SFX[name]]
    vol = {"whoosh": 0.55, "impact": 0.85, "riser": 0.5, "sparkle": 0.5}.get(name, 0.6)
    sfilt.append(f"[{n}:a]adelay={ms}|{ms},volume={vol}[s{n}]")
    slabs.append(f"[s{n}]")
    n += 1
sfilt.append("".join(slabs) + f"amix=inputs={n}:normalize=0,apad=whole_dur={TOTAL}[sfx]")
subprocess.run([FF, "-v", "error", "-y", *sins, "-filter_complex", ";".join(sfilt), "-map", "[sfx]", "-t", str(TOTAL), "-ar", "44100", "-ac", "2",
                "/tmp/rr_sfx.wav"], check=True)

# 4) mix with sidechain ducking + loudness
mix = (
    "[1:a]volume=0.30[mus];"
    "[0:a]asplit=2[vo][vsc];"
    "[mus][vsc]sidechaincompress=threshold=0.015:ratio=10:attack=15:release=450:makeup=1[duck];"
    "[vo][duck][2:a]amix=inputs=3:normalize=0,loudnorm=I=-15:TP=-1.5:LRA=11[out]"
)
subprocess.run([FF, "-v", "error", "-y", "-i", "/tmp/rr_voice_track.wav", "-i", "/tmp/rr_music.wav", "-i", "/tmp/rr_sfx.wav",
                "-filter_complex", mix,
                "-map", "[out]", "-t", str(TOTAL), "-b:a", "192k", os.path.join(OUT, "mix.mp3")], check=True)
print("mix ->", os.path.join(OUT, "mix.mp3"), round(dur(os.path.join(OUT, "mix.mp3")), 1), "s")
