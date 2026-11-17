"""The developer options (web patch 68):   py.cmd tools/neon/devtest.py      (webtest.py must be serving)
The cheat code DEVELOPER shows the section in Settings (picture scratch/dev_settings.png); a vehicle slider changes your kart only, off
line; unlimited pepperoni keeps a pepperoni in hand after each throw; flying climbs with the fly-up key; a hazard switched off is not built
(traffic on Peak District); a room's start sends the host's race settings (cfg.dev). Prints DEV TEST passed / FAILED."""
import asyncio, json
from playwright.async_api import async_playwright
SP = 'D:/crust-rush/scratch'


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(channel='chromium', args=['--use-angle=d3d11', '--enable-gpu', '--ignore-gpu-blocklist', '--enable-webgl'])
        ctx = await b.new_context(viewport={'width': 1280, 'height': 800}, service_workers='block')
        await ctx.add_init_script("try{localStorage.setItem('crust-lb-name','Bench');localStorage.setItem('crust-q','fast');localStorage.removeItem('crust-dev');localStorage.removeItem('crust-dev-on');}catch(e){}")
        await ctx.route('**/rest/v1/**', lambda r: r.fulfill(status=204, body=''))
        pg = await ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto('http://localhost:8771/webcopy6/index.html')
        await pg.wait_for_function("!!(document.getElementById('menu')&&!document.getElementById('menu').hidden&&window.__ev)", timeout=600000, polling=1000)
        ev = lambda js: pg.evaluate("(j)=>__ev(j)", js)
        R = {}
        R['hiddenFirst'] = await ev("$('devSec').hidden")
        await ev("applyCheat('developer');1")
        R['shown'] = await ev("!$('devSec').hidden&&$('devBody').querySelectorAll('input[type=range]').length")
        await ev("openSettings(menu,'more');1"); await pg.wait_for_timeout(800)
        await ev("$('devSec').scrollIntoView();1"); await pg.wait_for_timeout(600)
        await pg.screenshot(path=f'{SP}/dev_settings.png')
        await ev("closeSettings&&closeSettings();1")

        async def race(mapid, setup):
            await ev(setup)
            await ev(f"introSkip=true;mode='single';CPUS=3;clsKey='medium';mapIdx=MAPS.findIndex(q=>q.id==='{mapid}');goRace(mapIdx);1")
            for i in range(240):
                if await ev("state==='race'"): break
                await pg.wait_for_timeout(500)
            await pg.wait_for_timeout(500)

        # a vehicle slider: your kart only
        await race('margherita', "DEV.spd=1.5;DEV.acc=2;devSave();1")
        R['veh'] = json.loads(await ev("JSON.stringify({me:+(player.sm.spd/player.sm0.spd).toFixed(3),acc:+(player.sm.acc/player.sm0.acc).toFixed(3),cpu:+(karts.find(k=>k!==player).sm.spd/(karts.find(k=>k!==player).sm0||karts.find(k=>k!==player).sm).spd).toFixed(3)})"))
        # unlimited pepperoni
        await ev("DEV.infPep=1;devSave();for(let i=0;i<5;i++)update(STEP);1")
        R['pep1'] = await ev("player.item")
        await ev("useItem(player,false);for(let i=0;i<5;i++)update(STEP);1")
        R['pep2'] = await ev("player.item")
        # flying
        await ev("DEV.fly=1;devSave();devFlyToggle();window.__y0=player.wy||0;keys.flyup=true;for(let i=0;i<120;i++)update(STEP);keys.flyup=false;1")
        R['fly'] = json.loads(await ev("JSON.stringify({on:!!player.fly,up:+((player.wy||0)-window.__y0).toFixed(1)})"))
        await ev("toMenu();1"); await pg.wait_for_timeout(1500)
        # a hazard switched off: Peak District's traffic
        await race('peaks', "DEV.fly=0;DEV.infPep=0;DEV.hz.traffic=0;devSave();1")
        R['traffic'] = await ev("HAZ.traffic.length")
        await ev("toMenu();1"); await pg.wait_for_timeout(1500)
        await race('peaks', "DEV.hz.traffic=1;devSave();1")
        R['trafficOn'] = await ev("HAZ.traffic.length")
        # the host's race settings in a room's start
        R['cfg'] = json.loads(await ev("JSON.stringify(netBuildCfg(mapIdx).dev)"))
        R['proto'] = await ev("NET_PROTO")
        print(json.dumps(R, indent=1))
        ok = (R['hiddenFirst'] and R['shown'] and R['veh']['me'] == 1.5 and R['veh']['acc'] == 2 and R['veh']['cpu'] == 1
              and R['pep1'] == 'pepperoni' and R['pep2'] == 'pepperoni' and R['fly']['on'] and R['fly']['up'] > 20
              and R['traffic'] == 0 and R['trafficOn'] > 0 and R['cfg'] and R['cfg']['spd'] == 1.5 and R['cfg']['hz']['traffic'] == 1
              and R['proto'] == 120 and not errs)
        print('errors', errs[:4]); print('DEV TEST', 'passed' if ok else 'FAILED')
        await b.close()


asyncio.run(main())
