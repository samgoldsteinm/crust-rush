extends Node
## Sandbox's Back to the track key (web v212 patch 51; T by default, Settings > Controls): driving in Sandbox, T pauses and asks
## "Back to the track?". CR_MODE=sb CR_MAP=margherita. Prints SBKEY PASS / FAIL.

var main: Node


func _ready() -> void:
	main = load("res://scenes/main.tscn").instantiate()
	main.auto_drive = true
	add_child(main)
	for i in 400:
		await get_tree().process_frame
		if main.state == "race" and main.race != null and main.race.sb != null:
			break
	for i in 30:
		await get_tree().process_frame
	var e := InputEventKey.new()
	e.keycode = KEY_T
	e.physical_keycode = KEY_T
	e.pressed = true
	Input.parse_input_event(e)
	for i in 10:
		await get_tree().process_frame
	var ok: bool = main.paused and main.sb_back_ui != null and Keys.ACTS.any(func(a): return a[0] == "sbback")
	print("SBKEY %s: state %s, paused %s, asked %s" % ["PASS" if ok else "FAIL", main.state, main.paused, main.sb_back_ui != null])
	get_tree().quit(0 if ok else 1)
