"""Background camera proof, without altering the live Blender session."""
import bpy, json, collections, math
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

ROOT=Path(r'B:\Blender\Blender_Fort_Reconstruction\reconstruction')
s=bpy.data.scenes['Sindhudurg_1to1']
bpy.context.window.scene=s
s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=20
s.cycles.use_denoising=True
s.render.resolution_x=1400;s.render.resolution_y=1050;s.render.resolution_percentage=100
s.render.image_settings.file_format='PNG'
s.frame_set(1)
s.camera=bpy.data.objects['SD2_CAM_Aerial']
s.render.filepath=str(ROOT/'Sindhudurg_aerial.png')
bpy.ops.render.render(write_still=True)
(ROOT/'render_status.json').write_text(json.dumps({'stage':'Aerial complete; rendering north-up plan'}))
s.camera=bpy.data.objects['SD2_CAM_Top_North']
s.render.resolution_x=1100;s.render.resolution_y=1500
s.camera.data.ortho_scale=920
s.render.filepath=str(ROOT/'Sindhudurg_plan.png')
bpy.ops.render.render(write_still=True)
(ROOT/'render_status.json').write_text(json.dumps({'stage':'Plan complete; rendering interior detail'}))

# A feature camera proves wall contact and plant shape at an inspectable scale.
cd=bpy.data.cameras.new('CHECK_Camera');cam=bpy.data.objects.new('CHECK_Camera',cd)
s.collection.objects.link(cam)
cam.location=(150,-100,100);target=Vector((45,25,3))
cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
cd.type='ORTHO';cd.ortho_scale=180;cd.clip_end=5000;s.camera=cam
s.render.resolution_x=1400;s.render.resolution_y=1050
s.render.filepath=str(ROOT/'Sindhudurg_interior.png')
bpy.ops.render.render(write_still=True)
bpy.data.objects.remove(cam,do_unlink=True)

# New slotted actions are sampled through evaluated transforms, rather than assumed keys.
poses=[]
cam=bpy.data.objects['SD2_CAM_Aerial'];s.camera=cam
for f in [1,48,120,192,240]:
    s.frame_set(f);bpy.context.view_layer.update()
    pos=cam.evaluated_get(bpy.context.evaluated_depsgraph_get()).matrix_world.translation
    poses.append({'frame':f,'camera_position':list(pos)})
assert (Vector(poses[0]['camera_position'])-Vector(poses[-1]['camera_position'])).length>100
s.frame_set(1);bpy.context.view_layer.update()
dg=bpy.context.evaluated_depsgraph_get();counts=collections.Counter()
for item in dg.object_instances:
    if item.is_instance and item.parent:counts[item.parent.original.name]+=1
wall=bpy.data.objects['SD2_Wall_Mapped_Rampart'];ev=wall.evaluated_get(dg)
me=ev.to_mesh();edgecounts=collections.Counter()
for p in me.polygons:
    ids=list(p.vertices)
    for a,b in zip(ids,ids[1:]+ids[:1]):edgecounts[tuple(sorted((a,b)))]+=1
wall_stats={'verts':len(me.vertices),'faces':len(me.polygons),
            'edges_not_two_faces':sum(n!=2 for n in edgecounts.values()),
            'z_bounds':[min(v.co.z for v in me.vertices),max(v.co.z for v in me.vertices)]}
ev.to_mesh_clear()
assert wall_stats['edges_not_two_faces']==0,wall_stats
assert len(bpy.data.scenes['Sindhudurg'].objects)==480
assert all(counts['SD2_Scatter_'+k]>0 for k in ['Coconut','Broadleaf','Scrub','Grass'])
assert not any(n.bl_idname=='GeometryNodeRealizeInstances' for g in bpy.data.node_groups
               if g.name.startswith('SD2_') for n in g.nodes)
report={'instances':dict(counts),'wall_geometry':wall_stats,'camera_motion':poses,
        'original_scene_objects':480,'new_scene_objects':len(s.objects),
        'renders':['Sindhudurg_aerial.png','Sindhudurg_plan.png','Sindhudurg_interior.png']}
(ROOT/'validation.json').write_text(json.dumps(report,indent=2))
(ROOT/'render_status.json').write_text(json.dumps({'stage':'complete'}))
print('SINDHUDURG_VALIDATION '+json.dumps(report))
