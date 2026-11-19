"""The kart wheel sets' tyres (Redline, Emerald, Stealth, Forged Bronze, Turbo Fan: CAR_PACKS 'wheelset' w0..w4) rebuilt with a real tread.
    py.cmd tools/cars/tread.py      (once: it marks the packs 'tread' and refuses a second time)
The owner's uploaded wheel models were simplified long ago (before web v154; the originals are gone) and their rubber came out as blotchy
patches. Here the rubber (class 8) of each group is dropped and a new tyre of the same size goes in its place (measured from the old one):
a rounded shoulder, a slightly bulged sidewall and a performance tread with crisp groove walls: two circumferential main grooves, a thin
centre groove, angled shoulder blocks and sipes notched into the ribs. Every cell is its own flat-walled block, so the grooves are cut
straight down rather than smeared; the tops keep a round (radial) normal. The rims, spokes and calipers are untouched.
Running it again starts from the pack as it is: it is safe only once (it keeps 'tread' in the pack's header and refuses a second time).
"""
import sys, base64, math, json
import numpy as np
sys.path.insert(0, 'D:/crust-rush/source/tools'); import tables

RUB = 8
# --- the tread patterns: pitches round the tyre, groove depth (a little deeper than life, to read at game size), the tread's half width
# (of the tyre's), and the columns of the left half across the tread, as fractions of the tread's half width (the last one is the centre
# column, -x..x); the right half mirrors the left, its lateral grooves moved round by `rs` of a pitch (0: a V, .5: staggered).
# kinds: 'g' groove all round; 'r' plain rib; 'b' block, its lateral groove at phase ph, gw of the pitch wide; 's' rib with a sipe
PATTERNS = {
    'perf': dict(NP=36, D=.05, c=.80, rs=0, half=[(-1.00, -.81, 'b', .00, .30), (-.81, -.62, 'b', .10, .30), (-.62, -.49, 'g', 0, 0),
                                               (-.49, -.33, 's', .55, .10), (-.33, -.06, 'r', 0, 0), (-.06, .06, 'g', 0, 0)]),
    'touring': dict(NP=40, D=.045, c=.82, rs=.5, half=[(-1.00, -.78, 'b', .00, .22), (-.78, -.68, 'g', 0, 0), (-.68, -.42, 's', .30, .08),
                                                    (-.42, -.32, 'g', 0, 0), (-.32, -.06, 's', .80, .08), (-.06, .06, 'r', 0, 0)]),
    'arrow': dict(NP=32, D=.05, c=.82, rs=0, half=[(-1.00, -.82, 'b', .00, .28), (-.82, -.64, 'b', .08, .28), (-.64, -.46, 'b', .16, .28),
                                                (-.46, -.28, 'b', .24, .28), (-.28, -.08, 'b', .32, .28), (-.08, .08, 'r', 0, 0)]),
    'block': dict(NP=30, D=.055, c=.82, rs=.5, half=[(-1.00, -.66, 'b', .00, .25), (-.66, -.56, 'g', 0, 0), (-.56, -.08, 'b', .50, .20),
                                                  (-.08, .08, 'g', 0, 0)]),
    'semi': dict(NP=24, D=.04, c=.84, rs=.5, half=[(-1.00, -.86, 'b', .00, .18), (-.86, -.55, 'r', 0, 0), (-.55, -.47, 'g', 0, 0),
                                                (-.47, -.06, 'r', 0, 0), (-.06, .06, 'r', 0, 0)]),
    'lug': dict(NP=18, D=.13, c=.88, rs=.5, half=[(-1.00, -.52, 'b', .00, .48), (-.52, -.07, 'b', .50, .48), (-.07, .07, 'g', 0, 0)]),
}
WHEELSET = {'w0': 'perf', 'w1': 'touring', 'w2': 'arrow', 'w3': 'block', 'w4': 'semi'}   # Redline, Emerald, Stealth, Forged Bronze, Turbo Fan


