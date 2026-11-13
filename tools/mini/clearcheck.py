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
