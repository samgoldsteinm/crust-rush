import asyncio, sys, json
from playwright.async_api import async_playwright
from PIL import Image
# usage: view.py <out name> "asset[:az,el,zoom[,args json]];..."   -> D:/crust-rush/source/tools/mini/view/<out>.jpg (a sheet)
OUT, SPEC = sys.argv[1], sys.argv[2]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(channel='chromium', args=['--use-angle=d3d11','--enable-gpu','--ignore-gpu-blocklist','--enable-webgl'])
        ctx = await b.new_context(viewport={'width':960,'height':600})
        pg = await ctx.new_page()
        errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        ims=[]
        for i, s in enumerate(SPEC.split(';')):
            nm, _, rest = s.partition(':')
            a = rest.split(',', 3) if rest else []
            url = f'http://localhost:8771/../mini/view/viewer.html?asset={nm}'
            url = f'http://localhost:8772/view/viewer.html?asset={nm}'
            if len(a) > 0 and a[0]: url += f'&az={a[0]}'
            if len(a) > 1 and a[1]: url += f'&el={a[1]}'
            if len(a) > 2 and a[2]: url += f'&zoom={a[2]}'
            if len(a) > 3 and a[3]: url += '&' + a[3]
            await pg.goto(url)
            try:
                await pg.wait_for_function('window.__done', timeout=120000)
                print(await pg.evaluate('JSON.stringify(window.__info)'), flush=True)
            except Exception as e:
                print('FAIL', nm, errs[-2:], flush=True)
            f = f'D:/crust-rush/source/tools/mini/view/_{i}.png'; await pg.screenshot(path=f); ims.append(Image.open(f).convert('RGB'))
        await b.close()
        cols = 2 if len(ims) > 1 else 1; rows = (len(ims)+cols-1)//cols; w,h = ims[0].size
        sh = Image.new('RGB', (w*cols, h*rows))
        for i, im in enumerate(ims): sh.paste(im, ((i%cols)*w, (i//cols)*h))
        if sh.width > 1920: sh = sh.resize((1920, int(sh.height*1920/sh.width)))
        sh.save(f'D:/crust-rush/source/tools/mini/view/{OUT}.jpg', quality=88)
        if errs: print('errors', errs[:3])
asyncio.run(main())
