class_name HdSet
## The PC's finished set pieces (Settings > Graphics > Finished models): the web game's hand-built buildings that
## read as painted boxes are taken out of the track and built again properly, in the same spots, the same size and
## the same colours. Drawing only: none of them is anything a kart can touch.
##
##   Pineapple Lagoon  the five beach huts on stilts (lap boarding, shingled hip roofs, porches and railings,
##                     framed windows with shutters, panelled doors) and the long timber pier.

static var _noise: NoiseTexture2D
static var _wood_sh: Shader
static var _mats := {}


static func upgrade(root: Node3D, T: TrackData) -> int:
	match T.id:
		"lagoon":
			return _lagoon(root, T)
	return 0


# ---------------------------------------------------------------- Pineapple Lagoon

## web bayExtras, VAR 1: huts at atA(2.9 + i*.09, R+420) facing the middle, the pier at atA(2.6, R+500)
static func _lagoon(root: Node3D, T: TrackData) -> int:
	var cols := ["#ff6fae", "#2fd0ff", "#f7c948", "#3f9a35", "#ff8a1f"]
	var huts: Array = []
	for i in 5:
		var a := 2.9 + i * 0.09
		huts.append(_facing(Vector3(cos(a) * (T.R + 420.0), -14.0, sin(a) * (T.R + 420.0))))
	var pa := 2.6
	var pier := _facing(Vector3(cos(pa) * (T.R + 500.0), -14.0, sin(pa) * (T.R + 500.0)))
	# take the web's boxes out
	var boxes: Array = []
	for h in huts:
		boxes.append([h, Vector3(0, 80, 2), Vector3(62, 96, 66)])
	boxes.append([pier, Vector3(0, 10, -512), Vector3(90, 50, 342)])
	var cut := cut_boxes(root, boxes)
	var g := Node3D.new()
	g.name = "hd_lagoon"
	root.add_child(g)
	for i in 5:
		_hut(g, huts[i], Color(cols[i]), i)
	_pier(g, pier)
	return cut


## a frame at p whose +z faces the middle of the map (three's Object3D.lookAt)
static func _facing(p: Vector3) -> Transform3D:
	var z := (Vector3(0, p.y, 0) - p).normalized()
	var x := Vector3.UP.cross(z).normalized()
	return Transform3D(Basis(x, Vector3.UP, z), p)


