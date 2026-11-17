"""Patch 74 (web v222): a delivery's arrow.
The owner: "when doing a pizza delivery mission there should be an arrow at the top of the screen or somewhere that points you in the
direction you need to go".
Under the delivery bar at the top: an arrow turned to where to drive, relative to the camera (straight up = straight ahead), with what it
points at: in the delivery's place, its start line (SB.flag); elsewhere the tunnel or gate to the next place on the shortest way there
(sbNextHop: a breadth-first walk over the places' links, SB_LINKS and a toy place's own gates, both ways), and how far.
Run once: py.cmd tools/mini/patch74.py"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'patch 74' not in s, 'already patched'


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:90])
    s = s.replace(a, b)


rep("function sbActPlace(id){",
    "/* (patch 74) a delivery's way: the next place on the shortest way (over the places' links, both ways), and the point to drive to here */\n"
    "function sbNbrs(id){const r=SB_REG[id];return [...(SB_LINKS[id]||[]),...((r&&r.gates)||[]).map(d=>d.to)];}\n"
    "const _sbHop={};function sbNextHop(from,to){const key=from+'>'+to;if(key in _sbHop)return _sbHop[key];const ids=new Set([...Object.keys(SB_LINKS),...Object.keys(SB_REG)]),adj={};\n"
    "  const add=(a,b)=>{if(!sbRegOf(a)||!sbRegOf(b))return;(adj[a]=adj[a]||new Set()).add(b);(adj[b]=adj[b]||new Set()).add(a);};for(const a of ids)for(const b of sbNbrs(a))add(a,b);\n"
    "  const prev={[from]:null},q=[from];while(q.length){const c=q.shift();if(c===to)break;for(const n of adj[c]||[])if(!(n in prev)){prev[n]=c;q.push(n);}}\n"
    "  if(!(to in prev))return _sbHop[key]=null;let c=to;while(prev[c]!==from&&prev[c]!==null)c=prev[c];return _sbHop[key]=c;}\n"
    "function sbDelAim(a){if(SB.regId===a.to)return SB.flag?{x:SB.flag.x,z:SB.flag.z,say:'Start line'}:null;const n=sbNextHop(SB.regId,a.to),g=n&&SB.gates.find(q=>q.to===n);return g?{x:g.x,z:g.z,say:'To '+sbActPlace(n)}:null;}\n"
    "const _sbDv=new THREE.Vector3();function sbDelArrow(a){const k=player,t=k&&sbDelAim(a);if(!t)return '';camera.getWorldDirection(_sbDv);const fx=_sbDv.x,fz=_sbDv.z,dx=t.x-k.x,dz=t.z-k.y,ang=Math.atan2(fx*dz-fz*dx,fx*dx+fz*dz),d=Math.hypot(dx,dz);\n"
    "  return '<div style=\"display:flex;align-items:center;justify-content:center;gap:8px;margin-top:6px\"><svg width=\"40\" height=\"40\" viewBox=\"-15 -15 30 30\" style=\"transform:rotate('+ang.toFixed(3)+'rad);filter:drop-shadow(0 1px 2px #000)\"><path d=\"M0 -13 L10 6 L0 1 L-10 6 Z\" fill=\"#ffd65a\" stroke=\"#3a1a08\" stroke-width=\"1.5\" stroke-linejoin=\"round\"/></svg>'\n"
    "    +'<span style=\"font-size:12px\">'+t.say+' · '+Math.round(d/10)+' m</span></div>';}\n"
    "function sbActPlace(id){")
rep("+'<div style=\"height:5px;border-radius:3px;background:rgba(255,244,220,.2);margin-top:5px;overflow:hidden\"><div style=\"height:100%;width:'+(a.kind==='deliver'?Math.max(0,100*left/a.T):Math.min(100,100*A.v/a.need)).toFixed(1)+'%;background:'+(left<15?'#e8542f':'#ffd65a')+'\"></div></div>';}",
    "+'<div style=\"height:5px;border-radius:3px;background:rgba(255,244,220,.2);margin-top:5px;overflow:hidden\"><div style=\"height:100%;width:'+(a.kind==='deliver'?Math.max(0,100*left/a.T):Math.min(100,100*A.v/a.need)).toFixed(1)+'%;background:'+(left<15?'#e8542f':'#ffd65a')+'\"></div></div>'+(a.kind==='deliver'?sbDelArrow(a):'')/* (patch 74) */;}")
rep("SBA.barT-=dt;if(SBA.barT<=0){SBA.barT=.2;sbActBar();}", "SBA.barT-=dt;if(SBA.barT<=0){SBA.barT=SBA.act&&SBA.act.a.kind==='deliver'?.05:.2;/* (patch 74: the arrow turns smoothly) */sbActBar();}")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patch 74 applied')
