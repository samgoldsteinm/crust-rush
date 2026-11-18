"""PC: web patch 93 (v228): the Rims colour on the whole metal wheel (no limit at the tyre but on the Monster wheel); the Chariot's
whole wheel.      py.cmd tools/mini/pc88.py      (once, after pc87; edits kart_builder.gd)"""
G = 'D:/crust-rush/godot/scripts/'


def rep(f, a, b, n=1):
    p = G + f
    s = open(p, encoding='utf-8', newline='').read()
    assert s.count(a) == n, (f, s.count(a), a[:80])
    s = s.replace(a, b)
    open(p, 'w', encoding='utf-8', newline='').write(s)


K = 'kart_builder.gd'
rep(K, '"chariot": [1, 6, 2, 0],', '"chariot": [1, 6, 2, 0, 8, 7, 9, 10, 11],')   # (the whole chariot wheel)
rep(K, '"emerald": [6, 15, 16],', '"emerald": [6, 15, 16, 11],')
rep(K, '"rollpin": [21], "grater": [21], "comet": [21], "oilcan": [21],', '"rollpin": [21, 12], "grater": [21, 12], "comet": [21, 12], "oilcan": [21, 12],')
rep(K, '''		"cut": WHEEL_SPOKES.get(String(info["bodies"][int(spec.get("b", 0))]["id"]), [11]), "cutw": WHEEL_SPOKES.get(String(wheel_of(spec).get("id", "")), [])}''',
    '''		"cut": WHEEL_SPOKES.get("monster", [11]) if String(info["bodies"][int(spec.get("b", 0))]["id"]) == "monster" else [],
		"cutw": [11] if String(wheel_of(spec).get("id", "")) == "monster" else []}   # (pc88, web patch 93: the limit at the tyre only on the Monster wheel)''')
print('pc88 applied')
