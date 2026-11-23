"""Patch 118 (web v250): split screen, part D: player 2's sound (as the PC, tools/mini/pc122.py, pc123.py). The owner: "Let's add
the ability to pick karts for player 2 and hear the engine sounds" ... "And sound effect from items it should be like playing a
regular game as player 2".
- Player 2's engine: a second motor voice (E2: the same recipe as player 1's, tuned to player 2's body), driven by their kart.
- Player 2's sounds: everything player 1 hears for their own kart (bumps, boosts, hops, drift tiers, pickups, items, abilities,
  tricks, the special's ready chime, Balloon Battle's pops) plays for player 2's kart too; near() counts both cameras, so the
  sounds of karts near player 2 are heard. Each sound is still played once (it belongs to one kart), so nothing doubles.
Run once, after patch 117: py.cmd tools/mini/patch118.py"""
import re
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'function eng2Tick' not in s, 'already patched'


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:90])
    s = s.replace(a, b)


# sounds: whose kart
rep("function near(k){if(k===camT)return 1;const d=Math.hypot(k.x-camera.position.x,k.y-camera.position.z);",
    "/* (patch 118) split screen: player 2's kart is as near as player 1's, and a kart is as near as the nearer camera */\n"
    "const isMe=k=>k===player||(SPLIT.on&&!!player2&&k===player2);\n"
    "function near(k){if(k===camT||SPLIT.on&&player2&&(k===player2||k===SPLIT.camT2))return 1;let d=Math.hypot(k.x-camera.position.x,k.y-camera.position.z);if(SPLIT.on&&player2)d=Math.min(d,Math.hypot(k.x-SPLIT.c2.x,k.y-SPLIT.c2.z));")
rep("if(k===player)SFX.", "if(isMe(k))SFX.", 19)
n0 = len(re.findall(r"if\(k===player\)\{(SFX\.\w+\([^()]*\));", s))
assert n0 == 13, n0
s = re.sub(r"if\(k===player\)\{(SFX\.\w+\([^()]*\));", r"if(k===player2&&player2)\1;if(k===player){\1;", s)
rep("if(k===player&&k.abC>=1){SFX.ready();", "if(k===player2&&player2&&k.abC>=1)SFX.ready();if(k===player&&k.abC>=1){SFX.ready();")
rep("if(k===player&&!NET.replay){SFX.trick();", "if(k===player2&&player2&&!NET.replay)SFX.trick();if(k===player&&!NET.replay){SFX.trick();", 2)
rep("if(by===player&&!BB.skip){SFX.ring&&SFX.ring();",
    "if(by===player2&&player2&&!BB.skip){SFX.ring&&SFX.ring();showBanner2('+1',.5,'sm');}if(by===player&&!BB.skip){SFX.ring&&SFX.ring();")

# player 2's engine
rep("/* never more than a couple of dozen effect voices at once",
    "/* (patch 118) split screen: player 2's engine, player 1's recipe on its own voice */\n"
    "const E2={};\n"
    "function engMake2(){if(!ac||!master||E2.o1)return;try{const o1=ac.createOscillator(),o2=ac.createOscillator(),w=engWaves&&engWaves.pulse;if(w){o1.setPeriodicWave(w);o2.setPeriodicWave(w);}\n"
    "  const am=ac.createGain();am.gain.value=.68;const amo=ac.createOscillator();amo.type='triangle';const amd=ac.createGain();amd.gain.value=.32;amo.connect(amd);amd.connect(am.gain);\n"
    "  const hp=ac.createBiquadFilter();hp.type='highpass';hp.frequency.value=90;hp.Q.value=.6;const lp=ac.createBiquadFilter();lp.type='lowpass';lp.frequency.value=1100;lp.Q.value=.8;\n"
    "  const pk=ac.createBiquadFilter();pk.type='peaking';pk.frequency.value=1500;pk.Q.value=1.1;pk.gain.value=4;const g=ac.createGain();g.gain.value=0;const g2=ac.createGain();g2.gain.value=.45;\n"
    "  o1.connect(am);o2.connect(g2);g2.connect(am);am.connect(hp);hp.connect(pk);pk.connect(lp);lp.connect(g);g.connect(master);o1.start();o2.start();amo.start();Object.assign(E2,{o1,o2,amo,amd,lp,g,P:ENG_PROF.std,ps:null,gi:0,kick:0,act:0});}catch(e){console.warn('engine 2',e);}}\n"
    "function applyEngine2(k){engMake2();if(!E2.o1||!k)return;E2.P=engineFor(k);E2.ps=null;try{const w=engWaves&&engWaves[E2.P.wave];if(w){E2.o1.setPeriodicWave(w);E2.o2.setPeriodicWave(w);}E2.amd.gain.setTargetAtTime(E2.P.am,ac.currentTime,.05);}catch(e){}}\n"
    "function eng2Tick(dt){if(!E2.g)return;const k=player2,T0=ac.currentTime,P=E2.P,on=!muted&&SPLIT.on&&!!k&&(state==='race'||state==='countdown');if(!on){E2.g.gain.setTargetAtTime(0,T0,.06);return;}\n"
    "  const sp=Math.max(0,k.speed),bst=k.boost>0,r=Math.min(1.3,sp/(BASE_MAX||170)),GT=[0,.2,.42,.64,.86,1.31];let gi=0;while(gi<4&&r>GT[gi+1])gi++;\n"
    "  const rpm=P.gears?Math.min(1.12,.3+.7*Math.min(1,(r-GT[gi])/(GT[gi+1]-GT[gi]))+(bst?.12:0)):Math.min(1.12,.25+.7*Math.min(1.2,r)+(bst?.12:0)),ef=(24+rpm*58+(P.gears?gi*4:0))*P.f;\n"
    "  E2.o1.frequency.setTargetAtTime(ef,T0,.05);E2.o2.frequency.setTargetAtTime(ef,T0,.05);E2.amo.frequency.setTargetAtTime(ef*P.amR,T0,.05);E2.lp.frequency.setTargetAtTime((650+rpm*1500+(bst?500:0))*P.lp,T0,.08);\n"
    "  const a=(sp-(E2.ps==null?sp:E2.ps))/Math.max(dt,1e-3);E2.ps=sp;if(gi!==E2.gi){if(a>0)E2.kick=.55;E2.gi=gi;}E2.kick=Math.max(0,E2.kick-dt*1.4);\n"
    "  const tgt=Math.max(Math.min(1,Math.max(0,a)/((BASE_MAX||170)*.5)),bst?.9:0,E2.kick,r<.12&&a>1?.6:0);E2.act+=(tgt-E2.act)*(1-Math.exp(-dt/(tgt>E2.act?.1:1.2)));\n"
    "  E2.g.gain.setTargetAtTime((.0032+.0024*rpm)+E2.act*(.0038+.003*rpm),T0,.06);}\n"
    "/* never more than a couple of dozen effect voices at once")
rep("try{applyEngine(player);}catch(e){}", "try{applyEngine(player);if(SPLIT.on&&player2)applyEngine2(player2);}catch(e){}")
rep("  requestAnimationFrame(frame);\n}\nboot();", "  if(ac&&E2.g)try{eng2Tick(dt);}catch(e){}/* (patch 118) */\n  requestAnimationFrame(frame);\n}\nboot();")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patch 118 applied')
