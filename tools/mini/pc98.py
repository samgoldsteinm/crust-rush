"""PC: the cinematic finish (web patch 110, web v245): trackside slow motion, the driver close up, the place and name in 3D letters.
    py.cmd tools/mini/pc98.py      (once, after pc97; edits main.gd)
Same shots and timings as the web (read patch110.py): ~7.2 s of real time, letterboxed, the race HUD hidden, any key / button / click
skips; slow motion only off line (the race steps with a scaled dt); the results wait for it (fin_t). The letters are TextMesh in Bungee
(assets/fonts), one per character so each pops in."""
G = 'D:/crust-rush/godot/scripts/'


def rep(f, a, b, n=1):
    p = G + f
    s = open(p, encoding='utf-8', newline='').read()
    assert s.count(a) == n, (f, s.count(a), a[:80])
    s = s.replace(a, b)
    open(p, 'w', encoding='utf-8', newline='').write(s)


# --- state
rep('main.gd', 'var fin_punch := 0.0\n', '''var fin_punch := 0.0
# (pc98) the cinematic finish (web patch 110)
var fin_on := false
var fin_tt := 0.0
var fin_shot := -1
var fin_cp := Vector3()
var fin_lk := Vector3()
var fin_side := 1.0
var fin_sp := 0.0
var fin_grp: Node3D = null
var fin_born := 0.0
var fin_ui: CanvasLayer = null
var fin_hud := true
''')
# --- start it with the finish punch
rep('main.gd', '''		_show_center("Finish!", 2.4)
		fin_punch = 0.0001
		_shake(0.5)
		sfx.play("finish")
''', '''		_show_center("Finish!", 2.4)
		fin_punch = 0.0001
		_shake(0.5)
		sfx.play("finish")
		_fin_start()
''')
# --- slow motion off line
rep('main.gd', '''	if paused or test_hold:
		return
	_sim_tick(dt)
	if net_role == "host":''', '''	if paused or test_hold:
		return
	_sim_tick(dt * (_fin_ts() if fin_on and net_role == "" else 1.0))   # (pc98: the finish's slow motion, off line only)
	if net_role == "host":''')
# --- the results wait for it (both the local race and a browser friend's)
rep('main.gd', '''	elif state == "finished":
		fin_t -= dt
		if fin_t <= 0.0:
			race.finalize()
			state = "results"
			_show_results()
	if state == "race":''', '''	elif state == "finished":
		if not fin_on:   # (pc98: the cinematic finish first)
			fin_t -= dt
		if fin_t <= 0.0:
			race.finalize()
			state = "results"
			_show_results()
	if state == "race":''')
rep('main.gd', '''	elif state == "finished":
		fin_t -= dt
		if fin_t <= 0.0:
			race.finalize()
			state = "results"
			_show_results()''', '''	elif state == "finished":
		if not fin_on:
			fin_t -= dt
		if fin_t <= 0.0:
			race.finalize()
			state = "results"
			_show_results()''')
# --- its clock (real time) and its camera
rep('main.gd', '''	_camera(dt, float(v["rx"]), float(v["ry"]), float(v["rz"]), float(v["rma"]))
	_sb_cine_tick(dt)''', '''	if fin_on and not paused:
		fin_tt += dt
		if fin_tt >= 7.2:
			_fin_end()
	_camera(dt, float(v["rx"]), float(v["ry"]), float(v["rz"]), float(v["rma"]))
	if fin_on and kart != null and view.views.has(kart):
		var fv: Dictionary = view.views[kart]
		_fin_cam(dt, kart, float(fv["rx"]), float(fv["ry"]), float(fv["rz"]), float(fv["rma"]))
	_sb_cine_tick(dt)''')
