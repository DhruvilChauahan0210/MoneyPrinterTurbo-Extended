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

def Q(n, ctx): return [f"{n} {c}" for c in ctx]
CTX=["close up face","goal celebration close up","close up serious","celebrating close up","close up intense eyes","close up determined face","smiling close up","roaring celebration","match close up face","close up emotional","arms raised celebration","close up portrait","walking pitch close up","close up shirt","goal close up reaction","highlights close up"]
build('batch_ronaldo_record17.json','batch_ronaldo_calma2012.json',
 "In April 2012, Cristiano Ronaldo scored the winner in a 2-1 Real Madrid victory at Barcelona's Camp Nou, then gestured and shouted calma at the home fans, in a season Real Madrid won La Liga with a record 100 points",
 "In April twenty twelve, Real Madrid travelled to Barcelona's Camp Nou needing a win to move close to the La Liga title. Cristiano Ronaldo scored the winner in a two one victory, then held out his hands and shouted calma, telling the home fans to calm down. Real Madrid went on to win the league that season with a record one hundred points.",
 "HE TALKED BACK TO 90,000 FANS","MOST SAVAGE CELEBRATION EVER? 👇",
 "a tight close up of Cristiano Ronaldo's face in a white Real Madrid shirt, intense, face filling the frame",
 Q("Cristiano Ronaldo Real Madrid Barcelona Camp Nou calma celebration",[""])+Q("Cristiano Ronaldo Real Madrid",["Clasico winner celebration close up","Camp Nou goal close up","white shirt close up face","2012 goal celebration close up","hands out calm down celebration","La Liga 100 points celebration","roaring celebration close up","close up intense Clasico","smiling close up 2012","close up determined face","trophy celebration La Liga 2012","Clasico close up serious","goal close up reaction","close up portrait","match close up face"]),
 "Ronaldo calma celebration Camp Nou 2012, Real Madrid Barcelona 2-1 Clasico, Real Madrid 100 points La Liga 2012")

build('batch_messi_boateng2015.json','batch_messi_wembley2011.json',
 "In the 2011 Champions League final at Wembley, Lionel Messi, aged 23, scored the second goal in Barcelona's 3-1 win over Manchester United, the second time he had beaten them in a final",
 "In May twenty eleven, Barcelona played Manchester United in the Champions League final at Wembley. Lionel Messi scored the second goal with a powerful strike from outside the area, and Barcelona won three one. Messi was just twenty three years old. It was the second time he had beaten United in a Champions League final.",
 "HE BEAT THE SAME TEAM TWICE","BEST MESSI FINAL EVER? 👇",
 "a tight close up of Lionel Messi's face in a Barcelona shirt, intense, face filling the frame",
 Q("Lionel Messi Barcelona",["Wembley 2011 Champions League final close up","Manchester United final goal celebration","shirt close up face","Champions League trophy 2011 close up","goal celebration close up","close up serious 2011","blaugrana close up determined","Champions League final close up smiling","close up intense eyes","celebrating Wembley close up","Camp Nou goal close up","arms raised celebration","trophy lift close up","match close up face","close up emotional","goal close up reaction"]),
 "Messi Wembley 2011 final, Barcelona Manchester United 3-1, Messi goal Wembley")

build('batch_mbappe_2022uturn.json','batch_mbappe_firstseason.json',
 "In his first season at Real Madrid after joining on a free transfer in 2024, Kylian Mbappe had a slow start and drew criticism, but finished as La Liga's top scorer with 31 goals",
 "In twenty twenty four, Kylian Mbappe joined Real Madrid on a free transfer. His start was slow, and critics questioned whether the move was working. Madrid fans began to worry. But by the end of the season, he had scored thirty one league goals, more than anyone else in La Liga.",
 "MADRID FANS WERE ALREADY WORRIED","BEST FIRST SEASON? 👇",
 "a sharp tight close up of Kylian Mbappe's face in a white Real Madrid shirt, intense, face filling the frame",
 Q("Kylian Mbappe Real Madrid",["close up face white shirt","goal celebration close up","Bernabeu close up serious","debut close up","close up intense eyes","celebrating close up","La Liga goal close up","close up determined face","close up smiling","hat trick celebration","close up disappointed","Champions League close up","match close up face","close up emotional","arms out celebration","close up portrait"]),
 "Mbappe Real Madrid first season, Mbappe 31 La Liga goals, Mbappe free transfer 2024",
 ['a real photograph of Kylian Mbappe the footballer',"a tight close up of Kylian Mbappe's face",'Kylian Mbappe in a white Real Madrid shirt','Kylian Mbappe standing on a football pitch looking serious'])
