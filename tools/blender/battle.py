"""Prep Table Showdown, the Balloon Battle arena: its models, built to the SAME shapes the game collides with
(bbArena in tools/mini/battle.js: what you see is what stops you). Toy scale, as the Miniature Mayhem rooms: a kart is a
7.5 cm toy car and 347 game units are a metre, so the table is a real prep table, 2.19 x 1.50 m.
Every model is built in the ARENA'S OWN PLACE (the table's middle is the origin), so the game puts each at (0, 0) unturned.
Arena coordinates are x east, z south; here X = x / 347 and Y = -z / 347 (a model's -Y side is its south).
  bbtable   the steel top with its raised front edge, legs, an undershelf
  bbbins    four steel ingredient pans along the back wall: mozzarella, tomato sauce, pepperoni, olives
  bbboxes   four stacks of three pizza boxes along the south wall, and an opened-out box leaning on them: the ramp up, as wide as the stacks are deep
  bbblock   a butcher's block against the east wall (the raised route's other half) and a bread board leaning on its whole north end: the way down
  (2026-11-13, the owner's play-test: ramps the full width of their ledges, no fifth pan in the east ramp's way, no peel handle on the table)
  bbprops   a pepper mill, a rolling pin, a stack of plates
Run: D:/blender/blender.exe --background --python D:/crust-rush/source/tools/blender/battle.py [-- name ...]
then py.cmd tools/blender/pack_glb.py <name ...>
"""
import sys, math, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
import numpy as np
from mathutils import Vector
from crlib import *

ONLY = [a for a in sys.argv[sys.argv.index('--') + 1:]] if '--' in sys.argv else []
U = 347.0
def want(n): return not ONLY or n in ONLY
def ax(x): return x / U
def ay(z): return -z / U
def abox(name, x0, x1, z0, z1, h0, h1, m, bev=.003, seg=2):
    """a box given in arena units (x east, z south, heights)"""
    return box(name, ((x1 - x0) / U, (z1 - z0) / U, (h1 - h0) / U), ((x0 + x1) / 2 / U, -(z0 + z1) / 2 / U, (h0 + h1) / 2 / U), m, bev, seg)


def mats():
    return dict(steel=mat('bsteel', hexcol('#c2c6ca'), .35, metal=.8), card=mat('bcard', hexcol('#c79a5e'), .85), cardin=mat('bcardin', hexcol('#e9dcc2'), .9), wood=mat('bwood', hexcol('#c9a26c'), .5),
                dark=mat('bwoodd', hexcol('#5a3a22'), .45), plate=mat('bplate', hexcol('#f4f1ea'), .25), cheese=mat('bcheese', hexcol('#f3ecd2'), .6), sauce=mat('bsauce', hexcol('#b3261c'), .25),
                pep=mat('bpep', hexcol('#a8321e'), .5), olive=mat('bolive', hexcol('#1c1a17'), .3), oliveg=mat('boliveg', hexcol('#6f7a2a'), .35), mush=mat('bmush', hexcol('#d9c8a8'), .7), black=mat('gblack', hexcol('#0e0f11'), .5))


# ---------------- the table
if want('bbtable'):
    s = reset(); M = mats(); P = []; X, Z = 380, 260
    P.append(abox('top', -X - 8, X, -Z, Z, -14, 0, M['steel'], .004, 2))
    P.append(abox('edge', -X - 8, -X, -Z, Z, -14, 7, M['steel'], .006, 3))                                   # the raised front edge (west): a kart on its wheels cannot get over it
    for sx in (-X + 12, X - 20):
        for sz in (-Z + 20, Z - 20): P.append(abox(f'leg{sx}{sz}', sx - 8, sx + 8, sz - 8, sz + 8, -312, -14, M['steel'], .004, 2)); P.append(abox(f'foot{sx}{sz}', sx - 10, sx + 10, sz - 10, sz + 10, -312, -304, M['black'], .003, 1))
    P.append(abox('shelf', -X + 4, X - 12, -Z + 12, Z - 12, -232, -226, M['steel'], .004, 1))
    for sz in (-Z + 14, Z - 22): P.append(abox(f'rail{sz}', -X + 12, X - 20, sz, sz + 8, -40, -30, M['steel'], .003, 1))
    finish_model('bbtable', P, 9.0, views=((-140, 22),), floor=False)

