"""Helpers for the room models built in Blender (run headless: blender --background --python <model>.py).

Conventions
- Metres, Z up, the model stands on the floor at the origin. Blender -Y is the model's front (it becomes +z in the game).
- A material's NAME is the key of the game material that part gets (oak, linen, duvet...). The colours here are only
  for the check render: the game supplies the real, tiling materials, so close-ups stay sharp at toy-car scale.
- UVs are in metres (real size); the game scales them to each material's tile size.
- The colour attribute 'Col' holds baked ambient occlusion (soft shade in folds and under things).
Outputs go to D:/crust-rush/blender/<name>/: <name>.blend, <name>.glb, <name>_check.png
"""
import bpy, bmesh, math, os, sys
import numpy as np
from mathutils import Vector

OUT = 'D:/crust-rush/blender'


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    s = bpy.context.scene
    s.unit_settings.system = 'METRIC'
    s.render.engine = 'CYCLES'
    try:
        p = bpy.context.preferences.addons['cycles'].preferences
        p.compute_device_type = 'OPTIX'; p.get_devices()
        for d in p.devices: d.use = d.type != 'CPU'
        s.cycles.device = 'GPU'
    except Exception as e:
        print('GPU not set:', e)
    return s


def mat(name, col, rough=.6, metal=0.0, sheen=0.0):
    m = bpy.data.materials.get(name)
    if m: return m
    m = bpy.data.materials.new(name)
    try: m.use_nodes = True
    except Exception: pass
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*col, 1)
    b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metal
    if sheen: b.inputs['Sheen Weight'].default_value = sheen
    return m


def hexcol(h):
    """sRGB hex -> linear rgb"""
    h = h.lstrip('#'); c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4 for v in c)


def active(o):
    bpy.ops.object.select_all(action='DESELECT'); o.select_set(True); bpy.context.view_layer.objects.active = o


def apply_scale(o):
    active(o); bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)


def smooth(o):
    for p in o.data.polygons: p.use_smooth = True


def bevel(o, width, seg=3, angle=35):
    m = o.modifiers.new('bevel', 'BEVEL'); m.width = width; m.segments = seg; m.limit_method = 'ANGLE'; m.angle_limit = math.radians(angle)
    m.harden_normals = False
    w = o.modifiers.new('wn', 'WEIGHTED_NORMAL'); w.keep_sharp = True
    smooth(o)


def box(name, size, loc, m, bev=.004, seg=3):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object; o.name = name; o.scale = size; apply_scale(o); o.data.materials.append(m)
    if bev: bevel(o, bev, seg)
    return o


def frustum(name, r1, r2, h, loc, m, verts=28, bev=.002):
    """a tapered leg: radius r1 at the top, r2 at the bottom, standing on loc"""
    bpy.ops.mesh.primitive_cone_add(vertices=verts, radius1=r2, radius2=r1, depth=h, location=(loc[0], loc[1], loc[2] + h / 2))
    o = bpy.context.object; o.name = name; o.data.materials.append(m)
    if bev: bevel(o, bev, 2, 50)
    smooth(o)
    return o


def grid(name, sx, sy, nx, ny, loc, m):
    """a flat sheet sx by sy metres with nx by ny squares; its UVs are in metres"""
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=nx, y_subdivisions=ny, size=1, location=loc)
    o = bpy.context.object; o.name = name; o.scale = (sx, sy, 1); apply_scale(o); o.data.materials.append(m)
    uv_scale(o, sx, sy); smooth(o)
    return o


def uv_scale(o, su, sv):
    uv = o.data.uv_layers.active.data; a = np.zeros(len(uv) * 2, dtype=np.float32); uv.foreach_get('uv', a)
    a = a.reshape(-1, 2); a[:, 0] *= su; a[:, 1] *= sv; uv.foreach_set('uv', a.ravel())


