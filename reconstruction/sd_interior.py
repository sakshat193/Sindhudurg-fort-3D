# sd_interior.py - ground, paths, temples, wells, palace ruin, Nishan Buruj + flag,
# houses, cannons, vegetation.  Positions inside the fort are representative (no
# measured site plan is published); the inventory follows the sources in the README.
from mathutils.geometry import tessellate_polygon

SITE = dict(
    shivrajeshwar=(10.0, 20.0),     # "at the centre of the fort" (durgbharari, Anantam/Vishwakosh)
    mahadev=(-40.0, 20.0),          # behind (west of) Shivrajeshwar, with a square stepwell
    kund=(-40.0, 4.0),
    dudhbav=(-22.0, -18.0), dahibav=(-62.0, -14.0), sakharbav=(-58.0, 44.0),
    jarimari=(148.0, 160.0),        # small shrine on the paved path after the gate (1881 inscription)
    bhavani=(62.0, -64.0),
    mahapurush=(-22.0, -112.0),
    palace=(-95.0, 30.0),           # palace ruins
    nishan=(-142.0, 34.0),          # Nishankathi / Darya buruj, west of the palace ruins
    school=(105.0, 96.0),
)
WELL_R = 1.6


def circle(cx, cy, r, seg=12, ccw=True):
    pts = [(cx + r * math.cos(2 * math.pi * k / seg), cy + r * math.sin(2 * math.pi * k / seg)) for k in range(seg)]
    return pts if ccw else pts[::-1]


def rect(cx, cy, sx, sy):
    return [(cx - sx / 2, cy - sy / 2), (cx + sx / 2, cy - sy / 2), (cx + sx / 2, cy + sy / 2), (cx - sx / 2, cy + sy / 2)]


def ground(inner, holes, c):
    GZ = P["GROUND_Z"]
    loops = [inner] + holes
    verts = [Vector((x, y, GZ)) for lp in loops for x, y in lp]
    tris = tessellate_polygon([[Vector((x, y, GZ)) for x, y in lp] for lp in loops])
    faces = [(a, b, cc) for a, b, cc in tris]
    # make every triangle face up
    fixed = []
    for a, b, cc in faces:
        n = (verts[b] - verts[a]).cross(verts[cc] - verts[a])
        fixed.append((a, b, cc) if n.z >= 0 else (a, cc, b))
    return build("SD_Ground_Interior", verts, fixed, ["SD_Ground_Soil"], None, c)


def path_strip(name, pts, w, c, z=None):
    z = (P["GROUND_Z"] + 0.03) if z is None else z
    mb = MB(); left, right = [], []
    for i, p in enumerate(pts):
        p = Vector(p)
        a = Vector(pts[max(i - 1, 0)]); b = Vector(pts[min(i + 1, len(pts) - 1)])
        t = (b - a).normalized(); nn = Vector((-t.y, t.x))
        left.append(mb.add_v((*(p + nn * w / 2), z))); right.append(mb.add_v((*(p - nn * w / 2), z)))
    for i in range(len(pts) - 1):
        mb.face([right[i], right[i + 1], left[i + 1], left[i]])
    return mb.make(name, ["SD_Path_Paving"], c)


def well(name, cx, cy, c):
    GZ = P["GROUND_Z"]
    mb = MB(); seg = 12
    ro, ri = WELL_R + 0.45, WELL_R
    bo, to = mb.cylinder(0, 0, GZ - 0.05, GZ + 0.8, ro, ro, seg, 0, top=False)
    bi, ti = [], []
    for k in range(seg):
        a = 2 * math.pi * k / seg
        ti.append(mb.add_v((ri * math.cos(a), ri * math.sin(a), GZ + 0.8)))
        bi.append(mb.add_v((ri * math.cos(a), ri * math.sin(a), GZ - 6.0)))
    for k in range(seg):
        j = (k + 1) % seg
        mb.face([to[k], to[j], ti[j], ti[k]], 1)       # rim cap
        mb.face([ti[k], ti[j], bi[j], bi[k]], 0)       # shaft (faces inward)
    mb.face(list(reversed(bi)), 0)
    o = mb.make(name, ["SD_Stone_Ruin", "SD_Stone_Dressed"], c, loc=(cx, cy, 0))
    w = MB(); w.prism(circle(0, 0, ri, seg), GZ - 3.2, GZ - 3.19, 0, 0)
    w.make(name + "_Water", ["SD_Water_Well"], c, loc=(cx, cy, 0))
    return o


