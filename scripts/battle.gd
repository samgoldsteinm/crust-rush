extends RefCounted
## Balloon Battle, ported from the web game's tools/mini/battle.js (the rules: the web's docs/BALLOON-BATTLE-PLAN.md).
## A mode with no lap: karts drive anywhere in an arena and hit each other with items. Each hit pops one of the
## victim's balloons and is a point for whoever threw it; at no balloons you are out for a moment and come back with
## three and half your score; most points when the clock runs out wins. Off line only.
##
## The switch is the map: TrackData.battle (web BATTLE = def.battle). A Race on such a map makes one of these
## (race.bb) and sets race.mode = "bb"; a normal race never reads anything here. The hooks that call in:
##   kart.gd   step(): no off-road slowing; walls(): the arena's shapes instead of the track's walls; ground()
##   race.gd   ai_input -> ai(); spin_out -> hit(); update -> tick(); roll_item -> roll(); thrown items -> proj_walls()
##   view.gd   balloons, the pop, a thrown thing's height     hud.gd   the one-line read-out     main.gd   banners, camera
##
## The arena is a height field made of a few shapes, in the karts' own coordinates (x east, z south: a kart's k.y is z):
##   box  x0,x1,z0,z1,h     ramp  x0,x1,z0,z1,h0,h1,ax (its top runs from h0 at the low x or z to h1)     cyl  x,z,r,h
## One rule gives every wall: nothing drives up a step higher than STEP. The shapes, the spawn places, the ramps and
## the numbers all come from the map's export (the "battle" block, tools/ciexport.py): nothing of the arena is typed in here.
## This file has no class name on purpose: it is loaded by its path (a fresh checkout has no class list yet).

var race                     # the Race this battle is in
var T: TrackData
var spawn: Array = []        # [[x, z]] where karts are set down
var ramps: Array = []        # [{foot: [x, z], top: [x, z]}] for the computer's drivers
var items: Array = [["pepperoni", 3.0], ["trio", 2.0], ["meatball", 2.0], ["flour", 1.5], ["chili", 2.0]]   # web BB_ITEMS (the export's copy replaces it)
var cols: Array = ["#e3271d", "#1f6fd6", "#f6c41f", "#35a84a", "#ff7ab8", "#8a4fd6", "#ff8a1f", "#22b8c8"]   # web BB_COL
var TIME := 180.0            # web BB.T: the round's length
var STEP := 5.5              # web BB_STEP: the highest step a kart climbs
var R := 6.5                 # web BB_R: a kart's footprint
var X0 := -388.0             # web BB_X0: west of this there is only the kitchen floor
var FLOOR := -312.0          # web BB_FLOOR
var START := 3               # web BB_START: balloons each
var BACK := 3                # web BB_BACK: balloons you come back with
var t := 0.0                 # the clock, counting down (web BB.t)
var over := false
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
	TIME = float(d.get("T", TIME))
	STEP = float(d.get("step", STEP))
	R = float(d.get("r", R))
	X0 = float(d.get("x0", X0))
	FLOOR = float(d.get("floor", FLOOR))
	START = int(d.get("start", START))
	BACK = int(d.get("back", BACK))
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

## sets a kart down on a spawn place, facing the middle of the table (web bbSpawnAt)
func spawn_at(k: Kart, i: int) -> void:
	var s: Array = spawn[i % spawn.size()]
	k.x = float(s[0])
	k.y = float(s[1])
	k.a = atan2(-k.y, -k.x)
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


## the start of a round: three balloons each, no points, everyone round the arena (web battleStart)
func start() -> void:
	t = TIME
	over = false
	for i in race.karts.size():
		var k: Kart = race.karts[i]
		k.bal = START
		k.bb_s = 0
		k.bb_out = 0.0
		k.bb_i = i
		k.bb_a = {"t": 0.0, "tx": 0.0, "tz": 0.0, "stuck": 0.0, "rev": 0.0, "fire": 0.0, "pt": 0.0, "jam": 0}
		spawn_at(k, i)


