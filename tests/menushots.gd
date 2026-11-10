extends Node
## Renders each menu screen (home, driver, track, settings, play with friends) to build/menu/*.png,
## for side-by-side checks against the web game's menus.

var main: Node
var steps: Array = []
var si := 0
var wait := 0


func _ready() -> void:
	main = load("res://scenes/main.tscn").instantiate()
	add_child(main)
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path("res://build/menu"))
	steps = [
		[8, func(): pass, "p_home"],
		[6, func(): main.menu.show_modal("set"), "p_set"],
		[6, func():
			main.set_tab = "items"
			main.menu.show_modal("set"), "p_set_items"],
		[6, func():
			main.set_tab = "gameplay"
			main.menu.show_modal("set"), "p_set_gameplay"],
		[6, func():
			main.set_tab = "controls"
			main.menu.show_modal("set"), "p_set_controls"],
		[6, func(): main.menu.show_modal("mp"), "p_mp"],
		[6, func(): main.menu.show_modal("how"), "p_how"],
		[6, func(): main.menu.show_modal("rec"), "p_rec"],
		[6, func(): main.menu.show_modal("ach"), "p_ach"],
		[6, func():
			main.menu.close_modal()
			main.menu.open("driver"), "p_driver"],
		[14, func():
			main.menu.g_tab = "kart"
			main.menu.open("garage"), "p_garage"],
		[10, func():
			main.menu.g_tab = "car"
			main.menu.open("garage"), "p_garage_car"],
		[10, func():
			main.menu.g_tab = "theme"
			main.menu.build["t"] = "flame"
			main.menu.open("garage"), "p_garage_theme"],
		[10, func():
			main.menu.g_tab = "glider"
			main.menu.build["b"] = 1
			main.menu.open("garage"), "p_garage_glider"],
		[6, func(): main.menu.open("track"), "p_track"],
		[6, func():
			main.sel["mode"] = "single"
			main.menu.mode = "single"
			main.menu.open("track"), "p_track_single"],
		[10, func():
			main._start_race({})
			main.state = "race"
			main.race.state = "race"
			main._toggle_pause(), "p_pause"],
		[10, func():
			main._toggle_pause()
			main.gp = {"cup": 0, "race": 0, "pts": [0, 0, 0, 0, 0, 0, 0, 0], "tracks": ["bay", "bay", "bay", "bay"]}
			main.state = "results"
			main._show_results(), "p_results"],
	]
	wait = 4


func _process(_dt: float) -> void:
	if wait > 0:
		wait -= 1
		return
	if si > 0 and String(steps[si - 1][2]) != "":
		var img := get_viewport().get_texture().get_image()
		img.save_png(ProjectSettings.globalize_path("res://build/menu/%s.png" % steps[si - 1][2]))
		print("MENU shot ", steps[si - 1][2])
	if si >= steps.size():
		get_tree().quit(0)
		return
	(steps[si][1] as Callable).call()
	wait = int(steps[si][0])
	si += 1
