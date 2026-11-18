"""A race with a cheat on does not count towards records (web patch 79):   py.cmd tools/neon/cheattest.py   (webtest.py serving)
One single race on Margherita; for each case the race's start is replayed (ghostStart, as a restart does), the setting is put on, the
game runs a second, then the finish is saved (saveRun). Counted: a personal best is written and a world leaderboard run is queued.
Cases: nothing on (counts), UNLOCK (counts), developer options on but only the field of view / HUD changed (counts), a race setting
(top speed x1.5: not counted), a device setting (invincible: not counted), auto-drive (TESTING: not counted), a setting turned on
mid-race and off again before the finish (not counted). Prints CHEAT TEST passed / FAILED."""
import asyncio, json
from playwright.async_api import async_playwright
CASES = [('clean', '', True), ('unlock', "CHEAT=true;", True), ('looks', "DEVU=true;DEV.on=1;DEV.fov=80;DEV.hud=0;", True),
         ('speed', "DEVU=true;DEV.on=1;DEV.spd=1.5;", False), ('invincible', "DEVU=true;DEV.on=1;DEV.inv=1;", False),
         ('autodrive', "TD.on=true;", False), ('midrace', "DEVU=true;DEV.on=1;DEV.grav=.5;", False)]
OFF = "CHEAT=false;TD.on=false;DEVU=false;Object.assign(DEV,JSON.parse(JSON.stringify(DEVDEF)));"


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(channel='chromium', args=['--use-angle=d3d11', '--enable-gpu', '--ignore-gpu-blocklist', '--enable-webgl'])
        ctx = await b.new_context(viewport={'width': 1280, 'height': 720}, service_workers='block')
        await ctx.route('**/rest/v1/**', lambda r: r.fulfill(status=204, body=''))
        pg = await ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto('http://localhost:8771/webcopy6/index.html')
        await pg.wait_for_function("document.getElementById('menu')&&!document.getElementById('menu').hidden", timeout=600000)
        ev = lambda js: pg.evaluate("(j)=>__ev(j)", js)
        await ev("introSkip=true;mode='single';CPUS=3;clsKey='medium';mapIdx=MAPS.findIndex(m=>m.id==='margherita');goRace(mapIdx);1")
        for i in range(600):
            if await ev("state") == 'race': break
            await pg.wait_for_timeout(500)
        res, ok = {}, True
        for name, js, want in CASES:
            await ev(OFF + "store.set('crust-recs','{}');store.set('crust-lb-q','[]');ghostStart();" + (js if name != 'midrace' else '') + "1")
            if name == 'midrace':
                await pg.wait_for_timeout(500); await ev(js + "1"); await pg.wait_for_timeout(500); await ev(OFF + "1")
            await pg.wait_for_timeout(1000)
            r = await ev(OFF + "(()=>{player.finished=true;player.finishTime=61.5;player.place=1;saveRun();"
                         "return {rec:Object.keys(loadRecs()).length,lb:lbQueue().length,cheat:!!(lastRun&&lastRun.cheat),line:pbLine().replace(/<[^>]+>/g,'')};})()")
            player_reset = await ev("player.finished=false;player.finishTime=0;1")
            counted = r['rec'] == 1 and r['lb'] == 1
            good = counted == want and r['cheat'] == (not want)
            ok &= good; res[name] = r
            print(f"{name:11s} counted {counted} (want {want}) {'ok' if good else 'WRONG'}: {r['line']}")
        print('CHEAT TEST', 'passed' if ok and not errs else 'FAILED', 'errors', errs[:4])
        await b.close()

asyncio.run(main())