func colour(k: Kart) -> Color:
	return Color(String(cols[k.bb_i % cols.size()]))


## a hit that landed (web battleHit): the victim loses a balloon, whoever threw it gets a point; at no balloons the
## victim's score is halved and it is out for a moment. `by` is the thrower, or null (nobody's point).
func hit(v: Kart, by) -> void:
	if over or not (v.bal > 0):
		return
	v.bal -= 1
	race.fx.append({"t": "bb_pop", "k": v})
	if by is Kart and by != v:
		(by as Kart).bb_s += 1
		race.fx.append({"t": "bb_point", "k": by})
	if v.bal <= 0:
		v.bb_s = int(floor(v.bb_s / 2.0))
		v.bb_out = 2.2
		race.fx.append({"t": "bb_out", "k": v, "edge": false, "left": 0})


## the standings: points, then balloons left, then the grid (web bbRank)
func rank() -> Array:
	var r: Array = race.karts.duplicate()
	r.sort_custom(func(a: Kart, b: Kart) -> bool:
		if a.bb_s != b.bb_s:
			return a.bb_s > b.bb_s
		if a.bal != b.bal:
			return a.bal > b.bal
		return a.bb_i < b.bb_i)
	return r


## one physics step of the round: the clock, karts over the edge, coming back in, and the finish (web battleTick)
func tick(dt: float) -> void:
	if race.state != "race" or over:
		return
	t -= dt
	for k: Kart in race.karts:
		if not (k.bb_out > 0.0) and k.wy < -70.0:
			# over the edge: one balloon gone, nobody's point
			if k.bal > 0:
				k.bal -= 1
				race.fx.append({"t": "bb_pop", "k": k})
			if k.bal <= 0:
				k.bb_s = int(floor(k.bb_s / 2.0))
			k.bb_out = 1.3
			race.fx.append({"t": "bb_out", "k": k, "edge": true, "left": k.bal})
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
						if o != k:
							d = minf(d, (o.x - float(s[0])) ** 2 + (o.y - float(s[1])) ** 2)
					if d > bd:
						bd = d
						best = i
				spawn_at(k, best)
				if not (k.bal > 0):
					k.bal = BACK
				k.inv = 3.0
				k.bb_out = 0.0
				race.fx.append({"t": "bb_back", "k": k})
	if t <= 0.0:
		t = 0.0
		over = true
		var r := rank()
		for i in r.size():
			var k2: Kart = r[i]
			k2.finished = true
			k2.place = i + 1
			k2.finish_time = race.race_time
			k2.ai["auto"] = true
		race.finish_count = race.karts.size()
		race.fx.append({"t": "bb_time"})


## the read-out's three parts: the clock, your points, your place (web bbHud: "2:41 · 3 pts · 3rd")
func readout(me: Kart) -> Array:
	var s := maxi(0, ceili(t))
	var p := me.bb_s
	var r := rank().find(me) + 1
	return ["%d:%02d" % [int(s / 60.0), s % 60], "%d %s" % [p, "pt" if p == 1 else "pts"], "%d%s" % [r, "st" if r == 1 else ("nd" if r == 2 else ("rd" if r == 3 else "th"))]]


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
## fetch an item, hunt the nearest rival they can get at, shoot when lined up, feel their way round walls

func _reach(k: Kart, x: float, z: float) -> bool:
	return absf(ground(x, z) - k.wy) < 12.0


func _feel(k: Kart, a: float, r: float) -> bool:
	return ground(k.x + cos(k.a + a) * r, k.y + sin(k.a + a) * r) - k.wy > STEP


