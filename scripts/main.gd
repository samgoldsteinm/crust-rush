extends Node3D
## Race scene: Hawaiian Bay with the Hypercar, matching the web game's look and handling.
## Physics runs at 120 Hz in _physics_process (project setting); drawing interpolates between
## steps in _process, like the web game. Phone: touch the left/right half to steer, the corner
## pedals to drift/brake, gas is automatic. Keyboard: arrows/WASD, Space or Shift to drift.
## Controller: left stick, RT gas, LT drift.

const TRACK_JSON := "res://assets/track/bay.json"
const TRACK_SCENE := "res://assets/track/bay.gltf"
const KART_SCENE := "res://assets/kart/hypercar.glb"
const KART_JSON := "res://assets/kart/hypercar.json"
const CULL_DIST := 2200.0   # far clutter cells hide beyond this (the web uses 1500-2250 by preset)

var T: TrackData
var kart := Kart.new()
var kart_meta := {}
var kart_node: Node3D
var body: Node3D
var wheels: Array = []      # {node, r, front}
var cam: Camera3D
var sun: DirectionalLight3D
var env: Environment

var state := "countdown"     # countdown | race | finished
var cd := 3.2
var race_time := 0.0
var cam_a := 0.0
var cam_base := Vector3.ZERO
var cam_look := Vector3.ZERO
var cam_snap := true
var shake := 0.0
var cull_list: Array = []    # {node, rect: Rect2 in ground x/z}
var cull_t := 0.0
var auto_drive := false      # set by the smoke test

# input
var touches := {}            # index -> "l" | "r" | "pedal"
var pad_used_at := -1e9

# HUD
var lbl_lap: Label
var lbl_time: Label
var lbl_speed: Label
var lbl_info: Label
var lbl_center: Label
var pedal_l: Panel
var pedal_r: Panel
var btn_fps: Button
var btn_res: Button
var center_t := 0.0
var fps_cap := 60
var res_scale := 1.0
var is_phone := false


func _ready() -> void:
	is_phone = OS.has_feature("mobile") or DisplayServer.is_touchscreen_available() and OS.get_name() in ["iOS", "Android"]
	T = TrackData.load_from(TRACK_JSON)
	if T == null:
		return
	_load_kart_meta()
	_build_world()
	_build_kart()
	_build_hud()
	_apply_display()
	_restart()


# ---------------------------------------------------------------- world

func _load_kart_meta() -> void:
	var f := FileAccess.open(KART_JSON, FileAccess.READ)
	if f:
		kart_meta = JSON.parse_string(f.get_as_text())


func _hex(s, fallback: Color) -> Color:
	if typeof(s) == TYPE_STRING and String(s).begins_with("#"):
		return Color.html(s)
	return fallback


