class_name Props
extends Node3D
## Trees, palms, bushes and rocks (the track data's "props"). The exporter records where the web game places them and
## keeps a copy of each shape; on the PC they're drawn as finished models built here: bark-textured trunks, crowns of
## leaf clusters, palm fronds and pine boughs that sway in the wind, and rocks with a real stone surface (free CC0
## textures from Poly Haven). The web game's own shapes stand in further away, and everywhere on Fast.
## Drawing only: nothing here is part of the race (it has no collisions; the web game's obstacles are separate).

const HD_DIR := "res://assets/hd/"
const CC0 := "res://assets/hd/cc0/"
const NEAR := 950.0         # finished models up to here, the plain shapes beyond
const CELL := 500.0         # props are batched by area, so that applies area by area

static var _tex := {}
static var _mats := {}
static var _meshes := {}    # built models, by kind and size

var level := 2


static func _t(path: String) -> Texture2D:
	if _tex.has(path):
		return _tex[path]
	var t: Texture2D = load(path) if ResourceLoader.exists(path) else null
	_tex[path] = t
	return t


## which finished model a recorded prop becomes ("" = keep the web game's shape)
static func hd_kind(base: String) -> String:
	match base:
		"palm":
			return "palm"
		# the web game's forest trees (tree_round1/2, treeA/B) are spruces with drooping tiers, like its pines
		"treeA", "treeB", "tree_round1", "tree_round2", "pineA", "pineB", "pine", "tree_pine1", "tree_pine2":
			return "pine"
		"shrub", "tree_shrub", "bush":
			return "bush"
		"rock":
			return "rock"
	return ""


func build(data: Dictionary, lvl: int) -> Dictionary:
	level = lvl
	var stats := {"kinds": 0, "items": 0, "hd": 0}
	var kinds: Dictionary = data.get("kinds", {})
	var items: Dictionary = data.get("items", {})
	for key in kinds:
		var kd: Dictionary = kinds[key]
		var list: Array = items.get(key, [])
		if list.is_empty():
			continue
		stats["kinds"] += 1
		stats["items"] += list.size()
		var proto := _proto_mesh(kd)
		if proto == null:
			continue
		var info := _proto_info(kd)
		var hk := hd_kind(String(kd.get("base", "")))
		var hd: Mesh = null
		if level >= 1 and hk != "":
			hd = _hd_mesh(hk, info, kd, String(key))
		var xf := _transforms(kd, list)
		if hd != null:
			stats["hd"] += list.size()
		# one batch per area of the map, so near ones get the finished model and far ones the plain shape
		var cells := {}
		for i in xf.size():
			var o: Vector3 = (xf[i] as Transform3D).origin
			var ck := Vector2i(floori(o.x / CELL), floori(o.z / CELL))
			if not cells.has(ck):
				cells[ck] = []
			(cells[ck] as Array).append(i)
		for ck in cells:
			var ids: Array = cells[ck]
			var centre := Vector3.ZERO
			for i in ids:
				centre += (xf[i] as Transform3D).origin
			centre /= float(ids.size())
			if hd != null:
				var near := _mmi(hd, xf, list, ids, centre)
				near.visibility_range_end = NEAR
				near.visibility_range_end_margin = 120.0
				near.visibility_range_fade_mode = GeometryInstance3D.VISIBILITY_RANGE_FADE_SELF
				near.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_ON
				add_child(near)
				if OS.get_environment("CR_NOFAR") == "1":
					continue
				var far := _mmi(proto, xf, list, ids, centre)
				far.visibility_range_begin = NEAR
				far.visibility_range_begin_margin = 120.0
				far.visibility_range_fade_mode = GeometryInstance3D.VISIBILITY_RANGE_FADE_SELF
				far.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
				add_child(far)
			else:
				var mm := _mmi(proto, xf, list, ids, centre)
				mm.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_ON if int(kd.get("shadow", 1)) == 1 else GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
				add_child(mm)
	return stats


# ---------------------------------------------------------------- placing

## each item's transform: dbAdd items [x, y, z, ry, s, tint]; forest items [x, y, z, ry, sx, sy, sz]
func _transforms(kd: Dictionary, list: Array) -> Array:
	var out: Array = []
	for it in list:
		var a: Array = it
		var sc := Vector3.ONE * float(a[4])
		if a.size() >= 7 and typeof(a[5]) != TYPE_STRING and a[5] != null:
			sc = Vector3(float(a[4]), float(a[5]), float(a[6]))
		out.append(Transform3D(Basis(Vector3.UP, float(a[3])) * Basis.from_scale(sc), Vector3(float(a[0]), float(a[1]), float(a[2]))))
	return out


