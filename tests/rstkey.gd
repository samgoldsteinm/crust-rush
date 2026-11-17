extends Node
## The restart key (web patch 69; Backspace by default, Settings > Controls): one press pauses and asks "Restart the race?",
## Esc resumes, a second press restarts. CR_MODE=single CR_MAP=margherita. Prints RSTKEY PASS / FAIL.

var main: Node


func _key(c: int) -> void:
	for down in [true, false]:
		var e := InputEventKey.new()
		e.keycode = c
		e.physical_keycode = c
		e.pressed = down
		Input.parse_input_event(e)
		for i in 4:
			await get_tree().process_frame


func _ready() -> void:
	main = load("res://scenes/main.tscn").instantiate()
	main.auto_drive = true
	add_child(main)
	for i in 600:
		await get_tree().process_frame
		if main.state == "race" and main.race != null:
			break
	for i in 60:
		await get_tree().process_frame
	await _key(KEY_BACKSPACE)
	var asked: bool = main.paused and main.rst_ui != null
	await _key(KEY_ESCAPE)
	var resumed: bool = not main.paused and main.rst_ui == null and main.state == "race"
	var old_race = main.race
	await _key(KEY_BACKSPACE)
	await _key(KEY_BACKSPACE)
	for i in 30:
		await get_tree().process_frame
	var restarted: bool = main.race != old_race and main.rst_ui == null and not main.paused and (main.state == "countdown" or main.state == "race")
	var ok := asked and resumed and restarted
	print("RSTKEY %s: asked %s, resumed %s, restarted %s (state %s)" % ["PASS" if ok else "FAIL", asked, resumed, restarted, main.state])
	get_tree().quit(0 if ok else 1)
