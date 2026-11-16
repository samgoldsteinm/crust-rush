extends Node
## Sandbox's item boxes on the PC: the kart is set down on each box (at the height Sandbox gives it there) and the race steps once;
## every box must be taken. The owner, 2026-11-16, on the PC in Sandbox on the kitchen track: "I couldn't pick these item boxes up".
## CR_MAP=kitchen CR_MODE=sb <godot> --headless --path . res://tests/sbbox.tscn   ->  "SBBOX PASS"

const DT := 1.0 / 120.0


func _ready() -> void:
	var main: Node = load("res://scenes/main.tscn").instantiate()
	main.auto_drive = true
	main.test_hold = true
	add_child(main)
	await get_tree().process_frame
	var race: Race = main.race
	var sb = race.sb
	if sb == null:
		print("SBBOX FAIL not in Sandbox")
		get_tree().quit(1)
		return
	var k: Kart = race.player
	var T: TrackData = main.T
	var got := 0
	var lines := []
	for b in race.boxes:
		if bool(b["air"]):
			continue
		b["r"] = 0.0
		k.box_t = 0.0
		k.x = float(b["x"])
		k.y = float(b["y"])
		k.wy = sb.ground(k.x, k.y, float(b["gy"]) + 3.0)
		k.speed = 0.0
		k._save_prev()
		main.state = "race"
		race.state = "race"
		k.ai["auto"] = false
		race.update(DT, {"steer": 0.0, "brake": false, "nb": false, "mul": 0.0, "use": false, "back": false, "hold": false, "hold_sl": 1, "release": null})
		race.fx.clear()
		k.events.clear()
		var ok := float(b["r"]) > 0.0
		got += 1 if ok else 0
		lines.append("gy %d wy %d %s" % [roundi(float(b["gy"])), roundi(k.wy), "taken" if ok else "NOT taken"])
	print("SBBOX ", T.multi, " ", ", ".join(lines))
	# then the real way: driven along the track at speed through every box (from 60 units before it, held on the track's heading)
	var dgot := 0
	var dn := 0
	var dl := []
	for b in race.boxes:
		if bool(b["air"]):
			continue
		dn += 1
		for q in race.boxes:
			q["r"] = 0.0
		k.box_t = 0.0
		var bj := T.nearest_any(float(b["x"]), float(b["y"]))
		var a := 0.0
		if bj >= 0:
			a = float(T.ang[bj])
		k.x = float(b["x"]) - cos(a) * 60.0
		k.y = float(b["y"]) - sin(a) * 60.0
		k.a = a
		k.ma = a
		k.wy = sb.ground(k.x, k.y, float(b["gy"]) + 6.0)
		k.speed = 150.0
		k.spin = 0.0
		k._save_prev()
		var took := false
		for i in 120:
			k.a = a
			k.ma = a
			race.update(DT, {"steer": 0.0, "brake": false, "nb": false, "mul": 1.0, "use": false, "back": false, "hold": false, "hold_sl": 1, "release": null})
			race.fx.clear()
			k.events.clear()
			if float(b["r"]) > 0.0:
				took = true
				break
		dgot += 1 if took else 0
		dl.append("%s wy %d" % ["taken" if took else "MISSED", roundi(k.wy)])
	print("SBBOX driven: ", ", ".join(dl))
	got = got if dgot == dn else -1
	var pass_ := got == lines.size() and got > 0
	print("SBBOX %s %d of %d" % ["PASS" if pass_ else "FAIL", got, lines.size()])
	get_tree().quit(0 if pass_ else 1)
