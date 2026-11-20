extends Node
## The cinematic finish on CR_MAP: drives a few seconds, starts it, and saves each of its three shots to
## build/fin/<map>_<tag>_<a|b|c>.png (FIN_TAG names the run).
var main: Node


func _ready() -> void:
	main = load("res://scenes/main.tscn").instantiate()
	add_child(main)
	for i in 30:
		await get_tree().process_frame
	main.menu.visible = false
	main.state = "race"
	main.race.state = "race"
	main.cd = 0.0
	main.kart.ai["auto"] = true
	await get_tree().create_timer(4.0).timeout
	main._fin_start()
	print("FIN on ", main.fin_on)
	var dir := ProjectSettings.globalize_path("res://build/fin")
	DirAccess.make_dir_recursive_absolute(dir)
	var tag := "%s_%s" % [OS.get_environment("CR_MAP"), OS.get_environment("FIN_TAG")]
	for sh in [["a", 1.2], ["b", 3.6], ["c", 6.6]]:
		while main.fin_on and main.fin_tt < float(sh[1]):
			await get_tree().process_frame
		var img := get_viewport().get_texture().get_image()
		img.resize(960, 540, Image.INTERPOLATE_BILINEAR)
		img.save_png("%s/%s_%s.png" % [dir, tag, sh[0]])
		print("FIN shot ", tag, " ", sh[0], " cam ", main.cam.global_position, " kart y ", main.kart.wy)
	get_tree().quit(0)
