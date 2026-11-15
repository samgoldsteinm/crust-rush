extends RefCounted
## Balloon Battle, ported from the web game's tools/mini/battle.js (the rules: the web's docs/BALLOON-BATTLE-PLAN.md).
## A mode with no lap: karts drive anywhere in an arena and hit each other with items; each hit pops one of the
## victim's balloons. The rules since the web's v197 (the owner: "you start with 5 then after those are popped you have
## 3 then after the 3 are popped you get 1 after that is popped you are eliminated"): three sets of balloons, 5 then 3
## then 1 (SETS); losing the last of a set takes the kart out for a moment and brings it back with the next set; losing
## the single balloon ELIMINATES it (hidden, parked far off, nobody's target). A point for every balloon of a rival's
## you pop (points are never halved). Going off the table costs a balloon the same way. The round ends when one driver
## is left, or when the clock (a backstop, 300 s) runs out. Final order: drivers still in first, by points, then sets
## and balloons left; then the eliminated, the last one out highest. Off line only.
##
## The switch is the map: TrackData.battle (web BATTLE = def.battle). A Race on such a map makes one of these
## (race.bb) and sets race.mode = "bb"; a normal race never reads anything here. The hooks that call in:
##   kart.gd   step(): no off-road slowing; walls(): the arena's shapes instead of the track's walls; ground()
##   race.gd   ai_input -> ai(); spin_out -> hit(); update -> tick(); roll_item -> roll(); thrown items -> proj_walls();
##             standings -> rank()
##   view.gd   balloons, the pops, a thrown thing's height     hud.gd   the one-line read-out
##   main.gd   banners, camera, watching once you are out (its spectating), "Skip to results" (skip_on, then _bb_fast)
##
## The arena is a height field made of a few shapes, in the karts' own coordinates (x east, z south: a kart's k.y is z):
##   box  x0,x1,z0,z1,h     ramp  x0,x1,z0,z1,h0,h1,ax (its top runs from h0 at the low x or z to h1)     cyl  x,z,r,h
## One rule gives every wall: nothing drives up a step higher than STEP. The shapes, the spawn places, the ramps and
## the numbers all come from the map's export (the "battle" block, tools/ciexport.py): nothing of the arena is typed in here.
## An export made before the web's v197 has no "sets", "X" or "Z" and its spawn places have no heading: the rules are
## the new ones all the same (SETS as below, the clock 300 s) and the table's size is read off its shapes.
## This file has no class name on purpose: it is loaded by its path (a fresh checkout has no class list yet).

var race                     # the Race this battle is in
var T: TrackData
var spawn: Array = []        # [[x, z, heading]] where karts are set down (an older export: [x, z])
var ramps: Array = []        # [{lo, hi, foot: [x, z], top: [x, z], x0, x1, z0, z1}]: for the record, only tests read it (web BB.ramps)
var items: Array = [["pepperoni", 3.0], ["trio", 2.0], ["meatball", 2.0], ["flour", 1.5], ["chili", 2.0]]   # web BB_ITEMS (the export's copy replaces it)
var cols: Array = ["#e3271d", "#1f6fd6", "#f6c41f", "#35a84a", "#ff7ab8", "#8a4fd6", "#ff8a1f", "#22b8c8"]   # web BB_COL
var TIME := 300.0            # web BB.T: the clock, a backstop (rounds end by elimination well before it)
var SETS: Array = [5, 3, 1]  # web BB_SETS: the sets of balloons, one after the other
var X := 550.0               # web BB_X, BB_Z: half the table's length (east-west) and width
var Z := 380.0
var STEP := 5.5              # web BB_STEP: the highest step a kart climbs
var R := 6.5                 # web BB_R: a kart's footprint
var X0 := -558.0             # web BB_X0: west of this there is only the kitchen floor
var FLOOR := -312.0          # web BB_FLOOR
var START := 5               # the most balloons a kart ever has (the first set): view.gd makes that many
var t := 0.0                 # the clock, counting down (web BB.t)
var over := false
var by_time := false         # ...and it ended on the clock, not with one driver left
var left := 0                # drivers still in (web BB.left)
var skip := false            # "Skip to results": the rest is being played out at once, silently (web BB.skip)
var ghost := 0.0             # the player has just gone out: this long until the kart is parked and the watching starts
var ghost_k: Kart = null
var jams := 0                # times a computer's driver was set down again for going nowhere (web BB.jams)
var out_order: Array = []    # the eliminated, first out first (for the tests)
var meat_off := false        # the bowling meatball switched off in Settings (it is given to everyone here, unlocked or not)

# the shapes, unpacked into columns so the ground test is quick (it runs about a hundred times a step)
var _n := 0
var _kind := PackedInt32Array()     # 0 box, 1 ramp along x, 2 ramp along z, 3 cylinder
var _x0 := PackedFloat64Array()
var _x1 := PackedFloat64Array()
var _z0 := PackedFloat64Array()
var _z1 := PackedFloat64Array()
var _h0 := PackedFloat64Array()
var _h1 := PackedFloat64Array()
var _cx := PackedFloat64Array()
var _cz := PackedFloat64Array()
var _r2 := PackedFloat64Array()
var _fx := PackedFloat64Array()     # the eight points of a kart's footprint (web bbTouch: i * .785398)
var _fz := PackedFloat64Array()
var tnx := 0.0                      # touch(): the way into the wall (web _bbN)
var tnz := 0.0