def tiled_shrine(name, cx, cy, sx, sy, h, roof_rise, c, rot=0.0, dome=False, wall_mat="SD_Plaster_Lime"):
    GZ = P["GROUND_Z"]
    mb = MB()
    mb.box(0, 0, 0, sx + 1.0, sy + 1.0, 0.45, 0)                 # plinth
    mb.box(0, 0, 0.45, sx, sy, h, 1)                             # walls
    mb.box(0, -sy / 2 - 0.03, 0.45, min(1.2, sx * 0.4), 0.08, min(2.2, h - 0.3), 3)  # door
    mb.hip_roof(0, 0, 0.45 + h, sx, sy, roof_rise, 2, 0.0, 0.5)
    if dome:
        mb.cylinder(0, 0, 0.45 + h + roof_rise * 0.6, 0.45 + h + roof_rise + 0.4, 0.9, 0.9, 8, 1)
        mb.dome(0, 0, 0.45 + h + roof_rise + 0.4, 0.9, 1.0, 8, 3, 1)
        mb.cylinder(0, 0, 0.45 + h + roof_rise + 1.35, 0.45 + h + roof_rise + 1.8, 0.12, 0.03, 6, 4)
    return mb.make(name, ["SD_Stone_Dressed", wall_mat, "SD_Roof_Tile", "SD_Wood_Old", "SD_Brass"], c,
                   loc=(cx, cy, GZ), rot=(0, 0, rot))


def temple_shivrajeshwar(c):
    """Original shrine 13 x 7 m (Rajaram, 1689-1700) + front hall added by Shahu of Kolhapur (1907).
    Faces east. Elevation/roof forms are representative of Konkan temples (tile roofs, timber hall)."""
    GZ = P["GROUND_Z"]
    cx, cy = SITE["shivrajeshwar"]
    cc = coll("SD_31_Shivrajeshwar_Temple", c)
    L = lambda: (cx, cy, GZ)
    mb = MB()
    mb.box(-0.5, 0, 0, 26.6, 10.0, 0.6, 0)
    for k in range(3):
        mb.box(13.3 + 0.35 * k + 0.175, 0, 0, 0.35, 4.0, 0.6 - 0.2 * (k + 1) + 0.2, 0)
    mb.make("SD_Temple_Shivrajeshwar_Plinth", ["SD_Stone_Dressed"], cc, loc=L())
    mb = MB()
    mb.box(-6.5, 0, 0.6, 13.0, 7.0, 4.4, 0)
    mb.box(0.03, 0, 0.6, 0.08, 1.5, 2.6, 1)
    mb.make("SD_Temple_Shivrajeshwar_Sanctum", ["SD_Plaster_Lime", "SD_Wood_Old"], cc, loc=L())
    mb = MB(); mb.hip_roof(-6.5, 0, 5.0, 13.0, 7.0, 2.4, 0, 0.0, 0.7)
    mb.make("SD_Temple_Shivrajeshwar_Sanctum_Roof", ["SD_Roof_Tile"], cc, loc=L())
    mb = MB()
    mb.cylinder(-10.0, 0, 6.2, 8.4, 1.7, 1.7, 8, 0, rot=math.pi / 8)
    mb.dome(-10.0, 0, 8.4, 1.75, 1.8, 8, 3, 0)
    mb.cylinder(-10.0, 0, 10.15, 10.9, 0.22, 0.05, 8, 1)
    mb.make("SD_Temple_Shivrajeshwar_Shikhara", ["SD_Plaster_Lime", "SD_Brass"], cc, loc=L())
    mb = MB()
    xs = [0.6, 4.2, 7.8, 11.4]
    for x in xs:
        for y in (-4.1, 4.1):
            mb.box(x, y, 0.6, 0.35, 0.35, 3.4, 0)
    for y in (-1.5, 1.5):
        mb.box(11.4, y, 0.6, 0.35, 0.35, 3.4, 0)
    mb.box(6.0, 0, 3.85, 12.0, 8.6, 0.15, 0)        # timber ceiling beam frame
    mb.make("SD_Temple_Shivrajeshwar_Hall_Timber", ["SD_Wood_Old"], cc, loc=L())
    mb = MB()
    for y in (-4.1, 4.1):
        mb.box(6.0, y, 0.6, 10.8, 0.3, 0.8, 0)
    mb.make("SD_Temple_Shivrajeshwar_Hall_Parapet", ["SD_Plaster_Lime"], cc, loc=L())
    mb = MB(); mb.hip_roof(6.0, 0, 4.0, 12.0, 9.0, 2.0, 0, 0.0, 0.8)
    mb.make("SD_Temple_Shivrajeshwar_Hall_Roof", ["SD_Roof_Tile"], cc, loc=L())


