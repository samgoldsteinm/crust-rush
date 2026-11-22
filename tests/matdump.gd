extends Node
## Prints every material on the loaded CR_MAP track: name, triangle count, roughness, metallic, texture, colour.
var main: Node


func _ready() -> void:
	main = load("res://scenes/main.tscn").instantiate()
	main.auto_drive = true
	add_child(main)
	for i in 10:
		await get_tree().process_frame
	var seen := {}
	for node in main.world.find_children("*", "MeshInstance3D", true, false):
		var mi := node as MeshInstance3D
		if mi.mesh == null:
			continue
		for si in mi.mesh.get_surface_count():
			var m := mi.get_active_material(si)
			if m == null:
				continue
			var key := "%s|%s" % [m.resource_name, mi.name]
			var tris := 0
			var arr := mi.mesh.surface_get_arrays(si) if mi.mesh is ArrayMesh else []
			if arr.size() > 0 and arr[Mesh.ARRAY_INDEX] != null:
				tris = (arr[Mesh.ARRAY_INDEX] as PackedInt32Array).size() / 3
			var nm := String(m.resource_name)
			if not seen.has(nm):
				seen[nm] = [0, 0, ""]
			seen[nm][0] += 1
			seen[nm][1] += tris
			if m is StandardMaterial3D:
				var s := m as StandardMaterial3D
				seen[nm][2] = "r%.2f m%.2f tex%s col%s node %s" % [s.roughness, s.metallic, s.albedo_texture != null, s.albedo_color.to_html(false), mi.name]
			else:
				seen[nm][2] = "shader node %s" % mi.name
	for nm in seen:
		print("MAT %s n%d tris%d %s" % [nm, seen[nm][0], seen[nm][1], seen[nm][2]])
	get_tree().quit(0)
