"""The back garden, modelled: everything that stands in it, each thing built by one function here.

ONE source for two uses:
  yard.py     builds each model on its own, bakes its shade, renders a check picture and exports the GLB that the Backyard
              Mega Circuit shows (pack_glb.py -> toy_<name>_hq; placed by toyYard in tools/mini/mini.js)
  outside.py  stands the same models in one scene, the whole garden, and renders it from each room's window

Every function builds its model at the origin of the CURRENT scene, in the garden's own directions (X east, Y north,
Z up: the house is to the south, so a model's south side, -Y, is the one seen from the patio) and returns its parts.
Nothing here is rotated by angles typed in by hand: sloping and lapped parts are outlines pushed straight through
(crlib.prism), round bars run from point to point (crlib.tube / bar), and a part is turned only by whole quarter turns
(crlib.turn). Joints overlap; `joined` checks the ones that matter.
Sizes in metres. Materials are keys for the game's own (yMats in tools/mini/models.js); the colours here are for the
check pictures and the window views.
"""
import bpy, bmesh, math
import numpy as np
from mathutils import Vector, Matrix
from crlib import *


def ymats():
    return dict(
        fence=mat('yfence', hexcol('#9a7650'), .85), shed=mat('yshed', hexcol('#7d6146'), .85), sdoor=mat('ysheddoor', hexcol('#5c4630'), .8),
        felt=mat('yfelt', hexcol('#3a3d42'), .92), iron=mat('yiron', hexcol('#2a2c31'), .5, metal=.6), pane=mat('ypane', (.03, .05, .08), .08),
        white=mat('ywhite', hexcol('#f1f0ea'), .4), net=mat('ynet', hexcol('#f4f4f0'), .8), steel=mat('ysteel', hexcol('#b9bcc2'), .45, metal=.8),
        peg=mat('ypeg', hexcol('#c9a56a'), .7), c0=mat('ycloth0', hexcol('#d9534f'), .9), c1=mat('ycloth1', hexcol('#f4f1ea'), .9),
        c2=mat('ycloth2', hexcol('#4f86c6'), .9), c3=mat('ycloth3', hexcol('#f0c040'), .9),
        bark=mat('ybark', hexcol('#5a4636'), .95), leaf=mat('yleaf', hexcol('#4f8f38'), .8),
        brick=mat('ybrick', hexcol('#9a5a44'), .9), slate=mat('yslate', hexcol('#5d6470'), .7), trim=mat('ytrim', hexcol('#f1efe8'), .5),
        gutter=mat('ygutter', hexcol('#26282c'), .5), terra=mat('yterra', hexcol('#b8663e'), .8), soil=mat('ysoil', hexcol('#3a2a1e'), 1.0),
        petal=mat('ypetal', hexcol('#d8344a'), .6), petal2=mat('ypetal2', hexcol('#f2d44a'), .6), can=mat('ycan', hexcol('#3f7a4a'), .35),
        hose=mat('yhose', hexcol('#3f8a3a'), .5), brass=mat('ybrass', hexcol('#b08a4a'), .3, metal=.9), conc=mat('yconc', hexcol('#a9a7a0'), .9),
        siding=mat('ysiding', hexcol('#e6dcc8'), .8), stone=mat('ystone', hexcol('#b9b3a6'), .8),
        ghat=mat('gnhat', hexcol('#c0261c'), .5), gskin=mat('gnskin', hexcol('#e8b89a'), .6), gbeard=mat('gnbeard', hexcol('#f1efe8'), .8),
        gcoat=mat('gncoat', hexcol('#2f5d9a'), .6), gboot=mat('gnboot', hexcol('#3a2618'), .6), gbelt=mat('gnbelt', hexcol('#141414'), .5),
        ball=mat('yball', hexcol('#f4f4f0'), .45), ballb=mat('yballb', hexcol('#1b1c20'), .45), grass=mat('ygrass', hexcol('#4c8a30'), .9))


def _pyramid(name, w, h, loc, m):
    """a four-sided cap: its base w square, centred on loc"""
    bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=w * .7071, radius2=0, depth=h, location=(loc[0], loc[1], loc[2] + h / 2), rotation=(0, 0, math.pi / 4))
    o = bpy.context.object; o.name = name; apply_scale(o); o.data.materials.append(m); return o


# ---------------------------------------------------------------- the fence
def fence(seed=1, L=2.125):
    """one bay of close-board fence, L long along X, standing on the line Y = 0: seventeen upright boards on a gravel board,
    two rails and a post on the garden (south) side. The post stands at the bay's west end, so bays set end to end make a
    fence with a post at every joint. No two boards are the same height, lean or colour."""
    M = ymats(); r = np.random.RandomState(seed); P = []
    n = 17; pitch = L / n
    gb = box('gravel', (L, .022, .15), (0, .011, .075), M['fence'], .003, 1); uv_plank(gb, 0, 2, r.randint(6), r.rand()); gb['tint'] = (.74, .72, .69); P.append(gb)
    for i in range(n):
        h = 1.62 + r.rand() * .06; x = -L / 2 + pitch * (i + .5)
        b = box(f'board{i}', (pitch - .006, .018, h), (x, .0085 + r.rand() * .003, .148 + h / 2), M['fence'], .003, 1)
        lean = (r.rand() - .5) * .010
        for v in b.data.vertices: v.co.x += v.co.z * lean
        k = .74 + r.rand() * .26; b['tint'] = (k, k * (.96 + r.rand() * .04), k * (.92 + r.rand() * .08))
        uv_plank(b, 2, 0, r.randint(6), r.rand()); P.append(b)
    rails = []
    for z in (.45, 1.45):
        rl = box(f'rail{z}', (L, .044, .075), (0, -.020, z), M['fence'], .004, 1); uv_plank(rl, 0, 2, r.randint(6), r.rand()); rl['tint'] = (.86, .84, .8); P.append(rl); rails.append(rl)
    post = box('post', (.09, .09, 1.88), (-L / 2, -.045, .94), M['fence'], .005, 1); uv_plank(post, 2, 0, r.randint(6), r.rand()); post['tint'] = (.8, .78, .74); P.append(post)
    cap = _pyramid('postcap', .11, .035, (-L / 2, -.045, 1.875), M['fence']); uv_plank(cap, 2, 0, 0, .3); cap['tint'] = (.7, .68, .64); P.append(cap)
    for rl in rails: joined(rl, post); joined(rl, P[1])
    joined(cap, post)
    return P


# ---------------------------------------------------------------- the shed
def _lap_boards(name, length, z0, z1, m, r, top=None):
    """feather-edged boards lapped one over the next, along X from -length/2, facing -Y with the wall at y = 0, from z0 up
    to z1 (the last one is cut down to fit). `top(z)` gives the half-length at height z for a gable: there each board's
    ends are cut to the slope, so nothing pokes through the roof."""
    out = []; i = 0; z = z0
    while z < z1 - .03:
        zt = min(z + .137, z1); f = (zt - z) / .137
        hb = length / 2 if top is None else min(length / 2, top(z)); ht = length / 2 if top is None else min(length / 2, top(zt))
        if ht < .05: break
        V = []
        for sx in (-1, 1): V += [(sx * hb, 0, z), (sx * hb, -.021, z), (sx * ht, -.021 + .013 * f, zt), (sx * ht, 0, zt)]
        me = bpy.data.meshes.new(f'{name}{i}'); me.from_pydata(V, [], [(0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)]); me.update()
        b = bpy.data.objects.new(f'{name}{i}', me); bpy.context.scene.collection.objects.link(b); me.materials.append(m)
        bm = bmesh.new(); bm.from_mesh(me); bmesh.ops.recalc_face_normals(bm, faces=bm.faces); bm.to_mesh(me); bm.free()
        k = .72 + r.rand() * .28; b['tint'] = (k, k * (.96 + r.rand() * .04), k * (.92 + r.rand() * .08)); b['band'] = int(r.randint(6)); b['shift'] = float(r.rand())
        out.append(b); z += .125; i += 1
    return out


