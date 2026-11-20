"""PC: the cheese hills as the web's. The owner: "these mountains are all messed up on pc compared to the web version".
The web lays its ground picture on with world triplanar mapping (triplanar(mat,110): three projections of world x/110,
blended by the surface's direction to the 4th power), a shader change the glTF export can't carry, so the PC kept only the
top-down UVs (x/110, z/110) and every steep crust slope smeared the cheese into long streaks. Now the ground materials
(the exporter's "terrain_N") get Godot's world triplanar at 1/110, sharpness 4: the same on the flat, right on the slopes.
With or without Finished models.
    python tools/mini/pc109.py      (once, after pc108)"""
G = 'D:/crust-rush/godot/scripts/'


def patch(f, pairs):
    p = G + f
    s = open(p, encoding='utf-8', newline='').read()
    assert 'pc109' not in s, (f, 'already patched')
    for a, b in pairs:
        assert s.count(a) == 1, (f, s.count(a), a[:80])
        s = s.replace(a, b)
    open(p, 'w', encoding='utf-8', newline='').write(s)


patch('hd_ground.gd', [("""static var _grain: NoiseTexture2D
""", """static var _grain: NoiseTexture2D


## (pc109) the web's ground picture is laid on from three sides (its triplanar(mat, 110)), so the steep crust slopes
## aren't streaked: the ground materials ("terrain_N") the same, with or without the finished ground
static func triplanar(root: Node) -> int:
	var n := 0
	for node in root.find_children("*", "MeshInstance3D", true, false):
		var mi := node as MeshInstance3D
		if mi.mesh == null:
			continue
		for si in mi.mesh.get_surface_count():
			var m := mi.mesh.surface_get_material(si) as StandardMaterial3D
			if m == null or m.uv1_triplanar or not String(m.resource_name).begins_with("terrain"):
				continue
			m.uv1_triplanar = true
			m.uv1_world_triplanar = true
			m.uv1_scale = Vector3(1.0 / 110.0, 1.0 / 110.0, 1.0 / 110.0)
			m.uv1_triplanar_sharpness = 4.0
			n += 1
	return n
""")])
patch('world_build.gd', [("""func _prepare_track(root: Node) -> void:
	_use_vertex_colours(root)
""", """func _prepare_track(root: Node) -> void:
	_use_vertex_colours(root)
	HdGround.triplanar(root)   # (pc109)
""")])
patch('main.gd', [("""	print("vertex colours switched on for %d track materials" % _use_vertex_colours(root))
""", """	print("vertex colours switched on for %d track materials" % _use_vertex_colours(root))
	HdGround.triplanar(root)   # (pc109)
""")])
print('pc109 applied')
