
/* ================= SANDBOX: the world map and fast travel =================
   The owner's brief, section 3 (docs/NEXT-MODES-BRIEF.md). Opened while driving with Select / View / Back / Minus on a controller or M on a
   keyboard (again, or Back, returns to driving); on a phone from the pause menu, where Map sits directly under Resume (Back returns to the
   pause menu with Resume ready). It shows the world from above as it really is: SB_WORLD says where each region sits (metres: x east, y
   north, the house's garden wall along y = 0) and how a place in the region becomes a place on the map. Each region's track is drawn from
   its own lap. Region names are plain labels; the chequered pins are the fast-travel points (each track's start line). Picking a pin names
   it and asks; going there is the same dark duct as a passage. Hidden things are not on the map. */
const SB_WORLD={
  backyard:{name:'BACK GARDEN',box:[-13.9,11.6,0,7],at:(x,z)=>[x/SB_M-.75,3.5-z/SB_M],fill:'#4d8a3c'},
  kitchen:{name:'KITCHEN',box:[-9,-5,-4.8,0],at:(x,z)=>[-7+x/SB_M,-2.4-z/SB_M],fill:'#d9d3c6'},
  bedroom:{name:'BEDROOM',box:[-2,2,-4.8,0],at:(x,z)=>[x/SB_M,-2.4-z/SB_M],fill:'#c9a877'},
  garage:{name:'GARAGE',box:[5.5,9.5,-4.8,0],at:(x,z)=>[7.5+x/SB_M,-2.4-z/SB_M],fill:'#b9bbbd'}};
/* parts of the house that are on the map but not yet places to drive */
const SB_WORLD_MORE=[{name:'HALL',box:[-5,-2,-4.8,0]},{name:'',box:[2,5.5,-4.8,0]}];
const SBM={el:null,cv:null,open:false,from:'',pick:null,trk:{},pins:[],view:[-14.6,12.3,-6.3,7.7]};
function sbMapTrack(id){if(SBM.trk[id])return SBM.trk[id];const def=MAPS.find(m=>m.id===id);if(!def)return null;let t;try{t=makeTrack(def,false);}catch(e){return null;}const W=SB_WORLD[id],o=[];const st=Math.max(1,Math.floor(t.length/400));for(let j=0;j<t.length;j+=st)o.push(W.at(t[j].x,t[j].y));
  SBM.trk[id]={pts:o,start:W.at(t[0].x,t[0].y),name:def.name};return SBM.trk[id];}
function sbMapEl(){let e=SBM.el;if(e)return e;e=SBM.el=document.createElement('div');e.id='sbMap';e.className='overlay';e.hidden=true;
  e.innerHTML='<div class="panel" style="max-width:980px;gap:8px"><div style="display:flex;align-items:baseline;gap:12px"><h2 class="res-title" style="margin:0;font-size:26px">Map</h2><span style="opacity:.75;font-weight:700">Home</span><span style="flex:1"></span><span style="font-size:12px;opacity:.7" id="sbMapKey"></span></div>'
    +'<div id="sbMapBox" style="position:relative;width:100%;border-radius:14px;overflow:hidden;background:#1b120d;box-shadow:inset 0 0 0 2px rgba(255,255,255,.08)"><canvas id="sbMapCv" style="display:block;width:100%"></canvas></div>'
    +'<div id="sbMapAsk" style="min-height:52px;display:flex;align-items:center;gap:10px;flex-wrap:wrap"><span id="sbMapSay" style="flex:1;font-weight:700"></span><button id="sbMapGo" class="cta" style="padding:10px 18px;font-size:17px" hidden>Travel here</button><button id="sbMapNo" class="ghost" hidden>Cancel</button><button id="sbMapBack" class="ghost back" data-back="1">Back</button></div></div>';
  stage.appendChild(e);SBM.cv=e.querySelector('#sbMapCv');
  e.querySelector('#sbMapBack').onclick=()=>sbMap(false);e.querySelector('#sbMapNo').onclick=()=>{sbMapPick(null);};e.querySelector('#sbMapGo').onclick=()=>{const p=SBM.pick;if(p)sbMapTravel(p.id);};
  addEventListener('keydown',ev=>{if(SBM.open&&(ev.code==='Escape'||ev.code==='KeyM')){ev.preventDefault();ev.stopImmediatePropagation();if(SBM.pick&&ev.code==='Escape')sbMapPick(null);else sbMap(false);}else if(!SBM.open&&SBX&&state==='race'&&ev.code==='KeyM'&&!ev.repeat){ev.preventDefault();sbMap(true,'drive');}},true);
  return e;}
