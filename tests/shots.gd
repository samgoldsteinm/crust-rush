extends Node
## Renders the same moments as the web game's reference shots (tools/webref.py), step for step, so the
## two can be compared side by side: the countdown, the HUD with items, drift sparks, boost flames, each
## item in use, a held item, a trick, a spin-out, the Pizza Wheel, the glide canyon, plus views round
## the track. "wait_t" runs the race for that long without drawing and then draws two frames, as the
## web script does. Run with --fixed-fps 60. Saves PNGs to build/shots and prints a JPEG of each to
## the log in short pieces (SHOT_PART lines).

var main: Node
var dir := ""
var T: TrackData


func _ready() -> void:
	main = load("res://scenes/main.tscn").instantiate()
	main.auto_drive = true
	add_child(main)
	T = main.T
	dir = ProjectSettings.globalize_path("res://build/shots")
	DirAccess.make_dir_recursive_absolute(dir)
	_run()


func _k() -> Kart:
	return main.kart


func _frames(n: int) -> void:
	for i in n:
		await get_tree().process_frame


## the race runs for `sec` without drawing, then two frames are drawn (web wait_t)
func _wait_t(sec: float) -> void:
	for i in int(round(sec * 120.0)):
		main._sim_tick(1.0 / 120.0)
	main.cam_snap = true      # the web's camera follows every step; here it would still be where the race was before the jump
	await _frames(2)


func _shot(name: String) -> void:
	await _frames(1)
	_capture(name)


func _drift(tier: int, steer: float) -> void:
	var k := _k()
	k.drift = 1
	k.tier = tier
	k.charge = [0.0, 1.0, 2.0, 3.0][tier]
	k.d_amt = 1.0
	k.d_time = 0.0
	k.s_t = 0.0
	k.steer = steer


func _use(it: String, back := false) -> void:
	_k().item = it
	main.race.use_item(_k(), back)


func _run() -> void:
	await _frames(25)          # the track and karts settle in
	await _frames(2)
	await _shot("g_countdown")
	main.state = "race"
	main.race.state = "race"
	main.cd = 0.0
	main._show_center("Go!", 1.0, "md")
	await _wait_t(4.0)
	_k().item = "pepperoni"
	_k().item2 = "garlic"
	await _wait_t(0.3)
	await _shot("g_hud_items")
	_k().item = ""
	_k().item2 = ""
	_k().pend = ["chili"]
	_k().roll = 1.1
	await _wait_t(0.3)
	await _shot("g_hud_roll")
	await _wait_t(1.0)
	# drift sparks: three steps with the drift held, one frame each
	for i in 3:
		_drift(3, 1.0)
		main._sim_tick(1.0 / 120.0)
		_drift(3, 1.0)
		await _frames(1)
	await _shot("g_drift3")
	for i in 3:
		_drift(1, -1.0)
		main._sim_tick(1.0 / 120.0)
		_drift(1, -1.0)
		await _frames(1)
	await _shot("g_drift1")
	_k().drift = 0
	_k().charge = 0.0
	# boost flames
	var k := _k()
	k.boost = 2.5
	k.b_pk = 2.5
	k.f_tier = 0
	await _wait_t(0.15)
	await _shot("g_boost")
	k.boost = 1.3
	k.b_pk = 1.3
	k.f_tier = 3
	await _wait_t(0.1)
	await _shot("g_boost_t3")
	await _wait_t(1.5)
	# items in use
	_use("pepperoni")
	await _wait_t(0.25)
	await _shot("g_pep")
	_use("trio")
	await _wait_t(0.25)
	await _shot("g_trio")
	_use("dough")
	await _wait_t(0.3)
	await _shot("g_dough")
	_use("garlic")
	await _wait_t(0.5)
	await _shot("g_garlic")
	_use("flour")
	await _wait_t(0.4)
	await _shot("g_flour_fly")
	await _wait_t(0.4)
	await _shot("g_flour_boom")
	_k().sh_l = 0
	_use("chili")
	await _wait_t(0.3)
	await _shot("g_chili")
	await _wait_t(1.5)
	main.test_look = true
	_use("oil", true)
	await _wait_t(0.8)
	await _shot("g_oil_back")
	main.test_look = false
	_use("rush")
	await _wait_t(0.6)
	await _shot("g_rush")
	await _wait_t(3.0)
	_k().item = "pepperoni"
	main.race.hold_item(_k(), 1)
	await _wait_t(0.5)
	await _shot("g_held")
	main.race.drop_held(_k())
	k = _k()
	k.air = true
	k.big = true
	k.air_t = 0.3
	k.wvy = 70.0
	k.wy += 8.0
	k.trick = true
	k.trick_t = Kart.TRICK_T
	k.trick_k = 1
	await _wait_t(0.25)
	await _shot("g_trick")
	await _wait_t(1.5)
	_k().inv = 0.0
	_k().sh_l = 0
	main.race.spin_out(_k(), "pep")
	await _wait_t(0.15)
	await _shot("g_spin")
	await _wait_t(2.0)
	_use("wheel")
	await _wait_t(1.0)
	await _shot("g_wheel")
	# the glide canyon, from the floor
	if not T.glide.is_empty():
		_place(int((int(T.glide["j0"]) + int(T.glide["j1"])) / 2), true)
		await _frames(3)
		await _shot("g_canyon_floor")
		# looking down into the canyon from the ramp, where the water is
		_place(int(T.glide["rj"]) - 6, true)
		await _frames(3)
		await _shot("g_canyon_ramp")
	for j in [150, 520, 1000, 1140]:
		_place(j % T.N, true)
		await _frames(3)
		await _shot("g_" + {150: "early", 520: "mid", 1000: "late", 1140: "loop"}[j])
	print("SHOTS done")
	get_tree().quit(0)


func _place(j: int, floor_: bool) -> void:
	var k := _k()
	k.x = T.px[j]
	k.y = T.py[j]
	k.a = T.ang[j]
	k.ma = k.a
	k.idx = j
	k.wy = T.ground(k.x, k.y)
	k.last_g = NAN
	k.air = false
	k.glide = false
	k.loop = {}
	k.spin = 0.0
	k.speed = 0.0 if floor_ else 150.0
	k._save_prev()
	main.cam_snap = true


func _capture(name: String) -> void:
	var img := get_viewport().get_texture().get_image()
	img.save_png(dir + "/" + name + ".png")
	var small := img.duplicate() as Image
	small.resize(960, 540, Image.INTERPOLATE_BILINEAR)
	var jpg := small.save_jpg_to_buffer(0.8)
	# GitHub drops very long log lines: send the image in short numbered pieces
	var b64 := Marshalls.raw_to_base64(jpg)
	var n := int(ceil(b64.length() / 3000.0))
	for c in n:
		print("SHOT_PART %s %d %d %s" % [name, c, n, b64.substr(c * 3000, 3000)])
	print("SHOT %s fps %d tris %d draws %d" % [name, Engine.get_frames_per_second(), int(Performance.get_monitor(Performance.RENDER_TOTAL_PRIMITIVES_IN_FRAME)), int(Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME))])
