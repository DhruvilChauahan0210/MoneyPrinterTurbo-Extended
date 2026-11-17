import json,pandas as pd,numpy as np
from scipy import stats
df=pd.read_pickle('df.pkl')
m=df[df.matched&df.cuts_per_10s.notna()].copy()
print('matched with cuts',len(m))
pd.set_option('display.width',250)
for e,g in m.groupby('era'):
    print('\n###',e,len(g))
    for c in ['photo_share','cuts_per_10s','clips_per_10s','n_video','n_photo','duration','words','nbeats']:
        gg=g[[c,'views']].dropna()
        if len(gg)>8 and gg[c].nunique()>1:
            r=stats.spearmanr(gg[c],gg.views);print(f'  {c:14s} n={len(gg)} rho={r.statistic:+.2f} p={r.pvalue:.3f}  median {c}={gg[c].median()}')
# bins pre-drop
p1=m[m.date<'2026-10-29']
p1['cut_bin']=pd.cut(p1.cuts_per_10s,[0,3.5,5,7,10,40])
print(p1.groupby('cut_bin',observed=True).views.agg(['count','median',lambda x:(x<300).mean(),lambda x:(x>1500).mean()]).round(2))
p1['ps']=pd.cut(p1.photo_share,[-.01,0,.25,.75,1.0])
print(p1.groupby('ps',observed=True).views.agg(['count','median',lambda x:(x<300).mean(),lambda x:(x>1500).mean()]).round(2))
# P2 matched all-photo vs others
p2=m[m.date>='2026-10-29']
print(p2[['date','hour','views','photo_share','cuts_per_10s','duration']].sort_values('views').to_string())
# whole-sample mean photo-share share by era
print(m.groupby('era').photo_share.agg(['count','mean','median']))
print(m.groupby('era').cuts_per_10s.agg(['count','mean','median']))
print(m.groupby('era').duration.agg(['count','mean','median']))
print(m.groupby('era').words.agg(['count','mean','median']))
