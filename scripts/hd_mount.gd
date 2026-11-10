class_name HdMount
## The PC build's background mountains (Settings > Graphics > Finished models). Drawing only.
## - The far mountain ranges (web mountainRing: a ring of 480 x 30 points, coloured grass, rock and snow by height and
##   slope) are rebuilt from the web's own heights with nine times the points and finer ridges and gullies cut into them
##   (stronger where the land is high, nothing at the foot), so the skyline is the web's but the faces read as real
##   rock: crags from a CC0 cliff texture laid over the world, rock showing on the steep faces, snow left smooth.
## - The sculpted mountains (the user's own mountain model, which the web scatters decimated to 3,500 points) are
##   rebuilt from the full model's height field with ~20 times the triangles, lit from a detailed map of the model's
##   surface, so every ridge and gully of the original shows.

const H_MAP := "res://assets/hd/mount_h.png"
const N_MAP := "res://assets/hd/mount_nrm.jpg"
const C_MAP := "res://assets/hd/mount_col.jpg"
const CC0 := "res://assets/hd/cc0/"
const TOP := 347.57         # the model's height, in its own units
const HN := 1024

static var _h := PackedFloat32Array()
static var _mats := {}


static func upgrade(root: Node, level: int, theme: String) -> Dictionary:
	var st := {"rings": 0, "mounts": 0}
	if level < 1:
		return st
	for node in root.find_children("*", "MeshInstance3D", true, false):
		var mi := node as MeshInstance3D
		if mi.mesh == null:
			continue
		# a cell's mesh can hold several surfaces: rebuild the ones that are mountains, keep the rest as they are
		var out: Array = []
		var changed := false
		for si in mi.mesh.get_surface_count():
			var arr := mi.mesh.surface_get_arrays(si)
			var mat := mi.mesh.surface_get_material(si)
			var nm: ArrayMesh = null
			var V: PackedVector3Array = arr[Mesh.ARRAY_VERTEX]
			if V.size() >= 1500 and mi.mesh.surface_get_primitive_type(si) == Mesh.PRIMITIVE_TRIANGLES:
				var C = arr[Mesh.ARRAY_COLOR]
				var U = arr[Mesh.ARRAY_TEX_UV]
				if C is PackedColorArray and (C as PackedColorArray).size() == V.size() and V.size() >= 5000:
					nm = _ring(V, C, mat, level)
					if nm != null:
						st["rings"] += 1
				if nm == null and U is PackedVector2Array and (U as PackedVector2Array).size() == V.size() and V.size() <= 12000 and mat is StandardMaterial3D and (mat as StandardMaterial3D).albedo_texture != null:
					nm = _mount(V, U, mat as StandardMaterial3D, theme)
					if nm != null:
						st["mounts"] += 1
			if nm != null:
				changed = true
				out.append([nm.surface_get_arrays(0), nm.surface_get_material(0)])
			else:
				out.append([arr, mat])
		if not changed:
			continue
		var am := ArrayMesh.new()
		for e in out:
			am.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, e[0])
			am.surface_set_material(am.get_surface_count() - 1, e[1])
		mi.mesh = am
		mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	return st


# ---------------------------------------------------------------- the far ranges

