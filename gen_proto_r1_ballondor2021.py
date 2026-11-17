"""R1 prototype (opinionated commentary over moving clips): Messi 2021 Ballon d'Or, 33 points over Lewandowski."""
import json, sys
sys.path.insert(0, ".claude/skills/football-shorts/scripts")
from shortbuild import build  # noqa: E402

OUT = "batch_proto_r1_ballondor2021.json"


def B(says, visual, *images):
    return {"says": says, "visual": visual, "images": list(images)}


beats = [
    B("Thirty-three points. That was Messi's margin over Lewandowski.",
      "big close-up of Lionel Messi's face at the 2021 Ballon d'Or ceremony", "Messi Ballon d'Or 2021 close up"),
    B("Six hundred thirteen to five eighty.",
      "Lionel Messi holding the Ballon d'Or trophy in Paris", "Messi Ballon d'Or Paris 2021"),
    B("Now look at Lewandowski's season.",
      "Robert Lewandowski in Bayern Munich kit", "Robert Lewandowski Bayern 2021"),
    B("Forty-one Bundesliga goals, beating Gerd Muller's forty.",
      "Robert Lewandowski scoring a Bundesliga goal for Bayern Munich", "Lewandowski 41 goals Bundesliga"),
    B("Forty-eight in all competitions.",
      "Robert Lewandowski celebrating a goal for Bayern Munich", "Lewandowski celebrating Bayern"),
    B("Messi had thirty in La Liga.",
      "Lionel Messi scoring for Barcelona in 2021", "Messi Barcelona 2021 goal"),
    B("Then he won the Copa del Rey.",
      "Lionel Messi lifting the Copa del Rey with Barcelona", "Messi Copa del Rey 2021"),
    B("And captained Argentina to the Copa America.",
      "Lionel Messi lifting the Copa America trophy with Argentina", "Messi Copa America 2021 trophy"),
    B("Argentina's first title since nineteen ninety-three.",
      "Lionel Messi celebrating with Argentina after the Copa America final", "Messi Argentina celebration 2021"),
    B("My argument: a trophy outweighed a record.",
      "Messi and Lewandowski together at the Ballon d'Or ceremony", "Messi Lewandowski Ballon d'Or"),
    B("Thirty-three points backs it up.",
      "Lionel Messi smiling with the Ballon d'Or", "Lionel Messi Ballon d'Or smile"),
    B("Messi or Lewandowski? Your vote.",
      "Robert Lewandowski close up at the Ballon d'Or ceremony", "Robert Lewandowski Ballon d'Or 2021"),
]

build("batch_ronaldo_wolfsburg_hattrick.json", OUT,
      subject="Does a record Bundesliga season outweigh trophies? Lewandowski's 41 goals against Messi's Copa del Rey and Copa America, argued over the 33-point margin of the 2021 vote (613 to 580).",
      beats=beats,
      hook="613 TO 580: DECIDE",
      cta="MESSI OR LEWANDOWSKI? 👇",
      terms="messi, lewandowski, ballon d'or 2021, copa america, bundesliga record",
      cover="big close-up of Lionel Messi at the 2021 Ballon d'Or ceremony",
      positives=["a real photograph of Lionel Messi", "a real photograph of Robert Lewandowski"])

with open(OUT, encoding="utf-8") as f:
    data = json.load(f)
d = data["defaults"]
d.update(
    voice_name="en-US-RogerNeural-Male",
    voice_rate=1.1,
    voice_volume=1.6,
    bgm_volume=0.06,
    min_shot_seconds=2.4,
    image_motion_style="varied",
    image_fill_mode="cover",
    cover_min_keep=0.3,
    enable_hook_card=True,
    hook_duration=1.4,
    hook_overlay_opacity=0.28,
    enable_subscribe_button=False,
    footage_min_fraction=1.0,
    youtube_footage_queries=[],
)
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
    f.write("\n")