function sbMapPick(p){SBM.pick=p;const e=sbMapEl(),say=e.querySelector('#sbMapSay'),go=e.querySelector('#sbMapGo'),no=e.querySelector('#sbMapNo');
  if(p){say.textContent=p.track+' · the start line, '+SB_WORLD[p.id].name.charAt(0)+SB_WORLD[p.id].name.slice(1).toLowerCase();go.hidden=false;no.hidden=false;go.focus();}
  else{say.textContent='The chequered pins are places you can travel to. Everything on the map can be driven to.';go.hidden=true;no.hidden=true;}
  for(const q of SBM.pins)q.b.setAttribute('aria-pressed',String(!!p&&q.id===p.id));sbMapDraw();}
/* the picture: drawn each time the map opens, and again as the selection changes */
function sbMapDraw(){const cv=SBM.cv,box=cv.parentNode,V=SBM.view,wCss=box.clientWidth||600,asp=(V[3]-V[2])/(V[1]-V[0]),hCss=Math.round(wCss*asp),dpr=Math.min(2,window.devicePixelRatio||1);cv.width=Math.round(wCss*dpr);cv.height=Math.round(hCss*dpr);cv.style.height=hCss+'px';
  const g=cv.getContext('2d'),s=cv.width/(V[1]-V[0]),X=x=>(x-V[0])*s,Y=y=>(V[3]-y)*s,rect=(b,f,st,lw)=>{g.beginPath();g.rect(X(b[0]),Y(b[3]),(b[1]-b[0])*s,(b[3]-b[2])*s);if(f){g.fillStyle=f;g.fill();}if(st){g.strokeStyle=st;g.lineWidth=lw||2;g.stroke();}};
  g.fillStyle='#22301f';g.fillRect(0,0,cv.width,cv.height);
  /* the ground outside the fences, the garden with its patio, the house with its rooms */
  rect(SB_WORLD.backyard.box,SB_WORLD.backyard.fill);rect([-13.9,11.6,0,1.6],'#cfc6b3');rect(SB_WORLD.backyard.box,null,'#6b4f33',3*dpr);
  rect([-9.2,9.7,-5.0,0],'#8f6f5a');for(const m of SB_WORLD_MORE)rect(m.box,'#b8ad9c','#5b4636',1.5*dpr);for(const id of ['kitchen','bedroom','garage'])rect(SB_WORLD[id].box,SB_WORLD[id].fill,'#5b4636',2*dpr);
  rect([-14.6,12.3,-6.3,-5.0],'#55585c');/* the street in front */
  /* the tracks */g.lineJoin='round';g.lineCap='round';for(const id in SB_WORLD){const t=sbMapTrack(id);if(!t)continue;for(const [col,w] of [['#7a2a05',.36],['#ff7a1e',.26]]){g.beginPath();t.pts.forEach((p,i)=>i?g.lineTo(X(p[0]),Y(p[1])):g.moveTo(X(p[0]),Y(p[1])));g.closePath();g.strokeStyle=col;g.lineWidth=Math.max(2,w*s);g.stroke();}}
  /* the passages: a dot at each end and a dotted line between */
  g.setLineDash([5*dpr,5*dpr]);g.strokeStyle='rgba(20,12,8,.8)';g.lineWidth=2*dpr;for(const id in SB_WORLD)for(const d of (SB_REG[id]&&SB_REG[id].gates)||[]){if(id>d.to)continue;const a=sbMapGate(id,d.id),b=sbMapGate(d.to,d.at);if(!a||!b)continue;g.beginPath();g.moveTo(X(a[0]),Y(a[1]));g.lineTo(X(b[0]),Y(b[1]));g.stroke();}
  g.setLineDash([]);for(const id in SB_WORLD)for(const d of (SB_REG[id]&&SB_REG[id].gates)||[]){const a=sbMapGate(id,d.id);if(!a)continue;g.beginPath();g.arc(X(a[0]),Y(a[1]),4.5*dpr,0,7);g.fillStyle='#140c08';g.fill();g.strokeStyle='#f3ead6';g.lineWidth=1.5*dpr;g.stroke();}
  /* names: plain, never a button */g.textAlign='center';g.textBaseline='middle';const F=px=>'800 '+Math.round(px*dpr)+'px system-ui,sans-serif';
  for(const id in SB_WORLD){const W=SB_WORLD[id],b=W.box;g.font=F(id==='backyard'?15:12);g.fillStyle=id==='backyard'?'rgba(255,255,255,.92)':'rgba(30,18,10,.9)';g.fillText(W.name,X((b[0]+b[1])/2),Y(id==='backyard'?b[3]-.55:b[2]+.45));}
  for(const m of SB_WORLD_MORE)if(m.name){g.font=F(10);g.fillStyle='rgba(30,18,10,.6)';g.fillText(m.name,X((m.box[0]+m.box[1])/2),Y((m.box[2]+m.box[3])/2));}
  g.font=F(11);g.fillStyle='rgba(255,255,255,.65)';g.fillText('FRONT STREET',X(-1.2),Y(-5.65));
  /* you: an arrow where you are, pointing the way you face */
  if(SBX&&player&&SB_WORLD[SB.regId]){const p=SB_WORLD[SB.regId].at(player.x,player.y),a=player.ma,r=9*dpr;g.save();g.translate(X(p[0]),Y(p[1]));g.rotate(a);g.beginPath();g.moveTo(r*1.25,0);g.lineTo(-r*.8,r*.8);g.lineTo(-r*.35,0);g.lineTo(-r*.8,-r*.8);g.closePath();g.fillStyle='#39d0ff';g.fill();g.strokeStyle='#06222e';g.lineWidth=2*dpr;g.stroke();g.restore();}
  /* the pins sit over the picture as real buttons (so a finger, a mouse and a controller all reach them) */
  for(const q of SBM.pins){q.b.style.left=(X(q.at[0])/dpr)+'px';q.b.style.top=(Y(q.at[1])/dpr)+'px';}}
