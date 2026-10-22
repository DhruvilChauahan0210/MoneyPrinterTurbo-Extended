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

build('batch_messi_icelandpenalty2018.json','batch_messi_boateng2015.json',
 "In the May 2015 Champions League semi-final first leg, Lionel Messi scored twice in three minutes for Barcelona in a 3-0 win over Bayern Munich, leaving defender Jerome Boateng on the floor before chipping goalkeeper Manuel Neuer",
 "In May twenty fifteen, Barcelona hosted Bayern Munich in the Champions League semi final. Lionel Messi took on defender Jerome Boateng, who fell to the ground trying to stop him. Messi then chipped goalkeeper Manuel Neuer for his second goal in three minutes. Barcelona won three nil, and the moment is still replayed today.",
 "HE MADE A WORLD CUP WINNER FALL","BEST DRIBBLE EVER? 👇",
 "a tight close up of Lionel Messi's face in a Barcelona shirt, intense, face filling the frame",
 ["Lionel Messi Barcelona Bayern Munich 2015 close up","Lionel Messi Boateng dribble Barcelona","Lionel Messi chip Neuer goal celebration","Lionel Messi Barcelona shirt close up face","Lionel Messi Barcelona Champions League 2015 close up","Lionel Messi celebration Camp Nou close up","Lionel Messi blaugrana close up serious","Lionel Messi Barcelona goal celebration close up","Lionel Messi close up determined face Barcelona","Lionel Messi Barcelona Champions League semi final","Lionel Messi smiling close up Barcelona","Lionel Messi Barcelona 2015 treble close up","Lionel Messi close up intense eyes Barcelona","Lionel Messi Barcelona dribbling close up","Lionel Messi Barcelona match close up face","Lionel Messi arms raised Camp Nou"],
 "Messi Boateng Bayern 2015, Messi chip Neuer, Barcelona Bayern Champions League semi final",
 ['a real photograph of Lionel Messi the footballer',"a tight close up of Lionel Messi's face",'Lionel Messi in a red and blue Barcelona shirt','Lionel Messi celebrating a goal'])

build('batch_neymar_pelerecord.json','batch_neymar_berlin2015.json',
 "In the 2015 Champions League final in Berlin, Neymar scored in stoppage time to make it 3-1 for Barcelona against Juventus, completing the treble at age 23",
 "In June twenty fifteen, Barcelona played Juventus in the Champions League final in Berlin. With the game at two one, Neymar scored in stoppage time to make it three one. It completed Barcelona's treble, the league, the cup, and the Champions League, all in a single season. Neymar was just twenty three years old.",
 "NEYMAR SEALED IT IN THE 97TH MINUTE","BEST NEYMAR MOMENT EVER? 👇",
 "a sharp tight close up of Neymar's face in a Barcelona shirt celebrating, face filling the frame",
 ["Neymar Barcelona Juventus final goal celebration","Neymar Berlin 2015 close up","Neymar Barcelona shirt close up face","Neymar goal celebration Barcelona close up","Neymar Champions League trophy Barcelona close up","Neymar Barcelona 2015 close up smiling","Neymar close up intense Barcelona","Neymar Barcelona dribble close up","Neymar celebrating Champions League Barcelona","Neymar close up emotional Barcelona","Neymar Barcelona Champions League final","Neymar close up determined Barcelona 2015","Neymar Barcelona match close up face","Neymar hugging teammates Barcelona close up","Neymar young Barcelona close up","Neymar Camp Nou close up"],
 "Neymar Juventus final 2015, Neymar Berlin goal, Barcelona treble 2015",
 ['a real photograph of Neymar the footballer',"a tight close up of Neymar's face",'Neymar in a red and blue Barcelona shirt','Neymar celebrating a goal'])

build('batch_ronaldo_alnassrban.json','batch_ronaldo_record17.json',
 "In the 2013-14 season, Cristiano Ronaldo scored 17 Champions League goals, the most any player had scored in a single campaign, as Real Madrid beat Atletico Madrid in the final in Lisbon to win their tenth European Cup",
 "In the twenty thirteen fourteen season, Cristiano Ronaldo scored seventeen goals in the Champions League, the most any player had ever scored in a single campaign. Real Madrid reached the final in Lisbon and beat Atletico Madrid after extra time to win their tenth European Cup. Ronaldo scored in the final too.",
 "THE YEAR EUROPE COULDN'T STOP HIM","BEST UCL SEASON EVER? 👇",
 "a tight close up of Cristiano Ronaldo's face in a white Real Madrid shirt, intense, face filling the frame",
 ["Cristiano Ronaldo Real Madrid Champions League 2014 close up","Cristiano Ronaldo Real Madrid La Decima celebration","Cristiano Ronaldo Lisbon final goal celebration","Cristiano Ronaldo white Real Madrid shirt close up face","Cristiano Ronaldo Champions League trophy Real Madrid 2014","Cristiano Ronaldo Real Madrid goal celebration close up","Cristiano Ronaldo shirt off celebration Lisbon","Cristiano Ronaldo close up intense Real Madrid","Cristiano Ronaldo Bernabeu goal celebration close up","Cristiano Ronaldo Real Madrid 2014 close up serious","Cristiano Ronaldo Champions League goals 2014 close up","Cristiano Ronaldo Real Madrid smiling close up","Cristiano Ronaldo roaring celebration Real Madrid","Cristiano Ronaldo close up determined Real Madrid","Cristiano Ronaldo Real Madrid match close up face","Cristiano Ronaldo Madrid 2014 trophy close up"],
 "Ronaldo 17 Champions League goals 2014, Real Madrid La Decima Lisbon, Ronaldo Atletico final",
 ['a real photograph of Cristiano Ronaldo the footballer',"a tight close up of Cristiano Ronaldo's face",'Cristiano Ronaldo in a white Real Madrid shirt','Cristiano Ronaldo celebrating a goal'])
