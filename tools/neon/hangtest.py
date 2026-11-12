import asyncio, sys, glob
from playwright.async_api import async_playwright
MAP = sys.argv[1]
SP='/tmp/claude-0/-home-claude/009aa3b6-e96f-505b-b230-9e07dd3a3292/scratchpad'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width':480,'height':270}, service_workers='block')
        pg = await ctx.new_page()
        await pg.goto('http://localhost:8771/webcopy6/index.html')
        await pg.wait_for_function("document.getElementById('menu')&&!document.getElementById('menu').hidden", timeout=600000)
        cdp = await ctx.new_cdp_session(pg)
        await cdp.send('Debugger.enable')
        got = asyncio.get_event_loop().create_future()
        cdp.on('Debugger.paused', lambda ev: (not got.done()) and got.set_result(ev))
        asyncio.ensure_future(pg.evaluate("(a)=>__ev(`qKey='fast';applyQuality();clsKey='medium';mode='single';introSkip=true;goRace(MAPS.findIndex(m=>m.id==='${a}'))`)", MAP))
        await asyncio.sleep(45)
        await cdp.send('Debugger.pause')
        ev = await asyncio.wait_for(got, 30)
        src = open(glob.glob(SP+'/webcopy6/js/game.*.js')[0], encoding='utf-8').read().split('\n')
        for f in ev['callFrames'][:6]:
            l, c = f['location']['lineNumber'], f['location']['columnNumber']
            print(f['functionName'], l, c, '::', src[l][max(0, c-90):c+110].replace('\n', ' '))
        await b.close()
asyncio.run(main())
