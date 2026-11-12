/* ================= NEON CUP: tracks laid out by hand (straights and arcs, with a road height for each direction), with their own
   boost pads, ramps, shortcuts, glide and scenery. The layout data is in MAPS (npads, nramps, nshorts, nglide); everything here is
   decided from that data alone, so every player's copy of the track is the same. ================= */
/* a place on the lap given as a fraction of the forward lap: the same spot on the road whichever way the race runs */
const nfj=f=>{const j=Math.round(f*N)%N;return curRev?(N-j)%N:j;};
const nAcc=def=>def.acc||'#3ff0ff',nAcc2=def=>def.acc2||'#ff3fd8';
/* the glide: the road ends at the lip of a raised deck and starts again far ahead and lower down, with a deep shaft in the floor between */
function neonGlide(def){const g=curRev?(def.nglideR||def.nglide):def.nglide;if(!g)return;const GL=Math.round(g[1]/(T.L/N)),ja=Math.round(g[0]*N);
  const j0=curRev?N-ja-GL:ja,j1=j0+GL,a=track[j0],b=track[j1],L=Math.hypot(b.x-a.x,b.y-a.y),ux=(b.x-a.x)/L,uy=(b.y-a.y)/L,long=(a.ey||0)-(b.ey||0)>40;
  GLIDE={j0,j1,rj:j0-4,long,p:a,L,ux,uy,W:CURB+25,D:long?110:50};PITS.push({x:a.x,y:a.y,ux,uy,L,W:GLIDE.W,D:GLIDE.D});
  GLIDE.y0=a.ey||0;GLIDE.y1=b.ey||0;GLIDE.y=long?GLIDE.y0:Math.max(GLIDE.y0,GLIDE.y1);}
const nInGl=(j,a,b)=>GLIDE&&j>GLIDE.rj-(a||12)&&j<GLIDE.j1+(b||40);
function neonPads(def,mats){(def.npads||[]).forEach((q,i)=>{const j=nfj(q[0]);if(nInGl(j))return;const lat=(curRev?-1:1)*(q[1]||0),hw=q[2]||16,pd={j,lat};if(q[2])pd.w=q[2];pads.push(pd);
  const pm=strip(j-2,j+2,lat-hw,lat+hw,.12,mats[i%3],32);if(pm&&pm.isMesh){pm.userData.noMerge=true;pm.castShadow=false;}});}
function neonRampTex(def){const c=cnv(256,256),g=c.getContext('2d');g.fillStyle='#06101c';g.fillRect(0,0,256,256);g.strokeStyle=nAcc2(def);g.lineWidth=16;g.lineJoin='miter';
  for(let y=-40;y<300;y+=64){g.beginPath();g.moveTo(18,y+70);g.lineTo(128,y);g.lineTo(238,y+70);g.stroke();}g.strokeStyle=nAcc(def);g.lineWidth=8;g.strokeRect(4,-20,248,300);return c;}
function neonRamps(def){const t=T2(neonRampTex(def),1,1),topM=new THREE.MeshStandardMaterial({map:t,emissive:'#ffffff',emissiveMap:t,emissiveIntensity:.85,roughness:.3,metalness:.3}),
  sideM=new THREE.MeshStandardMaterial({color:'#0a1422',emissive:nAcc(def),emissiveIntensity:.18,roughness:.4,metalness:.5,side:THREE.DoubleSide});
  for(const f of def.nramps||[]){let j=nfj(f);if(curRev)j=(j-4+N)%N;if(nInGl(j,30,100))continue;const r={j,len:4*T.L/N,w:RW-3,h:6};ramps.push(r);buildRamp(r,topM,sideM);}}
/* shortcuts: given as two places on the lap; the path between them is drawn the same way the other tracks' shortcuts are */
function neonShortcuts(def){SHORTS=[];for(const q of def.nshorts||[]){let a=Math.round(q.a*N)%N,b=Math.round(q.b*N)%N;if(curRev){const t=a;a=(N-b)%N;b=(N-t)%N;}
  const pa=track[a],pb=track[b],s=Math.sign((pb.x-pa.x)*pa.nx+(pb.y-pa.y)*pa.ny)||1,sc=makePath({a,b,s,k:(b-a+N)%N},q.w||SCW,true);
  if(sc){if(q.route)sc.route=true;SHORTS.push(sc);}else console.warn('neon shortcut does not fit',def.id,JSON.stringify(q));}}
function neonLaneTex(def){const c=cnv(128,256),g=c.getContext('2d');g.fillStyle='#070d18';g.fillRect(0,0,128,256);g.strokeStyle=nAcc2(def);g.globalAlpha=.9;g.lineWidth=7;
  for(let y=-20;y<280;y+=64){g.beginPath();g.moveTo(26,y+34);g.lineTo(64,y);g.lineTo(102,y+34);g.stroke();}g.globalAlpha=1;g.fillStyle=nAcc2(def);g.fillRect(0,0,7,256);g.fillRect(121,0,7,256);return c;}
function neonShortcut(sc,def){const SW=sc.w||SCW,P=sc.pts,pos=[],uv=[],idx=[];
  for(let i=0;i<P.length;i++){const p=P[i];for(const sd of [-1,1]){const x=p.x+p.nx*SW*sd,z=p.y+p.ny*SW*sd;pos.push(x,groundAt(x,z)+.12,z);uv.push(sd<0?0:1,i*8/(SW*2));}if(i<P.length-1){const a=i*2;idx.push(a,a+1,a+2,a+1,a+3,a+2);}}
  const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(pos,3));g.setAttribute('uv',new THREE.Float32BufferAttribute(uv,2));g.setIndex(idx);g.computeVertexNormals();
  const lt=T2(neonLaneTex(def),1,1),lm=new THREE.MeshStandardMaterial({name:'neonlane',map:lt,emissive:'#ffffff',emissiveMap:lt,emissiveIntensity:.9,roughness:.3,metalness:.3,side:THREE.DoubleSide});
  const m=new THREE.Mesh(g,lm);m.receiveShadow=true;m.userData.noLift=true;m.userData.noMerge=true;world.add(m);animators.push((t,dt)=>{lt.offset.y-=dt*1.4;});
  /* low rails of light along both sides, open at each end */
  const rp=[],H=3.2,quad=(a,b,c,d)=>rp.push(...a,...b,...c,...a,...c,...d);
  for(const sd of [-1,1])for(let i=2;i<P.length-3;i++){const p=P[i],q=P[i+1],at=(pt,hh)=>{const x=pt.x+pt.nx*(SW+1.2)*sd,z=pt.y+pt.ny*(SW+1.2)*sd;return [x,groundAt(x,z)+hh,z];};quad(at(p,.2),at(q,.2),at(q,H),at(p,H));}
  const rg=new THREE.BufferGeometry();rg.setAttribute('position',new THREE.Float32BufferAttribute(rp,3));
  const rm=new THREE.Mesh(rg,new THREE.MeshBasicMaterial({color:nAcc2(def),transparent:true,opacity:.55,side:THREE.DoubleSide,toneMapped:false,depthWrite:false}));rm.userData.noLift=true;rm.renderOrder=2;world.add(rm);
  /* a gate of light at each mouth */
  const postM=wm('#0c1626',{metalness:.7,roughness:.3}),glow=new THREE.MeshBasicMaterial({color:nAcc2(def),toneMapped:false});
  for(const end of [1,P.length-2]){const p=P[end],G=new THREE.Group();G.position.set(p.x,groundAt(p.x,p.y),p.y);G.rotation.y=-Math.atan2(p.ty,p.tx);G.userData.noLift=true;world.add(G);
    for(const sd of [-1,1]){put(new THREE.CylinderGeometry(.8,1,16,10),postM,0,8,(SW+4)*sd,G);put(new THREE.CylinderGeometry(1.05,1.05,1.2,10),glow,0,12,(SW+4)*sd,G,false);put(new THREE.SphereGeometry(1.5,12,8),glow,0,16.6,(SW+4)*sd,G,false);}
    put(new THREE.BoxGeometry(.7,.7,2*(SW+4)),glow,0,16.6,0,G,false);}}
