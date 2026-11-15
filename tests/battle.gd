extends Node
## Headless test of Balloon Battle (scripts/battle.gd): starts a battle on the arena with the computer driving every kart
## (the player's too), runs the whole round and checks what the web's own test checks (tools/neon/bbtest.py there), under
## the rules of the web's v197 (three sets of balloons, 5 then 3 then 1, then out; the last driver left wins; a clock of
## 300 s as a backstop):
##   how it ended (one driver left, not the clock) and the time left; the balloons popped; the order the drivers went
##   out in against the final order; that the eliminated are hidden, parked and hold nothing; that points are never
##   taken away; the longest any kart still in stood in one place; nobody under the floor or ending below the table;
##   only the battle's five items ever held; and, when the player went out, that the watching started by itself.
## With CR_BB_SKIP=1 it also presses "Skip to results" as soon as the player is being watched, and checks the rest of
## the round is played out (a real order) and the results come.
## Prints "BATTLE PASS" or "BATTLE FAIL" with the numbers.
## The web game itself, eight computer drivers on the new table (its plan, six rounds): ended by elimination with 69 to
## 158 s left, about 70 balloons popped, longest still 2 to 6 s.
## Run: CR_MAP=preptable CR_MODE=bb CR_HD=0 <godot console> --headless --path . --fixed-fps 120 res://tests/battle.tscn

const MAX_T := 325.0      # 3.2 s countdown + 300 s + 2.4 s to the results, and room to spare
const POPS_MIN := 45      # balloons popped in the round (seven drivers out is 63; the winner's own come on top)
const POPS_MAX := 72      # (eight drivers have 72 between them)
const STUCK_MAX := 6      # seconds in one place (the computer's drivers set themselves down again after four or five; the web's test sees 2 to 6)
var main: Node
var steps := 0
var race_steps := 0
var next_print := 0.0
var falls := 0
var nan := 0
var under := 0
var max_stuck := 0
var stuck_who := ""
var max_proj := 0
var lost_pts := 0         # times a kart's points went DOWN (they never may)
var prev_s := {}
var was_low := {}
var last_p := {}
var stuck := {}
var held := {}
var dead_held := 0        # steps an eliminated kart held something
var dead_seen := 0        # steps an eliminated kart was not parked off the table (the player's 1.6 s on the spot aside)
var want_skip := false
var skipped := false
var skip_left := 0        # drivers still in when Skip was pressed
var skip_clock := 0.0
var watch_late := false   # the player went out and the watching did not start
var out_at := -1.0        # when the player went out (race time)
var last_pops := 0
var last_pop_clock := 0.0 # the clock when the last balloon went


func _ready() -> void:
	want_skip = OS.get_environment("CR_BB_SKIP") == "1"
	main = load("res://scenes/main.tscn").instantiate()
	main.auto_drive = true
	add_child(main)
	var T: TrackData = main.T
	var race: Race = main.race
	print("BATTLE start: map %s, T.battle %s, mode '%s', %d karts, %d boxes, %d shapes, %d spawn places, sets %s, clock %d s, table %d x %d, export %s" % [
		main.map_id, str(T.battle), race.mode, race.karts.size(), race.boxes.size(), (T.bb.get("shapes", []) as Array).size(),
		(T.bb.get("spawn", []) as Array).size(), str(race.bb.SETS) if race.bb != null else "-", int(race.bb.TIME) if race.bb != null else -1,
		int(race.bb.X * 2.0) if race.bb != null else 0, int(race.bb.Z * 2.0) if race.bb != null else 0,
		"with the new rules' fields" if T.bb.has("sets") else "OLD (no sets, X, Z or headings: read off the shapes)"])


## balloons a kart has lost so far: the sets it has used up, and what is gone of the one it is on
func _lost(bb, k: Kart) -> int:
	var n := 0
	for i in bb.SETS.size():
		if i < k.bb_l or k.bb_dead:
			n += int(bb.SETS[i])
	if not k.bb_dead:
		n += int(bb.SETS[k.bb_l]) - k.bal
	return n


