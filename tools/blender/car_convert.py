"""Convert a downloaded car model into the game's packed car format (an entry of CAR_PACKS in crust-rush.html).
usage: blender --background --python car_convert.py -- <id> [fast]
Writes D:/crust-rush/blender/cars/<id>/<id>.json (the pack, its high-quality twin and the measurements the game's car
definition needs) and check pictures. `car_pack.py` then puts the pack into the game. `fast` skips the high-quality twin.

What it does, in order:
 1. reads every mesh as loose triangles with the model's own normals, sorted by material (car_rules.py says what each
    material becomes: paint, glass, lights, a trim colour, the cabin, a wheel part, or nothing);
 2. turns the car to the game's frame and size (front along -Y here, 12.2 units long, tyres on the ground);
 3. finds the four wheels from the tyres and takes them off the body; each tyre is rebuilt as a clean round one of the
    same size (a simplified tyre comes out as a polygon);
 4. simplifies each group to the game's budget, bakes soft shadow into the vertices, and gives the simplified surface
    the ORIGINAL model's normals (so a car with a tenth of the triangles still reflects like the smooth original);
 5. packs it the way `carGeos` in the game reads it.
Badges, number plates, stickers and every texture are left out: the game paints the car itself, with no maker's marks.
The model files are other people's data and are only ever read.

Lessons built in (each was a visible fault on the first car):
 - simplifying a group of thousands of loose pieces to 2% leaves long stray triangles: the smallest pieces are removed
   first so no group is ever asked for less than a sixth, and any triangle that ends up away from the original is dropped;
 - Blender's simplifier stops early on meshes full of open edges, so the far model is made by snapping vertices to a
   grid instead (as the game does for its own far models);
 - a cabin simplified to 900 triangles loses its floor, and the ground shows through the windscreen: every car gets a
   plain dark tub under its cabin (a floor and four low walls that face inward, so they are only seen through the glass);
 - normals looked up per triangle differ a hair from one triangle to the next, which would give every corner its own
   vertex (a pack three times the size): corners of a vertex that agree within 24 degrees share their average.
"""
import sys, os, re, json, math, base64, time
import bpy
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import crlib
from car_rules import CARS

IN = 'D:/crust-rush/scratch/cars_in'; OUT = 'D:/crust-rush/blender/cars'
LEN = 12.2
CLS = ['paint', 'dark', 'stripe', 'tail', 'light', 'glass', 'carbon', 'metal', 'rubber', 'seat', 'chrome', 'rim', 'disc', 'caliper', 'blue', 'gunmetal', 'green', 'red', 'bluem', 'bronze', 'white']
# colour, roughness, metalness of each class, as CAR_PBR in the game (the paint is shown red in the check pictures)
PBR = dict(paint=('#c8261b', .3, .5), dark=('#161618', .36, .25), stripe=('#ffffff', .36, .5), tail=('#ff2a1a', .4, 0), light=('#ffffff', .2, 0), glass=('#0b0d10', .05, 0),
           carbon=('#161618', .36, .25), metal=('#76777d', .32, .9), rubber=('#121212', .9, 0), seat=('#1c1918', .8, 0), chrome=('#e9e9ee', .1, 1), rim=('#b5b7be', .24, .95), disc=('#58595d', .45, .85),
           caliper=('#c8321e', .35, .2), blue=('#2a5bff', .3, 0), gunmetal=('#3b3e44', .26, .9), green=('#3f9a1a', .34, .6), red=('#c0180c', .3, .5), bluem=('#1d7fe6', .22, .85), bronze=('#8a6232', .3, .95), white=('#eeeeee', .3, 0))
BASE = dict(paint=9000, vc=6000, int=900, glass=400, tail=300, light=450, wheel=1700)
HQ = dict(paint=22500, vc=15000, int=2600, glass=1000, tail=800, light=1100)
LOD = dict(paint=880, vc=600, glass=50, tail=30, light=40)
RUB = CLS.index('rubber')
T0 = time.time()


def log(*a): print('[car %5.0fs]' % (time.time() - T0), *a); sys.stdout.flush()


# ---------------------------------------------------------------- reading
def read_scene(path):
    crlib.reset()
    if path.lower().endswith('.fbx'): bpy.ops.import_scene.fbx(filepath=path)
    else: bpy.ops.import_scene.gltf(filepath=path)
    soups = {}
    for o in bpy.context.scene.objects:
        if o.type != 'MESH' or not len(o.data.polygons): continue
        me = o.data; mw = np.array(o.matrix_world, dtype=np.float64); R = mw[:3, :3]; T = mw[:3, 3]
        nv = len(me.vertices); co = np.empty(nv * 3, np.float32); me.vertices.foreach_get('co', co); co = co.reshape(-1, 3).astype(np.float64)
        me.calc_loop_triangles(); nt = len(me.loop_triangles)
        tv = np.empty(nt * 3, np.int32); me.loop_triangles.foreach_get('vertices', tv)
        tl = np.empty(nt * 3, np.int32); me.loop_triangles.foreach_get('loops', tl)
        tm = np.empty(nt, np.int32); me.loop_triangles.foreach_get('material_index', tm)
        cn = np.empty(len(me.loops) * 3, np.float32); me.corner_normals.foreach_get('vector', cn); cn = cn.reshape(-1, 3).astype(np.float64)
        P = (co @ R.T + T)[tv].reshape(nt, 3, 3)
        N = (cn @ np.linalg.inv(R))[tl]; N /= np.maximum(np.linalg.norm(N, axis=1, keepdims=True), 1e-12); N = N.reshape(nt, 3, 3)
        if np.linalg.det(R) < 0: P = P[:, ::-1]; N = N[:, ::-1]          # a mirrored object: its triangles wind the other way
        U = np.zeros((nt, 2))
        if me.uv_layers.active:
            uv = np.empty(len(me.loops) * 2, np.float32); me.uv_layers.active.data.foreach_get('uv', uv); U = uv.reshape(-1, 2).astype(np.float64)[tl].reshape(nt, 3, 2).mean(1)
        names = [m.name if m else '(none)' for m in me.materials] or ['(none)']
        for mi in np.unique(tm):
            k = tm == mi; nm = names[mi] if mi < len(names) else '(none)'
            soups.setdefault(f'{nm}@{o.name}', []).append((P[k], N[k], U[k]))
    for o in list(bpy.context.scene.objects): bpy.data.objects.remove(o)
    return {k: tuple(np.concatenate([x[j] for x in v]) for j in range(3)) for k, v in soups.items()}


