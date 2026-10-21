"""FortWall add-on: draw a fort with a Bezier curve.

Add > Curve > Fort Wall, or select any curve and click Make Fort Wall (sidebar N > Fort). The sidebar then places
bastions, gates and stairs (at selected control points in Edit Mode, else at the 3D cursor), edits the selected point's
crown width and height, the selected part's size, and every wall setting. The geometry is generator.py's node group.
"""
import bpy, math
from mathutils import Vector
from bpy.props import BoolProperty, EnumProperty, FloatProperty, IntProperty
from . import generator as gen

KINDS = [(k, k[:-1] if k != 'Stairs' else 'Stair', '') for k in gen.PARTS]
ICONS = {'Bastions': 'MESH_CIRCLE', 'Gates': 'EMPTY_ARROWS', 'Stairs': 'EMPTY_SINGLE_ARROW'}


def find_fort(ctx):
    """(curve, modifier, part kind or None) for the active object: a fort, or an empty in one of its part collections."""
    ob = ctx.active_object
    md = gen.fort_modifier(ob)
    if md: return ob, md, None
    if ob and ob.type == 'EMPTY':
        for o in ctx.scene.objects:
            md = gen.fort_modifier(o)
            for k in gen.PARTS if md else ():
                c = gen.mod_input(md, k).value
                if c and c.objects.get(ob.name) == ob: return o, md, k
    return None


def selected_points(ob):
    """(point, local xyz, local tangent) for each selected control point of curve ob (Edit Mode data)."""
    out = []
    for s in ob.data.splines:
        bez = s.type == 'BEZIER'
        pts = s.bezier_points if bez else s.points
        co = [p.co.xyz for p in pts]
        for i, p in enumerate(pts):
            if not (p.select_control_point if bez else p.select): continue
            j, k = (i - 1, i + 1) if s.use_cyclic_u else (max(i - 1, 0), min(i + 1, len(pts) - 1))
            out.append((p, co[i], co[k % len(pts)] - co[j]))
    return out


class FORTWALL_OT_add(bpy.types.Operator):
    """Add a closed Bezier fort wall, with bastions at its corners"""
    bl_idname, bl_label, bl_options = 'fortwall.add', 'Fort Wall', {'REGISTER', 'UNDO'}
    corners: IntProperty(name='Corners', default=5, min=3, max=24)
    radius: FloatProperty(name='Radius', default=40, min=5, subtype='DISTANCE')
    bastions: BoolProperty(name='Bastions at Corners', default=True)

    @classmethod
    def poll(cls, ctx): return ctx.mode == 'OBJECT'

    def execute(self, ctx):
        r, n = self.radius, self.corners
        ob = gen.new_curve('Fort_Wall', [(r * math.cos(a), r * math.sin(a), 0, 1)
                                         for a in (math.pi / 2 + gen.TAU * i / n for i in range(n))])
        ctx.collection.objects.link(ob)
        ob.location = ctx.scene.cursor.location
        for o in ctx.selected_objects: o.select_set(False)
        ob.select_set(True); ctx.view_layer.objects.active = ob
        md = gen.attach(ob)
        if self.bastions:
            for p in ob.data.splines[0].bezier_points: gen.add_part(md, 'Bastions', ob.location + p.co)
        return {'FINISHED'}


class FORTWALL_OT_convert(bpy.types.Operator):
    """Make the selected curves fort walls: point radius sets crown width, point Z raises the wall"""
    bl_idname, bl_label, bl_options = 'fortwall.convert', 'Make Fort Wall', {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, ctx):
        return ctx.mode == 'OBJECT' and any(o.type == 'CURVE' and not gen.fort_modifier(o) for o in ctx.selected_objects)

    def execute(self, ctx):
        for o in ctx.selected_objects:
            if o.type == 'CURVE' and not gen.fort_modifier(o): gen.attach(o)
        return {'FINISHED'}


class FORTWALL_OT_add_part(bpy.types.Operator):
    """Add a part: one at each selected control point in Edit Mode (stairs follow the curve), else at the 3D cursor"""
    bl_idname, bl_label, bl_options = 'fortwall.add_part', 'Add Part', {'REGISTER', 'UNDO'}
    kind: EnumProperty(name='Part', items=KINDS)

    @classmethod
    def poll(cls, ctx): return find_fort(ctx) is not None

    def execute(self, ctx):
        ob, md, _ = find_fort(ctx)
        mw = ob.matrix_world
        if ctx.mode == 'EDIT_CURVE':
            sel = selected_points(ob)
            if not sel:
                self.report({'WARNING'}, 'Select control points first'); return {'CANCELLED'}
            for _, co, t in sel:
                t = mw.to_3x3() @ t
                gen.add_part(md, self.kind, mw @ Vector((co.x, co.y, 0)), math.atan2(t.y, t.x))
            return {'FINISHED'}
        c = ctx.scene.cursor.location
        e = gen.add_part(md, self.kind, (c.x, c.y, mw.translation.z))
        for o in ctx.selected_objects: o.select_set(False)
        e.select_set(True); ctx.view_layer.objects.active = e  # ready for G / R / S
        return {'FINISHED'}