def decode(p):
    b = base64.b64decode(p['d']); o = 0; out = []
    for m in p['h']['meta']:
        v, i = m['v'], m['i']
        P = np.frombuffer(b, '<i2', v * 3, o).reshape(-1, 3) / 1000; o += v * 6
        N = np.frombuffer(b, 'i1', v * 3, o).reshape(-1, 3) / 127; o += v * 3
        C = np.frombuffer(b, 'u1', v, o).astype(np.int32); o += v
        A = np.frombuffer(b, 'u1', v, o) / 255; o += v
        if o % 2: o += 1
        I = np.frombuffer(b, '<u2', i, o).reshape(-1, 3).astype(np.int64); o += i * 2
        while o % 4: o += 1
        out.append((m['n'], P, N, C, A, I))
    assert o == len(b)
    return out


def encode(groups):
    blob = bytearray(); meta = []
    for name, pos, nrm, cls, ao in groups:          # per corner (triangle soup), as pack_group in car_convert.py
        rows = np.concatenate([np.round(pos * 1000), np.round(np.clip(nrm, -1, 1) * 127), cls[:, None], np.round(np.clip(ao, 0, 1) * 255)[:, None]], 1).astype(np.int32)
        u, inv = np.unique(rows, axis=0, return_inverse=True); idx = inv.reshape(-1, 3)
        idx = idx[(idx[:, 0] != idx[:, 1]) & (idx[:, 1] != idx[:, 2]) & (idx[:, 0] != idx[:, 2])]
        assert len(u) <= 65535
        blob += u[:, :3].astype('<i2').tobytes() + u[:, 3:6].astype(np.int8).tobytes() + u[:, 6].astype(np.uint8).tobytes() + u[:, 7].astype(np.uint8).tobytes()
        if len(blob) % 2: blob += b'\0'
        blob += idx.astype('<u2').tobytes()
        while len(blob) % 4: blob += b'\0'
        meta.append({'n': name, 'v': len(u), 'i': int(idx.size)})
    return meta, base64.b64encode(bytes(blob)).decode()


class Soup:
    def __init__(s): s.P = []; s.N = []; s.A = []

    def tri(s, a, b, c, na, nb, nc, ao, want=None):
        """one triangle; turned so it faces `want` (or its corners' normals)"""
        a, b, c = map(np.asarray, (a, b, c)); fn = np.cross(b - a, c - a)
        ref = want if want is not None else (np.asarray(na) + nb + nc)
        if fn @ ref < 0: b, c, nb, nc = c, b, nc, nb
        s.P += [a, b, c]; s.N += [na, nb, nc]; s.A += ao if isinstance(ao, list) else [ao] * 3

    def quad(s, a, b, c, d, na, nb, nc, nd, ao, want=None):
        s.tri(a, b, c, na, nb, nc, ao if not isinstance(ao, list) else ao[:3], want)
        s.tri(a, c, d, na, nc, nd, ao if not isinstance(ao, list) else [ao[0], ao[2], ao[3]], want)


