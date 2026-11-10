import asyncio,json,sys,os,base64
from playwright.async_api import async_playwright
MI=int(os.environ.get('MI','1'));Q=os.environ.get('Q','balanced');OUT=os.environ.get('OUT','/home/claude/crust-rush-godot/assets')
exec(open('common.py').read())
EXP=open('glbexport.js').read()
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist'])
    pg=await b.new_page(viewport={'width':900,'height':420},device_scale_factor=1);errs=[];pg.on('pageerror',lambda e:errs.append(str(e)[:300]))
    async def route(r):
      u=r.request.url
      if 'three' in u: await r.fulfill(body=three,content_type='application/javascript')
      elif u.startswith('http://t/'): await r.fulfill(body='<!doctype html><html><head><meta charset=utf-8></head><body style="margin:0">'+html2+'</body></html>',content_type='text/html')
      else: await r.abort()
    await pg.route('**/*',route)
    await pg.goto('http://t/',wait_until='domcontentloaded',timeout=180000);await pg.wait_for_function("document.getElementById('menu')&&!document.getElementById('menu').hidden",timeout=400000)
    await pg.evaluate('src=>__ev(src)',EXP)
    liv=await pg.evaluate("""__ev(`JSON.stringify({racers:RACERS.map(r=>r.name),bodies:BODIES.map((b,i)=>i+':'+b.id).join(' '),liv:liveriesFor('hyper').map(l=>[l.id,l.name,l.A,l.B,l.C||'',l.cat||'',l.only||''])})`)""")
    L=json.loads(liv);print('racers',L['racers']);print('bodies',L['bodies'][:400]);print('hyper liveries',len(L['liv']));[print('  ',x) for x in L['liv'][:60]]
    await pg.evaluate("__ev(`qKey='%s';store.set('crust-q',qKey);applyQuality();applyLad(0,false);clsKey='medium';mode='single';goRace(%d)`)"%(Q,MI));await pg.wait_for_function("document.getElementById('raceLd').hidden",timeout=900000)
    await pg.evaluate("__ev(`endIntro();state='paused';1`)")
    sv=json.loads(await pg.evaluate("__ev(`JSON.stringify(__sceneSurvey())`)"))
    print('world top-level:',len(sv['top']));[print('  ',t) for t in sorted(sv['top'],key=lambda t:-t[4])[:25]]
    print('scene types',sv['types'],'mats',sv['mats']);print('scene top (non-world)',sv['sceneTop'])
    if os.environ.get('SURVEY_ONLY'):await b.close();return
    if os.environ.get('WEBSHOTS'):
      await pg.set_viewport_size({'width':1280,'height':720})
      for j,nm in [(-1,'start'),(520,'mid'),(330,'glide')]:
        await pg.evaluate("""j=>__ev(`(()=>{fit();const k=player;if(${j}>=0){const p=track[${j}];k.x=k.px=p.x;k.y=k.py=p.y;k.a=k.ma=k.pa=k.pma=p.ang;k.idx=${j};k.wy=k.pwy=groundAt(p.x,p.y);k.speed=150;state='race';camSnap=true;}else{state='countdown';cd=2.2;}
          for(let i=0;i<4;i++){render(performance.now()/1000,1/60);renderer.shadowMap.needsUpdate=true;postRender();}return 1;})()`)""",j)
        await pg.screenshot(path='/tmp/claude-0/t/web_%s.png'%nm,timeout=240000);print('webshot',nm,flush=True)
    if os.environ.get('KART_ONLY'):
      spec=json.loads(await pg.evaluate("__ev(`JSON.stringify({ri:RACERS.findIndex(r=>r.name==='Basil'),b:BODIES.findIndex(b=>b.id==='hyper'),w:0,g:0,p:0,t:'hy_aurora',hq:0,u:0})`)"))
      k=json.loads(await pg.evaluate("s=>__ev('JSON.stringify(__exportKart('+s+'))')",json.dumps(spec)))
      open(OUT+'/kart/hypercar.glb','wb').write(base64.b64decode(k['b64']));json.dump(dict(k['meta'],spec=spec),open(OUT+'/kart/hypercar.json','w'),indent=1)
      print('kart glb',k['stats'],'livery',k['livery'],flush=True);print('errs',errs[:4]);await b.close();return
    d=json.loads(await pg.evaluate("__ev(`JSON.stringify(__exportData(10))`)"))
    os.makedirs(OUT+'/track',exist_ok=True);json.dump(d,open(OUT+'/track/%s.json'%d['map'],'w'),separators=(',',':'))
    if os.environ.get('DATA_ONLY'):
      print('data',d['map'],'glide',{k:v for k,v in (d['glide'] or {}).items() if k!='gy'},'loops',d['loopsD'],'shorts',d['shortsD'],'pondLim',d['pondLim'],'statMods',d['statMods'],'gridProg',d['gridProg'],'pit',bool(d['pit']));await b.close();return
    print('data',d['map'],'N',d['N'],'ramps',len(d['ramps']),'pads',len(d['pads']),'obst',len(d['obstacles']),'grid',len(d['grid']),'height n',d['height']['n'],'flags',{k:d[k] for k in ['hasGlide','loops','shorts','multi','relief','pits']},'light',d['light'],flush=True)
    nm=d['map'];t=json.loads(await pg.evaluate("n=>__ev('JSON.stringify(__exportTrack(\"'+n+'\"))')",nm))
    for f in os.listdir(OUT+'/track'):
      if f.endswith('.glb'):os.remove(OUT+'/track/'+f)
    open(OUT+'/track/%s.gltf'%nm,'w').write(t['json']);open(OUT+'/track/%s.bin'%nm,'wb').write(base64.b64decode(t['bin']))
    td=OUT+'/track/%s_tex'%nm;os.makedirs(td,exist_ok=True)
    for f in t['files']:open(td+'/'+f['name'],'wb').write(base64.b64decode(f['b64']))
    print('track gltf',t['stats'],flush=True)
    spec=json.loads(await pg.evaluate("__ev(`JSON.stringify({ri:RACERS.findIndex(r=>r.name==='Basil'),b:BODIES.findIndex(b=>b.id==='hyper'),w:0,g:0,p:0,t:'hy_aurora',hq:0,u:0})`)"))
    k=json.loads(await pg.evaluate("s=>__ev('JSON.stringify(__exportKart('+s+'))')",json.dumps(spec)))
    os.makedirs(OUT+'/kart',exist_ok=True);open(OUT+'/kart/hypercar.glb','wb').write(base64.b64decode(k['b64']));json.dump(dict(k['meta'],spec=spec),open(OUT+'/kart/hypercar.json','w'),indent=1)
    print('kart glb',k['stats'],'meta',k['meta'],flush=True)
    print('errs',errs[:4]);await b.close()
asyncio.run(main())