static func _hut(parent: Node3D, xf: Transform3D, col: Color, seed_: int) -> void:
	var k := Kit.new()
	var white := "trim"
	# stilts in the water, bearers and the deck with its front porch
	for x in [-42.0, 0.0, 42.0]:
		for z in [-38.0, 0.0, 38.0, 62.0]:
			k.cyl("pile", Vector3(x, -30, z), Vector3(x, 8.5, z), 3.0, 12)
	for z in [-38.0, 0.0, 38.0, 62.0]:
		k.box("pile", Vector3(0, 6.5, z), Vector3(92, 4, 4))
	k.box("deck", Vector3(0, 9.5, 11), Vector3(98, 2.4, 112))
	# steps down to the water at the front
	for s in 3:
		k.box("deck", Vector3(0, 6.4 - s * 3.0, 70 + s * 6.0), Vector3(30, 1.8, 6))
	for sd in [-1.0, 1.0]:
		k.box("deck", Vector3(sd * 15.5, 3.0, 76), Vector3(1.6, 8, 20))
	# porch railing round the front and sides of the porch (an opening for the steps)
	var rail_y := [19.0, 31.0]
	for x in [-47.0, -32.0, -17.0, 17.0, 32.0, 47.0]:
		k.box(white, Vector3(x, 21, 65.5), Vector3(2.4, 22, 2.4))
	for sd in [-1.0, 1.0]:
		k.box(white, Vector3(sd * 47, 21, 50), Vector3(2.4, 22, 2.4))
		for y in rail_y:
			k.box(white, Vector3(sd * 32, y, 65.5), Vector3(30, 1.8 if y < 25.0 else 2.4, 1.8))
			k.box(white, Vector3(sd * 47, y, 54), Vector3(1.8, 1.8 if y < 25.0 else 2.4, 23))
		# balusters
		for b in 6:
			k.box(white, Vector3(sd * (20.0 + b * 4.6), 20, 65.5), Vector3(1.0, 20, 1.0))
	# the walls: lap boards in the hut's colour
	k.box("siding", Vector3(0, 48, 0), Vector3(80, 76, 72))
	# corner boards, skirting and frieze
	for sx in [-1.0, 1.0]:
		for sz in [-1.0, 1.0]:
			k.box(white, Vector3(sx * 40, 48, sz * 36), Vector3(4.2, 76, 4.2))
	k.box(white, Vector3(0, 12.6, 0), Vector3(81.6, 4.2, 73.6))
	k.box(white, Vector3(0, 82.5, 0), Vector3(81.6, 7, 73.6))
	# front: a panelled door with a porthole, and a small window either side
	_frame(k, Vector3(0, 0, 36), Vector3.RIGHT, Vector3.BACK, 0.0, 10.5, 30.0, 56.0, 3.0)
	k.box("door", Vector3(0, 38.5, 36.6), Vector3(26, 52, 1.6))
	for px in [-6.5, 6.5]:
		for py in [22.0, 38.0]:
			k.box("door", Vector3(px, py, 37.6), Vector3(9, 13, 0.8))
	k.cyl(white, Vector3(0, 55, 37.0), Vector3(0, 55, 38.6), 6.2, 24)
	k.cyl("glass", Vector3(0, 55, 37.4), Vector3(0, 55, 38.9), 4.6, 24)
	k.sphere("brass", Vector3(9.5, 38, 38.6), 1.5)
	for wx in [-28.0, 28.0]:
		_window(k, Vector3(wx, 0, 36), Vector3.RIGHT, Vector3.BACK, 44.0, 14.0, 20.0, false)
	# sides: a shuttered window each; back: one more
	for sd in [-1.0, 1.0]:
		_window(k, Vector3(sd * 40, 0, 0), Vector3(0, 0, -sd), Vector3(sd, 0, 0), 40.0, 26.0, 28.0, true)
	_window(k, Vector3(-6, 0, -36), Vector3.LEFT, Vector3.FORWARD, 42.0, 20.0, 24.0, false)
	# a lantern by the door and a life ring on the wall
	k.box("iron", Vector3(-17.5, 60, 37.6), Vector3(1.2, 1.2, 3))
	k.box("iron", Vector3(-17.5, 56, 39.2), Vector3(4.4, 7.5, 4.4))
	k.box("lamp", Vector3(-17.5, 56, 39.2), Vector3(3.2, 6, 3.2))
	k.ring("ring_red", "ring_white", Vector3(26, 52, -37.9), Vector3.FORWARD, 6.0, 1.9)
	# the roof: a shingled hip roof over deep eaves, with fascia, soffit, hip caps and the web's finial
	var e0 := 86.0
	var hx := 49.0
	var hz := 45.0
	var top := 136.0
	var rl := 6.0
	var A := Vector3(-hx, e0, hz)
	var B := Vector3(hx, e0, hz)
	var C := Vector3(hx, e0, -hz)
	var D := Vector3(-hx, e0, -hz)
	var R0 := Vector3(-rl, top, 0)
	var R1 := Vector3(rl, top, 0)
	k.quad("roof", A, B, R1, R0)
	k.quad("roof", C, D, R0, R1)
	k.tri("roof", B, C, R1)
	k.tri("roof", D, A, R0)
	k.quad(white, Vector3(-hx, e0 - 0.1, -hz), Vector3(hx, e0 - 0.1, -hz), Vector3(hx, e0 - 0.1, hz), Vector3(-hx, e0 - 0.1, hz))
	var fas := "fascia"
	k.box(fas, Vector3(0, e0 - 1.2, hz + 0.6), Vector3(hx * 2 + 2.4, 3.2, 1.2))
	k.box(fas, Vector3(0, e0 - 1.2, -hz - 0.6), Vector3(hx * 2 + 2.4, 3.2, 1.2))
	k.box(fas, Vector3(hx + 0.6, e0 - 1.2, 0), Vector3(1.2, 3.2, hz * 2))
	k.box(fas, Vector3(-hx - 0.6, e0 - 1.2, 0), Vector3(1.2, 3.2, hz * 2))
	for p in [[A, R0], [B, R1], [C, R1], [D, R0], [R0, R1]]:
		k.beam(white, p[0] + Vector3(0, 0.9, 0), p[1] + Vector3(0, 0.9, 0), 2.6, 1.8)
	k.sphere(fas, Vector3(0, top + 6, 0), 5.0)
	k.cyl("iron", Vector3(0, top + 9, 0), Vector3(0, top + 28, 0), 0.9, 8)
	# a surfboard leaning by the door, and a striped towel over the porch rail
	var sb := Transform3D(Basis(Vector3(0, 0, 1), Vector3.UP, Vector3(-1, 0, 0)).rotated(Vector3(0, 0, 1), -0.2), Vector3(42, 33, 55))
	k.board("surf" + str(seed_ % 3), sb, 7.0, 46.0, 1.4)
	k.box("towel_a", Vector3(-32, 28, 65.5), Vector3(14, 8, 2.2))
	k.box("towel_b", Vector3(-32, 22, 66.6), Vector3(14, 12, 0.6))
	var mats := {
		"pile": _wood(Color("#5b4a38"), Color("#3e3226"), 3, 4.0, 0.0, 0.85),
		"deck": _wood(Color("#a58a6a"), Color("#7d6650"), 1, 6.0, 0.0, 0.8),
		"siding": _wood(col, Color("#a88e72"), 0, 5.6, 0.32, 0.62),
		"trim": _wood(Color("#f6f0e2"), Color("#b8a58c"), 3, 4.0, 0.15, 0.55),
		"door": _wood(col.darkened(0.18), Color("#9b7f62"), 3, 4.0, 0.2, 0.55),
		"fascia": _wood(col, Color("#a88e72"), 3, 4.0, 0.2, 0.55),
		"roof": _wood(Color("#efe6d2"), Color("#b9a68a"), 2, 5.2, 0.12, 0.78),
		"glass": _glass(),
		"brass": _std(Color("#c9a24a"), 0.28, 1.0),
		"iron": _std(Color("#2c2a28"), 0.5, 0.7),
		"lamp": _std(Color("#ffe8b0"), 0.2, 0.0, Color("#ffd27a"), 0.6),
		"ring_red": _std(Color("#d8331e"), 0.5),
		"ring_white": _std(Color("#f4f1ea"), 0.5),
		"towel_a": _std(Color("#2a7fd8"), 0.95),
		"towel_b": _std(Color("#fff4dc"), 0.95),
		"surf0": _std(Color("#ffd23f"), 0.25, 0.0, Color(0, 0, 0), 0.0, 0.6),
		"surf1": _std(Color("#2fd0ff"), 0.25, 0.0, Color(0, 0, 0), 0.0, 0.6),
		"surf2": _std(Color("#ff5a3c"), 0.25, 0.0, Color(0, 0, 0), 0.0, 0.6),
	}
	k.build(parent, xf, mats, 4500.0)


