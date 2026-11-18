extends Node
## A race with a cheat on does not count towards records (pc79, web patch 79): one race; for each case race_taint is cleared, the setting
## put on, and a few frames run. Nothing / UNLOCK / field of view + HUD: not tainted. Top speed, invincible, auto-drive: tainted.
## Prints CHEAT PASS / FAIL. (The saving itself: web tools/neon/cheattest.py; main._progress_finish skips Ach.record and lb when tainted.)

var main: Node


func _off() -> void:
	main.dev_u = false
	main.dev = main.DEV_DEF.duplicate(true)
	main.race.dev = {}
	main.test_drive = false
	Ach.cheat = false


func _ready() -> void:
	main = load("res://scenes/main.tscn").instantiate()
	add_child(main)
	for i in 40:
		await get_tree().process_frame
	main.sel["cpus"] = 2
	main.sel["mode"] = "single"
	main.gp = {}
	main.state = "menu"
	await main._race_on(main.map_id)
	for i in 600:
		if main.state == "race":
			break
		await get_tree().create_timer(0.1).timeout
	var cases := [["clean", func(): pass, false], ["unlock", func(): Ach.cheat = true, false],
		["looks", func(): main.dev_u = true; main.dev["fov"] = 80.0; main.dev["hud"] = 0, false],
		["speed", func(): main.dev_u = true; main.dev["spd"] = 1.5; main.race.dev = main.dev_race().duplicate(true), true],
		["invincible", func(): main.dev_u = true; main.dev["inv"] = 1, true],
		["autodrive", func(): main.test_drive = true, true]]
	var bad := 0
	for c in cases:
		_off()
		main.race_taint = false
		(c[1] as Callable).call()
		for i in 10:
			await get_tree().physics_frame
		var got: bool = main.race_taint
		print("CHEAT %-10s tainted %s (want %s)" % [c[0], got, c[2]])
		if got != bool(c[2]):
			bad += 1
	_off()
	print("CHEAT %s" % ("PASS" if bad == 0 else "FAIL"))
	get_tree().quit(0 if bad == 0 else 1)
