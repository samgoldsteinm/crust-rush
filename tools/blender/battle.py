"""Prep Table Showdown, the Balloon Battle arena: its models, built to the SAME shapes the game collides with
(bbArena in tools/mini/battle.js: what you see is what stops you). Toy scale, as the Miniature Mayhem rooms: a kart is a
7.5 cm toy car and 347 game units are a metre, so the table is a real prep table, 3.17 x 2.19 m (since 2026-11-14: the owner,
"make the map bigger" and "add another higher up section or make the higher up section bigger"; it was 2.19 x 1.50).
Every model is built in the ARENA'S OWN PLACE (the table's middle is the origin), so the game puts each at (0, 0) unturned.
Arena coordinates are x east, z south; here X = x / 347 and Y = -z / 347 (a model's -Y side is its south).
  bbtable   the steel top with its raised front edge, legs, an undershelf
  bbbins    five steel ingredient pans along the back wall: mozzarella, tomato sauce, pepperoni, olives, mushrooms
  bbboxes   five stacks of three pizza boxes along the south wall; a torn-off lid leaning on their west end: the ramp up, as wide as the
            stacks are deep; at their east end three more stacks, each one box taller than the last, with a baking sheet laid up them:
            the ramp from the boxes (42) to the top (84)
  bbblock   a butcher's block along the east wall; a bread board leaning on its whole north end: the way down to the table; on its south
            end a big wedge of hard cheese, rind up: the ramp from the block (42) to the top (84); in the corner three stacked dough
            trays with a lid: the top (84)
  bbisle    the island: two crates of tomatoes with a cutting board across them (42), a baking sheet leaning on its whole east side and
            a bread board on its whole south side: two ways up and down
  bbprops   a pepper mill, a rolling pin, a stack of plates, two big cans of tomatoes, a bag of flour
  (2026-11-13, the owner's play-test: ramps the full width of their ledges, nothing in a ramp's way; kept in the new layout)
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
X, Z, H, H2 = 550, 380, 42, 84                                # the table's half size, the raised route's height, the top's
def want(n): return not ONLY or n in ONLY
def start():
    """a fresh scene; with CR_CPU set the baking and the check pictures are done on the processor (the graphics card runs out of memory
    when the game's own tests are using it at the same time)"""
    s = reset()
    if os.environ.get('CR_CPU'): s.cycles.device = 'CPU'
    return s
def ax(x): return x / U
def ay(z): return -z / U
def abox(name, x0, x1, z0, z1, h0, h1, m, bev=.003, seg=2):
    """a box given in arena units (x east, z south, heights)"""
    return box(name, ((x1 - x0) / U, (z1 - z0) / U, (h1 - h0) / U), ((x0 + x1) / 2 / U, -(z0 + z1) / 2 / U, (h0 + h1) / 2 / U), m, bev, seg)


def aramp(name, x0, x1, z0, z1, h0, h1, axis, t, m):
    """a flat sheet `t` metres thick whose TOP is the game's ramp exactly: from h0 at the low x (axis 'x') or low z (axis 'z') to h1"""
    ha, hb, hc, hd = (h0, h1, h1, h0) if axis == 'x' else (h0, h0, h1, h1)
    V = [(ax(x0), ay(z0), ha / U), (ax(x1), ay(z0), hb / U), (ax(x1), ay(z1), hc / U), (ax(x0), ay(z1), hd / U)]
    return mesh(name, V + [(v[0], v[1], v[2] - t) for v in V], [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)], m, False)


def skirts(P, name, x0, x1, z0, z1, h0, h1, axis, m, drop=.5):
    """the two sides of a leaning ramp closed in down to the table (a board each side, 1.2 thick): the game's ramp is solid underneath,
    so a kart beside it must see something there, not look in under the sheet"""
    lo = lambda h: max(0.0, h - drop) / U
    if axis == 'x':
        for k, (a, b) in enumerate(((z0, z0 + 1.2), (z1 - 1.2, z1))):
            P.append(prism(f'{name}skirt{k}', [(ax(x0), 0), (ax(x1), 0), (ax(x1), lo(h1)), (ax(x0), lo(h0))], 'Y', ay(a), ay(b), m))
    else:
        for k, (a, b) in enumerate(((x0, x0 + 1.2), (x1 - 1.2, x1))):
            P.append(prism(f'{name}skirt{k}', [(ay(z0), 0), (ay(z1), 0), (ay(z1), lo(h1)), (ay(z0), lo(h0))], 'X', ax(a), ax(b), m))