# --- skip
rep('main.gd', '''func _input(ev: InputEvent) -> void:
''', '''func _input(ev: InputEvent) -> void:
	if fin_on and fin_tt > 0.5 and ((ev is InputEventKey and ev.pressed) or (ev is InputEventJoypadButton and ev.pressed) or (ev is InputEventMouseButton and ev.pressed) or (ev is InputEventScreenTouch and ev.pressed)):
		_fin_end()   # (pc98: skip the cinematic finish)
		get_viewport().set_input_as_handled()
		return
''')
# --- the functions (after _finish_check)
rep('main.gd', '''## the player's run is in: personal best, recent races, achievements (not in the automatic test drives)
func _progress_finish() -> void:''', '''## (pc98) the cinematic finish, as the web's patch 110: A trackside (0-2.3 s), B the driver (2.3-4.6), C the sign (4.6-7.2)
const FIN_COL := [[Color("#ffcf40"), Color("#8a5a00")], [Color("#e2e7ef"), Color("#4a5260")], [Color("#d98a48"), Color("#6a3410")], [Color("#fff4dc"), Color("#7a3a10")]]


func _fin_start() -> void:
	_fin_clear()
	if spec_on or kart == null or race == null or race.mode == "lss" or race.mode == "bb" or race.sb != null or T.battle or auto_drive:
		return
	fin_on = true
	fin_tt = 0.0
	fin_shot = -1
	_fin_ui(true)


func _fin_end() -> void:
	if not fin_on:
		return
	fin_on = false
	_fin_ui(false)
	cam_snap = true
	fin_t = minf(fin_t, 0.35)


func _fin_clear() -> void:
	if fin_grp != null and is_instance_valid(fin_grp):
		fin_grp.queue_free()
	fin_grp = null
	if fin_on:
		fin_on = false
		_fin_ui(false)


func _fin_ts() -> float:
	return 0.28 if fin_tt < 2.3 else (0.4 if fin_tt < 4.6 else 0.4 + 0.45 * minf(1.0, (fin_tt - 4.6) / 2.6))


func _fin_ui(on: bool) -> void:
	if fin_ui == null:
		if not on:
			return
		fin_ui = CanvasLayer.new()
		fin_ui.layer = 40
		add_child(fin_ui)
		for i in 2:
			var r := ColorRect.new()
			r.color = Color.BLACK
			r.anchor_left = 0.0
			r.anchor_right = 1.0
			r.anchor_top = 0.0 if i == 0 else 0.895
			r.anchor_bottom = 0.105 if i == 0 else 1.0
			r.mouse_filter = Control.MOUSE_FILTER_IGNORE
			fin_ui.add_child(r)
		var l := Label.new()
		l.text = "Press any key to skip"
		l.add_theme_font_size_override("font_size", 14)
		l.add_theme_color_override("font_color", Color(1, 0.96, 0.86, 0.66))
		l.anchor_left = 1.0
		l.anchor_right = 1.0
		l.anchor_top = 1.0
		l.anchor_bottom = 1.0
		l.offset_left = -240.0
		l.offset_right = -18.0
		l.offset_top = -38.0
		l.offset_bottom = -14.0
		l.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
		fin_ui.add_child(l)
	fin_ui.visible = on
	if hud_race != null:
		if on:
			fin_hud = hud_race.visible
			hud_race.visible = false
		else:
			hud_race.visible = fin_hud


## a word in 3D letters (Bungee), centred, one node per letter (so each can pop in); size = the font's em in world units
func _fin_word(s: String, size: float, depth: float, c: Array) -> Node3D:
	var g := Node3D.new()
	var font: Font = load("res://assets/fonts/Bungee-Regular.ttf")
	var fs := 64
	var px := size / float(fs)
	var mat := StandardMaterial3D.new()
	mat.albedo_color = c[0]
	mat.metallic = 0.55
	mat.roughness = 0.28
	mat.emission_enabled = true
	mat.emission = c[1]
	mat.emission_energy_multiplier = 0.55
	var x := 0.0
	var parts: Array = []
	for ch in s.to_upper():
		var w := font.get_char_size(ch.unicode_at(0), fs).x * px
		if ch != " ":
			var tm := TextMesh.new()
			tm.text = ch
			tm.font = font
			tm.font_size = fs
			tm.depth = depth
			tm.pixel_size = px
			tm.material = mat
			var piv := Node3D.new()
			var mi := MeshInstance3D.new()
			mi.mesh = tm
			piv.add_child(mi)
			piv.position.x = x + w / 2.0
			g.add_child(piv)
			parts.append(piv)
		x += w
	for n in g.get_children():
		(n as Node3D).position.x -= x / 2.0
	g.set_meta("w", x)
	g.set_meta("L", parts)
	return g


func _fin_ord(n: int) -> String:
	var v := n % 100
	if v > 10 and v < 14:
		return str(n) + "TH"
	return str(n) + (["TH", "ST", "ND", "RD"][v % 10] if v % 10 < 4 else "TH")


## the point `dist` ahead along the track from the kart's lap point, the way it is going: [x, y, tx, ty]
func _fin_ahead(k: Kart, dist: float) -> Array:
	var j := k.idx
	var dir := 1 if cos(k.ma) * T.tx[j] + sin(k.ma) * T.ty[j] >= 0.0 else -1
	var acc := 0.0
	var n := 0
	while acc < dist and n < T.N:
		var j2 := (j + dir + T.N) % T.N
		acc += Vector2(T.px[j2] - T.px[j], T.py[j2] - T.py[j]).length()
		j = j2
		n += 1
	return [T.px[j], T.py[j], T.tx[j] * dir, T.ty[j] * dir]


func _fin_cam(dt: float, k: Kart, rx: float, ry: float, rz: float, rma: float) -> void:
	var t := fin_tt
	var fx := cos(rma)
	var fy := sin(rma)
	var sh := 0 if t < 2.3 else (1 if t < 4.6 else 2)
	var cut := sh != fin_shot
	var ez := func(q: float) -> float: return 2.0 * q * q if q < 0.5 else 1.0 - pow(-2.0 * q + 2.0, 2.0) / 2.0
	var online := net_role != "" or web.racing()
	if cut:
		fin_shot = sh
		fin_sp = absf(k.speed)
		fin_side = 1.0 if randf() < 0.5 else -1.0
		if sh == 0:
			var a := _fin_ahead(k, maxf(40.0, fin_sp * (0.9 if online else 0.32)))
			var nxa := -float(a[3])
			var nya := float(a[2])
			var lat := T.lateral(k.idx, k.x, k.y)
			var side := 1.0 if lat >= 0.0 else -1.0
			var cl := lat + side * 20.0
			if absf(cl) > T.RW * 0.95:
				cl = lat - side * 20.0
			var x := float(a[0]) + nxa * cl
			var y := float(a[1]) + nya * cl
			fin_cp = Vector3(x, T.ground(x, y) + 3.2, y)
		if sh == 2:
			var d := clampf(fin_sp * (2.1 if online else 1.25), 70.0, 420.0)
			var a := _fin_ahead(k, d)
			var pl := maxi(1, k.place)
			var top := _fin_word(_fin_ord(pl), 15.0, 4.2, FIN_COL[mini(pl, 4) - 1])
			var nm := _fin_word(_web_name(), 7.2, 2.4, FIN_COL[3])
			top.position.y = 11.5
			var g := Node3D.new()
			g.add_child(top)
			g.add_child(nm)
			g.scale = Vector3.ONE * minf(1.0, T.RW * 1.7 / maxf(1.0, maxf(float(top.get_meta("w")), float(nm.get_meta("w")))))
			add_child(g)
			g.global_position = Vector3(float(a[0]), T.ground(float(a[0]), float(a[1])) + 14.0, float(a[1]))
			g.rotation.y = atan2(-float(a[2]), -float(a[3]))
			var L: Array = (top.get_meta("L") as Array) + (nm.get_meta("L") as Array)
			for l in L:
				(l as Node3D).scale = Vector3.ONE * 0.001
			g.set_meta("L", L)
			fin_born = t
			fin_grp = g
	if fin_grp != null and is_instance_valid(fin_grp):
		var L: Array = fin_grp.get_meta("L")
		for i in L.size():
			var u := clampf((t - fin_born - i * 0.05) / 0.45, 0.0, 1.0)
			var o := 1.0 + sin(u * PI) * 0.35 * (1.0 - u) if u < 1.0 else 1.0
			(L[i] as Node3D).scale = Vector3.ONE * maxf(0.001, float(ez.call(u)) * o)
			(L[i] as Node3D).rotation.y = (1.0 - u) * 1.2
	var fov := 48.0
	var kp := Vector3(rx, rz, ry)
	if sh == 0:
		cam.global_position = fin_cp
		var tg := kp + Vector3(0, 2.6, 0)
		fin_lk = tg if cut else fin_lk.lerp(tg, 1.0 - exp(-10.0 * dt))
		if cam.global_position.distance_to(fin_lk) > 0.1:
			cam.look_at(fin_lk, Vector3.UP)
		var dd := cam.global_position.distance_to(fin_lk)
		fov = clampf(rad_to_deg(2.0 * atan(15.0 / maxf(1.0, dd))), 16.0, 52.0)
	elif sh == 1:
		var hd := kp + Vector3(0, 4.0, 0)
		var v: Dictionary = view.views.get(k, {})
		var drv: Node3D = (v["model"] as Node3D).find_child("driver", true, false) as Node3D if v.get("model") is Node3D else null
		if drv != null:
			hd = drv.global_position
		hd.y += 1.4
		var u := clampf((t - 2.3) / 2.3, 0.0, 1.0)
		var an := rma + fin_side * (0.2 + 0.34 * float(ez.call(u))) * PI
		var R := (13.0 - 2.5 * u) * k.sf
		var cx := hd.x + cos(an) * R
		var cz := hd.z + sin(an) * R
		cam.global_position = Vector3(cx, maxf(hd.y + 2.4 - 1.2 * u, T.ground(cx, cz) + 1.5), cz)
		cam.look_at(hd, Vector3.UP)
		fov = 34.0
	else:
		var u := float(ez.call(clampf((t - 4.6) / 2.6, 0.0, 1.0)))
		var bx := rx - fx * (24.0 + 10.0 * u)
		var by := ry - fy * (24.0 + 10.0 * u)
		fin_cp = Vector3(bx, maxf(rz, T.ground(bx, by)) + 6.0 + 14.0 * u, by)
		cam.global_position = fin_cp if cut else cam.global_position.lerp(fin_cp, 1.0 - exp(-8.0 * dt))
		var tg := Vector3(rx + fx * 8.0, rz + 4.0, ry + fy * 8.0)
		if fin_grp != null and is_instance_valid(fin_grp):
			tg = tg.lerp(fin_grp.global_position + Vector3(0, 4.0, 0), 0.35 + 0.25 * u)
		fin_lk = tg if cut else fin_lk.lerp(tg, 1.0 - exp(-6.0 * dt))
		cam.look_at(fin_lk, Vector3.UP)
		fov = 50.0
	cam.fov = fov if (cut or sh == 0) else cam.fov + (fov - cam.fov) * minf(1.0, dt * 6.0)


## the player's run is in: personal best, recent races, achievements (not in the automatic test drives)
func _progress_finish() -> void:''')
# --- a new race clears the sign
rep('main.gd', '''
	fin_punch = 0.0
''', '''
	fin_punch = 0.0
	_fin_clear()   # (pc98)
''')
print('pc98 applied')
