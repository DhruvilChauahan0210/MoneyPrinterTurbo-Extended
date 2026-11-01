---
name: football-shorts
description: Build and schedule CD's football YouTube Shorts for the CD PHANTOM channel end to end, from topic research to scheduled in YouTube Studio. Covers choosing verified topics, writing beat-plan scripts, sourcing photos and match clips, rendering once per Short, QC, Desktop delivery, What-If Shorts, chat metadata and fast Studio scheduling. Use whenever the user asks to make, generate or build Shorts for a day or a range of days, to write Shorts metadata, or to schedule or upload Shorts.
---

# Football Shorts: creation to scheduled

This is the exact workflow CD approved (built 2–11 Nov 2026, 30 Shorts). Follow it in order and don't improvise
on the rules marked **RULE**. Everything runs from the repo root `~/Developer/CDH/MoneyPrinterTurbo-Extended`.
Address the user as **CD**.

```bash
export PATH="$HOME/.deno/bin:$PWD/.venv/bin:$PATH"   # ffmpeg, edge-tts, yt-dlp, deno live here
```

Files in this skill:
- `scripts/shortbuild.py`: `build()` turns a beat list into a batch config (`from shortbuild import build`).
  Copy it to the repo root, or add the skill's scripts folder to `sys.path`.
- `scripts/review.py`, `scripts/borrow.py`: photo pick sheets, and filling an empty beat from another beat's candidate.
- `scripts/run_day.sh`: one-render-per-Short build runner with a watchdog.
- `scripts/whatif.sh`, `scripts/whatif_photos.py`: What-If Shorts (Remotion).
- `scripts/qc_mosaic.sh`: 6-frame mosaic per Short for the visual check.
- `scripts/make_meta.py`, `scripts/cors_server.py`, `scripts/sched.js`: fast YouTube Studio scheduling.
- `reference/rules-and-traps.md`: every lesson learned (read it before the first build of a session).
- `reference/metadata-template.md`: the exact metadata format CD pastes into YouTube.
- `reference/youtube-schedule.md`: CD's Studio steps and how the fast scheduler works.

---

## 1. Plan the days
- **RULE: 3 Shorts a day** at **13:00 / 17:00 / 21:00 IST** (slot 1 / slot 2 / slot 3).
- **RULE: slot 1 and slot 3 are always Ronaldo and Messi, swapping each day.** 2 Nov 2026 = Ronaldo 13:00 / Messi
  21:00, so even November days are Ronaldo first and odd days Messi first. Check the last built day on the Desktop
  (`ls ~/Desktop | grep -E '^[0-9]{2}[A-Z]{3}_slot'`) and continue the flip from there.
- **RULE: slot 2 alternates by day** between a normal Short about another megastar and a **What-If** Short.
  In Nov 2026 the odd days (3, 5, 7, 9, 11) were What-If, so **12 Nov = normal**.
- If it's unclear which day was last uploaded, ask CD. A filename is not an upload date.
- **RULE: when CD asks for N days, build every slot of every day in one go.** No approval stop between Shorts
  or days. Report once at the end.

## 2. Topics (one verified angle per Short)
Spinning off research agents in parallel is fine (Ronaldo / Messi / slot-2 stars), each briefed with these rules:
- **Megastars only:** Ronaldo, Messi, Mbappé, Haaland, Vinícius, Bellingham, Yamal, Neymar, Kane, Salah.
  No retro legends as the subject.
- **Not already covered:** grep the ledger, `grep -l -i "<keyword>" batch_*.json`, and read the nearest scripts.
  The Jev preflight gate **blocks** any topic whose subject is more than 0.8 similar to an existing config.
- **Stays true until the posting day:** use past events or evergreen moments, never an outcome still to be decided.
- **Photographable and concrete:** a goal, match, trophy, record with numbers or named rival. Salary, contract,
  durability and business angles fail (no photos).
- **Drama over safe facts:** a conflict, rejection, revenge, rivalry or an emotional moment.
- **Verify every fact by fetching the source page.** Search summaries invent things.
- **RULE: no accusation or insult lines.** Jev hard-blocks "X accused Y of…" and "called him a liar" as
  'defamatory' or 'rumour_as_fact'. Transfer and ownership stories must say "reports say" plus "declined to
  comment" or "a deal might not happen".
- Famous historic matches (finals, 8–2, Anfield 2019, hat-tricks) are good evergreen fillers, and real clips exist for them.

## 3. Scripts and configs
- **8–9 beats.** Each beat is `B(says, visual, image_query_1, image_query_2)`. The joined `says` must equal the
  script exactly (the `build()` helper does this).
- **65–80 words (81 is the hard cap) at voice_rate 0.88 (in shortbuild),** which gives 26–35s. Render band is
  18–38s, and over 38s fails `check_render`.
- **Hook:** at most 6 words, ALL CAPS, sharing no words with spoken line 1, posing the question rather than
  answering it. **CTA:** a short ALL-CAPS question ending with ` 👇` (emoji only at the end).
- Every second named person in the script must be added to `positives` / `extra`, or their beats starve.
- Use plain image queries ("Harry Kane", "Kily Gonzalez"). Long queries return junk.
- Write one `gen_<range>.py` per build (see `gen_nov_rm.py` / `gen_nov_slot2.py` in the repo for the pattern),
  run it, then run `check_config.py` on each config. Ignore the "CLIP-weak list" warning (beat plans don't use the
  footage gate). Fix every over-length or hook-overlap warning **before** rendering.

