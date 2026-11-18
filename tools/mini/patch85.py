"""Patch 85 (web v225): a bike's wheels no longer carry pieces of its bodywork round with them.
The owner (the Street Cruiser in the garage): "there are wheel covers already on the bike and then also some that are on the wheel
spinning with it. Let's remove the ones that are spinning since the bike already has them".
Why: the downloaded bike models had their fenders, a tail-light piece and seat trim cut into the WHEEL meshes when they were converted
(car_convert took everything inside the wheel's box): bike_moto's wheel holds paint 0, tail 3, seat 9 and fender struts reaching past
the tyre; bike_mx's paint, stripe and glass. The body has its own fenders, so these spun as a second set.
wheelTrim (in carGeos, bikes only): a wheel keeps its tyre (class 8) whole and any other triangle only if it lies well inside the tyre
(centre within 90% of the tyre's outer radius: fender arcs and their brackets hug the tread) and is not body paint, stripe, tail lamp, glass or seat (classes 0, 2, 3, 5, 9). The PC takes its wheels
from the export of the web game, so it follows on the next export.
Run once, after patch 84: py.cmd tools/mini/patch85.py"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'patch 85' not in s, 'already patched'


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:90])
    s = s.replace(a, b)


rep("  p.d=null;p.b=null;p.g=g;return g;}",
    "  {const bd=BODIES.find(b=>b.id===id.replace(/_hq$/,''));if(bd&&bd.bike)for(const k in g)if(/^w\\d$/.test(k))wheelTrim(g[k]);}/* (patch 85) */\n"
    "  p.d=null;p.b=null;p.g=g;return g;}\n"
    "/* (patch 85) a bike's wheel: only what lies within its tyre and is wheel (no fender, lamp or seat that the conversion cut into it) */\n"
    "function wheelTrim(geo){const P=geo.attributes.position,uv=geo.attributes.uv,I=geo.index;if(!uv||!I)return;let R=0;\n"
    "  for(let i=0;i<P.count;i++)if(Math.floor(uv.getX(i)*32)===8)R=Math.max(R,Math.hypot(P.getX(i),P.getY(i)));if(!(R>0))return;\n"
    "  const A=I.array,keep=[],drop=new Set([0,2,3,5,9]);for(let t=0;t<A.length;t+=3){const a=A[t],b=A[t+1],c=A[t+2],cx=(P.getX(a)+P.getX(b)+P.getX(c))/3,cy=(P.getY(a)+P.getY(b)+P.getY(c))/3;\n"
    "    const cl=Math.floor(uv.getX(a)*32);if(cl!==8&&(Math.hypot(cx,cy)>R*.9||drop.has(cl)))continue;keep.push(a,b,c);}/* (the tyre whole; anything else out at the tyre is a fender) */\n"
    "  geo.setIndex(new THREE.BufferAttribute(A instanceof Uint32Array?new Uint32Array(keep):new Uint16Array(keep),1));}")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patch 85 applied')
