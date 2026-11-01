"""Example generator: copy to the repo root as gen_<range>.py, replace the shorts, run it.

Each build() writes one batch config (beat plan, voice_rate 0.88, photos sourced later by beat_source.py).
Donors: clone a recent working config of the same subject (e.g. batch_ronaldo_kholood_hattrick.json for
Ronaldo, batch_messi_benatia_fifth.json for Messi, batch_mbappe_clasico_ballondor_28pts.json for others).
"""
import sys
sys.path.insert(0, ".claude/skills/football-shorts/scripts")
from shortbuild import build  # noqa: E402


def B(says, visual, *images):
    return {"says": says, "visual": visual, "images": list(images)}


# 12 NOV slot 1 (13:00) - Ronaldo (example structure only; write a fresh, verified topic)
build("batch_ronaldo_kholood_hattrick.json", "batch_ronaldo_EXAMPLE.json",
      subject="One sentence of verified facts: who, what, when, numbers",
      beats=[B("Spoken line one, the tension, not the answer.", "what the photo should show",
               "Cristiano Ronaldo Al Nassr", "Ronaldo close up"),
             B("Spoken line two with a concrete fact.", "visual", "plain query", "plain query 2"),
             # ... 8-9 beats, 65-80 words in total ...
             B("End on the debate question?", "close up of Cristiano Ronaldo", "Cristiano Ronaldo close up",
               "Cristiano Ronaldo face")],
      hook="SIX WORDS MAX ALL CAPS", cta="SHORT DEBATE QUESTION? 👇",
      terms="comma separated search terms for the topic",
      cover="what frame 1 should show",
      positives=["a real photograph of Cristiano Ronaldo",
                 "a real photograph of Cristiano Ronaldo playing football"])
