extends Node
## Sandbox on a controller: D-pad up at the start line takes the race on offer (web: D-pad up). CR_MODE=sb CR_MAP=margherita.
## Prints SBPAD PASS / FAIL.

var main: Node


func _ready() -> void:
	main = load("res://scenes/main.tscn").instantiate()
	main.auto_drive = true
	add_child(main)
	for i in 400:
		await get_tree().process_frame
		if main.state == "race" and main.race != null and main.race.sb != null:
			break
	for i in 60:
		await get_tree().process_frame
	var fl = main.race.sb.flag
	main.kart.x = float(fl[0])
	main.kart.y = float(fl[2])
	main.kart.wy = float(fl[1])
	for i in 20:
		await get_tree().process_frame
	print("SBPAD near the line: %s, offer '%s'" % [main.race.sb.race_near, main.hud.sb_race])
	var e := InputEventJoypadButton.new()
	e.device = 0
	e.button_index = JOY_BUTTON_DPAD_UP
	e.pressed = true
	Input.parse_input_event(e)
	for i in 3:
		await get_tree().process_frame
	var e2 := InputEventJoypadButton.new()
	e2.device = 0
	e2.button_index = JOY_BUTTON_DPAD_UP
	e2.pressed = false
	Input.parse_input_event(e2)
	for i in 120:
		await get_tree().process_frame
	var ok: bool = main.race != null and main.race.sb == null and main.sb_back != ""
	print("SBPAD %s: state %s, in Sandbox %s, sb_back '%s'" % ["PASS" if ok else "FAIL", main.state, main.race != null and main.race.sb != null, main.sb_back])
	get_tree().quit(0 if ok else 1)
