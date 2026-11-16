"""Sandbox's mechanic's shop (web SB_SHOP, PC sandbox.gd SHOP): a real-size workshop that the game shrinks to kart scale.
The owner, 2026-11-16, with a video of a car pulling into a mechanic's garage: "that is what i want for the garage in sandbox. it should
be cool like in the video when you pull in". Original design (no names or logos from anywhere): our own sign is drawn by the game.
At kart scale one game unit is about 0.146 m (a kart is 13 units across, a car about 1.9 m), so the shop's footprint in the game,
100 x 90 units and 46 high, is this building: 14.6 m wide, 13.1 m deep, 6.7 m to the top of the parapet.
  mshop      the building and everything in it (static)
  mshopdoor  the roller door's curtain alone, 5.2 x 4.4 m, standing on the floor at the origin (the game rolls it up into the box)
Front is -Y (the door). Materials are keys for the game's own (shopMats in the game). The two picture parts, msign and mlogo, have
0..1 UVs over the whole part (the game passes a tile of 100 so they stay that way).
Run: D:/blender/blender.exe --background --python D:/crust-rush/source/tools/blender/mechshop.py [-- mshop | mshopdoor]
"""
import sys, math, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
import numpy as np
from mathutils import Vector
from crlib import *

ONLY = [a for a in sys.argv[sys.argv.index('--') + 1:]] if '--' in sys.argv else []
def want(n): return not ONLY or n in ONLY

W, D, HW, HT = 14.6, 13.1, 6.1, 6.7          # outside width, depth, wall height inside, top of the parapet
T = .3                                        # wall thickness
DW, DH = 5.2, 4.4                             # the door opening
YF, YB = -D / 2, D / 2                        # the front and back faces


def mats():
    c = lambda n, h, r=.6, m=0.0: mat(n, hexcol(h), r, m)
    return dict(conc=c('mconc', '#8f8c86', .75), block=c('mblock', '#d9d6cf', .85), brick=c('mbrick', '#9a5a44', .85), yel=c('myel', '#f2c21b', .45),
                red=c('mred', '#b8261d', .35), blue=c('mblue', '#24508f', .4), steel=c('msteel', '#3a3f45', .5), galv=c('mgalv', '#a0a6ac', .45, 1.0),
                chrome=c('mchrome', '#cfd2d6', .2, 1.0), rubber=c('mrubber', '#1d1d1d', .9), wood=c('mwood', '#b88a55', .6), lamp=c('mlamp', '#fffbe8', .3),
                sign=c('msign', '#f3ead8', .5), logo=c('mlogo', '#e8e0cc', .6), glass=c('mglass', '#8fb6c8', .1), black=c('mblack', '#121315', .6),
                door=c('mdoor', '#b9bec4', .45, .6), roof=c('mroof', '#55585c', .8), peg=c('mpeg', '#c7b08a', .8), green=c('mgreen', '#2f6b3d', .45),
                poster1=c('mposter1', '#c84a30', .6), poster2=c('mposter2', '#2c5e9e', .6), poster3=c('mposter3', '#e0b030', .6), safety=c('msafety', '#f2c21b', .6),
                clock=c('mclock', '#f4f1ea', .4), tv=c('mtv', '#101418', .15), cone=c('mcone', '#ff6a1a', .5), tarp=c('mtarp', '#2f6f6a', .8))


def uv01(o, ax=0, flip=False):
    """0..1 over the part's face (across: X when ax=0, Y when ax=1; up: Z): a picture laid over the whole part.
    flip mirrors it, for a picture seen from the other side of its axis"""
    me = o.data
    if not me.uv_layers: me.uv_layers.new(name='UVMap')
    uv = me.uv_layers.active.data; lo, hi = bounds(o)
    for l in me.loops:
        c = o.matrix_world @ me.vertices[l.vertex_index].co
        u = (c[ax] - lo[ax]) / max(1e-6, hi[ax] - lo[ax])
        uv[l.index].uv = (1 - u if flip else u, (c.z - lo.z) / max(1e-6, hi.z - lo.z))
    o['keep_uv'] = 1
    return o


