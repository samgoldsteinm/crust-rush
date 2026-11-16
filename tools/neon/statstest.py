"""Part stats add up (web v197, patch32):   py.cmd tools/neon/statstest.py
For EVERY body x wheel x glider: the build's bars are the vehicle's own bars plus the wheels' and the glider's card numbers (held to 0..12),
and the driving numbers come from the same sum. Writes every build's statMods to D:/crust-rush/scratch/stats/web_stats.json
({"b,w,g":[spd,acc,hnd,wgt,off]}, six places) for the PC to be compared with, and takes a picture of the garage with Slicks and the
Slice Wing on a body whose own speed is neutral: the speed row must read +2."""
import asyncio, json, os
from playwright.async_api import async_playwright
OUT = 'D:/crust-rush/scratch/stats'; os.makedirs(OUT, exist_ok=True)
JS = r"""(()=>{const bad=[],tab={};let n=0;const was=statsOn;statsOn=true;
for(let b=0;b<BODIES.length;b++)for(let w=0;w<WHEELS.length;w++)for(let g=0;g<GLIDERS.length;g++){const B={b,w,g,p:0},bd=BODIES[b],wh=wheelOf(B),gl=GLIDERS[g],base=statBarsOf(B,false),tot=statBarsOf(B,true),m=statMods(B);n++;
  for(let i=0;i<5;i++){const own=Math.round(6+1.5*4*Math.tanh(1.5*bd.st[i]/4)),bike=!!(bd.bike&&bd.bw),wantBase=Math.max(0,Math.min(12,own+(bike?wh.st[i]:0))),want=Math.max(0,Math.min(12,own+wh.st[i]+gl.st[i]));
    if(base[i]!==wantBase||tot[i]!==want)bad.push([bd.id,WHEELS[w].id,gl.id,i,base[i],wantBase,tot[i],want]);
    const e=Math.max(-4,Math.min(4,4*Math.tanh(1.5*bd.st[i]/4)+(wh.st[i]+gl.st[i])/1.5)),v=[1+.014*e,/* (patch 38: was .022) */Math.max(.62,1+.09*e),1+.05*e,1+.12*e,.9*e][i],got=[m.spd,m.acc,m.hnd,m.wgt,m.off][i];if(Math.abs(v-got)>1e-9)bad.push(['mods',bd.id,WHEELS[w].id,gl.id,i,got,v]);}
  tab[b+','+w+','+g]=[m.spd,m.acc,m.hnd,m.wgt,m.off].map(x=>+x.toFixed(6));}
statsOn=false;const off=statMods({b:1,w:1,g:1,p:0});statsOn=was;
return {n,bad:bad.slice(0,12),nbad:bad.length,off,proto:NET_PROTO,tab,neutral:BODIES.findIndex(q=>q.st[0]===0&&!q.bike),slick:WHEELS.findIndex(q=>q.id==='slick'),wing:GLIDERS.findIndex(q=>q.id==='wing')};})()"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(channel='chromium', args=['--use-angle=d3d11', '--enable-gpu', '--ignore-gpu-blocklist', '--enable-webgl'])
        ctx = await b.new_context(viewport={'width': 1280, 'height': 720}, service_workers='block'); pg = await ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto('http://localhost:8771/webcopy6/index.html')
        await pg.wait_for_function("document.getElementById('menu')&&!document.getElementById('menu').hidden", timeout=600000)
        r = json.loads(await pg.evaluate("(js)=>__ev('JSON.stringify('+js+')')", JS))
        json.dump(r['tab'], open(f'{OUT}/web_stats.json', 'w'), separators=(',', ':'), sort_keys=True)
        print('builds', r['n'], 'wrong', r['nbad'], r['bad'], 'stats off', r['off'], 'NET_PROTO', r['proto'])
        # the garage: Slicks and the Slice Wing on a neutral-speed body
        await pg.evaluate("__ev(`playerBuild={b:%d,w:%d,g:%d,p:0,t:''};try{openGarage();}catch(e){String(e)}`)" % (r['neutral'], r['slick'], r['wing']))
        await pg.wait_for_timeout(2500)
        row = await pg.evaluate("__ev(`(()=>{try{showStats(playerBuild);}catch(e){}const r=document.querySelectorAll('#gStats .st-row');return [...r].map(q=>q.querySelector('.st-d').textContent).join(' | ');})()`)")
        print('garage rows (speed first), body', r['neutral'], ':', row)
        await pg.screenshot(path=f'{OUT}/garage_slick_wing.png')
        print('STATS TEST', 'passed' if r['nbad'] == 0 and r['proto'] >= 111 and not errs else 'FAILED', 'errors', errs[:4]); await b.close()
asyncio.run(main())
