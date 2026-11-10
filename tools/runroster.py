import asyncio,json,sys,os,base64
from playwright.async_api import async_playwright
MI=int(os.environ.get('MI','1'));Q=os.environ.get('Q','balanced');OUT=os.environ.get('OUT','/home/claude/crust-rush-godot/assets')
HQ=int(os.environ.get('HQ','1'))
exec(open('common.py').read())
EXP=open('glbexport.js').read()
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist'])
    pg=await b.new_page(viewport={'width':900,'height':420},device_scale_factor=1);errs=[];pg.on('pageerror',lambda e:errs.append(str(e)[:300]))
    pg.on('console',lambda m:print('console',m.text[:200]) if m.type in ('warning','error') else None)
    async def route(r):
      u=r.request.url
      if 'three' in u: await r.fulfill(body=three,content_type='application/javascript')
      elif u.startswith('http://t/'): await r.fulfill(body='<!doctype html><html><head><meta charset=utf-8></head><body style="margin:0">'+html2+'</body></html>',content_type='text/html')
      else: await r.abort()
    await pg.route('**/*',route)
    await pg.goto('http://t/',wait_until='domcontentloaded',timeout=180000);await pg.wait_for_function("document.getElementById('menu')&&!document.getElementById('menu').hidden",timeout=400000)
    await pg.evaluate('src=>__ev(src)',EXP)
    print('booted',flush=True)
    await pg.evaluate("__ev(`qKey='%s';store.set('crust-q',qKey);applyQuality();applyLad(0,false);clsKey='medium';mode='single';goRace(%d)`)"%(Q,MI));await pg.wait_for_function("document.getElementById('raceLd').hidden",timeout=900000)
    await pg.evaluate("__ev(`endIntro();state='paused';1`)")
    print('race loaded',flush=True)
    os.makedirs(OUT+'/kart',exist_ok=True);os.makedirs(OUT+'/items',exist_ok=True)
    race=json.loads(await pg.evaluate("__ev(`JSON.stringify(__exportRace())`)"))
    tj=OUT+'/track/bay.json';d=json.load(open(tj));d['race']=race;json.dump(d,open(tj,'w'),separators=(',',':'))
    print('race data: boxes',len(race['boxes']),'loops',race['loops'],'loopK',race['loopK'],'haz',race['haz'],'L',race['L'],flush=True)
    hz=json.loads(await pg.evaluate("__ev(`JSON.stringify(__exportHaz())`)"))
    d=json.load(open(tj));d['haz']=hz['data'];json.dump(d,open(tj,'w'),separators=(',',':'))
    open(OUT+'/track/bay_haz.glb','wb').write(base64.b64decode(hz['b64']))
    print('hazards',{k:(len(v) if isinstance(v,list) else bool(v)) for k,v in hz['data'].items()},hz['stats'].get('bytes'),flush=True)
    ic=json.loads(await pg.evaluate("__ev(`JSON.stringify(__exportIcons())`)"))
    for k,v in ic.items():open(OUT+'/items/icon_%s.png'%k,'wb').write(base64.b64decode(v))
    print('icons',list(ic.keys()),flush=True)
    pts=json.loads(await pg.evaluate("__ev(`JSON.stringify(PORTRAITS.map(u=>u||''))`)"))
    for i,u in enumerate(pts):
      if u.startswith('data:image/png;base64,'):open(OUT+'/kart/portrait%d.png'%i,'wb').write(base64.b64decode(u.split(',',1)[1]))
    print('portraits',sum(1 for u in pts if u),flush=True)
    it=json.loads(await pg.evaluate("__ev(`JSON.stringify(__exportItems())`)"))
    open(OUT+'/items/items.glb','wb').write(base64.b64decode(it['b64']));print('items',it['names'],it['stats'],flush=True)
    roster=json.loads(await pg.evaluate("__ev(`JSON.stringify(__exportRoster())`)"))
    pspec=json.loads(await pg.evaluate("__ev(`JSON.stringify({ri:RACERS.findIndex(r=>r.name==='Basil'),b:BODIES.findIndex(b=>b.id==='hyper'),w:0,g:0,p:0,t:'hy_aurora'})`)"))
    pst=json.loads(await pg.evaluate("s=>__ev('JSON.stringify(__statsFor('+s+'))')",json.dumps(pspec)))
    out={'player':dict(pspec,file='player.glb',sm=pst['sm'],glider=pst['glider']),'racers':[]}
    specs=[('player.glb',dict(pspec,hq=HQ,u=0))]
    for r in roster:
      r['file']='racer%d.glb'%r['ri'];out['racers'].append(r)
      bb=r['build'];specs.append((r['file'],{'ri':r['ri'],'b':bb['b'],'w':bb['w'],'g':bb['g'],'p':bb['p'],'t':bb.get('t',''),'hq':HQ,'u':0}))
    for fn,spec in specs:
      k=json.loads(await pg.evaluate("s=>__ev('JSON.stringify(__exportKart('+s+'))')",json.dumps(spec)))
      open(OUT+'/kart/'+fn,'wb').write(base64.b64decode(k['b64']))
      meta=dict(k['meta'],spec=spec)
      if fn=='player.glb':out['player']['meta']=meta
      else:
        for r in out['racers']:
          if r['file']==fn:r['meta']=meta
      print('kart',fn,spec,'tris',k['stats'].get('tris'),'bytes',k['stats'].get('bytes'),flush=True)
    json.dump(out,open(OUT+'/kart/roster.json','w'),indent=1)
    print('errs',errs[:6]);await b.close()
asyncio.run(main())
