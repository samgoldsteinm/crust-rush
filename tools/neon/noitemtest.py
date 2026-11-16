"""Races without items (patch 47): the item guide may switch every item off, the menu's Items switch is the same setting, a race with
every item off has no item boxes (none drawn, nobody gets an item), Items On brings them back, the host's choice goes in the race
config (cfg.ni), and the world board has a No items tab and sends p_noitems. Nothing is written to the real board.
   py.cmd tools/neon/noitemtest.py   ->  "NO ITEMS TEST passed" (pictures scratch/noitem_*.png)"""
import asyncio, json
from playwright.async_api import async_playwright
SP = 'D:/crust-rush/scratch'


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(channel='chromium', args=['--use-angle=d3d11', '--enable-gpu', '--ignore-gpu-blocklist', '--enable-webgl'])
        ctx = await b.new_context(viewport={'width': 1280, 'height': 720}, service_workers='block'); pg = await ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await ctx.add_init_script("try{localStorage.setItem('crust-lb-name','Pizza Tester');localStorage.setItem('crust-q','fast');localStorage.removeItem('crust-items')}catch(e){}")
        sent, boards = [], []

        async def rpc(r):
            sent.append(json.loads(r.request.post_data or '{}')); await r.fulfill(status=204, body='')

        async def board(r):
            boards.append(r.request.url); await r.fulfill(status=200, content_type='application/json', body='[]')
        await pg.route('**/rest/v1/rpc/submit_run', rpc)
        await pg.route('**/rest/v1/best_runs*', board)
        await pg.goto('http://localhost:8771/webcopy6/index.html')
        await pg.wait_for_function("document.getElementById('menu')&&!document.getElementById('menu').hidden&&!!window.__ev", timeout=600000, polling=1000)
        await pg.wait_for_timeout(3000)
        R = {}
        # the guide: switch every item off one by one (it used to keep the last one on)
        R['guideAllOff'] = await pg.evaluate("""__ev(`(()=>{ITEMSET={};saveItemSet();renderItemSet();
            for(let n=0;n<40&&!itemsOff();n++){const li=[...document.querySelectorAll('#guideItems li[data-it]')].find(x=>itemOn(x.dataset.it)&&x.getAttribute('aria-disabled')!=='true');if(!li)break;li.click();}
            return itemsOff();})()`)""")
        R['menuSaysOff'] = await pg.evaluate("__ev(`refreshMenu();$('itmSeg').querySelector('[data-i=\"0\"]').getAttribute('aria-pressed')`)")
        R['cfgNi'] = await pg.evaluate("__ev(`(()=>{const pl=NET.pl;NET.pl=[{id:0,ri:selected}];const c=netBuildCfg(mapIdx);NET.pl=pl;return c.ni;})()`)")

        async def race(tag):
            await pg.evaluate("__ev(`mode='single';CPUS=2;store.set('crust-cpus','2');mapIdx=MAPS.findIndex(m=>m.id==='margherita');goRace(mapIdx)`)")
            await pg.wait_for_function("__ev(`state==='race'||state==='countdown'`)", timeout=300000, polling=1000)
            await pg.evaluate("__ev(`player.auto=true;window.__got=0`)")
            for i in range(45):
                await pg.evaluate("__ev(`for(const k of karts)if(k.item||k.item2||k.held||k.pend.length)window.__got++`)")
                await pg.wait_for_timeout(1000)
            out = json.loads(await pg.evaluate("__ev(`JSON.stringify({noitm:NOITM,got:window.__got,boxes:boxes.length,taken:boxes.filter(b=>b.r>0).length,st:state,prog:player.prog})`)"))
            await pg.screenshot(path=f'{SP}/noitem_{tag}.png')
            await pg.evaluate("__ev(`toMenu()`)"); await pg.wait_for_timeout(1500)
            return out
        R['off'] = await race('off')
        # the menu's On puts the guide back
        await pg.click('#itmSeg [data-i="1"]') if await pg.is_visible('#itmSeg') else await pg.evaluate("__ev(`$('itmSeg').querySelector('[data-i=\"1\"]').click()`)")
        R['onAgain'] = await pg.evaluate("__ev(`!itemsOff()&&ITEM_LIST.every(k=>!itemUnlocked(k)||itemOn(k))`)")
        R['on'] = await race('on')
        # the menu's Off switches every item off
        await pg.evaluate("__ev(`$('itmSeg').querySelector('[data-i=\"0\"]').click()`)")
        R['menuOff'] = await pg.evaluate("__ev(`itemsOff()`)")
        # the board: the No items tab, and a no-items run sent with p_noitems
        await pg.evaluate("__ev(`lbOpen(MAPS.findIndex(m=>m.id==='margherita'),'medium')`)"); await pg.wait_for_timeout(1200)
        await pg.click('#lbSolo [data-s="2"]'); await pg.wait_for_timeout(1200)
        await pg.screenshot(path=f'{SP}/noitem_board.png')
        await pg.click('#lbSolo [data-s="0"]'); await pg.wait_for_timeout(1200)
        await pg.evaluate("__ev(`$('lbOv').hidden=true;lbSaveQ([{map:'margherita',cls:'medium',ms:171234,drv:'Pep',kart:'Classic',solo:true,ni:true,at:Date.now()},{map:'margherita',cls:'medium',ms:181234,drv:'Pep',kart:'Classic',solo:false,at:Date.now()}]);lbFlush()`)")
        await pg.wait_for_timeout(2500)
        R['boards'] = boards; R['sent'] = sent
        R['proto'] = await pg.evaluate("__ev(`NET_PROTO`)")
        print(json.dumps(R, indent=1))
        ni_url = [u for u in boards if 'noitems=eq.true' in u]
        rv_url = [u for u in boards if 'solo=eq.false' in u and 'noitems=eq.false' in u]
        ok = (R['guideAllOff'] and R['menuSaysOff'] == 'true' and R['cfgNi'] is True
              and R['off']['noitm'] and R['off']['got'] == 0 and R['off']['taken'] == 0 and R['off']['prog'] > 0
              and R['onAgain'] and not R['on']['noitm'] and R['on']['got'] > 0
              and R['menuOff'] and ni_url and rv_url and len(sent) == 2 and sent[0].get('p_noitems') is True and 'p_noitems' not in sent[1]
              and R['proto'] == 116 and not errs)
        print('errors', errs[:3]); print('NO ITEMS TEST', 'passed' if ok else 'FAILED')
        await b.close()
asyncio.run(main())
