# sd_finish.py - cameras, sun, sky, viewport framing, scene stats.


def look_at(obj, target):
    d = Vector(target) - obj.location
    obj.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()


def build_finish():
    sc = scene()
    c = sub("SD_90_Camera_Light"); clear(c)
    guides = bpy.data.collections.get("SD_00_Guides")
    if guides is not None:
        guides.hide_render = True
    cams = {
        "SD_CAM_Aerial_SE": ((560.0, -620.0, 330.0), (0.0, -10.0, 0.0), 50),
        "SD_CAM_Gate_Approach": ((268.0, 150.0, 6.0), (195.0, 195.0, 7.0), 28),
        "SD_CAM_Temple": ((60.0, -12.0, 9.0), (10.0, 20.0, 5.0), 30),
        "SD_CAM_Top_Ortho": ((0.0, 0.0, 900.0), (0.0, 0.0, 0.0), None),
    }
    for nm, (loc, tgt, lens) in cams.items():
        cd = bpy.data.cameras.new(nm)
        o = bpy.data.objects.new(nm, cd); c.objects.link(o)
        o.location = loc; look_at(o, tgt)
        cd.clip_end = 8000.0
        if lens is None:
            cd.type = 'ORTHO'; cd.ortho_scale = 700.0
        else:
            cd.lens = lens
    sc.camera = bpy.data.objects["SD_CAM_Aerial_SE"]
    ld = bpy.data.lights.new("SD_LGT_Sun", 'SUN')
    ld.energy = 4.0; ld.angle = math.radians(1.5); ld.color = (1.0, 0.95, 0.88)
    lo = bpy.data.objects.new("SD_LGT_Sun", ld); c.objects.link(lo)
    lo.rotation_euler = (math.radians(48), 0.0, math.radians(-35))
    w = bpy.data.worlds.get("SD_World") or bpy.data.worlds.new("SD_World")
    sc.world = w
    try:
        w.use_nodes = True
    except Exception:
        pass
    bg = next((nd for nd in w.node_tree.nodes if nd.type == 'BACKGROUND'), None)
    if bg is not None:
        bg.inputs["Color"].default_value = (0.55, 0.70, 0.88, 1.0)
        bg.inputs["Strength"].default_value = 0.8
    try:
        sc.render.engine = 'BLENDER_EEVEE'
    except Exception:
        pass
    sc.render.resolution_x, sc.render.resolution_y = 1920, 1080
    # frame the fort in every 3D viewport of the open window (UI sessions only)
    try:
        for area in bpy.context.window.screen.areas:
            if area.type == 'VIEW_3D':
                sp = area.spaces.active
                sp.clip_end = 10000.0
                r3 = sp.region_3d
                r3.view_location = (0.0, 0.0, 0.0)
                r3.view_distance = 900.0
                from mathutils import Euler
                r3.view_rotation = Euler((math.radians(55), 0, math.radians(35))).to_quaternion()
                sp.shading.type = 'SOLID'; sp.shading.color_type = 'MATERIAL'
    except Exception:
        pass
    tris = 0; meshes = set(); objs = 0
    for o in sc.objects:
        objs += 1
        if o.type == 'MESH':
            tris += sum(len(p.vertices) - 2 for p in o.data.polygons)
            meshes.add(o.data.name)
    return {"objects": objs, "unique_meshes": len(meshes), "scene_tris": tris,
            "materials": sorted(m.name for m in bpy.data.materials if m.name.startswith("SD_"))}
