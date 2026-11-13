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
	for i in cams.size():
		var v := cams[i].split_floats(",")
		if v.size() < 6:
			continue
		cam.look_at_from_position(Vector3(v[0], v[1], v[2]), Vector3(v[3], v[4], v[5]), Vector3.UP)
		for j in 20:
			cam.make_current()
			await get_tree().process_frame
		get_viewport().get_texture().get_image().save_png("%s/room_%s_%d.png" % [dir, tag, i])
		print("ROOM shot ", i)
	get_tree().quit()
