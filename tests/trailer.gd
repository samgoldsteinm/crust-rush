extends Node
## Records a short gameplay clip for the download page. Run with Godot's Movie Maker:
##   xvfb-run godot --path . --resolution 1280x720 --fixed-fps 30 --write-movie build/clip.avi res://tests/trailer.tscn
## The computer drives the player's kart on Ultra with the PC extras on. Settings come from the environment:
##   CR_MAP     track id (default Hawaiian Bay)
##   TR_SKIP    seconds of race to run (without drawing) before recording; 0 keeps the countdown
##   TR_SECS    seconds to record after that
## Prints "TRAILER MARK" when the part worth keeping starts and "TRAILER DONE" before quitting;
## the workflow keeps the last TR_SECS seconds of the movie.

var main: Node


func _ready() -> void:
	main = load("res://scenes/main.tscn").instantiate()
	main.auto_drive = true
	add_child(main)
	main.quality = 2          # Ultra
	main.pc_plus = true       # with the PC extras
	main._apply_quality()
	_run()


func _frames(n: int) -> void:
	for i in n:
		await get_tree().process_frame


func _run() -> void:
	var skip := float(OS.get_environment("TR_SKIP")) if OS.get_environment("TR_SKIP") != "" else 0.0
	var secs := float(OS.get_environment("TR_SECS")) if OS.get_environment("TR_SECS") != "" else 8.0
	var fps := Engine.get_frames_per_second()
	await _frames(20)         # the track, karts and shaders settle in
	if skip > 0.0:
		main.state = "race"
		main.race.state = "race"
		main.cd = 0.0
		for i in int(round(skip * 120.0)):
			main._sim_tick(1.0 / 120.0)
		main.cam_snap = true
		await _frames(3)
	print("TRAILER MARK map=%s skip=%.1f frames=%d" % [main.map_id, skip, Engine.get_frames_drawn()])
	var n := int(ceil(secs * 30.0)) + 2
	for i in n:
		await get_tree().process_frame
		if i % 30 == 0:
			print("TRAILER t=%.1f state %s pos %d speed %.0f fps %s" % [i / 30.0, main.state, main.race.position_of(main.kart), main.kart.speed, str(fps)])
	print("TRAILER DONE")
	get_tree().quit()
