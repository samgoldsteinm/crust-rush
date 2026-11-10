extends Node3D
## Race scene: Hawaiian Bay, eight karts, items. The simulation is in race.gd and kart.gd (ported
## from the web game, 120 Hz in _physics_process); this file draws it, interpolating between
## steps, and handles input, the HUD and the race flow.
## Keyboard (as on the web): arrows/WASD steer, Space/Down/S drift-brake, X/E/Enter first item,
## Z/Q/V second item, Shift/B keep an item behind, F look back, P or Esc pause, F11 full screen.
## Controller: left stick or d-pad, RT gas, LT drift, A/LB first item, B/RB second item, X look back, Start pause.

const BUILTIN_DIR := "res://assets/track"   # Hawaiian Bay ships inside the game; the other tracks sit in a "maps" folder
const ROSTER_JSON := "res://assets/kart/roster.json"
const ITEMS_SCENE := "res://assets/items/items.glb"
const CULL_DIST := 2600.0   # far clutter cells hide beyond this (the web uses 1500-2250 by preset)
const TRICK_NAMES := ["Backflip", "360 Spin", "Frontflip", "Barrel roll", "Barrel roll"]

var T: TrackData
var map_id := ""              # which track; "" = the CR_MAP setting, else Hawaiian Bay
var maps: Array = []         # {id, name, mi, theme, dir, builtin}
var world: Node3D            # everything that belongs to the loaded track (sky, lights, scenery)
var haz_lib: Node3D          # the track's moving hazards (traffic, walkers...), copied into each race
var race: Race
var roster := {}
var net_prefs := {}       # host: each joined player's chosen driver and kart
var item_set := {}        # Settings > Items: {name: false} for items switched off
var last_run := {}        # the player's last finished run against their best: {t, old, pb}
var ghost: Ghost          # your best run, raced against you
var ghost_on := true      # Settings > Best-run ghost
var was_last := false     # dropped to last place this race (for Comeback Kid)
var found_sc := {}        # hidden shortcuts found this race
var spec_k: Kart = null   # Last Slice: the kart the camera watches once you are out
var kart: Kart               # the player's kart (kept for the tests)
var kart_scenes := {}        # file -> PackedScene
var view: View
var fx: Fx
var hud: Hud
var rim: DirectionalLight3D
var post: ColorRect
var post_mat: ShaderMaterial
var water_mats: Array = []
var portraits := {}
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
var shake_imp := 0.0
var cam_gp := 0.0
var cam_gr := 0.0
var cam_sx := 0.0
var cam_oy := 0.0
var cam_vy := 0.0
var cam_pvz := 0.0
var cam_pspd := 0.0
var cam_occ := 1.0
var cam_lb := false
var cam_bo := false
var cam_up := Vector3.UP
var fin_punch := 0.0
var edge_c := Color.WHITE
var edge_a := 0.0
var edge_t := 0.0
var spd_fx := 0.0
var cull_list: Array = []    # {node, rect: Rect2 in ground x/z}
var cull_t := 0.0
var auto_drive := false      # set by the tests: the computer drives the player's kart
var paused := false
var time := 0.0
var last_lap := 1

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
var lbl_info: Label
var btn_fps: Button
var btn_res: Button
var panel_results: PanelContainer
var results_box: VBoxContainer
var panel_pause: PanelContainer
var icons := {}
var fps_cap := 60
var res_scale := 1.0
var is_phone := false
var quality := 2             # 0 Low (the web look), 1 High, 2 Ultra
var hud_race: Control
var panel_menu: PanelContainer
var menu: Menu
var loading: Control
var sel := {"mode": "gp", "cls": "medium", "ri": 1, "cup": 0}   # the menu's choices
var gp := {}                 # Grand Prix in progress: {cup, race, pts: [8], tracks: [ids]}
const CLASS_MUL := {"small": 0.86, "medium": 1.0, "large": 1.14, "reverse": 1.14}
const CLASS_AI := {"small": "easy", "medium": "normal", "large": "hard", "reverse": "hard"}
var lbl_menu: Label
var ip_edit: LineEdit
var btn_start_net: Button
var btn_leave_net: Button
var btn_again: Button
var skip_menu := false       # tests go straight to the race
var test_look := false       # tests: look back
var test_hold := false       # tests: the race only moves when the test steps it (the screenshots match the web's step for step)
var shown_finish := false

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
var stats := {"used": {}, "spins": 0, "boxes": 0, "player_spins": 0, "abilities": {}}


func _ready() -> void:
	is_phone = OS.has_feature("mobile") or DisplayServer.is_touchscreen_available() and OS.get_name() in ["iOS", "Android"]
	quality = 0 if is_phone else 2
	process_mode = Node.PROCESS_MODE_ALWAYS
	if not auto_drive and not skip_menu:
		_load_settings()
	scan_maps()
	if map_id == "":
		map_id = OS.get_environment("CR_MAP")
	if OS.get_environment("CR_MODE") != "":
		sel["mode"] = OS.get_environment("CR_MODE")
	if map_id == "" or _map_info(map_id).is_empty():
		map_id = "bay"
	var f := FileAccess.open(ROSTER_JSON, FileAccess.READ)
	if f:
		roster = JSON.parse_string(f.get_as_text())
	_new_cpu_builds()
	_build_post()
	if not load_map(map_id):
		return
	_load_items()
	fx = Fx.new()
	add_child(fx)
	fx.cam = cam
	view = View.new()
	add_child(view)
	sfx = Sfx.new()
	add_child(sfx)
	music = Music.new()
	add_child(music)
	music.on = music_on
	music.level = music_level
	_build_hud()
	_apply_display()
	if sfx_vol < 0.99:
		AudioServer.set_bus_volume_db(0, linear_to_db(maxf(0.0001, sfx_vol)))
		AudioServer.set_bus_mute(0, sfx_vol < 0.01)
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


## where the exported tracks live: CR_MAPS, a "maps" folder next to the game, or res://maps while developing
static func maps_dirs() -> Array:
	var out: Array = []
	var e := OS.get_environment("CR_MAPS")
	if e != "":
		out.append(e)
	out.append(OS.get_executable_path().get_base_dir().path_join("maps"))
	out.append(ProjectSettings.globalize_path("res://maps"))
	return out


func scan_maps() -> void:
	maps.clear()
	var seen := {}
	for d in maps_dirs():
		var da := DirAccess.open(d)
		if da == null:
			continue
		for sub in da.get_directories():
			var dir: String = String(d).path_join(sub)
			if seen.has(sub) or not FileAccess.file_exists(dir.path_join(sub + ".json")) or not FileAccess.file_exists(dir.path_join(sub + ".gltf")):
				continue
			var info := {"id": sub, "name": sub.capitalize(), "mi": 99, "theme": "bay", "dir": dir, "builtin": false}
			var ip := dir.path_join(sub + ".info.json")
			if FileAccess.file_exists(ip):
				var j = JSON.parse_string(FileAccess.get_file_as_string(ip))
				if typeof(j) == TYPE_DICTIONARY:
					for key in ["name", "mi", "theme", "cup"]:
						if (j as Dictionary).has(key):
							info[key] = j[key]
			seen[sub] = true
			maps.append(info)
	if not seen.has("bay") and FileAccess.file_exists(BUILTIN_DIR + "/bay.json"):
		maps.append({"id": "bay", "name": "Hawaiian Bay", "mi": 1, "theme": "bay", "cup": 0, "dir": BUILTIN_DIR, "builtin": true})
	maps.sort_custom(func(a, b): return int(a["mi"]) < int(b["mi"]))


func _map_info(id: String) -> Dictionary:
	for m in maps:
		if m["id"] == id:
			return m
	return {}


## a glTF file from disk (the tracks exported from the web game), or the built-in copy
func _load_gltf(path: String) -> Node3D:
	if path.begins_with("res://"):
		var ps: PackedScene = load(path) if ResourceLoader.exists(path) else null
		return ps.instantiate() as Node3D if ps != null else null
	if not FileAccess.file_exists(path):
		return null
	var doc := GLTFDocument.new()
	var st := GLTFState.new()
	var err := OK
	if path.ends_with(".gltf"):
		# tell the loader which images are JPEGs (older exports left the type out, so it tried them as PNGs first)
		var txt := FileAccess.get_file_as_string(path)
		if txt.find("\"mimeType\"") < 0:
			var re := RegEx.new()
			re.compile("\"uri\":\"([^\"]+\\.(jpg|png))\"")
			txt = re.sub(txt, "\"uri\":\"$1\",\"mimeType\":\"image/$2\"", true).replace("image/jpg", "image/jpeg")
		err = doc.append_from_buffer(txt.to_utf8_buffer(), path.get_base_dir() + "/", st)
	else:
		err = doc.append_from_file(path, st)
	if err != OK:
		push_error("Could not read %s" % path)
		return null
	var n := doc.generate_scene(st) as Node3D
	# textures read at run time come without mipmaps: make them, or distant ground shimmers
	var done := {}
	for mi in n.find_children("*", "MeshInstance3D", true, false):
		var am := (mi as MeshInstance3D).mesh
		if am == null:
			continue
		for si in am.get_surface_count():
			var sm := am.surface_get_material(si) as BaseMaterial3D
			if sm == null:
				continue
			for slot in [BaseMaterial3D.TEXTURE_ALBEDO, BaseMaterial3D.TEXTURE_NORMAL, BaseMaterial3D.TEXTURE_ORM, BaseMaterial3D.TEXTURE_ROUGHNESS, BaseMaterial3D.TEXTURE_EMISSION]:
				var tx := sm.get_texture(slot) as ImageTexture
				if tx == null or done.has(tx):
					continue
				done[tx] = true
				var img := tx.get_image()
				if img != null and not img.has_mipmaps():
					if img.is_compressed():
						continue
					img.generate_mipmaps()
					tx.set_image(img)
	return n


## loads a track: its data, sky, lights and scenery. Returns false if it can't be read.
func load_map(id: String) -> bool:
	var info := _map_info(id)
	if info.is_empty():
		return false
	var dir: String = info["dir"]
	var nt := TrackData.load_from(dir.path_join(id + ".json"))
	if nt == null:
		return false
	if race != null:
		_clear_race_nodes()
		race = null
	if world != null:
		world.free()
	if haz_lib != null:
		haz_lib.free()
		haz_lib = null
	water_mats.clear()
	cull_list.clear()
	T = nt
	map_id = id
	world = Node3D.new()
	world.name = "World"
	add_child(world)
	_build_world()
	var hp := dir.path_join(id + "_haz.glb")
	haz_lib = _load_gltf(hp)
	if haz_lib != null:
		_use_vertex_colours(haz_lib)
	print("track %s: %s, hazards %s" % [id, info["name"], "yes" if haz_lib != null else "none"])
	return true