def uv_box(o):
    """real-size UVs for hard parts: each face is laid flat along the axis it faces, 1 unit = 1 metre"""
    me = o.data
    if not me.uv_layers: me.uv_layers.new(name='UVMap')
    uv = me.uv_layers.active.data
    for p in me.polygons:
        n = p.normal; ax = max(range(3), key=lambda i: abs(n[i]))
        for li in p.loop_indices:
            v = me.vertices[me.loops[li].vertex_index].co
            uv[li].uv = (v.y, v.z) if ax == 0 else (v.x, v.z) if ax == 1 else (v.x, v.y)


def rumple(o, amp, scale, seed=1):
    """small random heights before a sheet is dropped, so it lands with folds instead of dead flat"""
    rs = np.random.RandomState(seed); ph = rs.rand(6) * 6.283
    for v in o.data.vertices:
        x, y = v.co.x / scale, v.co.y / scale
        v.co.z += amp * (math.sin(x * 2.1 + ph[0]) * math.cos(y * 1.7 + ph[1]) + .6 * math.sin(x * 4.3 + y * 3.1 + ph[2]) + .4 * math.cos(y * 6.7 - x * 2.9 + ph[3]))


def quilt(o, cell, puff):
    """a quilt's stitched squares: the filling stands up between the stitch lines (uses the sheet's own UVs, in metres)"""
    me = o.data; uv = me.uv_layers.active.data; h = {}
    for l in me.loops:
        u, v = uv[l.index].uv
        h[l.vertex_index] = puff * (abs(math.sin(math.pi * u / cell)) * abs(math.sin(math.pi * v / cell))) ** .45
    for v in me.vertices: v.co += v.normal * h.get(v.index, 0)


def round_corners(o, r):
    """cut the four corners of a flat sheet to a radius: a square corner stands out as a stiff point when the sheet hangs"""
    xs = [v.co.x for v in o.data.vertices]; ys = [v.co.y for v in o.data.vertices]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    bm = bmesh.new(); bm.from_mesh(o.data); kill = []
    for v in bm.verts:
        cx = x0 + r if v.co.x < x0 + r else x1 - r if v.co.x > x1 - r else None
        cy = y0 + r if v.co.y < y0 + r else y1 - r if v.co.y > y1 - r else None
        if cx is not None and cy is not None and math.hypot(v.co.x - cx, v.co.y - cy) > r: kill.append(v)
    bmesh.ops.delete(bm, geom=kill, context='VERTS'); bm.to_mesh(o.data); bm.free(); o.data.update()


def relax(o, factor=.5, repeat=2):
    """take the jitter out of a simulated sheet"""
    m = o.modifiers.new('relax', 'SMOOTH'); m.factor = factor; m.iterations = repeat
    return freeze(o)


def freeze(o):
    """replace the object's mesh with what its modifiers (and any simulation, at the current frame) make of it"""
    dg = bpy.context.evaluated_depsgraph_get(); me = bpy.data.meshes.new_from_object(o.evaluated_get(dg))
    old = o.data; o.modifiers.clear(); o.data = me; bpy.data.meshes.remove(old)
    return o


def cloth(o, mass=.3, tension=15, bending=5, self_col=True, dist=.006, quality=8, pressure=0, gravity=1.0, damp=5):
    m = o.modifiers.new('cloth', 'CLOTH'); s = m.settings
    s.quality = quality; s.mass = mass
    s.tension_stiffness = tension; s.compression_stiffness = tension; s.shear_stiffness = tension * .5; s.bending_stiffness = bending
    s.tension_damping = damp; s.compression_damping = damp; s.shear_damping = damp; s.bending_damping = .5
    s.effector_weights.gravity = gravity
    if pressure:
        s.use_pressure = True; s.uniform_pressure_force = pressure
    c = m.collision_settings; c.collision_quality = 4; c.distance_min = dist
    c.use_self_collision = self_col; c.self_distance_min = dist
    return m


def collider(o, outer=.006, friction=25):
    o.modifiers.new('collision', 'COLLISION'); o.collision.thickness_outer = outer; o.collision.thickness_inner = .02; o.collision.cloth_friction = friction


