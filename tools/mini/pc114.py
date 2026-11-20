"""PC: the grid on a raised start. The owner (a toy track, the bedroom one): the countdown camera stood in the furniture.
Bedroom Blitz starts on a deck about 260 up, and the grid set every kart down on the room's floor under it (T.ground without
the road's height), so through the countdown the camera looked out of the bed's frame; the karts only came up to the road when
the race began. Now they start on the road: ground + T.k_ey (the height a kart is put back at, kart.gd / sandbox.gd).
    python tools/mini/pc114.py      (once, after pc113)"""
p = 'D:/crust-rush/godot/scripts/race.gd'
s = open(p, encoding='utf-8', newline='').read()
assert 'pc114' not in s
a = '	k.setup(T, {"x": x, "y": y, "a": T.ang[idx], "wy": T.ground(x, y)}, idx - T.N, info)\n'
b = '	k.setup(T, {"x": x, "y": y, "a": T.ang[idx], "wy": T.ground(x, y) + T.k_ey(idx, x, y)}, idx - T.N, info)   # (pc114) on a raised start too\n'
assert s.count(a) == 1
s = s.replace(a, b)
open(p, 'w', encoding='utf-8', newline='').write(s)
print('pc114 applied')
