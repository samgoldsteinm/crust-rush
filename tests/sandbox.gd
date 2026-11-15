extends Node
## Headless test of Sandbox (scripts/sandbox.gd) on one place, modelled on the web's own test (tools/neon/sbworld.py there):
##   lap      the whole track forwards with only the wheel turned toward the track ahead: reached > .98, never stuck
##   back     the whole track the wrong way round: a list of where the kart was stopped (want none)
##   arches   every passage's mouth can be driven to from the track (a flood over the open ground); every hidden coin on
##            the ground too
##   mode     one kart, no finish however far it drives, Park stops it, the item rule, coins are taken
##   travel   driving into a gate: the kart drives the tunnel while the next place is built on another thread, and comes
##            out of the matching gate still moving; a gate whose place cannot be had brings it back out of the same
##            gate; fast travel to a start line; the race from the start line and the way back to Sandbox
##   map      the map opens and stops the game, has a pin at every place this copy has, looks closer at a picked place
##            and shows its tunnels, and travels to a picked pin
## Prints "SANDBOX PASS" or "SANDBOX FAIL" with the numbers.
## Run: CR_MAP=bedroom CR_MODE=sb CR_HD=0 <godot console> --headless --path . --fixed-fps 120 res://tests/sandbox.tscn
## (CR_SB_TRAVEL=0 leaves the travel part out: it loads other maps, which takes a while.)

const DT := 1.0 / 120.0
var main: Node
var race: Race
var sb
var T: TrackData
var k: Kart
var fails: Array = []
var out := {}


func _ready() -> void:
	main = load("res://scenes/main.tscn").instantiate()
	main.auto_drive = true
	main.test_hold = true     # the race only moves when this test steps it
	add_child(main)
	await get_tree().process_frame
	_bind()
	if sb == null:
		print("SANDBOX FAIL this is not Sandbox: map %s, mode '%s', the map's Sandbox block %s (run with CR_MODE=sb on a map exported with it)" % [main.map_id, race.mode, "there" if not main.T.sb.is_empty() else "MISSING"])
		get_tree().quit(1)
		return
	print("SANDBOX start: %s (%s, %s), %d lap points, %d karts, %d gates of %d exported, %d coins (%d hidden), columns %s" % [sb.id, sb.kind, "free" if sb.free else "keep to the road", T.N, race.karts.size(),
		sb.gates.size(), (T.sb.get("gates", []) as Array).size(), sb.coin_n, int(sb.found()[1]), ("%d x %d" % [sb.cnx, sb.cnz]) if sb.has_col else "none"])
	_check("one kart", race.karts.size() == 1)
	_check("mode sb", race.mode == "sb")
	_flood()
	_lap()
	_back()
	_mode()
	if OS.get_environment("CR_SB_TRAVEL") != "0":
		await _travel()
	var ok := fails.is_empty()
	print("SANDBOX %s %s: %s%s" % ["PASS" if ok else "FAIL", out.get("id", "?"), JSON.stringify(out), "" if ok else "  FAILED: " + ", ".join(fails)])
	get_tree().quit(0 if ok else 1)


func _bind() -> void:
	race = main.race
	sb = race.sb
	T = main.T
	k = main.kart
	if sb != null and not out.has("id"):
		out["id"] = sb.id
		out["kind"] = sb.kind


func _check(what: String, ok: bool) -> void:
	if not ok:
		fails.append(what)


func _gb(x: float, z: float) -> float:
	return 0.0 if sb.toy else T.ground(x, z)


## the race as it would run with nobody touching anything but the wheel: the throttle is on by itself
func _step(steer := 0.0) -> void:
	main.state = "race"
	race.state = "race"
	k.ai["auto"] = false
	race.update(DT, {"steer": steer, "brake": false, "nb": false, "mul": 1.0, "use": false, "back": false, "hold": false, "hold_sl": 1, "release": null})
	race.fx.clear()
	k.events.clear()


func _place(j: int, backwards := false) -> void:
	k.x = T.px[j]
	k.y = T.py[j]
	k.idx = j
	k.a = atan2(-T.ty[j], -T.tx[j]) if backwards else atan2(T.ty[j], T.tx[j])
	k.ma = k.a
	k.speed = 0.0
	k.wy = _gb(k.x, k.y) + T.ey[j]
	k.last_g = k.wy
	k.wvy = 0.0
	k.g_rate = 0.0
	k.air = false
	k.big = false
	k.loop = {}
	k.loop_th = 0.0
	k.glide = false
	k.sc = -1
	k.spin = 0.0
	k.drift = 0
	k.boost = 0.0
	k.on_ramp = false
	k.on_glide = false
	k.bpx = k.x
	k.bpy = k.y
	k._save_prev()


