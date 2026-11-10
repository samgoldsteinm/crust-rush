extends Node3D
## Race scene: Hawaiian Bay, eight karts, items. The simulation is in race.gd and kart.gd (ported
## from the web game, 120 Hz in _physics_process); this file draws it, interpolating between
## steps, and handles input, the HUD and the race flow.
## Keyboard (as on the web): arrows/WASD steer, Space/Down/S drift-brake, X/E/Enter first item,
## Z/Q/V second item, Shift/B keep an item behind, F look back, P or Esc pause, F11 full screen.
## Controller: left stick or d-pad, RT gas, LT drift, A/LB first item, B/RB second item, X look back, Start pause.

const TRACK_JSON := "res://assets/track/bay.json"
const TRACK_SCENE := "res://assets/track/bay.gltf"
const ROSTER_JSON := "res://assets/kart/roster.json"
const ITEMS_SCENE := "res://assets/items/items.glb"
const CULL_DIST := 2600.0   # far clutter cells hide beyond this (the web uses 1500-2250 by preset)
const ITEM_NAMES := {"chili": "Chili Boost", "pepperoni": "Pepperoni", "oil": "Olive Oil", "dough": "Dough Ball", "trio": "Pepperoni Trio", "garlic": "Garlic Shield", "flour": "Flour Bomb", "wheel": "Pizza Wheel", "rush": "Delivery Rush"}
const PROJ_NODE := {"pep": "pep", "dough": "dough", "flour": "flour", "lob": "lob", "wheel": "wheel"}
const HELD_NODE := {"pepperoni": "pep", "dough": "dough", "flour": "flour"}
const HIT_COL := {"pep": Color(1, 0.35, 0.16), "dough": Color(1, 0.89, 0.63), "flour": Color(1, 1, 1), "oil": Color(0.91, 0.7, 0.23), "wheel": Color(1, 0.23, 0.1), "garlic": Color(0.5, 0.88, 0.48)}

var T: TrackData
var race: Race
var roster := {}
var kart: Kart               # the player's kart (kept for the tests)
var views := {}              # Kart -> {node, body, wheels, sc, bubble, held}
var kart_scenes := {}        # file -> PackedScene
var items_lib: Node3D
var cam: Camera3D
var sun: DirectionalLight3D
var env: Environment

var state := "countdown"     # countdown | race | finished | results
var cd := 3.2
var fin_t := 0.0
var cam_a := 0.0
var cam_base := Vector3.ZERO
var cam_look := Vector3.ZERO
var cam_snap := true
var shake := 0.0
var cull_list: Array = []    # {node, rect: Rect2 in ground x/z}
var cull_t := 0.0
var auto_drive := false      # set by the tests: the computer drives the player's kart
var paused := false
var time := 0.0
var last_lap := 1

# things drawn for the race
var box_nodes: Array = []    # one Node3D per race.boxes entry
var proj_nodes := {}         # id -> Node3D
var haz_nodes := {}          # id -> Node3D
var fx_root: Node3D
var sfx: Sfx
var roll_tick := 0.0

# input
var touches := {}            # index -> "l" | "r" | "pedal"
var pad_used_at := -1e9
var item_queued := ""        # "fwd" | "fwd2" | "hold" | "hold2"
var pad_held := [false, false, false]
var pad_hold := [0, 0, 0]
var look_back := false

# HUD
var ui_root: Control
var lbl_pos: Label
var lbl_lap: Label
var lbl_time: Label
var lbl_speed: Label
var lbl_info: Label
var lbl_center: Label
var lbl_toast: Label
var slot1: TextureRect
var slot2: TextureRect
var slot1_bg: Panel
var slot2_bg: Panel
var lbl_item: Label
var mini: MiniMap
var pedal_l: Panel
var pedal_r: Panel
var btn_fps: Button
var btn_res: Button
var panel_results: PanelContainer
var results_box: VBoxContainer
var panel_pause: PanelContainer
var icons := {}
var center_t := 0.0
var toast_t := 0.0
var fps_cap := 60
var res_scale := 1.0
var is_phone := false
var quality := 2             # 0 Low (the web look), 1 High, 2 Ultra
var hud_race: Control
var panel_menu: PanelContainer
var lbl_menu: Label
var ip_edit: LineEdit
var btn_start_net: Button
var btn_leave_net: Button
var btn_again: Button
var skip_menu := false       # tests go straight to the race
var shown_finish := false
var p_ka := 0.0              # the player's kart as drawn: heading and angle round the loop
var p_th := 0.0

# online, PC to PC: the host runs the race; everyone else sends their controls and draws what the host sends back
const NET_PORT := 24680
const SNAP_EVERY := 4        # physics steps between snapshots (30 a second)
var net_role := ""           # "" | "host" | "client"
var net_peers: Array[int] = []
var net_tick := 0
var net_snaps := 0
var net_snap_at := 0.0
var net_snap_dt := 1.0 / 30.0
var net_fresh := true
var net_out: Array = []
var net_addr := ""
var net_ready := false       # client: the connection to the host is up
var upnp_thread: Thread
var btn_quality: Button
var stats := {"used": {}, "spins": 0, "boxes": 0, "player_spins": 0}


func _ready() -> void:
	is_phone = OS.has_feature("mobile") or DisplayServer.is_touchscreen_available() and OS.get_name() in ["iOS", "Android"]
	quality = 0 if is_phone else 2
	process_mode = Node.PROCESS_MODE_ALWAYS
	T = TrackData.load_from(TRACK_JSON)
	if T == null:
		return
	var f := FileAccess.open(ROSTER_JSON, FileAccess.READ)
	if f:
		roster = JSON.parse_string(f.get_as_text())
	_build_world()
	_load_items()
	fx_root = Node3D.new()
	add_child(fx_root)
	sfx = Sfx.new()
	add_child(sfx)
	_build_hud()
	_apply_display()
	multiplayer.peer_connected.connect(_on_peer_in)
	multiplayer.peer_disconnected.connect(_on_peer_out)
	multiplayer.connected_to_server.connect(_on_connected)
	multiplayer.connection_failed.connect(_on_failed)
	multiplayer.server_disconnected.connect(_on_server_gone)
	if skip_menu or auto_drive:
		_start_race({})
	else:
		_to_menu("")


# ---------------------------------------------------------------- world

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
	sky.radiance_size = Sky.RADIANCE_SIZE_128 if not is_phone else Sky.RADIANCE_SIZE_64
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
	Gfx.apply_environment(env, sun, quality, is_phone)

	# the track: exported cells; clutter cells ("_d") get distance culling like the web game
	var ps: PackedScene = load(TRACK_SCENE)
	var track := ps.instantiate()
	add_child(track)
	_prepare_track(track)
	var up := Gfx.upgrade_track(track, quality, T.R, [Color.html("#2a8fb0"), Color.html("#06384a")])
	print("surface detail: %d flat-coloured materials given grain, %d textured ones given relief, %d water sheets" % [up[0], up[1], up[2]])


## Godot's glTF import doesn't switch vertex colours on in the materials it creates, and most of the
## scenery (and the karts' paint) gets its colour from them, as in the web game. Turn them on.
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


func _load_items() -> void:
	var ps: PackedScene = load(ITEMS_SCENE)
	if ps == null:
		return
	items_lib = ps.instantiate()
	_use_vertex_colours(items_lib)
	for k in ITEM_NAMES:
		var p := "res://assets/items/icon_%s.png" % k
		if ResourceLoader.exists(p):
			icons[k] = load(p)


## a copy of one of the web game's item models (pep, dough, oil, flour, wheel, itembox...)
func _item_node(name_: String) -> Node3D:
	var n3 := Node3D.new()
	if items_lib != null:
		var src := items_lib.find_child(name_, true, false)
		if src != null:
			var c := src.duplicate() as Node3D
			c.transform = Transform3D.IDENTITY
			n3.add_child(c)
			return n3
	var mi := MeshInstance3D.new()
	var sp := SphereMesh.new()
	sp.radius = 2.5
	sp.height = 5.0
	mi.mesh = sp
	n3.add_child(mi)
	return n3


# ---------------------------------------------------------------- karts

func _kart_view(k: Kart) -> Dictionary:
	var info: Dictionary = k.info
	var file := String(info.get("file", "player.glb"))
	if not kart_scenes.has(file):
		kart_scenes[file] = load("res://assets/kart/" + file)
	var node := Node3D.new()
	add_child(node)
	var ps: PackedScene = kart_scenes[file]
	var model := ps.instantiate()
	node.add_child(model)
	_use_vertex_colours(model)
	Gfx.upgrade_kart(model, quality)
	var meta: Dictionary = info.get("meta", {})
	var sc := float(meta.get("scale", 2.024))
	var wheels: Array = []
	for w in meta.get("wheels", []):
		var wd: Dictionary = w
		var wn := model.find_child(String(wd["name"]), true, false)
		if wn:
			wheels.append({"node": wn, "r": float(wd["r"]), "front": bool(wd["front"])})
	# garlic shield: a soft green bubble, shown while a layer is up
	var bub := MeshInstance3D.new()
	var sp := SphereMesh.new()
	sp.radius = 13.0
	sp.height = 22.0
	bub.mesh = sp
	var bm := StandardMaterial3D.new()
	bm.albedo_color = Color(0.6, 1.0, 0.62, 0.22)
	bm.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	bm.emission_enabled = true
	bm.emission = Color(0.45, 0.9, 0.5)
	bm.emission_energy_multiplier = 0.6
	bm.rim_enabled = true
	bm.rim = 1.0
	bm.roughness = 0.1
	bm.cull_mode = BaseMaterial3D.CULL_DISABLED
	bub.material_override = bm
	bub.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	bub.visible = false
	add_child(bub)
	var flame := _emitter(Color(1.0, 0.55, 0.12), 48, 0.28, 3.4, 70.0)
	var sparks := _emitter(Color(0.4, 0.75, 1.0), 40, 0.35, 1.3, 55.0)
	sparks.gravity = Vector3(0, -120, 0)
	sparks.spread = 50.0
	return {"node": node, "body": model.find_child("body", true, false), "wheels": wheels, "sc": sc, "bubble": bub, "held": null, "held_it": "", "top": float(meta.get("top", 7.0)), "flame": flame, "sparks": sparks, "ax_r": float(meta.get("axR", -3.0)) * sc}


