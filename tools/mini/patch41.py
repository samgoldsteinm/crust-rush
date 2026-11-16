"""Patch 41 (web v205; Sandbox only, nothing a race reads: online stays 114): the mechanic's shop, built in Blender, and pulling in.
The owner, 2026-11-16, with a video of a car pulling into a mechanic's garage: "watch how the car pulls in the mechanic garage and the
animations. that is what i want for the garage in sandbox. it should be cool like in the video when you pull in"; then "add some texture
to the garage building".
- The building: tools/blender/mechshop.py (toy_mshop_hq, toy_mshopdoor_hq), a real-size 14.6 x 13.1 m workshop shrunk to the old
  footprint (100 x 90 units, SHOP_K units a metre). Concrete floor and apron, painted block walls on a brick plinth, an asphalt roof
  (the stored texture pairs, real size), steel and paint; our own sign and wall logo drawn here. Until the packs arrive the old
  code-built shop stands there, and it is swapped once they do.
- The door rolls up as you drive at it (and down again when you leave), lights on inside. Drive through it and the shop takes over:
  the kart rolls slowly onto the lift bay and stops, the camera cuts to a low shot inside behind the lift and drifts, the kart's name
  slides in, and after a moment (or at a tap or a key) the screen fades into the driver screen as before. Coming back out, the door
  stands open behind you and rolls down once you are away.
Run once: py.cmd tools/mini/patch41.py"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'patch 41' not in s, 'already patched'


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:90])
    s = s.replace(a, b)


# ---- the input: while the shop drives, the shop's controls
rep("const inp=(k.isPlayer&&!k.auto&&!(k.rush>0&&!(k.megaT>0)&&!(k.pestoT>0)))?playerInput():(k.isPlayer&&k.rush>0?rushInput(k,dt):aiInput(k,dt));",
    "const inp=SBX&&k===player&&SB.shopQ&&SB.shopQ.drive?sbShopInp(k):(k.isPlayer&&!k.auto&&!(k.rush>0&&!(k.megaT>0)&&!(k.pestoT>0)))?playerInput():(k.isPlayer&&k.rush>0?rushInput(k,dt):aiInput(k,dt));/* (patch 41: pulling into the mechanic's shop) */")
# ---- the camera: after Sandbox's own
rep("  if(im)im.instanceMatrix.needsUpdate=true;}", "  if(im)im.instanceMatrix.needsUpdate=true;try{sbShopFrame(time);}catch(e){console.warn('shop',e);}/* (patch 41) last: it owns the camera while pulling in */}")

# ---- the shop itself: replaces sbShopBuild / sbShopTick, keeps the rest
a = s.index("function sbShopBuild(){")
b = s.index("function sbShopOpen(){")
old_build = s[a:b]
assert "SB.shopIn=false;}" in old_build and "function sbShopTick(k)" in old_build
fallback = old_build[:old_build.index("function sbShopTick(k)")]
fallback = fallback.replace("function sbShopBuild(){if(!sbShopIn()||!SB.grp)return;", "function sbShopOld(){")
fallback = fallback.replace("SB.grp.add(G);SB.shopG=G;", "SB.grp.add(G);SB.shopG=G;SB.shopPk=false;")
fallback = fallback.replace("const wall=(a,b,c,d)=>SB.shapes.push({t:'box',x0:a,x1:b,z0:c,z1:d,b:0,h:H+2});", "const wall=(a,b,c,d)=>SB.shapes.push({t:'box',x0:a,x1:b,z0:c,z1:d,b:0,h:H+2,shop:1});")
NEW = fallback + r"""/* ---- (patch 41) the Blender-built shop: tools/blender/mechshop.py. The model is a real 14.6 m workshop; SHOP_K game units to the metre
   puts it on the old footprint. Blender's front (-Y) is the game's +z, where the door is. */