## every square of floor that can be driven to from the track where it lies on the ground (web CHECK: the flood)
func _flood() -> void:
	out["gatesCut"] = []
	out["rareCut"] = 0
	if not sb.has_col:
		return
	var C: float = sb.cC
	var nx: int = sb.cnx
	var nz: int = sb.cnz
	var x0: float = sb.cx0
	var z0: float = sb.cz0
	var seen := PackedByteArray()
	seen.resize(nx * nz)
	var st := PackedInt32Array()
	for j in range(0, T.N, 3):
		if T.ey[j] < 1.5:
			var i := int(floor((T.px[j] - x0) / C))
			var q0 := int(floor((T.py[j] - z0) / C))
			if i >= 0 and q0 >= 0 and i < nx and q0 < nz and seen[i * nz + q0] == 0:
				seen[i * nz + q0] = 1
				st.append(i * nz + q0)
	var open := 0
	while not st.is_empty():
		var q := st[st.size() - 1]
		st.remove_at(st.size() - 1)
		var i2 := q / nz
		var kk := q % nz
		open += 1
		var wy := _gb(x0 + (i2 + 0.5) * C, z0 + (kk + 0.5) * C)
		for d in [[1, 0], [-1, 0], [0, 1], [0, -1]]:
			var ii: int = i2 + int(d[0])
			var k2: int = kk + int(d[1])
			if ii < 0 or k2 < 0 or ii >= nx or k2 >= nz:
				continue
			var n := ii * nz + k2
			if seen[n] != 0:
				continue
			if sb.blocked(x0 + (ii + 0.5) * C, z0 + (k2 + 0.5) * C, wy):
				continue
			seen[n] = 1
			st.append(n)
	var at := func(x: float, z: float) -> bool:
		for d in [[0, 0], [7, 0], [-7, 0], [0, 7], [0, -7]]:
			var i3 := int(floor((x + float(d[0]) - x0) / C))
			var k3 := int(floor((z + float(d[1]) - z0) / C))
			if i3 >= 0 and k3 >= 0 and i3 < nx and k3 < nz and seen[i3 * nz + k3] != 0:
				return true
		return false
	var cut: Array = []
	for g in sb.gates:
		if bool(g["road"]):
			continue
		var back := 60.0 if bool(g["plain"]) else 30.0
		if not at.call(float(g["x"]) - float(g["nx"]) * back, float(g["z"]) - float(g["nz"]) * back):
			cut.append(String(g["id"]))
	var rc := 0
	for i4 in sb.coin_n:
		if sb.coin_rare[i4] != 0 and sb.coin_y[i4] - _gb(sb.coin_x[i4], sb.coin_z[i4]) < 14.0 and not at.call(sb.coin_x[i4], sb.coin_z[i4]):
			rc += 1
	out["gatesCut"] = cut
	out["rareCut"] = rc
	out["openMm2"] = int(round(open * C * C / 1e4))
	_check("an arch cannot be reached: %s" % str(cut), cut.is_empty())
	_check("%d hidden coins on the ground cannot be reached" % rc, rc == 0)


## along the track from lap fraction .02: the wheel is turned toward the track ahead, nothing else (web __sb.lap)
func _lap() -> void:
	var N := T.N
	var j0 := int(round(0.02 * N)) % N
	_place(j0)
	var c0 := int(sb.save.get("c", 0))
	var off := 0
	var worst := 0.0
	var far := 0.0
	var stuck := 0
	var lx := k.x
	var ly := k.y
	var loops := 0
	var was_loop := false
	var steps := 0
	for i in 120000:
		var q := (k.idx + 9) % N
		var want := atan2(T.py[q] - k.y, T.px[q] - k.x)
		if k.loop.is_empty():
			k.a += Kart.ang_diff(want, k.a) * 0.25
			k.ma = k.a
		_step()
		var in_loop := not k.loop.is_empty()
		if in_loop and not was_loop:
			loops += 1
		was_loop = in_loop
		var lat := absf(T.lateral(k.idx, k.x, k.y))
		var dh := absf(k.wy - _gb(k.x, k.y) - T.ey[k.idx])
		if not in_loop and not k.glide:
			if lat > ((sb.TOYW + 4.0) if sb.toy else T.WALLD):
				off += 1
			if not k.air:
				worst = maxf(worst, dh)
		var d := k.idx - j0
		if d < 0:
			d += N
		far = maxf(far, float(d) / N)
		if i % 120 == 119:
			if Vector2(k.x - lx, k.y - ly).length() < 8.0:
				stuck += 1
			lx = k.x
			ly = k.y
		if float(d) / N > 0.985 and i > 600:
			steps = i
			break
	out["lap"] = {"reached": snappedf(far, 0.001), "steps": steps, "off": off, "gap": snappedf(worst, 0.1), "stuck": stuck, "loops": loops, "coins": int(sb.save.get("c", 0)) - c0}
	_check("lap forwards reached %.3f" % far, far > 0.98)
	_check("lap forwards stuck %d s" % stuck, stuck == 0)
	_check("no finish, no results", not k.finished and main.state == "race")


