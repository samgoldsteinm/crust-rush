class_name Kart
extends RefCounted
## Kart physics, ported from the web game's stepKart(). Runs at a fixed 120 Hz.
## Field names follow the web code (x, y on the ground plane; wy = height) so the two can
## be compared line by line. Items, spin-outs and the loop-the-loop are here; the race
## (other karts, item boxes, thrown items, the computer drivers) is in race.gd.
## Special abilities and shortcuts (each with its own path) are here too.

const TRICK_T := 0.55

var T: TrackData
var base_max := 170.5
var sm_spd := 1.0
var sm_acc := 1.0
var sm_hnd := 1.0
var sm_off := 0.0
var glider_sink := 15.0
var glider_air := 1.0

var x := 0.0
var y := 0.0
var a := 0.0          # facing
var ma := 0.0         # direction of motion
var speed := 0.0
var steer := 0.0
var brake := 0.0
var pen := 1.0        # off-road speed factor, eased
var acc := 0.0        # smoothed acceleration (body pitch)
var boost := 0.0
var p_boost := 0.0
var b_age := 9.0
var b_pk := 0.0
var drift := 0
var charge := 0.0
var tier := 0
var d_amt := 0.0
var d_time := 0.0
var s_t := 0.0
var d_hold := 0.0
var d_want := 0.0
var d_latch := false
var grip_t := 0.0
var air := false
var big := false
var air_t := 0.0
var glide := false
var g_h := 99.0
var g_tr := 0
var g_rings := 0          # the glide's boost rings this kart has flown through this glide (web gRings, a bit each)
var trick := false
var trick_t := 0.0
var trick_n := 0
var trick_k := 0
var wy := 0.0
var wvy := 0.0
var g_rate := 0.0
var last_g := NAN
var z := 0.0
var on_ramp := false
var on_glide := false
var idx := 0
var prog := 0
var wall_t := 0.0
var pd := false
var b_lock := false
var inv := 0.0
var finished := false
var finish_time := 0.0
var place := 0
var est := false

# who drives it
var ri := 0               # racer (character) index
var racer_name := ""
var is_player := false
var human := false        # read the stick itself (web isHuman); computer drivers get extra steering
var sm_wgt := 1.0
var ai := {}              # lane, lane_target, lane_t, skill, item_delay, in_bend
var info := {}            # roster entry: model file, stats
var peer := 0             # online: who drives it (0 = computer)
var remote := false       # online host: driven by a friend's controls
var net_inp := {"steer": 0.0, "brake": false, "nb": false, "mul": 1.0, "look": false}
var net_items: Array[String] = []
var web := false          # online host: a browser friend's kart, driven by exactly the controls they sent
var web_q: Array = []     # ...the ones to play this step: [steer, brake, nb, mul, ev, ab]

# items and hits
var item := ""
var item2 := ""
var pend: Array[String] = []
var roll := 0.0
var held := {}            # {it, sl, t} while an item trails behind
var shield := 0.0         # timed shield (old garlic)
var sh_l := 0             # garlic layers: each blocks one hit
var mz_h := 0
var abs_t := 0.0
var spin := 0.0
var frozen := 0.0
var rush := 0.0
var oil_t := 0.0
# the special ability (web useAbility / abilityTick): charge, queued volleys and what each one leaves running
var ab_c := 0.0           # 0..1, full after 30 s of racing
var ab_q: Array = []      # [[seconds left, Callable]]
var ab_wait := -1.0       # computer drivers: a short think before firing
var fire_t := 0.0         # Chili: laying fire
var fire_acc := 0.0
var mega_t := 0.0         # Shroom: giant
var flat_t := 0.0         # squashed by a Mega Shroom
var flat_imm := 0.0
var pesto_t := 0.0        # Basil: untouchable boost
var chili_t := 0.0
var olive_t := 0.0
var ab_fx := 0.0          # sparkle trail while an ability runs
var ab_col := Color.WHITE
var burn_t := 0.0         # caught fire (drawing only)
# the web's newer items (useItem2): what each one leaves running on a kart
var jal_n := 0            # Jalapeño Triple: boosts left
var mag_t := 0.0          # Pizza Magnet: reeling in
var mag_tg: Kart = null
var cut_t := 0.0          # Cutter Orbit
var cut_a := 0.0
var ghost_t := 0.0        # Ghost Pepper: untouchable, see-through
var sauce_t := 0.0        # Sauce Splat: slower, smeared view
var shrink_t := 0.0       # Heat Wave: shrunk and slower
var elim := false         # Last Slice Standing: knocked out (and on which lap)
var elim_lap := 0
var sc := -1              # on a shortcut (index into T.shorts), and where along it
var sc_i := 0
var cannon_t := 0.0       # Pizza Cannon: fired down the track
var auto_t := 0.0         # ...steering itself
var wall_hit := false
var wall_n := Vector2.ZERO  # last wall's outward normal (for the sparks)
var f_tier := 0           # which drift tier the current boost came from (flame colour)
var sf := 1.0             # the kart model's size factor (where a held item trails)

