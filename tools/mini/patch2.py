# second engine patch for the toy tracks: the loop, the start gate, boosters, ramps, shortcut drawing
p='/home/claude/crust-rush.html'; s=open(p).read()
def rep(a,b,n=1):
    global s
    assert s.count(a)==n,(a[:60],s.count(a)); s=s.replace(a,b)
rep("HR=def.R;HMIN=def.theme==='bay'?-8:-30;if(def.arena){LOOP=null;LOOPS=[];for(const p of track){p.flo=p.fhi=undefined;}if(def.neon)neonGlide(def);return;}",
    "HR=def.R;HMIN=def.theme==='bay'?-8:-30;LOOP_DH=14;if(def.arena){LOOP=null;LOOPS=[];for(const p of track){p.flo=p.fhi=undefined;}if(def.neon)neonGlide(def);if(def.toy)toyLoops(def);return;}")
rep("function shiftForLoop(L){const ss=t=>t<=0?0:t>=1?1:t*t*(3-2*t),W0=95,base=[];","function shiftForLoop(L){const ss=t=>t<=0?0:t>=1?1:t*t*(3-2*t),K=L.sc||1,W0=Math.round(95*K),TR=75*K,HOLD=18*K,base=[];")
rep("const off=o<0?-L.S*ss((o+W0)/75):L.S*(1-ss((o-18)/75)),p=track[j];","const off=o<0?-L.S*ss((o+W0)/TR):L.S*(1-ss((o-HOLD)/TR)),p=track[j];")
rep("for(const LOOP of LOOPS){const p=LOOP.p,g0=LOOP.g0,SEG=128,W=LOOP.W||15,pos=[],uv=[],idx=[],eL=[],eR=[];","for(const LOOP of LOOPS){if(def.toy){toyLoop(LOOP,def);continue;}const p=LOOP.p,g0=LOOP.g0,SEG=128,W=LOOP.W||15,pos=[],uv=[],idx=[],eL=[],eR=[];")
rep("(function(){const s=track[0],ang=s.ang,bm=new THREE.MeshStandardMaterial({map:T2(TX.crust,1,6),roughness:.65});const g=new THREE.Group();world.add(g);",
    "(def.toy?function(){toyGate(def);}:function(){const s=track[0],ang=s.ang,bm=new THREE.MeshStandardMaterial({map:T2(TX.crust,1,6),roughness:.65});const g=new THREE.Group();world.add(g);")
rep("if(def.neon){neonPads(def,mats);return;}","if(def.toy){toyPads(def);return;}if(def.neon){neonPads(def,mats);return;}")
rep("if(def.neon)neonRamps(def);else (function(){","if(def.toy)toyRamps(def);else if(def.neon)neonRamps(def);else (function(){")
rep("function buildShortcut(sc,def){if(def.neon)return neonShortcut(sc,def);","function buildShortcut(sc,def){if(def.toy)return toyShortcut(sc,def);if(def.neon)return neonShortcut(sc,def);")
rep("def.boxes.concat(LOOPS.filter(L=>L.full).map(L=>((L.j-66+N)%N)/N)).forEach(boxRow);","def.boxes.concat(LOOPS.filter(L=>L.full&&!def.neon).map(L=>((L.j-66+N)%N)/N)).forEach(boxRow);")
open(p,'w').write(s); print('patched')
