extends RefCounted
## Sandbox (free roam), ported from the web game's tools/mini/sandbox.js (the plan: the web's docs/SANDBOX-PLAN.md).
## One kart, no clock, no laps. Every track is a "place" of one of three kinds:
##   toy    the four rooms of the house: drive anywhere; the ground and the walls are worked out here
##   open   the fifteen pizza tracks: drive anywhere on the pizza; the ground is the track's height map plus what
##          stands on it; cliffs and deep water are walls; the crust is the edge
##   road   Sauce Spiral and the Neon tracks: the road hangs in the air, so you keep to it, either way round, with the
##          race's own ground and walls (`free` is false: the web's SBF)
## Places are joined by passages (gates); gold coins and hidden pepperoni coins are collected and saved.
##
## THE KEY FACT: on the web the walls are read from what is drawn (sbColumns goes through every triangle of the world).
## The PC has no scenery code, so the web hands over everything it worked out for a place (sbExport, taken by
## tools/ciexport.py into the map's json as "sandbox"): the kind, the numbers, the sparse grid of columns (for each
## square of floor the upright stretches that are solid there, each an underside and a top), the crust, the loops, the
## gates, the coins and the start flag. Nothing of a place is typed in here.
##
## The switch is the Race: race.sb is one of these in Sandbox and null in every race, Grand Prix, Last Slice and
## Balloon Battle, and a kart's own `sb` is the same object (null outside Sandbox). Every hook asks one of those first:
##   kart.gd   step(): ground(), walls(), idx_of(); the ramp from behind, the loop the other way round, no rim
##   race.gd   setup: one kart; update -> tick(); roll_item -> roll(); no finish
##   main.gd   the mode, travel, the race from the start line, Park, the map, the camera (solid())
##   view.gd   the kart's footing; scripts/sandbox_view.gd draws the coins, the flag and the gates
## This file has no class name on purpose: it is loaded by its path (a fresh checkout has no class list yet).

const SAVE_PATH := "user://sandbox.json"
const HASH_C := 48.0          # web SB_C: the size of a square of the lap-point grid

## the places this copy of the game has (id -> the "sb" card of its info.json: kind, name, R, start, lap). A passage
## to a place that is not installed is not offered. Set by main.gd when it lists the maps; empty = every gate stands.
static var places := {}
## the save, one record for the whole of Sandbox (web crust-sb): {c: coins, r: {coin id: 1}, g: {place: [[x, z, label]]}}
static var save := {}
static var no_save := false   # the tests: nothing is written to the player's save
static var _loaded := false

var race                     # the Race this is in
var T: TrackData
var id := ""
var kind := "toy"
var toy := true
var free := true             # web SBF: the driving is free (toy, open); false where you keep to the road
var title := ""              # "Home · Bedroom"
var STEP := 5.5              # web SB_STEP: the highest step a kart climbs
var R := 6.5                 # web SB_R: a kart's footprint
var HEAD := 9.0              # web SB_HEAD: what is higher than this above the kart is overhead, not in the way
var RAIL := 4.2              # web SB_RAIL: a toy track's raised edge
var GLEN := 190.0            # web SB_GLEN: a passage's length
var LVL := 6.5               # web sbLvl(): how far above or below the track still counts as "on it, at its level"
var TOYW := 46.0             # web TOYW(): half the width of a toy track with its edges
var rim := 0.0               # the crust's radius on a pizza (0: none)
var water := NAN             # a pizza's water level (NAN: none)
var loops: Array = []        # full loops: {x, y, tx, ty, nx, ny, g0, r, a, b}: round them the low things are not in the way
var shapes: Array = []       # what is not drawn (web SB.shapes: boxes and cylinders); empty today
var gates: Array = []        # {id, to, at, label, x, y, z, nx, nz, tx, tz, hw, road, plain, j}
var flag := []               # the start line's marker: [x, height, z]
var has_flag := false

# the coins, in columns (the tick goes through all of them every step)
var coin_n := 0
var coin_x := PackedFloat32Array()
var coin_y := PackedFloat32Array()     # height
var coin_z := PackedFloat32Array()
var coin_rare := PackedByteArray()
var coin_t := PackedFloat32Array()     # 0 there; > 0 seconds until it is back; < 0 found for good
var coin_id: Array = []
var coins_dirty := true                # for the drawing: something was taken or came back

# what the player is doing
var park := false            # the Park button (web SB.park)
var brake_both := false      # both brake pedals held on a touch screen (web keys.brakeBoth)
var race_near := false       # at the start line: the race is on offer (web SB.raceOn)
var cool := 0.0              # no passage takes the kart for a moment after it has arrived (web SB.cool)
var travel = null            # the gate the kart has just driven into: main.gd builds the next place (on another thread) and clears it
var arrived := false         # the kart has just come out of a tunnel into this place: main.gd notes it and clears it
var deferred := false        # read on another thread (scripts/world_build.gd): the save is not touched until sync_save()
var cam_f := 1.0             # the camera's pull-in (web SB.camF)

# the columns (web SB.col), unpacked: a count and a first span for every square, the spans one after another
var has_col := false
var cx0 := 0.0
var cz0 := 0.0
var cC := 5.0
var cnx := 0
var cnz := 0
var cb0 := 0.0
var cb1 := 0.0
var cb2 := 0.0
var cb3 := 0.0
var c_cnt := PackedByteArray()
var c_thin := PackedByteArray()
var c_first := PackedInt32Array()
var c_lo := PackedFloat32Array()
var c_hi := PackedFloat32Array()

var hash := {}               # web SB.hash: square of floor -> the lap points whose strip of track covers it
var bend := PackedFloat32Array()

