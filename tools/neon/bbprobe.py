"""Balloon Battle, a look at anything:   py.cmd tools/neon/bbprobe.py <file.js> [quality] [phone]
Starts a battle on the prep table (quality: fast, sharp, ultra ...; default ultra; `phone` gives a phone's screen and touch), waits for its
Blender-built models, then runs each block of <file.js> in the game and prints what it returns. Blocks are separated by a line holding only
----; each is one expression (wrap statements as (()=>{...})()). A block that starts with //shot <name> takes a picture
scratch/bb2/<name>.png one second after it ran; //wait <ms> waits first. Helpers loaded into the page (window):
  __solo()            the player alone on the table: the others are parked far off, the clock stands still, nothing can pop the player
  __put(x,z,a)        set the player down at (x,z) heading a
  __drv               a function (kart, dt) -> input that drives the player instead of the game's CPU driver (null: the CPU driver)
  __run(sec, stop)    run the game `sec` seconds at once (stop(): end early) -> the seconds it ran, or -1 if it ran them all
  __cam               [x,y,z, lookx,looky,lookz]: the camera held there (null: the game's own)
tools/neon/bbcheck.js is the standing check: every item box reached and taken, every spawn free, every wall met where it is drawn."""
import asyncio, json, re, sys
from playwright.async_api import async_playwright
SRC = open(sys.argv[1], encoding='utf-8').read(); SP = 'D:/crust-rush/scratch/bb2'
Q = sys.argv[2] if len(sys.argv) > 2 else 'ultra'; PHONE = len(sys.argv) > 3
HELP = r"""(()=>{const AI0=battleAI;window.__drv=null;battleAI=function(k,dt){if(k===player&&window.__drv)return window.__drv(k,dt);return AI0(k,dt);};
  window.__solo=()=>{for(const k of karts)if(k!==player){k.bbOut=1e9;k.x=k.px=60000;k.y=k.py=60000;k.speed=0;}player.auto=true;player.inv=1e9;BB.t=1e9;};
  window.__put=(x,z,a)=>{const k=player;k.x=k.px=x;k.y=k.py=z;k.a=k.ma=k.pa=k.pma=a;k.speed=0;k.wy=k.pwy=k.lastG=battleG(x,z);k.wvy=0;k.gRate=0;k.air=false;k.big=false;k.spin=0;k.drift=0;k.charge=0;k.boost=0;k.z=k.pz=0;k.bpx=x;k.bpy=z;k.bbOut=0;k.item=null;k.roll=0;k.rx=x;k.ry=z;k.rz=k.wy;k.rma=a;cam.a=a;camSnap=true;};
  window.__run=(sec,stop)=>{const n=Math.round(sec/STEP);for(let i=0;i<n;i++){update(STEP);if(stop&&stop())return (i+1)*STEP;}return -1;};
  window.__cam=null;const R0=renderer.render.bind(renderer);renderer.render=(s,c)=>{if(c===camera&&window.__cam){const q=window.__cam;camera.position.set(q[0],q[1],q[2]);camera.up.set(0,1,0);camera.lookAt(q[3],q[4],q[5]);camera.updateMatrixWorld(true);}R0(s,c);};return 1;})()"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(channel='chromium', args=['--use-angle=d3d11', '--enable-gpu', '--ignore-gpu-blocklist', '--enable-webgl'])
        ctx = await b.new_context(viewport={'width': 844, 'height': 390}, device_scale_factor=2, has_touch=True, is_mobile=True, service_workers='block') if PHONE else await b.new_context(viewport={'width': 1280, 'height': 720}, service_workers='block')
        pg = await ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:300])); pg.on('console', lambda m: errs.append('console: ' + m.text[:200]) if m.type == 'error' and 'GPU' not in m.text and 'WebGL' not in m.text else None)
        await pg.goto('http://localhost:8771/webcopy6/index.html')
        await pg.wait_for_function("document.getElementById('menu')&&!document.getElementById('menu').hidden", timeout=600000)
        await pg.evaluate("__ev(`qKey='" + Q + "';applyQuality();clsKey='medium';mode='bb';introSkip=true;goRace(MAPS.findIndex(m=>m.battle))`)")
        await pg.wait_for_function("document.getElementById('raceLd').hidden", timeout=900000)
        for i in range(400):
            if await pg.evaluate("__ev(`state`)") == 'race': break
            await pg.wait_for_timeout(500)
        print('packs', await pg.evaluate("__ev(`JSON.stringify(['bbtable','bbbins','bbboxes','bbblock','bbisle','bbprops'].map(n=>n+':'+(typeof PROP_PACKS!=='undefined'&&PROP_PACKS['toy_'+n+'_hq']&&(PROP_PACKS['toy_'+n+'_hq'].b||PROP_PACKS['toy_'+n+'_hq'].d)?'in':'NOT IN')))`)"), flush=True)
        await pg.evaluate("(js)=>__ev(js)", HELP)
        for blk in re.split(r'^----\s*$', SRC, flags=re.M):
            blk = blk.strip()
            if not blk: continue
            shot = None
            while True:
                m = re.match(r'//shot (\S+)\s*', blk)
                if m: shot = m.group(1); blk = blk[m.end():]; continue
                m = re.match(r'//wait (\d+)\s*', blk)
                if m: await pg.wait_for_timeout(int(m.group(1))); blk = blk[m.end():]; continue
                break
            if blk:
                try: r = await pg.evaluate("(js)=>__ev('JSON.stringify('+js+')')", blk)
                except Exception as e: r = 'ERROR ' + str(e)[:600]
                print(str(r)[:6000], flush=True)
            if shot: await pg.wait_for_timeout(1000); await pg.screenshot(path=f'{SP}/{shot}.png')
        print("errors", errs[:6]); await b.close()
asyncio.run(main())
