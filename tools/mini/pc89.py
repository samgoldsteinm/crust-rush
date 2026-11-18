"""PC: web patch 94 (v229): the Concept's Rims colour on its spokes only (the limit at the tyre, as the Monster wheel's).
    py.cmd tools/mini/pc89.py      (once, after pc88; edits kart_builder.gd)"""
p = 'D:/crust-rush/godot/scripts/kart_builder.gd'
s = open(p, encoding='utf-8', newline='').read()
a = '''		"cut": WHEEL_SPOKES.get("monster", [11]) if String(info["bodies"][int(spec.get("b", 0))]["id"]) == "monster" else [],'''
b = '''		"cut": WHEEL_SPOKES.get(String(info["bodies"][int(spec.get("b", 0))]["id"]), [11]) if ["monster", "concept"].has(String(info["bodies"][int(spec.get("b", 0))]["id"])) else [],   # (pc89: the Concept too)'''
assert s.count(a) == 1
s = s.replace(a, b)
open(p, 'w', encoding='utf-8', newline='').write(s)
a = '"concept": [1, 2],'
assert s.count(a) == 1
s = s.replace(a, '"concept": [1],')   # (its ribs are barrel: web patch 94 labels them 14)
open(p, 'w', encoding='utf-8', newline='').write(s)
print('pc89 applied')
