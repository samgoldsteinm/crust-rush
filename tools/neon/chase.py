import asyncio, json, sys, os
from playwright.async_api import async_playwright
# usage: chase.py <map> <tag> "idx,idx,..."  -> the game's own chase camera with the (self-driving) player at each point of the lap
MAP, TAG, IDX = sys.argv[1], sys.argv[2], [int(v) for v in sys.argv[3].split(',')]
SP='D:/crust-rush/scratch'
BODYJS = ("playerBuild.b=BODIES.findIndex(b=>b.id==='%s');playerBuild.t='';" % os.environ['BODY']) if os.environ.get('BODY') else ''   # BODY=<body id>: the player's body
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(channel='chromium', args=['--use-angle=d3d11','--enable-gpu','--ignore-gpu-blocklist','--enable-webgl'])
        ctx = await b.new_context(viewport={'width':960,'height':540}, service_workers='block')
        pg = await ctx.new_page(); errs=[]
        pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto('http://localhost:8771/webcopy6/index.html')
        await pg.wait_for_function("document.getElementById('menu')&&!document.getElementById('menu').hidden", timeout=600000)
        await pg.evaluate("(a)=>__ev(`qKey='" + os.environ.get('Q', 'fast') + "';applyQuality();clsKey='medium';mode='single';introSkip=true;" + BODYJS + "goRace(MAPS.findIndex(m=>m.id==='${a[0]}'))`)", [MAP])
        await pg.wait_for_function("document.getElementById('raceLd').hidden", timeout=900000)
        for i in range(400):
            if await pg.evaluate("__ev(`state`)")=='race': break
            await pg.wait_for_timeout(500)
        await pg.evaluate("__ev(`player.auto=true;window.__to=(j)=>{let n=0;while(n<60000&&!(player.idx>=j&&player.idx<j+12)){update(STEP);n++;}return JSON.stringify([player.idx,Math.round(player.wy),Math.round(player.speed),n]);};1`)")
        for i, j in enumerate(IDX):
            print(j, await pg.evaluate("(j)=>__ev(`__to(${j})`)", j), flush=True)
            await pg.wait_for_timeout(6000)
            await pg.screenshot(path=f'{SP}/chase_{TAG}_{i}.png', timeout=900000)
        print('errors', errs[:4])
        await b.close()
asyncio.run(main())