## inverse of Godot's ACES (tonemap_aces in the renderer): the HDR colour that comes out as `t`
static func _aces_inv(t: Vector3) -> Vector3:
	const A := 0.0245786
	const B := 0.000090537
	const C := 0.983729
	const D := 0.432951
	const E := 0.238081
	var bias := 1.8
	var w := 16.0 * bias
	var wt := (w * (w + A) - B) / (w * (C * w + D) + E)
	var odt := Basis(Vector3(1.60475, -0.10208, -0.00327), Vector3(-0.53108, 1.10813, -0.07276), Vector3(-0.07367, -0.00605, 1.07602))
	var rrt := Basis(Vector3(0.59719, 0.07600, 0.02840), Vector3(0.35458, 0.90834, 0.13383), Vector3(0.04823, 0.01566, 0.83777))
	var z := odt.inverse() * (t * wt)
	var u := Vector3.ZERO
	for i in 3:
		var y := clampf(z[i], 0.0, 0.995)
		# y = (u(u+A)-B)/(u(Cu+D)+E)  ->  (1-yC)u^2 + (A-yD)u - (B+yE) = 0
		var a := 1.0 - y * C
		var b := A - y * D
		var c := -(B + y * E)
		u[i] = (-b + sqrt(maxf(0.0, b * b - 4.0 * a * c))) / (2.0 * a)
	var x := rrt.inverse() * u / bias
	return Vector3(maxf(0.0, x.x), maxf(0.0, x.y), maxf(0.0, x.z))


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
	# the web game's lighting: a hemisphere fill (warm cream from above), the sun, ACES tone mapping in every
	# material, then its own grade (saturation, contrast, vignette: shaders/post.gdshader)
	env.ambient_light_source = Environment.AMBIENT_SOURCE_SKY
	env.ambient_light_sky_contribution = 0.25
	env.ambient_light_color = _hex(L.get("hemiSky"), Color(1, 0.89, 0.77))
	# Settings > Look: Vivid (a darker base, a stronger sun, more contrast and colour) or Classic (web applyLook)
	var night := T.theme == "night"
	var vivid := look != "classic"
	env.ambient_light_energy = float(L.get("hemiI", 0.52)) * ((0.88 if night else 0.7) if vivid else 1.0)
	env.reflected_light_source = Environment.REFLECTION_SOURCE_SKY
	env.tonemap_mode = Environment.TONE_MAPPER_ACES
	# Godot's ACES pre-scales by 1.8 and normalises to its white point; three.js pre-scales by 1/0.6 and
	# doesn't normalise. A high white point and exposure x(1.667/1.8) make the two curves match.
	env.tonemap_white = 16.0
	env.tonemap_exposure = float(L.get("exposure", 0.92)) * ((1.0 if night else 0.96) if vivid else 1.0) * (1.0 / 0.6) / 1.8
	# Ultra's screen-space ambient occlusion (radius 7, strong) and its bloom (threshold .94, strength .3)
	env.ssao_enabled = not is_phone
	env.ssao_radius = 2.5
	env.ssao_intensity = 1.6
	env.ssao_light_affect = 0.6   # the web multiplies the whole picture by its AO, lit faces included
	env.glow_enabled = not is_phone
	env.glow_intensity = 0.3
	env.glow_strength = 1.0
	env.glow_bloom = 0.0
	env.glow_blend_mode = Environment.GLOW_BLEND_MODE_ADDITIVE
	env.glow_hdr_threshold = 1.6
	env.glow_hdr_scale = 2.0
	for i in 7:
		env.set_glow_level(i, 1.0 if i == 2 or i == 4 else 0.0)
	var fog = L.get("fog")
	if typeof(fog) == TYPE_DICTIONARY:
		env.fog_enabled = true
		env.fog_mode = Environment.FOG_MODE_DEPTH
		var fd: Dictionary = fog
		# the web mixes fog in after tone mapping (three.js r149 applies fog last), Godot before: pick the
		# fog light so a fully fogged pixel comes out of Godot's ACES as the web's fog colour
		var fc := _hex(fd.get("color"), Color(0.94, 0.69, 0.55))
		var hdr := _aces_inv(Vector3(fc.r, fc.g, fc.b)) / maxf(0.05, env.tonemap_exposure)
		var mx := maxf(hdr.x, maxf(hdr.y, hdr.z))
		env.fog_light_color = Color(hdr.x / mx, hdr.y / mx, hdr.z / mx).linear_to_srgb()
		env.fog_light_energy = mx
		env.fog_depth_begin = float(fd.get("near", 2600))
		env.fog_depth_end = float(fd.get("far", 11000))
		env.fog_depth_curve = 1.0
		env.fog_density = 1.0
		env.fog_sky_affect = 0.0
	we.environment = env
	world.add_child(we)

	# the sun: one 4096 shadow map covering ±150 around a point 80 ahead of your kart (web snapSun, Ultra)
	sun = DirectionalLight3D.new()
	var sd: Array = L.get("sunDir", [0.84, 0.47, 0.26])
	var to_sun := Vector3(sd[0], sd[1], sd[2]).normalized()
	world.add_child(sun)
	sun.look_at_from_position(to_sun * 100.0, Vector3.ZERO, Vector3.UP)
	sun.light_color = _hex(L.get("sunColor"), Color(1, 0.84, 0.66))
	sun.light_energy = float(L.get("sunI", 3.25)) * (((1.12 if T.theme == "night" else 1.25)) if look != "classic" else 1.0)
	sun.shadow_enabled = true
	sun.directional_shadow_mode = DirectionalLight3D.SHADOW_ORTHOGONAL
	sun.directional_shadow_max_distance = 300.0
	sun.directional_shadow_fade_start = 0.9
	sun.shadow_bias = 0.04
	sun.shadow_normal_bias = 1.0
	sun.shadow_blur = 1.2
	# the web's rim light: a cool light from behind the camera, opposite the sun
	rim = DirectionalLight3D.new()
	rim.light_color = _hex(T.rim.get("c"), Color("#a8ccff"))
	rim.light_energy = float(T.rim.get("i", 0.55)) * 1.25
	rim.shadow_enabled = false
	world.add_child(rim)
	var rd := Vector3(to_sun.x * 400.0, -300.0, to_sun.z * 400.0).normalized()
	rim.look_at_from_position(Vector3.ZERO - rd, Vector3.ZERO, Vector3.UP)

	# the track: exported cells; clutter cells ("_d") get distance culling like the web game
	var track := _load_gltf(String(_map_info(map_id)["dir"]).path_join(map_id + ".gltf"))
	if track != null:
		world.add_child(track)
		_prepare_track(track)
	# the web's colour grade for this theme (bloom strength and threshold too)
	var G: Dictionary = T.grade
	if post_mat != null:
		var tn: Array = G.get("tint", [1.0, 1.0, 1.0])
		# the exported grade is the Vivid one; Classic takes its extra contrast and colour back out
		var nt := T.theme == "night"
		var cl := look == "classic"
		post_mat.set_shader_parameter("sat", float(G.get("sat", 1.07)) - ((0.02 if nt else 0.035) if cl else 0.0))
		post_mat.set_shader_parameter("con", float(G.get("con", 1.04)) - ((0.03 if nt else 0.06) if cl else 0.0))
		post_mat.set_shader_parameter("tint", Vector3(float(tn[0]), float(tn[1]), float(tn[2])))
		post_mat.set_shader_parameter("vig", float(G.get("vig", 0.16)))
	env.glow_intensity = float(G.get("bloom", 0.3))
	env.glow_hdr_threshold = 1.6 * float(G.get("thr", 0.94)) / 0.94
	_apply_quality()


func _build_post() -> void:
	# the web's final grade, drawn over the 3D view (under the HUD)
	var pl := CanvasLayer.new()
	pl.layer = -1
	add_child(pl)
	post = ColorRect.new()
	post.set_anchors_preset(Control.PRESET_FULL_RECT)
	post.mouse_filter = Control.MOUSE_FILTER_IGNORE
	post_mat = ShaderMaterial.new()
	post_mat.shader = load("res://shaders/post.gdshader")
	post.material = post_mat
	pl.add_child(post)
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
		var far := (mi.global_transform * mi.get_aabb()).get_center()
		if Vector2(far.x, far.z).length() > T.R + 3000.0 and mi.mesh != null:
			for si2 in mi.mesh.get_surface_count():
				var cm := mi.mesh.surface_get_material(si2) as BaseMaterial3D
				if cm != null and cm.shading_mode == BaseMaterial3D.SHADING_MODE_UNSHADED and cm.transparency != BaseMaterial3D.TRANSPARENCY_DISABLED:
					cm.disable_fog = true
		var am := mi.mesh as ArrayMesh
		if am != null:
			var bb0 := mi.get_aabb()
			for si in am.get_surface_count():
				var wm := am.surface_get_material(si) as StandardMaterial3D
				if wm != null and bb0.size.y < 3.0 and bb0.size.x > T.R and wm.transparency != BaseMaterial3D.TRANSPARENCY_DISABLED and wm.albedo_texture != null:
					water_mats.append(wm)
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
	for ri in 8:
		for ext in ["jpg", "png"]:
			var pp := "res://assets/kart/portrait%d.%s" % [ri, ext]
			if ResourceLoader.exists(pp):
				portraits[ri] = load(pp)
				break
	for k in ITEM_NAMES:
		var p := "res://assets/items/icon_%s.png" % k
		if ResourceLoader.exists(p):
			icons[k] = load(p)


# ---------------------------------------------------------------- karts

func _clear_race_nodes() -> void:
	if view != null:
		view.clear()
	if fx != null:
		fx.clear()


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


func _button(text: String, pos: Vector2) -> Button:
	var b := Button.new()
	b.text = text
	b.add_theme_font_size_override("font_size", 20)
	_place(b, 1, 0, 1, 0, pos.x, pos.y, pos.x + 140, pos.y + 44)
	b.focus_mode = Control.FOCUS_NONE
	return b


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
	hud = Hud.new()
	hud.kmh = opt_kmh
	hud_race.add_child(hud)
	lbl_info = _label(13, Vector2(0, 0), HORIZONTAL_ALIGNMENT_CENTER)
	_place(lbl_info, 0.5, 0, 0.5, 0, -300, 4, 300, 22)
	lbl_info.modulate.a = 0.8
	lbl_info.visible = false
	hud_race.add_child(lbl_info)
	btn_fps = Button.new()
	btn_res = Button.new()

	# results and pause: full-screen sheets in the menus' style, filled in when shown
	panel_results = PanelContainer.new()
	panel_results.add_theme_stylebox_override("panel", StyleBoxEmpty.new())
	panel_results.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	panel_results.visible = false
	root.add_child(panel_results)
	results_box = VBoxContainer.new()
	panel_pause = PanelContainer.new()
	panel_pause.add_theme_stylebox_override("panel", StyleBoxEmpty.new())
	panel_pause.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
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
	# the web's menus, over the live track
	var ml := CanvasLayer.new()
	ml.layer = 5
	add_child(ml)
	menu = Menu.new()
	menu.visible = false
	ml.add_child(menu)
	menu.go.connect(_menu_go)
	menu.modal_closed.connect(func():
		if state != "menu":
			menu.visible = false)
	menu.setting_changed.connect(func(k, v):
		sel[k] = v
		if k == "map" and String(v) != map_id:
			_menu_preview_map(String(v)))
	menu.modal_builders["mp"] = _mp_panel
	menu.modal_builders["set"] = _settings_panel
	loading = _loading_screen()
	loading.visible = false
	ml.add_child(loading)


func _apply_display() -> void:
	if not settings_loaded:
		fps_cap = 60 if is_phone else 0
		res_scale = 0.67 if is_phone else 1.0
	_apply_fps()
	_apply_res()
	var vp := get_viewport()
	_apply_quality()
	vp.use_debanding = true


func _toggle_fps() -> void:
	fps_cap = 120 if fps_cap == 60 else (0 if fps_cap == 120 else 60)
	_apply_fps()


func _apply_fps() -> void:
	Engine.max_fps = fps_cap
	btn_fps.text = ("Frame rate: %d" % fps_cap) if fps_cap > 0 else "Frame rate: max"


func _toggle_res() -> void:
	var steps := [0.5, 0.67, 0.8, 1.0]
	var i := steps.find(res_scale)
	res_scale = steps[(i + 1) % steps.size()]
	_apply_res()


func _apply_res() -> void:
	var vp := get_viewport()
	vp.scaling_3d_mode = Viewport.SCALING_3D_MODE_FSR if res_scale < 0.99 else Viewport.SCALING_3D_MODE_BILINEAR
	vp.scaling_3d_scale = res_scale
	vp.fsr_sharpness = 0.25 if sharpen_on else 2.0
	btn_res.text = "Resolution: %d%%" % int(round(res_scale * 100.0))


func _toggle_fullscreen() -> void:
	var w := get_window()
	w.mode = Window.MODE_MAXIMIZED if w.mode == Window.MODE_FULLSCREEN or w.mode == Window.MODE_EXCLUSIVE_FULLSCREEN else Window.MODE_FULLSCREEN


func _toggle_pause() -> void:
	if state == "results" or state == "menu":
		return
	if net_role != "":
		# an online race carries on for everyone: this only opens the menu
		panel_pause.visible = not panel_pause.visible
		if panel_pause.visible:
			_build_pause()
		return
	paused = not paused
	panel_pause.visible = paused
	if paused:
		_build_pause()


## a centred sheet over a dark wash (the web: .overlay > .panel, 520 CSS px wide)
func _sheet(host: Control, width_css := 520.0) -> VBoxContainer:
	for c in host.get_children():
		c.queue_free()
	var bg := Menu._Backdrop.new()
	bg.dim = 1.2
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	bg.mouse_filter = Control.MOUSE_FILTER_STOP
	host.add_child(bg)
	var cc := CenterContainer.new()
	cc.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	host.add_child(cc)
	var v := menu.vbox(14)
	v.custom_minimum_size.x = menu.z(width_css)
	cc.add_child(v)
	return v