func _mmi(mesh: Mesh, xf: Array, list: Array, ids: Array, centre: Vector3) -> MultiMeshInstance3D:
	var mm := MultiMesh.new()
	mm.transform_format = MultiMesh.TRANSFORM_3D
	mm.use_colors = true
	mm.mesh = mesh
	mm.instance_count = ids.size()
	for n in ids.size():
		var i: int = ids[n]
		var t: Transform3D = xf[i]
		t.origin -= centre
		mm.set_instance_transform(n, t)
		var a: Array = list[i]
		var c := Color.WHITE
		if a.size() == 6 and typeof(a[5]) == TYPE_STRING:
			c = Color(String(a[5]))
		mm.set_instance_color(n, c)
	var mi := MultiMeshInstance3D.new()
	mi.multimesh = mm
	mi.position = centre
	return mi


# ---------------------------------------------------------------- the web game's own shape

static func _arr(kd: Dictionary, k: String) -> PackedFloat32Array:
	return PackedFloat32Array(kd.get(k, []))


func _proto_mesh(kd: Dictionary) -> ArrayMesh:
	var P := _arr(kd, "P")
	if P.size() < 9:
		return null
	var N := _arr(kd, "N")
	var C := _arr(kd, "C")
	var nv := P.size() / 3
	var v := PackedVector3Array()
	var n := PackedVector3Array()
	var c := PackedColorArray()
	v.resize(nv)
	n.resize(nv)
	c.resize(nv)
	for i in nv:
		v[i] = Vector3(P[i * 3], P[i * 3 + 1], P[i * 3 + 2])
		n[i] = Vector3(N[i * 3], N[i * 3 + 1], N[i * 3 + 2]).normalized() if N.size() >= P.size() else Vector3.UP
		c[i] = Color(C[i * 3], C[i * 3 + 1], C[i * 3 + 2]) if C.size() >= P.size() else Color.WHITE
	var arrays := []
	arrays.resize(Mesh.ARRAY_MAX)
	arrays[Mesh.ARRAY_VERTEX] = v
	arrays[Mesh.ARRAY_NORMAL] = n
	arrays[Mesh.ARRAY_COLOR] = c
	var I = kd.get("I")
	if I is Array and not (I as Array).is_empty():
		arrays[Mesh.ARRAY_INDEX] = PackedInt32Array(I)
	var am := ArrayMesh.new()
	am.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arrays)
	var m := StandardMaterial3D.new()
	m.vertex_color_use_as_albedo = true
	m.vertex_color_is_srgb = false     # three.js keeps vertex colours linear
	m.roughness = 0.85
	if String(kd.get("base", "")) == "rock":
		m = _rock_mat()
	am.surface_set_material(0, m)
	# glowing parts (lamps and the like), unlit
	var GP := _arr(kd, "GP")
	var GC := _arr(kd, "GC")
	if GP.size() >= 9:
		var gv := PackedVector3Array()
		var gc := PackedColorArray()
		for i in GP.size() / 3:
			gv.append(Vector3(GP[i * 3], GP[i * 3 + 1], GP[i * 3 + 2]))
			gc.append(Color(GC[i * 3], GC[i * 3 + 1], GC[i * 3 + 2]) if GC.size() >= GP.size() else Color.WHITE)
		var ga := []
		ga.resize(Mesh.ARRAY_MAX)
		ga[Mesh.ARRAY_VERTEX] = gv
		ga[Mesh.ARRAY_COLOR] = gc
		am.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, ga)
		var gm := StandardMaterial3D.new()
		gm.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
		gm.vertex_color_use_as_albedo = true
		gm.vertex_color_is_srgb = false
		am.surface_set_material(1, gm)
	return am


