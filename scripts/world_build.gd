extends RefCounted
## A track's world built away from the running game: on another thread, on nodes that are not in the scene tree.
## Sandbox travels from place to place without stopping (the owner: "the game will never freeze or stop to load it will be
## one fluid drive through the tunnel right out to the other side"), so the next place cannot be built the way a race's
## track is (main.gd load_map, which blocks for one to four seconds). This does the same work, in the same order:
## the track's data, its sky, lights and scenery, the finished models, the moving hazards' models, and for Sandbox the
## Race, the Sandbox object (its columns decoded) and its drawing. Everything goes into this object's own fields. The
## main thread takes them over when the kart is ready to come out (main.gd, "Sandbox: travelling without a stop").
##
## THE RULES OF THE THREAD (keep them when changing this file):
##   - nothing here reads or writes a member of main.gd that the running game uses. What the build needs to know of
##     the game's settings is copied into `opt` before the thread starts;
##   - no node made here is in the tree, so nothing may ask a node for global_transform, get_tree() or get_viewport()
##     (scripts/xf.gd answers "where is this node" without the tree; the Hd* helpers use it);
##   - nothing is read back from the graphics card. Reading a texture's or a mesh's data back waits for the main thread
##     to reach the renderer, a whole frame each time. The one place that did (making the textures' smaller copies) is
##     done here on the picture as it is decoded (MipExt), before it ever becomes a texture.
## main.gd's load_map / _build_world / _prepare_track are the ordinary, blocking form of the same work and are not
## changed by this: an ordinary race loads exactly as it did. A change to how a world is built belongs in BOTH.
## Loaded by its path (no class name: a fresh checkout has no class list yet).

const Xf := preload("res://scripts/xf.gd")
const Sandbox := preload("res://scripts/sandbox.gd")
const SandboxView := preload("res://scripts/sandbox_view.gd")

# ---- what is asked for (set on the main thread before start())
var id := ""                 # the map
var info := {}               # its card from main.maps (dir, name, sb ...)
var opt := {}                # the game's settings the build depends on: look, is_phone, hd, quality
var maps: Array = []         # the list of maps (the signs' names)
var roster := {}             # for the Race
var pri := 1                 # the player's racer
var cls := "medium"
var build := {}              # the player's kart
var song := ""               # the place's song, read here so the main thread finds it already loaded
var want_sb := true

# ---- what comes out (read by the main thread only after `done`)
var T: TrackData
var world: Node3D
var track: Node3D            # the exported cells' parent, a child of `world`
var pending: Array = []      # [[parent, node]]: the world's pieces, taken out of it again at the end of the build so the
                             # main thread can bring them into the tree a few at a time (a toy room's mirror picture last)
var env: Environment
var sun: DirectionalLight3D
var rim: DirectionalLight3D
var cam_far := 14000.0
var toy_room := AABB()
var toy_room_on := false
var water_mats: Array = []
var cull_list: Array = []
var haz_lib: Node3D
var grade := {}              # sat, con, tint, vig for the post material
var race: Race
var sb_view: Node3D
var music_stream = null
var ok := false
var err := ""
var ms := {}                 # how long each part took (ms), for the log
var phase := ""              # what the thread is doing now (for the log of a long frame)
var at := ""

var _thread: Thread
var _done := false           # (written once by the thread at its very end, read by the main thread)
var _cancel := false
var _rush := false           # the main thread is waiting in join(): no more pacing by frames (none are being drawn)
var _mx := Mutex.new()

static var _ext = null         # the MipExt, registered once


## A picture of a track's model, decoded with its smaller copies (mipmaps) made at once. Godot's own loader makes a
## texture without them and main.gd's _load_gltf then reads each texture back from the graphics card to add them: on
## this thread that would wait a frame for every picture.
class MipExt extends GLTFDocumentExtension:
	var thread_id := -1   # the thread whose pictures get their smaller copies as they are decoded (-1: nobody's)
	var images: Array = []   # the pictures decoded for the model being loaded, in the model's own order

	func _parse_image_data(_state: GLTFState, data: PackedByteArray, mime: String, ret: Image) -> Error:
		if OS.get_thread_caller_id() != thread_id:
			return OK   # (any other load: left to Godot's own decoder, as before)
		var e := ERR_FILE_UNRECOGNIZED
		if mime == "image/png":
			e = ret.load_png_from_buffer(data)
		elif mime == "image/jpeg":
			e = ret.load_jpg_from_buffer(data)
		if e == OK and not ret.is_empty() and not ret.is_compressed():
			# (the graphics card takes no three-byte pictures: turned into four-byte ones here, not by the main thread as
			#  each one is handed over)
			if ret.get_format() == Image.FORMAT_RGB8:
				ret.convert(Image.FORMAT_RGBA8)
			if not ret.has_mipmaps():
				ret.generate_mipmaps()
			images.append(ret)
		return OK


