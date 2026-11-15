extends RefCounted
## Where a node is in the world, whether or not it is in the scene tree.
## A place travelled to in Sandbox is built on another thread, on a world that is not in the tree yet (scripts/world_build.gd);
## Godot only answers global_transform for nodes that are in it. In the tree these give Godot's own answer, to the last
## bit, so an ordinary track load is exactly what it was; out of it they multiply the local transforms up to the root.
## Loaded by its path (no class name: a fresh checkout has no class list yet).

static func g(n: Node3D) -> Transform3D:
	if n.is_inside_tree():
		return n.global_transform
	var t := n.transform
	var p := n.get_parent()
	while p != null:
		if p is Node3D:
			t = (p as Node3D).transform * t
		p = p.get_parent()
	return t


## puts a node at a place in the world (global_position = ...)
static func set_pos(n: Node3D, at: Vector3) -> void:
	if n.is_inside_tree():
		n.global_position = at
		return
	var p := n.get_parent()
	n.position = (g(p as Node3D).affine_inverse() * at) if p is Node3D else at


## moves a node under another parent and keeps it where it is in the world (reparent(parent, true))
static func reparent_keep(n: Node3D, to: Node3D) -> void:
	if n.is_inside_tree() and to.is_inside_tree():
		n.reparent(to, true)
		return
	var gt := g(n)
	var old := n.get_parent()
	if old != null:
		old.remove_child(n)
	to.add_child(n)
	n.transform = g(to).affine_inverse() * gt


# ---------------------------------------------------------------- a mesh's points and a texture's picture, without asking the graphics card
## Mesh.surface_get_arrays() and Texture2D.get_image() read the data back from the graphics card. On the main thread
## that is a short wait. On the thread that builds a Sandbox place it is a wait for the main thread to reach the
## renderer and then a stall of the renderer, once for every mesh looked at: hundreds of them, and long frames in the
## game the whole time. A model that has just been loaded still has all of it in memory, so the builder notes it here
## (scripts/world_build.gd _gltf) and the Hd* helpers ask here. With nothing noted (every ordinary track load) these are
## exactly the calls they stand in for.
static var _arr := {}      # ArrayMesh -> [the arrays of each of its surfaces]
static var _img := {}      # Texture2D -> its Image


static func arrays(mesh: Mesh, si: int) -> Array:
	if not _arr.is_empty():
		var a = _arr.get(mesh)
		if a != null and si < (a as Array).size():
			return (a as Array)[si]
	return mesh.surface_get_arrays(si)


static func image(tex: Texture2D) -> Image:
	if not _img.is_empty():
		var i = _img.get(tex)
		if i != null:
			return i
	return tex.get_image()


static func note_mesh(mesh: Mesh, surfaces: Array) -> void:
	_arr[mesh] = surfaces


static func note_image(tex: Texture2D, img: Image) -> void:
	_img[tex] = img


static func forget() -> void:
	_arr = {}
	_img = {}
