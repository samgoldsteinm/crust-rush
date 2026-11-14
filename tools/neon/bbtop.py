import asyncio, json
from playwright.async_api import async_playwright
# Balloon Battle: the player's kart placed on top of the boxes, on the block, on each ramp and by the east ramp's foot; chase-camera pictures
SP = 'D:/crust-rush/scratch'
SPOTS = [('boxes', 0, 195, 0), ('boxes_edge', 0, 140, 3.14), ('block', 306, 100, -1.57), ('lid_ramp', -275, 195, 0), ('bread_ramp', 306, -115, 1.57), ('ramp_foot', 306, -215, 1.57), ('table', -100, -60, .6)]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(channel='chromium', args=['--use-angle=d3d11','--enable-gpu','--ignore-gpu-blocklist','--enable-webgl'])
        ctx = await b.new_context(viewport={'width':1280,'height':720}, service_workers='block'); pg = await ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto('http://localhost:8771/webcopy6/index.html')
        await pg.wait_for_function("document.getElementById('menu')&&!document.getElementById('menu').hidden", timeout=600000)
        for nm in ('bbtable', 'bbbins', 'bbboxes', 'bbblock', 'bbprops'):
            await pg.wait_for_function("(n)=>__ev(`TM.pkReady('${n}')`)", arg=nm, timeout=600000)
        await pg.evaluate("__ev(`qKey='ultra';applyQuality();mode='bb';introSkip=true;goRace(MAPS.findIndex(m=>m.battle))`)")
        await pg.wait_for_function("document.getElementById('raceLd').hidden", timeout=900000)
        for i in range(400):
            if await pg.evaluate("__ev(`state`)") == 'race': break
            await pg.wait_for_timeout(500)
        for n, (name, x, z, a) in enumerate(SPOTS):
            await pg.evaluate("(q)=>__ev(`(()=>{const k=player;k.x=k.px=${q[0]};k.y=k.py=${q[1]};k.a=k.ma=k.pa=k.pma=${q[2]};k.speed=0;k.wy=k.pwy=k.lastG=battleG(k.x,k.y);k.wvy=0;k.air=false;k.bpx=k.x;k.bpy=k.y;k.inv=99;camSnap=true;cam.a=k.ma;BB.camF=1;state='countdown';cd=1e9;})()`)", [x, z, a])
            await pg.wait_for_timeout(1300)
            r = json.loads(await pg.evaluate("__ev(`JSON.stringify({kartY:+player.m.g.position.y.toFixed(1),ground:battleG(player.x,player.y),camY:Math.round(camera.position.y),camAbove:Math.round(camera.position.y-battleG(camera.position.x,camera.position.z)),tilt:[+player.m.g.rotation.x.toFixed(2),+player.m.g.rotation.z.toFixed(2)]})`)"))
            print(name, r, flush=True)
            await pg.screenshot(path=f'{SP}/bbtop_{n}.png')
        print('errors', errs[:4]); await b.close()
asyncio.run(main())
