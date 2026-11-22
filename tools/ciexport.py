"""Export one track of the web game for the PC build, on a GitHub runner.

Serves the published web game (a checkout of `main`), opens it in headless Chromium with a software GPU,
loads the track at the Ultra preset and runs tools/glbexport.js inside the page. Writes to OUT/<id>/:
  <id>.json      track data (centre line, walls, ramps, height maps, lights) + "race" (boxes, loops...) + "haz"
                 + "sandbox" (what the web's Sandbox worked out for the place: its walls as a grid of columns, its
                 gates, coins and flag; taken last, see below; not for the battle arena)
  <id>.info.json the menu's card; "sb" in it says the map is a Sandbox place and carries its lap for the world map
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
        # Since the web's v197 (three sets of balloons, then out; the bigger table): "sets" (BB_SETS), "X" and "Z" (BB_X, BB_Z:
        # half the table's length and width, for the computer drivers' grid), each spawn place with its heading, each ramp
        # with "lo", "hi" and its rectangle (BB.spawn and BB.ramps carry those as they are). A web build from before that
        # has no BB_SETS or BB_X: the three are then left out and the PC reads the table's size off the shapes.
        if await pg.evaluate("__ev('!!MAPS[mapIdx].battle')"):
            d['battle'] = json.loads(await pg.evaluate("__ev(`JSON.stringify(Object.assign({shapes:BB.shapes,spawn:BB.spawn,ramps:BB.ramps,T:BB.T,step:BB_STEP,r:BB_R,x0:BB_X0,floor:BB_FLOOR,start:BB_START,back:BB_BACK,items:BB_ITEMS,col:BB_COL},typeof BB_SETS==='undefined'?{}:{sets:BB_SETS,X:BB_X,Z:BB_Z}))`)"))
            print('battle', len(d['battle']['shapes']), 'shapes', len(d['battle']['spawn']), 'spawns', 'sets', d['battle'].get('sets'), 'table', d['battle'].get('X'), d['battle'].get('Z'), 'x0', d['battle'].get('x0'), flush=True)
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
        # Sandbox (web tools/mini/sandbox.js): the PC cannot read walls from what is drawn, so everything Sandbox works out for
        # this place is taken from the page itself (sbExport, web v196) and stored as d['sandbox']. It is taken LAST, after the
        # race data and the model are written: going into Sandbox adds its coins and arches to the scene and must not reach
        # either. The json is written a second time with the block in it; if anything here fails the first one stands.
        # The page's Sandbox save is emptied first, so the arches stand where a first visit puts them.
        sb_fail = False
        if not info.get('battle') and not info.get('special'):   # (a Special track, such as Apartment Run, is not in Sandbox)
            try:
                if not await pg.evaluate("__ev(`typeof sbExport==='function'&&!!sbRegOf(MAPS[mapIdx].id)`)"):
                    raise RuntimeError('this web build has no sbExport, or the map is not a Sandbox place')
                # On a pizza the rocks and bushes are in the way in the web's Sandbox, but this page was built without them
                # (glbexport.js keeps them out of the baked track: the PC draws its own). For this last step the world is
                # built once more with them in, so the walls read from what is drawn are the walls a player of the web meets.
                kind = await pg.evaluate("__ev(`sbRegOf(MAPS[mapIdx].id).kind||'toy'`)")
                if kind == 'open' and any(len(v) for v in d['props']['items'].values()):
                    await pg.evaluate("__ev(`window.__hdPropsOff=true;loadMap(%d,false);resetRace(true);1`)" % MI)
                    await pg.wait_for_timeout(1500)
                    print('sandbox: the world built again with its rocks and bushes', round(time.time() - t0), 's', flush=True)
                await pg.evaluate("__ev(`try{store.set('crust-sb','');}catch(e){};SB.save=null;SB.back=null;mode='sb';introSkip=true;goRace(%d);1`)" % MI)
                await pg.wait_for_function("__ev(`SBX&&!raceLoading&&SB.regId===MAPS[mapIdx].id`)", timeout=1800000)
                await pg.evaluate("__ev(`try{endIntro();}catch(e){};state='paused';1`)")
                # (two things sbExport does not carry and the PC needs: the water level of a pizza, null where there is none,
                #  and the number of lap points the page had, to be sure the block belongs to this lap)
                sb = json.loads(await pg.evaluate("__ev(`JSON.stringify(Object.assign({},sbExport(),{water:WATER_Y==null?null:WATER_Y,N:N,multi:!!MULTI}))`)"))
                if sb.get('id') != nm or sb.get('N') != d['N']:
                    raise RuntimeError('the Sandbox block is for another place: %s N %s' % (sb.get('id'), sb.get('N')))
                d['sandbox'] = sb
                json.dump(d, open(os.path.join(od, nm + '.json'), 'w'), separators=(',', ':'))
                # the menu's card: the kind of place, and the lap as a short line for the world map (so the map screen
                # can draw every installed place without reading every track)
                st = max(1, len(d['track']) // 260)
                info['sb'] = {'kind': sb['kind'], 'name': sb['name'], 'R': d['R'], 'start': [d['track'][0][0], d['track'][0][1]],
                              'lap': [[round(p[0], 1), round(p[1], 1)] for p in d['track'][::st]]}
                json.dump(info, open(os.path.join(od, nm + '.info.json'), 'w'))
                col = sb.get('col') or {}
                print('sandbox', nm, sb['kind'], 'gates', len(sb['gates']), 'coins', len(sb['coins']), 'cells', col.get('filled', 0), 'spans', col.get('spans', 0),
                      'bytes', len(json.dumps(sb, separators=(',', ':'))), round(time.time() - t0), 's', flush=True)
            except Exception as e:
                print('sandbox: NOT exported for', nm, str(e)[:300], flush=True)
                sb_fail = True
        print('errors', errs[:5], flush=True)
        await b.close()
        # a place without its Sandbox block would be missing from the PC's world, and nobody would see why: the run fails (the
        # track's files are written and stand, but the workflow stops before attaching them, and tools/release_pc.py builds nothing)
        if sb_fail: sys.exit(3)

asyncio.run(main())
