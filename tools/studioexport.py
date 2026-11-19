"""The garage's workshop room (web v224 patch 81, gStudioSet) for the PC garage: opens the test copy of the web game's garage, waits until
every scanned model of the room has downloaded (gSetFull), runs glbexport.js's __exportStudio and writes assets/garage_studio/studio.glb.
menu.gd _garage_scene loads it round the turntable. Run it again only when gStudioSet changes.
Usage: py.cmd tools/studioexport.py [URL of a built web game, default the local test copy]"""
import asyncio, base64, json, os, sys
from playwright.async_api import async_playwright
URL = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8771/webcopy6/index.html'
EXP = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'glbexport.js'), encoding='utf-8').read()
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets', 'garage_studio')


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(channel='chromium', args=['--use-angle=d3d11', '--enable-gpu', '--ignore-gpu-blocklist', '--enable-webgl'])
        ctx = await b.new_context(viewport={'width': 1280, 'height': 720}, service_workers='block'); pg = await ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await ctx.add_init_script("try{localStorage.setItem('crust-lb-name','Exporter')}catch(e){}")
        await pg.goto(URL)
        await pg.wait_for_function("!!(document.getElementById('menu')&&!document.getElementById('menu').hidden&&window.__ev)", timeout=600000, polling=1000)
        await pg.evaluate("__ev(`qKey='ultra';applyQuality();openGarage();1`)")
        for i in range(300):
            if await pg.evaluate("__ev(`(()=>{try{gStudioMake();}catch(e){}return gSetFull;})()`)"): break
            await pg.wait_for_timeout(1000)
        await pg.evaluate("src=>__ev(src)", EXP)
        d = json.loads(await pg.evaluate("__ev(`JSON.stringify(__exportStudio())`)"))
        if d.get('err'): print('STUDIOEXPORT FAIL', d['err'], errs[:3]); await b.close(); return
        os.makedirs(OUT, exist_ok=True)
        open(os.path.join(OUT, 'studio.glb'), 'wb').write(base64.b64decode(d.pop('b64')))
        print('STUDIOEXPORT done', json.dumps(d)[:600], errs[:3])
        await b.close()
asyncio.run(main())
