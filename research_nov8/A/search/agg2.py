import json,glob,collections
ch=collections.defaultdict(lambda:{'n':0,'views':[],'name':'','h':''})
v={}
for f in glob.glob('[qr]_*.json'):
    try: d=json.load(open(f))
    except: continue
    for e in d.get('entries',[]):
        if (e.get('duration') or 999)<=65 and e.get('channel_id'): v[e['id']]=e
for e in v.values():
    c=ch[e['channel_id']]; c['name']=e.get('channel'); c['h']=e.get('uploader_id'); c['n']+=1; c['views'].append(e.get('view_count') or 0)
print(len(v),len(ch))
rows=[(k,c) for k,c in ch.items()]
# rank by max views among channels with >=1 video >=50k
for k,c in sorted(rows,key=lambda x:-max(x[1]['views']))[:70]:
    print(c['h'],'|',c['name'],'| n',c['n'],'max',max(c['views']),'med',sorted(c['views'])[len(c['views'])//2])
print('---- top videos')
for e in sorted(v.values(),key=lambda e:-(e.get('view_count') or 0))[:90]:
    print(e.get('view_count'),e.get('duration'),e.get('uploader_id'),'|',e['title'][:80])
