"""The PC side of web patches 65-67: the style shop.
    py.cmd tools/mini/pc65.py      (once; edits D:/crust-rush/godot/scripts; needs scripts/style.gd from pc68.py)
- The garage's Colour tab: under the paints, a row of swatches per slot (trim, accent, interior, underglow, headlights, tyre smoke);
  a locked one shows its price; the first press asks, a second buys (Style.buy, the Sandbox purse); the build's "st" holds the choice.
- kart_builder: colours() takes trim and accent for the code-built karts' dark and stripe; a car body's baked part colours are repainted
  in a copy of its mesh (by each vertex's class, the uv's u: dark, carbon, gunmetal -> trim; stripe, caliper, red -> accent; seat ->
  interior), keeping the baked shading (the web's styleVC does it in the shader; the same rule).
- view: the underglow is two coloured lights under the kart (Godot's lights reach the toy tracks too) and a faint additive haze; tyre
  smoke in the chosen colour, thicker, plus launch smoke (the FX smoke pool 260 -> 420); rainbow cycles. sandbox_night: the headlight
  beam in the chosen colour. CPU karts sometimes wear a glow or smoke (random_build).
"""
G = 'D:/crust-rush/godot/scripts/'


def rep(f, a, b, n=1):
    p = G + f
    s = open(p, encoding='utf-8', newline='').read()
    assert s.count(a) == n, (f, s.count(a), a[:80])
    s = s.replace(a, b)
    open(p, 'w', encoding='utf-8', newline='').write(s)


# ---------------------------------------------------------------- kart_builder: colours, the car bodies' repaint, CPU styles
rep('kart_builder.gd', """	return {"paint": col, "dark": dark, "stripe": stripe, "lv": lv}""", """	# the style shop (web patch 65): trim and accent on the code-built karts; a car body's part classes repainted (vcre: class -> colour)
	var vcre := {}
	var S := preload("res://scripts/style.gd")
	if spec.get("st") is Dictionary:
		var t: Dictionary = S.pick(spec, "tr")
		var ac: Dictionary = S.pick(spec, "ac")
		var inn: Dictionary = S.pick(spec, "in")
		if t["h"] != null:
			dark = Color(String(t["h"]))
			for ci in [1, 6, 15]:
				vcre[ci] = dark
		if ac["h"] != null:
			stripe = Color(String(ac["h"]))
			for ci in [2, 13, 17]:
				vcre[ci] = stripe
		if inn["h"] != null:
			vcre[9] = Color(String(inn["h"]))
	return {"paint": col, "dark": dark, "stripe": stripe, "lv": lv, "vcre": vcre}""")
rep('kart_builder.gd', """			if not nm.begins_with("g_") and _is_car_vc(sm, fmt):
				m3.set_surface_override_material(si, car_vc_mat())
				continue""", """			if not nm.begins_with("g_") and _is_car_vc(sm, fmt):
				m3.set_surface_override_material(si, car_vc_mat())
				if not (cols.get("vcre", {}) as Dictionary).is_empty():
					_style_vc(m3, si, cols["vcre"])
				continue""")
