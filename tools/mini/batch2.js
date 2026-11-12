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
M.bed=function(o){o=o||{};const G=grp(),W=152*U,L=203*U,leg=28*U,rail=9*U,mh=24*U,oak=wood('oak','#b98a58','#5a3a1c',{rough:.5}),top=leg+rail;
  for(const sx of [-1,1])for(const sz of [-1,1]){const lg=add(G,cyl(3.2*U,2.2*U,leg,14),oak,sx*(W/2-5*U),leg/2,sz*(L/2-5*U));lg.userData.leg=1;}
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
  const dw=W/2-2.4*U,dh=(H-leg-3*U)/3-1*U;for(let c=0;c<2;c++)for(let r=0;r<3;r++){const x=(c-.5)*(W/2-.6*U),y=leg+.9*U+dh/2+r*(dh+.9*U);add(G,slab(dw,dh,1.8*U,.7*U,.35*U,3),body,x,y,D/2+.4*U,Math.PI/2);
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
  const nt=T2(heightToNormal(hc,1.5),6,9,true);add(G,g2,mat('rug',()=>std({map:tex(c,'rug'),normalMap:nt,normalScale:new THREE.Vector2(.7,.7),roughness:1,envMapIntensity:.15})),0,.6*U,0);return G;};
/* ============ shoes ============ */
/* one sneaker, 29 cm long: a rubber sole with a sidewall, an upper lofted from cross-sections, a toe cap, a tongue and laces. Toe at +z. */
M.sneaker=function(o){o=o||{};const G=grp(),L=29*U,col=o.color||'#f4f4f2',up=fabric('sneak'+col,col,{ws:2,ns:.6,rough:.8}),rub=plastic('sole','#f0eee8',.7),acc=plastic('sneakacc',o.accent||'#e0452c',.55);
  /* width of the foot along its length (0 heel .. 1 toe) */
  const wid=t=>(3.1+2.3*Math.sin(Math.min(1,t*1.25)*Math.PI*.62)+1.0*Math.sin(t*Math.PI))*U*(t>.93?1-(t-.93)*6:1),zOf=t=>(t-.5)*L;
  const sole=new THREE.Shape(),N=28;for(let i=0;i<=N;i++){const t=i/N;sole[i?'lineTo':'moveTo'](wid(t),zOf(t));}for(let i=N;i>=0;i--){const t=i/N;sole.lineTo(-wid(t),zOf(t));}
  const sg=new THREE.ExtrudeGeometry(sole,{depth:2.6*U,bevelEnabled:true,bevelThickness:.5*U,bevelSize:.45*U,bevelSegments:3,curveSegments:4});sg.rotateX(Math.PI/2);sg.translate(0,3.1*U,0);add(G,sg,rub);
  add(G,(()=>{const g=new THREE.ExtrudeGeometry(sole,{depth:.5*U,bevelEnabled:false});g.rotateX(Math.PI/2);g.translate(0,.5*U,0);g.scale(.96,1,.97);return g;})(),plastic('tread','#3a3d44',.9));
  /* the upper: half-ellipse hoops along the foot, taller toward the ankle, open at the collar */
  const P=[],I=[],UV=[],S=12,hgt=t=>(t<.18?10.5-(t/.18)*.3:t<.55?10.2-(t-.18)/.37*4.4:5.8-(t-.55)/.45*2.6)*U,st=20;
  for(let i=0;i<=st;i++){const t=i/st,w=wid(t)*.96,h=hgt(t)-3*U,open=t<.5?Math.max(0,1-t/.5):0;for(let k=0;k<=S;k++){const a=k/S*Math.PI,c=Math.cos(a),s=Math.sin(a),flat=open*.55;let x=c*w*(1-flat*.25*s),y=3*U+Math.pow(s,.75)*h;
      if(open>0&&s>.72)y-= (s-.72)/.28*h*.16*open; /* the collar dips where the foot goes in */P.push(x,y,zOf(t));UV.push(k/S*2,t*4);}}
  for(let i=0;i<st;i++)for(let k=0;k<S;k++){const a=i*(S+1)+k,b=a+1,c=a+S+1,e=c+1;I.push(a,b,c,b,e,c);}
  const ug=new THREE.BufferGeometry();ug.setAttribute('position',new THREE.Float32BufferAttribute(P,3));ug.setAttribute('uv',new THREE.Float32BufferAttribute(UV,2));ug.setIndex(I);ug.computeVertexNormals();const um=add(G,ug,up);um.material.side=THREE.DoubleSide;
  /* heel counter and toe cap in the accent colour, the tongue, and five laces across the instep */
  add(G,blob(6.6*U,6.6*U,5*U,.75,8),acc,0,6.6*U,zOf(.04)+1.6*U);add(G,blob(8.4*U,3.6*U,7*U,.8,8),rub,0,4.6*U,zOf(.93)-.6*U);
  add(G,blob(4.4*U,2*U,10*U,.6,8),up,0,8.3*U,zOf(.42),-.42);for(let i=0;i<5;i++){const t=.44+i*.075,y=hgt(t)-.2*U;add(G,cyl(.28*U,.28*U,wid(t)*1.05,6),paint('lace','#fbfbf8',.9),0,y,zOf(t),0,0,Math.PI/2);}
  add(G,box(.5*U,2.2*U,7*U),acc,wid(.5)*.93,5.3*U,zOf(.52),0,.05,.35);add(G,box(.5*U,2.2*U,7*U),acc,-wid(.5)*.93,5.3*U,zOf(.52),0,-.05,-.35);return G;};