def check(o, x0, x1, z0, z1, h1, tol=1.5):
    """the part's own box against the game's shape, in arena units: says so when what is drawn and what is solid differ by more than `tol`"""
    bpy.context.view_layer.update(); lo, hi = bounds(o)
    got = (lo.x * U, hi.x * U, -hi.y * U, -lo.y * U, hi.z * U); want_ = (x0, x1, z0, z1, h1)
    bad = [f'{n} {g:.1f} for {w:.1f}' for n, g, w in zip(('x0', 'x1', 'z0', 'z1', 'top'), got, want_) if abs(g - w) > tol]
    print(('SHAPE WARNING ' if bad else 'shape ok ') + o.name + (': ' + ', '.join(bad) if bad else ''))


def mats():
    return dict(steel=mat('bsteel', hexcol('#c2c6ca'), .35, metal=.8), card=mat('bcard', hexcol('#c79a5e'), .85), cardin=mat('bcardin', hexcol('#e9dcc2'), .9), wood=mat('bwood', hexcol('#c9a26c'), .5),
                dark=mat('bwoodd', hexcol('#5a3a22'), .45), plate=mat('bplate', hexcol('#f4f1ea'), .25), cheese=mat('bcheese', hexcol('#f3ecd2'), .6), sauce=mat('bsauce', hexcol('#b3261c'), .25),
                pep=mat('bpep', hexcol('#a8321e'), .5), olive=mat('bolive', hexcol('#1c1a17'), .3), oliveg=mat('boliveg', hexcol('#6f7a2a'), .35), mush=mat('bmush', hexcol('#d9c8a8'), .7), black=mat('gblack', hexcol('#0e0f11'), .5),
                tray=mat('btray', hexcol('#8f969c'), .55), can=mat('bcan', hexcol('#b3261c'), .35), canl=mat('bcanl', hexcol('#f3ead2'), .6), sack=mat('bsack', hexcol('#e6d8bb'), .92),
                tom=mat('btom', hexcol('#c9281c'), .28), green=mat('bgreen', hexcol('#4e7a2c'), .6), alu=mat('balu', hexcol('#b9bdc1'), .42, metal=.6), rind=mat('brind', hexcol('#d8a548'), .55))


def sheet_pan(P, name, x0, x1, z0, z1, h0, h1, axis, M):
    """a baking sheet lying as a ramp: the game's ramp is its floor; a low rolled rim along its two long sides (lower than a step:
    looks only) and none across its ends, where the karts drive on and off"""
    P.append(aramp(name, x0, x1, z0, z1, h0, h1, axis, .004, M['alu']))
    r = 2.2                                                  # the rim's height above the sheet, in game units
    if axis == 'x':
        for k, zz in enumerate((z0, z1)):
            a, b = (zz, zz + 2.4) if k == 0 else (zz - 2.4, zz)
            V = [(ax(x0), ay(a), h0 / U), (ax(x1), ay(a), h1 / U), (ax(x1), ay(b), h1 / U), (ax(x0), ay(b), h0 / U)]
            P.append(mesh(f'{name}rim{k}', V + [(v[0], v[1], v[2] + r / U) for v in V], [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)], M['alu'], False))
    else:
        for k, xx in enumerate((x0, x1)):
            a, b = (xx, xx + 2.4) if k == 0 else (xx - 2.4, xx)
            V = [(ax(a), ay(z0), h0 / U), (ax(b), ay(z0), h0 / U), (ax(b), ay(z1), h1 / U), (ax(a), ay(z1), h1 / U)]
            P.append(mesh(f'{name}rim{k}', V + [(v[0], v[1], v[2] + r / U) for v in V], [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)], M['alu'], False))


