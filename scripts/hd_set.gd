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
	var n := canyon(root, T)
	match T.id:
		"lagoon":
			n += _lagoon(root, T)
	return n


# ---------------------------------------------------------------- the glide canyon's ends

## The glide canyon is cut into the ground by the web's pitAt; the exported ground is a coarse polar grid, so at the
## canyon's square ends its triangles span from the rim to the floor and stand up as rows of teeth in front of the
## crust end walls. Near both ends the ground is laid again on a fine grid (the same picture, mapped the same way: x
## and z over 110): the canyon's floor and side slopes from the same formula, dropping straight down just behind each
## end wall so the walls show as clean cliffs; the coarse triangles there are taken out. Drawing only.
static func canyon(root: Node3D, T: TrackData) -> int:
	if T.glide.is_empty() or T.pits.is_empty():
		return 0
	var j0 := int(T.glide.get("j0", -1))
	var j1 := int(T.glide.get("j1", -1))
	if j0 < 0 or j1 < 0 or j0 >= T.N or j1 >= T.N:
		return 0
	var ax := T.px[j0]
	var az := T.py[j0]
	var L := Vector2(T.px[j1] - ax, T.py[j1] - az).length()
	if L < 50.0:
		return 0
	var ux := (T.px[j1] - ax) / L
	var uz := (T.py[j1] - az) / L
	var W := T.CURB + 25.0
	var D := 110.0 if bool(T.glide.get("long", false)) else 50.0
	# the canyon's own frame: x across (v), z along (u), origin at the start
	var xf := Transform3D(Basis(Vector3(-uz, 0, ux), Vector3.UP, Vector3(ux, 0, uz)), Vector3(ax, 0, az))
	var ends: Array = []
	if L < 220.0:
		ends.append([-20.0, L + 20.0])
	else:
		ends.append([-20.0, 50.0])
		ends.append([L - 50.0, L + 20.0])
	var VW := W + 80.0
	var boxes: Array = []
	for e in ends:
		boxes.append([xf, Vector3(0, 0, (e[0] + e[1]) * 0.5), Vector3(VW, 2000.0, (e[1] - e[0]) * 0.5), {"terrain": true}])
	# the ground's material, from the mesh that holds it
	var mat: Material = null
	var shadow := GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	for node in root.find_children("*", "MeshInstance3D", true, false):
		var mi := node as MeshInstance3D
		var am := mi.mesh as ArrayMesh
		if am == null:
			continue
		for si in am.get_surface_count():
			var m := am.surface_get_material(si)
			if m != null and String(m.resource_name).begins_with("terrain"):
				mat = mi.get_surface_override_material(si) if mi.get_surface_override_material(si) != null else m
				shadow = mi.cast_shadow
				break
		if mat != null:
			break
	if mat == null:
		return 0
	var cut := cut_boxes(root, boxes)
	if cut == 0:
		return 0
	# the new ground: 3-unit cells, reaching 28 units past the cut so it fills the holes the coarse triangles leave;
	# outside the cut it sits a hair lower so the old ground wins wherever both are
	var st := SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	var step := 3.0
	var pad := 28.0
	# the drop sits 0.2 behind the web's crust end walls (0.8 outside the canyon), so the walls show as the ends
	var cliff := [-1.0, L + 1.0]
	for e in ends:
		var u0: float = e[0] - pad
		var u1: float = e[1] + pad
		var us: Array = []
		var nu := int(ceil((u1 - u0) / step))
		for i in nu + 1:
			us.append([u0 + (u1 - u0) * float(i) / nu, 0])
		for c in cliff:
			if c > u0 and c < u1:
				us.append([c - 0.001, -1])
				us.append([c + 0.001, 1])
		us.sort_custom(func(a, b): return a[0] < b[0])
		var nv := int(ceil((VW + pad) * 2.0 / step))
		var pts: Array = []
		for i in us.size():
			var row: Array = []
			var u: float = us[i][0]
			for j in nv + 1:
				var v := -(VW + pad) + (VW + pad) * 2.0 * float(j) / nv
				var x := ax + ux * u - uz * v
				var z := az + uz * u + ux * v
				var base := T.ground(x, z) + T.pit(x, z)
				var d := 0.0
				if u > cliff[0] and u < cliff[1] and absf(v) < W + 70.0:
					var l := minf(1.0, (W + 70.0 - absf(v)) / 70.0)
					l = l * l * (3.0 - 2.0 * l)
					d = D * l
				var out := maxf(maxf(e[0] - u, u - e[1]), absf(v) - VW)
				var y := base - d - 0.6 * clampf(out / 4.0, 0.0, 1.0)
				row.append(Vector3(x, y, z))
			pts.append(row)
		for i in us.size() - 1:
			# no face across the drop itself: the crust wall stands there
			if absf(float(us[i + 1][0]) - float(us[i][0])) < 0.01:
				continue
			for j in nv:
				var p00: Vector3 = pts[i][j]
				var p01: Vector3 = pts[i][j + 1]
				var p10: Vector3 = pts[i + 1][j]
				var p11: Vector3 = pts[i + 1][j + 1]
				for tri in [[p00, p10, p11], [p00, p11, p01]]:
					var n: Vector3 = (tri[1] - tri[0]).cross(tri[2] - tri[0]).normalized()
					if n.y < 0.0:
						tri = [tri[0], tri[2], tri[1]]
					# Godot fronts wind clockwise: emit so the face points up
					for q in [tri[0], tri[2], tri[1]]:
						st.set_uv(Vector2(q.x, q.z) / 110.0)
						st.add_vertex(q)
	st.index()
	st.generate_normals()
	var mi2 := MeshInstance3D.new()
	mi2.name = "hd_canyon"
	mi2.mesh = st.commit()
	mi2.material_override = mat
	mi2.cast_shadow = shadow
	root.add_child(mi2)
	return cut


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
	# the lighthouse on its rock (atA(1.1, R+900)): only the web's lighthouse colours are taken out there
	var la := 1.1
	var lh := _facing(Vector3(cos(la) * (T.R + 900.0), -14.0, sin(la) * (T.R + 900.0)))
	cut += cut_boxes(root, [[lh, Vector3(0, 380, 0), Vector3(300, 470, 300), {"cyl": true, "cols": ["#7a7068", "#f4f4f2", "#c8261b", "#fff6c8", "#2a2a2a"]}]])
	_lighthouse(g, lh)
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