func start() -> void:
	if _ext == null:
		_ext = MipExt.new()
		GLTFDocument.register_gltf_document_extension(_ext, true)
	_thread = Thread.new()
	_thread.start(_run)


func done() -> bool:
	_mx.lock()
	var d := _done
	_mx.unlock()
	return d


func cancel() -> void:
	_mx.lock()
	_cancel = true
	_mx.unlock()


func _cancelled() -> bool:
	_mx.lock()
	var c := _cancel
	_mx.unlock()
	return c


## waits for the thread to end. The thread may itself be waiting for the main thread to reach the renderer (a mesh's
## points read back by an Hd* helper): the renderer is flushed here while waiting, or the two would wait for each other.
func join() -> void:
	if _thread == null:
		return
	_mx.lock()
	_rush = true
	_mx.unlock()
	while _thread.is_alive() and not done():
		RenderingServer.force_sync()
		OS.delay_msec(1)
	_thread.wait_to_finish()
	_thread = null


func joined() -> bool:
	return _thread == null


## frees what was built and never used (a cancelled journey)
func discard() -> void:
	for n in [world, haz_lib, sb_view, track]:
		if n != null and is_instance_valid(n) and not (n as Node).is_inside_tree() and (n as Node).get_parent() == null:
			(n as Node).free()
	world = null
	haz_lib = null
	sb_view = null
	track = null
	race = null


func _run() -> void:
	_ext.thread_id = OS.get_thread_caller_id()
	# (nodes made here are in no tree: Godot's "only from the main thread" checks are for nodes that are)
	Thread.set_thread_safety_checks_enabled(false)
	var t0 := Time.get_ticks_msec()
	var good := _build()
	ms["total"] = Time.get_ticks_msec() - t0
	_ext.thread_id = -1
	Xf.forget()
	_mx.lock()
	ok = good and not _cancel
	_done = true
	_mx.unlock()


static func _hex(s, fallback: Color) -> Color:
	if typeof(s) == TYPE_STRING and String(s).begins_with("#"):
		return Color.html(s)
	return fallback


## (main.gd _aces_inv: the HDR colour that comes out of Godot's ACES as `t`)
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
		var a := 1.0 - y * C
		var b := A - y * D
		var c := -(B + y * E)
		u[i] = (-b + sqrt(maxf(0.0, b * b - 4.0 * a * c))) / (2.0 * a)
	var x := rrt.inverse() * u / bias
	return Vector3(maxf(0.0, x.x), maxf(0.0, x.y), maxf(0.0, x.z))