# ---------------- the table
if want('bbtable'):
    s = start(); M = mats(); P = []
    top = abox('top', -X - 8, X, -Z, Z, -14, 0, M['steel'], .004, 2); P.append(top); check(top, -X - 8, X, -Z, Z, 0)
    edge = abox('edge', -X - 8, -X, -Z, Z, -14, 7, M['steel'], .006, 3); P.append(edge); check(edge, -X - 8, -X, -Z, Z, 7)   # the raised front edge (west): a kart on its wheels cannot get over it
    for sx in (-X + 12, 0, X - 20):                                                                         # six legs: it is over three metres long
        for sz in (-Z + 20, Z - 20):
            leg = abox(f'leg{sx}{sz}', sx - 8, sx + 8, sz - 8, sz + 8, -312, -14, M['steel'], .004, 2); P.append(leg); joined(leg, top)
            P.append(abox(f'foot{sx}{sz}', sx - 10, sx + 10, sz - 10, sz + 10, -312, -304, M['black'], .003, 1))
    P.append(abox('shelf', -X + 4, X - 12, -Z + 12, Z - 12, -232, -226, M['steel'], .004, 1))
    for sz in (-Z + 14, Z - 22): P.append(abox(f'rail{sz}', -X + 12, X - 20, sz, sz + 8, -40, -30, M['steel'], .003, 1))
    finish_model('bbtable', P, 12.0, views=((-140, 22),), floor=False)

# ---------------- the ingredient pans
if want('bbbins'):
    s = start(); M = mats(); P = []; r = np.random.RandomState(5)
    fills = ('cheese', 'sauce', 'pep', 'olive', 'mush')
    for i in range(5):
        x0 = -364 + i * 144; x1 = x0 + 100; z0, z1 = -332, -270; cx, cy = ax((x0 + x1) / 2), ay((z0 + z1) / 2); w, d = 100 / U, 62 / U
        # a steel pan: four walls, a floor, a rolled lip
        for nm, (a0, a1, b0, b1) in (('w', (x0, x0 + 1.4, z0, z1)), ('e', (x1 - 1.4, x1, z0, z1)), ('n', (x0, x1, z0, z0 + 1.4)), ('s', (x0, x1, z1 - 1.4, z1))):
            P.append(abox(f'pan{i}{nm}', a0, a1, b0, b1, 0, 36, M['steel'], .0015, 1))
        lip = abox(f'lip{i}', x0 - 1.4, x1 + 1.4, z0 - 1.4, z1 + 1.4, 33.6, 36, M['steel'], .003, 2); P.append(lip); check(lip, x0, x1, z0, z1, 36)
        P.append(abox(f'in{i}', x0 + 1.2, x1 - 1.2, z0 + 1.2, z1 - 1.2, 32.0, 34.4, M['black'], 0))               # (well under the filling: at 36.2 it showed through the sauce's ripples)
        f = fills[i]
        if f == 'sauce':
            bpy.ops.mesh.primitive_grid_add(x_subdivisions=28, y_subdivisions=18, size=1, location=(cx, cy, 36.4 / U)); o = bpy.context.object; o.name = 'sauce'; o.scale = (w - .009, d - .009, 1); apply_scale(o); o.data.materials.append(M['sauce'])
            for v in o.data.vertices: v.co.z += .0016 * math.sin(v.co.x * 90 + 1) * math.cos(v.co.y * 70) + .0012 * math.sin(v.co.y * 140 + v.co.x * 40)
            smooth(o); P.append(o)
        else:
            base = abox(f'bed{i}', x0 + 1.4, x1 - 1.4, z0 + 1.4, z1 - 1.4, 30, 36.3, M['cheese'] if f == 'cheese' else M['pep'] if f == 'pep' else M['olive'] if f == 'olive' else M['mush'], 0); P.append(base)
            n = dict(cheese=200, pep=46, olive=90, mush=60)[f]
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
    finish_model('bbbins', P, 7.0, views=((-25, 28),), floor=True)

