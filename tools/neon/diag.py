import asyncio, json, sys
from playwright.async_api import async_playwright
# usage: diag.py <map> <cls> <js expression evaluated inside the game after the race starts>
MAP, CLS, JS = sys.argv[1], sys.argv[2], sys.argv[3]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(channel='chromium', args=['--use-angle=d3d11','--enable-gpu','--ignore-gpu-blocklist','--enable-webgl'])
        ctx = await b.new_context(viewport={'width':480,'height':270}, service_workers='block')
        pg = await ctx.new_page()
        errs=[]
        pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        pg.on('console', lambda m: errs.append('console:'+m.text[:300]) if m.type in ('error','warning') and 'neon' in m.text else None)
        await pg.goto('http://localhost:8771/webcopy6/index.html')
        await pg.wait_for_function("document.getElementById('menu')&&!document.getElementById('menu').hidden", timeout=600000)
        await pg.evaluate("(a)=>__ev(`qKey='fast';applyQuality();clsKey='${a[1]}';mode='single';introSkip=true;goRace(MAPS.findIndex(m=>m.id==='${a[0]}'))`)", [MAP, CLS])
        await pg.wait_for_function("document.getElementById('raceLd').hidden", timeout=900000)
        for i in range(400):
            st = await pg.evaluate("__ev(`state`)")
            if st=='race': break
            await pg.wait_for_timeout(500)
        r = await pg.evaluate("(js)=>__ev(js)", JS)
        print(r)
        print('errors', errs[:8])
        await b.close()
asyncio.run(main())
