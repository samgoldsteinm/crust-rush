"""Load one map in the web test copy and print every page error and console error (no race needed).
usage: aptload.py <map id>"""
import asyncio, sys
from playwright.async_api import async_playwright
MAP = sys.argv[1] if len(sys.argv) > 1 else 'apartment'


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(channel='chromium', args=['--use-angle=d3d11', '--enable-gpu', '--ignore-gpu-blocklist', '--enable-webgl'])
        ctx = await b.new_context(viewport={'width': 960, 'height': 540}, service_workers='block')
        pg = await ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append('PAGE ' + str(e)[:600] + ' | ' + (e.stack or '')[:600]))
        pg.on('console', lambda m: errs.append('CONSOLE ' + m.text[:400]) if m.type in ('error', 'warning') and 'GPU' not in m.text else None)
        await pg.goto('http://localhost:8771/webcopy6/index.html')
        await pg.wait_for_function("document.getElementById('menu')&&!document.getElementById('menu').hidden", timeout=600000)
        await pg.evaluate("(a)=>__ev(`qKey='fast';applyQuality();clsKey='medium';mode='single';introSkip=true;goRace(MAPS.findIndex(m=>m.id==='${a}'))`)", MAP)
        for i in range(240):
            st = await pg.evaluate("__ev(`state`)")
            if st == 'race' or (errs and i > 20):
                break
            await pg.wait_for_timeout(500)
        print('state', st)
        for e in errs[:12]:
            print(e)
        await b.close()

asyncio.run(main())
