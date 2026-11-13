class_name HdToy
## The Miniature Mayhem tracks on the PC: toy racing sets built round real rooms. Drawing only.
## The sun reaches the room only through its windows, as in the web game since v155: the walls and the ceiling throw
## shadows (both sides), so the room is in shade except for the patches the window lets in. The skirting, the picture of
## outdoors behind the window, the glass and the soft dark patches under furniture never throw one.
## The track's plastic is glossy and mirrors the room: a reflection probe the size of the room, taken once, stands in
## for the room photograph the web game uses (toyRoomEnv). The shell's materials are named toy_pt_wall*, toy_pt_ceiling,
## toy_pt_skirting, toy_outside, toy_gs_* (glass), toy_aoshade*; the plastics toy_toyroad*, toy_toyorange,
## toy_toyplastic*, toy_toyblue, toy_toydash.
## The room itself (the furniture built in Blender, the oak floor's boards and relief, the garden behind the window) comes
## with the exported track: after the web game's room changes, re-run the track export and rebuild.


static func upgrade(root: Node3D) -> int:
	var n := 0
	var box := AABB()
	var have := false
	for node in root.find_children("*", "MeshInstance3D", true, false):
		var mi := node as MeshInstance3D
		if mi.mesh == null:
			continue
		for si in mi.mesh.get_surface_count():
			var m := mi.mesh.surface_get_material(si) as BaseMaterial3D
			if m == null:
				continue
			var nm := String(m.resource_name)
			if not nm.begins_with("toy_"):
				continue
			if nm.begins_with("toy_pt_wall") or nm.begins_with("toy_pt_ceiling"):
				mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_DOUBLE_SIDED
				var wb: AABB = mi.global_transform * mi.get_aabb()
				box = wb if not have else box.merge(wb)
				have = true
				n += 1
			elif nm.begins_with("toy_pt_skirting") or nm.begins_with("toy_outside") or nm.begins_with("toy_gs_") or nm.begins_with("toy_aoshade") or nm.begins_with("toy_toydash"):
				mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
			# the track, its walls and the piers: glossy moulded plastic that mirrors the room
			if nm.begins_with("toy_toyroad") or nm.begins_with("toy_toyorange") or nm.begins_with("toy_toyplastic") or nm.begins_with("toy_toyblue"):
				m.roughness = 0.34
				m.clearcoat_enabled = true
				m.clearcoat = 1.0
				m.clearcoat_roughness = 0.07
			if nm.begins_with("toy_outside"):
				m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
				m.disable_fog = true
	if have:
		root.set_meta("toy_room", box)
	return n


## a reflection of the room, taken once when the track is loaded: the track, the karts and the floor mirror the window
## and the walls, never the open sky. `amb` is the room's soft fill light, kept as the web game has it.
static func add_probe(world: Node3D, root: Node3D, amb: Color, amb_energy: float) -> void:
	if not root.has_meta("toy_room"):
		return
	var box: AABB = root.get_meta("toy_room")
	var rp := ReflectionProbe.new()
	rp.size = box.size + Vector3(8, 8, 8)
	rp.position = box.get_center()
	rp.origin_offset = Vector3(-120, 220, 200) - box.get_center()   # the open spot over the rug the web game photographs from
	rp.box_projection = true
	rp.interior = true
	rp.enable_shadows = true
	rp.update_mode = ReflectionProbe.UPDATE_ONCE
	rp.ambient_mode = ReflectionProbe.AMBIENT_COLOR
	rp.ambient_color = amb
	rp.ambient_color_energy = amb_energy
	rp.max_distance = box.size.length()
	world.add_child(rp)
