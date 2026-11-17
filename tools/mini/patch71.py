"""Patch 71 (web v222): the underglow, remade from the owner's reference photos.
The owner: the old pool "looks like a massive glowing block of blue is under the car ... it should look like ambient light coming from
under the car"; then "the light shouldnt shine so smoothly around the wheels. since the wheels cut it off a bit the light will shine behind
the wheels but not on the ground so it will be in sections the front and back and side to side instead of just a big circle around the
car. also it still looks like a circle drawn around the car on the web version" and "make it a slightly more saturated light ... keep that
ambient blur". In races it shows only when it should (the dark: the race loop's opacity .14 + .2 x darkness and the lights' strength).
The picture (ugTex) is worked out from the body's footprint (L x W, a rounded rectangle) and its wheels, in units of W:
- past the body's edge: a bright short fall (exp(-o/.09)) plus a long soft one (exp(-o/.3)): the light right under the sill and the
  ambient blur around it; under the body it stays lit (seen at the edges only);
- each tyre blocks it: beside a wheel the light is cut in a shadow that widens away from the car, so it comes out in sections (front,
  back, and each side between the wheels), as in the photos;
- the colour a little more saturated (ugSat). In the garage the two lights under the car are switched on (they were left at 0 there, so
  the web garage had only the flat picture: the PC's lights are why its garage looked softer).
Run once: py.cmd tools/mini/patch71.py"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'patch 71' not in s, 'already patched'


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:90])
    s = s.replace(a, b)


rep("let _ugG=null;function ugGenericT(){",
    "/* (patch 71) the underglow's picture from the body's footprint (lr = L/W) and its wheels (wf, wr: their x from the middle, rr: radius;\n"
    "   all in units of W): a bright fall past the sill plus a soft ambient one, cut beside each tyre into front, back and side sections */\n"
    "const UG_M=.75;const _ugV={};function ugTex(lr,wf,wr,rr){lr=+lr.toFixed(2);wf=+wf.toFixed(2);wr=+wr.toFixed(2);rr=+rr.toFixed(2);const key=[lr,wf,wr,rr].join(':');if(_ugV[key])return _ugV[key];\n"
    "  const m=UG_M,PL=lr+2*m,PW=1+2*m,W=256,H=Math.max(64,Math.round(256*PW/PL/8)*8),c=cnv(W,H),x=c.getContext('2d'),im=x.createImageData(W,H),D=im.data,rc=.28,bx=lr/2,bz=.5,sm=(a,b,v)=>{const t=Math.min(1,Math.max(0,(v-a)/(b-a)));return t*t*(3-2*t);};\n"
    "  for(let z=0;z<H;z++)for(let q=0;q<W;q++){const xs=((q+.5)/W-.5)*PL,X=Math.abs(xs),Z=Math.abs((z+.5)/H-.5)*PW,qx=X-(bx-rc),qz=Z-(bz-rc),\n"
    "      sd=Math.hypot(Math.max(qx,0),Math.max(qz,0))+Math.min(Math.max(qx,qz),0)-rc,o=Math.max(0,sd),fz=1-sm(0,m,o);let a=sd<=0?1:(.62*Math.exp(-o/.09)+.38*Math.exp(-o/.3))*fz;\n"
    "    if(Z>bz-.14)for(const xw of [wf,wr]){const out=Math.max(0,Z-bz),hw=rr*(1.05+1.5*out),dx=Math.abs(xs-xw);a*=1-.92*sm(hw,hw*.5,dx)*sm(bz-.14,bz-.02,Z);}\n"
    "    if(qx>0&&qx>qz)a*=.85;/* (nose and tail a little less than the sides) */\n"
    "    const i=(z*W+q)*4;D[i]=D[i+1]=D[i+2]=255;D[i+3]=Math.round(255*Math.max(0,Math.min(1,a)));}\n"
    "  x.putImageData(im,0,0);return _ugV[key]=new THREE.CanvasTexture(c);}\n"
    "function ugSat(h){const c=new THREE.Color(h),o={};c.getHSL(o);return c.setHSL(o.h,Math.min(1,o.s*1.15+.05),o.l*.96);}\n"
    "let _ugG=null;function ugGenericT(){")
# the footprint and wheels: a car's from its pack (the silhouette's box, its wheels), a code-built kart's from its axles
rep("if(gi&&GLOWS[gi]&&GLOWS[gi].h&&!cfg.hover){const hg=cfg.car?ugTexFor(cfg.car):null,W=hg?hg.w*1.5:(cfg.fw[0]-cfg.rw[0]+2*Math.max(cfg.rw[2],cfg.fw[2])+3)*1.45,H=hg?hg.h*2:(2*Math.max(cfg.fw[1],cfg.rw[1])+2.6)*1.9,",
    "if(gi&&GLOWS[gi]&&GLOWS[gi].h&&!cfg.hover){const hg=cfg.car?ugTexFor(cfg.car):null,bL=hg?hg.w*.84:cfg.fw[0]-cfg.rw[0]+2*Math.max(cfg.rw[2],cfg.fw[2])+3,bW=hg?hg.h*.84:2*Math.max(cfg.fw[1],cfg.rw[1])+2.6,"
    "cx0=hg?hg.cx:(cfg.fw[0]+cfg.rw[0])/2,wq=cfg.car&&CAR_PACKS[cfg.car].h.wheels||null,wF=wq?(wq.find(q=>q.f)||{c:[cfg.fw[0]]}):{c:[cfg.fw[0]],r:cfg.fw[2]},wR=wq?(wq.find(q=>!q.f)||{c:[cfg.rw[0]]}):{c:[cfg.rw[0]],r:cfg.rw[2]},"
    "ugT=ugTex(bL/bW,(wF.c[0]-cx0)/bW,(wR.c[0]-cx0)/bW,(wF.r||wR.r||1.3)/bW),W=bL+2*UG_M*bW,H=bW*(1+2*UG_M),")
rep("gm=new THREE.MeshBasicMaterial({map:hg?hg.t:ugGenericT(),color:GLOWS[gi].h==='rainbow'?'#ff3030':GLOWS[gi].h,",
    "gm=new THREE.MeshBasicMaterial({map:ugT,color:ugSat(GLOWS[gi].h==='rainbow'?'#ff3030':GLOWS[gi].h),/* (patch 71) */")
rep("transparent:true,opacity:.8,depthWrite:false,blending:THREE.AdditiveBlending,toneMapped:false}),pl=",
    "transparent:true,opacity:(c=>.62*(1-.45*(.3*c.r+.59*c.g+.11*c.b)))(ugSat(GLOWS[gi].h==='rainbow'?'#ff3030':GLOWS[gi].h)),depthWrite:false,blending:THREE.AdditiveBlending,toneMapped:false}),pl=")
rep("lm=new THREE.MeshBasicMaterial({map:ugPM(gm.map),color:gm.color.clone(),", "lm=new THREE.MeshBasicMaterial({map:ugPM(gm.map),color:gm.color.clone().multiplyScalar(gm.opacity/.62),")
rep("g.userData.ug={pl,pl2,base:gm.color.clone(),", "g.userData.ug={pl,pl2,base:gm.color.clone().multiplyScalar(gm.opacity/.62),")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patch 71 applied')
