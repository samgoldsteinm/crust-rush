class_name HdKitchen
## The kitchen tracks' room on the PC (Settings > Graphics > Finished models). Drawing only: nothing here touches the
## race. The web's round brick wall becomes a kitchen wall (shaders/kitchen_wall.gdshader: a glazed subway-tile
## backsplash with power outlets, warm plaster, a wooden crown moulding), a run of painted wall cabinets goes round the
## room up high, and the counter along the wall (the table the track sits on) gets what a pizza kitchen keeps there:
## a faucet under each window, stand mixers, toasters, a kettle, a coffee machine, knife blocks, utensil crocks,
## cutting boards, a bread box and paper towels. Every piece is made of smooth rounded shapes with proper materials
## (enamel, brushed and polished steel, wood, glass), never bare boxes.

const TABLE_Y := -60.0
const WINDOWS := [0.15, 1.75, 3.3, 4.9]     # web kitchenDressing's windows
const OVENS := [0.4, 1.97, 3.54, 5.11]      # the brick ovens near the wall
const SC := 2.2      # the pieces are modelled at about 5 units a centimetre; the table's own things are at about 11

static var _mats := {}


static func upgrade(root: Node3D) -> int:
	var wall := _find_wall(root)
	if wall.is_empty():
		return 0
	var mi: MeshInstance3D = wall["mi"]
	var rw: float = wall["r"]
	var top: float = wall["top"]
	var sm := ShaderMaterial.new()
	sm.shader = load("res://shaders/kitchen_wall.gdshader")
	sm.set_shader_parameter("radius", rw)
	sm.set_shader_parameter("y0", TABLE_Y)
	sm.set_shader_parameter("top", top)
	mi.set_surface_override_material(int(wall["si"]), sm)
	var g := Node3D.new()
	g.name = "hd_kitchen"
	root.add_child(g)
	_cabinets(g, rw, top)
	var n := 0
	for a in WINDOWS:
		_faucet(g, rw, a)
		n += 1
	var spots := [[0.72, "knives"], [0.98, "mixer"], [1.27, "boards"], [2.25, "coffee"], [2.55, "toaster"], [2.86, "bread"],
		[3.85, "kettle"], [4.14, "crock"], [4.45, "mixer2"], [5.45, "towels"], [5.76, "toaster"], [6.04, "knives"]]
	for sp in spots:
		if String(sp[1]) == "":
			continue
		var node := _piece(String(sp[1]))
		if node == null:
			continue
		var a: float = sp[0]
		var d: float = rw - 75.0 * SC
		node.position = Vector3(cos(a) * d, TABLE_Y, sin(a) * d)
		node.scale = Vector3.ONE * SC
		# face the room's centre
		node.look_at_from_position(node.position, Vector3(0, TABLE_Y, 0), Vector3.UP)
		g.add_child(node)
		n += 1
	for c in g.find_children("*", "MeshInstance3D", true, false):
		(c as MeshInstance3D).cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	return n


## the room's round wall: an open cylinder round the middle, standing on the table and reaching the ceiling
static func _find_wall(root: Node) -> Dictionary:
	for node in root.find_children("*", "MeshInstance3D", true, false):
		var mi := node as MeshInstance3D
		if mi.mesh == null:
			continue
		for si in mi.mesh.get_surface_count():
			var arr := mi.mesh.surface_get_arrays(si)
			var V: PackedVector3Array = arr[Mesh.ARRAY_VERTEX]
			if V.size() < 60 or V.size() > 4000:
				continue
			var lo := Vector3(1e9, 1e9, 1e9)
			var hi := -lo
			for p in V:
				var q := mi.global_transform * p
				lo = lo.min(q)
				hi = hi.max(q)
			var sz := hi - lo
			var c := (hi + lo) * 0.5
			if sz.y < 1800.0 or absf(c.x) > 60.0 or absf(c.z) > 60.0 or absf(sz.x - sz.z) > 80.0 or sz.x < 4000.0:
				continue
			if absf(lo.y - TABLE_Y) > 40.0:
				continue
			# every point on the circle: a wall, not a dome or a disc
			var r := sz.x * 0.5
			var ok := true
			for k in range(0, V.size(), maxi(1, V.size() / 40)):
				var q2 := mi.global_transform * V[k]
				if absf(Vector2(q2.x, q2.z).length() - r) > r * 0.03:
					ok = false
					break
			if ok:
				return {"mi": mi, "si": si, "r": r, "top": hi.y}
	return {}


# ---------------------------------------------------------------- materials and shapes

