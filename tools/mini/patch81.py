"""Patch 81 (web v224): the garage is a studio you can see, and the car reflects it.
The owner: "maybe if we added a studio setup to the garage it would look better as well ... a garage studio that had some objects in
the room. if there was more stuff in the environment the reflections might look better as well. they look really good on top of the car
but the sides are still flat looking and its probably just lacking stuff to reflect".
Why the sides were flat: 80's studio was dark walls with one thin strip each side; a car's sides reflect the walls round it at their own
height, so there was nothing there. Later the owner: "make high quality 3d models and make the garage look very realisitic".
gStudioSet(): a real workshop round the turntable, 1 m = 2.7 units (a car's length), 24 x 21 m, 5.5 m high: the Garage track's
Blender-built scanned models at real size (TM.gbench x2, gchest x2, gshelf x3, gtyres x3, gdoor x2, gfit grack / gelec / gladder; scale
K/(TM.U*100): TM.U is units per CENTIMETRE, the first try was 100x too big), sealed concrete and painted brick on NEW materials over the
track's scanned pictures (tinting the track's own surfTex copies did nothing; the track keeps its materials), a dark band low on the
walls, steel beams, LED panels overhead and an LED strip round the walls at door height (HDR: colour x intensity), windows.
The reflections are made from the room itself, once when the garage opens: PMREMGenerator(gR).fromScene on the room alone from the car's
middle height, so what the car shows is what you see. The scanned models download after the menu is up: until they are all there
(gSetFull) the room is rebuilt each time the garage opens (code-built stand-ins first). Zoom out limited to 1.1 (was 1.5) so the camera
stays inside the room. Garage frame time unchanged (7 ms).
Run once, after patch 80: py.cmd tools/mini/patch81.py"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'patch 81' not in s, 'already patched'


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:90])
    s = s.replace(a, b)


JS = r"""/* (patch 81) the garage studio: a real workshop round the turntable, built from the Garage track's scanned models at real size
   (1 m = 2.7 units, a car's length), and the car's reflections made from it */