const SHOP_K=100/14.6,SHOP_BAY=-.6*SHOP_K/* the lift bay's middle, from the shop's middle (z) */,SHOP_DW=2.6*SHOP_K/* half the door's width */,SHOP_DH=4.4*SHOP_K,SHOP_FL=.12*SHOP_K/* the floor slab */;
function sbShopSign(w,h,draw){const c=cnv(w,h),g=c.getContext('2d');draw(g,w,h);const t=T2(c);t.userData.keepCanvas=true;return new THREE.MeshStandardMaterial({map:t,roughness:.5,metalness:0,envMapIntensity:.5});}
/* a spanner crossed with a pizza slice: our own mark, nobody else's */
function sbShopMark(g,x,y,r){g.save();g.translate(x,y);g.fillStyle='#f2c21b';g.beginPath();g.moveTo(0,-r);g.lineTo(r*.86,r*.5);g.lineTo(-r*.86,r*.5);g.closePath();g.fill();g.fillStyle='#c0392b';for(const [px,py] of [[0,-r*.25],[-r*.3,r*.25],[r*.3,r*.22]]){g.beginPath();g.arc(px,py,r*.13,0,7);g.fill();}
  g.strokeStyle='#d8a24a';g.lineWidth=r*.14;g.beginPath();g.moveTo(-r*.86,r*.5);g.lineTo(r*.86,r*.5);g.stroke();g.rotate(-.75);g.fillStyle='#cfd5db';g.fillRect(-r*1.15,-r*.09,r*2.3,r*.18);for(const e of [-1,1]){g.beginPath();g.arc(e*r*1.15,0,r*.27,0,7);g.fill();}g.fillStyle='#1b1f26';g.fillRect(-r*1.42,-r*.08,r*.3,r*.16);g.fillRect(r*1.12,-r*.08,r*.3,r*.16);g.restore();}
function sbShopMats(){const tx=(k,r,col,t)=>[woodTex(k,r,()=>paint('shop_'+k,col,r)),t];
  return {mconc:tx('concrete',.85,'#8f8c86',260),mblock:tx('gbrick',.9,'#d9d6cf',150),mbrick:tx('brick',.85,'#9a5a44',120),mroof:tx('asphalt',.9,'#55585c',300),
    myel:[paint('shop_yel','#f2c21b',.45),60],mred:[paint('shop_red','#b8261d',.35),60],mblue:[paint('shop_blue','#24508f',.4),60],msteel:[metal('shop_steel','#3a3f45',.5),60],
    mgalv:[metal('shop_galv','#a0a6ac',.42),60],mchrome:[metal('shop_chrome','#d4d7db',.18),60],mrubber:[paint('shop_rubber','#2a2a2b',.9),60],mwood:tx('ash',.55,'#b88a55',90),
    mlamp:[mat('shop_lamp',()=>new THREE.MeshBasicMaterial({color:'#fff8e0',toneMapped:false})),60],mglass:[mat('shop_glass',()=>std({color:'#5f7f8f',roughness:.08,metalness:.2,envMapIntensity:1.2})),60],
    mblack:[paint('shop_black','#16171a',.55),60],mdoor:[metal('shop_door','#b9bec4',.4),40],mpeg:[paint('shop_peg','#c7b08a',.8),60],mgreen:[paint('shop_green','#2f6b3d',.45),60],
    msign:[mat('shop_sign',()=>sbShopSign(1024,202,(g,w,h)=>{g.fillStyle='#1d2b4a';g.fillRect(0,0,w,h);g.fillStyle='#f2c21b';g.fillRect(0,h-14,w,14);g.fillRect(0,0,w,8);sbShopMark(g,105,h/2+6,62);
      g.fillStyle='#fbf3df';g.font='900 86px Arial Black, Arial';g.textBaseline='middle';g.fillText('CRUST RUSH',200,h/2-14);g.fillStyle='#f2c21b';g.font='700 40px Arial';g.fillText('GARAGE  \u00b7  TUNING & REPAIRS',204,h/2+52);})),100],
    mlogo:[mat('shop_logo',()=>sbShopSign(1024,376,(g,w,h)=>{g.fillStyle='#e9e2d0';g.fillRect(0,0,w,h);g.fillStyle='rgba(0,0,0,.06)';for(let i=0;i<60;i++)g.fillRect(Math.random()*w,Math.random()*h,2+Math.random()*30,1+Math.random()*3);
      sbShopMark(g,170,h/2,120);g.fillStyle='#1d2b4a';g.font='italic 900 120px Arial Black, Arial';g.textBaseline='middle';g.fillText('Crust Rush',330,h/2-40);g.fillStyle='#b8261d';g.font='italic 700 58px Arial';g.fillText('Garage \u00b7 est. 2026',340,h/2+70);})),100]};}
