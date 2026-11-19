"""PC: the Night Tank (web v241): online version 122, its engine voice, its signature combo, and the model's credit in Settings > More.
    py.cmd tools/mini/pc96.py      (once, after pc95; edits webnet.gd, sfx.gd, style.gd, main.gd)"""
G = 'D:/crust-rush/godot/scripts/'


def rep(f, a, b, n=1):
    p = G + f
    s = open(p, encoding='utf-8', newline='').read()
    assert s.count(a) == n, (f, s.count(a), a[:80])
    s = s.replace(a, b)
    open(p, 'w', encoding='utf-8', newline='').write(s)


rep('webnet.gd', 'const PROTO := 121   # (121:', 'const PROTO := 122   # (122: web v241, the Night Tank; 121:')
rep('sfx.gd', 'const ENG_BODY := {"biome": "jet",', 'const ENG_BODY := {"nighttank": "jet", "biome": "jet",')
rep('style.gd', '''"c": 450, "only": ["biome", "surge"]}]''', '''"c": 450, "only": ["biome", "surge"]},
	{"n": "Dark Knight", "p": 23, "st": {"tr": 1, "ac": 14, "in": 1, "rm": 14, "cl": 1, "gl": 0, "hl": 2, "sm": 1}, "c": 500, "only": ["nighttank"]}]''')
rep('main.gd', '''		"more":
			c.add_child(menu.section_label("Username"))''', '''		"more":
			c.add_child(menu.section_label("Credits"))   # (pc96, web Settings > More > Credits)
			c.add_child(menu.para("Night Tank: based on \\"Batmobile-The Dark Knight Tumbler\\" by Gravity Jack, licensed under Creative Commons Attribution (CC BY 4.0). Scenery photo-scans from Poly Haven (CC0).", 12.5, Color("#c2a58c"), 720.0))
			c.add_child(menu.section_label("Username"))''')
print('pc96 applied')
