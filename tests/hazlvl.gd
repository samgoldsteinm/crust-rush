extends Node
## A trap lies on the road it was dropped on and only catches karts on that level (multi-level tracks).
## CR_MAP=bedroom godot --headless --path . res://tests/hazlvl.tscn   ->  "HAZLVL PASS"

func _ready() -> void:
	var main: Node = load("res://scenes/main.tscn").instantiate()
	main.auto_drive = true
	add_child(main)
	await get_tree().process_frame
	var T: TrackData = main.T
	var race: Race = main.race
	if not T.multi:
		print("HAZLVL SKIP: this track has one level")
		get_tree().quit()
		return
	# the highest point of the road, a trap dropped there by a kart standing on it
	var j := 0
	for i in T.N:
		if T.ey[i] > T.ey[j]:
			j = i
	var k: Kart = race.karts[0]
	var owner := Kart.new()
	owner.x = T.px[j]
	owner.y = T.py[j]
	owner.idx = j
	var h := {"id": 9001, "x": T.px[j], "y": T.py[j], "t": 30.0, "born": 0.0, "owner": owner, "armed": true}
	var g := race.haz_ground(h)
	var want := T.ground(T.px[j], T.py[j]) + T.ey[j]
	var ok := absf(g - want) < 0.5
	k.wy = want
	var same := race.same_lvl(k, h)
	k.wy = want - T.ey[j]   # a kart on the floor straight underneath
	var under := race.same_lvl(k, h)
	# a host's copy carries the height it was drawn at
	var hn := {"id": 9002, "x": T.px[j], "y": T.py[j], "ny": want}
	var net := absf(race.haz_ground(hn) - want) < 0.01
	print("HAZLVL road height %.1f, trap drawn at %.1f, hits same level %s, hits underneath %s, host copy %s" % [want, g, same, under, net])
	print("HAZLVL PASS" if ok and same and not under and net and T.ey[j] > 30.0 else "HAZLVL FAIL")
	get_tree().quit()
