"""The furniture of Kitchen Chaos (the room is laid out in tools/mini/t_kitchen.py and built in mini.js, toyKitchen).
Sizes are fixed by the track: the worktop is 90 cm high (the start straight runs along it), the table 75 cm (the track crosses it).
  kcounter  the base units along the north wall, 3.155 m: drawers, doors, a built-in oven under a glass hob, a sink with a tap
  kwallcab  a wall cabinet, 1.2 m wide, two doors
  kfridge   a tall fridge-freezer, 72 cm wide, 1.8 m high
  ktable    the kitchen table, 160 x 80 cm
  kchair    a wooden chair
  kstool    a bar stool (the spiral goes round it)
  kshelf    an open shelf unit with storage jars
Materials are keys for the game's own (see M.k* in tools/mini/models.js). Front is -Y.
Run: D:/blender/blender.exe --background --python D:/crust-rush/source/tools/blender/kitchen.py [name ...]
"""
import sys, math, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from crlib import *

ONLY = [a for a in sys.argv[sys.argv.index('--') + 1:]] if '--' in sys.argv else []


def want(n): return not ONLY or n in ONLY


def mats():
    return dict(cab=mat('kcab', hexcol('#7d9a8a'), .5), kick=mat('kkick', hexcol('#26282a'), .6), top=mat('ash', hexcol('#dcc096'), .45),
                steel=mat('ksteel', hexcol('#c9ccd2'), .3, metal=1.0), glass=mat('kblack', hexcol('#0c0d0f'), .15), ring=mat('kring', hexcol('#5a5d62'), .4),
                fridge=mat('kfridge', hexcol('#c8cbd0'), .35, metal=.7), wood=mat('ash', hexcol('#dcc096'), .45),
                jar=[mat('kjarA', hexcol('#f1ece0'), .3), mat('kjarB', hexcol('#c9573b'), .35), mat('kjarC', hexcol('#3f6f8f'), .35)], lid=mat('klid', hexcol('#b98a58'), .5))


