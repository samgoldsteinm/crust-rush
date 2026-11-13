"""Backyard Mega Circuit: the fourth Miniature Mayhem track. A toy racing set laid right round the back garden: the garden
every room's window looks onto (tools/blender/outside.py), at its real size, 25 m long and 7 m deep.
Garden coordinates, in metres, as in outside.py: x east with the bedroom window at 0, y north from the house wall (0) to
the back fence (7). What stands where (the yard in tools/mini/mini.js, toyYard, must match):
  house wall y 0, windows: kitchen x -7, bedroom 0, garage 7.5      patio y 0..1.6
  shed (-11.2, 5.4), 2.4 x 1.9          washing line y 4.2, poles at x -8.2 and -3.4
  the close tree (3.1, 5.2)              goal: posts (8.6, 5.6) and (10.6, 5.6)
Design coordinates are those metres turned into game units and centred: G() below. Two laps: one lap is 21 000 units,
three times the other rooms' (it is as long as a Neon Cup track).
Run: py.cmd tools/mini/t_backyard.py   (adds or replaces the backyard entry in tools/mini/tracks.json, draws backyard.png)
"""
import sys, json
sys.path.insert(0, 'D:/crust-rush/source/tools/neon')
from gen import Track

TJ = 'D:/crust-rush/source/tools/mini/tracks.json'
M = 347.0                                        # game units per metre (a toy kart is 7.5 cm long)
G = lambda gx, gy: ((gx + .75) * M, (gy - 3.5) * M)


def make():
    t = Track('backyard', 'Backyard Mega Circuit', themeName='Toy track', theme='kitchen', toy=1, rw=31, laps=2, R=4700, look='backyard',
              blurb='A toy racing set laid right round the back garden: along the patio under the windows, through the goal, a spiral up the tree and a long drop, down a drainpipe, behind the shed and home under the washing line. One lap is as long as three of the others.')
    t.center = False; t.walld = 46.0; t.cross_dh = 60.0; t.gap = 260
    t.origin = (*G(0.0, .9), 0.0)                # the start line, on the patio under the bedroom window, heading east
    m = lambda v: v * M
    s0 = t.S(m(4.0), h=0)                        # east along the patio: the loop
    t.A(m(1.2), 25, h=0); t.A(m(1.2), -50, h=0); t.A(m(1.2), 25, h=0)       # round a flowerpot and a watering can
    s1 = t.S(m(1.6), h=0)
    t.A(m(1.0), 90, h=0)                         # left at the garage end: north across the lawn
    s2 = t.S(m(1.1), h=0)
    t.A(m(1.0), -40, h=0); t.A(m(1.0), 40, h=0)  # line up with the goal
    s3 = t.S(m(1.31), h=0)                       # into the goal mouth
    t.A(m(.4), 90, h=0)                          # and out of its side, under the back stay
    s4 = t.S(m(4.1), h=0)                        # west along the back fence: a jump
    t.A(m(1.5), 25, h=0); t.A(m(1.5), -25, h=0)
    s4b = t.S(m(.23), h=0)
    sp = t.A(m(.52), 360, h=260)                 # once round the tree, climbing
    s5 = t.S(m(3.2), h=0)                        # the long drop
    s6 = t.S(m(7.1), h=0)                        # the back straight: through a drainpipe
    t.A(m(1.5), -45, h=0); t.A(m(1.5), 45, h=0)  # over to the gap behind the shed
    s7 = t.S(m(3.43), h=0)                       # behind the shed
    t.A(m(.55), 90, h=0)
    s8 = t.S(m(2.05), h=0)                       # south down the side fence
    t.A(m(.55), 90, h=0)
    s9 = t.S(m(4.2), h=0)                        # east past the shed door: a jump
    t.A(m(1.2), 45, h=0); t.A(m(1.2), -45, h=0)  # between the poles
    s10 = t.S(m(2.25), h=0)                      # under the washing
    t.A(m(1.2), -45, h=0); t.A(m(1.2), 45, h=0)
    t.A(m(.6), -90, h=0)                         # right, down to the patio
    s11 = t.S(m(1.35), h=0)
    t.A(m(.6), 90, h=0)
    s12 = t.S(m(1.7), h=0)                       # to the line
    t.build(close=(s12, s11))                    # the two straights whose lengths are solved so the lap closes
    for seg, f in [(s2, .1), (s5, .9), (s6, .55), (s9, .05), (s11, .3)]:
        t.pad(seg, f, 0, 10)
    for seg, f in [(s4, .5), (s9, .6)]:
        t.ramp(seg, f)
    for seg, f in [(s1, .5), (s4, .15), (s6, .2), (s7, .5), (s10, .5)]:
        t.box(seg, f)
    t.loops = [(s0, .55, .36)]
    t.S0 = s0
    t.named = dict(s0=s0, s4=s4, sp=sp, s5=s5, s6=s6, s7=s7, s9=s9, s10=s10)
    return t


if __name__ == '__main__':
    t = make()
    print(t.check())
    t.plot('D:/crust-rush/source/tools/mini/backyard.png')
    d = t.export()
    d['tloops'] = [[round(t.frac(sg, f), 5), k] for sg, f, k in t.loops]
    for i, sg in enumerate(t.segs):
        j = int(sg['_s0'] / 4.0) % len(t.P); x, y = t.P[j][0] / M - .75, t.P[j][1] / M + 3.5
        print('seg %2d %s starts at garden (%6.2f,%5.2f) lap %.3f  h %3.0f -> %3.0f  L %5.0f' % (i, sg['k'], x, y, sg['_s0'] / t.L, sg['_h0'], sg['_h1'], sg['_L']))
    ts = [x for x in json.load(open(TJ)) if x['id'] != 'backyard'] + [d]
    json.dump(ts, open(TJ, 'w', newline=''), separators=(',', ':'))
    print({k: (v if not isinstance(v, list) else len(v)) for k, v in d.items() if k not in ('blurb',)})