/* raised roads: a dark slab with a line of light along each edge, a faintly glowing underside and slim columns */
function neonDecks(def){if(def.toy)return toyDecks(def);const W=WALLD+3,inGl=j=>GLIDE&&j>=GLIDE.j0&&j<GLIDE.j1;
  const slabM=new THREE.MeshStandardMaterial({color:'#0b1524',roughness:.35,metalness:.6,side:THREE.DoubleSide,envMapIntensity:.9}),
    lineM=new THREE.MeshBasicMaterial({color:nAcc(def),toneMapped:false,side:THREE.DoubleSide}),
    ut=neonGridTex(nAcc(def)),undM=new THREE.MeshStandardMaterial({map:ut,emissive:'#ffffff',emissiveMap:ut,emissiveIntensity:.5,roughness:.5,metalness:.4,side:THREE.DoubleSide});
  const PIL=[],RING=[];const runs=[];let a=-1;for(let j=0;j<=N;j++){const on=j<N&&track[j].ey>1.5&&!inGl(j);if(on&&a<0)a=j;if(!on&&a>=0){runs.push([a,j]);a=-1;}}
  const P=j=>track[((j%N)+N)%N];
  for(const [j0,j1] of runs){const pos=[],und=[],uu=[],lin=[];
    for(let j=j0-1;j<j1;j++){if(inGl(j)||inGl(j+1))continue;const p=P(j),q=P(j+1),pe=p.ey||0,qe=q.ey||0;
      const c=(t,o,h)=>[t.x+t.nx*o,h,t.y+t.ny*o];const quad=(arr,A,B,C,D)=>arr.push(...A,...B,...C,...A,...C,...D);
      und.push(...c(p,-W,pe-6),...c(q,-W,qe-6),...c(q,W,qe-6),...c(p,-W,pe-6),...c(q,W,qe-6),...c(p,W,pe-6));
      for(const v of [[p,-W],[q,-W],[q,W],[p,-W],[q,W],[p,W]])uu.push((v[0].x+v[0].nx*v[1])/130,(v[0].y+v[0].ny*v[1])/130);
      for(const sd of [-1,1]){quad(pos,c(p,W*sd,pe-6),c(p,W*sd,pe+.1),c(q,W*sd,qe+.1),c(q,W*sd,qe-6));quad(lin,c(p,(W+.15)*sd,pe-3.6),c(p,(W+.15)*sd,pe-2),c(q,(W+.15)*sd,qe-2),c(q,(W+.15)*sd,qe-3.6));}}
    const mk=(arr,mat,uvs)=>{const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(arr,3));if(uvs)g.setAttribute('uv',new THREE.Float32BufferAttribute(uvs,2));g.computeVertexNormals();const m=new THREE.Mesh(g,mat);m.userData.noLift=true;world.add(m);return m;};
    const sm=mk(pos,slabM);sm.castShadow=true;sm.receiveShadow=true;mk(lin,lineM);mk(und,undM,uu);
    /* columns, except where another road or a shortcut passes underneath */
    for(let j=j0+3;j<j1;j+=7){const p=P(j);if(p.ey<14||inGl(j))continue;let blocked=false;
      for(let i=0;i<N;i+=2){let di=Math.abs(i-j)%N;di=Math.min(di,N-di);if(di<30)continue;const q=track[i];if(p.ey-(q.ey||0)<12)continue;if((q.x-p.x)**2+(q.y-p.y)**2<(WALLD+70)**2){blocked=true;break;}}
      if(blocked)continue;for(const sd of [-1,1]){const x=p.x+p.nx*52*sd,z=p.y+p.ny*52*sd;if(nearSC(x,z,SCW+10)||pitAt(x,z)>.5)continue;const h=p.ey-6;PIL.push({x,y:h/2-.5,z,sy:h+1});RING.push({x,y:h-3,z,sy:1.6});RING.push({x,y:2.2,z,sy:1.6});}}}
  instBatch(new THREE.CylinderGeometry(3,3.6,1,12),new THREE.MeshStandardMaterial({color:'#101c2e',roughness:.3,metalness:.7}),PIL,true);
  instBatch(new THREE.CylinderGeometry(4.1,4.1,1,12),new THREE.MeshBasicMaterial({color:nAcc(def),toneMapped:false}),RING,false);}
/* the floor: a glowing grid out to the horizon, cut open where the glide's shaft drops away */
function neonGridTex(col){const k=new THREE.Color(col),rgb=Math.round(k.r*255)+','+Math.round(k.g*255)+','+Math.round(k.b*255),c=cnv(512,512),g=c.getContext('2d');g.fillStyle='#03060c';g.fillRect(0,0,512,512);
  g.strokeStyle='rgba('+rgb+',.55)';g.lineWidth=3;for(let i=0;i<=512;i+=128){g.beginPath();g.moveTo(i,0);g.lineTo(i,512);g.stroke();g.beginPath();g.moveTo(0,i);g.lineTo(512,i);g.stroke();}
  g.strokeStyle='rgba('+rgb+',.16)';g.lineWidth=1.5;for(let i=0;i<512;i+=32){g.beginPath();g.moveTo(i,0);g.lineTo(i,512);g.stroke();g.beginPath();g.moveTo(0,i);g.lineTo(512,i);g.stroke();}
  const t=new THREE.CanvasTexture(c);t.encoding=THREE.sRGBEncoding;t.wrapS=t.wrapT=THREE.RepeatWrapping;t.anisotropy=8;return t;}