# ---------------- the worktop run
if want('kcounter'):
    s = reset(); M = mats(); P = []
    W, D, H = 3.155, .62, .90; X0 = -W / 2
    BX0, BX1, BY0, BY1 = 1.22, 1.52, -.20, .14           # the sink's opening in the top
    P.append(box('kick', (W, .50, .10), (0, .04, .05), M['kick'], 0))
    P.append(box('carcass', (BX0 - X0, .58, .76), ((X0 + BX0) / 2, .02, .48), M['cab'], .002, 1))
    P.append(box('carcassR', (W / 2 - BX1, .58, .76), ((BX1 + W / 2) / 2, .02, .48), M['cab'], .002, 1))
    P.append(box('carcassB', (BX1 - BX0, .14, .76), ((BX0 + BX1) / 2, .24, .48), M['cab'], 0))
    # the top, in four pieces round the sink
    for nm, x0, x1, y0, y1 in (('topL', X0, BX0, -.32, .31), ('topR', BX1, W / 2, -.32, .31), ('topF', BX0, BX1, -.32, BY0), ('topB', BX0, BX1, BY1, .31)):
        P.append(box(nm, (x1 - x0, y1 - y0, .04), ((x0 + x1) / 2, (y0 + y1) / 2, H - .02), M['top'], .004 if nm in ('topL', 'topR') else 0, 2))
    # the basin: a steel tub seen from inside, with a rolled rim
    bpy.ops.mesh.primitive_cube_add(size=1, location=((BX0 + BX1) / 2, (BY0 + BY1) / 2, H - .08)); tub = bpy.context.object; tub.name = 'tub'
    tub.scale = (BX1 - BX0, BY1 - BY0, .16); apply_scale(tub); tub.data.flip_normals(); tub.data.materials.append(M['steel']); P.append(tub)
    for nm, sz, lc in (('rimF', (BX1 - BX0 + .02, .012, .006), ((BX0 + BX1) / 2, BY0, H + .002)), ('rimB', (BX1 - BX0 + .02, .012, .006), ((BX0 + BX1) / 2, BY1, H + .002)),
                       ('rimL', (.012, BY1 - BY0, .006), (BX0, (BY0 + BY1) / 2, H + .002)), ('rimR', (.012, BY1 - BY0, .006), (BX1, (BY0 + BY1) / 2, H + .002))):
        P.append(box(nm, sz, lc, M['steel'], .002, 1))
    # the tap
    tx, ty = (BX0 + BX1) / 2, .225
    P.append(rod('tapbase', .024, .03, (tx, ty, H + .015), M['steel'], 'Z', 20)); P.append(rod('tapriser', .012, .24, (tx, ty, H + .15), M['steel'], 'Z'))
    for i in range(6):                                   # the swan neck: a quarter turn forward
        a0, a1 = i / 6 * math.pi / 2, (i + 1) / 6 * math.pi / 2; R = .07
        P.append(bar(f'neck{i}', (tx, ty - R + R * math.cos(a0), H + .27 + R * math.sin(a0)), (tx, ty - R + R * math.cos(a1), H + .27 + R * math.sin(a1)), .012, .012, M['steel']))
    P.append(rod('spout', .011, .11, (tx, ty - R - .055, H + .34), M['steel'], 'Y')); P.append(rod('lever', .007, .07, (tx + .04, ty, H + .05), M['steel'], 'X', 10))
    # the fronts, unit by unit from the left: drawers, a door, the oven, a door, the sink's two doors
    z0, z1 = .105, .855; fy = -.282
    def front(nm, x0, x1, za, zb, m=None): P.append(box(nm, (x1 - x0 - .006, .02, zb - za - .006), ((x0 + x1) / 2, fy, (za + zb) / 2), m or M['cab'], .004, 2))
    def hbar(nm, x, z, L=.16): P.append(rod(nm, .006, L, (x, fy - .034, z), M['steel'])); [P.append(rod(f'{nm}s{k}', .005, .024, (x + k * (L / 2 - .02), fy - .022, z), M['steel'], 'Y', 8)) for k in (-1, 1)]
    def vbar(nm, x, z, L=.16): P.append(rod(nm, .006, L, (x, fy - .034, z), M['steel'], 'Z')); [P.append(rod(f'{nm}s{k}', .005, .024, (x, fy - .022, z + k * (L / 2 - .02)), M['steel'], 'Y', 8)) for k in (-1, 1)]
    u = X0
    for i, (za, zb) in enumerate(((z0, .355), (.355, .605), (.605, z1))): front(f'drawer{i}', u, u + .6, za, zb); hbar(f'dh{i}', u + .3, zb - .07)
    u += .6; front('door1', u, u + .6, z0, z1); vbar('d1h', u + .6 - .06, z1 - .14)
    u += .6; ox = u + .3                                  # the oven
    front('ovenstrip', u, u + .6, .745, z1, M['steel']); front('oven', u, u + .6, .165, .745, M['glass']); front('ovenplinth', u, u + .6, z0, .165, M['steel'])
    P.append(rod('ovenbar', .009, .46, (ox, fy - .045, .70), M['steel'])); [P.append(rod(f'ovens{k}', .006, .035, (ox + k * .2, fy - .028, .70), M['steel'], 'Y', 8)) for k in (-1, 1)]
    for k in range(4): P.append(rod(f'knob{k}', .014, .016, (ox - .18 + k * .12, fy - .018, .80), M['kick'], 'Y', 14))
    u += .6; front('door2', u, u + .6, z0, z1); vbar('d2h', u + .06, z1 - .14)
    u += .6; mid = (u + W / 2) / 2
    front('sinkL', u, mid, z0, z1); front('sinkR', mid, W / 2, z0, z1); vbar('sLh', mid - .05, z1 - .14); vbar('sRh', mid + .05, z1 - .14)
    # the hob: black glass set into the top, four rings
    P.append(box('hob', (.56, .50, .003), (ox, 0, H + .0015), M['glass'], 0))
    for k, (hx, hy, hr) in enumerate(((-.14, .12, .085), (.14, .12, .07), (-.14, -.12, .07), (.14, -.12, .085))):
        bpy.ops.mesh.primitive_torus_add(major_radius=hr, minor_radius=.0025, major_segments=32, minor_segments=4, location=(ox + hx, hy, H + .003)); r = bpy.context.object; r.name = f'ring{k}'; r.scale.z = .3
        r.data.materials.append(M['ring']); P.append(r)
    finish_model('kcounter', P, 5.2, views=((-25, 22), (25, 40)))

# ---------------- a wall cabinet
if want('kwallcab'):
    s = reset(); M = mats(); P = []
    W, D, H = 1.20, .33, .70
    P.append(box('carcass', (W, D - .02, H), (0, .01, H / 2), M['cab'], .002, 1))
    for k in (-1, 1):
        P.append(box(f'door{k}', (W / 2 - .006, .02, H - .006), (k * W / 4, -D / 2 + .01, H / 2), M['cab'], .004, 2))
        P.append(rod(f'h{k}', .006, .14, (k * .05, -D / 2 - .024, .12), M['steel'], 'Z'))
        for q in (-1, 1): P.append(rod(f'h{k}s{q}', .005, .024, (k * .05, -D / 2 - .012, .12 + q * .05), M['steel'], 'Y', 8))
    finish_model('kwallcab', P, 2.6, floor=False)

# ---------------- the fridge
if want('kfridge'):
    s = reset(); M = mats(); P = []
    W, D, H = .72, .68, 1.80
    P.append(box('body', (W, D - .04, H), (0, .02, H / 2), M['fridge'], .008, 3))
    # the freezer's small door on top, the fridge's big door below
    P.append(box('doorTop', (W - .006, .04, .54), (0, -D / 2 + .02, 1.24 + .27), M['fridge'], .012, 4))
    P.append(box('doorBot', (W - .006, .04, 1.18), (0, -D / 2 + .02, .04 + .59), M['fridge'], .012, 4))
    P.append(box('plinth', (W - .04, .5, .04), (0, .03, .02), M['kick'], 0))
    for nm, z, L in (('hTop', 1.40, .22), ('hBot', .92, .5)):
        P.append(rod(nm, .009, L, (-W / 2 + .07, -D / 2 - .045, z), M['steel'], 'Z'))
        for q in (-1, 1): P.append(rod(f'{nm}s{q}', .006, .045, (-W / 2 + .07, -D / 2 - .022, z + q * (L / 2 - .03)), M['steel'], 'Y', 8))
    finish_model('kfridge', P, 4.6)

