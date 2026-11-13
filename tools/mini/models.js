/* ================= MINIATURE MAYHEM: the furniture and household things, modelled at their real size =================
   Every builder returns a THREE.Group whose origin is on the floor (or on whatever the thing stands on), x to the right,
   z toward the viewer, y up. Sizes are given in centimetres and turned into game units by U (a kart is a 7.5 cm toy car).
   Textures are drawn once on canvases; materials are shared by name so the world merges into few draw calls.
   Each model is checked on its own in /home/claude/mini/view (viewer.html) before it goes into a room. */
const TM=(function(){
const U=3.47,MC={},CC={},TXC={};
const rng=seed=>{let s=Math.floor(seed)%2147483646+1;return ()=>(s=s*48271%2147483647)/2147483647;};
function can(key,w,h,draw){if(!CC[key]){const c=cnv(w,h);draw(c.getContext('2d'),w,h,rng(key.length*977+w*13+h));CC[key]=c;}return CC[key];}
function tex(c,key,lin){const k=key+(lin?'|l':'');if(!TXC[k]){TXC[k]=T2(c,1,1,lin);}return TXC[k];}
function mat(key,make){return MC[key]||(MC[key]=Object.assign(make(),{name:'toy_'+key}));}
const std=o=>new THREE.MeshStandardMaterial(o),phy=o=>new THREE.MeshPhysicalMaterial(o);
/* ---- geometry helpers ---- */
/* texture coordinates in real units: `tile` cm of surface per repeat, taken from whichever way each face points */
function uvw(g,tile,turn){const p=g.attributes.position,n=g.attributes.normal,uv=new Float32Array(p.count*2),s=1/(tile*U);
  for(let i=0;i<p.count;i++){const ax=Math.abs(n.getX(i)),ay=Math.abs(n.getY(i)),az=Math.abs(n.getZ(i));let u,v;if(ay>=ax&&ay>=az){u=p.getX(i);v=p.getZ(i);}else if(ax>=az){u=p.getZ(i);v=p.getY(i);}else{u=p.getX(i);v=p.getY(i);}
    if(turn){const t=u;u=v;v=t;}uv[i*2]=u*s;uv[i*2+1]=v*s;}g.setAttribute('uv',new THREE.BufferAttribute(uv,2));return g;}
/* a slab with rounded corners (seen from above) and softened top and bottom edges; sizes in units, origin at its middle */
function slab(w,h,d,rc,bev,seg){rc=Math.min(rc||0,w/2-.01,d/2-.01);bev=Math.min(bev||0,h/2-.01,rc||1e9);const sh=new THREE.Shape(),x=w/2-bev,z=d/2-bev,r=Math.max(.001,rc-bev);
  sh.moveTo(-x+r,-z);sh.lineTo(x-r,-z);sh.absarc(x-r,-z+r,r,-Math.PI/2,0,false);sh.lineTo(x,z-r);sh.absarc(x-r,z-r,r,0,Math.PI/2,false);sh.lineTo(-x+r,z);sh.absarc(-x+r,z-r,r,Math.PI/2,Math.PI,false);sh.lineTo(-x,-z+r);sh.absarc(-x+r,-z+r,r,Math.PI,Math.PI*1.5,false);
  const g=new THREE.ExtrudeGeometry(sh,{depth:h-2*bev,bevelEnabled:bev>0,bevelThickness:bev,bevelSize:bev,bevelSegments:seg||3,curveSegments:rc>3?8:4});g.rotateX(-Math.PI/2);g.translate(0,-h/2+bev,0);return g;}
/* a soft cushion shape: a box blown out toward a ball by `puff` (0 = box, 1 = ball) */
function blob(w,h,d,puff,seg){const s=seg||10,g=new THREE.BoxGeometry(2,2,2,s,Math.max(2,Math.round(s*.6)),s),p=g.attributes.position;
  for(let i=0;i<p.count;i++){const x=p.getX(i),y=p.getY(i),z=p.getZ(i),sx=x*Math.sqrt(1-y*y/2-z*z/2+y*y*z*z/3),sy=y*Math.sqrt(1-z*z/2-x*x/2+z*z*x*x/3),sz=z*Math.sqrt(1-x*x/2-y*y/2+x*x*y*y/3);
    p.setXYZ(i,(x+(sx-x)*puff)*w/2,(y+(sy-y)*puff)*h/2,(z+(sz-z)*puff)*d/2);}g.computeVertexNormals();return g;}
function add(G,geo,m,x,y,z,rx,ry,rz){const o=new THREE.Mesh(geo,m);o.position.set(x||0,y||0,z||0);if(rx||ry||rz)o.rotation.set(rx||0,ry||0,rz||0);G.add(o);return o;}
function grp(parent,x,y,z,ry){const g=new THREE.Group();g.position.set(x||0,y||0,z||0);if(ry)g.rotation.y=ry;if(parent)parent.add(g);return g;}
const box=(w,h,d)=>new THREE.BoxGeometry(w,h,d),cyl=(r0,r1,h,s)=>new THREE.CylinderGeometry(r0,r1,h,s||20);
/* ---- textures ---- */
function woodCan(key,base,dark,planks,knots){return can('wood_'+key,1024,1024,(g,W,H,r)=>{const B=new THREE.Color(base),D=new THREE.Color(dark),n=planks||1,ph=H/n;
  for(let i=0;i<n;i++){const k=.9+r()*.2,c=B.clone().multiplyScalar(k);g.fillStyle='#'+c.getHexString();g.fillRect(0,i*ph,W,ph);
    const off=r()*W;for(let j=0;j<Math.round(170/n);j++){const y=i*ph+r()*ph,a=.05+r()*.16;g.strokeStyle='rgba('+Math.round(D.r*255)+','+Math.round(D.g*255)+','+Math.round(D.b*255)+','+a+')';g.lineWidth=.6+r()*2.4;g.beginPath();g.moveTo(-10,y);
      const w1=(r()-.5)*ph*.25,w2=(r()-.5)*ph*.25;g.bezierCurveTo(W*.33+off%60,y+w1,W*.66,y+w2,W+10,y+(r()-.5)*6);g.stroke();}
    for(let j=0;j<(knots||0);j++){if(r()>.55)continue;const x=r()*W,y=i*ph+ph*(.2+r()*.6);for(let q=2;q<16;q+=3){g.strokeStyle='rgba('+Math.round(D.r*255)+','+Math.round(D.g*255)+','+Math.round(D.b*255)+',.35)';g.lineWidth=1.4;g.beginPath();g.ellipse(x,y,q*2.4,q*.8,0,0,7);g.stroke();}}
    if(n>1){g.fillStyle='rgba(0,0,0,.42)';g.fillRect(0,i*ph,W,2.2);g.fillStyle='rgba(255,255,255,.07)';g.fillRect(0,i*ph+2.2,W,1.5);const bx=r()*W;g.fillStyle='rgba(0,0,0,.4)';g.fillRect(bx,i*ph,2,ph);}}});}
function woodBump(key,planks){return can('woodb_'+key,512,512,(g,W,H,r)=>{g.fillStyle='#808080';g.fillRect(0,0,W,H);for(let j=0;j<900;j++){const y=r()*H,v=110+r()*40;g.strokeStyle='rgba('+v+','+v+','+v+',.35)';g.lineWidth=.5+r()*1.2;g.beginPath();g.moveTo(0,y);g.lineTo(W,y+(r()-.5)*5);g.stroke();}
  const n=planks||1;if(n>1)for(let i=0;i<n;i++){g.fillStyle='#202020';g.fillRect(0,i*H/n,W,3);}});}
function wood(key,base,dark,o){o=o||{};return mat('wood_'+key,()=>{const c=woodCan(key,base,dark,o.planks,o.knots),t=tex(c,'wood_'+key),nb=tex(heightToNormal(woodBump(key,o.planks),o.bump||1.6),'woodn_'+key,true);
  return std({map:t,normalMap:nb,normalScale:new THREE.Vector2(.5,.5),roughness:o.rough||.5,metalness:0,envMapIntensity:o.env||.5});});}
function weaveCan(key,scale){return can('weave_'+key,256,256,(g,W,H,r)=>{g.fillStyle='#808080';g.fillRect(0,0,W,H);const s=scale||4;for(let y=0;y<H;y+=s)for(let x=0;x<W;x+=s){const v=((x/s+y/s)%2?150:105)+r()*26;g.fillStyle='rgb('+v+','+v+','+v+')';g.fillRect(x,y,s,s);}});}
function fabric(key,color,o){o=o||{};return mat('fab_'+key,()=>{const nb=tex(heightToNormal(weaveCan(o.weave||'a',o.ws||4),o.bump||1.2),'weaven_'+(o.weave||'a')+(o.ws||4)+(o.bump||''),true);
  const c=can('fabc_'+key,256,256,(g,W,H,r)=>{g.fillStyle=color;g.fillRect(0,0,W,H);for(let i=0;i<2600;i++){g.fillStyle='rgba('+(r()<.5?'255,255,255':'0,0,0')+','+(r()*.05)+')';g.fillRect(r()*W,r()*H,1+r()*2,1+r()*2);}});
  return std({map:tex(c,'fabc_'+key),normalMap:nb,normalScale:new THREE.Vector2(o.ns||.6,o.ns||.6),roughness:o.rough||.95,metalness:0,envMapIntensity:.25});});}
const plastic=(key,color,rough)=>mat('pl_'+key,()=>phy({color,roughness:rough==null?.45:rough,metalness:0,clearcoat:.25,clearcoatRoughness:.4,envMapIntensity:.6}));
const metal=(key,color,rough)=>mat('mt_'+key,()=>std({color,roughness:rough==null?.35:rough,metalness:1,envMapIntensity:1}));
const paint=(key,color,rough)=>mat('pt_'+key,()=>std({color,roughness:rough==null?.6:rough,metalness:0,envMapIntensity:.4}));
const glow=(key,color)=>mat('gl_'+key,()=>new THREE.MeshBasicMaterial({color,toneMapped:false}));
const glass=(key,color,op)=>mat('gs_'+key,()=>phy({color:color||'#101418',roughness:.05,metalness:0,transparent:true,opacity:op==null?.35:op,envMapIntensity:1.2,clearcoat:1,clearcoatRoughness:.05,depthWrite:false}));

/* ---- models built in Blender (tools/blender), packed like the game's other props ----
   pk(name,mats) builds a group from the pack toy_<name>_hq: one mesh per material; `mats` maps each material name in the
   model to [game material, tile in cm] (or [across, along] to lay one picture over the whole part). The pack's UVs are real size (metres) and are scaled to the material's tile here,
   so the game's own tiling materials stay sharp close up; the vertex colours carry baked soft shading.
   The packs download after the menu is up: pkReady says whether one has arrived, and every builder keeps its code-built
   model for the time before that. */
const pkReady=name=>{const p=typeof PROP_PACKS!=='undefined'&&PROP_PACKS['toy_'+name+'_hq'];return !!(p&&(p.b||p.d));};
function pk(name,mats){const id='toy_'+name+'_hq',G=grp(),geos=propGeos(id);
  for(const h of PROP_PACKS[id].h){const key=h.n.split('|')[1],q=mats[key];if(!q)continue;const g=geos[h.n];
    if(!g.userData.pkuv){const uv=g.attributes.uv,t=q[1]||50,ku=100/(t[0]||t),kv=100/(t[1]||t);/* a tile of [across,along] cm lays one picture over a part of that size */for(let i=0;i<uv.count;i++)uv.setXY(i,(uv.getX(i)*h.us+h.uo[0])*ku,(uv.getY(i)*h.us+h.uo[1])*kv);g.userData.pkuv=1;}
    add(G,g,mat('pk_'+q[0].name,()=>{const c=q[0].clone();c.vertexColors=true;return c;}));}
  return G;}

/* ============ the desk and what stands on it ============ */
const M={};
/* a gaming desk: 200 x 80 cm walnut top on a black steel frame, 75 cm high */
M.desk=function(o){o=o||{};const W=(o.w||200)*U,D=(o.d||80)*U,H=(o.h||75)*U,G=grp(),top=wood('walnut','#6b4428','#2c1608',{rough:.42,env:.6}),steel=mat('desksteel',()=>std({color:'#17181a',roughness:.55,metalness:.6,envMapIntensity:.6}));
  add(G,uvw(slab(W,3*U,D,2.5*U,.5*U,4),90),top,0,H-1.5*U,0);
  const T=6*U,t=3*U,legH=H-3*U;for(const sx of [-1,1]){const x=sx*(W/2-14*U);/* a frame at each end: two posts, a foot and a rail under the top */
    for(const sz of [-1,1])add(G,slab(T,legH-t,t,.6*U,.3*U,2),steel,x,(legH-t)/2+t*.5,sz*(D/2-9*U));
    add(G,slab(T,t,D-6*U,.8*U,.3*U,2),steel,x,t/2,0);add(G,slab(T,t,D-14*U,.6*U,.3*U,2),steel,x,legH-t/2,0);
    for(const sz of [-1,1])add(G,cyl(2.2*U,2.6*U,1*U,16),plastic('black','#0c0c0d',.6),x,.2*U,sz*(D/2-6*U));}
  add(G,slab(W-34*U,t,t*1.2,.5*U,.2*U,2),steel,0,legH-t/2,-D/2+12*U);/* the rail between the frames */
  /* a cable tray under the back edge */
  add(G,box(W*.55,.4*U,12*U),steel,0,legH-9*U,-D/2+16*U);for(const sx of [-1,1])add(G,box(.4*U,9*U,12*U),steel,sx*W*.275,legH-4.5*U,-D/2+16*U);return G;};
/* a cloth desk mat: 90 x 40 cm, 4 mm thick, with a stitched edge */
M.deskmat=function(){const G=grp(),c=can('deskmat',512,256,(g,W,H,r)=>{g.fillStyle='#15171b';g.fillRect(0,0,W,H);for(let i=0;i<5000;i++){g.fillStyle='rgba(255,255,255,'+r()*.035+')';g.fillRect(r()*W,r()*H,1.5,1.5);}
    g.strokeStyle='#ff6a12';g.lineWidth=3;g.setLineDash([7,4]);g.strokeRect(5,5,W-10,H-10);g.setLineDash([]);g.fillStyle='rgba(255,106,18,.9)';g.font='900 26px Arial';g.fillText('CRUST RUSH',W-196,H-22);}),
    m=mat('deskmat',()=>std({map:tex(c,'deskmat'),roughness:1,metalness:0,envMapIntensity:.15}));const g2=slab(90*U,.4*U,40*U,1.2*U,.12*U,2),p=g2.attributes.position,uv=new Float32Array(p.count*2);
  for(let i=0;i<p.count;i++){uv[i*2]=p.getX(i)/(90*U)+.5;uv[i*2+1]=-p.getZ(i)/(40*U)+.5;}g2.setAttribute('uv',new THREE.BufferAttribute(uv,2));add(G,g2,m,0,.2*U,0);return G;};
/* a picture for a screen: a desktop with a window open, or a racing game */
function screenCan(kind){return can('screen_'+kind,1024,576,(g,W,H,r)=>{if(kind==='game'){const sky=g.createLinearGradient(0,0,0,H*.55);sky.addColorStop(0,'#2a5cc8');sky.addColorStop(1,'#9ad0ff');g.fillStyle=sky;g.fillRect(0,0,W,H);
      g.fillStyle='#3d9a45';g.fillRect(0,H*.5,W,H*.5);g.fillStyle='#5a5f66';g.beginPath();g.moveTo(W*.42,H*.5);g.lineTo(W*.58,H*.5);g.lineTo(W*.95,H);g.lineTo(W*.05,H);g.fill();g.fillStyle='#fff';for(let i=0;i<6;i++){const t=i/6,y=H*(.52+t*t*.5),w=4+t*t*22;g.fillRect(W/2-w/2,y,w,10+t*30);}
      g.fillStyle='#e0452c';g.fillRect(W*.44,H*.74,W*.12,H*.1);g.fillStyle='#1a1a1a';g.fillRect(W*.43,H*.82,W*.04,H*.05);g.fillRect(W*.53,H*.82,W*.04,H*.05);g.fillStyle='rgba(0,0,0,.55)';g.fillRect(20,20,180,70);g.fillStyle='#ffd24a';g.font='900 44px Arial';g.fillText('1st',36,72);g.fillStyle='#fff';g.font='700 26px Arial';g.fillText('LAP 2/3',W-170,54);}
    else{const bg=g.createLinearGradient(0,0,W,H);bg.addColorStop(0,'#1b1040');bg.addColorStop(.5,'#3a2a8a');bg.addColorStop(1,'#d8496a');g.fillStyle=bg;g.fillRect(0,0,W,H);for(let i=0;i<5;i++){g.fillStyle='rgba(255,255,255,'+(.04+i*.012)+')';g.beginPath();g.ellipse(W*(.2+i*.17),H*(.9-i*.05),W*.5,H*.35,-.3,0,7);g.fill();}
      g.fillStyle='#f4f5f7';g.fillRect(W*.1,H*.12,W*.5,H*.62);g.fillStyle='#2b6fd8';g.fillRect(W*.1,H*.12,W*.5,26);g.fillStyle='#c9ced6';for(let i=0;i<9;i++)g.fillRect(W*.12,H*.2+i*30,W*(.2+r()*.24),12);g.fillStyle='#1e2430';g.fillRect(W*.64,H*.2,W*.28,H*.42);g.fillStyle='#39d98a';for(let i=0;i<8;i++)g.fillRect(W*.655,H*.23+i*26,W*(.08+r()*.16),9);
      g.fillStyle='rgba(12,14,20,.86)';g.fillRect(0,H-34,W,34);for(let i=0;i<9;i++){g.fillStyle=['#ff6a12','#39d98a','#4aa8ff','#ffd24a','#d86bff'][i%5];g.fillRect(W*.36+i*34,H-27,22,20);}}});}
/* a 27 inch monitor: 61.4 x 36.6 cm panel, thin bezels, on its stand (or on an arm from the back of the desk with arm:true) */
M.monitor=function(o){o=o||{};const G=grp(),pw=61.4*U,ph=36.6*U,dark=plastic('monblk','#101113',.5),lift=(o.lift||(o.arm?16:11))*U,cy=lift+ph/2,sc=screenCan(o.screen||'desk');
  const scr=mat('screen_'+(o.screen||'desk'),()=>new THREE.MeshBasicMaterial({map:tex(sc,'screen_'+(o.screen||'desk')),toneMapped:false,color:'#c9c9c9'}));
  const P=grp(G,0,cy,0);P.rotation.x=-.07;add(P,slab(pw,1.3*U,ph,.6*U,.25*U,2),dark,0,0,0,Math.PI/2);add(P,new THREE.PlaneGeometry(pw-1.6*U,ph-1.8*U),scr,0,.1*U,.67*U);
  add(P,box(pw-1.2*U,.5*U,.2*U),dark,0,-ph/2+.5*U,.7*U);add(P,slab(34*U,3*U,22*U,3*U,1.2*U,3),dark,0,0,-1.9*U,Math.PI/2);/* the bulge on the back with the electronics */
  add(P,box(.5*U,.25*U,.1*U),glow('monled','#7fd0ff'),pw/2-3*U,-ph/2+.5*U,.82*U);
  if(o.arm){const al=metal('armalu','#b9bcc2',.35);/* a gas-spring arm clamped to the back edge of the desk */
    add(G,cyl(1.7*U,1.7*U,cy-2*U,18),al,0,(cy-2*U)/2,-9*U);add(G,slab(9*U,1.6*U,11*U,1*U,.3*U,2),al,0,.8*U,-9*U);add(G,slab(5*U,3*U,3*U,.6*U,.3*U,2),al,0,cy-1*U,-6*U);add(G,slab(11*U,1*U,11*U,.8*U,.25*U,2),dark,0,cy,-3.4*U,Math.PI/2);}
  else{add(G,slab(5.5*U,cy+2*U,2.2*U,.8*U,.4*U,3),dark,0,(cy+2*U)/2,-5*U,-.09);add(G,slab(27*U,1.3*U,21*U,3*U,.45*U,3),dark,0,.65*U,-2*U);add(G,slab(10*U,1*U,10*U,.8*U,.25*U,2),dark,0,cy,-3.2*U,Math.PI/2);}
  return G;};
/* a tenkeyless mechanical keyboard: 36 x 13.5 cm, 87 separate keycaps over a lit plate */
M.keyboard=function(){const G=grp(),KU=1.905*U,body=plastic('kbcase','#1b1c20',.5),W=36*U,D=13.5*U,x0c=-18.1*KU/2+16.85*KU,z0c=-D/2+1.55*U+3.55*KU+.35*U;
  const tilt=grp(G,0,0,0);tilt.rotation.x=.07;tilt.position.y=1.5*U;add(tilt,slab(W,2.2*U,D,1.1*U,.5*U,3),body,0,0,0);
  const pc=can('kbplate',256,64,(g,w,h)=>{const gr=g.createLinearGradient(0,0,w,0);['#ff2d55','#ff9a1f','#ffe14d','#39d98a','#4aa8ff','#b56bff','#ff2d55'].forEach((c,i)=>gr.addColorStop(i/6,c));g.fillStyle=gr;g.fillRect(0,0,w,h);});
  add(tilt,new THREE.PlaneGeometry(W-1.6*U,D-1.6*U),mat('kbplate',()=>new THREE.MeshBasicMaterial({map:tex(pc,'kbplate'),toneMapped:false,color:'#4a4a4a'})),0,1.12*U,0,-Math.PI/2);add(tilt,box(3.2*KU,.35*U,2.05*KU),body,x0c,1.2*U,z0c);
  /* one keycap: a tapered cap with a softened top edge, 1.8 cm at the foot and 1.35 cm on top, 0.9 cm tall */
  const kc=(function(){const b=.9*KU/2,t=.66*KU/2,t2=.6*KU/2,h=.86*U,h2=.95*U,P=[],quad=(a,b2,c,d)=>P.push(...a,...b2,...c,...a,...c,...d);const ring=(s,y,sz)=>[[-s,y,-(sz||s)],[s,y,-(sz||s)],[s,y,(sz||s)],[-s,y,(sz||s)]];const r0=ring(b,0),r1=ring(t,h),r2=ring(t2,h2);
    for(let i=0;i<4;i++){const j=(i+1)%4;quad(r0[j],r0[i],r1[i],r1[j]);quad(r1[j],r1[i],r2[i],r2[j]);}quad(r2[3],r2[2],r2[1],r2[0]);const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(P,3));g.computeVertexNormals();return g;})();
  const rows=[[1,-1,1,1,1,1,-.5,1,1,1,1,-.5,1,1,1,1,-.25,1,1,1],[1,1,1,1,1,1,1,1,1,1,1,1,1,2,-.25,1,1,1],[1.5,1,1,1,1,1,1,1,1,1,1,1,1,1.5,-.25,1,1,1],[1.75,1,1,1,1,1,1,1,1,1,1,1,2.25],[2.25,1,1,1,1,1,1,1,1,1,1,2.75,-1.25,1],[1.25,1,1.25,6.25,1.25,1,1,1.25,-.25,1,1,1]];
  const caps=[],accent=[],x0=-18.1*KU/2,z0=-D/2+1.55*U;rows.forEach((row,ri)=>{let x=x0;const z=z0+ri*KU+(ri>0?.35*U:0);row.forEach((w,ci)=>{if(w<0){x+=-w*KU;return;}const it={x:x+w*KU/2,z,w};x+=w*KU;((ri===0&&ci===0)||(ri===3&&ci===12)||(ri===5&&ci===3)?accent:caps).push(it);});});
  const m4=new THREE.Matrix4(),mk=(list,m)=>{const im=new THREE.InstancedMesh(kc,m,list.length);list.forEach((k,i)=>{m4.makeScale((k.w*KU-.1*KU)/(.9*KU),1,1);m4.setPosition(k.x,1.15*U,k.z);im.setMatrixAt(i,m4);});tilt.add(im);return im;};
  mk(caps,plastic('kbcap','#2a2c31',.62));mk(accent,plastic('kbcap2','#ff6a12',.55));
  for(const sx of [-1,1])add(G,box(3*U,.5*U,1.2*U),plastic('black','#0c0c0d',.6),sx*14*U,.25*U,-D/2+1.5*U);return G;};
/* a gaming mouse: 12.5 x 6.6 x 4 cm */
M.mouse=function(){const G=grp(),sh=plastic('mouse','#17181b',.48),g=blob(6.6*U,4*U,12.5*U,.82,14),p=g.attributes.position;
  for(let i=0;i<p.count;i++){const x=p.getX(i),y=p.getY(i),z=p.getZ(i),t=z/(6.25*U);/* flat underneath, highest behind the middle, narrower at the front */p.setXYZ(i,x*(1-.12*t)*(y<0?1:1),y<0?Math.max(y,-.9*U)*.5:y*(1-.32*Math.max(0,-t)-.12*Math.max(0,t)),z);}
  g.computeVertexNormals();add(G,g,sh,0,1.35*U,0);const wh=add(G,cyl(1.0*U,1.0*U,.7*U,18),plastic('black','#0c0c0d',.8),0,2.45*U,-3.1*U);wh.rotation.z=Math.PI/2;add(G,box(.1*U,.12*U,4.4*U),plastic('black','#0c0c0d',.6),0,2.92*U,-4.3*U,.34);
  add(G,box(5.6*U,.18*U,.18*U),glow('rgb','#39d98a'),0,.95*U,5.7*U);for(const z of [-.4,1.3])add(G,slab(.4*U,.7*U,1.4*U,.2*U,.1*U,2),plastic('black','#0c0c0d',.6),-3.25*U,1.9*U,z*U);return G;};
/* a fan: a ring of light round a hub and blades, r in units */
function fan(G,r,x,y,z,rx,ry,col){const F=grp(G,x,y,z);F.rotation.set(rx||0,ry||0,0);add(F,new THREE.TorusGeometry(r*.93,r*.07,8,36),glow('fan'+col,col));add(F,cyl(r*.24,r*.24,r*.12,16),plastic('black','#0c0c0d',.6),0,0,0,Math.PI/2);
  const bl=mat('fanblade',()=>phy({color:'#22252b',roughness:.35,transparent:true,opacity:.86,side:THREE.DoubleSide,clearcoat:.4}));for(let i=0;i<9;i++){const b=add(F,new THREE.PlaneGeometry(r*.62,r*.3),bl,Math.cos(i/9*6.283)*r*.55,Math.sin(i/9*6.283)*r*.55,0);b.rotation.set(.45,0,i/9*6.283);}
  add(F,new THREE.TorusGeometry(r*1.02,r*.06,6,4),plastic('black','#0c0c0d',.6)).rotation.z=Math.PI/4;return F;}
/* a gaming PC: a 21 x 46 x 45 cm tower with a glass side, three lit fans in front, and the parts inside */
M.pc=function(){const G=grp(),W=21*U,H=46*U,D=45*U,blk=mat('pccase',()=>std({color:'#111214',roughness:.5,metalness:.55,envMapIntensity:.6})),t=.6*U;
  add(G,slab(W,t*2,D,.8*U,.3*U,2),blk,0,H-t,0);add(G,slab(W,t*2,D,.8*U,.3*U,2),blk,0,2.2*U,0);add(G,box(t,H-3*U,D-.4*U),blk,W/2-t/2,H/2+.4*U,0);add(G,box(W-.4*U,H-3*U,t),blk,0,H/2+.4*U,-D/2+t/2);
  for(const sx of [-1,1])for(const sz of [-1,1])add(G,cyl(1.2*U,1.4*U,1.6*U,14),plastic('black','#0c0c0d',.6),sx*(W/2-2.5*U),.8*U,sz*(D/2-4*U));
  add(G,box(.25*U,H-4.4*U,D-2*U),glass('pcglass','#0a0e14',.3),-W/2+.2*U,H/2+.4*U,0);/* the glass side */
  /* front: a fine mesh with three 12 cm fans behind it */
  const mc=can('pcmesh',128,128,(g,w,h)=>{g.fillStyle='#0b0c0e';g.fillRect(0,0,w,h);g.fillStyle='#000';for(let y=0;y<h;y+=8)for(let x=(y/8%2)*4;x<w;x+=8){g.beginPath();g.arc(x+2,y+2,2.3,0,7);g.fill();}});const mt=T2(mc,6,14);
  add(G,new THREE.PlaneGeometry(W-1.6*U,H-5*U),mat('pcmesh',()=>std({map:mt,alphaMap:null,roughness:.6,metalness:.6,transparent:true,opacity:.55,depthWrite:false})),0,H/2+.4*U,D/2-.1*U);
  for(let i=0;i<3;i++)fan(G,5.9*U,0,7.5*U+i*13*U+2*U,D/2-2.2*U,0,0,['#ff2d95','#b56bff','#4aa8ff'][i]);
  /* inside: the board, the cooler, the graphics card, memory and the power-supply cover */
  const pcb=can('pcb',256,256,(g,w,h,r)=>{g.fillStyle='#0f1512';g.fillRect(0,0,w,h);for(let i=0;i<70;i++){g.strokeStyle='rgba(60,120,90,'+(.2+r()*.3)+')';g.lineWidth=1;const x=r()*w,y=r()*h;g.beginPath();g.moveTo(x,y);g.lineTo(x+(r()-.5)*90,y);g.lineTo(x+(r()-.5)*90,y+(r()-.5)*90);g.stroke();}for(let i=0;i<26;i++){g.fillStyle=r()<.5?'#1c1e22':'#2a2d33';g.fillRect(r()*w,r()*h,8+r()*22,6+r()*16);}});
  add(G,new THREE.PlaneGeometry(D-9*U,H-14*U),mat('pcb',()=>std({map:tex(pcb,'pcb'),roughness:.6,metalness:.2})),W/2-t-.3*U,H/2+4*U,-1*U,0,-Math.PI/2);
  add(G,box(W-2*U,9.5*U,D-1.5*U),blk,.3*U,6.8*U,0);/* power-supply cover */
  const gp=grp(G,-.5*U,19*U,-2*U);add(gp,slab(13*U,5*U,30*U,.8*U,.4*U,2),plastic('gpu','#1a1c20',.4),0,0,0);add(gp,box(.3*U,.6*U,26*U),glow('rgbp','#ff2d95'),-6.6*U,1.6*U,0);for(const z of [-8,8])fan(gp,4.6*U,0,-2.6*U,z*U,Math.PI/2,0,'#39d98a');
  const cl=grp(G,2*U,32*U,-6*U);add(cl,box(9*U,12*U,6*U),metal('fins','#9aa0a8',.4),0,0,0);fan(cl,5.4*U,-.2*U,0,3.4*U,0,0,'#4aa8ff');
  for(let i=0;i<4;i++){add(G,box(.7*U,13*U,.6*U),plastic('ram','#15161a',.4),4.5*U,32*U,4*U+i*1.5*U);add(G,box(.8*U,.8*U,.62*U),glow('rgbr'+i,['#ff2d95','#b56bff','#4aa8ff','#39d98a'][i]),4.5*U,38.9*U,4*U+i*1.5*U);}
  fan(G,5.6*U,1*U,33*U,-D/2+1.8*U,0,0,'#b56bff');
  /* top: a vent grille and the power button */
  add(G,new THREE.PlaneGeometry(W-4*U,D-12*U),mat('pcmesh2',()=>std({map:T2(mc,5,12),roughness:.6,metalness:.6})),0,H+.05*U,-2*U,-Math.PI/2);add(G,cyl(.9*U,.9*U,.3*U,18),glow('pwr','#e8f4ff'),5*U,H+.1*U,D/2-4*U);return G;};
/* ============ the bed ============ */
/* cloth laid over a box: a grid across the top that falls down the sides, with soft folds; w,d the top, drop how far it hangs */
function drape(w,d,drop,o){o=o||{};const nx=o.nx||34,nz=o.nz||40,r=rng(o.seed||7),P=[],I=[],UV=[],tw=w+2*drop,td=d+(o.foot===false?0:drop),ph=[r()*6,r()*6,r()*6,r()*6];
  for(let j=0;j<=nz;j++)for(let i=0;i<=nx;i++){const u=i/nx,v=j/nz,sx=(u-.5)*tw,sz=v*td;let x=sx,y=0,z=sz;const ex=Math.abs(sx)-w/2,ez=sz-d;
    /* past the edge the cloth turns down; it bellies out a little and its hem waves */
    if(ex>0){const t=ex/drop;x=Math.sign(sx)*(w/2+Math.sin(t*1.5)*drop*.18+Math.sin(sz*.03+ph[0])*drop*.05*t);y=-ex+ (1-Math.cos(t*1.5))*drop*.04;}
    if(ez>0){const t=ez/drop;z=d+Math.sin(t*1.5)*drop*.16+Math.sin(sx*.035+ph[1])*drop*.05*t;y=Math.min(y,-ez);}
    const fold=(Math.sin(sx*.021+sz*.012+ph[2])*.5+Math.sin(sx*.008-sz*.027+ph[3])*.5+Math.sin(sz*.05+sx*.031)*.25)*(o.fold==null?1.6:o.fold)*U;
    P.push(x,y+(ex>0||ez>0?fold*.35:fold+(o.puff||0)*U*(1-Math.pow(Math.abs(u-.5)*2,6))),z);UV.push(sx/(60*U),sz/(60*U));}
  for(let j=0;j<nz;j++)for(let i=0;i<nx;i++){const a=j*(nx+1)+i,b=a+1,c=a+nx+1,e=c+1;I.push(a,c,b,b,c,e);}
  const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(P,3));g.setAttribute('uv',new THREE.Float32BufferAttribute(UV,2));g.setIndex(I);g.computeVertexNormals();return g;}
