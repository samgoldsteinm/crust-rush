"""Patch 109 (web v244): Monster wheels on a car whose own wheels are already big are capped.
The owner: "make sure the monster truck wheels fit all the new vehicles we added correctly since they are much bigger, i noticed they fit
the night tank a little weird". Monster wheels are 1.5x a car's own wheels; the Night Tank's own rear wheels are already r 1.49, so its
Monster rears came out r 2.23 (bigger than the Monster truck's own 1.66), poking up through its rear body, with a 1.6 lift.
(scratch/paint/monfit.js: Biome, Surge, Vortex, Scarlet sit right on Monster wheels; monfit2.js: the Night Tank stock vs Monster.)
- wr: the wheel type's size factor; for Monster on a car (not the Monster truck itself) at most what brings its biggest wheel to 1.75,
  never under 1.16 (so the lift-kit rule, > 1.15, still raises the body). Used for the wheels, the lift and the far model's wheels.
  Only the Night Tank changes (factor 1.18: rears 1.75, fronts 1.31); every other car has wheels under 1.17.
- PC: from the export (its wheel placement is the web's).
Run once, after patch 108: tools/py.cmd tools/mini/patch109.py"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'patch 109' not in s, 'already patched'


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:90])
    s = s.replace(a, b)


rep("const L=cfg.hover||cfg.rw[2]*(wt.r-1)*(cfg.car&&wt.r>1.15?2.2:1),",
    "const wr=wt.id==='monster'&&cfg.car&&cfg.car!=='monster'?Math.min(wt.r,Math.max(1.16,1.75/Math.max(cfg.rw[2],cfg.fw[2]))):wt.r;/* (patch 109) */"
    "const L=cfg.hover||cfg.rw[2]*(wr-1)*(cfg.car&&wr>1.15?2.2:1),")
rep("for(const s of [-1,1]){const R=w[2]*wt.r,yaw=new THREE.Group();", "for(const s of [-1,1]){const R=w[2]*wr,yaw=new THREE.Group();")
rep("const R=w[2]*wt.r;hrx(P3(KG.loWheel", "const R=w[2]*wr;hrx(P3(KG.loWheel")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patch 109 applied')