## a timber frame (casing) round an opening on a wall: centre `c`, along `r`, facing out `o`, from y0, w x h
static func _frame(k: Kit, c: Vector3, r: Vector3, o: Vector3, _unused: float, y0: float, w: float, h: float, t: float) -> void:
	var out := o * 0.9
	k.box_on("trim", c + out + Vector3(0, y0 + h * 0.5, 0) - r * (w * 0.5 - t * 0.5), r, o, Vector3(t, h, 1.8))
	k.box_on("trim", c + out + Vector3(0, y0 + h * 0.5, 0) + r * (w * 0.5 - t * 0.5), r, o, Vector3(t, h, 1.8))
	k.box_on("trim", c + out + Vector3(0, y0 + h - t * 0.5, 0), r, o, Vector3(w + 3, t + 1, 2.2))


## a window: casing, sill, two-by-two panes with glazing bars, louvred shutters either side
static func _window(k: Kit, c: Vector3, r: Vector3, o: Vector3, y0: float, w: float, h: float, shutters: bool) -> void:
	var mid := c + Vector3(0, y0 + h * 0.5, 0)
	k.box_on("glass", mid + o * 0.4, r, o, Vector3(w, h, 0.8))
	# casing
	for s in [-1.0, 1.0]:
		k.box_on("trim", mid + o * 1.0 + r * s * (w * 0.5 + 1.2), r, o, Vector3(2.6, h + 5, 2.0))
	k.box_on("trim", mid + o * 1.0 + Vector3(0, h * 0.5 + 1.6, 0), r, o, Vector3(w + 7.6, 3.2, 2.2))
	k.box_on("trim", mid + o * 2.0 - Vector3(0, h * 0.5 + 1.6, 0), r, o, Vector3(w + 9, 2.2, 4.0))
	# glazing bars
	k.box_on("trim", mid + o * 0.9, r, o, Vector3(1.2, h, 0.9))
	k.box_on("trim", mid + o * 0.9, r, o, Vector3(w, 1.2, 0.9))
	if shutters:
		for s in [-1.0, 1.0]:
			var sc: Vector3 = mid + o * 1.4 + r * s * (w * 0.5 + 2.6 + w * 0.25)
			k.box_on("fascia", sc, r, o, Vector3(w * 0.5, h + 2, 1.2))
			var n := int(h / 3.2)
			for i in n:
				k.box_on("fascia", sc + o * 0.7 + Vector3(0, -h * 0.5 + 2.0 + i * 3.2, 0), r, o, Vector3(w * 0.5 - 2.4, 0.9, 0.8))


