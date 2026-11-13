"""Item boxes against the starting grid, on every map and both ways round (builds each layout directly, about a minute).
usage: py.cmd tools/neon/boxcheck.py      Fails if a fixed box row lies within 56 track points before the start line or 44 after it."""
import asyncio, json, sys
from playwright.async_api import async_playwright
OUT = 'D:/crust-rush/scratch/boxcheck.json'
Q = """(a)=>__ev(`JSON.stringify((()=>{const mi=${a[0]},rev=${a[1]};loadMap(mi,!!rev);const m=MAPS[mi],sp=T.L/N,toyG=!!m.toy,slots=[];for(let s=0;s<12;s++){const back=toyG?5+s*2:5+s*3,idx=(N-back)%N,p=track[idx],lat=toyG?(s%2?1:-1)*RW*.42:[-30,-10,10,30][s%4]*LS;slots.push([p.x+p.nx*lat,p.y+p.ny*lat,idx]);}
  const rows=boxes.map(b=>{let bj=-1,bd=1e9;for(let i=0;i<N;i++){const p=track[i],d=(p.x-b.x)**2+(p.y-b.y)**2+((b.gy-groundAt(b.x,b.y))-(p.ey||0))**2;if(d<bd){bd=d;bj=i;}}
    let md=1e9;for(const s of slots.slice(0,8))md=Math.min(md,Math.hypot(s[0]-b.x,s[1]-b.y));return {j:bj,d:bj>N/2?bj-N:bj,grid:Math.round(md),air:b.air?1:0,train:b.trainCar||0};});
  return {id:m.id,N,sp:+sp.toFixed(2),rev:!!curRev,neon:!!m.neon,toy:!!m.toy,def:m.boxes||null,loops:LOOPS.map(L=>L.j),rows};})())`)"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(channel='chromium', args=['--use-angle=d3d11','--enable-gpu','--ignore-gpu-blocklist','--enable-webgl'])
        ctx = await b.new_context(viewport={'width':640,'height':360}, service_workers='block')
        pg = await ctx.new_page(); errs=[]
        pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        await pg.goto('http://localhost:8771/webcopy6/index.html')
        await pg.wait_for_function("document.getElementById('menu')&&!document.getElementById('menu').hidden", timeout=600000)
        await pg.evaluate("__ev(`qKey='fast';applyQuality();1`)")
        n = await pg.evaluate("__ev(`MAPS.length`)")
        res=[]
        for rev in (0,1):
            for i in range(n):
                try:
                    r = json.loads(await pg.evaluate(Q, [i, rev])); r['cls']='rev' if rev else 'fwd'; res.append(r)
                except Exception as e:
                    print('FAIL', rev, i, str(e)[:300], flush=True)
                json.dump(res, open(OUT,'w'))
        await b.close()
    bad = 0; closest = 1e9
    for r in res:
        rows = [(x['d'], x['grid']) for x in r['rows'] if not x['air'] and not x['train']]
        zone = sorted(set(d for d, g in rows if -56 <= d <= 44)); closest = min([closest] + [g for d, g in rows])
        if zone: bad += 1; print('IN START ZONE', r['cls'], r['id'], zone)
    print(len(res), 'layouts checked;', bad, 'with a box row in the start zone; closest box to a grid position:', closest, 'units')
    sys.exit(1 if bad else 0)
asyncio.run(main())
