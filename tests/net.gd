extends Node
## Online test: run one copy with "-- host" and another with "-- join" on the same machine.
## The host starts a race once the other copy has joined; both let the computer steer and check
## that the joined kart really drives round the host's race. Prints NET HOST PASS / NET CLIENT PASS.

var main: Node
var role := "host"
var t := 0.0
var started := false
var begun_at := -1.0
var steer_seen := 0.0
var done := false
var theirs: Kart


func _ready() -> void:
	role = "join" if OS.get_cmdline_user_args().has("join") else "host"
	Engine.max_fps = 120
	main = load("res://scenes/main.tscn").instantiate()
	main.auto_drive = true
	add_child(main)
	if role == "host":
		main._menu_host()
		print("NET host: listening, role '%s'" % main.net_role)
	else:
		main.ip_edit.text = "127.0.0.1"
		main._menu_join()
		print("NET join: connecting, role '%s'" % main.net_role)


func _their_kart() -> Kart:
	for k in main.race.karts:
		if k.peer != 0 and k.peer != 1:
			return k
	return null


func _process(dt: float) -> void:
	t += dt
	if done:
		return
	if role == "host":
		if not started and main.net_peers.size() >= 1 and t > 1.0:
			started = true
			begun_at = t
			main._net_start()
			print("NET host: %d joined, race started" % main.net_peers.size())
		if started:
			if theirs == null:
				theirs = _their_kart()
			var k := theirs
			if k != null:
				steer_seen = maxf(steer_seen, absf(float(k.net_inp["steer"])))
			if main.race.race_time > 22.0:
				done = true
				var ok: bool = k != null and k.prog > 150 and steer_seen > 0.05
				print("NET HOST %s their kart: prog %d, speed %.0f, steering received %.2f, item '%s'; my kart prog %d; race time %.1f" % ["PASS" if ok else "FAIL", k.prog if k else -1, k.speed if k else 0.0, steer_seen, k.item if k else "", main.kart.prog, main.race.race_time])
				await get_tree().create_timer(2.0).timeout
				get_tree().quit(0 if ok else 1)
	else:
		if main.net_role == "client" and main.race.race_time > 18.0 and main.net_snaps > 100:
			done = true
			var me: Kart = main.kart
			var mine: bool = me.peer == multiplayer.get_unique_id()
			var ok2: bool = mine and me.prog > 120 and main.net_snaps > 300
			print("NET CLIENT %s my kart: prog %d, speed %.0f, place %d of %d, snapshots %d, state %s, thrown items seen %d" % ["PASS" if ok2 else "FAIL", me.prog, me.speed, main.race.position_of(me), main.race.karts.size(), main.net_snaps, main.state, main.race.projectiles.size()])
			get_tree().quit(0 if ok2 else 1)
	if t > 150.0:
		done = true
		print("NET %s FAIL timed out: role '%s', peers %d, snapshots %d, state %s" % [role.to_upper(), main.net_role, main.net_peers.size(), main.net_snaps, main.state])
		get_tree().quit(1)