# ---------------- the ingredient pans
if want('bbbins'):
    s = reset(); M = mats(); P = []; r = np.random.RandomState(5)
    fills = ('cheese', 'sauce', 'pep', 'olive', 'mush')
    for i in range(4):
        x0 = -338 + i * 144; x1 = x0 + 100; z0, z1 = -212, -150; cx, cy = ax((x0 + x1) / 2), ay((z0 + z1) / 2); w, d = 100 / U, 62 / U; H = 36 / U
        # a steel pan: four walls, a floor, a rolled lip
        t = .004
        for nm, (a0, a1, b0, b1) in (('w', (x0, x0 + 1.4, z0, z1)), ('e', (x1 - 1.4, x1, z0, z1)), ('n', (x0, x1, z0, z0 + 1.4)), ('s', (x0, x1, z1 - 1.4, z1))):
            P.append(abox(f'pan{i}{nm}', a0, a1, b0, b1, 0, 36, M['steel'], .0015, 1))
        P.append(abox(f'lip{i}', x0 - 1.6, x1 + 1.6, z0 - 1.6, z1 + 1.6, 33.6, 36, M['steel'], .003, 2))
        P.append(abox(f'in{i}', x0 + 1.2, x1 - 1.2, z0 + 1.2, z1 - 1.2, 33.8, 36.2, M['black'], 0))               # (cut back out below by the filling that covers it)
        top = 31.5 / U; f = fills[i]
        if f == 'sauce':
            bpy.ops.mesh.primitive_grid_add(x_subdivisions=28, y_subdivisions=18, size=1, location=(cx, cy, 36.4 / U)); o = bpy.context.object; o.name = 'sauce'; o.scale = (w - .009, d - .009, 1); apply_scale(o); o.data.materials.append(M['sauce'])
            for v in o.data.vertices: v.co.z += .0016 * math.sin(v.co.x * 90 + 1) * math.cos(v.co.y * 70) + .0012 * math.sin(v.co.y * 140 + v.co.x * 40)
            smooth(o); P.append(o)
        else:
            base = abox(f'bed{i}', x0 + 1.4, x1 - 1.4, z0 + 1.4, z1 - 1.4, 30, 36.3, M['cheese'] if f == 'cheese' else M['pep'] if f == 'pep' else M['olive'] if f == 'olive' else M['mush'], 0); P.append(base)
            n = dict(cheese=260, pep=46, olive=90, mush=60)[f]
            for k in range(n):
                px, py = cx + (r.rand() - .5) * (w - .03), cy + (r.rand() - .5) * (d - .03); pz = 36.5 / U + r.rand() * .006
                if f == 'cheese':
                    o = box(f'sh{i}{k}', (.022 + r.rand() * .02, .004, .004), (px, py, pz), M['cheese'], 0); o.rotation_euler = (r.rand() * .5, r.rand() * .5, r.rand() * 3.14); apply_scale(o)
                elif f == 'pep':
                    o = rod(f'pp{i}{k}', .019, .003, (px, py, pz), M['pep'], 'Z', 14); o.rotation_euler = (r.randn() * .25, r.randn() * .25, 0); apply_scale(o)
                elif f == 'olive':
                    o = ball(f'ol{i}{k}', .0085, (px, py, pz + .004), M['olive'] if r.rand() < .65 else M['oliveg'], (1, 1, 1.25), 10, 6); o.rotation_euler = (r.rand() * 3, r.rand() * 3, 0); apply_scale(o)
                else:
                    o = rod(f'mu{i}{k}', .016, .005, (px, py, pz + .002), M['mush'], 'Z', 12); o.scale = (1, .55, 1); o.rotation_euler = (r.randn() * .3, r.randn() * .3, r.rand() * 3.14); apply_scale(o)
                P.append(o)
    finish_model('bbbins', P, 5.5, views=((-25, 28),), floor=True)

# ---------------- the pizza boxes: four stacks of three, and one opened out flat, leaning on the first stack as the ramp
if want('bbboxes'):
    s = reset(); M = mats(); P = []; r = np.random.RandomState(9)
    x0, x1, z0, z1, H = -215, 232, 130, 260, 42; n = 4; wx = (x1 - x0) / n
    for i in range(n):
        for j in range(3):
            dx, dz, tw = (r.rand() - .5) * 3 * (j > 0), (r.rand() - .5) * 2 * (j > 0), (r.rand() - .5) * .03 * (j > 0)
            a0, a1 = x0 + i * wx + .6 - dx * (j < 2), x0 + (i + 1) * wx - .6 - dx * (j < 2)
            b = abox(f'box{i}{j}', a0, a1, z0 + .4, z1 - .4, j * 14 + .15, (j + 1) * 14 - .15, M['card'], .002, 1); P.append(b)
            P.append(abox(f'flap{i}{j}', a0 - .25, a1 + .25, z0 - .2, z0 + .6, j * 14 + 9.5, (j + 1) * 14 - .1, M['card'], .001, 1))             # the lid's front flap, tucked down
            P.append(abox(f'seam{i}{j}', a0 + 1, a1 - 1, z0 + .1, z0 + .5, j * 14 + 8.6, j * 14 + 9.2, M['cardin'], 0))                             # the lid's edge shows as a paler line
    # the ramp: a box opened out flat (lid and base in one sheet, 66 cm) would be too long: it is one lid torn off, its flaps still on
    rx0, rx1, rz0, rz1 = -335, -215, 130, 260
    V = [(ax(rx0), ay(rz0), 0), (ax(rx1), ay(rz0), H / U), (ax(rx1), ay(rz1), H / U), (ax(rx0), ay(rz1), 0)]; t = .004
    sheet = mesh('lid', V + [(v[0], v[1], v[2] - t) for v in V], [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)], M['cardin'], False); P.append(sheet)
    for k, zz in enumerate((rz0, rz1)):                                                                      # its side flaps stand up a little: low kerbs along the ramp (looks only: lower than a step)
        P.append(mesh(f'lidflap{k}', [(ax(rx0), ay(zz), 0), (ax(rx1), ay(zz), H / U), (ax(rx1), ay(zz), H / U + .012), (ax(rx0), ay(zz), .012)], [(0, 1, 2, 3), (3, 2, 1, 0)], M['card'], False))
    P.append(abox('prop', rx1 - 26, rx1 - 6, rz0 + 6, rz1 - 6, 0, 30, M['card'], .002, 1))                   # what holds it up: a folded box underneath
    finish_model('bbboxes', P, 6.5, views=((-150, 24), (-60, 20)), floor=True)

