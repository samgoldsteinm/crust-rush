"""Sandbox in the Safari engine set up as an iPhone (touch): py.cmd tools/neon/sbphone.py
Starts Sandbox from the menu as a player would, drives a little, goes through the garden's passage to the kitchen and back, starts the
race at the kitchen's start line and leaves it. Prints how long each step took. Pictures: scratch/sbphone_<n>.png.
Want: every line ok, errors []. (The times are this PC's; a real phone is slower: ask the owner how long the duct lasts for them.)"""
import asyncio, json, time
from playwright.async_api import async_playwright
SP = 'D:/crust-rush/scratch'
async def main():
    async with async_playwright() as p:
        b = await p.webkit.launch()
        ctx = await b.new_context(**{k: v for k, v in p.devices['iPhone 15 Pro landscape'].items() if k != 'default_browser_type'}, service_workers='block')
        pg = await ctx.new_page(); errs = []; bad = 0
        pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        ev = lambda s: pg.evaluate("(js)=>__ev('JSON.stringify('+js+')')", s)
        def say(name, r, ok):
            nonlocal bad; bad += not ok; print(('ok   ' if ok else 'FAIL ') + name, r, flush=True)
        await pg.goto('http://localhost:8771/webcopy6/index.html')
        await pg.wait_for_function("document.getElementById('menu')&&!document.getElementById('menu').hidden", timeout=600000)
        await pg.evaluate("__ev(`qKey='fast';applyQuality();introSkip=true;document.querySelector('#modeSeg button[data-m=sb]').click();`)")
        await pg.wait_for_timeout(2000); await pg.evaluate("document.getElementById('map-backyard').click()"); await pg.wait_for_timeout(2500)
        await pg.screenshot(path=f'{SP}/sbphone_menu.png')
        await pg.evaluate("__ev(`goRace(mapIdx)`)")
        await pg.wait_for_function("document.getElementById('raceLd').hidden", timeout=900000)
        for i in range(400):
            if await pg.evaluate("__ev(`state`)") == 'race': break
            await pg.wait_for_timeout(500)
        await pg.wait_for_timeout(4000); await pg.screenshot(path=f'{SP}/sbphone_0.png')
        r = json.loads(await ev("({sbx:SBX,karts:karts.length,coins:SB.coins.length,columnsMs:SB.col.ms,columnsMB:+(SB.col.sp.byteLength/1e6).toFixed(1),speed:Math.round(player.speed)})"))
        say('starts in the garden', r, r['sbx'] and r['karts'] == 1 and r['coins'] > 100)
        async def through(gid, to, n):
            await ev("(()=>{const g=SB.gates.find(q=>q.id==='" + gid + "'),k=player;k.x=k.px=g.x-g.nx*170;k.y=k.py=g.z-g.nz*170;k.a=k.ma=k.pa=k.pma=Math.atan2(g.nz,g.nx);k.speed=90;k.wy=k.pwy=k.lastG=0;k.wvy=0;k.air=false;k.loop=null;k.bpx=k.x;k.bpy=k.y;k.idx=sbIdx(k,k.idx);camSnap=true;cam.a=k.ma;return 1})()")
            t0 = time.time()
            for i in range(900):
                st = json.loads(await ev("({reg:SB.regId,st:state,trav:!!SB.trav})"))
                if st['reg'] == to and st['st'] == 'race' and not st['trav']: break
                await pg.wait_for_timeout(100)
            secs = round(time.time() - t0, 1); await pg.wait_for_timeout(1500); await pg.screenshot(path=f'{SP}/sbphone_{n}.png')
            r = json.loads(await ev("({region:SB.regId,sbx:SBX,karts:karts.length,state:state,columnsMs:SB.col?SB.col.ms:null})")); r['seconds'] = secs
            say('passage to ' + to, r, r['region'] == to and r['sbx'] and r['state'] == 'race' and secs < 60)
        await through('g_k', 'kitchen', 1); await through('k_g', 'backyard', 2); await through('g_k', 'kitchen', 3)
        await ev("(()=>{const f=SB.flag,k=player;k.x=k.px=f.x;k.y=k.py=f.z;k.wy=k.pwy=k.lastG=f.y;k.bpx=k.x;k.bpy=k.y;k.speed=0;k.idx=sbIdx(k,k.idx);return 1})()"); await pg.wait_for_timeout(800)
        await pg.screenshot(path=f'{SP}/sbphone_4.png')
        r = json.loads(await ev("(()=>{const b=document.getElementById('sbRace');return {offered:!!b&&!b.hidden,says:b?b.textContent:''}})()"))
        say('race offered at the start line', r, r['offered'])
        await pg.evaluate("document.getElementById('sbRace').click()")
        for i in range(300):
            if await pg.evaluate("__ev(`karts.length===8&&(state==='race'||state==='countdown')`)"): break
            await pg.wait_for_timeout(300)
        r = json.loads(await ev("({mode:mode,karts:karts.length,sbx:SBX,state:state})")); say('the race starts', r, r['karts'] == 8 and not r['sbx'])
        await pg.evaluate("__ev(`toMenu()`)")
        for i in range(300):
            if await pg.evaluate("__ev(`state==='race'&&SBX&&karts.length===1`)"): break
            await pg.wait_for_timeout(300)
        r = json.loads(await ev("({mode:mode,karts:karts.length,sbx:SBX,state:state,region:SB.regId})")); say('and back to Sandbox', r, r['sbx'] and r['karts'] == 1 and r['region'] == 'kitchen')
        print('errors', errs[:5]); print('SANDBOX PHONE TEST', 'FAILED' if bad or errs else 'passed'); await b.close()
asyncio.run(main())
