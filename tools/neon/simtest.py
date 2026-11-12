import asyncio, json, sys
from playwright.async_api import async_playwright
MAP = sys.argv[1] if len(sys.argv) > 1 else 'laser'
CLS = sys.argv[2] if len(sys.argv) > 2 else 'medium'
SECS = int(sys.argv[3]) if len(sys.argv) > 3 else 330
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width':640,'height':360}, service_workers='block')
        pg = await ctx.new_page()
        errs=[]
        pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        pg.on('console', lambda m: errs.append('console:'+m.text[:300]) if m.type in ('error','warning') and 'GPU' not in m.text and 'WebGL' not in m.text else None)
        await pg.goto('http://localhost:8771/webcopy6/index.html')
        await pg.wait_for_function("document.getElementById('menu')&&!document.getElementById('menu').hidden", timeout=600000)
        await pg.evaluate("(a)=>__ev(`qKey='fast';applyQuality();clsKey='${a[1]}';mode='single';introSkip=true;goRace(MAPS.findIndex(m=>m.id==='${a[0]}'))`)", [MAP, CLS])
        await pg.wait_for_function("document.getElementById('raceLd').hidden", timeout=900000)
        for i in range(400):
            st = await pg.evaluate("__ev(`state`)")
            if st=='race': break
            await pg.wait_for_timeout(500)
        info = await pg.evaluate("""__ev(`JSON.stringify({N,L:Math.round(T.L),MULTI,rev:curRev,glide:GLIDE?{j0:GLIDE.j0,j1:GLIDE.j1,long:GLIDE.long,y0:GLIDE.y0,y1:GLIDE.y1,L:Math.round(GLIDE.L)}:null,shorts:SHORTS.map(s=>({a:s.a,b:s.b,s:s.s,L:Math.round(s.L),save:Math.round(s.save)})),pads:pads.length,ramps:ramps.length,boxes:boxes.length,obst:obstacles.length,karts:karts.length})`)""")
        print('info', info, flush=True)
        # fast-forward: the player drives itself; a short summary at the end
        await pg.evaluate("__ev(`player.auto=true;window.__st={gl:0,resp:0,sc:{},laps:[],stuck:[],spins:0,fall:0};window.__lp=karts.map(()=>0);window.__sp=karts.map(k=>[k.idx,0]);window.__ff=(sec)=>{const n=Math.round(sec/STEP);for(let i=0;i<n;i++){update(STEP);karts.forEach((k,ki)=>{if(k.glide&&!k._g)__st.gl++;k._g=k.glide;if(k.sc&&!k._s)__st.sc[ki]=(__st.sc[ki]||0)+1;k._s=k.sc;if((k.lap|0)!==__lp[ki]){__lp[ki]=k.lap|0;if(ki===0)__st.laps.push(+simTime.toFixed(1));}const q=__sp[ki];if(k.idx!==q[0]){q[0]=k.idx;q[1]=0;}else if(!k.finished&&!(k.spin>0)){q[1]+=STEP;if(q[1]>6){__st.stuck.push([ki,k.idx,+simTime.toFixed(0)]);q[1]=-30;}}});}return JSON.stringify({t:+simTime.toFixed(1),state,fin:karts.filter(k=>k.finished).length});}`)")
        for i in range(SECS // 10):
            r = json.loads(await pg.evaluate("__ev(`__ff(10)`)"))
            if len(sys.argv) > 4: print(r, flush=True)
            if r['state'] not in ('race','results','finish') or r['fin'] >= 8: break
        print('end', r, await pg.evaluate("__ev(`JSON.stringify({st:__st,k:karts.map(k=>[k.lap|0,k.idx,k.finished?1:0])})`)"), flush=True)
        print('errors', errs[:8])
        await b.close()
asyncio.run(main())