static func _pier(parent: Node3D, xf: Transform3D) -> void:
	var k := Kit.new()
	var z0 := -180.0
	var z1 := -848.0
	var deck_y := 29.0
	# piles in pairs every 48, with X bracing between each pair
	var bays := 14
	var step := (z0 - z1) / bays
	for i in bays + 1:
		var z := z0 - i * step
		for sd in [-1.0, 1.0]:
			k.cyl("pile", Vector3(sd * 74, -40, z), Vector3(sd * 74, deck_y + (14.0 if i % 2 == 0 else -2.0), z), 4.2, 14)
		k.beam("pile", Vector3(-74, -8, z), Vector3(74, deck_y - 6, z), 2.2, 3.0)
		k.beam("pile", Vector3(74, -8, z), Vector3(-74, deck_y - 6, z), 2.2, 3.0)
		k.box("pile", Vector3(0, deck_y - 4.5, z), Vector3(156, 4, 5))
	# stringers under the planks and the deck itself
	for x in [-60.0, -30.0, 0.0, 30.0, 60.0]:
		k.box("pile", Vector3(x, deck_y - 2.0, (z0 + z1) * 0.5), Vector3(4, 3, z0 - z1 + 8))
	k.box("deck", Vector3(0, deck_y, (z0 + z1) * 0.5), Vector3(160, 2.0, z0 - z1 + 8))
	# kerb timbers along both edges and rope between the taller piles
	for sd in [-1.0, 1.0]:
		k.box("pile", Vector3(sd * 79, deck_y + 2.0, (z0 + z1) * 0.5), Vector3(4, 3, z0 - z1 + 8))
		for i in range(0, bays - 1, 2):
			var a := Vector3(sd * 74, deck_y + 12.0, z0 - i * step)
			var b := Vector3(sd * 74, deck_y + 12.0, z0 - (i + 2) * step)
			var pts := PackedVector3Array()
			for s in 13:
				var t := s / 12.0
				pts.append(a.lerp(b, t) + Vector3(0, -6.0 * sin(PI * t), 0))
			k.tube("rope", pts, 0.8)
	# lamp posts every fourth pair
	var z := z0 - step * 0.5
	while z >= z1:
		for sd in [-1.0, 1.0]:
			k.cyl("iron", Vector3(sd * 70, deck_y, z), Vector3(sd * 70, deck_y + 46, z), 1.3, 10)
			k.box("iron", Vector3(sd * 70, deck_y + 49, z), Vector3(5.5, 7, 5.5))
			k.box("lamp", Vector3(sd * 70, deck_y + 49, z), Vector3(4.2, 5.4, 4.2))
			k.box("iron", Vector3(sd * 70, deck_y + 53.2, z), Vector3(7, 1.4, 7))
		z -= step * 4.0
	# a couple of bollards with mooring rope near the far end
	for p in [Vector3(-62, deck_y, -800), Vector3(62, deck_y, -740)]:
		k.cyl("iron", p, p + Vector3(0, 7, 0), 3.2, 16)
		k.sphere("iron", p + Vector3(0, 7.5, 0), 3.6)
	var mats := {
		"pile": _wood(Color("#5b4a38"), Color("#3e3226"), 3, 4.0, 0.0, 0.85),
		"deck": _wood(Color("#a7906f"), Color("#7d6650"), 1, 7.0, 0.0, 0.82),
		"rope": _std(Color("#c8b48a"), 0.95),
		"iron": _std(Color("#2c2a28"), 0.5, 0.7),
		"lamp": _std(Color("#ffe8b0"), 0.2, 0.0, Color("#ffd27a"), 0.6),
	}
	k.build(parent, xf, mats, 5000.0)


