import asyncio, json, sys, os
from playwright.async_api import async_playwright
# usage: probe.py <map> <seconds> "<js: a number for kart k, or null to skip>"   e.g. "k.x>130&&k.x<470&&k.y<-681&&k.y>-771?k.wy:null"
# a race with the player driving itself, fast-forwarded; prints the least and the greatest value the expression took
MAP, SECS = sys.argv[1], int(sys.argv[2]); EXPR = os.environ.get("EXPR") or sys.argv[3]   # (py.cmd is a batch file: an expression with < > & in it must come in the EXPR variable)
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(channel='chromium', args=['--use-angle=d3d11','--enable-gpu','--ignore-gpu-blocklist','--enable-webgl'])
        ctx = await b.new_context(viewport={'width':640,'height':360}, service_workers='block'); pg = await ctx.new_page()
        await pg.goto('http://localhost:8771/webcopy6/index.html')
        await pg.wait_for_function("document.getElementById('menu')&&!document.getElementById('menu').hidden", timeout=600000)
        await pg.evaluate("(m)=>__ev(`qKey='fast';applyQuality();clsKey='medium';mode='single';introSkip=true;goRace(MAPS.findIndex(q=>q.id==='${m}'))`)", MAP)
        await pg.wait_for_function("document.getElementById('raceLd').hidden", timeout=900000)
        for i in range(400):
            if await pg.evaluate("__ev(`state`)") == 'race': break
            await pg.wait_for_timeout(500)
        await pg.evaluate("(e)=>__ev(`player.auto=true;window.__pr={lo:1e9,hi:-1e9,n:0};window.__ff=(sec)=>{const n=Math.round(sec/STEP);for(let i=0;i<n;i++){update(STEP);for(const k of karts){const v=(${e});if(v!=null){__pr.n++;if(v<__pr.lo)__pr.lo=v;if(v>__pr.hi)__pr.hi=v;}}}return JSON.stringify(__pr);};1`)", EXPR)
        r = {}
        for i in range(SECS // 10): r = json.loads(await pg.evaluate("__ev(`__ff(10)`)"))
        print('probe', MAP, EXPR, '->', r)
        await b.close()
asyncio.run(main())
