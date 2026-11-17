import json,re,pandas as pd,numpy as np
from scipy import stats
df=pd.read_pickle('df.pkl')
raw={json.loads(l)['id']:json.loads(l) for l in open('channel_shorts.jsonl')}
def first_sent(r):
    d=raw[r.id]['description'] or ''
    return (r.title+' '+d.split('\n')[0]).lower()
df['txt']=df.apply(first_sent,axis=1)
kw={
 'money (million/billion/€/£/$)':r'million|billion|€|£|\$|\bm\b|salary|paid|worth',
 'refusal/rejection (no/refused/rejected/turned down/banned)':r'\bno\b|refus|reject|turned down|banned|denied|snub|ignored',
 'emotion (cried/tears/dead/father/shaking)':r'cried|tears|dead|father|sad|shaking|broke down|heartbreak',
 'conflict/insult (slammed/booed/angry/fight/mock/criticis)':r'slam|boo|angry|fight|mock|critic|insult|furious|disgrace|screamed|punish|teased',
 'rivalry Messi-vs-Ronaldo both named':None,
 'number in title':r'\d',
 'question mark':r'\?',
 'record/first/ever':r'record|first|ever|never|history|fastest|most',
 'whatif/never left':r'what if|never left',
}
def mk(d,p):
    if p is None: return d.txt.str.contains('messi')&d.txt.str.contains('ronaldo')
    return d.txt.str.contains(p,regex=True)
def fe_test(d,mask,label):
    d=d.copy();d['x']=mask.astype(float);d['y']=d.lv
    d['xd']=d.x-d.groupby('date').x.transform('mean');d['yd']=d.y-d.groupby('date').y.transform('mean')
    dd=d[d.groupby('date').x.transform('nunique')>1]
    n1=int(d.x.sum());
    if len(dd)<15 or n1<5: return (label,n1,len(d),None,None,None,None)
    b=(dd.xd*dd.yd).sum()/(dd.xd**2).sum()
    # robust: cluster-free t via regression
    res=stats.linregress(dd.xd,dd.yd)
    return (label,n1,len(d),round(d[d.x==1].views.median()),round(d[d.x==0].views.median()),round((10**res.slope-1)*100,1),round(res.pvalue,3))
p1=df[df.date<'2026-10-29']
rows=[]
for k,p in kw.items(): rows.append(fe_test(p1,mk(p1,p),k))
for c in ['title_starts_name','title_starts_number','title_has_number','title_q','halo','title_has_series']:
    rows.append(fe_test(p1,p1[c],c))
rows.append(fe_test(p1,p1.title_caps_words>=2,'>=2 all-caps words'))
rows.append(fe_test(p1,p1.title_len>=30,'title len>=30 chars'))
rows.append(fe_test(p1,p1.duration>=20,'duration>=20s'))
rows.append(fe_test(p1,p1.duration<15,'duration<15s'))
rows.append(fe_test(p1,p1.star=='ronaldo','star Ronaldo'))
rows.append(fe_test(p1,p1.star=='messi','star Messi'))
rows.append(fe_test(p1,~p1.star.isin(['ronaldo','messi']),'star other (not R/M)'))
rows.append(fe_test(p1,p1.slot==1,'slot 13:00'));rows.append(fe_test(p1,p1.slot==2,'slot 17:00'));rows.append(fe_test(p1,p1.slot==3,'slot 21:00'))
print('P1 only (before 29 Oct), date fixed effects. cols: feature | n_with | n_total | median views with | median without | adj % effect on views | p')
for r in rows: print(r)
# also unadjusted share>1300 for keyword hits
print()
for k,p in kw.items():
    m=mk(p1,p);print(k,'n',m.sum(),'share>1300',round((p1[m].views>1300).mean(),3),'vs',round((p1[~m].views>1300).mean(),3),' share<300',round((p1[m].views<300).mean(),3),'vs',round((p1[~m].views<300).mean(),3))
rows=pd.DataFrame(rows,columns=['feature','n_with','n_total','med_with','med_without','adj_pct','p']);rows.to_csv('feature_effects_P1.csv',index=False)
# Same for P2 (n=32) no FE
p2=df[df.date>='2026-10-29']
print('\nP2 raw (n=32)')
for k,p in kw.items():
    m=mk(p2,p)
    if m.sum()>=3: print(k,m.sum(),p2[m].views.median(),p2[~m].views.median())