rep('kart_builder.gd', """static func _mat4(a: Array) -> Transform3D:""", """## the classes' own colours, as the web's CAR_PBR (the baked vertex colour is this times the shading)
const CAR_BASE := {1: "#161618", 6: "#161618", 15: "#3b3e44", 2: "#ffffff", 13: "#c8321e", 17: "#c0180c", 9: "#1c1918"}
static var _vc_cache := {}


## web styleVC (patch 65), done once on a copy of the mesh: each vertex of the chosen classes takes the new colour times its own shading
static func _style_vc(m3: MeshInstance3D, si: int, re: Dictionary) -> void:
	var mesh := m3.mesh as ArrayMesh
	if mesh == null:
		return
	var ks: Array = re.keys()
	ks.sort()
	var key := "%d|%d" % [mesh.get_rid().get_id(), si]
	for c in ks:
		key += "|%d:%s" % [c, (re[c] as Color).to_html(false)]
	var nm: ArrayMesh = _vc_cache.get(key)
	if nm == null:
		nm = ArrayMesh.new()
		for j in mesh.get_surface_count():
			var arr := mesh.surface_get_arrays(j)
			if j == si and arr[Mesh.ARRAY_COLOR] != null and arr[Mesh.ARRAY_TEX_UV] != null:
				var cs: PackedColorArray = arr[Mesh.ARRAY_COLOR]
				var uv: PackedVector2Array = arr[Mesh.ARRAY_TEX_UV]
				for q in cs.size():
					var ci := int(uv[q].x * 32.0)
					if re.has(ci):
						var b := Color(String(CAR_BASE.get(ci, "#808080"))).srgb_to_linear()
						var bm := maxf(0.004, maxf(b.r, maxf(b.g, b.b)))
						var c0: Color = cs[q]
						var ao := clampf(maxf(c0.r, maxf(c0.g, c0.b)) / bm, 0.3, 1.2)
						var t: Color = (re[ci] as Color).srgb_to_linear() * ao
						t.a = c0.a
						cs[q] = t
				arr[Mesh.ARRAY_COLOR] = cs
			nm.add_surface_from_arrays(mesh.surface_get_primitive_type(j), arr)
			nm.surface_set_material(j, mesh.surface_get_material(j))
		_vc_cache[key] = nm
	var ov: Array = []
	for j in mesh.get_surface_count():
		ov.append(m3.get_surface_override_material(j))
	m3.mesh = nm
	for j in ov.size():
		if ov[j] != null:
			m3.set_surface_override_material(j, ov[j])


static func _mat4(a: Array) -> Transform3D:""")
rep('kart_builder.gd', """		"p": 0 if randf() < 0.65 or np < 2 else 1 + randi() % (np - 1), "t": String(lv[randi() % lv.size()]["id"]) if randf() < 0.45 and not lv.is_empty() else ""}""",
    """		"p": 0 if randf() < 0.65 or np < 2 else 1 + randi() % (np - 1), "t": String(lv[randi() % lv.size()]["id"]) if randf() < 0.45 and not lv.is_empty() else "",
		# (web patch 65: CPU karts sometimes wear a glow or coloured smoke, for show)
		"st": {"gl": randi() % 9, "sm": (randi() % 9) if randf() < 0.5 else 0} if randf() < 0.3 else {}}""")

# ---------------------------------------------------------------- view: underglow, smoke
rep('view.gd', """		"held": null, "held_it": "", "rx": k.x, "ry": k.y, "rz": k.wy, "rma": k.ma, "glider": glider, "ga": 0.0}""",
    """		"held": null, "held_it": "", "rx": k.x, "ry": k.y, "rz": k.wy, "rma": k.ma, "glider": glider, "ga": 0.0}
	_style_view(k, g, info, meta)""")
