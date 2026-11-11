class_name HdWater
## The PC's water (Settings > Graphics > Finished models): the web game's sea, lakes, the pools under the glide gaps
## and the swimming pools become real water (shaders/water.gdshader): drifting waves that calm into the distance,
## colour that deepens with the depth, the bottom showing through the shallows with a play of light on it, the sky
## and the sun reflected, and foam where it laps at the shore. Drawing only: where karts float, sink or get fished
## out doesn't change.
##
## A surface is water when it is flat and wide, blue or teal, and either glossy (the sea and the pools) or
## see-through (lakes and ponds). The faint white ripple sheets the web lays over its pools are dropped, since the
## water now ripples itself.

static var _n1: NoiseTexture2D
static var _n2: NoiseTexture2D
static var _foam: NoiseTexture2D
static var _hide: ShaderMaterial


static func upgrade(root: Node, theme: String, T: TrackData = null) -> int:
	var done := {}
	var n := 0
	for node in root.find_children("*", "MeshInstance3D", true, false):
		var mi := node as MeshInstance3D
		if mi.mesh == null:
			continue
		var bb := mi.get_aabb()
		if bb.size.y > 6.0 or bb.size.x * bb.size.z < 900.0:
			continue
		for si in mi.mesh.get_surface_count():
			var m := mi.get_active_material(si) as StandardMaterial3D
			if m == null:
				continue
			var kind := _kind(m, theme)
			if OS.has_environment("CR_WATER_DBG"):
				print("WATERDBG ", mi.name, " at ", (mi.global_transform * bb).get_center().snapped(Vector3.ONE), " ", bb.size.snapped(Vector3.ONE), " ", _avg(m), " tr=", m.transparency, " em=", m.emission_enabled, " ", m.emission_energy_multiplier, " sh=", m.shading_mode, " r=", m.roughness, " -> ", kind)
			if kind == "":
				continue
			if kind == "sheet":
				mi.set_surface_override_material(si, _hidden())
				continue
			# a pool laid on the ground (the web's kart-swallowing ponds) has almost no water under it: it gets a
			# body of water of its own, so it doesn't read as a sheet of foam over sand
			var shallow := 0.0
			if T != null and bb.size.x * bb.size.z < 2.0e5:
				var c := (mi.global_transform * bb).get_center()
				if c.y - T.ground(c.x, c.z) < 4.0:
					shallow = 24.0
			var key := [m, shallow]
			if not done.has(key):
				var sea := bb.size.x * bb.size.z > 4.0e6
				done[key] = _water(_avg(m), theme, sea, shallow)
				if sea and T != null:
					(done[key] as ShaderMaterial).set_shader_parameter("shelf_r", T.R)
			mi.set_surface_override_material(si, done[key])
			n += 1
	return n


## "water", "sheet" (a ripple overlay to drop) or "" (not water)
static func _kind(m: StandardMaterial3D, theme: String) -> String:
	var see := m.transparency != BaseMaterial3D.TRANSPARENCY_DISABLED
	var col := _avg(m)
	if see and m.albedo_color.a < 0.35 and col.r > 0.7 and col.g > 0.8 and col.b > 0.85:
		# (the frozen tracks' pools stay ice, so their sheen stays too)
		return "" if theme == "freezer" else "sheet"
	# glowing signs and lights stay as they are (the web's water glows only faintly)
	if m.emission_enabled and (m.emission * m.emission_energy_multiplier).get_luminance() > 0.3:
		return ""
	if m.shading_mode == BaseMaterial3D.SHADING_MODE_UNSHADED and not see:
		return ""
	# blue or teal (night water leans violet), clearly more blue than red
	if col.b < 0.2 or col.b < col.r + 0.08 or (col.g < col.r and theme != "night"):
		return ""
	# the ice of the frozen tracks stays ice: only see-through water there
	if theme == "freezer" and not see:
		return ""
	if not see and m.roughness > 0.3:
		return ""
	return "water"