## the wrong way round (web CHECK): where the kart was stopped
func _back() -> void:
	var N := T.N
	var best := N - 8
	var since := 0
	var total := 0
	_place(best, true)
	var stops: Array = []
	var respawns := 0
	var gl: Dictionary = T.glide
	var reach := 60
	if not gl.is_empty():
		reach = ((int(gl["j1"]) - int(gl["rj"]) + N) % N) + 90   # (a canyon crossed the wrong way round sets the kart down on its far side: that is progress)
	for i in 160000:
		if total >= N - 30 or stops.size() >= 12:
			break
		var q := ((k.idx - 9) % N + N) % N
		var want := atan2(T.py[q] - k.y, T.px[q] - k.x)
		if k.loop.is_empty():
			k.a += Kart.ang_diff(want, k.a) * 0.25
			k.ma = k.a
		main.state = "race"
		race.state = "race"
		k.ai["auto"] = false
		race.update(DT, {"steer": 0.0, "brake": false, "nb": false, "mul": 1.0, "use": false, "back": false, "hold": false, "hold_sl": 1, "release": null})
		for e in k.events:
			if e == "respawn":
				respawns += 1
		race.fx.clear()
		k.events.clear()
		var d := best - k.idx
		if d < -N / 2:
			d += N
		if d > N / 2:
			d -= N
		if d > 0 and d < reach:
			total += d
			best = k.idx
			since = 0
		else:
			since += 1
		if since > 600:
			stops.append(snappedf(float(best) / N, 0.001))
			var nj := ((best - 26) % N + N) % N
			total += 26
			best = nj
			_place(nj, true)
			since = 0
	out["back"] = stops
	out["backRespawns"] = respawns
	_check("lap backwards stopped at %s" % str(stops), stops.is_empty())


## the mode's own rules: Park and the full stop, the item, a coin
func _mode() -> void:
	_place(int(round(0.1 * T.N)) % T.N)
	for i in 360:
		var q := (k.idx + 9) % T.N
		if k.loop.is_empty():
			k.a += Kart.ang_diff(atan2(T.py[q] - k.y, T.px[q] - k.x), k.a) * 0.25
			k.ma = k.a
		_step()
	var v0 := absf(k.speed)
	sb.park = true
	var inp: Dictionary = main._input_state()
	_check("parked: no throttle", float(inp["mul"]) == 0.0 and not bool(inp["brake"]))
	for i in 600:
		main.state = "race"
		race.state = "race"
		race.update(DT, inp)
		race.fx.clear()
		k.events.clear()
	out["park"] = [snappedf(v0, 1.0), snappedf(absf(k.speed), 0.1)]
	_check("Park stops the kart (%.0f -> %.1f)" % [v0, absf(k.speed)], v0 > 60.0 and absf(k.speed) < 0.5)
	sb.park = false
	_check("only the boost in an item box", race.roll_item(0) == "chili" and race.roll_item(3) == "chili")
	# a gold coin is taken by driving over it, counted, and is back later; a hidden one is found for good
	var ci := -1
	var ri := -1
	for i in sb.coin_n:
		if sb.coin_rare[i] == 0 and ci < 0 and sb.coin_t[i] == 0.0:
			ci = i
		if sb.coin_rare[i] != 0 and ri < 0 and sb.coin_t[i] == 0.0:
			ri = i
	var c0 := int(sb.save.get("c", 0))
	var got := 0
	for i in [ci, ri]:
		if i < 0:
			continue
		k.x = sb.coin_x[i]
		k.y = sb.coin_z[i]
		k.wy = sb.coin_y[i] - 5.0
		k.speed = 0.0
		k.air = false
		sb.park = true
		sb.tick(DT)
		sb.park = false
		if sb.coin_t[i] != 0.0:
			got += 1
	race.fx.clear()
	out["coins"] = [got, int(sb.save.get("c", 0)) - c0, sb.found()]
	_check("coins are taken", (ci < 0 or sb.coin_t[ci] > 0.0) and (ri < 0 or sb.coin_t[ri] < 0.0) and int(sb.save.get("c", 0)) - c0 == (1 if ci >= 0 else 0) + (10 if ri >= 0 else 0))
	_check("the read-out", (sb.readout() as Array).size() == 4 and String(sb.readout()[0]) == sb.title)


