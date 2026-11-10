extends Node
## Every track in the maps folder, one after another: loads it, lets the computer drive all eight karts
## for RUN_T seconds of race time and checks that every kart gets round (none stuck, none fallen through
## the world). Prints one "MAP <id> ok|BAD ..." line per track and "MAPS PASS" or "MAPS FAIL" at the end.

const RUN_T := 60.0
var main: Node
var ids: Array = []
var at := -1
var results: Array = []


func _ready() -> void:
	main = load("res://scenes/main.tscn").instantiate()
	main.auto_drive = true
	add_child(main)
	for m in main.maps:
		ids.append(m["id"])
	print("MAPS found %d: %s" % [ids.size(), ", ".join(PackedStringArray(ids))])


func _process(_dt: float) -> void:
	at += 1
	if at >= ids.size():
		var bad := 0
		for r in results:
			if not r:
				bad += 1
		print("MAPS %s: %d of %d tracks drove cleanly" % ["PASS" if bad == 0 and not ids.is_empty() else "FAIL", ids.size() - bad, ids.size()])
		get_tree().quit(0 if bad == 0 else 1)
		return
	var id: String = ids[at]
	var t0 := Time.get_ticks_msec()
	if id != main.map_id and not main.load_map(id):
		print("MAP %s BAD could not load" % id)
		results.append(false)
		return
	var load_ms := Time.get_ticks_msec() - t0
	main._start_race({})
	main.state = "race"
	main.race.state = "race"
	main.cd = 0.0
	var race: Race = main.race
	var T: TrackData = main.T
	var resp := {}
	var nan := false
	var spins := 0
	for i in int(RUN_T * 120.0):
		race.update(1.0 / 120.0, main._input_state())
		for k in race.karts:
			if k.events.has("respawn"):
				resp[k] = int(resp.get(k, 0)) + 1
			if is_nan(k.x) or is_nan(k.y) or is_nan(k.wy):
				nan = true
		for e in race.fx:
			if e["t"] == "spin":
				spins += 1
		main._drain_events()
	var worst := 1e9
	var line := ""
	var most_resp := 0
	for k in race.karts:
		worst = minf(worst, float(k.prog) / T.N)
		most_resp = maxi(most_resp, int(resp.get(k, 0)))
		line += "%s %.2f  " % [k.racer_name.substr(0, 3), float(k.prog) / T.N]
	var ok := not nan and worst > 0.45 and most_resp <= 6
	results.append(ok)
	print("MAP %s %s %s (load %d ms): laps done %s| slowest %.2f, most respawns %d, spin-outs %d, traffic %d, walkers %d, rollers %d, train %s%s" % [
		id, "ok" if ok else "BAD", main._map_info(id)["name"], load_ms, line, worst, most_resp, spins,
		race.traffic.size(), race.walkers.size(), race.rollers.size(), "yes" if not race.train.is_empty() else "no", ", NaN!" if nan else ""])
