/* ================= MINIATURE MAYHEM CUP: toy racing sets built round real rooms =================
   Scale: a kart is a toy car 7.5 cm long, so 1 cm is TU units and every piece of furniture is its real size.
   The track is half the usual width (def.rw): thin orange plastic with raised edges, in pieces that clip together,
   held up by blue plastic piers. Layout data comes from /home/claude/mini (same fields as the Neon Cup's tracks). */
const TU=3.47;const tcm=v=>v*TU;
/* the furniture a track can stand on: boxes in room coordinates [x0,x1,z0,z1,top] */
let TOYF=[],TOYP=[],TOYB=[],TOYENV=null;/* TOYENV: where the room is photographed from for its reflections [x,height,z] *//* TOYP: places where a pier must stand (on a stack of books, say) */
function toyUnder(x,z,below){let h=0;for(const b of TOYF)if(x>=b[0]&&x<=b[1]&&z>=b[2]&&z<=b[3]&&b[4]<=below+.5&&b[4]>h)h=b[4];return h;}
/* The set comes in coloured sections, the way toy track does. TOYSEC lists them per room as [from,to,colour] in fractions of
   the lap (the lap as it is laid out, whichever way it is raced); everything else is orange. Looks only: the race never reads it. */
const TOYCOL={orange:'#ff6a12',red:'#e3271d',yellow:'#f6c41f',blue:'#1f55c8'},TOYSEC={bedroom:[[.073,.253,'red'],[.347,.514,'yellow'],[.783,.938,'blue']],kitchen:[[.079,.26,'yellow'],[.26,.426,'red'],[.789,.976,'blue']],garage:[[.126,.452,'yellow'],[.452,.635,'red'],[.674,.916,'blue']],backyard:[[.161,.309,'yellow'],[.336,.448,'red'],[.571,.737,'blue']]};
function toyColAt(def,j){j=((j%N)+N)%N;const f=(curRev?(N-j)%N:j)/N;for(const q of TOYSEC[def.look]||[])if(f>=q[0]&&f<q[1])return q[2];return 'orange';}
/* runs of one colour between two points of the lap: [[from,to,colour],...] */
function toyRuns(def,j0,j1){const out=[];let a=j0,k=toyColAt(def,j0);for(let j=j0+1;j<=j1;j++){const c=j<j1?toyColAt(def,j):null;if(c!==k){out.push([a,j,k]);a=j;k=c;}}return out;}
function toyPlasticTex(key){const c=cnv(256,512),g=c.getContext('2d');g.fillStyle=TOYCOL[key||'orange'];g.fillRect(0,0,256,512);
  /* one smooth piece of plastic: the only line is the joint where two pieces clip together (the white dashes are on the walls: toyRails) */
  g.fillStyle='rgba(0,0,0,.4)';g.fillRect(0,0,256,3);g.fillStyle='rgba(255,255,255,.28)';g.fillRect(0,3,256,2);
  for(let i=0;i<500;i++){g.fillStyle='rgba('+(Math.random()<.5?'255,255,255':'0,0,0')+','+(Math.random()*.04)+')';g.fillRect(Math.random()*256,Math.random()*512,1+Math.random()*3,1);}return c;}
const TOYW=()=>WALLD+4,TOYOR=key=>!key||key==='orange'?TM.mat('toyorange',()=>toySmooth(new THREE.MeshPhysicalMaterial({color:'#ff6a12',roughness:.34,clearcoat:1,clearcoatRoughness:.07,envMapIntensity:1,side:THREE.DoubleSide}))):TM.mat('toyplastic_'+key,()=>toySmooth(new THREE.MeshPhysicalMaterial({color:TOYCOL[key],roughness:.34,clearcoat:1,clearcoatRoughness:.07,envMapIntensity:1,side:THREE.DoubleSide}))),TOYBL=()=>TM.mat('toyblue',()=>toySmooth(new THREE.MeshPhysicalMaterial({color:'#1769d6',roughness:.35,clearcoat:.5,clearcoatRoughness:.25})));
/* moulded plastic is smooth: it takes none of the fine surface speckle Ultra gives plain materials */
function toySmooth(m){m.userData.noHQ=true;return m;}
/* the track is glossy plastic that mirrors the room it stands in (the room's own reflections, toyRoomEnv, never an outdoor sky) */
function toyRoadMat(key){key=key||'orange';return TM.mat('toyroad_'+key,()=>toySmooth(new THREE.MeshPhysicalMaterial({map:T2(toyPlasticTex(key),1,1),roughness:.34,metalness:0,clearcoat:1,clearcoatRoughness:.07,envMapIntensity:1,side:THREE.DoubleSide})));}
function toyRoad(def,SJ0,SJ1){if(def.battle)return;for(const q of toyRuns(def,SJ0,SJ1)){const r=strip(q[0],q[1],-TOYW(),TOYW(),.06,toyRoadMat(q[2]),120,true);if(r)r.receiveShadow=true;}}
/* one length of raised edge between two cross-sections: an inner face, a flat top and an outer face */
function toyRailQuad(pos,A,B,s){const quad=(a,b,c,d)=>pos.push(...a,...b,...c,...a,...c,...d);
  if(s>0){quad(A[0],B[0],B[1],A[1]);quad(A[1],B[1],B[2],A[2]);quad(A[2],B[2],B[3],A[3]);}else{quad(A[0],A[1],B[1],B[0]);quad(A[1],A[2],B[2],B[1]);quad(A[2],A[3],B[3],B[2]);}}
function toyRailMesh(pos,key){if(!pos.length)return;const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(pos,3));g.computeVertexNormals();const rm=new THREE.Mesh(g,TOYOR(key));rm.castShadow=true;rm.receiveShadow=true;rm.userData.noLift=true;rm.userData.noMerge=true;/* kept out of the merged scenery, which would swap its glossy plastic for a plain batch material */world.add(rm);}
/* the raised edges of the main track, left open where a shortcut leaves or joins and where the loop takes over */
function toyRails(def){if(def.battle)return;const W=TOYW(),by={},dash=[],sp=T.L/N,H=4.2,TH=3,P=j=>track[((j%N)+N)%N],at=(p,o,h)=>{const x=p.x+p.nx*o,z=p.y+p.ny*o;return [x,(p.ey||0)+h,z];},sec=(p,s)=>[at(p,W*s,0),at(p,W*s,H),at(p,(W+TH)*s,H),at(p,(W+TH)*s,-1.6)];
  for(const s of [-1,1])for(let j=0;j<N;j++){const p=P(j),q=P(j+1);if(p.cut)continue;const k=toyColAt(def,j),pos=by[k]||(by[k]=[]),open=(p.ey||0)<=2&&SHORTS.length&&(toyOffShort(p.x+p.nx*W*s,p.y+p.ny*W*s)<3||toyOffShort(q.x+q.nx*W*s,q.y+q.ny*W*s)<3);
    /* a white dash on the wall every 120 units, 36 long: along its top and down its inner face */
    if(!open&&(j*sp)%120<36){const q4=(a,b,c,d)=>dash.push(...a,...b,...c,...a,...c,...d);q4(at(p,(W+.4)*s,H+.05),at(p,(W+TH-.4)*s,H+.05),at(q,(W+TH-.4)*s,H+.05),at(q,(W+.4)*s,H+.05));q4(at(p,(W-.05)*s,1),at(p,(W-.05)*s,3.5),at(q,(W-.05)*s,3.5),at(q,(W-.05)*s,1));}
    if((p.ey||0)>2||!SHORTS.length){toyRailQuad(pos,sec(p,s),sec(q,s),s);continue;}toyRailClip(pos,sec(p,s),sec(q,s),s,toyOffShort);}
  for(const k in by)toyRailMesh(by[k],k);
  if(dash.length){const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(dash,3));g.computeVertexNormals();
    const dm=new THREE.Mesh(g,TM.mat('toydash',()=>toySmooth(new THREE.MeshPhysicalMaterial({color:'#f6f5f0',roughness:.4,clearcoat:.6,clearcoatRoughness:.2,side:THREE.DoubleSide,polygonOffset:true,polygonOffsetFactor:-2,polygonOffsetUnits:-2}))));
    dm.receiveShadow=true;dm.userData.noLift=true;dm.userData.noMerge=true;world.add(dm);}}
/* raised track: the thin underside of the plastic and blue piers down to whatever is underneath (the floor, a desk, a stack of books) */
function toyDecks(def){if(def.battle)return;const W=TOYW()+3,inGl=j=>GLIDE&&j>=GLIDE.j0&&j<GLIDE.j1,P=j=>track[((j%N)+N)%N],unds={};
  for(let j=0;j<N;j++){const p=P(j),q=P(j+1);if(inGl(j)||inGl(j+1))continue;const pe=p.ey||0,qe=q.ey||0;if(pe<1.5&&qe<1.5)continue;const c=(t,o,h)=>[t.x+t.nx*o,h,t.y+t.ny*o],kc=toyColAt(def,j),und=unds[kc]||(unds[kc]=[]);
    und.push(...c(p,-W,pe-1.6),...c(q,W,qe-1.6),...c(q,-W,qe-1.6),...c(p,-W,pe-1.6),...c(p,W,pe-1.6),...c(q,W,qe-1.6));}
  const mk=(arr,mat,cast)=>{const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(arr,3));g.computeVertexNormals();const m=new THREE.Mesh(g,mat);m.userData.noLift=true;m.castShadow=!!cast;m.receiveShadow=true;world.add(m);return m;};
  for(const kc in unds)mk(unds[kc],toySmooth(new THREE.MeshStandardMaterial({color:new THREE.Color(TOYCOL[kc]).multiplyScalar(.82),roughness:.45,side:THREE.DoubleSide})),true);
  /* piers every 30 cm or so: two tapered posts, a cross beam under the track, tie bars on the tall ones and round feet; none where another road runs underneath */
  const post=[],beam=[],foot=[],tie=[],arm=[];let last=-99;
  for(let j=0;j<N;j++){const p=P(j),e=p.ey||0,force=TOYP.some(q=>(q[0]-p.x)**2+(q[1]-p.y)**2<20);if(e<7||inGl(j)||(j-last<13&&!force))continue;const base=toyUnder(p.x,p.y,e-2);if(e-base<6)continue;let blocked=false;
    for(let i=0;i<N;i+=2){let di=Math.abs(i-j)%N;di=Math.min(di,N-di);if(di<16)continue;const q=track[i],qe=q.ey||0;if(qe>=e-8)continue;if((q.x-p.x)**2+(q.y-p.y)**2<(2*W+10)**2){blocked=true;break;}}
    if(blocked){/* a spiral stands over itself: one post outside the curve, clear of every level, with an arm under the track */
      const q=P(j+4),cr=p.tx*q.ty-p.ty*q.tx;if(Math.abs(cr)<.05||j-last<9)continue;const sd=cr>0?-1:1,ox=p.x+p.nx*(W+7)*sd,oz=p.y+p.ny*(W+7)*sd;let clear=true;
      for(let i=0;i<N;i+=2){const t=track[i];if((t.ey||0)<e-6&&(t.x-ox)**2+(t.y-oz)**2<(W+3)**2){clear=false;break;}}if(!clear)continue;
      last=j;const b2=toyUnder(ox,oz,e-2),hh=e-1-b2;post.push({x:ox,y:b2+hh/2,z:oz,sy:hh,ry:-p.ang});foot.push({x:ox,y:b2+1,z:oz,ry:-p.ang});arm.push({x:p.x+p.nx*(W-6)*sd,y:e-3.4,z:p.y+p.ny*(W-6)*sd,ry:-p.ang});continue;}
    last=j;beam.push({x:p.x,y:e-3.4,z:p.y,ry:-p.ang});
    /* a pier that rests on something (a stack of books) keeps its posts close in, so both stand on it */const po=force?20:W-7;for(const sd of [-1,1]){const x=p.x+p.nx*po*sd,z=p.y+p.ny*po*sd,b2=toyUnder(x,z,e-2),hh=e-5-b2;if(hh<2)continue;post.push({x,y:b2+hh/2,z,sy:hh,ry:-p.ang});foot.push({x,y:b2+1,z,ry:-p.ang});}
    const h=e-5-base;for(let y=base+34;y<e-24&&h>60;y+=42)tie.push({x:p.x,y,z:p.y,ry:-p.ang});}
  const blue=TOYBL();instBatch(new THREE.CylinderGeometry(2.6,3.6,1,4,1).rotateY(Math.PI/4),blue,post,true);instBatch(new THREE.BoxGeometry(8,3.4,2*W+4),blue,beam,true);instBatch(new THREE.CylinderGeometry(6,7.5,2,14),blue,foot,true);instBatch(new THREE.BoxGeometry(2.2,2.2,2*W-14),blue,tie,true);instBatch(new THREE.BoxGeometry(7,3.4,30),blue,arm,true);}
