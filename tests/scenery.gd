extends Node
## Scenery shots from a free camera (the scenery workflow, .github/workflows/scenery.yml): loads CR_MAP with the
## race held still and takes one picture per line of tests/scenery.txt for that map ("map name px,py,pz,tx,ty,tz",
## world units). PNGs go to build/scenery; each is also printed to the log as SHOT_PART lines (a JPEG in pieces).
var main: Node


func _ready() -> void:
	main = load("res://scenes/main.tscn").instantiate()
	main.auto_drive = true
	add_child(main)
	for i in 25:
		await get_tree().process_frame
	main.state = "race"
	main.race.state = "race"
	main.cd = 0.0
	main.test_hold = true
	main.paused = true
	var cam := Camera3D.new()
	cam.fov = 60.0
	cam.far = 30000.0
	cam.near = 0.5
	main.world.add_child(cam)
	var dir := ProjectSettings.globalize_path("res://build/scenery")
	DirAccess.make_dir_recursive_absolute(dir)
	var map := OS.get_environment("CR_MAP")
	for line in FileAccess.get_file_as_string("res://tests/scenery.txt").split("\n"):
		var f := line.strip_edges().split(" ", false)
		if f.size() < 3 or f[0] != map:
			continue
		var c := f[2].split(",")
		var p := Vector3(float(c[0]), float(c[1]), float(c[2]))
		var t := Vector3(float(c[3]), float(c[4]), float(c[5]))
		cam.look_at_from_position(p, t, Vector3.UP)
		cam.make_current()
		for k in 20:
			await get_tree().process_frame
		cam.make_current()
		await get_tree().process_frame
		var name := "%s_%s" % [map, f[1]]
		var img := get_viewport().get_texture().get_image()
		img.save_png(dir + "/" + name + ".png")
		var small := img.duplicate() as Image
		small.resize(1280, 720, Image.INTERPOLATE_BILINEAR)
		var b64 := Marshalls.raw_to_base64(small.save_jpg_to_buffer(0.85))
		var n := int(ceil(b64.length() / 3000.0))
		for k in n:
			print("SHOT_PART %s %d %d %s" % [name, k, n, b64.substr(k * 3000, 3000)])
		print("SCENERY shot ", name)
	get_tree().quit(0)
