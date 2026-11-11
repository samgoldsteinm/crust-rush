class_name TrackData
extends RefCounted
## A track exported from the web game: centre line, walls, ramps, boost pads, obstacles,
## start grid and height maps. Physics uses the web game's coordinates: x and y on the
## ground plane (Godot's x and z) and a separate height (Godot's y), so the numbers in
## kart.gd match the web version one for one.

var id := ""
var title := ""
var N := 0
var R := 0.0
var RIM := 0.0
var RW := 0.0
var CURB := 0.0
var WALLD := 0.0
var KS := 1.76
var BASE0 := 170.5
var ACCEL := 110.0
var TURN := 2.2
var LAPS := 3
var KERB_H := 0.45
var class_mul := 1.0
var pond_lim := 0.0
var multi := false        # roads stacked on several levels (decks): height comes from the road, not the ground

# centre line, one entry per track point
var px := PackedFloat32Array()
var py := PackedFloat32Array()
var nx := PackedFloat32Array()
var ny := PackedFloat32Array()
var tx := PackedFloat32Array()
var ty := PackedFloat32Array()
var ang := PackedFloat32Array()
var wall := PackedInt32Array()
var pond := PackedInt32Array()
var open := PackedInt32Array()
var ey := PackedFloat32Array()
var flo := PackedFloat32Array()   # NAN when the point has no lateral floor limits
var fhi := PackedFloat32Array()

var ramps: Array = []      # {j, len, h, w, glide}
var pads: Array = []       # {j, lat, w}
var obstacles: Array = []  # {x, y, r, h}
var grid: Array = []       # {x, y, a, wy, player}
var grid_prog: Array = []
var glide := {}            # {j0, j1, rj, long, p, ux, uy, L, y, rings: [[x, y, z, yaw]]} or empty
var sets := {}             # set pieces the PC builds itself, from the export: {pagoda: [[x, z, yaw]]}
var shorts: Array = []     # shortcuts: {a, b, s, route, w, n, x, y, tx, ty, nx, ny}
var stat_mods := {}        # the player's kart multipliers: spd, acc, hnd, wgt, off
var light := {}
var sky := {}

# the race: item boxes, loop-the-loops, obstacle lanes (for the computer drivers)
var L := 0.0                 # track length
var boxes: Array = []        # {x, y, gy, dbl, air}
var obst_lane: Array = []    # {j, lat, r} per obstacle, for the computer drivers to steer round
var loops: Array = []        # {j, full, lat0, W, S, shift, g0, p: {x, y, tx, ty, nx, ny, ang}}
var LOOP_DIV := 150.0
var LOOP_DH := 14.0
var LOOP_TAP := 150.0
var racers: Array = []       # {name, color, stripe}
var diffs := {}
var haz := {}                # moving hazards: traffic, rollers, walk, train (web HAZ, rollers)
var theme := "bay"
var props := {}            # trees, palms, bushes, rocks: {kinds: {key: {base, P, N, C, ...}}, items: {key: [...]}}
var grade := {}              # the web's colour grade for this theme: sat, con, tint, vig, bloom, thr
var rim := {}                # rim light colour and strength

# height maps on a square grid
var hx0 := 0.0
var hz0 := 0.0
var hstep := 10.0
var hn := 0
var heights := PackedFloat32Array()
var glide_h := PackedFloat32Array()   # -1e9 where there is no glide floor
var pits := PackedFloat32Array()


static func load_from(path: String) -> TrackData:
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null:
		push_error("Track data missing: %s" % path)
		return null
	var d: Dictionary = JSON.parse_string(f.get_as_text())
	var t := TrackData.new()
	t._read(d)
	return t