/* put a model in the room: design coordinates (x east, y north), y0 its height off the floor, ry its turn */
function toyPut(o,x,y,ry,y0){o.position.set(x,y0||0,-y);o.rotation.y=ry||0;o.userData.noLift=true;o.traverse(q=>{if(q.isMesh){q.castShadow=q.userData.cast!==false&&!q.material.transparent;q.receiveShadow=true;}});world.add(o);return o;}
/* a soft dark patch on the floor where furniture keeps the light off it (far furniture has no drawn shadow of its own) */
function toyShade(x0,x1,y0,y1,a,h){const c=TM.can('aoshade',64,64,(g,w,hh)=>{const gr=g.createRadialGradient(32,32,6,32,32,32);gr.addColorStop(0,'rgba(0,0,0,1)');gr.addColorStop(.7,'rgba(0,0,0,.75)');gr.addColorStop(1,'rgba(0,0,0,0)');g.fillStyle=gr;g.fillRect(0,0,w,hh);}),
  m=TM.mat('aoshade'+a,()=>new THREE.MeshBasicMaterial({map:TM.tex(c,'aoshade'),transparent:true,opacity:a,depthWrite:false,polygonOffset:true,polygonOffsetFactor:-1,polygonOffsetUnits:-1})),p=new THREE.Mesh(new THREE.PlaneGeometry((x1-x0)*1.25,(y1-y0)*1.25),m);
  p.rotation.x=-Math.PI/2;p.position.set((x0+x1)/2,(h||0)+.35,-(y0+y1)/2);p.userData.noLift=true;p.userData.noMerge=true;p.renderOrder=1;world.add(p);}
/* a wall with a rectangular opening: four pieces round the hole. ax 'x' runs along x at z=at, 'z' runs along z at x=at */
function toyWall(ax,at,a0,a1,H,hole,m,face,tile){const T=12*TM.U,mk=(u0,u1,v0,v1)=>{if(u1-u0<1||v1-v0<1)return;const g=ax==='x'?new THREE.BoxGeometry(u1-u0,v1-v0,T):new THREE.BoxGeometry(T,v1-v0,u1-u0),c=ax==='x'?[(u0+u1)/2,(v0+v1)/2,at+face*T/2]:[at+face*T/2,(v0+v1)/2,(u0+u1)/2];
    /* with `tile` (cm) the texture is laid by where the wall stands in the room, not from each piece's own middle: courses of brick run on round the window and round the corners */
    if(tile){g.translate(c[0],c[1],c[2]);TM.uvw(g,tile);g.translate(-c[0],-c[1],-c[2]);}else TM.uvw(g,120);const b=new THREE.Mesh(g,m);
    b.position.set(c[0],c[1],c[2]);b.receiveShadow=true;b.castShadow=true;b.userData.noLift=true;world.add(b);};
  if(!hole){mk(a0,a1,0,H);return;}const [h0,h1,y0,y1]=hole;mk(a0,h0,0,H);mk(h1,a1,0,H);mk(h0,h1,0,y0);mk(h0,h1,y1,H);}
/* ---- Bedroom Blitz: a teenager's bedroom, 4.0 x 4.8 m ---- */
function toyBedroom(def){const U=TM.U,X=695,Y=833,H=868,M=TM;
  /* light: a low afternoon sun that reaches the room only through the window (sunBeam, below): warm, hard-edged patches on the desk
     and across the middle of the floor; the rest of the room is in cooler shade, lit by the sky and by what the floor throws back up */
  renderer.toneMappingExposure=.98;hemi.color.set('#cfdcf0');hemi.groundColor.set('#b3937a');hemi.intensity=.54;sun.color.set('#ffdcaa');sun.intensity=2.7;sunDir.set(-.1,.56,-.82).normalize();rimL.intensity=.16;rimL.color.set('#cfe0ff');
  scene.fog=new THREE.Fog('#d8cfc0',6000,30000);scene.background=new THREE.Color('#bcd6f2');Object.assign(POST.grade,{sat:1.04,con:1.05,tint:[1.01,1,.985],vig:.16,bloom:.22,thr:.97});
  /* floor: oak boards 12 cm wide running the length of the room */
  /* the oak boards are a texture pair made by tools/blender/oak_tex.py (every board its own length, tone and ring figure; relief for the grain, the bevels and the gaps): one tile is 1.92 m. The drawn wood stays as the stand-in if the pictures are missing */
  const oak=typeof PROP_TEX!=='undefined'&&PROP_TEX.tex_toy_oak&&PROP_TEX.tex_toy_oak_n,fm=oak?M.mat('oakfloor',()=>{const c=propTex('tex_toy_oak'),n=propTex('tex_toy_oak_n',false);for(const t of [c,n])t.wrapS=t.wrapT=THREE.RepeatWrapping;return new THREE.MeshStandardMaterial({map:c,normalMap:n,normalScale:new THREE.Vector2(.9,.9),roughness:.4,metalness:0,envMapIntensity:.75});}):M.wood('floor','#b08556','#4a2f18',{planks:8,knots:1,rough:.46,env:.55,bump:1.4}),fg=new THREE.PlaneGeometry(2*X,2*Y,1,1);fg.rotateX(-Math.PI/2);M.uvw(fg,oak?192:96,true);const fl=new THREE.Mesh(fg,fm);fl.position.y=-.1;fl.receiveShadow=true;fl.userData.noLift=true;world.add(fl);
  /* walls (the window in the north wall, the door in the south wall), ceiling, skirting boards */
  /* painted walls: smooth, with the fine stipple a roller leaves (2 mm) instead of the cloudy mottling Ultra gives plain materials, which read as noise on a big flat wall. The names stay toy_pt_wall*, which the PC looks for */
  const stip=T2(heightToNormal(M.can('stipple',256,256,(g,w,h,r)=>{for(let y=0;y<h;y+=2)for(let x=0;x<w;x+=2){const v=112+r()*32;g.fillStyle='rgb('+v+','+v+','+v+')';g.fillRect(x,y,2,2);}}),1.1),7,7,true),
    wallM=(key,col)=>M.mat('pt_'+key,()=>{const m=new THREE.MeshStandardMaterial({color:col,roughness:.9,metalness:0,envMapIntensity:.4,normalMap:stip,normalScale:new THREE.Vector2(.35,.35)});m.userData.noHQ=true;return m;}),
    wall=wallM('wall','#e9e3d8'),wall2=wallM('wall2','#93a8a6'),win=[-370,150,330,764],dr=[-300,-14,0,712];
  sunBeam([[win[0],win[1],win[2],win[3],-Y-12*U,-Y]],win[3]/sunDir.y+160);
  toyWall('x',-Y,-X,X,H,[win[0],win[1],win[2],win[3]],wall,-1);toyWall('x',Y,-X,X,H,[dr[0],dr[1],dr[2],dr[3]],wall,1);toyWall('z',-X,-Y,Y,H,null,wall,-1);toyWall('z',X,-Y,Y,H,null,wall2,1);
  const cg=new THREE.PlaneGeometry(2*X,2*Y);cg.rotateX(Math.PI/2);const ce=new THREE.Mesh(cg,wallM('ceiling','#f4f1ea'));ce.position.y=H;ce.userData.noLift=true;world.add(ce);
  const sk=M.paint('skirting','#f6f4ee',.5),sb=(x0,x1,z0,z1)=>{const b=new THREE.Mesh(M.slab(Math.abs(x1-x0)||1.6*U,10*U,Math.abs(z1-z0)||1.6*U,.3*U,.3*U,2),sk);b.position.set((x0+x1)/2,5*U,(z0+z1)/2);b.userData.noLift=true;b.receiveShadow=true;world.add(b);};
  sb(-X,X,-Y+.8*U,-Y+.8*U);sb(-X,dr[0]-9*U,Y-.8*U,Y-.8*U);sb(dr[1]+9*U,X,Y-.8*U,Y-.8*U);sb(-X+.8*U,-X+.8*U,-Y,Y);sb(X-.8*U,X-.8*U,-Y,Y);
  /* the window, the view outside, curtains on a rod */
  const wcx=(win[0]+win[1])/2,wW=(win[1]-win[0])/U,wH=(win[3]-win[2])/U;toyPut(M.window(wW,wH),wcx,Y+4*U,0,win[2]);const out=M.outside(wW*2.6,wH*2.2);out.position.set(wcx,win[2]+wH*U*.55,-Y-60*U);out.userData.noLift=true;out.userData.envGain=6;/* the sky outside is far brighter than the room: in the room's reflections the window is a light */world.add(out);TOYENV=[-120,220,200];
  for(const s of [-1,1])toyPut(M.curtain(58,wH+34,{seed:s+3}),wcx+s*(wW*U/2+8*U),Y-5*U,0,win[3]+22*U).traverse(q=>{if(q.isMesh){q.userData.sunlit=true;q.receiveShadow=false;}});/* the folds reach from 2 to 16 cm off the wall. The curtains are lit from behind at a grazing angle, where the sun's shadow map breaks up into jagged patches on the folds: they throw shadows but are not tested against them */const rod=new THREE.Mesh(M.cyl(1.1*U,1.1*U,(wW+90)*U,12),M.metal('rod','#2a2c31',.4));rod.rotation.z=Math.PI/2;rod.position.set(wcx,win[3]+24*U,-Y+7*U);rod.userData.noLift=true;world.add(rod);
  toyPut(M.door(),(dr[0]+dr[1])/2,-Y+1*U,Math.PI,0);
  /* a ceiling light */
  {const g=new THREE.Group();M.add(g,M.cyl(17*U,17*U,2*U,32),M.paint('ceilrose','#f1eee6',.6),0,-1*U,0);M.add(g,new THREE.SphereGeometry(15*U,28,12,0,6.283,Math.PI/2,Math.PI/2),M.mat('ceilglass',()=>new THREE.MeshStandardMaterial({color:'#fffaf0',emissive:'#fff1d6',emissiveIntensity:.35,roughness:.4})),0,-2*U,0);toyPut(g,0,0,0,H);}
  /* ---- furniture ---- */
  const deskTop=260;toyPut(M.desk({w:200,d:80,h:75}),-123,694,0);TOYF.push([-470,224,-833,-555,deskTop]);
  toyPut(M.deskmat(),-110,738,0,deskTop);toyPut(M.monitor({screen:'game'}),-110,792,0,deskTop+.4*U);/* far enough from the wall that its angled screen clears the curtain */toyPut(M.monitor({arm:true,screen:'desk'}),-338,728,.42,deskTop);toyPut(M.keyboard(),-118,712,0,deskTop+.4*U);toyPut(M.mouse(),-22,706,.1,deskTop+.4*U);
  toyPut(M.pc(),150,733,Math.PI/2*0,deskTop);toyPut(M.mug({color:'#2f5d8a'}),-262,712,.6,deskTop);toyPut(M.sodacan(),30,776,0,deskTop);toyPut(M.books(4,5),-428,770,.3,deskTop);toyPut(M.plant({seed:4}),-452,792,0,deskTop).scale.setScalar(.5);
  /* the chair is pushed back to one side, clear of the sunlight that falls across the floor */toyPut(M.chair({turn:-.5}),-345,372,Math.PI+.35);toyPut(M.floorlamp(),460,455,0);
  /* the bed stands clear of the east wall and of the wall behind its headboard (it used to reach into both); its legs are at the frame's corners, just outside the track that runs underneath */
  toyPut(M.bed(),412,-460,Math.PI);toyPut(M.nightstand(),50,-760,Math.PI);toyPut(M.mug(),32,-756,2,52*U);toyPut(M.books(2,9),66,-764,.2,52*U);
  toyPut(M.dresser(),-617,268,Math.PI/2);TOYF.push([-695,-539,-476,-60,156]);
  /* the start of the climb rests on a stack of books */
  /* placed from the track's real height (not a straight-line guess, which put the top book through the road): the lowest point of the
     climb that clears the stack, then far enough up the slope that the whole stack is under the track */
  {const st=M.books(4,21),top=st.userData.top,T0=j=>track[((j%N)+N)%N];let jb=-1,eb=1e9;for(let j=0;j<N;j++){const q=track[j],e=q.ey||0;if(q.x<-560&&e>=top+5&&e<eb){eb=e;jb=j;}}
    if(jb>=0){const up=(T0(jb+1).ey||0)>eb?1:-1;let k=jb,dd=0;while(dd<48){const a=T0(k),b=T0(k+up);dd+=Math.hypot(b.x-a.x,b.y-a.y);k+=up;}const q=T0(k);toyPut(st,q.x,-q.y,Math.PI/2);TOYF.push([q.x-34,q.x+34,q.y-24,q.y+24,top]);TOYP.push([q.x,q.y]);}}
  toyPut(M.rug({w:110,l:150}),-60,-380,0);
  /* sneakers kicked off by the track */
  toyPut(M.sneaker(),-400,150,.3);toyPut(M.sneaker(),-330,168,.6);toyPut(M.sneaker({color:'#2a2c31',accent:'#39d98a'}),-520,-290,-1.5);toyPut(M.sneaker({color:'#2a2c31',accent:'#39d98a'}),-518,-365,-1.7);
  toyPut(M.bin(),300,770,0);toyPut(M.carton(42,32,22),250,-770,.1);toyPut(M.carton(30,24,18),630,-780,-.2);toyPut(M.plant({seed:15}),-345,-790,0);
  /* the small things left lying about: they show how small the karts are */
  toyPut(M.skateboard(),-60,-470,.5,4.2);toyPut(M.ball(),-300,-560,0);toyPut(M.ball({kind:'tennis'}),-330,470,0);toyPut(M.cube({seed:5}),214,-196,.6);toyPut(M.bricks({seed:3,n:10,spread:8}),-200,236,0);toyPut(M.bricks({seed:8,n:7,spread:7}),-646,-792,0);
  toyPut(M.pencils({seed:2,n:3}),-300,300,0);toyPut(M.pencils({seed:6,n:2,spread:10}),150,330,0);toyPut(M.backpack(),96,-604,-1.2);toyPut(M.controller(),-292,728,.4,deskTop);toyPut(M.cube({seed:9}),196,706,.3,deskTop);
  toyPut(M.setbox(),-130,-722,.15);toyPut(M.trackpiece(),-150,-722,.9,38.4);toyPut(M.trackpiece({l:22}),-248,-664,-.4);
  toyPut(M.poster(50,70,0),-689,268,Math.PI/2,430);toyPut(M.poster(42,60,1),689,-250,-Math.PI/2,500);toyPut(M.poster(42,60,2),689,-430,-Math.PI/2,470);toyPut(M.shelf(),689,250,-Math.PI/2,520);
  /* where furniture keeps the light off the floor */
  toyShade(139,685,-826,-126,.5);toyShade(-470,224,555,833,.34);toyShade(-695,-539,60,476,.3);toyShade(-415,-275,302,442,.22);toyShade(-28,127,-833,-690,.3);}
