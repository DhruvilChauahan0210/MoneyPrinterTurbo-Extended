#!/usr/bin/env python3
"""Grab a REAL news cut for a NewsCut Short: a screenshot of an article's headline area, or of an X post.

Usage (repo root):
  python nc_newsgrab.py <article-url> whatif-remotion/public/nc_<key>_news1.png
  python nc_newsgrab.py https://x.com/<user>/status/<id> whatif-remotion/public/nc_<key>_x1.png
Options: --width=430 (CSS px, phone width)  --scale=2.5 (pixel density)  --maxh=760 (CSS px kept below the top)
         --wait=3 (s after load)  --top=<css px> to start the crop at a fixed offset instead of above the headline

It opens the page in Remotion's own headless Chrome (whatif-remotion/node_modules/.remotion/chrome-headless-shell) at
phone size, removes cookie/consent/newsletter overlays and sticky bars, then screenshots from just above the main
headline down through the standfirst, byline and lead image. X posts are rendered with Twitter's public embed page
(platform.twitter.com/embed/Tweet.html), which needs no login.
It prints the page title and headline so you can check the grab is the real story. Never edit or fake a headline:
if a page will not render cleanly (paywall, bot wall), grab another outlet's real article instead.
In the spec, show it with a card: {"fromChunk": 16, "toChunk": 22, "image": "nc_<key>_news1.png", "site": "espn.com"}.
"""
import asyncio
import base64
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

import aiohttp

ROOT = os.path.dirname(os.path.abspath(__file__))
CHROME = os.path.join(ROOT, "whatif-remotion", "node_modules", ".remotion", "chrome-headless-shell", "win64",
                      "chrome-headless-shell-win64", "chrome-headless-shell.exe")
PORT = 9333
UA = ("Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/131.0.0.0 Mobile Safari/537.36")

CLEAN_JS = r"""
(() => {
  const bad = /cookie|consent|gdpr|onetrust|didomi|cmp-|sp_message|truste|paywall|piano|tp-modal|newsletter|subscribe|signup|modal|overlay|popup|interstitial|banner-ad|adhesion|notification/i;
  let n = 0;
  for (const el of [...document.querySelectorAll('body *')]) {
    const cs = getComputedStyle(el);
    const id = (el.id || '') + ' ' + (typeof el.className === 'string' ? el.className : '');
    if ((cs.position === 'fixed' || cs.position === 'sticky') || (bad.test(id) && (cs.position === 'absolute' || cs.zIndex > 100))) {
      el.remove(); n++;
    }
  }
  for (const el of [document.documentElement, document.body]) { el.style.overflow = 'visible'; el.style.position = 'static'; }
  document.querySelectorAll('iframe[src*="ads"], ins.adsbygoogle, [id^="google_ads"], [class*="ad-slot"], [class*="advert"]').forEach(e => { e.remove(); n++; });
  return n;
})()
"""

FIND_JS = r"""
((fixedTop, maxh) => {
  const vis = e => { const r = e.getBoundingClientRect(); return r.width > 40 && r.height > 10; };
  const hs = [...document.querySelectorAll('h1')].filter(vis);
  hs.sort((a, b) => parseFloat(getComputedStyle(b).fontSize) - parseFloat(getComputedStyle(a).fontSize));
  const h = hs[0];
  const sy = window.scrollY;
  if (!h) return { found: false, title: document.title, top: fixedTop ?? 0, height: maxh };
  const r = h.getBoundingClientRect();
  const top = fixedTop ?? Math.max(0, r.top + sy - 70);
  // extend through the lead image if it starts within reach
  let bottom = r.bottom + sy + 140;
  for (const img of [...document.querySelectorAll('img, picture, video')]) {
    const ir = img.getBoundingClientRect();
    if (ir.width >= window.innerWidth * 0.6 && ir.top + sy > r.bottom + sy - 5 && ir.top + sy < top + maxh) {
      bottom = Math.max(bottom, Math.min(ir.bottom + sy, top + maxh)); break;
    }
  }
  return { found: true, title: document.title, headline: h.innerText.trim().slice(0, 200), top, height: Math.min(maxh, bottom - top) };
})
"""

TWEET_JS = r"""
(() => {
  const el = document.querySelector('article') || document.querySelector('[data-testid="tweet"]') || document.body.firstElementChild;
  const r = el.getBoundingClientRect();
  return { found: !!el, title: document.title, headline: (el.innerText || '').trim().slice(0, 200), top: r.top + window.scrollY, left: r.left, width: r.width, height: r.height };
})()
"""


