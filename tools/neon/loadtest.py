import asyncio, sys
from playwright.async_api import async_playwright
MAP = sys.argv[1]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(channel='chromium', args=['--use-angle=d3d11','--enable-gpu','--ignore-gpu-blocklist','--enable-webgl'])
        ctx = await b.new_context(viewport={'width':480,'height':270}, service_workers='block')
        pg = await ctx.new_page()
        errs=[]
        pg.on('pageerror', lambda e: errs.append((getattr(e,'stack',None) or str(e))[:700]))
        pg.on('console', lambda m: errs.append('console:'+m.text[:400]) if m.type in ('error','warning') and 'GPU' not in m.text and 'WebGL' not in m.text and 'Canvas2D' not in m.text and 'Failed to load' not in m.text else None)
        await pg.goto('http://localhost:8771/webcopy6/index.html')
        await pg.wait_for_function("document.getElementById('menu')&&!document.getElementById('menu').hidden", timeout=600000)
        await pg.evaluate("(a)=>__ev(`qKey='fast';applyQuality();clsKey='medium';mode='single';introSkip=true;goRace(MAPS.findIndex(m=>m.id==='${a}'))`)", MAP)
        for i in range(90):
            await pg.wait_for_timeout(1000)
            st = await pg.evaluate("__ev(`state`)")
            if st in ('race','countdown','intro') or errs: break
        print('state', st); print('errors', errs[:6])
        await b.close()
asyncio.run(main())
