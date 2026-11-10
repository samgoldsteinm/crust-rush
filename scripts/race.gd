class_name Race
extends RefCounted
## The race: eight karts, item boxes, thrown items and traps, the computer drivers and the
## standings. Ported from the web game's update0(), aiInput(), useItem(), spinOut() and the
## projectile code, keeping its numbers. Nothing here draws: the scene reads `karts`,
## `boxes`, `projectiles`, `hazards` and the `fx` list of things that just happened.

## the web game's ten classic items minus the freezer (an award item there); power 1 (traps, single
## shots) to 5 (comeback items). Odds centre on a higher power the further back you are.
const ITEM_POWER := {"oil": 1.0, "forks": 1.0, "boxes": 1.0, "garlic": 1.0, "pepperoni": 1.0, "flour": 1.5,
	"trio": 2.0, "garlic2": 2.0, "dough": 2.0, "meatball": 2.0, "bomb": 2.0, "cutter": 2.2, "chili": 2.4,
	"torpedo": 3.0, "jalapeno": 3.0, "shroom": 3.0, "sauce": 3.0, "twister": 3.0, "swap": 3.2, "magnet": 3.4,
	"freezer": 4.0, "heat": 4.0, "ghost": 4.0, "rush": 4.4, "cannon": 5.0, "wheel": 5.0}
const NEEDS_TARGET := ["dough", "torpedo", "magnet", "swap", "ghost", "wheel", "freezer", "sauce"]
const DROPS := ["oil", "forks", "boxes"]
const HOLDABLE := ["pepperoni", "dough", "flour"]
const NOBACK := ["chili", "garlic", "wheel", "rush", "freezer", "jalapeno", "torpedo", "shroom", "magnet", "cutter", "sauce", "heat", "forks", "ghost", "cannon", "twister", "swap", "boxes"]
## the award items: each comes into the game once its achievement is won (web ITEM_RETIRED)
const ITEM_AWARD := {"meatball": "podium10", "bomb": "items100", "twister": "drift50", "freezer": "loops25"}
## the newer items' colours (web NEWITEMS)
const ITEM_COL2 := {"jalapeno": "#4fd02a", "meatball": "#9a5a32", "torpedo": "#8fc8e8", "shroom": "#e05a3a", "magnet": "#ff3b3b", "cutter": "#d8dde3",
	"sauce": "#d8301c", "heat": "#ff7a1a", "bomb": "#e2b06a", "forks": "#c9ced6", "ghost": "#e8f6ff", "cannon": "#ffd23a", "twister": "#f3dfb4",
	"swap": "#b26bff", "boxes": "#c98b4e", "garlic2": "#b8ffb0"}
const PTS := [15, 12, 10, 8, 6, 4, 2, 1]
## every racer's special (web ABIL): name, what it does, its colour
const ABIL := {
	"pep": ["Pepperoni Storm", "Fires a fan of six spinning pepperoni slices low along the track, ahead or, while you look back, behind you. Each slice ricochets between the track walls and off anything it hits and vanishes on its third hit.", "#ff5a2a"],
	"basil": ["Pesto Rush", "The longest ability boost: nothing can hit you while it lasts, and it ignores the slow cheese.", "#3fd06a"],
	"olive": ["Slick Trail", "Leaves ten olive-oil slicks behind; nothing can touch you while you lay them. Drive through one and your wheels get coated: no spin, but slowed a lot for 5 seconds.", "#c8b23a"],
	"mozz": ["Melt Shield", "Wraps the kart in stretchy cheese that blocks every hit for a while, with a quick burst of speed.", "#fff4c0"],
	"chili": ["Fire Trail", "A fiery boost that leaves burning flames on the road: anyone who drives into them spins out and catches fire. Nothing can hit you while it burns.", "#ff3a12"],
	"shroom": ["Mega Shroom", "Grows huge and unstoppable and flattens anyone it touches for 3 seconds.", "#c8a06a"],
	"pineapple": ["Spiky Shockwave", "A huge spiky blast that spins out every racer anywhere near you, even in the air. Goes through every protection.", "#ffd23a"],
	"anchovy": ["School of Fish", "Launches three anchovies that hunt down the next three racers ahead, or the three behind if you look back. A well-timed hop dodges one.", "#8fc8e8"],
}
const ABIL_TIME := 30.0
const MEGA_T := 5.5
const PESTO_T := 5.9
const OLIVE_T := 2.6
const FLAT_T := 3.0
const BURN_T := 2.0
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
var traffic: Array = []       # {s, s0, lat, latT, laneT, v, len, x, y, ang, i, hide}
var rollers: Array = []       # {j, ph, lat, x, y}
var walkers: Array = []       # {j, lat, latT, v, ph, pause, H, along, x, y, face, hit_t}
var train := {}               # {px, py, ux, uy, span, len, v, cars: [{off, L, t}], state, wait, pos, dir}
var _bump_t := {}
var mode := ""               # "lss": Last Slice Standing
var lss_lap := 0
var lss_done := false
var items_off := {}         # items switched off (settings) or not yet won (award items): {name: true}


## One-player race: the player in the middle of the grid, seven computer drivers.
func setup(track: TrackData, roster: Dictionary, player_ri: int, seed_: int = 0, cls := "medium", build := {}) -> void:
	T = track
	var sd := seed_
	if sd == 0:
		rng.randomize()
		sd = int(rng.randi() & 0x7fffffff) + 1
	setup_cfg(track, roster, make_cfg(roster, player_ri, [1], sd, cls, build), 1)


## the web's speed classes: top speed and how sharp the computer drivers are
const CLASS_MUL := {"small": 0.86, "medium": 1.0, "large": 1.14, "reverse": 1.14}
const CLASS_AI := {"small": "easy", "medium": "normal", "large": "hard", "reverse": "hard"}


## Who sits where: humans (the host first) take the middle of the grid, computer drivers the rest.
## peers: the people racing, the host's id (1) first. prefs: each joined player's chosen driver and kart
## ({peer id: {"ri", "build"}}); a driver someone else already has goes to the next free one.
func make_cfg(roster: Dictionary, host_ri: int, peers: Array, seed_: int, cls := "medium", host_build := {}, prefs := {}) -> Dictionary:
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
			var want := int((prefs.get(int(peers[n]), {}) as Dictionary).get("ri", -1))
			var pick: int = free.pop_at(free.find(want)) if free.has(want) else free.pop_front()
			slots[s2] = {"ri": pick, "peer": int(peers[n]), "own": false}
	for s3 in 8:
		if int(slots[s3]["ri"]) < 0 and not free.is_empty():
			slots[s3] = {"ri": free.pop_front(), "peer": 0, "own": false}
	# every slot's kart build travels with the race, so every machine builds the same karts
	for s4 in 8:
		var ri4 := int(slots[s4]["ri"])
		if ri4 < 0:
			continue
		var pb = (prefs.get(int(slots[s4]["peer"]), {}) as Dictionary).get("build")
		if bool(slots[s4]["own"]) and not host_build.is_empty():
			slots[s4]["build"] = host_build
		elif pb is Dictionary and not (pb as Dictionary).is_empty():
			slots[s4]["build"] = pb
		else:
			var rq := _racer(roster.get("racers", []), ri4)
			if rq.has("build"):
				slots[s4]["build"] = rq["build"]
	return {"seed": seed_, "slots": slots, "cls": cls}