## 4. Photos (pick once, before rendering)
```bash
.venv/bin/python beat_source.py batch_X.json            # one config at a time, never several in parallel
.venv/bin/python <skill>/scripts/review.py batch_X.json /tmp/rv_X.jpg 6   # one row per beat, top 6 candidates
.venv/bin/python beat_source.py batch_X.json --pick "1=0,2=3,3=1,..."    # beat=candidate index
.venv/bin/python <skill>/scripts/borrow.py batch_X.json 4 8 1            # empty beat 4 <- beat 8's candidate 1
```
- Look at every sheet. Pick the right person and era, prefer portrait framing, and never repeat a photo within a Short.
- A beat with junk or zero candidates: change its queries to plain names and run `--beats N`, or borrow.
- Wrap sourcing in a watchdog. A DDG query can hang forever; if it does, change that query.
- **Never run sourcing on a config while pinning or picking it.** Sourcing writes the JSON at the end and wipes the pins.

## 5. Real clips (CD wants clips wherever they exist)
For famous match moments, pin 2–4 clip beats per Short and keep photos for the rest:
```bash
.venv/bin/python beat_source.py batch_X.json --find "Barcelona 2-8 Bayern highlights|..."   # text list only
.venv/bin/python beat_source.py batch_X.json --scan "https://www.youtube.com/watch?v=ID" --scan-every 2
.venv/bin/python beat_source.py batch_X.json --replace 4 --url "https://www.youtube.com/watch?v=ID" --start 112 --len 4.4
```
- Read the scan strip and pick the seconds where the subject is clearly visible.
- **Reject 442oons cartoons and fan-phone uploads** (heads or hands in frame). Prefer broadcast highlight uploads.
- **RULE: always pin clips with `--len 6.0`** (the source must have 6s left after `--start`). A clip shorter than
  its spoken beat fails the whole render ("visual coverage X for Y audio"), and word count is a bad predictor:
  an 8-word beat with long names ran 4.9s and failed at 4.4s (12 Nov 2026).
- Changing `len` does not re-cut a cached shot. `rm` that beat's `shot_*.mp4` first, then `--replace`, then check it with ffprobe.

## 6. Render: exactly one attempt per Short
**RULE (CD, 1 Nov 2026): "do everything in first shot, don't retry any Short."**
- Fill `scripts/run_day.sh`'s build list (`cfg out` per line) and run it in the background. It wraps each
  render in caffeinate and a 25-minute watchdog, skips anything already on the Desktop or already attempted,
  and copies the result to `~/Desktop/<DDMON>_slot<N>_<HHMM>_<topic>.mp4`.
- Two batches can run in parallel. Don't edit a run script while it is executing.
- If a Short fails (Jev block, coverage), **don't rebuild it.** Report it. If CD then asks for replacements,
  pick a **new** topic for that slot and render it once.

## 7. QC (look, don't re-render)
- `check_render.py <mp4> ~/Desktop/BUILDLOG_<cfg>.log <cfg>`. "No assigner summary" and soft-shot warnings are normal for beat plans.
- `scripts/qc_mosaic.sh`, then read every mosaic: right person, nothing absurd. **Flag** problems to CD and ship as-is.

## 8. What-If Shorts (slot 2 on What-If days)
- Pick an evergreen alternate-history question about a megastar ("What if Messi never left Barcelona in 2021?").
- `scripts/whatif_photos.py`: source era-accurate photos, view the sheet and pick one (portrait if possible),
  then save it as `whatif-remotion/public/wi_<name>.jpg`.
- `scripts/whatif.sh` renders the Remotion `WhatIf` composition: an edge-tts EricNeural voice reads the
  question, the title is split over two caps lines, duration = voice + 1.2s (about 6–7s), output goes to the Desktop.

## 9. Deliver
- All Shorts go on `~/Desktop` with the slot naming above.
- **Metadata goes in chat only (never in files),** and only once every Short is built, using
  `reference/metadata-template.md` exactly: four separate blocks per Short (TITLE / DESCRIPTION / TAGS /
  PINNED COMMENT), with the slot time, filename and duration in each heading.
- Then go straight to step 10 (schedule). Report once at the end in short form: what's built and scheduled, what
  failed and why, anything shipped with flaws, and sources.
- Update the inventory memory if this login has memory (next build day, the slot-1 flip, slot-2 type).

## 10. Schedule on YouTube (ALWAYS, as the last step of every build)
**RULE (CD, 2 Nov 2026): a build is not done until it is scheduled.** After step 9, schedule every Short you
built in its slot (date + 13:00/17:00/21:00 IST) without waiting to be asked, then confirm it in the Content list
and delete the upload folder. Follow `reference/youtube-schedule.md`. In short:
1. Copy the Shorts plus a `meta.json` (built by `scripts/make_meta.py`) into a folder **inside the repo**.
   The chrome MCP can't read `~/Desktop`.
2. `python3 scripts/cors_server.py <that folder> 8799 &`
3. In CD's Studio tab (chrome MCP, CD's real Chrome, CD PHANTOM channel), run `evaluate_script` with
   `sourcePath: <skill>/scripts/sched.js`, then call `window.__sched(i)` in batches of 6–8 per call.
   It takes about 40s per Short, with no screenshots.
4. Reload the Content → Shorts list and confirm every row says **Scheduled** with the right date.
5. Stop the server by PID. Pinned comments stay manual (YouTube only allows them after a Short goes live).
**RULE: go fast.** CD can schedule one by hand in about 1 minute, so never click step by step with screenshots.