def temple_mahadev(c):
    GZ = P["GROUND_Z"]
    cx, cy = SITE["mahadev"]
    mb = MB()
    mb.box(0, 0, 0, 7.5, 7.5, 0.5, 0)
    mb.box(0, 0, 0.5, 5.0, 5.0, 3.2, 0)
    mb.box(2.53, 0, 0.5, 0.08, 1.1, 2.0, 2)
    for k, s in enumerate((5.2, 4.2, 3.2, 2.2, 1.2)):          # stepped stone shikhara
        mb.box(0, 0, 3.7 + 0.75 * k, s, s, 0.75, 0)
    mb.cylinder(0, 0, 7.45, 8.0, 0.18, 0.04, 6, 1)
    # Nandi facing the sanctum
    mb.box(5.2, 0, 0.5, 0.9, 0.9, 0.3, 0)
    mb.box(5.2, 0, 0.8, 1.3, 0.6, 0.55, 0)
    mb.box(4.55, 0, 1.15, 0.35, 0.4, 0.45, 0)
    mb.make("SD_Temple_Mahadev", ["SD_Stone_Dressed", "SD_Brass", "SD_Wood_Old"], c, loc=(cx, cy, GZ))
    # square stepwell (kund): rim, walls, west flight of steps, water
    kx, ky = SITE["kund"]; S = 8.0
    mb = MB()
    outer = rect(0, 0, S + 1.2, S + 1.2); inner = rect(0, 0, S, S)
    ob = [mb.add_v((x, y, GZ - 0.05)) for x, y in outer]; ot = [mb.add_v((x, y, GZ + 0.6)) for x, y in outer]
    it = [mb.add_v((x, y, GZ + 0.6)) for x, y in inner]; ib = [mb.add_v((x, y, GZ - 4.5)) for x, y in inner]
    for i in range(4):
        j = (i + 1) % 4
        mb.face([ob[i], ob[j], ot[j], ot[i]], 0); mb.face([ot[i], ot[j], it[j], it[i]], 1)
        mb.face([it[i], it[j], ib[j], ib[i]], 0)
    mb.face(list(reversed(ib)), 0)
    for k in range(8):
        mb.box(-S / 2 + 0.6 + 0.6 * k, -S / 2 + 1.0, GZ - 4.5, 0.6, 2.0, 4.5 - 0.5 * (k + 1), 1)
    mb.make("SD_Mahadev_Kund_Stepwell", ["SD_Stone_Ruin", "SD_Stone_Dressed"], c, loc=(kx, ky, 0))
    w = MB(); w.prism(rect(0, 0, S, S), GZ - 3.0, GZ - 2.99, 0, 0)
    w.make("SD_Mahadev_Kund_Water", ["SD_Water_Well"], c, loc=(kx, ky, 0))