/* ---- the pieces of the racing set ---- */
/* the loop: the same full loop the other cups have, scaled to the toy track. The road swings left into it and comes out on the right */
function toyLoops(def){LOOP_DH=5;for(const q of def.tloops||[]){const j=nfj(q[0]),p=track[j];LOOPS.push({j,p:{x:p.x,y:p.y,tx:p.tx,ty:p.ty,nx:p.nx,ny:p.ny,ang:p.ang},g0:groundAt(p.x,p.y)+(p.ey||0),W:WALLD,S:54,lat0:-54,shift:108,full:true,sc:q[1]||LS});}
  LOOPS.sort((a,b)=>a.j-b.j);LOOP=LOOPS[0]||null;for(const L of LOOPS)shiftForLoop(L);if(LOOPS.length){LOOP_TAP=30;LOOP_DIV=60;buildGrid();}}
function toyLoop(L,def){const p=L.p,g0=L.g0,SEG=96,LEAD=3,W=TOYW(),TH=3,H=4.2,pos=[],uv=[],idx=[],rails=[],secs=[[],[]];
  for(let i=-LEAD;i<=SEG;i++){const th=i<0?0:i/SEG*Math.PI*2,al=i<0?i*3.4:LOOPR*Math.sin(th),hg=LOOPR*(1-Math.cos(th)),lat=L.lat0+L.shift*Math.max(0,i)/SEG,nt=-Math.sin(th),nu=Math.cos(th),arc=i<0?i*3.4:LOOPR*th;
    const at=(l,up)=>[p.x+p.tx*(al+nt*up)+p.nx*l,g0+hg+.3+nu*up,p.y+p.ty*(al+nt*up)+p.ny*l];
    for(const sd of [-1,1]){pos.push(...at(lat+sd*W,0));uv.push(sd<0?0:1,arc/120);secs[sd<0?0:1].push([at(lat+sd*W,0),at(lat+sd*W,H),at(lat+sd*(W+TH),H),at(lat+sd*(W+TH),-1.6)]);}
    if(i<SEG){const a=(i+LEAD)*2;idx.push(a,a+1,a+2,a+1,a+3,a+2);}}
  const lg=new THREE.BufferGeometry();lg.setAttribute('position',new THREE.Float32BufferAttribute(pos,3));lg.setAttribute('uv',new THREE.Float32BufferAttribute(uv,2));lg.setIndex(idx);lg.computeVertexNormals();
  const lm=new THREE.Mesh(lg,toyRoadMat());lm.castShadow=lm.receiveShadow=true;lm.userData.noLift=true;world.add(lm);
  for(const k of [0,1])for(let i=0;i<secs[k].length-1;i++)toyRailQuad(rails,secs[k][i],secs[k][i+1],k?1:-1);toyRailMesh(rails);
  /* the frame: a blue arch over the top of the loop that the track clips into, on wide feet, and a spine along the floor between the way in and the way out */
  const G=new THREE.Group();G.position.set(p.x,g0,p.y);G.rotation.y=-p.ang;G.userData.noLift=true;world.add(G);const bl=TOYBL(),top=2*LOOPR,o=L.S+W+TH+9,M=TM;
  for(const sd of [-1,1]){M.add(G,new THREE.CylinderGeometry(4.6,7.4,top+10,4,1).rotateY(Math.PI/4),bl,0,(top+10)/2,sd*o);M.add(G,M.slab(46,3,20,5,1,2),bl,0,1.5,sd*o);
    for(const a of [-1,1])M.add(G,new THREE.BoxGeometry(3,top*.62,3).rotateZ(a*.36),bl,a*13.5,top*.3,sd*o);}
  M.add(G,M.slab(11,9,2*o+12,2,1.4,2),bl,0,top+7.2,0);M.add(G,M.slab(200,3,8,3,1,2),bl,0,1.5,0);
  for(const sd of [-1,1])M.add(G,M.slab(18,3.4,7,1.5,.6,1),bl,0,top+1.2,sd*(W+TH+2.5));
  const sc=TM.can('loopsign',512,128,(g,w,h)=>{g.fillStyle='#f6c21c';g.fillRect(0,0,w,h);g.fillStyle='#1b1b1e';g.fillRect(0,0,w,10);g.fillRect(0,h-10,w,10);g.font='900 84px Arial Black,Impact,sans-serif';g.textAlign='center';g.fillStyle='#d42a20';g.fillText('TURBO LOOP',w/2,94);}),
    sm=TM.mat('loopsign',()=>new THREE.MeshStandardMaterial({map:TM.tex(sc,'loopsign'),roughness:.4}));
  for(const sd of [-1,1]){const pl=M.add(G,new THREE.PlaneGeometry(64,16),sm,sd*5.7,top+16,0,0,sd*Math.PI/2);pl.userData.cast=false;}M.add(G,M.slab(10,17,66,1.5,.6,1),bl,0,top+16,0);
  G.traverse(q=>{if(q.isMesh){q.castShadow=q.userData.cast!==false;q.receiveShadow=true;}});
  obstacles.push({x:p.x-p.nx*o,y:p.y-p.ny*o,r:6,h:top,j:L.j,lat:999},{x:p.x+p.nx*o,y:p.y+p.ny*o,r:6,h:top,j:L.j,lat:999});}
/* the start gate: two blue posts and a chequered banner, the size a toy set would have */
function toyGate(def){if(def.battle)return;const s=track[0],G=new THREE.Group(),bl=TOYBL(),M=TM,o=TOYW()+9,Y=(s.ey||0);G.position.set(s.x,Y,s.y);G.rotation.y=-s.ang;G.userData.noLift=true;world.add(G);
  for(const sd of [-1,1]){M.add(G,new THREE.CylinderGeometry(2.6,3.4,40,4,1).rotateY(Math.PI/4),bl,0,20,sd*o);M.add(G,M.slab(13,2.4,13,3,.6,2),bl,0,1.2,sd*o);}
  const bt=T2(bannerC);bt.userData.keepCanvas=true;const bm=new THREE.MeshStandardMaterial({map:bt,roughness:.5}),b=new THREE.Mesh(new THREE.BoxGeometry(2,12.5,2*o+7),[bm,bm,bl,bl,bl,bl]);b.position.set(0,35,0);G.add(b);
  M.add(G,M.slab(4,3,2*o+12,1.4,.5,1),bl,0,42.4,0);G.traverse(q=>{if(q.isMesh){q.castShadow=true;q.receiveShadow=true;}});
  if(document.fonts)document.fonts.ready.then(()=>{drawBanner();bt.needsUpdate=true;});}
