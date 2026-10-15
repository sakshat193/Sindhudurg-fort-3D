# sd_core.py - shared helpers for the Sindhudurg build (Blender 4.2+/5.x).
# Units: metres, Z up, +Y = north, +X = east (towards Malvan).
import bpy, bmesh, math
from mathutils import Vector

SCENE_NAME = "Sindhudurg"

# ---------------- researched dimensions (see notes in the README text) ----------------
P = dict(
    WALL_H=9.1,        # 30 ft above the inner ground (1880 gazetteer 29-30 ft, CCRT 9 m)
    WALL_T=3.7,        # 12 ft thick
    GROUND_Z=2.0,      # interior ground level above mean sea level (assumed)
    FOOT_Z=0.4,        # outer wall foot on the rock shelf (assumed)
    BATTER=0.6,        # outer face lean: base sits this far outside the top line
    PARAPET_H=1.0, PARAPET_T=0.7,
    MERLON_W=1.4, MERLON_GAP=0.9, MERLON_H=0.8,
    BASTION_R=6.5, BASTION_R_SALIENT=7.5, BASTION_R_GATE=9.0,
)
P["WALL_TOP"] = P["GROUND_Z"] + P["WALL_H"]


# ---------------- scene / collections ----------------
def scene():
    sc = bpy.data.scenes.get(SCENE_NAME)
    if sc is None:
        sc = bpy.data.scenes.new(SCENE_NAME)
        sc.unit_settings.system = 'METRIC'
        sc.unit_settings.length_unit = 'METERS'
    return sc


def coll(name, parent=None):
    sc = scene()
    c = bpy.data.collections.get(name)
    if c is None:
        c = bpy.data.collections.new(name)
    par = parent if parent is not None else sc.collection
    if c.name not in [x.name for x in par.children]:
        par.children.link(c)
    return c


def root():
    return coll("SINDHUDURG")


def sub(name):
    return coll(name, root())


def clear(c):
    """Delete every object in collection c (and its children) - only our own SD_ data."""
    for ch in list(c.children):
        clear(ch)
    for o in list(c.objects):
        data = o.data
        bpy.data.objects.remove(o, do_unlink=True)
        if data is not None and getattr(data, "users", 1) == 0:
            if isinstance(data, bpy.types.Mesh):
                bpy.data.meshes.remove(data)
            elif isinstance(data, bpy.types.Curve):
                bpy.data.curves.remove(data)


# ---------------- materials ----------------
MATS = {
    # name: (base colour, roughness, metallic, tile size in metres)
    "SD_Stone_Wall":        ((0.20, 0.19, 0.18), 0.9, 0.0, 3.0),
    "SD_Stone_Wall_Inner":  ((0.29, 0.27, 0.25), 0.9, 0.0, 3.0),
    "SD_Stone_Walkway":     ((0.40, 0.38, 0.35), 0.85, 0.0, 2.0),
    "SD_Stone_Parapet":     ((0.25, 0.24, 0.23), 0.9, 0.0, 2.0),
    "SD_Stone_Bastion":     ((0.21, 0.20, 0.19), 0.9, 0.0, 3.0),
    "SD_Stone_Dressed":     ((0.46, 0.43, 0.38), 0.75, 0.0, 1.5),
    "SD_Stone_Ruin":        ((0.34, 0.30, 0.26), 0.95, 0.0, 2.0),
    "SD_Laterite":          ((0.52, 0.28, 0.18), 0.9, 0.0, 1.5),
    "SD_Plaster_Lime":      ((0.86, 0.83, 0.75), 0.8, 0.0, 2.0),
    "SD_Plaster_Ochre":     ((0.80, 0.60, 0.36), 0.8, 0.0, 2.0),
    "SD_Plaster_Shrine":    ((0.92, 0.88, 0.80), 0.7, 0.0, 1.0),
    "SD_Roof_Tile":         ((0.55, 0.21, 0.11), 0.7, 0.0, 1.5),
    "SD_Wood_Old":          ((0.27, 0.16, 0.08), 0.8, 0.0, 1.0),
    "SD_Iron_Old":          ((0.13, 0.12, 0.11), 0.6, 0.8, 0.5),
    "SD_Brass":             ((0.80, 0.58, 0.20), 0.35, 1.0, 0.5),
    "SD_Sindoor":           ((0.90, 0.33, 0.04), 0.6, 0.0, 0.5),
    "SD_Ground_Soil":       ((0.36, 0.33, 0.19), 0.95, 0.0, 4.0),
    "SD_Path_Paving":       ((0.47, 0.44, 0.39), 0.85, 0.0, 2.0),
    "SD_Rock_Island":       ((0.16, 0.15, 0.14), 0.9, 0.0, 4.0),
    "SD_Sand":              ((0.78, 0.67, 0.49), 0.95, 0.0, 3.0),
    "SD_Water_Sea":         ((0.04, 0.22, 0.27), 0.05, 0.0, 20.0),
    "SD_Water_Well":        ((0.06, 0.15, 0.10), 0.05, 0.0, 2.0),
    "SD_Palm_Trunk":        ((0.33, 0.26, 0.19), 0.9, 0.0, 1.0),
    "SD_Palm_Frond":        ((0.17, 0.33, 0.09), 0.7, 0.0, 1.0),
    "SD_Tree_Canopy":       ((0.14, 0.28, 0.09), 0.8, 0.0, 2.0),
    "SD_Flag_Saffron":      ((0.96, 0.42, 0.04), 0.7, 0.0, 1.0),
    "SD_Guide":             ((1.0, 0.1, 0.6), 0.5, 0.0, 1.0),
}


