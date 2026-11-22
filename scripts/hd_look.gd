class_name HdLook
## (pc117) The PC's look past the web game, each part its own setting (Settings > Graphics):
##  - baked light: a VoxelGI over the whole track, baked while the race loads, so light bounces off the road, the hills and
##    the walls onto everything near them (karts included). Ultra.
##  - fog and light rays: volumetric fog in the theme's air colour; the sun and the headlights shine through it. Ultra.
##  - screen reflections: glossy surfaces (toy plastic, water, polished floors, wet-looking road) show what is on screen. Ultra.
##  - film grade: a colour grade for each theme (cool shade, warm light; deep blue nights...). All qualities.
##  - road detail: fine grain and worn, glossier patches on the road surface. With Finished models.
## (Tyre marks are in fx.gd / view.gd.)

## the theme's split-tone: [shadow tint, highlight tint, strength]
const GRADES := {
	"kitchen": [Vector3(0.93, 0.98, 1.06), Vector3(1.05, 1.0, 0.92), 1.0],
	"bay": [Vector3(0.93, 0.99, 1.07), Vector3(1.05, 1.01, 0.94), 1.0],
	"night": [Vector3(0.9, 0.94, 1.14), Vector3(1.05, 0.98, 1.0), 1.0],
	"freezer": [Vector3(0.93, 0.98, 1.09), Vector3(1.01, 1.01, 1.02), 1.0],
	"toy": [Vector3(0.97, 0.97, 1.04), Vector3(1.05, 1.0, 0.93), 1.0],
}

## the air: [colour, density per unit, rays (forward scattering 0..1)]
const AIR := {
	"kitchen": [Color(1.0, 0.9, 0.78), 0.00018, 0.6],
	"bay": [Color(0.86, 0.92, 1.0), 0.00015, 0.6],
	"night": [Color(0.55, 0.62, 0.9), 0.0005, 0.45],
	"freezer": [Color(0.92, 0.96, 1.0), 0.0003, 0.5],
	"toy": [Color(1.0, 0.94, 0.85), 0.00014, 0.7],
}


static func _key(T: TrackData) -> String:
	if T.toy:
		return "toy"
	return T.theme if GRADES.has(T.theme) else "kitchen"


## baked bounce light over the track (returns the node, or null). Takes a few seconds on a big track.
static func bake_gi(world: Node3D, T: TrackData, energy := 0.35) -> VoxelGI:
	var lo := Vector3(INF, INF, INF)
	var hi := Vector3(-INF, -INF, -INF)
	for j in T.N:
		var p := Vector3(T.px[j], T.ground(T.px[j], T.py[j]) + T.ey[j], T.py[j])
		lo = lo.min(p)
		hi = hi.max(p)
	if not lo.is_finite() or not hi.is_finite():
		return null
	lo -= Vector3(250, 60, 250)
	hi += Vector3(250, 220, 250)
	var gi := VoxelGI.new()
	gi.name = "BakedLight"
	gi.size = hi - lo
	# a big track bakes at half the detail: 256 took 11-12 s on Spiral and Basil, too long to wait at the start
	gi.subdiv = VoxelGI.SUBDIV_128 if maxf(gi.size.x, gi.size.z) > 3600.0 else VoxelGI.SUBDIV_256
	gi.position = (lo + hi) * 0.5
	world.add_child(gi)
	var t0 := Time.get_ticks_msec()
	gi.bake(world)
	if gi.data == null:
		gi.queue_free()
		return null
	gi.data.energy = energy
	gi.data.propagation = 0.6
	gi.data.use_two_bounces = true
	print("baked light: %d ms" % (Time.get_ticks_msec() - t0))
	return gi


static func fog(env: Environment, T: TrackData, on: bool) -> void:
	env.volumetric_fog_enabled = on
	if not on:
		return
	var a: Array = AIR[_key(T)]
	env.volumetric_fog_albedo = a[0]
	env.volumetric_fog_density = float(a[1])
	env.volumetric_fog_anisotropy = float(a[2])
	env.volumetric_fog_length = 900.0 if not T.toy else 1400.0
	env.volumetric_fog_detail_spread = 2.0
	env.volumetric_fog_gi_inject = 0.6
	env.volumetric_fog_ambient_inject = 0.25
	env.volumetric_fog_sky_affect = 0.0
	env.volumetric_fog_temporal_reprojection_enabled = true
	env.volumetric_fog_temporal_reprojection_amount = 0.85


static func ssr(env: Environment, on: bool) -> void:
	env.ssr_enabled = on
	if on:
		env.ssr_max_steps = 64
		env.ssr_fade_in = 0.15
		env.ssr_fade_out = 2.0
		env.ssr_depth_tolerance = 1.5


