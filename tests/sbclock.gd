extends Node
## Sandbox's day and night on the PC (scripts/sandbox_clock.gd): pictures of the place at noon, sunset, dusk and night, to
## build/sbclock/<map>_<hour>.png. Windowed (it draws):  CR_MAP=<id> CR_MODE=sb <godot> --path . res://tests/sbclock.tscn
## Prints "SBCLOCK done" and whether the clock armed.

var main: Node
var steps: Array = []
var si := 0
var wait := 0


func _ready() -> void:
	main = load("res://scenes/main.tscn").instantiate()
	main.auto_drive = true
	main.test_hold = true
	add_child(main)
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path("res://build/sbclock"))
	var id := OS.get_environment("CR_MAP")
	for h in [[0.5, "1noon"], [0.735, "2sunset"], [0.8, "3dusk"], [0.95, "4night"]]:
		steps.append([40, func(): main.race.sb.save["t"] = h[0], "%s_%s" % [id, h[1]]])
	wait = 240


func _process(_dt: float) -> void:
	if main.race != null and main.race.sb != null:
		main.race.sb.park = true
	if wait > 0:
		wait -= 1
		return
	if si > 0:
		var img := get_viewport().get_texture().get_image()
		img.save_png(ProjectSettings.globalize_path("res://build/sbclock/%s.png" % steps[si - 1][2]))
		var v = main.sb_view
		print("SBCLOCK shot %s armed %s kind %s mats %d" % [steps[si - 1][2], v != null and v.clock != null and v.clock.armed, v.clock.kind if v != null and v.clock != null else "-", v.clock.mats.size() if v != null and v.clock != null else 0])
	if si >= steps.size():
		print("SBCLOCK done")
		get_tree().quit(0)
		return
	(steps[si][1] as Callable).call()
	wait = int(steps[si][0])
	si += 1
