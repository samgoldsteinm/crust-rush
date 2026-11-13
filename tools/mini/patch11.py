# eleventh engine patch (v166): items, from the user's play-test of Bedroom Blitz.
# 1. Item boxes on toy tracks: a row's three boxes stand right across the track (21 units apart; they were 12.7 apart, inside one
#    kart's reach) and step along it (the outer two 2 track points before and after the middle one); a kart that takes a box cannot
#    take another for BOXCD seconds (0.6 on toy tracks, 0 elsewhere), so one kart no longer clears a row; boxes come back after
#    BOXR seconds (2 on toy tracks, 4 elsewhere).
# 2. A homing anchovy (the item and Anchovy's special) that reaches a kart still inside its protection after a spin is used up
#    with no effect, like any other item. It used to circle the kart and strike the moment the protection ended: a second hit.
# 3. Olive's slick trail is SLICKN slicks long: 7 on toy tracks (the tracks are small), 10 elsewhere.
# 4. Olive's slicks never catch the kart that laid them, and that player sees their own in blue with no warning sign.
# Race rules and track data: NET_PROTO 104; the PC reads BOXR, BOXCD and SLICKN from the exported track.
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (a[:70], s.count(a)); s = s.replace(a, b)
rep("TOYT=false,DRIN=1.75,DROUT=1;", "TOYT=false,DRIN=1.75,DROUT=1,BOXR=4,BOXCD=0,SLICKN=10;")
rep("DRIN=TOYT?2.6:1.75;DROUT=TOYT?.6:1;", "DRIN=TOYT?2.6:1.75;DROUT=TOYT?.6:1;BOXR=TOYT?2:4;BOXCD=TOYT?.6:0;SLICKN=TOYT?7:10;/* toy tracks are short and narrow: item boxes come back sooner and a kart takes one box of a row, Olive's trail is shorter */")
# 1. box rows
rep("const boxRow=(f,gi)=>{const p=track[boxClear(def.neon?nfj(f):Math.floor(f*N))];[-26*LS,0,26*LS].forEach((o,i)=>{const x=p.x+p.nx*o,y=p.y+p.ny*o,dbl=i===(gi%2?0:2);",
    "const boxRow=(f,gi)=>{const j0=boxClear(def.neon?nfj(f):Math.floor(f*N)),bo=def.toy?RW-10:26*LS;/* a toy track's boxes stand right across it and step along it, out of one kart's reach of each other */[-bo,0,bo].forEach((o,i)=>{const p=track[((j0+(def.toy?(i-1)*2:0))%N+N)%N],x=p.x+p.nx*o,y=p.y+p.ny*o,dbl=i===(gi%2?0:2);")
rep("for(const b of boxes){if(b.r>0){b.r-=dt;continue;}for(const k of karts){if(b.air?",
    "for(const b of boxes){if(b.r>0){b.r-=dt;continue;}for(const k of karts){if(BOXCD&&k.boxT>simTime)continue;/* just took a box: the rest of the row is for the others */if(b.air?")
rep("<18))){b.r=4;burst(", "<18))){b.r=BOXR;k.boxT=simTime+BOXCD;burst(")
rep("for(const b of boxes){if(b.r>0||b.pr>simTime)continue;if(b.air?", "for(const b of boxes){if(b.r>0||b.pr>simTime||(BOXCD&&k.boxT>simTime))continue;if(b.air?")
rep("<18))){b.pr=simTime+1.5;boxFx(b,k);}}", "<18))){b.pr=simTime+1.5;k.boxT=simTime+BOXCD;boxFx(b,k);}}")
# 2. anchovies and protection
rep("if(tg.inv>0||tg.rush>0||abInv(tg)||tg.ghostT>0||tg.absT>0)return false;",
    "if(tg.inv>0){p.pop=1;return true;}/* still protected after a spin: the anchovy is used up on the protection, like any other item (it used to wait and strike the moment the protection ended) */if(tg.rush>0||abInv(tg)||tg.ghostT>0||tg.absT>0)return false;")
rep("if(heldBlock(k,p))return true;if((k.x-p.x)**2+(k.y-p.y)**2<R*R&&k.inv<=0&&sameLvl(k,p)){if(k===player)hitBy(p);p.pop=1;spinOut(k,p.type==='meat2'?'meat':'pep');",
    "if(heldBlock(k,p))return true;if(p.type==='torp'&&k===p.target&&k.inv>0&&(k.x-p.x)**2+(k.y-p.y)**2<R*R&&sameLvl(k,p)){p.pop=1;return true;}/* a homing anchovy that reaches its protected target is used up, it does not circle and wait */if((k.x-p.x)**2+(k.y-p.y)**2<R*R&&k.inv<=0&&sameLvl(k,p)){if(k===player)hitBy(p);p.pop=1;spinOut(k,p.type==='meat2'?'meat':'pep');")
