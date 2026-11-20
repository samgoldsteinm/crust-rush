extends Node
## Prints each walker's node tree in the race view (positions, mesh bounds) for CR_MAP.
var main: Node


func _ready() -> void:
	main = load("res://scenes/main.tscn").instantiate()
	main.auto_drive = true
	add_child(main)
	for i in 30:
		await get_tree().process_frame
	var wl: Array = main.view.whaz.get("walk", [])
	print("WALK count ", wl.size())
	for e in wl.slice(0, 2):
		_dump(e["n"], 0)
	get_tree().quit(0)


func _dump(n: Node, d: int) -> void:
	var s := "  ".repeat(d) + String(n.name) + " " + n.get_class()
	if n is Node3D:
		s += " pos %s rot %s scl %s" % [(n as Node3D).position, (n as Node3D).rotation, (n as Node3D).scale]
	if n is MeshInstance3D and (n as MeshInstance3D).mesh != null:
		s += " aabb %s" % (n as MeshInstance3D).mesh.get_aabb()
	print("WALK ", s)
	for c in n.get_children():
		_dump(c, d + 1)
