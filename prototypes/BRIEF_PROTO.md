# Prototype brief (CD approved on 8 Nov 2026: "start building prototypes now, 2 a day")

Repo: ~/Developer/CDH/MoneyPrinterTurbo-Extended. Use `export PATH="$HOME/.deno/bin:$PWD/.venv/bin:$PATH"`. Address the user as CD in any text.
Read FIRST: research_nov8/PLAN_28NOV.md (sections 1-5), .claude/skills/football-shorts/reference/rules-and-traps.md, and for beat-plan work
.claude/skills/football-shorts/SKILL.md steps 3-7 (config, photos, clips, one-render rule, QC).

## Why prototypes
CD PHANTOM's views fell ~80% on 29 Oct. Our current recipe (landscape photo in the middle third with blurred bars, stills held 3-4.5 s, no hook
card, no face-first opening, 29% stayed-to-watch, same title suffix) is the weakest class in the market. The sprint from 28 Nov (2 Shorts a day, 17:00
and 21:00 IST) tests 3 new recipes. These prototypes prove the recipes can be built with our tools and give CD something to look at.
Winners in the data: face or strong motion in the first second, a hook text on frame 1, a cut every 2.5-3.5 s, real moving footage, a conflict
or personal story angle, an ARGUED position (originality), and original graphics. Narrating facts over still photos is the weakest class.

## Hard rules
- Do NOT upload, schedule, or touch YouTube Studio. Do NOT use any chrome / browser MCP tools (CD's real Chrome is in use). Do not touch the
  already-scheduled Shorts, `~/Desktop/<DD>NOV_slot*` files, or any `batch_*.json` that already exists (copy to a new file name for yours).
- ONE render attempt per Short (CD's rule). If it fails, diagnose, report, and only re-render if the failure is clearly a bug in YOUR config/composition
  that you can fix without changing the recipe; say so in the report.
- Every DuckDuckGo-touching command (beat_source.py, whatif_photos.py, any image search) must run as `./ddg_lock.sh <command>` because other agents
  are searching at the same time. Never run beat_source on a config while pinning/picking the same config.
- Verify every fact by fetching a source page. No accusations or insults of real people ("X accused Y of...", "liar", "robbed", "cheat"): the Jev gate
  blocks them. No invented quotes or dialogue. State opinions as questions or as arguments from numbers.
- Remotion: use `--port=$((3400 + RANDOM % 500))` (port 3000 is CD's dev server). Disk is fine (247 GB free) but delete your temp renders when done.
- Deliver the finished Short(s) to `~/Desktop/PROTO_<recipe>_<topic>.mp4` and put every file you create under the repo (scripts at repo root named
  `gen_proto_<recipe>*.py`, assets under `prototypes/<recipe>/`). Make a 6-8 frame mosaic (`ffmpeg ... tile`) and LOOK at it with the Read tool; report
  honestly what is wrong (wrong person, text bands, watermark, blur bars, soft frames).
- Do not write report files (the Write tool refuses); return your report as your final message: what you built, file paths, measured facts (duration,
  cuts per 10 s, % moving footage, loudness), what is weak, what needs a decision from CD, and how long the build really took (so we can plan 28 Shorts).
- Time box: about 60-75 minutes. Report problems early rather than burning time.

## Title style for these Shorts (sprint rule)
30-45 characters, a statement not a question, star or event first, ONE emoji, no colon / pipe / quote marks, no `#halo try this sound #shorts` suffix.
Give your Short a proposed title, description (2-3 sentences + hashtags) and tags in your final message (chat only, never in files).
