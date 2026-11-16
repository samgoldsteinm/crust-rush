"""The usernames and the world leaderboard (patch 44), without writing to the real board: the name check and the board are read from it
(read only); claiming a name and sending a run are caught in the page and answered here, and what would have been sent is checked.
   py.cmd tools/neon/lbtest.py   ->  "LEADERBOARD TEST passed" (pictures scratch/lb_*.png)"""
import asyncio, json
from playwright.async_api import async_playwright
SP = 'D:/crust-rush/scratch'


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(channel='chromium', args=['--use-angle=d3d11', '--enable-gpu', '--ignore-gpu-blocklist', '--enable-webgl'])
        ctx = await b.new_context(viewport={'width': 1280, 'height': 720}, service_workers='block'); pg = await ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        sent = []

        async def route(r):
            u = r.request.url
            if '/rpc/claim_name' in u:
                body = json.loads(r.request.post_data or '{}'); sent.append(['claim', body])
                await r.fulfill(status=200, content_type='application/json', body=json.dumps(body.get('p_name')))
            elif '/rpc/submit_run' in u:
                sent.append(['run', json.loads(r.request.post_data or '{}')]); await r.fulfill(status=204, body='')
            else:
                await r.continue_()
        await pg.route('**/rest/v1/rpc/claim_name', route)
        await pg.route('**/rest/v1/rpc/submit_run', route)
        await pg.goto('http://localhost:8771/webcopy6/index.html')
        await pg.wait_for_function("document.getElementById('menu')&&!document.getElementById('menu').hidden", timeout=600000)
        await pg.evaluate("__ev(`try{store.set('crust-lb-name','');store.set('crust-lb-q','[]')}catch(e){};sessionStorage.removeItem('crust-lb-asked');dispatchEvent(new Event('cr-booted'))`)")
        await pg.wait_for_timeout(3500)
        R = {}
        R['sheetShown'] = await pg.evaluate("__ev(`!!$('lbNameOv')&&!$('lbNameOv').hidden`)")
        await pg.fill('#lbNameIn', 'x'); await pg.wait_for_timeout(300)
        R['shortMsg'] = await pg.inner_text('#lbNameMsg')
        await pg.fill('#lbNameIn', 'Pizza Tester 77'); await pg.wait_for_timeout(2500)
        R['freeMsg'] = await pg.inner_text('#lbNameMsg')
        await pg.screenshot(path=f'{SP}/lb_name.png')
        await pg.click('#lbNameOk'); await pg.wait_for_timeout(1500)
        R['stored'] = await pg.evaluate("__ev(`lbName()`)")
        R['token'] = len(await pg.evaluate("__ev(`lbToken()`)"))
        # a finished run, as saveRun hands it over (lbRun's checks are for a live race; the queue and the send are what is tested here)
        await pg.evaluate("__ev(`lbSaveQ([{map:'margherita',cls:'medium',ms:171234,drv:'Pep',kart:'Classic',solo:false,at:Date.now()}]);lbFlush()`)")
        await pg.wait_for_timeout(2500)
        R['queueAfter'] = await pg.evaluate("__ev(`lbQueue().length`)")
        R['netName'] = await pg.evaluate("__ev(`netName()`)")
        await pg.evaluate("__ev(`lbOpen(0,'medium')`)"); await pg.wait_for_timeout(2500)
        R['board'] = await pg.inner_text('#lbList')
        await pg.screenshot(path=f'{SP}/lb_board.png')
        R['sent'] = sent
        print(json.dumps(R, indent=1))
        run = [x for x in sent if x[0] == 'run']
        ok = (R['sheetShown'] and 'letters' in R['shortMsg'] and ('Available' in R['freeMsg']) and R['stored'] == 'Pizza Tester 77' and R['token'] == 40
              and R['queueAfter'] == 0 and run and run[0][1]['p_time_ms'] == 171234 and run[0][1]['p_platform'] == 'web' and run[0][1]['p_solo'] is False
              and R['netName'] == 'Pizza Tester 7' and ('No times yet' in R['board'] or '1' in R['board']) and not errs)
        print('errors', errs[:3]); print('LEADERBOARD TEST', 'passed' if ok else 'FAILED')
        await b.close()
asyncio.run(main())
