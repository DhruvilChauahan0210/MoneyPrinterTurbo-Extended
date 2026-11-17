import pandas as pd,numpy as np,datetime as dt
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt, matplotlib.dates as mdates
df=pd.read_pickle('df.pkl')
df['d']=pd.to_datetime(df.ts,unit='s')+pd.Timedelta(hours=5,minutes=30)
col={'semantic_clips':'#2a78c2','beat_plan':'#d9822b'}
fig,ax=plt.subplots(2,1,figsize=(13,8.5),gridspec_kw={'height_ratios':[3,1.4]})
a=ax[0]
for lab,g in df.groupby(df.pipeline.fillna('unmatched / What-If / other')):
    c={'semantic_clips':'#2a78c2','beat_plan':'#d9822b'}.get(lab,'#888888')
    a.scatter(g.d,g.views.clip(lower=1),s=22,c=c,alpha=.8,label=f'{lab} (n={len(g)})',edgecolor='none')
daily=df.groupby('date').views.median();daily.index=pd.to_datetime(daily.index)+pd.Timedelta(hours=12)
a.plot(daily.index,daily.values,color='k',lw=1.3,label='daily median')
a.axvline(pd.Timestamp('2026-10-29'),color='red',ls='--',lw=1.5);a.text(pd.Timestamp('2026-10-29 03:00'),3200,'29 Oct drop',color='red',fontsize=10,va='top',ha='right')
a.axhline(1000,color='grey',ls=':',lw=.8)
for s,e,t in [('2026-09-15','2026-09-20','dip'),('2026-10-10','2026-10-14','dip')]:
    a.axvspan(pd.Timestamp(s),pd.Timestamp(e)+pd.Timedelta(days=1),color='#f2c0c0',alpha=.35)
a.set_yscale('log');a.set_ylim(1,5000);a.set_ylabel('views (log scale)');a.set_title('CD PHANTOM Shorts, 1 Aug - 8 Nov 2026: views per Short by IST publish time (n=308)')
a.legend(loc='lower left',fontsize=8)
for dte,lab in [('2026-09-06','#halo added to titles'),('2026-10-17','beat-plan photo format starts')]:
    a.axvline(pd.Timestamp(dte),color='#555',ls='-',lw=.7);a.text(pd.Timestamp(dte)+pd.Timedelta(hours=6),4500,lab,fontsize=8,rotation=90,va='top')
b=ax[1]
wk=df.assign(w=df.d.dt.to_period('W-SUN').apply(lambda p:p.start_time)).groupby('w').views.median()
b.bar(wk.index+pd.Timedelta(days=3),wk.values,width=6,color='#4c78a8');b.set_ylabel('weekly median views');b.axvline(pd.Timestamp('2026-10-29'),color='red',ls='--')
b.xaxis.set_major_formatter(mdates.DateFormatter('%d %b'))
plt.tight_layout();plt.savefig('timeline_views.png',dpi=130)
# histogram
fig,ax=plt.subplots(1,2,figsize=(12,4))
p1=df[df.date<'2026-10-29'];p2=df[df.date>='2026-10-29']
bins=np.logspace(0,3.6,35)
ax[0].hist(p1.views.clip(lower=1),bins=bins,color='#2a78c2');ax[0].set_xscale('log');ax[0].set_title(f'1 Aug-28 Oct (n={len(p1)}): median {int(p1.views.median())}')
ax[1].hist(p2.views.clip(lower=1),bins=bins,color='#d9822b');ax[1].set_xscale('log');ax[1].set_title(f'29 Oct-8 Nov (n={len(p2)}): median {int(p2.views.median())}')
for x in ax: x.set_xlabel('views per Short (log)');x.set_ylabel('Shorts')
plt.tight_layout();plt.savefig('views_histogram.png',dpi=130)
# slot/hour boxplots P1
fig,ax=plt.subplots(1,3,figsize=(14,4))
q=p1[p1.hour.isin([13,17,21])]
ax[0].boxplot([q[q.hour==h].views for h in (13,17,21)],tick_labels=['13:00','17:00','21:00']);ax[0].set_title('slot (P1, before 29 Oct)');ax[0].set_ylim(0,3000)
wd=['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
ax[1].boxplot([p1[p1.weekday==w].views for w in wd],tick_labels=[w[:3] for w in wd]);ax[1].set_title('weekday (IST, P1)');ax[1].set_ylim(0,3000)
fb=['short_lt15','15-25','25-35']
ax[2].boxplot([p1[p1.fmt==f].views for f in fb],tick_labels=['<15s','15-25s','25-35s']);ax[2].set_title('duration bucket (P1)');ax[2].set_ylim(0,3000)
plt.tight_layout();plt.savefig('slot_weekday_duration.png',dpi=130)
# photo share vs views scatter, colored by period
m=df[df.matched&df.photo_share.notna()]
fig,ax=plt.subplots(figsize=(7,5))
for lab,g,c in [('before 29 Oct',m[m.date<'2026-10-29'],'#2a78c2'),('from 29 Oct',m[m.date>='2026-10-29'],'#d9822b')]:
    ax.scatter(g.photo_share+np.random.uniform(-.015,.015,len(g)),g.views.clip(lower=1),s=18,alpha=.6,c=c,label=f'{lab} (n={len(g)})')
ax.set_yscale('log');ax.set_xlabel('share of screen time on still photos (from render media plan)');ax.set_ylabel('views');ax.legend();ax.set_title('Still-image share vs views')
plt.tight_layout();plt.savefig('photo_share_vs_views.png',dpi=130)
