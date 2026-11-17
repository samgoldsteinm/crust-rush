"""The PC side of web patches 72-73 (v222): trim that looks like its colour (silver, chrome, gold shine), trim kept off the wheels, a Rims
row, interior metal that is not a black mirror, and the colour combos.
    py.cmd tools/mini/pc72.py      (once; edits D:/crust-rush/godot/scripts)
The owner: "the silver doesnt look silver at all on the trim pieces" (the PC repainted trim's vertex colour only: the parts kept their
satin plastic finish, so silver was flat grey) and "trim also shouldnt change the rim color we should jsut have a color section for rims"
(the PC repainted every car_vc mesh, the wheels too).
- kart_builder.colours(): vcre (body: trim on dark, carbon, metal, gunmetal; accent; interior) and vcpbr (class -> [roughness, metalness]
  for a metal trim colour and interior metal), rimre / rimpbr for the wheels' metal classes. _paint(..., wheel) uses the rim ones on a
  wheel, the body ones elsewhere; car_vc_mat_pbr(over) a cached copy of the parts' material with those classes' lookup pixels changed.
- style.gd: "rm" (Rims) shares the trim list; COMBOS (web patch 73, the same order), combo_owned / combo_allows / combo_buy; is_owned
  counts a bought combo's piece in its own slot.
- menu.gd: the Combos grid at the top of the style shop and the Rims row.
"""
G = 'D:/crust-rush/godot/scripts/'


def rep(f, a, b, n=1):
    p = G + f
    s = open(p, encoding='utf-8', newline='').read()
    assert s.count(a) == n, (f, s.count(a), a[:80])
    s = s.replace(a, b)
    open(p, 'w', encoding='utf-8', newline='').write(s)


# ---------------------------------------------------------------- style.gd
rep('style.gd', 'const SLOTS := {"tr": ["tr", TRIMS], "ac": ["tr", TRIMS], "in": ["tr", TRIMS], "gl": ["gl", GLOWS],',
    'const SLOTS := {"tr": ["tr", TRIMS], "ac": ["tr", TRIMS], "in": ["tr", TRIMS], "rm": ["tr", TRIMS], "gl": ["gl", GLOWS],')
rep('style.gd', 'const PATH := "user://own.json"\n', '''const PATH := "user://own.json"
## web patch 73's colour combos: p a paint (the garage's paint list), st the style; p price (0 free). KEEP THE WEB'S ORDER ("cb" + index)
const COMBOS := [{"n": "Stealth", "p": 8, "st": {"tr": 1, "ac": 1, "in": 1, "rm": 1, "gl": 0, "hl": 1, "sm": 0}, "c": 0},
	{"n": "Track Day", "p": 1, "st": {"tr": 1, "ac": 2, "in": 1, "rm": 3, "gl": 0, "hl": 1, "sm": 0}, "c": 0},
	{"n": "Arctic", "p": 9, "st": {"tr": 3, "ac": 13, "in": 2, "rm": 3, "gl": 1, "hl": 2, "sm": 0}, "c": 350},
	{"n": "Midnight Neon", "p": 8, "st": {"tr": 14, "ac": 13, "in": 1, "rm": 14, "gl": 1, "hl": 2, "sm": 2}, "c": 450},
	{"n": "Toxic", "p": 4, "st": {"tr": 1, "ac": 12, "in": 12, "rm": 1, "gl": 4, "hl": 5, "sm": 5}, "c": 500},
	{"n": "Miami", "p": 7, "st": {"tr": 2, "ac": 13, "in": 2, "rm": 2, "gl": 5, "hl": 1, "sm": 7}, "c": 550},
	{"n": "Inferno", "p": 2, "st": {"tr": 1, "ac": 4, "in": 4, "rm": 15, "gl": 3, "hl": 3, "sm": 3}, "c": 600},
	{"n": "Royal Gold", "p": 6, "st": {"tr": 16, "ac": 16, "in": 11, "rm": 16, "gl": 2, "hl": 0, "sm": 4}, "c": 650},
	{"n": "Chrome King", "p": 8, "st": {"tr": 17, "ac": 17, "in": 1, "rm": 17, "gl": 7, "hl": 1, "sm": 1}, "c": 900},
	{"n": "Spectrum", "p": 5, "st": {"tr": 1, "ac": 10, "in": 1, "rm": 17, "gl": 8, "hl": 4, "sm": 8}, "c": 1200}]


static func combo_owned(i: int) -> bool:
	if i < 0 or i >= COMBOS.size():
		return false
	return int(COMBOS[i]["c"]) == 0 or Ach.cheat or owned().has("cb%d" % i)


## a bought combo's piece, in its own slot only (web comboAllows)
static func combo_allows(slot: String, i: int) -> bool:
	if i == 0:
		return false
	var o := owned()
	for j in COMBOS.size():
		var c: Dictionary = COMBOS[j]
		if int(c["c"]) > 0 and int((c["st"] as Dictionary).get(slot, 0)) == i and o.has("cb%d" % j):
			return true
	return false


static func combo_buy(i: int) -> bool:
	if combo_owned(i):
		return true
	var sv: Dictionary = Sandbox.load_save()
	if int(sv.get("c", 0)) < int(COMBOS[i]["c"]):
		return false
	sv["c"] = int(sv["c"]) - int(COMBOS[i]["c"])
	Sandbox.keep()
	var o := owned()
	o["cb%d" % i] = true
	_put(o)
	return true
''')
rep('style.gd', """	return owned().has(String(SLOTS[slot][0]) + str(i))


## web styleBuy""", """	return owned().has(String(SLOTS[slot][0]) + str(i)) or combo_allows(slot, i)   # (pc72: a combo's piece)


## web styleBuy""")

