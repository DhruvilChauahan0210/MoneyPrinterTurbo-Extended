import json,subprocess,re,os,sys
R=os.path.expanduser('~/Developer/CDH/MoneyPrinterTurbo-Extended')
FF=R+'/.venv/bin/ffmpeg'
out={}
for l in open('task_index.jsonl'):
    r=json.loads(l)
    if not r['final_path']: continue
    p=subprocess.run([FF,'-hide_banner','-i',r['final_path'],'-vf',"scale=135:-1,select='gt(scene,0.3)',metadata=print:file=-",'-an','-f','null','-'],capture_output=True,text=True)
    ts=[float(x) for x in re.findall(r'pts_time:([\d.]+)',p.stdout)]
    out[r['task_id']]=ts
json.dump(out,open('cuts.json','w'))
print(len(out))
