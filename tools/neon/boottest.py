import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(channel='chromium', args=['--use-angle=d3d11','--enable-gpu','--ignore-gpu-blocklist','--enable-webgl'])
        ctx = await b.new_context(viewport={'width':480,'height':270}, service_workers='block')
        pg = await ctx.new_page()
        errs=[]
        pg.on('pageerror', lambda e: errs.append(str(e)[:600]))
        pg.on('console', lambda m: errs.append('console:'+m.text[:300]) if m.type=='error' and 'Failed to load' not in m.text else None)
        await pg.goto('http://localhost:8771/webcopy6/index.html')
        for i in range(60):
            await pg.wait_for_timeout(1000)
            ok = await pg.evaluate("!!(document.getElementById('menu')&&!document.getElementById('menu').hidden)")
            if ok or errs: break
        print('menu', ok, 'errors', errs[:4])
        await b.close()
asyncio.run(main())
