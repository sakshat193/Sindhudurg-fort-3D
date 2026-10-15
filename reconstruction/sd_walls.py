# sd_walls.py - curtain wall, parapet + merlons, 42 bastions, wall stairs.


def bastion_sites(pts, gate, target):
    """Bastions on every salient, then extra towers spread along the longest straight faces
    (never in re-entrant corners, never on the gate segments)."""
    n = len(pts)
    cum = cumlen(pts)
    nrm = seg_normals(pts)
    sites = []
    for i in range(n):
        if is_convex_vertex(pts, i):
            kind = "gate" if i in (gate[0], gate[-1]) else "salient"
            sites.append(dict(s=cum[i], seg=i, xy=Vector(pts[i]), out=-(nrm[i - 1] + nrm[i]).normalized(), kind=kind))
    gate_segs = set(range(gate[0], gate[-1]))
    count = {i: 0 for i in range(n) if i not in gate_segs}
    seglen = {i: cum[i + 1] - cum[i] for i in count}
    while len(sites) + sum(count.values()) < target:
        i = max(count, key=lambda k: seglen[k] / (count[k] + 1))
        count[i] += 1
    for i, k in count.items():
        a = Vector(pts[i]); b = Vector(pts[(i + 1) % n])
        for j in range(k):
            f = (j + 1) / (k + 1)
            sites.append(dict(s=cum[i] + f * seglen[i], seg=i, xy=a + (b - a) * f, out=-nrm[i], kind="face"))
    sites.sort(key=lambda d: d["s"])
    return sites


def bastion_mesh(name, r, z0, z1, batter, seg=16):
    """Round bastion: battered drum + deck + crenellated parapet. Cylindrical metre UVs."""
    PH, PT, MH = P["PARAPET_H"], P["PARAPET_T"], P["MERLON_H"]
    V, F, M, U = [], [], [], []
    def ring(rad, z):
        base = len(V)
        for k in range(seg):
            a = 2 * math.pi * k / seg
            V.append((rad * math.cos(a), rad * math.sin(a), z))
        return base
    def quad_strip(b0, b1, r_uv0, r_uv1, z0_, z1_, mi, outward=True, only=None):
        for k in range(seg):
            if only is not None and not only(k):
                continue
            j = (k + 1) % seg
            u0 = 2 * math.pi * k / seg * r_uv0; u1 = 2 * math.pi * (k + 1) / seg * r_uv0
            if outward:
                F.append((b0 + k, b0 + j, b1 + j, b1 + k)); U.append([(u0, z0_), (u1, z0_), (u1, z1_), (u0, z1_)])
            else:
                F.append((b0 + j, b0 + k, b1 + k, b1 + j)); U.append([(u1, z0_), (u0, z0_), (u0, z1_), (u1, z1_)])
            M.append(mi)
    ri = r - PT
    b_bot = ring(r + batter, z0); b_top = ring(r, z1)
    quad_strip(b_bot, b_top, r, r, z0, z1, 0)                       # drum
    p_out = ring(r, z1 + PH); quad_strip(b_top, p_out, r, r, z1, z1 + PH, 2)
    p_in_top = ring(ri, z1 + PH); p_in_bot = ring(ri, z1)
    quad_strip(p_in_bot, p_in_top, ri, ri, z1, z1 + PH, 2, outward=False)
    # parapet top band
    for k in range(seg):
        j = (k + 1) % seg
        F.append((p_out + k, p_out + j, p_in_top + j, p_in_top + k)); M.append(2); U.append(None)
    # deck
    F.append(tuple(p_in_bot + k for k in range(seg))); M.append(1); U.append(None)
    # merlons on every other facet; the gaps are the gun embrasures
    for k in range(0, seg, 2):
        j = (k + 1) % seg
        a0 = len(V)
        for rad in (r, ri):
            for kk in (k, j):
                a = 2 * math.pi * kk / seg
                V.append((rad * math.cos(a), rad * math.sin(a), z1 + PH))
        for rad in (r, ri):
            for kk in (k, j):
                a = 2 * math.pi * kk / seg
                V.append((rad * math.cos(a), rad * math.sin(a), z1 + PH + MH))
        o0, o1, i0, i1, O0, O1, I0, I1 = range(a0, a0 + 8)
        for f in ((o0, o1, O1, O0), (i1, i0, I0, I1), (O0, O1, I1, I0), (o1, i1, I1, O1), (i0, o0, O0, I0)):
            F.append(f); M.append(2); U.append(None)
    me = bpy.data.meshes.new(name)
    me.from_pydata(V, [], F)
    uvl = me.uv_layers.new(name="UVMap")
    for p in me.polygons:
        for k, li in enumerate(p.loop_indices):
            uvl.data[li].uv = U[p.index][k] if U[p.index] is not None else _planar_uv(me.vertices[me.loops[li].vertex_index].co, p.normal)
    for mname in ("SD_Stone_Bastion", "SD_Stone_Walkway", "SD_Stone_Parapet"):
        me.materials.append(mat(mname))
    me.polygons.foreach_set("material_index", M)
    me.update()
    return me


