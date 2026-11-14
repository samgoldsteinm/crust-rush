import asyncio, json, sys
from playwright.async_api import async_playwright
# Kitchen Chaos, a normal race: what could stop a kart on the climb (lap 0.78 .. 0.98)? Lists the obstacles, ramps and side limits there,
# then drives the player's kart up the climb in several lanes and reports every place it loses speed for no visible reason.
MAP = sys.argv[1] if len(sys.argv) > 1 else 'kitchen'; F0 = float(sys.argv[2]) if len(sys.argv) > 2 else .78; F1 = float(sys.argv[3]) if len(sys.argv) > 3 else .985
JS = r"""(()=>{const out={N:N,W:WALLD,RW:RW};const inR=j=>{const f=j/N;return f>=%F0%&&f<=%F1%;};
out.obstacles=obstacles.map(o=>{let bj=0,bd=1e18;for(let j=0;j<N;j++){const p=track[j],d=(p.x-o.x)**2+(p.y-o.y)**2;if(d<bd){bd=d;bj=j;}}const p=track[bj];return {lap:+(bj/N).toFixed(3),lat:Math.round((o.x-p.x)*p.nx+(o.y-p.y)*p.ny),r:Math.round(o.r),h:Math.round(o.h),at:[Math.round(o.x),Math.round(o.y)]};}).filter(o=>Math.abs(o.lat)<WALLD+20);
out.ramps=ramps.map(r=>({lap:+(r.j/N).toFixed(3),len:Math.round(r.len),w:Math.round(r.w),h:r.h}));
out.flo=[];for(let j=0;j<N;j++){const p=track[j];if(p.flo!==undefined&&inR(j)&&(out.flo.length===0||j-out.flo[out.flo.length-1].j>6))out.flo.push({j,lap:+(j/N).toFixed(3),flo:Math.round(p.flo),fhi:Math.round(p.fhi)});}
out.walls=[];for(let j=0;j<N;j++){const p=track[j];if(inR(j)&&(p.wall||p.pond||p.open))out.walls.push([j,p.wall,p.pond,p.open]);}
out.shorts=SHORTS.map(s=>({a:+(s.a/N).toFixed(3),b:+(s.b/N).toFixed(3),s:s.s,w:s.w,route:!!s.route}));out.loops=LOOPS.map(L=>({lap:+(L.j/N).toFixed(3),full:!!L.full}));
out.stops=[];const k=player;k.auto=false;for(const lat of [-40,-24,-8,8,24,40]){const j0=Math.round(%F0%*N),p=track[j0];k.x=k.px=p.x+p.nx*lat;k.y=k.py=p.y+p.ny*lat;k.idx=j0;k.prog=j0;k.a=k.ma=k.pa=k.pma=Math.atan2(p.ty,p.tx);k.speed=60;k.wy=k.pwy=k.lastG=kGround(k);k.wvy=0;k.gRate=0;k.air=false;k.loop=null;k.sc=null;k.spin=0;k.inv=9;let was=0;
 for(let i=0;i<4000;i++){/* hold the lane: steer toward the point ahead at this offset */const q=track[(k.idx+8)%N],want=Math.atan2(q.y+q.ny*lat-k.y,q.x+q.nx*lat-k.x);if(!k.loop){k.a+=angDiff(want,k.a)*.3;k.ma=k.a;}const sp0=k.speed,x0=k.x,y0=k.y;update(STEP);
  if(k.idx/N>%F1%)break;if(k.speed<sp0-12&&k.spin<=0&&!k.loop){const pj=track[k.idx];out.stops.push({lane:lat,lap:+(k.idx/N).toFixed(3),at:[Math.round(k.x),Math.round(k.y)],wy:Math.round(k.wy),lat:Math.round((k.x-pj.x)*pj.nx+(k.y-pj.y)*pj.ny),speed:[Math.round(sp0),Math.round(k.speed)],air:k.air,onRamp:k.onRamp,sc:!!k.sc});if(out.stops.length>14)break;}}}
return out})()""".replace('%F0%', str(F0)).replace('%F1%', str(F1))
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(channel='chromium', args=['--use-angle=d3d11','--enable-gpu','--ignore-gpu-blocklist','--enable-webgl'])
        ctx = await b.new_context(viewport={'width':960,'height':540}, service_workers='block'); pg = await ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto('http://localhost:8771/webcopy6/index.html')
        await pg.wait_for_function("document.getElementById('menu')&&!document.getElementById('menu').hidden", timeout=600000)
        await pg.evaluate("(a)=>__ev(`qKey='fast';applyQuality();clsKey='medium';mode='single';introSkip=true;goRace(MAPS.findIndex(m=>m.id==='${a}'))`)", MAP)
        await pg.wait_for_function("document.getElementById('raceLd').hidden", timeout=900000)
        for i in range(400):
            if await pg.evaluate("__ev(`state`)") == 'race': break
            await pg.wait_for_timeout(500)
        r = json.loads(await pg.evaluate("(js)=>__ev('JSON.stringify('+js+')')", JS))
        for k in r: print(k, json.dumps(r[k])[:900])
        print('errors', errs[:3]); await b.close()
asyncio.run(main())