# loop-the-loop
var loop := {}            # {th, p, lat0, shift, g0, j, full} while inside the loop
var loop_th := 0.0
var o_th := 0.0

# previous step, for drawing between physics steps
var ox := 0.0
var oy := 0.0
var oa := 0.0
var oma := 0.0
var owy := 0.0
var o_loop := false

## sounds and camera shakes for the scene to play: "hop", "tier1".."tier3", "boost1".."boost3",
## "pad", "bump", "trick", "land", "respawn"
var events: Array[String] = []


func setup(track: TrackData, slot: Dictionary, start_prog: int, stats := {}) -> void:
	T = track
	base_max = T.BASE0 * T.class_mul
	var sm: Dictionary = stats.get("sm", T.stat_mods)
	sm_spd = float(sm.get("spd", 1.0))
	sm_acc = float(sm.get("acc", 1.0))
	sm_hnd = float(sm.get("hnd", 1.0))
	sm_off = float(sm.get("off", 0.0))
	sm_wgt = float(sm.get("wgt", 1.0))
	var gl: Dictionary = stats.get("glider", {})
	glider_sink = float(gl.get("sink", 15.0))
	glider_air = float(gl.get("air", 1.0))
	x = float(slot["x"])
	y = float(slot["y"])
	a = float(slot["a"])
	ma = a
	wy = float(slot["wy"])
	idx = T.nearest_any(x, y)
	last_g = T.ground(x, y) + T.k_ey(idx, x, y)
	prog = start_prog
	_save_prev()


func _save_prev() -> void:
	ox = x
	oy = y
	oa = a
	oma = ma
	owy = wy
	o_th = loop_th
	o_loop = not loop.is_empty()


static func ang_diff(p: float, q: float) -> float:
	return atan2(sin(p - q), cos(p - q))


static func _drift_boost(t: int) -> float:
	return [0.0, 0.55, 0.9, 1.3][t]


static func _drift_surge(t: int) -> float:
	return [0.0, 10.0, 15.0, 22.0][t]


static func _tier_of(c: float) -> int:
	if c > 2.6:
		return 3
	if c > 1.6:
		return 2
	if c > 0.8:
		return 1
	return 0


