"""Patch 106 (web v243): the Surge's other wheel types sit where its own tyres sit.
The owner (the Surge in the garage, stock wheels vs Pepperoni): "The wheels on the surge don't sit correctly ... the pepperoni wheels
[stick far out] and it's happening for all the other kinds of wheels too. The hover wheels actually sit too far in."
- Measured (scratch/paint/wfit.js, front-left outer face): stock 2.67; slick 2.81, pepperoni 2.87, redline 2.77, forged 2.81,
  turbo 2.80; hover 2.53. The Surge's own tyres are narrow (.9 wide), so every wider wheel touched the body and clearZ pushed it out;
  the hover wheel is narrower than its nominal width, so it sat in.
- WHEEL_FLUSH (surge): no push-out (unless the wheel is much bigger than the car's own, monster: R > 1.2x), and after the wheel is
  built, its actual outer face is put on the car's own tyre's outer face (measured from the wheel's box, so the hover wheel too).
- PC: from the export.
Run once, after patch 105: tools/py.cmd tools/mini/patch106.py"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'patch 106' not in s, 'already patched'


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:90])
    s = s.replace(a, b)


rep("const WHEEL_ADDCAL={coupe:1,megawatt:1};",
    "const WHEEL_ADDCAL={coupe:1,megawatt:1};const WHEEL_FLUSH={surge:1};/* (patch 106: other wheel types' outer face on the car's own tyre's) */")
rep("if(R>w[2]*1.02||Wn>W0*1.02)z=Math.min(clearZ(",
    "if((R>w[2]*1.02||Wn>W0*1.02)&&!(WHEEL_FLUSH[cfg.car]&&q&&R<w[2]*1.2))z=Math.min(clearZ(")
rep("wh.scale.set(R/1.32,R/1.32,tyreR(R)/1.32*wz);}spin.add(wh);",
    "wh.scale.set(R/1.32,R/1.32,tyreR(R)/1.32*wz);}spin.add(wh);"
    "if(WHEEL_FLUSH[cfg.car]&&wt.id!=='standard'&&R<w[2]*1.2){/* (patch 106) */const q=CAR_PACKS[cfg.car].h.wheels.find(q=>Math.sign(q.c[2])===s&&q.f===f);"
    "if(q){const gw=carGeos(cfg.car)['w'+CAR_PACKS[cfg.car].h.wheels.indexOf(q)];if(!gw.boundingBox)gw.computeBoundingBox();const zO=Math.abs(q.c[2])+(s>0?gw.boundingBox.max.z:-gw.boundingBox.min.z);/* (the car's own tyre as drawn) */"
    "yaw.updateMatrixWorld(true);const bb=new THREE.Box3().setFromObject(wh),yz=yaw.getWorldPosition(new THREE.Vector3()).z,"
    "out=s>0?bb.max.z-yz:yz-bb.min.z;if(isFinite(out))yaw.position.z=s*(zO-out);}}")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patch 106 applied')
