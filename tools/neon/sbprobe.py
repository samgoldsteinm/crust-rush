"""Sandbox, a look at anything:   py.cmd tools/neon/sbprobe.py <map> <file.js> [shots]
Starts Sandbox on <map> (Fast quality), then runs each block of <file.js> in the game and prints what it returns. Blocks are separated by a
line holding only ----; each is one expression (wrap statements as (()=>{...})()). A block that starts with //shot <name> takes a picture
scratch/probe_<name>.png one second after it ran; //wait <ms> waits first. The helper window.__sb (put, line, lap: see sbtest.py) is loaded."""
import asyncio, json, re, sys
from playwright.async_api import async_playwright
REG = sys.argv[1]; SRC = open(sys.argv[2], encoding='utf-8').read(); SP = 'D:/crust-rush/scratch'
HELP = re.search(r'JS = r"""(.*?)"""', open('D:/crust-rush/source/tools/neon/sbtest.py', encoding='utf-8').read(), re.S)
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(channel='chromium', args=['--use-angle=d3d11', '--enable-gpu', '--ignore-gpu-blocklist', '--enable-webgl'])
        ctx = await b.new_context(viewport={'width': 1280, 'height': 720}, service_workers='block'); pg = await ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:300])); pg.on('console', lambda m: errs.append('console: ' + m.text[:200]) if m.type == 'error' else None)
        await pg.goto('http://localhost:8771/webcopy6/index.html')
        await pg.wait_for_function("document.getElementById('menu')&&!document.getElementById('menu').hidden", timeout=600000)
        q = sys.argv[3] if len(sys.argv) > 3 else 'fast'
        await pg.evaluate("__ev(`qKey='" + q + "';applyQuality();clsKey='medium';introSkip=true;document.querySelector('#modeSeg button[data-m=sb]').click();`)")
        await pg.wait_for_timeout(1500); await pg.evaluate("(a)=>{__ev(`{const i=MAPS.findIndex(m=>m.id==='" + REG + "');mapIdx=i;loadMap(i,false);resetRace(true);}`)}", REG); await pg.wait_for_timeout(2500)
        await pg.evaluate("__ev(`goRace(mapIdx)`)")
        await pg.wait_for_function("document.getElementById('raceLd').hidden", timeout=900000)
        for i in range(400):
            if await pg.evaluate("__ev(`state`)") == 'race': break
            await pg.wait_for_timeout(500)
        if HELP: await pg.evaluate("(js)=>__ev(js)", HELP.group(1))
        for blk in re.split(r'^----\s*$', SRC, flags=re.M):
            blk = blk.strip()
            if not blk: continue
            shot = None
            while True:
                m = re.match(r'//shot (\S+)\s*', blk)
                if m: shot = m.group(1); blk = blk[m.end():]; continue
                m = re.match(r'//wait (\d+)\s*', blk)
                if m: await pg.wait_for_timeout(int(m.group(1))); blk = blk[m.end():]; continue
                break
            if blk:
                try: r = await pg.evaluate("(js)=>__ev('JSON.stringify('+js+')')", blk)
                except Exception as e: r = 'ERROR ' + str(e)[:400]
                print(str(r)[:3000], flush=True)
            if shot: await pg.wait_for_timeout(1000); await pg.screenshot(path=f'{SP}/probe_{shot}.png')
        pl = await pg.evaluate("__ev(`window.__plan||null`)")
        if pl: open(f"{SP}/probe_plan_{REG}.png", "wb").write(__import__("base64").b64decode(pl.split(",")[1]))
        print("errors", errs[:6]); await b.close()
asyncio.run(main())
