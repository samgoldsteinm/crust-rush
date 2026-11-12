#!/usr/bin/env python3
"""One-off engine patches for the neon cup (run once on crust-rush.html)."""
import sys
P='D:/crust-rush/source/crust-rush.html'
s=open(P,encoding='utf-8').read()
def rep(a,b,cnt=1):
    global s
    n=s.count(a)
    assert n==cnt,(n,a[:90])
    s=s.replace(a,b)
if '/*NEON-BEGIN*/' in s:
    print('already patched'); sys.exit(0)
# cups and the track table
rep("{name:\"Meat Lover's Cup\",col:'#b06a3c'}];","{name:\"Meat Lover's Cup\",col:'#b06a3c'},{name:'Neon Cup',col:'#3ff0ff'}];")
rep("exact:1,arena:1,special:1,song:'napoli',themeName:'Neon arena',blurb:'A special track inside a glowing arena:","exact:1,arena:1,song:'napoli',themeName:'Neon arena',blurb:'A track inside a glowing arena:")
i=s.index("{id:'grid',name:'Neon Grid Arena'"); e=s.index('\n];\n',i)
s=s[:e]+'\n/*NEON-MAPS-BEGIN*//*NEON-MAPS-END*/'+s[e:]
# glide on a neon track, and oil/traps only vanish over the pit itself
rep("if(def.arena){LOOP=null;LOOPS=[];for(const p of track){p.flo=p.fhi=undefined;}return;}","if(def.arena){LOOP=null;LOOPS=[];for(const p of track){p.flo=p.fhi=undefined;}if(def.neon)neonGlide(def);return;}")
rep("const overPit=(x,y)=>GLIDE&&groundAt(x,y)<glideY(x,y)-20;","const overPit=(x,y)=>GLIDE&&pitAt(x,y)>1&&groundAt(x,y)<glideY(x,y)-20;")
# scenery
rep("if(def.arena)buildArena(def);else{","if(def.neon)buildNeon(def);else if(def.arena)buildArena(def);else{")
rep("if(def.arena){const nm=new THREE.MeshBasicMaterial({color:'#3ff0ff',toneMapped:false});strip(SJ0,SJ1,RW-.6","if(def.arena&&!def.neon){const nm=new THREE.MeshBasicMaterial({color:'#3ff0ff',toneMapped:false});strip(SJ0,SJ1,RW-.6")
rep("cA=new THREE.Color(def.arena?'#3ff0ff':def.theme==='night'?'#3a6fd8':def.theme==='freezer'?'#4aa8e8':'#d6301e'),cB=new THREE.Color('#f4efe4'),cT=new THREE.Color('#c98b4e'),cK=new THREE.Color('#3a2a20');","cA=new THREE.Color(def.arena?(def.acc||'#3ff0ff'):def.theme==='night'?'#3a6fd8':def.theme==='freezer'?'#4aa8e8':'#d6301e'),cB=new THREE.Color(def.neon?'#0c1826':'#f4efe4'),cT=new THREE.Color(def.neon?(def.acc2||'#ff3fd8'):'#c98b4e'),cK=new THREE.Color(def.neon?'#05080e':'#3a2a20');")
# boost pads
rep("(function(){const mats=[0,1,2].map(v=>holoPadMat(v));let pi=0;const mat=mats[0];","(function(){const mats=[0,1,2].map(v=>holoPadMat(v));let pi=0;const mat=mats[0];if(def.neon){neonPads(def,mats);return;}")
# ramps, road blocks, rolling meatballs
rep("(function(){const topM=new THREE.MeshStandardMaterial({map:T2(rampTex()),roughness:.45}),sideM2=","if(def.neon)neonRamps(def);else (function(){const topM=new THREE.MeshStandardMaterial({map:T2(rampTex()),roughness:.45}),sideM2=")
rep("(function(){const make=OBST[def.theme]();const pats=","if(!def.neon)(function(){const make=OBST[def.theme]();const pats=")
rep("(function(){const mm=new THREE.MeshStandardMaterial({map:T2(meatTex()),roughness:.65}),mg=new THREE.SphereGeometry(8,36,24);","if(!def.neon)(function(){const mm=new THREE.MeshStandardMaterial({map:T2(meatTex()),roughness:.65}),mg=new THREE.SphereGeometry(8,36,24);")
# item boxes: on the road's own level, and at the same places both ways round on a neon track
rep("const boxRow=(f,gi)=>{const p=track[Math.floor(f*N)];[-26,0,26].forEach((o,i)=>{const x=p.x+p.nx*o,y=p.y+p.ny*o,dbl=i===(gi%2?0:2);boxes.push({x,y,r:0,sv:gi*4+i,gy:groundAt(x,y),dbl});});};",
    "const boxRow=(f,gi)=>{const p=track[def.neon?nfj(f):Math.floor(f*N)];[-26,0,26].forEach((o,i)=>{const x=p.x+p.nx*o,y=p.y+p.ny*o,dbl=i===(gi%2?0:2);boxes.push({x,y,r:0,sv:gi*4+i,gy:groundAt(x,y)+(p.ey||0),dbl});});};")
# shortcuts and decks
rep("if(def.arena||MULTI)SHORTS=[];else findShortcuts(def);","if(def.neon)neonShortcuts(def);else if(def.arena||MULTI)SHORTS=[];else findShortcuts(def);")
rep("function buildShortcut(sc,def){const SW=sc.w||SCW;","function buildShortcut(sc,def){if(def.neon)return neonShortcut(sc,def);const SW=sc.w||SCW;")
rep("function buildDecks(def){if(!MULTI)return;","function buildDecks(def){if(!MULTI)return;if(def.neon)return neonDecks(def);")
rep("function makePath(c,w){const W=w||SCW;","function makePath(c,w,free){const W=w||SCW;")
rep("if(c.k*T.L/N-L<110||c.k*T.L/N-L>620)return null;","if(!free&&(c.k*T.L/N-L<110||c.k*T.L/N-L>620))return null;")
# ramps follow the road's own level
rep("const gp=(x,hh,z)=>[x,hh+edgeGround(x,z),z]","const gp=(x,hh,z)=>[x,hh+edgeGround(x,z)+(p.ey||0),z]")
# the glide's launch ramp, rings and sign; the canyon faces and the sauce pool are for the other themes
rep("function buildGlide(def){const G=GLIDE,gt=T2(glideTex());","function buildGlide(def){const G=GLIDE,gt=T2(glideTex()),NE=!!def.neon;")
rep("face(G.p,1);face(track[G.j1],-1);","if(!NE){face(G.p,1);face(track[G.j1],-1);}")
rep("pool.userData.noLift=true;world.add(pool);","pool.userData.noLift=true;if(!NE)world.add(pool);")
rep("const sgp=track[(G.rj-3+N)%N],gy=groundAt(sgp.x,sgp.y),postM=","const sgp=track[(G.rj-3+N)%N],gy=groundAt(sgp.x,sgp.y)+(sgp.ey||0),postM=")
rep("{const b0=groundAt(x,z)-1,ph=Math.max(8,gy+50-b0);","{const b0=NE?gy-1:groundAt(x,z)-1,ph=Math.max(8,gy+50-b0);")
# the neon code block
i=s.index('/* ================= LANDSCAPE: cliffs, terraces, valleys and lakes around the track')
s=s[:i]+'/*NEON-BEGIN*//*NEON-END*/\n'+s[i:]
open(P,'w',encoding='utf-8').write(s)
print('patched')
