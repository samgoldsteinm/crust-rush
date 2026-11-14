import asyncio, json
from playwright.async_api import async_playwright
# a battle run fast: which items do karts ever hold, what lies on the table, how many balloons at the start, are the pockets gone
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(channel='chromium', args=['--use-angle=d3d11','--enable-gpu','--ignore-gpu-blocklist','--enable-webgl'])
        ctx = await b.new_context(viewport={'width':960,'height':540}, service_workers='block'); pg = await ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto('http://localhost:8771/webcopy6/index.html')
        await pg.wait_for_function("document.getElementById('menu')&&!document.getElementById('menu').hidden", timeout=600000)
        await pg.evaluate("__ev(`qKey='fast';applyQuality();mode='bb';introSkip=true;goRace(MAPS.findIndex(m=>m.battle))`)")
        await pg.wait_for_function("document.getElementById('raceLd').hidden", timeout=900000)
        for i in range(400):
            if await pg.evaluate("__ev(`state`)") == 'race': break
            await pg.wait_for_timeout(500)
        r = await pg.evaluate("""__ev(`(()=>{const start=karts.map(k=>k.bal),seen={},haz={},proj={};player.auto=true;for(let i=0;i<120*150&&!BB.over;i++){update(STEP);if(i%30===0){for(const k of karts)for(const it of [k.item,k.item2,k.held&&k.held.type,...(k.pend||[])])if(it)seen[it]=(seen[it]||0)+1;for(const h of hazards)haz[h.type||h.kind||'?']=1;for(const q of projectiles)proj[q.type||q.kind||'?']=1;}}
          /* the pockets beside the ramps: is any floor-level place walled in on three sides within the old gaps? */
          const pocket=[[-275,246],[247,-110],[366,-110]].map(([x,z])=>[x,z,Math.round(battleG(x,z))]);
          return JSON.stringify({balloonsAtStart:start,boxes:boxes.length,itemsEverHeld:Object.keys(seen),onTheTable:Object.keys(haz),thrown:Object.keys(proj),oldPocketsNowRamp:pocket,pops:karts.reduce((a,k)=>a+(k.bbS||0),0),t:Math.round(BB.T-BB.t)})})()`)""")
        print(r); print('errors', errs[:4]); await b.close()
asyncio.run(main())
