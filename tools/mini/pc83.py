"""The PC side of web patch 83 (v224): flying keeps the race camera (aimed at the kart's height, not between it and the ground).
    py.cmd tools/mini/pc83.py      (once, after pc82; edits D:/crust-rush/godot/scripts/main.gd _camera)"""
p = 'D:/crust-rush/godot/scripts/main.gd'
s = open(p, encoding='utf-8', newline='').read()
for a, b in [('	var cy := rz - 4.0 if k.glide else rg + (rz - rg) * 0.45\n', '	var cy := rz - 2.0 if k.fly else (rz - 4.0 if k.glide else rg + (rz - rg) * 0.45)   # (pc83: flying, at the kart\'s height)\n'),
             ('	if (T.battle or sbf or k.tun != null) and not k.glide:\n', '	if (T.battle or sbf or k.tun != null) and not k.glide and not k.fly:\n')]:
    assert s.count(a) == 1, (s.count(a), a)
    s = s.replace(a, b)
open(p, 'w', encoding='utf-8', newline='').write(s)
print('pc83 applied')