## Builds the grid from a configuration (the same on every machine in an online race).
func setup_cfg(track: TrackData, roster: Dictionary, cfg: Dictionary, my_peer: int) -> void:
	T = track
	rng.seed = int(cfg["seed"])
	var cls := String(cfg.get("cls", "medium"))
	T.class_mul = float(CLASS_MUL.get(cls, 1.0))
	var dk := String(CLASS_AI.get(cls, "normal"))
	diff = (T.diffs.get(dk, T.diffs.get("normal", DEF_DIFF)) if not T.diffs.is_empty() else DEF_DIFF).duplicate()
	diff["key"] = dk
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
		var pl: Dictionary = roster.get("player", {})
		var info: Dictionary = pl if bool(sl["own"]) and int(pl.get("ri", -1)) == ri else _racer(racers, ri)
		# any garage build: the parts' placements and stats (the model itself is made by the view)
		var spec = sl.get("build")
		if spec is Dictionary and KartBuilder.ready():
			var bi := KartBuilder.describe(spec, ri)
			if not bi.is_empty():
				info = info.duplicate()
				info.merge(bi, true)
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
	_setup_haz()
	finish_count = 0
	wheel_n = 0
	wheel_at = -99.0
	race_time = 0.0
	sim_time = 0.0
	state = "countdown"
	stand = standings()


func _setup_haz() -> void:
	traffic.clear()
	for c in T.haz.get("traffic", []):
		var cd: Dictionary = c
		traffic.append({"s": float(cd["s0"]), "s0": float(cd["s0"]), "lat": float(cd["lat"]), "latT": float(cd["lat"]), "laneT": float(cd["laneT"]), "v": float(cd["v"]), "len": float(cd["len"]), "x": 0.0, "y": 0.0, "ang": 0.0, "i": 0, "hide": false})
	rollers.clear()
	for r in T.haz.get("rollers", []):
		var rd: Dictionary = r
		var j := int(rd["j"])
		rollers.append({"j": j, "ph": float(rd["ph"]), "lat": 0.0, "x": T.px[j], "y": T.py[j]})
	walkers.clear()
	for w in T.haz.get("walk", []):
		var wd: Dictionary = w
		walkers.append({"j": float(wd["j"]), "lat": float(wd["lat"]), "latT": 0.0, "v": float(wd["v"]), "ph": float(wd["ph"]), "pause": float(wd["pause"]), "H": float(wd["H"]), "along": 0.0, "x": 0.0, "y": 0.0, "face": 0.0, "hit_t": 0.0})
	train = {}
	var tr = T.haz.get("train")
	if typeof(tr) == TYPE_DICTIONARY:
		var td: Dictionary = tr
		var cars: Array = []
		for c in td["cars"]:
			cars.append({"off": float(c["off"]), "L": float(c["L"]), "t": 9e9})
		train = {"px": float(td["p"]["x"]), "py": float(td["p"]["y"]), "ux": float(td["ux"]), "uy": float(td["uy"]), "span": float(td["span"]), "len": float(td["len"]), "v": float(td["v"]),
			"cars": cars, "state": "wait", "wait": 2.0 + rng.randf() * 2.0, "pos": -float(td["span"]) - float(td["len"]), "dir": 1.0}
	haz_pose()


## web updateHazards + the rollers in update0: traffic cruising the road, rolling meatballs, walkers, the train
func _hazards_tick(dt: float) -> void:
	var racing := state == "race" or state == "menu"
	var seg_l := T.L / T.N
	for c in traffic:
		if racing:
			c["s"] = float(c["s"]) + float(c["v"]) * dt / seg_l
		c["laneT"] = float(c["laneT"]) - dt
		if float(c["laneT"]) <= 0.0:
			c["laneT"] = 4.0 + rng.randf() * 5.0
			c["latT"] = [-34.0, -12.0, 12.0, 34.0][rng.randi_range(0, 3)]
		c["lat"] = float(c["lat"]) + (float(c["latT"]) - float(c["lat"])) * minf(1.0, dt * 0.6)
	for w in walkers:
		if float(w["pause"]) > 0.0:
			w["pause"] = float(w["pause"]) - dt
		else:
			if absf(float(w["lat"]) - float(w["latT"])) < 2.0:
				w["latT"] = (rng.randf() * 2.0 - 1.0) * (T.RW + 8.0)
				w["pause"] = 0.4 + rng.randf() * 1.8
			else:
				w["lat"] = float(w["lat"]) + signf(float(w["latT"]) - float(w["lat"])) * float(w["v"]) * dt
		if float(w["hit_t"]) > 0.0:
			w["hit_t"] = float(w["hit_t"]) - dt
	if not train.is_empty():
		if train["state"] == "wait":
			train["wait"] = float(train["wait"]) - dt
			if float(train["wait"]) <= 0.0:
				train["state"] = "run"
				train["dir"] = 1.0 if rng.randf() < 0.5 else -1.0
				train["pos"] = -float(train["span"]) - float(train["len"])
		else:
			train["pos"] = float(train["pos"]) + float(train["v"]) * dt
			if float(train["pos"]) > float(train["span"]) + 10.0:
				train["state"] = "wait"
				train["wait"] = 4.0 + rng.randf() * 5.0
	haz_pose()
	_haz_hits()


## where every hazard is now (also run by online guests between the host's pictures)
func haz_pose() -> void:
	for r in rollers:
		var j: int = r["j"]
		var lat := sin(sim_time * 1.05 + float(r["ph"])) * (T.RW + 6.0)
		r["lat"] = lat
		r["x"] = T.px[j] + T.nx[j] * lat
		r["y"] = T.py[j] + T.ny[j] * lat
	for c in traffic:
		var P := T.track_at(float(c["s"]), float(c["lat"]))
		c["x"] = P.x
		c["y"] = P.y
		c["ang"] = T.ang_at(float(c["s"]))
		c["i"] = int(P.z)
		c["hide"] = T.seg_bad(int(P.z))
	for w in walkers:
		w["along"] = sin(sim_time * 0.3 + float(w["ph"])) * 3.0
		var P2 := T.track_at(float(w["j"]) + float(w["along"]), float(w["lat"]))
		w["x"] = P2.x
		w["y"] = P2.y
		var pa := T.ang_at(float(w["j"]) + float(w["along"]))
		w["face"] = pa + (sin(sim_time + float(w["ph"])) * 0.6 if float(w["pause"]) > 0.0 else signf(float(w["latT"]) - float(w["lat"])) * PI / 2.0)
	if not train.is_empty():
		for c in train["cars"]:
			c["t"] = (float(train["pos"]) + float(train["len"]) - float(c["off"])) * float(train["dir"]) if train["state"] == "run" else 9e9


## guests: keep the hazards moving between the host's pictures
func haz_guest_step(dt: float) -> void:
	sim_time += dt
	var seg_l := T.L / T.N
	for c in traffic:
		c["s"] = float(c["s"]) + float(c["v"]) * dt / seg_l
		c["lat"] = float(c["lat"]) + (float(c["latT"]) - float(c["lat"])) * minf(1.0, dt * 0.6)
	if not train.is_empty() and train["state"] == "run":
		train["pos"] = float(train["pos"]) + float(train["v"]) * dt
	haz_pose()


func _haz_hits() -> void:
	for r in rollers:
		for k in karts:
			if k.loop.is_empty() and k.z < 14.0 and (k.x - float(r["x"])) ** 2 + (k.y - float(r["y"])) ** 2 < 306.0:
				spin_out(k, "meat", true)
	for c in traffic:
		if c["hide"]:
			continue
		var fx_ := cos(float(c["ang"]))
		var fy := sin(float(c["ang"]))
		var hl := float(c["len"]) * 0.55
		for k in karts:
			if not k.loop.is_empty() or k.z > 12.0:
				continue
			for o in [-hl, 0.0, hl]:
				if _hz_bump(k, float(c["x"]) + fx_ * o, float(c["y"]) + fy * o, 15.0, ""):
					break
	if not train.is_empty() and train["state"] == "run":
		var ux: float = train["ux"]
		var uy: float = train["uy"]
		for c in train["cars"]:
			var t: float = c["t"]
			var x: float = float(train["px"]) + ux * t
			var y: float = float(train["py"]) + uy * t
			for k in karts:
				if not k.loop.is_empty() or k.z > 18.0:
					continue
				var dx := k.x - x
				var dy := k.y - y
				var u := dx * ux + dy * uy
				var v := dy * ux - dx * uy
				if absf(u) < float(c["L"]) / 2.0 + 6.0 and absf(v) < 12.0:
					var sg := signf(v) if v != 0.0 else 1.0
					k.x += -uy * sg * (14.0 - absf(v))
					k.y += ux * sg * (14.0 - absf(v))
					spin_out(k, "wheel", true)
	for w in walkers:
		for k in karts:
			if not k.loop.is_empty() or k.z > float(w["H"]) * 0.8:
				continue
			if (k.x - float(w["x"])) ** 2 + (k.y - float(w["y"])) ** 2 < 225.0 and k.inv <= 0.0:
				spin_out(k, "meat", true)
				w["pause"] = 1.2
				w["hit_t"] = 0.6


