"""The mechanic's shop of Sandbox (web v205 patch 41) for the PC: starts the test copy of the web game in Sandbox in the garage (where the
shop stands), waits for the shop's Blender packs, runs glbexport.js's __exportShop and writes assets/shop/mshop.glb (two nodes: "shop",
the building; "door", the roll-up door at its hinge) and assets/shop/mshop.json (the numbers: K, the floor, the bay, the door's place).
Usage: py.cmd tools/shopexport.py [URL of a built web game, default the local test copy]"""
import asyncio, base64, json, os, sys
from playwright.async_api import async_playwright
URL = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8771/webcopy6/index.html'
EXP = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'glbexport.js'), encoding='utf-8').read()
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets', 'shop')


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(channel='chromium', args=['--use-angle=d3d11', '--enable-gpu', '--ignore-gpu-blocklist', '--enable-webgl'])
        ctx = await b.new_context(viewport={'width': 1280, 'height': 720}, service_workers='block'); pg = await ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await ctx.add_init_script("try{localStorage.setItem('crust-lb-name','Exporter')}catch(e){}")
        await pg.goto(URL)
        await pg.wait_for_function("!!(document.getElementById('menu')&&!document.getElementById('menu').hidden&&window.__ev)", timeout=600000, polling=1000)
        await pg.evaluate("__ev(`qKey='ultra';applyQuality();clsKey='medium';introSkip=true;document.querySelector('#modeSeg button[data-m=sb]').click();`)")
        await pg.wait_for_timeout(1500)
        await pg.evaluate("__ev(`{const i=MAPS.findIndex(m=>m.id==='garage');mapIdx=i;loadMap(i,false);resetRace(true);goRace(i);}`)")
        for i in range(600):
            if await pg.evaluate("__ev(`state==='race'&&!!SB.shopG&&SB.shopPk!==false&&!!SB.shopDoorG`)"): break
            if i % 20 == 0: await pg.evaluate("__ev(`try{sbShopBuild();}catch(e){}1`)")
            await pg.wait_for_timeout(1000)
        await pg.evaluate("src=>__ev(src)", EXP)
        r = await pg.evaluate("__ev(`JSON.stringify(__exportShop())`)")
        d = json.loads(r)
        if d.get('err'): print('SHOPEXPORT FAIL', d['err'], errs[:3]); await b.close(); return
        os.makedirs(OUT, exist_ok=True)
        open(os.path.join(OUT, 'mshop.glb'), 'wb').write(base64.b64decode(d.pop('b64')))
        json.dump(d, open(os.path.join(OUT, 'mshop.json'), 'w'), indent=1)
        print('SHOPEXPORT done', json.dumps(d)[:600], errs[:3])
        await b.close()
asyncio.run(main())