/* boosters: a strip of arrows across the whole track between two motor housings, the way a toy set fires its cars on */
function toyPadTex(){return TM.can('toypad',256,256,(g,w,h)=>{g.fillStyle='#1b1b1e';g.fillRect(0,0,w,h);g.strokeStyle='#f6c21c';g.lineWidth=26;g.lineJoin='miter';for(let y=-60;y<340;y+=86){g.beginPath();g.moveTo(-10,y+70);g.lineTo(128,y);g.lineTo(266,y+70);g.stroke();}});}
function toyBooster(j,gate){const p=track[((j%N)+N)%N],G=new THREE.Group(),M=TM,bl=TOYBL(),o=TOYW()+3+7.5,Y=(p.ey||0);G.position.set(p.x,Y,p.y);G.rotation.y=-p.ang;G.userData.noLift=true;world.add(G);
  const gy=M.plastic('toygrey','#d9dce2',.4),bk=M.plastic('toyrubber','#16171a',.8),bolt=TM.can('bolt',64,128,(g,w,h)=>{g.fillStyle='#f6c21c';g.fillRect(0,0,w,h);g.fillStyle='#d42a20';g.beginPath();g.moveTo(38,6);g.lineTo(12,70);g.lineTo(30,70);g.lineTo(22,122);g.lineTo(54,52);g.lineTo(36,52);g.closePath();g.fill();}),bm=TM.mat('bolt',()=>new THREE.MeshStandardMaterial({map:TM.tex(bolt,'bolt'),roughness:.4}));
  for(const sd of [-1,1]){if(toyOffShort(p.x+p.nx*sd*o,p.y+p.ny*sd*o)<40)continue;M.add(G,M.slab(40,14,15,3,1.6,2),bl,0,7-1.6,sd*o);M.add(G,M.slab(26,3,11,2.4,.8,2),gy,0,13.6,sd*o);const st=M.add(G,new THREE.PlaneGeometry(9,18),bm,0,15.2,sd*o,-Math.PI/2,0,Math.PI/2);st.userData.cast=false;
    for(const a of [-9,9])M.add(G,M.cyl(7.2,7.2,5,20),bk,a,5.6,sd*(o-6.2));}
  G.traverse(q=>{if(q.isMesh){q.castShadow=q.userData.cast!==false;q.receiveShadow=true;}});}
function toyPads(def){if(def.battle)return;const m=TM.mat('toypad',()=>new THREE.MeshStandardMaterial({map:T2(toyPadTex(),1,1),roughness:.4,emissive:'#f6c21c',emissiveIntensity:.12,polygonOffset:true,polygonOffsetFactor:-2,polygonOffsetUnits:-2}));
  const put1=j=>{pads.push({j,lat:0,w:RW+4});const pm=strip(j-2,j+2,-RW-4,RW+4,.14,m,32);if(pm&&pm.isMesh){pm.userData.noMerge=true;pm.castShadow=false;}TOYB.push(j);};
  (def.npads||[]).forEach(q=>put1(nfj(q[0])));for(const L of LOOPS)if(L.full)put1((L.j-13+N)%N);}
function toyRamps(def){const c=TM.can('toyramp',256,256,(g,w,h)=>{g.fillStyle='#ff6a12';g.fillRect(0,0,w,h);g.fillStyle='#fff4dc';for(let y=-40;y<300;y+=64){g.beginPath();g.moveTo(40,y+52);g.lineTo(128,y);g.lineTo(216,y+52);g.lineTo(216,y+74);g.lineTo(128,y+22);g.lineTo(40,y+74);g.closePath();g.fill();}g.fillStyle='#1769d6';g.fillRect(0,0,14,h);g.fillRect(w-14,0,14,h);}),
    topM=new THREE.MeshPhysicalMaterial({map:T2(c,1,1),roughness:.32,clearcoat:.5,clearcoatRoughness:.3}),sideM=new THREE.MeshPhysicalMaterial({color:'#1769d6',roughness:.35,clearcoat:.4,side:THREE.DoubleSide});
  for(const f of def.nramps||[]){let j=nfj(f);if(curRev)j=(j-4+N)%N;const r={j,len:4*T.L/N,w:RW+2,h:6};ramps.push(r);buildRamp(r,topM,sideM);}}
/* a shortcut is a single lane of the same orange track */
const TOYSW=sc=>(sc.w||SCW)+5;/* a shortcut lane is drawn this much wider than its driving line each side, so karts stay clear of its edges */
/* how far a point is outside the main track's surface (floor level only): negative = on it */
function toyOffMain(x,z){let bd=1e9;for(let j=0;j<N;j++){const t=track[j];if((t.ey||0)>2)continue;const d=(t.x-x)**2+(t.y-z)**2;if(d<bd)bd=d;}return Math.sqrt(bd)-TOYW();}
/* how far a point is outside a shortcut's lane: negative = inside it */
function toyOffShort(x,z){let b=1e9;for(const sc of SHORTS){const P=sc.pts,W=TOYSW(sc);for(let i=0;i<P.length;i++){const p=P[i],al=(x-p.x)*p.tx+(z-p.y)*p.ty;if(Math.abs(al)>6)continue;const o=Math.abs((x-p.x)*p.nx+(z-p.y)*p.ny)-W;if(o<b)b=o;}}return b;}
/* a length of rail between two cross-sections, cut exactly where `off` (measured at the rail's inner foot) crosses zero, so two
   rails that meet at a junction meet without a gap */
function toyRailClip(pos,A,B,s,off){const mix=(P,Q,t)=>P.map((p,i)=>[p[0]+(Q[i][0]-p[0])*t,p[1]+(Q[i][1]-p[1])*t,p[2]+(Q[i][2]-p[2])*t]),fa=off(A[0][0],A[0][2]),fb=off(B[0][0],B[0][2]);
  if(fa<=0&&fb<=0)return;if(fa>0&&fb>0){toyRailQuad(pos,A,B,s);return;}let lo=0,hi=1;for(let i=0;i<12;i++){const t=(lo+hi)/2,M=mix(A,B,t),f=off(M[0][0],M[0][2]);if((f>0)===(fa>0))lo=t;else hi=t;}
  const M=mix(A,B,(lo+hi)/2);if(fa>0)toyRailQuad(pos,A,M,s);else toyRailQuad(pos,M,B,s);}
/* a shortcut is a single lane of the same orange track, walled all the way: its rails run right up to the main track's */
function toyShortcut(sc,def){const SW=TOYSW(sc),P=sc.pts,pos=[],uv=[],idx=[],rails=[];
  for(let i=0;i<P.length;i++){const p=P[i];for(const sd of [-1,1]){pos.push(p.x+p.nx*SW*sd,.16,p.y+p.ny*SW*sd);uv.push(sd<0?.2:.8,i*8/120);}if(i<P.length-1){const a=i*2;idx.push(a,a+1,a+2,a+1,a+3,a+2);}}
  const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(pos,3));g.setAttribute('uv',new THREE.Float32BufferAttribute(uv,2));g.setIndex(idx);g.computeVertexNormals();const m=new THREE.Mesh(g,toyRoadMat());m.receiveShadow=true;m.userData.noLift=true;world.add(m);
  const sec=(p,s)=>[[p.x+p.nx*SW*s,.1,p.y+p.ny*SW*s],[p.x+p.nx*SW*s,4.2,p.y+p.ny*SW*s],[p.x+p.nx*(SW+3)*s,4.2,p.y+p.ny*(SW+3)*s],[p.x+p.nx*(SW+3)*s,-.2,p.y+p.ny*(SW+3)*s]];
  for(const s of [-1,1])for(let i=0;i<P.length-1;i++)toyRailClip(rails,sec(P[i],s),sec(P[i+1],s),s,toyOffMain);toyRailMesh(rails);}
/* Room reflections: once the room is built it is photographed from an open spot into a small cube map, which becomes the map's
   environment: the track, the karts and the floor then mirror the window and the walls. Two passes, so the second sees the first
   one's reflections; karts are left out. Done once per load, no cost per frame. */
function toyRoomEnv(){const P=TOYENV;if(P&&world)try{sunShadeAll();const rt=new THREE.WebGLCubeRenderTarget(LOWQF()?128:256,{type:THREE.HalfFloatType}),cc=new THREE.CubeCamera(4,6000,rt);cc.position.set(P[0],P[1],P[2]);scene.add(cc);
    const hid=[],lit=[];for(const k of karts){if(k.m&&k.m.g.visible){k.m.g.visible=false;hid.push(k.m.g);}}
    world.traverse(o=>{if(o.userData.envGain&&o.material&&o.material.color){lit.push(o,o.material.color.clone());o.material.color.multiplyScalar(o.userData.envGain);}});
    try{for(let i=0;i<2;i++){renderer.shadowMap.needsUpdate=true;cc.update(renderer,scene);const pm=new THREE.PMREMGenerator(renderer),e=pm.fromCubemap(rt.texture).texture;pm.dispose();if(scene.environment)scene.environment.dispose();scene.environment=e;}}
    finally{for(let i=0;i<lit.length;i+=2)lit[i].material.color.copy(lit[i+1]);hid.forEach(g=>g.visible=true);scene.remove(cc);rt.dispose();}}catch(e){console.warn('room reflections',e);}
  applyEnvProbe();}
/* The shell an indoor toy room is built in: floor, four painted walls (a window in the north wall, a door in the south wall), ceiling,
   skirting, the view outside, the afternoon sun through the window and the spot the room is photographed from for its reflections.
   o: {key, X, Y, H (half width, half length, height), win:[x0,x1,y0,y1], dr:[x0,x1,y0,y1], walls:[north,south,west,east], floor:material, tile:cm, env:[x,height,z]}
   (the bedroom was built before this existed and keeps its own copy of these steps) */
function toyShell(o){const U=TM.U,M=TM,X=o.X,Y=o.Y,H=o.H,win=o.win,dr=o.dr;
  renderer.toneMappingExposure=.98;hemi.color.set('#cfdcf0');hemi.groundColor.set('#b3937a');hemi.intensity=.54;sun.color.set('#ffdcaa');sun.intensity=2.7;if(o.sun)sunDir.set(o.sun[0],o.sun[1],o.sun[2]).normalize();else sunDir.set(-.1,.56,-.82).normalize();/* (o.sun: a room lit from another side, as the garage through its big door) */rimL.intensity=.16;rimL.color.set('#cfe0ff');
  scene.fog=new THREE.Fog('#d8cfc0',6000,30000);scene.background=new THREE.Color('#bcd6f2');Object.assign(POST.grade,{sat:1.04,con:1.05,tint:[1.01,1,.985],vig:.16,bloom:.22,thr:.97});
  const fg=new THREE.PlaneGeometry(2*X,2*Y,1,1);fg.rotateX(-Math.PI/2);M.uvw(fg,o.tile,true);const fl=new THREE.Mesh(fg,o.floor);fl.position.y=-.1;fl.receiveShadow=true;fl.userData.noLift=true;world.add(fl);
  const stip=T2(heightToNormal(M.can('stipple',256,256,(g,w,h,r)=>{for(let y=0;y<h;y+=2)for(let x=0;x<w;x+=2){const v=112+r()*32;g.fillStyle='rgb('+v+','+v+','+v+')';g.fillRect(x,y,2,2);}}),1.1),7,7,true),
    wallM=(key,col)=>M.mat('pt_'+key,()=>{const m=new THREE.MeshStandardMaterial({color:col,roughness:.9,metalness:0,envMapIntensity:.4,normalMap:stip,normalScale:new THREE.Vector2(.35,.35)});m.userData.noHQ=true;return m;}),
    W=o.walls.map((c,i)=>typeof c==='string'?wallM('wall'+o.key+i,c):c);/* (a room may bring its own wall material: the garage's brick) *//* named toy_pt_wall..., which the PC looks for */
  if(o.beam)sunBeam(o.beam,o.beam[0][3]/sunDir.y+160);else sunBeam([[win[0],win[1],win[2],win[3],-Y-12*U,-Y]],win[3]/sunDir.y+160);
  toyWall('x',-Y,-X,X,H,win,W[0],-1,o.wallTile);toyWall('x',Y,-X,X,H,dr||null,W[1],1,o.wallTile);toyWall('z',-X,-Y,Y,H,null,W[2],-1,o.wallTile);toyWall('z',X,-Y,Y,H,null,W[3],1,o.wallTile);
  const cg=new THREE.PlaneGeometry(2*X,2*Y);cg.rotateX(Math.PI/2);const ce=new THREE.Mesh(cg,wallM('ceiling','#f4f1ea'));ce.position.y=H;ce.userData.noLift=true;world.add(ce);
  const sk=M.paint('skirting','#f6f4ee',.5),sb=(x0,x1,z0,z1)=>{const b=new THREE.Mesh(M.slab(Math.abs(x1-x0)||1.6*U,10*U,Math.abs(z1-z0)||1.6*U,.3*U,.3*U,2),sk);b.position.set((x0+x1)/2,5*U,(z0+z1)/2);b.userData.noLift=true;b.receiveShadow=true;world.add(b);};
  if(!o.noSkirt){if(!o.noNorthSkirt)sb(-X,X,-Y+.8*U,-Y+.8*U);sb(-X,dr[0]-9*U,Y-.8*U,Y-.8*U);sb(dr[1]+9*U,X,Y-.8*U,Y-.8*U);sb(-X+.8*U,-X+.8*U,-Y,Y);sb(X-.8*U,X-.8*U,-Y,Y);}
  const wcx=(win[0]+win[1])/2,wW=(win[1]-win[0])/U,wH=(win[3]-win[2])/U;toyPut(M.window(wW,wH),wcx,Y+4*U,0,win[2]);const out=M.outside(wW*2.6,wH*2.2,o.view);out.position.set(wcx,win[2]+wH*U*.55,-Y-60*U);out.userData.noLift=true;out.userData.envGain=6;world.add(out);TOYENV=o.env;
  if(dr&&!o.noDoor)toyPut(M.door(),(dr[0]+dr[1])/2,-Y+1*U,Math.PI,0);
  if(o.light==='tube'){for(const y of o.tubes||[-380,330])toyPut(M.tubelight(),0,y,0,H);}else{const g=new THREE.Group();M.add(g,M.cyl(17*U,17*U,2*U,32),M.paint('ceilrose','#f1eee6',.6),0,-1*U,0);M.add(g,new THREE.SphereGeometry(15*U,28,12,0,6.283,Math.PI/2,Math.PI/2),M.mat('ceilglass',()=>new THREE.MeshStandardMaterial({color:'#fffaf0',emissive:'#fff1d6',emissiveIntensity:.35,roughness:.4})),0,-2*U,0);toyPut(g,0,0,0,H);}}
