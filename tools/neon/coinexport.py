"""The Sandbox coins' shapes for the PC (web patches 61, 63): runs the web's sbCoinGeo for the gold, pepperoni and mission coins and writes
their triangles to godot/assets/sandbox/coin.json, coin_pep.json, coin_act.json, and the three mission icons (sbActIcon) as act_<kind>.png; as {p: positions, n: normals, c: colours}, flat lists, three per corner, wound as the web winds them
(counter-clockwise from outside: the PC turns each triangle round). webtest.py must be serving. Run again whenever sbCoinGeo changes.
    py.cmd tools/neon/coinexport.py"""
import asyncio, base64, json, os
from playwright.async_api import async_playwright
OUT = 'D:/crust-rush/godot/assets/sandbox/coin.json'


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(channel='chromium')
        pg = await (await b.new_context(service_workers='block')).new_page()
        await pg.goto('http://localhost:8771/webcopy6/index.html')
        await pg.wait_for_function("!!window.__ev&&typeof sbCoinGeo!=='undefined'||!!window.__ev", timeout=600000, polling=1000)
        out = {}
        for kind in ('gold', 'pep', 'act'):
            out[kind] = json.loads(await pg.evaluate("(k)=>__ev(`(()=>{const g=sbCoinGeo('${k}'),f=a=>Array.from(g.attributes[a].array,v=>Math.round(v*1e4)/1e4);return JSON.stringify({p:f('position'),n:f('normal'),c:f('color')});})()`)", kind))
        icons = {}
        for kind in ('deliver', 'drift', 'air'):
            icons[kind] = await pg.evaluate("(k)=>__ev(`sbActIcon('${k}').toDataURL('image/png')`)", kind)
        await b.close()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    for kind, d in out.items():
        f = OUT if kind == 'gold' else OUT.replace('coin.json', 'coin_%s.json' % kind)
        json.dump(d, open(f, 'w'), separators=(',', ':'))
        print('coin %s: %d triangles -> %s (%d KB)' % (kind, len(d['p']) // 9, f, os.path.getsize(f) // 1024))
    for kind, u in icons.items():
        f = OUT.replace('coin.json', 'act_%s.png' % kind)
        open(f, 'wb').write(base64.b64decode(u.split(',', 1)[1]))
        print('icon', kind, '->', f)


asyncio.run(main())
