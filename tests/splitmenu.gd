extends Node
## Split screen's menu (pc120): the home screen with Players 2, player 2's driver screen, a split race paused, and its results,
## to build/menu/split_*.png.

var main: Node
var steps: Array = []
var si := 0
var wait := 0


func _ready() -> void:
	main = load("res://scenes/main.tscn").instantiate()
	add_child(main)
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path("res://build/menu"))
	steps = [
		[8, func():
			main.sel["mode"] = "single"
			main.sel["players"] = 2
			main.menu.mode = "single"
			main.menu.players = 2
			main.menu.open("home"), "split_home"],
		[6, func(): main.menu.open("track"), "split_driver2"],
		[14, func():
			print("SPLITMENU p1 build before ", main.menu.build, " ri ", main.menu.ri, " p2_ri ", main.menu.p2_ri)
			main.menu.open("garage2"), "split_garage2"],
		[14, func():
			main.menu.build["b"] = 3
			main.menu._build_changed(), "split_garage2b"],
		[8, func():
			main.menu.open("track")
			print("SPLITMENU after: screen ", main.menu.cur, " p1 build ", main.menu.build, " ri ", main.menu.ri, " p2 build ", main.menu.p2_build, " sel p2_build ", main.sel.get("p2_build")), "split_track"],
		[30, func():
			main._start_race({})
			print("SPLITMENU race: kart2 ", main.kart2.racer_name if main.kart2 else "-", " body ", main.kart2.info.get("body", "?") if main.kart2 else "-", " | kart1 body ", main.kart.info.get("body", "?"))
			main.state = "race"
			main.race.state = "race", ""],
		[60, func(): main._toggle_pause(), "split_pause"],
		[10, func():
			main._toggle_pause()
			main.state = "results"
			main._show_results(), "split_results"],
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
