import json,pandas as pd,numpy as np
from scipy import stats
df=pd.DataFrame(json.load(open('master.json')))
df['period']=np.where(df.date<'2026-10-29','P1_pre29Oct','P2_post29Oct')
pd.set_option('display.width',200);pd.set_option('display.max_columns',30)
def grp(d,col,minn=1):
    g=d.groupby(col).views.agg(n='count',median='median',mean='mean',p25=lambda x:x.quantile(.25),p75=lambda x:x.quantile(.75),share_lt300=lambda x:(x<300).mean())
    return g[g.n>=minn].round(2)
def kw(d,col,minn=5):
    gs=[x.views.values for _,x in d.groupby(col) if len(x)>=minn]
    return stats.kruskal(*gs) if len(gs)>1 else None
for P in ['P1_pre29Oct','P2_post29Oct']:
    d=df[df.period==P]
    print('=====',P,len(d),'median',d.views.median())
    d2=d.copy(); d2['hour_g']=d2.hour.map(lambda h:h if h in(13,17,21) else 'other')
    print(grp(d2,'hour_g'));print(kw(d2[d2.hour_g!='other'],'hour_g'))
    print(grp(d,'weekday'));print(kw(d,'weekday'))
    print(grp(d,'fmt'));print(kw(d,'fmt'))
    print(grp(d,'star'));
    print(grp(d,'angle'))
    for c in ['title_q','title_emoji','title_has_number','title_starts_number','title_starts_name','halo','title_has_series']:
        print(c,grp(d,c).to_dict('index'),stats.mannwhitneyu(d[d[c]].views,d[~d[c]].views).pvalue if d[c].nunique()>1 and d[c].sum()>2 else 'NA')
    for c in ['title_len','title_caps_words','title_words','duration','hour','desc_len','n_tags']:
        print(c,'spearman',stats.spearmanr(d[c],d.views))
