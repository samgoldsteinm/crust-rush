#!/usr/bin/env python3
"""Neon cup track generator: lays each track out from straights and arcs (turtle style), with a road height per
segment, and writes the centre line (16 units apart), the heights for both driving directions and the feature
positions (boost pads, ramps, item boxes, glide, shortcuts) for the web game's MAPS table.

  python3 gen.py plot      -> neon/<id>.png for every track (top view, coloured by height)
  python3 gen.py js        -> neon/tracks.js (the MAPS entries)
"""
import math, sys, json
import numpy as np

STEP = 4.0      # fine sampling
OUT = 16.0      # spacing of the exported points
WALLD = 93.0
CROSS_DH = 62.0   # least height between two roads that cross


class Track:
    def __init__(self, id, name, **meta):
        self.id, self.name, self.meta = id, name, meta
        self.segs = []      # dicts: kind S/A, L or (R, deg), h, hR, tag
        self.feat = []      # (kind, seg index, fraction, extra)
        self.center = True  # move the lap so its bounding box sits round the origin
        self.walld = WALLD; self.cross_dh = CROSS_DH; self.origin = (0.0, 0.0, 0.0)

    def S(self, L, h=None, hR=None, tag=None):
        self.segs.append(dict(k='S', L=L, h=h, hR=hR, tag=tag)); return len(self.segs) - 1

    def A(self, R, deg, h=None, hR=None, tag=None):
        self.segs.append(dict(k='A', R=R, deg=deg, h=h, hR=hR, tag=tag)); return len(self.segs) - 1

    def pad(self, seg, f, lat=0, w=None): self.feat.append(('pad', seg, f, dict(lat=lat, w=w)))
    def ramp(self, seg, f): self.feat.append(('ramp', seg, f, {}))
    def box(self, seg, f): self.feat.append(('box', seg, f, {}))
    def glide_rev(self, seg, f, L): self.feat.append(('glideR', seg, f, dict(L=L)))
    def short(self, sa, fa, sb, fb, side, **kw): self.feat.append(('short', sa, fa, dict(sb=sb, fb=fb, side=side, **kw)))

    # ---- geometry ----
    def build(self, close=None):
        """close: (i, j) indices of two straights whose lengths are solved so the loop closes."""
        if close:
            self._solve(close)
        pts = []; x, y, a = self.origin; s = 0.0
        bounds = []
        hprev = self.segs[-1]['h'] or 0.0
        hRprev = self.segs[-1]['hR'] if self.segs[-1]['hR'] is not None else hprev
        for sg in self.segs:
            L = sg['L'] if sg['k'] == 'S' else abs(math.radians(sg['deg'])) * sg['R']
            n = max(1, int(round(L / STEP)))
            h1 = hprev if sg['h'] is None else sg['h']
            hR1 = sg['hR'] if sg['hR'] is not None else h1
            sg['_h0'], sg['_h1'], sg['_hR0'], sg['_hR1'] = hprev, h1, hRprev, hR1
            sg['_s0'], sg['_L'] = s, L
            for i in range(n):
                t = i / n
                e = t * t * (3 - 2 * t)
                if sg['k'] == 'S':
                    px, py, pa = x + math.cos(a) * L * t, y + math.sin(a) * L * t, a
                else:
                    sgn = 1 if sg['deg'] > 0 else -1
                    cx, cy = x - math.sin(a) * sg['R'] * sgn, y + math.cos(a) * sg['R'] * sgn
                    th = math.radians(sg['deg']) * t
                    px = cx + math.sin(a + th) * sg['R'] * sgn
                    py = cy - math.cos(a + th) * sg['R'] * sgn
                    pa = a + th
                pts.append((px, py, pa, s + L * t, hprev + (h1 - hprev) * e, hRprev + (hR1 - hRprev) * e, len(bounds)))
            if sg['k'] == 'S':
                x, y = x + math.cos(a) * L, y + math.sin(a) * L
            else:
                sgn = 1 if sg['deg'] > 0 else -1
                cx, cy = x - math.sin(a) * sg['R'] * sgn, y + math.cos(a) * sg['R'] * sgn
                a += math.radians(sg['deg'])
                x, y = cx + math.sin(a) * sg['R'] * sgn, cy - math.cos(a) * sg['R'] * sgn
            s += L; hprev = h1; hRprev = hR1
            bounds.append(s)
        self.end = (x, y, a)
        self.P = np.array(pts)
        self.L = s
        return self

    def _end(self):
        x, y, a = self.origin
        for sg in self.segs:
            if sg['k'] == 'S':
                x += math.cos(a) * sg['L']; y += math.sin(a) * sg['L']
            else:
                sgn = 1 if sg['deg'] > 0 else -1
                cx, cy = x - math.sin(a) * sg['R'] * sgn, y + math.cos(a) * sg['R'] * sgn
                a += math.radians(sg['deg'])
                x, y = cx + math.sin(a) * sg['R'] * sgn, cy - math.cos(a) * sg['R'] * sgn
        return x, y, a

    def _solve(self, close):
        i, j = close
        tot = sum(sg['deg'] for sg in self.segs if sg['k'] == 'A')
        assert abs(tot % 360) < 1e-6 or abs(tot % 360 - 360) < 1e-6, 'arc angles sum to %s' % tot
        for it in range(6):
            x0, y0, _ = self._end()
            self.segs[i]['L'] += 1; x1, y1, _ = self._end(); self.segs[i]['L'] -= 1
            self.segs[j]['L'] += 1; x2, y2, _ = self._end(); self.segs[j]['L'] -= 1
            M = np.array([[x1 - x0, x2 - x0], [y1 - y0, y2 - y0]])
            d = np.linalg.solve(M, [self.origin[0] - x0, self.origin[1] - y0])
            self.segs[i]['L'] += d[0]; self.segs[j]['L'] += d[1]
        x0, y0, a0 = self._end()
        assert abs(x0 - self.origin[0]) < 1e-3 and abs(y0 - self.origin[1]) < 1e-3, (x0, y0)
        assert self.segs[i]['L'] > 60 and self.segs[j]['L'] > 60, ('closing straights too short', self.segs[i]['L'], self.segs[j]['L'])

    # ---- checks ----
    def check(self):
        P = self.P; n = len(P); out = []
        # centre the track
        cx, cy = (P[:, 0].max() + P[:, 0].min()) / 2, (P[:, 1].max() + P[:, 1].min()) / 2
        if self.center:
            P[:, 0] -= cx; P[:, 1] -= cy
        self.rad = float(np.hypot(P[:, 0], P[:, 1]).max())
        gap = int(getattr(self, 'gap', 420) / STEP)
        cross = []
        idx = np.arange(0, n, 3)
        X, Y, H, HR = P[idx, 0], P[idx, 1], P[idx, 4], P[idx, 5]
        for ai, i in enumerate(idx):
            d2 = (X - X[ai]) ** 2 + (Y - Y[ai]) ** 2
            near = np.where(d2 < (2 * self.walld + 34) ** 2)[0]
            for bj in near:
                j = idx[bj]
                dj = abs(j - i); dj = min(dj, n - dj)
                if dj < gap or j < i:
                    continue
                dh, dhr = abs(H[ai] - H[bj]), abs(HR[ai] - HR[bj])
                cross.append((i, j, math.sqrt(d2[bj]), dh, dhr))
        bad = [c for c in cross if c[3] < self.cross_dh or c[4] < self.cross_dh]
        # slope
        ds = np.diff(P[:, 3]); sl = np.abs(np.diff(P[:, 4])) / ds; slr = np.abs(np.diff(P[:, 5])) / ds
        out.append('%s: L=%.0f pts=%d radius=%.0f maxslope=%.2f/%.2f crossings=%d bad=%d' % (self.id, self.L, round(self.L / OUT), self.rad, sl.max(), slr.max(), len(cross), len(bad)))
        if bad:
            seen = set()
            for c in bad:
                key = (int(P[c[0], 6]), int(P[c[1], 6]))
                if key in seen: continue
                seen.add(key)
                out.append('   too close: seg %d (s=%.0f h=%.0f/%.0f) and seg %d (s=%.0f h=%.0f/%.0f) d=%.0f' % (key[0], P[c[0], 3], P[c[0], 4], P[c[0], 5], key[1], P[c[1], 3], P[c[1], 4], P[c[1], 5], c[2]))
        self.cross = cross
        return '\n'.join(out)

    def arc_center(self, seg):
        sg = self.segs[seg]; P = self.P
        i = int(np.searchsorted(P[:, 3], sg['_s0'])); x, y, a = P[i, 0], P[i, 1], P[i, 2]
        sgn = 1 if sg['deg'] > 0 else -1
        return (x - math.sin(a) * sg['R'] * sgn, y + math.cos(a) * sg['R'] * sgn)

    def frac(self, seg, f):
        sg = self.segs[seg]
        return ((sg['_s0'] + sg['_L'] * f) % self.L) / self.L

    def plot(self, path):
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        from matplotlib.collections import LineCollection
        P = self.P
        fig, axs = plt.subplots(1, 2, figsize=(22, 11))
        for ax, col, ttl in ((axs[0], 4, 'forward'), (axs[1], 5, 'reverse')):
            pts = P[:, :2].reshape(-1, 1, 2)
            segs = np.concatenate([pts[:-1], pts[1:]], axis=1)
            lc = LineCollection(segs, cmap='plasma', linewidths=7)
            lc.set_array(P[:-1, col]); lc.set_clim(0, 200)
            ax.add_collection(lc)
            ax.set_aspect('equal'); ax.set_facecolor('#111')
            R = self.rad + 200
            ax.set_xlim(-R, R); ax.set_ylim(-R, R)
            ax.add_patch(plt.Circle((0, 0), self.rad + 208, fill=False, color='#3ff0ff'))
            for k, sg in enumerate(self.segs):
                i = np.searchsorted(P[:, 3], sg['_s0'] + sg['_L'] * 0.5)
                i = min(i, len(P) - 1)
                ax.text(P[i, 0], P[i, 1], '%d%s' % (k, (':' + sg['tag']) if sg['tag'] else ''), color='w', fontsize=9, ha='center', va='center', bbox=dict(facecolor='#000', alpha=.6, pad=1))
            ax.plot([P[0, 0]], [P[0, 1]], 'o', color='#fff', ms=12)
            ax.arrow(P[0, 0], P[0, 1], math.cos(P[0, 2]) * 250, math.sin(P[0, 2]) * 250, color='#fff', width=14)
            for kind, seg, f, ex in self.feat:
                fr = self.frac(seg, f); i = min(len(P) - 1, int(fr * len(P)))
                mk = dict(pad='^', ramp='s', box='D', short='*', glideR='P')[kind]
                cc = dict(pad='#ff0', ramp='#0f0', box='#f8f', short='#0ff', glideR='#fff')[kind]
                ax.plot([P[i, 0]], [P[i, 1]], mk, color=cc, ms=9)
                if kind == 'short':
                    fr2 = self.frac(ex['sb'], ex['fb']); i2 = min(len(P) - 1, int(fr2 * len(P)))
                    ax.plot([P[i, 0], P[i2, 0]], [P[i, 1], P[i2, 1]], '--', color='#0ff')
            ax.set_title('%s  %s  L=%.0f' % (self.name, ttl, self.L))
        fig.colorbar(lc, ax=axs, shrink=.6, label='height')
        fig.savefig(path, dpi=55, bbox_inches='tight')
        plt.close(fig)

    # ---- export ----
    def export(self):
        P = self.P
        n = int(round(self.L / OUT))
        s = np.arange(n) * self.L / n
        x = np.interp(s, P[:, 3], P[:, 0]); y = np.interp(s, P[:, 3], P[:, 1])
        h = np.interp(s, P[:, 3], P[:, 4]); hr = np.interp(s, P[:, 3], P[:, 5])
        ctrl = [[round(float(a), 1), round(float(-b), 1)] for a, b in zip(x, y)]   # game y runs the other way
        R = int(math.ceil((self.rad + 210) / 10) * 10)
        d = dict(id=self.id, name=self.name, theme='night', R=R, exact=1, arena=1, neon=1)
        d.update(self.meta)
        if hasattr(self, 'holo_seg'):
            c = self.arc_center(self.holo_seg); d['holoC'] = [round(float(c[0]), 1), round(float(-c[1]), 1)]
        d['ctrl'] = ctrl
        d['elev'] = [round(float(v), 2) for v in h]
        # the reverse lap keeps point 0 and runs the rest backwards (buildTrack), its heights are read the same way
        d['elevR'] = [round(float(v), 2) for v in hr]
        pads, ramps, boxes, shorts = [], [], [], []
        for kind, seg, f, ex in self.feat:
            fr = round(self.frac(seg, f), 4)
            if kind == 'pad': pads.append([fr, ex['lat']] + ([ex['w']] if ex['w'] else []))
            elif kind == 'ramp': ramps.append(fr)
            elif kind == 'box': boxes.append(fr)
            elif kind == 'glideR': d['nglideR'] = [round(self.frac(seg, f), 5), ex['L']]
            elif kind == 'short':
                e = dict(a=fr, b=round(self.frac(ex['sb'], ex['fb']), 4), s=ex['side'])
                for k in ex:
                    if k not in ('sb', 'fb', 'side'): e[k] = ex[k]
                shorts.append(e)
        d['boxes'] = boxes; d['npads'] = pads; d['nramps'] = ramps; d['nshorts'] = shorts
        for sg in self.segs:
            if sg['tag'] == 'glide':
                d['nglide'] = [round(sg['_s0'] / self.L, 5), round(sg['_L'], 1)]
        return d


TRACK_MODULES = ('t_laser', 't_holo', 't_synth')


def tracks():
    out = []
    import importlib
    for m in TRACK_MODULES:
        try:
            mod = importlib.import_module(m)
        except ModuleNotFoundError:
            continue
        out.append(mod.make())
    return out


if __name__ == '__main__':
    sys.path.insert(0, '/home/claude/neon')
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'plot'
    ts = tracks()
    for t in ts:
        print(t.check())
        if cmd == 'plot':
            t.plot('/home/claude/neon/%s.png' % t.id)
    if cmd == 'js':
        with open('/home/claude/neon/tracks.json', 'w') as f:
            json.dump([t.export() for t in ts], f, separators=(',', ':'))
        print('wrote tracks.json')
