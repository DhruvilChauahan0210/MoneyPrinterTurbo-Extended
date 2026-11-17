#!/usr/bin/env python3
"""NewsCut helpers: cache source videos, make timestamped contact sheets, list scene cuts.

  .venv/bin/python nc_tools.py dl ID [ID...]            download each source once into the fetch_exact_clip cache
  .venv/bin/python nc_tools.py sheet ID FROM TO EVERY OUT.jpg [COLS W]  frame strip; labels are source seconds x10 (425 = 42.5 s)
  .venv/bin/python nc_tools.py scenes ID [FROM TO]      print scene-cut seconds (threshold 0.30)
"""
import hashlib, os, subprocess, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
FF = os.path.join(ROOT, ".venv/bin/ffmpeg")
CACHE = os.path.join(ROOT, "storage", "cache_videos", "comparison")


def url_of(vid):
    return f"https://www.youtube.com/watch?v={vid}"


def src_of(vid):
    d = os.path.join(CACHE, hashlib.md5(url_of(vid).encode()).hexdigest()[:12])
    if os.path.isdir(d):
        fs = sorted(f for f in os.listdir(d) if f.lower().endswith((".mp4", ".mkv", ".webm", ".mov")) and os.path.getsize(os.path.join(d, f)) > 100000)
        if fs:
            return os.path.join(d, fs[0])
    return ""


def dl(vids):
    from app.services import auto_footage as a
    use_node = bool(a._which("node") or a._which("deno"))
    for v in vids:
        if src_of(v):
            print(v, "cached", src_of(v)); continue
        d = os.path.join(CACHE, hashlib.md5(url_of(v).encode()).hexdigest()[:12])
        os.makedirs(d, exist_ok=True)
        p = a._download_url(url_of(v), d, 1080, 600, use_node, timeout=600, retries=2)
        print(v, "OK" if p else "FAILED", p, flush=True)


def sheet(vid, a, b, every, out, cols=10, w=192):
    """Frame strip: one frame every `every` seconds, each labelled with its real source second."""
    src = src_of(vid)
    n = int((b - a) / every) + 1
    rows = (n + cols - 1) // cols
    vf = (f"select='isnan(prev_selected_t)+gte(t-prev_selected_t\\,{every})',scale={w}:-2,"
          f"drawtext=text='%{{eif\\:(t+{a})*10\\:d}}':x=4:y=4:fontsize=20:fontcolor=yellow:box=1:boxcolor=black@0.7,"
          f"tile={cols}x{rows}")
    r = subprocess.run([FF, "-v", "error", "-y", "-ss", str(a), "-t", str(b - a), "-i", src, "-vf", vf, "-frames:v", "1", "-q:v", "4", out],
                       capture_output=True, text=True)
    print(out if r.returncode == 0 else r.stderr[-400:])


def scenes(vid, a=None, b=None):
    src = src_of(vid)
    cmd = [FF, "-hide_banner", "-nostats"]
    if a is not None:
        cmd += ["-ss", str(a), "-t", str(b - a)]
    cmd += ["-i", src, "-vf", "scale=320:-2,select='gt(scene,0.30)',showinfo", "-f", "null", "-"]
    r = subprocess.run(cmd, capture_output=True, text=True)
    ts = [round(float(l.split("pts_time:")[1].split()[0]) + (a or 0), 2) for l in r.stderr.splitlines() if "pts_time:" in l]
    print(" ".join(f"{t:.2f}" for t in ts))


if __name__ == "__main__":
    c = sys.argv[1]
    if c == "dl":
        dl(sys.argv[2:])
    elif c == "sheet":
        sheet(sys.argv[2], float(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5]), sys.argv[6], *(int(x) for x in sys.argv[7:9]))
    elif c == "scenes":
        scenes(sys.argv[2], *(float(x) for x in sys.argv[3:5]))
