"""Patch 61 (web v217): Sandbox coins with detail, and a shadow under each.
The owner: "make the coins look better in sandbox right now they look basic with very little detail maybe add a shadow for them too".
Was: a plain 22-sided gold cylinder, glowing evenly (emissive .9), no shadow: it read as a flat yellow token.
Now (sbCoinGeo, one geometry for the whole batch, still ONE instanced draw):
  - turned like a real coin: a sunken field, a raised rim with a sloped inner wall and a bevelled outer edge, a reeded (ribbed) edge;
  - on both faces a raised pizza slice: the cheese, a taller crust along the top, three pepperoni (vertex colours: gold field, bright
    rim, darker edge, cheese, crust, red pepperoni), so the spinning coin catches light on every step;
  - less glow (emissive .9 -> .45) so the relief shows, still bright at night.
Shadows (sbCoinShadows): a soft dark ellipse flat on the ground under every coin, turning with it (long across the coin's face, narrow
across it), one more instanced draw; none under the coin that hangs in the air off a bend. A coin's ground is known from how it is put
(plain coins 5.4 above it, the hidden ones 8). Hidden with the coin while it is taken.
The PC loads the same shape: tools/neon/coinexport.py writes godot/assets/sandbox/coin.json from sbCoinGeo.
Run once: py.cmd tools/mini/patch61.py"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'patch 61' not in s, 'already patched'


def rep(a, b):
    global s
    assert s.count(a) == 1, (s.count(a), a[:90])
    s = s.replace(a, b)


# --- the coin's ground: plain ones 5.4 above it, hidden ones 8; the one hanging off a bend has none
rep("  if(R.air==='auto'){/* the highest part of the track that is on a bend:",
    "  const nAir=C.length;/* (patch 61: coins from here on hang in the air: no shadow) */\n  if(R.air==='auto'){/* the highest part of the track that is on a bend:")
rep("  for(const c of C)if(c.rare&&sv.r[c.id])c.t=-1;/* found for good */",
    "  C.forEach((c,i)=>{c.gy=i>=nAir&&c.rare?null:c.y-(c.rare?8:5.4);});/* where its shadow lies (patch 61) */\n"
    "  for(const c of C)if(c.rare&&sv.r[c.id])c.t=-1;/* found for good */")

# --- the plain coins: the detailed shape, vertex coloured
rep("  const g=new THREE.CylinderGeometry(4.2,4.2,.9,22);g.rotateX(Math.PI/2);const plain=C.filter(c=>!c.rare),im=SB.im=new THREE.InstancedMesh(g,new THREE.MeshStandardMaterial({color:'#ffc93a',roughness:.28,metalness:.85,emissive:'#a86a00',emissiveIntensity:.9}),Math.max(1,plain.length));",
    "  const g=sbCoinGeo();const plain=C.filter(c=>!c.rare),im=SB.im=new THREE.InstancedMesh(g,new THREE.MeshStandardMaterial({color:'#ffffff',vertexColors:true,roughness:.3,metalness:.85,emissive:'#8a5800',emissiveIntensity:.45}),Math.max(1,plain.length));/* (patch 61: the detailed coin) */")
rep("  im.frustumCulled=false;im.castShadow=false;im.userData.sunlit=true;SB.grp.add(im);plain.forEach((c,i)=>c.i=i);",
    "  im.frustumCulled=false;im.castShadow=false;im.userData.sunlit=true;SB.grp.add(im);plain.forEach((c,i)=>c.i=i);sbCoinShadows(C);")

# --- the shape, the shadows
rep("function sbFound(){",
    r"""/* (patch 61) the Sandbox coin: turned like a real coin, its face along z, 8.5 across, about 1 thick. A profile (radius, z) from the
   back's centre round the edge to the front's centre is spun round z (each profile step keeps its own normal: crisp steps, round
   the other way); the edge band is reeded; a raised pizza slice (cheese, crust, three pepperoni) sits on each face. One geometry,
   vertex coloured, not indexed. The PC reads the same triangles (tools/neon/coinexport.py -> godot/assets/sandbox/coin.json). */
