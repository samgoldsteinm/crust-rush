(()=>{/* 1. what the layout says, without driving: every item box stands on open ground (nothing solid and no edge within 12 of it), every spawn is free with 60 clear ahead of it, and the drivers' map reaches every box from every spawn */
  const o={x:0,z:0},bad=[];
  boxes.forEach((b,i)=>{const g=battleG(b.x,b.y);let m=1e9;for(let a=0;a<16;a++)for(const r of [6,12]){const h=battleG(b.x+Math.cos(a*.3927)*r,b.y+Math.sin(a*.3927)*r);if(Math.abs(h-g)>BB_STEP)m=Math.min(m,r);}if(m<1e9||Math.abs(g-b.gy)>.01)bad.push('box '+i+' at '+b.x+','+b.y+': something within '+m);});
  BB.spawn.forEach((s,i)=>{const g=battleG(s[0],s[1]);if(bbTouch(s[0],s[1],g,o))bad.push('spawn '+i+' touches something');if(!bbClear(s[0],s[1],g,s[0]+Math.cos(s[2])*60,s[1]+Math.sin(s[2])*60))bad.push('spawn '+i+' has no 60 clear ahead');
    let near=1e9;BB.spawn.forEach((q,j)=>{if(j!==i)near=Math.min(near,Math.hypot(q[0]-s[0],q[1]-s[1]));});if(near<200)bad.push('spawn '+i+' is only '+Math.round(near)+' from another');
    boxes.forEach((b,bi)=>{if(!bbPath({x:s[0],y:s[1],wy:g},b.x,b.y,false))bad.push('no way from spawn '+i+' to box '+bi);});});
  return {layout:bad.length?bad:'ok: '+boxes.length+' boxes, '+BB.spawn.length+' spawns'};})()
----
(()=>{/* 2. every item box reached and taken, by a kart that drives there from the last spawn along the drivers' own map */
  __solo();const out=[];let worst=0;
  for(let bi=0;bi<boxes.length;bi++){const b=boxes[bi],s=BB.spawn[BB.spawn.length-1];boxes.forEach(q=>q.r=0);__put(s[0],s[1],s[2]);
    window.__drv=(k,dt)=>{const q={steer:0,drift:false,brake:false,mul:1,use:false,back:false,hold:false,holdSl:1,release:null},W=bbPath(k,b.x,b.y,false)||[b.x,b.y];q.steer=clamp(angDiff(Math.atan2(W[1]-k.y,W[0]-k.x),k.a)*2.2,-1,1);if(Math.abs(q.steer)>.9&&k.speed>70)q.mul=.25;if(Math.hypot(b.x-k.x,b.y-k.y)<70&&Math.abs(q.steer)>.5)q.mul=k.speed>40?0:.3;/* (close and not pointing at it: slow right down, do not circle it) */return q;};
    const t=__run(60,()=>b.r>0);if(t<0)out.push('box '+bi+' at '+b.x+','+b.y+' NOT TAKEN in 60 s (kart at '+Math.round(player.x)+','+Math.round(player.y)+')');else worst=Math.max(worst,t);}
  window.__drv=null;return {taken:out.length?out:'ok: all '+boxes.length+' taken, the slowest in '+worst.toFixed(1)+' s'};})()
----
(()=>{/* 3. a kart driven at every wall and every thing on the table, from each side at three places: where it stops against the game's shape, and how far
     the nearest DRAWN surface in front of it then is (a ray from the kart at each height from 2 to 10). Both should be next to nothing: listed when
     the kart stops more than 1.5 short of, or sunk more than 1.5 into, what is drawn. */
  __solo();const rc=new THREE.Raycaster(),o={x:0,z:0},R=BB_R,list=[],all=[];let n=0;
  const tryAt=(name,px,pz,dx,dz,hTop)=>{const sx=px-dx*45,sz=pz-dz*45;if(sx<-BB_X+8||sx>BB_X-8||Math.abs(sz)>BB_Z-8)return;const g0=battleG(sx,sz);if(g0<-100||hTop-g0<=BB_STEP||bbTouch(sx,sz,g0,o))return;
    if(!bbClear(sx,sz,g0,px-dx*(R+2),pz-dz*(R+2)))return;if(battleG(px+dx*1.5,pz+dz*1.5)-battleG(px-dx*1.5,pz-dz*1.5)<=BB_STEP)return;/* (no wall at this place: a ramp's end, or the ledge a ramp leads onto) */
    __put(sx,sz,Math.atan2(dz,dx));window.__drv=()=>({steer:0,drift:false,brake:false,mul:.5,use:false,back:false,hold:false,holdSl:1,release:null});__run(1.8);
    const k=player,solid=-((k.x-px)*dx+(k.y-pz)*dz)-R;let best=1e9;for(let h=2;h<=10;h++){rc.set(new THREE.Vector3(k.x,(k.wy||0)+h,k.y),new THREE.Vector3(dx,0,dz));rc.far=80;const I=rc.intersectObjects(world.children,true);for(const q of I){if(q.object.visible===false||(q.object.userData&&q.object.userData.sbx))continue;best=Math.min(best,q.distance);break;}}
    const drawn=best>1e8?null:best-R;n++;all.push(drawn);if(drawn===null||Math.abs(drawn)>1.5||Math.abs(solid)>1.2)list.push(name+' at '+Math.round(px)+','+Math.round(pz)+' heading '+dx+','+dz+': stops '+solid.toFixed(2)+' from the shape, '+(drawn===null?'NOTHING DRAWN ahead':drawn.toFixed(2)+' from what is drawn'));};
  for(const s of BB.shapes){const nm=s.k+(s.i!=null?s.i:'');
    if(s.t==='cyl'){for(let a=0;a<8;a++){const dx=+Math.cos(a*.7854).toFixed(4),dz=+Math.sin(a*.7854).toFixed(4);tryAt(nm,s.x-dx*s.r,s.z-dz*s.r,dx,dz,s.h);}continue;}
    const hi=s.t==='box'?s.h:Math.max(s.h0,s.h1);
    for(const f of [.2,.5,.8]){const x=s.x0+(s.x1-s.x0)*f,z=s.z0+(s.z1-s.z0)*f,hx=s.t==='box'?s.h:s.ax==='z'?s.h0+(s.h1-s.h0)*f:null,hz=s.t==='box'?s.h:s.ax==='x'?s.h0+(s.h1-s.h0)*f:null;
      if(s.k!=='wall'||s.x0>=BB_X){tryAt(nm,s.x0,z,1,0,hx==null?s.h0:hx);}if(s.k!=='wall'&&s.k!=='rim')tryAt(nm,s.x1,z,-1,0,hx==null?s.h1:hx);if(s.k==='rim')tryAt(nm,s.x1,z,-1,0,s.h);
      if(s.k!=='wall'||s.z0>=BB_Z)tryAt(nm,x,s.z0,0,1,hz==null?s.h0:hz);if(s.k!=='wall'||s.z1<=-BB_Z)tryAt(nm,x,s.z1,0,-1,hz==null?s.h1:hz);}}
  window.__drv=null;const d=all.filter(v=>v!==null);return {walls:n+' places driven at; drawn against solid: least '+Math.min(...d).toFixed(2)+', most '+Math.max(...d).toFixed(2),over:list.length?list:'none over 1.5'};})()