def build_walls():
    pts, gate, beach = read_outline()
    c = sub("SD_10_Fortifications"); clear(c)
    cb = coll("SD_11_Bastions", c); cs = coll("SD_12_Wall_Stairs", c)
    n = len(pts)
    T, H, Z0, TOP = P["WALL_T"], P["WALL_H"], P["FOOT_Z"], P["WALL_TOP"]
    GZ = P["GROUND_Z"]
    cum = cumlen(pts)
    outer_top = pts
    outer_bot = offset(pts, -P["BATTER"])
    inner = offset(pts, T)

    # ---------- curtain wall ring ----------
    V, F, M, U = [], [], [], []
    ot = [len(V) + i for i in range(n)]; V += [(x, y, TOP) for x, y in outer_top]
    ob = [len(V) + i for i in range(n)]; V += [(x, y, Z0) for x, y in outer_bot]
    it = [len(V) + i for i in range(n)]; V += [(x, y, TOP) for x, y in inner]
    ib = [len(V) + i for i in range(n)]; V += [(x, y, GZ - 0.3) for x, y in inner]
    for i in range(n):
        j = (i + 1) % n
        u0, u1 = cum[i], cum[i + 1]
        F.append((ob[i], ob[j], ot[j], ot[i])); M.append(0); U.append([(u0, Z0), (u1, Z0), (u1, TOP), (u0, TOP)])
        F.append((ot[i], ot[j], it[j], it[i])); M.append(2); U.append([(u0, 0), (u1, 0), (u1, T), (u0, T)])
        F.append((it[i], it[j], ib[j], ib[i])); M.append(1); U.append([(u0, TOP), (u1, TOP), (u1, GZ - .3), (u0, GZ - .3)])
        F.append((ib[i], ib[j], ob[j], ob[i])); M.append(0); U.append(None)
    wall = build("SD_Wall_Curtain", V, F, ["SD_Stone_Wall", "SD_Stone_Wall_Inner", "SD_Stone_Walkway"], M, c, U)
    wall["source"] = "30 ft (9.1 m) high above inner ground, 12 ft (3.7 m) thick - 1880 gazetteer / Wikipedia / CCRT"

    # ---------- bastions ----------
    target = int(bpy.data.objects["SD_GUIDE_Outline"].get("bastion_target", 42))
    sites = bastion_sites(pts, gate, target)
    centers = []
    gi = 0
    for k, s in enumerate(sites):
        r = {"gate": P["BASTION_R_GATE"], "salient": P["BASTION_R_SALIENT"], "face": P["BASTION_R"]}[s["kind"]]
        r *= 0.9 + 0.2 * hrand(k, 3)
        if s["kind"] == "gate":
            r = P["BASTION_R_GATE"]
        cxy = s["xy"] + s["out"] * (0.55 * r)
        if s["kind"] == "gate":
            nm = "SD_Bastion_Gate_" + ("South" if gi == 0 else "North"); gi += 1
        else:
            nm = f"SD_Bastion_{k + 1:02d}"
        me = bastion_mesh(nm, r, 0.0, TOP + (0.6 if s["kind"] == "gate" else 0.0), P["BATTER"])
        o = bpy.data.objects.new(nm, me)
        o.location = (cxy.x, cxy.y, 0)
        o["kind"] = s["kind"]; o["radius_m"] = round(r, 2); o["trace_pos_m"] = round(s["s"], 1)
        o["out_deg"] = round(math.degrees(math.atan2(s["out"].y, s["out"].x)), 1)
        cb.objects.link(o)
        centers.append((cxy, r))

    # ---------- parapet ring + merlons ----------
    PH, PT, MW, MG, MH = P["PARAPET_H"], P["PARAPET_T"], P["MERLON_W"], P["MERLON_GAP"], P["MERLON_H"]
    pin = offset(pts, PT)
    mb = MB()
    po = [mb.add_v((x, y, TOP)) for x, y in pts]
    pot = [mb.add_v((x, y, TOP + PH)) for x, y in pts]
    pit = [mb.add_v((x, y, TOP + PH)) for x, y in pin]
    pib = [mb.add_v((x, y, TOP)) for x, y in pin]
    for i in range(n):
        j = (i + 1) % n
        mb.face([po[i], po[j], pot[j], pot[i]])
        mb.face([pot[i], pot[j], pit[j], pit[i]])
        mb.face([pit[i], pit[j], pib[j], pib[i]])
    nrm = seg_normals(pts)
    merlons = 0
    for i in range(n):
        a = Vector(pts[i]); b = Vector(pts[(i + 1) % n]); L = (b - a).length
        t = (b - a) / L; nn = nrm[i]
        s = 1.2
        while s + MW < L - 1.2:
            mid = a + t * (s + MW / 2) + nn * (PT / 2)
            if all((mid - cc).length > rr + 1.0 for cc, rr in centers):
                ang = math.atan2(t.y, t.x)
                mb.box(mid.x, mid.y, TOP + PH, MW, PT, MH, 0, ang)
                merlons += 1
            s += MW + MG
    mb.make("SD_Wall_Parapet", ["SD_Stone_Parapet"], c)

    # ---------- stairs (one shared mesh, linked duplicates) ----------
    steps = 34; rise = H / steps; tread = 0.30; width = 1.6
    prof = [(0.0, 0.0)]
    for k in range(steps):
        prof += [(k * tread, (k + 1) * rise), ((k + 1) * tread, (k + 1) * rise)]
    prof.append((steps * tread, 0.0))
    run = steps * tread
    sm = bpy.data.meshes.get("SD_Stair_Flight_mesh")
    if sm is not None:
        bpy.data.meshes.remove(sm)
    mbs = MB()
    a_ = [mbs.add_v((x, 0.0, z)) for x, z in prof]
    b_ = [mbs.add_v((x, width, z)) for x, z in prof]
    m_ = len(prof)
    mbs.face(list(reversed(a_)), 0)       # wall-side face
    mbs.face(b_, 0)                      # open side
    for k in range(m_):
        j = (k + 1) % m_
        mbs.face([a_[k], a_[j], b_[j], b_[k]], 1 if prof[k][1] == prof[j][1] and prof[k][1] > 0 else 0)
    proto = mbs.make("SD_Stair_Flight_proto", ["SD_Stone_Wall_Inner", "SD_Stone_Walkway"], cs)
    proto.data.name = "SD_Stair_Flight_mesh"
    shared = proto.data
    bpy.data.objects.remove(proto, do_unlink=True)
    gate_segs = set(range(gate[0] - 1, gate[-1] + 1))
    stairs = 0
    for i in range(n):
        if i in gate_segs or i % 2:
            continue
        a = Vector(inner[i]); b = Vector(inner[(i + 1) % n]); L = (b - a).length
        if L < run + 8:
            continue
        t = (b - a) / L
        p = a + t * ((L - run) / 2)
        if any((p - cc).length < rr + 2 for cc, rr in centers) and any((p + t * run - cc).length < rr + 2 for cc, rr in centers):
            continue
        o = bpy.data.objects.new(f"SD_Wall_Stair_{stairs + 1:02d}", shared)
        o.location = (p.x, p.y, GZ); o.rotation_euler = (0, 0, math.atan2(t.y, t.x))
        cs.objects.link(o); stairs += 1

    return {"wall_trace_m": round(cum[-1], 1), "bastions": len(sites), "merlons": merlons, "stairs": stairs,
            "kinds": {k: sum(1 for s in sites if s["kind"] == k) for k in ("salient", "face", "gate")}}
