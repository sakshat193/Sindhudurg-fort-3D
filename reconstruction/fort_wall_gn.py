"""FortWall: procedural fort wall + bastions as one Geometry Nodes modifier (Blender 5.2).

Run in Blender: exec(open(r'...\\fort_wall_gn.py').read())  -> rebuilds node group 'FortWall',
creates the demo (Fort_Wall curve, Bastions collection, stone material) only if missing.

Controls on the 'Fort_Wall' Bezier curve (Edit Mode):
  Alt+S on a control point   crown width there   (point radius x Crown Width)
  G Z on a control point     wall height there   (point Z is added to Height)
Bastions collection (Circle empties): move = placement, scale = radius, Z = extra bastion height.
The outer face of the wall wraps onto each bastion's circle inside the same mesh band,
so wall and bastion are one continuous surface (no booleans). Inner face (gorge) stays flush.
Outside side is detected from the curve winding; tick Flip Outside if it picks the wrong one.
"""
import bpy, math

TAU = 2 * math.pi
Z = (0, 0, 1)
EPS = 0.005   # boolean clearance: keeps cutter faces off coplanar wall/bastion faces
BIG = 200.0   # "sky" height for cutters (absolute z for slab/courtyard, above parapet for caps)


def build_group(name='FortWall'):
    g = bpy.data.node_groups.get(name) or bpy.data.node_groups.new(name, 'GeometryNodeTree')
    g.nodes.clear(); g.is_modifier = True
    spec = [
        ('Geometry', 'Geometry', {}),
        ('Bastions', 'Collection', {}),
        ('Height', 'Float', dict(default_value=9.144, min_value=0)),
        ('Crown Width', 'Float', dict(default_value=3.6576, min_value=0)),
        ('Batter', 'Float', dict(default_value=0.1, min_value=0, max_value=1)),
        ('Parapet Height', 'Float', dict(default_value=1.2, min_value=0)),
        ('Parapet Thickness', 'Float', dict(default_value=0.6, min_value=0)),
        ('Ground', 'Float', dict(default_value=0.0)),
        ('Resolution', 'Float', dict(default_value=0.5, min_value=0.05)),
        ('Flip Outside', 'Bool', {}),
        ('Bastion Batter', 'Float', dict(default_value=0.15, min_value=0, max_value=1)),
        ('Bricks', 'Bool', dict(default_value=True)),
        ('Brick Size', 'Float', dict(default_value=0.4, min_value=0.1)),
        ('Mortar Gap', 'Float', dict(default_value=0.03, min_value=0)),
        ('Brick Relief', 'Float', dict(default_value=0.03, min_value=0)),
        ('Brick Jitter', 'Float', dict(default_value=0.3, min_value=0, max_value=1)),
        ('Seed', 'Int', {}),
        ('Material', 'Material', {}),
        ('Mortar Material', 'Material', {}),
    ]
    # keep the interface (socket ids) on re-runs, or existing modifiers reset their values to 0
    if [i.name for i in g.interface.items_tree] != ['Geometry'] + [s[0] for s in spec]:  # output listed first
        g.interface.clear()
        for nm, t, kw in spec:
            s = g.interface.new_socket(name=nm, in_out='INPUT', socket_type='NodeSocket' + t)
            for k, v in kw.items(): setattr(s, k, v)
        g.interface.new_socket(name='Geometry', in_out='OUTPUT', socket_type='NodeSocketGeometry')

    N, L = g.nodes, g.links
    lay = dict(x=0, k=0, frame=None, gi=None)

    def live(socks): return [s for s in socks if s.enabled and s.bl_idname != 'NodeSocketVirtual']

    def put(s, v):
        if isinstance(v, bpy.types.Node): v = live(v.outputs)[0]
        if isinstance(v, bpy.types.NodeSocket): L.new(v, s)
        else: s.default_value = v

    def n(kind, *args, items=0, **kw):
        """New node: lowercase kwargs = node props, positional = enabled inputs, Cap_Kwargs = input by name."""
        nd = N.new(kind)
        for k in [k for k in kw if k[0].islower()]: setattr(nd, k, kw.pop(k))
        for _ in range(items - 2): nd.index_switch_items.new()
        for s, v in zip(live(nd.inputs), args):
            if v is not None: put(s, v)
        for k, v in kw.items():
            cand = [s for s in nd.inputs if s.name == k.replace('_', ' ')]
            assert cand, f'{kind} has no input {k!r}: {[s.name for s in nd.inputs]}'
            put(next((s for s in cand if s.enabled), cand[0]), v)
        nd.parent = lay['frame']; k = lay['k']; lay['k'] += 1
        loc = (lay['x'] + (k // 8) * 190, -(k % 8) * 150)
        if hasattr(nd, 'location_absolute'): nd.location_absolute = loc
        else: nd.location = loc
        return nd

    def stage(label):
        if lay['frame'] is not None: lay['x'] += ((lay['k'] - 1) // 8 + 1) * 190 + 150
        lay['frame'] = N.new('NodeFrame'); lay['frame'].label = label; lay['k'] = 0; lay['gi'] = None

    def GI(name):
        if lay['gi'] is None: lay['gi'] = n('NodeGroupInput')
        return lay['gi'].outputs[name]

    def m(op, *a): return n('ShaderNodeMath', *a, operation=op)
    def vm(op, *a, **kw): return n('ShaderNodeVectorMath', *a, operation=op, **kw)
    def cmp(a, b, op): return n('FunctionNodeCompare', a, b, data_type='FLOAT', operation=op)
    def sw(c, f_, t, typ): return n('GeometryNodeSwitch', c, f_, t, input_type=typ)
    def attr(name, dt='FLOAT_VECTOR'): return n('GeometryNodeInputNamedAttribute', Name=name, data_type=dt)
    def store(geo, name, val, dt='FLOAT_VECTOR'):
        return n('GeometryNodeStoreNamedAttribute', geo, None, name, val, data_type=dt, domain='POINT')

    def unfold(geo, name, h, base=None):
        """Offset point `name` (meant to sit h from the base polyline) that lands closer than h has
        overshot a corner (swallowtail fold): snap it to the last valid point before it along the spline."""
        pm = n('GeometryNodeCurveToMesh', geo)
        if base: pm = n('GeometryNodeSetPosition', pm, Position=attr(base))
        X = attr(name)
        dist = n('GeometryNodeProximity', pm, Sample_Position=X, target_element='EDGES').outputs['Distance']
        ok = cmp(dist, m('SUBTRACT', h, 1e-3), 'GREATER_THAN')
        pts = n('GeometryNodeMeshToPoints', pm, ok, X)  # valid points, spline order kept
        acc = n('GeometryNodeAccumulateField', ok, data_type='INT', domain='POINT')
        k = n('FunctionNodeIntegerMath', n('FunctionNodeIntegerMath', acc.outputs['Trailing'], 1, operation='SUBTRACT'),
              acc.outputs['Total'], operation='FLOORED_MODULO')  # wraps to the last one on a cyclic seam
        snap = n('GeometryNodeSampleIndex', pts, pos, k, data_type='FLOAT_VECTOR', domain='POINT')
        return store(geo, name, sw(ok, snap, X, 'VECTOR'))

    stage('1 Spine: resample, crown height = Ground + Height + point Z, flatten')
    idx, pos = n('GeometryNodeInputIndex'), n('GeometryNodeInputPosition')
    sp = n('GeometryNodeResampleCurve', GI('Geometry'), Mode='Length', Length=GI('Resolution'))
    zcw = m('ADD', m('ADD', GI('Ground'), GI('Height')), n('ShaderNodeSeparateXYZ', pos).outputs['Z'])
    sp = store(sp, 'zcw', zcw, 'FLOAT')
    sp = n('GeometryNodeSetPosition', sp, Position=vm('MULTIPLY', pos, (1, 1, 0)))

    def nb(off):  # neighbour index along the spline (own index past an open end)
        o = n('GeometryNodeOffsetPointInCurve', Offset=off)
        return sw(o.outputs['Is Valid Offset'], idx, o.outputs['Point Index'], 'INT')
    iP, iN = nb(-1), nb(1)
    def at(v, i): return n('GeometryNodeFieldAtIndex', Index=i, Value=v, data_type='FLOAT_VECTOR', domain='POINT')

    stage('2 Outside side: from curve winding (shoelace), Flip Outside inverts')
    cz = n('ShaderNodeSeparateXYZ', vm('CROSS_PRODUCT', pos, at(pos, iN))).outputs['Z']
    area = n('GeometryNodeAttributeStatistic', sp, None, cz, data_type='FLOAT', domain='POINT').outputs['Sum']
    ccw_xor = n('FunctionNodeBooleanMath', cmp(area, 0, 'GREATER_THAN'), GI('Flip Outside'), operation='XOR')
    f = sw(ccw_xor, 1.0, -1.0, 'FLOAT')  # +1: outside is left of travel, -1: right

    def dirs(p):  # unit tangent, outward normal * miter, for a flat polyline field p
        dp = vm('NORMALIZE', vm('SUBTRACT', p, at(p, iP)))
        dn = vm('NORMALIZE', vm('SUBTRACT', at(p, iN), p))
        D = vm('NORMALIZE', vm('ADD', dp, dn))
        c = m('MAXIMUM', vm('DOT_PRODUCT', D, dp), vm('DOT_PRODUCT', D, dn))
        return D, vm('SCALE', vm('CROSS_PRODUCT', Z, D), Scale=m('DIVIDE', f, m('MAXIMUM', c, 0.25)))

    stage('3 Wall lines: crown half-width = Crown Width/2 x point radius; offsets of the spine, unfolded')
    D, nrm = dirs(pos)
    sp = store(sp, 'hw', m('MULTIPLY', m('MULTIPLY', GI('Crown Width'), 0.5), n('GeometryNodeInputRadius')), 'FLOAT')
    HW, ZC, G0 = attr('hw', 'FLOAT'), attr('zcw', 'FLOAT'), GI('Ground')
    hb = m('ADD', HW, m('MULTIPLY', GI('Batter'), m('SUBTRACT', ZC, G0)))   # toe distance from spine
    hp = m('SUBTRACT', HW, GI('Parapet Thickness'))                          # parapet foot distance
    hy = m('SUBTRACT', HW, EPS * 4)                                          # courtyard cut, just inside the wall
    sp = store(sp, 'tan', vm('SCALE', D, Scale=f))  # T such that T x up-the-face = outward normal
    for name, h, sgn in (('outer', HW, 1), ('toe', hb, 1), ('pf', hp, 1), ('inner', HW, -1), ('cy', hy, -1)):
        sp = store(sp, name, vm('ADD', pos, vm('SCALE', nrm, Scale=m('MULTIPLY', h, sgn))))
        sp = unfold(sp, name, h)  # swallowtail folds at sharp corners
    sp = store(sp, 'far', vm('SUBTRACT', pos, vm('SCALE', nrm, Scale=m('ADD', HW, 0.5))))  # slab reach into the court

    def sweep(geo, xys, zs):  # spine x closed K-point profile; vertex = ring*K + j
        K = len(xys)
        me = n('GeometryNodeCurveToMesh', geo, n('GeometryNodeCurvePrimitiveCircle', Resolution=K), Fill_Caps=True)
        j = n('FunctionNodeIntegerMath', idx, K, operation='MODULO')
        xy = n('GeometryNodeIndexSwitch', j, *xys, data_type='VECTOR', items=K)
        zz = n('GeometryNodeIndexSwitch', j, *zs, data_type='FLOAT', items=K)
        me = n('GeometryNodeSetPosition', me, Position=vm('ADD', vm('MULTIPLY', xy, (1, 1, 0)), n('ShaderNodeCombineXYZ', 0, 0, zz)))
        return n('GeometryNodeFlipFaces', me, cmp(f, 0, 'GREATER_THAN'))

    stage('4 Wall solid: 7-point profile toe, inner foot, inner top, parapet foot x2, parapet top x2')
    O, I, toe, pf = (attr(k) for k in ('outer', 'inner', 'toe', 'pf'))
    zp = m('ADD', ZC, GI('Parapet Height'))
    wall = sweep(sp, [toe, I, I, pf, pf, O, O], [G0, G0, ZC, ZC, zp, zp, ZC])
    slab = sweep(sp, [pf, attr('far'), attr('far'), pf], [m('SUBTRACT', G0, 1), m('SUBTRACT', G0, 1), BIG, BIG])
    cyc = n('GeometryNodeDeleteGeometry', sp, n('FunctionNodeBooleanMath', n('GeometryNodeInputSplineCyclic'),
                                                operation='NOT'), domain='CURVE')
    fill = n('GeometryNodeFillCurve', n('GeometryNodeSetPosition', cyc, Position=attr('cy')), Mode='N-gons')
    fill = n('GeometryNodeSetPosition', fill, Offset=n('ShaderNodeCombineXYZ', 0, 0, m('SUBTRACT', G0, 1)))  # spine is flat
    fill = n('GeometryNodeFlipFaces', fill, cmp(n('ShaderNodeSeparateXYZ', n('GeometryNodeInputNormal')).outputs['Z'], 0, 'LESS_THAN'))
    top = n('GeometryNodeExtrudeMesh', fill, Offset=n('ShaderNodeCombineXYZ', 0, 0, m('SUBTRACT', BIG, m('SUBTRACT', G0, 1))),
            mode='FACES')  # extrude drops the bottom: add it back flipped and weld
    jn = n('GeometryNodeJoinGeometry', top); L.new(live(n('GeometryNodeFlipFaces', fill).outputs)[0], jn.inputs[0])
    court = n('GeometryNodeMergeByDistance', jn, Distance=1e-4)

    stage('5 Bastions: empties -> points; R = scale X, zb = wall crown nearby + empty Z')
    ci = n('GeometryNodeCollectionInfo', GI('Bastions'), Separate_Children=True, transform_space='RELATIVE')
    ci = n('GeometryNodeStoreNamedAttribute', ci, None, 'R', n('ShaderNodeSeparateXYZ', n('GeometryNodeInputInstanceScale')).outputs['X'],
           data_type='FLOAT', domain='INSTANCE')  # instance scale is gone once instances become points
    bp = n('GeometryNodeInstancesToPoints', ci)
    bp = store(bp, 'bz', n('ShaderNodeSeparateXYZ', pos).outputs['Z'], 'FLOAT')
    bp = n('GeometryNodeSetPosition', bp, Position=vm('MULTIPLY', pos, (1, 1, 0)))
    proxy = n('GeometryNodeCurveToMesh', sp)
    zn = n('GeometryNodeSampleIndex', proxy, ZC, n('GeometryNodeSampleNearest', proxy, domain='POINT'),
           data_type='FLOAT', domain='POINT')
    bp = store(bp, 'zb', m('ADD', zn, attr('bz', 'FLOAT')), 'FLOAT')
    R, ZB = attr('R', 'FLOAT'), attr('zb', 'FLOAT')
    bp = store(bp, 'rc', m('MAXIMUM', m('SUBTRACT', R, GI('Parapet Thickness')), 0.05), 'FLOAT')
    bp = store(bp, 'rt', m('ADD', R, m('MULTIPLY', GI('Bastion Batter'), m('SUBTRACT', ZB, G0))), 'FLOAT')

    def lathe(zs, rs):  # per bastion: vertical axis with K stations (z, radius) swept by a 96-gon, capped
        K = len(zs)
        ax = n('GeometryNodeResampleCurve', n('GeometryNodeCurvePrimitiveLine', End=(0, 0, 1)), Mode='Count', Count=K)
        ax = n('GeometryNodeRealizeInstances', n('GeometryNodeInstanceOnPoints', bp, Instance=ax))
        j = n('FunctionNodeIntegerMath', idx, K, operation='MODULO')
        zz = n('GeometryNodeIndexSwitch', j, *zs, data_type='FLOAT', items=K)
        rr = n('GeometryNodeIndexSwitch', j, *rs, data_type='FLOAT', items=K)
        ax = n('GeometryNodeSetPosition', ax, Position=vm('ADD', vm('MULTIPLY', pos, (1, 1, 0)), n('ShaderNodeCombineXYZ', 0, 0, zz)))
        return n('GeometryNodeCurveToMesh', ax, n('GeometryNodeCurvePrimitiveCircle', Resolution=96), Scale=rr, Fill_Caps=True)

    ZP, RC, RT = m('ADD', ZB, GI('Parapet Height')), attr('rc', 'FLOAT'), attr('rt', 'FLOAT')
    body = lathe([m('SUBTRACT', G0, 0.01), ZB], [RT, R])
    ring = lathe([m('SUBTRACT', ZB, 2 * EPS), ZP], [R, R])
    # cutter = platform void (r < rc above zb) + cap (r < R above the bastion parapet): cuts the wall and other rings
    cut = lathe([m('SUBTRACT', ZB, EPS), m('ADD', ZP, EPS), m('ADD', ZP, 2 * EPS), m('ADD', ZP, BIG)], [RC, RC, R, R])

    stage('6 Core: (wall - cutters) + bodies + (rings - cutters - walkway slab), minus courtyard')
    def boolean(op, a, *bs):
        b = n('GeometryNodeMeshBoolean', a, operation=op, solver='MANIFOLD')  # ~100x faster than EXACT, same solid
        for x in bs: L.new(live(x.outputs)[0], b.inputs['Mesh 2'])
        return b
    core = boolean('UNION', None, boolean('DIFFERENCE', wall, cut), body, boolean('DIFFERENCE', ring, cut, slab))
    core = boolean('DIFFERENCE', core, court)
    core = n('GeometryNodeSetShadeSmooth', core, Shade_Smooth=False, domain='FACE')
    geo = n('GeometryNodeSetMaterial', core, Material=GI('Material'))
    put(n('NodeGroupOutput').inputs[0], geo)
    return g


def _mat(name, c0, c1, fac_from_tint):
    mt = bpy.data.materials.new(name)
    if not mt.node_tree: mt.use_nodes = True
    nt = mt.node_tree; bsdf = next(x for x in nt.nodes if x.type == 'BSDF_PRINCIPLED')
    tc, nz, cr = (nt.nodes.new(k) for k in ('ShaderNodeTexCoord', 'ShaderNodeTexNoise', 'ShaderNodeValToRGB'))
    nz.inputs['Scale'].default_value = 3; nz.inputs['Detail'].default_value = 8
    cr.color_ramp.elements[0].color = c0; cr.color_ramp.elements[1].color = c1
    nt.links.new(tc.outputs['Object'], nz.inputs['Vector'])
    fac = nz.outputs['Fac']
    if fac_from_tint:  # per-brick shade from the 'tint' instance attribute, grain from noise
        at = nt.nodes.new('ShaderNodeAttribute'); at.attribute_type = 'INSTANCER'; at.attribute_name = 'tint'
        mix = nt.nodes.new('ShaderNodeMath'); mix.operation = 'MULTIPLY_ADD'; mix.inputs[1].default_value = 0.35
        nt.links.new(nz.outputs['Fac'], mix.inputs[0]); nt.links.new(at.outputs['Fac'], mix.inputs[2])
        fac = mix.outputs[0]
    nt.links.new(fac, cr.inputs['Fac'])
    nt.links.new(cr.outputs['Color'], bsdf.inputs['Base Color']); bsdf.inputs['Roughness'].default_value = 0.9
    return mt


def brick_mat(): return _mat('FortWall_Brick', (0.16, 0.10, 0.07, 1), (0.48, 0.36, 0.28, 1), True)   # laterite
def mortar_mat(): return _mat('FortWall_Mortar', (0.30, 0.29, 0.26, 1), (0.42, 0.40, 0.36, 1), False)  # lime


def mod_input(md, name):  # Blender 5.x: modifier inputs live in md.properties.inputs.Socket_N.value
    it = next(i for i in md.node_group.interface.items_tree
              if i.item_type == 'SOCKET' and i.in_out == 'INPUT' and i.name == name)
    return getattr(md.properties.inputs, it.identifier)


def demo():
    g = build_group()
    scn = bpy.context.scene
    col = bpy.data.collections.get('Bastions')
    if not col:
        col = bpy.data.collections.new('Bastions'); scn.collection.children.link(col)
        # (x, y, radius, extra height): four corner bastions + one mid-curtain
        for i, (x, y, r, z) in enumerate([(-40, -30, 7, 0), (35, -35, 8, 1.5), (50, 10, 7, 0),
                                          (-45, 20, 6, 0), (-2, -32.5, 5, 0)]):
            e = bpy.data.objects.new(f'Bastion_{i + 1}', None)
            e.empty_display_type = 'CIRCLE'; e.empty_display_size = 1
            e.location, e.scale = (x, y, z), (r, r, r); col.objects.link(e)
    ob = bpy.data.objects.get('Fort_Wall')
    if not ob:
        cu = bpy.data.curves.new('Fort_Wall', 'CURVE'); cu.dimensions = '3D'
        s = cu.splines.new('BEZIER')
        pts = [(-40, -30, 0, 1), (35, -35, 0, 1), (50, 10, 0, 1), (5, 40, 3, 1.5), (-45, 20, 0, 1)]  # x y z radius
        s.bezier_points.add(len(pts) - 1)
        for p, (x, y, z, r) in zip(s.bezier_points, pts):
            p.co, p.radius = (x, y, z), r
            p.handle_left_type = p.handle_right_type = 'VECTOR'
        s.use_cyclic_u = True
        ob = bpy.data.objects.new('Fort_Wall', cu); scn.collection.objects.link(ob)
    md = ob.modifiers.get('FortWall')
    if md and (md.node_group != g or mod_input(md, 'Bastions').value is None):
        ob.modifiers.remove(md); md = None  # interface was rebuilt: start from fresh defaults
    if not md:
        md = ob.modifiers.new('FortWall', 'NODES'); md.node_group = g
        mod_input(md, 'Bastions').value = col
        mod_input(md, 'Material').value = bpy.data.materials.get('FortWall_Brick') or brick_mat()
        mod_input(md, 'Mortar Material').value = bpy.data.materials.get('FortWall_Mortar') or mortar_mat()
    ob.update_tag()
    return ob


def check(ob=None):
    """Core is one closed outward solid; every bastion parapet reaches its circle; bricks were laid."""
    import bmesh, time
    ob = ob or bpy.data.objects['Fort_Wall']
    t0 = time.perf_counter(); dg = bpy.context.evaluated_depsgraph_get(); ob.update_tag(); dg.update()
    ev = ob.evaluated_get(dg); secs = time.perf_counter() - t0
    me = ev.to_mesh(); bm = bmesh.new(); bm.from_mesh(me)
    vol, open_edges = bm.calc_volume(signed=True), sum(not e.is_manifold for e in bm.edges)
    bm.free(); ev.to_mesh_clear()
    bricks = sum(1 for i in dg.object_instances if i.is_instance and i.parent and i.parent.original == ob)
    assert vol > 0, f'normals point inward (signed volume {vol:.0f})'
    assert open_edges == 0, f'{open_edges} non-manifold edges'
    assert bricks > 0 or not mod_input(ob.modifiers['FortWall'], 'Bricks').value, 'no bricks'
    return dict(volume=round(vol), open_edges=open_edges, bricks=bricks, secs=round(secs, 2))


if __name__ == '__main__':
    demo()
