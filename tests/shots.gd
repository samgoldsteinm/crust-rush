extends Node
## Renders the same moments as the web game's reference shots (tools/webref.py) so the two can be
## compared side by side: the countdown, the HUD with items, drift sparks, boost flames, each item in use,
## a trick, a spin-out, the glide canyon, plus views round the track. Run with --fixed-fps 60 so every
## frame is 1/60 s of game time however slowly the software renderer draws. Saves PNGs to build/shots
## and prints a JPEG of each to the log in short pieces (SHOT_PART lines).

var main: Node
var dir := ""
var steps: Array = []
var si := 0
var wait := 0
var each := Callable()
var T: TrackData


func _ready() -> void:
	main = load("res://scenes/main.tscn").instantiate()
	main.auto_drive = true
	add_child(main)
	T = main.T
	dir = ProjectSettings.globalize_path("res://build/shots")
	DirAccess.make_dir_recursive_absolute(dir)
	steps = [
		[25, _nop, "g_countdown"],
		[0, _s_go, ""],
		[12, _s_items, "g_hud_items"],
		[12, _s_roll, "g_hud_roll"],
		[0, _s_sim1, ""],
		[20, _s_drift3, "g_drift3"],
		[20, _s_drift1, "g_drift1"],
		[10, _s_boost, "g_boost"],
		[8, _s_boost3, "g_boost_t3"],
		[0, _s_sim15, ""],
		[15, _s_pep, "g_pep"],
		[15, _s_trio, "g_trio"],
		[18, _s_dough, "g_dough"],
		[30, _s_garlic, "g_garlic"],
		[24, _s_flour, "g_flour_fly"],
		[24, _nop, "g_flour_boom"],
		[18, _s_chili, "g_chili"],
		[0, _s_sim15, ""],
		[48, _s_oil, "g_oil_back"],
		[36, _s_rush, "g_rush"],
		[0, _s_sim3, ""],
		[30, _s_held, "g_held"],
		[15, _s_trick, "g_trick"],
		[0, _s_sim15, ""],
		[9, _s_spin, "g_spin"],
		[0, _s_sim2, ""],
		[60, _s_wheel, "g_wheel"],
		[20, _s_canyon, "g_canyon_floor"],
		[20, _s_p150, "g_early"],
		[20, _s_p520, "g_mid"],
		[20, _s_p1000, "g_late"],
		[20, _s_p1140, "g_loop"],
	]
	wait = 1


func _k() -> Kart:
	return main.kart


func _nop() -> void:
	pass


func _s_go() -> void:
	_go(4.0)


func _s_items() -> void:
	_k().item = "pepperoni"
	_k().item2 = "garlic"


func _s_roll() -> void:
	var k := _k()
	k.item = ""
	k.item2 = ""
	k.pend = ["chili"]
	k.roll = 1.1


func _s_sim1() -> void:
	_sim(1.0)


func _s_sim15() -> void:
	_sim(1.5)


func _s_sim2() -> void:
	_sim(2.0)


func _s_sim3() -> void:
	_sim(3.0)


func _s_drift3() -> void:
	each = _drift.bind(3)


func _s_drift1() -> void:
	each = _drift.bind(1)


func _s_boost() -> void:
	var k := _k()
	each = Callable()
	k.drift = 0
	k.charge = 0.0
	k.boost = 2.5
	k.b_pk = 2.5
	k.f_tier = 0


func _s_boost3() -> void:
	var k := _k()
	k.boost = 1.3
	k.b_pk = 1.3
	k.f_tier = 3


func _s_pep() -> void:
	_use(_k(), "pepperoni", false)


func _s_trio() -> void:
	_use(_k(), "trio", false)


func _s_dough() -> void:
	_use(_k(), "dough", false)


func _s_garlic() -> void:
	_use(_k(), "garlic", false)


func _s_flour() -> void:
	_use(_k(), "flour", false)


func _s_chili() -> void:
	_k().sh_l = 0
	_use(_k(), "chili", false)


func _s_oil() -> void:
	main.test_look = true
	_use(_k(), "oil", true)


func _s_rush() -> void:
	main.test_look = false
	_use(_k(), "rush", false)


func _s_held() -> void:
	_k().item = "pepperoni"
	main.race.hold_item(_k(), 1)


func _s_trick() -> void:
	var k := _k()
	main.race.drop_held(k)
	k.air = true
	k.big = true
	k.air_t = 0.3
	k.wvy = 70.0
	k.wy += 8.0
	k.trick = true
	k.trick_t = Kart.TRICK_T
	k.trick_k = 1


func _s_spin() -> void:
	var k := _k()
	k.inv = 0.0
	k.sh_l = 0
	main.race.spin_out(k, "pep")


func _s_wheel() -> void:
	_use(_k(), "wheel", false)


func _s_canyon() -> void:
	_place(_k(), int((int(T.glide["j0"]) + int(T.glide["j1"])) / 2), true)


func _s_p150() -> void:
	_place(_k(), 150, false)


func _s_p520() -> void:
	_place(_k(), 520, false)


func _s_p1000() -> void:
	_place(_k(), 1000, false)


func _s_p1140() -> void:
	_place(_k(), 1140, false)


func _go(sec: float) -> void:
	main.state = "race"
	main.race.state = "race"
	main.cd = 0.0
	_sim(sec)


## run the race for a while without drawing
func _sim(sec: float) -> void:
	for i in int(sec * 120.0):
		main._sim_tick(1.0 / 120.0)
	main.cam_snap = true


func _drift(tier: int) -> void:
	var k := _k()
	k.drift = 1
	k.tier = tier
	k.charge = [0.0, 1.0, 2.0, 3.0][tier]
	k.d_amt = 1.0
	k.d_time = 0.0
	k.s_t = 0.0
	k.steer = 1.0 if tier == 3 else -1.0


func _use(k: Kart, it: String, back: bool) -> void:
	k.item = it
	main.race.use_item(k, back)


func _place(k: Kart, j: int, floor_: bool) -> void:
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


func _physics_process(_dt: float) -> void:
	if each.is_valid():
		each.call()


func _process(_dt: float) -> void:
	if wait > 0:
		wait -= 1
		return
	if si > 0:
		var nm: String = steps[si - 1][2]
		if nm != "":
			_capture(nm)
	if si >= steps.size():
		print("SHOTS done")
		get_tree().quit(0)
		return
	var st: Array = steps[si]
	si += 1
	(st[1] as Callable).call()
	wait = int(st[0])


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
