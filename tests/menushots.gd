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
		[6, func(): main.menu.show_modal("mp"), "p_mp"],
		[6, func(): main.menu.show_modal("how"), "p_how"],
		[6, func():
			main.menu.close_modal()
			main.menu.open("driver"), "p_driver"],
		[6, func(): main.menu.open("track"), "p_track"],
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
