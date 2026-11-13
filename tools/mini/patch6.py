# sixth engine patch (v155): dropped traps (olive slicks, oil, forks, pizza boxes, fire) were drawn at floor height on
# multi-level tracks, so on raised road they lay out of sight underneath while still hitting karts on the road above.
# Looks only: the hit test is unchanged, so nothing here affects online play. Run once: py.cmd tools\mini\patch6.py
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (a[:70], s.count(a)); s = s.replace(a, b)
rep("function eyAt(j,t){",
    """/* The road height under a dropped trap on a multi-level track. Worked out once, from the level its owner was driving on when it was
   dropped (a spiral passes over itself, so the nearest stretch of road is not always the right one); a trap with no owner close by
   (lobbed, or one that arrived over the network) takes the nearest stretch, the upper one where two cross. */
function hazEy(h){if(!MULTI)return 0;const o=h.owner;let j=-1;if(o&&typeof o.idx==='number'&&(o.x-h.x)**2+(o.y-h.y)**2<3600)j=o.idx;
  if(j<0){let bd=1e9;for(let i=0;i<N;i++){const p=track[i],d=(p.x-h.x)**2+(p.y-h.y)**2-(p.ey||0)*.01;if(d<bd){bd=d;j=i;}}}
  /* on a slope the trap lies along the road instead of sinking into it */
  const sl=T.L/N,s=((track[(j+1)%N].ey||0)-(track[(j-1+N)%N].ey||0))/(2*sl),p=track[j];if(Math.abs(s)>.02)h.nq=new THREE.Quaternion().setFromUnitVectors(_hzUp,new THREE.Vector3(-p.tx*s,1,-p.ty*s).normalize());
  return kEy({idx:j,x:h.x,y:h.y});}
const _hzUp=new THREE.Vector3(0,1,0);
function eyAt(j,t){""")
rep("h.mesh.position.set(h.x,groundAt(h.x,h.y)+.12,h.y);h.mesh.rotation.y=h.born*.05;",
    "if(h.ey===undefined)h.ey=hazEy(h);h.mesh.position.set(h.x,groundAt(h.x,h.y)+h.ey+.12,h.y);if(h.nq)h.mesh.quaternion.setFromAxisAngle(_hzUp,h.born*.05).premultiply(h.nq);else h.mesh.rotation.y=h.born*.05;")
open(p, 'w', encoding='utf-8', newline='').write(s); print('patched')