def details(M, add):
    """what the owner asked for after the first version (2026-11-16): "add more details inside the mechanic shop, stuff on the walls and
    stuff sitting around the shop similar to the shop in the video". Inner wall faces: x = +-7.0, back y = 6.25, front y = -6.25."""
    XL, XR, YBk, YFr = -W / 2 + T, W / 2 - T, YB - T, YF + T
    pic = lambda n, key, size, loc, ax, flip: add(uv01(box(n, size, loc, M[key], .004, 1), ax, flip))
    # ---- pictures on the walls (drawn by the game): posters, a safety sign, a clock face, a TV
    pic('posterL1', 'poster1', (.03, 1.0, 1.4), (XL + .02, -3.6, 3.6), 1, False)
    pic('posterL2', 'poster2', (.03, 1.0, 1.4), (XL + .02, -1.0, 3.6), 1, False)
    pic('posterR1', 'poster3', (.03, 1.2, .9), (XR - .02, 4.6, 3.2), 1, True)
    pic('posterF1', 'poster2', (1.0, .03, 1.4), (-5.2, YFr + .02, 3.3), 0, True)
    pic('posterF2', 'poster1', (1.0, .03, 1.4), (5.2, YFr + .02, 3.3), 0, True)
    pic('safety', 'safety', (.9, .03, .6), (-3.6, YFr + .02, 2.6), 0, True)
    pic('safety2', 'safety', (.03, .9, .6), (XR - .02, -5.0, 3.0), 1, True)
    add(rod('clockRim', .34, .08, (5.6, YBk - .04, 4.1), M['black'], 'Y', 28)); pic('clock', 'clock', (.6, .02, .6), (5.6, YBk - .09, 4.1), 0, False)
    add(box('tvF', (1.5, .1, .9), (-5.9, YBk - .06, 3.4), M['black'], .02, 2)); pic('tv', 'tv', (1.36, .02, .78), (-5.9, YBk - .12, 3.4), 0, False)
    # ---- the electrics: a panel, a switch box, conduit up to the roof
    add(box('epanel', (.7, .18, .9), (6.4, YBk - .1, 1.7), M['galv'], .02, 2)); add(box('ebox', (.25, .12, .3), (5.8, YBk - .07, 1.4), M['galv'], .01, 2))
    for x in (6.2, 6.4, 6.6): add(rod(f'cond{x}', .025, HW - 2.15, (x, YBk - .05, 2.15 + (HW - 2.15) / 2), M['galv'], 'Z', 8))
    # ---- a fire extinguisher by the door, on its bracket
    add(rod('ext', .09, .5, (-2.95, YFr + .14, 1.15), M['red'], 'Z', 16)); add(rod('extTop', .03, .1, (-2.95, YFr + .14, 1.45), M['black'], 'Z', 8))
    add(bar('extHose', (-2.92, YFr + .14, 1.45), (-2.85, YFr + .22, 1.05), .012, .012, M['black'], 6)); add(box('extBr', (.22, .06, .1), (-2.95, YFr + .03, 1.15), M['steel'], .005, 1))
    # ---- hanging tyres on the right wall: a rail and four tyres stood on edge
    add(box('tyreRail', (.1, 3.2, .1), (XR - .15, -1.6, 3.9), M['steel'], .01, 1))
    for i in range(4):
        y = -2.9 + i * .85
        bpy.ops.mesh.primitive_torus_add(major_radius=.3, minor_radius=.11, major_segments=26, minor_segments=8, location=(XR - .3, y, 3.55), rotation=(0, math.pi / 2, 0))
        t = bpy.context.object; t.name = f'htyre{i}'; t.data.materials.append(M['rubber']); smooth(t); add(t)
    # ---- shelving on the back wall, right: boxes, oil cans, a battery
    for sx in (3.4, 5.2):
        for sy in (0, .5): add(box(f'bsP{sx}{sy}', (.05, .05, 2.6), (sx, YBk - .1 - sy, 1.42), M['galv'], .005, 1))
    for z in (.4, 1.1, 1.8, 2.5):
        add(box(f'bsB{z}', (1.85, .55, .03), (4.3, YBk - .35, z + .12), M['galv'], .005, 1))
    rs = np.random.RandomState(9)
    for zi, z in enumerate((.4, 1.1, 1.8, 2.5)):
        x = 3.55
        while x < 5.0:
            kind = rs.randint(3)
            if kind == 0: add(box(f'bsx{zi}{x:.2f}', (.36, .4, .3), (x + .18, YBk - .35, z + .29), M['wood'], .02, 2)); x += .42
            elif kind == 1:
                for j in range(3): add(rod(f'can{zi}{x:.2f}{j}', .07, .26, (x + .08, YBk - .25 - j * .16, z + .26), M['blue' if j % 2 else 'red'], 'Z', 12))
                x += .2
            else: add(box(f'bat{zi}{x:.2f}', (.3, .2, .22), (x + .15, YBk - .3, z + .24), M['black'], .02, 2)); x += .36
    # ---- the floor: an engine hoist, two tool carts, a tyre changer, axle stands, a drain pan, cones, a pallet of crates, a bin
    hx, hy = 4.9, -4.0
    for k in (-1, 1): add(box(f'hoistLeg{k}', (.12, 1.6, .1), (hx + k * .45, hy + .1, .2), M['yel'], .01, 1))
    add(box('hoistBase', (1.0, .14, .14), (hx, hy - .65, .22), M['yel'], .01, 1)); add(box('hoistMast', (.14, .14, 1.7), (hx, hy - .62, 1.1), M['yel'], .01, 1))
    add(bar('hoistBoom', (hx, hy - .62, 1.85), (hx, hy + .9, 1.65), .07, .06, M['yel'], 8)); add(bar('hoistRam', (hx, hy - .55, .8), (hx, hy + .1, 1.75), .04, .035, M['red'], 8))
    add(rod('hoistChain', .02, .5, (hx, hy + .9, 1.38), M['steel'], 'Z', 6)); add(box('hoistHook', (.08, .04, .12), (hx, hy + .9, 1.08), M['steel'], .01, 1))
    for k in (-1, 1):
        for j in (-1, 1): add(rod(f'hoistW{k}{j}', .06, .05, (hx + k * .45, hy + .1 + j * .7, .07), M['black'], 'X', 10))
    for n, (cx, cy) in enumerate(((2.7, 2.9), (-5.2, -5.1))):
        add(box(f'cart{n}', (.9, .5, .8), (cx, cy, .55), M['red'], .03, 3)); add(box(f'cartTop{n}', (.92, .52, .04), (cx, cy, .97), M['rubber'], .005, 1))
        for i in range(4): add(box(f'cartD{n}{i}', (.82, .02, .14), (cx, cy - .26, .27 + i * .18), M['chrome'], .005, 1))
        add(rod(f'cartH{n}', .015, .5, (cx + .5, cy, .9), M['chrome'], 'Y', 8))
        for k in (-1, 1):
            for j in (-1, 1): add(rod(f'cartW{n}{k}{j}', .05, .04, (cx + k * .38, cy + j * .19, .07), M['black'], 'Y', 10))
        add(box(f'cartBox{n}', (.4, .2, .18), (cx - .15, cy, 1.08), M['blue'], .02, 2)); add(bar(f'cartTool{n}', (cx + .1, cy - .1, 1.0), (cx + .35, cy + .1, 1.0), .015, .012, M['chrome'], 6))
    tx, ty = 5.9, 5.0
    add(box('tcBase', (.7, .9, .8), (tx, ty, .52), M['red'], .03, 3)); add(rod('tcTable', .38, .06, (tx, ty, .95), M['steel'], 'Z', 24))
    add(box('tcPost', (.12, .12, 1.1), (tx + .32, ty + .3, 1.4), M['steel'], .01, 1)); add(bar('tcArm', (tx + .32, ty + .3, 1.9), (tx, ty, 1.2), .04, .035, M['steel'], 8))
    for n, (sx, sy) in enumerate(((2.9, 4.6), (3.3, 4.6), (2.9, 5.0), (3.3, 5.0))):   # (out of the bay: they stood in the cinematic's view)
        add(bar(f'astand{n}', (sx, sy, .12), (sx, sy, .62), .1, .03, M['red'], 8)); add(box(f'astandT{n}', (.12, .12, .05), (sx, sy, .64), M['steel'], .01, 1))
    add(rod('drainPan', .4, .1, (-2.8, 3.5, .17), M['black'], 'Z', 24)); add(rod('drainPan2', .36, .02, (-2.8, 3.5, .215), M['steel'], 'Z', 24))
    for i, (cx, cy) in enumerate(((-3.6, 3.8), (-3.35, 4.1), (-3.75, 4.2))): add(box(f'oilc{i}', (.2, .12, .3), (cx, cy, .27), M['yel' if i % 2 else 'blue'], .02, 2))
    for i in range(2): add(box(f'jerry{i}', (.18, .45, .5), (XR - .45, -2.3 + i * .25, .37), M['green' if i else 'red'], .03, 3))
    for i, (cx, cy) in enumerate(((3.2, -5.5), (3.7, -5.8), (2.6, -5.9))):
        add(bar(f'cone{i}', (cx, cy, .14), (cx, cy, .82), .2, .025, M['cone'], 14)); add(box(f'coneB{i}', (.46, .46, .05), (cx, cy, .145), M['cone'], .01, 1))
        add(bar(f'coneS{i}', (cx, cy, .42), (cx, cy, .56), .14, .11, M['block'], 14))
    px, py = -6.0, 4.9
    add(box('pallet', (1.2, 1.0, .14), (px, py, .19), M['wood'], .01, 1))
    for i, (dx, dy, dz, s) in enumerate(((-.28, -.2, 0, .5), (.28, -.18, 0, .5), (0, .22, 0, .5), (-.05, -.15, .5, .42))):
        add(box(f'crate{i}', (s, s, s), (px + dx, py + dy, .26 + dz + s / 2), M['wood'], .02, 2))
    add(box('tarp', (.75, .6, .06), (px + .1, py + .1, 1.24), M['tarp'], .03, 3))
    add(rod('bin', .25, .7, (2.9, -6.0, .47), M['green'], 'Z', 18)); add(rod('binLid', .27, .05, (2.9, -6.0, .84), M['black'], 'Z', 18))
    add(bar('broom', (3.25, -6.1, .14), (3.4, -6.2, 1.5), .015, .015, M['wood'], 6)); add(box('broomH', (.35, .06, .1), (3.25, -6.1, .18), M['black'], .01, 1))
    # ---- on the workbench: a toolbox, a battery charger, a lamp, spray cans, a part
    BXc = XL + .4
    add(box('tbox', (.3, .55, .25), (BXc, .3, 1.14), M['red'], .02, 2)); add(box('tboxH', (.04, .35, .04), (BXc, .3, 1.29), M['black'], .01, 1))
    add(box('charger', (.3, .3, .22), (BXc, 1.3, 1.12), M['yel'], .02, 2))
    add(rod('lampB', .08, .03, (BXc - .1, 2.3, 1.03), M['black'], 'Z', 12)); add(bar('lampArm', (BXc - .1, 2.3, 1.04), (BXc + .05, 2.4, 1.5), .015, .015, M['black'], 6)); add(box('lampHd', (.18, .14, .1), (BXc + .1, 2.42, 1.48), M['black'], .02, 2))
    for i in range(3): add(rod(f'spray{i}', .035, .2, (BXc + .15, 3.3 + i * .09, 1.11), M['blue' if i == 1 else 'red'], 'Z', 10))
    add(rod('gear', .12, .05, (BXc + .05, 2.9, 1.04), M['chrome'], 'Z', 18))
    # ---- a wall fan high on the left wall, and strings of pennants under the beams
    add(rod('fanGuard', .38, .14, (XL + .25, 4.6, 4.7), M['galv'], 'X', 22)); add(box('fanMount', (.2, .2, .3), (XL + .1, 4.6, 4.7), M['steel'], .01, 1))
    cols = ('red', 'yel', 'blue', 'green')
    for si, (y0, y1) in enumerate(((-3.5, 3.5), (3.5, -3.5))):
        x0, x1 = (-6.6, 6.6)
        n = 22
        for i in range(n):
            f = (i + .5) / n; x = x0 + (x1 - x0) * f; y = y0 + (y1 - y0) * f; z = HW + .12 - 1.35 - math.sin(f * math.pi) * .55
            tri = prism(f'flag{si}{i}', [(-.11, 0), (.11, 0), (0, -.28)], 'Y', y - .006, y + .006, M[cols[(i + si) % 4]])
            tri.location = (x, 0, z); add(tri)
        add(tube(f'flagLine{si}', [(x0, y0, HW + .12 - 1.35), ((x0 + x1) / 2, (y0 + y1) / 2, HW + .12 - 1.9), (x1, y1, HW + .12 - 1.35)], .008, M['black'], fillet=4.0, verts=4, steps=10))


