"""The restart key (web patch 69): Backspace once pauses and asks, again restarts; Esc keeps racing.   py.cmd tools/neon/rsttest.py
Prints RESTART TEST passed / FAILED and takes scratch/rst_ask.png."""
import asyncio, json
from playwright.async_api import async_playwright


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(channel='chromium', args=['--use-angle=d3d11', '--enable-gpu', '--ignore-gpu-blocklist', '--enable-webgl'])
        ctx = await b.new_context(viewport={'width': 1280, 'height': 720}, service_workers='block')
        await ctx.add_init_script("try{localStorage.setItem('crust-lb-name','Bench');localStorage.setItem('crust-q','fast');}catch(e){}")
        await ctx.route('**/rest/v1/**', lambda r: r.fulfill(status=204, body=''))
        pg = await ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto('http://localhost:8771/webcopy6/index.html')
        await pg.wait_for_function("!!(document.getElementById('menu')&&!document.getElementById('menu').hidden&&window.__ev)", timeout=600000, polling=1000)
        ev = lambda js: pg.evaluate("(j)=>__ev(j)", js)
        await ev("introSkip=true;mode='single';CPUS=3;clsKey='medium';mapIdx=MAPS.findIndex(q=>q.id==='margherita');goRace(mapIdx);1")
        for i in range(240):
            if await ev("state==='race'"): break
            await pg.wait_for_timeout(500)
        await pg.wait_for_timeout(4000)
        R = {}
        R['t0'] = await ev("+raceTime.toFixed(1)")
        await pg.keyboard.press('Backspace'); await pg.wait_for_timeout(500)
        R['ask'] = await ev("JSON.stringify({ov:!$('rstOv').hidden,st:state,txt:$('rstTxt').textContent})")
        await pg.screenshot(path='D:/crust-rush/scratch/rst_ask.png')
        await pg.keyboard.press('Escape'); await pg.wait_for_timeout(500)
        R['cancel'] = await ev("JSON.stringify({ov:!$('rstOv').hidden,st:state})")
        await pg.wait_for_timeout(1500)
        R['t1'] = await ev("+raceTime.toFixed(1)")
        await pg.keyboard.press('Backspace'); await pg.wait_for_timeout(300)
        await pg.keyboard.press('Backspace'); await pg.wait_for_timeout(1500)
        R['after'] = await ev("JSON.stringify({ov:!$('rstOv').hidden,st:state,t:+raceTime.toFixed(1)})")
        print(json.dumps(R, indent=1))
        a, c, af = json.loads(R['ask']), json.loads(R['cancel']), json.loads(R['after'])
        ok = (a['ov'] and a['st'] == 'paused' and not c['ov'] and c['st'] == 'race' and R['t1'] > R['t0']
              and not af['ov'] and af['st'] in ('countdown', 'race') and af['t'] < R['t1'] and not errs)
        print('errors', errs[:3]); print('RESTART TEST', 'passed' if ok else 'FAILED')
        await b.close()


asyncio.run(main())
