# sd_gate.py - hidden (gomukhi) Mahadarwaja / Dilli Darwaja complex, doors, nagarkhana,
# Hanuman shrine, Shivaji hand/foot-print domes, jetty, and the Ranichi Vela postern.


def arch_profile(w, spring, seg=8, pointed=True):
    """Arch outline (x, z) CCW starting bottom-left; pointed (two-centred) Maratha-style arch."""
    pts = [(-w / 2, 0.0), (w / 2, 0.0), (w / 2, spring)]
    r = w * 0.8 if pointed else w / 2
    cxs = (w / 2 - r, -(w / 2 - r))   # right arc centred left of middle, left arc centred right
    top_z = spring + math.sqrt(max(r * r - (r - w / 2) ** 2, 0.0)) if pointed else spring + w / 2
    # right half: from (w/2, spring) up to apex (0, top)
    cx = cxs[0]
    a0 = 0.0; a1 = math.atan2(top_z - spring, 0 - cx)
    for k in range(1, seg + 1):
        a = a0 + (a1 - a0) * k / seg
        pts.append((cx + r * math.cos(a), spring + r * math.sin(a)))
    cx = cxs[1]
    b0 = math.atan2(top_z - spring, 0 - cx); b1 = math.pi
    for k in range(1, seg):
        a = b0 + (b1 - b0) * k / seg
        pts.append((cx + r * math.cos(a), spring + r * math.sin(a)))
    pts.append((-w / 2, spring))
    return pts, top_z


def fix_normals(o):
    bm = bmesh.new(); bm.from_mesh(o.data)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(o.data); bm.free(); o.data.update()


def extrude_profile(prof, y0, y1, mi_side=1, mi_floor=2):
    mb = MB()
    a = [mb.add_v((x, y0, z)) for x, z in prof]
    b = [mb.add_v((x, y1, z)) for x, z in prof]
    m = len(prof)
    mb.face(list(reversed(a)), mi_side); mb.face(b, mi_side)
    for k in range(m):
        j = (k + 1) % m
        mb.face([a[k], a[j], b[j], b[k]], mi_floor if k == 0 else mi_side)
    return mb


def cut(target, cutter):
    mod = target.modifiers.new("cut", 'BOOLEAN')
    mod.operation = 'DIFFERENCE'; mod.object = cutter
    try:
        mod.solver = 'EXACT'
    except Exception:
        pass
    try:
        mod.material_mode = 'INDEX'
    except Exception:
        pass
    dg = bpy.context.evaluated_depsgraph_get()
    ev = target.evaluated_get(dg)
    newme = bpy.data.meshes.new_from_object(ev, preserve_all_data_layers=True, depsgraph=dg)
    old = target.data
    target.modifiers.remove(mod)
    target.data = newme
    newme.name = target.name
    if old.users == 0:
        bpy.data.meshes.remove(old)
    cutter.hide_viewport = True; cutter.hide_render = True


def opening(name, pts, seg_i, frac, w, spring, z_floor, guides):
    """Arch cutter through the curtain wall on outline segment seg_i at fraction frac."""
    n = len(pts)
    a = Vector(pts[seg_i]); b = Vector(pts[(seg_i + 1) % n])
    t = (b - a).normalized(); nin = Vector((-t.y, t.x))
    p = a + (b - a) * frac
    prof, top = arch_profile(w, spring)
    mb = extrude_profile(prof, -2.0, P["WALL_T"] + 2.0)
    o = mb.make(name, ["SD_Stone_Wall", "SD_Stone_Wall_Inner", "SD_Stone_Walkway"], guides,
                loc=(p.x, p.y, z_floor), rot=(0, 0, math.atan2(t.y, t.x)))
    fix_normals(o)
    o.display_type = 'WIRE'
    return o, p, t, nin, top


def door_leaf(name, w, h, thick, spikes, coll_, loc, rot_z, hinge_left=True):
    """Wooden leaf with origin on the hinge edge; iron spikes on the outer (−Y) face."""
    mb = MB()
    x0, x1 = (0.0, w) if hinge_left else (-w, 0.0)
    mb.prism([(x0, -thick), (x1, -thick), (x1, 0.0), (x0, 0.0)], 0.0, h, 0, 0, 0)
    if spikes:
        for row in range(3):
            zc = h * (0.35 + 0.18 * row)
            for col in range(3):
                xc = x0 + w * (0.2 + 0.3 * col)
                s = 0.06
                base = [mb.add_v((xc - s, -thick, zc - s)), mb.add_v((xc + s, -thick, zc - s)),
                        mb.add_v((xc + s, -thick, zc + s)), mb.add_v((xc - s, -thick, zc + s))]
                tip = mb.add_v((xc, -thick - 0.22, zc))
                for k in range(4):
                    mb.face([base[(k + 1) % 4], base[k], tip], 1)
    return mb.make(name, ["SD_Wood_Old", "SD_Iron_Old"], coll_, loc=loc, rot=(0, 0, rot_z))


