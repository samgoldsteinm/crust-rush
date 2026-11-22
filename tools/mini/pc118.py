"""PC: Margherita's brick wall back. The owner: "in the picture of margherita there is no brick wall ... like there is supposed
to be". HdKitchen (Finished models) painted the web's round brick wall over with a tiled kitchen wall; now the web's own
brick picture stays, and gains relief from itself (mortar sunk, bricks standing out: a normal map made from the picture's
brightness) and a slightly rough, unglazed finish. The counter pieces, cabinets and faucets stay.
    python tools/mini/pc118.py      (once, after pc117)"""
p = 'D:/crust-rush/godot/scripts/hd_kitchen.gd'
s = open(p, encoding='utf-8', newline='').read()
assert 'pc118' not in s
a = """	var sm := ShaderMaterial.new()
	sm.shader = load("res://shaders/kitchen_wall.gdshader")
	sm.set_shader_parameter("radius", rw)
	sm.set_shader_parameter("y0", TABLE_Y)
	sm.set_shader_parameter("top", top)
	mi.set_surface_override_material(int(wall["si"]), sm)
"""
b = """	# (pc118) the web's brick stays (the owner: "there is supposed to be" a brick wall), with relief made from the picture
	_brick_relief(mi.mesh.surface_get_material(int(wall["si"])) as StandardMaterial3D)
"""
assert s.count(a) == 1
s = s.replace(a, b)
a2 = """## the room's round wall: an open cylinder round the middle, standing on the table and reaching the ceiling
"""
b2 = """## (pc118) the brick picture's own relief: the light mortar lines sink, the red bricks stand out
static func _brick_relief(m: StandardMaterial3D) -> void:
	if m == null or m.albedo_texture == null or m.normal_texture != null:
		return
	var img := m.albedo_texture.get_image()
	if img == null or img.is_empty():
		return
	img = img.duplicate()
	if img.is_compressed():
		img.decompress()
	img.convert(Image.FORMAT_RGBA8)
	# height: dark (brick) high, light (mortar) low
	for y in img.get_height():
		for x in img.get_width():
			var c := img.get_pixel(x, y)
			var h := 1.0 - clampf((c.get_luminance() - 0.25) * 1.8, 0.0, 1.0)
			img.set_pixel(x, y, Color(h, h, h, 1.0))
	img.bump_map_to_normal_map(6.0)
	img.generate_mipmaps()
	m.normal_enabled = true
	m.normal_texture = ImageTexture.create_from_image(img)
	m.normal_scale = 1.2
	m.roughness = maxf(m.roughness, 0.85)


## the room's round wall: an open cylinder round the middle, standing on the table and reaching the ceiling
"""
assert s.count(a2) == 1
s = s.replace(a2, b2)
open(p, 'w', encoding='utf-8', newline='').write(s)
print('pc118 applied')