## a stream of glowing particles (boost flames, drift sparks); switched on and off per kart
func _emitter(col: Color, amount: int, life: float, size: float, speed: float) -> CPUParticles3D:
	var p := CPUParticles3D.new()
	p.emitting = false
	p.amount = amount
	p.lifetime = life
	p.local_coords = false
	p.direction = Vector3(-1, 0.12, 0)
	p.spread = 14.0
	p.initial_velocity_min = speed * 0.6
	p.initial_velocity_max = speed
	p.gravity = Vector3(0, 12, 0)
	p.scale_amount_min = size * 0.6
	p.scale_amount_max = size
	var curve := Curve.new()
	curve.add_point(Vector2(0, 1))
	curve.add_point(Vector2(1, 0))
	p.scale_amount_curve = curve
	p.color = col
	var qm := QuadMesh.new()
	var m := StandardMaterial3D.new()
	m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	m.billboard_mode = BaseMaterial3D.BILLBOARD_PARTICLES
	m.vertex_color_use_as_albedo = true
	m.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
	m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	m.albedo_color = Color(1, 1, 1, 0.9)
	qm.material = m
	p.mesh = qm
	p.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	add_child(p)
	return p


func _clear_race_nodes() -> void:
	for k in views:
		var v: Dictionary = views[k]
		(v["node"] as Node).queue_free()
		(v["bubble"] as Node).queue_free()
		(v["flame"] as Node).queue_free()
		(v["sparks"] as Node).queue_free()
		if v["held"] != null:
			(v["held"] as Node).queue_free()
	views.clear()
	for n in box_nodes:
		(n as Node).queue_free()
	box_nodes.clear()
	for id in proj_nodes:
		(proj_nodes[id] as Node).queue_free()
	proj_nodes.clear()
	for id in haz_nodes:
		(haz_nodes[id] as Node).queue_free()
	haz_nodes.clear()


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
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return l


func _box_style(bg: Color, border: Color, radius: int, bw := 3) -> StyleBoxFlat:
	var sb := StyleBoxFlat.new()
	sb.bg_color = bg
	sb.border_color = border
	sb.set_border_width_all(bw)
	sb.set_corner_radius_all(radius)
	return sb


func _pedal(left: bool) -> Panel:
	var p := Panel.new()
	p.add_theme_stylebox_override("panel", _box_style(Color(0.1, 0.05, 0.03, 0.55), Color(1, 0.96, 0.86, 0.45), 22))
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
	b.add_theme_font_size_override("font_size", 20)
	_place(b, 1, 0, 1, 0, pos.x, pos.y, pos.x + 140, pos.y + 44)
	b.focus_mode = Control.FOCUS_NONE
	return b


func _slot(x: float, size: float) -> Array:
	var bg := Panel.new()
	bg.add_theme_stylebox_override("panel", _box_style(Color(0.1, 0.05, 0.03, 0.6), Color(1, 0.82, 0.3, 0.9), int(size * 0.24), 4))
	bg.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_place(bg, 0.5, 0, 0.5, 0, x, 18, x + size, 18 + size)
	var tr := TextureRect.new()
	tr.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	tr.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	tr.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_place(tr, 0, 0, 1, 1, 6, 6, -6, -6)
	bg.add_child(tr)
	return [bg, tr]


func _build_hud() -> void:
	var ui := CanvasLayer.new()
	add_child(ui)
	var root := Control.new()
	root.set_anchors_preset(Control.PRESET_FULL_RECT)
	root.mouse_filter = Control.MOUSE_FILTER_IGNORE
	ui.add_child(root)
	ui_root = root
	hud_race = Control.new()
	hud_race.set_anchors_preset(Control.PRESET_FULL_RECT)
	hud_race.mouse_filter = Control.MOUSE_FILTER_IGNORE
	root.add_child(hud_race)
	lbl_pos = _label(92, Vector2(0, 0))
	_place(lbl_pos, 0, 1, 0, 1, 30, -150, 330, -24)
	lbl_pos.add_theme_constant_override("outline_size", 14)
	hud_race.add_child(lbl_pos)
	lbl_lap = _label(38, Vector2(28, 16))
	hud_race.add_child(lbl_lap)
	lbl_time = _label(28, Vector2(28, 62))
	hud_race.add_child(lbl_time)
	lbl_info = _label(15, Vector2(28, 102))
	lbl_info.modulate.a = 0.75
	hud_race.add_child(lbl_info)
	lbl_speed = _label(40, Vector2(0, 0), HORIZONTAL_ALIGNMENT_RIGHT)
	_place(lbl_speed, 1, 1, 1, 1, -330, -86, -30, -24)
	hud_race.add_child(lbl_speed)
	lbl_center = _label(110, Vector2(0, 0), HORIZONTAL_ALIGNMENT_CENTER)
	_place(lbl_center, 0.5, 0.5, 0.5, 0.5, -600, -200, 600, -40)
	lbl_center.add_theme_constant_override("outline_size", 16)
	root.add_child(lbl_center)
	lbl_toast = _label(34, Vector2(0, 0), HORIZONTAL_ALIGNMENT_CENTER)
	_place(lbl_toast, 0.5, 0, 0.5, 0, -500, 130, 500, 180)
	hud_race.add_child(lbl_toast)
	# two item slots, top centre: the big one fires first
	var s1 := _slot(-58, 104)
	slot1_bg = s1[0]
	slot1 = s1[1]
	hud_race.add_child(slot1_bg)
	var s2 := _slot(58, 70)
	slot2_bg = s2[0]
	slot2 = s2[1]
	hud_race.add_child(slot2_bg)
	lbl_item = _label(20, Vector2(0, 0), HORIZONTAL_ALIGNMENT_CENTER)
	_place(lbl_item, 0.5, 0, 0.5, 0, -200, 124, 200, 150)
	hud_race.add_child(lbl_item)
	mini = MiniMap.new()
	mini.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_place(mini, 1, 0, 1, 0, -250, 70, -20, 300)
	hud_race.add_child(mini)
	pedal_l = _pedal(true)
	pedal_r = _pedal(false)
	hud_race.add_child(pedal_l)
	hud_race.add_child(pedal_r)
	pedal_l.visible = is_phone
	pedal_r.visible = is_phone
	btn_fps = _button("60 fps", Vector2(-156, 14))
	btn_fps.pressed.connect(_toggle_fps)
	hud_race.add_child(btn_fps)
	btn_res = _button("Res 100%", Vector2(-306, 14))
	btn_res.pressed.connect(_toggle_res)
	hud_race.add_child(btn_res)
	var pb := _button("Pause", Vector2(-456, 14))
	pb.pressed.connect(_toggle_pause)
	hud_race.add_child(pb)

	# results
	panel_results = PanelContainer.new()
	panel_results.add_theme_stylebox_override("panel", _box_style(Color(0.12, 0.06, 0.04, 0.9), Color(1, 0.82, 0.3), 26, 4))
	_place(panel_results, 0.5, 0.5, 0.5, 0.5, -330, -330, 330, 330)
	var mg := MarginContainer.new()
	for side in ["margin_left", "margin_right", "margin_top", "margin_bottom"]:
		mg.add_theme_constant_override(side, 26)
	panel_results.add_child(mg)
	results_box = VBoxContainer.new()
	results_box.add_theme_constant_override("separation", 8)
	mg.add_child(results_box)
	panel_results.visible = false
	root.add_child(panel_results)

	# pause
	panel_pause = PanelContainer.new()
	panel_pause.add_theme_stylebox_override("panel", _box_style(Color(0.12, 0.06, 0.04, 0.92), Color(1, 0.82, 0.3), 26, 4))
	_place(panel_pause, 0.5, 0.5, 0.5, 0.5, -230, -285, 230, 285)
	var mg2 := MarginContainer.new()
	for side in ["margin_left", "margin_right", "margin_top", "margin_bottom"]:
		mg2.add_theme_constant_override(side, 26)
	panel_pause.add_child(mg2)
	var vb := VBoxContainer.new()
	vb.add_theme_constant_override("separation", 14)
	mg2.add_child(vb)
	var pt := _label(44, Vector2.ZERO, HORIZONTAL_ALIGNMENT_CENTER)
	pt.text = "Paused"
	vb.add_child(pt)
	for spec in [["Resume", _toggle_pause], ["Restart race", _restart], ["Graphics: Ultra", _cycle_quality], ["Full screen", _toggle_fullscreen], ["Main menu", _to_menu.bind("")], ["Quit", _quit]]:
		var b := Button.new()
		b.text = spec[0]
		b.add_theme_font_size_override("font_size", 26)
		b.custom_minimum_size = Vector2(0, 54)
		b.pressed.connect(spec[1])
		vb.add_child(b)
		if String(spec[0]).begins_with("Graphics"):
			btn_quality = b
	panel_pause.visible = false
	root.add_child(panel_pause)

	# main menu
	panel_menu = PanelContainer.new()
	panel_menu.add_theme_stylebox_override("panel", _box_style(Color(0.12, 0.06, 0.04, 0.88), Color(1, 0.82, 0.3), 30, 4))
	_place(panel_menu, 0.5, 0.5, 0.5, 0.5, -300, -330, 300, 330)
	var mg3 := MarginContainer.new()
	for side in ["margin_left", "margin_right", "margin_top", "margin_bottom"]:
		mg3.add_theme_constant_override(side, 30)
	panel_menu.add_child(mg3)
	var mv := VBoxContainer.new()
	mv.add_theme_constant_override("separation", 14)
	mg3.add_child(mv)
	var title := _label(72, Vector2.ZERO, HORIZONTAL_ALIGNMENT_CENTER)
	title.text = "CRUST RUSH"
	title.add_theme_color_override("font_color", Color(1, 0.82, 0.3))
	title.add_theme_constant_override("outline_size", 14)
	mv.add_child(title)
	lbl_menu = _label(20, Vector2.ZERO, HORIZONTAL_ALIGNMENT_CENTER)
	lbl_menu.text = "Hawaiian Bay  ·  3 laps  ·  8 racers"
	lbl_menu.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	lbl_menu.custom_minimum_size = Vector2(520, 0)
	mv.add_child(lbl_menu)
	var mb := func(text: String, fn: Callable) -> Button:
		var b2 := Button.new()
		b2.text = text
		b2.add_theme_font_size_override("font_size", 28)
		b2.custom_minimum_size = Vector2(0, 58)
		b2.pressed.connect(fn)
		mv.add_child(b2)
		return b2
	var race_btn: Button = mb.call("Race", _menu_race)
	mb.call("Host an online race", _menu_host)
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 10)
	ip_edit = LineEdit.new()
	ip_edit.placeholder_text = "Host's address, e.g. 192.168.1.20"
	ip_edit.add_theme_font_size_override("font_size", 22)
	ip_edit.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	ip_edit.custom_minimum_size = Vector2(0, 54)
	row.add_child(ip_edit)
	var jb := Button.new()
	jb.text = "Join"
	jb.add_theme_font_size_override("font_size", 26)
	jb.custom_minimum_size = Vector2(120, 54)
	jb.pressed.connect(_menu_join)
	row.add_child(jb)
	mv.add_child(row)
	btn_start_net = mb.call("Start the online race", _net_start)
	btn_leave_net = mb.call("Leave online", _menu_leave)
	mb.call("Quit", _quit)
	btn_start_net.visible = false
	btn_leave_net.visible = false
	panel_menu.visible = false
	root.add_child(panel_menu)
	race_btn.grab_focus.call_deferred()