## the surface's own colour (its picture averaged, times its tint)
static func _avg(m: StandardMaterial3D) -> Color:
	var c := m.albedo_color
	if m.albedo_texture != null:
		var img := m.albedo_texture.get_image()
		if img != null:
			img = img.duplicate()
			if img.is_compressed():
				img.decompress()
			img.resize(1, 1, Image.INTERPOLATE_BILINEAR)
			var t := img.get_pixel(0, 0)
			c = Color(c.r * t.r, c.g * t.g, c.b * t.b, c.a)
	return c


static func _water(col: Color, theme: String, sea: bool, shallow := 0.0) -> ShaderMaterial:
	_make()
	var m := ShaderMaterial.new()
	m.shader = load("res://shaders/water.gdshader")
	# the colours from the web's own: clear and bright where it's shallow, a deep saturated blue-green where it isn't
	var c := Color(col.r, col.g, col.b)
	var lum := c.get_luminance()
	if lum > 0.55:
		c = c.darkened(0.35)
	var sh := c.lerp(Color(0.2, 0.74, 0.72), 0.3)
	var dp := Color(sh.r * 0.04, sh.g * 0.48, sh.b * 0.64)
	if theme == "night":
		sh = sh.darkened(0.35)
		dp = Color(dp.r * 0.6 + 0.02, dp.g * 0.5, dp.b * 0.7 + 0.04)
	elif theme == "freezer":
		sh = sh.lerp(Color(0.5, 0.74, 0.82), 0.45)
		dp = dp.lerp(Color(0.06, 0.2, 0.3), 0.4)
	elif theme == "kitchen":
		sh = sh.lerp(Color(0.3, 0.55, 0.5), 0.2)
	if shallow > 0.0 and theme != "night" and theme != "freezer":
		# a pond beside the road: clear blue (it read grey, the bottom and the pale sky showing more than the water)
		sh = sh.lerp(Color(0.16, 0.6, 0.86), 0.55)
		dp = dp.lerp(Color(0.03, 0.22, 0.42), 0.5)
		m.set_shader_parameter("own_colour", 0.35)
	m.set_shader_parameter("shallow", sh)
	m.set_shader_parameter("deep", dp)
	# the open sea is deep almost everywhere; a pool or a lake fills in over a shorter depth
	m.set_shader_parameter("depth_scale", 70.0 if sea else 40.0)
	m.set_shader_parameter("min_depth", shallow)
	m.set_shader_parameter("n1", _n1)
	m.set_shader_parameter("n2", _n2)
	m.set_shader_parameter("foam_tex", _foam)
	m.set_shader_parameter("foam_amount", 0.6 if theme == "freezer" else 1.0)
	m.set_shader_parameter("wave_strength", 0.6 if sea else 0.4)
	return m


## draws nothing (the dropped ripple sheets)
static func _hidden() -> ShaderMaterial:
	if _hide == null:
		var s := Shader.new()
		s.code = "shader_type spatial;\nrender_mode unshaded;\nvoid fragment() { discard; }\n"
		_hide = ShaderMaterial.new()
		_hide.shader = s
	return _hide


static func _make() -> void:
	if _n1 != null:
		return
	_n1 = _noise(91, 0.02, 4, true, 3.0)
	_n2 = _noise(92, 0.05, 3, true, 2.0)
	_foam = _noise(93, 0.06, 3, false, 0.0)


static func _noise(seed_: int, freq: float, oct: int, nrm: bool, bump: float) -> NoiseTexture2D:
	var t := NoiseTexture2D.new()
	t.width = 512
	t.height = 512
	t.seamless = true
	t.generate_mipmaps = true
	t.as_normal_map = nrm
	if nrm:
		t.bump_strength = bump
	var n := FastNoiseLite.new()
	n.seed = seed_
	n.frequency = freq
	n.fractal_octaves = oct
	t.noise = n
	return t
