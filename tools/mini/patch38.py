"""Patch 38 (web v203, ONLINE VERSION 114): the vehicles evened out.
The owner, 2026-11-15, after a time trial showed top speed decided almost everything (Formula best, Monster Truck 12% behind):
"Yes go ahead with the vehicle changes".
- Speed per point 2.2% -> SPD_K (statMods .spd); the other stats count for more:
- Handling also gives grip: outside a drift the path follows where the kart points 1 + 1.2*(hnd-1) as fast (0.76x..1.24x).
- Weight: a wall hit costs 1 - 0.4*(wgt-1) of the usual speed (a heavy kart keeps more, a light one loses more; 0.81x..1.19x).
- Off-road: kerb 0.86 + 0.03*off (was 0.02), grass clamp(0.58 + 0.08*off, 0.36, 0.86) (was 0.06, 0.4, 0.82).
- Stat sums: Slicer [2,-2,1,-1,-2] -> [2,-1,1,-1,-1] (it was 2 points short), Pronto [0,-1,0,2,1] -> [0,-2,0,2,1] and
  Tomatino [-1,1,0,0,2] -> [-1,0,0,0,2] (each 2 points over, now 1). Numbers only; the models are untouched.
The PC has the same in kart_builder.gd / kart.gd / garage.json / roster.json / webnet.gd. Run once: py.cmd tools/mini/patch38.py"""
import sys
SPD_K = sys.argv[1] if len(sys.argv) > 1 else '.014'
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'patch 38' not in s, 'already patched'


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:90])
    s = s.replace(a, b)


rep("return {spd:1+.022*e[0],", "return {spd:1+%s*e[0]," % SPD_K)
rep("function validBuild(b){",
    "/* (patch 38) weight in a wall hit: a heavy kart keeps more of its speed (0.81x the loss at the heaviest, 1.19x at the lightest) */\n"
    "const wallK=k=>k&&k.sm&&isFinite(k.sm.wgt)?1-.4*(k.sm.wgt-1):1;\nfunction validBuild(b){")
for c in ('.22', '.15', '.35', '.2'):
    n = s.count('k.speed*=1-%s*dot' % c)
    assert n in (1, 4), (c, n)
    s = s.replace('k.speed*=1-%s*dot' % c, 'k.speed*=1-%s*dot*wallK(k)' % c)
rep("tp=lat<RW?1:lat<CURB?.86+.02*sm.off:clamp(.58+.06*sm.off,.4,.82);",
    "tp=lat<RW?1:lat<CURB?.86+.03*sm.off:clamp(.58+.08*sm.off,.36,.86);/* (patch 38) off-road counts for more */")
rep("(k.drift?9-5*da:k.gripT>0?7:9)", "(k.drift?9-5*da:(k.gripT>0?7:9)*(1+1.2*(k.sm.hnd-1)))/* (patch 38) handling is grip too */")
rep("name:'Slicer',desc:'Built around a giant pizza cutter. Long, low and razor quick once it gets going.',st:[2,-2,1,-1,-2]",
    "name:'Slicer',desc:'Built around a giant pizza cutter. Long, low and razor quick once it gets going.',st:[2,-1,1,-1,-1]")
rep("Heavy and sure-footed, slow to wind up.',st:[0,-1,0,2,1]", "Heavy and sure-footed, slow to wind up.',st:[0,-2,0,2,1]")
rep("a little lazy on the straights.',st:[-1,1,0,0,2]", "a little lazy on the straights.',st:[-1,0,0,0,2]")
rep("const NET_PROTO=113;", "const NET_PROTO=114;")
s = s.replace("function statMods(b){", "/* patch 38: speed counts for less, handling/weight/off-road for more */function statMods(b){", 1)
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patch 38 applied, speed per point', SPD_K)