# ---------------------------------------------------------------- materials

static func _wood(paint: Color, under: Color, mode: int, board: float, wear: float, rough: float) -> ShaderMaterial:
	var key := "w|%s|%s|%d|%.2f|%.2f|%.2f" % [paint.to_html(), under.to_html(), mode, board, wear, rough]
	if _mats.has(key):
		return _mats[key]
	if _wood_sh == null:
		_wood_sh = load("res://shaders/hd_wood.gdshader")
	var m := ShaderMaterial.new()
	m.shader = _wood_sh
	m.set_shader_parameter("paint", paint)
	m.set_shader_parameter("under", under)
	m.set_shader_parameter("mode", mode)
	m.set_shader_parameter("board", board)
	m.set_shader_parameter("wear", wear)
	m.set_shader_parameter("rough", rough)
	m.set_shader_parameter("noise", _noise_tex())
	_mats[key] = m
	return m


static func _std(col: Color, rough: float, metal := 0.0, emit := Color(0, 0, 0), energy := 0.0, coat := 0.0) -> StandardMaterial3D:
	var key := "s|%s|%.2f|%.2f|%s|%.2f|%.2f" % [col.to_html(), rough, metal, emit.to_html(), energy, coat]
	if _mats.has(key):
		return _mats[key]
	var m := StandardMaterial3D.new()
	m.albedo_color = col
	m.roughness = rough
	m.metallic = metal
	if energy > 0.0:
		m.emission_enabled = true
		m.emission = emit
		m.emission_energy_multiplier = energy
	if coat > 0.0:
		m.clearcoat_enabled = true
		m.clearcoat = coat
		m.clearcoat_roughness = 0.1
	_mats[key] = m
	return m


static func _glass() -> StandardMaterial3D:
	if _mats.has("glass"):
		return _mats["glass"]
	var m := StandardMaterial3D.new()
	m.albedo_color = Color("#456472")
	m.roughness = 0.03
	m.metallic = 0.0
	m.metallic_specular = 0.95
	# a faint warm room behind the glass, so a window never reads as a hole
	m.emission_enabled = true
	m.emission = Color("#5a4632")
	m.emission_energy_multiplier = 0.25
	_mats["glass"] = m
	return m


static func _noise_tex() -> NoiseTexture2D:
	if _noise != null:
		return _noise
	_noise = NoiseTexture2D.new()
	_noise.width = 512
	_noise.height = 512
	_noise.seamless = true
	_noise.generate_mipmaps = true
	var n := FastNoiseLite.new()
	n.seed = 311
	n.frequency = 0.03
	n.fractal_octaves = 4
	_noise.noise = n
	return _noise


# ---------------------------------------------------------------- taking the web's pieces out

