"""Patch 99 (web v234): the Street Cruiser's wheels clear their fenders; the pieces that spun with them stand still.
The owner: "this bikes wheels are completely going through the covers above them and they have little pieces attached that spin with
them that are supposed to be stationary and apart of the wheel covers".
Measured (scratch/paint/moto2.js, moto3.js): the front tyre reaches 1.99 from its axle (98th percentile) while the front fender's
underside comes down to 1.87; the rear fender clears its tyre. The rear wheel model holds two fender stays and brackets (dark 1, reaching
2.52, past the tyre at 1.87), and both wheels carry metal arcs (7) out at the tyre; patch 88's rule held only the rear's arcs.
- WHEEL_HOLD bike_moto {outer:.9}: every piece that is not tyre and reaches past 90% of the tyre's radius is held (still, steering).
- WHEEL_SCALE: the Street Cruiser's front wheel (w1) at .94 of its size about its axle (tyre 1.87): it clears the fender, and floats at
  most .05 above the ground (the wheel's place and the physics are unchanged).
- PC: from the export (pw / ph nodes).
Run once, after patch 98: tools/py.cmd tools/mini/patch99.py"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'patch 99' not in s, 'already patched'


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:90])
    s = s.replace(a, b)


rep("bike_moto:{cls:[7]}", "bike_moto:{outer:.9}/* (patch 99: all that reaches the tyre) */")
rep("  const L=[...C.values()],hold=new Set();for(const c of L){const n=c.t.length,top=+Object.entries(c.cl).sort((a,b)=>b[1]-a[1])[0][0];\n",
    "  const L=[...C.values()],hold=new Set();let RT=0;if(rule.outer){const rr=[];for(let i=0;i<P.count;i++)if(uv&&Math.floor(uv.getX(i)*32)===8)rr.push(Math.hypot(P.getX(i),P.getY(i)));rr.sort((a,b)=>a-b);RT=rr.length?rr[Math.floor(rr.length*.98)]:R;}\n"
    "  for(const c of L){const n=c.t.length,top=+Object.entries(c.cl).sort((a,b)=>b[1]-a[1])[0][0];\n"
    "    if(rule.outer){if(top!==8&&c.r1*R>rule.outer*RT)for(const t of c.t)hold.add(t);continue;}/* (patch 99) */\n")
rep("  {const bd=BODIES.find(b=>b.id===id.replace(/_hq$/,''));if(bd&&bd.bike)for(const k in g)if(/^w\\d$/.test(k))wheelTrim(g[k]);}/* (patch 85) */",
    "  {const bd=BODIES.find(b=>b.id===id.replace(/_hq$/,''));if(bd&&bd.bike)for(const k in g)if(/^w\\d$/.test(k))wheelTrim(g[k]);}/* (patch 85) */\n"
    "  {const ws=WHEEL_SCALE[id.replace(/_hq$/,'')];if(ws)for(const k in ws)if(g[k])g[k].scale(ws[k],ws[k],1);}/* (patch 99) */")
rep("const WHEEL_HOLD={", "/* (patch 99) a bike wheel shrunk about its axle to clear its fender */const WHEEL_SCALE={bike_moto:{w1:.94}};\nconst WHEEL_HOLD={")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patch 99 applied')
