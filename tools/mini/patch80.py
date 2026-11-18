"""Patch 80 (web v223): the garage's paint shines; more solid paints; gold, silver and bronze look like metal.
The owner: "some of the paint on the cars in the web app still look flat or a little dull try to make them have better reflections, at
least when we are in the garage ... i want them to have a clearer shine reflection so they look more realistic"; "add more solid colors
to the vehicle paint and work on making the gold silver and bronze better" (the gold was a dull brown).
Why it was flat: the garage has its own renderer (gR, another WebGL context), but its environment came from the game renderer's PMREM
(envFrom -> pmrem): a render-target texture of one context is empty in another, so garage cars reflected NOTHING (every paint flat,
gold brown). And what it would have reflected the kitchen track's sky (envFrom(THEMES.kitchen.env)) was warm brown with three blurry spots, all
below 1.0, so the clear coat (roughness .08) had nothing bright and sharp to show. gStudioEnv(): an HDR studio (float equirect -> PMREM),
a dark neutral room with sharp soft-boxes: a long one overhead, a strip each side, a panel front and back, a faint horizon line. Garage
only (the races keep their own skies; nothing changes per frame).
Run once, after patch 79: py.cmd tools/mini/patch80.py"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'patch 80' not in s, 'already patched'


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:90])
    s = s.replace(a, b)


rep("function openGarage(){",
    "/* (patch 80) the garage's reflections: an HDR photo studio, dark neutral walls and sharp bright soft-boxes, so paint and metal shine */\n"
    "function gStudioEnv(){const W=1024,H=512,d=new Uint16Array(W*H*4),S=(e0,e1,x)=>{const t=Math.min(1,Math.max(0,(x-e0)/(e1-e0)));return t*t*(3-2*t);},\n"
    "  box=(a,lo,hi,f)=>S(lo-f,lo,a)*(1-S(hi,hi+f,a));\n"
    "  for(let y=0;y<H;y++){const el=((y+.5)/H-.5)*Math.PI,dy=Math.sin(el),ce=Math.cos(el);for(let x=0;x<W;x++){const ph=((x+.5)/W-.5)*2*Math.PI,dx=Math.cos(ph)*ce,dz=Math.sin(ph)*ce;\n"
    "    let v=dy>0?.012*(1+.8*dy):.006*(1+dy);/* dark walls, a darker floor */\n"
    "    v+=.2*box(dy,-.012,.022,.01);/* the line where wall meets floor */\n"
    "    if(dy>.2){const a=dx/dy,b=dz/dy;v+=10*box(a,-1,1,.04)*box(b,-.07,.07,.03);}/* overhead: one long narrow soft-box */\n"
    "    v+=5*(box(dz,.9,1.01,.02)+box(-dz,.9,1.01,.02))*box(dx,-.045,.045,.02)*box(dy,.06,.62,.03);/* a tall strip each side */\n"
    "    v+=3*box(dx,.9,1.01,.02)*box(dz,-.3,.3,.03)*box(dy,.12,.42,.03)+2*box(-dx,.9,1.01,.02)*box(dz,-.3,.3,.03)*box(dy,.12,.42,.03);/* front and back panels */\n"
    "    const i=(y*W+x)*4,h=THREE.DataUtils.toHalfFloat;d[i]=h(v*.97);d[i+1]=h(v);d[i+2]=h(v*1.03);d[i+3]=h(1);}}\n"
    "  const t=new THREE.DataTexture(d,W,H,THREE.RGBAFormat,THREE.HalfFloatType);/* (half float: filterable everywhere) */t.mapping=THREE.EquirectangularReflectionMapping;t.magFilter=t.minFilter=THREE.LinearFilter;t.needsUpdate=true;\n"
    "  const pg=new THREE.PMREMGenerator(gR),rt=pg.fromEquirectangular(t);pg.dispose();t.dispose();return rt.texture;}/* (made with the garage's own renderer: a texture made by the game's renderer is empty in another WebGL context) */\n"
    "function openGarage(){")
rep("gS.add(new THREE.HemisphereLight('#fff1d6','#6b3a1e',.75));const dl=new THREE.DirectionalLight('#fff0d8',2.4);",
    "gS.add(new THREE.HemisphereLight('#fff1d6','#6b3a1e',.35));const dl=new THREE.DirectionalLight('#fff0d8',2.2);/* (patch 80: the studio's light now comes from its soft-boxes too) */")
rep("new THREE.MeshStandardMaterial({map:gFloorTex(),roughness:.62,metalness:0,envMapIntensity:.6})",
    "new THREE.MeshStandardMaterial({map:gFloorTex(),roughness:.62,metalness:0,envMapIntensity:.25})")
# the car models' body paint: tagged, and in the garage tuned for real reflections (the race keeps its own values)
rep("const mats={paint:M.carPaint,", "M.carPaint.userData.cp=1;/* (patch 80) */const mats={paint:M.carPaint,")
rep("gModel.g.traverse(o=>{if(o.isMesh){o.castShadow=true;}});gS.add(gModel.g);",
    "gModel.g.traverse(o=>{if(o.isMesh){o.castShadow=true;for(const m of [].concat(o.material))if(m&&m.userData&&m.userData.cp){/* (patch 80) the garage's paint: the base less mirror-like (its colour stays rich), a crisp clear coat */\n"
    "    m.envMapIntensity=m.metalness>0?.75:.8;if(!(m.metalness>0))m.roughness=.45;m.clearcoatRoughness=.04;}}});gS.add(gModel.g);")
# gold, silver and bronze: brighter metal colours (with reflections in the garage they read as metal)
rep("{n:'Bronze',h:'#8a6232',$:250,m:1},{n:'Gold',h:'#d4a838',$:400,m:1}", "{n:'Bronze',h:'#b5763f',$:250,m:1,r:.26},{n:'Gold',h:'#e3b448',$:400,m:1,r:.18}")
rep("{n:'Silver',h:'#b8bcc4',$:0,m:1}", "{n:'Silver',h:'#c9ccd2',$:0,m:1,r:.16}")
# more solid paints (added at the end: a saved build's number keeps its colour; the PC gets them from the export)
rep("const PAINTS=[null,'#c40c0c','#ff5a00','#ffb400','#3fae0c','#0b49c9','#5317ad','#ff2c84','#1c1d22','#efe4cb'];",
    "const PAINTS=[null,'#c40c0c','#ff5a00','#ffb400','#3fae0c','#0b49c9','#5317ad','#ff2c84','#1c1d22','#efe4cb',\n"
    "  '#7a0912','#ffd21a','#86c916','#0b4a26','#0e8c86','#2f9bff','#0c1d4d','#2a1150','#b4532a','#c9b28a','#a9adb5','#3a3d43','#f5f6f8','#07080a'];/* (patch 80: 14 more solids) */")
rep("const PAINT_NAMES=['Driver color','Tomato','Orange','Cheddar','Basil','Ocean','Grape','Bubblegum','Charcoal','Cream'];",
    "const PAINT_NAMES=['Driver color','Tomato','Orange','Cheddar','Basil','Ocean','Grape','Bubblegum','Charcoal','Cream',\n"
    "  'Crimson','Sunburst','Lime','Racing green','Teal','Sky','Navy','Midnight','Copper','Sand','Silver grey','Gunmetal','Snow','Jet black'];")
rep("gS.environment=envFrom(THEMES.kitchen.env,[[128,40,40,'#ffffff'],[384,40,40,'#ffffff'],[256,140,40,'#ff8a2a']]);",
    "gS.environment=gStudioEnv();/* (patch 80: was the kitchen's sky) */")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patch 80 applied')
