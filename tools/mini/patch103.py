"""Patch 103 (web v236): body calipers the same on both sides; every car's body calipers hide on a wheel type.
The owner (Scissor and Mega GT in the garage, both sides): "The calipers show up correct on one side of these cars but not the other
... make sure they are lined up correctly".
Measured on the detailed packs the garage uses (scratch/paint/calz.js, wind.js): every car's calipers sit at the same place and depth
on both sides, but the Scissor's on its left (-z) side are inside out (wound against their normals: -0.82), so they draw as their
back faces, see-through; and the detailed Mega GT has body calipers its standard pack lacks, so a wheel set on it showed two.
- bodyCalSplit runs on every car body (not just BODY_CAL): its calipers in their own mesh, hidden on any wheel type.
- a caliper triangle wound against its normals is turned (its index order swapped), on both packs.
- PC: from the export (bcal; the export builds the detailed bodies).
Run once, after patch 102: tools/py.cmd tools/mini/patch103.py"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'patch 103' not in s, 'already patched'


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:90])
    s = s.replace(a, b)


rep("  if(BODY_CAL[cid]&&g.b_vc){", "  if(g.b_vc){/* (patch 103: every car) */")
rep("cal=hw.some(q=>Math.hypot(x-q.c[0],y-q.c[1])<q.r*1.1&&Math.abs(z-q.c[2])<q.r);}(cal?b:a).push(I[t],I[t+1],I[t+2]);}",
    "cal=hw.some(q=>Math.hypot(x-q.c[0],y-q.c[1])<q.r*1.1&&Math.abs(z-q.c[2])<q.r);}\n"
    "    if(cal&&geo.attributes.normal){/* (patch 103) an inside-out caliper face is turned */const N=geo.attributes.normal,A=new THREE.Vector3().fromBufferAttribute(P,I[t]),B=new THREE.Vector3().fromBufferAttribute(P,I[t+1]),C=new THREE.Vector3().fromBufferAttribute(P,I[t+2]);\n"
    "      const fn=B.sub(A).cross(C.sub(A)),vn=new THREE.Vector3(N.getX(I[t])+N.getX(I[t+1])+N.getX(I[t+2]),N.getY(I[t])+N.getY(I[t+1])+N.getY(I[t+2]),N.getZ(I[t])+N.getZ(I[t+1])+N.getZ(I[t+2]));\n"
    "      if(fn.dot(vn)<0){b.push(I[t],I[t+2],I[t+1]);continue;}}\n"
    "    (cal?b:a).push(I[t],I[t+1],I[t+2]);}")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patch 103 applied')