static func _m(col: String, rough: float, metal := 0.0, coat := 0.0) -> StandardMaterial3D:
	var key := "%s|%.2f|%.2f|%.2f" % [col, rough, metal, coat]
	if _mats.has(key):
		return _mats[key]
	var m := StandardMaterial3D.new()
	m.albedo_color = Color(col)
	m.roughness = rough
	m.metallic = metal
	if coat > 0.0:
		m.clearcoat_enabled = true
		m.clearcoat = coat
		m.clearcoat_roughness = 0.08
	_mats[key] = m
	return m


static func _glass(col: String, a: float) -> StandardMaterial3D:
	var key := "glass|%s|%.2f" % [col, a]
	if _mats.has(key):
		return _mats[key]
	var m := StandardMaterial3D.new()
	m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	var c := Color(col)
	c.a = a
	m.albedo_color = c
	m.roughness = 0.05
	m.metallic_specular = 0.9
	_mats[key] = m
	return m


## a box with rounded edges and corners (an inner box grown by a sphere): smooth shading all round
static func rbox(half: Vector3, r: float, seg := 20) -> ArrayMesh:
	r = minf(r, minf(half.x, minf(half.y, half.z)) * 0.98)
	var inner := half - Vector3.ONE * r
	var st := SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	var rings := seg / 2
	var pts: Array = []
	for i in rings + 1:
		# offset by half a step so no ring sits exactly on the box's middle (the flat faces stretch between rings)
		var phi := PI * float(i) / float(rings)
		var row: Array = []
		for k in seg + 1:
			var th := TAU * (float(k) + 0.5) / float(seg)
			var n := Vector3(sin(phi) * cos(th), cos(phi), sin(phi) * sin(th))
			var c := Vector3(inner.x * signf(n.x) if absf(n.x) > 1e-4 else 0.0, inner.y * signf(n.y) if absf(n.y) > 1e-4 else inner.y * (1.0 if i < rings / 2 else -1.0), inner.z * signf(n.z) if absf(n.z) > 1e-4 else 0.0)
			row.append([c + n * r, n])
		pts.append(row)
	for i in rings:
		for k in seg:
			var a: Array = pts[i][k]
			var b: Array = pts[i][k + 1]
			var c2: Array = pts[i + 1][k]
			var d: Array = pts[i + 1][k + 1]
			for p in [a, c2, b, b, c2, d]:
				st.set_normal(p[1])
				st.add_vertex(p[0])
	return st.commit()


static func _cyl(rt: float, rb: float, h: float, segs := 48) -> CylinderMesh:
	var c := CylinderMesh.new()
	c.top_radius = rt
	c.bottom_radius = rb
	c.height = h
	c.radial_segments = segs
	c.rings = 1
	return c


static func _sph(r: float, h := -1.0) -> SphereMesh:
	var s := SphereMesh.new()
	s.radius = r
	s.height = r * 2.0 if h < 0.0 else h
	s.radial_segments = 40
	s.rings = 20
	return s


static func _cap(r: float, h: float) -> CapsuleMesh:
	var c := CapsuleMesh.new()
	c.radius = r
	c.height = h
	c.radial_segments = 24
	c.rings = 8
	return c


static func _tor(r_in: float, r_out: float) -> TorusMesh:
	var t := TorusMesh.new()
	t.inner_radius = r_in
	t.outer_radius = r_out
	t.rings = 40
	t.ring_segments = 16
	return t


## a tube along a path (a faucet's gooseneck)
static func tube(path: PackedVector3Array, r: float, sides := 16) -> ArrayMesh:
	var st := SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
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
			for p in [a, b, c, b, d, c]:
				st.set_normal(p[1])
				st.add_vertex(p[0])
	return st.commit()


static func _add(parent: Node3D, mesh: Mesh, mat: Material, pos: Vector3, rot := Vector3.ZERO, sc := Vector3.ONE) -> MeshInstance3D:
	var mi := MeshInstance3D.new()
	mi.mesh = mesh
	mi.material_override = mat
	mi.position = pos
	mi.rotation = rot
	mi.scale = sc
	parent.add_child(mi)
	return mi


# ---------------------------------------------------------------- the room