def target_of(key, rules):
    for rx, t in rules:
        if re.search(rx, key, re.I): return t
    return None


def fnormal(P):
    n = np.cross(P[:, 1] - P[:, 0], P[:, 2] - P[:, 0]); a = np.linalg.norm(n, axis=1)
    return n / np.maximum(a, 1e-20)[:, None], a / 2


# ---------------------------------------------------------------- mesh helpers (plain arrays)
def weld(P, extra=None, tol=3e-4):
    """loose triangles -> shared vertices; `extra` (one value per triangle) is carried along"""
    X = P.reshape(-1, 3); q = np.round(X / tol).astype(np.int64) + (1 << 20)
    key = (q[:, 0] << 42) | (q[:, 1] << 21) | q[:, 2]
    _, first, inv = np.unique(key, return_index=True, return_inverse=True)
    F = inv.reshape(-1, 3); ok = (F[:, 0] != F[:, 1]) & (F[:, 1] != F[:, 2]) & (F[:, 0] != F[:, 2])
    return X[first], F[ok], (None if extra is None else extra[ok])


def pieces(V, F):
    """the loose pieces of a mesh: for every triangle, its piece's size across and its piece's number"""
    lab = np.arange(len(V))
    for _ in range(4000):
        m = lab[F].min(1); new = lab.copy()
        for j in range(3): np.minimum.at(new, F[:, j], m)
        for _ in range(6): new = new[new]
        if np.array_equal(new, lab): break
        lab = new
    lo = np.full((len(V), 3), 1e9); hi = -lo
    np.minimum.at(lo, lab, V); np.maximum.at(hi, lab, V)
    return np.linalg.norm(hi - lo, axis=1)[lab[F[:, 0]]], lab[F[:, 0]]


def drop_small(V, F, C, thresh):
    """remove loose pieces smaller than `thresh` across (bolts, clips, wires: they eat the triangle budget unseen)"""
    if not len(F) or thresh <= 0: return F, C
    size, _ = pieces(V, F); keep = size >= thresh
    return F[keep], C[keep]


def keep_largest(V, F, C, limit):
    """keep whole pieces, largest first, until `limit` triangles are reached"""
    if len(F) <= limit: return F, C
    size, pid = pieces(V, F); order = np.argsort(-size, kind='stable'); pid_o = pid[order]
    first = np.r_[True, pid_o[1:] != pid_o[:-1]]; grp = np.cumsum(first) - 1; cnt = np.bincount(grp); cum = np.cumsum(cnt)
    ok_grp = cum <= max(limit, cnt[0]); keep = np.zeros(len(F), bool); keep[order[ok_grp[grp]]] = True
    return F[keep], C[keep]


def compact(V, F):
    used = np.unique(F); mp = np.full(len(V), -1); mp[used] = np.arange(len(used)); return V[used], mp[F]


def cluster(V, F, C, budget):
    """the far model: snap vertices to a grid, as coarse as the budget needs"""
    lo = V.min(0); size = (V.max(0) - lo).max()
    def run(cells):
        q = np.floor((V - lo) / (size / cells)).astype(np.int64); key = q[:, 0] | (q[:, 1] << 12) | (q[:, 2] << 24)
        u, inv = np.unique(key, return_inverse=True); G = inv[F]; ok = (G[:, 0] != G[:, 1]) & (G[:, 1] != G[:, 2]) & (G[:, 0] != G[:, 2]); G = G[ok]; Cc = C[ok]
        if not len(G): return np.zeros((0, 3)), G, Cc
        G = np.take_along_axis(G, (np.argmin(G, 1)[:, None] + np.arange(3)) % 3, 1)      # smallest index first, winding kept
        _, first = np.unique(G, axis=0, return_index=True); G = G[first]; Cc = Cc[first]
        cnt = np.bincount(inv, minlength=len(u)); Vc = np.stack([np.bincount(inv, V[:, j], len(u)) / cnt for j in range(3)], 1)
        return Vc, G, Cc
    a, b = 3, 220
    while b - a > 1:
        m = (a + b) // 2
        if len(run(m)[1]) <= budget: a = m
        else: b = m
    Vc, G, Cc = run(a); Vc, G = compact(Vc, G) if len(G) else (Vc, G)
    return Vc, G, Cc