func _apply_display() -> void:
	fps_cap = 60 if is_phone else 0
	res_scale = 0.67 if is_phone else 1.0
	_apply_fps()
	_apply_res()
	Gfx.apply_viewport(get_viewport(), quality, is_phone)
	btn_quality.text = "Graphics: " + ["Low", "High", "Ultra"][quality]


## Ultra -> High -> Low -> Ultra: lighting, shadows and screen effects change at once
func _cycle_quality() -> void:
	quality = (quality + 2) % 3
	Gfx.apply_environment(env, sun, quality, is_phone)
	Gfx.apply_viewport(get_viewport(), quality, is_phone)
	btn_quality.text = "Graphics: " + ["Low", "High", "Ultra"][quality]


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


func _toggle_fullscreen() -> void:
	var w := get_window()
	w.mode = Window.MODE_MAXIMIZED if w.mode == Window.MODE_FULLSCREEN or w.mode == Window.MODE_EXCLUSIVE_FULLSCREEN else Window.MODE_FULLSCREEN


func _toggle_pause() -> void:
	if state == "results" or state == "menu":
		return
	if net_role != "":
		# an online race carries on for everyone: this only opens the menu
		panel_pause.visible = not panel_pause.visible
		return
	paused = not paused
	panel_pause.visible = paused


func _quit() -> void:
	get_tree().quit()


# ---------------------------------------------------------------- race flow

func _restart() -> void:
	if net_role == "host":
		_net_start()
	elif net_role == "client":
		_toast("Only the host can restart the race")
	else:
		_start_race({})


## builds the grid: a one-player race, or (online) the configuration the host sent
func _start_race(cfg: Dictionary) -> void:
	paused = false
	panel_pause.visible = false
	panel_results.visible = false
	panel_menu.visible = false
	hud_race.visible = true
	_clear_race_nodes()
	race = Race.new()
	var pri := int((roster.get("player", {}) as Dictionary).get("ri", 1))
	if cfg.is_empty():
		race.setup(T, roster, pri)
	else:
		race.setup_cfg(T, roster, cfg, multiplayer.get_unique_id())
	kart = race.player
	if auto_drive and net_role != "client":
		kart.ai["auto"] = true
	for k in race.karts:
		views[k] = _kart_view(k)
	for b in race.boxes:
		var n := _item_node("itembox2" if bool(b["dbl"]) else "itembox")
		add_child(n)
		box_nodes.append(n)
	state = "countdown"
	cd = 3.2
	fin_t = 0.0
	last_lap = 1
	shown_finish = false
	net_fresh = true
	net_out.clear()
	cam_a = kart.ma
	cam_snap = true
	stats = {"used": {}, "spins": 0, "boxes": 0, "player_spins": 0}
	_show_center("3", 1.0)


func _show_center(t: String, dur: float) -> void:
	lbl_center.text = t
	center_t = dur


func _toast(t: String, dur := 1.6) -> void:
	lbl_toast.text = t
	toast_t = dur


func _ordinal(n: int) -> String:
	var suf := "th"
	if n % 100 < 11 or n % 100 > 13:
		suf = ["th", "st", "nd", "rd", "th", "th", "th", "th", "th", "th"][n % 10]
	return "%d%s" % [n, suf]


func _physics_process(dt: float) -> void:
	if T == null or race == null:
		return
	if state == "menu":
		return
	if net_role == "client":
		_net_client_tick()
		return
	if paused:
		return
	_sim_tick(dt)
	if net_role == "host":
		_net_host_tick()


func _sim_tick(dt: float) -> void:
	if auto_drive and kart != null:
		kart.ai["auto"] = true
	if state == "countdown":
		var before := ceili(cd)
		cd -= dt
		var after := ceili(cd)
		if after != before and after > 0:
			_show_center(str(after), 1.0)
			sfx.play("beep")
		if cd <= 0.0:
			state = "race"
			race.state = "race"
			_show_center("GO!", 0.8)
			sfx.play("go")
		for k in race.karts:
			k._save_prev()
		return
	race.update(dt, _input_state())
	_drain_events()
	if state == "race":
		_finish_check()
		# the race is over once every person has finished (the computer drivers get estimated times)
		var all_done := true
		for k in race.karts:
			if k.peer != 0 and not k.finished:
				all_done = false
			elif k.peer != 0 and k.remote:
				k.ai["auto"] = true
		if all_done:
			state = "finished"
			fin_t = 3.5
	elif state == "finished":
		fin_t -= dt
		if fin_t <= 0.0:
			race.finalize()
			state = "results"
			_show_results()
	if state == "race":
		_lap_check()


func _finish_check() -> void:
	if kart.finished and not shown_finish:
		shown_finish = true
		kart.ai["auto"] = true
		_show_center("Finish!  %s" % _ordinal(kart.place), 3.0)
		sfx.play("finish")


func _lap_check() -> void:
	var lp := kart.lap()
	if lp != last_lap and not kart.finished:
		last_lap = lp
		_toast("Final lap!" if lp == T.LAPS else "Lap %d" % lp, 2.0)
		sfx.play("lap", 1.0, 1.2 if lp == T.LAPS else 1.0)


