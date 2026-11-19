"""Patch 110 (web v245): a cinematic finish.
The owner: "make the slow mo ending at the end of a race way more cinematic, maybe even throw in another camera angle and a close up of the
driver in the car going by and their name in 3d letters on the ground or in the air and the place they took as well".
Before: 1.25 s at .38 speed, a wide-angle kick, "Finish!", the results 2.4 s later. Now, when the player finishes a race (not a battle,
Sandbox or Last Slice Standing; not while spectating), about 7 s of real time, letterboxed, the HUD faded, any key or tap skips:
  A 0-2.3 s   trackside: a camera low at the road's edge ahead of the kart (on the side of the road the kart is on, 20 off its line, or
              the other side when it is near the edge), fixed; it follows the kart past, zooming in as it nears. Speed .28.
  B 2.3-4.6   the driver: a camera swinging round the driver's head (from ahead to the side) a few metres out, riding with the kart. Speed .4.
  C 4.6-7.2   the sign: the place (1ST gold, 2ND silver, 3RD bronze, others cream) over the player's name, in 3D letters (Bungee,
              extruded, bevelled; godot/assets/fonts, OFL; outlines in data/font3d.json from tools/fin/font3d.py) floating across the
              road ahead where the kart will reach them; each letter pops in. The camera rises behind the kart as it drives under them.
              Speed .4 -> .85.
On line the race runs on the host's clock: no slow motion there, the same shots at full speed (the sign further ahead). The results come
.35 s after the end (their 2.4 s timer waits). The sign stays until the next race. PC: pc98.
Run once, after patch 109: tools/py.cmd tools/mini/patch110.py"""
import json
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'patch 110' not in s, 'already patched'
FONT = json.dumps(json.load(open('D:/crust-rush/source/data/font3d.json')), separators=(',', ':'))


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:90])
    s = s.replace(a, b)