def shed():
    """a garden shed, 2.4 x 1.9 m, 2 m to the eaves and 2.42 m to the ridge (which runs east-west): lapped boards, a felt
    roof with barge boards, a ledged and braced door with strap hinges and a bolt, a window. The door is in the south side."""
    M = ymats(); r = np.random.RandomState(4); P = []; W, D, E, R = 2.4, 1.9, 2.0, 2.42
    P.append(box('core', (W - .02, D - .02, E), (0, 0, E / 2), M['iron'], 0))                                 # what shows through any chink: dark
    P.append(prism('coregable', [(-D / 2 + .01, E - .01), (D / 2 - .01, E - .01), (0, R - .03)], 'X', -W / 2 + .01, W / 2 - .01, M['iron']))
    P.append(box('plinth', (W + .03, D + .03, .035), (0, 0, .0175), M['iron'], .004, 1))
    ye, ze, t = D / 2 + .10, E - .045, .03; ox = W / 2 + .08                                            # the roof: its eaves' edge, its thickness, its overhang past the gables
    gable = lambda z: ye * (1 - (z + .012 - ze) / (R - ze))                                             # half the width under the roof at height z
    for nm, ln, deg, at, tp in (('s', W, 0, (0, -D / 2, 0), None), ('n', W, 180, (0, D / 2, 0), None), ('e', D, 90, (W / 2, 0, 0), gable), ('w', D, -90, (-W / 2, 0, 0), gable)):
        for b in _lap_boards(nm, ln, .03, E - .008 if tp is None else R - .03, M['shed'], r, tp):
            turn(b, deg, at); uv_plank(b, 0 if tp is None else 1, 2, b['band'], b['shift']); P.append(b)
    for sx in (-1, 1):
        for sy in (-1, 1):
            c = box(f'corner{sx}{sy}', (.055, .055, E + .02), (sx * (W / 2 + .008), sy * (D / 2 + .008), (E + .02) / 2), M['shed'], .004, 1); uv_plank(c, 2, 0, r.randint(6), r.rand()); c['tint'] = (.66, .64, .6); P.append(c)
    # the roof: two felted slopes meeting at the ridge, a capping strip, barge boards and a finial on each gable
    for sy in (-1, 1):
        P.append(prism(f'roof{sy}', [(sy * ye, ze), (0, R), (0, R + t), (sy * ye, ze + t)], 'X', -ox, ox, M['felt']))
        P.append(box(f'fascia{sy}', (2 * ox, .02, .085), (0, sy * (ye - .012), ze - .02), M['shed'], .003, 1)); P[-1]['tint'] = (.66, .64, .6); uv_plank(P[-1], 0, 2, 2, .2)
        for k, f in enumerate((.34, .67)):                                                                    # felt goes on in three widths, each lapped over the one below
            y0 = sy * ye * (1 - f); z0 = ze + (R - ze) * f; a = t + .007 * k; b_ = t + .007 * (k + 1)
            P.append(prism(f'lap{sy}{k}', [(y0, z0 + a), (0, R + a), (0, R + b_), (y0, z0 + b_)], 'X', -ox, ox, M['felt']))
        for sx in (-1, 1):
            bb = prism(f'barge{sy}{sx}', [(sy * (ye + .01), ze - .10), (0, R - .10), (0, R + t + .022), (sy * (ye + .01), ze + t + .022)], 'X', sx * ox - .011, sx * ox + .011, M['shed'])
            bb['tint'] = (.66, .64, .6); uv_plank(bb, 1, 2, 4, .1 * sx); P.append(bb)
    P.append(prism('ridge', [(-.08, R + t - .018), (0, R + t + .018), (.08, R + t - .018), (.08, R + t - .008), (0, R + t + .030), (-.08, R + t - .008)], 'X', -ox, ox, M['felt']))
    for sx in (-1, 1):
        f = prism(f'finial{sx}', [(-.045, R - .09), (0, R - .16), (.045, R - .09), (.03, R + .10), (0, R + .16), (-.03, R + .10)], 'X', sx * ox + .010, sx * ox + .028, M['shed']); f['tint'] = (.62, .6, .56); uv_plank(f, 2, 1, 1, .5); P.append(f)
    # the door (ledged and braced, hung on strap hinges, shut with a bolt and a padlock), 0.8 x 1.75 m, left of the middle
    yb = -D / 2 - .021; dx, dw, dz0, dz1 = -.42, .80, .05, 1.80
    for sx in (-1, 1):
        j = box(f'jamb{sx}', (.06, .03, dz1 - dz0 + .06), (dx + sx * (dw / 2 + .032), yb - .013, (dz0 + dz1) / 2 + .03), M['sdoor'], .004, 1); uv_plank(j, 2, 0, 3, .1 + sx); j['tint'] = (.8, .78, .75); P.append(j)
    hd = box('doorhead', (dw + .124, .03, .06), (dx, yb - .013, dz1 + .03), M['sdoor'], .004, 1); uv_plank(hd, 0, 2, 5, .4); hd['tint'] = (.8, .78, .75); P.append(hd)
    for i in range(6):
        b = box(f'dboard{i}', (dw / 6 - .004, .02, dz1 - dz0), (dx - dw / 2 + dw / 6 * (i + .5), yb - .010, (dz0 + dz1) / 2), M['sdoor'], .003, 1)
        k = .78 + r.rand() * .22; b['tint'] = (k, k, k * .97); uv_plank(b, 2, 0, r.randint(6), r.rand()); P.append(b)
    yl = yb - .020
    for k, z in enumerate((.26, .92, 1.58)):
        l = box(f'ledge{k}', (dw - .03, .022, .11), (dx, yl - .011, z), M['sdoor'], .004, 1); l['tint'] = (.9, .88, .85); uv_plank(l, 0, 2, k, .3 * k); P.append(l)
    for k, (za, zb) in enumerate(((.315, .865), (.975, 1.525))):                                              # the braces rise toward the latch side
        br = prism(f'brace{k}', [(dx - dw / 2 + .02, za), (dx - dw / 2 + .13, za), (dx + dw / 2 - .02, zb), (dx + dw / 2 - .13, zb)], 'Y', yl - .021, yl - .001, M['sdoor']); br['tint'] = (.9, .88, .85); uv_plank(br, 0, 2, 4, .7); P.append(br)
    for k, z in enumerate((.26, 1.58)):                                                                       # strap hinges on the west edge
        P.append(prism(f'strap{k}', [(dx - dw / 2 + .0, z - .028), (dx - dw / 2 + .40, z - .012), (dx - dw / 2 + .40, z + .012), (dx - dw / 2 + .0, z + .028)], 'Y', yl - .028, yl - .021, M['iron']))
        P.append(rod(f'knuckle{k}', .011, .075, (dx - dw / 2 - .012, yl - .022, z), M['iron'], 'Z', 10)); P.append(box(f'hplate{k}', (.035, .007, .09), (dx - dw / 2 - .036, yl - .003, z), M['iron'], .002, 1))
    P.append(box('boltplate', (.15, .006, .05), (dx + dw / 2 - .09, yl - .025, .92), M['iron'], .002, 1)); P.append(rod('bolt', .008, .19, (dx + dw / 2 - .05, yl - .034, .92), M['steel'], 'X', 10))
    P.append(box('keep', (.04, .012, .05), (dx + dw / 2 + .034, yb - .034, .92), M['iron'], .002, 1))
    P.append(box('padlock', (.04, .02, .045), (dx + dw / 2 - .11, yl - .04, .875), M['brass'], .004, 2)); P.append(tube('shackle', [(dx + dw / 2 - .122, yl - .04, .895), (dx + dw / 2 - .122, yl - .04, .925), (dx + dw / 2 - .098, yl - .04, .925), (dx + dw / 2 - .098, yl - .04, .895)], .004, M['steel'], .01, 6, 3))
    P.append(box('threshold', (dw + .2, .16, .04), (dx, yb - .08, .02), M['sdoor'], .006, 1)); P[-1]['tint'] = (.7, .68, .64); uv_plank(P[-1], 0, 1, 2, .6)
    # the window, right of the door: a frame standing proud, one upright bar, dark glass
    wx, wz, ww, wh = .66, 1.36, .56, .50
    P.append(box('glass', (ww, .008, wh), (wx, yb - .012, wz), M['pane'], 0))
    for sx in (-1, 1): f = box(f'wjamb{sx}', (.05, .034, wh + .10), (wx + sx * (ww / 2 + .012), yb - .015, wz), M['sdoor'], .004, 1); uv_plank(f, 2, 0, 1, sx * .3); f['tint'] = (.8, .78, .75); P.append(f)
    for sz in (-1, 1): f = box(f'whead{sz}', (ww + .074, .034, .05), (wx, yb - .015, wz + sz * (wh / 2 + .012)), M['sdoor'], .004, 1); uv_plank(f, 0, 2, 0, sz * .2); f['tint'] = (.8, .78, .75); P.append(f)
    f = box('wbar', (.028, .026, wh), (wx, yb - .016, wz), M['sdoor'], .003, 1); uv_plank(f, 2, 0, 2, .8); f['tint'] = (.8, .78, .75); P.append(f)
    f = box('wsill', (ww + .13, .06, .028), (wx, yb - .03, wz - wh / 2 - .048), M['sdoor'], .004, 1); uv_plank(f, 0, 1, 3, .1); f['tint'] = (.75, .73, .7); P.append(f)
    return P