# surf(): every surface at a point (web SB.S: [top, underside, lap point or -1, how far along, on the lap's own width])
var s_top := PackedFloat64Array()
var s_bot := PackedFloat64Array()
var s_j := PackedInt32Array()
var s_u := PackedFloat64Array()
var s_on := PackedByteArray()
var in_g := -1               # the gate whose mouth or passage the point is in (web SB.inG), or -1
var _fx := PackedFloat64Array()     # the eight points of a kart's footprint (web sbTouch: i * .785398)
var _fz := PackedFloat64Array()
var tnx := 0.0                      # touch(): the way into the wall (web _sbN)
var tnz := 0.0
# the gates again, in columns (surf() asks them first, about a hundred times a step)
var _gn := 0
var _gx := PackedFloat64Array()
var _gz := PackedFloat64Array()
var _gnx := PackedFloat64Array()
var _gnz := PackedFloat64Array()
var _ghw := PackedFloat64Array()
var _gy := PackedFloat64Array()
var _groad := PackedByteArray()


# ---------------------------------------------------------------- the tunnel between two places

## A kart travelling from one place to the next. The owner: "it should be the player continusously driving and eventually
## the new map will load and the driver will drive out but the game will never freeze or stop to load it will be one fluid
## drive through the tunnel right out to the other side". So the tunnel is not part of either place: from the moment the
## kart commits to a gate it drives THIS, a straight level corridor of any length, under the player's hands (the wheel
## between its walls, throttle, brake), while the next place is built on another thread. When that place is ready the
## corridor is laid, without the kart noticing, onto the gate it comes out of: `swap()` moves the corridor's own frame,
## and main.gd moves the kart, the camera and the sparks by the same step, so nothing on the screen changes.
## The kart's Kart.tun is one of these while it is inside (null everywhere else, and in every race).
## What is drawn of it is scripts/sandbox_warp.gd.
class Tun extends RefCounted:
	var ox := 0.0            # a point on the corridor's middle line: the mouth it was entered by (after the swap, a point
	var oz := 0.0            # that far behind the mouth it leaves by), and
	var dx := 1.0            # the way through it
	var dz := 0.0
	var y := 0.0             # its floor
	var hw := 17.0           # half its width, for the kart; it eases to the width of the gate it comes out of
	var hw_to := 17.0
	var rx := 21.0           # the tube that is drawn: half its width and its height above the middle line; eased likewise
	var ry := 34.0
	var rx_to := 21.0
	var ry_to := 34.0
	var s := 0.0             # how far along the kart is
	var s_in := 0.0          # where it committed: there is no way back past it
	var s_exit := INF        # where the mouth it leaves by stands (set by swap)
	var e_off := 0.0         # the way-out picture stands this far inside that mouth
	var swapped := false     # laid onto the place it comes out in
	var sealed := false      # the mouth behind is gone (the place left behind is being thrown away)
	var clip0 := 0.3         # drawn from here along (the entry mouth's plane), until sealed
	var cam_in := 0.0        # how far a camera must be past the entry mouth before the tube is shown to it
	var room_out := false    # the mouth it leaves by is in a room's wall (the arch there stands proud of the skirting)
	var to := ""             # where it leads
	var at := ""             # the gate there
	var from_gate := {}      # the gate it was entered by (to come back out of, should the next place fail)

	func depth(x: float, z: float) -> float:
		return (x - ox) * dx + (z - oz) * dz

	func across(x: float, z: float) -> float:
		return (x - ox) * -dz + (z - oz) * dx

	## one step of a kart in the corridor, in place of everything the track would do to it (Kart.step)
	func step(k: Kart, dt: float) -> void:
		hw = move_toward(hw, hw_to, 24.0 * dt)
		rx = move_toward(rx, rx_to, 24.0 * dt)
		ry = move_toward(ry, ry_to, 24.0 * dt)
		var sd := depth(k.x, k.y)
		var l := across(k.x, k.y)
		var lim := maxf(1.0, hw - 6.5)
		if absf(l) > lim:
			# the corridor's side: pushed back in and slid along it, as along any wall
			var sg := signf(l)
			var ov := absf(l) - lim
			var nx := -dz * sg
			var nz := dx * sg
			k.x -= nx * ov
			k.y -= nz * ov
			k._slide(nx, nz, 0.22, 0.5)
		if sd < s_in:
			# no way back out of the mouth it came in by: that place may already be gone
			k.x += dx * (s_in - sd)
			k.y += dz * (s_in - sd)
			sd = s_in
			if k.speed * (cos(k.ma) * dx + sin(k.ma) * dz) < 0.0:
				k.speed = 0.0
		s = sd
		if k.wall_t > 0.0:
			k.wall_t -= dt
		# the floor is level; a drift's hop still leaves it for a moment
		if k.air:
			k.air_t += dt
			k.wvy -= 260.0 * dt
			k.wy += k.wvy * dt
			if k.wy <= y:
				k.wy = y
				k.air = false
				k.big = false
				k.wvy = 0.0
		else:
			k.wy = y
		k.z = maxf(0.0, k.wy - y)
		k.last_g = y
		k.g_rate = 0.0
		k.glide = false
		k.on_ramp = false
		k.on_glide = false

	## lays the corridor onto the gate the kart comes out of: `f` is that gate's frame (frame_out), `ahead` how far
	## the kart still has to drive to its mouth. The kart's own distance along (s) does not change: the frame moves.
	## Returns [the turn, the old frame's point, the new frame's point] for main.gd to move everything else by.
	func swap(f: Dictionary, ahead: float) -> Array:
		var th0 := atan2(dz, dx)
		var from := Vector3(ox, y, oz)
		dx = float(f["dx"])
		dz = float(f["dz"])
		ox = float(f["ox"]) - dx * (s + ahead)
		oz = float(f["oz"]) - dz * (s + ahead)
		y = float(f["y"])
		s_exit = s + ahead
		s_in = s - 2.0
		e_off = float(f["e_off"])
		room_out = bool(f["room"])
		hw_to = float(f["hw"])
		rx_to = float(f["rx"])
		ry_to = float(f["ry"])
		swapped = true
		sealed = true
		return [atan2(dz, dx) - th0, from, Vector3(ox, y, oz)]