let gSetFull=false;
function gStudioSet(){const G=new THREE.Group(),M={},K=2.7,S=K/(TM.U*100)/* (TM.U units per cm) */,X=33,Z=28,H=15;
  const mat=(k,o)=>M[k]||(M[k]=o.emit!=null?new THREE.MeshBasicMaterial({color:new THREE.Color(o.c).multiplyScalar(o.emit)}):new THREE.MeshStandardMaterial({color:o.c,roughness:o.r==null?.8:o.r,metalness:o.m||0,envMapIntensity:o.e==null?.5:o.e}));
  const box=(k,o,x,y,z,w,h,d)=>{const m=new THREE.Mesh(new THREE.BoxGeometry(w,h,d),mat(k,o));m.position.set(x,y,z);G.add(m);return m;};
  /* a surface at real size: UVs in repeats of the scan (about 2 m) */
  const plane=(m,w,h,tile,x,y,z,rx,ry)=>{const g=new THREE.PlaneGeometry(w,h),uv=g.attributes.uv;for(let i=0;i<uv.count;i++)uv.setXY(i,uv.getX(i)*w/tile,uv.getY(i)*h/tile);const me=new THREE.Mesh(g,m);me.position.set(x,y,z);me.rotation.set(rx||0,ry||0,0);G.add(me);return me;};
  const put=(o,x,y,z,ry,sc)=>{if(!o)return null;o.scale.setScalar(S*(sc||1));o.position.set(x,y,z);o.rotation.y=ry||0;G.add(o);return o;};
  const fromScan=(f,col,o)=>{try{const c=f();if(!c||!c.map)return null;return new THREE.MeshStandardMaterial(Object.assign({map:c.map,normalMap:c.normalMap||null,normalScale:c.normalScale?c.normalScale.clone():undefined,color:new THREE.Color(col),roughness:.6,metalness:0,envMapIntensity:.5},o));}catch(e){return null;}};
  /* new materials on the track's scanned pictures (its own materials stay as they are): polished grey concrete, a warm grey brick */
  const conc=fromScan(()=>TM.gconcrete(),'#5a5a5c',{roughness:.34,envMapIntensity:.8}),brick=fromScan(()=>TM.gbrick(),'#8f8a82',{roughness:.9,envMapIntensity:.3});
  plane(conc||mat('floor',{c:'#55565a',r:.6}),2*X,2*Z,2*K,0,-.03,0,-Math.PI/2);/* sealed concrete */
  const wm=brick||mat('wall',{c:'#d9d6cf',r:.9});/* painted brick */
  /* a dark painted band low on every wall, as in a workshop */const band=mat('band',{c:'#2b2e33',r:.55,e:.6});box('band',{},-X+.06,1.6,0,.12,3.2,2*Z);box('band',{},X-.06,1.6,0,.12,3.2,2*Z);box('band',{},0,1.6,-Z+.06,2*X,3.2,.12);box('band',{},0,1.6,Z-.06,2*X,3.2,.12);
  plane(wm,2*Z,H,2*K,-X,H/2,0,0,Math.PI/2);plane(wm,2*Z,H,2*K,X,H/2,0,0,-Math.PI/2);plane(wm,2*X,H,2*K,0,H/2,-Z,0,0);plane(wm,2*X,H,2*K,0,H/2,Z,0,Math.PI);
  box('ceil',{c:'#3a3c41',r:.9},0,H+.25,0,2*X,.5,2*Z);for(const x of [-22,-11,0,11,22])box('beam',{c:'#55585e',r:.5,m:.6},x,H-.4,0,.6,.8,2*Z);/* steel beams */
  /* lighting: long LED panels overhead, an LED strip round the walls at door height, as in a detailing studio */
  for(const z of [-12,-4,4,12])for(const x of [-16,0,16])box('ledC',{c:'#ffffff',emit:10},x,H-.9,z,12,.15,1.1);
  for(const [y,k,o,t] of [[6.2,'led',{c:'#eef3ff',emit:5},.35]]){box(k,o,-X+.08,y,0,.15,t,2*Z-1);box(k,o,X-.08,y,0,.15,t,2*Z-1);box(k,o,0,y,-Z+.08,2*X-1,t,.15);box(k,o,0,y,Z-.08,2*X-1,t,.15);}
  box('skirt',{c:'#26282c',r:.6},0,.35,-Z+.1,2*X,.7,.2);box('skirt',{c:'#26282c',r:.6},0,.35,Z-.1,2*X,.7,.2);box('skirt',{c:'#26282c',r:.6},-X+.1,.35,0,.2,.7,2*Z);box('skirt',{c:'#26282c',r:.6},X-.1,.35,0,.2,.7,2*Z);
  const T=f=>{try{return f();}catch(e){return null;}};
  /* back wall (-X): two workbenches, the tool chests, the tool rack and the electrics */
  put(T(()=>TM.gbench(116)),-X+.85,0,-9,Math.PI/2);put(T(()=>TM.gbench(116)),-X+.85,0,-5.8,Math.PI/2);
  put(T(()=>TM.gchest()),-X+.7,0,-1.6,Math.PI/2);put(T(()=>TM.gchest()),-X+.7,0,.3,Math.PI/2);
  put(T(()=>TM.gfit('grack')),-X,3.6,-7.4,Math.PI/2);put(T(()=>TM.gfit('gelec')),-X,3.2,9,Math.PI/2);
  /* front wall (+X): two roll-up doors */
  put(T(()=>TM.gdoor(318,214)),X,0,-6,-Math.PI/2,1.25);put(T(()=>TM.gdoor(318,214)),X,0,6,-Math.PI/2,1.25);
  /* -Z wall: shelving, tyres, the ladder */
  for(const x of [-16,-11.6,-7.2])put(T(()=>TM.gshelf()),x,0,-Z+.6,0);put(T(()=>TM.gtyres(4)),-5,0,-Z+1.2,0);put(T(()=>TM.gtyres(4)),-2.6,0,-Z+1.4,.6);put(T(()=>TM.gfit('gladder')),8,1.2,-Z,0);
  /* +Z wall: windows onto daylight, a tyre stack in the corner */
  for(const x of [-14,0,14]){box('win',{c:'#d6e6ff',emit:2.6},x,9.5,Z-.12,9,4.2,.1);box('frame',{c:'#2a2c30',r:.5,m:.4},x,9.5,Z-.2,9.6,.35,.2);box('frame',{c:'#2a2c30',r:.5,m:.4},x,9.5,Z-.2,.3,4.6,.2);box('frame',{c:'#2a2c30',r:.5,m:.4},x,7.3,Z-.25,9.6,.25,.4);}
  put(T(()=>TM.gtyres(4)),X-3,0,Z-3,.3);
  G.traverse(o=>{if(o.isMesh){o.castShadow=false;o.receiveShadow=true;}});
  gSetFull=['gbench','gchest','gshelf','gtyres','gdoor','grack','gelec','gladder'].every(n=>{try{return TM.pkReady(n);}catch(e){return false;}});return G;}
function gStudioEnvFrom(set){const sc=new THREE.Scene(),par=set.parent;sc.add(set);set.position.y=-3;set.updateMatrixWorld(true);
  sc.add(new THREE.HemisphereLight('#fff1d6','#2a2a30',.35));const dl=new THREE.DirectionalLight('#fff0d8',2.2);dl.position.set(10,22,12);sc.add(dl);
  const pg=new THREE.PMREMGenerator(gR),rt=pg.fromScene(sc,0,.5,400);pg.dispose();set.position.y=0;if(par)par.add(set);set.updateMatrixWorld(true);return rt.texture;}
/* the room again once the scanned models have arrived (they download after the menu is up) */
let gSet=null;function gStudioMake(){if(gSet){gS.remove(gSet);gSet.traverse(o=>{if(o.isMesh)o.geometry.dispose();});}gSet=gStudioSet();const old=gS.environment;gS.environment=gStudioEnvFrom(gSet);gS.add(gSet);if(old&&old!==gS.environment)old.dispose();}
"""

rep("/* (patch 80) the garage's reflections: an HDR photo studio", JS + "/* (patch 80) the garage's reflections: an HDR photo studio")
rep("gS=new THREE.Scene();gS.environment=gStudioEnv();/* (patch 80: was the kitchen's sky) */",
    "gS=new THREE.Scene();/* (patch 81: the studio room and the car's reflections from it: gStudioMake below; 80's painted studio was gStudioEnv) */")
rep("gC=new THREE.PerspectiveCamera(30,1.6,.1,500);}catch(e){gR=null;}}",
    "gC=new THREE.PerspectiveCamera(30,1.6,.1,500);}catch(e){gR=null;}}\n  if(gR&&(!gSet||!gSetFull))try{gStudioMake();}catch(e){console.warn('studio',e);}/* (patch 81) */")
rep(",.32,1.5)", ",.32,1.1)", 3)   # (the camera stays inside the room)
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patch 81 applied')