function sbCoinGeo(){if(SB.coinGeo)return SB.coinGeo;const P=[],N=[],Cl=[],col=h=>{const c=new THREE.Color(h);return [c.r,c.g,c.b];};
  const SEG=40,H=[[0,-.3,'#e8aa2a'],[2.85,-.3,'#e8aa2a'],[3.05,-.46,'#ffcf45'],[3.5,-.54,'#ffcf45'],[3.95,-.5,'#ffcf45'],[4.25,-.3,'#d99a20'],[4.25,.3,'#d99a20'],[3.95,.5,'#ffcf45'],[3.5,.54,'#ffcf45'],[3.05,.46,'#ffcf45'],[2.85,.3,'#e8aa2a'],[0,.3,'#e8aa2a']];
  for(let e=0;e+1<H.length;e++){const [r0,z0,c0]=H[e],[r1,z1]=H[e+1],dr=r1-r0,dz=z1-z0,L=Math.hypot(dr,dz),nr=dz/L,nz=-dr/L,reed=e===5,k=col(c0);
    const at=(i,r,z)=>{const t=i/SEG*Math.PI*2,rr=reed?r+(i%2?.07:-.03):r;return [Math.cos(t)*rr,Math.sin(t)*rr,z];},nAt=i=>{const t=i/SEG*Math.PI*2,tw=reed?(i%2?1:-1)*.35:0;
      /* a reed's flanks tilt its normal round the rim, so the ribs catch light */const x=Math.cos(t)*nr-Math.sin(t)*tw,y=Math.sin(t)*nr+Math.cos(t)*tw,l=Math.hypot(x,y,nz);return [x/l,y/l,nz/l];};
    for(let i=0;i<SEG;i++){const a0=at(i,r0,z0),a1=at(i+1,r0,z0),b0=at(i,r1,z1),b1=at(i+1,r1,z1),n0=nAt(i),n1=nAt(i+1),mid=[(n0[0]+n1[0])/2,(n0[1]+n1[1])/2,nz];
      const T=(a,b,c,na,nb,nc)=>{const u=[b[0]-a[0],b[1]-a[1],b[2]-a[2]],v=[c[0]-a[0],c[1]-a[1],c[2]-a[2]],f=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]];
        if(f[0]*mid[0]+f[1]*mid[1]+f[2]*mid[2]<0){P.push(...a,...c,...b);N.push(...na,...nc,...nb);}else{P.push(...a,...b,...c);N.push(...na,...nb,...nc);}Cl.push(...k,...k,...k);};
      if(r0>0)T(a0,a1,b1,n0,n1,n1);if(r1>0)T(a0,b1,b0,n0,n1,n0);}}
  /* the emblem: extruded flat shapes, set into the field of each face */
  const sh=[],slice=new THREE.Shape();slice.moveTo(0,-2.2);slice.lineTo(1.7,1.0);slice.lineTo(-1.7,1.0);slice.closePath();sh.push([slice,.16,'#ffe27a']);
  const crust=new THREE.Shape();crust.moveTo(-2.0,.88);crust.quadraticCurveTo(0,2.3,2.0,.88);crust.lineTo(1.62,1.02);crust.quadraticCurveTo(0,1.8,-1.62,1.02);crust.closePath();sh.push([crust,.27,'#f0a52c']);
  for(const [x,y] of [[0,-.95],[-.62,.28],[.62,.3]]){const c=new THREE.Shape();c.absarc(x,y,.42,0,Math.PI*2,false);sh.push([c,.24,'#c4452a']);}
  for(const [S,d,h] of sh){const eg=new THREE.ExtrudeGeometry(S,{depth:d,bevelEnabled:false,curveSegments:8}),g=eg.index?eg.toNonIndexed():eg;g.computeVertexNormals();const p=g.attributes.position.array,n=g.attributes.normal.array,k=col(h);
    for(const side of [1,-1])for(let i=0;i<p.length;i+=9){const v=[0,3,6].map(o=>[p[i+o],p[i+o+1],side*(p[i+o+2]+.28)]),w=[0,3,6].map(o=>[n[i+o],n[i+o+1],side*n[i+o+2]]);
      const ord=side>0?[0,1,2]:[0,2,1];/* (the back's copy is mirrored: its triangles turned round to face out) */for(const o of ord){P.push(...v[o]);N.push(...w[o]);Cl.push(...k);}}
    eg.dispose();}
  const G=new THREE.BufferGeometry();G.setAttribute('position',new THREE.Float32BufferAttribute(P,3));G.setAttribute('normal',new THREE.Float32BufferAttribute(N,3));G.setAttribute('color',new THREE.Float32BufferAttribute(Cl,3));G.computeBoundingSphere();return SB.coinGeo=G;}