func _drain_events() -> void:
	if net_role == "host" and not net_peers.is_empty():
		for i in race.karts.size():
			for e in race.karts[i].events:
				net_out.append(["e", i, e])
		for e in race.fx:
			var d: Dictionary = (e as Dictionary).duplicate()
			for key in ["k", "a", "b"]:
				if d.has(key) and d[key] is Kart:
					d[key] = race.karts.find(d[key])
			net_out.append(d)
	for k in race.karts:
		for e in k.events:
			if k == kart:
				if e.begins_with("boost") or e == "pad" or e == "loopout":
					shake = maxf(shake, 0.18)
					sfx.play("boost", 0.8, 1.0 + 0.12 * (int(e.right(1)) if e.begins_with("boost") else 0))
				elif e == "bump":
					shake = maxf(shake, 0.25)
					sfx.play("bump", 0.8)
				elif e == "respawn":
					cam_snap = true
					sfx.play("bump")
				elif e == "land":
					shake = maxf(shake, 0.2)
					sfx.play("land", 0.7)
				elif e == "hop":
					sfx.play("hop", 0.6)
				elif e.begins_with("tier"):
					sfx.play("tier", 0.6, 0.8 + 0.2 * int(e.right(1)))
				elif e == "trick":
					sfx.play("trick", 0.7)
				elif e == "ready":
					sfx.play("ready", 0.8)
				elif e == "loopin":
					sfx.play("boost", 0.7, 1.3)
			if e.begins_with("boost") or e == "pad":
				_burst(_kpos(k) + Vector3(0, 3, 0), Color(1, 0.7, 0.2), 14, 60.0, 1.6, 0.35)
		k.events.clear()
	for e in race.fx:
		var ed: Dictionary = e
		var t: String = ed["t"]
		if t == "spin":
			var k: Kart = ed["k"]
			stats["spins"] = int(stats["spins"]) + 1
			var col: Color = HIT_COL.get(String(ed["kind"]), Color(1, 0.9, 0.5))
			_burst(_kpos(k) + Vector3(0, 6, 0), col, 34, 90.0, 3.0, 0.6)
			_burst(_kpos(k) + Vector3(0, 6, 0), Color(1, 1, 1), 14, 60.0, 2.0, 0.4)
			sfx.play("hit", _near(k))
			if k == kart:
				stats["player_spins"] = int(stats["player_spins"]) + 1
				shake = maxf(shake, 1.0)
				_toast("Spun out!", 1.2)
		elif t == "box":
			stats["boxes"] = int(stats["boxes"]) + 1
			_burst(Vector3(float(ed["x"]), float(ed["h"]) + 7.0, float(ed["y"])), Color(1, 0.85, 0.3), 30, 85.0, 2.4, 0.6)
			_burst(Vector3(float(ed["x"]), float(ed["h"]) + 7.0, float(ed["y"])), Color(0.9, 0.3, 0.2), 16, 60.0, 2.4, 0.6)
			sfx.play("pickup", 0.8 if ed["k"] == kart else _near(ed["k"]) * 0.3)
		elif t == "use":
			var it: String = ed["it"]
			stats["used"][it] = int(stats["used"].get(it, 0)) + 1
			var k2: Kart = ed["k"]
			_burst(_kpos(k2) + Vector3(0, 7, 0), Color(1, 0.88, 0.4), 10, 45.0, 2.0, 0.35)
			sfx.play("boost" if (it == "chili" or it == "rush") else "throw", 0.9 if k2 == kart else _near(k2) * 0.5)
			if k2 == kart:
				shake = maxf(shake, 0.18)
		elif t == "shield":
			stats["used"]["garlic"] = int(stats["used"].get("garlic", 0)) + 1
			_burst(_kpos(ed["k"]) + Vector3(0, 7, 0), Color(0.5, 0.88, 0.48), 24, 60.0, 2.4, 0.5)
			sfx.play("shield", 0.8 if ed["k"] == kart else _near(ed["k"]) * 0.4)
		elif t == "unshield" or t == "absorb":
			var k3: Kart = ed["k"]
			_burst(_kpos(k3) + Vector3(0, 7, 0), Color(0.78, 1.0, 0.75), 36, 110.0, 3.0, 0.5)
			sfx.play("block", 0.9 if k3 == kart else _near(k3) * 0.5)
			if k3 == kart:
				shake = maxf(shake, 0.3)
				_toast("Blocked!", 1.0)
		elif t == "flour":
			var p := Vector3(float(ed["x"]), T.ground(float(ed["x"]), float(ed["y"])) + 5.0, float(ed["y"]))
			_burst(p, Color(0.96, 0.94, 0.9), 60, 70.0, 9.0, 1.3, 0.2)
			sfx.play("boom", clampf(1.0 - p.distance_to(cam.global_position) / 500.0, 0.0, 1.0))
			if p.distance_to(cam.global_position) < 140.0:
				shake = maxf(shake, 0.5)
		elif t == "clash":
			var p2 := Vector3(float(ed["x"]), T.ground(float(ed["x"]), float(ed["y"])) + 6.0, float(ed["y"]))
			_burst(p2, Color(1, 0.8, 0.3), 26, 90.0, 3.0, 0.4)
		elif t == "bump":
			_burst(Vector3(float(ed["x"]), float(ed["h"]), float(ed["y"])), Color(1, 0.83, 0.42), 10, 80.0, 1.6, 0.25)
			if ed["a"] == kart or ed["b"] == kart:
				shake = maxf(shake, 0.22)
				sfx.play("bump", 0.6)
		elif t == "slice":
			var k4: Kart = ed["k"]
			_burst(_kpos(k4) + Vector3(0, 8, 0), Color(1, 0.23, 0.1), 56, 130.0, 4.0, 0.7)
			sfx.play("boom", maxf(0.3, _near(k4)))
			if k4 == kart:
				shake = maxf(shake, 1.6)
		elif t == "wind":
			if ed["k"] == kart:
				_toast("Pizza Wheel!", 1.0)
				sfx.play("warn")
		elif t == "oily":
			if ed["k"] == kart:
				_toast("Oily wheels!", 1.0)
	race.fx.clear()


func _kpos(k: Kart) -> Vector3:
	return Vector3(k.x, k.wy, k.y)


## how loud something at a kart sounds from the camera: 1 next to it, 0 far away
func _near(k: Kart) -> float:
	return clampf(1.0 - _kpos(k).distance_to(cam.global_position) / 420.0, 0.0, 1.0)


## a quick puff of coloured sparks
func _burst(pos: Vector3, col: Color, n: int, speed: float, size: float, life: float, gravity := 1.0) -> void:
	if DisplayServer.get_name() == "headless":
		return
	var p := CPUParticles3D.new()
	p.one_shot = true
	p.explosiveness = 0.95
	p.amount = n
	p.lifetime = life
	p.direction = Vector3.UP
	p.spread = 180.0
	p.initial_velocity_min = speed * 0.35
	p.initial_velocity_max = speed
	p.gravity = Vector3(0, -90.0 * gravity, 0)
	p.damping_min = speed * 0.6
	p.damping_max = speed * 1.2
	p.scale_amount_min = size * 0.5
	p.scale_amount_max = size
	var curve := Curve.new()
	curve.add_point(Vector2(0, 1))
	curve.add_point(Vector2(1, 0))
	p.scale_amount_curve = curve
	var qm := QuadMesh.new()
	qm.size = Vector2(1, 1)
	var m := StandardMaterial3D.new()
	m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	m.billboard_mode = BaseMaterial3D.BILLBOARD_PARTICLES
	m.albedo_color = col
	m.emission_enabled = true
	m.emission = col
	m.emission_energy_multiplier = 1.5
	m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	qm.material = m
	p.mesh = qm
	p.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	fx_root.add_child(p)
	p.global_position = pos
	p.emitting = true
	get_tree().create_timer(life + 0.3).timeout.connect(p.queue_free)


func _show_results() -> void:
	for c in results_box.get_children():
		c.queue_free()
	var title := _label(46, Vector2.ZERO, HORIZONTAL_ALIGNMENT_CENTER)
	title.text = "Results"
	results_box.add_child(title)
	var st := race.standings()
	for i in st.size():
		var k := st[i]
		var row := HBoxContainer.new()
		var a := _label(26, Vector2.ZERO)
		a.text = "%s   %s%s" % [_ordinal(i + 1), k.racer_name, "  (you)" if k == kart else ""]
		a.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		if k == kart:
			a.add_theme_color_override("font_color", Color(1, 0.82, 0.3))
		row.add_child(a)
		var b := _label(26, Vector2.ZERO, HORIZONTAL_ALIGNMENT_RIGHT)
		b.text = ("~" if k.est else "") + _fmt(k.finish_time)
		row.add_child(b)
		var c := _label(22, Vector2.ZERO, HORIZONTAL_ALIGNMENT_RIGHT)
		c.text = "  +%d" % (Race.PTS[i] if i < Race.PTS.size() else 0)
		c.custom_minimum_size = Vector2(64, 0)
		row.add_child(c)
		results_box.add_child(row)
	var again := Button.new()
	again.text = "Race again" if net_role != "client" else "Waiting for the host"
	again.disabled = net_role == "client"
	again.add_theme_font_size_override("font_size", 28)
	again.custom_minimum_size = Vector2(0, 58)
	again.pressed.connect(_restart)
	results_box.add_child(again)
	var back := Button.new()
	back.text = "Main menu"
	back.add_theme_font_size_override("font_size", 22)
	back.custom_minimum_size = Vector2(0, 46)
	back.pressed.connect(_to_menu.bind(""))
	results_box.add_child(back)
	panel_results.visible = true
	if not auto_drive and net_role != "client":
		again.grab_focus()


# ---------------------------------------------------------------- input

