"""A phone session: several races one after another in ONE page, in the Safari engine set up as an iPhone (touch, so the
memory saver freeCanvases() runs). After each track loads it lists every scenery texture that is reading an emptied (1x1)
canvas AFTER it was emptied: those are drawn BLACK on a real phone. Want: black [] and bad uploads 0 on every line, and PHONE TEST passed.
usage: py.cmd tools/neon/phonetest.py <map> <map> ...     (repeat a map to test coming back to it)   pictures: scratch/phone_<n>.png
Why it exists: web v187. Every other test loads one track per page, on a desktop, where nothing is ever emptied."""
import asyncio, sys, os, json
from playwright.async_api import async_playwright
MAPS = sys.argv[1:]; SP = 'D:/crust-rush/scratch'; Q = os.environ.get('Q', 'fast')
# the page is watched from its first line: which canvases get emptied, and whether one is ever sent to the graphics chip afterwards (that is the bug)
WATCH = r"""(()=>{const F=window.__freed=new WeakSet(),S=window.__stale=[];const d=Object.getOwnPropertyDescriptor(HTMLCanvasElement.prototype,'width');
Object.defineProperty(HTMLCanvasElement.prototype,'width',{get(){return d.get.call(this)},set(v){if(v<=1&&d.get.call(this)>1){F.add(this);let th='';try{const t=document.createElement('canvas');d.set.call(t,96);t.height=96;t.getContext('2d').drawImage(this,0,0,96,96);th=t.toDataURL('image/png');}catch(e){}(window.__was=window.__was||new WeakMap()).set(this,[d.get.call(this)+'x'+this.height,th]);window.__nfreed=(window.__nfreed||0)+1;}else if(v>1)F.delete(this);d.set.call(this,v)},configurable:true});
for(const C of [window.WebGL2RenderingContext,window.WebGLRenderingContext])if(C)for(const fn of ['texImage2D','texSubImage2D']){const o=C.prototype[fn];C.prototype[fn]=function(...a){for(const x of a)if(x instanceof HTMLCanvasElement&&F.has(x)){S.push(x);try{const gl=this,pr=gl.getParameter(gl.CURRENT_PROGRAM),unit=gl.getParameter(gl.ACTIVE_TEXTURE)-gl.TEXTURE0;let nm='?';if(pr){const n=gl.getProgramParameter(pr,gl.ACTIVE_UNIFORMS);for(let i=0;i<n;i++){const u=gl.getActiveUniform(pr,i);if(u&&(u.type===gl.SAMPLER_2D)){const l=gl.getUniformLocation(pr,u.name);if(l&&gl.getUniform(pr,l)===unit)nm=u.name;}}}window.__pr=pr;(window.__who=window.__who||[]).push('input '+nm+' of shader '+window.__ev("(()=>{const q=renderer.info.programs.find(p=>p.program===window.__pr);return q?(q.name+' '+String(q.cacheKey).slice(0,160)):'?'})()"));}catch(e){(window.__who=window.__who||[]).push('gl ask failed '+e)}try{window.__x=x;(window.__who=window.__who||[]).push(window.__ev("(()=>{const o=[],x=window.__x,seen=new Set();const dig=(v,path,d)=>{if(!v||typeof v!=='object'||seen.has(v))return;seen.add(v);if(v.isTexture){if(v.image===x)o.push(path);return;}if(d>3||v.isObject3D||v.isBufferGeometry||v.isBufferAttribute||ArrayBuffer.isView(v))return;for(const k in v){let c;try{c=v[k];}catch(e){continue;}if(c&&typeof c==='object')dig(c,path+'.'+k,d+1);}};const obj=(m,root)=>{let par='',q=m;while(q.parent){q=q.parent;par=(q.name||q.type)+'/'+par;}const id=root+':'+par+(m.name||m.type);const ms=m.material?(Array.isArray(m.material)?m.material:[m.material]):[];ms.forEach((mt,i)=>{if(mt){seen.delete(mt);dig(mt,id+':'+(mt.name||mt.type)+'['+i+']',0);try{const pr=renderer.properties.get(mt);if(pr&&pr.uniforms)for(const k in pr.uniforms){const u=pr.uniforms[k];if(u&&u.value&&u.value.isTexture&&u.value.image===x)o.push(id+':'+(mt.name||mt.type)+'#'+(mt.color?mt.color.getHexString():'')+' shader input '+k+' (material.'+k+' is '+(mt[k]?'set':'not set')+')');}}catch(e){}}});for(const k of ['customDepthMaterial','customDistanceMaterial','userData'])if(m[k])dig(m[k],id+'.'+k,0);};scene.traverse(m=>obj(m,'scene'));if(typeof camera!=='undefined'&&camera)camera.traverse(m=>obj(m,'camera'));dig(scene.background,'scene.background',0);dig(scene.environment,'scene.environment',0);return o.slice(0,4).join(' ; ')+' ('+o.length+')'})()"));}catch(e){(window.__who=window.__who||[]).push('scan failed '+e)}(window.__st=window.__st||[]).push(new Error().stack.split('\n').slice(1,40).map(l=>l.replace(/@.*?:(\d+):\d+$/,'@$1')).filter(l=>!/^[a-zA-Z]{0,2}@/.test(l)).slice(0,10).join(' < '));}return o.apply(this,a)}}})()"""
STALE = """__ev(`(()=>{const o=[],S=new Set(window.__stale);const look=m=>{const ms=m.material?(Array.isArray(m.material)?m.material:[m.material]):[];for(const mt of ms){if(!mt)continue;const ts=[];for(const p in mt){const v=mt[p];if(v&&v.isTexture)ts.push(v);}
if(mt.uniforms)for(const p in mt.uniforms){const v=mt.uniforms[p]&&mt.uniforms[p].value;if(v&&v.isTexture)ts.push(v);}
for(const t of ts)if(S.has(t.image))o.push((m.name||m.type)+':'+(mt.name||mt.type));}};scene.traverse(look);if(typeof _warmG!=='undefined'&&_warmG)_warmG.traverse(look);for(const k of ['background','environment'])if(scene[k]&&S.has(scene[k].image))o.push('scene.'+k);const wz=[...S].map(c=>(window.__was&&window.__was.get(c))||['?','']),was=wz.map(w=>w[0]);window.__thumbs=wz.map(w=>w[1]);const n=window.__stale.length,f=window.__nfreed||0;window.__stale.length=0;window.__nfreed=0;const st=[...new Set(window.__st||[])];window.__st=[];const who=window.__who||[];window.__who=[];return JSON.stringify({black:[...new Set(o)],uploads:n,emptied:f,was:was,held:who,from:st})})()`)"""
def judge(r):
    """is this line a fault? An upload into three.js's own shadow pass is not: its one shared shadow material keeps the map of the last
    thing that cast a shadow (three r149, WebGLShadowMap) and never tests it, so an emptied canvas there changes no pixel."""
    d = json.loads(r); ins = [h for h in d['held'] if h.startswith('input ')]
    real = [h for h in ins if 'shader MeshDepthMaterial' not in h and 'shader MeshDistanceMaterial' not in h]
    fault = bool(d['black']) or bool(real) or d['uploads'] > len(ins)
    return fault, json.dumps({'black': d['black'], 'bad uploads': len(real) + max(0, d['uploads'] - len(ins)), 'shadow-pass uploads (harmless)': len(ins) - len(real), 'emptied': d['emptied'], **({'held': d['held'], 'from': d['from'], 'was': d['was']} if fault else {})})


