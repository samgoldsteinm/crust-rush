"""PC: the underglow less of a box, the wheels blocking it (web v247, patch 114): shaders/underglow.gdshaderinc, the web's ugLs.
    python tools/mini/pc103.py      (once, after pc102)"""
p = 'D:/crust-rush/godot/shaders/underglow.gdshaderinc'
s = open(p, encoding='utf-8', newline='').read()


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:80])
    s = s.replace(a, b)


rep("	float kT = ug_p0.w;\n", "	float kT = ug_p0.w * 1.8;   // (pc103: the tyres block harder)\n")
for w in ('vec4(wf, wz, rf * 0.85, tw * 0.5)', 'vec4(wf, -wz, rf * 0.85, tw * 0.5)', 'vec4(wr, wz, rr * 0.85, tw * 0.5)', 'vec4(wr, -wz, rr * 0.85, tw * 0.5)'):
    rep(w, w.replace(' * 0.85', '').replace('tw * 0.5', 'tw * 0.62'))
rep("	float rc = 0.3 * b;", "	float rc = 0.85 * b;   // (pc103: nearly a pill, was 0.3 b)")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('pc103 applied')
