import json,re,subprocess,time,sys
u={}
for l in open('raw_all.jsonl'):
    r=json.loads(l); u.setdefault(r['id'],r)
done={json.loads(l)['id'] for l in open('raw_meta.jsonl')}
try: done|={json.loads(l)['id'] for l in open('raw_meta_curl.jsonl')}
except: pass
ids=sorted([i for i,r in u.items() if r['duration']<=90 and i not in done], key=lambda i:u[i]['duration'])
out=open('raw_meta_curl.jsonl','a')
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/124 Safari/537.36"
for n,i in enumerate(ids):
    h=subprocess.run(["curl","-sL","-m","30","-A",UA,"-H","Cookie: CONSENT=YES+1; SOCS=CAI","https://www.youtube.com/watch?v="+i],capture_output=True).stdout.decode("utf8","ignore")
    def g(p):
        m=re.search(p,h); return m.group(1) if m else None
    m=re.search(r'"keywords":\[(.*?)\]',h)
    kw=json.loads('['+m.group(1)+']') if m else []
    sd=g(r'"shortDescription":"((?:[^"\\]|\\.)*)"')
    try: sd=json.loads('"'+sd+'"')[:400] if sd else None
    except: sd=None
    rec={'id':i,'title':u[i]['title'],'channel':u[i]['channel'],'channel_id':u[i]['channel_id'],'view_count':int(g(r'"viewCount":"(\d+)"') or 0) or u[i]['views'],'like_count':int(g(r'"likeCount":"(\d+)"') or 0) or None,'duration':u[i]['duration'],'upload_date':(g(r'"uploadDate":"(\d{4}-\d\d-\d\d)')),'tags':kw[:12],'description':sd}
    out.write(json.dumps(rec,ensure_ascii=False)+'\n'); out.flush()
    time.sleep(0.6)
print('done')
