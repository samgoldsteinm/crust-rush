extends Node
## The countdown view on CR_MAP (the start of a race, as the player sees it) to build/cd/<map>_<tag>.png, with the camera's
## and the kart's positions printed.
var main: Node


func _ready() -> void:
	main = load("res://scenes/main.tscn").instantiate()
	main.auto_drive = true
	add_child(main)
	var n := 0
	while main.state != "countdown" and n < 2000:
		await get_tree().process_frame
		n += 1
	var t0 := Time.get_ticks_msec()
	while Time.get_ticks_msec() - t0 < int(OS.get_environment("CD_MS") if OS.get_environment("CD_MS") != "" else "1500"):
		await get_tree().process_frame
	var dir := ProjectSettings.globalize_path("res://build/cd")
	DirAccess.make_dir_recursive_absolute(dir)
	var tag := "%s_%s" % [OS.get_environment("CR_MAP"), OS.get_environment("CD_TAG")]
	var img := get_viewport().get_texture().get_image()
	img.resize(960, 540, Image.INTERPOLATE_BILINEAR)
	img.save_png("%s/%s.png" % [dir, tag])
	print("CD shot ", tag, " state ", main.state, " cd ", main.cd, " cam ", main.cam.global_position, " kart ", Vector3(main.kart.x, main.kart.wy, main.kart.y), " grid ", main.race.karts.size(), " place ", main.kart.place)
	get_tree().quit(0)