func _input_state() -> Dictionary:
	var steer := 0.0
	var brake := false
	var nb := false
	var mul := 1.0
	var look := false
	# keyboard (the web game's default keys)
	if Input.is_key_pressed(KEY_LEFT) or Input.is_key_pressed(KEY_A):
		steer -= 1.0
	if Input.is_key_pressed(KEY_RIGHT) or Input.is_key_pressed(KEY_D):
		steer += 1.0
	var kb_brake := Input.is_key_pressed(KEY_SPACE) or Input.is_key_pressed(KEY_DOWN) or Input.is_key_pressed(KEY_S)
	if kb_brake:
		brake = true
	if Input.is_key_pressed(KEY_F):
		look = true
	# controller, mapped as on the web: left stick (20% dead zone) or d-pad, RT gas, LT drift, A/LB and B/RB items, X look back
	var pads := Input.get_connected_joypads()
	if pads.size() > 0:
		var j: int = pads[0]
		var ax := Input.get_joy_axis(j, JOY_AXIS_LEFT_X)
		var ay := Input.get_joy_axis(j, JOY_AXIS_LEFT_Y)
		var rt := Input.get_joy_axis(j, JOY_AXIS_TRIGGER_RIGHT)
		var lt := Input.get_joy_axis(j, JOY_AXIS_TRIGGER_LEFT)
		var any := absf(ax) > 0.5 or absf(ay) > 0.5 or rt > 0.5 or lt > 0.5
		for bi in [JOY_BUTTON_A, JOY_BUTTON_B, JOY_BUTTON_X, JOY_BUTTON_Y, JOY_BUTTON_LEFT_SHOULDER, JOY_BUTTON_RIGHT_SHOULDER, JOY_BUTTON_DPAD_LEFT, JOY_BUTTON_DPAD_RIGHT]:
			if Input.is_joy_button_pressed(j, bi):
				any = true
		if any:
			pad_used_at = Time.get_ticks_msec()
		var act := Time.get_ticks_msec() - pad_used_at < 20000
		var dz := 0.2
		var sx := 0.0 if absf(ax) < dz else signf(ax) * (absf(ax) - dz) / (1.0 - dz)
		var dl := Input.is_joy_button_pressed(j, JOY_BUTTON_DPAD_LEFT)
		var dr := Input.is_joy_button_pressed(j, JOY_BUTTON_DPAD_RIGHT)
		steer += clampf(sx + (1.0 if dr else 0.0) - (1.0 if dl else 0.0), -1.0, 1.0)
		var gas := rt > 0.5
		var drift := lt > 0.5
		if drift:
			brake = true
		if not kb_brake and gas and drift:
			nb = true      # drift trigger with the throttle held: drift only, never brake
		if act and not gas:
			mul = 0.0
		if Input.is_joy_button_pressed(j, JOY_BUTTON_X) or Input.is_joy_button_pressed(j, JOY_BUTTON_BACK):
			look = true
		if ay > 0.55 and act:
			look = true   # stick pulled back: the next item goes behind
		# items: slot 1 (A or LB) and slot 2 (B or RB); hold to keep a holdable item behind, let go to fire it
		var groups := [[], [JOY_BUTTON_A, JOY_BUTTON_LEFT_SHOULDER], [JOY_BUTTON_B, JOY_BUTTON_RIGHT_SHOULDER]]
		for sl in [1, 2]:
			var down := false
			for bi2 in groups[sl]:
				if Input.is_joy_button_pressed(j, bi2):
					down = true
			if down == pad_held[sl]:
				continue
			pad_held[sl] = down
			var it: String = kart.item if sl == 1 else kart.item2
			var suf := "2" if sl == 2 else ""
			var holding_this: bool = not kart.held.is_empty() and int(kart.held["sl"]) == sl
			if down:
				if holding_this:
					item_queued = "fwd" + suf
					pad_hold[sl] = 0
				elif it != "" and it in Race.HOLDABLE:
					item_queued = "hold" + suf
					pad_hold[sl] = 1
				else:
					item_queued = "fwd" + suf
					pad_hold[sl] = 0
			elif pad_hold[sl] == 1:
				pad_hold[sl] = 0
				if holding_this:
					item_queued = ("hold" if ay > 0.6 else "fwd") + suf
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
	look_back = look
	var o := {"steer": clampf(steer, -1.0, 1.0), "brake": brake, "nb": nb, "mul": mul, "use": false, "back": false, "hold": false, "hold_sl": 1, "release": null}
	var it2 := item_queued
	item_queued = ""
	if auto_drive and net_role == "client" and kart != null:
		var tj := (kart.idx + 14) % T.N
		o["steer"] = clampf(Kart.ang_diff(atan2(T.py[tj] - kart.y, T.px[tj] - kart.x), kart.a) * 2.5, -1.0, 1.0)
		o["mul"] = 1.0
		if kart.item != "" and kart.roll <= 0.0 and net_tick % 240 == 0:
			it2 = "fwd"
	if it2 != "" and kart != null:
		if net_role == "client":
			if net_ready:
				_net_item.rpc_id(1, it2)
		else:
			race.item_intent(kart, it2, o)
	if bool(o["use"]) and kart.item != "" and look and not kart.item in Race.NOBACK:
		o["back"] = true
	return o


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
		if kev.pressed and not kev.echo:
			match kev.keycode:
				KEY_X, KEY_E, KEY_ENTER:
					if state == "menu" or ip_edit.has_focus():
						pass
					elif state == "results":
						_restart()
					else:
						item_queued = "fwd"
				KEY_Z, KEY_Q, KEY_V:
					item_queued = "fwd2"
				KEY_SHIFT, KEY_B:
					item_queued = "hold"
				KEY_P, KEY_ESCAPE:
					_toggle_pause()
				KEY_F11:
					_toggle_fullscreen()
	elif ev is InputEventJoypadButton:
		var jb := ev as InputEventJoypadButton
		if jb.pressed:
			pad_used_at = Time.get_ticks_msec()
			if jb.button_index == JOY_BUTTON_START:
				if state == "results":
					_restart()
				else:
					_toggle_pause()
			elif jb.button_index == JOY_BUTTON_A and state == "results":
				_restart()
			elif jb.button_index == JOY_BUTTON_A and state == "menu" and net_role == "":
				_menu_race()
			elif jb.button_index == JOY_BUTTON_A and paused:
				_toggle_pause()


func _zone(p: Vector2) -> String:
	if is_phone and (pedal_l.get_global_rect().has_point(p) or pedal_r.get_global_rect().has_point(p)):
		return "pedal"
	return "l" if p.x < get_viewport().get_visible_rect().size.x * 0.5 else "r"


# ---------------------------------------------------------------- drawing

func _process(dt: float) -> void:
	if T == null or race == null:
		return
	if not paused:
		time += dt
	var al := 1.0 if (paused or state == "menu") else Engine.get_physics_interpolation_fraction()
	if net_role == "client":
		al = clampf((Time.get_ticks_msec() / 1000.0 - net_snap_at) / net_snap_dt, 0.0, 1.0)
	var rx := 0.0
	var ry := 0.0
	var rz := 0.0
	var rma := 0.0
	for k in race.karts:
		var v: Dictionary = views[k]
		var kx := lerpf(k.ox, k.x, al)
		var ky := lerpf(k.oy, k.y, al)
		var kz := lerpf(k.owy, k.wy, al)
		var ka := lerp_angle(k.oa, k.a, al)
		var th := 0.0
		if not k.loop.is_empty():
			th = lerpf(k.o_th if k.o_loop else 0.0, k.loop_th, al)
		if k == kart:
			rx = kx
			ry = ky
			rz = kz
			rma = lerp_angle(k.oma, k.ma, al)
			p_ka = ka
			p_th = th
		# kart: model forward is +X; heading a turns +X toward +Z; in the loop it pitches round with the track
		var node: Node3D = v["node"]
		var sc: float = v["sc"]
		var bs := Basis(Vector3.UP, -ka)
		if th != 0.0:
			bs = bs * Basis(Vector3(0, 0, 1), th)
		node.transform = Transform3D(bs.scaled(Vector3.ONE * sc), Vector3(kx, kz, ky))
		# blink while protected after a hit
		node.visible = not (k.inv > 0.0 and k.spin <= 0.0 and int(time * 16.0) % 2 == 0 and not k.finished)
		var body: Node3D = v["body"]
		if body and not paused:
			var f := 1.0 - exp(-10.0 * dt)
			var roll := (k.steer * 0.08 * k.d_amt if k.drift != 0 else 0.0) + k.steer * 0.04
			var pitch := clampf(k.acc * 0.0006, -0.07, 0.05)
			if k.trick_t > 0.0:
				var u := 1.0 - k.trick_t / Kart.TRICK_T
				if k.trick_k == 3 or k.trick_k == 4:
					roll += (TAU * u) * (-1.0 if k.trick_k == 3 else 1.0)
				elif k.trick_k == 1:
					pitch += TAU * u
				else:
					body.rotation.y = TAU * u
			else:
				body.rotation.y = 0.0
			if k.trick_t > 0.0:
				body.rotation.x = roll
				body.rotation.z = pitch
			else:
				body.rotation.x += (roll - body.rotation.x) * f
				body.rotation.z += (pitch - body.rotation.z) * f
		if not paused:
			for w in v["wheels"]:
				var n: Node3D = w["node"]
				n.rotation.z -= k.speed * dt / (float(w["r"]) * T.KS)
				if w["front"]:
					n.rotation.y = -k.steer * 0.38
		# boost flames out of the back, drift sparks at the rear wheels (blue, orange, pink as the charge builds)
		var flame: CPUParticles3D = v["flame"]
		var rear := Vector3(kx + cos(ka) * float(v["ax_r"]) - cos(ka) * 4.0, kz + 3.0, ky + sin(ka) * float(v["ax_r"]) - sin(ka) * 4.0)
		flame.emitting = k.boost > 0.0 and not paused and k.spin <= 0.0
		flame.position = rear
		flame.rotation.y = -ka
		flame.color = Color(0.45, 0.95, 1.0) if k.rush > 0.0 else Color(1.0, 0.55, 0.12)
		var sparks: CPUParticles3D = v["sparks"]
		sparks.emitting = k.drift != 0 and k.tier > 0 and not k.air and not paused
		sparks.position = rear + Vector3(0, -2.2, 0)
		sparks.rotation.y = -ka
		if k.tier > 0:
			sparks.color = [Color(0.4, 0.75, 1.0), Color(0.4, 0.75, 1.0), Color(1.0, 0.6, 0.15), Color(1.0, 0.4, 0.85)][k.tier]
		# garlic bubble
		var bub: MeshInstance3D = v["bubble"]
		bub.visible = k.sh_l > 0
		if bub.visible:
			bub.position = Vector3(kx, kz + 7.0, ky)
			var s := (1.0 + 0.04 * sin(time * 6.0)) * (1.12 if k.sh_l > 1 else 1.0)
			bub.scale = Vector3.ONE * s
		# item trailing behind
		var want: String = String(k.held.get("it", "")) if not k.held.is_empty() else ""
		if want != String(v["held_it"]):
			if v["held"] != null:
				(v["held"] as Node).queue_free()
				v["held"] = null
			v["held_it"] = want
			if want != "":
				var hn := _item_node(HELD_NODE.get(want, "pep"))
				add_child(hn)
				v["held"] = hn
		if v["held"] != null:
			var hn2: Node3D = v["held"]
			hn2.position = Vector3(kx - cos(ka) * 11.0, kz + 3.0, ky - sin(ka) * 11.0)
			hn2.rotation.y = time * 3.0

	_draw_items(al, dt)
	_camera(dt, rx, ry, rz, rma)

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
			var vis: bool = dd < (CULL_DIST * 1.08 if was else CULL_DIST)
			if vis != was:
				c["vis"] = vis
				(c["node"] as Node3D).visible = vis
	_hud(dt)


