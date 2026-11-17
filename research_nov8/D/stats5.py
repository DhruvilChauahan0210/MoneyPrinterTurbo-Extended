import json,pandas as pd,numpy as np
from scipy import stats
df=pd.read_pickle('df.pkl')
m=df[df.matched&df.cuts_per_10s.notna()].copy()
def fe(d,x,y='lv'):
    d=d[[x,y,'date']].dropna().copy()
    d['xd']=d[x]-d.groupby('date')[x].transform('mean');d['yd']=d[y]-d.groupby('date')[y].transform('mean')
    d=d[d.groupby('date')[x].transform('nunique')>1]
    if len(d)<8: return None
    r=stats.pearsonr(d.xd,d.yd);b=np.polyfit(d.xd,d.yd,1)[0]
    return len(d),round(r.statistic,2),round(r.pvalue,3),round(b,3)
for name,sub in [('era C',m[m.era.str.startswith('C')]),('era C Oct21-28',m[(m.date>='2026-10-21')&(m.date<'2026-10-29')]),('P1 all',m[m.date<'2026-10-29']),('era D',m[m.era.str.startswith('D')]),('ALL matched',m)]:
    print(name)
    for x in ['photo_share','cuts_per_10s','n_video']:
        print('  date-FE',x,fe(sub,x))
# date trend within era C
c=m[m.era.str.startswith('C')]
c=c.assign(dnum=pd.to_datetime(c.date).map(lambda d:d.toordinal()))
print('C views vs date rho',stats.spearmanr(c.dnum,c.views),'photo vs date',stats.spearmanr(c.dnum,c.photo_share))
# same-day comparison: Oct 24 clip-only 988 vs photo-only 1034,1018
# photo-only vs not, Oct17-28, medians
c2=m[(m.date>='2026-10-17')&(m.date<'2026-10-29')]
for lab,g in c2.groupby(c2.photo_share>=0.95): print('Oct17-28 photo>=95%',lab,len(g),g.views.median())
# Oct 21-28 only
c3=m[(m.date>='2026-10-21')&(m.date<'2026-10-29')]
for lab,g in c3.groupby(c3.photo_share>=0.95): print('Oct21-28 photo>=95%',lab,len(g),g.views.median(),g.views.min(),g.views.max())