rep('view.gd', """## Sandbox, at the swap between two places (main.gd _sb_adopt)""", """## the style shop's look on a kart (web patches 65-67): the underglow (two coloured lights under it and a faint haze over the ground)
## and the tyre smoke's colour (views[k]["smc"]; "rainbow" cycles)
func _style_view(k: Kart, g: Node3D, info: Dictionary, meta: Dictionary) -> void:
	var S := preload("res://scripts/style.gd")
	var spec: Dictionary = info.get("spec", {}) if info.get("spec") is Dictionary else {}
	var v: Dictionary = views[k]
	var sm: Dictionary = S.pick(spec, "sm")
	v["smc"] = String(sm["h"])
	var gi: Dictionary = S.pick(spec, "gl")
	v["ug"] = []
	v["ug_rb"] = gi["h"] != null and String(gi["h"]) == "rainbow"
	if gi["h"] == null or float(meta.get("hover", 0.0)) > 0.0:
		return
	var col := Color("#ff3030") if bool(v["ug_rb"]) else Color(String(gi["h"]))
	var sc: float = g.scale.x if g.scale.x > 0.0 else 1.0
	var axf := float(meta.get("axF", 6.0)) / sc
	var axr := float(meta.get("axR", -6.0)) / sc
	for ax in [axf * 0.55, axr * 0.55]:
		var L := OmniLight3D.new()
		L.light_color = col
		L.omni_range = 95.0
		L.omni_attenuation = 0.45
		L.light_energy = 0.0
		L.shadow_enabled = false
		L.position = Vector3(ax, 0.3, 0.0)
		g.add_child(L)
		(v["ug"] as Array).append(L)
	var q := MeshInstance3D.new()
	var pm := PlaneMesh.new()
	pm.size = Vector2((axf - axr) * 1.9 + 6.0, float(meta.get("axW", 5.0)) / sc * 3.4 + 3.0)
	q.mesh = pm
	var hm := StandardMaterial3D.new()
	hm.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	hm.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	hm.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
	hm.depth_draw_mode = BaseMaterial3D.DEPTH_DRAW_DISABLED
	hm.albedo_texture = _ug_tex()
	hm.albedo_color = Color(col.r, col.g, col.b, 0.3)
	hm.disable_fog = true
	q.material_override = hm
	q.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	q.position = Vector3((axf + axr) / 2.0, 0.2, 0.0)
	g.add_child(q)
	v["ug_haze"] = hm


static var _ugt: ImageTexture = null


## a soft rounded pool: brightest near the edge of the body, fading out over the ground (web ugGenericT)
static func _ug_tex() -> ImageTexture:
	if _ugt != null:
		return _ugt
	var W := 128
	var H := 64
	var img := Image.create(W, H, false, Image.FORMAT_RGBA8)
	for zz in H:
		for q in W:
			var u := absf(q + 0.5 - W / 2.0) / (W / 2.0)
			var w := absf(zz + 0.5 - H / 2.0) / (H / 2.0)
			var d := pow(pow(u, 6.0) + pow(w, 6.0), 1.0 / 6.0)
			var ring := exp(-pow((d - 0.72) / 0.13, 2.0))
			var fill := 0.55 if d < 0.72 else maxf(0.0, 1.0 - (d - 0.72) / 0.28) * 0.55
			var a := minf(1.0, ring * 0.9 + fill) * (1.0 if d < 1.0 else 0.0)
			img.set_pixel(q, zz, Color(1, 1, 1, a))
	_ugt = ImageTexture.create_from_image(img)
	return _ugt


## each frame: the glow brighter in the dark, rainbow cycling (web patch 66's light, patch 67's haze)
func _style_frame(k: Kart, v: Dictionary, time: float, dark: float) -> void:
	var ug: Array = v.get("ug", [])
	if ug.is_empty():
		return
	var rc := Color.from_hsv(fmod(time * 0.12 + k.ri * 0.13, 1.0), 1.0, 1.0) if bool(v.get("ug_rb", false)) else Color(0, 0, 0, 0)
	for L in ug:
		(L as OmniLight3D).light_energy = (2.0 + 6.0 * dark) * (1.2 if k.boost > 0.0 else 1.0)
		if rc.a > 0.0:
			(L as OmniLight3D).light_color = rc
	var hm: StandardMaterial3D = v.get("ug_haze")
	if hm != null:
		var c := rc if rc.a > 0.0 else (ug[0] as OmniLight3D).light_color
		hm.albedo_color = Color(c.r, c.g, c.b, 0.05 + 0.07 * dark)   # (a faint haze only: the lights do the work)


func smoke_col(k: Kart, v: Dictionary) -> Color:
	var h := String(v.get("smc", "#f2ebe0"))
	if h == "rainbow":
		return Color.from_hsv(fmod(Time.get_ticks_msec() / 1000.0 * 0.12 + k.ri * 0.13, 1.0), 0.85, 1.0)
	return Color(h) if h != "" and h != "<null>" else Color("#f2ebe0")


## Sandbox, at the swap between two places (main.gd _sb_adopt)""")
rep('view.gd', """			if i % 3 == 0:
				var tv2: Vector3 = gt * (fxl[0 if randf() < 0.5 else mini(1, fxl.size() - 1)] as Vector3)
				fx.spawn_n(tv2.x, tv2.y + 0.6, tv2.z, (randf() - 0.5) * 6.0, 4.0 + randf() * 4.0, (randf() - 0.5) * 6.0, Color("#f2ebe0"), 2.5, 8.0, 0.8, -2.0, 1.5)""",
    """			if i % 2 == 0:
				# tyre smoke in the chosen colour: thick, rolling up and out, hanging a while (web patch 65)
				var scol := smoke_col(k, v)
				for lv2 in fxl:
					var tv2: Vector3 = gt * (lv2 as Vector3)
					fx.spawn_n(tv2.x, tv2.y + 0.8, tv2.z, (randf() - 0.5) * 9.0 - cos(k.ma) * 6.0, 5.0 + randf() * 6.0, (randf() - 0.5) * 9.0 - sin(k.ma) * 6.0, scol, 3.6, 15.0, 1.25, -1.5, 1.2)
		if not k.air and k.drift == 0 and k.speed > 3.0 and k.speed < 48.0 and k.acc > 30.0 and i % 2 == 0 and fxl.size() > 0 and (k == me or randf() < 0.4):
			# a hard launch from slow: smoke off the rear tyres (web patch 65)
			var lc := smoke_col(k, v)
			for lv3 in fxl:
				var tv3: Vector3 = gt * (lv3 as Vector3)
				fx.spawn_n(tv3.x, tv3.y + 0.6, tv3.z, (randf() - 0.5) * 8.0 - cos(k.ma) * 12.0, 3.0 + randf() * 5.0, (randf() - 0.5) * 8.0 - sin(k.ma) * 12.0, lc, 3.0, 13.0, 1.1, -1.5, 1.4)""")
