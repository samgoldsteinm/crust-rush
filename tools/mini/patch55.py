"""Patch 55 (web v214): no causeway posts or lamps standing in a shortcut's lane.
The owner (a picture on Margherita Ring where its shortcut comes back onto the raised road): "there are also still some shortcuts that
have objects in the driving path. the driver can go right through them but they still look weird can we remove these from in the
shortcut paths". They were the causeway's stone posts, slim poles and lamps (water maps' raised road, CAUSE), put along both edges with no
shortcut check (scratch/scvert.js found 16 posts, colour #d8cbb2, in the lane). A post is now left out where a shortcut passes
(nearSC, the lane plus 4). Any other row of things along the road edge must check nearSC the same way (most already do).
Run once: py.cmd tools/mini/patch55.py"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'patch 55' not in s, 'already patched'
a = "const x=p.x+p.nx*(WALLD+5)*sd,z=p.y+p.ny*(WALLD+5)*sd,gy=groundAt(p.x,p.y);\n      PO.push({x,y:gy+4.5,z});"
assert s.count(a) == 1
s = s.replace(a, "const x=p.x+p.nx*(WALLD+5)*sd,z=p.y+p.ny*(WALLD+5)*sd,gy=groundAt(p.x,p.y);if(nearSC(x,z,SCW+4))continue;/* (patch 55: not in a shortcut's lane) */\n      PO.push({x,y:gy+4.5,z});")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patch 55 applied')
