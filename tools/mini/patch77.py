"""Patch 77 (web v222): the underglow remade as LED strips (the owner's brief: "a professionally rendered automotive underglow ...
LED strips installed along the vehicle's undercarriage", the same look on the PC and the web).
The light (ugLs; the PC's shaders/underglow.gdshaderinc is the same sum, line for line):
- four strips at the body's underside (ugParams: the body's outline, its sill height and its wheels, from the car's own model): one
  under each sill between the wheels, one under each bumper; each is summed as a continuous line of light (the closed form of a
  line source over the ground, in six or four pieces), so no single spots or seams show;
- each strip faces down and a little outward (under the car is dimmer than the edge where the light escapes);
- the tyres block it (each piece's ray to the ground tested against the tyres' footprints, a soft fall through them), so it comes out
  in sections and the ground under a tyre stays dark;
- a little light bounced out from under the body, fading over a distance set by the body's width and its height;
- the strips' height is the car's sill height: a low supercar's glow is tight, an SUV's or a monster truck's wider;
- the light is smooth-limited (1 - e^-t), so it never clips to white, and it ends with the margin round the body (no edges).
The picture is worked out once per car (ugBake, 160 wide, cached) into a data texture (the light's square root, for the dark tail's
precision). Colour: the chosen colour a little more saturated (ugSat), evened out by its brightness (ugComp: a dark blue is lifted, a
pale cyan or yellow is brought down, the colour itself unchanged).
In races the two sheets stay (lit only in the dark, as before), with the new picture. In the garage the sheets are hidden and the floor
itself is lit (ugFloorMat: its material adds floor colour x light, so the floor keeps its look), and the two lights under the car only
tint the lowest panels and tyres (decay 2, reaching 2.4 x the half-width; they had reached 120 units, two bright pools).
Run once (after patches 71-76): py.cmd tools/mini/patch77.py"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'patch 77' not in s, 'already patched'


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:90])
    s = s.replace(a, b)


def cut(a, z, b):
    """replace from a up to and including z (the first z after a)"""
    global s
    i = s.find(a)
    assert i >= 0 and s.count(a) == 1, ('cut start', a[:80])
    j = s.find(z, i)
    assert j > i, ('cut end', z[:80])
    s = s[:i] + b + s[j + len(z):]


LIB = r"""/* (patch 77) the underglow as LED strips under the sills and bumpers: ugParams (the body's outline, sill height and wheels, in the
   kart's own units, from the body's centre), ugLs (the light on the ground at a point), ugBake (the picture). The PC's
   shaders/underglow.gdshaderinc is the same sum, line for line */
const UG_GAIN=1,UG_REF=.048,UG_BOUNCE=.35,UG_BOUNCE_R=1.6;/* (the garage floor's light; the floor's own colour at the middle; the lights under the car, garage and race) */
function ugSm(a,b,v){const t=Math.min(1,Math.max(0,(v-a)/(b-a)));return t*t*(3-2*t);}
const _ugPc={};
function ugParams(cfg){const id=cfg.car&&CAR_PACKS[cfg.car]?cfg.car:null,key=id||('k'+[cfg.fw,cfg.rw].join());if(_ugPc[key])return _ugPc[key];let P;
  if(id){const g=carGeos(id),hw=CAR_PACKS[id].h.wheels||[];let x0=1e9,x1=-1e9,z0=1e9,z1=-1e9,y0=1e9;const V=[];
    for(const k in g){if(!k.startsWith('b_'))continue;const A=g[k].attributes.position.array;for(let i=0;i<A.length;i+=3){const x=A[i],y=A[i+1],z=A[i+2];if(x<x0)x0=x;if(x>x1)x1=x;if(z<z0)z0=z;if(z>z1)z1=z;if(y<y0)y0=y;V.push(x,y,z);}}
    const cx=(x0+x1)/2,cz=(z0+z1)/2,avg=A=>A.reduce((u,v)=>u+v,0)/(A.length||1),F=hw.filter(q=>q.c[0]>cx),R=hw.filter(q=>q.c[0]<=cx),pct=(A,f)=>{if(!A.length)return null;A.sort((u,v)=>u-v);return A[Math.min(A.length-1,Math.floor(A.length*f))];};
    const a=(x1-x0)/2*.96,wf=F.length?avg(F.map(q=>q.c[0]))-cx:a*.6,wr=R.length?avg(R.map(q=>q.c[0]))-cx:-a*.6,rf=F.length?avg(F.map(q=>q.r)):0,rr=R.length?avg(R.map(q=>q.r)):0,
      wz=hw.length?avg(hw.map(q=>Math.abs(q.c[2]-cz))):0,tw=hw.length?avg(hw.map((q,i)=>packTyreW(id,i,true))):0,rA=(rf+rr)/2||1;
    /* the body's half-width low down (mirrors and wings left out); the sill height: the low 5% of the body between the wheels, at its sides */
    const zs=[];for(let i=0;i<V.length;i+=3)if(V[i+1]<y0+1.6*rA)zs.push(Math.abs(V[i+2]-cz));let b=pct(zs,.97)||(z1-z0)/2;const bike=wz<.25*b;if(!bike)b=Math.max(b,wz+tw*.35);
    const ys=[];for(let i=0;i<V.length;i+=3){const x=V[i]-cx;if(x>wr+rr&&x<wf-rf&&Math.abs(V[i+2]-cz)>.6*b)ys.push(V[i+1]);}let h=bike?.6*rA:(pct(ys,.05)??.5*rA);h=Math.min(1.6*rA,Math.max(.25*rA,h));
    P={a,b,cx,cz,h,wf,wr,rf,rr,wz,tw};}
  else{const f=cfg.fw,r=cfg.rw,rA=(f[2]+r[2])/2,hx=(f[0]-r[0])/2;P={a:hx+Math.max(f[2],r[2])+1.5,b:(Math.max(f[1],r[1])+1.3)*.85,cx:(f[0]+r[0])/2,cz:0,h:.45*rA,wf:hx,wr:-hx,rf:f[2],rr:r[2],wz:(f[1]+r[1])/2,tw:.9*rA};}
  for(const k in P)P[k]=+(+P[k]).toFixed(3);return _ugPc[key]=ugDerive(P);}
