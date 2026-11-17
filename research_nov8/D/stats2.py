import json,pandas as pd,numpy as np
from scipy import stats
df=pd.DataFrame(json.load(open('master.json')))
df['period']=np.where(df.date<'2026-10-29','P1','P2')
b=df[df.matched].copy()
b['ps']=pd.cut(b.photo_share,[-0.01,0.0,0.5,0.99,1.0],labels=['0% photo (all clips)','1-50%','51-99%','100% photo'])
pd.set_option('display.width',200)
print(b.groupby(['period','pipeline','ps'],observed=True).views.agg(['count','median',lambda x:(x<300).mean()]).round(2))
# Oct 22 - Oct 28 photo-only
x=b[(b.date>='2026-10-21')&(b.date<='2026-10-28')][['date','hour','views','photo_share','n_photo','n_video','title']]
print(x.to_string())
