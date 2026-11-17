extends Node
## Sandbox coins on the PC (web patch 61): the detailed coin from assets/sandbox/coin.json, and a shadow under each coin.
## CR_MODE=sb CR_MAP=margherita; with a window it also takes a picture (build/menu/sbcoin.png). Also the mission medallions (web patch 63). Prints SBCOIN PASS / FAIL.

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
	var sb = main.race.sb
	var v = main.sb_view
	var r := {"coins": sb.coin_n, "tris": v._mm.mesh.get_faces().size() / 3, "shadows": v._shm.instance_count if v._shm != null else 0, "medallions": v._meds.size(), "missions": sb.acts.marks.size(), "rare": v._rare.size()}
	# a plain coin, the camera held close beside it
	var ci := -1
	for i in sb.coin_n:
		if sb.coin_rare[i] == 0:
			ci = i
			if i >= 9:
				break
	var c := Vector3(sb.coin_x[ci], sb.coin_y[ci], sb.coin_z[ci])
	sb.save["t"] = 0.5
	var cam := Camera3D.new()
	cam.fov = 60.0
	main.add_child(cam)
	cam.global_position = c + Vector3(16, 4, 9.6)
	cam.look_at(c - Vector3(0, 1.5, 0))
	cam.make_current()
	for i in 60:
		await get_tree().process_frame
	if DisplayServer.get_name() != "headless":
		get_viewport().get_texture().get_image().save_png(ProjectSettings.globalize_path("res://build/menu/sbcoin.png"))
	var ok: bool = r["tris"] > 1000 and r["shadows"] == sb.coin_n and r["medallions"] == r["missions"]
	print("SBCOIN %s %s" % ["PASS" if ok else "FAIL", JSON.stringify(r)])
	get_tree().quit()
