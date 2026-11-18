"""PC: web patches 87-90 (v227): calipers that do not roll, the Accent colour on every vehicle, more combos and your own combos.
    py.cmd tools/mini/pc86.py      (once, after pc85; edits tools/glbexport.js, kart_builder.gd, view.gd, style.gd, menu.gd)
- glbexport.js: a wheel's held part (web patch 88: caliper, hub carrier, strut, kept in the steering group) goes out as its own node,
  ph<i> beside pw<i> (a car's own wheels) and hold_L / hold_R beside wheel_L / wheel_R (wheel types); __placeBW no longer lists it as
  an axle piece. The Classic's slice (87) and the karts' accent spots (89, materials g_acc) come with the export as they are.
- kart_builder: the held part in a 'wheel_XX_hold' node at the wheel's place (it steers, it does not roll), painted as the web's
  holdOut: its caliper classes (13, the pack's own, the wheel's spoke classes) take the Calipers colour. Accent: the chrome trim (10) and
  carbon (6, not the Slip's) and ACC_X's class too (web patch 89); g_acc parts take the accent.
- view.gd: a front wheel's held part turns with the steering.
- style.gd / menu.gd: COMBOS 10..29 as the web (KEEP THE ORDER), "only" ones first and starred for their vehicles; the Calipers chip;
  My combos (user://mycombos.json, up to 12): save this look, wear one on any vehicle (a livery made for another vehicle stays off, a
  colour not owned is stock), delete (a second press confirms).
"""
G = 'D:/crust-rush/godot/'


def rep(f, a, b, n=1):
    p = G + f
    s = open(p, encoding='utf-8', newline='').read()
    assert s.count(a) == n, (f, s.count(a), a[:80])
    s = s.replace(a, b)
    open(p, 'w', encoding='utf-8', newline='').write(s)


# ---- the exporter
rep('tools/glbexport.js', """    const pr=parts(G,sp,sp.matrixWorld,null);if(pr.length){const nm='pw'+i;top.push(G.node(nm,pr));pw.push(nm);}});""",
    """    const pr=parts(G,sp,sp.matrixWorld,null);if(pr.length){const nm='pw'+i;top.push(G.node(nm,pr));pw.push(nm);}
    /* (pc86, web patch 88) the wheel's held part (caliper, hub carrier): in the same space, its own node */
    const ph=[];for(const h of yaw.children)if(h.userData.held)ph.push(...parts(G,h,sp.matrixWorld,null));if(ph.length)top.push(G.node('ph'+i,ph));});""")
rep('tools/glbexport.js', """    const pr=parts(G,wh,wh.matrixWorld,null);if(pr.length)top.push(G.node('wheel_'+side,pr));});""",
    """    const pr=parts(G,wh,wh.matrixWorld,null);if(pr.length)top.push(G.node('wheel_'+side,pr));
    const ph=[];for(const h of yaw.children)if(h.userData.held)ph.push(...parts(G,h,wh.matrixWorld,null));if(ph.length)top.push(G.node('hold_'+side,ph));/* (pc86) */});""")
rep('tools/glbexport.js', "yaw.children.forEach(c=>{if(c!==sp&&c.isMesh)ax.push(", "yaw.children.forEach(c=>{if(c!==sp&&c.isMesh&&!c.userData.held)ax.push(")

rep('tools/glbexport.js', """else if(near(m.color,st)){m.vertexColors=true;m.name='g_stripe';}}});};""",
    """else if(near(m.color,st)){m.vertexColors=true;m.name='g_stripe';}else if(m.name==='g_acc'){m.vertexColors=true;}/* (pc86: a kart's accent spot stays its own material) */}});};""")

