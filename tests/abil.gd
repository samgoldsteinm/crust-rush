extends Node
## The drivers' specials after web patch 37 (online 113), the same checks as the web's tools/neon/abiltest.py:
## the Spiky Shockwave's reach (150), what it spares (in the air, blinking after a hit), what it pops without a spin (a shield, garlic),
## that it still goes through an ability boost; a held item stops a sure anchovy; MEGA_T 4.5, FLAT_T 2; Olive's slick reach (16.5 now
## catches); a storm slice's first bounce turns toward a racer ahead (at most .5 rad); webnet PROTO 113.
## CR_MAP=margherita godot --headless --path . res://tests/abil.tscn   ->  "ABIL PASS"

func _ready() -> void:
	var main: Node = load("res://scenes/main.tscn").instantiate()
	main.auto_drive = true
	add_child(main)
	await get_tree().process_frame
	var T: TrackData = main.T
	var race: Race = main.race
	var ok := true
	for i in 12:
		main._sim_tick(1.0 / 120.0)
	var P: Kart = race.karts[0]
	var O: Array = race.karts.slice(1)
	var clr := func(k: Kart) -> void:
		k.shield = 0.0
		k.mz_h = 0
		k.sh_l = 0
		k.inv = 0.0
		k.air = false
		k.glide = false
		k.spin = 0.0
		k.pesto_t = 0.0
		k.rush = 0.0
		k.abs_t = 0.0
		k.held = {}
		k.ghost_t = 0.0
		k.mega_t = 0.0
		k.chili_t = 0.0
		k.olive_t = 0.0
		k.oil_t = 0.0
	clr.call(P)
	#ANCHOVY
	# the Shockwave
	var cases := [["plain 100", 100.0, true], ["plain 200", 200.0, false], ["Mozz shield", 100.0, false], ["in the air", 100.0, false],
		["blinking", 100.0, false], ["Pesto Rush", 100.0, true], ["garlic", 100.0, false]]
	for i in cases.size():
		var k: Kart = O[i]
		clr.call(k)
		k.x = P.x + float(cases[i][1])
		k.y = P.y
	O[2].shield = 7.0
	O[2].mz_h = 3
	O[3].air = true
	O[4].inv = 2.0
	O[5].pesto_t = 3.0
	O[5].rush = 3.0
	O[6].sh_l = 2
	race.blast(P.x, P.y, 150.0, P, "pep", true)
	var line := []
	for i in cases.size():
		var k: Kart = O[i]
		var spun := k.spin > 0.0
		line.append("%s %s" % [cases[i][0], "spun" if spun else "not spun"])
		ok = ok and spun == bool(cases[i][2])
	ok = ok and O[2].shield == 0.0 and O[6].sh_l == 0
	print("ABIL shockwave: ", ", ".join(line), "; shield left %s, garlic left %d" % [O[2].shield, O[6].sh_l])
	# a sure anchovy: a held item stops it, without one it hits (two karts on the grid, before the Shockwave moves them)
	for held in [true, false]:
		var tg: Kart = race.karts[3] if held else race.karts[5]
		clr.call(tg)
		if held:
			tg.held = {"it": "oil", "sl": 1, "t": 0.0}
		race.projectiles.clear()
		var p: Dictionary = race._proj(P, "torp", tg.x + 2.0, tg.y, 0.0, 0.0, 600.0, 0.0)
		p["target"] = tg
		p["sure"] = true
		race._projectiles(1.0 / 120.0)
		var gone := race.projectiles.is_empty()
		print("ABIL anchovy, %s: used up %s, kart spun %s, held item left %s" % ["holding an item" if held else "no item", gone, tg.spin > 0.0, not tg.held.is_empty()])
		ok = ok and gone and (tg.spin <= 0.0 if held else tg.spin > 0.0) and tg.held.is_empty()
	race.projectiles.clear()
	# constants and the online version
	var proto: int = load("res://scripts/webnet.gd").PROTO
	print("ABIL MEGA_T %.1f FLAT_T %.1f PROTO %d" % [Race.MEGA_T, Race.FLAT_T, proto])
	ok = ok and Race.MEGA_T == 4.5 and Race.FLAT_T == 2.0 and proto == 113
	# Olive's slick reaches 16.5
	race.hazards.clear()
	var ot: Kart = O[1]
	clr.call(ot)
	ot.x = O[1].x
	ot.wy = T.ground(ot.x, ot.y) + T.k_ey(ot.idx, ot.x, ot.y)
	race.hazards.append({"id": 9201, "x": ot.x + 16.5, "y": ot.y, "t": 1.0e9, "born": 1.0, "owner": P, "armed": true, "olive": true})
	race._hazards(1.0 / 120.0)
	print("ABIL slick at 16.5: caught %s" % (ot.oil_t > 0.0))
	ok = ok and ot.oil_t > 0.0
	# Pep's first bounce
	var D: Kart = O[3]
	clr.call(D)
	var s := {"x": P.x + 5000.0, "y": P.y + 5000.0, "vx": 400.0, "vy": 0.0, "owner": P}
	D.x = float(s["x"]) + 300.0
	D.y = float(s["y"]) + 100.0
	race._pep_aim(s)
	var turned := atan2(float(s["vy"]), float(s["vx"]))
	print("ABIL storm slice turned %.1f degrees, speed %.1f" % [rad_to_deg(turned), Vector2(float(s["vx"]), float(s["vy"])).length()])
	ok = ok and turned > 0.0 and turned <= 0.5001 and absf(Vector2(float(s["vx"]), float(s["vy"])).length() - 400.0) < 1e-3
	print("ABIL PASS" if ok else "ABIL FAIL")
	get_tree().quit()
