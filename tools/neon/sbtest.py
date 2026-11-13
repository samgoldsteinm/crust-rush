"""Sandbox, driven by the test: py.cmd tools/neon/sbtest.py [region]      (region: a track id with a Sandbox region; default backyard)
Starts Sandbox the way the menu does, then puts the one kart at chosen places and lets the game's own physics run:
  walls    driven straight at each thing that should stop it: it must stop where the thing is, not before and not inside
  open     driven across what should be open ground: it must get there
  lap      steered along the whole track (the test only turns the wheel toward the track ahead): it must stay on the track's own
           heights (up the tree and down again), pick coins up, and never be thrown off
  edge     driven off the side of the track where it is high: it must fall to the lawn
Places are in GARDEN METRES (x east from the bedroom window, y north from the house wall), headings in degrees (0 east, 90 north).
Pictures: scratch/sb_<n>.png. Want: every line 'ok', errors [].   Q=<quality> (default fast)"""
import asyncio, json, sys, os
from playwright.async_api import async_playwright
SP = 'D:/crust-rush/scratch'; REG = sys.argv[1] if len(sys.argv) > 1 else 'backyard'; Q = os.environ.get('Q', 'fast')
JS = r"""
window.__sb={
  put(gx,gy,deg,wy){const k=player,a=-deg*Math.PI/180;k.x=k.px=sbGX(gx);k.y=k.py=sbGZ(gy);k.a=k.ma=k.pa=k.pma=a;k.speed=0;k.wy=k.pwy=k.lastG=(wy==null?sbG(k.x,k.y,0):wy);k.wvy=0;k.gRate=0;k.air=false;k.big=false;k.drift=0;k.spin=0;k.boost=0;k.bpx=k.x;k.bpy=k.y;k.loop=null;k.idx=sbIdx(k,k.idx);},
  at(){const k=player;return {x:+(k.x/SB_M-.75).toFixed(2),y:+(3.5-k.y/SB_M).toFixed(2),h:Math.round(k.wy||0),sp:Math.round(k.speed),air:!!k.air};},
  run(n){for(let i=0;i<n;i++)update(STEP);return this.at();},
  /* straight ahead for n steps, the heading held */
  line(gx,gy,deg,n,wy){this.put(gx,gy,deg,wy);const a=-deg*Math.PI/180;let top=0;for(let i=0;i<n;i++){player.a=player.ma=a;update(STEP);top=Math.max(top,player.wy||0);}const r=this.at();r.top=Math.round(top);return r;},
  /* along the track from lap fraction f0 for n steps: the wheel is turned toward the track ahead, nothing else */
  lap(f0,n){const k=player,j0=Math.round(f0*N)%N,p=track[j0];k.x=k.px=p.x;k.y=k.py=p.y;k.idx=j0;k.a=k.ma=k.pa=k.pma=Math.atan2(p.ty,p.tx);k.speed=0;k.wy=k.pwy=k.lastG=(p.ey||0);k.wvy=0;k.gRate=0;k.air=false;k.loop=null;k.bpx=k.x;k.bpy=k.y;
    const c0=sbSave().c;let off=0,airs=0,worst=0,maxh=0,far=0,stuck=0,lx=k.x,ly=k.y,done=0,loops=0,wasLoop=false;
    for(let i=0;i<n;i++){const q=track[(k.idx+9)%N],want=Math.atan2(q.y-k.y,q.x-k.x);if(!k.loop){k.a+=angDiff(want,k.a)*.25;k.ma=k.a;}update(STEP);if(k.loop&&!wasLoop)loops++;wasLoop=!!k.loop;
      const pj=track[k.idx],lat=Math.abs((k.x-pj.x)*pj.nx+(k.y-pj.y)*pj.ny),dh=Math.abs((k.wy||0)-(pj.ey||0));if(!k.loop){if(lat>TOYW()+4)off++;if(k.air)airs++;else worst=Math.max(worst,dh);}maxh=Math.max(maxh,k.wy||0);
      let d=k.idx-j0;if(d<0)d+=N;far=Math.max(far,d/N);if(i%120===119){if(Math.hypot(k.x-lx,k.y-ly)<8)stuck++;lx=k.x;ly=k.y;}if(d/N>.985&&i>600){done=i;break;}}
    return {reached:+far.toFixed(3),steps:done,off:off,airSteps:airs,worstHeightGap:+worst.toFixed(1),maxHeight:Math.round(maxh),stuck:stuck,loops:loops,coins:sbSave().c-c0};}
};'ok'
"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(channel='chromium', args=['--use-angle=d3d11','--enable-gpu','--ignore-gpu-blocklist','--enable-webgl'])
        ctx = await b.new_context(viewport={'width':1280,'height':720}, service_workers='block'); pg = await ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:400]))
        await pg.goto('http://localhost:8771/webcopy6/index.html')
        await pg.wait_for_function("document.getElementById('menu')&&!document.getElementById('menu').hidden", timeout=600000)
        await pg.evaluate("(a)=>__ev(`qKey='" + Q + "';applyQuality();clsKey='medium';introSkip=true;document.querySelector('#modeSeg button[data-m=sb]').click();`)", [REG])
        await pg.wait_for_timeout(1500)
        print('menu:', await pg.evaluate("__ev(`JSON.stringify({mode:mode,map:MAPS[mapIdx].id,label:document.getElementById('trackLabel').textContent,start:document.getElementById('startBtn').textContent,sbx:SBX,karts:karts.length})`)"))
        await pg.screenshot(path=f'{SP}/sb_menu.png')
        await pg.evaluate("(a)=>__ev(`goRace(MAPS.findIndex(m=>m.id==='${a[0]}'))`)", [REG])
        await pg.wait_for_function("document.getElementById('raceLd').hidden", timeout=900000)
        for i in range(400):
            if await pg.evaluate("__ev(`state`)") == 'race': break
            await pg.wait_for_timeout(500)
        print('started:', await pg.evaluate("__ev(`JSON.stringify({sbx:SBX,battle:BATTLE,karts:karts.length,coins:SB.coins.length,rare:SB.coins.filter(c=>c.rare).length,shapes:SB.shapes.length,cells:SB.hash.size,kartZ:[Math.round(player.y),Math.round(player.m.g.position.z)],start:[+(player.x/SB_M-.75).toFixed(2),+(3.5-player.y/SB_M).toFixed(2)]})`)"))
        await pg.wait_for_timeout(2500); await pg.screenshot(path=f'{SP}/sb_0.png')
        await pg.evaluate("(js)=>__ev(js)", JS)
        ev = lambda s: pg.evaluate("(js)=>__ev('JSON.stringify('+js+')')", s)
        bad = 0
        def say(name, r, ok):
            nonlocal bad; bad += not ok; print(('ok   ' if ok else 'FAIL ') + name, r, flush=True)
        if REG == 'backyard':
            # pictures from the chase camera: coins on the patio, the ring round the football, a pepperoni coin in the goal, nose against the back fence, the shed's door
            for i, (x, y, d) in enumerate([(-13.2, .8, 0), (5.2, 3.9, 0), (9.9, 4.9, 60), (6.0, 6.6, 90), (-10.9, 3.2, 100), (0.6, 4.0, 60)]):
                await ev(f"(()=>{{window.__sb.put({x},{y},{d});camSnap=true;cam.a=player.ma;return 1}})()"); await pg.wait_for_timeout(700); await pg.screenshot(path=f'{SP}/sb_v{i}.png')
            W = [  # name, x, y, heading, steps, test on the end place
                ('back fence', 5.5, 3.2, 90, 1500, lambda r: 6.85 < r['y'] < 6.97), ('east fence', 9.5, 2.6, 0, 1200, lambda r: 11.45 < r['x'] < 11.57),
                ('house wall', -5, 1.3, 270, 900, lambda r: 0 < r['y'] < .12), ('west fence', -11.5, 1.0, 180, 1200, lambda r: -13.87 < r['x'] < -13.75),
                ('shed, from the east', -8.9, 5.5, 180, 900, lambda r: -10.0 < r['x'] < -9.9), ('shed, from the south', -11.2, 3.0, 90, 900, lambda r: 4.3 < r['y'] < 4.45),
                ('the tree, under the spiral', 3.1, 3.2, 90, 1200, lambda r: 4.75 < r['y'] < 4.9 and r['h'] < 6), ('a flowerpot', 5.0, 1.5, 270, 700, lambda r: .7 < r['y'] < .85),
                ('the pipe, from the side', -3.6, 4.6, 90, 900, lambda r: 5.15 < r['y'] < 5.30),
                ('a post under the high track', None, None, 0, 500, lambda r: r['stopped']),
            ]
            for name, x, y, d, n, t in W:
                if x is None:   # straight at the first post that stands clear of the track, from 0.4 m to its west
                    r = json.loads(await ev("(()=>{const q=TOYPOSTS.find(q=>q[2]>40&&!sbBlocked(q[0]-140,q[1],0)&&!sbBlocked(q[0]-70,q[1],0));if(!q)return {stopped:false,why:'no post'};const gx=q[0]/SB_M-.75,gy=3.5-q[1]/SB_M;const r=window.__sb.line(gx-.4,gy,0," + str(n) + ");r.post=[+gx.toFixed(2),+gy.toFixed(2)];r.stopped=r.x<gx-.01&&r.x>gx-.06;return r})()")); say('wall: ' + name, r, t(r)); continue
                r = json.loads(await ev(f"window.__sb.line({x},{y},{d},{n})")); say('wall: ' + name, r, t(r))
            O = [('across the lawn, west to east', -1.5, 3.3, 0, 1500, lambda r: r['x'] > 4), ('over the track where it lies on the lawn (the weaving run home)', -6, 1.6, 90, 500, lambda r: r['y'] > 2.9 and r['top'] >= 3),
                 ('along the patio', -12.5, .8, 0, 1700, lambda r: r['x'] > -7), ('through the goal mouth', 9.9, 4.2, 90, 700, lambda r: r['y'] > 5.9)]
            for name, x, y, d, n, t in O:
                r = json.loads(await ev(f"window.__sb.line({x},{y},{d},{n})")); say('open: ' + name, r, t(r))
            r = json.loads(await ev("window.__sb.lap(.02,60000)"))
            r2 = json.loads(await ev("(()=>{player.prog=LAPS*N+50;for(let i=0;i<30;i++)update(STEP);return {finished:!!player.finished,state:state}})()"))
            say('no finish: more than the race distance on the clock', r2, not r2['finished'] and r2['state'] == 'race')
            say('lap: the whole track by its own heights', r, r['reached'] > .98 and r['off'] < 40 and r['worstHeightGap'] < 6 and r['maxHeight'] > 240 and r['stuck'] == 0 and r['coins'] > 20)
            await pg.wait_for_timeout(1500); await pg.screenshot(path=f'{SP}/sb_1.png')
            # off the high part of the track: at the top of the tree's spiral, heading out over the lawn
            r = json.loads(await ev("(()=>{const j=Math.round(.352*N),p=track[j];const k=player;k.x=k.px=p.x;k.y=k.py=p.y;k.idx=j;k.wy=k.pwy=k.lastG=p.ey;k.air=false;k.wvy=0;k.gRate=0;k.loop=null;const out=Math.atan2(p.y-sbGZ(5.2),p.x-sbGX(3.1));let top=k.wy;for(let i=0;i<700;i++){k.a=k.ma=out;update(STEP);}const r=window.__sb.at();r.from=Math.round(top);return r})()"))
            say('edge: off the top of the spiral', r, r['from'] > 150 and r['h'] < 6 and not r['air'])
            await pg.wait_for_timeout(1500); await pg.screenshot(path=f'{SP}/sb_2.png')
        print('saved:', await pg.evaluate("localStorage.getItem('crust-sb')"))
        await pg.evaluate("__ev(`toMenu()`)"); await pg.wait_for_timeout(1500)
        print('back at the menu:', await pg.evaluate("__ev(`JSON.stringify({sbx:SBX,battle:BATTLE,karts:karts.length,hud:!document.getElementById('sbHud')||document.getElementById('sbHud').hidden,cls:document.body.classList.contains('battle')})`)"))
        print('errors', errs[:6]); print('SANDBOX TEST', 'FAILED' if bad or errs else 'passed')
        await b.close()
asyncio.run(main())