# ---------------------------------------------------------------- the save (web sbSave, sbKeep)

static func load_save() -> Dictionary:
	if _loaded:
		return save
	_loaded = true
	save = {"c": 0, "r": {}, "g": {}}
	if not no_save and FileAccess.file_exists(SAVE_PATH):
		var j = JSON.parse_string(FileAccess.get_file_as_string(SAVE_PATH))
		if typeof(j) == TYPE_DICTIONARY:
			save["c"] = int(j.get("c", 0))
			if j.get("r") is Dictionary:
				save["r"] = j["r"]
			if j.get("g") is Dictionary:
				save["g"] = j["g"]
			if j.get("v") != null:
				save["v"] = float(j["v"])
	return save


static func keep() -> void:
	if no_save:
		return
	var f := FileAccess.open(SAVE_PATH, FileAccess.WRITE)
	if f:
		f.store_string(JSON.stringify(save))


# ---------------------------------------------------------------- the speed slider (web sbSpd, sbSpdStep; tools/mini/sandbox.js, patch32.py)
## The share of its normal top speed the car may reach in Sandbox, .25 to 1 in steps of .05. main.gd multiplies the
## player's throttle by it (a positive throttle, not parked); a race from the start line is not Sandbox and is not slowed.
## Kept in the save as `v`, so it carries through passages, fast travel and a restart.
static var _spd := -1.0


static func spd() -> float:
	if _spd < 0.0:
		load_save()
		_spd = clampf(roundf(float(save.get("v", 1.0)) * 20.0) / 20.0, 0.25, 1.0) if float(save.get("v", 1.0)) > 0.0 else 1.0
	return _spd


static func spd_set(v: float) -> float:
	spd()
	v = clampf(roundf(v * 20.0) / 20.0, 0.25, 1.0)
	if v == _spd:
		return v
	_spd = v
	save["v"] = v
	keep()
	return v


static func spd_step(d: int) -> float:
	return spd_set(spd() + d * 0.05)


## is this place there to drive to? (its map is installed and was exported with a Sandbox block)
static func has_place(pid: String) -> bool:
	return places.is_empty() or places.has(pid)


# ---------------------------------------------------------------- loading a place (web sbArm, from the export)

func setup(race_, track: TrackData, defer_save := false) -> void:
	race = race_
	T = track
	deferred = defer_save
	var d: Dictionary = T.sb
	id = String(d.get("id", T.id))
	kind = String(d.get("kind", "toy"))
	toy = kind == "toy"
	free = kind != "road"
	title = String(d.get("name", T.title))
	STEP = float(d.get("step", STEP))
	R = float(d.get("r", R))
	HEAD = float(d.get("head", HEAD))
	RAIL = float(d.get("rail", RAIL))
	GLEN = float(d.get("glen", GLEN))
	LVL = float(d.get("lvl", LVL))
	TOYW = float(d.get("toyw", T.WALLD + 4.0))
	rim = float(d.get("rim", 0.0))
	water = float(d["water"]) if d.get("water") != null else NAN
	loops = d.get("loops", [])
	shapes = d.get("shapes", []) if d.get("shapes") is Array else []
	for i in 8:
		_fx.append(cos(i * 0.785398))
		_fz.append(sin(i * 0.785398))
	s_top.resize(48)
	s_bot.resize(48)
	s_u.resize(48)
	s_j.resize(48)
	s_on.resize(48)
	# the lap's bend at every point (the height along a bend, as the race works it out: web kEy)
	bend = T.bend
	if bend.size() != T.N:
		bend = PackedFloat32Array()
		bend.resize(T.N)
		for j in T.N:
			bend[j] = Kart.ang_diff(T.ang[(j + 10) % T.N], T.ang[(j - 10 + T.N) % T.N])
	if free:
		_read_col(d.get("col") if d.get("col") is Dictionary else {})
		_hash_track()
	# the gates: only those that lead to a place this copy has
	gates = []
	for g in d.get("gates", []):
		var gd: Dictionary = (g as Dictionary).duplicate()
		if not has_place(String(gd.get("to", ""))):
			continue
		gd["x"] = float(gd["x"])
		gd["y"] = float(gd.get("y", 0.0))
		gd["z"] = float(gd["z"])
		gd["nx"] = float(gd["nx"])
		gd["nz"] = float(gd["nz"])
		gd["tx"] = -float(gd["nz"])
		gd["tz"] = float(gd["nx"])
		gd["hw"] = float(gd.get("hw", 17.0))
		gd["road"] = int(gd.get("road", 0)) != 0
		gd["plain"] = int(gd.get("plain", 0)) != 0
		gd["j"] = int(gd.get("j", -1))
		gates.append(gd)
	_gn = gates.size()
	for gd2 in gates:
		_gx.append(gd2["x"])
		_gz.append(gd2["z"])
		_gnx.append(gd2["nx"])
		_gnz.append(gd2["nz"])
		_ghw.append(gd2["hw"])
		_gy.append(gd2["y"])
		_groad.append(1 if gd2["road"] else 0)
	# the coins; the hidden ones already found stay found (web sbCoins: c.t = -1)
	var found := {}
	if not deferred:
		found = load_save()["r"]
	for c in d.get("coins", []):
		var ca: Array = c
		coin_x.append(float(ca[0]))
		coin_y.append(float(ca[1]))
		coin_z.append(float(ca[2]))
		var rare := int(ca[3]) != 0
		coin_rare.append(1 if rare else 0)
		coin_id.append(String(ca[4]))
		coin_t.append(-1.0 if (rare and found.has(String(ca[4]))) else 0.0)
	coin_n = coin_x.size()
	if d.get("flag") is Array and (d["flag"] as Array).size() >= 3:
		flag = [float(d["flag"][0]), float(d["flag"][1]), float(d["flag"][2])]
		has_flag = true
	if not deferred:
		_remember_gates()


