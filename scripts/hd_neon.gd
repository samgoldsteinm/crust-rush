class_name HdNeon
## The Neon Cup's lights on the PC. Drawing only.
## The web game's track model keeps its materials' names. The glowing pieces of the neon tracks are named
## (neonadd, neonholo, neonhaze, neonsun, neonfar, neonlane, neonshaft), and here each gets what the web gives it:
## beams, rings and the hologram add their light to what is behind them, the sun and the far ridges are not
## dimmed by fog, the hologram turns, and the arrows on a shortcut and the lights in the glide's shaft run.
## A dome of stars goes round the whole track.


static func upgrade(root: Node3D) -> int:
	var n := 0
	var holo: Array = []
	var run: Array = []
	for node in root.find_children("*", "MeshInstance3D", true, false):
		var mi := node as MeshInstance3D
		if mi.mesh == null:
			continue
		for si in mi.mesh.get_surface_count():
			var m := mi.mesh.surface_get_material(si) as StandardMaterial3D
			if m == null:
				continue
			var nm := String(m.resource_name)
			if not nm.begins_with("neon"):
				continue
			n += 1
			if nm.begins_with("neonadd") or nm.begins_with("neonholo") or nm.begins_with("neonhaze"):
				m.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
				m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
				m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
				m.depth_draw_mode = BaseMaterial3D.DEPTH_DRAW_DISABLED
				m.cull_mode = BaseMaterial3D.CULL_DISABLED
				m.disable_fog = true
				mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
			elif nm.begins_with("neonsun") or nm.begins_with("neonfar"):
				m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
				m.disable_fog = true
				m.cull_mode = BaseMaterial3D.CULL_DISABLED
				mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
			if nm.begins_with("neonholo") and not holo.has(mi):
				holo.append(mi)
			if nm.begins_with("neonlane"):
				run.append([m, 1.4])
			elif nm.begins_with("neonshaft"):
				run.append([m, 0.35])
	if n == 0:
		return 0
	var live := _Live.new()
	live.name = "hd_neon"
	live.run = run
	root.add_child(live)
	# the hologram: its discs turn about the middle of the tower
	for mi in holo:
		var box: AABB = (mi as MeshInstance3D).global_transform * (mi as MeshInstance3D).get_aabb()
		var piv := Node3D.new()
		root.add_child(piv)
		piv.global_position = Vector3(box.get_center().x, 0.0, box.get_center().z)
		(mi as MeshInstance3D).reparent(piv, true)
		live.spin.append(piv)
	# stars
	var dome := MeshInstance3D.new()
	var sm := SphereMesh.new()
	sm.radius = 14000.0
	sm.height = 28000.0
	sm.radial_segments = 32
	sm.rings = 16
	dome.mesh = sm
	var mat := ShaderMaterial.new()
	mat.shader = load("res://shaders/stars.gdshader")
	mat.render_priority = -100
	dome.material_override = mat
	dome.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	dome.extra_cull_margin = 16000.0
	dome.name = "stars"
	root.add_child(dome)
	return n


class _Live extends Node:
	var run: Array = []    # [material, speed]
	var spin: Array = []   # pivots
	func _process(dt: float) -> void:
		for q in run:
			var m: StandardMaterial3D = q[0]
			m.uv1_offset.y = fposmod(m.uv1_offset.y + float(q[1]) * dt, 1.0)
		for p in spin:
			(p as Node3D).rotate_y(0.35 * dt)