func _build_world() -> void:
	var L: Dictionary = T.light
	var S: Dictionary = T.sky
	# sky, fog, tone mapping
	var we := WorldEnvironment.new()
	env = Environment.new()
	env.background_mode = Environment.BG_SKY
	var sky := Sky.new()
	var sm := ShaderMaterial.new()
	sm.shader = load("res://shaders/sky.gdshader")
	sm.set_shader_parameter("top_col", _hex(S.get("top"), Color(0.24, 0.43, 0.7)))
	sm.set_shader_parameter("hor_col", _hex(S.get("hor"), Color(1, 0.7, 0.54)))
	sm.set_shader_parameter("bot_col", _hex(S.get("bot"), Color(0.16, 0.44, 0.52)))
	sm.set_shader_parameter("sun_col", _hex(S.get("sunCol"), Color(1, 0.85, 0.63)))
	sky.sky_material = sm
	sky.radiance_size = Sky.RADIANCE_SIZE_64
	env.sky = sky
	# the web game's lighting with its default "Vivid" look: hemisphere fill x0.7, sun x1.25, exposure x0.96,
	# a touch more contrast and saturation. Its fill is a warm cream from above, so the ambient is that colour,
	# with a little of the sky gradient (teal below) for the hemisphere's falloff.
	env.ambient_light_source = Environment.AMBIENT_SOURCE_SKY
	env.ambient_light_sky_contribution = 0.25
	env.ambient_light_color = _hex(L.get("hemiSky"), Color(1, 0.89, 0.77))
	env.ambient_light_energy = float(L.get("hemiI", 0.52)) * 0.7
	env.reflected_light_source = Environment.REFLECTION_SOURCE_SKY
	env.tonemap_mode = Environment.TONE_MAPPER_ACES
	# Godot's ACES pre-scales by 1.8 and normalises to its white point; the web game's (three.js) pre-scales by
	# 1/0.6 and doesn't normalise. A high white point and exposure x(1.667/1.8) make the two curves match.
	env.tonemap_white = 16.0
	env.tonemap_exposure = float(L.get("exposure", 0.92)) * 0.96 * (1.0 / 0.6) / 1.8
	env.adjustment_enabled = true
	env.adjustment_contrast = 1.07
	env.adjustment_saturation = 1.06
	if not is_phone:
		env.ssao_enabled = true
		env.ssao_radius = 2.5
		env.ssao_intensity = 1.6
		env.glow_enabled = true
		env.glow_intensity = 0.35
		env.glow_bloom = 0.04
		env.glow_hdr_threshold = 1.1
	var fog = L.get("fog")
	if typeof(fog) == TYPE_DICTIONARY:
		env.fog_enabled = true
		env.fog_mode = Environment.FOG_MODE_DEPTH
		var fd: Dictionary = fog
		env.fog_light_color = _hex(fd.get("color"), Color(0.94, 0.69, 0.55))
		env.fog_depth_begin = float(fd.get("near", 2600))
		env.fog_depth_end = float(fd.get("far", 11000))
		env.fog_depth_curve = 1.0
		env.fog_density = 1.0
		env.fog_sky_affect = 0.0
	we.environment = env
	add_child(we)

	# the sun
	sun = DirectionalLight3D.new()
	var sd: Array = L.get("sunDir", [0.84, 0.47, 0.26])
	var to_sun := Vector3(sd[0], sd[1], sd[2]).normalized()
	add_child(sun)
	sun.look_at_from_position(to_sun * 100.0, Vector3.ZERO, Vector3.UP)
	sun.light_color = _hex(L.get("sunColor"), Color(1, 0.84, 0.66))
	sun.light_energy = float(L.get("sunI", 3.25)) * 1.25
	sun.shadow_enabled = true
	sun.directional_shadow_mode = DirectionalLight3D.SHADOW_PARALLEL_2_SPLITS
	sun.directional_shadow_max_distance = 700.0
	sun.shadow_blur = 1.0

	# the track: exported cells; clutter cells ("_d") get distance culling like the web game
	var ps: PackedScene = load(TRACK_SCENE)
	var track := ps.instantiate()
	add_child(track)
	_prepare_track(track)


## Godot's glTF import doesn't switch vertex colours on in the materials it creates, and most of the
## scenery (and the kart's livery) gets its colour from them, as in the web game. Turn them on.
func _use_vertex_colours(root: Node) -> int:
	var n := 0
	for node in root.find_children("*", "MeshInstance3D", true, false):
		var am := (node as MeshInstance3D).mesh as ArrayMesh
		if am == null:
			continue
		for si in am.get_surface_count():
			var sm := am.surface_get_material(si) as StandardMaterial3D
			if sm != null and (am.surface_get_format(si) & Mesh.ARRAY_FORMAT_COLOR) != 0 and not sm.vertex_color_use_as_albedo:
				sm.vertex_color_use_as_albedo = true
				n += 1
	return n