# ---------------------------------------------------------------- the football goal
def goal():
    """a garden football goal, 2 m wide and 1.3 m high, its mouth to the south: steel tube with rounded corners, a stay from
    each top corner back to the ground 70 cm behind, a bar joining the stays' feet, and a net between the crossbar and that
    bar. The sides are open (the Backyard track goes in at the mouth and out under the west stay)."""
    M = ymats(); P = []; W, H, D, R = 2.0, 1.3, .7, .03
    P.append(tube('frame', [(-W / 2, 0, 0), (-W / 2, 0, H), (W / 2, 0, H), (W / 2, 0, 0)], R, M['white'], .09, 12, 6))
    for sx in (-1, 1):
        P.append(tube(f'stay{sx}', [(sx * W / 2, .01, H - .03), (sx * W / 2, D, .024)], R * .8, M['white'], 0, 10))
        P.append(rod(f'foot{sx}', .05, .012, (sx * W / 2, 0, .006), M['white'], 'Z', 16)); P.append(rod(f'elbow{sx}', R * .95, .07, (sx * W / 2, D, .026), M['white'], 'X', 12))
    P.append(tube('back', [(-W / 2, D, .024), (W / 2, D, .024)], R * .8, M['white'], 0, 10))
    # the net: a sheet of 10 cm squares hung from the crossbar to the back bar, bellying out behind, each strand a thin cord
    nx, ny = 20, 15; V = []; F = []
    for j in range(ny + 1):
        for i in range(nx + 1):
            u, v = i / nx, j / ny; s = math.sin(math.pi * u) ** .6 * math.sin(math.pi * v) ** .8
            V.append((-W / 2 + .02 + (W - .04) * u, .01 + (D - .01) * v + .16 * s, H - .01 + (.03 - H) * v - .10 * s * (1 - v)))
    for j in range(ny):
        for i in range(nx): a = j * (nx + 1) + i; F.append((a, a + 1, a + nx + 2, a + nx + 1))
    me = bpy.data.meshes.new('net'); me.from_pydata(V, [], F); me.update(); net = bpy.data.objects.new('net', me); bpy.context.scene.collection.objects.link(net); me.materials.append(M['net'])
    wf = net.modifiers.new('wf', 'WIREFRAME'); wf.thickness = .007; wf.use_replace = True; wf.use_even_offset = False; wf.use_boundary = True
    freeze(net); P.append(net)
    joined(P[0], P[1]); joined(P[1], P[-2])
    return P


# ---------------------------------------------------------------- the washing line
def washing():
    """a washing line 4.8 m long between two steel posts (at x = -2.4 and 2.4), 1.95 m up, sagging a little, with four
    things pegged out on it: each is a sheet of cloth dropped from its pegs and left to hang."""
    M = ymats(); P = []; S = 2.4; r = np.random.RandomState(8)
    line_z = lambda x: 1.95 - .075 * (1 - (x / S) ** 2)
    for sx in (-1, 1):
        P.append(tube(f'post{sx}', [(sx * S, 0, 0), (sx * S, 0, 2.0)], .024, M['steel'], 0, 12)); P.append(tube(f'arm{sx}', [(sx * S, -.25, 1.97), (sx * S, .25, 1.97)], .016, M['steel'], 0, 10))
        P.append(rod(f'collar{sx}', .045, .05, (sx * S, 0, .025), M['steel'], 'Z', 14)); P.append(rod(f'cap{sx}', .028, .012, (sx * S, 0, 2.004), M['iron'], 'Z', 12))
    P.append(tube('line', [(x, 0, line_z(x)) for x in np.linspace(-S, S, 25)], .0035, M['white'], 0, 6, 1, caps=False))
    cloths = []
    for k, (cx, w, h) in enumerate(((-1.4, .62, .62), (-.5, .56, .74), (.5, .62, .60), (1.4, .50, .78))):
        nx, nz = 22, 24; V = []; F = []; UV = []
        for j in range(nz + 1):
            for i in range(nx + 1):
                u, v = i / nx, j / nz; x = cx + (u - .5) * w
                V.append((x, .012 * math.sin(u * 9 + k) * v, line_z(x) - .004 - v * h)); UV.append((u * w, (1 - v) * h))
        for j in range(nz):
            for i in range(nx): a = j * (nx + 1) + i; F.append((a, a + nx + 1, a + nx + 2, a + 1))
        me = bpy.data.meshes.new(f'cloth{k}'); me.from_pydata(V, [], F); me.update(); o = bpy.data.objects.new(f'cloth{k}', me); bpy.context.scene.collection.objects.link(o); me.materials.append(M[f'c{k}'])
        ul = me.uv_layers.new(name='UVMap')
        for l in me.loops: ul.data[l.index].uv = UV[l.vertex_index]
        o['keep_uv'] = 1; smooth(o)
        pegs = (0, nx // 2, nx) if w > .5 else (0, nx)
        vg = o.vertex_groups.new(name='pin'); vg.add([i + d for i in pegs for d in (-1, 0, 1) if 0 <= i + d <= nx], 1.0, 'REPLACE')
        cm = cloth(o, mass=.25, tension=12, bending=.35, self_col=False, quality=6); cm.settings.vertex_group_mass = 'pin'; cm.settings.shrink_min = -.075   # the cloth is 7 % bigger than the distance between its pegs: it sags between them and folds
        cloths.append(o)
        for i in pegs:
            x = cx + (i / nx - .5) * w; x += .012 if i == 0 else -.012 if i == nx else 0
            P.append(box(f'peg{k}{i}', (.011, .014, .072), (x, 0, line_z(x) - .018), M['peg'], .002, 1))
    # a breath of wind from the south-west while they settle, so they do not hang dead flat
    bpy.ops.object.effector_add(type='WIND', location=(0, -3, 1.4), rotation=(-math.pi / 2, 0, 0)); wind = bpy.context.object
    wind.field.strength = 260; wind.field.noise = 2.5; wind.field.flow = .3
    simulate(46); bpy.context.view_layer.update()
    for o in cloths: freeze(o); relax(o, .4, 2); smooth(o); P.append(o)
    bpy.data.objects.remove(wind)
    return P


# ---------------------------------------------------------------- trees
class _Limbs:
    """one mesh for a tree's trunk and branches: each limb is a tube swept along a path, thick at one end and thin at the
    other; the bark's texture runs up it at real size (u once round, v in metres)"""
    def __init__(self): self.V = []; self.F = []; self.UV = []

    def add(self, path, radii, sides, twist=0.0):
        P = [Vector(p) for p in path]; n = len(P); base = len(self.V); v = 0.0; ref = Vector((0, 0, 1))
        for i in range(n):
            d = (P[min(i + 1, n - 1)] - P[max(i - 1, 0)]).normalized()
            a = d.cross(ref); a = a.normalized() if a.length > 1e-4 else d.orthogonal().normalized(); b = d.cross(a).normalized(); ref = a.cross(d)   # carry the frame along so the tube does not twist
            if i: v += (P[i] - P[i - 1]).length
            for k in range(sides):
                t = 2 * math.pi * k / sides + twist; self.V.append(tuple(P[i] + (a * math.cos(t) + b * math.sin(t)) * radii[i]))
            if i:
                rep = max(1, round(2 * math.pi * radii[0] / 1.0))                                               # how many times the bark goes round
                for k in range(sides):
                    q0, q1 = base + (i - 1) * sides + k, base + (i - 1) * sides + (k + 1) % sides
                    self.F.append((q0, q1, q1 + sides, q0 + sides)); u0, u1 = k / sides * rep, (k + 1) / sides * rep
                    self.UV.append(((u0, self._v), (u1, self._v), (u1, v), (u0, v)))
            self._v = v
        self.F.append(tuple(base + (n - 1) * sides + k for k in range(sides))); self.UV.append(tuple((0.5, v) for k in range(sides)))   # the tip

    def build(self, name, m):
        me = bpy.data.meshes.new(name); me.from_pydata(self.V, [], self.F); me.update()
        ul = me.uv_layers.new(name='UVMap')
        for poly, uvs in zip(me.polygons, self.UV):
            for li, uv in zip(poly.loop_indices, uvs): ul.data[li].uv = uv
        o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o); me.materials.append(m)
        bm = bmesh.new(); bm.from_mesh(me); bmesh.ops.recalc_face_normals(bm, faces=bm.faces); bm.to_mesh(me); bm.free()
        smooth(o); o['keep_uv'] = 1
        return o