/* a pillow: 70 x 45 cm, plump in the middle and pinched at the seams */
function pillowGeo(w,d,h){const g=blob(w,h,d,.72,14),p=g.attributes.position;for(let i=0;i<p.count;i++){const x=p.getX(i)/(w/2),z=p.getZ(i)/(d/2),e=Math.max(Math.abs(x),Math.abs(z)),k=1-.72*Math.pow(e,5);p.setY(i,p.getY(i)*Math.max(.12,k));}g.computeVertexNormals();return uvw(g,50);}
/* a queen bed: 152 x 203 cm mattress on a wooden frame with legs (28 cm clear underneath), a padded headboard, duvet and pillows.
   The head is at -z. */
M.bed=function(o){o=o||{};
  /* the Blender-built bed (tools/blender/bed.py): bedding dropped on as cloth, pillows blown up from flat cases. Same size, same clearance underneath */
  if(pkReady('bed'))return pk('bed',{oak:[wood('oak','#b98a58','#5a3a1c',{rough:.5}),80],slats:[paint('slats','#8a6a48',.8),80],linen:[fabric('linen','#b9b2a4',{ws:3,ns:.8}),40],sheet:[fabric('sheet','#f2efe8',{ws:2,ns:.35,rough:.9}),60],
    duvet:[fabric('duvet',o.duvet||'#3d5a80',{ws:4,ns:.9}),50],duvet2:[fabric('duvet2','#e8e2d6',{ws:4,ns:.8}),50],pillow:[fabric('pillow','#fbfaf6',{ws:2,ns:.4,rough:.9}),45],cushion:[fabric('cushion','#e07a3a',{ws:5,ns:1}),30],throw:[fabric('throw','#d9a441',{ws:6,ns:1.2}),35]});
  const G=grp(),W=152*U,L=203*U,leg=28*U,rail=9*U,mh=24*U,oak=wood('oak','#b98a58','#5a3a1c',{rough:.5}),top=leg+rail;
  for(const sx of [-1,1])for(const sz of [-1,1]){const lg=add(G,cyl(3.2*U,2.2*U,leg,14),oak,sx*(W/2-.5*U),leg/2,sz*(L/2-5*U));lg.userData.leg=1;}
  for(const sx of [-1,1])add(G,uvw(slab(3.2*U,rail+6*U,L+4*U,.8*U,.4*U,2),80,true),oak,sx*(W/2+1.2*U),leg+(rail+6*U)/2-1*U,0);
  add(G,uvw(slab(W+5.6*U,rail+6*U,3.2*U,.8*U,.4*U,2),80),oak,0,leg+(rail+6*U)/2-1*U,L/2+1.2*U);add(G,box(W,2*U,L),paint('slats','#8a6a48',.8),0,leg+rail-1*U,0);
  /* headboard: an oak frame holding three padded panels */
  const hb=grp(G,0,0,-L/2-3.4*U);add(hb,uvw(slab(W+8*U,112*U,4*U,1.2*U,.5*U,3),80),oak,0,56*U,0);const lin=fabric('linen','#b9b2a4',{ws:3,ns:.8});for(let i=0;i<3;i++)add(hb,uvw(blob(W/3-2*U,58*U,7*U,.32,10),40),lin,(i-1)*(W/3),78*U,3.2*U);
  /* mattress and fitted sheet */
  add(G,uvw(slab(W,mh,L,7*U,3.2*U,5),60),fabric('sheet','#f2efe8',{ws:2,ns:.35,rough:.9}),0,top+mh/2,0);
  /* the duvet: over the lower two thirds and hanging down both sides and the foot, turned back near the pillows */
  const dv=fabric('duvet',o.duvet||'#3d5a80',{ws:4,ns:.9}),dg=drape(W+4*U,L*.72,26*U,{seed:5,puff:3.5,fold:1.7});add(G,dg,dv,0,top+mh+1.2*U,-L/2+L*.28).material.side=THREE.DoubleSide;
  add(G,uvw(blob(W+10*U,9*U,26*U,.55,12),50),fabric('duvet2','#e8e2d6',{ws:4,ns:.8}),0,top+mh+4.5*U,-L/2+L*.28+6*U);/* the turned-back band, lining side up */
  const pg=pillowGeo(70*U,45*U,17*U),pw=fabric('pillow','#fbfaf6',{ws:2,ns:.4,rough:.9});add(G,pg,pw,-38*U,top+mh+7*U,-L/2+27*U,.12,.06,0);add(G,pg,pw,38*U,top+mh+7*U,-L/2+26*U,.1,-.05,0);
  add(G,pillowGeo(46*U,46*U,15*U),fabric('cushion','#e07a3a',{ws:5,ns:1}),6*U,top+mh+10*U,-L/2+52*U,.5,.3,0);
  /* a throw folded across the foot */
  add(G,drape(W+2*U,46*U,20*U,{seed:9,nx:30,nz:14,fold:1.1,puff:1.5,foot:false}),fabric('throw','#d9a441',{ws:6,ns:1.2}),0,top+mh+5.2*U,L/2-62*U).material.side=THREE.DoubleSide;return G;};