# ---------------- the kitchen table
if want('ktable'):
    s = reset(); M = mats(); P = []
    W, D, H = 1.60, .80, .75
    P.append(box('top', (W, D, .03), (0, 0, H - .015), M['wood'], .008, 4))
    for sx in (-1, 1):
        P.append(box(f'apronE{sx}', (.022, D - .2, .08), (sx * (W / 2 - .09), 0, H - .07), M['wood'], .003, 1))
        for sy in (-1, 1): P.append(frustum(f'leg{sx}{sy}', .032, .022, H - .03, (sx * (W / 2 - .09), sy * (D / 2 - .09), 0), M['wood'], 16))
    for sy in (-1, 1): P.append(box(f'apronS{sy}', (W - .2, .022, .08), (0, sy * (D / 2 - .09), H - .07), M['wood'], .003, 1))
    finish_model('ktable', P, 4.0)

# ---------------- a chair
if want('kchair'):
    s = reset(); M = mats(); P = []
    P.append(box('seat', (.42, .40, .03), (0, 0, .445), M['wood'], .01, 3))
    for sx in (-1, 1):
        P.append(frustum(f'legF{sx}', .019, .014, .43, (sx * .18, -.165, 0), M['wood'], 12))
        P.append(bar(f'legB{sx}', (sx * .18, .19, 0), (sx * .18, .165, .43), .014, .019, M['wood']))
        P.append(bar(f'post{sx}', (sx * .18, .165, .43), (sx * .175, .215, .90), .019, .015, M['wood']))
        P.append(rod(f'side{sx}', .009, .34, (sx * .18, .01, .2), M['wood'], 'Y', 10))
    P.append(box('rail', (.38, .022, .075), (0, .212, .84), M['wood'], .008, 3)); P.append(box('rail2', (.35, .018, .045), (0, .19, .64), M['wood'], .006, 2))
    for k in (-1, 0, 1): P.append(box(f'slat{k}', (.05, .012, .17), (k * .1, .2, .745), M['wood'], .004, 1))
    P.append(rod('front', .009, .36, (0, -.165, .2), M['wood'], 'X', 10))
    finish_model('kchair', P, 2.6, views=((-35, 20),))

# ---------------- the bar stool
if want('kstool'):
    s = reset(); M = mats(); P = []
    st = rod('seat', .17, .04, (0, 0, .74), M['wood'], 'Z', 40); bevel(st, .012, 4, 40); P.append(st)
    for sx in (-1, 1):
        for sy in (-1, 1): P.append(bar(f'leg{sx}{sy}', (sx * .19, sy * .19, 0), (sx * .11, sy * .11, .725), .012, .016, M['steel']))
    bpy.ops.mesh.primitive_torus_add(major_radius=.228, minor_radius=.008, major_segments=40, minor_segments=8, location=(0, 0, .25)); r = bpy.context.object; r.name = 'ring'; r.data.materials.append(M['steel']); P.append(r)
    finish_model('kstool', P, 2.6)

# ---------------- the shelf unit with jars
if want('kshelf'):
    s = reset(); M = mats(); P = []
    W, D, H = .90, .30, 1.80
    for sx in (-1, 1): P.append(box(f'side{sx}', (.022, D, H), (sx * (W / 2 - .011), 0, H / 2), M['wood'], .003, 1))
    P.append(box('back', (W - .04, .008, H - .1), (0, D / 2 - .006, H / 2), M['wood'], 0))
    levels = (.08, .48, .88, 1.28, 1.78)
    for i, z in enumerate(levels): P.append(box(f'shelf{i}', (W - .044, D - .01, .022), (0, 0, z), M['wood'], .003, 1))
    r = np.random.RandomState(5)
    for li, z in enumerate(levels[:4]):
        x = -W / 2 + .1
        while x < W / 2 - .09:
            rr = .042 + r.rand() * .02; hh = .11 + r.rand() * .12; m = M['jar'][r.randint(3)]; y = (r.rand() - .5) * .06
            j = rod(f'jar{li}_{x:.2f}', rr, hh, (x, y, z + .011 + hh / 2), m, 'Z', 24); bevel(j, .006, 2, 40); P.append(j)
            l = rod(f'lid{li}_{x:.2f}', rr * .82, .022, (x, y, z + .011 + hh + .011), M['lid'], 'Z', 20); bevel(l, .004, 2, 40); P.append(l)
            x += rr * 2 + .035 + r.rand() * .05
    finish_model('kshelf', P, 4.4)
