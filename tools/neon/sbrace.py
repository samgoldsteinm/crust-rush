"""(patch 52) A room's Sandbox race from a start line, with invites; built on sbnet.py's setup.
   py.cmd tools/neon/sbrace.py   ->  "SANDBOX RACE TEST passed"
1. The friend, in the garage, asks to race there; the host (on Margherita Ring) gets the invite and joins: both race on the garage's track,
   only they; the host's Back to Sandbox ends it for both, back in Sandbox in the garage.
2. The friend asks again; the host says no: no race, the friend is offered a race alone.
3. The host asks; the friend says no: the host races (on line, alone), the friend keeps driving in Sandbox; the host comes back.
(sbnet.py's own doc follows.) Sandbox on line, two players (host and friend in two browser windows on this PC, through the game's own matchmaking):
   py.cmd tools/neon/sbnet.py      ->  "ONLINE SANDBOX TEST passed"   (pictures scratch/sbnet_*.png)
The host opens a room in Sandbox (Margherita Ring), the friend joins and readies up, both start Sandbox there. Checked: both are in
Sandbox in the same place, each sees the other's car (drawn, named) near where it really is, the friend's clock follows the host's
(set to night on the host), then the friend fast-travels to the garage: the host no longer draws them and lists them as elsewhere."""
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
            await pg.evaluate("__ev(`qKey='fast';applyQuality();introSkip=true;const ov=$('lbNameOv');if(ov)ov.hidden=true;`)")
        A, B = pages
        await A.evaluate("__ev(`mode='sb';mapIdx=MAPS.findIndex(m=>m.id==='margherita');loadMap(mapIdx,false);resetRace(true);try{refreshMenu();}catch(e){}`)")
        # (patch 47b) the friend's menu shows another map: they must still start at the host's place
        await B.evaluate("__ev(`mapIdx=MAPS.findIndex(m=>m.id==='backyard');loadMap(mapIdx,false);resetRace(true);1`)")
        ev = lambda pg, s: pg.evaluate("(js)=>__ev('JSON.stringify('+js+')')", s)

        def say(name, r, ok):
            nonlocal bad; bad += not ok; print(('ok   ' if ok else 'FAIL ') + name, json.dumps(r)[:500], flush=True)

        async def until(pg, js, secs=120, what=''):
            for i in range(int(secs * 4)):
                if json.loads(await ev(pg, js)): return True
                await pg.wait_for_timeout(250)
            print('TIMED OUT waiting for', what or js, flush=True); return False
        await A.evaluate("__ev(`netHost().then(()=>{window.__code=NET.code;}).catch(e=>{window.__err=String(e&&e.message||e);})`)")
        if not await until(A, "!!(window.__code||window.__err)", 60, 'the room'): return
        code = json.loads(await ev(A, "window.__code||null"))
        if not code: print('no room', await ev(A, "window.__err")); return
        say('the host is still in Sandbox in its room', json.loads(await ev(A, "({mode,map:MAPS[mapIdx].id})")), json.loads(await ev(A, "mode==='sb'")))
        await B.evaluate("(c)=>__ev(`netJoin('${c}').then(()=>{window.__j=1;}).catch(e=>{window.__err=String(e&&e.message||e);})`)", code)
        if not await until(A, "NET.conns.some(c=>c.open)", 90, 'the friend to connect'): print('friend error', await ev(B, "window.__err||null")); return
        await A.evaluate("__ev(`startFromMenu()`)")
        await until(B, "!!NET.hostTk||NET.pl.length>0", 20); await B.wait_for_timeout(800); await B.evaluate("__ev(`netSendPick(true)`)")
        if not await until(A, "NET.pendMap!=null&&netAllReady()", 40, 'everyone ready'): return
        await A.evaluate("__ev(`netHostGo()`)")
        if not (await until(A, "SBX&&state==='race'", 240, 'the host in Sandbox') and await until(B, "SBX&&state==='race'", 240, 'the friend in Sandbox')): bad += 1; print('ERR', errs[:4]); return
        say('the friend starts at the host place (patch 47b)', {'host': json.loads(await ev(A, "MAPS[mapIdx].id")), 'friend': json.loads(await ev(B, "MAPS[mapIdx].id"))}, json.loads(await ev(A, "MAPS[mapIdx].id")) == json.loads(await ev(B, "MAPS[mapIdx].id")) == 'margherita')
        await A.wait_for_timeout(3500)
        S = "(()=>{const o=[...SBN.peers.values()].map(P=>({nm:P.nm,reg:P.reg,drawn:!!(P.m&&P.m.g.visible),x:P.m?Math.round(P.m.g.position.x):null,z:P.m?Math.round(P.m.g.position.z):null}));return {sbx:SBX,cfg:!!NET.cfg,map:MAPS[mapIdx].id,me:[Math.round(player.x),Math.round(player.y)],peers:o,list:document.getElementById('sbnList')&&document.getElementById('sbnList').textContent,ck:+sbClockNow().toFixed(3)}})()"
        ra = json.loads(await ev(A, S)); rb = json.loads(await ev(B, S))
        say('both in Sandbox in the same place, no race config', {'host': ra['map'], 'friend': rb['map']}, ra['sbx'] and rb['sbx'] and ra['map'] == rb['map'] and not ra['cfg'] and not rb['cfg'])
        def near(peer, me): return peer and peer['drawn'] and peer['x'] is not None and abs(peer['x'] - me[0]) < 40 and abs(peer['z'] - me[1]) < 40
        say('the host draws the friend\'s car where it is', {'peer': ra['peers'], 'friend at': rb['me']}, len(ra['peers']) == 1 and near(ra['peers'][0], rb['me']))
        say('the friend draws the host\'s car where it is', {'peer': rb['peers'], 'host at': ra['me']}, len(rb['peers']) == 1 and near(rb['peers'][0], ra['me']))
        await A.screenshot(path='D:/crust-rush/scratch/sbnet_host.png'); await B.screenshot(path='D:/crust-rush/scratch/sbnet_friend.png')
        await A.evaluate("__ev(`SB.clock=.02;sbClockApply();`)"); await B.wait_for_timeout(1500)
        ck = json.loads(await ev(B, "+sbClockNow().toFixed(3)"))
        say('the friend\'s clock follows the host\'s (set to night)', {'friend': ck}, abs(ck - .02) < .01)
        await B.evaluate("__ev(`sbMapTravel('garage')`)")
        await until(B, "SBX&&state==='race'&&MAPS[mapIdx].id==='garage'", 120, 'the friend in the garage'); await A.wait_for_timeout(2500)
        ra = json.loads(await ev(A, S))
        await A.screenshot(path='D:/crust-rush/scratch/sbnet_apart.png')
        say('the friend went to the garage', {}, True)
        R = "(()=>({st:state,sbx:SBX,map:MAPS[mapIdx].id,cfg:NET.cfg?{sbr:NET.cfg.sbr,mi:NET.cfg.mi,n:NET.cfg.karts.filter(k=>k.who!=null&&k.who>=0).length}:null,inv:!!(SBI.inv),ask:!!(document.getElementById('sbiAsk')&&!document.getElementById('sbiAsk').hidden),askT:document.getElementById('sbiAsk')?document.getElementById('sbiAsk').textContent.slice(0,60):'',race:NET.sbRace?[...NET.sbRace]:null}))()"
        # 1. the friend asks in the garage, the host joins
        await B.evaluate("__ev(`SBI.ask={mi:mapIdx};sbRaceAskPick('f')`)")
        ok = await until(A, "!!SBI.inv", 20, 'the invite on the host')
        say('the host sees the friend invite', json.loads(await ev(A, R)), ok)
        await A.screenshot(path='D:/crust-rush/scratch/sbrace_invite.png')
        await A.evaluate("__ev(`sbInvAnswer(true)`)")
        ok = await until(A, "state==='race'&&!SBX&&!!NET.cfg", 240, 'the host in the race') and await until(B, "state==='race'&&!SBX&&!!NET.cfg", 240, 'the friend in the race')
        ra = json.loads(await ev(A, R)); rb = json.loads(await ev(B, R))
        say('both race on the garage track, a Sandbox race of two players', {'host': ra, 'friend': rb}, ok and ra['map'] == rb['map'] == 'garage' and ra['cfg'] and ra['cfg']['sbr'] == 1 and ra['cfg']['n'] == 2)
        await B.screenshot(path='D:/crust-rush/scratch/sbrace_race.png')
        await A.wait_for_timeout(4000)
        await A.evaluate("__ev(`toMenu()`)")
        ok = await until(A, "SBX&&state==='race'&&!NET.cfg", 240, 'the host back in Sandbox') and await until(B, "SBX&&state==='race'&&!NET.cfg", 240, 'the friend back in Sandbox')
        ra = json.loads(await ev(A, R)); rb = json.loads(await ev(B, R))
        say('the host goes back: both are in Sandbox again, at the garage', {'host': ra, 'friend': rb}, ok and ra['map'] == rb['map'] == 'garage' and ra['race'] is None)
        # 2. the host says no
        await B.wait_for_timeout(2500)
        await B.evaluate("__ev(`SBI.ask={mi:mapIdx};sbRaceAskPick('f')`)")
        await until(A, "!!SBI.inv", 20, 'the second invite')
        await A.evaluate("__ev(`sbInvAnswer(false)`)")
        ok = await until(B, "!!(document.getElementById('sbiAsk')&&!document.getElementById('sbiAsk').hidden)", 20, 'the offer to race alone')
        rb = json.loads(await ev(B, R))
        say('the host said no: no race, the friend is offered a race alone', rb, ok and rb['sbx'] and not rb['cfg'] and 'host' in rb['askT'])
        await B.evaluate("__ev(`sbiHide('sbiAsk')`)")
        # 3. the host asks, the friend says no
        await A.wait_for_timeout(1000)
        await A.evaluate("__ev(`SBI.ask={mi:mapIdx};sbRaceAskPick('f')`)")
        await until(B, "!!SBI.inv", 20, 'the host invite')
        await B.evaluate("__ev(`sbInvAnswer(false)`)")
        ok = await until(A, "state==='race'&&!SBX&&!!NET.cfg", 240, 'the host racing')
        await B.wait_for_timeout(3000)
        ra = json.loads(await ev(A, R)); rb = json.loads(await ev(B, R))
        say('the friend said no: the host races, the friend keeps driving in Sandbox', {'host': ra, 'friend': rb}, ok and ra['cfg'] and ra['cfg']['n'] == 1 and rb['sbx'] and not rb['cfg'])
        await A.evaluate("__ev(`toMenu()`)")
        ok = await until(A, "SBX&&state==='race'&&!NET.cfg", 240, 'the host back')
        say('the host is back in Sandbox', json.loads(await ev(A, R)), ok)
        print('errors', errs[:6]); print('SANDBOX RACE TEST', 'FAILED' if bad or errs else 'passed'); await b.close()
asyncio.run(main())