func _read(d: Dictionary) -> void:
	# shortcuts and side routes: their own path (web SHORTS), when the export has it
	shorts.clear()
	for c in d.get("shortsD", []):
		var cd: Dictionary = c
		if not cd.has("pts"):
			continue
		var sc := {"a": int(cd["a"]), "b": int(cd["b"]), "s": int(cd["s"]), "route": bool(cd.get("route", false)), "w": float(cd.get("w", 19.0))}
		var cols := [PackedFloat32Array(), PackedFloat32Array(), PackedFloat32Array(), PackedFloat32Array(), PackedFloat32Array(), PackedFloat32Array()]
		for q in cd["pts"]:
			for k in 6:
				var arr: PackedFloat32Array = cols[k]
				arr.append(float(q[k]))
				cols[k] = arr   # packed arrays are values: put the grown one back
		for k in 6:
			sc[["x", "y", "tx", "ty", "nx", "ny"][k]] = cols[k]
		sc["n"] = (cols[0] as PackedFloat32Array).size()
		if int(sc["n"]) < 4:
			continue
		shorts.append(sc)
	id = d["map"]
	title = d["name"]
	N = int(d["N"])
	R = d["R"]
	RIM = d["RIM"]
	RW = d["RW"]
	CURB = d["CURB"]
	WALLD = d["WALLD"]
	KS = d["KS"]
	BASE0 = d["BASE0"]
	ACCEL = d["ACCEL"]
	TURN = d["TURN"]
	LAPS = int(d["LAPS"])
	KERB_H = d["KERB_H"]
	class_mul = d["classMul"]
	multi = bool(d.get("multi", false))
	pond_lim = d["pondLim"] if d.get("pondLim") != null else WALLD - 3.5
	for p in d["track"]:
		px.append(p[0]); py.append(p[1]); nx.append(p[2]); ny.append(p[3])
		tx.append(p[4]); ty.append(p[5]); ang.append(p[6])
		wall.append(int(p[7])); pond.append(int(p[8])); open.append(int(p[9]))
		ey.append(p[10])
		flo.append(NAN if p[11] == null else p[11])
		fhi.append(NAN if p[12] == null else p[12])
	ramps = d["ramps"]
	pads = d["pads"]
	obstacles = d["obstacles"]
	grid = d["grid"]
	grid_prog = d.get("gridProg", [])
	glide = d["glide"] if d.get("glide") != null else {}
	sets = d["sets"] if d.get("sets") is Dictionary else {}
	stat_mods = d["statMods"] if d.get("statMods") != null else {"spd": 1.0, "acc": 1.0, "hnd": 1.0, "wgt": 1.0, "off": 0.0}
	light = d["light"]
	sky = d["sky"] if d.get("sky") != null else {}
	var rc = d.get("race")
	if rc != null:
		var r: Dictionary = rc
		L = float(r["L"])
		boxes = r["boxes"]
		loops = r["loops"]
		var lk: Dictionary = r["loopK"]
		LOOP_DIV = float(lk["DIV"])
		LOOP_DH = float(lk["DH"])
		LOOP_TAP = float(lk["TAP"])
		racers = r["racers"]
		diffs = r["diffs"]
		for o in r["obstacles"]:
			var od: Dictionary = o
			if od.get("j") != null and od.get("lat") != null:
				obst_lane.append({"j": int(od["j"]), "lat": float(od["lat"]), "r": float(od["r"])})
	if L <= 0.0:
		for i in N:
			var k := (i + 1) % N
			L += Vector2(px[k] - px[i], py[k] - py[i]).length()
	if d.get("haz") != null:
		haz = d["haz"]
	theme = String(d.get("theme", "bay"))
	props = d.get("props", {})
	if d.get("grade") != null:
		grade = d["grade"]
	if d.get("rim") != null:
		rim = d["rim"]
	var h: Dictionary = d["height"]
	hx0 = h["x0"]
	hz0 = h["z0"]
	hstep = h["step"]
	hn = int(h["n"])
	heights = _grid(h["b64"], 1.0 / float(h["scale"]), -INF)
	if not glide.is_empty() and glide.get("gy") != null:
		glide_h = _grid(glide["gy"], 1.0 / 20.0, -32768)
	if d.get("pit") != null:
		pits = _grid(d["pit"], 1.0 / 20.0, -INF)


## int16 grid (base64) → floats; `missing` marks cells with no value (→ -1e9)
func _grid(b64: String, scale: float, missing: float) -> PackedFloat32Array:
	var raw := Marshalls.base64_to_raw(b64)
	var out := PackedFloat32Array()
	out.resize(raw.size() / 2)
	for i in out.size():
		var v := raw.decode_s16(i * 2)
		out[i] = -1e9 if (missing != -INF and v == int(missing)) else v * scale
	return out


func _sample(arr: PackedFloat32Array, x: float, y: float) -> float:
	if arr.is_empty():
		return 0.0
	var fx := (x - hx0) / hstep
	var fy := (y - hz0) / hstep
	var i := int(floor(fx))
	var j := int(floor(fy))
	if i < 0 or j < 0 or i >= hn - 1 or j >= hn - 1:
		return 0.0
	var u := fx - i
	var v := fy - j
	var a := arr[j * hn + i]
	var b := arr[j * hn + i + 1]
	var c := arr[(j + 1) * hn + i]
	var e := arr[(j + 1) * hn + i + 1]
	if a < -1e8 or b < -1e8 or c < -1e8 or e < -1e8:
		return -1e9
	return lerpf(lerpf(a, b, u), lerpf(c, e, u), v)


