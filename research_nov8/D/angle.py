import json,re,pandas as pd,numpy as np
from scipy import stats
df=pd.read_pickle('df.pkl')
raw={json.loads(l)['id']:json.loads(l) for l in open('channel_shorts.jsonl')}
def txt(r): return (r.title+' '+(raw[r.id]['description'] or '').split('\n')[0]).lower()
RULES=[('what_if',r'what if|never left|never happened|wasn.t injured'),
 ('award_ranking',r'ballon|ranking|vote|golden boot|player of the year|best player|award|ceremony|robbed'),
 ('money_transfer_rejection',r'million|billion|€|£|\$|transfer|contract|rejected|turned down|refus|said no|\bno to\b|sold|sell|joined|left|exile|clause|salary|paid|signed'),
 ('conflict_confrontation',r'slam|boo|angry|fight|mock|critic|insult|furious|disgrace|screamed|punish|teas|banned|sent off|red card|clash|feud|cheat|attack|hate|silenc|warn|stole|crown|revenge|haunt|kick'),
 ('personal_emotional',r'cried|tears|dead|father|dad|mother|mum|son\b|daughter|family|childhood|brother|twin|doctor|surgery|alone|shaking|sad|survive|died|death'),
 ('match_moment',r'final|hat-?trick|debut|comeback|penalty|free kick|goal|minute|match|win|beat|scored|derby|clasico|semi|cup|champions league|world cup'),
 ('record_number',r'record|first|history|fastest|most|\d+')]
def ang(r):
    t=txt(r)
    for k,p in RULES:
        if re.search(p,t): return k
    return 'other'
df['angle2']=df.apply(ang,axis=1)
df.to_pickle('df.pkl')
m=json.load(open('master.json'))
amap=dict(zip(df.id,df.angle2));
for r in m: r['angle2']=amap[r['id']]
json.dump(m,open('master.json','w'));open('master.jsonl','w').write('\n'.join(json.dumps(r,ensure_ascii=False) for r in m)+'\n')
p1=df[df.date<'2026-10-29']
g=p1.groupby('angle2').views.agg(n='count',median='median',share_gt1300=lambda x:(x>1300).mean(),share_lt300=lambda x:(x<300).mean()).round(2)
print(g)
print(stats.kruskal(*[x.views for _,x in p1.groupby('angle2') if len(x)>=5]))
p2=df[df.date>='2026-10-29']
print(p2.groupby('angle2').views.agg(['count','median']))
# fisher on top tail for money_transfer_rejection
m_=p1.angle2=='money_transfer_rejection'
a=(p1[m_].views>1300).sum();b=m_.sum()-a;c=(p1[~m_].views>1300).sum();d=(~m_).sum()-c
print('money_transfer_rejection >1300',a,b,c,d,stats.fisher_exact([[a,b],[c,d]]))
