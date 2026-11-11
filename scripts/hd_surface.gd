class_name HdSurface
## The PC build's finish for the web game's plain-coloured scenery (Settings > Graphics > Finished models). Drawing
## only. Every opaque track material that has no picture of its own (buildings, barriers, signs, barrels, crates, the
## baked trackside clutter) gets a fine surface laid over the world: a soft mottling of its colour and a light grain
## in the light, so painted wood, plaster, plastic and metal read as surfaces instead of flat untextured colour. The
## colours and shapes stay the web's own.

static var _mottle: NoiseTexture2D
static var _grain: NoiseTexture2D
static var _mask: ImageTexture


static func upgrade(root: Node) -> int:
	_make()
	_relief_cache.clear()
	var done := {}
	var n := 0
	for node in root.find_children("*", "MeshInstance3D", true, false):
		var mi := node as MeshInstance3D
		if mi.mesh == null:
			continue
		for si in mi.mesh.get_surface_count():
			var m := mi.get_active_material(si) as StandardMaterial3D
			if m == null or done.has(m):
				continue
			done[m] = true
			if _plain(m):
				_finish(m)
				n += 1
			elif _pictured(m):
				_relief_cache[m] = _relief(m)
				n += 1
		# pictured materials become the relief shader (a new material, so swap it in on every surface using it)
		for si2 in mi.mesh.get_surface_count():
			var m2 := mi.get_active_material(si2) as StandardMaterial3D
			if m2 != null and _relief_cache.has(m2):
				mi.set_surface_override_material(si2, _relief_cache[m2])
	return n


static var _relief_cache := {}
static var _shaders := {}


## opaque, lit, with a picture of its own; not the ground (it has its own finish), not glowing, not triplanar
static func _pictured(m: StandardMaterial3D) -> bool:
	if m.shading_mode == BaseMaterial3D.SHADING_MODE_UNSHADED or m.transparency != BaseMaterial3D.TRANSPARENCY_DISABLED:
		return false
	if m.albedo_texture == null or m.detail_enabled or m.normal_enabled or m.uv1_triplanar:
		return false
	if m.emission_enabled or m.resource_name.begins_with("terrain"):
		return false
	return true


static func _relief(m: StandardMaterial3D) -> ShaderMaterial:
	var cull := "cull_disabled" if m.cull_mode == BaseMaterial3D.CULL_DISABLED else "cull_back"
	if not _shaders.has(cull):
		var sh := Shader.new()
		sh.code = (load("res://shaders/relief.gdshader") as Shader).code.replace("CULL_MODE", cull)
		_shaders[cull] = sh
	var r := ShaderMaterial.new()
	r.shader = _shaders[cull]
	r.set_shader_parameter("albedo", m.albedo_color)
	r.set_shader_parameter("tex", m.albedo_texture)
	r.set_shader_parameter("grain", _grain)
	r.set_shader_parameter("uv_scale", m.uv1_scale)
	r.set_shader_parameter("uv_offset", m.uv1_offset)
	r.set_shader_parameter("vcol", m.vertex_color_use_as_albedo)
	r.set_shader_parameter("rough", m.roughness)
	r.set_shader_parameter("metal", m.metallic)
	var tw := maxi(1, m.albedo_texture.get_width())
	var th := maxi(1, m.albedo_texture.get_height())
	r.set_shader_parameter("texel", Vector2(1.0 / tw, 1.0 / th))
	return r


## opaque, lit, no picture of its own, not glowing, not already finished (the ground has its own)
static func _plain(m: StandardMaterial3D) -> bool:
	if m.shading_mode == BaseMaterial3D.SHADING_MODE_UNSHADED or m.transparency != BaseMaterial3D.TRANSPARENCY_DISABLED:
		return false
	if m.albedo_texture != null or m.detail_enabled or m.normal_enabled:
		return false
	if m.emission_enabled and m.emission_energy_multiplier > 0.3 and (m.emission.r + m.emission.g + m.emission.b) > 0.3:
		return false
	return true


static func _finish(m: StandardMaterial3D) -> void:
	m.detail_enabled = true
	m.detail_uv_layer = BaseMaterial3D.DETAIL_UV_2
	m.uv2_triplanar = true
	m.uv2_world_triplanar = true
	m.uv2_scale = Vector3(0.05, 0.05, 0.05)
	m.detail_blend_mode = BaseMaterial3D.BLEND_MODE_MUL
	m.detail_albedo = _mottle
	m.detail_normal = _grain
	m.detail_mask = _mask
	# metal stays metal; everything else gets a touch more texture in its sheen
	if m.metallic < 0.5:
		m.roughness = clampf(m.roughness + 0.04, 0.0, 1.0)


static func _make() -> void:
	if _mottle != null:
		return
	# a soft mottling: near white, multiplied, so a colour varies by a few percent across a surface
	_mottle = NoiseTexture2D.new()
	_mottle.width = 512
	_mottle.height = 512
	_mottle.seamless = true
	_mottle.generate_mipmaps = true
	var n := FastNoiseLite.new()
	n.seed = 77
	n.frequency = 0.012
	n.fractal_octaves = 5
	_mottle.noise = n
	var ramp := Gradient.new()
	ramp.set_color(0, Color(0.85, 0.845, 0.835))
	ramp.set_color(1, Color(1.0, 1.0, 1.0))
	_mottle.color_ramp = ramp
	_grain = NoiseTexture2D.new()
	_grain.width = 512
	_grain.height = 512
	_grain.seamless = true
	_grain.as_normal_map = true
	_grain.bump_strength = 1.4
	_grain.generate_mipmaps = true
	var gn := FastNoiseLite.new()
	gn.seed = 79
	gn.frequency = 0.06
	gn.fractal_octaves = 3
	_grain.noise = gn
	var k := Image.create(4, 4, false, Image.FORMAT_RGBA8)
	k.fill(Color(0.8, 0.8, 0.8))
	_mask = ImageTexture.create_from_image(k)
