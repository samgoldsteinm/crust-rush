class_name HdGround
## The PC build's finished ground: the web game's own ground picture (cheese on most tracks, frost on the frozen
## ones) keeps its colours and gains depth. Its light flecks of shredded cheese stand up, the browned blisters swell,
## the pepper specks sink in; a slow melted ripple runs through it, it's glossier where it's fresh, and a fine grain
## shows up close. The relief and gloss maps are made from each track's own picture by tools/hd_ground.py (listed in
## <track>_hd.json next to the track), so they match every track's ground. Drawing only.

static var _grain: NoiseTexture2D
static var _white: ImageTexture
static var _mask: ImageTexture


## finishes the ground material(s) of a loaded track (the exporter names them "terrain_N"); returns how many
static func upgrade(root: Node, index_path: String) -> int:
	if not FileAccess.file_exists(index_path):
		return 0
	var idx = JSON.parse_string(FileAccess.get_file_as_string(index_path))
	if not (idx is Dictionary) or (idx as Dictionary).is_empty():
		return 0
	var base := index_path.get_base_dir()
	var done := {}
	for node in root.find_children("*", "MeshInstance3D", true, false):
		var mi := node as MeshInstance3D
		if mi.mesh == null:
			continue
		for si in mi.mesh.get_surface_count():
			var m := mi.mesh.surface_get_material(si) as StandardMaterial3D
			if m == null or done.has(m):
				continue
			var nm := String(m.resource_name)
			if not idx.has(nm):
				continue
			done[m] = true
			_finish(m, base.path_join(String(idx[nm].get("n", ""))), base.path_join(String(idx[nm].get("r", ""))))
	return done.size()


static func _load(path: String) -> ImageTexture:
	if not FileAccess.file_exists(path):
		return null
	var img := Image.load_from_file(path)
	if img == null or img.is_empty():
		return null
	img.generate_mipmaps()
	return ImageTexture.create_from_image(img)


static func _finish(m: StandardMaterial3D, n_path: String, r_path: String) -> void:
	var nt := _load(n_path)
	if nt != null:
		m.normal_enabled = true
		m.normal_texture = nt
		m.normal_scale = 1.0
	var rt := _load(r_path)
	if rt != null:
		m.roughness = 1.0
		m.roughness_texture = rt
		m.roughness_texture_channel = BaseMaterial3D.TEXTURE_CHANNEL_GREEN
	# a fine grain up close, laid over the world so it has no seams
	if _grain == null:
		_grain = NoiseTexture2D.new()
		_grain.width = 512
		_grain.height = 512
		_grain.seamless = true
		_grain.as_normal_map = true
		_grain.bump_strength = 2.5
		_grain.generate_mipmaps = true
		var n := FastNoiseLite.new()
		n.seed = 31
		n.frequency = 0.05
		n.fractal_octaves = 4
		_grain.noise = n
		var w := Image.create(4, 4, false, Image.FORMAT_RGBA8)
		w.fill(Color(1, 1, 1, 1))
		_white = ImageTexture.create_from_image(w)
		var k := Image.create(4, 4, false, Image.FORMAT_RGBA8)
		k.fill(Color(0.35, 0.35, 0.35))
		_mask = ImageTexture.create_from_image(k)
	m.detail_enabled = true
	m.detail_uv_layer = BaseMaterial3D.DETAIL_UV_2
	m.uv2_triplanar = true
	m.uv2_world_triplanar = true
	m.uv2_scale = Vector3(0.12, 0.12, 0.12)
	# white, multiplied: the colours stay the picture's own, only the grain's relief is added
	m.detail_blend_mode = BaseMaterial3D.BLEND_MODE_MUL
	m.detail_normal = _grain
	m.detail_albedo = _white
	m.detail_mask = _mask
