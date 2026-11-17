"""Patch 71 (web v222): underglow styles to choose from.
The owner (on v221's garage: "it looks like a massive glowing block of blue is under the car ... it should look like ambient light coming
from under the car ... brightest at the center ... the edges should look a little fuzzy ... Make a few different versions").
The old pool was the body's silhouette, blurred a little and filled evenly, on a plane 1.5-2x the body: a solid shape. Now the picture is
worked out from the body's own footprint (length L, width W) with a margin m of ground around it: under the body (r = 0 middle, 1 at the
body's edge, a rounded-rectangle distance) it is brightest in the middle; past the body's edge (o = 0 at the edge, 1 at the plane's
edge) it fades out softly, with no line anywhere. Four versions (UGV; in the spec key, so a change rebuilds the kart):
  1 Soft pool:      a bright middle, an even soft fade over m = .5 W.
  2 Core and halo:  a strong core under the car and a wide faint halo (m = .75 W).
  3 Side strips:    the light leaks out mostly along the sills (as the photos), less at nose and tail.
  4 Wide and faint: one broad, dim wash (m = .9 W).
  0 the old silhouette pool (for comparison).
The light layer (patch 67, ground x colour) uses the same picture.
Run once: py.cmd tools/mini/patch71.py"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'patch 71' not in s, 'already patched'


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:90])
    s = s.replace(a, b)


rep("let _ugG=null;function ugGenericT(){",
    "/* (patch 71) the underglow's styles, from the body's footprint L x W and a margin m of ground around it (all in units of W) */\n"
    "let UGV=1;try{const q=store.get('crust-ugv');if(q!=null&&+q>=0&&+q<=4)UGV=+q;}catch(e){}\n"
    "const UG_M=[0,.8,.9,.7,1.1];\n"
    "const _ugV={};function ugVarT(v,lr){const key=v+':'+lr.toFixed(1);if(_ugV[key])return _ugV[key];lr=+lr.toFixed(1);const m=UG_M[v],PL=lr+2*m,PW=1+2*m,W=256,H=Math.max(64,Math.round(256*PW/PL/8)*8),c=cnv(W,H),x=c.getContext('2d'),im=x.createImageData(W,H),D=im.data,rc=.3;\n"
    "  for(let z=0;z<H;z++)for(let q=0;q<W;q++){const X=Math.abs((q+.5)/W-.5)*PL,Z=Math.abs((z+.5)/H-.5)*PW,bx=lr/2,bz=.5,\n"
    "      qx=X-(bx-rc),qz=Z-(bz-rc),sd=Math.hypot(Math.max(qx,0),Math.max(qz,0))+Math.min(Math.max(qx,qz),0)-rc,o=Math.max(0,sd),t=Math.min(1,o/m),fz=1-t*t*(3-2*t),\n"
    "      r=Math.pow(Math.pow(X/bx,4)+Math.pow(Z/bz,4),.25),k=Math.max(0,1-r*r),side=.4+.6*Math.min(1,Math.max(0,1-(X-bx)/.5));let a;\n"
    "    if(v===2)a=sd<=0?.6+.4*k*k:.6*(.55/(1+(o/.1)*(o/.1))+.45*Math.exp(-(o/.45)*(o/.45)))*fz;\n"
    "    else if(v===3)a=sd<=0?.8:.8/(1+(o/.14)*(o/.14))*side*fz;\n"
    "    else if(v===4)a=sd<=0?.45+.15*k:.45/(1+(o/.35)*(o/.35))*fz;\n"
    "    else a=sd<=0?.75+.25*k:.75/(1+(o/.16)*(o/.16))*fz;\n"
    "    const i=(z*W+q)*4;D[i]=D[i+1]=D[i+2]=255;D[i+3]=Math.round(255*Math.max(0,Math.min(1,a)));}\n"
    "  x.putImageData(im,0,0);return _ugV[key]=new THREE.CanvasTexture(c);}\n"
    "let _ugG=null;function ugGenericT(){")
rep("if(gi&&GLOWS[gi]&&GLOWS[gi].h&&!cfg.hover){const hg=cfg.car?ugTexFor(cfg.car):null,W=hg?hg.w*1.5:(cfg.fw[0]-cfg.rw[0]+2*Math.max(cfg.rw[2],cfg.fw[2])+3)*1.45,H=hg?hg.h*2:(2*Math.max(cfg.fw[1],cfg.rw[1])+2.6)*1.9,",
    "if(gi&&GLOWS[gi]&&GLOWS[gi].h&&!cfg.hover){const hg=cfg.car?ugTexFor(cfg.car):null,uv=UGV,bL=hg?hg.w:cfg.fw[0]-cfg.rw[0]+2*Math.max(cfg.rw[2],cfg.fw[2])+3,bW=hg?hg.h:2*Math.max(cfg.fw[1],cfg.rw[1])+2.6,"
    "W=uv?bL+2*UG_M[uv]*bW:bL*(hg?1.5:1.45),H=uv?bW*(1+2*UG_M[uv]):bW*(hg?2:1.9),")
rep("gm=new THREE.MeshBasicMaterial({map:hg?hg.t:ugGenericT(),",
    "gm=new THREE.MeshBasicMaterial({map:uv?ugVarT(uv,bL/bW):hg?hg.t:ugGenericT(),/* (patch 71) */")
rep("s.st?JSON.stringify(s.st):'',s.ugL?1:0].join('.'", "s.st?JSON.stringify(s.st):'',s.ugL?1:0,s.st&&s.st.gl?UGV:0].join('.'")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patch 71 applied')
