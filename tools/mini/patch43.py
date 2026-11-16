"""Patch 43 (web v206; Sandbox only, nothing a race reads): Sandbox at night.
The owner, 2026-11-16: "When it's nighttime on the tracks make those little white lines we added to the walls on the hot wheels maps light up
like leds and make the shadows and lighting looks good. Do this for every map in sandbox but maybe for some add street lights or for more off
road type of maps give the cars headlights instead".
- The toy tracks' wall dashes (toyRails, material toydash, now tagged userData.led) glow a cool white as the lamps come on (SB clock's L).
- Headlights on the kart you drive, under every open sky (the pizzas, the back garden): a spot light ahead of it, on as the lamps come on;
  it throws shadows except on the Lite and Fast settings.
- Street lamps on the road-like places (SB_LAMPS: Sauce Spiral, Basil Boulevard, Neon Napoli, Topping Tour): posts beside the road every
  ~300 units, glowing heads, a pool of light on the ground under each, and a few real lights (3; 2 on Lite / Fast) that move to the lamps
  nearest you, so the karts and the road are lit by them without a light per lamp.
- The neon places are night already and are left as they are; the house's rooms keep their own lamps.
Everything is built when a place is armed (sbClockArm) into SB.grp, so it goes with the place. Run once: py.cmd tools/mini/patch43.py"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'patch 43' not in s, 'already patched'


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:90])
    s = s.replace(a, b)


rep("dm.receiveShadow=true;dm.userData.noLift=true;dm.userData.noMerge=true;world.add(dm);}}",
    "dm.receiveShadow=true;dm.userData.noLift=true;dm.userData.noMerge=true;dm.userData.led=1;/* (patch 43: Sandbox lights them at night) */world.add(dm);}}")
rep("  sbClockApply();}\n/* the materials the clock touches",
    "  try{sbNightArm();}catch(e){console.warn('night',e);}sbClockApply();}\n/* the materials the clock touches")
rep("  if(im)im.instanceMatrix.needsUpdate=true;try{sbShopFrame(time);}",
    "  if(im)im.instanceMatrix.needsUpdate=true;try{sbNightFrame(time);}catch(e){console.warn('night',e);}try{sbShopFrame(time);}")
NEW = r"""/* ================= (patch 43) SANDBOX AT NIGHT: LED strips on the toy tracks, headlights, street lamps ================= */
const SB_LAMPS=new Set(['spiral','basil','napoli','tour']);
function sbNightArm(){const R=SBC.rec,def=MAPS[mapIdx];SBC.night=null;if(!R||!SB.grp)return;const Nt=SBC.night={led:[],spot:null,lamps:[],pool:[],head:null,glow:null,pick:0};
  const halos=[];world.traverse(o=>{if(o.userData&&o.userData.led&&o.material){if(Nt.led.indexOf(o.material)<0){Nt.led.push(o.material);o.material.emissive=new THREE.Color('#8fd0ff');o.material.emissiveIntensity=0;}halos.push(o);}});
  if(halos.length){/* the glow round each dash: the same strips again, drawn adding light, a little proud of the wall */const hm=new THREE.MeshBasicMaterial({color:'#6fc2ff',transparent:true,opacity:0,blending:THREE.AdditiveBlending,depthWrite:false,side:THREE.DoubleSide,toneMapped:false,polygonOffset:true,polygonOffsetFactor:-6,polygonOffsetUnits:-6});
    for(const o of halos){const h=new THREE.Mesh(o.geometry,hm);h.position.copy(o.position);h.scale.setScalar(1.0);h.renderOrder=3;SB.grp.add(h);}Nt.halo=hm;}
  const lite=!QUAL[qKey]||QUAL[qKey].lite||qKey==='fast';
  if(R.kind==='out'){/* headlights: one spot light just ahead of the kart, looking down the road */const sp=new THREE.SpotLight('#fff1d8',0,420,.5,.55,1.0);sp.castShadow=!lite;
    if(sp.castShadow){sp.shadow.mapSize.set(1024,1024);sp.shadow.camera.near=3;sp.shadow.camera.far=560;sp.shadow.bias=-.0005;}SB.grp.add(sp);SB.grp.add(sp.target);Nt.spot=sp;
    /* the beam on the ground: a cone 18 wide at the kart and 90 wide 174 ahead, its light in the vertices (brightest close in, fading to the edges and the far end) */
    const bg=new THREE.PlaneGeometry(1,1,6,12),bp=bg.attributes.position,base=new Float32Array(bp.count*2),col=new Float32Array(bp.count*3);for(let i=0;i<bp.count;i++){const f=bp.getY(i)+.5,ac=bp.getX(i)*2,u=4+f*170,v=ac*(9+f*36);base[i*2]=u;base[i*2+1]=v;
      const e=1.6*Math.pow(1-f,.75)*Math.pow(Math.max(0,1-Math.abs(ac)),1.2)*(f<.04?f/.04:1);col[i*3]=e;col[i*3+1]=e*.95;col[i*3+2]=e*.84;}bg.setAttribute('color',new THREE.Float32BufferAttribute(col,3));
    const beam=new THREE.Mesh(bg,new THREE.MeshBasicMaterial({vertexColors:true,transparent:true,opacity:0,depthWrite:false,blending:THREE.AdditiveBlending,toneMapped:false,side:THREE.DoubleSide,polygonOffset:true,polygonOffsetFactor:-4,polygonOffsetUnits:-4}));
    beam.userData.base=base;beam.renderOrder=2;beam.frustumCulled=false;SB.grp.add(beam);Nt.beam=beam;}
  if(SB_LAMPS.has(def.id)&&R.kind==='out'){const sp=T.L/N,step=Math.max(1,Math.round(300/sp)),pts=[];let side=1;
    for(let j=0;j<N;j+=step){const p=track[j];if(p.cut||(p.ey||0)>4)continue;side=-side;const o=WALLD+12,x=p.x+p.nx*o*side,z=p.y+p.ny*o*side,g=groundAt(x,z);
      if(WATER_Y!=null&&g<WATER_Y+1)continue;if(typeof nearSC==='function'&&nearSC(x,z,SCW+12))continue;if(nearTrack(x,z,WALLD+4))continue;if(sbBlocked(x,z,g+1))continue;if(Math.abs(g-groundAt(p.x,p.y)-(p.ey||0))>18)continue;
      pts.push({x,z,g,hx:x-p.nx*side*9,hz:z-p.ny*side*9,a:Math.atan2(-p.ny*side,-p.nx*side)});}
    if(pts.length){const H=48,pole=new THREE.InstancedMesh(new THREE.CylinderGeometry(.55,.85,H,8),new THREE.MeshStandardMaterial({color:'#4a4f57',roughness:.55,metalness:.4}),pts.length),
        arm=new THREE.InstancedMesh(new THREE.BoxGeometry(11,.7,.7),pole.material,pts.length),
        hm=new THREE.MeshStandardMaterial({color:'#3a3d42',roughness:.4,emissive:new THREE.Color('#ffd7a0'),emissiveIntensity:0}),head=new THREE.InstancedMesh(new THREE.BoxGeometry(5,1.3,2.6),hm,pts.length);
      const c=cnv(128,128),g2=c.getContext('2d'),gr=g2.createRadialGradient(64,64,0,64,64,64);gr.addColorStop(0,'rgba(255,214,160,.9)');gr.addColorStop(.45,'rgba(255,200,140,.35)');gr.addColorStop(1,'rgba(255,190,120,0)');g2.fillStyle=gr;g2.fillRect(0,0,128,128);
      const gm=new THREE.MeshBasicMaterial({map:T2(c),transparent:true,opacity:0,depthWrite:false,blending:THREE.AdditiveBlending,polygonOffset:true,polygonOffsetFactor:-4,toneMapped:false}),glow=new THREE.InstancedMesh(new THREE.PlaneGeometry(80,80),gm,pts.length);
      const M=new THREE.Matrix4(),Q=new THREE.Quaternion(),E=new THREE.Euler(),P=new THREE.Vector3(),S=new THREE.Vector3(1,1,1);
      pts.forEach((q,i)=>{P.set(q.x,q.g+H/2,q.z);M.compose(P,Q.identity(),S);pole.setMatrixAt(i,M);E.set(0,-q.a,0);Q.setFromEuler(E);P.set((q.x+q.hx)/2,q.g+H-.5,(q.z+q.hz)/2);M.compose(P,Q,S);arm.setMatrixAt(i,M);
        P.set(q.hx,q.g+H-1.6,q.hz);M.compose(P,Q,S);head.setMatrixAt(i,M);E.set(-Math.PI/2,0,0);Q.setFromEuler(E);const gg=groundAt(q.hx,q.hz);P.set(q.hx,gg+.4,q.hz);M.compose(P,Q,S);glow.setMatrixAt(i,M);
        SB.shapes.push({t:'cyl',x:q.x,z:q.z,r:1.6,b:q.g-1,h:q.g+H,night:1});q.ly=q.g+H-4;});
      for(const m of [pole,arm,head]){m.castShadow=true;m.receiveShadow=true;SB.grp.add(m);}glow.renderOrder=2;SB.grp.add(glow);
      Nt.lamps=pts;Nt.head=hm;Nt.glow=gm;for(let i=0;i<(lite?2:3);i++){const l=new THREE.PointLight('#ffcf95',0,170,1.6);l.position.set(pts[0].hx,pts[0].ly,pts[0].hz);SB.grp.add(l);Nt.pool.push(l);}}}}
