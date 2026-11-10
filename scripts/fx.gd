class_name Fx
extends Node3D
## The web game's effects, ported one for one: the two particle pools (FXA: glowing sparks, added
## on top; FXN: soft smoke and dust), the expanding rings, and burst(). Same parameters as the web
## calls (positions in world space: x, height, z), same textures (radial gradients), same sizing:
## a particle's size is its diameter in world units, capped on screen like the web's point sprites.

const RINGS := 12

class Pool:
	var mm: MultiMesh
	var node: MultiMeshInstance3D
	var max_n := 0
	var next := 0
	# per particle: life, max life, pos, vel, s0, s1, colour, gravity, drag
	var l := PackedFloat32Array()
	var ml := PackedFloat32Array()
	var p := PackedVector3Array()
	var v := PackedVector3Array()
	var s0 := PackedFloat32Array()
	var s1 := PackedFloat32Array()
	var c := PackedColorArray()
	var gr := PackedFloat32Array()
	var dr := PackedFloat32Array()

	func _init(n: int, mat: ShaderMaterial, parent: Node3D) -> void:
		max_n = n
		mm = MultiMesh.new()
		mm.transform_format = MultiMesh.TRANSFORM_3D
		mm.use_colors = true
		var q := QuadMesh.new()
		q.size = Vector2(1, 1)
		mm.mesh = q
		mm.instance_count = n
		mm.visible_instance_count = 0
		node = MultiMeshInstance3D.new()
		node.multimesh = mm
		node.material_override = mat
		node.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		node.extra_cull_margin = 16384.0
		node.custom_aabb = AABB(Vector3(-1e5, -1e5, -1e5), Vector3(2e5, 2e5, 2e5))
		parent.add_child(node)
		for arr in [l, ml, s0, s1, gr, dr]:
			arr.resize(n)
		p.resize(n)
		v.resize(n)
		c.resize(n)

	func spawn(x: float, y: float, z: float, vx: float, vy: float, vz: float, col: Color, a: float, b: float, life: float, grav: float, drag: float) -> void:
		var i := next
		next = (next + 1) % max_n
		p[i] = Vector3(x, y, z)
		v[i] = Vector3(vx, vy, vz)
		c[i] = col
		s0[i] = a
		s1[i] = b
		l[i] = life
		ml[i] = life
		gr[i] = grav
		dr[i] = drag

	func clear() -> void:
		for i in max_n:
			l[i] = 0.0

	func update(dt: float) -> void:
		var n := 0
		for i in max_n:
			if l[i] <= 0.0:
				continue
			l[i] -= dt
			if l[i] <= 0.0:
				continue
			var k := maxf(0.0, 1.0 - dr[i] * dt)
			var vv := v[i]
			vv.x *= k
			vv.y = vv.y * k - gr[i] * dt
			vv.z *= k
			v[i] = vv
			p[i] += vv * dt
			var f := maxf(0.0, l[i] / ml[i])
			var s := s1[i] + (s0[i] - s1[i]) * f
			var col := c[i]
			col.a = minf(1.0, f * 1.6)
			mm.set_instance_transform(n, Transform3D(Basis.from_scale(Vector3(s, s, s)), p[i]))
			mm.set_instance_color(n, col)
			n += 1
		mm.visible_instance_count = n


var fxa: Pool
var fxn: Pool
var rings: Array = []          # {m: MeshInstance3D, mat, t, life, size, flat}
var ring_i := 0
var cam: Camera3D
var spark_tex: Texture2D
var smoke_tex: Texture2D
var glow_tex: Texture2D
var lite := false


static func radial(stops: Array, size := 64) -> GradientTexture2D:
	var g := Gradient.new()
	g.offsets = PackedFloat32Array()
	g.colors = PackedColorArray()
	for s in stops:
		g.add_point(float(s[0]), Color(1, 1, 1, float(s[1])))
	# Gradient starts with two default points; drop them
	g.remove_point(0)
	g.remove_point(0)
	var t := GradientTexture2D.new()
	t.gradient = g
	t.fill = GradientTexture2D.FILL_RADIAL
	t.fill_from = Vector2(0.5, 0.5)
	t.fill_to = Vector2(1.0, 0.5)
	t.width = size
	t.height = size
	return t


func _init() -> void:
	spark_tex = radial([[0.0, 1.0], [0.2, 0.9], [0.5, 0.25], [1.0, 0.0]])
	smoke_tex = radial([[0.0, 0.9], [0.5, 0.35], [1.0, 0.0]])
	glow_tex = radial([[0.0, 1.0], [0.25, 0.55], [1.0, 0.0]], 128)


