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


# 31 OCT slot 1 (13:00) — Ronaldo. Alternation flips: Ronaldo slot 1 / Messi slot 3
# (30 Oct was Messi slot1/Ronaldo slot3).
# SWAPPED after 3 straight fails on the "never misses a match / durability" angle (consistently
# 17-20 downloads but never enough survived the gate) — same recipe as the Messi salary swap.
build(
    "batch_ronaldo_bestselling_jersey.json",
    "batch_ronaldo_1200_appearances.json",
    subject=(
        "Cristiano Ronaldo has made over 1,200 career appearances, more than any outfield player "
        "in football history"
    ),
    beats=[
        {"says": "One number separates Cristiano Ronaldo from every outfield player ever.",
         "visual": "Cristiano Ronaldo celebrating a goal for Al Nassr",
         "images": ["Cristiano Ronaldo Al Nassr goal celebration", "Ronaldo Al Nassr goal 2026"]},
        {"says": "Over twelve hundred career appearances.",
         "visual": "Cristiano Ronaldo pointing to the sky in celebration",
         "images": ["Cristiano Ronaldo celebration pointing sky", "Ronaldo Al Nassr trophy celebration"]},
        {"says": "More than any outfield player in the history of the sport.",
         "visual": "Cristiano Ronaldo in Al Nassr kit looking serious",
         "images": ["Cristiano Ronaldo Al Nassr serious 2026", "Ronaldo Al Nassr portrait"]},
        {"says": "Manchester United, Real Madrid, Juventus, and now Al Nassr.",
         "visual": "Cristiano Ronaldo training",
         "images": ["Cristiano Ronaldo training 2026", "Ronaldo training session"]},
        {"says": "At forty one, he is still adding to the total every single week.",
         "visual": "Cristiano Ronaldo running with the ball",
         "images": ["Cristiano Ronaldo running Al Nassr 2026", "Ronaldo dribble Al Nassr"]},
        {"says": "No injury, no club change has ever slowed him down for long.",
         "visual": "Cristiano Ronaldo celebrating with Al Nassr teammates",
         "images": ["Cristiano Ronaldo teammates celebration", "Ronaldo Al Nassr team celebrate goal"]},
        {"says": "It is a record that may never be broken.",
         "visual": "Cristiano Ronaldo shooting the ball",
         "images": ["Cristiano Ronaldo shooting 2026", "Ronaldo shot on goal"]},
        {"says": "How many more appearances before he finally stops?",
         "visual": "Cristiano Ronaldo smiling on the pitch",
         "images": ["Cristiano Ronaldo smiling 2026", "Ronaldo happy celebration"]},
    ],
    hook="A RECORD THAT MAY NEVER BE BROKEN",
    cta="HOW MANY MORE BEFORE HE STOPS? 👇",
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

# 31 OCT slot 2 (17:00) — free pick, back to NORMAL under the alternation (30 Oct was What-If).
# Neymar: extended his Santos deal through end of 2026 and has hinted at retiring when it ends.
build(
    "batch_mbappe_madrid_goaltally.json",
    "batch_neymar_santos_retirement_hint.json",
    subject=(
        "Neymar extended his Santos contract through the end of 2026 and has hinted he may retire "
        "once it expires, saying he is living year to year now"
    ),
    beats=[
        {"says": "Neymar just made a decision that could end his career.",
         "visual": "Neymar in Santos kit looking serious",
         "images": ["Neymar Santos 2026 serious", "Neymar Santos portrait"]},
        {"says": "He extended his contract with Santos through the end of twenty twenty six.",
         "visual": "Neymar celebrating a goal for Santos",
         "images": ["Neymar Santos goal celebration 2026", "Neymar Santos goal"]},
        {"says": "His boyhood club, where it all began.",
         "visual": "Santos stadium Vila Belmiro",
         "images": ["Vila Belmiro stadium Santos", "Santos FC stadium 2026"]},
        {"says": "But Neymar himself admits he is living year to year now.",
         "visual": "Neymar looking thoughtful on the bench",
         "images": ["Neymar thoughtful bench Santos", "Neymar pensive Santos 2026"]},
        {"says": "He said that when December comes, he might want to retire.",
         "visual": "Neymar walking off the pitch",
         "images": ["Neymar walking off pitch Santos", "Neymar Santos leaving field"]},
        {"says": "A recent injury has only added to the uncertainty.",
         "visual": "Neymar receiving treatment on the sideline",
         "images": ["Neymar injury treatment Santos", "Neymar sideline Santos 2026"]},
        {"says": "One of the most gifted players of his generation, running out of time.",
         "visual": "Neymar dribbling past a defender",
         "images": ["Neymar dribble Santos 2026", "Neymar skill move Santos"]},
        {"says": "Could this really be Neymar's final season?",
         "visual": "Neymar smiling with Santos teammates",
         "images": ["Neymar Santos teammates smiling", "Neymar Santos celebration 2026"]},
    ],
    hook="HIS FINAL SEASON?",
    cta="IS THIS REALLY THE END? 👇",
    terms=(
        "Neymar, Neymar Santos, Neymar Santos 2026, Neymar goal celebration, Neymar close up, "
        "Neymar portrait, Neymar training, Neymar Santos kit, Neymar smiling, Neymar celebration, "
        "Neymar Brazil, Neymar dribbling, Neymar bench, Neymar Vila Belmiro, Neymar injury, Neymar sad"
    ),
    cover="Neymar in Santos kit looking serious",
    positives=[
        "a real photograph of Neymar",
        "a real photograph of Neymar playing for Santos",
        "a real photograph of Neymar celebrating a goal",
    ],
)

# 31 OCT slot 3 (21:00) — Messi (strongest slot).
build(
    "batch_messi_assist_record.json",
    "batch_messi_playoff_debut.json",
    subject=(
        "Lionel Messi made his first-ever MLS Cup playoff appearance for Inter Miami, the reigning "
        "champions entering the postseason as the top seed"
    ),
    beats=[
        {"says": "Lionel Messi just played a game he had never played before.",
         "visual": "Lionel Messi in Inter Miami kit looking serious",
         "images": ["Lionel Messi Inter Miami 2026 serious", "Messi Inter Miami portrait 2026"]},
        {"says": "His first ever MLS Cup playoff match.",
         "visual": "Lionel Messi running onto the pitch",
         "images": ["Messi Inter Miami walkout 2026", "Messi Inter Miami entrance"]},
        {"says": "Inter Miami enter as the top seed and defending champions.",
         "visual": "Inter Miami's stadium packed with fans",
         "images": ["Chase Stadium Inter Miami 2026", "Inter Miami stadium crowd"]},
        {"says": "At thirty nine, this is new territory even for him.",
         "visual": "Lionel Messi celebrating a goal for Inter Miami",
         "images": ["Messi goal celebration Inter Miami 2026", "Lionel Messi Inter Miami goal"]},
        {"says": "No team has repeated as MLS Cup champion since twenty eleven.",
         "visual": "Lionel Messi dribbling past a defender",
         "images": ["Messi dribble Inter Miami 2026", "Messi skill move Inter Miami"]},
        {"says": "Messi has carried this franchise from nothing to the top of the league.",
         "visual": "Lionel Messi celebrating with Inter Miami teammates",
         "images": ["Messi Inter Miami teammates celebration", "Messi Inter Miami team celebrate goal"]},
        {"says": "Now the biggest stage of his MLS career is here.",
         "visual": "Lionel Messi pointing to the sky in celebration",
         "images": ["Messi pointing to the sky Inter Miami", "Messi celebration pointing up"]},
        {"says": "Can Messi deliver back to back MLS Cups?",
         "visual": "Lionel Messi smiling on the pitch",
         "images": ["Messi Inter Miami smiling 2026", "Lionel Messi happy Inter Miami"]},
    ],
    hook="HIS FIRST EVER PLAYOFF GAME",
    cta="CAN HE DO IT BACK TO BACK? 👇",
    terms=(
        "Lionel Messi, Messi Inter Miami, Messi Inter Miami goal celebration, Messi Inter Miami 2026, "
        "Messi pointing to sky, Messi Inter Miami running, Messi Inter Miami training, Messi smiling Inter Miami, "
        "Messi close up, Messi portrait, Messi celebrating goal, Messi Inter Miami stadium crowd, "
        "Messi Inter Miami teammates, Messi dribbling, Messi playoffs, Messi MLS Cup"
    ),
    cover="Lionel Messi celebrating a goal for Inter Miami",
    positives=[
        "a real photograph of Lionel Messi",
        "a real photograph of Lionel Messi playing for Inter Miami",
        "a real photograph of Lionel Messi celebrating a goal",
    ],
)