func ai(k: Kart, dt: float) -> Dictionary:
	var A: Dictionary = k.bb_a
	var wy := k.wy
	var o := {"steer": 0.0, "brake": false, "nb": false, "mul": 1.0, "use": false, "back": false, "hold": false, "hold_sl": 1, "release": null}
	if k.bb_out > 0.0 or over:
		return o
	var at := float(A["t"]) - dt
	# the nearest rival on my level
	var en: Kart = null
	var ed := 1e9
	for q: Kart in race.karts:
		if q == k or q.bb_out > 0.0 or not (q.bal > 0):
			continue
		var d := sqrt((q.x - k.x) ** 2 + (q.y - k.y) ** 2)
		if d < ed and absf(q.wy - wy) < 14.0:
			ed = d
			en = q
	if at <= 0.0:
		var st: float = race.sim_time
		at = 0.45 + float((k.bb_i * 37 + int(floor(st * 3.0))) % 7) * 0.07
		var has := false
		var tx := 0.0
		var tz := 0.0
		if k.item != "" and en != null and ed < 330.0:
			tx = en.x + cos(en.ma) * en.speed * 0.25
			tz = en.y + sin(en.ma) * en.speed * 0.25
			has = true
		else:
			var bd := 1e9
			for b in race.boxes:
				if float(b["r"]) > 0.0:
					continue
				var bx := float(b["x"])
				var bz := float(b["y"])
				var d2 := sqrt((bx - k.x) ** 2 + (bz - k.y) ** 2) * (1.0 if _reach(k, bx, bz) else 2.2)
				if d2 < bd:
					bd = d2
					tx = bx
					tz = bz
					has = true
			if not has and en != null:
				tx = en.x
				tz = en.y
				has = true
			if not has:
				var s: Array = spawn[(k.bb_i * 3 + int(floor(st / 4.0))) % spawn.size()]
				tx = float(s[0]) * 0.5
				tz = float(s[1]) * 0.5
		# a target on another level: make for the foot (or the top) of the nearer ramp first
		if not _reach(k, tx, tz):
			var up := ground(tx, tz) > wy + 6.0
			var br = null
			var bd2 := 1e9
			for r in ramps:
				var p: Array = r["foot"] if up else r["top"]
				var d3 := sqrt((float(p[0]) - k.x) ** 2 + (float(p[1]) - k.y) ** 2)
				if d3 < bd2:
					bd2 = d3
					br = r
			if br != null:
				var p0: Array = br["foot"] if up else br["top"]
				var p1: Array = br["top"] if up else br["foot"]
				if bd2 < 34.0:
					tx = float(p1[0])
					tz = float(p1[1])
				else:
					tx = float(p0[0])
					tz = float(p0[1])
		A["tx"] = tx
		A["tz"] = tz
	A["t"] = at
	var des := atan2(float(A["tz"]) - k.y, float(A["tx"]) - k.x)
	var dd := Kart.ang_diff(des, k.a)
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
	o["steer"] = clampf(dd * 2.2, -1.0, 1.0)
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
			k.bb_out = 0.01
			return o
	A["pt"] = pt
	if float(A["rev"]) > 0.0:
		A["rev"] = float(A["rev"]) - dt
		o["brake"] = true
		o["steer"] = -float(o["steer"])
	# use what it holds
	var fire := float(A["fire"]) - dt
	if k.item != "" and fire <= 0.0 and k.spin <= 0.0 and not (k.roll > 0.0):
		var it := k.item
		var go := false
		var back := false
		if en != null:
			var ang := absf(Kart.ang_diff(atan2(en.y - k.y, en.x - k.x), k.a))
			if it == "oil" or it == "flour":
				if ed < 110.0 and ang > 2.2:
					go = true
					back = true
				elif at < 0.1 and ed > 260.0:
					go = true
					back = true
			elif it == "chili" or it == "rush":
				go = ed < 300.0 and ang < 0.5
			elif it == "garlic":
				go = ed < 200.0
			else:
				go = ed < 260.0 and ang < 0.22
		elif it == "chili" or it == "rush" or it == "garlic":
			go = true
		if go:
			o["use"] = true
			o["back"] = back
			fire = 0.8 + float((k.bb_i * 13) % 5) * 0.2
	A["fire"] = fire
	return o
