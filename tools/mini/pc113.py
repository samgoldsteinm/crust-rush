"""PC: the cinematic finish on the toy tracks. The owner: "the cinematic camera shots are not working on the hot wheels maps".
The trackside camera (shot A) and the place sign (shot C) stood on the ground under the road, T.ground(x, y), without the
road's own height above it (T.ey: the toy tracks' raised decks, the multi-level roads), so on a toy track the camera sat on the
room's floor looking up through the furniture, and the sign stood down there too. Now both are on the road: ground + ey at that
point of the track (as the karts are, kart.gd), as the web's (groundAt + q.ey).
    python tools/mini/pc113.py      (once, after pc112)"""
p = 'D:/crust-rush/godot/scripts/main.gd'
s = open(p, encoding='utf-8', newline='').read()
assert 'pc113' not in s


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:80])
    s = s.replace(a, b)


rep("""	return [T.px[j], T.py[j], T.tx[j] * dir, T.ty[j] * dir]
""", """	return [T.px[j], T.py[j], T.tx[j] * dir, T.ty[j] * dir, j]   # (pc113: and which point, for the road's height there)
""")
rep("""			fin_cp = Vector3(x, T.ground(x, y) + 3.2, y)
""", """			fin_cp = Vector3(x, T.ground(x, y) + T.ey[int(a[4])] + 3.2, y)   # (pc113) on the road, raised decks too
""")
rep("""			g.global_position = Vector3(float(a[0]), T.ground(float(a[0]), float(a[1])) + 14.0, float(a[1]))
""", """			g.global_position = Vector3(float(a[0]), T.ground(float(a[0]), float(a[1])) + T.ey[int(a[4])] + 14.0, float(a[1]))   # (pc113)
""")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('pc113 applied')
