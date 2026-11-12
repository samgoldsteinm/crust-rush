import asyncio, json, sys
from playwright.async_api import async_playwright
# usage: shots.py <map> <tag> <quality> "px,py,pz,tx,ty,tz;..."   (world coords: x, height, z)   or "j:<idx>,<back>,<up>,<ahead>[,<lat>]" for a view along the road
MAP, TAG, Q, CAMS = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
REV = len(sys.argv) > 5 and sys.argv[5] == 'rev'
SP='/tmp/claude-0/-home-claude/009aa3b6-e96f-505b-b230-9e07dd3a3292/scratchpad'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        import os
        VW,VH=[int(v) for v in os.environ.get('VP','960x540').split('x')]
        ctx = await b.new_context(viewport={'width':VW,'height':VH}, service_workers='block')
        pg = await ctx.new_page()
        errs=[]
        pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto('http://localhost:8771/webcopy6/index.html')
        await pg.wait_for_function("document.getElementById('menu')&&!document.getElementById('menu').hidden", timeout=600000)
        await pg.evaluate("(a)=>__ev(`qKey='${a[1]}';applyQuality();clsKey='${a[2]}';mode='single';introSkip=true;goRace(MAPS.findIndex(m=>m.id==='${a[0]}'))`)", [MAP, Q, 'reverse' if REV else 'medium'])
        await pg.wait_for_function("document.getElementById('raceLd').hidden", timeout=900000)
        if os.environ.get('HOLD'):
            await pg.evaluate("__ev(`try{endIntro();}catch(e){};state='countdown';cd=1e9;1`)")
        else:
          for i in range(400):
            st = await pg.evaluate("__ev(`state`)")
            if st=='race': break
            await pg.wait_for_timeout(500)
        await pg.evaluate("""__ev(`cd=1e6;window.__cam=null;const R0=renderer.render.bind(renderer);renderer.render=(s,c)=>{if(c===camera&&window.__cam){const q=window.__cam;camera.position.set(q[0],q[1],q[2]);camera.lookAt(q[3],q[4],q[5]);camera.updateMatrixWorld(true);}R0(s,c);};
          window.__camJ=(j,back,up,ahead,lat)=>{j=((j%N)+N)%N;const p=track[j],q=track[(j+ahead)%N],l=lat||0;return [p.x-p.tx*back+p.nx*l,(p.ey||0)+up,p.y-p.ty*back+p.ny*l,q.x,(q.ey||0)+4,q.y];};
          document.querySelectorAll('body *').forEach(e=>{if(e.tagName!=='CANVAS'&&!e.querySelector('canvas'))e.style.visibility='hidden';});`)""")
        for i, c in enumerate(CAMS.split(';')):
            if c.startswith('s:'):
                a = c[2:].split(',')
                await pg.evaluate("(a)=>__ev(`(()=>{const P=SHORTS[${a[0]}].pts,p=P[${a[1]}],q=P[Math.min(P.length-1,${a[1]}+14)];window.__cam=[p.x-p.tx*${a[2]},${a[3]},p.y-p.ty*${a[2]},q.x,4,q.y];})()`)", a)
            elif c.startswith('j:'):
                a = c[2:].split(',')
                await pg.evaluate("(a)=>__ev(`window.__cam=__camJ(${a.join(',')})`)", a)
            else:
                await pg.evaluate("(c)=>__ev(`window.__cam=[${c}]`)", c)
            await pg.wait_for_timeout(2500)
            await pg.screenshot(path=f'{SP}/neon_{TAG}_{i}.png', timeout=900000)
            print('shot', i, flush=True)
        print('errors', errs[:5])
        await b.close()
asyncio.run(main())
