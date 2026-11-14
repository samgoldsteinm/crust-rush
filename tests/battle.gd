extends Node
## Headless test of Balloon Battle (scripts/battle.gd): starts a battle on the arena with the computer driving every kart
## (the player's too), runs the whole three minutes and checks what the web's own test checks (tools/neon/bbtest.py there):
## it reaches the results; balloons are popped at a sane rate; no kart sits in one place for more than a few seconds;
## nobody falls through the world or ends below the table; only the battle's five items are ever held.
## Prints "BATTLE PASS" or "BATTLE FAIL" with the numbers.
## Two counts, because they are easy to confuse: the POINTS on the table at the end (what the web's test prints, and what
## the web's plan calls "15 to 38 pops a round": every kart that loses all its balloons loses half its points, so this is
## far fewer than the hits) and the POPS that really happened. The web game itself, run the same way with eight computer
## drivers (its build of 2026-11-14, two rounds): 108 and 116 pops, 29 and 34 points left, 290 and 307 boxes taken,
## 0 and 2 karts over the edge, longest still 2 and 4 s. The PC should land in the same place.
## Run: CR_MAP=preptable CR_MODE=bb CR_HD=0 <godot console> --headless --path . --fixed-fps 120 res://tests/battle.tscn

const MAX_T := 215.0      # 3.2 s countdown + 180 s + 2.4 s to the results, and room to spare
const POPS_MIN := 50      # balloons popped in the round
const POPS_MAX := 180
const SCORE_MIN := 12     # points on the table at the end
const SCORE_MAX := 60
const STUCK_MAX := 6      # seconds in one place (the computer's drivers set themselves down again after four or five; the web's test sees 2 to 4)
var main: Node
var steps := 0
var race_steps := 0
var next_print := 0.0
var pops := 0
var points := 0
var falls := 0
var outs := 0
var nan := 0
var under := 0
var max_stuck := 0
var stuck_who := ""
var max_proj := 0
var prev_bal := {}
var prev_s := {}
var was_out := {}
var was_low := {}
var last_p := {}
var stuck := {}
var held := {}


func _ready() -> void:
	main = load("res://scenes/main.tscn").instantiate()
	main.auto_drive = true
	add_child(main)
	var T: TrackData = main.T
	var race: Race = main.race
	print("BATTLE start: map %s, T.battle %s, mode '%s', %d karts, %d boxes, %d shapes, %d spawn places, clock %d s" % [
		main.map_id, str(T.battle), race.mode, race.karts.size(), race.boxes.size(), (T.bb.get("shapes", []) as Array).size(),
		(T.bb.get("spawn", []) as Array).size(), int(race.bb.TIME) if race.bb != null else -1])


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
	for k: Kart in race.karts:
		var pb := int(prev_bal.get(k, k.bal))
		if k.bal < pb:
			pops += pb - k.bal
		prev_bal[k] = k.bal
		var ps := int(prev_s.get(k, 0))
		if k.bb_s > ps:
			points += k.bb_s - ps
		prev_s[k] = k.bb_s
		var out := k.bb_out > 0.0
		if out and not bool(was_out.get(k, false)):
			outs += 1
		was_out[k] = out
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
		for it in k.pend:
			held[it] = true
	max_proj = maxi(max_proj, race.projectiles.size())
	# once a second of the round: who has not moved (the web's test: under 6 units in the second, and not waiting to come back)
	if race.state == "race" and not bb.over:
		race_steps += 1
		if race_steps % 120 == 0:
			for k: Kart in race.karts:
				var p := Vector2(k.x, k.y)
				var moved := p.distance_to(last_p.get(k, Vector2(1e9, 1e9)))
				last_p[k] = p
				stuck[k] = int(stuck.get(k, 0)) + 1 if (moved < 6.0 and not (k.bb_out > 0.0)) else 0
				if int(stuck[k]) > max_stuck:
					max_stuck = int(stuck[k])
					stuck_who = "%s at (%.0f, %.0f) h %.1f" % [k.racer_name, k.x, k.y, k.wy]
	if t >= next_print:
		next_print += 20.0
		var line := ""
		for k: Kart in race.karts:
			line += "%s%s %d/%d  " % [k.racer_name.substr(0, 3), "*" if k == main.kart else "", k.bb_s, k.bal]
		print("BATTLE t=%5.1f %s clock %3d | points/balloons %s| pops %d falls %d thrown %d longest still %d s" % [t, main.state, ceili(bb.t), line, pops, falls, race.projectiles.size(), max_stuck])
	if main.state == "results":
		var st := race.standings()
		var line2 := ""
		var places := {}
		var ordered := true
		var below := 0
		for i in st.size():
			var k: Kart = st[i]
			line2 += "%d %s %d pt (%d left)  " % [i + 1, k.racer_name, k.bb_s, k.bal]
			places[k.place] = true
			if not k.finished or k.place != i + 1:
				ordered = false
			if i > 0 and st[i - 1].bb_s < k.bb_s:
				ordered = false
			if k.wy < -1.0:
				below += 1
		var score := 0
		for k: Kart in race.karts:
			score += k.bb_s
		var bad_items: Array = []
		for it in held:
			if not it in ["pepperoni", "trio", "meatball", "flour", "chili"]:
				bad_items.append(it)
		print("BATTLE results: " + line2)
		print("BATTLE items held %s, used %s, spin-outs %d, boxes taken %d, most thrown at once %d" % [str(held.keys()), str(main.stats["used"]), main.stats["spins"], main.stats["boxes"], max_proj])
		var why: Array = []
		if not main.T.battle or race.mode != "bb":
			why.append("not a battle")
		if race.karts.size() != 8:
			why.append("%d karts, not 8" % race.karts.size())
		if race.boxes.size() != 16:
			why.append("%d item boxes, not 16" % race.boxes.size())
		if not bb.over or not ordered or places.size() != race.karts.size():
			why.append("the results are not in order of points")
		if pops < POPS_MIN or pops > POPS_MAX:
			why.append("%d pops is outside %d to %d" % [pops, POPS_MIN, POPS_MAX])
		if score < SCORE_MIN or score > SCORE_MAX:
			why.append("%d points left at the end is outside %d to %d" % [score, SCORE_MIN, SCORE_MAX])
		if max_stuck > STUCK_MAX:
			why.append("a kart sat still for %d s (%s)" % [max_stuck, stuck_who])
		if nan > 0:
			why.append("bad numbers")
		if under > 0:
			why.append("a kart went under the kitchen floor")
		if below > 0:
			why.append("%d kart(s) ended below the table" % below)
		if not bad_items.is_empty():
			why.append("items that do not belong in a battle: %s" % str(bad_items))
		if not main.panel_results.visible:
			why.append("no results screen")
		var ok := why.is_empty()
		print("BATTLE %s pops %d (web 108 to 116), points left at the end %d (web 15 to 38), points given %d, all-popped or off the table %d times, over the edge %d, longest still %d s, ended below the table %d, T.battle %s, karts %d, player %s with %d points%s" % [
			"PASS" if ok else "FAIL", pops, score, points, outs, falls, max_stuck, below, str(main.T.battle), race.karts.size(), main._ordinal(main.kart.place), main.kart.bb_s,
			"" if ok else " | " + "; ".join(PackedStringArray(why))])
		get_tree().quit(0 if ok else 1)
		set_physics_process(false)
	elif t > MAX_T:
		print("BATTLE FAIL no results after %d s: state %s, clock %.1f, pops %d" % [int(t), main.state, bb.t, pops])
		get_tree().quit(1)
		set_physics_process(false)