def simulate(frames):
    s = bpy.context.scene; s.frame_start = 1; s.frame_end = frames
    for f in range(1, frames + 1): s.frame_set(f)


def solidify(o, t, offset=1.0):
    m = o.modifiers.new('solid', 'SOLIDIFY'); m.thickness = t; m.offset = offset; m.use_rim = True; m.use_even_offset = True


def bake_ao(objs, samples=48):
    """ambient occlusion into the colour attribute 'Col' of each object (every visible object casts)"""
    s = bpy.context.scene; s.cycles.samples = samples; s.cycles.use_denoising = False
    for o in objs:
        me = o.data
        if 'Col' not in me.color_attributes: me.color_attributes.new('Col', 'FLOAT_COLOR', 'POINT')   # one value per vertex: per-corner colours would split every vertex on export
        me.color_attributes.active_color = me.color_attributes['Col']
        try: me.color_attributes.render_color_index = list(me.color_attributes).index(me.color_attributes['Col'])
        except Exception: pass
        active(o)
        bpy.ops.object.bake(type='AO', target='VERTEX_COLORS')


def soften_ao(o, blur=2, lift=.3):
    """smooth the baked shade across neighbouring vertices and lighten it: on tight folds the raw bake is nearly black
    and changes from one vertex to the next, which shows as dark jagged streaks"""
    me = o.data; ca = me.color_attributes['Col']; n = len(me.vertices)
    c = np.zeros(n * 4, dtype=np.float32); ca.data.foreach_get('color', c); c = c.reshape(n, 4)
    e = np.zeros(len(me.edges) * 2, dtype=np.int32); me.edges.foreach_get('vertices', e); e = e.reshape(-1, 2)
    for _ in range(blur):
        acc = c[:, :3].copy(); cnt = np.ones(n, dtype=np.float32)
        np.add.at(acc, e[:, 0], c[e[:, 1], :3]); np.add.at(acc, e[:, 1], c[e[:, 0], :3])
        np.add.at(cnt, e[:, 0], 1); np.add.at(cnt, e[:, 1], 1)
        c[:, :3] = acc / cnt[:, None]
    c[:, :3] = c[:, :3] + (1 - c[:, :3]) * lift
    ca.data.foreach_set('color', c.ravel()); me.update()


def check_render(name, objs, size=(1600, 1000), views=((35, 22),), samples=96, dist=None):
    """a studio picture of the model on its own: grey floor, a warm key light, soft sky light"""
    s = bpy.context.scene
    lo = Vector((1e9,) * 3); hi = Vector((-1e9,) * 3)
    for o in objs:
        for c in o.bound_box:
            w = o.matrix_world @ Vector(c)
            lo = Vector(map(min, lo, w)); hi = Vector(map(max, hi, w))
    ctr = (lo + hi) / 2; rad = (hi - lo).length / 2
    bpy.ops.mesh.primitive_plane_add(size=rad * 14, location=(ctr.x, ctr.y, 0)); fl = bpy.context.object; fl.name = '_floor'
    fl.data.materials.append(mat('_floor', (.55, .53, .5), .7))
    w = bpy.data.worlds.new('w'); s.world = w
    try: w.use_nodes = True
    except Exception: pass
    bg = w.node_tree.nodes['Background']; bg.inputs[0].default_value = (.75, .82, .95, 1); bg.inputs[1].default_value = .55
    sun = bpy.data.lights.new('sun', 'SUN'); sun.energy = 4.2; sun.angle = math.radians(2.5); sun.color = (1, .93, .82)
    so = bpy.data.objects.new('sun', sun); s.collection.objects.link(so); so.rotation_euler = (math.radians(52), 0, math.radians(35))
    cam = bpy.data.cameras.new('cam'); cam.lens = 55; co = bpy.data.objects.new('cam', cam); s.collection.objects.link(co); s.camera = co
    s.render.resolution_x, s.render.resolution_y = size; s.cycles.samples = samples; s.cycles.use_denoising = True
    s.view_settings.view_transform = 'Standard' if 'Standard' in [e.identifier for e in type(s.view_settings).bl_rna.properties['view_transform'].enum_items] else s.view_settings.view_transform
    outs = []
    for i, (az, el) in enumerate(views):
        d = dist or rad * 3.6; a = math.radians(az); e = math.radians(el)
        co.location = ctr + Vector((math.sin(a) * math.cos(e) * d, -math.cos(a) * math.cos(e) * d, math.sin(e) * d))
        co.rotation_euler = (ctr - co.location).to_track_quat('-Z', 'Y').to_euler()
        p = f'{OUT}/{name}/{name}_check{i}.png'; s.render.filepath = p; bpy.ops.render.render(write_still=True); outs.append(p)
    bpy.data.objects.remove(fl); bpy.data.objects.remove(so); bpy.data.objects.remove(co)
    return outs