function neonFloor(def){const R=def.R,E=R*2.4,ft=neonGridTex(def.grid||nAcc(def)),fm=new THREE.MeshStandardMaterial({map:ft,emissive:'#ffffff',emissiveMap:ft,emissiveIntensity:.45,roughness:.55,metalness:.4,envMapIntensity:.5,side:THREE.DoubleSide});
  const pos=[],uv=[],G=GLIDE,ux=G?G.ux:1,uy=G?G.uy:0,ox=G?G.p.x:0,oy=G?G.p.y:0,nx=-uy,ny=ux;
  const V=(u,v,y)=>{const x=ox+ux*u+nx*v,z=oy+uy*u+ny*v;pos.push(x,y,z);uv.push(x/260,z/260);};
  const rect=(u0,u1,v0,v1)=>{V(u0,v0,-.4);V(u1,v0,-.4);V(u1,v1,-.4);V(u0,v0,-.4);V(u1,v1,-.4);V(u0,v1,-.4);};
  if(!G)rect(-E,E,-E,E);else{const VW=G.W+70,L=G.L;rect(-E,E,-E,-VW);rect(-E,E,VW,E);rect(-E,0,-VW,VW);rect(L,E,-VW,VW);
    /* the shaft: the same shape the karts fall into (pitAt), drawn as the floor's own grid running down its walls */
    const us=[0,.5,2,4,8];for(let u=20;u<L-8;u+=20)us.push(u);us.push(L-8,L-4,L-2,L-.5,L);const vs=[];for(let v=-VW;v<=VW+.01;v+=VW/14)vs.push(v);
    const Y=(u,v)=>{const x=ox+ux*u+nx*v,z=oy+uy*u+ny*v;return -.4-pitAt(x,z);};
    for(let i=0;i<us.length-1;i++)for(let k=0;k<vs.length-1;k++){const a=[us[i],vs[k]],b=[us[i+1],vs[k]],c=[us[i+1],vs[k+1]],d=[us[i],vs[k+1]];for(const q of [a,b,c,a,c,d])V(q[0],q[1],Y(q[0],q[1]));}}
  const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(pos,3));g.setAttribute('uv',new THREE.Float32BufferAttribute(uv,2));g.computeVertexNormals();
  const fl=new THREE.Mesh(g,fm);fl.receiveShadow=true;fl.userData.noLift=true;world.add(fl);
  if(G){/* light rising from the bottom of the shaft */
    const c=cnv(64,256),x=c.getContext('2d');x.fillStyle='#12041c';x.fillRect(0,0,64,256);for(let i=0;i<26;i++){x.fillStyle=i%3?nAcc2(def):nAcc(def);x.globalAlpha=.25+Math.random()*.6;x.fillRect(Math.random()*60,Math.random()*250,2+Math.random()*3,10+Math.random()*40);}
    const pt=T2(c,(2*G.W)/60,G.L/240),pm=new THREE.MeshBasicMaterial({name:'neonshaft',map:pt,toneMapped:false}),pl=new THREE.Mesh(new THREE.PlaneGeometry(G.L-6,2*G.W-4),pm);
    pl.rotation.set(-Math.PI/2,0,-Math.atan2(G.uy,G.ux));pl.position.set(G.p.x+G.ux*G.L/2,-.4-G.D+.6,G.p.y+G.uy*G.L/2);pl.userData.noLift=true;world.add(pl);animators.push((t,dt)=>{pt.offset.y-=dt*.35;});}
  return fm;}
function neonShoulderTex(def){const c=cnv(128,256),g=c.getContext('2d');g.fillStyle='#070c16';g.fillRect(0,0,128,256);g.strokeStyle='rgba(120,200,230,.16)';g.lineWidth=2;
  for(let y=0;y<256;y+=32){g.beginPath();g.moveTo(0,y);g.lineTo(128,y);g.stroke();}for(let x=0;x<=128;x+=32){g.beginPath();g.moveTo(x,0);g.lineTo(x,256);g.stroke();}
  g.fillStyle=nAcc2(def);g.fillRect(108,0,5,256);return c;}
function buildNeon(def){neonFloor(def);const SJ0=GLIDE?GLIDE.j1:0,SJ1=GLIDE?GLIDE.j0+N:N;
  /* the strip between the road and the wall, and the lines of light along the road's edges */
  for(const sd of [-1,1]){const st=T2(neonShoulderTex(def),1,1),sm=new THREE.MeshStandardMaterial({map:st,emissive:'#ffffff',emissiveMap:st,emissiveIntensity:.8,roughness:.75,metalness:0,envMapIntensity:.15});
    if(sd>0)strip(SJ0,SJ1,RW,WALLD+3,.03,sm,64);else{st.repeat.x=-1;st.offset.x=1;strip(SJ0,SJ1,-WALLD-3,-RW,.03,sm,64);}}
  const nm=new THREE.MeshBasicMaterial({color:nAcc(def),toneMapped:false});strip(SJ0,SJ1,RW-.6,RW+1.4,.08,nm,60);strip(SJ0,SJ1,-RW-1.4,-RW+.6,.08,nm,60);}

/* ---------- scenery: decided by its own random numbers, so it never changes the race's ---------- */
function nRand(seed){let s=Math.floor(seed)%2147483646+1;return ()=>(s=s*48271%2147483647)/2147483647;}
function nGeo(pos,uv,mat,o){const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(pos,3));if(uv)g.setAttribute('uv',new THREE.Float32BufferAttribute(uv,2));g.computeVertexNormals();
  const m=new THREE.Mesh(g,mat);m.userData.noLift=true;m.castShadow=!!(o&&o.cast);m.receiveShadow=!!(o&&o.recv);if(o&&o.ro)m.renderOrder=o.ro;world.add(m);return m;}