## the hazards' state for an online picture, and back
func haz_snap() -> Array:
	var tr: Array = []
	for c in traffic:
		tr.append_array([c["s"], c["lat"], c["latT"]])
	var wk: Array = []
	for w in walkers:
		wk.append_array([w["lat"], w["latT"], w["pause"], w["hit_t"]])
	var tn: Array = []
	if not train.is_empty():
		tn = [1 if train["state"] == "run" else 0, train["pos"], train["dir"]]
	return [sim_time, tr, wk, tn]


func haz_unsnap(a: Array) -> void:
	sim_time = a[0]
	var tr: Array = a[1]
	for i in mini(traffic.size(), tr.size() / 3):
		traffic[i]["s"] = tr[i * 3]
		traffic[i]["lat"] = tr[i * 3 + 1]
		traffic[i]["latT"] = tr[i * 3 + 2]
	var wk: Array = a[2]
	for i in mini(walkers.size(), wk.size() / 4):
		walkers[i]["lat"] = wk[i * 4]
		walkers[i]["latT"] = wk[i * 4 + 1]
		walkers[i]["pause"] = wk[i * 4 + 2]
		walkers[i]["hit_t"] = wk[i * 4 + 3]
	var tn: Array = a[3]
	if not train.is_empty() and tn.size() == 3:
		train["state"] = "run" if int(tn[0]) == 1 else "wait"
		train["pos"] = tn[1]
		train["dir"] = tn[2]
	haz_pose()


## web hzBump: pushed out of a hazard; slowed (or spun out, with a kind)
func _hz_bump(k: Kart, x: float, y: float, r: float, kind: String) -> bool:
	var dx := k.x - x
	var dy := k.y - y
	var d := sqrt(dx * dx + dy * dy)
	if d == 0.0:
		d = 1.0
	if d >= r:
		return false
	var ov := r - d
	k.x += dx / d * ov
	k.y += dy / d * ov
	if kind != "":
		spin_out(k, kind, true)
		return true
	if k.inv > 0.0:
		return true
	k.speed *= 0.55
	k.inv = 0.35
	fx.append({"t": "hzbump", "k": k})
	return true


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
	k.sf = float((info.get("meta", {}) as Dictionary).get("sf", 1.0))
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
	_hazards_tick(dt)
	_ability_tick(dt)
	_items_tick(dt)
	for k in karts:
		if k.elim:
			continue
		var inp: Dictionary
		if k.web and k.remote and not bool(k.ai.get("auto", false)):
			# a browser friend's kart: each of their numbered controls played exactly once, in order (none, or a few
			# to catch up), so it drives the same path it drove on their screen (web netSteps)
			for e in k.web_q:
				var wi := {"steer": float(e[0]), "brake": bool(e[1]), "nb": bool(e[2]), "mul": float(e[3]), "use": false, "back": false, "hold": false, "hold_sl": 1, "release": null}
				var ev := String(e[4])
				if ev != "" and k.spin <= 0.0:
					var bk := ev.ends_with("B")
					if bk:
						ev = ev.substr(0, ev.length() - 1)
					item_intent(k, ev, wi)
					if bk and bool(wi["use"]):
						wi["back"] = true
				if int(e[5]) != 0 and state == "race":
					use_ability(k, int(e[5]) == 2)
				if k.rush > 0.0:
					wi["use"] = false
				k.step(wi, dt)
			k.web_q.clear()
			continue
		if k.remote and not bool(k.ai.get("auto", false)) and not (k.rush > 0.0):
			# a friend's kart: their latest controls, and any item presses they sent
			inp = {"steer": float(k.net_inp["steer"]), "brake": bool(k.net_inp["brake"]), "nb": bool(k.net_inp["nb"]), "mul": float(k.net_inp["mul"]), "use": false, "back": false, "hold": false, "hold_sl": 1, "release": null}
			if not k.net_items.is_empty():
				item_intent(k, k.net_items.pop_front(), inp)
				if bool(inp.get("ability", false)):
					use_ability(k, bool(k.net_inp["look"]))
				if bool(inp["use"]) and k.item != "" and bool(k.net_inp["look"]) and not k.item in NOBACK:
					inp["back"] = true
		elif k.is_player and not bool(k.ai.get("auto", false)) and not (k.rush > 0.0 and not (k.mega_t > 0.0) and not (k.pesto_t > 0.0)):
			inp = player_inp
			if bool(player_inp.get("ability", false)):
				use_ability(k, bool(player_inp.get("look", false)))
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
			var mg := (a.mega_t > 0.0) != (b.mega_t > 0.0)
			if d2 < (784.0 if mg else 361.0) and d2 > 0.0 and a.loop.is_empty() and b.loop.is_empty():
				var sa2 := a.shield > 0.0 or (a.rush > 0.0 and not (a.pesto_t > 0.0))
				var sb2 := b.shield > 0.0 or (b.rush > 0.0 and not (b.pesto_t > 0.0))
				if mg:
					var am := a.mega_t > 0.0
					if _mega_crush(a if am else b, b if am else a):
						continue
					if d2 >= 361.0:
						continue
				elif sa2 and not sb2:
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

	if mode == "lss":
		if state == "race":
			_lss_tick()
		return
	for k in karts:
		if state == "race" and not k.finished and k.prog >= T.LAPS * T.N:
			k.finished = true
			k.finish_time = race_time
			finish_count += 1
			k.place = finish_count
			fx.append({"t": "finish", "k": k})


## Last Slice Standing: each time the leader starts a new lap, whoever is last is out; the last kart racing wins (web lssTick)
func _lss_tick() -> void:
	var act: Array[Kart] = []
	for k in karts:
		if not k.finished:
			act.append(k)
	if act.size() <= 1:
		return
	var lead: Kart = act[0]
	for k in act:
		if k.prog > lead.prog:
			lead = k
	if lead.prog >= T.LAPS * T.N:
		# the winner: everyone left is placed by how far they got
		var rest: Array[Kart] = []
		for k in act:
			if k != lead:
				rest.append(k)
		rest.sort_custom(func(a, b): return a.prog < b.prog)
		for i in rest.size():
			_lss_elim(rest[i], rest.size() - i + 1, false)
		lead.finished = true
		lead.finish_time = race_time
		lead.place = 1
		lss_done = true
		fx.append({"t": "lss_win", "k": lead})
		return
	var lap := int(floor(float(lead.prog) / T.N))
	if lap > lss_lap and lap < T.LAPS:
		lss_lap = lap
		var last: Kart = act[0]
		for k in act:
			if k.prog < last.prog:
				last = k
		_lss_elim(last, act.size(), true)


