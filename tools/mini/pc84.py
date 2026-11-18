"""PC: the second take of web patches 82 and 83 (the first takes, pc82 and pc83, went out in the PC build of web v223):
- the rim colour paints the spokes and the brake caliper only (the owner: "the entire wheel shouldnt change colors only the brake caliper
  and the wheel spokes"): a kart's wheel set its spoke classes 16-19 and the caliper 13 (was every class but tyre and caliper); a car's
  own wheels their rim classes plus the caliper; a code-built wheel its spokes only (g_paint; its rim g_dark keeps the trim colour);
  a car body's calipers (class 13, which took the accent colour) take the rim colour when one is chosen.
- flying: the camera sits low behind the kart (cy = rz - 8, was rz - 2): "the camera should sit lower behind the user so they can see
  more in front of them".
    py.cmd tools/mini/pc84.py      (once, after pc83)"""
G = 'D:/crust-rush/godot/scripts/'


def rep(f, a, b, n=1):
    p = G + f
    s = open(p, encoding='utf-8', newline='').read()
    assert s.count(a) == n, (f, s.count(a), a[:80])
    s = s.replace(a, b)
    open(p, 'w', encoding='utf-8', newline='').write(s)


rep('kart_builder.gd', '''			for ci in 23:   # (pc82, web patch 82: a kart's wheel set: all but the tyre and the caliper)
				if ci != 8 and ci != 13:
					rimall[ci] = rimc
					rimallpbr[ci] = [float(rmc.get("r", 0.2)), 0.95] if rmc.has("m") else [0.38, 0.3]
''', '''			for ci in [16, 17, 18, 19]:   # (pc84, web patch 82: a kart's wheel set: its spokes' own colour classes)
				rimall[ci] = rimc
				rimallpbr[ci] = [float(rmc.get("r", 0.2)), 0.95] if rmc.has("m") else [0.38, 0.3]
			rimall[13] = rimc   # (pc84: the caliper too, keeping its painted finish)
			rimre[13] = rimc
			vcre[13] = rimc   # (pc84: a car body's calipers: the rims' colour, not the accent's)
''')
rep('kart_builder.gd', '''			if wheel and cols.get("rimc") != null and (nm.begins_with("g_dark") or nm.begins_with("g_paint")):
				# (pc82, web patch 82) a code-built wheel: its rim and spokes take the rim colour''', '''			if wheel and cols.get("rimc") != null and nm.begins_with("g_paint"):
				# (pc82 / pc84, web patch 82) a code-built wheel: its spokes take the rim colour (its rim keeps the trim's)''')
rep('main.gd', '	var cy := rz - 2.0 if k.fly else', '	var cy := rz - 8.0 if k.fly else')
print('pc84 applied')
