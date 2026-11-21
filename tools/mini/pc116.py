"""PC: Settings > Graphics > Bounced light (off by default). The owner asked for lighting "as realistic as possible"; Godot's
SDFGI (signed-distance-field global illumination) lets sunlight bounce off the ground, walls and buildings onto what is near
them (warmer shade under bridges, colour picked up from the floor in the toy rooms). It costs frame rate, so it is opt-in and
needs Ultra on a computer. Tested earlier with tests/mtnshots (MT_GI=1); same values.
    python tools/mini/pc116.py      (once, after pc115)"""
p = 'D:/crust-rush/godot/scripts/main.gd'
s = open(p, encoding='utf-8', newline='').read()
assert 'pc116' not in s


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:80])
    s = s.replace(a, b)


rep("""var ao_on := true
""", """var ao_on := true
var gi_on := false      # (pc116) Settings > Bounced light (SDFGI), Ultra only, off by default
""")
rep("""				["Ambient occlusion", "Soft contact""", """				["Bounced light", "Sunlight bounces off the ground, walls and buildings onto everything near them, so shade picks up the colour around it, the way real light does. The most realistic lighting, and the heaviest: try it on a fast graphics card. Ultra only.", "gi", on_off, "1" if gi_on else "0"],
				["Ambient occlusion", "Soft contact""")
rep("""		"ao":
			ao_on = val == "1"
			_apply_quality()
""", """		"ao":
			ao_on = val == "1"
			_apply_quality()
		"gi":
			gi_on = val == "1"
			_apply_quality()
""")
rep("""	env.ssil_enabled = false
""", """	env.ssil_enabled = false
	# (pc116) bounced light: SDFGI round the camera, six cascades from 2-unit cells (reaches across a toy room)
	var gi := gi_on and quality >= 2 and not is_phone
	if env.sdfgi_enabled != gi:
		env.sdfgi_enabled = gi
	if gi:
		env.sdfgi_use_occlusion = true
		env.sdfgi_min_cell_size = 2.0
		env.sdfgi_cascades = 6
		env.sdfgi_energy = 1.0
""")
rep('"ao_on", "sharpen_on"', '"ao_on", "gi_on", "sharpen_on"', 2)
open(p, 'w', encoding='utf-8', newline='').write(s)
print('pc116 applied')
