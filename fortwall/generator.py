"""FortWall: procedural fort wall + bastions + gates as one Geometry Nodes modifier (Blender 5.2).

Used by the FortWall add-on (fortwall/__init__.py). Standalone: exec(open(r'...\\fortwall\\generator.py').read())
-> rebuilds node group 'FortWall', creates the demo (Fort_Wall curve, Bastions + Gates collections, materials) only if missing.

Controls on the 'Fort_Wall' Bezier curve (Edit Mode):
  Alt+S on a control point   crown width there   (point radius x Crown Width)
  G Z on a control point     wall height there   (point Z is added to Height)
Bastions collection (empties): move = placement, scale = radius, Z = extra bastion height.
Gates collection (empties): snapped across the nearest wall; width = 2 x scale X, height = Gate Height x scale Z.
Stairs collection (empties): a flight along the courtyard face (bends with it), foot at the empty, rising along its X axis,
  width = scale X; 0.2 m max rise, 0.3 m going, stepped parapet with coping on the open side, end wall at the top;
  set off the true face (winders round corners), brick + mortar sides (treads and coping laterite).
Walkway runs level with each bastion platform where it meets it, ramping up or down to its crown over Ramp Run; a low
rail lines its courtyard edge (gaps at stair tops and ladders). Each bastion gets a ladder up its courtyard face.
Flag Chance plants flagpoles on platforms and the walkway (Flagpole Height, Wood / Flag Material).
Merlons: crenels cut at random spacing (Merlon Spacing, Merlon Randomness, Crenel Width, Merlon Height; 0 = none).
Core solid = (wall - bastion cylinders - crenels) + bastion bodies + (rings - cutters - walkway slab - crenels)
             - courtyard - gates (Manifold booleans). Bricks: Bricks toggle, Brick Size, Mortar Gap,
Brick Relief, Brick Jitter, Seed; the core shows between them as mortar (Mortar Material).
Outside side is detected from the curve winding; tick Flip Outside if it picks the wrong one.
"""
import bpy, hashlib, inspect, math
from pathlib import Path