def tyre(R, rin, W, pat):
    """the new tyre, axle along z, centred: corners (pos, normal, ao)"""
    pa = PATTERNS[pat]; NP = pa['NP']; DEPTH = pa['D']; k = R / 1.32     # (k: the shoulder's size, the Monster's bigger)
    S = Soup(); c = pa['c'] * W                              # the tread's half width
    pt = lambda r, th, z: np.array([r * math.cos(th), r * math.sin(th), z])
    rad = lambda th: np.array([math.cos(th), math.sin(th), 0.])
    crown = lambda u: R - .012 * k * (u / c) ** 2            # a slight crown
    # --- columns across the tread (fractions of c): kind, phase of its lateral groove in the pitch, groove width in the pitch
    # 'g' groove all round; 'b' block with a lateral groove; 's' rib with a narrow sipe; 'r' plain rib
    half = pa['half']
    cols = half + [(-b, -a, kd, (ph + pa['rs']) % 1, gw) for a, b, kd, ph, gw in reversed(half[:-1])]
    def ivals(kd, ph, gw):
        """the column's intervals round the tyre: (t0, t1, low) in pitch units over 0..NP, neighbours of a kind merged"""
        if kd == 'g': return [(0., float(NP), True)]
        if kd == 'r': return [(0., float(NP), False)]
        out = []
        for p in range(NP):
            a = p + ph; b = a + gw
            if b <= p + 1: out += [(p + 0., a, False), (a, b, True), (b, p + 1., False)]
            else: out += [(p + 0., b - 1, True), (b - 1, a, False), (a, p + 1., True)]
        out = [list(x) for x in out if x[1] - x[0] > 1e-6]; m = [out[0]]
        for x in out[1:]:
            if x[2] == m[-1][2]: m[-1][1] = x[1]
            else: m.append(x)
        return [tuple(x) for x in m]
    steps = lambda t0, t1: max(1, int(math.ceil((t1 - t0) * 360 / NP / 10 - 1e-9)))   # at most 10 degrees a step (the curve)
    T = lambda t: t / NP * 2 * math.pi
    colI = [ivals(k, ph, gw) for _, _, k, ph, gw in cols]
    for (a, b, kd, ph, gw), iv in zip(cols, colI):
        u0, u1 = a * c, b * c
        for t0, t1, low in iv:
            n = steps(t0, t1)
            for j in range(n):
                th0 = T(t0 + (t1 - t0) * j / n); th1 = T(t0 + (t1 - t0) * (j + 1) / n); d = DEPTH if low else 0
                ao = .42 if low else 1.
                S.quad(pt(crown(u0) - d, th0, u0), pt(crown(u1) - d, th0, u1), pt(crown(u1) - d, th1, u1), pt(crown(u0) - d, th1, u0),
                       rad(th0), rad(th0), rad(th1), rad(th1), ao)
            if low:                                            # the groove's walls at its two ends round the tyre (lateral grooves)
                for th, sgn in ((T(t0), 1), (T(t1), -1)):
                    if kd == 'g': break
                    if iv[0][2] and iv[-1][2] and ((t0 == 0 and sgn > 0) or (t1 == NP and sgn < 0)): continue   # (a groove running on round the join: no wall)
                    tn = np.array([-math.sin(th), math.cos(th), 0.]) * sgn
                    S.quad(pt(crown(u0), th, u0), pt(crown(u1), th, u1), pt(crown(u1) - DEPTH, th, u1), pt(crown(u0) - DEPTH, th, u0), tn, tn, tn, tn, [1., 1., .5, .5], tn)
    # --- walls between neighbouring columns (and the tread's two edges against the smooth shoulder)
    def wall(u, L, Rr, nz):
        """L, R: interval lists either side of u (None: the shoulder, always high); a wall wherever exactly one side is low"""
        cuts = sorted({0., float(NP)} | {x for iv in (L or []) + (Rr or []) for x in iv[:2]})
        lowat = lambda iv, t: False if iv is None else next(l for x, y, l in iv if x <= t < y)
        for t0, t1 in zip(cuts, cuts[1:]):
            m = (t0 + t1) / 2; lo_l, lo_r = lowat(L, m), lowat(Rr, m)
            if lo_l == lo_r: continue
            face = np.array([0, 0, -nz if lo_l else nz], float)   # the wall faces the low side
            n = steps(t0, t1)
            for j in range(n):
                th0 = T(t0 + (t1 - t0) * j / n); th1 = T(t0 + (t1 - t0) * (j + 1) / n)
                S.quad(pt(crown(u), th0, u), pt(crown(u), th1, u), pt(crown(u) - DEPTH, th1, u), pt(crown(u) - DEPTH, th0, u), face, face, face, face, [1., 1., .5, .5], face)
    wall(cols[0][0] * c, None, colI[0], 1)
    for i in range(len(cols) - 1): wall(cols[i][1] * c, colI[i], colI[i + 1], 1)
    wall(cols[-1][1] * c, colI[-1], None, 1)
    # --- the shoulders and sidewalls (a smooth lathe from the tread's edge down to the bead)
    prof = [(c, crown(c)), (.92 * W, R - .025 * k), (.975 * W, R - .075 * k), (1.0 * W, R - .16 * k), (.995 * W, rin + .09), (.94 * W, rin - .01)]
    pr = np.array(prof); tan = np.gradient(pr, axis=0); pn = np.stack([tan[:, 1] * -1, tan[:, 0]], 1)   # (z, r) normal
    pn = pn / np.linalg.norm(pn, axis=1)[:, None]
    for i in range(len(pn)):                                  # outward: away from the tyre's middle and the axle
        if pn[i] @ np.array([pr[i, 0], pr[i, 1] - (R + rin) / 2]) < 0: pn[i] *= -1
    aop = [1., .96, .9, .82, .7, .58]
    seg = 36          # (the sidewall: 10 degrees a step)
    for side in (1, -1):
        for i in range(len(pr) - 1):
            for j in range(seg):
                th0 = 2 * math.pi * j / seg; th1 = 2 * math.pi * (j + 1) / seg
                P = lambda k, th: pt(pr[k, 1], th, side * pr[k, 0]); Nn = lambda k, th: rad(th) * pn[k, 1] + np.array([0, 0, side * pn[k, 0]])
                S.quad(P(i, th0), P(i + 1, th0), P(i + 1, th1), P(i, th1), Nn(i, th0), Nn(i + 1, th0), Nn(i + 1, th1), Nn(i, th1), [aop[i], aop[i + 1], aop[i + 1], aop[i]])
    pos = np.array(S.P); nrm = np.array(S.N); nrm /= np.linalg.norm(nrm, axis=1)[:, None]
    return pos, nrm, np.array(S.A)