func _prepare_track(root: Node) -> void:
	print("vertex colours switched on for %d track materials" % _use_vertex_colours(root))
	for n in root.find_children("*", "MeshInstance3D", true, false):
		var mi := n as MeshInstance3D
		var nm := String(mi.name)
		if nm.find("noshadow") >= 0:
			mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		var cell_name := String(mi.get_parent().name) if mi.get_parent() else ""
		if nm.find("_d_") >= 0 or nm.ends_with("_d") or cell_name.ends_with("_d"):
			var bb := mi.global_transform * mi.get_aabb()
			cull_list.append({"node": mi, "rect": Rect2(bb.position.x, bb.position.z, bb.size.x, bb.size.z), "vis": true})


func _build_kart() -> void:
	var ps: PackedScene = load(KART_SCENE)
	kart_node = Node3D.new()
	add_child(kart_node)
	var model := ps.instantiate()
	kart_node.add_child(model)
	var sc := float(kart_meta.get("scale", 2.024))
	kart_node.scale = Vector3.ONE * sc
	print("vertex colours switched on for %d kart materials" % _use_vertex_colours(model))
	body = model.find_child("body", true, false)
	for w in kart_meta.get("wheels", []):
		var wd: Dictionary = w
		var wn := model.find_child(String(wd["name"]), true, false)
		if wn:
			wheels.append({"node": wn, "r": float(wd["r"]), "front": bool(wd["front"])})


# ---------------------------------------------------------------- HUD

## anchors (0..1) and pixel offsets from them, like CSS positioning
func _place(c: Control, al: float, at: float, ar: float, ab: float, ol: float, ot: float, o_r: float, ob: float) -> void:
	c.anchor_left = al
	c.anchor_top = at
	c.anchor_right = ar
	c.anchor_bottom = ab
	c.offset_left = ol
	c.offset_top = ot
	c.offset_right = o_r
	c.offset_bottom = ob


func _label(size: int, pos: Vector2, align := HORIZONTAL_ALIGNMENT_LEFT) -> Label:
	var l := Label.new()
	l.add_theme_font_size_override("font_size", size)
	l.add_theme_color_override("font_color", Color(1, 0.96, 0.86))
	l.add_theme_color_override("font_outline_color", Color(0.1, 0.05, 0.03))
	l.add_theme_constant_override("outline_size", 8)
	l.position = pos
	l.horizontal_alignment = align
	return l


func _pedal(left: bool) -> Panel:
	var p := Panel.new()
	var sb := StyleBoxFlat.new()
	sb.bg_color = Color(0.1, 0.05, 0.03, 0.55)
	sb.border_color = Color(1, 0.96, 0.86, 0.45)
	sb.set_border_width_all(3)
	sb.set_corner_radius_all(22)
	p.add_theme_stylebox_override("panel", sb)
	p.mouse_filter = Control.MOUSE_FILTER_IGNORE
	if left:
		_place(p, 0, 1, 0, 1, 14, -204, 164, -14)
	else:
		_place(p, 1, 1, 1, 1, -164, -204, -14, -14)
	var l := Label.new()
	l.text = "DRIFT"
	l.add_theme_font_size_override("font_size", 22)
	l.add_theme_color_override("font_color", Color(1, 0.96, 0.86, 0.8))
	_place(l, 0, 0, 1, 1, 0, 0, 0, 0)
	l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	l.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	p.add_child(l)
	return p


func _button(text: String, pos: Vector2) -> Button:
	var b := Button.new()
	b.text = text
	b.add_theme_font_size_override("font_size", 22)
	_place(b, 1, 0, 1, 0, pos.x, pos.y, pos.x + 150, pos.y + 52)
	b.focus_mode = Control.FOCUS_NONE
	return b