func _build_pause() -> void:
	var v := _sheet(panel_pause)
	v.add_child(menu.label("PAUSED", menu.f_disp, 48.0, Color("#f7c948"), Color("#7d1d0e"), Vector2(0, 4)))
	var res := menu.button("Resume", "cta", 22.0, Vector4(16, 14, 16, 14))
	res.pressed.connect(_toggle_pause)
	v.add_child(res)
	var row := menu.hbox(10)
	for spec in [["Restart race", _restart], ["Settings", _pause_settings], ["Quit to menu", _to_menu.bind("")]]:
		var b := menu.button(String(spec[0]), "ghost", 15.0, Vector4(12, 12, 12, 12))
		b.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		b.pressed.connect(spec[1])
		row.add_child(b)
	v.add_child(row)
	res.grab_focus.call_deferred()


func _pause_settings() -> void:
	menu.visible = true
	menu.show_modal("set")


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
	if menu != null:
		menu.visible = false
		menu.close_modal()
	paused = false
	panel_pause.visible = false
	panel_results.visible = false
	panel_menu.visible = false
	hud_race.visible = true
	_clear_race_nodes()
	if cfg.has("map") and String(cfg["map"]) != map_id:
		if not load_map(String(cfg["map"])):
			_to_menu("This race is on %s, which isn't in your maps folder." % String(cfg["map"]))
			return
	race = Race.new()
	var pri := int(sel["ri"])
	if cfg.is_empty():
		race.setup(T, roster, pri, 0, String(sel["cls"]), _my_build())
	else:
		race.setup_cfg(T, roster, cfg, multiplayer.get_unique_id())
	kart = race.player
	if auto_drive and net_role != "client":
		kart.ai["auto"] = true
	race.items_off = items_off()
	var lss := String(cfg.get("mode", "")) == "lss" if not cfg.is_empty() else (String(sel.get("mode", "")) == "lss" and gp.is_empty())
	race.mode = "lss" if lss else ""
	T.LAPS = maxi(2, race.karts.size() - 1) if race.mode == "lss" else 3
	spec_k = null
	view.setup(T, race, fx, cam, items_lib)
	for k in race.karts:
		view.add_kart(k, _kart_scene)
	view.build_boxes()
	view.build_world_haz(haz_lib)
	view.build_pads()
	hud.race = race
	hud.me = kart
	hud.T = T
	# your best run on this track and class: its time under the clock, and its ghost (not in Last Slice Standing)
	if ghost == null:
		ghost = Ghost.new()
		ghost.name = "Ghost"
		add_child(ghost)
	var best := Ach.best(map_id, String(cfg.get("cls", sel["cls"])) if not cfg.is_empty() else String(sel["cls"]))
	hud.pb_text = ("Best " + Hud._fmt(float(best["t"]))) if not best.is_empty() else ""
	if race.mode == "lss" or auto_drive:
		ghost.start({}, false, kart.ri, {})
		ghost.recording = not auto_drive
	else:
		ghost.start(best, ghost_on, kart.ri, _my_build())
	hud.icons = icons
	hud.portraits = portraits
	hud.racer_cols = []
	for r in T.racers:
		hud.racer_cols.append(Color.html(String((r as Dictionary)["color"])))
	state = "countdown"
	cd = 3.2
	fin_t = 0.0
	last_lap = 1
	shown_finish = false
	was_last = false
	last_run = {}
	found_sc = {}
	net_fresh = true
	net_out.clear()
	cam_a = kart.ma
	cam_snap = true
	shake_imp = 0.0
	fin_punch = 0.0
	stats = {"used": {}, "spins": 0, "boxes": 0, "player_spins": 0, "abilities": {}}
	_show_center("3", 0.9)


func _show_center(t: String, dur: float, kind := "md") -> void:
	if hud != null:
		hud.banner(t, dur, kind)


func _kart_scene(file: String) -> PackedScene:
	if not kart_scenes.has(file):
		kart_scenes[file] = load("res://assets/kart/" + file)
	return kart_scenes[file]


## web shake(): impulses add up (to 1.6) and fade at the camera
func _shake(a: float) -> void:
	shake_imp = minf(1.6, shake_imp + a)


## web edgeFx: a colour flash creeping in from the screen edges
func _edge(col: Color, soft := false) -> void:
	edge_c = col
	edge_a = 0.5 if soft else 0.8
	edge_t = 0.3


func _toast(t: String, dur := 1.6) -> void:
	if hud != null:
		hud.banner(t, dur, "sm")


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
		if state != "results":
			race.haz_guest_step(dt)
		_net_client_tick()
		return
	if paused or test_hold:
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
			_show_center(str(after), 0.9)
			sfx.play("beep")
		if cd <= 0.0:
			state = "race"
			race.state = "race"
			_show_center("Go!", 1.0)
			sfx.play("go")
		for k in race.karts:
			k._save_prev()
		return
	race.update(dt, _input_state())
	_drain_events()
	if state == "race":
		if not auto_drive and kart != null and not kart.finished:
			if kart.glide:
				Ach.add("glide", dt)
			if race.race_time > 8.0 and race.stand.size() > 1 and race.stand[race.stand.size() - 1] == kart:
				was_last = true
		_finish_check()
		# the race is over once every person has finished (the computer drivers get estimated times)
		var all_done := true
		for k in race.karts:
			if k.peer != 0 and not k.finished:
				all_done = false
			elif k.peer != 0 and k.remote:
				k.ai["auto"] = true
		if race.mode == "lss":
			all_done = race.lss_done
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
	if race.mode == "lss":
		return
	if kart.finished and not shown_finish:
		shown_finish = true
		_progress_finish()
		kart.ai["auto"] = true
		_show_center("Finish!", 2.4)
		fin_punch = 0.0001
		_shake(0.5)
		sfx.play("finish")


## the player's run is in: personal best, recent races, achievements (not in the automatic test drives)
func _progress_finish() -> void:
	last_run = {}
	if auto_drive or kart == null or kart.est:
		return
	var cls := String(sel["cls"])
	var run := ghost.finish() if ghost != null and race.mode != "lss" else {}
	last_run = Ach.record(map_id, cls, kart.finish_time, kart.place, kart.ri, _my_build(), run)
	Ach.n_tracks = maxi(1, maps.size())
	Ach.race_done(kart.place, was_last, cls, kart.ri, map_id, gp)
	_ach_toasts()


## a toast for each achievement just won, one after another (web achToast)
func _ach_toasts() -> void:
	var i := 0
	while not Ach.fresh.is_empty():
		var a: Array = Ach.fresh.pop_front()
		var lv := KartBuilder.livery(String(a[5])) if KartBuilder.ready() else {}
		var txt := "Achievement: %s" % String(a[1]) + (" · %s livery unlocked" % String(lv.get("name", "")) if not lv.is_empty() else "")
		if String(a[6]) != "":
			txt += " · %s item unlocked" % String(Ach.ITEM_NAMES.get(String(a[6]), a[6]))
		get_tree().create_timer(0.4 + i * 4.2).timeout.connect(func():
			hud.toast(txt, 3.8)
			sfx.play("lap", 0.8, 1.2))
		i += 1


func _lap_check() -> void:
	var lp := kart.lap()
	if lp != last_lap and not kart.finished:
		last_lap = lp
		var split := ghost.lap(race.race_time, lp) if ghost != null else ""
		_toast(("Final lap" if lp == T.LAPS else "Lap %d" % lp) + (" · " + split if split != "" else ""), 2.0 if split != "" else 1.4)
		if lp == T.LAPS and music != null:
			music.final_lap()
		sfx.play("lap", 1.0, 1.2 if lp == T.LAPS else 1.0)


func _drain_events() -> void:
	if net_role == "host" and not net_peers.is_empty():
		for i in race.karts.size():
			for e in race.karts[i].events:
				net_out.append(["e", i, e])
		for e in race.fx:
			var d: Dictionary = (e as Dictionary).duplicate()
			for key in ["k", "a", "b", "by"]:
				if d.has(key) and d[key] is Kart:
					d[key] = race.karts.find(d[key])
			net_out.append(d)
	for k in race.karts:
		for e in k.events:
			view.kart_event(k, e)
			var mine := k == kart
			if e.begins_with("boost") and e.length() == 6:
				var tier := int(e.right(1))
				if mine and tier == 3 and not auto_drive and state == "race":
					Ach.add("drift3")
				if mine:
					_shake(0.15 + tier * 0.05)
					sfx.play("boost", 0.8, 1.0 + 0.12 * tier)
			elif e == "pad":
				if mine:
					_shake(0.25)
					sfx.play("boost", 0.7)
			elif e == "sc" or e == "sc_new":
				if mine and not auto_drive and state == "race":
					Ach.add("routes")
				if mine and e == "sc_new" and not found_sc.has(k.sc):
					# a hidden shortcut found for the first time this race
					found_sc[k.sc] = true
					sfx.play("tier", 0.9, 1.3)
					_edge(Color("#7dff8a"), true)
			elif e == "loopout":
				if mine and not auto_drive and state == "race":
					Ach.add("loops")
				if mine:
					_shake(0.5)
					sfx.play("boost", 0.8, 1.3)
			elif e == "loopin":
				if mine:
					sfx.play("boost", 0.6, 1.2)
			elif e == "wall":
				if mine:
					_shake(0.25)
					sfx.play("bump", 0.7)
			elif e == "bump":
				if mine:
					_shake(0.5)
				sfx.play("bump", _near(k))
			elif e == "respawn":
				if mine:
					cam_snap = true
					_shake(0.4)
					_edge(Color.WHITE, true)
					sfx.play("bump")
			elif e == "land":
				if mine:
					_shake(0.55)
				sfx.play("land", 0.7 * maxf(_near(k), 0.4 if mine else 0.0))
			elif e == "hop":
				if mine:
					sfx.play("hop", 0.6)
			elif e.begins_with("tier"):
				if mine:
					sfx.play("tier", 0.6, 0.8 + 0.2 * int(e.right(1)))
			elif e == "trick":
				if mine:
					sfx.play("trick", 0.7)
					var tn: String = TRICK_NAMES[clampi(k.trick_k, 0, 4)]
					_show_center(tn + (" x%d" % k.g_tr if k.g_tr > 1 else "") + "!", 0.6, "sm")
			elif e == "ready":
				if mine:
					sfx.play("ready", 0.8)
		k.events.clear()
	for e in race.fx:
		var ed: Dictionary = e
		view.race_event(ed)
		var t: String = ed["t"]
		if t == "spin":
			var k: Kart = ed["k"]
			stats["spins"] = int(stats["spins"]) + 1
			sfx.play("hit", _near(k))
			if k == kart:
				stats["player_spins"] = int(stats["player_spins"]) + 1
				_shake(1.1)
				hud.hit_flash()
		elif t == "box":
			stats["boxes"] = int(stats["boxes"]) + 1
			sfx.play("pickup", 0.8 if ed["k"] == kart else _near(ed["k"]) * 0.3)
		elif t == "use":
			var it: String = ed["it"]
			if ed["k"] == kart and not auto_drive and state == "race":
				Ach.add("items")
			stats["used"][it] = int(stats["used"].get(it, 0)) + 1
			var k2: Kart = ed["k"]
			sfx.play("boost" if it in ["chili", "rush", "jalapeno", "shroom", "cannon", "magnet"] else ("shield" if it in ["ghost", "garlic2"] else "throw"), 0.9 if k2 == kart else _near(k2) * 0.5)
			if k2 == kart and it == "cannon":
				_shake(1.2)
			elif k2 == kart and it == "shroom":
				_shake(0.4)
			if k2 == kart:
				_shake(0.18)
		elif t == "shield":
			stats["used"]["garlic"] = int(stats["used"].get("garlic", 0)) + 1
			sfx.play("shield", 0.8 if ed["k"] == kart else _near(ed["k"]) * 0.4)
			if ed["k"] == kart:
				_edge(Color("#fff3c4"), true)
		elif t == "unshield" or t == "absorb":
			var k3: Kart = ed["k"]
			if k3 == kart and t == "absorb" and not auto_drive:
				Ach.add("blocks")
			sfx.play("block", 0.9 if k3 == kart else _near(k3) * 0.5)
			if k3 == kart:
				_shake(0.35)
				_edge(Color("#fff3c4"), t == "absorb")
		elif t == "flour":
			var p := Vector3(float(ed["x"]), T.ground(float(ed["x"]), float(ed["y"])) + 5.0, float(ed["y"]))
			sfx.play("boom", clampf(1.0 - p.distance_to(cam.global_position) / 500.0, 0.0, 1.0))
			if Vector2(p.x - cam.global_position.x, p.z - cam.global_position.z).length() < 120.0:
				_shake(0.5)
		elif t == "clash":
			sfx.play("bump", 0.5)
		elif t == "hzbump":
			var k5: Kart = ed["k"]
			if k5 == kart:
				_shake(0.6)
			sfx.play("bump", _near(k5))
		elif t == "bump":
			if ed["a"] == kart or ed["b"] == kart:
				_shake(0.22)
				sfx.play("bump", 0.55)
		elif t == "slice":
			var k4: Kart = ed["k"]
			sfx.play("boom", maxf(0.3, _near(k4)))
			if k4 == kart:
				_shake(1.6)
		elif t == "wind":
			if ed["k"] == kart:
				sfx.play("warn")
		elif t == "oily":
			if ed["k"] == kart:
				_show_center("Oily wheels!", 0.9, "sm")
				_edge(Color("#c8b23a"), true)
				_shake(0.25)
		elif t == "ability":
			var ka: Kart = ed["k"]
			stats["abilities"][String(ed["id"])] = int(stats["abilities"].get(String(ed["id"]), 0)) + 1
			var A: Array = Race.ABIL.get(String(ed["id"]), ["", "", "#ffe066"])
			if ka == kart:
				sfx.play("ability", 0.9)
				_show_center(String(A[0]), 1.1, "sm")
				_shake(0.6)
				hud.abil_flash(Color(String(A[2])))
			elif _near(ka) > 0.0:
				sfx.play("ability", _near(ka) * 0.6)
		elif t == "ability_ready":
			if ed["k"] == kart:
				sfx.play("ready", 0.8)
		elif t == "melt":
			if ed["k"] == kart:
				sfx.play("shield", 0.9)
				sfx.play("block", 0.6)
				_shake(0.2)
		elif t == "flat":
			var kf: Kart = ed["k"]
			if kf == kart:
				_shake(0.55)
			elif ed.get("by") == kart:
				_shake(0.3)
			sfx.play("bump", maxf(_near(kf), 0.4))
		elif t == "blast":
			var bsc := maxf(1.0, float(ed["r"]) / 130.0)
			var bp := Vector2(float(ed["x"]), float(ed["y"]))
			var cd2 := Vector2(cam.global_position.x, cam.global_position.z).distance_to(bp)
			sfx.play("boom", maxf(0.3, clampf(1.0 - cd2 / 420.0, 0.0, 1.0)))
			if cd2 < 160.0 * bsc:
				_shake(0.9 * minf(1.6, bsc))
		elif t == "dodge":
			if ed["k"] == kart:
				_show_center("Dodged!", 0.6, "sm")
		elif t == "elim":
			var ke: Kart = ed["k"]
			if bool(ed["loud"]):
				_show_center(("You\u2019re out" if ke == kart else ke.racer_name + " is out") + " \u00b7 " + _ordinal(int(ed["place"])), 2.2, "sm")
				sfx.play("hit", 0.8, 0.7)
			if ke == kart:
				kart.ai["auto"] = true
		elif t == "lss_win":
			var kw: Kart = ed["k"]
			sfx.play("finish")
			if kw == kart:
				_show_center("Last Slice Standing!", 2.6, "md")
				if not auto_drive:
					Ach.race_done(1, was_last, String(sel["cls"]), kart.ri, map_id, {})
					_ach_toasts()
			else:
				_show_center(kw.racer_name + " wins!", 2.4, "md")
			kart.ai["auto"] = true
		elif t == "frozen":
			if ed["k"] == kart:
				_edge(Color("#bfe6ff"))
				sfx.play("block", 0.7, 1.4)
		elif t == "sauced":
			if ed["k"] == kart:
				hud.sauce_on()
				sfx.play("hit", 0.6, 0.8)
		elif t == "heat":
			hud.heat_flash()
			sfx.play("boom", 0.6, 1.3)
			if kart != null and kart.shrink_t > 0.0:
				_shake(0.8)
		elif t == "robbed":
			if ed["k"] == kart:
				_edge(Color("#b26bff"))
				sfx.play("block", 0.7)
		elif t == "swap":
			if ed["k"] == kart or ed["by"] == kart:
				cam_snap = true
				sfx.play("tier", 0.8, 0.7)
			if ed["by"] == kart:
				_edge(Color("#b26bff"))
		elif t == "ricochet":
			var rp := Vector3(float(ed["x"]), T.ground(float(ed["x"]), float(ed["y"])), float(ed["y"]))
			sfx.play("bump", clampf(1.0 - rp.distance_to(cam.global_position) / 420.0, 0.0, 1.0) * 0.45)
	race.fx.clear()