# ---------------------------------------------------------------- kart_builder.gd
rep('kart_builder.gd', """		if t["h"] != null:
			dark = Color(String(t["h"]))
			for ci in [1, 6, 15]:
				vcre[ci] = dark
		if ac["h"] != null:
			stripe = Color(String(ac["h"]))
			for ci in [2, 13, 17]:
				vcre[ci] = stripe
		if inn["h"] != null:
			vcre[9] = Color(String(inn["h"]))
	return {"paint": col, "dark": dark, "stripe": stripe, "lv": lv, "vcre": vcre}""", """		if t["h"] != null:
			dark = Color(String(t["h"]))
			for ci in [1, 6, 7, 15]:   # (pc72: the interior's metal trim too)
				vcre[ci] = dark
				if t.has("m"):
					vcpbr[ci] = [float(t.get("r", 0.22)), 0.9]   # (pc72: silver, chrome, gold... shine as metal)
		if ac["h"] != null:
			stripe = Color(String(ac["h"]))
			for ci in [2, 13, 17]:
				vcre[ci] = stripe
		if inn["h"] != null:
			vcre[9] = Color(String(inn["h"]))
			if inn.has("m"):
				vcpbr[9] = [0.28, 0.45]   # (web patch 72: interior metal, not a black mirror)
		var rmc: Dictionary = S.pick(spec, "rm")
		if rmc["h"] != null:
			for ci in [7, 10, 11, 15, 19, 21]:   # (pc72: the rims, web rimVC)
				rimre[ci] = Color(String(rmc["h"]))
				rimpbr[ci] = [float(rmc.get("r", 0.2)), 0.95] if rmc.has("m") else [0.38, 0.3]
	return {"paint": col, "dark": dark, "stripe": stripe, "lv": lv, "vcre": vcre, "vcpbr": vcpbr, "rimre": rimre, "rimpbr": rimpbr}""")
rep('kart_builder.gd', """	var vcre := {}
	var S := preload("res://scripts/style.gd")""", """	var vcre := {}
	var vcpbr := {}
	var rimre := {}
	var rimpbr := {}
	var S := preload("res://scripts/style.gd")""")
rep('kart_builder.gd', """const CAR_BASE := {1: "#161618", 6: "#161618", 15: "#3b3e44", 2: "#ffffff", 13: "#c8321e", 17: "#c0180c", 9: "#1c1918"}""",
    """const CAR_BASE := {1: "#161618", 6: "#161618", 15: "#3b3e44", 2: "#ffffff", 13: "#c8321e", 17: "#c0180c", 9: "#1c1918",
	7: "#76777d", 10: "#e9e9ee", 11: "#b5b7be", 19: "#8a6232", 21: "#c4c7cd"}   # (pc72: the rims' and metal trim's classes)""")
rep('kart_builder.gd', """static func _paint(n: Node, cols: Dictionary, liv, ri: int, cloth := false) -> void:""",
    """static func _paint(n: Node, cols: Dictionary, liv, ri: int, cloth := false, wheel := false) -> void:""")
rep('kart_builder.gd', """				m3.set_surface_override_material(si, car_vc_mat())
				if not (cols.get("vcre", {}) as Dictionary).is_empty():
					_style_vc(m3, si, cols["vcre"])
				continue""", """				var re: Dictionary = cols.get("rimre" if wheel else "vcre", {})
				var pbr: Dictionary = cols.get("rimpbr" if wheel else "vcpbr", {})
				m3.set_surface_override_material(si, car_vc_mat_pbr(pbr) if not pbr.is_empty() else car_vc_mat())
				if not re.is_empty():
					_style_vc(m3, si, re)
				continue""")
rep('kart_builder.gd', """			_paint(wm, cols, null, ri)""", """			_paint(wm, cols, null, ri, false, true)   # (pc72: a wheel takes the rims' colour, never the trim's)""")
rep('kart_builder.gd', """		elif nm.begins_with("wheel_"):
			_paint(c, cols, null, ri)""", """		elif nm.begins_with("wheel_"):
			_paint(c, cols, null, ri, false, true)""")
