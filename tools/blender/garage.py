"""The large things of Garage Overdrive (the room is laid out in tools/mini/t_garage.py and built in mini.js, toyGarage).
Sizes are fixed by the track and by the code-built stand-ins in tools/mini/models.js (same names, same sizes):
  gbench   the workbench's east arm, 116 x 62 cm, 90 cm high (the track runs along its top)
  gbenchn  its return along the north wall, 101 cm long
  gchest   a roller tool cabinet, 68 x 46 x 95 cm, seven drawers
  gshelf   steel shelving, 150 x 40 x 180 cm, boards at 8, 50, 92, 134 and 176 cm (the game stands the tins and boxes on them)
  gtyres   four car tyres in a stack (the spiral goes round it): 58 cm across, 20 cm wide each
  gdoor    the sectional garage door seen from inside, 318 x 214 cm
Materials are keys for the game's own (gMats in tools/mini/models.js). Front is -Y.
Run: D:/blender/blender.exe --background --python D:/crust-rush/source/tools/blender/garage.py [-- name ...]
"""
import sys, math, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
import numpy as np
from crlib import *

ONLY = [a for a in sys.argv[sys.argv.index('--') + 1:]] if '--' in sys.argv else []


def want(n): return not ONLY or n in ONLY


def mats():
    return dict(wood=mat('gwood', hexcol('#dcc096'), .5), steel=mat('gsteel', hexcol('#3d4248'), .5), red=mat('gred', hexcol('#b3261c'), .3), chrome=mat('gchrome', hexcol('#c9ccd2'), .25, metal=1.0),
                black=mat('gblack', hexcol('#0e0f11'), .5), rubber=mat('grubber', hexcol('#1c1c1c'), .9), galv=mat('ggalv', hexcol('#9aa0a6'), .5, metal=1.0), door=mat('gdoor', hexcol('#e9e6de'), .45), board=mat('gboard', hexcol('#c9b48e'), .8))


# ---------------- the workbench (two lengths)
def bench(name, L):
    s = reset(); M = mats(); P = []; D, H, T = .62, .90, .05
    P.append(box('top', (L, D, T), (0, 0, H - T / 2), M['wood'], .006, 3))
    n = max(2, round(L / 1.1) + 1); xs = [-L / 2 + .06 + (L - .12) * i / (n - 1) for i in range(n)]
    for i, x in enumerate(xs):
        for k, y in enumerate((-D / 2 + .05, D / 2 - .05)):
            P.append(box(f'leg{i}{k}', (.04, .04, H - T), (x, y, (H - T) / 2), M['steel'], .004, 2)); P.append(box(f'foot{i}{k}', (.06, .06, .008), (x, y, .004), M['black'], .002, 1))
        for z in (H - T - .02, .20): P.append(box(f'tie{i}{z}', (.036, D - .14, .04), (x, 0, z), M['steel'], .003, 1))
    for k, y in enumerate((-D / 2 + .05, D / 2 - .05)):
        P.append(box(f'railT{k}', (L - .16, .03, .04), (0, y, H - T - .02), M['steel'], .003, 1)); P.append(box(f'railB{k}', (L - .16, .03, .036), (0, y, .20), M['steel'], .003, 1))
    P.append(box('shelf', (L - .10, D - .08, .02), (0, 0, .23), M['wood'], .003, 2))
    # a drawer under the top at the front, with a pull
    P.append(box('drawer', (.42, .03, .11), (-L / 2 + .36, -D / 2 + .035, H - T - .075), M['wood'], .004, 2)); P.append(rod('pull', .007, .16, (-L / 2 + .36, -D / 2 + .005, H - T - .075), M['chrome']))
    for k in (-1, 1): P.append(rod(f'pulls{k}', .005, .03, (-L / 2 + .36 + k * .06, -D / 2 + .018, H - T - .075), M['chrome'], 'Y', 8))
    for i, x in enumerate(xs):                           # the bolts that hold the top down
        for y in (-D / 2 + .05, D / 2 - .05): P.append(rod(f'bolt{i}{y}', .008, .004, (x, y, H + .001), M['steel'], 'Z', 10))
    finish_model(name, P, 3.4 if L > 1.1 else 3.0, views=((-30, 20),))


if want('gbench'): bench('gbench', 1.16)
if want('gbenchn'): bench('gbenchn', 1.01)

