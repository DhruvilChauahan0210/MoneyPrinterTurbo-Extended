import json, copy
def build(donor, out, subject, script, hook, cta, cover, queries, terms, pos=None):
    d = json.load(open(donor))
    df = d['defaults']
    df.update(video_subject=subject, video_script=script, hook_text=hook, cta_text=cta,
              hook_cover_term=cover, youtube_footage_queries=queries, video_terms=terms,
              curated_image_paths=[], era_negative_labels=[], series_badge_text="")
    if pos:
        df['subject_positive_labels'] = pos
        df['visual_evidence_prompts'] = pos
        df['era_positive_labels'] = pos[:2]
    d['videos'] = [{"video_subject": subject, "video_script": script}]
    json.dump(d, open(out, 'w'), indent=2, ensure_ascii=False)
    print(out, len(script.split()), 'words')

R = "Cristiano Ronaldo"
build('batch_ronaldo_alnassrban.json', 'batch_ronaldo_slovenia2024.json',
 "At Euro 2024, with Portugal and Slovenia level 0-0 in extra time, Cristiano Ronaldo, aged 39, had an extra-time penalty saved by Jan Oblak and cried on the pitch, then scored first in the shootout as Diogo Costa saved all three Slovenian penalties",
 "At Euro twenty twenty four, Portugal and Slovenia were still level at nil nil in extra time. Portugal were awarded a penalty, and Cristiano Ronaldo, thirty nine years old, stepped up to take it. Slovenia's goalkeeper Jan Oblak saved it, and Ronaldo broke down in tears on the pitch. But in the shootout, he stepped up first and scored. Portugal's goalkeeper Diogo Costa then saved all three Slovenian penalties, and Portugal went through.",
 "RONALDO CRIED ON THE PITCH AGAIN", "DID HE DESERVE THAT WIN? 👇",
 "a tight close up of Cristiano Ronaldo's face in tears, emotional, face filling the frame",
 ["Cristiano Ronaldo crying Euro 2024 close up","Cristiano Ronaldo penalty saved Slovenia close up","Cristiano Ronaldo tears Portugal close up face","Cristiano Ronaldo Portugal Euro 2024 close up serious","Cristiano Ronaldo shootout penalty Slovenia goal","Cristiano Ronaldo apologises teammates Portugal Euro 2024","Cristiano Ronaldo emotional close up Portugal","Cristiano Ronaldo Portugal shirt close up Euro 2024","Cristiano Ronaldo disappointed close up Portugal","Cristiano Ronaldo celebrates Portugal Euro 2024 close up","Cristiano Ronaldo Portugal red shirt close up face","Cristiano Ronaldo hands on face Portugal","Cristiano Ronaldo intense eyes Portugal Euro","Cristiano Ronaldo walking pitch close up Portugal 2024","Cristiano Ronaldo Euro 2024 round of 16 close up","Cristiano Ronaldo sad close up Portugal"],
 "Ronaldo crying Slovenia Euro 2024, Ronaldo penalty saved Oblak, Portugal Slovenia shootout Diogo Costa",
 ['a real photograph of Cristiano Ronaldo the footballer',"a tight close up of Cristiano Ronaldo's face",'Cristiano Ronaldo in a red Portugal shirt','Cristiano Ronaldo standing on a football pitch looking emotional'])

build('batch_haaland_debuthattrick.json', 'batch_haaland_leipzigfive.json',
 "In March 2023, Erling Haaland scored five goals for Manchester City in a 7-0 Champions League win over RB Leipzig, matching the record for most goals by one player in a Champions League match, and was substituted just after the hour mark",
 "In March twenty twenty three, Manchester City hosted RB Leipzig in the Champions League. Erling Haaland scored five goals in a single game, matching the record for most goals by one player in a Champions League match. City won seven nil. And Haaland did not even finish it. He was substituted just after the hour mark, with the game already long over.",
 "HE SCORED FIVE AND WAS TAKEN OFF", "BEST HAALAND GAME EVER? 👇",
 "a sharp tight close up of Erling Haaland's face, intense, filling the frame",
 ["Erling Haaland five goals Leipzig close up","Erling Haaland Manchester City Champions League close up face","Erling Haaland celebration Etihad close up","Erling Haaland sky blue shirt close up serious","Erling Haaland Man City goal celebration close up","Erling Haaland substituted off Leipzig","Erling Haaland close up intense Champions League","Erling Haaland Manchester City 2023 close up","Erling Haaland hat trick Champions League City","Erling Haaland roar celebration close up","Erling Haaland close up determined face City","Erling Haaland walking off pitch close up","Erling Haaland Pep Guardiola hug Leipzig","Erling Haaland Champions League 2023 goals","Erling Haaland close up serious portrait City","Erling Haaland match ball Leipzig"],
 "Haaland five goals Leipzig, Manchester City 7-0 RB Leipzig, Haaland Champions League record",
 ['a real photograph of Erling Haaland the Norwegian footballer',"a tight close up of Erling Haaland's face, long blonde hair tied back, strong jaw, intense expression",'a very tall blonde footballer in the sky blue shirt of Manchester City','Erling Haaland standing on a football pitch looking serious'])

