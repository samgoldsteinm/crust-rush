"""How close does each loose thing in a toy room stand to the track? usage: py.cmd tools/mini/clearcheck.py garage
Reads the lap from tools/mini/tracks.json and the things below (design coordinates as in mini.js: x east, y north; r is the
thing's reach from its middle, h its height, all in game units). A thing is in the way if any part of the lap passes
within its reach plus the track's own half width (road, raised edge and a margin: 31 + 7 + 6), unless that part of the lap
is well above the thing's top. Prints the worst gap for each (negative: it is in the track)."""
import json, math, sys
HALF = 31 + 7 + 6
THINGS = {'garage': [  # name, x, y, reach, height
    ('tyre stack', -252, 576, 86, 226), ('jerry can', 70, 430, 62, 160), ('paint can a', 40, 530, 30, 66), ('paint can b', 10, 580, 30, 66),
    ('trolley jack', -170, -20, 125, 250), ('cone a', 330, -420, 50, 160), ('cone b', 400, -250, 50, 160), ('cone c', -520, -640, 50, 160),
    ('one tyre', 360, 330, 104, 70), ('toolbox', 330, 60, 80, 80), ('tennis ball', -560, 420, 12, 24), ('bricks', 420, 160, 40, 20), ('cube', -90, -480, 16, 20),
    ('set box', 120, -470, 75, 30), ('track piece', 250, -520, 45, 6), ('skateboard', -560, -300, 40, 45), ('carton sw', -600, -770, 100, 100), ('carton se', 646, -774, 70, 160),
    ('tool cabinet', -582, 746, 135, 330), ('shelving', -625, 100, 72, 625)]}   # (the skateboard and the shelving are long and lie along the wall: their reach is the short way)
# the garden's loose things, in GARDEN METRES as toyYard has them (x east from the bedroom window, y north from the house wall): name, gx, gy, reach m, height m
YARD = [('pot a', 5.0, .5, .24, .5), ('pot b', -1.2, .3, .22, .5), ('pot c', 1.4, .32, .26, .5), ('pot d', 6.3, .3, .23, .5), ('pot e', -8.6, .34, .25, .5), ('watering can', 4.5, 1.72, .22, .35),
        ('gnome', 2.3, 3.6, .09, .36), ('fuel can', -13.3, 2.9, .2, .46), ('cone', -12.4, 2.5, .15, .46), ('one tyre', 10.9, 2.2, .3, .2), ('skateboard', -3.3, 1.2, .16, .13), ('sneaker', -4.0, .55, .16, .12),
        ('set box', 1.6, 1.45, .25, .08), ('track piece', 2.5, 1.5, .15, .02), ('tennis ball', -11.4, 2.8, .04, .07), ('bricks', 6.9, 1.5, .14, .06), ('cube', -6.2, 2.7, .05, .06), ('football', 7.4, 3.9, .12, .22),
        ('tree trunk', 3.1, 5.2, .3, 6.0), ('washing pole w', -8.2, 4.2, .05, 2.0), ('washing pole e', -3.4, 4.2, .05, 2.0), ('goal post w', 8.6, 5.6, .05, 1.3), ('goal post e', 10.6, 5.6, .05, 1.3),
        ('goal stay foot w', 8.6, 6.3, .05, .1), ('goal stay foot e', 10.6, 6.3, .05, .1)] + [('bed pot %d' % i, gx, 6.62, .22, .4) for i, gx in enumerate((-6.9, -5.9, -4.9, -2.6, -1.5))]
THINGS['backyard'] = [(n, (gx + .75) * 347, (gy - 3.5) * 347, r * 347, h * 347) for n, gx, gy, r, h in YARD]
room = sys.argv[1]
t = [x for x in json.load(open('D:/crust-rush/source/tools/mini/tracks.json')) if x['id'] == room][0]
P = [(c[0], -c[1], e) for c, e in zip(t['ctrl'], t['elev'])]
bad = 0
for name, x, y, r, h in THINGS[room]:
    best = 1e9; at = None
    for (px, py, e) in P:
        if e > h + 30: continue                      # the lap is over its head here
        d = math.hypot(px - x, py - y) - r - HALF
        if d < best: best = d; at = (round(px), round(py), round(e))
    flag = '  <-- IN THE WAY' if best < 0 else ''
    bad += best < 0
    print(f'{name:14s} gap {best:7.1f}  nearest lap point {at}{flag}')
print('in the way:', bad)
