"""Cross-play of the modes added on line in web v208, the browser side (the PC side: tests/xmodes.gd). The browser hosts a room in Balloon
Battle (MODE=bb) or Sandbox (MODE=sb) through a test broker, the PC joins and readies up.
  bb: the battle starts; once the PC's kart is driving on its controls, the host's player takes one of its balloons (battleHit), then the
      clock is run out. Passes if the PC's controls were played and the round ended.
  sb: Sandbox starts on Margherita Ring; passes if the PC's car is drawn on the browser's screen there.
Usage: WEB=<built site> ROOM_FILE=room.txt BROKER=ws://127.0.0.1:8765/mqtt MODE=bb python tools/xmodes_web.py   ->  "XMODES WEB PASS" / FAIL"""
import asyncio, functools, http.server, json, os, re, sys, threading, time
from playwright.async_api import async_playwright

WEB = os.environ.get('WEB', 'web')
ROOM = os.environ.get('ROOM_FILE', 'room.txt')
BROKER = os.environ.get('BROKER', 'ws://127.0.0.1:8765/mqtt')
MODE = os.environ.get('MODE', 'bb')
PORT = 8791


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


srv = http.server.ThreadingHTTPServer(('127.0.0.1', PORT), functools.partial(Quiet, directory=WEB))
threading.Thread(target=srv.serve_forever, daemon=True).start()
HOOK = 'window.__ev=(x)=>eval(x);requestAnimationFrame(frame);\n})();'


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(channel='chromium', args=['--use-angle=d3d11', '--enable-gpu', '--ignore-gpu-blocklist', '--disable-features=LocalNetworkAccessChecks,PrivateNetworkAccessRespectPreflightResults'])
        ctx = await b.new_context(viewport={'width': 800, 'height': 450}, service_workers='block')
        await ctx.add_init_script("window.CR_BROKERS=%s;try{localStorage.setItem('crust-q','fast');sessionStorage.setItem('crust-lb-asked','1')}catch(e){}" % json.dumps([BROKER]))
        pg = await ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:300]))

        async def route(r):
            u = r.request.url
            if u.startswith('http://127.0.0.1:%d/' % PORT) and re.search(r'/js/game\.[0-9a-f]+\.js', u):
                resp = await r.fetch(); body = await resp.text()
                if 'window.__ev' not in body and 'requestAnimationFrame(frame);\n})();' in body:
                    body = body[::-1].replace('requestAnimationFrame(frame);\n})();'[::-1], HOOK[::-1], 1)[::-1]
                await r.fulfill(response=resp, body=body, headers={**resp.headers, 'cache-control': 'no-store'})
            elif u.startswith('http://127.0.0.1') or u.startswith('ws://127.0.0.1'):
                await r.continue_()
            else:
                await r.abort()
        await pg.route('**/*', route)
        await pg.goto('http://127.0.0.1:%d/index.html' % PORT, wait_until='domcontentloaded', timeout=300000)
        t0 = time.time()
        while not await pg.evaluate("!!(document.getElementById('menu')&&!document.getElementById('menu').hidden&&window.__ev)"):
            if time.time() - t0 > 600: print('XMODES WEB FAIL the game did not start', flush=True); return False
            await asyncio.sleep(1)
        if MODE == 'bb':
            await pg.evaluate("__ev(`introSkip=true;mode='bb';mapIdx=MAPS.findIndex(m=>m.battle);loadMap(mapIdx,false);resetRace(true);1`)")
        else:
            await pg.evaluate("__ev(`introSkip=true;mode='sb';mapIdx=MAPS.findIndex(m=>m.id==='margherita');loadMap(mapIdx,false);resetRace(true);1`)")
        code = await pg.evaluate("__ev('netHost()').then(()=>__ev('NET.code'))")
        open(ROOM, 'w').write(code); print('XMODES web: hosting room', code, MODE, flush=True)
        t1 = time.time()
        while True:
            st = json.loads(await pg.evaluate("__ev(`JSON.stringify({n:NET.pl.length,ready:NET.pl.every(p=>p.id===0||p.ready)})`)"))
            if st['n'] > 1 and st['ready']: break
            if time.time() - t1 > 300: print('XMODES WEB FAIL nobody joined', flush=True); return False
            await asyncio.sleep(1)
        print('XMODES web: the PC joined', flush=True)
        await pg.evaluate("__ev(`clsKey='medium';gp=null;netHostStart(mapIdx);1`)")
        ok = False; t2 = time.time(); hit = False; ended = False; last = 0
        while time.time() - t2 < 900:
            if MODE == 'bb':
                s = json.loads(await pg.evaluate("__ev(`(()=>{const k=karts.find(q=>q.netId===1);return JSON.stringify({st:state,bb:BATTLE,t:BB.t,ack:NET.ack[1]||0,bal:k?k.bal:null,res:!results.hidden})})()`)"))
                if s['st'] == 'race' and s['ack'] > 300 and not hit:
                    await pg.evaluate("__ev(`{const k=karts.find(q=>q.netId===1);player.auto=true;if(k)battleHit(k,player);}`)"); hit = True; print('XMODES web: hit the PC', flush=True); hitT = time.time()
                if hit and not ended and time.time() - hitT > 8:
                    await pg.evaluate("__ev(`BB.t=.05`)"); ended = True; print('XMODES web: the clock run out', flush=True)
                if time.time() - last > 5: last = time.time(); print('XMODES web', json.dumps(s), flush=True)
                if ended and s['res']:
                    ok = s['bb'] and s['ack'] > 300; print('XMODES WEB %s battle: PC controls played %d, results shown' % ('PASS' if ok else 'FAIL', s['ack']), flush=True); break
            elif MODE == 'sbr':
                s = json.loads(await pg.evaluate("__ev(`JSON.stringify({sbx:SBX,st:state,map:MAPS[mapIdx].id,inv:!!SBI.inv,cfg:NET.cfg?{sbr:NET.cfg.sbr,n:NET.cfg.karts.filter(k=>k.who!=null&&k.who>=0).length}:null})`)"))
                if time.time() - last > 5: last = time.time(); print('XMODES web', json.dumps(s), flush=True)
                if s['inv'] and not getattr(main, 'joined', False):
                    await pg.evaluate("__ev(`sbInvAnswer(true)`)"); main.joined = True; print('XMODES web: joined the PC invite', flush=True)
                if s['cfg'] and s['st'] == 'race' and not s['sbx'] and not getattr(main, 'raced', False):
                    main.raced = s['cfg']; main.raceT = time.time(); print('XMODES web: racing', json.dumps(s), flush=True)
                if getattr(main, 'raced', False) and not getattr(main, 'back', False) and time.time() - main.raceT > 8:
                    await pg.evaluate("__ev(`toMenu()`)"); main.back = True; print('XMODES web: back to Sandbox', flush=True)
                if getattr(main, 'back', False) and s['sbx'] and not s['cfg']:
                    ok = main.raced['sbr'] == 1 and main.raced['n'] == 2; print('XMODES WEB %s sandbox race: raced with the PC (%s), back in Sandbox' % ('PASS' if ok else 'FAIL', json.dumps(main.raced)), flush=True); break
            else:
                s = json.loads(await pg.evaluate("__ev(`JSON.stringify({sbx:SBX,st:state,map:MAPS[mapIdx].id,peers:[...SBN.peers.values()].map(P=>({nm:P.nm,reg:P.reg,drawn:!!(P.m&&P.m.g.visible)}))})`)"))
                if time.time() - last > 5: last = time.time(); print('XMODES web', json.dumps(s), flush=True)
                if any(q['drawn'] for q in s['peers']) and time.time() - t2 > 20:
                    ok = True; print('XMODES WEB PASS sandbox: the PC\'s car is drawn here', json.dumps(s['peers']), flush=True); break
            await asyncio.sleep(0.5)
        if not ok: print('XMODES WEB FAIL', flush=True)
        await asyncio.sleep(15)
        if errs: print('XMODES web page errors:', errs[:5], flush=True)
        await b.close(); return ok


sys.exit(0 if asyncio.run(main()) else 1)
