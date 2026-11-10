class_name Gfx
extends RefCounted
## The PC version's look: lighting, shadows, screen effects and surface detail on top of the
## geometry exported from the web game. Drawing only; nothing here touches the race simulation.
## Levels: 0 = Low (the web game's look), 1 = High, 2 = Ultra (the default on PC).

static var _detail_albedo: NoiseTexture2D
static var _detail_normal: NoiseTexture2D
static var _fine_normal: NoiseTexture2D
static var _water_normal: NoiseTexture2D
static var _done := {}          # materials already upgraded (by instance id)
static var _nrm_cache := {}     # albedo texture id -> normal map built from it


static func _noise(seed_: int, freq: float, octaves: int) -> FastNoiseLite:
	var n := FastNoiseLite.new()
	n.seed = seed_
	n.noise_type = FastNoiseLite.TYPE_SIMPLEX_SMOOTH
	n.frequency = freq
	n.fractal_type = FastNoiseLite.FRACTAL_FBM
	n.fractal_octaves = octaves
	n.fractal_gain = 0.55
	return n


static func _ensure_textures() -> void:
	if _detail_albedo != null:
		return
	# a faint mottled grain multiplied over flat-coloured surfaces
	_detail_albedo = NoiseTexture2D.new()
	_detail_albedo.width = 512
	_detail_albedo.height = 512
	_detail_albedo.seamless = true
	_detail_albedo.generate_mipmaps = true
	_detail_albedo.noise = _noise(11, 0.012, 5)
	var gr := Gradient.new()
	gr.set_color(0, Color(0.8, 0.8, 0.8))
	gr.set_color(1, Color(1, 1, 1))
	_detail_albedo.color_ramp = gr
	# surface relief for the same surfaces
	_detail_normal = NoiseTexture2D.new()
	_detail_normal.width = 512
	_detail_normal.height = 512
	_detail_normal.seamless = true
	_detail_normal.generate_mipmaps = true
	_detail_normal.as_normal_map = true
	_detail_normal.bump_strength = 5.0
	_detail_normal.noise = _noise(23, 0.02, 5)
	# fine grain for tyres and matt kart parts
	_fine_normal = NoiseTexture2D.new()
	_fine_normal.width = 256
	_fine_normal.height = 256
	_fine_normal.seamless = true
	_fine_normal.generate_mipmaps = true
	_fine_normal.as_normal_map = true
	_fine_normal.bump_strength = 3.0
	_fine_normal.noise = _noise(37, 0.06, 4)
	_water_normal = NoiseTexture2D.new()
	_water_normal.width = 512
	_water_normal.height = 512
	_water_normal.seamless = true
	_water_normal.generate_mipmaps = true
	_water_normal.as_normal_map = true
	_water_normal.bump_strength = 7.0
	_water_normal.noise = _noise(51, 0.01, 4)


# ---------------------------------------------------------------- light, shadows, screen effects

