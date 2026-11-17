"""The UNLOCK code and the style shop (web patch 70):   py.cmd tools/neon/unlocktest.py      (webtest.py must be serving)
Before the code a paid colour is locked; after it everything in the style shop can be picked, picking one costs no coins and records no
purchase (crust-own, the coins untouched); after a reload (the code is for one session) the picked style goes back to the free default.
Prints UNLOCK TEST passed / FAILED."""
import asyncio, json
from playwright.async_api import async_playwright


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(channel='chromium', args=['--use-angle=d3d11', '--enable-gpu', '--ignore-gpu-blocklist', '--enable-webgl'])
        ctx = await b.new_context(viewport={'width': 1280, 'height': 800}, service_workers='block')
        await ctx.add_init_script("try{if(!sessionStorage.getItem('ut')){sessionStorage.setItem('ut','1');localStorage.setItem('crust-lb-name','Bench');localStorage.setItem('crust-q','fast');localStorage.removeItem('crust-own');}}catch(e){}")
        await ctx.route('**/rest/v1/**', lambda r: r.fulfill(status=204, body=''))
        pg = await ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        url = 'http://localhost:8771/webcopy6/index.html'
        await pg.goto(url)
        ready = "!!(document.getElementById('menu')&&!document.getElementById('menu').hidden&&window.__ev)"
        await pg.wait_for_function(ready, timeout=600000, polling=1000)
        ev = lambda js: pg.evaluate("(j)=>__ev(j)", js)
        R = {}
        chrome = "TRIMS.findIndex(t=>t.n==='Chrome')"
        await ev("{const sv=sbSave();sv.c=5;sbKeep();}1")
        R['lockedBefore'] = not await ev(f"styleOwned('tr',{chrome})")
        await ev("applyCheat('unlock');1")
        R['allOpen'] = await ev("['tr','ac','in','gl','hl','sm'].every(sl=>STYLE[sl][1].every((_,i)=>styleOwned(sl,i)))")
        R['buy'] = await ev(f"styleBuy('tr',{chrome})&&styleBuy('gl',GLOWS.length-1)&&styleBuy('sm',SMOKES.length-1)")
        await ev(f"playerBuild.st=Object.assign({{}},playerBuild.st||{{}},{{tr:{chrome},gl:GLOWS.length-1,sm:SMOKES.length-1,hl:1}});store.set('crust-build',JSON.stringify(playerBuild));1")
        R['coins'] = await ev("sbSave().c")
        R['own'] = await ev("store.get('crust-own')")
        await pg.reload()
        await pg.wait_for_function(ready, timeout=600000, polling=1000)
        R['after'] = json.loads(await ev("JSON.stringify({cheat:CHEAT,st:playerBuild.st,locked:!styleOwned('tr',TRIMS.findIndex(t=>t.n==='Chrome'))})"))
        print(json.dumps(R, indent=1))
        a = R['after']
        ok = (R['lockedBefore'] and R['allOpen'] and R['buy'] and R['coins'] == 5 and R['own'] in (None, '[]')
              and not a['cheat'] and a['locked'] and a['st']['tr'] == 0 and a['st']['gl'] == 0 and a['st']['sm'] == 0 and a['st']['hl'] == 1 and not errs)
        print('errors', errs[:4]); print('UNLOCK TEST', 'passed' if ok else 'FAILED')
        await b.close()


asyncio.run(main())