/* is (x,z) in the glide's corridor: along the shaft and its landing run, with room to the sides */
function nGlideNear(x,z,side){const G=GLIDE;if(!G)return false;const dx=x-G.p.x,dz=z-G.p.y,u=dx*G.ux+dz*G.uy,v=Math.abs(dz*G.ux-dx*G.uy);return u>-260&&u<G.L+700&&v<G.W+side;}
/* is another stretch of road (not the one at point j) close to (x,z)? */
function nRoadNear(x,z,j,th){const t2=th*th;for(let i=0;i<N;i+=2){let d=Math.abs(i-j)%N;d=Math.min(d,N-d);if(d<40)continue;const q=track[i];if((q.x-x)**2+(q.y-z)**2<t2)return true;}return false;}
/* a box (four walls and a roof) with the wall texture laid out in world units, so windows are the same size on every building */
function nBox(P,U,x,z,w,d,y0,y1,rot,us,vs){const c=Math.cos(rot),s=Math.sin(rot),K=[[-w/2,-d/2],[w/2,-d/2],[w/2,d/2],[-w/2,d/2]].map(([a,b])=>[x+a*c-b*s,z+a*s+b*c]);
  for(let i=0;i<4;i++){const A=K[i],B=K[(i+1)%4],L=i%2?d:w,u1=Math.max(1,Math.round(L/us*8))/8,v0=Math.round(y0/vs*32)/32,v1=v0+Math.max(1,Math.round((y1-y0)/vs*32))/32;
    P.push(A[0],y0,A[1],B[0],y0,B[1],B[0],y1,B[1],A[0],y0,A[1],B[0],y1,B[1],A[0],y1,A[1]);U.push(0,v0,u1,v0,u1,v1,0,v0,u1,v1,0,v1);}
  P.push(K[0][0],y1,K[0][1],K[2][0],y1,K[2][1],K[1][0],y1,K[1][1],K[0][0],y1,K[0][1],K[3][0],y1,K[3][1],K[2][0],y1,K[2][1]);for(let i=0;i<6;i++)U.push(.004,.002);}
/* a band of light round a box */
function nRim(P,x,z,w,d,y0,y1,rot){const c=Math.cos(rot),s=Math.sin(rot),K=[[-w/2,-d/2],[w/2,-d/2],[w/2,d/2],[-w/2,d/2]].map(([a,b])=>[x+a*c-b*s,z+a*s+b*c]);
  for(let i=0;i<4;i++){const A=K[i],B=K[(i+1)%4];P.push(A[0],y0,A[1],B[0],y0,B[1],B[0],y1,B[1],A[0],y0,A[1],B[0],y1,B[1],A[0],y1,A[1]);}}
function neonWinTex(cols,seed){const r=nRand(seed),c=cnv(256,512),g=c.getContext('2d');g.fillStyle='#050912';g.fillRect(0,0,256,512);const main=cols[Math.floor(r()*cols.length)];
  for(let y=0;y<32;y++){const band=r()<.06,dark=r()<.3;for(let x=0;x<8;x++){const lit=!dark&&(band||r()<.24);g.globalAlpha=1;if(!lit){g.fillStyle='#09101d';g.fillRect(x*32+6,y*16+4,20,8);continue;}
    g.fillStyle=band||r()<.72?main:cols[Math.floor(r()*cols.length)];g.globalAlpha=.45+r()*.5;g.fillRect(x*32+6,y*16+4,20,8);}}g.globalAlpha=1;return c;}
/* buildings of light: a skyline beyond the edge of the arena and, where there is room, lower blocks inside the lap */
function neonCity(def,o){const r=nRand(def.R*7+o.seed),R=def.R,P=[[],[],[]],U=[[],[],[]],L1=[],L2=[],AN=[],AL=[];
  const mats=[0,1,2].map(i=>{const t=T2(neonWinTex(o.cols,o.seed+i*31),1,1);return new THREE.MeshStandardMaterial({map:t,emissive:'#ffffff',emissiveMap:t,emissiveIntensity:o.glow||.9,roughness:.45,metalness:.35,envMapIntensity:.4,side:THREE.DoubleSide});});
  const add=(x,z,w,d,h,rot)=>{const k=Math.floor(r()*3),h1=h*(.5+r()*.2),w2=w*(.55+r()*.25),d2=d*(.55+r()*.25);nBox(P[k],U[k],x,z,w,d,-2,h1,rot,112,224);nBox(P[k],U[k],x,z,w2,d2,h1,h,rot,112,224);
    nRim(L1,x,z,w+1.6,d+1.6,h1-2.6,h1+.3,rot);nRim(r()<.5?L1:L2,x,z,w2+1.6,d2+1.6,h-2.6,h+.3,rot);if(h>260&&r()<.6){const ah=40+r()*90;AN.push({x,y:h+ah/2,z,sy:ah});AL.push({x,y:h+ah,z});}};
  for(let i=0;i<o.far;i++){const a=r()*6.283,rad=R+150+Math.pow(r(),1.3)*1700,w=90+r()*170,d=90+r()*170,h=(200+r()*r()*950)*(o.hk||1);add(Math.cos(a)*rad,Math.sin(a)*rad,w,d,h,r()*1.57);}
  if(o.near)for(let x=-R+200;x<R-200;x+=230)for(let z=-R+200;z<R-200;z+=230){if(r()>o.near)continue;const px=x+(r()-.5)*90,pz=z+(r()-.5)*90;if(Math.hypot(px,pz)>R-150)continue;
    const dd=minTrackDist(px,pz);if(dd<310||nGlideNear(px,pz,330)||nearSC(px,pz,170))continue;const w=70+r()*90,d=70+r()*90;add(px,pz,w,d,(46+r()*Math.min(230,(dd-250)*.6))*(o.hk||1),r()<.6?0:r()*1.57);}
  for(let k=0;k<3;k++)if(P[k].length)nGeo(P[k],U[k],mats[k],{cast:false,recv:false});
  const l1=new THREE.MeshBasicMaterial({color:nAcc(def),toneMapped:false,side:THREE.DoubleSide}),l2=new THREE.MeshBasicMaterial({color:nAcc2(def),toneMapped:false,side:THREE.DoubleSide});
  if(L1.length)nGeo(L1,null,l1);if(L2.length)nGeo(L2,null,l2);
  instBatch(new THREE.CylinderGeometry(.6,1.6,1,6),new THREE.MeshStandardMaterial({color:'#0c1420',roughness:.4,metalness:.7}),AN,false);
  instBatch(new THREE.SphereGeometry(3.2,10,8),new THREE.MeshBasicMaterial({color:'#ff3b3b',toneMapped:false}),AL,false);}
/* slim posts with a blade of light, along both sides of the road */
function neonPylons(def){const post=[],b1=[],b2=[];let n=0;for(let j=6;j<N;j+=12){if(nInGl(j,10,6))continue;const p=track[j],sd=(n++%2)?1:-1,ey=p.ey||0,deck=ey>1.5,o=(deck?WALLD+1.3:WALLD+8)*sd,x=p.x+p.nx*o,z=p.y+p.ny*o,y0=deck?ey+4.6:0;
    if(!deck&&(nRoadNear(x,z,j,WALLD+14)||nearSC(x,z,SCW+10)||pitAt(x,z)>.5))continue;post.push({x,y:y0+10,z,sy:20});(n%4<2?b1:b2).push({x,y:y0+16.5,z,ry:-p.ang});}
  instBatch(new THREE.CylinderGeometry(.5,.95,1,8),new THREE.MeshStandardMaterial({color:'#0d1626',roughness:.35,metalness:.7}),post,true);
  const bg=()=>new THREE.BoxGeometry(2.6,11,.7);instBatch(bg(),new THREE.MeshBasicMaterial({color:nAcc(def),toneMapped:false}),b1,false);instBatch(bg(),new THREE.MeshBasicMaterial({color:nAcc2(def),toneMapped:false}),b2,false);}