_file = globals().get('__file__')  # unset when exec()'d
ASSET = Path(_file).with_name('fortwall_nodes.blend') if _file else None  # prebuilt group, written by bake()
TAU = 2 * math.pi
Z = (0, 0, 1)
EPS = 0.005   # boolean clearance: keeps cutter faces off coplanar wall/bastion faces
BIG = 200.0   # "sky" height for cutters (absolute z for slab/courtyard, above parapet for caps)
RAIL_T, RAIL_H = 0.4, 0.7   # low inner parapet on the courtyard edge of the walkway: thickness, height
PARTS = ('Bastions', 'Gates', 'Stairs')  # collection inputs: one empty per part
PANELS = (  # modifier and sidebar grouping of the inputs
    ('Wall', ('Height', 'Crown Width', 'Batter', 'Ground', 'Parapet Height', 'Parapet Thickness', 'Resolution', 'Flip Outside')),
    ('Bastions, Gates, Stairs', ('Bastions', 'Bastion Batter', 'Gates', 'Gate Height', 'Stairs', 'Ramp Run')),
    ('Merlons', ('Merlon Height', 'Merlon Spacing', 'Merlon Randomness', 'Crenel Width')),
    ('Bricks', ('Bricks', 'Brick Size', 'Mortar Gap', 'Brick Relief', 'Brick Jitter', 'Seed')),
    ('Flags & Materials', ('Flag Chance', 'Flagpole Height', 'Material', 'Mortar Material', 'Wood Material', 'Flag Material')),
)


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
        ('Gates', 'Collection', {}),
        ('Gate Height', 'Float', dict(default_value=4.5, min_value=0)),
        ('Merlon Height', 'Float', dict(default_value=0.6, min_value=0)),
        ('Merlon Spacing', 'Float', dict(default_value=2.0, min_value=0.5)),
        ('Merlon Randomness', 'Float', dict(default_value=0.7, min_value=0, max_value=1)),
        ('Crenel Width', 'Float', dict(default_value=0.6, min_value=0.1)),
        ('Bricks', 'Bool', dict(default_value=True)),
        ('Brick Size', 'Float', dict(default_value=0.4, min_value=0.1)),
        ('Mortar Gap', 'Float', dict(default_value=0.03, min_value=0)),
        ('Brick Relief', 'Float', dict(default_value=0.03, min_value=0)),
        ('Brick Jitter', 'Float', dict(default_value=0.3, min_value=0, max_value=1)),
        ('Seed', 'Int', {}),
        ('Material', 'Material', {}),
        ('Mortar Material', 'Material', {}),
        ('Stairs', 'Collection', {}),
        ('Ramp Run', 'Float', dict(default_value=3.0, min_value=0.5)),
        ('Flag Chance', 'Float', dict(default_value=0.35, min_value=0, max_value=1)),
        ('Flagpole Height', 'Float', dict(default_value=6.0, min_value=0.5)),
        ('Wood Material', 'Material', {}),
        ('Flag Material', 'Material', {}),
    ]
    # keep the interface (socket ids) on re-runs, or existing modifiers reset their values to 0
    def inputs(): return {i.name: i for i in g.interface.items_tree if i.item_type == 'SOCKET' and i.in_out == 'INPUT'}
    if sorted(inputs()) != sorted(s[0] for s in spec):  # sorted: panels reorder items_tree
        g.interface.clear()
        for nm, t, kw in spec:
            s = g.interface.new_socket(name=nm, in_out='INPUT', socket_type='NodeSocket' + t)
            for k, v in kw.items(): setattr(s, k, v)
        g.interface.new_socket(name='Geometry', in_out='OUTPUT', socket_type='NodeSocketGeometry')
    # modifier panels: moving a socket into a panel keeps its id, so existing modifier values survive
    socks = inputs()
    for title, names in PANELS:
        p = next((i for i in g.interface.items_tree if i.item_type == 'PANEL' and i.name == title), None) \
            or g.interface.new_panel(title, default_closed=title != PANELS[0][0])
        for nm in names:
            if socks[nm].parent != p: g.interface.move_to_parent(socks[nm], p, len(p.interface_items))

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
    def v3(xy, z): return vm('ADD', vm('MULTIPLY', xy, (1, 1, 0)), n('ShaderNodeCombineXYZ', 0, 0, z))
    def mx(geo, v): return n('GeometryNodeAttributeStatistic', geo, None, v, data_type='FLOAT', domain='POINT').outputs['Max']
    def join(*gs):
        j = n('GeometryNodeJoinGeometry')
        for x in gs: put(j.inputs[0], x)
        return j
    def AND(*a):
        x = a[0]
        for b in a[1:]: x = n('FunctionNodeBooleanMath', x, b, operation='AND')
        return x

    def outward(geo):  # flip every island whose signed volume is negative (mirrored placements)
        v = m('MULTIPLY', n('GeometryNodeInputMeshFaceArea'), vm('DOT_PRODUCT', n('GeometryNodeInputNormal'), pos))
        tot = n('GeometryNodeAccumulateField', v, n('GeometryNodeInputMeshIsland'), data_type='FLOAT', domain='FACE').outputs['Total']
        return n('GeometryNodeFlipFaces', geo, cmp(tot, 0, 'LESS_THAN'))

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
    # the sample nearest each knot moves onto it: a corner stays one sharp point, not a Resolution-long chord across it
    kn = n('GeometryNodeCurveToPoints', n('GeometryNodeCurveSplineType', GI('Geometry'), spline_type='POLY'), mode='EVALUATED')
    kp = n('GeometryNodeSampleIndex', kn, pos, n('GeometryNodeSampleNearest', kn, pos, domain='POINT'), data_type='FLOAT_VECTOR', domain='POINT')
    sp = n('GeometryNodeSetPosition', sp, cmp(vm('DISTANCE', pos, kp), m('MULTIPLY', GI('Resolution'), 0.49), 'LESS_THAN'), kp)
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
    sp = store(sp, 'mdir', nrm)  # miter vector, length 1/cos(half turn)
    HW, ZC, G0 = attr('hw', 'FLOAT'), attr('zcw', 'FLOAT'), GI('Ground')
    hb = m('ADD', HW, m('MULTIPLY', GI('Batter'), m('SUBTRACT', ZC, G0)))   # toe distance from spine
    hp = m('SUBTRACT', HW, GI('Parapet Thickness'))                          # parapet foot distance
    hy = m('SUBTRACT', HW, EPS * 4)                                          # courtyard cut, just inside the wall
    sp = store(sp, 'tan', vm('SCALE', D, Scale=f))  # T such that T x up-the-face = outward normal
    hr = m('SUBTRACT', HW, RAIL_T)                                           # inner rail, courtyard side of the walkway
    for name, h, sgn in (('outer', HW, 1), ('toe', hb, 1), ('pf', hp, 1), ('inner', HW, -1), ('cy', hy, -1), ('rin', hr, -1)):
        sp = store(sp, name, vm('ADD', pos, vm('SCALE', nrm, Scale=m('MULTIPLY', h, sgn))))
        sp = unfold(sp, name, h)  # swallowtail folds at sharp corners
    sp = store(sp, 'far', vm('SUBTRACT', pos, vm('SCALE', nrm, Scale=m('ADD', HW, 0.5))))  # slab reach into the court

    stage('3b Bastion points: R = scale X, zb = wall crown nearby + empty Z; walkway level at platforms, ramped')
    ci = n('GeometryNodeCollectionInfo', GI('Bastions'), Separate_Children=True, transform_space='RELATIVE')
    ci = n('GeometryNodeStoreNamedAttribute', ci, None, 'R', n('ShaderNodeSeparateXYZ', n('GeometryNodeInputInstanceScale')).outputs['X'],
           data_type='FLOAT', domain='INSTANCE')  # instance scale is gone once instances become points
    bp = n('GeometryNodeInstancesToPoints', ci)
    bp = store(bp, 'bz', n('ShaderNodeSeparateXYZ', pos).outputs['Z'], 'FLOAT')
    bp = store(n('GeometryNodeSetPosition', bp, Position=vm('MULTIPLY', pos, (1, 1, 0))), 'ctr', pos)
    proxy = n('GeometryNodeCurveToMesh', sp)
    zn = n('GeometryNodeSampleIndex', proxy, ZC, n('GeometryNodeSampleNearest', proxy, domain='POINT'),
           data_type='FLOAT', domain='POINT')
    bp = store(bp, 'zb', m('ADD', zn, attr('bz', 'FLOAT')), 'FLOAT')
    R, ZB = attr('R', 'FLOAT'), attr('zb', 'FLOAT')
    bp = store(bp, 'rc', m('MAXIMUM', m('SUBTRACT', R, GI('Parapet Thickness')), 0.05), 'FLOAT')
    bp = store(bp, 'rt', m('ADD', R, m('MULTIPLY', GI('Bastion Batter'), m('SUBTRACT', ZB, G0))), 'FLOAT')

    def nbs(v, at_, dt='FLOAT'):  # value at the bastion nearest at_
        return n('GeometryNodeSampleIndex', bp, v, n('GeometryNodeSampleNearest', bp, at_, domain='POINT'), data_type=dt, domain='POINT')
    nb = n('GeometryNodeAttributeDomainSize', bp, component='POINTCLOUD').outputs['Point Count']
    def dcirc(at_):  # at_ to the nearest bastion circle; with none, far away (sampling no points gives 0: a circle at the origin)
        return sw(cmp(nb, 0, 'GREATER_THAN'), 1e6, m('SUBTRACT', vm('DISTANCE', at_, nbs(pos, at_, 'FLOAT_VECTOR')), nbs(R, at_)), 'FLOAT')
    dB = dcirc(pos)  # spine point to the nearest bastion circle
    # level with the platform wherever the section (half-width HW) can touch the circle, one sample further (the crown is
    # linear between samples): no step where the circle crosses the walkway; then up or down to the crown over Ramp Run
    ramp = n('ShaderNodeClamp', m('SUBTRACT', 1, m('DIVIDE', m('SUBTRACT', dB, m('ADD', HW, GI('Resolution'))), GI('Ramp Run'))), 0, 1)
    zbn = nbs(ZB, pos)
    sp = store(sp, 'zcw', sw(cmp(ramp, 1, 'LESS_THAN'), zbn, m('ADD', ZC, m('MULTIPLY', m('SUBTRACT', zbn, ZC), ramp)), 'FLOAT'), 'FLOAT')
    proxy = n('GeometryNodeCurveToMesh', sp)  # ramped crown, for gates and ladders


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

    stage('5 Bastions: lathed body, ring, platform cutters')
    CR = n('ShaderNodeClamp', m('CEIL', m('MULTIPLY', mx(bp, attr('rt', 'FLOAT')), TAU)), 24, 96)  # facets ~1 m at the widest toe
    def lathe(zs, rs):  # per bastion: vertical axis with K stations (z, radius) swept by a CR-gon, capped
        K = len(zs)
        ax = n('GeometryNodeResampleCurve', n('GeometryNodeCurvePrimitiveLine', End=(0, 0, 1)), Mode='Count', Count=K)
        ax = n('GeometryNodeRealizeInstances', n('GeometryNodeInstanceOnPoints', bp, Instance=ax))
        j = n('FunctionNodeIntegerMath', idx, K, operation='MODULO')
        zz = n('GeometryNodeIndexSwitch', j, *zs, data_type='FLOAT', items=K)
        rr = n('GeometryNodeIndexSwitch', j, *rs, data_type='FLOAT', items=K)
        ax = n('GeometryNodeSetPosition', ax, Position=vm('ADD', vm('MULTIPLY', pos, (1, 1, 0)), n('ShaderNodeCombineXYZ', 0, 0, zz)))
        return n('GeometryNodeCurveToMesh', ax, n('GeometryNodeCurvePrimitiveCircle', Resolution=CR), Scale=rr, Fill_Caps=True)

    ZP, RC, RT = m('ADD', ZB, GI('Parapet Height')), attr('rc', 'FLOAT'), attr('rt', 'FLOAT')
    body = lathe([m('SUBTRACT', G0, 0.01), ZB], [RT, R])
    ring = lathe([m('SUBTRACT', ZB, 2 * EPS), ZP], [R, R])
    # cutter = platform void (r < rc above zb) + cap (r < R above the bastion parapet): cuts the wall and other rings
    cut = lathe([m('SUBTRACT', ZB, EPS), m('ADD', ZP, EPS), m('ADD', ZP, 2 * EPS), m('ADD', ZP, BIG)], [RC, RC, R, R])
    # the wall stops at the bastion circle above the platform: every face inside a bastion belongs to it
    wcut = lathe([m('SUBTRACT', ZB, EPS), m('ADD', ZP, BIG)], [m('SUBTRACT', R, EPS)] * 2)

    stage('6 Openings: crenels at random spacing on wall and bastion parapets; arched gates snapped across the wall')
    MH, CW = GI('Merlon Height'), GI('Crenel Width')
    MS = m('MAXIMUM', GI('Merlon Spacing'), m('ADD', CW, 0.2))
    # junctions: a solid pier (no crenel within 0.75 x spacing) where the curtain parapet runs into a bastion ring, so the two
    # parapets never cut each other's merlons; the overlap is one solid at one height (walkway level with the platform there)
    flat = vm('MULTIPLY', pos, (1, 1, 0))
    clear = m('MULTIPLY', MS, 0.75)
    off_bastion = cmp(dcirc(flat), clear, 'GREATER_THAN')
    off_wall = cmp(m('SUBTRACT', n('GeometryNodeProximity', proxy, Sample_Position=flat, target_element='EDGES').outputs['Distance'],
                     n('GeometryNodeSampleIndex', proxy, HW, n('GeometryNodeSampleNearest', proxy, flat, domain='POINT'),
                       data_type='FLOAT', domain='POINT')), clear, 'GREATER_THAN')
    def crenels(cv, ztop, across, sd, keep):  # along cv, the parapet centreline: boxes from ztop - MH up; shift stays under half a gap so boxes never touch
        cp = n('GeometryNodeCurveToPoints', n('GeometryNodeResampleCurve', cv, Mode='Length', Length=MS), mode='EVALUATED')
        cp = store(cp, 'tg', cp.outputs['Tangent']); tg = attr('tg')
        sh = m('MULTIPLY', m('MULTIPLY', m('SUBTRACT', MS, CW), m('MULTIPLY', GI('Merlon Randomness'), 0.45)),
               n('FunctionNodeRandomValue', Min=-1.0, Max=1.0, Seed=m('ADD', GI('Seed'), sd), data_type='FLOAT'))
        cp = n('GeometryNodeSetPosition', cp, Position=v3(vm('ADD', pos, vm('SCALE', tg, Scale=sh)),
                                                         m('ADD', m('SUBTRACT', ztop, MH), m('MULTIPLY', m('ADD', MH, 1), 0.5))))
        box = n('GeometryNodeInstanceOnPoints', cp, AND(cmp(MH, 0, 'GREATER_THAN'), keep), n('GeometryNodeMeshCube'),
                Rotation=n('FunctionNodeAxesToRotation', Z, tg, primary_axis='Z', secondary_axis='X'),
                Scale=n('ShaderNodeCombineXYZ', CW, across, m('ADD', MH, 1)))
        return n('GeometryNodeRealizeInstances', box), cp
    pl = n('GeometryNodeSetPosition', sp, Position=vm('SCALE', vm('ADD', pf, O), Scale=0.5))  # parapet centreline
    # corners turning over ~20 deg keep a solid merlon: no crenel within (Crenel Width + Parapet Thickness) x miter of one
    kc = n('GeometryNodeDeleteGeometry', n('GeometryNodeCurveToPoints', pl, mode='EVALUATED'), cmp(vm('LENGTH', attr('mdir')), 1.0154, 'LESS_THAN'))
    ki = n('GeometryNodeSampleNearest', kc, flat, domain='POINT')
    off_corner = cmp(vm('DISTANCE', flat, n('GeometryNodeSampleIndex', kc, pos, ki, data_type='FLOAT_VECTOR', domain='POINT')),
                     m('MULTIPLY', m('ADD', CW, GI('Parapet Thickness')),
                       n('GeometryNodeSampleIndex', kc, vm('LENGTH', attr('mdir')), ki, data_type='FLOAT', domain='POINT')), 'GREATER_THAN')
    wcren, wcp = crenels(pl, zp, m('ADD', GI('Parapet Thickness'), 0.5), 11, AND(off_bastion, off_corner))
    circ = n('GeometryNodeRealizeInstances', n('GeometryNodeInstanceOnPoints', bp, Instance=n('GeometryNodeCurvePrimitiveCircle', Resolution=CR),
                                                Scale=m('MULTIPLY', m('ADD', R, RC), 0.5)))
    bcren, bcp = crenels(circ, ZP, m('ADD', m('SUBTRACT', R, RC), 0.5), 12, off_wall)

    gc = n('GeometryNodeCollectionInfo', GI('Gates'), Separate_Children=True, transform_space='RELATIVE')
    gc = n('GeometryNodeStoreNamedAttribute', gc, None, 'gs', n('GeometryNodeInputInstanceScale'), data_type='FLOAT_VECTOR', domain='INSTANCE')
    gp = n('GeometryNodeInstancesToPoints', gc)
    ni = n('GeometryNodeSampleNearest', proxy, vm('MULTIPLY', pos, (1, 1, 0)), domain='POINT')
    def gs(v, dt='FLOAT'): return n('GeometryNodeSampleIndex', proxy, v, ni, data_type=dt, domain='POINT')  # nearest spine point
    gsc = n('ShaderNodeSeparateXYZ', attr('gs')); w2 = gsc.outputs['X']
    gp = store(gp, 'tg', gs(attr('tan'), 'FLOAT_VECTOR'))
    gp = n('GeometryNodeSetPosition', gp, Position=v3(gs(pos, 'FLOAT_VECTOR'), m('SUBTRACT', m('ADD', G0, m('MULTIPLY', GI('Gate Height'), gsc.outputs['Z'])), w2)))
    arch = n('GeometryNodeMeshCylinder', Vertices=32, Radius=1, Depth=1)  # lower half pushed underground: round arch, straight jambs
    arch = n('GeometryNodeSetPosition', arch, cmp(n('ShaderNodeSeparateXYZ', pos).outputs['Y'], -1e-4, 'LESS_THAN'), Offset=(0, -60, 0))
    depth = m('ADD', m('MULTIPLY', m('ADD', gs(HW), m('MULTIPLY', GI('Batter'), m('SUBTRACT', gs(ZC), G0))), 2), 2)
    gates = n('GeometryNodeRealizeInstances', n('GeometryNodeInstanceOnPoints', gp, None, arch,
              Rotation=n('FunctionNodeAxesToRotation', Z, gs(attr('tan'), 'FLOAT_VECTOR'), primary_axis='Y', secondary_axis='X'),
              Scale=n('ShaderNodeCombineXYZ', w2, w2, depth)))

    stage('6b Stairs: flight along the courtyard face (bends with it), foot at the empty, toward its X axis; parapet on the open side')
    sc = n('GeometryNodeCollectionInfo', GI('Stairs'), Separate_Children=True, transform_space='RELATIVE')
    sc = n('GeometryNodeStoreNamedAttribute', sc, None, 'sx', n('FunctionNodeRotateVector', n('ShaderNodeCombineXYZ',
           n('ShaderNodeSeparateXYZ', n('GeometryNodeInputInstanceScale')).outputs['X'], 0, 0), n('GeometryNodeInputInstanceRotation')),
           data_type='FLOAT_VECTOR', domain='INSTANCE')
    sq = n('GeometryNodeInstancesToPoints', sc)
    # stations run along the face foot blurred over ~1.4x the widest flight (a sharp corner becomes a bend they wind around),
    # each set off the true face: full width round a corner that juts into the court, where the blurred line runs in the wall
    BK =m('CEIL', m('DIVIDE', m('MULTIPLY', m('POWER', m('MULTIPLY', mx(sq, vm('LENGTH', attr('sx'))), 1.4), 2), 1.5),
                     m('MULTIPLY', GI('Resolution'), GI('Resolution'))))  # blur passes: each adds ~2/3 Resolution^2 of variance
    def blur(v): return n('GeometryNodeBlurAttribute', v, BK, data_type='FLOAT_VECTOR')
    icv = n('GeometryNodeSetPosition', sp, Position=attr('inner'))  # courtyard face foot, exactly as swept ('inner', 'mdir' kept)
    icv = n('GeometryNodeSetPosition', icv, Position=blur(pos))
    icv = store(store(icv, 'aq', n('ShaderNodeCombineXYZ', n('GeometryNodeSplineParameter').outputs['Length'],
                                   n('GeometryNodeSplineLength').outputs['Length'], n('GeometryNodeCurveOfPoint').outputs['Curve Index'])),
                'itg', n('GeometryNodeInputTangent'))
    im = n('GeometryNodeCurveToMesh', icv)
    kq = n('GeometryNodeSampleNearest', im, vm('MULTIPLY', pos, (1, 1, 0)), domain='POINT')
    def iq(v, dt='FLOAT_VECTOR'): return n('GeometryNodeSampleIndex', im, v, kq, data_type=dt, domain='POINT')
    aq, itg = n('ShaderNodeSeparateXYZ', iq(attr('aq'))), iq(attr('itg'))
    RI, GO = 0.2, 0.3  # max rise, going
    sg = sw(cmp(vm('DOT_PRODUCT', attr('sx'), itg), 0, 'LESS_THAN'), 1.0, -1.0, 'FLOAT')
    s0 = m('ADD', aq.outputs['X'], vm('DOT_PRODUCT', vm('SUBTRACT', vm('MULTIPLY', pos, (1, 1, 0)), iq(pos)), itg))  # foot, arc length
    s1 = m('FLOORED_MODULO', m('ADD', s0, m('MULTIPLY', sg, m('MULTIPLY', m('SUBTRACT', iq(ZC, 'FLOAT'), G0), GO / RI))), aq.outputs['Y'])
    zt = n('GeometryNodeSampleCurve', icv, ZC, s1, aq.outputs['Z'], mode='LENGTH', data_type='FLOAT').outputs['Value']  # crown at the top
    sq = store(store(sq, 'ss', n('ShaderNodeCombineXYZ', s0, sg, aq.outputs['Y'])), 'sci', aq.outputs['Z'], 'INT')
    sq = store(sq, 'sh', m('SUBTRACT', zt, m('ADD', G0, 0.01)), 'FLOAT')  # tops out 2 cm under the walkway (no coplanar faces)
    SH = attr('sh', 'FLOAT'); NS = m('CEIL', m('DIVIDE', SH, RI))
    fl0 = fl = n('GeometryNodeRealizeInstances', n('GeometryNodeInstanceOnPoints', sq, Instance=n('GeometryNodeCurvePrimitiveLine')))
    fl = n('GeometryNodeResampleCurve', fl, Mode='Count', Count=m('MULTIPLY', NS, 2))  # two stations per step
    fl = store(fl, 'ri', n('GeometryNodeSplineParameter').outputs['Index'], 'FLOAT')
    fm = n('GeometryNodeCurveToMesh', fl, n('GeometryNodeCurvePrimitiveCircle', Resolution=4), Fill_Caps=True)
    r_ = attr('ri', 'FLOAT'); kk = m('FLOOR', m('DIVIDE', r_, 2))
    tS = sw(cmp(m('SUBTRACT', r_, m('MULTIPLY', kk, 2)), 0.5, 'GREATER_THAN'),  # station: even = riser foot (leans back 1 cm), odd = tread end
            m('ADD', m('MULTIPLY', kk, GO), m('MULTIPLY', m('MINIMUM', kk, 1), 0.01)), m('MULTIPLY', m('ADD', kk, 1), GO), 'FLOAT')
    zS = m('MULTIPLY', m('ADD', kk, 1), m('DIVIDE', SH, NS))  # tread height over the base
    jj = n('FunctionNodeIntegerMath', idx, 4, operation='MODULO')  # profile: 0 wall/low, 1 open/low, 2 open/high, 3 wall/high
    ss, W, B = n('ShaderNodeSeparateXYZ', attr('ss')), vm('LENGTH', attr('sx')), m('SUBTRACT', G0, 0.01)
    ends = m('SUBTRACT', cmp(r_, m('SUBTRACT', m('MULTIPLY', NS, 2), 1.5), 'GREATER_THAN'), cmp(r_, 0.5, 'LESS_THAN'))  # -1 foot, +1 top
    def at_s(v, t):  # value on the blurred face line, t along the flight
        s_ = m('FLOORED_MODULO', m('ADD', ss.outputs['X'], m('MULTIPLY', ss.outputs['Y'], t)), ss.outputs['Z'])
        return n('GeometryNodeSampleCurve', icv, v, s_, attr('sci', 'INT'), mode='LENGTH', data_type='FLOAT_VECTOR')
    def face(t, w):  # point w into the court off the true face foot (miter, as swept), t along the flight; + the mdir sample
        md = at_s(attr('mdir'), t)
        return vm('SUBTRACT', at_s(attr('inner'), t).outputs['Value'], vm('SCALE', md.outputs['Value'], Scale=w)), md
    def flight(w0, w1, zlo, zhi, t):  # every station sampled on the face line: treads and sides stay planar as the flight bends
        op = cmp(m('ABSOLUTE', m('SUBTRACT', jj, 1.5)), 1, 'LESS_THAN')
        return outward(n('GeometryNodeSetPosition', fm, Position=v3(face(t, sw(op, w0, w1, 'FLOAT'))[0],
                                                                    sw(cmp(jj, 1.5, 'GREATER_THAN'), zlo, zhi, 'FLOAT'))))
    PH, top = 0.9, m('ADD', B, zS)  # parapet over the treads; parts overlap by a few cm (no coplanar faces)
    def te(e): return m('ADD', tS, m('MULTIPLY', ends, e))
    E = m('MULTIPLY', NS, GO)  # run
    steps = (flight(-0.15, m('SUBTRACT', W, 0.15), B, top, tS),                                        # body, into the wall (chords at corners)
             flight(m('SUBTRACT', W, 0.3), W, m('SUBTRACT', B, 0.01), m('ADD', top, PH), te(0.02)),     # parapet
             flight(m('SUBTRACT', W, 0.36), m('ADD', W, 0.05), m('ADD', top, PH - 0.08), m('ADD', top, PH + 0.06), te(0.05)),  # coping
             flight(-0.04, m('ADD', W, 0.03), m('SUBTRACT', B, 0.02), m('ADD', m('ADD', B, SH), PH + 0.03),  # end wall past the top tread
                    m('ADD', m('SUBTRACT', E, 0.05), m('MULTIPLY', m('DIVIDE', r_, m('SUBTRACT', m('MULTIPLY', NS, 2), 1)), 0.35))))

    stage('6c Inner rail: low parapet on the courtyard edge of the walkway, gaps at stair tops and ladders; ladder spots')
    # ladder half a radius along the wall from the bastion, square to that face segment (not the corner bisector), topping
    # out at the local crown, 0.15 m off the face
    cnt = n('GeometryNodeAttributeDomainSize', proxy, component='MESH').outputs['Point Count']
    def wrap(i): return n('FunctionNodeIntegerMath', i, cnt, operation='FLOORED_MODULO')
    jn = wrap(n('FunctionNodeIntegerMath', n('GeometryNodeSampleNearest', proxy, pos, domain='POINT'),
                m('ROUND', m('DIVIDE', m('MULTIPLY', R, 0.5), GI('Resolution'))), operation='ADD'))
    jn1 = wrap(n('FunctionNodeIntegerMath', jn, 1, operation='ADD'))
    def ps(v, i, dt='FLOAT_VECTOR'): return n('GeometryNodeSampleIndex', proxy, v, i, data_type=dt, domain='POINT')
    I0, I1 = ps(I, jn), ps(I, jn1)
    lt = vm('NORMALIZE', vm('MULTIPLY', vm('SUBTRACT', I1, I0), (1, 1, 0)))  # ponytail: a segment snapped to zero length at a fold has no direction
    m0 = vm('NORMALIZE', ps(attr('mdir'), jn))
    inw = vm('NORMALIZE', vm('SUBTRACT', vm('SCALE', lt, Scale=vm('DOT_PRODUCT', m0, lt)), m0))  # into the court
    fI, zt = vm('SCALE', vm('ADD', I0, I1), Scale=0.5), m('MULTIPLY', m('ADD', ps(ZC, jn, 'FLOAT'), ps(ZC, jn1, 'FLOAT')), 0.5)
    la = v3(vm('ADD', fI, vm('SCALE', inw, Scale=m('ADD', m('MULTIPLY', m('SUBTRACT', zt, G0), 0.25), 0.15))), G0)  # foot, leaning 1 in 4
    lc = v3(vm('ADD', fI, vm('SCALE', inw, Scale=0.15)), zt)                                                       # walkway edge
    lp = store(store(store(store(bp, 'la', la), 'lb', vm('ADD', lc, vm('NORMALIZE', vm('SUBTRACT', lc, la)))), 'lt', lt), 'lg', v3(fI, zt))
    def gaps(pts, at_, along, length):  # 1.6 m across the face line, 4 m tall
        return n('GeometryNodeRealizeInstances', n('GeometryNodeInstanceOnPoints', n('GeometryNodeSetPosition', pts, Position=at_), None,
                 n('GeometryNodeMeshCube'), Rotation=n('FunctionNodeAxesToRotation', Z, along, primary_axis='Z', secondary_axis='X'),
                 Scale=n('ShaderNodeCombineXYZ', length, 1.6, 4)))
    gq, smp = face(m('SUBTRACT', E, 0.75), 0)  # the last 1.5 m of each flight, where it steps onto the walkway
    gap = join(gaps(lp, attr('lg'), attr('lt'), 1.1), gaps(sq, v3(gq, m('ADD', G0, SH)), smp.outputs['Tangent'], 1.5))
    # same winding as the wall profile; sits 5 cm into the walkway, its courtyard side trimmed with the wall's (shared cutter)
    rail = sweep(sp, [attr('rin'), I, I, attr('rin')], [m('SUBTRACT', ZC, 0.05)] * 2 + [m('ADD', ZC, RAIL_H)] * 2)

    stage('7 Core: (wall - bastion cylinders - crenels) + bodies + (rings - cutters - slab - crenels), each - courtyard - gates; + stairs')
    def boolean(op, a, *bs):
        b = n('GeometryNodeMeshBoolean', a, operation=op, solver='MANIFOLD')  # ~100x faster than EXACT, same solid
        for x in bs: L.new(live(x.outputs)[0], b.inputs['Mesh 2'])
        if op != 'DIFFERENCE': return b
        # an empty Mesh 1 (a fort with no bastions) makes MANIFOLD return Mesh 2, the 200 m courtyard prism: keep it empty
        return sw(n('GeometryNodeAttributeDomainSize', a, component='MESH').outputs['Face Count'], a, b, 'GEOMETRY')
    def own(geo, v): return n('GeometryNodeStoreNamedAttribute', geo, None, 'own', v, data_type='FLOAT', domain='FACE')
    body, ring, cut, wcut, bcren = (own(x, 1) for x in (body, ring, cut, wcut, bcren))  # face owner for bricks: 1 bastion, else 0 wall (slab cut is flush with the parapet face)
    # (A + B + C) - K = (A - K) + (B - K) + (C - K): cut the parts, then one union over the whole fort
    solid = boolean('UNION', None, boolean('DIFFERENCE', wall, wcut, wcren, court, gates), boolean('DIFFERENCE', rail, court, gates, gap),
                    boolean('DIFFERENCE', body, court, gates),
                    boolean('DIFFERENCE', ring, cut, slab, bcren, court, gates),
                    *(own(x, v) for x, v in zip(steps, (2, 3, 2, 3))))  # stairs uncut (the courtyard would take them); own 2 laterite, 3 bricked
    core = n('GeometryNodeSetShadeSmooth', solid, Shade_Smooth=False, domain='FACE')

    stage('8 Brick rows: world-level courses on upright faces, even rows on flat ones, one row set per face')
    S = GI('Brick Size'); q = m('MULTIPLY', S, 0.25)
    span = m('MAXIMUM', m('SUBTRACT', m('ADD', m('MAXIMUM', mx(sp, ZC), mx(bp, ZB)), GI('Parapet Height')), G0),
             m('MAXIMUM', m('MULTIPLY', mx(sp, HW), 2), mx(bp, R)))
    NR = m('ADD', m('CEIL', m('DIVIDE', span, S)), 1)  # rows per face family, enough for the tallest/widest face

    def seg(r, A3, B3, za, zb, ext):
        """Row r on profile segment A3->B3: (clamped factor, offset du of the true row centre, pitch across, keep margin)."""
        ln = vm('LENGTH', vm('SUBTRACT', B3, A3))
        if ext is None:  # flat face: rows spread evenly across it
            cnt = m('MAXIMUM', m('ROUND', m('ADD', m('DIVIDE', ln, S), 0.01)), 1)  # bias: exact ties (0.6 / 0.4) must not flicker
            t, pu, mg = m('DIVIDE', m('ADD', r, 0.5), cnt), m('DIVIDE', ln, cnt), m('SUBTRACT', m('SUBTRACT', cnt, r), 0.5)
        elif ext == 'edge':  # flat face of varying width: rows at brick pitch from A stay parallel (no jog where the count changes)
            c = m('MULTIPLY', m('ADD', r, 0.5), S)
            t, pu, mg = m('DIVIDE', c, ln), S, m('SUBTRACT', m('ADD', ln, m('MULTIPLY', S, 0.3)), c)  # last row trimmed at B
        else:  # upright face: courses at world levels so faces line up; ext (low, high) lets a course overhang a true edge
            cr = m('ADD', G0, m('MULTIPLY', m('ADD', r, 0.5), S))
            t, pu = m('DIVIDE', m('SUBTRACT', cr, za), m('SUBTRACT', zb, za)), S
            lo = m('SUBTRACT', cr, m('MINIMUM', za, zb)); hi = m('SUBTRACT', m('SUBTRACT', m('MAXIMUM', za, zb), cr), 1e-5)
            mg = m('MINIMUM', m('ADD', lo, q) if ext[0] else lo, m('ADD', hi, q) if ext[1] else hi)
        mg = m('MINIMUM', mg, m('SUBTRACT', ln, 1e-3))  # degenerate face: no rows
        a = m('MINIMUM', m('DIVIDE', q, ln), 0.5)
        tc = n('ShaderNodeClamp', t, a, m('SUBTRACT', 1, a))  # support point stays a quarter brick inside the face
        return tc, m('MULTIPLY', m('SUBTRACT', t, tc), ln), pu, mg

    def lerp(a, b, t): return vm('ADD', a, vm('SCALE', vm('SUBTRACT', b, a), Scale=t))
    def tag(geo, r, U, du, pu, mg, fam):  # per row point: U (up the face), k = (du, pitch across, margin), rf = (row, family)
        geo = store(geo, 'U', vm('NORMALIZE', U))
        geo = store(geo, 'k', n('ShaderNodeCombineXYZ', du, pu, mg))
        geo = store(geo, 'in', cmp(mg, 0, 'GREATER_EQUAL'), 'FLOAT')
        return store(geo, 'rf', n('ShaderNodeCombineXYZ', r, fam, 0))

    def course(cv):  # half-brick steps along each row; pt = along-row pitch
        cnt = m('MULTIPLY', m('MAXIMUM', m('ROUND', m('DIVIDE', n('GeometryNodeSplineLength').outputs['Length'], S)), 1), 2)
        cv = n('GeometryNodeResampleCurve', cv, Mode='Count', Count=cnt)
        sl = n('GeometryNodeSplineLength')
        return store(cv, 'pt', m('DIVIDE', m('MULTIPLY', sl.outputs['Length'], 2), sl.outputs['Point Count']), 'FLOAT')

    def bricks_at(cv, T):  # keep every other step, offset by row (running bond), and only rows on their face
        up = cmp(m('ABSOLUTE', n('ShaderNodeSeparateXYZ', attr('U')).outputs['Z']), 0.7, 'GREATER_THAN')  # upright face: courses stay level
        cv = store(cv, 'T', vm('NORMALIZE', sw(up, T, vm('MULTIPLY', T, (1, 1, 0)), 'VECTOR')))  # (rows clamped to a ramp edge tilt)
        odd = n('FunctionNodeIntegerMath', n('FunctionNodeIntegerMath', n('GeometryNodeSplineParameter').outputs['Index'],
                m('ROUND', n('ShaderNodeSeparateXYZ', attr('rf')).outputs['X'])), 2, operation='MODULO')  # resampled 15 -> 14.9999
        drop = n('FunctionNodeBooleanMath', cmp(odd, 0.5, 'GREATER_THAN'),
                 cmp(n('ShaderNodeSeparateXYZ', attr('k')).outputs['Z'], 0, 'LESS_THAN'), operation='OR')
        return n('GeometryNodeCurveToPoints', n('GeometryNodeDeleteGeometry', cv, drop, domain='POINT'), mode='EVALUATED')

    def near(v, dt='FLOAT'):  # value at the bastion nearest the inner line
        return n('GeometryNodeSampleIndex', bp, v, n('GeometryNodeSampleNearest', bp, I, domain='POINT'), data_type=dt, domain='POINT')
    inside = cmp(vm('DISTANCE', I, near(pos, 'FLOAT_VECTOR')), near(R), 'LESS_THAN')
    zi = sw(inside, ZC, m('MAXIMUM', ZC, near(ZB)), 'FLOAT')  # courtyard face rises to a raised bastion's platform
    # rows run per leg: the spine split at sharp corners (where the miter fences stand), so no row bends through a miter
    acc = n('GeometryNodeAccumulateField', n('GeometryNodeFieldAtIndex', Index=idx, Value=cmp(vm('LENGTH', attr('mdir')), 1.002, 'GREATER_EQUAL'),
            data_type='FLOAT', domain='POINT'), data_type='INT', domain='EDGE')  # curve-to-mesh edge i starts at point i
    grp = n('FunctionNodeIntegerMath', acc.outputs['Leading'], n('FunctionNodeIntegerMath', acc.outputs['Total'], 2, operation='MAXIMUM'),
            operation='MODULO')  # last leg wraps into the first; one corner still splits
    legs = n('GeometryNodeMeshToCurve', n('GeometryNodeRealizeInstances', n('GeometryNodeSplitToInstances', n('GeometryNodeCurveToMesh', sp),
             None, grp, domain='EDGE')))
    wr = n('GeometryNodeJoinGeometry')
    zs =sw(cmp(MH, 0, 'GREATER_THAN'), m('SUBTRACT', G0, 1e3), m('SUBTRACT', zp, MH), 'FLOAT')  # crenel sill rows (only crenels support them)
    for A, za, B, zb, ext in ((I, G0, I, zi, (0, 1)), (I, ZC, pf, ZC, 'edge'), (pf, ZC, pf, zp, (1, 1)), (pf, zp, O, zp, None),
                              (pf, zs, O, zs, None), (O, zp, O, ZC, (0, 1)), (O, ZC, toe, G0, (0, 0))):
        d = n('GeometryNodeDuplicateElements', legs, None, NR, domain='SPLINE'); r = d.outputs['Duplicate Index']
        A3, B3 = v3(A, za), v3(B, zb)
        tc, du, pu, mg = seg(r, A3, B3, za, zb, ext)
        d = n('GeometryNodeSetPosition', tag(d, r, vm('SUBTRACT', B3, A3), du, pu, mg, 0), Position=lerp(A3, B3, tc))
        L.new(live(d.outputs)[0], wr.inputs[0])
    wr = n('GeometryNodeDeleteGeometry', wr, cmp(attr('in', 'FLOAT'), 0, 'LESS_EQUAL'), domain='CURVE')  # rows wholly off
    tg = n('GeometryNodeInputTangent')
    wp = bricks_at(course(wr), vm('SCALE', tg, Scale=m('SIGN', vm('DOT_PRODUCT', tg, attr('tan')))))  # legs come out either way round

    br = n('GeometryNodeJoinGeometry')
    for ra, za, rb, zb, ext in ((RT, G0, R, ZB, (0, 0)), (R, ZB, R, ZP, (0, 1)), (R, ZP, RC, ZP, None),
                                (RC, ZP, RC, ZB, (1, 1)), (R, ZB, RC, ZB, None), (RC, ZB, 0, ZB, None),  # R..RC: walkway openings
                                (R, m('ADD', zs, m('SUBTRACT', ZP, zp)), RC, m('ADD', zs, m('SUBTRACT', ZP, zp)), None)):  # crenel sills
        d = n('GeometryNodeDuplicateElements', bp, None, NR, domain='POINT'); r = d.outputs['Duplicate Index']
        A3, B3 = n('ShaderNodeCombineXYZ', ra, 0, za), n('ShaderNodeCombineXYZ', rb, 0, zb)  # (radius, -, z)
        tc, du, pu, mg = seg(r, A3, B3, za, zb, ext)
        P = n('ShaderNodeSeparateXYZ', lerp(A3, B3, tc))
        d = store(tag(d, r, vm('SUBTRACT', B3, A3), du, pu, mg, 1), 'rho', P.outputs['X'], 'FLOAT')
        d = n('GeometryNodeSetPosition', d, Position=vm('ADD', pos, n('ShaderNodeCombineXYZ', 0, 0, P.outputs['Z'])))
        L.new(live(d.outputs)[0], br.inputs[0])
    br = n('GeometryNodeDeleteGeometry', br, cmp(attr('in', 'FLOAT'), 0, 'LESS_EQUAL'), domain='POINT')
    rings = n('GeometryNodeInstanceOnPoints', br, Instance=n('GeometryNodeCurvePrimitiveCircle', Resolution=CR),
              Scale=attr('rho', 'FLOAT'))
    rings = course(n('GeometryNodeRealizeInstances', rings))
    rh = vm('NORMALIZE', vm('MULTIPLY', vm('SUBTRACT', pos, attr('ctr')), (1, 1, 0)))
    u2 = n('ShaderNodeSeparateXYZ', attr('U'))
    rings = store(rings, 'U', vm('ADD', vm('SCALE', rh, Scale=u2.outputs['X']), n('ShaderNodeCombineXYZ', 0, 0, u2.outputs['Z'])))
    bpts = bricks_at(rings, vm('CROSS_PRODUCT', Z, rh))

    def cheeks(cp, cxy, half, ac, za, zb, ext, fam):
        """Both side faces of each opening centred at cp ('tg' along the wall, half out each way): courses za..zb, rows along ac."""
        d = n('GeometryNodeDuplicateElements', cp, None, m('MULTIPLY', NR, 2), domain='POINT'); di = d.outputs['Duplicate Index']
        sd = m('SUBTRACT', m('MULTIPLY', m('MODULO', di, 2), 2), 1)  # -1 / +1 face
        r = m('FLOOR', m('DIVIDE', di, 2))
        tc, du, pu, mg = seg(r, n('ShaderNodeCombineXYZ', 0, 0, za), n('ShaderNodeCombineXYZ', 0, 0, zb), za, zb, ext)
        d = store(tag(d, r, Z, du, pu, mg, fam), 'T', vm('SCALE', vm('CROSS_PRODUCT', attr('tg'), Z), Scale=sd))  # N = T x up: into the opening
        d = store(store(d, 'ac', ac), 'c3', v3(vm('ADD', cxy, vm('SCALE', attr('tg'), Scale=m('MULTIPLY', half, sd))),
                                               m('ADD', za, m('MULTIPLY', m('SUBTRACT', zb, za), tc))))
        d = n('GeometryNodeDeleteGeometry', d, cmp(attr('in', 'FLOAT'), 0, 'LESS_EQUAL'), domain='POINT')
        ln = n('GeometryNodeRealizeInstances', n('GeometryNodeInstanceOnPoints', d, Instance=n('GeometryNodeCurvePrimitiveLine')))
        ln = n('GeometryNodeSetPosition', ln, Position=vm('ADD', attr('c3'), vm('SCALE', attr('ac'),
               Scale=m('SUBTRACT', n('FunctionNodeIntegerMath', idx, 2, operation='MODULO'), 0.5))))
        return bricks_at(course(ln), attr('T'))
    hc = m('MULTIPLY', CW, 0.5)
    rad = vm('NORMALIZE', vm('MULTIPLY', vm('SUBTRACT', pos, attr('ctr')), (1, 1, 0)))
    gz = m('SUBTRACT', m('ADD', G0, m('MULTIPLY', GI('Gate Height'), gsc.outputs['Z'])), w2)  # arch springing
    cpts = join(cheeks(wcp, pos, hc, vm('SUBTRACT', O, pf), m('SUBTRACT', zp, MH), zp, (0, 1), 0),                  # wall merlon gaps
                cheeks(bcp, pos, hc, vm('SCALE', rad, Scale=m('SUBTRACT', R, RC)), m('SUBTRACT', ZP, MH), ZP, (0, 1), 1),  # bastion gaps
                cheeks(gp, vm('SCALE', vm('ADD', gs(I, 'FLOAT_VECTOR'), gs(toe, 'FLOAT_VECTOR')), Scale=0.5), w2,      # gate jambs
                       vm('SUBTRACT', gs(toe, 'FLOAT_VECTOR'), gs(I, 'FLOAT_VECTOR')), G0, gz, (0, 0), 0))
    # platform centre: one square slab inside the innermost ring (the rings there shrink to slivers and drop out)
    pc = m('DIVIDE', RC, m('MAXIMUM', m('ROUND', m('ADD', m('DIVIDE', RC, S), 0.01)), 1)); sl = m('MULTIPLY', pc, 1.35)
    cb = n('GeometryNodeSetPosition', bp, Position=v3(pos, ZB))
    cb = store(store(store(store(store(cb, 'T', (1, 0, 0)), 'U', (0, 1, 0)), 'k', n('ShaderNodeCombineXYZ', 0, sl, 1)),
                     'rf', (0, 1, 0)), 'pt', sl, 'FLOAT')

    def srow(wa, ta, wb, tb, side, along):  # stair face rows (family 3) at the wall's course levels, along the flight or across it
        cv = n('GeometryNodeResampleCurve', fl0, Mode='Count', Count=m('ADD', m('CEIL', m('MULTIPLY', E, 2)), 3)) if along else fl0
        d = n('GeometryNodeDuplicateElements', cv, None, m('ADD', m('CEIL', m('DIVIDE', m('ADD', SH, PH + 0.1), S)), 1), domain='SPLINE')
        r, F = d.outputs['Duplicate Index'], n('GeometryNodeSplineParameter').outputs['Factor']
        t_, w_ = (m('ADD', a, m('MULTIPLY', m('SUBTRACT', b, a), F)) for a, b in ((ta, tb), (wa, wb)))
        p, smp = face(t_, w_)
        nn = vm('NORMALIZE', smp.outputs['Value']) if along else vm('SCALE', vm('NORMALIZE', smp.outputs['Tangent']), Scale=ss.outputs['Y'])  # out of the court / up the flight
        cr = m('ADD', G0, m('MULTIPLY', m('ADD', r, 0.5), S))
        d = tag(store(d, 'nn', vm('SCALE', nn, Scale=side)), r, Z, 0, S, m('SUBTRACT', m('ADD', G0, m('ADD', SH, PH + 0.02 + 0.1)), cr), 3)
        return n('GeometryNodeSetPosition', d, Position=v3(p, cr))
    Wi = m('SUBTRACT', W, 0.3)
    spts = bricks_at(course(join(srow(W, -0.02, W, m('ADD', E, 0.3), -1, True),            # parapet + end wall, court side
                                 srow(Wi, -0.02, Wi, m('SUBTRACT', E, 0.05), 1, True),     # parapet over the treads
                                 srow(Wi, -0.02, W, -0.02, -1, False),                     # parapet foot
                                 srow(-0.04, m('SUBTRACT', E, 0.05), Wi, m('SUBTRACT', E, 0.05), -1, False),  # end wall over the top tread
                                 srow(-0.04, m('ADD', E, 0.3), m('ADD', W, 0.03), m('ADD', E, 0.3), 1, False))),  # end wall back
                     vm('CROSS_PRODUCT', Z, attr('nn')))

    stage('9 Fit bricks: snap onto a face of their own family, trim at edges and against rising faces, drop slivers')
    pts = join(wp, bpts, cpts, cb, spts)
    T_, U_ = attr('T'), attr('U')
    N_ = vm('NORMALIZE', vm('CROSS_PRODUCT', T_, U_))  # outward face normal
    k, rf = n('ShaderNodeSeparateXYZ', attr('k')), n('ShaderNodeSeparateXYZ', attr('rf'))
    sup = n('GeometryNodeRaycast', Target_Geometry=solid, Attribute=attr('own', 'FLOAT'), data_type='FLOAT',
            Source_Position=vm('ADD', pos, vm('SCALE', N_, Scale=0.1)), Ray_Direction=vm('SCALE', N_, Scale=-1), Ray_Length=0.25)
    ok = AND(sup.outputs['Is Hit'], cmp(m('ABSOLUTE', m('SUBTRACT', sup.outputs['Hit Distance'], 0.1)), 0.06, 'LESS_THAN'),
             cmp(vm('DOT_PRODUCT', sup.outputs['Hit Normal'], N_), 0.7, 'GREATER_THAN'),
             cmp(m('ABSOLUTE', m('SUBTRACT', sup.outputs['Attribute'], rf.outputs['Y'])), 0.5, 'LESS_THAN'))
    pts = n('GeometryNodeSetPosition', store(pts, 'ok', ok, 'BOOLEAN'), Position=sup.outputs['Hit Position'])
    pts = n('GeometryNodeDeleteGeometry', pts, n('FunctionNodeBooleanMath', attr('ok', 'BOOLEAN'), operation='NOT'), domain='POINT')

    gap, rel = GI('Mortar Gap'), GI('Brick Relief')
    hg = m('MULTIPLY', gap, 0.5)
    fence = lathe([m('SUBTRACT', G0, 1), m('ADD', ZP, 1)], [R, R])  # bastion circles: wall paving ends there (coplanar, no edge to hit)
    ml = vm('LENGTH', attr('mdir'))  # ... and at sharp spine corners (turn > ~7 deg): vertical miter planes
    mp = n('GeometryNodeDeleteGeometry', n('GeometryNodeCurveToPoints', sp, mode='EVALUATED'), cmp(ml, 1.002, 'LESS_THAN'), domain='POINT')
    mpl = n('GeometryNodeRealizeInstances', n('GeometryNodeInstanceOnPoints', mp, None, n('GeometryNodeMeshGrid'),
            Rotation=n('FunctionNodeAxesToRotation', attr('mdir'), Z, primary_axis='X', secondary_axis='Y'),
            Scale=n('ShaderNodeCombineXYZ', m('MULTIPLY', m('ADD', m('MULTIPLY', HW, ml), 2), 2), 1e3, 1)))
    fence = n('GeometryNodeJoinGeometry', fence); L.new(live(mpl.outputs)[0], fence.inputs[0])
    flat = cmp(m('ABSOLUTE', n('ShaderNodeSeparateXYZ', N_).outputs['Z']), 0.7, 'GREATER_THAN')
    paving = AND(flat, cmp(rf.outputs['Y'], 0.5, 'LESS_THAN'))
    def reach(dv, ln, w, e):  # free run along dv: just under the face (convex edge), just above it (rising face + its bricks), fences
        best = None
        for tgt, off, pad, gate in ((solid, -0.01, hg, None), (solid, m('ADD', rel, 0.01), m('ADD', rel, hg), None), (fence, 0, hg, paving)):
            rc = n('GeometryNodeRaycast', Target_Geometry=tgt, Source_Position=vm('ADD', pos, vm('SCALE', N_, Scale=off)),
                   Ray_Direction=dv, Ray_Length=m('ADD', m('MAXIMUM', ln, 0), 0.01) if gate is None else
                   sw(gate, 0.0, m('ADD', m('MAXIMUM', ln, 0), 0.01), 'FLOAT'))
            hit = rc.outputs['Is Hit'] if gate is None else AND(rc.outputs['Is Hit'], gate)
            Nh = rc.outputs['Hit Normal']  # oblique hit: the brick corner (half-width e along w) reaches the plane first
            tilt = m('DIVIDE', m('MULTIPLY', e, m('ABSOLUTE', vm('DOT_PRODUCT', w, Nh))), m('MAXIMUM', m('ABSOLUTE', vm('DOT_PRODUCT', dv, Nh)), 0.3))
            d = sw(hit, BIG, m('SUBTRACT', rc.outputs['Hit Distance'], m('ADD', pad, tilt)), 'FLOAT')
            best = d if best is None else m('MINIMUM', best, d)
        return best
    def neg(x): return vm('SCALE', x, Scale=-1)
    hU = m('MULTIPLY', m('SUBTRACT', k.outputs['Y'], gap), 0.5)
    rho = attr('rho', 'FLOAT')  # ring radius (bastion rows): flat ring bricks are sized at their inner edge so they don't collide
    wedge = sw(AND(flat, cmp(rho, 0, 'GREATER_THAN')), 1.0, m('DIVIDE', m('MAXIMUM', m('SUBTRACT', rho, m('ADD', k.outputs['X'], hU)), 0), rho), 'FLOAT')
    hT = m('MULTIPLY', m('SUBTRACT', m('MULTIPLY', attr('pt', 'FLOAT'), wedge), gap), 0.5)
    hiU, loU = m('ADD', k.outputs['X'], hU), m('SUBTRACT', k.outputs['X'], hU)
    pts = store(pts, 'hi', n('ShaderNodeCombineXYZ', m('MINIMUM', hT, reach(T_, hT, U_, hU)), m('MINIMUM', hiU, reach(U_, hiU, T_, hT))))
    pts = store(pts, 'lo', n('ShaderNodeCombineXYZ', m('MAXIMUM', m('MULTIPLY', hT, -1), m('MULTIPLY', reach(neg(T_), hT, U_, hU), -1)),
                             m('MAXIMUM', loU, m('MULTIPLY', reach(neg(U_), m('MULTIPLY', loU, -1), T_, hT), -1))))
    HI, LO = attr('hi'), attr('lo')
    sz = n('ShaderNodeSeparateXYZ', vm('SUBTRACT', HI, LO)); mid = n('ShaderNodeSeparateXYZ', vm('SCALE', vm('ADD', HI, LO), Scale=0.5))
    sliver = n('FunctionNodeBooleanMath', cmp(sz.outputs['X'], m('MULTIPLY', S, 0.2), 'LESS_THAN'),
               cmp(sz.outputs['Y'], m('MULTIPLY', S, 0.2), 'LESS_THAN'), operation='OR')
    pts = n('GeometryNodeDeleteGeometry', pts, sliver, domain='POINT')

    stage('10 Bricks: rounded blocks, jittered, per-brick tint; the core shows between them as mortar')
    J, seed = GI('Brick Jitter'), GI('Seed')
    # half a brick deep, but no deeper than the thinnest bricked feature (stair parapet 0.3, Parapet Thickness), or big bricks poke through
    dep = m('MINIMUM', m('MULTIPLY', S, 0.5), m('ADD', rel, m('MULTIPLY', m('MINIMUM', GI('Parapet Thickness'), 0.3), 0.8)))
    def rnd(dt, lo, hi, s): return n('FunctionNodeRandomValue', Min=lo, Max=hi, Seed=m('ADD', seed, s), data_type=dt)
    off = m('ADD', m('SUBTRACT', rel, m('MULTIPLY', dep, 0.5)), m('MULTIPLY', m('MULTIPLY', J, rel), rnd('FLOAT', -0.6, 0.6, 1)))
    P = vm('ADD', vm('ADD', pos, vm('SCALE', T_, Scale=mid.outputs['X'])),
           vm('ADD', vm('SCALE', U_, Scale=mid.outputs['Y']), vm('SCALE', N_, Scale=off)))
    pts = store(n('GeometryNodeSetPosition', pts, Position=P), 'tint', rnd('FLOAT', 0, 1, 2), 'FLOAT')
    # every back corner must lie in the core: the T/U trims can't see a concave notch, so a brick wider than its face
    # (the platform slab at a courtyard corner, big courses over a stair) would hang in the air there; drop it instead
    back = vm('SUBTRACT', pos, vm('SCALE', N_, Scale=m('ADD', off, m('MAXIMUM', m('SUBTRACT', dep, rel), 0.02))))
    inside = []
    for a, b in ((-0.4, -0.4), (-0.4, 0.4), (0.4, -0.4), (0.4, 0.4)):
        c = vm('ADD', back, vm('ADD', vm('SCALE', T_, Scale=m('MULTIPLY', sz.outputs['X'], a)), vm('SCALE', U_, Scale=m('MULTIPLY', sz.outputs['Y'], b))))
        rc = n('GeometryNodeRaycast', Target_Geometry=solid, Source_Position=c, Ray_Direction=neg(N_), Ray_Length=BIG)
        inside.append(AND(rc.outputs['Is Hit'], cmp(vm('DOT_PRODUCT', rc.outputs['Hit Normal'], N_), 0, 'LESS_THAN')))  # leaves the core
    pts = n('GeometryNodeDeleteGeometry', pts, n('FunctionNodeBooleanMath', AND(*inside), operation='NOT'), domain='POINT')
    Jt = m('MULTIPLY', J, m('MINIMUM', m('DIVIDE', 0.4, S), 1))  # tilt angle shrinks past the default size: a brick's rim moves the same few mm
    tilt = n('FunctionNodeEulerToRotation', rnd('FLOAT_VECTOR', vm('SCALE', (-0.03, -0.03, -0.05), Scale=Jt),
                                                vm('SCALE', (0.03, 0.03, 0.05), Scale=Jt), 3))
    rot = n('FunctionNodeRotateRotation', n('FunctionNodeAxesToRotation', N_, T_, primary_axis='Z', secondary_axis='X'),
            tilt, rotation_space='LOCAL')
    cube = n('GeometryNodeSubdivisionSurface', n('GeometryNodeMeshCube', Size=(1, 1, 1)), Level=1, Edge_Crease=0.6)
    cube = n('GeometryNodeSetMaterial', cube, Material=GI('Material'))
    inst = n('GeometryNodeInstanceOnPoints', pts, Instance=cube, Rotation=rot,
             Scale=n('ShaderNodeCombineXYZ', sz.outputs['X'], sz.outputs['Y'], dep))
    mortar = n('GeometryNodeSetMaterial', n('GeometryNodeSetMaterial', core, Material=GI('Mortar Material')),
               AND(cmp(attr('own', 'FLOAT'), 1.5, 'GREATER_THAN'), n('FunctionNodeBooleanMath', cmp(attr('own', 'FLOAT'), 2.5, 'LESS_THAN'),
                   cmp(m('ABSOLUTE', n('ShaderNodeSeparateXYZ', n('GeometryNodeInputNormal')).outputs['Z']), 0.7, 'GREATER_THAN'), operation='OR')),
               GI('Material'))  # stairs: laterite treads, coping, tops; bricked parapet and end wall
    geo = sw(GI('Bricks'), n('GeometryNodeSetMaterial', core, Material=GI('Material')), join(mortar, inst), 'GEOMETRY')

    stage('11 Props: a ladder up the courtyard face to every bastion platform; flagpoles by Flag Chance')
    cyl = n('GeometryNodeSetMaterial', n('GeometryNodeMeshCylinder', Vertices=8, Radius=1, Depth=1), Material=GI('Wood Material'))
    def rod(pts, r):  # cylinder from attr 'ra' to 'rb' on every point
        A_, B_ = attr('ra'), attr('rb')
        p = n('GeometryNodeSetPosition', pts, Position=vm('SCALE', vm('ADD', A_, B_), Scale=0.5))
        return n('GeometryNodeInstanceOnPoints', p, Instance=cyl, Rotation=n('FunctionNodeAlignRotationToVector', Vector=vm('SUBTRACT', B_, A_), axis='Z'),
                 Scale=n('ShaderNodeCombineXYZ', r, r, vm('DISTANCE', A_, B_)))
    LA, LB, LT = attr('la'), attr('lb'), attr('lt')  # ladder spots from 6c
    d = n('GeometryNodeDuplicateElements', lp, None, 2, domain='POINT')
    sd = m('SUBTRACT', m('MULTIPLY', d.outputs['Duplicate Index'], 2), 1)
    rails = rod(store(store(d, 'ra', vm('ADD', LA, vm('SCALE', LT, Scale=m('MULTIPLY', sd, 0.3)))), 'rb',
                      vm('ADD', LB, vm('SCALE', LT, Scale=m('MULTIPLY', sd, 0.3)))), 0.05)
    nr = m('CEIL', m('DIVIDE', vm('DISTANCE', LA, LB), 0.32))
    d = n('GeometryNodeDuplicateElements', lp, None, nr, domain='POINT')
    c = vm('ADD', LA, vm('SCALE', vm('SUBTRACT', LB, LA), Scale=m('DIVIDE', m('ADD', d.outputs['Duplicate Index'], 0.5), nr)))
    rungs = rod(store(store(d, 'ra', vm('SUBTRACT', c, vm('SCALE', LT, Scale=0.34))), 'rb', vm('ADD', c, vm('SCALE', LT, Scale=0.34))), 0.03)
    FH = GI('Flagpole Height')
    fb = store(store(bp, 'ra', v3(pos, m('SUBTRACT', ZB, 0.2))), 'rb', v3(pos, m('ADD', ZB, FH)))  # platform centres
    wk = n('GeometryNodeCurveToPoints', n('GeometryNodeResampleCurve', sp, Mode='Length', Length=25), mode='EVALUATED')
    wx = vm('ADD', pf, vm('SCALE', vm('NORMALIZE', vm('SUBTRACT', I, pf)), Scale=0.4))  # walkway, by the parapet
    fw = store(store(wk, 'ra', v3(wx, m('SUBTRACT', ZC, 0.2))), 'rb', v3(wx, m('ADD', ZC, FH)))
    fl = n('GeometryNodeDeleteGeometry', join(fb, fw), n('FunctionNodeBooleanMath', n('FunctionNodeRandomValue', data_type='BOOLEAN',
           Probability=GI('Flag Chance'), Seed=m('ADD', GI('Seed'), 21)), operation='NOT'), domain='POINT')
    cloth = n('GeometryNodeSetMaterial', n('GeometryNodeMeshCube'), Material=GI('Flag Material'))
    flags = n('GeometryNodeInstanceOnPoints', n('GeometryNodeSetPosition', fl, Position=vm('ADD', attr('rb'), (0.75, 0, -0.5))),
              Instance=cloth, Scale=(1.4, 0.03, 0.9))  # one wind direction for all
    props = store(n('GeometryNodeRealizeInstances', join(rails, rungs, rod(fl, 0.07), flags)), 'prop', True, 'BOOLEAN')  # check() skips these
    put(n('NodeGroupOutput').inputs[0], join(geo, props))
    g['fortwall_fp'] = FINGERPRINT
    return g