func _kpos(k: Kart) -> Vector3:
	return Vector3(k.x, k.wy, k.y)


## how loud something at a kart sounds from the camera: 1 next to it, 0 far away
func _near(k: Kart) -> float:
	return clampf(1.0 - _kpos(k).distance_to(cam.global_position) / 420.0, 0.0, 1.0)


func _show_results() -> void:
	var st := race.standings()
	var me_place := st.find(kart) + 1
	var gp_done := false
	var gp_rows: Array = []
	if not gp.is_empty():
		# points for this race, then the cup table
		if not bool(gp.get("scored", false)):
			for i in st.size():
				var ri := st[i].ri
				gp["pts"][ri] = int(gp["pts"][ri]) + (Race.PTS[i] if i < Race.PTS.size() else 0)
			gp["scored"] = true
		for k in race.karts:
			gp_rows.append([k, int(gp["pts"][k.ri])])
		gp_rows.sort_custom(func(a, b): return a[1] > b[1])
		gp_done = int(gp["race"]) >= (gp["tracks"] as Array).size() - 1
	var v := _sheet(panel_results, 820.0 if not gp.is_empty() else 520.0)
	var title := "%s place!" % _ordinal(me_place)
	if gp_done:
		var cp := 1
		for i in gp_rows.size():
			if gp_rows[i][0] == kart:
				cp = i + 1
		title = ("You win the %s!" % Menu.CUPS[int(gp["cup"])][0]) if cp == 1 else ("%s in the cup" % _ordinal(cp))
		if not auto_drive:
			Ach.cup_done(gp, cp, String(sel["cls"]))
			_ach_toasts()
	v.add_child(menu.label(title, menu.f_disp, 48.0, Color("#f7c948"), Color("#7d1d0e"), Vector2(0, 4)))
	var sub := "%s · %s" % [String(_map_info(map_id).get("name", map_id)), String({"small": "50cc", "medium": "100cc", "large": "200cc", "reverse": "Reverse"}.get(String(sel["cls"]), "100cc"))]
	if not gp.is_empty():
		sub += " · race %d of %d" % [int(gp["race"]) + 1, (gp["tracks"] as Array).size()]
	v.add_child(menu.label(sub, menu.f_semi, 15.0, Color("#c2a58c")))
	if not last_run.is_empty():
		var lr := last_run
		var pbt := ""
		if bool(lr["pb"]):
			pbt = ("First time logged · " + _fmt(float(lr["t"]))) if float(lr["old"]) < 0.0 else ("New personal best! %s (−%.2fs)" % [_fmt(float(lr["t"])), float(lr["old"]) - float(lr["t"])])
		else:
			pbt = "Personal best %s · +%.2fs" % [_fmt(float(lr["old"])), float(lr["t"]) - float(lr["old"])]
		v.add_child(menu.label(pbt, menu.f_bold, 15.0, Color("#7fe07a") if bool(lr["pb"]) else Color("#c2a58c")))
	var cols := menu.hbox(14)
	v.add_child(cols)
	var c1 := menu.vbox(6)
	c1.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	cols.add_child(c1)
	c1.add_child(menu.section_label("Race"))
	for i in st.size():
		var k := st[i]
		var rtxt := ("~" if k.est else "") + _fmt(k.finish_time)
		if race.mode == "lss":
			rtxt = ("out on lap %d" % k.elim_lap) if k.elim else ("last slice" if k.place == 1 else _fmt(k.finish_time))
		c1.add_child(_result_row(i + 1, k, rtxt, "+%d" % (Race.PTS[i] if i < Race.PTS.size() else 0) if not gp.is_empty() else ""))
	if not gp.is_empty():
		var c2 := menu.vbox(6)
		c2.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		cols.add_child(c2)
		c2.add_child(menu.section_label("Cup standings"))
		for i in gp_rows.size():
			c2.add_child(_result_row(i + 1, gp_rows[i][0], "%d pts" % int(gp_rows[i][1]), ""))
	var again_text := "Race again"
	if not gp.is_empty():
		again_text = "New Grand Prix" if gp_done else "Next race  ›"
	if net_role == "client":
		again_text = "Waiting for the host…"
	var again := menu.button(again_text, "cta", 22.0, Vector4(16, 14, 16, 14))
	again.disabled = net_role == "client"
	again.pressed.connect(_results_primary)
	v.add_child(again)
	var row := menu.hbox(10)
	var tb := menu.button("Choose another track", "ghost", 15.0, Vector4(12, 12, 12, 12))
	tb.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	tb.pressed.connect(func():
		_to_menu("")
		menu.open("track"))
	row.add_child(tb)
	var mb := menu.button("Change track or driver", "ghost", 15.0, Vector4(12, 12, 12, 12))
	mb.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	mb.pressed.connect(_to_menu.bind(""))
	row.add_child(mb)
	v.add_child(row)
	panel_results.visible = true
	if not auto_drive and net_role != "client":
		again.grab_focus.call_deferred()


## one line of a results table: place, the racer's colour, name, time or points
func _result_row(place: int, k: Kart, right: String, add: String) -> Control:
	var me := k == kart
	var st := menu.glass(10.0, Vector4(12, 7, 12, 7))
	if me:
		st = menu.box([Color(0.97, 0.79, 0.28, 0.2), Color(0.88, 0.27, 0.17, 0.14)], 135.0, 10.0, Color("#f7c948"), 1.0, Vector4(12, 7, 12, 7))
	var p := menu.panel(st)
	var h := menu.hbox(10)
	p.add_child(h)
	var pc := [Color("#ffd54a"), Color("#d8dde3"), Color("#e09a5a")]
	var pl := menu.label(str(place), menu.f_disp, 16.0, pc[place - 1] if place <= 3 else Color("#f7c948"))
	pl.custom_minimum_size.x = menu.z(26)
	h.add_child(pl)
	var sw := ColorRect.new()
	sw.color = hud._racer_col(k)
	sw.custom_minimum_size = Vector2(menu.z(12), menu.z(12))
	sw.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	h.add_child(sw)
	var nm := menu.label(k.racer_name + ("  (you)" if me else ""), menu.f_bold, 15.0, Color("#fff4dc"))
	nm.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	h.add_child(nm)
	if add != "":
		h.add_child(menu.label(add, menu.f_bold, 14.0, Color("#7fe07a")))
	h.add_child(menu.label(right, menu.f_semi, 14.0, Color("#c2a58c")))
	return p


## the results screen's main button: race again, the next Grand Prix race, or a new cup
func _results_primary() -> void:
	if net_role == "client":
		return
	if gp.is_empty():
		_restart()
		return
	var n := (gp["tracks"] as Array).size()
	if int(gp["race"]) >= n - 1:
		gp = {"cup": int(gp["cup"]), "race": 0, "pts": [0, 0, 0, 0, 0, 0, 0, 0], "tracks": gp["tracks"]}
	else:
		gp["race"] = int(gp["race"]) + 1
		gp["scored"] = false
	panel_results.visible = false
	await _race_on(String(gp["tracks"][int(gp["race"])]))


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
	look_back = look or test_look
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
	elif ev is InputEventMouseButton:
		var mb := ev as InputEventMouseButton
		if mb.pressed and mb.button_index == MOUSE_BUTTON_LEFT and hud != null and hud_race.visible and state != "menu":
			if hud.pause_rect().has_point(mb.position):
				_toggle_pause()
			elif hud.special_rect().has_point(mb.position):
				item_queued = "ability"
			elif hud.item_rect(1).has_point(mb.position):
				item_queued = "fwd"
			elif hud.item_rect(2).has_point(mb.position):
				item_queued = "fwd2"
	elif ev is InputEventKey:
		var kev := ev as InputEventKey
		if kev.pressed and not kev.echo:
			match kev.keycode:
				KEY_F3:
					lbl_info.visible = not lbl_info.visible
				KEY_X, KEY_E, KEY_ENTER:
					if state == "menu" or state == "results" or paused or (ip_edit != null and is_instance_valid(ip_edit) and ip_edit.has_focus()):
						pass
					else:
						item_queued = "fwd"
				KEY_Z, KEY_Q, KEY_V:
					item_queued = "fwd2"
				KEY_SHIFT, KEY_B:
					item_queued = "hold"
				KEY_C, KEY_R:
					if state == "race":
						item_queued = "ability"
				KEY_P, KEY_ESCAPE:
					if not (menu != null and menu.visible):
						_toggle_pause()
				KEY_F11:
					_toggle_fullscreen()
	elif ev is InputEventJoypadButton:
		var jb := ev as InputEventJoypadButton
		if jb.pressed:
			pad_used_at = Time.get_ticks_msec()
			if jb.button_index == JOY_BUTTON_Y and state == "race":
				item_queued = "ability"
			if jb.button_index == JOY_BUTTON_START:
				if state == "results":
					_results_primary()
				elif not (menu != null and menu.visible):
					_toggle_pause()


