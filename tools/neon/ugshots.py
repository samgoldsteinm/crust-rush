"""Underglow styles side by side (web patch 71):   py.cmd tools/neon/ugshots.py [variants, default 0,1,2,3,4]   (webtest.py must be serving)
Basil's scissor car, orange, ice-blue underglow: the garage as it opens, and in a race behind the kart.
Pictures scratch/ug/web_garage_<v>.png and scratch/ug/web_race_<v>.png."""
import asyncio, os, sys
from playwright.async_api import async_playwright
SP = 'D:/crust-rush/scratch/ug'
VS = [int(v) for v in (sys.argv[1] if len(sys.argv) > 1 else '0,1,2,3,4').split(',')]
MAP = os.environ.get('MAP', 'frosty')


async def main():
    os.makedirs(SP, exist_ok=True)
    async with async_playwright() as p:
        b = await p.chromium.launch(channel='chromium', args=['--use-angle=d3d11', '--enable-gpu', '--ignore-gpu-blocklist', '--enable-webgl'])
        ctx = await b.new_context(viewport={'width': 1280, 'height': 590}, service_workers='block')
        await ctx.add_init_script("try{localStorage.setItem('crust-lb-name','Bench');}catch(e){}")
        await ctx.route('**/rest/v1/**', lambda r: r.fulfill(status=204, body=''))
        pg = await ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto('http://localhost:8771/webcopy6/index.html')
        await pg.wait_for_function("!!(document.getElementById('menu')&&!document.getElementById('menu').hidden&&window.__ev)", timeout=600000, polling=1000)
        ev = lambda js: pg.evaluate("(j)=>__ev(j)", js)
        await ev("qKey='ultra';applyQuality();1"); await pg.wait_for_timeout(6000)
        await pg.evaluate("()=>{for(const b of document.querySelectorAll('button'))if(/^not now$/i.test(b.textContent.trim())&&b.offsetParent)b.click();}")
        setup = "const i=BODIES.findIndex(b=>b.id==='scissor');playerBuild.b=i;playerBuild.w=0;playerBuild.p=2;playerBuild.t='';playerBuild.st={gl:1};"
        for v in VS:
            await ev(f"UGV={v};{setup}if(!garageOpen)openGarage();else refreshGarage(true);setBig(false);gRot=1.0;1")
            await pg.wait_for_timeout(2000)
            await ev("gRot=1.0;1"); await pg.wait_for_timeout(120)
            await pg.screenshot(path=f'{SP}/web_garage_{v}.png')
        await ev("closeGarage&&closeGarage();1"); await pg.wait_for_timeout(800)
        for v in VS:
            await ev(f"UGV={v};{setup}introSkip=true;mode='single';CPUS=3;clsKey='medium';mapIdx=MAPS.findIndex(q=>q.id==='{MAP}');goRace(mapIdx);1")
            for i in range(240):
                if await ev("state==='race'"): break
                await pg.wait_for_timeout(500)
            print(v, await ev("MAPS[mapIdx].id"))
            await ev("player.auto=true;1")
            await pg.wait_for_timeout(3500)
            await pg.screenshot(path=f'{SP}/web_race{os.environ.get("PRE","")}_{v}.png')
            await ev("toMenu();1"); await pg.wait_for_timeout(1500)
        print('errors', errs[:4])
        await b.close()


asyncio.run(main())