/* a tiled surface: n x n tiles per texture in two colours with sunk grout lines; glossy, so it shows the window */
function toyTiles(key,c1,c2,grout,n,rough){return TM.mat('tiles_'+key,()=>{const S=512,q=S/n,c=TM.can('tile_'+key,S,S,(g,w,h,r)=>{for(let j=0;j<n;j++)for(let i=0;i<n;i++){g.fillStyle=(i+j)%2?c2:c1;g.fillRect(i*q,j*q,q,q);for(let k=0;k<160;k++){g.fillStyle='rgba('+(r()<.5?'255,255,255':'0,0,0')+','+r()*.04+')';g.fillRect(i*q+r()*q,j*q+r()*q,2+r()*10,2+r()*10);}}
      g.fillStyle=grout;for(let i=0;i<=n;i++){g.fillRect(i*q-2,0,4,S);g.fillRect(0,i*q-2,S,4);}}),
    b=TM.can('tileb_'+key,S,S,(g)=>{g.fillStyle='#b0b0b0';g.fillRect(0,0,S,S);g.fillStyle='#404040';for(let i=0;i<=n;i++){g.fillRect(i*q-3,0,6,S);g.fillRect(0,i*q-3,S,6);}}),
    m=new THREE.MeshStandardMaterial({map:T2(c,1,1),normalMap:T2(heightToNormal(b,1.6),1,1,true),normalScale:new THREE.Vector2(.6,.6),roughness:rough,metalness:0,envMapIntensity:.8});m.userData.noHQ=true;return m;});}
/* ---- Kitchen Chaos: a kitchen, 4.0 x 4.8 m. The numbers match tools/mini/t_kitchen.py ---- */
function toyKitchen(def){const U=TM.U,X=695,Y=833,H=868,M=TM,win=[-250,250,400,764],dr=[330,616,0,712],top=312,tab=260;
  toyShell({key:'k',X,Y,H,win,dr,walls:['#ece7dc','#ece7dc','#ece7dc','#c9d6c8'],floor:toyTiles('kfloor','#ebe5d6','#93a09c','#6f6a62',2,.3),tile:60,env:[-150,400,-330],noNorthSkirt:true,view:'k'});
  /* white tiles on the wall behind the worktop, up to the wall cabinets and under the window */
  {const tm=toyTiles('ksplash','#f6f5f0','#f1efe8','#c9c6bd',4,.22),pl=(x0,x1,y0,y1)=>{const g=new THREE.PlaneGeometry(x1-x0,y1-y0);const uv=g.attributes.uv;for(let i=0;i<uv.count;i++)uv.setXY(i,uv.getX(i)*(x1-x0)/(40*U),uv.getY(i)*(y1-y0)/(40*U));const m=new THREE.Mesh(g,tm);m.position.set((x0+x1)/2,(y0+y1)/2,-Y+.6);m.userData.noLift=true;m.receiveShadow=true;world.add(m);};
    pl(-X,win[0]-9*U,top,503);pl(win[0]-9*U,win[1]+9*U,top,win[2]-3*U);pl(win[1]+9*U,440,top,503);}
  /* ---- furniture ---- */
  toyPut(M.kcounter(),-147.5,725.5,0);TOYF.push([-695,400,-833,-618,top]);
  toyPut(M.kwallcab(),-487,776,0,503);{const wc=M.kwallcab();wc.scale.x=.45;toyPut(wc,345,776,0,503);}
  toyPut(M.kfridge(),567.5,715,0);
  toyPut(M.ktable(),0,-1,0);TOYF.push([-278,278,-138,140,tab]);
  toyPut(M.kchair(),-140,196,.08);toyPut(M.kchair(),44,204,-.12);toyPut(M.kchair(),-140,-218,Math.PI-.1);toyPut(M.kchair(),118,-230,Math.PI+.22);
  toyPut(M.kstool(),-460,-210,.4);toyPut(M.kshelf(),-643,200,Math.PI/2);
  /* on the worktop, behind the track; on the table, clear of it; on the fridge */
  toyPut(M.mug({color:'#c9573b'}),-560,798,.6,top);toyPut(M.plant({seed:7}),-640,792,0,top).scale.setScalar(.5);toyPut(M.sodacan(),-330,804,0,top);toyPut(M.books(3,12),60,800,.2,top);toyPut(M.mug(),150,806,2.1,top);
  toyPut(M.fruitbowl(),-150,70,0,tab);toyPut(M.plates(5),-30,84,0,tab);toyPut(M.mug({color:'#2f5d8a'}),70,104,1,tab);toyPut(M.carton(30,24,18),560,716,.15,180*U);
  /* on the floor: a runner in front of the worktop, the bin, shopping by the back door, things left lying about */
  toyPut(M.rug({w:55,l:150}),-110,562,Math.PI/2);toyPut(M.bin(),640,520,0);toyPut(M.grocery(),236,-774,.2);toyPut(M.grocery(),150,-766,-.3);toyPut(M.carton(42,32,22),640,-762,.1);
  toyPut(M.ball({kind:'tennis'}),360,-60,0);toyPut(M.bricks({seed:4,n:9,spread:8}),-640,-690,0);toyPut(M.cube({seed:7}),-250,-300,.5);toyPut(M.pencils({seed:3,n:3}),330,250,0);
  toyPut(M.setbox(),-370,-772,.1);toyPut(M.trackpiece({l:22}),-200,-752,-.5);
  /* the kitchen has its own wall art: a market print, a lettered print, and a clock over the door */
  toyPut(M.poster(50,70,3),689,-150,-Math.PI/2,470);toyPut(M.poster(42,60,4),-689,-430,Math.PI/2,440);toyPut(M.clock(),40,-Y+.6*U,Math.PI,560);
  /* where furniture keeps the light off the floor */
  toyShade(-278,278,-140,138,.4);toyShade(-695,400,560,833,.34);toyShade(440,695,590,833,.4);toyShade(-695,-591,44,356,.3);toyShade(-520,-400,-270,-150,.2);}
/* ---- what is outside the garage's open door: the front of the house. Real things at their real places, so the view shifts rightly as you drive past
   the doorway: the concrete drive, lawn either side, the pavement and the street, two houses over the road, trees, the sky.
   z0 is the outer face of the south wall. Everything out here stands in full sun (`sunlit`: it is outside the beam the room's shadows are worked out in). */
