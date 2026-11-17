import json,glob,collections
ch=collections.defaultdict(lambda:{'n':0,'views':[],'name':'','h':'','titles':[]})
seen=set()
for f in glob.glob('q_*.json'):
    try: d=json.load(open(f))
    except: continue
    for e in d.get('entries',[]):
        if e['id'] in seen: continue
        seen.add(e['id'])
        if (e.get('duration') or 999)>65: continue
        c=ch[e.get('channel_id')]
        c['name']=e.get('channel'); c['h']=e.get('uploader_id'); c['n']+=1; c['views'].append(e.get('view_count') or 0); c['titles'].append((e.get('view_count'),e['title']))
print(len(seen),len(ch))
for k,c in sorted(ch.items(),key=lambda x:-x[1]['n']):
    print(k,c['h'],c['name'],c['n'],max(c['views']),sorted(c['views'])[len(c['views'])//2])