def unify(F, N, bad, cos=math.cos(math.radians(24))):
    """corners of one vertex whose normals agree share their average (so they pack as one vertex); a corner with no
    normal of its own (`bad`) takes the nearest of its vertex's, or stays flat"""
    n = len(F); v = F.ravel(); X = N.reshape(-1, 3).copy(); bd = bad.ravel(); nv = int(F.max()) + 1 if n else 0
    acc = np.zeros((nv, 3)); np.add.at(acc, v[~bd], X[~bd]); acc /= np.maximum(np.linalg.norm(acc, axis=1), 1e-12)[:, None]
    d = (X * acc[v]).sum(1); d[bd] = 1; mind = np.ones(nv); np.minimum.at(mind, v, d)
    sm = (mind[v] >= cos) & ~bd; X[sm] = acc[v][sm]
    rest = np.nonzero(~sm & ~bd)[0]; by = {}
    for i in rest.tolist(): by.setdefault(int(v[i]), []).append(i)
    for vi, lst in by.items():
        rem = lst
        while rem:
            seed = X[rem[0]]; mem = [i for i in rem if X[i] @ seed >= cos]; avg = X[mem].sum(0); avg /= max(np.linalg.norm(avg), 1e-12)
            X[mem] = avg; rem = [i for i in rem if i not in set(mem)]
    if bd.any():                                                     # corners without a normal: borrow the best-fitting one at the same vertex
        good = {}
        for i in np.nonzero(~bd & np.isin(v, v[bd]))[0].tolist(): good.setdefault(int(v[i]), []).append(i)
        for i in np.nonzero(bd)[0].tolist():
            c = good.get(int(v[i]))
            if c:
                dd = X[c] @ X[i]; j = int(np.argmax(dd))
                if dd[j] > .6: X[i] = X[c[j]]
    return X.reshape(n, 3, 3)


def lathe_tyre(c, r, rin, hw, seg=36):
    """a clean round tyre: centre c, outer radius r, bead radius rin, half width hw (the axle runs along X)"""
    h = r - rin; prof = [(-.78, rin), (-.97, rin + .30 * h), (-1.0, rin + .60 * h), (-.93, rin + .88 * h), (-.74, r), (0, r), (.74, r), (.93, rin + .88 * h), (1.0, rin + .60 * h), (.97, rin + .30 * h), (.78, rin)]
    pr = np.array([(a * hw, b) for a, b in prof]); n = len(pr); tan = np.gradient(pr, axis=0); pn = np.stack([-tan[:, 1], tan[:, 0]], 1); pn /= np.linalg.norm(pn, axis=1)[:, None]
    if pn[n // 2, 1] < 0: pn = -pn
    th = np.arange(seg) * 2 * math.pi / seg; cs, sn = np.cos(th), np.sin(th)
    V = np.stack([np.repeat(pr[:, 0], seg), np.outer(pr[:, 1], cs).ravel(), np.outer(pr[:, 1], sn).ravel()], 1) + c
    Nv = np.stack([np.repeat(pn[:, 0], seg), np.outer(pn[:, 1], cs).ravel(), np.outer(pn[:, 1], sn).ravel()], 1)
    F = []
    for i in range(n - 1):
        for j in range(seg):
            a = i * seg + j; b = i * seg + (j + 1) % seg; d = a + seg; e = b + seg; F += [(a, b, e), (a, e, d)]
    F = np.array(F); fn, _ = fnormal(V[F]); flip = (fn * Nv[F].mean(1)).sum(1) < 0; F[flip] = F[flip][:, ::-1]
    shade = np.array([.45, .7, .85, .9, .85, .8, .85, .9, .85, .7, .45]); ao = np.repeat(shade, seg)
    return V, F, np.full(len(F), RUB, np.int32), ao, Nv[F]


def tub(x, y0, y1, z0, z1):
    """the cabin's liner: an open-topped box seen from inside (a floor and four walls, all facing inward)"""
    V = np.array([[-x, y0, z0], [x, y0, z0], [x, y1, z0], [-x, y1, z0], [-x, y0, z1], [x, y0, z1], [x, y1, z1], [-x, y1, z1]], float)
    Q = [(0, 1, 2, 3), (0, 4, 5, 1), (3, 2, 6, 7), (0, 3, 7, 4), (1, 5, 6, 2)]; F = np.array([t for a, b, c, d in Q for t in ((a, b, c), (a, c, d))])
    fn, _ = fnormal(V[F]); ao = np.array([.3] * 4 + [.5] * 4)
    return V, F, np.full(len(F), CLS.index('seat'), np.int32), ao, np.repeat(fn[:, None, :], 3, 1)


# ---------------------------------------------------------------- Blender objects
def cls_mat(c):
    m = bpy.data.materials.get('c_' + c)
    if m: return m
    col, rough, metal = PBR[c]; m = bpy.data.materials.new('c_' + c); m.use_nodes = True
    nt = m.node_tree; b = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED'); rgb = crlib.hexcol(col)
    at = nt.nodes.new('ShaderNodeAttribute'); at.attribute_name = 'Col'; mx = nt.nodes.new('ShaderNodeMix'); mx.data_type = 'RGBA'; mx.blend_type = 'MULTIPLY'; mx.inputs[0].default_value = 1
    mx.inputs[6].default_value = (*rgb[:3], 1); nt.links.new(at.outputs['Color'], mx.inputs[7]); nt.links.new(mx.outputs[2], b.inputs['Base Color'])
    b.inputs['Roughness'].default_value = rough; b.inputs['Metallic'].default_value = metal
    if c == 'paint': b.inputs['Coat Weight'].default_value = 1; b.inputs['Coat Roughness'].default_value = .04
    if c == 'glass': b.inputs['Alpha'].default_value = .35
    if c in ('light', 'tail'): b.inputs['Emission Color'].default_value = (*rgb[:3], 1); b.inputs['Emission Strength'].default_value = .6
    return m


def mk_obj(name, V, F, C, ao=None, N=None):
    """a Blender object from vertices, triangles and one class number per triangle (kept as the material index)"""
    me = bpy.data.meshes.new(name)
    me.vertices.add(len(V)); me.vertices.foreach_set('co', V.astype(np.float32).ravel())
    me.loops.add(len(F) * 3); me.loops.foreach_set('vertex_index', F.astype(np.int32).ravel())
    me.polygons.add(len(F)); me.polygons.foreach_set('loop_start', np.arange(0, len(F) * 3, 3, dtype=np.int32))
    try: me.polygons.foreach_set('loop_total', np.full(len(F), 3, np.int32))
    except Exception: pass
    used = sorted(set(C.tolist())) or [1]; slot = {c: i for i, c in enumerate(used)}
    for c in used: me.materials.append(cls_mat(CLS[c]))
    me.polygons.foreach_set('material_index', np.array([slot[c] for c in C.tolist()], np.int32))
    me.update(calc_edges=True)
    if N is None: me.validate()
    ca = me.color_attributes.new('Col', 'FLOAT_COLOR', 'POINT'); a = np.ones(len(V)) if ao is None else ao
    ca.data.foreach_set('color', np.repeat(a.astype(np.float32), 4).reshape(-1, 4).ravel())
    if N is not None:
        me.polygons.foreach_set('use_smooth', np.ones(len(F), bool)); me.normals_split_custom_set(N.reshape(-1, 3).tolist())
    o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o); o['cls'] = used
    return o


