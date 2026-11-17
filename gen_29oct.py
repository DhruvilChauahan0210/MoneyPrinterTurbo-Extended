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


# 29 OCT slot 1 (13:00) — Ronaldo. Alternation flips: Ronaldo slot 1 / Messi slot 3 (28 Oct was
# Messi slot1/Ronaldo slot3). LESSON from 28 Oct: when a script names a second real person
# (here, Sadio Mane), positives MUST include them too, or every beat about them starves the gate.
build(
    "batch_ronaldo_postecoglou_era.json",
    "batch_ronaldo_mane_partnership.json",
    subject=(
        "Cristiano Ronaldo and Sadio Mane's strike partnership continues to fire for Al Nassr in "
        "the Saudi Pro League this season, with both forwards scoring regularly together"
    ),
    beats=[
        {"says": "Al Nassr's front two are unstoppable right now.",
         "visual": "Cristiano Ronaldo and Sadio Mane celebrating together for Al Nassr",
         "images": ["Cristiano Ronaldo Sadio Mane celebration Al Nassr", "Ronaldo Mane Al Nassr goal celebration"]},
        {"says": "Cristiano Ronaldo and Sadio Mane keep scoring together.",
         "visual": "Cristiano Ronaldo celebrating a goal for Al Nassr",
         "images": ["Cristiano Ronaldo Al Nassr goal 2026", "Ronaldo Al Nassr celebration"]},
        {"says": "Two of the most decorated forwards in the world, on the same team.",
         "visual": "Sadio Mane in Al Nassr kit",
         "images": ["Sadio Mane Al Nassr 2026", "Sadio Mane Al Nassr portrait"]},
        {"says": "Ronaldo has five Champions Leagues.",
         "visual": "Cristiano Ronaldo holding the Champions League trophy",
         "images": ["Cristiano Ronaldo Champions League trophy", "Ronaldo Champions League celebration"]},
        {"says": "Mane has won it with Liverpool and lifted an AFCON title with Senegal.",
         "visual": "Sadio Mane celebrating for Senegal",
         "images": ["Sadio Mane Senegal celebration", "Sadio Mane AFCON trophy"]},
        {"says": "Now they are chasing trophies together in Saudi Arabia.",
         "visual": "Cristiano Ronaldo and Sadio Mane training together",
         "images": ["Ronaldo Mane training Al Nassr", "Cristiano Ronaldo Sadio Mane training"]},
        {"says": "Al Nassr fans are getting used to seeing both names on the scoresheet.",
         "visual": "Al Nassr fans celebrating in the stadium",
         "images": ["Al Nassr fans celebration 2026", "Al Nassr stadium crowd"]},
        {"says": "Can this strike partnership finally deliver a trophy for Al Nassr?",
         "visual": "Cristiano Ronaldo pointing to the sky in celebration",
         "images": ["Cristiano Ronaldo celebration pointing sky", "Ronaldo Al Nassr trophy celebration"]},
    ],
    hook="TWO LEGENDS, ONE ATTACK",
    cta="CAN THEY WIN AL NASSR A TROPHY? 👇",
    terms=(
        "Cristiano Ronaldo, Sadio Mane, Ronaldo Mane Al Nassr, Ronaldo Al Nassr, "
        "Sadio Mane Al Nassr, Ronaldo Al Nassr celebration, Mane celebration, "
        "Ronaldo close up 2026, Mane close up, Ronaldo portrait, Mane portrait, "
        "Ronaldo training, Mane training, Ronaldo goal, Mane goal, "
        "Ronaldo Saudi Arabia, Mane Senegal, Ronaldo smiling, Al Nassr celebration"
    ),
    cover="Cristiano Ronaldo and Sadio Mane celebrating together for Al Nassr",
    positives=[
        "a real photograph of Cristiano Ronaldo",
        "a real photograph of Cristiano Ronaldo playing for Al Nassr",
        "a real photograph of Sadio Mane",
        "a real photograph of Sadio Mane playing for Al Nassr",
    ],
)

