extends Node
## The style shop's look on the PC (web patches 65-67): a kart re-dressed with gold trim, a purple underglow and blue smoke; at night in
## Sandbox. With a window it takes build/menu/style_night.png (and closes itself). CR_MODE=sb CR_MAP=backyard. Prints STYLE PASS / FAIL.

var main: Node


func _ready() -> void:
	main = load("res://scenes/main.tscn").instantiate()
	main.auto_drive = true
	add_child(main)
	for i in 600:
		await get_tree().create_timer(0.25).timeout
		if main.state == "race" and main.race != null and main.race.sb != null and main.sb_view != null:
			break
	main.race.sb.park = true
	main.race.sb.save["t"] = 0.95
	var k = main.kart
	var spec: Dictionary = (k.info.get("spec", {}) as Dictionary).duplicate(true)
	spec["st"] = {"gl": 2, "tr": 16, "sm": 2}
	k.info["spec"] = spec
	var v0: Dictionary = main.view.views[k]
	(v0["g"] as Node).queue_free()
	main.view.views.erase(k)
	main.view.add_kart(k, main._kart_scene)
	for i in 90:
		await get_tree().process_frame
	var v: Dictionary = main.view.views[k]
	var ug: Array = v.get("ug", [])
	var r := {"lights": ug.size(), "energy": (ug[0] as OmniLight3D).light_energy if not ug.is_empty() else 0.0, "smoke": String(v.get("smc", ""))}
	var cam := Camera3D.new()
	cam.fov = 58.0
	main.add_child(cam)
	var p := Vector3(k.x, k.wy, k.y)
	var back := Vector3(-cos(k.a), 0, -sin(k.a))
	var side := Vector3(-sin(k.a), 0, cos(k.a))
	cam.global_position = p + back * 34.0 + side * 18.0 + Vector3(0, 14, 0)
	cam.look_at(p + Vector3(0, 2, 0))
	cam.make_current()
	for i in 30:
		await get_tree().process_frame
	if DisplayServer.get_name() != "headless":
		get_viewport().get_texture().get_image().save_png(ProjectSettings.globalize_path("res://build/menu/style_night.png"))
	var ok: bool = r["lights"] == 2 and float(r["energy"]) > 1.0 and r["smoke"] == "#2a6cff"
	print("STYLE %s %s" % ["PASS" if ok else "FAIL", JSON.stringify(r)])
	get_tree().quit(0 if ok else 1)
