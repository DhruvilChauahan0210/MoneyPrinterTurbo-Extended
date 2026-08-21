#!/usr/bin/env python3
"""Generate the 9 batch configs for 25-27 Aug 2026 (3 shorts/day, voiceover, no BGM).

Same render settings as the 30 shorts already shipped (imports from gen_15to21aug).
Emits run_25to27aug.sh with the 25-min per-build watchdog and Desktop-skip.
"""
import json
import os

from gen_15to21aug import PLAYERS, build, cover
from gen_22to24aug import RUN_TEMPLATE, SLOT_TIMES

# --- extra player visual profiles (slot-2 stars, no prior batch coverage) ---
PLAYERS["pogba"] = {
    "positives": [
        "a real photograph of Paul Pogba the footballer",
        "Paul Pogba in a red Manchester United jersey",
        "Paul Pogba in a blue France jersey",
        "a tight close up of Paul Pogba's face",
        "Paul Pogba celebrating a goal close up",
    ],
    "queries": [
        "Paul Pogba Manchester United close up face serious",
        "Paul Pogba France close up face",
        "Paul Pogba Juventus close up face",
        "Paul Pogba goal celebration close up slow motion",
        "Paul Pogba skills close up slow motion",
        "Paul Pogba walking on pitch close up",
    ],
    "cover": cover("Paul Pogba"),
    "terms": "Paul Pogba, Pogba Manchester United, Pogba Juventus, Pogba France, Pogba close up face",
}

PLAYERS["ramos"] = {
    "positives": [
        "a real photograph of Sergio Ramos the footballer",
        "Sergio Ramos in a white Real Madrid jersey",
        "Sergio Ramos in a red Spain jersey",
        "a tight close up of Sergio Ramos's bearded face",
        "Sergio Ramos arguing with a referee close up",
    ],
    "queries": [
        "Sergio Ramos Real Madrid close up face serious",
        "Sergio Ramos red card close up",
        "Sergio Ramos Spain close up face",
        "Sergio Ramos header goal celebration close up",
        "Sergio Ramos tackle close up slow motion",
        "Sergio Ramos lifting Champions League trophy close up",
    ],
    "cover": cover("Sergio Ramos", "intense and aggressive"),
    "terms": "Sergio Ramos, Ramos Real Madrid, Ramos Spain, Ramos red card, Ramos close up face",
}

PLAYERS["trent"] = {
    "positives": [
        "a real photograph of Trent Alexander-Arnold the footballer",
        "Trent Alexander-Arnold in a red Liverpool jersey",
        "a tight close up of Trent Alexander-Arnold's face",
        "Trent Alexander-Arnold taking a corner kick close up",
        "Trent Alexander-Arnold celebrating close up",
    ],
    "queries": [
        "Trent Alexander-Arnold Liverpool close up face serious",
        "Trent Alexander-Arnold corner taken quickly Barcelona 2019",
        "Trent Alexander-Arnold crossing close up slow motion",
        "Trent Alexander-Arnold free kick close up",
        "Trent Alexander-Arnold celebration close up slow motion",
        "Trent Alexander-Arnold England close up face",
    ],
    "cover": cover("Trent Alexander-Arnold"),
    "terms": "Trent Alexander-Arnold, Trent Liverpool, corner taken quickly, Trent close up face, Trent assists",
}

MESSI_ARGENTINA = {
    "queries": [
        "Lionel Messi Argentina World Cup 2022 celebration close up",
        "Lionel Messi Argentina close up face serious",
        "Lionel Messi Argentina lifting World Cup trophy close up",
        "Lionel Messi Argentina celebration close up slow motion",
        "Lionel Messi Argentina dribbling close up",
        "Lionel Messi Argentina walking on pitch close up",
    ]
}

RONALDO_PORTUGAL_YOUNG = {
    "positives": [
        "a real photograph of Cristiano Ronaldo the footballer",
        "young Cristiano Ronaldo in a red Portugal jersey",
        "a tight close up of young Cristiano Ronaldo's face",
        "Cristiano Ronaldo crying on the pitch close up",
        "Cristiano Ronaldo celebrating close up",
    ],
    "queries": [
        "young Cristiano Ronaldo Euro 2004 final Greece crying",
        "young Cristiano Ronaldo Portugal close up face",
        "Cristiano Ronaldo Euro 2016 trophy celebration close up",
        "Cristiano Ronaldo Portugal celebration close up slow motion",
        "young Cristiano Ronaldo Portugal dribbling close up",
        "Cristiano Ronaldo Portugal close up face serious",
    ],
    "cover": cover("young Cristiano Ronaldo", "emotional and serious"),
}

RONALDO_PORTUGAL = {
    "queries": [
        "Cristiano Ronaldo Portugal free kick Spain 2018 World Cup",
        "Cristiano Ronaldo Portugal close up face serious",
        "Cristiano Ronaldo Portugal celebration close up slow motion",
        "Cristiano Ronaldo Portugal hat trick celebration close up",
        "Cristiano Ronaldo Portugal dribbling close up",
        "Cristiano Ronaldo Portugal walking on pitch close up",
    ]
}