/* hoops of light over the straights */
function neonGates(def){const cdj=(a,b)=>{const d=Math.abs(a-b)%N;return Math.min(d,N-d);},hoop=[],hoop2=[],feet=[];let last=-999,n=0;
  for(let j=40;j<N-30;j++){if(j-last<150)continue;const p=track[j];let ok=true;for(let o=-14;o<=14;o+=2)if(Math.abs(track[(j+o+N)%N].bend)>.1){ok=false;break;}if(!ok||nInGl(j,40,110))continue;
    if(ramps.some(r=>cdj(r.j,j)<26)||pads.some(q=>cdj(q.j,j)<8)||SHORTS.some(sc=>cdj(sc.a,j)<24||cdj(sc.b,j)<24)||cdj(j,0)<60)continue;const ey=p.ey||0,deck=ey>1.5,rad=deck?WALLD+1.3:WALLD+9;
    if(!deck&&(nRoadNear(p.x,p.y,j,2*WALLD+60)))continue;if(deck&&Math.abs((track[(j+10)%N].ey||0)-ey)>1.5)continue;last=j;const it={x:p.x,y:deck?ey+4.6:0,z:p.y,ry:-p.ang-Math.PI/2,sx:rad/100,sy:rad/100,sz:1};(n++%2?hoop2:hoop).push(it);
    for(const sd of [-1,1])feet.push({x:p.x+p.nx*rad*sd,y:(deck?ey+4.6:0)+3,z:p.y+p.ny*rad*sd,ry:-p.ang,sy:6});}
  const tg=()=>new THREE.TorusGeometry(100,1.5,8,56,Math.PI);instBatch(tg(),new THREE.MeshBasicMaterial({color:nAcc(def),toneMapped:false}),hoop,false);instBatch(tg(),new THREE.MeshBasicMaterial({color:nAcc2(def),toneMapped:false}),hoop2,false);
  instBatch(new THREE.BoxGeometry(5,1,5),new THREE.MeshStandardMaterial({color:'#0d1626',roughness:.35,metalness:.7}),feet,true);}
/* stars and a glow along the horizon */
function neonSky(def){const r=nRand(def.R+77),n=1400,pos=new Float32Array(n*3);for(let i=0;i<n;i++){const a=r()*6.283,e=Math.asin(.04+r()*.96),D=15000;pos[i*3]=Math.cos(a)*Math.cos(e)*D;pos[i*3+1]=Math.sin(e)*D;pos[i*3+2]=Math.sin(a)*Math.cos(e)*D;}
  const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.BufferAttribute(pos,3));const st=new THREE.Points(g,new THREE.PointsMaterial({color:'#dfe8ff',size:1.6,sizeAttenuation:false,fog:false,toneMapped:false,transparent:true,opacity:.85,depthWrite:false}));st.userData.noLift=true;st.frustumCulled=false;world.add(st);
  const c=cnv(8,128),x=c.getContext('2d'),gr=x.createLinearGradient(0,128,0,0),k=new THREE.Color(def.haze||nAcc2(def)),rgb=Math.round(k.r*255)+','+Math.round(k.g*255)+','+Math.round(k.b*255);gr.addColorStop(0,'rgba('+rgb+',.55)');gr.addColorStop(.35,'rgba('+rgb+',.16)');gr.addColorStop(1,'rgba('+rgb+',0)');x.fillStyle=gr;x.fillRect(0,0,8,128);
  const hz=new THREE.Mesh(new THREE.CylinderGeometry(def.R*2.6,def.R*2.6,900,64,1,true),new THREE.MeshBasicMaterial({name:'neonhaze',map:T2(c),transparent:true,side:THREE.BackSide,depthWrite:false,fog:false,toneMapped:false}));hz.position.y=448;hz.userData.noLift=true;hz.renderOrder=-1;world.add(hz);}
/* Laser Slice Skyway: searchlights sweeping from the tallest towers */
function neonLasers(def){const r=nRand(def.R+5),R=def.R,m=new THREE.MeshBasicMaterial({name:'neonadd',color:nAcc2(def),transparent:true,opacity:.34,depthWrite:false,blending:THREE.AdditiveBlending,side:THREE.DoubleSide,fog:false,toneMapped:false}),m2=m.clone();m2.color.set(nAcc(def));
  for(let i=0;i<7;i++){const a=i/7*6.283+r()*.5,rad=R+300+r()*500,G=new THREE.Group();G.position.set(Math.cos(a)*rad,300+r()*300,Math.sin(a)*rad);G.userData.noLift=true;world.add(G);
    const b=new THREE.Mesh(new THREE.PlaneGeometry(9,5200),i%2?m:m2);b.position.y=2600;const piv=new THREE.Group();piv.add(b);const b2=b.clone();b2.rotation.y=Math.PI/2;piv.add(b2);piv.rotation.z=.5+r()*.5;G.add(piv);const sp=.05+r()*.07,ph=r()*6;G.rotation.y=ph;animators.push((t)=>{G.rotation.y=ph+t*sp;piv.rotation.z=.75+Math.sin(t*.21+ph)*.3;});}}
