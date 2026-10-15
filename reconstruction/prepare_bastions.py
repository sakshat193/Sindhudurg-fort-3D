"""Identify mapped salient arcs for fighting decks, with a reviewable overlay."""
import json
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
ROOT=Path(__file__).resolve().parent
data=json.loads((ROOT/'site_data.json').read_text())
p=np.asarray(data['outline'])
prev=p-np.roll(p,1,axis=0);nxt=np.roll(p,-1,axis=0)-p
ang=np.degrees(np.arctan2(prev[:,0]*nxt[:,1]-prev[:,1]*nxt[:,0],(prev*nxt).sum(axis=1)))
neck=np.where(ang < -25)[0]
candidates=[]
for a,b in zip(neck,np.roll(neck,-1)):
    ids=(np.arange(a,a+1+(b-a)%len(p)))%len(p)
    pp=p[ids];turn=ang[ids[1:-1]].sum()
    chord=np.linalg.norm(pp[-1]-pp[0])
    area=abs(np.sum(pp[:,0]*np.roll(pp[:,1],-1)-pp[:,1]*np.roll(pp[:,0],-1))/2)
    if len(ids)>=4 and turn>80:
        candidates.append(dict(ids=ids.tolist(),chord=round(float(chord),1),
                               area=round(float(area),1),turn=round(float(turn),1),
                               confidence='clear projecting arc'))
# Additional corner/entry positions are visible but their necks are ambiguous at
# this resolution. These stay labelled provisional; no outline is moved.
for a,b in [(36,42),(94,98),(111,117),(212,218),(261,266),(272,279),(296,3),(24,27),(150,153)]:
    ids=(np.arange(a,a+1+(b-a)%len(p)))%len(p)
    candidates.append(dict(ids=ids.tolist(),confidence='provisional corner or entry terrace'))
assert len(candidates)==42
(ROOT/'bastion_candidates.json').write_text(json.dumps(candidates,indent=2))
im=Image.open(ROOT.parent/'SAT/GOOGLE_SAT_WM.tif').convert('RGB');dr=ImageDraw.Draw(im)
for k,c in enumerate(candidates):
    center=p[c['ids']].mean(axis=0)
    x=(center[0]/data['correction']-data['map_origin_image_empty'][0])/data['worldfile'][0]+896-.5
    y=-(center[1]/data['correction']-data['map_origin_image_empty'][1])/data['worldfile'][0]+512-.5
    dr.ellipse((x-5,y-5,x+5,y+5),outline='yellow',width=2)
    dr.text((x+6,y-8),str(k+1),fill='yellow')
im.crop((700,220,1240,960)).resize((1080,1480)).save(ROOT/'bastion_candidates.png')
print('Candidates:',len(candidates))
print([(c['ids'][0],c['ids'][-1],c['confidence']) for c in candidates])
