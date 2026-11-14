import asyncio, json, sys
from playwright.async_api import async_playwright
# for a room: along each wall, how far can a kart drive straight in from the wall before something stops it (floor level)?
# prints, per wall, the stretches (in the region's own measure) with at least 260 units clear and 30 units clear to each side
REG = sys.argv[1]
JS = r"""(()=>{const c=SB.col,b=c.b,out={};const clear=(x,z,nx,nz)=>{let d=24;for(;d<600;d+=6){if(sbBlocked(x-nx*d,z-nz*d,0))break;}return d;};
const walls={E:[b[1],0,1,0],W:[b[0],0,-1,0],N:[0,b[2],0,-1],S:[0,b[3],0,1]};const room=!!SB.reg.room;
for(const w in walls){const [wx,wz,nx,nz]=walls[w],res=[];const lo=(nx?b[2]:b[0])+40,hi=(nx?b[3]:b[1])-40;for(let t=lo;t<=hi;t+=12){const x=nx?wx:t,z=nx?t:wz;const d=Math.min(clear(x,z,nx,nz),clear(x+(nx?0:14),z+(nx?14:0),nx,nz),clear(x-(nx?0:14),z-(nx?14:0),nx,nz));
  const p=room?(nx?Math.round(-t/3.47):Math.round(t/3.47)):(nx?+(3.5-t/347).toFixed(2):+(t/347-.75).toFixed(2));res.push([p,d]);}
  /* runs of good places */const runs=[];let cur=null;for(const [p,d] of res){if(d>=200){if(!cur)cur={from:p,to:p,min:d};cur.to=p;cur.min=Math.min(cur.min,d);}else if(cur){runs.push(cur);cur=null;}}if(cur)runs.push(cur);out[w]=runs.map(r=>r.from+'..'+r.to+' ('+r.min+')');}
return out})()"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(channel='chromium', args=['--use-angle=d3d11','--enable-gpu','--ignore-gpu-blocklist','--enable-webgl'])
        ctx = await b.new_context(viewport={'width':960,'height':540}, service_workers='block'); pg = await ctx.new_page()
        await pg.goto('http://localhost:8771/webcopy6/index.html')
        await pg.wait_for_function("document.getElementById('menu')&&!document.getElementById('menu').hidden", timeout=600000)
        await pg.evaluate("__ev(`qKey='ultra';applyQuality();clsKey='medium';introSkip=true;document.querySelector('#modeSeg button[data-m=sb]').click();`)")
        await pg.wait_for_timeout(1500); await pg.evaluate("(a)=>{document.getElementById('map-'+a).click()}", REG); await pg.wait_for_timeout(3000)
        await pg.evaluate("__ev(`goRace(mapIdx)`)")
        await pg.wait_for_function("document.getElementById('raceLd').hidden", timeout=900000)
        for i in range(400):
            if await pg.evaluate("__ev(`state`)") == 'race': break
            await pg.wait_for_timeout(500)
        r = json.loads(await pg.evaluate("(js)=>__ev('JSON.stringify('+js+')')", JS))
        for w in r: print(REG, w, r[w])
        await b.close()
asyncio.run(main())