## the shape's size and colours: height, crown radius, trunk and foliage colour, snow
func _proto_info(kd: Dictionary) -> Dictionary:
	var P := _arr(kd, "P")
	var C := _arr(kd, "C")
	var lo := Vector3(1e9, 1e9, 1e9)
	var hi := -lo
	for i in P.size() / 3:
		var p := Vector3(P[i * 3], P[i * 3 + 1], P[i * 3 + 2])
		lo = lo.min(p)
		hi = hi.max(p)
	var h := maxf(1.0, hi.y - maxf(0.0, lo.y))
	var rad := maxf(maxf(absf(lo.x), absf(hi.x)), maxf(absf(lo.z), absf(hi.z)))
	var leaf := Vector3.ZERO
	var nl := 0
	var trunk := Vector3.ZERO
	var nt := 0
	var white := 0
	for i in P.size() / 3:
		if C.size() < P.size():
			break
		var y := P[i * 3 + 1]
		var c := Vector3(C[i * 3], C[i * 3 + 1], C[i * 3 + 2])
		var axis := Vector2(P[i * 3], P[i * 3 + 2]).length()
		if y > 0.45 * h and c.y >= c.x * 0.9:
			leaf += c
			nl += 1
			if c.x > 0.6 and c.y > 0.6 and c.z > 0.6:
				white += 1
		elif y < 0.3 * h and axis < 0.25 * rad:
			trunk += c
			nt += 1
	# the crown's outline: how far the foliage reaches out at each height, so the finished tree keeps the web shape
	var NB := 12
	var cy0 := 1e9
	var cy1 := -1e9
	var fol: Array = []
	for i in P.size() / 3:
		if C.size() < P.size():
			break
		var c2 := Vector3(C[i * 3], C[i * 3 + 1], C[i * 3 + 2])
		var y2 := P[i * 3 + 1]
		if y2 > 0.15 * h and c2.y >= c2.x * 0.9 and maxf(c2.x, maxf(c2.y, c2.z)) > 0.012:
			fol.append(Vector3(P[i * 3], y2, P[i * 3 + 2]))
			cy0 = minf(cy0, y2)
			cy1 = maxf(cy1, y2)
	var prof := PackedFloat32Array()
	prof.resize(NB)
	prof.fill(-1.0)
	if fol.size() >= 8 and cy1 - cy0 > 0.5:
		for q in fol:
			var b := clampi(int(((q as Vector3).y - cy0) / (cy1 - cy0) * NB), 0, NB - 1)
			prof[b] = maxf(prof[b], Vector2((q as Vector3).x, (q as Vector3).z).length())
		# fill gaps from the neighbours; the very top closes to a point
		for b in NB:
			if prof[b] < 0.0:
				var lo2 := -1.0
				var hi2 := -1.0
				for j in range(b - 1, -1, -1):
					if prof[j] >= 0.0:
						lo2 = prof[j]
						break
				for j in range(b + 1, NB):
					if prof[j] >= 0.0:
						hi2 = prof[j]
						break
				prof[b] = maxf(0.0, (lo2 + hi2) * 0.5 if lo2 >= 0.0 and hi2 >= 0.0 else maxf(lo2, hi2))
	else:
		cy0 = h * 0.35
		cy1 = h
		for b in NB:
			prof[b] = rad * sin(PI * (float(b) + 0.5) / NB)
	var lf := (leaf / nl) if nl > 0 else Vector3(0.05, 0.25, 0.04)
	if maxf(lf.x, maxf(lf.y, lf.z)) < 0.012:
		lf = Vector3(0.05, 0.22, 0.04)      # shapes that take their leaf colour from elsewhere: a plain leaf green
	# keep the web game's hue, but never so dark that the leaves' own detail is lost
	var lum := lf.x * 0.2126 + lf.y * 0.7152 + lf.z * 0.0722
	if lum < 0.09:
		lf *= 0.09 / maxf(0.001, lum)
	return {"h": h, "rad": maxf(1.0, rad), "lo": lo, "hi": hi, "leaf": lf, "cy0": cy0, "cy1": cy1, "prof": prof,
		"trunk": (trunk / nt) if nt > 0 else Vector3(0.2, 0.12, 0.06), "snow": clampf(float(white) / maxf(1.0, nl) * 1.6, 0.0, 1.0)}


# ---------------------------------------------------------------- materials

static func _rock_mat() -> StandardMaterial3D:
	if _mats.has("rock"):
		return _mats["rock"]
	var m := StandardMaterial3D.new()
	m.vertex_color_use_as_albedo = true
	m.vertex_color_is_srgb = false
	m.roughness = 0.9
	var col := _t(CC0 + "rock_boulder_dry_col.jpg")
	if col != null:
		m.albedo_texture = col
		m.albedo_color = Color(1.9, 1.9, 1.9)     # the stone's own grey is ~0.5: keep the web's colour, add the stone
		m.normal_enabled = true
		m.normal_texture = _t(CC0 + "rock_boulder_dry_nrm.jpg")
		m.normal_scale = 1.2
		m.roughness_texture = _t(CC0 + "rock_boulder_dry_rgh.jpg")
		m.uv1_triplanar = true
		m.uv1_world_triplanar = true
		m.uv1_scale = Vector3(0.09, 0.09, 0.09)
		m.uv1_triplanar_sharpness = 3.0
	_mats["rock"] = m
	return m


