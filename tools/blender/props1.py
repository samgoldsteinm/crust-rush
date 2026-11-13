"""The floor lamp and the desk for the toy-track rooms (sizes fixed: the track spirals round the lamp and runs along the desk).
- floorlamp: a weighted brass base, a slim pole 1.5 m tall, a tapered fabric drum shade with rolled rims, held by a three-arm
  fitting, and a bulb. Materials: lampbrass, shade, bulb.
- desk: a 200 x 80 cm top 75 cm high with softened edges on a black steel frame (two end frames with feet and glides, a back
  rail, a cable tray). Materials: walnut (the top), desksteel, black (the glides).
Front is -Y. Run: D:/blender/blender.exe --background --python D:/crust-rush/source/tools/blender/props1.py
"""
import sys, math, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from crlib import *


def finish(name, parts, dist, lift=.3):
    bpy.context.view_layer.update()
    for o in parts:
        active(o); bpy.ops.object.transform_apply(location=True, rotation=True, scale=True); freeze(o); smooth(o)
        if not o.get('keep_uv'): uv_box(o)
    bpy.ops.mesh.primitive_plane_add(size=6, location=(0, 0, -.0005)); floor = bpy.context.object; floor.data.materials.append(mat('_floor', (.5, .5, .5)))
    bake_ao(parts); bpy.data.objects.remove(floor)
    for o in parts: soften_ao(o, 1, lift)
    print('CHECK', check_render(name, parts, views=((-30, 16),), dist=dist))
    export(name, parts)


def tube(name, r_bot, r_top, h, z0, m, verts=48, caps=False):
    bpy.ops.mesh.primitive_cone_add(vertices=verts, radius1=r_bot, radius2=r_top, depth=h, location=(0, 0, z0 + h / 2), end_fill_type='NGON' if caps else 'NOTHING')
    o = bpy.context.object; o.name = name; o.data.materials.append(m); smooth(o); return o


def ring(name, R, r, z, m):
    bpy.ops.mesh.primitive_torus_add(major_radius=R, minor_radius=r, major_segments=48, minor_segments=8, location=(0, 0, z))
    o = bpy.context.object; o.name = name; o.data.materials.append(m); smooth(o); return o


# ---------------- the floor lamp
s = reset(); os.makedirs(f'{OUT}/floorlamp', exist_ok=True)
brass = mat('lampbrass', hexcol('#8c6a3c'), .32, metal=1.0); shade = mat('shade', hexcol('#f3e6cc'), .9); bulb = mat('bulb', hexcol('#fff1cf'), .5)
P = []
base = tube('base', .14, .13, .022, 0, brass, 48, True); bevel(base, .006, 3, 40); P.append(base)
P.append(tube('collar', .022, .014, .05, .022, brass, 24, True))
P.append(tube('pole', .011, .011, 1.42, .05, brass, 20, True))
P.append(tube('socket', .02, .02, .07, 1.36, brass, 20, True))
sh = tube('shade', .20, .17, .26, 1.33, shade, 64); sh['keep_uv'] = 1; P.append(sh)      # an open drum: lit from inside, seen from both sides
P.append(ring('rim_top', .17, .0035, 1.59, brass)); P.append(ring('rim_bot', .20, .0035, 1.33, brass))
for i in range(3):                                                                      # the fitting: three arms from the pole to the top rim
    a = i / 3 * 2 * math.pi + .4
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=.0025, depth=.17, location=(math.cos(a) * .085, math.sin(a) * .085, 1.585), rotation=(0, math.pi / 2, a))
    o = bpy.context.object; o.name = f'arm{i}'; o.data.materials.append(brass); smooth(o); P.append(o)
bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=12, radius=.04, location=(0, 0, 1.46)); b = bpy.context.object; b.scale.z = 1.25; b.data.materials.append(bulb); smooth(b); P.append(b)
finish('floorlamp', P, 4.2, .6)

# ---------------- the desk
s = reset(); os.makedirs(f'{OUT}/desk', exist_ok=True)
walnut = mat('walnut', hexcol('#6b4428'), .4); steel = mat('desksteel', hexcol('#17181a'), .55, metal=.6); black = mat('black', hexcol('#0c0c0d'), .6)
W, D, H = 2.00, .80, .75
T, t = .06, .03; LH = H - .03
P = [box('top', (W, D, .03), (0, 0, H - .015), walnut, .007, 4)]
for sx in (-1, 1):
    x = sx * (W / 2 - .14)
    for sy in (-1, 1):
        P.append(box(f'post{sx}{sy}', (T, t, LH - t), (x, sy * (D / 2 - .09), (LH - t) / 2 + t * .5), steel, .005, 2))
        g = tube(f'glide{sx}{sy}', .026, .022, .01, 0, black, 18, True); g.location.x = x; g.location.y = sy * (D / 2 - .06); P.append(g)
    P.append(box(f'foot{sx}', (T, D - .06, t), (x, 0, t / 2 + .004), steel, .006, 3))
    P.append(box(f'rail{sx}', (T, D - .14, t), (x, 0, LH - t / 2), steel, .004, 2))
P.append(box('backrail', (W - .34, t * 1.2, t), (0, D / 2 - .12, LH - t / 2), steel, .004, 2))
P.append(box('tray', (W * .55, .12, .004), (0, D / 2 - .16, LH - .09), steel, 0))
for sx in (-1, 1): P.append(box(f'trayend{sx}', (.004, .12, .09), (sx * W * .275, D / 2 - .16, LH - .045), steel, 0))
finish('desk', P, 4.4)
