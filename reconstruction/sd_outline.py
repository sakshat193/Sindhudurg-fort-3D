# sd_outline.py - creates the editable wall-trace guide (only if it does not exist yet).
# Edit SD_GUIDE_Outline in Edit Mode (or retrace it over a satellite image) and re-run the
# build; move the SD_GUIDE_Gate* / SD_GUIDE_Beach empties to re-site the gate and postern.

DEFAULT_PTS = [
    (182.3, -204.7), (194.4, -153.1), (178.9, -110.9), (203.0, -70.5), (206.4, -17.2),
    (182.3, 24.4), (209.8, 63.6), (204.7, 110.1), (173.7, 137.4), (203.0, 168.6),
    (184.0, 172.0), (185.8, 199.5), (208.1, 211.6), (171.2, 219.1), (160.0, 258.0),
    (116.9, 243.3), (101.5, 283.8), (51.6, 263.3), (25.8, 299.3), (-9.2, 265.0),
    (-49.9, 289.0), (-76.1, 241.4), (-118.7, 263.2), (-131.5, 219.2), (-177.2, 204.7),
    (-156.7, 161.5), (-194.4, 129.0), (-190.9, 82.6), (-158.2, 53.1), (-192.6, 20.6),
    (-203.0, -25.8), (-172.0, -63.8), (-204.7, -101.5), (-194.4, -146.2), (-156.7, -166.8),
    (-182.3, -203.0), (-140.0, -219.3), (-129.0, -258.0), (-86.3, -239.7), (-58.5, -285.5),
    (-23.7, -246.0), (17.2, -289.0), (52.3, -252.9), (89.4, -280.4), (115.9, -240.3),
    (151.4, -242.5), (156.7, -209.6),
]
DEFAULT_GATE = (9, 10, 11, 12)   # salient A, notch corner, door-wall end, salient B
DEFAULT_BEACH = 40               # Ranichi Vela bay vertex


def build_outline(force=False):
    g = sub("SD_00_Guides")
    o = bpy.data.objects.get("SD_GUIDE_Outline")
    if o is not None and not force:
        return {"outline": "kept existing (user-editable)"}
    if o is not None:
        bpy.data.objects.remove(o, do_unlink=True)
    me = bpy.data.meshes.new("SD_GUIDE_Outline")
    n = len(DEFAULT_PTS)
    me.from_pydata([(x, y, P["WALL_TOP"]) for x, y in DEFAULT_PTS], [(i, (i + 1) % n) for i in range(n)], [])
    o = bpy.data.objects.new("SD_GUIDE_Outline", me)
    g.objects.link(o)
    o["note"] = ("Outer top edge of the curtain wall, CCW, metres. Approximation scaled to 19.0 ha; "
                 "retrace over imagery for an exact footprint, then re-run the build.")
    o["bastion_target"] = 42
    o.show_in_front = True
    for k, i in enumerate(DEFAULT_GATE):
        nm = "SD_GUIDE_Gate" + "ABCD"[k]
        e = bpy.data.objects.get(nm) or bpy.data.objects.new(nm, None)
        e.location = (*DEFAULT_PTS[i], P["WALL_TOP"] + 3)
        e.empty_display_type = 'SPHERE'; e.empty_display_size = 3
        if e.name not in g.objects:
            g.objects.link(e)
    e = bpy.data.objects.get("SD_GUIDE_Beach") or bpy.data.objects.new("SD_GUIDE_Beach", None)
    e.location = (*DEFAULT_PTS[DEFAULT_BEACH], P["WALL_TOP"] + 3)
    e.empty_display_type = 'CONE'; e.empty_display_size = 4
    if e.name not in g.objects:
        g.objects.link(e)
    return {"outline": "created", "verts": n}
