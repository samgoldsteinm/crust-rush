"""Retake a track's menu pictures on this PC (the same camera places as godot/tools/cishots.py, which does it on a GitHub runner), and
keep, for each of the three pictures a track has (h the start grid, m a place on the lap, a from the air), the new one that looks most
like the picture it has now: the same viewpoint, the scenery as it is today.
Usage: MI=<map index> py.cmd tools/neon/mapshots.py      (serves D:/crust-rush/app, so build first with webtest.py)
Out: D:/crust-rush/scratch/mapshots/<id>-<h|m|a>.jpg (the kept three) and all/<id>-<name>.jpg (every candidate).
then: py.cmd tools/neon/embed_shots.py D:/crust-rush/scratch/mapshots
"""
import asyncio, functools, http.server, io, json, os, re, threading, time
from playwright.async_api import async_playwright
from PIL import Image

WEB = os.environ.get('WEB', 'D:/crust-rush/app')
KEEP = 'D:/crust-rush/scratch/mapshots'
OUT = KEEP + '/all'
OLD = 'D:/crust-rush/source/data/shots'
MI = int(os.environ.get('MI', '1'))
Q = os.environ.get('Q', 'ultra')
SCALE = float(os.environ.get('SCALE', '2'))
PORT = 8865 + MI

# extra camera places for some tracks: name -> [fraction of the lap, back, up, points ahead, to the side]
EXTRA = {
    'laser': {'m6': [.262, 150, 70, 60, 0], 'm7': [.33, 40, 150, 30, 260], 'm8': [.70, 60, 46, 40, 0], 'm9': [.385, 120, 60, 40, -40]},
    'holo': {'m6': [.20, 200, 120, 80, -260], 'm7': [.47, 60, 60, 40, -60], 'm8': [.61, 40, 46, 40, 0], 'm9': [.33, 60, 50, 50, 0]},
    'synth': {'m6': [.585, 60, 44, 40, 0], 'm7': [.40, 160, 90, 70, 200], 'm8': [.47, 80, 50, 50, 0], 'm9': [.88, 120, 70, 50, -150]},
    'spiral': {'m6': [.30, 220, 150, 60, 300], 'm7': [.55, 220, 150, 60, -300]},
    'grid': {'m6': [.25, 160, 90, 70, -200], 'm7': [.6, 160, 90, 70, 200]},
}


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


srv = http.server.ThreadingHTTPServer(('127.0.0.1', PORT), functools.partial(Quiet, directory=WEB))
threading.Thread(target=srv.serve_forever, daemon=True).start()

RIG = r"""(()=>{
  window.__cam=null;window.__fr=0;const R0=renderer.render.bind(renderer);
  renderer.render=(s,c)=>{if(c===camera&&window.__cam){const q=window.__cam;if(Math.abs(camera.fov-q[6])>.01){camera.fov=q[6];camera.updateProjectionMatrix();}camera.up.set(0,1,0);camera.position.set(q[0],q[1],q[2]);camera.lookAt(q[3],q[4],q[5]);camera.updateMatrixWorld(true);try{snapSun(q[3],q[4],q[5]);}catch(e){}window.__fr++;}R0(s,c);};
  try{LODF=1e5;}catch(e){}
  const gy=(x,z)=>{try{return groundAt(x,z);}catch(e){return 0;}};
  /* a view along the road: from `back` units behind point j, `up` above the road and `lat` to the side, looking `ahead` points on */
  window.__camJ=(j,back,up,ahead,lat,fov)=>{j=((Math.round(j)%N)+N)%N;const p=track[j],q=track[(j+ahead+N)%N],l=lat||0,x=p.x-p.tx*back+p.nx*l,z=p.y-p.ty*back+p.ny*l;
    return [x,Math.max(gy(x,z)+6,gy(p.x,p.y)+(p.ey||0)+up),z,q.x,gy(q.x,q.y)+(q.ey||0)+5,q.y,fov||58];};
  /* from the air: the whole lap from one side */
  window.__camA=(az,el,k)=>{let x0=1e9,x1=-1e9,z0=1e9,z1=-1e9;for(const p of track){x0=Math.min(x0,p.x);x1=Math.max(x1,p.x);z0=Math.min(z0,p.y);z1=Math.max(z1,p.y);}const cx=(x0+x1)/2,cz=(z0+z1)/2,r=Math.max(x1-x0,z1-z0)/2,d=r*k;
    return [cx+Math.cos(az)*Math.cos(el)*d,Math.sin(el)*d,cz+Math.sin(az)*Math.cos(el)*d,cx,0,cz,50];};
  document.querySelectorAll('body *').forEach(e=>{if(e.tagName!=='CANVAS'&&!e.querySelector('canvas'))e.style.visibility='hidden';});
  return JSON.stringify({id:MAPS[mapIdx].id,N});})()"""


