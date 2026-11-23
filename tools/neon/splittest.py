"""Split screen on the web (patch 115 on):   py.cmd tools/neon/splittest.py [menu|race|full]
Two pretend controllers (navigator.getGamepads replaced before the game loads).
  menu   Players 2 on the home screen; driver -> kart -> player 2's driver (choose controller: a press on pad 2) -> player 2's kart
         -> track; player 1's driver and kart are kept; player 2's saved.
  race   (patch 116 on) a split race on margherita: both karts driven, pictures.
Pictures D:/crust-rush/scratch/split_*.png."""
import asyncio, json, sys
from playwright.async_api import async_playwright
WHAT = sys.argv[1] if len(sys.argv) > 1 else 'menu'
INIT = """(()=>{const b=()=>({pressed:false,touched:false,value:0});const mk=(i,id)=>({id,index:i,connected:true,mapping:'standard',timestamp:1,axes:[0,0,0,0],buttons:Array.from({length:17},b),vibrationActuator:null});
const pads=[mk(0,'Test pad A (STANDARD GAMEPAD Vendor: 045e Product: 0b13)'),mk(1,'Test pad B (STANDARD GAMEPAD Vendor: 054c Product: 0ce6)')];
window.__pads=pads;navigator.getGamepads=()=>pads;window.__axes=(p,a)=>{pads[p].axes=a;pads[p].timestamp++;};window.__btn=(p,i,on)=>{pads[p].buttons[i]={pressed:!!on,touched:!!on,value:on?1:0};pads[p].timestamp++;};})()"""
SH = 'D:/crust-rush/scratch/split_%s.png'


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(channel='chromium', args=['--use-angle=d3d11', '--enable-gpu', '--ignore-gpu-blocklist', '--enable-webgl'])
        ctx = await b.new_context(viewport={'width': 1280, 'height': 720}, service_workers='block'); await ctx.add_init_script(INIT); pg = await ctx.new_page(); errs = []; bad = 0
        pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        ev = lambda s: pg.evaluate("(js)=>__ev('JSON.stringify('+js+')')", s)
        async def js(s): return json.loads(await ev(s))
        def say(name, r, ok):
            nonlocal bad; bad += not ok; print(('ok   ' if ok else 'FAIL ') + name, r, flush=True)
        async def press(pad, i): await pg.evaluate("([p,i])=>window.__btn(p,i,true)", [pad, i]); await pg.wait_for_timeout(120); await pg.evaluate("([p,i])=>window.__btn(p,i,false)", [pad, i]); await pg.wait_for_timeout(250)
        async def click(sel): await pg.evaluate("(s)=>document.querySelector(s).click()", sel); await pg.wait_for_timeout(500)
        await pg.goto('http://localhost:8771/webcopy6/index.html')
        await pg.wait_for_function("document.getElementById('menu')&&!document.getElementById('menu').hidden", timeout=600000)
        await pg.evaluate("__ev(`qKey='fast';applyQuality();clsKey='medium';introSkip=true;localStorage.removeItem('crust-p2pad');localStorage.removeItem('crust-build2');SPLIT.pid=-1;SPLIT.pidId='';SPLIT.build=null;mode='single';refreshMenu();goStep('home');`)")
        await pg.wait_for_timeout(600)
        if WHAT != 'menu':
            await race(pg, js, say, press)
            print('errors', errs[:5]); print('SPLIT TEST', WHAT, 'FAILED' if bad or errs else 'passed'); await b.close(); return
        vis = await js("!$('plySec').hidden")
        await click('#plySeg button[data-n="2"]')
        st = await js("({n:SPLIT.n,store:localStorage.getItem('crust-players'),note:$('plyNote').textContent})")
        await pg.screenshot(path=SH % 'home')
        say('home: Players shown, 2 picked and kept', st, vis and st['n'] == 2 and st['store'] == '2')
        p1 = await js("({sel:selected,build:JSON.stringify(playerBuild)})")
        await click('#toDriver'); await click('#garageBtn'); await pg.wait_for_timeout(800)
        gd = await js("({done:$('gDone').textContent,step:document.querySelector('#garage .g-step').textContent,open:garageOpen})")
        await pg.screenshot(path=SH % 'kart1')
        say('player 1 garage: its Done button leads to player 2', gd, gd['open'] and 'Player 2' in gd['done'])
        await click('#gDone'); await pg.wait_for_timeout(600)
        d2 = await js("({step:menuStep,sw:SPLIT.sw,h:document.querySelector('[data-step=\"driver\"] h2').textContent,pad:!$('p2Pad').hidden,say:$('p2PadSay').textContent,sel:selected,taken:[...document.querySelectorAll('.card.taken')].map(e=>e.id)})")
        await pg.screenshot(path=SH % 'driver2')
        say('player 2 driver screen', d2, d2['sw'] and 'Player 2' in d2['h'] and d2['pad'] and d2['taken'] == ['driver-%d' % p1['sel']] and d2['sel'] != p1['sel'])
        await click('#p2PadBtn'); w = await js("({wait:SPLIT.wait,say:$('p2PadSay').textContent})")
        await pg.screenshot(path=SH % 'padwait')
        await press(1, 0); await pg.wait_for_timeout(300)
        c = await js("({wait:SPLIT.wait,pid:SPLIT.pid,id:SPLIT.pidId,say:$('p2PadSay').textContent,store:localStorage.getItem('crust-p2pad'),step:menuStep,garage:garageOpen})")
        await pg.screenshot(path=SH % 'padset')
        say('choose controller: a press on pad 2 makes it player 2s, and does not click', {'waiting': w, 'after': c}, w['wait'] and not c['wait'] and c['pid'] == 1 and 'Test pad B' in c['say'] and c['step'] == 'driver' and not c['garage'])
        pick = (p1['sel'] + 3) % 8
        await click('#driver-%d' % pick)
        await click('#garageBtn'); await pg.wait_for_timeout(800)
        g2 = await js("({step:document.querySelector('#garage .g-step').textContent,back:$('gBack').textContent,done:$('gDone').textContent,sel:selected})")
        await pg.evaluate("__ev(`playerBuild=Object.assign({},playerBuild,{p:(playerBuild.p+1)%PAINTS.length});saveBuild();refreshGarage(false);`)"); await pg.wait_for_timeout(600)
        b2 = await js("JSON.stringify(playerBuild)")
        await pg.screenshot(path=SH % 'kart2')
        say('player 2 garage', g2, g2['step'] == 'Player 2' and 'Choose track' in g2['done'] and g2['sel'] == pick)
        await click('#gDone'); await pg.wait_for_timeout(600)
        t = await js("({step:menuStep,sw:SPLIT.sw,sel:selected,build:JSON.stringify(playerBuild),p2sel:SPLIT.sel,p2b:JSON.stringify(SPLIT.build),d2:localStorage.getItem('crust-driver2'),b2:localStorage.getItem('crust-build2'),b1:localStorage.getItem('crust-build'),back:document.querySelector('[data-step=\"track\"] .st-back').dataset.back})")
        await pg.screenshot(path=SH % 'track')
        say('track: player 1 keeps their driver and kart; player 2s saved', t, t['step'] == 'track' and not t['sw'] and t['sel'] == p1['sel'] and t['build'] == p1['build'] and t['p2sel'] == pick and t['p2b'] == b2 and t['d2'] == str(pick) and t['b2'] == b2 and t['back'] == 'kart2')
        await click('[data-step="track"] .st-back'); await pg.wait_for_timeout(800)
        bk = await js("({garage:garageOpen,sw:SPLIT.sw,sel:selected})")
        say('back from the track opens player 2s garage', bk, bk['garage'] and bk['sw'] and bk['sel'] == pick)
        await click('#gBack'); await click('[data-step="driver"] .st-back'); await pg.wait_for_timeout(800)
        bk2 = await js("({garage:garageOpen,sw:SPLIT.sw,sel:selected,build:JSON.stringify(playerBuild)})")
        say('and back again to player 1s garage, with player 1s kart', bk2, bk2['garage'] and not bk2['sw'] and bk2['sel'] == p1['sel'] and bk2['build'] == p1['build'])
        await click('#gBack'); await click('[data-step="driver"] .st-back')
        await click('#plySeg button[data-n="1"]'); await click('#toDriver'); await click('#garageBtn'); await pg.wait_for_timeout(600)
        one = await js("({done:$('gDone').textContent,step:document.querySelector('#garage .g-step').textContent})")
        say('1 player: the usual three steps', one, 'Choose track' in one['done'] and one['step'] == 'Step 2 of 3')
        await click('#gDone')
        print('errors', errs[:5]); print('SPLIT TEST', WHAT, 'FAILED' if bad or errs else 'passed'); await b.close()
