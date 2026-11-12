class_name HdToy
## The Miniature Mayhem tracks on the PC: toy racing sets built round real rooms. Drawing only.
## The room's shell (walls, ceiling, skirting, the window and the picture of outdoors behind it) never throws a
## shadow: the sun lights the whole room the way it does in the web game, and the furniture, the track and the karts
## throw theirs. The shell's materials are named toy_pt_wall*, toy_pt_ceiling, toy_pt_skirting, toy_outside,
## toy_gs_* (glass) and toy_aoshade* (the soft dark patches under furniture). The track's plastic (toy_toyroad,
## toy_toyorange, toy_toyblue) loses its lacquer shine, which washed the orange out under the PC's brighter sun.


static func upgrade(root: Node3D) -> int:
	var n := 0
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
			if nm.begins_with("toy_pt_wall") or nm.begins_with("toy_pt_ceiling") or nm.begins_with("toy_pt_skirting") or nm.begins_with("toy_outside") or nm.begins_with("toy_gs_") or nm.begins_with("toy_aoshade"):
				mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
				n += 1
			# the orange track and the blue piers: plain moulded plastic, no lacquer shine washing the colour out
			if nm.begins_with("toy_toyroad") or nm.begins_with("toy_toyorange") or nm.begins_with("toy_toyblue"):
				m.clearcoat_enabled = false
				m.roughness = 0.55
			# indoors nothing mirrors the open sky: the web game turns its sky reflections right down on these
			# materials, and here the same is done with the mirror strength (metal and glass keep theirs)
			if not (nm.begins_with("toy_mt_") or nm.begins_with("toy_gs_")) and m.metallic < 0.5:
				m.metallic_specular = minf(m.metallic_specular, 0.16)
			if nm.begins_with("toy_outside"):
				m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
				m.disable_fog = true
	return n
