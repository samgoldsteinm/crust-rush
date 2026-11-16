extends Node
## Races without items on the PC (web v209, patch 47): every item switched off -> a race has no item boxes (race.noitm, boxes empty);
## items back on -> boxes again; the room's race settings carry the host's choice ("ni"); PROTO 116. Prints NOITEMS PASS / FAIL.

var main: Node


func _ready() -> void:
	main = load("res://scenes/main.tscn").instantiate()
	add_child(main)
	for i in 40:
		await get_tree().process_frame
	var bad := 0
	main.sel["cpus"] = 2
	main.sel["mode"] = "single"
	main.gp = {}
	for it in main.ITEM_NAMES:
		main.item_set[it] = false
	main.state = "menu"
	await main._race_on(main.map_id)
	var a := [main.race.noitm, main.race.boxes.size(), main.T.boxes.size()]
	print("NOITEMS all off: noitm %s, boxes %d of %d" % a)
	if not (a[0] and a[1] == 0 and a[2] > 0):
		bad += 1
	var c: Dictionary = main.web._build_cfg(0)
	print("NOITEMS room settings ni = %s, PROTO %d" % [c.get("ni"), WebNet.PROTO])
	if c.get("ni") != true or WebNet.PROTO != 116:
		bad += 1
	main._to_menu("")
	for i in 10:
		await get_tree().process_frame
	main.item_set.clear()
	main.state = "menu"
	await main._race_on(main.map_id)
	var b := [main.race.noitm, main.race.boxes.size()]
	print("NOITEMS items on: noitm %s, boxes %d" % b)
	if b[0] or b[1] == 0:
		bad += 1
	print("NOITEMS %s" % ("PASS" if bad == 0 else "FAIL"))
	get_tree().quit(0 if bad == 0 else 1)