async def main():
    async with async_playwright() as p:
        b = await p.webkit.launch()
        ctx = await b.new_context(**{k: v for k, v in p.devices['iPhone 15 Pro landscape'].items() if k != 'default_browser_type'}, service_workers='block')
        pg = await ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.add_init_script(WATCH)
        await pg.goto('http://localhost:8771/webcopy6/index.html')
        await pg.wait_for_function("document.getElementById('menu')&&!document.getElementById('menu').hidden", timeout=600000)
        await pg.wait_for_timeout(7000)                             # the memory saver runs 5 s after the game has started
        print('menu', await pg.evaluate(STALE), flush=True)
        bad = 0
        for n, mp in enumerate(MAPS):
            await pg.evaluate("(a)=>__ev(`qKey='" + Q + "';applyQuality();clsKey='medium';mode='single';introSkip=true;goRace(MAPS.findIndex(m=>m.id==='${a[0]}'))`)", [mp])
            await pg.wait_for_function("document.getElementById('raceLd').hidden", timeout=900000)
            for i in range(400):
                if await pg.evaluate("__ev(`state`)") == 'race': break
                await pg.wait_for_timeout(500)
            await pg.evaluate("__ev(`player.auto=true;let n=0;while(n<60000&&!(player.idx>=110&&player.idx<122)){update(STEP);n++;}`)")
            await pg.wait_for_timeout(8000)                         # long enough for the memory saver to run on this track (4 s and 6 s after loading)
            f, r = judge(await pg.evaluate(STALE)); bad += f
            for i, th in enumerate(await pg.evaluate('window.__thumbs||[]')):
                if th: open(f'{SP}/phone_stale_{n}_{i}.png', 'wb').write(__import__('base64').b64decode(th.split(',')[1]))
            await pg.screenshot(path=f'{SP}/phone_{n}.png', timeout=900000)
            print(n, mp, r, flush=True)
            await pg.evaluate("__ev(`toMenu()`)"); await pg.wait_for_timeout(8000)
            f, r = judge(await pg.evaluate(STALE)); bad += f
            print('   back at the menu', r, flush=True)
        print('errors', errs[:6]); print('PHONE TEST', 'FAILED' if bad or errs else 'passed')
        await b.close()
asyncio.run(main())