JS = r"""
/* (patch 110) the cinematic finish: three shots, then the results */
const FONT3D=__FONT__;const FIN={on:false,t:0,shot:-1,grp:null,end:7.2,cp:new THREE.Vector3(),lk:new THREE.Vector3(),side:1,sp:0};
function finOrd(n){const v=n%100;return n+(v>10&&v<14?'TH':['TH','ST','ND','RD'][v%10]||'TH');}
const _f3g={};function text3D(str,size,depth,mat){const F=FONT3D,sc=size/F.r,g=new THREE.Group();let x=0;
  for(const ch of String(str).toUpperCase()){const q=F.g[ch]||F.g['?'];if(!q)continue;
    if(q[1]){const key=ch+'|'+size+'|'+depth;let geo=_f3g[key];
      if(!geo){const sp=new THREE.ShapePath(),c=q[1].split(' ');let i=0;const n=()=>+c[i++]*sc;
        while(i<c.length){const o=c[i++];if(o==='m'){const a=n(),b=n();sp.moveTo(a,b);}else if(o==='l'){const a=n(),b=n();sp.lineTo(a,b);}
          else if(o==='q'){const a=n(),b=n(),d=n(),e=n();sp.quadraticCurveTo(a,b,d,e);}else if(o==='b'){const a=n(),b=n(),d=n(),e=n(),f=n(),h=n();sp.bezierCurveTo(a,b,d,e,f,h);}}
        geo=_f3g[key]=new THREE.ExtrudeGeometry(sp.toShapes(false),{depth,curveSegments:5,bevelEnabled:true,bevelThickness:depth*.2,bevelSize:size*.016,bevelSegments:2});geo.computeBoundingBox();}
      const piv=new THREE.Group(),m=new THREE.Mesh(geo,mat);const bx=geo.boundingBox;m.position.set(-(bx.min.x+bx.max.x)/2,0,-depth/2);piv.position.x=x+(bx.min.x+bx.max.x)/2;piv.add(m);m.castShadow=true;g.add(piv);}
    x+=q[0]*sc;}
  for(const c of g.children)c.position.x-=x/2;g.userData.w=x;return g;}
const FIN_COL=[['#ffcf40','#8a5a00'],['#e2e7ef','#4a5260'],['#d98a48','#6a3410'],['#fff4dc','#7a3a10']];
function finMat(c){return new THREE.MeshStandardMaterial({color:c[0],emissive:c[1],emissiveIntensity:.55,metalness:.55,roughness:.28});}
function finAhead(x,y,dist,h){let bi=0,bd=1e18;for(let j=0;j<N;j++){const q=track[j],d=(q.x-x)**2+(q.y-y)**2;if(d<bd){bd=d;bi=j;}}
  const tg=j=>{const a=track[(j-1+N)%N],b=track[(j+1)%N],l=Math.hypot(b.x-a.x,b.y-a.y)||1;return [(b.x-a.x)/l,(b.y-a.y)/l];};
  const t0=tg(bi),dir=t0[0]*Math.cos(h)+t0[1]*Math.sin(h)>=0?1:-1;let j=bi,acc=0;
  while(acc<dist){const k=(j+dir+N)%N;acc+=Math.hypot(track[k].x-track[j].x,track[k].y-track[j].y);j=k;if(j===bi)break;}
  const t=tg(j);return {x:track[j].x,y:track[j].y,tx:t[0]*dir,ty:t[1]*dir,lat:(x-track[bi].x)*-t0[1]+(y-track[bi].y)*t0[0]};}
function finClear(){if(FIN.grp){scene.remove(FIN.grp);FIN.grp=null;}FIN.on=false;finUi(false);}
function finUi(on){let el=document.getElementById('finBars');if(!el){if(!on)return;el=document.createElement('div');el.id='finBars';el.innerHTML='<i></i><i></i><b>Tap or press any key to skip</b>';stage.appendChild(el);
    const st=document.createElement('style');st.textContent='#finBars{position:absolute;inset:0;pointer-events:none;z-index:40}#finBars i{position:absolute;left:0;right:0;height:10.5%;background:#000;transition:transform .45s cubic-bezier(.2,.8,.2,1)}#finBars i:first-child{top:0;transform:translateY(-101%)}#finBars i:nth-child(2){bottom:0;transform:translateY(101%)}#finBars.on i{transform:none}#finBars b{position:absolute;right:18px;bottom:3.2%;font:600 13px var(--body);color:#fff4dcaa;letter-spacing:.06em;opacity:0;transition:opacity .4s .8s}#finBars.on b{opacity:1}#stage.fincine .hud,#stage.fincine .saucefx{opacity:0!important;transition:opacity .35s}';document.head.appendChild(st);}
  el.classList.toggle('on',on);stage.classList.toggle('fincine',on);}
function finStart(){finClear();if((typeof SPEC!=='undefined'&&SPEC.on)||!player||!player.m||!N||BATTLE||SBX||mode==='lss')return;FIN.on=true;FIN.t=0;FIN.shot=-1;finUi(true);}
function finEnd(){if(!FIN.on)return;FIN.on=false;finUi(false);slowT=0;camSnap=true;if(resultsAt>.35)resultsAt=.35;}
function finTS(){const t=FIN.t;return t<2.3?.28:t<4.6?.4:.4+.45*Math.min(1,(t-4.6)/2.6);}
addEventListener('keydown',()=>{if(FIN.on&&FIN.t>.5)finEnd();},true);addEventListener('pointerdown',()=>{if(FIN.on&&FIN.t>.5)finEnd();},true);
const _fh=new THREE.Vector3();
function finCam(dt){const k=player,t=FIN.t,h=k.rma!=null?k.rma:k.ma,fx=Math.cos(h),fy=Math.sin(h),kp=_fh.set(k.rx,(k.rz||0),k.ry),sh=t<2.3?0:t<4.6?1:2,cut=sh!==FIN.shot,ez=x=>x<.5?2*x*x:1-(-2*x+2)**2/2;
  if(cut){FIN.shot=sh;FIN.sp=Math.abs(k.speed||0);FIN.side=Math.random()<.5?1:-1;
    if(sh===0){const a=finAhead(k.rx,k.ry,Math.max(40,FIN.sp*(NET.cfg?.9:.32)),h),nx=-a.ty,ny=a.tx;let lat=a.lat,side=lat>=0?1:-1,cl=lat+side*20;if(Math.abs(cl)>RW*.95)cl=lat-side*20;
      const x=a.x+nx*cl,y=a.y+ny*cl;FIN.cp.set(x,groundAt(x,y)+3.2,y);}
    if(sh===2){const d=clamp(FIN.sp*(NET.cfg?2.1:1.25),70,420),a=finAhead(k.rx,k.ry,d,h),g=new THREE.Group(),pl=Math.max(1,k.place|0),c=FIN_COL[Math.min(pl,4)-1];
      const top=text3D(finOrd(pl),15,4.2,finMat(c)),nm=text3D(netName(),7.2,2.4,finMat(FIN_COL[3]));top.position.y=11.5;nm.position.y=0;
      const sc=Math.min(1,RW*1.7/Math.max(top.userData.w,nm.userData.w,1));g.scale.setScalar(sc);g.add(top,nm);g.position.set(a.x,groundAt(a.x,a.y)+14,a.y);g.rotation.y=Math.atan2(-a.tx,-a.ty);
      g.userData.born=t;g.userData.L=[...top.children,...nm.children];g.userData.L.forEach(l=>l.scale.setScalar(.001));scene.add(g);FIN.grp=g;}}
  if(FIN.grp){const g=FIN.grp,L=g.userData.L;L.forEach((l,i)=>{const u=clamp((t-g.userData.born-i*.05)/.45,0,1),o=u<1?1+Math.sin(u*Math.PI)*.35*(1-u):1;l.scale.setScalar(Math.max(.001,ez(u)*o));l.rotation.y=(1-u)*1.2;});}
  let fov=48;
  if(sh===0){camera.position.copy(FIN.cp);const tg=_fh.set(k.rx,(k.rz||0)+2.6,k.ry);if(cut)FIN.lk.copy(tg);else FIN.lk.lerp(tg,1-Math.exp(-10*dt));camera.up.set(0,1,0);camera.lookAt(FIN.lk);
    const d=camera.position.distanceTo(FIN.lk);fov=clamp(2*Math.atan(15/Math.max(1,d))*180/Math.PI,16,52);}
  else if(sh===1){const hd=new THREE.Vector3();if(k.m.drv)k.m.drv.getWorldPosition(hd);else hd.set(k.rx,(k.rz||0)+4,k.ry);hd.y+=1.4;
    const u=clamp((t-2.3)/2.3,0,1),a=h+FIN.side*(.2+.34*ez(u))*Math.PI,R=(13-2.5*u)*(BODIES[playerBuild.b]&&BODIES[playerBuild.b].sf||1);/* from ahead of the driver round to the side */
    camera.position.set(hd.x+Math.cos(a)*R,Math.max(hd.y+2.4-1.2*u,groundAt(hd.x+Math.cos(a)*R,hd.z+Math.sin(a)*R)+1.5),hd.z+Math.sin(a)*R);camera.up.set(0,1,0);camera.lookAt(hd);fov=34;}
  else{const u=ez(clamp((t-4.6)/2.6,0,1)),g=FIN.grp,bx=k.rx-fx*(24+10*u),by=k.ry-fy*(24+10*u);FIN.cp.set(bx,Math.max((k.rz||0),groundAt(bx,by))+6+14*u,by);
    if(cut)camera.position.copy(FIN.cp);else camera.position.lerp(FIN.cp,1-Math.exp(-8*dt));const tg=_fh.set(k.rx+fx*8,(k.rz||0)+4,k.ry+fy*8);if(g)tg.lerp(new THREE.Vector3(g.position.x,g.position.y+4,g.position.z),.35+.25*u);
    if(cut)FIN.lk.copy(tg);else FIN.lk.lerp(tg,1-Math.exp(-6*dt));camera.up.set(0,1,0);camera.lookAt(FIN.lk);fov=50;}
  if(Math.abs(camera.fov-fov)>.05){camera.fov=cut||sh===0?fov:camera.fov+(fov-camera.fov)*Math.min(1,dt*6);camera.updateProjectionMatrix();}}
""".replace('__FONT__', FONT)

