"""12 NOV 2026 slot 1 (13:00) — Ronaldo. Built with the football-shorts skill."""
import sys
sys.path.insert(0, ".claude/skills/football-shorts/scripts")
from shortbuild import build  # noqa: E402


def B(says, visual, *images):
    return {"says": says, "visual": visual, "images": list(images)}


build("batch_ronaldo_wolfsburg_hattrick.json", "batch_ronaldo_bayern_100th_ucl.json",
      subject="Cristiano Ronaldo scored a hat-trick as Real Madrid beat Bayern Munich 4-2 after extra time in the "
              "April 2017 Champions League quarter-final, becoming the first player to reach 100 Champions League goals",
      beats=[B("April twenty seventeen: Real Madrid against Bayern Munich.", "Real Madrid against Bayern Munich",
               "Real Madrid Bayern 2017 Champions League", "Real Madrid vs Bayern Munich 2017"),
             B("Robert Lewandowski scored a penalty, Cristiano Ronaldo equalised,", "Cristiano Ronaldo celebrating for Real Madrid",
               "Ronaldo goal Bayern 2017", "Cristiano Ronaldo Real Madrid 2017 celebration"),
             B("then a Sergio Ramos own goal forced extra time.", "Sergio Ramos looking frustrated",
               "Sergio Ramos Bayern 2017", "Sergio Ramos frustrated"),
             B("Then Arturo Vidal was sent off.", "Arturo Vidal shown a red card",
               "Arturo Vidal red card Real Madrid 2017", "Arturo Vidal Bayern"),
             B("In extra time, Ronaldo scored twice more,", "Cristiano Ronaldo scoring for Real Madrid",
               "Ronaldo hat-trick Bayern", "Cristiano Ronaldo goal Real Madrid"),
             B("becoming the first player to score one hundred Champions League goals.",
               "Cristiano Ronaldo celebrating a historic goal", "Ronaldo 100 Champions League goals",
               "Cristiano Ronaldo Champions League celebration"),
             B("Replays showed one of those goals was offside, and Bayern were furious.",
               "Bayern Munich players protesting to the referee", "Bayern players protest referee Real Madrid 2017",
               "Bayern Munich players angry"),
             B("Real Madrid won four-two, then won the whole tournament.", "Cristiano Ronaldo with the Champions League trophy 2017",
               "Ronaldo Champions League trophy 2017 Cardiff", "Real Madrid Champions League 2017 champions"),
             B("Did Ronaldo deserve that hundredth goal?", "close up of Cristiano Ronaldo in Real Madrid kit",
               "Cristiano Ronaldo Real Madrid close up", "Cristiano Ronaldo Real Madrid portrait")],
      hook="THE GOAL BAYERN NEVER ACCEPTED", cta="DID HE DESERVE IT? 👇",
      terms="Real Madrid 4-2 Bayern 2017, Ronaldo hat-trick 100 Champions League goals, Vidal red card offside",
      cover="Cristiano Ronaldo celebrating for Real Madrid",
      positives=["a real photograph of Cristiano Ronaldo", "a real photograph of Cristiano Ronaldo playing for Real Madrid",
                 "a real photograph of Bayern Munich players"])
