"""Sandbox, the whole world in one sitting:   py.cmd tools/neon/sbworld.py [quality] [maps...]   (default: fast, every place)
Starts Sandbox in the back garden, then fast-travels to every place in turn (the map's own travel: sbTravel to a start line) and in each:
  lap      the whole track forwards with only the wheel turned toward the track ahead: reached > .98, never stuck
  back     the whole track the wrong way round: a list of where the kart was stopped (want none)
  arches   every passage's mouth can be driven to from the track (a flood over the open ground); every hidden coin on the ground too
  build    how long reading the walls took (ms)
Prints one line a place and a verdict. scratch/sbworld_<map>.png is the view on arrival."""
import asyncio, json, re, sys, time
from playwright.async_api import async_playwright
Q = sys.argv[1] if len(sys.argv) > 1 else 'fast'; ONLY = sys.argv[2:]; SP = 'D:/crust-rush/scratch'
HELP = re.search(r'JS = r"""(.*?)"""', open('D:/crust-rush/source/tools/neon/sbtest.py', encoding='utf-8').read(), re.S).group(1)
CHECK = r"""(()=>{const out={reg:SB.regId,kind:SB.kind,gates:SB.gates.length,coins:SB.coins.length,rare:SB.coins.filter(c=>c.rare).length,ms:SB.col?Math.round(SB.col.ms||0):0};
 const gb=(x,z)=>SB.kind==='toy'?0:groundAt(x,z),k=player;sbPark(false);
 if(SB.col){const c=SB.col,C=c.C,seen=new Uint8Array(c.nx*c.nz),st=[];for(let j=0;j<N;j+=3){const p=track[j];if((p.ey||0)<1.5){const i=Math.floor((p.x-c.x0)/C),q0=Math.floor((p.y-c.z0)/C),q=i*c.nz+q0;if(i>=0&&q0>=0&&i<c.nx&&q0<c.nz&&!seen[q]){seen[q]=1;st.push(q);}}}
  let open=0;while(st.length){const q=st.pop(),i=Math.floor(q/c.nz),kk=q%c.nz;open++;for(const [a,b] of [[1,0],[-1,0],[0,1],[0,-1]]){const ii=i+a,k2=kk+b;if(ii<0||k2<0||ii>=c.nx||k2>=c.nz)continue;const n=ii*c.nz+k2;if(seen[n])continue;const X=c.x0+(ii+.5)*C,Z=c.z0+(k2+.5)*C;if(sbBlocked(X,Z,gb(c.x0+(i+.5)*C,c.z0+(kk+.5)*C)))continue;seen[n]=1;st.push(n);}}
  const at=(x,z)=>{for(const [a,b] of [[0,0],[7,0],[-7,0],[0,7],[0,-7]]){const i=Math.floor((x+a-c.x0)/C),k2=Math.floor((z+b-c.z0)/C);if(i>=0&&k2>=0&&i<c.nx&&k2<c.nz&&seen[i*c.nz+k2])return true;}return false;};
  out.gatesCut=SB.gates.filter(g=>!g.road&&!at(g.x-g.nx*(g.plain?60:30),g.z-g.nz*(g.plain?60:30))).map(g=>g.id);out.rareCut=SB.coins.filter(q=>q.rare&&q.y-gb(q.x,q.z)<14&&!at(q.x,q.z)).length;out.openMm2=Math.round(open*C*C/1e4);}
 else{out.gatesCut=[];out.rareCut=0;}
 const lap=window.__sb.lap(.02,120000);out.lap={reached:lap.reached,off:lap.off,gap:lap.worstHeightGap,stuck:lap.stuck,loops:lap.loops,coins:lap.coins};
 /* the wrong way round */{const place=j=>{const p=track[j];k.x=k.px=p.x;k.y=k.py=p.y;k.idx=j;k.a=k.ma=k.pa=k.pma=Math.atan2(-p.ty,-p.tx);k.speed=0;k.wy=k.pwy=k.lastG=gb(p.x,p.y)+(p.ey||0);k.wvy=0;k.gRate=0;k.air=false;k.loop=null;k.glide=false;k.bpx=k.x;k.bpy=k.y;};
  let best=N-8,since=0,total=0;place(best);const stops=[];for(let i=0;i<160000&&total<N-30&&stops.length<12;i++){const q=track[((k.idx-9)%N+N)%N],want=Math.atan2(q.y-k.y,q.x-k.x);if(!k.loop){k.a+=angDiff(want,k.a)*.25;k.ma=k.a;}update(STEP);
   let d=best-k.idx;if(d<-N/2)d+=N;if(d>N/2)d-=N;if(d>0&&d<(GLIDE?((GLIDE.j1-GLIDE.rj+N)%N)+90:60)){/* (a canyon crossed the wrong way round sets the kart down on its far side: that is progress) */total+=d;best=k.idx;since=0;}else since++;
   if(since>600){stops.push(+(best/N).toFixed(3));const nj=((best-26)%N+N)%N;total+=26;best=nj;place(nj);since=0;}}out.back=stops;}
 {const p=track[(N-6)%N];k.x=k.px=p.x;k.y=k.py=p.y;k.idx=(N-6)%N;k.a=k.ma=k.pa=k.pma=p.ang;k.speed=0;k.wy=k.pwy=k.lastG=gb(p.x,p.y)+(p.ey||0);k.air=false;k.loop=null;k.glide=false;k.bpx=k.x;k.bpy=k.y;sbPark(true);}
 return out})()"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(channel='chromium', args=['--use-angle=d3d11', '--enable-gpu', '--ignore-gpu-blocklist', '--enable-webgl'])
        ctx = await b.new_context(viewport={'width': 1280, 'height': 720}, service_workers='block'); pg = await ctx.new_page(); errs = []; bad = 0
        pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        ev = lambda s: pg.evaluate("(js)=>__ev('JSON.stringify('+js+')')", s)
        await pg.goto('http://localhost:8771/webcopy6/index.html')
        await pg.wait_for_function("document.getElementById('menu')&&!document.getElementById('menu').hidden", timeout=600000)
        await pg.evaluate("__ev(`qKey='" + Q + "';applyQuality();clsKey='medium';introSkip=true;document.querySelector('#modeSeg button[data-m=sb]').click();`)")
        await pg.wait_for_timeout(1500); await pg.evaluate("__ev(`{const i=MAPS.findIndex(m=>m.id==='backyard');mapIdx=i;loadMap(i,false);resetRace(true);}`)"); await pg.wait_for_timeout(2500)
        await pg.evaluate("__ev(`goRace(mapIdx)`)"); print('started', flush=True)
        await pg.wait_for_function("document.getElementById('raceLd').hidden", timeout=900000)
        for i in range(400):
            if await pg.evaluate("__ev(`state`)") == 'race': break
            await pg.wait_for_timeout(500)
        await pg.evaluate("(js)=>__ev(js)", HELP)
        ids = json.loads(await ev("MAPS.filter(m=>sbRegOf(m.id)).map(m=>m.id)"))
        if ONLY: ids = [i for i in ids if i in ONLY]
        print(len(ids), 'places', flush=True)
        for rid in ids:
            t0 = time.time(); await ev("(()=>{sbPark(false);if(state==='paused')togglePause();sbTravel({to:'" + rid + "',start:true});return 1})()")
            for i in range(900):
                st = json.loads(await ev("({reg:SB.regId,st:state,trav:!!SB.trav})"))
                if st['reg'] == rid and st['st'] == 'race' and not st['trav']: break
                await pg.wait_for_timeout(100)
            secs = round(time.time() - t0, 1); await ev("(()=>{sbPark(true);return 1})()"); await pg.wait_for_timeout(900); await pg.screenshot(path=f'{SP}/sbworld_{rid}.png')
            try: r = json.loads(await ev(CHECK))
            except Exception as e: r = {'error': str(e)[:300]}
            lap = r.get('lap', {}); ok = 'error' not in r and r.get('reg') == rid and lap.get('reached', 0) > .98 and lap.get('stuck', 1) == 0 and not r.get('back') and not r.get('gatesCut') and not r.get('rareCut') and r.get('gates', 0) > 0
            bad += not ok; r['travel_s'] = secs
            print(('ok   ' if ok else 'FAIL ') + rid, json.dumps(r), flush=True)
        mem = await pg.evaluate("performance.memory?Math.round(performance.memory.usedJSHeapSize/1e6):0")
        print('heap MB', mem, 'errors', errs[:5]); print('SANDBOX WORLD TEST', 'FAILED' if bad or errs else 'passed'); await b.close()
asyncio.run(main())
