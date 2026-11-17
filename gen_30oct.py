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


# 30 OCT slot 1 (13:00) — Messi. Alternation flips: Messi slot 1 / Ronaldo slot 3
# (29 Oct was Ronaldo slot1/Messi slot3).
# SWAPPED from the salary/earnings angle after 5 straight hard fails (consistently capped at
# 18 raw downloads no matter how many search terms were tried — that framing just doesn't have
# strong matching imagery). Back to a proven goal-celebration/milestone style, same visual
# recipe as the successful 100-goals and back-to-back-bid builds.
build(
    "batch_messi_backtoback_bid.json",
    "batch_messi_assist_record.json",
    subject=(
        "Lionel Messi has broken the MLS single-season assist record this year, adding another "
        "milestone to his Inter Miami trophy case at age 39"
    ),
    beats=[
        {"says": "Lionel Messi just broke another record nobody saw coming.",
         "visual": "Lionel Messi celebrating a goal for Inter Miami",
         "images": ["Messi goal celebration Inter Miami 2026", "Lionel Messi Inter Miami goal"]},
        {"says": "He now holds the MLS single season assist record.",
         "visual": "Lionel Messi pointing to the sky after an assist",
         "images": ["Messi pointing to the sky Inter Miami", "Messi celebration pointing up"]},
        {"says": "At thirty nine, most players are watching from the bench.",
         "visual": "Lionel Messi running with the ball for Inter Miami",
         "images": ["Messi running Inter Miami 2026", "Messi dribble Inter Miami"]},
        {"says": "Messi is still rewriting the league's record books.",
         "visual": "Lionel Messi dribbling past a defender",
         "images": ["Messi skill move Inter Miami", "Messi dribble skill 2026"]},
        {"says": "Inter Miami's stadium has never been louder.",
         "visual": "Inter Miami's stadium packed with fans",
         "images": ["Chase Stadium Inter Miami 2026", "Inter Miami stadium crowd"]},
        {"says": "Every pass he makes seems to find the back of the net.",
         "visual": "Lionel Messi celebrating with Inter Miami teammates",
         "images": ["Messi Inter Miami teammates celebration", "Messi Inter Miami team celebrate goal"]},
        {"says": "He had already retired from Argentina and hinted his career could end soon.",
         "visual": "Lionel Messi waving in an Argentina shirt",
         "images": ["Messi Argentina farewell wave", "Messi Argentina last match goodbye"]},
        {"says": "How many more records can he break before he walks away?",
         "visual": "Lionel Messi smiling on the pitch",
         "images": ["Messi Inter Miami smiling 2026", "Lionel Messi happy Inter Miami"]},
    ],
    hook="ANOTHER RECORD JUST FELL",
    cta="HOW MANY MORE CAN HE BREAK? 👇",
    terms=(
        "Lionel Messi, Messi Inter Miami, Messi Inter Miami goal celebration, Messi Inter Miami 2026, "
        "Messi pointing to sky, Messi Inter Miami running, Messi Inter Miami training, Messi smiling Inter Miami, "
        "Messi close up, Messi portrait, Messi celebrating goal, Messi Inter Miami stadium crowd, "
        "Messi Inter Miami teammates, Messi dribbling, Messi Argentina, Messi assist"
    ),
    cover="Lionel Messi celebrating a goal for Inter Miami",
    positives=[
        "a real photograph of Lionel Messi",
        "a real photograph of Lionel Messi playing for Inter Miami",
        "a real photograph of Lionel Messi celebrating a goal",
    ],
)

# 30 OCT slot 3 (21:00) — Ronaldo (strongest slot).
build(
    "batch_ronaldo_mane_partnership.json",
    "batch_ronaldo_bestselling_jersey.json",
    subject=(
        "Cristiano Ronaldo's shirt remains the best-selling football jersey in the world, a record "
        "he has held across Manchester United, Real Madrid, Juventus and Al Nassr for over a decade"
    ),
    beats=[
        {"says": "One football shirt has outsold every other for over a decade.",
         "visual": "Cristiano Ronaldo in Al Nassr kit celebrating",
         "images": ["Cristiano Ronaldo Al Nassr celebration 2026", "Ronaldo Al Nassr goal celebration"]},
        {"says": "Cristiano Ronaldo's jersey is still the best seller on the planet.",
         "visual": "Cristiano Ronaldo close up smiling",
         "images": ["Cristiano Ronaldo close up 2026", "Ronaldo portrait smiling"]},
        {"says": "It has topped the charts at Manchester United, Real Madrid, and Juventus.",
         "visual": "Cristiano Ronaldo training",
         "images": ["Cristiano Ronaldo training 2026", "Ronaldo training session"]},
        {"says": "Now it is happening all over again in Saudi Arabia.",
         "visual": "Cristiano Ronaldo in Al Nassr kit running",
         "images": ["Cristiano Ronaldo Al Nassr running", "Ronaldo Al Nassr action 2026"]},
        {"says": "At forty one, he still outsells players half his age.",
         "visual": "Cristiano Ronaldo celebrating with fans",
         "images": ["Cristiano Ronaldo fans celebration", "Ronaldo Al Nassr fans 2026"]},
        {"says": "No retro legend, no young superstar has ever caught him.",
         "visual": "Cristiano Ronaldo shooting the ball",
         "images": ["Cristiano Ronaldo shooting 2026", "Ronaldo shot on goal"]},
        {"says": "His name alone still moves more shirts than anyone in the sport.",
         "visual": "Cristiano Ronaldo smiling on the pitch",
         "images": ["Cristiano Ronaldo smiling 2026", "Ronaldo happy celebration"]},
        {"says": "Is Ronaldo still the biggest name in football?",
         "visual": "Cristiano Ronaldo pointing to the sky in celebration",
         "images": ["Cristiano Ronaldo celebration pointing sky", "Ronaldo Al Nassr trophy celebration"]},
    ],
    hook="STILL #1 AFTER ALL THESE YEARS",
    cta="IS HE STILL THE BIGGEST NAME IN FOOTBALL? 👇",
    terms=(
        "Cristiano Ronaldo, Ronaldo Al Nassr, Ronaldo close up 2026, Ronaldo portrait, Ronaldo smiling, "
        "Ronaldo training, Ronaldo Al Nassr kit, Ronaldo running, Ronaldo celebration, Ronaldo Saudi Arabia, "
        "Ronaldo goal, Ronaldo Al Nassr 2026, Ronaldo match, Ronaldo serious, Ronaldo action, Ronaldo fans"
    ),
    cover="Cristiano Ronaldo in Al Nassr kit celebrating",
    positives=[
        "a real photograph of Cristiano Ronaldo",
        "a real photograph of Cristiano Ronaldo playing for Al Nassr",
        "a real photograph of Cristiano Ronaldo celebrating a goal",
    ],
)