## inp: steer (-1..1, right positive), brake (drift/brake button held), nb (brake disabled), mul (gas: 1 or 0),
## use / back / hold / hold_sl / release for items (see race.gd)
func step(inp: Dictionary, dt: float) -> void:
	_save_prev()
	inv = maxf(0.0, inv - dt)
	if trick_t > 0.0:
		trick_t -= dt
	var brake_in: bool = inp["brake"]
	var d_press := brake_in and not pd
	pd = brake_in
	if grip_t > 0.0:
		grip_t -= dt
	if not loop.is_empty():
		_loop_step(dt)
		return

	# a tap in the air is a trick (a different one each jump); in a glide every tap with room below is one
	var trick_now := false
	var st_in: float = inp["steer"]
	if glide and d_press and air_t > 0.25 and not (trick_t > 0.0) and g_h > 16.0:
		b_lock = true
		trick = true
		g_tr += 1
		trick_t = TRICK_T
		trick_n += 1
		var tk1: int = [1, 0, 2][trick_n % 3]
		trick_k = 3 if st_in < -0.4 else (4 if st_in > 0.4 else tk1)
		trick_now = true
		events.append("trick")
	elif air and (big or (air_t > 0.12 and z > 5.0)) and not glide and d_press and not trick:
		b_lock = true
		trick = true
		trick_t = TRICK_T
		trick_n += 1
		var tk2: int = trick_n % 3
		trick_k = 3 if st_in < -0.4 else (4 if st_in > 0.4 else tk2)
		trick_now = true
		events.append("trick")

	# surface: road, kerb, grass
	var lat := absf(T.lateral(idx, x, y))
	var tp: float
	if lat < T.RW:
		tp = 1.0
	elif lat < T.CURB:
		tp = 0.86 + 0.02 * sm_off
	else:
		tp = clampf(0.58 + 0.06 * sm_off, 0.4, 0.82)
	if glide:
		tp = 1.0
	if sc >= 0:
		tp = 1.0 if bool(T.shorts[sc]["route"]) else 0.96
	if boost > 0.0:
		tp = maxf(tp, 0.93)
	pen += (tp - pen) * minf(1.0, dt * (3.5 if tp < pen else 6.0))

	var mul: float = inp["mul"]
	var mx: float = base_max * mul * pen * sm_spd * (glider_air if glide else 1.0)
	if boost > p_boost + 1e-4:
		b_pk = boost
		f_tier = 0
	if boost > 0.0:
		b_age = (b_age + dt) if p_boost > 0.0 else 0.0
		mx *= 1.58
		boost -= dt
	else:
		b_age = 9.0
	p_boost = boost
	if d_want > 0.0:
		d_want -= dt
	if shield > 0.0:
		shield -= dt
		mx *= 1.08
	if abs_t > 0.0:
		abs_t -= dt
	if rush > 0.0:
		rush -= dt
		if not (pesto_t > 0.0):
			mx *= 1.12
		pen = maxf(pen, 0.95)
	if oil_t > 0.0:
		oil_t -= dt
	if cannon_t > 0.0:
		mx *= 1.22
	if shrink_t > 0.0:
		mx *= 0.78
	if sauce_t > 0.0:
		mx *= 0.93
	if frozen > 0.0:
		frozen -= dt
		mx *= 0.55
	if flat_t > 0.0:
		mx = minf(mx * 0.6, base_max * mul * pen * sm_spd * 0.6)

	# Pizza Cannon: the kart steers itself down the road (web autoT)
	if auto_t > 0.0:
		auto_t -= dt
		if spin <= 0.0:
			var latc := T.lateral(idx, x, y)
			var q := (idx + 14) % T.N
			var tx := T.px[q] + T.nx[q] * latc * 0.6
			var ty := T.py[q] + T.ny[q] * latc * 0.6
			var dd := ang_diff(atan2(ty - y, tx - x), a)
			a += dd * minf(1.0, dt * 7.0)
			ma = a
			drift = 0
			charge = 0.0
			d_latch = false
			d_want = 0.0
			steer = 0.0
			inp = inp.duplicate()
			inp["steer"] = 0.0
			inp["brake"] = false
	var v0 := speed
	if spin > 0.0:
		spin -= dt
		var os := oil_t > Race.SLICK_T     # Olive's slick: a much faster spin that slides on further
		a += (26.0 if os else 14.0) * dt
		speed += (0.0 - speed) * minf(1.0, (1.1 if os else 2.5) * dt)
		if spin <= 0.0:
			spin = 0.0
			a = ma
		brake = 0.0
	else:
		_drive(inp, dt, brake_in, d_press, trick_now, mx)

	acc += ((speed - v0) / dt - acc) * minf(1.0, dt * 6.0)
	x += cos(ma) * speed * dt
	y += sin(ma) * speed * dt
	_sc_step()

	_walls()
	if wall_t > 0.0:
		wall_t -= dt
	_rim()
	if _vertical(dt):
		return
	_obstacles()

	# items: fire, keep behind, or let go of what trails behind
	if not held.is_empty():
		held["t"] = float(held["t"]) + dt
	if race != null:
		var rel = inp.get("release")
		if rel != null and not held.is_empty() and spin <= 0.0:
			race.release_held(self, rel == "back")
		elif inp.get("hold", false) and item != "" and spin <= 0.0:
			if not race.hold_item(self, int(inp.get("hold_sl", 1))):
				race.use_item(self, true)
		elif inp.get("use", false) and item != "" and spin <= 0.0:
			race.use_item(self, bool(inp.get("back", false)))
	if roll > 0.0:
		roll -= dt
		if roll <= 0.0:
			while not pend.is_empty():
				var it: String = pend.pop_front()
				if item == "":
					item = it
				elif item2 == "" and held.is_empty():
					item2 = it
			if race != null:
				race.after_roll(self)
			events.append("ready")

	# progress round the lap (on a shortcut, its own path keeps the count)
	var o_idx := idx
	var best := T.nearest(idx, x, y) if sc < 0 else idx
	var di := best - idx
	if di > T.N / 2:
		di -= T.N
	if di < -T.N / 2:
		di += T.N
	prog += di
	idx = best

	_loop_walls_and_entry(o_idx)

	for p in T.pads:
		var dj: int = idx - int(p["j"])
		if dj > T.N / 2:
			dj -= T.N
		if dj < -T.N / 2:
			dj += T.N
		if absi(dj) <= 2 and absf(T.lateral(idx, x, y) - float(p["lat"])) < float(p["w"]) and boost < 0.9:
			boost = maxf(boost, 1.0)
			events.append("pad")


var race = null   # the Race this kart is in (items need it)