## painted wall cabinets all the way round, up above the shelves and the hanging pans
static func _cabinets(g: Node3D, rw: float, top: float) -> void:
	var y_lo := 1250.0
	var y_hi := minf(top - 90.0, 1960.0)
	if y_hi - y_lo < 300.0:
		return
	var depth := 150.0
	var paint := _m("#7f9a86", 0.42, 0.0, 0.35)
	var paint_dk := _m("#5f7866", 0.6)
	var brass := _m("#c9a14a", 0.22, 1.0)
	var hgt := y_hi - y_lo
	var door_w := 230.0
	var n := int(TAU * (rw - depth) / door_w)
	var door := rbox(Vector3(door_w * 0.5 - 5.0, hgt * 0.5 - 8.0, 9.0), 4.0)
	var panel := rbox(Vector3(door_w * 0.5 - 34.0, hgt * 0.5 - 40.0, 5.0), 6.0)
	var handle := _cap(5.0, 120.0)
	var mm_door := MultiMesh.new()
	mm_door.transform_format = MultiMesh.TRANSFORM_3D
	mm_door.mesh = door
	mm_door.instance_count = n
	var mm_pan := MultiMesh.new()
	mm_pan.transform_format = MultiMesh.TRANSFORM_3D
	mm_pan.mesh = panel
	mm_pan.instance_count = n
	var mm_h := MultiMesh.new()
	mm_h.transform_format = MultiMesh.TRANSFORM_3D
	mm_h.mesh = handle
	mm_h.instance_count = n
	var yc := (y_lo + y_hi) * 0.5
	for i in n:
		var a := TAU * (float(i) + 0.5) / n
		var d := rw - depth
		var pos := Vector3(cos(a) * d, yc, sin(a) * d)
		# the door's face looks at the middle of the room
		var b := Basis.looking_at(Vector3(-cos(a), 0, -sin(a)), Vector3.UP)
		mm_door.set_instance_transform(i, Transform3D(b, pos))
		mm_pan.set_instance_transform(i, Transform3D(b, pos + b * Vector3(0, 0, -10.0)))
		var side := -1.0 if i % 2 == 0 else 1.0
		mm_h.set_instance_transform(i, Transform3D(b, pos + b * Vector3(side * (door_w * 0.5 - 30.0), -hgt * 0.5 + 110.0, -16.0)))
	for e in [[mm_door, paint], [mm_pan, paint], [mm_h, brass]]:
		var mmi := MultiMeshInstance3D.new()
		mmi.multimesh = e[0]
		mmi.material_override = e[1]
		g.add_child(mmi)
	# the cabinets' underside and their top, as rings
	_ring(g, rw - depth - 12.0, rw, y_lo - 9.0, 18.0, paint_dk)
	_ring(g, rw - depth - 22.0, rw, y_hi + 12.0, 26.0, paint)


static func _ring(g: Node3D, r0: float, r1: float, y: float, h: float, mat: Material) -> void:
	var st := SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	var n := 160
	for i in n:
		var a0 := TAU * i / n
		var a1 := TAU * (i + 1) / n
		var p := [Vector2(cos(a0), sin(a0)), Vector2(cos(a1), sin(a1))]
		for yy in [y - h * 0.5, y + h * 0.5]:
			var nn := Vector3.DOWN if yy < y else Vector3.UP
			var q := [Vector3(p[0].x * r0, yy, p[0].y * r0), Vector3(p[1].x * r0, yy, p[1].y * r0), Vector3(p[0].x * r1, yy, p[0].y * r1), Vector3(p[1].x * r1, yy, p[1].y * r1)]
			for v in [q[0], q[1], q[2], q[1], q[3], q[2]]:
				st.set_normal(nn)
				st.add_vertex(v)
		# the inner face, toward the room
		var f := [Vector3(p[0].x * r0, y - h * 0.5, p[0].y * r0), Vector3(p[1].x * r0, y - h * 0.5, p[1].y * r0), Vector3(p[0].x * r0, y + h * 0.5, p[0].y * r0), Vector3(p[1].x * r0, y + h * 0.5, p[1].y * r0)]
		for v in [f[0], f[2], f[1], f[1], f[2], f[3]]:
			st.set_normal(-Vector3(v.x, 0, v.z).normalized())
			st.add_vertex(v)
	var mi := MeshInstance3D.new()
	mi.mesh = st.commit()
	mi.material_override = mat
	(mi.material_override as BaseMaterial3D).cull_mode = BaseMaterial3D.CULL_DISABLED
	g.add_child(mi)


