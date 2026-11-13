extends Node
## Pictures of a track from fixed cameras, for comparing the PC with the web game's free-camera photos
## (web: tools/neon/shots.py, same camera numbers: x, height, z of the camera, then of the point it looks at).
## CR_MAP=<track> CR_CAMS="px,py,pz,tx,ty,tz;..." CR_TAG=<name>  ->  build/shots/room_<name>_<n>.png
## Run with a window (it needs the graphics card): godot --path . --resolution 1280x720 res://tests/room.tscn

var main: Node


func _ready() -> void:
	main = load("res://scenes/main.tscn").instantiate()
	main.auto_drive = true
	add_child(main)
	_run()


func _run() -> void:
	for i in 120:
		await get_tree().process_frame
	main.test_hold = true
	if main.hud != null:
		main.hud.visible = false
	var cam := Camera3D.new()
	cam.fov = 60.0
	cam.near = 1.6
	cam.far = 22000.0
	add_child(cam)
	main._toy_dof()
	cam.attributes = main.cam.attributes   # the game camera's own settings (background blur on toy tracks)
	var dir := ProjectSettings.globalize_path("res://build/shots")
	DirAccess.make_dir_recursive_absolute(dir)
	var tag := OS.get_environment("CR_TAG")
	var cams := OS.get_environment("CR_CAMS").split(";", false)
	# CR_BOOST=<drift tier 0..3>: every kart boosts while the pictures are taken, to look at the boost flames
	var bt := OS.get_environment("CR_BOOST")
	for i in cams.size():
		var v := cams[i].split_floats(",")
		if v.size() == 3:
			# three numbers: a view from behind the player's kart (back, to the side, up)
			var pk: Kart = main.kart
			var ca := cos(pk.ma)
			var sa := sin(pk.ma)
			print("ROOM kart at ", pk.x, ", ", pk.wy, ", ", pk.y)
			cam.look_at_from_position(Vector3(pk.x - ca * v[0] + sa * v[1], pk.wy + v[2], pk.y - sa * v[0] - ca * v[1]), Vector3(pk.x + ca * 6.0, pk.wy + 3.0, pk.y + sa * 6.0), Vector3.UP)
		elif v.size() < 6:
			continue
		else:
			cam.look_at_from_position(Vector3(v[0], v[1], v[2]), Vector3(v[3], v[4], v[5]), Vector3.UP)
		for j in 20:
			if bt != "":
				main.state = "race"   # so the boost streaks at the screen's edges show (the race itself is held still)
				if OS.get_environment("CR_MBLUR") != "":
					main.mblur_on = true
					main.kart.speed = main.kart.base_max * float(OS.get_environment("CR_MBLUR"))   # motion blur and wind at this share of top speed
				for k in main.race.karts:
					k.boost = 1.4
					k.b_pk = 1.6
					k.f_tier = int(bt)
			cam.make_current()
			await get_tree().process_frame
		get_viewport().get_texture().get_image().save_png("%s/room_%s_%d.png" % [dir, tag, i])
		print("ROOM shot ", i)
	get_tree().quit()
