"""Patch 107 (web v244): the Night Tank's accent shows, the same on both sides.
The owner: "currently the night tank has no visible accents, give it some but make sure they are symmetrical on the car".
Its model has no chrome, carbon or stripe (the classes the accent paints). tools/blender/car_rules.py now makes its three pairs of rear
fins (Spoiler1..6, left/right twins) carbon, which looks as dark as before until an accent is picked; ACC_X nighttank: metal 7 adds its
two side fans (boostfanleft/right). PC: from the export.
Run once, after patch 106: tools/py.cmd tools/mini/patch107.py"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'patch 107' not in s, 'already patched'
a = "const ACC_X={bike_neutron:7,bike_mx:7,bike_rocket:7,retrogt:7,coupe:1,muscle:1}"
assert s.count(a) == 1
s = s.replace(a, "const ACC_X={bike_neutron:7,bike_mx:7,bike_rocket:7,retrogt:7,coupe:1,muscle:1,nighttank:7/* (patch 107: its side fans) */}")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patch 107 applied')