def finish_model(name, parts, dist, lift=.3, views=((-30, 18),), floor=True, after=None):
    """the last steps every model shares: apply transforms and modifiers, real-size UVs (unless a part is marked keep_uv),
    baked shade with a floor underneath, a check picture, the GLB"""
    os.makedirs(f'{OUT}/{name}', exist_ok=True)
    bpy.context.view_layer.update()
    for o in parts:
        active(o); bpy.ops.object.transform_apply(location=True, rotation=True, scale=True); freeze(o); smooth(o)
        if not o.get('keep_uv'): uv_box(o)
    fl = None
    if floor:
        bpy.ops.mesh.primitive_plane_add(size=8, location=(0, 0, -.0005)); fl = bpy.context.object; fl.data.materials.append(mat('_floor', (.5, .5, .5)))
    bake_ao(parts)
    if fl: bpy.data.objects.remove(fl)
    for o in parts: soften_ao(o, 1, lift)
    for o in parts: tint(o)
    if after: after(parts)                                  # (a model's own last touch before the picture and the export: custom normals, say)
    print('CHECK', check_render(name, parts, views=views, dist=dist))
    export(name, parts)


def tint(o):
    """multiply the baked shade by a colour: o['tint'] = (r, g, b) for the whole part (one board a little darker than the
    next), and/or a per-vertex colour layer called 'Tint' (leaves of many greens). The game multiplies its material by this."""
    me = o.data; t = o.get('tint'); lay = me.color_attributes.get('Tint')
    if t is None and lay is None: return
    n = len(me.vertices); c = np.zeros(n * 4, dtype=np.float32); me.color_attributes['Col'].data.foreach_get('color', c); c = c.reshape(n, 4)
    if t is not None: c[:, :3] *= np.array(list(t), dtype=np.float32)
    if lay is not None:
        q = np.zeros(n * 4, dtype=np.float32); lay.data.foreach_get('color', q); c[:, :3] *= q.reshape(n, 4)[:, :3]
    me.color_attributes['Col'].data.foreach_set('color', c.ravel()); me.update()


def rod(name, r, length, loc, m, axis='X', verts=14):
    """a round bar along X, Y or Z, centred on loc"""
    rot = {'X': (0, math.pi / 2, 0), 'Y': (math.pi / 2, 0, 0), 'Z': (0, 0, 0)}[axis]
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=length, location=loc, rotation=rot)
    o = bpy.context.object; o.name = name; o.data.materials.append(m); smooth(o); return o


def bar(name, p0, p1, r0, r1, m, verts=12):
    """a tapered round bar from point p0 (radius r0) to point p1 (radius r1)"""
    a = Vector(p0); b = Vector(p1); d = b - a
    bpy.ops.mesh.primitive_cone_add(vertices=verts, radius1=r0, radius2=r1, depth=d.length, location=(a + b) / 2)
    o = bpy.context.object; o.name = name; o.rotation_euler = d.to_track_quat('Z', 'Y').to_euler(); o.data.materials.append(m); smooth(o); return o