func _draw_items(al: float, dt: float) -> void:
	# item boxes: spin and bob; gone for four seconds after someone takes one
	for i in race.boxes.size():
		var b: Dictionary = race.boxes[i]
		var n: Node3D = box_nodes[i]
		var up := float(b["r"]) <= 0.0
		var base_y: float = float(b["gy"]) if bool(b["air"]) else T.ground(float(b["x"]), float(b["y"]))
		n.visible = up or float(b["r"]) < 0.35
		if n.visible:
			var grow := 1.0 if up else clampf(1.0 - float(b["r"]) / 0.35, 0.05, 1.0)
			n.position = Vector3(float(b["x"]), base_y + 7.0 + sin(time * 2.2 + i) * 0.9, float(b["y"]))
			n.rotation = Vector3(0.25 * sin(time * 1.3 + i), time * 1.6 + i, 0.2)
			n.scale = Vector3.ONE * 1.25 * grow
	# thrown items
	var seen := {}
	for p in race.projectiles:
		var pd: Dictionary = p
		var id: int = pd["id"]
		seen[id] = true
		var type: String = pd["type"]
		if not proj_nodes.has(id):
			var nn := _item_node(PROJ_NODE.get(type, "pep"))
			add_child(nn)
			proj_nodes[id] = nn
		var node: Node3D = proj_nodes[id]
		var x := lerpf(float(pd["px"]), float(pd["x"]), al)
		var y := lerpf(float(pd["py"]), float(pd["y"]), al)
		var g := T.ground(x, y)
		if type == "pep":
			node.position = Vector3(x, g + 3.4, y)
			node.rotation = Vector3(0.0, time * 14.0, 0.25)
		elif type == "dough":
			node.position = Vector3(x, g + 2.8, y)
			var sp := Vector2(float(pd["vx"]), float(pd["vy"])).length()
			node.rotation = Vector3(0.0, -atan2(float(pd["vy"]), float(pd["vx"])), node.rotation.z - sp * dt / 2.6)
		elif type == "flour" or type == "lob":
			var t0 := maxf(0.05, float(pd["t0"]))
			var u := clampf(1.0 - float(pd["t"]) / t0, 0.0, 1.0)
			node.position = Vector3(x, g + 4.0 + sin(PI * u) * (16.0 if type == "flour" else 12.0), y)
			node.rotation = Vector3(time * 5.0, time * 3.0, 0.0)
		elif type == "wheel":
			var ph: String = pd.get("ph", "")
			var yy := g + 7.5
			var pitch := 0.0
			var bank := 0.42 + sin(time * 5.5) * 0.1
			var s := minf(1.0, 0.35 + float(pd.get("age", 1.0)) * 3.5)
			if ph == "wind":
				var e := minf(1.0, 1.0 - maxf(0.0, float(pd["pt"])) / 0.62)
				yy = g + 8.0 + 9.0 * e
				pitch = e
				s = 1.0 + 0.06 * e
			elif ph == "slice":
				var f := minf(1.0, 1.0 - maxf(0.0, float(pd["pt"])) / 0.16)
				yy = g + 17.0 - 11.0 * f * f
				pitch = 1.0 - 2.1 * f
				s = 1.18
			elif ph == "done":
				var f2 := minf(1.0, 1.0 - maxf(0.0, float(pd["pt"])) / 0.4)
				yy = g + 7.0 + f2 * 5.0
				pitch = -1.1
				s = 1.18 * (1.0 - f2 * f2)
			node.position = Vector3(x, yy, y)
			node.rotation = Vector3(bank, -float(pd["dir"]) + PI / 2.0, pitch)
			node.scale = Vector3.ONE * maxf(0.01, s)
	for id in proj_nodes.keys():
		if not seen.has(id):
			var gone: Node3D = proj_nodes[id]
			_burst(gone.position, Color(1, 0.8, 0.4), 12, 50.0, 2.0, 0.3)
			gone.queue_free()
			proj_nodes.erase(id)
	# oil slicks on the road
	var hseen := {}
	for h in race.hazards:
		var hd: Dictionary = h
		var hid: int = hd["id"]
		hseen[hid] = true
		if not haz_nodes.has(hid):
			var hn := _item_node("oil")
			add_child(hn)
			var gx := float(hd["x"])
			var gz := float(hd["y"])
			var g0 := T.ground(gx, gz)
			# lie on the slope
			var nrm := Vector3(T.ground(gx - 3.0, gz) - T.ground(gx + 3.0, gz), 6.0, T.ground(gx, gz - 3.0) - T.ground(gx, gz + 3.0)).normalized()
			hn.position = Vector3(gx, g0 + 0.35, gz)
			if absf(nrm.dot(Vector3.UP)) < 0.999:
				hn.quaternion = Quaternion(Vector3.UP, nrm)
			haz_nodes[hid] = hn
		var hnode: Node3D = haz_nodes[hid]
		var grow2 := clampf(float(hd["born"]) / 0.25, 0.1, 1.0) * clampf(float(hd["t"]) / 0.4, 0.0, 1.0)
		hnode.scale = Vector3.ONE * grow2
	for hid2 in haz_nodes.keys():
		if not hseen.has(hid2):
			(haz_nodes[hid2] as Node).queue_free()
			haz_nodes.erase(hid2)


func _camera(dt: float, rx: float, ry: float, rz: float, rma: float) -> void:
	var k := kart
	if state == "menu":
		var oa := time * 0.18 + k.a + 2.4
		cam.position = Vector3(rx + cos(oa) * 62.0, rz + 17.0 + sin(time * 0.3) * 3.0, ry + sin(oa) * 62.0)
		cam.look_at(Vector3(rx, rz + 6.0, ry), Vector3.UP)
		cam.fov = 55.0
		cam_snap = true
		cam_a = k.ma
		return
	# chase camera (the web game's close camera); hold look-back to see behind
	cam_a = lerp_angle(cam_a, rma, 1.0 - exp(-5.5 * dt))
	var dist := 30.0 + (5.0 if k.boost > 0.0 else 0.0)
	var h := 12.6
	var back := -1.0 if look_back and state == "race" else 1.0
	var fx := cos(cam_a) * back
	var fy := sin(cam_a) * back
	var rg := T.ground(rx, ry)
	var in_loop := not k.loop.is_empty()
	var cy := rz - 4.0 if (k.glide or in_loop) else rg + (rz - rg) * 0.45
	var tv2 := Vector3(rx - fx * dist, cy + h, ry - fy * dist)
	var tv := Vector3(rx + fx * 32.0, cy + 6.2, ry + fy * 32.0)
	if in_loop:
		# ride round the loop with the kart: behind it and towards the middle of the ring, rolling over with it
		var lb := Basis(Vector3.UP, -p_ka) * Basis(Vector3(0, 0, 1), p_th)
		var kp := Vector3(rx, rz, ry)
		cam_base = kp + lb * Vector3(-26.0, 9.5, 0.0)
		cam_look = kp + lb * Vector3(22.0, 4.0, 0.0)
		cam.position = cam_base
		cam.look_at(cam_look, lb * Vector3.UP)
		cam.fov += (78.0 - cam.fov) * minf(1.0, 5.0 * dt)
		return
	if cam_snap:
		cam_base = tv2
		cam_look = tv
		cam_snap = false
	else:
		cam_base = cam_base.lerp(tv2, 1.0 - exp(-(30.0 if look_back else 12.0) * dt))
		cam_look = cam_look.lerp(tv, 1.0 - exp(-(30.0 if look_back else 16.0) * dt))
	var sh := Vector3.ZERO
	if shake > 0.0:
		shake = maxf(0.0, shake - dt)
		sh = Vector3(randf_range(-1, 1), randf_range(-1, 1), randf_range(-1, 1)) * minf(shake, 1.2) * 2.0
	cam.position = cam_base + sh
	if cam.position.distance_to(cam_look) > 0.1:
		cam.look_at(cam_look, Vector3.UP)
	var vs := get_viewport().get_visible_rect().size
	var aspect := vs.x / maxf(1.0, vs.y)
	var hf := deg_to_rad(96.0 if k.boost > 0.0 else 92.0)
	var vf := clampf(rad_to_deg(2.0 * atan(tan(hf / 2.0) / aspect)), 52.0, 100.0)
	cam.fov += (vf - cam.fov) * minf(1.0, 5.0 * dt)