class FORTWALL_OT_rebuild(bpy.types.Operator):
    """Rebuild the FortWall node group from the add-on (keeps every modifier value). A big fort can freeze Blender for minutes"""
    bl_idname, bl_label, bl_options = 'fortwall.rebuild', 'Rebuild Nodes', {'REGISTER', 'UNDO'}

    def execute(self, ctx):
        gen.build_group(); return {'FINISHED'}


class FORTWALL_OT_check(bpy.types.Operator):
    """Check the fort is one closed, outward-facing solid and its bricks were laid"""
    bl_idname, bl_label = 'fortwall.check', 'Check Solid'

    @classmethod
    def poll(cls, ctx): return find_fort(ctx) is not None

    def execute(self, ctx):
        try: self.report({'INFO'}, str(gen.check(find_fort(ctx)[0])))
        except AssertionError as e: self.report({'ERROR'}, str(e))
        return {'FINISHED'}


class VIEW3D_PT_fortwall(bpy.types.Panel):
    bl_space_type, bl_region_type, bl_category, bl_label = 'VIEW_3D', 'UI', 'Fort', 'FortWall'

    def draw(self, ctx):
        L = self.layout
        fort = find_fort(ctx)
        if not fort:
            L.operator('fortwall.add', icon='ADD')
            L.operator('fortwall.convert', icon='CURVE_BEZCURVE')
            return
        ob, md, kind = fort
        L.label(text=ob.name, icon='CURVE_BEZCURVE')
        edit = ctx.mode == 'EDIT_CURVE'
        row = L.row(align=True)
        for k, label, _ in KINDS: row.operator('fortwall.add_part', text=label, icon=ICONS[k]).kind = k
        L.label(text='Adds at selected points' if edit else 'Adds at the 3D cursor', icon='INFO')

        box = L.box()
        if edit:
            sel = selected_points(ob)
            if len(sel) == 1:
                p = sel[0][0]
                box.prop(p, 'radius', text='Crown Width ×')
                box.prop(p, 'co', index=2, text='Wall Height +')
            else:
                box.label(text=f'{len(sel)} points: Alt+S width, G Z height')
            row = box.row(align=True)
            row.operator('curve.handle_type_set', text='Sharp').type = 'VECTOR'
            row.operator('curve.handle_type_set', text='Smooth').type = 'AUTOMATIC'
        elif kind:
            e = ctx.active_object
            box.label(text=e.name, icon=ICONS[kind])
            if kind == 'Bastions':
                box.prop(e, 'scale', index=0, text='Radius')
                box.prop(e, 'location', index=2, text='Platform Height +')
            elif kind == 'Gates':
                box.prop(e, 'scale', index=0, text='Half Width')
                box.prop(e, 'scale', index=2, text='Height ×')
            else:
                box.prop(e, 'scale', index=0, text='Width')
                box.prop(e, 'rotation_euler', index=2, text='Direction')
        else:
            box.label(text='Tab: edit the wall curve', icon='EDITMODE_HLT')

        row = L.row(align=True)
        row.prop(md, 'show_in_editmode', text='Live Edit', toggle=True)
        row.prop(gen.mod_input(md, 'Bricks'), 'value', text='Bricks', toggle=True)
        for it in md.node_group.interface.items_tree:
            if it.item_type != 'PANEL': continue
            head, body = L.panel('fortwall_' + it.name, default_closed=it.default_closed)
            head.label(text=it.name)
            if body:
                for s in it.interface_items:
                    body.prop(getattr(md.properties.inputs, s.identifier), 'value', text=s.name)
        row = L.row(align=True)
        row.operator('fortwall.check', icon='CHECKMARK')
        row.operator('fortwall.rebuild', icon='FILE_REFRESH')


def menu_add(self, ctx):
    if ctx.mode == 'OBJECT': self.layout.operator('fortwall.add', icon='MOD_BUILD')


classes = (FORTWALL_OT_add, FORTWALL_OT_convert, FORTWALL_OT_add_part, FORTWALL_OT_rebuild, FORTWALL_OT_check,
           VIEW3D_PT_fortwall)


def register():
    for c in classes: bpy.utils.register_class(c)
    bpy.types.VIEW3D_MT_curve_add.append(menu_add)


def unregister():
    bpy.types.VIEW3D_MT_curve_add.remove(menu_add)
    for c in reversed(classes): bpy.utils.unregister_class(c)