# 3. the trail's length
rep("k.abQ=[0,1,2,3,4,5,6,7,8,9].map(n=>[n*.25,()=>{", "k.abQ=[0,1,2,3,4,5,6,7,8,9].slice(0,SLICKN).map(n=>[n*.25,()=>{")
rep("olive:1,mesh:itemMesh('oil')});}]);k.oliveT=OLIVE_T;k.abFx=OLIVE_T;", "olive:1,mesh:itemMesh('oil')});}]);k.oliveT=k.abFx=OLIVE_T-(10-SLICKN)*.25;/* untouchable for as long as the trail takes to lay */")
# 4. own slicks
rep("for(const k of karts){if(k.loop||(k===h.owner&&!h.armed)||(k.netId&&!k.finished))continue;", "for(const k of karts){if(k.loop||(k===h.owner&&(h.olive||!h.armed))||(k.netId&&!k.finished))continue;/* Olive's slicks never catch the kart that laid them */")
rep("if(!m.hk||(m.ho===me&&!m.armed))continue;", "if(!m.hk||(m.ho===me&&(!m.armed||m.hk==='olive')))continue;")
rep("function hazDecorate(mesh,kind){if(!mesh||mesh.userData.hzd||!HZ_DEC[kind])return;mesh.userData.hzd=1;",
    "function hazDecorate(mesh,kind,mine){if(!mesh||mesh.userData.hzd||!HZ_DEC[kind])return;mesh.userData.hzd=1;")
rep("HZMK={rg,rk,ring:mm('#ffe02a',.95),edge:mm('#1a0d06',.55),warn:wm2};}", "HZMK={rg,rk,ring:mm('#ffe02a',.95),mine:mm('#35c8ff',.95),edge:mm('#1a0d06',.55),warn:wm2,tint:new Map()};}\n  /* your own slick (it cannot catch you): blue instead of yellow, and no warning sign */\n  if(mine)mesh.traverse(o=>{if(!o.isMesh||!o.material||!o.material.color)return;let t=HZMK.tint.get(o.material);if(!t){t=o.material.clone();t.color.lerp(new THREE.Color('#2a9cff'),.72);t.userData.shared=true;SHSET.add(t);HZMK.tint.set(o.material,t);}o.material=t;});")
rep("const e=new THREE.Mesh(HZMK.rk,HZMK.edge),r=new THREE.Mesh(HZMK.rg,HZMK.ring);", "const e=new THREE.Mesh(HZMK.rk,HZMK.edge),r=new THREE.Mesh(HZMK.rg,mine?HZMK.mine:HZMK.ring);")
rep("const g=new THREE.Sprite(glowMat(kind==='forks'?'#d8ecff':kind==='boxes'?'#ffb040':'#ffd23a'));", "const g=new THREE.Sprite(glowMat(mine?'#35c8ff':kind==='forks'?'#d8ecff':kind==='boxes'?'#ffb040':'#ffd23a'));")
rep("const w=new THREE.Sprite(HZMK.warn);w.scale.setScalar(7.5);", "const w=new THREE.Sprite(HZMK.warn);w.visible=!mine;w.scale.setScalar(7.5);")
rep("if(!h.mesh.userData.hzd)hazDecorate(h.mesh,h.olive?'olive':h.kind||'oil');", "if(!h.mesh.userData.hzd)hazDecorate(h.mesh,h.olive?'olive':h.kind||'oil',!!h.olive&&h.owner===player);")
rep("if(HZMK){HZMK.ring.opacity=.62+.33*Math.sin(time*7);", "if(HZMK){HZMK.ring.opacity=HZMK.mine.opacity=.62+.33*Math.sin(time*7);")
rep("if(!m.mesh.userData.hzd)hazDecorate(m.mesh,m.hk);", "if(!m.mesh.userData.hzd)hazDecorate(m.mesh,m.hk,m.hk==='olive'&&m.ho===karts.indexOf(player));")
rep("NET_PROTO=103", "NET_PROTO=104")
open(p, 'w', encoding='utf-8', newline='').write(s); print('patched')