# ---------------- the pizza boxes: five stacks of three; a torn-off lid as the ramp up; three taller stacks and a baking sheet up to the top
if want('bbboxes'):
    s = start(); M = mats(); P = []; r = np.random.RandomState(9)

    def stack(tag, a0_, a1_, b0, b1, n):
        """n pizza boxes on top of each other, each 14 high, the upper ones a little out of true (inside the game's shape)"""
        for j in range(n):
            dx, tw = (r.rand() - .5) * 2.4 * (0 < j < n - 1), 0
            a0, a1 = a0_ + .15 - dx * .5, a1_ - .15 - dx * .5
            b = abox(f'box{tag}{j}', a0, a1, b0 + .4, b1 - .4, j * 14 + .15, (j + 1) * 14 - .15, M['card'], .002, 1); P.append(b)
            P.append(abox(f'flap{tag}{j}', a0 - .25, a1 + .25, b0 - .2, b0 + .6, j * 14 + 9.5, (j + 1) * 14 - .1, M['card'], .001, 1))             # the lid's front flap, tucked down
            P.append(abox(f'seam{tag}{j}', a0 + 1, a1 - 1, b0 + .1, b0 + .5, j * 14 + 8.6, j * 14 + 9.2, M['cardin'], 0))                             # the lid's edge shows as a paler line
        return b

    x0, x1, z0, z1 = -360, 250, 240, 380; n = 5; wx = (x1 - x0) / n
    for i in range(n):
        tb = stack(f's{i}', x0 + i * wx, x0 + (i + 1) * wx, z0, z1, 3)
        if i in (0, n - 1): check(tb, x0 + i * wx, x0 + (i + 1) * wx, z0, z1, H)
    # the ramp up from the table: one lid torn off, its flaps still on
    rx0, rx1, rz0, rz1 = -500, -360, 240, 380
    lid = aramp('lid', rx0, rx1, rz0, rz1, 0, H, 'x', .004, M['cardin']); P.append(lid); check(lid, rx0, rx1, rz0, rz1, H); skirts(P, 'lid', rx0, rx1, rz0, rz1, 0, H, 'x', M['card'])
    for k, zz in enumerate((rz0, rz1)):                                                                      # its side flaps stand up a little: low kerbs along the ramp (looks only: lower than a step)
        P.append(mesh(f'lidflap{k}', [(ax(rx0), ay(zz), 0), (ax(rx1), ay(zz), H / U), (ax(rx1), ay(zz), H / U + .012), (ax(rx0), ay(zz), .012)], [(0, 1, 2, 3), (3, 2, 1, 0)], M['card'], False))
    P.append(abox('prop', rx1 - 26, rx1 - 6, rz0 + 6, rz1 - 6, 0, 30, M['card'], .002, 1))                   # what holds it up: a folded box underneath
    # the ramp on up to the top: three more stacks, 3, 4 and 5 boxes high, and a baking sheet laid up them from the boxes (42) to the top (84)
    sx0, sx1 = 250, 380; sw = (sx1 - sx0) / 3
    for i in range(3): stack(f'u{i}', sx0 + i * sw, sx0 + (i + 1) * sw, z0, z1, 3 + i)
    sheet_pan(P, 'sheet', sx0, sx1, z0, z1, H, H2, 'x', M)
    check(P[-3], sx0, sx1, z0, z1, H2)
    finish_model('bbboxes', P, 9.0, views=((-150, 24), (-40, 22)), floor=True)

