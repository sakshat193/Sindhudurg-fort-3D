# sd_terrain.py - Kurte island rock shelf, reef rocks, Ranichi Vela beach, sea, Padmagad islet.


def offset_var(pts, ds, max_miter=2.5):
    """offset() with a per-vertex distance (negative = outward for a CCW polygon)."""
    nrm = seg_normals(pts); res = []
    for i in range(len(pts)):
        m = nrm[i - 1] + nrm[i]
        m = nrm[i].copy() if m.length < 1e-6 else m.normalized()
        k = max(m.dot(nrm[i]), 1.0 / max_miter)
        p = Vector(pts[i]) + m * (ds[i] / k)
        res.append((p.x, p.y))
    return res


def rock_blob(mb, cx, cy, cz, r, seed, mi=0, flat=0.55):
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=1, radius=1.0)
    vmap = {}
    for k, v in enumerate(bm.verts):
        j = 0.7 + 0.6 * hrand(seed * 31 + k, 5)
        co = Vector((v.co.x * j, v.co.y * j * (0.8 + 0.4 * hrand(seed, 7)), v.co.z * j * flat))
        vmap[v.index] = mb.add_v((cx + co.x * r, cy + co.y * r, cz + co.z * r))
    for f in bm.faces:
        mb.face([vmap[v.index] for v in f.verts], mi)
    bm.free()