static func _leaf_mat(kind: String, tint: Vector3, snow: float, h: float) -> ShaderMaterial:
	var key := "%s|%s|%.2f|%.0f" % [kind, str(tint.snapped(Vector3.ONE * 0.02)), snow, h]
	if _mats.has(key):
		return _mats[key]
	var tex: String = {"round": "leaves", "bush": "bushleaf", "palm": "frond", "pine": "bough"}[kind]
	var m := ShaderMaterial.new()
	m.shader = load("res://shaders/foliage.gdshader")
	m.set_shader_parameter("tex", _t(HD_DIR + tex + "_col.png"))
	m.set_shader_parameter("nrm", _t(HD_DIR + tex + "_nrm.png"))
	m.set_shader_parameter("tint", tint)
	m.set_shader_parameter("snow", snow)
	m.set_shader_parameter("height", h)
	m.set_shader_parameter("sway", 0.6 if kind == "pine" else (1.4 if kind == "palm" else 1.0))
	m.set_shader_parameter("cut", 0.5 if kind == "pine" else 0.42)
	_mats[key] = m
	return m


static func _bark_mat(kind: String, tint: Vector3) -> StandardMaterial3D:
	var key := "bark|%s|%s" % [kind, str(tint.snapped(Vector3.ONE * 0.02))]
	if _mats.has(key):
		return _mats[key]
	var m := StandardMaterial3D.new()
	var cc := "bark_willow" if kind == "palm" else "bark_brown_02"
	var col := _t(CC0 + cc + "_col.jpg")
	if col == null:
		cc = ""
		col = _t(HD_DIR + ("palmbark" if kind == "palm" else "bark") + "_col.png")
	m.albedo_texture = col
	m.albedo_color = Color(tint.x, tint.y, tint.z)
	m.normal_enabled = true
	m.normal_texture = _t(CC0 + cc + "_nrm.jpg") if cc != "" else _t(HD_DIR + ("palmbark" if kind == "palm" else "bark") + "_nrm.png")
	m.normal_scale = 1.3
	if cc != "":
		m.roughness_texture = _t(CC0 + cc + "_rgh.jpg")
	m.roughness = 0.9
	_mats[key] = m
	return m


## how much to tint a texture so it matches the web game's colour for that part (both in linear light): its
## brightness fully, its hue only partly, so the textures' own natural colour survives
static func _match(web_lin: Vector3, tex_srgb: Color) -> Vector3:
	var t := tex_srgb.srgb_to_linear()
	var lw := web_lin.x * 0.2126 + web_lin.y * 0.7152 + web_lin.z * 0.0722
	var lt := t.r * 0.2126 + t.g * 0.7152 + t.b * 0.0722
	var l := clampf(lw / maxf(0.005, lt), 0.25, 2.5)
	var ratio := Vector3(web_lin.x / maxf(0.005, t.r), web_lin.y / maxf(0.005, t.g), web_lin.z / maxf(0.005, t.b)) / maxf(0.01, l * 1.0)
	ratio = ratio / maxf(0.001, (ratio.x * 0.2126 + ratio.y * 0.7152 + ratio.z * 0.0722))
	var hue := Vector3.ONE.lerp(ratio, 0.3)
	return Vector3(clampf(l * hue.x, 0.15, 3.0), clampf(l * hue.y, 0.15, 3.0), clampf(l * hue.z, 0.15, 3.0))


# ---------------------------------------------------------------- finished models