## drive on for a while and say whether the kart is free (not walled in, not stopped)
func _free_after(steps: int) -> bool:
	var x0 := k.x
	var y0 := k.y
	for i in steps:
		_step()
	return Vector2(k.x - x0, k.y - y0).length() > 30.0 and not is_nan(k.wy)


func _wait_travel(n0: int) -> bool:
	for i in 3000:
		await get_tree().process_frame
		if main.sb_arrived > n0 and not main.sb_trav:
			return true
	return false


## through a passage and back, fast travel, the race from the start line and the way back
## sets the kart down before a gate's mouth, facing it, and drives it in until it commits to the gate (it is then in the
## tunnel's corridor: Kart.tun)
func _into_gate(g: Dictionary) -> bool:
	var road: bool = g["road"]
	var back := 30.0 if road else 40.0
	k.x = float(g["x"]) - float(g["nx"]) * back
	k.y = float(g["z"]) - float(g["nz"]) * back
	k.a = atan2(float(g["nz"]), float(g["nx"]))
	k.ma = k.a
	k.speed = 120.0
	k.air = false
	k.loop = {}
	k.glide = false
	k.wvy = 0.0
	k.g_rate = 0.0
	if road:
		k.idx = (int(g["j"]) - int(round(back / (T.L / T.N))) + T.N) % T.N
		k.wy = T.ground(k.x, k.y) + T.k_ey(k.idx, k.x, k.y)
	else:
		k.wy = sb.ground(k.x, k.y, float(g["y"]) + 2.0)
		k.idx = sb.idx_of(k, k.idx)
	k.last_g = k.wy
	k.bpx = k.x
	k.bpy = k.y
	sb.cool = 0.0
	for i in 900:
		k.a = atan2(float(g["nz"]), float(g["nx"]))
		k.ma = k.a
		_step()
		if k.tun != null:
			return true
	return false


## the kart drives the tunnel (nobody touching anything: the throttle is on by itself) until it is out in a place.
## The next place is built on another thread and taken over by main.gd a stage a frame: frames are let go by between
## the steps. Returns the seconds of driving it took, or -1 if it never came out.
func _through() -> float:
	var n0: int = main.sb_arrived
	var steps := 0
	for f in 6000:
		race = main.race
		sb = race.sb
		for i in 4:
			_step()
			steps += 1
		main._sb_tick()
		if main.sb_arrived > n0:
			_bind()
			return steps * DT
		await get_tree().process_frame
	_bind()
	return -1.0