function sbShopBuild(){if(!sbShopIn()||!SB.grp)return;SB.shapes=SB.shapes.filter(q=>!q.shop);if(SB.shopG){SB.grp.remove(SB.shopG);SB.shopG=null;}SB.shopDoorG=null;SB.shopLt=null;
  if(!pkReady('mshop')||!pkReady('mshopdoor')){sbShopOld();return;}
  const S=SB_SHOP,K=SHOP_K,sc=K/347,G=new THREE.Group(),Mt=sbShopMats();for(const q in Mt)if(!Mt[q])delete Mt[q];
  const B=pk('mshop',Mt);B.scale.setScalar(sc);B.position.set(S.x,0,S.z);G.add(B);
  const D=pk('mshopdoor',Mt);D.scale.setScalar(sc);const Dg=new THREE.Group();Dg.position.set(S.x,SHOP_FL,S.z+6.42*K);Dg.add(D);G.add(Dg);SB.shopDoorG=Dg;
  /* the light inside: off until the door opens */const L=new THREE.PointLight('#fff1d6',0,150,1.4);L.position.set(S.x,4.6*K,S.z);G.add(L);SB.shopLt=L;
  G.traverse(o=>{if(o.isMesh){o.castShadow=true;o.receiveShadow=true;}});SB.grp.add(G);SB.shopG=G;SB.shopPk=true;
  /* solid: the walls, the door while it is shut, the lift posts; the slab and the apron are floor */
  const x0=S.x-50,x1=S.x+50,z0=S.z-6.55*K,z1=S.z+6.55*K,T=.3*K+.6,H=S.h,box=(a,b,c,d,h,bt)=>SB.shapes.push({t:'box',x0:a,x1:b,z0:c,z1:d,b:bt==null?0:bt,h,shop:1});
  box(x0,x1,z0,z0+T,H);box(x0,x0+T,z0,z1,H);box(x1-T,x1,z0,z1,H);box(x0,S.x-SHOP_DW,z1-T,z1,H);box(S.x+SHOP_DW,x1,z1-T,z1,H);
  const dr={t:'box',x0:S.x-SHOP_DW,x1:S.x+SHOP_DW,z0:z1-T,z1:z1,b:0,h:H,shop:1};SB.shapes.push(dr);SB.shopDr=dr;
  box(x0,x1,z0,z1,SHOP_FL,-1);box(S.x-3.6*K,S.x+3.6*K,z1,z1+4.2*K,.08*K,-1);
  for(const sx of [-1,1])SB.shapes.push({t:'cyl',x:S.x+sx*1.85*K,z:S.z-.6*K,r:.3*K,b:0,h:4*K,shop:1});
  SB.shopIn=false;SB.shopQ=null;SB.shopD=SB.shopD||0;sbShopDoor(SB.shopD);}