def build_terrain():
    pts, gate, beach = read_outline()
    c = sub("SD_40_Terrain_Sea"); clear(c)
    n = len(pts)
    Z0 = P["FOOT_Z"]
    ring0 = offset(pts, -(P["BATTER"] + 0.4))
    d1 = [-(P["BATTER"] + 4.0 + 6.0 * hrand(i, 51)) for i in range(n)]
    d2 = [-(P["BATTER"] + 12.0 + 20.0 * hrand(i, 53)) for i in range(n)]
    d3 = [x - 22.0 for x in d2]
    rings = [ring0, offset_var(pts, d1), offset_var(pts, d2), offset_var(pts, d3, 2.0)]
    # the gate notch: bridge the outer rings straight across from salient A to salient B
    gA, gN, gD, gB = gate
    for r in rings[1:]:
        A_, B_ = Vector(r[gA]), Vector(r[gB])
        r[gN] = tuple(A_ + (B_ - A_) * 0.33); r[gD] = tuple(A_ + (B_ - A_) * 0.66)
    zs = [Z0 + 0.05, None, -1.6, -5.0]
    mb = MB(); idx = []
    for k, r in enumerate(rings):
        row = []
        for i, (x, y) in enumerate(r):
            z = zs[k] if zs[k] is not None else 0.05 + 0.45 * hrand(i, 57)
            row.append(mb.add_v((x, y, z)))
        idx.append(row)
    for k in range(3):
        for i in range(n):
            j = (i + 1) % n
            mb.face([idx[k][i], idx[k + 1][i], idx[k + 1][j], idx[k][j]], 0)
    mb.make("SD_Island_Rock_Shelf", ["SD_Rock_Island"], c)

    # reef / boulders: one object so it textures in a single pass
    mb = MB(); cnt = 0
    cx_ = sum(p[0] for p in pts) / n; cy_ = sum(p[1] for p in pts) / n
    for i in range(n):
        for k in range(3):
            s = i * 3 + k
            a = Vector(rings[1][i]); b = Vector(rings[2][(i + 1) % n])
            q = a + (b - a) * hrand(s, 61)
            q += (q - Vector((cx_, cy_))).normalized() * (6 * hrand(s, 63))
            r = 1.2 + 2.8 * hrand(s, 67)
            rock_blob(mb, q.x, q.y, -0.6 + 0.9 * hrand(s, 69), r, s); cnt += 1
    for s in range(40):                       # reef off the north end (where the Johnston Castle struck)
        x = -60 + 200 * hrand(s, 71); y = 330 + 120 * hrand(s, 73)
        rock_blob(mb, x, y, -0.9 + 0.6 * hrand(s, 75), 1.0 + 3.0 * hrand(s, 77), 1000 + s); cnt += 1
    mb.make("SD_Rocks_Reef", ["SD_Rock_Island"], c)

    # Ranichi Vela - crescent of sand in the south bay, below the postern
    if beach is not None:
        mb = MB()
        ids = [(beach - 1) % n, beach, (beach + 1) % n]
        inner = []
        for f in (0.55, 0.8, 1.0):
            a = Vector(ring0[ids[0]]); b = Vector(ring0[ids[1]]); inner.append(a + (b - a) * f)
        for f in (0.2, 0.45):
            a = Vector(ring0[ids[1]]); b = Vector(ring0[ids[2]]); inner.append(a + (b - a) * f)
        outer = []
        for f in (0.55, 0.8, 1.0):
            a = Vector(rings[2][ids[0]]); b = Vector(rings[2][ids[1]]); outer.append(a + (b - a) * f)
        for f in (0.2, 0.45):
            a = Vector(rings[2][ids[1]]); b = Vector(rings[2][ids[2]]); outer.append(a + (b - a) * f)
        iv = [mb.add_v((p.x, p.y, Z0 + 0.15)) for p in inner]
        mv = [mb.add_v(((p.x + q.x) / 2, (p.y + q.y) / 2, 0.55)) for p, q in zip(inner, outer)]
        ov = [mb.add_v((q.x, q.y, -1.45)) for q in outer]
        for row_a, row_b in ((iv, mv), (mv, ov)):
            for k in range(len(row_a) - 1):
                f = [row_a[k], row_b[k], row_b[k + 1], row_a[k + 1]]
                mb.face(f, 0)
        o = mb.make("SD_Beach_RanichiVela", ["SD_Sand"], c)
        bm = bmesh.new(); bm.from_mesh(o.data)
        for f in bm.faces:
            if f.normal.z < 0:
                f.normal_flip()
        bm.to_mesh(o.data); bm.free()

    # sea
    S = 2500.0
    build("SD_Sea", [(-S, -S, 0), (S, -S, 0), (S, S, 0), (-S, S, 0)], [(0, 1, 2, 3)], ["SD_Water_Sea"], None, c)

    # Padmagad - the smaller island towards the Malvan shore (shipyard; now mostly ruin). Position indicative.
    px, py = 560.0, -80.0
    mb = MB(); seg = 14
    top = [(px + (38 + 10 * hrand(k, 81)) * math.cos(2 * math.pi * k / seg), py + (30 + 8 * hrand(k, 83)) * math.sin(2 * math.pi * k / seg)) for k in range(seg)]
    bot = [(px + (x - px) * 1.5, py + (y - py) * 1.5) for x, y in top]
    t_ = [mb.add_v((x, y, 1.2 + 0.5 * hrand(k, 85))) for k, (x, y) in enumerate(top)]
    b_ = [mb.add_v((x, y, -1.8)) for x, y in bot]
    for k in range(seg):
        j = (k + 1) % seg
        mb.face([t_[k], b_[k], b_[j], t_[j]], 0)
    mb.face(t_, 0)
    mb.make("SD_Padmagad_Islet", ["SD_Rock_Island"], c)
    mb = MB()
    for k in range(seg):
        if k % 4 == 3:
            continue
        a = Vector(top[k]); b = Vector(top[(k + 1) % seg])
        a = Vector((px, py)) + (a - Vector((px, py))) * 0.8; b = Vector((px, py)) + (b - Vector((px, py))) * 0.8
        m_ = (a + b) / 2; L = (b - a).length
        mb.box(m_.x, m_.y, 1.2, L, 1.5, 0.6 + 1.6 * hrand(k, 87), 0, math.atan2((b - a).y, (b - a).x))
    mb.make("SD_Padmagad_Ruins", ["SD_Stone_Ruin"], c)
    return {"rocks": cnt, "beach": beach is not None}