/* ============ the gaming chair ============ */
M.chair=function(o){o=o||{};const G=grp(),blk=mat('pu',()=>std({color:'#16171a',roughness:.48,metalness:0,envMapIntensity:.5,normalMap:tex(heightToNormal(weaveCan('pu',2),.5),'pun',true),normalScale:new THREE.Vector2(.25,.25)})),acc=mat('pu2',()=>std({color:o.accent||'#ff6a12',roughness:.5,envMapIntensity:.5})),nyl=plastic('nylon','#121214',.55),stl=metal('chrome','#c9ccd2',.18);
  /* five-star base with twin-wheel casters */
  for(let i=0;i<5;i++){const a=i/5*6.283+.3,arm=grp(G,0,0,0,a);add(arm,slab(31*U,3.2*U,5*U,1.2*U,.8*U,3),nyl,16*U,8.6*U,0,0,0,-.11);const cx=31*U;add(arm,cyl(1*U,1*U,4*U,10),nyl,cx,6*U,0);for(const s of [-1,1]){const w=add(arm,cyl(2.6*U,2.6*U,1.8*U,18),plastic('caster','#0b0b0c',.35),cx,2.6*U,s*1.6*U);w.rotation.x=Math.PI/2;}add(arm,box(4.6*U,2.4*U,5.4*U),nyl,cx,4.2*U,0);}
  add(G,cyl(5*U,6.5*U,5*U,20),nyl,0,10.5*U,0);add(G,cyl(2.6*U,2.6*U,22*U,18),stl,0,23*U,0);add(G,cyl(3.6*U,4.2*U,9*U,18),nyl,0,17*U,0);
  const top=grp(G,0,34*U,0,o.turn||0);add(top,slab(22*U,3*U,26*U,2*U,.8*U,2),nyl,0,0,0);add(top,cyl(.8*U,.8*U,14*U,10),nyl,15*U,-.5*U,4*U,0,0,Math.PI/2);
  /* seat: a cushion with raised side bolsters and a waterfall front */
  const seat=grp(top,0,3*U,2*U);add(seat,uvw(blob(40*U,11*U,50*U,.42,12),30),blk,0,5*U,0);for(const s of [-1,1])add(seat,uvw(blob(9*U,10*U,48*U,.6,10),30),s>0?acc:acc,s*23*U,7.5*U,0,0,0,-s*.25);
  /* back: reclined a little, with shoulder wings, a lumbar cushion and a head pillow */
  const back=grp(top,0,12*U,-22*U);back.rotation.x=-.16;add(back,uvw(blob(38*U,80*U,10*U,.4,12),30),blk,0,42*U,0);for(const s of [-1,1]){add(back,uvw(blob(9*U,52*U,13*U,.6,10),30),acc,s*21*U,30*U,2.5*U,0,-s*.3,0);add(back,uvw(blob(11*U,28*U,12*U,.6,10),30),blk,s*20*U,68*U,2*U,0,-s*.25,s*.12);}
  add(back,uvw(blob(30*U,13*U,7*U,.7,10),30),acc,0,76*U,6*U);add(back,uvw(blob(30*U,16*U,8*U,.7,10),30),blk,0,22*U,7*U);add(back,slab(34*U,70*U,3*U,3*U,1*U,3),nyl,0,40*U,-5.6*U);
  /* armrests */
  for(const s of [-1,1]){add(top,slab(4*U,22*U,6*U,1*U,.5*U,2),nyl,s*27*U,13*U,0);add(top,slab(8*U,3*U,26*U,2*U,1*U,3),nyl,s*27*U,25.5*U,2*U);add(top,box(9*U,2*U,4*U),nyl,s*23*U,3*U,0);}return G;};