# ---------------- the roller cabinet
if want('gchest'):
    s = reset(); M = mats(); P = []; W, D, H0, H = .68, .46, .12, .95
    P.append(box('body', (W, D, H - H0), (0, 0, H0 + (H - H0) / 2), M['red'], .012, 4)); P.append(box('mat', (W - .03, D - .03, .008), (0, 0, H + .003), M['rubber'], .003, 2))
    for k in (-1, 1): P.append(box(f'lip{k}', (W - .02, .012, .02), (0, k * (D / 2 - .008), H + .008), M['red'], .003, 1)); P.append(box(f'lipS{k}', (.012, D - .02, .02), (k * (W / 2 - .008), 0, H + .008), M['red'], .003, 1))
    z = H - .04
    for i, h in enumerate((.07, .07, .07, .09, .09, .14, .22)):
        P.append(box(f'dr{i}', (W - .05, .022, h - .012), (0, -D / 2 - .004, z - h / 2), M['red'], .005, 3)); P.append(box(f'pull{i}', (W - .07, .016, .016), (0, -D / 2 - .02, z - .022), M['chrome'], .005, 3)); z -= h
    P.append(rod('lock', .012, .006, (W / 2 - .06, -D / 2 - .016, H - .02), M['chrome'], 'Y', 14))
    for sx in (-1, 1):
        for sy in (-1, 1):
            x, y = sx * (W / 2 - .06), sy * (D / 2 - .06)
            P.append(box(f'plate{sx}{sy}', (.07, .07, .006), (x, y, H0 - .003), M['steel'], .002, 1)); P.append(box(f'fork{sx}{sy}', (.012, .05, .07), (x - .022, y, H0 - .04), M['steel'], .002, 1)); P.append(box(f'forkb{sx}{sy}', (.012, .05, .07), (x + .022, y, H0 - .04), M['steel'], .002, 1))
            P.append(rod(f'wheel{sx}{sy}', .05, .03, (x, y, .05), M['rubber'], 'X', 24)); P.append(rod(f'hub{sx}{sy}', .018, .034, (x, y, .05), M['chrome'], 'X', 12))
    P.append(rod('handle', .012, D - .08, (W / 2 + .045, 0, H - .10), M['chrome'], 'Y'))
    for k in (-1, 1): P.append(box(f'hmount{k}', (.05, .02, .02), (W / 2 + .022, k * (D / 2 - .06), H - .10), M['chrome'], .004, 2))
    finish_model('gchest', P, 3.2, views=((-32, 18), (150, 20)))

# ---------------- the shelving (the frame and boards only)
if want('gshelf'):
    s = reset(); M = mats(); P = []; W, D, H = 1.50, .40, 1.80
    for sx in (-1, 1):
        for sy in (-1, 1):
            P.append(box(f'postA{sx}{sy}', (.034, .004, H), (sx * (W / 2 - .017), sy * (D / 2 - .002), H / 2), M['galv'], 0)); P.append(box(f'postB{sx}{sy}', (.004, .034, H), (sx * (W / 2 - .002), sy * (D / 2 - .017), H / 2), M['galv'], 0))
            P.append(box(f'foot{sx}{sy}', (.04, .04, .006), (sx * (W / 2 - .018), sy * (D / 2 - .018), .003), M['black'], .001, 1))
    for i, z in enumerate((.08, .50, .92, 1.34, 1.76)):
        P.append(box(f'board{i}', (W - .015, D - .015, .018), (0, 0, z), M['board'], .002, 1))
        for sy in (-1, 1): P.append(box(f'beam{i}{sy}', (W - .01, .004, .034), (0, sy * (D / 2 - .002), z - .012), M['galv'], 0)); P.append(box(f'beamlip{i}{sy}', (W - .01, .014, .004), (0, sy * (D / 2 - .008), z - .027), M['galv'], 0))
        for sx in (-1, 1): P.append(box(f'side{i}{sx}', (.004, D - .01, .034), (sx * (W / 2 - .002), 0, z - .012), M['galv'], 0))
    for sx in (-1, 1):                                    # a cross brace at each end
        for k, (z0, z1) in enumerate(((.10, .48), (.48, .10))):
            P.append(bar(f'brace{sx}{k}', (sx * (W / 2 - .008), -D / 2 + .02, z0), (sx * (W / 2 - .008), D / 2 - .02, z1), .005, .005, M['galv'], 8))
    finish_model('gshelf', P, 5.0, views=((-28, 16),))

