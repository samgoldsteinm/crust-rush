"""Patch 60 (web v216, NET_PROTO 118): what a stat point counts for, so karts, cars and bikes are level, and Classic is the middle.
The owner: "It feels like it's hard for the karts to compete with the cars", then (shown the numbers): "I like the classic kart being the
same for everything so shift the stats accordingly so that the classic kart is still neutral that means you might have to re assign the
quantity that a point in a category counts for".
Measured (scratch/statlap3.py: every vehicle alone, the computer driving, standard wheels and glider, three fixed seeds on Margherita and
Basil; scratch/fitstats.py fits the race time to the five effective stats, r2 .91): a point of SPEED was worth 2.45 s a race, acceleration
.76, handling .60, weight .34, off-road .23. The cars put their minus points in weight and off-road (cheap) and their plus points in
speed (dear): every car's total came out ahead of Classic, the karts' (minus points in acceleration and handling) behind; karts averaged
3.3 s a race slower than cars. scratch/reweight.py found the values that put every group's average on Classic, every vehicle within
about 1 s of it: speed x.25, weight x1.95, off-road x3.2 of today's, acceleration and handling as they were. So statMods:
  spd 1 + .0035 e (was .014: a full bar now 1.4% over the middle), wgt 1 + .234 e held to .4..1.6 (was .12), off 2.88 e (was .9);
  the kerb's share of top speed is held to .70..1 (it could pass 1 with the stronger off-road). No vehicle's own numbers change.
The PC the same (scripts/kart_builder.gd stat_mods, kart.gd). The garage's and Settings' explanations give the new figures.
Run once: py.cmd tools/mini/patch60.py"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'patch 60' not in s, 'already patched'


def rep(a, b):
    global s
    assert s.count(a) == 1, (s.count(a), a[:90])
    s = s.replace(a, b)


rep("return {spd:1+.014*e[0],acc:Math.max(.62,1+.09*e[1]),hnd:1+.05*e[2],wgt:1+.12*e[3],off:e[4]*.9};}",
    "return {spd:1+.0035*e[0],acc:Math.max(.62,1+.09*e[1]),hnd:1+.05*e[2],wgt:clamp(1+.234*e[3],.4,1.6),off:e[4]*2.88};}/* (patch 60: a point is worth about the same in a race in every stat) */")
rep("lat<CURB?.86+.03*sm.off:clamp(.58+.08*sm.off,.36,.86);",
    "lat<CURB?clamp(.86+.03*sm.off,.7,1):clamp(.58+.08*sm.off,.36,.86);")
rep("const NET_PROTO=117;", "const NET_PROTO=118;/* (118: patch 60, what a stat point counts for) */")
rep("Top speed. Each bar is about 1.5%: full is 9% faster than the middle, empty 9% slower.",
    "Top speed. Each bar is about 0.25%: full is 1.4% faster than the middle, empty 1.4% slower. Every stat is weighed so a point is worth about the same in a race: a kart, a car and a bike can all match the Classic.")
rep("In a bump the heavier kart is pushed aside less (full against empty: about a third as far), and a kart over 15% lighter also loses a little speed while they touch. A heavier kart also recovers sooner from an item hit: a spin lasts 0.97 s at full, 1.1 s in the middle, 1.23 s at empty.",
    "In a bump the heavier kart is pushed aside less (full against empty: about a quarter as far), and a kart over 15% lighter also loses a little speed while they touch. A heavier kart also loses less speed against a wall and recovers sooner from an item hit: a spin lasts 0.94 s at full, 1.1 s in the middle, 1.27 s at empty.")
rep("Off it every kart is held to a share of its top speed: on grass, sand, dirt or the floor beside a toy track 80% at full, 58% in the middle, 40% at empty; on the kerb 93%, 86%, 79%.",
    "Off it every kart is held to a share of its top speed: on grass, sand, dirt or the floor beside a toy track 86% at full, 58% in the middle, 36% at empty (a few bars either way make most of that difference); on the kerb 100%, 86%, 70%.")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patch 60 applied')