build('batch_messi_icelandpenalty2018.json', 'batch_messi_saudi2022.json',
 "At the 2022 World Cup, Argentina arrived on a 36-game unbeaten run and lost their opening match 2-1 to Saudi Arabia after Lionel Messi scored a penalty, one of the biggest shocks in World Cup history, before going on to win the tournament",
 "At the twenty twenty two World Cup, Argentina opened against Saudi Arabia, a team ranked far below them. Messi scored an early penalty to put them ahead. But Saudi Arabia came back to win two one, ending Argentina's thirty six game unbeaten run. It was one of the biggest shocks in World Cup history. Argentina were written off. They went on to win the whole tournament.",
 "THE SHOCK THAT NEARLY BROKE ARGENTINA", "BIGGEST WORLD CUP SHOCK EVER? 👇",
 "a tight close up of Lionel Messi's face looking stunned and serious, face filling the frame",
 ["Lionel Messi Saudi Arabia World Cup 2022 close up face","Lionel Messi penalty goal Saudi Arabia 2022","Lionel Messi stunned close up Argentina Qatar","Lionel Messi close up serious Argentina 2022","Lionel Messi Argentina sky blue shirt close up Qatar","Lionel Messi walking off close up disappointed Argentina 2022","Lionel Messi close up intense eyes Argentina Qatar","Lionel Messi Lusail stadium close up","Lionel Messi close up upset face World Cup 2022","Lionel Messi Argentina match close up Qatar","Lionel Messi close up serious portrait Qatar 2022","Lionel Messi Argentina bench close up Qatar","Lionel Messi training close up Argentina Qatar","Lionel Messi close up determined face Argentina 2022","Lionel Messi World Cup 2022 group stage close up","Lionel Messi close up frustrated Argentina 2022"],
 "Messi Saudi Arabia 2022 World Cup, Argentina lose to Saudi Arabia, Messi penalty Saudi Arabia, Argentina Qatar 2022")

build('batch_messi_icelandpenalty2018.json', 'batch_messi_everyround2022.json',
 "At the 2022 World Cup, Lionel Messi scored in every round, from the group stage through the round of 16, quarter-final, semi-final and final, finishing with seven goals including two in the final against France, and won the Golden Ball",
 "At the twenty twenty two World Cup, Lionel Messi found the net in every single round. He scored in the group stage, the round of sixteen, the quarter final, the semi final, and the final. Seven goals in total, including two against France in the final. Argentina won on penalties, and Messi was named the best player of the entire tournament.",
 "THE TOURNAMENT HE FINALLY OWNED", "BEST WORLD CUP RUN EVER? 👇",
 "a tight close up of Lionel Messi's face looking emotional and determined, face filling the frame",
 ["Lionel Messi World Cup final close up face","Lionel Messi goal celebration Argentina close up","Lionel Messi World Cup trophy lift close up","Lionel Messi Argentina sky blue shirt close up celebration","Lionel Messi Golden Ball close up","Lionel Messi penalty goal celebration Argentina","Lionel Messi emotional close up Argentina","Lionel Messi roaring celebration Argentina","Lionel Messi close up smiling Argentina World Cup","Lionel Messi Argentina captain close up","Lionel Messi hugging teammates Argentina close up","Lionel Messi close up serious Argentina match","Lionel Messi Argentina semi final close up","Lionel Messi Argentina quarter final close up","Lionel Messi close up face celebrating goal","Lionel Messi arms raised celebration Argentina"],
 "Messi World Cup 2022 final goals, Messi scored every round, Messi Golden Ball, Argentina France final")