/* each frame: the night's lights follow the hour (the clock's L: 0 by day, 1 at night) and the kart */
function sbNightFrame(time){const Nn=SBC.night;if(!Nn||!SBC.rec||!SBX)return;const L=sbClockF().L,on=L>.02;
  for(const m of Nn.led)m.emissiveIntensity=2.4*L;if(Nn.halo)Nn.halo.opacity=.85*L;
  const k=camT||player;if(Nn.spot&&k){const sp=Nn.spot;sp.intensity=on?5.5*L:0;sp.visible=on;if(on){const a=k.rma!=null?k.rma:k.ma,x=k.rx!=null?k.rx:k.x,z=k.ry!=null?k.ry:k.y,y=(k.rz!=null?k.rz:k.wy)||0;
      sp.position.set(x+Math.cos(a)*7,y+6.5,z+Math.sin(a)*7);sp.target.position.set(x+Math.cos(a)*80,y-9,z+Math.sin(a)*80);sp.target.updateMatrixWorld();}}
  if(Nn.beam&&k){const b=Nn.beam;b.visible=L>.02;b.material.opacity=.9*L;if(b.visible){const a=k.rma!=null?k.rma:k.ma,x=k.rx!=null?k.rx:k.x,z=k.ry!=null?k.ry:k.y,gnd=(px,pz)=>sbG(px,pz,((k.rz!=null?k.rz:k.wy)||0)+8);
      /* lying on the ground from the front of the kart to 120 ahead: each row of the strip set down on the ground under it */const P=b.geometry.attributes.position,ca=Math.cos(a),sa=Math.sin(a);
      const B0=b.userData.base;for(let i=0;i<P.count;i++){const u=B0[i*2],v=B0[i*2+1],wx=x+ca*u-sa*v,wz=z+sa*u+ca*v;P.setXYZ(i,wx,gnd(wx,wz)+.5,wz);}
      P.needsUpdate=true;b.position.set(0,0,0);b.rotation.set(0,0,0);b.geometry.computeBoundingSphere();}}
  if(Nn.lamps.length){if(Nn.head)Nn.head.emissiveIntensity=on?.4+2.6*L:0;if(Nn.glow)Nn.glow.opacity=.55*L;
    if(k&&on&&time-Nn.pick>.25){Nn.pick=time;const x=k.x,z=k.y,best=Nn.lamps.map(q=>[(q.hx-x)**2+(q.hz-z)**2,q]).sort((a,b)=>a[0]-b[0]);Nn.pool.forEach((l,i)=>{const q=best[i]&&best[i][1];if(q)l.position.set(q.hx,q.ly,q.hz);});}
    for(const l of Nn.pool){l.intensity=on?1.9*L:0;l.visible=on;}}}
"""
rep("/* the materials the clock touches, listed once", NEW + "/* the materials the clock touches, listed once")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patch 43 applied')