/* Hologram Heights: a giant pizza of light turning above the middle of the tower */
function neonHologram(def){const C=def.holoC;if(!C)return;const x=C[0],z=C[1],a1=nAcc(def),a2=nAcc2(def);
  const c=cnv(512,512),g=c.getContext('2d');g.translate(256,256);g.strokeStyle=a1;g.lineWidth=10;g.beginPath();g.arc(0,0,244,0,7);g.stroke();g.lineWidth=5;g.beginPath();g.arc(0,0,214,0,7);g.stroke();
  g.lineWidth=4;for(let i=0;i<8;i++){const a=i*Math.PI/4;g.beginPath();g.moveTo(0,0);g.lineTo(Math.cos(a)*214,Math.sin(a)*214);g.stroke();}
  g.strokeStyle=a2;g.fillStyle=a2;g.lineWidth=5;const r=nRand(41);for(let i=0;i<8;i++)for(let k=0;k<2;k++){const a=i*Math.PI/4+.2+r()*.38,d=70+k*78+r()*22,px=Math.cos(a)*d,py=Math.sin(a)*d;g.beginPath();g.arc(px,py,17+r()*5,0,7);g.globalAlpha=.3;g.fill();g.globalAlpha=1;g.stroke();}
  const t=T2(c),pm=new THREE.MeshBasicMaterial({name:'neonholo',map:t,transparent:true,opacity:.9,side:THREE.DoubleSide,depthWrite:false,blending:THREE.AdditiveBlending,fog:false,toneMapped:false});
  const G=new THREE.Group();G.position.set(x,0,z);G.userData.noLift=true;world.add(G);
  const tilt=new THREE.Group();tilt.position.y=330;tilt.rotation.z=.38;G.add(tilt);const disc=new THREE.Mesh(new THREE.CircleGeometry(165,64),pm);disc.rotation.x=-Math.PI/2;tilt.add(disc);const d2=disc.clone();d2.position.y=-9;d2.scale.setScalar(.985);tilt.add(d2);
  const rm=new THREE.MeshBasicMaterial({name:'neonadd',color:a2,transparent:true,opacity:.8,blending:THREE.AdditiveBlending,depthWrite:false,fog:false,toneMapped:false}),rings=[];
  for(const [rad,ty,tx] of [[196,.5,.9],[214,-.7,.35],[232,.2,-.6]]){const ring=new THREE.Mesh(new THREE.TorusGeometry(rad,1.6,8,96),rm);ring.rotation.set(Math.PI/2+tx,0,ty);ring.position.y=330;G.add(ring);rings.push(ring);}
  /* the projector: a dark drum with bands of light, and the beam it throws */
  const drum=wm('#0c1524',{metalness:.7,roughness:.3});put(new THREE.CylinderGeometry(58,70,16,40),drum,0,8,0,G);put(new THREE.CylinderGeometry(40,52,12,40),drum,0,22,0,G);
  const gl=new THREE.MeshBasicMaterial({color:a1,toneMapped:false});put(new THREE.TorusGeometry(64,1.4,8,64),gl,0,16.5,0,G,false).rotation.x=Math.PI/2;put(new THREE.TorusGeometry(46,1.4,8,64),gl,0,28.5,0,G,false).rotation.x=Math.PI/2;
  const bc=cnv(8,128),bx=bc.getContext('2d'),bg=bx.createLinearGradient(0,128,0,0);bg.addColorStop(0,'rgba(255,255,255,.75)');bg.addColorStop(.5,'rgba(255,255,255,.22)');bg.addColorStop(1,'rgba(255,255,255,0)');bx.fillStyle=bg;bx.fillRect(0,0,8,128);
  const beam=new THREE.Mesh(new THREE.CylinderGeometry(150,34,300,40,1,true),new THREE.MeshBasicMaterial({name:'neonadd',map:T2(bc),color:a1,transparent:true,opacity:.22,side:THREE.DoubleSide,depthWrite:false,blending:THREE.AdditiveBlending,fog:false,toneMapped:false}));beam.position.y=178;G.add(beam);
  animators.push((tt,dt)=>{tilt.rotation.y+=dt*.35;rings.forEach((q,i)=>{q.rotation.z+=dt*(.25+i*.12)*(i%2?-1:1);});pm.opacity=.78+Math.sin(tt*3.1)*.12;});
  /* cubes of light drifting round the tower */
  const cr=nRand(97),cubes=[],cubes2=[];for(let i=0;i<46;i++){const a=cr()*6.283,d=820+cr()*900,s=10+cr()*26,cx=x+Math.cos(a)*d,cz=z+Math.sin(a)*d;if(Math.hypot(cx,cz)>def.R-120||minTrackDist(cx,cz)<200&&cr()<2||nGlideNear(cx,cz,300))continue;(i%2?cubes:cubes2).push({x:cx,y:150+cr()*330,z:cz,ry:cr()*3,sx:s,sy:s,sz:s});}
  const wire=col=>{const cc=cnv(64,64),q=cc.getContext('2d');q.fillStyle='rgba(8,14,26,.55)';q.fillRect(0,0,64,64);q.strokeStyle=col;q.lineWidth=7;q.strokeRect(2,2,60,60);const tx=T2(cc);return new THREE.MeshBasicMaterial({map:tx,transparent:true,side:THREE.DoubleSide,depthWrite:false,toneMapped:false});};
  instBatch(new THREE.BoxGeometry(1,1,1),wire(a1),cubes,false);instBatch(new THREE.BoxGeometry(1,1,1),wire(a2),cubes2,false);}
/* Synthwave Supreme: a striped sun on the horizon the glide flies toward, ridges of light round the horizon and palms along the road */
function neonSun(def){const R=def.R,G=def.nglide,j0=Math.round(G[0]*N)%N,j1=Math.round((G[0]+G[1]/T.L)*N)%N,pa=curRev?track[(N-j0)%N]:track[j0],pb=curRev?track[(N-j1)%N]:track[j1];let ux=pb.x-pa.x,uz=pb.y-pa.y;const l=Math.hypot(ux,uz)||1;ux/=l;uz/=l;
  const c=cnv(1024,768),g=c.getContext('2d'),cx=512,cy=520,rad=330;const halo=g.createRadialGradient(cx,cy,rad*.9,cx,cy,rad*1.5);halo.addColorStop(0,'rgba(255,90,160,.5)');halo.addColorStop(1,'rgba(255,90,160,0)');g.fillStyle=halo;g.fillRect(0,0,1024,768);
  g.save();g.beginPath();g.arc(cx,cy,rad,0,7);g.clip();const gr=g.createLinearGradient(0,cy-rad,0,cy+rad*.45);gr.addColorStop(0,'#fff27a');gr.addColorStop(.45,'#ff9a3d');gr.addColorStop(1,'#ff2d95');g.fillStyle=gr;g.fillRect(0,0,1024,768);
  g.globalCompositeOperation='destination-out';for(let i=0;i<9;i++){const y=cy-rad*.2+i*i*3.6+i*19,h=4+i*2.6;g.fillRect(0,y,1024,h);}g.restore();
  const t=T2(c),W=5200,H=W*768/1024,sun=new THREE.Mesh(new THREE.PlaneGeometry(W,H),new THREE.MeshBasicMaterial({name:'neonsun',map:t,transparent:true,depthWrite:false,fog:false,toneMapped:false}));
  const D=R*2.9;sun.position.set(ux*D,H/2-H*(768-cy-rad*.42)/768,uz*D);sun.lookAt(0,sun.position.y,0);sun.userData.noLift=true;sun.renderOrder=-2;world.add(sun);
  /* ridges: two rings of jagged peaks, dark with their edges drawn in light */
  const r=nRand(R+3);for(const [rad2,hk,col,seed] of [[R*2.35,1,nAcc(def),1],[R*2.75,1.7,nAcc2(def),2]]){const n=150,fill=[],line=[],hs=[];let h=150;for(let i=0;i<=n;i++){h=Math.max(40,Math.min(520,h+(r()-.5)*230));hs.push((i%3===0?h*1.25:h*.7)*hk);}hs[n]=hs[0];
    const pt=(i,y)=>{const a=i/n*6.283;return [Math.cos(a)*rad2,y,Math.sin(a)*rad2];},T=5*hk;
    for(let i=0;i<n;i++){const a0=pt(i,-4),a1=pt(i,hs[i]),b0=pt(i+1,-4),b1=pt(i+1,hs[i+1]);fill.push(...a0,...b0,...b1,...a0,...b1,...a1);const u0=pt(i,hs[i]+T),u1=pt(i+1,hs[i+1]+T);line.push(...a1,...b1,...u1,...a1,...u1,...u0);
      if(i%3===0){const m0=pt(i+.12,-4),m1=pt(i+.12,hs[i]);line.push(...a0,...m0,...m1,...a0,...m1,...a1);}}
    nGeo(fill,null,new THREE.MeshBasicMaterial({name:'neonfar',color:'#0a0618',side:THREE.DoubleSide,fog:false,toneMapped:false}),{ro:-1});nGeo(line,null,new THREE.MeshBasicMaterial({name:'neonfar',color:col,side:THREE.DoubleSide,fog:false,toneMapped:false}),{ro:-1});}}