TOPICS = [
    ("messi_helicopter", "messi", "5 MILLION BLOCKED THEM \U0001F92F", "BIGGEST PARTY EVER? \U0001F447",
     "Argentina's 2022 World Cup parade drew around five million people who flooded the roads and blocked the team bus, so the players had to be lifted off the route by helicopter",
     "Argentina's World Cup parade was so big that five million people flooded the streets and blocked the bus. The players had to be airlifted out. Which makes you wonder,",
     MESSI_ARGENTINA),
    ("pogba_ban", "pogba", "BANNED FOR FOUR YEARS \U0001F633", "DESERVED OR TOO HARSH? \U0001F447",
     "Paul Pogba was banned from football for four years after a positive doping test, said he considered quitting the game entirely, and the ban was later cut to eighteen months on appeal",
     "Pogba was banned from football for four years for doping and said he thought about quitting. The ban was cut to eighteen months. Which makes you wonder,",
     None),
    ("ronaldo_euro2004", "ronaldo", "HE CRIED ON THE PITCH \U0001F62D", "BEST COMEBACK STORY? \U0001F447",
     "At nineteen Cristiano Ronaldo lost the Euro 2004 final on home soil to Greece and cried on the pitch, and twelve years later he captained Portugal to win the Euros",
     "At nineteen, Ronaldo lost the Euro final at home to Greece and cried on the pitch. Twelve years later he came back and won it. Which makes you wonder,",
     RONALDO_PORTUGAL_YOUNG),
    ("ronaldo_spain_hattrick", "ronaldo", "A HAT-TRICK AGAINST SPAIN \U0001F92F", "BEST WORLD CUP GAME? \U0001F447",
     "Spain were favourites in the 2018 World Cup opener but Cristiano Ronaldo scored a penalty, a scruffy shot past De Gea and then a curling free kick to complete a hat-trick",
     "Spain were the favourites. Ronaldo scored a penalty, then a scruffy shot, then curled a free kick over the wall to complete a hat-trick. Which makes you wonder,",
     RONALDO_PORTUGAL),
    ("ramos_reds", "ramos", "MOST RED CARDS EVER \U0001F7E5", "DIRTY OR JUST A WINNER? \U0001F447",
     "Sergio Ramos has been sent off more times than any player in the history of Spanish league football, and in the same career he won four Champions Leagues and a World Cup",
     "Sergio Ramos has been sent off more times than any player in Spanish football history. In the same career he won four Champions Leagues. Which makes you wonder,",
     None),
    ("messi_tax", "messi", "HE GOT A JAIL SENTENCE \U0001F633", "FAIR OR TOO HARSH? \U0001F447",
     "Lionel Messi and his father were convicted of tax fraud in Spain in 2016 and handed suspended prison sentences of twenty one months, paying millions in fines without serving jail time",
     "Messi and his father were convicted of tax fraud in Spain and handed suspended prison sentences. He paid millions and never spent a night in jail. Which makes you wonder,",
     None),
    ("messi_sleeping", "messi", "HE SLEPT WITH THE TROPHY \U0001F97A", "MOST DESERVED WIN EVER? \U0001F447",
     "After winning the 2022 World Cup Lionel Messi fell asleep in bed holding the trophy, and the photo his wife posted became one of the most liked pictures ever shared",
     "After winning the World Cup, Messi fell asleep in bed holding the trophy. The photo became one of the most liked pictures ever posted. Which makes you wonder,",
     MESSI_ARGENTINA),
    ("trent_corner", "trent", "CORNER TAKEN QUICKLY \U0001F92F", "GREATEST COMEBACK EVER? \U0001F447",
     "Liverpool trailed Barcelona three nil from the first leg, and Trent Alexander-Arnold spotted the defence switching off, took a corner quickly for Divock Origi to score and complete a four nil win",
     "Barcelona were three nil up on aggregate. Then Alexander-Arnold took a corner quickly, Origi scored, and Liverpool won four nil. Which makes you wonder,",
     None),
    ("ronaldo_donations", "ronaldo", "HE PAID THE WHOLE BILL \U0001F97A", "MOST UNDERRATED SIDE OF HIM? \U0001F447",
     "A young fan needed brain surgery his family could not afford, and Cristiano Ronaldo quietly paid for the entire treatment without publicising it, one of several medical bills he has covered for fans",
     "A young fan needed brain surgery his family could not afford. Ronaldo paid the entire bill, and said nothing about it publicly. Which makes you wonder,",
     None),
]

SLOTS = [
    ("25AUG", ["messi_helicopter", "pogba_ban", "ronaldo_euro2004"]),
    ("26AUG", ["ronaldo_spain_hattrick", "ramos_reds", "messi_tax"]),
    ("27AUG", ["messi_sleeping", "trent_corner", "ronaldo_donations"]),
]


def main():
    root = os.path.dirname(os.path.abspath(__file__))
    assert len({t[0] for t in TOPICS}) == 9
    for slug, *rest in TOPICS:
        cfg = build(slug, *rest)
        with open(os.path.join(root, f"batch_{slug}.json"), "w") as f:
            json.dump(cfg, f, indent=2, ensure_ascii=False)
        print(f"wrote batch_{slug}.json  ({len(cfg['videos'][0]['video_script'].split())} words)")

    order = "\n".join(
        f'  "batch_{slug}:{day}_slot{i + 1}_{SLOT_TIMES[i]}_{slug}"'
        for day, slugs in SLOTS
        for i, slug in enumerate(slugs)
    )
    header = (
        "# 25-27 Aug 2026 — 9 VOICEOVER shorts, NO background music, no phonk.\n"
        "# Ronaldo/Messi alternate slot 1 / slot 3 daily (25 Aug = day B: slot1 Messi, slot3 Ronaldo)."
    )
    script = RUN_TEMPLATE.format(order=order)
    script = script.replace(
        "# 22-24 Aug 2026 — 9 VOICEOVER shorts, NO background music, no phonk.\n"
        "# Ronaldo/Messi alternate slot 1 / slot 3 daily (22 Aug = day A: slot1 Ronaldo, slot3 Messi).",
        header,
    )
    run_path = os.path.join(root, "run_25to27aug.sh")
    with open(run_path, "w") as f:
        f.write(script)
    os.chmod(run_path, 0o755)
    print("wrote run_25to27aug.sh (9 builds)")


if __name__ == "__main__":
    main()