## steering, braking, accelerating and drifting: everything a kart does while it isn't spinning out
func _drive(inp: Dictionary, dt: float, brake_in: bool, d_press: bool, trick_now: bool, mx: float) -> void:
	var st_in: float = inp["steer"]
	var rate := 5.0 if st_in == 0.0 else (7.0 if steer != 0.0 and signf(st_in) != signf(steer) else 3.2)
	steer += clampf(st_in - steer, -rate * dt, rate * dt)
	if not brake_in:
		b_lock = false
	if d_press and not air and absf(speed) > 55.0:
		b_lock = true
	var nb: bool = inp.get("nb", false)
	var want_brake := 1.0 if (brake_in and not nb and drift == 0 and not b_lock and not air and not glide) else 0.0
	brake += (want_brake - brake) * minf(1.0, dt * 9.0)
	if brake > 0.04:
		if speed > 2.0:
			speed -= 200.0 * brake * dt
		else:
			speed = maxf(-55.0, speed - 100.0 * brake * dt)
	elif speed < mx:
		var f := 1.0 - 0.72 * (clampf(speed / mx, 0.0, 1.0) if mx > 0.0 else 1.0)
		speed = minf(mx, speed + (T.ACCEL * sm_acc * (2.8 if boost > 0.0 else 1.0) * f + (220.0 if speed < 0.0 else 0.0)) * dt)
	else:
		speed += (mx - speed) * minf(1.0, dt * 1.5)
	if not air:
		var ca := cos(ma)
		var sa := sin(ma)
		var sl := (T.ground(x + ca * 5.0, y + sa * 5.0) - T.ground(x - ca * 5.0, y - sa * 5.0)) / 10.0
		speed -= sl * 165.0 * dt

	var sp := absf(speed)
	var dir := (-1.0 if speed < 0.0 else 1.0) * (0.35 if (air and big) else 1.0)
	var hs := clampf((sp - 40.0) / (base_max - 40.0), 0.0, 1.0)
	var lo := 0.0 if sp < 1.0 else minf(1.0, sp / 35.0)
	var over := clampf((sp - base_max) / (base_max * 0.58), 0.0, 1.0)
	var tf_n: float = lo * (1.0 - 0.52 * hs) * (1.0 if human else 1.4) * sm_hnd * (1.0 + 0.4 * over)
	var tf_d: float = lo * (1.0 - 0.38 * hs) * 1.02 * sm_hnd * (1.0 + 0.55 * over)

	# drift: tap to hop and slide; let go (or straighten) to fire the mini-turbo
	var d_rel := false
	if spin > 0.0:
		d_latch = false
	if d_press and air and drift == 0:
		if not trick_now and not (glide and g_h > 16.0):
			d_latch = not d_latch
			d_want = 0.0
	elif d_press and drift != 0 and not air:
		d_rel = true
	else:
		if d_press and drift == 0:
			d_want = 0.6
		if d_want > 0.0 and brake_in:
			d_want = maxf(d_want, 0.12)
		if d_latch and drift == 0 and not air:
			if sp > 40.0:
				d_latch = false
				d_want = 0.0
				_start_drift(0.35)
			elif sp < 30.0:
				d_latch = false
		if d_want > 0.0 and drift == 0 and not air and sp > 55.0 and not (not human and boost > 0.0 and b_age < 0.8):
			d_want = 0.0
			_start_drift(0.0)
			air = true
			big = false
			air_t = 0.0
			wvy = g_rate + 18.0
	if drift != 0 and not d_rel:
		d_time += dt
		if brake_in:
			d_hold += dt
		var sl2 := absf(ang_diff(a, ma))
		var st_abs := absf(st_in if human else steer)
		var up := human and not brake_in and d_hold > 0.35 and not air
		if d_time > (0.0 if up else (0.3 if human else 0.45)) and st_abs < (0.6 if up else (0.15 if human else 0.3)) and (human or sl2 < 0.14):
			s_t += dt
			if s_t > (0.016 if up else ((0.5 if brake_in else 0.3) if human else 0.3)):
				d_rel = true
		else:
			s_t = 0.0
	if drift != 0:
		if d_rel or sp < 35.0:
			var tr := _tier_of(charge)
			if tr > 0:
				boost = maxf(boost, _drift_boost(tr))
				speed = maxf(speed, minf(speed + _drift_surge(tr), base_max * sm_spd * 1.45))
				p_boost = boost
				b_age = 9.0
				b_pk = boost
				f_tier = tr
				events.append("boost%d" % tr)
			drift = 0
			charge = 0.0
			grip_t = 0.25
		else:
			d_amt = minf(1.0, d_amt + dt * 1.75)
			var da := d_amt * d_amt * (3.0 - 2.0 * d_amt)
			a += steer * T.TURN * (tf_n + (tf_d - tf_n) * da) * dt * dir
			speed -= 3.0 * dt
			charge += dt * (0.5 + absf(steer)) * (0.35 + 0.65 * da) * (0.0 if s_t > 0.0 else 1.0)
			var tr2 := _tier_of(charge)
			if tr2 > tier:
				tier = tr2
				events.append("tier%d" % tr2)
	else:
		a += steer * T.TURN * tf_n * dt * dir
	# the direction of motion follows the facing, slower while drifting
	var da2 := d_amt * d_amt * (3.0 - 2.0 * d_amt)
	var follow := (9.0 - 5.0 * da2) if drift != 0 else (7.0 if grip_t > 0.0 else 9.0)
	# slick tyres after Olive's spin: the path follows where the kart points far more slowly, and it can slide much wider
	var slk := oil_t > 0.0 and oil_t <= Race.SLICK_T
	ma += ang_diff(a, ma) * minf(1.0, follow * (0.2 if slk else 1.0) * dt)
	var slip := ang_diff(a, ma)
	var smax := 1.1 if slk else 0.5
	if absf(slip) > smax:
		ma = a - signf(slip) * smax


# ---------------------------------------------------------------- loop-the-loop

const LOOPR := 56.0