def _fingerprint():  # build_group's source + the constants it reads: changes whenever the graph would
    try: src = inspect.getsource(build_group)
    except (OSError, TypeError): return None  # exec()'d without a file: can't tell, so groups are trusted as they are
    return hashlib.sha256((src + repr((EPS, BIG, RAIL_T, RAIL_H, PARTS, PANELS))).encode()).hexdigest()[:16]


FINGERPRINT = _fingerprint()


def _inputs(g): return [i for i in g.interface.items_tree if i.item_type == 'SOCKET' and i.in_out == 'INPUT' and i.name != 'Geometry']


def ensure_group(name='FortWall'):
    """The FortWall group, current with this generator. Reused if its fingerprint matches, else appended from the bundled
    asset (under a second), else built from source (minutes). An outdated group in the file is replaced: every modifier on
    it switches to the new one with its values kept by name (same socket ids, so drivers and keys still resolve)."""
    old = bpy.data.node_groups.get(name)
    if old and (FINGERPRINT is None or old.get('fortwall_fp') == FINGERPRINT): return old
    new = None
    if ASSET and ASSET.exists():
        with bpy.data.libraries.load(str(ASSET), link=False) as (src, dst): dst.node_groups = [name]
        new = dst.node_groups[0]
        for lib in [l for l in bpy.data.libraries if Path(bpy.path.abspath(l.filepath)) == ASSET]:
            if not any(i.library == lib for i in bpy.data.node_groups): bpy.data.libraries.remove(lib)  # append leaves it empty
        ids = {i.name: i.identifier for i in _inputs(new)} if new else {}
        if new and (new.get('fortwall_fp') != FINGERPRINT or (old and any(ids.get(i.name, i.identifier) != i.identifier for i in _inputs(old)))):
            bpy.data.node_groups.remove(new); new = None  # asset not baked from this source, or ids moved: build in place
    if new is None: return build_group(name)  # in place: socket ids and modifier values kept
    new.use_fake_user = False
    if old:
        mods = [md for o in bpy.data.objects for md in o.modifiers if md.type == 'NODES' and md.node_group == old]
        vals = [{i.name: getattr(md.properties.inputs, i.identifier).value for i in _inputs(old)} for md in mods]
        for md in mods: md.node_group = new  # same ids, so Blender keeps the values; it also adds inputs the old group lacked
        old.user_remap(new)  # any other user (a group node in another tree)
        for md, v in zip(mods, vals):
            for i in _inputs(new):
                if i.name in v: getattr(md.properties.inputs, i.identifier).value = v[i.name]
        bpy.data.node_groups.remove(old)
    new.name = name
    return new