func setup(race_, track: TrackData) -> void:
	race = race_
	T = track
	var d: Dictionary = T.bb
	spawn = d.get("spawn", [])
	ramps = d.get("ramps", [])
	if d.get("items") is Array and not (d["items"] as Array).is_empty():
		items = d["items"]
	if d.get("col") is Array and not (d["col"] as Array).is_empty():
		cols = d["col"]
	STEP = float(d.get("step", STEP))
	R = float(d.get("r", R))
	X0 = float(d.get("x0", X0))
	FLOOR = float(d.get("floor", FLOOR))
	if d.get("sets") is Array and not (d["sets"] as Array).is_empty():
		SETS = []
		for n0 in d["sets"]:
			SETS.append(int(n0))
		TIME = float(d.get("T", TIME))
	# (an export from before the sets: its "T", "start" and "back" are the old rules' numbers and are not read)
	START = 0
	for n in SETS:
		START = maxi(START, int(n))
	# the table's half length and width: as exported, else read off the shapes (the open west edge is X0 = -X - 8; the
	# wall along the south side starts at z = Z)
	X = float(d["X"]) if d.has("X") else -X0 - 8.0
	if d.has("Z"):
		Z = float(d["Z"])
	else:
		for s0 in d.get("shapes", []):
			if String((s0 as Dictionary).get("k", "")) == "wall" and float((s0 as Dictionary).get("z0", 0.0)) > 0.0 and float(s0["x1"]) - float(s0["x0"]) > X:
				Z = float(s0["z0"])
	for s in d.get("shapes", []):
		var sd: Dictionary = s
		var k := String(sd.get("t", "box"))
		if k == "cyl":
			var r := float(sd["r"])
			_kind.append(3)
			_x0.append(float(sd["x"]) - r)
			_x1.append(float(sd["x"]) + r)
			_z0.append(float(sd["z"]) - r)
			_z1.append(float(sd["z"]) + r)
			_h0.append(float(sd["h"]))
			_h1.append(float(sd["h"]))
			_cx.append(float(sd["x"]))
			_cz.append(float(sd["z"]))
			_r2.append(r * r)
		else:
			var ramp := k == "ramp"
			_kind.append((1 if String(sd.get("ax", "x")) == "x" else 2) if ramp else 0)
			_x0.append(float(sd["x0"]))
			_x1.append(float(sd["x1"]))
			_z0.append(float(sd["z0"]))
			_z1.append(float(sd["z1"]))
			_h0.append(float(sd["h0"]) if ramp else float(sd["h"]))
			_h1.append(float(sd["h1"]) if ramp else float(sd["h"]))
			_cx.append(0.0)
			_cz.append(0.0)
			_r2.append(0.0)
	_n = _kind.size()
	for i in 8:
		_fx.append(cos(i * 0.785398))
		_fz.append(sin(i * 0.785398))


# ---------------------------------------------------------------- the arena: ground and walls

## the height of the arena at a spot: the table top (0), whatever stands there, or the kitchen floor past the open edge (web battleG)
func ground(x: float, z: float) -> float:
	if x < X0:
		return FLOOR
	var h := 0.0
	for i in _n:
		if x < _x0[i] or x > _x1[i] or z < _z0[i] or z > _z1[i]:
			continue
		var kd := _kind[i]
		var v := _h0[i]
		if kd == 1:
			v += (_h1[i] - v) * (x - _x0[i]) / (_x1[i] - _x0[i])
		elif kd == 2:
			v += (_h1[i] - v) * (z - _z0[i]) / (_z1[i] - _z0[i])
		elif kd == 3:
			var dx := x - _cx[i]
			var dz := z - _cz[i]
			if dx * dx + dz * dz > _r2[i]:
				continue
		if v > h:
			h = v
	return h


## is a kart's footprint (eight points round it) against something too high to climb from the height it is at?
## 0 no; 1 yes, and (tnx, tnz) is the way in; 2 walled in on every side (web bbTouch)
func touch(x: float, z: float, wy: float) -> int:
	var nx := 0.0
	var nz := 0.0
	var n := 0
	for i in 8:
		if ground(x + _fx[i] * R, z + _fz[i] * R) - wy > STEP:
			nx += _fx[i]
			nz += _fz[i]
			n += 1
	if n == 0:
		return 0
	var l := sqrt(nx * nx + nz * nz)
	if l < 1e-6:
		tnx = 0.0
		tnz = 0.0
		return 2
	tnx = nx / l
	tnz = nz / l
	return 1


