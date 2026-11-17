"""Patch 63 (web v217): the pepperoni coin and the mission coin made like the new gold coin (patch 61).
The owner: "Let's make the mission coin and pepperoni coin better too".
Was: the hidden pepperoni coin a flat red disc, a torus and six flat dots; a mission's marker a flat picture (a sprite) of its icon.
Now sbCoinGeo(kind) makes three coins from the one turned profile (raised rim, sunken field, reeded edge):
  gold  the plain coin (as patch 61);
  pep   1.5 x as wide, 1.3 x as thick: a gold rim round a pepperoni-red face, six raised pepperoni slices and cheese flecks on each face;
  act   1.65 x as wide: a gold medallion with a cream field; the mission's icon (sbActIcon) laid on both faces.
The mission medallion turns and bobs over its ring (it was a picture that only rocked) and casts the coins' soft shadow.
The PC reads the same shapes (tools/neon/coinexport.py: coin_pep.json, coin_act.json and the three icons as PNGs).
Run once: py.cmd tools/mini/patch63.py"""
import re
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'patch 63' not in s, 'already patched'


def rep(a, b):
    global s
    assert s.count(a) == 1, (s.count(a), a[:90])
    s = s.replace(a, b)


# --- one profile, three coins
rep("function sbCoinGeo(){if(SB.coinGeo)return SB.coinGeo;const P=[],N=[],Cl=[],col=h=>{const c=new THREE.Color(h);return [c.r,c.g,c.b];};",
    "function sbCoinGeo(kind){kind=kind||'gold';/* (patch 63: gold, pep, act) */const K={gold:[1,1,'#e8aa2a'],pep:[1.5,1.3,'#b3241a'],act:[1.65,1.25,'#fff4dc']}[kind],SR=K[0],ST=K[1];"
    "if(!SB.coinGeoK)SB.coinGeoK={};if(SB.coinGeoK[kind])return SB.coinGeoK[kind];const P=[],N=[],Cl=[],col=h=>{const c=new THREE.Color(h);return [c.r,c.g,c.b];};")
rep("[3.05,.46,'#ffcf45'],[2.85,.3,'#e8aa2a'],[0,.3,'#e8aa2a']];",
    "[3.05,.46,'#ffcf45'],[2.85,.3,'#e8aa2a'],[0,.3,'#e8aa2a']].map(([r,z,c])=>[r*SR,z*ST,c==='#e8aa2a'?K[2]:c]);")
rep("""  const sh=[],slice=new THREE.Shape();slice.moveTo(0,-2.2);slice.lineTo(1.7,1.0);slice.lineTo(-1.7,1.0);slice.closePath();sh.push([slice,.16,'#ffe27a']);
  const crust=new THREE.Shape();crust.moveTo(-2.0,.88);crust.quadraticCurveTo(0,2.3,2.0,.88);crust.lineTo(1.62,1.02);crust.quadraticCurveTo(0,1.8,-1.62,1.02);crust.closePath();sh.push([crust,.27,'#f0a52c']);
  for(const [x,y] of [[0,-.95],[-.62,.28],[.62,.3]]){const c=new THREE.Shape();c.absarc(x,y,.42,0,Math.PI*2,false);sh.push([c,.24,'#c4452a']);}""",
    """  const sh=[],disc=(x,y,r,d,h)=>{const c=new THREE.Shape();c.absarc(x,y,r,0,Math.PI*2,false);sh.push([c,d,h]);};
  if(kind==='gold'){const slice=new THREE.Shape();slice.moveTo(0,-2.2);slice.lineTo(1.7,1.0);slice.lineTo(-1.7,1.0);slice.closePath();sh.push([slice,.16,'#ffe27a']);
    const crust=new THREE.Shape();crust.moveTo(-2.0,.88);crust.quadraticCurveTo(0,2.3,2.0,.88);crust.lineTo(1.62,1.02);crust.quadraticCurveTo(0,1.8,-1.62,1.02);crust.closePath();sh.push([crust,.27,'#f0a52c']);
    for(const [x,y] of [[0,-.95],[-.62,.28],[.62,.3]])disc(x,y,.42,.24,'#c4452a');}
  else if(kind==='pep'){/* pepperoni slices, a darker red, and cheese flecks */for(const [x,y] of [[-2.0,1.7],[2.2,1.2],[0,-2.3],[-2.4,-1.5],[2.4,-1.8],[.3,3.0],[-.2,.4]])disc(x,y,.95,.22,'#7e160c');
    for(const [x,y] of [[-.9,-.9],[1.1,-.3],[-1.2,2.6],[1.5,2.6],[1.0,-3.0],[-3.0,.4]])disc(x,y,.32,.14,'#f2d6a8');}""")
