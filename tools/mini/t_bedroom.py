import sys
sys.path.insert(0, 'D:/crust-rush/source/tools/neon')
from gen import Track

def make():
    t = Track('bedroom', 'Bedroom Blitz', themeName='Toy track', theme='kitchen', toy=1, rw=31, laps=4, R=1160, look='bedroom',
              blurb='A toy racing set built round a real bedroom: off the desk, down a wide spiral round the lamp, under the bed, through the loop in the middle of the room, past the sneakers and back up over the dresser.')
    t.center = False; t.walld = 46.0; t.cross_dh = 60.0; t.gap = 260
    t.origin = (-200.0, 605.0, 0.0)             # the start line, on the desk, heading east
    s0 = t.S(424, h=262)                        # along the desk to its east end
    s1 = t.S(180, h=235)                        # the launch and the raised landing
    s2 = t.S(56, h=235)
    a3 = t.A(150, -450, h=0)                    # a wide spiral round the floor lamp, one and a quarter turns down to the floor
    s4 = t.S(1015, h=0)                         # south along the east wall, under the bed
    a5 = t.A(100, -180, h=0)                    # hairpin under the bed
    s6 = t.S(480, h=0)
    a7 = t.A(100, 90, h=0)
    s8 = t.S(630, h=0)                          # west through the middle of the room: the loop
    a9 = t.A(100, 90, h=0)
    s10 = t.S(520, h=0)                         # south: the jump between the sneakers
    a11 = t.A(100, -180, h=0)
    s12 = t.S(900, h=262)                       # the climb along the west wall, over the dresser
    s13 = t.S(195, h=262)
    a14 = t.A(110, -90, h=262)
    s15 = t.S(310, h=262)                       # onto the desk, to the line
    t.build(close=(s15, s13))
    # boosters (the whole width of the track), jumps, item boxes and the loop
    for seg, f in [(s4, .72), (s6, .45), (s12, .04)]:
        t.pad(seg, f, 0, 10)
    for seg, f in [(s0, .9), (s10, .3)]:
        t.ramp(seg, f)
    for seg, f in [(s4, .1), (s10, .82), (s13, .5)]:
        t.box(seg, f)
    t.short(s8, .85, s10, .18, 0)               # a one-lane cut across the corner after the loop: STRAIGHT, leaving and rejoining at about 45 degrees (web v192: it was .93 to .5, which left at 72 degrees)
    t.loops = [(s8, .435, .36)]
    t.S0 = s0
    return t

if __name__ == '__main__':
    import json
    t = make()
    print(t.check())
    t.plot('D:/crust-rush/source/tools/mini/bedroom.png')
    d = t.export()
    d['tloops'] = [[round(t.frac(sg, f), 5), k] for sg, f, k in t.loops]
    import numpy as np
    for nm, (sg, f, _k) in [('loop', t.loops[0])]:
        i = int(t.frac(sg, f) * len(t.P)); print(nm, t.P[i][:2])
    json.dump([d], open('D:/crust-rush/source/tools/mini/tracks.json', 'w'), separators=(',', ':'))
    print({k: (v if not isinstance(v, list) else len(v)) for k, v in d.items() if k not in ('blurb',)})
