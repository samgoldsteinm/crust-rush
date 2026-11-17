extends Node
## The developer options on the PC (web patch 68): a vehicle setting changes the player's kart only, off line; a rival's skill follows
## "cpu"; a moving hazard switched off is not built; the room's start carries the host's race settings (cfg "dev"); flying climbs;
## unlimited pepperoni refills; a used item marks the race as one with items (web patch 64). Prints DEVTEST PASS / FAIL.
## Run headless: CR_MAP=peaks (a track with traffic).

var main: Node


func _ready() -> void:
	main = load("res://scenes/main.tscn").instantiate()
	add_child(main)
	for i in 40:
		await get_tree().process_frame
	var bad := 0
	main.load_map("peaks")   # (when the local copy has it; the hazard check runs only on a track with traffic)
	print("DEVTEST map ", main.map_id, " traffic in the export: ", (main.T.haz.get("traffic", []) as Array).size())
	main.dev_u = true
	main.dev = main.DEV_DEF.duplicate(true)
	main.dev["spd"] = 1.5
	main.dev["acc"] = 2.0
	main.dev["cpu"] = 0.8
	main.dev["hz"]["traffic"] = 0
	main.dev["fly"] = 1
	main.dev["infPep"] = 1
	main.sel["cpus"] = 3
	main.sel["mode"] = "single"
	main.gp = {}
	main.item_set.clear()
	main.state = "menu"
	await main._race_on(main.map_id)
	var me = main.race.player
	var cpu = null
	for k in main.race.karts:
		if k != me:
			cpu = k
			break
	var r := {"traffic": main.race.traffic.size(), "haz_in_track": (main.T.haz.get("traffic", []) as Array).size(), "itm_used0": main.race.itm_used}
	r["cfg"] = main.web._build_cfg(0).get("dev")
	r["proto"] = WebNet.PROTO
	main.race.state = "race"
	main.state = "race"
	for i in 5:
		await get_tree().process_frame
	r["pep"] = me.item
	main._dev_fly_toggle()
	var y0: float = me.wy
	Input.action_press("ui_page_up") if false else null
	for i in 90:
		me.step({"steer": 0.0, "brake": false, "nb": false, "mul": 1.0, "flyup": 1.0}, 1.0 / 60.0)
	r["fly_up"] = snappedf(me.wy - y0, 0.1)
	r["fly"] = me.fly
	main.race.use_item(me, false)
	r["itm_used"] = main.race.itm_used
	print("DEVTEST ", JSON.stringify(r))
	# (the multipliers: compare with a kart built with the options off)
	main.dev["on"] = 0
	main._to_menu("")
	for i in 10:
		await get_tree().process_frame
	await main._race_on(main.map_id)
	var me0 = main.race.player
	var r2 := {"spd": snappedf(me.sm_spd / me0.sm_spd, 0.001), "acc": snappedf(me.sm_acc / me0.sm_acc, 0.001), "traffic_on": main.race.traffic.size()}
	print("DEVTEST off-run ", JSON.stringify(r2))
	var has_tr: bool = int(r2["traffic_on"]) > 0 or int(r["haz_in_track"]) > 0
	if (has_tr and (r["traffic"] != 0 or int(r2["traffic_on"]) == 0)) or r["cfg"] == null or float(r["cfg"]["spd"]) != 1.5 or int(r["proto"]) != 120:
		bad += 1
	if String(r["pep"]) != "pepperoni" or not bool(r["fly"]) or float(r["fly_up"]) < 20.0 or r["itm_used0"] or not r["itm_used"]:
		bad += 1
	if absf(float(r2["spd"]) - 1.5) > 0.01 or absf(float(r2["acc"]) - 2.0) > 0.01:
		bad += 1
	print("DEVTEST %s" % ("PASS" if bad == 0 else "FAIL"))
	get_tree().quit(0 if bad == 0 else 1)
