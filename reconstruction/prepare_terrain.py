"""Sample satellite vegetation colour into editable Blender density attributes."""
import json
import math
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter

ROOT=Path(__file__).resolve().parent
site=json.loads((ROOT/'site_data.json').read_text())
poly=np.asarray(site['outline'])
step=3.0
xs=np.arange(math.floor(poly[:,0].min()/step)*step,poly[:,0].max()+step,step)
ys=np.arange(math.floor(poly[:,1].min()/step)*step,poly[:,1].max()+step,step)
xx,yy=np.meshgrid(xs,ys)
x,y=xx.ravel(),yy.ravel()
inside=np.zeros(len(x),dtype=bool)
distance=np.full(len(x),1e9)
for a,b in zip(poly,np.roll(poly,-1,axis=0)):
    dx,dy=b-a
    t=np.clip(((x-a[0])*dx+(y-a[1])*dy)/(dx*dx+dy*dy),0,1)
    distance=np.minimum(distance,np.hypot(x-a[0]-t*dx,y-a[1]-t*dy))
    cross=((a[1]>y)!=(b[1]>y))
    if abs(dy)>1e-9:
        inside^=cross&(x<(b[0]-a[0])*(y-a[1])/dy+a[0])
fade=np.clip((distance-5)/30,0,1)
z=2.6+fade*(1.0+0.7*np.sin(x/83)*np.cos(y/109)+0.35*np.cos(y/39))
verts=np.stack([x,y,z],axis=1)
ny,nx=xx.shape
ids=np.arange(nx*ny).reshape(ny,nx)
a=ids[:-1,:-1].ravel();b=a+1;c=a+nx;d=c+1
faces=np.concatenate([np.stack([a,b,d],axis=1),np.stack([a,d,c],axis=1)])
valid=inside&(distance>4.1)
faces=faces[valid[faces].all(axis=1)]

image=np.asarray(Image.open(ROOT.parent/'SAT/GOOGLE_SAT_WM.tif').convert('RGB')
                 .filter(ImageFilter.GaussianBlur(2)),dtype=float)/255
px=(x/site['correction']-site['map_origin_image_empty'][0])/site['worldfile'][0]+site['image_size'][0]/2-.5
py=-(y/site['correction']-site['map_origin_image_empty'][1])/site['worldfile'][0]+site['image_size'][1]/2-.5
rgb=image[np.clip(py.astype(int),0,image.shape[0]-1),np.clip(px.astype(int),0,image.shape[1]-1)]
r,g,b=rgb.T
green=np.clip((g-(r+b)/2)*11+0.22,0,1)
dark=np.clip((.25-rgb.mean(axis=1))*4,0,1)
canopy=np.clip(green*.65+dark*.35,0,1)
edge=np.clip((distance-12)/18,0,1)*inside
open_ground=np.clip(1-canopy*1.5,.05,1)
attrs={
 'coconut_density':edge*(.10+.65*canopy),
 'broadleaf_density':edge*canopy,
 'scrub_density':edge*(.1+.7*canopy),
 'grass_density':edge*open_ground,
 'satellite_green':canopy,
 'wall_clearance':distance,
}
used=np.unique(faces)
remap=np.full(len(x),-1,dtype=np.int32);remap[used]=np.arange(len(used))
np.savez_compressed(ROOT/'terrain_samples.npz',verts=verts[used],faces=remap[faces],
                    **{k:v[used].astype(np.float32) for k,v in attrs.items()})
assert len(faces)>30000
assert verts[used,2].min()>2.5
print(json.dumps({'terrain_vertices':len(used),'triangles':len(faces),
                  'height_range_estimated_m':[float(verts[used,2].min()),float(verts[used,2].max())]}))
