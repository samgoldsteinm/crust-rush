"""Patch 76 (web v222): the delivery arrow takes the quickest way you can drive, not the fewest places.
The owner: "make it point to the quickest route that is driveable to finish the mission. so if you have to go through a tunnel first it
will point to the tunnel".
SB_COST (from tools/neon/sbcost.py, build/sb_cost.json): in each place, the driving distance from each gate to each other gate and to the
start line (a road place along the lap, the shorter way round; elsewhere straight across x1.15); gates are named by where they lead.
sbRouteNext(to): from where the kart is (in this place, its live gates: along the lap or straight across), a shortest-path search over
(place, the gate you came in by) to the destination's start line; returns the first gate's place. sbNextHop (fewest places) only when the
table has no entry. Margherita to Sauce Spiral now goes by the Oven Rush Raceway, as the delivery's own tip says.
Run once, after patch 74: py.cmd tools/mini/patch76.py"""
import json
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'patch 76' not in s, 'already patched'
C = json.load(open('D:/crust-rush/source/build/sb_cost.json', encoding='utf-8'))


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:90])
    s = s.replace(a, b)


rep("function sbDelAim(a){if(SB.regId===a.to)return SB.flag?{x:SB.flag.x,z:SB.flag.z,say:'Start line'}:null;const n=sbNextHop(SB.regId,a.to),",
    "/* (patch 76) each place's driving distances (tools/neon/sbcost.py): 'a>b' from the gate to a to the gate to b, '@flag' the start line */\n"
    "const SB_COST=" + json.dumps(C, separators=(',', ':')) + ";\n"
    "function sbRouteNext(to){const t=performance.now(),R=SB._rt;if(R&&R.to===to&&R.reg===SB.regId&&t-R.t<500)return R.v;const v=sbRouteCalc(to);SB._rt={t,to,reg:SB.regId,v};return v;}/* (worked out twice a second) */\n"
    "function sbRouteCalc(to){const k=player;if(!k||!SB_COST[to])return null;const road=SB.kind==='road',cum=road?SB.cum||(SB.cum=(()=>{const c=[0];for(let j=1;j<=N;j++){const a=track[j-1],b=track[j%N];c.push(c[j-1]+Math.hypot(b.x-a.x,b.y-a.y));}return c;})()):null;\n"
    "  let kj=0;if(road){let bd=1e18;for(let j=0;j<N;j+=2){const d=(track[j].x-k.x)**2+(track[j].y-k.y)**2;if(d<bd){bd=d;kj=j;}}}\n"
    "  const here=g=>{if(road&&g.j!=null){const L=cum[N],d=Math.abs(cum[kj]-cum[g.j]);return Math.min(d,L-d);}return Math.hypot(g.x-k.x,g.z-k.y)*1.15;};\n"
    "  const Q=[],seen={};for(const g of SB.gates)Q.push({r:g.to,f:SB.regId,c:here(g),first:g.to});let best=null;\n"
    "  while(Q.length){Q.sort((a,b)=>a.c-b.c);const q=Q.shift(),key=q.r+'|'+q.f;if(seen[key])continue;seen[key]=1;if(best&&q.c>=best.c)break;const T=SB_COST[q.r]||{};\n"
    "    if(q.r===to){const c=q.c+(T[q.f+'>@flag']||0);if(!best||c<best.c)best={c,first:q.first};continue;}\n"
    "    for(const kk in T){const [a,b]=kk.split('>');if(a!==q.f||b==='@flag'||!sbRegOf(b))continue;Q.push({r:b,f:q.r,c:q.c+T[kk],first:q.first});}}\n"
    "  return best?best.first:null;}\n"
    "function sbDelAim(a){if(SB.regId===a.to)return SB.flag?{x:SB.flag.x,z:SB.flag.z,say:'Start line'}:null;const n=sbRouteNext(a.to)||sbNextHop(SB.regId,a.to),")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patch 76 applied')