async def race(pg, js, say, press):
    track = sys.argv[2] if len(sys.argv) > 2 else 'margherita'
    md = 'bb' if WHAT == 'bb' else 'single'
    mi = "MAPS.findIndex(m=>m.battle)" if md == 'bb' else "MAPS.findIndex(m=>m.id==='%s')" % track
    code = "SPLIT.n=2;SPLIT.pid=1;SPLIT.pidId=navigator.getGamepads()[1].id;mode='%s';refreshMenu();cpuBuilds=RACERS.map(randomBuild);gp=null;goRace(%s);" % (md, mi)
    await pg.evaluate("(c)=>__ev(c)", code)
    await pg.wait_for_function("document.getElementById('raceLd').hidden", timeout=900000)
    for i in range(300):
        if await pg.evaluate("__ev(`state`)") in ('countdown', 'race'): break
        await pg.wait_for_timeout(200)
    st = await js("({on:SPLIT.on,split:document.body.classList.contains('split'),p2:player2?player2.r.name:null,p1:player.r.name,n:karts.length,hud2:!!H2.el})")
    await pg.wait_for_timeout(700)
    await pg.screenshot(path=SH % (WHAT + '_count'))
    say('race: split on, player 2 seated', st, st['on'] and st['split'] and st['p2'] and st['p2'] != st['p1'] and st['n'] == 8)
    for i in range(100):
        if await pg.evaluate("__ev(`state`)") == 'race': break
        await pg.wait_for_timeout(200)
    # both throttles down (RT), player 2 steers a little
    await pg.evaluate("window.__btn(0,7,true);window.__btn(1,7,true)")
    p0 = await js("({a:player.prog,b:player2.prog})")
    await pg.wait_for_timeout(3500)
    await pg.screenshot(path=SH % (WHAT + '_drive'))
    await pg.evaluate("__ev(`player2.item='pepperoni';`)"); await press(1, 0); await pg.wait_for_timeout(400)
    it = await js("({item:player2.item,proj:projectiles.length,p1item:player.item})")
    await pg.evaluate("window.__axes(1,[.8,0,0,0])"); await pg.wait_for_timeout(1500); await pg.evaluate("window.__axes(1,[0,0,0,0])")
    p1 = await js("({a:player.prog,b:player2.prog,auto2:player2.auto,fps:Math.round(1/Math.max(1e-3,render.fdt||1)),lowq:LOWQF()})")
    await pg.screenshot(path=SH % (WHAT + '_item'))
    mv = WHAT == 'bb' or (p1['a'] > p0['a'] + 20 and p1['b'] > p0['b'] + 20)
    say('race: both karts drive on their own controllers', {'start': p0, 'after': p1}, mv and not p1['auto2'])
    say('race: player 2 fires their item with A on their controller', it, it['item'] is None)
    en = await js("({ac:ac?ac.state:null,e2:!!E2.g,gain:E2.g?+E2.g.gain.value.toFixed(5):0,hz:E2.o1?Math.round(E2.o1.frequency.value):0,hz1:eng?Math.round(eng.frequency.value):0,body2:BODIES[player2.spec.b].id})")
    say('race: player 2 has their own engine voice, following their kart', en, en['e2'] and en['gain'] > 0 and en['hz'] > 30)
    await press(1, 9); await pg.wait_for_timeout(500)
    pz = await pg.evaluate("__ev(`state`)"); await pg.screenshot(path=SH % (WHAT + '_pause'))
    await press(1, 9); await pg.wait_for_timeout(400)
    say('race: Start on player 2s controller pauses and resumes', {'paused': pz, 'now': await pg.evaluate("__ev(`state`)")}, pz == 'paused')
    if '--full' in sys.argv:
        await pg.evaluate("__ev(`player.auto=true;player2.auto=true;`)")
        for i in range(600):
            if await pg.evaluate("!document.getElementById('results').hidden"): break
            await pg.wait_for_timeout(500)
        await pg.wait_for_timeout(800)
        r = await js("({res:!document.getElementById('results').hidden,rows:[...document.querySelectorAll('#results .me')].map(e=>e.textContent.slice(0,60)),t:(document.querySelector('#results .res-title')||{}).textContent})")
        await pg.screenshot(path=SH % (WHAT + '_results'))
        say('results: both players marked', r, r['res'])
    await pg.evaluate("window.__btn(0,7,false);window.__btn(1,7,false)")


asyncio.run(main())