def redo(p, pats, monster=False):
    """a pack's wheel groups with new tyres; the other groups as they are"""
    out = []
    for name, P, N, C, A, I in decode(p):
        if name not in pats:
            out.append((name, P[I].reshape(-1, 3), N[I].reshape(-1, 3), C[I].ravel(), A[I].ravel())); continue
        tc = C[I][:, 0]; cen = P[I].mean(1); rc = np.hypot(cen[:, 0], cen[:, 1])
        if monster:   # the Monster: its tyre is the rubber outside the rim's lip (the rubber dish inside stays); the old 'rim' tread blocks go
            lip = float(rc[(tc == 11) & (rc < 1.0)].max()) + .03
            rub = (tc == RUB) & (rc > lip); drop = rub | ((rc > 1.2) & (tc != RUB))
        else:
            rub = (C[I] == RUB).all(1); drop = rub; lip = None
        keep = I[~drop]; vr = np.unique(I[rub]); r = np.hypot(P[vr, 0], P[vr, 1])
        R = float(r.max()); rin = lip if monster else float(r.min()) + .005; W = float(max(-P[vr, 2].min(), P[vr, 2].max()))
        zc = float((P[vr, 2].min() + P[vr, 2].max()) / 2); base = float(np.median(A[vr]))
        tp, tn, ta = tyre(R, rin, W, pats[name]); tp[:, 2] += zc; ta = ta * base
        pos = np.concatenate([P[keep].reshape(-1, 3), tp]); nrm = np.concatenate([N[keep].reshape(-1, 3), tn])
        cls = np.concatenate([C[keep].ravel(), np.full(len(tp), RUB)]); ao = np.concatenate([A[keep].ravel(), ta])
        out.append((name, pos, nrm, cls, ao)); print(name, pats[name], 'R %.3f rin %.3f half width %.3f' % (R, rin, W), 'old', int(drop.sum()), '-> tyre', len(tp) // 3, 'tris')
    meta, d = encode(out)
    return {'h': dict(p['h'], meta=meta, tread=1), 'd': d}


def main():
    D = tables.load('CAR_PACKS')
    for k in ('wheelset', 'monster'): assert not D[k]['h'].get('tread'), k + ' already has the new tread'
    D['wheelset'] = redo(D['wheelset'], WHEELSET)
    D['monster'] = redo(D['monster'], {f'w{i}': 'lug' for i in range(4)}, monster=True)   # (its own four wheels are the Monster wheel type too)
    tables.save('CAR_PACKS', D); print('CAR_PACKS wheelset and monster written')


if __name__ == '__main__':
    main()