def palace_ruin(c):
    GZ = P["GROUND_Z"]
    cx, cy = SITE["palace"]
    mb = MB()
    mb.box(0, 0, 0, 25.0, 17.0, 0.4, 0)
    walls = [(-12, 0, 0.8, 16, 2.2), (12, -4, 0.8, 8, 1.6), (12, 6, 0.8, 4, 0.9), (-4, -8, 16, 0.8, 1.8),
             (8, -8, 4, 0.8, 0.7), (0, 8, 24, 0.8, 1.2), (-3, 0, 0.8, 10, 1.0), (5, 2, 7, 0.8, 0.6)]
    for x, y, sx, sy, h in walls:
        mb.box(x, y, 0.4, sx, sy, h, 1)
    mb.make("SD_Palace_Ruins", ["SD_Stone_Ruin", "SD_Laterite"], c, loc=(cx, cy, GZ))


def nishan_buruj(c, bastion_mesh_fn):
    """Free-standing flag bastion (Nishankathi / Jhenda / Darya buruj) with the Bhagwa flag."""
    GZ = P["GROUND_Z"]
    cx, cy = SITE["nishan"]
    me = bastion_mesh_fn("SD_Nishan_Buruj", 5.0, 0.0, 12.0, 0.5)
    o = bpy.data.objects.new("SD_Nishan_Buruj", me); o.location = (cx, cy, GZ); c.objects.link(o)
    mb = MB(); mb.cylinder(0, 0, 12.0, 21.0, 0.13, 0.08, 8, 0)
    mb.make("SD_Nishan_Flagpole", ["SD_Wood_Old"], c, loc=(cx, cy, GZ))
    # swallow-tailed saffron Bhagwa Jhenda in the XZ plane, flying east
    pts = [(0.0, 0.0), (3.6, 0.7), (2.5, 1.2), (3.6, 1.7), (0.0, 2.4)]
    mb = MB()
    vs = [mb.add_v((x + 0.15, 0.0, 18.4 + z)) for x, z in pts]
    mb.face(vs, 0); mb.face(list(reversed(vs)), 0)
    mb.make("SD_Flag_Bhagwa", ["SD_Flag_Saffron"], c, loc=(cx, cy, GZ))


HOUSE_VARIANTS = {
    "A": (9.0, 6.0, 3.0, "SD_Laterite"),
    "B": (11.0, 7.0, 3.2, "SD_Plaster_Ochre"),
    "C": (7.0, 5.0, 2.8, "SD_Laterite"),
}


def house_mesh(key):
    sx, sy, h, wm = HOUSE_VARIANTS[key]
    nm = f"SD_House_mesh_{key}"
    old = bpy.data.meshes.get(nm)
    if old is not None and old.users == 0:
        bpy.data.meshes.remove(old)
    mb = MB()
    mb.box(0, 0, 0, sx + 0.6, sy + 0.6, 0.35, 3)                # plinth
    mb.box(0, 0, 0.35, sx, sy, h, 0)                            # walls
    mb.box(0, -sy / 2 - 0.03, 0.35, 1.1, 0.08, 2.1, 2)          # door
    for x in (-sx / 3, sx / 3):
        mb.box(x, -sy / 2 - 0.03, 1.3, 0.9, 0.08, 1.0, 2)       # shuttered windows
    mb.hip_roof(0, 0, 0.35 + h, sx, sy, 2.2, 1, 0.0, 0.8)
    o = mb.make("tmp_house", [wm, "SD_Roof_Tile", "SD_Wood_Old", "SD_Stone_Ruin"])
    me = o.data; me.name = nm
    bpy.data.objects.remove(o, do_unlink=True)
    return me


