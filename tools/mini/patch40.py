"""Patch 40 (web v204; Sandbox only, nothing a race reads: online stays 114): drive up the hills on every pizza.
The owner, 2026-11-15, with a picture of the dunes beside Oven Rush Raceway: "In sandbox I want to be able to drive on hills on all the maps
such as these hills. You should be able to drive up them unless of course they are straight up and down. The car should struggle a little
like a real car would to get up the hills, better off-roading will help as well to climb them".
Measured first (scratch/oven_probe.js): the land beside the pizza tracks rises 50-75 degrees for its first 40-60 units, then rolls gently;
v200's limit (sbClimb, about 40 degrees for a middle kart) stopped every kart at the foot. The kerbs are 4.6 high: already a step.
- The steepest ground a kart can climb (sbClimb, a rise over SB_R): tan 1.88 + 0.24*off, from 1.19 to 2.75: about 62 degrees for a middle
  kart, 70 the best off-road, 50 the worst. Steeper is a cliff, as before.
- The pull back down a hill going up, in Sandbox only: 165 * sin(slope) * sbGrav (it was tan(slope) * sbGrav, which grows without end);
  sbGrav .69 - .04*off (.4 to .95). With the engine's own push (ACCEL 110 * acceleration, less as the speed rises) a middle kart keeps
  about 30% of its top speed up 50 degrees and 15% up 60; the best off-road about 40% up 60; the worst stalls at about 53.
  So the kart's acceleration matters too, as a real car's power does.
The PC has the same in kart.gd and sandbox.gd. Run once: py.cmd tools/mini/patch40.py"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'patch 40' not in s, 'already patched'


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:90])
    s = s.replace(a, b)


rep("A middle kart: 45% of the pull, up to about 40 degrees; the best off-road 15%, 50 degrees; the worst 85%, 26 degrees */",
    "(patch 40, the owner: drive up the hills \"unless of course they are straight up and down\") the pull goes by the sine of the slope:\n"
    "   a middle kart 69% of it, up to about 62 degrees; the best off-road 55%, 70 degrees; the worst 83%, 50 degrees */")
rep("function sbGrav(k){return clamp(.45-.085*sbOffRd(k),.12,.9);}", "function sbGrav(k){return clamp(.69-.04*sbOffRd(k),.4,.95);}")
rep("function sbClimb(k){return SB_R*clamp(.84+.1*sbOffRd(k),.45,1.2);}", "function sbClimb(k){return SB_R*clamp(1.88+.24*sbOffRd(k),1.19,2.75);}")
rep("k.speed-=sl*165*(SBX&&sl>0?sbGrav(k):1)*dt;", "k.speed-=sl*165*(SBX&&sl>0?sbGrav(k)/Math.sqrt(1+sl*sl):1)*dt;/* (patch 40) Sandbox uphill: by the sine */")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patch 40 applied')
