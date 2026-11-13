# tenth engine patch (v165): handling on toy tracks, from the user's play-test of Bedroom Blitz.
# - steering a little less sharp: TURN x1.2 on toy tracks (was x1.3; regular tracks 2.2 as before)
# - drifts start and end quicker, because a toy track is one quick bend after another: the drift builds to full in 0.38 s
#   (0.57 s elsewhere); it ends after 0.18 s with the stick straight (0.3 s elsewhere; 0.3 s instead of 0.5 s with the button
#   held), can end from 0.18 s into the drift, and full grip is back 0.15 s after it ends (0.25 s elsewhere).
# The numbers are DRIN (how fast a drift builds) and DROUT (a factor on the times that end one); both set per map in loadMap0.
# Kart physics: NET_PROTO 103, and the same numbers in the PC's kart.gd (it keys them off the track's toy flag).
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (a[:70], s.count(a)); s = s.replace(a, b)
rep("LS=1,TURN=2.2,TOYT=false;", "LS=1,TURN=2.2,TOYT=false,DRIN=1.75,DROUT=1;")
rep("TOYT=!!def.toy;TURN=TOYT?2.86:2.2;/* a toy track's bends are tight: karts turn 30% quicker on it */",
    "TOYT=!!def.toy;TURN=TOYT?2.64:2.2;/* a toy track's bends are tight: karts turn 20% quicker on it (30% was too sharp) */DRIN=TOYT?2.6:1.75;DROUT=TOYT?.6:1;/* and drifts start and end quicker there: one quick bend after another */")
rep("if(k.dTime>(up?0:hu?.3:.45)&&st<(up?.6:hu?.15:.3)&&(hu||sl<.14)){k.sT+=dt;if(k.sT>(up?.016:hu?(inp.brake?.5:.3):.3))dRel=true;}",
    "if(k.dTime>(up?0:hu?.3*DROUT:.45)&&st<(up?.6:hu?.15:.3)&&(hu||sl<.14)){k.sT+=dt;if(k.sT>(up?.016:hu?(inp.brake?.5:.3)*DROUT:.3))dRel=true;}")
rep("k.drift=0;k.charge=0;k.gripT=.25;}", "k.drift=0;k.charge=0;k.gripT=.25*DROUT;}")
rep("else{k.dAmt=Math.min(1,(k.dAmt||0)+dt*1.75);", "else{k.dAmt=Math.min(1,(k.dAmt||0)+dt*DRIN);")
rep("NET_PROTO=102", "NET_PROTO=103")
open(p, 'w', encoding='utf-8', newline='').write(s); print('patched')
