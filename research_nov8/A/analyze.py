import json,glob,statistics as st,datetime as dt,re,os,sys
today=dt.date(2026,11,8)
out=[]
allrows=[]
def pct(v,p):
    v=sorted(v); k=(len(v)-1)*p; f=int(k); c=min(f+1,len(v)-1); return v[f]+(v[c]-v[f])*(k-f)
for f in sorted(glob.glob('ch/full_*.jsonl')):
    rows=[json.loads(l) for l in open(f)]
    if not rows: continue
    h=rows[0]['uploader_id']; subs=rows[0]['channel_follower_count']
    for r in rows: r['h']=h
    allrows+=rows
    # exclude <3 days old for distribution
    old=[r for r in rows if (today-dt.datetime.strptime(r['upload_date'],'%Y%m%d').date()).days>=3]
    v=[r['view_count'] or 0 for r in old]
    ds=[dt.datetime.strptime(r['upload_date'],'%Y%m%d').date() for r in rows]
    span=(max(ds)-min(ds)).days or 1
    per_week=len(rows)/span*7
    top=sorted(old,key=lambda r:-r['view_count'])
    tv=sum(v)
    top3share=sum(r['view_count'] for r in top[:3])/tv
    top10=[r['view_count'] for r in top[:10]]
    durs=[r['duration'] for r in old if r['duration']]
    topq=[r['duration'] for r in top[:max(1,len(top)//4)] if r['duration']]
    last30=[r for r in old if (today-dt.datetime.strptime(r['upload_date'],'%Y%m%d').date()).days<=30]
    out.append(dict(h=h,subs=subs,n=len(rows),oldest=str(min(ds)),newest=str(max(ds)),span_days=span,posts_per_week=round(per_week,1),
        median=int(st.median(v)),p90=int(pct(v,.9)),max=max(v),top10_median=int(st.median(top10)),top3_share=round(top3share,2),
        med_dur=st.median(durs),topq_dur=st.median(topq),
        median_over_subs=round(st.median(v)/subs,2) if subs else None,
        pct_over_100k=round(sum(1 for x in v if x>=100000)/len(v),2),
        like_rate=round(st.median([r['like_count']/r['view_count'] for r in old if r['like_count'] and r['view_count']]),3),
        hash_in_title=round(sum('#' in r['title'] for r in rows)/len(rows),2),
        emoji_in_title=round(sum(bool(re.search('[\U0001F300-\U0001FAFF☀-➿]',r['title'])) for r in rows)/len(rows),2),
        caps_title=round(sum(sum(c.isupper() for c in r['title'])/max(1,sum(c.isalpha() for c in r['title']))>0.5 for r in rows)/len(rows),2)))
json.dump(out,open('channel_stats.json','w'),indent=1)
for o in out: print(o)
json.dump(allrows,open('all_shorts.json','w'),ensure_ascii=False)
