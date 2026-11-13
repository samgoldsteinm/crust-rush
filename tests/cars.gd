extends Node
## Each body named in CR_BODIES ("skywing,megagt,..."; default: the six cars added with web v173) in the garage,
## to build/menu/car_<id>.png. Optional CR_LIV=<web livery id>.
## A body the garage export does not hold is reported as "CARS missing <id>" (run the garage export first).

var main: Node
var ids: PackedStringArray
var i := -1
var wait := 12


func _ready() -> void:
	main = load("res://scenes/main.tscn").instantiate()
	add_child(main)
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path("res://build/menu"))
	var e := OS.get_environment("CR_BODIES")
	ids = (e if e != "" else "skywing,megagt,megawatt,endur,slip,retrogt").split(",")


func _process(_dt: float) -> void:
	if wait > 0:
		wait -= 1
		return
	if i >= 0 and i < ids.size():
		get_viewport().get_texture().get_image().save_png(ProjectSettings.globalize_path("res://build/menu/car_%s.png" % ids[i]))
		print("CARS shot ", ids[i])
	i += 1
	if i >= ids.size():
		get_tree().quit(0)
		return
	var bodies: Array = KartBuilder.info.get("bodies", [])
	var bi := -1
	for k in bodies.size():
		if String(bodies[k]["id"]) == ids[i]:
			bi = k
	if bi < 0:
		print("CARS missing ", ids[i])
		wait = 1
		return
	main.menu.build["b"] = bi
	main.menu.build["w"] = 0
	main.menu.build["t"] = OS.get_environment("CR_LIV")
	main.menu.g_tab = "car"
	main.menu.open("garage")
	wait = 40