## a glTF file from disk (main.gd _load_gltf, without its reading back of every texture: see MipExt)
func _gltf(path: String) -> Node3D:
	if path.begins_with("res://"):
		var ps: PackedScene = load(path) if ResourceLoader.exists(path) else null
		return ps.instantiate() as Node3D if ps != null else null
	if not FileAccess.file_exists(path):
		return null
	var doc := GLTFDocument.new()
	var st := GLTFState.new()
	var e := OK
	_ext.images = []
	if path.ends_with(".gltf"):
		var txt := FileAccess.get_file_as_string(path)
		if txt.find("\"mimeType\"") < 0:
			var re := RegEx.new()
			re.compile("\"uri\":\"([^\"]+\\.(jpg|png))\"")
			txt = re.sub(txt, "\"uri\":\"$1\",\"mimeType\":\"image/$2\"", true).replace("image/jpg", "image/jpeg")
		e = doc.append_from_buffer(txt.to_utf8_buffer(), path.get_base_dir() + "/", st)
	else:
		e = doc.append_from_file(path, st)
	if e != OK:
		return null
	# The model's meshes are handed to the graphics card here, a few megabytes a frame. Left to generate_scene they are
	# all made in one go, and the main thread, which does the handing over, spends one long frame on it (50 ms and more
	# for a room). generate_scene then finds them made. What the loader still has in memory of each mesh is noted for
	# the Hd* helpers on the way (scripts/xf.gd): they then need nothing read back from the graphics card.
	var sent := 0
	for gm in st.get_meshes():
		var im: ImporterMesh = (gm as GLTFMesh).mesh
		if im == null:
			continue
		var sf: Array = []
		for i in im.get_surface_count():
			var arr := im.get_surface_arrays(i)
			sf.append(arr)
			var vx = arr[Mesh.ARRAY_VERTEX]
			var ix = arr[Mesh.ARRAY_INDEX]
			sent += (vx.size() * 36 if vx != null else 0) + (ix.size() * 4 if ix != null else 0)
		Xf.note_mesh(im.get_mesh(), sf)
		if sent > 3000000:
			sent = 0
			_next_frame()
	var n := doc.generate_scene(st) as Node3D
	# (the pictures, matched to the textures made of them: the same order, and the same size or it is not a match)
	var pics: Array = _ext.images
	var pi := 0
	for tx in st.get_images():
		if tx == null or pi >= pics.size():
			continue
		var im0: Image = pics[pi]
		if (tx as Texture2D).get_width() == im0.get_width() and (tx as Texture2D).get_height() == im0.get_height():
			Xf.note_image(tx, im0)
			pi += 1
	_ext.images = []
	return n


## waits until the game has drawn another frame (so that what this thread has just handed to the renderer is not
## added to what it hands over next), unless the main thread is itself waiting for this one to end
func _next_frame() -> void:
	var f0 := Engine.get_process_frames()
	while Engine.get_process_frames() == f0 and not _hurry():
		OS.delay_msec(1)


func _hurry() -> bool:
	_mx.lock()
	var h := _rush or _cancel
	_mx.unlock()
	return h


## (main.gd _use_vertex_colours. A material that is changed like this gets another shader, and it is the main thread
##  that works a material's shader out, for every changed material at once, before its next frame: a few at a time here)
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
				if n % 4 == 0:
					_next_frame()
	return n


## (main.gd _prepare_track, into this object's own lists)
func _prepare_track(root: Node) -> void:
	_use_vertex_colours(root)
	for n in root.find_children("*", "MeshInstance3D", true, false):
		var mi := n as MeshInstance3D
		var nm := String(mi.name)
		if nm.find("noshadow") >= 0:
			mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		var gx := Xf.g(mi)
		var far := (gx * mi.get_aabb()).get_center()
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
			var bb := gx * mi.get_aabb()
			cull_list.append({"node": mi, "rect": Rect2(bb.position.x, bb.position.z, bb.size.x, bb.size.z), "vis": true})


func _build() -> bool:
	var dir: String = info["dir"]
	var t := Time.get_ticks_msec()
	T = TrackData.load_from(dir.path_join(id + ".json"))
	ms["json"] = Time.get_ticks_msec() - t
	if T == null:
		err = "the track's data could not be read"
		return false
	if want_sb and T.sb.is_empty():
		err = "the place has no Sandbox block"
		return false
	if _cancelled():
		return false
	t = Time.get_ticks_msec()
	_world()
	ms["world"] = Time.get_ticks_msec() - t
	if _cancelled():
		return false
	# Everything of this place that is drawn goes on its own layer (the second): until the kart is nearly out of the
	# tunnel the game's camera does not look at that layer (main.gd), so nothing of a place that happens to stand where
	# the tunnel runs can show inside it; a small second camera does look at it, so that it has all been drawn once.
	for gi in world.find_children("*", "GeometryInstance3D", true, false):
		(gi as GeometryInstance3D).layers = 2
	# the world's pieces, apart: its sky and lights go into the tree first, then these, a few a frame
	var late: Array = []
	if track != null:
		# (a loaded model's nodes all name its root as their owner; taken out and put back one by one that only earns
		#  a warning each: nothing here goes by owner)
		for n in track.find_children("*", "", true, false):
			(n as Node).owner = null
		for c in track.get_children():
			track.remove_child(c)
			pending.append([track, c])
	for c in world.get_children():
		if c is WorldEnvironment or c == sun or c == rim or c == track:
			continue
		world.remove_child(c)
		if c is ReflectionProbe:
			late.append([world, c])   # (it photographs the room as it comes in: the room must be there)
		else:
			pending.append([world, c])
	pending.append_array(late)
	t = Time.get_ticks_msec()
	# (a place with no moving hazards has an empty model file, which the loader reports as an error: not read at all)
	var hp := dir.path_join(id + "_haz.glb")
	var hf := FileAccess.open(hp, FileAccess.READ) if FileAccess.file_exists(hp) else null
	haz_lib = _gltf(hp) if hf != null and hf.get_length() > 400 else null
	if haz_lib != null:
		_use_vertex_colours(haz_lib)
	if song != "" and ResourceLoader.exists(song):
		music_stream = load(song)
	ms["haz"] = Time.get_ticks_msec() - t
	if _cancelled():
		return false
	if want_sb:
		# the Race, the Sandbox object and what Sandbox draws, as main.gd _start_race makes them for a place
		t = Time.get_ticks_msec()
		race = Race.new()
		race.sb_want = true
		race.sb_defer = true      # (the save is the main thread's: the Sandbox object reads it when it is taken over)
		race.setup(T, roster, pri, 0, cls, build)
		if race.sb == null:
			err = "Sandbox could not be set up there"
			return false
		sb_view = SandboxView.new()
		sb_view.name = "SandboxView"
		sb_view.setup(race.sb, T, maps)
		ms["race"] = Time.get_ticks_msec() - t
	return true


