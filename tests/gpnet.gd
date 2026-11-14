extends Node
## A Grand Prix on line, the PC's bookkeeping (web: tools/mini/patch28.py, netGpNow). No network: the cup arrives as the host's
## settings would bring it, a race is started with two players on the same racer and six computer racers, and the cup's table
## is worked out from the standings. Wants: the cup read whole from the wire form and written back the same; each player's
## points under the player, each computer racer's under the racer; eight rows; nothing added to the cup until the host goes on.
## Prints GPNET PASS / FAIL.

func _ready() -> void:
	var main: Node = load("res://scenes/main.tscn").instantiate()
	main.auto_drive = true
	add_child(main)
	var bad := 0
	var wire := {"cup": 0, "race": 1, "pts": [3, 0, 6, 0, 10, 0, 12, 15], "last": [0, 0, 0, 0, 0, 0, 0, 0], "np": {"0": 8, "1": 1}}
	main.gp = main._gp_from_wire(wire)
	var back = main.gp_wire()
	var ok1: bool = back != null and int(back["cup"]) == 0 and int(back["race"]) == 1 and (back["pts"] as Array) == wire["pts"] and int(back["np"]["0"]) == 8 and int(back["np"]["1"]) == 1 and not (main.gp["tracks"] as Array).is_empty()
	print("GPNET wire in and out: ", ok1, " ", back)
	bad += 0 if ok1 else 1
	# a race as a room would have it: the host (peer 1) and a friend (peer 2) both on racer 0
	var slots: Array = []
	var ris := [3, 4, 5, 0, 0, 6, 7, 1]
	for s in 8:
		slots.append({"ri": ris[s], "peer": 1 if s == 4 else (2 if s == 3 else 0), "own": s == 4, "build": main._my_build(), "name": "A" if s == 4 else ("B" if s == 3 else "")})
	main._start_race({"seed": 1, "slots": slots, "cls": "medium"})
	main.gp = main._gp_from_wire(wire)
	var now: Dictionary = main._gp_net_now()
	var rows: Array = now["rows"]
	var st: Array = main.race.standings()
	var humans := 0
	var sum_ok := true
	for i in st.size():
		var k: Kart = st[i]
		var pt: int = Race.PTS[i] if i < Race.PTS.size() else 0
		if k.peer > 0:
			humans += 1
			sum_ok = sum_ok and int(now["np"][str(k.peer - 1)]) == int(wire["np"][str(k.peer - 1)]) + pt
		else:
			sum_ok = sum_ok and int(now["pts"][k.ri]) == int(wire["pts"][k.ri]) + pt
	var untouched: bool = (main.gp["pts"] as Array) == wire["pts"] and int(main.gp["np"]["0"]) == 8
	var ok2: bool = rows.size() == 8 and humans == 2 and sum_ok and untouched and int(now["pts"][0]) == int(wire["pts"][0])
	print("GPNET table: rows ", rows.size(), " players ", humans, " sums ", sum_ok, " cup untouched ", untouched, " np ", now["np"], " pts ", now["pts"])
	bad += 0 if ok2 else 1
	print("GPNET PASS" if bad == 0 else "GPNET FAIL")
	get_tree().quit(0 if bad == 0 else 1)