## the map remembers this place's tunnels (web sbArm: sv.g[regId])
func _remember_gates() -> void:
	var sv := load_save()
	var gl: Array = []
	for gd3 in gates:
		gl.append([roundf(gd3["x"]), roundf(gd3["z"]), String(gd3["label"])])
	(sv["g"] as Dictionary)[id] = gl
	keep()


## a place read on another thread did not touch the save (it is the main thread's): the hidden coins already found, and
## this place's tunnels for the map, are settled here when the main thread takes the place over
func sync_save() -> void:
	if not deferred:
		return
	deferred = false
	var found: Dictionary = load_save()["r"]
	for i in coin_n:
		if coin_rare[i] != 0 and found.has(String(coin_id[i])):
			coin_t[i] = -1.0
	coins_dirty = true
	_remember_gates()


## the columns grid from its packed form: `cells` (which squares hold something, 32-bit), `cnt` and `thin` (a byte a
## square), `sp` (their undersides and tops, 16-bit pairs in eighths of a unit, one square after another)
func _read_col(c: Dictionary) -> void:
	if c.is_empty():
		return
	cx0 = float(c["x0"])
	cz0 = float(c["z0"])
	cC = float(c["C"])
	cnx = int(c["nx"])
	cnz = int(c["nz"])
	var b: Array = c["b"]
	cb0 = float(b[0])
	cb1 = float(b[1])
	cb2 = float(b[2])
	cb3 = float(b[3])
	var q := float(T.sb.get("q", 8.0))
	var cells := Marshalls.base64_to_raw(String(c["cells"])).to_int32_array()
	var cnt := Marshalls.base64_to_raw(String(c["cnt"]))
	var thin := Marshalls.base64_to_raw(String(c["thin"]))
	var sp := Marshalls.base64_to_raw(String(c["sp"]))
	var n := cnx * cnz
	c_cnt.resize(n)
	c_thin.resize(n)
	c_first.resize(n)
	var tot := sp.size() / 4
	c_lo.resize(tot)
	c_hi.resize(tot)
	for i in tot:
		c_lo[i] = sp.decode_s16(i * 4) / q
		c_hi[i] = sp.decode_s16(i * 4 + 2) / q
	var w := 0
	for i in cells.size():
		var cell := cells[i]
		if cell < 0 or cell >= n:
			continue
		c_cnt[cell] = cnt[i]
		c_thin[cell] = thin[i]
		c_first[cell] = w
		w += cnt[i]
	has_col = true


## the track as ground: a grid of which lap points lie near each square (web sbHashTrack). Each lap point is entered
## for the squares its own strip of track covers: from one point's distance behind it to one ahead, edge to edge.
func _hash_track() -> void:
	hash = {}
	var w := (TOYW if toy else T.WALLD) + 3.4
	var sl := T.L / float(T.N)
	for j in T.N:
		var x := T.px[j]
		var y := T.py[j]
		for t in [-sl, 0.0, sl]:
			var l := -w
			while l <= w + 0.01:
				var c := (int(floor((x + T.nx[j] * l + T.tx[j] * t) / HASH_C)) + 2048) * 4096 + int(floor((y + T.ny[j] * l + T.ty[j] * t) / HASH_C)) + 2048
				var a = hash.get(c)
				if a == null:
					a = []
					hash[c] = a
				var arr: Array = a
				var seen := false
				for q in range(maxi(0, arr.size() - 8), arr.size()):
					if int(arr[q]) == j:
						seen = true
						break
				if not seen:
					arr.append(j)
				l += 16.0
	for key in hash:
		hash[key] = PackedInt32Array(hash[key])


# ---------------------------------------------------------------- the ground and the walls

func _put(n: int, t: float, b: float, j: int) -> void:
	if n >= s_top.size():
		s_top.resize(n + 16)
		s_bot.resize(n + 16)
		s_u.resize(n + 16)
		s_j.resize(n + 16)
		s_on.resize(n + 16)
	s_top[n] = t
	s_bot[n] = b
	s_j[n] = j
	s_u[n] = 0.0
	s_on[n] = 0