def shop():
    reset(); M = mats(); P = []; add = P.append
    # ---- the slab and the apron in front of the door
    add(box('slab', (W, D, .12), (0, 0, .06), M['conc'], .01, 1))
    add(box('apron', (DW + 4.4, 4.2, .08), (0, YF - 2.1, .04), M['conc'], .02, 2))
    for i in range(9):                                 # hazard stripes on the apron's edge kerbs
        for sx in (-1, 1):
            x = sx * (DW / 2 + 1.6); y = YF - .3 - i * .44
            add(box(f'kerb{sx}{i}', (.5, .42, .16), (x, y, .16), M['yel'] if i % 2 == 0 else M['black'], .02, 2))
    for sx in (-1, 1):                                 # bollards either side of the door
        for k, y in enumerate((YF - .6, YF - 2.6)):
            x = sx * (DW / 2 + .45)
            add(rod(f'boll{sx}{k}', .14, 1.1, (x, y, .63), M['yel'], 'Z', 16)); add(rod(f'bollcap{sx}{k}', .15, .06, (x, y, 1.2), M['black'], 'Z', 16))
            for z in (.85, 1.0): add(rod(f'bollband{sx}{k}{z}', .145, .05, (x, y, z), M['black'], 'Z', 16))
    # ---- painted lines on the floor inside: the lift bay and a walkway
    for sx in (-1, 1): add(box(f'bayL{sx}', (.12, 7.4, .006), (sx * 2.9, .6, .123), M['yel'], 0))
    for y in (-3.1, 4.3): add(box(f'bayE{y}', (5.92, .12, .006), (0, y, .123), M['yel'], 0))
    for i in range(10): add(box(f'walk{i}', (.5, .12, .006), (-5.0, -5.6 + i * 1.2, .123), M['yel'], 0))
    # ---- walls: back, sides, front with the door opening; brick to 1.1 m outside, painted block above and inside
    add(box('wallB', (W, T, HW), (0, YB - T / 2, HW / 2 + .12), M['block'], .01, 1))
    for sx in (-1, 1): add(box(f'wallS{sx}', (T, D - 2 * T, HW), (sx * (W / 2 - T / 2), 0, HW / 2 + .12), M['block'], .01, 1))
    sw = (W - DW) / 2
    for sx in (-1, 1): add(box(f'wallF{sx}', (sw, T, HW), (sx * (DW / 2 + sw / 2), YF + T / 2, HW / 2 + .12), M['block'], .01, 1))
    add(box('wallFtop', (DW, T, HW - DH), (0, YF + T / 2, DH + .12 + (HW - DH) / 2), M['block'], .01, 1))
    for sx in (-1, 1):                                 # the brick plinth outside, and a blue band at 4.9 m
        add(box(f'plF{sx}', (sw, .06, 1.1), (sx * (DW / 2 + sw / 2), YF - .03, .67), M['brick'], .005, 1))
        add(box(f'plS{sx}', (.06, D, 1.1), (sx * (W / 2 + .03), 0, .67), M['brick'], .005, 1))
        add(box(f'bandS{sx}', (.07, D + .14, .35), (sx * (W / 2 + .035), 0, 4.9), M['blue'], .01, 1))
    add(box('plB', (W + .12, .06, 1.1), (0, YB + .03, .67), M['brick'], .005, 1))
    add(box('bandF', (W + .14, .07, .35), (0, YF - .035, 4.9), M['blue'], .01, 1)); add(box('bandB', (W + .14, .07, .35), (0, YB + .035, 4.9), M['blue'], .01, 1))
    # ---- the roof: a slab on the walls, a parapet round it, steel beams under it inside
    add(box('roof', (W, D, .3), (0, 0, HW + .12 + .15), M['roof'], .01, 1))
    for sx in (-1, 1): add(box(f'parS{sx}', (.25, D, HT - HW - .12), (sx * (W / 2 - .125), 0, (HW + .12 + HT) / 2), M['block'], .01, 1))
    for sy in (-1, 1): add(box(f'parF{sy}', (W, .25, HT - HW - .12), (0, sy * (D / 2 - .125), (HW + .12 + HT) / 2), M['block'], .01, 1))
    for i in range(5):
        y = -4.8 + i * 2.4
        add(box(f'beam{i}', (W - 2 * T, .22, .5), (0, y, HW + .12 - .25), M['steel'], .01, 1))
        add(box(f'beamF{i}', (W - 2 * T, .34, .04), (0, y, HW + .12 - .52), M['steel'], .005, 1))
    # ---- strip lights hanging under the beams (the game makes mlamp glow)
    for i in range(4):
        y = -3.6 + i * 2.4
        for x in (-4.2, 0.0, 4.2):
            add(box(f'lampH{i}{x}', (1.6, .22, .1), (x, y, HW + .12 - 1.1), M['steel'], .01, 2)); add(box(f'lamp{i}{x}', (1.5, .14, .04), (x, y, HW + .12 - 1.17), M['lamp'], .005, 1))
            for k in (-1, 1): add(rod(f'lampW{i}{x}{k}', .008, .55, (x + k * .6, y, HW + .12 - .78), M['galv'], 'Z', 6))
    # ---- the door: its steel frame, the box the curtain rolls into, the guides
    for sx in (-1, 1): add(box(f'jamb{sx}', (.22, .4, DH + .1), (sx * (DW / 2 + .06), YF - .02, (DH + .1) / 2 + .1), M['steel'], .01, 2))
    add(box('dbox', (DW + .5, .7, .75), (0, YF - .3, DH + .12 + .38), M['galv'], .03, 3))
    add(box('dboxcap', (DW + .56, .76, .05), (0, YF - .3, DH + .12 + .78), M['steel'], .01, 1))
    # ---- the sign over the door and two wall lamps
    sg = box('sign', (7.6, .12, 1.5), (0, YF - .5, 5.75), M['sign'], .01, 1); add(uv01(sg))
    add(box('signback', (7.9, .2, 1.8), (0, YF - .38, 5.75), M['steel'], .02, 2))
    for sx in (-1, 1):
        for k in (-1, 1): add(box(f'signarm{sx}{k}', (.1, .5, .1), (sx * 3.2, YF - .2, 5.75 + k * .6), M['steel'], .01, 1))
        add(box(f'wlamp{sx}', (.5, .35, .25), (sx * (DW / 2 + 1.4), YF - .2, 3.9), M['black'], .03, 3)); add(box(f'wlampg{sx}', (.42, .3, .05), (sx * (DW / 2 + 1.4), YF - .22, 3.76), M['lamp'], .01, 1))
    for sx in (-1, 1): add(rod(f'downpipe{sx}', .07, HT - .3, (sx * (W / 2 + .15), YF + .4, (HT - .3) / 2), M['galv'], 'Z', 10))
    # ---- inside, the lift: two posts with their carriages and four swing arms, a ramp plate under each post
    LY = .6
    for sx in (-1, 1):
        x = sx * 1.85
        add(box(f'post{sx}', (.34, .34, 3.8), (x, LY, 1.9 + .12), M['blue'], .02, 2))
        add(box(f'postBase{sx}', (.7, .7, .04), (x, LY, .14), M['steel'], .01, 1))
        add(box(f'carr{sx}', (.44, .44, .7), (x - sx * .05, LY, .55), M['steel'], .02, 2))
        add(box(f'postTop{sx}', (.44, .44, .12), (x, LY, 3.92), M['steel'], .01, 1))
        for k in (-1, 1):                              # the arms swung in under where the car stands
            a0 = Vector((x - sx * .2, LY + k * .15, .3)); a1 = Vector((x - sx * 1.25, LY + k * 1.15, .3))
            add(bar(f'arm{sx}{k}', a0, a1, .07, .06, M['steel'], 10)); add(rod(f'pad{sx}{k}', .11, .08, (a1.x, a1.y, .36), M['rubber'], 'Z', 14))
        add(box(f'hose{sx}', (.04, .04, 3.5), (x + sx * .2, LY + .2, 1.9), M['black'], .01, 1))
    add(box('liftTop', (3.9, .22, .22), (0, LY, 4.05), M['blue'], .02, 2))
    add(box('ctrl', (.25, .2, .45), (2.3, LY - .3, 1.45), M['steel'], .02, 2)); add(box('ctrlB', (.12, .03, .08), (2.3, LY - .41, 1.5), M['red'], .005, 1))
    # ---- the left wall: a long workbench with a vice, a pegboard of tools over it, a roll cabinet, a compressor
    BX = -W / 2 + T
    add(box('bench', (.75, 4.2, .06), (BX + .4, 1.6, .98), M['wood'], .01, 2))
    for y in (-.4, 1.6, 3.6):
        add(box(f'bleg{y}', (.06, .06, .9), (BX + .1, y, .57), M['steel'], .005, 1)); add(box(f'blegf{y}', (.06, .06, .9), (BX + .7, y, .57), M['steel'], .005, 1))
    add(box('bshelf', (.7, 4.1, .03), (BX + .4, 1.6, .35), M['wood'], .005, 1))
    add(box('vice', (.18, .28, .16), (BX + .6, 3.0, 1.09), M['blue'], .02, 2)); add(rod('viceH', .015, .35, (BX + .6, 3.0 - .3, 1.07), M['chrome'], 'Y', 8))
    add(box('peg', (.03, 4.0, 1.4), (BX + .02, 1.6, 1.95), M['peg'], .005, 1))
    rs = np.random.RandomState(4)
    for i in range(16):                                 # spanners and screwdrivers on the board
        y = .0 + (i % 8) * .45 + rs.rand() * .1; z = 1.55 + (i // 8) * .55
        if i % 3: add(bar(f'tool{i}', (BX + .06, y, z - .18), (BX + .06, y, z + .18), .018, .013, M['chrome'], 8))
        else: add(box(f'tool{i}', (.03, .05, .3), (BX + .06, y, z), M['red'], .01, 2))
    for i in range(3): add(box(f'boxsh{i}', (.25, .3, .2), (BX + .2, -.2 + i * .45, 2.85), M['blue' if i % 2 else 'red'], .02, 2))
    add(box('cab', (.6, 1.1, 1.0), (BX + .35, -2.0, .62), M['red'], .03, 3))
    for i in range(5): add(box(f'cabd{i}', (.03, 1.0, .15), (BX + .66, -2.0, .3 + i * .18), M['chrome'], .005, 1))
    add(box('cabtop', (.62, 1.12, .04), (BX + .35, -2.0, 1.14), M['rubber'], .005, 1))
    add(rod('comp', .32, 1.2, (BX + .5, -3.8, .45), M['red'], 'Y', 18)); add(box('compM', (.4, .4, .3), (BX + .5, -3.8, .95), M['steel'], .03, 2))
    # ---- the right wall: tyre stacks, drums, shelving with boxes
    RX = W / 2 - T
    for k, (y, n) in enumerate(((-4.4, 4), (-3.6, 3), (3.2, 5))):
        for i in range(n):
            bpy.ops.mesh.primitive_torus_add(major_radius=.28, minor_radius=.11, major_segments=28, minor_segments=10, location=(RX - .45, y, .23 + .23 + i * .23))
            t = bpy.context.object; t.name = f'tyre{k}{i}'; t.data.materials.append(M['rubber']); smooth(t); add(t)
    for k, (y, m) in enumerate(((-1.6, 'blue'), (-1.0, 'red'), (-.4, 'blue'))):
        add(rod(f'drum{k}', .29, .88, (RX - .4, y, .56), M[m], 'Z', 20))
        for z in (.35, .78): add(rod(f'drumr{k}{z}', .30, .03, (RX - .4, y, z), M['steel'], 'Z', 20))
    for sy in (-1, 1):
        for sx2 in (0, 1): add(box(f'shpost{sy}{sx2}', (.05, .05, 2.4), (RX - .1 - sx2 * .55, 1.4 + sy * 1.0, 1.32), M['galv'], .005, 1))
    for z in (.5, 1.2, 1.9, 2.5):
        add(box(f'shboard{z}', (.6, 2.1, .03), (RX - .38, 1.4, z), M['galv'], .005, 1))
        for i in range(4):
            if (i + int(z * 10)) % 3: add(box(f'shbox{z}{i}', (.4, .38, .3), (RX - .38, .7 + i * .48, z + .17), M['wood' if i % 2 else 'blue'], .02, 2))
    # ---- the back wall: the logo panel (drawn by the game), a parts rack, a door to the office with a window
    lg = box('logo', (6.0, .05, 2.2), (0, YB - T - .03, 3.4), M['logo'], .005, 1); add(uv01(lg))
    add(box('logoF', (6.2, .06, 2.4), (0, YB - T - .01, 3.4), M['black'], .01, 1))
    add(box('odoor', (1.0, .06, 2.1), (-4.6, YB - T - .03, 1.17), M['steel'], .01, 2)); add(box('owin', (1.8, .06, 1.1), (-2.9, YB - T - .03, 1.7), M['glass'], .005, 1))
    add(box('owinF', (1.95, .07, 1.25), (-2.9, YB - T - .02, 1.7), M['steel'], .01, 1))
    for i in range(3): add(box(f'rim{i}', (.5, .12, .5), (3.2 + i * .65, YB - T - .1, 2.0), M['chrome'], .03, 3)); add(rod(f'rimh{i}', .03, .3, (3.2 + i * .65, YB - T - .05, 2.3), M['galv'], 'Y', 8))
    # ---- two floodlight stands by the bay (their heads glow), a creeper board, a trolley jack, a hose reel
    for sx in (-1, 1):
        x, y = sx * 3.6, -1.2
        for a in range(3):
            an = a * 2.094 + .3
            add(bar(f'fleg{sx}{a}', (x + math.cos(an) * .45, y + math.sin(an) * .45, .13), (x, y, .9), .02, .02, M['yel'], 6))
        add(rod(f'fpole{sx}', .025, 1.9, (x, y, 1.8), M['yel'], 'Z', 8)); add(box(f'fhead{sx}', (.4, .2, .3), (x, y, 2.85), M['black'], .02, 2))
        add(box(f'flamp{sx}', (.34, .02, .24), (x, y - .11 * 1, 2.85), M['lamp'], .005, 1))
    add(box('creeper', (.45, 1.0, .06), (1.0, -4.6, .22), M['red'], .02, 2))
    for k in range(4): add(rod(f'crw{k}', .04, .05, (1.0 + (k % 2 - .5) * .36, -4.6 + (k // 2 - .5) * .8, .16), M['black'], 'Z', 8))
    add(box('jack', (.4, 1.0, .18), (-1.6, -4.8, .25), M['red'], .03, 3)); add(bar('jackH', (-1.6, -5.25, .3), (-1.6, -6.0, 1.0), .02, .02, M['steel'], 6))
    add(rod('reel', .35, .2, (RX - .12, -5.4, 2.0), M['red'], 'X', 20))
    details(M, add)
    return P


def door():
    reset(); M = mats(); P = []
    n = 22; sh = DH / n
    for i in range(n):
        z = sh * (i + .5)
        P.append(box(f'slat{i}', (DW, .05, sh - .012), (0, 0, z), M['door'], .006, 2))
        P.append(box(f'rib{i}', (DW - .02, .02, .03), (0, -.03, z), M['door'], .005, 1))
    P.append(box('bottom', (DW, .1, .1), (0, 0, .05), M['steel'], .01, 2))
    for sx in (-1, 1): P.append(box(f'handle{sx}', (.3, .06, .05), (sx * 1.2, -.06, .45), M['black'], .01, 2))
    return P


if want('mshop'):
    P = shop()
    finish_model('mshop', P, 30.0, lift=.35, views=((-28, 18), (35, 50)), floor=False)
if want('mshopdoor'):
    P = door()
    finish_model('mshopdoor', P, 10.0, lift=.4, views=((-20, 10),), floor=False)