function ugDerive(P){P.kT=5/Math.max(.2,Math.min(P.tw||1,(P.rf+P.rr)/2||1));P.M=.45*P.b+1.5*P.h;return P;}
/* the length of the ground ray o -> o+d inside a tyre's footprint (centre cx,cz, half-sizes ex,ez) */
function ugSlab(ox,oz,dx,dz,cx,cz,ex,ez){if(ex<=0)return 0;let t0=0,t1=1;
  if(Math.abs(dx)<1e-6){if(Math.abs(ox-cx)>ex)return 0;}else{const u=(cx-ex-ox)/dx,v=(cx+ex-ox)/dx;t0=Math.max(t0,Math.min(u,v));t1=Math.min(t1,Math.max(u,v));}
  if(Math.abs(dz)<1e-6){if(Math.abs(oz-cz)>ez)return 0;}else{const u=(cz-ez-oz)/dz,v=(cz+ez-oz)/dz;t0=Math.max(t0,Math.min(u,v));t1=Math.min(t1,Math.max(u,v));}
  return t1>t0?(t1-t0)*Math.hypot(dx,dz):0;}
/* one strip x0,z0 -> x1,z1 at height h facing n (outward), in n pieces, each a continuous line of light (h/r^3 summed in closed form)
   blocked by the two tyres beside it; adds the light and the light unblocked to acc */
function ugStrip(px,pz,x0,z0,x1,z1,nx,nz,n,O1,O2,h,kT,acc){const len=Math.hypot(x1-x0,z1-z0);if(len<1e-4)return;const tx=(x1-x0)/len,tz=(z1-z0)/len,al=(px-x0)*tx+(pz-z0)*tz,dp=(px-x0)*nx+(pz-z0)*nz,r2=dp*dp+h*h,rho=Math.sqrt(r2),I=.3+.7*ugSm(-.5,.6,dp/rho);
  for(let k=0;k<n;k++){const ta=k*len/n-al,tb=(k+1)*len/n-al,e=I*h/r2*(tb/Math.sqrt(tb*tb+r2)-ta/Math.sqrt(ta*ta+r2)),sx=x0+tx*(k+.5)*len/n,sz=z0+tz*(k+.5)*len/n,dx=px-sx,dz=pz-sz,
    L=ugSlab(sx,sz,dx,dz,O1[0],O1[1],O1[2],O1[3])+ugSlab(sx,sz,dx,dz,O2[0],O2[1],O2[2],O2[3]);acc[0]+=e*Math.exp(-L*kT);acc[1]+=e;}}