class Geo:
	var v := PackedVector3Array()
	var n := PackedVector3Array()
	var uv := PackedVector2Array()
	var idx := PackedInt32Array()

	func quad(a: Vector3, b: Vector3, c: Vector3, d: Vector3, na: Vector3, nb: Vector3, nc: Vector3, nd: Vector3, u0: Vector2, u1: Vector2) -> void:
		var i0 := v.size()
		v.append_array([a, b, c, d])
		n.append_array([na, nb, nc, nd])
		uv.append_array([Vector2(u0.x, u1.y), Vector2(u1.x, u1.y), Vector2(u1.x, u0.y), Vector2(u0.x, u0.y)])
		idx.append_array([i0, i0 + 2, i0 + 1, i0, i0 + 3, i0 + 2])     # Godot's front faces wind clockwise

	## a tapering tube along a path of points, with radii; u wraps round it, v runs along it
	func tube(path: Array, radii: Array, sides: int, v_scale: float) -> void:
		var base := v.size()
		var along := 0.0
		for i in path.size():
			var p: Vector3 = path[i]
			var dir: Vector3 = ((path[mini(i + 1, path.size() - 1)] as Vector3) - (path[maxi(i - 1, 0)] as Vector3)).normalized()
			var side := dir.cross(Vector3(0, 0, 1))
			if side.length() < 0.1:
				side = dir.cross(Vector3(1, 0, 0))
			side = side.normalized()
			var up := side.cross(dir).normalized()
			if i > 0:
				along += (p - (path[i - 1] as Vector3)).length()
			for s in sides + 1:
				var a := TAU * float(s) / float(sides)
				var o := side * cos(a) + up * sin(a)
				v.append(p + o * float(radii[i]))
				n.append(o)
				uv.append(Vector2(float(s) / float(sides) * 2.0, along * v_scale))
		for i in path.size() - 1:
			for s in sides:
				var a0 := base + i * (sides + 1) + s
				var b0 := a0 + sides + 1
				idx.append_array([a0, a0 + 1, b0, a0 + 1, b0 + 1, b0])

	func mesh(am: ArrayMesh, mat: Material) -> void:
		if v.is_empty():
			return
		var arr := []
		arr.resize(Mesh.ARRAY_MAX)
		arr[Mesh.ARRAY_VERTEX] = v
		arr[Mesh.ARRAY_NORMAL] = n
		arr[Mesh.ARRAY_TEX_UV] = uv
		arr[Mesh.ARRAY_INDEX] = idx
		# white vertex colours: the instance's tint multiplies them (a mesh without colours reads black on some GPUs)
		var cols := PackedColorArray()
		cols.resize(v.size())
		cols.fill(Color.WHITE)
		arr[Mesh.ARRAY_COLOR] = cols
		var tmp := ArrayMesh.new()
		tmp.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arr)
		# tangents for the relief maps
		var st := SurfaceTool.new()
		st.create_from(tmp, 0)
		st.generate_tangents()
		var arr2 := st.commit_to_arrays()
		am.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arr2)
		am.surface_set_material(am.get_surface_count() - 1, mat)


func _hd_mesh(kind: String, info: Dictionary, kd: Dictionary, key: String) -> Mesh:
	var h: float = info["h"]
	var rad: float = info["rad"]
	var ck := "%s|%.1f|%.1f|%s|%s|%.2f|%d" % [kind, h, rad, str((info["leaf"] as Vector3).snapped(Vector3.ONE * 0.01)), str((info["trunk"] as Vector3).snapped(Vector3.ONE * 0.01)), float(info["snow"]), hash(info.get("prof", PackedFloat32Array()))]
	if _meshes.has(ck):
		return _meshes[ck]
	var rng := RandomNumberGenerator.new()
	rng.seed = hash(ck)
	var am := ArrayMesh.new()
	match kind:
		"rock":
			_meshes[ck] = null
			return null      # rocks keep the web game's shape, with the stone surface (see _proto_mesh)
		"palm":
			_palm(am, info, rng)
		"round":
			_round(am, info, rng)
		"pine":
			_pine(am, info, rng)
		"bush":
			_bush(am, info, rng)
	_meshes[ck] = am
	return am


