extends Node
## The mechanic's shop on the PC (web v205 patch 41; assets/shop/mshop.glb from tools/shopexport.py): the model and its door are there,
## the door rolls up as the kart comes at it, through it the pull-in plays and opens the driver screen, and the garage's way out puts the
## kart back in front of the door. CR_MODE=sb CR_MAP=garage. Prints SBSHOP PASS / FAIL.

var main: Node


func _ready() -> void:
	main = load("res://scenes/main.tscn").instantiate()
	main.auto_drive = true
	add_child(main)
	for i in 500:
		await get_tree().process_frame
		if main.state == "race" and main.race != null and main.race.sb != null and main.sb_view != null:
			break
	var V = main.sb_view
	var S: Dictionary = main.race.sb.SHOP
	var k = main.kart
	var r := {"model": V.shop_door != null}
	var ab := AABB()
	var first := true
	for m in V.find_children("*", "MeshInstance3D", true, false):
		var mi: MeshInstance3D = m
		if mi.mesh == null or mi.get_parent() == null:
			continue
		var bb: AABB = mi.global_transform * mi.get_aabb()
		if mi.get_path().get_concatenated_names().find("door") >= 0 or String(mi.get_parent().name).find("mshop") >= 0 or String(mi.name).find("shop") >= 0:
			ab = bb if first else ab.merge(bb)
			first = false
	print("SBSHOP model box %s" % str(ab))
	var nm := []
	var ps = load("res://assets/shop/mshop.glb")
	var inst: Node = ps.instantiate()
	for c in inst.find_children("*", "", true, false):
		nm.append(String(c.name) + ":" + c.get_class())
	print("SBSHOP glb nodes %s" % str(nm.slice(0, 12)))
	for c in inst.find_children("*", "MeshInstance3D", true, false):
		print("SBSHOP mesh %s aabb %s" % [c.name, str((c as MeshInstance3D).get_aabb())])
	main.race.sb.park = false
	k.x = float(S["x"])
	k.y = float(S["z"]) + float(S["d"]) / 2.0 + 30.0
	k.a = -PI / 2.0
	for i in 30:
		await get_tree().create_timer(0.1).timeout
		k.speed = 0.0
	r["door_open"] = V.shop_open
	_shot("sbshop_door")
	k.x = float(S["x"])
	k.y = float(S["z"])
	k.wy = 0.0
	for i in 30:
		await get_tree().process_frame
	r["pulling_in"] = not main.sb_cine.is_empty()
	await get_tree().create_timer(1.2).timeout
	_shot("sbshop_cine")
	for i in 60:
		await get_tree().create_timer(0.1).timeout
		if main.menu.visible and main.menu.shop:
			break
	r["driver_screen"] = main.menu.visible and main.menu.shop
	main.menu.shop_done.emit()
	for i in 300:
		await get_tree().process_frame
		if main.state == "race" and main.race != null and main.race.sb != null:
			break
	for i in 30:
		await get_tree().process_frame
	r["back_out"] = main.race != null and main.race.sb != null and main.kart.y > float(S["z"]) + float(S["d"]) / 2.0
	var ok: bool = r["model"] and r["door_open"] > 0.9 and r["pulling_in"] and r["driver_screen"] and r["back_out"]
	print("SBSHOP %s %s" % ["PASS" if ok else "FAIL", str(r)])
	get_tree().quit(0 if ok else 1)


func _shot(nm: String) -> void:
	if OS.get_environment("CR_SHOT") == "":
		return
	if main.paused:
		main._toggle_pause()
	await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_png(ProjectSettings.globalize_path("res://build/%s.png" % nm))