func _zone(p: Vector2) -> String:
	if hud.pedal_rect(0).has_point(p) or hud.pedal_rect(1).has_point(p):
		return "pedal"
	return "l" if p.x < get_viewport().get_visible_rect().size.x * 0.5 else "r"


# ---------------------------------------------------------------- drawing

func _process(dt: float) -> void:
	if music != null and not auto_drive:
		music.want(map_id, "loading" if (loading != null and loading.visible) else state, paused, dt)
	if T == null or race == null:
		return
	if not paused:
		time += dt
	var al := 1.0 if (paused or state == "menu") else Engine.get_physics_interpolation_fraction()
	if net_role == "client":
		al = clampf((Time.get_ticks_msec() / 1000.0 - net_snap_at) / net_snap_dt, 0.0, 1.0)
	view.draw(al, dt, state == "race", paused)
	if kart.elim and race.mode == "lss" and state == "race":
		var st0 := race.standings()
		for q in st0:
			if not q.finished:
				spec_k = q
				break
	var ck: Kart = spec_k if spec_k != null and kart.elim else kart
	var v: Dictionary = view.views[ck]
	_camera(dt, float(v["rx"]), float(v["ry"]), float(v["rz"]), float(v["rma"]))
	if ghost != null:
		if state == "race" and not paused:
			ghost.record(race.race_time, (view.views[kart]["tilt"] as Node3D).global_transform, kart.finished)
		ghost.tick(race.race_time if state == "race" else 0.0, state == "race" or state == "countdown", cam.global_position)
	# shadows follow your kart (the web re-centres its shadow camera 80 ahead of it)
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
			var cdist: float = CULL_DIST * [0.6, 1.0, 1.5][clampi(scenery, 0, 2)]
			var vis: bool = dd < (cdist * 1.08 if was else cdist)
			if vis != was:
				c["vis"] = vis
				(c["node"] as Node3D).visible = vis
	# the sea drifts and breathes (web buildWater animator)
	for wm in water_mats:
		var w: StandardMaterial3D = wm
		w.uv1_offset += Vector3(dt * 0.004, dt * 0.003, 0.0) * (0.0 if paused else 1.0)
	# post: edge flash, speed streaks while boosting
	if edge_t > 0.0:
		edge_t -= dt
	var ea := edge_a * clampf(edge_t / 0.3, 0.0, 1.0)
	post_mat.set_shader_parameter("edge_c", Vector3(edge_c.r, edge_c.g, edge_c.b))
	post_mat.set_shader_parameter("edge_a", ea)
	spd_fx += ((1.0 if (kart.boost > 0.0 and state == "race") else 0.0) - spd_fx) * minf(1.0, dt / 0.25)
	post_mat.set_shader_parameter("spd", spd_fx)
	post_mat.set_shader_parameter("tm", time)
	_hud(dt)


## the web game's close chase camera: it eases round behind the kart, hangs on a sprung mount, leans
## into turns and with the ground, shakes with speed and hits, and rides round the loop-the-loop
func _camera(dt: float, rx: float, ry: float, rz: float, rma: float) -> void:
	var k: Kart = spec_k if spec_k != null and kart.elim else kart
	var v: Dictionary = view.views[k]
	if state == "menu":
		var oa := time * 0.18 + k.a + 2.4
		cam.position = Vector3(rx + cos(oa) * 62.0, rz + 17.0 + sin(time * 0.3) * 3.0, ry + sin(oa) * 62.0)
		cam.look_at(Vector3(rx, rz + 6.0, ry), Vector3.UP)
		cam.fov = 55.0
		cam_snap = true
		cam_a = k.ma
		return
	cam_a = lerp_angle(cam_a, rma, 1.0 - exp(-5.5 * dt))
	var ex := maxf(0.0, float(v["top"]) - 7.2) * T.KS
	var cS := cam_d / 100.0
	var dist := ((44.0 if cam_far else 30.0) + ((4.0 if cam_far else 5.0) if k.boost > 0.0 else 0.0) + ex * 1.1) * cS
	var h := ((17.4 if cam_far else 12.6) + ex * 0.8) * (0.4 + 0.6 * cS)
	var lb := look_back and state == "race" and k.loop.is_empty()
	if lb != cam_lb:
		cam_lb = lb
		cam_snap = true
	var fx_ := cos(cam_a) * (-1.0 if lb else 1.0)
	var fy := sin(cam_a) * (-1.0 if lb else 1.0)
	var rg := T.ground(rx, ry)
	if not T.glide.is_empty():
		var gyy := T.glide_y(rx, ry)
		if rg < gyy - 20.0:
			rg = minf(rz, gyy)
	var cy := rz - 4.0 if k.glide else rg + (rz - rg) * 0.45
	var tv2 := Vector3(rx - fx_ * dist, cy + h, ry - fy * dist)
	var tv := Vector3(rx + fx_ * 32.0, cy + 6.2 + ex * 0.5, ry + fy * 32.0)
	var in_loop := not k.loop.is_empty() and k.loop.has("p")
	var up_t := Vector3.UP
	if in_loop:
		var P: Dictionary = k.loop["p"]
		var th := k.loop_th
		var F := Vector3(float(P["tx"]) * cos(th), sin(th), float(P["ty"]) * cos(th)).normalized()
		var U := Vector3(-float(P["tx"]) * sin(th), cos(th), -float(P["ty"]) * sin(th))
		var kp := Vector3(rx, rz, ry)
		tv2 = kp - F * 30.0 + U * 13.0
		tv = kp + F * 16.0 + U * 3.0
		cam_base = cam_base.lerp(tv2, 1.0 - exp(-16.0 * dt))
		cam_look = cam_look.lerp(tv, 1.0 - exp(-18.0 * dt))
		cam_up = cam_up.lerp(U, 1.0 - exp(-12.0 * dt)).normalized()
		cam_a = float(P["ang"])
	else:
		cam_up = cam_up.lerp(Vector3.UP, 1.0 - exp(-8.0 * dt)).normalized()
		if cam_snap:
			cam_base = tv2
			cam_look = tv
			cam_snap = false
		else:
			cam_base = cam_base.lerp(tv2, 1.0 - exp(-12.0 * dt))
			cam_look = cam_look.lerp(tv, 1.0 - exp(-16.0 * dt))
		# hills and banks beside the road: pull the camera in along its line of sight instead of sinking into the ground
		var t := 1.0
		while t > 0.3:
			var x := cam_look.x + (cam_base.x - cam_look.x) * t
			var z := cam_look.z + (cam_base.z - cam_look.z) * t
			var y := cam_look.y + (cam_base.y - cam_look.y) * t
			if y >= T.ground(x, z) + 2.5:
				break
			t -= 0.1
		cam_occ = t if t < cam_occ else cam_occ + (t - cam_occ) * minf(1.0, dt * 3.0)
		if cam_occ < 0.999:
			cam_base = cam_look + (cam_base - cam_look) * cam_occ
		var fl := T.ground(cam_base.x, cam_base.z) + 2.5
		if cam_base.y < fl:
			cam_base.y = fl
	var spn := minf(1.4, absf(k.speed) / k.base_max)
	var lat := absf(T.lateral(k.idx, k.x, k.y))
	var sf := 2 if lat < T.RW else (1 if lat < T.CURB else 0)
	var amp := 0.03 + 0.09 * spn + (0.32 if sf == 0 and spn > 0.25 else (0.12 if sf == 1 and spn > 0.25 else 0.0)) + (0.24 if k.boost > 0.0 else 0.0) + shake_imp
	shake_imp *= exp(-6.0 * dt)
	if not shake_on:
		amp = 0.0
	var bo := k.boost > 0.0
	if bo and not cam_bo and state == "race":
		_shake(0.75)
	cam_bo = bo
	if state == "countdown":
		amp = 0.02
	var n1 := sin(time * 29.0) * 0.5 + sin(time * 47.3 + 1.3) * 0.3 + sin(time * 11.7 + 0.7) * 0.2
	var n2 := sin(time * 33.1 + 2.0) * 0.5 + sin(time * 53.0 + 0.4) * 0.3 + sin(time * 9.3 + 1.1) * 0.2
	var n3 := sin(time * 26.7 + 4.0) * 0.5 + sin(time * 41.0 + 2.2) * 0.5
	var G := 0.0 if (state == "countdown" or in_loop or dt <= 0.0) else 1.0
	var ff := func(kk: float) -> float: return 1.0 - exp(-kk * dt)
	var acc := (k.speed - cam_pspd) / dt if dt > 0.0 else 0.0
	cam_pspd = k.speed
	cam_gp += ((float(v["tp"]) * 0.4 - clampf(acc * 0.00016, -0.035, 0.035)) * G - cam_gp) * ff.call(6.0)
	cam_gr += ((float(v["tr"]) * 0.5 - k.steer * 0.04 - (k.steer * 0.035 * k.d_amt if k.drift != 0 else 0.0)) * G - cam_gr) * ff.call(5.0)
	cam_sx += (k.steer * 2.4 * spn * G - cam_sx) * ff.call(3.0)
	var vz := (rz - cam_pvz) / dt if dt > 0.0 else 0.0
	cam_pvz = rz
	var f := (-cam_oy * 55.0 - cam_vy * 9.0) + clampf(-vz * 0.9, -40.0, 40.0) * G * (0.25 if k.air else 1.0)
	cam_vy += f * dt
	cam_oy = clampf(cam_oy + cam_vy * dt, -2.6, 2.6)
	var sx_ := sin(cam_a)
	var sz_ := -cos(cam_a)
	cam.position = Vector3(cam_base.x + n1 * amp * 0.3 - sx_ * cam_sx, cam_base.y + n2 * amp * 0.35 + cam_oy, cam_base.z + n3 * amp * 0.3 - sz_ * cam_sx)
	var look := Vector3(cam_look.x, cam_look.y + cam_oy * 0.45, cam_look.z)
	if cam.position.distance_to(look) > 0.1:
		cam.look_at(look, cam_up)
	cam.rotate_object_local(Vector3(1, 0, 0), -cam_gp)
	cam.rotate_object_local(Vector3(0, 0, 1), cam_gr + n3 * amp * 0.006)
	var vs := get_viewport().get_visible_rect().size
	var aspect := vs.x / maxf(1.0, vs.y)
	var hf := deg_to_rad((96.0 if cam_far else 100.0) if k.boost > 0.0 else (90.0 if cam_far else 92.0))
	var vf := clampf(rad_to_deg(2.0 * atan(tan(hf / 2.0) / aspect)), 52.0, 100.0)
	var fp := 0.0
	if fin_punch > 0.0:
		fin_punch += dt
		fp = sin(minf(1.0, fin_punch / 0.8) * PI) * (fin_punch / 0.12 if fin_punch < 0.12 else 1.0) * 14.0
		if fin_punch > 0.8:
			fin_punch = 0.0
	vf += fp
	if absf(cam.fov - vf) > 0.05:
		cam.fov += (vf - cam.fov) * minf(1.0, (18.0 if fp > 0.0 else 5.0) * dt)
	# the sun's shadow box follows the kart (centred 80 ahead of it)
	var sc := Vector3(rx + cos(cam_a) * 80.0, rg, ry + sin(cam_a) * 80.0)
	sun.global_position = sc