function toyFront(z0){const U=TM.U,M=TM,out=o=>{o.userData.noLift=true;o.userData.sunlit=true;o.userData.cast=false;o.castShadow=false;o.receiveShadow=false;o.traverse(q=>{if(q.isMesh){q.userData.sunlit=true;q.castShadow=false;q.receiveShadow=false;}});world.add(o);return o;},
    flat=(x0,x1,za,zb,m,tile,y)=>{const g=new THREE.PlaneGeometry(x1-x0,zb-za);g.rotateX(-Math.PI/2);M.uvw(g,tile);const o=new THREE.Mesh(g,m);o.position.set((x0+x1)/2,y,(za+zb)/2);return out(o);},
    slab=(x0,x1,za,zb,h,m,tile,y)=>{const o=new THREE.Mesh(M.uvw(new THREE.BoxGeometry(x1-x0,h,zb-za),tile),m);o.position.set((x0+x1)/2,y+h/2,(za+zb)/2);return out(o);},
    scan=typeof PROP_TEX!=='undefined'&&!!PROP_TEX.tex_toy_lawn,cm=M.surfTex('concrete',.8,.2,.9,()=>M.paint('fdrive','#bdbab2',.8)),pv=M.surfTex('paving',.82,.3,1,()=>M.paint('fpave','#c4bdb0',.8)),as=M.surfTex('asphalt',.9,.15,1,()=>M.paint('fasph','#4a4b4e',.9));
  flat(-9000,9000,z0,z0+2400,M.ylawn(),scan?70:240,-3);flat(-640,640,z0-12*U,z0+2420,cm,scan?110:240,-1.2);/* the drive runs in under the door, level with the garage floor */
  flat(-9000,9000,z0+2400,z0+2880,pv,scan?150:90,-1);slab(-9000,9000,z0+2880,z0+2930,14,M.paint('fkerb','#b7b2a8',.85),100,-13);flat(-9000,9000,z0+2930,z0+5330,as,300,-12);
  slab(-9000,9000,z0+5330,z0+5380,14,M.paint('fkerb','#b7b2a8',.85),100,-13);flat(-9000,9000,z0+5380,z0+5860,pv,scan?150:90,-1);flat(-9000,9000,z0+5860,z0+16000,M.ylawn(),scan?70:240,-3);
  /* a low brick wall along the front of the plot, open at the drive, with a pier each side of it */
  {const bk=M.surfTex('brick',.9,.2,1,()=>M.paint('fbrick','#9a5a44',.9)),cp=M.paint('fcope','#c9c3b6',.8);for(const sx of [-1,1]){slab(sx<0?-1750:700,sx<0?-700:1750,z0+2330,z0+2372,200,bk,140,0);slab(sx<0?-1756:694,sx<0?-694:1756,z0+2324,z0+2378,12,cp,100,200);slab(sx*700-34,sx*700+34,z0+2317,z0+2385,270,bk,140,0);slab(sx*700-40,sx*700+40,z0+2311,z0+2391,14,cp,100,270);}}
  /* the houses over the road, their windowed side toward us; the neighbours' fences; trees behind and between */
  for(const [x,z] of [[-2100,z0+8200],[2500,z0+8500],[6900,z0+8300],[-6600,z0+8400]]){const h=M.yPk&&M.yPk('yneigh');if(h){h.position.set(x,0,z);h.rotation.y=Math.PI;out(h);}}
  if(M.pkReady('yfence')&&M.pkReady('yfenceb'))for(const sx of [-1,1])for(let i=0;i<3;i++){const f=M.yPk(i%2?'yfenceb':'yfence');f.position.set(sx*1750,0,z0+2.125*347*(i+.5));f.rotation.y=sx*Math.PI/2;out(f);}
  const far=typeof PROP_TEX!=='undefined'&&PROP_TEX.tex_toy_treefar?M.mat('outsidetree',()=>{const t=propTex('tex_toy_treefar');t.userData.alpha=true;return new THREE.MeshBasicMaterial({map:t,color:new THREE.Color(1.45,1.45,1.4),alphaTest:.5,side:THREE.DoubleSide,toneMapped:false,fog:false});}):null;
  if(far)for(const [x,z,h,sd] of [[-3300,z0+1500,900,1],[3600,z0+1900,1050,2],[-900,z0+6500,1000,3],[4600,z0+6700,1150,4],[-4700,z0+6900,1100,5],[700,z0+11500,1300,6],[-3900,z0+11000,1250,7],[5200,z0+11800,1350,8],[9000,z0+7000,1200,9],[-9200,z0+7400,1200,10]]){
      const S=h*U*1.29;for(const q of [0,1]){const g=new THREE.PlaneGeometry(S,S),uv=g.attributes.uv,fl=sd%2===q;for(let i=0;i<4;i++)uv.setX(i,q*.5+(fl?1-uv.getX(i):uv.getX(i))*.5);const c=new THREE.Mesh(g,far);c.position.set(x,S/2-4*U,z);c.rotation.y=q?Math.PI/2:0;c.userData.noMerge=true;out(c);}}
  if(typeof PROP_TEX!=='undefined'&&PROP_TEX.tex_toy_sky){const sg=new THREE.SphereGeometry(16000,48,14,0,Math.PI*2,0,Math.PI*.53);sg.scale(-1,1,1);const sd=new THREE.Mesh(sg,M.mat('outsidesky',()=>new THREE.MeshBasicMaterial({map:propTex('tex_toy_sky'),toneMapped:false,fog:false})));
    sd.position.set(0,0,z0+3000);sd.rotation.y=Math.PI;/* (turned half round: the sky's bright side is where this room's sun is, in the south) */sd.userData.noMerge=true;sd.frustumCulled=false;out(sd);}
  {const b=M.sPk&&M.sPk('sball',false,.6);if(b){b.position.set(-1050,0,z0+700);out(b);}}}
/* an oil stain on the floor, about d units across */
function toyStain(x,y,d,a,rot){const m=TM.mat('goil'+a,()=>new THREE.MeshBasicMaterial({map:TM.tex(TM.stainCan(),'goil'),transparent:true,opacity:a,depthWrite:false,polygonOffset:true,polygonOffsetFactor:-1,polygonOffsetUnits:-1})),p=new THREE.Mesh(new THREE.PlaneGeometry(d,d),m);
  p.rotation.x=-Math.PI/2;p.rotation.z=rot||0;p.position.set(x,.3,-y);p.userData.noLift=true;p.userData.noMerge=true;p.renderOrder=1;world.add(p);}
/* ---- Garage Overdrive: a single garage, 4.0 x 4.8 m. The numbers match tools/mini/t_garage.py ----
   The garage is at the east end of the house: the door to the house is in its west wall, the big door in the south wall,
   and its window looks north onto the same garden as the bedroom's and the kitchen's (view 'g'). */
function toyGarage(def){const U=TM.U,X=695,Y=833,H=868,M=TM,win=[-420,80,430,764],top=312;
  /* the walls: painted brickwork from a scan (tools/blender/ph_tex.py, gbrick), 1.8 m to the repeat; plain paint until it is there */
  const gb=M.gbrick(),bw=gb?M.mat('pt_wallg',()=>{const m=gb.clone();m.userData.noHQ=true;return m;}):'#e6e3db';
  const dr=[-552,552,0,743];/* the big door's opening, 318 x 214 cm: the door is up, and the sun comes in through it (in this room it stands in the south) */
  toyShell({key:'g',X,Y,H,win,dr,noDoor:true,sun:[.22,.5,.84],beam:[[dr[0],dr[1],0,dr[3],Y,Y+12*U]],tubes:[190,610],walls:[bw,bw,bw,bw],wallTile:gb?180:0,floor:M.gconcrete(),tile:typeof PROP_TEX!=='undefined'&&PROP_TEX.tex_toy_concrete?110:240,env:[-60,400,-80],noSkirt:true,light:'tube',view:'g'});
  /* a grey band painted round the foot of the walls, as garages have */
  {const bm=gb?M.mat('gbandbrick',()=>{const m=gb.clone();m.color.set('#a9afb8');m.roughness=.7;m.userData.noHQ=true;return m;}):M.paint('gband','#8f9499',.7),bd=(x0,x1,z0,z1)=>{const g=new THREE.BoxGeometry(Math.abs(x1-x0)||.5*U,100*U,Math.abs(z1-z0)||.5*U),c=[(x0+x1)/2,50*U,(z0+z1)/2];
      if(gb){g.translate(c[0],c[1],c[2]);M.uvw(g,180);g.translate(-c[0],-c[1],-c[2]);}/* the same bricks as the wall behind it, course for course */const b=new THREE.Mesh(g,bm);b.position.set(c[0],c[1],c[2]);b.userData.noLift=true;b.receiveShadow=true;world.add(b);};
    bd(-X,X,-Y+.25*U,-Y+.25*U);bd(-X+.25*U,-X+.25*U,-Y,Y);bd(X-.25*U,X-.25*U,-Y,Y);bd(-X,-560,Y-.25*U,Y-.25*U);bd(560,X,Y-.25*U,Y-.25*U);}
  /* ---- the big door, the door to the house ---- */
  toyPut(M.gfit('gdooro'),0,-Y,Math.PI);toyPut(M.door(),-X+2.4*U,-560,Math.PI/2);toyFront(Y+12*U);
  /* ---- the workbench: along the east wall and returning along the north wall; the track runs along both ---- */
  toyPut(M.gbench(116),587.5,631.5,Math.PI/2);TOYF.push([480,695,-833,-430,top]);
  toyPut(M.gbench(101),305,725.5,0);TOYF.push([130,480,-833,-618,top]);
  /* on the bench, clear of the track (it takes x 543..633 on the east arm and y 681..771 on the north arm) */
  toyPut(M.gvice(),168,643,0,top);toyPut(M.paintcan('#c9573b'),436,803,1,top);toyPut(M.mug({color:'#3f6f8f'}),270,806,2,top);toyPut(M.sodacan(),666,806,0,top);toyPut(M.paintcan('#e9e3d2'),668,560,2,top);
  toyPut(M.pegboard(110,70),X-1*U,640,-Math.PI/2,400);toyPut(M.gsign(0),330,Y-.6*U,0,520);toyPut(M.gsign(2),560,Y-.6*U,0,640);toyPut(M.gsign(1),-X+.6*U,-120,Math.PI/2,700);toyPut(M.clock(),-X+.6*U,-560,Math.PI/2,770);
  /* ---- on the walls, built in Blender (tools/blender/garage.py): the electrics by the door to the house, a ladder hung on the east wall, garden tools on a rail ---- */
  toyPut(M.gfit('gelec'),-X,-300,Math.PI/2);toyPut(M.gfit('gladder'),X,-100,-Math.PI/2,677);toyPut(M.gfit('grack'),-X,430,Math.PI/2);
  /* ---- the rest of the furniture ---- */
  toyPut(M.gchest(),-582,746,0);toyPut(M.gtyres(4),-252,576,0).scale.setScalar(.78);/* smaller tyres (45 cm): at full size the stack touched the spiral's inner edge. tools/mini/clearcheck.py garage measures every loose thing against the lap */toyPut(M.gshelf(),-625,100,Math.PI/2);
  toyPut(M.carton(36,28,26),646,-774,.1);toyPut(M.carton(30,24,20),650,-776,-.2,26*U);toyPut(M.carton(50,36,28),-600,-770,.06);
  /* ---- on the floor, in the pockets the track leaves ---- */
  toyPut(M.gjack(),-170,-20,.5);toyPut(M.jerry('#4a5a3a'),70,430,.4);toyPut(M.paintcan('#e9e3d2'),40,530,1);toyPut(M.paintcan('#2f6f9f'),10,580,2);/* (the can stood in the spiral's outer edge) */
  toyPut(M.cone(),330,-420,0);toyPut(M.cone(),400,-250,0);toyPut(M.cone(),-520,-640,0);toyPut(M.gtyres(1),360,330,0).rotation.z=0;toyPut(M.gtoolbox(),330,60,-.5);
  toyPut(M.ball({kind:'tennis'}),-560,420,0);toyPut(M.bricks({seed:9,n:8,spread:8}),420,160,0);toyPut(M.cube({seed:3}),-90,-480,.4);
  toyPut(M.setbox(),120,-470,-.15);toyPut(M.trackpiece({l:22}),250,-520,.5);toyPut(M.skateboard(),-560,-300,1.4);
  /* oil where the car stands, and drips by the door */
  toyStain(330,-60,330,.55,.4);toyStain(250,300,220,.4,2);toyStain(-120,-420,200,.35,1);toyStain(60,60,150,.3,3);
  /* where furniture keeps the light off the floor */
  toyShade(480,695,430,833,.4);toyShade(130,480,618,833,.38);toyShade(-700,-464,666,826,.34);toyShade(-695,-556,-160,360,.34);toyShade(-340,-164,488,664,.3);}
/* ---- Backyard Mega Circuit: the whole back garden, 25 x 7 m, as tools/blender/outside.py draws it for the windows ----
   Garden coordinates in metres: x east from the bedroom window, y north from the house wall (0) to the back fence (7).
   The numbers match tools/mini/t_backyard.py. Outdoors: no window sun (TOYSUN stays empty), the ordinary sun and shadows. */