func _lss_elim(k: Kart, place: int, loud: bool) -> void:
	if k.finished:
		return
	k.finished = true
	k.elim = true
	k.elim_lap = mini(T.LAPS, int(floor(maxf(0.0, float(k.prog)) / T.N)) + 1)
	k.finish_time = race_time
	k.place = place
	k.speed = 0.0
	k.ai["auto"] = true
	k.item = ""
	k.item2 = ""
	k.ab_q = []
	# out of the race: parked far off the pizza
	k.x = 50000.0 + place * 300.0
	k.y = 50000.0
	k._save_prev()
	fx.append({"t": "elim", "k": k, "place": place, "loud": loud})


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
	for c in traffic:
		if c["hide"]:
			continue
		var dj2: int = int(c["i"]) - k.idx
		if dj2 < 0:
			dj2 += T.N
		if dj2 > 1 and dj2 < 24 and absf(float(ai["lane"]) - float(c["lat"])) < 28.0:
			ai["lane_target"] = clampf(float(c["lat"]) - 32.0 if float(c["lat"]) > 0.0 else float(c["lat"]) + 32.0, -44.0, 44.0)
			ai["lane_t"] = maxf(float(ai["lane_t"]), 1.0)
			avoid = true
	for w in walkers:
		var dj3: int = int(w["j"]) - k.idx
		if dj3 < 0:
			dj3 += T.N
		if dj3 > 1 and dj3 < 14 and absf(float(ai["lane"]) - float(w["lat"])) < 20.0 and rng.randf() < 0.6:
			ai["lane_target"] = clampf(float(w["lat"]) - 26.0 if float(w["lat"]) > 0.0 else float(w["lat"]) + 26.0, -44.0, 44.0)
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
	if k.sc >= 0:
		var c: Dictionary = T.shorts[k.sc]
		var qi := mini(int(c["n"]) - 1, k.sc_i + 4)
		des = atan2(float(c["y"][qi]) - k.y, float(c["x"][qi]) - k.x)
	else:
		for ci in T.shorts.size():
			var c2: Dictionary = T.shorts[ci]
			var dj := k.idx - int(c2["a"])
			if dj > T.N / 2:
				dj -= T.N
			if dj < -T.N / 2:
				dj += T.N
			if dj > -62 and dj < -48 and int(ai.get("sc_seen", -1)) != ci:
				ai["sc_seen"] = ci
				var pk := 0.5 if bool(c2["route"]) else float({"easy": 0.25, "normal": 0.5, "hard": 0.8}.get(String(diff.get("key", "normal")), 0.5))
				ai["sc_pick"] = ci if rng.randf() < pk else -1
			if int(ai.get("sc_pick", -1)) == ci:
				if dj > -16 and dj < 6:
					des = atan2(float(c2["y"][2]) - k.y, float(c2["x"][2]) - k.x)
				elif dj >= -40 and dj <= -16:
					ai["lane"] = float(ai["lane"]) + (int(c2["s"]) * 48.0 - float(ai["lane"])) * minf(1.0, dt * 2.0)
				elif dj >= 6:
					ai["sc_pick"] = -1
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


# ---------------------------------------------------------------- the TESTING cheat's driver (web TD)

const STEP := 1.0 / 120.0
var td_sc := -1          # the shortcut the bar is asking about
var td_ch := {}          # shortcut -> true (take it) / false (ignore it); asked again each lap
var td_lane = null


## the next shortcut ahead and how many points away (web tdNext)
func td_next(k: Kart) -> Array:
	var best := -1
	var bd := 1 << 30
	for ci in T.shorts.size():
		var dj := int(T.shorts[ci]["a"]) - k.idx
		if dj < -6:
			dj += T.N
		if dj > T.N - 6:
			dj -= T.N
		if dj < -6:
			continue
		if dj < bd:
			bd = dj
			best = ci
	return [best, bd] if best >= 0 else []


## what's ahead to steer round, as [lateral, radius] (web tdObst): traps, meatballs, walkers, traffic, flying items
func td_obst(k: Kart) -> Array:
	var L: Array = []
	var j := k.idx
	var ca := cos(k.ma)
	var sa := sin(k.ma)
	var add := func(x: float, y: float, r: float) -> void:
		var f := (x - k.x) * ca + (y - k.y) * sa
		if f > -6.0 and f < 230.0:
			L.append([(x - T.px[j]) * T.nx[j] + (y - T.py[j]) * T.ny[j], r])
	for h in hazards:
		if float(h["t"]) > 0.0 and not (h["owner"] == k and not bool(h["armed"])):
			add.call(float(h["x"]), float(h["y"]), 24.0)
	for r in rollers:
		var dj := int(r["j"]) - k.idx
		if dj > T.N / 2:
			dj -= T.N
		if dj < -T.N / 2:
			dj += T.N
		if dj > -5 and dj < 60:
			var tt := maxf(0.0, dj) * T.L / T.N / maxf(60.0, k.speed)
			L.append([sin((sim_time + tt) * 1.05 + float(r["ph"])) * (T.RW + 6.0), 32.0])
	for w in walkers:
		var dj2 := int(w["j"]) - k.idx
		if dj2 > T.N / 2:
			dj2 -= T.N
		if dj2 < -T.N / 2:
			dj2 += T.N
		if dj2 > -4 and dj2 < 45:
			L.append([float(w["lat"]), 24.0])
			L.append([float(w["latT"]), 24.0])
			L.append([(float(w["lat"]) + float(w["latT"])) / 2.0, 24.0])
	for c in traffic:
		if c["hide"]:
			continue
		var dj3 := int(c["i"]) - k.idx
		if dj3 > T.N / 2:
			dj3 -= T.N
		if dj3 < -T.N / 2:
			dj3 += T.N
		if dj3 > -8 and dj3 < 40:
			L.append([float(c["lat"]), 34.0])
	# flying items: where each one will be at its closest pass
	var kv := maxf(0.0, k.speed)
	var kx := ca * kv
	var ky := sa * kv
	for q in projectiles:
		if q["owner"] == k or float(q.get("t", 0.0)) <= 0.0 or q.get("dead", false):
			continue
		var x := float(q["x"])
		var y := float(q["y"])
		var vx := float(q.get("vx", 0.0))
		var vy := float(q.get("vy", 0.0))
		var rx := x - k.x
		var ry := y - k.y
		if rx * rx + ry * ry > 300.0 * 300.0:
			continue
		var wx := vx - kx
		var wy := vy - ky
		var w2 := wx * wx + wy * wy
		if w2 < 1.0:
			continue
		var t := -(rx * wx + ry * wy) / w2
		if t < 0.0 or t > 1.4:
			continue
		var cx := rx + wx * t
		var cy := ry + wy * t
		if cx * cx + cy * cy > 70.0 * 70.0:
			continue
		L.append([(x + vx * t - T.px[j]) * T.nx[j] + (y + vy * t - T.py[j]) * T.ny[j], 22.0])
	return L