/* ============ storage ============ */
/* a low dresser: 120 x 45 cm, 45 cm high on short legs, six drawers with bar handles */
M.dresser=function(){const G=grp(),W=120*U,D=45*U,H=45*U,leg=9*U,body=paint('dresser','#eceae4',.55),oak=wood('oak','#b98a58','#5a3a1c',{rough:.5}),hd=metal('brass','#b08a4a',.3);
  add(G,slab(W,H-leg-3*U,D,1*U,.4*U,3),body,0,leg+(H-leg-3*U)/2,0);add(G,uvw(slab(W+3*U,3*U,D+2*U,1.2*U,.5*U,3),80),oak,0,H-1.5*U,0);
  for(const sx of [-1,1])for(const sz of [-1,1])add(G,cyl(2*U,1.3*U,leg,12),oak,sx*(W/2-6*U),leg/2,sz*(D/2-5*U));
  const dw=W/2-2.4*U,dh=(H-leg-3*U)/3-1*U;for(let c=0;c<2;c++)for(let r=0;r<3;r++){const x=(c-.5)*(W/2-.6*U),y=leg+.9*U+dh/2+r*(dh+.9*U);add(G,slab(dw,1.8*U,dh,.7*U,.35*U,3),body,x,y,D/2+.4*U,Math.PI/2);
    add(G,cyl(.55*U,.55*U,14*U,10),hd,x,y+dh*.12,D/2+3.2*U,0,0,Math.PI/2);for(const s of [-1,1])add(G,cyl(.45*U,.45*U,2*U,8),hd,x+s*6*U,y+dh*.12,D/2+2.2*U,Math.PI/2);}return G;};
/* a stack of books: n books of different sizes lying on each other, each with a cover, a spine and a block of pages */
M.books=function(n,seed){const G=grp(),r=rng(seed||3),cols=['#b8322a','#27527a','#e0a020','#2f6b4a','#5a3d7a','#d8d2c4','#1d1f24','#c9632b'];let y=0;const pages=paint('pages','#efe9da',.9);
  for(let i=0;i<(n||5);i++){const w=(15+r()*8)*U,d=(21+r()*7)*U,h=(1.6+r()*3)*U,c=cols[Math.floor(r()*cols.length)],B=grp(G,(r()-.5)*2.5*U,y,(r()-.5)*2.5*U,(r()-.5)*.35),cov=paint('book'+c,c,.6);
    add(B,box(w-.5*U,h-.5*U,d-.5*U),pages,.2*U,h/2,0);add(B,slab(w,.28*U,d,.25*U,.1*U,2),cov,0,.14*U,0);add(B,slab(w,.28*U,d,.25*U,.1*U,2),cov,0,h-.14*U,0);add(B,box(.3*U,h,d),cov,-w/2+.15*U,h/2,0);
    add(B,box(.32*U,h*.5,d*.16),paint('bookband','#f1e3c0',.6),-w/2+.15*U,h/2,d*.2);y+=h;}G.userData.top=y;return G;};
/* a floor lamp: a weighted base, a slim pole 150 cm tall and a lit drum shade */
M.floorlamp=function(){const G=grp(),br=metal('lampbrass','#8c6a3c',.32),sh=mat('shade',()=>std({color:'#f3e6cc',emissive:'#ffcf8a',emissiveIntensity:.55,roughness:.9,side:THREE.DoubleSide,transparent:true,opacity:.96}));
  add(G,cyl(13*U,14*U,2.2*U,36),br,0,1.1*U,0);add(G,cyl(1.1*U,1.1*U,148*U,14),br,0,75*U,0);add(G,new THREE.CylinderGeometry(17*U,20*U,26*U,36,1,true),sh,0,146*U,0);
  add(G,new THREE.TorusGeometry(17*U,.25*U,6,36),br,0,159*U,0,Math.PI/2);add(G,new THREE.TorusGeometry(20*U,.25*U,6,36),br,0,133*U,0,Math.PI/2);add(G,new THREE.SphereGeometry(4*U,14,10),glow('bulb','#fff1cf'),0,144*U,0);return G;};
/* a rug: 160 x 230 cm with a woven pattern and a bound edge */
M.rug=function(o){o=o||{};const G=grp(),W=(o.w||160)*U,L=(o.l||230)*U,c=can('rug',512,736,(g,w,h,r)=>{g.fillStyle='#d9cfbf';g.fillRect(0,0,w,h);g.strokeStyle='#27425e';g.lineWidth=14;g.strokeRect(26,26,w-52,h-52);g.strokeStyle='#c8643a';g.lineWidth=5;g.strokeRect(46,46,w-92,h-92);
    for(let y=0;y<7;y++)for(let x=0;x<5;x++){const cx=86+x*85,cy=96+y*90;g.strokeStyle=(x+y)%2?'#27425e':'#c8643a';g.lineWidth=4;g.beginPath();g.moveTo(cx,cy-30);g.lineTo(cx+28,cy);g.lineTo(cx,cy+30);g.lineTo(cx-28,cy);g.closePath();g.stroke();}
    for(let i=0;i<26000;i++){g.fillStyle='rgba('+(r()<.5?'255,255,255':'40,30,20')+','+r()*.07+')';g.fillRect(r()*w,r()*h,1.6,1.6);}}),hc=can('rugb',256,256,(g,w,h,r)=>{for(let y=0;y<h;y+=2)for(let x=0;x<w;x+=2){const v=90+r()*110;g.fillStyle='rgb('+v+','+v+','+v+')';g.fillRect(x,y,2,2);}});
  const g2=slab(W,1.2*U,L,2*U,.5*U,3),p=g2.attributes.position,uv=new Float32Array(p.count*2);for(let i=0;i<p.count;i++){uv[i*2]=p.getX(i)/W+.5;uv[i*2+1]=p.getZ(i)/L+.5;}g2.setAttribute('uv',new THREE.BufferAttribute(uv,2));
  const nt=T2(heightToNormal(hc,1.5),6,9,true),rm=mat('rug',()=>std({map:tex(c,'rug'),normalMap:nt,normalScale:new THREE.Vector2(.7,.7),roughness:1,envMapIntensity:.15}));
  /* the Blender-built rug (tools/blender/rug.py): not quite flat, one corner curling, a fringe at both ends; 110 x 150 cm, scaled to other sizes */
  if(pkReady('rug')){const g=pk('rug',{rug:[rm,[110,150]],fringe:[fabric('fringe','#e9e0cf',{ws:2,ns:.5}),12]});g.scale.set((o.w||160)/110,1,(o.l||230)/150);return g;}
  add(G,g2,rm,0,.6*U,0);return G;};