## every surface at a point: the s_ columns filled, their number returned (web sbSurf)
func surf(x: float, z: float) -> int:
	var n := 0
	in_g = -1
	for g in _gn:
		if _groad[g] != 0:
			continue
		var d := (x - _gx[g]) * _gnx[g] + (z - _gz[g]) * _gnz[g]
		if d > -20.0 and d < GLEN:
			# (a gate's own way along the wall is its normal turned a quarter: tx = -nz, tz = nx)
			var l := (x - _gx[g]) * -_gnz[g] + (z - _gz[g]) * _gnx[g]
			if l > -_ghw[g] and l < _ghw[g]:
				# in a passage's mouth or the passage itself: bare floor (the mouth reaches 20 units into the room)
				in_g = g
				return 0
	for s in shapes:
		var sd: Dictionary = s
		if String(sd.get("t", "box")) == "cyl":
			var dx := x - float(sd["x"])
			var dz := z - float(sd["z"])
			if dx * dx + dz * dz <= float(sd["r"]) * float(sd["r"]):
				_put(n, float(sd["h"]), float(sd["b"]), -1)
				n += 1
		elif x >= float(sd["x0"]) and x <= float(sd["x1"]) and z >= float(sd["z0"]) and z <= float(sd["z1"]):
			_put(n, float(sd["h"]), float(sd["b"]), -1)
			n += 1
	if rim > 0.0 and x * x + z * z > rim * rim:
		_put(n, 1e6, -1e9, -1)   # past the crust
		n += 1
	if has_col:
		if x < cb0 or x > cb1 or z < cb2 or z > cb3:
			_put(n, 1e6, -1e9, -1)   # past the room's own edge
			n += 1
		else:
			var i := int(floor((x - cx0) / cC))
			var k := int(floor((z - cz0) / cC))
			if i >= 0 and k >= 0 and i < cnx and k < cnz:
				var q := i * cnz + k
				var cn := c_cnt[q]
				if cn > 0:
					# round a full loop the low things, its lips and the rails of its two lanes, are not in the way: the
					# loop's own rules place the kart there (without this a pizza's loop could not be entered in free driving)
					var low := -1e9
					for lp in loops:
						var ld: Dictionary = lp
						var al := (x - float(ld["x"])) * float(ld["tx"]) + (z - float(ld["y"])) * float(ld["ty"])
						if al > -float(ld["r"]) and al < float(ld["r"]):
							var lt := (x - float(ld["x"])) * float(ld["nx"]) + (z - float(ld["y"])) * float(ld["ny"])
							if lt > float(ld["a"]) and lt < float(ld["b"]):
								low = float(ld["g0"]) + 7.5
								break
					var o := c_first[q]
					for e in cn:
						var t := c_hi[o + e]
						if t > low:
							_put(n, t, c_lo[o + e], -1)
							n += 1
	var a = hash.get((int(floor(x / HASH_C)) + 2048) * 4096 + int(floor(z / HASH_C)) + 2048)
	if a != null:
		# (on a pizza the track lies on the hills: its height is the ground's plus its own; it has no raised edge to bump
		# over, and its width for "the lap is always open" is the road's)
		var arr: PackedInt32Array = a
		var N := T.N
		var sl := T.L / float(N)
		var w := TOYW if toy else T.RW + 10.0
		var wide := (w + 3.2) if toy else T.WALLD
		var g0 := 0.0 if toy else T.ground(x, z)
		var n0 := n
		for j in arr:
			var dx2 := x - T.px[j]
			var dz2 := z - T.py[j]
			var u := dx2 * T.tx[j] + dz2 * T.ty[j]
			if u < -sl * 0.75 or u > sl * 0.75:
				continue
			var lat := dx2 * T.nx[j] + dz2 * T.ny[j]
			var la := absf(lat)
			if la > wide:
				continue
			# how far along, with the bend allowed for exactly as the race does (web kEy): on the outside of a bend the lap
			# points are further apart than on the middle line
			var kap := bend[j] / (20.0 * sl)
			var f := clampf(u / (1.0 - clampf(kap * lat, -0.7, 0.7)) / sl, -2.0, 2.0)
			var fi := int(floor(f))
			var e2 := g0 + T.ey_at(((j + fi) % N + N) % N, f - float(fi))
			var top := e2 + (RAIL if (toy and la > w) else 0.0)
			var au := absf(u)
			var hit := false
			for q2 in range(n0, n):
				if absf(s_bot[q2] + 2.5 - e2) < 6.0:
					hit = true
					if au < s_u[q2]:
						s_top[q2] = top
						s_bot[q2] = e2 - 2.5
						s_j[q2] = j
						s_u[q2] = au
						s_on[q2] = 1 if la <= w else 0
					break
			if not hit:
				_put(n, top, e2 - 2.5, j)
				s_u[n] = au
				s_on[n] = 1 if la <= w else 0
				n += 1
	return n


## the ground under a point for something at height wy: the highest surface it could be standing on (web sbG;
## wy = 1e9 asks for the highest of all)
func ground(x: float, z: float, wy: float = 1e9) -> float:
	var n := surf(x, z)
	if in_g >= 0 and not toy and ((x - _gx[in_g]) * _gnx[in_g] + (z - _gz[in_g]) * _gnz[in_g]) > -2.0:
		return _gy[in_g]   # in a passage through the crust: its own level floor
	# on the track's own surface, at the kart's own level, the ground IS the track: nothing drawn there lifts the kart
	var r := -1e9
	for i in n:
		if s_j[i] >= 0 and s_on[i] != 0 and absf(s_bot[i] + 2.5 - wy) <= LVL and s_top[i] > r:
			r = s_top[i]
	if r > -1e8:
		return r
	var h := 0.0 if toy else T.ground(x, z)
	for i in n:
		var t := s_top[i]
		if t <= wy + STEP and t > h:
			h = t
	return h


## THE LAP IS ALWAYS OPEN: where the point is on the track's own surface at the kart's own level, nothing drawn there
## is in the way. Otherwise: anything too high to climb whose underside is not overhead (web sbBlocked)
func blocked(x: float, z: float, wy: float) -> bool:
	var n := surf(x, z)
	for i in n:
		if s_j[i] >= 0 and s_on[i] != 0 and absf(s_bot[i] + 2.5 - wy) <= LVL:
			return false
	if kind == "open" and in_g < 0:
		# a pizza's own ground: a face that rises more than a step from where the kart stands is a cliff, not a hill, and
		# water deeper than the wheels is a shore
		var g0 := T.ground(x, z)
		if g0 > wy + STEP or (not is_nan(water) and g0 < water - 3.0 and wy < water + HEAD):
			return true
	for i in n:
		if s_top[i] > wy + STEP and s_bot[i] < wy + HEAD:
			return true
	return false


## is a kart's footprint (eight points round it) against something it cannot climb? 0 no; 1 yes, and (tnx, tnz) is
## the way in; 2 walled in on every side (web sbTouch)
func touch(x: float, z: float, wy: float) -> int:
	var nx := 0.0
	var nz := 0.0
	var n := 0
	for i in 8:
		if blocked(x + _fx[i] * R, z + _fz[i] * R, wy):
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