func _ready() -> void:
	var sh: Shader = load("res://shaders/particle.gdshader")
	var ma := ShaderMaterial.new()
	ma.shader = sh
	ma.set_shader_parameter("tex", spark_tex)
	ma.set_shader_parameter("additive", true)
	var mn := ShaderMaterial.new()
	mn.shader = load("res://shaders/particle_mix.gdshader")
	mn.set_shader_parameter("tex", smoke_tex)
	fxa = Pool.new(560, ma, self)
	fxn = Pool.new(260, mn, self)
	fxa.node.sorting_offset = 5.0
	# rings: a flat annulus, added on top, fading as it grows
	var ring_mesh := _annulus(0.82, 1.0, 56)
	for i in RINGS:
		var m := MeshInstance3D.new()
		m.mesh = ring_mesh
		var mat := StandardMaterial3D.new()
		mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
		mat.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
		mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
		mat.cull_mode = BaseMaterial3D.CULL_DISABLED
		mat.no_depth_test = false
		mat.disable_fog = true
		mat.depth_draw_mode = BaseMaterial3D.DEPTH_DRAW_DISABLED
		m.material_override = mat
		m.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		m.visible = false
		add_child(m)
		rings.append({"m": m, "mat": mat, "t": 0.0, "life": 1.0, "size": 1.0, "flat": true})


static func _annulus(r0: float, r1: float, seg: int) -> ArrayMesh:
	var st := SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	for i in seg:
		var a0 := TAU * i / seg
		var a1 := TAU * (i + 1) / seg
		var p0 := Vector3(cos(a0) * r0, sin(a0) * r0, 0)
		var p1 := Vector3(cos(a0) * r1, sin(a0) * r1, 0)
		var p2 := Vector3(cos(a1) * r1, sin(a1) * r1, 0)
		var p3 := Vector3(cos(a1) * r0, sin(a1) * r0, 0)
		for q in [p0, p1, p2, p0, p2, p3]:
			st.set_normal(Vector3(0, 0, 1))
			st.add_vertex(q)
	return st.commit()


func spawn_a(x: float, y: float, z: float, vx: float, vy: float, vz: float, col: Color, s0: float, s1: float, life: float, grav := 0.0, drag := 0.0) -> void:
	fxa.spawn(x, y, z, vx, vy, vz, col, s0, s1, life, grav, drag)


func spawn_n(x: float, y: float, z: float, vx: float, vy: float, vz: float, col: Color, s0: float, s1: float, life: float, grav := 0.0, drag := 0.0) -> void:
	fxn.spawn(x, y, z, vx, vy, vz, col, s0, s1, life, grav, drag)


## web burst0: n sparks thrown up and out
func burst(x: float, y: float, z: float, n: int, cols: Array, spd: float, size: float) -> void:
	for i in n:
		var a := randf() * TAU
		var u := randf()
		var col: Color = cols[i % cols.size()]
		fxa.spawn(x, y, z, cos(a) * spd * u, spd * (0.4 + randf() * 0.8), sin(a) * spd * u, col, size, size * 0.3, 0.6 + randf() * 0.4, 60.0, 1.5)


## web spawnRing0: an expanding ring, flat on the ground or facing the camera
func ring(x: float, y: float, z: float, col: Color, size: float, life: float, flat := true) -> void:
	var r: Dictionary = rings[ring_i % rings.size()]
	ring_i += 1
	(r["mat"] as StandardMaterial3D).albedo_color = col
	var m: MeshInstance3D = r["m"]
	m.position = Vector3(x, y, z)
	r["t"] = 0.0
	r["life"] = life
	r["size"] = size
	r["flat"] = flat
	m.visible = true
	m.rotation = Vector3(-PI / 2.0 if flat else 0.0, 0.0, 0.0)


func step(dt: float) -> void:
	fxa.update(dt)
	fxn.update(dt)
	for r in rings:
		var m: MeshInstance3D = r["m"]
		if not m.visible:
			continue
		r["t"] = float(r["t"]) + dt
		var f := float(r["t"]) / float(r["life"])
		if f >= 1.0:
			m.visible = false
			continue
		var e := 1.0 - pow(1.0 - f, 3.0)
		var s := 0.5 + float(r["size"]) * e
		var mat: StandardMaterial3D = r["mat"]
		var col := mat.albedo_color
		col.a = (1.0 - f) * 0.9
		mat.albedo_color = col
		if not bool(r["flat"]) and cam != null:
			m.look_at(cam.global_position, Vector3.UP)
			m.rotate_object_local(Vector3.UP, PI)
		m.scale = Vector3(s, s, s)


func clear() -> void:
	fxa.clear()
	fxn.clear()
	for r in rings:
		(r["m"] as MeshInstance3D).visible = false