## the web ring's heights and colours back on their grid (angle k of AS, row i of RS), then rebuilt finely
static func _ring(V: PackedVector3Array, C: PackedColorArray, mat: Material, level: int) -> ArrayMesh:
	var n := V.size()
	var r0 := 1e9
	var r1 := 0.0
	var ymin := 1e9
	for p in V:
		var r := Vector2(p.x, p.z).length()
		r0 = minf(r0, r)
		r1 = maxf(r1, r)
		ymin = minf(ymin, p.y)
	if r1 - r0 < 800.0 or r0 < 1500.0:
		return null
	# which angular step: almost every point sits on a whole step
	var AS := 0
	for cand in [480, 360, 240]:
		var ok := 0
		var tried := 0
		for j in range(0, n, maxi(1, n / 400)):
			tried += 1
			var a: float = fposmod(atan2(V[j].z, V[j].x), TAU) / TAU * float(cand)
			if absf(a - roundf(a)) < 0.02:
				ok += 1
		if ok >= tried * 0.9:
			AS = cand
			break
	if AS == 0:
		return null
	# how many rows: every point sits on a whole row
	var RS := 0
	for cand in [30, 22, 16, 40]:
		var ok2 := 0
		var tried2 := 0
		for j in range(0, n, maxi(1, n / 400)):
			tried2 += 1
			var t: float = (Vector2(V[j].x, V[j].z).length() - r0) / (r1 - r0) * float(cand)
			if absf(t - roundf(t)) < 0.03:
				ok2 += 1
		if ok2 >= tried2 * 0.9:
			RS = cand
			break
	if RS == 0:
		return null
	var H := PackedFloat32Array()
	H.resize((RS + 1) * AS)
	H.fill(NAN)
	var CG := PackedColorArray()
	CG.resize((RS + 1) * AS)
	for j in n:
		var p := V[j]
		var k := posmod(roundi(fposmod(atan2(p.z, p.x), TAU) / TAU * AS), AS)
		var i := clampi(roundi((Vector2(p.x, p.z).length() - r0) / (r1 - r0) * RS), 0, RS)
		H[i * AS + k] = p.y
		CG[i * AS + k] = C[j]
	for q in H.size():
		if is_nan(H[q]):
			H[q] = ymin
	# the web's finest ridge octave aliases into needles at its spacing: soften it round the ring before the
	# finer detail goes on
	var Hs := H.duplicate()
	for i in RS + 1:
		for k in AS:
			Hs[i * AS + k] = H[i * AS + posmod(k - 1, AS)] * 0.25 + H[i * AS + k] * 0.5 + H[i * AS + posmod(k + 1, AS)] * 0.25
	H = Hs
	var base := ymin
	var hmax := base
	for q in H.size():
		hmax = maxf(hmax, H[q])
	var span := maxf(1.0, hmax - base)
	var f := 3 if level >= 2 else 2
	var A2 := AS * f
	var R2 := RS * f
	var rid := FastNoiseLite.new()
	rid.noise_type = FastNoiseLite.TYPE_SIMPLEX_SMOOTH
	rid.fractal_type = FastNoiseLite.FRACTAL_RIDGED
	rid.fractal_octaves = 5
	rid.frequency = 1.0 / 760.0
	rid.seed = 11
	var wob := FastNoiseLite.new()
	wob.frequency = 1.0 / 900.0
	wob.seed = 5
	var pos := PackedVector3Array()
	var col := PackedColorArray()
	pos.resize((R2 + 1) * (A2 + 1))
	col.resize(pos.size())
	for i in R2 + 1:
		var ti := float(i) / f
		var r := r0 + (r1 - r0) * float(i) / R2
		for k in A2 + 1:
			var tk := float(k) / f
			var a := float(k) / A2 * TAU
			var h := _bicubic(H, AS, RS, ti, tk)
			var x := cos(a) * r
			var z := sin(a) * r
			# finer ridges and gullies, in proportion to how high the land is here (the foot stays put)
			var lift := clampf((h - base) / span, 0.0, 1.0)
			var wx := x + wob.get_noise_2d(x, z) * 260.0
			var wz := z + wob.get_noise_2d(z + 777.0, x) * 260.0
			var d := rid.get_noise_2d(wx, wz)
			h += d * span * 0.055 * lift * (0.35 + 0.65 * lift)
			pos[i * (A2 + 1) + k] = Vector3(x, h, z)
			col[i * (A2 + 1) + k] = _bilin_c(CG, AS, RS, ti, tk)
	var idx := PackedInt32Array()
	for i in R2:
		for k in A2:
			var p0 := i * (A2 + 1) + k
			# clockwise seen from above (Godot's front faces): outward first, then round
			idx.append_array([p0, p0 + A2 + 1, p0 + 1, p0 + 1, p0 + A2 + 1, p0 + A2 + 2])
	var nrm := PackedVector3Array()
	nrm.resize(pos.size())
	for i in R2 + 1:
		for k in A2 + 1:
			var c0 := i * (A2 + 1) + k
			var kl := c0 - 1 if k > 0 else i * (A2 + 1) + A2 - 1
			var kr := c0 + 1 if k < A2 else i * (A2 + 1) + 1
			var iu := c0 - (A2 + 1) if i > 0 else c0
			var id := c0 + (A2 + 1) if i < R2 else c0
			var ta := pos[kr] - pos[kl]
			var tr := pos[id] - pos[iu]
			var nn := ta.cross(tr).normalized()
			if nn.y < 0.0:
				nn = -nn
			nrm[c0] = nn
	var arr := []
	arr.resize(Mesh.ARRAY_MAX)
	arr[Mesh.ARRAY_VERTEX] = pos
	arr[Mesh.ARRAY_NORMAL] = nrm
	arr[Mesh.ARRAY_COLOR] = col
	arr[Mesh.ARRAY_INDEX] = idx
	var am := ArrayMesh.new()
	am.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arr)
	am.surface_set_material(0, _ring_mat(mat))
	return am


static func _cr(p0: float, p1: float, p2: float, p3: float, t: float) -> float:
	return 0.5 * ((2.0 * p1) + (-p0 + p2) * t + (2.0 * p0 - 5.0 * p1 + 4.0 * p2 - p3) * t * t + (-p0 + 3.0 * p1 - 3.0 * p2 + p3) * t * t * t)