## a palm: a ringed trunk leaning as it rises, a crown of arching fronds folded along their midribs, coconuts
func _palm(am: ArrayMesh, info: Dictionary, rng: RandomNumberGenerator) -> void:
	var h: float = info["h"]
	var top := h * 0.84
	var lean := h * 0.2
	var trunk := Geo.new()
	var path: Array = []
	var radii: Array = []
	var segs := 16
	for i in segs + 1:
		var t := float(i) / segs
		path.append(Vector3(lean * t * t, top * t, 0.0))
		radii.append(h * (0.042 - 0.016 * t) * (1.0 + 0.18 * pow(1.0 - t, 6.0)))
	trunk.tube(path, radii, 14, 1.0 / (h * 0.09))
	trunk.mesh(am, _bark_mat("palm", _match(info["trunk"], Color(0.55, 0.43, 0.3))))
	var crown := Geo.new()
	var c: Vector3 = path[path.size() - 1]
	var nf := 13
	for f in nf:
		var a := TAU * float(f) / nf + rng.randf_range(-0.15, 0.15)
		var dirh := Vector3(cos(a), 0.0, sin(a))
		var side := Vector3(-sin(a), 0.0, cos(a))
		var L := h * rng.randf_range(0.36, 0.46)
		var rise := rng.randf_range(0.35, 0.9)      # how steeply it leaves the crown
		var segn := 10
		var prev := c
		var wid := L * 0.26
		for s in segn:
			var t0 := float(s) / segn
			var t1 := float(s + 1) / segn
			var p0 := c + dirh * L * t0 + Vector3.UP * L * (rise * t0 - 0.95 * t0 * t0)
			var p1 := c + dirh * L * t1 + Vector3.UP * L * (rise * t1 - 0.95 * t1 * t1)
			var w0 := wid * sin(PI * minf(1.0, t0 * 1.1 + 0.05))
			var w1 := wid * sin(PI * minf(1.0, t1 * 1.1 + 0.05))
			# folded along the midrib: each half tilts down a little
			var down := Vector3.DOWN * 0.35
			var nup := (Vector3.UP * 0.8 + dirh * 0.2).normalized()
			var l0 := p0 + (side + down).normalized() * w0
			var l1 := p1 + (side + down).normalized() * w1
			var r0 := p0 + (-side + down).normalized() * w0
			var r1 := p1 + (-side + down).normalized() * w1
			crown.quad(p0, p1, l1, l0, nup, nup, nup, nup, Vector2(t0, 0.5), Vector2(t1, 0.0))
			crown.quad(r0, r1, p1, p0, nup, nup, nup, nup, Vector2(t0, 1.0), Vector2(t1, 0.5))
			prev = p1
	var tex_avg := Color(0.25, 0.5, 0.17)
	crown.mesh(am, _leaf_mat("palm", _match(info["leaf"], tex_avg) * 0.68, float(info["snow"]), h))
	# coconuts
	var nuts := Geo.new()
	for k in 5:
		var a2 := TAU * k / 5.0 + rng.randf()
		var cp := c + Vector3(cos(a2), -0.6, sin(a2)) * h * 0.035
		_sphere(nuts, cp, h * 0.026, 8, 6)
	var nm := StandardMaterial3D.new()
	nm.albedo_color = Color(0.25, 0.16, 0.08)
	nm.roughness = 0.6
	nuts.mesh(am, nm)


## a broadleaf tree: a trunk forking into a few boughs inside a crown of leaf clusters, the crown filling the web
## shape's own outline (tall and slender on the bay, rounder elsewhere)
func _round(am: ArrayMesh, info: Dictionary, rng: RandomNumberGenerator) -> void:
	var h: float = info["h"]
	var rad: float = info["rad"]
	var y0: float = info["cy0"]
	var y1: float = info["cy1"]
	var prof: PackedFloat32Array = info["prof"]
	var span := maxf(0.5, y1 - y0)
	var rmax := 0.3
	for r0 in prof:
		rmax = maxf(rmax, r0)
	var r_at := func(y: float) -> float:
		var t := clampf((y - y0) / span * prof.size() - 0.5, 0.0, prof.size() - 1.0)
		var i0 := int(floor(t))
		var i1 := mini(i0 + 1, prof.size() - 1)
		return lerpf(prof[i0], prof[i1], t - i0)
	var trunk := Geo.new()
	var tp: Array = []
	var tr: Array = []
	var ttop := y0 + span * 0.45
	var tw := clampf(rmax * 0.13, h * 0.02, h * 0.05)
	for i in 7:
		var t := float(i) / 6.0
		tp.append(Vector3(sin(t * 2.0) * tw * 0.4, ttop * t, cos(t * 1.7) * tw * 0.3))
		tr.append(tw * (1.0 - 0.45 * t) * (1.0 + 0.4 * pow(1.0 - t, 8.0)))
	trunk.tube(tp, tr, 10, 1.0 / (h * 0.12))
	var fork: Vector3 = tp[2]
	for b in 4:
		var a := TAU * b / 4.0 + rng.randf_range(-0.3, 0.3)
		var by := lerpf(y0, y1, rng.randf_range(0.35, 0.7))
		var end: Vector3 = Vector3(cos(a), 0.0, sin(a)) * float(r_at.call(by)) * 0.55 + Vector3.UP * by
		var mid := fork.lerp(end, 0.5) + Vector3.UP * span * 0.05
		trunk.tube([fork, mid, end], [tw * 0.55, tw * 0.38, tw * 0.15], 7, 1.0 / (h * 0.12))
	trunk.mesh(am, _bark_mat("round", _match(info["trunk"], Color(0.42, 0.33, 0.25))))
	var crown := Geo.new()
	var cc := Vector3(0, (y0 + y1) * 0.5, 0)
	var csize := clampf(rmax * 0.95, rad * 0.3, rad * 0.65)
	# enough clusters to close the outline's surface
	var area := 0.0
	for b in prof.size():
		area += TAU * maxf(0.3, prof[b]) * span / prof.size()
	var n := clampi(int(area / (csize * csize * 0.42)), 50, 170)
	var placed := 0
	var tries := 0
	while placed < n and tries < n * 20:
		tries += 1
		var y := lerpf(y0 - span * 0.04, y1 - span * 0.03, rng.randf())
		var ry := float(r_at.call(y))
		# denser where the crown is wider (more surface there)
		if rng.randf() * rmax > maxf(ry, rmax * 0.15):
			continue
		var a2 := rng.randf() * TAU
		var rr := ry * (0.4 + 0.6 * pow(rng.randf(), 0.3))
		var p := Vector3(cos(a2) * rr, y, sin(a2) * rr)
		var out := (Vector3(p.x, 0.0, p.z).normalized() * 0.8 + (p - cc).normalized() * 0.5).normalized()
		var size := clampf(maxf(ry, rmax * 0.4) * rng.randf_range(0.75, 1.05), csize * 0.55, csize * 1.1)
		_card(crown, p, out, size, rng, Vector3(0, y, 0).lerp(cc, 0.35))
		placed += 1
	crown.mesh(am, _leaf_mat("round", _match(info["leaf"], Color(0.27, 0.52, 0.2)), float(info["snow"]), h))