/* ============ shoes ============ */
/* one sneaker, 29 cm long: a rubber sole with a sidewall, an upper lofted from cross-sections, a toe cap, a tongue and laces. Toe at +z. */
M.sneaker=function(o){o=o||{};const G=grp(),L=29*U,col=o.color||'#f4f4f2',up=fabric('sneak'+col,col,{ws:2,ns:.6,rough:.8}),rub=plastic('sole','#f0eee8',.7),acc=plastic('sneakacc'+(o.accent||''),o.accent||'#e0452c',.55);
  /* half the foot's width along its length (0 heel .. 1 toe), and the height of the upper */
  const wid=t=>(3.0+2.4*Math.sin(Math.min(1,t*1.25)*Math.PI*.62)+1.0*Math.sin(t*Math.PI))*U*(t>.8?Math.sqrt(Math.max(.02,1-Math.pow((t-.8)/.2,2))):t<.12?.62+.38*Math.sqrt(Math.max(0,1-Math.pow((.12-t)/.12,2))):1),zOf=t=>(t-.5)*L;
  const hgt=t=>(t<.2?12.5:t<.5?12.5-(t-.2)/.3*5.3:t<.85?7.2-(t-.5)/.35*2:5.2-(t-.85)/.15*1.6)*U;
  const sole=new THREE.Shape(),N=30;for(let i=0;i<=N;i++){const t=i/N;sole[i?'lineTo':'moveTo'](wid(t)*1.04,zOf(t)*1.02);}for(let i=N;i>=0;i--){const t=i/N;sole.lineTo(-wid(t)*1.04,zOf(t)*1.02);}
  const sg=new THREE.ExtrudeGeometry(sole,{depth:2.2*U,bevelEnabled:true,bevelThickness:.4*U,bevelSize:.3*U,bevelSegments:3});sg.rotateX(Math.PI/2);sg.translate(0,3.0*U,0);add(G,sg,rub);
  add(G,(()=>{const g=new THREE.ExtrudeGeometry(sole,{depth:.45*U,bevelEnabled:false});g.rotateX(Math.PI/2);g.translate(0,.45*U,0);g.scale(.97,1,.98);return g;})(),plastic('tread','#3a3d44',.9));
  add(G,(()=>{const g=new THREE.ExtrudeGeometry(sole,{depth:.5*U,bevelEnabled:false});g.rotateX(Math.PI/2);g.translate(0,2.0*U,0);g.scale(1.012,1,1.006);return g;})(),acc);/* a stripe round the midsole */
  /* the upper: hoops across the foot from heel to toe, closed over the toe, open at the collar where the foot goes in */
  function loft(t0,t1,k,m,st){const P=[],I=[],UV=[],S=14;for(let i=0;i<=st;i++){const t=t0+(t1-t0)*i/st,w=wid(t)*k,h=(hgt(t)-2.8*U)*k,open=t<.42?1:0;for(let q=0;q<=S;q++){const a=q/S*Math.PI,c=Math.cos(a),s=Math.sin(a);let x=c*w*(.86+.14*(1-s)),y=2.8*U+Math.pow(s,.62)*h;
        if(open){const rim=.78;if(s>rim){const f=(s-rim)/(1-rim);y=2.8*U+Math.pow(rim,.62)*h+f*h*.04;x=c*w*(.86+.14*(1-rim))*(1-f*.1);}}P.push(x,y,zOf(t));UV.push(q/S*2,t*4);}}
    for(let i=0;i<st;i++)for(let q=0;q<S;q++){const a=i*(S+1)+q,b=a+1,c=a+S+1,e=c+1;if(t0+(t1-t0)*(i+.5)/st<.42&&q>=5&&q<9)continue;I.push(a,b,c,b,e,c);}
    const g=new THREE.BufferGeometry();if(t0===0){/* the back of the heel */const c0=P.length/3;P.push(0,2.8*U,zOf(0));UV.push(1,0);for(let q=0;q<S;q++)I.push(c0,q+1,q);}g.setAttribute('position',new THREE.Float32BufferAttribute(P,3));g.setAttribute('uv',new THREE.Float32BufferAttribute(UV,2));g.setIndex(I);g.computeVertexNormals();const o2=add(G,g,m);m.side=THREE.DoubleSide;return o2;}
  loft(0,1,1,up,26);loft(0,.13,1.035,acc,5);loft(.8,1,1.035,rub,8);
  /* inside, the tongue, the eyelet strips and five laces */
  add(G,box(wid(.25)*1.5,.3*U,L*.4),paint('insole','#2a2c31',.9),0,4.2*U,zOf(.22));add(G,blob(4.6*U,1.6*U,11*U,.6,8),up,0,9.6*U,zOf(.47),-.36);
  for(let i=0;i<5;i++){const t=.45+i*.07,y=hgt(t)+.1*U;add(G,cyl(.26*U,.26*U,wid(t)*.95,6),paint('lace','#fbfbf8',.9),0,y,zOf(t),0,0,Math.PI/2);}
  return G;};
/* ============ the room's own parts ============ */
/* a window, w x h cm: frame, a centre bar, glass and a sill; origin at the middle of the opening's bottom edge, facing +z (into the room) */
M.window=function(w,h,o){o=o||{};const G=grp(),W=w*U,H=h*U,fr=paint('winframe','#f6f5f1',.45),t=5.5*U,dp=9*U;
  for(const s of [-1,1])add(G,slab(t,H,dp,.6*U,.3*U,2),fr,s*(W/2-t/2),H/2,0);add(G,slab(W,t,dp,.6*U,.3*U,2),fr,0,t/2,0);add(G,slab(W,t,dp,.6*U,.3*U,2),fr,0,H-t/2,0);
  add(G,slab(4*U,H-2*t,5*U,.5*U,.25*U,2),fr,0,H/2,0);for(const s of [-1,1]){const x=s*(W/4-t/4+1*U);/* each sash: a thinner inner frame */
    for(const q of [-1,1])add(G,box(2.6*U,H-2*t,3*U),fr,x+q*(W/4-t/2-1.6*U),H/2,-1*U);add(G,box(W/2-t-2*U,2.6*U,3*U),fr,x,t+1.3*U,-1*U);add(G,box(W/2-t-2*U,2.6*U,3*U),fr,x,H-t-1.3*U,-1*U);
    add(G,box(1.2*U,5*U,1.6*U),metal('winhandle','#c9ccd2',.3),x-s*(W/4-t/2-3*U),H/2,1.4*U);}
  const gl=add(G,new THREE.PlaneGeometry(W-2*t,H-2*t),glass('winglass','#dfeeff',.12),0,H/2,-1.5*U);gl.userData.cast=false;
  add(G,slab(W+10*U,3*U,dp+9*U,1*U,.6*U,3),fr,0,-1.5*U,4.5*U);/* the sill */return G;};
/* what is outside the window: sky, clouds, a neighbour's roof and trees, as a lit picture a little way beyond the glass */
M.outside=function(w,h){
  /* the garden rendered in Blender (tools/blender/outside.py): lawn, a board fence, trees lit from behind, a neighbour's house. It covers the same 2.6 x 2.2 window-sizes the drawn picture did */
  if(typeof PROP_TEX!=='undefined'&&PROP_TEX.tex_toy_outside){const m=new THREE.Mesh(new THREE.PlaneGeometry(w*U,h*U),mat('outside',()=>new THREE.MeshBasicMaterial({map:propTex('tex_toy_outside'),toneMapped:false,color:new THREE.Color(1.22,1.22,1.24)})/* a little over full brightness: daylight seen from indoors */));m.userData.cast=false;return m;}
  const c=can('outside',1024,768,(g,W,H,r)=>{const sk=g.createLinearGradient(0,0,0,H);sk.addColorStop(0,'#5fa0e6');sk.addColorStop(.6,'#bfe0fb');sk.addColorStop(1,'#eaf5ff');g.fillStyle=sk;g.fillRect(0,0,W,H);
    for(let i=0;i<9;i++){const x=r()*W,y=40+r()*260;for(let k=0;k<7;k++){g.fillStyle='rgba(255,255,255,'+(.16+r()*.2)+')';g.beginPath();g.ellipse(x+(r()-.5)*150,y+(r()-.5)*30,60+r()*70,20+r()*18,0,0,7);g.fill();}}
    g.fillStyle='#8c9aa6';g.beginPath();g.moveTo(520,560);g.lineTo(760,420);g.lineTo(1024,540);g.lineTo(1024,768);g.lineTo(520,768);g.fill();g.fillStyle='#d9d2c4';g.fillRect(560,590,464,178);g.fillStyle='#6f7f8c';g.fillRect(640,630,90,90);g.fillRect(820,630,90,90);
    for(let i=0;i<60;i++){const x=r()*560-40,y=470+r()*200,rr=40+r()*60;g.fillStyle=['#3f7a3a','#4e8f45','#2f6a34','#5a9c4c'][i%4];g.globalAlpha=.9;g.beginPath();g.arc(x,y,rr,0,7);g.fill();}g.globalAlpha=1;g.fillStyle='#4a8a40';g.fillRect(0,690,1024,78);});
  const m=new THREE.Mesh(new THREE.PlaneGeometry(w*U,h*U),mat('outside',()=>new THREE.MeshBasicMaterial({map:tex(c,'outside'),toneMapped:false,color:'#e8e8e8'})));m.userData.cast=false;return m;};
/* a curtain panel hanging in pleats from a rod: w cm wide when drawn back, h cm long; origin at the top middle */
M.curtain=function(w,h,o){o=o||{};
  /* the Blender-built panels (tools/blender/curtain.py), hung as cloth: 58 x 159 cm, two that hang differently; other sizes are scaled from them */
  if(pkReady('curtain')){const cm=fabric('curtain',o.color||'#c9bfae',{ws:3,ns:.9});cm.side=THREE.DoubleSide;const g=pk('curtain',{[(o.seed||4)>3?'curtainR':'curtainL']:[cm,40]});g.scale.set(w/58,h/159,.75);return g;}
  const G=grp(),W=w*U,H=h*U,nx=40,ny=10,P=[],I=[],UV=[],r=rng(o.seed||4);
  for(let j=0;j<=ny;j++)for(let i=0;i<=nx;i++){const u=i/nx,v=j/ny,amp=(2.2+v*2.6)*U,ph=u*Math.PI*2*7;P.push((u-.5)*W*(1-v*.06),-v*H,Math.sin(ph)*amp+Math.sin(ph*.5+1)*amp*.4);UV.push(u*3,v*H/(40*U));}
  for(let j=0;j<ny;j++)for(let i=0;i<nx;i++){const a=j*(nx+1)+i,b=a+1,c=a+nx+1,e=c+1;I.push(a,c,b,b,c,e);}const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(P,3));g.setAttribute('uv',new THREE.Float32BufferAttribute(UV,2));g.setIndex(I);g.computeVertexNormals();
  const m=fabric('curtain',o.color||'#c9bfae',{ws:3,ns:.9});m.side=THREE.DoubleSide;add(G,g,m);return G;};
/* an interior door, 82 x 203 cm, with four raised panels, its casing, hinges and a lever handle; origin at the bottom middle, facing +z */
M.door=function(){const G=grp(),W=82*U,H=203*U,wh=paint('doorwhite','#f3f1ec',.5),t=4*U;add(G,slab(W,H,t,.3*U,.2*U,2),wh,0,H/2,0);
  for(const [x,y,w,h] of [[-.25,.72,.36,.42],[.25,.72,.36,.42],[-.25,.26,.36,.4],[.25,.26,.36,.4]]){add(G,slab(w*W,1*U,h*H,1*U,.5*U,3),wh,x*W,y*H,t/2+.2*U,Math.PI/2);add(G,slab(w*W-5*U,.8*U,h*H-5*U,.8*U,.4*U,3),wh,x*W,y*H,t/2+.9*U,Math.PI/2);}
  const cs=9*U;for(const s of [-1,1])add(G,slab(cs,H+cs,2.4*U,.5*U,.5*U,3),wh,s*(W/2+cs/2+.5*U),(H+cs)/2,t/2);add(G,slab(W+2*cs+1*U,cs,2.4*U,.5*U,.5*U,3),wh,0,H+cs/2+.5*U,t/2);
  const st=metal('doorsteel','#b9bcc2',.3);add(G,cyl(2.6*U,2.6*U,1*U,20),st,W/2-7*U,100*U,t/2+.5*U,Math.PI/2);add(G,cyl(.9*U,.9*U,5*U,12),st,W/2-7*U,100*U,t/2+3*U,Math.PI/2);add(G,slab(12*U,1.8*U,2*U,.8*U,.5*U,3),st,W/2-12*U,100*U,t/2+5.5*U);
  for(const y of [22,100,180])add(G,box(.6*U,9*U,3*U),st,-W/2-.2*U,y*U,t/2);return G;};
