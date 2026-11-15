"""Patch 32 (web v197, online version 111): part stats that add up; the Sandbox speed slider's engine side; the body on a jump ramp.

1. PART STATS STACK. The owner, 2026-11-14: "it doesnt look like the stats from the glider dont stack with the stat changes from the wheel.
   for example if the wheel increases speed by 1 and the glider increases speed by 1 that would be a total of 2 speed increase instead of
   overlapping them and giving them it just 1".
   The cards showed a part's own numbers (st), but the sum weighted a wheel 1 and a glider .5 (the body 1.5), squeezed the total through
   tanh and rounded it to bars: +1 and +1 often came out as +1. Now, the SAME numbers on web and PC (godot/scripts/kart_builder.gd):
     eBody[i] = 4*tanh(1.5*body.st[i]/4)                                   a vehicle on its own is what it was
     e[i]     = clamp(eBody[i] + (wheel.st[i] + glider.st[i])/1.5, -4, 4)  wheel = wheelOf(b): a bike's built-in set
     statMods from e exactly as before (spd 1+.022e, acc max(.62,1+.09e), hnd 1+.05e, wgt 1+.12e, off .9e)
     bars: the vehicle alone round(6+1.5*eBody) (plus its built-in wheels' st on a bike); the build that plus wheel st plus glider st,
           held to 0..12
   So one point on a wheel or glider card is one bar, they add, and the driving follows the bars. This changes how karts drive:
   NET_PROTO 110 -> 111 (PC: PROTO 111 in the same release).
2. SANDBOX'S SPEED SLIDER (tools/mini/sandbox.js: sbSpd): in Sandbox the player's throttle is multiplied by SB.spd, and D-pad left and
   right step it (there they no longer steer: the stick does).
3. THE BODY ON A JUMP RAMP (looks only). syncKart takes the body's pitch from surfH, which knows the ground and the raised road but not
   a jump ramp, so the body stayed level all the way up. k.rampS is the slope of the ramp under the kart along its heading (set where
   the ramp's physics sets onRamp; nothing reads it but syncKart). A friend's kart seen on line has none (it is not sent): level, as before.
Run once, after patch31: py.cmd tools/mini/patch32.py"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'function statE(' not in s, 'already patched'
assert 'bbResRow(k)' in s.split('/*MINI-END*/')[1], 'run patch31.py first'


def rep(a, b, n=1):
    global s
    if s.count(a) == 0 and '\n' in a: a = a.replace('\n', '\r\n'); b = b.replace('\n', '\r\n')
    assert s.count(a) == n, (s.count(a), a[:80])
    s = s.replace(a, b)


# ---- 1. stats
rep("""/* every build sits on a 12-step scale per stat: the body counts most, wheels less, the glider a little.
   Parts are balanced so every gain is paid for elsewhere, and stacking is soft-capped: the further a stat is pushed, the less each extra point adds. */