# ---------------- the butcher's block, the bread board down from it, the cheese wedge up from it, the dough trays (the top)
if want('bbblock'):
    s = start(); M = mats(); P = []; r = np.random.RandomState(3)
    x0, x1, z0, z1 = 380, 550, -100, 240                     # (the block runs on under the cheese: the game's wedge is solid down to the table)
    n = 10; sw = (x1 - x0) / n
    for i in range(n):                                       # end-grain strips glued up, each its own tone
        b = abox(f'strip{i}', x0 + i * sw, x0 + (i + 1) * sw, z0, z1, 6, H, M['wood'], .0015, 1); k = .8 + r.rand() * .2; b['tint'] = (k, k * .98, k * .95); P.append(b)
    check(P[0], x0, x0 + sw, z0, z1, H)
    for sx in (x0 + 10, x1 - 22):
        for sz in (z0 + 10, z1 - 22): P.append(abox(f'bfoot{sx}{sz}', sx, sx + 12, sz, sz + 12, 0, 6.2, M['dark'], .002, 1))
    P.append(abox('skirt', x0 + 6, x1 - 6, z0 + 6, z1 - 6, 2, 6.2, M['dark'], 0))
    # the bread board: it leans from the table up to the block's top, across the block's whole north end
    px0, px1, pz0, pz1 = 380, 550, -230, -100
    bread = aramp('blade', px0, px1, pz0, pz1, 0, H, 'z', .008, M['wood']); P.append(bread); check(bread, px0, px1, pz0, pz1, H); skirts(P, 'blade', px0, px1, pz0, pz1, 0, H, 'z', M['dark'], 2.5)
    P.append(abox('chock', px0 + 8, px1 - 8, pz1 - 30, pz1 - 4, 0, 30, M['dark'], .002, 1))
    # the wedge of hard cheese on the block's south end: its rind is the ramp, from the block (42) at z 110 up to the top (84) at z 240
    wz0, wz1 = 110, 240
    rind = aramp('rind', x0, x1, wz0, wz1, H, H2, 'z', .004, M['rind']); P.append(rind); check(rind, x0, x1, wz0, wz1, H2)
    P.append(prism('cheese', [(ay(wz0 + 10), H / U), (ay(wz1), H / U), (ay(wz1), (H2 - 1) / U)], 'X', ax(x0 + .4), ax(x1), M['cheese']))   # (just under the rind everywhere)
    # the top: three dough trays stacked in the corner, 28 high each, the lid of the uppermost flat at 84
    tx0, tx1, tz0, tz1 = 380, 550, 240, 380
    for j in range(3):
        b0 = j * 28
        body = abox(f'tray{j}', tx0 + 1.3, tx1 - 1.3, tz0 + 1.3, tz1 - 1.3, b0, b0 + 24, M['tray'], .004, 2); P.append(body)
        rim = abox(f'trayrim{j}', tx0, tx1, tz0, tz1, b0 + 22, b0 + 28, M['tray'], .003, 2); P.append(rim); joined(rim, body)
        for q in range(7):                                    # the ribs down its long sides
            xx = tx0 + 14 + q * (tx1 - tx0 - 28) / 6
            P.append(abox(f'rib{j}{q}', xx - 1.6, xx + 1.6, tz0 + .1, tz0 + 1.6, b0 + 1, b0 + 22.5, M['tray'], .001, 1))
        for q in range(6):                                    # and its ends
            zz = tz0 + 14 + q * (tz1 - tz0 - 28) / 5
            P.append(abox(f'ribw{j}{q}', tx0 + .1, tx0 + 1.6, zz - 1.6, zz + 1.6, b0 + 1, b0 + 22.5, M['tray'], .001, 1))
    check(P[-1 - 13], tx0, tx1, tz0, tz1, H2)
    finish_model('bbblock', P, 9.0, views=((-120, 24), (-60, 20)), floor=True)