/* the door: f 0 shut, 1 open (rolled up into its box) */
function sbShopDoor(f){SB.shopD=f;const g=SB.shopDoorG;if(g){const h=1-.95*f;g.scale.y=h;g.position.y=SHOP_FL+SHOP_DH*(1-h);g.visible=f<.99;}if(SB.shopDr)SB.shopDr.h=f>.8?-1:SB_SHOP.h;if(SB.shopLt)SB.shopLt.intensity=SB.shopQ?1.6:Math.min(1,f*1.4)*1.2;}
/* each step: the door, and the way in */
function sbShopTick(k){if(!sbShopIn())return;const S=SB_SHOP,z1=S.z+6.55*SHOP_K,Q=SB.shopQ;
  if(!SB.shopPk&&pkReady('mshop')&&pkReady('mshopdoor'))sbShopBuild();/* the models arrived after the room was built: swap them in */
  if(!SB.shopPk){/* the old open-fronted playset until then: drive in and the driver screen opens, as before */const inside=k.x>S.x-S.w/2+10&&k.x<S.x+S.w/2-10&&k.y>S.z-S.d/2+6&&k.y<S.z+S.d/2-22&&Math.abs(k.wy||0)<8;
    if(inside&&!SB.shopIn&&!SB.trav&&state==='race'){SB.shopIn=true;sbShopOpen();return;}if(!inside&&k.y>S.z+S.d/2+10)SB.shopIn=false;return;}
  const near=Math.abs(k.x-S.x)<46&&k.y>z1-50&&k.y<z1+95;const want=Q||near?1:0;let f=SB.shopD||0;if(f!==want){f+=(want?1:-1)*STEP/(want?1.1:1.4);f=clamp(f,0,1);sbShopDoor(f);if(want&&f>0&&f<.2&&!SB.shopSnd){SB.shopSnd=1;try{SFX.bump(.25);}catch(e){}}if(!want)SB.shopSnd=0;}
  if(!Q){if(f>.8&&!SB.shopIn&&!SB.trav&&state==='race'&&k.y<z1-4&&k.y>S.z&&Math.abs(k.x-S.x)<SHOP_DW){SB.shopIn=true;SB.shopQ={t:0,drive:true,st:'in'};if(SBA&&SBA.act)sbActEnd('cancel');try{SFX.ready();}catch(e){}}
    if(k.y>z1+20)SB.shopIn=false;return;}
  Q.t+=STEP;const bay=S.z+SHOP_BAY,left=k.y-bay;
  if(Q.st==='in'&&(Math.abs(left)<3||Q.t>7)){Q.st='hold';Q.h=0;}
  if(Q.st==='hold'){k.speed*=.9;if(Math.abs(k.speed)<.5)k.speed=0;Q.h+=STEP;if(Q.h>2.6&&!Q.fade){Q.fade=1;sbShopFade(true);setTimeout(()=>{if(SB.shopQ===Q)sbShopGo();},380);}}}
/* the controls while the shop drives: straight for the bay, slower and slower */
function sbShopInp(k){const S=SB_SHOP,Q=SB.shopQ,bay=S.z+SHOP_BAY,ax=S.x,az=Math.min(k.y-12,bay-8),want=Math.atan2(az-k.y,ax-k.x),left=Math.max(0,k.y-bay);
  const st=Q.st==='in'?clamp(angDiff(want,k.a)*2.4,-1,1):0;return {steer:st,brake:false,nb:false,mul:Q.st==='in'?clamp(.1+left/90,.1,.42):0,use:false,back:false,hold:false,holdSl:1,release:null};}
