"""PC: wheels on the road, not in it. The owner: "some of the wheels are going into the tracks on some maps". The web draws a
kart's body at the road under it (syncKart: base = max(road at the middle, the road between the axles, the road between the
sides), the body at clamp(base, z - 1.2, z + 6), or at least z on a jump ramp or off the ground), not at the kart's own
height alone; the PC drew it at the kart's height, which on the toy tracks' steep ramps runs a few units under the road, so
the wheels sank a third of the way into it. Now the same as the web.
    python tools/mini/pc115.py      (once, after pc114)"""
p = 'D:/crust-rush/godot/scripts/view.gd'
s = open(p, encoding='utf-8', newline='').read()
assert 'pc115' not in s


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:80])
    s = s.replace(a, b)


rep("""			var hR := T.ground(x + sa * fW, y - ca * fW) + T.k_ey(k.idx, x + sa * fW, y - ca * fW)
""", """			var hR := T.ground(x + sa * fW, y - ca * fW) + T.k_ey(k.idx, x + sa * fW, y - ca * fW)
			var hC := T.ground(x, y) + T.k_ey(k.idx, x, y)   # (pc115) the road under the middle
""")
rep("""				hR = arena.ground(x + sa * fW, y - ca * fW)
			if k.tun != null:""", """				hR = arena.ground(x + sa * fW, y - ca * fW)
				hC = arena.ground(x, y)
			if k.tun != null:""")
rep("""				hR = hF
			elif k.sbf:""", """				hR = hF
				hC = hF
			elif k.sbf:""")
rep("""				hR = sbx.ground(x + sa * fW, y - ca * fW, z + 1.0)
""", """				hR = sbx.ground(x + sa * fW, y - ca * fW, z + 1.0)
				hC = sbx.ground(x, y, z + 1.0)
""")
rep("""			var sR := (hL - hR) / (2.0 * fW)
			var ff := minf(1.0, 16.0 * dt)
""", """			var sR := (hL - hR) / (2.0 * fW)
			var ff := minf(1.0, 16.0 * dt)
			# (pc115) the body on the road under it, as the web's (syncKart: mid, base, clamp)
			var mid := hB + (hF - hB) * (-fR) / (fF - fR)
			var base := maxf(hC, maxf(mid, (hL + hR) * 0.5))
			pos.y = maxf(z, base) if (k.on_ramp or k.z > 0.4) else clampf(base, z - 1.2, z + 6.0)
""")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('pc115 applied')
