"""Sandbox, two things a lap test does not see:   py.cmd tools/neon/sbfall.py [region]   (default backyard)
  smooth   the kart held 28 units left, then right, of the middle up the highest climb: the biggest jolt in its height from one step to the
           next (the change in the change). A smooth ramp gives well under 0.5; the fault fixed in web v192 gave about 0.7 at every lap point.
  drop     driven off the highest part of the track, in real time, three times: in every frame of the fall is the kart in the picture
           (its place on the screen, -1..1 each way) and how far is the camera above or below it? Pictures scratch/sbfall_<try>_<frame>.png.
Want: jolt < 0.5; the kart on screen (|x| < 0.9, -0.8 < y < 0.9) in every frame of every drop."""
import asyncio, json, sys
from playwright.async_api import async_playwright
REG = sys.argv[1] if len(sys.argv) > 1 else 'backyard'; SP = 'D:/crust-rush/scratch'
SMOOTH = r"""(()=>{let top=0,jt=0;for(let j=0;j<N;j++)if((track[j].ey||0)>top){top=track[j].ey;jt=j;}const out={};
for(const lat of [-28,28]){/* start 260 lap points before the top: the climb */const j0=(jt-Math.round(620/(T.L/N))+N)%N,p=track[j0],k=player;k.x=k.px=p.x+p.nx*lat;k.y=k.py=p.y+p.ny*lat;k.idx=j0;k.a=k.ma=k.pa=k.pma=Math.atan2(p.ty,p.tx);k.speed=120;k.wy=k.pwy=k.lastG=sbG(k.x,k.y,(p.ey||0)+2);k.wvy=0;k.gRate=0;k.air=false;k.loop=null;k.bpx=k.x;k.bpy=k.y;
 let a=k.wy,b=k.wy,worst=0,n=0,airs=0;for(let i=0;i<2500;i++){const q=track[(k.idx+7)%N],want=Math.atan2(q.y+q.ny*lat-k.y,q.x+q.nx*lat-k.x);k.a+=angDiff(want,k.a)*.3;k.ma=k.a;update(STEP);if(k.air){airs++;a=b=k.wy;continue;}const d2=Math.abs(k.wy-2*b+a);if(i>5&&d2<4)worst=Math.max(worst,d2);a=b;b=k.wy;n++;let d=k.idx-jt;if(d>N/2)d-=N;if(d>-6)break;}
 out[lat]={jolt:+worst.toFixed(3),steps:n,airSteps:airs,reached:Math.round(k.wy)};}return out})()"""
DROP = r"""(()=>{let top=0,jt=0;for(let j=0;j<N;j++)if((track[j].ey||0)>top){top=track[j].ey;jt=j;}const j=(jt-%OFF%+N)%N,p=track[j],q=track[(j+14)%N],sd=((q.x-p.x)*p.nx+(q.y-p.y)*p.ny)>0?-1:1,k=player;
k.x=k.px=p.x;k.y=k.py=p.y;k.idx=j;k.wy=k.pwy=k.lastG=p.ey||0;k.air=false;k.wvy=0;k.gRate=0;k.loop=null;k.speed=%SP%;const out=Math.atan2(p.ny*sd+p.ty*.4,p.nx*sd+p.tx*.4);k.a=k.ma=k.pa=k.pma=out;k.bpx=k.x;k.bpy=k.y;cam.a=out;camSnap=true;window.__hold=out;return Math.round(p.ey||0)})()"""
FRAME = r"""(()=>{const k=player;if(window.__hold!=null&&!k.sbOff===false){}const v=new THREE.Vector3(k.rx,k.rz+4,k.ry).project(camera);return {sx:+v.x.toFixed(2),sy:+v.y.toFixed(2),behind:v.z>1,h:Math.round(k.wy),air:k.air,camAbove:Math.round(camera.position.y-k.rz),dist:Math.round(Math.hypot(camera.position.x-k.rx,camera.position.z-k.ry))}})()"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(channel='chromium', args=['--use-angle=d3d11','--enable-gpu','--ignore-gpu-blocklist','--enable-webgl'])
        ctx = await b.new_context(viewport={'width':1280,'height':720}, service_workers='block'); pg = await ctx.new_page(); errs = []; bad = 0
        pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        ev = lambda s: pg.evaluate("(js)=>__ev('JSON.stringify('+js+')')", s)
        await pg.goto('http://localhost:8771/webcopy6/index.html')
        await pg.wait_for_function("document.getElementById('menu')&&!document.getElementById('menu').hidden", timeout=600000)
        await pg.evaluate("__ev(`qKey='fast';applyQuality();clsKey='medium';introSkip=true;document.querySelector('#modeSeg button[data-m=sb]').click();`)")
        await pg.wait_for_timeout(1500); await pg.evaluate("(a)=>{document.getElementById('map-'+a).click()}", REG); await pg.wait_for_timeout(3000)
        await pg.evaluate("__ev(`goRace(mapIdx)`)")
        await pg.wait_for_function("document.getElementById('raceLd').hidden", timeout=900000)
        for i in range(400):
            if await pg.evaluate("__ev(`state`)") == 'race': break
            await pg.wait_for_timeout(500)
        r = json.loads(await ev(SMOOTH)); ok = all(v['jolt'] < .5 for v in r.values()); bad += not ok
        print(('ok   ' if ok else 'FAIL ') + 'smooth: up the highest climb, 28 units either side of the middle', r, flush=True)
        for t, (off, sp) in enumerate([(30, 120), (90, 170), (150, 90)]):
            h0 = json.loads(await ev(DROP.replace('%OFF%', str(off)).replace('%SP%', str(sp))))
            frames = []
            for f in range(14):
                await pg.wait_for_timeout(140); fr = json.loads(await ev(FRAME)); frames.append(fr)
                if f in (1, 4, 7, 10): await pg.screenshot(path=f'{SP}/sbfall_{t}_{f}.png')
            falling = [f for f in frames if f['air'] or f['h'] > 12]
            ok = len(falling) > 0 and all((not f['behind']) and abs(f['sx']) < .9 and -.8 < f['sy'] < .9 for f in frames)
            bad += not ok
            print(('ok   ' if ok else 'FAIL ') + f'drop {t}: from height {h0}', [(f['h'], f['sx'], f['sy'], f['camAbove']) for f in frames], flush=True)
        print('errors', errs[:4]); print('SANDBOX FALL TEST', 'FAILED' if bad or errs else 'passed'); await b.close()
asyncio.run(main())