# ---- kart_builder: held parts, accent
K = 'scripts/kart_builder.gd'
rep(K, """		if wm != null:
			yaw.add_child(wm)
			_paint(wm, cols, null, ri, false, true, not own)   # (pc72: a wheel takes the rims' colour, never the trim's; pc82: a kart's wheel set all over)""",
    """		if wm != null:
			yaw.add_child(wm)
			_paint(wm, cols, null, ri, false, true, not own)   # (pc72: a wheel takes the rims' colour, never the trim's; pc82: a kart's wheel set all over)
			# (pc86, web patch 88 holdOut) the caliper / hub carrier: beside the wheel, it steers but does not roll
			var hsrc: Node3D = null
			if own:
				hsrc = bsrc.find_child("ph%d" % int(wq["i"]), true, false) as Node3D
			elif wsrc != null:
				hsrc = wsrc.find_child("hold_" + ("L" if z < 0.0 else "R"), true, false) as Node3D
				if hsrc == null:
					hsrc = wsrc.find_child("hold_R", true, false) as Node3D
			if hsrc != null:
				var hn := Node3D.new()
				hn.name = nm + "_hold"
				hn.position = yaw.position
				root.add_child(hn)
				var hm := hsrc.duplicate() as Node3D
				hm.transform = wm.transform
				hn.add_child(hm)
				_paint(hm, hold_cols(cols, spec, String(bd["id"]) if own else String(wd["id"])), null, ri, false, true, not own)""")
rep(K, """## (pc85, web patch 82 WHEEL_SPOKES / WHEEL_CAL) each wheel's spokes and calipers""",
    """## (pc86, web patch 88) a held part's colours: its caliper classes (13, the pack's own HOLD_K, the wheel's calipers and spoke classes)
## take the Calipers colour; nothing else is repainted
const HOLD_K := {"monster": [12, 11], "muscle": [12], "retrogt": [7], "hatch": [9]}
static func hold_cols(cols: Dictionary, spec: Dictionary, hid: String) -> Dictionary:
	var c := cols.duplicate()
	var re := {}
	var clc: Dictionary = preload("res://scripts/style.gd").pick(spec, "cl")
	if spec.get("st") is Dictionary and clc["h"] != null:
		var cl: Array = [13]
		for ci in HOLD_K.get(hid, []) + WHEEL_CAL.get(hid, []) + WHEEL_SPOKES.get(hid, [11]):
			if not cl.has(ci):
				cl.append(ci)
		for ci in cl.slice(0, 4):
			re[ci] = Color(String(clc["h"]))
	c["rimre"] = re
	c["rimall"] = re
	c["rimpbr"] = {}
	c["rimallpbr"] = {}
	c["cut"] = []
	c["cutw"] = []
	return c


## (pc86, web patch 89 ACC_X / ACC_NO6) a body's own extra accent class; the Slip's carbon is most of its body
const ACC_X := {"bike_neutron": 7, "bike_mx": 7, "bike_rocket": 7, "retrogt": 7, "coupe": 1, "concept": 1, "muscle": 1, "slip": 1}
const ACC_NO6 := ["slip"]


## (pc85, web patch 82 WHEEL_SPOKES / WHEEL_CAL) each wheel's spokes and calipers""")
rep(K, """		if ac["h"] != null:
			stripe = Color(String(ac["h"]))
			for ci in [2, 13, 17]:
				vcre[ci] = stripe""",
    """		if ac["h"] != null:
			stripe = Color(String(ac["h"]))
			# (pc86, web patch 89) also the chrome trim and the carbon (ahead of the trim colour), and the body's own extra class
			var abid := String(info["bodies"][int(spec.get("b", 0))]["id"])
			var acl: Array = [2, 13, 17, 10]
			if not ACC_NO6.has(abid):
				acl.append(6)
			if ACC_X.has(abid):
				acl.append(int(ACC_X[abid]))
			for ci in acl:
				vcre[ci] = stripe
				vcpbr.erase(ci)""")
rep(K, """	return {"paint": col, "dark": dark, "stripe": stripe, "lv": lv,""",
    """	var accm: Dictionary = {}
	var acc_c = null
	if spec.get("st") is Dictionary:
		accm = S.pick(spec, "ac")
		if accm["h"] != null:
			acc_c = Color(String(accm["h"]))
	return {"acc": acc_c, "accm": accm, "paint": col, "dark": dark, "stripe": stripe, "lv": lv,""")
