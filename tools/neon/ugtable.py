"""The underglow's body table for the PC (web patch 77 -> pc77):   py.cmd tools/neon/ugtable.py   (webtest.py serving a build with patch 77)
Builds each body in the web build and reads its ugParams (the body's half-length and half-width, its centre, the strips' height, the
axles, the wheels' radius and z, a tyre's width, in the kart's own units). Writes tools/neon/ug_params.json (committed) {body id: [a, b, cx, cz, h, wf,
wr, rf, rr, wz, tw]}; pc77 pastes it into view.gd UG_P, so both draw the glow from the same numbers. Run it again when a body changes."""
import asyncio, json
from playwright.async_api import async_playwright
JS = """(()=>{const out={};BODIES.forEach((bd,i)=>{try{const m=buildKart(Object.assign({},playerBuild,{ri:0,g:0,p:2,t:"",b:i,w:0,st:{gl:1},ugL:1}));const ug=m.g.userData.ug;
  if(ug&&ug.P){const P=ug.P;out[bd.id]=[P.a,P.b,P.cx,P.cz,P.h,P.wf,P.wr,P.rf,P.rr,P.wz,P.tw];}}catch(e){out[bd.id]='ERR '+e;}});return out;})()"""


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(channel='chromium', args=['--use-angle=d3d11', '--enable-gpu', '--ignore-gpu-blocklist', '--enable-webgl'])
        ctx = await b.new_context(viewport={'width': 1280, 'height': 590}, service_workers='block')
        await ctx.route('**/rest/v1/**', lambda r: r.fulfill(status=204, body=''))
        pg = await ctx.new_page()
        await pg.goto('http://localhost:8771/webcopy6/index.html')
        await pg.wait_for_function("!!(document.getElementById('menu')&&!document.getElementById('menu').hidden&&window.__ev)", timeout=600000, polling=1000)
        r = await pg.evaluate("(j)=>__ev(j)", JS)
        await b.close()
    bad = {k: v for k, v in r.items() if not isinstance(v, list)}
    assert not bad, bad
    json.dump(r, open('D:/crust-rush/source/tools/neon/ug_params.json', 'w'), indent=0, sort_keys=True)
    print('UG TABLE written', len(r), 'bodies')

asyncio.run(main())
