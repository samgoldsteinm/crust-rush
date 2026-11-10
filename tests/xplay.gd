extends Node
## Cross-play test, the PC side, through the test broker (CR_BROKERS). CR_XROLE=join (default): joins the room a
## browser (tools/xplay_test.py) made, races with the computer steering, and checks the race really runs both ways:
## snapshots arrive, the host plays our controls (its acknowledgements climb), and our kart gets round.
## CR_XROLE=host: makes a room, writes its code for the browser, starts on Hawaiian Bay once the browser is ready, and
## checks the browser's kart gets round with its controls played here. Prints XPLAY PC PASS / FAIL.

var main: Node
var t := 0.0
var joined := false
var done := false
var room_file := ""
var role := "join"
var started := false


func _ready() -> void:
	room_file = OS.get_environment("CR_ROOM_FILE")
	role = OS.get_environment("CR_XROLE") if OS.get_environment("CR_XROLE") != "" else "join"
	Engine.max_fps = 15     # idle while the browser starts up (it needs the CPU); full speed once racing
	main = load("res://scenes/main.tscn").instantiate()
	main.auto_drive = true
	add_child(main)
	print("XPLAY pc: waiting for the room code in %s" % room_file)


func _process(dt: float) -> void:
	t += dt
	if done:
		return
	var web: WebNet = main.web
	if role == "host":
		_host(web, dt)
		return
	if not joined:
		if room_file != "" and FileAccess.file_exists(room_file):
			var c := FileAccess.get_file_as_string(room_file).strip_edges()
			if c.length() == 4:
				joined = true
				Engine.max_fps = 120
				web.join(c, "PC tester")
				print("XPLAY pc: joining room %s" % c)
	elif int(t * 2) % 10 == 0 and int((t - dt) * 2) % 10 != 0:
		print("XPLAY pc t=%.0f role %s link %s state %s go %s snaps-ack %d seq %d host %s race_time %.1f prog %d fixes %d ping %.0f" % [t, web.role, "up" if not web.chan.is_empty() else "-", main.state, web.go, web.ack_rx, web.seq, web.host_gs, main.race.race_time if main.race else 0.0, main.kart.prog if main.kart else -1, web.fixes, web.ping_ms])
	if joined and web.racing() and main.race != null and main.race.race_time > 30.0:
		done = true
		var k: Kart = main.kart
		var ok: bool = k.prog > 150 and web.ack_rx > 1500 and web.seq > 1500
		print("XPLAY PC %s my kart prog %d, controls sent %d, acknowledged %d, last snapshot %d, place %d, race time %.1f" % ["PASS" if ok else "FAIL", k.prog, web.seq, web.ack_rx, web.last_sn, k.place, main.race.race_time])
		web.leave()
		await get_tree().create_timer(1.0).timeout
		get_tree().quit(0 if ok else 1)
	if t > 2700.0:
		done = true
		print("XPLAY PC FAIL timed out: role '%s', state %s, joined %s" % [web.role, main.state, joined])
		get_tree().quit(1)


func _host(web: WebNet, dt: float) -> void:
	if not joined and t > 3.0:
		joined = true
		web.host("PC host")
		var f := FileAccess.open(room_file, FileAccess.WRITE)
		f.store_string(web.code)
		f.close()
		print("XPLAY pc: hosting room %s" % web.code)
		return
	if not joined:
		return
	if not started:
		for p in web.pl:
			if int(p["id"]) > 0 and bool(p.get("ready", false)):
				started = true
				Engine.max_fps = 120
				var e := web.host_start()
				print("XPLAY pc: starting the race on %s %s" % [main.map_id, e])
		return
	var their: Kart = null
	for k in main.race.karts:
		if (k as Kart).web:
			their = k
	if int(t * 2) % 10 == 0 and int((t - dt) * 2) % 10 != 0:
		print("XPLAY pc t=%.0f state %s go %s race_time %.1f their prog %d acks %s queue %s my prog %d" % [t, main.state, web.go, main.race.race_time, their.prog if their else -1,
			str(web.acks), str(web.in_q.get(1, []).size()), main.kart.prog])
	if main.race.race_time > 34.0 and not done:
		done = true
		var ack := int(web.acks.get(1, 0))
		var ok: bool = their != null and their.prog > 150 and ack > 1500
		print("XPLAY PC %s their kart prog %d, controls played %d, race time %.1f" % ["PASS" if ok else "FAIL", their.prog if their else -1, ack, main.race.race_time])
		await get_tree().create_timer(4.0).timeout
		web.leave()
		await get_tree().create_timer(1.0).timeout
		get_tree().quit(0 if ok else 1)