def build_gate():
    pts, gate, beach = read_outline()
    c = sub("SD_20_Gate_Complex"); clear(c)
    guides = sub("SD_00_Guides")
    for nm in ("SD_CUT_Mahadarwaja", "SD_CUT_RanichiVela"):
        o = bpy.data.objects.get(nm)
        if o is not None:
            bpy.data.objects.remove(o, do_unlink=True)
    wall = bpy.data.objects["SD_Wall_Curtain"]
    T, TOP, GZ, Z0 = P["WALL_T"], P["WALL_TOP"], P["GROUND_Z"], P["FOOT_Z"]
    A, NOTCH, DEND, B = [Vector(pts[i]) for i in gate]
    out = {}

    # ---- main gate opening on the notch -> door-wall-end segment (faces the screened courtyard) ----
    W, SPRING = 3.0, 3.4
    if not wall.get("cut_gate"):
        cutter, p, t, nin, top = opening("SD_CUT_Mahadarwaja", pts, gate[1], 0.6, W, SPRING, GZ - 0.4, guides)
        cut(wall, cutter); wall["cut_gate"] = True
    else:
        cutter = bpy.data.objects.get("SD_CUT_Mahadarwaja")
    a = Vector(pts[gate[1]]); b = Vector(pts[gate[2]])
    t = (b - a).normalized(); nin = Vector((-t.y, t.x)); p = a + (b - a) * 0.6
    ang = math.atan2(t.y, t.x)
    prof, top = arch_profile(W, SPRING)
    prof_o, _ = arch_profile(W + 1.2, SPRING + 0.1)
    # arch surround: outer profile minus inner profile, as a frame proud of the battered face
    mb = MB()
    m = len(prof)
    def ring_pts(pp, y):
        return [mb.add_v((x, y, z)) for x, z in pp]
    # resample both outlines to the same count by construction (same seg) -> same length lists
    fi0 = ring_pts(prof, -0.75); fi1 = ring_pts(prof, -0.2)
    fo0 = ring_pts(prof_o, -0.75); fo1 = ring_pts(prof_o, -0.2)
    for k in range(1, m):                       # skip the floor edge (k = 0)
        j = (k + 1) % m
        mb.face([fo0[k], fo0[j], fi0[j], fi0[k]])   # front face
        mb.face([fo0[j], fo0[k], fo1[k], fo1[j]])   # outer reveal
        mb.face([fi0[k], fi0[j], fi1[j], fi1[k]])   # inner reveal
    frame = mb.make("SD_Gate_Arch_Frame", ["SD_Stone_Dressed"], c, loc=(p.x, p.y, GZ - 0.4), rot=(0, 0, ang))
    fix_normals(frame)
    # passage floor slab (dressed stone) through the wall thickness
    mb = MB(); mb.box(0, T / 2, -0.05, W, T + 1.6, 0.05, 0)
    mb.make("SD_Gate_Passage_Floor", ["SD_Path_Paving"], c, loc=(p.x, p.y, GZ - 0.4), rot=(0, 0, ang))
    # doors: hinged inside the passage, swung ~70 deg inward
    leaf_w, leaf_h = W / 2, SPRING + 0.9
    hinge_y = T * 0.55
    for side, sgn in (("L", -1), ("R", 1)):
        hx = sgn * W / 2
        hp = p + t * hx + nin * hinge_y
        rz = ang + (1 if side == "L" else -1) * math.radians(70)
        door_leaf(f"SD_Gate_Door_{side}", leaf_w, leaf_h, 0.18, True, c, (hp.x, hp.y, GZ - 0.4), rz, hinge_left=(side == "L"))

    # ---- screen wall: runs south from bastion B so the door is invisible from the sea ----
    d = (A - B); L = d.length; d.normalize()
    west = Vector((d.y, -d.x))          # right of the southward run = into the courtyard
    s0 = B + d * (0.08 * L); s1 = B + d * (0.58 * L)
    T2 = 3.0
    poly = [(s0.x, s0.y), (s1.x, s1.y), ((s1 + west * T2).x, (s1 + west * T2).y), ((s0 + west * T2).x, (s0 + west * T2).y)]
    if signed_area(poly) < 0:
        poly = poly[::-1]
    mb = MB(); mb.prism(poly, 0.0, TOP, 0, 1)
    # parapet strip along the sea face + merlons
    pp = [(s0.x, s0.y), (s1.x, s1.y), ((s1 + west * P["PARAPET_T"]).x, (s1 + west * P["PARAPET_T"]).y), ((s0 + west * P["PARAPET_T"]).x, (s0 + west * P["PARAPET_T"]).y)]
    if signed_area(pp) < 0:
        pp = pp[::-1]
    mb.prism(pp, TOP, TOP + P["PARAPET_H"], 2, 2)
    s = 1.0; seglen = (s1 - s0).length
    while s + P["MERLON_W"] < seglen - 1.0:
        mid = s0 + d * (s + P["MERLON_W"] / 2) + west * (P["PARAPET_T"] / 2)
        mb.box(mid.x, mid.y, TOP + P["PARAPET_H"], P["MERLON_W"], P["PARAPET_T"], P["MERLON_H"], 2, math.atan2(d.y, d.x))
        s += P["MERLON_W"] + P["MERLON_GAP"]
    mb.make("SD_Gate_Screen_Wall", ["SD_Stone_Wall", "SD_Stone_Walkway", "SD_Stone_Parapet"], c)

    # ---- courtyard paving between door wall and screen ----
    cy = [tuple(A), tuple(NOTCH), tuple(DEND), tuple(B)]
    if signed_area(cy) < 0:
        cy = cy[::-1]
    mb = MB(); mb.prism(cy, 0.0, GZ - 0.45, 0, 0)
    mb.make("SD_Gate_Courtyard_Floor", ["SD_Path_Paving"], c)

    # ---- nagarkhana (drum house) ruin above the gate ----
    cc = p + nin * (T / 2)
    mb = MB()
    for (ox, oy, sx, sy, h) in ((0, -1.6, 7.0, 0.5, 2.8), (0, 1.6, 7.0, 0.5, 1.5), (-3.25, 0, 0.5, 2.7, 2.2), (3.25, 0, 0.5, 2.7, 1.0)):
        q = cc + t * ox + nin * oy
        mb.box(q.x, q.y, TOP, sx, sy, h, 0, ang)
    mb.make("SD_Gate_Nagarkhana_Ruin", ["SD_Stone_Ruin"], c)

    # ---- Shivaji hand + foot print domes (to the right of the gate seen from outside = north) ----
    for nm, f in (("SD_Shivaji_Handprint_Dome", 0.84), ("SD_Shivaji_Footprint_Dome", 0.93)):
        q = a + (b - a) * f + nin * (T * 0.55)
        mb = MB(); mb.box(0, 0, 0, 1.1, 1.1, 0.7, 0)
        mb.dome(0, 0, 0.7, 0.62, 0.6, seg=8, rings=3, mi=0)
        mb.cylinder(0, 0, 1.3, 1.55, 0.06, 0.02, seg=6, mi=1)
        mb.make(nm, ["SD_Plaster_Shrine", "SD_Brass"], c, loc=(q.x, q.y, TOP), rot=(0, 0, ang))

    # ---- Hanuman (Maruti) shrine just inside the gate ----
    q = p + nin * (T + 8.0) + t * 5.0
    mb = MB(); mb.box(0, 0, 0, 3.2, 3.2, 0.4, 0)
    mb.box(0, 0, 0.4, 2.6, 2.6, 2.4, 1)
    mb.dome(0, 0, 2.8, 1.5, 1.4, seg=8, rings=3, mi=1)
    mb.box(0, -1.35, 0.4, 0.7, 0.15, 1.2, 2)       # sindoor-coated image at the opening
    mb.make("SD_Shrine_Hanuman", ["SD_Stone_Dressed", "SD_Plaster_Shrine", "SD_Sindoor"], c,
            loc=(q.x, q.y, GZ), rot=(0, 0, ang))

    # ---- jetty at the mouth of the gate approach ----
    east = Vector((-d.y, d.x))
    mouth = s1 + (A - s1) * 0.35 + east * 6.0
    mb = MB()
    jl, jw = 32.0, 6.0
    mb.box(jl / 2, 0, -1.6, jl, jw, 2.9, 0)
    for k in range(4):
        mb.box(jl + 0.45 + k * 0.9, 0, -1.6, 0.9, jw, 2.9 - (k + 1) * 0.55, 0)
    for k in range(3):
        mb.box(6 + k * 9, jw / 2 - 0.5, 1.3, 0.5, 0.5, 0.6, 1)   # sandstone anchors / mooring stones
    mb.make("SD_Jetty", ["SD_Stone_Dressed", "SD_Stone_Ruin"], c, loc=(mouth.x, mouth.y, 0), rot=(0, 0, math.atan2(east.y, east.x)))

    # ---- Ranichi Vela postern (small door in the south wall onto the queen's beach) ----
    if beach is not None:
        i_seg = (beach - 1) % len(pts)
        wall = bpy.data.objects["SD_Wall_Curtain"]
        if not wall.get("cut_postern"):
            cutter2, *_ = opening("SD_CUT_RanichiVela", pts, i_seg, 0.82, 1.4, 1.8, 1.0, guides)
            cut(wall, cutter2); wall["cut_postern"] = True
        a2 = Vector(pts[i_seg]); b2 = Vector(pts[beach]); t2 = (b2 - a2).normalized(); n2 = Vector((-t2.y, t2.x))
        p2 = a2 + (b2 - a2) * 0.82
        door_leaf("SD_Door_RanichiVela", 1.4, 2.5, 0.15, False, c, ((p2 - t2 * 0.7 + n2 * 1.8).x, (p2 - t2 * 0.7 + n2 * 1.8).y, 1.0),
                  math.atan2(t2.y, t2.x), hinge_left=True)
        out["postern"] = True
    out.update({"gate_door_xy": [round(p.x, 1), round(p.y, 1)], "arch_top_z": round(GZ - 0.4 + top, 2)})
    return out
