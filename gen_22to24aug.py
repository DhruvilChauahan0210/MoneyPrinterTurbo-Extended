#!/usr/bin/env python3
"""Generate the 9 batch configs for 22-24 Aug 2026 (3 shorts/day, voiceover, no BGM).

Reuses the defaults/labels/build() from gen_15to21aug.py so the render settings stay
identical to the 21 shorts already shipped. Emits run_22to24aug.sh with the 25-min
per-build watchdog and Desktop-skip.
"""
import json
import os

from gen_15to21aug import PLAYERS, build, cover

# --- extra player visual profiles (slot-2 stars, no prior batch coverage) ---
PLAYERS["son"] = {
    "positives": [
        "a real photograph of Son Heung-min the footballer",
        "Son Heung-min in a white Tottenham jersey",
        "Son Heung-min in a red South Korea jersey",
        "a tight close up of Son Heung-min's face",
        "Son Heung-min celebrating a goal close up",
    ],
    "queries": [
        "Son Heung-min Tottenham close up face serious",
        "Son Heung-min South Korea close up face",
        "Son Heung-min Asian Games 2018 final celebration",
        "Son Heung-min goal celebration close up slow motion",
        "Son Heung-min dribbling close up slow motion",
        "Son Heung-min emotional crying close up",
    ],
    "cover": cover("Son Heung-min"),
    "terms": "Son Heung-min, Son Tottenham, Son South Korea, Son close up face, Son celebration",
}

PLAYERS["rodri"] = {
    "positives": [
        "a real photograph of Rodri the Manchester City footballer",
        "Rodri in a sky blue Manchester City jersey",
        "Rodri in a red Spain jersey",
        "a tight close up of Rodri Hernandez's face",
        "Rodri passing the ball close up",
    ],
    "queries": [
        "Rodri Manchester City close up face serious",
        "Rodri Ballon d'Or 2024 ceremony close up",
        "Rodri Spain close up face",
        "Rodri passing midfield close up slow motion",
        "Rodri Champions League final goal close up",
        "Rodri walking on pitch close up",
    ],
    "cover": cover("Rodri Hernandez"),
    "terms": "Rodri, Rodri Manchester City, Rodri Spain, Rodri close up face, Rodri Ballon d'Or",
}

PLAYERS["osimhen"] = {
    "positives": [
        "a real photograph of Victor Osimhen the footballer",
        "Victor Osimhen in a sky blue Napoli jersey",
        "Victor Osimhen wearing a black protective face mask",
        "a tight close up of Victor Osimhen's face",
        "Victor Osimhen celebrating a goal close up",
    ],
    "queries": [
        "Victor Osimhen Napoli close up face serious",
        "Victor Osimhen mask celebration close up",
        "Victor Osimhen goal celebration close up slow motion",
        "Victor Osimhen header goal close up",
        "Victor Osimhen Nigeria close up face",
        "Victor Osimhen walking on pitch close up",
    ],
    "cover": cover("Victor Osimhen"),
    "terms": "Victor Osimhen, Osimhen Napoli, Osimhen mask, Osimhen close up face, Osimhen celebration",
}

RONALDO_JUVE = {
    "positives": [
        "a real photograph of Cristiano Ronaldo the footballer",
        "Cristiano Ronaldo in a black and white striped Juventus jersey",
        "a tight close up of Cristiano Ronaldo's face",
        "Cristiano Ronaldo celebrating a goal close up",
        "Cristiano Ronaldo shooting the ball close up",
    ],
    "queries": [
        "Cristiano Ronaldo Juventus signing presentation 2018 close up",
        "Cristiano Ronaldo Juventus close up face serious",
        "Cristiano Ronaldo Juventus celebration close up slow motion",
        "Cristiano Ronaldo Juventus goal close up",
        "Cristiano Ronaldo Juventus dribbling close up",
        "Cristiano Ronaldo Juventus walking on pitch close up",
    ],
}

RONALDO_PORTUGAL = {
    "queries": [
        "Cristiano Ronaldo Portugal close up face serious",
        "Cristiano Ronaldo Madeira close up",
        "Cristiano Ronaldo Portugal celebration close up slow motion",
        "Cristiano Ronaldo Portugal free kick close up",
        "Cristiano Ronaldo Portugal dribbling close up",
        "Cristiano Ronaldo smiling close up",
    ]
}

