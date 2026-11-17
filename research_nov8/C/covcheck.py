import json,glob,re,sys
docs={}
for f in glob.glob('batch_*.json')+glob.glob('topics_nov13_27/*.json')+glob.glob('topics_nov13_27/finish/*.json'):
    try: d=json.load(open(f))
    except: continue
    txt=json.dumps(d,ensure_ascii=False)
    # keep only subject+script text
    parts=[]
    def w(o):
        if isinstance(o,dict):
            for k,v in o.items():
                if k in('video_subject','video_script','script','subject','topic','title','hook','beats','narration','text','query','queries'): parts.append(json.dumps(v,ensure_ascii=False))
                else: w(v)
        elif isinstance(o,list):
            for v in o: w(v)
    w(d)
    docs[f]=(' '.join(parts) or txt)
def cov(rx):
    r=re.compile(rx,re.I)
    return [f for f,t in docs.items() if r.search(t)]
if __name__=='__main__':
    for rx in sys.argv[1:]:
        m=cov(rx); print(f"{len(m):3d} {rx} -> {[x.replace('batch_','').replace('.json','') for x in m[:8]]}")
