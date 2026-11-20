"""PC: the garage's combo cards as the web's (styleUI / myCards): a dark card, the name, a row of colour dots, Owned / Free /
price; My combos with the x in the card's corner, and a name asked for when a look is saved (the web's prompt).
    python tools/mini/pc105.py      (once, after pc104)"""
p = 'D:/crust-rush/godot/scripts/menu.gd'
s = open(p, encoding='utf-8', newline='').read()
assert '_combo_tile' not in s, 'already patched'


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:80])
    s = s.replace(a, b)


def cut(a, b, new):
    """replace from a (inclusive) to b (inclusive), each once"""
    global s
    assert s.count(a) == 1, a[:80]
    i = s.index(a)
    j = s.index(b, i)
    s = s[:i] + new + s[j + len(b):]


# --- the shop's combos
cut('		var bt := Button.new()\n		bt.custom_minimum_size = Vector2(z(150), z(58))',
    '		bt.add_theme_constant_override("outline_size", zi(5))\n',
    '		var pls: Array = KartBuilder.info.get("paints", [])\n'
    '		var bt := _combo_tile(("★ " if cb.has("only") else "") + String(cb["n"]), _combo_chips(pls[int(cb["p"])] if int(cb["p"]) < pls.size() else null, cst),\n'
    '			(("Free" if int(cb["c"]) == 0 else "Owned") if cown else "%d coins" % int(cb["c"])), con)\n'
    '		bt.set_meta("gkey", "cb:%d" % ci)\n')

# --- My combos
cut('		var row := HBoxContainer.new()\n		row.add_theme_constant_override("separation", zi(2))',
    '		row.add_child(dx)\n		mg.add_child(row)\n',
    '		var pls: Array = KartBuilder.info.get("paints", [])\n'
    '		var lvd: Dictionary = KartBuilder.livery(String(c.get("t", ""))) if String(c.get("t", "")) != "" else {}\n'
    '		var first = lvd.get("A") if not lvd.is_empty() else (pls[int(c.get("p", 0))] if int(c.get("p", 0)) < pls.size() else null)\n'
    '		var bt := _combo_tile(String(c.get("n", "My combo")), _combo_chips(first, cst), String(lvd.get("name", "Livery")) if not lvd.is_empty() else "Saved", on, true)\n'
    '		bt.set_meta("gkey", "my:%d" % mi)\n'
    '		var mix := mi\n'
    '		bt.pressed.connect(func(): _my_wear(mix))\n'
    '		var dx := Button.new()   # (the web\'s round x in the card\'s top right corner)\n'
    '		dx.text = "×"\n'
    '		dx.tooltip_text = "Delete"\n'
    '		dx.set_meta("gkey", "myx:%d" % mi)\n'
    '		dx.focus_mode = Control.FOCUS_NONE\n'
    '		dx.add_theme_font_override("font", f_bold)\n'
    '		dx.add_theme_font_size_override("font_size", zi(13))\n'
    '		dx.add_theme_color_override("font_color", Color("#fff4dc"))\n'
    '		var dxs := StyleBoxFlat.new()\n'
    '		dxs.bg_color = Color(0, 0, 0, 0.45)\n'
    '		dxs.set_corner_radius_all(zi(11))\n'
    '		for s3 in ["normal", "hover", "pressed", "focus"]:\n'
    '			dx.add_theme_stylebox_override(s3, dxs)\n'
    '		dx.anchor_left = 1.0\n'
    '		dx.anchor_right = 1.0\n'
    '		dx.offset_left = -z(26)\n'
    '		dx.offset_right = -z(4)\n'
    '		dx.offset_top = z(4)\n'
    '		dx.offset_bottom = z(26)\n'
    '		dx.pressed.connect(func():\n'
    '			var M2: Array = S.my_combos()\n'
    '			if mix >= M2.size():\n'
    '				return\n'
    '			if _style_ask != "md%d" % mix:\n'
    '				_style_ask = "md%d" % mix\n'
    '				setting_changed.emit("toast", "Press × on %s again to delete it." % String((M2[mix] as Dictionary).get("n", "this combo")))\n'
    '				return\n'
    '			_style_ask = ""\n'
    '			M2.remove_at(mix)\n'
    '			S.my_combos_put(M2)\n'
    '			_build_changed())\n'
    '		bt.add_child(dx)\n'
    '		mg.add_child(bt)\n')

