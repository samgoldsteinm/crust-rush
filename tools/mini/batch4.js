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
M.cube=function(o){o=o||{};const G=grp(),r=rng(o.seed||5),S=1.9*U,cols=['#f4f4f0','#f2d21c','#d42a20','#f07a18','#1e5fd0','#1c9a4c'],L=[],cg=slab(S*.98,S*.98,S*.98,S*.14,S*.12,2),sg=slab(S*.78,.03*U,S*.78,S*.12,0,1);
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
  add(G,slab(5*U,3*U,.5*U,.5*U,.1*U,1),zp,0,17*U,12.8*U,Math.PI/2);return G;};
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
M.trackpiece=function(o){o=o||{};const G=grp(),L=(o.l||30)*U,W=84,or=mat('toyorange',()=>phy({color:'#ff6a12',roughness:.32,clearcoat:.5,clearcoatRoughness:.3,envMapIntensity:.7})),bl=mat('toyblue',()=>phy({color:'#1769d6',roughness:.35,clearcoat:.4,clearcoatRoughness:.35}));
  add(G,box(W,1.4,L),or,0,.7,0);for(const s of [-1,1])add(G,slab(3,5.6,L,.8,.6,2),or,s*(W/2+1.5),2.8,0);for(const x of [-21,0,21])add(G,box(.9,.2,L),mat('toygroove',()=>std({color:'#c44a08',roughness:.5})),x,1.45,0);
  add(G,slab(22,1,16,2,.3,1),bl,0,.45,L/2+3);add(G,slab(22,1,16,2,.3,1),bl,0,.45,-L/2-3);return G;};
