class_name Race
extends RefCounted
## The race: eight karts, item boxes, thrown items and traps, the computer drivers and the
## standings. Ported from the web game's update0(), aiInput(), useItem(), spinOut() and the
## projectile code, keeping its numbers. Nothing here draws: the scene reads `karts`,
## `boxes`, `projectiles`, `hazards` and the `fx` list of things that just happened.

## the web game's ten classic items minus the freezer (an award item there); power 1 (traps, single
## shots) to 5 (comeback items). Odds centre on a higher power the further back you are.
const ITEM_POWER := {"oil": 1.0, "garlic": 1.0, "pepperoni": 1.0, "flour": 1.5, "trio": 2.0, "dough": 2.0, "chili": 2.4, "rush": 4.4, "wheel": 5.0}
const NEEDS_TARGET := ["dough", "wheel", "freezer"]
const DROPS := ["oil"]
const HOLDABLE := ["pepperoni", "dough", "flour"]
const NOBACK := ["chili", "garlic", "wheel", "rush", "freezer"]
const PTS := [15, 12, 10, 8, 6, 4, 2, 1]
const DEF_DIFF := {"skill": [0.88, 0.95], "ahead": 0.94, "behind": 1.06, "delay": [1.6, 5.5], "corner": 0.3, "boost": 0.3}

var T: TrackData
var karts: Array[Kart] = []
var player: Kart
var stand: Array[Kart] = []
var rng := RandomNumberGenerator.new()
var diff := {}
var sim_time := 0.0
var race_time := 0.0
var state := "countdown"      # countdown | race | done
var boxes: Array = []         # {x, y, gy, dbl, air, r}
var projectiles: Array = []   # {id, type, x, y, vx, vy, t, owner, safe, b, ...}
var hazards: Array = []       # {id, x, y, t, born, owner, armed}
var finish_count := 0
var wheel_n := 0
var wheel_at := -99.0
var next_id := 1
var fx: Array = []            # what just happened, for the scene: {t: "spin" | "box" | "boom" | ..., ...}
var _bump_t := {}


## One-player race: the player in the middle of the grid, seven computer drivers.
func setup(track: TrackData, roster: Dictionary, player_ri: int, seed_: int = 0) -> void:
	T = track
	var sd := seed_
	if sd == 0:
		rng.randomize()
		sd = int(rng.randi() & 0x7fffffff) + 1
	setup_cfg(track, roster, make_cfg(roster, player_ri, [1], sd), 1)


## Who sits where: humans (the host first) take the middle of the grid, computer drivers the rest.
## peers: the people racing, the host's id (1) first.
func make_cfg(roster: Dictionary, host_ri: int, peers: Array, seed_: int) -> Dictionary:
	var r := RandomNumberGenerator.new()
	r.seed = seed_
	var free: Array[int] = []
	for q in roster.get("racers", []):
		var ri := int((q as Dictionary)["ri"])
		if ri != host_ri:
			free.append(ri)
	for i in range(free.size() - 1, 0, -1):
		var j := r.randi_range(0, i)
		var t := free[i]
		free[i] = free[j]
		free[j] = t
	var order := [4, 3, 5, 2, 6, 1, 7, 0]
	var slots: Array = []
	for s in 8:
		slots.append({"ri": -1, "peer": 0, "own": false})
	for n in mini(peers.size(), 8):
		var s2: int = order[n]
		if n == 0:
			slots[s2] = {"ri": host_ri, "peer": int(peers[0]), "own": true}
		elif not free.is_empty():
			slots[s2] = {"ri": free.pop_front(), "peer": int(peers[n]), "own": false}
	for s3 in 8:
		if int(slots[s3]["ri"]) < 0 and not free.is_empty():
			slots[s3] = {"ri": free.pop_front(), "peer": 0, "own": false}
	return {"seed": seed_, "slots": slots}


## Builds the grid from a configuration (the same on every machine in an online race).
func setup_cfg(track: TrackData, roster: Dictionary, cfg: Dictionary, my_peer: int) -> void:
	T = track
	rng.seed = int(cfg["seed"])
	diff = T.diffs.get("normal", DEF_DIFF) if not T.diffs.is_empty() else DEF_DIFF
	var racers: Array = roster.get("racers", [])
	karts.clear()
	player = null
	var slots: Array = cfg["slots"]
	for s in slots.size():
		var sl: Dictionary = slots[s]
		var ri := int(sl["ri"])
		if ri < 0:
			continue
		var pid := int(sl["peer"])
		var info: Dictionary = roster.get("player", {}) if bool(sl["own"]) else _racer(racers, ri)
		var k := _make_kart(ri, s, pid != 0 and pid == my_peer, info)
		k.peer = pid
		k.human = pid != 0
		k.remote = pid != 0 and pid != my_peer
		k.ai["auto"] = pid == 0
		if pid != 0 and pid == my_peer:
			player = k
		karts.append(k)
	if player == null and not karts.is_empty():
		player = karts[0]
	boxes.clear()
	for b in T.boxes:
		var bd: Dictionary = b
		if bool(bd.get("train", false)):
			continue
		boxes.append({"x": float(bd["x"]), "y": float(bd["y"]), "gy": float(bd["gy"]), "dbl": bool(bd["dbl"]), "air": bool(bd["air"]), "r": 0.0})
	projectiles.clear()
	hazards.clear()
	finish_count = 0
	wheel_n = 0
	wheel_at = -99.0
	race_time = 0.0
	sim_time = 0.0
	state = "countdown"
	stand = standings()