rep(K, """			elif nm.begins_with("g_dark") or nm.begins_with("g_stripe"):""",
    """			elif nm.begins_with("g_acc"):
				# (pc86, web patch 89 accM) an accent spot on a code-built kart: its own material until an accent is picked
				if cols.get("acc") != null:
					var am := sm.duplicate() as BaseMaterial3D
					am.albedo_color = cols["acc"]
					am.albedo_texture = null
					var amm: Dictionary = cols.get("accm", {})
					am.metallic = 0.9 if amm.has("m") else 0.35
					am.roughness = float(amm.get("r", 0.22)) if amm.has("m") else 0.32
					m3.set_surface_override_material(si, am)
			elif nm.begins_with("g_dark") or nm.begins_with("g_stripe"):""")
# repaint(): a held part keeps the hold colours (it begins with wheel_ too)
rep(K, """		elif nm.begins_with("wheel_"):
			_paint(c, cols, null, ri, false, true)""",
    """		elif nm.ends_with("_hold"):
			pass   # (pc86) a held part: painted when built
		elif nm.begins_with("wheel_"):
			_paint(c, cols, null, ri, false, true)""")

# ---- view.gd: a front wheel's held part steers
rep('scripts/view.gd', """			wheels.append({"node": wn, "r": float(wd["r"]), "front": bool(wd["front"])})""",
    """			wheels.append({"node": wn, "r": float(wd["r"]), "front": bool(wd["front"]), "hold": model.find_child(String(wd["name"]) + "_hold", true, false)})   # (pc86: the caliper)""")
rep('scripts/view.gd', """			if w["front"]:
				n.rotation.y = -k.steer * 0.42""",
    """			if w["front"]:
				n.rotation.y = -k.steer * 0.42
				var hd = w.get("hold")
				if hd != null:
					(hd as Node3D).rotation.y = -k.steer * 0.42   # (pc86: the caliper steers, it does not roll)""")

