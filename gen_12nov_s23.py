"""12 NOV 2026 slots 2 (17:00, Kane) and 3 (21:00, Messi). Built with the football-shorts skill.
New opening rule (6 Nov 2026 retention study): beat 1 = big close-up of the named megastar,
first spoken words carry a number or the star's name, never a bare date.
"""
import sys
sys.path.insert(0, ".claude/skills/football-shorts/scripts")
from shortbuild import build  # noqa: E402


def B(says, visual, *images):
    return {"says": says, "visual": visual, "images": list(images)}


# ---- slot 2: Kane, 2018 World Cup Golden Boot ----
build("batch_ronaldo_wolfsburg_hattrick.json", "batch_kane_goldenboot_2018.json",
      subject="Harry Kane won the 2018 World Cup Golden Boot with six goals, three of them penalties, five in "
              "England's first two games, but England lost the semi-final to Croatia and the third-place game "
              "to Belgium and finished fourth",
      beats=[B("Six goals at the 2018 World Cup. One Golden Boot. England still finished fourth.",
               "close up of Harry Kane in an England shirt", "Harry Kane", "Harry Kane England 2018 World Cup"),
             B("Harry Kane scored twice against Tunisia,", "Harry Kane celebrating a goal for England",
               "Harry Kane Tunisia 2018", "Harry Kane celebrating England 2018"),
             B("then a hat-trick against Panama.", "Harry Kane scoring a hat-trick for England",
               "Harry Kane Panama hat-trick", "Harry Kane Panama 2018 World Cup goal"),
             B("Three of his six goals were penalties.", "Harry Kane taking a penalty for England",
               "Harry Kane penalty World Cup 2018", "Harry Kane penalty Colombia"),
             B("His only knockout goal was a penalty against Colombia.", "Harry Kane against Colombia at the World Cup",
               "Harry Kane Colombia 2018", "Harry Kane Colombia penalty shootout England"),
             B("Mbappé, Ronaldo and Lukaku all finished on four.", "Kylian Mbappé at the 2018 World Cup",
               "Kylian Mbappe 2018 World Cup", "Romelu Lukaku 2018 World Cup"),
             B("England lost the semi-final to Croatia in extra time,", "Harry Kane dejected after losing to Croatia",
               "Harry Kane Croatia semi-final 2018", "Harry Kane dejected England 2018"),
             B("then lost the third-place game to Belgium.", "Harry Kane after the Belgium defeat",
               "Harry Kane Belgium 2018", "England Belgium third place 2018"),
             B("Does a Golden Boot make up for fourth place?", "Harry Kane holding the Golden Boot trophy",
               "Harry Kane Golden Boot", "Harry Kane Golden Boot 2018 trophy")],
      hook="NO MEDAL FOR THE TOP SCORER?", cta="GOLDEN BOOT OR TROPHY? 👇",
      terms="Harry Kane 2018 World Cup Golden Boot, England fourth, Panama hat-trick, Colombia penalty",
      cover="Harry Kane in an England shirt",
      positives=["a real photograph of Harry Kane", "a real photograph of Harry Kane playing for England",
                 "a real photograph of Kylian Mbappé", "a real photograph of Romelu Lukaku"])

# ---- slot 3: Messi, 2011 Bernabeu semi-final ----
build("batch_ronaldo_wolfsburg_hattrick.json", "batch_messi_bernabeu_2011_semifinal.json",
      subject="Lionel Messi scored twice in eleven minutes, in the 76th and 87th, as Barcelona won 2-0 at Real Madrid "
              "in the first leg of the April 2011 Champions League semi-final after Pepe was sent off, "
              "the second a solo run from the halfway line, and Barcelona went on to win the trophy",
      beats=[B("Messi scored two goals in eleven minutes at the Bernabéu.",
               "close up of Lionel Messi in a Barcelona shirt", "Lionel Messi", "Lionel Messi Barcelona 2011"),
             B("Real Madrid against Barcelona, Champions League semi-final.", "Real Madrid against Barcelona in 2011",
               "Real Madrid Barcelona 2011 Champions League semi-final", "Real Madrid vs Barcelona Bernabeu 2011"),
             B("Pepe was sent off after sixty-one minutes.", "Pepe shown a red card",
               "Pepe red card Barcelona 2011", "Pepe Real Madrid 2011"),
             B("Messi scored in the seventy-sixth minute after a pass from Ibrahim Afellay,",
               "Lionel Messi scoring against Real Madrid", "Lionel Messi goal Real Madrid 2011",
               "Lionel Messi Afellay Real Madrid"),
             B("then ran from the halfway line past the defenders for the second.",
               "Lionel Messi dribbling past Real Madrid defenders", "Lionel Messi solo goal Real Madrid 2011",
               "Messi dribbles Real Madrid 2011"),
             B("Barcelona won two-nil, three-one on aggregate.", "Barcelona players celebrating at the Bernabéu",
               "Barcelona celebrate Bernabeu 2011", "Barcelona players celebrating 2011"),
             B("Barcelona then won the Champions League at Wembley.", "Barcelona with the Champions League trophy 2011",
               "Barcelona Champions League trophy 2011 Wembley", "Messi Champions League trophy 2011"),
             B("Was this Messi's greatest night against Real Madrid?", "close up of Lionel Messi in a Barcelona shirt",
               "Lionel Messi Barcelona portrait", "Lionel Messi Barcelona 2011 close up")],
      hook="COULD ANYONE STOP HIM?", cta="HIS BEST SOLO GOAL? 👇",
      terms="Real Madrid 0-2 Barcelona 2011 Champions League semi-final, Messi two goals, Pepe red card, solo run",
      cover="Lionel Messi celebrating for Barcelona",
      positives=["a real photograph of Lionel Messi", "a real photograph of Lionel Messi playing for Barcelona",
                 "a real photograph of Pepe", "a real photograph of Ibrahim Afellay"])
