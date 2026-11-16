"""Patch 48 (web v210): in Sandbox's tunnels the kart drives straight and the camera stays square behind it.
The owner (a picture in a tunnel, the camera turned so half the screen was the black outside of the tube): "when going through the tunnels
lets lock the player into driving straight and the camera from not moving behind them so they dont see outside the tunnel".
sbWarpKart copied the game camera as it was at the gate: coming in on a turn or a drift, it looked off to one side all the way through;
and steering slid the kart up to 14 to each side with the camera following. Now the tunnel camera is put straight behind the kart at the
game camera's own distance and height, looking down the middle of the tube, and steering does nothing in the tunnel (sbWarpFrame).
Run once: py.cmd tools/mini/patch48.py"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'patch 48' not in s, 'already patched'


def rep(a, b):
    global s
    assert s.count(a) == 1, (s.count(a), a[:80])
    s = s.replace(a, b)


rep("_sbWN.decompose(w.cam.position,w.cam.quaternion,w.cam.scale);w.cb.copy(w.cam.position);",
    "_sbWN.decompose(w.cam.position,w.cam.quaternion,w.cam.scale);"
    "{/* (patch 48) square behind the kart, at the game camera's distance and height, looking down the tube */const d=clamp(Math.hypot(w.cam.position.x-w.base.x,w.cam.position.z-w.base.z),14,60),h=clamp(w.cam.position.y-w.base.y,4,30);"
    "w.cam.position.set(w.base.x,w.base.y+h,w.base.z+d);w.cam.up.set(0,1,0);w.cam.lookAt(w.base.x,w.base.y+h*.4,w.base.z-160);}w.cb.copy(w.cam.position);")
rep("if(w.kart){const st=clamp((keys.right?1:0)-(keys.left?1:0)+(PAD.act?PAD.steer:0),-1,1);",
    "if(w.kart){const st=0;/* (patch 48: no steering in the tunnel: straight through) */")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patch 48 applied')
