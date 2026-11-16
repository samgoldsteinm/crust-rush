"""Patch 47b (web v209): a friend joining a room's Sandbox starts at the host's place, not at whatever was behind their menu.
The owner: "the host spawned in garage like selected but the guest started in backyard". The guest's 'sbgo' set mapIdx to the host's place
and then called goRace(mapIdx); goRace only loads a map when mi !== mapIdx, so the guest kept the menu's map (the backyard). Now the guest
calls goRace(d.mi) and lets goRace set mapIdx and load it. (tools/neon/sbnet.py now starts the two windows on different maps.)
Run once: py.cmd tools/mini/patch47b.py"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'patch 47b' not in s, 'already patched'
a = "mode='sb';mapIdx=d.mi|0;NET.fromNet=true;goRace(mapIdx);}}"
assert s.count(a) == 1
s = s.replace(a, "mode='sb';NET.fromNet=true;goRace(d.mi|0);/* (patch 47b: goRace loads it; setting mapIdx first kept the menu's map) */}}")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patch 47b applied')
