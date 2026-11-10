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
                                          '--autoplay-policy=no-user-gesture-required'])
        ctx = await b.new_context(viewport={'width': 960, 'height': 540}, service_workers='block')
        await ctx.add_init_script('window.CR_BROKERS=%s;' % json.dumps([BROKER]))
        pg = await ctx.new_page()
        errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:300]))

        async def route(r):
            u = r.request.url
            if u.startswith('http://127.0.0.1:%d/' % PORT) and (re.search(r'/js/game\.[0-9a-f]+\.js', u) or u.endswith('/') or u.endswith('.html')):
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
        await pg.wait_for_function("document.getElementById('menu')&&!document.getElementById('menu').hidden&&window.__ev", timeout=900000)
        print('XPLAY web: booted in %ds' % (time.time() - t0), flush=True)
        await pg.evaluate("__ev(`qKey='fast';store.set('crust-q',qKey);applyQuality();introSkip=true;1`)")
        if ROLE == 'join':
            ok = await join(pg)
            if errs:
                print('XPLAY web page errors:', errs[:5], flush=True)
            await b.close()
            return ok
        code = await pg.evaluate("__ev('netHost()').then(()=>__ev('NET.code'))")
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
            if s['st'] == 'race' and s['rt'] > 32:
                ok = (s['pk'] or 0) > 150 and s['ack'] > 1500
                print('XPLAY WEB %s PC kart prog %s, controls played %d, race time %.1f' % ('PASS' if ok else 'FAIL', s['pk'], s['ack'], s['rt']), flush=True)
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
    await pg.evaluate("__ev(`netJoin('%s')`).then(()=>__ev('netSendPick(true);1'))" % code)
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
        if s['st'] == 'race' and s['rt'] > 32:
            ok = (s['me'] or 0) > 150 and s['ack'] > 1500
            print('XPLAY WEB %s my kart prog %s, controls sent %d, played by the PC %d, big fixes %d, race time %.1f' % ('PASS' if ok else 'FAIL', s['me'], s['seq'], s['ack'], s['fix'], s['rt']), flush=True)
            return ok
        await asyncio.sleep(0.5)
    print('XPLAY WEB FAIL timed out', flush=True)
    return False


sys.exit(0 if asyncio.run(main()) else 1)
