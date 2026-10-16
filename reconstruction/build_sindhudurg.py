"""Editable metre-scale reconstruction. Run stages inside the connected Blender.

The original Sindhudurg scene is protected. No paid generation or realized scatter.
shortcut: terrain heights and obscured feature positions are estimates; replace
with a ground survey when elevation-level accuracy is required.
"""
import bpy, bmesh, json, math, random
from pathlib import Path
import numpy as np
from mathutils import Vector
from mathutils.geometry import tessellate_polygon

ROOT=Path(r'B:\Blender\Blender_Fort_Reconstruction\reconstruction')
SITE=json.loads((ROOT/'data'/'site_data.json').read_text())
TRACE=SITE['outline']
SCENE='Sindhudurg_1to1'
PREFIX='SD2_'
HEIGHT=9.144
THICKNESS=3.6576
TOE=.4

# Reuse the existing mesh accumulator and offset geometry, with SD2 material ownership.
exec(compile((ROOT/'sd_core.py').read_text(),str(ROOT/'sd_core.py'),'exec'),globals())
SCENE_NAME=SCENE
_old_mat=mat

def material(name):
    target=PREFIX+name.removeprefix('SD_')
    m=bpy.data.materials.get(target)
    if m is None:
        m=_old_mat(name).copy(); m.name=target
    return m
mat=material

def sc():
    return bpy.data.scenes[SCENE]

def collection(name):
    name=PREFIX+name
    c=bpy.data.collections.get(name)
    if c is None:
        c=bpy.data.collections.new(name);sc().collection.children.link(c)
    return c

def empty_collection(name):
    c=collection(name)
    for o in list(c.objects):
        assert o.name.startswith(PREFIX)
        bpy.data.objects.remove(o,do_unlink=True)
    return c

def obj_mesh(name,verts,faces,c,mats=(),edges=()):
    name=PREFIX+name
    me=bpy.data.meshes.new(name)
    me.from_pydata(verts,edges,faces);me.update()
    for m in mats: me.materials.append(m)
    o=bpy.data.objects.new(name,me);c.objects.link(o)
    return o

def attr(o,name,values,kind='FLOAT'):
    a=o.data.attributes.get(name)
    if a is None:a=o.data.attributes.new(name,kind,'POINT')
    assert a.data_type==kind and a.domain=='POINT'
    a.data.foreach_set('vector' if kind=='FLOAT_VECTOR' else 'value',
                       np.asarray(values,dtype=np.float32).ravel())
    return a

def pixel(p):
    a=SITE['worldfile'][0];co=SITE['correction'];w,h=SITE['image_size']
    dx,dy=SITE['map_origin_image_empty']
    return ((dx+(p[0]+.5-w/2)*a)*co,(dy-(p[1]+.5-h/2)*a)*co)

def ground_z(x,y):
    distance=dist_to_poly(x,y,TRACE)
    fade=max(0,min(1,(distance-5)/30))
    return 2.6+fade*(1+.7*math.sin(x/83)*math.cos(y/109)+.35*math.cos(y/39))