function toyYard(def){const U=TM.U,M=TM,m=100*U,GX=g=>(g+.75)*m,GY=g=>(g-3.5)*m,put=(o,gx,gy,ry,y0)=>toyPut(o,GX(gx),GY(gy),ry||0,y0||0),W0=-13.9,W1=11.6;
  renderer.toneMappingExposure=1;hemi.color.set('#d4e6ff');hemi.groundColor.set('#7c9a52');hemi.intensity=.8;sun.color.set('#fff0d2');sun.intensity=2.9;sunDir.set(-.1,.56,-.82).normalize();rimL.intensity=.18;rimL.color.set('#cfe0ff');
  scene.fog=new THREE.Fog('#cfe2f4',14000,70000);scene.background=new THREE.Color('#a8cdf3');Object.assign(POST.grade,{sat:1.06,con:1.04,tint:[1,1,.99],vig:.14,bloom:.2,thr:.97});TOYENV=null;/* no picture of the surroundings for reflections here: the open sky in it washed the glossy track out to pastel */
  /* the sky: a dome over the garden carrying the sky rendered in Blender from the garden's own scene (outside.py -- sky), the same sky the rooms' windows show.
     The picture runs all the way round (its left edge is east, then south, west, north) from straight up down to a little under the horizon.
     Drawn as it is (no lighting, no fog); 16 000 units out, which is past every tree and inside the camera's reach (22 000 web; the PC's is raised for this track). */
  if(typeof PROP_TEX!=='undefined'&&PROP_TEX.tex_toy_sky){const sg=new THREE.SphereGeometry(16000,48,14,0,Math.PI*2,0,Math.PI*.53);sg.scale(-1,1,1);/* turned inside out: its face is the inside */
    const sd=new THREE.Mesh(sg,M.mat('outsidesky',()=>new THREE.MeshBasicMaterial({map:propTex('tex_toy_sky'),toneMapped:false,fog:false})));sd.position.set(GX(-1.15),0,0);sd.userData.noLift=true;sd.userData.noMerge=true;sd.frustumCulled=false;world.add(sd);}
  const flat=(x0,x1,y0,y1,mat,tile,h)=>{const g=new THREE.PlaneGeometry((x1-x0)*m,(y1-y0)*m);g.rotateX(-Math.PI/2);M.uvw(g,tile);const p=new THREE.Mesh(g,mat);p.position.set(GX((x0+x1)/2),h,-GY((y0+y1)/2));p.receiveShadow=true;p.userData.noLift=true;world.add(p);return p;},
    wall=(x0,x1,y0,y1,h,mat,tile,h0,turn)=>{const g=M.uvw(new THREE.BoxGeometry(Math.max(.02,x1-x0)*m,h*m,Math.max(.02,y1-y0)*m),tile,turn),b=new THREE.Mesh(g,mat);b.position.set(GX((x0+x1)/2),((h0||0)+h/2)*m,-GY((y0+y1)/2));b.castShadow=true;b.receiveShadow=true;b.userData.noLift=true;world.add(b);return b;};
  /* the ground: lawn far past the fences, the patio along the house, a bed of earth under the back fence */
  const scan=typeof PROP_TEX!=='undefined'&&!!PROP_TEX.tex_toy_lawn;/* (not by asking surfTex: the first call makes the shared material) */flat(-60,60,-20,60,M.ylawn(),scan?70:240,-.1);flat(W0,W1,0,1.6,M.surfTex('paving',.82,.3,1,()=>toyTiles('ypatio','#cbc4b6','#bfb8aa','#8d887e',2,.75)),scan?150:90,-.04);
  if(scan){/* the mower's stripes, which the scanned grass does not have: faint darker bands 60 cm wide across the lawn */const c=M.can('ystripes',8,64,(g,w,h)=>{g.clearRect(0,0,w,h);g.fillStyle='rgba(0,0,0,1)';g.fillRect(0,0,w,h/2);}),t=T2(c,1,(W1-W0)/1.2),sp=flat(W0,W1,1.6,7,new THREE.MeshBasicMaterial({map:t,color:'#0a2a05',transparent:true,opacity:.13,depthWrite:false,polygonOffset:true,polygonOffsetFactor:-1,polygonOffsetUnits:-1}),100,-.06);
    const uv=sp.geometry.attributes.uv;for(let i=0;i<uv.count;i++)uv.setXY(i,0,(sp.geometry.attributes.position.getX(i)/((W1-W0)*m)+.5));uv.needsUpdate=true;sp.userData.noMerge=true;sp.receiveShadow=false;sp.renderOrder=1;}flat(-7.4,-.6,6.25,6.98,M.surfTex('soil',1,.1,1,()=>M.mat('ysoil',()=>new THREE.MeshStandardMaterial({color:'#4a3626',roughness:1}))),60,-.02);
  /* the house: its north wall with the three rooms' windows, a brick plinth, the eaves, a back door, a drainpipe and a tap */
  {const render=M.mat('yrender',()=>{const mm=new THREE.MeshStandardMaterial({color:'#ebe4d4',roughness:.92,envMapIntensity:.25});mm.userData.noHQ=true;return mm;}),brick=toyTiles('ybrick','#9a5a44','#8c4f3c','#cfc6b6',4,.9),dark=M.mat('yroom',()=>new THREE.MeshStandardMaterial({color:'#2b3038',roughness:.4,envMapIntensity:.9}));
    const bs=M.surfTex('brick',.9,.2,1,()=>null),hs=M.yPk('yhouse');/* a brick wall from a scan; the eaves, gutter, downpipes, roof, back door and lamp built in Blender (yardlib.house), in garden coordinates */
    if(bs)wall(W0,W1,-.3,0,3.0,M.mat('yhousebrick',()=>{const m=bs.clone();m.userData.noHQ=true;return m;}),140);else{wall(W0,W1,-.3,0,3.0,render,200);wall(W0,W1,-.31,.012,.42,brick,60);}
    if(hs)put(hs,0,0,0);else{wall(W0-.4,W1+.4,-.9,.45,.16,M.paint('yeaves','#f1efe8',.6),100,3.0);wall(W0-.4,W1+.4,-.9,.5,.5,M.paint('yroof','#5d6470',.7),100,3.16);}
    for(const [gx,sill,w] of [[-7,1.153,1.441],[0,1.153,1.441],[7.51,1.239,1.441]]){const hh=sill<1.2?1.049:.963;toyPut(M.window(w*100,hh*100),GX(gx),GY(0)+4*U,Math.PI,sill*m);const p=new THREE.Mesh(new THREE.PlaneGeometry(w*m*.94,hh*m*.94),dark);p.position.set(GX(gx),(sill+hh/2)*m,-GY(0)-.4*U);p.rotation.y=Math.PI;p.userData.noLift=true;world.add(p);
      wall(gx-w/2-.06,gx+w/2+.06,0,.07,.05,M.paint('ysill','#f1efe8',.5),100,sill-.05);}
    if(!hs){toyPut(M.door(),GX(-4.3),GY(0)+2*U,Math.PI);wall(-4.85,-3.75,0,.5,.03,M.paint('ystep','#b9b3a6',.8),100,0);
      const pipe=new THREE.Mesh(M.cyl(4*U,4*U,3*m,12),M.paint('ydrain','#3a3d42',.5));pipe.position.set(GX(3.3),1.5*m,-GY(.06));pipe.userData.noLift=true;pipe.castShadow=true;world.add(pipe);}{const sh=M.sPk('shose',false,.55);if(sh)put(sh,-2.4,0,0,1.05*m);/* a scanned hose on its wall bracket */else put(M.yhose(),-2.4,.35);}}
  /* the fences: the back one and the two sides */
  if(M.pkReady('yfence')&&M.pkReady('yfenceb')){/* built in Blender, bay by bay (2.125 m): twelve along the back, three down each side stretched to fit; a bay's post is at its west end, so every joint and corner has one */
    const B=2.125,bay=i=>M.yPk(i%2?'yfenceb':'yfence'),sc=7/(3*B);for(let i=0;i<12;i++)put(bay(i),W0+B*(i+.5),7,0);
    for(let i=0;i<3;i++){put(bay(i+1),W0,7*(i+.5)/3,Math.PI/2).scale.x=sc;put(bay(i),W1,7*(i+.5)/3,-Math.PI/2).scale.x=sc;}}
  else{const fm=M.yboards('fence','#9a7650',false);wall(W0,W1,7,7.04,1.8,fm,100,0,true);wall(W0-.04,W0,0,7.04,1.8,fm,100,0,true);wall(W1,W1+.04,0,7.04,1.8,fm,100,0,true);for(let x=W0;x<=W1;x+=2.2)wall(x-.045,x+.045,6.93,7.0,1.9,fm,100,0,true);}
  /* the shed, the washing line, the tree, the goal: where every window's picture has them */
  put(M.yPk('yshed')||M.yshed(),-11.2,5.4,0);
  if(M.pkReady('ywash'))put(M.yPk('ywash'),-5.8,4.2,0);else{const steel=M.metal('ypole','#b9bcc2',.45);for(const px of [-8.2,-3.4]){const p=new THREE.Mesh(M.cyl(2.5*U,2.5*U,2*m,10),steel);p.position.set(GX(px),m,-GY(4.2));p.castShadow=true;p.userData.noLift=true;world.add(p);}wall(-8.2,-3.4,4.195,4.205,.01,steel,100,1.95);
    [[-7.2,'#d9534f',.62],[-6.3,'#f4f1ea',.72],[-5.3,'#4f86c6',.62],[-4.4,'#f0c040',.72]].forEach(([px,c,hh])=>{const g=new THREE.PlaneGeometry(.62*m,hh*m,6,6),pp=g.attributes.position;for(let i=0;i<pp.count;i++)pp.setZ(i,Math.sin(pp.getX(i)*.02+px)*4*U*(.5-pp.getY(i)/(hh*m)));g.computeVertexNormals();
      const cl=new THREE.Mesh(g,M.mat('ycloth'+c,()=>new THREE.MeshStandardMaterial({color:c,roughness:.95,side:THREE.DoubleSide})));cl.position.set(GX(px),(1.94-hh/2)*m,-GY(4.2));cl.castShadow=true;cl.userData.noLift=true;world.add(cl);});}
  put((typeof PROP_TEX!=='undefined'&&PROP_TEX.tex_toy_sprays&&M.yPk('ytreec'))||M.yPk('ytree')||M.ytree(620,250,3),3.1,5.2,0);/* the garden tree: with cut-out sprays of real leaves if they are there */put(M.yPk('ygoal')||M.ygoal(),9.6,5.6,0);/* its mouth faces the house; the back (-z in the model) is north */{const sb=M.sPk('sball',false,.6);if(sb)put(sb,7.4,3.9,1.1);else if(M.pkReady('yball'))put(M.yPk('yball'),7.4,3.9,1.1);else{const b=new THREE.Mesh(new THREE.SphereGeometry(11*U,24,16),M.paint('yball','#f4f4f0',.45));b.position.set(GX(7.4),11*U,-GY(3.9));b.castShadow=true;b.userData.noLift=true;world.add(b);}}
  /* over the fence: the neighbour's house and the trees beyond */
  {if(M.pkReady('yneigh')){put(M.yPk('yneigh'),-2.5,23,0);put(M.yPk('yneigh'),21.5,2.6,Math.PI/2);put(M.yPk('yneigh'),-24.5,4.4,-Math.PI/2);}/* the neighbours: the house over the back fence (the one every window shows) and one beyond each side fence */
    else{const hw=M.paint('ysiding','#e6dcc8',.8),hr=M.paint('yroof','#5d6470',.7);wall(-7.5,2.5,19.5,26.5,3.2,hw,300);const rg=new THREE.ConeGeometry(7.6*m,2.6*m,4,1);rg.rotateY(Math.PI/4);rg.scale(1,1,.72);const rf=new THREE.Mesh(rg,hr);rf.position.set(GX(-2.5),4.5*m,-GY(23));rf.userData.noLift=true;world.add(rf);}
    const far=typeof PROP_TEX!=='undefined'&&PROP_TEX.tex_toy_treefar?M.mat('outsidetree',()=>{const t=propTex('tex_toy_treefar');t.userData.alpha=true;return new THREE.MeshBasicMaterial({map:t,color:new THREE.Color(1.45,1.45,1.4),alphaTest:.5,side:THREE.DoubleSide,toneMapped:false,fog:false});}):null;
    for(const [x,y,h,cr,sd] of [[-4.6,11.5,850,340,5],[6.5,15,950,380,7],[-10.5,17,900,360,9],[12.5,26,1100,440,12],[3.5,31,1200,480,14],[-15,33,1200,500,17],[16.2,6.2,900,360,23],[18.5,12.5,1050,420,27],[-18.6,9.5,950,380,31],[-21,15,1100,440,35],[20,19,1150,460,39]]){if(far){/* a real tree's picture on two crossed cards (treecards.py: seen from the south on one, from the east on the other), shown as it is */const S=h*U*1.29;for(const q of [0,1]){const g=new THREE.PlaneGeometry(S,S),uv=g.attributes.uv,fl=sd%2===q;for(let i=0;i<4;i++)uv.setX(i,q*.5+(fl?1-uv.getX(i):uv.getX(i))*.5);
          const c=new THREE.Mesh(g,far);c.position.set(GX(x),S/2-4*U,-GY(y));c.rotation.y=q?Math.PI/2:0;c.userData.noLift=true;c.userData.noMerge=true;c.userData.cast=false;world.add(c);}}
        else{const t=M.yPk('ytreef');if(t){t.scale.setScalar(h/1000);put(t,x,y,sd);}else put(M.ytree(h,cr,sd),x,y,sd);}}}
  /* along the way */
  put(M.ypot(15,5),5.0,.5,0);put(M.wcan(),4.5,1.72,2.4);put(M.ypot(13,8),-1.2,.3,0);put(M.ypot(17,3),1.4,.32,0);put(M.ypot(14,12),6.3,.3,0);put(M.ypot(16,21),-8.6,.34,0);
  if(M.pkReady('ypipe'))put(M.yPk('ypipe'),-3.6,5.71,0);else{const pp=M.ypipe(37,150);pp.position.set(GX(-3.6),20,-GY(5.71));pp.userData.noLift=true;pp.traverse(o=>{if(o.isMesh){o.castShadow=true;o.receiveShadow=true;}});world.add(pp);}
  /* tufts of longer grass where a mower does not reach: along the fences, round the shed, the tree and the poles, a few on the lawn; none on or near the track */
  if(M.pkReady('ytuft')&&typeof track!=='undefined'&&track.length){const SG=['sgrassa','sgrassb','sgrassc'].map(n=>M.sPk(n,true,1,'grass','#b9c8a2')).filter(Boolean),/* scanned clumps of grass, cut out of their picture: used when all three are there */scan=SG.length===3,
      tg=M.yPk('ytuft').children[0],L=[],LS=[[],[],[]],r=M.rng(77),near=(x,z)=>{for(let j=0;j<N;j+=3){const p=track[j];if((p.x-x)**2+(p.y-z)**2<5600)return true;}return false;},
      tuft=(gx,gy)=>{const x=GX(gx),z=-GY(gy);if(near(x,z))return;const k=.55+r()*.6;if(scan){const q=.5+r()*.45;LS[Math.floor(r()*3)].push({x,y:0,z,ry:r()*6.283,sx:q,sy:q*(.8+r()*.4),sz:q});}else L.push({x,y:0,z,ry:r()*6.283,sx:k,sy:k*(.7+r()*.5),sz:k});};
    for(let x=W0+.05;x<W1;x+=.08+r()*.13)tuft(x,6.95-r()*.07);
    for(let y=1.68;y<6.9;y+=.09+r()*.14){tuft(W0+.05+r()*.07,y);tuft(W1-.05-r()*.07,y);}
    for(let t=0;t<8.6;t+=.1+r()*.12){const q=t<2.4?[-12.4+t,4.42-r()*.05]:t<4.3?[-9.97+r()*.05,4.45+t-2.4]:t<6.7?[-10+2.4-(t-4.3)-2.4,6.38+r()*.05]:[-12.43-r()*.05,6.35-(t-6.7)];tuft(q[0],q[1]);}
    for(let i=0;i<16;i++){const a=i/16*6.283+r();tuft(3.1+Math.cos(a)*(.33+r()*.08),5.2+Math.sin(a)*(.33+r()*.08));}
    for(const [px,py] of [[-8.2,4.2],[-3.4,4.2],[8.6,5.6],[10.6,5.6],[8.6,6.3],[10.6,6.3]])for(let i=0;i<5;i++){const a=r()*6.283;tuft(px+Math.cos(a)*.07,py+Math.sin(a)*.07);}
    for(let i=0;i<90;i++)tuft(W0+.4+r()*(W1-W0-.8),1.9+r()*4.8);
    if(scan)SG.forEach((g,i)=>{const c=g.children[0],tm=instBatch(c.geometry,c.material,LS[i],false);if(tm)tm.userData.noMerge=true;});else{const tm=instBatch(tg.geometry,tg.material,L,false);if(tm)tm.userData.noMerge=true;}}
  for(const [gx,sd] of [[-6.9,2],[-5.9,6],[-4.9,9],[-2.6,13],[-1.5,17]])put(M.ypot(13+sd%5,sd),gx,6.62,sd).position.y=-10*U;
  put(M.ygnome(),2.2,4.3,2.6);put(M.jerry('#b3261c'),-9.7,4.75,.4);put(M.cone(),-12.2,3.95,0);put(M.gtyres(1),10.9,2.2,0);put(M.skateboard(),-3.3,1.2,.3);put(M.sneaker?M.sneaker():M.cube({seed:2}),-4.0,.55,.6);
  put(M.setbox(),1.6,1.45,-.2);put(M.trackpiece({l:22}),2.5,1.5,.6);put(M.ball({kind:'tennis'}),-10.3,2.6,0);put(M.bricks({seed:5,n:9,spread:9}),6.9,1.5,0);put(M.cube({seed:8}),-6.2,2.7,.5);
  /* shade the sun's own shadow map does not reach: under the tree, north of the shed and of the back fence */
  toyShade(GX(1.2),GX(5),GY(4.2),GY(6.9),.3);toyShade(GX(-12.6),GX(-9.8),GY(6.1),GY(6.95),.4);toyShade(GX(-11),GX(9),GY(6.6),GY(7),.25);}