static func apply_environment(env: Environment, sun: DirectionalLight3D, level: int, phone: bool) -> void:
	env.ssao_enabled = level >= 1 and not phone
	env.ssao_radius = 3.0
	env.ssao_intensity = 1.8
	env.ssao_power = 1.4
	env.ssil_enabled = level >= 2 and not phone      # bounce light between nearby surfaces
	env.ssil_radius = 7.0
	env.ssil_intensity = 0.9
	env.ssr_enabled = level >= 2 and not phone       # reflections on the water and wet-look paint
	env.set("ssr_max_steps", 56)
	env.set("ssr_fade_in", 0.15)
	env.set("ssr_fade_out", 2.0)
	env.set("ssr_depth_tolerance", 0.6)
	env.glow_enabled = level >= 1 and not phone
	env.glow_intensity = 0.45
	env.glow_bloom = 0.05
	env.glow_hdr_threshold = 1.05
	env.glow_blend_mode = Environment.GLOW_BLEND_MODE_SCREEN
	# sun shafts through the palms: a thin participating haze lit by the low sun
	env.volumetric_fog_enabled = level >= 2 and not phone
	env.volumetric_fog_density = 0.00007
	env.volumetric_fog_albedo = Color(1.0, 0.93, 0.85)
	env.volumetric_fog_emission_energy = 0.0
	env.volumetric_fog_anisotropy = 0.65
	env.volumetric_fog_length = 1400.0
	env.volumetric_fog_detail_spread = 2.0
	env.volumetric_fog_gi_inject = 0.4
	env.volumetric_fog_ambient_inject = 0.1
	env.volumetric_fog_sky_affect = 0.0
	env.volumetric_fog_temporal_reprojection_enabled = true
	if sun != null:
		sun.light_volumetric_fog_energy = 1.0
		sun.directional_shadow_mode = DirectionalLight3D.SHADOW_PARALLEL_4_SPLITS if (level >= 1 and not phone) else DirectionalLight3D.SHADOW_PARALLEL_2_SPLITS
		sun.directional_shadow_max_distance = 1000.0 if level >= 2 else 700.0
		sun.directional_shadow_blend_splits = level >= 1
		sun.directional_shadow_fade_start = 0.85
		sun.light_angular_distance = 0.45 if level >= 2 else 0.0   # soft, widening shadow edges
		sun.shadow_blur = 1.0 if level >= 2 else 1.4
		sun.shadow_normal_bias = 1.6
		sun.shadow_bias = 0.06


static func apply_viewport(vp: Viewport, level: int, phone: bool) -> void:
	if phone:
		return
	vp.msaa_3d = Viewport.MSAA_4X if level >= 1 else Viewport.MSAA_2X
	vp.screen_space_aa = Viewport.SCREEN_SPACE_AA_FXAA if level >= 2 else Viewport.SCREEN_SPACE_AA_DISABLED
	vp.use_debanding = true
	vp.anisotropic_filtering_level = Viewport.ANISOTROPY_16X if level >= 1 else Viewport.ANISOTROPY_4X
	vp.mesh_lod_threshold = 0.5 if level >= 2 else 1.0
	RenderingServer.directional_shadow_atlas_set_size(8192 if level >= 2 else 4096, true)
	RenderingServer.directional_soft_shadow_filter_set_quality(RenderingServer.SHADOW_QUALITY_SOFT_HIGH if level >= 2 else RenderingServer.SHADOW_QUALITY_SOFT_LOW)


# ---------------------------------------------------------------- surfaces

## Scenery: flat vertex-coloured surfaces get a mottled grain and relief (projected in world space, so
## it needs no UVs); textured ones get a relief map made from their own picture. The sea becomes
## moving water. Returns how many materials were touched: [grain, relief, water].
static func upgrade_track(root: Node, level: int, track_r: float, water_look: Array) -> Array:
	var out := [0, 0, 0]
	if level < 1:
		return out
	_ensure_textures()
	var budget := 70 if level >= 2 else 0     # relief maps built from pictures (Ultra only)
	for node in root.find_children("*", "MeshInstance3D", true, false):
		var mi := node as MeshInstance3D
		var am := mi.mesh as ArrayMesh
		if am == null:
			continue
		var bb := mi.get_aabb()
		for si in am.get_surface_count():
			var sm := am.surface_get_material(si) as StandardMaterial3D
			if sm == null:
				continue
			# the sea: one huge flat sheet
			if bb.size.y < 3.0 and bb.size.x > track_r and sm.transparency != BaseMaterial3D.TRANSPARENCY_DISABLED:
				mi.set_surface_override_material(si, water_material(water_look))
				mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
				out[2] += 1
				continue
			var id := sm.get_instance_id()
			if _done.has(id):
				continue
			_done[id] = true
			if sm.shading_mode == BaseMaterial3D.SHADING_MODE_UNSHADED or sm.transparency != BaseMaterial3D.TRANSPARENCY_DISABLED or sm.emission_enabled:
				continue
			if sm.albedo_texture == null and sm.normal_texture == null:
				sm.uv1_triplanar = true
				sm.uv1_world_triplanar = true
				sm.uv1_scale = Vector3(0.035, 0.035, 0.035)
				sm.uv1_triplanar_sharpness = 2.0
				sm.albedo_texture = _detail_albedo
				sm.normal_enabled = true
				sm.normal_texture = _detail_normal
				sm.normal_scale = 0.55
				out[0] += 1
			elif sm.albedo_texture != null and sm.normal_texture == null and budget > 0 and (am.surface_get_format(si) & Mesh.ARRAY_FORMAT_TANGENT) != 0:
				var nt := _relief_from(sm.albedo_texture)
				if nt != null:
					sm.normal_enabled = true
					sm.normal_texture = nt
					sm.normal_scale = 0.6
					budget -= 1
					out[1] += 1
	return out


