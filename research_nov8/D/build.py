import json,glob,datetime,re
rows={}
for f in sorted(glob.glob('raw_full*.jsonl')):
    for l in open(f):
        try: d=json.loads(l)
        except: continue
        rows[d['id']]=d
IST=datetime.timezone(datetime.timedelta(hours=5,minutes=30))
out=[]
for d in rows.values():
    ts=d.get('timestamp')
    if not ts: continue
    dt=datetime.datetime.fromtimestamp(ts,IST)
    if dt.date()<datetime.date(2026,8,1): continue
    out.append(dict(id=d['id'],title=d['title'],view_count=d.get('view_count'),like_count=d.get('like_count'),
      comment_count=d.get('comment_count'),duration=d.get('duration'),upload_date=d.get('upload_date'),timestamp=ts,
      ist_datetime=dt.isoformat(),ist_date=dt.date().isoformat(),ist_hour=dt.hour,ist_weekday=dt.strftime('%A'),
      description=d.get('description'),tags=d.get('tags'),url='https://www.youtube.com/shorts/'+d['id']))
out.sort(key=lambda r:r['timestamp'])
with open('channel_shorts.jsonl','w') as f:
    for r in out: f.write(json.dumps(r,ensure_ascii=False)+'\n')
print(len(out),out[0]['ist_date'],out[-1]['ist_date'])
