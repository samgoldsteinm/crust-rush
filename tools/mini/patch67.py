"""Patch 67 (web v218): the underglow lights the toy tracks too.
Patch 66's real lights light the kart and ordinary ground, but the toy tracks' surface is a ShaderMaterial that takes no scene lights
(found with a ray straight down in Sandbox's back garden: ShaderMaterial, lights false), so on them the glow was still only patch 65's
flat coloured haze. A light multiplies with what it falls on: so a second layer, shaped like the glow, is drawn with blending
  out = ground x glow colour + ground   (CustomBlending: src DstColor, dst One)
which brightens the ground in the glow's colour and keeps its own texture and shading (the wood grain, the kerbs), the way light does;
its picture is premultiplied (the colour fades out with the shape). On every glowing kart (it costs one more see-through quad), brighter
in the dark. The additive haze stays, faint, for the glow in the air; the player's real lights stay for the tyres and sills.
Run once: py.cmd tools/mini/patch67.py"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'patch 67' not in s, 'already patched'


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:90])
    s = s.replace(a, b)


# premultiplied copies of the two glow pictures
rep("const _ugF={};function ugTexFor(id){",
    "/* (patch 67) a premultiplied copy of a glow picture (colour fading with the shape), for the light layer */\n"
    "const _ugPM=new Map();function ugPM(t){if(_ugPM.has(t))return _ugPM.get(t);const src=t.image,c=cnv(src.width,src.height),x=c.getContext('2d');x.drawImage(src,0,0);const im=x.getImageData(0,0,c.width,c.height),D=im.data;"
    "for(let i=0;i<D.length;i+=4){const a=D[i+3];D[i]=D[i]*a/255;D[i+1]=D[i+1]*a/255;D[i+2]=D[i+2]*a/255;D[i+3]=255;}x.putImageData(im,0,0);const r=new THREE.CanvasTexture(c);_ugPM.set(t,r);return r;}\n"
    "const _ugF={};function ugTexFor(id){")
# the light layer beside the haze
rep("pl.renderOrder=2;g.add(pl);g.userData.ug={pl,lights:ugLs,rb:GLOWS[gi].h==='rainbow',on:true};}}",
    "pl.renderOrder=2;g.add(pl);"
    "const lm=new THREE.MeshBasicMaterial({map:ugPM(gm.map),color:gm.color.clone(),transparent:true,depthWrite:false,toneMapped:false,blending:THREE.CustomBlending,blendEquation:THREE.AddEquation,blendSrc:THREE.DstColorFactor,blendDst:THREE.OneFactor}),"
    "pl2=new THREE.Mesh(pl.geometry,lm);pl2.rotation.copy(pl.rotation);pl2.position.copy(pl.position);pl2.position.y+=.02;pl2.renderOrder=2;g.add(pl2);/* (patch 67: light on the ground: ground x colour + ground) */"
    "g.userData.ug={pl,pl2,base:gm.color.clone(),lights:ugLs,rb:GLOWS[gi].h==='rainbow',on:true};}}")
rep("if(ug.pl){ug.pl.material.opacity=ug.lights.length?.16+.22*L:.4+.4*L;if(rc)ug.pl.material.color.copy(rc);}",
    "if(ug.pl){ug.pl.material.opacity=.14+.2*L;if(rc)ug.pl.material.color.copy(rc);}if(ug.pl2){ug.pl2.material.color.copy(rc||ug.base).multiplyScalar(.75+.25*L+(k.boost>0?.15:0));}")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patch 67 applied')