/* ============ smaller things ============ */
M.nightstand=function(){const G=grp(),W=46*U,D=40*U,H=52*U,oak=wood('oak','#b98a58','#5a3a1c',{rough:.5}),leg=14*U;add(G,uvw(slab(W,H-leg,D,1.2*U,.5*U,3),80),oak,0,leg+(H-leg)/2,0);for(const sx of [-1,1])for(const sz of [-1,1])add(G,cyl(1.8*U,1.2*U,leg,12),oak,sx*(W/2-4*U),leg/2,sz*(D/2-4*U));
  for(let i=0;i<2;i++){const y=leg+4*U+(H-leg-6*U)/4+i*(H-leg-4*U)/2;add(G,uvw(slab(W-4*U,1.6*U,(H-leg)/2-3.4*U,.8*U,.4*U,3),80),oak,0,y,D/2+.3*U,Math.PI/2);add(G,cyl(1.3*U,1.3*U,1.6*U,16),metal('brass','#b08a4a',.3),0,y,D/2+2*U,Math.PI/2);}return G;};
/* a coffee mug, 9.5 cm tall and 8 cm across, with a handle */
M.mug=function(o){o=o||{};const G=grp(),c=mat('mug'+(o.color||''),()=>phy({color:o.color||'#f4f1ea',roughness:.25,clearcoat:.6,clearcoatRoughness:.2,envMapIntensity:.8,side:THREE.DoubleSide})),pts=[];
  for(const [r,y] of [[0,0],[3.4,0],[3.9,.5],[4,9.3],[3.85,9.5],[3.55,9.3],[3.5,1],[0,.9]])pts.push(new THREE.Vector2(r*U,y*U));add(G,new THREE.LatheGeometry(pts,36),c);add(G,new THREE.TorusGeometry(2.5*U,.6*U,10,24,Math.PI*1.25),c,4.4*U,4.8*U,0,0,0,-Math.PI*.62);
  add(G,cyl(3.5*U,3.5*U,.1*U,28),mat('coffee',()=>std({color:'#3a2313',roughness:.2})),0,8.2*U,0);return G;};
/* a drinks can, 12.2 cm tall */
M.sodacan=function(o){o=o||{};const G=grp(),c=can('can'+(o.color||'o'),256,256,(g,W,H)=>{g.fillStyle=o.color||'#e0452c';g.fillRect(0,0,W,H);g.fillStyle='#fff4dc';g.font='900 54px Arial';g.save();g.translate(128,128);g.rotate(-Math.PI/2);g.textAlign='center';g.fillText('FIZZ',0,18);g.restore();g.fillStyle='rgba(255,255,255,.25)';g.fillRect(0,0,W,22);g.fillRect(0,H-22,W,22);});
  add(G,cyl(3.3*U,3.3*U,10.6*U,32),mat('can'+(o.color||'o'),()=>std({map:tex(c,'can'+(o.color||'o')),roughness:.3,metalness:.7,envMapIntensity:1})),0,5.9*U,0);const al=metal('alu','#cfd3d8',.28);add(G,cyl(3.3*U,2.7*U,.7*U,32),al,0,.35*U,0);add(G,cyl(2.7*U,3.3*U,1*U,32),al,0,11.7*U,0);add(G,new THREE.TorusGeometry(2.7*U,.18*U,6,28),al,0,12.2*U,0,Math.PI/2);return G;};
/* a house plant in a ceramic pot: broad leaves on arching stems, about 55 cm tall */
M.plant=function(o){o=o||{};const G=grp(),r=rng(o.seed||11),pot=mat('pot',()=>phy({color:'#e9e4da',roughness:.4,clearcoat:.3,envMapIntensity:.6})),pts=[];for(const [x,y] of [[0,0],[7,0],[9.5,1],[10.5,16],[10.8,17],[9.6,17],[9.2,3],[0,3]])pts.push(new THREE.Vector2(x*U,y*U));add(G,new THREE.LatheGeometry(pts,28),pot);add(G,cyl(9.4*U,9.4*U,.6*U,24),mat('soil',()=>std({color:'#3a2a1e',roughness:1})),0,15.5*U,0);
  const leaf=mat('leaf',()=>std({color:'#3f7d3c',roughness:.55,side:THREE.DoubleSide,envMapIntensity:.5})),stem=mat('stem',()=>std({color:'#5b8a45',roughness:.7}));
  for(let i=0;i<11;i++){const a=i/11*6.283+r()*.5,len=(22+r()*20)*U,lean=.35+r()*.6,S=grp(G,0,15.5*U,0,a);const top=new THREE.Vector3(Math.sin(lean)*len,Math.cos(lean)*len,0),mid=new THREE.Vector3(Math.sin(lean*.4)*len*.55,Math.cos(lean*.4)*len*.6,0);
    S.add(new THREE.Mesh(new THREE.TubeGeometry(new THREE.QuadraticBezierCurve3(new THREE.Vector3(0,0,0),mid,top),8,.35*U,5),stem));
    /* a leaf: a pointed oval, folded a little along its rib and curled down at the tip */
    const L=(13+r()*8)*U,Wl=L*.42,P=[],I=[],n=8;for(let j=0;j<=n;j++){const t=j/n,w=Math.sin(t*Math.PI)*Wl*(1-.25*t),y=-t*t*L*.35;for(const s of [-1,0,1])P.push(t*L,y+Math.abs(s)*w*.22,s*w);}
    for(let j=0;j<n;j++){const b=j*3;I.push(b,b+3,b+1,b+1,b+3,b+4,b+1,b+4,b+2,b+2,b+4,b+5);}const lg=new THREE.BufferGeometry();lg.setAttribute('position',new THREE.Float32BufferAttribute(P,3));lg.setIndex(I);lg.computeVertexNormals();
    const lm=new THREE.Mesh(lg,leaf);lm.position.copy(top);lm.rotation.z=-lean+.2;S.add(lm);}return G;};
/* a framed poster, w x h cm, with one of a few pictures */
M.poster=function(w,h,kind){const G=grp(),W=w*U,H=h*U,c=can('poster'+kind,512,720,(g,cw,ch,r)=>{if(kind===0){const b=g.createLinearGradient(0,0,0,ch);b.addColorStop(0,'#ff8a3d');b.addColorStop(.55,'#d8496a');b.addColorStop(1,'#2a1a4a');g.fillStyle=b;g.fillRect(0,0,cw,ch);g.fillStyle='#ffe9a8';g.beginPath();g.arc(cw/2,ch*.48,120,0,7);g.fill();g.fillStyle='#1a1030';g.beginPath();g.moveTo(0,ch*.62);for(let x=0;x<=cw;x+=40)g.lineTo(x,ch*(.56+r()*.1));g.lineTo(cw,ch);g.lineTo(0,ch);g.fill();g.fillStyle='#fff4dc';g.font='900 64px Arial';g.textAlign='center';g.fillText('RACE DAY',cw/2,ch-60);}
    else if(kind===1){g.fillStyle='#10131a';g.fillRect(0,0,cw,ch);for(let i=0;i<7;i++){g.strokeStyle=['#ff6a12','#39d98a','#4aa8ff','#ffd24a'][i%4];g.lineWidth=14;g.beginPath();g.arc(cw/2,ch*.45,40+i*30,-.6+i*.3,2.2+i*.3);g.stroke();}g.fillStyle='#fff';g.font='900 54px Arial';g.textAlign='center';g.fillText('CRUST RUSH',cw/2,ch-70);g.font='700 26px Arial';g.fillText('WORLD TOUR',cw/2,ch-34);}
    else{g.fillStyle='#e9e2d2';g.fillRect(0,0,cw,ch);g.fillStyle='#c8321d';g.beginPath();g.moveTo(cw*.2,ch*.25);g.lineTo(cw*.8,ch*.32);g.lineTo(cw*.42,ch*.72);g.closePath();g.fill();g.fillStyle='#f7c948';g.beginPath();g.moveTo(cw*.26,ch*.29);g.lineTo(cw*.72,ch*.345);g.lineTo(cw*.43,ch*.66);g.closePath();g.fill();g.fillStyle='#a8281a';for(const [x,y] of [[.4,.38],[.55,.42],[.45,.52]]){g.beginPath();g.arc(cw*x,ch*y,22,0,7);g.fill();}g.fillStyle='#25150f';g.font='900 50px Arial';g.textAlign='center';g.fillText('ONE MORE SLICE',cw/2,ch-70);}});
  add(G,new THREE.PlaneGeometry(W,H),mat('poster'+kind,()=>std({map:tex(c,'poster'+kind),roughness:.6,envMapIntensity:.3})),0,0,.9*U);const fr=plastic('black','#0c0c0d',.6),t=1.6*U;for(const s of [-1,1]){add(G,box(t,H+2*t,1.8*U),fr,s*(W/2+t/2),0,.6*U);add(G,box(W,t,1.8*U),fr,0,s*(H/2+t/2),.6*U);}
  const gl=add(G,new THREE.PlaneGeometry(W,H),glass('frameglass','#ffffff',.08),0,0,1.2*U);gl.userData.cast=false;return G;};
/* a wall shelf, 90 cm long, with books standing on it, a trophy and a small plant pot */
M.shelf=function(){const G=grp(),oak=wood('oak','#b98a58','#5a3a1c',{rough:.5}),W=90*U,D=22*U;add(G,uvw(slab(W,3*U,D,.8*U,.4*U,3),80),oak,0,0,D/2);for(const s of [-1,1])add(G,box(2*U,12*U,2*U),metal('bracket','#2a2c31',.5),s*W*.36,-7*U,1*U);
  const r=rng(21),cols=['#b8322a','#27527a','#e0a020','#2f6b4a','#5a3d7a','#d8d2c4','#1d1f24'];let x=-W/2+5*U;for(let i=0;i<9;i++){const t=(2+r()*2.6)*U,h=(18+r()*7)*U,d=(13+r()*4)*U,c=cols[Math.floor(r()*cols.length)];add(G,slab(t,h,d,.3*U,.15*U,2),paint('book'+c,c,.6),x+t/2,1.5*U+h/2,D/2,0,0,i===8?.18:0);x+=t+.15*U;}
  const gold=metal('gold','#d8a83a',.22),tx=W/2-16*U;add(G,slab(8*U,3*U,8*U,.6*U,.3*U,2),plastic('black','#0c0c0d',.6),tx,3*U,D/2);add(G,cyl(.8*U,1.6*U,6*U,14),gold,tx,7.5*U,D/2);const cp=[];for(const [rr,y] of [[1,0],[3.2,2],[4.4,6],[4.6,8.5],[4.2,8.5],[3.9,6],[2.6,2.4],[0,1.2]])cp.push(new THREE.Vector2(rr*U,y*U));add(G,new THREE.LatheGeometry(cp,24),gold,tx,10.2*U,D/2);return G;};
/* a cardboard storage box with a taped lid, w x d x h cm */
M.carton=function(w,d,h){const G=grp(),c=can('carton',256,256,(g,W,H,r)=>{g.fillStyle='#b58a5a';g.fillRect(0,0,W,H);for(let i=0;i<160;i++){g.strokeStyle='rgba(90,60,30,'+r()*.14+')';g.beginPath();const y=r()*H;g.moveTo(0,y);g.lineTo(W,y);g.stroke();}}),m=mat('carton',()=>std({map:tex(c,'carton'),roughness:.9,envMapIntensity:.2}));
  add(G,uvw(slab(w*U,h*U,d*U,.6*U,.3*U,2),40),m,0,h*U/2,0);add(G,box(w*U+.2*U,.15*U,6*U),mat('tape',()=>std({color:'#c9a878',roughness:.35,envMapIntensity:.6})),0,h*U+.05*U,0);add(G,box(.15*U,h*U*.4,6*U),mat('tape',()=>std({color:'#c9a878',roughness:.35})),w*U/2+.05*U,h*U*.8,0);return G;};