function sbShopGo(){const Q=SB.shopQ;SB.shopQ=null;sbShopCard(false);sbShopOpen();setTimeout(()=>sbShopFade(false),250);}
/* the black between the shop and the driver screen */
function sbShopFade(on){let el=document.getElementById('sbShopFade');if(!el){el=document.createElement('div');el.id='sbShopFade';el.style.cssText='position:fixed;inset:0;background:#000;opacity:0;pointer-events:none;transition:opacity .35s;z-index:60';document.body.appendChild(el);}el.style.opacity=on?'1':'0';}
/* the kart's name, as it rolls in */
function sbShopCard(on){let el=document.getElementById('sbShopCard');if(!el){el=document.createElement('div');el.id='sbShopCard';
    el.style.cssText='position:fixed;right:6vw;top:44vh;text-align:right;pointer-events:none;z-index:55;opacity:0;transform:translateX(30px);transition:opacity .5s,transform .5s;font-family:inherit;text-shadow:0 2px 10px rgba(0,0,0,.7)';
    el.innerHTML='<div class="n" style="font:800 clamp(22px,4.4vw,46px)/1.05 inherit;color:#fff;letter-spacing:.01em"></div><div class="s" style="font:italic 700 clamp(14px,2.4vw,24px)/1.2 inherit;color:#7fc4ff;margin-top:4px"></div>';document.body.appendChild(el);}
  if(on){const b=BODIES[playerBuild.b]||BODIES[0];el.querySelector('.n').textContent=b.name;el.querySelector('.s').textContent=(player&&player.r?player.r.name+'\u2019s ride':'')+' \u00b7 '+(b.bike?'Bike':'Kart');}
  el.style.opacity=on?'1':'0';el.style.transform=on?'none':'translateX(30px)';}
/* each frame while pulling in: the camera low inside, behind the lift, drifting; the name at 0.8 s; a tap or a key skips */
function sbShopFrame(time){const Q=SB.shopQ;if(!Q||!SBX){if(SB.shopCamOn){SB.shopCamOn=false;camera.fov=SB.shopFov||camera.fov;camera.updateProjectionMatrix();}return;}
  const S=SB_SHOP,K=SHOP_K,k=player;if(!SB.shopCamOn){SB.shopCamOn=true;SB.shopFov=camera.fov;camera.fov=48;camera.updateProjectionMatrix();Q.c0=time;
    const sk=e=>{if(!SB.shopQ||SB.shopQ!==Q||Q.fade)return;if(e.type==='keydown'&&!['Enter',' ','Escape','KeyX','KeyZ','KeyA'].includes(e.key)&&!['Space','Enter','Escape'].includes(e.code))return;Q.fade=1;sbShopFade(true);setTimeout(()=>{if(SB.shopQ===Q)sbShopGo();},380);};
    addEventListener('keydown',sk,{once:false});addEventListener('pointerdown',sk);Q.unhook=()=>{removeEventListener('keydown',sk);removeEventListener('pointerdown',sk);};}
  const u=time-Q.c0;if(u>.8&&!Q.card){Q.card=1;sbShopCard(true);}
  const e=Math.min(1,u/5),ease=e*e*(3-2*e),cx=S.x+(3.4-1.0*ease)*K,cz=S.z-(2.6-.5*ease)*K,cy=(.55+.25*ease)*K;camera.position.set(cx,cy,cz);
  const rx=k.rx!=null?k.rx:k.x,ry=k.ry!=null?k.ry:k.y,rz=(k.rz!=null?k.rz:k.wy)||0;if(!Q.look)Q.look={x:rx,y:rz+2.5,z:ry};Q.look.x+=(rx-Q.look.x)*.08;Q.look.y+=(rz+2.5-Q.look.y)*.08;Q.look.z+=(ry-Q.look.z)*.08;camera.lookAt(Q.look.x,Q.look.y,Q.look.z);
  if(Q.fade&&Q.unhook){Q.unhook();Q.unhook=null;}}
"""
s = s[:a] + NEW + s[b:]
# ---- coming back out: the door stands open behind you
rep("function sbShopPut(k){const S=SB_SHOP;", "function sbShopPut(k){const S=SB_SHOP;SB.shopQ=null;sbShopCard(false);sbShopFade(false);if(SB.shopPk)sbShopDoor(1);")
rep("k.y=k.py=S.z+S.d/2+34;", "k.y=k.py=S.z+S.d/2+(SB.shopPk?40:34);")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patch 41 applied')
