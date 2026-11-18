"""Patch 94 (web v229): the Concept's Rims colour on its spokes only, not its barrel.
The owner: "For the concept vehicle make the rim cover only cover the spokes not the barrel it looks weird with the barrel covered in
color". The Concept's spokes and barrel are one piece of one class (dark 1), at the same depth (scratch/paint/concz.js), with white ribs
(class 2) on the barrel. barrelMark labels the barrel 14 (uv only: the stock look stays; the Rims colour leaves it): every rib
triangle, and the dark triangles in the wheel's outer half (over 50% of its radius) whose surface faces away from the axle (a
cylinder: |normal . radial| over .65). The limit at the tyre stays too (WHEEL_CUT), so the lip keeps its colour. PC: pc89 (the cut;
the labels come with the export).
Run once, after patch 93: tools/py.cmd tools/mini/patch94.py"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'patch 94' not in s, 'already patched'


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:90])
    s = s.replace(a, b)


rep("const WHEEL_CUT={monster:1},", "const WHEEL_CUT={monster:1,concept:1}/* (patch 94: the Concept's lip stays) */,")
rep("concept:[1,2],", "concept:[1],")
a = "if(m&&hw[+m[1]])rotorMark(g[k],Math.sign(hw[+m[1]].c[2])||1,WHEEL_SPOKES[cid]||[11]);}}/* (patch 91) */"
rep(a, a + "\n  if(id.replace(/_hq$/,'')==='concept')for(const k in g)if(/^w\\d$/.test(k))barrelMark(g[k]);/* (patch 94) */")
rep("function rotorMark(geo,os,sp){",
    "/* (patch 94) the Concept's barrel (one piece with its spokes): its white ribs, and the dark surface in the outer half facing away from\n"
    "   the axle, are labelled 14 (uv only) */\n"
    "function barrelMark(geo){const P=geo.attributes.position,N=geo.attributes.normal,uv=geo.attributes.uv,I=geo.index&&geo.index.array;if(!uv||!N||!I)return;let R=0;for(let i=0;i<P.count;i++)R=Math.max(R,Math.hypot(P.getX(i),P.getY(i)));if(!(R>0))return;\n"
    "  const mk=[];for(let t=0;t<I.length;t+=3){const c=Math.floor(uv.getX(I[t])*32);if(c!==1&&c!==2)continue;let x=0,y=0,nx=0,ny=0;for(let j=0;j<3;j++){const v=I[t+j];x+=P.getX(v);y+=P.getY(v);nx+=N.getX(v);ny+=N.getY(v);}\n"
    "    const r=Math.hypot(x,y)/3,nr=Math.abs(nx*x+ny*y)/(Math.hypot(x,y)*3||1);if(c===2||(r>.5*R&&nr>.65))mk.push(t);}\n"
    "  for(const t of mk)for(let j=0;j<3;j++)uv.setX(I[t+j],(14+.5)/32);uv.needsUpdate=true;}\n"
    "function rotorMark(geo,os,sp){")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patch 94 applied')
