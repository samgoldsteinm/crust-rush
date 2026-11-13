"""Kitchen Chaos: the second Miniature Mayhem track. A toy racing set built round a real kitchen, 4.0 x 4.8 m.
Design coordinates as for the bedroom: x east, y north, the room's middle at 0, heading 0 = east; the game's z is -y.
The room (tools/mini/mini.js, toyKitchen) must match these numbers:
  worktop along the north wall   y 618..833, top 312 (90 cm)        the start straight runs along it at y 720
  kitchen table in the middle    x -278..278, y -140..138, top 260  the track crosses it
  spiral                          centre (-460,-210), radius 150     round a bar stool
Run: py.cmd tools/mini/t_kitchen.py   (adds or replaces the kitchen entry in tools/mini/tracks.json and draws kitchen.png)
"""
import sys, json
sys.path.insert(0, 'D:/crust-rush/source/tools/neon')
from gen import Track

TJ = 'D:/crust-rush/source/tools/mini/tracks.json'


def make():
    t = Track('kitchen', 'Kitchen Chaos', themeName='Toy track', theme='kitchen', toy=1, rw=31, laps=4, R=1160, look='kitchen',
              blurb='A toy racing set built round a real kitchen: along the worktop, over a bridge onto the kitchen table, down a wide spiral round a stool, through the loop by the back door, and a long climb home past the fridge.')
    t.center = False; t.walld = 46.0; t.cross_dh = 60.0; t.gap = 260
    t.origin = (-300.0, 720.0, 0.0)             # the start line, on the worktop, heading east
    s0 = t.S(390, h=314)                        # along the worktop
    a1 = t.A(110, -90, h=314)                   # right, to the front edge
    s2 = t.S(472, h=262)                        # the bridge down to the kitchen table
    s3 = t.S(98, h=262)                         # onto the table
    a4 = t.A(100, -90, h=262)
    s5 = t.S(560, h=262)                        # west along the table and off its end
    a6 = t.A(150, 450, h=0)                     # a wide spiral round the bar stool, one and a quarter turns down to the floor
    s7 = t.S(300, h=0)                          # south along the west wall
    a8 = t.A(110, 90, h=0)
    s9 = t.S(920, h=0)                          # east along the south wall: the loop
    a10 = t.A(110, 90, h=0)
    s11 = t.S(840, h=0)                         # north up the east side: the jump
    a12 = t.A(110, 90, h=0)
    s13 = t.S(890, h=230)                       # the climb west, under the bridge
    a14 = t.A(140, -180, h=314)                 # round onto the worktop
    s15 = t.S(170, h=314)                       # to the line
    t.build(close=(s15, s11))               # the two straights whose lengths are solved so the lap closes (they must not be parallel)
    for seg, f in [(s7, .55), (s11, .08), (s13, .04)]:
        t.pad(seg, f, 0, 10)
    for seg, f in [(s2, .25), (s11, .5)]:
        t.ramp(seg, f)
    for seg, f in [(s7, .15), (s11, .8), (s13, .6)]:
        t.box(seg, f)
    t.short(s9, .9, s11, .14, 0)                # a one-lane cut across the corner after the loop
    t.loops = [(s9, .45, .36)]
    t.S0 = s0
    return t


if __name__ == '__main__':
    t = make()
    print(t.check())
    t.plot('D:/crust-rush/source/tools/mini/kitchen.png')
    d = t.export()
    d['tloops'] = [[round(t.frac(sg, f), 5), k] for sg, f, k in t.loops]
    for nm, (sg, f, _k) in [('loop', t.loops[0])]:
        i = int(t.frac(sg, f) * len(t.P)); print(nm, t.P[i][:2])
    for i, sg in enumerate(t.segs):
        j = int(sg['_s0'] / 4.0) % len(t.P); print('seg %2d %s starts at (%5.0f,%5.0f) lap %.3f  h %3.0f -> %3.0f  L %4.0f' % (i, sg['k'], t.P[j][0], t.P[j][1], sg['_s0'] / t.L, sg['_h0'], sg['_h1'], sg['_L']))
    ts = [x for x in json.load(open(TJ)) if x['id'] != 'kitchen'] + [d]
    json.dump(ts, open(TJ, 'w', newline=''), separators=(',', ':'))
    print({k: (v if not isinstance(v, list) else len(v)) for k, v in d.items() if k not in ('blurb',)})
