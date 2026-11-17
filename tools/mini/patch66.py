"""Patch 66 (web v218): the underglow is light, not a coloured patch.
The owner, of patch 65's underglow: "the colors look good but it doesnt look like light it looks flat make the the lighting more
ambient and not just solid colors. its a similar issue that we had with the headlights".
Why it looked flat: an additive picture adds the same colour whatever it lies on, so the ground's own texture and shading disappear
under an even coloured shape. Real light multiplies with what it falls on: the wood grain, the kerbs, the tyres' and sills' undersides
pick the colour up, brightest near the body and fading with distance (the photos).
Now the kart you drive carries two real coloured lights under it (front and rear axle, low down, a soft falloff), which light the ground
and the underside; the picture stays only as a faint haze (the glow in the air) and as the cheap glow under OTHER karts, which carry no
lights (a full grid of lights would cost too much, and the number of lights must not change mid-race: the shader-recompile stalls).
The player's model always has the two lights (dark when no glow is chosen), so the light count is the same whatever is worn.
In the garage preview too (spec.ugL). Brighter in the dark (Sandbox's clock, night tracks).
Run once: py.cmd tools/mini/patch66.py"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'patch 66' not in s, 'already patched'


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:90])
    s = s.replace(a, b)


rep("if(gi&&GLOWS[gi]&&GLOWS[gi].h&&!cfg.hover){const hg=cfg.car?ugTexFor(cfg.car):null,",
    "const ugLs=[];if(spec.ugL&&!cfg.hover){/* (patch 66) real light under the kart you drive: front and rear, low, a soft falloff */for(const ax of [cfg.fw[0]*.55,cfg.rw[0]*.55]){const L=new THREE.PointLight(GLOWS[gi]&&GLOWS[gi].h&&GLOWS[gi].h!=='rainbow'?GLOWS[gi].h:'#ff3030',0,120,1.3);L.position.set(ax,.3,0);L.castShadow=false;g.add(L);ugLs.push(L);}g.userData.ug={pl:null,lights:ugLs,rb:GLOWS[gi]&&GLOWS[gi].h==='rainbow',on:!!(gi&&GLOWS[gi]&&GLOWS[gi].h)};}\n"
    "if(gi&&GLOWS[gi]&&GLOWS[gi].h&&!cfg.hover){const hg=cfg.car?ugTexFor(cfg.car):null,")
rep("pl.renderOrder=2;g.add(pl);g.userData.ug={pl,rb:GLOWS[gi].h==='rainbow'};}}",
    "pl.renderOrder=2;g.add(pl);g.userData.ug={pl,lights:ugLs,rb:GLOWS[gi].h==='rainbow',on:true};}}")
rep("{const ug=m.g.userData.ug;if(ug){/* (patch 65) the underglow: brighter in the dark */const L=SBX&&typeof sbClockF==='function'?sbClockF().L:(MAPS[mapIdx]&&MAPS[mapIdx].theme==='night'?1:0);ug.pl.material.opacity=.5+.5*L+(k.boost>0?.15:0);if(ug.rb)ug.pl.material.color.copy(rainbowC(time,k.ri*.13));}}",
    "{const ug=m.g.userData.ug;if(ug){/* (patch 65) the underglow: brighter in the dark; (patch 66) the light does the work, the picture is a haze over it */const L=SBX&&typeof sbClockF==='function'?sbClockF().L:(MAPS[mapIdx]&&MAPS[mapIdx].theme==='night'?1:0),rc=ug.rb?rainbowC(time,k.ri*.13):null;"
    "if(ug.pl){ug.pl.material.opacity=ug.lights.length?.16+.22*L:.4+.4*L;if(rc)ug.pl.material.color.copy(rc);}for(const l of ug.lights){l.intensity=ug.on?(2.4+7*L)*(k.boost>0?1.2:1):0;if(rc)l.color.copy(rc);}}}")
# the player's model and the garage preview carry the lights
rep("u:build.u||0,st:build.st||null},m=getModel(spec)", "u:build.u||0,st:build.st||null,ugL:isPlayer?1:0},m=getModel(spec)")
rep("s.st?JSON.stringify(s.st):''].join('.');", "s.st?JSON.stringify(s.st):'',s.ugL?1:0].join('.');")
rep("gModel=buildKart(Object.assign({ri:selected},playerBuild));", "gModel=buildKart(Object.assign({ri:selected,ugL:1},playerBuild));/* (patch 66: the underglow's lights in the preview) */")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patch 66 applied')
