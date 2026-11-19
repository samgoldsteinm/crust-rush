"""PC: the garage is the web's workshop room (web v224 patch 81), which the PC never had. The owner: "the pc version must not be fully
updated because i dont have the new garage in the game".
- godot/tools/studioexport.py exports gStudioSet from the web game (glbexport.js __exportStudio) to assets/garage_studio/studio.glb:
  concrete floor, brick walls, steel beams, LED panels and strip, the Garage track's scanned benches, chests, shelves, tyres, doors,
  rack, electrics and ladder, windows. Same units as the garage (the web's room sits round the same 15.5 disc).
- menu.gd _garage_scene: loads it round the turntable (if the file is there); a ReflectionProbe (UPDATE_ONCE) in the room's middle so
  the paint reflects the room, as the web's PMREM from the room does; the sky stays for the ambient light.
- _frame_garage_cam: the web's patch 87 ceiling rule (camera y <= 12.6: closer first, not nearer than 1.7 x the radius, then no higher);
  zoom out at most 1.1 (was 1.5) so the camera stays inside the room.
    python tools/mini/pc101.py      (once, after pc100)"""
G = 'D:/crust-rush/godot/scripts/'


def rep(f, a, b, n=1):
    p = G + f
    s = open(p, encoding='utf-8', newline='').read()
    assert s.count(a) == n, (f, s.count(a), a[:80])
    s = s.replace(a, b)
    open(p, 'w', encoding='utf-8', newline='').write(s)


rep('menu.gd', """	_gcam = Camera3D.new()
	_gcam.fov = 30.0
	w3.add_child(_gcam)
""", """	_gcam = Camera3D.new()
	_gcam.fov = 30.0
	w3.add_child(_gcam)
	# (pc101) the web's workshop room round the turntable (godot/tools/studioexport.py), and the paint reflecting it
	if ResourceLoader.exists("res://assets/garage_studio/studio.glb"):
		var ps = load("res://assets/garage_studio/studio.glb")
		if ps is PackedScene:
			var room: Node3D = (ps as PackedScene).instantiate()
			for mi in room.find_children("*", "MeshInstance3D", true, false):
				(mi as MeshInstance3D).cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
				(mi as MeshInstance3D).layers = 2   # the rim light (car only) skips the room: it glared on the polished concrete
			w3.add_child(room)
			var pr := ReflectionProbe.new()
			pr.update_mode = ReflectionProbe.UPDATE_ONCE
			pr.size = Vector3(66.0, 15.6, 56.0)
			pr.position = Vector3(0.0, 7.8, 0.0)
			pr.origin_offset = Vector3(0.0, -4.8, 0.0)   # captured from car height
			pr.box_projection = false
			pr.interior = true
			pr.ambient_mode = ReflectionProbe.AMBIENT_DISABLED
			pr.max_distance = 120.0
			pr.intensity = 0.5
			w3.add_child(pr)
""")
rep('menu.gd', """	rim.light_color = Color("#dfe8ff")
""", """	rim.light_color = Color("#dfe8ff")
	rim.light_cull_mask = 1   # (pc101) the car, not the workshop room (layer 2)
""")
rep('menu.gd', """	var d := _grad / sin(minf(vh, hh)) * (0.95 if _gbig else 0.84) * _gzc
	var el := 0.22 + _gpc
""", """	var d0 := _grad / sin(minf(vh, hh)) * (0.95 if _gbig else 0.84) * _gzc
	var el0 := 0.22 + _gpc
	# (pc101, web patch 87) under the room's ceiling: closer first (not nearer than 1.7 x the radius), then no higher
	var yM := 12.6
	var d := d0
	if sin(el0) > 0.02 and _gcy + sin(el0) * d0 > yM:
		d = maxf(minf(d0, _grad * 1.7), (yM - _gcy) / sin(el0))
	var el := minf(el0, asin(clampf((yM - _gcy) / d, -1.0, 1.0)))
""")
rep('menu.gd', "0.32, 1.5)", "0.32, 1.1)", 3)
print('pc101 applied')
