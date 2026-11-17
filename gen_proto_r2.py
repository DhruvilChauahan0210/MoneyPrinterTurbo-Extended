#!/usr/bin/env python3
"""R2 prototype builder: ORIGINAL-graphics Shorts (Duel 'PICK ONE' and 'WHO IS IT?') from a JSON spec.

Usage (repo root):  .venv/bin/python gen_proto_r2.py prototypes/r2/duel_dembele_yamal.json
                    .venv/bin/python gen_proto_r2.py prototypes/r2/whoisit_haaland.json [--no-render]

Spec "mode": "duel" | "whoisit". See prototypes/r2/*.json for the full schema by example. Steps:
 1. crop each photo (box in source pixels) -> whatif-remotion/public/proto_r2_<key>_<name>.jpg
 2. edge-tts one clip per segment (voice en-US-GuyNeural), laid out on a timeline (gap 0.25 s, optional minStart)
 3. mix: voice + music bed (sidechain-ducked under the voice) + tick/whoosh/impact sfx, loudnorm to about -11 LUFS
 4. write props, render with the Remotion composition (Duel / WhoIsIt), copy to ~/Desktop/<out>
No upload, no Studio. Every image-search step is done beforehand (see README in the spec comment / the final report).
"""
import json
import os
import random
import shutil
import subprocess
import sys

from PIL import Image

ROOT = os.path.dirname(os.path.abspath(__file__))
REMO = os.path.join(ROOT, "whatif-remotion")
PUB = os.path.join(REMO, "public")
FF = os.path.join(ROOT, ".venv/bin/ffmpeg")
FP = os.path.join(ROOT, ".venv/bin/ffprobe")
EDGE = os.path.join(ROOT, ".venv/bin/edge-tts")
OUTDIR = os.path.join(ROOT, "prototypes/r2/out")
GAP = 0.15
TAIL = 1.2


def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode != 0:
        raise SystemExit(f"FAILED: {' '.join(cmd)[:200]}\n{r.stderr[-1500:]}")
    return r


