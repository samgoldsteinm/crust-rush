"""PC: the finish's driver close-up looks down into the cockpit from a front three-quarter (web v246, patch 112).
    python tools/mini/pc100.py      (once, after pc99)"""
G = 'D:/crust-rush/godot/scripts/'


def rep(f, a, b, n=1):
    p = G + f
    s = open(p, encoding='utf-8', newline='').read()
    assert s.count(a) == n, (f, s.count(a), a[:80])
    s = s.replace(a, b)
    open(p, 'w', encoding='utf-8', newline='').write(s)


rep('main.gd', """		var an := rma + fin_side * (0.2 + 0.34 * float(ez.call(u))) * PI
		var R := (13.0 - 2.5 * u) * k.sf""", """		var an := rma + fin_side * (0.14 + 0.22 * float(ez.call(u))) * PI   # (pc100) round to the front quarter, not past side-on
		var R := (14.0 - 2.0 * u) * k.sf
		var up := maxf(3.0, R * 0.58)   # looking down into the cockpit, so the face shows over the door""")
rep('main.gd', "cam.global_position = Vector3(cx, maxf(hd.y + 2.4 - 1.2 * u, T.ground(cx, cz) + 1.5), cz)",
    "cam.global_position = Vector3(cx, maxf(hd.y + up, T.ground(cx, cz) + 1.5), cz)")
print('pc100 applied')