## a kart against the place: pushed back out of whatever it cannot climb and slid along it (web sbWalls).
## Called from Kart.step() in place of the track's side walls.
func walls(k: Kart) -> void:
	var wy := k.wy
	var r := touch(k.x, k.y, wy)
	if r == 0:
		k.bpx = k.x
		k.bpy = k.y
		return
	if r == 2:
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
	# the web's own numbers (speed *= 1 - .22 * dot, the facing turns half way, sparks and a bump past .45): Kart._slide
	k._slide(nx, ny, 0.22, 0.5)
	if touch(k.x, k.y, wy) == 0:
		k.bpx = k.x
		k.bpy = k.y


## which lap point the kart is over, if it is on the track at its own level (the boosters and the loop go by lap
## point); otherwise the one it had. near: the race's own answer (the nearest lap point either side of the last one):
## on a pizza a kart in the air goes by that, when that lap point is really nearby (web sbIdx)
func idx_of(k: Kart, was: int, near: int = -1) -> int:
	var n := surf(k.x, k.y)
	var wy := k.wy
	var j := was
	var bd := 7.0
	var on := false
	for i in n:
		if s_j[i] < 0:
			continue
		var d := absf(s_bot[i] + 2.5 - wy)
		if d < bd:
			bd = d
			j = s_j[i]
			on = true
	k.sb_off = not on
	if not on and near >= 0 and kind == "open" and (k.air or k.glide):
		var dx := T.px[near] - k.x
		var dy := T.py[near] - k.y
		if dx * dx + dy * dy < 170.0 * 170.0:
			return near
	return j


## the lap's own height at a kart's place, where the place has no ground of its own (web kGround)
func _base(x: float, z: float) -> float:
	return 0.0 if toy else T.ground(x, z)


## is something solid at this spot and height? For the camera, which must not look from inside a fence or a wall;
## the track's posts and bars ("thin") are looked past (web sbSolid)
func solid(x: float, z: float, y: float) -> bool:
	for g in _gn:
		if _groad[g] != 0:
			continue
		var d := (x - _gx[g]) * _gnx[g] + (z - _gz[g]) * _gnz[g]
		if d > -12.0 and d < GLEN + 10.0 and absf((x - _gx[g]) * -_gnz[g] + (z - _gz[g]) * _gnx[g]) < _ghw[g] + 1.0:
			return false
	if has_col:
		if x < cb0 or x > cb1 or z < cb2 or z > cb3:
			return true
		for dx in [-2.0, 0.0, 2.0]:
			for dz in [-2.0, 0.0, 2.0]:
				var i := int(floor((x + dx - cx0) / cC))
				var k := int(floor((z + dz - cz0) / cC))
				if i < 0 or k < 0 or i >= cnx or k >= cnz:
					continue
				var q := i * cnz + k
				if c_thin[q] != 0:
					continue
				var o := c_first[q]
				for e in c_cnt[q]:
					if c_lo[o + e] <= y + 1.0 and c_hi[o + e] >= y - 1.0:
						return true
	for s in shapes:
		var sd: Dictionary = s
		if float(sd["h"]) <= y or float(sd["b"]) >= y:
			continue
		if String(sd.get("t", "box")) == "cyl":
			var ddx := x - float(sd["x"])
			var ddz := z - float(sd["z"])
			var rr := float(sd["r"]) + 2.0
			if ddx * ddx + ddz * ddz <= rr * rr:
				return true
		elif x >= float(sd["x0"]) - 3.0 and x <= float(sd["x1"]) + 3.0 and z >= float(sd["z0"]) - 3.0 and z <= float(sd["z1"]) + 3.0:
			return true
	return false


# ---------------------------------------------------------------- starting, arriving, the tick

## the karts are set on Sandbox's own ground where they stand (web sbStart)
func start() -> void:
	for k: Kart in race.karts:
		k.sb = self
		k.sbf = free
		k.bal = 0
		k.bb_s = 0
		k.bb_out = 0.0
		if free:
			k.wy = ground(k.x, k.y, _base(k.x, k.y) + T.ey[k.idx] + 2.0)
			k.last_g = k.wy
			k.wvy = 0.0
			k.g_rate = 0.0
			k.air = false
			k.bpx = k.x
			k.bpy = k.y
			k._save_prev()
	park = false
	cool = 0.0
	travel = null
	cam_f = 1.0


## A gate as a tunnel's frame for a kart driving IN: the mouth's point, the way through, the floor, the widths.
## An arch (in a room's wall or a pizza's crust) leads out along its normal; so does the arch over a road's left-hand
## lane; the garage's open door has no arch: its tunnel begins 64 out on the drive, round wherever the kart crosses.
func frame_in(g: Dictionary, k: Kart) -> Dictionary:
	var nx := float(g["nx"])
	var nz := float(g["nz"])
	var f := {"dx": nx, "dz": nz, "y": float(g["y"]), "ox": float(g["x"]), "oz": float(g["z"]), "hw": float(g["hw"]), "e_off": 0.0, "room": false, "cam_in": 0.9 + 2.0}
	if bool(g["plain"]):
		var l: float = (k.x - float(g["x"])) * float(g["tx"]) + (k.y - float(g["z"])) * float(g["tz"])
		f["ox"] = float(g["x"]) + nx * 64.0 + float(g["tx"]) * l
		f["oz"] = float(g["z"]) + nz * 64.0 + float(g["tz"]) * l
		f["hw"] = 17.0
		f["cam_in"] = 2.0
	elif not bool(g["road"]) and toy and id != "backyard":
		f["cam_in"] = 7.2 + 2.0   # (a room's arch stands proud of the wall's skirting: the tube is shown from just before its face)
	_tube_size(f, bool(g["road"]))
	return f