## a conifer: a straight trunk and whorls of drooping boughs, each tier reaching as far as the web shape's own
## outline at that height (slender spruces on the bay, broad pines in the freezer)
func _pine(am: ArrayMesh, info: Dictionary, rng: RandomNumberGenerator) -> void:
	var h: float = info["h"]
	var rad: float = info["rad"]
	var y0: float = info["cy0"]
	var y1: float = info["cy1"]
	var prof: PackedFloat32Array = info["prof"]
	var span := maxf(0.5, y1 - y0)
	var rmax := 0.3
	for r0 in prof:
		rmax = maxf(rmax, r0)
	var trunk := Geo.new()
	var tw := clampf(rmax * 0.1, h * 0.012, h * 0.035)
	trunk.tube([Vector3.ZERO, Vector3(0, y0 + span * 0.5, 0), Vector3(0, y1 * 0.99, 0)], [tw, tw * 0.6, tw * 0.1], 9, 1.0 / (h * 0.1))
	trunk.mesh(am, _bark_mat("pine", _match(info["trunk"], Color(0.42, 0.33, 0.25))))
	var crown := Geo.new()
	var tiers := clampi(int(span / maxf(0.4, rmax * 0.42)), 8, 18)
	for t in tiers:
		var f := float(t) / (tiers - 1)
		var y := lerpf(y0 + span * 0.02, y1 - span * 0.02, f)
		var ti := clampf((y - y0) / span * prof.size() - 0.5, 0.0, prof.size() - 1.0)
		var i0 := int(floor(ti))
		var R := lerpf(prof[i0], prof[mini(i0 + 1, prof.size() - 1)], ti - i0)
		# the drooping tips hang below the tier, so reach a little further than the outline at the root
		R = maxf(R * 1.08, rmax * 0.12)
		var nb := clampi(int(R / maxf(0.3, rmax) * 9.0) + 3, 4, 10)
		var off := rng.randf() * TAU
		for b in nb:
			var a := off + TAU * b / nb + rng.randf_range(-0.22, 0.22)
			var dir := Vector3(cos(a), 0.0, sin(a))
			var L := R * rng.randf_range(0.9, 1.08)
			var root := Vector3(0, y + span * 0.02, 0)
			var tip := root + dir * L + Vector3.DOWN * L * rng.randf_range(0.3, 0.5)
			var mid := root.lerp(tip, 0.5) + Vector3.UP * L * 0.07
			var side := Vector3(-sin(a), 0.0, cos(a))
			var w := maxf(L * 0.55, span * 0.06)
			var nrm := (dir * 0.6 + Vector3.UP * 0.8).normalized()
			# the bough as two flat strips (root to middle, middle to tip), with a second one tipped up across it
			for half in 2:
				var pa := root if half == 0 else mid
				var pb := mid if half == 0 else tip
				var ua := 0.0 if half == 0 else 0.5
				var ub := 0.5 if half == 0 else 1.0
				crown.quad(pa - side * w * 0.5, pb - side * w * 0.5, pb + side * w * 0.5, pa + side * w * 0.5, nrm, nrm, nrm, nrm, Vector2(ua, 1.0), Vector2(ub, 0.0))
				var up2 := (side * 0.35 + Vector3.UP).normalized() * w * 0.32
				crown.quad(pa - up2, pb - up2, pb + up2, pa + up2, nrm, nrm, nrm, nrm, Vector2(ua, 0.82), Vector2(ub, 0.18))
	# a spike of fresh growth at the very top
	var tipy := y1
	crown.quad(Vector3(-rmax * 0.15, tipy - span * 0.1, 0), Vector3(-rmax * 0.02, tipy + span * 0.02, 0), Vector3(rmax * 0.02, tipy + span * 0.02, 0), Vector3(rmax * 0.15, tipy - span * 0.1, 0),
		Vector3.UP, Vector3.UP, Vector3.UP, Vector3.UP, Vector2(0.0, 1.0), Vector2(1.0, 0.0))
	# the cards let light through and wrap it round: a shade darker keeps the web game's deep green
	crown.mesh(am, _leaf_mat("pine", _match(info["leaf"], Color(0.19, 0.4, 0.22)) * 0.78, float(info["snow"]), h))


