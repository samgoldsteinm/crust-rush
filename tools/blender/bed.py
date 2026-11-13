"""The bed for Bedroom Blitz: an oak frame on four tapered legs, a padded headboard, a mattress, a duvet and a throw
that are dropped on as cloth so they fold and hang the way fabric does, and pillows blown up from flat cases.
Same footprint and clearances as the code-built bed it replaces (152 x 203 cm, 28 cm clear underneath: the track
runs under it). Run: D:/blender/blender.exe --background --python D:/crust-rush/source/tools/blender/bed.py
"""
import sys, math, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from crlib import *

NAME = 'bed'
s = reset()
os.makedirs(f'{OUT}/{NAME}', exist_ok=True)
W, L, LEG, RAIL, MH = 1.52, 2.03, .28, .15, .24          # mattress width and length, leg height, rail depth, mattress height
TOP = LEG + .09                                            # where the mattress sits
oak = mat('oak', hexcol('#b98a58'), .5); slat = mat('slats', hexcol('#8a6a48'), .8)
linen = mat('linen', hexcol('#b9b2a4'), .9, sheen=.3); sheet = mat('sheet', hexcol('#f2efe8'), .9, sheen=.2)
duvet = mat('duvet', hexcol('#3d5a80'), .9, sheen=.4); lining = mat('duvet2', hexcol('#e8e2d6'), .9, sheen=.3)
pillow = mat('pillow', hexcol('#fbfaf6'), .9, sheen=.3); cushion = mat('cushion', hexcol('#e07a3a'), .9, sheen=.4)
throw = mat('throw', hexcol('#d9a441'), .95, sheen=.5)
hard = []; soft = []

# ---- frame (head of the bed at +Y, foot at -Y)
for sx in (-1, 1):
    for sy in (-1, 1):
        hard.append(frustum(f'leg{sx}{sy}', .032, .022, LEG, (sx * (W / 2 - .05), sy * (L / 2 - .05), 0), oak))
    hard.append(box(f'rail{sx}', (.032, L + .04, RAIL), (sx * (W / 2 + .012), 0, LEG + RAIL / 2 - .01), oak, .006))
hard.append(box('footrail', (W + .056, .032, RAIL), (0, -L / 2 - .012, LEG + RAIL / 2 - .01), oak, .006))
hard.append(box('slats', (W, L, .02), (0, 0, TOP - .01), slat, 0))
hard.append(box('headboard', (W + .08, .04, 1.12), (0, L / 2 + .034, .56), oak, .01, 4))
# three padded panels: soft boxes that bulge towards the room
for i in range(3):
    p = box(f'pad{i}', (W / 3 - .02, .07, .58), ((i - 1) * W / 3, L / 2 + .002, .78), linen, .028, 5)
    sub = p.modifiers.new('sub', 'SUBSURF'); sub.levels = 1
    hard.append(p)
# mattress: a rounded slab
mt = box('mattress', (W, L, MH), (0, 0, TOP + MH / 2), sheet, .045, 6)
hard.append(mt)
for o in hard: freeze(o); smooth(o); uv_box(o)

# ---- pillows and the cushion: two flat sheets sewn round the edge and blown up
def pillow_case(name, w, h, nx, ny, m, puff):
    a = grid(name, w, h, nx, ny, (0, 0, 0), m); b = grid(name + 'b', w, h, nx, ny, (0, 0, 0), m)
    for o, dz in ((a, .002), (b, -.002)):
        for v in o.data.vertices:
            if abs(abs(v.co.x) - w / 2) > 1e-4 and abs(abs(v.co.y) - h / 2) > 1e-4: v.co.z = dz
    b.data.flip_normals()
    bpy.ops.object.select_all(action='DESELECT'); a.select_set(True); b.select_set(True); bpy.context.view_layer.objects.active = a
    bpy.ops.object.join(); bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.remove_doubles(threshold=.0005); bpy.ops.object.mode_set(mode='OBJECT')
    cloth(a, mass=.15, tension=40, bending=.6, self_col=False, pressure=puff, gravity=0, quality=6)
    a.modifiers['cloth'].settings.shrink_min = -.04 if hasattr(a.modifiers['cloth'].settings, 'shrink_min') else 0
    return a

cases = [pillow_case('pillowL', .70, .45, 34, 22, pillow, 9), pillow_case('pillowR', .70, .45, 34, 22, pillow, 9), pillow_case('cushion', .46, .46, 24, 24, cushion, 12)]
simulate(28)
for o in cases: freeze(o); smooth(o)
PZ = TOP + MH
for o, loc, rot in ((cases[0], (-.38, L / 2 - .30, PZ + .085), (math.radians(8), 0, math.radians(4))), (cases[1], (.38, L / 2 - .29, PZ + .085), (math.radians(7), 0, math.radians(-3))),
                    (cases[2], (.06, L / 2 - .56, PZ + .15), (math.radians(52), math.radians(4), math.radians(14)))):
    o.location = loc; o.rotation_euler = rot; apply_scale(o); active(o); bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
soft += cases

# ---- the duvet: a quilt dropped onto the bed; it hangs over both sides and a little over the foot
DL = L * .74
dv = grid('duvet', W + .56, DL, 78, 60, (0, -L / 2 + DL / 2 - .13, PZ + .07), duvet)
round_corners(dv, .2); rumple(dv, .012, .16, 3)
cloth(dv, mass=.4, tension=14, bending=1.6, self_col=True, dist=.008, quality=10, damp=8)
# the cloth lands on the mattress, the pillows and ONE smooth block the size of the frame. Colliding with the rails, legs and slats
# separately pinched the sheet between them at the foot corners and shot a spike out of it.
proxy = box('proxy', (W + .09, L + .07, RAIL + .02), (0, -.003, LEG + RAIL / 2 - .01), oak, .014, 4); freeze(proxy)
for o in [mt, proxy] + cases: collider(o)
simulate(110)
freeze(dv); relax(dv, .5, 2); quilt(dv, .27, .017); solidify(dv, .026, 1.0); freeze(dv); smooth(dv)
# the turned-back band at the pillow end, lining side up: a long flat case blown up a little and laid across
bpy.context.scene.frame_set(1)
band = pillow_case('band', W + .06, .30, 56, 10, lining, 3.5)
simulate(22); freeze(band); smooth(band)
band.location = (0, -L / 2 + DL - .22, PZ + .075); band.rotation_euler = (math.radians(-3), 0, 0)
active(band); bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
# a throw dropped across the foot, a little askew
bpy.context.scene.frame_set(1)
collider(dv); collider(band)
th = grid('throw', W + .42, .58, 70, 22, (.04, -L / 2 + .52, PZ + .17), throw)
rumple(th, .016, .09, 7)
th.rotation_euler = (0, 0, math.radians(5)); apply_scale(th)
cloth(th, mass=.2, tension=10, bending=.25, self_col=True, dist=.006, quality=10, damp=8)
simulate(60)
freeze(th); relax(th, .4, 1); solidify(th, .012, 1.0); freeze(th); smooth(th)
soft += [dv, band, th]
bpy.data.objects.remove(proxy)
for o in hard + soft: o.modifiers.clear()

allo = hard + soft
bake_ao(allo)
print('CHECK', check_render(NAME, allo, views=((32, 24), (150, 16), (-60, 40))))
export(NAME, allo)
