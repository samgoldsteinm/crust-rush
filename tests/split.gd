extends Node
## Split screen (pc120): starts a race with two players (CR_SPLIT=1), both driven by the computer, saves window pictures at
## SPLIT_AT seconds (default "6,20,45") to build/shots/split_<tag>_<n>.png, then runs on to the end of the race (SPLIT_FULL=1)
## or stops. Prints "SPLIT PASS" when the second player's kart, camera and HUD were live and the race went on.

var main: Node
var t := 0.0
var shots: Array = []
var n := 0
var fails: Array = []


func _ready() -> void:
	main = load("res://scenes/main.tscn").instantiate()
	main.auto_drive = true
	add_child(main)
	for v in OS.get_environment("SPLIT_AT").split(",", false) if OS.get_environment("SPLIT_AT") != "" else PackedStringArray(["6", "20", "45"]):
		shots.append(float(v))
	await get_tree().process_frame
	await get_tree().process_frame
	if String(OS.get_environment("CR_MODE")) != "":
		main.sel["mode"] = OS.get_environment("CR_MODE")
	main._start_race({})
	print("SPLIT start: split_live ", main.split_live, " kart2 ", main.kart2 != null, " karts ", main.race.karts.size(), " mode '", main.race.mode, "'")
	if not main.split_live or main.kart2 == null:
		fails.append("split did not start")


func _process(dt: float) -> void:
	t += dt
	if main == null or main.race == null:
		return
	if n < shots.size() and t >= float(shots[n]):
		var dir := ProjectSettings.globalize_path("res://build/shots")
		DirAccess.make_dir_recursive_absolute(dir)
		get_viewport().get_texture().get_image().save_png("%s/split_%s_%d.png" % [dir, OS.get_environment("SPLIT_TAG"), n])
		var k2: Kart = main.kart2
		print("SPLIT shot %d t=%.1f state %s | P1 %s prog %d speed %d | P2 %s prog %d speed %d | cam1 %s cam2 %s" % [n, t, main.state, main.kart.racer_name, main.kart.prog, main.kart.speed,
			k2.racer_name if k2 else "-", k2.prog if k2 else 0, k2.speed if k2 else 0, main.cam.global_position, main.cam2.global_position if main.cam2 else Vector3.ZERO])
		print("SPLIT p2 pass sounds so far ", main.sfx.played2, " | hud2 toast '", main.hud2.banner_text, "'")
		if main.sfx2 != null:
			print("SPLIT engines: p1 playing ", main.sfx.eng.playing, " pitch %.2f" % main.sfx.eng.pitch_scale, " | p2 playing ", main.sfx2.eng.playing, " pitch %.2f" % main.sfx2.eng.pitch_scale)
		n += 1
		if n >= shots.size() and OS.get_environment("SPLIT_FULL") != "1":
			_end()
	if OS.get_environment("SPLIT_FULL") == "1" and (main.state == "results" or t > 420.0):
		print("SPLIT race over: state ", main.state, " t ", t)
		_end()


func _end() -> void:
	if main.kart2 != null and main.kart2.prog <= 0:
		fails.append("player 2 did not move")
	if main.cam2 != null and main.cam2.global_position.distance_to(main.cam.global_position) < 0.01:
		fails.append("the two cameras are in the same place")
	print("SPLIT PASS" if fails.is_empty() else "SPLIT FAIL " + str(fails))
	get_tree().quit()
