"""PC: web patch 97 (v232): a wheel type's caliper is not added on the six cars with calipers in their body.
    py.cmd tools/mini/pc92.py      (once, after pc91; edits kart_builder.gd)"""
p = 'D:/crust-rush/godot/scripts/kart_builder.gd'
s = open(p, encoding='utf-8', newline='').read()
a = '''			elif wsrc != null:
				hsrc = wsrc.find_child("hold_" + ("L" if z < 0.0 else "R"), true, false) as Node3D'''
b = '''			elif wsrc != null and not ["gt", "hyper", "interceptor", "scissor", "skywing", "endur"].has(String(bd["id"])):   # (pc92, web BODY_CAL: their own calipers)
					hsrc = wsrc.find_child("hold_" + ("L" if z < 0.0 else "R"), true, false) as Node3D'''
assert s.count(a) == 1
s = s.replace(a, b)
open(p, 'w', encoding='utf-8', newline='').write(s)
print('pc92 applied')