static func _lighthouse(parent: Node3D, xf: Transform3D) -> void:
	var k := Kit.new()
	# the rock: a weathered mound rising out of the water, flattened on top for the tower
	var fnl := FastNoiseLite.new()
	fnl.seed = 41
	fnl.frequency = 0.012
	fnl.fractal_octaves = 4
	fnl.fractal_type = FastNoiseLite.FRACTAL_RIDGED
	var rings := 22
	var segs := 72
	var grid: Array = []
	for i in rings + 1:
		var r := 300.0 * float(i) / rings
		var row: Array = []
		for j in segs:
			var a := TAU * j / segs
			var x := cos(a) * r
			var z := sin(a) * r
			var t := clampf(1.0 - pow(r / 262.0, 2.0), 0.0, 1.0)
			var h := 205.0 * pow(t, 0.7) - 36.0 * pow(r / 300.0, 3.0)
			h += fnl.get_noise_2d(x, z) * 34.0 * smoothstep(-20.0, 60.0, h) * smoothstep(60.0, 120.0, r)
			h = lerpf(196.0, h, smoothstep(92.0, 120.0, r))
			row.append(Vector3(x, h, z))
		grid.append(row)
	# normals from the neighbours round each point
	var nrm: Array = []
	for i in rings + 1:
		var row: Array = []
		for j in segs:
			var p: Vector3 = grid[i][j]
			var pr: Vector3 = grid[mini(i + 1, rings)][j]
			var pl: Vector3 = grid[maxi(i - 1, 0)][j]
			var pa: Vector3 = grid[i][(j + 1) % segs]
			var pb: Vector3 = grid[i][(j - 1 + segs) % segs]
			var n := (pr - pl).cross(pa - pb)
			if i == 0 or n.length() < 1e-4:
				n = Vector3.UP
			n = n.normalized()
			if n.y < 0.0 and i > 0:
				n = -n
			if n.dot(Vector3(p.x, 0, p.z).normalized() + Vector3.UP * 0.3) < -0.5:
				n = -n
			row.append(n)
		nrm.append(row)
	for i in rings:
		for j in segs:
			var j2 := (j + 1) % segs
			var a: Vector3 = grid[i][j]
			var b: Vector3 = grid[i][j2]
			var c: Vector3 = grid[i + 1][j2]
			var d: Vector3 = grid[i + 1][j]
			k.tri_n("rock", a, b, c, nrm[i][j], nrm[i][j2], nrm[i + 1][j2])
			k.tri_n("rock", a, c, d, nrm[i][j], nrm[i + 1][j2], nrm[i + 1][j])
	# boulders at the waterline
	var rng := RandomNumberGenerator.new()
	rng.seed = 77
	for i in 14:
		var a := rng.randf() * TAU
		var r := 240.0 + rng.randf() * 60.0
		k.sphere("rock", Vector3(cos(a) * r, -6.0 + rng.randf() * 8.0, sin(a) * r), 14.0 + rng.randf() * 18.0, 10)
	# a plinth, then the tower in red and white bands, tapering
	k.lathe("stone", [[0.0, 192.0], [96.0, 192.0], [96.0, 204.0], [90.0, 208.0], [0.0, 208.0]], 64)
	var y0 := 206.0
	var y1 := 640.0
	var bands := 6
	for b in bands:
		var ya := lerpf(y0, y1, float(b) / bands)
		var yb := lerpf(y0, y1, float(b + 1) / bands)
		var ra := lerpf(80.0, 52.0, (ya - y0) / (y1 - y0))
		var rb := lerpf(80.0, 52.0, (yb - y0) / (y1 - y0))
		k.lathe("t_red" if b % 2 == 0 else "t_white", [[ra, ya], [rb, yb]], 64, false)
	# small windows up the tower, a door at its foot facing the track
	for w in 5:
		var y := 280.0 + w * 72.0
		var a := 0.6 + w * 1.9
		var rr := lerpf(80.0, 52.0, (y - y0) / (y1 - y0))
		var o := Vector3(cos(a), 0, sin(a))
		var r := Vector3(-sin(a), 0, cos(a))
		k.box_on("glass", o * (rr - 1.0) + Vector3(0, y, 0), r, o, Vector3(8, 16, 3))
		k.box_on("trim", o * (rr - 0.5) + Vector3(0, y + 9.5, 0), r, o, Vector3(12, 2.4, 4))
		k.box_on("trim", o * (rr - 0.5) + Vector3(0, y - 9.5, 0), r, o, Vector3(12, 2.4, 5))
	var dz := Vector3(0, 0, 1)
	k.box_on("trim", dz * 79.0 + Vector3(0, 236, 0), Vector3.RIGHT, dz, Vector3(30, 52, 6))
	k.box_on("door", dz * 81.5 + Vector3(0, 232, 0), Vector3.RIGHT, dz, Vector3(22, 44, 2))
	k.sphere("brass", dz * 83.0 + Vector3(7, 230, 0), 1.6)
	for s in 4:
		k.box("stone", Vector3(0, 199.0 - s * 4.0, 100.0 + s * 7.0), Vector3(34, 4, 8))
	# the gallery: a corbelled cornice, the walkway and a railing
	k.lathe("t_white", [[52.0, 640.0], [60.0, 648.0], [66.0, 654.0], [72.0, 656.0], [72.0, 660.0], [0.0, 660.0]], 64)
	k.lathe("iron", [[0.0, 640.0], [52.0, 640.0]], 64)
	for i in 36:
		var a := TAU * i / 36
		k.cyl("iron", Vector3(cos(a) * 70, 660, sin(a) * 70), Vector3(cos(a) * 70, 678, sin(a) * 70), 0.8, 6)
	for y in [669.0, 678.0]:
		var pts := PackedVector3Array()
		for i in 73:
			var a := TAU * i / 72
			pts.append(Vector3(cos(a) * 70, y, sin(a) * 70))
		k.tube("iron", pts, 0.9 if y > 670.0 else 0.6, 6)
	# the lantern room: a low wall, twelve glazed panes between mullions, the lamp inside, a domed roof
	k.lathe("t_red", [[46.0, 660.0], [46.0, 674.0], [48.0, 676.0], [0.0, 676.0]], 48)
	var n := 12
	for i in n:
		var a0 := TAU * i / n
		var a1 := TAU * (i + 1) / n
		var p0 := Vector3(cos(a0) * 42, 676, sin(a0) * 42)
		var p1 := Vector3(cos(a1) * 42, 676, sin(a1) * 42)
		k.quad("lens", p0, p1, p1 + Vector3(0, 44, 0), p0 + Vector3(0, 44, 0))
		k.quad("lens", p1, p0, p0 + Vector3(0, 44, 0), p1 + Vector3(0, 44, 0))
		k.cyl("iron", p0, p0 + Vector3(0, 44, 0), 1.3, 6)
	k.sphere("lamp", Vector3(0, 698, 0), 15.0, 20)
	k.lathe("iron", [[0.0, 674.0], [10.0, 674.0], [6.0, 684.0], [0.0, 684.0]], 24)
	var dome: Array = [[0.0, 720.0], [50.0, 720.0], [50.0, 723.0]]
	for i in 9:
		var t := float(i + 1) / 9.0
		dome.append([lerpf(48.0, 0.0, t) * (1.0 - 0.25 * sin(PI * t)), 723.0 + 36.0 * sin(t * PI * 0.5)])
	k.lathe("roof", dome, 48)
	k.sphere("roof", Vector3(0, 763, 0), 6.5, 16)
	k.cyl("iron", Vector3(0, 768, 0), Vector3(0, 800, 0), 1.0, 8)
	var rock := _rock_mat()
	var mats := {
		"rock": rock,
		"stone": _wood(Color("#b9b0a2"), Color("#8e8578"), 4, 8.0, 0.0, 0.85),
		"t_red": _wood(Color("#c8261b"), Color("#b9b0a2"), 4, 9.0, 0.0, 0.6, true),
		"t_white": _wood(Color("#f4f4f2"), Color("#b9b0a2"), 4, 9.0, 0.0, 0.6, true),
		"trim": _wood(Color("#f6f0e2"), Color("#b8a58c"), 3, 4.0, 0.1, 0.55),
		"door": _wood(Color("#2f5d46"), Color("#9b7f62"), 3, 4.0, 0.15, 0.55),
		"glass": _glass(),
		"brass": _std(Color("#c9a24a"), 0.28, 1.0),
		"iron": _std(Color("#262a2c"), 0.45, 0.6),
		"roof": _std(Color("#1f3029"), 0.72, 0.0),
		"lamp": _std(Color("#fff6c8"), 0.2, 0.0, Color("#ffe080"), 2.2),
		"lens": _lens(),
	}
	k.build(parent, xf, mats, 16000.0)


