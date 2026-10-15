"""Recover the user's satellite trace in ground metres; no Blender dependency."""
import collections
import json
import math
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent
WORK = ROOT.parent
mesh = json.loads((ROOT / 'draft_trace_mesh.json').read_text())
meta = json.loads((ROOT / 'draft_sat_meta.json').read_text())
wf = [float(x) for x in (WORK / 'SAT/GOOGLE_SAT_WM.wld').read_text().split()]
im = Image.open(WORK / 'SAT/GOOGLE_SAT_WM.tif').convert('RGB')
width, height = im.size
pixel_m = wf[0]
assert abs(meta['scale'][0] - width * pixel_m) < 0.01
centre_merc = (wf[4] + (width - 1) * pixel_m / 2,
               wf[5] - (height - 1) * pixel_m / 2)
latitude = math.degrees(math.atan(math.sinh(centre_merc[1] / 6378137)))
ground_correction = math.cos(math.radians(latitude))

counts = collections.Counter(tuple(sorted((face[i], face[(i+1) % len(face)])))
                             for face in mesh['faces'] for i in range(len(face)))
edges = [e for e, n in counts.items() if n == 1
         and min(mesh['verts'][i][2] for i in e) > 10]
adj = collections.defaultdict(list)
for a, b in edges:
    adj[a].append(b)
    adj[b].append(a)
assert all(len(v) == 2 for v in adj.values()), 'Expected one simple top boundary'
start = min(adj)
order, previous, current = [start], None, start
while True:
    nxt = next(i for i in adj[current] if i != previous)
    if nxt == start:
        break
    assert nxt not in order, 'Trace revisits a vertex before closing'
    order.append(nxt)
    previous, current = current, nxt
assert len(order) == len(adj) == 300
outline = [[mesh['verts'][i][0]*ground_correction,
            mesh['verts'][i][1]*ground_correction] for i in order]
outline = [p for i,p in enumerate(outline) if math.dist(p,outline[i-1]) > 0.05]
assert all(math.dist(a,b)>0.05 for a,b in zip(outline,outline[1:]+outline[:1]))
area = sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(outline,outline[1:]+outline[:1])) / 2
if area < 0:
    outline.reverse()
area = abs(area)
perimeter = sum(math.dist(a,b) for a,b in zip(outline,outline[1:]+outline[:1]))

def pixel_to_xy(p):
    # Image-empty centre sits halfway between the two central pixel centres.
    return [(meta['location'][0] + (p[0]+0.5-width/2)*pixel_m)*ground_correction,
            (meta['location'][1] - (p[1]+0.5-height/2)*pixel_m)*ground_correction]

def xy_to_pixel(p):
    return [(p[0]/ground_correction-meta['location'][0])/pixel_m+width/2-0.5,
            -(p[1]/ground_correction-meta['location'][1])/pixel_m+height/2-0.5]

assert 160000 < area < 220000, area
assert 2400 < perimeter < 3600, perimeter
assert math.dist(pixel_to_xy(xy_to_pixel(outline[0])),outline[0]) < 1e-7

# Visible routes are traced; branch paths and obscured building identities remain estimates.
paths_px = [
    [[1164,440],[1140,450],[1121,469],[1090,490],[1050,508],[1019,527],[990,540],[977,553]],
    [[979,554],[970,577],[969,608],[979,635],[979,665],[979,695],[975,715]],
    [[977,554],[935,547],[904,552],[873,575],[849,602],[826,642],[822,676],[817,697]],
    [[818,698],[850,696],[881,700],[914,694],[943,689],[979,695]],
    [[818,698],[801,718],[813,733],[841,731],[876,731]],
    [[979,695],[1007,727],[1036,752],[1068,775],[1100,803]],
]
data = dict(outline=outline, area_m2=area, perimeter_m=perimeter,
            correction=ground_correction, latitude=latitude,
            satellite_pixel_m=abs(pixel_m)*ground_correction,
            map_origin_image_empty=meta['location'][:2], image_size=[width,height],
            worldfile=wf, paths_px=paths_px,
            paths=[[pixel_to_xy(p) for p in lp] for lp in paths_px],
            uncertainty_m=3.5,
            gate_px=[1164,438], gate_xy=pixel_to_xy([1164,438]),
            jetty_px=[[1166,402],[1183,387],[1210,369],[1235,350],[1251,327],[1268,299]],
            beach_px=[[968,453],[978,438],[985,422]],
            shivrajeshwar_px=[978,545], mahadev_px=[945,548], kund_px=[945,558],
            # Count is documented, contour is image-based; no invented evenly-spaced towers.
            documented_bastions=42)
(ROOT / 'site_data.json').write_text(json.dumps(data,indent=2))

draw = ImageDraw.Draw(im)
pp = [tuple(xy_to_pixel(p)) for p in outline]
draw.line(pp+[pp[0]],fill=(255,220,20),width=2)
for path in paths_px:
    draw.line([tuple(p) for p in path], fill=(70,220,255), width=2)
draw.text((720,230),f'{area/10000:.2f} ha  |  {perimeter:.0f}m perimeter  |  north up',fill='white')
im.crop((700,220,1290,960)).save(ROOT / 'mapped_plan.png')
print(json.dumps({k:data[k] for k in ['area_m2','perimeter_m','correction','satellite_pixel_m']}))
