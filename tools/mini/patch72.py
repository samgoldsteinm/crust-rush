"""Patch 72 (web v222): the garage's look and three style-shop fixes.
The owner: "the chrome interior is still showing up as black and the trim color you pick should also effect the interior trim. the
rainbow color also doesnt work ... currently it sits on a brown circle can you make that area look better. it will also help the player
see the underglow to the car better because it doesnt look good on the brown right now".
- The garage: the underglow's two lights are lit (intensity 7; they were created at 0 and only the race loop set them), and a rainbow
  glow cycles there too (only the race loop cycled it, so the garage showed a fixed red).
- Chrome (or any metal) on the interior: metalness .85 made it a mirror of the dark cabin, so black. Now .45 with roughness .28 and the
  colour kept: it reads as polished metal, not a hole.
- The trim colour also takes the interior's metal trim (class 'metal', 7: the INT_ALU / interior metal pieces), with the dark plastics
  (class 'dark', 1, inside and out) it already took.
- The garage floor: a dark showroom floor (polished, a soft lighter spot under the car fading to the edge) instead of the brown disc, and
  the panel behind it charcoal, so a glow reads; the yellow ring stays as the stage's edge.
Run once: py.cmd tools/mini/patch72.py"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'patch 72' not in s, 'already patched'


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:90])
    s = s.replace(a, b)


# the garage: the glow's lights on, the rainbow cycling
rep("  gModel.gl.rotation.z=Math.sin(performance.now()/700)*.05;frameGarageCam(",
    "  gModel.gl.rotation.z=Math.sin(performance.now()/700)*.05;{/* (patch 72) the underglow in the garage: its lights on, a rainbow cycling */const ug=gModel.g.userData.ug;if(ug&&ug.on){const rc=ug.rb?rainbowC(performance.now()/1000,0):null;for(const l of ug.lights){l.intensity=.6;if(rc)l.color.copy(rc);}if(rc){if(ug.pl)ug.pl.material.color.copy(rc);if(ug.pl2)ug.pl2.material.color.copy(rc);}}}frameGarageCam(")
# interior metal: not a black mirror
rep("uTM:{value:new THREE.Vector4(t.m?.9:.25,t.m?(t.r||.22):.4,n.m?.85:0,n.m?.25:.6)}};",
    "uTM:{value:new THREE.Vector4(t.m?.9:.25,t.m?(t.r||.22):.4,n.m?.45:0,n.m?.28:.6)}};/* (patch 72: interior metal .45, not a black mirror) */")
# the trim colour on the interior's metal trim too
rep("+'if(uOn.x>.5&&(abs(sCi-1.)<.1||abs(sCi-6.)<.1||abs(sCi-15.)<.1)){",
    "+'if(uOn.x>.5&&(abs(sCi-1.)<.1||abs(sCi-6.)<.1||abs(sCi-7.)<.1||abs(sCi-15.)<.1)){")
# the floor
rep("    const fl=new THREE.Mesh(new THREE.CircleGeometry(15.5,64),new THREE.MeshStandardMaterial({color:'#3a2216',roughness:.85}));fl.rotation.x=-Math.PI/2;fl.receiveShadow=true;gS.add(fl);",
    "    const fl=new THREE.Mesh(new THREE.CircleGeometry(15.5,96),new THREE.MeshStandardMaterial({map:gFloorTex(),roughness:.62,metalness:0,envMapIntensity:.6}));fl.rotation.x=-Math.PI/2;fl.receiveShadow=true;gS.add(fl);/* (patch 72: a dark showroom floor) */")
rep("function openGarage(){garageOpen=true;",
    "/* (patch 72) the garage's floor: dark polished charcoal, a softer lighter spot under the car, fine circular brushing, darker to the edge */\n"
    "function gFloorTex(){const N=512,c=cnv(N,N),g=c.getContext('2d'),gr=g.createRadialGradient(N/2,N/2,0,N/2,N/2,N/2);gr.addColorStop(0,'#3a3c44');gr.addColorStop(.45,'#26272d');gr.addColorStop(1,'#121317');g.fillStyle=gr;g.fillRect(0,0,N,N);\n"
    "  const t=new THREE.CanvasTexture(c);t.encoding=THREE.sRGBEncoding;t.anisotropy=8;return t;}\n"
    "function openGarage(){garageOpen=true;")
rep(".g-view{position:relative;min-width:0;min-height:0;border-radius:18px;overflow:hidden;background:radial-gradient(ellipse at 50% 35%,#3a2216,#1c0f0a 75%);",
    ".g-view{position:relative;min-width:0;min-height:0;border-radius:18px;overflow:hidden;background:radial-gradient(ellipse at 50% 35%,#2c2d33,#0e0f12 75%);")
# races: the glow only when it should (the dark): the lights off by day, the picture faint
rep("if(ug.pl){ug.pl.material.opacity=.14+.2*L;", "if(ug.pl){ug.pl.material.opacity=.06+.4*L;/* (patch 72) */")
rep("for(const l of ug.lights){l.intensity=ug.on?(2.4+7*L)*(k.boost>0?1.2:1):0;", "for(const l of ug.lights){l.intensity=ug.on?6*L*(k.boost>0?1.2:1):0;")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patch 72 applied')