MESSI_BARCA = {
    "positives": [
        "a real photograph of Lionel Messi the footballer",
        "Lionel Messi in a blue and red Barcelona jersey",
        "a tight close up of Lionel Messi's face",
        "Lionel Messi dribbling with the ball close up",
        "Lionel Messi celebrating a goal close up",
    ],
    "queries": [
        "Lionel Messi Barcelona close up face serious",
        "Lionel Messi Barcelona celebration close up slow motion",
        "Lionel Messi Barcelona dribbling close up slow motion",
        "Lionel Messi Barcelona free kick close up",
        "Lionel Messi Barcelona goal close up",
        "Lionel Messi Barcelona walking on pitch close up",
    ],
}

TOPICS = [
    ("ronaldo_bust", "ronaldo", "THEY LAUGHED AT HIS FACE \U0001F602", "WAS IT THAT BAD? \U0001F447",
     "Madeira renamed its airport after Cristiano Ronaldo and unveiled a bronze bust of him, but the sculpture was mocked worldwide for not looking like him and was quietly replaced with a new one",
     "Madeira named its airport after Ronaldo and unveiled a bust of him. The world laughed so hard at the face that they quietly replaced it. Which makes you wonder,",
     RONALDO_PORTUGAL),
    ("son_army", "son", "HE PLAYED FOR HIS FREEDOM \U0001F633", "TOUGHEST PRESSURE EVER? \U0001F447",
     "Son Heung-min faced nearly two years of compulsory South Korean military service, and winning the 2018 Asian Games earned him an exemption, after which he dropped to his knees in tears",
     "Son Heung-min was facing two years of military service. He won the Asian Games to earn an exemption, then dropped to his knees crying. Which makes you wonder,",
     None),
    ("messi_penalty_pass", "messi", "HE PASSED A PENALTY \U0001F92F", "GENIUS OR DISRESPECT? \U0001F447",
     "Lionel Messi won a penalty for Barcelona and instead of shooting he rolled it sideways for Luis Suarez to score, a trick almost nobody had tried, and half of football called it arrogant",
     "Messi won a penalty, walked up, and rolled it sideways for Suarez to score instead. Half of football called it arrogant. Which makes you wonder,",
     MESSI_BARCA),
    ("messi_bernabeu_shirt", "messi", "HE SILENCED 80,000 FANS \U0001F92B", "BEST CELEBRATION EVER? \U0001F447",
     "Lionel Messi scored a last minute winner at the Bernabeu in 2017, pulled off his Barcelona shirt and held his name and number up towards eighty thousand silent Real Madrid fans",
     "Messi scored in the last minute at the Bernabeu, took off his shirt, and held his name up to eighty thousand silent Madrid fans. Which makes you wonder,",
     MESSI_BARCA),
    ("rodri_boycott", "rodri", "MADRID BOYCOTTED THE AWARD \U0001F633", "WHO REALLY DESERVED IT? \U0001F447",
     "Rodri won the 2024 Ballon d'Or and Real Madrid boycotted the entire ceremony in protest, insisting Vinicius Junior had been robbed of the award",
     "Rodri won the Ballon d'Or, and Real Madrid boycotted the whole ceremony, saying Vinicius was robbed. Nobody from Madrid clapped. Which makes you wonder,",
     None),
    ("ronaldo_strike", "ronaldo", "HIS SIGNING CAUSED A STRIKE \U0001F633", "WAS HE WORTH IT? \U0001F447",
     "When Juventus signed Cristiano Ronaldo in 2018, workers at the car plants owned by the club's owners went on strike in protest at the money spent on one player",
     "When Juventus signed Ronaldo, workers at the company that owns the club walked out on strike over the money. He still sold out the stadium. Which makes you wonder,",
     RONALDO_JUVE),
    ("ronaldo_museum", "ronaldo", "HE BUILT HIS OWN MUSEUM \U0001F92F", "CONFIDENCE OR EGO? \U0001F447",
     "At twenty eight years old Cristiano Ronaldo opened a museum dedicated to himself in Madeira, filled with his own trophies, his own waxwork and his own name above the door",
     "At twenty eight, Ronaldo opened a museum about himself. His own trophies, his own statue, his own name above the door. Which makes you wonder,",
     RONALDO_PORTUGAL),
    ("osimhen_tiktok", "osimhen", "HIS CLUB MOCKED HIM \U0001F633", "WOULD YOU FORGIVE THEM? \U0001F447",
     "Napoli posted a social media video mocking their own striker Victor Osimhen after he missed a penalty, and Osimhen deleted every Napoli photo from his account and threatened legal action against the club",
     "Napoli posted a video mocking their own striker after he missed a penalty. Osimhen deleted every Napoli photo and threatened to sue the club. Which makes you wonder,",
     None),
    ("messi_goldenball", "messi", "HE DIDN'T DESERVE IT \U0001F633", "DID HE DESERVE IT? \U0001F447",
     "Lionel Messi was given the Golden Ball as best player of the 2014 World Cup minutes after losing the final, looked broken collecting it, and Diego Maradona said he never deserved the award",
     "Messi was handed best player of the World Cup minutes after losing the final. He looked broken. Maradona said he never deserved it. Which makes you wonder,",
     None),
]

