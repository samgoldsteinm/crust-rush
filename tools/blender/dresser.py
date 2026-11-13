"""The low dresser (120 x 45 cm, 45 cm high: the track climbs over it, so the size is fixed) and the nightstand
(46 x 40 cm, 52 cm high) for the toy-track rooms. Carcasses with softened edges, drawer fronts standing proud with
shadow gaps between them, bar handles on standoffs (dresser) and round knobs (nightstand), tapered legs, an
overhanging oak top. Materials: dresser (white paint), oak, brass. Front is -Y.
Run: D:/blender/blender.exe --background --python D:/crust-rush/source/tools/blender/dresser.py   (builds both)
"""
import sys, math, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from crlib import *


def rod(name, r, length, loc, m, axis='X'):
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=r, depth=length, location=loc,
                                        rotation=(0, math.pi / 2, 0) if axis == 'X' else (math.pi / 2, 0, 0))
    o = bpy.context.object; o.name = name; o.data.materials.append(m); smooth(o); return o


def finish(name, parts, dist):
    bpy.context.view_layer.update()
    for o in parts:
        active(o); bpy.ops.object.transform_apply(location=True, rotation=True, scale=True); freeze(o); smooth(o); uv_box(o)
    bpy.ops.mesh.primitive_plane_add(size=4, location=(0, 0, -.0005)); floor = bpy.context.object; floor.data.materials.append(mat('_floor', (.5, .5, .5)))
    bake_ao(parts); bpy.data.objects.remove(floor)
    for o in parts: soften_ao(o, 1, .3)
    print('CHECK', check_render(name, parts, views=((-30, 20),), dist=dist))
    export(name, parts)


# ---------------- the dresser
s = reset(); os.makedirs(f'{OUT}/dresser', exist_ok=True)
white = mat('dresser', hexcol('#eceae4'), .55); oak = mat('oak', hexcol('#b98a58'), .5); brass = mat('brass', hexcol('#b08a4a'), .3, metal=1.0)
W, D, H, LEG = 1.20, .45, .45, .09
P = [box('carcass', (W, D, H - LEG - .03), (0, 0, LEG + (H - LEG - .03) / 2), white, .006, 3),
     box('top', (W + .03, D + .02, .03), (0, 0, H - .015), oak, .009, 3)]
for sx in (-1, 1):
    for sy in (-1, 1): P.append(frustum(f'leg{sx}{sy}', .02, .013, LEG, (sx * (W / 2 - .06), sy * (D / 2 - .05), 0), oak))
dw = W / 2 - .024; dh = (H - LEG - .03) / 3 - .01
for c in range(2):
    for r in range(3):
        x = (c - .5) * (W / 2 - .006); z = LEG + .009 + dh / 2 + r * (dh + .009)
        P.append(box(f'drawer{c}{r}', (dw, .018, dh), (x, -D / 2 - .004, z), white, .005, 3))
        hz = z + dh * .12
        P.append(rod(f'bar{c}{r}', .0055, .14, (x, -D / 2 - .032, hz), brass))
        for sd in (-1, 1): P.append(rod(f'stand{c}{r}{sd}', .0045, .022, (x + sd * .06, -D / 2 - .022, hz), brass, 'Y'))
finish('dresser', P, 3.0)

# ---------------- the nightstand
s = reset(); os.makedirs(f'{OUT}/nightstand', exist_ok=True)
oak = mat('oak', hexcol('#b98a58'), .5); brass = mat('brass', hexcol('#b08a4a'), .3, metal=1.0)
W, D, H, LEG = .46, .40, .52, .14
P = [box('carcass', (W, D, H - LEG - .02), (0, 0, LEG + (H - LEG - .02) / 2), oak, .006, 3),
     box('top', (W + .02, D + .015, .02), (0, 0, H - .01), oak, .007, 3)]
for sx in (-1, 1):
    for sy in (-1, 1): P.append(frustum(f'leg{sx}{sy}', .018, .012, LEG, (sx * (W / 2 - .04), sy * (D / 2 - .04), 0), oak))
dh = (H - LEG - .02) / 2 - .014
for i in range(2):
    z = LEG + .01 + dh / 2 + i * (dh + .008)
    P.append(box(f'drawer{i}', (W - .03, .016, dh), (0, -D / 2 - .003, z), oak, .005, 3))
    bpy.ops.mesh.primitive_uv_sphere_add(segments=18, ring_count=10, radius=.014, location=(0, -D / 2 - .026, z)); k = bpy.context.object; k.scale.y = .75; k.data.materials.append(brass); smooth(k); P.append(k)
    P.append(rod(f'neck{i}', .006, .014, (0, -D / 2 - .016, z), brass, 'Y'))
finish('nightstand', P, 1.9)