rep('fx.gd', "	fxn = Pool.new(260, mn, self)", "	fxn = Pool.new(420, mn, self)   # (web patch 65: thicker tyre smoke)")

# ---------------------------------------------------------------- the Sandbox headlight beam's colour
rep('sandbox_night.gd', """	spot.light_energy = 3.2 * maxf(L, 0.45) * hon * (1.0 if hm == true else hf)""", """	spot.light_energy = 3.2 * maxf(L, 0.45) * hon * (1.0 if hm == true else hf)
	# the headlight colour from the style shop (web patch 65); halogen, the first, keeps the cool white beam
	var hli: Dictionary = preload("res://scripts/style.gd").pick(k.info.get("spec", {}) if k.info.get("spec") is Dictionary else {}, "hl")
	var hc := Color(String(hli["h"])) if String(hli["h"]) != "#fff2d6" else Color("#eef3ff")
	if spot.light_color != hc:
		spot.light_color = hc""")

# ---------------------------------------------------------------- the garage's Colour tab: the style shop
rep('menu.gd', """			desc = "[b][color=#fff4dc]%s.[/color][/b] One colour all over the kart." % pn[int(build["p"])]""",
    """			desc = "[b][color=#fff4dc]%s.[/color][/b] One colour all over the kart. Below: the style shop." % pn[int(build["p"])]
			# the style shop (web patch 65): its rows go under the paints, in the same scrolling list
			var rr := sc.get_child(0)
			sc.remove_child(rr)
			var outer := vbox(6)
			outer.size_flags_horizontal = Control.SIZE_EXPAND_FILL
			outer.add_child(rr)
			_style_shop(outer)
			sc.add_child(outer)""")
