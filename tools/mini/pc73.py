"""PC: the garage as a neutral car showroom (the owner: "on the pc version really spend some time making the car paints and colors look
better. the lighting and reflections need to be really good"; "the car colors are super flat on pc"; "the silver doesnt look silver").
    py.cmd tools/mini/pc73.py      (once; edits D:/crust-rush/godot/scripts/menu.gd; the sky is shaders/studio_neutral.gdshader)
Before: a warm studio sky (cream top, orange horizon, brown below) at ambient .55, ACES white 16: every reflection warm, chrome bronze,
black paint brown, colours washed pale. Now: studio_neutral (a dark neutral room with long white strip lights) at radiance 512, ambient
.35, a neutral key light and a cool rim light behind, ACES (white 8): deep colours, crisp highlight lines that show the body's shape.
Pictures: tests/ugshots.tscn with UG_BIG=1 (scratch/ug/pcshots.sh before|after).
"""
G = 'D:/crust-rush/godot/scripts/'


def rep(f, a, b, n=1):
    p = G + f
    s = open(p, encoding='utf-8', newline='').read()
    assert s.count(a) == n, (f, s.count(a), a[:80])
    s = s.replace(a, b)
    open(p, 'w', encoding='utf-8', newline='').write(s)


rep('menu.gd', """	skm.shader = load("res://shaders/studio_sky.gdshader")
	sky.sky_material = skm
	sky.radiance_size = Sky.RADIANCE_SIZE_256
	e.sky = sky
	e.ambient_light_source = Environment.AMBIENT_SOURCE_SKY
	e.ambient_light_sky_contribution = 1.0
	e.ambient_light_energy = 0.55
	e.reflected_light_source = Environment.REFLECTION_SOURCE_SKY
	e.tonemap_mode = Environment.TONE_MAPPER_ACES
	e.tonemap_white = 16.0
	e.tonemap_exposure = 1.05 * (1.0 / 0.6) / 1.8
	env.environment = e
	w3.add_child(env)
	var sun := DirectionalLight3D.new()
	sun.light_energy = 2.4
	sun.light_color = Color("#fff0d8")
""", """	skm.shader = load("res://shaders/studio_neutral.gdshader")   # (pc73: a neutral showroom, not the warm studio)
	sky.sky_material = skm
	sky.radiance_size = Sky.RADIANCE_SIZE_512
	e.sky = sky
	e.ambient_light_source = Environment.AMBIENT_SOURCE_SKY
	e.ambient_light_sky_contribution = 1.0
	e.ambient_light_energy = 0.35
	e.reflected_light_source = Environment.REFLECTION_SOURCE_SKY
	e.tonemap_mode = Environment.TONE_MAPPER_ACES
	e.tonemap_white = 8.0
	e.tonemap_exposure = 1.0
	env.environment = e
	w3.add_child(env)
	var rim := DirectionalLight3D.new()   # (pc73) a cool rim light from behind, for the edges of the body
	rim.light_energy = 1.1
	rim.light_color = Color("#dfe8ff")
	w3.add_child(rim)
	rim.look_at_from_position(Vector3(-14, 10, -12), Vector3.ZERO, Vector3.UP)
	var sun := DirectionalLight3D.new()
	sun.light_energy = 2.6
	sun.light_color = Color("#fffaf2")
""")
print('pc73 applied')
