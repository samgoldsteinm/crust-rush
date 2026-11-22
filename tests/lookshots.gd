extends Node
## The pc117 look, on or off (LOOK=on|off; for off run with CR_NOGI=1 CR_NOROAD=1 too): three held chase views round
## CR_MAP, then the race let go for a while (tyre marks, fog in motion) and two more, to build/look/<map>_<look>_<n>.png.
var main: Node


func _shot(dir: String, tag: String) -> void:
	var img := get_viewport().get_texture().get_image()
	img.resize(1280, 720, Image.INTERPOLATE_BILINEAR)
	img.save_png("%s/%s.png" % [dir, tag])


func _ready() -> void:
	main = load("res://scenes/main.tscn").instantiate()
	main.auto_drive = true
	add_child(main)
	for i in 25:
		await get_tree().process_frame
	var on := OS.get_environment("LOOK") == "on"
	var map := OS.get_environment("CR_MAP")
	var T: TrackData = main.T
	main.quality = 2
	main.fog_on = on
	main.ssr_on = on
	main.grade_on = on
	main.marks_on = on
	main.fx.marks_on = on
	main.light_mode = "baked" if on else "off"
	if on and main.baked_gi == null:
		main.baked_gi = HdLook.bake_gi(main.world, T)
	main._apply_quality()
	main.test_hold = true
	main.state = "race"
	main.race.state = "race"
	main.cd = 0.0
	main.paused = true
	var dir := ProjectSettings.globalize_path("res://build/look")
	DirAccess.make_dir_recursive_absolute(dir)
	var lk := "on" if on else "off"
	for f in [0.05, 0.35, 0.65]:
		var j := int(f * T.N)
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
		for i in 10:
			await get_tree().process_frame
		Engine.time_scale = 1.0
		for i in 30:
			await get_tree().process_frame
		_shot(dir, "%s_%s_%d" % [map, lk, int(f * 100)])
	# let the race go: the karts drift and leave their marks
	var k0: Kart = main.kart
	var j0 := 0
	k0.x = T.px[j0]
	k0.y = T.py[j0]
	k0.a = T.ang[j0]
	k0.ma = k0.a
	k0.idx = j0
	k0.wy = T.ground(k0.x, k0.y) + T.k_ey(j0, k0.x, k0.y)
	k0._save_prev()
	main.cam_snap = true
	main.test_hold = false
	main.paused = false
	for n in 2:
		var t0 := Time.get_ticks_msec()
		while Time.get_ticks_msec() - t0 < 14000:
			await get_tree().process_frame
		_shot(dir, "%s_%s_run%d" % [map, lk, n])
	print("LOOK fps %d marks %d" % [Engine.get_frames_per_second(), main.fx.mk_n])
	# the newest tyre marks, from above
	if main.fx.mk_n > 0:
		main.paused = true
		var last: Transform3D = main.fx.mk_mm.get_instance_transform((main.fx.mk_next - 1 + main.fx.MARKS) % main.fx.MARKS)
		var cam := Camera3D.new()
		cam.fov = 50.0
		cam.far = 20000.0
		main.world.add_child(cam)
		cam.look_at_from_position(last.origin + Vector3(25, 45, 25), last.origin, Vector3.UP)
		cam.make_current()
		for i in 5:
			await get_tree().process_frame
		_shot(dir, "%s_%s_marks" % [map, lk])
	get_tree().quit(0)