func _hud(dt: float) -> void:
	var k := kart
	hud.fps_on = fps_counter
	lbl_info.text = "%d fps · %s · %dk tris · %d draws" % [Engine.get_frames_per_second(), RenderingServer.get_current_rendering_driver_name(), int(Performance.get_monitor(Performance.RENDER_TOTAL_PRIMITIVES_IN_FRAME)) / 1000, int(Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME))]
	sfx.drive(absf(k.speed) / k.base_max, true, k.boost > 0.0, k.drift != 0 and not k.air, k.tier, state != "countdown" and state != "results" and state != "menu" and not paused)
	if k.roll > 0.0 and not paused:
		roll_tick -= dt
		if roll_tick <= 0.0:
			roll_tick = 0.09
			sfx.play("roll", 0.5)
	# wrong way: moving against the track for most of a second
	var back := state == "race" and not k.finished and k.spin <= 0.0 and k.speed > 15.0 and (cos(k.ma) * T.tx[k.idx] + sin(k.ma) * T.ty[k.idx]) < -0.4
	hud.wrong_t = hud.wrong_t + dt if back else 0.0
	var st := 0
	for z in touches.values():
		if z == "l":
			st = -1
		elif z == "r":
			st = 1
	if st == 0:
		st = -1 if k.steer < -0.3 else (1 if k.steer > 0.3 else 0)
	hud.steer_dir = st
	hud.braking = k.brake > 0.04
	hud.look = look_back
	hud.pad_mode = Time.get_ticks_msec() - pad_used_at < 20000
	hud.tick(dt)


func _fmt(t: float) -> String:
	var m := int(t / 60.0)
	var s := t - m * 60.0
	return "%d:%05.2f" % [m, s]


# ---------------------------------------------------------------- menu and online

func _to_menu(note: String) -> void:
	_net_close()
	gp = {}
	_start_race({})
	state = "menu"
	hud_race.visible = false
	hud.banner("", 0.0)
	panel_menu.visible = false
	panel_results.visible = false
	panel_pause.visible = false
	_menu_sync()
	menu.open("home")
	if note != "":
		menu.show_modal("mp")
		_menu_refresh(note)


## hand the menu what it shows: tracks, drivers, portraits, the current choices
func _menu_sync() -> void:
	menu.maps = maps
	menu.roster = roster
	menu.portraits = portraits
	var rj := FileAccess.get_file_as_string("res://assets/racers.json")
	var ra = JSON.parse_string(rj) if rj != "" else null
	menu.racers_info = ra if ra is Array else T.racers
	menu.mode = String(sel["mode"])
	menu.cls = String(sel["cls"])
	menu.ri = int(sel["ri"])
	menu.cup = int(sel["cup"])
	menu.map_id = map_id
	menu.build = _my_build() if KartBuilder.ready() else menu.build


## the player's kart build: the garage's choice, else the build the web game gave this driver
func _my_build() -> Dictionary:
	if not KartBuilder.ready():
		return {}
	var b = sel.get("build")
	if b is Dictionary and not (b as Dictionary).is_empty():
		return b
	var pl: Dictionary = roster.get("player", {})
	return {"b": int(pl.get("b", 0)), "w": int(pl.get("w", 0)), "g": int(pl.get("g", 0)), "p": int(pl.get("p", 0)), "t": String(pl.get("t", ""))}


## the track menu: show the chosen track behind the menu
func _menu_preview_map(id: String) -> void:
	if state != "menu":
		return
	await _with_loading("Loading " + String(_map_info(id).get("name", id)) + "…")
	if load_map(id):
		_start_race({})
		state = "menu"
		hud_race.visible = false
	loading.visible = false


## items left out of races: the award items until their achievement is won, and any switched off in Settings
func items_off() -> Dictionary:
	var off := {}
	for it in Race.ITEM_AWARD:
		if not Ach.unlocked(String(Race.ITEM_AWARD[it])):
			off[it] = true
	for it in item_set:
		if item_set[it] == false:
			off[it] = true
	return off


## the rivals get new karts each time a race or Grand Prix starts from the menu (web cpuBuilds)
func _new_cpu_builds() -> void:
	if not KartBuilder.ready():
		return
	for r in roster.get("racers", []):
		(r as Dictionary)["build"] = KartBuilder.random_build()


## the menu's Start: a single race, Last Slice, or a whole Grand Prix cup
func _menu_go(o: Dictionary) -> void:
	sel.merge(o, true)
	_new_cpu_builds()
	var id := String(o.get("map", map_id))
	if String(o["mode"]) == "gp":
		var ts: Array = []
		for m in maps:
			if int(m.get("cup", -1)) == int(o.get("cup", 0)):
				ts.append(String(m["id"]))
		if ts.is_empty():
			ts = [map_id]
		gp = {"cup": int(o.get("cup", 0)), "race": 0, "pts": [0, 0, 0, 0, 0, 0, 0, 0], "tracks": ts}
		id = ts[0]
	else:
		gp = {}
	menu.visible = false
	await _race_on(id)


func _race_on(id: String) -> void:
	if id != map_id:
		await _with_loading("Loading " + String(_map_info(id).get("name", id)) + "…")
		if not load_map(id):
			loading.visible = false
			_to_menu("Couldn't load that track.")
			return
	loading.visible = false
	if net_role == "host":
		_net_start()
	else:
		_start_race({})


func _with_loading(text: String) -> void:
	(loading.get_meta("txt") as Label).text = text
	loading.visible = true
	await get_tree().process_frame
	await get_tree().process_frame


## the web's loading screen: logo, spinning pizza, the oven bar
func _loading_screen() -> Control:
	var c := ColorRect.new()
	c.color = Color("#1a0d08")
	c.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	var v := VBoxContainer.new()
	v.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	v.alignment = BoxContainer.ALIGNMENT_CENTER
	v.add_theme_constant_override("separation", 18)
	v.grow_horizontal = Control.GROW_DIRECTION_BOTH
	v.grow_vertical = Control.GROW_DIRECTION_BOTH
	c.add_child(v)
	var lg := menu.logo("CRUST RUSH", 62.0)
	lg.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
	v.add_child(lg)
	var t := menu.label("Firing up the oven…", menu.f_med, 13.0, Color("#c2a58c"))
	t.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	v.add_child(t)
	c.set_meta("txt", t)
	return c


## Play with friends (PC to PC): host or join, the address, who has joined, start
func _mp_panel() -> Control:
	var v := menu.vbox(12)
	var card := menu.panel(menu.glass(18.0, Vector4(18, 16, 18, 16)))
	v.add_child(card)
	var cv := menu.vbox(12)
	card.add_child(cv)
	cv.add_child(menu.section_label("Online race, PC to PC"))
	lbl_menu = menu.para("Everyone plays on the PC version. One player hosts; the others type the host's address and join. The host picks the track and starts the race.", 15.0, Color("#c2a58c"), 640.0)
	cv.add_child(lbl_menu)
	var row := menu.hbox(10)
	var hb := menu.button("Host a race", "cta", 19.0, Vector4(20, 12, 20, 12))
	hb.pressed.connect(_menu_host)
	row.add_child(hb)
	ip_edit = LineEdit.new()
	ip_edit.placeholder_text = "Host's address, e.g. 192.168.1.20"
	ip_edit.add_theme_font_override("font", menu.f_semi)
	ip_edit.add_theme_font_size_override("font_size", menu.zi(16))
	ip_edit.add_theme_stylebox_override("normal", menu.glass(12.0, Vector4(12, 10, 12, 10)))
	ip_edit.add_theme_stylebox_override("focus", menu.box([Color(1, 0.957, 0.863, 0.08)], 180.0, 12.0, Color("#f7c948"), 2.0, Vector4(12, 10, 12, 10)))
	ip_edit.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	ip_edit.text = net_addr_last
	row.add_child(ip_edit)
	var jb := menu.button("Join", "ghost", 16.0, Vector4(22, 12, 22, 12))
	jb.pressed.connect(_menu_join)
	row.add_child(jb)
	cv.add_child(row)
	var row2 := menu.hbox(10)
	btn_start_net = menu.button("Start the online race", "cta", 19.0, Vector4(20, 12, 20, 12))
	btn_start_net.pressed.connect(func():
		menu.close_modal()
		menu.visible = false
		_net_start())
	row2.add_child(btn_start_net)
	btn_leave_net = menu.button("Leave", "ghost", 16.0, Vector4(20, 12, 20, 12))
	btn_leave_net.pressed.connect(_menu_leave)
	row2.add_child(btn_leave_net)
	cv.add_child(row2)
	_menu_refresh("")
	return v


var net_addr_last := ""


## Settings: the PC version's options, laid out like the web's (tabs, a title and a note per row)
## web #settings: Graphics, Sound, Gameplay, Controls, Items & specials, More
func _settings_panel() -> Control:
	var v := menu.vbox(12)
	var tabs := [["graphics", "Graphics"], ["sound", "Sound"], ["gameplay", "Gameplay"], ["controls", "Controls"], ["items", "Items & specials"], ["more", "More"]]
	var th := menu.hbox(0)
	th.add_child(menu.seg("settab", tabs, set_tab, func(k):
		set_tab = String(k)
		menu.show_modal("set"), 14.0, 6.0))
	v.add_child(th)
	var sc := ScrollContainer.new()
	sc.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	sc.size_flags_vertical = Control.SIZE_EXPAND_FILL
	v.add_child(sc)
	var card := menu.panel(menu.glass(18.0, Vector4(16, 16, 16, 16)))
	card.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	sc.add_child(card)
	var c := menu.vbox(12)
	card.add_child(c)
	var on_off := [["1", "On"], ["0", "Off"]]
	match set_tab:
		"graphics":
			c.add_child(menu.section_label("Graphics"))
			c.add_child(_set_rows([
				["Quality", "Ultra: every racer and building in high detail, ambient occlusion, shadows across the whole view, 4x anti-aliasing and bloom. Balanced: lighter shadows and no ambient occlusion. Fast: the lightest, for older laptops.", "q", [["0", "Fast"], ["1", "Balanced"], ["2", "Ultra"]], str(quality)],
				["Shadows", "Real-time shadows from karts and scenery.", "shadows", on_off, "1" if shadows_on else "0"],
				["PC extras", "A step past the web game's Ultra: shadows reach more than twice as far and soften with distance like real sunlight, a little light bounces between nearby surfaces, and textures and reflections are sharper. Off matches the web game's Ultra exactly. Ultra only.", "pcx", on_off, "1" if pc_plus else "0"],
				["Look", "Vivid: a darker base tone with a stronger sun, deeper shadows and richer colour, so lit faces and light sources stand out. Classic: the softer, brighter balance. Applies from the next race.", "look", [["vivid", "Vivid"], ["classic", "Classic"]], look],
				["Ambient occlusion", "Soft contact shading in corners and crevices, computed every frame. The single most expensive effect: turn it off to run Ultra's detail at a higher frame rate.", "ao", on_off, "1" if ao_on else "0"],
				["Sharpening", "When the 3D view is drawn below screen size to hold the frame rate, a sharpening pass brings the detail back. Turn off if you prefer a softer picture.", "sharp", on_off, "1" if sharpen_on else "0"],
				["Scenery distance", "How far away trackside props are drawn.", "scenery", [["0", "Near"], ["1", "Normal"], ["2", "Far"]], str(scenery)],
				["Frame rate", "Auto runs at your monitor's full rate. 60 fps caps the game at a steady 60 for slower computers.", "fps", [["0", "Auto"], ["60", "60 fps"], ["120", "120 fps"]], str(fps_cap)],
				["Resolution", "Draw the 3D view smaller and scale it up, for a higher frame rate on slower graphics cards.", "res", [["1.0", "100%"], ["0.85", "85%"], ["0.67", "67%"]], str(snappedf(res_scale, 0.01)) if res_scale < 0.99 else "1.0"],
				["Full screen", "F11 switches too.", "fs", on_off, "1" if DisplayServer.window_get_mode() in [DisplayServer.WINDOW_MODE_FULLSCREEN, DisplayServer.WINDOW_MODE_EXCLUSIVE_FULLSCREEN] else "0"],
				["Frame counter", "Show frames per second during a race.", "fpsc", on_off, "1" if fps_counter else "0"],
			]))
		"sound":
			c.add_child(menu.section_label("Sound"))
			c.add_child(_set_rows([
				["Sound", "Engine, effects and music cues.", "snd", on_off, "1" if sfx_vol > 0.01 else "0"],
				["Volume", "How loud everything plays.", "vol", [["0.25", "25%"], ["0.5", "50%"], ["0.75", "75%"], ["1.0", "100%"]], str(snappedf(snd_level, 0.25))],
				["Music", "A different soundtrack on every track, four that take turns on the menus.", "music", on_off, "1" if music_on else "0"],
				["Music volume", "How loud the soundtrack sits under the engine and effects.", "mvol", [["0.25", "25%"], ["0.45", "45%"], ["0.7", "70%"], ["1.0", "100%"]], str(music_level)],
			]))
		"gameplay":
			c.add_child(menu.section_label("Gameplay"))
			c.add_child(_set_rows([
				["Kart stats", "Off makes every part cosmetic, so all karts drive the same. Applies from the next race.", "stats", on_off, "1" if KartBuilder.stats_on else "0"],
				["Speed units", "", "units", [["mph", "mph"], ["kmh", "km/h"]], "kmh" if hud.kmh else "mph"],
				["Camera", "Close sits right behind your driver.", "cam", [["close", "Close"], ["far", "Far"]], "far" if cam_far else "close"],
				["Camera distance", "How far behind your kart the camera sits.", "camd", [["80", "80%"], ["90", "90%"], ["100", "100%"], ["110", "110%"], ["120", "120%"]], str(cam_d)],
				["Camera shake", "Shake on bumps, boosts and hits.", "shake", on_off, "1" if shake_on else "0"],
				["Best-run ghost", "Race a see-through copy of your personal best.", "ghost", on_off, "1" if ghost_on else "0"],
			]))
		"controls":
			c.add_child(menu.section_label("Controls"))
			c.add_child(_controls_table())
		"items":
			c.add_child(menu.section_label("Items"))
			c.add_child(menu.para("Hold up to two items and use either slot. Items marked drop land on the road behind you; everything else fires or works forward. Click an item to switch it on or off for races; your choice is saved, and in a friends' race the host's choice is used. Locked items are rewards from Awards.", 13.0, Color("#c2a58c"), 720.0))
			c.add_child(_item_grid())
			var all_on := menu.button("Turn all items back on", "ghost", 14.0, Vector4(14, 8, 14, 8))
			all_on.pressed.connect(func():
				item_set.clear()
				_save_settings()
				menu.show_modal("set"))
			c.add_child(all_on)
			c.add_child(menu.section_label("Special abilities"))
			c.add_child(menu.para("Every driver has their own special. It recharges over 30 seconds; the ring around the button fills as it charges. Use it when it glows.", 13.0, Color("#c2a58c"), 720.0))
			var g := GridContainer.new()
			g.columns = 2
			g.add_theme_constant_override("h_separation", menu.zi(10))
			g.add_theme_constant_override("v_separation", menu.zi(10))
			for r in roster.get("racers", []):
				var A: Array = Race.ABIL.get(String(r["name"]).to_lower(), [])
				if A.is_empty():
					continue
				var pc := menu.panel(menu.glass(12.0, Vector4(12, 10, 12, 10)))
				pc.size_flags_horizontal = Control.SIZE_EXPAND_FILL
				var pv := menu.vbox(2)
				pc.add_child(pv)
				pv.add_child(menu.label("%s · %s" % [String(r["name"]), String(A[0])], menu.f_bold, 14.0, Color(String(A[2]))))
				pv.add_child(menu.para(String(A[1]), 12.0, Color("#c2a58c"), 340.0))
				g.add_child(pc)
			c.add_child(g)
		"more":
			c.add_child(menu.section_label("Reset"))
			var rr := menu.hbox(20)
			var rv := menu.vbox(2)
			rv.size_flags_horizontal = Control.SIZE_EXPAND_FILL
			rv.add_child(menu.label("Reset settings", menu.f_bold, 16.0, Color("#fff4dc")))
			rv.add_child(menu.para("Puts these settings back to how they started. Your progress and karts are kept.", 13.0, Color("#c2a58c"), 420.0))
			rr.add_child(rv)
			var rb := menu.button("Reset to defaults", "ghost", 14.0, Vector4(14, 8, 14, 8))
			rb.size_flags_vertical = Control.SIZE_SHRINK_CENTER
			rb.pressed.connect(func():
				_reset_settings()
				menu.show_modal("set"))
			rr.add_child(rb)
			c.add_child(rr)
	return v