def read_obj(o):
    me = o.data; nv = len(me.vertices); V = np.empty(nv * 3, np.float32); me.vertices.foreach_get('co', V); V = V.reshape(-1, 3).astype(np.float64)
    me.calc_loop_triangles(); nt = len(me.loop_triangles); F = np.empty(nt * 3, np.int32); me.loop_triangles.foreach_get('vertices', F); F = F.reshape(-1, 3)
    mi = np.empty(nt, np.int32); me.loop_triangles.foreach_get('material_index', mi); used = np.array(list(o['cls']), np.int32)
    C = used[np.clip(mi, 0, len(used) - 1)]
    ao = np.ones(nv)
    if 'Col' in me.color_attributes:
        c = np.empty(nv * 4, np.float32); me.color_attributes['Col'].data.foreach_get('color', c); ao = c.reshape(-1, 4)[:, 0].astype(np.float64)
    ok = (F[:, 0] != F[:, 1]) & (F[:, 1] != F[:, 2]) & (F[:, 0] != F[:, 2])
    return V, F[ok], C[ok], ao


def simplified(name, V, F, C, n, prune):
    """a new object: the mesh brought down to about n triangles"""
    if prune and len(F) > n * 10: F, C = keep_largest(V, F, C, n * 10)
    V2, F2 = compact(V, F) if len(F) else (V[:0], F); o = mk_obj(name, V2, F2, C); nt = len(o.data.polygons)
    if nt > n:
        m = o.modifiers.new('d', 'DECIMATE'); m.ratio = max(n / nt, 1e-4); m.use_collapse_triangulate = True
        crlib.active(o); bpy.ops.object.modifier_apply(modifier='d')
    if prune and len(o.data.polygons) > n * 1.08:
        V3, F3, C3, _ = read_obj(o); F3, C3 = keep_largest(V3, F3, C3, n); V3, F3 = compact(V3, F3); used = o['cls']; bpy.data.objects.remove(o); o = mk_obj(name, V3, F3, C3)
    return o