rep('menu.gd', """func _build_changed() -> void:""", """var _style_ask := ""


## web styleUI: a row of swatches per slot; a locked one shows its price; the first press asks, a second buys
func _style_shop(outer: VBoxContainer) -> void:
	var S := preload("res://scripts/style.gd")
	var coins := int(preload("res://scripts/sandbox.gd").load_save().get("c", 0))
	outer.add_child(label("Style shop · %d coins" % coins, f_bold, 15.0, CHEESE))
	var st: Dictionary = build.get("st", {}) if build.get("st") is Dictionary else {}
	for row in [["tr", "Trim"], ["ac", "Accent"], ["in", "Interior"], ["gl", "Underglow"], ["hl", "Headlights"], ["sm", "Tyre smoke"]]:
		var slot := String(row[0])
		outer.add_child(section_label(String(row[1])))
		var gr := GridContainer.new()
		gr.columns = 6
		gr.add_theme_constant_override("h_separation", zi(8))
		gr.add_theme_constant_override("v_separation", zi(8))
		var L: Array = S.SLOTS[slot][1]
		for i in L.size():
			var it: Dictionary = L[i]
			var own: bool = S.is_owned(slot, i)
			var on := int(st.get(slot, 0)) == i
			var sw := Button.new()
			sw.custom_minimum_size = Vector2(z(52), z(52))
			sw.tooltip_text = String(it["n"]) + ("" if own else " · %d coins" % int(it["p"]))
			sw.set_meta("gkey", "st:%s:%d" % [slot, i])
			var cl: Array = [Color("#3a2a22"), Color("#2a1c16")] if it["h"] == null else ([Color("#ff3030"), Color("#ffd22a"), Color("#3dff6a"), Color("#2ae8ff"), Color("#a040ff")] if String(it["h"]) == "rainbow" else ([Color("#ffffff"), Color(String(it["h"])), Color("#222222")] if it.has("m") else [Color(String(it["h"]))]))
			var stb := box(cl, 135.0, 26.0, CHEESE if on else Color(1, 0.957, 0.863, 0.3), 3.0 if on else 1.5)
			for s2 in ["normal", "hover", "pressed", "hover_pressed", "focus"]:
				sw.add_theme_stylebox_override(s2, stb)
			if not own:
				sw.text = str(int(it["p"]))
				sw.add_theme_font_override("font", f_bold)
				sw.add_theme_font_size_override("font_size", zi(12))
				sw.add_theme_color_override("font_color", CHEESE)
				sw.add_theme_color_override("font_outline_color", Color("#2a140a"))
				sw.add_theme_constant_override("outline_size", zi(4))
			var si := i
			sw.pressed.connect(func():
				if not S.is_owned(slot, si):
					var have := int(preload("res://scripts/sandbox.gd").load_save().get("c", 0))
					if have < int(it["p"]):
						setting_changed.emit("toast", "%s costs %d coins. You have %d. Earn coins by racing and in Sandbox." % [String(it["n"]), int(it["p"]), have])
						return
					if _style_ask != slot + str(si):
						_style_ask = slot + str(si)
						setting_changed.emit("toast", "Press %s again to buy it for %d coins" % [String(it["n"]), int(it["p"])])
						return
					_style_ask = ""
					S.buy(slot, si)
				var ns := st.duplicate()
				ns[slot] = si
				build["st"] = ns
				_build_changed())
			gr.add_child(sw)
		outer.add_child(gr)


func _build_changed() -> void:""")
rep('main.gd', """	menu.setting_changed.connect(func(k, v):
		sel[k] = v""", """	menu.setting_changed.connect(func(k, v):
		if k == "toast":
			_toast(String(v))   # (the style shop's messages, web patch 65)
			return
		sel[k] = v""")
rep('view.gd', """func draw_kart(k: Kart, al: float, dt: float, racing: bool, paused: bool) -> void:
	var v: Dictionary = views[k]""", """func draw_kart(k: Kart, al: float, dt: float, racing: bool, paused: bool) -> void:
	var v: Dictionary = views[k]
	if not (v.get("ug", []) as Array).is_empty():
		var dk := 0.0
		if race != null and race.sb != null:
			dk = float(preload("res://scripts/sandbox_clock.gd").f(float(race.sb.save.get("t", 0.4)))["L"])
		elif String(T.theme) == "night":
			dk = 1.0
		_style_frame(k, v, time, dk)""")
print('pc65 applied')