## a bush: leaf clusters heaped into a low dome
func _bush(am: ArrayMesh, info: Dictionary, rng: RandomNumberGenerator) -> void:
	var h: float = info["h"]
	var rad: float = info["rad"]
	var crown := Geo.new()
	var cc := Vector3(0, h * 0.42, 0)
	for i in 34:
		var dir := Vector3(rng.randf_range(-1, 1), rng.randf_range(-0.3, 1), rng.randf_range(-1, 1)).normalized()
		var p := cc + Vector3(dir.x * rad * 0.85, dir.y * h * 0.5, dir.z * rad * 0.85) * (0.4 + 0.6 * pow(rng.randf(), 0.4))
		p.y = maxf(p.y, h * 0.12)
		_card(crown, p, (p - cc).normalized(), rad * rng.randf_range(0.55, 0.8), rng, cc)
	crown.mesh(am, _leaf_mat("bush", _match(info["leaf"], Color(0.27, 0.52, 0.2)), float(info["snow"]), h))


## one leaf-cluster card, facing roughly outwards; its normals lean out from the crown's centre
func _card(g: Geo, p: Vector3, out: Vector3, size: float, rng: RandomNumberGenerator, cc: Vector3) -> void:
	var nrm := (out + Vector3(rng.randf_range(-0.6, 0.6), rng.randf_range(-0.3, 0.6), rng.randf_range(-0.6, 0.6))).normalized()
	var t1 := nrm.cross(Vector3.UP)
	if t1.length() < 0.1:
		t1 = nrm.cross(Vector3.RIGHT)
	t1 = t1.normalized().rotated(nrm, rng.randf() * TAU)
	var t2 := nrm.cross(t1).normalized()
	var s := size * 0.5
	var corners := [p - t1 * s - t2 * s, p + t1 * s - t2 * s, p + t1 * s + t2 * s, p - t1 * s + t2 * s]
	var ns: Array = []
	for q in corners:
		ns.append(((q as Vector3) - cc).normalized().lerp(out, 0.4).normalized())
	g.quad(corners[0], corners[1], corners[2], corners[3], ns[0], ns[1], ns[2], ns[3], Vector2(0, 0), Vector2(1, 1))


func _sphere(g: Geo, c: Vector3, r: float, seg: int, rings: int) -> void:
	var base := g.v.size()
	for i in rings + 1:
		var th := PI * float(i) / rings
		for s in seg + 1:
			var ph := TAU * float(s) / seg
			var nn := Vector3(sin(th) * cos(ph), cos(th), sin(th) * sin(ph))
			g.v.append(c + nn * r)
			g.n.append(nn)
			g.uv.append(Vector2(float(s) / seg, float(i) / rings))
	for i in rings:
		for s in seg:
			var a := base + i * (seg + 1) + s
			var b := a + seg + 1
			g.idx.append_array([a, a + 1, b, a + 1, b + 1, b])
