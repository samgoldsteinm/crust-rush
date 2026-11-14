"""Patch 26 (web v192, online version 110; the PC's kart.gd and race.gd carry the same three changes): racing fixes from the owner's play-test.
1. A JUMP RAMP ONLY ON ITS OWN LEVEL. On Kitchen Chaos "something invisible on the track ... was stopping me from going forward": the jump ramp
   on the bridge stopped karts on the climb that passes under the bridge. The ramp rule in stepKart went by place only. Now a ramp whose own
   height is more than its rise + 26 from the kart's is not there for that kart.
2. THE FINISH IS THE LINE. "every race is ending slightly before the actual finish line": a kart was finished when its count of lap points
   (prog) reached laps x N. Measured (tools/neon/finishtest.py): that count runs 4 to 22 points ahead of the kart after loops, shortcuts and
   glides (35 units early on the toy tracks, up to 180 on Laser Slice Skyway), and with no drift it still tripped half a point before the line.
   Now: finAt(k). On the last lap a kart finishes once it has come round past lap point 0 and is at or beyond the line itself. And each
   time a kart crosses the line its count is set right (a whole number of laps plus where it is), so the lap counter keeps true as well.
3. TOY SHORTCUT LANES ARE STRAIGHT. "make the shortcuts like this not have any curve and just be straight. when they curve to the right
   slightly back into the track it forces the player to run into the wall": on toy tracks makePath lays the lane as one straight line
   from its mouth to its end (the other tracks keep their curved side roads).
   (by hand with it: the clearance a lane must keep from the track is WALLD+W-2 for a straight lane, WALLD+W+5 as before for a curved one;
   and the bedroom's lane was moved, tools/mini/t_bedroom.py, so that it leaves and rejoins at about 45 degrees: it left at 72.)
4. (looks only, by hand) THE CHASE CAMERA IN A LONG DROP, Sandbox and Balloon Battle: `cy=...BATTLE?camT.rz-Math.min(8,(camT.rz-camT.rg)*.55):...`.
   The owner: "the camera is also really bad at following the car when you jump from a high piece of the track to the ground".
   and the camera's look along the track's slope is skipped in Sandbox for a kart heading across the track (it looked up the climb while the kart drove off the side).
   and that look follows the way the kart is going: driving a climb the wrong way round in Sandbox, the camera looked up the hill behind it.
Run once: py.cmd tools/mini/patch26.py"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'finAt(k)' not in s, 'already patched'


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:70])
    s = s.replace(a, b)


rep("  for(const r of ramps){let al=-1,lat=0,acc=0,fx=0,fy=0;",
    "  for(const r of ramps){if(MULTI){/* a ramp on another level of the track (on a bridge overhead, say) is not there for this kart */const pr=track[r.j];if(Math.abs(k.wy-(groundAt(pr.x,pr.y)+(pr.ey||0)))>r.h+26)continue;}let al=-1,lat=0,acc=0,fx=0,fy=0;")
rep("let di=best-k.idx;if(di>N/2)di-=N;if(di<-N/2)di+=N;k.prog+=di;k.idx=best;",
    "let di=best-k.idx;if(di>N/2)di-=N;if(di<-N/2)di+=N;k.prog+=di;k.idx=best;\n"
    "  if(!BATTLE){/* crossing the line sets the count of lap points right: loops, shortcuts and glides each leave it a few points out */if(oIdx>N*.75&&best<N*.25)k.prog=Math.round(k.prog/N)*N+best;else if(oIdx<N*.25&&best>N*.75)k.prog=Math.round(k.prog/N)*N+best-N;}")
rep("&&!k.finished&&!BATTLE&&k.prog>=LAPS*N){", "&&!k.finished&&!BATTLE&&finAt(k)){")
rep("function lateral(k){", "/* has this kart finished? On the last lap, once it has come round past lap point 0 and is at or beyond the line itself */\n"
    "function finAt(k){if(k.prog<LAPS*N-(N>>2))return false;if(k.idx>(N>>2))return k.prog>=LAPS*N+(N>>2);const p=track[0];return (k.x-p.x)*p.tx+(k.y-p.y)*p.ty>=0;}\n"
    "function lateral(k){")
rep("  const c1=[S[0]+(pa.tx*.55+pa.nx*s*.85)*h,S[1]+(pa.ty*.55+pa.ny*s*.85)*h],c2=[E[0]+(-pb.tx*.55+pb.nx*s*.85)*h,E[1]+(-pb.ty*.55+pb.ny*s*.85)*h];",
    "  const str8=typeof TOYT!=='undefined'&&!!TOYT;/* a toy track's lane is one straight piece from mouth to end: no bend back into the track at the far end */\n"
    "  const c1=str8?[S[0]+(E[0]-S[0])/3,S[1]+(E[1]-S[1])/3]:[S[0]+(pa.tx*.55+pa.nx*s*.85)*h,S[1]+(pa.ty*.55+pa.ny*s*.85)*h],c2=str8?[S[0]+(E[0]-S[0])*2/3,S[1]+(E[1]-S[1])*2/3]:[E[0]+(-pb.tx*.55+pb.nx*s*.85)*h,E[1]+(-pb.ty*.55+pb.ny*s*.85)*h];")
rep("NET_PROTO=109", "NET_PROTO=110")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patched')