func _build_hud() -> void:
	var ui := CanvasLayer.new()
	add_child(ui)
	var root := Control.new()
	root.set_anchors_preset(Control.PRESET_FULL_RECT)
	root.mouse_filter = Control.MOUSE_FILTER_IGNORE
	ui.add_child(root)
	lbl_lap = _label(40, Vector2(28, 18))
	root.add_child(lbl_lap)
	lbl_time = _label(30, Vector2(28, 66))
	root.add_child(lbl_time)
	lbl_info = _label(18, Vector2(28, 108))
	root.add_child(lbl_info)
	lbl_speed = _label(46, Vector2(0, 0), HORIZONTAL_ALIGNMENT_CENTER)
	_place(lbl_speed, 0.5, 1, 0.5, 1, -160, -96, 160, -30)
	root.add_child(lbl_speed)
	lbl_center = _label(96, Vector2(0, 0), HORIZONTAL_ALIGNMENT_CENTER)
	_place(lbl_center, 0.5, 0.5, 0.5, 0.5, -500, -170, 500, -30)
	root.add_child(lbl_center)
	pedal_l = _pedal(true)
	pedal_r = _pedal(false)
	root.add_child(pedal_l)
	root.add_child(pedal_r)
	btn_fps = _button("60 fps", Vector2(-166, 16))
	btn_fps.pressed.connect(_toggle_fps)
	root.add_child(btn_fps)
	btn_res = _button("Res 100%", Vector2(-326, 16))
	btn_res.pressed.connect(_toggle_res)
	root.add_child(btn_res)
	var rb := _button("Restart", Vector2(-486, 16))
	rb.pressed.connect(_restart)
	root.add_child(rb)


func _apply_display() -> void:
	fps_cap = 60 if is_phone else 0
	res_scale = 0.67 if is_phone else 1.0
	_apply_fps()
	_apply_res()


func _toggle_fps() -> void:
	fps_cap = 120 if fps_cap == 60 else (0 if fps_cap == 120 else 60)
	_apply_fps()


func _apply_fps() -> void:
	Engine.max_fps = fps_cap
	btn_fps.text = ("%d fps" % fps_cap) if fps_cap > 0 else "max fps"


func _toggle_res() -> void:
	var steps := [0.5, 0.67, 0.8, 1.0]
	var i := steps.find(res_scale)
	res_scale = steps[(i + 1) % steps.size()]
	_apply_res()


func _apply_res() -> void:
	var vp := get_viewport()
	vp.scaling_3d_mode = Viewport.SCALING_3D_MODE_FSR if res_scale < 0.99 else Viewport.SCALING_3D_MODE_BILINEAR
	vp.scaling_3d_scale = res_scale
	vp.fsr_sharpness = 0.25
	btn_res.text = "Res %d%%" % int(round(res_scale * 100.0))


# ---------------------------------------------------------------- race flow

func _restart() -> void:
	var slot: Dictionary = T.grid[0]
	var gi := 0
	for i in T.grid.size():
		var gslot: Dictionary = T.grid[i]
		if bool(gslot.get("player", false)):
			slot = T.grid[i]
			gi = i
	var p0: int = int(T.grid_prog[gi]) if gi < T.grid_prog.size() else 0
	kart = Kart.new()
	kart.setup(T, slot, p0)
	state = "countdown"
	cd = 3.2
	race_time = 0.0
	cam_a = kart.ma
	cam_snap = true
	_show_center("3", 1.0)


func _show_center(t: String, dur: float) -> void:
	lbl_center.text = t
	center_t = dur


func _physics_process(dt: float) -> void:
	if T == null:
		return
	if state == "countdown":
		var before := ceili(cd)
		cd -= dt
		var after := ceili(cd)
		if after != before and after > 0:
			_show_center(str(after), 1.0)
		if cd <= 0.0:
			state = "race"
			_show_center("GO!", 0.8)
		kart._save_prev()
		return
	var inp := _input_state()
	kart.step(inp, dt)
	if state == "race":
		race_time += dt
		if kart.prog >= T.LAPS * T.N:
			state = "finished"
			kart.finish_time = race_time
			_show_center("Finish!  " + _fmt(race_time), 4.0)
	for e in kart.events:
		if e.begins_with("boost") or e == "pad":
			shake = maxf(shake, 0.18)
		elif e == "bump":
			shake = maxf(shake, 0.25)
		elif e == "respawn":
			cam_snap = true
	kart.events.clear()