## ...and for a kart coming OUT: the mouth's point and the way out of it. Out of an arch in a wall or a crust the kart
## drives back along the normal, into the place. On a road it comes through the arch from behind, along the lap. At the
## garage's door the mouth is 64 out on the drive and the kart drives in through the door.
func frame_out(g: Dictionary) -> Dictionary:
	var nx := float(g["nx"])
	var nz := float(g["nz"])
	var room: bool = toy and id != "backyard"
	var f := {"dx": -nx, "dz": -nz, "y": float(g["y"]), "ox": float(g["x"]), "oz": float(g["z"]), "hw": float(g["hw"]), "e_off": 10.0 if room else 52.0, "room": room, "road": false, "j": -1}
	if bool(g["road"]):
		f["dx"] = nx
		f["dz"] = nz
		f["e_off"] = 3.0
		f["room"] = false
		f["road"] = true
		f["j"] = int(g["j"])
	elif bool(g["plain"]):
		f["ox"] = float(g["x"]) + nx * 64.0
		f["oz"] = float(g["z"]) + nz * 64.0
		f["hw"] = 17.0
		f["e_off"] = 1.0
		f["room"] = false
	_tube_size(f, bool(g["road"]))
	return f


## the tube drawn round a corridor (web sbGates: W = hw + 1, H = 27, or 31 over a road; rx = W + 3, ry = H + 7)
func _tube_size(f: Dictionary, road: bool) -> void:
	f["rx"] = float(f["hw"]) + 1.0 + 3.0
	f["ry"] = (31.0 if road else 27.0) + 7.0


## the kart commits to a gate: from here it drives the tunnel (Tun), not this place
func _commit(k: Kart, g: Dictionary) -> void:
	var f := frame_in(g, k)
	var tn := Tun.new()
	tn.ox = float(f["ox"])
	tn.oz = float(f["oz"])
	tn.dx = float(f["dx"])
	tn.dz = float(f["dz"])
	tn.y = float(f["y"])
	tn.hw = float(f["hw"])
	tn.hw_to = tn.hw
	tn.rx = float(f["rx"])
	tn.ry = float(f["ry"])
	tn.rx_to = tn.rx
	tn.ry_to = tn.ry
	tn.cam_in = float(f["cam_in"])
	tn.s = tn.depth(k.x, k.y)
	tn.s_in = tn.s - 2.0
	tn.to = String(g["to"])
	tn.at = String(g.get("at", ""))
	tn.from_gate = g
	# (whatever the kart was in the middle of belongs to the place it is leaving)
	k.loop = {}
	k.loop_th = 0.0
	k.sc = -1
	k.glide = false
	k.big = false
	k.sb_off = true
	k.tun = tn
	travel = g


## the kart has reached the mouth it comes out of: it is this place's from here (called from tick)
func _leave_tun(k: Kart) -> void:
	var tn = k.tun
	k.tun = null
	k.bpx = k.x
	k.bpy = k.y
	k.air = false
	k.wvy = 0.0
	k.g_rate = 0.0
	if free:
		k.wy = ground(k.x, k.y, float(tn.y) + 2.0)
		k.idx = idx_of(k, 0)
	else:
		var g = gate_by_id(String(tn.at))
		if g != null and int(g["j"]) >= 0:
			k.idx = int(g["j"])
		else:
			k.idx = T.nearest_any(k.x, k.y)
		k.sb_off = false
		k.wy = T.ground(k.x, k.y) + T.k_ey(k.idx, k.x, k.y)
	k.last_g = k.wy
	k.prog = 0
	cool = 1.0
	travel = null
	arrived = true


func gate_by_id(gid: String) -> Variant:
	for g in gates:
		if String(g["id"]) == gid:
			return g
	return null


## sets the kart down where it comes out: at the gate `at` (the first gate if this place has no such gate), or a
## little behind the start line when `at` is "" (fast travel, and the way back from a race) (web sbTravel, its second half)
func arrive(k: Kart, at: String, sp: float) -> void:
	var a = null
	if at != "":
		a = gate_by_id(at)
		if a == null and not gates.is_empty():
			a = gates[0]
	var N := T.N
	k.idx = 0
	k.prog = 0
	k.loop = {}
	k.loop_th = 0.0
	k.sc = -1
	k.glide = false
	if a != null and bool(a["road"]):
		k.x = float(a["x"]) + float(a["nx"]) * 34.0
		k.y = float(a["z"]) + float(a["nz"]) * 34.0
		k.a = atan2(float(a["nz"]), float(a["nx"]))
		k.idx = (int(a["j"]) + int(round(34.0 / (T.L / N)))) % N
	elif a != null:
		var out := 46.0 if bool(a["plain"]) else GLEN - 60.0
		k.x = float(a["x"]) + float(a["nx"]) * out
		k.y = float(a["z"]) + float(a["nz"]) * out
		k.a = atan2(-float(a["nz"]), -float(a["nx"]))
	else:
		var j := (N - int(round(40.0 / (T.L / N)))) % N
		k.x = T.px[j]
		k.y = T.py[j]
		k.a = atan2(T.ty[j], T.tx[j])
		k.idx = j
	k.ma = k.a
	k.speed = sp
	k.wvy = 0.0
	k.g_rate = 0.0
	k.air = false
	k.big = false
	k.drift = 0
	k.charge = 0.0
	k.spin = 0.0
	k.z = 0.0
	k.on_ramp = false
	k.on_glide = false
	k.bpx = k.x
	k.bpy = k.y
	if free:
		var lvl: float = float(a["y"]) if (a != null and not bool(a["road"])) else (_base(k.x, k.y) + T.ey[k.idx])
		k.wy = ground(k.x, k.y, lvl + 2.0)
		k.last_g = k.wy
		k.idx = idx_of(k, k.idx)
	else:
		k.wy = T.ground(k.x, k.y) + T.k_ey(k.idx, k.x, k.y)
		k.last_g = k.wy
	k._save_prev()
	cool = 1.0
	travel = null