def bake():
    """Developer: build the group from source and save it as the bundled asset ensure_group() appends. Run headless."""
    g = build_group()
    bpy.data.libraries.write(str(ASSET), {g}, fake_user=True, compress=True)
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
    gcol = bpy.data.collections.get('Gates')
    if not gcol:
        gcol = bpy.data.collections.new('Gates'); scn.collection.children.link(gcol)
        e = bpy.data.objects.new('Gate_1', None); e.empty_display_type = 'ARROWS'
        e.location, e.scale = (-20, -31.3, 0), (1.5, 1.5, 1); gcol.objects.link(e)  # 3 m wide, Gate Height tall
    scol = bpy.data.collections.get('Stairs')
    if not scol:
        scol = bpy.data.collections.new('Stairs'); scn.collection.children.link(scol)
        for i, (x, y, a, w) in enumerate([(8, -33.2, 0, 1.5), (-43, 0, -90, 1.5)]):  # foot, rising toward local X, width
            e = bpy.data.objects.new(f'Stair_{i + 1}', None); e.empty_display_type = 'SINGLE_ARROW'
            e.location, e.rotation_euler, e.scale = (x, y, 0), (0, 0, math.radians(a)), (w, 1, 1); scol.objects.link(e)
    ob = bpy.data.objects.get('Fort_Wall')
    if not ob:
        ob = new_curve('Fort_Wall', [(-40, -30, 0, 1), (35, -35, 0, 1), (50, 10, 0, 1), (5, 40, 3, 1.5), (-45, 20, 0, 1)])
        scn.collection.objects.link(ob)
    md = ob.modifiers.get('FortWall')
    if md and (md.node_group != g or mod_input(md, 'Bastions').value is None):
        ob.modifiers.remove(md)  # interface was rebuilt: start from fresh defaults
    attach(ob, Bastions=col, Gates=gcol, Stairs=scol)
    return ob