/* a wire-mesh waste bin, 28 cm tall */
M.bin=function(){const G=grp(),c=can('binmesh',64,64,(g,W,H)=>{g.clearRect(0,0,W,H);g.strokeStyle='#1c1d20';g.lineWidth=5;g.beginPath();g.moveTo(0,0);g.lineTo(W,H);g.moveTo(W,0);g.lineTo(0,H);g.stroke();}),t=T2(c,22,8),m=mat('binmesh',()=>std({map:t,alphaTest:.5,side:THREE.DoubleSide,roughness:.5,metalness:.7}));
  add(G,new THREE.CylinderGeometry(12*U,9.5*U,28*U,28,1,true),m,0,14*U,0);const bl=metal('binrim','#1c1d20',.5);add(G,new THREE.TorusGeometry(12*U,.5*U,6,28),bl,0,28*U,0,Math.PI/2);add(G,cyl(9.5*U,9.5*U,.6*U,24),bl,0,.3*U,0);
  for(let i=0;i<3;i++)add(G,blob((7+i)*U,(6+i)*U,(7+i)*U,.9,6),paint('paperball','#f1eee6',.95),(i-1)*4*U,(4+i*4)*U,(i%2)*3*U);return G;};
/* ============ small things on the floor and the desk: the scale references ============ */
/* several coloured pieces baked into one mesh: [geometry, matrix, colour] */
function bake(list,m){const P=[],Nn=[],C=[],v=new THREE.Vector3(),nm=new THREE.Matrix3(),col=new THREE.Color();
  for(const [g0,mx,c] of list){const g=g0.index?g0.toNonIndexed():g0,p=g.attributes.position,n=g.attributes.normal;nm.getNormalMatrix(mx);col.set(c);
    for(let i=0;i<p.count;i++){v.fromBufferAttribute(p,i).applyMatrix4(mx);P.push(v.x,v.y,v.z);v.fromBufferAttribute(n,i).applyMatrix3(nm).normalize();Nn.push(v.x,v.y,v.z);C.push(col.r,col.g,col.b);}}
  const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(P,3));g.setAttribute('normal',new THREE.Float32BufferAttribute(Nn,3));g.setAttribute('color',new THREE.Float32BufferAttribute(C,3));return new THREE.Mesh(g,m);}
const MX=(x,y,z,rx,ry,rz,s)=>new THREE.Matrix4().compose(new THREE.Vector3(x||0,y||0,z||0),new THREE.Quaternion().setFromEuler(new THREE.Euler(rx||0,ry||0,rz||0)),new THREE.Vector3(s||1,s||1,s||1));
const vcPlastic=()=>mat('vcplastic',()=>phy({vertexColors:true,roughness:.3,clearcoat:.5,clearcoatRoughness:.25,envMapIntensity:.7}));
const vcMatte=()=>mat('vcmatte',()=>std({vertexColors:true,roughness:.7,envMapIntensity:.3}));
/* a skateboard: 80 x 20 cm maple deck with kicked nose and tail, grip tape, trucks and four wheels */
M.skateboard=function(o){o=o||{};const G=grp(),L=80*U,W=20.5*U,TH=1.15*U,NX=40,NZ=10,top=[],bot=[],edge=[],uvT=[],uvB=[],uvE=[];
  const hw=x=>{const a=Math.abs(x),e=L/2-W/2;if(a<=e)return W/2;const t=(a-e)/(W/2);return W/2*Math.pow(Math.max(0,1-t*t),.42);},
    yy=(x,z)=>{const a=Math.abs(x),k=27*U,t=Math.max(0,(a-k)/(L/2-k));return t*t*5.2*U+.55*U*Math.pow(Math.abs(z)/(W/2),2);};
  const pt=(i,j)=>{const x=-L/2+L*i/NX,x1=Math.max(-L/2+.02*U,Math.min(L/2-.02*U,x)),w=Math.max(.3*U,hw(x1)),z=-w+2*w*j/NZ;return [x1,yy(x1,z),z];};
  for(let i=0;i<NX;i++)for(let j=0;j<NZ;j++){const a=pt(i,j),b=pt(i+1,j),c=pt(i+1,j+1),d=pt(i,j+1),u=p=>[p[0]/L+.5,p[2]/W+.5];
    top.push(...a,...d,...c,...a,...c,...b);for(const p of [a,d,c,a,c,b])uvT.push(...u(p));
    const dn=p=>[p[0],p[1]-TH,p[2]];bot.push(...dn(a),...dn(c),...dn(d),...dn(a),...dn(b),...dn(c));for(const p of [a,c,d,a,b,c])uvB.push(...u(p));}
  /* the rim: seven plies of maple seen edge on */
  const rim=[];for(let i=0;i<=NX;i++)rim.push(pt(i,0));for(let j=1;j<=NZ;j++)rim.push(pt(NX,j));for(let i=NX-1;i>=0;i--)rim.push(pt(i,NZ));for(let j=NZ-1;j>=1;j--)rim.push(pt(0,j));
  for(let i=0;i<rim.length;i++){const a=rim[i],b=rim[(i+1)%rim.length],a2=[a[0],a[1]-TH,a[2]],b2=[b[0],b[1]-TH,b[2]];edge.push(...a,...b,...b2,...a,...b2,...a2);uvE.push(i,1,i+1,1,i+1,0,i,1,i+1,0,i,0);}
  const mk=(pos,uv,m)=>{const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(pos,3));g.setAttribute('uv',new THREE.Float32BufferAttribute(uv,2));g.computeVertexNormals();return add(G,g,m,0,9.3*U,0);};
  const grip=can('grip',256,64,(g,w,h,r)=>{g.fillStyle='#17181a';g.fillRect(0,0,w,h);for(let i=0;i<5000;i++){const v=20+r()*50;g.fillStyle='rgb('+v+','+v+','+v+')';g.fillRect(r()*w,r()*h,1,1);}}),
    art=can('deckart'+(o.color||''),512,128,(g,w,h,r)=>{g.fillStyle=o.color||'#d8452e';g.fillRect(0,0,w,h);g.fillStyle='#f6c945';for(let i=0;i<7;i++){g.beginPath();g.moveTo(256,64);g.arc(256,64,400,i*.9,i*.9+.42);g.fill();}
      g.fillStyle='#1b1b1e';g.beginPath();g.arc(256,64,46,0,7);g.fill();g.fillStyle='#fff4dc';g.font='900 30px Arial';g.textAlign='center';g.fillText('RUSH',256,75);for(let i=0;i<60;i++){g.strokeStyle='rgba(255,255,255,'+(.05+r()*.12)+')';g.lineWidth=.6+r();g.beginPath();const x=r()*w,y=r()*h;g.moveTo(x,y);g.lineTo(x+(r()-.5)*90,y+(r()-.5)*14);g.stroke();}}),
    ply=can('ply',8,64,(g,w,h)=>{for(let i=0;i<7;i++){g.fillStyle=i%2?'#c79a62':'#e2bd86';g.fillRect(0,i*h/7,w,h/7+1);}});
  mk(top,uvT,mat('grip',()=>std({map:tex(grip,'grip'),roughness:1,envMapIntensity:.1})));mk(bot,uvB,mat('deckart'+(o.color||''),()=>phy({map:tex(art,'deckart'+(o.color||'')),roughness:.35,clearcoat:.5,side:THREE.DoubleSide})));
  mk(edge,uvE,mat('ply',()=>std({map:tex(ply,'ply'),roughness:.6,side:THREE.DoubleSide})));
  const al=metal('truck','#b9bcc2',.38),ur=mat('urethane'+(o.wheel||''),()=>phy({color:o.wheel||'#f1ead8',roughness:.42,clearcoat:.3,envMapIntensity:.5})),bk=plastic('black','#0c0c0d',.6);
  for(const s of [-1,1]){const T=grp(G,s*21.5*U,0,0);add(T,slab(8.2*U,.7*U,5.6*U,.8*U,.2*U,2),al,0,7.75*U,0);add(T,cyl(1.5*U,1.9*U,2.6*U,14),bk,0,6.2*U,0);
    const h=add(T,cyl(1.25*U,1.25*U,13.2*U,14),al,-s*.9*U,2.75*U,0,Math.PI/2);add(T,new THREE.CylinderGeometry(1.3*U,2.4*U,3.4*U,12),al,-s*.6*U,4.6*U,0);
    add(T,cyl(.42*U,.42*U,21.4*U,10),metal('axle','#8d9096',.3),-s*.9*U,2.75*U,0,Math.PI/2);add(T,cyl(.5*U,.5*U,.8*U,10),al,s*1.4*U,8.3*U,0);
    for(const z of [-1,1]){const wg=new THREE.LatheGeometry([[0,-1.6],[1.6,-1.6],[2.45,-1.25],[2.7,-.6],[2.7,.6],[2.45,1.25],[1.6,1.6],[0,1.6]].map(p=>new THREE.Vector2(p[0]*U,p[1]*U)),28);add(T,wg,ur,-s*.9*U,2.75*U,z*8.9*U,Math.PI/2);
      add(T,cyl(1.1*U,1.1*U,3.3*U,16),metal('bearing','#70747b',.3),-s*.9*U,2.75*U,z*8.9*U,Math.PI/2);add(T,cyl(.62*U,.62*U,.5*U,6),al,-s*.9*U,2.75*U,z*10.75*U,Math.PI/2);}}
  return G;};
/* a ball: 'basket' (24 cm) or 'tennis' (6.7 cm) */
M.ball=function(o){o=o||{};const kind=o.kind||'basket',R=(kind==='tennis'?3.35:12)*U,G=grp();
  const c=can('ball_'+kind,1024,512,(g,W,H,r)=>{if(kind==='tennis'){g.fillStyle='#c9dc3c';g.fillRect(0,0,W,H);for(let i=0;i<9000;i++){g.fillStyle='rgba('+(r()<.5?'255,255,200':'90,110,0')+','+(r()*.12)+')';g.fillRect(r()*W,r()*H,2,1);}
      g.strokeStyle='#f4f6e6';g.lineWidth=17;g.beginPath();for(let x=-10;x<=W+10;x+=4){const y=H/2+H*.27*Math.sin(x/W*Math.PI*4);x<0?g.moveTo(x,y):g.lineTo(x,y);}g.stroke();}
    else{g.fillStyle='#d2691e';g.fillRect(0,0,W,H);for(let i=0;i<14000;i++){g.fillStyle='rgba('+(r()<.5?'255,190,120':'70,25,0')+','+(.05+r()*.12)+')';g.beginPath();g.arc(r()*W,r()*H,1.2,0,7);g.fill();}
      g.strokeStyle='#17110d';g.lineWidth=7;g.beginPath();g.moveTo(0,H/2);g.lineTo(W,H/2);g.stroke();for(const x of [0,W/2,W]){g.beginPath();g.moveTo(x,0);g.lineTo(x,H);g.stroke();}
      for(const x of [W/4,W*3/4]){g.beginPath();g.ellipse(x,H/2,W*.085,H*.33,0,0,7);g.stroke();}}}),
    b=can('ballb_'+kind,256,128,(g,W,H,r)=>{g.fillStyle='#808080';g.fillRect(0,0,W,H);for(let i=0;i<(kind==='tennis'?5000:2600);i++){const v=kind==='tennis'?90+r()*80:150+r()*60;g.fillStyle='rgb('+v+','+v+','+v+')';g.beginPath();g.arc(r()*W,r()*H,kind==='tennis'?.8:1.5,0,7);g.fill();}}),
    nt=tex(heightToNormal(b,1.2),'ballb_'+kind,true);nt.repeat.set(kind==='tennis'?3:7,kind==='tennis'?2:4);
  add(G,new THREE.SphereGeometry(R,40,26),mat('ball_'+kind,()=>std({map:tex(c,'ball_'+kind),normalMap:nt,normalScale:new THREE.Vector2(.6,.6),roughness:kind==='tennis'?1:.72,envMapIntensity:.3})),0,R,0,o.rx||.5,o.ry||0,o.rz||.3);return G;};
/* a 5.7 cm puzzle cube, scrambled: 26 black cubies with a coloured sticker on every outside face */
M.cube=function(o){o=o||{};const G=grp(),r=rng(o.seed||5),S=1.9*U,cols=['#f4f4f0','#f2d21c','#d42a20','#f07a18','#1e5fd0','#1c9a4c'],L=[],cg=slab(S*.98,S*.98,S*.98,S*.14,S*.12,1),sg=box(S*.78,.035*U,S*.78);
  for(let x=-1;x<=1;x++)for(let y=-1;y<=1;y++)for(let z=-1;z<=1;z++){if(!x&&!y&&!z)continue;L.push([cg,MX(x*S,y*S,z*S),'#141416']);
    const st=(cnd,px,py,pz,rx,rz)=>{if(cnd)L.push([sg,MX(x*S+px,y*S+py,z*S+pz,rx,0,rz),cols[Math.floor(r()*6)]]);},h=S*.5;
    st(y===1,0,h,0,0,0);st(y===-1,0,-h,0,Math.PI,0);st(x===1,h,0,0,0,-Math.PI/2);st(x===-1,-h,0,0,0,Math.PI/2);st(z===1,0,0,h,Math.PI/2,0);st(z===-1,0,0,-h,-Math.PI/2,0);}
  const m=bake(L,vcPlastic());m.position.y=1.5*S;if(o.twist){m.rotation.y=o.twist;}G.add(m);return G;};
