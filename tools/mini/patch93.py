"""Patch 93 (web v228): the Rims colour covers the whole metal wheel: spokes, lip and barrel; the Chariot's whole wheel.
The owner (on the rim pictures): "some of the color doesn't cover the full rim or spokes. The color gold ends before it covers the
spokes completely. It leaves like the rim around the spokes the original color ... When the spokes are a different color normally the
entire metal part of the wheel is. So inside the wheel the part that the tire wraps around should be the same as the rim color. Also
for the chariot wheel rim should just change the entire color of the wheel because chariot wheels are all one piece".
Why: patch 82 stopped the spoke classes at the tyre's inner radius (uCut), so the lip and barrel (the same classes) kept their colour.
- uCut only on the Monster wheel now (WHEEL_CUT: its tread blocks are in its rim class); everywhere else the spoke classes are painted
  whole, lip and barrel too. The held part (caliper), the brake discs (12) and the tyre (8) keep theirs.
- WHEEL_ALL: the Chariot's wheel takes the Rims colour all over (uAll).
- The Emerald set's rim class 11 joins its list (its lip and barrel).
- PC: pc88 the same (cut lists only for the Monster wheel, the Chariot's every class).
Run once, after patch 92: tools/py.cmd tools/mini/patch93.py"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'patch 93' not in s, 'already patched'


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:90])
    s = s.replace(a, b)


rep("emerald:[6,15,16],", "emerald:[6,15,16,11],")
rep("rollpin:[21],grater:[21],comet:[21],oilcan:[21],", "rollpin:[21,12],grater:[21,12],comet:[21,12],oilcan:[21,12],/* (patch 93: the toys' dish is their class 12) */")
rep("const _rvc={};function rimVC(", "/* (patch 93) the spokes' limit at the tyre only where the rim class holds tread (the Monster wheel); the Chariot's wheel all over */\nconst WHEEL_CUT={monster:1},WHEEL_ALL={chariot:1};\nconst _rvc={};function rimVC(")
rep("let cut=1e9;if(geo&&geo.attributes.uv){", "let cut=1e9;if(WHEEL_CUT[id]&&geo&&geo.attributes.uv){")
rep("uS:{value:v4(r&&r.h?sp:[])}", "uS:{value:v4(r&&r.h?sp:[])},uAll:{value:r&&r.h&&WHEEL_ALL[id]?1:0}")
rep("uniform vec4 uS,uK;", "uniform vec4 uS,uK;uniform float uAll;")
rep("else if(rIn(rCi,uS)&&length(vRO)<uCut)", "else if((rIn(rCi,uS)||uAll>.5)&&length(vRO)<uCut)")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patch 93 applied')