## your kart drives itself (web tdDrive): the computer's racing line held steady, the nearest clear lane round
## anything ahead, and a shortcut taken only when you chose it in the bar. Items stay yours to use.
func td_drive(k: Kart, o: Dictionary) -> void:
	var ai := k.ai
	if ai.is_empty():
		return
	if k.sc < 0:
		var nx := td_next(k)
		if not nx.is_empty() and int(nx[1]) < 70:
			ai["sc_seen"] = int(nx[0])
			ai["sc_pick"] = int(nx[0]) if bool(td_ch.get(int(nx[0]), false)) else -1
	ai["lane_t"] = maxf(float(ai["lane_t"]), 0.5)
	ai["lane_target"] = float(ai["lane_target"]) * 0.985
	var L: Array = [] if k.sc >= 0 else td_obst(k)
	var dl = null
	if not L.is_empty():
		var best := 0.0
		var bc := 1e9
		var cur: float = td_lane if td_lane != null else float(ai["lane"])
		for ci in range(-13, 14):
			var c := ci * 4.0
			var cost := absf(c - cur) + absf(c) * 0.15
			for q in L:
				if absf(c - float(q[0])) < float(q[1]):
					cost += 1e4
			if cost < bc:
				bc = cost
				best = c
		if bc < 1e4:
			dl = best
	var b0 := k.boost
	var r := ai_input(k, STEP)
	k.boost = b0
	var steer := float(r["steer"])
	var busy := k.sc >= 0
	for Lp in T.loops:
		var d := (int(Lp["j"]) - k.idx + T.N) % T.N
		if d < 80 or d > T.N - 10:
			busy = true
	if not T.glide.is_empty() and (int(T.glide["rj"]) - k.idx + T.N) % T.N < 70:
		busy = true
	var pick := int(ai.get("sc_pick", -1))
	var pd := 0
	if pick >= 0:
		pd = k.idx - int(T.shorts[pick]["a"])
		if pd > T.N / 2:
			pd -= T.N
		if pd < -T.N / 2:
			pd += T.N
		if pd > -45 and pd < 8:
			busy = true
	var mul := minf(1.0, float(r.get("mul", 1.0)) / 0.97)
	var lane_steer := func(lane: float) -> float:
		var ti := (k.idx + 6 + int(floor(maxf(0.0, k.speed) / 45.0))) % T.N
		var des := atan2(T.py[ti] + T.ny[ti] * lane - k.y, T.px[ti] + T.nx[ti] * lane - k.x)
		return clampf(Kart.ang_diff(des, k.a) * 3.0, -1.0, 1.0)
	if pick >= 0 and k.sc < 0 and pd > -60 and pd < 8:
		# a shortcut you chose: move out to its side early, then aim straight into its mouth
		var sc: Dictionary = T.shorts[pick]
		if pd < (-20 if bool(sc["route"]) else -14):
			td_lane = float(ai["lane"]) if td_lane == null else float(td_lane)
			td_lane = float(td_lane) + (int(sc["s"]) * 58.0 - float(td_lane)) * minf(1.0, STEP * 3.5)
			ai["lane"] = td_lane
			steer = lane_steer.call(float(td_lane))
		else:
			var px: PackedFloat32Array = sc["x"]
			var py: PackedFloat32Array = sc["y"]
			var bi := 0
			var bd := 1e18
			for i in mini(16, px.size()):
				var dd := (px[i] - k.x) ** 2 + (py[i] - k.y) ** 2
				if dd < bd:
					bd = dd
					bi = i
			var qi := mini(px.size() - 1, bi + 4)
			steer = clampf(Kart.ang_diff(atan2(py[qi] - k.y, px[qi] - k.x), k.a) * 3.2, -1.0, 1.0)
			mul = minf(mul, 0.85)
	elif dl != null and not busy:
		td_lane = float(ai["lane"]) if td_lane == null else float(td_lane)
		td_lane = float(td_lane) + (float(dl) - float(td_lane)) * minf(1.0, STEP * 6.0)
		ai["lane"] = td_lane
		ai["lane_target"] = dl
		steer = lane_steer.call(float(td_lane))
	else:
		td_lane = null
	o["steer"] = roundf(steer * 100.0) / 100.0
	o["brake"] = false
	o["nb"] = false
	o["mul"] = mul


## the bar's state each frame (web tdTick): which shortcut, how many seconds away, your choice; once a shortcut is
## behind you it's asked again next lap
func td_tick(k: Kart) -> Dictionary:
	var out := {"show": false}
	if k.sc < 0:
		var nx := td_next(k)
		if not nx.is_empty():
			var sec := int(nx[1]) * T.L / T.N / maxf(120.0, k.speed)
			if int(nx[1]) > 2 and (sec <= 10.5 or (td_sc == int(nx[0]) and int(nx[1]) < 600)):
				td_sc = int(nx[0])
				var has := td_ch.has(td_sc)
				out = {"show": true, "sec": maxi(0, ceili(sec)), "take": has and bool(td_ch[td_sc]), "skip": has and not bool(td_ch[td_sc])}
	for sc in td_ch.keys():
		var dj := k.idx - int(T.shorts[int(sc)]["b"])
		if dj < 0:
			dj += T.N
		if dj > 20 and dj < 140 and k.sc < 0:
			td_ch.erase(sc)
			if td_sc == int(sc):
				td_sc = -1
	return out


func td_pick(take: bool) -> void:
	if td_sc >= 0:
		td_ch[td_sc] = take


# ---------------------------------------------------------------- items

## web itemIntent: what a press on an item button means right now ("fwd", "fwd2", "hold", "hold2")
func item_intent(k: Kart, it: String, o: Dictionary) -> void:
	if it == "ability":
		o["ability"] = true
		return
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
		if k == "garlic2" and items_off.has("garlic"):
			continue
		if items_off.has(k):
			continue
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


## three pepperoni slices in a fan (the Trio item, and each Pepperoni Storm volley)
func _fire_trio(k: Kart, back: bool) -> void:
	for off in [-0.17, 0.0, 0.17]:
		var an: float = k.a + off + (PI if back else 0.0)
		var v4 := 240.0 if back else 300.0 + maxf(0.0, k.speed)
		_proj(k, "pep", k.x + cos(an) * 12.0, k.y + sin(an) * 12.0, cos(an) * v4, sin(an) * v4, 4.0, 0.35)


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
	if it == "garlic" or it == "garlic2":
		k.item = k.item2
		k.item2 = ""
		add_shield(k, 2 if it == "garlic2" else 1)
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
		_fire_trio(k, back)
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
	elif it == "freezer":
		# every racer ahead is frozen in a block of ice for a moment
		var sf2 := standings()
		var fi := sf2.find(k)
		for j in fi:
			var o2: Kart = sf2[j]
			if o2 == k or o2.finished or o2.inv > 0.0 or o2.shield > 0.0 or o2.rush > 0.0 or not o2.loop.is_empty() or o2.abs_t > 0.0 or ab_inv(o2) or o2.ghost_t > 0.0:
				continue
			if _absorb(o2):
				continue
			o2.frozen = 2.8
			o2.inv = maxf(o2.inv, 2.8 + 3.0)
			fx.append({"t": "frozen", "k": o2})
	else:
		_use_item2(k, it, back)