func _racer(racers: Array, ri: int) -> Dictionary:
	for r in racers:
		if int((r as Dictionary)["ri"]) == ri:
			return r
	return {}


## staggered grid across four lanes: every kart has its own row (web makeKart)
func _make_kart(ri: int, slot: int, is_player: bool, info: Dictionary) -> Kart:
	var back := 5 + slot * 3
	var idx := (T.N - back) % T.N
	var lat: float = [-30.0, -10.0, 10.0, 30.0][slot % 4]
	var sk_r: Array = diff["skill"]
	var sk := float(sk_r[0]) + rng.randf() * (float(sk_r[1]) - float(sk_r[0]))
	var k := Kart.new()
	var x := T.px[idx] + T.nx[idx] * lat
	var y := T.py[idx] + T.ny[idx] * lat
	k.setup(T, {"x": x, "y": y, "a": T.ang[idx], "wy": T.ground(x, y)}, idx - T.N, info)
	k.idx = idx
	k.ri = ri
	k.racer_name = String(T.racers[ri]["name"]) if ri < T.racers.size() else String(info.get("name", "Racer"))
	k.is_player = is_player
	k.human = is_player
	k.info = info
	k.race = self
	k.ai = {"lane": lat, "lane_target": lat, "lane_t": 1.0 + rng.randf() * 3.0, "skill": sk, "item_delay": 0.0, "in_bend": false, "auto": not is_player}
	return k


func standings() -> Array[Kart]:
	var st: Array[Kart] = []
	st.assign(karts)
	st.sort_custom(_ahead)
	return st


func _ahead(a: Kart, b: Kart) -> bool:
	if a.finished and b.finished:
		return a.place < b.place
	if a.finished:
		return true
	if b.finished:
		return false
	return a.prog > b.prog


func position_of(k: Kart) -> int:
	return stand.find(k) + 1


func _wrap(d: int) -> int:
	if d > T.N / 2:
		d -= T.N
	if d < -T.N / 2:
		d += T.N
	return d


# ---------------------------------------------------------------- one physics step (web update0)