func _hud(dt: float) -> void:
	var k := kart
	var pos := race.position_of(k)
	lbl_pos.text = _ordinal(k.place if k.finished else pos)
	lbl_pos.add_theme_color_override("font_color", [Color(1, 0.84, 0.25), Color(0.88, 0.9, 0.95), Color(0.93, 0.62, 0.38)][pos - 1] if pos <= 3 else Color(1, 0.96, 0.86))
	lbl_lap.text = "Lap %d/%d" % [k.lap(), T.LAPS]
	lbl_time.text = _fmt(k.finish_time if k.finished else race.race_time)
	lbl_speed.text = "%d mph" % int(round(maxf(0.0, k.speed) * 0.66))
	var prims := int(Performance.get_monitor(Performance.RENDER_TOTAL_PRIMITIVES_IN_FRAME))
	var draws := int(Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME))
	lbl_info.text = "%d fps · %s · %dk tris · %d draws" % [Engine.get_frames_per_second(), RenderingServer.get_current_rendering_driver_name(), prims / 1000, draws]
	if center_t > 0.0:
		center_t -= dt
		if center_t <= 0.0:
			lbl_center.text = ""
	if toast_t > 0.0:
		toast_t -= dt
		lbl_toast.modulate.a = clampf(toast_t / 0.3, 0.0, 1.0)
		if toast_t <= 0.0:
			lbl_toast.text = ""
	sfx.drive(absf(k.speed) / k.base_max, true, k.boost > 0.0, k.drift != 0 and not k.air, k.tier, state != "countdown" and state != "results" and state != "menu" and not paused)
	# item slots: while the roulette runs, the icons flick through the items
	var keys: Array = icons.keys()
	if k.roll > 0.0 and not paused:
		roll_tick -= dt
		if roll_tick <= 0.0:
			roll_tick = 0.09
			sfx.play("roll", 0.5)
	if k.roll > 0.0 and keys.size() > 0:
		slot1.texture = icons[keys[int(time * 14.0) % keys.size()]]
		slot2.texture = null
		lbl_item.text = ""
	else:
		var show1: String = k.item
		if show1 == "" and not k.held.is_empty():
			show1 = String(k.held["it"])
		slot1.texture = icons.get(show1) if show1 != "" else null
		slot1.modulate.a = 0.5 if (k.item == "" and not k.held.is_empty()) else 1.0
		slot2.texture = icons.get(k.item2) if k.item2 != "" else null
		lbl_item.text = String(ITEM_NAMES.get(show1, "")) if show1 != "" else ""
	slot2_bg.modulate.a = 1.0 if slot2.texture != null else 0.45
	slot1_bg.modulate.a = 1.0 if slot1.texture != null else 0.6
	mini.T = T
	mini.race = race
	mini.me = kart
	mini.queue_redraw()
	if is_phone:
		var piv := 1.0 if touches.values().has("pedal") else 0.55
		pedal_l.modulate.a = piv
		pedal_r.modulate.a = piv


func _fmt(t: float) -> String:
	var m := int(t / 60.0)
	var s := t - m * 60.0
	return "%d:%05.2f" % [m, s]


# ---------------------------------------------------------------- menu and online

func _to_menu(note: String) -> void:
	_net_close()
	_start_race({})
	state = "menu"
	hud_race.visible = false
	lbl_center.text = ""
	panel_menu.visible = true
	_menu_refresh(note)


func _menu_refresh(note := "") -> void:
	btn_start_net.visible = net_role == "host"
	btn_leave_net.visible = net_role != ""
	var t := "Hawaiian Bay  ·  3 laps  ·  8 racers"
	if net_role == "host":
		t = "Hosting. Friends on the PC version join with your address%s\n%d joined so far" % [net_addr, net_peers.size()]
		btn_start_net.text = "Start the online race (%d player%s)" % [net_peers.size() + 1, "" if net_peers.is_empty() else "s"]
	elif net_role == "client":
		t = "Connecting..."
	if note != "":
		t = note
	lbl_menu.text = t


func _menu_race() -> void:
	_net_close()
	_start_race({})


func _menu_leave() -> void:
	_net_close()
	_menu_refresh("")


func _menu_host() -> void:
	if net_role == "host":
		return
	_net_close()
	var peer := ENetMultiplayerPeer.new()
	if peer.create_server(NET_PORT, 7) != OK:
		_menu_refresh("Could not open port %d. Is another copy of the game already hosting?" % NET_PORT)
		return
	multiplayer.multiplayer_peer = peer
	net_role = "host"
	net_peers.clear()
	var ips := PackedStringArray()
	for ip in IP.get_local_addresses():
		if ip.count(".") == 3 and not ip.begins_with("127.") and not ip.begins_with("169.254."):
			ips.append(ip)
	net_addr = ":\nsame Wi-Fi or network: %s" % ("  or  ".join(ips) if not ips.is_empty() else "(no network found)")
	_menu_refresh()
	if not auto_drive and upnp_thread == null:
		upnp_thread = Thread.new()
		upnp_thread.start(_upnp_work)


## asks the router to pass the game's port through, so friends elsewhere can join with the public address
func _upnp_work() -> void:
	var u := UPNP.new()
	var ext := ""
	if u.discover(2000, 2, "InternetGatewayDevice") == UPNP.UPNP_RESULT_SUCCESS and u.get_gateway() != null and u.get_gateway().is_valid_gateway():
		if u.add_port_mapping(NET_PORT, NET_PORT, "Crust Rush", "UDP", 0) == UPNP.UPNP_RESULT_SUCCESS:
			ext = u.query_external_address()
	_upnp_done.call_deferred(ext)


func _upnp_done(ext: String) -> void:
	upnp_thread.wait_to_finish()
	upnp_thread = null
	if net_role != "host":
		return
	if ext != "":
		net_addr += "\nover the internet: %s" % ext
	else:
		net_addr += "\nover the internet: your router did not open the port by itself (forward UDP %d to this PC)" % NET_PORT
	if state == "menu":
		_menu_refresh()


func _menu_join() -> void:
	var ip := ip_edit.text.strip_edges()
	if ip == "":
		_menu_refresh("Type the host's address first (they see it after choosing Host an online race)")
		return
	_net_close()
	var peer := ENetMultiplayerPeer.new()
	if peer.create_client(ip, NET_PORT) != OK:
		_menu_refresh("That address did not work: %s" % ip)
		return
	multiplayer.multiplayer_peer = peer
	net_role = "client"
	_menu_refresh("Connecting to %s..." % ip)


func _net_close() -> void:
	if net_role != "":
		var mp := multiplayer.multiplayer_peer
		if mp != null:
			mp.close()
		multiplayer.multiplayer_peer = OfflineMultiplayerPeer.new()
	net_role = ""
	net_ready = false
	net_peers.clear()
	net_out.clear()


func _on_peer_in(id: int) -> void:
	if net_role == "host":
		net_peers.append(id)
		if state == "menu":
			_menu_refresh()


func _on_peer_out(id: int) -> void:
	if net_role != "host":
		return
	net_peers.erase(id)
	if race != null:
		for k in race.karts:
			if k.peer == id:      # the computer takes over a kart whose driver left
				k.peer = 0
				k.remote = false
				k.ai["auto"] = true
	if state == "menu":
		_menu_refresh()


func _on_connected() -> void:
	net_ready = true
	if state == "menu":
		_menu_refresh("Connected. Waiting for the host to start the race.")


func _on_failed() -> void:
	_net_close()
	_menu_refresh("Could not reach that address. Check it, and that the host has chosen Host an online race.")


func _on_server_gone() -> void:
	_to_menu("The host left the race.")


func _net_start() -> void:
	if net_role != "host":
		return
	var peers: Array = [1]
	peers.append_array(net_peers)
	var pri := int((roster.get("player", {}) as Dictionary).get("ri", 1))
	var cfg := Race.new().make_cfg(roster, pri, peers, int(randi() & 0x7fffffff) + 1)
	_net_begin.rpc(cfg)
	_start_race(cfg)


@rpc("authority", "call_remote", "reliable")
func _net_begin(cfg: Dictionary) -> void:
	if net_role == "client":
		_start_race(cfg)


@rpc("any_peer", "call_remote", "unreliable_ordered")
func _net_input(steer: float, bits: int) -> void:
	if net_role != "host" or race == null:
		return
	var id := multiplayer.get_remote_sender_id()
	for k in race.karts:
		if k.peer == id:
			k.net_inp = {"steer": clampf(steer, -1.0, 1.0), "brake": (bits & 1) != 0, "nb": (bits & 2) != 0, "mul": 1.0 if (bits & 4) != 0 else 0.0, "look": (bits & 8) != 0}


