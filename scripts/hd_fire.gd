class_name HdFire
## Real-looking wood fires on the PC (Settings > Graphics > Finished models). Drawing only.
## The web game draws each fire in the oven (Oven Rush Raceway) as five plain orange cones over a glowing ball. Here
## the cones are taken out and each fire gets: flames drawn by a shader on sheets that face you (shaders/fire.gdshader),
## a bed of embers with glowing seams (shaders/coals.gdshader), sparks that rise and drift, a soft glow in the air
## round it, and a flickering light on the logs, the floor and the oven wall.
## Works from what is in the track: wherever the web's flame cones stand, a fire is built.


static func upgrade(root: Node3D) -> int:
	var hide := StandardMaterial3D.new()
	hide.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	hide.albedo_color = Color(0, 0, 0, 0)
	hide.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	var coals := ShaderMaterial.new()
	coals.shader = load("res://shaders/coals.gdshader")
	var pits: Array = []          # [centre sum, count, lowest y, highest y]
	for node in root.find_children("*", "MeshInstance3D", true, false):
		var mi := node as MeshInstance3D
		if mi.mesh == null:
			continue
		for si in mi.mesh.get_surface_count():
			var m := mi.mesh.surface_get_material(si) as StandardMaterial3D
			if m == null:
				continue
			var c := m.albedo_color
			if m.shading_mode == BaseMaterial3D.SHADING_MODE_UNSHADED and m.transparency != BaseMaterial3D.TRANSPARENCY_DISABLED \
					and c.r > 0.9 and c.g > 0.45 and c.g < 0.85 and c.b < 0.45 and c.a > 0.7 and c.a < 0.95 and m.albedo_texture == null:
				# the web's flame cones: out, and remembered for where the fires stand
				var V: PackedVector3Array = mi.mesh.surface_get_arrays(si)[Mesh.ARRAY_VERTEX]
				if V.is_empty():
					continue
				var gt := mi.global_transform
				for v0 in V:
					var v := gt * v0
					var hit := false
					for p in pits:
						var cc: Vector3 = p[0] / float(p[1])
						if Vector2(cc.x - v.x, cc.z - v.z).length() < 700.0:
							p[0] += v
							p[1] += 1
							p[2] = minf(p[2], v.y)
							p[3] = maxf(p[3], v.y)
							hit = true
							break
					if not hit:
						pits.append([v, 1, v.y, v.y])
				mi.set_surface_override_material(si, hide)
			elif m.emission_enabled and m.emission.r > 0.8 and m.emission.g < 0.45 and m.emission.b < 0.2 and c.r > 0.8 and c.g < 0.6 \
					and mi.mesh.get_aabb().size.x > 400.0:
				# the glowing ball under the logs: a bed of embers
				mi.set_surface_override_material(si, coals)
	if pits.is_empty():
		return 0
	var flame := ShaderMaterial.new()
	flame.shader = load("res://shaders/fire.gdshader")
	flame.set_shader_parameter("energy", 1.5)
	var holder := Node3D.new()
	holder.name = "hd_fire"
	root.add_child(holder)
	var rng := RandomNumberGenerator.new()
	rng.seed = 9173
	for p in pits:
		var cc: Vector3 = p[0] / float(p[1])
		var base := float(p[2]) + 20.0
		var tall := maxf(420.0, float(p[3]) - float(p[2]))
		var at := Vector3(cc.x, base, cc.z)
		holder.add_child(_flames(at, tall, flame, rng))
		holder.add_child(_sparks(at, tall))
		holder.add_child(_glow(at + Vector3(0, tall * 0.42, 0), tall))
		var L := _Light.new()
		L.position = at + Vector3(0, tall * 0.45, 0)
		L.ph = rng.randf() * 20.0
		holder.add_child(L)
	return pits.size()


## the flames: sheets of several sizes standing in the fire, all in one mesh (one draw)
static func _flames(at: Vector3, tall: float, mat: ShaderMaterial, rng: RandomNumberGenerator) -> MeshInstance3D:
	var st := SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	var n := 0
	# [how many, spread from the middle, width, height] : a tall core, a ring of mid flames, low flames round the logs
	for tier in [[4, 70.0, 0.7, 1.3], [8, 200.0, 0.56, 0.95], [12, 250.0, 0.46, 0.62]]:
		for i in int(tier[0]):
			var a := rng.randf() * TAU
			var r := sqrt(rng.randf()) * float(tier[1])
			var c := Vector3(cos(a) * r, rng.randf() * 40.0 - 50.0, sin(a) * r)
			var w := tall * float(tier[2]) * (0.8 + rng.randf() * 0.4)
			var h := tall * float(tier[3]) * (0.8 + rng.randf() * 0.4)
			var seed_ := rng.randf()
			for q in [[-0.5, 0.0, 0.0, 1.0], [0.5, 0.0, 1.0, 1.0], [0.5, 1.0, 1.0, 0.0], [-0.5, 1.0, 0.0, 0.0]]:
				st.set_color(Color(seed_, 0, 0))
				st.set_uv(Vector2(q[2], q[3]))
				st.set_uv2(Vector2(float(q[0]) * w, float(q[1]) * h))
				st.add_vertex(c)
			for k in [0, 1, 2, 0, 2, 3]:
				st.add_index(n + k)
			n += 4
	var mi := MeshInstance3D.new()
	mi.name = "flames"
	mi.mesh = st.commit()
	mi.material_override = mat
	mi.position = at
	mi.custom_aabb = AABB(Vector3(-tall, -50.0, -tall), Vector3(tall * 2.0, tall * 2.2, tall * 2.0))
	mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	return mi


