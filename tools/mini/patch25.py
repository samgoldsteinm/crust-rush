"""Patch 25 (web v191): Balloon Battle, on top of the boxes and the block.
The owner, 2026-11-13, from the pizza boxes: "the camera angle is really bad and the car sort of floats on the object".
The drawn ground under a kart, the five heights its body is laid on, and with them the chase camera's height all read the lap's ground,
which in the arena is the bare table: so up on the 42-unit route the camera stayed down at table height looking up through the boxes,
and the body sat wrong. Patch 22 had made Sandbox read its own ground there; a battle needs the arena's (battleG) just the same.
  - those six read `BATTLE?battleG(..)` (battleG hands on to Sandbox's ground when Sandbox is on, so Sandbox is as it was);
  - battle.js: bbCam() stops the camera short of anything of the arena that stands between it and the kart.
Run once: py.cmd tools/mini/patch25.py   (then inject_mini.py)"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'BATTLE?battleG(x,y,z)' not in s, 'already patched'


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:70])
    s = s.replace(a, b)


rep("{let rg=SBX?sbG(x,y,z):", "{let rg=BATTLE?battleG(x,y,z):")
for a in ("x+ca*fF,y+sa*fF", "x+ca*fR,y+sa*fR", "x-sa*fW,y+ca*fW", "x+sa*fW,y-ca*fW", "x,y"):
    rep(f"SBX?sbG({a},z+1):", f"BATTLE?battleG({a},z+1):")
open(p, 'w', encoding='utf-8', newline='').write(s)

p = 'D:/crust-rush/source/tools/mini/battle.js'
s = open(p, encoding='utf-8', newline='').read()
rep("function battleRender(time){if(SBX)return sbRender(time);if(!BATTLE||!BB.grp)return;",
    "/* the chase camera must not sit inside the boxes, the block or a pan: walk from the kart out to where the camera wants to be and stop short of the\n"
    "   first thing of the arena that is higher than the camera there. It closes in at once and eases back out. */\n"
    "function bbCam(){const k=camT;if(!k||state==='menu')return;const tx=k.x,tz=k.y,ty=(k.wy||0)+7,cx=camera.position.x,cy=camera.position.y,cz=camera.position.z;let ok=1;\n"
    "  for(let i=1;i<=16;i++){const f=i/16,g=Math.min(1.05,f+.05);if(battleG(tx+(cx-tx)*g,tz+(cz-tz)*g)>ty+(cy-ty)*g-2){ok=(i-1)/16;break;}}\n"
    "  const was=BB.camF==null?1:BB.camF;BB.camF=ok<was?ok:Math.min(ok,was+.02);const f=Math.max(.16,BB.camF);if(f>=.999)return;\n"
    "  camera.position.set(tx+(cx-tx)*f,ty+(cy-ty)*f+(1-f)*9,tz+(cz-tz)*f);camera.lookAt(cam.look.x,cam.look.y+cam.oy*.45,cam.look.z);}\n"
    "function battleRender(time){if(SBX)return sbRender(time);if(!BATTLE)return;bbCam();if(!BB.grp)return;")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patched')
