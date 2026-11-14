"""The controller's on-screen cursor in the menus (web v194, tools/mini/patch29.py):   py.cmd tools/neon/padtest.py
A pretend controller (navigator.getGamepads is replaced before the game loads; the test moves its sticks and presses its buttons):
  move     the left stick moves the arrow; let go and it stays
  press    A presses what is under the arrow (the Sandbox mode button, then a track card)
  hover    the thing under the arrow carries .padhover; nothing has the yellow ring (body.padnav is off)
  scroll   the right stick scrolls the track list; the arrow held against its bottom edge scrolls it too
  race     in a race the arrow is hidden; in the pause menu it is back, and A on Resume resumes
Pictures scratch/pad_*.png."""
import asyncio, json
from playwright.async_api import async_playwright
INIT = """(()=>{const b=()=>({pressed:false,touched:false,value:0});const pad={id:'Test pad (STANDARD GAMEPAD)',index:0,connected:true,mapping:'standard',timestamp:1,axes:[0,0,0,0],buttons:Array.from({length:17},b),vibrationActuator:null};
window.__pad=pad;navigator.getGamepads=()=>[pad];window.__axes=(a)=>{pad.axes=a;pad.timestamp++;};window.__btn=(i,on)=>{pad.buttons[i]={pressed:!!on,touched:!!on,value:on?1:0};pad.timestamp++;};})()"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(channel='chromium', args=['--use-angle=d3d11', '--enable-gpu', '--ignore-gpu-blocklist', '--enable-webgl'])
        ctx = await b.new_context(viewport={'width': 1280, 'height': 720}, service_workers='block'); await ctx.add_init_script(INIT); pg = await ctx.new_page(); errs = []; bad = 0
        pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        ev = lambda s: pg.evaluate("(js)=>__ev('JSON.stringify('+js+')')", s)
        def say(name, r, ok):
            nonlocal bad; bad += not ok; print(('ok   ' if ok else 'FAIL ') + name, r, flush=True)
        async def axes(a, ms): await pg.evaluate("(a)=>window.__axes(a)", a); await pg.wait_for_timeout(ms); await pg.evaluate("window.__axes([0,0,0,0])"); await pg.wait_for_timeout(120)
        async def press(i): await pg.evaluate("(i)=>window.__btn(i,true)", i); await pg.wait_for_timeout(90); await pg.evaluate("(i)=>window.__btn(i,false)", i); await pg.wait_for_timeout(250)
        CUR = "({x:Math.round(PAD.cx),y:Math.round(PAD.cy),on:!!PAD.curOn,shown:!!PAD.cur&&!PAD.cur.hidden,hov:PAD.hov?(PAD.hov.id||PAD.hov.className||PAD.hov.tagName):null,ring:document.body.classList.contains('padnav')})"
        async def goto(sel):   # steer the arrow onto an element by its place on the screen (as a player would), in a few hops
            for hop in range(14):
                r = await pg.evaluate("(s)=>{const e=document.querySelector(s);if(!e)return null;const r=e.getBoundingClientRect();return [r.left+r.width/2,r.top+r.height/2]}", sel)
                c = json.loads(await ev(CUR))
                if r is None: return False
                dx, dy = r[0] - c['x'], r[1] - c['y']; d = (dx * dx + dy * dy) ** .5
                if d < 9: return True
                f = .34 if d < 60 else .55 if d < 220 else 1; await axes([dx / d * f, dy / d * f, 0, 0], 60 if d < 60 else 140 if d < 220 else int(min(420, d / 1.3)))
            return False
        await pg.goto('http://localhost:8771/webcopy6/index.html')
        await pg.wait_for_function("document.getElementById('menu')&&!document.getElementById('menu').hidden", timeout=600000)
        await pg.evaluate("__ev(`qKey='fast';applyQuality();clsKey='medium';introSkip=true;`)"); await pg.wait_for_timeout(600)
        await axes([.6, .2, 0, 0], 300); c0 = json.loads(await ev(CUR)); await pg.wait_for_timeout(300); c1 = json.loads(await ev(CUR))
        await axes([-1, 0, 0, 0], 250); c2 = json.loads(await ev(CUR))
        say('move: the left stick moves the arrow, and it stays where it is left', {'after': c0, 'later': c1, 'left': c2}, c0['on'] and c0['shown'] and (c0['x'], c0['y']) == (c1['x'], c1['y']) and c2['x'] < c1['x'] - 80 and not c0['ring'])
        await pg.screenshot(path='D:/crust-rush/scratch/pad_0.png')
        # into the mode list and press Sandbox
        step = json.loads(await ev("menuStep"))
        ok = await goto('#modeSeg button[data-m=sb]')
        if not ok:   # the mode buttons are on a later step of the menu: walk there with the main button
            for i in range(4):
                if await pg.evaluate("(()=>{const e=document.querySelector('#modeSeg button[data-m=sb]');if(!e)return false;const r=e.getBoundingClientRect();return r.width>0&&r.top>0&&r.bottom<innerHeight})()"): break
                await press(0); await pg.wait_for_timeout(500)
            ok = await goto('#modeSeg button[data-m=sb]')
        h = json.loads(await ev(CUR)); hov = await pg.evaluate("document.querySelectorAll('.padhover').length"); await press(0); m = json.loads(await ev("mode"))
        say('press: A presses what is under the arrow (the Sandbox mode)', {'reached': ok, 'cursor': h, 'mode': m, 'step': step}, ok and m == 'sb' and h['hov'] is not None)
        say('hover: one thing lit under the arrow, no yellow ring', {'lit': hov, 'ring': h['ring']}, hov == 1 and not h['ring'])
        await pg.screenshot(path='D:/crust-rush/scratch/pad_1.png')
        # scrolling: Settings is taller than a small window. Open it with the arrow, scroll it both ways, leave with B
        await pg.set_viewport_size({'width': 900, 'height': 440}); await pg.evaluate("__ev(`mode='single';refreshMenu();goStep('home');`)"); await pg.wait_for_timeout(900)
        ok = await goto('#setBtn'); await press(0); await pg.wait_for_timeout(500); opened = await pg.evaluate("!document.getElementById('setOv').hidden")
        say('press: A on the Settings button opens Settings', {'reached': ok, 'open': opened}, ok and opened)
        await axes([-.5, -.3, 0, 0], 250)
        SC = "(()=>{const e=document.elementFromPoint(PAD.cx,PAD.cy),s=padScroller(e,'Y');return s?{id:s.id,top:Math.round(s.scrollTop),max:s.scrollHeight-s.clientHeight}:null})()"
        s0 = json.loads(await ev(SC)); await axes([0, 0, 0, 1], 500); s1 = json.loads(await ev(SC)); await axes([0, 0, 0, -1], 900); s2 = json.loads(await ev(SC))
        say('scroll: the right stick scrolls what is under the arrow, down and back up', [s0, s1, s2], bool(s0 and s1 and s2) and s1['top'] > s0['top'] + 30 and s2['top'] < s1['top'] - 30)
        await axes([0, 1, 0, 0], 1600); s3 = json.loads(await ev(SC)); c = json.loads(await ev(CUR)); await pg.screenshot(path='D:/crust-rush/scratch/pad_2.png')
        say('scroll: the arrow held against the bottom edge scrolls on down', {'scroll': s3, 'cursor': c}, bool(s3) and s3['top'] > s2['top'] + 30)
        await axes([0, -1, 0, 0], 1800); s4 = json.loads(await ev(SC))
        say('scroll: and against the top edge, back up', {'scroll': s4}, bool(s4) and s4['top'] < s3['top'] - 30)
        await press(1); closed = await pg.evaluate("document.getElementById('setOv').hidden")
        say('back: B closes Settings', {'closed': closed}, closed)
        await pg.set_viewport_size({'width': 1280, 'height': 720}); await pg.wait_for_timeout(400)
        # a race: no arrow; the pause menu: arrow, and A on Resume
        await pg.evaluate("__ev(`mode='single';goRace(MAPS.findIndex(m=>m.id==='margherita'))`)")
        await pg.wait_for_function("document.getElementById('raceLd').hidden", timeout=900000)
        for i in range(200):
            if await pg.evaluate("__ev(`state`)") == 'race': break
            await pg.wait_for_timeout(300)
        await axes([.5, 0, 0, 0], 300); r = json.loads(await ev(CUR)); st = json.loads(await ev("({steer:+PAD.steer.toFixed(2)})"))
        say('race: no arrow while racing (the stick steers)', {'cursor': r, 'state': await pg.evaluate("__ev(`state`)")}, not r['shown'])
        await press(9); await pg.wait_for_timeout(400); await axes([.3, .3, 0, 0], 200); ok = await goto('#resumeBtn'); pz = json.loads(await ev(CUR)); await pg.screenshot(path='D:/crust-rush/scratch/pad_3.png')
        await press(0); s = await pg.evaluate("__ev(`state`)")
        say('pause: the arrow is back, and A on Resume resumes', {'reached': ok, 'cursor': pz, 'state': s}, ok and pz['shown'] and s == 'race')
        print('errors', errs[:5]); print('CONTROLLER CURSOR TEST', 'FAILED' if bad or errs else 'passed'); await b.close()
asyncio.run(main())