func update(dt: float, player_inp: Dictionary) -> void:
	stand = standings()
	sim_time += dt
	if state == "race":
		race_time += dt
	for k in karts:
		var inp: Dictionary
		if k.remote and not bool(k.ai.get("auto", false)) and not (k.rush > 0.0):
			# a friend's kart: their latest controls, and any item presses they sent
			inp = {"steer": float(k.net_inp["steer"]), "brake": bool(k.net_inp["brake"]), "nb": bool(k.net_inp["nb"]), "mul": float(k.net_inp["mul"]), "use": false, "back": false, "hold": false, "hold_sl": 1, "release": null}
			if not k.net_items.is_empty():
				item_intent(k, k.net_items.pop_front(), inp)
				if bool(inp["use"]) and k.item != "" and bool(k.net_inp["look"]) and not k.item in NOBACK:
					inp["back"] = true
		elif k.is_player and not bool(k.ai.get("auto", false)) and not (k.rush > 0.0):
			inp = player_inp
		else:
			inp = ai_input(k, dt)
		if k.rush > 0.0:
			inp["use"] = false
		k.step(inp, dt)

	# karts shove each other apart, the lighter one more; a garlic shield or a rush spins out whoever it touches
	for i in karts.size():
		for j in range(i + 1, karts.size()):
			var a := karts[i]
			var b := karts[j]
			var dx := b.x - a.x
			var dy := b.y - a.y
			var d2 := dx * dx + dy * dy
			if d2 < 361.0 and d2 > 0.0 and a.loop.is_empty() and b.loop.is_empty():
				var sa2 := a.shield > 0.0 or a.rush > 0.0
				var sb2 := b.shield > 0.0 or b.rush > 0.0
				if sa2 and not sb2:
					spin_out(b, "garlic")
				elif sb2 and not sa2:
					spin_out(a, "garlic")
				var d := sqrt(d2)
				var p := (19.0 - d) / 2.0
				var nx := dx / d
				var ny := dy / d
				var wa := a.sm_wgt
				var wb := b.sm_wgt
				var ra := 1.6 * wb / (wa + wb)
				var rb := 1.6 * wa / (wa + wb)
				a.x -= nx * p * ra
				a.y -= ny * p * ra
				b.x += nx * p * rb
				b.y += ny * p * rb
				if wa > wb * 1.15:
					b.speed *= 0.992
				elif wb > wa * 1.15:
					a.speed *= 0.992
				if a.boost > 0.0 and b.boost <= 0.0:
					b.speed *= 0.97
				elif b.boost > 0.0 and a.boost <= 0.0:
					a.speed *= 0.97
				var cl := (cos(a.ma) * a.speed - cos(b.ma) * b.speed) * nx + (sin(a.ma) * a.speed - sin(b.ma) * b.speed) * ny
				var key := i * 64 + j
				if cl > 28.0 and sim_time - float(_bump_t.get(key, -9.0)) > 0.45:
					_bump_t[key] = sim_time
					fx.append({"t": "bump", "x": (a.x + b.x) / 2.0, "y": (a.y + b.y) / 2.0, "h": (a.wy + b.wy) / 2.0 + 3.5, "cl": cl, "a": a, "b": b})

	# item boxes
	for b in boxes:
		if float(b["r"]) > 0.0:
			b["r"] = float(b["r"]) - dt
			continue
		for k in karts:
			var hit := false
			var ddx := k.x - float(b["x"])
			var ddy := k.y - float(b["y"])
			if bool(b["air"]):
				hit = k.glide and ddx * ddx + ddy * ddy < 400.0
			else:
				hit = ddx * ddx + ddy * ddy < 270.0
			if hit:
				b["r"] = 4.0
				var cap := 2 - (1 if k.item != "" else 0) - (1 if k.item2 != "" else 0) - (0 if k.held.is_empty() else 1) - k.pend.size()
				var give := mini(cap, 2 if bool(b["dbl"]) else 1)
				for g2 in give:
					k.pend.append(roll_item(stand.find(k)))
				if give > 0 and k.roll <= 0.0:
					k.roll = 1.1 if k.human else 0.5
				fx.append({"t": "box", "x": float(b["x"]), "y": float(b["y"]), "h": (float(b["gy"]) if bool(b["air"]) else T.ground(float(b["x"]), float(b["y"]))), "k": k})
				break

	# two items from different racers that meet cancel out
	var i2 := projectiles.size() - 1
	while i2 >= 0:
		var pa: Dictionary = projectiles[i2]
		if pa["type"] != "flour" and pa["type"] != "lob" and not pa.has("ph"):
			var j2 := i2 - 1
			while j2 >= 0:
				var pb: Dictionary = projectiles[j2]
				if pb["owner"] != pa["owner"] and pb["type"] != "flour" and pb["type"] != "lob" and not pb.has("ph"):
					var rr := 20.0 if (pa["type"] == "wheel" or pb["type"] == "wheel") else 15.0
					var ex := float(pa["x"]) - float(pb["x"])
					var ey := float(pa["y"]) - float(pb["y"])
					if ex * ex + ey * ey < rr * rr:
						fx.append({"t": "clash", "x": (float(pa["x"]) + float(pb["x"])) / 2.0, "y": (float(pa["y"]) + float(pb["y"])) / 2.0})
						pa["t"] = 0.0
						pb["t"] = 0.0
						pa["dead"] = true
						pb["dead"] = true
						break
				j2 -= 1
		i2 -= 1

	_projectiles(dt)
	_hazards(dt)

	for k in karts:
		if state == "race" and not k.finished and k.prog >= T.LAPS * T.N:
			k.finished = true
			k.finish_time = race_time
			finish_count += 1
			k.place = finish_count
			fx.append({"t": "finish", "k": k})


# ---------------------------------------------------------------- the computer drivers (web aiInput)