## smooth (Catmull-Rom) between the web's points; round the ring it wraps
static func _bicubic(H: PackedFloat32Array, AS: int, RS: int, ti: float, tk: float) -> float:
	var i1 := int(floorf(ti))
	var k1 := int(floorf(tk))
	var fi: float = ti - float(i1)
	var fk: float = tk - float(k1)
	var rows := PackedFloat32Array()
	rows.resize(4)
	for a in 4:
		var ii := clampi(i1 - 1 + a, 0, RS)
		var b0 := H[ii * AS + posmod(k1 - 1, AS)]
		var b1 := H[ii * AS + posmod(k1, AS)]
		var b2 := H[ii * AS + posmod(k1 + 1, AS)]
		var b3 := H[ii * AS + posmod(k1 + 2, AS)]
		rows[a] = _cr(b0, b1, b2, b3, fk)
	return _cr(rows[0], rows[1], rows[2], rows[3], fi)


static func _bilin_c(C: PackedColorArray, AS: int, RS: int, ti: float, tk: float) -> Color:
	var i0 := clampi(int(floorf(ti)), 0, RS)
	var i1 := mini(i0 + 1, RS)
	var k0 := posmod(int(floorf(tk)), AS)
	var k1 := posmod(k0 + 1, AS)
	var fi: float = ti - floorf(ti)
	var fk: float = tk - floorf(tk)
	var a: Color = C[i0 * AS + k0].lerp(C[i0 * AS + k1], fk)
	var b: Color = C[i1 * AS + k0].lerp(C[i1 * AS + k1], fk)
	return a.lerp(b, fi)


static func _tex(path: String) -> Texture2D:
	return load(path) if ResourceLoader.exists(path) else null


## the ring's own vertex colours, with crags and rock from a CC0 cliff texture laid over the world
static func _ring_mat(orig: Material) -> Material:
	var key := "ring|%d" % (orig.get_instance_id() if orig != null else 0)
	if _mats.has(key):
		return _mats[key]
	var m := ShaderMaterial.new()
	m.shader = load("res://shaders/mountain_ring.gdshader")
	var om := orig as StandardMaterial3D
	m.set_shader_parameter("tint", Vector3(om.albedo_color.r, om.albedo_color.g, om.albedo_color.b) if om != null else Vector3.ONE)
	m.set_shader_parameter("srgb_vc", om.vertex_color_is_srgb if om != null else false)
	m.set_shader_parameter("rough", om.roughness if om != null else 0.95)
	var cc := "cliff_side"
	var rc := _tex(CC0 + cc + "_col.jpg")
	m.set_shader_parameter("rock", rc)
	m.set_shader_parameter("rock_n", _tex(CC0 + cc + "_nrm.jpg"))
	m.set_shader_parameter("has_rock", rc != null)
	_mats[key] = m
	return m


# ---------------------------------------------------------------- the sculpted mountains

static func _load_h() -> bool:
	if not _h.is_empty():
		return true
	var tex := _tex(H_MAP)
	var img: Image = tex.get_image() if tex != null else null
	if img == null:
		return false
	if img.is_compressed():
		img.decompress()
	img.convert(Image.FORMAT_RGB8)
	if img.get_width() != HN or img.get_height() != HN:
		return false
	var data := img.get_data()
	_h.resize(HN * HN)
	for q in HN * HN:
		_h[q] = float(data[q * 3] * 256 + data[q * 3 + 1]) / 65535.0
	return true


## the model's height (0..1) at u, v (the web's v), smoothly
static func _hat(u: float, v: float) -> float:
	var x := clampf(u, 0.0, 1.0) * (HN - 1)
	var y := clampf(v, 0.0, 1.0) * (HN - 1)
	var x0 := mini(int(x), HN - 2)
	var y0 := mini(int(y), HN - 2)
	var fx := x - x0
	var fy := y - y0
	var a := lerpf(_h[y0 * HN + x0], _h[y0 * HN + x0 + 1], fx)
	var b := lerpf(_h[(y0 + 1) * HN + x0], _h[(y0 + 1) * HN + x0 + 1], fx)
	return lerpf(a, b, fy)


## least squares: value = c0*u + c1*v + c2 over the points
static func _fit_plane(U: PackedVector2Array, vals: PackedFloat32Array, ids: PackedInt32Array) -> Array:
	var s := [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]   # uu uv u vv v n
	var b := [0.0, 0.0, 0.0]
	for j in ids:
		var u := U[j].x
		var v := U[j].y
		var w := vals[j]
		s[0] += u * u
		s[1] += u * v
		s[2] += u
		s[3] += v * v
		s[4] += v
		s[5] += 1.0
		b[0] += u * w
		b[1] += v * w
		b[2] += w
	var M := Basis(Vector3(s[0], s[1], s[2]), Vector3(s[1], s[3], s[4]), Vector3(s[2], s[4], s[5]))
	if absf(M.determinant()) < 1e-9:
		return []
	var c := M.inverse() * Vector3(b[0], b[1], b[2])
	return [c.x, c.y, c.z]


