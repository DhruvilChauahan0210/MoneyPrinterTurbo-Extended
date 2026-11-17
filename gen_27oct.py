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


build(
    "batch_ronaldo_alnassr_stake.json",
    "batch_ronaldo_kvara_message.json",
    subject=(
        "Cristiano Ronaldo publicly sent Khvicha Kvaratskhelia a message of support after the PSG "
        "winger ruptured his ACL in the Champions League win over Barcelona"
    ),
    beats=[
        {"says": "Khvicha Kvaratskhelia tore his ACL against Barcelona.",
         "visual": "Khvicha Kvaratskhelia injured on the ground in a PSG shirt",
         "images": ["Kvaratskhelia injury PSG Barcelona October 2026", "Kvaratskhelia injured knee PSG"]},
        {"says": "He said he prayed before every match to leave the pitch safely,",
         "visual": "Khvicha Kvaratskhelia looking emotional in PSG kit",
         "images": ["Kvaratskhelia emotional PSG", "Kvaratskhelia sad PSG 2026"]},
        {"says": "and asked one question: why me?",
         "visual": "close up of Khvicha Kvaratskhelia looking down",
         "images": ["Kvaratskhelia close up PSG", "Khvicha Kvaratskhelia portrait"]},
        {"says": "Then his idol answered.",
         "visual": "close up of Cristiano Ronaldo looking intense",
         "images": ["Cristiano Ronaldo close up 2026", "Cristiano Ronaldo portrait serious"]},
        {"says": "Cristiano Ronaldo wrote that the toughest battles in football are often the ones nobody sees.",
         "visual": "Cristiano Ronaldo training alone in the gym",
         "images": ["Cristiano Ronaldo injury recovery gym", "Cristiano Ronaldo training alone"]},
        {"says": "He told Kvara not to let a difficult moment make him doubt how far he can go.",
         "visual": "Cristiano Ronaldo and Khvicha Kvaratskhelia together",
         "images": ["Ronaldo Kvaratskhelia", "Ronaldo Kvaratskhelia Portugal Georgia Euro 2024"]},
        {"says": "PSG say surgery will happen in the coming days.",
         "visual": "Khvicha Kvaratskhelia in PSG kit at the Parc des Princes",
         "images": ["Kvaratskhelia PSG Parc des Princes 2026", "Kvaratskhelia PSG Champions League"]},
        {"says": "Can Kvara come back even stronger?",
         "visual": "Khvicha Kvaratskhelia celebrating a goal for PSG",
         "images": ["Kvaratskhelia goal celebration PSG", "Kvaratskhelia Champions League final celebration"]},
    ],
    hook="THE MESSAGE HE NEEDED MOST",
    cta="CAN KVARA COME BACK STRONGER? 👇",
    terms=(
        "Ronaldo message Kvaratskhelia ACL injury, Kvaratskhelia ACL PSG Barcelona, "
        "Ronaldo toughest battles nobody sees"
    ),
    cover="Khvicha Kvaratskhelia injured and emotional in PSG kit",
    positives=[
        "a real photograph of Cristiano Ronaldo",
        "a real photograph of Khvicha Kvaratskhelia playing for PSG",
        "a real photograph of Khvicha Kvaratskhelia",
    ],
)