## the web's newer items (useItem2)
func _use_item2(k: Kart, it: String, back: bool) -> void:
	var ca := cos(k.a)
	var sa := sin(k.a)
	var i := stand.find(k)
	if it == "jalapeno":
		# three quick boosts, one per tap
		k.boost = maxf(k.boost, 1.05)
		k.jal_n = (k.jal_n if k.jal_n > 0 else 3) - 1
		if k.jal_n > 0:
			k.item2 = k.item
			k.item = "jalapeno"
		else:
			k.jal_n = 0
	elif it == "meatball":
		var dr := -1.0 if back else 1.0
		var sp := 160.0 if back else 230.0 + maxf(0.0, k.speed) * 0.55
		var p := _proj(k, "meat2", k.x + ca * 12.0 * dr, k.y + sa * 12.0 * dr, ca * sp * dr, sa * sp * dr, 7.0, 0.4)
		p["hits"] = 0
	elif it == "torpedo":
		var sp2 := 360.0 + maxf(0.0, k.speed)
		var p2 := _proj(k, "torp", k.x + ca * 12.0, k.y + sa * 12.0, ca * sp2, sa * sp2, 8.0, 0.3)
		p2["target"] = stand[i - 1] if i > 0 else null
	elif it == "shroom":
		# a huge springy jump with a burst of speed
		k.air = true
		k.big = true
		k.air_t = 0.0
		k.wvy = 78.0
		k.boost = maxf(k.boost, 0.9)
		k.drift = 0
	elif it == "magnet":
		k.mag_t = 2.6
		k.mag_tg = stand[i - 1] if i > 0 else null
	elif it == "cutter":
		k.cut_t = 8.0
		k.cut_a = 0.0
	elif it == "sauce":
		for j in i:
			var o: Kart = stand[j]
			if o.inv > 0.0 or o.shield > 0.0 or o.ghost_t > 0.0 or not o.loop.is_empty() or o.abs_t > 0.0 or ab_inv(o):
				continue
			if _absorb(o):
				continue
			o.sauce_t = 4.0
			o.inv = maxf(o.inv, 3.0)
			fx.append({"t": "sauced", "k": o})
	elif it == "heat":
		for o in karts:
			if o == k or not o.loop.is_empty() or o.inv > 0.0 or o.shield > 0.0 or o.ghost_t > 0.0 or o.abs_t > 0.0 or ab_inv(o):
				continue
			if _absorb(o):
				continue
			o.shrink_t = 3.2
			o.speed *= 0.6
			spin_out(o, "pep")
			o.inv = maxf(o.inv, 3.0)
		fx.append({"t": "heat", "k": k})
	elif it == "bomb":
		if back:
			var pb := _proj(k, "bomb", k.x - cos(k.ma) * 16.0, k.y - sin(k.ma) * 16.0, 0.0, 0.0, 1.6, 9.0)
			pb["fuse"] = 1.6
			pb["landed"] = true
		else:
			var sp3 := maxf(0.0, k.speed) + 160.0
			var pb2 := _proj(k, "bomb", k.x + ca * 8.0, k.y + sa * 8.0, ca * sp3, sa * sp3, 0.75 + 1.1, 9.0)
			pb2["t0"] = 0.75
			pb2["fuse"] = 1.1
			pb2["landed"] = false
	elif it == "forks" or it == "boxes":
		var j0 := ((k.idx % T.N) + T.N) % T.N
		var back_d := 22.0 if it == "forks" else 26.0
		for o3 in ([-22.0, 0.0, 22.0] if it == "forks" else [-30.0, 0.0, 30.0]):
			var hx := k.x - cos(k.ma) * back_d + T.nx[j0] * float(o3)
			var hy := k.y - sin(k.ma) * back_d + T.ny[j0] * float(o3)
			hazards.append({"id": _nid(), "x": hx, "y": hy, "t": 25.0 if it == "forks" else 22.0, "born": 0.0, "owner": k, "armed": false, "kind": it})
	elif it == "ghost":
		# fade out, and take the leader's item
		k.ghost_t = 4.5
		var ld: Kart = stand[0] if stand.size() > 0 else null
		if ld != null and ld != k and ld.item != "" and not _absorb(ld):
			var got := ld.item
			ld.item = ld.item2
			ld.item2 = ""
			if k.item == "":
				k.item = got
			elif k.item2 == "" and k.held.is_empty():
				k.item2 = got
			fx.append({"t": "robbed", "k": ld, "by": k})
	elif it == "cannon":
		k.cannon_t = 4.2
		k.rush = 4.2
		k.auto_t = 4.2
		k.boost = maxf(k.boost, 4.2)
		k.drift = 0
	elif it == "twister":
		var pt := _proj(k, "twist", k.x + ca * 16.0, k.y + sa * 16.0, 0.0, 0.0, 9.0, 0.6)
		pt["prog"] = float(k.prog + 3)
		pt["lat"] = T.lateral(k.idx, k.x, k.y)
		pt["ph"] = rng.randf() * 6.0
	elif it == "swap":
		var o4: Kart = stand[i - 1] if i > 0 else null
		if o4 != null and o4.loop.is_empty() and k.loop.is_empty() and not o4.finished and o4.prog - k.prog < int(T.N * 0.35) and not _absorb(o4):
			# only the places swap: each keeps its own speed and its heading along the road
			var ta := func(q: Kart) -> float: return T.ang[((q.idx % T.N) + T.N) % T.N]
			var rk := [Kart.ang_diff(k.a, ta.call(k)), Kart.ang_diff(k.ma, ta.call(k))]
			var ro := [Kart.ang_diff(o4.a, ta.call(o4)), Kart.ang_diff(o4.ma, ta.call(o4))]
			for f in ["x", "y", "idx", "prog", "wy", "last_g"]:
				var tmp = k.get(f)
				k.set(f, o4.get(f))
				o4.set(f, tmp)
			var a0 := float(ta.call(k))
			k.a = a0 + float(rk[0])
			k.ma = a0 + float(rk[1])
			var a1 := float(ta.call(o4))
			o4.a = a1 + float(ro[0])
			o4.ma = a1 + float(ro[1])
			k._save_prev()
			o4._save_prev()
			k.inv = maxf(k.inv, 1.0)
			fx.append({"t": "swap", "k": k, "by": o4})


## the class's top speed (web BASE_MAX)
func k_base_max() -> float:
	return 170.5 * T.class_mul


## the newer items that keep running on a kart: the magnet's pull, the orbiting cutters, the timers (web itemsTick)
func _items_tick(dt: float) -> void:
	for k in karts:
		if k.mag_t > 0.0:
			k.mag_t -= dt
			var tg := k.mag_tg
			if tg != null and not tg.finished:
				var dx := tg.x - k.x
				var dy := tg.y - k.y
				var dd := maxf(0.001, sqrt(dx * dx + dy * dy))
				if dd < 26.0:
					k.mag_t = 0.0
				else:
					k.boost = maxf(k.boost, 0.12)
					k.ma += clampf(Kart.ang_diff(atan2(dy, dx), k.ma), -1.4 * dt, 1.4 * dt)
					k.speed = maxf(k.speed, minf(k.base_max * 1.75, absf(tg.speed) + 130.0))
			else:
				k.mag_t = 0.0
		if k.cut_t > 0.0:
			k.cut_t -= dt
			k.cut_a += dt * 5.5
			for b in 3:
				var an := k.cut_a + b * 2.094
				var bx := k.x + cos(an) * 15.0
				var by := k.y + sin(an) * 15.0
				for o in karts:
					if o == k or not o.loop.is_empty():
						continue
					if (o.x - bx) ** 2 + (o.y - by) ** 2 < 144.0 and o.inv <= 0.0:
						spin_out(o, "wheel")
				for p in projectiles:
					if p["owner"] != k and not bool(p.get("sure", false)) and (float(p["x"]) - bx) ** 2 + (float(p["y"]) - by) ** 2 < 121.0:
						p["t"] = 0.0
						p["dead"] = true
						fx.append({"t": "cutblock", "x": bx, "y": by})
		if k.ghost_t > 0.0:
			k.ghost_t -= dt
		if k.sauce_t > 0.0:
			k.sauce_t -= dt
		if k.shrink_t > 0.0:
			k.shrink_t -= dt
		if k.cannon_t > 0.0:
			k.cannon_t -= dt


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


## where a held item trails: right behind the kart (the web draws it there and checks hits there)
func held_pos(k: Kart) -> Vector2:
	var L := 11.0 * k.sf * T.KS * 0.62 + 4.0
	return Vector2(k.x - cos(k.ma) * L, k.y - sin(k.ma) * L)


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
		k.mz_h = 0
	else:
		if k.inv > 0.0 or k.rush > 0.0 or ab_inv(k) or k.abs_t > 0.0 or k.ghost_t > 0.0:
			return false
		if not world and (k.air or k.glide or not k.loop.is_empty()):
			return false
	if k.shield > 0.0:
		if k.mz_h > 0:
			k.mz_h -= 1
			k.abs_t = 0.6
			fx.append({"t": "melt", "k": k})
			if k.mz_h <= 0:
				k.shield = 0.0
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


## an ability that makes its driver untouchable (web abInv)
static func ab_inv(k: Kart) -> bool:
	return k.pesto_t > 0.0 or k.chili_t > 0.0 or k.mega_t > 0.0 or k.olive_t > 0.0


static func abil_key(k: Kart) -> String:
	return k.racer_name.to_lower()