class Ref:
    """the original surface of one group: answers 'what is the model's own normal here?' and 'how far is this from the original?'"""

    def __init__(self, P, N):
        self.P = P; self.N = N; self.fn, _ = fnormal(P)
        self.bvh = BVHTree.FromPolygons(P.reshape(-1, 3).tolist(), np.arange(len(P) * 3).reshape(-1, 3).tolist()) if len(P) else None

    def near(self, V, F, far):
        """triangles that stay within `far` of the original (their middle and their corners)"""
        if self.bvh is None or not len(F): return np.ones(len(F), bool)
        find = self.bvh.find_nearest
        dv = np.array([(find(p)[3] or 0) for p in V.tolist()]); dc = np.array([(find(p)[3] or 0) for p in V[F].mean(1).tolist()])
        return (dc <= far) & (dv[F].max(1) <= far * 1.3)

    def normals(self, V, F, reach=.12):
        tri = V[F]; fn, _ = fnormal(tri); n = len(F)
        if self.bvh is None or not n: return np.repeat(fn[:, None, :], 3, 1), np.ones((n, 3), bool)
        pts = tri + (tri.mean(1)[:, None, :] - tri) * .1             # a little inside the triangle, so a hard edge picks its own side
        idx = np.zeros((n, 3), np.int64); loc = np.zeros((n, 3, 3)); bad = np.zeros((n, 3), bool)
        sfn = self.fn; find = self.bvh.find_nearest; rng = self.bvh.find_nearest_range; pl = pts.tolist()
        for f in range(n):
            nf = fn[f]
            for c in range(3):
                p = pl[f][c]; h = find(p)
                if h[0] is None: bad[f, c] = True; continue
                i = h[2]; co = h[0]
                if sfn[i] @ nf < .3:                                 # the nearest surface faces another way (an inner skin): look for one that agrees
                    best = -9
                    for co2, _, j, d in rng(p, reach):
                        sc = sfn[j] @ nf - d / reach * .5
                        if sc > best: best = sc; i = j; co = co2
                    if best < .2: bad[f, c] = True; continue
                idx[f, c] = i; loc[f, c] = co
        A = self.P[idx]; a = A[..., 0, :]; v0 = A[..., 1, :] - a; v1 = A[..., 2, :] - a; v2 = loc - a
        d00 = (v0 * v0).sum(-1); d01 = (v0 * v1).sum(-1); d11 = (v1 * v1).sum(-1); d20 = (v2 * v0).sum(-1); d21 = (v2 * v1).sum(-1)
        den = d00 * d11 - d01 * d01; den = np.where(np.abs(den) < 1e-30, 1e-30, den)
        w1 = np.clip((d11 * d20 - d01 * d21) / den, 0, 1); w2 = np.clip((d00 * d21 - d01 * d20) / den, 0, 1); w0 = np.clip(1 - w1 - w2, 0, 1)
        NN = self.N[idx]; out = NN[..., 0, :] * w0[..., None] + NN[..., 1, :] * w1[..., None] + NN[..., 2, :] * w2[..., None]
        ln = np.linalg.norm(out, axis=-1); out = out / np.maximum(ln, 1e-12)[..., None]
        bad |= (ln < 1e-6) | ((out * fn[:, None, :]).sum(-1) < .15)
        out[bad] = np.repeat(fn[:, None, :], 3, 1)[bad]
        return out, bad


def bake(objs, show, lift=.18):
    """soft shadow into each object's vertices, with only `show` in the scene"""
    for o in bpy.context.scene.objects: o.hide_render = o not in show
    objs = [o for o in objs if len(o.data.polygons)]
    crlib.bake_ao(objs, samples=40)
    for o in objs:
        crlib.soften_ao(o, blur=1, lift=0)
        me = o.data; n = len(me.vertices); c = np.empty(n * 4, np.float32); me.color_attributes['Col'].data.foreach_get('color', c); c = c.reshape(-1, 4)
        v = lift + (1 - lift) * np.clip(c[:, 0] * 1.15, 0, 1); c[:, 0] = c[:, 1] = c[:, 2] = v; me.color_attributes['Col'].data.foreach_set('color', c.ravel())


def to_game(A): return np.stack([-A[..., 1], A[..., 2], -A[..., 0]], -1)


def pack_group(parts):
    """parts: [(V, F, C per triangle, ao per vertex, normals per corner)] -> the bytes of one group, vertex count, index count"""
    pos = np.concatenate([V[F].reshape(-1, 3) for V, F, C, ao, N in parts]); nrm = np.concatenate([N.reshape(-1, 3) for V, F, C, ao, N in parts])
    cls = np.concatenate([np.repeat(C, 3) for V, F, C, ao, N in parts]); aoc = np.concatenate([ao[F].ravel() for V, F, C, ao, N in parts])
    rows = np.concatenate([np.round(to_game(pos) * 1000), np.round(np.clip(to_game(nrm), -1, 1) * 127), cls[:, None], np.round(np.clip(aoc, 0, 1) * 255)[:, None]], 1).astype(np.int32)
    assert np.abs(rows[:, :3]).max() < 32767
    u, inv = np.unique(rows, axis=0, return_inverse=True); idx = inv.reshape(-1, 3)
    idx = idx[(idx[:, 0] != idx[:, 1]) & (idx[:, 1] != idx[:, 2]) & (idx[:, 0] != idx[:, 2])]
    assert len(u) <= 65535, f'{len(u)} vertices in one group: over the 16-bit index limit'
    b = u[:, :3].astype('<i2').tobytes() + u[:, 3:6].astype(np.int8).tobytes() + u[:, 6].astype(np.uint8).tobytes() + u[:, 7].astype(np.uint8).tobytes()
    return b, len(u), idx.astype('<u2').tobytes(), int(idx.size)


def render(objs, path, views, size=(1280, 760)):
    s = bpy.context.scene
    for o in s.objects: o.hide_render = o not in objs
    bpy.ops.mesh.primitive_plane_add(size=120, location=(0, 0, -.01)); fl = bpy.context.object; fl.data.materials.append(crlib.mat('_floor', (.5, .5, .5), .6))
    w = bpy.data.worlds.get('w') or bpy.data.worlds.new('w'); s.world = w
    try: w.use_nodes = True
    except Exception: pass
    bg = w.node_tree.nodes['Background']; bg.inputs[0].default_value = (.8, .86, .95, 1); bg.inputs[1].default_value = .8
    sun = bpy.data.lights.new('sun', 'SUN'); sun.energy = 3.5; sun.angle = math.radians(3); so = bpy.data.objects.new('sun', sun); s.collection.objects.link(so); so.rotation_euler = (math.radians(50), 0, math.radians(-30))
    cam = bpy.data.cameras.new('cam'); cam.lens = 60; co = bpy.data.objects.new('cam', cam); s.collection.objects.link(co); s.camera = co
    s.render.resolution_x, s.render.resolution_y = size; s.cycles.samples = 40; s.cycles.use_denoising = True
    try: s.view_settings.view_transform = 'Standard'
    except Exception: pass
    for i, (az, el, d) in enumerate(views):
        a = math.radians(az); e = math.radians(el); ctr = Vector((0, 0, 1.3))
        co.location = ctr + Vector((math.sin(a) * math.cos(e) * d, -math.cos(a) * math.cos(e) * d, math.sin(e) * d))
        co.rotation_euler = (ctr - co.location).to_track_quat('-Z', 'Y').to_euler()
        s.render.filepath = f'{path}{i}.png'; bpy.ops.render.render(write_still=True)
    for x in (fl, so, co): bpy.data.objects.remove(x)


