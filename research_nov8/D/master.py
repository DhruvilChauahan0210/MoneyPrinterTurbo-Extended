import json,re,datetime,statistics as st,collections
m=json.load(open('match_raw.json'));R=[json.loads(l) for l in open('channel_shorts.jsonl')]
T={}
for l in open('task_index.jsonl'):
    t=json.loads(l);T[t['task_id']]=t
cuts=json.load(open('cuts.json'))
NOW=datetime.datetime(2026,11,8,20,30,tzinfo=datetime.timezone(datetime.timedelta(hours=5,minutes=30)))
STARS=['ronaldo','messi','mbappe','haaland','kane','salah','yamal','vinicius','bellingham','neymar']
def star(r):
    tags=re.findall(r'#(\w+)',r['description'] or '')
    tags=[t.lower() for t in tags if t.lower() not in('halo','shorts','football','soccer','fyp','viral','footballshorts','futbol','skills')]
    # primary: first hashtag matching a star
    for t in tags:
        for s in STARS:
            if s in t or (s=='ronaldo' and t in('cr7',)) : return s
        if t in ('cristianoronaldo','lionelmessi','leomessi'): return 'ronaldo' if 'cristiano' in t else 'messi'
        if t=='kylianmbappe': return 'mbappe'
    ttl=r['title'].lower()
    for s in STARS:
        if s in ttl: return s
    txt=(r['description'] or '').lower()
    best=None
    for s in STARS+['mbappé','vinícius']:
        i=txt.find(s)
        if i>=0 and (best is None or i<best[0]): best=(i,s)
    if best: return best[1].replace('é','e').replace('í','i')
    return 'other'
ANGLES=[('whatif',r'what if|never left|never happened|\?$'),
 ('rivalry_conflict',r'slam|silenc|revenge|teas|beat messi|vs\b|stole|robbed|reject|refus|ban|attack|booed|angry|furious|fight|feud|insult|warn|sent off|red card|slap|clash|rival|critic|disrespect|cheat|hate|ban'),
 ('number_record',r'\b\d{2,4}(st|nd|rd|th)?\b|record|broke|goals?\b|first ever|all-time|most '),
 ('award_ballondor',r'ballon|award|golden boot|trophy|title|champion'),
 ('emotion_personal',r'cried|tears|dad|father|mum|mother|son|daughter|family|childhood|alone|shaking|doctor|surgery|ill|death')]
def angle(r):
    t=r['title'].lower()
    t=re.sub(r'#\w+','',t)
    for a,p in ANGLES:
        if re.search(p,t): return a
    return 'other'
rows=[]
for r in R:
    x=m[r['id']]
    t=T[x['task_id']]
    matched=(x['sim']>=0.6) or (x['sim']>=0.45 and x['ddur']<=1.0)
    ts=datetime.datetime.fromisoformat(r['ist_datetime'])
    ttl=r['title']; tclean=re.sub(r'\s*#\w.*$','',ttl).strip()
    words=re.findall(r"[A-Za-z']+",tclean)
    caps=sum(1 for w in words if len(w)>=2 and w.isupper())
    row=dict(id=r['id'],date=r['ist_date'],hour=r['ist_hour'],weekday=r['ist_weekday'],ts=r['timestamp'],views=r['view_count'],likes=r['like_count'],
      comments=r['comment_count'],duration=r['duration'],title=ttl,
      age_days=round((NOW-ts).total_seconds()/86400,2),
      slot={13:1,17:2,21:3}.get(r['ist_hour']),
      star=star(r),angle=angle(r),
      title_len=len(tclean),title_words=len(words),title_caps_words=caps,title_q='?' in ttl,
      title_emoji=bool(re.search(r'[\U0001F300-\U0001FAFF☀-➿]',ttl)),
      title_has_number=bool(re.search(r'\d',tclean)),title_starts_number=bool(re.match(r'\s*\d',tclean)),
      title_starts_name=bool(re.match(r'\s*(ronaldo|messi|mbapp|haaland|kane|salah|yamal|vinic|bellingham|neymar|cristiano|lionel)',tclean,re.I)),
      halo='#halo' in ttl,
      title_has_series=bool(re.search(r'part\s*\d|ep\.?\s*\d|episode',ttl,re.I)),
      fmt=('whatif7s' if (r['duration']<=8.5 and r['ist_date']>='2026-10-26') else 'short_lt15' if r['duration']<15 else '15-25' if r['duration']<25 else '25-35' if r['duration']<35 else '35+'),
      desc_len=len(r['description'] or ''),n_tags=len(r['tags'] or []),
      matched=matched,match_sim=x['sim'],match_ddur=x['ddur'],task_id=x['task_id'] if matched else None)
    if matched:
        txt=t.get('script') or ''
        row.update(words=len(txt.split()),beat_plan=t['beat_plan'],nbeats=t['nbeats'],hook=t['hook'],cta=t.get('cta'),
           n_clips=t.get('n_clips'),n_photo=t.get('n_photo'),n_video=t.get('n_video'),photo_s=t.get('photo_s'),video_s=t.get('video_s'),
           n_pinned_clips=t.get('n_pinned_clips'),bgm_volume=t.get('bgm_volume'),
           has_final=t['has_final'])
        tot=(t.get('photo_s') or 0)+(t.get('video_s') or 0)
        row['photo_share']=round(t['photo_s']/tot,3) if tot else None
        c=cuts.get(t['task_id'])
        if c is not None and t.get('duration'): row['cuts_per_10s']=round(len(c)/t['duration']*10,2)
        row['clips_per_10s']=round(t['n_clips']/t['duration']*10,2) if t.get('n_clips') and t.get('duration') else None
        row['pipeline']='beat_plan' if t['beat_plan'] else 'semantic_clips'
    rows.append(row)
json.dump(rows,open('master.json','w'),indent=0)
with open('master.jsonl','w') as f:
    for r in rows: f.write(json.dumps(r,ensure_ascii=False)+'\n')
print(len(rows),sum(r['matched'] for r in rows))
print(collections.Counter(r['star'] for r in rows))
print(collections.Counter(r['angle'] for r in rows))
print(collections.Counter(r.get('pipeline') for r in rows))