static func _rock_mat() -> StandardMaterial3D:
	if _mats.has("rock"):
		return _mats["rock"]
	var m := StandardMaterial3D.new()
	m.albedo_color = Color("#a49a8e")
	m.roughness = 0.92
	var cc := "res://assets/hd/cc0/rock_face_"
	if ResourceLoader.exists(cc + "col.jpg"):
		m.albedo_texture = load(cc + "col.jpg")
		m.albedo_color = Color("#c4bab0")
		if ResourceLoader.exists(cc + "nrm.jpg"):
			m.normal_enabled = true
			m.normal_texture = load(cc + "nrm.jpg")
			m.normal_scale = 1.2
		if ResourceLoader.exists(cc + "rgh.jpg"):
			m.roughness_texture = load(cc + "rgh.jpg")
			m.roughness = 1.0
		m.uv1_triplanar = true
		m.uv1_world_triplanar = true
		m.uv1_scale = Vector3(0.008, 0.008, 0.008)
		m.texture_filter = BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS_ANISOTROPIC
	_mats["rock"] = m
	return m


static func _lens() -> StandardMaterial3D:
	if _mats.has("lens"):
		return _mats["lens"]
	var m := StandardMaterial3D.new()
	m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	m.albedo_color = Color(0.85, 0.92, 0.95, 0.28)
	m.roughness = 0.02
	m.metallic_specular = 1.0
	m.emission_enabled = true
	m.emission = Color("#ffe6a0")
	m.emission_energy_multiplier = 0.35
	_mats["lens"] = m
	return m


