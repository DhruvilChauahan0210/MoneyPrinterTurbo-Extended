import copy
import json


def build(donor, output, *, subject, beats, hook, cta, terms, cover, positives):
    with open(donor, "r", encoding="utf-8") as handle:
        data = json.load(handle)

    script = " ".join(b["says"] for b in beats)
    plan = [{"says": b["says"], "visual": b["visual"], "images": b["images"], "clips": []} for b in beats]

    defaults = copy.deepcopy(data["defaults"])
    defaults.update(
        video_subject=subject,
        video_script=script,
        video_terms=terms,
        hook_text=hook,
        cta_text=cta,
        hook_cover_term=cover,
        subject_positive_labels=positives,
        visual_evidence_prompts=positives,
        curated_image_paths=[],
        intro_image_paths=[],
        beat_plan=plan,
        beat_shared_clips=[],
        series_badge_text="",
        series_ledger_path="",
        enable_youtube_footage=False,
        youtube_only_media=False,
        youtube_footage_queries=[],
        voice_rate=0.88,
        bgm_type="random",
        bgm_volume=0.10,
        cover_min_keep=0.62,
        # Fix for the repeated "render plan is short Xs vs Ys required" near-misses: raising the
        # per-shot hold length means each surviving image covers more seconds, so total visual
        # duration clears the audio length reliably instead of depending on getting lucky with
        # how many images survive the editorial/sharpness gates.
        video_clip_duration=7,
    )
    data["defaults"] = defaults
    data["videos"] = [{
        "video_subject": subject,
        "video_script": script,
        "video_terms": terms,
        "hook_text": hook,
        "cta_text": cta,
        "beat_plan": plan,
        "beat_shared_clips": [],
    }]
    with open(output, "w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    print(f"{output}: {len(script.split())} words, {len(beats)} beats")


# 28 OCT slot 1 (13:00) — Messi. Alternation flips: Messi slot 1 / Ronaldo slot 3 (per
# shorts-inventory-status memory: 27 Oct was Ronaldo slot1/Messi slot3).
# NOTE: original angle (Miami contract to 2028) HARD FAILED on thin pool (10 distinct images for
# 8 beats). Swapped to a goal-celebration milestone per the "swap the topic, don't tune" rule —
# celebration shots are far more heavily photographed/indexed than a contract-signing story.
build(
    "batch_messi_1000_prediction.json",
    "batch_messi_miami100goals.json",
    subject=(
        "Lionel Messi has scored his 100th goal for Inter Miami, reaching the milestone in MLS "
        "play at age 39 while already agreeing to extend his contract through 2028"
    ),
    beats=[
        {"says": "Lionel Messi just hit a number nobody saw coming this fast.",
         "visual": "Lionel Messi celebrating a goal for Inter Miami",
         "images": ["Messi goal celebration Inter Miami 2026", "Lionel Messi Inter Miami goal"]},
        {"says": "One hundred goals for Inter Miami.",
         "visual": "Lionel Messi pointing to the sky after scoring",
         "images": ["Messi pointing to the sky Inter Miami", "Messi celebration pointing up 2026"]},
        {"says": "He reached it faster than almost anyone expected when he arrived in Miami.",
         "visual": "Lionel Messi running with the ball for Inter Miami",
         "images": ["Messi running Inter Miami 2026", "Messi dribble Inter Miami"]},
        {"says": "At thirty nine, most players have already retired.",
         "visual": "Lionel Messi warming up before a match",
         "images": ["Messi Inter Miami warm up 2026", "Messi Inter Miami training pitch"]},
        {"says": "Instead he just agreed to stay in Miami until twenty twenty eight.",
         "visual": "Lionel Messi in Inter Miami kit looking serious",
         "images": ["Lionel Messi Inter Miami 2026 serious", "Messi Inter Miami portrait 2026"]},
        {"says": "He had already retired from Argentina and hinted his career could end soon.",
         "visual": "Lionel Messi waving in an Argentina shirt",
         "images": ["Messi Argentina farewell wave", "Messi Argentina last match goodbye"]},
        {"says": "But the goals keep coming anyway.",
         "visual": "Lionel Messi celebrating with Inter Miami teammates",
         "images": ["Messi Inter Miami teammates celebration", "Messi Inter Miami team celebrate goal"]},
        {"says": "How many more can he score before twenty twenty eight?",
         "visual": "Lionel Messi smiling on the pitch",
         "images": ["Messi Inter Miami smiling 2026", "Lionel Messi happy Inter Miami"]},
    ],
    hook="100 GOALS AND NOT DONE YET",
    cta="HOW MANY MORE BEFORE 2028? 👇",
    terms=(
        "Lionel Messi, Messi Inter Miami, Messi Inter Miami goal celebration, "
        "Messi Inter Miami 2026, Messi pointing to sky, Messi Inter Miami running, "
        "Messi Inter Miami training, Messi Argentina, Messi Inter Miami teammates, "
        "Messi smiling Inter Miami, Messi close up, Messi portrait, "
        "Messi celebrating goal, Messi free kick, Messi warm up, Messi Miami fans"
    ),
    cover="Lionel Messi celebrating a goal for Inter Miami",
    positives=[
        "a real photograph of Lionel Messi",
        "a real photograph of Lionel Messi playing for Inter Miami",
        "a real photograph of Lionel Messi celebrating a goal",
    ],
)

# 28 OCT slot 2 (17:00) — free pick. SWAPPED TWICE: Yamal injury hard-failed (too new/thin a photo
# pool for an 18-year-old's single event), then Vinicius Jr hard-failed 3x even at 20 search terms
# (consistently only ~17 raw images — his online photo pool is just thinner than expected for this
# sourcing path). Landing on Mbappe: proven deep pool (32 prior successful builds on this subject in
# the ledger), so pool depth is not a gamble here. Fresh angle (goals-for-Real-Madrid milestone, not
# in the ledger's 100th/madrid13/finalhattrick/etc. angles already covered).
build(
    "batch_kane_ronaldo_streak.json",
    "batch_mbappe_madrid_goaltally.json",
    subject=(
        "Kylian Mbappe has now scored over 50 goals in all competitions for Real Madrid since "
        "joining the club in 2024, one of the fastest tallies in the club's history"
    ),
    beats=[
        {"says": "Kylian Mbappe just passed a number worth stopping for.",
         "visual": "Kylian Mbappe celebrating a goal for Real Madrid",
         "images": ["Mbappe goal celebration Real Madrid 2026", "Kylian Mbappe Real Madrid goal"]},
        {"says": "Over fifty goals in all competitions since he signed.",
         "visual": "Kylian Mbappe pointing to the sky after scoring",
         "images": ["Mbappe celebration pointing sky", "Mbappe Real Madrid celebration 2026"]},
        {"says": "He only joined Real Madrid back in twenty twenty four.",
         "visual": "Kylian Mbappe in Real Madrid kit looking serious",
         "images": ["Kylian Mbappe Real Madrid portrait 2026", "Mbappe Real Madrid serious close up"]},
        {"says": "That is one of the fastest tallies in the club's history.",
         "visual": "Real Madrid's Santiago Bernabeu stadium",
         "images": ["Santiago Bernabeu stadium 2026", "Real Madrid Bernabeu exterior"]},
        {"says": "He is running at a pace that puts him alongside Real Madrid legends.",
         "visual": "Kylian Mbappe running with the ball for Real Madrid",
         "images": ["Mbappe dribble Real Madrid 2026", "Kylian Mbappe running with ball"]},
        {"says": "Fans in Paris once feared this day would never come.",
         "visual": "Kylian Mbappe training with Real Madrid",
         "images": ["Mbappe training Real Madrid 2026", "Kylian Mbappe practice session"]},
        {"says": "Now he is doing it for Real Madrid instead.",
         "visual": "Kylian Mbappe celebrating with Real Madrid teammates",
         "images": ["Mbappe teammates celebration Real Madrid", "Kylian Mbappe team celebrate goal"]},
        {"says": "How many more before this season is over?",
         "visual": "Kylian Mbappe smiling on the pitch",
         "images": ["Mbappe smiling Real Madrid 2026", "Kylian Mbappe happy celebration"]},
    ],
    hook="50 GOALS AND COUNTING",
    cta="HOW MANY MORE THIS SEASON? 👇",
    terms=(
        "Kylian Mbappe, Mbappe Real Madrid, Mbappe goal celebration, Mbappe close up, "
        "Mbappe portrait, Mbappe dribbling, Mbappe training, Mbappe Real Madrid 2026, "
        "Mbappe smiling, Mbappe celebration, Mbappe skills, Mbappe match, Mbappe kit, "
        "Mbappe action, Mbappe sprint, Mbappe free kick, Mbappe Champions League, "
        "Mbappe La Liga, Mbappe Bernabeu, Mbappe running"
    ),
    cover="Kylian Mbappe celebrating a goal for Real Madrid",
    positives=[
        "a real photograph of Kylian Mbappe",
        "a real photograph of Kylian Mbappe playing for Real Madrid",
        "a real photograph of Kylian Mbappe celebrating a goal",
    ],
)

# 28 OCT slot 3 (21:00) — Ronaldo (strongest slot, alternation flip from 27 Oct).
build(
    "batch_ronaldo_kvara_message.json",
    "batch_ronaldo_postecoglou_era.json",
    subject=(
        "Cristiano Ronaldo has returned to Al Nassr training after Portugal's exit from the 2026 "
        "World Cup, beginning his first season under new head coach Ange Postecoglou"
    ),
    beats=[
        {"says": "Cristiano Ronaldo is back in training.",
         "visual": "Cristiano Ronaldo arriving at Al Nassr's training ground",
         "images": ["Cristiano Ronaldo Al Nassr training 2026", "Ronaldo Al Nassr return training"]},
        {"says": "Portugal's World Cup ended without him lifting the trophy.",
         "visual": "Cristiano Ronaldo looking dejected in a Portugal shirt",
         "images": ["Ronaldo Portugal World Cup 2026 disappointed", "Ronaldo Portugal exit 2026"]},
        {"says": "Now he has returned to Saudi Arabia for a new era.",
         "visual": "Cristiano Ronaldo in Al Nassr kit",
         "images": ["Cristiano Ronaldo Al Nassr kit 2026", "Ronaldo Al Nassr portrait"]},
        {"says": "Al Nassr have a brand new head coach.",
         "visual": "A football manager giving instructions from the touchline",
         "images": ["Ange Postecoglou touchline", "Ange Postecoglou coaching 2026"]},
        {"says": "Ange Postecoglou is now in charge of Ronaldo's club.",
         "visual": "Ange Postecoglou talking to his players",
         "images": ["Ange Postecoglou team talk", "Postecoglou Al Nassr press conference"]},
        {"says": "It is Ronaldo's first season under a manager who has never managed him before.",
         "visual": "Cristiano Ronaldo training alone",
         "images": ["Cristiano Ronaldo training alone 2026", "Ronaldo gym training session"]},
        {"says": "At forty one, he is still expected to lead the line.",
         "visual": "Cristiano Ronaldo practicing his shooting",
         "images": ["Cristiano Ronaldo shooting practice 2026", "Ronaldo training shot"]},
        {"says": "Can this new era bring Ronaldo more silverware?",
         "visual": "Cristiano Ronaldo celebrating a goal for Al Nassr",
         "images": ["Cristiano Ronaldo Al Nassr goal celebration", "Ronaldo Al Nassr celebration 2026"]},
    ],
    hook="RONALDO'S NEW ERA BEGINS",
    cta="CAN POSTECOGLOU BRING RONALDO A TROPHY? 👇",
    terms=(
        "Cristiano Ronaldo, Ronaldo Al Nassr, Ronaldo Al Nassr training, "
        "Ronaldo Portugal World Cup, Ronaldo training alone, Ronaldo shooting practice, "
        "Ronaldo Al Nassr celebration, Ronaldo close up 2026, Ronaldo portrait, "
        "Ronaldo smiling, Ronaldo Al Nassr kit, Ronaldo running, Ronaldo celebration, "
        "Ronaldo Portugal, Ronaldo goal, Ronaldo Al Nassr 2026, Ronaldo match, "
        "Ronaldo serious, Ronaldo action, Ronaldo Saudi Arabia"
    ),
    cover="Cristiano Ronaldo in Al Nassr kit training",
    positives=[
        "a real photograph of Cristiano Ronaldo",
        "a real photograph of Cristiano Ronaldo playing for Al Nassr",
        "a real photograph of Cristiano Ronaldo training",
        "a real photograph of a football manager or head coach on the touchline",
    ],
)
