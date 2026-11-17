"""Patch 75 (web v222): a road place's tunnel arch never stands where another part of the track passes by it, above or below.
The owner: "on sauce spiral in sandbox one of the tunnel entrances is going through the spiral".
A road place (sbGates, SB.kind 'road') puts each arch over the left lane at a lap point clear of bends, jumps, loops and the glide; it did
not look at the rest of the track. On Sauce Spiral the arch to Oven Rush Raceway (lap point 309) stood 50 units beside the spiral's next
level, 60+ units up, which ran through the arch and its sign. clear(j) now also wants no lap point more than 60 points away within
RW x 1.4 + 40 across and between 20 below and 110 above. The PC reads its gates from the export (sbExport), so it follows after the
tracks are re-exported (release_pc does that).
Run once: py.cmd tools/mini/patch75.py"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'patch 75' not in s, 'already patched'


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:90])
    s = s.replace(a, b)


rep("return ramps.every(r=>far(j,r.j,30))&&LOOPS.every(L=>far(j,L.j,40));};",
    "if(!(ramps.every(r=>far(j,r.j,30))&&LOOPS.every(L=>far(j,L.j,40))))return false;"
    "/* (patch 75: no other part of the track beside it, above or below: on Sauce Spiral the next level ran through an arch) */"
    "const p0=track[j],e0=p0.ey||0,R2=(RW*1.4+40)**2;for(let k=0;k<N;k++){if(!far(j,k,60))continue;const q=track[k],dx=q.x-p0.x,dz=q.y-p0.y,dy=(q.ey||0)-e0;if(dx*dx+dz*dz<R2&&dy>-20&&dy<110)return false;}return true;};")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patch 75 applied')
