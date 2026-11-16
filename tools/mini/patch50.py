"""Patch 50 (web v211): Sandbox's tunnels without the freeze.
The owner: "lets fix the tunnel lag it was really bad the whole game froze for like 5 seconds, it should be smooth".
Measured (scratch/lights.js, tunnel48c.js with sbprobe.py): margherita -> garage spent 7.3 s in ONE step of sbWarmG's shader warm-up and
170-420 ms in each of ~20 more. Two causes:
1. The places do not have the same lights. A shader is built for a count of each kind of light: the garage has a room lamp (a PointLight)
   that Margherita Ring has not, the lamp places (SB_LAMPS) three; so every material's shader, the karts' heavy livery shader too, was
   built again on every trip that changed the count. Now every Sandbox place has the same number of point lights (lite 3, else 4): the
   missing ones are dark placeholders (sbLightPad, from sbNightArm and again at the start of sbWarmG). Shaders made once are used again.
2. The warm-up built the wrong shaders. renderer.compile ran with no render target, so the shaders were made for drawing straight to the
   screen (sRGB output); the game draws into the post pass's target (linear output), a different shader. All that work was thrown away
   and the real ones were built in the draw step after (warm5: ~200 ms an object). The compile now runs into the same target.
And the warm-up takes 2 objects a step, not 8, so a step that has to build new shaders stays short.
Rule: anything that adds or removes a light in Sandbox must keep the count of each kind the same in every place (or pad it here), and any
new warm-up must compile into the target the game really draws to.
Run once: py.cmd tools/mini/patch50.py"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'patch 50' not in s, 'already patched'


def rep(a, b):
    global s
    assert s.count(a) == 1, (s.count(a), a[:90])
    s = s.replace(a, b)


rep("function* sbWarmG(){try{sunShadeAll();}catch(e){}yield \"warm1\";",
    "/* (patch 50) the same number of point lights in every Sandbox place: dark placeholders make up the rest (a different count rebuilds every shader) */\n"
    "function sbLightPad(){if(!SB.grp)return;const K=(!QUAL[qKey]||QUAL[qKey].lite||qKey==='fast')?3:4;let n=0;const ph=[];scene.traverse(o=>{if(!o.isPointLight)return;if(o.userData.sbPad)ph.push(o);else n++;});\n"
    "  for(const o of ph)if(o.parent)o.parent.remove(o);for(let i=n;i<K;i++){const l=new THREE.PointLight('#000000',0,1,2);l.userData.sbPad=1;l.position.set(0,-50000,0);SB.grp.add(l);}}\n"
    "function* sbWarmG(){try{sunShadeAll();}catch(e){}try{sbLightPad();}catch(e){}yield \"warm1\";\n"
    "  let wtg=null;try{if(!LOWQF()&&CFG.post!==false){postInit();const sz=renderer.getDrawingBufferSize(v2);postSize(sz.x,sz.y);wtg=POST.rt;}}catch(e){}/* (patch 50) compile for the target the game draws into */")
rep("for(let i=0;i<objs.length;i+=8){const ch=objs.slice(i,i+8);",
    "for(let i=0;i<objs.length;i+=2){const ch=objs.slice(i,i+2);")
rep("try{renderer.compile(F,camera);}catch(e){console.warn('sandbox shaders',e);}finally{renderer.debug.checkShaderErrors=ck;renderer.__crDefer=false;}yield \"warm2\";}",
    "try{renderer.setRenderTarget(wtg);renderer.compile(F,camera);}catch(e){console.warn('sandbox shaders',e);}finally{renderer.setRenderTarget(null);renderer.debug.checkShaderErrors=ck;renderer.__crDefer=false;}yield \"warm2\";}")
rep("Nt.pool.push(l);}}}}\n/* each frame: the night's lights",
    "Nt.pool.push(l);}}}try{sbLightPad();}catch(e){}/* (patch 50) */}\n/* each frame: the night's lights")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patch 50 applied')