func _loop_step(dt: float) -> void:
	var L := loop
	speed = maxf(speed, base_max * 1.18)
	L["th"] = float(L["th"]) + speed * dt / LOOPR
	var th := minf(float(L["th"]), TAU)
	var p: Dictionary = L["p"]
	var sx := LOOPR * sin(th)
	var hg := LOOPR * (1.0 - cos(th))
	var lat := float(L["lat0"]) + float(L["shift"]) * th / TAU
	x = float(p["x"]) + float(p["tx"]) * sx + float(p["nx"]) * lat
	y = float(p["y"]) + float(p["ty"]) * sx + float(p["ny"]) * lat
	wy = float(L["g0"]) + hg + 0.35
	z = hg
	loop_th = th
	a = float(p["ang"])
	ma = a
	drift = 0
	steer *= 0.9
	air = false
	if float(L["th"]) >= TAU:
		if bool(L["full"]):
			var di := int(L["j"]) - idx
			if di > T.N / 2:
				di -= T.N
			if di < -T.N / 2:
				di += T.N
			prog += di
			idx = int(L["j"])
		loop = {}
		loop_th = 0.0
		o_th = 0.0
		boost = maxf(boost, 1.5)
		wvy = 0.0
		g_rate = 0.0
		last_g = T.ground(x, y) + T.k_ey(idx, x, y)
		wy = last_g
		z = 0.0
		events.append("loopout")


## the divider between the way into a loop and the way out, and getting carried into the loop
func _loop_walls_and_entry(o_idx: int) -> void:
	for L in T.loops:
		if not bool(L["full"]) or not loop.is_empty():
			continue
		var P: Dictionary = L["p"]
		var al := (x - float(P["x"])) * float(P["tx"]) + (y - float(P["y"])) * float(P["ty"])
		var aa := absf(al)
		if aa > T.LOOP_DIV + T.LOOP_TAP:
			continue
		var hw := T.LOOP_DH if aa <= T.LOOP_DIV else T.LOOP_DH * (1.0 - (aa - T.LOOP_DIV) / T.LOOP_TAP)
		var lim := hw + 4.0
		var lt := (x - float(P["x"])) * float(P["nx"]) + (y - float(P["y"])) * float(P["ny"])
		if absf(lt) >= lim:
			continue
		var dj := int(L["j"]) - idx
		if dj > T.N / 2:
			dj -= T.N
		if dj < -T.N / 2:
			dj += T.N
		var sd := -1.0 if dj > 0 else 1.0
		var push := sd * lim - lt
		x += float(P["nx"]) * push
		y += float(P["ny"]) * push
		var tl := 0.0 if aa <= T.LOOP_DIV else (T.LOOP_DH / T.LOOP_TAP) * signf(al)
		var ex := float(P["nx"]) * sd + float(P["tx"]) * tl
		var ey_ := float(P["ny"]) * sd + float(P["ty"]) * tl
		var el := sqrt(ex * ex + ey_ * ey_)
		_slide(-ex / el, -ey_ / el, 0.22, 0.5)
	for L in T.loops:
		if not loop.is_empty() or not bool(L["full"]):
			continue
		var dj2 := int(L["j"]) - idx
		if dj2 > T.N / 2:
			dj2 -= T.N
		if dj2 < -T.N / 2:
			dj2 += T.N
		if dj2 >= 1 and dj2 <= 8:
			var P2: Dictionary = L["p"]
			var al2 := (x - float(P2["x"])) * float(P2["tx"]) + (y - float(P2["y"])) * float(P2["ty"])
			var lt2 := (x - float(P2["x"])) * float(P2["nx"]) + (y - float(P2["y"])) * float(P2["ny"])
			if al2 >= -1.0:
				var S := float(L["S"])
				var W := float(L["W"])
				loop = {"th": 0.0, "p": P2, "lat0": clampf(lt2, -S - W + 5.0, -S + W - 5.0), "shift": float(L["shift"]), "g0": float(L["g0"]), "j": int(L["j"]), "full": true}
				drift = 0
				spin = 0.0
				air = false
				big = false
				glide = false
				events.append("loopin")
	for L in T.loops:
		if bool(L["full"]) or air or speed <= 50.0 or spin > 0.0 or not loop.is_empty():
			continue
		var d0 := o_idx - int(L["j"])
		var d1 := idx - int(L["j"])
		if d0 > T.N / 2:
			d0 -= T.N
		if d0 < -T.N / 2:
			d0 += T.N
		if d1 > T.N / 2:
			d1 -= T.N
		if d1 < -T.N / 2:
			d1 += T.N
		if d0 < 0 and d1 >= 0:
			var lt3 := T.lateral(idx, x, y)
			if absf(lt3 - float(L["lat0"])) < 17.0:
				loop = {"th": 0.0, "p": L["p"], "lat0": float(L["lat0"]), "shift": float(L["shift"]), "g0": float(L["g0"]), "j": int(L["j"]), "full": false}
				drift = 0
				events.append("loopin")


func _start_drift(amt: float) -> void:
	drift = 1
	charge = 0.0
	d_amt = amt
	tier = 0
	d_time = 0.0
	s_t = 0.0
	d_hold = 0.0
	events.append("hop")