func ai_input(k: Kart, dt: float) -> Dictionary:
	var ai := k.ai
	ai["lane_t"] = float(ai["lane_t"]) - dt
	if float(ai["lane_t"]) <= 0.0:
		ai["lane_t"] = 1.5 + rng.randf() * 3.0
		ai["lane_target"] = (rng.randf() * 2.0 - 1.0) * 36.0
	var avoid := false
	for o in T.obst_lane:
		var dj: int = int(o["j"]) - k.idx
		if dj < 0:
			dj += T.N
		var ol: float = o["lat"]
		var orr: float = o["r"]
		if dj > 1 and dj < 28 and absf(float(ai["lane"]) - ol) < orr + 15.0:
			ai["lane_target"] = clampf(ol - orr - 22.0 if ol > 0.0 else ol + orr + 22.0, -42.0, 42.0)
			ai["lane_t"] = maxf(float(ai["lane_t"]), 1.2)
			avoid = true
	for L in T.loops:
		if bool(L["full"]):
			continue
		var dl: int = int(L["j"]) - k.idx
		if dl < 0:
			dl += T.N
		if dl > 1 and dl < 70:
			ai["lane_target"] = float(L["lat0"])
			avoid = true
	if not T.glide.is_empty():
		var dg: int = int(T.glide["rj"]) - k.idx
		if dg < 0:
			dg += T.N
		if dg > 0 and dg < 60:
			ai["lane_target"] = clampf(float(ai["lane_target"]), -28.0, 28.0)
			avoid = true
	ai["lane"] = float(ai["lane"]) + (float(ai["lane_target"]) - float(ai["lane"])) * minf(1.0, dt * (2.8 if avoid else 0.8))
	var ti := (k.idx + 9 + int(floor(maxf(0.0, k.speed) / 32.0))) % T.N
	var tx := T.px[ti]
	var ty := T.py[ti]
	var tnx := T.nx[ti]
	var tny := T.ny[ti]
	for L in T.loops:
		if not bool(L["full"]):
			continue
		var la := (int(L["j"]) - 1 - k.idx + T.N) % T.N
		var lb := (ti - k.idx + T.N) % T.N
		if la < lb and la < T.N / 2:
			var c := (int(L["j"]) - 1 + T.N) % T.N
			var ex := (lb - la) * T.L / T.N
			tx = T.px[c] + T.tx[c] * ex
			ty = T.py[c] + T.ty[c] * ex
			tnx = T.nx[c]
			tny = T.ny[c]
			break
	var lane: float = ai["lane"]
	var des := atan2(ty + tny * lane - k.y, tx + tnx * lane - k.x)
	var steer := clampf(Kart.ang_diff(des, k.a) * 2.6, -1.0, 1.0)
	var bend := absf(Kart.ang_diff(T.ang[(k.idx + 18) % T.N], T.ang[k.idx]))
	var mul: float = 0.97 if k.is_player else float(ai["skill"])
	if player != null and not k.is_player and state == "race":
		var d := k.prog - player.prog
		mul *= float(diff["ahead"]) if d > 30 else (float(diff["behind"]) if d < -30 else 1.0)
	mul *= 1.0 - minf(0.3, maxf(0.0, (bend - 0.6) * float(diff["corner"])))
	var in_bend := bend > 0.9
	if bool(ai["in_bend"]) and not in_bend and rng.randf() < float(diff["boost"]):
		k.boost = maxf(k.boost, float(diff.get("bst", 0.55)))
	ai["in_bend"] = in_bend
	var use := false
	var back := false
	var hold := false
	var release = null
	if k.item != "":
		ai["item_delay"] = float(ai["item_delay"]) - dt
		if float(ai["item_delay"]) <= 0.0:
			use = true
			var i := stand.find(k)
			var ah: Kart = stand[i - 1] if i > 0 else null
			var bh: Kart = stand[i + 1] if i >= 0 and i + 1 < stand.size() else null
			var a_close := ah != null and (ah.prog - k.prog) < 14
			var b_close := bh != null and (k.prog - bh.prog) < 12
			var it := k.item
			if it == "oil" or it == "flour":
				back = not (a_close and rng.randf() < 0.35)
			elif it == "pepperoni" or it == "trio" or it == "dough":
				back = b_close and not a_close
			if it == "garlic" and not b_close and not a_close and rng.randf() < 0.5:
				use = false
				ai["item_delay"] = 0.6
			if k.item == "pepperoni" and not a_close and not b_close and rng.randf() < 0.6:
				use = false
				ai["item_delay"] = 0.5
			if use and k.held.is_empty() and k.item in HOLDABLE and not b_close and (k.item in DROPS or rng.randf() < 0.35) and rng.randf() < 0.7:
				use = false
				hold = true
	if not k.held.is_empty():
		var i3 := stand.find(k)
		var bh2: Kart = stand[i3 + 1] if i3 >= 0 and i3 + 1 < stand.size() else null
		if (bh2 != null and (k.prog - bh2.prog) < 6 and float(k.held["t"]) > 1.5) or float(k.held["t"]) > 9.0:
			release = "back"
	return {"steer": steer, "brake": false, "nb": false, "mul": mul, "use": use, "back": back, "hold": hold, "hold_sl": 1, "release": release}


# ---------------------------------------------------------------- items

## web itemIntent: what a press on an item button means right now ("fwd", "fwd2", "hold", "hold2")
func item_intent(k: Kart, it: String, o: Dictionary) -> void:
	var sl := 2 if it.ends_with("2") else 1
	var is_hold := it.begins_with("hold")
	if not k.held.is_empty() and int(k.held["sl"]) == sl:
		o["release"] = "back" if is_hold else "fwd"
	elif not k.held.is_empty():
		o["use"] = true
		o["back"] = is_hold
	else:
		if sl == 2 and k.item2 != "" and not (k.roll > 0.0):
			var t := k.item
			k.item = k.item2
			k.item2 = t
		if is_hold and k.item != "" and k.item in HOLDABLE:
			o["hold"] = true
			o["hold_sl"] = sl
		else:
			o["use"] = true
			o["back"] = is_hold


