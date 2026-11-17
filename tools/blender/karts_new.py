"""Four new kart bodies, built here from scratch (no downloaded model), for the car pipeline (car_convert.py -> car_pack.py).
The owner, 2026-11-17: "Let's work on new kart designs and really make them unique and try using blender for some of them so that they
can look better". Each has a silhouette none of the nine karts has, read from the chase camera (behind and a little above):
  rollpin  Rolling Pin    a retro open-wheel racer: the body a long wooden rolling pin, its handles fore and aft, wheels out on
                          struts, a pizza-peel rear wing
  grater   Grater         a chunky utility kart: a tall box grater behind the driver (rows of grating), a roll-hoop handle, bull bar
                          and lamps, fat off-road tyres
  comet    Calzone Comet  a low crescent streamliner: a folded calzone shell with a crimped edge, a bubble canopy, a tail fin
  oilcan   Oil Can        a dragster: a spout nose on a long rail, the can as the engine with its cap as a scoop, huge rear slicks,
                          little front wheels, a wheelie bar
Materials are named for what car_rules.py makes them (K_PAINT the player's paint, K_DARK, K_STRIPE, K_CHROME, K_METAL, K_GLASS,
K_LIGHT, K_TAIL, K_SEAT, K_WOOD, K_RED, K_WHITE, K_TYRE and K_RIM the wheels). Front along -Y, x across, z up, in metres (the
converter scales to the game's 12.2 units). Writes D:/crust-rush/scratch/cars_in/karts/<id>.glb.
usage: blender --background --python karts_new.py -- [ids...]"""
import sys, os, math
import bpy, bmesh
from mathutils import Vector, Matrix

OUT = 'D:/crust-rush/scratch/cars_in/karts'
COL = {'K_PAINT': (0.85, 0.2, 0.12), 'K_DARK': (0.05, 0.05, 0.06), 'K_STRIPE': (0.95, 0.9, 0.8), 'K_CHROME': (0.9, 0.9, 0.92), 'K_METAL': (0.6, 0.62, 0.65),
       'K_GLASS': (0.2, 0.3, 0.4), 'K_LIGHT': (1, 1, 0.9), 'K_TAIL': (0.9, 0.05, 0.05), 'K_SEAT': (0.15, 0.1, 0.08), 'K_WOOD': (0.72, 0.5, 0.3),
       'K_RED': (0.8, 0.1, 0.08), 'K_WHITE': (0.95, 0.95, 0.95), 'K_TYRE': (0.03, 0.03, 0.03), 'K_RIM': (0.7, 0.7, 0.72)}


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def mat(name):
    m = bpy.data.materials.get(name)
    if m is None:
        m = bpy.data.materials.new(name); m.use_nodes = True
        m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (*COL[name], 1)
    return m


def finish(o, m, smooth=True, bevel=0.0, sub=0, seg=3):
    o.data.materials.clear(); o.data.materials.append(mat(m))
    if bevel > 0:
        b = o.modifiers.new('bv', 'BEVEL'); b.width = bevel; b.segments = seg; b.limit_method = 'ANGLE'
    if sub:
        s = o.modifiers.new('sb', 'SUBSURF'); s.levels = sub; s.render_levels = sub
    if smooth:
        for p in o.data.polygons:
            p.use_smooth = True
    return o


def box(name, m, c, h, bevel=0.02, sub=0):
    """a box: centre c, HALF extents h (size=2 cube, scale = half extent)"""
    bpy.ops.mesh.primitive_cube_add(size=2, location=c)
    o = bpy.context.active_object; o.name = name; o.scale = h
    bpy.ops.object.transform_apply(scale=True)
    return finish(o, m, smooth=sub > 0, bevel=bevel, sub=sub)


