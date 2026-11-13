import asyncio, json, sys, os
from playwright.async_api import async_playwright
# usage: matprobe.py <map> <text in material name> [WAITPK env as shots.py]: what the game really draws that material with
MAP, KEY = sys.argv[1], sys.argv[2]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(channel='chromium', args=['--use-angle=d3d11','--enable-gpu','--ignore-gpu-blocklist','--enable-webgl'])
        ctx = await b.new_context(viewport={'width':960,'height':540}, service_workers='block'); pg = await ctx.new_page()
        await pg.goto('http://localhost:8771/webcopy6/index.html')
        await pg.wait_for_function("document.getElementById('menu')&&!document.getElementById('menu').hidden", timeout=600000)
        for nm in [v for v in os.environ.get('WAITPK','').split(',') if v]:
            await pg.wait_for_function("(n)=>__ev(`TM.pkReady('${n}')`)", arg=nm, timeout=600000)
        await pg.evaluate("(a)=>__ev(`qKey='${a[1]}';applyQuality();mode='single';introSkip=true;goRace(MAPS.findIndex(m=>m.id==='${a[0]}'))`)", [MAP, os.environ.get('Q','ultra')])
        await pg.wait_for_function("document.getElementById('raceLd').hidden", timeout=900000)
        r = await pg.evaluate("(k)=>__ev(`(()=>{const out=[];scene.traverse(o=>{if(!o.isMesh)return;const ms=Array.isArray(o.material)?o.material:[o.material];for(const m of ms){if(!m||!(m.name||'').includes('${k}'))continue;out.push({mesh:o.name||o.type,name:m.name,type:m.type,alphaTest:m.alphaTest,side:m.side,transparent:m.transparent,map:!!m.map,mapImg:m.map&&m.map.image?[m.map.image.width,m.map.image.height]:null,enc:m.map&&m.map.encoding,color:m.color&&m.color.getHexString(),rough:m.roughness,vc:m.vertexColors,verts:o.geometry.attributes.position.count,hasUV:!!o.geometry.attributes.uv,hasCol:!!o.geometry.attributes.color,emis:m.emissive&&m.emissive.getHexString(),sheen:m.sheen,cc:m.clearcoat});}});return JSON.stringify(out);})()`)", KEY)
        for q in json.loads(r): print(q)
        await b.close()
asyncio.run(main())