func _slide(nx_: float, ny_: float, keep: float, turn: float) -> void:
	var vx := cos(ma)
	var vy := sin(ma)
	var dot := vx * nx_ + vy * ny_
	if dot <= 0.0:
		return
	speed *= 1.0 - keep * dot
	var tx_ := vx - dot * nx_
	var ty_ := vy - dot * ny_
	if Vector2(tx_, ty_).length() > 0.05:
		var na := atan2(ty_, tx_)
		ma = na
		a += ang_diff(na, a) * turn
	if dot > 0.45 and wall_t <= 0.0:
		wall_t = 0.35
		wall_n = Vector2(nx_, ny_)
		events.append("wall")


## the side walls, the pond's edge and a bridge's lateral limits
func _walls() -> void:
	var j := idx
	var lt := T.lateral(j, x, y)
	var sg := -1 if lt < 0.0 else 1
	var lim: float
	if T.wall[j] == sg:
		lim = T.CURB + 7.0
	elif T.pond[j] == sg:
		lim = T.pond_lim
	else:
		lim = T.WALLD - 3.5
	if T.open[j] == 0 and not glide and sc < 0 and lt * sg > lim and not _sc_mouth(sg, lt) and not (air and _sc_over(8.0)[0] >= 0):
		var ov := lt * sg - lim
		var nx_ := T.nx[j] * sg
		var ny_ := T.ny[j] * sg
		x -= nx_ * ov
		y -= ny_ * ov
		_slide(nx_, ny_, 0.22, 0.5)
	if not is_nan(T.flo[j]) and not glide:
		var lt2 := T.lateral(j, x, y)
		var ov2 := 0.0
		var sg2 := 0
		if lt2 < T.flo[j]:
			ov2 = T.flo[j] - lt2
			sg2 = -1
		elif lt2 > T.fhi[j]:
			ov2 = lt2 - T.fhi[j]
			sg2 = 1
		if ov2 > 0.0:
			var nx2 := T.nx[j] * sg2
			var ny2 := T.ny[j] * sg2
			x -= nx2 * ov2
			y -= ny2 * ov2
			_slide(nx2, ny2, 0.15, 0.5)


## near a shortcut's mouth on this side the main wall is open (web: SHORTS.some(...) in the wall check)
func _sc_mouth(sg: int, lt: float) -> bool:
	for c in T.shorts:
		if int(c["s"]) != sg:
			continue
		var rt := bool(c["route"])
		if lt * sg >= T.WALLD + (70.0 if rt else 30.0):
			continue
		var d := absi(idx - int(c["a"])) % T.N
		if mini(d, T.N - d) <= (8 if rt else 3):
			return true
	return false


## which shortcut point the kart is over: [shortcut, point] or [-1, -1] (web scOver)
func _sc_over(pad: float) -> Array:
	for ci in T.shorts.size():
		var c: Dictionary = T.shorts[ci]
		var sw := float(c["w"]) + pad
		for i in range(1, int(c["n"]) - 1):
			var px_: float = c["x"][i]
			var py_: float = c["y"][i]
			var off := (x - px_) * float(c["nx"][i]) + (y - py_) * float(c["ny"][i])
			if absf(off) > sw:
				continue
			var al := (x - px_) * float(c["tx"][i]) + (y - py_) * float(c["ty"][i])
			if absf(al) < 10.0:
				return [ci, i]
	return [-1, -1]