# ---------------- the island: two crates of tomatoes, a cutting board across them, a baking sheet down its east side, a bread board down its south side
if want('bbisle'):
    s = start(); M = mats(); P = []; r = np.random.RandomState(11)
    x0, x1, z0, z1 = -420, -200, -170, -10; CH = 37           # the crates are 37 high, the board on them 5 thick: 42
    for c in range(2):
        a0, a1 = (x0, (x0 + x1) / 2) if c == 0 else ((x0 + x1) / 2, x1)
        # a slatted wooden crate: four corner posts, a floor, three slats on each side with gaps between them
        for sx in (a0, a1 - 5):
            for sz in (z0, z1 - 5): P.append(abox(f'post{c}{sx}{sz}', sx, sx + 5, sz, sz + 5, 0, CH, M['wood'], .0015, 1))
        P.append(abox(f'floor{c}', a0 + 1, a1 - 1, z0 + 1, z1 - 1, 1.5, 4, M['wood'], .001, 1))
        for q in range(3):
            h0 = 3 + q * 12; h1 = h0 + 9
            for nm, (p0, p1, b0, b1) in (('n', (a0, a1, z0, z0 + 2)), ('s', (a0, a1, z1 - 2, z1)), ('w', (a0, a0 + 2, z0, z1)), ('e', (a1 - 2, a1, z0, z1))):
                sl = abox(f'slat{c}{q}{nm}', p0, p1, b0, b1, h0, h1, M['wood'], .001, 1); k = .82 + r.rand() * .18; sl['tint'] = (k, k * .97, k * .93); P.append(sl)
        # tomatoes, a layer and a half of them: seen through the gaps
        nxt, nzt = 5, 7
        for layer in range(2):
            for i in range(nxt):
                for j in range(nzt):
                    if layer == 1 and (i + j) % 2: continue
                    px = a0 + 12 + i * (a1 - a0 - 24) / (nxt - 1) + (r.rand() - .5) * 4 + layer * 5; pz = z0 + 13 + j * (z1 - z0 - 26) / (nzt - 1) + (r.rand() - .5) * 4
                    rr = 9.0 + r.rand() * 1.4; hh = 4 + rr * .86 + layer * 10
                    if hh + rr * .9 > CH - 1: continue
                    P.append(ball(f'tom{c}{layer}{i}{j}', rr / U, (ax(px), ay(pz), hh / U), M['tom'], (1, 1, .86), 12, 8))
                    if layer == 1 or r.rand() < .3: P.append(ball(f'stalk{c}{layer}{i}{j}', 2.4 / U, (ax(px), ay(pz), (hh + rr * .82) / U), M['green'], (1, 1, .35), 6, 4))
    board = abox('iboard', x0, x1, z0, z1, CH, H, M['dark'], .0025, 2); P.append(board); check(board, x0, x1, z0, z1, H)
    # the two ramps, each across the whole of its side: down the east side a baking sheet, down the south side a bread board
    sheet_pan(P, 'isheet', -200, -70, z0, z1, H, 0, 'x', M); check(P[-3], -200, -70, z0, z1, H); skirts(P, 'isheet', -200, -70, z0, z1, H, 0, 'x', M['wood'], 1.2)
    P.append(abox('ichockE', -196, -176, z0 + 8, z1 - 8, 0, 28, M['wood'], .002, 1))
    ib = aramp('ibread', x0, x1, -10, 120, H, 0, 'z', .008, M['wood']); P.append(ib); check(ib, x0, x1, -10, 120, H); skirts(P, 'ibread', x0, x1, -10, 120, H, 0, 'z', M['dark'], 2.5)
    P.append(abox('ichockS', x0 + 8, x1 - 8, -6, 14, 0, 28, M['dark'], .002, 1))
    finish_model('bbisle', P, 8.0, views=((-140, 26), (130, 22)), floor=True)

