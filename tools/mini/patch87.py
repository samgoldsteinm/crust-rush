"""Patch 87 (web v227): the Classic kart's spare slice is whole again; the garage camera stays under the studio's ceiling.
The owner (Basil's Classic in the garage): "The pizza slice is messed up on the side of this kart also if you move the camera too high
in the garage you run into the ceiling let's fix that so it doesn't happen".
1. The spare slice strapped to the Classic's right pod: the slice's crust end is at x -0.3 and it points forward (tip at x 1.9), but two
   of its three pepperoni (x -0.8, -0.4) and the rear strap (x -1.1) were placed behind the crust, floating on the green pod. Now all
   three pepperoni lie on the cheese, both straps cross the slice, and a crust runs along its wide end. Cosmetic only (no physics); the PC
   takes kart bodies from the export (body_classic.glb), so it follows on the next export.
2. frameGarageCam: the inspect view lets the pitch reach .22+1.1 rad at up to 1.1x zoom, which put the camera 20+ units up, through the
   studio's LED panels (bottom at 14) and ceiling (15). Now the camera stays at or below y 12.6: it first comes closer (never nearer than
   1.7 x the car's radius), and if that is not enough the tilt stops there. The PC garage has no room round it: nothing to change there.
Run once, after patch 86: tools/py.cmd tools/mini/patch87.py"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'patch 87' not in s, 'already patched'


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:90])
    s = s.replace(a, b)


rep("const sp=kAdd(KG.slice,SH.cheese,-.3,2.3,2.98,S,0,0,-Math.PI/2,.34,.34,.08);for(const x of [-1.1,.5])P3(kRBox(.18,.9,.26,.05),cm('#2a2420',.7),x,2.3,3.05,S);\n"
    "    for(const [dx,dy] of [[-.5,.25],[.3,.05],[-.1,-.35]])kAdd(new THREE.CylinderGeometry(.16,.16,.05,12),cm('#c53b22',.4),-.3+dx,2.3+dy,3.08,S,Math.PI/2);",
    "const sp=kAdd(KG.slice,SH.cheese,-.3,2.3,2.98,S,0,0,-Math.PI/2,.34,.34,.08);for(const x of [-.05,.7])P3(kRBox(.18,.9,.26,.05),cm('#2a2420',.7),x,2.3,3.05,S);\n"
    "    kAdd(KG.crust,SH.crust,-.36,2.3,2.98,S,0,0,0,.2,.29,.12);/* (patch 87: the slice's crust along its wide end; pepperoni and straps on the slice, not behind it) */\n"
    "    for(const [dx,dy] of [[.6,.35],[.7,-.32],[1.45,0]])kAdd(new THREE.CylinderGeometry(.16,.16,.05,12),cm('#c53b22',.4),-.3+dx,2.3+dy,3.08,S,Math.PI/2);")
rep("d=rad/Math.sin(Math.min(vh,hh))*(gBig?.95:.84+.12*ga)*gZc,",
    "d0=rad/Math.sin(Math.min(vh,hh))*(gBig?.95:.84+.12*ga)*gZc,el0=.22+gPc,yM=12.6,"
    "d=Math.sin(el0)>.02&&ty+Math.sin(el0)*d0>yM?Math.max(Math.min(d0,rad*1.7),(yM-ty)/Math.sin(el0)):d0/* (patch 87: under the studio's ceiling: closer first) */,")
rep("el=.22+gPc,hz=Math.cos(el)*d", "el=Math.min(el0,Math.asin(clamp((yM-ty)/d,-1,1)))/* (then no higher) */,hz=Math.cos(el)*d")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patch 87 applied')
