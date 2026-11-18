extends Node
## A delivery's arrow (pc74, web patch 74): Sandbox on Margherita, the Sauce Spiral delivery started: the arrow points at the gate to
## Basil Boulevard (the shortest way). CR_MODE=sb CR_MAP=margherita. With a window: build/menu/del_arrow.png. Prints DELARROW PASS / FAIL.

var main: Node


func _ready() -> void:
	main = load("res://scenes/main.tscn").instantiate()
	main.auto_drive = true
	add_child(main)
	for i in 600:
		await get_tree().create_timer(0.25).timeout
		if main.state == "race" and main.race != null and main.race.sb != null and main.race.sb.acts != null:
			break
	preload("res://scripts/sandbox.gd").no_save = true
	main.race.sb.acts.start("del_spiral")
	for i in 60:
		await get_tree().process_frame
	var arr: Array = main.hud.sb_arrow
	var hop: String = main._sb_next_hop("margherita", "spiral")
	var route: String = main._sb_route_next(main.race.sb, "spiral")   # (pc76) the quickest drivable way: from the start line, Basil (the web says the same)
	if DisplayServer.get_name() != "headless":
		DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path("res://build/menu"))
		get_viewport().get_texture().get_image().save_png(ProjectSettings.globalize_path("res://build/menu/del_arrow.png"))
	var ok: bool = arr.size() == 2 and String(arr[1]).begins_with("To Basil") and (hop == "basil" or hop == "oven") and route == "basil"
	print("DELARROW %s: hop %s, route %s, arrow %s" % ["PASS" if ok else "FAIL", hop, route, str(arr)])
	get_tree().quit(0 if ok else 1)
