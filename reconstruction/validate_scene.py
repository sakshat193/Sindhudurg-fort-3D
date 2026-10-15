"""Focused geometry, parameter propagation and evaluated scatter proof in Blender."""
import bpy, json, collections, math
from pathlib import Path
import numpy as np
ROOT=Path(r'B:\Blender\Blender_Fort_Reconstruction\reconstruction')
s=bpy.data.scenes['Sindhudurg_1to1']
assert bpy.context.scene==s
s.frame_set(2);s.frame_set(1);bpy.context.view_layer.update()

def max_z(name):
    o=bpy.data.objects[name].evaluated_get(bpy.context.evaluated_depsgraph_get())
    me=o.to_mesh()
    try:return max(v.co.z for v in me.vertices)
    finally:o.to_mesh_clear()

wall=bpy.data.objects['SD2_Wall_Mapped_Rampart']
g=bpy.data.node_groups['SD2_GN_Rampart_Dimensions']
interface_socket=next(i for i in g.interface.items_tree if i.name=='Wall height m' and i.in_out=='INPUT')
socket=getattr(wall.modifiers[0].properties.inputs,interface_socket.identifier)
old=socket.value
before=[max_z('SD2_Wall_Mapped_Rampart'),max_z('SD2_Bastion_Fighting_Decks')]
try:
    socket.value=old+1;g.update_tag()
    wall.update_tag(refresh={'DATA'});bpy.context.view_layer.update()
    after=[max_z('SD2_Wall_Mapped_Rampart'),max_z('SD2_Bastion_Fighting_Decks')]
    assert abs(after[0]-before[0]-1)<1e-4,(before,after)
    assert abs(after[1]-before[1]-.9125)<1e-4,(before,after)
finally:
    socket.value=old;g.update_tag()
    wall.update_tag(refresh={'DATA'});bpy.context.view_layer.update()

dg=bpy.context.evaluated_depsgraph_get()
names=['SD2_Scatter_'+k for k in ['Coconut','Broadleaf','Scrub','Grass']]
points={name:[] for name in names}
radii={k:max(math.hypot(v.co.x,v.co.y) for v in bpy.data.objects['SD2_Prototype_'+k].data.vertices)
       for k in ['Coconut','Broadleaf','Scrub','Grass']}
instance_counts=collections.Counter()
for item in dg.object_instances:
    if not item.is_instance or not item.parent:continue
    name=item.parent.original.name;instance_counts[name]+=1
    if name in points:
        kind=name.removeprefix('SD2_Scatter_');pos=item.matrix_world.translation
        scale=item.matrix_world.to_scale()
        points[name].append([pos.x,pos.y,radii[kind]*max(scale.x,scale.y)])
arrays={k:np.asarray(v,dtype=float).reshape((-1,3)) for k,v in points.items()}
counts={k:len(v) for k,v in arrays.items()}
assert all(counts.values()),counts
gaps={}
for i,a in enumerate(names):
    for b in names[i:]:
        aa,bb=arrays[a],arrays[b];smallest=1e9
        for start in range(0,len(aa),128):
            block=aa[start:start+128]
            diff=np.hypot(block[:,None,0]-bb[None,:,0],block[:,None,1]-bb[None,:,1])
            diff-=block[:,None,2]+bb[None,:,2]
            if a==b:
                for local in range(len(block)):diff[local,start+local]=1e9
            smallest=min(smallest,float(diff.min()))
        gaps[a+' / '+b]=round(smallest,4)
assert min(gaps.values())>=.30,gaps
assert not any(n.bl_idname=='GeometryNodeRealizeInstances' for group in bpy.data.node_groups
               if group.name.startswith('SD2_') for n in group.nodes)
assert len(bpy.data.scenes['Sindhudurg'].objects)==480
assert len([o for o in s.objects if o.name.startswith('SD2_Bastion_') and o.type=='EMPTY'])==42
mesh_checks={}
for name in ['SD2_Wall_Mapped_Rampart','SD2_Bastion_Fighting_Decks']:
    ev=bpy.data.objects[name].evaluated_get(dg);me=ev.to_mesh();edges=collections.Counter()
    for p in me.polygons:
        ids=list(p.vertices)
        for a,b in zip(ids,ids[1:]+ids[:1]):edges[tuple(sorted((a,b)))]+=1
    mesh_checks[name]={'vertices':len(me.vertices),'faces':len(me.polygons),
                       'non_manifold_edges':sum(n!=2 for n in edges.values())}
    ev.to_mesh_clear()
    assert mesh_checks[name]['non_manifold_edges']==0,mesh_checks
report={'counts':counts,'minimum_planar_footprint_gaps_m':gaps,'passed':True,
        'method':'Evaluated instance transforms and conservative horizontal prototype radii',
        'wall_height_propagation':{'wall_delta_m':after[0]-before[0],'bastion_deck_delta_m':after[1]-before[1]},
        'mesh_checks':mesh_checks,'original_objects':480,'instances':dict(instance_counts),
        'bastion_features':42,'clear_projecting_arcs':33,'provisional_corner_terraces':9}
(ROOT/'scatter_collision_validation.json').write_text(json.dumps(report,indent=2))
result=report