# ---- style.gd: the combos as the web's (patch 90), and My combos
rep('scripts/style.gd', """	{"n": "Spectrum", "p": 5, "st": {"tr": 1, "ac": 10, "in": 1, "rm": 17, "gl": 8, "hl": 4, "sm": 8}, "c": 1200}]""",
    """	{"n": "Spectrum", "p": 5, "st": {"tr": 1, "ac": 10, "in": 1, "rm": 17, "gl": 8, "hl": 4, "sm": 8}, "c": 1200},
	# (pc86, web patch 90) ten more for every vehicle, then ten made for one kind ("only": its body ids)
	{"n": "Blackout", "p": 23, "st": {"tr": 1, "ac": 1, "in": 1, "rm": 1, "cl": 1, "gl": 0, "hl": 1, "sm": 1}, "c": 200},
	{"n": "Sunburst", "p": 11, "st": {"tr": 1, "ac": 1, "in": 1, "rm": 1, "cl": 4, "gl": 6, "hl": 3, "sm": 6}, "c": 350},
	{"n": "Racing Green", "p": 13, "st": {"tr": 1, "ac": 16, "in": 11, "rm": 16, "cl": 16, "gl": 0, "hl": 0, "sm": 0}, "c": 400},
	{"n": "Sky Rocket", "p": 15, "st": {"tr": 2, "ac": 5, "in": 1, "rm": 2, "cl": 5, "gl": 1, "hl": 1, "sm": 2}, "c": 450},
	{"n": "Teal Wave", "p": 14, "st": {"tr": 2, "ac": 2, "in": 2, "rm": 3, "cl": 5, "gl": 1, "hl": 2, "sm": 2}, "c": 450},
	{"n": "Copper Sunset", "p": 18, "st": {"tr": 1, "ac": 6, "in": 11, "rm": 15, "cl": 6, "gl": 6, "hl": 3, "sm": 6}, "c": 500},
	{"n": "Grape Soda", "p": 6, "st": {"tr": 1, "ac": 10, "in": 9, "rm": 3, "cl": 10, "gl": 2, "hl": 4, "sm": 4}, "c": 500},
	{"n": "Lime Rush", "p": 12, "st": {"tr": 1, "ac": 1, "in": 12, "rm": 1, "cl": 12, "gl": 4, "hl": 5, "sm": 5}, "c": 500},
	{"n": "Ice Queen", "p": 22, "st": {"tr": 3, "ac": 13, "in": 2, "rm": 17, "cl": 13, "gl": 1, "hl": 2, "sm": 0}, "c": 550},
	{"n": "Navy Brass", "p": 16, "st": {"tr": 2, "ac": 16, "in": 11, "rm": 15, "cl": 16, "gl": 0, "hl": 0, "sm": 0}, "c": 600},
	{"n": "Pursuit", "p": 23, "st": {"tr": 2, "ac": 2, "in": 1, "rm": 3, "cl": 8, "gl": 0, "hl": 2, "sm": 0}, "c": 400, "only": ["interceptor"]},
	{"n": "Mud Slinger", "p": 13, "st": {"tr": 1, "ac": 6, "in": 1, "rm": 1, "cl": 6, "gl": 6, "hl": 3, "sm": 1}, "c": 400, "only": ["monster"]},
	{"n": "Steam Baron", "p": 18, "st": {"tr": 15, "ac": 16, "in": 11, "rm": 15, "cl": 16, "gl": 6, "hl": 3, "sm": 0}, "c": 500, "only": ["chariot"]},
	{"n": "Pit Lane", "p": 1, "st": {"tr": 1, "ac": 2, "in": 1, "rm": 1, "cl": 4, "gl": 0, "hl": 1, "sm": 0}, "c": 350, "only": ["formula", "gokart", "rollpin"]},
	{"n": "Night Stint", "p": 16, "st": {"tr": 1, "ac": 6, "in": 1, "rm": 1, "cl": 6, "gl": 1, "hl": 3, "sm": 0}, "c": 450, "only": ["endur", "retrogt", "gt"]},
	{"n": "Grand Tour", "p": 17, "st": {"tr": 17, "ac": 17, "in": 11, "rm": 17, "cl": 1, "gl": 0, "hl": 0, "sm": 0}, "c": 600, "only": ["coupe", "tourer", "suv"]},
	{"n": "Pizza Rider", "p": 2, "st": {"tr": 1, "ac": 6, "in": 1, "rm": 1, "cl": 6, "gl": 0, "hl": 3, "sm": 3}, "c": 400, "only": ["bike_moto", "bike_mx", "bike_neutron", "bike_june", "bike_rocket"]},
	{"n": "Hypersonic", "p": 21, "st": {"tr": 1, "ac": 13, "in": 1, "rm": 14, "cl": 13, "gl": 1, "hl": 2, "sm": 2}, "c": 550, "only": ["hyper", "skywing", "megawatt", "megagt", "scissor", "onyx", "concept", "slip"]},
	{"n": "Cheese Wheel", "p": 3, "st": {"tr": 4, "ac": 2, "in": 4, "rm": 2, "cl": 4, "gl": 6, "hl": 3, "sm": 6}, "c": 350, "only": ["classic", "wedge", "tomato", "delivery", "cutter", "oven", "grater", "comet", "oilcan", "rocket"]},
	{"n": "Heritage", "p": 10, "st": {"tr": 1, "ac": 2, "in": 11, "rm": 17, "cl": 1, "gl": 0, "hl": 0, "sm": 0}, "c": 450, "only": ["muscle", "roadster", "hatch", "interceptor"]}]
const MY_PATH := "user://mycombos.json"


## (pc86, web patch 90) your own combos: [{n, p, t, st}], up to 12
static func my_combos() -> Array:
	var out: Array = []
	if FileAccess.file_exists(MY_PATH):
		var j = JSON.parse_string(FileAccess.get_file_as_string(MY_PATH))
		if j is Array:
			for c in j:
				if c is Dictionary and (c as Dictionary).get("st") is Dictionary:
					out.append(c)
	return out


static func my_combos_put(a: Array) -> void:
	var f := FileAccess.open(MY_PATH, FileAccess.WRITE)
	if f:
		f.store_string(JSON.stringify(a.slice(0, 12)))""")

