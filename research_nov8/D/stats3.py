import json,pandas as pd,numpy as np
from scipy import stats
df=pd.DataFrame(json.load(open('master.json')))
df['lv']=np.log10(df.views.clip(lower=1))
df['dt']=pd.to_datetime(df.ts,unit='s')
df=df.sort_values('ts').reset_index(drop=True)
# eras
def era(r):
    if r.date<'2026-09-06': return 'A Aug1-Sep5 (9-15s clips, no #halo)'
    if r.date<'2026-10-17': return 'B Sep6-Oct16 (20-30s clips, #halo)'
    if r.date<'2026-10-29': return 'C Oct17-28 (beat-plan, photos+clips)'
    return 'D Oct29-Nov8 (all-photo beat-plan + What-If)'
df['era']=df.apply(era,axis=1)
g=df.groupby('era').views.agg(n='count',median='median',p10=lambda x:x.quantile(.1),p25=lambda x:x.quantile(.25),p75=lambda x:x.quantile(.75),p90=lambda x:x.quantile(.9),mx='max',
   share_850_1150=lambda x:((x>=850)&(x<=1150)).mean(),share_lt300=lambda x:(x<300).mean(),share_gt1500=lambda x:(x>1500).mean())
pd.set_option('display.width',250)
print(g.round(2))
# ICC by day (P1)
p1=df[df.date<'2026-10-29']
dm=p1.groupby('date').lv.transform('mean')
# lag-1 spearman of consecutive Shorts
print('lag1 spearman P1 (log views):',stats.spearmanr(p1.lv.values[1:],p1.lv.values[:-1]))
print('lag1 spearman all:',stats.spearmanr(df.lv.values[1:],df.lv.values[:-1]))
# daily-median autocorr
d=df.groupby('date').lv.median()
print('daily median lag1',stats.spearmanr(d.values[1:],d.values[:-1]))
# ICC: one-way anova on date groups (3 each)
def icc(data,col):
    groups=[x[col].values for _,x in data.groupby('date') if len(x)>=2]
    k=np.mean([len(x) for x in groups]);gm=np.concatenate(groups).mean()
    msb=sum(len(x)*(x.mean()-gm)**2 for x in groups)/(len(groups)-1)
    msw=sum(((x-x.mean())**2).sum() for x in groups)/(sum(len(x) for x in groups)-len(groups))
    return (msb-msw)/(msb+(k-1)*msw)
print('ICC by publish date, all',icc(df,'lv'),' P1',icc(p1,'lv'))
# daily medians list to find dip days
dd=df.groupby('date').views.median()
dips=dd[dd<450]
print('dip days (daily median<450):',list(dips.index))
df.to_pickle('df.pkl')
# Within-day slot analysis (P1 only, exactly 13/17/21 present)
for name,sub in [('P1',p1),('P2',df[df.date>='2026-10-29']),('all',df)]:
    piv=sub[sub.hour.isin([13,17,21])].pivot_table(index='date',columns='hour',values='views',aggfunc='first').dropna()
    print(name,'days with 3 slots',len(piv),'median by slot',piv.median().to_dict(),'friedman',stats.friedmanchisquare(*[piv[c] for c in piv.columns]).pvalue)
    print('  share of days where slot2<slot1', (piv[17]<piv[13]).mean(),'slot3<slot1',(piv[21]<piv[13]).mean(),'slot3<slot2',(piv[21]<piv[17]).mean())
    print('  wilcoxon 17 vs 13',stats.wilcoxon(piv[17],piv[13]).pvalue,'21 vs 13',stats.wilcoxon(piv[21],piv[13]).pvalue,'21 vs 17',stats.wilcoxon(piv[21],piv[17]).pvalue)
# does the same-day previous Short's views predict next? (cannibalisation would give a negative relation within day)
x=[];y=[]
for date,s in df.groupby('date'):
    s=s.sort_values('ts')
    if len(s)==3 : 
        x.append(s.views.iloc[0]);y.append(s.views.iloc[1])
print('slot1->slot2 same-day spearman',stats.spearmanr(x,y))