class CDP:
    def __init__(self, ws):
        self.ws, self.i, self.events = ws, 0, []

    async def call(self, method, **params):
        self.i += 1
        mid = self.i
        await self.ws.send_str(json.dumps({"id": mid, "method": method, "params": params}))
        while True:
            msg = json.loads((await self.ws.receive()).data)
            if msg.get("id") == mid:
                if "error" in msg:
                    raise RuntimeError(f"{method}: {msg['error']}")
                return msg.get("result", {})
            self.events.append(msg)

    async def wait_event(self, name, timeout):
        t0 = time.time()
        if any(e.get("method") == name for e in self.events):
            return True
        while time.time() - t0 < timeout:
            try:
                msg = json.loads((await asyncio.wait_for(self.ws.receive(), timeout=max(0.1, timeout - (time.time() - t0)))).data)
            except asyncio.TimeoutError:
                return False
            if msg.get("method") == name:
                return True
        return False


async def grab(url, out, width, scale, maxh, wait, fixed_top):
    tweet = re.search(r"(?:x|twitter)\.com/[^/]+/status/(\d+)", url)
    target = f"https://platform.twitter.com/embed/Tweet.html?id={tweet.group(1)}&theme=light&hideThread=true" if tweet else url
    async with aiohttp.ClientSession() as s:
        for _ in range(40):
            try:
                async with s.put(f"http://127.0.0.1:{PORT}/json/new?about:blank") as r:
                    tab = await r.json(content_type=None)
                break
            except Exception:
                await asyncio.sleep(0.25)
        else:
            raise SystemExit("headless Chrome did not start")
        async with s.ws_connect(tab["webSocketDebuggerUrl"], max_msg_size=0) as ws:
            c = CDP(ws)
            await c.call("Page.enable")
            await c.call("Network.enable")
            await c.call("Network.setUserAgentOverride", userAgent=UA)
            await c.call("Emulation.setDeviceMetricsOverride", width=width, height=1400, deviceScaleFactor=scale, mobile=True)
            await c.call("Page.navigate", url=target)
            await c.wait_event("Page.loadEventFired", 25)
            await asyncio.sleep(wait)
            if tweet:
                info = (await c.call("Runtime.evaluate", expression=TWEET_JS, returnByValue=True))["result"]["value"]
                clip = {"x": max(0, info["left"] - 6), "y": max(0, info["top"] - 6), "width": min(width, info["width"] + 12),
                        "height": info["height"] + 12, "scale": 1}
            else:
                removed = (await c.call("Runtime.evaluate", expression=CLEAN_JS, returnByValue=True))["result"].get("value")
                await asyncio.sleep(0.6)
                info = (await c.call("Runtime.evaluate", expression=f"{FIND_JS}({json.dumps(fixed_top)}, {maxh})", returnByValue=True))["result"]["value"]
                info["removed_overlays"] = removed
                clip = {"x": 0, "y": info["top"], "width": width, "height": max(120, info["height"]), "scale": 1}
            shot = await c.call("Page.captureScreenshot", format="png", clip=clip, captureBeyondViewport=True)
    open(out, "wb").write(base64.b64decode(shot["data"]))
    return info


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    opt = dict(a[2:].split("=", 1) for a in sys.argv[1:] if a.startswith("--") and "=" in a)
    if len(args) < 2:
        raise SystemExit(__doc__)
    url, out = args
    if not os.path.exists(CHROME):
        raise SystemExit(f"headless Chrome not found: {CHROME} (run one Remotion render first so it downloads)")
    prof = tempfile.mkdtemp(prefix="nc_newsgrab_")
    proc = subprocess.Popen([CHROME, f"--remote-debugging-port={PORT}", f"--user-data-dir={prof}", "--headless",
                             "--hide-scrollbars", "--mute-audio", "--no-first-run", "--disable-gpu", "about:blank"],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        info = asyncio.run(grab(url, out, int(opt.get("width", 430)), float(opt.get("scale", 2.5)), int(opt.get("maxh", 760)),
                                float(opt.get("wait", 3)), int(opt["top"]) if "top" in opt else None))
    finally:
        proc.terminate()
        try:
            proc.wait(5)
        except Exception:
            proc.kill()
        shutil.rmtree(prof, ignore_errors=True)
    from PIL import Image
    w, h = Image.open(out).size
    print(json.dumps({"out": out, "px": [w, h], **{k: info.get(k) for k in ("title", "headline", "found", "removed_overlays")}}, ensure_ascii=False))


if __name__ == "__main__":
    main()
