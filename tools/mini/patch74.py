"""Patch 74 (web v222): a delivery's arrow.
The owner: "when doing a pizza delivery mission there should be an arrow at the top of the screen or somewhere that points you in the
direction you need to go".
A 3D orange arrow above the kart turned to where to drive, and under the delivery bar what it points at: in the delivery's place, its start line (SB.flag); elsewhere the tunnel or gate to the next place on the shortest way there
(sbNextHop: a breadth-first walk over the places' links, SB_LINKS and a toy place's own gates, both ways), and how far.
Run once: py.cmd tools/mini/patch74.py"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'patch 74' not in s, 'already patched'


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:90])
    s = s.replace(a, b)


rep("function sbActPlace(id){",
    "/* (patch 74) a delivery's way: the next place on the shortest way (over the places' links, both ways), and the point to drive to here */\n"
    "function sbNbrs(id){const r=SB_REG[id];return [...(SB_LINKS[id]||[]),...((r&&r.gates)||[]).map(d=>d.to)];}\n"
    "const _sbHop={};function sbNextHop(from,to){const key=from+'>'+to;if(key in _sbHop)return _sbHop[key];const ids=new Set([...Object.keys(SB_LINKS),...Object.keys(SB_REG)]),adj={};\n"
    "  const add=(a,b)=>{if(!sbRegOf(a)||!sbRegOf(b))return;(adj[a]=adj[a]||new Set()).add(b);(adj[b]=adj[b]||new Set()).add(a);};for(const a of ids)for(const b of sbNbrs(a))add(a,b);\n"
    "  const prev={[from]:null},q=[from];while(q.length){const c=q.shift();if(c===to)break;for(const n of adj[c]||[])if(!(n in prev)){prev[n]=c;q.push(n);}}\n"
    "  if(!(to in prev))return _sbHop[key]=null;let c=to;while(prev[c]!==from&&prev[c]!==null)c=prev[c];return _sbHop[key]=c;}\n"
    "function sbDelAim(a){if(SB.regId===a.to)return SB.flag?{x:SB.flag.x,z:SB.flag.z,say:'Start line'}:null;const n=sbNextHop(SB.regId,a.to),g=n&&SB.gates.find(q=>q.to===n);return g?{x:g.x,z:g.z,say:'To '+sbActPlace(n)}:null;}\n"
    "function sbDelArrow(a){const k=player,t=k&&sbDelAim(a);if(!t)return '';return '<div style=\"font-size:12px;margin-top:5px\">'+t.say+' · '+Math.round(Math.hypot(t.x-k.x,t.z-k.y)*.25)+' m</div>';}\n"
    "/* (patch 74, the owner: \"make the arrow a 3d orange arrow that changes direction based on where you need to go and the direction the car is facing\")\n"
    "   a 3D orange arrow floating above your kart, turned (in the world) toward where to drive: it swings as the kart turns; it bobs a little */\n"
    "let SBDA=null;function sbDel3D(k,A){const on=!!(A&&A.a.kind==='deliver'&&state==='race'&&k&&!SB.trav),t=on&&sbDelAim(A.a);if(!t){if(SBDA)SBDA.visible=false;return;}\n"
    "  if(!SBDA){const sh=new THREE.Shape();sh.moveTo(9,0);sh.lineTo(1.5,5.6);sh.lineTo(1.5,1.7);sh.lineTo(-5,1.7);sh.lineTo(-5,-1.7);sh.lineTo(1.5,-1.7);sh.lineTo(1.5,-5.6);sh.closePath();\n"
    "    const ge=new THREE.ExtrudeGeometry(sh,{depth:1,bevelEnabled:true,bevelThickness:.3,bevelSize:.3,bevelSegments:2});ge.translate(0,0,-.5);ge.rotateX(-Math.PI/2);\n"
    "    const m=new THREE.Mesh(ge,new THREE.MeshStandardMaterial({color:'#ff7a12',emissive:'#ff5a00',emissiveIntensity:.12,roughness:.35,metalness:.1}));m.castShadow=true;m.receiveShadow=true;/* (lit, shaded and casting a shadow) */SBDA=new THREE.Group();SBDA.add(m);SBDA.userData.m=m;scene.add(SBDA);}\n"
    "  if(!SBDA.parent)scene.add(SBDA);const tt=performance.now()/1000,yaw=Math.atan2(-(t.z-k.y),t.x-k.x);SBDA.visible=true;SBDA.position.set(k.x,(k.wy||0)+19+Math.sin(tt*2.4)*.5,k.y);SBDA.scale.setScalar(.8);\n"
    "  {let d=yaw-SBDA.rotation.y;d=Math.atan2(Math.sin(d),Math.cos(d));SBDA.rotation.y+=d*.2;}SBDA.userData.m.rotation.z=-.75;}\n"
    "function sbActPlace(id){")
rep("+'<div style=\"height:5px;border-radius:3px;background:rgba(255,244,220,.2);margin-top:5px;overflow:hidden\"><div style=\"height:100%;width:'+(a.kind==='deliver'?Math.max(0,100*left/a.T):Math.min(100,100*A.v/a.need)).toFixed(1)+'%;background:'+(left<15?'#e8542f':'#ffd65a')+'\"></div></div>';}",
    "+'<div style=\"height:5px;border-radius:3px;background:rgba(255,244,220,.2);margin-top:5px;overflow:hidden\"><div style=\"height:100%;width:'+(a.kind==='deliver'?Math.max(0,100*left/a.T):Math.min(100,100*A.v/a.need)).toFixed(1)+'%;background:'+(left<15?'#e8542f':'#ffd65a')+'\"></div></div>'+(a.kind==='deliver'?sbDelArrow(a):'')/* (patch 74) */;}")
rep("SBA.barT-=dt;if(SBA.barT<=0){SBA.barT=.2;sbActBar();}", "SBA.barT-=dt;if(SBA.barT<=0){SBA.barT=.2;sbActBar();}")
rep("function sbActTick(k,dt){const A=SBA.act;", "function sbActTick(k,dt){const A=SBA.act;try{sbDel3D(k,A);}catch(e){}/* (patch 74) */")
# the owner: "the character ability box needs to be moved down so it doesnt overlap with the coin counter. also move the rear mirror with it":
# in Sandbox (body.sbx) the Special button and the rear-view button go below the read-out (#sbHud, top 64, four lines)
rep("#stage{--hudTop:clamp(58px,15vh,96px)}", "#stage{--hudTop:clamp(58px,15vh,96px)}\nbody.sbx .abtn{top:172px!important}body.sbx .lookbtn{top:calc(172px + var(--btn)*.95 + 20px)!important}/* (patch 74: below Sandbox's read-out) */")
# the owner: "when doing a mission fast travel should not be allowed": refused while a delivery or challenge runs (a Retry still uses it)
rep("function sbTravel(g){if(SB.trav||SB.warp)return;if(g.start&&SBA.act&&!SBA.retry)sbActEnd('cancel');/* (fast travel cannot finish a delivery) */",
    "function sbTravel(g){if(SB.trav||SB.warp)return;if(g.start&&SBA.act&&!SBA.retry){showBanner('No fast travel during a mission: drive there',2.6,'sm');return;}/* (patch 74: refused, not the mission ended) */")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patch 74 applied')