func _physics_process(dt: float) -> void:
	steps += 1
	var t := steps * dt
	var race: Race = main.race
	var bb = race.bb
	if bb == null:
		print("BATTLE FAIL this is not a battle: map %s, T.battle %s, mode '%s' (run with CR_MAP=preptable CR_MODE=bb)" % [main.map_id, str(main.T.battle), race.mode])
		get_tree().quit(1)
		set_physics_process(false)
		return
	var pops := 0
	for k: Kart in race.karts:
		pops += _lost(bb, k)
		var ps := int(prev_s.get(k, 0))
		if k.bb_s < ps:
			lost_pts += 1
		prev_s[k] = k.bb_s
		var low := k.wy < -70.0
		if low and not bool(was_low.get(k, false)):
			falls += 1
		was_low[k] = low
		if is_nan(k.x) or is_nan(k.y) or is_nan(k.wy) or is_nan(k.speed):
			nan += 1
		if k.wy < bb.FLOOR - 1.0:
			under += 1
		for it in [k.item, k.item2]:
			if it != "":
				held[it] = true
				if k.bb_dead:
					dead_held += 1
		for it in k.pend:
			held[it] = true
		if k.bb_dead and k.x < 40000.0 and not (k == main.kart and bb.ghost > 0.0) and not bb.over:
			dead_seen += 1
	max_proj = maxi(max_proj, race.projectiles.size())
	if pops != last_pops:
		last_pops = pops
		last_pop_clock = bb.t
	# the player (driven by the computer here) has gone out: after 1.6 s on the spot the watching starts by itself
	var me: Kart = main.kart
	if me.bb_dead and out_at < 0.0:
		out_at = race.race_time
	if me.bb_dead and not bb.over and main.state == "race" and race.race_time - out_at > 2.0 and not main.spec_on:
		watch_late = true
	if want_skip and not skipped and main.spec_on and not bb.over:
		skipped = true
		skip_left = bb.left
		skip_clock = bb.t
		main._spec_exit(true)   # the bar's "Skip to results"
		print("BATTLE skip pressed at t=%.1f: %d drivers still in, clock %d, watching %s, skip %s" % [t, skip_left, ceili(bb.t), main.spec_kart.racer_name if main.spec_kart != null else "nobody", str(bb.skip)])
	# once a second of the round: who has not moved (the web's test: under 6 units in the second, and not waiting to come back)
	if race.state == "race" and not bb.over and not skipped:
		race_steps += 1
		if race_steps % 120 == 0:
			for k: Kart in race.karts:
				var p := Vector2(k.x, k.y)
				var moved := p.distance_to(last_p.get(k, Vector2(1e9, 1e9)))
				last_p[k] = p
				stuck[k] = int(stuck.get(k, 0)) + 1 if (moved < 6.0 and not (k.bb_out > 0.0) and not k.bb_dead) else 0
				if int(stuck[k]) > max_stuck:
					max_stuck = int(stuck[k])
					stuck_who = "%s at (%.0f, %.0f) h %.1f" % [k.racer_name, k.x, k.y, k.wy]
	if t >= next_print:
		next_print += 20.0
		var line := ""
		for k: Kart in race.karts:
			line += "%s%s %d/%s  " % [k.racer_name.substr(0, 3), "*" if k == main.kart else "", k.bb_s, "out" if k.bb_dead else "%d+%d" % [k.bal, bb.SETS.size() - 1 - k.bb_l]]
		print("BATTLE t=%5.1f %s clock %3d left %d | points/balloons+sets to come %s| pops %d falls %d thrown %d longest still %d s" % [t, main.state, ceili(bb.t), bb.left, line, pops, falls, race.projectiles.size(), max_stuck])
	if main.state == "results":
		var st := race.standings()
		var line2 := ""
		var places := {}
		var ordered := true
		var below := 0
		var alive := 0
		var bad_dead := 0
		for i in st.size():
			var k: Kart = st[i]
			line2 += "%d %s %s  " % [i + 1, k.racer_name, bb.res_row(k)]
			places[k.place] = true
			if not k.finished or k.place != i + 1:
				ordered = false
			if i > 0:
				var p: Kart = st[i - 1]
				# drivers still in before the eliminated; among those in, by points; among the eliminated, the last out first
				if p.bb_dead and not k.bb_dead:
					ordered = false
				if not p.bb_dead and not k.bb_dead and p.bb_s < k.bb_s:
					ordered = false
				if p.bb_dead and k.bb_dead and bb.out_order.find(p) < bb.out_order.find(k):
					ordered = false
			if k.bb_dead:
				if k.bal != 0 or k.bb_l != bb.SETS.size() - 1 or not k.elim or k.item != "" or (k.x < 40000.0 and k != main.kart):
					bad_dead += 1
			else:
				alive += 1
				if k.wy < -1.0:
					below += 1
		var score := 0
		for k: Kart in race.karts:
			score += k.bb_s
		var outs := ""
		for k: Kart in bb.out_order:
			outs += k.racer_name.substr(0, 3) + " "
		var bad_items: Array = []
		for it in held:
			if not it in ["pepperoni", "trio", "meatball", "flour", "chili"]:
				bad_items.append(it)
		var new_table: bool = main.T.bb.has("sets")
		print("BATTLE results: " + line2)
		print("BATTLE went out in this order: %s| items held %s, used %s, spin-outs %d, boxes taken %d, most thrown at once %d, drivers set down again for going nowhere %d" % [outs, str(held.keys()), str(main.stats["used"]), main.stats["spins"], main.stats["boxes"], max_proj, bb.jams])
		var why: Array = []
		if not main.T.battle or race.mode != "bb":
			why.append("not a battle")
		if race.karts.size() != 8:
			why.append("%d karts, not 8" % race.karts.size())
		if race.boxes.size() != (31 if new_table else 16):
			why.append("%d item boxes, not %d" % [race.boxes.size(), 31 if new_table else 16])
		if bb.SETS != [5, 3, 1]:
			why.append("the sets are %s, not 5, 3, 1" % str(bb.SETS))
		if not bb.over or not ordered or places.size() != race.karts.size():
			why.append("the results are not in the battle's order")
		# (the clock is a backstop and a round may end on it: that is in the rules, so it passes, but it is said out loud below)
		if bb.by_time and (alive < 2 or bb.t > 0.0):
			why.append("ended on the clock with %d in and %.1f s left" % [alive, bb.t])
		elif not bb.by_time and (alive != 1 or bb.out_order.size() != race.karts.size() - 1):
			why.append("%d drivers still in at the end and %d out: not one left" % [alive, bb.out_order.size()])
		if bad_dead > 0:
			why.append("%d eliminated kart(s) with balloons, an item, or still on the table" % bad_dead)
		if dead_held > 0:
			why.append("an eliminated kart held an item")
		if dead_seen > 0:
			why.append("an eliminated kart stayed on the table (%d steps)" % dead_seen)
		if lost_pts > 0:
			why.append("points were taken away %d times (they are never halved now)" % lost_pts)
		if pops < POPS_MIN or pops > POPS_MAX:
			why.append("%d pops is outside %d to %d" % [pops, POPS_MIN, POPS_MAX])
		if score > pops:
			why.append("%d points for %d pops" % [score, pops])
		if max_stuck > STUCK_MAX:
			why.append("a kart sat still for %d s (%s)" % [max_stuck, stuck_who])
		if nan > 0:
			why.append("bad numbers")
		if under > 0:
			why.append("a kart went under the kitchen floor")
		if below > 0:
			why.append("%d kart(s) still in ended below the table" % below)
		if not bad_items.is_empty():
			why.append("items that do not belong in a battle: %s" % str(bad_items))
		if watch_late:
			why.append("the player went out and the watching did not start")
		if want_skip and not skipped:
			why.append("Skip was never pressed (the player was never out and being watched)")
		if skipped and skip_left <= 2:
			why.append("Skip was pressed with only %d left: nothing much to play out" % skip_left)
		if not main.panel_results.visible:
			why.append("no results screen")
		var ok := why.is_empty()
		if bb.by_time:
			print("BATTLE NOTE the round ran out the clock with %d drivers still in; the last balloon went with %d s left (nothing popped after that)" % [alive, ceili(last_pop_clock)])
		print("BATTLE %s ended %s with %d s left on the clock (web 69 to 158), pops %d (web about 70), points %d, over the edge %d, longest still %d s%s, ended below the table %d, player %s%s with %d points%s%s" % [
			"PASS" if ok else "FAIL", "on the clock" if bb.by_time else "with one driver left", ceili(bb.t), pops, score, falls, max_stuck,
			" (not counted after Skip)" if skipped else "", below, main._ordinal(main.kart.place), " (out)" if main.kart.bb_dead else "", main.kart.bb_s,
			(" | Skip pressed with %d in and %d s on the clock: played out to the end" % [skip_left, ceili(skip_clock)]) if skipped else "",
			"" if ok else " | " + "; ".join(PackedStringArray(why))])
		get_tree().quit(0 if ok else 1)
		set_physics_process(false)
	elif t > MAX_T:
		print("BATTLE FAIL no results after %d s: state %s, clock %.1f, left %d, pops %d" % [int(t), main.state, bb.t, bb.left, pops])
		get_tree().quit(1)
		set_physics_process(false)