rep("for(const side of [1,-1])for(let i=0;i<p.length;i+=9){const v=[0,3,6].map(o=>[p[i+o],p[i+o+1],side*(p[i+o+2]+.28)])",
    "for(const side of [1,-1])for(let i=0;i<p.length;i+=9){const v=[0,3,6].map(o=>[p[i+o],p[i+o+1],side*(p[i+o+2]+.3*ST-.02)])")
rep("G.computeBoundingSphere();return SB.coinGeo=G;}",
    "G.computeBoundingSphere();if(kind==='gold')SB.coinGeo=G;return SB.coinGeoK[kind]=G;}")

# --- the hidden pepperoni coins: the new coin, the glow kept
a = s.index("  const rg=new THREE.CylinderGeometry(6.4,6.4,1.2,28);")
b = s.index("try{const sp=new THREE.Sprite(glowMat('#ffb030'))", a)
old = s[a:b]
assert old.count('for(const c of C)if(c.rare){const G=new THREE.Group();') == 1
s = s[:a] + ("  const pgm=new THREE.MeshStandardMaterial({color:'#ffffff',vertexColors:true,roughness:.3,metalness:.45,emissive:'#5a1206',emissiveIntensity:.35,transparent:true}),pgg=sbCoinGeo('pep');/* (drawn after its glow, in the see-through pass: the glow, a picture through the coin's middle, would cover the far half of its face) *//* (patch 63: the detailed pepperoni coin) */\n"
             "  for(const c of C)if(c.rare){const G=new THREE.Group();{const cm=new THREE.Mesh(pgg,pgm);cm.renderOrder=2;G.add(cm);}") + s[b:]

# --- the mission medallion
rep("const t=T2(sbActIcon(a.kind));t.userData.keepCanvas=true;const sp=new THREE.Sprite(new THREE.SpriteMaterial({map:t,toneMapped:false,depthWrite:false}));sp.scale.setScalar(14);sp.position.y=17;G.add(sp);",
    "const t=T2(sbActIcon(a.kind));t.userData.keepCanvas=true;/* (patch 63) a gold medallion with the icon on both faces, turning over its ring, with a shadow */"
    "const M=new THREE.Group();M.position.y=17;M.add(new THREE.Mesh(sbCoinGeo('act'),new THREE.MeshStandardMaterial({color:'#ffffff',vertexColors:true,roughness:.3,metalness:.85,emissive:'#8a5800',emissiveIntensity:.4})));"
    "const im=new THREE.MeshStandardMaterial({map:t,alphaTest:.5,roughness:.45,metalness:.05,emissive:'#ffffff',emissiveMap:t,emissiveIntensity:.3}),ig=new THREE.PlaneGeometry(9.6,9.6);"
    "for(const sd of [1,-1]){const d=new THREE.Mesh(ig,im);d.position.z=sd*(.3*1.25+.03);if(sd<0)d.rotation.y=Math.PI;M.add(d);}G.add(M);"
    "const S=new THREE.Mesh(new THREE.PlaneGeometry(1,1).rotateX(-Math.PI/2),new THREE.MeshBasicMaterial({map:sbShadowTex(),transparent:true,depthWrite:false,polygonOffset:true,polygonOffsetFactor:-2,polygonOffsetUnits:-4}));S.scale.set(15,1,6);S.position.y=.8;S.renderOrder=1;G.add(S);const sp=null;")
rep("SB.grp.add(G);return {a,G,sp,x:p.x,z:p.y,y:e,j};}", "SB.grp.add(G);return {a,G,sp,M,S,x:p.x,z:p.y,y:e,j};}")
rep("  for(const m of SBA.marks)if(m.sp)m.sp.material.rotation=Math.sin(performance.now()/600)*.15;",
    "  {const tt=performance.now()/1000;for(const m of SBA.marks)if(m.M){m.M.rotation.y=tt*1.4;m.M.position.y=17+Math.sin(tt*2)*.8;m.S.rotation.y=tt*1.4;}}/* (patch 63: the medallion turns and bobs) */")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patch 63 applied')