## a kart against the arena: pushed back out of whatever it cannot climb and slid along it (web battleWalls).
## Called from Kart.step() in place of the track's side walls.
func walls(k: Kart) -> void:
	var wy := k.wy
	var r := touch(k.x, k.y, wy)
	if r == 0:
		k.bpx = k.x
		k.bpy = k.y
		return
	if r == 2:
		# walled in on every side: back to where it last stood free
		if not is_nan(k.bpx):
			k.x = k.bpx
			k.y = k.bpy
		k.speed *= 0.5
		return
	var nx := tnx
	var ny := tnz
	for n in 16:
		k.x -= nx * 0.7
		k.y -= ny * 0.7
		if touch(k.x, k.y, wy) == 0:
			break
	# the web's own numbers (speed *= 1 - .22 * dot, the facing turns half way, sparks and a bump past .45): Kart._slide does exactly that
	k._slide(nx, ny, 0.22, 0.5)
	if touch(k.x, k.y, wy) == 0:
		k.bpx = k.x
		k.bpy = k.y


## a thrown thing against the arena: true if it has just met a wall (and has been turned back off it) (web battleProjWall)
func proj_wall(p: Dictionary, h: float) -> bool:
	var px := float(p["x"])
	var py := float(p["y"])
	if ground(px, py) - h <= STEP:
		return false
	# which way is the wall? try stepping back along each axis
	var bx := px - float(p["vx"]) * 0.02
	var by := py - float(p["vy"]) * 0.02
	var free_x := ground(bx, py) - h <= STEP
	var free_y := ground(px, by) - h <= STEP
	if free_x and not free_y:
		p["vx"] = -float(p["vx"])
		p["x"] = bx
	elif free_y and not free_x:
		p["vy"] = -float(p["vy"])
		p["y"] = by
	else:
		p["vx"] = -float(p["vx"])
		p["vy"] = -float(p["vy"])
		p["x"] = bx
		p["y"] = by
	return true


## thrown things in the arena. p["bh"] is the level a thrown thing is on: it follows the ground down a drop and up a
## ramp, and anything higher than a step is a wall it turns back off (twice; the third wall breaks it) (web bbProjWalls)
func proj_walls(p: Dictionary) -> void:
	if not p.has("bh"):
		var o = p.get("owner")
		p["bh"] = maxf(0.0, (o as Kart).wy) if o is Kart else maxf(0.0, ground(float(p["x"]), float(p["y"])))
	var type := String(p["type"])
	if type == "lob" or type == "flour":
		return   # those are in the air
	var g := ground(float(p["x"]), float(p["y"]))
	if g < -100.0:
		p["t"] = 0.0   # over the open edge
		return
	var bh := float(p["bh"])
	if g - bh > STEP:
		if proj_wall(p, bh):
			race.fx.append({"t": "bb_ric", "x": float(p["x"]), "y": float(p["y"]), "h": bh})
			p["b"] = int(p["b"]) + 1
			if int(p["b"]) > 2:
				p["t"] = 0.0
	else:
		p["bh"] = g


## the height a thrown thing is drawn at (web pGround in a battle)
func proj_ground(p: Dictionary, x: float, y: float) -> float:
	return float(p["bh"]) if p.has("bh") else maxf(0.0, ground(x, y))


## is this kart on the level of a thrown thing? (web sameLvl in a battle). A hit needs it: a pepperoni on the table
## does not catch a kart up on the boxes.
func same_lvl(k: Kart, p: Dictionary) -> bool:
	return absf(k.wy - (float(p["bh"]) if p.has("bh") else ground(float(p["x"]), float(p["y"])))) < 16.0


# ---------------------------------------------------------------- the round

## sets a kart down on a spawn place, facing the way the place says (an older export has no heading: then the middle
## of the table) (web bbSpawnAt)
func spawn_at(k: Kart, i: int) -> void:
	var s: Array = spawn[i % spawn.size()]
	k.x = float(s[0])
	k.y = float(s[1])
	k.a = float(s[2]) if s.size() > 2 else atan2(-k.y, -k.x)
	k.ma = k.a
	k.speed = 0.0
	k.wy = ground(k.x, k.y)
	k.last_g = k.wy
	k.wvy = 0.0
	k.g_rate = 0.0
	k.air = false
	k.big = false
	k.glide = false
	k.on_ramp = false
	k.on_glide = false
	k.drift = 0
	k.charge = 0.0
	k.boost = 0.0
	k.spin = 0.0
	k.z = 0.0
	k.bpx = k.x
	k.bpy = k.y
	k.loop = {}
	k.sc = -1
	k._save_prev()   # (the web sets px, py, pa, pma, pwy: it is drawn there at once, not sliding in from where it was)


## the start of a round: the first set of balloons each, no points, everyone round the arena (web battleStart)
func start() -> void:
	left = race.karts.size()
	t = TIME
	over = false
	skip = false
	by_time = false
	ghost = 0.0
	ghost_k = null
	jams = 0
	for i in race.karts.size():
		var k: Kart = race.karts[i]
		k.bb_l = 0
		k.bal = int(SETS[0])
		k.bb_s = 0
		k.bb_out = 0.0
		k.bb_dead = false
		k.bb_place = 0
		k.bb_i = i
		k.bb_a = {"t": 0.0, "tx": 0.0, "tz": 0.0, "stuck": 0.0, "rev": 0.0, "fire": 0.0, "pt": 0.0, "jam": 0, "en": null}
		spawn_at(k, i)


func colour(k: Kart) -> Color:
	return Color(String(cols[k.bb_i % cols.size()]))


