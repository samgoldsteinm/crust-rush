"""PC: the final take of web patch 82 (v224): the Rims colour paints exactly each wheel's spokes, a new Calipers colour the calipers.
    py.cmd tools/mini/pc85.py      (once, after pc84; edits kart_builder.gd, style.gd, menu.gd)
The same per-wheel tables as the web (WHEEL_SPOKES / WHEEL_CAL, measured: tools/mini/patch82.py), the same "inside the tyre" limit for
the spoke class (a vertex further from the axle than the tyre's inner radius (2nd percentile) less 5% of the wheel's radius, never under
45% of it, keeps its colour: the lip, the barrel, the Monster's tread blocks), the body's calipers (class 13) take the Calipers colour
(they took the accent's, and pc84 the rims'). The style shop gets a Calipers row (slot "cl", the trim list).
"""
G = 'D:/crust-rush/godot/scripts/'


def rep(f, a, b, n=1):
    p = G + f
    s = open(p, encoding='utf-8', newline='').read()
    assert s.count(a) == n, (f, s.count(a), a[:80])
    s = s.replace(a, b)
    open(p, 'w', encoding='utf-8', newline='').write(s)


rep('kart_builder.gd', '''		var rmc: Dictionary = S.pick(spec, "rm")
		if rmc["h"] != null:
			for ci in [7, 10, 11, 15, 19, 21]:   # (pc72: the rims, web rimVC)
				rimre[ci] = Color(String(rmc["h"]))
				rimpbr[ci] = [float(rmc.get("r", 0.2)), 0.95] if rmc.has("m") else [0.38, 0.3]
			rimc = Color(String(rmc["h"]))
			for ci in [16, 17, 18, 19]:   # (pc84, web patch 82: a kart's wheel set: its spokes' own colour classes)
				rimall[ci] = rimc
				rimallpbr[ci] = [float(rmc.get("r", 0.2)), 0.95] if rmc.has("m") else [0.38, 0.3]
			rimall[13] = rimc   # (pc84: the caliper too, keeping its painted finish)
			rimre[13] = rimc
			vcre[13] = rimc   # (pc84: a car body's calipers: the rims' colour, not the accent's)
''', '''		# (pc85, web patch 82) the Rims colour on each wheel's spokes (its own class), the Calipers colour on its calipers
		var rmc: Dictionary = S.pick(spec, "rm")
		var clc: Dictionary = S.pick(spec, "cl")
		var bid := String(info["bodies"][int(spec.get("b", 0))]["id"])
		var wid := String(wheel_of(spec).get("id", ""))
		if rmc["h"] != null:
			rimc = Color(String(rmc["h"]))
			var fin: Array = [float(rmc.get("r", 0.2)), 0.95] if rmc.has("m") else [0.38, 0.3]
			for ci in WHEEL_SPOKES.get(bid, [11]):
				rimre[ci] = rimc
				rimpbr[ci] = fin
			for ci in WHEEL_SPOKES.get(wid, []):
				rimall[ci] = rimc
				rimallpbr[ci] = fin
		if clc["h"] != null:
			var cc := Color(String(clc["h"]))
			vcre[13] = cc   # a car body's calipers
			for ci in WHEEL_CAL.get(wid, []):
				rimall[ci] = cc
''')
rep('kart_builder.gd', '''"rimc": rimc, "rimm": S.pick(spec, "rm") if spec.get("st") is Dictionary else {}}''',
    '''"rimc": rimc, "rimm": S.pick(spec, "rm") if spec.get("st") is Dictionary else {},
		"cut": WHEEL_SPOKES.get(String(info["bodies"][int(spec.get("b", 0))]["id"]), [11]), "cutw": WHEEL_SPOKES.get(String(wheel_of(spec).get("id", "")), [])}


## (pc85, web patch 82 WHEEL_SPOKES / WHEEL_CAL) each wheel's spokes and calipers: its colour classes, measured; not listed: spokes 11
const WHEEL_SPOKES := {"suv": [10], "retrogt": [10], "concept": [1], "chariot": [1], "skywing": [6], "bike_mx": [10], "bike_moto": [10],
	"rollpin": [21], "grater": [21], "comet": [21], "oilcan": [21], "redline": [17], "emerald": [16], "stealth": [16], "turbo": [18], "forged": [19]}
const WHEEL_CAL := {"forged": [17]}''')
rep('kart_builder.gd', '''const CAR_BASE := {1: "#161618", 6: "#161618", 15: "#3b3e44", 2: "#ffffff", 13: "#c8321e", 17: "#c0180c", 9: "#1c1918",''',
    '''const CAR_BASE := {1: "#161618", 6: "#161618", 15: "#3b3e44", 2: "#ffffff", 13: "#c8321e", 17: "#c0180c", 9: "#1c1918", 16: "#3f9a1a", 18: "#1d7fe6",''')
# the spokes' limit: inside the tyre
rep('kart_builder.gd', '''				if not re.is_empty():
					_style_vc(m3, si, re)''', '''				if not re.is_empty():
					_style_vc(m3, si, re, (cols.get("cutw" if wset else "cut", []) as Array) if wheel else [])''')
rep('kart_builder.gd', '''static func _style_vc(m3: MeshInstance3D, si: int, re: Dictionary) -> void:''',
    '''static func _style_vc(m3: MeshInstance3D, si: int, re: Dictionary, cut_cls: Array = []) -> void:''')
rep('kart_builder.gd', '''	var key := "%d|%d" % [mesh.get_rid().get_id(), si]''', '''	var key := "%d|%d|%s" % [mesh.get_rid().get_id(), si, str(cut_cls)]''')
rep('kart_builder.gd', '''				var cs: PackedColorArray = arr[Mesh.ARRAY_COLOR]
				var uv: PackedVector2Array = arr[Mesh.ARRAY_TEX_UV]
				for q in cs.size():
					var ci := int(uv[q].x * 32.0)
					if re.has(ci):''', '''				var cs: PackedColorArray = arr[Mesh.ARRAY_COLOR]
				var uv: PackedVector2Array = arr[Mesh.ARRAY_TEX_UV]
				# (pc85, web rimVC uCut) a wheel's spoke class only inside the tyre: its lip and barrel are the same class
				var cut := 1e9
				var vx: PackedVector3Array = arr[Mesh.ARRAY_VERTEX]
				if not cut_cls.is_empty():
					var rr: Array = []
					var rm := 0.0
					for q in vx.size():
						var d := Vector2(vx[q].x, vx[q].y).length()
						rm = maxf(rm, d)
						if int(uv[q].x * 32.0) == 8:
							rr.append(d)
					if rr.size() > 20:
						rr.sort()
						cut = maxf(0.45 * rm, float(rr[int(rr.size() * 0.02)]) - 0.05 * rm)
				for q in cs.size():
					var ci := int(uv[q].x * 32.0)
					if re.has(ci) and not (cut_cls.has(ci) and Vector2(vx[q].x, vx[q].y).length() >= cut):''')
rep('style.gd', '''"rm": ["tr", TRIMS], "gl"''', '''"rm": ["tr", TRIMS], "cl": ["tr", TRIMS], "gl"''')
rep('menu.gd', '''["rm", "Rims"], ["gl", "Underglow"]''', '''["rm", "Rims"], ["cl", "Calipers"], ["gl", "Underglow"]''')
print('pc85 applied')