const STAT_W=[1.5,1,.5],STAT_MID=6,STAT_BARS=12;
function statRaw(b){const o=[0,0,0,0,0];[BODIES[b.b],wheelOf(b),GLIDERS[b.g]].forEach((p,k)=>{for(let i=0;i<5;i++)o[i]+=p.st[i]*STAT_W[k];});return o;}
const statSoft=r=>4*Math.tanh(r/4);
function statMods(b){const e=(statsOn?statRaw(b):[0,0,0,0,0]).map(statSoft);return {""",
    """/* every build sits on a 12-step scale per stat. The vehicle sets where it starts (its own numbers count for the most: statBody); every
   point on a wheel or glider card is then exactly one step, and they add: +1 and +1 is +2 (web v197, tools/mini/patch32.py; before, a
   glider's point counted half, the sum was squeezed and rounded, and two +1s often showed as +1). Only the ends of the scale cap.
   The driving follows the same numbers (statE is in the engine's own units: 1.5 steps to one). PC: KartBuilder.stat_mods, the same sums. */
const STAT_W=[1.5,1,.5],STAT_MID=6,STAT_BARS=12;
const statSoft=r=>4*Math.tanh(r/4),statBody=(b,i)=>statSoft(BODIES[b.b].st[i]*STAT_W[0]);
function statE(b){const w=wheelOf(b),g=GLIDERS[b.g],o=[];for(let i=0;i<5;i++)o.push(clamp(statBody(b,i)+(w.st[i]+g.st[i])/1.5,-4,4));return o;}
function statMods(b){const e=statsOn?statE(b):[0,0,0,0,0];return {""")
rep("function statBarsOf(b,all){const o=[0,0,0,0,0],bd=BODIES[b.b],bike=!!(bd.bike&&bd.bw);[bd,wheelOf(b),GLIDERS[b.g]].forEach((p,k)=>{if(!all&&(k===2||(k===1&&!bike)))return;for(let i=0;i<5;i++)o[i]+=p.st[i]*STAT_W[k];});return o.map(r=>clamp(Math.round(STAT_MID+statSoft(r)*1.5),0,STAT_BARS));}",
    "function statBarsOf(b,all){const bd=BODIES[b.b],bike=!!(bd.bike&&bd.bw),w=wheelOf(b),g=GLIDERS[b.g],o=[];for(let i=0;i<5;i++)o.push(clamp(Math.round(STAT_MID+statBody(b,i)*1.5)+(all||bike?w.st[i]:0)+(all?g.st[i]:0),0,STAT_BARS));return o;}/* the vehicle's own steps, plus one for every point on the wheels' and the glider's cards */")
rep("const NET_PROTO=110;", "const NET_PROTO=111;")
# ---- 2. the Sandbox speed slider
rep("  if(SBX&&sbStop()){/* Sandbox: parked, or both brake buttons held: no throttle, and no brake either (held, it would reverse) */o.brake=false;o.nb=false;o.mul=0;}",
    "  if(SBX&&sbStop()){/* Sandbox: parked, or both brake buttons held: no throttle, and no brake either (held, it would reverse) */o.brake=false;o.nb=false;o.mul=0;}\n  else if(SBX&&o.mul>0)o.mul*=sbSpd();/* Sandbox's speed slider: the share of its top speed the car may reach */")
rep("    PAD.steer=clamp(sx+(dr?1:0)-(dl?1:0),-1,1);PAD.gas=M.GAS.some(pr);",
    "    PAD.steer=SBX?sx:clamp(sx+(dr?1:0)-(dl?1:0),-1,1);if(SBX&&state==='race'&&!(SPEC&&SPEC.on)){if(edge(M.LEFT))sbSpdStep(-1);if(edge(M.RIGHT))sbSpdStep(1);}/* (in Sandbox the D-pad's left and right are the speed slider; the stick steers) */PAD.gas=M.GAS.some(pr);")
# ---- 3. the body on a jump ramp
rep("  let G=BATTLE?battleG(k.x,k.y,k.wy):kGround(k),onR=false,gR=false;", "  let G=BATTLE?battleG(k.x,k.y,k.wy):kGround(k),onR=false,gR=false,rS=0;/* rS: looks only (syncKart) */")
rep("{if(k.wy<=G+hh+1.5){G+=hh;onR=true;gR=!!r.glide;}continue;}", "{if(k.wy<=G+hh+1.5){G+=hh;onR=true;gR=!!r.glide;rS=r.h/r.len*fwd;}continue;}")
rep("  k.onRamp=onR;k.onGlide=gR;", "  k.onRamp=onR;k.rampS=onR?rS:0;k.onGlide=gR;")
rep("      sF=(hF-hB)/(fF-fR),sR=(hL-hRt)/(2*fW),", "      sF=(hF-hB)/(fF-fR)+(k.onRamp?k.rampS||0:0)/* on a jump ramp the body lies along it */,sR=(hL-hRt)/(2*fW),")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patched')