# ---- menu.gd: the shop's combos for this vehicle (its own first, starred), the Calipers chip, My combos
M = 'scripts/menu.gd'
rep(M, """	for ci in S.COMBOS.size():
		var cb: Dictionary = S.COMBOS[ci]""",
    """	var cbid := String((KartBuilder.info["bodies"][int(build["b"])] as Dictionary)["id"])
	var corder: Array = []
	for pass_i in 2:   # (pc86, web patch 90) this vehicle's own combos first, then the rest; another vehicle's own are not shown
		for ci0 in S.COMBOS.size():
			var oc = (S.COMBOS[ci0] as Dictionary).get("only")
			if (pass_i == 0 and oc is Array and (oc as Array).has(cbid)) or (pass_i == 1 and not (oc is Array)):
				corder.append(ci0)
	for ci: int in corder:
		var cb: Dictionary = S.COMBOS[ci]""")
rep(M, """		bt.text = "%s\\n%s" % [String(cb["n"]), ("Free" if int(cb["c"]) == 0 else "Owned") if cown else "%d coins" % int(cb["c"])]""",
    """		bt.text = "%s%s\\n%s" % ["★ " if cb.has("only") else "", String(cb["n"]), ("Free" if int(cb["c"]) == 0 else "Owned") if cown else "%d coins" % int(cb["c"])]""")
rep(M, """		for k in ["tr", "ac", "rm", "gl"]:
			var it2: Dictionary = (S.SLOTS[k][1] as Array)[int(cst[k])]""",
    """		for k in ["tr", "ac", "rm", "cl", "gl"]:
			var it2: Dictionary = (S.SLOTS[k][1] as Array)[int(cst.get(k, 0))]""")
rep(M, """	outer.add_child(cg)
	for row in [["tr", "Trim"], ["ac", "Accent"],""",
    """	outer.add_child(cg)
	_my_combos(outer, st)
	for row in [["tr", "Trim"], ["ac", "Accent"],""")