@rpc("any_peer", "call_remote", "reliable")
func _net_item(it: String) -> void:
	if net_role != "host" or race == null or not it in ["fwd", "fwd2", "hold", "hold2"]:
		return
	var id := multiplayer.get_remote_sender_id()
	for k in race.karts:
		if k.peer == id and k.net_items.size() < 4:
			k.net_items.append(it)


## host: thirty times a second, everything the other screens need to draw the race
func _net_host_tick() -> void:
	net_tick += 1
	if net_peers.is_empty():
		net_out.clear()
		return
	if not net_out.is_empty():
		_net_fx.rpc(net_out.duplicate())
		net_out.clear()
	if net_tick % SNAP_EVERY != 0:
		return
	var ks: Array = []
	for k in race.karts:
		ks.append([k.x, k.y, k.wy, k.a, k.ma, k.speed, k.steer, k.boost, k.spin, k.inv, k.rush, k.z, k.drift, k.tier, k.d_amt,
			(1 if k.air else 0) | (2 if k.glide else 0) | (4 if k.big else 0) | (8 if k.finished else 0) | (16 if k.est else 0),
			k.item, k.item2, String(k.held.get("it", "")), int(k.held.get("sl", 1)), k.sh_l, k.prog, k.idx, k.place, k.finish_time,
			k.loop_th if not k.loop.is_empty() else -1.0, k.roll, k.trick_t, k.trick_k, k.acc])
	var bx := PackedFloat32Array()
	for b in race.boxes:
		bx.append(float(b["r"]))
	var pr: Array = []
	for p in race.projectiles:
		pr.append([p["id"], p["type"], p["x"], p["y"], p["vx"], p["vy"], p["t"], p["t0"], p.get("ph", ""), p.get("pt", 0.0), p.get("dir", 0.0), p.get("spin", 0.0), p.get("age", 0.0)])
	var hz: Array = []
	for h in race.hazards:
		hz.append([h["id"], h["x"], h["y"], h["t"], h["born"]])
	_net_snap.rpc([state, cd, race.race_time, ks, bx, pr, hz])


@rpc("authority", "call_remote", "reliable")
func _net_fx(list: Array) -> void:
	if net_role != "client" or race == null:
		return
	for e in list:
		if e is Array:
			var i: int = e[1]
			if i >= 0 and i < race.karts.size():
				race.karts[i].events.append(String(e[2]))
		elif e is Dictionary:
			var d: Dictionary = e
			var ok := true
			for key in ["k", "a", "b"]:
				if d.has(key):
					var ki := int(d[key])
					if ki >= 0 and ki < race.karts.size():
						d[key] = race.karts[ki]
					else:
						ok = false
			if ok:
				race.fx.append(d)


@rpc("authority", "call_remote", "unreliable_ordered")
func _net_snap(s: Array) -> void:
	if net_role != "client" or race == null or state == "menu":
		return
	net_snaps += 1
	var now := Time.get_ticks_msec() / 1000.0
	net_snap_dt = lerpf(net_snap_dt, clampf(now - net_snap_at, 1.0 / 60.0, 0.2), 0.2)
	net_snap_at = now
	var st: String = s[0]
	var ncd: float = s[1]
	if st == "countdown" and ceili(ncd) != ceili(cd) and ceili(ncd) > 0 and ncd < 3.0:
		_show_center(str(ceili(ncd)), 1.0)
		sfx.play("beep")
	if st != "countdown" and state == "countdown":
		_show_center("GO!", 0.8)
		sfx.play("go")
	cd = ncd
	race.race_time = s[2]
	race.state = "countdown" if st == "countdown" else "race"
	var ks: Array = s[3]
	for i in mini(ks.size(), race.karts.size()):
		var k := race.karts[i]
		var q: Array = ks[i]
		k.ox = k.x
		k.oy = k.y
		k.owy = k.wy
		k.oa = k.a
		k.oma = k.ma
		k.o_th = k.loop_th
		k.o_loop = not k.loop.is_empty()
		k.x = q[0]
		k.y = q[1]
		k.wy = q[2]
		k.a = q[3]
		k.ma = q[4]
		k.speed = q[5]
		k.steer = q[6]
		k.boost = q[7]
		k.spin = q[8]
		k.inv = q[9]
		k.rush = q[10]
		k.z = q[11]
		k.drift = q[12]
		k.tier = q[13]
		k.d_amt = q[14]
		var fl: int = q[15]
		k.air = (fl & 1) != 0
		k.glide = (fl & 2) != 0
		k.big = (fl & 4) != 0
		k.finished = (fl & 8) != 0
		k.est = (fl & 16) != 0
		k.item = q[16]
		k.item2 = q[17]
		k.held = {"it": q[18], "sl": q[19], "t": 0.0} if String(q[18]) != "" else {}
		k.sh_l = q[20]
		k.prog = q[21]
		k.idx = q[22]
		k.place = q[23]
		k.finish_time = q[24]
		var th: float = q[25]
		k.loop = {"th": th} if th >= 0.0 else {}
		k.loop_th = maxf(0.0, th)
		k.roll = q[26]
		k.trick_t = q[27]
		k.trick_k = q[28]
		k.acc = q[29]
		if net_fresh or Vector2(k.x - k.ox, k.y - k.oy).length() > 120.0:
			k._save_prev()      # first picture, or a jump (a respawn): don't slide there
	net_fresh = false
	var bx: PackedFloat32Array = s[4]
	for i in mini(bx.size(), race.boxes.size()):
		race.boxes[i]["r"] = bx[i]
	var old := {}
	for p in race.projectiles:
		old[p["id"]] = p
	race.projectiles.clear()
	for q2 in s[5]:
		var prev = old.get(q2[0])
		race.projectiles.append({"id": q2[0], "type": q2[1], "x": q2[2], "y": q2[3], "px": prev["x"] if prev != null else q2[2], "py": prev["y"] if prev != null else q2[3],
			"vx": q2[4], "vy": q2[5], "t": q2[6], "t0": q2[7], "ph": q2[8], "pt": q2[9], "dir": q2[10], "spin": q2[11], "age": q2[12], "owner": null, "target": null})
	race.hazards.clear()
	for q3 in s[6]:
		race.hazards.append({"id": q3[0], "x": q3[1], "y": q3[2], "t": q3[3], "born": q3[4]})
	race.stand = race.standings()
	if st == "results" and state != "results":
		state = "results"
		_show_results()
	elif st != "results":
		if state == "results":
			panel_results.visible = false
		state = st


## everyone but the host: send the controls sixty times a second, and play what the host reported
func _net_client_tick() -> void:
	net_tick += 1
	if kart == null or not net_ready:
		return
	var o := _input_state()
	if net_tick % 2 == 0 and state != "results":
		var bits := (1 if bool(o["brake"]) else 0) | (2 if bool(o["nb"]) else 0) | (4 if float(o["mul"]) > 0.0 else 0) | (8 if look_back else 0)
		_net_input.rpc_id(1, float(o["steer"]), bits)
	_drain_events()
	if state == "race" or state == "finished":
		_finish_check()
		_lap_check()


func _exit_tree() -> void:
	if upnp_thread != null:
		upnp_thread.wait_to_finish()


func _enter_tree() -> void:
	cam = Camera3D.new()
	cam.near = 0.5
	cam.far = 14000.0
	cam.fov = 70.0
	add_child(cam)
	cam.current = true


## the track from above, with a dot per racer
class MiniMap extends Control:
	var T: TrackData
	var race: Race
	var me: Kart
	var pts := PackedVector2Array()
	var for_size := Vector2.ZERO
	const COLS := [Color(0.84, 0.23, 0.15), Color(0.18, 0.6, 0.24), Color(0.42, 0.31, 0.69), Color(0.95, 0.92, 0.85), Color(0.94, 0.45, 0.08), Color(0.54, 0.37, 0.26), Color(0.95, 0.75, 0.12), Color(0.16, 0.5, 0.85)]

	func _map(x: float, y: float) -> Vector2:
		var r := T.R
		var s: float = minf(size.x, size.y)
		return Vector2((x / r * 0.5 + 0.5) * s, (y / r * 0.5 + 0.5) * s)

	func _draw() -> void:
		if T == null or race == null:
			return
		if pts.is_empty() or for_size != size:
			for_size = size
			pts = PackedVector2Array()
			for i in range(0, T.N, 6):
				pts.append(_map(T.px[i], T.py[i]))
			pts.append(pts[0])
		draw_polyline(pts, Color(0.1, 0.05, 0.03, 0.7), 9.0, true)
		draw_polyline(pts, Color(1, 0.96, 0.86, 0.85), 4.0, true)
		for k in race.karts:
			if k == me:
				continue
			var c: Color = COLS[k.ri % COLS.size()]
			if k.ri < T.racers.size():
				c = Color.html(String(T.racers[k.ri]["color"]))
			draw_circle(_map(k.x, k.y), 6.0, Color(0.1, 0.05, 0.03))
			draw_circle(_map(k.x, k.y), 4.5, c)
		if me != null:
			draw_circle(_map(me.x, me.y), 9.0, Color(0.1, 0.05, 0.03))
			draw_circle(_map(me.x, me.y), 7.0, Color(1, 0.84, 0.25))
