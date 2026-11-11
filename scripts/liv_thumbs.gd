class_name LivThumbs
extends Node
## The garage's livery pictures: your own kart (body, wheels, driver) drawn in each livery, three-quarter view from the
## front, in the garage's studio light, on a clear background. One small off-screen view repaints the kart and takes a
## picture per livery, a couple per frame, in the order the list shows them; pictures are kept for the session, so
## picking a livery or coming back to the list shows them at once.

const W := 400
const H := 230

var _vp: SubViewport
var _turn: Node3D
var _kart: Node3D
var _cam: Camera3D
var _kkey := ""            # the kart in the view: body | wheels | glider | driver
var _cache := {}           # key -> ImageTexture
var _queue: Array = []     # [key, spec, ri, callback]
var _busy := false
var px := 1.0              # screen pixels per layout unit (2 on a 1440p screen)


func _ready() -> void:
	_vp = SubViewport.new()
	_vp.own_world_3d = true
	_vp.transparent_bg = true
	_vp.msaa_3d = Viewport.MSAA_4X
	_vp.render_target_update_mode = SubViewport.UPDATE_DISABLED
	_vp.size = Vector2i(W, H)
	add_child(_vp)
	var w3 := Node3D.new()
	_vp.add_child(w3)
	# the garage's stage light (menu.gd _garage_scene), without the floor
	var env := WorldEnvironment.new()
	var e := Environment.new()
	e.background_mode = Environment.BG_CLEAR_COLOR
	var sky := Sky.new()
	var skm := ShaderMaterial.new()
	skm.shader = load("res://shaders/studio_sky.gdshader")
	skm.set_shader_parameter("top_col", Color("#fff1d6"))
	skm.set_shader_parameter("hor_col", Color("#ffd9a8"))
	skm.set_shader_parameter("bot_col", Color("#6b3a1e"))
	sky.sky_material = skm
	sky.radiance_size = Sky.RADIANCE_SIZE_128
	e.sky = sky
	e.ambient_light_source = Environment.AMBIENT_SOURCE_SKY
	e.ambient_light_energy = 0.6
	e.reflected_light_source = Environment.REFLECTION_SOURCE_SKY
	e.tonemap_mode = Environment.TONE_MAPPER_ACES
	e.tonemap_white = 16.0
	e.tonemap_exposure = 1.05 * (1.0 / 0.6) / 1.8
	env.environment = e
	w3.add_child(env)
	var sun := DirectionalLight3D.new()
	sun.light_energy = 2.4
	sun.light_color = Color("#fff0d8")
	w3.add_child(sun)
	sun.look_at_from_position(Vector3(10, 22, 12), Vector3.ZERO, Vector3.UP)
	_cam = Camera3D.new()
	_cam.fov = 26.0
	w3.add_child(_cam)
	_turn = Node3D.new()
	w3.add_child(_turn)


func set_px(p: float) -> void:
	var s := clampf(p, 1.0, 2.0)
	if absf(s - px) > 0.01:
		px = s
		_cache.clear()
	_vp.size = Vector2i(int(W * px / 2.0), int(H * px / 2.0))   # W x H is the 1440p size


static func key_of(spec: Dictionary, ri: int, id: String) -> String:
	return "%d|%d|%d|%d|%d|%s" % [int(spec.get("b", 0)), int(spec.get("w", 0)), int(spec.get("g", 0)), int(spec.get("p", 0)), ri, id]


## a picture of `spec` (with livery `id`, "" for its plain paint) for driver `ri`: at once if it's been taken,
## otherwise `cb` gets it when it's ready
func want(spec: Dictionary, ri: int, id: String, cb: Callable) -> void:
	var k := key_of(spec, ri, id)
	if _cache.has(k):
		cb.call(_cache[k])
		return
	var s := spec.duplicate()
	s["t"] = id
	_queue.append([k, s, ri, cb])


## the list was rebuilt: forget the old list's requests (their cards are gone)
func clear_queue() -> void:
	_queue.clear()


func _process(_dt: float) -> void:
	if _busy or _queue.is_empty():
		return
	_shoot()


func _shoot() -> void:
	_busy = true
	var n := 0
	while not _queue.is_empty() and n < 2:
		var q: Array = _queue.pop_front()
		var k := String(q[0])
		if _cache.has(k):
			(q[3] as Callable).call(_cache[k])
			continue
		var spec: Dictionary = q[1]
		var ri := int(q[2])
		if not _pose(spec, ri):
			continue
		_vp.render_target_update_mode = SubViewport.UPDATE_ONCE
		await RenderingServer.frame_post_draw
		if not is_instance_valid(self):
			return
		var img := _vp.get_texture().get_image()
		if img == null or img.is_empty():
			continue
		img.generate_mipmaps()
		var tex := ImageTexture.create_from_image(img)
		_cache[k] = tex
		var cb: Callable = q[3]
		if cb.is_valid():
			cb.call(tex)
		n += 1
	_busy = false


## the kart for this spec in the view, painted in its livery and framed
func _pose(spec: Dictionary, ri: int) -> bool:
	var kk := "%d|%d|%d|%d" % [int(spec.get("b", 0)), int(spec.get("w", 0)), int(spec.get("g", 0)), ri]
	if kk != _kkey or _kart == null or not is_instance_valid(_kart):
		if _kart != null and is_instance_valid(_kart):
			_kart.queue_free()
		_kart = null
		var built := KartBuilder.build(spec, ri)
		if built.is_empty():
			return false
		_kart = built["node"]
		_turn.add_child(_kart)
		var sc := float((built["meta"] as Dictionary).get("scale", 1.76)) / 1.76
		_turn.scale = Vector3.ONE * sc
		_turn.rotation.y = 0.62
		_kkey = kk
		_frame()
	else:
		KartBuilder.repaint(_kart, spec, ri)
	return true


func _frame() -> void:
	# the kart's box, measured square to the kart, then fitted into the picture as the camera sees it turned
	var rot := _turn.rotation.y
	_turn.rotation.y = 0.0
	var bb := AABB()
	var first := true
	for mi in _kart.find_children("*", "MeshInstance3D", true, false):
		var m := mi as MeshInstance3D
		if not m.is_visible_in_tree() or m.mesh == null:
			continue
		var ab := (_turn.transform * _kart.transform * Menu._rel_xf(m, _kart)) * m.mesh.get_aabb()
		bb = ab if first else bb.merge(ab)
		first = false
	_turn.rotation.y = rot
	if first:
		return
	var turn := Basis(Vector3.UP, rot)
	var c := turn * bb.get_center()
	var el := 0.3
	var f := Vector3(cos(el) * 0.756, sin(el), cos(el) * 0.654).normalized()   # towards the camera
	var r := Vector3.UP.cross(f).normalized()
	var u := f.cross(r)
	var tv := tan(deg_to_rad(_cam.fov * 0.5)) * 0.9
	var th := tv * float(W) / float(H)
	var d := 1.0
	for i in 8:
		var p := turn * bb.get_endpoint(i) - c
		var z := p.dot(f)
		d = maxf(d, z + absf(p.dot(r)) / th)
		d = maxf(d, z + absf(p.dot(u)) / tv)
	_cam.near = maxf(0.2, d * 0.25)
	_cam.far = d * 4.0
	_cam.look_at_from_position(c + f * d, c, Vector3.UP)
