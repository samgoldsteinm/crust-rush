extends Node
## Prototype: a VoxelGI over the whole CR_MAP track, baked when the race loads (GI_SUB subdivisions); prints the bake time
## and saves the same chase views as mtnshots to build/gi/<map>_<tag>_<n>.png. GI_MODE: off | voxel | sdfgi
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
	var mode := OS.get_environment("GI_MODE")
	var map := OS.get_environment("CR_MAP")
	if mode == "voxel":
		var lo := Vector3(INF, INF, INF)
		var hi := Vector3(-INF, -INF, -INF)
		for j in T.N:
			var p := Vector3(T.px[j], T.ground(T.px[j], T.py[j]) + T.ey[j], T.py[j])
			lo = lo.min(p)
			hi = hi.max(p)
		lo -= Vector3(250, 60, 250)
		hi += Vector3(250, 220, 250)
		var gi := VoxelGI.new()
		gi.subdiv = VoxelGI.SUBDIV_512 if OS.get_environment("GI_SUB") == "512" else VoxelGI.SUBDIV_256
		gi.size = hi - lo
		gi.position = (lo + hi) * 0.5
		main.world.add_child(gi)
		var t0 := Time.get_ticks_msec()
		gi.bake(main.world)
		print("GI bake %d ms size %s" % [Time.get_ticks_msec() - t0, str(gi.size)])
		gi.data.energy = float(OS.get_environment("GI_E")) if OS.get_environment("GI_E") != "" else 1.0
	elif mode == "sdfgi":
		main.quality = 2
		main.gi_on = true
		main._apply_quality()
	var dir := ProjectSettings.globalize_path("res://build/gi")
	DirAccess.make_dir_recursive_absolute(dir)
	for i in 60:
		await get_tree().process_frame
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
		for i in 20:
			await get_tree().process_frame
		var img := get_viewport().get_texture().get_image()
		img.resize(960, 540, Image.INTERPOLATE_BILINEAR)
		img.save_png("%s/%s_%s_%d.png" % [dir, map, mode if mode != "" else "off", int(f * 100)])
	print("GI fps %d" % Engine.get_frames_per_second())
	get_tree().quit(0)
