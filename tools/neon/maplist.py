"""What every map is, as the game holds it: py.cmd tools/neon/maplist.py
One line a map: id, name, cup, world radius, and every setting that is not plain data (toy, neon, arena, glide, loops, shortcuts, ponds ...).
Used to plan Sandbox's regions (docs/SANDBOX-PLAN.md)."""
import asyncio, json
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(channel='chromium', args=['--use-angle=d3d11','--enable-gpu','--ignore-gpu-blocklist','--enable-webgl'])
        pg = await (await b.new_context(service_workers='block')).new_page()
        await pg.goto('http://localhost:8771/webcopy6/index.html')
        await pg.wait_for_function("document.getElementById('menu')&&!document.getElementById('menu').hidden", timeout=600000)
        r = json.loads(await pg.evaluate("__ev(`JSON.stringify(MAPS.map(m=>{const o={};for(const k in m){const v=m[k];if(k==='blurb'||k==='name'||k==='id')continue;o[k]=Array.isArray(v)?'['+v.length+']':(v&&typeof v==='object')?'{'+Object.keys(v).slice(0,6).join(',')+'}':v;}return [m.id,m.name,o]}))`)"))
        for id_, name, o in r: print(f'{id_:11s} {name:26s}', json.dumps(o, separators=(',', ':'))[:330])
        await b.close()
asyncio.run(main())