## sparks: thrown up out of the fire, drifting and dying as they rise
static func _sparks(at: Vector3, tall: float) -> GPUParticles3D:
	var ps := GPUParticles3D.new()
	ps.name = "sparks"
	ps.position = at + Vector3(0, tall * 0.15, 0)
	ps.amount = 140
	ps.lifetime = 4.2
	ps.preprocess = 4.0
	ps.randomness = 0.6
	ps.visibility_aabb = AABB(Vector3(-900, -100, -900), Vector3(1800, 2400, 1800))
	var pm := ParticleProcessMaterial.new()
	pm.emission_shape = ParticleProcessMaterial.EMISSION_SHAPE_SPHERE
	pm.emission_sphere_radius = tall * 0.32
	pm.direction = Vector3(0, 1, 0)
	pm.spread = 24.0
	pm.initial_velocity_min = 120.0
	pm.initial_velocity_max = 360.0
	pm.gravity = Vector3(0, 28.0, 0)
	pm.damping_min = 12.0
	pm.damping_max = 30.0
	pm.turbulence_enabled = true
	pm.turbulence_noise_strength = 3.0
	pm.turbulence_noise_scale = 3.0
	pm.turbulence_influence_min = 0.05
	pm.turbulence_influence_max = 0.25
	pm.scale_min = 0.5
	pm.scale_max = 1.6
	var g := Gradient.new()
	g.offsets = PackedFloat32Array([0.0, 0.25, 0.7, 1.0])
	g.colors = PackedColorArray([Color(1.0, 0.92, 0.6, 1.0), Color(1.0, 0.6, 0.15, 1.0), Color(0.9, 0.22, 0.03, 0.8), Color(0.4, 0.05, 0.0, 0.0)])
	var gt := GradientTexture1D.new()
	gt.gradient = g
	pm.color_ramp = gt
	ps.process_material = pm
	var q := QuadMesh.new()
	q.size = Vector2(7.0, 7.0)
	var sm := StandardMaterial3D.new()
	sm.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	sm.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
	sm.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	sm.vertex_color_use_as_albedo = true
	sm.billboard_mode = BaseMaterial3D.BILLBOARD_PARTICLES
	sm.albedo_texture = _dot()
	sm.albedo_color = Color(2.2, 2.2, 2.2)
	sm.disable_receive_shadows = true
	q.material = sm
	ps.draw_pass_1 = q
	ps.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	return ps


static var _dot_tex: GradientTexture2D = null


## a soft round dot
static func _dot() -> GradientTexture2D:
	if _dot_tex == null:
		var g := Gradient.new()
		g.offsets = PackedFloat32Array([0.0, 0.35, 1.0])
		g.colors = PackedColorArray([Color(1, 1, 1, 1), Color(1, 1, 1, 0.55), Color(1, 1, 1, 0)])
		_dot_tex = GradientTexture2D.new()
		_dot_tex.gradient = g
		_dot_tex.fill = GradientTexture2D.FILL_RADIAL
		_dot_tex.fill_from = Vector2(0.5, 0.5)
		_dot_tex.fill_to = Vector2(1.0, 0.5)
		_dot_tex.width = 64
		_dot_tex.height = 64
	return _dot_tex


## the glow in the air round the fire
static func _glow(at: Vector3, tall: float) -> MeshInstance3D:
	var q := QuadMesh.new()
	q.size = Vector2(tall * 3.4, tall * 3.0)
	var m := StandardMaterial3D.new()
	m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	m.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
	m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	m.billboard_mode = BaseMaterial3D.BILLBOARD_ENABLED
	m.albedo_texture = _dot()
	m.albedo_color = Color(1.0, 0.42, 0.1, 0.2)
	m.no_depth_test = false
	m.disable_receive_shadows = true
	m.disable_fog = true
	q.material = m
	var mi := MeshInstance3D.new()
	mi.name = "glow"
	mi.mesh = q
	mi.position = at
	mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	return mi


## the fire's light, flickering
class _Light extends OmniLight3D:
	var ph := 0.0
	var t := 0.0
	func _init() -> void:
		light_color = Color(1.0, 0.52, 0.18)
		omni_range = 2300.0
		omni_attenuation = 1.3
		light_energy = 5.0
		light_specular = 0.3
		shadow_enabled = false
	func _process(dt: float) -> void:
		t += dt
		var f := 0.5 + 0.5 * sin(t * 9.0 + ph) * sin(t * 5.3 + ph * 1.7)
		var s := 0.5 + 0.5 * sin(t * 1.9 + ph * 0.6)
		light_energy = 5.0 * (0.78 + 0.16 * f + 0.1 * s)
