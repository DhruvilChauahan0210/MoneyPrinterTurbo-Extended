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


# 1 NOV slot 1 (13:00) — Messi. Alternation flips: Messi slot 1 / Ronaldo slot 3
# (31 Oct was Ronaldo slot1/Messi slot3).
# SWAPPED AGAIN — the MVP angle was blocked by the Jev duplicate gate (0.84 match against the
# existing messi_backtoback_bid topic). Landing on the jersey-sales angle, mirroring the Ronaldo
# jersey short's structure (which cleared fine) rather than another superlative "record" claim.
build(
    "batch_messi_playoff_debut.json",
    "batch_messi_bestselling_jersey.json",
    subject=(
        "Lionel Messi's Inter Miami jersey has become the best-selling jersey in MLS history, "
        "transforming the league's global reach since he signed"
    ),
    beats=[
        {"says": "One jersey changed Major League Soccer forever.",
         "visual": "Lionel Messi celebrating a goal for Inter Miami",
         "images": ["Messi goal celebration Inter Miami 2026", "Lionel Messi Inter Miami goal"]},
        {"says": "Lionel Messi's Inter Miami shirt is the best selling jersey in league history.",
         "visual": "Lionel Messi in Inter Miami kit looking serious",
         "images": ["Lionel Messi Inter Miami 2026 serious", "Messi Inter Miami portrait 2026"]},
        {"says": "Sales exploded the moment he signed in twenty twenty three.",
         "visual": "Lionel Messi celebrating with Inter Miami fans",
         "images": ["Messi Inter Miami fans celebration", "Messi Inter Miami crowd 2026"]},
        {"says": "Stadiums across the league sold out just to see him play.",
         "visual": "Inter Miami's stadium packed with fans",
         "images": ["Chase Stadium Inter Miami 2026", "Inter Miami stadium crowd"]},
        {"says": "At thirty nine, he is still the biggest draw in American soccer.",
         "visual": "Lionel Messi running with the ball",
         "images": ["Messi running Inter Miami 2026", "Messi dribble Inter Miami"]},
        {"says": "Kids across the country now wear his number everywhere.",
         "visual": "Lionel Messi celebrating with Inter Miami teammates",
         "images": ["Messi Inter Miami teammates celebration", "Messi Inter Miami team celebrate goal"]},
        {"says": "No signing has ever moved a league this fast.",
         "visual": "Lionel Messi smiling on the pitch",
         "images": ["Messi Inter Miami smiling 2026", "Lionel Messi happy Inter Miami"]},
        {"says": "How much bigger can Messi make this league before he retires?",
         "visual": "Lionel Messi pointing to the sky in celebration",
         "images": ["Messi pointing to the sky Inter Miami", "Messi celebration pointing up"]},
    ],
    hook="HE CHANGED THE LEAGUE FOREVER",
    cta="HOW MUCH BIGGER CAN HE MAKE IT? 👇",
    terms=(
        "Lionel Messi, Messi Inter Miami, Messi Inter Miami goal celebration, Messi Inter Miami 2026, "
        "Messi pointing to sky, Messi Inter Miami running, Messi Inter Miami training, Messi smiling Inter Miami, "
        "Messi close up, Messi portrait, Messi celebrating goal, Messi Inter Miami teammates, Messi dribbling, "
        "Messi Inter Miami fans, Messi stadium, Messi jersey"
    ),
    cover="Lionel Messi celebrating a goal for Inter Miami",
    positives=[
        "a real photograph of Lionel Messi",
        "a real photograph of Lionel Messi playing for Inter Miami",
        "a real photograph of Lionel Messi celebrating a goal",
    ],
)

# 1 NOV slot 3 (21:00) — Ronaldo (strongest slot).
build(
    "batch_ronaldo_1200_appearances.json",
    "batch_ronaldo_23years_pro.json",
    subject=(
        "Cristiano Ronaldo has now played professional football for over 23 years since his 2002 "
        "debut, a career spanning five different decades of his life"
    ),
    beats=[
        {"says": "Cristiano Ronaldo has been doing this for over twenty three years.",
         "visual": "Cristiano Ronaldo celebrating a goal for Al Nassr",
         "images": ["Cristiano Ronaldo Al Nassr goal celebration", "Ronaldo Al Nassr goal 2026"]},
        {"says": "His professional debut came all the way back in two thousand two.",
         "visual": "Cristiano Ronaldo in Al Nassr kit looking serious",
         "images": ["Cristiano Ronaldo Al Nassr serious 2026", "Ronaldo Al Nassr portrait"]},
        {"says": "Most of today's fans were not even born yet.",
         "visual": "Cristiano Ronaldo training",
         "images": ["Cristiano Ronaldo training 2026", "Ronaldo training session"]},
        {"says": "He has played under more than a dozen different managers.",
         "visual": "Cristiano Ronaldo running with the ball",
         "images": ["Cristiano Ronaldo running Al Nassr 2026", "Ronaldo dribble Al Nassr"]},
        {"says": "Across four countries and five different clubs.",
         "visual": "Cristiano Ronaldo pointing to the sky in celebration",
         "images": ["Cristiano Ronaldo celebration pointing sky", "Ronaldo Al Nassr trophy celebration"]},
        {"says": "And at forty one, he still starts every single week.",
         "visual": "Cristiano Ronaldo shooting the ball",
         "images": ["Cristiano Ronaldo shooting 2026", "Ronaldo shot on goal"]},
        {"says": "No one in the modern game has lasted this long at the top.",
         "visual": "Cristiano Ronaldo celebrating with Al Nassr teammates",
         "images": ["Cristiano Ronaldo teammates celebration", "Ronaldo Al Nassr team celebrate goal"]},
        {"says": "How much longer can this career possibly go on?",
         "visual": "Cristiano Ronaldo smiling on the pitch",
         "images": ["Cristiano Ronaldo smiling 2026", "Ronaldo happy celebration"]},
    ],
    hook="23 YEARS AND STILL GOING",
    cta="HOW MUCH LONGER CAN HE GO? 👇",
    terms=(
        "Cristiano Ronaldo, Ronaldo Al Nassr, Ronaldo close up 2026, Ronaldo portrait, Ronaldo training, "
        "Ronaldo Al Nassr kit, Ronaldo running, Ronaldo celebration, Ronaldo goal, Ronaldo Al Nassr 2026, "
        "Ronaldo match, Ronaldo serious, Ronaldo action, Ronaldo smiling, Ronaldo fans, Ronaldo teammates"
    ),
    cover="Cristiano Ronaldo celebrating a goal for Al Nassr",
    positives=[
        "a real photograph of Cristiano Ronaldo",
        "a real photograph of Cristiano Ronaldo playing for Al Nassr",
        "a real photograph of Cristiano Ronaldo celebrating a goal",
    ],
)
