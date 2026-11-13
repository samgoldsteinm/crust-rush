import asyncio, json, sys, os
from playwright.async_api import async_playwright
# usage: bbtest.py [seconds] [shots]   a Balloon Battle with the player driving itself, fast-forwarded: a summary every 20 s,
# then pictures (scratch/bb_<n>.png: the chase camera, and two looks down at the table) if `shots` is given
SECS = int(sys.argv[1]) if len(sys.argv) > 1 else 185
SP = 'D:/crust-rush/scratch'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(channel='chromium', args=['--use-angle=d3d11','--enable-gpu','--ignore-gpu-blocklist','--enable-webgl'])
        ctx = await b.new_context(viewport={'width':1280,'height':720}, service_workers='block'); pg = await ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:400]))
        pg.on('console', lambda m: errs.append('console:'+m.text[:300]) if m.type == 'error' and 'GPU' not in m.text and 'WebGL' not in m.text else None)
        await pg.goto('http://localhost:8771/webcopy6/index.html')
        await pg.wait_for_function("document.getElementById('menu')&&!document.getElementById('menu').hidden", timeout=600000)
        if len(sys.argv) > 2:                                # the menu with the mode chosen, as a player gets there
            await pg.click('#modeSeg button[data-m="bb"]'); await pg.wait_for_timeout(2500); await pg.screenshot(path=f'{SP}/bb_menu.png')
        await pg.evaluate("(q)=>__ev(`qKey='${q}';applyQuality();mode='bb';introSkip=true;goRace(MAPS.findIndex(m=>m.battle))`)", os.environ.get('Q', 'ultra'))
        await pg.wait_for_function("document.getElementById('raceLd').hidden", timeout=900000)
        for i in range(400):
            if await pg.evaluate("__ev(`state`)") == 'race': break
            await pg.wait_for_timeout(500)
        print('battle', await pg.evaluate("__ev(`JSON.stringify({BATTLE,shapes:BB.shapes.length,boxes:boxes.length,karts:karts.length,N,RIM:Math.round(RIM)})`)"), flush=True)
        await pg.evaluate("""__ev(`player.auto=true;window.__bb={stuck:karts.map(()=>0),maxStuck:0,out:0,nan:0,esc:0};window.__lastp=karts.map(k=>[k.x,k.y]);
          window.__ff=(sec)=>{const n=Math.round(sec/STEP);for(let i=0;i<n;i++){update(STEP);if(i%120===0)karts.forEach((k,ki)=>{const l=__lastp[ki],d=Math.hypot(k.x-l[0],k.y-l[1]);__lastp[ki]=[k.x,k.y];if(d<6&&!(k.bbOut>0))__bb.stuck[ki]++;else __bb.stuck[ki]=0;__bb.maxStuck=Math.max(__bb.maxStuck,__bb.stuck[ki]);
              if(!isFinite(k.x)||!isFinite(k.y)||!isFinite(k.wy))__bb.nan++;if(Math.abs(k.x)>384||Math.abs(k.y)>264)__bb.esc++;});}
            return JSON.stringify({t:Math.round(BB.t),state,over:BB.over,sc:karts.map(k=>k.bbS||0),bal:karts.map(k=>k.bal||0),items:karts.filter(k=>k.item).length,proj:projectiles.length,haz:hazards.length,lv:karts.map(k=>Math.round(k.wy||0)),bb:__bb});};1`)""")
        if len(sys.argv) > 2:
            for i in range(3):
                await pg.evaluate("__ev(`__ff(6)`)"); await pg.wait_for_timeout(1500); await pg.screenshot(path=f'{SP}/bb_{i}.png')
            await pg.evaluate("""__ev(`cd=1e6;window.__cam=null;const R0=renderer.render.bind(renderer);renderer.render=(s,c)=>{if(c===camera&&window.__cam){const q=window.__cam;camera.position.set(q[0],q[1],q[2]);camera.lookAt(q[3],q[4],q[5]);camera.updateMatrixWorld(true);}R0(s,c);};1`)""")
            for i, c in enumerate(('0,620,560,0,0,20', '-520,260,420,60,20,-40', '480,120,-380,-60,30,60')):
                await pg.evaluate("(c)=>__ev(`window.__cam=[${c}];1`)", c); await pg.wait_for_timeout(1500); await pg.screenshot(path=f'{SP}/bb_{3+i}.png')
            await pg.evaluate("__ev(`window.__cam=null;1`)")
        r = {}
        for i in range(SECS // 20):
            r = json.loads(await pg.evaluate("__ev(`__ff(20)`)")); print(r, flush=True)
            if r['over']: break
        if len(sys.argv) > 2: await pg.wait_for_timeout(5000); await pg.screenshot(path=f'{SP}/bb_res.png')   # the results
        print('errors', errs[:8])
        await b.close()
asyncio.run(main())