# ---------------------------------------------------------------- materials

static func _wood(paint: Color, under: Color, mode: int, board: float, wear: float, rough: float, round_u := false) -> ShaderMaterial:
	var key := "w|%s|%s|%d|%.2f|%.2f|%.2f|%s" % [paint.to_html(), under.to_html(), mode, board, wear, rough, str(round_u)]
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
	m.set_shader_parameter("round_u", round_u)
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
	var opts: Array = []
	for b in boxes:
		var xf: Transform3D = b[0]
		var c: Vector3 = b[1]
		var h: Vector3 = b[2]
		var opt: Dictionary = b[3] if b.size() > 3 else {}
		var cols: Array = []
		for hx in opt.get("cols", []):
			cols.append(Color(hx))
		opts.append({"cyl": bool(opt.get("cyl", false)), "cols": cols, "terrain": bool(opt.get("terrain", false))})
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
			# which of the boxes may cut this surface (never the ground; a box with colours only those colours)
			var here: Array = []
			var ter := sm != null and String(sm.resource_name).begins_with("terrain")
			for i in hit:
				if ter != bool(opts[i]["terrain"]):
					continue
				var cl: Array = opts[i]["cols"]
				if cl.is_empty():
					here.append(i)
					continue
				var bm := sm as BaseMaterial3D
				if bm == null:
					continue
				for cc in cl:
					var d4: Color = bm.albedo_color - cc
					if absf(d4.r) < 0.04 and absf(d4.g) < 0.04 and absf(d4.b) < 0.04:
						here.append(i)
						break
			if here.is_empty():
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
				for i in here:
					var lp: Vector3 = inv[i] * m
					var c: Vector3 = boxes[i][1]
					var h: Vector3 = boxes[i][2]
					var d := (lp - c).abs()
					if opts[i]["cyl"]:
						if d.y <= h.y and Vector2(lp.x - c.x, lp.z - c.z).length() <= h.x:
							inside = true
							break
					elif d.x <= h.x and d.y <= h.y and d.z <= h.z:
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

	## a triangle with its own normals at each corner
	func tri_n(key: String, a: Vector3, b: Vector3, c: Vector3, na: Vector3, nb: Vector3, nc: Vector3) -> void:
		_t(_st(key), a, b, c, na, nb, nc)

	var smooth := {}

	## a triangle whose normals are worked out at the end, smoothed with its neighbours; `out` is roughly outward
	func smooth_tri(key: String, a: Vector3, b: Vector3, c: Vector3, out: Vector3) -> void:
		smooth[key] = true
		_t(_st(key), a, b, c, out, out, out)

	## a surface turned round the y axis from a profile of [radius, height] points (bottom to top)
	func lathe(key: String, prof: Array, segs := 48, _cap := true) -> void:
		var st := _st(key)
		for i in prof.size() - 1:
			var r0: float = prof[i][0]
			var y0: float = prof[i][1]
			var r1: float = prof[i + 1][0]
			var y1: float = prof[i + 1][1]
			var nn := Vector2(y1 - y0, -(r1 - r0)).normalized()
			for j in segs:
				var a0 := TAU * j / segs
				var a1 := TAU * (j + 1) / segs
				var d0 := Vector3(cos(a0), 0, sin(a0))
				var d1 := Vector3(cos(a1), 0, sin(a1))
				var n0 := (d0 * nn.x + Vector3.UP * nn.y).normalized()
				var n1 := (d1 * nn.x + Vector3.UP * nn.y).normalized()
				var p00 := d0 * r0 + Vector3(0, y0, 0)
				var p01 := d1 * r0 + Vector3(0, y0, 0)
				var p10 := d0 * r1 + Vector3(0, y1, 0)
				var p11 := d1 * r1 + Vector3(0, y1, 0)
				if r0 > 0.001:
					_t(st, p00, p01, p11, n0, n1, n1)
				if r1 > 0.001:
					_t(st, p00, p11, p10, n0, n1, n0)

	func build(parent: Node3D, xf: Transform3D, mats: Dictionary, vis_end: float) -> void:
		for key in parts:
			var st: SurfaceTool = parts[key]
			if smooth.has(key):
				st.index()
				st.generate_normals()
			var mesh := st.commit()
			var mi := MeshInstance3D.new()
			mi.mesh = mesh
			mi.material_override = mats.get(key, null)
			mi.transform = xf
			mi.visibility_range_end = vis_end
			mi.visibility_range_end_margin = 300.0
			mi.visibility_range_fade_mode = GeometryInstance3D.VISIBILITY_RANGE_FADE_SELF
			parent.add_child(mi)
