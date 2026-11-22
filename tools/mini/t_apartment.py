"""Apartment Run: a toy racing set laid through the owner's own apartment (their video, sketch and photos, 2026-11-22).
A special track: no cup, no Sandbox. The floor plan the owner approved is tools/mini/apt_plan.py (scratch/apt_plan6.png),
in METRES: x east, y north, the apartment's south-west corner (the bedroom's) at 0. G() below turns metres into design units
(347 a metre, the toy scale: a kart is 7.5 cm) with the apartment's middle at 0. The room (mini.js, toyApartment) uses the
same metres through the same G().
  bedroom x 0..4.6, y 1.1..6.1    living room x 4.6..7.4, kitchen/dining x 7.4..10.3, y 1.1..6.3    hall y 0.3..1.1
  bed: headboard on the west wall, x 0..1.65, y 3.05..4.3, top 55 cm   nightstand x .05..5, y 4.35..4.8, 60 cm
  dresser on the north wall x 1.15..2.95, y 5.55..6.07, 85 cm           desk in the north-east corner x 3.3..4.55, y 5.35..6.05, 75 cm
  bedroom door x 2.75..3.55 (the two lanes pass side by side)           loveseat x 5.5..6.78, y 2.0..2.86 (faces the TV)
  dining table x 7.57..9.5, y 4.79..5.71 (the track runs under it)     galley floor x 8.36..9.57
The lap: start in the hall by the kitchen heading west; into the bedroom; a climb up onto the bed; across it; over the
nightstand onto the dresser; a jump onto the desk; raised track down the bedroom's east wall, out of the door and over the
hall (the start straight runs underneath); north up the living room's west side; the loop in front of the TV and the sliding
door; under the dining table; down the galley; back into the hall.
Run: py.cmd tools/mini/t_apartment.py   (adds or replaces the apartment entry in tracks.json, draws apartment.png)
"""
import sys, json
sys.path.insert(0, 'D:/crust-rush/source/tools/neon')
from gen import Track

TJ = 'D:/crust-rush/source/tools/mini/tracks.json'
M = 347.0                                         # design units a metre
CX, CY = 5.3, 3.15                                # the apartment's middle, in metres
G = lambda gx, gy: ((gx - CX) * M, (gy - CY) * M)
BED, DRESSER, DESK = 193, 297, 264                # track heights on them (2 above the top)


def make():
    t = Track('apartment', 'Apartment Run', themeName='Toy track', theme='kitchen', toy=1, rw=31, laps=3, R=2300, look='apartment', special=1,
              blurb='A toy racing set through a real apartment: down the hall, up onto the bed, across the dresser and a jump onto the desk, out over the hall, a loop in front of the TV, under the dining table and down the galley.')
    t.center = False; t.walld = 46.0; t.cross_dh = 60.0; t.gap = 260
    m = lambda v: v * M
    S = lambda L, h: t.S(m(L), h=h)
    A = lambda R, deg, h: t.A(m(R), deg, h=h)
    t.origin = (*G(8.3, 0.68), 3.14159265358979)    # the start line, in the hall by the kitchen, heading west
    s0 = S(5.02, 0)                               # west down the hall, past the bikes, the vacuum and the closets
    A(.3, -90, 0)                                 # right, into the bedroom (the door's west half)
    s2 = S(.52, 0)
    s3 = S(1.78, 100)                             # north past the laundry basket, climbing
    A(.4, 90, 135)                                # left, still climbing
    s5 = S(.93, BED)                              # west, up to the foot of the bed
    s6 = S(.95, BED)                              # across the bedspread
    A(.4, -90, BED)                               # right, at the head of the bed
    s8 = S(1.24, DRESSER)                         # north over the nightstand, up to the dresser
    A(.4, -90, DRESSER)                           # right
    s10 = S(2.25, DRESSER)                        # east along the dresser, under the window
    s11 = S(.35, DESK)                            # the jump across to the desk
    s12 = S(.6, DESK)                             # along the desk
    A(.35, -90, DESK)                             # right, off the desk's front
    s14 = S(2.97, 160)                            # south down the east wall on piers, past the TV
    A(.45, -90, 155)                              # right
    A(.45, 90, 150)                               # left, round the litter box
    s17 = S(.4, 150)                              # out of the door (its east half)
    A(.33, 90, 150)                               # left, over the hall
    s19 = S(1.22, 150)                            # east over the start straight
    A(.35, 90, 140)                               # left, into the living room
    s21 = S(2.08, 0)                              # north up the west side, down to the floor
    s22 = S(1.7, 0)                               # past the speakers and the records
    A(.4, -90, 0)                                 # right, in front of the TV
    s24 = S(2.95, 0)                              # east past the sliding door (the loop), under the dining table
    A(.4, -90, 0)                                 # right, into the galley
    s26 = S(3.82, 0)                              # south down the galley, past the fridge and the dishwasher
    A(.4, -90, 0)                                 # right, into the hall
    s28 = S(.3, 0)                                # to the line
    t.build(close=(s28, s26))
    for seg, f in [(s0, .3), (s14, .35), (s24, .82), (s21, .7)]:
        t.pad(seg, f, 0, 10)
    for seg, f in [(s10, .93), (s26, .55)]:       # the dresser's end is the jump; a kicker in the galley
        t.ramp(seg, f)
    for seg, f in [(s0, .62), (s6, .5), (s22, .5), (s26, .25)]:
        t.box(seg, f)
    t.loops = [(s24, .22, .36)]
    t.S0 = s0
    return t


if __name__ == '__main__':
    t = make()
    print(t.check())
    t.plot('D:/crust-rush/source/tools/mini/apartment.png')
    d = t.export()
    d['tloops'] = [[round(t.frac(sg, f), 5), k] for sg, f, k in t.loops]
    for i, sg in enumerate(t.segs):
        j = int(sg['_s0'] / 4.0) % len(t.P)
        print('seg %2d %s starts at (%5.2f,%5.2f) m  lap %.3f  h %3.0f -> %3.0f  L %4.0f' % (i, sg['k'], t.P[j][0] / M + CX, t.P[j][1] / M + CY, sg['_s0'] / t.L, sg['_h0'], sg['_h1'], sg['_L']))
    ts = [x for x in json.load(open(TJ)) if x['id'] != 'apartment'] + [d]
    json.dump(ts, open(TJ, 'w', newline=''), separators=(',', ':'))
    print({k: (v if not isinstance(v, list) else len(v)) for k, v in d.items() if k not in ('blurb',)})