async def main():
    t0 = time.time()
    os.makedirs(OUT, exist_ok=True)
    async with async_playwright() as p:
        b = await p.chromium.launch(channel='chromium', args=['--use-angle=d3d11', '--enable-gpu', '--ignore-gpu-blocklist', '--enable-webgl'])
        ctx = await b.new_context(viewport={'width': 1280, 'height': 720}, device_scale_factor=SCALE, service_workers='block')
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
        await pg.wait_for_function("document.getElementById('menu')&&!document.getElementById('menu').hidden", timeout=1800000)
        print('booted', round(time.time() - t0), 's', flush=True)
        await pg.evaluate("__ev(`qKey='%s';store.set('crust-q',qKey);applyQuality();applyLad(0,false);clsKey='medium';mode='single';introSkip=true;goRace(%d)`)" % (Q, MI))
        await pg.wait_for_function("document.getElementById('raceLd').hidden", timeout=2400000)
        # everyone stays on the grid: the race never starts
        await pg.evaluate("__ev(`try{endIntro();}catch(e){};state='countdown';cd=1e9;1`)")
        info = json.loads(await pg.evaluate("__ev(%s)" % json.dumps(RIG)))
        mid, N = info['id'], info['N']
        print('track loaded', mid, N, round(time.time() - t0), 's', flush=True)
        shots = [('h0', f"__camJ({N - 24},70,30,25,0)"), ('h1', f"__camJ({N - 20},90,44,30,34)")]
        for i, f in enumerate([.12, .27, .42, .57, .72, .87]):
            shots.append((f'm{i}', f"__camJ({f}*N,70,36,45,0)"))
        for nm, q in EXTRA.get(mid, {}).items():
            shots.append((nm, f"__camJ({q[0]}*N,{q[1]},{q[2]},{q[3]},{q[4]})"))
        shots += [("a0", "__camA(.9,.62,1.35)"), ("a1", "__camA(4.0,.5,1.3)")]
        only = [x for x in os.environ.get('ONLY', '').split(',') if x]
        if only:
            shots = [q for q in shots if q[0] in only]
        for nm, js in shots:
            f0 = await pg.evaluate("(js)=>__ev(`window.__cam=${js};window.__fr`)", js)
            try:
                await pg.wait_for_function("(f)=>window.__fr>=f+3", arg=f0, timeout=900000)
            except Exception as e:
                print('slow frame', nm, str(e)[:80], flush=True)
            png = await pg.screenshot(type='png', timeout=900000)
            im = Image.open(io.BytesIO(png)).convert('RGB')
            if im.size != (1280, 720):
                im = im.resize((1280, 720), Image.LANCZOS)
            im.save(os.path.join(OUT, f'{mid}-{nm}.jpg'), quality=90, optimize=True)
            print('shot', nm, round(time.time() - t0), 's', flush=True)
        print('errors', errs[:5], flush=True)
        await b.close()
        # for each of the track's three pictures: the candidate nearest the picture it has now
        import numpy as np
        small = lambda path: np.asarray(Image.open(path).convert('L').resize((64, 36), Image.BILINEAR)).astype(np.float32)
        for k in 'hma':
            old = os.path.join(OLD, f'{mid}-{k}.jpg'); cands = [nm for nm, _ in shots if nm[0] == k]
            if not cands: continue
            if os.path.exists(old):
                o = small(old); o -= o.mean(); best = min(cands, key=lambda nm: float((((lambda c: c - c.mean())(small(os.path.join(OUT, f'{mid}-{nm}.jpg'))) - o) ** 2).mean()))
            else: best = cands[0]
            Image.open(os.path.join(OUT, f'{mid}-{best}.jpg')).save(os.path.join(KEEP, f'{mid}-{k}.jpg'), quality=88, optimize=True)
            print('keep', k, '=', best, flush=True)

asyncio.run(main())