# --- Save this look: the web's dashed card; asks for a name first
cut('		var sv := Button.new()\n		sv.custom_minimum_size = Vector2(z(118), z(58))',
    '			_build_changed())\n		mg.add_child(sv)\n',
    '		var sv := Button.new()\n'
    '		sv.custom_minimum_size = Vector2(z(118), z(66))\n'
    '		sv.size_flags_horizontal = Control.SIZE_EXPAND_FILL\n'
    '		sv.set_meta("gkey", "mysave")\n'
    '		for s2 in ["normal", "hover", "pressed", "hover_pressed", "focus"]:\n'
    '			sv.add_theme_stylebox_override(s2, _combo_sb(Color(0, 0, 0, 0.18 if s2 == "normal" else 0.3), Color(1, 0.957, 0.863, 0.35)))\n'
    '		var svv := VBoxContainer.new()\n'
    '		svv.mouse_filter = Control.MOUSE_FILTER_IGNORE\n'
    '		svv.alignment = BoxContainer.ALIGNMENT_CENTER\n'
    '		svv.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)\n'
    '		svv.add_theme_constant_override("separation", zi(2))\n'
    '		for t2 in [["+", 20.0, 1.0], ["Save this look", 11.5, 0.85]]:\n'
    '			var l2 := label(String(t2[0]), f_bold, float(t2[1]), Color(1, 0.957, 0.863, float(t2[2])))\n'
    '			l2.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER\n'
    '			svv.add_child(l2)\n'
    '		sv.add_child(svv)\n'
    '		sv.pressed.connect(func():\n'
    '			if S.my_combos().size() >= 12:\n'
    '				setting_changed.emit("toast", "You can keep 12 combos. Delete one first.")\n'
    '				return\n'
    '			modal_builders["cbname"] = _cb_name_panel\n'
    '			show_modal("cbname"))\n'
    '		mg.add_child(sv)\n')

rep('"lb": 760.0, "lbname": 600.0}', '"lb": 760.0, "lbname": 600.0, "cbname": 560.0}')
rep('"lb": lb_title, "lbname": "Pick a username"}', '"lb": lb_title, "lbname": "Pick a username", "cbname": "Name this combo"}')

