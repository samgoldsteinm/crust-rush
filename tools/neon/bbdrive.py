import asyncio, json, sys, os
from playwright.async_api import async_playwright
# usage: bbdrive.py   a Balloon Battle driven by key presses (not the self-driving player the other tests use), in real time:
# steer left and right, use items, drive at a wall. Prints where the kart went and what it did; pictures scratch/bbdrive_<n>.png
SP = 'D:/crust-rush/scratch'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(channel='chromium', args=['--use-angle=d3d11','--enable-gpu','--ignore-gpu-blocklist','--enable-webgl'])
        ctx = await b.new_context(viewport={'width':1280,'height':720}, service_workers='block'); pg = await ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:400]))
        await pg.goto('http://localhost:8771/webcopy6/index.html')
        await pg.wait_for_function("document.getElementById('menu')&&!document.getElementById('menu').hidden", timeout=600000)
        for nm in ('bbtable', 'bbbins', 'bbboxes', 'bbblock', 'bbprops'):
            await pg.wait_for_function("(n)=>__ev(`TM.pkReady('${n}')`)", arg=nm, timeout=600000)
        await pg.evaluate("__ev(`qKey='ultra';applyQuality();mode='bb';introSkip=true;goRace(MAPS.findIndex(m=>m.battle))`)")
        await pg.wait_for_function("document.getElementById('raceLd').hidden", timeout=900000)
        for i in range(400):
            if await pg.evaluate("__ev(`state`)") == 'race': break
            await pg.wait_for_timeout(500)
        snap = "__ev(`JSON.stringify({x:Math.round(player.x),z:Math.round(player.y),h:Math.round(player.wy||0),sp:Math.round(player.speed),item:player.item,bal:player.bal,sc:player.bbS,auto:player.auto,t:Math.round(BB.t),proj:projectiles.length})`)"
        log = []
        async def step(label, keys, ms, shot=None):
            for k in keys: await pg.keyboard.down(k)
            await pg.wait_for_timeout(ms)
            for k in keys: await pg.keyboard.up(k)
            log.append((label, json.loads(await pg.evaluate(snap))))
            if shot is not None: await pg.screenshot(path=f'{SP}/bbdrive_{shot}.png')
        await step('start', [], 300, 0)
        await step('straight 2 s', [], 2000)
        await step('left 1.2 s', ['ArrowLeft'], 1200, 1)
        await step('straight 1.5 s', [], 1500)
        await step('right 1.5 s', ['ArrowRight'], 1500, 2)
        for i in range(10):
            await step(f'cruise {i}', ['ArrowLeft'] if i % 3 == 0 else [], 1500)
            it = log[-1][1]['item']
            if it:
                await pg.keyboard.press('KeyX'); await pg.wait_for_timeout(400); log.append(('used ' + it, json.loads(await pg.evaluate(snap))))
        await pg.screenshot(path=f'{SP}/bbdrive_3.png')
        for l in log: print(l)
        print('errors', errs[:6])
        await b.close()
asyncio.run(main())
