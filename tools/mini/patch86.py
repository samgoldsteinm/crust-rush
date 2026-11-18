"""Patch 86 (web v225): Sandbox's left-hand read-out and buttons sit up in the corner (more room for thumbs on a phone).
The owner (an iPhone, landscape): "the coin counter has room above it still, let's move the hud on the left side higher up to the corner so
there is more room for the user to drive with touch controls". The read-out (#sbHud) sat 64 px down (the race's place box's room, which
Sandbox does not show); now 10 px (or the notch's inset) from the top. The Special and Rear buttons below it move up with it (172 -> 108).
The PC is played with a controller or keys: unchanged.
Run once, after patch 85: py.cmd tools/mini/patch86.py"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'patch 86' not in s, 'already patched'
for a, b, n in [("e.id='sbHud';e.style.cssText='position:absolute;left:max(10px,env(safe-area-inset-left));top:64px;", "e.id='sbHud';e.style.cssText='position:absolute;left:max(10px,env(safe-area-inset-left));top:max(10px,env(safe-area-inset-top));/* (patch 86: up in the corner) */", 1),
                ("body.sbx .abtn{top:172px!important}body.sbx .lookbtn{top:calc(172px + var(--btn)*.95 + 20px)!important}", "body.sbx .abtn{top:108px!important}body.sbx .lookbtn{top:calc(108px + var(--btn)*.95 + 20px)!important}/* (patch 86: up with the read-out) */", 1)]:
    assert s.count(a) == n, (s.count(a), a[:60])
    s = s.replace(a, b)
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patch 86 applied')
