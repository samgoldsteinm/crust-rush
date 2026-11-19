"""Patch 97 (web v232): no second caliper on cars that have their own.
The owner (Endurance GT on Redline wheels): "this car is having 2 calipers shown, for cars that already had a caliper make sure you
didn't add one and if you did remove it so the original one shows. Just make sure the original one doesn't spin with the wheel".
Why: six car bodies carry their calipers in the BODY (class 13 by the wheels; scratch/paint/bodycal.js: GT 165 triangles, Hyper 134,
Interceptor 320, Scissor 150, Skywing 148, Endurance 128; the Roadster's 8 are a sliver behind its hubcaps): part of the body, they never
spun. A wheel set or the Monster wheel brings its own caliper (patch 88's held part), so those cars showed two.
- BODY_CAL: those six. holdOut on a wheel type (not the car's own wheels) on one of them: the held part is not shown (the wheel keeps
  only its rolling part); the body's caliper stays, still and in the Calipers colour. Patch 92's added calipers are only on the
  Grand Coupe, Megawatt and SUV on their own wheels (none of these).
- PC: pc92 (kart_builder: no hold node for a wheel type on those bodies).
Run once, after patch 96: tools/py.cmd tools/mini/patch97.py"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'patch 97' not in s, 'already patched'


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:90])
    s = s.replace(a, b)


rep("function holdOut(wh,yaw,M,id,wset,pack){", "/* (patch 97) car bodies that carry their own calipers: a wheel type's caliper is not shown on them */\nconst BODY_CAL={gt:1,hyper:1,interceptor:1,scissor:1,skywing:1,endur:1};\nfunction holdOut(wh,yaw,M,id,wset,pack,noCal){")
rep("m.castShadow=false;m.userData.held=1;yaw.add(m);\n", "m.castShadow=false;m.userData.held=1;if(noCal)m.visible=false;/* (patch 97) */yaw.add(m);\n")
rep("if(wh.userData.pk)holdOut(wh,yaw,M,wh.userData.wid,wh.userData.wset,wh.userData.pk);",
    "if(wh.userData.pk)holdOut(wh,yaw,M,wh.userData.wid,wh.userData.wset,wh.userData.pk,!!(cfg.car&&BODY_CAL[cfg.car]));")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patch 97 applied')