function ugLs(P,px,pz){const {a,b,h,wf,wr,wz,rf,rr,M,kT}=P,tw=Math.max(P.tw,.2),ins=.08*b,zs=b-ins,acc=[0,0],
    oFp=[wf,wz,rf*.85,tw*.5],oFm=[wf,-wz,rf*.85,tw*.5],oRp=[wr,wz,rr*.85,tw*.5],oRm=[wr,-wz,rr*.85,tw*.5],x0=wr+rr*1.1,x1=wf-rf*1.1;
  if(x1>x0){ugStrip(px,pz,x0,zs,x1,zs,0,1,6,oFp,oRp,h,kT,acc);ugStrip(px,pz,x0,-zs,x1,-zs,0,-1,6,oFm,oRm,h,kT,acc);}
  const xF=Math.max(wf+rf*1.15,a-2*ins),xR=Math.min(wr-rr*1.15,-a+2*ins),zw=.75*zs;
  ugStrip(px,pz,xF,-zw,xF,zw,1,0,4,oFp,oFm,h,kT,acc);ugStrip(px,pz,xR,-zw,xR,zw,-1,0,4,oRp,oRm,h,kT,acc);
  const rc=.3*b,Lb=.15*b+.6*h,qx=Math.abs(px)-(a-rc),qz=Math.abs(pz)-(b-rc),sd=Math.hypot(Math.max(qx,0),Math.max(qz,0))+Math.min(Math.max(qx,qz),0)-rc,
    t=acc[0]*h/1.2+.22*Math.exp(-Math.max(sd,0)/Lb)*(.2+.8*(acc[1]>0?acc[0]/acc[1]:1));
  return (1-Math.exp(-1.25*t))*(1-ugSm(.5*M,M,sd));}
/* the picture, once per car: tA (rgb = alpha = the light's square root: an additive sheet gives colour x light), tP (the light, for the
   ground x colour sheet); W, H its size in the kart's units */
const _ugB=new Map();function ugBake(P){if(_ugB.has(P))return _ugB.get(P);const PL=2*(P.a+P.M),PW=2*(P.b+P.M),W=160,H=Math.max(32,Math.round(W*PW/PL/2)*2),A=new Uint8Array(W*H*4),Q=new Uint8Array(W*H*4);
  for(let z=0;z<H/2;z++){const pz=((z+.5)/H-.5)*PW;for(let q=0;q<W;q++){const v=Math.max(0,Math.min(1,ugLs(P,((q+.5)/W-.5)*PL,pz))),sq=Math.round(255*Math.sqrt(v)),l=Math.round(255*v);
    for(const zz of [z,H-1-z]){const i=(zz*W+q)*4;A[i]=A[i+1]=A[i+2]=A[i+3]=sq;Q[i]=Q[i+1]=Q[i+2]=l;Q[i+3]=255;}}}
  const mk=D=>{const t=new THREE.DataTexture(D,W,H,THREE.RGBAFormat);t.magFilter=t.minFilter=THREE.LinearFilter;t.needsUpdate=true;return t;},B={tA:mk(A),tP:mk(Q),W:PL,H:PW};_ugB.set(P,B);return B;}
/* the colour evened out by its brightness (the colour itself kept): a dark blue lifted, a pale cyan or yellow brought down */
function ugComp(c){const Y=.2126*c.r+.7152*c.g+.0722*c.b;return Math.min(1.6,Math.max(.8,Math.pow(.25/Math.max(Y,.01),.3)));}
/* the garage floor lit by the glow: floor colour x light added to its lighting, so it keeps its look (UGF: the car's picture and place) */
const UGF={uUgOn:{value:0},uUgInv:{value:new THREE.Matrix4()},uUgSize:{value:new THREE.Vector2(1,1)},uUgMap:{value:null},uUgCol:{value:new THREE.Color(0,0,0)}},_ugV3=new THREE.Vector3();
function ugFloorMat(m){m.onBeforeCompile=sh=>{Object.assign(sh.uniforms,UGF);
    sh.vertexShader=sh.vertexShader.replace('#include <common>','#include <common>\nvarying vec3 vUgW;').replace('#include <fog_vertex>','#include <fog_vertex>\nvUgW=(modelMatrix*vec4(transformed,1.0)).xyz;');
    sh.fragmentShader=sh.fragmentShader.replace('#include <common>','#include <common>\nvarying vec3 vUgW;uniform float uUgOn;uniform mat4 uUgInv;uniform vec2 uUgSize;uniform sampler2D uUgMap;uniform vec3 uUgCol;')
      .replace('#include <lights_fragment_end>','#include <lights_fragment_end>\nif(uUgOn>.5){vec2 uq=(uUgInv*vec4(vUgW,1.)).xy/uUgSize+.5;if(uq.x>0.&&uq.x<1.&&uq.y>0.&&uq.y<1.){float us=texture2D(uUgMap,uq).r;reflectedLight.indirectDiffuse+=diffuseColor.rgb*uUgCol*(us*us);}}');};
  m.customProgramCacheKey=()=>'ugfloor';return m;}