def cyl(name, m, a, b, r, r2=None, n=32, cap=True, bevel=0.0):
    """a cylinder (or cone) from point a to point b, built with bmesh: no rotations to get wrong"""
    a, b = Vector(a), Vector(b); d = b - a; L = d.length; f = d / L
    up = Vector((0, 0, 1)) if abs(f.z) < 0.99 else Vector((1, 0, 0))
    rx = f.cross(up).normalized(); ry = rx.cross(f).normalized()
    r2 = r if r2 is None else r2
    me = bpy.data.meshes.new(name); o = bpy.data.objects.new(name, me); bpy.context.collection.objects.link(o)
    bm = bmesh.new(); ring = []
    for end, rr in ((a, r), (b, r2)):
        ring.append([bm.verts.new(end + (rx * math.cos(2 * math.pi * i / n) + ry * math.sin(2 * math.pi * i / n)) * rr) for i in range(n)])
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((ring[0][i], ring[0][j], ring[1][j], ring[1][i]))
    if cap:
        bm.faces.new(list(reversed(ring[0]))); bm.faces.new(ring[1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.to_mesh(me); bm.free()
    finish(o, m, smooth=True, bevel=bevel, seg=2)
    if bevel:
        for p in o.data.polygons:
            p.use_smooth = True
    return o


def sphere(name, m, c, s, seg=32):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=seg // 2, location=c)
    o = bpy.context.active_object; o.name = name; o.scale = s
    bpy.ops.object.transform_apply(scale=True)
    return finish(o, m)


def wheel(tag, x, y, r, w, hub='K_RIM', spokes=5):
    """a tyre (a thick ring with rounded shoulders) and a rim with spokes, the axle along x"""
    s = 1 if x > 0 else -1
    me = bpy.data.meshes.new(tag + '_tyre'); o = bpy.data.objects.new(tag + '_tyre', me); bpy.context.collection.objects.link(o)
    bm = bmesh.new(); n = 40; prof = []
    for k in range(9):           # the tyre's cross-section: a rounded rectangle from the bead round the tread and back
        t = k / 8
        ang = math.pi * t
        prof.append((x + s * 0 + (-w / 2 + w * t) * 1.0, r - (w * 0.18) * (math.sin(ang) ** 6) * 0 - (0.06 * r) * (1 - math.sin(ang)) ))
    rin = r * 0.66
    pts = [(x - w / 2, rin), (x - w / 2, r * 0.88), (x - w * 0.42, r * 0.97), (x - w * 0.25, r), (x + w * 0.25, r), (x + w * 0.42, r * 0.97), (x + w / 2, r * 0.88), (x + w / 2, rin)]
    rings = []
    for (px, pr) in pts:
        rings.append([bm.verts.new((px, y + math.cos(2 * math.pi * i / n) * pr, r + math.sin(2 * math.pi * i / n) * pr)) for i in range(n)])
    for a in range(len(rings) - 1):
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new((rings[a][i], rings[a][j], rings[a + 1][j], rings[a + 1][i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:]); bm.to_mesh(me); bm.free()
    finish(o, 'K_TYRE')
    # the rim: a dish and spokes inside the tyre
    cyl(tag + '_rimdish', hub, (x - s * w * 0.18, y, r), (x + s * w * 0.32, y, r), rin * 0.98, n=32)
    cyl(tag + '_hub', hub, (x + s * w * 0.3, y, r), (x + s * w * 0.46, y, r), rin * 0.28, n=20)
    for k in range(spokes):
        a = 2 * math.pi * k / spokes
        p = Vector((x + s * w * 0.38, y + math.cos(a) * rin * 0.85, r + math.sin(a) * rin * 0.85))
        cyl(tag + '_spoke%d' % k, hub, (x + s * w * 0.38, y, r), tuple(p), 0.035 * r / 0.3, n=10)


def fender(name, m, x, y, r, w, a0=0.25, a1=2.9, t=0.03):
    """a curved fender over a wheel: a band of arc round the axle (x across), from angle a0 to a1 above it, t thick"""
    me = bpy.data.meshes.new(name); o = bpy.data.objects.new(name, me); bpy.context.collection.objects.link(o)
    bm = bmesh.new(); n = 20; rows = []
    for rr in (r, r + t):
        for xx in (x - w / 2, x + w / 2):
            rows.append([bm.verts.new((xx, y - math.cos(a0 + (a1 - a0) * i / n) * rr, r * 0.0 + rr * math.sin(a0 + (a1 - a0) * i / n) + YZ[0])) for i in range(n + 1)])
    for A, B in ((0, 1), (2, 3), (0, 2), (1, 3)):
        for i in range(n):
            bm.faces.new((rows[A][i], rows[A][i + 1], rows[B][i + 1], rows[B][i]))
    for A, B in ((0, 1), (2, 3)):
        pass
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:]); bm.to_mesh(me); bm.free()
    return finish(o, m)


YZ = [0.0]


def export(cid):
    os.makedirs(OUT, exist_ok=True)
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.gltf(filepath=f'{OUT}/{cid}.glb', export_format='GLB', use_selection=True, export_apply=True, export_yup=True)
    print('[karts] wrote', cid)


# ------------------------------------------------------------------ Rolling Pin: a retro open-wheel racer
def rollpin():
    reset()
    R, zc = 0.3, 0.46
    # the pin itself: long, round, its ends rounded into the handles' collars
    cyl('pin', 'K_PAINT', (0, -1.05, zc), (0, 1.0, zc), R, n=48, bevel=0.06)
    for y0, y1 in ((-1.05, -1.12), (1.0, 1.07)):
        cyl('collar%.0f' % (y0 * 10), 'K_WOOD', (0, y0, zc), (0, y1, zc), R * 0.7, n=40, bevel=0.02)
    # handles fore and aft, turned wood with knobs
    for sg in (-1, 1):
        y0 = -1.12 if sg < 0 else 1.07
        cyl('handle%d' % sg, 'K_WOOD', (0, y0, zc), (0, y0 + sg * 0.42, zc), 0.1, 0.12, n=32)
        sphere('knob%d' % sg, 'K_WOOD', (0, y0 + sg * 0.5, zc), (0.15, 0.13, 0.15))
    # the grain: a few thin darker bands round the pin (wood rings, paint's stripes)
    for k, yy in enumerate((-0.7, -0.35, 0.55, 0.8)):
        cyl('band%d' % k, 'K_STRIPE', (0, yy - 0.02, zc), (0, yy + 0.02, zc), R + 0.006, n=48)
    # the cockpit: a padded seat set into the pin, a cowl and a small screen
    box('seat', 'K_SEAT', (0, 0.18, zc + R * 0.6), (0.2, 0.2, 0.09), bevel=0.05)
    box('seatback', 'K_SEAT', (0, 0.36, zc + R * 0.95), (0.19, 0.05, 0.2), bevel=0.04)
    box('cowl', 'K_DARK', (0, -0.28, zc + R * 0.8), (0.22, 0.14, 0.06), bevel=0.04)
    box('screen', 'K_GLASS', (0, -0.42, zc + R * 1.08), (0.2, 0.012, 0.11), bevel=0.01)
    cyl('wheelstalk', 'K_DARK', (0, -0.2, zc + R * 0.95), (0, -0.05, zc + R * 1.25), 0.02, n=10)
    sphere('steer', 'K_DARK', (0, -0.04, zc + R * 1.28), (0.12, 0.02, 0.12))
    # wheels out on chrome struts
    for sg in (-1, 1):
        wheel('f%d' % sg, sg * 0.6, -0.78, 0.25, 0.2)
        wheel('r%d' % sg, sg * 0.64, 0.74, 0.31, 0.28)
        cyl('fstrut%d' % sg, 'K_CHROME', (sg * 0.2, -0.78, zc - 0.05), (sg * 0.52, -0.78, 0.25), 0.03, n=12)
        cyl('fstrut2%d' % sg, 'K_CHROME', (sg * 0.18, -0.62, zc + 0.05), (sg * 0.52, -0.78, 0.27), 0.022, n=12)
        cyl('rstrut%d' % sg, 'K_CHROME', (sg * 0.2, 0.74, zc - 0.05), (sg * 0.52, 0.74, 0.31), 0.035, n=12)
    # the pizza peel wing: a flat round-ended paddle on two struts, its handle trailing
    cyl('peel', 'K_WOOD', (0, 1.2, zc + 0.62), (0, 1.2, zc + 0.66), 0.42, n=48)
    box('peelhandle', 'K_WOOD', (0, 1.72, zc + 0.64), (0.06, 0.18, 0.018), bevel=0.012)
    for sg in (-1, 1):
        cyl('wingpost%d' % sg, 'K_DARK', (sg * 0.16, 0.95, zc + 0.15), (sg * 0.16, 1.15, zc + 0.62), 0.03, n=12)
    # lamps: two round headlamps on the front handle, tail lamps on the rear knob
    for sg in (-1, 1):
        cyl('lamp%d' % sg, 'K_CHROME', (sg * 0.16, -1.3, zc + 0.12), (sg * 0.16, -1.36, zc + 0.12), 0.07, n=24)
        cyl('lampglass%d' % sg, 'K_LIGHT', (sg * 0.16, -1.36, zc + 0.12), (sg * 0.16, -1.37, zc + 0.12), 0.06, n=24)
        cyl('tail%d' % sg, 'K_TAIL', (sg * 0.13, 1.5, zc + 0.04), (sg * 0.13, 1.55, zc + 0.04), 0.05, n=20)
    export('rollpin')


# ------------------------------------------------------------------ Grater: a chunky utility kart
def grater():
    reset()
    # the chassis tub, low and wide, in paint
    box('tub', 'K_PAINT', (0, 0, 0.42), (0.62, 1.15, 0.16), bevel=0.06, sub=0)
    box('nose', 'K_PAINT', (0, -1.05, 0.48), (0.55, 0.22, 0.14), bevel=0.08)
    # the grater: a tapered steel box behind the seat, a grid of grating slots on every side
    me = bpy.data.meshes.new('grater'); o = bpy.data.objects.new('grater', me); bpy.context.collection.objects.link(o)
    bm = bmesh.new(); y0, y1, zb, zt = 0.0, 0.95, 0.56, 1.42; wb, wt = 0.5, 0.36
    v = [bm.verts.new(p) for p in ((-wb, y0, zb), (wb, y0, zb), (wb, y1, zb), (-wb, y1, zb), (-wt, y0 + 0.08, zt), (wt, y0 + 0.08, zt), (wt, y1 - 0.08, zt), (-wt, y1 - 0.08, zt))]
    for f in ((0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)):
        bm.faces.new([v[i] for i in f])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:]); bm.to_mesh(me); bm.free()
    finish(o, 'K_METAL', smooth=False, bevel=0.03, seg=2)
    # grating: raised little lips and dark slots in rows on the two sides and the back
    k = 0
    for sg in (-1, 1):
        for row in range(5):
            z = zb + 0.12 + row * 0.15
            wz = wb + (wt - wb) * (z - zb) / (zt - zb)
            for col in range(5):
                y = y0 + 0.16 + col * 0.16
                box('slot%d' % k, 'K_DARK', (sg * (wz + 0.004), y, z), (0.012, 0.05, 0.022), bevel=0.008); k += 1
                box('lip%d' % k, 'K_CHROME', (sg * (wz + 0.014), y, z + 0.03), (0.012, 0.055, 0.008), bevel=0.004); k += 1
    for row in range(5):
        z = zb + 0.12 + row * 0.15
        for col in range(3):
            x = -0.2 + col * 0.2
            box('bslot%d%d' % (row, col), 'K_DARK', (x, y1 + 0.004 - 0.08 * (z - zb) / (zt - zb), z), (0.06, 0.012, 0.022), bevel=0.008)
    # the handle on top: a roll hoop with a paint grip
    for sg in (-1, 1):
        cyl('hoopleg%d' % sg, 'K_DARK', (sg * 0.3, 0.45, zt - 0.02), (sg * 0.3, 0.45, zt + 0.3), 0.035, n=14)
    cyl('hoopbar', 'K_PAINT', (-0.33, 0.45, zt + 0.3), (0.33, 0.45, zt + 0.3), 0.06, n=24, bevel=0.01)
    # the cab: a seat, a dash and a screen in front of the grater
    box('seat', 'K_SEAT', (0, -0.18, 0.66), (0.22, 0.2, 0.08), bevel=0.05)
    box('seatback', 'K_SEAT', (0, -0.02, 0.88), (0.22, 0.05, 0.22), bevel=0.04)
    box('dash', 'K_DARK', (0, -0.62, 0.7), (0.4, 0.1, 0.12), bevel=0.04)
    box('screen', 'K_GLASS', (0, -0.72, 0.92), (0.38, 0.015, 0.14), bevel=0.01)
    cyl('steer', 'K_DARK', (0, -0.52, 0.86), (0, -0.48, 0.9), 0.13, n=24)
    # bull bar and lamps
    for sg in (-1, 1):
        cyl('bbpost%d' % sg, 'K_DARK', (sg * 0.36, -1.24, 0.36), (sg * 0.36, -1.24, 0.78), 0.035, n=12)
        cyl('lamp%d' % sg, 'K_CHROME', (sg * 0.36, -1.26, 0.86), (sg * 0.36, -1.33, 0.86), 0.085, n=24)
        cyl('lampglass%d' % sg, 'K_LIGHT', (sg * 0.36, -1.33, 0.86), (sg * 0.36, -1.34, 0.86), 0.072, n=24)
        box('tail%d' % sg, 'K_TAIL', (sg * 0.48, 1.16, 0.5), (0.07, 0.012, 0.04), bevel=0.008)
    cyl('bbbar', 'K_DARK', (-0.42, -1.25, 0.72), (0.42, -1.25, 0.72), 0.035, n=12)
    cyl('bbbar2', 'K_DARK', (-0.42, -1.25, 0.46), (0.42, -1.25, 0.46), 0.035, n=12)
    # fat tyres, flared arches
    for sg in (-1, 1):
        wheel('f%d' % sg, sg * 0.72, -0.72, 0.34, 0.34, spokes=6)
        wheel('r%d' % sg, sg * 0.74, 0.68, 0.36, 0.38, spokes=6)
        for yy, rr in ((-0.72, 0.34), (0.68, 0.36)):
            YZ[0] = rr
            fender('arch%d%.0f' % (sg, yy * 10), 'K_DARK', sg * 0.73, yy, rr + 0.07, 0.44)
    export('grater')