def mat(name):
    m = bpy.data.materials.get(name)
    if m is not None:
        return m
    col, rough, metal, tile = MATS[name]
    m = bpy.data.materials.new(name)
    try:
        m.use_nodes = True
    except Exception:
        pass
    m.diffuse_color = (*col, 1.0)
    m["tile_m"] = tile
    nt = m.node_tree
    bsdf = next((n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED'), None)
    if bsdf is None:
        bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = (*col, 1.0)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metal
    # ready-made texture hookup: UV (metres) -> Mapping (1/tile) -> empty Image Texture
    tc = nt.nodes.new("ShaderNodeTexCoord"); tc.location = (-900, 300)
    mp = nt.nodes.new("ShaderNodeMapping"); mp.location = (-700, 300)
    mp.label = f"Tile {tile:g} m (scale = 1/tile)"
    mp.inputs["Scale"].default_value = (1.0 / tile, 1.0 / tile, 1.0)
    im = nt.nodes.new("ShaderNodeTexImage"); im.location = (-450, 300)
    im.label = "PLUG TEXTURE HERE -> Base Color"
    nt.links.new(tc.outputs["UV"], mp.inputs["Vector"])
    nt.links.new(mp.outputs["Vector"], im.inputs["Vector"])
    if name.startswith("SD_Water"):
        bsdf.inputs["Roughness"].default_value = 0.04
    return m


# ---------------- 2D polygon helpers ----------------
def signed_area(pts):
    a = 0.0
    for i in range(len(pts)):
        x1, y1 = pts[i]; x2, y2 = pts[(i + 1) % len(pts)]
        a += x1 * y2 - x2 * y1
    return a / 2


def seg_normals(pts):
    """Inward unit normals of each edge i->i+1 for a CCW polygon."""
    out = []
    for i in range(len(pts)):
        a = Vector(pts[i]); b = Vector(pts[(i + 1) % len(pts)])
        t = (b - a).normalized()
        out.append(Vector((-t.y, t.x)))
    return out


def offset(pts, d, max_miter=4.0):
    """Vertex-correspondent mitred offset. d>0 = inward for a CCW polygon."""
    n = len(pts)
    nrm = seg_normals(pts)
    res = []
    for i in range(n):
        n1 = nrm[i - 1]; n2 = nrm[i]
        m = n1 + n2
        if m.length < 1e-6:
            m = n1.copy()
        m.normalize()
        k = max(m.dot(n1), 1.0 / max_miter)
        p = Vector(pts[i]) + m * (d / k)
        res.append((p.x, p.y))
    return res


def is_convex_vertex(pts, i):
    a = Vector(pts[i - 1]); b = Vector(pts[i]); c = Vector(pts[(i + 1) % len(pts)])
    return (b.x - a.x) * (c.y - b.y) - (b.y - a.y) * (c.x - b.x) > 0


def cumlen(pts):
    c = [0.0]
    for i in range(len(pts)):
        c.append(c[-1] + (Vector(pts[(i + 1) % len(pts)]) - Vector(pts[i])).length)
    return c


def point_in_poly(x, y, pts):
    ins = False
    j = len(pts) - 1
    for i in range(len(pts)):
        xi, yi = pts[i]; xj, yj = pts[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi + 1e-12) + xi:
            ins = not ins
        j = i
    return ins


def dist_to_poly(x, y, pts):
    best = 1e18
    p = Vector((x, y))
    for i in range(len(pts)):
        a = Vector(pts[i]); b = Vector(pts[(i + 1) % len(pts)])
        ab = b - a
        t = max(0.0, min(1.0, (p - a).dot(ab) / max(ab.length_squared, 1e-9)))
        best = min(best, (a + ab * t - p).length)
    return best


# ---------------- deterministic noise ----------------
def hrand(i, salt=0):
    x = math.sin(i * 12.9898 + salt * 78.233) * 43758.5453
    return x - math.floor(x)


# ---------------- mesh builder with metric UVs ----------------
def _planar_uv(co, n):
    if abs(n.z) > 0.95:
        return (co.x, co.y)
    t = Vector((0, 0, 1)).cross(n)
    if t.length < 1e-6:
        t = Vector((1, 0, 0))
    t.normalize()
    b = n.cross(t)
    return (co.dot(t), co.dot(b))


def build(name, verts, faces, mats, face_mats=None, coll_=None, uvs=None,
          loc=(0, 0, 0), rot=(0, 0, 0), mesh=None, smooth=False):
    """Create an object. uvs: optional list (per face) of list of (u,v) per corner.
    Without uvs every face gets a world-metre planar projection (1 UV unit = 1 m)."""
    if mesh is None:
        me = bpy.data.meshes.new(name)
        me.from_pydata([tuple(v) for v in verts], [], [tuple(f) for f in faces])
        me.validate(clean_customdata=False)
        uvl = me.uv_layers.new(name="UVMap")
        for p in me.polygons:
            n = p.normal
            for k, li in enumerate(p.loop_indices):
                if uvs is not None and p.index < len(uvs) and uvs[p.index] is not None:
                    uvl.data[li].uv = uvs[p.index][k]
                else:
                    uvl.data[li].uv = _planar_uv(me.vertices[me.loops[li].vertex_index].co, n)
        for m in mats:
            me.materials.append(mat(m))
        if face_mats:
            me.polygons.foreach_set("material_index", list(face_mats))
        for p in me.polygons:
            p.use_smooth = smooth
        me.update()
    else:
        me = mesh
    o = bpy.data.objects.new(name, me)
    o.location = loc
    o.rotation_euler = rot
    (coll_ or root()).objects.link(o)
    return o


class MB:
    """Tiny mesh accumulator: add boxes/prisms/rings into one mesh with material indices."""

    def __init__(self):
        self.v, self.f, self.m, self.uv = [], [], [], []

    def face(self, idx, mi=0, uv=None):
        self.f.append(idx); self.m.append(mi); self.uv.append(uv)

    def add_v(self, co):
        self.v.append(tuple(co)); return len(self.v) - 1

    def prism(self, poly2d, z0, z1, mi_side=0, mi_top=0, mi_bot=None, top=True):
        """Extrude a CCW 2D polygon between z0 and z1."""
        n = len(poly2d)
        b = [self.add_v((x, y, z0)) for x, y in poly2d]
        t = [self.add_v((x, y, z1)) for x, y in poly2d]
        for i in range(n):
            j = (i + 1) % n
            self.face([b[i], b[j], t[j], t[i]], mi_side)
        if top:
            self.face(t, mi_top)
        if mi_bot is not None:
            self.face(list(reversed(b)), mi_bot)
        return b, t

    def box(self, cx, cy, z0, sx, sy, h, mi=0, rot=0.0, mi_top=None):
        c, s = math.cos(rot), math.sin(rot)
        pts = []
        for dx, dy in ((-sx / 2, -sy / 2), (sx / 2, -sy / 2), (sx / 2, sy / 2), (-sx / 2, sy / 2)):
            pts.append((cx + dx * c - dy * s, cy + dx * s + dy * c))
        self.prism(pts, z0, z0 + h, mi, mi if mi_top is None else mi_top)

    def hip_roof(self, cx, cy, z, sx, sy, rise, mi=0, rot=0.0, over=0.6):
        """Hipped roof over an sx*sy rectangle (with eave overhang)."""
        if sy > sx:
            sx, sy, rot = sy, sx, rot + math.pi / 2
        sx += 2 * over; sy += 2 * over
        c, s = math.cos(rot), math.sin(rot)
        def P_(dx, dy, dz):
            return self.add_v((cx + dx * c - dy * s, cy + dx * s + dy * c, z + dz))
        ridge = max(sx - sy, 0.0) / 2
        a = P_(-sx / 2, -sy / 2, 0); b = P_(sx / 2, -sy / 2, 0)
        cc = P_(sx / 2, sy / 2, 0); d = P_(-sx / 2, sy / 2, 0)
        r1 = P_(-ridge, 0, rise); r2 = P_(ridge, 0, rise)
        self.face([a, b, r2, r1], mi)
        self.face([b, cc, r2], mi)
        self.face([cc, d, r1, r2], mi)
        self.face([d, a, r1], mi)
        self.face([a, d, cc, b], mi)  # soffit (underside)

    def pyramid_roof(self, cx, cy, z, sx, sy, rise, mi=0, over=0.4):
        self.hip_roof(cx, cy, z, max(sx, sy), max(sx, sy), rise, mi, 0.0, over)

    def cylinder(self, cx, cy, z0, z1, r0, r1, seg=16, mi=0, top=True, mi_top=None, rot=0.0):
        b, t = [], []
        for k in range(seg):
            a = rot + 2 * math.pi * k / seg
            b.append(self.add_v((cx + r0 * math.cos(a), cy + r0 * math.sin(a), z0)))
            t.append(self.add_v((cx + r1 * math.cos(a), cy + r1 * math.sin(a), z1)))
        for k in range(seg):
            j = (k + 1) % seg
            self.face([b[k], b[j], t[j], t[k]], mi)
        if top:
            self.face(t, mi if mi_top is None else mi_top)
        return b, t

    def dome(self, cx, cy, z, r, h, seg=8, rings=3, mi=0):
        prev = None
        for k in range(rings + 1):
            ang = (math.pi / 2) * k / rings
            rr = r * math.cos(ang); zz = z + h * math.sin(ang)
            if k == rings:
                apex = self.add_v((cx, cy, zz))
                for i in range(seg):
                    self.face([prev[i], prev[(i + 1) % seg], apex], mi)
                break
            ring = [self.add_v((cx + rr * math.cos(2 * math.pi * i / seg), cy + rr * math.sin(2 * math.pi * i / seg), zz)) for i in range(seg)]
            if prev is not None:
                for i in range(seg):
                    j = (i + 1) % seg
                    self.face([prev[i], prev[j], ring[j], ring[i]], mi)
            prev = ring

    def make(self, name, mats, coll_=None, loc=(0, 0, 0), rot=(0, 0, 0), smooth=False):
        return build(name, self.v, self.f, mats, self.m, coll_, self.uv if any(u is not None for u in self.uv) else None,
                     loc, rot, smooth=smooth)


# ---------------- outline guide ----------------
def read_outline():
    """Return (pts CCW list of (x,y), gate (A,notch,doorEnd,B) indices, beach index) from SD_GUIDE_Outline."""
    o = bpy.data.objects.get("SD_GUIDE_Outline")
    if o is None:
        raise RuntimeError("SD_GUIDE_Outline missing - run sd_outline first")
    me = o.data
    mw = o.matrix_world
    # walk the edge loop from vertex 0 so the user can edit/retrace freely
    adj = {v.index: [] for v in me.vertices}
    for e in me.edges:
        a, b = e.vertices
        adj[a].append(b); adj[b].append(a)
    order = [0]; prev = None; cur = 0
    while True:
        nxt = [x for x in adj[cur] if x != prev]
        if not nxt or nxt[0] == 0:
            break
        prev, cur = cur, nxt[0]
        order.append(cur)
    pts = [tuple((mw @ me.vertices[i].co).xy) for i in order]
    flip = signed_area(pts) < 0
    if flip:
        pts = pts[::-1]
    def find(tag):
        idx = []
        for k in range(4 if tag == "gate" else 1):
            nm = f"SD_GUIDE_{'Gate' + 'ABCD'[k] if tag == 'gate' else 'Beach'}"
            e = bpy.data.objects.get(nm)
            if e is None:
                return None
            p = Vector(e.location.xy)
            idx.append(min(range(len(pts)), key=lambda i: (Vector(pts[i]) - p).length))
        return idx
    gate = find("gate"); beach = find("beach")
    return pts, gate, (beach[0] if beach else None)