rep("let finPunch=0,slowT=0;function finishPunch(){finPunch=.0001;if(!NET.cfg)slowT=1.25;shake(.5);}",
    "let finPunch=0,slowT=0;function finishPunch(){finPunch=.0001;if(!NET.cfg)slowT=1.25;shake(.5);try{finStart();}catch(e){console.warn('fin',e);}}" + JS)
rep("if(slowT>0){slowT-=dt;const ts=slowT>.5?.38:.38+.62*(1-slowT/.5);dt*=Math.max(.38,Math.min(1,ts));}",
    "if(FIN.on){FIN.t+=dt;if(FIN.t>=FIN.end)finEnd();}/* (patch 110: the cinematic finish runs on real time; its slow motion offline only) */"
    "if(FIN.on){if(!NET.cfg)dt*=finTS();}else if(slowT>0){slowT-=dt;const ts=slowT>.5?.38:.38+.62*(1-slowT/.5);dt*=Math.max(.38,Math.min(1,ts));}")
rep("if(resultsAt>0){resultsAt-=dt;if(resultsAt<=0){", "if(resultsAt>0&&!FIN.on){resultsAt-=dt;if(resultsAt<=0){")
rep("snapSun(camT.rx+Math.cos(cam.a)*80,camT.rg,camT.ry+Math.sin(cam.a)*80);}", "if(FIN.on)try{finCam(dt);}catch(e){console.warn('fin',e);finEnd();}/* (patch 110) */snapSun(camT.rx+Math.cos(cam.a)*80,camT.rg,camT.ry+Math.sin(cam.a)*80);}")
rep("finishCount=0;lapShown=1;resultsAt=0;", "finishCount=0;lapShown=1;resultsAt=0;try{finClear();}catch(e){}")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patch 110 applied')
