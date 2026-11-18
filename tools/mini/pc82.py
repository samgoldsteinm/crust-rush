"""The PC side of web patch 82 (v224): the rim colour paints a kart's whole wheel.
    py.cmd tools/mini/pc82.py      (once, after pc81; edits D:/crust-rush/godot/scripts/kart_builder.gd)
A kart's wheel set (wsrc, an imported car_vc mesh) is recoloured on every class but the tyre (8) and the caliper (13) (rimall); a car's
own wheels keep the metal classes (rimre). A code-built wheel exported from the web (its rim g_dark, its spokes g_paint) takes the rim
colour on both when one is chosen.
"""
G = 'D:/crust-rush/godot/scripts/'


def rep(f, a, b, n=1):
    p = G + f
    s = open(p, encoding='utf-8', newline='').read()
    assert s.count(a) == n, (f, s.count(a), a[:80])
    s = s.replace(a, b)
    open(p, 'w', encoding='utf-8', newline='').write(s)


rep('kart_builder.gd', '''	var rimre := {}
	var rimpbr := {}
''', '''	var rimre := {}
	var rimpbr := {}
	var rimall := {}
	var rimallpbr := {}
	var rimc = null
''')
rep('kart_builder.gd', '''				rimpbr[ci] = [float(rmc.get("r", 0.2)), 0.95] if rmc.has("m") else [0.38, 0.3]
''', '''				rimpbr[ci] = [float(rmc.get("r", 0.2)), 0.95] if rmc.has("m") else [0.38, 0.3]
			rimc = Color(String(rmc["h"]))
			for ci in 23:   # (pc82, web patch 82: a kart's wheel set: all but the tyre and the caliper)
				if ci != 8 and ci != 13:
					rimall[ci] = rimc
					rimallpbr[ci] = [float(rmc.get("r", 0.2)), 0.95] if rmc.has("m") else [0.38, 0.3]
''')
rep('kart_builder.gd', '''"rimre": rimre, "rimpbr": rimpbr}''', '''"rimre": rimre, "rimpbr": rimpbr, "rimall": rimall, "rimallpbr": rimallpbr, "rimc": rimc, "rimm": S.pick(spec, "rm") if spec.get("st") is Dictionary else {}}''')
rep('kart_builder.gd', '''			_paint(wm, cols, null, ri, false, true)   # (pc72: a wheel takes the rims' colour, never the trim's)''',
    '''			_paint(wm, cols, null, ri, false, true, not own)   # (pc72: a wheel takes the rims' colour, never the trim's; pc82: a kart's wheel set all over)''')
rep('kart_builder.gd', '''static func _paint(n: Node, cols: Dictionary, liv, ri: int, cloth := false, wheel := false) -> void:''',
    '''static func _paint(n: Node, cols: Dictionary, liv, ri: int, cloth := false, wheel := false, wset := false) -> void:''')
rep('kart_builder.gd', '''				var re: Dictionary = cols.get("rimre" if wheel else "vcre", {})
				var pbr: Dictionary = cols.get("rimpbr" if wheel else "vcpbr", {})''', '''				var re: Dictionary = cols.get(("rimall" if wset else "rimre") if wheel else "vcre", {})
				var pbr: Dictionary = cols.get(("rimallpbr" if wset else "rimpbr") if wheel else "vcpbr", {})''')
rep('kart_builder.gd', '''			if nm.begins_with("g_paint"):
				var wrap''', '''			if wheel and cols.get("rimc") != null and (nm.begins_with("g_dark") or nm.begins_with("g_paint")):
				# (pc82, web patch 82) a code-built wheel: its rim and spokes take the rim colour
				var rmm: Dictionary = cols.get("rimm", {})
				var rw := StandardMaterial3D.new()
				rw.albedo_color = cols["rimc"]
				rw.vertex_color_use_as_albedo = true
				rw.metallic = 0.95 if rmm.has("m") else 0.3
				rw.roughness = float(rmm.get("r", 0.2)) if rmm.has("m") else 0.38
				m3.set_surface_override_material(si, rw)
			elif nm.begins_with("g_paint"):
				var wrap''')
print('pc82 applied')
