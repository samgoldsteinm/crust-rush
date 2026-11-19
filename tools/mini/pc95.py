"""PC: the four concept cars of web v239 (tools/cars/patch_cars2.py): online version 121, their engine voices, their signature combos.
    py.cmd tools/mini/pc95.py      (once, after pc94; edits webnet.gd, sfx.gd, style.gd)
The bodies, wheels, liveries (signature themes included) come with the garage export.
"""
G = 'D:/crust-rush/godot/scripts/'


def rep(f, a, b, n=1):
    p = G + f
    s = open(p, encoding='utf-8', newline='').read()
    assert s.count(a) == n, (f, s.count(a), a[:80])
    s = s.replace(a, b)
    open(p, 'w', encoding='utf-8', newline='').write(s)


rep('webnet.gd', 'const PROTO := 120   # (120:', 'const PROTO := 121   # (121: web v239, four new car bodies; 120:')
rep('sfx.gd', 'const ENG_BODY := {"oilcan": "v8",', 'const ENG_BODY := {"biome": "jet", "surge": "jet", "vortex": "race", "scarlet": "race", "oilcan": "v8",')
rep('style.gd', '''	{"n": "Heritage", "p": 10, "st": {"tr": 1, "ac": 2, "in": 11, "rm": 17, "cl": 1, "gl": 0, "hl": 0, "sm": 0}, "c": 450, "only": ["muscle", "roadster", "hatch", "interceptor"]}]''',
    '''	{"n": "Heritage", "p": 10, "st": {"tr": 1, "ac": 2, "in": 11, "rm": 17, "cl": 1, "gl": 0, "hl": 0, "sm": 0}, "c": 450, "only": ["muscle", "roadster", "hatch", "interceptor"]},
	# (pc95, web v239) the four concept cars' signature combos
	{"n": "Glowroot", "p": 14, "st": {"tr": 1, "ac": 13, "in": 7, "rm": 2, "cl": 13, "gl": 1, "hl": 2, "sm": 2}, "c": 450, "only": ["biome"]},
	{"n": "Plug In", "p": 22, "st": {"tr": 1, "ac": 4, "in": 1, "rm": 1, "cl": 4, "gl": 0, "hl": 1, "sm": 0}, "c": 400, "only": ["surge"]},
	{"n": "Acid Strike", "p": 12, "st": {"tr": 1, "ac": 1, "in": 12, "rm": 1, "cl": 12, "gl": 4, "hl": 5, "sm": 5}, "c": 550, "only": ["vortex"]},
	{"n": "Grand Prix Red", "p": 10, "st": {"tr": 1, "ac": 16, "in": 11, "rm": 16, "cl": 16, "gl": 0, "hl": 0, "sm": 0}, "c": 500, "only": ["scarlet"]},
	{"n": "Static Charge", "p": 17, "st": {"tr": 1, "ac": 13, "in": 1, "rm": 14, "cl": 13, "gl": 1, "hl": 2, "sm": 2}, "c": 450, "only": ["biome", "surge"]}]''')
print('pc95 applied')
