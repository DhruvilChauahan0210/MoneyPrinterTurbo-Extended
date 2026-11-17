import json,glob,re,os,collections,math
STOP=set("the a an and of to in on at for with was were is it his he her she that this as by from be had has have but not no they them their then than so up out after before over into who what when how which one two just only still all more most been being its i you we our about also too very can could would will did do does".split())
def toks(s):
    s=re.sub(r'#\w+','',s.lower())
    s=s.replace("’","'")
    w=re.findall(r"[a-z0-9àéíóúñçüöä']+",s)
    w=[x.strip("'") for x in w]
    # number words -> digits-ish normalisation left simple
    return [x for x in w if x not in STOP and len(x)>1]
rows={}
for f in glob.glob('raw_full*.jsonl'):
    for l in open(f):
        d=json.loads(l);rows[d['id']]=d
tasks=[json.loads(l) for l in open('task_index.jsonl')]
for t in tasks:
    txt=' '.join(filter(None,[t.get('script'),t.get('subject'),t.get('hook')]))
    t['_t']=collections.Counter(toks(txt))
N=len(tasks)
df=collections.Counter()
for t in tasks:
    for w in t['_t']: df[w]+=1
idf={w:math.log((N+1)/(c+1))+1 for w,c in df.items()}
def vec(c): 
    return {w:idf.get(w,math.log(N+1)+1) for w in c}
def sim(a,b):
    va=vec(a);vb=vec(b)
    num=sum(min(a[w],b[w])*va[w] for w in a if w in b)
    na=sum(va[w]*a[w] for w in a);nb=sum(vb[w]*b[w] for w in b)
    return num/math.sqrt(na*nb) if na and nb else 0
res={}
for vid,d in rows.items():
    dt=toks(d['title']+' '+re.sub(r'Follow.*','',d['description'],flags=re.S))
    dc=collections.Counter(dt)
    best=[]
    for t in tasks:
        if t.get('duration') is None: continue
        s=sim(dc,t['_t'])
        dd=abs((t['duration'] or 0)-d['duration'])
        best.append((s-0.02*min(dd,10),s,dd,t))
    best.sort(key=lambda x:-x[0])
    b=best[0]
    res[vid]=dict(task_id=b[3]['task_id'],sim=round(b[1],3),ddur=round(b[2],2),score=round(b[0],3),
       second=round(best[1][1],3) if len(best)>1 else None)
json.dump(res,open('match_raw.json','w'))
import sys
if len(sys.argv)>1:
    for vid in sorted(rows,key=lambda v:rows[v]['upload_date'],reverse=True)[:int(sys.argv[1])]:
        m=res[vid];t=[x for x in tasks if x['task_id']==m['task_id']][0]
        print(rows[vid]['upload_date'],rows[vid]['duration'],rows[vid]['title'][:45],'||',m['sim'],m['ddur'],'|',(t['subject'] or '')[:60])
