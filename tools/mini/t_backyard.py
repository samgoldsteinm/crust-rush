"""Backyard Mega Circuit: the fourth Miniature Mayhem track. A toy racing set laid right round the back garden: the garden
every room's window looks onto (tools/blender/outside.py, yardlib.py), at its real size, 25 m long and 7 m deep.
Garden coordinates, in metres: x east with the bedroom window at 0, y north from the house wall (0) to the back fence (7).
What stands where (the yard in tools/mini/mini.js, toyYard, must match):
  house wall y 0, windows: kitchen x -7, bedroom 0, garage 7.5      patio y 0..1.6
  shed (-11.2, 5.4), 2.4 x 1.9          washing line y 4.2, poles at x -8.2 and -3.4
  the tree (3.1, 5.2)                    goal: posts (8.6, 5.6) and (10.6, 5.6)       drain pipe (-3.6, 5.71), 1.5 long, lying east-west
  flower bed x -7.4..-0.6, y 6.25..7
Design coordinates are those metres turned into game units and centred: G() below. Two laps.

SECOND LAYOUT (web v186, 2026-11-13). The owner on the first: "There's too many straights ... right now it's mainly just
driving straight". The first was one long thin lap of straights (4, 4, 3, 7, 3.5, 4 m). This one keeps its landmarks (the
loop off the line, in at the goal's mouth and out under its stay, once round the tree climbing, the long drop, through the
drain pipe, behind the shed, under the washing) and bends everything between them: a slalom along the patio, S-bends up to
the goal and along the back fence, the drop swung out over the lawn, three hairpins back and forth under the washing line,
and a weaving run home along the lawn's edge. The longest straights left are the loop's run-up and the one through the pipe.
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
              blurb='A toy racing set laid right round the back garden: a slalom along the patio, through the goal, a spiral up the tree and a swooping drop, down a drainpipe, three hairpins under the washing line, behind the shed and a weaving run home.')
    t.center = False; t.walld = 46.0; t.cross_dh = 60.0; t.gap = 260
    t.origin = (*G(-.6, .9), 0.0)                # the start line, on the patio by the bedroom window, heading east
    m = lambda v: v * M
    S = lambda L, h=0: t.S(m(L), h=h)
    A = lambda R, deg, h=0: t.A(m(R), deg, h=h)
    # ---- the patio: the loop, then a slalom between the flowerpots
    s0 = S(3.3)                                  # the loop's run-up and the loop
    A(.62, 48); A(.62, -96); A(.62, 96); A(.62, -96); A(.62, 48)
    s1 = S(.5)
    # ---- the east end: up to the goal in a wide S, in at its mouth, out under its west stay
    A(.8, 90)                                    # north
    A(1.2, -78); A(1.2, 78)                      # over to the goal's line (x 9.6)
    s3 = S(1.55)                                 # to the mouth (y 5.6)
    A(.4, 90)                                    # round inside it: west, at y 6.0
    s4 = S(.9)                                   # out under the stay
    # ---- along the back fence to the tree: two S-bends with a step south between them
    A(.75, 40); A(.75, -80); A(.75, 40)
    s4b = S(.5)
    A(.75, 35); A(.75, -35)
    A(.75, 40); A(.75, -80); A(.75, 40)          # arrives at the tree: (3.07, 5.73)
    sp = t.A(m(.52), 360, h=260)                 # once round the tree, climbing
    # ---- the drop: swung out over the lawn and back, then an S into the pipe
    A(1.0, 62, h=170); A(1.0, -124, h=50); A(1.0, 62, h=0)
    A(.8, 30); A(.8, -60); A(.8, 30)
    s6 = S(2.6)                                  # the one straight: through the drain pipe (x -2.85..-4.35)
    # ---- back and forth under the washing line
    A(.55, 90)                                   # south, at x -5.2
    h1 = S(1.38)
    A(.5, -180)                                  # hairpin: north, at x -6.2
    h2 = S(1.5)
    A(.5, 180)                                   # hairpin: south, at x -7.2 (its top is at y 5.8: the flower bed begins at 6.25)
    h3 = S(1.5)
    A(.55, -90)                                  # west, south of the washing pole
    h3b = S(1.15)
    A(.55, -90)                                  # north, between the pole and the shed (x -9.45)
    h4 = S(2.275)
    A(.6, 90)                                    # west, behind the shed (y 6.675: the gap is 6.35..7.0)
    s7 = S(2.75)                                 # behind the shed
    A(.55, 90)
    s8 = S(1.775)                                # south down the side fence
    A(.55, 90)                                   # east, past the shed door (y 3.8)
    s9 = S(1.3)                                  # a jump
    A(1.1, -73); A(1.1, 73)                      # down to the lawn's edge (y 2.25)
    # ---- the run home along the lawn's edge: a weave, then down onto the patio
    s10 = S(.2)
    A(.9, 28); A(.9, -56); A(.9, 56); A(.9, -56); A(.9, 56); A(.9, -56); A(.9, 56); A(.9, -56); A(.9, 28)
    s11 = S(.34)                                 # (solved)
    A(.55, -90)                                  # south onto the patio
    s12 = S(.25)                                 # (solved)
    A(.55, 90)                                   # east: the line
    s13 = S(.4)
    t.build(close=(s11, s12))                    # the two straights whose lengths are solved so the lap closes
    for seg, f in [(s6, .06), (h4, .25), (s3, .15)]:
        t.pad(seg, f, 0, 10)
    for seg, f in [(s9, .3), (s7, .75)]:
        t.ramp(seg, f)
    for seg, f in [(s1, .5), (s4, .6), (h2, .5), (s7, .3), (s8, .6)]:
        t.box(seg, f)
    t.loops = [(s0, .55, .36)]
    t.S0 = s0
    t.named = dict(s0=s0, s4=s4, sp=sp, s6=s6, s7=s7, s9=s9, h2=h2)
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
    order = ['bedroom', 'kitchen', 'garage', 'backyard', 'preptable']; ts.sort(key=lambda x: order.index(x['id']) if x['id'] in order else 99)   # the tracks' order in the game must not change
    json.dump(ts, open(TJ, 'w', newline=''), separators=(',', ':'))
    print({k: (v if not isinstance(v, list) else len(v)) for k, v in d.items() if k not in ('blurb',)})
