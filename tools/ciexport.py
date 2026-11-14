"""Export one track of the web game for the PC build, on a GitHub runner.

Serves the published web game (a checkout of `main`), opens it in headless Chromium with a software GPU,
loads the track at the Ultra preset and runs tools/glbexport.js inside the page. Writes to OUT/<id>/:
  <id>.json      track data (centre line, walls, ramps, height maps, lights) + "race" (boxes, loops...) + "haz"
  <id>.gltf/.bin the track's geometry by cell and material, textures in <id>_tex/
  <id>_haz.glb   the moving hazards (traffic, walkers, rolling meatballs, train wagons)
Usage: WEB=web OUT=maps MI=<map index> [Q=ultra] python3 tools/ciexport.py
"""
import asyncio, base64, functools, http.server, json, os, re, sys, threading, time
from playwright.async_api import async_playwright

WEB = os.environ.get('WEB', 'web')
OUT = os.environ.get('OUT', 'maps')
MI = int(os.environ.get('MI', '1'))
Q = os.environ.get('Q', 'ultra')
EXP = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'glbexport.js')).read()
PORT = 8765 + MI


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


srv = http.server.ThreadingHTTPServer(('127.0.0.1', PORT), functools.partial(Quiet, directory=WEB))
threading.Thread(target=srv.serve_forever, daemon=True).start()


async def main():
    t0 = time.time()
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--no-sandbox'])
        ctx = await b.new_context(viewport={'width': 1280, 'height': 720}, service_workers='block')
        pg = await ctx.new_page()
        errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:300]))

        async def route(r):
            u = r.request.url
            if re.search(r'/js/game\.[0-9a-f]+\.js', u):
                resp = await r.fetch()
                body = await resp.text()
                # reach the game's own variables from outside (they live inside its closure)
                body = body.replace('requestAnimationFrame(frame);\n})();', 'window.__ev=(x)=>eval(x);requestAnimationFrame(frame);\n})();')
                await r.fulfill(response=resp, body=body, headers={**resp.headers, 'cache-control': 'no-store'})
            else:
                await r.continue_()
        await pg.route('**/*', route)
        await pg.goto(f'http://127.0.0.1:{PORT}/index.html', wait_until='domcontentloaded', timeout=300000)
        await pg.wait_for_function("document.getElementById('menu')&&!document.getElementById('menu').hidden", timeout=900000)
        # the room models built in Blender (packs named toy_*) download after the menu is up: wait for them, or the
        # track would be exported with the simpler code-built stand-ins
        await pg.wait_for_function("__ev(`Object.keys(PROP_PACKS).filter(k=>k.startsWith('toy_')).every(k=>PROP_PACKS[k].b||PROP_PACKS[k].d)`)", timeout=900000)
        await pg.evaluate("__ev('window.CR_GLB_EMISSIVE=1')")
        await pg.evaluate('src=>__ev(src)', EXP)
        print('booted', round(time.time() - t0), 's', flush=True)
        await pg.evaluate("__ev(`qKey='%s';store.set('crust-q',qKey);applyQuality();applyLad(0,false);clsKey='medium';mode='single';introSkip=true;goRace(%d)`)" % (Q, MI))
        await pg.wait_for_function("document.getElementById('raceLd').hidden", timeout=1800000)
        await pg.evaluate("__ev(`try{endIntro();}catch(e){};state='paused';1`)")
        print('track loaded', round(time.time() - t0), 's', flush=True)
        d = json.loads(await pg.evaluate("__ev(`JSON.stringify(__exportData(10))`)"))
        nm = d['map']
        od = os.path.join(OUT, nm)
        os.makedirs(od, exist_ok=True)
        d['race'] = json.loads(await pg.evaluate("__ev(`JSON.stringify(__exportRace())`)"))
        # trees, palms, bushes and rocks: where they stand, and a copy of each shape (the PC draws finished ones)
        d['props'] = json.loads(await pg.evaluate("__ev(`JSON.stringify(__exportProps())`)"))
        print('props', {k: len(v) for k, v in d['props']['items'].items()}, flush=True)
        hz = json.loads(await pg.evaluate("__ev(`JSON.stringify(__exportHaz())`)"))
        d['haz'] = hz['data']
        d['mi'] = MI
        d['theme'] = await pg.evaluate("__ev('MAPS[mapIdx].theme')")
        d['grade'] = json.loads(await pg.evaluate("__ev(`JSON.stringify(POST.grade||{})`)"))
        d['rim'] = json.loads(await pg.evaluate("__ev(`JSON.stringify({c:'#'+rimL.color.getHexString(),i:rimL.intensity})`)"))
        # the Balloon Battle arena (web tools/mini/battle.js): the shapes that are its floor and walls, where the karts start,
        # the ramps the computer's drivers use and the mode's numbers, so the PC reads them and never carries its own copy.
        # The exported height map is the bare table (it samples groundAt, not battleG): the arena's ground is these shapes.
        if await pg.evaluate("__ev('!!MAPS[mapIdx].battle')"):
            d['battle'] = json.loads(await pg.evaluate("__ev(`JSON.stringify({shapes:BB.shapes,spawn:BB.spawn,ramps:BB.ramps,T:BB.T,step:BB_STEP,r:BB_R,x0:BB_X0,floor:BB_FLOOR,start:BB_START,back:BB_BACK,items:BB_ITEMS,col:BB_COL})`)"))
            print('battle', len(d['battle']['shapes']), 'shapes', len(d['battle']['spawn']), 'spawns', flush=True)
        open(os.path.join(od, nm + '_haz.glb'), 'wb').write(base64.b64decode(hz['b64']))
        # a small card for the track menu, so the game needn't read every track to list them
        info = json.loads(await pg.evaluate("__ev(`JSON.stringify({name:MAPS[mapIdx].name,theme:MAPS[mapIdx].theme,special:!!MAPS[mapIdx].special,battle:!!MAPS[mapIdx].battle,cup:MAPS[mapIdx].cup})`)"))
        info.update({'id': nm, 'mi': MI})
        json.dump(info, open(os.path.join(od, nm + '.info.json'), 'w'))
        json.dump(d, open(os.path.join(od, nm + '.json'), 'w'), separators=(',', ':'))
        print('data', nm, 'N', d['N'], 'boxes', len(d['race']['boxes']), 'loops', len(d['race']['loops']), 'haz', {k: (len(v) if isinstance(v, list) else bool(v)) for k, v in d['haz'].items()}, flush=True)
        t = json.loads(await pg.evaluate("n=>__ev('JSON.stringify(__exportTrack(\"'+n+'\"))')", nm))
        open(os.path.join(od, nm + '.gltf'), 'w').write(t['json'])
        open(os.path.join(od, nm + '.bin'), 'wb').write(base64.b64decode(t['bin']))
        td = os.path.join(od, nm + '_tex')
        os.makedirs(td, exist_ok=True)
        for f in t['files']:
            open(os.path.join(td, f['name']), 'wb').write(base64.b64decode(f['b64']))
        print('track', nm, t['stats'], round(time.time() - t0), 's', flush=True)
        print('errors', errs[:5], flush=True)
        await b.close()

asyncio.run(main())
