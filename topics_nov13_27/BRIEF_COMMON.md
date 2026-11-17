# Common brief: CD PHANTOM football Shorts for 13-27 Nov 2026 (read fully)

Repo root: /Users/dhruvilchauhan/Developer/CDH/MoneyPrinterTurbo-Extended. Today is 6 Nov 2026. These Shorts are all scheduled in advance and will go live between 13 and 27 Nov 2026,
and must still work (true, interesting, unexpired) 20+ days after that. Write ONLY the JSON file named in your task. Do not edit any other file, do not delete anything.

## Why these rules (from CD's analytics, 6 Nov 2026)
Views per Short fell from ~1,000 to 40-320; the Shorts that broke out had a hard NUMBER or named CONFLICT in the first second and >50% "stayed to watch"
(e.g. "Mbappe was ROBBED by 28 points", "23 YEARS AND STILL GOING"). Vague hooks ("NOBODY SAW THIS COMING") lost. Viewers decide in the first second from the first photo and first spoken words.

## Topic rules (hard)
1. EVERGREEN: a finished past event (historic match/goal/final/record/rivalry moment/dramatic reversal) whose facts will not change. NEVER: current-season stats, "this season", form, injuries, transfers, rumours,
   upcoming matches, anything still to be decided, "latest/now/currently". Do not state running totals that grow (career goals etc.) unless pinned to a date ("by the end of 2022").
2. DRAMA + A NUMBER: a twist, reversal, rejection, revenge, collapse, snub, impossible comeback, rivalry. Prefer a concrete number or named rival/coach/referee in the first line.
3. PHOTOGRAPHABLE: a named match/goal/trophy/ceremony so era-accurate photos and broadcast clips exist. No salary/contract/business/health topics.
4. MEGASTARS ONLY as subject (Ronaldo, Messi, Mbappe, Haaland, Vinicius, Bellingham, Yamal, Neymar, Kane, Salah).
5. NOT ALREADY COVERED: the repo has ~490 configs. First `ls batch_*.json` and grep: `grep -il "<keyword>" batch_*.json`. Then PRE-SCREEN every candidate with Jev:
   write one subject sentence per line into a text file and run `.venv/bin/python jev_tools.py topics yourfile.txt` (shows dup=0.xx with the closest existing file; a topic with dup >= 0.80 is BLOCKED, so discard or change angle; aim <0.60).
   Also run `.venv/bin/python jev_tools.py screen "your whole script"`: any sentence flagged defamatory/rumour_as_fact (>=0.8) will block; rewrite it neutrally. 'overclaim' warnings are fine.
6. NO accusations/insults ("X accused Y of ...", "called him a liar", "cheated") and no claims about living people's private life/legal issues. State only verified facts with neutral attribution.
7. VERIFY EVERY FACT by fetching a source page (WebFetch / WebSearch). Search snippets invent things; Wikipedia match pages, UEFA/FIFA, BBC, ESPN, Guardian, Reuters are good. Record source URLs. If you cannot verify a fact, drop it.

## Script rules
- 8 or 9 beats. Joined `says` = the whole spoken script: 65-78 words total (hard cap 80), about 30s. Write numbers/years/scores AS WORDS for the voice ("two thousand and eleven", "twenty eleven", "four-two", "the seventy-sixth minute"); no digits in `says`.
- BEAT 1 (opening rule): `visual` = "close up of <star> in <correct team kit/era>" (a big recognisable face), and `says` must START with a number or the star's NAME + a hook fact (e.g. "Six goals. One Golden Boot. ..." or "Messi scored two goals in eleven minutes ..."). NEVER start with a bare date ("April 2017 ...") or a wide scene.
- Each other beat: one short spoken line (<= 12 words) + `visual` (what photo is needed) + `images` = 2 PLAIN search queries (a name + one keyword, e.g. "Lionel Messi Barcelona 2011", "Pepe Real Madrid"). Long/descriptive queries return junk. Every second named person must also appear in `positives`.
- Last beat = the debate question. `cta` = short ALL-CAPS question ending with " 👇" (emoji only at the end). `hook` = <= 6 words ALL CAPS posing a question, sharing NO words with beat 1's `says`.
- `cover` = one phrase describing the best hero photo ("Lionel Messi celebrating for Barcelona"). `terms` = comma keyword string.
- `clip_queries` (optional, 1-2 strings): YouTube search phrases likely to find a BROADCAST highlight of the key moment (not fan edits / cartoons). Only for famous matches.
- Metadata (for YouTube): `title_hook` ~28 chars, leads with a name or number, exactly ONE ALL-CAPS curiosity word (e.g. "Kane's 6 goals, England FOURTH"); `p1` (hook + concrete facts, starts with the player's full name), `p2` (payoff ending in the debate question), `hashtags` (5-7 topic hashtags like "#HarryKane #WorldCup2018"), `tags` (exactly 14 comma-separated topic tags), `pinned` (the CTA rephrased as a question ending with " 👀"). Description facts must match the script exactly; add no new claims.

## JSON schema (a list; put the best first; include the requested number of EXTRA spare candidates at the end, marked "spare": true)
{"slot": "<as told>", "name": "<unique_snake_slug_prefixed_by_star>", "star": "...", "subject": "<one sentence, concrete, includes year/competition/numbers>",
 "beats": [{"says": "...", "visual": "...", "images": ["q1", "q2"]}, ...], "hook": "...", "cta": "...", "terms": "...", "cover": "...", "positives": ["a real photograph of X", ...],
 "clip_queries": ["..."], "title_hook": "...", "p1": "...", "p2": "...", "hashtags": "#A #B ...", "tags": "t1, t2, ... (14)", "pinned": "... 👀",
 "dup": <closest Jev dup score you measured>, "sources": ["https://...", ...], "why_evergreen": "<one line>"}
When done, reply with only: the file path, the count, and any topics you dropped and why (<= 6 lines).
