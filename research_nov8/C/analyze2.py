import json,re,statistics,collections
from analyze import rows, pct, stat
sh=[r for r in rows if r['is_short']]
rec=[r for r in sh if r['age_days']<=60]
# primary-angle classifier (ordered; first match wins)
PRI=[
 ('news_event_retire', r'retire|retires|retirement|is leaving|farewell|last dance|goodbye|deserved better|thank you|never forget you'),
 ('kids_fans_cute', r'\bkid\b|\bkids\b|little (fan|boy|girl)|\bboy\b|\bgirl\b|\bbaby\b|3-year|child(ren)?\b.*(fan|ronaldo)|fan\'s heart|prank|ishowspeed|speed\b'),
 ('family_partner_gift', r'girlfriend|\bmom\b|mother|family|\bdad\b|father|wife|\bjr\b|junior|\bson\b|\bgift\b|christmas|\bines\b|princess|grandma|brother|sister|friendship|baby'),
 ('emotion_respect', r'cried|crying|tears|💔|🥹|❤️‍🩹|heartwarming|sweetest|respect|kindness|apolog|emotional|jota|rewarded'),
 ('rivalry_head2head', r'\bvs\.?\b|versus|rival|fight for|goat\?|who is the goat|ronaldo or messi|messi or ronaldo|trap|destroy|stole|triggered|not ready'),
 ('skill_moment', r'skill|nutmeg|rabona|dribbl|insane|not human|unreal|magic|golazo|goal|goals|free kick|speed|passes|trick'),
 ('story_origin_evolution', r'story|journey|poor|struggl|childhood|evolution|from .* to |broke to|rich|bullied|untold|at 14|how '),
 ('records_numbers', r'record|history|\d+ goals|\d{3}|most |youngest|fastest|every trophy|all time|ballon d.or'),
 ('quiz_ranking', r'guess|quiz|can you|how many|rank|top \d|finish the|phrase'),
 ('transfer_contract', r'transfer|signs?\b|signing|contract|join|deal'),
 ('controversy_ref', r'controvers|banned|red card|\bref|\bvar\b|altercation|heated|cheat|argument'),
 ('funny_meme', r'funn|😂|🤣|meme|parody|hairstyle|animals|pov'),
]
def primary(t):
    t=t.lower()
    for k,p in PRI:
        if re.search(p,t): return k
    return 'other_unclassified'
for r in sh: r['primary']=primary(r['title'])
g=collections.defaultdict(list)
for r in rec: g[r['primary']].append(r['views'])
ang={k:stat(v) for k,v in sorted(g.items(),key=lambda x:-statistics.median(x[1]))}
# star single (first matched) — multi-label for star
from analyze import STARS
import re as _re
def stars(t):
    t=t.lower(); return [k for k,p in STARS.items() if _re.search(p,t)]
gs=collections.defaultdict(list)
for r in rec:
    for s in (stars(r['title']) or ['(no star named)']): gs[s].append(r['views'])
star={k:stat(v) for k,v in sorted(gs.items(),key=lambda x:-len(x[1]))}
# only-star shorts (exactly one star) to reduce overlap
gs1=collections.defaultdict(list)
for r in rec:
    s=stars(r['title'])
    if len(s)==1: gs1[s[0]].append(r['views'])
star1={k:stat(v) for k,v in sorted(gs1.items(),key=lambda x:-len(x[1]))}
# duration buckets
bk=collections.defaultdict(list)
for r in rec:
    d=r['duration']; b='<=15s' if d<=15 else '16-30s' if d<=30 else '31-45s' if d<=45 else '46-61s'
    bk[b].append(r['views'])
dur={k:stat(v) for k,v in bk.items()}
# format cues
def feat(t):
    return {
     'has_emoji': bool(re.search(r'[\U0001F300-\U0001FAFF☀-➿❤]',t)),
     'hashtag': '#' in t,
     'question': '?' in t,
     'starts_digit': bool(re.match(r'\s*\W*\d',t)),
     'allcaps_word': bool(re.search(r'\b[A-Z]{4,}\b',re.sub(r'#\w+','',t))),
     'starts_lower': t[:1].islower(),
     'ellipsis': '..' in t or '…' in t,
     'quote': bool(re.search(r'["“”]',t)),
     'colon_pipe': ('|' in t) or (': ' in t),
     'POV': t.lower().startswith('pov'),
     'len': len(t),
    }
for r in sh: r['feat']=feat(r['title'])
cue={}
for c in ['has_emoji','hashtag','question','starts_digit','allcaps_word','starts_lower','ellipsis','quote','colon_pipe','POV']:
    a=[r['views'] for r in rec if r['feat'][c]]; b=[r['views'] for r in rec if not r['feat'][c]]
    cue[c]={'with':stat(a),'without':stat(b)}
lb={}
for name,(lo,hi) in {'<=25':(0,25),'26-40':(26,40),'41-60':(41,60),'61+':(61,999)}.items():
    lb[name]=stat([r['views'] for r in rec if lo<=r['feat']['len']<=hi])
# Top 40 unique titles
seen=set(); top=[]
for r in sorted(rec,key=lambda r:-r['views']):
    k=re.sub(r'[^a-z]','',r['title'].lower())[:40]
    if k in seen: continue
    seen.add(k); top.append(r)
    if len(top)==40: break
tp=collections.Counter()
for r in top:
    f=r['feat']
    for c in ['has_emoji','hashtag','question','starts_digit','allcaps_word','starts_lower','ellipsis','quote','colon_pipe','POV']:
        if f[c]: tp[c]+=1
    nm=re.match(r"\W*(lamine|yamal|ronaldo|cristiano|messi|mbapp|haaland|neymar|kane|vini|bellingham|salah)",r['title'].lower())
    if nm: tp['name_first']+=1
lens=[r['feat']['len'] for r in top]
top_info={'pattern_counts_of_40':dict(tp),'len_median':statistics.median(lens),'len_mean':round(sum(lens)/40,1),'len_min':min(lens),'len_max':max(lens),
 'titles':[{'views':r['views'],'age':r['age_days'],'dur':r['duration'],'ch':r['channel'],'title':r['title']} for r in top]}
# channel concentration in top 40
chs=collections.Counter(r['channel'] for r in top)
top_info['channels_in_top40']=chs.most_common(8)
# 'info/AI-voice-like' class: duration>=28 AND title has numbers/record/story etc.  show median
facty=[r for r in rec if r['primary'] in ('records_numbers','story_origin_evolution','transfer_contract') and r['duration']>=28]
fact_stat=stat([r['views'] for r in facty])
# repeated share of results with <1000 views
low=[r for r in rec if r['views']<1000]
out={'n_rec60':len(rec),'overall':stat([r['views'] for r in rec]),'by_primary_angle':ang,'by_star_multi':star,'by_star_single':star1,'by_duration':dur,'title_cues':cue,'title_len_buckets':lb,'top40':top_info,'facty_28s+':fact_stat,'under1000_views_share':round(len(low)/len(rec),3),'n_under1000':len(low)}
# A-variant only (relevance, any date) vs rest
json.dump(out,open('stats2.json','w'),indent=1,ensure_ascii=False)
json.dump(sh,open('shorts_dataset.json','w'),ensure_ascii=False)
print(json.dumps({k:out[k] for k in ['n_rec60','overall','by_primary_angle','by_star_single','by_duration','title_len_buckets','facty_28s+','under1000_views_share']},indent=1))
print(json.dumps(out['title_cues'],indent=0)[:2500])
print(json.dumps({k:v for k,v in top_info.items() if k!='titles'},indent=0))