## karts on a shortcut follow its own path for progress and walls; others may turn into one (web scStep)
func _sc_step() -> void:
	if T.shorts.is_empty():
		return
	if sc >= 0:
		var c: Dictionary = T.shorts[sc]
		var n := int(c["n"])
		var bi := sc_i
		var bd := 1e18
		for i in range(maxi(0, sc_i - 3), mini(n - 1, sc_i + 6) + 1):
			var dd := (float(c["x"][i]) - x) ** 2 + (float(c["y"][i]) - y) ** 2
			if dd < bd:
				bd = dd
				bi = i
		sc_i = bi
		var px_: float = c["x"][bi]
		var py_: float = c["y"][bi]
		var along := (x - px_) * float(c["tx"][bi]) + (y - py_) * float(c["ty"][bi])
		var off := (x - px_) * float(c["nx"][bi]) + (y - py_) * float(c["ny"][bi])
		var span := (int(c["b"]) - int(c["a"]) + T.N) % T.N
		var nidx := (int(c["a"]) + int(round(float(bi) / float(n - 1) * span))) % T.N
		var di := nidx - idx
		if di > T.N / 2:
			di -= T.N
		if di < -T.N / 2:
			di += T.N
		prog += di
		idx = nidx
		var w := float(c["w"])
		if (bi >= n - 1 and along > 0.0) or (bi >= n - 3 and absf(off) > w - 4.0):
			sc = -1
			idx = int(c["b"])
			return
		if bi <= 2 and (along < -2.0 or absf(off) > w + 2.0):
			sc = -1
			idx = int(c["a"])
			return
		var lim := w - 3.5
		if absf(off) > lim and bi > 2 and bi < n - 3:
			var sg := signf(off)
			var ov := absf(off) - lim
			var nx_ := float(c["nx"][bi]) * sg
			var ny_ := float(c["ny"][bi]) * sg
			x -= nx_ * ov
			y -= ny_ * ov
			var vx := cos(ma)
			var vy := sin(ma)
			var dot := vx * nx_ + vy * ny_
			if dot > 0.0:
				speed *= 1.0 - 0.2 * dot
				var tx_ := vx - dot * nx_
				var ty_ := vy - dot * ny_
				if Vector2(tx_, ty_).length() > 0.05:
					var na := atan2(ty_, tx_)
					ma = na
					a += ang_diff(na, a) * 0.5
		return
	for ci in T.shorts.size():
		var c2: Dictionary = T.shorts[ci]
		var dj := idx - int(c2["a"])
		if dj > T.N / 2:
			dj -= T.N
		if dj < -T.N / 2:
			dj += T.N
		if absi(dj) > 9:
			continue
		var rt := bool(c2["route"])
		var lat := T.lateral(idx, x, y) * int(c2["s"])
		var mouth := absi(dj) <= (8 if rt else 4) and lat > T.WALLD - (40.0 if rt else 16.0)
		var w2 := float(c2["w"])
		for i in mini(8, int(c2["n"])):
			var px2: float = c2["x"][i]
			var py2: float = c2["y"][i]
			var off2 := (x - px2) * float(c2["nx"][i]) + (y - py2) * float(c2["ny"][i])
			var al2 := (x - px2) * float(c2["tx"][i]) + (y - py2) * float(c2["ty"][i])
			if ((absf(off2) < w2 - 1.0 and absf(al2) < 9.0) or (mouth and absf(off2) < w2 + 4.0 and absf(al2) < 12.0)) and cos(ma) * float(c2["tx"][i]) + sin(ma) * float(c2["ty"][i]) > -0.1:
				sc = ci
				sc_i = i
				events.append("sc" if rt else "sc_new")
				return
	# a jump that comes down on a shortcut (past its mouth) joins it there
	var lt3 := absf(T.lateral(idx, x, y))
	if lt3 > T.WALLD - 8.0 or air:
		var h := _sc_over(-1.0)
		if int(h[0]) >= 0 and int(h[1]) > 2:
			sc = int(h[0])
			sc_i = int(h[1])
			events.append("sc" if bool(T.shorts[sc]["route"]) else "sc_new")


func _rim() -> void:
	var d := Vector2(x, y).length()
	if d > T.RIM:
		var nx_ := x / d
		var ny_ := y / d
		x = nx_ * T.RIM
		y = ny_ * T.RIM
		_slide(nx_, ny_, 0.35, 0.6)


