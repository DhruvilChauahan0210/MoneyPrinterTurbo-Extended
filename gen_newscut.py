#!/usr/bin/env python3
"""NewsCut builder: fast-cut news Short (BallBlitz-style) from a JSON spec.

Usage (repo root):  .venv/bin/python gen_newscut.py prototypes/newscut/<spec>.json [--tts-only] [--no-render] [--audio-only]

Format: ~95-word script, one fast voice, a hard cut every ~1.4 s on a word boundary, every shot a moving clip that
matches the words, 1-3 word ALL-CAPS captions dead centre alternating white / yellow, small channel watermark top
right, source cards, a 2-frame cover image at the very end, and a last sentence that stops mid-way so the Short loops
into its own first line.

Spec: see prototypes/newscut/*.json. "sentences" is a list of sentences, each a list of [display, spoken] chunks.
"loopTail" is the spoken text that completes the last sentence for natural intonation and is cut off in the audio.
Music: "music" (file in public/; nc_bed.py makes the string bed), "musicVol", "duck" (sidechain ratio, 1 = off),
"musicFadeIn" / "musicFadeOut" (s; 0 = the bed runs to the last frame so the loop back to the start is seamless). --audio-only re-mixes and puts the new audio on the existing render (video copied) as <out>_v2.
"shots": [{"at": chunk index, "vid": YouTube id, "start": sec, "x"?: crop x in source px, "fill"?: "contain"} |
          {"at": chunk index, "gfx": "crash"}], sorted by "at". Each shot runs until the next one starts.
Steps: edge-tts per sentence with word boundaries -> chunk times -> cut clips (fetch_exact_clip) -> mix -> props ->
one Remotion render (composition NewsCut) -> ~/Desktop/<out>. No upload.
"""
import asyncio
import json
import os
import random
import re
import shutil
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.abspath(__file__))
REMO = os.path.join(ROOT, "whatif-remotion")
PUB = os.path.join(REMO, "public")
FF = os.path.join(ROOT, ".venv/bin/ffmpeg")
FP = os.path.join(ROOT, ".venv/bin/ffprobe")
OUTDIR = os.path.join(ROOT, "prototypes/newscut/out")
GAP = 0.10      # pause between sentences (s)
END_PAD = 0.10  # audio kept after a sentence's last word (s)
COVER_FRAMES = 2
FPS = 30


def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode != 0:
        raise SystemExit(f"FAILED: {' '.join(cmd)[:200]}\n{r.stderr[-1500:]}")
    return r