func _input_state() -> Dictionary:
	var steer := 0.0
	var brake := false
	var mul := 1.0
	# keyboard
	if Input.is_key_pressed(KEY_LEFT) or Input.is_key_pressed(KEY_A):
		steer -= 1.0
	if Input.is_key_pressed(KEY_RIGHT) or Input.is_key_pressed(KEY_D):
		steer += 1.0
	if Input.is_key_pressed(KEY_SPACE) or Input.is_key_pressed(KEY_SHIFT) or Input.is_key_pressed(KEY_DOWN) or Input.is_key_pressed(KEY_S):
		brake = true
	# controller: left stick steers, RT gas, LT drift
	var pads := Input.get_connected_joypads()
	if pads.size() > 0:
		var j: int = pads[0]
		var sx := Input.get_joy_axis(j, JOY_AXIS_LEFT_X)
		var rt := Input.get_joy_axis(j, JOY_AXIS_TRIGGER_RIGHT)
		var lt := Input.get_joy_axis(j, JOY_AXIS_TRIGGER_LEFT)
		if absf(sx) > 0.18 or rt > 0.2 or lt > 0.2:
			pad_used_at = Time.get_ticks_msec()
		if absf(sx) > 0.18:
			steer += signf(sx) * clampf((absf(sx) - 0.18) / 0.72, 0.0, 1.0)
		if lt > 0.3:
			brake = true
		if Time.get_ticks_msec() - pad_used_at < 20000 and rt < 0.2:
			mul = 0.0
	# touch
	var l := false
	var r := false
	for k in touches:
		var z: String = touches[k]
		if z == "pedal":
			brake = true
		elif z == "l":
			l = true
		elif z == "r":
			r = true
	if l:
		steer -= 1.0
	if r:
		steer += 1.0
	if auto_drive:
		var tj := (kart.idx + 14) % T.N
		var want := atan2(T.py[tj] - kart.y, T.px[tj] - kart.x)
		steer = clampf(Kart.ang_diff(want, kart.a) * 2.5, -1.0, 1.0)
	return {"steer": clampf(steer, -1.0, 1.0), "brake": brake, "nb": false, "mul": mul}


func _input(ev: InputEvent) -> void:
	if ev is InputEventScreenTouch:
		var t := ev as InputEventScreenTouch
		if t.pressed:
			touches[t.index] = _zone(t.position)
		else:
			touches.erase(t.index)
	elif ev is InputEventScreenDrag:
		var d := ev as InputEventScreenDrag
		if touches.has(d.index) and touches[d.index] != "pedal":
			touches[d.index] = _zone(d.position)
	elif ev is InputEventKey:
		var kev := ev as InputEventKey
		if kev.pressed and not kev.echo and kev.keycode == KEY_R:
			_restart()


func _zone(p: Vector2) -> String:
	if pedal_l.get_global_rect().has_point(p) or pedal_r.get_global_rect().has_point(p):
		return "pedal"
	return "l" if p.x < get_viewport().get_visible_rect().size.x * 0.5 else "r"


# ---------------------------------------------------------------- drawing

