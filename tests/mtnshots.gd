extends Node
## Chase-camera views round CR_MAP, held still, to build/mtn/<map>_<hd>_<j>.png (CR_HD=0: the web's own shapes).
## For comparing the mountains with and without the PC's finished models.
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
	var dir := ProjectSettings.globalize_path("res://build/mtn")
	DirAccess.make_dir_recursive_absolute(dir)
	var T: TrackData = main.T
	var tag := "%s_%s" % [OS.get_environment("CR_MAP"), "web" if OS.get_environment("CR_HD") == "0" else "hd"]
	for f in [0.05, 0.2, 0.35, 0.5, 0.65, 0.8]:
		var j := int(f * T.N)
		var k: Kart = main.kart
		k.x = T.px[j]
		k.y = T.py[j]
		k.a = T.ang[j]
		k.ma = k.a
		k.idx = j
		k.wy = T.ground(k.x, k.y)
		k.last_g = NAN
		k.air = false
		k.speed = 0.0
		k._save_prev()
		main.cam_snap = true
		Engine.time_scale = 6.0
		for i in 10:
			await get_tree().process_frame
		Engine.time_scale = 1.0
		var img := get_viewport().get_texture().get_image()
		img.resize(1280, 720, Image.INTERPOLATE_BILINEAR)
		img.save_png("%s/%s_%d.png" % [dir, tag, int(f * 100)])
		print("MTN shot ", tag, " ", j)
	get_tree().quit(0)
