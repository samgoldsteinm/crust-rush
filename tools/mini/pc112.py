"""PC: the karts' clear coat catches the web's lights in a race. The owner: "the cars look a little flat in the game ... double
check they all have a clear coat and that the light is reflecting correctly". The paint has its clear coat (kart_builder), but in
a race it mirrored the visible sky, a soft gradient with nothing bright in it. The web gives every track a separate reflection
picture (scene.environment = envFrom(theme.env, spots)): the theme's four-colour gradient with bright round lights in it (two
white lamps and an orange glow in the kitchen, a low warm sun at the bay, ...), and that is what the gloss shows. The sky shader
now draws that picture when Godot makes its reflections (AT_CUBEMAP_PASS), and the visible sky stays as it was. Toy rooms keep
their photographed room (their probe wins inside it).
    python tools/mini/pc112.py      (once, after pc111)"""
G = 'D:/crust-rush/godot/'


def patch(f, pairs):
    p = G + f
    s = open(p, encoding='utf-8', newline='').read()
    assert 'pc112' not in s, (f, 'already patched')
    for a, b in pairs:
        assert s.count(a) == 1, (f, s.count(a), a[:80])
        s = s.replace(a, b)
    open(p, 'w', encoding='utf-8', newline='').write(s)


patch('shaders/sky.gdshader', [("""uniform float stars = 0.0;
""", """uniform float stars = 0.0;
// (pc112) the web's reflection picture (envFrom): a 512x256 panorama, gradient stops at 0 .42 .55 1 down the picture, round
// lights (x, y, radius in its pixels; colour) fading out to their edge; drawn only into the reflections
uniform bool env_on = false;
uniform vec3 env0 = vec3(1.0);
uniform vec3 env1 = vec3(1.0);
uniform vec3 env2 = vec3(0.5);
uniform vec3 env3 = vec3(0.1);
uniform vec4 spot0 = vec4(0.0);
uniform vec4 spot1 = vec4(0.0);
uniform vec4 spot2 = vec4(0.0);
uniform vec3 spot_c0 = vec3(1.0);
uniform vec3 spot_c1 = vec3(1.0);
uniform vec3 spot_c2 = vec3(1.0);

vec3 lin(vec3 c) {
	return mix(c / 12.92, pow((c + 0.055) / 1.055, vec3(2.4)), step(0.04045, c));
}

vec3 spot(vec3 base, vec2 px, vec4 s, vec3 col) {
	if (s.z <= 0.0) {
		return base;
	}
	vec2 d = px - s.xy;
	d.x = mod(d.x + 256.0, 512.0) - 256.0;   // (round the panorama)
	float a = clamp(1.0 - length(d) / s.z, 0.0, 1.0);
	return mix(base, col, a);
}

vec3 env_pic(vec3 d) {
	float px = (atan(d.z, d.x) / (2.0 * PI) + 0.5) * 512.0;
	float py = (0.5 - asin(clamp(d.y, -1.0, 1.0)) / PI) * 256.0;
	float t = py / 256.0;
	vec3 c = t < 0.42 ? mix(env0, env1, t / 0.42) : (t < 0.55 ? mix(env1, env2, (t - 0.42) / 0.13) : mix(env2, env3, (t - 0.55) / 0.45));
	c = spot(c, vec2(px, py), spot0, spot_c0);
	c = spot(c, vec2(px, py), spot1, spot_c1);
	c = spot(c, vec2(px, py), spot2, spot_c2);
	return lin(c);
}
"""), ("""	COLOR = c * 1.2;
}""", """	COLOR = c * 1.2;
	if (env_on && AT_CUBEMAP_PASS) {
		COLOR = env_pic(EYEDIR);   // (pc112) what the gloss shows: the web's reflection picture
	}
}""")])

HELPER = '''

## (pc112) the web's reflection picture for a theme (THEMES[theme].env and the spots of its envFrom call), into the sky shader
static func sky_env(sm: ShaderMaterial, theme: String) -> void:
	var E := {"kitchen": ["#fff6e4", "#ffb26a", "#7a3a1c", "#1e0e08"], "bay": ["#9cc4ff", "#ffc39a", "#2e7b8f", "#0d3442"],
		"freezer": ["#cfe6ff", "#ffffff", "#9db8d4", "#5a7590"], "night": ["#2a3a7a", "#3a3a6a", "#120c1c", "#05050a"]}
	var P := {"kitchen": [[128, 40, 30, "#ffffff"], [384, 40, 30, "#ffffff"], [256, 140, 40, "#ff8a2a"]],
		"freezer": [[256, 50, 50, "#ffffff"], [100, 120, 20, "#dff2ff"]], "bay": [[380, 110, 40, "#fff2d0"]]}
	var cols: Array = E.get(theme, E["kitchen"])
	var sp: Array = P.get(theme, [[100, 60, 10, "#bcd0ff"], [300, 130, 16, "#ffd27a"], [420, 130, 16, "#ffd27a"]])
	sm.set_shader_parameter("env_on", true)
	for i in 4:
		var c := Color(String(cols[i]))
		sm.set_shader_parameter("env%d" % i, Vector3(c.r, c.g, c.b))
	for i in 3:
		if i < sp.size():
			var s: Array = sp[i]
			var c2 := Color(String(s[3]))
			sm.set_shader_parameter("spot%d" % i, Vector4(float(s[0]), float(s[1]), float(s[2]), 0.0))
			sm.set_shader_parameter("spot_c%d" % i, Vector3(c2.r, c2.g, c2.b))
		else:
			sm.set_shader_parameter("spot%d" % i, Vector4.ZERO)
'''

patch('scripts/world_build.gd', [("""	sky.sky_material = sm
	# (the sky's light for glossy paint""", """	sky_env(sm, T.theme)   # (pc112)
	sky.sky_material = sm
	# (the sky's light for glossy paint"""), ("""func _ph(name: String) -> void:""", HELPER.strip('\n') + "\n\n\nfunc _ph(name: String) -> void:")])
patch('scripts/main.gd', [("""	sky.sky_material = sm
	sky.radiance_size = Sky.RADIANCE_SIZE_64
	env.sky = sky""", """	WorldBuild.sky_env(sm, T.theme)   # (pc112)
	sky.sky_material = sm
	sky.radiance_size = Sky.RADIANCE_SIZE_64
	env.sky = sky""")])
print('pc112 applied')