## a hit that landed (web battleHit): one balloon of the victim's gone, a point to whoever threw it. `by` is the
## thrower, or null (nobody's point).
func hit(v: Kart, by) -> void:
	if over or v.bb_dead or not (v.bal > 0):
		return
	v.bal -= 1
	if not skip:
		race.fx.append({"t": "bb_pop", "k": v})
	if by is Kart and by != v:
		(by as Kart).bb_s += 1
		if not skip:
			race.fx.append({"t": "bb_point", "k": by})
	if v.bal <= 0:
		set_lost(v, 2.2)


## the last balloon of a set is gone: out for a moment and back with the next set, or, if that was the single balloon,
## out for good (web bbSetLost)
func set_lost(k: Kart, out: float) -> void:
	if k.bb_l >= SETS.size() - 1:
		elim(k)
		return
	k.bb_l += 1
	k.bb_out = out
	if not skip:
		race.fx.append({"t": "bb_out", "k": k, "next": int(SETS[k.bb_l])})


## eliminated (web bbElim): a bigger pop; the kart is hidden and parked far off the table (as Last Slice Standing
## does), it is nobody's target and takes nothing; its place is the number of drivers that were still in. The player's
## own kart stays where it happened, hidden, for 1.6 s (the camera is on it); then the watching starts.
func elim(k: Kart) -> void:
	var alive := 0
	for q: Kart in race.karts:
		if not q.bb_dead:
			alive += 1
	var stay: bool = k == race.player and not skip
	k.bb_dead = true
	left = alive - 1
	k.bb_place = alive
	k.bal = 0
	k.bb_out = 0.0
	k.finished = true
	k.elim = true
	k.place = alive
	k.finish_time = race.race_time
	k.item = ""
	k.item2 = ""
	k.pend.clear()
	k.ab_q = []
	k.ai["auto"] = true
	out_order.append(k)
	if not skip:
		race.fx.append({"t": "bb_elim", "k": k, "place": alive, "x": k.x, "y": k.y, "h": maxf(0.0, k.wy)})
	k.speed = 0.0
	k.spin = 0.0
	if stay:
		ghost = 1.6
		ghost_k = k
	else:
		away(k)
	if alive - 1 <= 1:
		finish(false)


## parked far off the table (web bbAway)
func away(k: Kart) -> void:
	k.speed = 0.0
	k.x = 50000.0 + maxi(1, k.bb_place) * 300.0
	k.y = 50000.0
	k.wy = 0.0
	k.last_g = 0.0
	k.wvy = 0.0
	k.g_rate = 0.0
	k.air = false
	k.z = 0.0
	k._save_prev()


## the order (web bbRank): drivers still in first, by points, then sets left, then balloons; then the eliminated,
## the last one out highest
func rank() -> Array[Kart]:
	var r: Array[Kart] = []
	r.assign(race.karts)
	r.sort_custom(func(a: Kart, b: Kart) -> bool:
		if a.bb_dead != b.bb_dead:
			return b.bb_dead
		if a.bb_dead:
			if a.bb_place != b.bb_place:
				return a.bb_place < b.bb_place
		else:
			if a.bb_s != b.bb_s:
				return a.bb_s > b.bb_s
			if a.bb_l != b.bb_l:
				return a.bb_l < b.bb_l
			if a.bal != b.bal:
				return a.bal > b.bal
		return a.bb_i < b.bb_i)
	return r


## the end of the round: one driver left, or (time) the clock ran out (web bbFinish)
func finish(time: bool) -> void:
	if over:
		return
	over = true
	by_time = time
	var r := rank()
	var sk := skip
	skip = false
	for i in r.size():
		var k: Kart = r[i]
		k.finished = true
		k.place = i + 1
		if not k.bb_dead:
			k.finish_time = race.race_time
		k.ai["auto"] = true
	race.finish_count = race.karts.size()
	race.fx.append({"t": "bb_end", "time": time, "first": r[0], "fast": sk})


## one physics step of the round: the clock, karts over the edge, coming back in, and the finish (web battleTick)
func tick(dt: float) -> void:
	if ghost > 0.0:
		# (the web: a timer of 1.6 s from the moment the player went out)
		ghost -= dt
		if ghost <= 0.0:
			if ghost_k != null and ghost_k.bb_dead:
				away(ghost_k)
				if race.state == "race" and not over:
					race.fx.append({"t": "bb_watch", "k": ghost_k})
			ghost_k = null
	if race.state != "race" or over:
		return
	t -= dt
	for k: Kart in race.karts:
		if k.bb_dead or over:
			continue
		if not (k.bb_out > 0.0) and k.wy < -70.0:
			# over the edge: one balloon gone, nobody's point
			if k.bal > 0:
				k.bal -= 1
				if not skip:
					race.fx.append({"t": "bb_pop", "k": k})
			if k.bal <= 0:
				set_lost(k, 1.3)
				if k.bb_dead or over:
					continue
			else:
				k.bb_out = 1.3
				if not skip:
					race.fx.append({"t": "bb_edge", "k": k})
		if k.bb_out > 0.0:
			k.bb_out -= dt
			k.speed *= pow(0.02, dt)
			if k.bb_out <= 0.0:
				# back in, well away from the others
				var best := 0
				var bd := -1.0
				for i in spawn.size():
					var s: Array = spawn[i]
					var d := 1e9
					for o: Kart in race.karts:
						if o != k and not o.bb_dead:
							d = minf(d, (o.x - float(s[0])) ** 2 + (o.y - float(s[1])) ** 2)
					if d > bd:
						bd = d
						best = i
				spawn_at(k, best)
				var last_now := false
				if not (k.bal > 0):
					k.bal = int(SETS[k.bb_l])
					last_now = k.bal == 1
				k.inv = 3.0
				k.bb_out = 0.0
				if not skip:
					race.fx.append({"t": "bb_back", "k": k, "last": last_now})
	if over:
		return
	if t <= 0.0:
		t = 0.0
		finish(true)