static func _mount(V: PackedVector3Array, U: PackedVector2Array, om: StandardMaterial3D, theme: String) -> ArrayMesh:
	if not _load_h():
		return null
	var n := V.size()
	var ids := PackedInt32Array()
	for j in range(0, n, maxi(1, n / 600)):
		ids.append(j)
	var xs := PackedFloat32Array()
	var zs := PackedFloat32Array()
	var ys := PackedFloat32Array()
	var hs := PackedFloat32Array()
	xs.resize(n)
	zs.resize(n)
	ys.resize(n)
	hs.resize(n)
	for j in n:
		xs[j] = V[j].x
		zs[j] = V[j].z
		ys[j] = V[j].y
	var fx := _fit_plane(U, xs, ids)
	var fz := _fit_plane(U, zs, ids)
	if fx.is_empty() or fz.is_empty():
		return null
	# a planar map: x and z follow u and v exactly, by a turn and an even scale
	var err := 0.0
	for j in ids:
		err = maxf(err, absf(fx[0] * U[j].x + fx[1] * U[j].y + fx[2] - xs[j]) + absf(fz[0] * U[j].x + fz[1] * U[j].y + fz[2] - zs[j]))
	var au := Vector2(fx[0], fz[0])
	var av := Vector2(fx[1], fz[1])
	if err > 2.0 or au.length() < 500.0 or absf(au.length() - av.length()) > au.length() * 0.02 or absf(au.dot(av)) > au.length() * av.length() * 0.02:
		return null
	# the height: y = A * h + y0, with the full model's heights
	for j in n:
		hs[j] = _hat(U[j].x, U[j].y)
	var sh := 0.0
	var shh := 0.0
	var sy := 0.0
	var shy := 0.0
	for j in ids:
		sh += hs[j]
		shh += hs[j] * hs[j]
		sy += ys[j]
		shy += hs[j] * ys[j]
	var cnt := float(ids.size())
	var den := cnt * shh - sh * sh
	if absf(den) < 1e-9:
		return null
	var A := (cnt * shy - sh * sy) / den
	var y0 := (sy - A * sh) / cnt
	if A <= 0.0:
		return null
	var G := 256
	var pos := PackedVector3Array()
	var uv := PackedVector2Array()
	pos.resize((G + 1) * (G + 1))
	uv.resize(pos.size())
	for i in G + 1:
		var v := float(i) / G
		for k in G + 1:
			var u := float(k) / G
			pos[i * (G + 1) + k] = Vector3(fx[0] * u + fx[1] * v + fx[2], A * _hat(u, v) + y0, fz[0] * u + fz[1] * v + fz[2])
			uv[i * (G + 1) + k] = Vector2(u, v)
	var idx := PackedInt32Array()
	# wind each triangle clockwise seen from above (Godot's front faces), whichever way the map is turned
	var cw := au.cross(av) > 0.0
	for i in G:
		for k in G:
			var p0 := i * (G + 1) + k
			if cw:
				idx.append_array([p0, p0 + 1, p0 + G + 1, p0 + 1, p0 + G + 2, p0 + G + 1])
			else:
				idx.append_array([p0, p0 + G + 1, p0 + 1, p0 + 1, p0 + G + 1, p0 + G + 2])
	var nrm := PackedVector3Array()
	nrm.resize(pos.size())
	nrm.fill(Vector3.UP)
	var arr := []
	arr.resize(Mesh.ARRAY_MAX)
	arr[Mesh.ARRAY_VERTEX] = pos
	arr[Mesh.ARRAY_NORMAL] = nrm
	arr[Mesh.ARRAY_TEX_UV] = uv
	arr[Mesh.ARRAY_INDEX] = idx
	var am := ArrayMesh.new()
	am.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arr)
	var m := ShaderMaterial.new()
	m.shader = load("res://shaders/mountain.gdshader")
	var col := _tex(C_MAP)
	m.set_shader_parameter("col", col if col != null else om.albedo_texture)
	m.set_shader_parameter("nrm", _tex(N_MAP))
	m.set_shader_parameter("tint", Vector3(om.albedo_color.r, om.albedo_color.g, om.albedo_color.b))
	m.set_shader_parameter("ax", au)
	m.set_shader_parameter("az", av)
	m.set_shader_parameter("hs", A * 2000.0 / TOP)
	m.set_shader_parameter("snow", 0.9 if theme == "freezer" else 0.0)
	am.surface_set_material(0, m)
	return am