# 29 OCT slot 2 (17:00) — free pick, Erling Haaland (single subject, deep proven photo pool;
# evergreen milestone angle with no date-dependency risk).
build(
    "batch_mbappe_madrid_goaltally.json",
    "batch_haaland_150goals.json",
    subject=(
        "Erling Haaland has now scored over 150 goals in all competitions for Manchester City "
        "since joining the club in 2022, reaching the mark faster than any player in club history"
    ),
    beats=[
        {"says": "Erling Haaland just passed a number that stuns even Manchester City fans.",
         "visual": "Erling Haaland celebrating a goal for Manchester City",
         "images": ["Erling Haaland goal celebration Man City 2026", "Haaland Manchester City goal"]},
        {"says": "He has now scored over one hundred fifty goals in all competitions for the club.",
         "visual": "Erling Haaland pointing to the sky in celebration",
         "images": ["Haaland celebration pointing sky", "Erling Haaland Man City celebration"]},
        {"says": "He only joined Manchester City in twenty twenty two.",
         "visual": "Erling Haaland in Manchester City kit looking serious",
         "images": ["Erling Haaland Man City portrait 2026", "Haaland Manchester City serious close up"]},
        {"says": "No player has ever reached that mark faster for the club.",
         "visual": "Manchester City's Etihad Stadium",
         "images": ["Etihad Stadium Manchester City 2026", "Man City stadium exterior"]},
        {"says": "He is already being compared to the greatest number nines in Premier League history.",
         "visual": "Erling Haaland running with the ball",
         "images": ["Haaland dribble Man City 2026", "Erling Haaland running with ball"]},
        {"says": "Defenders still have no answer for him.",
         "visual": "Erling Haaland shooting the ball",
         "images": ["Haaland shooting Man City 2026", "Erling Haaland shot on goal"]},
        {"says": "Manchester City built their entire attack around him.",
         "visual": "Erling Haaland celebrating with Manchester City teammates",
         "images": ["Haaland teammates celebration Man City", "Erling Haaland Man City team celebrate"]},
        {"says": "How many more records can he break before he turns thirty?",
         "visual": "Erling Haaland smiling on the pitch",
         "images": ["Haaland smiling Man City 2026", "Erling Haaland happy celebration"]},
    ],
    hook="150 GOALS AND JUST GETTING STARTED",
    cta="HOW MANY RECORDS CAN HE BREAK? 👇",
    terms=(
        "Erling Haaland, Haaland Manchester City, Haaland goal celebration, Haaland close up, "
        "Haaland portrait, Haaland dribbling, Haaland training, Haaland Man City 2026, "
        "Haaland smiling, Haaland celebration, Haaland skills, Haaland match, Haaland kit, "
        "Haaland action, Haaland sprint, Haaland shooting, Haaland Premier League, "
        "Haaland Etihad, Haaland running, Haaland Norway"
    ),
    cover="Erling Haaland celebrating a goal for Manchester City",
    positives=[
        "a real photograph of Erling Haaland",
        "a real photograph of Erling Haaland playing for Manchester City",
        "a real photograph of Erling Haaland celebrating a goal",
    ],
)

# 29 OCT slot 3 (21:00) — Messi (strongest slot). Fresh angle: title-defense / individual-award
# narrative, distinct from the already-covered NYCFC-clinch stat line (batch_messi_nycfc_playoffs).
build(
    "batch_messi_miami100goals.json",
    "batch_messi_backtoback_bid.json",
    subject=(
        "Inter Miami enter the 2026 MLS Cup playoffs as the top seed and defending champions, with "
        "Lionel Messi chasing a third straight MVP award and a second straight Golden Boot"
    ),
    beats=[
        {"says": "Inter Miami are not just chasing a title.",
         "visual": "Lionel Messi in Inter Miami kit looking serious",
         "images": ["Lionel Messi Inter Miami serious 2026", "Messi Inter Miami portrait"]},
        {"says": "They are defending one.",
         "visual": "Lionel Messi celebrating with a trophy",
         "images": ["Messi Inter Miami trophy celebration", "Messi MLS Cup celebration"]},
        {"says": "Inter Miami enter the playoffs as the top seed.",
         "visual": "Inter Miami's stadium before a match",
         "images": ["Chase Stadium Inter Miami 2026", "Inter Miami stadium crowd"]},
        {"says": "No team has won back to back MLS Cups since twenty eleven.",
         "visual": "Lionel Messi running on the pitch for Inter Miami",
         "images": ["Messi Inter Miami sprint 2026", "Messi Inter Miami running"]},
        {"says": "Messi is chasing a third straight MVP award.",
         "visual": "Lionel Messi dribbling past a defender",
         "images": ["Messi dribble Inter Miami 2026", "Messi skill move Inter Miami"]},
        {"says": "And a second straight Golden Boot.",
         "visual": "Lionel Messi celebrating a goal for Inter Miami",
         "images": ["Messi goal celebration Inter Miami 2026", "Lionel Messi Inter Miami goal"]},
        {"says": "At thirty nine, he is still the best player on the field every single week.",
         "visual": "Lionel Messi celebrating with Inter Miami teammates",
         "images": ["Messi Inter Miami teammates celebration", "Messi Inter Miami team celebrate goal"]},
        {"says": "Can he lead Miami to history?",
         "visual": "Lionel Messi pointing to the sky in celebration",
         "images": ["Messi pointing to the sky Inter Miami", "Messi celebration pointing up"]},
    ],
    hook="CAN MIAMI MAKE HISTORY?",
    cta="WILL MESSI WIN BACK TO BACK TITLES? 👇",
    terms=(
        "Lionel Messi, Messi Inter Miami, Messi Inter Miami goal celebration, "
        "Messi Inter Miami 2026, Messi pointing to sky, Messi Inter Miami running, "
        "Messi Inter Miami training, Messi trophy, Messi Inter Miami teammates, "
        "Messi smiling Inter Miami, Messi close up, Messi portrait, Messi celebrating goal, "
        "Messi free kick, Messi warm up, Messi Miami fans, Messi MLS, Messi playoffs"
    ),
    cover="Lionel Messi celebrating with a trophy",
    positives=[
        "a real photograph of Lionel Messi",
        "a real photograph of Lionel Messi playing for Inter Miami",
        "a real photograph of Lionel Messi celebrating a goal",
    ],
)
