extends Node
## The underglow on the PC (pc71): the scissor car, orange, an underglow colour (UG_GL, default 1 ice blue), in the garage's preview
## (build/menu/pc_garage.png) or, with UG_RACE=1 and CR_MODE=single CR_MAP=<id>, in a race behind the kart (build/menu/pc_race.png).
## Run with a window.

var main: Node


func _shot(name_: String) -> void:
	for i in 6:
		await get_tree().process_frame
	get_viewport().get_texture().get_image().save_png(ProjectSettings.globalize_path("res://build/menu/%s.png" % name_))
	print("UG shot ", name_)


func _ready() -> void:
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path("res://build/menu"))
	main = load("res://scenes/main.tscn").instantiate()
	main.auto_drive = OS.get_environment("UG_RACE") != ""
	add_child(main)
	for i in 40:
		await get_tree().process_frame
	var bi := 0
	var bodies: Array = KartBuilder.info.get("bodies", [])
	for j in bodies.size():
		if String(bodies[j].get("id", "")) == String(OS.get_environment("UG_BODY") if OS.get_environment("UG_BODY") != "" else "scissor"):
			bi = j
	var gl := int(OS.get_environment("UG_GL")) if OS.get_environment("UG_GL") != "" else 1
	var b := {"b": bi, "w": 0, "g": 0, "p": int(OS.get_environment("UG_P")) if OS.get_environment("UG_P") != "" else 2, "t": "", "st": {"gl": gl} if gl > 0 else {}}
	if OS.get_environment("UG_COMBO") != "":
		var cb: Dictionary = preload("res://scripts/style.gd").COMBOS[int(OS.get_environment("UG_COMBO"))]
		b = {"b": bi, "w": 0, "g": 0, "p": int(cb["p"]), "t": "", "st": (cb["st"] as Dictionary).duplicate()}
	var nm := String(OS.get_environment("UG_NAME")) if OS.get_environment("UG_NAME") != "" else "pc_garage"
	if OS.get_environment("UG_RACE") == "":
		main.menu.g_tab = String(OS.get_environment("UG_TAB")) if OS.get_environment("UG_TAB") != "" else "car"
		main.menu.build = b
		main.menu.open("garage")
		for i in 20:
			await get_tree().process_frame
		var big := OS.get_environment("UG_BIG") != ""
		if big:
			main.menu._set_big(true)
			for i in 10:
				await get_tree().process_frame
		main.menu._grot = float(OS.get_environment("UG_ROT")) if OS.get_environment("UG_ROT") != "" else 1.0
		main.menu._gzoom = 0.62 if big else 1.5
		main.menu._gzc = main.menu._gzoom
		main.menu._gpitch = 0.12 if big else 0.35
		main.menu._gpc = main.menu._gpitch
		main.menu._frame_garage_cam()
		for i in 4:
			await get_tree().process_frame
		await _shot(nm)
		get_tree().quit(0)
		return
	main.sel["build"] = b
	main.menu.build = b
	main._start_race({})
	for i in 600:
		await get_tree().process_frame
		if main.state == "race":
			break
	for i in 200:
		await get_tree().process_frame
	await _shot("pc_race")
	get_tree().quit(0)
