class_name WallBalls
## The walls of dough balls on the outside of the bends (web: "barrier walls of dough balls on the outside of bends"):
## two balls stacked at every walled point, alternating the theme's colour and cream. The track export missed many of
## them, so the PC places them all from the track data exactly as the web does (same spots, same heights, same
## colours), as smooth glossy balls. A ball the export did keep sits just inside the PC's slightly larger one.

static func build(parent: Node3D, T: TrackData) -> int:
	var N := T.N
	if N == 0 or T.wall.size() < N:
		return 0
	var night := T.theme == "night"
	var cold := T.theme == "freezer"
	var cA := Color("#3a6fd8") if night else (Color("#4aa8e8") if cold else Color("#e0452c"))
	var cB := Color("#e4ecff") if (night or cold) else Color("#fff4dc")
	var spots: Array = []
	for j in N:
		var w := T.wall[j]
		if w == 0:
			continue
		if T.multi and T.ey.size() > j and T.ey[j] > 0.5:
			continue
		# not where a shortcut leaves or rejoins on this side
		var skip := false
		for sc in T.shorts:
			var scd: Dictionary = sc
			if int(scd.get("s", 0)) != w:
				continue
			for e in [int(scd.get("a", -999)), int(scd.get("b", -999))]:
				var d := absi(j - e) % N
				if mini(d, N - d) <= 14:
					skip = true
		if skip:
			continue
		var o := (T.CURB + 11.0) * w
		var x := T.px[j] + T.nx[j] * o
		var z := T.py[j] + T.ny[j] * o
		var gy := T.ground(x, z)
		for r in 2:
			spots.append([Vector3(x, gy + 3.8 + r * 6.6, z), cA if (j + r) % 2 == 1 else cB])
	if spots.is_empty():
		return 0
	var mesh := SphereMesh.new()
	mesh.radius = 3.95
	mesh.height = 7.9
	mesh.radial_segments = 32
	mesh.rings = 16
	var mat := StandardMaterial3D.new()
	mat.vertex_color_use_as_albedo = true
	mat.roughness = 0.38
	mat.clearcoat_enabled = true
	mat.clearcoat = 0.4
	mat.clearcoat_roughness = 0.2
	mesh.material = mat
	# one multimesh per 600-unit cell, so far cells drop out of view like the rest of the scenery
	var cells := {}
	for s in spots:
		var p: Vector3 = s[0]
		var key := Vector2i(floori(p.x / 600.0), floori(p.z / 600.0))
		if not cells.has(key):
			cells[key] = []
		cells[key].append(s)
	var g := Node3D.new()
	g.name = "wall_balls"
	parent.add_child(g)
	for key in cells:
		var list: Array = cells[key]
		var mm := MultiMesh.new()
		mm.transform_format = MultiMesh.TRANSFORM_3D
		mm.use_colors = true
		mm.mesh = mesh
		mm.instance_count = list.size()
		for i in list.size():
			mm.set_instance_transform(i, Transform3D(Basis(), list[i][0]))
			mm.set_instance_color(i, list[i][1])
		var mmi := MultiMeshInstance3D.new()
		mmi.multimesh = mm
		mmi.visibility_range_end = 3200.0
		mmi.visibility_range_end_margin = 200.0
		mmi.visibility_range_fade_mode = GeometryInstance3D.VISIBILITY_RANGE_FADE_SELF
		g.add_child(mmi)
	return spots.size()
