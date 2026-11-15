"""Patch 34 (web v199): the engine's side of the no-stop tunnel (tools/mini/sandbox.js, sbTravel and sbWarpFrame).
The owner, 2026-11-14: "i dont want the streaks to freeze for a second it should be the player continusously driving and eventually the new
map will load and the driver will drive out but the game will never freeze or stop to load it will be one fluid drive through the tunnel
right out to the other side".
- postRender and postLite draw `postRender.s || scene` through `postRender.c || camera`: the tunnel's own small scene goes through the same
  glow, grade and the rest, so it looks like the real tunnel it hands over to.
- render()'s last line (the post pass, or a plain draw) becomes drawNow(), which the tunnel calls too.
- the frame loop: while SB.warp is set it calls sbWarpFrame (which draws the tunnel and builds a slice of the next place), and the HUD waits
  (it reads the place being built). The engine sound keeps running in the tunnel.
Nothing here moves a kart. Run once: py.cmd tools/mini/patch34.py"""
import re, subprocess
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'function drawNow(' not in s, 'already patched'


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:90])
    s = s.replace(a, b)


def span(fn):
    o = subprocess.run(['D:/crust-rush/tools/node/node.exe', 'D:/crust-rush/source/tools/jsparse/span.js', p, fn], capture_output=True, text=True, check=True).stdout.split()
    a, b = map(int, o)
    assert s[a:a + len('function ' + fn)] == 'function ' + fn
    return a, b


open(p, 'w', encoding='utf-8', newline='').write(s)  # (span.js reads the file)
for fn in ('postRender', 'postLite'):
    a, b = span(fn)
    f = s[a:b]
    g = re.sub(r'(?<![.\w$])scene(?=[.,)])', '(postRender.s||scene)', f)
    g = re.sub(r'(?<![.\w$])camera(?=[.,)])', '(postRender.c||camera)', g)
    assert g != f
    s = s[:a] + g + s[b:]
    open(p, 'w', encoding='utf-8', newline='').write(s)

LINE = "if(!LOWQF()&&CFG.post!==false&&!LADV.np&&!BENCH.noPost){try{postRender();}catch(e){console.warn('post',e);CFG.post=false;renderer.setRenderTarget(null);renderer.render(scene,camera);}}else if(APPLEWK&&!POST.liteFail){try{postLite();}catch(e){console.warn('post lite',e);POST.liteFail=true;renderer.setRenderTarget(null);renderer.render(scene,camera);}}else{renderer.render(scene,camera);render.calls=renderer.info.render.calls;render.tris=renderer.info.render.triangles;}"
rep('  ' + LINE, '  drawNow();')
body = LINE.replace('render(scene,camera)', 'render(postRender.s||scene,postRender.c||camera)')
rep('function postRender(){', '/* the frame\'s last step: the post pass, or a plain draw (patch 34: also the Sandbox tunnel\'s, with postRender.s and .c set) */\nfunction drawNow(){' + body + '}\nfunction postRender(){')
# the frame loop
rep("let dt=(now-last)/1000;last=now;if(dt>.1)dt=.1;if(dt<0)dt=0;const time=now/1000;const cw0=performance.now();",
    "let dt=(now-last)/1000;last=now;if(dt>.1)dt=.1;if(dt<0)dt=0;const time=now/1000;const cw0=performance.now();\n  if(SB.warp){/* Sandbox: driving the tunnel while the next place is built (sandbox.js) */try{sbWarpFrame(dt,time);}catch(e){console.warn('sandbox warp',e);SB.warp=null;state='race';}}")
rep("  hud(dt,time);\n  try{musTick();}", "  if(!SB.warp)hud(dt,time);\n  try{musTick();}")
rep("const on=!muted&&(state==='race'||state==='countdown')&&!!player;", "const on=!muted&&(state==='race'||state==='countdown'||!!SB.warp)&&!!player;")
# the clock (sandbox.js sbClockMats) darkens pictures of the outside with the sky; the kitchen's window panes are plain unlit blue with no
# picture, so it could not tell them from anything else: they get a name it knows
rep("sky=new THREE.MeshBasicMaterial({color:'#bfe3ff',toneMapped:false,fog:false})", "sky=new THREE.MeshBasicMaterial({name:'sky_window',color:'#bfe3ff',toneMapped:false,fog:false})")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patched')
