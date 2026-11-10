"""Cross-play test, the browser side, through a test broker (tools/mqtt_broker.py).
ROLE=host (default): the published web game hosts a room, writes the room code for the PC copy (tests/xplay.tscn) to
join, starts the race once the PC is ready, lets the computer drive the host's kart, and checks the PC's kart really
races on the host: its controls arrive and are played (the host's acknowledgements climb) and it gets round.
ROLE=join: the PC hosts and writes the code; the web game joins, its TESTING autopilot drives, and it checks its own
kart gets round on the PC's race with its controls played. Prints XPLAY WEB PASS / FAIL.
Usage: WEB=web ROOM_FILE=room.txt BROKER=ws://127.0.0.1:8765/mqtt [MI=1] [ROLE=host|join] python3 tools/xplay_test.py"""
import asyncio, functools, http.server, json, os, re, sys, threading, time
from playwright.async_api import async_playwright

WEB = os.environ.get('WEB', 'web')
ROOM = os.environ.get('ROOM_FILE', 'room.txt')
BROKER = os.environ.get('BROKER', 'ws://127.0.0.1:8765/mqtt')
MI = int(os.environ.get('MI', '1'))
ROLE = os.environ.get('ROLE', 'host')
PORT = 8790


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


srv = http.server.ThreadingHTTPServer(('127.0.0.1', PORT), functools.partial(Quiet, directory=WEB))
threading.Thread(target=srv.serve_forever, daemon=True).start()
HOOK = 'window.__ev=(x)=>eval(x);requestAnimationFrame(frame);\n})();'


async def main():
    t0 = time.time()
    ok = False
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--no-sandbox',
                                          '--autoplay-policy=no-user-gesture-required', '--disable-features=LocalNetworkAccessChecks,PrivateNetworkAccessRespectPreflightResults'])
        ctx = await b.new_context(viewport={'width': 640, 'height': 360}, service_workers='block')
        # the lightest picture preset from the start (no recompiling later): a software GPU manages only a few frames a second
        await ctx.add_init_script("window.CR_BROKERS=%s;try{localStorage.setItem('crust-q','lite')}catch(e){}" % json.dumps([BROKER]))
        pg = await ctx.new_page()
        errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        pg.on('websocket', lambda ws: (print('XPLAY web: websocket', ws.url, flush=True), ws.on('close', lambda *_: print('XPLAY web: websocket closed', ws.url, flush=True)), ws.on('socketerror', lambda e: print('XPLAY web: websocket error', e, flush=True))))
        pg.on('console', lambda m: print('XPLAY web console:', m.text[:160], flush=True) if ('ebSocket' in m.text or 'mqtt' in m.text.lower()) else None)

        async def route(r):
            u = r.request.url
            # only the game script is rewritten: a page whose HTML comes back rewritten counts as a public origin, and Chrome's
            # local network checks then refuse its socket to the test broker on 127.0.0.1
            if u.startswith('http://127.0.0.1:%d/' % PORT) and re.search(r'/js/game\.[0-9a-f]+\.js', u):
                resp = await r.fetch()
                body = await resp.text()
                if 'requestAnimationFrame(frame);\n})();' in body:
                    body = body[::-1].replace('requestAnimationFrame(frame);\n})();'[::-1], HOOK[::-1], 1)[::-1]
                await r.fulfill(response=resp, body=body, headers={**resp.headers, 'cache-control': 'no-store'})
            elif u.startswith('http://127.0.0.1') or u.startswith('ws://127.0.0.1'):
                await r.continue_()
            else:
                await r.abort()   # nothing from the internet: fonts, the WebRTC library and TURN list fail, as when offline
        await pg.route('**/*', route)
        await pg.goto('http://127.0.0.1:%d/index.html' % PORT, wait_until='domcontentloaded', timeout=300000)
        # polled by hand: waiting on animation frames stalls while the software GPU is busy compiling the menu
        while True:
            okm = await pg.evaluate("!!(document.getElementById('menu')&&!document.getElementById('menu').hidden&&window.__ev)")
            if okm:
                break
            if time.time() - t0 > 900:
                print('XPLAY WEB FAIL the game did not start', errs[:3], flush=True)
                await b.close()
                return False
            await asyncio.sleep(2)
        print('XPLAY web: booted in %ds' % (time.time() - t0), flush=True)
        # (no quality change here: recompiling every shader on a software GPU holds the page past the relay's 9 s
        # connect limit; the game's own boot preset is fine)
        await pg.evaluate("__ev(`introSkip=true;1`)")
        if ROLE == 'join':
            ok = await join(pg)
            if errs:
                print('XPLAY web page errors:', errs[:5], flush=True)
            await b.close()
            return ok
        code = None
        for attempt in range(4):
            try:
                code = await pg.evaluate("__ev('netHost()').then(()=>__ev('NET.code'))")
                break
            except Exception as e:     # a busy software GPU can hold the page past the relay's 9 s connect limit
                print('XPLAY web: hosting failed (%s), trying again' % str(e)[:120], flush=True)
                await asyncio.sleep(3)
        if not code:
            print('XPLAY WEB FAIL could not host', flush=True)
            await b.close()
            return False
        open(ROOM, 'w').write(code)
        print('XPLAY web: hosting room', code, flush=True)
        t1 = time.time()
        while True:
            st = await pg.evaluate("__ev(`JSON.stringify({n:NET.pl.length,ready:NET.pl.every(p=>p.id===0||p.ready),pl:NET.pl.map(p=>p.name)})`)")
            st = json.loads(st)
            if st['n'] > 1 and st['ready']:
                print('XPLAY web: joined', st['pl'], flush=True)
                break
            if time.time() - t1 > 240:
                print('XPLAY WEB FAIL nobody joined', flush=True)
                await b.close()
                return False
            await asyncio.sleep(1)
        await pg.evaluate("__ev(`clsKey='medium';mode='single';gp=null;netHostStart(%d);1`)" % MI)
        print('XPLAY web: race loading', flush=True)
        t2 = time.time()
        auto = False
        last = 0
        while time.time() - t2 < 900:
            s = json.loads(await pg.evaluate("""__ev(`(()=>{const k=karts.find(q=>q.netId===1);return JSON.stringify({st:state,rt:raceTime,ack:NET.ack[1]||0,
                pk:k?k.prog:null,px:k?Math.round(k.x):0,py:k?Math.round(k.y):0,me:player?player.prog:null,q:(NET.inQ[1]||[]).length,conns:NET.conns.length,
                buf:NET.inS[1]?NET.inS[1].T:0})})()`)"""))
            if s['st'] == 'race' and not auto:
                await pg.evaluate("__ev(`player.auto=true;1`)")
                auto = True
            if time.time() - last > 5:
                last = time.time()
                print('XPLAY web', json.dumps(s), flush=True)
            if s['conns'] == 0 and s['st'] in ('race', 'countdown'):
                print('XPLAY WEB FAIL the PC left during the race', flush=True)
                break
            # passes once the PC's kart has got well round on its own controls; then stays a little so the PC sees it too
            ok = s['st'] == 'race' and s['rt'] > 15 and (s['pk'] or 0) > 150 and s['ack'] > 1500
            if ok or (s['st'] == 'race' and s['rt'] > 150):
                print('XPLAY WEB %s PC kart prog %s, controls played %d, race time %.1f' % ('PASS' if ok else 'FAIL', s['pk'], s['ack'], s['rt']), flush=True)
                if ok:
                    await asyncio.sleep(20)
                break
            await asyncio.sleep(0.5)
        if errs:
            print('XPLAY web page errors:', errs[:5], flush=True)
        await b.close()
    return ok