def tube(name, pts, r, m, fillet=.03, verts=10, steps=5, caps=True):
    """a round tube along the points `pts`, its corners rounded to radius `fillet` (a pipe, a conduit, a bent rail)"""
    P = [Vector(p) for p in pts]; out = [P[0]]
    for i in range(1, len(P) - 1):
        a, b, c = P[i - 1], P[i], P[i + 1]; u = (a - b); v = (c - b); f = min(fillet, u.length * .45, v.length * .45)
        if f < 1e-5 or u.normalized().dot(v.normalized()) < -.9999: out.append(b); continue
        p0 = b + u.normalized() * f; p1 = b + v.normalized() * f
        for k in range(steps + 1):
            t = k / steps; out.append((1 - t) ** 2 * p0 + 2 * t * (1 - t) * b + t * t * p1)
    out.append(P[-1])
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '3D'; sp = cu.splines.new('POLY'); sp.points.add(len(out) - 1)
    for q, p in zip(sp.points, out): q.co = (*p, 1)
    cu.bevel_depth = r; cu.bevel_resolution = max(1, verts // 4 - 1); cu.use_fill_caps = caps
    o = bpy.data.objects.new(name, cu); bpy.context.scene.collection.objects.link(o)
    active(o); bpy.ops.object.convert(target='MESH'); o = bpy.context.object; o.data.materials.append(m); smooth(o)
    return o


def prism(name, poly, axis, a0, a1, m, bev=0, seg=1):
    """a flat outline pushed straight through: `poly` is a list of 2D points, extruded along `axis` from a0 to a1.
    axis 'X': the points are (y, z); 'Y': (x, z); 'Z': (x, y). No rotations anywhere, so nothing can end up on the wrong axis
    (roof slopes, lapped boards, gutters, barge boards)."""
    put = {'X': lambda u, v, a: (a, u, v), 'Y': lambda u, v, a: (u, a, v), 'Z': lambda u, v, a: (u, v, a)}[axis]
    n = len(poly); V = [put(u, v, a0) for u, v in poly] + [put(u, v, a1) for u, v in poly]
    F = [tuple(range(n)), tuple(range(n, 2 * n))] + [(i, (i + 1) % n, n + (i + 1) % n, n + i) for i in range(n)]
    me = bpy.data.meshes.new(name); me.from_pydata(V, [], F); me.update()
    o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o); me.materials.append(m)
    bm = bmesh.new(); bm.from_mesh(me); bmesh.ops.recalc_face_normals(bm, faces=bm.faces); bm.to_mesh(me); bm.free()
    if bev: bevel(o, bev, seg)
    return o


def turn(o, deg, at=(0, 0, 0)):
    """turn an object about the vertical through the origin by `deg`, then move it by `at`; the transform is applied at once"""
    from mathutils import Matrix
    bpy.context.view_layer.update()
    o.matrix_world = Matrix.Translation(Vector(at)) @ Matrix.Rotation(math.radians(deg), 4, 'Z') @ o.matrix_world
    active(o); bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    return o


# the planks of the timber scan (blender/tex/planks.jpg, 1 m square, boards running across it): each (from, to) is one
# board's band, as fractions from the picture's bottom, clear of the joints
PLANK_BANDS = [(1 - .205, 1 - .07), (1 - .33, 1 - .225), (1 - .44, 1 - .35), (1 - .63, 1 - .50), (1 - .765, 1 - .655), (1 - .92, 1 - .805)]