## web useAbility
func use_ability(k: Kart, back: bool) -> void:
	var id := abil_key(k)
	if not ABIL.has(id) or k.ab_c < 1.0 or not k.loop.is_empty() or k.finished:
		return
	k.ab_c = 0.0
	var col := Color(String(ABIL[id][2]))
	fx.append({"t": "ability", "k": k, "id": id})
	var st := stand
	var i := st.find(k)
	match id:
		"pep":
			var vol := func():
				var n0 := projectiles.size()
				_fire_trio(k, back)
				for q in range(n0, projectiles.size()):
					var P: Dictionary = projectiles[q]
					P["storm"] = true
					P["hp"] = 3
					P["t"] = 8.0
					P["ign"] = {}
			vol.call()
			k.ab_q = [[0.25, vol]]
		"basil":
			k.boost = maxf(k.boost, PESTO_T)
			k.rush = maxf(k.rush, PESTO_T)
			k.pesto_t = PESTO_T
			k.ab_fx = PESTO_T
			k.ab_col = col
		"olive":
			k.ab_q = []
			for n in 10:
				k.ab_q.append([n * 0.25, func():
					hazards.append({"id": _nid(), "x": k.x - cos(k.ma) * 22.0, "y": k.y - sin(k.ma) * 22.0, "t": 25.0, "born": 0.0, "owner": k, "armed": false, "olive": true})])
			k.olive_t = OLIVE_T
			k.ab_fx = OLIVE_T
			k.ab_col = col
		"mozz":
			k.shield = 7.0
			k.mz_h = 3
			k.boost = maxf(k.boost, 0.7)
			k.p_boost = 0.0
		"chili":
			k.boost = maxf(k.boost, 2.2)
			k.fire_t = 2.2
			k.chili_t = 2.2
			k.ab_fx = 2.2
			k.ab_col = col
		"shroom":
			k.mega_t = MEGA_T
			k.boost = maxf(k.boost, 0.55)
			k.speed = maxf(k.speed, minf(k.speed + 12.0, k.base_max * 1.15))
			k.p_boost = k.boost
			k.b_age = 9.0
			k.b_pk = k.boost
		"pineapple":
			blast(k.x, k.y, 260.0, k, "pep", true)
			k.inv = maxf(k.inv, 0.6)
		"anchovy":
			for j in range(1, 4):
				var ti := i + j if back else i - j
				var tg: Kart = st[ti] if ti >= 0 and ti < st.size() else null
				var sp := 360.0 + maxf(0.0, k.speed)
				var an := k.a + (PI if back else 0.0) + (j - 2) * 0.25
				var p := _proj(k, "torp", k.x + cos(an) * 12.0, k.y + sin(an) * 12.0, cos(an) * sp, sin(an) * sp, 600.0 if tg != null else 8.0, 0.3)
				p["target"] = tg
				p["sure"] = tg != null


func _nid() -> int:
	var v := next_id
	next_id += 1
	return v


## web blast(): everyone within r spins out (forced: through shields and boosts, and in the air)
func blast(x: float, y: float, r: float, owner: Kart, kind: String, force := false) -> void:
	for k in karts:
		if k == owner or not k.loop.is_empty():
			continue
		if (k.x - x) ** 2 + (k.y - y) ** 2 < r * r:
			var hit := spin_out(k, kind, force, force)
			if hit and k.air and k.loop.is_empty():
				k.big = true
				k.wvy = maxf(k.wvy, 55.0 * maxf(1.0, r / 130.0))
	fx.append({"t": "blast", "x": x, "y": y, "r": r, "col": String(ABIL["pineapple"][2]) if force else "#ff9a1f"})


## web abilityTick: charge up, run queued volleys and fire trails, count down, and let the computer drivers use theirs
func _ability_tick(dt: float) -> void:
	for k in karts:
		if state == "race" and not k.finished and k.ab_c < 1.0:
			k.ab_c = minf(1.0, k.ab_c + dt / ABIL_TIME)
			if k.ab_c >= 1.0:
				fx.append({"t": "ability_ready", "k": k})
		if not k.ab_q.is_empty():
			for q in k.ab_q:
				q[0] = float(q[0]) - dt
			while not k.ab_q.is_empty() and float(k.ab_q[0][0]) <= 0.0:
				(k.ab_q.pop_front()[1] as Callable).call()
		if k.fire_t > 0.0:
			k.fire_t -= dt
			k.fire_acc += dt
			if k.fire_acc > 0.12:
				k.fire_acc = 0.0
				hazards.append({"id": _nid(), "x": k.x - cos(k.ma) * 16.0, "y": k.y - sin(k.ma) * 16.0, "t": 2.2, "born": 0.0, "owner": k, "armed": false, "kind": "fire"})
		for f in ["mega_t", "flat_t", "flat_imm", "pesto_t", "chili_t", "olive_t", "ab_fx", "burn_t"]:
			if float(k.get(f)) > 0.0:
				k.set(f, float(k.get(f)) - dt)
		if not k.human and k.ab_c >= 1.0 and state == "race":
			k.ab_wait = (1.0 + rng.randf() * 4.0 if k.ab_wait < 0.0 else k.ab_wait) - dt
			if k.ab_wait <= 0.0:
				var id := abil_key(k)
				var i := stand.find(k)
				var go := true
				if id == "pineapple":
					go = false
					for o in karts:
						if o != k and (o.x - k.x) ** 2 + (o.y - k.y) ** 2 < 70.0 * 70.0:
							go = true
				elif id == "anchovy" or id == "pep":
					go = i > 0
				elif id == "olive":
					go = i < stand.size() - 1
				if go:
					use_ability(k, false)
					k.ab_wait = -1.0
				else:
					k.ab_wait = 0.8


## a Mega Shroom rolls over a normal kart: squashed flat for 3 s (web megaCrush). True when it rolled over.
func _mega_crush(a: Kart, b: Kart) -> bool:
	if b.flat_t > 0.0:
		return true
	if b.flat_imm > 0.0 or b.glide or not b.loop.is_empty():
		return false
	if b.inv > 0.0 or ab_inv(b) or b.abs_t > 0.0:
		return false
	if b.shield > 0.0:
		spin_out(b, "mega", true)
		return false
	b.flat_t = FLAT_T
	b.flat_imm = FLAT_T + 0.6
	b.inv = maxf(b.inv, FLAT_T + 3.0)
	b.air = false
	b.wvy = 0.0
	b.big = false
	b.speed *= 0.5
	b.drift = 0
	b.charge = 0.0
	b.boost = 0.0
	b.d_want = 0.0
	b.d_latch = false
	b.s_t = 0.0
	fx.append({"t": "flat", "k": b, "by": a})
	return true


func _oil_up(k: Kart) -> void:
	k.oil_t = 5.0
	k.inv = maxf(k.inv, 3.0)
	fx.append({"t": "oily", "k": k})


# ---------------------------------------------------------------- thrown items