static func grade(post_mat: ShaderMaterial, T: TrackData, on: bool) -> void:
	if post_mat == null:
		return
	var g: Array = GRADES[_key(T)]
	post_mat.set_shader_parameter("split", float(g[2]) if on else 0.0)
	post_mat.set_shader_parameter("sh_col", g[0])
	post_mat.set_shader_parameter("hi_col", g[1])


static var _grain: NoiseTexture2D
static var _wear: NoiseTexture2D
static var _patch: NoiseTexture2D


static func _tex() -> void:
	if _grain != null:
		return
	_grain = NoiseTexture2D.new()
	_grain.width = 512
	_grain.height = 512
	_grain.seamless = true
	_grain.as_normal_map = true
	_grain.bump_strength = 6.0
	_grain.generate_mipmaps = true
	var n := FastNoiseLite.new()
	n.seed = 77
	n.noise_type = FastNoiseLite.TYPE_CELLULAR
	n.frequency = 0.09
	n.fractal_type = FastNoiseLite.FRACTAL_FBM
	n.fractal_octaves = 3
	_grain.noise = n
	# the worn and polished patches: low, slow noise; dark = glossier
	_wear = NoiseTexture2D.new()
	_wear.width = 256
	_wear.height = 256
	_wear.seamless = true
	_wear.generate_mipmaps = true
	var w := FastNoiseLite.new()
	w.seed = 5
	w.frequency = 0.012
	w.fractal_octaves = 4
	_wear.noise = w
	var cr := Gradient.new()
	cr.set_color(0, Color(0.55, 0.55, 0.55))
	cr.set_color(1, Color(1, 1, 1))
	_wear.color_ramp = cr
	# the surface's colour: a little darker in places (tyre rubber, old oil), multiplied
	_patch = NoiseTexture2D.new()
	_patch.width = 256
	_patch.height = 256
	_patch.seamless = true
	_patch.generate_mipmaps = true
	var p := FastNoiseLite.new()
	p.seed = 19
	p.frequency = 0.02
	p.fractal_octaves = 3
	_patch.noise = p
	var pr := Gradient.new()
	pr.set_color(0, Color(0.8, 0.8, 0.8))
	pr.set_color(1, Color(1, 1, 1))
	_patch.color_ramp = pr


## the road's surfaces, found by where they lie (on the track, at road height), given grain and wear; returns how many
static func road(root: Node, T: TrackData) -> int:
	if T.toy or OS.get_environment("CR_NOROAD") == "1":
		return 0
	_tex()
	var done := {}
	for node in root.find_children("*", "MeshInstance3D", true, false):
		var mi := node as MeshInstance3D
		if mi.mesh == null or not (mi.mesh is ArrayMesh):
			continue
		var xf := mi.global_transform
		for si in mi.mesh.get_surface_count():
			var m := mi.mesh.surface_get_material(si) as StandardMaterial3D
			if m == null or done.has(m) or String(m.resource_name).begins_with("terrain") or m.detail_enabled:
				continue
			if m.transparency != BaseMaterial3D.TRANSPARENCY_DISABLED or m.metallic > 0.3:
				continue
			var arr := mi.mesh.surface_get_arrays(si)
			var vs: PackedVector3Array = arr[Mesh.ARRAY_VERTEX]
			var ns: PackedVector3Array = arr[Mesh.ARRAY_NORMAL]
			if vs.size() < 12:
				continue
			var hit := 0
			var tot := 0
			var step := maxi(1, vs.size() / 60)
			var j := 0
			for vi in range(0, vs.size(), step):
				var p := xf * vs[vi]
				tot += 1
				if ns.size() > vi and (xf.basis * ns[vi]).normalized().y < 0.7:
					continue
				j = T.nearest_any(p.x, p.z)
				if absf(T.lateral(j, p.x, p.z)) > T.RW * 1.02:
					continue
				var g := T.ground(p.x, p.z) + T.k_ey(j, p.x, p.z)
				if absf(p.y - g) < 2.5:
					hit += 1
			if tot == 0 or float(hit) / tot < 0.85:
				continue
			done[m] = true
			m.detail_enabled = true
			m.detail_uv_layer = BaseMaterial3D.DETAIL_UV_2
			m.uv2_triplanar = true
			m.uv2_world_triplanar = true
			m.uv2_scale = Vector3(0.35, 0.35, 0.35)
			m.detail_blend_mode = BaseMaterial3D.BLEND_MODE_MUL
			m.detail_albedo = _patch
			m.detail_normal = _grain
			m.normal_enabled = true
			m.normal_scale = 0.6
			if m.roughness_texture == null:
				m.roughness_texture = _wear
				m.roughness = minf(1.0, m.roughness * 1.05)
	return done.size()
