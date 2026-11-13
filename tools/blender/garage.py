"""The large things of Garage Overdrive (the room is laid out in tools/mini/t_garage.py and built in mini.js, toyGarage).
Sizes are fixed by the track and by the code-built stand-ins in tools/mini/models.js (same names, same sizes):
  gbench   the workbench's east arm, 116 x 62 cm, 90 cm high (the track runs along its top)
  gbenchn  its return along the north wall, 101 cm long
  gchest   a roller tool cabinet, 68 x 46 x 95 cm, seven drawers
  gshelf   steel shelving, 150 x 40 x 180 cm, boards at 8, 50, 92, 134 and 176 cm (the game stands the tins and boxes on them)
  gtyres   four car tyres in a stack (the spiral goes round it): 58 cm across, 20 cm wide each
  gdoor    the sectional garage door seen from inside, 318 x 214 cm
  gdooro   the same door OPEN: its four panels run back under the ceiling on their tracks, the opening is clear
Things on the walls (the wall is the plane Y = 0 behind them; the game stands them against a wall at any height):
  gelec    the electrics: a consumer unit at 1.6 m, conduit up to the ceiling, a run to a switch and one to a double socket
  gladder  an aluminium ladder, 2.3 m, hung flat on two hooks
  grack    a wooden rail with pegs: a broom, a spade and a rake hanging from it
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
                black=mat('gblack', hexcol('#0e0f11'), .5), rubber=mat('grubber', hexcol('#1c1c1c'), .9), galv=mat('ggalv', hexcol('#9aa0a6'), .5, metal=1.0), door=mat('gdoor', hexcol('#e9e6de'), .45), board=mat('gboard', hexcol('#c9b48e'), .8), alu=mat('galu', hexcol('#c3c7cc'), .4, metal=.5))


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

# ---------------- on the walls: the electrics
if want('gelec'):
    s = reset(); M = mats(); P = []
    # the consumer unit: a steel box with a lid, a row of breakers behind a window in it
    P.append(box('unit', (.38, .10, .30), (0, -.05, 1.60), M['door'], .008, 3)); P.append(box('lid', (.34, .012, .26), (0, -.104, 1.60), M['door'], .006, 2))
    P.append(box('slot', (.27, .006, .075), (0, -.111, 1.615), M['black'], .002, 1))
    for i in range(12):
        P.append(box(f'brk{i}', (.0175, .016, .062), (-.118 + i * .0215, -.118, 1.615), M['door'] if i else M['red'], .0015, 1)); P.append(box(f'tog{i}', (.009, .012, .016), (-.118 + i * .0215, -.128, 1.622 + (.006 if i % 5 else -.006)), M['black'], .001, 1))
    P.append(box('label', (.20, .002, .03), (0, -.111, 1.515), M['board'], 0))
    # conduit: two up to the ceiling, one across to a switch, one down to a double socket
    R = .0105; y = -.02
    for k, x in enumerate((-.10, -.04)): P.append(tube(f'up{k}', [(x, y, 1.75), (x, y, 2.50)], R, M['alu']))
    P.append(tube('across', [(.19, y, 1.66), (.80, y, 1.66), (.80, y, 1.36)], R, M['alu'], .04))
    P.append(tube('down', [(.10, y, 1.45), (.10, y, 1.06)], R, M['alu']))
    P.append(tube('on', [(.10 + .075, y, 1.00), (.55, y, 1.00), (.55, y, .52)], R, M['alu'], .04))
    for (x, z, hz) in ((-.10, 2.0, 0), (-.04, 2.0, 0), (-.10, 2.38, 0), (-.04, 2.38, 0), (.45, 1.66, 1), (.80, 1.5, 0), (.10, 1.25, 0), (.36, 1.00, 1), (.55, .76, 0)):   # saddle clips
        P.append(box(f'clip{x}{z}', (.012, .026, .05) if hz else (.05, .026, .012), (x, y - .001, z), M['alu'], .002, 1))
    # the switch, the double socket, a single socket at the end of the lower run
    P.append(box('switch', (.086, .04, .086), (.80, -.02, 1.317), M['door'], .006, 2)); P.append(box('rocker', (.022, .008, .04), (.80, -.043, 1.317), M['door'], .002, 1))
    P.append(box('sock', (.15, .042, .088), (.10, -.021, 1.016), M['door'], .006, 2))
    for sx in (-1, 1):
        for (dx, dz) in ((0, .012), (-.011, -.008), (.011, -.008)): P.append(box(f'pin{sx}{dx}', (.006, .004, .009), (.10 + sx * .037 + dx, -.043, 1.012 + dz), M['black'], 0))
        P.append(box(f'srk{sx}', (.012, .008, .016), (.10 + sx * .066, -.044, 1.04), M['door'], .001, 1))
    P.append(box('sock2', (.088, .042, .088), (.55, -.021, .477), M['door'], .006, 2))
    for (dx, dz) in ((0, .012), (-.011, -.008), (.011, -.008)): P.append(box(f'pin2{dx}', (.006, .004, .009), (.55 + dx, -.043, .473 + dz), M['black'], 0))
    finish_model('gelec', P, 4.2, views=((-25, 8),), floor=False)

# ---------------- an aluminium ladder hung flat on two hooks (its length along X)
if want('gladder'):
    s = reset(); M = mats(); P = []; L = 2.30; Z0 = 0.0     # the lower rail's middle is the model's zero height
    for k, z in enumerate((Z0, Z0 + .36)):
        P.append(box(f'rail{k}', (L, .026, .066), (0, -.045, z), M['alu'], .004, 2))
        for sx in (-1, 1): P.append(box(f'cap{k}{sx}', (.03, .032, .072), (sx * (L / 2 + .012), -.045, z), M['black'], .005, 2))
    for i in range(8):
        x = -L / 2 + .16 + i * (L - .32) / 7
        P.append(box(f'rung{i}', (.03, .024, .36), (x, -.045, Z0 + .18), M['alu'], .006, 2))
    for sx in (-1, 1):                                      # the hooks: a plate on the wall, an arm, an upturned end
        x = sx * .72
        P.append(box(f'plate{sx}', (.04, .006, .16), (x, -.003, Z0 + .30), M['steel'], .002, 1))
        P.append(tube(f'hook{sx}', [(x, -.006, Z0 + .35), (x, -.006, Z0 + .312), (x, -.085, Z0 + .312), (x, -.085, Z0 + .36)], .007, M['steel'], .015))
        for dz in (.25, .36): P.append(rod(f'screw{sx}{dz}', .006, .004, (x, -.007, Z0 + dz), M['chrome'], 'Y', 8))
    finish_model('gladder', P, 5.5, views=((-25, 10),), floor=False)

# ---------------- a rail of pegs with garden tools (the rail's middle is 1.75 m up; the tools hang to within 25 cm of the floor)
if want('grack'):
    s = reset(); M = mats(); P = []; ZR = 1.75
    P.append(box('rail', (1.00, .022, .09), (0, -.011, ZR), M['wood'], .004, 2))
    for i, x in enumerate((-.43, -.33, -.05, .05, .31, .41)): P.append(bar(f'peg{i}', (x, -.02, ZR), (x, -.115, ZR + .025), .008, .008, M['steel'], 10))
    for x in (-.46, .46): P.append(rod(f'scr{x}', .007, .004, (x, -.023, ZR), M['chrome'], 'Y', 8))
    # a broom, head up, resting on two pegs
    bx = -.38; P.append(rod('bhandle', .0125, 1.32, (bx, -.065, ZR - .64), M['wood'], 'Z', 12)); P.append(box('bhead', (.30, .05, .05), (bx, -.065, ZR + .045), M['wood'], .008, 2))
    P.append(box('bristle', (.29, .042, .10), (bx, -.065, ZR + .12), M['board'], .006, 1))
    # a spade, hanging by its handle
    sx_ = 0.0; P.append(rod('shandle', .016, .74, (sx_, -.065, ZR - .43), M['wood'], 'Z', 12))
    P.append(tube('sgrip', [(sx_ - .05, -.065, ZR - .075), (sx_ - .05, -.065, ZR + .012), (sx_ + .05, -.065, ZR + .012), (sx_ + .05, -.065, ZR - .075)], .011, M['wood'], .02)); P.append(box('syoke', (.12, .026, .03), (sx_, -.065, ZR - .075), M['wood'], .008, 2))
    P.append(rod('ssocket', .02, .16, (sx_, -.065, ZR - .86), M['steel'], 'Z', 12))
    bl = box('sblade', (.19, .006, .29), (sx_, -.058, ZR - 1.08), M['galv'], 0); P.append(bl)
    for v in bl.data.vertices:                              # a blade narrows to its edge
        if v.co.z < ZR - 1.08: v.co.x = sx_ + (v.co.x - sx_) * .72
    # a rake, head up
    rx = .36; P.append(rod('rhandle', .0125, 1.38, (rx, -.065, ZR - .66), M['wood'], 'Z', 12)); P.append(box('rhead', (.36, .014, .022), (rx, -.065, ZR + .04), M['steel'], .003, 1))
    for i in range(13): P.append(tube(f'tine{i}', [(rx - .168 + i * .028, -.065, ZR + .04), (rx - .168 + i * .028, -.065, ZR + .075), (rx - .168 + i * .028, -.10, ZR + .10)], .003, M['steel'], .012, 6, 3))
    finish_model('grack', P, 4.6, views=((-25, 8),), floor=False)

# ---------------- the garage door, open: the panels lie under the ceiling on the horizontal tracks; -Y is into the garage
if want('gdooro'):
    s = reset(); M = mats(); P = []; W, H = 3.18, 2.14; n = 4; ph = H / n; ZT = H + .13                     # ZT: the height the open door hangs at (the ceiling is at 2.50)
    Y0 = -.30                                                                                               # the first panel's leading edge, back from the wall
    for i in range(n):
        yc = Y0 - ph * (i + .5)
        P.append(box(f'panel{i}', (W, ph - .006, .04), (0, yc, ZT), M['door'], .004, 2))
        for k in range(3): P.append(box(f'rib{i}{k}', (W - .08, .05, .012), (0, yc + (k - 1) * ph * .29, ZT - .024), M['door'], .005, 3))
        for x in (-.42, -.14, .14, .42):
            P.append(box(f'stile{i}{x}', (.05, ph - .02, .02), (x * W, yc, ZT - .03), M['door'], .004, 2))
            if i: P.append(box(f'hinge{i}{x}', (.05, .09, .008), (x * W, Y0 - ph * i, ZT - .044), M['galv'], .002, 1))
    P.append(box('seal', (W, .024, .05), (0, Y0 + .012, ZT), M['rubber'], .004, 2))                          # the bottom seal, now the door's front edge
    for sx in (-1, 1):
        x = sx * (W / 2 + .03)
        # each track: up the side of the opening, round a quarter turn, back under the ceiling
        P.append(tube(f'track{sx}', [(x, -.03, 0), (x, -.03, ZT - .30), (x, -.33, ZT), (x, -(H + .55), ZT)], .028, M['galv'], .30, 8, 6))
        for i in range(n + 1): P.append(rod(f'roller{sx}{i}', .022, .026, (sx * (W / 2 + .012), Y0 - min(H - .03, ph * i + .04), ZT), M['black'], 'X', 14))
        for k, yy in enumerate((-.9, -2.3)):                                                               # hangers up to the ceiling
            hg = box(f'hang{sx}{k}', (.03, .004, 2.50 - ZT - .02), (x, yy, (2.50 + ZT + .02) / 2), M['galv'], 0); P.append(hg)
            P.append(box(f'hangfoot{sx}{k}', (.06, .08, .004), (x, yy, 2.498), M['galv'], 0))
        P.append(box(f'jamb{sx}', (.09, .135, H + .02), (sx * (W / 2 + .045), .06, (H + .02) / 2), M['door'], .004, 1))      # the frame in the wall's thickness (the wall is 12 cm, from Y = 0 outward)
    P.append(box('head', (W + .18, .135, .09), (0, .06, H + .045), M['door'], .004, 1))
    P.append(box('headrail', (W + .14, .07, .05), (0, -.035, H + .30), M['galv'], .003, 1))
    P.append(rod('shaft', .014, W + .10, (0, -.09, H + .26), M['galv'])); P.append(rod('spring', .035, 1.1, (-.5, -.09, H + .26), M['steel'], 'X', 18))
    for sx in (-1, 1): P.append(rod(f'drum{sx}', .06, .05, (sx * (W / 2 + .01), -.09, H + .26), M['galv'], 'X', 20))
    P.append(tube('cord', [(.9, -.34, ZT - .03), (.9, -.36, ZT - .32)], .004, M['red'], 0, 6)); P.append(rod('cordgrip', .012, .05, (.9, -.36, ZT - .345), M['red'], 'Z', 10))   # the pull cord
    finish_model('gdooro', P, 8.5, views=((-150, -8), (-30, 14)), floor=False)
