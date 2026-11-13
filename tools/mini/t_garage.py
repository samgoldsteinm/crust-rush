"""Garage Overdrive: the third Miniature Mayhem track. A toy racing set built round a real garage, 4.0 x 4.8 m.
Design coordinates as for the other rooms: x east, y north, the room's middle at 0, heading 0 = east; the game's z is -y.
The room (tools/mini/mini.js, toyGarage) must match these numbers:
  workbench along the east wall    x 480..695, y 430..833, top 312 (90 cm)   the track runs along it at x 588
  its return along the north wall  x 130..695, y 618..833, top 312           the track runs along it at y 726
  stack of tyres                    centre (-252,576), radius 100             the spiral goes round it
  garage door                       the south wall; the start straight runs in front of it at y -700
Run: py.cmd tools/mini/t_garage.py   (adds or replaces the garage entry in tools/mini/tracks.json and draws garage.png)
"""
import sys, json
sys.path.insert(0, 'D:/crust-rush/source/tools/neon')
from gen import Track

TJ = 'D:/crust-rush/source/tools/mini/tracks.json'


def make():
    t = Track('garage', 'Garage Overdrive', themeName='Toy track', theme='kitchen', toy=1, rw=31, laps=4, R=1160, look='garage',
              blurb='A toy racing set built round a real garage: off the line past the big door, up a plank onto the workbench, a flying leap off its end, down a spiral round a stack of tyres, the loop, and a chicane across the oil-stained floor.')
    t.center = False; t.walld = 46.0; t.cross_dh = 60.0; t.gap = 260
    t.origin = (-150.0, -700.0, 0.0)            # the start line, on the floor in front of the garage door, heading east
    s0 = t.S(611, h=0)                          # east along the garage door: the loop
    a1 = t.A(127, 90, h=0)                      # left, to head north up the east side
    s2 = t.S(1040, h=314)                       # the plank: a long climb onto the workbench (any shorter is steeper than the bedroom's steepest, .44)
    s3 = t.S(149, h=314)                        # north along the workbench
    a4 = t.A(110, 90, h=314)                    # left, onto its return along the north wall
    s5 = t.S(250, h=314)                        # west along the north wall
    s6 = t.S(480, h=170)                        # off the end of the bench: the jump, and down
    a7 = t.A(150, 450, h=0)                     # a wide spiral round the stack of tyres, one and a quarter turns down to the floor
    s8 = t.S(250, h=0)                          # south along the west side
    a9 = t.A(120, 90, h=0)                      # the chicane across the middle of the floor
    s10 = t.S(300, h=0)
    a11 = t.A(120, -90, h=0)
    s12 = t.S(200, h=0)
    a13 = t.A(120, -90, h=0)
    s14 = t.S(300, h=0)
    a15 = t.A(120, 90, h=0)
    s16 = t.S(216, h=0)                         # south again, past the door to the house
    a17 = t.A(130, 90, h=0)
    s18 = t.S(122, h=0)                         # to the line
    t.build(close=(s18, s16))                   # the two straights whose lengths are solved so the lap closes (they must not be parallel)
    for seg, f in [(s2, .04), (s8, .1), (s16, .2)]:
        t.pad(seg, f, 0, 10)
    for seg, f in [(s6, .1), (s14, .45)]:
        t.ramp(seg, f)
    for seg, f in [(s5, .6), (s8, .5), (s12, .5)]:
        t.box(seg, f)
    t.short(s10, .7, s12, .3, 0)                # a one-lane cut across the first corner of the chicane
    t.loops = [(s0, .55, .36)]
    t.S0 = s0
    return t


if __name__ == '__main__':
    t = make()
    print(t.check())
    t.plot('D:/crust-rush/source/tools/mini/garage.png')
    d = t.export()
    d['tloops'] = [[round(t.frac(sg, f), 5), k] for sg, f, k in t.loops]
    for nm, (sg, f, _k) in [('loop', t.loops[0])]:
        i = int(t.frac(sg, f) * len(t.P)); print(nm, t.P[i][:2])
    for i, sg in enumerate(t.segs):
        j = int(sg['_s0'] / 4.0) % len(t.P); print('seg %2d %s starts at (%5.0f,%5.0f) lap %.3f  h %3.0f -> %3.0f  L %4.0f' % (i, sg['k'], t.P[j][0], t.P[j][1], sg['_s0'] / t.L, sg['_h0'], sg['_h1'], sg['_L']))
    ts = [x for x in json.load(open(TJ)) if x['id'] != 'garage'] + [d]
    json.dump(ts, open(TJ, 'w', newline=''), separators=(',', ':'))
    print({k: (v if not isinstance(v, list) else len(v)) for k, v in d.items() if k not in ('blurb',)})
