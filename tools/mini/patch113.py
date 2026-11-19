"""Patch 113 (web v247): the underglow about a third brighter. The owner: "brighten the underglow a little bit. its just a little too dim".
- UG_GAIN 1 -> 1.35 (the garage floor's light), UG_BOUNCE .35 -> .47 (the light under the car in the garage), UG_BOUNCE_R 1.6 -> 2.15
  (the lights under a racing kart, in the dark).
- In a race: the haze on the ground .06+.4L -> .09+.52L opacity (L: how dark it is), the strip colour x(.75+.25L) -> x(1+.3L).
- PC: tools/mini/pc102.py (view.gd's same constants and the haze's alpha).
Run once, after patch 112: python tools/mini/patch113.py"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'patch 113' not in s, 'already patched'


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:90])
    s = s.replace(a, b)


rep("const UG_GAIN=1,UG_REF=.048,UG_BOUNCE=.35,UG_BOUNCE_R=1.6;",
    "const UG_GAIN=1.35,UG_REF=.048,UG_BOUNCE=.47,UG_BOUNCE_R=2.15;/* (patch 113: a third brighter; were 1, .35, 1.6) */")
rep("ug.pl.material.opacity=.06+.4*L;", "ug.pl.material.opacity=.09+.52*L;/* (patch 113) */")
rep("multiplyScalar(.75+.25*L+(k.boost>0?.15:0))", "multiplyScalar(1+.3*L+(k.boost>0?.15:0))")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patch 113 applied')