## Pepperoni Storm slices ricochet off the road's edges: two bounces, the third wall smashes them (web pepWall)
func _pep_wall(p: Dictionary) -> void:
	if not p.has("rp"):
		var o: Kart = p["owner"]
		p["rp"] = float(o.prog) if o != null else 0.0
	_rail_sync(p)
	var j := posmod(int(round(float(p["rp"]))), T.N)
	var lt := float(p["rl"])
	var sg := 0
	var ov := 0.0
	if not is_nan(T.flo[j]):
		if lt < T.flo[j]:
			sg = -1
			ov = T.flo[j] - lt
		elif lt > T.fhi[j]:
			sg = 1
			ov = lt - T.fhi[j]
	else:
		var s0 := -1 if lt < 0.0 else 1
		var lim := T.RW + 3.0
		if lt * s0 > lim:
			sg = s0
			ov = lt * s0 - lim
	if sg == 0:
		return
	var nx := T.nx[j] * sg
	var ny := T.ny[j] * sg
	var dot := float(p["vx"]) * nx + float(p["vy"]) * ny
	if dot <= 0.0:
		return
	p["hp"] = int(p["hp"]) - 1
	if int(p["hp"]) <= 0:
		p["t"] = 0.0
		p["pop"] = true
		return
	p["vx"] = float(p["vx"]) - 2.0 * dot * nx
	p["vy"] = float(p["vy"]) - 2.0 * dot * ny
	p["x"] = float(p["x"]) - nx * ov
	p["y"] = float(p["y"]) - ny * ov
	p["rl"] = float(p["rl"]) - sg * ov
	fx.append({"t": "ricochet", "x": float(p["x"]), "y": float(p["y"])})


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
		if type == "twist":
			# a dough tornado that rolls down the track, weaving across it
			p["prog"] = float(p["prog"]) + dt * maxf(14.0, k_base_max() * 0.72 / (T.L / T.N))
			p["lat"] = sin(sim_time * 1.6 + float(p["ph"])) * (T.RW * 0.75)
			var tp := T.track_at(float(p["prog"]), float(p["lat"]))
			p["x"] = tp.x
			p["y"] = tp.y
			for k in karts:
				if not k.loop.is_empty() or (k == p["owner"] and float(p["safe"]) > 0.0):
					continue
				if (k.x - tp.x) ** 2 + (k.y - tp.y) ** 2 < 400.0 and k.inv <= 0.0:
					if spin_out(k, "flour") and k.air and k.loop.is_empty():
						k.big = true
						k.wvy = maxf(k.wvy, 65.0)
			if float(p["t"]) <= 0.0:
				projectiles.remove_at(i)
			i -= 1
			continue
		if type == "bomb":
			if not bool(p["landed"]):
				if float(p["t"]) <= float(p["fuse"]):
					p["landed"] = true
					p["vx"] = 0.0
					p["vy"] = 0.0
			else:
				p["vx"] = float(p["vx"]) * 0.9
				p["vy"] = float(p["vy"]) * 0.9
			if float(p["t"]) <= 0.0:
				blast(float(p["x"]), float(p["y"]), 48.0, null, "pep")
				projectiles.remove_at(i)
				i -= 1
				continue
		if type == "dough" and tg != null and not tg.finished:
			_home_step(p, tg, dt, maxf(300.0, absf(tg.speed) * 1.22 + 70.0), 9.0 if Vector2(tg.x - float(p["x"]), tg.y - float(p["y"])).length() < 70.0 else 5.5)
		elif type == "torp" and tg != null and not tg.finished and not bool(p.get("sure", false)):
			_home_step(p, tg, dt, maxf(380.0, absf(tg.speed) * 1.35 + 90.0), 7.0)
		elif type == "torp" and tg != null and not tg.finished:
			_home_step(p, tg, dt, maxf(380.0, absf(tg.speed) * 1.35 + 90.0), 7.0)
		elif type != "wheel":
			p["x"] = float(p["x"]) + float(p["vx"]) * dt
			p["y"] = float(p["y"]) + float(p["vy"]) * dt
			if p.get("storm", false):
				_pep_wall(p)
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
			if int(p["b"]) > (4 if type in ["meat2", "torp", "bomb"] else 3):
				p["t"] = 0.0
		if type == "bomb":
			i -= 1
			continue
		if type == "meat2":
			# the bowling meatball rolls on through up to three racers, slowing a little each time
			var gone := false
			for k in karts:
				if not k.loop.is_empty() or (k == p["owner"] and float(p["safe"]) > 0.0) or k.ghost_t > 0.0:
					continue
				if _held_block(k, p):
					gone = true
					break
				if (k.x - float(p["x"])) ** 2 + (k.y - float(p["y"])) ** 2 < 484.0 and k.inv <= 0.0:
					if spin_out(k, "meat"):
						fx.append({"t": "hit", "k": k, "type": "meat2", "x": float(p["x"]), "y": float(p["y"])})
					p["hits"] = int(p["hits"]) + 1
					if int(p["hits"]) >= 3:
						gone = true
						break
					var spm := Vector2(float(p["vx"]), float(p["vy"])).length()
					p["vx"] = float(p["vx"]) * 0.85
					p["vy"] = float(p["vy"]) * 0.85
					if spm < 60.0:
						gone = true
						break
			for h in hazards:
				if (float(h["x"]) - float(p["x"])) ** 2 + (float(h["y"]) - float(p["y"])) ** 2 < 484.0 * 0.6:
					h["t"] = 0.0
			if gone or float(p["t"]) <= 0.0:
				projectiles.remove_at(i)
			i -= 1
			continue
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
		if type == "torp" and bool(p.get("sure", false)):
			# an ability anchovy always reaches its target; it waits out any protection, a hop dodges it
			if tg == null or tg.finished:
				projectiles.remove_at(i)
				i -= 1
				continue
			if tg.loop.is_empty() and (tg.x - float(p["x"])) ** 2 + (tg.y - float(p["y"])) ** 2 < 256.0 and not (tg.inv > 0.0 or tg.rush > 0.0 or ab_inv(tg) or tg.abs_t > 0.0):
				if tg.air and not tg.glide:
					fx.append({"t": "dodge", "k": tg})
				elif spin_out(tg, "pep", true):
					tg.spin *= 0.6
					tg.inv = tg.spin + 3.0
					fx.append({"t": "hit", "k": tg, "type": "torp", "x": float(p["x"]), "y": float(p["y"])})
				projectiles.remove_at(i)
			i -= 1
			continue
		if p.get("storm", false):
			var ig: Dictionary = p["ign"]
			for k in karts:
				if not k.loop.is_empty() or k == p["owner"] or float(ig.get(k, -1.0)) > sim_time:
					continue
				if _held_block(k, p):
					ig[k] = sim_time + 0.5
					p["hp"] = int(p["hp"]) - 1
					if int(p["hp"]) <= 0:
						hit = true
						break
					continue
				if (k.x - float(p["x"])) ** 2 + (k.y - float(p["y"])) ** 2 < 200.0 and k.inv <= 0.0:
					ig[k] = sim_time + 0.6
					spin_out(k, "pep")
					fx.append({"t": "hit", "k": k, "type": "pep", "x": float(p["x"]), "y": float(p["y"])})
					var ddx := float(p["x"]) - k.x
					var ddy := float(p["y"]) - k.y
					var dd := maxf(0.001, sqrt(ddx * ddx + ddy * ddy))
					var dot2 := float(p["vx"]) * ddx / dd + float(p["vy"]) * ddy / dd
					if dot2 < 0.0:
						p["vx"] = float(p["vx"]) - 2.0 * dot2 * ddx / dd
						p["vy"] = float(p["vy"]) - 2.0 * dot2 * ddy / dd
					p["hp"] = int(p["hp"]) - 1
					if int(p["hp"]) <= 0:
						hit = true
						break
			for h in hazards:
				if (float(h["x"]) - float(p["x"])) ** 2 + (float(h["y"]) - float(p["y"])) ** 2 < 100.0:
					h["t"] = 0.0
					p["hp"] = int(p["hp"]) - 1
			if hit or float(p["t"]) <= 0.0 or int(p["hp"]) <= 0:
				projectiles.remove_at(i)
			i -= 1
			continue
		for k in karts:
			if not k.loop.is_empty() or (k == p["owner"] and (float(p["safe"]) > 0.0 or type == "pep")) or k.ghost_t > 0.0:
				continue
			if _held_block(k, p):
				hit = true
				break
			if (k.x - float(p["x"])) ** 2 + (k.y - float(p["y"])) ** 2 < (256.0 if type == "torp" else 200.0) and k.inv <= 0.0:
				spin_out(k, "pep" if type == "torp" else type)
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
				if h.get("olive", false):
					if k.air or k.glide or k.shield > 0.0 or k.rush > 0.0 or ab_inv(k) or k.oil_t > 4.5:
						continue
					_oil_up(k)
				elif String(h.get("kind", "")) == "fire":
					if spin_out(k, "fire"):
						k.burn_t = BURN_T
				else:
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
