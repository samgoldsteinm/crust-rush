"""PC: web patch 95 (v230): accent no longer on the Slipstream's decals (ACC_X) or the Onyx's carbon (ACC_NO6). The held crescent,
the Interceptor's roof slots and lamps and the GT driver's size come with the export.
    py.cmd tools/mini/pc90.py      (once, after pc89; edits kart_builder.gd)"""
p = 'D:/crust-rush/godot/scripts/kart_builder.gd'
s = open(p, encoding='utf-8', newline='').read()
for a, b in [('"coupe": 1, "concept": 1, "muscle": 1, "slip": 1}', '"coupe": 1, "muscle": 1}'),
             ('const ACC_NO6 := ["slip"]', 'const ACC_NO6 := ["slip", "onyx"]')]:
    assert s.count(a) == 1, a
    s = s.replace(a, b)
open(p, 'w', encoding='utf-8', newline='').write(s)
print('pc90 applied')