build(
    "batch_yamal_mbappe_teen_record.json",
    "batch_kane_ronaldo_streak.json",
    subject=(
        "Harry Kane scored in his 10th consecutive Champions League match against Arsenal, one short "
        "of Cristiano Ronaldo's record of 11 straight from 2017-18"
    ),
    beats=[
        {"says": "One Champions League record has belonged to Cristiano Ronaldo since 2018.",
         "visual": "Cristiano Ronaldo celebrating a Champions League goal for Real Madrid",
         "images": ["Cristiano Ronaldo Real Madrid Champions League 2018 celebration", "Ronaldo Real Madrid 2018 goal"]},
        {"says": "Harry Kane is now one game away from it.",
         "visual": "close up of Harry Kane in Bayern Munich kit",
         "images": ["Harry Kane Bayern close up 2026", "Harry Kane Bayern Munich portrait"]},
        {"says": "His penalty against Arsenal made it ten straight Champions League matches with a goal.",
         "visual": "Harry Kane taking a penalty for Bayern against Arsenal",
         "images": ["Harry Kane penalty Arsenal Bayern October 2026", "Kane Bayern Arsenal Champions League 2026"]},
        {"says": "Only Ronaldo has ever gone longer,",
         "visual": "Cristiano Ronaldo in Real Madrid white kit",
         "images": ["Cristiano Ronaldo Real Madrid Champions League 2017", "Ronaldo Real Madrid Juventus 2018"]},
        {"says": "with eleven in a row for Real Madrid.",
         "visual": "Cristiano Ronaldo with the Champions League trophy",
         "images": ["Ronaldo Champions League trophy 2018 Kiev", "Ronaldo Real Madrid Champions League trophy"]},
        {"says": "Kane is thirty-three, and that goal was his fifty-eighth in the competition.",
         "visual": "Harry Kane celebrating a goal for Bayern Munich",
         "images": ["Harry Kane celebration Bayern Champions League", "Harry Kane goal celebration Bayern 2026"]},
        {"says": "Bayern travel to Atlético Madrid next.",
         "visual": "Atletico Madrid stadium Metropolitano",
         "images": ["Atletico Madrid Metropolitano stadium", "Bayern Atletico Madrid Champions League"]},
        {"says": "If Kane scores there, he matches Ronaldo.",
         "visual": "Harry Kane and Cristiano Ronaldo",
         "images": ["Harry Kane Cristiano Ronaldo", "Kane Ronaldo England Portugal"]},
        {"says": "Will Kane take Ronaldo's record?",
         "visual": "Harry Kane looking determined",
         "images": ["Harry Kane determined Bayern", "Harry Kane Bayern Munich 2026"]},
    ],
    hook="KANE IS COMING FOR CR7",
    cta="WILL KANE TAKE IT? 👇",
    terms=(
        "Harry Kane 10 consecutive Champions League games, Kane Ronaldo record 11 straight, "
        "Kane penalty Arsenal Bayern October 2026"
    ),
    cover="Harry Kane celebrating a Champions League goal for Bayern",
    positives=[
        "a real photograph of Harry Kane playing for Bayern Munich",
        "a real photograph of Cristiano Ronaldo playing for Real Madrid",
        "a real photograph of Harry Kane celebrating a goal",
    ],
)

build(
    "batch_messi_asturias_award.json",
    "batch_messi_1000_prediction.json",
    subject=(
        "Inter Miami coach Kily Gonzalez said Lionel Messi will reach 1,000 career goals; Messi has 936 "
        "and has hinted at retiring sooner rather than later"
    ),
    beats=[
        {"says": "Messi's manager has made a bold prediction.",
         "visual": "Lionel Messi in Inter Miami pink kit looking intense",
         "images": ["Lionel Messi Inter Miami 2026 close up", "Messi Inter Miami intense"]},
        {"says": "Inter Miami coach Kily González says Messi will reach one thousand career goals.",
         "visual": "Inter Miami coach Kily Gonzalez on the touchline",
         "images": ["Kily Gonzalez Inter Miami coach", "Cristian Gonzalez Inter Miami head coach 2026"]},
        {"says": "He has nine hundred and thirty-six,",
         "visual": "Lionel Messi celebrating a goal for Inter Miami",
         "images": ["Messi goal celebration Inter Miami 2026", "Messi celebrates Inter Miami goal"]},
        {"says": "so he still needs sixty-four.",
         "visual": "Lionel Messi shooting the ball",
         "images": ["Messi shooting Inter Miami", "Messi free kick Inter Miami 2026"]},
        {"says": "At thirty-nine, he leads MLS with twenty-five goals,",
         "visual": "Lionel Messi scoring against Atlanta United",
         "images": ["Messi Atlanta United October 2026 goal", "Messi Inter Miami Atlanta 2026"]},
        {"says": "and he has a goal or assist in thirteen straight matches.",
         "visual": "Lionel Messi celebrating with Inter Miami teammates",
         "images": ["Messi De Paul Inter Miami celebration", "Messi Inter Miami teammates celebrate 2026"]},
        {"says": "But he has already retired from Argentina,",
         "visual": "Lionel Messi waving goodbye in an Argentina shirt",
         "images": ["Messi Argentina farewell Benin October 2026", "Messi last game Argentina goodbye"]},
        {"says": "and he has hinted his career could end sooner rather than later.",
         "visual": "Lionel Messi looking thoughtful",
         "images": ["Messi thoughtful Inter Miami", "Lionel Messi pensive 2026"]},
        {"says": "Can Messi still reach one thousand?",
         "visual": "Lionel Messi pointing to the sky",
         "images": ["Messi pointing to the sky Inter Miami", "Messi celebration pointing up"]},
    ],
    hook="CAN MESSI STILL DO THIS?",
    cta="WILL MESSI HIT 1,000? 👇",
    terms=(
        "Messi 1000 goals prediction Kily Gonzalez, Messi 936 career goals, Messi 25 MLS goals 2026"
    ),
    cover="Lionel Messi celebrating a goal for Inter Miami",
    positives=[
        "a real photograph of Lionel Messi",
        "a real photograph of Lionel Messi playing for Inter Miami",
        "a real photograph of Lionel Messi celebrating a goal",
    ],
)
