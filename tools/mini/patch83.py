"""Patch 83 (web v224): flying (developer options) keeps the race's camera.
The owner: "when using the fly feature in developer mode the camera only moves up and down and it struggles to follow the car. i want the
same camera movement we have when racing but also while flying". Why: the chase camera aims between the kart and the ground under it
(cy = rg + (rz - rg) * .45): flying high, that point is far below the kart, so the camera sat low and lagged. Flying now aims at the
kart's own height (cy = rz - 8: the camera sits a little above it, low behind, and looks ahead), as gliding does (rz - 4). The owner, after the first try (rz - 2): "the camera should sit lower behind the user so they can see more in front of them"; the rest is the race camera. PC: pc83 (main.gd _camera).
Run once, after patch 82: py.cmd tools/mini/patch83.py"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'patch 83' not in s, 'already patched'
a = "cy=camT.glide?camT.rz-4:BATTLE?"
assert s.count(a) == 1, s.count(a)
s = s.replace(a, "cy=camT.fly?camT.rz-8/* (patch 83: flying, the race camera low behind the kart, looking ahead) */:camT.glide?camT.rz-4:BATTLE?")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patch 83 applied')
