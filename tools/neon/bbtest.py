import asyncio, json, sys, os
from playwright.async_api import async_playwright
# usage: bbtest.py [rounds] [shots]   Balloon Battle (the rules of 2026-11-14: sets of 5, 3 and 1 balloons, then out) with every kart driven
# by the computer, fast-forwarded. For each round: how it ended (one driver left, or the clock), the time left, the balloons popped, the
# order of going out, the longest any kart stood still, karts below the table at the end, how often each ramp was driven onto, how often a
# driver had to be set down again (jams), bad numbers. With `shots`: pictures of the menu, the round and the results in scratch/bb_*.png.
# Q=<quality> picks the preset (default ultra).
ROUNDS = int(sys.argv[1]) if len(sys.argv) > 1 else 6
SP = 'D:/crust-rush/scratch'
HOOK = """__ev(`player.auto=true;window.__bb={stuck:karts.map(()=>0),maxStuck:0,nan:0,esc:0,ramp:BB.ramps.map(()=>0),z:karts.map(()=>-1),low:0,where:[]};window.__lastp=karts.map(k=>[k.x,k.y]);BB.jams=0;
  window.__ff=(sec)=>{const n=Math.round(sec/STEP);for(let i=0;i<n&&!BB.over;i++){update(STEP);
      karts.forEach((k,ki)=>{if(k.bbDead||k.bbOut>0)return;const z=bbZone(k.x,k.y);if(z!==__bb.z[ki]){if(z>=0)__bb.ramp[z]++;__bb.z[ki]=z;}});
      if(i%120===0)karts.forEach((k,ki)=>{if(k.bbDead)return;const l=__lastp[ki],d=Math.hypot(k.x-l[0],k.y-l[1]);__lastp[ki]=[k.x,k.y];if(d<6&&!(k.bbOut>0)){__bb.stuck[ki]++;if(__bb.stuck[ki]===2)__bb.where.push([Math.round(k.x),Math.round(k.y),Math.round(k.wy||0),Math.round(k.a*57),k.item||'-',Math.round(k.bbA.tx),Math.round(k.bbA.tz)]);}else __bb.stuck[ki]=0;__bb.maxStuck=Math.max(__bb.maxStuck,__bb.stuck[ki]);
          if(!isFinite(k.x)||!isFinite(k.y)||!isFinite(k.wy))__bb.nan++;if(!(k.bbOut>0)&&(Math.abs(k.x)>BB_X+10||Math.abs(k.y)>BB_Z+4))__bb.esc++;});}
    const lost=k=>k.bbDead?BB_SETS.reduce((a,b)=>a+b,0):BB_SETS.slice(0,k.bbL||0).reduce((a,b)=>a+b,0)+BB_SETS[k.bbL||0]-(k.bal||0);
    return JSON.stringify({t:Math.round(BB.t),state,over:BB.over,left:karts.filter(k=>!k.bbDead).length,pops:karts.reduce((a,k)=>a+lost(k),0),pts:karts.map(k=>k.bbS||0),sets:karts.map(k=>k.bbDead?'x':BB_SETS[k.bbL||0]+':'+(k.bal||0)),
      out:karts.filter(k=>k.bbDead).sort((a,b)=>b.bbPlace-a.bbPlace).map(k=>k.r.name),order:bbRank().map(k=>k.r.name+(k.bbDead?'(out)':'')),places:karts.map(k=>k.place||0),
      below:karts.filter(k=>!k.bbDead&&(k.wy||0)<-20).length,items:karts.filter(k=>k.item).length,proj:projectiles.length,haz:hazards.length,jams:BB.jams||0,bb:{maxStill:__bb.maxStuck*2,nan:__bb.nan,esc:__bb.esc,ramp:__bb.ramp,where:__bb.where}});};1`)"""


async def start(pg):
    await pg.evaluate("(q)=>__ev(`if(SPEC.on)specExit(false);results.hidden=true;qKey='${q}';applyQuality();mode='bb';introSkip=true;goRace(MAPS.findIndex(m=>m.battle))`)", os.environ.get('Q', 'ultra'))
    await pg.wait_for_function("document.getElementById('raceLd').hidden", timeout=900000)
    for i in range(400):
        if await pg.evaluate("__ev(`state`)") == 'race': break
        await pg.wait_for_timeout(500)
    await pg.evaluate(HOOK)


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(channel='chromium', args=['--use-angle=d3d11', '--enable-gpu', '--ignore-gpu-blocklist', '--enable-webgl'])
        ctx = await b.new_context(viewport={'width': 1280, 'height': 720}, service_workers='block'); pg = await ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:400]))
        pg.on('console', lambda m: errs.append('console:' + m.text[:300]) if m.type == 'error' and 'GPU' not in m.text and 'WebGL' not in m.text else None)
        await pg.goto('http://localhost:8771/webcopy6/index.html')
        await pg.wait_for_function("document.getElementById('menu')&&!document.getElementById('menu').hidden", timeout=600000)
        shots = len(sys.argv) > 2
        if shots:                                            # the menu with the mode chosen, as a player gets there
            await pg.click('#modeSeg button[data-m="bb"]'); await pg.wait_for_timeout(2500); await pg.screenshot(path=f'{SP}/bb_menu.png')
        ended = []
        for rn in range(ROUNDS):
            await start(pg)
            if rn == 0:
                print('battle', await pg.evaluate("__ev(`JSON.stringify({BATTLE,T:BB.T,sets:BB_SETS,shapes:BB.shapes.length,boxes:boxes.length,spawn:BB.spawn.length,ramps:BB.ramps.length,karts:karts.length,N,RIM:Math.round(RIM)})`)"), flush=True)
            if shots and rn == 0:
                for i in range(3):
                    await pg.evaluate("__ev(`__ff(6)`)"); await pg.wait_for_timeout(1500); await pg.screenshot(path=f'{SP}/bb_{i}.png')
            r = {}
            for i in range(60):
                r = json.loads(await pg.evaluate("__ev(`__ff(20)`)"))
                if r['over']: break
            how = 'one driver left' if r['left'] <= 1 else 'the clock'
            ended.append(how)
            print(f"round {rn + 1}: ended by {how}, {r['t']} s left, {r['pops']} pops, drivers left {r['left']}, out in order {r['out']}, final order {r['order']}", flush=True)
            print(f"   points {r['pts']}, sets {r['sets']}, longest still {r['bb']['maxStill']} s, below the table at the end {r['below']}, ramps driven onto {r['bb']['ramp']}, set down again {r['jams']}, bad numbers {r['bb']['nan']}, outside {r['bb']['esc']}", flush=True)
            if os.environ.get('WHERE'): print('   stood still 4 s at [x, z, height, heading, item, target x, target z]:', r['bb']['where'], flush=True)
            if shots and rn == 0: await pg.wait_for_timeout(5000); await pg.screenshot(path=f'{SP}/bb_res.png')   # the results
        print('ended', ended, 'errors', errs[:8])
        await b.close()
asyncio.run(main())