function buildToy(def){TOYF=[];TOYP=[];TOYB=[];if(def.look==='bedroom')toyBedroom(def);else if(def.look==='kitchen')toyKitchen(def);else if(def.look==='garage')toyGarage(def);else if(def.look==='backyard')toyYard(def);else if(def.look==='battle')toyBattle(def);}
/* ---- Prep Table Showdown: the Balloon Battle arena (the shapes that are its floor and walls: bbArena in battle.js) ----
   A pizzeria's steel prep table, at the toy scale: the table top is the floor, the kitchen's own floor is 90 cm below. */
function toyBattle(def){const U=TM.U,M=TM;battleSetup(def);
  renderer.toneMappingExposure=.98;hemi.color.set('#dfe6f0');hemi.groundColor.set('#b9a892');hemi.intensity=.62;sun.color.set('#fff0d8');sun.intensity=2.2;sunDir.set(-.25,.82,-.5).normalize();rimL.intensity=.16;rimL.color.set('#cfe0ff');
  scene.fog=new THREE.Fog('#d8cfc0',6000,30000);scene.background=new THREE.Color('#d9d2c6');Object.assign(POST.grade,{sat:1.04,con:1.05,tint:[1.01,1,.985],vig:.16,bloom:.2,thr:.97});TOYENV=null;
  const add=(g,m,x,y,z,cast)=>{const o=new THREE.Mesh(g,m);o.position.set(x,y,z);o.castShadow=cast!==false;o.receiveShadow=true;o.userData.noLift=true;world.add(o);return o;},
    steel=M.mat('bbsteel',()=>{const m=new THREE.MeshStandardMaterial({color:'#c2c6ca',roughness:.38,metalness:.25,envMapIntensity:.9});m.userData.noHQ=true;return m;}),
    K={rim:steel,bin:M.mat('bbbin',()=>new THREE.MeshStandardMaterial({color:'#aeb3b8',roughness:.3,metalness:.3,envMapIntensity:.9})),lid:M.paint('bbcard','#c79a5e',.85),boxes:M.paint('bbcard','#c79a5e',.85),board:M.paint('bbwood','#b98a58',.6),bread:M.paint('bbwood','#b98a58',.6),
      mill:M.paint('bbmill','#5a3a22',.45),pin:M.paint('bbpin','#d9b98a',.5),plates:M.paint('bbplate','#f4f1ea',.3)};
  /* the table top, and the kitchen floor far below it */
  /* the Blender-built models (tools/blender/battle.py) stand in for each kind of shape once their packs have arrived; plain blocks of the same shapes until then */
  const PK={bbtable:['rim'],bbbins:['bin'],bbboxes:['boxes','lid'],bbblock:['board','bread'],bbprops:['mill','pin','plates']},done={};
  for(const n in PK){const o=M.bPk(n);if(o){toyPut(o,0,0,0);for(const k of PK[n])done[k]=1;}}
  {const f=new THREE.PlaneGeometry(6000,6000);f.rotateX(-Math.PI/2);add(f,toyTiles('kfloor','#ebe5d6','#93a09c','#6f6a62',2,.3),0,-312,0,false);
    if(!done.rim){const g=new THREE.PlaneGeometry(768,520);g.rotateX(-Math.PI/2);add(g,steel,-4,-.05,0,false);add(new THREE.BoxGeometry(768,14,520),steel,-4,-7.2,0,false);for(const sx of [-1,1])for(const sz of [-1,1])add(new THREE.BoxGeometry(16,298,16),steel,sx*364,-163,sz*240);}}
  /* the alcove's three walls, tiled, from the kitchen floor up; the room's far wall and ceiling */
  {const tm=toyTiles('ksplash','#f6f5f0','#f1efe8','#c9c6bd',4,.22),wall=(w,x,z,ry)=>{const g=new THREE.PlaneGeometry(w,1200),uv=g.attributes.uv;for(let i=0;i<uv.count;i++)uv.setXY(i,uv.getX(i)*w/(40*U),uv.getY(i)*1200/(40*U));const o=add(g,tm,x,288,z,false);o.rotation.y=ry;};
    wall(900,-10,-260,0);wall(900,-10,260,Math.PI);wall(520,380,0,-Math.PI/2);wall(3000,-1700,0,Math.PI/2);const cg=new THREE.PlaneGeometry(3000,3000);cg.rotateX(Math.PI/2);add(cg,M.paint('bbceil','#f4f1ea',.9),-400,888,0,false);}
  for(const q of BB.shapes){if(q.k==='wall'||done[q.k])continue;const m=K[q.k]||steel;
    if(q.t==='cyl')add(new THREE.CylinderGeometry(q.r,q.r,q.h,32),m,q.x,q.h/2,q.z);
    else if(q.t==='box')add(new THREE.BoxGeometry(q.x1-q.x0,q.h,q.z1-q.z0),m,(q.x0+q.x1)/2,q.h/2,(q.z0+q.z1)/2);
    else{/* a ramp: a wedge */const w=q.x1-q.x0,d=q.z1-q.z0,P=q.ax==='x'?[[q.x0,q.h0,q.z0],[q.x1,q.h1,q.z0],[q.x1,q.h1,q.z1],[q.x0,q.h0,q.z1]]:[[q.x0,q.h0,q.z0],[q.x1,q.h0,q.z0],[q.x1,q.h1,q.z1],[q.x0,q.h1,q.z1]],B=P.map(v=>[v[0],0,v[2]]),V=[],quad=(a,b,c,e)=>V.push(...a,...b,...c,...a,...c,...e);
      quad(P[0],P[3],P[2],P[1]);quad(P[0],P[1],B[1],B[0]);quad(P[1],P[2],B[2],B[1]);quad(P[2],P[3],B[3],B[2]);quad(P[3],P[0],B[0],B[3]);const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(V,3));g.computeVertexNormals();const o=add(g,m,0,0,0);o.material=m.clone();o.material.side=THREE.DoubleSide;}}}
function toyScenery(def){if(def.battle)return;toyRails(def);TOYB.forEach(j=>toyBooster(j));/* the motor housings go on last, once the shortcuts are known */}
