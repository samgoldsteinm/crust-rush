"""Colour combos and the Rims row (web patch 73):   py.cmd tools/neon/combotest.py      (webtest.py must be serving)
A bought combo opens its pieces only in their own slots; coins are spent once; a free combo is owned; the Colour tab shows the combos and
a Rims row (patch 90: the Scissor sees 21 combos, its own Hypersonic among them, and the Save card). Pictures scratch/ug/web_colour.png (the tab) and scratch/ug/web_combo.png (Chrome King in the inspect view).
Prints COMBO TEST passed / FAILED."""
import asyncio, json
from playwright.async_api import async_playwright
SP = 'D:/crust-rush/scratch/ug'


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(channel='chromium', args=['--use-angle=d3d11', '--enable-gpu', '--ignore-gpu-blocklist', '--enable-webgl'])
        ctx = await b.new_context(viewport={'width': 1280, 'height': 720}, service_workers='block')
        await ctx.add_init_script("try{localStorage.setItem('crust-lb-name','Bench');localStorage.removeItem('crust-own');}catch(e){}")
        await ctx.route('**/rest/v1/**', lambda r: r.fulfill(status=204, body=''))
        pg = await ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto('http://localhost:8771/webcopy6/index.html')
        await pg.wait_for_function("!!(document.getElementById('menu')&&!document.getElementById('menu').hidden&&window.__ev)", timeout=600000, polling=1000)
        ev = lambda js: pg.evaluate("(j)=>__ev(j)", js)
        await ev("qKey='ultra';applyQuality();1"); await pg.wait_for_timeout(5000)
        await pg.evaluate("()=>{for(const b of document.querySelectorAll('button'))if(/^not now$/i.test(b.textContent.trim())&&b.offsetParent)b.click();}")
        R = {}
        ck = "COMBOS.findIndex(c=>c.n==='Chrome King')"
        await ev("{const sv=sbSave();sv.c=1000;sbKeep();}1")
        R['before'] = await ev("styleOwned('rm',17)")
        R['free'] = await ev("comboOwned(0)&&comboOwned(1)")
        R['buy'] = await ev(f"comboBuy({ck})")
        R['coins'] = await ev("sbSave().c")
        R['pieces'] = json.loads(await ev("JSON.stringify({rm:styleOwned('rm',17),tr:styleOwned('tr',17),ac:styleOwned('ac',17),gl:styleOwned('gl',7),inChrome:styleOwned('in',17),trGold:styleOwned('tr',16)})"))
        await ev(f"{{const c=COMBOS[{ck}];playerBuild.b=BODIES.findIndex(q=>q.id==='scissor');playerBuild.w=0;playerBuild.p=c.p;playerBuild.t='';playerBuild.st=Object.assign({{}},c.st);}}if(!garageOpen)openGarage();gTab='colour';refreshGarage(true);1")
        await pg.wait_for_timeout(2500)
        R['ui'] = json.loads(await ev("JSON.stringify({want:COMBOS.filter(c=>!c.only||c.only.includes('scissor')).length+1/* (patch 90: and the Save card) */,combos:document.querySelectorAll('#pStyle button.combo').length,rims:[...document.querySelectorAll('#pStyle .g-sub')].some(e=>e.textContent==='Rims'),on:[...document.querySelectorAll('#pStyle button.combo')].filter(b=>b.getAttribute('aria-pressed')==='true').length})"))
        await ev("gRot=1.0;1"); await pg.wait_for_timeout(200)
        await pg.screenshot(path=f'{SP}/web_colour.png')
        await ev("setBig(true);gRot=.9;gZoom=.55;gPitch=.1;1"); await pg.wait_for_timeout(1500); await ev("gRot=.9;1"); await pg.wait_for_timeout(150)
        await pg.screenshot(path=f'{SP}/web_combo.png')
        print(json.dumps(R, indent=1))
        P = R['pieces']
        ok = (not R['before'] and R['free'] and R['buy'] and R['coins'] == 100 and P['rm'] and P['tr'] and P['ac'] and P['gl'] and not P['inChrome']
              and not P['trGold'] and R['ui']['combos'] == R['ui']['want'] == 22 and R['ui']['rims'] and R['ui']['on'] == 1 and not errs)
        print('errors', errs[:4]); print('COMBO TEST', 'passed' if ok else 'FAILED')
        await b.close()


asyncio.run(main())