## a relief (normal) map from a surface's own picture: bright = raised
static func _relief_from(tex: Texture2D) -> Texture2D:
	var id := tex.get_instance_id()
	if _nrm_cache.has(id):
		return _nrm_cache[id]
	var res: Texture2D = null
	var img := tex.get_image()
	if img != null and not img.is_empty():
		if img.is_compressed():
			img.decompress()
		if not img.is_compressed() and img.get_width() >= 128:
			var w := img.get_width()
			var h := img.get_height()
			var cap := 768.0
			if maxi(w, h) > int(cap):
				var k := cap / float(maxi(w, h))
				img.resize(maxi(4, int(w * k)), maxi(4, int(h * k)), Image.INTERPOLATE_BILINEAR)
			img.clear_mipmaps()
			img.convert(Image.FORMAT_L8)
			img.convert(Image.FORMAT_RGBA8)
			img.bump_map_to_normal_map(6.0)
			img.generate_mipmaps()
			res = ImageTexture.create_from_image(img)
	_nrm_cache[id] = res
	return res


static func water_material(look: Array) -> ShaderMaterial:
	_ensure_textures()
	var m := ShaderMaterial.new()
	m.shader = load("res://shaders/water.gdshader")
	m.set_shader_parameter("shallow", look[0])
	m.set_shader_parameter("deep", look[1])
	m.set_shader_parameter("nmap", _water_normal)
	return m


## Karts: glossy paint gets a clear coat; matt and rubber parts get a fine grain.
static func upgrade_kart(root: Node, level: int) -> void:
	if level < 1:
		return
	_ensure_textures()
	for node in root.find_children("*", "MeshInstance3D", true, false):
		var mi := node as MeshInstance3D
		var am := mi.mesh as ArrayMesh
		if am == null:
			continue
		var is_wheel := String(mi.name).begins_with("wheel") or (mi.get_parent() != null and String(mi.get_parent().name).begins_with("wheel"))
		for si in am.get_surface_count():
			var sm := am.surface_get_material(si) as StandardMaterial3D
			if sm == null:
				continue
			var id := sm.get_instance_id()
			if _done.has(id):
				continue
			_done[id] = true
			if sm.shading_mode == BaseMaterial3D.SHADING_MODE_UNSHADED or sm.transparency != BaseMaterial3D.TRANSPARENCY_DISABLED:
				continue
			if sm.roughness <= 0.45 and not is_wheel:
				sm.clearcoat_enabled = true
				sm.clearcoat = 1.0
				sm.clearcoat_roughness = 0.06
				sm.rim_enabled = true
				sm.rim = 0.25
				sm.rim_tint = 0.6
			elif sm.albedo_texture == null and sm.normal_texture == null and not sm.emission_enabled:
				sm.uv1_triplanar = true
				sm.uv1_scale = Vector3(0.9, 0.9, 0.9) if is_wheel else Vector3(0.5, 0.5, 0.5)
				sm.normal_enabled = true
				sm.normal_texture = _fine_normal
				sm.normal_scale = 0.9 if is_wheel else 0.35