# --- the helpers, before _my_wear
rep('## (pc86, web myWear) put a saved combo on the vehicle in the garage\n', '''## (pc105) the web's combo card: rgba(0,0,0,.28), a 2 px border (cheese when worn), corners 12 px
func _combo_sb(bg: Color, border: Color) -> StyleBoxFlat:
	var sb := StyleBoxFlat.new()
	sb.bg_color = bg
	sb.border_color = border
	sb.set_border_width_all(maxi(1, zi(2)))
	sb.set_corner_radius_all(zi(12))
	sb.anti_aliasing = true
	return sb


## (pc105) the web's combo colours: paint (or the livery's first), trim, accent, rims, calipers, underglow
func _combo_chips(first, cst: Dictionary) -> Array:
	var S := preload("res://scripts/style.gd")
	var out: Array = [first]
	for k in ["tr", "ac", "rm", "cl", "gl"]:
		var L: Array = S.SLOTS[k][1]
		out.append((L[clampi(int(cst.get(k, 0)), 0, L.size() - 1)] as Dictionary)["h"])
	return out


## (pc105) a combo card as the web's: the name, a row of overlapping colour dots, a small line under
func _combo_tile(name_: String, chips: Array, sub: String, on: bool, room_x := false) -> Button:
	var bt := Button.new()
	bt.custom_minimum_size = Vector2(z(118), z(66))
	bt.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	bt.tooltip_text = name_
	var line := Color("#f7c948") if on else Color(1, 0.957, 0.863, 0.14)
	bt.add_theme_stylebox_override("normal", _combo_sb(Color(0, 0, 0, 0.28), line))
	for s2 in ["hover", "pressed", "hover_pressed", "focus"]:
		bt.add_theme_stylebox_override(s2, _combo_sb(Color(0, 0, 0, 0.4), Color("#f7c948") if on else Color(1, 0.957, 0.863, 0.3)))
	var v := VBoxContainer.new()
	v.mouse_filter = Control.MOUSE_FILTER_IGNORE
	v.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	v.offset_left = z(10)
	v.offset_right = -z(26 if room_x else 10)
	v.offset_top = z(8)
	v.offset_bottom = -z(8)
	v.alignment = BoxContainer.ALIGNMENT_CENTER
	v.add_theme_constant_override("separation", zi(5))
	var nl := label(name_, f_bold, 13.0, Color("#fff4dc"))
	nl.text_overrun_behavior = TextServer.OVERRUN_TRIM_ELLIPSIS
	nl.clip_text = true
	nl.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	v.add_child(nl)
	var row := HBoxContainer.new()
	row.mouse_filter = Control.MOUSE_FILTER_IGNORE
	row.add_theme_constant_override("separation", -zi(4))
	for h in chips:
		var d := Control.new()
		d.mouse_filter = Control.MOUSE_FILTER_IGNORE
		d.custom_minimum_size = Vector2(z(14), z(14))
		var hh = h
		d.draw.connect(func():
			var c0 := d.size * 0.5
			var r := d.size.x * 0.5
			d.draw_circle(c0, r + z(2), Color("#1a1210"))
			if hh != null and String(hh) == "rainbow":
				var rb := [Color("#ff3030"), Color("#ffd22a"), Color("#3dff6a"), Color("#2ae8ff"), Color("#a040ff")]
				for q in 5:
					var pts := PackedVector2Array([c0])
					for e in 9:
						var a := TAU * (q + e / 8.0) / 5.0 - PI * 0.5
						pts.append(c0 + Vector2(cos(a), sin(a)) * r)
					d.draw_colored_polygon(pts, rb[q])
			else:
				d.draw_circle(c0, r, Color(String(hh)) if hh != null else Color("#333333")))
		row.add_child(d)
	v.add_child(row)
	v.add_child(label(sub, f_semi, 11.5, Color(1, 0.957, 0.863, 0.8)))
	bt.add_child(v)
	return bt


## (pc105, web mySave's prompt) the name for the look being saved
func _cb_name_panel() -> Control:
	var S := preload("res://scripts/style.gd")
	var v: VBoxContainer = vbox(12)
	v.add_child(para("A name for this look in My combos. You can wear it on any vehicle.", 15.0, Color("#c2a58c"), 480.0))
	var ed := LineEdit.new()
	ed.text = "My look %d" % (S.my_combos().size() + 1)
	ed.max_length = 24
	ed.select_all_on_focus = true
	ed.add_theme_font_override("font", f_semi)
	ed.add_theme_font_size_override("font_size", zi(18))
	ed.custom_minimum_size = Vector2(z(420), z(44))
	v.add_child(ed)
	var save := func():
		var M3: Array = S.my_combos()
		if M3.size() >= 12:
			close_modal()
			setting_changed.emit("toast", "You can keep 12 combos. Delete one first.")
			return
		var nm := ed.text.strip_edges().left(24)
		if nm == "":
			nm = "My look %d" % (M3.size() + 1)
		M3.append({"n": nm, "p": int(build.get("p", 0)), "t": String(build.get("t", "")), "st": (build.get("st", {}) as Dictionary).duplicate() if build.get("st") is Dictionary else {}})
		S.my_combos_put(M3)
		close_modal()
		setting_changed.emit("toast", "Saved %s. Wear it on any vehicle from My combos." % nm)
		_build_changed()
	ed.text_submitted.connect(func(_t): save.call())
	var row: HBoxContainer = hbox(10)
	var later: Button = button("Cancel", "ghost", 15.0, Vector4(16, 10, 16, 10))
	later.pressed.connect(close_modal)
	row.add_child(later)
	var ok: Button = button("Save", "cta", 15.0, Vector4(22, 10, 22, 10))
	ok.pressed.connect(save)
	row.add_child(ok)
	v.add_child(row)
	(func():
		if is_instance_valid(ed):
			ed.grab_focus()
			ed.select_all()).call_deferred()
	return v


## (pc86, web myWear) put a saved combo on the vehicle in the garage
''')
open(p, 'w', encoding='utf-8', newline='').write(s)
print('pc105 applied')