# ------------------------------------------------------------------ Calzone Comet: a low crescent streamliner
def calzone():
    reset()
    # the shell: a half-oval of dough, flat beneath, domed over the top (a calzone folded over the driver's legs)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=64, ring_count=32, location=(0, 0, 0.3))
    o = bpy.context.active_object; o.name = 'shell'; o.scale = (0.74, 1.35, 0.42)
    bpy.ops.object.transform_apply(scale=True)
    bm = bmesh.new(); bm.from_mesh(o.data)
    for vv in bm.verts:
        if vv.co.z < 0.3:
            vv.co.z = 0.3 - (0.3 - vv.co.z) * 0.35       # a flattened belly
        vv.co.z += 0.12 * (vv.co.y / 1.35) ** 2 * (1 if vv.co.y > 0 else 0.4)   # the tail sweeps up a little
    bm.to_mesh(o.data); bm.free()
    finish(o, 'K_PAINT')
    # the crimped edge: a row of pinched dough lumps round the seam, in the stripe colour
    n = 46
    for i in range(n):
        a = 2 * math.pi * i / n
        x, y = math.cos(a) * 0.76, math.sin(a) * 1.37
        sphere('crimp%d' % i, 'K_STRIPE', (x, y, 0.3), (0.07, 0.07 if abs(math.cos(a)) > 0.3 else 0.09, 0.05), seg=12)
    # the bubble canopy and the driver's cut-out
    bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=24, location=(0, -0.05, 0.64))
    c = bpy.context.active_object; c.name = 'canopy'; c.scale = (0.32, 0.5, 0.46)
    bpy.ops.object.transform_apply(scale=True)
    bm = bmesh.new(); bm.from_mesh(c.data)
    bmesh.ops.delete(bm, geom=[vv for vv in bm.verts if vv.co.z < 0.6], context='VERTS')
    bm.to_mesh(c.data); bm.free(); finish(c, 'K_GLASS')
    box('seat', 'K_SEAT', (0, 0.08, 0.6), (0.2, 0.18, 0.05), bevel=0.04)
    cyl('canopyrim', 'K_CHROME', (0, -0.05, 0.6), (0, -0.05, 0.62), 0.0, n=4, cap=False) if False else None
    # tail fin, steam vents (three little slits on top, as on a baked calzone)
    me = bpy.data.meshes.new('fin'); f = bpy.data.objects.new('fin', me); bpy.context.collection.objects.link(f)
    bm = bmesh.new(); pts = [(0, 0.75, 0.66), (0, 1.38, 0.62), (0, 1.42, 1.08), (0, 1.15, 1.1)]
    vs = [bm.verts.new((p[0] - 0.03, p[1], p[2])) for p in pts] + [bm.verts.new((p[0] + 0.03, p[1], p[2])) for p in pts]
    bm.faces.new(vs[:4]); bm.faces.new(list(reversed(vs[4:])))
    for i in range(4):
        j = (i + 1) % 4; bm.faces.new((vs[i], vs[4 + i], vs[4 + j], vs[j]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:]); bm.to_mesh(me); bm.free(); finish(f, 'K_PAINT', bevel=0.015)
    for k, (x, y) in enumerate(((-0.28, 0.45), (0.28, 0.45), (0, 0.72))):
        box('vent%d' % k, 'K_DARK', (x, y, 0.72 - 0.15 * abs(x)), (0.025, 0.12, 0.02), bevel=0.012)
    # a slim red stripe down the middle of the nose (sauce peeking out of the fold)
    box('sauce', 'K_RED', (0, -0.95, 0.56), (0.05, 0.3, 0.02), bevel=0.015)
    # lamps: two slits in the nose, a light bar in the tail
    for sg in (-1, 1):
        box('lamp%d' % sg, 'K_LIGHT', (sg * 0.3, -1.16, 0.44), (0.09, 0.03, 0.022), bevel=0.012)
    box('tailbar', 'K_TAIL', (0, 1.36, 0.46), (0.36, 0.02, 0.025), bevel=0.01)
    # wheels tucked under the shell's skirt
    for sg in (-1, 1):
        wheel('f%d' % sg, sg * 0.6, -0.78, 0.2, 0.16, spokes=5)
        wheel('r%d' % sg, sg * 0.64, 0.8, 0.23, 0.2, spokes=5)
    export('comet')