func _travel() -> void:
	var home: String = sb.id
	var tr := {}
	out["travel"] = tr
	if not sb.gates.is_empty():
		var g: Dictionary = sb.gates[0]
		var to := String(g["to"])
		var at := String(g["at"])
		tr["gate"] = String(g["id"])
		# 0. a gate that leads nowhere this copy has: the kart drives in, and comes back out of the same gate
		g["to"] = "nowhere"
		var in0 := _into_gate(g)
		var t_fail: float = (await _through()) if in0 else -1.0
		g["to"] = to
		var d0 := Vector2(k.x - float(g["x"]), k.y - float(g["z"])).length()
		tr["closed"] = [snappedf(t_fail, 0.01), snappedf(d0, 0.1)]
		_check("a way that is closed brings the kart back out of the same gate", in0 and t_fail > 0.0 and main.map_id == home and sb != null and k.tun == null and d0 < 60.0 and main.sb_go.is_empty())
		_check("...free of the walls", not sb.free or sb.touch(k.x, k.y, k.wy) == 0)
		# let the camera's tunnel be put away, as it would be when the kart has driven on
		main._sb_tun_over()
		# 1. drive into the gate: the commit, the tunnel for as long as the build takes, out of the matching gate
		var fired := _into_gate(g)
		tr["fired"] = fired
		_check("driving into the gate %s starts the journey" % String(g["id"]), fired)
		if fired:
			var sp0 := k.speed
			var t_tun: float = await _through()
			tr["to"] = main.map_id
			tr["tunnel_s"] = snappedf(t_tun, 0.01)
			_check("the journey to %s arrives" % to, t_tun > 0.0 and main.map_id == to and sb != null and race.karts.size() == 1 and race.player == k and k.tun == null)
			_check("the kart never stopped in the tunnel", k.speed > 60.0 and sp0 > 60.0)
			if sb != null:
				var ga = sb.gate_by_id(at)
				tr["atGate"] = ga != null
				var dist := 0.0
				if ga != null:
					dist = Vector2(k.x - float(ga["x"]), k.y - float(ga["z"])).length()
				tr["fromGate"] = snappedf(dist, 0.1)
				_check("it comes out of the matching gate %s" % at, ga != null and dist < 60.0)
				_check("out free of the walls", not sb.free or sb.touch(k.x, k.y, k.wy) == 0)
				_check("no countdown after a passage", main.state == "race")
				_check("drives on after arriving", _free_after(240))
				main._sb_tun_over()
				# and back the way it came, set down at the gate (as the map sets a kart down)
				var n1: int = main.sb_arrived
				main._sb_travel(home, String(g["id"]))
				var came2: bool = await _wait_travel(n1)
				_bind()
				_check("the journey back to %s arrives" % home, came2 and main.map_id == home and sb != null and main.sb_go.is_empty())
	# 2. fast travel to this place's own start line (the map's "To the start line")
	if sb != null:
		var n2: int = main.sb_arrived
		main._sb_travel(home, "")
		var came3: bool = await _wait_travel(n2)
		_bind()
		var j := (T.N - int(round(40.0 / (T.L / T.N)))) % T.N
		var d2 := Vector2(k.x - T.px[j], k.y - T.py[j]).length()
		tr["startLine"] = snappedf(d2, 0.1)
		_check("fast travel sets the kart down behind the start line", came3 and d2 < 1.0 and (not sb.free or sb.touch(k.x, k.y, k.wy) == 0))
		# 3. the start line's offer, the race, and the way back
		for i in 120:
			sb.park = true
			_step()
		for i in 1200:
			sb.park = false
			if sb.race_near:
				break
			var q := (k.idx + 9) % T.N
			if k.loop.is_empty():
				k.a += Kart.ang_diff(atan2(T.py[q] - k.y, T.px[q] - k.x), k.a) * 0.25
				k.ma = k.a
			_step()
		tr["offer"] = sb.race_near
		_check("the race is offered at the start line", sb.race_near)
		if sb.race_near:
			main._sb_race_here()
			_bind()
			tr["race"] = [race.karts.size(), race.mode, main.sb_back]
			_check("Race here starts an ordinary race", sb == null and race.karts.size() == 8 and race.mode == "" and main.sb_back == home)
			main._to_menu("")
			_bind()
			_check("leaving the race comes back to Sandbox", sb != null and race.karts.size() == 1 and main.map_id == home and main.sb_back == "" and main.state != "menu")
	# 4. the map: its pins, looking closer, travelling to a pin
	if sb != null:
		var S = load("res://scripts/sandbox.gd")
		main.state = "race"
		main._sb_map(true)
		await get_tree().process_frame
		await get_tree().process_frame
		var ui = main.sb_map_ui
		_check("the map opens and stops the game", ui != null and main.paused and main.panel_pause.visible)
		if ui != null:
			tr["pins"] = [ui.pins.size(), (S.places as Dictionary).size()]
			_check("a pin at every place this copy has", ui.pins.size() == (S.places as Dictionary).size() and ui.pins.size() > 0)
			ui._pick(home)
			await get_tree().process_frame
			tr["tunnels"] = (ui.tunnels(home) as Array).size()
			_check("looking closer at this place shows its tunnels", ui.zoom == home and ui.b_go.visible and (ui.tunnels(home) as Array).size() == sb.gates.size())
			var other := ""
			for q in ui.pins:
				if String(q["id"]) != home:
					other = String(q["id"])
					break
			if other != "":
				var n3: int = main.sb_arrived
				main._sb_map_travel(other)
				var came4: bool = await _wait_travel(n3)
				_bind()
				tr["mapTo"] = main.map_id
				_check("the map travels to %s" % other, came4 and main.map_id == other and sb != null and not main.paused and main.sb_map_ui == null and not main.panel_pause.visible)
			else:
				main._sb_map(false)
				_check("closing the map goes back to driving", not main.paused and main.sb_map_ui == null)
