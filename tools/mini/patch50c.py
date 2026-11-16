"""Patch 50c (web v211): the tunnel hands the graphics driver a few new shaders a frame, not dozens.
After patches 50/50b and the wider __crDefer (build/build_gh.py) the game's own work in a trip is small (the worst step 59 ms; compile
61 ms in all, was 1975), but a first trip to the garage still had frames of 200-300 ms (scratch/ftrip.js): compiling had become so cheap
that one frame's 9 ms of building sent dozens of new shaders to the driver at once, and the frames after waited for it. sbWarmG now
yields 'warmF' once 3 new programs have been made since the last one, and the tunnel's frame loop stops building for that frame on it.
Run once: py.cmd tools/mini/patch50c.py"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'patch 50c' not in s, 'already patched'


def rep(a, b):
    global s
    assert s.count(a) == 1, (s.count(a), a[:90])
    s = s.replace(a, b)


rep("finally{renderer.setRenderTarget(null);renderer.debug.checkShaderErrors=ck;renderer.__crDefer=false;}yield \"warm2\";}",
    "finally{renderer.setRenderTarget(null);renderer.debug.checkShaderErrors=ck;renderer.__crDefer=false;}yield \"warm2\";"
    "{const np=renderer.info.programs.length;if(np-(sbWarmG.np||0)>=3){sbWarmG.np=np;yield 'warmF';}}/* (patch 50c: a few new shaders a frame) */}")
rep("w.pv=r.value;if(r.done)break;}if(r.done){w.job=null;break;}if(performance.now()-t0>B)break;}}",
    "w.pv=r.value;if(r.done||r.value==='warmF')break;}if(r.done){w.job=null;break;}if(r.value==='warmF'||performance.now()-t0>B)break;}}")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patch 50c applied')