## "Skip to results" while watching (web bbSkip): the rest of the round is then played out at once by main.gd, many
## steps a frame with no sound and nothing of the pops drawn, so the final order is a real one. False once it is over.
func skip_on() -> bool:
	if over:
		return false
	if not skip:
		skip = true
		race.fx.append({"t": "bb_skip"})
	return true


## the read-out's parts (web bbHud): how many of your sets you still have (the pips), the clock, how many drivers are
## left (or that you are out, and where you came), your points
func readout(me: Kart) -> Dictionary:
	var s := maxi(0, ceili(t))
	var p := me.bb_s
	var n := 0
	for k: Kart in race.karts:
		if not k.bb_dead:
			n += 1
	return {"pips": 0 if me.bb_dead else SETS.size() - me.bb_l, "sets": SETS.size(), "clock": "%d:%02d" % [int(s / 60.0), s % 60],
		"mid": ("Out · " + ordinal(me.bb_place)) if me.bb_dead else "%d left" % n, "pts": "%d %s" % [p, "pt" if p == 1 else "pts"]}


static func ordinal(n: int) -> String:
	var v := n % 100
	if v >= 11 and v <= 13:
		return "%dth" % n
	return "%d%s" % [n, "st" if n % 10 == 1 else ("nd" if n % 10 == 2 else ("rd" if n % 10 == 3 else "th"))]


## under the name of the driver being watched (web bbSpecInfo)
func spec_info(k: Kart) -> String:
	if k.bb_dead:
		return "out"
	var p := k.bb_s
	var s := "%d %s" % [k.bal, "balloon" if k.bal == 1 else "balloons"]
	if k.bb_l < SETS.size() - 1:
		var rest: Array = []
		for i in range(k.bb_l + 1, SETS.size()):
			rest.append(str(int(SETS[i])))
		s += " (" + ", then ".join(PackedStringArray(rest)) + " to come)"
	else:
		s += ", the last"
	return s + " · %d %s" % [p, "point" if p == 1 else "points"]


## a row of the results sheet: the points, and that the driver went out (web bbResRow)
func res_row(k: Kart) -> String:
	var s := "%d %s" % [k.bb_s, "point" if k.bb_s == 1 else "points"]
	return ("out · " + s) if k.bb_dead else s


# ---------------------------------------------------------------- items

## what a battle's item boxes give (web bbRoll): only what you aim or steer yourself, by the web's weights, and only
## those left switched on in Settings. The meatball is one of the items a player unlocks for races; in a battle
## everybody has it unless it is switched off.
func roll() -> String:
	var l: Array = []
	var tot := 0.0
	for q in items:
		var nm := String(q[0])
		if (meat_off if nm == "meatball" else race.items_off.has(nm)):
			continue
		l.append(q)
		tot += float(q[1])
	if l.is_empty():
		return "pepperoni"
	var r: float = race.rng.randf() * tot
	for q in l:
		r -= float(q[1])
		if r <= 0.0:
			return String(q[0])
	return String(l[0][0])


# ---------------------------------------------------------------- the computer's drivers (web battleAI)
## fetch an item, hunt the nearest rival, shoot when lined up with a clear line, find their way round things.
## THE DRIVERS' MAP (web bbGrid, 2026-11-14, for the bigger table with its ramps and levels): the arena as a grid of
## 20-unit squares, made once from the shapes. A square can be stood on if a kart at its middle touches nothing; from a
## square to the next is a step if the ground between them never rises faster than a ramp does, and a drop of any height
## is a step too (never off the table). path() walks that grid from the kart to where it wants to be and gives back the
## furthest square of the way that can be driven at in a straight line (clear()). So no list of ramps is needed: a ramp
## is simply the only way the ground rises gently.

const C := 20.0                     # web BB_C
var _gnx := 0
var _gnz := 0
var _gh := PackedFloat32Array()
var _gok := PackedByteArray()
var _ged := PackedByteArray()
var _gpar := PackedInt32Array()
var _gmark := PackedInt32Array()
var _gq := PackedInt32Array()
var _gstamp := 0
const _D := [[1, 0], [0, 1], [-1, 0], [0, -1]]


