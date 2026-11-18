"""Patch 84 (web v224): Margherita's kitchen: real brick and windows onto a real garden.
The owner: "lets fix the brick and the windows on this map, its just a blue block for the windows and the brick is extremely flat and
cartoonish" (the Margherita Ring kitchen, buildKitchen + kitchenDressing).
- Brick: the walls and the four pizza ovens were a drawn brick picture (brickTex). Now the scanned CC0 red brick (tools/blender/ph_tex.py
  'brick': tex_toy_brick + its relief tex_toy_brick_n) at a believable course height (one scan repeat = 800 units, about 27 courses).
  One pair of textures (scanTex) for every surface; each surface scales its own UVs (uvS), so the phone holds one copy.
- Windows: the panes were a flat light-blue colour. Now the kitchen's garden view rendered in Blender (tex_toy_outsidek, as the toy
  kitchen's window), cropped to the tall panes, a little over full brightness; still named 'sky_window' so night darkens it.
- Until those pictures have downloaded (they come after the menu) the old look stays: nothing waits for them.
Not changed: the floor plane that reaches past the walls. It is one flat surface of two triangles, hidden behind the walls from inside,
so it costs next to nothing to draw; Sandbox reuses the room. PC: the tracks' export carries the web's room to the PC.
Run once, after patch 83: py.cmd tools/mini/patch84.py"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'patch 84' not in s, 'already patched'


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:90])
    s = s.replace(a, b)


rep("/* kitchen dressing: tall windows of daylight", """/* (patch 84) a scanned surface (tools/blender/ph_tex.py) and its relief, one texture pair per key for every surface that uses it;
   null until both pictures are in. uvS scales a geometry's UVs: each surface sets its own repeat without copying the textures */
const SCANT={};function scanTex(key){const a='tex_toy_'+key,b=a+'_n';if(typeof PROP_TEX==='undefined'||!PROP_TEX[a]||!PROP_TEX[b])return null;if(SCANT[key])return SCANT[key];
  const tx=(n,srgb)=>{const im=new Image(),src=texSrc(PROP_TEX[n]);if(/^https?:/.test(src))im.crossOrigin='anonymous';im.src=src;const t=new THREE.Texture(im);im.onload=()=>{t.needsUpdate=true;};if(im.complete)t.needsUpdate=true;
    if(srgb)t.encoding=THREE.sRGBEncoding;t.wrapS=t.wrapT=THREE.RepeatWrapping;t.anisotropy=maxAniso;t.userData.shared=true;return t;};
  return SCANT[key]={map:tx(a,true),normalMap:tx(b,false)};}
function uvS(g,rx,ry){const uv=g.attributes.uv;for(let i=0;i<uv.count;i++)uv.setXY(i,uv.getX(i)*rx,uv.getY(i)*ry);return g;}
/* kitchen dressing: tall windows of daylight""")
# the walls
rep("put(new THREE.CylinderGeometry(R+1700,R+1700,2200,120,1,true),new THREE.MeshStandardMaterial({map:T2(brickTex(),70,9),side:THREE.BackSide,roughness:.9}),0,1040,0,world,false);",
    "{const B=scanTex('brick'),T=800/* (one scan repeat: about 27 courses) */,g=new THREE.CylinderGeometry(R+1700,R+1700,2200,120,1,true);/* (patch 84: the scanned brick) */\n"
    "  put(B?uvS(g,Math.round(2*Math.PI*(R+1700)/T),2200/T):g,B?new THREE.MeshStandardMaterial({map:B.map,normalMap:B.normalMap,normalScale:new THREE.Vector2(1.2,1.2),side:THREE.BackSide,roughness:.88,envMapIntensity:.3}):new THREE.MeshStandardMaterial({map:T2(brickTex(),70,9),side:THREE.BackSide,roughness:.9}),0,1040,0,world,false);}")
# the ovens: one shared scanned material, each part's UVs scaled to its size
rep("const fires=[];", "const fires=[],KB=scanTex('brick'),KBM=KB?new THREE.MeshStandardMaterial({map:KB.map,normalMap:KB.normalMap,normalScale:new THREE.Vector2(1.2,1.2),roughness:.88,envMapIntensity:.3}):null;/* (patch 84) */")
rep("put(new THREE.CylinderGeometry(330,340,110,48),bm,0,55,0,S);put(new THREE.SphereGeometry(320,48,24,0,Math.PI*2,0,Math.PI/2),bm,0,110,0,S);",
    "put(KBM?uvS(new THREE.CylinderGeometry(330,340,110,48),2.6,110/800):new THREE.CylinderGeometry(330,340,110,48),KBM||bm,0,55,0,S);put(KBM?uvS(new THREE.SphereGeometry(320,48,24,0,Math.PI*2,0,Math.PI/2),2.5,1.0):new THREE.SphereGeometry(320,48,24,0,Math.PI*2,0,Math.PI/2),KBM||bm,0,110,0,S);")
rep("put(new THREE.CylinderGeometry(55,60,520,24),bm,0,420,-190,S);", "put(KBM?uvS(new THREE.CylinderGeometry(55,60,520,24),.45,520/800):new THREE.CylinderGeometry(55,60,520,24),KBM||bm,0,420,-190,S);")
# the windows: the garden outside
rep("sky=new THREE.MeshBasicMaterial({name:'sky_window',color:'#bfe3ff',toneMapped:false,fog:false})",
    "sky=typeof PROP_TEX!=='undefined'&&PROP_TEX['tex_toy_outsidek']?new THREE.MeshBasicMaterial({name:'sky_window',map:propTex('tex_toy_outsidek'),color:new THREE.Color(1.15,1.15,1.17),toneMapped:false,fog:false})/* (patch 84: the garden rendered in Blender) */:new THREE.MeshBasicMaterial({name:'sky_window',color:'#bfe3ff',toneMapped:false,fog:false})")
rep("put(new THREE.PlaneGeometry(520,620),sky,0,0,0,w,false);",
    "{const pg=new THREE.PlaneGeometry(520,620);if(sky.map){const uv=pg.attributes.uv;for(let i=0;i<uv.count;i++)uv.setX(i,.5+(uv.getX(i)-.5)*.71);}/* (the picture is wider than the pane: its middle) */put(pg,sky,0,0,0,w,false);}")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patch 84 applied')