def uv_plank(o, along, across, band, shift=0.0):
    """give a board its own plank of the scan: its length (axis `along`, 0 1 or 2) runs along the picture at real size,
    its width (axis `across`) fills one band. The game uses these with a tile of 100 cm (pk leaves them as they are)."""
    me = o.data
    if not me.uv_layers: me.uv_layers.new(name='UVMap')
    uv = me.uv_layers.active.data; lo, hi = bounds(o); w0, w1 = lo[across], hi[across]; b0, b1 = PLANK_BANDS[band % len(PLANK_BANDS)]
    for l in me.loops:
        c = o.matrix_world @ me.vertices[l.vertex_index].co
        uv[l.index].uv = (c[along] + shift, b0 + (c[across] - w0) / max(1e-6, w1 - w0) * (b1 - b0))
    o['keep_uv'] = 1
    return o


def lathe(name, prof, seg, m, loc=(0, 0, 0)):
    """a shape turned about the vertical: `prof` is a list of (radius, height) from one end to the other (a pot, a can, a hat).
    A radius of 0 closes the end."""
    V = []; F = []; n = len(prof)
    for (r, z) in prof:
        for k in range(seg): a = 2 * math.pi * k / seg; V.append((loc[0] + r * math.cos(a), loc[1] + r * math.sin(a), loc[2] + z))
    for i in range(n - 1):
        for k in range(seg): F.append((i * seg + k, i * seg + (k + 1) % seg, (i + 1) * seg + (k + 1) % seg, (i + 1) * seg + k))
    me = bpy.data.meshes.new(name); me.from_pydata(V, [], F); me.update()
    bm = bmesh.new(); bm.from_mesh(me); bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6); bmesh.ops.recalc_face_normals(bm, faces=bm.faces); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o); me.materials.append(m); smooth(o)
    return o


def ball(name, r, loc, m, scale=(1, 1, 1), seg=16, rings=10):
    """a ball, or with `scale` an egg or a bun shape, centred on loc"""
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, segments=seg, ring_count=rings, location=loc)
    o = bpy.context.object; o.name = name; o.scale = scale; apply_scale(o); o.data.materials.append(m); smooth(o)
    return o


def mesh(name, V, F, m, smooth_=True):
    """a part from its corners and faces, its faces turned to look outward"""
    me = bpy.data.meshes.new(name); me.from_pydata([tuple(v) for v in V], [], F); me.update()
    bm = bmesh.new(); bm.from_mesh(me); bmesh.ops.recalc_face_normals(bm, faces=bm.faces); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o); me.materials.append(m)
    if smooth_: smooth(o)
    return o


def bounds(o):
    """world-space box of an object: (lo, hi) as Vectors (modifiers not applied)"""
    vs = [o.matrix_world @ v.co for v in o.data.vertices]
    return Vector((min(v.x for v in vs), min(v.y for v in vs), min(v.z for v in vs))), Vector((max(v.x for v in vs), max(v.y for v in vs), max(v.z for v in vs)))


def joined(a, b, slack=.0005):
    """do two parts' boxes meet on all three axes? Prints a warning when they only come near: a gap of a few millimetres
    shows as a part floating free once the model is in the game"""
    bpy.context.view_layer.update()
    la, ha = bounds(a); lb, hb = bounds(b); gap = max(max(la[i], lb[i]) - min(ha[i], hb[i]) for i in range(3))
    if gap > slack: print(f'GAP WARNING {a.name} <-> {b.name}: {gap * 1000:.1f} mm apart')
    return gap <= slack


def export(name, objs):
    os.makedirs(f'{OUT}/{name}', exist_ok=True)
    for o in objs:
        active(o); bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bpy.ops.wm.save_as_mainfile(filepath=f'{OUT}/{name}/{name}.blend')
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs: o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=f'{OUT}/{name}/{name}.glb', export_format='GLB', use_selection=True, export_apply=True, export_yup=True,
                              export_vertex_color='ACTIVE', export_all_vertex_colors=False, export_active_vertex_color_when_no_material=True,
                              export_texcoords=True, export_normals=True, export_materials='EXPORT', export_image_format='NONE')
    tris = sum(len(p.vertices) - 2 for o in objs for p in o.data.polygons)
    print('EXPORTED', name, len(objs), 'objects', sum(len(o.data.vertices) for o in objs), 'verts', tris, 'tris')