function neonPalms(def){/* one palm: a leaning trunk in rings of light and a crown of drooping fronds */
  const P=[],C=[],k1=new THREE.Color(nAcc2(def)),k2=new THREE.Color(nAcc(def)),kd=new THREE.Color('#1a0a2a');const tri=(a,b,c,k)=>{P.push(...a,...b,...c);for(let i=0;i<3;i++)C.push(k.r,k.g,k.b);},quad=(a,b,c,d,k)=>{tri(a,b,c,k);tri(a,c,d,k);};
  const H=34,seg=9,tp=i=>{const f=i/seg;return [f*f*5,f*H,0,1.5-f*.7];};for(let i=0;i<seg;i++){const A=tp(i),B=tp(i+1);for(let s=0;s<6;s++){const a0=s/6*6.283,a1=(s+1)/6*6.283,v=(q,a)=>[q[0]+Math.cos(a)*q[3],q[1],q[2]+Math.sin(a)*q[3]];quad(v(A,a0),v(A,a1),v(B,a1),v(B,a0),i%3===2?k1:kd);}}
  const top=tp(seg);for(let f=0;f<9;f++){const a=f/9*6.283+.2,L=22,n=6,dx=Math.cos(a),dz=Math.sin(a),px=-dz,pz=dx;let prev=null;for(let i=0;i<=n;i++){const u=i/n,d=u*L,y=top[1]+Math.sin(u*2.6)*7-u*u*13,w=(1-u*.85)*2.6,c0=[top[0]+dx*d-px*w,y,dz*d-pz*w],c1=[top[0]+dx*d+px*w,y,dz*d+pz*w];if(prev)quad(prev[0],prev[1],c1,c0,f%2?k2:k1);prev=[c0,c1];}}
  const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(P,3));g.setAttribute('color',new THREE.Float32BufferAttribute(C,3));g.computeVertexNormals();
  const list=[],r=nRand(def.R+9);let n=0;for(let j=3;j<N;j+=9){if(nInGl(j,14,10))continue;const p=track[j];if((p.ey||0)>1.5||Math.abs(p.bend)>.5)continue;const sd=(n++%2)?1:-1,o=(WALLD+20+r()*10)*sd,x=p.x+p.nx*o,z=p.y+p.ny*o;if(nRoadNear(x,z,j,WALLD+30)||nearSC(x,z,SCW+18)||pitAt(x,z)>.5)continue;const s=.9+r()*.5;list.push({x,y:0,z,ry:r()*6.283,sx:s,sy:s,sz:s});}
  instBatch(g,new THREE.MeshBasicMaterial({vertexColors:true,side:THREE.DoubleSide,toneMapped:false}),list,false);}
/* arrows of light running round the outside of every real corner, on top of the wall */
function neonChevrons(def){const pos=[],uv=[],H0=5.4,H1=13.4,o=WALLD+1.3;let run=0;
  for(let j=0;j<N;j++){const p=track[j],q=track[(j+1)%N],b=p.bend;if(Math.abs(b)<.34||Math.sign(q.bend)!==Math.sign(b)||nInGl(j,6,6)||p.open||q.open){run=0;continue;}const sd=-Math.sign(b);
    if(SHORTS.some(sc=>sc.s===sd&&[sc.a,sc.b].some(e=>{const d=Math.abs(j-e)%N;return Math.min(d,N-d)<=5;}))){run=0;continue;}
    const A=[p.x+p.nx*o*sd,p.y+p.ny*o*sd,p.ey||0],B=[q.x+q.nx*o*sd,q.y+q.ny*o*sd,q.ey||0],L=Math.hypot(B[0]-A[0],B[1]-A[1]),v0=run/16,v1=(run+L)/16;run+=L;
    pos.push(A[0],A[2]+H0,A[1],B[0],B[2]+H0,B[1],B[0],B[2]+H1,B[1],A[0],A[2]+H0,A[1],B[0],B[2]+H1,B[1],A[0],A[2]+H1,A[1]);uv.push(0,v0,0,v1,1,v1,0,v0,1,v1,1,v0);}
  if(!pos.length)return;const t=T2(neonLaneTex(def),1,1),m=new THREE.MeshBasicMaterial({name:'neonlane',map:t,side:THREE.DoubleSide,toneMapped:false,transparent:true,opacity:.92});nGeo(pos,uv,m);animators.push((tt,dt)=>{t.offset.y-=dt*1.4;});}
/* signs of light beside the straights */
function neonSignTex(def,k){const c=cnv(512,224),g=c.getContext('2d'),a1=nAcc(def),a2=nAcc2(def);g.fillStyle='#060b16';g.fillRect(0,0,512,224);g.strokeStyle=a1;g.lineWidth=8;g.strokeRect(8,8,496,208);g.textAlign='center';g.textBaseline='middle';
  if(k===0){g.fillStyle=a2;g.font='900 84px "Arial Black",Impact,sans-serif';g.fillText('CRUST',256,78);g.fillStyle=a1;g.fillText('RUSH',256,154);}
  else if(k===1){g.strokeStyle=a2;g.lineWidth=20;g.lineJoin='miter';for(let i=0;i<4;i++){const x=70+i*110;g.globalAlpha=.4+i*.2;g.beginPath();g.moveTo(x,50);g.lineTo(x+62,112);g.lineTo(x,174);g.stroke();}g.globalAlpha=1;}
  else{/* a slice of pizza drawn in light */g.strokeStyle=a2;g.lineWidth=9;g.lineJoin='round';g.beginPath();g.moveTo(90,40);g.lineTo(210,184);g.lineTo(60,150);g.closePath();g.stroke();g.fillStyle=a2;for(const [x,y] of [[112,92],[150,150],[98,138]]){g.beginPath();g.arc(x,y,10,0,7);g.fill();}
    g.fillStyle=a1;g.font='900 60px "Arial Black",Impact,sans-serif';g.fillText('NEON',356,84);g.fillText('CUP',356,150);}
  return c;}