# ---------------- the butcher's block and the pizza peel
if want('bbblock'):
    s = reset(); M = mats(); P = []; r = np.random.RandomState(3)
    x0, x1, z0, z1, H = 232, 380, -58, 260, 42
    # end-grain blocks glued up: strips along z, each its own tone
    n = 9; sw = (x1 - x0) / n
    for i in range(n):
        b = abox(f'strip{i}', x0 + i * sw, x0 + (i + 1) * sw, z0, z1, 6, H, M['wood'], .0015, 1); k = .8 + r.rand() * .2; b['tint'] = (k, k * .98, k * .95); P.append(b)
    for sx in (x0 + 10, x1 - 22):
        for sz in (z0 + 10, z1 - 22): P.append(abox(f'bfoot{sx}{sz}', sx, sx + 12, sz, sz + 12, 0, 6.2, M['dark'], .002, 1))
    P.append(abox('skirt', x0 + 6, x1 - 6, z0 + 6, z1 - 6, 2, 6.2, M['dark'], 0))
    # the peel: its blade leans from the table up to the block's top, its handle lies back along the table
    px0, px1, pz0, pz1 = 232, 380, -170, -58; t = .008
    V = [(ax(px0), ay(pz0), 0), (ax(px1), ay(pz0), 0), (ax(px1), ay(pz1), H / U), (ax(px0), ay(pz1), H / U)]
    P.append(mesh('blade', V + [(v[0], v[1], v[2] - t) for v in V], [(0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)], M['wood'], False))
    P.append(abox('chock', px0 + 8, px1 - 8, pz1 - 30, pz1 - 4, 0, 30, M['dark'], .002, 1))
    finish_model('bbblock', P, 6.5, views=((30, 24), (-120, 20)), floor=True)

# ---------------- a pepper mill, a rolling pin, a stack of plates
if want('bbprops'):
    s = reset(); M = mats(); P = []
    mx, mz = ax(70), ay(-10)
    P.append(lathe('mill', [(0, 0), (.032, 0), (.034, .01), (.030, .04), (.022, .09), (.026, .13), (.031, .16), (.026, .19), (.024, .215), (.031, .225), (.033, .245), (.024, .258), (0, .26)], 28, M['dark'], (mx, mz, 0)))
    P.append(ball('millknob', .011, (mx, mz, .268), M['steel'], (1, 1, .8), 12, 8)); P.append(lathe('millring', [(.0315, .160), (.0335, .162), (.0335, .170), (.0315, .172)], 28, M['steel'], (mx, mz, 0)))
    # the rolling pin lies along x: box [-170,-50] x [34,52], 17 high
    py_, pz_ = ay(43), 8.5 / U
    P.append(rod('pin', 8.5 / U, 120 / U, (ax(-110), py_, pz_), M['wood'], 'X', 24))
    for sx in (-1, 1): P.append(tube(f'pinh{sx}', [(ax(-110) + sx * 60 / U, py_, pz_), (ax(-110) + sx * 74 / U, py_, pz_), (ax(-110) + sx * 92 / U, py_, pz_)], .011, M['wood'], 0, 10))
    for sx in (-1, 1): P.append(abox(f'pinchock{sx}', -110 + sx * 40 - 3, -110 + sx * 40 + 3, 34, 52, 0, 2.2, M['dark'], 0))    # two slips of wood keep it from rolling
    # six plates
    cx, cz = ax(-262), ay(-60)
    for i in range(6): P.append(lathe(f'plate{i}', [(0, .001), (.055, .001), (.075, .004), (.1035, .0095), (.1035, .0105), (.075, .0058), (.055, .003), (0, .003)], 36, M['plate'], (cx + (i % 2) * .001, cz, i * .0104)))
    finish_model('bbprops', P, 4.0, views=((-30, 22),), floor=True)