# ------------------------------------------------------------------ Oil Can: a dragster
def oilcan():
    reset()
    # the rails: a long, thin ladder frame
    for sg in (-1, 1):
        cyl('rail%d' % sg, 'K_DARK', (sg * 0.16, -1.55, 0.3), (sg * 0.22, 1.0, 0.36), 0.035, n=12)
    for y in (-1.3, -0.8, -0.2, 0.4, 0.95):
        cyl('rung%.0f' % (y * 10), 'K_DARK', (-0.19, y, 0.32), (0.19, y, 0.32), 0.025, n=10)
    # the spout nose: a long tapered cone from the can to the front
    cyl('spout', 'K_METAL', (0, -1.75, 0.33), (0, -0.85, 0.4), 0.035, 0.14, n=32)
    cyl('spoutlip', 'K_METAL', (0, -1.79, 0.33), (0, -1.75, 0.33), 0.05, n=24)
    # the can: an upright cylinder, its shoulders rounded, a cap on top as the air scoop, a label band in stripe
    cyl('can', 'K_PAINT', (0, -0.15, 0.35), (0, -0.15, 1.05), 0.36, n=48, bevel=0.05)
    cyl('shoulder', 'K_PAINT', (0, -0.15, 1.05), (0, -0.15, 1.18), 0.36, 0.22, n=48)
    cyl('neck', 'K_METAL', (0, -0.15, 1.18), (0, -0.15, 1.27), 0.12, n=32)
    cyl('cap', 'K_RED', (0, -0.15, 1.27), (0, -0.15, 1.38), 0.14, n=32, bevel=0.02)
    box('scoop', 'K_DARK', (0, -0.28, 1.33), (0.09, 0.025, 0.04), bevel=0.01)
    cyl('label', 'K_STRIPE', (0, -0.15, 0.55), (0, -0.15, 0.85), 0.362, n=48)
    cyl('canhandle', 'K_CHROME', (0, 0.22, 1.0), (0, 0.22, 0.5), 0.03, n=12)
    # headers: chrome pipes out of the can's sides
    for sg in (-1, 1):
        for k, z in enumerate((0.55, 0.7, 0.85)):
            cyl('header%d%d' % (sg, k), 'K_CHROME', (sg * 0.3, -0.15, z), (sg * 0.55, 0.05, z + 0.25), 0.03, n=10)
    # the seat behind the can, between the slicks
    box('seat', 'K_SEAT', (0, 0.55, 0.48), (0.18, 0.22, 0.07), bevel=0.05)
    box('seatback', 'K_SEAT', (0, 0.78, 0.7), (0.18, 0.05, 0.24), bevel=0.04)
    box('cage', 'K_DARK', (0, 0.62, 1.05), (0.22, 0.03, 0.03), bevel=0.01)
    for sg in (-1, 1):
        cyl('cagepost%d' % sg, 'K_DARK', (sg * 0.2, 0.8, 0.4), (sg * 0.2, 0.62, 1.05), 0.025, n=10)
    # the rear wing high on struts
    box('wing', 'K_PAINT', (0, 1.12, 1.28), (0.55, 0.16, 0.025), bevel=0.012)
    for sg in (-1, 1):
        box('endplate%d' % sg, 'K_DARK', (sg * 0.56, 1.12, 1.2), (0.012, 0.18, 0.1), bevel=0.006)
        cyl('wingstrut%d' % sg, 'K_DARK', (sg * 0.25, 0.9, 0.42), (sg * 0.25, 1.1, 1.26), 0.025, n=10)
    # wheelie bar with two little casters
    cyl('wbar', 'K_CHROME', (0, 0.95, 0.3), (0, 1.75, 0.18), 0.025, n=10)
    for sg in (-1, 1):
        cyl('caster%d' % sg, 'K_DARK', (sg * 0.08, 1.75, 0.1), (sg * 0.13, 1.75, 0.1), 0.07, n=16)
    # lamps
    cyl('lamp', 'K_LIGHT', (0, -1.0, 0.43), (0, -1.02, 0.43), 0.05, n=16)
    for sg in (-1, 1):
        box('tail%d' % sg, 'K_TAIL', (sg * 0.45, 1.3, 1.24), (0.06, 0.012, 0.02), bevel=0.006)
    # big slicks at the back, tiny wheels at the front
    for sg in (-1, 1):
        wheel('f%d' % sg, sg * 0.32, -1.45, 0.15, 0.09, spokes=5)
        wheel('r%d' % sg, sg * 0.58, 0.55, 0.44, 0.42, spokes=8)
    export('oilcan')


KARTS = {'rollpin': rollpin, 'grater': grater, 'comet': calzone, 'oilcan': oilcan}
if __name__ == '__main__':
    args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    for cid in (args or list(KARTS)):
        KARTS[cid]()