func _grid() -> void:
	_gnx = ceili(2.0 * X / C)
	_gnz = ceili(2.0 * Z / C)
	var n := _gnx * _gnz
	_gh.resize(n)
	_gok.resize(n)
	_ged.resize(n)
	_gpar.resize(n)
	_gmark.resize(n)
	_gq.resize(n)
	_gok.fill(0)
	_ged.fill(0)
	_gmark.fill(0)
	_gstamp = 0
	for j in _gnz:
		for i in _gnx:
			var x := -X + (i + 0.5) * C
			var z := -Z + (j + 0.5) * C
			var g := ground(x, z)
			var q := j * _gnx + i
			_gh[q] = g
			_gok[q] = 1 if (g > -100.0 and g < 400.0 and touch(x, z, g) == 0) else 0
	for j in _gnz:
		for i in _gnx:
			var q := j * _gnx + i
			if _gok[q] == 0:
				continue
			var x := -X + (i + 0.5) * C
			var z := -Z + (j + 0.5) * C
			var e := 0
			for d in 4:
				var i2: int = i + int(_D[d][0])
				var j2: int = j + int(_D[d][1])
				if i2 < 0 or j2 < 0 or i2 >= _gnx or j2 >= _gnz or _gok[j2 * _gnx + i2] == 0:
					continue
				var p := float(_gh[q])
				var good := true
				for s in range(1, 5):
					var g2 := ground(x + float(_D[d][0]) * C * s / 4.0, z + float(_D[d][1]) * C * s / 4.0)
					if g2 - p > 2.4:
						good = false
						break
					p = g2
				if good:
					e |= 1 << d
			_ged[q] = e


## can a kart drive straight from one point to the other? The ground on the way neither steps up nor drops, and
## nothing stands within a kart's half width of the line (web bbClear)
func clear(x0: float, z0: float, h0: float, x1: float, z1: float) -> bool:
	var dx := x1 - x0
	var dz := z1 - z0
	var L := sqrt(dx * dx + dz * dz)
	if L < 1.0:
		return true
	var n := ceili(L / 8.0)
	var ux := dx / L
	var uz := dz / L
	var p := h0
	for s in range(1, n + 1):
		var f := float(s) / n
		var x := x0 + dx * f
		var z := z0 + dz * f
		var g := ground(x, z)
		if absf(g - p) > 3.4:
			return false
		if ground(x - uz * R, z + ux * R) - g > STEP or ground(x + uz * R, z - ux * R) - g > STEP:
			return false
		p = g
	return true


## is there a clear shot from one point to the other? (the ground between them is one surface: no wall, no drop) (web bbSee)
func see(x0: float, z0: float, h0: float, x1: float, z1: float) -> bool:
	var dx := x1 - x0
	var dz := z1 - z0
	var n := maxi(1, ceili(sqrt(dx * dx + dz * dz) / 10.0))
	var p := h0
	for s in range(1, n + 1):
		var g := ground(x0 + dx * s / n, z0 + dz * s / n)
		if absf(g - p) > 4.6:
			return false
		p = g
	return true


## the grid square at a point: its own if it can be stood on (and, with a height given, is at that height), else the
## nearest such within two squares; -1 if there is none
func _cell(x: float, z: float, wy: float, any_h: bool) -> int:
	var i := clampi(int(floor((x + X) / C)), 0, _gnx - 1)
	var j := clampi(int(floor((z + Z) / C)), 0, _gnz - 1)
	var q := j * _gnx + i
	if _gok[q] != 0 and (any_h or absf(_gh[q] - wy) < 9.0):
		return q
	var b := -1
	var bd := 1e9
	for dj in range(-2, 3):
		for di in range(-2, 3):
			var i2 := i + di
			var j2 := j + dj
			if i2 < 0 or j2 < 0 or i2 >= _gnx or j2 >= _gnz:
				continue
			var p := j2 * _gnx + i2
			if _gok[p] == 0 or (not any_h and absf(_gh[p] - wy) >= 9.0):
				continue
			var d := (-X + (i2 + 0.5) * C - x) ** 2 + (-Z + (j2 + 0.5) * C - z) ** 2
			if d < bd:
				bd = d
				b = p
	return b