## removes every triangle whose middle lies inside one of the boxes ([frame, centre, half size], in the frame's
## space) from the track's baked meshes. Returns how many it removed.
static func cut_boxes(root: Node, boxes: Array) -> int:
	var inv: Array = []
	var aabbs: Array = []
	for b in boxes:
		var xf: Transform3D = b[0]
		var c: Vector3 = b[1]
		var h: Vector3 = b[2]
		inv.append(xf.affine_inverse())
		var bb := AABB(c - h, h * 2.0)
		aabbs.append(xf * bb)
	var removed := 0
	for node in root.find_children("*", "MeshInstance3D", true, false):
		var mi := node as MeshInstance3D
		var am := mi.mesh as ArrayMesh
		if am == null:
			continue
		var gx := mi.global_transform
		var gb := gx * am.get_aabb()
		var hit: Array = []
		for i in boxes.size():
			if gb.intersects(aabbs[i]):
				hit.append(i)
		if hit.is_empty():
			continue
		var out := ArrayMesh.new()
		var changed := false
		var overrides: Array = []
		for si in am.get_surface_count():
			overrides.append(mi.get_surface_override_material(si))
			var arr := am.surface_get_arrays(si)
			var sm := am.surface_get_material(si)
			if sm != null and String(sm.resource_name).begins_with("terrain"):
				out.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arr)
				out.surface_set_material(out.get_surface_count() - 1, sm)
				continue
			var v: PackedVector3Array = arr[Mesh.ARRAY_VERTEX]
			var idx: PackedInt32Array = arr[Mesh.ARRAY_INDEX] if arr[Mesh.ARRAY_INDEX] != null else PackedInt32Array()
			if idx.is_empty():
				idx.resize(v.size())
				for q in v.size():
					idx[q] = q
			var keep := PackedInt32Array()
			keep.resize(idx.size())
			var nk := 0
			for t in range(0, idx.size() - 2, 3):
				var m := gx * ((v[idx[t]] + v[idx[t + 1]] + v[idx[t + 2]]) / 3.0)
				var inside := false
				for i in hit:
					var lp: Vector3 = inv[i] * m
					var c: Vector3 = boxes[i][1]
					var h: Vector3 = boxes[i][2]
					var d := (lp - c).abs()
					if d.x <= h.x and d.y <= h.y and d.z <= h.z:
						inside = true
						break
				if inside:
					removed += 1
					if OS.has_environment("CR_CUT_DBG"):
						var mk := "%s/%s" % [mi.name, am.surface_get_material(si).resource_name if am.surface_get_material(si) else "-"]
						_dbg[mk] = int(_dbg.get(mk, 0)) + 1
					continue
				keep[nk] = idx[t]
				keep[nk + 1] = idx[t + 1]
				keep[nk + 2] = idx[t + 2]
				nk += 3
			if nk != idx.size():
				changed = true
			keep.resize(nk)
			arr[Mesh.ARRAY_INDEX] = keep
			if nk > 0:
				out.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arr)
				out.surface_set_material(out.get_surface_count() - 1, am.surface_get_material(si))
			else:
				overrides[si] = "drop"
		if not changed:
			continue
		mi.mesh = out
		var k := 0
		for si in overrides.size():
			if typeof(overrides[si]) == TYPE_STRING:
				continue
			if overrides[si] != null:
				mi.set_surface_override_material(k, overrides[si])
			k += 1
	if OS.has_environment("CR_CUT_DBG"):
		for k in _dbg:
			print("CUT ", k, " ", _dbg[k])
	return removed


static var _dbg := {}


# ---------------------------------------------------------------- a small geometry kit