## ground, kerbs, ramps, jumps and the glide. Returns true if the kart was respawned.
func _vertical(dt: float) -> bool:
	var g := T.ground(x, y) + T.k_ey(idx, x, y)
	var on_r := false
	var g_r := false
	if not T.in_glide(idx):
		var la := absf(T.lateral(idx, x, y))
		if la > T.RW and la < T.CURB:
			g += T.kerb_h(la)
	for r in T.ramps:
		var al := -1.0
		var rl := 0.0
		var run := 0.0
		var fx := 0.0
		var fy := 0.0
		var j0 := int(r["j"])
		for q in 4:
			var ia := (j0 + q) % T.N
			var ib := (j0 + q + 1) % T.N
			var seg := Vector2(T.px[ib] - T.px[ia], T.py[ib] - T.py[ia])
			var sl := seg.length()
			if sl == 0.0:
				sl = 1.0
			var ux := seg.x / sl
			var uy := seg.y / sl
			var dx := x - T.px[ia]
			var dy := y - T.py[ia]
			var u := dx * ux + dy * uy
			if u >= (-0.5 if q > 0 else -7.0) and u <= sl + (7.0 if q == 3 else 0.5):
				al = run + u
				rl = dx * -uy + dy * ux
				fx = ux
				fy = uy
				break
			run += sl
		var rlen: float = r["len"]
		var rw: float = r["w"]
		var rh: float = r["h"]
		if al < -6.0 or al > rlen + 6.0 or absf(rl) > rw + 7.0:
			continue
		var hh := rh * clampf(al, 0.0, rlen) / rlen
		var fwd := cos(ma) * fx + sin(ma) * fy
		if al >= 0.0 and al <= rlen and (wy >= g + hh - 0.8 or (wy >= g + hh - 2.5 and fwd > 0.5 and absf(rl) <= rw + 2.0)):
			if wy <= g + hh + 1.5:
				g += hh
				on_r = true
				g_r = bool(r["glide"])
			continue
		# the ramp is a solid wedge: from the sides or the back it's a wall
		if al < 0.0 or wy >= g + hh - 0.8 or glide:
			continue
		var to_back := rlen + 6.0 - al
		var to_side := rw + 7.0 - absf(rl)
		var sd := signf(rl) if rl != 0.0 else 1.0
		var nx2: float
		var ny2: float
		if to_back < to_side:
			x += fx * to_back
			y += fy * to_back
			nx2 = fx
			ny2 = fy
		else:
			x += -fy * sd * to_side
			y += fx * sd * to_side
			nx2 = -fy * sd
			ny2 = fx * sd
		_slide(-nx2, -ny2, 0.22, 0.5)

	var rate := (g - (g if is_nan(last_g) else last_g)) / dt
	last_g = g
	if air and not glide and on_glide and not g_r and speed > 20.0:
		_start_glide()
		wvy = maxf(30.0, wvy)
	# leaving a ramp always launches, even mid drift-hop
	if on_ramp and not on_r and speed > 20.0 and air and not big and not glide and z < 4.0:
		air = false
	if air:
		air_t += dt
		if glide:
			wvy -= 70.0 * dt
			var sk := -glider_sink
			if wvy < sk:
				wvy += (sk - wvy) * minf(1.0, dt * 4.0)
			var gyy := T.glide_y(x, y)
			if g < gyy - 20.0 and wy < gyy + 6.0 and wvy < 0.0:
				wvy *= 0.8
			if race != null:
				race.glide_rings(self)
			g_h = wy - maxf(g, gyy)
		else:
			wvy -= ((80.0 if wvy > 0.0 else 110.0) if big else 260.0) * dt
		wy += wvy * dt
		if wy <= g:
			wy = g
			air = false
			if big or glide:
				_land()
			big = false
			glide = false
			wvy = rate
			g_rate = rate
	elif on_ramp and not on_r and speed > 20.0:
		air = true
		big = true
		air_t = 0.0
		wvy = 32.0 + minf(maxf(0.0, speed), base_max * 1.6) * 0.05
		speed = maxf(speed, base_max * 0.9)
		trick = false
		drift = 0
		if on_glide:
			_start_glide()
		wy += wvy * dt
	elif rate < g_rate - 260.0 * dt * 1.1 and speed > 60.0:
		air = true
		big = (g_rate - rate) > 55.0
		air_t = 0.0
		wvy = minf(g_rate, 42.0)
		wy += wvy * dt
	else:
		wy = g
		g_rate = rate
	on_ramp = on_r
	on_glide = g_r
	z = maxf(0.0, wy - g)
	if not T.glide.is_empty() and wy < T.glide_y(x, y) - 32.0 and T.pit(x, y) > 25.0:
		respawn()
		return true
	return false


func _start_glide() -> void:
	air = true
	glide = true
	big = false
	trick = false
	drift = 0
	speed = maxf(speed, base_max * 0.85)
	wvy = 55.0 + speed * 0.08
	g_tr = 0
	g_rings = 0
	g_h = 99.0
	if race != null and race.player == self:
		race.rings_snap()


func _land() -> void:
	var tr := trick
	var gt := g_tr
	trick = false
	g_tr = 0
	if tr:
		boost = maxf(boost, minf(1.6, 0.8 + 0.25 * (gt - 1)) if gt > 1 else 0.8)
		events.append("boost1")
	else:
		events.append("land")


func _obstacles() -> void:
	for o in T.obstacles:
		var dx: float = x - float(o["x"])
		var dy: float = y - float(o["y"])
		var rr: float = float(o["r"]) + 8.5
		var d2 := dx * dx + dy * dy
		if d2 < rr * rr and z < float(o["h"]):
			var dd := sqrt(d2)
			if dd == 0.0:
				dd = 0.01
			var nx_ := dx / dd
			var ny_ := dy / dd
			x = float(o["x"]) + nx_ * rr
			y = float(o["y"]) + ny_ * rr
			var vx := cos(ma)
			var vy := sin(ma)
			var dot := vx * nx_ + vy * ny_
			if dot < 0.0:
				speed *= 1.0 + 0.5 * dot
				var tx_ := vx - dot * nx_
				var ty_ := vy - dot * ny_
				if Vector2(tx_, ty_).length() > 0.05:
					var na := atan2(ty_, tx_)
					ma = na
					a += ang_diff(na, a) * 0.6
				if -dot > 0.3:
					events.append("bump")


## back to the start of the glide after falling into the gap
func respawn() -> void:
	sc = -1
	var j := (int(T.glide["rj"]) - 24 + T.N) % T.N
	var di := j - idx
	if di > T.N / 2:
		di -= T.N
	if di < -T.N / 2:
		di += T.N
	prog += di
	idx = j
	x = T.px[j]
	y = T.py[j]
	a = T.ang[j]
	ma = a
	speed = base_max * 0.5
	wy = T.ground(x, y) + T.ey[j]
	last_g = wy
	wvy = 0.0
	g_rate = 0.0
	air = false
	big = false
	glide = false
	on_ramp = false
	on_glide = false
	drift = 0
	charge = 0.0
	boost = 0.0
	spin = 0.0
	inv = 3.0
	z = 0.0
	_save_prev()
	events.append("respawn")


func lap() -> int:
	return clampi(int(floor(maxf(0.0, prog) / T.N)) + 1, 1, T.LAPS)
