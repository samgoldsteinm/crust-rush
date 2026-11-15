"""Sandbox, the web's answers for the PC to check itself against (tests/sbground.gd reads what this writes).

Serves a copy of the built web game, starts Sandbox on one map with an empty save (as tools/ciexport.py does), and asks the
page for its own ground and walls at a few hundred points: sbG(x, z, wy) and sbBlocked(x, z, wy) (web tools/mini/sandbox.js).
Each point: [x, z, height, sbG, sbBlocked, sbG with no height, kind of point, the page's own bare ground there].
The points: at random over the place at the ground's own level and at a random height, and along the lap on and beside the
track at the track's level. Also notes whether the page's sbExport() is the same as the one in the map's json (if it is not,
a difference found by the test is the export's, not the PC code's).
Usage: WEB=<built web game> MAPS=<maps folder> MI=<map index> [N=400] [Q=ultra] OUT=<file.json> python tools/sbground.py
"""
import asyncio, functools, http.server, json, os, re, threading
from playwright.async_api import async_playwright

WEB = os.environ.get('WEB', 'web')
MAPS = os.environ.get('MAPS', 'maps')
MI = int(os.environ.get('MI', '20'))
N = int(os.environ.get('N', '400'))
Q = os.environ.get('Q', 'ultra')
OUT = os.environ.get('OUT', 'sbground.json')
PORT = 8900 + MI

JS = r"""(()=>{const rnd=prng(90210+mapIdx),P=[],toy=SB.kind==='toy',gb=(x,z)=>toy?0:groundAt(x,z),c=SB.col;
 const ask=(x,z,wy,why)=>{x=+x.toFixed(2);z=+z.toFixed(2);wy=+wy.toFixed(2);P.push([x,z,wy,+sbG(x,z,wy).toFixed(3),sbBlocked(x,z,wy)?1:0,+sbG(x,z).toFixed(3),why,+gb(x,z).toFixed(3)]);};
 if(c){const b=c.b;for(let i=0;i<%d;i++){let x,z;if(SB.rim){const a=rnd()*6.28318,r=Math.sqrt(rnd())*(SB.rim+30);x=Math.cos(a)*r;z=Math.sin(a)*r;}else{x=b[0]-15+rnd()*(b[1]-b[0]+30);z=b[2]-15+rnd()*(b[3]-b[2]+30);}
   ask(x,z,gb(x,z),0);if(i%%3===0)ask(x,z,gb(x,z)+rnd()*c.cap,1);}}
 for(let i=0;i<%d;i++){const j=Math.floor(rnd()*N),p=track[j],lat=(rnd()*2-1)*(WALLD+30),al=(rnd()-.5)*T.L/N,x=p.x+p.nx*lat+p.tx*al,z=p.y+p.ny*lat+p.ty*al;ask(x,z,gb(x,z)+(p.ey||0),2);}
 for(const g of SB.gates){for(const d of [-30,-10,5,60,150])for(const l of [0,g.hw-2,g.hw+6]){const x=g.x+g.nx*d-g.nz*l,z=g.z+g.nz*d+g.nx*l;ask(x,z,g.y,3);}}
 const e=sbExport();return {id:SB.regId,kind:SB.kind,free:SBF,pts:P,gates:e.gates,col:e.col||null,coins:e.coins.length};})()"""


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


srv = http.server.ThreadingHTTPServer(('127.0.0.1', PORT), functools.partial(Quiet, directory=WEB))
threading.Thread(target=srv.serve_forever, daemon=True).start()


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--no-sandbox'])
        ctx = await b.new_context(viewport={'width': 1280, 'height': 720}, service_workers='block')
        pg = await ctx.new_page()
        errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:300]))

        async def route(r):
            if re.search(r'/js/game\.[0-9a-f]+\.js', r.request.url):
                resp = await r.fetch()
                body = (await resp.text()).replace('requestAnimationFrame(frame);\n})();', 'window.__ev=(x)=>eval(x);requestAnimationFrame(frame);\n})();')
                await r.fulfill(response=resp, body=body, headers={**resp.headers, 'cache-control': 'no-store'})
            else:
                await r.continue_()
        await pg.route('**/*', route)
        await pg.goto(f'http://127.0.0.1:{PORT}/index.html', wait_until='domcontentloaded', timeout=300000)
        await pg.wait_for_function("document.getElementById('menu')&&!document.getElementById('menu').hidden", timeout=900000)
        await pg.wait_for_function("__ev(`Object.keys(PROP_PACKS).filter(k=>k.startsWith('toy_')).every(k=>PROP_PACKS[k].b||PROP_PACKS[k].d)`)", timeout=900000)
        # the same road into Sandbox as the exporter takes: a race on the map first, then Sandbox on the same world
        await pg.evaluate("__ev(`qKey='%s';store.set('crust-q',qKey);applyQuality();applyLad(0,false);clsKey='medium';mode='single';introSkip=true;goRace(%d)`)" % (Q, MI))
        await pg.wait_for_function("document.getElementById('raceLd').hidden", timeout=1800000)
        await pg.evaluate("__ev(`try{endIntro();}catch(e){};state='paused';1`)")
        await pg.evaluate("__ev(`try{store.set('crust-sb','');}catch(e){};SB.save=null;SB.back=null;mode='sb';introSkip=true;goRace(%d);1`)" % MI)
        await pg.wait_for_function("__ev(`SBX&&!raceLoading&&SB.regId===MAPS[mapIdx].id`)", timeout=1800000)
        await pg.evaluate("__ev(`try{endIntro();}catch(e){};state='paused';1`)")
        r = json.loads(await pg.evaluate("(js)=>__ev('JSON.stringify('+js+')')", JS % (N, N // 2)))
        mj = os.path.join(MAPS, r['id'], r['id'] + '.json')
        same = None
        if os.path.exists(mj):
            sb = json.load(open(mj, encoding='utf-8')).get('sandbox') or {}
            mc = sb.get('col')
            same = (mc is None and r['col'] is None) or (mc is not None and r['col'] is not None and mc['sp'] == r['col']['sp'] and mc['cnt'] == r['col']['cnt'])
            gs = json.dumps(sb.get('gates')) == json.dumps(r['gates'])
            r['same_gates'] = gs
        r['same_export'] = same
        if r['col']:
            # (the session's own grid, kept beside the answers: to see where two sessions differ)
            json.dump(r['col'], open(OUT + '.col.json', 'w'), separators=(',', ':'))
            r['col'] = {'filled': r['col'].get('filled'), 'spans': r['col'].get('spans')}
        json.dump(r, open(OUT, 'w'), separators=(',', ':'))
        print('sbground', r['id'], r['kind'], 'points', len(r['pts']), 'export same as the map json:', same, 'gates same:', r.get('same_gates'), 'errors', errs[:3], flush=True)
        await b.close()

asyncio.run(main())