## web .ctl: what does what, on the keyboard and on a controller
func _controls_table() -> Control:
	var rows := [["Steer", "\u2190 \u2192 or A / D", "Left stick or D-pad"], ["Accelerate", "Automatic", "Hold RT (right trigger)"], ["Brake / reverse", "Hold Space, \u2193 or S when slow", "Hold LT (left trigger) when slow"],
		["Drift / trick in the air", "Space, \u2193 or S", "LT (left trigger) \u00b7 GameCube R"], ["Use first item", "X or Enter", "A or LB \u00b7 GameCube A"], ["Use second item", "Z or Q", "B or RB \u00b7 GameCube B"],
		["Keep an item behind you", "Shift or B", "Hold the item button"], ["Throw the item you're holding", "X", "Let go of the item button"], ["Drop it behind you", "Shift or B again", "Stick down as you let go"],
		["Throw an item behind you", "Hold F, then the item key", "Pull the left stick back as you press the item, or hold X"], ["Special ability", "C or R", "Y"], ["Look back", "Hold F", "Hold X"], ["Pause", "P or Esc", "Start / Menu"]]
	var g := GridContainer.new()
	g.columns = 3
	g.add_theme_constant_override("h_separation", menu.zi(18))
	g.add_theme_constant_override("v_separation", menu.zi(8))
	for hcol in ["Action", "Keyboard", "Controller"]:
		g.add_child(menu.label(hcol.to_upper(), menu.f_bold, 11.0, Color("#c2a58c")))
	for r in rows:
		g.add_child(menu.label(String(r[0]), menu.f_bold, 14.0, Color("#fff4dc")))
		var k := menu.para(String(r[1]), 13.0, Color("#c2a58c"), 220.0)
		g.add_child(k)
		g.add_child(menu.para(String(r[2]), 13.0, Color("#c2a58c"), 260.0))
	var v := menu.vbox(10)
	v.add_child(g)
	v.add_child(menu.para("Xbox, PlayStation, Backbone and GameCube controllers work. In menus the stick or D-pad moves, A selects and B goes back. F11 switches full screen.", 13.0, Color("#c2a58c"), 720.0))
	return v


const ITEM_NAMES := {"chili": "Chili Boost", "pepperoni": "Pepperoni", "oil": "Olive Oil", "dough": "Dough Ball", "trio": "Pepperoni Trio", "garlic": "Garlic Shield", "flour": "Flour Bomb", "wheel": "Pizza Wheel", "rush": "Delivery Rush",
	"freezer": "Freezer Blast", "jalapeno": "Jalape\u00f1o Triple", "meatball": "Bowling Meatball", "torpedo": "Anchovy Torpedo", "shroom": "Spring Shroom", "magnet": "Pizza Magnet", "cutter": "Cutter Orbit", "sauce": "Sauce Splat",
	"heat": "Heat Wave", "bomb": "Calzone Bomb", "forks": "Fork Spikes", "ghost": "Ghost Pepper", "cannon": "Pizza Cannon", "twister": "Dough Twister", "swap": "Topping Swap", "boxes": "Box Barricade"}


## the item switches: every item's icon and name; on, off, or locked until its achievement
func _item_grid() -> Control:
	var g := GridContainer.new()
	g.columns = 5
	g.add_theme_constant_override("h_separation", menu.zi(8))
	g.add_theme_constant_override("v_separation", menu.zi(8))
	for it in ITEM_NAMES:
		var locked := Race.ITEM_AWARD.has(it) and not Ach.unlocked(String(Race.ITEM_AWARD[it]))
		var on: bool = not locked and item_set.get(it, true) != false
		var b := Button.new()
		b.custom_minimum_size = Vector2(menu.z(128), menu.z(46))
		b.focus_mode = Control.FOCUS_ALL
		b.mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
		var st := menu.glass(10.0, Vector4(6, 4, 6, 4))
		if on:
			st = menu.box([Color(0.97, 0.79, 0.28, 0.18), Color(0.88, 0.27, 0.17, 0.12)], 135.0, 10.0, Color(0.97, 0.79, 0.28, 0.55), 1.0, Vector4(6, 4, 6, 4))
		for sn in ["normal", "hover", "pressed", "focus", "disabled"]:
			b.add_theme_stylebox_override(sn, st)
		var h := menu.hbox(6)
		h.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
		h.offset_left = menu.z(6)
		h.mouse_filter = Control.MOUSE_FILTER_IGNORE
		b.add_child(h)
		var ic := TextureRect.new()
		ic.texture = load("res://assets/items/icon_%s.png" % it) if ResourceLoader.exists("res://assets/items/icon_%s.png" % it) else null
		ic.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		ic.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		ic.custom_minimum_size = Vector2(menu.z(30), menu.z(30))
		ic.size_flags_vertical = Control.SIZE_SHRINK_CENTER
		ic.modulate = Color(1, 1, 1, 1.0 if on else 0.4)
		h.add_child(ic)
		var nv := menu.vbox(0)
		nv.size_flags_vertical = Control.SIZE_SHRINK_CENTER
		var nl := menu.label(String(ITEM_NAMES[it]), menu.f_bold, 11.0, Color("#fff4dc") if on else Color("#c2a58c"))
		nv.add_child(nl)
		nv.add_child(menu.label("locked" if locked else ("drop" if it in Race.DROPS else ("on" if on else "off")), menu.f_med, 10.0, Color("#7fe07a") if on else Color("#c2a58c")))
		h.add_child(nv)
		var iid: String = it
		b.pressed.connect(func():
			if locked:
				return
			if item_set.get(iid, true) == false:
				item_set.erase(iid)
			else:
				item_set[iid] = false
			_save_settings()
			menu.show_modal("set"))
		g.add_child(b)
	return g


func _reset_settings() -> void:
	quality = 2
	shadows_on = true
	pc_plus = true
	look = "vivid"
	ao_on = true
	sharpen_on = true
	scenery = 1
	fps_cap = 0
	res_scale = 1.0
	fps_counter = false
	snd_level = 1.0
	sfx_vol = 1.0
	KartBuilder.stats_on = true
	hud.kmh = false
	cam_far = false
	cam_d = 100
	shake_on = true
	ghost_on = true
	music_on = true
	music_level = 0.45
	if music != null:
		music.on = true
		music.level = 0.45
	item_set.clear()
	_apply_quality()
	_apply_fps()
	_apply_res()
	_apply_volume()
	_save_settings()


var set_tab := "graphics"
var music: Music
var music_on := true
var music_level := 0.45
var shadows_on := true
var pc_plus := true       # Settings > PC extras
var look := "vivid"
var ao_on := true
var sharpen_on := true
var scenery := 1          # 0 near, 1 normal, 2 far
var fps_counter := false
var snd_level := 1.0
var cam_far := false
var cam_d := 100
var shake_on := true


var sfx_vol := 1.0


func _set_rows(rows: Array) -> Control:
	var v := menu.vbox(0)
	for r in rows:
		var h := menu.hbox(20)
		var tv := menu.vbox(2)
		tv.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		tv.add_child(menu.label(String(r[0]), menu.f_bold, 16.0, Color("#fff4dc")))
		tv.add_child(menu.para(String(r[1]), 13.0, Color("#c2a58c"), 420.0))
		h.add_child(tv)
		var key: String = r[2]
		var sg := menu.seg("set_" + key, r[3], String(r[4]), func(val): _apply_setting(key, String(val)), 15.0, 8.0)
		sg.custom_minimum_size.x = menu.z(330)
		sg.size_flags_vertical = Control.SIZE_SHRINK_CENTER
		h.add_child(sg)
		var mg := MarginContainer.new()
		mg.add_theme_constant_override("margin_top", menu.zi(10))
		mg.add_theme_constant_override("margin_bottom", menu.zi(10))
		mg.add_child(h)
		v.add_child(mg)
	return v


