"""Patch 92 (web v228): calipers added to the cars whose wheels showed none: Grand Coupe, Megawatt, Luxury SUV.
The owner, shown the prototype (scratch/paint/addcal3.js): "dont worry about the calipers for bikes the rest look good".
- WHEEL_ADDCAL: the cars. addCal(wh, yaw, M, id): a caliper over the brake disc's edge at the disc's rear top (a rounded annular
  sector, ExtrudeGeometry with a bevel): radially from half the disc's radius to 1.14x it (never past 95% of the tyre's inner
  radius), its depth the disc's (at most 12% of the wheel's radius) plus 16%, centred on the disc but kept 4% of the radius behind the
  spokes' innermost point. Class 13 (stock caliper red, CAR_COL), built once per wheel geometry. It goes in the steering group as a
  held part (userData.held): it steers, does not roll, takes the Calipers colour, and the PC gets it with the wheel's ph<i> node.
Run once, after patch 91: tools/py.cmd tools/mini/patch92.py"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'patch 92' not in s, 'already patched'


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:90])
    s = s.replace(a, b)


rep("function buildWheel(type,side,M){", r"""/* (patch 92) a caliper for the cars whose wheels show none: over the brake disc's edge at its rear top, behind the spokes */
const WHEEL_ADDCAL={coupe:1,megawatt:1,suv:1};
function addCalGeo(geo,os,id){const k='addcal'+os;if(geo.userData[k]!==undefined)return geo.userData[k];geo.userData[k]=null;const P=geo.attributes.position,uv=geo.attributes.uv;if(!uv)return null;
  let R=0,rd=0,z=0,n=0,z0=1e9,z1=-1e9;const rt=[];for(let i=0;i<P.count;i++){const q=Math.hypot(P.getX(i),P.getY(i));R=Math.max(R,q);const c=Math.floor(uv.getX(i)*32);if(c===12){rd=Math.max(rd,q);z+=P.getZ(i);n++;z0=Math.min(z0,P.getZ(i));z1=Math.max(z1,P.getZ(i));}if(c===8)rt.push(q);}
  if(!n||!rt.length)return null;rt.sort((a,b)=>a-b);const inner=rt[Math.floor(rt.length*.02)],sp=WHEEL_SPOKES[id]||[11];let si=1e9;
  for(let i=0;i<P.count;i++){const c=Math.floor(uv.getX(i)*32);if(sp.includes(c)&&Math.hypot(P.getX(i),P.getY(i))<inner*.95)si=Math.min(si,P.getZ(i)*os);}
  const th=Math.min(z1-z0,R*.12),r0=rd*.5,r1=Math.min(rd*1.14,inner*.95),a=.5,ang=Math.PI*.8,sh=new THREE.Shape();sh.absarc(0,0,r1,ang-a,ang+a,false);sh.absarc(0,0,r0,ang+a*.86,ang-a*.86,true);sh.closePath();
  const dep=Math.max(th,R*.03)+R*.16,g=new THREE.ExtrudeGeometry(sh,{depth:dep,bevelEnabled:true,bevelThickness:R*.03,bevelSize:R*.03,bevelSegments:3,curveSegments:10});
  let zc=z/n;if(si<1e9&&zc*os+dep/2+R*.04>si)zc=(si-dep/2-R*.04)*os;g.translate(0,0,zc-dep/2);
  const m=g.attributes.position.count,C=new Float32Array(m*3),U=new Float32Array(m*2),cc=new THREE.Color(CAR_COL.caliper);for(let i=0;i<m;i++){C[i*3]=cc.r;C[i*3+1]=cc.g;C[i*3+2]=cc.b;U[i*2]=(13+.5)/32;U[i*2+1]=.5;}
  g.setAttribute('color',new THREE.BufferAttribute(C,3));g.setAttribute('uv',new THREE.BufferAttribute(U,2));g.computeVertexNormals();CARGEO.add(g);return geo.userData[k]=g;}
function addCal(wh,yaw,M,id){if(!WHEEL_ADDCAL[id]||!wh||!wh.isMesh||!yaw)return;const os=Math.sign(yaw.position.z)||1,g=addCalGeo(wh.userData.geo0||wh.geometry,os,id);if(!g)return;
  const m=new THREE.Mesh(g,(M&&M.st&&rimVC(M.st,0,id,null,[]))||SH.carVC);m.position.copy(wh.position);m.rotation.copy(wh.rotation);m.scale.copy(wh.scale);m.castShadow=false;m.userData.held=1;yaw.add(m);}
function buildWheel(type,side,M){""")
rep("else if(cfg.car&&wt.id==='standard')holdOut(wh,yaw,M,cfg.car,0,cfg.car);",
    "else if(cfg.car&&wt.id==='standard'){holdOut(wh,yaw,M,cfg.car,0,cfg.car);addCal(wh,yaw,M,cfg.car);}/* (patch 92) */")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patch 92 applied')
