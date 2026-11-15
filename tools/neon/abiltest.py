"""The drivers' specials after patch 37 (web v202, online 113), and a time trial of every vehicle.
   py.cmd tools/neon/abiltest.py            the ability checks (on Margherita Ring)
   py.cmd tools/neon/abiltest.py trial [maps...]   every body on Standard wheels and the Parachute, the player's kart driving itself alone
                                            (no rivals, items taken away every step, the same random numbers each run): race time
Checks: the Shockwave's reach (150), what it spares (air, the blink after a hit) and what it pops without a spin (shields, garlic),
that it still goes through an ability boost; a held item stops a sure anchovy; MEGA_T 4.5, FLAT_T 2; Olive's slick reach; a storm
slice's first bounce turns toward a racer ahead; NET_PROTO 113."""
import asyncio, json, sys
from playwright.async_api import async_playwright
TRIAL = len(sys.argv) > 1 and sys.argv[1] == 'trial'
MAPS = sys.argv[2:] if TRIAL and len(sys.argv) > 2 else ['margherita']
CHECK = r"""(()=>{const R={},P=player,O=karts.filter(k=>k!==P);
const clr=k=>{Object.assign(k,{shield:0,mzH:0,shL:0,inv:0,air:false,glide:false,spin:0,pestoT:0,rush:0,absT:0,held:null,loop:null,ghostT:0,megaT:0,chiliT:0,oliveT:0,flatT:0,flatImm:0,big:false,wvy:0});};
clr(P);const put=(k,d,o)=>{clr(k);k.x=P.x+d;k.y=P.y;k.wy=P.wy;Object.assign(k,o||{});};
const cs=[['plain 100',100,{}],['plain 200',200,{}],['Mozz shield',100,{shield:7,mzH:3}],['in the air',100,{air:true}],['blinking',100,{inv:2}],['Pesto Rush',100,{pestoT:3,rush:3}],['garlic',100,{shL:2}]];
cs.forEach((c,i)=>put(O[i],c[1],c[2]));blast(P.x,P.y,150,P,'pep','#ffd23a',true);
R.shock=cs.map((c,i)=>({case:c[0],spun:O[i].spin>0,shield:O[i].shield,shL:O[i].shL}));
const want={'plain 100':1,'plain 200':0,'Mozz shield':0,'in the air':0,'blinking':0,'Pesto Rush':1,'garlic':0};
R.shockOk=R.shock.every(q=>q.spun===!!want[q.case])&&R.shock[2].shield===0&&R.shock[6].shL===0;
/* anchovy: a held item stops it; without one it hits */
const fish=tg=>({type:'torp',custom:1,sure:1,target:tg,x:tg.x+4,y:tg.y,vx:0,vy:0,t:600,owner:P,safe:0,b:0,mesh:itemMesh('torpedo')});
/* both on the track, well apart */const tp=j=>track[((P.idx+j)%N+N)%N];const A=O[0],B=O[1];clr(A);clr(B);A.held={it:'oil',sl:1,t:0,mesh:null};A.x=tp(40).x;A.y=tp(40).y;B.x=tp(80).x;B.y=tp(80).y;
const r1=itemsProj(fish(A),STEP),r2=itemsProj(fish(B),STEP);R.fish={RIM:typeof RIM!=='undefined'?RIM:null,heldUsedUp:r1,heldGone:A.held===null,heldSpun:A.spin>0,plainSpun:B.spin>0,r2};
R.fishOk=r1&&A.held===null&&!(A.spin>0)&&B.spin>0;
R.consts={MEGA_T,FLAT_T,NET_PROTO};R.constOk=MEGA_T===4.5&&FLAT_T===2&&NET_PROTO===113;
/* Olive: a slick catches at 16.5 units (it used not to past 14.1) */
const C=O[2];clr(C);C.x=tp(120).x;C.y=tp(120).y;C.wy=C.lastG=groundAt(C.x,C.y);C.idx=(P.idx+120)%N;C.speed=0;hazards.push({x:C.x+16.5,y:C.y,ti:C.idx,t:1e9,born:1,owner:P,armed:true,olive:1,mesh:itemMesh('oil')});
update(STEP);R.slick={oilT:+(C.oilT||0).toFixed(2),air:C.air,slicksLeft:hazards.filter(h=>h.olive&&h.owner===P).length};R.slickOk=C.oilT>0;
/* Pep: the first wall bounce turns a slice toward a racer ahead */
/* away from every other kart */const D=O[3];clr(D);const s={x:P.x+5000,y:P.y+5000,vx:400,vy:0};D.x=s.x+300;D.y=s.y+100;const a0=Math.atan2(s.vy,s.vx);pepAim(s);const a1=Math.atan2(s.vy,s.vx);
R.pep={turnedDeg:+((a1-a0)*57.3).toFixed(1),speed:+Math.hypot(s.vx,s.vy).toFixed(1)};R.pepOk=a1>a0&&a1-a0<=.5001&&Math.abs(Math.hypot(s.vx,s.vy)-400)<1e-6;
R.desc=ABIL.pineapple[1];return R;})()"""
TRIALJS = r"""((bi)=>{statsOn=true;CPUS=0;playerBuild={b:bi,w:0,g:0,p:0,t:''};resetRace();state='race';raceTime=0;/* (the countdown runs on the clock, not in update) */const P=player;P.auto=true;const rr=Math.random;Math.random=prng(7);let i=0;
for(;i<120*600&&!P.finished;i++){update(STEP);P.item=P.item2=null;P.held=null;}Math.random=rr;return {b:BODIES[bi].id,name:BODIES[bi].name,st:BODIES[bi].st,t:P.finished?+P.finishTime.toFixed(2):null};})"""


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(channel='chromium', args=['--use-angle=d3d11', '--enable-gpu', '--ignore-gpu-blocklist', '--enable-webgl'])
        for mp in MAPS:
            ctx = await b.new_context(viewport={'width': 960, 'height': 540}, service_workers='block'); pg = await ctx.new_page(); errs = []
            pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
            await pg.goto('http://localhost:8771/webcopy6/index.html')
            await pg.wait_for_function("document.getElementById('menu')&&!document.getElementById('menu').hidden", timeout=600000)
            await pg.evaluate("(a)=>__ev(`qKey='fast';applyQuality();clsKey='medium';mode='single';introSkip=true;goRace(MAPS.findIndex(m=>m.id==='${a}'))`)", mp)
            await pg.wait_for_function("document.getElementById('raceLd').hidden", timeout=900000)
            for i in range(400):
                if await pg.evaluate("__ev(`state`)") in ('race', 'countdown'): break
                await pg.wait_for_timeout(500)
            if not TRIAL:
                r = json.loads(await pg.evaluate("(js)=>__ev('JSON.stringify('+js+')')", CHECK))
                for k in ('shock', 'fish', 'consts', 'slick', 'pep', 'desc'): print(k, r[k])
                ok = all(r[k] for k in ('shockOk', 'fishOk', 'constOk', 'slickOk', 'pepOk')) and not errs
                print({k: r[k] for k in ('shockOk', 'fishOk', 'constOk', 'slickOk', 'pepOk')}, 'errors', errs[:3])
                print('ABILITY TEST', 'passed' if ok else 'FAILED')
            else:
                n = await pg.evaluate("__ev(`BODIES.length`)"); res = []
                for bi in range(n):
                    r = json.loads(await pg.evaluate("([js,bi])=>__ev('JSON.stringify(('+js+')('+bi+'))')", [TRIALJS, bi]))
                    res.append(r); print(mp, r, flush=True)
                json.dump(res, open(f'D:/crust-rush/scratch/trial_{mp}.json', 'w'))
                print('errors', errs[:3])
            await ctx.close()
        await b.close()
asyncio.run(main())
