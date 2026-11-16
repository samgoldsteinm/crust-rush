"""Balloon Battle on line, two players (host and friend in two browser windows on this PC, through the game's own matchmaking):
   py.cmd tools/neon/bbnet.py      ->  "ONLINE BALLOON BATTLE TEST passed"
The host opens a room in Balloon Battle, the friend joins and readies up, the battle starts on both. Then, on the host: a hit on the friend
(one balloon gone, a point to the host), the friend's whole round knocked out (eliminated), and the clock run out. Checked on the friend's
screen each time: the same arena and karts, balloons on every kart, the host's clock, the friend's own balloons and the host's points, out
of the round but watching (no results yet), then the results in battle order on both screens. Names are the game's defaults."""
import asyncio, json
from playwright.async_api import async_playwright
URL = 'http://localhost:8771/webcopy6/index.html'


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(channel='chromium', args=['--use-angle=d3d11', '--enable-gpu', '--ignore-gpu-blocklist', '--enable-webgl'])
        pages = []; errs = []; bad = 0
        for who in ('host', 'friend'):
            ctx = await b.new_context(viewport={'width': 1000, 'height': 600}, service_workers='block'); pg = await ctx.new_page()
            pg.on('pageerror', lambda e, w=who: errs.append(w + ': ' + str(e)[:200])); pages.append(pg)
            await pg.goto(URL); await pg.wait_for_function("document.getElementById('menu')&&!document.getElementById('menu').hidden", timeout=600000)
            await pg.evaluate("__ev(`qKey='fast';applyQuality();introSkip=true;try{store.set('crust-lb-name','')}catch(e){};const ov=$('lbNameOv');if(ov)ov.hidden=true;`)")
        A, B = pages
        await A.evaluate("__ev(`mode='bb';mapIdx=MAPS.findIndex(m=>m.battle);loadMap(mapIdx,false);resetRace(true);try{refreshMenu();}catch(e){}`)")
        ev = lambda pg, s: pg.evaluate("(js)=>__ev('JSON.stringify('+js+')')", s)

        def say(name, r, ok):
            nonlocal bad; bad += not ok; print(('ok   ' if ok else 'FAIL ') + name, json.dumps(r)[:600], flush=True)

        async def until(pg, js, secs=120, what=''):
            for i in range(int(secs * 4)):
                if json.loads(await ev(pg, js)): return True
                await pg.wait_for_timeout(250)
            print('TIMED OUT waiting for', what or js, flush=True); return False
        await A.evaluate("__ev(`netHost().then(()=>{window.__code=NET.code;}).catch(e=>{window.__err=String(e&&e.message||e);})`)")
        if not await until(A, "!!(window.__code||window.__err)", 60, 'the room'): return
        code = json.loads(await ev(A, "window.__code||null")); print('room', 'opened' if code else json.loads(await ev(A, "window.__err")), flush=True)
        if not code: return
        say('the host is still in Balloon Battle in its room', json.loads(await ev(A, "({mode,map:MAPS[mapIdx].id})")), json.loads(await ev(A, "mode==='bb'")))
        await B.evaluate("(c)=>__ev(`netJoin('${c}').then(()=>{window.__j=1;}).catch(e=>{window.__err=String(e&&e.message||e);})`)", code)
        if not await until(A, "NET.conns.some(c=>c.open)", 90, 'the friend to connect'): print('friend error', await ev(B, "window.__err||null")); return
        print('joined', flush=True)
        await A.evaluate("__ev(`startFromMenu()`)")
        await until(B, "!!NET.hostTk||NET.pl.length>0", 20); await B.wait_for_timeout(800); await B.evaluate("__ev(`netSendPick(true)`)")
        if not await until(A, "NET.pendMap!=null&&netAllReady()", 40, 'everyone ready'): return
        await A.evaluate("__ev(`netHostGo()`)")
        if not (await until(A, "state==='race'", 240, 'the host in the battle') and await until(B, "state==='race'", 240, 'the friend in the battle')): bad += 1; return
        await A.wait_for_timeout(3000)
        S = "({mode,map:MAPS[mapIdx].id,battle:BATTLE,karts:karts.length,t:Math.round(BB.t),bal:karts.map(k=>k.bal),me:player&&{bal:player.bal,bbS:player.bbS||0,dead:!!player.bbDead,fin:!!player.finished},hud:document.getElementById('bbHud')&&document.getElementById('bbHud').textContent,spec:!!(SPEC&&SPEC.on),res:!results.hidden})"
        ra = json.loads(await ev(A, S)); rb = json.loads(await ev(B, S))
        say('the same arena and karts on both, in a battle', {'host': ra, 'friend': rb}, ra['battle'] and rb['battle'] and ra['map'] == rb['map'] and ra['karts'] == rb['karts'] and rb['bal'] == ra['bal'] and len(rb['bal']) == ra['karts'])
        say('the friend\'s clock follows the host\'s', {'host': ra['t'], 'friend': rb['t'], 'hud': rb['hud']}, abs(ra['t'] - rb['t']) <= 2 and rb['hud'] and ':' in rb['hud'])
        # a hit: the host's player pops one of the friend's balloons
        await A.evaluate("__ev(`{const f=karts.find(k=>k.netName&&k!==player);battleHit(f,player);}`)")
        await until(B, "player.bal===4", 10, 'the friend to lose a balloon')
        rb = json.loads(await ev(B, S)); hostOnB = json.loads(await ev(B, "(()=>{const h=karts.find(k=>k.netName&&k!==player);return h?h.bbS||0:-1})()"))
        say('the friend lost a balloon and sees the host\'s point', {'friendBal': rb['me']['bal'], 'hostPoints': hostOnB}, rb['me']['bal'] == 4 and hostOnB == 1)
        # the friend knocked right out (all three sets)
        await A.evaluate("__ev(`{const f=karts.find(k=>k.netName&&k!==player);f.bbL=BB_SETS.length-1;f.bal=1;battleHit(f,player);}`)")
        await until(B, "!!player.bbDead", 10, 'the friend to be out'); await B.wait_for_timeout(2600)
        rb = json.loads(await ev(B, S))
        await B.screenshot(path='D:/crust-rush/scratch/bbnet_out.png')
        say('the friend is out of the round, watching, no results yet', rb['me'] | {'spec': rb['spec'], 'res': rb['res']}, rb['me']['dead'] and rb['spec'] and not rb['res'])
        # the clock runs out
        await A.evaluate("__ev(`BB.t=0.05`)")
        ok = await until(A, "!results.hidden", 30, 'the host\'s results') and await until(B, "!results.hidden", 30, 'the friend\'s results')
        await A.wait_for_timeout(800)
        R = "({sub:document.getElementById('resSub').textContent,rows:[...document.querySelectorAll('#resList li')].map(l=>l.textContent)})"
        xa = json.loads(await ev(A, R)); xb = json.loads(await ev(B, R))
        await A.screenshot(path='D:/crust-rush/scratch/bbnet_host.png'); await B.screenshot(path='D:/crust-rush/scratch/bbnet_friend.png')
        say('results on both, in battle order with points', {'host': xa, 'friend': xb}, ok and 'Balloon Battle' in xa['sub'] and 'Balloon Battle' in xb['sub'] and 'logged' not in xb['sub'] and any('point' in r for r in xa['rows']) and
            [r.replace(' (you)', '') for r in xa['rows']] == [r.replace(' (you)', '') for r in xb['rows']])
        print('errors', errs[:6]); print('ONLINE BALLOON BATTLE TEST', 'FAILED' if bad or errs else 'passed'); await b.close()
asyncio.run(main())