# ---------------- a pepper mill, a rolling pin, a stack of plates, two big cans of tomatoes, a bag of flour
if want('bbprops'):
    s = start(); M = mats(); P = []; r = np.random.RandomState(4)
    mx, mz = ax(200), ay(10)
    P.append(lathe('mill', [(0, 0), (.032, 0), (.034, .01), (.030, .04), (.022, .09), (.026, .13), (.031, .16), (.026, .19), (.024, .215), (.031, .225), (.033, .245), (.024, .258), (0, .26)], 28, M['dark'], (mx, mz, 0)))
    P.append(ball('millknob', .011, (mx, mz, .268), M['steel'], (1, 1, .8), 12, 8)); P.append(lathe('millring', [(.0315, .160), (.0335, .162), (.0335, .170), (.0315, .172)], 28, M['steel'], (mx, mz, 0)))
    check(P[-3], 200 - 12, 200 + 12, 10 - 12, 10 + 12, 90)
    # the rolling pin lies along x: box [40,160] x [110,128], 17 high; its handles [7,40] and [160,193]
    py_, pz_ = ay(119), 8.5 / U
    pin = rod('pin', 8.5 / U, 120 / U, (ax(100), py_, pz_), M['wood'], 'X', 24); P.append(pin); check(pin, 40, 160, 110.5, 127.5, 17)
    for sx in (-1, 1): P.append(tube(f'pinh{sx}', [(ax(100) + sx * 60 / U, py_, pz_), (ax(100) + sx * 74 / U, py_, pz_), (ax(100) + sx * 92 / U, py_, pz_)], .011, M['wood'], 0, 10))
    for sx in (-1, 1): P.append(abox(f'pinchock{sx}', 100 + sx * 40 - 3, 100 + sx * 40 + 3, 110, 128, 0, 2.2, M['dark'], 0))    # two slips of wood keep it from rolling
    # six plates
    cx, cz = ax(20), ay(-160)
    for i in range(6): P.append(lathe(f'plate{i}', [(0, .001), (.055, .001), (.075, .004), (.1035, .0095), (.1035, .0105), (.075, .0058), (.055, .003), (0, .003)], 36, M['plate'], (cx + (i % 2) * .001, cz, i * .0104)))
    check(P[-1], 20 - 36, 20 + 36, -160 - 36, -160 + 36, 22)
    # two big cans of tomatoes (15.5 cm across, 17.5 cm tall): a ribbed steel can with a paper label round it
    for ci, (qx, qz) in enumerate(((-30, 50), (290, 150))):
        R_, Hc = 27 / U, 61 / U; loc = (ax(qx), ay(qz), 0)
        prof = [(0, 0), (R_, 0), (R_, .004), (R_ - .0012, .006)] + [(R_ - .0012 - (.0008 if k % 2 else 0), .010 + k * (.012 - .004) / 2) for k in range(4)] + [(R_ - .0012, Hc - .030)] + \
               [(R_ - .0012 - (.0008 if k % 2 else 0), Hc - .028 + k * .004) for k in range(4)] + [(R_ - .0012, Hc - .006), (R_, Hc - .004), (R_, Hc), (R_ - .003, Hc), (R_ - .004, Hc - .003), (0, Hc - .003)]
        can = lathe(f'can{ci}', prof, 40, M['steel'], loc); P.append(can); check(can, qx - 27, qx + 27, qz - 27, qz + 27, 61)
        P.append(lathe(f'label{ci}', [(R_ - .0009, .030), (R_ - .0003, .031), (R_ - .0003, Hc - .034), (R_ - .0009, Hc - .033)], 40, M['can'], loc))
        P.append(lathe(f'band{ci}', [(R_ - .0005, Hc * .42), (R_, Hc * .425), (R_, Hc * .62), (R_ - .0005, Hc * .625)], 40, M['canl'], loc))
    # a bag of flour lying on its side: [230,300] x [-190,-140], 40 high; paper, a little puffed, its top fold glued down, a printed band
    bx0, bx1, bz0, bz1, BH = 230, 300, -190, -140, 40
    bag = abox('sack', bx0, bx1, bz0, bz1, 0, BH, M['sack'], .0085, 4); P.append(bag); check(bag, bx0, bx1, bz0, bz1, BH)
    P.append(abox('sackband', bx0 + 22, bx1 - 22, bz0 - .15, bz1 + .15, 1.5, BH + .15, M['can'], .0085, 4))
    P.append(abox('sackfold', bx1 - 9, bx1 - .4, bz0 + 3, bz1 - 3, BH - .4, BH + 1.6, M['sack'], .002, 2))
    finish_model('bbprops', P, 7.0, views=((-30, 22), (150, 24)), floor=True)