## gathers boxes, cylinders, quads and tubes by material, then makes one mesh per material. Every triangle is
## wound to face the way its normal points, so the shapes can be described in any order.
class Kit:
	var parts := {}

	func _st(key: String) -> SurfaceTool:
		if not parts.has(key):
			var st := SurfaceTool.new()
			st.begin(Mesh.PRIMITIVE_TRIANGLES)
			parts[key] = st
		return parts[key]

	## one triangle; Godot's front faces wind clockwise seen from the front, so flip it when it doesn't
	func _t(st: SurfaceTool, p0: Vector3, p1: Vector3, p2: Vector3, n0: Vector3, n1: Vector3, n2: Vector3) -> void:
		if (p1 - p0).cross(p2 - p0).dot(n0 + n1 + n2) > 0.0:
			var tp := p1
			p1 = p2
			p2 = tp
			var tn := n1
			n1 = n2
			n2 = tn
		st.set_normal(n0)
		st.add_vertex(p0)
		st.set_normal(n1)
		st.add_vertex(p1)
		st.set_normal(n2)
		st.add_vertex(p2)

	func _face(st: SurfaceTool, a: Vector3, b: Vector3, c: Vector3, d: Vector3, n: Vector3) -> void:
		_t(st, a, b, c, n, n, n)
		_t(st, a, c, d, n, n, n)

	## a flat triangle; its front is the side a, b, c run counter-clockwise round
	func tri(key: String, a: Vector3, b: Vector3, c: Vector3) -> void:
		var n := (b - a).cross(c - a).normalized()
		_t(_st(key), a, b, c, n, n, n)

	## a flat quad; its front is the side a, b, c, d run counter-clockwise round
	func quad(key: String, a: Vector3, b: Vector3, c: Vector3, d: Vector3) -> void:
		var n := (b - a).cross(c - a).normalized()
		_face(_st(key), a, b, c, d, n)

	## an axis-aligned box (centre, full size)
	func box(key: String, c: Vector3, s: Vector3) -> void:
		box_basis(key, c, Basis(), s)

	## a box on a wall: x along `r`, z out along `o`
	func box_on(key: String, c: Vector3, r: Vector3, o: Vector3, s: Vector3) -> void:
		box_basis(key, c, Basis(r.normalized(), Vector3.UP, o.normalized()), s)

	func box_basis(key: String, c: Vector3, b: Basis, s: Vector3) -> void:
		var st := _st(key)
		var bx := b.x.normalized()
		var by := b.y.normalized()
		var bz := b.z.normalized()
		var X := bx * s.x * 0.5
		var Y := by * s.y * 0.5
		var Z := bz * s.z * 0.5
		_face(st, c + X - Y + Z, c + X - Y - Z, c + X + Y - Z, c + X + Y + Z, bx)
		_face(st, c - X - Y - Z, c - X - Y + Z, c - X + Y + Z, c - X + Y - Z, -bx)
		_face(st, c - X + Y + Z, c + X + Y + Z, c + X + Y - Z, c - X + Y - Z, by)
		_face(st, c - X - Y - Z, c + X - Y - Z, c + X - Y + Z, c - X - Y + Z, -by)
		_face(st, c - X - Y + Z, c + X - Y + Z, c + X + Y + Z, c - X + Y + Z, bz)
		_face(st, c + X - Y - Z, c - X - Y - Z, c - X + Y - Z, c + X + Y - Z, -bz)

	## a square beam from a to b (w wide, h deep), its depth kept as upright as it can be
	func beam(key: String, a: Vector3, b: Vector3, w: float, h: float) -> void:
		var d := b - a
		var z := d.normalized()
		var x := Vector3.UP.cross(z)
		if x.length() < 0.01:
			x = Vector3.RIGHT
		x = x.normalized()
		var y := z.cross(x).normalized()
		box_basis(key, (a + b) * 0.5, Basis(x, y, z), Vector3(w, h, d.length()))

	## a capped cylinder from a to b
	func cyl(key: String, a: Vector3, b: Vector3, r: float, segs := 16) -> void:
		var st := _st(key)
		var z := (b - a).normalized()
		var x := z.cross(Vector3.UP)
		if x.length() < 0.01:
			x = z.cross(Vector3.RIGHT)
		x = x.normalized()
		var y := x.cross(z).normalized()
		for i in segs:
			var a0 := TAU * i / segs
			var a1 := TAU * (i + 1) / segs
			var n0 := x * cos(a0) + y * sin(a0)
			var n1 := x * cos(a1) + y * sin(a1)
			_t(st, a + n0 * r, a + n1 * r, b + n1 * r, n0, n1, n1)
			_t(st, a + n0 * r, b + n1 * r, b + n0 * r, n0, n1, n0)
			_t(st, a, a + n1 * r, a + n0 * r, -z, -z, -z)
			_t(st, b, b + n0 * r, b + n1 * r, z, z, z)

	func sphere(key: String, c: Vector3, r: float, segs := 16) -> void:
		var st := _st(key)
		var rings := segs / 2
		for i in rings:
			var p0 := PI * i / rings
			var p1 := PI * (i + 1) / rings
			for k in segs:
				var t0 := TAU * k / segs
				var t1 := TAU * (k + 1) / segs
				var v0 := Vector3(sin(p0) * cos(t0), cos(p0), sin(p0) * sin(t0))
				var v1 := Vector3(sin(p0) * cos(t1), cos(p0), sin(p0) * sin(t1))
				var v2 := Vector3(sin(p1) * cos(t1), cos(p1), sin(p1) * sin(t1))
				var v3 := Vector3(sin(p1) * cos(t0), cos(p1), sin(p1) * sin(t0))
				if i > 0:
					_t(st, c + v0 * r, c + v1 * r, c + v2 * r, v0, v1, v2)
				if i < rings - 1:
					_t(st, c + v0 * r, c + v2 * r, c + v3 * r, v0, v2, v3)

	## a tube along a path
	func tube(key: String, path: PackedVector3Array, r: float, sides := 8) -> void:
		var st := _st(key)
		var rings: Array = []
		for i in path.size():
			var t := (path[mini(i + 1, path.size() - 1)] - path[maxi(i - 1, 0)]).normalized()
			var side := t.cross(Vector3.UP)
			if side.length() < 0.01:
				side = t.cross(Vector3.RIGHT)
			side = side.normalized()
			var up := side.cross(t).normalized()
			var ring: Array = []
			for k in sides + 1:
				var an := TAU * float(k) / sides
				var n := side * cos(an) + up * sin(an)
				ring.append([path[i] + n * r, n])
			rings.append(ring)
		for i in path.size() - 1:
			for k in sides:
				var a: Array = rings[i][k]
				var b: Array = rings[i][k + 1]
				var c: Array = rings[i + 1][k]
				var d: Array = rings[i + 1][k + 1]
				_t(st, a[0], b[0], c[0], a[1], b[1], c[1])
				_t(st, b[0], d[0], c[0], b[1], d[1], c[1])

	## a life ring on a wall: alternating red and white quarters
	func ring(k1: String, k2: String, c: Vector3, o: Vector3, R: float, r: float) -> void:
		var z := o.normalized()
		var x := Vector3.UP.cross(z).normalized()
		var y := Vector3.UP
		var segs := 32
		var sides := 10
		for i in segs:
			var key := k1 if (i * 4 / segs) % 2 == 0 else k2
			var st := _st(key)
			for j in sides:
				var q := []
				for e in [[i, j], [i + 1, j], [i + 1, j + 1], [i, j + 1]]:
					var a: float = TAU * e[0] / segs
					var b: float = TAU * e[1] / sides
					var cdir := x * cos(a) + y * sin(a)
					var n := cdir * cos(b) + z * sin(b)
					q.append([c + cdir * R + n * r, n])
				_t(st, q[0][0], q[1][0], q[2][0], q[0][1], q[1][1], q[2][1])
				_t(st, q[0][0], q[2][0], q[3][0], q[0][1], q[2][1], q[3][1])

	## a surfboard: a thin rounded slab, w wide and l long, along the frame's y
	func board(key: String, xf: Transform3D, w: float, l: float, t: float) -> void:
		var st := _st(key)
		var n := 20
		var outline: Array = []
		for i in n + 1:
			var s := float(i) / n
			var y := (s - 0.5) * l
			var half := w * 0.5 * pow(sin(PI * clampf(s * 0.96 + 0.02, 0.0, 1.0)), 0.6)
			outline.append([y, half])
		for i in n:
			var a: Array = outline[i]
			var b: Array = outline[i + 1]
			for sd in [1.0, -1.0]:
				var nz := (xf.basis * Vector3(0, 0, sd)).normalized()
				var zz: float = sd * t * 0.5
				_face(st, xf * Vector3(-a[1], a[0], zz), xf * Vector3(a[1], a[0], zz), xf * Vector3(b[1], b[0], zz), xf * Vector3(-b[1], b[0], zz), nz)
			for sx in [-1.0, 1.0]:
				var ns := (xf.basis * Vector3(sx, 0, 0)).normalized()
				_face(st, xf * Vector3(sx * a[1], a[0], t * 0.5), xf * Vector3(sx * a[1], a[0], -t * 0.5), xf * Vector3(sx * b[1], b[0], -t * 0.5), xf * Vector3(sx * b[1], b[0], t * 0.5), ns)

	func build(parent: Node3D, xf: Transform3D, mats: Dictionary, vis_end: float) -> void:
		for key in parts:
			var st: SurfaceTool = parts[key]
			var mesh := st.commit()
			var mi := MeshInstance3D.new()
			mi.mesh = mesh
			mi.material_override = mats.get(key, null)
			mi.transform = xf
			mi.visibility_range_end = vis_end
			mi.visibility_range_end_margin = 300.0
			mi.visibility_range_fade_mode = GeometryInstance3D.VISIBILITY_RANGE_FADE_SELF
			parent.add_child(mi)
