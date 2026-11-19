"""Patch 114 (web v247): the underglow less of a box, the wheels blocking it. The owner: "it looks too much like a square remember the
wheels block the light a little bit".
- ugLs: each tyre's footprint (what the light must get past) rf*.85 x tw*.5 -> rf x tw*.62, and it blocks 1.8 x as hard (kT), so the
  ground beside each wheel is in its shadow.
- The halo and the edge where the light ends: the rounded box's corner radius .3b -> .85b (nearly a pill), so the ends fall off round.
  (A superellipse was tried: its distance is not a true distance, the light reached the picture's edge and was cut straight.)
- PC: shaders/underglow.gdshaderinc is the same sum (tools/mini/pc103.py).
Run once, after patch 113: python tools/mini/patch114.py"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'patch 114' not in s, 'already patched'


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:90])
    s = s.replace(a, b)


rep("function ugLs(P,px,pz){const {a,b,h,wf,wr,wz,rf,rr,M,kT}=P,",
    "function ugLs(P,px,pz){const {a,b,h,wf,wr,wz,rf,rr,M}=P,kT=P.kT*1.8/* (patch 114: the tyres block harder) */,")
rep("oFp=[wf,wz,rf*.85,tw*.5],oFm=[wf,-wz,rf*.85,tw*.5],oRp=[wr,wz,rr*.85,tw*.5],oRm=[wr,-wz,rr*.85,tw*.5]",
    "oFp=[wf,wz,rf,tw*.62],oFm=[wf,-wz,rf,tw*.62],oRp=[wr,wz,rr,tw*.62],oRm=[wr,-wz,rr,tw*.62]")
rep("const rc=.3*b,Lb=.15*b+.6*h,qx=", "const rc=.85*b/* (patch 114: nearly a pill, was .3b) */,Lb=.15*b+.6*h,qx=")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patch 114 applied')