## a gooseneck faucet in polished chrome under a window, with a lever and a soap pump beside it
static func _faucet(g: Node3D, rw: float, a: float) -> void:
	var f := Node3D.new()
	var d := rw - 60.0 * SC
	f.position = Vector3(cos(a) * d, TABLE_Y, sin(a) * d)
	f.scale = Vector3.ONE * SC
	g.add_child(f)
	f.look_at_from_position(f.position, Vector3(0, TABLE_Y, 0), Vector3.UP)
	var chrome := _m("#e8ebef", 0.08, 1.0)
	_add(f, _cyl(22.0, 26.0, 16.0), chrome, Vector3(0, 8, 0))
	_add(f, _cyl(11.0, 13.0, 180.0), chrome, Vector3(0, 106, 0))
	# a half circle from the top of the riser, over toward the room and down
	var path := PackedVector3Array()
	for k in 25:
		var t2 := PI * float(k) / 24.0
		path.append(Vector3(0, 196.0 + sin(t2) * 62.0, -(62.0 - cos(t2) * 62.0)))
	_add(f, tube(path, 9.5), chrome, Vector3.ZERO)
	_add(f, _cyl(11.0, 9.0, 22.0), chrome, Vector3(0, 186, -124))
	_add(f, _cap(6.0, 70.0), chrome, Vector3(30, 60, 0), Vector3(0, 0, -1.1))
	# soap pump: amber glass bottle with a chrome pump
	var s := Node3D.new()
	s.position = Vector3(-95, 0, -10)
	f.add_child(s)
	_add(s, _cyl(20.0, 22.0, 90.0), _glass("#b8792a", 0.75), Vector3(0, 45, 0))
	_add(s, _cyl(8.0, 9.0, 24.0), chrome, Vector3(0, 102, 0))
	_add(s, rbox(Vector3(14, 4, 5), 3.0), chrome, Vector3(-6, 116, 0))