/* (patch 61) a soft shadow flat on the ground under each coin: a dark ellipse turning with the coin; one instanced draw */
let _sbShT=null;function sbShadowTex(){if(_sbShT)return _sbShT;const c=cnv(64,64),g=c.getContext('2d'),gr=g.createRadialGradient(32,32,1,32,32,31);gr.addColorStop(0,'rgba(0,0,0,.85)');gr.addColorStop(.55,'rgba(0,0,0,.55)');gr.addColorStop(1,'rgba(0,0,0,0)');g.fillStyle=gr;g.fillRect(0,0,64,64);return _sbShT=new THREE.CanvasTexture(c);}
function sbCoinShadows(C){const L=C.filter(c=>c.gy!=null);SB.shIm=null;if(!L.length)return;const pg=new THREE.PlaneGeometry(1,1);pg.rotateX(-Math.PI/2);
  const m=new THREE.MeshBasicMaterial({map:sbShadowTex(),transparent:true,depthWrite:false,polygonOffset:true,polygonOffsetFactor:-2,polygonOffsetUnits:-4,fog:true}),im=SB.shIm=new THREE.InstancedMesh(pg,m,L.length);
  im.frustumCulled=false;im.castShadow=false;im.receiveShadow=false;im.renderOrder=1;L.forEach((c,i)=>{c.si=i;});SB.grp.add(im);}
function sbFound(){""")

# --- each frame: the shadow turns with its coin, gone while the coin is
rep("const im=SB.im;for(const c of SB.coins){const a=time*2.6+c.ph;if(c.rare){if(c.m&&c.m.visible){c.m.rotation.y=a;c.m.position.y=c.y+Math.sin(time*2+c.ph)*.8;}continue;}",
    "const im=SB.im,sh=SB.shIm;for(const c of SB.coins){const a=time*2.6+c.ph;if(sh&&c.si!=null){/* its shadow (patch 61) */const on=c.t===0,big=c.rare?1.5:1,bob=c.rare?1-Math.sin(time*2+c.ph)*.04:1;_sbE.set(0,a,0);_sbQ.setFromEuler(_sbE);_sbP.set(c.x,c.gy+.3,c.z);_sbS.set(on?9.5*big*bob:0,1,on?3.8*big*bob:0);_sbM.compose(_sbP,_sbQ,_sbS);sh.setMatrixAt(c.si,_sbM);}if(c.rare){if(c.m&&c.m.visible){c.m.rotation.y=a;c.m.position.y=c.y+Math.sin(time*2+c.ph)*.8;}continue;}")
rep("  if(im)im.instanceMatrix.needsUpdate=true;try{sbNightFrame(time);}",
    "  if(im)im.instanceMatrix.needsUpdate=true;if(sh)sh.instanceMatrix.needsUpdate=true;try{sbNightFrame(time);}")
rep("coins:SB.coins.map(c=>[+c.x.toFixed(2),+c.y.toFixed(2),+c.z.toFixed(2),c.rare?1:0,c.id||''])",
    "coins:SB.coins.map(c=>[+c.x.toFixed(2),+c.y.toFixed(2),+c.z.toFixed(2),c.rare?1:0,c.id||'',c.gy==null?null:+c.gy.toFixed(2)])/* (patch 61: [5] the ground under it, for its shadow; null: it hangs in the air) */")
s = s.replace("const SB={loops:[]", "/* (patch 61: detailed coins, their shadows) */const SB={loops:[]", 1)
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patch 61 applied')