func _process(dt: float) -> void:
	if T == null:
		return
	var al := Engine.get_physics_interpolation_fraction()
	var k := kart
	var rx := lerpf(k.ox, k.x, al)
	var ry := lerpf(k.oy, k.y, al)
	var rz := lerpf(k.owy, k.wy, al)
	var ra := lerp_angle(k.oa, k.a, al)
	var rma := lerp_angle(k.oma, k.ma, al)
	# kart: model forward is +X; heading a turns +X toward +Z
	kart_node.position = Vector3(rx, rz, ry)
	kart_node.rotation = Vector3(0.0, -ra, 0.0)
	if body:
		var f := 1.0 - exp(-10.0 * dt)
		var roll := (k.steer * 0.08 * k.d_amt if k.drift != 0 else 0.0) + k.steer * 0.04
		body.rotation.x += (roll - body.rotation.x) * f
		body.rotation.z += (clampf(k.acc * 0.0006, -0.07, 0.05) - body.rotation.z) * f
	for w in wheels:
		var n: Node3D = w["node"]
		n.rotation.z -= k.speed * dt / (float(w["r"]) * T.KS)
		if w["front"]:
			n.rotation.y = -k.steer * 0.38

	# chase camera (the web game's close camera)
	cam_a = lerp_angle(cam_a, rma, 1.0 - exp(-5.5 * dt))
	var dist := 30.0 + (5.0 if k.boost > 0.0 else 0.0)
	var h := 12.6
	var fx := cos(cam_a)
	var fy := sin(cam_a)
	var rg := T.ground(rx, ry)
	var cy := (rz - 4.0) if k.glide else rg + (rz - rg) * 0.45
	var tv2 := Vector3(rx - fx * dist, cy + h, ry - fy * dist)
	var tv := Vector3(rx + fx * 32.0, cy + 6.2, ry + fy * 32.0)
	if cam_snap:
		cam_base = tv2
		cam_look = tv
		cam_snap = false
	else:
		cam_base = cam_base.lerp(tv2, 1.0 - exp(-12.0 * dt))
		cam_look = cam_look.lerp(tv, 1.0 - exp(-16.0 * dt))
	var sh := Vector3.ZERO
	if shake > 0.0:
		shake = maxf(0.0, shake - dt)
		sh = Vector3(randf_range(-1, 1), randf_range(-1, 1), randf_range(-1, 1)) * shake * 2.0
	cam.position = cam_base + sh
	cam.look_at(cam_look, Vector3.UP)
	var vs := get_viewport().get_visible_rect().size
	var aspect := vs.x / maxf(1.0, vs.y)
	var hf := deg_to_rad(96.0 if k.boost > 0.0 else 92.0)
	var vf := clampf(rad_to_deg(2.0 * atan(tan(hf / 2.0) / aspect)), 52.0, 100.0)
	cam.fov += (vf - cam.fov) * minf(1.0, 5.0 * dt)

	# far clutter cells, five times a second
	cull_t -= dt
	if cull_t <= 0.0:
		cull_t = 0.2
		var cp := Vector2(cam.global_position.x, cam.global_position.z)
		for c in cull_list:
			var rect: Rect2 = c["rect"]
			var q := Vector2(clampf(cp.x, rect.position.x, rect.end.x), clampf(cp.y, rect.position.y, rect.end.y))
			var dd := cp.distance_to(q)
			var was: bool = c["vis"]
			var v: bool = dd < (CULL_DIST * 1.08 if was else CULL_DIST)
			if v != was:
				c["vis"] = v
				(c["node"] as Node3D).visible = v

	# HUD
	lbl_lap.text = "Lap %d/%d" % [k.lap(), T.LAPS]
	lbl_time.text = _fmt(k.finish_time if state == "finished" else race_time)
	lbl_speed.text = "%d mph" % int(round(maxf(0.0, k.speed) * 0.66))
	var prims := int(Performance.get_monitor(Performance.RENDER_TOTAL_PRIMITIVES_IN_FRAME))
	var draws := int(Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME))
	lbl_info.text = "%d fps · %s · %dk tris · %d draws · drift %s" % [Engine.get_frames_per_second(), RenderingServer.get_current_rendering_driver_name(), prims / 1000, draws, ["", "blue", "orange", "pink"][k.tier] if k.drift != 0 else "-"]
	if center_t > 0.0:
		center_t -= dt
		if center_t <= 0.0:
			lbl_center.text = ""
	var piv := 1.0 if touches.values().has("pedal") else 0.55
	pedal_l.modulate.a = piv
	pedal_r.modulate.a = piv


func _fmt(t: float) -> String:
	var m := int(t / 60.0)
	var s := t - m * 60.0
	return "%d:%05.2f" % [m, s]


func _enter_tree() -> void:
	cam = Camera3D.new()
	cam.near = 0.5
	cam.far = 14000.0
	cam.fov = 70.0
	add_child(cam)
	cam.current = true