rep('kart_builder.gd', """## which marker a material is:""", """## (pc72) the parts' material with some classes' roughness and metalness changed (over: class -> [roughness, metalness]), cached
static var _car_vc_pbr := {}
static func car_vc_mat_pbr(over: Dictionary) -> StandardMaterial3D:
	var ks: Array = over.keys()
	ks.sort()
	var key := ""
	for c in ks:
		key += "%d:%.2f,%.2f|" % [c, float(over[c][0]), float(over[c][1])]
	if _car_vc_pbr.has(key):
		return _car_vc_pbr[key]
	var base := car_vc_mat()
	var m := base.duplicate() as StandardMaterial3D
	var img := (base.roughness_texture as ImageTexture).get_image()
	img = img.duplicate() as Image
	for c in ks:
		img.set_pixel(int(c), 0, Color(1, float(over[c][0]), float(over[c][1]), 1))
	var rt := ImageTexture.create_from_image(img)
	m.roughness_texture = rt
	m.metallic_texture = rt
	_car_vc_pbr[key] = m
	return m


## which marker a material is:""")

# ---------------------------------------------------------------- menu.gd: the combos, the Rims row
rep('menu.gd', """	var st: Dictionary = build.get("st", {}) if build.get("st") is Dictionary else {}
	for row in [["tr", "Trim"], ["ac", "Accent"], ["in", "Interior"], ["gl", "Underglow"], ["hl", "Headlights"], ["sm", "Tyre smoke"]]:""",
    """	var st: Dictionary = build.get("st", {}) if build.get("st") is Dictionary else {}
	# (pc72, web patch 73) the combos: a whole look; a bought one's colours are yours for the parts it puts them on
	outer.add_child(section_label("Combos"))
	var cg := GridContainer.new()
	cg.columns = 3
	cg.add_theme_constant_override("h_separation", zi(8))
	cg.add_theme_constant_override("v_separation", zi(8))
	for ci in S.COMBOS.size():
		var cb: Dictionary = S.COMBOS[ci]
		var cst: Dictionary = cb["st"]
		var cown: bool = S.combo_owned(ci)
		var con := int(build.get("p", -1)) == int(cb["p"]) and String(build.get("t", "")) == ""
		for k in cst:
			con = con and int(st.get(k, 0)) == int(cst[k])
		var bt := Button.new()
		bt.custom_minimum_size = Vector2(z(150), z(58))
		bt.text = "%s\\n%s" % [String(cb["n"]), ("Free" if int(cb["c"]) == 0 else "Owned") if cown else "%d coins" % int(cb["c"])]
		bt.set_meta("gkey", "cb:%d" % ci)
		var pls: Array = KartBuilder.info.get("paints", [])
		var pc = pls[int(cb["p"])] if int(cb["p"]) < pls.size() else null
		var chips: Array = [Color(String(pc)) if pc != null else Color("#555555")]
		for k in ["tr", "ac", "rm", "gl"]:
			var it2: Dictionary = (S.SLOTS[k][1] as Array)[int(cst[k])]
			if it2["h"] != null and String(it2["h"]) != "rainbow":
				chips.append(Color(String(it2["h"])).darkened(0.25))
		var cbx := box(chips, 120.0, 12.0, CHEESE if con else Color(1, 0.957, 0.863, 0.25), 3.0 if con else 1.5)
		for s2 in ["normal", "hover", "pressed", "hover_pressed", "focus"]:
			bt.add_theme_stylebox_override(s2, cbx)
		bt.add_theme_font_override("font", f_bold)
		bt.add_theme_font_size_override("font_size", zi(13))
		bt.add_theme_color_override("font_color", Color("#fff4dc"))
		bt.add_theme_color_override("font_outline_color", Color("#1a0e08"))
		bt.add_theme_constant_override("outline_size", zi(5))
		var cix := ci
		bt.pressed.connect(func():
			var c2: Dictionary = S.COMBOS[cix]
			if not S.combo_owned(cix):
				var have := int(preload("res://scripts/sandbox.gd").load_save().get("c", 0))
				if have < int(c2["c"]):
					setting_changed.emit("toast", "%s costs %d coins. You have %d. Earn coins by racing and in Sandbox." % [String(c2["n"]), int(c2["c"]), have])
					return
				if _style_ask != "cb%d" % cix:
					_style_ask = "cb%d" % cix
					setting_changed.emit("toast", "Press %s again to buy it for %d coins. Its colours are yours for the parts it puts them on." % [String(c2["n"]), int(c2["c"])])
					return
				_style_ask = ""
				S.combo_buy(cix)
			build["p"] = int(c2["p"])
			build["t"] = ""
			build["st"] = (c2["st"] as Dictionary).duplicate()
			_build_changed())
		cg.add_child(bt)
	outer.add_child(cg)
	for row in [["tr", "Trim"], ["ac", "Accent"], ["in", "Interior"], ["rm", "Rims"], ["gl", "Underglow"], ["hl", "Headlights"], ["sm", "Tyre smoke"]]:""")
print('pc72 applied')
