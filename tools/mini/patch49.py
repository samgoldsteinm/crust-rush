"""Patch 49 (web v210): headlights that light the world, and only when they are needed.
The owner: "the headlight just looks like a white triangle beam, try to make it look more realistic" (with pictures of our flat cone on
the grass and reference shots: a soft pool of cool white light on the road ahead, two lobes, brightest a little ahead, lighting walls and
kerbs as real light does), and: "for maps that have track lights or street lights only make the headlights turn on when the player is not
on the track, if there are no street lights or track lights for that track then the headlights will be the default option even on the track".
- The additive cone drawn over the ground (patch 43, reshaped in 47c) is gone: it was a picture laid on top, so it looked flat.
- The spot light now does all of it: cool white (#eef3ff), at bumper height, aimed 120 ahead and down, a wider cone (0.62) with a cookie
  (SpotLight.map, three r149 supports it without shadows): two soft lobes side by side, a low-beam cut-off along the top, brightest just
  below it. It lights the grass, the road, kerbs and walls with their own textures and shading.
- Every Sandbox place has it (it was only under an open sky). Where the place has track lights (the toy tracks' LED strips) or street
  lamps (SB_LAMPS), the headlights fade out while the kart is on the track (nearTrack, road half-width + 10) and back on off it; elsewhere
  they are on all night. The light is never hidden (visible stays true, only its strength changes): switching a light in or out makes
  every shader compile again, a stall.
Run once: py.cmd tools/mini/patch49.py"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'patch 49' not in s, 'already patched'


def rep(a, b):
    global s
    assert s.count(a) == 1, (s.count(a), a[:90])
    s = s.replace(a, b)


rep("if(R.kind==='out'){/* headlights: one spot light just ahead of the kart, looking down the road */const sp=new THREE.SpotLight('#fff1d8',0,520,.42,.6,1.0);",
    "if(true){/* headlights (patch 49: every place; a cookie shapes the light: two lobes and a low-beam cut-off) */const sp=new THREE.SpotLight('#eef3ff',0,420,.62,.45,1.15);sp.map=sbHeadCookie();")
rep("SB.grp.add(beam);Nt.beam=beam;}", "Nt.beam=null;/* (patch 49: the light itself makes the beam now) */}")
rep("sp.intensity=on?3*L:0;sp.visible=on;",
    "{const def=MAPS[mapIdx],lit=SB_LAMPS.has(def.id)||!!def.toy||Nn.led.length>0,onT=lit&&nearTrack(k.rx!=null?k.rx:k.x,k.ry!=null?k.ry:k.y,RW+10),h0=Nn.hf==null?(onT?0:1):Nn.hf;Nn.hf=h0+((onT?0:1)-h0)*.06;}"
    "sp.intensity=on?24*L*Nn.hf:0;sp.visible=true;/* (patch 49: off on a lit track; never hidden) */")
rep("sp.position.set(x+Math.cos(a)*8,y+3.5,z+Math.sin(a)*8);sp.target.position.set(x+Math.cos(a)*220,y-5,z+Math.sin(a)*220);",
    "sp.position.set(x+Math.cos(a)*7,y+4,z+Math.sin(a)*7);sp.target.position.set(x+Math.cos(a)*120,y-10,z+Math.sin(a)*120);")
rep("function sbNightArm(){",
    "/* (patch 49) the headlights' cookie: what the spot light's cone looks like, as a picture across it */\n"
    "let _sbHC=null;function sbHeadCookie(){if(_sbHC)return _sbHC;const c=cnv(256,256),g=c.getContext('2d');g.fillStyle='#000';g.fillRect(0,0,256,256);g.globalCompositeOperation='lighter';\n"
    "  for(const cx of [100,156]){g.save();g.translate(cx,150);g.scale(1.35,.72);const r=g.createRadialGradient(0,0,0,0,0,92);r.addColorStop(0,'rgba(255,255,255,1)');r.addColorStop(.45,'rgba(235,242,255,.62)');r.addColorStop(1,'rgba(200,215,255,0)');g.fillStyle=r;g.beginPath();g.arc(0,0,92,0,7);g.fill();g.restore();}\n"
    "  g.globalCompositeOperation='destination-in';const v=g.createLinearGradient(0,70,0,256);v.addColorStop(0,'rgba(0,0,0,0)');v.addColorStop(.2,'rgba(0,0,0,1)');v.addColorStop(1,'rgba(0,0,0,.85)');g.fillStyle=v;g.fillRect(0,0,256,256);\n"
    "  _sbHC=T2(c,0,0,true);return _sbHC;}\n"
    "function sbNightArm(){")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patch 49 applied')
