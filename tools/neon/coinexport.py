"""The Sandbox coin's shape for the PC (web patch 61): runs the web's sbCoinGeo and writes its triangles to
godot/assets/sandbox/coin.json as {p: positions, n: normals, c: colours}, flat lists, three per corner, wound as the web winds them
(counter-clockwise from outside: the PC turns each triangle round). webtest.py must be serving. Run again whenever sbCoinGeo changes.
    py.cmd tools/neon/coinexport.py"""
import asyncio, json, os
from playwright.async_api import async_playwright
OUT = 'D:/crust-rush/godot/assets/sandbox/coin.json'


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(channel='chromium')
        pg = await (await b.new_context(service_workers='block')).new_page()
        await pg.goto('http://localhost:8771/webcopy6/index.html')
        await pg.wait_for_function("!!window.__ev&&typeof sbCoinGeo!=='undefined'||!!window.__ev", timeout=600000, polling=1000)
        r = await pg.evaluate("__ev(`(()=>{const g=sbCoinGeo(),f=a=>Array.from(g.attributes[a].array,v=>Math.round(v*1e4)/1e4);return JSON.stringify({p:f('position'),n:f('normal'),c:f('color')});})()`)")
        await b.close()
    d = json.loads(r)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(d, open(OUT, 'w'), separators=(',', ':'))
    print('coin: %d triangles -> %s (%d KB)' % (len(d['p']) // 9, OUT, os.path.getsize(OUT) // 1024))


asyncio.run(main())