## one of the things kept along the counter, built at the origin facing -Z (toward the room after look_at)
static func _piece(kind: String) -> Node3D:
	var p := Node3D.new()
	match kind:
		"mixer", "mixer2":
			var enamel := _m("#c8261b" if kind == "mixer" else "#efe6d2", 0.22, 0.0, 0.8)
			var steel := _m("#d9dde2", 0.18, 1.0)
			_add(p, rbox(Vector3(70, 14, 44), 12.0), enamel, Vector3(0, 14, -10))
			_add(p, rbox(Vector3(30, 85, 34), 22.0), enamel, Vector3(0, 100, 22))
			_add(p, _cap(40.0, 190.0), enamel, Vector3(0, 196, -20), Vector3(PI / 2.0, 0, 0))
			_add(p, _cyl(48.0, 32.0, 80.0), steel, Vector3(0, 70, -40))
			_add(p, _tor(40.0, 48.0), steel, Vector3(0, 110, -40))
			_add(p, _cyl(5.0, 5.0, 40.0), steel, Vector3(0, 160, -48))
			_add(p, _tor(9.0, 13.0), steel, Vector3(0, 196, -112), Vector3(PI / 2.0, 0, 0))
		"toaster":
			var steel2 := _m("#c9cdd2", 0.32, 0.95)
			var dark := _m("#1b1b1d", 0.6)
			_add(p, rbox(Vector3(72, 50, 44), 18.0), steel2, Vector3(0, 52, 0))
			for x in [-22.0, 22.0]:
				_add(p, rbox(Vector3(7, 3, 32), 2.5), dark, Vector3(x, 101, 0))
			_add(p, rbox(Vector3(74, 5, 46), 4.0), dark, Vector3(0, 4, 0))
			_add(p, rbox(Vector3(4, 7, 9), 3.0), dark, Vector3(74, 70, 0))
			_add(p, _cyl(6.0, 6.0, 6.0, 24), dark, Vector3(0, 40, -45), Vector3(PI / 2.0, 0, 0))
		"kettle":
			var cream := _m("#e9dfcb", 0.2, 0.0, 0.9)
			var steel3 := _m("#cfd3d8", 0.15, 1.0)
			_add(p, _cyl(46.0, 58.0, 90.0), cream, Vector3(0, 52, 0))
			_add(p, _sph(46.0, 50.0), cream, Vector3(0, 97, 0))
			_add(p, _cyl(12.0, 6.0, 16.0, 24), steel3, Vector3(0, 124, 0))
			_add(p, _cyl(6.0, 11.0, 70.0, 24), cream, Vector3(0, 78, -64), Vector3(-0.9, 0, 0))
			var hp := PackedVector3Array()
			for k in 17:
				var t := PI * float(k) / 16.0
				hp.append(Vector3(0, 100.0 + sin(t) * 45.0, -cos(t) * 32.0))
			_add(p, tube(hp, 6.0), _m("#2a2420", 0.5), Vector3(0, 0, 0))
			_add(p, _cyl(58.0, 60.0, 8.0), steel3, Vector3(0, 4, 0))
		"coffee":
			var black := _m("#18181a", 0.18, 0.0, 0.7)
			var steel4 := _m("#d2d6db", 0.16, 1.0)
			_add(p, rbox(Vector3(55, 100, 58), 14.0), black, Vector3(0, 100, 4))
			_add(p, rbox(Vector3(50, 6, 40), 5.0), steel4, Vector3(0, 6, -50))
			_add(p, _cyl(30.0, 34.0, 70.0), _glass("#2a1a10", 0.82), Vector3(0, 48, -50))
			_add(p, _cyl(31.0, 31.0, 10.0), black, Vector3(0, 87, -50))
			_add(p, _cyl(8.0, 8.0, 6.0, 24), _m("#e04a2a", 0.3), Vector3(30, 170, -55), Vector3(PI / 2.0, 0, 0))
		"knives":
			var wood := _m("#8a5a33", 0.55)
			var black2 := _m("#141414", 0.35)
			var kb := Node3D.new()
			kb.rotation = Vector3(-0.32, 0, 0)
			kb.position = Vector3(0, 0, 10)
			p.add_child(kb)
			_add(kb, rbox(Vector3(38, 62, 48), 8.0), wood, Vector3(0, 62, 0))
			for i in 5:
				_add(kb, _cap(5.5 + (i % 2), 70.0), black2, Vector3(-24.0 + i * 12.0, 152, -10.0 + (i % 2) * 14.0), Vector3(0.05 * (i - 2), 0, 0.06 * (i - 2)))
		"crock":
			var ceramic := _m("#f1ead8", 0.15, 0.0, 0.8)
			var wood2 := _m("#b98a55", 0.5)
			_add(p, _cyl(34.0, 30.0, 85.0), ceramic, Vector3(0, 43, 0))
			_add(p, _tor(30.0, 36.0), ceramic, Vector3(0, 86, 0))
			for i in 4:
				var ang := -0.5 + i * 0.33
				var sp := Node3D.new()
				sp.position = Vector3(sin(ang) * 10.0, 60, cos(ang) * 6.0)
				sp.rotation = Vector3(0.22 * cos(ang * 3.0), 0, ang * 0.5)
				p.add_child(sp)
				_add(sp, _cap(3.5, 150.0), wood2, Vector3(0, 60, 0))
				_add(sp, _sph(14.0, 26.0), wood2, Vector3(0, 140, 0), Vector3.ZERO, Vector3(1, 1, 0.45))
			_add_boards(p, Vector3(85, 0, 25))
		"boards":
			_add_boards(p, Vector3(0, 0, 18))
		"bread":
			var wood3 := _m("#a4703f", 0.5)
			var cream2 := _m("#efe2c6", 0.3, 0.0, 0.5)
			_add(p, rbox(Vector3(95, 10, 55), 6.0), wood3, Vector3(0, 10, 0))
			_add(p, _cyl(55.0, 55.0, 186.0), cream2, Vector3(0, 62, 0), Vector3(0, 0, PI / 2.0))
			_add(p, rbox(Vector3(4, 6, 20), 3.0), wood3, Vector3(0, 70, -50))
		"towels":
			var chrome2 := _m("#e3e6ea", 0.1, 1.0)
			var paper := _m("#f7f5ef", 0.85)
			_add(p, _cyl(30.0, 30.0, 6.0), chrome2, Vector3(0, 3, 0))
			_add(p, _cyl(4.0, 4.0, 170.0, 16), chrome2, Vector3(0, 88, 0))
			_add(p, _cyl(32.0, 32.0, 140.0), paper, Vector3(0, 80, 0))
			_add(p, _sph(7.0), chrome2, Vector3(0, 176, 0))
		_:
			return null
	return p


## two wooden cutting boards leaning on the wall
static func _add_boards(p: Node3D, at: Vector3) -> void:
	for i in 2:
		var b := Node3D.new()
		b.position = at + Vector3(i * 40.0 - 20.0, 0, i * -6.0)
		b.rotation = Vector3(0.16, 0, (i - 0.5) * 0.08)
		p.add_child(b)
		var w := _m("#c79a62" if i == 0 else "#9b6a3c", 0.5)
		_add(b, rbox(Vector3(85.0 - i * 15.0, 125.0 - i * 20.0, 7), 18.0), w, Vector3(0, 125.0 - i * 20.0, 0))
