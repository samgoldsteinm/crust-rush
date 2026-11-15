"""Patch 36 (web v201): in Sandbox, Y on a controller fires the special ability (as in a race) and the map is Select alone.
The owner, 2026-11-15: "if y is to use an item on controller in sandbox then the map should be the select button". Select (View / Back /
Minus) already opened the map in Sandbox, and nothing else uses it there (in a race it is the look-back; Sandbox gave that up in v193).
Web v200 had put the ability on R3 because Y was the map; that goes. Nothing here moves a kart. Run once: py.cmd tools/mini/patch36.py"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'patch 36' not in s, 'already patched'


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:90])
    s = s.replace(a, b)


rep("if(edge(M.Y)&&!(SPEC&&SPEC.on)){if(SBX)sbMap(true,'drive');else abilQueued=true;}if(SBX&&gp.mapping==='standard'&&edge(11))abilQueued=true;",
    "if(edge(M.Y)&&!(SPEC&&SPEC.on))abilQueued=true;/* (patch 36: Y is the ability in Sandbox too; its map is Select) */")
rep("if(SBM.open&&(edge(M.Y)||edge(M.BACK)))sbMap(false);else", "if(SBM.open&&edge(M.BACK))sbMap(false);else")
rep("The map travels fast: Y on a controller, M on a keyboard", "The map travels fast: Select on a controller, M on a keyboard")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patched')
