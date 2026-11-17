# Common brief (read fully)

Client: CD. Channel: CD PHANTOM (@CDPHANTOM-0210, UCfLjJwaxD7VhKwfSmTDQv3Q), a FACELESS football YouTube Shorts channel.
Today is 8 Nov 2026. 45 Shorts are already scheduled for 13-27 Nov. CD wants to LEARN why views collapsed and decide what to build
from 28 Nov onward. Do NOT touch the schedule or YouTube Studio. Your job is research only; write findings to files.

## What we make today
- Beat-plan Shorts, 27-35 s, 1080x1920, edge-tts voice (EricNeural, calm male), 65-80 spoken words, 8-9 beats of ONE image/clip each
  (a "beat" = one sentence, one visual). Visuals = Google/DDG photos of the star (often still images with slow zoom) plus a few 6 s
  match-highlight clips. White caption, no on-screen hook card, music bed. Topics: Ronaldo, Messi, Mbappe, Haaland, Kane, Salah,
  Yamal, Vinicius, Bellingham, Neymar; angles: records, famous matches, "What If" 7 s Shorts (one photo + a question).
- 3 Shorts a day, 13:00 / 17:00 / 21:00 IST. India audience 25%, UK 7%, US 4.5%; 99% of watch time is from non-subscribers;
  Shorts feed is ~95% of traffic.
- Performance: Oct 24-28 about 1,000 views/Short; since 29 Oct 40-320 views/Short. "Stayed to watch" ~39% -> ~28-34%; the only
  Shorts that broke out had ~50%+ stayed-to-watch and a hard number or named conflict in the hook. Jul 2026: 180K views/month, with
  breakouts at 15K (confrontation hooks, #halo trending sound). Sep: 80K/month. Now far lower.
- Past learnings: first 3 seconds decide everything; 25-45 s is the performing length now; family/personal drama topics beat pure
  career facts 5-10x on one benchmark channel; serialized "Part N" titles repel cold viewers.

## Rules for you
- Tools: use `~/Developer/CDH/MoneyPrinterTurbo-Extended/.venv/bin/yt-dlp` (needs deno on PATH: `export PATH="$HOME/.deno/bin:$HOME/Developer/CDH/MoneyPrinterTurbo-Extended/.venv/bin:$PATH"`),
  WebSearch, WebFetch. Do NOT use any chrome / browser MCP tools (the user's real Chrome is in use by someone else).
  If yt-dlp needs cookies, try `--cookies-from-browser chrome` last; first try without.
- Be gentle with YouTube: sleep 1-2 s between requests (`--sleep-requests 1`), no parallel hammering.
- Metadata-only first. Download at most 6 videos total (small, `-f "bv*[height<=720]+ba/b[height<=720]"`) into your own scratch dir
  and look at frame mosaics (ffmpeg is in the repo .venv/bin; `ffmpeg -i x.mp4 -vf "fps=1/2,scale=270:-1,tile=6x2" mosaic.jpg`) with the Read tool.
- Put every artifact under `~/Developer/CDH/MoneyPrinterTurbo-Extended/research_nov8/<your-letter>/` (raw data jsonl/csv, mosaics, your report).
- Facts only from data you actually pulled. Quote numbers with their source. Say clearly what is a measured fact vs your inference.
  No invented channels or view counts: if a search fails, say so.
- Time box: about 60 minutes of work. Finish with a report file `report.md` in your folder, and return its key findings (max ~600 words)
  as your final message: top patterns, the numbers behind them, and concrete things CD's pipeline could copy.
