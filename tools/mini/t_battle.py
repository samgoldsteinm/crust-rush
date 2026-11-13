"""Prep Table Showdown: the arena for Balloon Battle (docs/BALLOON-BATTLE-PLAN.md). Not a race track: there is no lap.
The game still wants a ring of track points to hang its bookkeeping on, so this writes a small circle in the middle of
the table, flat, with nothing on it: no boxes, pads, ramps or shortcuts. `battle` switches the track's walls and rules off
(BATTLE in tools/mini/battle.js); the arena itself (its floor, walls, bins, the raised route) is BATTLE_SHAPES there.
Run: py.cmd tools/mini/t_battle.py   (adds or replaces the entry in tools/mini/tracks.json)
"""
import json, math
TJ = 'D:/crust-rush/source/tools/mini/tracks.json'
R, n = 96.0, 40
d = dict(id='preptable', name='Prep Table Showdown', theme='kitchen', R=1160, exact=1, arena=1, neon=1, themeName='Battle arena', toy=1, rw=31, laps=99,
         look='battle', battle=1, special=1,
         blurb='Balloon Battle on a pizzeria prep table: an open middle to line up a shot, a pizza-box lid for a ramp onto the stacked boxes, and a row of ingredient bins to dodge round.')
d['ctrl'] = [[round(R * math.cos(2 * math.pi * i / n), 1), round(R * math.sin(2 * math.pi * i / n), 1)] for i in range(n)]
d['elev'] = [0.0] * n; d['elevR'] = [0.0] * n
d['boxes'] = []; d['npads'] = []; d['nramps'] = []; d['nshorts'] = []; d['tloops'] = []
ts = [x for x in json.load(open(TJ)) if x['id'] != 'preptable'] + [d]
json.dump(ts, open(TJ, 'w', newline=''), separators=(',', ':'))
print('preptable written:', n, 'ring points')