/* building bricks tipped out on the floor (n of them inside a circle of `spread` cm) */
M.bricks=function(o){o=o||{};const G=grp(),r=rng(o.seed||3),n=o.n||9,sp=(o.spread||16)*U,cols=['#d42a20','#1e5fd0','#f2c81c','#1c9a4c','#f4f4f0','#f07a18'],L=[],P=.8*U,H=.96*U,sd=cyl(.245*U,.245*U,.18*U,10);
  for(let i=0;i<n;i++){const nx=r()<.6?4:2,nz=r()<.8?2:1,hh=r()<.25?H/3:H,c=cols[Math.floor(r()*cols.length)],a=r()*6.283,d=Math.sqrt(r())*sp,x=Math.cos(a)*d,z=Math.sin(a)*d,ry=r()*6.283,tip=r()<.22,
      base=tip?MX(x,nz*P/2,z,Math.PI/2,ry,0):MX(x,0,z,0,ry,0),bg=slab(nx*P-.02*U,hh,nz*P-.02*U,.06*U,.05*U,1);L.push([bg,base.clone().multiply(MX(0,hh/2,0)),c]);
    for(let ix=0;ix<nx;ix++)for(let iz=0;iz<nz;iz++)L.push([sd,base.clone().multiply(MX((ix-(nx-1)/2)*P,hh+.09*U,(iz-(nz-1)/2)*P)),c]);}
  G.add(bake(L,vcPlastic()));return G;};
/* pencils left on the floor: six-sided, 17.5 cm, with a metal band and a rubber on the end */
M.pencils=function(o){o=o||{};const G=grp(),r=rng(o.seed||2),n=o.n||3,cols=['#f2c230','#d8452e','#2f6fd0','#2e9a58','#f2c230'],L=[],R=.36*U,body=cyl(R,R,15*U,6),tip=new THREE.CylinderGeometry(.09*U,R,1.7*U,6),lead=new THREE.CylinderGeometry(.01,.1*U,.5*U,6),band=cyl(R*1.04,R*1.04,.9*U,12),rub=cyl(R*.98,R*.98,.8*U,12);
  for(let i=0;i<n;i++){const x=(r()-.5)*(o.spread||14)*U,z=(r()-.5)*(o.spread||14)*U,ry=r()*6.283,B=MX(x,R*.87,z,0,ry,0).multiply(MX(0,0,0,0,0,Math.PI/2));
    L.push([body,B.clone().multiply(MX(0,0,0)),cols[i%cols.length]],[tip,B.clone().multiply(MX(0,8.35*U,0)),'#e3c39a'],[lead,B.clone().multiply(MX(0,9.4*U,0)),'#2a2a2e'],[band,B.clone().multiply(MX(0,-7.95*U,0)),'#c9ccd2'],[rub,B.clone().multiply(MX(0,-8.8*U,0)),'#e98a9a']);}
  G.add(bake(L,vcMatte()));return G;};
/* a school backpack stood on the floor */
M.backpack=function(o){o=o||{};const G=grp(),f=fabric('pack'+(o.color||''),o.color||'#2f4a6e',{ws:3,ns:.9}),f2=fabric('pack2'+(o.accent||''),o.accent||'#1b2433',{ws:3,ns:.9}),zp=metal('zip','#a7abb3',.4);
  add(G,blob(31*U,44*U,17*U,.5,14),f,0,22*U,0);add(G,blob(24*U,20*U,8*U,.55,10),f2,0,13.5*U,8.6*U);add(G,blob(26*U,12*U,6*U,.6,10),f,0,32*U,8*U);
  for(const [y,w,z] of [[23.6,23,12.4],[38.2,24,10.6]]){const cv=new THREE.CatmullRomCurve3([-1,-.6,0,.6,1].map(t=>new THREE.Vector3(t*w/2*U,(y-Math.abs(t)*Math.abs(t)*2.2)*U,(z-Math.abs(t)*2.6)*U)));add(G,new THREE.TubeGeometry(cv,20,.28*U,6),zp);}
  const hd=new THREE.CatmullRomCurve3([[-5,43.2,0],[-4,46.5,0],[0,47.6,0],[4,46.5,0],[5,43.2,0]].map(p=>new THREE.Vector3(p[0]*U,p[1]*U,p[2]*U)));add(G,new THREE.TubeGeometry(hd,16,.8*U,8),f2);
  for(const s of [-1,1]){const cv=new THREE.CatmullRomCurve3([[s*8,41,-7],[s*10.5,34,-10.4],[s*11,20,-10.8],[s*10,8,-9.6],[s*8.5,3,-7]].map(p=>new THREE.Vector3(p[0]*U,p[1]*U,p[2]*U))),tg=new THREE.TubeGeometry(cv,20,2.2*U,8);tg.scale(1,1,.35);add(G,tg,f2,0,0,-6.4*U);}
  add(G,slab(1.1*U,2.6*U,.35*U,.4*U,.1*U,1),zp,10.5*U,22.4*U,11.6*U,Math.PI/2);return G;};
/* a game controller */
M.controller=function(o){o=o||{};const G=grp(),b=mat('pad'+(o.color||''),()=>phy({color:o.color||'#e9e9ec',roughness:.42,clearcoat:.3,envMapIntensity:.6})),bk=plastic('black','#0c0c0d',.6),rb=plastic('padrubber','#1a1b1e',.85);
  add(G,blob(15.5*U,4.4*U,7.4*U,.62,12),b,0,3*U,-1*U);for(const s of [-1,1]){const g=add(G,blob(5.2*U,4.6*U,10.4*U,.78,10),b,s*6.2*U,2.8*U,2.2*U);g.rotation.set(-.2,s*-.32,0);}
  for(const [x,z] of [[-4.2,-1.4],[2.2,1.2]]){add(G,cyl(1.15*U,1.25*U,.5*U,20),bk,x*U,5.25*U,z*U);add(G,cyl(.5*U,.6*U,.9*U,12),rb,x*U,5.8*U,z*U);add(G,cyl(.92*U,.85*U,.34*U,20),rb,x*U,6.35*U,z*U);}
  add(G,slab(2.6*U,.5*U,.86*U,.15*U,.12*U,1),bk,-2.2*U,5.3*U,1.2*U);add(G,slab(.86*U,.5*U,2.6*U,.15*U,.12*U,1),bk,-2.2*U,5.3*U,1.2*U);
  [['#f2c81c',4.2,-2.6],['#d42a20',5.5,-1.4],['#1e5fd0',2.9,-1.4],['#1c9a4c',4.2,-.2]].forEach(([c,x,z])=>add(G,cyl(.52*U,.52*U,.5*U,14),plastic('btn'+c,c,.3),x*U,5.3*U,z*U));
  add(G,cyl(.75*U,.75*U,.4*U,18),glow('padhome','#ffffff'),0,5.2*U,-2.2*U);for(const s of [-1,1]){add(G,slab(3.6*U,1.2*U,1.4*U,.4*U,.3*U,2),bk,s*5.2*U,3.9*U,-4.6*U);add(G,slab(1*U,.3*U,.5*U,.2*U,.1*U,1),bk,s*1.5*U,5.2*U,-1.4*U);}
  return G;};
/* the box the racing set came in */
M.setbox=function(o){o=o||{};const G=grp(),W=(o.w||62)*U,D=(o.d||40)*U,H=(o.h||11)*U,c=can('setbox',1024,640,(g,w,h,r)=>{const gr=g.createLinearGradient(0,0,w,h);gr.addColorStop(0,'#143a8c');gr.addColorStop(1,'#0c1f52');g.fillStyle=gr;g.fillRect(0,0,w,h);
      g.fillStyle='#f6c21c';g.beginPath();g.moveTo(0,h);g.lineTo(0,h*.62);g.lineTo(w,h*.34);g.lineTo(w,h);g.fill();g.strokeStyle='#ff6a12';g.lineWidth=44;g.lineCap='round';g.beginPath();g.moveTo(-40,h*.86);g.bezierCurveTo(w*.3,h*.8,w*.36,h*.5,w*.52,h*.5);g.stroke();
      g.beginPath();g.arc(w*.62,h*.5,h*.2,Math.PI,Math.PI*3.02);g.stroke();g.beginPath();g.moveTo(w*.72,h*.5);g.bezierCurveTo(w*.84,h*.5,w*.9,h*.66,w+40,h*.6);g.stroke();
      g.strokeStyle='rgba(120,40,0,.5)';g.lineWidth=3;for(const d of [-12,0,12]){g.beginPath();g.arc(w*.62,h*.5,h*.2+d,0,7);g.stroke();}
      g.fillStyle='#fff';g.font='900 100px Arial Black,Impact,sans-serif';g.textAlign='left';g.fillText('TURBO LOOP',40,120);g.fillStyle='#f6c21c';g.font='900 54px Arial Black,Impact,sans-serif';g.fillText('RACEWAY SET',44,186);
      g.fillStyle='#d42a20';g.beginPath();g.arc(w-120,116,84,0,7);g.fill();g.fillStyle='#fff';g.font='900 46px Arial';g.textAlign='center';g.fillText('62',w-120,112);g.font='900 24px Arial';g.fillText('PIECES',w-120,146);
      g.fillStyle='#0c1f52';g.font='700 26px Arial';g.textAlign='left';g.fillText('CRUST RUSH  -  AGES 5+  -  2 KARTS INCLUDED',44,h-34);}),
    sc=can('setboxside',512,96,(g,w,h)=>{g.fillStyle='#0c1f52';g.fillRect(0,0,w,h);g.fillStyle='#f6c21c';g.fillRect(0,h-16,w,16);g.fillStyle='#fff';g.font='900 46px Arial Black,Impact,sans-serif';g.textAlign='center';g.fillText('TURBO LOOP RACEWAY',w/2,58);}),
    tm=mat('setbox',()=>phy({map:tex(c,'setbox'),roughness:.45,clearcoat:.35,clearcoatRoughness:.4})),sm=mat('setboxside',()=>phy({map:tex(sc,'setboxside'),roughness:.5,clearcoat:.3})),cm2=mat('setboxcard',()=>std({color:'#b99a72',roughness:.9}));
  const m=new THREE.Mesh(new THREE.BoxGeometry(W,H,D),[sm,sm,tm,cm2,sm,sm]);m.position.y=H/2;G.add(m);return G;};
/* a spare piece of track: 30 cm of orange plastic with raised edges and a blue tongue to join the next piece */
M.trackpiece=function(o){o=o||{};const G=grp(),L=(o.l||30)*U,W=84,/* the same two plastics as the track itself (TOYOR and TOYBL in mini.js share these names: keep the settings identical) */sm=m=>{m.userData.noHQ=true;return m;},or=mat('toyorange',()=>sm(phy({color:'#ff6a12',roughness:.34,clearcoat:1,clearcoatRoughness:.07,envMapIntensity:1,side:THREE.DoubleSide}))),bl=mat('toyblue',()=>sm(phy({color:'#1769d6',roughness:.35,clearcoat:.5,clearcoatRoughness:.25})));
  add(G,box(W,1.4,L),or,0,.7,0);for(const s of [-1,1])add(G,slab(3,5.6,L,.8,.6,2),or,s*(W/2+1.5),2.8,0);for(const x of [-21,0,21])add(G,box(.9,.2,L),mat('toygroove',()=>std({color:'#c44a08',roughness:.5})),x,1.45,0);
  add(G,slab(22,1,16,2,.3,1),bl,0,.45,L/2+3);add(G,slab(22,1,16,2,.3,1),bl,0,.45,-L/2-3);return G;};
return Object.assign(M,{U,pk,pkReady,bake,MX,vcPlastic,vcMatte,drape,wood,fabric,plastic,metal,paint,glow,glass,slab,blob,uvw,add,grp,box,cyl,can,tex,mat,std,phy,rng});})();
