"""A Grand Prix on line, two players (host and friend in two browser windows on this PC, through the game's own matchmaking):
   py.cmd tools/neon/gpnet2.py
The host opens a room in Grand Prix mode, the friend joins by the room's code, both ready up, the race is run (the test ends it early: the
host's karts are put over the line, the friend's own kart a moment later, so the friend finishes AFTER the host), then the results are read
on both screens, the host presses its main button, both ready up again and the second race of the cup must load on both.
Want: the host's button says "Next race"; both screens show the cup standings; the friend's late finish is counted in the cup; the second
race is the cup's second track on both, with the same points on both. Player names are the game's defaults (nothing personal is sent)."""
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
            await pg.evaluate("__ev(`qKey='fast';applyQuality();clsKey='medium';introSkip=true;mode='gp';cupIdx=0;try{refreshMenu();}catch(e){}`)")
        A, B = pages
        ev = lambda pg, s: pg.evaluate("(js)=>__ev('JSON.stringify('+js+')')", s)
        def say(name, r, ok):
            nonlocal bad; bad += not ok; print(('ok   ' if ok else 'FAIL ') + name, r, flush=True)
        async def until(pg, js, secs=120, what=''):
            for i in range(int(secs * 4)):
                if json.loads(await ev(pg, js)): return True
                await pg.wait_for_timeout(250)
            print('TIMED OUT waiting for', what or js, flush=True); return False
        await A.evaluate("__ev(`netHost().then(()=>{window.__code=NET.code;}).catch(e=>{window.__err=String(e&&e.message||e);})`)")
        if not await until(A, "!!(window.__code||window.__err)", 60, 'the room'): return
        code = json.loads(await ev(A, "window.__code||null")); print('room', 'opened' if code else json.loads(await ev(A, "window.__err")), flush=True)
        if not code: return
        await B.evaluate("(c)=>__ev(`netJoin('${c}').then(()=>{window.__j=1;}).catch(e=>{window.__err=String(e&&e.message||e);})`)", code)
        if not await until(A, "NET.conns.some(c=>c.open)", 90, 'the friend to connect'): print('friend error', await ev(B, "window.__err||null")); return
        print('joined', flush=True)
        async def start(first):
            if first: await A.evaluate("__ev(`startFromMenu()`)")
            await until(B, "!!NET.hostTk||NET.pl.length>0", 20); await B.wait_for_timeout(800); await B.evaluate("__ev(`netSendPick(true)`)")
            if not await until(A, "NET.pendMap!=null&&netAllReady()", 40, 'everyone ready'): return False
            await A.evaluate("__ev(`netHostGo()`)")
            ok = await until(A, "state==='race'", 240, 'the host in the race') and await until(B, "state==='race'", 240, 'the friend in the race')
            return ok
        if not await start(True): print('the first race did not start', await ev(A, "({state:state,pend:NET.pendMap,pl:NET.pl})")); return
        r0 = {w: json.loads(await ev(pg, "({map:MAPS[mapIdx].id,mode:mode,gp:gp&&{race:gp.race,pts:gp.pts},karts:karts.length})")) for w, pg in (('host', A), ('friend', B))}
        say('race 1 is the cup\'s first track on both, in Grand Prix', r0, r0['host']['map'] == r0['friend']['map'] and r0['host']['gp'] and r0['friend']['gp'] and r0['host']['gp']['race'] == 0)
        await A.wait_for_timeout(2500)
        # the end of the race: everyone but the friend over the line now, the friend three seconds later
        await A.evaluate("__ev(`{let i=0;for(const k of karts){if(k.netName&&k!==player)continue;const p=track[2+i];k.x=k.px=p.x;k.y=k.py=p.y;k.idx=2+i;k.prog=LAPS*N+2+i;i++;}}`)")
        await until(A, "!results.hidden", 30, 'the host\'s results'); await A.wait_for_timeout(3000)
        early = json.loads(await ev(A, "({again:document.getElementById('againBtn').textContent,menu:document.getElementById('toMenuBtn').textContent,cup:!document.getElementById('gpBox').hidden,rows:[...document.querySelectorAll('#gpList li')].map(l=>l.textContent).slice(0,8)})"))
        print('host, friend still racing:', early, flush=True)
        await A.evaluate("__ev(`{for(const k of karts){if(k.netName&&k!==player){const p=track[12];k.x=k.px=p.x;k.y=k.py=p.y;k.idx=12;k.prog=LAPS*N+12;}}}`)")
        await until(B, "!results.hidden", 40, 'the friend\'s results'); await A.wait_for_timeout(2500)
        READ = "({again:document.getElementById('againBtn').textContent,againShown:getComputedStyle(document.getElementById('againBtn')).display!=='none',menu:document.getElementById('toMenuBtn').textContent,cup:!document.getElementById('gpBox').hidden,label:document.getElementById('gpLabel').textContent,rows:[...document.querySelectorAll('#gpList li')].map(l=>l.textContent),sub:document.getElementById('resSub').textContent,gp:gp&&{race:gp.race,pts:gp.pts}})"
        ra = json.loads(await ev(A, READ)); rb = json.loads(await ev(B, READ))
        await A.screenshot(path='D:/crust-rush/scratch/gpnet_host.png'); await B.screenshot(path='D:/crust-rush/scratch/gpnet_friend.png')
        say('host: the button goes on to the next race, and says so', {k: ra[k] for k in ('again', 'menu', 'cup', 'label')}, ra['again'] == 'Next race' and ra['cup'])
        say('friend: sees the cup standings', {k: rb[k] for k in ('againShown', 'cup', 'label')}, rb['cup'] and not rb['againShown'])
        fr = json.loads(await ev(A, "(()=>{const k=karts.find(k=>k.netName&&k!==player);return k?{name:k.netName,ri:k.ri,place:k.place}:null})()"))
        row = next((x for x in ra['rows'] if fr and fr['name'] in x and '(you)' not in x), '')
        say('the friend, who finished after the host, has points in the cup', {'friend': fr, 'row': row, 'rows': ra['rows']}, bool(row) and '+0' not in row)
        say('both screens show the same cup table', {'host': ra['rows'][:3], 'friend': rb['rows'][:3]}, [x.replace(' (you)', '') for x in ra['rows']] == [x.replace(' (you)', '') for x in rb['rows']])
        await A.evaluate("document.getElementById('againBtn').click()")
        if not await start(False): print('the second race did not start', await ev(A, "({state:state,pend:NET.pendMap})")); bad += 1
        r1 = {w: json.loads(await ev(pg, "({map:MAPS[mapIdx].id,want:MAPS[CUP_TRACKS[0][1]].id,gp:gp&&{race:gp.race,pts:gp.pts,np:gp.np||{}}})")) for w, pg in (('host', A), ('friend', B))}
        say('race 2 is the cup\'s second track on both, with the same points', r1, r1['host']['map'] == r1['host']['want'] == r1['friend']['map'] and r1['host']['gp'] and r1['friend']['gp'] and r1['host']['gp']['race'] == 1 and r1['host']['gp'] == r1['friend']['gp'] and sum(r1['host']['gp']['pts']) > 0 and len(r1['host']['gp'].get('np', {})) == 2)
        print('errors', errs[:6]); print('ONLINE GRAND PRIX TEST', 'FAILED' if bad or errs else 'passed'); await b.close()
asyncio.run(main())