## notes what the thread is starting on, and how long the part before it took (for the log)
var _ph_t := 0
func _ph(name: String) -> void:
	var now := Time.get_ticks_msec()
	if phase != "" and _ph_t > 0:
		ms[phase] = int(ms.get(phase, 0)) + now - _ph_t
	phase = name
	_ph_t = now


## (main.gd _build_world, into this object's own fields; what it sets on the camera, the post material and the
##  viewport is left for the main thread: cam_far, grade, and main.gd _apply_quality at the takeover)
func _world() -> void:
	var look := String(opt.get("look", "vivid"))
	var is_phone := bool(opt.get("is_phone", false))
	var quality := int(opt.get("quality", 2))
	var L: Dictionary = T.light
	var S: Dictionary = T.sky
	world = Node3D.new()
	world.name = "World"
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
	cam_far = 26000.0 if T.toy else 14000.0
	if T.toy and T.toyenv == null and typeof(L.get("bg")) == TYPE_STRING:
		var skyc := _hex(L.get("bg"), Color(0.66, 0.8, 0.95))
		sm.set_shader_parameter("top_col", skyc.darkened(0.2))
		sm.set_shader_parameter("hor_col", skyc.lightened(0.4))
		sm.set_shader_parameter("bot_col", skyc.lightened(0.25))
		sm.set_shader_parameter("sun_col", Color(1, 0.96, 0.86))
	sky.sky_material = sm
	# (the sky's light for glossy paint is worked out when the sky is first drawn. All at once that is a long frame, so
	#  here it is spread over several (the same quality), and it is made at the size main.gd _apply_quality will ask for,
	#  so that asking does not start it again)
	sky.radiance_size = Sky.RADIANCE_SIZE_256 if bool(opt.get("plus", false)) else Sky.RADIANCE_SIZE_64
	sky.process_mode = Sky.PROCESS_MODE_INCREMENTAL
	env.sky = sky
	env.ambient_light_source = Environment.AMBIENT_SOURCE_SKY
	env.ambient_light_sky_contribution = 0.25
	env.ambient_light_color = _hex(L.get("hemiSky"), Color(1, 0.89, 0.77))
	if T.toy:
		env.ambient_light_color = env.ambient_light_color.lerp(_hex(L.get("hemiGround"), Color(0.7, 0.58, 0.48)), 0.45)
	var night := T.theme == "night"
	var vivid := look != "classic"
	env.ambient_light_energy = float(L.get("hemiI", 0.52)) * (1.25 if T.toy else ((0.88 if night else 0.7) if vivid else 1.0))
	env.reflected_light_source = Environment.REFLECTION_SOURCE_SKY
	env.tonemap_mode = Environment.TONE_MAPPER_ACES
	env.tonemap_white = 16.0
	env.tonemap_exposure = float(L.get("exposure", 0.92)) * ((1.0 if night or T.toy else 0.96) if vivid else 1.0) * (1.0 / 0.6) / 1.8
	env.ssao_enabled = not is_phone
	env.ssao_radius = 2.5
	env.ssao_intensity = 1.6
	env.ssao_light_affect = 0.6
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

	sun = DirectionalLight3D.new()
	var sd: Array = L.get("sunDir", [0.84, 0.47, 0.26])
	var to_sun := Vector3(sd[0], sd[1], sd[2]).normalized()
	world.add_child(sun)
	sun.look_at_from_position(to_sun * 100.0, Vector3.ZERO, Vector3.UP)
	sun.light_color = _hex(L.get("sunColor"), Color(1, 0.84, 0.66))
	sun.light_energy = float(L.get("sunI", 3.25)) * (0.5 if T.toy else ((1.12 if T.theme == "night" else 1.25) if look != "classic" else 1.0))
	sun.shadow_enabled = true
	sun.directional_shadow_mode = DirectionalLight3D.SHADOW_ORTHOGONAL
	sun.directional_shadow_max_distance = 300.0
	sun.directional_shadow_fade_start = 0.9
	sun.shadow_bias = 0.04
	sun.shadow_normal_bias = 1.0
	sun.shadow_blur = 1.2
	rim = DirectionalLight3D.new()
	rim.light_color = _hex(T.rim.get("c"), Color("#a8ccff"))
	rim.light_energy = float(T.rim.get("i", 0.55)) * 1.25
	rim.shadow_enabled = false
	world.add_child(rim)
	var rd := Vector3(to_sun.x * 400.0, -300.0, to_sun.z * 400.0).normalized()
	rim.look_at_from_position(Vector3.ZERO - rd, Vector3.ZERO, Vector3.UP)

	var dir: String = info["dir"]
	var t := Time.get_ticks_msec()
	_ph("gltf")
	track = _gltf(dir.path_join(id + ".gltf"))
	ms["gltf"] = Time.get_ticks_msec() - t
	t = Time.get_ticks_msec()
	if track != null:
		world.add_child(track)
		_ph("prepare")
		_prepare_track(track)
	if track != null and T.toy:
		_ph("toy")
		HdToy.upgrade(track)
		if track.has_meta("toy_room"):
			toy_room = track.get_meta("toy_room")
			toy_room_on = true
			HdToy.add_probe(world, track, env.ambient_light_color, env.ambient_light_energy, T.toyenv)
	if track != null and T.theme == "night":
		_ph("neon")
		HdNeon.upgrade(track)
	var hd := bool(opt.get("hd", true)) and quality >= 1 and OS.get_environment("CR_HD") != "0"
	if track != null and hd:
		_ph("ground")
		HdGround.upgrade(track, dir.path_join(id + "_hd.json"))
		_ph("water")
		HdWater.upgrade(track, T.theme, T)
		_ph("surface")
		HdSurface.upgrade(track)
		_ph("set")
		HdSet.upgrade(track, T)
		_ph("mount")
		HdMount.upgrade(track, 2 if quality >= 2 else 1, T.theme)
		if T.theme == "kitchen" and not T.toy:
			_ph("kitchen")
			HdKitchen.upgrade(track)
			_ph("fire")
			HdFire.upgrade(track)
	_ph("balls")
	WallBalls.build(world, T)
	_ph("props")
	if not T.props.is_empty():
		var pr := Props.new()
		pr.name = "Props"
		world.add_child(pr)
		pr.build(T.props, 2 if hd else 0)
	ms["finish"] = Time.get_ticks_msec() - t
	_ph("rest")
	var G: Dictionary = T.grade
	var tn: Array = G.get("tint", [1.0, 1.0, 1.0])
	var cl := look == "classic"
	grade = {"sat": float(G.get("sat", 1.07)) - ((0.02 if night else 0.035) if cl else 0.0), "con": float(G.get("con", 1.04)) - ((0.03 if night else 0.06) if cl else 0.0),
		"tint": Vector3(float(tn[0]), float(tn[1]), float(tn[2])), "vig": float(G.get("vig", 0.16))}
	env.glow_intensity = float(G.get("bloom", 0.3))
	env.glow_hdr_threshold = 1.6 * float(G.get("thr", 0.94)) / 0.94
