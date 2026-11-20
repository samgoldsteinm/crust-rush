extends Node
## Sandbox street lamps at night on the PC: fast-travels to SBL_TO (default napoli), night, pictures on the road
## (build/menu/lamps_on.png) and off it beside the road (lamps_off.png). Prints SBLAMPS with the lamp count. Run with a window.

var main: Node


func _ready() -> void:
	main = load("res://scenes/main.tscn").instantiate()
	main.auto_drive = true
	add_child(main)
	for i in 400:
		await get_tree().process_frame
		if main.state == "race" and main.race != null and main.race.sb != null and main.sb_view != null and main.sb_view.night != null:
			break
	var to := OS.get_environment("SBL_TO") if OS.get_environment("SBL_TO") != "" else "napoli"
	main._sb_travel(to, "")
	for i in 1500:
		await get_tree().process_frame
		if main.sb_go.is_empty() and String(main.race.sb.id) == to and main.sb_view.night != null:
			break
	main.race.sb.park = true
	main.race.sb.save["t"] = 0.95
	for i in 120:
		await get_tree().process_frame
	var N = main.sb_view.night
	_shot("lamps_on")
	var k = main.kart
	var T = main.T
	var j := clampi(k.idx + 20, 0, T.N - 1)
	k.x = T.px[j] + T.nx[j] * 70.0
	k.y = T.py[j] + T.ny[j] * 70.0
	for i in 120:
		await get_tree().process_frame
	_shot("lamps_off")
	print("SBLAMPS id %s lamps %d pool %d spot %.2f" % [main.race.sb.id, N.lamps.size(), N.pool.size(), N.spot.light_energy])
	get_tree().quit(0)


func _shot(nm: String) -> void:
	get_viewport().get_texture().get_image().save_png(ProjectSettings.globalize_path("res://build/menu/%s.png" % nm))