def palm_mesh():
    nm = "SD_Palm_mesh"
    old = bpy.data.meshes.get(nm)
    if old is not None and old.users == 0:
        bpy.data.meshes.remove(old)
    mb = MB(); seg = 6; H = 10.0; nseg = 5
    rings = []
    for k in range(nseg + 1):
        f = k / nseg
        r = 0.24 - 0.09 * f
        off = 0.9 * f * f                                     # gentle lean
        z = H * f
        rings.append([mb.add_v((off + r * math.cos(2 * math.pi * i / seg), r * math.sin(2 * math.pi * i / seg), z)) for i in range(seg)])
    for k in range(nseg):
        for i in range(seg):
            j = (i + 1) % seg
            mb.face([rings[k][i], rings[k][j], rings[k + 1][j], rings[k + 1][i]], 0)
    top = (0.9, 0.0, H)
    for fidx in range(10):
        a = 2 * math.pi * fidx / 10 + 0.3 * (fidx % 2)
        d = Vector((math.cos(a), math.sin(a), 0)); side = Vector((-d.y, d.x, 0))
        prev = None
        for s in range(4):
            f = s / 3
            dist = 4.6 * f
            droop = 0.6 * f - 2.4 * f * f
            wdt = 0.75 * math.sin(math.pi * min(f + 0.15, 1.0)) + 0.05
            ctr = Vector(top) + d * dist + Vector((0, 0, droop))
            pair = (mb.add_v(ctr - side * wdt), mb.add_v(ctr + side * wdt))
            if prev is not None:
                mb.face([prev[0], pair[0], pair[1], prev[1]], 1)
            prev = pair
    o = mb.make("tmp_palm", ["SD_Palm_Trunk", "SD_Palm_Frond"])
    me = o.data; me.name = nm
    bpy.data.objects.remove(o, do_unlink=True)
    return me


def tree_mesh():
    nm = "SD_Tree_mesh"
    old = bpy.data.meshes.get(nm)
    if old is not None and old.users == 0:
        bpy.data.meshes.remove(old)
    mb = MB()
    mb.cylinder(0, 0, 0, 4.0, 0.7, 0.45, 8, 0)
    mb.dome(0, 0, 3.0, 6.0, 4.5, 10, 3, 1)
    mb.dome(2.0, 1.5, 5.0, 3.5, 3.0, 8, 2, 1)
    mb.dome(-2.0, -1.0, 4.6, 3.8, 3.2, 8, 2, 1)
    o = mb.make("tmp_tree", ["SD_Palm_Trunk", "SD_Tree_Canopy"])
    me = o.data; me.name = nm
    bpy.data.objects.remove(o, do_unlink=True)
    return me


def cannon_mesh():
    nm = "SD_Cannon_mesh"
    old = bpy.data.meshes.get(nm)
    if old is not None and old.users == 0:
        bpy.data.meshes.remove(old)
    mb = MB()
    mb.box(0, 0, 0.25, 1.5, 0.9, 0.35, 1)
    for x in (-0.5, 0.5):
        for y in (-0.5, 0.5):
            pass
    # barrel along +X
    seg = 10; L_ = 2.6
    b0 = [mb.add_v((-0.6, 0.22 * math.cos(2 * math.pi * k / seg), 0.85 + 0.22 * math.sin(2 * math.pi * k / seg))) for k in range(seg)]
    b1 = [mb.add_v((-0.6 + L_, 0.15 * math.cos(2 * math.pi * k / seg), 0.85 + 0.15 * math.sin(2 * math.pi * k / seg))) for k in range(seg)]
    for k in range(seg):
        j = (k + 1) % seg
        mb.face([b0[j], b0[k], b1[k], b1[j]], 0)
    mb.face(list(reversed(b0)), 0); mb.face(b1, 0)
    for x in (-0.45, 0.45):
        for y in (-0.5, 0.5):
            cy_ = y
            ring = [mb.add_v((x + 0.3 * math.cos(2 * math.pi * k / 8), cy_, 0.3 + 0.3 * math.sin(2 * math.pi * k / 8))) for k in range(8)]
            mb.face(ring, 1)
    o = mb.make("tmp_cannon", ["SD_Iron_Old", "SD_Wood_Old"])
    me = o.data; me.name = nm
    bpy.data.objects.remove(o, do_unlink=True)
    return me


