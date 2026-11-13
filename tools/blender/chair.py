"""The gaming chair for the toy-track rooms: a five-star base on twin-wheel casters, a gas lift, a bucket seat with raised
side bolsters, a tall reclined back with shoulder wings, a lumbar cushion and a head pillow, and two armrests.
Same size and proportions as the code-built chair it replaces (seat top 47 cm, back top about 1.26 m, 62 cm across the
base). Soft parts are bevelled boxes smoothed into cushions; hard parts keep crisp bevels.
Materials: pu (black upholstery), pu2 (the accent colour), nylon (black plastic), chrome, caster.
Front is -Y. Run: D:/blender/blender.exe --background --python D:/crust-rush/source/tools/blender/chair.py
"""
import sys, math, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from mathutils import Matrix, Vector
from crlib import *

NAME = 'chair'
s = reset()
os.makedirs(f'{OUT}/{NAME}', exist_ok=True)
pu = mat('pu', hexcol('#16171a'), .5); pu2 = mat('pu2', hexcol('#ff6a12'), .5)
nyl = mat('nylon', hexcol('#121214'), .55); chrome = mat('chrome', hexcol('#c9ccd2'), .18, metal=1.0); cast = mat('caster', hexcol('#0b0b0c'), .35)
parts = []


def cushion(name, size, m, soft=.3, level=1):
    """a padded shape: a box with generous round edges, smoothed"""
    o = box(name, size, (0, 0, 0), m, min(size) * soft, 4)
    sub = o.modifiers.new('sub', 'SUBSURF'); sub.levels = level
    return o


def place(o, M):
    o.matrix_world = M; parts.append(o); return o


def T(x, y, z): return Matrix.Translation((x, y, z))
def R(ax, a): return Matrix.Rotation(a, 4, ax)


def cyl(name, r1, r2, h, m, verts=24):
    bpy.ops.mesh.primitive_cone_add(vertices=verts, radius1=r1, radius2=r2, depth=h, location=(0, 0, 0)); o = bpy.context.object; o.name = name
    o.data.materials.append(m); bevel(o, min(r1, r2, h) * .12, 2, 50); return o


# ---- the base: five arms sloping down from the hub to the casters
for i in range(5):
    A = R('Z', i / 5 * 2 * math.pi + .3)
    place(box(f'arm{i}', (.30, .05, .032), (0, 0, 0), nyl, .012, 3), A @ T(.17, 0, .082) @ R('Y', .11))
    place(cyl(f'stem{i}', .01, .01, .04, nyl, 12), A @ T(.31, 0, .06))
    place(box(f'fork{i}', (.046, .054, .024), (0, 0, 0), nyl, .008, 2), A @ T(.31, 0, .044))
    for sd in (-1, 1):
        place(cyl(f'wheel{i}{sd}', .026, .026, .018, cast, 22), A @ T(.31, sd * .016, .026) @ R('X', math.pi / 2))
place(cyl('hub', .065, .05, .05, nyl), T(0, 0, .105))
place(cyl('shroud', .042, .036, .09, nyl), T(0, 0, .17))
place(cyl('lift', .026, .026, .22, chrome), T(0, 0, .23))
place(box('plate', (.22, .26, .03), (0, 0, 0), nyl, .008, 2), T(0, 0, .34))
place(cyl('lever', .008, .008, .14, nyl, 10), T(.15, -.04, .335) @ R('Y', math.pi / 2))

# ---- the seat: a cushion with a waterfall front, and raised bolsters either side
place(cushion('seat', (.40, .50, .11), pu, .34), T(0, -.02, .42))
for sd in (-1, 1):
    place(cushion(f'bolster{sd}', (.09, .48, .10), pu2, .42), T(sd * .23, -.02, .445) @ R('Y', sd * .25))

# ---- the back: reclined a little about a pivot behind the seat
B = T(0, .22, .46) @ R('X', -.16)
place(cushion('back', (.38, .10, .80), pu, .36), B @ T(0, 0, .42))
for sd in (-1, 1):
    place(cushion(f'wing{sd}', (.09, .13, .52), pu2, .42), B @ T(sd * .21, -.025, .30) @ R('Z', sd * .3))
    place(cushion(f'shoulder{sd}', (.11, .12, .28), pu, .42), B @ T(sd * .20, -.02, .68) @ R('Z', sd * .25) @ R('Y', -sd * .12))
place(cushion('headrest', (.30, .07, .13), pu2, .45), B @ T(0, -.06, .76))
place(cushion('lumbar', (.30, .08, .16), pu, .45), B @ T(0, -.07, .22))
place(box('shell', (.34, .03, .70), (0, 0, 0), nyl, .012, 3), B @ T(0, .056, .40))
# two stitched channels down the middle of the back, pressed into the padding
for sd in (-1, 1):
    place(cushion(f'channel{sd}', (.012, .02, .46), pu2, .45, 0), B @ T(sd * .075, -.047, .48))

# ---- the armrests
for sd in (-1, 1):
    place(box(f'post{sd}', (.04, .06, .22), (0, 0, 0), nyl, .01, 3), T(sd * .27, 0, .47))
    place(cushion(f'pad{sd}', (.08, .26, .03), nyl, .42, 1), T(sd * .27, -.02, .595))
    place(box(f'bracket{sd}', (.09, .04, .02), (0, 0, 0), nyl, .005, 2), T(sd * .23, 0, .37))

bpy.context.view_layer.update()
for o in parts:
    active(o); bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    freeze(o); smooth(o); uv_box(o)
bpy.ops.mesh.primitive_plane_add(size=4, location=(0, 0, -.0005)); floor = bpy.context.object; floor.data.materials.append(mat('_floor', (.5, .5, .5)))
bake_ao(parts); bpy.data.objects.remove(floor)
for o in parts: soften_ao(o, 1, .25)
print('CHECK', check_render(NAME, parts, views=((-35, 18), (150, 14)), dist=3.4))
export(NAME, parts)
