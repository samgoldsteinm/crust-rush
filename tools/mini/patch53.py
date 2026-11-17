"""Patch 53 (web v214): headlights the kart cannot block; no second host on a guest's screen in a room's Sandbox race.
- The owner (a picture: a dark V in front of the kart, light only at its edges): "there is also something blocking the headlight from
  working". The spot light sits at the bumper, inside the kart's own shape, and cast shadows: the kart's body shadowed everything straight
  ahead. The headlights cast no shadows now (as most games' headlights).
- The owner: "after a race on sandbox starts the guest still sees 2 versions of the host. one froze on the start line of the race and the
  actual hosts car racing with them", "lets remove the host that remains on the start line". The friends' cars drawn in Sandbox (SBN.peers,
  patch 46) were left in the scene when a race began. Every friend car (and its name tag) is taken away when a race loads (netBeginLoad);
  back in Sandbox they come back from the host's next list of places.
Run once: py.cmd tools/mini/patch53.py"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'patch 53' not in s, 'already patched'


def rep(a, b):
    global s
    assert s.count(a) == 1, (s.count(a), a[:90])
    s = s.replace(a, b)


rep("sp.castShadow=!lite;", "sp.castShadow=false;/* (patch 53: the kart's own body shadowed its headlights) */")
rep("function netBeginLoad(cfg){NET.cfg=cfg;",
    "function netBeginLoad(cfg){try{for(const P of SBN.peers.values())sbnDrop(P);SBN.peers.clear();if(SBN.el)SBN.el.hidden=true;}catch(e){}/* (patch 53: no friend left standing in Sandbox's place) */NET.cfg=cfg;")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patch 53 applied')
