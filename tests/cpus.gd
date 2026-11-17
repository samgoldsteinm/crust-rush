extends Node
## The menu's rivals count (web v200 crust-cpus) on the PC: a race started from the menu has as many computer racers as chosen
## (it used to get a full grid: the start ran while the state was still "menu", which only the background race should check),
## and the menu's background race still has a full grid. Prints CPUS PASS / FAIL.

var main: Node


func _ready() -> void:
	main = load("res://scenes/main.tscn").instantiate()
	add_child(main)
	for i in 40:
		await get_tree().process_frame
	var bad := 0
	var bg: int = main.race.karts.size() if main.race != null else -1
	print("CPUS background race in the menu: %d karts" % bg)
	if bg != 8:
		bad += 1
	for n in [0, 1, 3]:
		main.sel["cpus"] = n
		main.sel["mode"] = "single"   # (a Sandbox test run before saves "sb" as the last mode)
		main.gp = {}
		main.state = "menu"
		await main._race_on(main.map_id)
		var got: int = main.race.karts.size() - 1
		print("CPUS chose %d rivals, the race has %d (state %s)" % [n, got, main.state])
		if got != n:
			bad += 1
		main._to_menu("")
		for i in 10:
			await get_tree().process_frame
	print("CPUS %s" % ("PASS" if bad == 0 else "FAIL"))
	get_tree().quit(0 if bad == 0 else 1)