function neonSigns(def){const cdj=(a,b)=>{const d=Math.abs(a-b)%N;return Math.min(d,N-d);},posts=[],panels=[[],[],[]],backs=[];let last=-999,n=0;
  for(let j=70;j<N-40;j++){if(j-last<120)continue;const p=track[j];if((p.ey||0)>1.5||nInGl(j,30,110))continue;let ok=true;for(let o=-10;o<=10;o+=2)if(Math.abs(track[(j+o+N)%N].bend)>.12){ok=false;break;}if(!ok)continue;
    const sd=(n%2)?1:-1,o=(WALLD+44)*sd,x=p.x+p.nx*o,z=p.y+p.ny*o;if(nRoadNear(x,z,j,WALLD+70)||nearSC(x,z,SCW+50)||nGlideNear(x,z,120)||Math.hypot(x,z)>def.R-120)continue;last=j;const ry=-p.ang+Math.PI/2+sd*.28;
    panels[n%3].push({x,y:33,z,ry});backs.push({x:x+p.tx*1.2,y:33,z:z+p.ty*1.2,ry,sx:1.03,sy:1.06});for(const e of [-17,17])posts.push({x:x+p.nx*e*Math.cos(.28)*1+0,y:11.5,z:z+p.ny*e,sy:23});n++;}
  for(let k=0;k<3;k++){const t=T2(neonSignTex(def,k));instBatch(new THREE.BoxGeometry(48,21,.8),new THREE.MeshBasicMaterial({map:t,toneMapped:false}),panels[k],false);}
  instBatch(new THREE.BoxGeometry(48,21,1.4),new THREE.MeshStandardMaterial({color:'#0a1220',roughness:.4,metalness:.6}),backs,true);
  instBatch(new THREE.CylinderGeometry(.7,1,1,8),new THREE.MeshStandardMaterial({color:'#0d1626',roughness:.35,metalness:.7}),posts,true);}
/* grandstands of light either side of the start line */
function neonStands(def){const P=[],U=[],RP=[],L=[],r=nRand(def.R+21),c=cnv(256,128),g=c.getContext('2d');g.fillStyle='#070c18';g.fillRect(0,0,256,128);const cols=[nAcc(def),nAcc2(def),'#ffffff','#ffd24a'];
  for(let y=0;y<8;y++)for(let x=0;x<32;x++){if(r()<.2)continue;g.fillStyle=cols[Math.floor(r()*4)];g.globalAlpha=.35+r()*.65;g.fillRect(x*8+2,y*16+4,4,7);}g.globalAlpha=1;g.fillStyle='rgba(120,200,230,.25)';for(let y=0;y<8;y++)g.fillRect(0,y*16,256,1.5);
  const j0=N-26,j1=22,D0=WALLD+26,D1=WALLD+74,H=30;
  for(const sd of [-1,1]){let ok=true;for(let j=j0;j<=N+j1;j+=6){const p=track[j%N];if(nRoadNear(p.x+p.nx*D1*sd,p.y+p.ny*D1*sd,j%N,WALLD+30)||Math.abs(p.bend)>.12)ok=false;}if(!ok)continue;
    for(let j=j0;j<N+j1;j++){const p=track[j%N],q=track[(j+1)%N],at=(t,d,y)=>[t.x+t.nx*d*sd,y,t.y+t.ny*d*sd],u0=(j-j0)/8,u1=(j+1-j0)/8;
      const a=at(p,D0,5),b=at(q,D0,5),c2=at(q,D1,H),d=at(p,D1,H);P.push(...a,...b,...c2,...a,...c2,...d);U.push(u0,0,u1,0,u1,1,u0,0,u1,1,u0,1);
      const quad=(arr,A,B,C,D2)=>arr.push(...A,...B,...C,...A,...C,...D2);quad(RP,at(p,D0,0),at(q,D0,0),b,a);quad(RP,at(p,D1,0),at(q,D1,0),c2,d);quad(RP,at(p,D0-6,H+16),at(q,D0-6,H+16),at(q,D1+2,H+22),at(p,D1+2,H+22));
      quad(L,at(p,D0-6.2,H+15.2),at(q,D0-6.2,H+15.2),at(q,D0-6.2,H+17),at(p,D0-6.2,H+17));quad(L,at(p,D0-.2,4.2),at(q,D0-.2,4.2),at(q,D0-.2,5.4),at(p,D0-.2,5.4));}
    const posts=[];for(let j=j0;j<=N+j1;j+=8){const p=track[j%N];posts.push({x:p.x+p.nx*(D1+1)*sd,y:(H+22)/2,z:p.y+p.ny*(D1+1)*sd,sy:H+22});}instBatch(new THREE.CylinderGeometry(.9,1.2,1,8),new THREE.MeshStandardMaterial({color:'#0d1626',roughness:.35,metalness:.7}),posts,true);}
  if(!P.length)return;const t=T2(c,1,1);nGeo(P,U,new THREE.MeshStandardMaterial({map:t,emissive:'#ffffff',emissiveMap:t,emissiveIntensity:.9,roughness:.6,metalness:.2,side:THREE.DoubleSide}),{recv:true});
  nGeo(RP,null,new THREE.MeshStandardMaterial({color:'#0b1422',roughness:.4,metalness:.6,side:THREE.DoubleSide}),{cast:true,recv:true});nGeo(L,null,new THREE.MeshBasicMaterial({color:nAcc(def),toneMapped:false,side:THREE.DoubleSide}));}
function neonScenery(def){neonSky(def);neonPylons(def);neonChevrons(def);neonSigns(def);neonStands(def);
  if(def.look==='city'){neonCity(def,{seed:11,far:150,near:.62,cols:['#3ff0ff','#ff3fd8','#ffffff','#8fb8ff','#ffd24a']});neonLasers(def);}
  else if(def.look==='holo'){neonCity(def,{seed:23,far:70,near:.2,hk:.8,cols:['#4dffb8','#b56bff','#ffffff','#7fe8ff']});neonHologram(def);}
  else if(def.look==='sun'){neonCity(def,{seed:37,far:46,near:0,hk:.55,cols:['#ff5fa2','#ffb43f','#b56bff','#ffffff']});neonSun(def);neonPalms(def);}}