def new_curve(name, pts):
    """Closed 3D Bezier object with sharp (vector) corners; pts = (x, y, z, radius). Not linked to a collection."""
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '3D'
    s = cu.splines.new('BEZIER')
    s.bezier_points.add(len(pts) - 1)
    for p, (x, y, z, r) in zip(s.bezier_points, pts):
        p.co, p.radius = (x, y, z), r
        p.handle_left_type = p.handle_right_type = 'VECTOR'
    s.use_cyclic_u = True
    return bpy.data.objects.new(name, cu)


def fort_modifier(ob):
    g = bpy.data.node_groups.get('FortWall')
    return ob and g and next((m for m in ob.modifiers if m.type == 'NODES' and m.node_group == g), None)


def attach(ob, **parts):
    """Make curve object ob a fort: FortWall modifier (node group built if missing), empty part inputs filled from parts
    (else new '<ob> Bastions' etc. collections under '<ob> Parts'), default materials. Values already set are kept."""
    g = ensure_group()
    md = fort_modifier(ob)
    if not md:
        md = ob.modifiers.new('FortWall', 'NODES'); md.node_group = g
    ob.data.dimensions = '3D'  # point Z raises the wall there
    home = None
    for k in PARTS:
        if mod_input(md, k).value is None:
            c = parts.get(k)
            if c is None:
                if home is None:
                    home = bpy.data.collections.new(f'{ob.name} Parts')
                    (ob.users_collection[0] if ob.users_collection else bpy.context.scene.collection).children.link(home)
                c = bpy.data.collections.new(f'{ob.name} {k}'); home.children.link(c)
            mod_input(md, k).value = c
    M = bpy.data.materials.get
    for k, v in (('Material', lambda: M('FortWall_Brick') or brick_mat()), ('Mortar Material', lambda: M('FortWall_Mortar') or mortar_mat()),
                 ('Wood Material', lambda: M('FortWall_Wood') or _mat('FortWall_Wood', (0.10, 0.06, 0.03, 1), (0.28, 0.17, 0.09, 1), False)),
                 ('Flag Material', lambda: M('FortWall_Flag') or _mat('FortWall_Flag', (0.85, 0.28, 0.02, 1), (0.98, 0.45, 0.05, 1), False))):
        if mod_input(md, k).value is None: mod_input(md, k).value = v()  # keep the user's picks
    ob.update_tag()
    return md


