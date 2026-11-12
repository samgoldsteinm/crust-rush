# fourth engine patch (v155): in a toy room the sun reaches the room only through the window.
# The sun's shadow camera is fixed on the window opening instead of following the player, and everything outside that
# beam counts as shade. Run once: py.cmd tools\mini\patch4.py
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (a[:70], s.count(a)); s = s.replace(a, b)

# 1. the shadow shader: a shadow radius of 50 or more marks a light whose beam is the whole of its shadow map
rep(r"""a='\t\t}\n\t\treturn shadow;\n\t}\n\tvec2 cubeToUV';if(C[k].indexOf(a)>=0)C[k]=C[k].replace(a,'\t\t}\n\t\tshadow=mix(1.0,shadow,smoothstep(""",
    r"""a='\t\t}\n\t\treturn shadow;\n\t}\n\tvec2 cubeToUV',h='float shadowRadius, vec4 shadowCoord ) {\n\t\tfloat shadow = 1.0;';
  /* a shadow radius of 50 or more marks a light whose beam is the whole of its shadow map (the sun through a toy room's window):
     outside the map is shade, not light. Everywhere else beamLit is 1 and the shader does what it always did. */
  if(C[k].indexOf(a)>=0&&C[k].indexOf(h)>=0)C[k]=C[k].replace(h,'float shadowRadius, vec4 shadowCoord ) {\n\t\tfloat beamLit = 1.0 - step( 50.0, shadowRadius );\n\t\tshadowRadius -= 50.0 * ( 1.0 - beamLit );\n\t\tfloat shadow = beamLit;').replace(a,'\t\t}\n\t\tshadow=mix(beamLit,shadow,smoothstep(""")

# 2. the two shadow-camera modes, and the list of meshes that receive shadows for this map only
rep("const sunDir=new THREE.Vector3(.6,1,.35).normalize();",
    """const sunDir=new THREE.Vector3(.6,1,.35).normalize();
/* Toy rooms: the sun comes in only through the window. TOYSUN holds a shadow camera fixed on the window opening (it does not follow the
   player); a shadow radius of 51 tells the shader that everything outside that beam is shade (see the shader patch above).
   sunBox() puts the shadow camera into the mode the current map needs: call it after anything that changes the map or the shadow map's size. */
let TOYSUN=null,SUNRCV=[];
function sunBox(){const sc=sun.shadow.camera,b=TOYSUN;
  if(b){Object.assign(sc,{left:b.l,right:b.r,bottom:b.b,top:b.t,near:b.n,far:b.f});sun.position.copy(b.pos);sun.target.position.copy(b.tgt);sun.shadow.radius=51;sun.shadow.normalBias=Math.max(.35,1.6*(b.r-b.l)/sun.shadow.mapSize.x);}
  else{const X=QUAL[qKey].sx||115;Object.assign(sc,{left:-X,right:X,top:X,bottom:-X,near:20,far:1400});sun.shadow.radius=1;sun.shadow.normalBias=.35;}
  sc.updateProjectionMatrix();}
/* fit the sun's beam to the openings it shines through: each is [x0,x1,y0,y1,z0,z1], the box of a hole in a wall; reach is how far
   past the opening the light can travel before it meets the floor */
function sunBeam(holes,reach){const A=new THREE.Vector3(0,1,0).cross(sunDir).normalize(),B=new THREE.Vector3().copy(sunDir).cross(A).normalize(),c=new THREE.Vector3(),v=new THREE.Vector3(),pts=[];
  for(const h of holes)for(const x of [h[0],h[1]])for(const y of [h[2],h[3]])for(const z of [h[4],h[5]]){const q=new THREE.Vector3(x,y,z);pts.push(q);c.add(q);}c.multiplyScalar(1/pts.length);
  let l=1e9,r=-1e9,bt=1e9,t=-1e9;for(const q of pts){v.copy(q).sub(c);const a=v.dot(A),b=v.dot(B);l=Math.min(l,a);r=Math.max(r,a);bt=Math.min(bt,b);t=Math.max(t,b);}
  /* the shader fades the outer 7% of the map into shade, so the opening sits well inside it */
  const px=(r-l)*.14+12,py=(t-bt)*.14+12;TOYSUN={l:l-px,r:r+px,b:bt-py,t:t+py,n:20,f:700+reach,pos:c.clone().addScaledVector(sunDir,700),tgt:c};sunBox();}
/* in a toy room every lit surface has to be tested against the beam, or it would stand in full sun wherever it is. Meshes built
   without shadows receive them for this map only; userData.sunlit marks the things outdoors, which stay in full sun */
function sunShadeAll(){if(!TOYSUN)return;scene.traverse(o=>{if(o.isMesh&&!o.receiveShadow&&!o.userData.sunlit){o.receiveShadow=true;SUNRCV.push(o);}});}
function sunReset(){for(const o of SUNRCV)o.receiveShadow=false;SUNRCV=[];TOYSUN=null;sunBox();}""")

# 3. every map load starts from the ordinary sun (per-track state is reset on every map type)
rep("sun.color.set(th.sun[0]);sun.intensity=th.sun[1];sunDir.set(th.dir[0],th.dir[1],th.dir[2]).normalize();varLook(def);balanceLook(def);",
    "sunReset();sun.color.set(th.sun[0]);sun.intensity=th.sun[1];sunDir.set(th.dir[0],th.dir[1],th.dir[2]).normalize();varLook(def);balanceLook(def);")

# 4. the sun does not follow the camera in a toy room
rep("function snapSun(x,y,z){const sc=sun.shadow.camera,", "function snapSun(x,y,z){if(TOYSUN)return;const sc=sun.shadow.camera,")

# 5. the quality setting and the frame-rate ladder change the shadow map: keep the shadow camera in the right mode
rep("{const X=q.sx||115;Object.assign(sun.shadow.camera,{left:-X,right:X,top:X,bottom:-X});sun.shadow.camera.updateProjectionMatrix();rimL.intensity=q.hqAll?.28:0;}",
    "{sunBox();rimL.intensity=q.hqAll?.28:0;}")
rep("if(sun.shadow.mapSize.x!==sm){sun.shadow.mapSize.set(sm,sm);if(sun.shadow.map){sun.shadow.map.dispose();sun.shadow.map=null;}}\n  LODM=0;",
    "if(sun.shadow.mapSize.x!==sm){sun.shadow.mapSize.set(sm,sm);if(sun.shadow.map){sun.shadow.map.dispose();sun.shadow.map=null;}}sunBox();\n  LODM=0;")

# 6. once the map is built (and again now and then, for things that appear during the race) every mesh is tested against the beam
rep("function warmScene(){try{if(!_warmG){", "function warmScene(){sunShadeAll();try{if(!_warmG){")
rep("  render.n=(render.n||0)+1;render.fdt=render.fdt==null?dt:render.fdt*.9+dt*.1;",
    "  render.n=(render.n||0)+1;render.fdt=render.fdt==null?dt:render.fdt*.9+dt*.1;if(TOYSUN&&render.n%90===0)sunShadeAll();")

open(p, 'w', encoding='utf-8', newline='').write(s); print('patched')