## heading into a mouth a little off its middle, the kart is eased sideways into it instead of meeting the jamb: only in
## the last 110 units before the wall, only when it is pointing in and already within reach of the mouth, and never
## faster than a kart could steer there (web sbGuide, v197; road gates are left alone)
func guide(k: Kart, dt: float) -> void:
	if not free or k.air or not k.loop.is_empty() or not (k.speed > 20.0):
		return
	for g in gates:
		var gd: Dictionary = g
		if bool(gd["road"]):
			continue
		var gx := float(gd["x"])
		var gz := float(gd["z"])
		var d := (k.x - gx) * float(gd["nx"]) + (k.y - gz) * float(gd["nz"])
		if d < -110.0 or d > 30.0:
			continue
		var tx := float(gd["tx"])
		var tz := float(gd["tz"])
		var hw := float(gd["hw"])
		var l := (k.x - gx) * tx + (k.y - gz) * tz
		var lim := maxf(4.0, hw - 10.0)
		if absf(l) <= lim or absf(l) > hw + 26.0:
			continue
		if cos(k.ma) * float(gd["nx"]) + sin(k.ma) * float(gd["nz"]) < 0.55:
			continue
		if absf(k.wy - float(gd["y"])) > 12.0:
			continue
		var mv := clampf(signf(l) * lim - l, -70.0 * dt, 70.0 * dt)
		var nx2 := k.x + tx * mv
		var ny2 := k.y + tz * mv
		if d < -22.0 and blocked(nx2, ny2, k.wy):
			continue   # (out in the room something may stand beside the kart)
		k.x = nx2
		k.y = ny2
		return


## parked, or both brake pedals held: no throttle and no brake (web sbStop)
func stopped() -> bool:
	return park or brake_both


## how many hidden coins of this place are found, and how many there are (web sbFound)
func found() -> Array:
	var n := 0
	var t := 0
	for i in coin_n:
		if coin_rare[i] != 0:
			t += 1
			if coin_t[i] < 0.0:
				n += 1
	return [n, t]


## each step of the race: the full stop, the start line's offer, the passages, the coins (web sbTick)
func tick(dt: float) -> void:
	if race.state != "race":
		race_near = false
		return
	var k: Kart = race.player
	if k == null:
		return
	if stopped() and k.loop.is_empty() and not k.air:
		var sp := k.speed
		var d := minf(absf(sp), (140.0 + absf(sp) * 5.0) * dt)
		k.speed = sp - signf(sp) * d
		if absf(k.speed) < 1.5:
			k.speed = 0.0
		k.boost = 0.0
		k.drift = 0
		k.charge = 0.0
	if k.tun != null:
		# in the tunnel between two places: nothing of this place reaches the kart until it is out of the mouth
		race_near = false
		if k.tun.swapped and k.tun.s >= k.tun.s_exit:
			_leave_tun(k)
		return
	guide(k, dt)
	race_near = has_flag and travel == null and (k.x - float(flag[0])) ** 2 + (k.y - float(flag[2])) ** 2 < 46.0 * 46.0 and absf(k.wy - float(flag[1])) < 10.0
	if cool > 0.0:
		cool -= dt
	elif travel == null:
		for g in gates:
			var gd: Dictionary = g
			var road: bool = gd["road"]
			var d2: float = (k.x - float(gd["x"])) * float(gd["nx"]) + (k.y - float(gd["z"])) * float(gd["nz"])
			# (an arch in a wall or a crust: once the kart is 30 in. The web waits until 120 and then stops to load; here the
			#  next place is built while the kart drives on, so it is started as soon as the kart is clearly going through)
			if d2 > (0.0 if road else (64.0 if bool(gd["plain"]) else 30.0)) and (not road or (d2 < 26.0 and absf(k.wy - float(gd["y"])) < 14.0)) \
					and absf((k.x - float(gd["x"])) * float(gd["tx"]) + (k.y - float(gd["z"])) * float(gd["tz"])) < float(gd["hw"]) + 2.0 \
					and cos(k.ma) * float(gd["nx"]) + sin(k.ma) * float(gd["nz"]) > 0.2:
				_commit(k, gd)
				return
	# the coins: a gold one is back 40 s after it is taken; a pepperoni coin is found once, for good, and is worth ten
	var y := k.wy + 3.5
	var ch := false
	for i in coin_n:
		var t := coin_t[i]
		if t < 0.0:
			continue
		if t > 0.0:
			t -= dt
			if t <= 0.0:
				t = 0.0
				coins_dirty = true
			coin_t[i] = t
			continue
		var dx := coin_x[i] - k.x
		var dz := coin_z[i] - k.y
		var rare := coin_rare[i] != 0
		var r := 12.0 if rare else 10.5
		if dx * dx + dz * dz > r * r or absf(coin_y[i] - y) > (14.0 if rare else 10.0):
			continue
		if rare:
			coin_t[i] = -1.0
			(save["r"] as Dictionary)[String(coin_id[i])] = 1
			save["c"] = int(save["c"]) + 10
			var f := found()
			race.fx.append({"t": "sb_rare", "x": coin_x[i], "y": coin_z[i], "h": coin_y[i], "n": int(f[0]), "of": int(f[1])})
		else:
			coin_t[i] = 40.0
			save["c"] = int(save["c"]) + 1
			race.fx.append({"t": "sb_coin", "x": coin_x[i], "y": coin_z[i], "h": coin_y[i]})
		coins_dirty = true
		ch = true
	if ch:
		keep()


## what an item box gives here: only the boost, there is nobody to throw anything at (web sbRoll)
func roll() -> String:
	return "chili"


## the read-out's three lines: the place, the coins, the hidden coins found of how many (web sbHud)
func readout() -> Array:
	var f := found()
	return [title, int(save.get("c", 0)), int(f[0]), int(f[1])]
