extends Node
## Item rules that must match the web game (web v166):
## - toy tracks: item boxes come back after T.BOXR seconds and a kart takes one box of a row (T.BOXCD)
## - a homing anchovy (item and special) that reaches a kart still protected after a spin is used up, no second hit
## - Olive's slicks never catch the kart that laid them; her trail is T.SLICKN slicks long
## CR_MAP=bedroom godot --headless --path . res://tests/items.tscn   ->  "ITEMS PASS"

func _ready() -> void:
	var main: Node = load("res://scenes/main.tscn").instantiate()
	main.auto_drive = true
	add_child(main)
	await get_tree().process_frame
	var T: TrackData = main.T
	var race: Race = main.race
	var ok := true
	for i in 12:
		main._sim_tick(1.0 / 120.0)   # the karts settle on the road (their heights are worked out by the first ticks)
	print("ITEMS track numbers: TURN %.2f DRIN %.2f DROUT %.2f BOXR %.1f BOXCD %.1f SLICKN %d" % [T.TURN, T.DRIN, T.DROUT, T.BOXR, T.BOXCD, T.SLICKN])

	# an anchovy on a protected kart: used up, the kart is not spun
	var tg: Kart = race.karts[3]
	var ow: Kart = race.karts[5]
	for sure in [true, false]:
		race.projectiles.clear()
		tg.inv = 3.0
		tg.spin = 0.0
		var p: Dictionary = race._proj(ow, "torp", tg.x + 2.0, tg.y, 0.0, 0.0, 600.0, 0.0)
		p["target"] = tg
		p["sure"] = sure
		race._projectiles(1.0 / 120.0)
		var gone := race.projectiles.is_empty()
		print("ITEMS anchovy %s on a protected kart: used up %s, kart spun %s" % ["special" if sure else "item", gone, tg.spin > 0.0])
		ok = ok and gone and tg.spin <= 0.0
	tg.inv = 0.0
	race.projectiles.clear()

	# Olive's own slick: she drives over it untouched; another kart is caught
	race.hazards.clear()
	var me: Kart = race.karts[0]
	var ot: Kart = race.karts[1]
	for k in [me, ot]:
		k.wy = T.ground(k.x, k.y) + T.k_ey(k.idx, k.x, k.y)   # standing on the road (the race works this out once it is under way)
		k.inv = 0.0
		k.oil_t = 0.0
		k.spin = 0.0
	race.hazards.append({"id": 9101, "x": me.x, "y": me.y, "t": 1.0e9, "born": 1.0, "owner": me, "armed": true, "olive": true})
	race.hazards.append({"id": 9102, "x": ot.x, "y": ot.y, "t": 1.0e9, "born": 1.0, "owner": me, "armed": true, "olive": true})
	race._hazards(1.0 / 120.0)
	var own_left := false
	for h in race.hazards:
		if int(h["id"]) == 9101:
			own_left = true
	print("ITEMS own slick: owner caught %s, still there %s; another kart caught %s" % [me.oil_t > 0.0 or me.spin > 0.0, own_left, ot.oil_t > 0.0 or ot.spin > 0.0])
	ok = ok and own_left and not (me.oil_t > 0.0 or me.spin > 0.0) and (ot.oil_t > 0.0 or ot.spin > 0.0)

	if T.toy:
		ok = ok and absf(T.BOXR - 2.0) < 0.01 and absf(T.BOXCD - 0.6) < 0.01 and T.SLICKN == 7
	print("ITEMS PASS" if ok else "ITEMS FAIL")
	get_tree().quit()