## the way from the kart to (tx, tz): the point to steer at now, or an empty array if there is no way (in the air,
## walled in). shy: keep off the squares along the open west edge (web bbPath)
func path(k: Kart, tx: float, tz: float, shy: bool) -> Array:
	if _gnx == 0:
		_grid()
	var nx := _gnx
	var s := _cell(k.x, k.y, k.wy, false)
	var tq := _cell(tx, tz, 0.0, true)
	if s < 0 or tq < 0:
		return []
	if s == tq:
		return [tx, tz]
	_gstamp += 1
	var st := _gstamp
	var iw := 2 if shy else -1
	var qh := 0
	var qt := 0
	var found := false
	_gq[qt] = s
	qt += 1
	_gmark[s] = st
	_gpar[s] = -1
	while qh < qt:
		var q := _gq[qh]
		qh += 1
		if q == tq:
			found = true
			break
		var e := _ged[q]
		if e == 0:
			continue
		var p := 0
		if e & 1:
			p = q + 1
			if _gmark[p] != st:
				_gmark[p] = st
				_gpar[p] = q
				_gq[qt] = p
				qt += 1
		if e & 2:
			p = q + nx
			if _gmark[p] != st and (p % nx > iw or q % nx <= iw):
				_gmark[p] = st
				_gpar[p] = q
				_gq[qt] = p
				qt += 1
		if e & 4:
			p = q - 1
			if _gmark[p] != st and p % nx > iw:
				_gmark[p] = st
				_gpar[p] = q
				_gq[qt] = p
				qt += 1
		if e & 8:
			p = q - nx
			if _gmark[p] != st and (p % nx > iw or q % nx <= iw):
				_gmark[p] = st
				_gpar[p] = q
				_gq[qt] = p
				qt += 1
	if not found:
		return []
	var P := PackedInt32Array()
	var c := tq
	while c != -1:
		P.append(c)
		c = _gpar[c]
	P.reverse()
	var n := P.size() - 1
	var wy := k.wy
	if clear(k.x, k.y, wy, tx, tz) and absf(ground(tx, tz) - _gh[tq]) < 9.0:
		return [tx, tz]
	var pick := mini(n, 2)
	var a := mini(n, 14)
	while a > 2:
		var q2 := P[a]
		if clear(k.x, k.y, wy, -X + (q2 % nx + 0.5) * C, -Z + (int(q2 / nx) + 0.5) * C):
			pick = a
			break
		a -= 1
	var q3 := P[pick]
	return [-X + (q3 % nx + 0.5) * C, -Z + (int(q3 / nx) + 0.5) * C]


func _feel(k: Kart, a: float, r: float) -> bool:
	return ground(k.x + cos(k.a + a) * r, k.y + sin(k.a + a) * r) - k.wy > STEP


func _live(q) -> bool:
	return q is Kart and not (q as Kart).bb_dead and not ((q as Kart).bb_out > 0.0) and (q as Kart).bal > 0