func _apply_setting(key: String, val: String) -> void:
	match key:
		"q":
			quality = int(val)
			_apply_quality()
		"fps":
			fps_cap = int(val)
			_apply_fps()
		"res":
			res_scale = float(val)
			_apply_res()
		"fs":
			var want := val == "1"
			var is_fs := DisplayServer.window_get_mode() in [DisplayServer.WINDOW_MODE_FULLSCREEN, DisplayServer.WINDOW_MODE_EXCLUSIVE_FULLSCREEN]
			if want != is_fs:
				_toggle_fullscreen()
		"snd":
			sfx_vol = snd_level if val == "1" else 0.0
			_apply_volume()
		"vol":
			snd_level = float(val)
			if sfx_vol > 0.01:
				sfx_vol = snd_level
			_apply_volume()
		"shadows":
			shadows_on = val == "1"
			_apply_quality()
		"pcx":
			pc_plus = val == "1"
			_apply_quality()
		"ao":
			ao_on = val == "1"
			_apply_quality()
		"sharp":
			sharpen_on = val == "1"
			_apply_res()
		"scenery":
			scenery = int(val)
		"look":
			look = val
		"fpsc":
			fps_counter = val == "1"
		"stats":
			KartBuilder.stats_on = val == "1"
			menu.stats_on = KartBuilder.stats_on
		"units":
			hud.kmh = val == "kmh"
		"cam":
			cam_far = val == "far"
		"camd":
			cam_d = int(val)
		"shake":
			shake_on = val == "1"
		"ghost":
			ghost_on = val == "1"
		"music":
			music_on = val == "1"
			if music != null:
				music.on = music_on
		"mvol":
			music_level = float(val)
			if music != null:
				music.level = music_level
	_save_settings()


func _apply_volume() -> void:
	AudioServer.set_bus_volume_db(0, linear_to_db(maxf(0.0001, sfx_vol)))
	AudioServer.set_bus_mute(0, sfx_vol < 0.01)


## Ultra: everything; High: no ambient occlusion, shorter shadows; Low: no shadows, glow or ambient occlusion
func _apply_quality() -> void:
	var vp := get_viewport()
	# PC extras (Ultra on a computer): a step past the web's Ultra, drawing only. Shadows reach more than twice
	# as far in four cascades, so the hills and buildings in the distance are shaded too and the ones up close
	# are crisper, with edges that soften the further a shadow falls from what casts it (like real sunlight);
	# a little light bounces between nearby surfaces; textures stay sharp at a glance along the road; and glossy
	# paint reflects a finer sky. Off is the web's Ultra exactly.
	var plus := pc_plus and quality >= 2 and not is_phone
	vp.anisotropic_filtering_level = Viewport.ANISOTROPY_16X if plus else Viewport.ANISOTROPY_8X
	if env == null or sun == null:
		return
	env.ssao_enabled = quality >= 2 and not is_phone and ao_on
	env.glow_enabled = quality >= 1 or not is_phone
	env.ssil_enabled = plus and ao_on
	env.ssil_radius = 6.0
	env.ssil_intensity = 0.55
	env.ssil_sharpness = 0.98
	env.ssil_normal_rejection = 1.0
	if env.sky != null:
		var rs := Sky.RADIANCE_SIZE_256 if plus else Sky.RADIANCE_SIZE_64
		if env.sky.radiance_size != rs:
			env.sky.radiance_size = rs
	sun.shadow_enabled = quality >= 1 and shadows_on
	if plus:
		sun.directional_shadow_mode = DirectionalLight3D.SHADOW_PARALLEL_4_SPLITS
		sun.directional_shadow_max_distance = 700.0
		sun.directional_shadow_split_1 = 0.05
		sun.directional_shadow_split_2 = 0.14
		sun.directional_shadow_split_3 = 0.38
		sun.directional_shadow_blend_splits = true
		sun.directional_shadow_fade_start = 0.8
		sun.light_angular_distance = 0.35
		sun.shadow_blur = 1.0
	else:
		sun.directional_shadow_mode = DirectionalLight3D.SHADOW_ORTHOGONAL
		sun.directional_shadow_max_distance = 300.0 if quality >= 2 else 200.0
		sun.directional_shadow_blend_splits = false
		sun.directional_shadow_fade_start = 0.9
		sun.light_angular_distance = 0.0
		sun.shadow_blur = 1.2
	vp.msaa_3d = Viewport.MSAA_4X if quality >= 2 else (Viewport.MSAA_2X if quality >= 1 else Viewport.MSAA_DISABLED)   # web Ultra: 4x


func _save_settings() -> void:
	var cf := ConfigFile.new()
	cf.set_value("gfx", "quality", quality)
	cf.set_value("gfx", "fps", fps_cap)
	cf.set_value("gfx", "res", res_scale)
	cf.set_value("snd", "vol", sfx_vol)
	cf.set_value("snd", "level", snd_level)
	for k2 in ["shadows_on", "pc_plus", "ao_on", "sharpen_on", "scenery", "fps_counter", "cam_far", "cam_d", "shake_on", "ghost_on", "item_set", "music_on", "music_level", "look"]:
		cf.set_value("opt", k2, get(k2))
	cf.set_value("opt", "stats_on", KartBuilder.stats_on)
	cf.set_value("opt", "kmh", hud.kmh if hud != null else false)
	for k in sel:
		cf.set_value("menu", k, sel[k])
	cf.set_value("menu", "map", map_id)
	cf.save("user://settings.cfg")


var settings_loaded := false
var opt_kmh := false


func _load_settings() -> void:
	var cf := ConfigFile.new()
	if cf.load("user://settings.cfg") != OK:
		return
	settings_loaded = true
	quality = int(cf.get_value("gfx", "quality", quality))
	fps_cap = int(cf.get_value("gfx", "fps", fps_cap))
	res_scale = float(cf.get_value("gfx", "res", res_scale))
	sfx_vol = float(cf.get_value("snd", "vol", 1.0))
	snd_level = float(cf.get_value("snd", "level", 1.0))
	for k2 in ["shadows_on", "pc_plus", "ao_on", "sharpen_on", "scenery", "fps_counter", "cam_far", "cam_d", "shake_on", "ghost_on", "item_set", "music_on", "music_level", "look"]:
		var vv = cf.get_value("opt", k2, get(k2))
		if typeof(vv) == typeof(get(k2)):
			set(k2, vv)
	KartBuilder.stats_on = bool(cf.get_value("opt", "stats_on", true))
	opt_kmh = bool(cf.get_value("opt", "kmh", false))
	for k in ["mode", "cls", "ri", "cup"]:
		sel[k] = cf.get_value("menu", k, sel[k])
	var bb = cf.get_value("menu", "build", {})
	if bb is Dictionary:
		sel["build"] = bb
	var mid := String(cf.get_value("menu", "map", ""))
	if mid != "" and map_id == "" and OS.get_environment("CR_MAP") == "":
		map_id = mid


func _menu_refresh(note := "") -> void:
	if btn_start_net != null and is_instance_valid(btn_start_net):
		btn_start_net.visible = net_role == "host"
		btn_start_net.text = "Start the online race (%d player%s)" % [net_peers.size() + 1, "" if net_peers.is_empty() else "s"]
	if btn_leave_net != null and is_instance_valid(btn_leave_net):
		btn_leave_net.visible = net_role != ""
	if lbl_menu == null or not is_instance_valid(lbl_menu):
		return
	var t := "Everyone plays on the PC version. One player hosts; the others type the host's address and join. The host picks the track (Choose driver, then the track) and starts the race here."
	if net_role == "host":
		t = "Hosting on %s. Friends on the PC version join with your address%s\n%d joined so far." % [String(_map_info(map_id).get("name", map_id)), net_addr, net_peers.size()]
	elif net_role == "client":
		t = "Connected. Waiting for the host to start the race." if net_ready else "Connecting..."
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
	net_addr_last = ip
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
	net_prefs.erase(id)
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
	# tell the host which driver and kart we picked
	_net_pref.rpc_id(1, int(sel["ri"]), _my_build())
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
	var pri := int(sel["ri"])
	var cfg := Race.new().make_cfg(roster, pri, peers, int(randi() & 0x7fffffff) + 1, String(sel["cls"]), _my_build(), net_prefs)
	cfg["map"] = map_id
	if String(sel.get("mode", "")) == "lss" and gp.is_empty():
		cfg["mode"] = "lss"
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


## a joined player's chosen driver and kart (checked: only small numbers and a livery id get through)
@rpc("any_peer", "call_remote", "reliable")
func _net_pref(ri: int, build: Dictionary) -> void:
	if net_role != "host":
		return
	var b := {}
	for key in ["b", "w", "g", "p"]:
		if build.has(key) and typeof(build[key]) in [TYPE_INT, TYPE_FLOAT]:
			b[key] = clampi(int(build[key]), 0, 255)
	if build.has("t") and typeof(build["t"]) == TYPE_STRING and String(build["t"]).length() < 40:
		b["t"] = String(build["t"])
	net_prefs[multiplayer.get_remote_sender_id()] = {"ri": clampi(ri, 0, 7), "build": b if b.size() >= 4 else {}}


@rpc("any_peer", "call_remote", "reliable")
func _net_item(it: String) -> void:
	if net_role != "host" or race == null or not it in ["fwd", "fwd2", "hold", "hold2", "ability"]:
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
			(1 if k.air else 0) | (2 if k.glide else 0) | (4 if k.big else 0) | (8 if k.finished else 0) | (16 if k.est else 0) | (32 if k.elim else 0),
			k.item, k.item2, String(k.held.get("it", "")), int(k.held.get("sl", 1)), k.sh_l, k.prog, k.idx, k.place, k.finish_time,
			k.loop_th if not k.loop.is_empty() else -1.0, k.roll, k.trick_t, k.trick_k, k.acc,
			k.shield, k.mz_h, k.ab_c, k.mega_t, k.flat_t, k.pesto_t, k.chili_t, k.olive_t, k.burn_t, k.ab_fx, k.ab_col.to_html(false),
			k.frozen, k.ghost_t, k.sauce_t, k.shrink_t, k.cannon_t, k.cut_t, k.cut_a, k.mag_t, race.karts.find(k.mag_tg) if k.mag_tg != null else -1, k.jal_n])
	var bx := PackedFloat32Array()
	for b in race.boxes:
		bx.append(float(b["r"]))
	var pr: Array = []
	for p in race.projectiles:
		pr.append([p["id"], p["type"], p["x"], p["y"], p["vx"], p["vy"], p["t"], p["t0"], p.get("ph", ""), p.get("pt", 0.0), p.get("dir", 0.0), p.get("spin", 0.0), p.get("age", 0.0), 1 if p.get("storm", false) else 0, 1 if p.get("landed", true) else 0, p.get("fuse", 0.0)])
	var hz: Array = []
	for h in race.hazards:
		hz.append([h["id"], h["x"], h["y"], h["t"], h["born"], "olive" if h.get("olive", false) else String(h.get("kind", ""))])
	_net_snap.rpc([state, cd, race.race_time, ks, bx, pr, hz, race.haz_snap()])


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
			for key in ["k", "a", "b", "by"]:
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
		k.elim = (fl & 32) != 0
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
		if q.size() > 40:
			k.shield = q[30]
			k.mz_h = q[31]
			k.ab_c = q[32]
			k.mega_t = q[33]
			k.flat_t = q[34]
			k.pesto_t = q[35]
			k.chili_t = q[36]
			k.olive_t = q[37]
			k.burn_t = q[38]
			k.ab_fx = q[39]
			k.ab_col = Color(String(q[40]))
		if q.size() > 50:
			k.frozen = q[41]
			k.ghost_t = q[42]
			k.sauce_t = q[43]
			k.shrink_t = q[44]
			k.cannon_t = q[45]
			k.cut_t = q[46]
			k.cut_a = q[47]
			k.mag_t = q[48]
			var mi2 := int(q[49])
			k.mag_tg = race.karts[mi2] if mi2 >= 0 and mi2 < race.karts.size() else null
			k.jal_n = q[50]
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
			"vx": q2[4], "vy": q2[5], "t": q2[6], "t0": q2[7], "ph": q2[8], "pt": q2[9], "dir": q2[10], "spin": q2[11], "age": q2[12], "storm": q2.size() > 13 and int(q2[13]) == 1, "landed": q2.size() <= 14 or int(q2[14]) == 1, "fuse": float(q2[15]) if q2.size() > 15 else 0.0, "owner": null, "target": null})
	race.hazards.clear()
	for q3 in s[6]:
		var hk := String(q3[5]) if q3.size() > 5 else ""
		var hd := {"id": q3[0], "x": q3[1], "y": q3[2], "t": q3[3], "born": q3[4]}
		if hk == "olive":
			hd["olive"] = true
		elif hk != "":
			hd["kind"] = hk
		race.hazards.append(hd)
	if s.size() > 7:
		race.haz_unsnap(s[7])
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
	if haz_lib != null:
		haz_lib.free()
		haz_lib = null
	if upnp_thread != null:
		upnp_thread.wait_to_finish()


func _enter_tree() -> void:
	cam = Camera3D.new()
	cam.near = 0.5
	cam.far = 14000.0
	cam.fov = 70.0
	add_child(cam)
	cam.current = true

