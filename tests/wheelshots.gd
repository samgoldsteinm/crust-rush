extends Node
## The player's kart from the side at wheel height, at six points round CR_MAP, held still, to build/wheels/<map>_<n>.png:
## for seeing whether the wheels sit on the road or sink into it. Prints the kart's height and the road's there.
var main: Node


func _ready() -> void:
	main = load("res://scenes/main.tscn").instantiate()
	main.auto_drive = true
	add_child(main)
	for i in 25:
		await get_tree().process_frame
	main.test_hold = true
	main.state = "race"
	main.race.state = "race"
	main.cd = 0.0
	main.paused = true
	var T: TrackData = main.T
	var dir := ProjectSettings.globalize_path("res://build/wheels")
	DirAccess.make_dir_recursive_absolute(dir)
	var cam := Camera3D.new()
	cam.fov = 40.0
	cam.near = 0.3
	cam.far = 20000.0
	main.world.add_child(cam)
	var map := OS.get_environment("CR_MAP")
	for n in 6:
		var j := int((float(n) + 0.15) / 6.0 * T.N)
		var k: Kart = main.kart
		k.x = T.px[j]
		k.y = T.py[j]
		k.a = T.ang[j]
		k.ma = k.a
		k.idx = j
		k.wy = T.ground(k.x, k.y) + T.k_ey(j, k.x, k.y)
		k.last_g = NAN
		k.air = false
		k.speed = 0.0
		k._save_prev()
		main.cam_snap = true
		Engine.time_scale = 6.0
		for i in 8:
			await get_tree().process_frame
		Engine.time_scale = 1.0
		var side := Vector3(T.nx[j], 0.0, T.ny[j])
		var kp := Vector3(k.x, k.wy, k.y)
		cam.look_at_from_position(kp + side * 22.0 + Vector3(0, float(OS.get_environment("WH_UP")) if OS.get_environment("WH_UP") != "" else 2.2, 0), kp + Vector3(0, 1.5, 0), Vector3.UP)
		cam.make_current()
		for i in 3:
			await get_tree().process_frame
		var img := get_viewport().get_texture().get_image()
		img.resize(640, 360, Image.INTERPOLATE_BILINEAR)
		img.save_png("%s/%s_%d.png" % [dir, map, n])
		print("WHEEL %s %d j %d wy %.2f ground %.2f ey %.2f" % [map, n, j, k.wy, T.ground(k.x, k.y), T.k_ey(j, k.x, k.y)])
	get_tree().quit(0)