async def join(pg):
    t1 = time.time()
    while not (os.path.exists(ROOM) and len(open(ROOM).read().strip()) == 4):
        if time.time() - t1 > 600:
            print('XPLAY WEB FAIL no room code from the PC', flush=True)
            return False
        await asyncio.sleep(1)
    code = open(ROOM).read().strip()
    print('XPLAY web: joining the PC room', code, flush=True)
    for attempt in range(4):
        try:
            await pg.evaluate("__ev(`netJoin('%s')`).then(()=>__ev('netSendPick(true);1'))" % code)
            break
        except Exception as e:
            print('XPLAY web: joining failed (%s), trying again' % str(e)[:120], flush=True)
            await asyncio.sleep(3)
    print('XPLAY web: in the room', flush=True)
    t2 = time.time()
    last = 0
    td = False
    while time.time() - t2 < 1200:
        s = json.loads(await pg.evaluate("""__ev(`JSON.stringify({st:state,rt:raceTime,cfg:!!NET.cfg,role:NET.role,me:player?player.prog:null,ack:NET.ackRx||0,
            seq:NET.seq||0,fix:NET.fixN||0,sn:NET.lastSn||0,pl:NET.pl.length})`)"""))
        if s['st'] == 'race' and s['cfg'] and not td:
            await pg.evaluate("__ev(`TD.on=true;1`)")
            td = True
        if time.time() - last > 5:
            last = time.time()
            print('XPLAY web', json.dumps(s), flush=True)
        if not s['role']:
            print('XPLAY WEB FAIL left the room', flush=True)
            return False
        # a browser on a software GPU sends only a few controls a second against the PC's 60, so its kart is slow to get
        # round on the PC's race: a smaller bar, and more time
        ok = s['st'] == 'race' and s['rt'] > 15 and (s['me'] or 0) > 60 and s['ack'] > 600
        if ok or (s['st'] == 'race' and s['rt'] > 320):
            print('XPLAY WEB %s my kart prog %s, controls sent %d, played by the PC %d, big fixes %d, race time %.1f' % ('PASS' if ok else 'FAIL', s['me'], s['seq'], s['ack'], s['fix'], s['rt']), flush=True)
            if ok:
                await asyncio.sleep(20)
            return ok
        await asyncio.sleep(0.5)
    print('XPLAY WEB FAIL timed out', flush=True)
    return False


sys.exit(0 if asyncio.run(main()) else 1)
