extends Node
## Sandbox at night on the PC (scripts/sandbox_night.gd): at night the headlights are on off the track and off on a lit (LED) track,
## off by day, and the L key's hand setting overrides; the LED dashes glow. CR_MODE=sb CR_MAP=backyard. Prints SBNIGHT PASS / FAIL.

var main: Node


func _ready() -> void:
	main = load("res://scenes/main.tscn").instantiate()
	main.auto_drive = true
	add_child(main)
	for i in 400:
		await get_tree().process_frame
		if main.state == "race" and main.race != null and main.race.sb != null and main.sb_view != null and main.sb_view.night != null:
			break
	main.race.sb.park = true
	var N = main.sb_view.night
	var k = main.kart
	var T = main.T
	var r := {}
	main.race.sb.save["t"] = 0.95
	for i in 90:
		await get_tree().process_frame
	r["on_track"] = N.spot.light_energy
	_shot("night_on")
	var j := clampi(k.idx, 0, T.N - 1)
	k.x = T.px[j] + T.nx[j] * 140.0
	k.y = T.py[j] + T.ny[j] * 140.0
	for i in 120:
		await get_tree().process_frame
	r["off_track"] = N.spot.light_energy
	_shot("night_off")
	r["led"] = (N.led[0][0] as StandardMaterial3D).emission_energy_multiplier if not N.led.is_empty() else -1.0
	main.hl_mode = false
	for i in 10:
		await get_tree().process_frame
	r["by_hand_off"] = N.spot.light_energy
	main.hl_mode = null
	main.race.sb.save["t"] = 0.5
	for i in 30:
		await get_tree().process_frame
	r["noon"] = N.spot.light_energy
	var ok: bool = r["on_track"] < 0.5 and r["off_track"] > 1.2 and r["led"] > 1.0 and r["by_hand_off"] == 0.0 and r["noon"] == 0.0
	print("SBNIGHT %s %s" % ["PASS" if ok else "FAIL", str(r)])
	get_tree().quit(0 if ok else 1)


## with a window: a picture of what it looks like (build/menu/<name>.png)
func _shot(nm: String) -> void:
	if DisplayServer.get_name() != "headless":
		get_viewport().get_texture().get_image().save_png(ProjectSettings.globalize_path("res://build/menu/%s.png" % nm))