## the web game's groundAt(x, y)
func ground(x: float, y: float) -> float:
	return _sample(heights, x, y)


func glide_y(x: float, y: float) -> float:
	if glide_h.is_empty():
		return -1e9
	return _sample(glide_h, x, y)


func pit(x: float, y: float) -> float:
	return _sample(pits, x, y)


## web kEy/eyAt: on a multi-level map, the road deck's height under (x, y) near point j (smooth between points)
func k_ey(j0: int, x: float, y: float) -> float:
	if not multi:
		return 0.0
	var j := j0
	for it in 3:
		var q := (j + 1) % N
		var ux := px[q] - px[j]
		var uy := py[q] - py[j]
		var l2 := ux * ux + uy * uy
		var t := ((x - px[j]) * ux + (y - py[j]) * uy) / (l2 if l2 > 0.0 else 1.0)
		if t > 1.0 and it < 2:
			j = (j + 1) % N
			continue
		if t < 0.0 and it < 2:
			j = (j - 1 + N) % N
			continue
		return ey_at(j, clampf(t, 0.0, 1.0))
	return ey[j0]


func ey_at(j: int, t: float) -> float:
	var e0 := ey[(j - 1 + N) % N]
	var e1 := ey[j]
	var e2 := ey[(j + 1) % N]
	var e3 := ey[(j + 2) % N]
	var t2 := t * t
	var t3 := t2 * t
	return 0.5 * (2.0 * e1 + (-e0 + e2) * t + (2.0 * e0 - 5.0 * e1 + 4.0 * e2 - e3) * t2 + (-e0 + 3.0 * e1 - 3.0 * e2 + e3) * t3)


func lateral(j: int, x: float, y: float) -> float:
	return (x - px[j]) * nx[j] + (y - py[j]) * ny[j]


## nearest centre-line point, searching from `from` like the web game (-12..+20)
func nearest(from: int, x: float, y: float) -> int:
	var best := from
	var bd := INF
	for o in range(-12, 21):
		var j := (from + o + N) % N
		var dd := (px[j] - x) * (px[j] - x) + (py[j] - y) * (py[j] - y)
		if dd < bd:
			bd = dd
			best = j
	return best


## full search, for placing a kart anywhere
func nearest_any(x: float, y: float) -> int:
	var best := 0
	var bd := INF
	for j in N:
		var dd := (px[j] - x) * (px[j] - x) + (py[j] - y) * (py[j] - y)
		if dd < bd:
			bd = dd
			best = j
	return best


## the raised kerb's height across its width
func kerb_h(la: float) -> float:
	var u := la - RW
	if u < 0.6:
		return KERB_H * u / 0.6
	if u < 6.5:
		return KERB_H * (1.0 - 0.25 * (u - 0.6) / 5.9)
	return KERB_H * 0.75 + (0.05 - KERB_H * 0.75) * (u - 6.5) / (CURB - RW - 6.5)


## a point s track-points along the centre line (fractions allowed), lat to the side (web trackAt)
func track_at(s: float, lat: float) -> Vector3:
	var i := int(floorf(fposmod(s, float(N))))
	var f: float = s - floorf(s)
	var q := (i + 1) % N
	var xx: float = px[i] + (px[q] - px[i]) * f
	var yy: float = py[i] + (py[q] - py[i]) * f
	var nxx: float = nx[i] + (nx[q] - nx[i]) * f
	var nyy: float = ny[i] + (ny[q] - ny[i]) * f
	return Vector3(xx + nxx * lat, yy + nyy * lat, float(i))


## the heading of the centre line at s (web lerpA between points)
func ang_at(s: float) -> float:
	var i := int(floorf(fposmod(s, float(N))))
	var f: float = s - floorf(s)
	return lerp_angle(ang[i], ang[(i + 1) % N], f)


## web loopNear / segBad: stretches where traffic hides (open sides, near loops, the glide)
func loop_near(j: int, g: int) -> bool:
	for L in loops:
		var d := absi(j - int(L["j"])) % N
		if mini(d, N - d) < g + (100 if bool(L["full"]) else 0):
			return true
	return false


func seg_bad(j0: int) -> bool:
	var j := posmod(j0, N)
	if open[j] != 0:
		return true
	if loop_near(j, 26):
		return true
	if not glide.is_empty() and j > int(glide["rj"]) - 8 and j < int(glide["j1"]) + 8:
		return true
	return false


func in_glide(j: int) -> bool:
	return not glide.is_empty() and j >= int(glide["j0"]) and j < int(glide["j1"])