def add_part(md, kind, loc, yaw=0.0):
    """New empty in the fort's `kind` collection ('Bastions' / 'Gates' / 'Stairs') at world loc, turned yaw about Z.
    Bastion: radius = scale, Z over the fort = extra platform height. Gate: half width = scale X. Stair: width = scale X."""
    name, shape, scale = {'Bastions': ('Bastion', 'CIRCLE', (1, 1, 1)), 'Gates': ('Gate', 'ARROWS', (1.5, 1.5, 1)),
                          'Stairs': ('Stair', 'SINGLE_ARROW', (1.5, 1, 1))}[kind]
    if kind == 'Bastions': scale = (max(3.0, 2 * mod_input(md, 'Crown Width').value),) * 3
    e = bpy.data.objects.new(name, None)
    e.empty_display_type, e.empty_display_size = shape, 1
    e.location, e.rotation_euler, e.scale = loc, (0, 0, yaw), scale
    mod_input(md, kind).value.objects.link(e)
    md.id_data.update_tag()
    return e


def check(ob=None):
    """The core (ladders and flags left out) is one closed, outward-facing solid, and bricks were laid if Bricks is on."""
    import bmesh, time
    ob = ob or bpy.data.objects['Fort_Wall']
    t0 = time.perf_counter(); dg = bpy.context.evaluated_depsgraph_get(); ob.update_tag(); dg.update()
    ev = ob.evaluated_get(dg); secs = time.perf_counter() - t0
    gs = ev.evaluated_geometry(); pc = gs.instances_pointcloud()  # one point per brick (gs must outlive pc)
    bricks = len(pc.points) if pc else 0  # not dg.object_instances: that also holds the object's own mesh
    me = ev.to_mesh(); bm = bmesh.new(); bm.from_mesh(me)
    a = me.attributes.get('prop')
    if a:
        prop = [False] * len(me.vertices); a.data.foreach_get('value', prop)
        bmesh.ops.delete(bm, geom=[v for v in bm.verts if prop[v.index]], context='VERTS')
    vol, open_edges = bm.calc_volume(signed=True), sum(not e.is_manifold for e in bm.edges)
    seen, islands = set(), 0
    for v in bm.verts:
        if v in seen: continue
        seen.add(v); todo = [v]; faces = set()
        while todo:
            u = todo.pop(); faces.update(u.link_faces)
            for e in u.link_edges:
                w = e.other_vert(u)
                if w not in seen: seen.add(w); todo.append(w)
        islands += sum(f.calc_area() for f in faces) > 1e-3  # booleans can leave zero-area slivers: not pieces
    bm.free(); ev.to_mesh_clear()
    assert islands == 1, f'core is {islands} separate pieces, not one'
    assert vol > 0, f'normals point inward (signed volume {vol:.0f})'
    assert open_edges == 0, f'{open_edges} non-manifold edges'
    assert bricks > 0 or not mod_input(fort_modifier(ob), 'Bricks').value, 'no bricks'
    return dict(volume=round(vol), open_edges=open_edges, islands=islands, bricks=bricks, secs=round(secs, 2))


if __name__ == '__main__':
    demo()
