import json,glob,os,re,datetime
R=os.path.expanduser('~/Developer/CDH/MoneyPrinterTurbo-Extended')
out=[]
for sd in sorted(glob.glob(R+'/storage/tasks/*/')):
    tid=os.path.basename(sd.rstrip('/'))
    sj=sd+'script.json'; qj=sd+'quality_report.json'; fm=sd+'final-1.mp4'
    if not os.path.exists(sj): continue
    try: s=json.load(open(sj))
    except: continue
    p=s.get('params',{})
    rec=dict(task_id=tid,mtime=datetime.datetime.fromtimestamp(os.path.getmtime(sj)).isoformat(),
      script=s.get('script') or p.get('video_script'),subject=p.get('video_subject'),hook=p.get('hook_text'),cta=p.get('cta_text'),
      has_final=os.path.exists(fm),final_path=fm if os.path.exists(fm) else None,
      voice_rate=p.get('voice_rate'),bgm_type=p.get('bgm_type'),bgm_volume=p.get('bgm_volume'),
      beat_plan=bool(p.get('beat_plan')),nbeats=len(p.get('beat_plan') or []))
    if p.get('beat_plan'):
        bp=p['beat_plan']
        rec['n_pinned_clips']=sum(len(b.get('clips') or []) for b in bp)
        rec['beats_with_clips']=sum(1 for b in bp if b.get('clips'))
    if os.path.exists(qj):
        try:
            q=json.load(open(qj));rec['duration']=q.get('duration')
            mp=q.get('media_plan',{});clips=mp.get('clips',[])
            ph=vid=0;phs=vid_s=0.0
            for c in clips:
                b=os.path.basename(c['path'])
                if re.match(r'^(shot_|clip_|vid|.*\.mp4\.seg)',b) or '.mp4.seg' in b: vid+=1;vid_s+=c['duration']
                else: ph+=1;phs+=c['duration']
            rec.update(n_clips=len(clips),n_photo=ph,n_video=vid,photo_s=round(phs,2),video_s=round(vid_s,2))
            rec['clip_names']=[os.path.basename(c['path']) for c in clips]
        except Exception as e: rec['qerr']=str(e)
    out.append(rec)
with open(R+'/research_nov8/D/task_index.jsonl','w') as f:
    for r in out: f.write(json.dumps(r)+'\n')
print(len(out),sum(1 for r in out if r.get('beat_plan')),sum(1 for r in out if r['has_final']))