def build_interior():
    pts, gate, beach = read_outline()
    c = sub("SD_30_Interior"); clear(c)
    for nm in ("SD_House_mesh_A", "SD_House_mesh_B", "SD_House_mesh_C", "SD_Palm_mesh", "SD_Tree_mesh", "SD_Cannon_mesh"):
        m = bpy.data.meshes.get(nm)
        if m is not None and m.users == 0:
            bpy.data.meshes.remove(m)
    cg = coll("SD_32_Shrines_Wells", c); ch = coll("SD_33_Settlement", c)
    cv = coll("SD_34_Vegetation", c); cp = coll("SD_35_Props", c)
    T, GZ, TOP = P["WALL_T"], P["GROUND_Z"], P["WALL_TOP"]
    inner = offset(pts, T)

    # ground with holes for the wells and the kund
    holes = [list(reversed(rect(*SITE["kund"], 8.0, 8.0)))]
    for k in ("dudhbav", "dahibav", "sakharbav"):
        holes.append(circle(*SITE[k], WELL_R, 12, ccw=False))
    ground(inner, holes, c)

    # gate geometry for the path start
    a = Vector(pts[gate[1]]); b = Vector(pts[gate[2]]); t = (b - a).normalized(); nin = Vector((-t.y, t.x))
    door_in = a + (b - a) * 0.6 + nin * (T + 1.0)
    sx_, sy_ = SITE["shivrajeshwar"]
    main = [tuple(door_in), tuple(door_in + nin * 14), (SITE["jarimari"][0] - 4, SITE["jarimari"][1] - 6),
            (110.0, 120.0), (70.0, 70.0), (38.0, 32.0), (sx_ + 14.5, sy_)]
    path_strip("SD_Path_Main", main, 3.0, c)
    mk = SITE["mahadev"]
    path_strip("SD_Path_Temple_Ring", [(sx_ + 14.5, sy_ - 7), (sx_ - 14, sy_ - 7), (mk[0] + 6, mk[1] - 6), (mk[0] + 6, mk[1] + 7),
                                       (sx_ - 14, sy_ + 7), (sx_ + 14.5, sy_ + 7)], 2.0, c)
    i_seg = (beach - 1) % len(pts) if beach is not None else None
    if i_seg is not None:
        a2 = Vector(pts[i_seg]); b2 = Vector(pts[beach]); t2 = (b2 - a2).normalized(); n2 = Vector((-t2.y, t2.x))
        post = a2 + (b2 - a2) * 0.82 + n2 * (T + 1.0)
        rv = [(sx_ - 4, sy_ - 7), (0.0, -40.0), SITE["mahapurush"], tuple(post + n2 * 12), tuple(post)]
        path_strip("SD_Path_RanichiVela", rv, 2.0, c)
    paths = [main, rv] if i_seg is not None else [main]

    temple_shivrajeshwar(c)
    temple_mahadev(cg)
    for k in ("dudhbav", "dahibav", "sakharbav"):
        well("SD_Well_" + k.capitalize(), *SITE[k], cg)
    tiled_shrine("SD_Temple_Jarimari", *SITE["jarimari"], 4.0, 4.0, 2.8, 1.6, cg, rot=math.radians(130))
    tiled_shrine("SD_Temple_Bhavani", *SITE["bhavani"], 5.5, 5.0, 3.4, 1.8, cg, rot=math.radians(90), dome=True)
    tiled_shrine("SD_Temple_Mahapurush", *SITE["mahapurush"], 3.6, 3.6, 2.6, 1.4, cg, rot=0.0)
    palace_ruin(cg)
    nishan_buruj(cg, bastion_mesh)

    # settlement: a handful of resident families' houses + the anganwadi / pre-primary school
    houses = [("A", 120, 190, 40), ("B", 132, 140, 130), ("C", 95, 160, 15), ("A", 75, 135, 100), ("C", 140, 95, 70),
              ("B", 40, 150, 10), ("A", 0, 175, 95), ("C", -35, 150, 30), ("A", 60, 205, 160), ("B", 120, 30, 80),
              ("C", 150, -10, 105), ("A", 95, -120, 20), ("C", 130, -150, 60), ("B", 40, -170, 120)]
    meshes = {k: house_mesh(k) for k in HOUSE_VARIANTS}
    for k, (v, x, y, r) in enumerate(houses):
        o = bpy.data.objects.new(f"SD_House_{k + 1:02d}", meshes[v])
        o.location = (x, y, GZ); o.rotation_euler = (0, 0, math.radians(r)); ch.objects.link(o)
    tiled_shrine("SD_Anganwadi_School", *SITE["school"], 14.0, 7.0, 3.2, 2.2, ch, rot=math.radians(40), wall_mat="SD_Plaster_Ochre")

    # cannons on a dozen sea-facing bastions, laid through an embrasure gap
    cm = cannon_mesh()
    bast = sorted([o for o in bpy.data.collections["SD_11_Bastions"].objects], key=lambda o: o.name)
    placed = 0
    for k, o in enumerate(bast):
        if k % 3 or "Gate" in o.name:
            continue
        out = math.radians(o["out_deg"]); r = o["radius_m"]
        step = 2 * math.pi / 16
        gaps = [step * (kk + 0.5) for kk in range(1, 16, 2)]
        g = min(gaps, key=lambda a: abs(math.atan2(math.sin(a - out), math.cos(a - out))))
        pos = Vector(o.location.xy) + Vector((math.cos(g), math.sin(g))) * (r - P["PARAPET_T"] - 1.6)
        cn = bpy.data.objects.new(f"SD_Cannon_{placed + 1:02d}", cm)
        cn.location = (pos.x, pos.y, TOP); cn.rotation_euler = (0, 0, g); cp.objects.link(cn); placed += 1

    # vegetation: coconut palms + a few broad trees, kept clear of buildings and the wall
    keep_out = [(SITE["shivrajeshwar"][0], SITE["shivrajeshwar"][1], 20), (SITE["mahadev"][0], SITE["mahadev"][1] - 8, 13),
                (*SITE["palace"], 17), (*SITE["nishan"], 9), (*SITE["school"], 10), (*SITE["jarimari"], 6),
                (*SITE["bhavani"], 7), (*SITE["mahapurush"], 5), (*SITE["dudhbav"], 4), (*SITE["dahibav"], 4), (*SITE["sakharbav"], 4)]
    keep_out += [(x, y, 9) for _, x, y, _ in houses]
    pm = palm_mesh(); tm = tree_mesh()
    def free(x, y, extra=0.0):
        if not point_in_poly(x, y, inner) or dist_to_poly(x, y, inner) < 7:
            return False
        if any((x - a_) ** 2 + (y - b_) ** 2 < (r_ + extra) ** 2 for a_, b_, r_ in keep_out):
            return False
        for lp in paths:
            for k in range(len(lp) - 1):
                a_, b_ = Vector(lp[k]), Vector(lp[k + 1]); ab = b_ - a_
                tt = max(0.0, min(1.0, (Vector((x, y)) - a_).dot(ab) / max(ab.length_squared, 1e-9)))
                if (a_ + ab * tt - Vector((x, y))).length < 4.5:
                    return False
        return True
    import random
    rng = random.Random(1664)
    palms = 0; i = 0
    while palms < 320 and i < 12000:
        i += 1
        x = -200 + 410 * rng.random(); y = -290 + 590 * rng.random()
        # palms cluster: denser in the north and east (inhabited, coconut groves)
        if rng.random() > 0.45 + 0.4 * (y > -50):
            continue
        if not free(x, y):
            continue
        o = bpy.data.objects.new(f"SD_Palm_{palms + 1:03d}", pm)
        s = 0.8 + 0.45 * rng.random()
        o.location = (x, y, GZ - 0.1); o.rotation_euler = (0, 0, 2 * math.pi * rng.random()); o.scale = (s, s, s)
        cv.objects.link(o); palms += 1
        keep_out.append((x, y, 3.5))
    trees = [(SITE["shivrajeshwar"][0] + 26, SITE["shivrajeshwar"][1] + 14), (SITE["mahadev"][0] - 12, SITE["mahadev"][1] + 16),
             (SITE["bhavani"][0] + 9, SITE["bhavani"][1] + 8), (-60, -60), (30, -90), (-120, -40), (60, 110), (-90, 120)]
    for k, (x, y) in enumerate(trees):
        o = bpy.data.objects.new(f"SD_Tree_{k + 1:02d}", tm)
        o.location = (x, y, GZ - 0.1); o.rotation_euler = (0, 0, k * 1.3); s = 0.9 + 0.3 * hrand(k, 41); o.scale = (s, s, s)
        cv.objects.link(o)
    return {"houses": len(houses), "cannons": placed, "palms": palms, "trees": len(trees)}
