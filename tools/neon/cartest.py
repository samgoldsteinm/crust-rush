import asyncio, sys
from playwright.async_api import async_playwright
# usage: cartest.py <tag> <body id> [<body id> ...]  -> each body in the garage's inspect view, front-quarter and rear-quarter,
# as scratch/car_<tag>_<id>_<0|1>.png (webtest.py must be serving). Set PAINT=<index> for a paint, LIV=<livery id> for a livery.
import os
TAG, IDS = sys.argv[1], sys.argv[2:]
SP = 'D:/crust-rush/scratch'; PAINT = os.environ.get('PAINT', ''); LIV = os.environ.get('LIV', '')
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(channel='chromium', args=['--use-angle=d3d11', '--enable-gpu', '--ignore-gpu-blocklist', '--enable-webgl'])
        ctx = await b.new_context(viewport={'width': 1280, 'height': 720}, service_workers='block')
        pg = await ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto('http://localhost:8771/webcopy6/index.html')
        await pg.wait_for_function("document.getElementById('menu')&&!document.getElementById('menu').hidden", timeout=600000)
        await pg.evaluate("__ev(`qKey='" + os.environ.get('Q', 'ultra') + "';applyQuality();1`)")
        await pg.wait_for_timeout(6000)                                # the late high-quality packs
        for cid in IDS:
            r = await pg.evaluate("(a)=>__ev(`(()=>{const i=BODIES.findIndex(b=>b.id==='${a[0]}');if(i<0)return 'no such body';playerBuild.b=i;playerBuild.w=0;" +
                                  "if('${a[1]}')playerBuild.p=+'${a[1]}';playerBuild.t='${a[2]}';" +
                                  "if(!garageOpen)openGarage();else refreshGarage(true);setBig(true);return BODIES[i].name+' hq:'+hqReady('${a[0]}');})()`)", [cid, PAINT, LIV])
            print(cid, r, flush=True)
            for k, rot in enumerate([float(v) for v in os.environ.get('ROT', '1.35,4.5').split(',')]):
                await pg.evaluate("(r)=>__ev(`gRot=${r};gZoom=" + os.environ.get('ZOOM', '.42') + ";gPitch=" + os.environ.get('PITCH', '.12') + ";1`)", rot)
                await pg.wait_for_timeout(700)
                await pg.evaluate("(r)=>__ev(`gRot=${r};1`)", rot)
                await pg.wait_for_timeout(150)
                await pg.screenshot(path=f'{SP}/car_{TAG}_{cid}_{k}.png')
        print('errors', errs[:4])
        await b.close()
asyncio.run(main())
