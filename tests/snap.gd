extends Node
## One picture of a race a few seconds in: CR_MAP=<id> [CR_SNAP_T=seconds] [CR_SNAP_OUT=path] <godot> --path . --resolution 1280x720 res://tests/snap.tscn
## (not headless: it draws). Used to check how bright a track looks.

func _ready() -> void:
	var main: Node = load("res://scenes/main.tscn").instantiate()
	main.auto_drive = true
	add_child(main)
	var t := float(OS.get_environment("CR_SNAP_T")) if OS.get_environment("CR_SNAP_T") != "" else 9.0
	var out := OS.get_environment("CR_SNAP_OUT") if OS.get_environment("CR_SNAP_OUT") != "" else "D:/crust-rush/scratch/snap.png"
	await get_tree().create_timer(t).timeout
	await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_png(out)
	print("SNAP saved ", out, " map ", main.map_id)
	get_tree().quit()
