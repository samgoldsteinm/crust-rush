import asyncio, sys
from playwright.async_api import async_playwright
SP='/tmp/claude-0/-home-claude/009aa3b6-e96f-505b-b230-9e07dd3a3292/scratchpad'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        for nm, vw, vh in [('phone', 956, 440), ('desk', 1280, 720)]:
            ctx = await b.new_context(viewport={'width':vw,'height':vh}, service_workers='block', has_touch=(nm=='phone'))
            pg = await ctx.new_page()
            await pg.goto('http://localhost:8771/webcopy6/index.html')
            await pg.wait_for_function("document.getElementById('menu')&&!document.getElementById('menu').hidden", timeout=600000)
            await pg.evaluate("__ev(`qKey='fast';applyQuality();mode='gp';cupIdx=4;goStep('track')`)")
            await pg.wait_for_timeout(2500)
            await pg.screenshot(path=f'{SP}/menu_{nm}_gp.png')
            await pg.evaluate("__ev(`mode='single';mapIdx=20;mapCat='sp';goStep('track')`)")
            await pg.wait_for_timeout(2500)
            await pg.screenshot(path=f'{SP}/menu_{nm}_single.png')
            await ctx.close()
        await b.close()
asyncio.run(main())
