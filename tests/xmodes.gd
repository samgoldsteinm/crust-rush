extends Node
## Cross-play of the modes added on line in web v208 (patch 45, 46), the PC side: the browser (tools/xmodes_web.py) hosts a room in
## Balloon Battle or Sandbox (CR_XMODE=bb | sb), this PC joins and readies up.
##   bb: the PC's race is a battle on the arena, its clock follows the host's, a hit from the host takes one of its balloons (a bb_pop
##       for its kart), and when the host ends the round the PC goes to its results.
##   sb: the PC starts its own Sandbox at the host's place (no race config), sees the host's car there (a drawn node) and the host
##       sees it (checked on the browser's side).
## CR_BROKERS=ws://127.0.0.1:8765/mqtt CR_ROOM_FILE=room.txt CR_XMODE=bb <godot> --headless --path . res://tests/xmodes.tscn
## Prints "XMODES PC PASS" / "XMODES PC FAIL".

var main: Node
var t := 0.0
var joined := false
var done := false
var mode := "bb"
var room_file := ""
var pops := 0
var bal_min := 99
var clock_ok := false
var saw_peer := false
var sbr_step := 0
var sbr_ok := false
var sbr_a := false
var sbr_t := 0.0


func _ready() -> void:
	room_file = OS.get_environment("CR_ROOM_FILE")
	mode = OS.get_environment("CR_XMODE") if OS.get_environment("CR_XMODE") != "" else "bb"
	Engine.max_fps = 30
	main = load("res://scenes/main.tscn").instantiate()
	main.auto_drive = true
	add_child(main)
	print("XMODES pc: %s, waiting for the room code in %s" % [mode, room_file])


func _process(dt: float) -> void:
	t += dt
	if done:
		return
	var web: WebNet = main.web
	if not joined:
		if room_file != "" and FileAccess.file_exists(room_file):
			var c := FileAccess.get_file_as_string(room_file).strip_edges()
			if c.length() == 4:
				joined = true
				Engine.max_fps = 60
				web.join(c, "PC tester")
				print("XMODES pc: joining room %s" % c)
		return
	if not web.chan.is_empty() and not web.ready_ and web.cfg.is_empty() and not web.sbx:
		web.set_ready(true)
	var race = main.race
	if int(t * 2) % 10 == 0 and int((t - dt) * 2) % 10 != 0:
		print("XMODES pc t=%.0f state %s map %s bb %s sb %s sbx %s peers %d nodes %d" % [t, main.state, main.map_id, race != null and race.bb != null, race != null and race.sb != null, web.sbx, web.sb_peers.size(), main.sb_peer_nodes.size()])
	if mode == "bb" and race != null and race.bb != null and main.kart != null:
		for e in race.fx:
			if String(e.get("t", "")) == "bb_pop" and e.get("k") == main.kart:
				pops += 1
		bal_min = mini(bal_min, main.kart.bal)
		if race.bb.t > 0.0 and race.bb.t < 299.0:
			clock_ok = true
		if main.state == "results" or main.state == "finished":
			done = true
			var ok: bool = clock_ok and bal_min <= 4 and race.bb.over
			print("XMODES PC %s battle: clock followed %s, lowest balloons %d (pops seen %d), round over %s, state %s" % ["PASS" if ok else "FAIL", clock_ok, bal_min, pops, race.bb.over, main.state])
			await _linger(web)
			get_tree().quit(0 if ok else 1)
			return
	if mode == "sb" and race != null and race.sb != null:
		for id in main.sb_peer_nodes:
			var n: Dictionary = main.sb_peer_nodes[id]
			if is_instance_valid(n["g"]) and (n["g"] as Node3D).visible:
				saw_peer = true
		if saw_peer and t > 20.0:
			done = true
			var ok: bool = web.cfg.is_empty() and web.sbx and saw_peer
			print("XMODES PC %s sandbox: in Sandbox at %s, no race config %s, the host's car drawn %s, peers %s" % ["PASS" if ok else "FAIL", main.map_id, web.cfg.is_empty(), saw_peer, str(web.sb_peers.keys())])
			await _linger(web)
			get_tree().quit(0 if ok else 1)
			return
	if mode == "sbr" and race != null:
		# (web patch 52) 1. the PC asks at its start line, the web host joins, both race; the PC goes back FIRST, the host still racing:
		# the PC must still be in the room (and in Sandbox) 30 s later. 2. the host asks, the PC says no, the host races 30 s: the PC must
		# still be in the room (the owner: guests were thrown out of the room in both cases)
		if sbr_step == 0 and race.sb != null and main.state == "race" and t > 25.0 and web.sb_peers.size() > 0 and main.sb_peer_nodes.size() > 0:
			main.sbi_ask = {"mi": int(main._map_info(main.map_id).get("mi", -1))}
			main._sbi_pick("f")
			sbr_step = 1
			print("XMODES pc: asked to race on %s" % main.map_id)
		elif sbr_step == 1 and race.sb == null and main.state == "race" and not web.cfg.is_empty():
			sbr_step = 2
			sbr_ok = web.cfg.get("sbr") != null
			sbr_t = t
			print("XMODES pc: racing, a Sandbox race %s, karts %d" % [sbr_ok, race.karts.size()])
		elif sbr_step == 2 and t - sbr_t > 6.0:
			main._to_menu("")
			sbr_step = 3
			print("XMODES pc: went back first")
		elif sbr_step == 3 and race.sb != null and web.cfg.is_empty():
			sbr_step = 4
			sbr_t = t
		elif sbr_step == 4 and t - sbr_t > 30.0:
			sbr_a = web.role == "guest" and race.sb != null
			print("XMODES pc: 30 s after going back first: role '%s', in Sandbox %s" % [web.role, race.sb != null])
			sbr_step = 5
		elif sbr_step == 5 and not main.sbi_inv.is_empty():
			main._sbi_answer(false)
			sbr_step = 6
			sbr_t = t
			print("XMODES pc: said no to the host's invite")
		elif sbr_step == 6 and t - sbr_t > 35.0:
			done = true
			var b: bool = web.role == "guest" and race.sb != null
			var ok2: bool = sbr_ok and sbr_a and b
			print("XMODES PC %s sandbox race: raced %s; went back first and stayed %s; said no and stayed %s (role '%s')" % ["PASS" if ok2 else "FAIL", sbr_ok, sbr_a, b, web.role])
			await _linger(web)
			get_tree().quit(0 if ok2 else 1)
			return
	if t > 1500.0:
		done = true
		print("XMODES PC FAIL timed out: state %s, map %s" % [main.state, main.map_id])
		get_tree().quit(1)


func _linger(web: WebNet) -> void:
	var t0 := t
	while t - t0 < 120.0 and web.role != "":
		await get_tree().create_timer(0.5).timeout
	web.leave()
	await get_tree().create_timer(1.0).timeout
