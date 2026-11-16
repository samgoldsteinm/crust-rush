"""Patch 50d (web v211): the tunnel's frame loop keeps to its time budget.
With the shaders fixed (patches 50-50c), a first trip to the garage still had frames of 100-375 ms (scratch/fsplit.js: all inside
sbWarpFrame's building, in the steps warm3 and warm4). The loop ran up to 16 steps before looking at the clock: warm3 asked every one of
~300 programs whether the driver had finished it (about 24 ms a time), so 16 of those were 375 ms; warm4 uploads one texture a step, a big
one 10-30 ms. Now the clock is read after every step (B: 9 ms, 6 on a phone), and warm3 asks only the programs not yet finished, once
each a frame (a finished one is marked __crOk and never asked again).
Run once: py.cmd tools/mini/patch50d.py"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'patch 50d' not in s, 'already patched'


def rep(a, b):
    global s
    assert s.count(a) == 1, (s.count(a), a[:90])
    s = s.replace(a, b)


rep("const t0=performance.now();for(;;){let all=true;for(const p of renderer.info.programs)if(!gl.getProgramParameter(p.program,ext.COMPLETION_STATUS_KHR)){all=false;break;}if(all||performance.now()-t0>8000)break;yield \"warm3\";}",
    "const t0=performance.now();for(;;){let all=true;for(const p of renderer.info.programs){if(p.__crOk)continue;if(gl.getProgramParameter(p.program,ext.COMPLETION_STATUS_KHR))p.__crOk=1;else{all=false;break;}}if(all||performance.now()-t0>8000)break;yield 'warmF';}/* (patch 50d: only the unfinished ones, once a frame) */")
rep("w.pv=r.value;if(r.done||r.value==='warmF')break;}",
    "w.pv=r.value;if(r.done||r.value==='warmF'||performance.now()-t0>B)break;}/* (patch 50d: the clock after every step) */")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patch 50d applied')
