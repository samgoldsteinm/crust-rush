"""Patch 78 (web v222): no underglow on bikes; karts' underglow sized to their frame, not their wheels.
The owner: "on karts and bikes it doesn't look good. Remove the under glow feature for bikes and fix the size of the under glow for the
karts it's too big for most of them it doesn't look like LEDS coming from under the car".
Bikes (BODIES[b].bike): no strips, no lights, no Underglow row in the garage (a saved colour stays in the build, unused).
Karts (the garage's Kart tab: not a bike, not in CAR_BODIES): the strips sit under the frame between the wheels (b = the median low
half-width there; 77 pushed them out to the wheels' track plus a tyre), and no higher than .45 x the wheel radius; the code-built karts
.85 x their wheel track (was that + 1.1) at .4 x the radius. The spread (M = .45b + 1.5h) follows. Then tools/neon/ugtable.py and pc78.
Run once, after patch 77: py.cmd tools/mini/patch78.py"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'patch 78' not in s, 'already patched'


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:90])
    s = s.replace(a, b)


rep("let b=pct(zs,.97)||(z1-z0)/2;const bike=wz<.25*b;if(!bike)b=Math.max(b,wz+tw*.35);",
    "let b=pct(zs,.97)||(z1-z0)/2;const bike=wz<.25*b,kart=!bike&&!CAR_BODIES.includes(id);\n"
    "    /* (patch 78) a kart: the strips under its frame between the wheels, not out at the wheels */\n"
    "    if(kart){const zm=[];for(let i=0;i<V.length;i+=3){const x=V[i]-cx;if(x>wr+rr&&x<wf-rf&&V[i+1]<y0+rA)zm.push(Math.abs(V[i+2]-cz));}b=pct(zm,.5)||b*.5;}else if(!bike)b=Math.max(b,wz+tw*.35);")
rep("h=Math.min(1.6*rA,Math.max(.25*rA,h));", "h=Math.min(1.6*rA,Math.max(.25*rA,h));if(kart)h=Math.min(h,.45*rA);")
rep("P={a:hx+Math.max(f[2],r[2])+1.5,b:(Math.max(f[1],r[1])+1.3)*.85,cx:(f[0]+r[0])/2,cz:0,h:.45*rA,",
    "P={a:hx+Math.max(f[2],r[2])+1.5,b:Math.max(f[1],r[1])*.85,cx:(f[0]+r[0])/2,cz:0,h:.4*rA,/* (patch 78: under the frame) */")
# bikes: none
rep("const ugLs=[];if(spec.ugL&&!cfg.hover){", "const ugLs=[],ugBike=!!(BODIES[spec.b]&&BODIES[spec.b].bike);/* (patch 78) no underglow on a bike */if(spec.ugL&&!cfg.hover&&!ugBike){")
rep("if(gi&&GLOWS[gi]&&GLOWS[gi].h&&!cfg.hover){/* (patch 77)", "if(gi&&GLOWS[gi]&&GLOWS[gi].h&&!cfg.hover&&!ugBike){/* (patch 77)")
rep("+row('gl','Underglow')+", "+(BODIES[playerBuild.b].bike?'':row('gl','Underglow'))+/* (patch 78) */")
# the garage camera framed the glow too (a bigger glow zoomed the car out); now only the car (the PC measures before adding it)
rep("gModel.g.updateMatrixWorld(true);const bb=new THREE.Box3(),tb=new THREE.Box3();gModel.g.traverseVisible(o=>{if(o.isMesh&&o.geometry){",
    "gModel.g.updateMatrixWorld(true);const bb=new THREE.Box3(),tb=new THREE.Box3();gModel.g.traverseVisible(o=>{if(o.isMesh&&o.geometry&&!(o.material&&o.material.blending===THREE.AdditiveBlending)){/* (patch 78: not the glow) */")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patch 78 applied')
