"""Export the web game's garage for the PC build, on a GitHub runner: every body, wheel set, glider and driver.

Serves the published web game (a checkout of `main`), opens it in headless Chromium with a software GPU
at the Ultra preset and runs tools/glbexport.js inside the page. Writes to OUT/:
  garage.json            parts, stats, paints, liveries, and where every wheel set and driver sits on every body
  body_<id>.glb          each body, its paint, dark trim and stripe kept as separate marker-coloured materials
  wheel_<id>.glb, glider_<id>.glb, driver_<n>.glb, liv_*.png (livery decals and numbers)
Usage: WEB=web OUT=garage python3 tools/cigarage.py
"""
import asyncio, base64, functools, http.server, json, os, re, sys, threading, time
from playwright.async_api import async_playwright

WEB = os.environ.get('WEB', 'web')
OUT = os.environ.get('OUT', 'garage')
Q = os.environ.get('Q', 'ultra')
EXP = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'glbexport.js')).read()
PORT = 8790


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


srv = http.server.ThreadingHTTPServer(('127.0.0.1', PORT), functools.partial(Quiet, directory=WEB))
threading.Thread(target=srv.serve_forever, daemon=True).start()


async def main():
    t0 = time.time()
    os.makedirs(OUT, exist_ok=True)
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--no-sandbox'])
        ctx = await b.new_context(viewport={'width': 900, 'height': 420}, service_workers='block')
        pg = await ctx.new_page()
        errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:300]))

        async def route(r):
            u = r.request.url
            if re.search(r'/js/game\.[0-9a-f]+\.js', u):
                resp = await r.fetch()
                body = await resp.text()
                body = body.replace('requestAnimationFrame(frame);\n})();', 'window.__ev=(x)=>eval(x);requestAnimationFrame(frame);\n})();')
                await r.fulfill(response=resp, body=body, headers={**resp.headers, 'cache-control': 'no-store'})
            else:
                await r.continue_()
        await pg.route('**/*', route)
        await pg.goto(f'http://127.0.0.1:{PORT}/index.html', wait_until='domcontentloaded', timeout=300000)
        await pg.wait_for_function("document.getElementById('menu')&&!document.getElementById('menu').hidden", timeout=900000)

        async def ev(js):
            return await pg.evaluate("s=>__ev(s)", js)
        await ev("qKey='%s';store.set('crust-q',qKey);applyQuality();1" % Q)
        await pg.evaluate('src=>__ev(src)', EXP)
        print('booted', round(time.time() - t0), 's', flush=True)
        info = json.loads(await ev("JSON.stringify(__garageInfo())"))
        nb, nw, ng, nr = len(info['bodies']), len(info['wheels']), len(info['gliders']), len(info['racers'])
        print('parts', nb, nw, ng, nr, flush=True)
        # where the wheels and the driver sit on every body (in its real colours)
        info['placeBW'] = [[None] * nw for _ in range(nb)]
        info['placeDrv'] = [[None] * nr for _ in range(nb)]
        for bi in range(nb):
            for wi in range(nw):
                info['placeBW'][bi][wi] = json.loads(await ev("JSON.stringify(__placeBW(%d,%d))" % (bi, wi)))
            for ri in range(nr):
                info['placeDrv'][bi][ri] = json.loads(await ev("JSON.stringify(__placeDrv(%d,%d))" % (bi, ri)))
            print('placed body', bi, info['bodies'][bi]['id'], round(time.time() - t0), flush=True)
        for ri in range(nr):
            d = json.loads(await ev("JSON.stringify(__exportDriver(%d))" % ri))
            open(os.path.join(OUT, 'driver_%d.glb' % ri), 'wb').write(base64.b64decode(d['b64']))
            print('driver', ri, d['stats'].get('bytes'), flush=True)
        lt = json.loads(await ev("__livTex().then(o=>JSON.stringify(o))"))
        for k, v in lt.items():
            open(os.path.join(OUT, 'liv_%s' % k), 'wb').write(base64.b64decode(v))
        # marker colours: a paint and a stripe nobody else uses; the bake keeps paint, trim and stripe apart
        await ev("window.__b0=bake;bake=function(S,sh,vc){__garageBake(S);return window.__b0(S,sh,vc);};PAINTS.push('#fe01fd');window.__st0=RACERS.map(r=>r.stripe);RACERS.forEach(r=>r.stripe='#01fe03');1")
        info['liv'] = [None] * nb
        info['pw'] = [None] * nb
        for bi in range(nb):
            d = json.loads(await ev("JSON.stringify(__exportBody(%d))" % bi))
            open(os.path.join(OUT, 'body_%s.glb' % info['bodies'][bi]['id']), 'wb').write(base64.b64decode(d['b64']))
            info['liv'][bi] = d['liv']
            info['pw'][bi] = d['pw']
            print('body', bi, info['bodies'][bi]['id'], d['stats'].get('bytes'), 'tris', d['stats'].get('tris'), round(time.time() - t0), flush=True)
        for wi in range(nw):
            d = json.loads(await ev("JSON.stringify(__exportWheel(%d))" % wi))
            open(os.path.join(OUT, 'wheel_%s.glb' % info['wheels'][wi]['id']), 'wb').write(base64.b64decode(d['b64']))
        for gi in range(ng):
            d = json.loads(await ev("JSON.stringify(__exportGlider(%d))" % gi))
            open(os.path.join(OUT, 'glider_%s.glb' % info['gliders'][gi]['id']), 'wb').write(base64.b64decode(d['b64']))
        await ev("bake=window.__b0;PAINTS.pop();RACERS.forEach((r,i)=>r.stripe=window.__st0[i]);1")
        json.dump(info, open(os.path.join(OUT, 'garage.json'), 'w'), separators=(',', ':'))
        print('done', round(time.time() - t0), 's, errors', errs[:5], flush=True)
        if errs:
            sys.exit(1)
        await b.close()

asyncio.run(main())