func ai(k: Kart, dt: float) -> Dictionary:
	var A: Dictionary = k.bb_a
	var wy := k.wy
	var o := {"steer": 0.0, "brake": false, "nb": false, "mul": 1.0, "use": false, "back": false, "hold": false, "hold_sl": 1, "release": null}
	if k.bb_out > 0.0 or over or k.bb_dead:
		return o
	var at := float(A["t"]) - dt
	var last := k.bb_l >= SETS.size() - 1 and left > 2   # (careful on the last balloon, until it is down to a duel)
	if sqrt((float(A["tx"]) - k.x) ** 2 + (float(A["tz"]) - k.y) ** 2) < 26.0:
		at = minf(at, 0.05)   # at the point it was steering for: where next?
	if at <= 0.0:
		var st: float = race.sim_time
		at = 0.45 + float((k.bb_i * 37 + int(floor(st * 3.0))) % 7) * 0.07
		var has := false
		var aim := false
		var tx := 0.0
		var tz := 0.0
		# the nearest rival it has a clear shot at; the nearest of all, to hunt; the nearest armed one, to keep away from
		var en: Kart = null
		var ed := 1e9
		var far: Kart = null
		var fd := 1e9
		var arm: Kart = null
		var ad := 1e9
		for q: Kart in race.karts:
			if q == k or q.bb_dead or q.bb_out > 0.0 or not (q.bal > 0):
				continue
			var d := sqrt((q.x - k.x) ** 2 + (q.y - k.y) ** 2)
			if d < fd:
				fd = d
				far = q
			if d < 340.0 and absf(q.wy - wy) < 14.0 and see(k.x, k.y, wy, q.x, q.y):
				if d < ed:
					ed = d
					en = q
				if q.item != "" and d < ad:
					ad = d
					arm = q
		A["en"] = en
		if k.item != "" and en != null and ed < 330.0:
			# a clear shot: straight at where they will be
			tx = en.x + cos(en.ma) * en.speed * 0.25
			tz = en.y + sin(en.ma) * en.speed * 0.25
			has = true
			aim = true
		elif k.item != "" and far != null and (not last or fd < 300.0):
			# something to throw: after the nearest rival, wherever on the table
			tx = far.x
			tz = far.y
			has = true
		elif last and k.item == "" and arm != null and ad < 170.0:
			# on the last balloon with nothing to throw, and somebody armed is close: away from them
			var a := atan2(k.y - arm.y, k.x - arm.x)
			tx = clampf(k.x + cos(a) * 150.0, -X + 90.0, X - 40.0)
			tz = clampf(k.y + sin(a) * 150.0, -Z + 40.0, Z - 40.0)
			has = true
		else:
			# an item box: a near one, by each driver's own taste (it changes every twenty seconds and spreads them
			# over the table, the top included)
			var bd := 1e9
			var tw := int(floor(st / 20.0)) * 5
			for bi in race.boxes.size():
				var b: Dictionary = race.boxes[bi]
				var bx := float(b["x"])
				if float(b["r"]) > 0.0 or (last and bx < -X + 90.0):
					continue
				var bz := float(b["y"])
				var gy := float(b["gy"])
				var hsh: int = ((k.bb_i * 7 + bi * 13 + tw) * 2654435761) & 0xFFFFFFFF
				# (the box on the top is worth the climb)
				var d2 := sqrt((bx - k.x) ** 2 + (bz - k.y) ** 2) * (1.0 if absf(gy - wy) < 12.0 else 1.2) * (0.3 if gy > 60.0 else 1.0) * (0.55 + 0.9 * float(hsh % 1000) / 1000.0)
				if d2 < bd:
					bd = d2
					tx = bx
					tz = bz
					has = true
			if not has and far != null:
				tx = far.x
				tz = far.y
				has = true
			if not has:
				var s: Array = spawn[(k.bb_i * 3 + int(floor(st / 4.0))) % spawn.size()]
				tx = float(s[0]) * 0.5
				tz = float(s[1]) * 0.5
		if last:
			tx = maxf(tx, -X + 80.0)   # the last balloon keeps away from the open edge
		if not aim:
			var W := path(k, tx, tz, last)
			if not W.is_empty():
				tx = float(W[0])
				tz = float(W[1])
		A["tx"] = tx
		A["tz"] = tz
	A["t"] = at
	var des := atan2(float(A["tz"]) - k.y, float(A["tx"]) - k.x)
	var dd := Kart.ang_diff(des, k.a)
	var d0 := dd
	# feelers: straight ahead and to each side; a wall ahead turns the kart toward the freer side
	var f0 := _feel(k, 0.0, 30.0) or _feel(k, 0.0, 54.0)
	var fl := _feel(k, -0.6, 34.0)
	var fr := _feel(k, 0.6, 34.0)
	if f0:
		dd = 1.2 if (fl and not fr) else (-1.2 if (fr and not fl) else (1.2 if dd >= 0.0 else -1.2))
	elif fl:
		dd += 0.5
	elif fr:
		dd -= 0.5
	# the last balloon, close to the open west edge and heading for it: turn back in
	if last and k.x < -X + 60.0 and cos(k.a) < -0.15:
		dd = Kart.ang_diff(1.1 if sin(k.a) >= 0.0 else -1.1, k.a)
	o["steer"] = clampf(dd * 2.2, -1.0, 1.0)
	# the way on lies behind and it is going fast: ease off, so the turn fits between the things on the table
	if absf(d0) > 1.7 and k.speed > 110.0:
		o["mul"] = 0.4
	# nose against something with the way on behind it: back out at once
	if float(A["rev"]) <= 0.0 and absf(d0) > 1.5 and absf(k.speed) < 40.0 and _feel(k, 0.0, 15.0):
		A["rev"] = 0.8
		A["stuck"] = 0.0
	# stuck against something: back off, turning the other way
	var stuck := float(A["stuck"])
	if absf(k.speed) < 14.0 and k.spin <= 0.0:
		stuck += dt
	else:
		stuck = maxf(0.0, stuck - dt * 2.0)
	if stuck > 0.9:
		A["rev"] = 0.9
		stuck = 0.0
	A["stuck"] = stuck
	# going nowhere for four seconds, whatever the speedometer says (sliding along a wall, shunting back and forth):
	# set down again on open table, nothing lost
	var pt := float(A["pt"]) + dt
	if pt >= 1.0:
		pt = 0.0
		if A.has("px") and sqrt((k.x - float(A["px"])) ** 2 + (k.y - float(A["pz"])) ** 2) < 14.0 and k.spin <= 0.0:
			A["jam"] = int(A["jam"]) + 1
		else:
			A["jam"] = 0
		A["px"] = k.x
		A["pz"] = k.y
		if int(A["jam"]) >= 4:
			A["jam"] = 0
			A.erase("px")
			A["pt"] = pt
			jams += 1
			k.bb_out = 0.01
			return o
	A["pt"] = pt
	if float(A["rev"]) > 0.0:
		A["rev"] = float(A["rev"]) - dt
		o["brake"] = true
		o["steer"] = clampf(-d0 * 2.2, -1.0, 1.0)   # backing: the tail swings so the nose comes round to the way on
	# use what it holds
	var fire := float(A["fire"]) - dt
	var en2: Kart = A["en"] if _live(A.get("en")) else null
	var ed2 := sqrt((en2.x - k.x) ** 2 + (en2.y - k.y) ** 2) if en2 != null else 1e9
	if k.item != "" and fire <= 0.0 and k.spin <= 0.0 and not (k.roll > 0.0):
		var it := k.item
		var go := false
		var back := false
		if en2 != null:
			var ang := absf(Kart.ang_diff(atan2(en2.y - k.y, en2.x - k.x), k.a))
			if it == "oil" or it == "flour":
				if ed2 < 110.0 and ang > 2.2:
					go = true
					back = true
				elif at < 0.1 and ed2 > 260.0:
					go = true
					back = true
			elif it == "chili" or it == "rush":
				go = ed2 < 300.0 and ang < 0.5 and not last
			elif it == "garlic":
				go = ed2 < 200.0
			else:
				go = ed2 < 290.0 and ang < 0.24 and see(k.x, k.y, wy, en2.x, en2.y)
		elif it == "chili" or it == "rush" or it == "garlic":
			go = not last or cos(k.a) > -0.2
		if go:
			o["use"] = true
			o["back"] = back
			fire = 0.8 + float((k.bb_i * 13) % 5) * 0.2
	A["fire"] = fire
	return o
