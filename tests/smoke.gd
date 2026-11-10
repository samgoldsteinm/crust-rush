extends Node
## Headless test: loads the race, lets the computer drive every kart (the player's too) for all the
## laps and prints what happens. Prints "SMOKE PASS" when the race finishes cleanly, "SMOKE FAIL" otherwise.

const MAX_T := 400.0
var main: Node
var steps := 0
var next_print := 0.0
var respawns := 0
var max_air := 0.0
var glides := 0
var was_glide := false
var jumps := 0
var was_big := false
var loops := 0
var was_loop := false
var items_held := 0
var max_proj := 0
var max_haz := 0
var sc_runs := 0
var was_sc := {}


func _ready() -> void:
	main = load("res://scenes/main.tscn").instantiate()
	main.auto_drive = true
	add_child(main)
	print("SMOKE start: %d track points, %d laps, %d ramps, %d pads, %d obstacles, %d boxes, %d loops, %d karts" % [main.T.N, main.T.LAPS, main.T.ramps.size(), main.T.pads.size(), main.T.obstacles.size(), main.race.boxes.size(), main.T.loops.size(), main.race.karts.size()])


func _physics_process(dt: float) -> void:
	steps += 1
	var t := steps * dt
	var k: Kart = main.kart
	var race: Race = main.race
	for e in k.events:
		if e == "respawn":
			respawns += 1
	if k.glide and not was_glide:
		glides += 1
	was_glide = k.glide
	if k.big and not was_big:
		jumps += 1
	was_big = k.big
	var in_loop := not k.loop.is_empty()
	if in_loop and not was_loop:
		loops += 1
	was_loop = in_loop
	max_air = maxf(max_air, k.z)
	for q in race.karts:
		var on_sc := q.sc >= 0
		if on_sc and not bool(was_sc.get(q, false)):
			sc_runs += 1
		was_sc[q] = on_sc
	max_proj = maxi(max_proj, race.projectiles.size())
	max_haz = maxi(max_haz, race.hazards.size())
	if t >= next_print:
		next_print += 15.0
		var order := ""
		for q in race.stand:
			order += "%s%s " % [q.racer_name.substr(0, 3), "*" if q == k else ""]
		print("SMOKE t=%5.1f %s pos %d lap %d prog %d speed %.0f h %.1f item '%s' | %s| proj %d slicks %d" % [t, main.state, race.position_of(k), k.lap(), k.prog, k.speed, k.wy, k.item, order, race.projectiles.size(), race.hazards.size()])
	if main.state == "results":
		var st := race.standings()
		var line := ""
		var slow := 0
		for i in st.size():
			line += "%d %s %s%.1f  " % [i + 1, st[i].racer_name, "~" if st[i].est else "", st[i].finish_time]
			if st[i].prog < main.T.N:
				slow += 1
		print("SMOKE results: " + line)
		print("SMOKE items used %s, spin-outs %d (player %d), boxes taken %d, most thrown at once %d, most slicks %d" % [str(main.stats["used"]), main.stats["spins"], main.stats["player_spins"], main.stats["boxes"], max_proj, max_haz])
		print("SMOKE abilities used %s" % str(main.stats.get("abilities", {})))
		print("SMOKE shortcut runs (all karts) %d of %d on this track" % [sc_runs, main.T.shorts.size()])
		var ok: bool = slow == 0 and int(main.stats["boxes"]) > 10 and main.stats["used"].size() >= 4 and loops >= 3 and main.stats.get("abilities", {}).size() >= 3
		print("SMOKE %s player %s in %.2f s, respawns %d, ramp jumps %d, glides %d, loops %d, highest %.1f, karts stuck on lap 1: %d" % ["PASS" if ok else "FAIL", main._ordinal(k.place), k.finish_time, respawns, jumps, glides, loops, max_air, slow])
		get_tree().quit(0 if ok else 1)
	elif t > MAX_T:
		print("SMOKE FAIL no finish after %d s: prog %d of %d, respawns %d" % [int(t), k.prog, main.T.LAPS * main.T.N, respawns])
		get_tree().quit(1)