func roll_item(pos: int) -> String:
	var n := karts.size()
	var f := float(pos) / float(n - 1) if n > 1 else 0.0
	var target := 1.0 + f * 4.0
	var odds := {}
	var sum := 0.0
	for k in ITEM_POWER:
		var w: float = ITEM_POWER[k]
		if pos == 0 and k in NEEDS_TARGET:
			continue
		if f < 0.35 and w >= 4.0:
			continue
		if f < 0.15 and w >= 3.0:
			continue
		if k == "wheel" and (wheel_n >= 4 or race_time - wheel_at < 28.0):
			continue
		var d := w - target
		var o := exp(-d * d / (2.0 * 0.85 * 0.85)) * (0.55 if k == "wheel" else 1.0)
		odds[k] = o
		sum += o
	var r := rng.randf() * sum
	for k in odds:
		r -= float(odds[k])
		if r <= 0.0:
			if k == "wheel":
				wheel_n += 1
				wheel_at = race_time
			return k
	return "pepperoni"


func after_roll(k: Kart) -> void:
	var dl: Array = diff["delay"]
	k.ai["item_delay"] = float(dl[0]) + rng.randf() * (float(dl[1]) - float(dl[0]))


func _proj(k: Kart, type: String, x: float, y: float, vx: float, vy: float, t: float, safe: float) -> Dictionary:
	var p := {"id": next_id, "type": type, "x": x, "y": y, "px": x, "py": y, "vx": vx, "vy": vy, "t": t, "t0": t, "owner": k, "safe": safe, "b": 0, "target": null}
	next_id += 1
	projectiles.append(p)
	return p


func _hazard(k: Kart, x: float, y: float) -> void:
	hazards.append({"id": next_id, "x": x, "y": y, "t": 30.0, "born": 0.0, "owner": k, "armed": false})
	next_id += 1


func use_item(k: Kart, back_in: bool) -> void:
	var it := k.item
	if it == "":
		return
	var back := it in DROPS or (back_in and not it in NOBACK)
	if it == "garlic":
		k.item = k.item2
		k.item2 = ""
		add_shield(k, 1)
		return
	k.item = k.item2
	k.item2 = ""
	fx.append({"t": "use", "k": k, "it": it, "back": back})
	if k.item != "":
		k.ai["item_delay"] = 0.6 + rng.randf() * 1.6
	var ca := cos(k.a)
	var sa := sin(k.a)
	var i := stand.find(k)
	if it == "chili":
		k.boost = maxf(k.boost, 1.4)
	elif it == "pepperoni":
		if back:
			_proj(k, "pep", k.x - ca * 10.0, k.y - sa * 10.0, -ca * 240.0, -sa * 240.0, 4.0, 0.3)
		else:
			var v := 265.0 + maxf(0.0, k.speed)
			_proj(k, "pep", k.x + ca * 10.0, k.y + sa * 10.0, ca * v, sa * v, 4.4, 0.3)
	elif it == "oil":
		if back:
			_hazard(k, k.x - cos(k.ma) * 24.0, k.y - sin(k.ma) * 24.0)
		else:
			var v2 := maxf(0.0, k.speed) + 150.0
			_proj(k, "lob", k.x + ca * 8.0, k.y + sa * 8.0, ca * v2, sa * v2, 0.6, 9.0)
	elif it == "dough":
		var tg: Kart = null
		if back:
			tg = stand[i + 1] if i + 1 < stand.size() else null
		else:
			tg = stand[i - 1] if i > 0 else null
		var dr := -1.0 if back else 1.0
		var v3 := 280.0 if back else 300.0 + maxf(0.0, k.speed) * 0.5
		var p := _proj(k, "dough", k.x + ca * 10.0 * dr, k.y + sa * 10.0 * dr, ca * v3 * dr, sa * v3 * dr, 9.0, 0.3)
		p["target"] = tg
	elif it == "trio":
		for off in [-0.17, 0.0, 0.17]:
			var an: float = k.a + off + (PI if back else 0.0)
			var v4 := 240.0 if back else 300.0 + maxf(0.0, k.speed)
			_proj(k, "pep", k.x + cos(an) * 12.0, k.y + sin(an) * 12.0, cos(an) * v4, sin(an) * v4, 4.0, 0.35)
	elif it == "flour":
		if back:
			_proj(k, "flour", k.x - cos(k.ma) * 18.0, k.y - sin(k.ma) * 18.0, 0.0, 0.0, 0.3, 9.0)
		else:
			var v5 := maxf(0.0, k.speed) + 170.0
			_proj(k, "flour", k.x + ca * 10.0, k.y + sa * 10.0, ca * v5, sa * v5, 0.75, 9.0)
	elif it == "wheel":
		var p2 := _proj(k, "wheel", k.x, k.y, 0.0, 0.0, 16.0, 9.0)
		p2["target"] = null if (stand.size() > 0 and stand[0] == k) else stand[0]
		p2["prog"] = float(k.prog + 2)
		p2["lat"] = T.lateral(k.idx, k.x, k.y)
		p2["spin"] = 0.0
		p2["dir"] = k.a
		p2["age"] = 0.0
	elif it == "rush":
		k.rush = 3.2
		k.boost = maxf(k.boost, 3.2)
		k.drift = 0


func hold_item(k: Kart, sl: int) -> bool:
	var it := k.item
	if it == "" or not it in HOLDABLE or not k.held.is_empty():
		return false
	k.held = {"it": it, "sl": sl, "t": 0.0}
	k.item = k.item2
	k.item2 = ""
	fx.append({"t": "hold", "k": k, "it": it})
	return true


