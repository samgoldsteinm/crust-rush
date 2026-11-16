"""Patch 50b (web v211): the tunnel's last warm-up step no longer draws the whole place three times.
After patch 50 the first trip to the garage still had one 2.4 to 2.9 s step (scratch/warm5.js: no single draw was slow, so it was the
step's last call): sbWarmG ended with warmScene(), which draws the whole place, everything shown and nothing culled, into the post pass's
target, then to the screen, then into a 64 px target. In Sandbox the screen and the 64 px target are never drawn into: each needs its own
shader for every material, all built for nothing. In the tunnel it is now one draw into the target the game really draws to (wtg: the
post pass's, or the screen with no post pass), which also builds the shadows' shaders. With no post pass (Lite) the one-object draws (warm5)
are skipped too: they drew into a small target the game never uses, so they built shaders for nothing, and the screen cannot be drawn into
in the middle of the tunnel.
Run once: py.cmd tools/mini/patch50b.py"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'patch 50b' not in s, 'already patched'


def rep(a, b):
    global s
    assert s.count(a) == 1, (s.count(a), a[:90])
    s = s.replace(a, b)


rep("try{warmScene();}catch(e){}\n  if(SBX)for(const p of renderer.info.programs)",
    "try{sunShadeAll();renderer.shadowMap.needsUpdate=true;renderer.setRenderTarget(wtg);renderer.render(scene,camera);}catch(e){}finally{renderer.setRenderTarget(null);}/* (patch 50b: one draw into the real target, not warmScene's three) */\n  if(SBX)for(const p of renderer.info.programs)")
rep("for(const x of objs){if(!(x.isMesh||x.isPoints||x.isLine||x.isSprite))continue;const fc=x.frustumCulled",
    "for(const x of (wtg?objs:[])){if(!(x.isMesh||x.isPoints||x.isLine||x.isSprite))continue;const fc=x.frustumCulled")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patch 50b applied')