SLOTS = [
    ("22AUG", ["ronaldo_bust", "son_army", "messi_penalty_pass"]),
    ("23AUG", ["messi_bernabeu_shirt", "rodri_boycott", "ronaldo_strike"]),
    ("24AUG", ["ronaldo_museum", "osimhen_tiktok", "messi_goldenball"]),
]
SLOT_TIMES = ["1300", "1700", "2100"]

RUN_TEMPLATE = """#!/bin/zsh
# 22-24 Aug 2026 — 9 VOICEOVER shorts, NO background music, no phonk.
# Ronaldo/Messi alternate slot 1 / slot 3 daily (22 Aug = day A: slot1 Ronaldo, slot3 Messi).
# ONE attempt per short, no retries. 25-min watchdog per build. Skips finished shorts.
cd ~/Developer/CDH/MoneyPrinterTurbo-Extended
export PATH="$HOME/.deno/bin:$PWD/.venv/bin:$PATH"
export HF_HUB_DISABLE_TELEMETRY=1
PY=./.venv/bin/python

ORDER=(
{order}
)

ok=0; fail=0
for pair in $ORDER; do
  batch="${{pair%%:*}}"; out="${{pair##*:}}"
  if [[ -f ~/Desktop/"$out.mp4" ]]; then
    echo ">>> SKIP $out (already on Desktop)"
    continue
  fi
  echo "### BUILDING $batch  ->  ~/Desktop/$out.mp4"
  tmplog="/tmp/mpt_${{batch}}.log"
  $PY batch_generator.py "$batch.json" > "$tmplog" 2>&1 &
  bpid=$!
  killed=0
  for i in {{1..100}}; do
    kill -0 $bpid 2>/dev/null || break
    sleep 15
  done
  if kill -0 $bpid 2>/dev/null; then
    echo ">>> !!! TIMEOUT after 25 min — killing $batch and moving on"
    kill -9 $bpid 2>/dev/null
    killed=1
  fi
  wait $bpid 2>/dev/null
  rc=$?
  (( killed )) && rc=124
  build_log=$(cat "$tmplog")
  generated=$(print -r -- "$build_log" | sed -n 's/^GENERATED_VIDEO=//p' | tail -1)
  if (( rc == 0 )) && [[ -n "$generated" && -f "$generated" ]]; then
    cp "$generated" ~/Desktop/"$out.mp4"
    dur=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$generated" 2>/dev/null)
    echo ">>> COPIED -> ~/Desktop/$out.mp4  (duration=${{dur}}s)"
    ok=$((ok+1))
  else
    echo ">>> !!! BUILD FAILED for $batch (no retry)"
    print -r -- "$build_log" | tail -25
    fail=$((fail+1))
  fi
done
echo "9 SHORTS ATTEMPTED — ok=$ok failed=$fail"
"""


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
    run_path = os.path.join(root, "run_22to24aug.sh")
    with open(run_path, "w") as f:
        f.write(RUN_TEMPLATE.format(order=order))
    os.chmod(run_path, 0o755)
    print("wrote run_22to24aug.sh (9 builds)")


if __name__ == "__main__":
    main()