/* each garage frame: the floor lit from the car's picture (the sheets hidden), the lights under the car tinting its lowest panels */
function ugGarage(g){const ug=g&&g.userData.ug,U=UGF;if(!ug||!ug.on||!ug.pl){U.uUgOn.value=0;return;}
  const rc=ug.rb?rainbowC(performance.now()/1000,0):null,col=rc?ugSat(rc):ug.col,cp=rc?ugComp(col):ug.cp;ug.pl.visible=ug.pl2.visible=false;
  ug.pl.updateWorldMatrix(true,false);U.uUgInv.value.copy(ug.pl.matrixWorld).invert();U.uUgSize.value.set(ug.B.W,ug.B.H);U.uUgMap.value=ug.B.tA;U.uUgCol.value.copy(col).multiplyScalar(cp*UG_GAIN/UG_REF);U.uUgOn.value=1;
  const ws=ug.pl.getWorldScale(_ugV3).x;for(const l of ug.lights){l.color.copy(col);l.intensity=UG_BOUNCE*cp;l.distance=(l.userData.ld||10)*ws;}}
"""

# the old picture (patch 71's ugTex) goes; ugSat stays
cut("/* (patch 71) the underglow's picture from the body's footprint", "x.putImageData(im,0,0);return _ugV[key]=new THREE.CanvasTexture(c);}\n", LIB)

# the sheets under the kart: the new picture
cut("if(gi&&GLOWS[gi]&&GLOWS[gi].h&&!cfg.hover){const hg=cfg.car?ugTexFor(cfg.car):null,bL=", "rb:GLOWS[gi].h==='rainbow',on:true};}",
    "if(gi&&GLOWS[gi]&&GLOWS[gi].h&&!cfg.hover){/* (patch 77) LED strips: the picture from the body and its wheels */const P=ugParams(cfg),B=ugBake(P),col=ugSat(GLOWS[gi].h==='rainbow'?'#ff3030':GLOWS[gi].h),cp=ugComp(col),"
    "gm=new THREE.MeshBasicMaterial({map:B.tA,color:col.clone().multiplyScalar(cp*.75),transparent:true,opacity:.46,depthWrite:false,blending:THREE.AdditiveBlending,toneMapped:false}),pl=new THREE.Mesh(new THREE.PlaneGeometry(B.W,B.H),gm);"
    "pl.rotation.x=-Math.PI/2;pl.position.set(P.cx,.22,P.cz);pl.renderOrder=2;g.add(pl);"
    "const lm=new THREE.MeshBasicMaterial({map:B.tP,color:col.clone().multiplyScalar(cp*.75),transparent:true,depthWrite:false,toneMapped:false,blending:THREE.CustomBlending,blendEquation:THREE.AddEquation,blendSrc:THREE.DstColorFactor,blendDst:THREE.OneFactor}),"
    "pl2=new THREE.Mesh(pl.geometry,lm);pl2.rotation.copy(pl.rotation);pl2.position.copy(pl.position);pl2.position.y+=.02;pl2.renderOrder=2;g.add(pl2);/* (ground x colour + ground) */"
    "ugLs.forEach((L,i)=>{L.position.set(P.cx+(i?P.wr:P.wf)*.5,P.h*.55,P.cz);L.decay=2;L.userData.ld=P.b*2.4;L.color.copy(col);});/* (low under the car, short: they tint its lowest panels and tyres) */"
    "g.userData.ug={pl,pl2,P,B,col,cp,base:col.clone().multiplyScalar(cp*.75),lights:ugLs,rb:GLOWS[gi].h==='rainbow',on:true};}")

# races: the lights under the kart short and soft
rep("for(const l of ug.lights){l.intensity=ug.on?6*L*(k.boost>0?1.2:1):0;if(rc)l.color.copy(rc);}",
    "{const ws=ug.ws||(ug.ws=m.g.getWorldScale(new THREE.Vector3()).x);for(const l of ug.lights){l.intensity=ug.on?UG_BOUNCE_R*(ug.cp||1)*L*(k.boost>0?1.2:1):0;l.distance=(l.userData.ld||40)*ws;if(rc)l.color.copy(rc);}}/* (patch 77) */")

# the garage: the floor lit, the lights under the car
rep("const ug=gModel.g.userData.ug;if(ug&&ug.on){const rc=ug.rb?rainbowC(performance.now()/1000,0):null;for(const l of ug.lights){l.intensity=.6;if(rc)l.color.copy(rc);}if(rc){if(ug.pl)ug.pl.material.color.copy(rc);if(ug.pl2)ug.pl2.material.color.copy(rc);}}",
    "ugGarage(gModel.g);/* (patch 77) */")
rep("new THREE.MeshStandardMaterial({map:gFloorTex(),roughness:.62,metalness:0,envMapIntensity:.6})", "ugFloorMat(new THREE.MeshStandardMaterial({map:gFloorTex(),roughness:.62,metalness:0,envMapIntensity:.6}))")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patch 77 applied')