func drop_held(k: Kart) -> String:
	if k.held.is_empty():
		return ""
	var it: String = k.held["it"]
	k.held = {}
	return it


func release_held(k: Kart, back: bool) -> void:
	var it := drop_held(k)
	if it == "":
		return
	var a := k.item
	var b := k.item2
	var d: float = k.ai.get("item_delay", 0.0)
	k.item = it
	k.item2 = ""
	use_item(k, back)
	k.item = a
	k.item2 = b
	k.ai["item_delay"] = d


## where a held item trails: right behind the kart
func held_pos(k: Kart) -> Vector2:
	return Vector2(k.x - cos(k.ma) * 11.0, k.y - sin(k.ma) * 11.0)


func _absorb_held(k: Kart) -> bool:
	if k.held.is_empty():
		return false
	var hp := held_pos(k)
	drop_held(k)
	k.inv = maxf(k.inv, 0.5)
	fx.append({"t": "absorb", "k": k, "x": hp.x, "y": hp.y})
	return true


func _held_block(k: Kart, p: Dictionary) -> bool:
	if k.held.is_empty() or (p["owner"] == k and float(p["safe"]) > 0.0):
		return false
	var hp := held_pos(k)
	var dx := float(p["x"]) - hp.x
	var dz := float(p["y"]) - hp.y
	if dx * dx + dz * dz > 121.0:
		return false
	drop_held(k)
	fx.append({"t": "absorb", "k": k, "x": hp.x, "y": hp.y})
	return true


func add_shield(k: Kart, n: int) -> void:
	k.sh_l = mini(2, k.sh_l + n)
	fx.append({"t": "shield", "k": k})


func _absorb(k: Kart) -> bool:
	if not (k.sh_l > 0):
		return false
	k.sh_l -= 1
	k.abs_t = 0.6
	k.inv = maxf(k.inv, 0.6)
	fx.append({"t": "unshield", "k": k})
	return true


## web spinOut: world hazards (world=true) also hit karts in the air
func spin_out(k: Kart, kind: String, world := false, force := false) -> bool:
	if force:
		if not k.loop.is_empty():
			return false
		k.shield = 0.0
		k.abs_t = 0.0
	else:
		if k.inv > 0.0 or k.rush > 0.0 or k.abs_t > 0.0:
			return false
		if not world and (k.air or k.glide or not k.loop.is_empty()):
			return false
	if k.shield > 0.0:
		return false
	if not force and not world and _absorb_held(k):
		return false
	if not force and not world and _absorb(k):
		return false
	k.spin = 1.1 * (1.25 - 0.25 * k.sm_wgt)
	k.inv = k.spin + 3.0
	k.speed *= 0.3
	k.drift = 0
	k.charge = 0.0
	k.boost = 0.0
	if not k.air and k.loop.is_empty():
		k.air = true
		k.big = false
		k.air_t = 0.0
		k.wvy = k.g_rate + 40.0
	fx.append({"t": "spin", "k": k, "kind": kind})
	return true


func _oil_up(k: Kart) -> void:
	k.oil_t = 5.0
	k.inv = maxf(k.inv, 3.0)
	fx.append({"t": "oily", "k": k})


# ---------------------------------------------------------------- thrown items

func _rail_sync(p: Dictionary) -> void:
	var j0 := posmod(int(round(float(p["rp"]))), T.N)
	var bo := 0
	var bd := 1e18
	for o in range(-10, 11):
		var q := (j0 + o + T.N) % T.N
		var d := (T.px[q] - float(p["x"])) ** 2 + (T.py[q] - float(p["y"])) ** 2
		if d < bd:
			bd = d
			bo = o
	var qi := (j0 + bo + T.N) % T.N
	var f := clampf(((float(p["x"]) - T.px[qi]) * T.tx[qi] + (float(p["y"]) - T.py[qi]) * T.ty[qi]) / (T.L / T.N), -0.5, 0.5)
	p["rp"] = round(float(p["rp"])) + bo + f
	p["rl"] = (float(p["x"]) - T.px[qi]) * T.nx[qi] + (float(p["y"]) - T.py[qi]) * T.ny[qi]


