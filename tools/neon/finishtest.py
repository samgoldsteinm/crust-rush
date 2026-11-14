"""Where does a race end, measured against the start/finish line?   py.cmd tools/neon/finishtest.py <map> [<map> ...]
Runs a race with the player's kart self-driving and, at the step each kart is marked finished, records how far it is past the line
(track point 0; minus = it has not reached the line yet), in game units. Also where the karts stood at the start, and where the game
draws the line. Want: every kart finishes at or just past the line (0 .. about one step of travel, 3 units), never before it."""
import asyncio, json, sys
from playwright.async_api import async_playwright
MAPS = sys.argv[1:] or ['margherita']
JS = r"""(()=>{const p0=track[0],al=k=>(k.x-p0.x)*p0.tx+(k.y-p0.y)*p0.ty,out={N:N,laps:LAPS,step:+(T.L/N).toFixed(2),grid:karts.map(k=>Math.round(al(k))),prog0:karts.map(k=>k.prog),idx0:karts.map(k=>k.idx),fin:[]};
const seen=new Set();player.auto=true;for(let i=0;i<120*900&&seen.size<karts.length;i++){const pre=karts.map(k=>[k.x,k.y]);update(STEP);for(let q=0;q<karts.length;q++){const k=karts[q];if(k.finished&&!seen.has(k)){seen.add(k);const a=al(k),ap=(pre[q][0]-p0.x)*p0.tx+(pre[q][1]-p0.y)*p0.ty;out.fin.push({pastLine:+a.toFixed(1),stepBefore:+ap.toFixed(1),idx:k.idx,prog:k.prog,need:LAPS*N,speed:Math.round(k.speed),lat:Math.round((k.x-p0.x)*p0.nx+(k.y-p0.y)*p0.ny)});}}if(state!=='race'&&state!=='countdown')break;}
out.t=+raceTime.toFixed(1);return out})()"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(channel='chromium', args=['--use-angle=d3d11','--enable-gpu','--ignore-gpu-blocklist','--enable-webgl'])
        for mp in MAPS:
            ctx = await b.new_context(viewport={'width':960,'height':540}, service_workers='block'); pg = await ctx.new_page()
            await pg.goto('http://localhost:8771/webcopy6/index.html')
            await pg.wait_for_function("document.getElementById('menu')&&!document.getElementById('menu').hidden", timeout=600000)
            await pg.evaluate("(a)=>__ev(`qKey='fast';applyQuality();clsKey='medium';mode='single';introSkip=true;goRace(MAPS.findIndex(m=>m.id==='${a}'))`)", mp)
            await pg.wait_for_function("document.getElementById('raceLd').hidden", timeout=900000)
            for i in range(400):
                if await pg.evaluate("__ev(`state`)") == 'race': break
                await pg.wait_for_timeout(500)
            r = json.loads(await pg.evaluate("(js)=>__ev('JSON.stringify('+js+')')", JS))
            f = r['fin']; print(mp, 'N', r['N'], 'laps', r['laps'], 'step', r['step'], 'grid (units past the line)', r['grid'], 'prog at start', r['prog0'][:8], 'idx at start', r['idx0'][:8])
            print('   finished at (units past the line):', [q['pastLine'] for q in f], '| the step before:', [q['stepBefore'] for q in f][:4], '| idx', [q['idx'] for q in f][:4], 'prog', [q['prog'] for q in f][:4], 'need', f[0]['need'] if f else None, flush=True)
            await ctx.close()
        await b.close()
asyncio.run(main())