def norm(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


async def _speak(text, voice, rate, mp3):
    import edge_tts
    words = []
    com = edge_tts.Communicate(text, voice, rate=rate, boundary="WordBoundary")
    with open(mp3, "wb") as f:
        async for ev in com.stream():
            if ev["type"] == "audio":
                f.write(ev["data"])
            elif ev["type"] == "WordBoundary":
                words.append((ev["offset"] / 1e7, ev["duration"] / 1e7, ev["text"]))
    return words


def tts_sentence(chunks, tail, voice, rate, work, i):
    """Returns (wav, dur, [chunk start offsets]). The optional tail is spoken but cut out of the audio."""
    text = " ".join(c[1] for c in chunks) + (" " + tail if tail else "")
    mp3 = os.path.join(work, f"s{i}.mp3")
    meta = os.path.join(work, f"s{i}.json")
    sig = {"text": text, "voice": voice, "rate": rate}
    words = []
    if os.path.exists(meta) and os.path.exists(mp3):
        m = json.load(open(meta, encoding="utf-8"))
        if m.get("sig") == sig:
            words = [tuple(w) for w in m["words"]]
    for attempt in range(5 if not words else 0):  # the edge-tts service drops a request now and then: retry, same text and voice
        try:
            words = asyncio.run(_speak(text, voice, rate, mp3))
            if words:
                json.dump({"sig": sig, "words": words}, open(meta, "w", encoding="utf-8"))
                break
        except Exception as e:
            print(f"  tts retry {attempt + 1} (sentence {i}): {type(e).__name__}")
            time.sleep(1.5)
    if not words:
        raise SystemExit(f"tts failed for sentence {i}")
    starts, wi = [], 0
    for disp, spoken in chunks:
        want, got = norm(spoken), ""
        starts.append(words[wi][0])
        while got != want:
            if wi >= len(words) or not want.startswith(got):
                raise SystemExit(f"word align failed in sentence {i}: chunk {spoken!r} got {got!r}; words={[w[2] for w in words]}")
            got += norm(words[wi][2])
            wi += 1
    last = words[wi - 1]
    end = (words[wi][0] - 0.02) if (tail and wi < len(words)) else (last[0] + last[1] + END_PAD)
    lead = max(0.0, starts[0] - 0.03)
    wav = os.path.join(work, f"s{i}.wav")
    fo = 0.06 if tail else 0.02  # the cut-off loop line gets a softer edge so it doesn't click
    run([FF, "-v", "error", "-y", "-i", mp3, "-af", f"atrim={lead:.3f}:{end:.3f},asetpts=PTS-STARTPTS,afade=t=out:st={end-lead-fo:.3f}:d={fo}",
         "-ar", "48000", "-ac", "2", wav])
    return wav, end - lead, [s - lead for s in starts]


def mix(placed, total, music_file, music_vol, out_wav, duck=6.0, fade_in=0.25, fade_out=0.35):
    """Voice + looped music bed -> mastered wav. duck = sidechain ratio under the voice (<= 1: no ducking)."""
    inputs, filt = [], []
    for n, (st, w) in enumerate(placed):
        inputs += ["-i", w]
        filt.append(f"[{n}:a]adelay={int(st*1000)}|{int(st*1000)},apad=whole_dur={total:.3f}[v{n}]")
    nv = len(placed)
    inputs += ["-stream_loop", "-1", "-i", music_file]
    filt.append("".join(f"[v{i}]" for i in range(nv)) + f"amix=inputs={nv}:normalize=0,atrim=0:{total:.3f}[voice]")
    filt.append("[voice]asplit=2[va][vsc]")
    filt.append(f"[{nv}:a]atrim=0:{total + 1:.3f},volume={music_vol},afade=t=in:d={fade_in}" + (f",afade=t=out:st={total-fade_out:.3f}:d={fade_out}" if fade_out > 0 else "") + "[mus]")
    if duck > 1:
        filt.append(f"[mus][vsc]sidechaincompress=threshold=0.03:ratio={duck}:attack=15:release=300:makeup=1[duck]")
    else:
        filt.append("[vsc]anullsink")
        filt.append("[mus]anull[duck]")
    # apad + 1 s of extra music: the chain needs audio past the end so the last frames are real, then atrim cuts to total
    filt.append("[va][duck]amix=inputs=2:normalize=0:dropout_transition=0,apad=pad_dur=1,"
                "acompressor=threshold=-20dB:ratio=3:attack=5:release=80,loudnorm=I=-10.5:TP=-2.0:LRA=7,"
                "loudnorm=I=-10.5:TP=-2.0:LRA=7,alimiter=limit=0.8:level=false,aresample=48000,"
                f"asetpts=N/SR/TB,atrim=end_sample={round(total * 48000)}[out]")
    # trim by sample count: with loudnorm in the chain, output -t cut the file ~0.18 s short (silent tail at the loop point)
    run([FF, "-v", "error", "-y", *inputs, "-filter_complex", ";".join(filt), "-map", "[out]",
         "-ac", "2", "-ar", "48000", out_wav])


def lufs(path):
    r = subprocess.run([FF, "-hide_banner", "-nostats", "-i", path, "-af", "ebur128=peak=true", "-f", "null", "-"],
                       capture_output=True, text=True)
    return " | ".join(l.strip() for l in r.stderr.splitlines() if l.strip().startswith(("I:", "Peak:")))


def cut_shot(key, shot, length):
    """Cut one clip into public/ (cached by source, start, length and crop). Returns the public filename.
    Manual crop: "x" (and optional "y", "h") in source pixels; the window is 9:16, h high (default: full height)."""
    from app.services import auto_footage, craft
    auto_footage._REJECT_BURNED_IN_TEXT = False
    tag = f"{shot.get('x', 'a')}_{shot.get('y', 0)}_{shot.get('h', 'f')}{shot.get('fill', '')[:1]}"
    name = f"nc_{key}_{shot['vid']}_{int(round(shot['start'] * 100))}_{int(round(length * 100))}_{tag}.mp4"
    dst = os.path.join(PUB, name)
    if os.path.exists(dst) and os.path.getsize(dst) > 10000:
        return name
    orig = craft.subject_window
    if "x" in shot:
        h = int(shot.get("h", shot.get("srcH", 1080)))
        w = int(round(h * 9 / 16 / 2) * 2)
        win = {"w": w, "h": h, "x": int(shot["x"]), "y": int(shot.get("y", 0)), "method": "manual"}
        craft.subject_window = lambda *a, **k: win
    try:
        st = float(shot["start"])
        got = auto_footage.fetch_exact_clip(f"https://www.youtube.com/watch?v={shot['vid']}", st, st + length, 1080, 1920, dst,
                                            max_height=1080, max_filesize_mb=600, fill=shot.get("fill", "cover"), retries=2)
    finally:
        craft.subject_window = orig
    if not got:
        raise SystemExit(f"clip failed: {shot}")
    return name


def build_audio(spec, placed, total, out_wav):
    music = os.path.join(PUB, spec.get("music", "music3.mp3"))
    mix(placed, total, music, float(spec.get("musicVol", 0.14)), out_wav,
        duck=float(spec.get("duck", 6.0)), fade_in=float(spec.get("musicFadeIn", 0.25)),
        fade_out=float(spec.get("musicFadeOut", 0.35)))
    print("audio:", lufs(out_wav))


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags = {a for a in sys.argv[1:] if a.startswith("--")}
    spec = json.load(open(args[0], encoding="utf-8"))
    key = spec["key"]
    work = os.path.join(OUTDIR, key)
    os.makedirs(work, exist_ok=True)

    # 1. voice + chunk times
    chunks, placed, t = [], [], 0.0
    sents = spec["sentences"]
    for i, sent in enumerate(sents):
        tail = spec.get("loopTail", "") if i == len(sents) - 1 else ""
        wav, d, starts = tts_sentence(sent, tail, spec["voice"], spec["rate"], work, i)
        placed.append((t, wav))
        for (disp, _), s in zip(sent, starts):
            chunks.append({"t": round(t + s, 3), "text": disp})
        t += d + (GAP if i < len(sents) - 1 else 0.0)
    total = round(t + COVER_FRAMES / FPS, 3)
    words = sum(len(c[1].split()) for s in sents for c in s)
    print(f"voice: {t:.2f}s, {words} words, {words / t * 60:.0f} wpm, {len(chunks)} chunks; total {total:.2f}s")
    for n, c in enumerate(chunks):
        print(f"  {n:2d} {c['t']:6.2f}  {c['text']}")
    json.dump(chunks, open(os.path.join(work, "chunks.json"), "w"), indent=1)
    if "--tts-only" in flags:
        return
    if "--audio-only" in flags:
        # new mix on the existing render: the video stream is copied, nothing is re-rendered
        src = os.path.join(work, spec["out"])
        if not os.path.exists(src):
            raise SystemExit(f"no render to remix: {src}")
        wav = os.path.join(work, "remix_audio.wav")
        build_audio(spec, placed, total, wav)
        stem, ext = os.path.splitext(spec["out"])
        out = os.path.join(work, f"{stem}_v2{ext}")
        vdur = float(run([FP, "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=duration", "-of", "csv=p=0", src]).stdout.strip(" ,\n"))
        run([FF, "-v", "error", "-y", "-i", src, "-i", wav, "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy",
             "-af", f"apad=whole_dur={vdur:.3f}", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out])
        desk = os.path.expanduser(f"~/Desktop/{stem}_v2{ext}")
        shutil.copy2(out, desk)
        print("remixed:", desk, "|", lufs(desk))
        return

    # 2. shots
    shots_in = sorted(spec["shots"], key=lambda s: s["at"])
    assert shots_in[0]["at"] == 0, "first shot must start at chunk 0"
    shots = []
    for i, s in enumerate(shots_in):
        st = 0.0 if i == 0 else chunks[s["at"]]["t"] + float(s.get("shift", 0.0))
        en = t if i + 1 == len(shots_in) else chunks[shots_in[i + 1]["at"]]["t"] + float(shots_in[i + 1].get("shift", 0.0))
        row = {"from": round(st, 3), "dur": round(en - st, 3)}
        if s.get("gfx"):
            row["gfx"] = s["gfx"]
            row.update({k: v for k, v in s.items() if k in ("tag", "lines", "label", "note", "a", "b")})
            row["marks"] = [round(chunks[m]["t"] - st, 3) for m in s.get("marksAt", [])]
        if s.get("vid"):
            row["src"] = cut_shot(key, s, round(en - st + 0.35, 2))
        shots.append(row)
        print(f"  shot {i:2d} {st:6.2f} +{en - st:4.2f}  {('gfx:' + row['gfx'] + ' ') if row.get('gfx') else ''}{row.get('src', '')}")
    print(f"shots: {len(shots)}, avg {t / len(shots):.2f}s, longest {max(s['dur'] for s in shots):.2f}s")

    # 3. audio
    audio_name = f"nc_{key}_audio.wav"
    build_audio(spec, placed, total, os.path.join(PUB, audio_name))

    # 4. cover stills (frames taken from two of the cut clips)
    cover = dict(spec.get("cover") or {})
    for part in ("top", "bottom"):
        c = cover.get(part)
        if c:
            jpg = f"nc_{key}_cover_{part}.jpg"
            run([FF, "-v", "error", "-y", "-ss", str(c.get("t", 0.3)), "-i", os.path.join(PUB, shots[c["shot"]]["src"]),
                 "-frames:v", "1", "-q:v", "2", os.path.join(PUB, jpg)])
            cover[part] = jpg

    cards = [{"from": chunks[c["fromChunk"]]["t"], "to": (chunks[c["toChunk"]]["t"] if c["toChunk"] < len(chunks) else t),
              **{k: v for k, v in c.items() if k not in ("fromChunk", "toChunk")}} for c in spec.get("cards", [])]
    props = {"shots": shots, "caps": chunks, "cards": cards, "cover": cover, "coverFrames": COVER_FRAMES,
             "watermark": spec.get("watermark", "CD PHANTOM"), "audioFile": audio_name, "voiceEnd": round(t, 3),
             "durationInSeconds": total}
    if spec.get("hook"):
        props["hook"] = spec["hook"]
        props["hookDur"] = float(spec.get("hookDur", shots[1]["from"] if len(shots) > 1 and shots[1]["from"] > 0 else 0.7))
    props_path = os.path.join(work, "props.json")
    json.dump(props, open(props_path, "w"), indent=1)
    if "--no-render" in flags:
        print("props:", props_path)
        return

    # 5. one render
    out = os.path.join(work, spec["out"])
    port = random.randint(3400, 3900)
    run([shutil.which("npx") or "npx", "remotion", "render", "src/index.ts", "NewsCut", out, f"--props={props_path}", f"--port={port}",
         "--codec=h264", "--crf=17", "--concurrency=4", "--log=error"], cwd=REMO)
    desk = os.path.expanduser(f"~/Desktop/{spec['out']}")
    shutil.copy2(out, desk)
    print("rendered:", desk)


if __name__ == "__main__":
    main()
