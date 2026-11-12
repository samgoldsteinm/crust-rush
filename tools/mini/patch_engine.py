#!/usr/bin/env python3
"""One-off engine patches for the Miniature Mayhem Cup: per-track road width and lap count, toy-track hooks."""
import sys
P='D:/crust-rush/source/crust-rush.html'
s=open(P,encoding='utf-8').read()
def rep(a,b,cnt=1):
    global s
    n=s.count(a); assert n==cnt,(n,a[:90]); s=s.replace(a,b)
if '/*MINI-BEGIN*/' in s:
    print('already patched'); sys.exit(0)
# road width per track: LS is the track's width against the usual one (1 on every other track)
rep("let LAPS=3;const RW=63,CURB=73,WALLD=CURB+20,KS=1.76,","let LAPS=3,RW=63,CURB=73,WALLD=93,LS=1;const KS=1.76,")
rep("curRev=!!rev;\n  /* the Neon Cup is the hardest","curRev=!!rev;\n  RW=def.rw||63;LS=RW/63;CURB=def.rw?RW+7:73;WALLD=def.rw?RW+11:93;\n  /* the Neon Cup is the hardest")
rep("const d=DIFFS0[k],o=DIFFS[k],h=!!def.neon;","const d=DIFFS0[k],o=DIFFS[k],h=!!def.neon&&!def.toy;")
rep("for(let j=0;j<N;j++){const b=track[j].bend;if(Math.abs(b)>.42){const sd=-Math.sign(b);for(let o=-7;o<=7;o++)track[(j+o+N)%N].wall=sd;}}","if(!def.toy)for(let j=0;j<N;j++){const b=track[j].bend;if(Math.abs(b)>.42){const sd=-Math.sign(b);for(let o=-7;o<=7;o++)track[(j+o+N)%N].wall=sd;}}")
# laps
rep("LAPS=mode==='lss'?Math.max(2,karts.length-1):3","LAPS=mode==='lss'?Math.max(2,karts.length-1):(MAPS[mapIdx].laps||3)")
# rivals' lanes, the start grid, box rows and glide rings in the track's own width
rep("ai.laneTarget=(Math.random()*2-1)*36;}","ai.laneTarget=(Math.random()*2-1)*36*LS;}")
rep("ai.laneTarget=clamp(ai.laneTarget,-28,28);avoid=true;}}","ai.laneTarget=clamp(ai.laneTarget,-28*LS,28*LS);avoid=true;}}")
rep("ai.lane+=(sc.s*48-ai.lane)*Math.min(1,dt*2);}","ai.lane+=(sc.s*48*LS-ai.lane)*Math.min(1,dt*2);}")
rep("for(let c=-52;c<=52;c+=4){let cost=","for(let c=-52*LS;c<=52*LS;c+=4*LS){let cost=")
rep("TD.lane+=(sc.s*58-TD.lane)*Math.min(1,STEP*3.5);","TD.lane+=(sc.s*58*LS-TD.lane)*Math.min(1,STEP*3.5);")
rep("lat=[-30,-10,10,30][slot%4];","lat=[-30,-10,10,30][slot%4]*LS;")
rep("[-26,0,26].forEach((o,i)=>{const x=p.x+p.nx*o,y=p.y+p.ny*o,dbl=i===(gi%2?0:2);","[-26*LS,0,26*LS].forEach((o,i)=>{const x=p.x+p.nx*o,y=p.y+p.ny*o,dbl=i===(gi%2?0:2);")
rep("[-24,0,24].forEach((o,i)=>{const x=G.p.x+G.ux*G.L*f+nx*o,","[-24*LS,0,24*LS].forEach((o,i)=>{const x=G.p.x+G.ux*G.L*f+nx*o,")
rep("const lat=[0,-12,12][i%3],x=G.p.x+G.ux*G.L*f+nx*lat,","const lat=[0,-12,12][i%3]*LS,x=G.p.x+G.ux*G.L*f+nx*lat,")
# toy tracks: their own road, rails and scenery
rep("function buildRoad(def,SJ0,SJ1){if(def.arena){","function buildRoad(def,SJ0,SJ1){if(def.toy){toyRoad(def,SJ0,SJ1);ROAD_SEGS=[{a:SJ0,b:SJ1,id:'asphalt'}];return ROAD_SEGS;}if(def.arena){")
rep("if(def.neon)buildNeon(def);else if(def.arena)buildArena(def);else{","if(def.toy)buildToy(def);else if(def.neon)buildNeon(def);else if(def.arena)buildArena(def);else{")
rep("buildBarrier();if(MULTI)buildDecks(def);if(def.neon)try{neonScenery(def);neonGates(def);}catch(e){console.warn('neon scenery',e);}","if(!def.toy)buildBarrier();if(MULTI)buildDecks(def);if(def.toy)try{toyScenery(def);}catch(e){console.warn('toy scenery',e);}else if(def.neon)try{neonScenery(def);neonGates(def);}catch(e){console.warn('neon scenery',e);}")
i=s.index('/*NEON-BEGIN*/')
s=s[:i]+'/*MINI-BEGIN*//*MINI-END*/\n'+s[i:]
i=s.index('/*NEON-MAPS-END*/')+len('/*NEON-MAPS-END*/')
s=s[:i]+'/*MINI-MAPS-BEGIN*//*MINI-MAPS-END*/'+s[i:]
open(P,'w',encoding='utf-8').write(s)
print('patched')