def dur(path):
    return float(run([FP, "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path]).stdout.strip())


def crop_photo(key, name, spec):
    """spec: {"src": path, "box": [x0,y0,x1,y1] (source px)}. Returns the public filename."""
    im = Image.open(os.path.join(ROOT, spec["src"])).convert("RGB")
    if spec.get("box"):
        im = im.crop(tuple(spec["box"]))
    out = f"proto_r2_{key}_{name}.jpg"
    im.save(os.path.join(PUB, out), quality=92)
    return out


def fetch_clips(key, tag, items):
    """items: [{"url", "start", "len"?}] -> public filenames of 1080x1920 cover clips (cached)."""
    from app.services import auto_footage
    auto_footage._REJECT_BURNED_IN_TEXT = False
    outs = []
    for i, it in enumerate(items or []):
        name = f"proto_r2_{key}_{tag}{i}.mp4"
        dst = os.path.join(PUB, name)
        if not (os.path.exists(dst) and os.path.getsize(dst) > 10000):
            st = float(it["start"])
            got = auto_footage.fetch_exact_clip(it["url"], st, st + float(it.get("len", 7.0)), 1080, 1920, dst,
                                                max_height=1080, max_filesize_mb=600, fill="cover", retries=2)
            if not got:
                raise SystemExit(f"clip failed: {it}")
        outs.append(name)
    return outs


def tts(text, path_wav, voice, rate):
    mp3 = path_wav.replace(".wav", ".mp3")
    run([EDGE, "--voice", voice, "--rate", rate, "--text", text, "--write-media", mp3])
    # edge-tts leaves ~0.9 s pauses after every sentence: squeeze any silence longer than 0.3 s down to 0.18 s
    run([FF, "-v", "error", "-y", "-i", mp3, "-af",
         "silenceremove=start_periods=1:start_threshold=-45dB:stop_periods=-1:stop_duration=0.3:stop_threshold=-45dB:stop_silence=0.18",
         "-ar", "48000", "-ac", "2", path_wav])
    os.remove(mp3)


def make_tick(path):
    if not os.path.exists(path):
        run([FF, "-v", "error", "-y", "-f", "lavfi", "-i", "sine=f=1700:d=0.06", "-af",
             "afade=t=out:st=0.01:d=0.05,volume=0.9,aformat=sample_rates=48000:channel_layouts=stereo", path])


def layout(segments, work, voice, rate):
    """Generate TTS per segment and place on a timeline. Returns list of (start, end, wav)."""
    placed, t = [], 0.0
    for i, s in enumerate(segments):
        w = os.path.join(work, f"seg{i}.wav")
        tts(s.get("tts") or s["text"], w, voice, rate)
        d = dur(w)
        st = max(t, s.get("minStart", 0.0)) if i else 0.0
        placed.append((st, st + d, w))
        t = st + d + GAP
    return placed


def mix_audio(placed, total, sfx, music_file, music_vol, out_wav):
    """sfx: list of (time, file, volume). Voice drives a sidechain compressor on the music, then loudnorm."""
    inputs, filt = [], []
    n = 0
    for st, _, w in placed:
        inputs += ["-i", w]
        filt.append(f"[{n}:a]adelay={int(st*1000)}|{int(st*1000)},apad=whole_dur={total:.3f}[v{n}]")
        n += 1
    nv = n
    inputs += ["-stream_loop", "-1", "-i", music_file]
    music_idx = n
    n += 1
    sfx_labels = []
    for k, (tm, f, vol) in enumerate(sfx):
        inputs += ["-i", f]
        filt.append(f"[{n}:a]volume={vol},adelay={int(tm*1000)}|{int(tm*1000)},apad=whole_dur={total:.3f}[x{k}]")
        sfx_labels.append(f"[x{k}]")
        n += 1
    vlabels = "".join(f"[v{i}]" for i in range(nv))
    filt.append(f"{vlabels}amix=inputs={nv}:normalize=0,atrim=0:{total:.3f}[voice]")
    filt.append("[voice]asplit=2[voice_a][voice_sc]")
    filt.append(f"[{music_idx}:a]atrim=0:{total:.3f},volume={music_vol},afade=t=in:d=0.4,afade=t=out:st={total-1.2:.3f}:d=1.2[mus]")
    filt.append("[mus][voice_sc]sidechaincompress=threshold=0.03:ratio=8:attack=15:release=350:makeup=1[musduck]")
    parts = ["[voice_a]", "[musduck]"] + sfx_labels
    filt.append(f"{''.join(parts)}amix=inputs={len(parts)}:normalize=0:dropout_transition=0,"
                f"loudnorm=I=-11:TP=-1.2:LRA=9,aresample=48000[out]")
    run([FF, "-v", "error", "-y", *inputs, "-filter_complex", ";".join(filt), "-map", "[out]", "-ac", "2", "-ar", "48000", out_wav])


def measure_lufs(path):
    r = subprocess.run([FF, "-hide_banner", "-nostats", "-i", path, "-af", "ebur128=peak=true", "-f", "null", "-"],
                       capture_output=True, text=True)
    lines = [l for l in r.stderr.splitlines() if "I:" in l or "Peak:" in l]
    return " | ".join(l.strip() for l in lines[-2:])


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    spec = json.load(open(args[0]))
    no_render = "--no-render" in sys.argv
    key, mode = spec["key"], spec["mode"]
    os.makedirs(OUTDIR, exist_ok=True)
    work = os.path.join(OUTDIR, key)
    os.makedirs(work, exist_ok=True)
    voice = spec.get("voice", "en-US-GuyNeural")
    rate = spec.get("rate", "+5%")

    photos = {n: crop_photo(key, n, s) for n, s in spec["photos"].items()}
    placed = layout(spec["segments"], work, voice, rate)
    starts = {s["id"]: placed[i][0] for i, s in enumerate(spec["segments"])}
    total = round(placed[-1][1] + spec.get("tail", TAIL), 2)
    total = max(total, spec.get("minDuration", 0))

    tick = os.path.join(ROOT, "prototypes/r2/sfx_tick.wav")
    make_tick(tick)
    sfxs = []
    if mode == "duel":
        cd = spec["countdownSeconds"]
        for k in range(cd):
            sfxs.append((float(k), tick, 0.55))
        for i in range(len(spec["rows"])):
            sfxs.append((starts[f"row{i}"], os.path.join(PUB, "sfx_swish.wav"), 0.5))
        sfxs.append((starts["reveal"], os.path.join(PUB, "sfx_impact.wav"), 0.8))
    else:
        for i in range(3):
            sfxs.append((starts[f"clue{i}"], os.path.join(PUB, "sfx_swish.wav"), 0.5))
        for k in range(int(starts["reveal"])):
            sfxs.append((float(k), tick, 0.3))
        sfxs.append((starts["reveal"], os.path.join(PUB, "sfx_impact.wav"), 0.8))
        sfxs.append((starts["reveal"] + 0.1, os.path.join(PUB, "sfx_sparkle.wav"), 0.4))
    music = os.path.join(PUB, spec.get("music", "music2.mp3"))
    mix_name = f"proto_r2_{key}_mix.wav"
    mix_audio(placed, total, sfxs, music, spec.get("musicVolume", 0.22), os.path.join(PUB, mix_name))

    if mode == "duel":
        props = dict(
            headline=spec["headline"], countdownSeconds=spec["countdownSeconds"],
            left={**spec["left"], "photo": photos["left"], "clips": fetch_clips(key, "L", spec.get("leftClips"))},
            right={**spec["right"], "photo": photos["right"], "clips": fetch_clips(key, "R", spec.get("rightClips"))},
            rows=spec["rows"], rowStarts=[round(starts[f"row{i}"], 2) for i in range(len(spec["rows"]))],
            revealAt=round(starts["reveal"], 2), reveal=spec["reveal"], source=spec["source"],
            audioFile=mix_name, durationInSeconds=total)
        comp = "Duel"
    else:
        props = dict(
            headline=spec["headline"], photo=photos["photo"], clips=fetch_clips(key, "C", spec.get("clips")),
            posX=spec.get("posX", 50), posY=spec.get("posY", 25),
            zoom=spec.get("zoom", 1.0), shiftY=spec.get("shiftY", 0),
            clues=spec["clues"], clueStarts=[round(starts[f"clue{i}"], 2) for i in range(3)],
            revealAt=round(starts["reveal"], 2), name=spec["name"], fact=spec["fact"], source=spec["source"],
            audioFile=mix_name, durationInSeconds=total)
        comp = "WhoIsIt"
    pj = os.path.join(OUTDIR, f"{key}.props.json")
    json.dump(props, open(pj, "w"), indent=1, ensure_ascii=False)
    print("timeline:", {k: round(v, 2) for k, v in starts.items()}, "total", total)
    print("props:", pj)
    if no_render:
        return
    out_mp4 = os.path.join(REMO, "out", f"{spec['out']}.mp4")
    port = 3400 + random.randint(0, 499)
    subprocess.run(["npx", "remotion", "render", "src/index.ts", comp, out_mp4, f"--props={pj}", "--log=error",
                    f"--port={port}"], cwd=REMO, check=True)
    dest = os.path.expanduser(f"~/Desktop/{spec['out']}.mp4")
    shutil.copy(out_mp4, dest)
    print("DONE", dest, f"{dur(dest):.2f}s", measure_lufs(dest))


if __name__ == "__main__":
    main()