def _curve(p0, d, length, n, r, droop=0.0, wander=.12):
    """a branch's path: from p0 along d, bending a little as it goes (up for a young branch, down with `droop`)"""
    P = [Vector(p0)]; d = Vector(d).normalized(); step = length / n
    for i in range(n):
        d = (d + Vector(r.randn(3)) * wander + Vector((0, 0, .10 - droop))).normalized(); P.append(P[-1] + d * step)
    return P


def tree(height=6.2, crown=2.5, seed=3, n_leaf=7000, leaf=.10, r0=.15, cards=0):
    """a broadleaf tree: a trunk that spreads at the foot, boughs that fork twice, and a crown of separate leaves gathered
    at the ends of the twigs. `height` to the top of the crown, `crown` its radius, r0 the trunk's radius at chest height.
    Two parts: the wood (ybark) and the leaves (yleaf: each leaf a folded diamond; their greens differ; their shading
    normals point out of the crown, so the tree is lit as a mass and not as confetti).
    With `cards` (their size in metres) the leaves are instead cut-out cards carrying sprays of a real tree's leaves
    (treecards.py; material ycards, the picture is a 2 x 2 sheet): about three to a twig end, facing every way."""
    M = ymats(); r = np.random.RandomState(seed); L = _Limbs(); tips = []
    th = height * .42
    # the trunk, leaning a touch, flared where it meets the ground
    tp = [Vector((0, 0, -.05))]; lean = Vector((r.randn() * .02, r.randn() * .02, 1)).normalized()
    for z in (.08, .25, .6, 1.0, 1.5, 2.0, th * .9, th): tp.append(Vector((lean.x * z + r.randn() * .012, lean.y * z + r.randn() * .012, z)))
    tr = [r0 * 2.0, r0 * 1.55, r0 * 1.22, r0 * 1.08, r0, r0 * .96, r0 * .92, r0 * .88, r0 * .86][:len(tp)]
    L.add(tp, tr, 14)
    top = tp[-1]
    def branch(p0, d, length, rad, level):
        n = 7 if level == 0 else 5 if level == 1 else 3
        P = _curve(p0, d, length, n, r, droop=.04 * level, wander=.15 + .05 * level)
        R = [rad * (1 - .86 * i / n) for i in range(n + 1)]
        L.add(P, R, 9 if level == 0 else 6 if level == 1 else 4)
        if level == 2: tips.append((P[-1], length)); tips.append(((P[-1] + P[-2]) / 2, length * .8)); return
        kids = 4 if level == 0 else 3
        for k in range(kids):
            f = .35 + .6 * (k + r.rand() * .6) / kids; i = min(n - 1, int(f * n)); q = P[i].lerp(P[i + 1], f * n - i)
            dd = (P[i + 1] - P[i]).normalized(); side = dd.cross(Vector((0, 0, 1))); side = side.normalized() if side.length > .05 else Vector((1, 0, 0))
            ang = (1 if k % 2 else -1) * (.6 + r.rand() * .5); up = .25 + r.rand() * .45
            nd = (dd * math.cos(ang) + side * math.sin(ang) + Vector((0, 0, up))).normalized()
            branch(q, nd, length * (.5 + r.rand() * .15), R[i] * .62, level + 1)
        tips.append((P[-1], length * .5))
    nb = 6
    for k in range(nb):
        az = 2 * math.pi * (k + r.rand() * .5) / nb; el = .45 + r.rand() * .5
        d = Vector((math.cos(az) * math.cos(el), math.sin(az) * math.cos(el), math.sin(el)))
        branch(top - Vector((0, 0, r.rand() * th * .22)), d, crown * (.8 + r.rand() * .25), r0 * .50, 0)
    branch(top, lean + Vector((r.randn() * .1, r.randn() * .1, 0)), (height - th) * .78, r0 * .7, 0)          # the leader
    wood = L.build('wood', M['bark'])
    C = Vector((lean.x * (height - crown * .9), lean.y * (height - crown * .9), height - crown * 1.0))          # the middle of the crown
    if cards:
        V = []; F = []; T = []; N = []; UV = []
        for (tip, ln) in tips:
            for q in range(5):
                c = tip + Vector(r.randn(3)) * (.12 + .10 * min(1.5, ln)) + Vector((0, 0, .08)); out = (c - C); out = out.normalized() if out.length > .01 else Vector((0, 0, 1))
                n = (out * .5 + Vector(r.randn(3)) * .9 + Vector((0, 0, .35))).normalized()                      # some face out, some up, some along: from any side and from underneath a few are seen square on
                a = n.cross(Vector(r.randn(3))).normalized(); b = n.cross(a).normalized(); h = cards * (.75 + r.rand() * .5) / 2
                if (a.cross(b)).dot(n) < 0: b = -b
                i0 = len(V); V += [tuple(c - a * h - b * h), tuple(c + a * h - b * h), tuple(c + a * h + b * h), tuple(c - a * h + b * h)]; F.append((i0, i0 + 1, i0 + 2, i0 + 3))
                k = r.randint(4); u0, v0 = (k % 2) * .5, (1 - k // 2) * .5; fl = r.rand() < .5; us = (u0 + .5, u0) if fl else (u0, u0 + .5)
                UV += [(us[0], v0), (us[1], v0), (us[1], v0 + .5), (us[0], v0 + .5)]
                sh = .7 + r.rand() * .3; yel = r.rand() * .16; T += [(sh * (.9 + yel), sh, sh * (.8 + r.rand() * .15), 1)] * 4
                sn = (out * .8 + Vector((0, 0, .45)) + n * .25).normalized(); N += [tuple(sn)] * 4
        me = bpy.data.meshes.new('leaves'); me.from_pydata(V, [], F); me.update()
        me.color_attributes.new('Tint', 'FLOAT_COLOR', 'POINT').data.foreach_set('color', np.array(T, dtype=np.float32).ravel())
        ul = me.uv_layers.new(name='UVMap'); ul.data.foreach_set('uv', np.array(UV, dtype=np.float32).ravel())
        lv = bpy.data.objects.new('leaves', me); bpy.context.scene.collection.objects.link(lv); me.materials.append(mat('ycards', hexcol('#4f8f38'), .9)); smooth(lv); lv['keep_uv'] = 1
        lv['_N'] = [c for nn in N for c in nn]
        return [wood, lv]
    # the leaves, in clumps round the twig ends
    per = max(6, n_leaf // len(tips)); V = []; F = []; T = []; N = []
    for (tip, ln) in tips:
        rad = .34 + .26 * min(1.5, ln) + r.rand() * .14
        q = r.randn(per, 3); q /= np.linalg.norm(q, axis=1, keepdims=True); q *= rad * (.35 + .65 * r.rand(per, 1) ** .6); q[:, 2] *= .75
        for o_ in q:
            c = tip + Vector(o_); out = (c - C); out = out.normalized() if out.length > .01 else Vector((0, 0, 1))
            n = (out * .7 + Vector(r.randn(3)) * .75 + Vector((0, 0, .5))).normalized()                         # leaves face outward and up, loosely
            a = n.cross(Vector(r.randn(3))).normalized(); b = n.cross(a).normalized(); ll = leaf * (.7 + r.rand() * .6); w = ll * .56
            # a pointed oval of six corners, cupped a little: stalk end, two shoulders, two further up, the tip (drooping)
            i0 = len(V); cup = n * ll * .06
            V += [tuple(c - a * ll * .5), tuple(c - a * ll * .18 - b * w * .5 + cup), tuple(c + a * ll * .2 - b * w * .44 + cup), tuple(c + a * ll * .5 - n * ll * .06),
                  tuple(c + a * ll * .2 + b * w * .44 + cup), tuple(c - a * ll * .18 + b * w * .5 + cup)]
            tri = [(0, 1, 5), (1, 2, 5), (2, 4, 5), (2, 3, 4)]
            F += [(i0 + x, i0 + y, i0 + z) if (a.cross(b)).dot(n) > 0 else (i0 + x, i0 + z, i0 + y) for x, y, z in tri]   # wound so the face looks the way its shading normal does (a custom normal cannot lean more than a quarter turn from its face)
            sh = .62 + r.rand() * .38; yel = r.rand() * .22; T += [(sh * (.82 + yel), sh, sh * (.72 + r.rand() * .2), 1)] * 6
            sn = (out * .8 + Vector((0, 0, .45)) + n * .25).normalized(); N += [tuple(sn)] * 6
    me = bpy.data.meshes.new('leaves'); me.from_pydata(V, [], F); me.update()
    me.color_attributes.new('Tint', 'FLOAT_COLOR', 'POINT').data.foreach_set('color', np.array(T, dtype=np.float32).ravel())
    ul = me.uv_layers.new(name='UVMap'); ul.data.foreach_set('uv', np.zeros(len(me.loops) * 2, dtype=np.float32))   # all alike: a new layer's own corners differ, and the exporter then splits every leaf's corners
    lv = bpy.data.objects.new('leaves', me); bpy.context.scene.collection.objects.link(lv); me.materials.append(M['leaf']); smooth(lv); lv['keep_uv'] = 1; lv['normals'] = 1
    lv['_N'] = [c for nn in N for c in nn]
    return [wood, lv]


def leaf_normals(o):
    """give the leaves their outward shading normals (stored by tree(); call after the mesh's last rebuild)"""
    N = o.get('_N')
    if N is None: return
    me = o.data; N = np.array(list(N), dtype=np.float32).reshape(-1, 3)
    if len(N) != len(me.vertices): print('LEAF NORMALS: vertex count changed', len(N), len(me.vertices)); return
    for p in me.polygons: p.use_smooth = True
    me.normals_split_custom_set_from_vertices([tuple(v) for v in N]); me.update()
    del o['_N']


# ---------------------------------------------------------------- the back of the house
W0, W1 = -13.9, 11.6                      # the garden's west and east fences, in garden metres (x = 0 is the bedroom window)


def house():
    """what the back of the house has on it, from the garden: the eaves (soffit, fascia, a gutter on brackets, two
    downpipes), the roof's slope above them, the back door with its step and a lamp beside it, an air brick. In garden
    coordinates: the wall is the plane Y = 0, the garden is north of it (+Y), x = 0 is the middle of the bedroom window.
    The wall itself and the windows are the game's own (toyYard)."""
    M = ymats(); P = []; X0, X1 = W0 - .4, W1 + .4; EZ = 3.0
    sof = box('soffit', (X1 - X0, .44, .02), ((X0 + X1) / 2, .22, EZ - .01), M['trim'], 0); P.append(sof)
    fas = box('fascia', (X1 - X0, .028, .20), ((X0 + X1) / 2, .434, EZ + .06), M['trim'], .004, 1); P.append(fas); joined(sof, fas)
    # the gutter: a half-round trough, its brackets, a stop at each end
    gy, gz, R = .503, EZ + .115, .058; arc = [(gy + R * math.cos(a), gz - R * math.sin(a)) for a in np.linspace(0, math.pi, 9)]
    gut = prism('gutter', arc + [(gy + (R - .006) * math.cos(a), gz - (R - .006) * math.sin(a)) for a in np.linspace(math.pi, 0, 9)], 'X', X0, X1, M['gutter']); P.append(gut); joined(gut, fas)
    for x in (X0, X1): P.append(prism(f'stop{x}', arc, 'X', x - .004, x + .004, M['gutter']))
    x = X0 + .5
    while x < X1: P.append(prism(f'brk{x:.1f}', [(gy + (R + .008) * math.cos(a), gz - (R + .008) * math.sin(a)) for a in np.linspace(0, math.pi, 7)] + [(.447, gz - .005), (.447, gz + .012)], 'X', x - .012, x + .012, M['gutter'])); x += 1.0
    for k, dx in enumerate((3.3, -10.4)):                                                                     # downpipes: out of the gutter, back to the wall in a swan neck, down, a shoe at the foot
        P.append(tube(f'pipe{k}', [(dx, gy, gz - R + .01), (dx, gy, EZ - .10), (dx, .07, EZ - .42), (dx, .07, .16), (dx, .17, .05)], .034, M['gutter'], .07, 12, 5))
        for z in (.6, 1.5, 2.3): P.append(box(f'clip{k}{z}', (.10, .05, .03), (dx, .045, z), M['gutter'], .004, 1))
    # the roof: slates rising to the south at 30 degrees, a barge board at each end
    ry0, rz0, ry1, rz1, t = .56, EZ + .13, -3.2, EZ + .13 + 3.76 * .577, .05
    roof = prism('roof', [(ry0, rz0), (ry1, rz1), (ry1, rz1 + t), (ry0, rz0 + t)], 'X', X0 - .05, X1 + .05, M['slate']); P.append(roof)
    for x in (X0 - .05, X1 + .05): P.append(prism(f'barge{x}', [(ry0, rz0 - .12), (ry1, rz1 - .12), (ry1, rz1 + t + .02), (ry0, rz0 + t + .02)], 'X', x - .015, x + .015, M['trim']))
    P.append(box('eavesfill', (X1 - X0, .10, .16), ((X0 + X1) / 2, .47, EZ + .05), M['trim'], 0))             # behind the gutter, under the first slates
    # the back door at x = -4.3: frame, a door with two panels below and glass above, a lever, a stone step, a lamp
    dx, dw, dh = -4.3, .86, 2.03
    for sx in (-1, 1): P.append(box(f'jamb{sx}', (.07, .09, dh + .07), (dx + sx * (dw / 2 + .035), .045, (dh + .07) / 2), M['trim'], .006, 2))
    P.append(box('head', (dw + .14, .09, .07), (dx, .045, dh + .035), M['trim'], .006, 2))
    P.append(box('leaf', (dw, .045, dh), (dx, .03, dh / 2), M['trim'], .004, 1))
    for sx in (-1, 1): P.append(box(f'panel{sx}', (dw / 2 - .11, .016, .62), (dx + sx * (dw / 4 - .012), .058, .47), M['trim'], .012, 2))
    P.append(box('doorglass', (dw - .20, .012, .86), (dx, .056, 1.44), M['pane'], 0))
    for sx in (-1, 1): P.append(box(f'gbead{sx}', (.022, .02, .90), (dx + sx * (dw / 2 - .10), .06, 1.44), M['trim'], .004, 1))
    for z in (1.0, 1.88): P.append(box(f'gbeadh{z}', (dw - .18, .02, .022), (dx, .06, z), M['trim'], .004, 1))
    P.append(box('gbar', (.02, .018, .86), (dx, .06, 1.44), M['trim'], .003, 1)); P.append(box('gbarh', (dw - .20, .018, .02), (dx, .06, 1.44), M['trim'], .003, 1))
    P.append(box('rose', (.05, .012, .17), (dx + dw / 2 - .07, .058, 1.0), M['steel'], .004, 1)); P.append(tube('lever', [(dx + dw / 2 - .07, .06, 1.03), (dx + dw / 2 - .07, .105, 1.03), (dx + dw / 2 - .19, .105, 1.03)], .009, M['steel'], .015, 8, 3))
    P.append(box('sill', (dw + .2, .14, .045), (dx, .07, .0225), M['stone'], .006, 1)); P.append(box('step', (1.3, .46, .12), (dx, .23 + .12, .06), M['stone'], .012, 2))
    lx = dx + .75
    P.append(box('lampback', (.10, .02, .16), (lx, .01, 1.86), M['iron'], .004, 1)); P.append(tube('lamparm', [(lx, .02, 1.90), (lx, .13, 1.90), (lx, .13, 1.86)], .008, M['iron'], .02, 8, 3))
    P.append(box('lampglass', (.10, .10, .15), (lx, .13, 1.78), M['white'], .008, 2)); P.append(_pyramid('lamptop', .15, .06, (lx, .13, 1.852), M['iron'])); P.append(box('lampfoot', (.11, .11, .012), (lx, .13, 1.70), M['iron'], .003, 1))
    # an air brick low in the wall
    ax = 5.6; P.append(box('airbrick', (.22, .012, .07), (ax, .006, .30), M['iron'], 0))
    for i in range(6): P.append(box(f'slat{i}', (.20, .014, .005), (ax, .012, .273 + i * .011), M['stone'], 0))
    return P


# ---------------------------------------------------------------- the neighbour's house
def neighbour():
    """the house over the back fence, 10 x 7 m with a hipped slate roof: boarded walls, white corner boards and window
    frames, a brick chimney. Its middle is at the origin; the south side is the one the garden sees."""
    M = ymats(); P = []; W, D, E, R = 10.0, 7.0, 3.2, 5.5; r = np.random.RandomState(21)
    P.append(box('core', (W - .04, D - .04, E), (0, 0, E / 2), M['siding'], 0))
    for nm, ln, deg, at in (('s', W, 0, (0, -D / 2, 0)), ('n', W, 180, (0, D / 2, 0)), ('e', D, 90, (W / 2, 0, 0)), ('w', D, -90, (-W / 2, 0, 0))):
        z = .25; i = 0
        while z < E - .05:
            b = prism(f'{nm}{i}', [(0, z), (-.03, z), (-.008, min(E, z + .21)), (0, min(E, z + .21))], 'X', -ln / 2, ln / 2, M['siding']); turn(b, deg, at); P.append(b); z += .19; i += 1
    P.append(box('plinth', (W + .06, D + .06, .26), (0, 0, .13), M['brick'], 0))
    for sx in (-1, 1):
        for sy in (-1, 1): P.append(box(f'corner{sx}{sy}', (.12, .12, E - .2), (sx * (W / 2 + .02), sy * (D / 2 + .02), .25 + (E - .25) / 2), M['trim'], .008, 1))
    # the roof: four slopes over eaves that stand 45 cm out, a ridge 3 m long
    o_ = .45; ex, ey, rx = W / 2 + o_, D / 2 + o_, 1.5; ez = E - .02
    V = [(-ex, -ey, ez), (ex, -ey, ez), (ex, ey, ez), (-ex, ey, ez), (-rx, 0, R), (rx, 0, R)]
    P.append(mesh('roof', V, [(0, 1, 5, 4), (1, 2, 5), (2, 3, 4, 5), (3, 0, 4), (0, 3, 2, 1)], M['slate'], False))
    P.append(box('fasciaS', (2 * ex, .03, .18), (0, -ey + .015, ez - .07), M['trim'], 0)); P.append(box('fasciaN', (2 * ex, .03, .18), (0, ey - .015, ez - .07), M['trim'], 0))
    P.append(box('fasciaE', (.03, 2 * ey, .18), (ex - .015, 0, ez - .07), M['trim'], 0)); P.append(box('fasciaW', (.03, 2 * ey, .18), (-ex + .015, 0, ez - .07), M['trim'], 0))
    P.append(box('soffit', (2 * ex - .04, 2 * ey - .04, .02), (0, 0, ez - .15), M['trim'], 0))
    P.append(tube('ridge', [(-rx, 0, R + .01), (rx, 0, R + .01)], .06, M['gutter'], 0, 8))
    P.append(box('chimney', (.7, .5, 1.7), (2.6, .6, R - .55), M['brick'], .01, 1)); P.append(box('chimcap', (.82, .62, .08), (2.6, .6, R + .33), M['stone'], .01, 1)); P.append(rod('chimpot', .12, .32, (2.6, .6, R + .52), M['terra'], 'Z', 14))
    # windows on the south side and one in each end; a back door
    def window(name, deg, at, x, w=1.1, h=1.25, z=1.75):
        parts = [box(f'{name}g', (w, .02, h), (x, -.035, z), M['pane'], 0)]
        for sx in (-1, 1): parts.append(box(f'{name}j{sx}', (.09, .06, h + .18), (x + sx * (w / 2 + .045), -.05, z), M['trim'], .006, 1))
        for sz in (-1, 1): parts.append(box(f'{name}h{sz}', (w + .18, .06, .09), (x, -.05, z + sz * (h / 2 + .045)), M['trim'], .006, 1))
        parts.append(box(f'{name}m', (.05, .04, h), (x, -.05, z), M['trim'], .004, 1)); parts.append(box(f'{name}t', (w, .04, .05), (x, -.05, z + h * .16), M['trim'], .004, 1))
        parts.append(box(f'{name}s', (w + .3, .12, .05), (x, -.09, z - h / 2 - .115), M['trim'], .006, 1))
        for q in parts: turn(q, deg, at); P.append(q)
    for k, wx in enumerate((-2.6, .2, 2.9)): window(f'ws{k}', 0, (0, -D / 2, 0), wx)
    window('we', 90, (W / 2, 0, 0), .6); window('ww', -90, (-W / 2, 0, 0), -.4); window('wn', 180, (0, D / 2, 0), 1.0)
    P.append(box('door', (.9, .05, 2.05), (-4.0, -D / 2 - .03, 1.28), M['gcoat'], .006, 1)); P.append(box('doorframe', (1.06, .04, 2.2), (-4.0, -D / 2 - .012, 1.3), M['trim'], .006, 1)); P.append(box('doorstep', (1.3, .5, .25), (-4.0, -D / 2 - .25, .125), M['stone'], .01, 1))
    return P


# ---------------------------------------------------------------- pots, and the plants in them
def _leaf(V, F, T, base, d, n, ll, w, r, sh, nseg=3):
    """one pointed leaf from `base` along d, its face n, arching over toward its tip; corners appended to V, faces to F"""
    a = Vector(d).normalized(); nn = Vector(n).normalized(); b = nn.cross(a).normalized(); i0 = len(V)
    V.append(tuple(base)); prev = [i0]; T.append((sh * .8, sh * .8, sh * .7, 1))
    for i in range(1, nseg + 1):
        t = i / (nseg + 1); c = Vector(base) + a * ll * t - nn * ll * .22 * t * t + Vector((0, 0, -.10 * ll * t * t)); hw = w * .5 * math.sin(math.pi * (t * .85 + .08)) ; cup = nn * hw * .25
        V += [tuple(c - b * hw + cup), tuple(c), tuple(c + b * hw + cup)]; cur = [len(V) - 3, len(V) - 2, len(V) - 1]; T += [(sh, sh, sh * .85, 1)] * 3
        if len(prev) == 1: F += [(prev[0], cur[0], cur[1]), (prev[0], cur[1], cur[2])]
        else: F += [(prev[0], cur[0], cur[1], prev[1]), (prev[1], cur[1], cur[2], prev[2])]
        prev = cur
    tip = Vector(base) + a * ll - nn * ll * .22 + Vector((0, 0, -.10 * ll)); V.append(tuple(tip)); T.append((sh, sh, sh * .85, 1)); it = len(V) - 1
    F += [(prev[0], it, prev[1]), (prev[1], it, prev[2])]


def pot(kind=1, seed=5):
    """a terracotta pot (rim 10.8 cm in radius, 17 cm tall) on a saucer, with a plant: kind 1 a bushy plant with red
    flower heads, 2 a clump of arching grass, 3 a leafier plant with yellow flowers. About 45 cm tall in all; the game
    scales it to the pot it wants."""
    M = ymats(); r = np.random.RandomState(seed * 7 + kind); P = []
    P.append(lathe('pot', [(0, .012), (.068, .012), (.075, .0), (.082, .012), (.100, .148), (.110, .150), (.112, .172), (.104, .174), (.100, .160), (.094, .156), (.074, .03), (0, .03)], 28, M['terra']))
    P.append(lathe('saucer', [(0, 0), (.095, 0), (.118, .022), (.112, .024), (.092, .008), (0, .008)], 28, M['terra']))
    soil = lathe('soil', [(0, .152), (.05, .151), (.097, .146)], 20, M['soil']); P.append(soil)
    V = []; F = []; T = []; top = Vector((0, 0, .15))
    if kind == 2:
        for i in range(46):
            az = r.rand() * 6.283; lean = .15 + r.rand() * .75; ll = .30 + r.rand() * .26; d = Vector((math.cos(az) * math.sin(lean), math.sin(az) * math.sin(lean), math.cos(lean)))
            n = Vector((-math.cos(az) * math.cos(lean), -math.sin(az) * math.cos(lean), math.sin(lean)))
            _leaf(V, F, T, top + Vector((math.cos(az), math.sin(az), 0)) * r.rand() * .05, d, -n, ll, .022 + r.rand() * .012, r, .6 + r.rand() * .4, 4)
    else:
        stems = []; ns = 12 if kind == 1 else 15
        for i in range(ns):
            az = 6.283 * (i + r.rand() * .6) / ns; lean = .12 + r.rand() * .5; ln = .16 + r.rand() * .16
            d = Vector((math.cos(az) * math.sin(lean), math.sin(az) * math.sin(lean), math.cos(lean))); b0 = top + Vector((math.cos(az), math.sin(az), 0)) * r.rand() * .05; e = b0 + d * ln
            stems.append((b0, e, d)); P.append(tube(f'stem{i}', [tuple(b0), tuple(b0 + d * ln * .5 + Vector((0, 0, .01))), tuple(e)], .0032, M['leaf'], .03, 5, 2))
            for k in range(5 if kind == 1 else 7):
                f = .3 + .7 * r.rand(); q = b0.lerp(e, f); la = r.rand() * 6.283; ld = (Vector((math.cos(la), math.sin(la), .25)) + d * .3).normalized()
                _leaf(V, F, T, q, ld, Vector((0, 0, 1)), (.075 if kind == 1 else .10) * (.7 + r.rand() * .6), (.062 if kind == 1 else .034) * (.8 + r.rand() * .4), r, .6 + r.rand() * .4, 2)
        pm = M['petal'] if kind == 1 else M['petal2']
        for i in range(0, ns, 2):                                                                             # a flower head on every other stem: a bunch of small blooms
            b0, e, d = stems[i]; c = e + d * .03; P.append(tube(f'fstalk{i}', [tuple(e), tuple(c)], .0025, M['leaf'], 0, 5))
            for k in range(7 if kind == 1 else 1):
                o_ = Vector(r.randn(3)) * (.016 if kind == 1 else 0); P.append(ball(f'bloom{i}{k}', .014 if kind == 1 else .024, tuple(c + o_), pm, (1, 1, .7 if kind == 1 else .45), 8, 5))
            if kind == 3: P.append(ball(f'eye{i}', .010, tuple(c + Vector((0, 0, .008))), M['gboot'], (1, 1, .6), 8, 4))
    me = bpy.data.meshes.new('fronds'); me.from_pydata(V, [], F); me.update()
    me.color_attributes.new('Tint', 'FLOAT_COLOR', 'POINT').data.foreach_set('color', np.array(T, dtype=np.float32).ravel())
    ul = me.uv_layers.new(name='UVMap'); ul.data.foreach_set('uv', np.zeros(len(me.loops) * 2, dtype=np.float32))
    fr = bpy.data.objects.new('fronds', me); bpy.context.scene.collection.objects.link(fr); me.materials.append(M['leaf']); smooth(fr); fr['keep_uv'] = 1; P.append(fr)
    return P


# ---------------------------------------------------------------- small things
def wcan():
    """a watering can, 40 cm from handle to rose: its spout points east (+X)"""
    M = ymats(); m = M['can']; P = []
    P.append(lathe('body', [(0, 0), (.105, 0), (.110, .01), (.104, .22), (.098, .225), (.094, .215), (.100, .012), (0, .012)], 28, m))
    P.append(mesh('hood', [(-.098 * math.cos(a), .098 * math.sin(a), .222) for a in np.linspace(-math.pi / 2, math.pi / 2, 9)] + [(-.02, .098 * math.sin(a), .236) for a in np.linspace(-math.pi / 2, math.pi / 2, 9)], [(i, i + 1, i + 10, i + 9) for i in range(8)], m))
    P.append(bar('spout', (.085, 0, .045), (.30, 0, .262), .026, .013, m, 12)); P.append(bar('rose', (.292, 0, .254), (.335, 0, .297), .016, .042, m, 16)); P.append(rod('roseface', .042, .004, (.3355, 0, .2975), M['steel'], 'Z', 16))
    P[-1].rotation_euler = (0, math.pi / 4, 0); apply_scale(P[-1])
    P.append(bar('strut', (.10, 0, .215), (.215, 0, .178), .005, .005, m, 6))
    P.append(tube('handleback', [(-.098, 0, .19), (-.20, 0, .20), (-.21, 0, .08), (-.105, 0, .04)], .011, m, .06, 8, 5))
    P.append(tube('handletop', [(-.07, 0, .225), (-.05, 0, .32), (.06, 0, .32), (.085, 0, .225)], .010, m, .05, 8, 5))
    return P


def hose():
    """a garden hose coiled on the ground under the tap on the house wall: the coil's middle is the origin, the wall
    35 cm to the south (Y = -0.35), the tap 60 cm up it"""
    M = ymats(); P = []; pts = []
    for i in range(0, 5 * 24 + 1):
        a = i / 24 * 2 * math.pi; rr = .19 - .008 * (i / 24) + .006 * math.sin(a * 3.1); pts.append((rr * math.cos(a), rr * math.sin(a), .014 + .024 * (i / 24) * .55 + .004 * math.sin(a * 2 + i)))
    last = Vector(pts[-1]); pts += [tuple(last + Vector((.02, -.10, .0))), (.10, -.26, .03), (.06, -.325, .30), (.0, -.325, .52)]
    P.append(tube('hose', pts, .011, M['hose'], .05, 8, 3))
    P.append(box('plate', (.07, .012, .07), (0, -.344, .60), M['brass'], .004, 1)); P.append(tube('tap', [(0, -.345, .60), (0, -.30, .60), (0, -.30, .53)], .013, M['brass'], .02, 8, 3))
    P.append(rod('tapstem', .008, .05, (0, -.30, .63), M['brass'], 'Z', 8)); P.append(tube('taphandle', [(-.035, -.30, .655), (.035, -.30, .655)], .007, M['brass'], 0, 8)); P.append(rod('union', .017, .03, (0, -.325, .52), M['brass'], 'Z', 10))
    P[-1].location = (0, -.3125, .525); bpy.context.view_layer.update()
    return P


def gnome():
    """a garden gnome, 33 cm: made up, nobody's design. He faces south (-Y)."""
    M = ymats(); P = []
    P.append(lathe('coat', [(0, .03), (.058, .03), (.066, .06), (.060, .13), (.045, .175), (.03, .19), (0, .19)], 20, M['gcoat']))
    P.append(lathe('belt', [(.061, .088), (.066, .09), (.0655, .108), (.061, .11)], 20, M['gbelt'])); P.append(box('buckle', (.022, .008, .022), (0, -.066, .099), M['brass'], .003, 1))
    P.append(ball('head', .046, (0, 0, .212), M['gskin'], (1, 1, 1.02), 16, 10)); P.append(ball('nose', .013, (0, -.047, .212), M['gskin'], (1, 1, 1), 10, 6))
    P.append(ball('beard', .05, (0, -.022, .178), M['gbeard'], (.95, .62, 1.05), 14, 9)); P.append(ball('beardtip', .028, (0, -.03, .135), M['gbeard'], (.9, .6, 1.2), 10, 6))
    P.append(lathe('hat', [(.05, .236), (.047, .252), (.036, .285), (.022, .315), (.009, .335), (0, .342)], 18, M['ghat'])); P.append(lathe('hatband', [(.047, .228), (.052, .231), (.052, .241), (.048, .245)], 18, M['ghat']))
    for sx in (-1, 1):
        P.append(tube(f'arm{sx}', [(sx * .05, 0, .165), (sx * .078, -.012, .125), (sx * .062, -.045, .10)], .016, M['gcoat'], .03, 8, 3)); P.append(ball(f'hand{sx}', .015, (sx * .062, -.048, .098), M['gskin']))
        P.append(ball(f'boot{sx}', .03, (sx * .028, -.022, .018), M['gboot'], (.8, 1.35, .62), 12, 7)); P.append(ball(f'eye{sx}', .0055, (sx * .017, -.041, .224), M['gbelt'], (1, 1, 1), 8, 5))
    return P


def pipe(r_in=.37, length=1.5, wall=.05, centre=.0576):
    """a length of concrete drain pipe lying half sunk in the lawn, its bore along X: the Backyard track runs through it.
    Only what is above the ground is modelled (and a hand's width below). A thicker collar at the west end."""
    M = ymats(); P = []
    def ring(name, ri, ro, x0, x1, n=30):
        a0 = math.asin(max(-1, (-.05 - centre) / ro)); A = np.linspace(a0, math.pi - a0, n); V = []; F = []
        for x in (x0, x1):
            for a in A: V.append((x, ri * math.cos(a), centre + ri * math.sin(a)))
            for a in A: V.append((x, ro * math.cos(a), centre + ro * math.sin(a)))
        for i in range(n - 1): F += [(i, i + 1, 2 * n + i + 1, 2 * n + i), (n + i, 3 * n + i, 3 * n + i + 1, n + i + 1), (i, n + i, n + i + 1, i + 1), (2 * n + i, 2 * n + i + 1, 3 * n + i + 1, 3 * n + i)]
        return mesh(name, V, F, M['conc'])
    P.append(ring('barrel', r_in, r_in + wall, -length / 2, length / 2)); P.append(ring('collar', r_in + wall - .004, r_in + wall + .035, -length / 2 - .001, -length / 2 + .16))
    return P


def football():
    """a football, 22 cm: white with dark patches. It sits on the origin."""
    M = ymats(); bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=4, radius=.11, location=(0, 0, .11)); o = bpy.context.object; o.name = 'ball'; o.data.materials.append(M['ball']); o.data.materials.append(M['ballb'])
    t = (1 + 5 ** .5) / 2; ico = [Vector(v).normalized() for v in ((-1, t, 0), (1, t, 0), (-1, -t, 0), (1, -t, 0), (0, -1, t), (0, 1, t), (0, -1, -t), (0, 1, -t), (t, 0, -1), (t, 0, 1), (-t, 0, -1), (-t, 0, 1))]
    for p in o.data.polygons:
        c = (p.center - Vector((0, 0, .11))).normalized(); p.material_index = 1 if max(c.dot(v) for v in ico) > .945 else 0
    smooth(o); return [o]


def tuft(seed=2, blades=12):
    """a tuft of longer grass, the kind a mower leaves along a fence: a dozen blades up to 15 cm, bending outward"""
    M = ymats(); r = np.random.RandomState(seed); V = []; F = []; T = []
    for i in range(blades):
        az = r.rand() * 6.283; lean = .1 + r.rand() * .55; ll = .07 + r.rand() * .09
        d = Vector((math.cos(az) * math.sin(lean), math.sin(az) * math.sin(lean), math.cos(lean))); n = Vector((-math.cos(az) * math.cos(lean), -math.sin(az) * math.cos(lean), math.sin(lean)))
        _leaf(V, F, T, Vector((math.cos(az), math.sin(az), 0)) * r.rand() * .035, d, -n, ll, .009 + r.rand() * .005, r, .7 + r.rand() * .3, 2)
    me = bpy.data.meshes.new('tuft'); me.from_pydata(V, [], F); me.update()
    me.color_attributes.new('Tint', 'FLOAT_COLOR', 'POINT').data.foreach_set('color', np.array(T, dtype=np.float32).ravel())
    ul = me.uv_layers.new(name='UVMap'); ul.data.foreach_set('uv', np.zeros(len(me.loops) * 2, dtype=np.float32))
    o = bpy.data.objects.new('tuft', me); bpy.context.scene.collection.objects.link(o); me.materials.append(M['grass']); smooth(o); o['keep_uv'] = 1
    return [o]
