# third engine patch (v153): stale pools on arena maps, smooth deck heights and a slope-aware camera on toy tracks,
# toy tracks back to the first width, quicker steering on toy tracks
p='D:/crust-rush/source/crust-rush.html'; s=open(p).read()
def rep(a,b,n=1):
    global s
    assert s.count(a)==n,(a[:70],s.count(a)); s=s.replace(a,b)
# 1. pools left over from the last track: arena, neon and toy maps never cleared them, so karts sank through the road
rep("if(def.neon)neonGlide(def);if(def.toy)toyLoops(def);return;}","planPonds(def);if(def.neon)neonGlide(def);if(def.toy)toyLoops(def);return;}")
# 2. per-map steering and the toy flag
rep("let LAPS=3,RW=63,CURB=73,WALLD=93,LS=1;const KS=1.76,BASE0=170.5,ACCEL=110,TURN=2.2,STEP=1/120;","let LAPS=3,RW=63,CURB=73,WALLD=93,LS=1,TURN=2.2,TOYT=false;const KS=1.76,BASE0=170.5,ACCEL=110,STEP=1/120;")
rep("CURB=def.rw?RW+4:73;WALLD=def.rw?RW+6:93;","CURB=def.rw?RW+7:73;WALLD=def.rw?RW+11:93;TOYT=!!def.toy;TURN=TOYT?2.86:2.2;/* a toy track's bends are tight: karts turn 30% quicker on it */")
# 3. road height under a kart on a toy track: worked out along the bend, so it no longer steps where the road curves tightly
rep("function kEy(k){if(!MULTI)return 0;let j=k.idx;",
    "function kEy(k){if(!MULTI)return 0;if(TOYT){const j0=k.idx,p=track[j0],sl=T.L/N,u=(k.x-p.x)*p.tx+(k.y-p.y)*p.ty,lat=(k.x-p.x)*p.nx+(k.y-p.y)*p.ny,kap=(p.bend||0)/(20*sl),f=clamp(u/(1-clamp(kap*lat,-.7,.7)),-2*sl,2*sl)/sl,fi=Math.floor(f);return eyAt(((j0+fi)%N+N)%N,f-fi);}let j=k.idx;")
# 4. camera on a toy track: rises over the road behind on a descent and looks down the slope ahead
rep("if(state==='countdown'&&!CL){const f=clamp((cd-.4)/3,0,1);dist+=80*f*f;h+=50*f*f;}",
    "if(state==='countdown'&&!CL){const f=clamp((cd-.4)/3,0,1);dist+=80*f*f;h+=50*f*f;}let cSA=0;if(TOYT&&MULTI&&!camT.loop&&!camT.glide&&!(camT.z>3)){const sp=T.L/N,ix=camT.idx,e0=track[ix].ey||0,eb=track[((ix-Math.round(dist/sp))%N+N)%N].ey||0,ea=track[(ix+Math.round(40/sp))%N].ey||0,bk=keys.look||PAD.look,f=Math.min(1,dt*5);cam.sb=(cam.sb||0)+(Math.max(0,(bk?ea:eb)-e0)-(cam.sb||0))*f;cam.sa=(cam.sa||0)+(((bk?eb:ea)-e0)-(cam.sa||0))*f;h+=cam.sb*1.15+Math.max(0,-cam.sa)*.6;cSA=cam.sa*.75;}")
rep("tv.set(camT.rx+fx*(CL?32:21),cy+(CL?6.2:5.5)+ex*.5,camT.ry+fy*(CL?32:21));","tv.set(camT.rx+fx*(CL?32:21),cy+(CL?6.2:5.5)+ex*.5+cSA,camT.ry+fy*(CL?32:21));")
open(p,'w').write(s); print('patched')