def graph(name,inputs=()):
    name=PREFIX+name
    old=bpy.data.node_groups.get(name)
    if old:
        assert old.users==0, f'Clear managed modifier before rebuilding {name}'
        bpy.data.node_groups.remove(old)
    g=bpy.data.node_groups.new(name,'GeometryNodeTree')
    g.interface.new_socket(name='Geometry',in_out='INPUT',socket_type='NodeSocketGeometry')
    g.interface.new_socket(name='Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
    for key,kind,value in inputs:
        s=g.interface.new_socket(name=key,in_out='INPUT',socket_type=kind)
        s.default_value=value
        if kind=='NodeSocketFloat':s.min_value=0;s.max_value=100
    gi=g.nodes.new('NodeGroupInput');gi.location=(-800,0)
    go=g.nodes.new('NodeGroupOutput');go.location=(700,0)
    return g,gi,go

def add_node(g,kind,label,x,y):
    n=g.nodes.new(kind);n.label=label;n.location=(x,y);return n

def modifier(o,g):
    m=o.modifiers.new(g.name,'NODES');m.node_group=g;return m

def copy_asset(source,name,c,location=None,rotation=None,scale=None):
    src=bpy.data.objects[source]
    o=src.copy();o.name=PREFIX+name
    # One copied mesh per source datablock, preserving shared data between instances.
    if src.type=='MESH':
        dn=PREFIX+src.data.name
        me=bpy.data.meshes.get(dn)
        if me is None:
            me=src.data.copy();me.name=dn
            for i,m in enumerate(list(me.materials)):
                if m and m.name.startswith('SD_'):me.materials[i]=material(m.name)
        o.data=me
    o.animation_data_clear();c.objects.link(o)
    if location is not None:o.location=location
    if rotation is not None:o.rotation_euler=rotation
    if scale is not None:o.scale=scale
    o['accuracy']='Rough existing asset; placement from imagery where visible; elevations estimated'
    return o

def setup():
    assert 'Sindhudurg' in bpy.data.scenes
    assert len(bpy.data.scenes['Sindhudurg'].objects)==480
    if SCENE not in bpy.data.scenes:
        s=bpy.data.scenes.new(SCENE)
    else:s=sc()
    s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
    s.unit_settings.length_unit='METERS'
    s['ground_m_per_pixel']=SITE['satellite_pixel_m']
    s['enclosed_area_m2']=SITE['area_m2'];s['mapped_perimeter_m']=SITE['perimeter_m']
    s['documented_bastions']=42
    s['accuracy']='1:1 ground metre scale; footprint traced from supplied satellite; heights estimated except nominal wall dimension'
    s['wall_height_definition']='9.144m from assumed toe to continuous parapet crest; embrasure cheeks extend above crest'
    s['sources']='See SD2_RECONSTRUCTION_NOTES and reconstruction/PLAN.md'
    s.render.engine='CYCLES';s.cycles.samples=32;s.cycles.use_denoising=True
    s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.resolution_percentage=100
    s.render.fps=24;s.frame_start=1;s.frame_end=240
    s.view_settings.view_transform='AgX'
    world=bpy.data.worlds.get(PREFIX+'World')
    if world is None:world=bpy.data.scenes['Sindhudurg'].world.copy();world.name=PREFIX+'World'
    s.world=world
    bg=next(n for n in world.node_tree.nodes if n.type=='BACKGROUND')
    bg.inputs['Color'].default_value=(.48,.65,.8,1);bg.inputs['Strength'].default_value=.45
    bpy.context.window.scene=s
    return {'scene':s.name,'original_protected_objects':480}

def make_wall():
    c=empty_collection('10_Fortifications')
    profile=[(-.15,0),(1,0),(1,.9125),(.20,.9125),(.20,1),(0,1)]
    ns=seg_normals(TRACE);directions=[]
    for i in range(len(TRACE)):
        m=ns[i-1]+ns[i]
        m=ns[i].copy() if m.length<1e-6 else m.normalized()
        directions.append(m/max(.4,m.dot(ns[i])))
    verts=[];offsets=[];fractions=[];faces=[];indices=[]
    for p,n in zip(TRACE,directions):
        for w,z in profile:
            verts.append((p[0]+n.x*w*THICKNESS,p[1]+n.y*w*THICKNESS,TOE+z*HEIGHT))
            offsets.append((n.x*w,n.y*w,0));fractions.append(z)
    L=len(profile)
    for i in range(len(TRACE)):
        j=(i+1)%len(TRACE)
        for k in range(L):
            q=(k+1)%L
            faces.append((i*L+k,j*L+k,j*L+q,i*L+q))
            indices.append([0,1,2,1,2,0][k])
    o=obj_mesh('Wall_Mapped_Rampart',verts,faces,c,
               [material('SD_Stone_Wall'),material('SD_Stone_Wall_Inner'),material('SD_Stone_Walkway')])
    o.data.polygons.foreach_set('material_index',indices)
    bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
    attr(o,'width_direction',offsets,'FLOAT_VECTOR');attr(o,'height_fraction',fractions)
    g,gi,go=graph('GN_Rampart_Dimensions',[
        ('Wall height m','NodeSocketFloat',HEIGHT),('Wall thickness m','NodeSocketFloat',THICKNESS)])
    wd=add_node(g,'GeometryNodeInputNamedAttribute','Mapped width direction',-750,-150);wd.data_type='FLOAT_VECTOR';wd.inputs['Name'].default_value='width_direction'
    hf=add_node(g,'GeometryNodeInputNamedAttribute','Normalized vertical profile',-750,-380);hf.data_type='FLOAT';hf.inputs['Name'].default_value='height_fraction'
    w=add_node(g,'ShaderNodeMath','Thickness adjustment in metres',-500,-90);w.operation='SUBTRACT';w.inputs[1].default_value=THICKNESS
    h=add_node(g,'ShaderNodeMath','Height adjustment in metres',-500,-330);h.operation='SUBTRACT';h.inputs[1].default_value=HEIGHT
    width=add_node(g,'ShaderNodeVectorMath','Offset along mapped wall normal',-280,-100);width.operation='SCALE'
    hz=add_node(g,'ShaderNodeMath','Scale profile height',-280,-330);hz.operation='MULTIPLY'
    cv=add_node(g,'ShaderNodeCombineXYZ','Vertical adjustment',-90,-330)
    plus=add_node(g,'ShaderNodeVectorMath','Combine dimensional offsets',150,-120);plus.operation='ADD'
    sp=add_node(g,'GeometryNodeSetPosition','Editable wall dimensions',410,30)
    link=g.links.new
    link(gi.outputs['Wall thickness m'],w.inputs[0]);link(gi.outputs['Wall height m'],h.inputs[0])
    link(wd.outputs['Attribute'],width.inputs[0]);link(w.outputs[0],width.inputs['Scale'])
    link(hf.outputs['Attribute'],hz.inputs[0]);link(h.outputs[0],hz.inputs[1]);link(hz.outputs[0],cv.inputs['Z'])
    link(width.outputs['Vector'],plus.inputs[0]);link(cv.outputs[0],plus.inputs[1])
    link(gi.outputs['Geometry'],sp.inputs['Geometry']);link(plus.outputs[0],sp.inputs['Offset']);link(sp.outputs[0],go.inputs['Geometry'])
    modifier(o,g)
    o['trace_source']='Recovered from user Draft1.blend, corrected from EPSG:3857 to local ground metres'
    o['nominal_height_m']=HEIGHT;o['nominal_thickness_m']=THICKNESS
    o['bastions']='Projecting forms are integrated in the mapped perimeter, not evenly distributed towers'
    return {'wall_vertices':len(verts),'mapped_trace_points':len(TRACE),'area_m2':SITE['area_m2'],'perimeter_m':SITE['perimeter_m']}

def terrain():
    c=empty_collection('40_Terrain_Sea')
    samples=np.load(ROOT/'data'/'terrain_samples.npz')
    o=obj_mesh('Terrain_Interior',samples['verts'].tolist(),samples['faces'].tolist(),c,[material('SD_Ground_Soil')])
    for key in ('coconut_density','broadleaf_density','scrub_density','grass_density','satellite_green','wall_clearance'):
        attr(o,key,samples[key])
    o['height_source']='Estimated 2.6–4.65m; no usable island ground survey supplied'
    for f in o.data.polygons:f.use_smooth=True
    poly=offset(TRACE,THICKNESS)
    v=[Vector((x,y,2.52)) for x,y in poly]
    f=tessellate_polygon([v])
    obj_mesh('Terrain_Boundary_Fill',[tuple(p) for p in v],f,c,[material('SD_Ground_Soil')])
    # Shore ledge follows the actual wall rather than a made-up expanded ellipse.
    rings=[offset(TRACE,-q,max_miter=2.0) for q in (.55,5,12,24)]
    verts=[]
    for k,ring in enumerate(rings):
        for i,(x,y) in enumerate(ring):
            z=[.5,.05,-1.0,-3.8][k]+(.22*math.sin(i*2.3) if k in (1,2) else 0)
            verts.append((x,y,z))
    N=len(TRACE);faces=[]
    for k in range(3):
        for i in range(N):
            j=(i+1)%N;faces.append((k*N+i,(k+1)*N+i,(k+1)*N+j,k*N+j))
    shore=obj_mesh('Rock_Shore_Shelf',verts,faces,c,[material('SD_Rock_Island')])
    shore['accuracy']='Mapped perimeter; shore width and bathymetry estimated'
    # Ocean excludes the island: freshwater wells can sit below sea level without an ocean sheet crossing them.
    outside=[Vector((-3000,-3000,0)),Vector((3000,-3000,0)),Vector((3000,3000,0)),Vector((-3000,3000,0))]
    hole=[Vector((x,y,0)) for x,y in reversed(TRACE)]
    vv=outside+hole;ff=tessellate_polygon([outside,hole])
    obj_mesh('Ocean',[tuple(p) for p in vv],ff,c,[material('SD_Water_Sea')])
    return {'terrain_vertices':len(o.data.vertices),'terrain_triangles':len(o.data.polygons),'estimated_height_range_m':[2.59,4.65]}

def presentation():
    c=empty_collection('90_Presentation')
    target=Vector((45,-20,1))
    camdata=bpy.data.cameras.new(PREFIX+'CAM_Aerial');cam=bpy.data.objects.new(PREFIX+'CAM_Aerial',camdata);c.objects.link(cam)
    cam.location=(850,-1100,1100);cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
    camdata.type='ORTHO';camdata.ortho_scale=1080;camdata.clip_end=10000
    cd=bpy.data.cameras.new(PREFIX+'CAM_Top_North');top=bpy.data.objects.new(PREFIX+'CAM_Top_North',cd);c.objects.link(top)
    top.location=(45,-20,1200);top.rotation_euler=(0,0,0);cd.type='ORTHO';cd.ortho_scale=1500;cd.clip_end=10000
    ld=bpy.data.lights.new(PREFIX+'LGT_Sun','SUN');sun=bpy.data.objects.new(PREFIX+'LGT_Sun',ld);c.objects.link(sun)
    ld.energy=2.8;ld.angle=math.radians(2);ld.color=(1,.95,.86)
    sun.rotation_euler=(math.radians(35),math.radians(-25),math.radians(-35))
    sun['purpose']='Reveal wall height, canopy structure and coastal relief'
    sun['motivation']='Oblique coastal daylight';sc().camera=cam
    for area in bpy.context.window.screen.areas:
        if area.type=='VIEW_3D':
            sp=area.spaces.active;sp.clip_end=10000;sp.region_3d.view_perspective='CAMERA'
            sp.shading.type='SOLID';sp.shading.color_type='MATERIAL'
    return {'active_camera':cam.name,'top_camera':top.name}

def blockout():
    return {'setup':setup(),'wall':make_wall(),'terrain':terrain(),'presentation':presentation()}

def sample_route(points,spacing):
    out=[]
    for a,b in zip(points,points[1:]+points[:1]):
        a,b=Vector(a),Vector(b);d=b-a
        if d.length<.01:continue
        count=max(1,int(d.length/spacing))
        for k in range(count):
            p=a+d*((k+.5)/count)
            out.append((p,math.atan2(d.y,d.x)))
    return out

def point_instances(name,points,angles,proto,c):
    o=obj_mesh(name,points,[],c)
    attr(o,'instance_rotation',[(0,0,a) for a in angles],'FLOAT_VECTOR')
    g,gi,go=graph('GN_'+name)
    mtp=add_node(g,'GeometryNodeMeshToPoints','One point per mapped position',-560,40);mtp.mode='VERTICES'
    info=add_node(g,'GeometryNodeObjectInfo','Shared prototype',-500,-190)
    info.inputs['Object'].default_value=proto;info.inputs['As Instance'].default_value=True
    rot=add_node(g,'GeometryNodeInputNamedAttribute','Follow wall tangent',-270,-250);rot.data_type='FLOAT_VECTOR';rot.inputs['Name'].default_value='instance_rotation'
    inst=add_node(g,'GeometryNodeInstanceOnPoints','Keep repeated geometry instanced',120,20)
    g.links.new(gi.outputs['Geometry'],mtp.inputs['Mesh'])
    wall_info=geometry_info(g,bpy.data.objects[PREFIX+'Wall_Mapped_Rampart'],'Read live rampart height',-750,350)
    box=add_node(g,'GeometryNodeBoundBox','Live crest height',-520,350)
    sep=add_node(g,'ShaderNodeSeparateXYZ','Crest Z',-320,350)
    delta=add_node(g,'ShaderNodeMath','Change from nominal wall height',-100,350);delta.operation='SUBTRACT';delta.inputs[1].default_value=TOE+HEIGHT
    g.links.new(wall_info.outputs['Geometry'],box.inputs['Geometry']);g.links.new(box.outputs['Max'],sep.inputs[0]);g.links.new(sep.outputs['Z'],delta.inputs[0])
    if name=='Rampart_Embrasures':
        cv=add_node(g,'ShaderNodeCombineXYZ','Follow parapet crest',100,350)
        sp=add_node(g,'GeometryNodeSetPosition','Details follow wall height',-100,100)
        g.links.new(delta.outputs[0],cv.inputs['Z']);g.links.new(mtp.outputs['Points'],sp.inputs['Geometry']);g.links.new(cv.outputs[0],sp.inputs['Offset'])
        g.links.new(sp.outputs[0],inst.inputs['Points'])
    else:
        scale=add_node(g,'ShaderNodeMath','Stairs meet the live fighting deck',100,350);scale.operation='MULTIPLY_ADD'
        scale.inputs[1].default_value=.9125/((TOE+HEIGHT*.9125)-2.6);scale.inputs[2].default_value=1
        cv=add_node(g,'ShaderNodeCombineXYZ','Vertical stair scale',350,350);cv.inputs['X'].default_value=1;cv.inputs['Y'].default_value=1
        g.links.new(delta.outputs[0],scale.inputs[0]);g.links.new(scale.outputs[0],cv.inputs['Z']);g.links.new(cv.outputs[0],inst.inputs['Scale'])
        g.links.new(mtp.outputs['Points'],inst.inputs['Points'])
    g.links.new(info.outputs['Geometry'],inst.inputs['Instance']);g.links.new(rot.outputs['Attribute'],inst.inputs['Rotation'])
    g.links.new(inst.outputs['Instances'],go.inputs['Geometry']);modifier(o,g)
    o['instance_count']=len(points)
    return o

def wall_details():
    c=empty_collection('11_Rampart_Details');cp=collection('80_Instance_Assets')
    cp.hide_render=True
    old=bpy.data.objects.get(PREFIX+'Prototype_Embrasure_Cheek')
    if old:bpy.data.objects.remove(old,do_unlink=True)
    mb=MB();mb.box(0,0,0,1.10,.72,.45)
    proto=mb.make(PREFIX+'Prototype_Embrasure_Cheek',['SD_Stone_Parapet'],cp)
    proto.hide_render=True;proto.hide_set(True)
    sites=sample_route(offset(TRACE,.36),2.1)
    points=[(p.x,p.y,TOE+HEIGHT) for p,a in sites]
    o=point_instances('Rampart_Embrasures',points,[a for p,a in sites],proto,c)
    # Source stair geometry is reused with a height correction to the mapped wall deck.
    stair_src=bpy.data.objects['SD_Wall_Stair_01']
    proto=copy_asset('SD_Wall_Stair_01','Prototype_Wall_Stair',cp,location=(0,0,0),rotation=(0,0,0))
    proto.data=proto.data.copy()
    for v in proto.data.vertices:v.co.z*=((TOE+HEIGHT*.9125)-2.6)/9.1
    proto.hide_render=True;proto.hide_set(True)
    points=[];angles=[]
    for i in range(len(TRACE)):
        a=Vector(TRACE[i]);b=Vector(TRACE[(i+1)%len(TRACE)])
        tangent=(b-a).normalized();p=(a+b)/2+Vector((-tangent.y,tangent.x))*THICKNESS
        if (b-a).length<13 or (p-Vector(SITE['gate_xy'])).length<30:continue
        start=p-tangent*5.1
        if any(math.hypot(start.x-q[0],start.y-q[1])<62 for q in points):continue
        points.append((start.x,start.y,2.6));angles.append(math.atan2(tangent.y,tangent.x))
    stair=point_instances('Rampart_Stairs',points,angles,proto,c)
    return {'instanced_embrasure_cheeks':o['instance_count'],'instanced_stairs':stair['instance_count']}

def paths_and_interior():
    c=empty_collection('30_Interior');cg=empty_collection('20_Entrance');cp=empty_collection('35_Paths')
    exclusions=[]
    for k,route in enumerate(SITE['paths']):
        verts=[];faces=[]
        for i,p in enumerate(route):
            a=Vector(route[max(0,i-1)]);b=Vector(route[min(len(route)-1,i+1)])
            tangent=(b-a).normalized();n=Vector((-tangent.y,tangent.x))
            for sign in (-1,1):
                q=Vector(p)+n*sign*(1.35 if k==0 else .8)
                verts.append((q.x,q.y,ground_z(q.x,q.y)+.045))
            if i:faces.append((2*i-2,2*i,2*i+1,2*i-1))
        o=obj_mesh(f'Path_{k+1:02d}_Mapped',verts,faces,cp,[material('SD_Path_Paving')]);o['accuracy']='Visible route traced from supplied satellite; path width estimated'
    shiva=pixel(SITE['shivrajeshwar_px']);mahadev=pixel(SITE['mahadev_px']);kund=pixel(SITE['kund_px'])
    for src in bpy.data.scenes['Sindhudurg'].objects:
        if src.name.startswith('SD_Temple_Shivrajeshwar_'):
            copy_asset(src.name,src.name.removeprefix('SD_'),c,location=(*shiva,ground_z(*shiva)-.1))
    copy_asset('SD_Temple_Mahadev','Temple_Mahadev',c,location=(*mahadev,ground_z(*mahadev)-.1))
    for name in ('SD_Mahadev_Kund_Stepwell','SD_Mahadev_Kund_Water'):
        copy_asset(name,name.removeprefix('SD_'),c,location=(*kund,ground_z(*kund)-2))
    exclusions.extend([(*shiva,18),(*mahadev,8),(*kund,8)])
    # Well identities and locations under canopy are provisional, rather than invented survey points.
    wells=[('Dudhbav',(960,568)),('Dahibav',(940,575)),('Sakharbav',(957,530))]
    hole_centres=[]
    for name,px in wells:
        pos=pixel(px);gz=ground_z(*pos)
        for suffix in ('','_Water'):
            o=copy_asset('SD_Well_'+name+suffix,'Well_'+name+suffix,c,location=(*pos,gz-2))
            o['accuracy']='Documented freshwater well; exact canopy-obscured position/shaft dimensions provisional'
        exclusions.append((*pos,5));hole_centres.append((*pos,1.64,gz))
    shrines=[('SD_Temple_Jarimari',(1124,467)),('SD_Temple_Bhavani',(979,713)),
             ('SD_Temple_Mahapurush',(962,591))]
    for src,px in shrines:
        pos=pixel(px);o=copy_asset(src,src.removeprefix('SD_'),c,location=(*pos,ground_z(*pos)-.1))
        o['accuracy']='Rough shrine proxy; landmark identification and elevation require site verification'
        exclusions.append((*pos,7))
    # Roof positions are visible on the source raster; sizes/height remain rough.
    buildings=[(1003,514,8,6,35),(1020,526,9,6,35),(1003,539,8,5,15),
      (1008,554,10,6,30),(1012,569,10,6,80),(986,568,8,6,0),
      (974,580,9,6,0),(958,586,10,7,10),(971,599,8,5,0),
      (990,579,8,6,75),(1002,590,8,6,0),(970,628,7,5,0),
      (945,539,7,5,10),(933,550,8,5,0),(955,554,7,5,0),
      (927,568,8,6,20),(1031,515,9,5,30),(1072,486,7,5,35),
      (960,690,10,7,0),(1002,731,8,5,30),(1032,767,8,5,30),
      (1048,783,9,6,30),(979,716,10,7,30),(976,651,6,4,0)]
    for k,(px,py,w,d,deg) in enumerate(buildings):
        pos=pixel((px,py));src=bpy.data.objects[f'SD_House_{k%14+1:02d}']
        size=src.dimensions
        o=copy_asset(src.name,f'Settlement_Roof_{k+1:02d}',c,location=(*pos,ground_z(*pos)-.1),
                     rotation=(0,0,math.radians(deg)),scale=(w/size.x,d/size.y,1))
        o['accuracy']='Visible roof centre from satellite; footprint size, use and height estimated'
        exclusions.append((*pos,math.hypot(w,d)/2+2))
    # Ruins and flag bastion: approximate local inventory, flagged as low-confidence.
    for src,px in [('SD_Palace_Ruins',(906,543)),('SD_Nishan_Buruj',(916,508)),
                   ('SD_Nishan_Flagpole',(916,508)),('SD_Flag_Bhagwa',(916,508))]:
        pos=pixel(px);o=copy_asset(src,src.removeprefix('SD_'),c,location=(*pos,ground_z(*pos)-.1))
        o['accuracy']='Provisional landmark placement; confirm using survey/site photographs'
        exclusions.append((*pos,17 if 'Palace' in src else 8))
    # Reuse the authored hidden entry arch/doors, anchored to the mapped northeast notch.
    gx,gy=SITE['gate_xy'];gz=ground_z(gx,gy)
    for srcname in ('SD_Gate_Arch_Frame','SD_Gate_Passage_Floor','SD_Gate_Door_L','SD_Gate_Door_R'):
        src=bpy.data.objects[srcname]
        pos=src.location.copy();pos.x+=gx-185.08;pos.y+=gy-188.5;pos.z+=gz-1.6
        copy_asset(srcname,srcname.removeprefix('SD_'),cg,location=pos)
    src=bpy.data.objects['SD_CUT_Mahadarwaja']
    pos=src.location.copy();pos.x+=gx-185.08;pos.y+=gy-188.5;pos.z+=gz-1.6
    cutter=copy_asset(src.name,'CUT_Entrance',cg,location=pos)
    cutter.hide_render=True;cutter.display_type='WIRE';cutter.hide_set(True)
    wall=bpy.data.objects[PREFIX+'Wall_Mapped_Rampart']
    for m in list(wall.modifiers):
        if m.type=='BOOLEAN':wall.modifiers.remove(m)
    bo=wall.modifiers.new('Mapped concealed entry passage','BOOLEAN');bo.operation='DIFFERENCE';bo.solver='EXACT';bo.object=cutter
    for srcname in ('SD_Shivaji_Handprint_Dome','SD_Shivaji_Footprint_Dome','SD_Shrine_Hanuman'):
        src=bpy.data.objects[srcname];pos=src.location.copy()
        pos.x+=gx-185.08;pos.y+=gy-188.5
        pos.z+=((TOE+HEIGHT*.9125)-11.1) if 'Dome' in srcname else gz-2
        copy_asset(srcname,srcname.removeprefix('SD_'),cg,location=pos)
    exclusions.append((gx,gy,13))
    # Trace the current jetty, retaining its hooked plan rather than the old straight proxy.
    jet=[pixel(p) for p in SITE['jetty_px']]
    mb=MB()
    for a,b in zip(jet,jet[1:]):
        aa,bb=Vector(a),Vector(b);d=bb-aa;mid=(aa+bb)/2
        mb.box(mid.x,mid.y,.45,d.length+1.2,2.2,.6,0,math.atan2(d.y,d.x))
    mb.make(PREFIX+'Jetty_Mapped',['SD_Stone_Dressed'],cg)
    # Small sandy cove visible on the western indentation.
    beach=[pixel(p) for p in [[954,474],[968,454],[977,438],[977,418],[985,413],[990,427],[985,448],[973,463]]]
    vv=[Vector((x,y,.33)) for x,y in beach]
    obj_mesh('Beach_West_Cove',[tuple(p) for p in vv],tessellate_polygon([vv]),cg,[material('SD_Sand')])
    exclusions.append((*kund,8))
    (ROOT/'data'/'feature_exclusions.json').write_text(json.dumps(exclusions))
    # Cut actual well mouths in the support surfaces, using closed cutter volumes.
    mb=MB()
    for x,y,r,z in hole_centres:
        bot,top=mb.cylinder(x,y,-7,z+3,r,r,32,0)
        mb.face(list(reversed(bot)))
    # Rectangular kund cavity is part of the same managed cutter.
    mb.box(kund[0],kund[1],-7,8,8,ground_z(*kund)+10)
    cuts=mb.make(PREFIX+'CUT_Freshwater_Openings',['SD_Stone_Ruin'],c)
    cuts.hide_render=True;cuts.hide_set(True)
    for name in ('Terrain_Interior','Terrain_Boundary_Fill'):
        terrain_obj=bpy.data.objects[PREFIX+name]
        for m in list(terrain_obj.modifiers):
            if m.type=='BOOLEAN':terrain_obj.modifiers.remove(m)
        m=terrain_obj.modifiers.new('Freshwater well openings','BOOLEAN');m.operation='DIFFERENCE';m.solver='EXACT';m.object=cuts
    return {'mapped_roof_proxies':len(buildings),'freshwater_wells':3,'mapped_paths':len(SITE['paths']),'gate':SITE['gate_xy']}

def prototype_assets():
    c=collection('80_Instance_Assets');c.hide_render=True
    made={}
    for name in ('Coconut','Broadleaf','Scrub','Grass','Rock'):
        old=bpy.data.objects.get(PREFIX+'Prototype_'+name)
        if old:bpy.data.objects.remove(old,do_unlink=True)
    # Coconut: curved tapering trunk, radiating drooping fronds and paired leaflets.
    mb=MB();segments=9;prev=None
    for k in range(13):
        z=k*.95;cx=.014*z*z;rad=.28-.009*z
        ring=[mb.add_v((cx+rad*math.cos(j*2*math.pi/segments),rad*math.sin(j*2*math.pi/segments),z)) for j in range(segments)]
        if prev:
            for j in range(segments):mb.face([prev[j],prev[(j+1)%segments],ring[(j+1)%segments],ring[j]],0)
        else:mb.face(list(reversed(ring)),0)
        prev=ring
    mb.face(prev,0);crown=Vector((.014*11.4**2,0,11.4))
    for f in range(12):
        angle=f*2*math.pi/12+.13*math.sin(f*2)
        direction=Vector((math.cos(angle),math.sin(angle),0));side=Vector((-direction.y,direction.x,0))
        length=4.7+.5*math.sin(f*3)
        prev=None
        for k in range(11):
            t=k/10;p=crown+direction*(length*t)+Vector((0,0,1.1*math.sin(math.pi*t)-1.5*t*t))
            w=.11*(1-t)+.025
            pair=[mb.add_v(p-side*w),mb.add_v(p+side*w)]
            if prev:mb.face([prev[0],pair[0],pair[1],prev[1]],1)
            prev=pair
            if k in (0,10):continue
            for sign in (-1,1):
                tip=p+side*sign*(1.0*math.sin(math.pi*t)**.6)+direction*.25+Vector((0,0,-.18))
                root=p-direction*.12
                mb.face([mb.add_v(root),mb.add_v(tip),mb.add_v(p+direction*.2)],1)
    made['Coconut']=mb.make(PREFIX+'Prototype_Coconut',['SD_Palm_Trunk','SD_Palm_Frond'],c)
    def blob(mb,centre,scale,seed,mi):
        rng=random.Random(seed);bm=bmesh.new();bmesh.ops.create_icosphere(bm,subdivisions=2,radius=1)
        bm.verts.ensure_lookup_table();idx={}
        for v in bm.verts:
            jitter=.78+.35*rng.random();co=Vector((v.co.x*scale[0],v.co.y*scale[1],v.co.z*scale[2]))*jitter+Vector(centre)
            idx[v.index]=mb.add_v(co)
        for face in bm.faces:mb.face([idx[v.index] for v in face.verts],mi)
        bm.free()
    mb=MB();mb.cylinder(0,0,0,4.8,.32,.17,8,0)
    for k,(x,y,z) in enumerate([(0,0,6.5),(2.5,0,5.7),(-2.1,.8,5.5),(.3,2.1,6.0),(0,-2.2,5.8)]):
        blob(mb,(x,y,z),(2.9,2.5,2.5),10+k,1)
    made['Broadleaf']=mb.make(PREFIX+'Prototype_Broadleaf',['SD_Palm_Trunk','SD_Tree_Canopy'],c,smooth=True)
    mb=MB()
    for k,centre in enumerate([(0,0,.7),(.55,.2,.5),(-.4,-.25,.45)]):blob(mb,centre,(.8,.65,.7),30+k,0)
    made['Scrub']=mb.make(PREFIX+'Prototype_Scrub',['SD_Tree_Canopy'],c,smooth=True)
    mb=MB();rng=random.Random(33)
    for k in range(9):
        angle=k*2.399;d=Vector((math.cos(angle),math.sin(angle),0));side=Vector((-d.y,d.x,0))
        start=d*rng.random()*.16;tip=start+d*(.15+rng.random()*.25)+Vector((0,0,.25+rng.random()*.5))
        mb.face([mb.add_v(start-side*.027),mb.add_v(start+side*.027),mb.add_v(tip)],0)
    made['Grass']=mb.make(PREFIX+'Prototype_Grass',['SD_Ground_Soil'],c)
    mb=MB();blob(mb,(0,0,.6),(1.2,.8,.7),91,0)
    # Bury the rocky underside into the sampled shore to avoid hovering.
    made['Rock']=mb.make(PREFIX+'Prototype_Rock',['SD_Rock_Island'],c)
    for kind,o in made.items():
        o.hide_render=True;o.hide_set(True);o['role']='Shared source mesh for unrealized Geometry Nodes instances'
        if kind=='Broadleaf':o['species_confidence']='Broadleaf canopy morphotype; mango/cashew not taxonomically confirmed on island'
        if kind=='Coconut':o['species']='Cocos nucifera; coconut groves documented inside fort'
        if kind=='Scrub':o['species_confidence']='Coastal scrub morphotype; no species inventory supplied'
    return made

def scatter(name,source,proto,attribute,density,spacing,seed,scale):
    c=collection('34_Procedural_Vegetation' if name!='Shore_Rocks' else '41_Procedural_Reef')
    old=bpy.data.objects.get(PREFIX+name)
    if old:bpy.data.objects.remove(old,do_unlink=True)
    o=bpy.data.objects.new(PREFIX+name,source.data);c.objects.link(o)
    g,gi,go=graph('GN_'+name,[('Density per m2','NodeSocketFloat',density),
        ('Minimum spacing m','NodeSocketFloat',spacing),('Seed','NodeSocketInt',seed)])
    mask=add_node(g,'GeometryNodeInputNamedAttribute','Paintable mapped density / clearance mask',-750,-120);mask.data_type='FLOAT';mask.inputs['Name'].default_value=attribute
    dist=add_node(g,'GeometryNodeDistributePointsOnFaces','Seeded Poisson scatter',-430,80);dist.distribute_method='POISSON'
    info=add_node(g,'GeometryNodeObjectInfo','One reusable species source',-430,-230)
    info.inputs['Object'].default_value=proto;info.inputs['As Instance'].default_value=True
    rot=add_node(g,'FunctionNodeRandomValue','Random azimuth, trunks stay vertical',-170,-160);rot.data_type='FLOAT_VECTOR'
    rot.inputs['Min'].default_value=(0,0,0);rot.inputs['Max'].default_value=(0,0,2*math.pi)
    size=add_node(g,'FunctionNodeRandomValue','Natural size variation',-170,-420);size.data_type='FLOAT'
    next(s for s in size.inputs if s.name=='Min' and s.type=='VALUE').default_value=scale[0]
    next(s for s in size.inputs if s.name=='Max' and s.type=='VALUE').default_value=scale[1]
    cv=add_node(g,'ShaderNodeCombineXYZ','Uniform scale preserves species form',60,-420)
    inst=add_node(g,'GeometryNodeInstanceOnPoints','Instances remain unrealized',320,80)
    link=g.links.new
    link(gi.outputs['Geometry'],dist.inputs['Mesh']);link(mask.outputs['Attribute'],dist.inputs['Density Factor'])
    link(gi.outputs['Density per m2'],dist.inputs['Density Max']);link(gi.outputs['Minimum spacing m'],dist.inputs['Distance Min']);link(gi.outputs['Seed'],dist.inputs['Seed'])
    link(gi.outputs['Seed'],rot.inputs['Seed']);link(gi.outputs['Seed'],size.inputs['Seed'])
    link(dist.outputs['Points'],inst.inputs['Points']);link(info.outputs['Geometry'],inst.inputs['Instance']);link(rot.outputs['Value'],inst.inputs['Rotation'])
    for axis in ('X','Y','Z'):link(next(s for s in size.outputs if s.name=='Value' and s.type=='VALUE'),cv.inputs[axis])
    link(cv.outputs[0],inst.inputs['Scale']);link(inst.outputs['Instances'],go.inputs['Geometry']);modifier(o,g)
    o['density_attribute']=attribute;o['seed']=seed;o['instances_realized']=False
    return o

def flora():
    terrain_obj=bpy.data.objects[PREFIX+'Terrain_Interior']
    samples=np.load(ROOT/'data'/'terrain_samples.npz');verts=samples['verts'];x,y=verts[:,:2].T
    free=np.ones(len(x),dtype=float)
    exclusions=json.loads((ROOT/'data'/'feature_exclusions.json').read_text())
    for cx,cy,r in exclusions:free*=np.clip((np.hypot(x-cx,y-cy)-r)/3,0,1)
    for path in SITE['paths']:
        for a,b in zip(path,path[1:]):
            dx=b[0]-a[0];dy=b[1]-a[1];t=np.clip(((x-a[0])*dx+(y-a[1])*dy)/(dx*dx+dy*dy),0,1)
            d=np.hypot(x-a[0]-t*dx,y-a[1]-t*dy)
            free*=np.clip((d-3.2)/3,0,1)
    for key in ('coconut_density','broadleaf_density','scrub_density','grass_density'):
        terrain_obj.data.attributes[key].data.foreach_set('value',(samples[key]*free).astype(np.float32))
    assets=prototype_assets()
    shore=bpy.data.objects[PREFIX+'Rock_Shore_Shelf']
    mask=[1.0 if v.co.z>-.9 else .22 for v in shore.data.vertices]
    attr(shore,'reef_density',mask)
    rock=scatter('Shore_Rocks',shore,assets['Rock'],'reef_density',.028,3,83,(.55,2.3))
    return {'plant_prototypes':[assets[k].name for k in ('Coconut','Broadleaf','Scrub','Grass')],
            'shore_scatter':rock.name,'realize_instances_nodes':0}

def shade_noise(m,colour_a,colour_b,scale,bump=.025):
    nt=m.node_tree;nt.nodes.clear()
    out=nt.nodes.new('ShaderNodeOutputMaterial');out.location=(620,40)
    bs=nt.nodes.new('ShaderNodeBsdfPrincipled');bs.location=(350,40);bs.inputs['Roughness'].default_value=.88
    tc=nt.nodes.new('ShaderNodeTexCoord');tc.location=(-800,0)
    noise=nt.nodes.new('ShaderNodeTexNoise');noise.location=(-590,60)
    noise.inputs['Scale'].default_value=scale;noise.inputs['Detail'].default_value=3
    ramp=nt.nodes.new('ShaderNodeValToRGB');ramp.location=(-300,120)
    ramp.color_ramp.elements[0].color=(*colour_a,1);ramp.color_ramp.elements[1].color=(*colour_b,1)
    bn=nt.nodes.new('ShaderNodeBump');bn.location=(100,-180);bn.inputs['Strength'].default_value=.35;bn.inputs['Distance'].default_value=bump
    nt.links.new(tc.outputs['Object'],noise.inputs['Vector']);nt.links.new(noise.outputs['Fac'],ramp.inputs['Fac'])
    nt.links.new(ramp.outputs['Color'],bs.inputs['Base Color']);nt.links.new(noise.outputs['Fac'],bn.inputs['Height'])
    nt.links.new(bn.outputs['Normal'],bs.inputs['Normal']);nt.links.new(bs.outputs[0],out.inputs['Surface'])
    m.diffuse_color=(*(np.asarray(colour_a)+np.asarray(colour_b))/2,1)
    return nt,bs,tc,noise,ramp

def lookdev():
    for role in ('SD_Stone_Wall','SD_Stone_Wall_Inner','SD_Stone_Bastion','SD_Stone_Parapet','SD_Stone_Ruin'):
        shade_noise(material(role),(.085,.07,.05),(.26,.215,.15),2.2,.035)
    shade_noise(material('SD_Stone_Walkway'),(.23,.205,.16),(.38,.34,.27),3,.02)
    shade_noise(material('SD_Rock_Island'),(.075,.063,.055),(.22,.18,.12),1.3,.06)
    shade_noise(material('SD_Path_Paving'),(.26,.22,.16),(.43,.36,.24),2,.02)
    m=material('SD_Ground_Soil')
    nt,bs,tc,noise,ramp=shade_noise(m,(.17,.11,.048),(.36,.27,.105),.17,.045)
    mask=nt.nodes.new('ShaderNodeAttribute');mask.attribute_name='satellite_green';mask.location=(-500,360)
    mix=nt.nodes.new('ShaderNodeMixRGB');mix.blend_type='MIX';mix.location=(0,240);mix.inputs[2].default_value=(.095,.14,.041,1)
    nt.links.new(mask.outputs['Fac'],mix.inputs[0]);nt.links.new(ramp.outputs['Color'],mix.inputs[1]);nt.links.new(mix.outputs[0],bs.inputs['Base Color'])
    shade_noise(material('SD_Tree_Canopy'),(.055,.12,.022),(.21,.29,.065),1.3,.055)
    shade_noise(material('SD_Palm_Frond'),(.075,.17,.025),(.28,.37,.065),2,.015)
    shade_noise(material('SD_Palm_Trunk'),(.20,.145,.083),(.43,.33,.19),4,.02)
    grass=bpy.data.materials.get(PREFIX+'Dry_Coastal_Grass')
    if grass is None:grass=material('SD_Ground_Soil').copy();grass.name=PREFIX+'Dry_Coastal_Grass'
    shade_noise(grass,(.115,.16,.027),(.42,.34,.13),4,.008)
    bpy.data.objects[PREFIX+'Prototype_Grass'].data.materials[0]=grass
    shade_noise(material('SD_Roof_Tile'),(.32,.095,.045),(.57,.25,.11),5,.025)
    shade_noise(material('SD_Sand'),(.42,.33,.19),(.72,.58,.34),3,.01)
    nt,bs,tc,noise,ramp=shade_noise(material('SD_Water_Sea'),(.015,.085,.12),(.027,.18,.20),.024,.15)
    bs.inputs['Roughness'].default_value=.20;bs.inputs['IOR'].default_value=1.333
    bs.inputs['Metallic'].default_value=0;bs.inputs['Transmission Weight'].default_value=.10
    water=material('SD_Water_Well');bs=next(n for n in water.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    bs.inputs['Roughness'].default_value=.18;bs.inputs['IOR'].default_value=1.333
    return {'material_strategy':'Shared local procedural materials, bump in metre coordinates','generated_assets':0}

def inspection_motion():
    c=collection('90_Presentation');cam=bpy.data.objects[PREFIX+'CAM_Aerial']
    rig=bpy.data.objects.get(PREFIX+'RIG_Inspection_Orbit')
    if rig is None:rig=bpy.data.objects.new(PREFIX+'RIG_Inspection_Orbit',None);c.objects.link(rig)
    rig.location=(45,-20,1);rig.empty_display_type='PLAIN_AXES';rig.empty_display_size=15
    cam.parent=rig;cam.location=(805,-1080,1099)
    for frame,angle in ((1,0),(48,0),(192,.26),(240,.26)):
        rig.rotation_euler.z=angle;rig.keyframe_insert(data_path='rotation_euler',index=2,frame=frame)
    rig['purpose']='Optional slow 15-degree inspection orbit; stationary rest at beginning/end'
    sc().frame_set(1)
    return {'frames':[1,48,192,240],'rotation_rad':.26}

def documentation():
    source=(ROOT/'build_sindhudurg.py').read_text()
    text=bpy.data.texts.get(PREFIX+'build_sindhudurg.py') or bpy.data.texts.new(PREFIX+'build_sindhudurg.py')
    text.clear();text.write(source)
    note=bpy.data.texts.get(PREFIX+'RECONSTRUCTION_NOTES') or bpy.data.texts.new(PREFIX+'RECONSTRUCTION_NOTES')
    note.clear();note.write((ROOT.parent/'docs'/'reconstruction'/'PLAN.md').read_text())
    note.write('\n\nEDITING\nWall dimensions: select SD2_Wall_Mapped_Rampart > Geometry Nodes modifier.\n')
    note.write('Flora controls: SD2_Occupancy_All_Trees / Occupancy_Scrub / Occupancy_Grass modifiers. Density, seed and spacing are editable; spacing is clamped to safe scaled footprints.\n')
    note.write('Density attributes are on SD2_Terrain_Interior (POINT domain floats), sampled from satellite and cleared around features.\n')
    note.write('No Realize Instances nodes. Embrasure cheeks and stairs are also instanced.\n')
    note.write('Species share tree occupancy. Scrub avoids tree crowns; grass avoids trees and scrub. Conservative XY footprint radii guarantee separation across categories.\n')
    note.write('42 raised bastion terraces: 33 clear mapped projections, 9 provisional corner/entry identifications. Anchors carry confidence labels. Decks and wall details follow live rampart height.\n')
    note.write('Original Sindhudurg scene and its 480 objects are retained. New scene: Sindhudurg_1to1.\n')
    note.write('Wall height means 9.144m from assumed toe to continuous parapet crest; .45m embrasure cheeks project above it.\n')
    note.write('Actual traced area: 190112.57m2; perimeter: 2988.78m. No artificial area/perimeter scaling.\n')
    note.write('Building identities/roof height and obscured well positions are provisional; see each object accuracy property.\n')
    note.write('Coconut is documented; broadleaf/scrub/grass are morphotypes. Regional crop lists do not prove island tree species.\n')
    note.write('Rebuild: run SD2_build_sindhudurg.py in Text Editor; external source/data remain in reconstruction folder.\n')
    return {'texts':[text.name,note.name]}

def bastion_decks():
    c=empty_collection('12_Bastion_Platforms')
    candidates=json.loads((ROOT/'data'/'bastion_candidates.json').read_text())
    inner=offset(TRACE,.72,max_miter=2.0);ns=seg_normals(TRACE)
    mb=MB();fractions=[];footprints=[]
    for k,candidate in enumerate(candidates):
        ids=candidate['ids']
        # Large curtain corners must not turn whole parts of the island into a terrace.
        arc=[Vector(TRACE[i]) for i in ids]
        lengths=[0]
        for a,b in zip(arc,arc[1:]):lengths.append(lengths[-1]+(b-a).length)
        if lengths[-1]>38:
            middle=lengths[-1]/2
            ids=[idx for idx,length in zip(ids,lengths) if abs(length-middle)<13]
            if len(ids)<2:ids=candidate['ids'][len(candidate['ids'])//2-1:len(candidate['ids'])//2+2]
        poly=[inner[i] for i in ids]
        # The back chord gives a usable fighting deck behind the mapped outer arc.
        a,b=Vector(poly[0]),Vector(poly[-1])
        depth=5.0 if candidate['confidence'].startswith('provisional') else 4.0
        poly += [tuple(b+ns[ids[-1]]*depth),tuple(a+ns[ids[0]]*depth)]
        # Satellite corner terraces are approximate; keep all platform vertices inside the fort.
        centre=sum((Vector(p) for p in poly),Vector((0,0)))/len(poly)
        for i,p in enumerate(poly):
            q=Vector(p)
            for _ in range(15):
                if point_in_poly(q.x,q.y,TRACE):break
                q=q*.8+centre*.2
            poly[i]=(q.x,q.y)
        if signed_area(poly)<0:poly.reverse()
        assert abs(signed_area(poly))>1,k
        old=len(mb.v);mb.prism(poly,TOE,TOE+HEIGHT*.9125,0,1,0)
        fractions.extend([0]*len(poly)+[.9125]*len(poly))
        footprints.append({'id':k+1,'polygon':poly,'confidence':candidate['confidence']})
    o=mb.make(PREFIX+'Bastion_Fighting_Decks',['SD_Stone_Bastion','SD_Stone_Walkway'],c)
    bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
    attr(o,'height_fraction',fractions)
    g,gi,go=graph('GN_Bastion_Decks_Follow_Rampart')
    info=add_node(g,'GeometryNodeObjectInfo','Read live rampart height',-700,-160);info.inputs['Object'].default_value=bpy.data.objects[PREFIX+'Wall_Mapped_Rampart']
    bounds=add_node(g,'GeometryNodeBoundBox','Continuous parapet crest',-450,-160)
    sep=add_node(g,'ShaderNodeSeparateXYZ','Crest Z',-260,-160)
    delta=add_node(g,'ShaderNodeMath','Height change from nominal crest',-50,-160);delta.operation='SUBTRACT';delta.inputs[1].default_value=TOE+HEIGHT
    frac=add_node(g,'GeometryNodeInputNamedAttribute','Deck fraction of wall height',-450,-370);frac.data_type='FLOAT';frac.inputs['Name'].default_value='height_fraction'
    mult=add_node(g,'ShaderNodeMath','Decks follow height adjustment',130,-160);mult.operation='MULTIPLY'
    cv=add_node(g,'ShaderNodeCombineXYZ','Vertical offset',310,-160)
    pos=add_node(g,'GeometryNodeSetPosition','Keep decks aligned with rampart walkway',500,20)
    link=g.links.new
    link(info.outputs['Geometry'],bounds.inputs['Geometry']);link(bounds.outputs['Max'],sep.inputs[0]);link(sep.outputs['Z'],delta.inputs[0])
    link(delta.outputs[0],mult.inputs[0]);link(frac.outputs['Attribute'],mult.inputs[1]);link(mult.outputs[0],cv.inputs['Z'])
    link(gi.outputs['Geometry'],pos.inputs['Geometry']);link(cv.outputs[0],pos.inputs['Offset']);link(pos.outputs[0],go.inputs['Geometry']);modifier(o,g)
    bo=o.modifiers.new('Entrance remains open through gate terraces','BOOLEAN');bo.operation='DIFFERENCE';bo.solver='EXACT';bo.object=bpy.data.objects[PREFIX+'CUT_Entrance']
    o['bastion_features']=42;o['clear_mapped_arcs']=33;o['provisional_corner_terraces']=9
    o['accuracy']='Outer shapes follow trace; nine corner/entry deck identifications and rear depths provisional'
    (ROOT/'data'/'bastion_footprints.json').write_text(json.dumps(footprints,indent=2))
    # Reviewed marker names permit selecting a bastion without duplicating its geometry.
    for feature in footprints:
        p=np.mean(feature['polygon'],axis=0)
        e=bpy.data.objects.new(PREFIX+f'Bastion_{feature["id"]:02d}_Anchor',None);c.objects.link(e)
        e.location=(*p,TOE+HEIGHT*.9125);e.empty_display_type='CIRCLE';e.empty_display_size=2
        e.hide_render=True;e.hide_set(True);e['confidence']=feature['confidence']
    return {'bastion_platforms':42,'clear_projecting_arcs':33,'provisional_corner_terraces':9}

def planar_radius(o):
    # shortcut: bounds are recomputed on rebuild; rerun after changing prototype meshes.
    return max(math.hypot(v.co.x,v.co.y) for v in o.data.vertices)

def collision_footprints():
    c=empty_collection('81_Scatter_Clearance')
    verts=[];faces=[]
    exclusions=json.loads((ROOT/'data'/'feature_exclusions.json').read_text())
    polys=[]
    for x,y,r in exclusions:
        polys.append([(x+r*math.cos(k*2*math.pi/24),y+r*math.sin(k*2*math.pi/24)) for k in range(24)])
    polys += [f['polygon'] for f in json.loads((ROOT/'data'/'bastion_footprints.json').read_text())]
    for route in SITE['paths']:
        for a,b in zip(route,route[1:]):
            aa,bb=Vector(a),Vector(b);t=(bb-aa).normalized();n=Vector((-t.y,t.x))*1.7
            polys.append([tuple(aa-n),tuple(bb-n),tuple(bb+n),tuple(aa+n)])
    for poly in polys:
        vv=[Vector((x,y,0)) for x,y in poly]
        tris=tessellate_polygon([vv]);base=len(verts);verts.extend(tuple(v) for v in vv)
        faces.extend(tuple(base+i for i in face) for face in tris)
    o=obj_mesh('Clearance_Buildings_Paths_Bastions',verts,faces,c)
    o.hide_render=True;o.hide_set(True)
    # Include the evaluated wall footprint so changing wall thickness stays safe.
    g,gi,go=graph('GN_Clearance_Includes_Live_Wall')
    wall=geometry_info(g,bpy.data.objects[PREFIX+'Wall_Mapped_Rampart'],'Live rampart geometry',-700,-200)
    position=add_node(g,'GeometryNodeInputPosition','Wall positions',-700,-400)
    flat=add_node(g,'ShaderNodeVectorMath','Project wall footprint into XY',-450,-400);flat.operation='MULTIPLY';flat.inputs[1].default_value=(1,1,0)
    sp=add_node(g,'GeometryNodeSetPosition','Live planar wall clearance',-180,-180)
    join=add_node(g,'GeometryNodeJoinGeometry','Protect structures plus the live rampart',200,50)
    link=g.links.new
    link(position.outputs[0],flat.inputs[0]);link(wall.outputs['Geometry'],sp.inputs['Geometry']);link(flat.outputs[0],sp.inputs['Position'])
    link(gi.outputs['Geometry'],join.inputs[0]);link(sp.outputs[0],join.inputs[0]);link(join.outputs[0],go.inputs['Geometry']);modifier(o,g)
    o['purpose']='Planar collision footprints for canopy-aware flora clearance; includes the live wall width'
    return o

def output_socket(node,name,kind='VALUE'):
    return next(s for s in node.outputs if s.name==name and s.type==kind)

def random_float(g,label,minimum,maximum,x,y):
    n=add_node(g,'FunctionNodeRandomValue',label,x,y);n.data_type='FLOAT'
    next(s for s in n.inputs if s.name=='Min' and s.type=='VALUE').default_value=minimum
    next(s for s in n.inputs if s.name=='Max' and s.type=='VALUE').default_value=maximum
    return n

def geometry_info(g,o,label,x,y):
    n=add_node(g,'GeometryNodeObjectInfo',label,x,y);n.inputs['Object'].default_value=o
    n.inputs['As Instance'].default_value=False
    return n

def points_clear(g,geometry,own_radius,target,other_radius,label,x):
    info=geometry_info(g,target,label,x,-400)
    prox=add_node(g,'GeometryNodeProximity','Distance to occupied footprint',x+210,-180)
    prox.target_element='FACES' if other_radius is None else 'POINTS'
    position=add_node(g,'GeometryNodeInputPosition','Point positions',x,-80)
    flat=add_node(g,'ShaderNodeVectorMath','Use horizontal clearance',x+20,90);flat.operation='MULTIPLY';flat.inputs[1].default_value=(1,1,0)
    # Point clouds retain surface Z. Match their plane for proximity, without realizing instances.
    if other_radius is not None:
        flatten=add_node(g,'GeometryNodeSetPosition','Flatten occupied centres for XY distances',x,-570)
        targetpos=add_node(g,'GeometryNodeInputPosition','Occupied centre positions',x-190,-570)
        tv=add_node(g,'ShaderNodeVectorMath','XY occupied centres',x-190,-730);tv.operation='MULTIPLY';tv.inputs[1].default_value=(1,1,0)
        g.links.new(targetpos.outputs[0],tv.inputs[0]);g.links.new(info.outputs['Geometry'],flatten.inputs['Geometry'])
        g.links.new(tv.outputs[0],flatten.inputs['Position']);target_geo=flatten.outputs[0]
    else:target_geo=info.outputs['Geometry']
    threshold=add_node(g,'ShaderNodeMath','Radius plus protected category margin',x+240,-410);threshold.operation='ADD'
    threshold.inputs[1].default_value=(.35 if other_radius is None else other_radius+.35)
    compare=add_node(g,'ShaderNodeMath','Reject overlapping centres',x+470,-180);compare.operation='LESS_THAN'
    delete=add_node(g,'GeometryNodeDeleteGeometry','Keep only collision-free points',x+660,60);delete.domain='POINT'
    link=g.links.new
    link(position.outputs[0],flat.inputs[0]);link(flat.outputs[0],next(s for s in prox.inputs if s.type=='VECTOR'))
    link(target_geo,prox.inputs['Geometry']);link(own_radius,threshold.inputs[0])
    link(prox.outputs['Distance'],compare.inputs[0]);link(threshold.outputs[0],compare.inputs[1])
    link(geometry,delete.inputs['Geometry']);link(compare.outputs[0],delete.inputs['Selection'])
    return delete.outputs[0]

def occupancy_points(name,source,mask,density,max_radius,seed,scale,radii,obstacles,tree=False):
    c=collection('82_Shared_Plant_Occupancy')
    old=bpy.data.objects.get(PREFIX+name)
    if old:bpy.data.objects.remove(old,do_unlink=True)
    o=bpy.data.objects.new(PREFIX+name,source.data);c.objects.link(o);o.hide_render=True;o.hide_set(True)
    safe_spacing=2*max_radius+.5
    g,gi,go=graph('GN_'+name,[('Density per m2','NodeSocketFloat',density),
                             ('Spacing m','NodeSocketFloat',safe_spacing),('Seed','NodeSocketInt',seed)])
    md=add_node(g,'GeometryNodeInputNamedAttribute','Mapped planting density',-800,-200);md.data_type='FLOAT';md.inputs['Name'].default_value=mask
    spacing=add_node(g,'ShaderNodeMath','Clamp spacing to largest scaled footprint',-620,200);spacing.operation='MAXIMUM';spacing.inputs[1].default_value=safe_spacing
    dist=add_node(g,'GeometryNodeDistributePointsOnFaces','Shared Poisson occupancy, all species',-400,100);dist.distribute_method='POISSON'
    size=random_float(g,'Bounded size variation',scale[0],scale[1],-400,-350)
    store=add_node(g,'GeometryNodeStoreNamedAttribute','Store scale on the shared points',-130,80);store.data_type='FLOAT';store.domain='POINT';store.inputs['Name'].default_value='plant_scale'
    link=g.links.new
    link(gi.outputs['Geometry'],dist.inputs['Mesh']);link(md.outputs['Attribute'],dist.inputs['Density Factor'])
    link(gi.outputs['Density per m2'],dist.inputs['Density Max']);link(gi.outputs['Spacing m'],spacing.inputs[0]);link(spacing.outputs[0],dist.inputs['Distance Min']);link(gi.outputs['Seed'],dist.inputs['Seed'])
    link(gi.outputs['Seed'],size.inputs['Seed']);link(dist.outputs['Points'],store.inputs['Geometry']);link(output_socket(size,'Value'),store.inputs['Value'])
    current=store.outputs[0]
    radius=add_node(g,'ShaderNodeMath','Actual scaled planar footprint radius',140,-330);radius.operation='MULTIPLY'
    link(output_socket(size,'Value'),radius.inputs[0])
    if tree:
        prob=add_node(g,'GeometryNodeInputNamedAttribute','Mapped coconut fraction',-400,-650);prob.data_type='FLOAT';prob.inputs['Name'].default_value='coconut_fraction'
        choice=random_float(g,'One species assignment per occupied point',0,1,-400,-850);link(gi.outputs['Seed'],choice.inputs['Seed'])
        compare=add_node(g,'ShaderNodeMath','Coconut if random value below mapped fraction',-130,-650);compare.operation='LESS_THAN'
        link(output_socket(choice,'Value'),compare.inputs[0]);link(prob.outputs['Attribute'],compare.inputs[1])
        species=add_node(g,'GeometryNodeStoreNamedAttribute','Exactly one tree species per point',140,80);species.data_type='FLOAT';species.domain='POINT';species.inputs['Name'].default_value='coconut_selection'
        link(current,species.inputs['Geometry']);link(compare.outputs[0],species.inputs['Value']);current=species.outputs[0]
        rad=add_node(g,'ShaderNodeMath','Species-specific footprint',140,-620);rad.operation='MULTIPLY_ADD';rad.inputs[1].default_value=radii[0]-radii[1];rad.inputs[2].default_value=radii[1]
        link(compare.outputs[0],rad.inputs[0]);link(rad.outputs[0],radius.inputs[1])
    else:radius.inputs[1].default_value=radii[0]
    rs=add_node(g,'GeometryNodeStoreNamedAttribute','Store collision radius in metres',420,80);rs.data_type='FLOAT';rs.domain='POINT';rs.inputs['Name'].default_value='plant_radius_m'
    link(current,rs.inputs['Geometry']);link(radius.outputs[0],rs.inputs['Value']);current=rs.outputs[0]
    own=add_node(g,'GeometryNodeInputNamedAttribute','Occupied plant radius',420,-350);own.data_type='FLOAT';own.inputs['Name'].default_value='plant_radius_m'
    for k,(target,r) in enumerate(obstacles):
        current=points_clear(g,current,own.outputs['Attribute'],target,r,'Protect '+target.name,900+k*1100)
    go.location=(1100+len(obstacles)*1100,100);link(current,go.inputs['Geometry']);modifier(o,g)
    o['safe_minimum_spacing_m']=safe_spacing;o['maximum_footprint_radius_m']=max_radius
    o['purpose']='Shared occupancy points, before instances; downstream categories reserve this footprint'
    return o

def instances_from_occupancy(name,points,prototype,seed,species=None):
    c=collection('34_Procedural_Vegetation')
    old=bpy.data.objects.get(PREFIX+name)
    if old:bpy.data.objects.remove(old,do_unlink=True)
    o=obj_mesh(name,[],[],c)
    g,gi,go=graph('GN_'+name)
    info=geometry_info(g,points,'Read shared collision-free occupancy',-700,100)
    proto=geometry_info(g,prototype,'Shared species geometry',-700,-180);proto.inputs['As Instance'].default_value=True
    size=add_node(g,'GeometryNodeInputNamedAttribute','Scale chosen at occupancy stage',-480,-360);size.data_type='FLOAT';size.inputs['Name'].default_value='plant_scale'
    cv=add_node(g,'ShaderNodeCombineXYZ','Uniform species scale',-230,-360)
    for axis in 'XYZ':g.links.new(size.outputs['Attribute'],cv.inputs[axis])
    rot=add_node(g,'FunctionNodeRandomValue','Random azimuth',-480,-600);rot.data_type='FLOAT_VECTOR';rot.inputs['Min'].default_value=(0,0,0);rot.inputs['Max'].default_value=(0,0,2*math.pi);rot.inputs['Seed'].default_value=seed
    inst=add_node(g,'GeometryNodeInstanceOnPoints','Unrealized instances on reserved footprints',200,100)
    link=g.links.new
    link(info.outputs['Geometry'],inst.inputs['Points']);link(proto.outputs['Geometry'],inst.inputs['Instance']);link(cv.outputs[0],inst.inputs['Scale']);link(rot.outputs['Value'],inst.inputs['Rotation'])
    if species is not None:
        sel=add_node(g,'GeometryNodeInputNamedAttribute','Exclusive species category',-480,330);sel.data_type='FLOAT';sel.inputs['Name'].default_value='coconut_selection'
        test=add_node(g,'ShaderNodeMath','Select only this species',-200,330);test.operation='GREATER_THAN' if species else 'LESS_THAN';test.inputs[1].default_value=.5
        link(sel.outputs['Attribute'],test.inputs[0]);link(test.outputs[0],inst.inputs['Selection'])
    link(inst.outputs[0],go.inputs['Geometry']);modifier(o,g)
    o['occupancy_source']=points.name;o['instances_realized']=False
    return o

def collision_safe_flora():
    terrain_obj=bpy.data.objects[PREFIX+'Terrain_Interior']
    def read(name):
        a=terrain_obj.data.attributes[name];v=np.zeros(len(a.data),np.float32);a.data.foreach_get('value',v);return v
    coco,bro=read('coconut_density'),read('broadleaf_density')
    attr(terrain_obj,'shared_tree_density',np.clip((coco+bro)*3,0,1))
    ratio=np.divide(coco*.012,coco*.012+bro*.025,out=np.full_like(coco,.5),where=(coco+bro)>1e-9)
    attr(terrain_obj,'coconut_fraction',ratio)
    assets={kind:bpy.data.objects[PREFIX+'Prototype_'+kind] for kind in ('Coconut','Broadleaf','Scrub','Grass')}
    radii={kind:planar_radius(o) for kind,o in assets.items()}
    tree_max=max(radii['Coconut'],radii['Broadleaf'])*1.35
    scrub_max=radii['Scrub']*1.7;grass_max=radii['Grass']*1.5
    buildings=collision_footprints()
    # The order establishes one-way dependencies and prevents inter-species overlap.
    trees=occupancy_points('Occupancy_All_Trees',terrain_obj,'shared_tree_density',.025,tree_max,11,(.70,1.35),
                           (radii['Coconut'],radii['Broadleaf']),[(buildings,None)],tree=True)
    shrubs=occupancy_points('Occupancy_Scrub',terrain_obj,'scrub_density',.035,scrub_max,43,(.6,1.7),
                            (radii['Scrub'],),[(buildings,None),(trees,tree_max)])
    grass=occupancy_points('Occupancy_Grass',terrain_obj,'grass_density',.08,grass_max,67,(.7,1.5),
                           (radii['Grass'],),[(buildings,None),(trees,tree_max),(shrubs,scrub_max)])
    instances_from_occupancy('Scatter_Coconut',trees,assets['Coconut'],11,True)
    instances_from_occupancy('Scatter_Broadleaf',trees,assets['Broadleaf'],29,False)
    instances_from_occupancy('Scatter_Scrub',shrubs,assets['Scrub'],43)
    instances_from_occupancy('Scatter_Grass',grass,assets['Grass'],67)
    return {'shared_tree_spacing_m':2*tree_max+.5,'scrub_spacing_m':2*scrub_max+.5,
            'grass_spacing_m':2*grass_max+.5,'unrealized':True,'cross_category_proximity':True,
            'maximum_radii':{'Trees':tree_max,'Scrub':scrub_max,'Grass':grass_max}}

def rebuild():
    result={'blockout':blockout(),'wall_details':wall_details(),'interior':paths_and_interior(),
            'flora':flora(),'materials':lookdev(),'bastions':bastion_decks(),
            'collision_safe_flora':collision_safe_flora(),'motion':inspection_motion(),'documentation':documentation()}
    return result

if __name__=='__main__':
    result=rebuild()