## a homing item rides the road towards its target, then closes in directly (web homeStep)
func _home_step(p: Dictionary, tg: Kart, dt: float, want: float, tr: float) -> void:
	var v := Vector2(float(p["vx"]), float(p["vy"])).length()
	if v == 0.0:
		v = want
	v += (want - v) * minf(1.0, dt * 3.0)
	if not p.has("rp"):
		var o: Kart = p["owner"]
		p["rp"] = float(o.prog) if o != null else 0.0
		_rail_sync(p)
	var dx := tg.x - float(p["x"])
	var dy := tg.y - float(p["y"])
	var dd := sqrt(dx * dx + dy * dy)
	var gap := float(tg.prog) - float(p["rp"])
	if dd < 75.0 or not tg.loop.is_empty() or absf(gap) < 3.0:
		var des := atan2(dy, dx)
		var cur := atan2(float(p["vy"]), float(p["vx"]))
		cur += clampf(Kart.ang_diff(des, cur), -tr * dt, tr * dt)
		p["vx"] = cos(cur) * v
		p["vy"] = sin(cur) * v
		p["x"] = float(p["x"]) + float(p["vx"]) * dt
		p["y"] = float(p["y"]) + float(p["vy"]) * dt
		_rail_sync(p)
		var rl: float = p["rl"]
		if absf(rl) > T.CURB and dd > 40.0:
			var qi := posmod(int(round(float(p["rp"]))), T.N)
			var pl := signf(rl) * (absf(rl) - T.CURB)
			p["x"] = float(p["x"]) - T.nx[qi] * pl
			p["y"] = float(p["y"]) - T.ny[qi] * pl
			p["rl"] = rl - pl
		return
	var st := v * dt / (T.L / T.N)
	p["rp"] = float(p["rp"]) + signf(gap) * minf(absf(gap), st)
	var tl := clampf(T.lateral(tg.idx, tg.x, tg.y), -(T.RW - 10.0), T.RW - 10.0)
	var rl2: float = p["rl"]
	rl2 += (tl - rl2) * minf(1.0, dt * (4.0 if absf(gap) < 30.0 else 1.2))
	rl2 = clampf(rl2, -(T.RW - 6.0), T.RW - 6.0)
	p["rl"] = rl2
	var P := T.track_at(float(p["rp"]), rl2)
	var mx := P.x - float(p["x"])
	var my := P.y - float(p["y"])
	var ml := sqrt(mx * mx + my * my)
	if ml == 0.0:
		ml = 1.0
	p["vx"] = mx / ml * v
	p["vy"] = my / ml * v
	p["x"] = P.x
	p["y"] = P.y


func _projectiles(dt: float) -> void:
	var i := projectiles.size() - 1
	while i >= 0:
		var p: Dictionary = projectiles[i]
		p["px"] = p["x"]
		p["py"] = p["y"]
		if p.get("dead", false):
			projectiles.remove_at(i)
			i -= 1
			continue
		p["t"] = float(p["t"]) - dt
		p["safe"] = float(p["safe"]) - dt
		var type: String = p["type"]
		var tg: Kart = p["target"]
		if type == "dough" and tg != null and not tg.finished:
			_home_step(p, tg, dt, maxf(300.0, absf(tg.speed) * 1.22 + 70.0), 9.0 if Vector2(tg.x - float(p["x"]), tg.y - float(p["y"])).length() < 70.0 else 5.5)
		elif type != "wheel":
			p["x"] = float(p["x"]) + float(p["vx"]) * dt
			p["y"] = float(p["y"]) + float(p["vy"]) * dt
		var d := Vector2(float(p["x"]), float(p["y"])).length()
		if d > T.RIM:
			var nx := float(p["x"]) / d
			var ny := float(p["y"]) / d
			var dot := float(p["vx"]) * nx + float(p["vy"]) * ny
			p["vx"] = float(p["vx"]) - 2.0 * dot * nx
			p["vy"] = float(p["vy"]) - 2.0 * dot * ny
			p["x"] = nx * (T.RIM - 1.0)
			p["y"] = ny * (T.RIM - 1.0)
			p["b"] = int(p["b"]) + 1
			if int(p["b"]) > 3:
				p["t"] = 0.0
		if type == "wheel":
			if _wheel(p, dt):
				projectiles.remove_at(i)
			i -= 1
			continue
		if type == "flour":
			if float(p["t"]) <= 0.0:
				for k in karts:
					if k == p["owner"] or not k.loop.is_empty():
						continue
					if (k.x - float(p["x"])) ** 2 + (k.y - float(p["y"])) ** 2 < 38.0 * 38.0:
						spin_out(k, "flour")
				fx.append({"t": "flour", "x": float(p["x"]), "y": float(p["y"])})
				projectiles.remove_at(i)
			i -= 1
			continue
		if type == "lob":
			if float(p["t"]) <= 0.0:
				if not (not T.glide.is_empty() and T.ground(float(p["x"]), float(p["y"])) < T.glide_y(float(p["x"]), float(p["y"])) - 20.0):
					_hazard(p["owner"], float(p["x"]), float(p["y"]))
				projectiles.remove_at(i)
			i -= 1
			continue
		var hit := false
		for k in karts:
			if not k.loop.is_empty() or (k == p["owner"] and (float(p["safe"]) > 0.0 or type == "pep")):
				continue
			if _held_block(k, p):
				hit = true
				break
			if (k.x - float(p["x"])) ** 2 + (k.y - float(p["y"])) ** 2 < 200.0 and k.inv <= 0.0:
				spin_out(k, type)
				hit = true
				p["pop"] = true
				fx.append({"t": "hit", "k": k, "type": type, "x": float(p["x"]), "y": float(p["y"])})
				break
		for h in hazards:
			if (float(h["x"]) - float(p["x"])) ** 2 + (float(h["y"]) - float(p["y"])) ** 2 < 100.0:
				h["t"] = 0.0
				hit = true
		if hit or float(p["t"]) <= 0.0:
			projectiles.remove_at(i)
		i -= 1