# ---------------------------------------------------------------- the conversion
def convert(cid, fast=False):
    cfg = CARS[cid]; os.makedirs(f'{OUT}/{cid}', exist_ok=True)
    soups = read_scene(f'{IN}/{cfg["src"]}'); log('read', len(soups), 'material/object groups,', sum(len(v[0]) for v in soups.values()), 'triangles')
    # --- what each material becomes
    tg = {k: target_of(k, cfg['rules']) for k in soups}
    for k in sorted(soups):
        if tg[k] is None: log('  NO RULE for', k, len(soups[k][0]), 'tris -> dark'); tg[k] = 'dark'
    # --- the car's frame: sized and centred from the paint and the tyres
    ref = np.concatenate([soups[k][0].reshape(-1, 3) for k in soups if tg[k] in ('paint', 'wheel:rubber', 'wheel:auto')])
    tyr = np.concatenate([soups[k][0].reshape(-1, 3) for k in soups if tg[k] in ('wheel:rubber', 'wheel:auto')])
    lo, hi = ref.min(0), ref.max(0); s = LEN * cfg.get('len', 1) / (hi[1] - lo[1]); sg = -cfg.get('front', -1)
    org = np.array([(tyr[:, 0].min() + tyr[:, 0].max()) / 2, (lo[1] + hi[1]) / 2, tyr[:, 2].min()]); mul = np.array([sg, sg, 1.0])
    log('source size', np.round(hi - lo, 3), 'scale', round(s, 4))
    G = {}                                                           # group -> lists of P, N, class
    def put(g, c, P, N):
        if len(P): G.setdefault(g, []).append((P, N, np.full(len(P), CLS.index(c), np.int32)))
    rep = []
    for k, (P, N, U) in soups.items():
        P = (P - org) * s * mul; N = N * mul; t = tg[k]; cen = P.mean(1)
        if callable(t): t = t(cen, U)
        tt = np.array([t] * len(P)) if isinstance(t, str) else np.asarray(t)
        for u in np.unique(tt):
            m = tt == u; rep.append((k, u, int(m.sum()), np.round(cen[m].min(0), 1).tolist(), np.round(cen[m].max(0), 1).tolist()))
            if u == 'drop': continue
            if u in ('paint', 'glass', 'tail', 'light'): put(u, u, P[m], N[m])
            elif u.startswith('int:'): put('int', u[4:], P[m], N[m])
            elif u == 'wheel:auto': put('wheelparts', 'stripe', P[m], N[m])     # tyre and rim in one material ('stripe' only marks it here)
            elif u.startswith('wheel:'): put('wheelparts', u[6:], P[m], N[m])
            else: put('vc', u, P[m], N[m])
    with open(f'{OUT}/{cid}/rules.txt', 'w') as f:
        for k, u, n, a, b in sorted(rep, key=lambda r: (r[1], -r[2])): f.write(f'{u:14s} {n:7d}  {k:60s} {a} .. {b}\n')
    # --- the wheels: found from the tyres, everything inside each tyre's cylinder belongs to it
    wp = G.pop('wheelparts'); WP = np.concatenate([a for a, _, _ in wp]); WN = np.concatenate([b for _, b, _ in wp]); WC = np.concatenate([c for _, _, c in wp])
    AUTO = CLS.index('stripe'); auto = WC == AUTO; WC = np.where(auto, CLS.index(cfg.get('rim', 'rim')), WC)
    cen = WP.mean(1); rub = (WC == RUB) | auto; ymid = (cen[rub, 1].min() + cen[rub, 1].max()) / 2; wheels = []; taken = np.zeros(len(WP), bool)
    for front in (0, 1):
        for side in (1, -1):                                          # side: the sign of the game's z (= -x here)
            k = rub & ((cen[:, 1] < ymid) == bool(front)) & (np.sign(-cen[:, 0]) == side); pts = WP[k].reshape(-1, 3); l2, h2 = pts.min(0), pts.max(0)
            c = (l2 + h2) / 2; r = (h2[2] - l2[2]) / 2; hw = (h2[0] - l2[0]) / 2; rin = float(np.hypot(pts[:, 1] - c[1], pts[:, 2] - c[2]).min())
            inside = (np.hypot(cen[:, 1] - c[1], cen[:, 2] - c[2]) < r * 1.03) & (np.abs(cen[:, 0] - c[0]) < hw + .4 * r) & ~taken
            if (k & auto).any():                                    # no tyre material: the tyre is whatever lies beyond the rim's radius
                rin = r * cfg.get('rim_ratio', .72); tyre_part = inside & auto & (np.hypot(cen[:, 1] - c[1], cen[:, 2] - c[2]) > rin * .985)
            else: tyre_part = inside & rub
            taken |= inside; part = inside & ~tyre_part
            wheels.append(dict(c=c, r=float(r), rin=rin, hw=float(hw), f=front, P=WP[part], N=WN[part], C=WC[part]))
    ground = min(w['c'][2] - w['r'] for w in wheels)
    left = ~taken & ~(WC == RUB) & ~auto
    if left.any():                                                    # wheel-coloured parts that are not on a wheel stay with the body
        G.setdefault('vc', []).append((WP[left], WN[left], WC[left])); log('  wheel materials left on the body:', int(left.sum()), 'tris')
    for w in wheels: log('  wheel', 'front' if w['f'] else 'rear', np.round(w['c'], 3), 'r %.3f rin %.3f half width %.3f' % (w['r'], w['rin'], w['hw']), len(w['P']), 'tris')
    # --- the full-detail meshes and the reference surfaces for normals
    hi = {}; refs = {}
    small = dict(vc=cfg.get('small', .07), int=cfg.get('small_int', .3), wheel=.03)
    body = [g for g in ('paint', 'vc', 'int', 'glass', 'tail', 'light') if g in G]; wh = [f'w{i}' for i in range(4)]
    for g in body:
        P = np.concatenate([a for a, _, _ in G[g]]); N = np.concatenate([b for _, b, _ in G[g]]); C = np.concatenate([c for _, _, c in G[g]])
        P[..., 2] -= ground
        V, F, C2 = weld(P, C); n0 = len(F); F, C2 = drop_small(V, F, C2, small.get(g, 0))
        hi[g] = (V, F, C2); refs[g] = Ref(P, N); log('  group', g, len(P), 'tris ->', len(F), 'after welding and clearing small parts')
    for i, w in enumerate(wheels):
        w['P'][..., 2] -= ground; w['c'][2] -= ground
        V, F, C2 = weld(w['P'], w['C']); F, C2 = drop_small(V, F, C2, small['wheel'])
        hi[f'w{i}'] = (V, F, C2); refs[f'w{i}'] = Ref(w['P'], w['N'])
    log('references built')
    # --- the simplified versions
    prune = lambda g: g in ('vc', 'int') or g[0] == 'w'
    base = {g: simplified('b_' + g, *hi[g], BASE['wheel' if g[0] == 'w' else g], prune(g)) for g in body + wh}; log('base simplified')
    hq = {} if fast else {g: simplified('h_' + g, *hi[g], HQ[g], prune(g)) for g in body}; log('high quality simplified')
    tyres = [lathe_tyre(w['c'], w['r'], w['rin'], w['hw']) for w in wheels]
    tyo = [mk_obj(f'tyre{i}', t[0], t[1], t[2], t[3], t[4]) for i, t in enumerate(tyres)]
    bpy.ops.mesh.primitive_plane_add(size=80, location=(0, 0, -.02)); floor = bpy.context.object
    wobj = [base[w] for w in wh]
    shade = lambda d: [d[g] for g in d if g in ('paint', 'vc', 'int')]
    bake(shade(base), [o for g, o in base.items() if g != 'glass'] + tyo + [floor]); log('base shaded')
    for w, t in zip(wobj, tyo): bake([w], [w, t], lift=.3)
    if hq: bake(shade(hq), [o for g, o in hq.items() if g != 'glass'] + wobj + tyo + [floor]); log('high quality shaded')
    bpy.data.objects.remove(floor)
    # --- read back, drop strays, give every corner the original model's normal
    def finish(d):
        res = {}
        for g, o in d.items():
            V, F, C, ao = read_obj(o); n0 = len(F)
            if g != 'paint': k = refs[g].near(V, F, .16); F = F[k]; C = C[k]
            N, bad = refs[g].normals(V, F); N = unify(F, N, bad)
            res[g] = (V, F, C, ao, N); log(f'    {o.name}: {len(F)} tris ({n0 - len(F)} strays dropped), {bad.mean() * 100:.1f}% corners without a normal of their own')
        return res
    Bd = finish(base); Hd = finish(hq)
    if 'int' in hi and cfg.get('tub', True):
        iV = hi['int'][0][np.unique(hi['int'][1])]; gV = hi['glass'][0][np.unique(hi['glass'][1])] if 'glass' in hi else iV
        side = gV[np.abs(gV[:, 0]) > np.abs(gV[:, 0]).max() * .8]; fw_ = [w for w in wheels if w['f']]; rw_ = [w for w in wheels if not w['f']]
        tx = min(.8 * np.abs(gV[:, 0]).max(), .92 * np.abs(iV[:, 0]).max()); ty0 = max(iV[:, 1].min(), fw_[0]['c'][1] + fw_[0]['r'] + .15); ty1 = min(iV[:, 1].max(), rw_[0]['c'][1] - rw_[0]['r'] - .15)
        tz0 = max(iV[:, 2].min() + .05, .32); tz1 = max(side[:, 2].min() - .15, tz0 + .4)
        t = cfg.get('tub') if isinstance(cfg.get('tub'), (list, tuple)) else (tx, ty0, ty1, tz0, tz1)
        if t[2] - t[1] > 1:
            Bd['tub'] = tub(*t); log('  cabin tub: half width %.2f, y %.2f..%.2f, z %.2f..%.2f' % tuple(t))
            if Hd: Hd['tub'] = Bd['tub']
    Ld = {}
    for g in body:
        if g == 'int': continue
        V, F, C, ao, _ = Bd[g]
        if not len(F): continue
        # Blender's simplifier first (it keeps the shape far better); it stops early on meshes full of open edges, and only
        # if it stops far short of the budget is the mesh snapped to a grid instead
        o = simplified('l_' + g, V, F, C, LOD[g], g != 'paint'); Vc, Fc, Cc, _ = read_obj(o); bpy.data.objects.remove(o)
        if len(Fc) > LOD[g] * 3.5: log(f'    far {g}: the simplifier stopped at {len(Fc)}, snapping to a grid instead'); Vc, Fc, Cc = cluster(Vc, Fc, Cc, int(LOD[g] * 1.6))
        k = refs[g].near(Vc, Fc, .3); Fc = Fc[k]; Cc = Cc[k]
        if not len(Fc): continue
        Vc, Fc = compact(Vc, Fc)
        bV = V[np.unique(F)]; bao = ao[np.unique(F)]; aoc = np.array([bao[np.argmin(((bV - v) ** 2).sum(1))] for v in Vc])
        N, bad = refs[g].normals(Vc, Fc, reach=.4); Ld[g] = (Vc, Fc, Cc, aoc, unify(Fc, N, bad)); log(f'    far {g}: {len(Fc)} tris')
    log('normals transferred')
    # --- pack
    def pack(sets):
        blob = bytearray(); meta = []
        for name, parts in sets:
            parts = [p for p in parts if len(p[1])]
            if not parts: continue
            vb, v, ib, i = pack_group(parts); blob += vb
            if len(blob) % 2: blob += b'\0'
            blob += ib
            while len(blob) % 4: blob += b'\0'
            meta.append({'n': name, 'v': v, 'i': i})
        return meta, bytes(blob)
    def body_sets(D, pre):
        vcp = [D[g] for g in ('vc', 'int', 'tub') if g in D]
        return [(pre + 'vc', vcp)] + [(pre + g, [D[g]]) for g in ('glass', 'tail', 'light', 'paint') if g in D]
    wsets = []
    for i, w in enumerate(wheels):
        V, F, C, ao, N = Bd[f'w{i}']; tV, tF, tC, tao, tN = tyres[i]; wsets.append((f'w{i}', [(V - w['c'], F, C, ao, N), (tV - w['c'], tF, tC, tao, tN)]))
    gw = [dict(c=[round(float(x), 3) for x in to_game(w['c'])], r=round(w['r'], 3), f=w['f']) for w in wheels]
    meta, blob = pack(body_sets(Bd, 'b_') + body_sets(Ld, 'l_') + wsets)
    res = {'id': cid, 'pack': {'h': {'meta': meta, 'wheels': gw}, 'd': base64.b64encode(blob).decode()}}
    log('pack', len(blob) // 1024, 'KB:', ' '.join(f"{m['n']}:{m['v']}/{m['i'] // 3}" for m in meta))
    if Hd:
        meta, blob = pack(body_sets(Hd, 'b_')); res['hq'] = {'h': {'meta': meta, 'wheels': gw}, 'd': base64.b64encode(blob).decode()}
        log('high quality pack', len(blob) // 1024, 'KB:', ' '.join(f"{m['n']}:{m['v']}/{m['i'] // 3}" for m in meta))
    # --- measurements for the car's definition in the game (game axes: x forward, y up, z to the right)
    info = {'wheels': gw}
    for g in ('paint', 'glass', 'tail', 'light', 'vc', 'int', 'tub'):
        if g in Bd and len(Bd[g][1]):
            X = to_game(Bd[g][0][np.unique(Bd[g][1])]); info[g] = [[round(float(v), 2) for v in X.min(0)], [round(float(v), 2) for v in X.max(0)]]
    if 'glass' in Bd and len(Bd['glass'][1]):
        X = to_game(Bd['glass'][0][np.unique(Bd['glass'][1])]); side = X[np.abs(X[:, 2]) > np.abs(X[:, 2]).max() * .8]
        info['glass_side_y'] = [round(float(side[:, 1].min()), 2), round(float(side[:, 1].max()), 2)]
    res['info'] = info; log('info', json.dumps(info))
    json.dump(res, open(f'{OUT}/{cid}/{cid}.json', 'w'))
    # --- pictures of exactly what was packed
    for o in list(base.values()) + list(hq.values()): bpy.data.objects.remove(o)
    show = lambda D, tag: [mk_obj(f'{tag}_{g}', *D[g]) for g in D if len(D[g][1])]
    fb = show(Bd, 'fb'); render(fb + tyo, f'{OUT}/{cid}/{cid}_check', [(-35, 16, 26), (145, 18, 26), (-90, 4, 24), (0, 88, 30)])
    fw = [o for o in fb if o.name.startswith('fb_w')]
    if Hd: render(show(Hd, 'fh') + fw + tyo, f'{OUT}/{cid}/{cid}_hq', [(-35, 16, 26), (-90, 4, 24)])
    render(show(Ld, 'fl') + fw + tyo, f'{OUT}/{cid}/{cid}_far', [(-35, 16, 26)])
    log('done')


if __name__ == '__main__':
    a = sys.argv[sys.argv.index('--') + 1:]
    convert(a[0], fast='fast' in a)
