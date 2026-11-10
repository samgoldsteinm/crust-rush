extends Node
## Renders views around the track to check the look. Saves PNGs to build/shots and prints a small
## JPEG of each to the log (SHOT_B64 lines) so they can be checked without downloading anything.

const SPOTS := [[-1, "start"], [150, "early"], [262, "glide_ramp"], [330, "glide"], [520, "mid"], [760, "shortcut"], [1000, "late"], [1140, "loop"]]
var main: Node
var i := -1
var wait := 0
var dir := ""


func _ready() -> void:
	main = load("res://scenes/main.tscn").instantiate()
	add_child(main)
	main.auto_drive = true
	dir = ProjectSettings.globalize_path("res://build/shots")
	DirAccess.make_dir_recursive_absolute(dir)
	wait = 20


func _process(_dt: float) -> void:
	if wait > 0:
		wait -= 1
		return
	if i >= 0:
		_capture(String(SPOTS[i][1]))
	i += 1
	if i >= SPOTS.size():
		print("SHOTS done")
		get_tree().quit(0)
		return
	var j: int = SPOTS[i][0]
	if j >= 0:
		var T: TrackData = main.T
		var k: Kart = main.kart
		k.x = T.px[j]
		k.y = T.py[j]
		k.a = T.ang[j]
		k.ma = k.a
		k.idx = j
		k.wy = T.ground(k.x, k.y)
		k.last_g = NAN
		k.air = false
		k.glide = false
		k.speed = 150.0
		k._save_prev()
		main.state = "race"
		main.cam_a = k.a
		main.cam_snap = true
	wait = 8


func _capture(name: String) -> void:
	var img := get_viewport().get_texture().get_image()
	img.save_png(dir + "/" + name + ".png")
	var small := img.duplicate() as Image
	small.resize(640, 360, Image.INTERPOLATE_BILINEAR)
	var jpg := small.save_jpg_to_buffer(0.72)
	print("SHOT_B64 %s %s" % [name, Marshalls.raw_to_base64(jpg)])
	print("SHOT %s fps %d tris %d draws %d" % [name, Engine.get_frames_per_second(), int(Performance.get_monitor(Performance.RENDER_TOTAL_PRIMITIVES_IN_FRAME)), int(Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME))])