# ---------------- the stack of tyres
if want('gtyres'):
    s = reset(); M = mats(); P = []; rs = np.random.RandomState(11)
    R, w = .29, .20
    for i in range(4):
        z = .10 + i * .203; ox, oy, rot = (rs.rand() - .5) * .04, (rs.rand() - .5) * .04, rs.rand() * 6.28
        # the carcass: a ring with a flat tread band, rounded shoulders and sidewalls down to the bead
        prof = [(.180, -.085), (.195, -.096), (.240, -.100), (.268, -.094), (.284, -.074), (.288, -.05), (.288, .05), (.284, .074), (.268, .094), (.240, .100), (.195, .096), (.180, .085), (.172, .04), (.172, -.04)]
        seg = 56; V = []; F = []
        for j in range(seg):
            a = j / seg * 2 * math.pi
            for (r, h) in prof: V.append((r * math.cos(a), r * math.sin(a), h))
        n = len(prof)
        for j in range(seg):
            for k in range(n): F.append((j * n + k, ((j + 1) % seg) * n + k, ((j + 1) % seg) * n + (k + 1) % n, j * n + (k + 1) % n))
        me = bpy.data.meshes.new(f'tyre{i}'); me.from_pydata(V, [], F); me.update(); o = bpy.data.objects.new(f'tyre{i}', me); bpy.context.scene.collection.objects.link(o)
        o.location = (ox, oy, z); o.rotation_euler = (0, 0, rot); o.data.materials.append(M['rubber']); active(o); bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.normals_make_consistent(inside=False); bpy.ops.object.mode_set(mode='OBJECT'); smooth(o); P.append(o)
        # the tread: blocks in three rows round the band, and a raised ring on each sidewall
        nb = 40
        for row, (hz, bw) in enumerate(((-.052, .034), (0, .04), (.052, .034))):
            for j in range(nb):
                a = (j + (.5 if row == 1 else 0)) / nb * 2 * math.pi + rot
                b = box(f'blk{i}{row}{j}', (.012, 2 * math.pi * R / nb * .72, bw), (ox + (R - .001) * math.cos(a), oy + (R - .001) * math.sin(a), z + hz), M['rubber'], 0); b.rotation_euler = (0, 0, a); P.append(b)   # plain blocks: bevelled ones made the pack 736 KB
        for sgn in (-1, 1):
            bpy.ops.mesh.primitive_torus_add(major_radius=.232, minor_radius=.006, major_segments=48, minor_segments=6, location=(ox, oy, z + sgn * .1)); t = bpy.context.object; t.name = f'ring{i}{sgn}'; t.data.materials.append(M['rubber']); smooth(t); P.append(t)
    finish_model('gtyres', P, 3.0, lift=.5, views=((-30, 22),))

# ---------------- the garage door
if want('gdoor'):
    s = reset(); M = mats(); P = []; W, H = 3.18, 2.14; n = 4; ph = H / n
    for i in range(n):
        zc = ph * (i + .5)
        P.append(box(f'panel{i}', (W, .04, ph - .006), (0, 0, zc), M['door'], .004, 2))
        for k in range(3): P.append(box(f'rib{i}{k}', (W - .08, .012, .05), (0, -.024, zc + (k - 1) * ph * .29), M['door'], .005, 3))
        for x in (-.42, -.14, .14, .42):
            P.append(box(f'stile{i}{x}', (.05, .02, ph - .02), (x * W, -.03, zc), M['door'], .004, 2))
            if i: P.append(box(f'hinge{i}{x}', (.05, .008, .09), (x * W, -.044, ph * i), M['galv'], .002, 1)); P.append(rod(f'pin{i}{x}', .007, .06, (x * W, -.05, ph * i), M['galv'], 'X', 10))
    for sx in (-1, 1):
        P.append(box(f'track{sx}', (.05, .06, H + .08), (sx * (W / 2 + .03), -.03, (H + .08) / 2), M['galv'], .003, 1))
        for i in range(n + 1): P.append(rod(f'roller{sx}{i}', .022, .026, (sx * (W / 2 + .012), -.05, min(H - .03, ph * i + .04)), M['black'], 'X', 14))
    P.append(box('head', (W + .14, .07, .05), (0, -.035, H + .06), M['galv'], .003, 1)); P.append(box('seal', (W, .05, .024), (0, 0, .012), M['rubber'], .004, 2))
    P.append(box('grip', (.16, .04, .024), (0, -.06, ph * .55), M['black'], .008, 3))
    for k in (-1, 1): P.append(box(f'gripm{k}', (.016, .04, .024), (k * .07, -.044, ph * .55), M['black'], .003, 1))
    # the spring shaft over the door with its two drums
    P.append(rod('shaft', .014, W + .10, (0, -.09, H + .16), M['galv'])); P.append(rod('spring', .035, 1.1, (-.5, -.09, H + .16), M['steel'], 'X', 18))
    for sx in (-1, 1): P.append(rod(f'drum{sx}', .06, .05, (sx * (W / 2 + .01), -.09, H + .16), M['galv'], 'X', 20))
    finish_model('gdoor', P, 8.5, views=((-20, 12),))