rep(M, """var _style_ask := \"\"
""", """var _style_ask := \"\"


## (pc86, web patch 90 myCards) My combos: press one to wear it on this vehicle, x to delete (a second press confirms), + to save this look
func _my_combos(outer: VBoxContainer, st: Dictionary) -> void:
	var S := preload("res://scripts/style.gd")
	outer.add_child(section_label("My combos"))
	var mg := GridContainer.new()
	mg.columns = 3
	mg.add_theme_constant_override("h_separation", zi(8))
	mg.add_theme_constant_override("v_separation", zi(8))
	var mine: Array = S.my_combos()
	for mi in mine.size():
		var c: Dictionary = mine[mi]
		var cst: Dictionary = c["st"]
		var on := int(build.get("p", -1)) == int(c.get("p", 0)) and String(build.get("t", "")) == String(c.get("t", ""))
		for k in S.SLOTS:
			on = on and int(st.get(k, 0)) == int(cst.get(k, 0))
		var row := HBoxContainer.new()
		row.add_theme_constant_override("separation", zi(2))
		var bt := Button.new()
		bt.custom_minimum_size = Vector2(z(118), z(58))
		bt.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		bt.clip_text = true
		bt.text = "%s\\n%s" % [String(c.get("n", "My combo")), "Livery" if String(c.get("t", "")) != "" else "Saved"]
		bt.set_meta("gkey", "my:%d" % mi)
		var pls: Array = KartBuilder.info.get("paints", [])
		var pc = pls[int(c.get("p", 0))] if int(c.get("p", 0)) < pls.size() else null
		var chips: Array = [Color(String(pc)) if pc != null else Color("#555555")]
		for k in ["tr", "ac", "rm", "cl", "gl"]:
			var L: Array = S.SLOTS[k][1]
			var it2: Dictionary = L[clampi(int(cst.get(k, 0)), 0, L.size() - 1)]
			if it2["h"] != null and String(it2["h"]) != "rainbow":
				chips.append(Color(String(it2["h"])).darkened(0.25))
		var cbx := box(chips, 120.0, 12.0, CHEESE if on else Color(1, 0.957, 0.863, 0.25), 3.0 if on else 1.5)
		for s2 in ["normal", "hover", "pressed", "hover_pressed", "focus"]:
			bt.add_theme_stylebox_override(s2, cbx)
		bt.add_theme_font_override("font", f_bold)
		bt.add_theme_font_size_override("font_size", zi(13))
		bt.add_theme_color_override("font_color", Color("#fff4dc"))
		bt.add_theme_color_override("font_outline_color", Color("#1a0e08"))
		bt.add_theme_constant_override("outline_size", zi(5))
		var mix := mi
		bt.pressed.connect(func(): _my_wear(mix))
		row.add_child(bt)
		var dx := Button.new()
		dx.text = "×"
		dx.custom_minimum_size = Vector2(z(26), z(26))
		dx.size_flags_vertical = Control.SIZE_SHRINK_BEGIN
		dx.tooltip_text = "Delete"
		dx.set_meta("gkey", "myx:%d" % mi)
		dx.pressed.connect(func():
			var M2: Array = S.my_combos()
			if mix >= M2.size():
				return
			if _style_ask != "md%d" % mix:
				_style_ask = "md%d" % mix
				setting_changed.emit("toast", "Press × on %s again to delete it." % String((M2[mix] as Dictionary).get("n", "this combo")))
				return
			_style_ask = ""
			M2.remove_at(mix)
			S.my_combos_put(M2)
			_build_changed())
		row.add_child(dx)
		mg.add_child(row)
	if mine.size() < 12:
		var sv := Button.new()
		sv.custom_minimum_size = Vector2(z(118), z(58))
		sv.text = "+\\nSave this look"
		sv.set_meta("gkey", "mysave")
		sv.add_theme_font_override("font", f_bold)
		sv.add_theme_font_size_override("font_size", zi(13))
		sv.pressed.connect(func():
			var M3: Array = S.my_combos()
			if M3.size() >= 12:
				setting_changed.emit("toast", "You can keep 12 combos. Delete one first.")
				return
			var nm := "My look %d" % (M3.size() + 1)
			M3.append({"n": nm, "p": int(build.get("p", 0)), "t": String(build.get("t", "")), "st": (build.get("st", {}) as Dictionary).duplicate() if build.get("st") is Dictionary else {}})
			S.my_combos_put(M3)
			setting_changed.emit("toast", "Saved %s. Wear it on any vehicle from My combos." % nm)
			_build_changed())
		mg.add_child(sv)
	outer.add_child(mg)


## (pc86, web myWear) put a saved combo on the vehicle in the garage
func _my_wear(i: int) -> void:
	var S := preload("res://scripts/style.gd")
	var M: Array = S.my_combos()
	if i < 0 or i >= M.size():
		return
	var c: Dictionary = M[i]
	var bid := String((KartBuilder.info["bodies"][int(build["b"])] as Dictionary)["id"])
	var t := String(c.get("t", ""))
	var lv := KartBuilder.livery(t) if t != "" else {}
	var lv_ok := not lv.is_empty() and (not lv.has("only") or String(lv["only"]) == bid)
	var nst := {}
	var lost := 0
	var cst: Dictionary = c["st"]
	for k in S.SLOTS:
		var v := int(cst.get(k, 0))
		if v != 0 and not S.is_owned(k, v):
			lost += 1
			continue
		if v != 0:
			nst[k] = v
	var pls: Array = KartBuilder.info.get("paints", [])
	build["p"] = clampi(int(c.get("p", 0)), 0, maxi(0, pls.size() - 1))
	build["t"] = t if lv_ok else ""
	build["st"] = nst
	_build_changed()
	if t != "" and not lv_ok:
		setting_changed.emit("toast", "%s: its livery is made for another vehicle, so its paint and colours went on." % String(c.get("n", "Your combo")))
	elif lost > 0:
		setting_changed.emit("toast", "Some of %s's colours are not yours yet: those parts are stock." % String(c.get("n", "this combo")))
""")
print('pc86 applied')