function sbMapGate(id,gid){const R=SB_REG[id],W=SB_WORLD[id];if(!R||!W)return null;const d=(R.gates||[]).find(q=>q.id===gid);if(!d)return null;const b=W.box;if(R.room){const y=(b[2]+b[3])/2+d.p/100,x=(b[0]+b[1])/2+d.p/100;return d.w==='E'?[b[1],y]:d.w==='W'?[b[0],y]:d.w==='N'?[x,b[3]]:[x,b[2]];}return d.w==='S'?[d.p,b[2]]:d.w==='N'?[d.p,b[3]]:d.w==='E'?[b[1],d.p]:[b[0],d.p];}
function sbMapPins(){const box=sbMapEl().querySelector('#sbMapBox');for(const q of SBM.pins)q.b.remove();SBM.pins=[];
  for(const id in SB_WORLD){const t=sbMapTrack(id);if(!t||!SB_REG[id])continue;const b=document.createElement('button');b.type='button';b.className='sbpin';b.setAttribute('aria-label','Travel to '+t.name);
    b.style.cssText='position:absolute;width:34px;height:34px;margin:-17px 0 0 -17px;border-radius:50%;border:3px solid #ffd45a;padding:0;cursor:pointer;background:conic-gradient(#141210 25%,#fbf6ea 0 50%,#141210 0 75%,#fbf6ea 0) 0 0/14px 14px;box-shadow:0 2px 6px rgba(0,0,0,.6)';
    b.innerHTML='<span style="position:absolute;left:50%;top:100%;transform:translateX(-50%);margin-top:3px;font:800 11px/1 system-ui,sans-serif;color:#fff;white-space:nowrap;text-shadow:0 1px 3px #000,0 0 6px #000;pointer-events:none">'+t.name+'</span>';
    b.onclick=()=>sbMapPick({id,track:t.name});box.appendChild(b);SBM.pins.push({id,b,at:t.start});}
  if(!document.getElementById('sbPinCss')){const st=document.createElement('style');st.id='sbPinCss';st.textContent='.sbpin:focus-visible,.sbpin[aria-pressed=true]{outline:3px solid #39d0ff;outline-offset:3px}';document.head.appendChild(st);}}
/* open or close. from: 'drive' (straight from driving: closing goes back to driving) or 'pause' (from the pause menu: closing goes back to it) */
function sbMap(open,from){const e=sbMapEl();if(open===SBM.open)return;if(open){if(!SBX||SB.trav||(state!=='race'&&state!=='paused'))return;SBM.from=from||'drive';
    if(state==='race')togglePause();/* the game stops under the map, exactly as under the pause menu */pauseOv.hidden=true;SBM.open=true;e.hidden=false;sbMapPins();sbMapPick(null);
    e.querySelector('#sbMapKey').textContent=(typeof COARSE!=='undefined'&&COARSE)?'':'M or Select: close';const first=SBM.pins.find(q=>q.id===SB.regId)||SBM.pins[0];if(first)first.b.focus();}
  else{SBM.open=false;e.hidden=true;SBM.pick=null;if(SBM.from==='pause'){pauseOv.hidden=false;const r=document.getElementById('resumeBtn');if(r)r.focus();}else if(state==='paused')togglePause();}}
/* fast travel: to a region's start line. Only this player moves. */
function sbMapTravel(id){if(!SB_REG[id])return;SBM.from='drive';sbMap(false);if(state!=='race')return;sbTravel({to:id,start:true});}
/* the pause menu's Map button, directly under Resume, in Sandbox only */
function sbMapBtn(){let b=document.getElementById('sbMapBtn');if(!b){const r=document.getElementById('resumeBtn');if(!r)return;b=document.createElement('button');b.id='sbMapBtn';b.className='cta';b.type='button';b.textContent='Map';b.style.cssText='background:var(--oven-2);box-shadow:0 5px 0 rgba(0,0,0,.35);border:2px solid var(--oven-3)';r.insertAdjacentElement('afterend',b);b.onclick=()=>sbMap(true,'pause');}
  b.hidden=!SBX;}