## the pizza wheel: races along the road to the leader, hovers over them, winds up and slices down.
## Returns true when it is gone.
func _wheel(p: Dictionary, dt: float) -> bool:
	var tg: Kart = p["target"]
	var per := T.L / T.N
	p["age"] = float(p.get("age", 0.0)) + dt
	var ph: String = p.get("ph", "")
	p["spin"] = float(p["spin"]) + dt * (46.0 if ph == "wind" else (30.0 if ph != "" else 24.0))
	if ph != "":
		p["pt"] = float(p["pt"]) - dt
		if tg == null or tg.finished:
			p["t"] = 0.0
		else:
			p["x"] = tg.x
			p["y"] = tg.y
			p["dir"] = tg.ma
		if ph == "wind" and float(p["pt"]) <= 0.0 and tg != null and not tg.finished:
			p["ph"] = "slice"
			p["pt"] = 0.16
		elif ph == "slice" and float(p["pt"]) <= 0.0:
			p["ph"] = "done"
			p["pt"] = 0.4
			if tg != null and not tg.finished:
				if spin_out(tg, "wheel", true):
					tg.spin *= 1.7
					tg.inv = tg.spin + 3.0
					tg.speed = 0.0
					tg.wvy = maxf(tg.wvy, 62.0)
				fx.append({"t": "slice", "k": tg})
		elif ph == "done" and float(p["pt"]) <= 0.0:
			p["t"] = 0.0
	elif tg != null and tg.loop.is_empty() and float(tg.prog) - float(p["prog"]) > 4.0:
		p["prog"] = float(p["prog"]) + minf(float(tg.prog) - float(p["prog"]) - 3.5, dt * maxf(760.0 / per, absf(tg.speed) / per * 1.8 + 30.0))
		var lat: float = p["lat"]
		var P := T.track_at(float(p["prog"]), lat)
		p["lat"] = lat + (clampf(T.lateral(tg.idx, tg.x, tg.y), -(T.RW - 12.0), T.RW - 12.0) - lat) * minf(1.0, dt * (3.0 if float(tg.prog) - float(p["prog"]) < 40.0 else 1.0))
		p["dir"] = atan2(P.y - float(p["y"]), P.x - float(p["x"]))
		p["x"] = P.x
		p["y"] = P.y
	elif tg != null and tg.loop.is_empty():
		var dx := tg.x - float(p["x"])
		var dy := tg.y - float(p["y"])
		var dd := sqrt(dx * dx + dy * dy)
		if dd == 0.0:
			dd = 1.0
		var v := maxf(700.0, absf(tg.speed) * 1.7 + 120.0) * dt
		p["dir"] = atan2(dy, dx)
		p["x"] = float(p["x"]) + dx / dd * minf(v, dd)
		p["y"] = float(p["y"]) + dy / dd * minf(v, dd)
		if dd < 24.0:
			p["ph"] = "wind"
			p["pt"] = 0.62
			fx.append({"t": "wind", "k": tg})
	elif tg == null:
		p["prog"] = float(p["prog"]) + dt * 450.0 / 8.0
		var P2 := T.track_at(float(p["prog"]), 0.0)
		p["dir"] = atan2(P2.y - float(p["y"]), P2.x - float(p["x"]))
		p["x"] = P2.x
		p["y"] = P2.y
	return float(p["t"]) <= 0.0


func _hazards(dt: float) -> void:
	var i := hazards.size() - 1
	while i >= 0:
		var h: Dictionary = hazards[i]
		h["t"] = float(h["t"]) - dt
		h["born"] = float(h["born"]) + dt
		var o: Kart = h["owner"]
		if not bool(h["armed"]) and (o == null or (o.x - float(h["x"])) ** 2 + (o.y - float(h["y"])) ** 2 > 34.0 * 34.0):
			h["armed"] = true
		for k in karts:
			if not k.loop.is_empty() or (k == o and not bool(h["armed"])):
				continue
			if (k.x - float(h["x"])) ** 2 + (k.y - float(h["y"])) ** 2 < 200.0 and k.inv <= 0.0:
				spin_out(k, "oil")
				h["t"] = 0.0
				break
		if float(h["t"]) <= 0.0:
			hazards.remove_at(i)
		i -= 1


# ---------------------------------------------------------------- the finish

## when the player is done, everyone still racing gets an estimated time and place (web finalizeRace)
func finalize() -> void:
	var st := standings()
	for k in st:
		if not k.finished:
			k.finished = true
			finish_count += 1
			k.place = finish_count
			k.est = true
			k.finish_time = race_time + maxf(0.0, T.LAPS * T.N - k.prog) * 8.0 / maxf(60.0, k.base_max * 0.85)
	state = "done"
	stand = standings()
