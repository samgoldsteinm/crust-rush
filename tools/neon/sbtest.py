"""Sandbox, driven by the test: py.cmd tools/neon/sbtest.py [region]      (region: a track id with a Sandbox region; default backyard)
Starts Sandbox the way the menu does, then puts the one kart at chosen places and lets the game's own physics run:
  walls    driven straight at each thing that should stop it: it must stop where the thing is, not before and not inside
  open     driven across what should be open ground: it must get there
  lap      steered along the whole track (the test only turns the wheel toward the track ahead): it must stay on the track's own
           heights (up the tree and down again), pick coins up, and never be thrown off
  edge     driven off the side of the track where it is high: it must fall to the lawn
  passage  pointed at each gate in the wall and left to drive: it must come out in the next place, still driving, and back again
           (pictures scratch/sb_gate_<from>-to-<to>_<0..3>.png: before, in the duct, coming out, a moment later)
Places are in GARDEN METRES (x east from the bedroom window, y north from the house wall), headings in degrees (0 east, 90 north).
Any other region (bedroom, kitchen, garage): the lap, the no-finish check, and a plan of the room as Sandbox understands it,
scratch/sb_plan_<region>.png: white = open floor, grey = something you can drive up onto, black = a wall, blue = something you can
drive under, green = the track, yellow = coins, red = pepperoni coins, magenta = where you start.
Pictures: scratch/sb_<n>.png. Want: every line 'ok', errors [].   Q=<quality> (default fast)"""
import asyncio, json, sys, os
from playwright.async_api import async_playwright
SP = 'D:/crust-rush/scratch'; REG = sys.argv[1] if len(sys.argv) > 1 else 'backyard'; Q = os.environ.get('Q', 'fast')
PLAN = r"""(()=>{const c=SB.col,s=Math.max(1,Math.ceil(Math.max(c.nx,c.nz)/1800)),w=Math.ceil(c.nx/s),h=Math.ceil(c.nz/s),cv=document.createElement('canvas');cv.width=w;cv.height=h;const g=cv.getContext('2d'),im=g.createImageData(w,h),d=im.data;
for(let i=0;i<w;i++)for(let k=0;k<h;k++){let wall=false,under=false,up=0;for(let a=0;a<s;a++)for(let b=0;b<s;b++){const ii=i*s+a,kk=k*s+b;if(ii>=c.nx||kk>=c.nz)continue;const q=ii*c.nz+kk,o=q*SB_K*2,g0=SB.kind==='toy'?0:groundAt(c.x0+(ii+.5)*c.C,c.z0+(kk+.5)*c.C);for(let e=0;e<c.cnt[q];e++){const lo=c.sp[o+e*2]/SB_Q-g0,hi=c.sp[o+e*2+1]/SB_Q-g0;if(lo>=SB_HEAD){if(lo<c.cap)under=true;}else if(hi>SB_STEP)wall=true;else up=Math.max(up,hi);}}
 const x=c.x0+(i+.5)*s*c.C,z=c.z0+(k+.5)*s*c.C;let col=wall?[20,20,20]:under?[120,160,255]:up>0?[190,190,190]:[255,255,255];if(x<c.b[0]||x>c.b[1]||z<c.b[2]||z>c.b[3]||(SB.rim&&x*x+z*z>SB.rim*SB.rim))col=[60,0,0];else if(SB.kind==='open'&&pitAt(x,z)>25)col=[150,90,200];
 const a=SB.hash.get((Math.floor(x/SB_C)+2048)*4096+Math.floor(z/SB_C)+2048);if(a){for(const j of a){const p=track[j],dx=x-p.x,dz=z-p.y;if(Math.abs(dx*p.tx+dz*p.ty)<4&&Math.abs(dx*p.nx+dz*p.ny)<(SB.kind==='toy'?TOYW():RW)){col=wall?[0,90,0]:[70,200,90];break;}}}
 const o=(k*w+i)*4;d[o]=col[0];d[o+1]=col[1];d[o+2]=col[2];d[o+3]=255;}g.putImageData(im,0,0);
const P=(x,z)=>[(x-c.x0)/c.C/s,(z-c.z0)/c.C/s];for(const q of SB.coins){const [x,y]=P(q.x,q.z);g.fillStyle=q.rare?'#ff2020':'#f5c400';g.beginPath();g.arc(x,y,q.rare?5:2,0,7);g.fill();}for(const q of SB.gates){const [x,y]=P(q.x,q.z);g.fillStyle='#0040ff';g.beginPath();g.arc(x,y,7,0,7);g.fill();}{const [x,y]=P(player.x,player.y);g.fillStyle='#ff00ff';g.beginPath();g.arc(x,y,5,0,7);g.fill();}
return cv.toDataURL('image/png')})()"""
JS = r"""
window.__sb={
  put(gx,gy,deg,wy){const k=player,a=-deg*Math.PI/180;k.x=k.px=sbGX(gx);k.y=k.py=sbGZ(gy);k.a=k.ma=k.pa=k.pma=a;k.speed=0;k.wy=k.pwy=k.lastG=(wy==null?sbG(k.x,k.y,0):wy);k.wvy=0;k.gRate=0;k.air=false;k.big=false;k.drift=0;k.spin=0;k.boost=0;k.bpx=k.x;k.bpy=k.y;k.loop=null;k.idx=sbIdx(k,k.idx);},
  at(){const k=player;return {x:+(k.x/SB_M-.75).toFixed(2),y:+(3.5-k.y/SB_M).toFixed(2),h:Math.round(k.wy||0),sp:Math.round(k.speed),air:!!k.air};},
  run(n){for(let i=0;i<n;i++)update(STEP);return this.at();},
  /* straight ahead for n steps, the heading held */
  line(gx,gy,deg,n,wy){this.put(gx,gy,deg,wy);const a=-deg*Math.PI/180;let top=0;for(let i=0;i<n;i++){player.a=player.ma=a;update(STEP);top=Math.max(top,player.wy||0);}const r=this.at();r.top=Math.round(top);return r;},
  /* along the track from lap fraction f0 for n steps: the wheel is turned toward the track ahead, nothing else */
  lap(f0,n){const k=player,j0=Math.round(f0*N)%N,p=track[j0];k.x=k.px=p.x;k.y=k.py=p.y;k.idx=j0;k.a=k.ma=k.pa=k.pma=Math.atan2(p.ty,p.tx);k.speed=0;const gb=(x,y)=>SB.kind==='toy'?0:groundAt(x,y);k.wy=k.pwy=k.lastG=gb(p.x,p.y)+(p.ey||0);k.wvy=0;k.gRate=0;k.air=false;k.loop=null;k.glide=false;k.bpx=k.x;k.bpy=k.y;
    const c0=sbSave().c;let off=0,airs=0,worst=0,maxh=0,far=0,stuck=0,lx=k.x,ly=k.y,done=0,loops=0,wasLoop=false;
    for(let i=0;i<n;i++){const q=track[(k.idx+9)%N],want=Math.atan2(q.y-k.y,q.x-k.x);if(!k.loop){k.a+=angDiff(want,k.a)*.25;k.ma=k.a;}update(STEP);if(k.loop&&!wasLoop)loops++;wasLoop=!!k.loop;
      const pj=track[k.idx],lat=Math.abs((k.x-pj.x)*pj.nx+(k.y-pj.y)*pj.ny),dh=Math.abs((k.wy||0)-gb(k.x,k.y)-(pj.ey||0));if(!k.loop&&!k.glide){if(lat>(SB.kind==='toy'?TOYW()+4:WALLD))off++;if(k.air)airs++;else worst=Math.max(worst,dh);}maxh=Math.max(maxh,k.wy||0);
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
        await pg.evaluate("(a)=>{const b=document.getElementById('map-'+a[0]);if(b)b.click();}", [REG]); await pg.wait_for_timeout(3000)
        print('chosen:', await pg.evaluate("__ev(`JSON.stringify({map:MAPS[mapIdx].id,shown:[...document.querySelectorAll('#maps .mapc')].filter(b=>!b.hidden).map(b=>b.id.slice(4)),tabs:document.getElementById('mapCats').hidden})`)"))
        await pg.evaluate("(a)=>__ev(`goRace(MAPS.findIndex(m=>m.id==='${a[0]}'))`)", [REG])
        await pg.wait_for_function("document.getElementById('raceLd').hidden", timeout=900000)
        for i in range(400):
            if await pg.evaluate("__ev(`state`)") == 'race': break
            await pg.wait_for_timeout(500)
        print('started:', await pg.evaluate("__ev(`JSON.stringify({sbx:SBX,battle:BATTLE,karts:karts.length,coins:SB.coins.length,rare:SB.coins.filter(c=>c.rare).length,shapes:SB.shapes.length,cells:SB.hash?SB.hash.size:0,columns:SB.col?{squares:SB.col.nx*SB.col.nz,MB:+(SB.col.sp.byteLength/1e6).toFixed(1),triangles:SB.col.tris,things:SB.col.used,ms:SB.col.ms,filled:SB.col.cnt.reduce((a,b)=>a+(b?1:0),0)}:null,kartZ:[Math.round(player.y),Math.round(player.m.g.position.z)],start:[+(player.x/SB_M-.75).toFixed(2),+(3.5-player.y/SB_M).toFixed(2)]})`)"))
        await pg.wait_for_timeout(2500); await pg.screenshot(path=f'{SP}/sb_0.png')
        await pg.evaluate("(js)=>__ev(js)", JS)
        ev = lambda s: pg.evaluate("(js)=>__ev('JSON.stringify('+js+')')", s)
        bad = 0
        def say(name, r, ok):
            nonlocal bad; bad += not ok; print(('ok   ' if ok else 'FAIL ') + name, r, flush=True)
        KIND = json.loads(await ev('SB.kind'))
        if KIND != 'road': open(f'{SP}/sb_plan_{REG}.png', 'wb').write(__import__('base64').b64decode((await pg.evaluate("(js)=>__ev(js)", PLAN)).split(',')[1]))
        # every coin on the floor must be somewhere the kart can drive to from the track: a flood over the floor, square by square
        r = {'cannotReach': [], 'kind': 'road: no free ground'} if KIND == 'road' else json.loads(await ev("(()=>{const c=SB.col,C=c.C,gb=(x,z)=>SB.kind==='toy'?0:groundAt(x,z),seen=new Uint8Array(c.nx*c.nz),st=[];for(let j=0;j<N;j+=3){const p=track[j];if((p.ey||0)<1.5){const i=Math.floor((p.x-c.x0)/C),k=Math.floor((p.y-c.z0)/C),q=i*c.nz+k;if(!seen[q]){seen[q]=1;st.push(q);}}}"
            "while(st.length){const q=st.pop(),i=Math.floor(q/c.nz),k=q%c.nz;for(const [a,b] of [[1,0],[-1,0],[0,1],[0,-1]]){const ii=i+a,kk=k+b;if(ii<0||kk<0||ii>=c.nx||kk>=c.nz)continue;const n=ii*c.nz+kk;if(seen[n])continue;seen[n]=1;{const X=c.x0+(ii+.5)*C,Z=c.z0+(kk+.5)*C;if(sbBlocked(X,Z,gb(X,Z)))continue;}st.push(n);}}"
            "const lost=[];let fl=0;for(const q of SB.coins){if(q.y-gb(q.x,q.z)>14)continue;{const n=sbSurf(q.x,q.z);let tr=false;for(let e=0;e<n;e++)if(SB.S[e][2]>=0)tr=true;if(tr)continue;/* on the track: the lap test collects those */}fl++;let ok=false;for(const [a,b] of [[0,0],[6,0],[-6,0],[0,6],[0,-6]]){const i=Math.floor((q.x+a-c.x0)/C),k=Math.floor((q.z+b-c.z0)/C);if(seen[i*c.nz+k]&&!sbBlocked(q.x+a,q.z+b,gb(q.x+a,q.z+b)))ok=true;}if(!ok)lost.push([q.rare?q.id:'gold',Math.round(q.x),Math.round(q.z)]);}"
            "return {floorCoins:fl,rare:SB.coins.filter(q=>q.rare).map(q=>q.id.split(':')[1]+'@'+Math.round(q.y)),cannotReach:lost.slice(0,8)}})()"))
        say('coins: every one on the floor can be driven to', r, not r['cannotReach'])
        if REG != 'backyard':
            # a look at each hidden coin from the chase camera, the kart 60 units short of it on whichever side is open
            nv = json.loads(await ev("SB.coins.filter(q=>q.rare&&q.y<14).length"))
            for i in range(min(nv, 5)):
                await ev("(()=>{const q=SB.coins.filter(q=>q.rare&&q.y<14)[" + str(i) + "],k=player;for(const a of [0,3.14,1.57,-1.57,.78,-.78,2.36,-2.36]){const x=q.x-Math.cos(a)*60,z=q.z-Math.sin(a)*60;let ok=!sbBlocked(x,z,0);for(let d=10;d<60&&ok;d+=10)if(sbBlocked(q.x-Math.cos(a)*d,q.z-Math.sin(a)*d,0))ok=false;if(ok){k.x=k.px=x;k.y=k.py=z;k.a=k.ma=k.pa=k.pma=a;k.speed=0;k.wy=k.pwy=k.lastG=0;k.air=false;k.wvy=0;k.gRate=0;k.loop=null;k.bpx=x;k.bpy=z;k.idx=sbIdx(k,k.idx);camSnap=true;cam.a=a;break;}}state='countdown';cd=1e9;return 1})()")
                await pg.wait_for_timeout(1200); await pg.screenshot(path=f'{SP}/sb_{REG}_v{i}.png')
            await ev("(()=>{state='race';return 1})()")
            r2 = json.loads(await ev("(()=>{const p0=player.prog;player.prog=LAPS*N+50;for(let i=0;i<30;i++)update(STEP);const r={finished:!!player.finished,state:state};player.prog=p0;return r})()"))
            say('no finish: more than the race distance on the clock', r2, not r2['finished'] and r2['state'] == 'race')
            r = json.loads(await ev("window.__sb.lap(.02,90000)"))
            say('lap: the whole track by its own heights', r, r['reached'] > .98 and r['off'] < 60 and r['worstHeightGap'] < (6.5 if KIND == 'toy' else 24) and r['stuck'] == 0 and r['coins'] > 10)
            await pg.wait_for_timeout(1500); await pg.screenshot(path=f'{SP}/sb_{REG}_lap.png')
        if REG == 'backyard':
            # pictures from the chase camera: coins on the patio, the ring round the football, a pepperoni coin in the goal, nose against the back fence, the shed's door
            for i, (x, y, d) in enumerate([(-13.2, .8, 0), (5.2, 3.9, 0), (9.9, 4.9, 60), (6.0, 6.6, 90), (-10.9, 3.2, 100), (0.6, 4.0, 60)]):
                await ev(f"(()=>{{window.__sb.put({x},{y},{d});camSnap=true;cam.a=player.ma;return 1}})()"); await pg.wait_for_timeout(700); await pg.screenshot(path=f'{SP}/sb_v{i}.png')
            W = [  # name, x, y, heading, steps, test on the end place
                ('back fence', 5.5, 3.2, 90, 1500, lambda r: 6.9 < r['y'] <= 6.99), ('east fence', 9.5, 2.6, 0, 1200, lambda r: 11.5 < r['x'] <= 11.59),
                ('house wall', -5, 1.3, 270, 900, lambda r: 0 < r['y'] < .12), ('west fence', -11.5, 1.0, 180, 1200, lambda r: -13.89 <= r['x'] < -13.78),
                ('shed, from the east', -8.9, 5.5, 180, 900, lambda r: -10.0 < r['x'] < -9.9), ('shed, from the south', -11.2, 3.0, 90, 900, lambda r: 4.3 < r['y'] < 4.45),
                ('the tree, under the spiral', 3.1, 3.2, 90, 1200, lambda r: 4.75 < r['y'] < 4.9 and r['h'] < 6), ('a flowerpot', 5.0, 1.5, 270, 700, lambda r: .6 < r['y'] < .85),
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
        # ---- the passages: out through each gate of this region and back again, in real time (the game drives; the test only points the kart)
        gates = json.loads(await ev("SB.gates.map(g=>({id:g.id,to:g.to,at:g.at}))"))
        aim = lambda gid, back: ("(()=>{const g=SB.gates.find(q=>q.id==='" + gid + "'),k=player,d=" + str(back) + ";if(g.road){const j=((g.j-Math.round(d/(T.L/N)))%N+N)%N,p=track[j];k.x=k.px=p.x-p.nx*RW*.5;k.y=k.py=p.y-p.ny*RW*.5;k.a=k.ma=k.pa=k.pma=p.ang;}else{k.x=k.px=g.x-g.nx*d;k.y=k.py=g.z-g.nz*d;k.a=k.ma=k.pa=k.pma=Math.atan2(g.nz,g.nx);}k.speed=90;k.wy=k.pwy=k.lastG=g.road?g.y:SBF?sbG(k.x,k.y,g.y+3):g.y;k.wvy=0;k.air=false;k.glide=false;k.loop=null;k.spin=0;k.bpx=k.x;k.bpy=k.y;if(g.road)k.idx=((g.j-Math.round(d/(T.L/N)))%N+N)%N;else k.idx=sbIdx(k,k.idx);camSnap=true;cam.a=k.ma;state='race';return 1})()")
        async def through(gid, to, tag):
            import time
            await ev(aim(gid, 170)); await pg.wait_for_timeout(250); await pg.screenshot(path=f'{SP}/sb_gate_{tag}_0.png')
            t0 = time.time(); shots = 1
            for i in range(600):
                st = json.loads(await ev("(()=>{const g=SB.gates.find(q=>q.id==='" + gid + "'),k=player;if(g&&g.road&&state==='race'&&!SB.trav){const d=(g.x-k.x)*g.nx+(g.z-k.y)*g.nz;if(d>4)k.a=k.ma=Math.atan2(g.z+g.nz*6-k.y,g.x+g.nx*6-k.x);}return {reg:SB.regId,st:state,trav:!!SB.trav,o:SB.ductO||0,sbx:SBX}})()"))
                if shots == 1 and st['o'] > .5: await pg.screenshot(path=f'{SP}/sb_gate_{tag}_1.png'); shots = 2
                if st['reg'] == to and st['st'] == 'race' and not st['trav']: break
                await pg.wait_for_timeout(100)
            secs = round(time.time() - t0, 1); await pg.wait_for_timeout(900); await pg.screenshot(path=f'{SP}/sb_gate_{tag}_2.png')
            await pg.wait_for_timeout(1500); await pg.screenshot(path=f'{SP}/sb_gate_{tag}_3.png')
            r = json.loads(await ev("(()=>{const k=player,b=SB.col?SB.col.b:[-1e9,1e9,-1e9,1e9];return {region:SB.regId,state:state,sbx:SBX,battle:BATTLE,karts:karts.length,inRoom:k.x>b[0]&&k.x<b[1]&&k.y>b[2]&&k.y<b[3],speed:Math.round(k.speed),duct:SB.ductO||0,coins:SB.coins.length,hud:document.getElementById('sbHud').textContent.slice(0,22)}})()"))
            r['seconds'] = secs
            say(f'passage: {tag}', r, r['region'] == to and r['state'] == 'race' and r['sbx'] and r['karts'] == 1 and r['inRoom'] and r['duct'] == 0 and secs < 60)
        for g in gates:
            await through(g['id'], g['to'], f"{REG}-to-{g['to']}")
            if json.loads(await ev("SB.regId")) == g['to']: await through(g['at'], REG, f"{g['to']}-to-{REG}")
            else: break
        # ---- a race from the start line: the marker, the offer, the race, and back to Sandbox
        await ev("(()=>{const f=SB.flag,p=track[0],k=player;k.x=k.px=f.x-p.tx*70;k.y=k.py=f.z-p.ty*70;k.a=k.ma=k.pa=k.pma=Math.atan2(p.ty,p.tx);k.speed=0;k.wy=k.pwy=k.lastG=f.y;k.wvy=0;k.air=false;k.loop=null;k.bpx=k.x;k.bpy=k.y;k.idx=SBF?sbIdx(k,k.idx):(N-Math.round(70/(T.L/N)))%N;camSnap=true;cam.a=k.ma;state='countdown';cd=1e9;return 1})()")
        await pg.wait_for_timeout(1200); await pg.screenshot(path=f'{SP}/sb_race_{REG}_0.png')
        await ev("(()=>{const f=SB.flag,k=player;k.x=k.px=f.x;k.y=k.py=f.z;k.bpx=k.x;k.bpy=k.y;k.speed=0;if(!SBF){k.idx=0;k.wy=k.pwy=k.lastG=f.y;}sbPark(true);state='race';return 1})()"); await pg.wait_for_timeout(700)
        r = json.loads(await ev("(()=>{const b=document.getElementById('sbRace');return {offered:!!b&&!b.hidden,says:b?b.textContent:''}})()")); await pg.screenshot(path=f'{SP}/sb_race_{REG}_1.png')
        say('race: offered at the start line', r, r['offered'] and 'Race here' in r['says'])
        await pg.evaluate("document.getElementById('sbRace').click()")
        await pg.wait_for_function("document.getElementById('raceLd').hidden", timeout=900000)
        for i in range(200):
            if await pg.evaluate("__ev(`state`)") in ('race', 'countdown') and await pg.evaluate("__ev(`karts.length`)") == 8: break
            await pg.wait_for_timeout(300)
        await pg.wait_for_timeout(1500); await pg.screenshot(path=f'{SP}/sb_race_{REG}_2.png')
        r = json.loads(await ev("({mode:mode,karts:karts.length,sbx:SBX,battle:BATTLE,state:state,back:SB.back,offer:!!(document.getElementById('sbRace')&&!document.getElementById('sbRace').hidden),laps:LAPS,map:MAPS[mapIdx].id})"))
        say('race: an ordinary race on this track', r, r['mode'] == 'single' and r['karts'] == 8 and not r['sbx'] and not r['battle'] and r['back'] == REG and not r['offer'] and r['map'] == REG)
        await pg.evaluate("__ev(`toMenu()`)")
        for i in range(300):
            if await pg.evaluate("__ev(`state==='race'&&SBX&&karts.length===1`)"): break
            await pg.wait_for_timeout(300)
        r = json.loads(await ev("({mode:mode,karts:karts.length,sbx:SBX,state:state,region:SB.regId,back:SB.back,menu:!document.getElementById('menu').hidden})"))
        say('race: leaving it comes back to Sandbox', r, r['mode'] == 'sb' and r['sbx'] and r['karts'] == 1 and r['region'] == REG and not r['back'] and not r['menu'])
        print('saved:', await pg.evaluate("localStorage.getItem('crust-sb')"))
        await pg.evaluate("__ev(`toMenu()`)"); await pg.wait_for_timeout(1500)
        print('back at the menu:', await pg.evaluate("__ev(`JSON.stringify({sbx:SBX,battle:BATTLE,karts:karts.length,hud:!document.getElementById('sbHud')||document.getElementById('sbHud').hidden,cls:document.body.classList.contains('battle')})`)"))
        print('errors', errs[:6]); print('SANDBOX TEST', 'FAILED' if bad or errs else 'passed')
        await b.close()
asyncio.run(main())
