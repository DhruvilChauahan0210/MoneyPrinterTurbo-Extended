import sys, json
sys.path.insert(0, ".claude/skills/football-shorts/scripts")
from shortbuild import build  # noqa: E402


def B(says, visual, *images):
    return {"says": says, "visual": visual, "images": list(images)}


OUT = "batch_proto_r3_morocco_portugal.json"
build("batch_ronaldo_wolfsburg_hattrick.json", OUT,
      subject="On 10 December 2022 at Al Thumama Stadium Morocco beat Portugal 1-0 in the World Cup quarter-final, Youssef En-Nesyri heading the 42nd-minute goal, becoming the first African team in a World Cup semi-final, while Cristiano Ronaldo, a 51st-minute substitute, left the pitch in tears.",
      beats=[
          B("Ronaldo cried at the World Cup.", "big close up of Cristiano Ronaldo in tears, Portugal kit 2022", "Cristiano Ronaldo crying Portugal Morocco", "Ronaldo tears World Cup 2022"),
          B("Morocco had just beaten Portugal, one-nil.", "Morocco players celebrating", "Morocco Portugal World Cup 2022", "Morocco celebrate Portugal"),
          B("En-Nesyri headed it in, forty-second minute.", "Youssef En-Nesyri heading a goal", "Youssef En-Nesyri Morocco", "En-Nesyri goal Portugal"),
          B("Ronaldo came on after the break.", "Cristiano Ronaldo Portugal 2022 substitute", "Cristiano Ronaldo Portugal 2022", "Ronaldo Portugal Morocco"),
          B("Portugal never found an equaliser.", "Portugal players dejected", "Portugal players dejected Morocco", "Bruno Fernandes Portugal 2022"),
          B("Morocco even finished with ten men.", "Morocco players defending", "Morocco defence Portugal", "Achraf Hakimi Morocco 2022"),
          B("They became Africa's first World Cup semi-finalists.", "Morocco players celebrating with fans", "Morocco semi-final 2022", "Morocco World Cup semi-final celebration"),
          B("Ronaldo, thirty-seven, in his fifth World Cup.", "Cristiano Ronaldo Portugal portrait", "Cristiano Ronaldo Portugal 2022 portrait", "Cristiano Ronaldo Qatar 2022"),
          B("His World Cup dream ended that night.", "Cristiano Ronaldo dejected Portugal", "Ronaldo dejected Portugal Morocco", "Ronaldo sad World Cup 2022"),
          B("He left the pitch immediately, crying.", "Cristiano Ronaldo walking off in tears", "Ronaldo walking off tears Morocco", "Ronaldo tunnel tears 2022"),
          B("One header ended Ronaldo's Qatar campaign.", "Youssef En-Nesyri celebrating", "Youssef En-Nesyri celebrating", "En-Nesyri Portugal header"),
          B("Underdog glory, or Ronaldo's biggest heartbreak?", "Cristiano Ronaldo in tears Portugal", "Cristiano Ronaldo tears Portugal", "Cristiano Ronaldo crying Qatar"),
      ],
      hook="10 DEC 2022: MOROCCO MADE HISTORY",
      cta="UNDERDOG GLORY OR HEARTBREAK? \U0001F447",
      terms="Morocco 1-0 Portugal World Cup 2022 quarter-final, Ronaldo tears, En-Nesyri header, Al Thumama",
      cover="big close up of Cristiano Ronaldo crying, Portugal 2022",
      positives=["a real photograph of Cristiano Ronaldo",
                 "a real photograph of Youssef En-Nesyri",
                 "a real photograph of a Morocco footballer in a red shirt"])

d = json.load(open(OUT))
df = d["defaults"]
df.update(
    enable_hook_card=True,
    hook_duration=1.2,
    hook_overlay_opacity=0.35,
    enable_subscribe_button=False,
    enable_cta=False,
    cover_min_keep=0.36,
    min_shot_seconds=2.4,
    image_motion_style="varied",
)
json.dump(d, open(OUT, "w"), indent=2, ensure_ascii=False)
print("patched defaults")
