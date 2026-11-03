
(function(){
'use strict';
const stage=document.getElementById('stage');
function fail(msg){const l=document.getElementById('loader');if(l)l.remove();stage.insertAdjacentHTML('beforeend','<div class="fail">'+msg+'</div>');}
if(!window.THREE){fail('The 3D engine did not load. Check your connection and reopen the page.');return;}
if(THREE.ColorManagement)THREE.ColorManagement.legacyMode=false;
const COARSE=matchMedia('(pointer:coarse)').matches;
const LAPS=3,RW=63,CURB=73,WALLD=CURB+20,KS=1.76,BASE0=170.5,ACCEL=110,TURN=2.2,STEP=1/120;
const RM=matchMedia('(prefers-reduced-motion: reduce)').matches;let BASE_MAX=BASE0;

const RACERS=[
  {name:'Pep',color:'#d63a26',stripe:'#fff4dc',top:'#8e1f10',iris:'#5a3a1e'},
  {name:'Basil',color:'#2f9a3e',stripe:'#f7c948',top:'#2d6b27',iris:'#2d5a1e'},
  {name:'Olive',color:'#6a4fb0',stripe:'#d8d0f0',top:'#1e1a24',iris:'#3a2a5a'},
  {name:'Mozz',color:'#f3ebd8',stripe:'#e0452c',top:'#fffaf0',iris:'#4a6a9a'},
  {name:'Chili',color:'#f07214',stripe:'#1b0f0b',top:'#c4170c',iris:'#6a2a10'},
  {name:'Shroom',color:'#8a5f42',stripe:'#e3d2b0',top:'#e3d2b0',iris:'#4a3020'},
  {name:'Pineapple',color:'#f2bf1e',stripe:'#2f9a3e',top:'#fff07a',iris:'#3a5a1e'},
  {name:'Anchovy',color:'#2a7fd8',stripe:'#fff4dc',top:'#a9bccb',iris:'#1e3a6a'}
];
const CUPS=[{name:'Margherita Cup',col:'#f7c948'},{name:'Supreme Cup',col:'#3f9a35'},{name:'Deep Dish Cup',col:'#e0452c'},{name:"Meat Lover's Cup",col:'#b06a3c'}];
const MAPS=[
  {id:'margherita',name:'Margherita Ring',theme:'kitchen',R:1700,ctrl:[[200,820],[160,600],[220,380],[180,210],[340,120],[520,170],[560,330],[700,300],[850,190],[915,360],[820,520],[880,700],[760,875],[560,860],[440,720],[320,880]].map(([x,y])=>[(x-512)/512,(y-512)/512])},
  {id:'bay',name:'Hawaiian Bay',theme:'bay',R:1850,ctrl:[[-.75,.55],[-.86,.05],[-.62,-.45],[-.2,-.72],[.25,-.8],[.66,-.56],[.82,-.15],[.56,.1],[.25,0],[.04,.26],[.3,.46],[.72,.5],[.62,.83],[.1,.86],[-.36,.78]]},
  {id:'peaks',name:'Pepperoni Peaks',theme:'night',R:1750,ctrl:[[-.8,-.1],[-.66,-.6],[-.2,-.86],[.16,-.56],[-.04,-.26],[.36,-.14],[.76,-.46],[.9,.05],[.6,.42],[.2,.3],[0,.62],[-.3,.86],[-.62,.56],[-.36,.24]]},
  {id:'frosty',name:'Frosty Freezer',theme:'freezer',R:1750,gen:11},
  {id:'basil',name:'Basil Boulevard',theme:'kitchen',R:1800,gen:21},{id:'lagoon',name:'Pineapple Lagoon',theme:'bay',R:1850,gen:22},
  {id:'mozz',name:'Midnight Mozzarella',theme:'night',R:1800,gen:23},{id:'burn',name:'Freezer Burn Pass',theme:'freezer',R:1800,gen:24},
  {id:'oven',name:'Oven Rush Raceway',theme:'kitchen',R:1900,gen:31},{id:'calzone',name:'Calzone Coast',theme:'bay',R:1900,gen:32},
  {id:'napoli',name:'Neon Napoli',theme:'night',R:1850,gen:33},{id:'glacier',name:'Glacier Crust',theme:'freezer',R:1900,gen:34},
  {id:'spiral',name:'Sauce Spiral',theme:'kitchen',R:1900,gen:41},{id:'tour',name:'Topping Tour',theme:'bay',R:1950,gen:42},
  {id:'moon',name:'Pepper Moon Circuit',theme:'night',R:1900,gen:43},{id:'peak',name:'Frozen Pie Peak',theme:'freezer',R:1950,gen:44}
];
MAPS.forEach((m,i)=>{m.cup=Math.floor(i/4);if(!m.boxes)m.boxes=[.14,.39,.62,.85];});
const CUP_TRACKS=CUPS.map((_,c)=>MAPS.map((m,i)=>m.cup===c?i:-1).filter(i=>i>=0));
const DIFFS={
  easy:{skill:[.82,.88],ahead:.9,behind:1.04,delay:[1.4,4],corner:.34,boost:.1},
  normal:{skill:[.88,.95],ahead:.94,behind:1.06,delay:[.8,3],corner:.3,boost:.3},
  hard:{skill:[.94,1.0],ahead:.97,behind:1.1,delay:[.4,1.8],corner:.24,boost:.6}
};
const CLASSES={small:{mul:.86,ai:'easy',label:'50cc',note:'50cc: a relaxed speed for learning the tracks.'},
  medium:{mul:1,ai:'normal',label:'100cc',note:'100cc: the standard race speed.'},
  large:{mul:1.14,ai:'hard',label:'200cc',note:'200cc: much faster karts and sharper rivals.'},
  reverse:{mul:1.14,ai:'hard',label:'Reverse',rev:true,note:'Every track runs backwards at 200cc speed.'}};
const PTS=[15,12,10,8,6,4,2,1];
const SVG={
  chili:'<svg viewBox="0 0 24 24"><path d="M15.5 3.5c1.2 1 1.3 2.3.3 3.5" stroke="#4f9a44" stroke-width="2.2" fill="none" stroke-linecap="round"/><path d="M15.5 7c3.6 2 2.6 8.6-1.8 11.6S4.4 21.8 3 20.6c4.4-1.2 7.4-4.4 8.4-8.8.4-3.4 2.2-6 4.1-4.8z" fill="#e0331c"/><path d="M14 9.5c.8 1.5-.2 4-1.6 5.6" stroke="#ff8a6a" stroke-width="1.2" fill="none" stroke-linecap="round"/></svg>',
  pepperoni:'<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9.5" fill="#b8311c"/><circle cx="12" cy="12" r="9.5" fill="none" stroke="#8e1f10" stroke-width="1.5"/><circle cx="8.5" cy="9" r="1.6" fill="#7d1d0e"/><circle cx="15" cy="10.5" r="1.3" fill="#7d1d0e"/><circle cx="11" cy="15.5" r="1.5" fill="#7d1d0e"/></svg>',
  oil:'<svg viewBox="0 0 24 24"><path d="M12 2.5c3.2 5 6.5 8.2 6.5 12.3a6.5 6.5 0 0 1-13 0C5.5 10.7 8.8 7.5 12 2.5z" fill="#e2b22d"/><path d="M9 14.5c0 2 1.2 3.4 3 3.8" stroke="#fff2b0" stroke-width="1.6" fill="none" stroke-linecap="round"/></svg>',
  dough:'<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9" fill="#f3dfb4" stroke="#c98b4e" stroke-width="1.6"/><path d="M8 10c1.5-1 3-1 4.5 0M11 15c1.5-1 3-1 4.5 0" stroke="#d9b98a" stroke-width="1.3" fill="none" stroke-linecap="round"/></svg>'
};
Object.assign(SVG,{
  trio:'<svg viewBox="0 0 24 24"><circle cx="7" cy="15.5" r="5" fill="#b8311c"/><circle cx="17" cy="15.5" r="5" fill="#b8311c"/><circle cx="12" cy="7" r="5" fill="#c93a22"/><circle cx="6" cy="14.5" r="1.2" fill="#7d1d0e"/><circle cx="16" cy="16.5" r="1.2" fill="#7d1d0e"/><circle cx="12.5" cy="6" r="1.2" fill="#7d1d0e"/></svg>',
  garlic:'<svg viewBox="0 0 24 24"><circle cx="12" cy="13" r="10.5" fill="none" stroke="#7fe07a" stroke-width="1.3" stroke-dasharray="2 2.4"/><path d="M12 4c0 3-1 4-3 5-3 1.5-4.5 3.5-4.5 6.5a5.5 5.5 0 0 0 5.5 5.5h4a5.5 5.5 0 0 0 5.5-5.5c0-3-1.5-5-4.5-6.5-2-1-3-2-3-5z" fill="#f4ecdc" stroke="#cfc3a8" stroke-width="1.2"/><path d="M12 9v12M9 11c-1 3-1 6 .4 9.5M15 11c1 3 1 6-.4 9.5" stroke="#d9cdb2" stroke-width="1.1" fill="none"/></svg>',
  flour:'<svg viewBox="0 0 24 24"><path d="M7 7h10l2 4-1 10H6L5 11z" fill="#f6f1e6" stroke="#cfc3a8" stroke-width="1.2"/><path d="M8 7l1-3h6l1 3" fill="#e9dfc8" stroke="#cfc3a8" stroke-width="1.2"/><circle cx="12" cy="15" r="3" fill="#e0452c"/><path d="M17 4l2-2.5M19 5.5l2.5-1" stroke="#ff9a1f" stroke-width="1.5" stroke-linecap="round"/></svg>',
  wheel:'<svg viewBox="0 0 24 24"><circle cx="10" cy="10" r="7.5" fill="#dfe3e6" stroke="#8c8f93" stroke-width="1.5"/><circle cx="10" cy="10" r="2" fill="#8c8f93"/><path d="M14.5 14.5l6.5 6.5" stroke="#e0452c" stroke-width="3.4" stroke-linecap="round"/><path d="M2 3l2 1.5M3 1l1 2" stroke="#ff3b1a" stroke-width="1.3" stroke-linecap="round"/></svg>',
  rush:'<svg viewBox="0 0 24 24"><path d="M1.5 15l5.5-2.5 3 1-4 3.5z" fill="#ff9a1f"/><path d="M1 11.5h4.5M2.5 19h3" stroke="#ffd36b" stroke-width="1.6" stroke-linecap="round"/><rect x="8" y="8" width="14" height="9" rx="1.6" fill="#f5ead2" stroke="#d6402a" stroke-width="1.4"/><path d="M15 9.6l-3 6h6z" fill="#d6402a"/></svg>',
  freezer:'<svg viewBox="0 0 24 24"><g stroke="#8fd8ff" stroke-width="2" stroke-linecap="round"><path d="M12 2v20M3.3 7l17.4 10M3.3 17l17.4-10"/><path d="M9.5 3.5L12 6l2.5-2.5M9.5 20.5L12 18l2.5 2.5"/></g><circle cx="12" cy="12" r="2.6" fill="#dff4ff"/></svg>'});
const ITEM_KEYS=['chili','pepperoni','oil','dough','trio','garlic','flour','wheel','rush','freezer'];
const HELP={chili:['Chili Boost','A burst of speed that works even on the cheese.'],pepperoni:['Pepperoni','Fires straight ahead and bounces off the crust walls.'],oil:['Olive Oil','Drops a slick on the road behind you. Karts that drive through it spin out.'],dough:['Dough Ball','Rolls forward and chases down the racer ahead of you.'],trio:['Pepperoni Trio','Fires three pepperoni ahead at once in a spread.'],garlic:['Garlic Shield','A garlic bubble that stays on until something hits you. It blocks one item or special ability.'],flour:['Flour Bomb','Lobbed ahead, it bursts into a cloud that spins out everyone nearby.'],wheel:['Pizza Wheel','A rolling cutter that chases down whoever is in first. Only shows up for racers near the back.'],rush:['Delivery Rush','Autopilot at full speed for a few seconds, plowing through anyone in the way.'],freezer:['Freezer Blast','Slows down every racer ahead of you for a few seconds.']};
for(const k of ITEM_KEYS){document.getElementById('h-'+k).innerHTML=SVG[k]+'<span><b>'+HELP[k][0]+'.</b> '+HELP[k][1]+'</span>';}

let seed=20261101;const rnd=()=>{seed=(seed*16807)%2147483647;return (seed-1)/2147483646;};
const clamp=(v,a,b)=>v<a?a:v>b?b:v;
const angDiff=(a,b)=>Math.atan2(Math.sin(a-b),Math.cos(a-b));
const lerpA=(a,b,t)=>a+angDiff(b,a)*t;
function cnv(w,h){const c=document.createElement('canvas');c.width=w;c.height=h;return c;}
function shade(hex,amt){const n=parseInt(hex.slice(1),16);let r=n>>16,g=(n>>8)&255,b=n&255;const tg=amt<0?0:255,a=Math.abs(amt);r=Math.round(r+(tg-r)*a);g=Math.round(g+(tg-g)*a);b=Math.round(b+(tg-b)*a);return '#'+((1<<24)|(r<<16)|(g<<8)|b).toString(16).slice(1);}
const store={get(k){try{return localStorage.getItem(k);}catch(e){return null;}},set(k,v){try{localStorage.setItem(k,v);}catch(e){}}};
const CFG_DEF={shadows:true,detail:'normal',fps:'60',showfps:false,vol:80,units:'mph',shake:true,mini:true,ghost:true,cam:'close',music:true,mvol:45};
const CFG=Object.assign({},CFG_DEF,(()=>{try{return JSON.parse(store.get('crust-cfg')||'{}')||{};}catch(e){return {};}})());
if(!CFG.v33){CFG.v33=1;CFG.fps='60';}/* everyone moves to the steady 60 fps default once */
const saveCfg=()=>store.set('crust-cfg',JSON.stringify(CFG));

/* ================= TRACK ================= */
function cr(p0,p1,p2,p3,t){const t2=t*t,t3=t2*t;return .5*(2*p1+(-p0+p2)*t+(2*p0-5*p1+4*p2-p3)*t2+(-p0+3*p1-3*p2+p3)*t3);}
function resampleClosed(arr,n){const D=arr.length,cum=[0];for(let i=1;i<=D;i++){const a=arr[i-1],b=arr[i%D];cum[i]=cum[i-1]+Math.hypot(b.x-a.x,b.y-a.y);}
  const L=cum[D],out=[];let seg=0;for(let j=0;j<n;j++){const d=j*L/n;while(cum[seg+1]<d)seg++;const t=(d-cum[seg])/((cum[seg+1]-cum[seg])||1);const a=arr[seg],b=arr[(seg+1)%D];out.push({x:a.x+(b.x-a.x)*t,y:a.y+(b.y-a.y)*t});}return {pts:out,L};}
function smoothClosed(arr,it){const n=arr.length;for(let k=0;k<it;k++){const c=arr.map(p=>({x:p.x,y:p.y}));for(let i=0;i<n;i++){const a=c[(i-1+n)%n],b=c[(i+1)%n];arr[i].x=c[i].x*.5+(a.x+b.x)*.25;arr[i].y=c[i].y*.5+(a.y+b.y)*.25;}}}
function crDense(P,per){const C=P.length,out=[];for(let i=0;i<C;i++){const p0=P[(i-1+C)%C],p1=P[i],p2=P[(i+1)%C],p3=P[(i+2)%C];for(let s=0;s<per;s++){const t=s/per;out.push({x:cr(p0.x,p1.x,p2.x,p3.x,t),y:cr(p0.y,p1.y,p2.y,p3.y,t)});}}return out;}
function genCtrl(sd){let s=(sd*7919+13)%2147483647||7;const r=()=>{s=(s*16807)%2147483647;return (s-1)/2147483646;};const n=9+Math.floor(r()*5),pts=[],rot=r()*6.283;
  for(let i=0;i<n;i++){const a=rot+(i+(r()-.5)*.55)/n*Math.PI*2;let rad=.45+r()*.52;if(r()<.28)rad*=.58;pts.push([Math.cos(a)*rad,Math.sin(a)*rad]);}return pts;}
function trackOK(tk){const P=tk.pts,N2=tk.N;for(let j=0;j<N2;j++)if(Math.abs(P[j].bend)>1.25)return false;
  for(let a=0;a<N2;a+=2)for(let b=a+40;b<N2;b+=2){if(N2-(b-a)<40)continue;const dx=P[a].x-P[b].x,dy=P[a].y-P[b].y;if(dx*dx+dy*dy<215*215)return false;}return true;}
function makeTrack(def,rev){if(!def.ctrl){let ok=false;for(let t=0;t<60&&!ok;t++){def.ctrl=genCtrl(def.gen+t*101);ok=trackOK(buildTrack(def,false));}}return buildTrack(def,rev);}
function buildTrack(def,rev){
  const ctrl=def.ctrl.map(([x,y])=>({x,y}));
  const coarse=resampleClosed(crDense(ctrl,32),90).pts;smoothClosed(coarse,8);
  let mr=0;for(const p of coarse)mr=Math.max(mr,Math.hypot(p.x,p.y));const sc=(def.R-170)/mr;for(const p of coarse){p.x*=sc;p.y*=sc;}
  const dense=crDense(coarse,12);let L0=0;for(let i=0;i<dense.length;i++){const a=dense[i],b=dense[(i+1)%dense.length];L0+=Math.hypot(b.x-a.x,b.y-a.y);}
  const N=Math.round(L0/8),rs=resampleClosed(dense,N),pts=rs.pts,L=rs.L;
  if(rev){const r0=pts[0],rest=pts.slice(1).reverse();pts.length=0;pts.push(r0,...rest);}
  for(let j=0;j<N;j++){const n=pts[(j+1)%N],p=pts[(j-1+N)%N];let tx=n.x-p.x,ty=n.y-p.y;const l=Math.hypot(tx,ty);tx/=l;ty/=l;Object.assign(pts[j],{tx,ty,nx:-ty,ny:tx,ang:Math.atan2(ty,tx)});}
  for(let j=0;j<N;j++){pts[j].bend=angDiff(pts[(j+10)%N].ang,pts[(j-10+N)%N].ang);}
  return {pts,N,L,R:def.R};
}
let T=null,track=[],N=0,grid=null,RIM=1000;
let HILLS=[],FLATS=[],HR=1000,HMIN=-30,LOOP=null,LOOPS=[],PITS=[],GLIDE=null;const LOOPR=46,UPV=new THREE.Vector3(0,1,0);
function pitAt(x,y){let d=0;for(const q of PITS){const dx=x-q.x,dy=y-q.y,u=dx*q.ux+dy*q.uy;if(u<=0||u>=q.L)continue;const v=Math.abs(dy*q.ux-dx*q.uy);if(v>=q.W+70)continue;
  let a=Math.min(u,q.L-u)/8;a=a>=1?1:a*a*(3-2*a);let l=Math.min(1,(q.W+70-v)/70);l=l*l*(3-2*l);d+=q.D*a*l;}return d;}
function groundAt(x,y){let h=0,r=0;for(const b of HILLS){const dx=x-b.x,dy=y-b.y;h+=b.a*Math.exp(-(dx*dx+dy*dy)*b.k);}
  if(h!==0){if(h>0)h=90*Math.tanh(h/90);let f=clamp((HR-90-Math.hypot(x,y))/260,0,1);f=f*f*(3-2*f);for(const q of FLATS){f*=1-Math.exp(-((x-q.x)**2+(y-q.y)**2)*q.k);}r=Math.max(HMIN,h*f);}
  return PITS.length?r-pitAt(x,y):r;}
function glideY(x,y){const G=GLIDE;if(!G||!G.long||!G.p)return G?G.y:0;const u=clamp(((x-G.p.x)*G.ux+(y-G.p.y)*G.uy)/G.L,0,1);return G.y0+(G.y1-G.y0)*u;}
const overPit=(x,y)=>GLIDE&&groundAt(x,y)<glideY(x,y)-20;
const loopNear=(j,g)=>LOOPS.some(L=>{const d=Math.abs(j-L.j)%N;return Math.min(d,N-d)<g+(L.full?40:0);});
const INLOOP=['margherita','peaks','lagoon','burn','spiral','moon','calzone'];
const LONGGLIDE=['bay','peaks','lagoon','calzone','tour','peak','glacier','frosty'];
function makeHills(def){HILLS=[];FLATS=[];PITS=[];GLIDE=null;HR=def.R;HMIN=def.theme==='bay'?-8:-30;
  for(let i=0;i<9;i++){const p=track[Math.floor((i+.3+rnd()*.4)*N/9)%N],off=(rnd()-.5)*240,s=150+rnd()*130,neg=def.theme!=='bay'&&rnd()<.3;
    HILLS.push({x:p.x+p.nx*off,y:p.y+p.ny*off,a:neg?-(18+rnd()*16):(30+rnd()*50),k:1/(2*s*s)});}
  for(let i=0;i<4;i++){const a=rnd()*6.283,r=Math.sqrt(rnd())*(def.R-450),s=200+rnd()*150;HILLS.push({x:Math.cos(a)*r,y:Math.sin(a)*r,a:35+rnd()*55,k:1/(2*s*s)});}
  for(const p of track){p.flo=p.fhi=undefined;}const s0=track[0];FLATS.push({x:s0.x,y:s0.y,k:1/(2*120*120)});
  LOOP=null;for(const lim of [.1,.18,.3]){let best=null,bs=1e9;for(let j=Math.floor(N*.25);j<Math.floor(N*.85);j++){let ok=true;for(let o=-26;o<=26;o+=2)if(Math.abs(track[(j+o)%N].bend)>lim){ok=false;break;}
      if(!ok)continue;const d=Math.abs(j-N*.55);if(d<bs){bs=d;best=j;}}
    if(best!=null){LOOP={j:best,lat0:-18,shift:36,p:track[best],g0:0,W:15};FLATS.push({x:track[best].x,y:track[best].y,k:1/(2*160*160)});break;}}
  LOOPS=LOOP?[LOOP]:[];
  /* built-in loop: the whole road funnels into a wide loop, with a boost pad and a row of item boxes on the way in */
  if(INLOOP.includes(def.id)){const cdl=(a,b)=>{const d=Math.abs(a-b)%N;return Math.min(d,N-d);};const bx=def.boxes.map(f=>Math.floor(f*N));
    for(const lim of [.12,.18,.26]){let best=null,bs=1e9;for(let j=70;j<N-30;j++){if(cdl(j,0)<110)continue;if(LOOP&&cdl(j,LOOP.j)<N*.22)continue;if(bx.some(b=>cdl(b,j)<70))continue;
        let ok=true;for(let o=-62;o<=24;o+=2)if(Math.abs(track[(j+o+N)%N].bend)>lim){ok=false;break;}if(!ok)continue;const d=Math.min(cdl(j,Math.floor(N*.2)),cdl(j,Math.floor(N*.8)));if(d<bs){bs=d;best=j;}}
      if(best!=null){const L={j:best,lat0:-24,shift:48,p:track[best],g0:0,W:22,full:true};LOOPS.push(L);FLATS.push({x:track[best].x,y:track[best].y,k:1/(2*190*190)});
        const fl=(best-34+N)%N,q=track[fl];FLATS.push({x:q.x,y:q.y,k:1/(2*120*120)});
        for(let o=-56;o<=0;o++){const t=Math.min(1,(o+56)/46),p=track[(best+o+N)%N];p.flo=-(WALLD-3.5)+((L.lat0-L.W+4)+(WALLD-3.5))*t;p.fhi=(WALLD-3.5)+((L.lat0+L.W-4)-(WALLD-3.5))*t;}
        break;}}}
  {const bx=def.boxes.map(f=>Math.floor(f*N)),cd=(a,b)=>{const d=Math.abs(a-b)%N;return Math.min(d,N-d);};
    /* long glides on some maps: a high launch cliff, a deep canyon and a landing far below, 5-8 seconds in the air */
    const tries=LONGGLIDE.includes(def.id)?[[1050,1],[850,1],[300,0]]:[[300,0]];
    for(const [len,long] of tries){if(GLIDE)break;const GL=Math.round(len/(T.L/N));
    for(const lim of long?[.12,.18,.26]:[.1,.16,.24,.34,.5]){let best=null,bs=1e9;
      for(let j=Math.max(60,Math.floor(N*.1));j+GL<N-45;j++){if(loopNear(j+(GL>>1),(GL>>1)+75))continue;if(bx.some(b=>b-j>-30&&b-j<GL+24))continue;
        let ok=true;for(let o=-18;o<=GL+12;o+=2)if(Math.abs(track[(j+o)%N].bend)>lim){ok=false;break;}if(!ok)continue;
        if(long){const a=track[j],b=track[j+GL],Lc=Math.hypot(b.x-a.x,b.y-a.y),ux=(b.x-a.x)/Lc,uy=(b.y-a.y)/Lc;for(let o=0;o<=GL;o+=3){const q=track[j+o];if(Math.abs((q.y-a.y)*ux-(q.x-a.x)*uy)>45){ok=false;break;}}if(!ok)continue;
          if(Math.hypot(a.x,a.y)>def.R-260||Math.hypot(b.x,b.y)>def.R-260)continue;}
        const d=Math.min(Math.abs(j-N*.36),Math.abs(j-N*.78));if(d<bs){bs=d;best=j;}}
      if(best!=null){GLIDE={j0:best,j1:best+GL,rj:best-4,long};break;}}}
    if(GLIDE){const GL=GLIDE.j1-GLIDE.j0,a=track[GLIDE.j0],b=track[GLIDE.j1],mid=track[GLIDE.j0+(GL>>1)];
      const L=Math.hypot(b.x-a.x,b.y-a.y),ux=(b.x-a.x)/L,uy=(b.y-a.y)/L;
      if(GLIDE.long){HILLS.push({x:a.x-ux*90,y:a.y-uy*90,a:95,k:1/(2*190*190)});HILLS.push({x:b.x+ux*60,y:b.y+uy*60,a:-26,k:1/(2*170*170)});}
      else FLATS.push({x:mid.x,y:mid.y,k:1/(2*240*240)});
      Object.assign(GLIDE,{p:a,L,ux,uy,W:CURB+25,D:GLIDE.long?110:50});GLIDE.y0=groundAt(a.x,a.y);GLIDE.y1=groundAt(b.x,b.y);GLIDE.y=GLIDE.long?GLIDE.y0:Math.max(GLIDE.y0,GLIDE.y1);
      PITS.push({x:a.x,y:a.y,ux,uy,L,W:GLIDE.W,D:GLIDE.D});GLIDE.y0=groundAt(a.x-ux*2,a.y-uy*2);GLIDE.y1=groundAt(b.x+ux*2,b.y+uy*2);if(GLIDE.long)GLIDE.y=GLIDE.y0;}}
  planPonds(def);
  for(const L of LOOPS)L.g0=groundAt(L.p.x,L.p.y);}
function terrainMesh(R,mat){const RS=96,AS=340,pos=[],uv=[],idx=[],dr=(R-10)/RS;
  for(let i=0;i<=RS;i++){const r=(R-10)*i/RS,da=Math.PI*2/AS;for(let a=0;a<=AS;a++){const an=a*da,x=Math.cos(an)*r,z=Math.sin(an)*r;
    let h=groundAt(x,z);if(r>0){const tx=-Math.sin(an),tz=Math.cos(an),ht=r*da*.5,hr=dr*.5;for(const [ox,oz] of [[tx*ht,tz*ht],[-tx*ht,-tz*ht],[Math.cos(an)*hr,Math.sin(an)*hr],[-Math.cos(an)*hr,-Math.sin(an)*hr]])h=Math.min(h,groundAt(x+ox,z+oz));}
    if(grid&&nearTrack(x,z,CURB+14))h-=.35;pos.push(x,h-.08,z);uv.push(x/110,z/110);}}
  for(let i=0;i<RS;i++)for(let a=0;a<AS;a++){const p0=i*(AS+1)+a,p1=p0+1,p2=p0+AS+1,p3=p2+1;idx.push(p0,p1,p2,p1,p3,p2);}
  const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(pos,3));g.setAttribute('uv',new THREE.Float32BufferAttribute(uv,2));g.setIndex(idx);g.computeVertexNormals();
  const m=new THREE.Mesh(g,mat);m.receiveShadow=true;m.userData.noLift=true;return m;}
function buildGrid(){const cell=64,g=new Map();for(const p of track){const k=Math.floor(p.x/cell)+','+Math.floor(p.y/cell);if(!g.has(k))g.set(k,[]);g.get(k).push(p);}grid={cell,g};}
function nearTrack(x,y,th){const c=grid.cell,r=Math.ceil(th/c),cx=Math.floor(x/c),cy=Math.floor(y/c),th2=th*th;
  for(let dx=-r;dx<=r;dx++)for(let dy=-r;dy<=r;dy++){const a=grid.g.get((cx+dx)+','+(cy+dy));if(a)for(const p of a)if((p.x-x)**2+(p.y-y)**2<th2)return true;}return false;}
function minTrackDist(x,y){let m=1e18;for(let j=0;j<N;j+=2){const p=track[j],d=(p.x-x)**2+(p.y-y)**2;if(d<m)m=d;}return Math.sqrt(m);}
function pathTrack(c,pts,sc,ox,oy){c.beginPath();pts.forEach((p,i)=>i?c.lineTo(ox+p.x*sc,oy+p.y*sc):c.moveTo(ox+p.x*sc,oy+p.y*sc));c.closePath();}

/* ================= RENDERER ================= */
const cvs=document.getElementById('game');
let renderer;
try{renderer=new THREE.WebGLRenderer({canvas:cvs,antialias:true,powerPreference:'high-performance',stencil:false});renderer.shadowMap.enabled=CFG.shadows!==false;}
catch(e){fail('This device could not start 3D graphics (WebGL).');return;}
const QUAL={fast:{cap:1.25,start:1,floor:.85,sm:1024,soft:false,detail:1100,note:'Lower resolution and no glow pass, for the smoothest frame rate on older phones.'},
  balanced:{cap:1.75,start:1.5,floor:1.0,sm:2048,soft:true,detail:1500,note:'Crisp detail with glow and colour grading at a steady 60 fps. Best for most phones.'},
  sharp:{cap:2.25,start:2,floor:1.5,sm:4096,soft:true,detail:2100,note:'Highest resolution and the longest scenery distance. Best on newer phones and computers.'}};
let qKey=store.get('crust-q')||(COARSE?'balanced':'sharp');if(!QUAL[qKey])qKey='balanced';
const DPR=window.devicePixelRatio||1;let pr=Math.min(DPR,QUAL[qKey].start),capPR=Math.min(DPR,QUAL[qKey].cap);
renderer.setPixelRatio(pr);
renderer.outputEncoding=THREE.sRGBEncoding;renderer.toneMapping=THREE.ACESFilmicToneMapping;
renderer.shadowMap.enabled=true;renderer.shadowMap.type=QUAL[qKey].soft?THREE.PCFSoftShadowMap:THREE.PCFShadowMap;
const maxAniso=Math.min(16,renderer.capabilities.getMaxAnisotropy());
const scene=new THREE.Scene();
const camera=new THREE.PerspectiveCamera(60,16/9,1.6,22000);
const hemi=new THREE.HemisphereLight('#ffffff','#444444',.7);scene.add(hemi);
const rimL=new THREE.DirectionalLight('#9fc4ff',.0);scene.add(rimL);scene.add(rimL.target);
const sun=new THREE.DirectionalLight('#ffffff',2);sun.castShadow=true;
sun.shadow.mapSize.set(QUAL[qKey].sm,QUAL[qKey].sm);
Object.assign(sun.shadow.camera,{left:-115,right:115,top:115,bottom:-115,near:20,far:1400});sun.shadow.normalBias=.6;
sun.shadow.bias=-.0004;sun.shadow.normalBias=.35;scene.add(sun,sun.target);
const sunDir=new THREE.Vector3(.6,1,.35).normalize();
const pmrem=new THREE.PMREMGenerator(renderer);

function T2(c,rx,ry,linear){const t=new THREE.CanvasTexture(c);t.anisotropy=maxAniso;if(!linear)t.encoding=THREE.sRGBEncoding;if(rx){t.wrapS=t.wrapT=THREE.RepeatWrapping;t.repeat.set(rx,ry);}return t;}
function wrap9(w,h,fn){for(const ox of [-w,0,w])for(const oy of [-h,0,h])fn(ox,oy);}

/* ---------- texture painters ---------- */
function cheeseTile(){const S=1024,c=cnv(S,S),g=c.getContext('2d');g.fillStyle='#f3c046';g.fillRect(0,0,S,S);
  for(let i=0;i<60;i++){const x=rnd()*S,y=rnd()*S,r=60+rnd()*120,col=rnd()<.55?'251,216,116':'226,160,52';wrap9(S,S,(ox,oy)=>{const gr=g.createRadialGradient(x+ox,y+oy,0,x+ox,y+oy,r);gr.addColorStop(0,'rgba('+col+',.55)');gr.addColorStop(1,'rgba('+col+',0)');g.fillStyle=gr;g.fillRect(x+ox-r,y+oy-r,r*2,r*2);});}
  for(let i=0;i<150;i++){const x=rnd()*S,y=rnd()*S,r=5+rnd()*16;wrap9(S,S,(ox,oy)=>{const gr=g.createRadialGradient(x+ox,y+oy,0,x+ox,y+oy,r);gr.addColorStop(0,'rgba(190,105,30,.75)');gr.addColorStop(1,'rgba(190,105,30,0)');g.fillStyle=gr;g.fillRect(x+ox-r,y+oy-r,r*2,r*2);});}
  for(let i=0;i<520;i++){const x=rnd()*S,y=rnd()*S,rx=3+rnd()*11,ry=2+rnd()*7,a=rnd()*3;wrap9(S,S,(ox,oy)=>{g.fillStyle='rgba(255,236,160,.85)';g.beginPath();g.ellipse(x+ox,y+oy,rx,ry,a,0,7);g.fill();g.strokeStyle='rgba(200,140,40,.35)';g.lineWidth=1.2;g.stroke();});}
  for(let i=0;i<2200;i++){g.fillStyle=rnd()<.5?'#4e6b26':'#6b4a1e';g.fillRect(rnd()*S,rnd()*S,1.5+rnd()*2,1+rnd());}
  return c;}
function sauceTile(dark){const W=512,H=1024,c=cnv(W,H),g=c.getContext('2d');
  const gr=g.createLinearGradient(0,0,W,0);const e=dark?'#5e140a':'#8f2112',m=dark?'#8a1e10':'#b8321d',cc=dark?'#982414':'#c53b22';
  gr.addColorStop(0,e);gr.addColorStop(.12,m);gr.addColorStop(.5,cc);gr.addColorStop(.88,m);gr.addColorStop(1,e);g.fillStyle=gr;g.fillRect(0,0,W,H);
  for(let i=0;i<900;i++){const x=rnd()*W,y=rnd()*H,r=2+rnd()*9,a=rnd()*3;const col=rnd()<.5?'rgba(110,18,8,.35)':'rgba(235,95,60,.28)';for(const oy of [-H,0,H]){g.fillStyle=col;g.beginPath();g.ellipse(x,y+oy,r,r*.6,a,0,7);g.fill();}}
  for(let i=0;i<70;i++){const x=30+rnd()*(W-60),y=rnd()*H,w=6+rnd()*10,h=5+rnd()*8,a=rnd()*3;for(const oy of [-H,0,H]){g.fillStyle='#d9472a';g.beginPath();g.ellipse(x,y+oy,w,h,a,0,7);g.fill();g.fillStyle='rgba(255,180,150,.55)';g.beginPath();g.ellipse(x-w*.3,y+oy-h*.3,w*.3,h*.25,0,0,7);g.fill();}}
  for(let i=0;i<500;i++){g.fillStyle=rnd()<.6?'#2f4a18':'#57702a';g.fillRect(rnd()*W,rnd()*H,2+rnd()*3,1.2+rnd()*1.5);}
  g.fillStyle='rgba(255,232,196,.42)';for(let y=0;y<H;y+=256){g.fillRect(W/2-4,y+40,8,120);}
  g.fillStyle='rgba(255,240,220,.85)';g.fillRect(14,0,5,H);g.fillRect(W-19,0,5,H);
  return c;}
/* ================= ROAD SURFACES: detailed procedural paving, several per track ================= */
const ROAD_SURF={
  sauce:{name:'Tomato asphalt',rough:.66,ns:.6,grain:.06},
  asphalt:{name:'Race asphalt',rough:.82,ns:.5,grain:.06},
  cobble:{name:'Cobblestone',rough:.6,ns:1.25,grain:.06},
  planks:{name:'Boardwalk',rough:.72,ns:1.2,grain:.07},
  ice:{name:'Packed ice',rough:.18,ns:.9,grain:.05,phys:1},
  brick:{name:'Brick pavers',rough:.74,ns:1.35,grain:.06},
  marble:{name:'Marble',rough:.22,ns:.7,grain:.04,phys:1}};
const ROAD_THEME={kitchen:['sauce','marble','planks'],bay:['asphalt','planks','brick'],night:['asphalt','cobble','sauce'],freezer:['ice','asphalt','cobble']};
function prng(seed){let a=seed>>>0;return ()=>{a=(a+0x6D2B79F5)>>>0;let t=a;t=Math.imul(t^(t>>>15),t|1);t^=t+Math.imul(t^(t>>>7),t|61);return ((t^(t>>>14))>>>0)/4294967296;};}
function hashStr(s){let h=2166136261;for(let i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,16777619);}return h>>>0;}
/* height canvas -> tangent-space normal map */
function heightToNormal(hc,str){const W=hc.width,H=hc.height,src=hc.getContext('2d').getImageData(0,0,W,H).data,out=cnv(W,H),og=out.getContext('2d'),id=og.createImageData(W,H),d=id.data;
  const h=(x,y)=>src[(((y+H)%H)*W+((x+W)%W))*4]/255;
  for(let y=0;y<H;y++)for(let x=0;x<W;x++){const dx=(h(x+1,y)-h(x-1,y))*str,dy=(h(x,y+1)-h(x,y-1))*str,l=Math.hypot(dx,dy,1),i=(y*W+x)*4;
    d[i]=(-dx/l*.5+.5)*255;d[i+1]=(dy/l*.5+.5)*255;d[i+2]=(1/l*.5+.5)*255;d[i+3]=255;}
  og.putImageData(id,0,0);return out;}
let _grainT=null;
function grainTex(){if(_grainT)return _grainT;const S=256,c=cnv(S,S),g=c.getContext('2d'),id=g.createImageData(S,S),r=prng(77);
  const v=new Float32Array(S*S);for(let i=0;i<S*S;i++)v[i]=r();
  for(let y=0;y<S;y++)for(let x=0;x<S;x++){let a=0;for(const [ox,oy,w] of [[0,0,.5],[1,0,.125],[0,1,.125],[-1,0,.125],[0,-1,.125]])a+=v[((y+oy+S)%S)*S+((x+ox+S)%S)]*w;const i=(y*S+x)*4;id.data[i]=id.data[i+1]=id.data[i+2]=a*255;id.data[i+3]=255;}
  g.putImageData(id,0,0);_grainT=new THREE.CanvasTexture(c);_grainT.wrapS=_grainT.wrapT=THREE.RepeatWrapping;_grainT.anisotropy=maxAniso;_grainT.userData.shared=true;return _grainT;}
function grainify(mat,amt,rep){mat.onBeforeCompile=sh=>{sh.uniforms.grainMap={value:grainTex()};
  sh.fragmentShader=sh.fragmentShader.replace('void main() {','uniform sampler2D grainMap;\nvoid main() {').replace('#include <map_fragment>','#include <map_fragment>\n{float gq=texture2D(grainMap,vUv*'+rep.toFixed(1)+').r*.6+texture2D(grainMap,vUv*'+(rep*3.7).toFixed(1)+').r*.4;diffuseColor.rgb*=1.0+'+amt.toFixed(3)+'*(gq-.5)*2.4;}');};
  mat.customProgramCacheKey=()=>'grain'+amt+'_'+rep;}
/* every generator paints: C colour (1024²), Hh height (512², grey), R roughness (256², grey) */
function paintSurf(id,dark){const r=prng(hashStr(id)+(dark?7:0)),S=1024,C=cnv(S,S),g=C.getContext('2d'),Hc=cnv(512,512),h=Hc.getContext('2d'),Rc=cnv(256,256),q=Rc.getContext('2d');
  const R=()=>r(),both=(fn)=>{for(const o of [-S,0,S])fn(o);};
  const speck=(n,cols,rmin,rmax,hv)=>{for(let i=0;i<n;i++){const x=R()*S,y=R()*S,rr=rmin+R()*(rmax-rmin);g.fillStyle=cols[(R()*cols.length)|0];g.beginPath();g.ellipse(x,y,rr,rr*(.6+R()*.4),R()*3,0,7);g.fill();
    if(hv!==undefined){h.fillStyle=`rgba(${hv},${hv},${hv},.6)`;h.beginPath();h.arc(x/2,y/2,Math.max(.6,rr/2),0,7);h.fill();}}};
  const hBase=(v)=>{h.fillStyle=`rgb(${v},${v},${v})`;h.fillRect(0,0,512,512);},rBase=(v)=>{q.fillStyle=`rgb(${v},${v},${v})`;q.fillRect(0,0,256,256);};
  const edgeLines=(col,w,inset,hv)=>{g.fillStyle=col;for(const x of [inset,S-inset-w]){g.fillRect(x,0,w,S);}h.fillStyle=`rgb(${hv},${hv},${hv})`;for(const x of [inset,S-inset-w])h.fillRect(x/2,0,w/2,512);q.fillStyle='rgb(120,120,120)';for(const x of [inset,S-inset-w])q.fillRect(x/4,0,Math.max(1,w/4),256);};
  const dashes=(col,w,len,gap,hv)=>{for(let y=0;y<S;y+=len+gap){g.fillStyle=col;g.fillRect(S/2-w/2,y,w,len);h.fillStyle=`rgb(${hv},${hv},${hv})`;h.fillRect(S/4-w/4,y/2,w/2,len/2);}};
  const wear=(alpha)=>{for(const u of [.3,.7]){const gr=g.createLinearGradient(S*(u-.09),0,S*(u+.09),0);gr.addColorStop(0,'rgba(0,0,0,0)');gr.addColorStop(.5,`rgba(10,8,8,${alpha})`);gr.addColorStop(1,'rgba(0,0,0,0)');g.fillStyle=gr;g.fillRect(S*(u-.09),0,S*.18,S);
    const rq=q.createLinearGradient(256*(u-.09),0,256*(u+.09),0);rq.addColorStop(0,'rgba(0,0,0,0)');rq.addColorStop(.5,'rgba(60,60,60,.45)');rq.addColorStop(1,'rgba(0,0,0,0)');q.fillStyle=rq;q.fillRect(256*(u-.09),0,256*.18,256);}};
  const crack=(col,wid,hv)=>{let x=R()*S,y=R()*S,a=R()*6.28;g.strokeStyle=col;g.lineWidth=wid;g.beginPath();g.moveTo(x,y);h.strokeStyle=`rgb(${hv},${hv},${hv})`;h.lineWidth=Math.max(1,wid/2);h.beginPath();h.moveTo(x/2,y/2);
    for(let k=0;k<14;k++){a+=(R()-.5)*1.1;x+=Math.cos(a)*14;y+=Math.sin(a)*14;g.lineTo(x,y);h.lineTo(x/2,y/2);}g.stroke();h.stroke();};
  let lineW=0;
  if(id==='sauce'||id==='asphalt'){const base=id==='sauce'?(dark?'#4e1a12':'#6a2216'):(dark?'#2a2c31':'#3b3e44');g.fillStyle=base;g.fillRect(0,0,S,S);hBase(120);rBase(id==='sauce'?150:200);
    // low-frequency tone patches
    for(let i=0;i<40;i++){const x=R()*S,y=R()*S,rr=60+R()*160,gr=g.createRadialGradient(x,y,0,x,y,rr);const c=R()<.5?'rgba(255,255,255,.035)':'rgba(0,0,0,.06)';gr.addColorStop(0,c);gr.addColorStop(1,'rgba(0,0,0,0)');both(o=>{g.fillStyle=gr;g.save();g.translate(0,o);g.fillRect(x-rr,y-rr,rr*2,rr*2);g.restore();});}
    // aggregate
    const ag=id==='sauce'?['#712518','#5f1d12','#7d2c1c','#86321f','#561a10']:['#4b4e55','#2b2d31','#5c5f66','#6d7078','#25272b','#7a6f62'];
    if(id==='sauce'){speck(30000,ag,.5,1.4,150);speck(900,ag,1.2,2.4,170);}else{speck(26000,ag,.6,2.2,138);speck(2600,ag,1.6,3.6,150);}
    if(id==='sauce'){for(let i=0;i<55;i++){const x=R()*S,y=R()*S,w=20+R()*70,hh=10+R()*30,a=R()*3;g.fillStyle='rgba(200,52,30,.33)';g.beginPath();g.ellipse(x,y,w,hh,a,0,7);g.fill();q.fillStyle='rgba(40,40,40,.7)';q.beginPath();q.ellipse(x/4,y/4,w/4,hh/4,a,0,7);q.fill();
        g.fillStyle='rgba(255,170,140,.22)';g.beginPath();g.ellipse(x-w*.25,y-hh*.25,w*.35,hh*.25,a,0,7);g.fill();}
      for(let i=0;i<420;i++){g.fillStyle=R()<.6?'#2f4a18':'#57702a';g.save();g.translate(R()*S,R()*S);g.rotate(R()*3);g.fillRect(0,0,2+R()*4,1.4+R()*1.6);g.restore();}
      for(let i=0;i<140;i++){g.fillStyle='rgba(250,230,190,.5)';g.fillRect(R()*S,R()*S,1.6,1.6);}}
    else{for(let i=0;i<7;i++){const x=80+R()*(S-260),y=R()*S,w=80+R()*140,hh=60+R()*160;g.fillStyle=R()<.5?'rgba(0,0,0,.12)':'rgba(255,255,255,.04)';g.fillRect(x,y,w,hh);g.strokeStyle='rgba(0,0,0,.25)';g.lineWidth=2;g.strokeRect(x,y,w,hh);}
      for(let i=0;i<10;i++)crack('rgba(12,12,14,.65)',1.8,70);
      for(let i=0;i<6;i++)crack('rgba(20,20,22,.9)',4,90);}
    wear(id==='sauce'?.22:.28);
    lineW=14;edgeLines(id==='sauce'?'#f6ecd2':'#f2f2ee',lineW,22,175);
    dashes(id==='sauce'?'rgba(255,236,200,.85)':'rgba(255,214,64,.9)',10,170,110,170);
    // paint wear on lines
    speck(900,[id==='sauce'?'#6a2216':'#3b3e44'],.8,2.4);}
  else if(id==='cobble'){g.fillStyle=dark?'#2f2a26':'#4a423a';g.fillRect(0,0,S,S);hBase(40);rBase(170);
    const rows=56,rh=S/rows;for(let ri=0;ri<rows;ri++){let x=-R()*30;const y=ri*rh;while(x<S){const w=rh*(.85+R()*.4),cx=x+w/2,cy=y+rh/2,tone=R(),base=dark?['#5e5852','#4d4844','#6b625a','#544b44']:['#7d7469','#6b6259','#8a8072','#625a52','#94897b','#7a6a5a'];
        const col=base[(tone*base.length)|0];const pad=1.6;
        g.fillStyle=col;g.beginPath();g.roundRect?g.roundRect(x+pad,y+pad,w-pad*2,rh-pad*2,5):g.rect(x+pad,y+pad,w-pad*2,rh-pad*2);g.fill();
        const gr=g.createRadialGradient(cx-w*.15,cy-rh*.2,1,cx,cy,w*.7);gr.addColorStop(0,'rgba(255,255,255,.18)');gr.addColorStop(1,'rgba(0,0,0,.22)');g.fillStyle=gr;g.fill();
        const hg=h.createRadialGradient(cx/2,cy/2,0,cx/2,cy/2,w*.36);hg.addColorStop(0,'rgb(235,235,235)');hg.addColorStop(.7,'rgb(170,170,170)');hg.addColorStop(1,'rgb(60,60,60)');h.fillStyle=hg;h.beginPath();h.ellipse(cx/2,cy/2,w/4-.6,rh/4-.6,0,0,7);h.fill();
        q.fillStyle='rgb(110,110,110)';q.beginPath();q.ellipse(cx/4,cy/4,w/8,rh/8,0,0,7);q.fill();
        x+=w;}}
    speck(5000,['rgba(0,0,0,.18)','rgba(255,255,255,.08)'],.6,1.8);
    // granite gutter bands at the edges
    for(const x0 of [0,S-36]){g.fillStyle=dark?'#3e3a36':'#6a645c';g.fillRect(x0,0,36,S);for(let y=0;y<S;y+=64){g.fillStyle='rgba(0,0,0,.45)';g.fillRect(x0,y,36,2);h.fillStyle='rgb(30,30,30)';h.fillRect(x0/2,y/2,18,1);}h.fillStyle='rgb(150,150,150)';h.fillRect(x0/2+1,0,16,512);}
    // faint painted centre line, worn into the stones
    for(let y=0;y<S;y+=200){g.fillStyle='rgba(240,236,224,.55)';g.fillRect(S/2-5,y,10,120);}}
  else if(id==='planks'){g.fillStyle='#3b2414';g.fillRect(0,0,S,S);hBase(40);rBase(190);const bw=30;
    for(let y=0;y<S;y+=bw){const tone=['#a8743f','#9a6534','#b57f48','#8f5c2e','#c08a52'][(R()*5)|0];const gr=g.createLinearGradient(0,y,0,y+bw);gr.addColorStop(0,shade(tone,.08));gr.addColorStop(.5,tone);gr.addColorStop(1,shade(tone,-.15));g.fillStyle=gr;g.fillRect(0,y+3,S,bw-5);
      for(let k=0;k<16;k++){g.strokeStyle=`rgba(70,38,16,${.12+R()*.22})`;g.lineWidth=.6+R()*1.1;const yy=y+4+R()*(bw-8);g.beginPath();g.moveTo(0,yy);let xx=0;while(xx<S){xx+=60+R()*80;g.lineTo(xx,yy+(R()-.5)*3);}g.stroke();}
      if(R()<.4){const kx=R()*S,ky=y+bw/2;for(let k=1;k<4;k++){g.strokeStyle='rgba(60,30,12,.4)';g.lineWidth=1.4;g.beginPath();g.ellipse(kx,ky,k*7,k*2.4,0,0,7);g.stroke();}}
      h.fillStyle='rgb(175,175,175)';h.fillRect(0,(y+3)/2,512,(bw-5)/2);
      // butt joints and nail heads over the joists
      const jx=R()*S;g.fillStyle='#2a170b';g.fillRect(jx,y+3,3,bw-5);h.fillStyle='rgb(40,40,40)';h.fillRect(jx/2,(y+3)/2,2,(bw-5)/2);
      for(const nx of [70,S/2,S-70])for(const ny of [y+9,y+bw-10]){g.fillStyle='#4c4a48';g.beginPath();g.arc(nx,ny,2.2,0,7);g.fill();g.fillStyle='rgba(255,255,255,.35)';g.beginPath();g.arc(nx-1,ny-1,1.2,0,7);g.fill();q.fillStyle='rgb(60,60,60)';q.fillRect(nx/4-1,ny/4-1,2,2);}}
    speck(1600,['rgba(40,20,8,.25)','rgba(255,230,180,.08)'],.6,1.6);
    g.fillStyle='rgba(255,246,220,.75)';for(const x of [24,S-38])g.fillRect(x,0,14,S);}
  else if(id==='ice'){const gr=g.createLinearGradient(0,0,S,0);gr.addColorStop(0,'#d8eefa');gr.addColorStop(.15,'#8fc4e2');gr.addColorStop(.5,'#74b3db');gr.addColorStop(.85,'#8fc4e2');gr.addColorStop(1,'#d8eefa');g.fillStyle=gr;g.fillRect(0,0,S,S);hBase(128);rBase(40);
    for(let i=0;i<50;i++){const x=R()*S,y=R()*S,rr=40+R()*120,gg=g.createRadialGradient(x,y,0,x,y,rr);gg.addColorStop(0,R()<.5?'rgba(255,255,255,.22)':'rgba(70,140,190,.16)');gg.addColorStop(1,'rgba(0,0,0,0)');g.fillStyle=gg;g.fillRect(x-rr,y-rr,rr*2,rr*2);}
    for(let i=0;i<26;i++)crack('rgba(235,248,255,.85)',1.8,165);for(let i=0;i<18;i++)crack('rgba(30,80,130,.55)',1.4,90);for(let i=0;i<30;i++){const x=R()*S,y=R()*S,rr=6+R()*30;g.fillStyle='rgba(255,255,255,.35)';g.beginPath();g.ellipse(x,y,rr,rr*.5,R()*3,0,7);g.fill();q.fillStyle='rgb(200,200,200)';q.beginPath();q.ellipse(x/4,y/4,rr/4,rr/8,0,0,7);q.fill();}
    // frost and snow dust (rough) with scrape marks (smooth)
    for(let i=0;i<3200;i++){const u=R(),edge=Math.min(u,1-u);if(R()>.25+(.2-edge)*3)continue;const x=u*S,y=R()*S,rr=.8+R()*3;g.fillStyle='rgba(255,255,255,.7)';g.beginPath();g.arc(x,y,rr,0,7);g.fill();q.fillStyle='rgb(220,220,220)';q.fillRect(x/4,y/4,1.2,1.2);}
    for(let i=0;i<60;i++){const x=R()*S,y=R()*S,l=80+R()*200;g.strokeStyle='rgba(255,255,255,.28)';g.lineWidth=1;g.beginPath();g.moveTo(x,y);g.lineTo(x+(R()-.5)*20,y+l);g.stroke();}
    lineW=14;edgeLines('#1f6fc4',lineW,22,150);dashes('rgba(255,255,255,.6)',8,150,130,140);}
  else if(id==='brick'){g.fillStyle=dark?'#3a2a22':'#8e7f6a';g.fillRect(0,0,S,S);hBase(40);rBase(200);const u=18;
    const brick=(x,y,w,hh)=>{const tone=(dark?['#6b3326','#5a2a20','#7a3b2b']:['#b0563a','#9d4a30','#c2643f','#a8513a','#8f4329'])[(R()*5)%(dark?3:5)|0];const pad=1.5;
      const gr=g.createLinearGradient(x,y,x+w,y+hh);gr.addColorStop(0,shade(tone,.1));gr.addColorStop(1,shade(tone,-.12));g.fillStyle=gr;g.fillRect(x+pad,y+pad,w-pad*2,hh-pad*2);
      h.fillStyle='rgb(190,190,190)';h.fillRect((x+pad)/2,(y+pad)/2,(w-pad*2)/2,(hh-pad*2)/2);h.fillStyle='rgb(215,215,215)';h.fillRect((x+pad+2)/2,(y+pad+2)/2,(w-pad*2-4)/2,(hh-pad*2-4)/2);};
    // herringbone-style basket weave in the middle, soldier course along the edges
    for(let by=0;by<S;by+=u*2)for(let bx=40;bx<S-40;bx+=u*2){const alt=((bx-40)/(u*2)+by/(u*2))%2;if(alt){brick(bx,by,u*2,u);brick(bx,by+u,u*2,u);}else{brick(bx,by,u,u*2);brick(bx+u,by,u,u*2);}}
    for(const x0 of [0,S-40])for(let y=0;y<S;y+=u)brick(x0,y,40,u);
    speck(6000,['rgba(0,0,0,.18)','rgba(255,240,220,.1)'],.5,1.6);
    for(let i=0;i<14;i++){const x=R()*S,y=R()*S,rr=30+R()*80,gg=g.createRadialGradient(x,y,0,x,y,rr);gg.addColorStop(0,'rgba(40,20,10,.18)');gg.addColorStop(1,'rgba(0,0,0,0)');g.fillStyle=gg;g.fillRect(x-rr,y-rr,rr*2,rr*2);}}
  else if(id==='marble'){g.fillStyle='#e4dccf';g.fillRect(0,0,S,S);hBase(128);rBase(30);
    for(let i=0;i<60;i++){const x=R()*S,y=R()*S,rr=60+R()*200,gg=g.createRadialGradient(x,y,0,x,y,rr);gg.addColorStop(0,R()<.5?'rgba(210,198,182,.35)':'rgba(255,255,255,.4)');gg.addColorStop(1,'rgba(0,0,0,0)');g.fillStyle=gg;g.fillRect(x-rr,y-rr,rr*2,rr*2);}
    for(let v=0;v<34;v++){let x=R()*S,y=R()*S,a=R()*6.28;const w=.8+R()*3,al=.3+R()*.4;g.strokeStyle=R()<.25?`rgba(176,140,90,${al})`:`rgba(96,88,84,${al})`;g.lineWidth=w;g.beginPath();g.moveTo(x,y);
      for(let k=0;k<40;k++){a+=(R()-.5)*.5;x+=Math.cos(a)*16;y+=Math.sin(a)*16;g.lineTo(x,y);if(R()<.06){g.stroke();g.lineWidth=w*.6;}}g.stroke();}
    // slab joints, slightly sunken
    for(let k=0;k<=4;k++){const y=k*256;g.fillStyle='rgba(120,110,100,.55)';g.fillRect(0,y-1,S,3);h.fillStyle='rgb(60,60,60)';h.fillRect(0,y/2-1,512,2);}
    for(const x of [S/3,2*S/3]){g.fillStyle='rgba(120,110,100,.45)';g.fillRect(x-1,0,3,S);h.fillStyle='rgb(60,60,60)';h.fillRect(x/2-1,0,2,512);}
    // brass inlay racing lines
    for(const x of [26,S-40]){const gr=g.createLinearGradient(x,0,x+14,0);gr.addColorStop(0,'#8a6a2a');gr.addColorStop(.5,'#e8c46a');gr.addColorStop(1,'#8a6a2a');g.fillStyle=gr;g.fillRect(x,0,14,S);q.fillStyle='rgb(70,70,70)';q.fillRect(x/4,0,4,256);h.fillStyle='rgb(150,150,150)';h.fillRect(x/2,0,7,512);}}
  // shared: soft darkening toward the edges where dirt collects
  const ed=g.createLinearGradient(0,0,S,0);ed.addColorStop(0,'rgba(0,0,0,.28)');ed.addColorStop(.06,'rgba(0,0,0,0)');ed.addColorStop(.94,'rgba(0,0,0,0)');ed.addColorStop(1,'rgba(0,0,0,.28)');g.fillStyle=ed;g.fillRect(0,0,S,S);
  return {C,H:Hc,R:Rc};}
function roadMaterial(id,dark){const sd=ROAD_SURF[id],p=paintSurf(id,dark);
  const map=T2(p.C),nm=T2(heightToNormal(p.H,id==='marble'||id==='ice'?3:6),0,0,true),rm=T2(p.R,0,0,true);
  for(const t of [map,nm,rm]){t.wrapS=THREE.ClampToEdgeWrapping;t.wrapT=THREE.RepeatWrapping;}
  const o={map,normalMap:nm,normalScale:new THREE.Vector2(sd.ns,sd.ns),roughnessMap:rm,roughness:Math.min(1,sd.rough*1.6),metalness:0,envMapIntensity:id==='ice'||id==='marble'?.7:.5,vertexColors:true};
  const m=sd.phys?new THREE.MeshPhysicalMaterial(Object.assign(o,{clearcoat:id==='ice'?.6:.5,clearcoatRoughness:id==='ice'?.08:.12})):new THREE.MeshStandardMaterial(o);
  if(qKey==='fast'){m.normalMap=null;}else grainify(m,sd.grain,3.0);return m;}
/* road built in sections of different paving; vertex colours carry large-scale tone and edge occlusion */
function buildRoad(def,SJ0,SJ1){const pal=ROAD_THEME[def.theme]||ROAD_THEME.kitchen,h=hashStr(def.id||def.name||'x'),span=SJ1-SJ0;
  const order=[0,1,2].map(i=>pal[(i+h)%pal.length]);const cuts=[SJ0,SJ0+Math.round(span*(.34+((h>>4)%10)*.012)),SJ0+Math.round(span*(.68+((h>>8)%10)*.01)),SJ1];
  const segs=[[cuts[0],cuts[1],order[0]],[cuts[1],cuts[2],order[1]],[cuts[2],cuts[3],(h>>12)%2?order[2]:order[0]]];
  const mats={};const tone=(x,z,o)=>{const n=bnoise(x*.006+3.1,z*.006-1.7)*.6+bnoise(x*.02,z*.02)*.4,e=Math.abs(o)/RW;return (.9+n*.16)*(1-.16*Math.pow(Math.max(0,(e-.86)/.14),1.5));};
  ROAD_SEGS=[];
  for(const [a,b,id] of segs){if(b<=a)continue;const m=mats[id]||(mats[id]=roadMaterial(id,def.theme==='night'));strip(a,b,-RW,RW,.06,m,RW*2,false,tone);ROAD_SEGS.push({a,b,id});}
  // steel expansion joints where the paving changes
  const jm=new THREE.MeshStandardMaterial({color:'#4a4d52',metalness:.85,roughness:.32,envMapIntensity:1});
  for(let i=1;i<segs.length;i++){if(segs[i][2]===segs[i-1][2])continue;const j=segs[i][0];strip(j-1,j+1,-RW,RW,.1,jm,4);}
  return ROAD_SEGS;}
let ROAD_SEGS=[];
const PROP_PACKS={"tree_pine1":{"h":[{"n":"tree_pine1","v":1677,"i":4791,"c":1,"uv":0,"i32":0,"o":[0,12.0301,0],"s":12.03012}]},"tree_pine2":{"h":[{"n":"tree_pine2","v":1673,"i":4791,"c":1,"uv":0,"i32":0,"o":[0,10.7447,0],"s":10.73693}]},"tree_round1":{"h":[{"n":"tree_round1","v":1050,"i":3792,"c":1,"uv":0,"i32":0,"o":[0,8.8817,0],"s":8.88175}]},"tree_round2":{"h":[{"n":"tree_round2","v":1050,"i":3792,"c":1,"uv":0,"i32":0,"o":[0,10.8407,0],"s":10.84067}]},"tree_shrub":{"h":[{"n":"tree_shrub","v":648,"i":1302,"c":1,"uv":0,"i32":0,"o":[0,2.092,0],"s":3.31336}]},"skyline":{"h":[{"n":"skyline","v":7167,"i":18234,"c":0,"uv":1,"i32":0,"o":[0,740.1505,0],"s":1765.03434}]},"mount":{"h":[{"n":"mount","v":3517,"i":21000,"c":0,"uv":1,"i32":0,"o":[0,172.7069,0],"s":1000.00012}]},"tunnel":{"h":[{"n":"body","v":7339,"i":26991,"c":1,"uv":0,"i32":0,"o":[0,175.736,0.082],"s":1469.16602},{"n":"glow","v":2404,"i":9000,"c":1,"uv":0,"i32":0,"o":[0,183.6109,-4.0292],"s":1464.97278}]},"city":{"h":[{"n":"city","v":20010,"i":45969,"c":1,"uv":0,"i32":0,"o":[0,193.9968,0],"s":1300}]},"tree_pine1_lo":{"h":[{"n":"tree_pine1_lo","v":716,"i":1254,"c":1,"uv":0,"i32":0,"o":[-0.1016,11.9914,0.1502],"s":11.99137}]},"tree_pine2_lo":{"h":[{"n":"tree_pine2_lo","v":725,"i":1257,"c":1,"uv":0,"i32":0,"o":[0,10.7136,0.1127],"s":10.69771}]},"tree_round1_lo":{"h":[{"n":"tree_round1_lo","v":457,"i":1257,"c":1,"uv":0,"i32":0,"o":[0,8.8659,0],"s":8.86587}]},"tree_round2_lo":{"h":[{"n":"tree_round2_lo","v":457,"i":1260,"c":1,"uv":0,"i32":0,"o":[0,10.8128,0],"s":10.81284}]},"waterfall":{"h":[{"n":"wf0","v":1073,"i":5082,"c":0,"uv":1,"i32":0,"o":[-0.4102,2.9013,0.5179],"s":11.69935},{"n":"wf1","v":1066,"i":5097,"c":0,"uv":1,"i32":0,"o":[-0.3607,2.8235,-2.132],"s":12.55984},{"n":"wf2","v":1129,"i":5094,"c":0,"uv":1,"i32":0,"o":[-0.9206,3.0562,1.0239],"s":11.62378},{"n":"wf3","v":1143,"i":5091,"c":0,"uv":1,"i32":0,"o":[0.0464,2.8651,-0.096],"s":14.64192},{"n":"wf4","v":1115,"i":5094,"c":0,"uv":1,"i32":0,"o":[0.2119,2.8911,-0.0143],"s":11.5846},{"n":"wf5","v":1165,"i":5088,"c":0,"uv":1,"i32":0,"o":[0.2774,2.8717,0.3831],"s":13.0889},{"n":"wf6","v":1268,"i":5097,"c":0,"uv":1,"i32":0,"o":[-0.6664,2.9964,1.301],"s":13.16944},{"n":"wf7","v":1450,"i":5091,"c":0,"uv":1,"i32":0,"o":[-0.0831,2.6855,0.8455],"s":13.92758},{"n":"wf8","v":1911,"i":5097,"c":0,"uv":1,"i32":0,"o":[-0.2572,2.7587,0.5623],"s":13.49127},{"n":"wf9","v":3032,"i":5097,"c":0,"uv":1,"i32":0,"o":[-0.1573,2.6081,0.9822],"s":13.1312}]},"riverbed":{"h":[{"n":"cobble","v":4271,"i":14994,"c":0,"uv":1,"i32":0,"o":[0.0146,0.4103,0.0062],"s":4.34363}]},"pond":{"h":[{"n":"pond_base","v":860,"i":2844,"c":0,"uv":1,"i32":0,"o":[0.4372,-2.2792,-0.0545],"s":10.53573},{"n":"pond_grass","v":7624,"i":25524,"c":0,"uv":1,"i32":0,"o":[2.0495,-0.0685,-0.0508],"s":13.25558},{"n":"pond_rock","v":884,"i":1572,"c":1,"uv":0,"i32":0,"o":[0.4377,-2.2526,0.0626],"s":9.24595},{"n":"pond_water","v":81,"i":384,"c":0,"uv":1,"i32":0,"o":[0,-0.1269,0],"s":9.68269},{"n":"pond_wave","v":1104,"i":1872,"c":0,"uv":0,"i32":0,"o":[0.0139,-0.1765,0.168],"s":4.61376}]}};
const PROP_TEX={"tex_skyline":"assets/tex/tex_skyline.457a6fecf7.jpg","tex_skyline_e":"assets/tex/tex_skyline_e.30cb2dfa85.jpg","tex_mount":"assets/tex/tex_mount.b8a1c13020.jpg","tex_space":"assets/tex/tex_space.98cb95ba4c.jpg","tex_wf0":"assets/tex/tex_wf0.76f8455401.jpg","tex_wf1":"assets/tex/tex_wf1.8327e7fb03.jpg","tex_wf2":"assets/tex/tex_wf2.b9baa7fcb6.jpg","tex_wf3":"assets/tex/tex_wf3.1339551440.jpg","tex_wf4":"assets/tex/tex_wf4.5a24678b6c.jpg","tex_wf5":"assets/tex/tex_wf5.c7c965caa0.jpg","tex_wf6":"assets/tex/tex_wf6.2c65d0bc3f.jpg","tex_wf7":"assets/tex/tex_wf7.6ffe181e72.jpg","tex_wf8":"assets/tex/tex_wf8.735a884f42.jpg","tex_wf9":"assets/tex/tex_wf9.c0a2dc9c2d.jpg","tex_riverbed":"assets/tex/tex_riverbed.0b4642c165.jpg","sky_anime":"assets/tex/sky_anime.590aabd5d9.jpg","sky_beach":"assets/tex/sky_beach.d899e80210.jpg","sky_mc":"assets/tex/sky_mc.e744b96a84.jpg","sky_cave":"assets/tex/sky_cave.7ed938e790.jpg","sky_nebula":"assets/tex/sky_nebula.f4e8c6c9bb.jpg","tex_pond":"assets/tex/tex_pond.8f551e9556.jpg","tex_pondgrass":"assets/tex/tex_pondgrass.ea3a48c6f8.jpg"};

/* decoded once per session; geometry is shared and never disposed with a track */
const PROPG={};
function propGeos(name){if(PROPG[name])return PROPG[name];const pk=PROP_PACKS[name],bin=pk.b?new Uint8Array(pk.b):Uint8Array.from(atob(pk.d),c=>c.charCodeAt(0)),buf=bin.buffer;let o=0;const out={};
  for(const m of pk.h){const v=m.v,pos=new Int16Array(buf,o,v*3);o+=v*6;const nr=new Int8Array(buf,o,v*3);o+=v*3;let col=null,uv=null;if(m.c){col=new Uint8Array(buf,o,v*3);o+=v*3;}if(o%2)o++;if(m.uv){uv=new Uint16Array(buf,o,v*2);o+=v*4;}while(o%4)o++;
    const idx=m.i32?new Uint32Array(buf,o,m.i):new Uint16Array(buf,o,m.i);o+=m.i*(m.i32?4:2);while(o%4)o++;
    const P=new Float32Array(v*3),Nn=new Float32Array(v*3);for(let i=0;i<v*3;i++){P[i]=pos[i]/32767*m.s+m.o[i%3];Nn[i]=nr[i]/127;}
    const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.BufferAttribute(P,3));g.setAttribute('normal',new THREE.BufferAttribute(Nn,3));
    if(col){const C=new Float32Array(v*3);for(let i=0;i<v*3;i++)C[i]=col[i]/255;g.setAttribute('color',new THREE.BufferAttribute(C,3));}
    if(uv){const U=new Float32Array(v*2);for(let i=0;i<v*2;i++)U[i]=uv[i]/65535;g.setAttribute('uv',new THREE.BufferAttribute(U,2));}
    g.setIndex(new THREE.BufferAttribute(m.i32?new Uint32Array(idx):new Uint16Array(idx),1));g.computeBoundingSphere();KGSET.add(g);out[m.n]=g;}
  return PROPG[name]=out;}
const PROPT={};
const texSrc=v=>!v?'':v.length<400?v:'data:image/jpeg;base64,'+v;
function propTex(name,srgb){if(PROPT[name])return PROPT[name];const im=new Image();im.src=texSrc(PROP_TEX[name]);const t=new THREE.Texture(im);im.onload=()=>{t.needsUpdate=true;};if(im.complete)t.needsUpdate=true;
  if(srgb!==false)t.encoding=THREE.sRGBEncoding;t.anisotropy=maxAniso;t.userData.shared=true;return PROPT[name]=t;}
/* snow settles on upward-facing faces */
function snowify(mat,amt){mat.onBeforeCompile=sh=>{sh.vertexShader=sh.vertexShader.replace('#include <common>','#include <common>\nvarying float vUp;').replace('#include <beginnormal_vertex>','#include <beginnormal_vertex>\nvUp=normalize((modelMatrix*vec4(objectNormal,0.)).xyz).y;');
  sh.fragmentShader=sh.fragmentShader.replace('#include <common>','#include <common>\nvarying float vUp;').replace('#include <map_fragment>','#include <map_fragment>\ndiffuseColor.rgb=mix(diffuseColor.rgb,vec3(.93,.96,1.),smoothstep(.55,.8,vUp)*'+amt.toFixed(2)+');');};mat.customProgramCacheKey=()=>'snow'+amt;return mat;}
/* the sculpted mountain model, scattered between the arena and the far ridges */
function mountainModels(n,r0,r1,sc,snow,tint,seed){const g=propGeos('mount').mount,mat=new THREE.MeshStandardMaterial({map:propTex('tex_mount'),color:tint||'#ffffff',roughness:.95});if(snow)snowify(mat,snow);
  const im=new THREE.InstancedMesh(g,mat,n),q=new THREE.Quaternion(),m4=new THREE.Matrix4(),e=new THREE.Euler();let k=seed||0;
  for(let i=0;i<n;i++){const a=i/n*Math.PI*2+rnd()*.4,d=r0+rnd()*(r1-r0),s=sc*(.75+rnd()*.5);q.setFromEuler(e.set(0,rnd()*6.28,0));m4.compose(new THREE.Vector3(Math.cos(a)*d,-62,Math.sin(a)*d),q,new THREE.Vector3(s,s*(.9+rnd()*.5),s));im.setMatrixAt(i,m4);}
  im.frustumCulled=false;im.userData.noLift=true;world.add(im);return im;}
/* the futuristic tunnel, bent to follow the road over the straightest clear stretch */
let TUNNEL=null;
function placeTunnel(len){const step=T.L/N,K=Math.round(len/step),near=(j,list,r)=>list.some(e=>{const d=Math.abs(j-e)%N;return Math.min(d,N-d)<r;});
  let best=-1,bs=1e9;for(let j=80;j<N-K-60;j+=3){let m=0,bad=false;for(let o=-6;o<=K+6;o+=2){const jj=(j+o)%N,p=track[jj];m=Math.max(m,Math.abs(p.bend));
      if(GLIDE&&jj>GLIDE.rj-40&&jj<GLIDE.j1+40){bad=true;break;}if(loopNear(jj,45)){bad=true;break;}}
    if(bad)continue;if(near(j,ramps.map(r=>r.j),K+30)||near(j+K,ramps.map(r=>r.j),30))continue;
    if(SHORTS.some(sc=>[sc.a,sc.b].some(e=>{const d=(e-j+N)%N;return d<K+40||(N-d)<40;})))continue;
    if(m<bs){bs=m;best=j;}}
  if(best<0||bs>.6)return null;
  const G=propGeos('tunnel'),sx=.5,sy=.5;const mk=(src,mat)=>{const g=src.clone(),pa=g.attributes.position,na=g.attributes.normal;g.computeBoundingBox();const zb=g.boundingBox,Z0=-1469.25,Z1=1469.25;
    for(let i=0;i<pa.count;i++){const t=(pa.getZ(i)-Z0)/(Z1-Z0)*K,j0=Math.floor(t),f=t-j0,a=track[(best+j0)%N],b=track[(best+j0+1)%N];
      const cx=a.x+(b.x-a.x)*f,cz=a.y+(b.y-a.y)*f,nx=a.nx+(b.nx-a.nx)*f,nz=a.ny+(b.ny-a.ny)*f,tx=a.tx+(b.tx-a.tx)*f,tz=a.ty+(b.ty-a.ty)*f,x=pa.getX(i)*sx;
      pa.setXYZ(i,cx+nx*x,groundAt(cx,cz)-3+pa.getY(i)*sy,cz+nz*x);const lx=na.getX(i),ly=na.getY(i),lz=na.getZ(i);na.setXYZ(i,nx*lx+tx*lz,ly,nz*lx+tz*lz);}
    g.computeBoundingSphere();const m=new THREE.Mesh(g,mat);m.userData.noLift=true;world.add(m);return m;};
  const body=mk(G.body,new THREE.MeshStandardMaterial({vertexColors:true,roughness:.45,metalness:.55,envMapIntensity:.9,side:THREE.DoubleSide}));body.castShadow=true;body.receiveShadow=true;
  mk(G.glow,new THREE.MeshBasicMaterial({color:'#2fa6d6'}));
  return {j:best,K};}

/* ---------- scene fillers built from the imported packs (all instanced, so the extra scenery is a handful of draw calls) ---------- */
function forest(list,y,snow){/* list: [name,x,z,scale,rot] */const by={};for(const t of list)(by[t[0]]=by[t[0]]||[]).push(t);
  const m4=new THREE.Matrix4(),q=new THREE.Quaternion(),e=new THREE.Euler(),v=new THREE.Vector3(),sc=new THREE.Vector3();
  for(const name in by){const ln=PROP_PACKS[name+'_lo']?name+'_lo':name,g0=propGeos(ln)[ln];let g=g0;if(snow){g=g0.clone();const ca=g.attributes.color,na=g.attributes.normal;for(let i=0;i<ca.count;i++){const k=Math.min(1,Math.max(0,(na.getY(i)-.25)*2))*snow;ca.setXYZ(i,ca.getX(i)+(.92-ca.getX(i))*k,ca.getY(i)+(.95-ca.getY(i))*k,ca.getZ(i)+(1-ca.getZ(i))*k);}}
    const L=by[name],im=new THREE.InstancedMesh(g,new THREE.MeshStandardMaterial({vertexColors:true,roughness:.85}),L.length);
    L.forEach((t,i)=>{q.setFromEuler(e.set(0,t[4]??rnd()*6.28,0));m4.compose(v.set(t[1],t[5]??(typeof y==='function'?y(t[1],t[2]):y),t[2]),q,sc.set(t[3],t[3]*(.9+rnd()*.25),t[3]));im.setMatrixAt(i,m4);});
    im.castShadow=false;im.receiveShadow=false;im.userData.noLift=true;world.add(im);}}
function ring(n,r0,r1,f){const out=[];for(let i=0;i<n;i++){const a=rnd()*6.283,r=r0+Math.sqrt(rnd())*(r1-r0);out.push(f(Math.cos(a)*r,Math.sin(a)*r,a));}return out;}
/* lit billboards for the night city: original pizza-shop signs painted on a canvas */
function signTex(lines,bg,fg,accent){const c=cnv(512,256),g=c.getContext('2d');const gr=g.createLinearGradient(0,0,0,256);gr.addColorStop(0,shade(bg,.15));gr.addColorStop(1,shade(bg,-.25));g.fillStyle=gr;g.fillRect(0,0,512,256);
  g.strokeStyle=accent;g.lineWidth=10;g.strokeRect(10,10,492,236);g.fillStyle=fg;g.textAlign='center';g.textBaseline='middle';g.shadowColor=accent;g.shadowBlur=18;
  g.font='900 76px system-ui,sans-serif';g.fillText(lines[0],256,lines[1]?100:128);if(lines[1]){g.font='800 42px system-ui,sans-serif';g.fillText(lines[1],256,186);}
  g.shadowBlur=0;g.fillStyle=accent;for(let i=0;i<5;i++){g.beginPath();g.arc(52+i*102,232,6,0,7);g.fill();}return T2(c);}
function crustTex(){const c=cnv(512,128),g=c.getContext('2d');const gr=g.createLinearGradient(0,0,0,128);gr.addColorStop(0,'#9e5f28');gr.addColorStop(.45,'#e3a862');gr.addColorStop(.6,'#d99a52');gr.addColorStop(1,'#8f5422');g.fillStyle=gr;g.fillRect(0,0,512,128);
  for(let i=0;i<500;i++){const x=rnd()*512,y=rnd()*128,rx=1+rnd()*7,ry=1+rnd()*3,col=rnd()<.5?'rgba(100,52,18,.45)':'rgba(255,224,170,.35)';for(const ox of [-512,0,512]){g.fillStyle=col;g.beginPath();g.ellipse(x+ox,y,rx,ry,0,0,7);g.fill();}}
  for(let i=0;i<120;i++){g.fillStyle='rgba(255,250,235,.6)';g.fillRect(rnd()*512,rnd()*128,1.5,1.5);}
  return c;}
function woodTex(){const S=1024,c=cnv(S,S),g=c.getContext('2d');for(let i=0;i<8;i++){g.fillStyle=['#6e4527','#7a4f2d','#6a4224','#7d5230'][i%4];g.fillRect(0,i*128,S,128);g.fillStyle='#3f2513';g.fillRect(0,i*128,S,3);}
  for(let i=0;i<500;i++){g.strokeStyle='rgba(55,30,12,'+(.15+rnd()*.25)+')';g.lineWidth=.8+rnd()*2.2;const y=rnd()*S;g.beginPath();g.moveTo(0,y);g.bezierCurveTo(S*.33,y+rnd()*10-5,S*.66,y+rnd()*10-5,S,y);g.stroke();}
  for(let i=0;i<12;i++){const x=rnd()*S,y=rnd()*S;g.strokeStyle='rgba(50,26,10,.45)';g.lineWidth=2;for(let r=3;r<18;r+=4){g.beginPath();g.ellipse(x,y,r*2,r*.7,0,0,7);g.stroke();}}
  return c;}
function brickTex(){const c=cnv(1024,512),g=c.getContext('2d');g.fillStyle='#4a2a1c';g.fillRect(0,0,1024,512);
  for(let r=0;r<8;r++)for(let i=-1;i<5;i++){const x=i*256+(r%2?128:0),y=r*64;const v=rnd(),gr=g.createLinearGradient(0,y,0,y+64);const b=v<.33?'#8a3b22':v<.66?'#9b4528':'#7a321c';gr.addColorStop(0,shade(b,.12));gr.addColorStop(1,shade(b,-.18));g.fillStyle=gr;g.fillRect(x+5,y+5,246,54);
    for(let k=0;k<70;k++){g.fillStyle=rnd()<.5?'rgba(0,0,0,.14)':'rgba(255,220,190,.08)';g.fillRect(x+5+rnd()*240,y+5+rnd()*50,2+rnd()*3,2+rnd()*2);}g.fillStyle='rgba(255,255,255,.08)';g.fillRect(x+5,y+5,246,3);}return c;}
function slateTex(){const S=1024,c=cnv(S,S),g=c.getContext('2d');g.fillStyle='#2a2a33';g.fillRect(0,0,S,S);
  for(let i=0;i<900;i++){const x=rnd()*S,y=rnd()*S,r=4+rnd()*28,a=rnd()*3,col=rnd()<.5?'60,60,72':'20,20,26';wrap9(S,S,(ox,oy)=>{g.fillStyle='rgba('+col+',.35)';g.beginPath();g.ellipse(x+ox,y+oy,r,r*.6,a,0,7);g.fill();});}return c;}
function sandTex(){const S=512,c=cnv(S,S),g=c.getContext('2d');g.fillStyle='#e9d29a';g.fillRect(0,0,S,S);for(let i=0;i<3000;i++){g.fillStyle=rnd()<.5?'rgba(200,170,110,.5)':'rgba(255,245,210,.5)';g.fillRect(rnd()*S,rnd()*S,1.5,1.5);}return c;}
function waterNormal(){const S=256,c=cnv(S,S),g=c.getContext('2d'),img=g.createImageData(S,S),d=img.data;
  const W=[[1,2,.9,.3],[3,-1,.5,1.7],[-2,3,.4,2.5],[5,4,.2,.9],[-6,2,.18,4.1],[2,-7,.15,5.2]];
  for(let y=0;y<S;y++)for(let x=0;x<S;x++){let dx=0,dy=0;for(const [kx,ky,a,ph] of W){const th=2*Math.PI*(kx*x+ky*y)/S+ph,cs=Math.cos(th)*a*2*Math.PI/S;dx+=cs*kx;dy+=cs*ky;}
    let nx=-dx*14,ny=-dy*14,nz=1;const l=Math.hypot(nx,ny,nz);nx/=l;ny/=l;nz/=l;const i=(y*S+x)*4;d[i]=(nx*.5+.5)*255;d[i+1]=(ny*.5+.5)*255;d[i+2]=(nz*.5+.5)*255;d[i+3]=255;}
  g.putImageData(img,0,0);return c;}
function radial(stops,S){S=S||128;const c=cnv(S,S),g=c.getContext('2d'),gr=g.createRadialGradient(S/2,S/2,0,S/2,S/2,S/2);stops.forEach(([o,col])=>gr.addColorStop(o,col));g.fillStyle=gr;g.fillRect(0,0,S,S);return c;}
function checkerTex(){const c=cnv(320,64),g=c.getContext('2d');for(let i=0;i<10;i++)for(let r=0;r<2;r++){g.fillStyle=(i+r)%2?'#141010':'#fff4dc';g.fillRect(i*32,r*32,32,32);}return c;}
function padTex(){const c=cnv(128,256),g=c.getContext('2d');const gr=g.createLinearGradient(0,0,128,0);gr.addColorStop(0,'#7a1608');gr.addColorStop(.5,'#ff5a1a');gr.addColorStop(1,'#7a1608');g.fillStyle=gr;g.fillRect(0,0,128,256);
  g.fillStyle='#ffe066';for(let i=0;i<2;i++){const y=i*128+20;g.beginPath();g.moveTo(64,y);g.lineTo(116,y+52);g.lineTo(116,y+84);g.lineTo(64,y+32);g.lineTo(12,y+84);g.lineTo(12,y+52);g.closePath();g.fill();}
  g.strokeStyle='#fff4dc';g.lineWidth=6;g.strokeRect(3,-10,122,276);return c;}
function pepTex(){const c=cnv(256,256),g=c.getContext('2d');g.fillStyle='#a92a17';g.fillRect(0,0,256,256);const gr=g.createRadialGradient(128,128,40,128,128,128);gr.addColorStop(0,'#c93a22');gr.addColorStop(.85,'#b8311c');gr.addColorStop(1,'#7d1d0e');g.fillStyle=gr;g.beginPath();g.arc(128,128,124,0,7);g.fill();
  for(let i=0;i<34;i++){const a=rnd()*7,r=rnd()*100;g.fillStyle=rnd()<.55?'rgba(110,20,8,.8)':'rgba(240,160,130,.75)';g.beginPath();g.ellipse(128+Math.cos(a)*r,128+Math.sin(a)*r,2+rnd()*6,2+rnd()*4,rnd()*3,0,7);g.fill();}return c;}
function lidTex(){const c=cnv(256,256),g=c.getContext('2d');g.fillStyle='#f5ead2';g.fillRect(0,0,256,256);g.strokeStyle='#d6402a';g.lineWidth=14;g.strokeRect(10,10,236,236);
  g.fillStyle='#d6402a';g.beginPath();g.moveTo(128,46);g.lineTo(62,196);g.lineTo(194,196);g.closePath();g.fill();g.fillStyle='#f5c443';g.beginPath();g.moveTo(128,76);g.lineTo(80,182);g.lineTo(176,182);g.closePath();g.fill();
  g.fillStyle='#b8311c';[[118,140],[146,156],[128,112]].forEach(([x,y])=>{g.beginPath();g.arc(x,y,9,0,7);g.fill();});return c;}
function boxSideTex(){const c=cnv(256,64),g=c.getContext('2d');g.fillStyle='#ead9b6';g.fillRect(0,0,256,64);g.fillStyle='#d6402a';g.fillRect(0,22,256,20);g.fillStyle='#fff4dc';g.font='bold 14px Arial';g.textAlign='center';g.fillText('HOT & FRESH',128,37);return c;}
function chevTex(dir){const c=cnv(256,128),g=c.getContext('2d');g.fillStyle='#d6402a';g.fillRect(0,0,256,128);g.fillStyle='#fff4dc';
  for(let i=0;i<3;i++){const x=34+i*70;g.beginPath();if(dir>0){g.moveTo(x,20);g.lineTo(x+36,64);g.lineTo(x,108);g.lineTo(x+24,108);g.lineTo(x+60,64);g.lineTo(x+24,20);}else{g.moveTo(x+60,20);g.lineTo(x+24,64);g.lineTo(x+60,108);g.lineTo(x+36,108);g.lineTo(x,64);g.lineTo(x+36,20);}g.closePath();g.fill();}
  g.strokeStyle='#7d1d0e';g.lineWidth=8;g.strokeRect(4,4,248,120);return c;}
function stripeTex(a,b,n){const c=cnv(256,32),g=c.getContext('2d');for(let i=0;i<n;i++){g.fillStyle=i%2?b:a;g.fillRect(i*256/n,0,256/n+1,32);}return c;}
function windowTex(){const c=cnv(128,256),g=c.getContext('2d');g.fillStyle='#0b0d18';g.fillRect(0,0,128,256);for(let y=6;y<256;y+=12)for(let x=6;x<128;x+=12){if(rnd()<.45){g.fillStyle=rnd()<.7?'#ffd27a':'#9fd0ff';g.fillRect(x,y,7,7);}}return c;}
function pineTex(){const c=cnv(256,256),g=c.getContext('2d');g.fillStyle='#d99a1e';g.fillRect(0,0,256,256);g.strokeStyle='#7a4a10';g.lineWidth=5;
  for(let i=-8;i<16;i++){g.beginPath();g.moveTo(i*32,0);g.lineTo(i*32+256,256);g.stroke();g.beginPath();g.moveTo(i*32,256);g.lineTo(i*32+256,0);g.stroke();}
  g.fillStyle='#f6c64a';for(let y=0;y<256;y+=32)for(let x=0;x<256;x+=32){g.beginPath();g.arc(x+16,y,4,0,7);g.fill();}return c;}
const bannerC=cnv(1024,128);
function drawBanner(){const g=bannerC.getContext('2d');g.fillStyle='#1b0f0b';g.fillRect(0,0,1024,128);
  for(let i=0;i<64;i++)for(let r=0;r<2;r++){g.fillStyle=(i+r)%2?'#fff4dc':'#1b0f0b';g.fillRect(i*16,r*12,16,12);g.fillRect(i*16,104+r*12,16,12);}
  g.fillStyle='#d6402a';g.fillRect(0,24,1024,80);g.font='64px Bungee, "Arial Black", Impact, sans-serif';g.textAlign='center';g.textBaseline='middle';
  g.fillStyle='#7d1d0e';g.fillText('CRUST RUSH',512,70);g.fillStyle='#f7c948';g.fillText('CRUST RUSH',512,64);}
drawBanner();

const TX={crust:crustTex(),pep:pepTex(),lid:lidTex(),side:boxSideTex(),glow:radial([[0,'rgba(255,255,255,1)'],[.25,'rgba(255,255,255,.55)'],[1,'rgba(255,255,255,0)']]),
  smoke:radial([[0,'rgba(255,255,255,.9)'],[.5,'rgba(255,255,255,.35)'],[1,'rgba(255,255,255,0)']],64),spark:radial([[0,'rgba(255,255,255,1)'],[.2,'rgba(255,255,255,.9)'],[.5,'rgba(255,255,255,.25)'],[1,'rgba(255,255,255,0)']],64)};
const crustT=T2(TX.crust,4,1),pepMat=new THREE.MeshStandardMaterial({map:T2(TX.pep),roughness:.42});

/* ================= MERGE HELPER ================= */
const _m4=new THREE.Matrix4(),_inv=new THREE.Matrix4();
const canVC=m=>m.isMeshStandardMaterial&&!m.map&&!m.transparent&&!m.vertexColors&&!(m.emissiveIntensity>0&&m.emissive&&m.emissive.r+m.emissive.g+m.emissive.b>0);
const VCM=new Map();const vcKey=m=>'VC|'+(Math.round(m.roughness*5)/5)+'|'+(Math.round(m.metalness*4)/4)+'|'+((m.clearcoat||0)>.3?1:0)+'|'+((m.sheen||0)>.3?1:0);
function vcMat(m){const k=vcKey(m);let v=VCM.get(k);if(!v){const o={vertexColors:true,roughness:Math.round(m.roughness*5)/5,metalness:Math.round(m.metalness*4)/4};
  v=((m.clearcoat||0)>.3||(m.sheen||0)>.3)?new THREE.MeshPhysicalMaterial(Object.assign(o,{clearcoat:(m.clearcoat||0)>.3?1:0,clearcoatRoughness:.12,sheen:(m.sheen||0)>.3?.6:0,sheenRoughness:.6,sheenColor:new THREE.Color('#ffffff')})):new THREE.MeshStandardMaterial(o);VCM.set(k,v);v.userData.shared=true;}return v;}
function bake(S,shadow,vc){S.updateMatrixWorld(true);_inv.copy(S.matrixWorld).invert();const buckets=new Map();
  S.traverse(o=>{if(!o.isMesh)return;_m4.multiplyMatrices(_inv,o.matrixWorld);let g=o.geometry.index?o.geometry.toNonIndexed():o.geometry.clone();g.applyMatrix4(_m4);
    if(!g.attributes.uv)g.setAttribute('uv',new THREE.Float32BufferAttribute(new Float32Array(g.attributes.position.count*2),2));
    const uv=vc&&canVC(o.material),key=uv?vcKey(o.material):o.material.uuid;if(!buckets.has(key))buckets.set(key,{mat:uv?vcMat(o.material):o.material,list:[],cols:uv?[]:null});const bk=buckets.get(key);bk.list.push(g);if(uv)bk.cols.push(o.material.color);});
  while(S.children.length)S.remove(S.children[0]);
  for(const {mat,list,cols} of buckets.values()){let n=0;list.forEach(g=>n+=g.attributes.position.count);const P=new Float32Array(n*3),Nn=new Float32Array(n*3),U=new Float32Array(n*2),Cc=(cols||mat.vertexColors)?new Float32Array(n*3):null;let o=0;
    list.forEach((g,gi)=>{const c0=g.attributes.position.count;P.set(g.attributes.position.array,o*3);Nn.set(g.attributes.normal.array,o*3);U.set(g.attributes.uv.array,o*2);if(Cc&&cols){const c=cols[gi];for(let i=0;i<c0;i++){Cc[(o+i)*3]=c.r;Cc[(o+i)*3+1]=c.g;Cc[(o+i)*3+2]=c.b;}}else if(Cc){if(g.attributes.color)Cc.set(g.attributes.color.array.subarray(0,c0*3),o*3);else Cc.fill(1,o*3,(o+c0)*3);}o+=c0;g.dispose();});
    const mg=new THREE.BufferGeometry();mg.setAttribute('position',new THREE.BufferAttribute(P,3));mg.setAttribute('normal',new THREE.BufferAttribute(Nn,3));mg.setAttribute('uv',new THREE.BufferAttribute(U,2));if(Cc)mg.setAttribute('color',new THREE.BufferAttribute(Cc,3));mg.computeBoundingSphere();
    const mesh=new THREE.Mesh(mg,mat);mesh.castShadow=shadow!==false;mesh.receiveShadow=true;S.add(mesh);}
  return S;}
const UP=new THREE.Vector3(0,1,0);
function limb(geo,mat,a,b,parent){const A=new THREE.Vector3(a[0],a[1],a[2]),B=new THREE.Vector3(b[0],b[1],b[2]),d=B.clone().sub(A);const m=new THREE.Mesh(geo,mat);m.position.copy(A).add(B).multiplyScalar(.5);m.scale.y=d.length();m.quaternion.setFromUnitVectors(UP,d.normalize());parent.add(m);return m;}
function P3(geo,mat,x,y,z,parent){const m=new THREE.Mesh(geo,mat);m.position.set(x||0,y||0,z||0);parent.add(m);m.castShadow=true;m.receiveShadow=true;return m;}

/* ================= KART MODELS ================= */
const KG={};
(function(){
  const prof=new THREE.Shape();prof.moveTo(-4,.9);prof.lineTo(4.4,.9);prof.lineTo(4.95,1.45);prof.quadraticCurveTo(3.6,2.35,1.6,2.5);prof.lineTo(-1,2.7);prof.lineTo(-3.6,2.95);prof.lineTo(-4.25,2.2);prof.closePath();
  KG.body=new THREE.ExtrudeGeometry(prof,{depth:3.6,bevelEnabled:true,bevelThickness:.4,bevelSize:.35,bevelSegments:5,curveSegments:16});KG.body.translate(0,0,-1.8);
  KG.stripe=new THREE.ExtrudeGeometry(prof,{depth:.7,bevelEnabled:true,bevelThickness:.42,bevelSize:.39,bevelSegments:5,curveSegments:16});KG.stripe.translate(0,0,-.35);
  KG.pan=new THREE.BoxGeometry(9.4,.4,5.3);KG.pod=new THREE.CapsuleGeometry(.58,3.4,8,16);KG.bumper=new THREE.CapsuleGeometry(.42,5.4,8,16);
  KG.grille=new THREE.BoxGeometry(.25,.62,2.3);KG.bar=new THREE.BoxGeometry(.3,.08,2.2);
  KG.post=new THREE.BoxGeometry(.28,1.7,.28);KG.wing=new THREE.BoxGeometry(1.9,.22,5.9);KG.wingEnd=new THREE.BoxGeometry(2.1,1.2,.18);
  KG.engine=new THREE.BoxGeometry(1.8,1.2,2.6);KG.fin=new THREE.BoxGeometry(1.6,.1,2.7);KG.scoop=new THREE.BoxGeometry(1.3,.7,1.1);
  KG.pipe=new THREE.CylinderGeometry(.32,.42,1.9,18,1,true);KG.pipeIn=new THREE.CircleGeometry(.31,18);KG.pipeRing=new THREE.TorusGeometry(.4,.07,8,18);
  KG.seat=new THREE.BoxGeometry(1.1,2.3,2.8);KG.headrest=new THREE.CapsuleGeometry(.45,1.3,6,12);
  KG.stalk=new THREE.CylinderGeometry(.07,.07,1,6);KG.mirror=new THREE.BoxGeometry(.28,.48,.75);KG.glassM=new THREE.BoxGeometry(.05,.38,.62);
  KG.steer=new THREE.TorusGeometry(.65,.13,10,24);KG.col=new THREE.CylinderGeometry(.12,.12,1,8);
  KG.light=new THREE.CylinderGeometry(.38,.38,.25,18);KG.bezel=new THREE.TorusGeometry(.42,.07,8,20);KG.tail=new THREE.BoxGeometry(.16,.36,.95);
  KG.axle=new THREE.CylinderGeometry(.16,.16,5.6,10);KG.spring=new THREE.TorusGeometry(.28,.06,6,14);KG.rod=new THREE.CylinderGeometry(.07,.07,1,6);
  const tp=[[.72,-.72],[1.1,-.72],[1.26,-.62],[1.32,-.35],[1.32,.35],[1.26,.62],[1.1,.72],[.72,.72]].map(([x,y])=>new THREE.Vector2(x,y));
  KG.tire=new THREE.LatheGeometry(tp,36);KG.tread=new THREE.TorusGeometry(1.3,.05,4,36);
  KG.rim=new THREE.CylinderGeometry(.74,.74,1.2,28);KG.spoke=new THREE.BoxGeometry(.16,.62,.14);KG.hub=new THREE.CylinderGeometry(.22,.26,1.48,14);KG.disc=new THREE.CylinderGeometry(.62,.62,.1,24);
  const sl=new THREE.Shape();sl.moveTo(-2.4,0);sl.lineTo(2.4,0);sl.lineTo(.18,6.1);sl.quadraticCurveTo(0,6.45,-.18,6.1);sl.closePath();
  KG.slice=new THREE.ExtrudeGeometry(sl,{depth:.9,bevelEnabled:true,bevelThickness:.3,bevelSize:.3,bevelSegments:4,curveSegments:10});KG.slice.translate(0,0,-.45);
  KG.crust=new THREE.CapsuleGeometry(.85,4.6,10,20);KG.eye=new THREE.SphereGeometry(.56,24,16);KG.iris=new THREE.SphereGeometry(.34,18,12);KG.pupil=new THREE.SphereGeometry(.19,14,10);KG.shine=new THREE.SphereGeometry(.09,8,6);
  KG.brow=new THREE.CapsuleGeometry(.08,.5,4,8);KG.smile=new THREE.TorusGeometry(.5,.11,8,18,Math.PI);KG.cheek=new THREE.SphereGeometry(.3,14,10);
  KG.gogRim=new THREE.TorusGeometry(.36,.1,8,22);KG.gogLens=new THREE.CircleGeometry(.33,22);KG.band=new THREE.BoxGeometry(2.3,.3,.14);KG.leaf=new THREE.SphereGeometry(1,16,10);
  KG.topD=new THREE.CylinderGeometry(.55,.55,.22,18);KG.glove=new THREE.SphereGeometry(.42,16,12);KG.arm=new THREE.CylinderGeometry(.2,.2,1,10);KG.drip=new THREE.SphereGeometry(.35,12,10);
  KG.plate=new THREE.PlaneGeometry(1.8,1.8);KG.loWheel=new THREE.CylinderGeometry(1.32,1.32,1.4,10);KG.bubble=new THREE.SphereGeometry(6.4,28,18);KG.flame=new THREE.ConeGeometry(.55,2.6,16,1,true);KG.flameIn=new THREE.ConeGeometry(.3,1.7,12,1,true);
})();
const SH={rubber:new THREE.MeshStandardMaterial({color:'#1a1514',roughness:.88}),chrome:new THREE.MeshStandardMaterial({color:'#eeeeee',metalness:1,roughness:.14}),
  metal:new THREE.MeshStandardMaterial({color:'#5a524c',metalness:.7,roughness:.35}),carbon:new THREE.MeshStandardMaterial({color:'#211e1d',roughness:.45,metalness:.2}),
  seat:new THREE.MeshStandardMaterial({color:'#2a1c18',roughness:.65}),cheese:new THREE.MeshStandardMaterial({color:'#f6c548',roughness:.38}),
  drip:new THREE.MeshStandardMaterial({color:'#f9d76a',roughness:.3}),crust:new THREE.MeshStandardMaterial({map:crustT,roughness:.72}),
  white:new THREE.MeshStandardMaterial({color:'#ffffff',roughness:.18}),black:new THREE.MeshStandardMaterial({color:'#0e0e0e',roughness:.15}),
  cheek:new THREE.MeshStandardMaterial({color:'#ff8f7a',roughness:.6}),basil:new THREE.MeshStandardMaterial({color:'#3f9a35',roughness:.45}),
  lens:new THREE.MeshStandardMaterial({color:'#7fd6ff',metalness:.9,roughness:.06}),band:new THREE.MeshStandardMaterial({color:'#2a1c18',roughness:.55}),
  light:new THREE.MeshStandardMaterial({color:'#fff6d8',emissive:'#fff0c0',emissiveIntensity:1.6}),glove:new THREE.MeshStandardMaterial({color:'#fff4dc',roughness:.55}),
  disc:new THREE.MeshStandardMaterial({color:'#8a8a90',metalness:.8,roughness:.3})};
const SHSET=new Set(Object.values(SH));
const bubbleMat=bubbleShader('#6fe06a','#eaffd8'),bubRushMat=bubbleShader('#ff8a1f','#ffe39a');
const flameMat=new THREE.MeshBasicMaterial({color:'#ff7a1a',transparent:true,opacity:.85,depthWrite:false,blending:THREE.AdditiveBlending,toneMapped:false});
const flameInMat=new THREE.MeshBasicMaterial({color:'#fff0a0',transparent:true,opacity:.95,depthWrite:false,blending:THREE.AdditiveBlending,toneMapped:false});
function plateTex(n,col){const c=cnv(128,128),g=c.getContext('2d');g.fillStyle='#fff4dc';g.beginPath();g.arc(64,64,60,0,7);g.fill();g.strokeStyle=col;g.lineWidth=8;g.stroke();g.fillStyle='#1b0f0b';g.font='bold 72px "Arial Black",Impact,sans-serif';g.textAlign='center';g.textBaseline='middle';g.fillText(n,64,70);return T2(c);}
/* ---------- kart parts: stats are [speed, accel, handling, weight, off-road] ---------- */
const STAT_NAMES=['Speed','Accel','Handling','Weight','Off-road'],STAT_SHORT=['SPD','ACC','HND','WGT','OFF'];
const BODIES=[
  {id:'classic',name:'Classic',desc:'The neutral kart. No strengths, no drawbacks.',st:[0,0,0,0,0]},
  {id:'hyper',sf:1.15,name:'Hypercar',desc:'A low electric hypercar concept. Huge pace, fragile off the road.',st:[2,1,0,-1,-2]},
  {id:'monster',name:'Monster Truck',desc:'A 1960s muscle coupe on giant tires. Huge, heavy and great in the cheese. Turns like a bus.',st:[-1,-1,-2,2,2]},
  {id:'rocket',name:'Rocket',desc:'Snappy thrusters and sharp turning. Light and easy to bump.',st:[0,2,1,-2,-1]},
  {id:'roadster',sf:1.42,name:'Roadster',desc:'A little 1950s open two-seater. Light and nimble, modest top speed.',st:[-1,1,2,-2,0]},
  {id:'oven',name:'Brick Oven',desc:'A rolling wood-fired oven. Heavy hitter with a high top speed, slow to build up.',st:[1,-2,-1,2,0]},
  {id:'formula',name:'Formula',desc:'An open-wheel race car. Blistering on smooth road, light, and lost in the cheese.',st:[2,1,1,-2,-2]},
  {id:'gt',sf:1.08,name:'GT Racer',desc:'A roofless GT race car with a roll cage. Quick and planted, but hates going off-road.',st:[1,1,0,0,-2]},
  {id:'tourer',sf:1.02,name:'Vintage Tourer',desc:'A grand 1930s saloon on spoked wheels. Heavy and steady, slow to get going.',st:[0,-2,-1,2,1]},
  {id:'concept',sf:1.06,name:'Concept',desc:'A sharp-edged future supercar. Explosive launch, hates the cheese.',st:[1,2,0,-1,-2]},
  {id:'interceptor',sf:1.14,name:'Interceptor',desc:'A pursuit hypercar with a flashing light bar. Top speed for days, heavy in the turns.',st:[2,0,-1,1,-2]},
  {id:'muscle',sf:1.1,name:'Muscle Car',desc:'A modern V8 muscle coupe. Brutal launch, a handful in the corners.',st:[1,1,-1,1,-2]},
  {id:'gokart',name:'Go-Kart',desc:'A real racing kart: low, light and razor sharp in the turns.',st:[0,1,2,-2,-1]},
  {id:'chariot',name:'Chariot',desc:'A steampunk chariot with brass trumpets. Heavy hitter, slow to turn.',st:[1,-1,-1,2,-1]},
  {id:'hatch',sf:1.16,name:'Sport Sedan',desc:'A sharp little street sedan. Darts through the turns, quick off the line.',st:[0,1,2,-1,0]},
  {id:'suv',sf:1.02,name:'Luxury SUV',desc:'A huge chrome-trimmed land yacht. Heavy, unbothered by the rough stuff.',st:[-1,-1,-1,2,2]},
  {id:'coupe',sf:1.08,name:'Grand Coupe',desc:'A long-legged luxury grand tourer. Fast and stable, but not a fan of the dirt.',st:[1,0,0,1,-1]},
  {id:'scissor',sf:1.08,name:'Scissor',desc:'A wedge-shaped V12 supercar with doors that open upward. Savage pace, fragile off the road.',st:[2,1,-1,0,-2]}];
const WHEELS=[
  {id:'standard',name:'Standard',desc:'Neutral all-round tires.',st:[0,0,0,0,0],r:1,wz:1},
  {id:'slick',name:'Slicks',desc:'Smooth racing rubber. Faster, slides in the cheese.',st:[1,0,0,0,-1],r:1,wz:1.25},
  {id:'monster',name:'Monster',desc:'The monster truck\u2019s giant off-road tires lift the whole ride.',st:[-1,0,-1,1,1],r:1.5,wz:1.35,pack:'monster',g:'w3'},
  {id:'hover',name:'Hover',desc:'Glowing discs. Nimble and quick, but light.',st:[0,1,1,-1,-1],r:.88,wz:.7},
  {id:'pepperoni',name:'Pepperoni',desc:'Spicy slices. Quick off the line, lower top speed.',st:[-1,1,0,0,0],r:1.05,wz:1},
  {id:'redline',name:'Redline',desc:'Red split-spoke race rims with carbon inserts.',st:[1,0,1,-1,-1],r:1.02,wz:.92,pack:'wheelset',g:'w0'},
  {id:'emerald',name:'Emerald',desc:'Polished mesh rims with green pinstripes. Light and quick to spin up.',st:[0,1,0,-1,0],r:1,wz:.92,pack:'wheelset',g:'w1'},
  {id:'stealth',name:'Stealth',desc:'Gunmetal mesh rims with green caps. Grippy in the turns.',st:[-1,0,2,0,-1],r:1,wz:.92,pack:'wheelset',g:'w2'},
  {id:'forged',name:'Forged Bronze',desc:'Heavy forged bronze spokes. Planted, slow to spin up.',st:[0,-1,1,1,-1],r:1.04,wz:.95,pack:'wheelset',g:'w3'},
  {id:'turbo',name:'Turbo Fan',desc:'Blue turbofan rims built for top speed.',st:[1,-1,0,0,0],r:1.02,wz:1,pack:'wheelset',g:'w4'}];
const GLIDERS=[
  {id:'chute',name:'Parachute',desc:'Neutral, steady glide.',st:[0,0,0,0,0],sink:15,air:1},
  {id:'wing',name:'Slice Wing',desc:'Fast in the air, sinks quicker.',st:[1,-1,0,0,0],sink:19,air:1.06},
  {id:'leaf',name:'Basil Leaf',desc:'Floats longest. Very light.',st:[0,1,0,-1,0],sink:11,air:.97},
  {id:'box',name:'Pizza Box',desc:'Sturdy cardboard. Heavier, a bit stiff.',st:[0,0,-1,1,0],sink:16,air:1},
  {id:'para',name:'Parafoil',desc:'A ram-air wing with open cells. Fast and stable.',st:[1,0,0,0,-1],sink:16,air:1.04},
  {id:'hang',name:'Hang Glider',desc:'A taut delta wing on an aluminium frame. Glides far.',st:[0,0,1,-1,0],sink:12,air:1},
  {id:'twin',name:'Twin Canopy',desc:'Two small chutes. Very steady, a touch slow.',st:[-1,1,0,0,1],sink:13,air:.98},
  {id:'balloon',name:'Dough Balloon',desc:'A puffed-up dough balloon. Floats forever, drifts slowly.',st:[-1,0,0,1,1],sink:9,air:.95},
  {id:'umbrella',name:'Patio Umbrella',desc:'The pizzeria terrace umbrella. Quick to open.',st:[0,1,0,0,0],sink:15,air:1}];
const PAINTS=[null,'#e0452c','#ff8a1f','#f6c548','#3f9a35','#2f7fd8','#7b4bd8','#ff6fae','#2a2626','#f3ead8'];
const PAINT_NAMES=['Driver color','Tomato','Orange','Cheddar','Basil','Ocean','Grape','Bubblegum','Charcoal','Cream'];
function sumStats(b){const o=[0,0,0,0,0];for(const p of [BODIES[b.b],WHEELS[b.w],GLIDERS[b.g]])for(let i=0;i<5;i++)o[i]+=p.st[i];return o;}
let statsOn=store.get('crust-stats')!=='0';
function statMods(b){const s=statsOn?sumStats(b):[0,0,0,0,0];return {spd:1+.028*s[0],acc:Math.max(.55,1+.12*s[1]),hnd:1+.065*s[2],wgt:1+.16*s[3],off:s[4]};}
function validBuild(b){return b&&BODIES[b.b]&&WHEELS[b.w]&&GLIDERS[b.g]&&b.p>=0&&b.p<PAINTS.length;}
let playerBuild=(()=>{try{const b=JSON.parse(store.get('crust-build')||'null');if(validBuild(b))return b;}catch(e){}return {b:0,w:0,g:0,p:0};})();
function randomBuild(){const r=n=>Math.floor(Math.random()*n),b=r(BODIES.length),lv=liveriesFor(BODIES[b].id);return {b,w:Math.random()<.35?0:r(WHEELS.length),g:r(GLIDERS.length),p:Math.random()<.65?0:1+r(PAINTS.length-1),t:Math.random()<.45?lv[r(lv.length)].id:''};}
let cpuBuilds=null;

/* ---------- kart geometry ---------- */
KG.tube=new THREE.CylinderGeometry(.14,.14,1,8);KG.shock=new THREE.CylinderGeometry(.24,.24,1,8);KG.knob=new THREE.BoxGeometry(.32,.5,1.25);KG.bolt=new THREE.CylinderGeometry(.09,.09,.2,6);
KG.hoverDisc=new THREE.CylinderGeometry(1.25,1.25,.5,32);KG.hoverRing=new THREE.TorusGeometry(1.1,.13,8,32);KG.vane=new THREE.BoxGeometry(.2,1.9,.6);
KG.pepWheel=new THREE.CylinderGeometry(1.3,1.3,1.15,32);KG.pepSpot=new THREE.CylinderGeometry(.2,.2,.04,10);KG.pepCrust=new THREE.TorusGeometry(1.3,.2,8,32);
KG.slickRing=new THREE.TorusGeometry(1.0,.06,6,32);KG.light2=new THREE.SphereGeometry(.32,12,8);
const KGSET=new Set(Object.values(KG));
Object.assign(SH,{glowC:new THREE.MeshBasicMaterial({color:'#7fe8ff',toneMapped:false}),glowO:new THREE.MeshBasicMaterial({color:'#ffae3a',toneMapped:false}),
  glass:new THREE.MeshStandardMaterial({color:'#bfeaff',roughness:.05,metalness:.1,transparent:true,opacity:.28,depthWrite:false}),
  pep:new THREE.MeshStandardMaterial({color:'#b8311c',roughness:.5}),pepFat:new THREE.MeshStandardMaterial({color:'#e8836a',roughness:.45}),
  card:new THREE.MeshStandardMaterial({color:'#c9a06a',roughness:.8}),cardIn:new THREE.MeshStandardMaterial({color:'#e8d2a8',roughness:.85}),rope:new THREE.MeshStandardMaterial({color:'#3a2a20',roughness:.8}),carLight:new THREE.MeshPhysicalMaterial({color:'#dfe6ea',emissive:'#fff2d6',emissiveIntensity:.35,roughness:.06,metalness:.2,clearcoat:1}),carGlass:new THREE.MeshPhysicalMaterial({color:'#2c3742',roughness:.04,metalness:0,clearcoat:1,transparent:true,opacity:.18,depthWrite:false,envMapIntensity:.8}),kvc:new THREE.MeshStandardMaterial({vertexColors:true,roughness:.4,metalness:.2})});
SHSET.clear();Object.values(SH).forEach(m=>SHSET.add(m));
const brickT=(()=>{const c=cnv(256,256),g=c.getContext('2d');g.fillStyle='#d9cfc2';g.fillRect(0,0,256,256);for(let r=0;r<8;r++)for(let i=-1;i<5;i++){const x=i*64+(r%2?32:0);g.fillStyle=['#b8462c','#a63c25','#c55234','#9a3520'][(r*7+i*3+16)%4];g.fillRect(x+3,r*32+3,58,26);}return T2(c,3,2);})();
const extr=(pts,depth,bev)=>{const s=new THREE.Shape();s.moveTo(pts[0][0],pts[0][1]);for(let i=1;i<pts.length;i++)s.lineTo(pts[i][0],pts[i][1]);s.closePath();
  const g=new THREE.ExtrudeGeometry(s,{depth,bevelEnabled:bev>0,bevelThickness:bev,bevelSize:bev,bevelSegments:3,curveSegments:8});g.translate(0,0,-depth/2);return g;};
const hrz=(m)=>{m.rotation.z=Math.PI/2;return m;},hrx=(m)=>{m.rotation.x=Math.PI/2;return m;};
const SHADOW_ONLY=new THREE.MeshBasicMaterial({colorWrite:false,depthWrite:false});SHSET.add(SHADOW_ONLY);
const PWG=new Map();let _wVC=null;const wheelVC=()=>{if(!_wVC){_wVC=SH.carVC.clone();_wVC.side=THREE.DoubleSide;SHSET.add(_wVC);}return _wVC;};
function packWheelGeo(pack,g,side){const key=pack+'|'+g+'|'+side;let geo=PWG.get(key);if(geo)return geo;const src=carGeos(pack)[g];geo=src.clone();
  geo.computeBoundingBox();const bb=geo.boundingBox,c=bb.getCenter(new THREE.Vector3()),r=(bb.max.y-bb.min.y)/2,w=bb.max.z-bb.min.z;
  // a right-hand wheel faces +z; car packs keep each wheel's own facing
  const hw=CAR_PACKS[pack].h.wheels,wi=+g.slice(1),fz=hw&&hw[wi]?Math.sign(hw[wi].c[2])||1:1;geo.translate(-c.x,-c.y,-c.z);geo.scale(1.32/r,1.32/r,1.44/w*fz*side);
  if(fz*side<0){const ix=geo.index.array;for(let i=0;i<ix.length;i+=3){const t=ix[i+1];ix[i+1]=ix[i+2];ix[i+2]=t;}}
  geo.computeBoundingSphere();CARGEO.add(geo);PWG.set(key,geo);return geo;}
let _pepF=null,_pepM=null;
function pepFace(){if(_pepF)return _pepF;const g=new THREE.CircleGeometry(1.18,56,0,Math.PI*2);const p=g.attributes.position;
  for(let i=0;i<p.count;i++){const r=Math.hypot(p.getX(i),p.getY(i))/1.18;p.setZ(i,.02+.07*Math.pow(r,3)-.03*(1-r)*(1-r));}g.computeVertexNormals();KGSET.add(g);return _pepF=g;}
function pepFaceMat(){if(_pepM)return _pepM;const S=512,c=cnv(S,S),g=c.getContext('2d'),r=prng(91);
  const gr=g.createRadialGradient(S/2,S/2,0,S/2,S/2,S/2);gr.addColorStop(0,'#c23a22');gr.addColorStop(.78,'#a82c18');gr.addColorStop(.93,'#7e1e10');gr.addColorStop(1,'#4a120a');g.fillStyle=gr;g.beginPath();g.arc(S/2,S/2,S/2,0,7);g.fill();
  for(let i=0;i<260;i++){const a=r()*6.283,d=Math.sqrt(r())*S*.42,x=S/2+Math.cos(a)*d,y=S/2+Math.sin(a)*d,rr=2+r()*r()*14;g.fillStyle=`rgba(${232+r()*20|0},${150+r()*40|0},${120+r()*30|0},${.55+r()*.35})`;g.beginPath();g.ellipse(x,y,rr,rr*(.6+r()*.4),r()*3,0,7);g.fill();}
  for(let i=0;i<1600;i++){const a=r()*6.283,d=Math.sqrt(r())*S*.47;g.fillStyle=r()<.5?'rgba(90,16,8,.35)':'rgba(255,170,140,.18)';g.fillRect(S/2+Math.cos(a)*d,S/2+Math.sin(a)*d,1.5,1.5);}
  for(let i=0;i<40;i++){const a=r()*6.283,d=S*(.3+r()*.15);g.fillStyle='rgba(40,8,4,.35)';g.beginPath();g.arc(S/2+Math.cos(a)*d,S/2+Math.sin(a)*d,1+r()*3,0,7);g.fill();}
  _pepM=new THREE.MeshPhysicalMaterial({map:T2(c),roughness:.42,clearcoat:.6,clearcoatRoughness:.25,sheen:.3,sheenColor:new THREE.Color('#ffb08a')});_pepM.map.userData.shared=true;SHSET.add(_pepM);return _pepM;}
function buildWheel(type,side,M){const wd=WHEELS.find(w=>w.id===type);if(wd&&wd.pack){const m=new THREE.Mesh(packWheelGeo(wd.pack,wd.g,side),wd.pack==='wheelset'?wheelVC():SH.carVC);m.castShadow=false;return m;}
  const W=new THREE.Group();
  if(type==='hover'){hrx(P3(KG.hoverDisc,SH.carbon,0,0,0,W));for(const s of [-1,1])P3(KG.hoverRing,SH.glowC,0,0,s*.27,W);
    for(let i=0;i<3;i++){const v=P3(KG.vane,M.paint,0,0,side*.28,W);v.rotation.z=i*Math.PI/3;}hrx(P3(KG.hub,SH.chrome,0,0,0,W)).scale.set(1,.5,1);}
  else if(type==='pepperoni'){hrx(P3(KG.tire,SH.rubber,0,0,0,W));for(const s of [-1,1])P3(KG.tread,SH.rubber,0,0,s*.36,W).scale.set(1.005,1.005,1);
    for(const s of [-1,1]){const f=P3(pepFace(),pepFaceMat(),0,0,s*.7,W);if(s<0)f.rotation.y=Math.PI;}hrx(P3(KG.hub,SH.chrome,0,0,0,W)).scale.set(.7,1.02,.7);}
  else{const t=hrx(P3(KG.tire,SH.rubber,0,0,0,W));
    if(type==='standard'){for(const s of [-1,1])P3(KG.tread,SH.rubber,0,0,s*.36,W).scale.set(1.005,1.005,1);hrx(P3(KG.rim,M.dark,0,0,0,W));
      for(let i=0;i<5;i++){const a=i*Math.PI*2/5,sp=P3(KG.spoke,M.paint,Math.cos(a)*.36,Math.sin(a)*.36,side*.58,W);sp.rotation.z=a-Math.PI/2;}}
    else if(type==='slick'){P3(KG.slickRing,M.stripe,0,0,side*.66,W);hrx(P3(KG.rim,SH.chrome,0,0,0,W));
      for(let i=0;i<6;i++){const a=i*Math.PI/3,sp=P3(KG.spoke,SH.metal,Math.cos(a)*.36,Math.sin(a)*.36,side*.58,W);sp.rotation.z=a-Math.PI/2;sp.scale.set(.6,1,1);}}
    else if(type==='monster'){for(let i=0;i<18;i++){const a=i/18*Math.PI*2,k=P3(KG.knob,SH.rubber,Math.cos(a)*1.36,Math.sin(a)*1.36,(i%2?.12:-.12),W);k.rotation.z=a;}
      hrx(P3(KG.rim,SH.black,0,0,0,W));for(let i=0;i<6;i++){const a=i*Math.PI/3;hrx(P3(KG.bolt,SH.chrome,Math.cos(a)*.45,Math.sin(a)*.45,side*.62,W));}}
    hrx(P3(KG.hub,SH.chrome,0,0,0,W));}
  if(type!=='hover')hrx(P3(KG.disc,SH.disc,0,0,-side*.5,W));
  return bake(W,true,true);}
/* ---------- driver characters: each racer is its own topping, built once and baked to a single mesh ---------- */
const CHM=new Map();const cm=(c,r,m,cc,sh)=>{const k=c+'|'+(r??.5)+'|'+(m||0)+'|'+(cc||0)+'|'+(sh||0);let v=CHM.get(k);if(!v){const o={color:c,roughness:r??.5,metalness:m||0};
  v=(cc||sh)?new THREE.MeshPhysicalMaterial(Object.assign(o,{clearcoat:cc||0,clearcoatRoughness:.08,sheen:sh||0,sheenRoughness:.5,sheenColor:new THREE.Color('#ffffff')})):new THREE.MeshStandardMaterial(o);CHM.set(k,v);SHSET.add(v);}return v;};
const cvm=(r,m,cc,sh)=>{const k='VC|'+r+'|'+(m||0)+'|'+(cc||0)+'|'+(sh||0);let v=CHM.get(k);if(!v){v=new THREE.MeshPhysicalMaterial({vertexColors:true,roughness:r,metalness:m||0,clearcoat:cc||0,clearcoatRoughness:.1,sheen:sh||0,sheenRoughness:.5,sheenColor:new THREE.Color('#ffffff')});CHM.set(k,v);SHSET.add(v);}return v;};
const CG={sph:new THREE.SphereGeometry(1,44,30),sphM:new THREE.SphereGeometry(1,24,16),sphS:new THREE.SphereGeometry(1,14,10),cyl:new THREE.CylinderGeometry(1,1,1,32),cone:new THREE.ConeGeometry(1,1,20),
  tor:new THREE.TorusGeometry(1,.12,14,64),half:new THREE.TorusGeometry(1,.16,12,32,Math.PI),cap:new THREE.CapsuleGeometry(.5,1,10,18),disc:new THREE.CircleGeometry(1,32),hemi:new THREE.SphereGeometry(1,40,18,0,Math.PI*2,0,Math.PI/2),
  oct:new THREE.OctahedronGeometry(1,0),box:new THREE.BoxGeometry(1,1,1),halfDisc:new THREE.CircleGeometry(1,24,Math.PI,Math.PI),arc:new THREE.TorusGeometry(1,.07,8,24,Math.PI*.8)};
for(const g of Object.values(CG))KGSET.add(g);
function M3(geo,mat,p,s,r,parent){const m=new THREE.Mesh(geo,mat);m.position.set(p[0],p[1],p[2]);if(s!=null)Array.isArray(s)?m.scale.set(s[0],s[1],s[2]):m.scale.setScalar(s);if(r)m.rotation.set(r[0],r[1],r[2]);parent.add(m);return m;}
const hsh=(x,y,z)=>{const s=Math.sin(x*12.9898+y*78.233+z*37.719)*43758.5453;return s-Math.floor(s);};
const vn=(x,y,z)=>{const xi=Math.floor(x),yi=Math.floor(y),zi=Math.floor(z),xf=x-xi,yf=y-yi,zf=z-zi,u=xf*xf*(3-2*xf),v=yf*yf*(3-2*yf),w=zf*zf*(3-2*zf);
  const L=(a,b,t)=>a+(b-a)*t;return L(L(L(hsh(xi,yi,zi),hsh(xi+1,yi,zi),u),L(hsh(xi,yi+1,zi),hsh(xi+1,yi+1,zi),u),v),L(L(hsh(xi,yi,zi+1),hsh(xi+1,yi,zi+1),u),L(hsh(xi,yi+1,zi+1),hsh(xi+1,yi+1,zi+1),u),v),w);};
function paintV(geo,fn){const p=geo.attributes.position,c=new Float32Array(p.count*3),col=new THREE.Color();for(let i=0;i<p.count;i++){fn(p.getX(i),p.getY(i),p.getZ(i),col);c[i*3]=col.r;c[i*3+1]=col.g;c[i*3+2]=col.b;}geo.setAttribute('color',new THREE.BufferAttribute(c,3));return geo;}
function bumpV(geo,fn){const p=geo.attributes.position,v=new THREE.Vector3(),n=new THREE.Vector3();geo.computeVertexNormals();const nr=geo.attributes.normal;
  for(let i=0;i<p.count;i++){v.fromBufferAttribute(p,i);n.fromBufferAttribute(nr,i);const d=fn(v.x,v.y,v.z);p.setXYZ(i,v.x+n.x*d,v.y+n.y*d,v.z+n.z*d);}geo.computeVertexNormals();return geo;}
const C3=c=>new THREE.Color(c);
/* expressive face: glossy eyes with iris rings, pupils and two catch-lights, lids, brows, open smile with teeth and tongue, blush. Faces +z. */
function faceKit(D,o){const {y,z,s=1,sp=.62,iris,mood='happy',lid,lash}=o,W=cm('#fdfbf7',.12,0,1),K=cm('#100c0c',.25),I=cm(iris,.12,0,1),IR=cm(shade(iris,-.45),.3),Ck=cm('#ff8f7a',.7),Lid=cm(lid||'#2a1a14',.5);
  for(const sd of [-1,1]){const x=sp*s*sd;M3(CG.sph,W,[x,y,z],[.5*s,.58*s,.38*s],null,D);
    M3(CG.sphM,IR,[x,y-.02*s,z+.25*s],[.32*s,.36*s,.16*s],null,D);M3(CG.sphM,I,[x,y-.02*s,z+.27*s],[.29*s,.33*s,.16*s],null,D);M3(CG.sphS,K,[x,y-.03*s,z+.39*s],[.15*s,.18*s,.06*s],null,D);
    M3(CG.sphS,cm('#ffffff',.05),[x+.11*s,y+.13*s,z+.45*s],.08*s,null,D);M3(CG.sphS,cm('#ffffff',.05),[x-.08*s,y-.12*s,z+.44*s],.04*s,null,D);
    M3(CG.arc,Lid,[x,y+.02*s,z+.2*s],[.52*s,.6*s,.9*s],[0,0,Math.PI*.1],D);
    if(lash)for(let k=0;k<3;k++){const a=Math.PI*(.62+k*.12)*(sd<0?1:1),lx=x+Math.cos(Math.PI-a*sd)*.5*s*sd,ly=y+Math.sin(a)*.58*s;M3(CG.cone,K,[lx,ly+.06*s,z+.22*s],[.05*s,.22*s,.05*s],[0,0,(sd*(.5-k*.4))],D);}
    const tilt=mood==='angry'?-.45:mood==='cool'?-.15:.22;M3(CG.cap,cm(lid||'#1a1210',.45),[x,y+.66*s,z+.25*s],[.16*s,.52*s,.14*s],[0,0,Math.PI/2+tilt*sd],D);
    M3(CG.sphM,Ck,[x*1.55,y-.62*s,z-.05*s],[.3*s,.18*s,.1*s],null,D);}
  if(mood==='angry'){M3(CG.half,K,[0,y-1.02*s,z+.12*s],[.3*s,.18*s,.5*s],null,D);M3(CG.box,cm('#fdfbf7',.2),[0,y-1.0*s,z+.16*s],[.42*s,.08*s,.05*s],null,D);}
  else{const mo=new THREE.Group();mo.position.set(0,y-.86*s,z+.14*s);D.add(mo);M3(CG.halfDisc,cm('#5a1410',.6),[0,0,0],[.38*s,.32*s,1],null,mo);M3(CG.half,K,[0,0,.01],[.38*s,.32*s,.5*s],[0,0,Math.PI],mo);
    M3(CG.box,cm('#fdfbf7',.25),[0,-.05*s,.02],[.46*s,.09*s,.04*s],null,mo);M3(CG.sphS,cm('#e0505a',.5),[0,-.22*s,.02],[.16*s,.08*s,.05*s],null,mo);}}
function goggles(D,y,z,s,band,rx){const R=cm('#3a2a22',.4,.3),Rm=cm('#c9ccd2',.2,1),L=cm('#7fd6ff',.04,.6,1);const g=new THREE.Group();g.position.set(0,y,z);g.rotation.x=rx||0;D.add(g);
  for(const sd of [-1,1]){M3(CG.tor,R,[.45*s*sd,0,0],[.38*s,.38*s,1.1*s],null,g);M3(CG.tor,Rm,[.45*s*sd,0,.04*s],[.33*s,.33*s,.5*s],null,g);M3(CG.disc,L,[.45*s*sd,0,.05*s],.32*s,null,g);
    M3(CG.sphS,cm('#ffffff',.05),[.45*s*sd+.1*s,.12*s,.09*s],[.07*s,.05*s,.02*s],null,g);}
  M3(CG.box,cm(band,.55),[0,0,-.08*s],[2.15*s,.28*s,.12*s],null,g);M3(CG.box,R,[0,0,.02*s],[.18*s,.16*s,.1*s],null,g);return g;}
function pepGeo(){return paintV(new THREE.LatheGeometry([[0,.14],[.6,.16],[.86,.2],[1,.14],[1.02,0],[.96,-.1],[0,-.1]].map(([r,y])=>new THREE.Vector2(r,y)),28),(x,y,z,c)=>{const r=Math.hypot(x,z),n=vn(x*5,y*5,z*5);c.copy(C3('#b3241a')).lerp(C3('#d24a30'),n*.6);if(r>.82)c.lerp(C3('#5e1009'),(r-.82)*4);if(n>.72&&r<.75)c.lerp(C3('#f0a088'),.7);});}
const CHAR_FN={
  pep(D,rc,topM){const slice=paintV(bumpV(KG.slice.clone(),(x,y,z)=>z>.4?(vn(x*2.2,y*2.2,1)-.5)*.12:0),(x,y,z,c)=>{const n=vn(x*1.6,y*1.6,z);c.copy(C3('#f6c548')).lerp(C3('#ffe08a'),n*.7);if(n<.3)c.lerp(C3('#e0a52e'),.6);});
    M3(slice,cvm(.32,0,.6),[0,0,0],1,null,D);
    const cr=paintV(bumpV(KG.crust.clone(),(x,y,z)=>(vn(x*3,y*3,z*3)-.5)*.1),(x,y,z,c)=>{const n=vn(x*4,y*4,z*4);c.copy(C3('#c27a34')).lerp(C3('#8a4b1c'),n*.8);if(y>.5)c.lerp(C3('#e0a35a'),.4);if(hsh(Math.round(x*9),Math.round(y*9),Math.round(z*9))>.93)c.set('#f6e7c4');});
    M3(cr,cvm(.75),[0,0,0],1,[0,0,Math.PI/2],D);
    [[-1.5,.9,.85],[0,.85,.85],[1.5,.9,-.85],[-.6,.95,-.85],[.9,.8,.86]].forEach(([x,y,z])=>{M3(CG.sphM,cm('#f9d76a',.25,0,.8),[x,y-.2,z],[.34,.62,.2],null,D);M3(CG.sphS,cm('#f9d76a',.25,0,.8),[x,y-.75,z],[.2,.24,.14],null,D);});
    const pg=pepGeo();[[-1.4,1.1,.78,.62],[1.45,1.25,.78,.62],[-1.3,1.3,-.78,.6],[1.3,1.5,-.78,.6],[0,4.25,-.78,.45],[-.3,2.6,-.78,.62]].forEach(([x,y,z,s])=>M3(pg,cvm(.35,0,.9),[x,y,z],[s,s*1.4,s],[Math.PI/2*(z>0?1:-1),0,0],D));
    for(let i=0;i<16;i++){const x=(hsh(i,1,2)-.5)*3.2,y=.9+hsh(i,3,4)*4.2;if(Math.abs(x)>2.25*(1-(y-.2)/6.2))continue;M3(CG.sphS,cm('#ffe7a8',.3,0,.6),[x,y,.62],[.16,.12,.05],null,D);}
    faceKit(D,{y:2.7,z:.55,iris:rc.iris,lash:1});goggles(D,3.82,.78,1,'#2a1c18');
    const lf=P3(KG.leaf,cm('#3f9a35',.4,0,.5),.2,6.2,0,D);lf.scale.set(.9,.25,.5);lf.rotation.z=.5;},
  basil(D,rc){const sh=new THREE.Shape();sh.moveTo(0,0);sh.bezierCurveTo(2.9,.9,3.0,4.6,0,7.0);sh.bezierCurveTo(-3.0,4.6,-2.9,.9,0,0);
    const lg=new THREE.ExtrudeGeometry(sh,{depth:.7,bevelEnabled:true,bevelThickness:.45,bevelSize:.35,bevelSegments:6,curveSegments:40,steps:1});lg.translate(0,0,-.35);
    const p=lg.attributes.position;for(let i=0;i<p.count;i++){const x=p.getX(i),y=p.getY(i);p.setZ(i,p.getZ(i)-x*x*.09+Math.sin(y*.6)*.12);}
    paintV(lg,(x,y,z,c)=>{const ax=Math.abs(x),n=vn(x*1.4,y*1.4,z);c.copy(C3('#2f8a2a')).lerp(C3('#58b44a'),Math.max(0,1-ax/2.6)*.7+n*.15);if(ax<.12)c.lerp(C3('#a8e08e'),.6);const vv=Math.abs(((y-ax*.7)%1.15+1.15)%1.15-.57);if(vv<.06&&ax>.2&&ax<2)c.lerp(C3('#8ccf74'),.5);});lg.computeVertexNormals();
    M3(lg,cvm(.36,0,.7),[0,-.2,0],1,null,D);
    M3(CG.cyl,cm('#2c7a26',.5),[0,-.15,0],[.22,.8,.22],null,D);
    faceKit(D,{y:3.45,z:.95,iris:rc.iris,s:.9});
    const band=M3(CG.tor,cm('#fff4dc',.55,0,0,.5),[0,4.85,-.05],[1.9,.8,1],[Math.PI/2,0,0],D);band.scale.set(2.06,1.0,1.5);
    M3(CG.box,cm(rc.stripe,.45),[0,4.86,.92],[1.2,.32,.08],null,D);
    for(const sd of [-1,1])M3(CG.cone,cm('#fff4dc',.55,0,0,.5),[sd*.4,4.85,-1.15],[.22,.95,.1],[-.6,0,sd*.6],D);},
  olive(D,rc){const og=paintV(bumpV(new THREE.SphereGeometry(1,64,44),(x,y,z)=>(vn(x*3,y*3,z*3)-.5)*.025),(x,y,z,c)=>{const n=vn(x*2.5,y*2.5,z*2.5);c.copy(C3('#2b2233')).lerp(C3('#4a3a5a'),n*.55);if(y<-.6)c.lerp(C3('#1c1622'),.5);});
    M3(og,cvm(.16,.1,1),[0,3.0,0],[2.45,2.95,2.2],null,D);
    const pim=paintV(bumpV(new THREE.CylinderGeometry(.95,.9,.6,40,4),(x,y,z)=>Math.max(0,Math.sin(Math.atan2(z,x)*9))*.06),(x,y,z,c)=>{c.copy(C3('#d8342a')).lerp(C3('#a8201a'),vn(x*4,y*4,z*4)*.6);});
    M3(pim,cvm(.35,0,.7),[0,5.8,0],1,null,D);M3(CG.tor,cm('#1a141f',.3,0,.8),[0,5.8,0],[1.0,1.0,2],[Math.PI/2,0,0],D);M3(CG.sphM,cm('#e04a3a',.3),[0,6.12,0],[.55,.18,.55],null,D);
    faceKit(D,{y:3.25,z:1.95,iris:rc.iris,s:1.05,mood:'cool',lid:'#1a141f'});
    const sg=new THREE.Group();sg.position.set(0,4.75,1.6);sg.rotation.x=-.55;D.add(sg);const fr=cm(rc.color,.25,.5,1),ln=cm('#141018',.04,.6,1);
    for(const sd of [-1,1]){M3(CG.tor,fr,[sd*.62,0,0],[.44,.44,1.4],null,sg);M3(CG.disc,ln,[sd*.62,0,.02],.41,null,sg);M3(CG.sphS,cm('#ffffff',.05),[sd*.62+.12,.14,.06],[.09,.05,.02],null,sg);
      M3(CG.box,fr,[sd*1.12,-.05,-.6],[.08,.08,1.2],null,sg);}M3(CG.box,fr,[0,.05,0],[.4,.09,.09],null,sg);},
  mozz(D,rc){const mg=paintV(bumpV(new THREE.SphereGeometry(1,64,44),(x,y,z)=>(vn(x*2.2,y*2.2,z*2.2)-.5)*.06+(y>.75?(y-.75)*.4:0)),(x,y,z,c)=>{const n=vn(x*3,y*3,z*3);c.copy(C3('#f9f3e6')).lerp(C3('#ece0c6'),n*.5);if(y<-.5)c.lerp(C3('#e2d3b2'),.4);});
    M3(mg,cvm(.24,0,.9,.4),[0,2.75,0],[2.55,2.6,2.35],null,D);
    const tg=paintV(new THREE.CylinderGeometry(1.55,1.55,.32,40,1),(x,y,z,c)=>{const r=Math.hypot(x,z),a=Math.atan2(z,x);c.set('#d6301e');if(r<1.3&&Math.abs(Math.sin(a*3))<.18)c.set('#f2785e');if(r>1.32)c.set('#b81e10');if(r<.35)c.set('#f2785e');});
    M3(tg,cvm(.25,0,1),[.45,5.35,-.1],1,[.18,0,-.25],D);
    for(let i=0;i<6;i++){const a=i/6*Math.PI*2+.5;M3(CG.sphS,cm('#f7d24a',.3,0,1),[.45+Math.cos(a)*.78,5.53+Math.sin(a)*.08,-.1+Math.sin(a)*.78],[.13,.05,.08],[.18,0,-.25],D);}
    const lf=new THREE.Shape();lf.moveTo(0,0);lf.bezierCurveTo(.7,.25,.7,1.25,0,1.6);lf.bezierCurveTo(-.7,1.25,-.7,.25,0,0);const lfg=new THREE.ExtrudeGeometry(lf,{depth:.06,bevelEnabled:true,bevelThickness:.04,bevelSize:.04,bevelSegments:2,curveSegments:16});
    M3(lfg,cm('#3f9a35',.35,0,.7),[-.7,5.7,.1],1,[-1.2,.4,.6],D);
    faceKit(D,{y:2.95,z:2.15,iris:rc.iris,s:1.05,lash:1});},
  chili(D,rc){const prof=[[0,0],[.25,.25],[.55,.8],[.95,1.8],[1.3,2.9],[1.55,4.0],[1.6,4.6],[1.4,5.05],[0,5.15]].map(([r,y])=>new THREE.Vector2(r,y));
    const g=new THREE.LatheGeometry(prof,48),p=g.attributes.position;for(let i=0;i<p.count;i++){const y=p.getY(i),b=Math.max(0,3.4-y);p.setZ(i,p.getZ(i)+b*b*.11);}
    bumpV(g,(x,y,z)=>(vn(x*1.8,y*1.2,z*1.8)-.5)*.09+Math.sin(Math.atan2(z,x)*3+y)*.025);paintV(g,(x,y,z,c)=>{const n=vn(x*2,y*2,z*2);c.copy(C3('#c51a12')).lerp(C3('#e8382a'),n*.7);if(y>4.6)c.lerp(C3('#8a1a10'),.4);});
    M3(g,cvm(.16,0,1),[0,.2,0],[1,1,.92],null,D);
    const gr=cm('#3b8a2c',.42,0,.4);M3(CG.sphM,gr,[0,5.3,0],[1.35,.38,1.25],null,D);for(let i=0;i<5;i++){const a=i/5*Math.PI*2;M3(CG.cone,gr,[Math.cos(a)*1.0,5.05,Math.sin(a)*1.0],[.34,.85,.18],[Math.sin(a)*1.9,0,-Math.cos(a)*1.9],D);}
    const st=new THREE.CatmullRomCurve3([new THREE.Vector3(0,5.4,0),new THREE.Vector3(.1,6.1,-.1),new THREE.Vector3(.55,6.55,-.35),new THREE.Vector3(.95,6.6,-.45)]);M3(new THREE.TubeGeometry(st,16,.2,10),gr,[0,0,0],1,null,D);
    faceKit(D,{y:3.45,z:1.35,iris:rc.iris,s:.95,sp:.6,mood:'angry',lid:'#6a0e08'});goggles(D,4.45,1.2,.95,rc.color,-.2);},
  shroom(D,rc){const sp=[[0,0],[1.55,0],[1.62,.3],[1.45,1.6],[1.35,3.0],[1.25,3.8],[0,3.8]].map(([r,y])=>new THREE.Vector2(r,y));
    const sg=paintV(bumpV(new THREE.LatheGeometry(sp,48,0,Math.PI*2),(x,y,z)=>(vn(Math.atan2(z,x)*6,y*.8,0)-.5)*.05),(x,y,z,c)=>{const n=vn(Math.atan2(z,x)*8,y*.6,1);c.copy(C3('#f3e8d2')).lerp(C3('#d9c6a6'),n*.6);if(y<.4)c.lerp(C3('#c4ad88'),.5);});
    M3(sg,cvm(.62,0,0,.5),[0,0,0],1,null,D);
    const cg=paintV(bumpV(new THREE.SphereGeometry(1,56,24,0,Math.PI*2,0,Math.PI/2),(x,y,z)=>(vn(x*3,y*3,z*3)-.5)*.04),(x,y,z,c)=>{const n=vn(x*3.5,y*3.5,z*3.5);c.copy(C3('#7a4a2a')).lerp(C3('#a8703f'),y*.8+n*.2);if(hsh(Math.round(x*7),Math.round(y*7),Math.round(z*7))>.86&&y>.25)c.lerp(C3('#d9b88c'),.65);});
    M3(cg,cvm(.42,0,.35),[0,3.55,0],[3.0,2.05,2.9],null,D);
    M3(CG.disc,cm('#c9a47c',.8),[0,3.54,0],[2.95,2.85,1],[Math.PI/2,0,0],D);for(let i=0;i<36;i++){const a=i/36*Math.PI*2;M3(CG.box,cm('#a8875c',.85),[Math.cos(a)*2.0,3.5,Math.sin(a)*1.95],[1.75,.04,.05],[0,-a,0],D);}
    M3(CG.tor,cm('#6a4024',.45,0,.3),[0,3.58,0],[2.95,2.85,1.6],[Math.PI/2,0,0],D);M3(CG.tor,cm('#efe3cb',.6),[0,2.95,0],[1.42,1.42,2.2],[Math.PI/2,0,0],D);
    faceKit(D,{y:2.15,z:1.38,iris:rc.iris,s:.85,sp:.6});goggles(D,4.6,2.05,1.0,rc.stripe,-.6);},
  pineapple(D,rc){const pg=paintV(bumpV(new THREE.SphereGeometry(1,60,44),(x,y,z)=>{const a=Math.atan2(z,x)*7/Math.PI,b=y*4.2;const u=a+b,v=a-b;return (Math.abs(Math.sin(u*Math.PI*.5))*Math.abs(Math.sin(v*Math.PI*.5)))*.07;}),
      (x,y,z,c)=>{const a=Math.atan2(z,x)*7/Math.PI,b=y*4.2,u=a+b,v=a-b,t=Math.abs(Math.sin(u*Math.PI*.5))*Math.abs(Math.sin(v*Math.PI*.5));c.copy(C3('#9a6418')).lerp(C3('#e8b03a'),t);if(t>.85)c.lerp(C3('#fff0a0'),.4);if(t<.12)c.set('#6a4210');});
    M3(pg,cvm(.5,0,.2),[0,2.8,0],[2.15,2.75,2.0],null,D);
    const lf=cm('#3f8a35',.4,0,.4),lf2=cm('#2f6f2a',.42,0,.4);
    for(let i=0;i<14;i++){const a=i/14*Math.PI*2,t=i%2?.6:.32,L=(i%2?1.7:2.1);const sh=new THREE.Shape();sh.moveTo(-.22,0);sh.quadraticCurveTo(-.12,L*.6,0,L);sh.quadraticCurveTo(.12,L*.6,.22,0);sh.closePath();
      const g2=new THREE.ExtrudeGeometry(sh,{depth:.05,bevelEnabled:true,bevelThickness:.03,bevelSize:.03,bevelSegments:1,curveSegments:8});M3(g2,i%2?lf:lf2,[Math.cos(a)*.3,5.45,Math.sin(a)*.3],1,[Math.sin(a)*t,-a+Math.PI/2,-Math.cos(a)*t],D);}
    M3(CG.cone,lf,[0,6.45,0],[.3,2.0,.12],null,D);
    faceKit(D,{y:3.05,z:1.85,iris:rc.iris,s:.95,lash:1});
    const sg=new THREE.Group();sg.position.set(0,4.05,1.72);sg.rotation.x=-.35;D.add(sg);const fr=cm('#ff6fae',.25,0,1),ln=cm('#141018',.04,.6,1);
    for(const sd of [-1,1]){M3(CG.box,fr,[sd*.62,0,0],[1.08,.66,.14],null,sg);M3(CG.box,ln,[sd*.62,0,.06],[.92,.52,.06],null,sg);M3(CG.box,cm('#ffffff',.05),[sd*.62-.25,.14,.1],[.22,.06,.02],[0,0,.5],sg);}M3(CG.box,fr,[0,.08,0],[.26,.1,.1],null,sg);},
  anchovy(D,rc){const bg=new THREE.SphereGeometry(1,60,44);bumpV(bg,(x,y,z)=>{const s2=Math.abs(Math.sin(x*14+y*9))*Math.abs(Math.sin(x*14-y*9));return s2*.008;});
    paintV(bg,(x,y,z,c)=>{const t=(z+1)/2,n=vn(x*6,y*6,z*6);c.copy(C3('#1f4672')).lerp(C3('#dfe7ee'),Math.min(1,Math.max(0,(t-.35)*2.2)));if(Math.abs(t-.52)<.03)c.lerp(C3('#9fd0ff'),.6);c.lerp(C3('#ffffff'),Math.max(0,n-.7)*.8);
      const sc=Math.abs(Math.sin(x*10+y*7))*Math.abs(Math.sin(x*10-y*7));if(sc<.08)c.multiplyScalar(.82);});
    M3(bg,cvm(.18,.45,1),[0,3.2,0],[1.75,3.05,1.55],null,D);
    const fin=cm('#5a86b8',.3,.2,.6);
    const finG=(w,h)=>{const sh=new THREE.Shape();sh.moveTo(0,0);sh.lineTo(w,h*.2);sh.quadraticCurveTo(w*.8,h*.7,w*.15,h);sh.closePath();return new THREE.ExtrudeGeometry(sh,{depth:.06,bevelEnabled:true,bevelThickness:.03,bevelSize:.03,bevelSegments:1});};
    for(const sd of [-1,1])M3(finG(1.6,1.4),fin,[sd*.3,.6,-.2],1,[0,sd<0?Math.PI:0,Math.PI+.25],D);
    M3(finG(1.3,2.0),fin,[0,4.2,-1.2],[1,1,1],[0,Math.PI/2,-.2],D);for(const sd of [-1,1])M3(finG(1.2,.8),fin,[sd*1.5,2.7,.4],1,[0,sd<0?Math.PI:0,.5],D);
    for(const sd of [-1,1]){M3(CG.half,cm('#9fb3c8',.25,.5),[sd*1.15,4.3,.95],[.6,.75,.6],[0,sd*.9,Math.PI/2],D);M3(CG.half,cm('#7f93a8',.25,.5),[sd*1.25,4.0,.8],[.45,.55,.45],[0,sd*.9,Math.PI/2],D);}
    faceKit(D,{y:4.55,z:1.32,iris:rc.iris,s:.9,sp:.58});
    const bd=M3(CG.tor,cm(rc.color,.5,0,0,.5),[0,5.55,-.1],[1.3,.9,1],[Math.PI/2+.15,0,0],D);bd.scale.set(1.28,1.08,1.7);
    for(let i=0;i<8;i++){const a=i/8*Math.PI*2;M3(CG.sphS,cm('#ffffff',.5),[Math.cos(a)*1.55,5.55+Math.sin(a)*.05,-.1+Math.sin(a)*1.1],.09,null,D);}
    M3(CG.cone,cm(rc.color,.5,0,0,.5),[0,5.4,-1.4],[.38,.9,.15],[2.2,0,0],D);M3(CG.cone,cm(rc.color,.5,0,0,.5),[.25,5.3,-1.45],[.3,.8,.12],[2.4,0,.4],D);}
};
/* the camera kart gets the full-detail driver; everyone else is built with roughly half the curve segments */
const LOWQ=.5;let CG_LO=null;
function lowDetail(fn){const T=THREE,q=LOWQ,r=(n,m)=>n==null?n:Math.max(m,Math.round(n*q)),O={};
  const wrap={SphereGeometry:B=>class extends B{constructor(a,w,h,...x){super(a,r(w??32,8),r(h??16,6),...x);}},CylinderGeometry:B=>class extends B{constructor(a,b,h,rs,hs,...x){super(a,b,h,r(rs??32,6),hs,...x);}},
    TorusGeometry:B=>class extends B{constructor(a,t,rs,ts,...x){super(a,t,r(rs??12,4),r(ts??48,8),...x);}},ConeGeometry:B=>class extends B{constructor(a,h,rs,...x){super(a,h,r(rs??32,6),...x);}},
    CapsuleGeometry:B=>class extends B{constructor(a,l,cs,rs){super(a,l,r(cs??4,2),r(rs??8,6));}},CircleGeometry:B=>class extends B{constructor(a,sg,...x){super(a,r(sg??32,8),...x);}},LatheGeometry:B=>class extends B{constructor(pts,sg,...x){super(pts,r(sg??12,6),...x);}}};
  if(!CG_LO){CG_LO={};for(const k in CG){const g=CG[k],p=g.parameters||{},t=g.type;let n=null;
      if(t==='SphereGeometry')n=new T.SphereGeometry(p.radius,r(p.widthSegments,8),r(p.heightSegments,6),p.phiStart,p.phiLength,p.thetaStart,p.thetaLength);
      else if(t==='CylinderGeometry')n=new T.CylinderGeometry(p.radiusTop,p.radiusBottom,p.height,r(p.radialSegments,6),p.heightSegments,p.openEnded);
      else if(t==='TorusGeometry')n=new T.TorusGeometry(p.radius,p.tube,r(p.radialSegments,4),r(p.tubularSegments,8),p.arc);
      else if(t==='ConeGeometry')n=new T.ConeGeometry(p.radius,p.height,r(p.radialSegments,6));
      else if(t==='CapsuleGeometry')n=new T.CapsuleGeometry(p.radius,p.length,r(p.capSegments,2),r(p.radialSegments,6));
      else if(t==='CircleGeometry')n=new T.CircleGeometry(p.radius,r(p.segments,8),p.thetaStart,p.thetaLength);
      CG_LO[k]=n||g;if(n)KGSET.add(n);}}
  const cg={};for(const k in CG){cg[k]=CG[k];CG[k]=CG_LO[k];}for(const k in wrap){O[k]=T[k];T[k]=wrap[k](O[k]);}
  try{return fn();}finally{for(const k in O)T[k]=O[k];for(const k in cg)CG[k]=cg[k];}}
function buildDriver(parent,rc,topM,irisM){const D=new THREE.Group();parent.add(D);(CHAR_FN[rc.name.toLowerCase()]||CHAR_FN.pep)(D,rc,topM,irisM);return bake(D,true,true);}
const CHAR_COL={pep:'#f6c548',basil:'#3c9a33',olive:'#2b2233',mozz:'#f8f1e2',chili:'#d3221a',shroom:'#efe3cb',pineapple:'#e2a72e',anchovy:'#5a86b8'};
const CHAR_LO={basil:['#3c9a33',[2.2,3.2,1]],olive:['#2b2233',[2.45,2.95,2.2]],mozz:['#f8f1e2',[2.55,2.6,2.35]],chili:['#d3221a',[1.5,2.6,1.4]],shroom:['#8d5a36',[2.9,2.2,2.8]],pineapple:['#e2a72e',[2.15,3.2,2]],anchovy:['#2f5f92',[1.75,3.0,1.55]]};
function loDriver(ld,rc){const k=rc.name.toLowerCase(),c=CHAR_LO[k];if(!c){P3(KG.slice,SH.cheese,0,0,0,ld);hrz(P3(KG.crust,SH.crust,0,0,0,ld));return;}M3(CG.sphS,cm(c[0],.5),[0,c[1][1],0],c[1],null,ld);}

function addCockpit(S,cfg,rc){const armM=cm(CHAR_COL[(rc&&rc.name||'pep').toLowerCase()]||'#f6c548',.5);const [dx,dy]=cfg.drv,[sx,sy]=cfg.steer;
  const stG=new THREE.Group();stG.position.set(sx,sy,0);stG.rotation.z=.55;S.add(stG);P3(KG.steer,SH.black,0,0,0,stG).rotation.y=Math.PI/2;
  limb(KG.col,SH.metal,[sx,sy,0],[sx+.9,sy-1.25,0],S);
  for(const s of [-1,1]){limb(KG.arm,armM,[dx+.3,dy+1.2,1.0*s],[sx-.2,sy+.3,.6*s],S);P3(KG.glove,SH.glove,sx-.15,sy+.3,.6*s,S);}}
function addPlates(S,M,idx,rc,list){for(const [x,y,z,sc] of list)for(const s of [-1,1]){const t=plateTex(String(idx+1),rc.stripe);t.userData.kart=true;
  const pl=new THREE.Mesh(KG.plate,new THREE.MeshStandardMaterial({map:t,transparent:true,roughness:.4}));pl.position.set(x,y,z*s);pl.scale.setScalar(sc||.6);if(s<0)pl.rotation.y=Math.PI;S.add(pl);}}
function lightPair(S,x,y,z,M){for(const s of [-1,1]){hrz(P3(KG.light,SH.light,x,y,z*s,S));P3(KG.bezel,SH.chrome,x+.11,y,z*s,S).rotation.y=Math.PI/2;}}
function exhaust(S,x,y,z){const pp=hrz(P3(KG.pipe,SH.chrome,x,y,z,S));const pi=P3(KG.pipeIn,SH.black,x-.93,y,z,S);pi.rotation.y=-Math.PI/2;P3(KG.pipeRing,SH.chrome,x-.94,y,z,S).rotation.y=Math.PI/2;return [x-.93,y,z];}
const BODY_FN={
  classic(S,M,rc,idx){
    P3(KG.body,M.paint,0,0,0,S);P3(KG.stripe,M.stripe,0,0,0,S);P3(KG.pan,SH.carbon,0,.75,0,S);
    for(const s of [-1,1]){hrz(P3(KG.pod,M.dark,-.2,1.35,2.6*s,S));
      P3(KG.post,SH.metal,-3.7,3.6,1.6*s,S);P3(KG.wingEnd,M.dark,-3.95,4.45,2.95*s,S);
      P3(KG.tail,M.tailM,-4.33,2.15,1.35*s,S);
      limb(KG.stalk,SH.carbon,[1.0,2.6,1.85*s],[1.25,3.3,2.45*s],S);P3(KG.mirror,M.dark,1.25,3.38,2.5*s,S);P3(KG.glassM,SH.lens,1.1,3.38,2.5*s,S);
      limb(KG.rod,SH.metal,[2.5,1.2,1.6*s],[3.15,1.05,2.2*s],S);limb(KG.rod,SH.metal,[2.5,1.75,1.6*s],[3.15,1.35,2.2*s],S);
      for(let i=0;i<4;i++){hrx(P3(KG.spring,SH.chrome,2.45,1.45+i*.18,1.85*s,S));hrx(P3(KG.spring,SH.chrome,-2.2,1.6+i*.18,2.0*s,S));}}
    const pipes=[exhaust(S,-4.8,2.45,.85),exhaust(S,-4.8,2.45,-.85)];
    lightPair(S,4.86,1.62,1.35);
    hrx(P3(KG.axle,SH.metal,-2.95,1.32,0,S));hrx(P3(KG.bumper,SH.carbon,5.08,.95,0,S));
    P3(KG.grille,SH.black,4.98,1.28,0,S);for(let i=0;i<3;i++)P3(KG.bar,SH.chrome,5.05,1.1+i*.18,0,S);
    P3(KG.wing,M.paint,-3.95,4.5,0,S).rotation.z=.12;
    P3(KG.engine,SH.metal,-3.2,3.45,0,S);for(let i=0;i<4;i++)P3(KG.fin,SH.chrome,-3.2,3.75+i*.18,0,S).scale.set(1-i*.08,1,1);
    P3(KG.scoop,M.dark,-2.55,4.35,0,S);P3(KG.seat,SH.seat,-1.75,3.6,0,S);hrx(P3(KG.headrest,SH.seat,-1.95,5.0,0,S));
    addPlates(S,M,idx,rc,[[-.2,1.38,3.2]]);
    return {rw:[-2.95,3.0,1.32],fw:[3.15,2.75,1.05],drv:[-.5,3.05],steer:[1.7,3.65],pipes,lo:[9,2.2,4.2,1.9],bubY:3.4,glY:10,top:7.2};},
  racer(S,M,rc,idx){
    const prof=[[-4.9,.75],[6.4,.75],[6.95,1.0],[5.2,1.45],[2.2,1.9],[-.8,2.15],[-3.6,2.4],[-5.0,1.85]];
    P3(extr(prof,2.2,.35),M.paint,0,0,0,S);P3(extr(prof,.5,.37),M.stripe,0,0,0,S);P3(new THREE.BoxGeometry(10.6,.25,4.4),SH.carbon,0,.62,0,S);
    for(const s of [-1,1]){hrz(P3(KG.pod,M.dark,-.7,1.3,1.75*s,S)).scale.set(1.25,1,1.25);
      P3(new THREE.BoxGeometry(1.5,.85,.12),M.dark,6.2,.85,3.4*s,S);
      P3(new THREE.BoxGeometry(2.3,1.9,.14),M.dark,-4.6,3.65,3.0*s,S);P3(new THREE.BoxGeometry(.25,1.7,.25),SH.metal,-4.25,3.0,.7*s,S);
      limb(KG.rod,SH.metal,[4.6,1.25,1.0*s],[4.4,1.1,2.4*s],S);limb(KG.rod,SH.metal,[4.6,1.6,1.0*s],[4.4,1.25,2.4*s],S);
      limb(KG.rod,SH.metal,[-2.8,1.4,1.2*s],[-3.7,1.38,2.5*s],S);
      limb(KG.stalk,SH.carbon,[1.4,2.0,1.1*s],[1.5,2.6,1.6*s],S);P3(KG.mirror,M.dark,1.5,2.65,1.65*s,S);}
    P3(new THREE.BoxGeometry(1.3,.15,6.9),M.paint,6.2,.6,0,S);P3(new THREE.BoxGeometry(.8,.12,6.6),M.stripe,6.0,.82,0,S).rotation.z=.15;
    P3(new THREE.BoxGeometry(1.7,.18,5.9),M.paint,-4.7,3.95,0,S).rotation.z=.1;P3(new THREE.BoxGeometry(1.1,.14,5.9),M.stripe,-4.45,4.45,0,S).rotation.z=.25;
    P3(new THREE.BoxGeometry(2.2,1.0,1.1),M.dark,-2.7,2.85,0,S);P3(KG.pipeIn,SH.black,-1.58,2.95,0,S).rotation.y=Math.PI/2;
    P3(new THREE.BoxGeometry(1,1.7,2.0),SH.seat,-1.6,2.5,0,S);P3(KG.tail,M.tailM,-5.05,1.7,0,S);
    const pipes=[exhaust(S,-4.4,1.75,0)];
    addPlates(S,M,idx,rc,[[-.7,1.35,2.55,.55]]);
    return {rw:[-3.7,3.2,1.38],fw:[4.4,3.0,1.1],wz:1.15,drv:[-.85,2.3],steer:[1.2,3.0],pipes,lo:[11.5,1.6,3.4,1.5],bubY:3.1,glY:9.2,top:6.6};},
  monster(S,M,rc,idx){
    const prof=[[-4.7,3.2],[4.9,3.2],[5.2,4.3],[2.6,4.7],[-4.7,4.8]];
    P3(extr(prof,4.3,.3),M.paint,0,0,0,S);P3(extr(prof,.7,.33),M.stripe,0,0,0,S);
    for(const s of [-1,1]){P3(new THREE.BoxGeometry(9.6,.5,.5),SH.metal,0,2.9,1.5*s,S);
      for(const x of [-3.3,3.5]){P3(new THREE.BoxGeometry(3.8,.35,1.7),M.dark,x,5.05,3.55*s,S);limb(KG.shock,SH.chrome,[x+.6,4.6,2.0*s],[x,2.2,3.0*s],S);}
      limb(KG.tube,SH.chrome,[-2.7,4.9,1.9*s],[-2.4,8.0,1.6*s],S);limb(KG.tube,SH.chrome,[1.4,4.9,1.9*s],[.7,8.0,1.6*s],S);limb(KG.tube,SH.chrome,[-2.4,8.0,1.6*s],[.7,8.0,1.6*s],S);
      P3(KG.tail,M.tailM,-4.95,4.3,1.75*s,S);}
    limb(KG.tube,SH.chrome,[-2.4,8.0,1.6],[-2.4,8.0,-1.6],S);limb(KG.tube,SH.chrome,[.7,8.0,1.6],[.7,8.0,-1.6],S);limb(KG.tube,SH.chrome,[-2.6,5,1.8],[-2.4,8,-1.6],S);
    P3(new THREE.BoxGeometry(.5,.5,3.6),SH.black,.75,8.4,0,S);for(const z of [-1.2,-.4,.4,1.2])P3(KG.light2,SH.light,1.0,8.4,z,S);
    hrx(P3(KG.bumper,SH.chrome,5.4,3.5,0,S));P3(KG.grille,SH.black,5.1,3.95,0,S).scale.set(1,1.2,1.3);lightPair(S,5.12,4.25,1.6);
    P3(KG.seat,SH.seat,-1.5,5.6,0,S);hrx(P3(KG.headrest,SH.seat,-1.7,6.9,0,S));
    const pipes=[exhaust(S,-4.6,3.7,1.3),exhaust(S,-4.6,3.7,-1.3)];
    addPlates(S,M,idx,rc,[[.2,4.0,2.5,.7]]);
    return {rw:[-3.3,3.55,2.1],fw:[3.5,3.55,2.1],wz:1.3,drv:[-.95,4.7],steer:[1.0,6.0],pipes,lo:[10,1.9,4.8,4.0],bubY:5.2,bubS:1.15,glY:13,top:10.2};},
  rocket(S,M,rc,idx){
    const lp=[[0,-5.2],[.9,-5.0],[1.5,-4.2],[1.75,-2.5],[1.8,0],[1.6,2.4],[1.15,4.2],[.5,5.6],[0,6.0]].map(([r,y])=>new THREE.Vector2(r,y));
    const fus=P3(new THREE.LatheGeometry(lp,32),M.paint,0,2.3,0,S);fus.rotation.z=-Math.PI/2;fus.scale.set(1,1,1.15);
    for(const x of [2.6,-3.3]){const r=P3(new THREE.TorusGeometry(x>0?1.66:1.78,.14,8,32),M.stripe,x,2.3,0,S);r.rotation.y=Math.PI/2;r.scale.set(1.15,1,1);}
    P3(new THREE.SphereGeometry(.38,14,10),M.stripe,6.0,2.3,0,S);
    const dome=P3(new THREE.SphereGeometry(2.3,28,14,0,Math.PI*2,0,Math.PI/2),SH.glass,-.2,3.6,0,S);dome.scale.set(1.5,1.15,1);
    {const t=P3(new THREE.TorusGeometry(2.3,.12,8,32),SH.chrome,-.2,3.6,0,S);t.rotation.x=Math.PI/2;t.scale.set(1.5,1,1);}
    for(const s of [-1,1]){P3(extr([[1.8,0],[-3.2,0],[-4.4,3.8*s],[-2.6,4.0*s]],.28,.08),M.dark,0,2.5,0,S).rotation.x=-Math.PI/2;
      const pod=hrz(P3(new THREE.CapsuleGeometry(.5,2.2,6,14),M.paint,-3.4,2.55,3.95*s,S));
      P3(KG.pipeIn,SH.glowC,-4.75,2.55,3.95*s,S).rotation.y=-Math.PI/2;}
    P3(extr([[-2.4,0],[-5.0,0],[-5.5,3.1],[-4.4,3.1]],.24,.08),M.dark,0,3.5,0,S);
    const nz=hrz(P3(new THREE.CylinderGeometry(1.15,1.5,1.4,24,1,true),SH.metal,-5.6,2.3,0,S));
    P3(new THREE.CircleGeometry(1.1,24),SH.glowC,-5.75,2.3,0,S).rotation.y=-Math.PI/2;
    limb(KG.stalk,SH.metal,[-1.6,4.6,0],[-2.0,6.4,0],S);P3(KG.light2,SH.glowO,-2.02,6.5,0,S);
    for(const s of [-1,1])P3(KG.light2,SH.light,5.0,2.0,.7*s,S);
    for(const s of [-1,1])P3(KG.tail,M.tailM,-5.1,3.3,.9*s,S);
    P3(new THREE.BoxGeometry(1,1.4,1.8),SH.seat,-1.4,3.9,0,S);
    return {rw:[-3.0,3.0,1.2],fw:[3.2,2.2,1.0],drv:[-.45,3.45],steer:[1.35,4.1],pipes:[[-6.2,2.3,0],[-4.85,2.55,3.95],[-4.85,2.55,-3.95]],lo:[11.5,2.6,3.6,2.3],bubY:3.6,glY:10.5,top:7.6};},
  buggy(S,M,rc,idx){
    P3(new THREE.BoxGeometry(7.2,.3,3.4),SH.carbon,0,1.25,0,S);
    P3(extr([[1.6,1.2],[4.5,1.2],[4.85,1.75],[2.0,2.7]],2.4,.2),M.paint,0,0,0,S);P3(extr([[1.6,1.2],[4.5,1.2],[4.85,1.75],[2.0,2.7]],.5,.22),M.stripe,0,0,0,S);
    P3(new THREE.BoxGeometry(1.7,1.2,2.0),SH.metal,-3.0,2.0,0,S);for(let i=0;i<4;i++)P3(KG.fin,SH.chrome,-3.0,2.65+i*.16,0,S).scale.set(1-i*.08,1,.7);
    P3(new THREE.CylinderGeometry(.5,.5,.6,16),SH.chrome,-2.7,3.45,0,S);
    P3(KG.seat,SH.seat,-1.5,2.55,0,S).scale.set(1,.85,.8);hrx(P3(KG.headrest,SH.seat,-1.75,3.7,0,S)).scale.set(.8,.8,.8);
    const cage=[[[-2.0,1.3,1.45],[-2.0,5.3,1.05]],[[-2.0,5.3,1.05],[-2.0,5.3,-1.05]],[[-2.0,5.3,1.05],[1.4,4.0,1.15]],[[1.4,4.0,1.15],[2.9,1.4,1.3]],[[-2.0,5.0,1.0],[-3.9,1.6,1.0]],[[-2.6,2.1,1.75],[2.4,1.9,1.55]],[[1.4,4.0,1.15],[1.4,4.0,-1.15]]];
    for(const [a,b] of cage){limb(KG.tube,M.paint,a,b,S);if(a[2]!==-b[2]||a[2]===0)limb(KG.tube,M.paint,[a[0],a[1],-a[2]],[b[0],b[1],-b[2]],S);}
    const sp=hrz(P3(KG.tire,SH.rubber,-4.2,2.7,0,S));sp.scale.setScalar(.72);hrz(P3(KG.rim,M.dark,-4.2,2.7,0,S)).scale.setScalar(.72);
    for(const s of [-1,1]){P3(KG.light2,SH.light,4.5,2.0,.75*s,S);P3(KG.tail,M.tailM,-3.9,1.7,1.0*s,S);limb(KG.rod,SH.metal,[2.4,1.4,1.2*s],[3.2,1.0,2.0*s],S);}
    const pipes=[exhaust(S,-3.4,2.0,.65),exhaust(S,-3.4,2.0,-.65)];
    return {rw:[-2.8,2.6,1.3],fw:[3.2,2.3,1.0],wz:1.1,drv:[-.85,2.55],steer:[1.15,3.35],pipes,lo:[8,1.6,3.4,1.9],bubY:3.2,bubS:.95,glY:9.5,top:6.4};},
  oven(S,M,rc,idx){
    P3(new THREE.BoxGeometry(9.6,1.2,4.8),M.paint,0,1.75,0,S);P3(new THREE.BoxGeometry(9.7,.3,4.9),M.stripe,0,2.15,0,S);
    for(const s of [-1,1])P3(new THREE.BoxGeometry(8.4,.9,.3),M.dark,0,1.5,2.55*s,S);
    const dome=P3(new THREE.SphereGeometry(2.7,28,14,0,Math.PI*2,0,Math.PI/2),M.brick,-2.55,2.35,0,S);dome.scale.set(1,1.02,.95);
    P3(new THREE.CylinderGeometry(2.75,2.85,.35,28),M.dark,-2.55,2.45,0,S);
    const arch=P3(new THREE.TorusGeometry(1.05,.25,8,20,Math.PI),M.dark,-5.15,2.45,0,S);arch.rotation.y=Math.PI/2;
    const glow=P3(new THREE.CircleGeometry(1.0,20,0,Math.PI),SH.glowO,-5.2,2.45,0,S);glow.rotation.y=-Math.PI/2;
    P3(new THREE.CylinderGeometry(.45,.55,2.2,14),SH.metal,-1.6,5.4,0,S);P3(new THREE.CylinderGeometry(.75,.75,.25,14),SH.metal,-1.6,6.55,0,S);
    const hood=[[2.5,2.3],[4.85,2.3],[5.05,2.95],[3.4,3.4],[2.5,3.4]];P3(extr(hood,4.0,.2),M.paint,0,0,0,S);P3(extr(hood,.6,.22),M.stripe,0,0,0,S);
    P3(KG.grille,SH.black,5.0,1.75,0,S).scale.set(1,1.3,1.5);for(let i=0;i<3;i++)P3(KG.bar,SH.chrome,5.08,1.55+i*.22,0,S).scale.set(1,1,1.4);
    lightPair(S,4.95,2.65,1.55);hrx(P3(KG.bumper,SH.carbon,5.25,1.1,0,S)).scale.set(1,1,1.1);
    for(const s of [-1,1])P3(KG.tail,M.tailM,-4.85,1.85,2.0*s,S);
    const pipes=[exhaust(S,-4.4,1.35,1.5),exhaust(S,-4.4,1.35,-1.5)];
    addPlates(S,M,idx,rc,[[1.6,1.75,2.72,.65]]);
    return {rw:[-3.1,3.25,1.4],fw:[3.4,3.1,1.2],wz:1.2,drv:[.75,2.35],steer:[2.75,3.4],pipes,lo:[10,3,4.8,2.6],bubY:3.6,bubS:1.05,glY:10.5,top:7.2,smoke:[-1.6,6.9,0]};}
};
/* ================= HAND-BUILT KARTS (v51) =================
   Seven original karts modelled from primitives: smooth spline profiles, lathed shells, bevelled panels,
   tubes, rivets, vents and lamps. Paint, stripe and trim parts follow the player's colours and liveries;
   themed parts (brick, cheese, leaves, wood) keep their own look. Everything is merged by material when the kart is built. */
const KB={};let _kGlass=null;const kGlass=()=>{if(!_kGlass){_kGlass=new THREE.MeshPhysicalMaterial({color:'#cfeeff',roughness:.04,metalness:0,transparent:true,opacity:.32,depthWrite:false,side:THREE.DoubleSide,envMapIntensity:1.4});SHSET.add(_kGlass);}return _kGlass;};
/* smooth side profile from points, extruded across the kart with a soft bevel */
const KQ=()=>HQB?1:.35;
function kProf(pts,depth,bev,curve){const s=new THREE.Shape();s.moveTo(pts[0][0],pts[0][1]);s.splineThru(pts.slice(1).map(p=>new THREE.Vector2(p[0],p[1])));s.closePath();
  const g=new THREE.ExtrudeGeometry(s,{depth,bevelEnabled:bev>0,bevelThickness:bev,bevelSize:bev*.9,bevelSegments:HQB?4:2,curveSegments:Math.max(6,Math.round((curve||40)*KQ())),steps:1});g.translate(0,0,-depth/2);return g;}
/* rounded box (x length, y height, z width) */
function kRBox(w,h,d,r){r=Math.min(r,w/2-.01,h/2-.01);const s=new THREE.Shape(),x=-w/2+r,y=-h/2+r;s.moveTo(x,-h/2);s.lineTo(w/2-r,-h/2);s.quadraticCurveTo(w/2,-h/2,w/2,y);s.lineTo(w/2,h/2-r);s.quadraticCurveTo(w/2,h/2,w/2-r,h/2);
  s.lineTo(x,h/2);s.quadraticCurveTo(-w/2,h/2,-w/2,h/2-r);s.lineTo(-w/2,y);s.quadraticCurveTo(-w/2,-h/2,x,-h/2);const b=Math.min(r*.8,d/2-.01);
  const g=new THREE.ExtrudeGeometry(s,{depth:Math.max(.01,d-2*b),bevelEnabled:true,bevelThickness:b,bevelSize:b*.95,bevelSegments:HQB?4:2,curveSegments:HQB?8:3});g.translate(0,0,-(d-2*b)/2);return g;}
/* lathe along the kart's length: pts are [radius, x] pairs, nose at +x */
function kLathe(pts,seg){const g=new THREE.LatheGeometry(pts.map(([r,x])=>new THREE.Vector2(Math.max(.001,r),x)),Math.max(8,Math.round((seg||36)*(HQB?1:.5))));g.rotateZ(-Math.PI/2);return g;}
function kTube(pts,r,seg,rad){return new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts.map(p=>new THREE.Vector3(...p))),Math.max(4,Math.round((seg||24)*(HQB?1:.5))),r,HQB?(rad||8):Math.max(4,(rad||8)>>1),false);}
const kAdd=(geo,mat,x,y,z,S,rx,ry,rz,sx,sy,sz)=>{const m=P3(geo,mat,x,y,z,S);if(rx||ry||rz)m.rotation.set(rx||0,ry||0,rz||0);if(sx)m.scale.set(sx,sy??sx,sz??sx);return m;};
/* a row of round rivet heads */
function kRivets(S,mat,a,b,n,r){const g=KB.rivet||(KB.rivet=new THREE.SphereGeometry(1,8,6,0,Math.PI*2,0,Math.PI/2));for(let i=0;i<n;i++){const t=n>1?i/(n-1):.5,m=P3(g,mat,a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t,a[2]+(b[2]-a[2])*t,S);m.scale.setScalar(r||.07);if(a[3])m.rotation.set(a[3],a[4]||0,a[5]||0);}}
/* slotted vent: a dark recess with chrome slats */
function kVent(S,x,y,z,w,h,n,face,matIn,matSlat){const G=new THREE.Group();G.position.set(x,y,z);if(face)G.rotation.y=face;S.add(G);
  P3(kRBox(w,h,.12,.06),matIn||cm('#141110',.6),0,0,0,G);for(let i=0;i<n;i++)P3(kRBox(w*.92,h/(n*2.2),.16,.02),matSlat||SH.chrome,0,-h/2+h*(i+.5)/n,.04,G);return G;}
/* headlamp: chrome cup, glowing lens, little visor */
function kLamp(S,x,y,z,r,ry,mat){const G=new THREE.Group();G.position.set(x,y,z);G.rotation.y=ry||0;S.add(G);
  const cup=P3(KB.cup||(KB.cup=new THREE.SphereGeometry(1,20,12,0,Math.PI*2,0,Math.PI/2)),SH.chrome,0,0,0,G);cup.rotation.z=-Math.PI/2;cup.scale.set(r*1.15,r*1.1,r*1.1);
  const ln=P3(KB.lens||(KB.lens=new THREE.SphereGeometry(1,18,10,0,Math.PI*2,0,Math.PI/2)),mat||SH.light,.02,0,0,G);ln.rotation.z=-Math.PI/2;ln.scale.set(r*.35,r*.92,r*.92);
  const rim=P3(KB.rim2||(KB.rim2=new THREE.TorusGeometry(1,.09,8,24)),SH.chrome,0,0,0,G);rim.rotation.y=Math.PI/2;rim.scale.setScalar(r*1.02);return G;}
/* tyre-style bolt pattern hub cap for decorative wheels */
function kSeat(S,x,y,mat,w){const G=new THREE.Group();G.position.set(x,y,0);S.add(G);const W=w||1.9;
  P3(kRBox(1.3,.42,W,.18),mat,0,0,0,G);const back=P3(kRBox(.38,1.9,W,.17),mat,-.55,.95,0,G);back.rotation.z=.2;
  for(const s of [-1,1])P3(kRBox(1.0,.7,.3,.12),mat,-.1,.42,(W/2-.05)*s,G);P3(kRBox(.3,.62,W*.62,.14),mat,-.95,2.05,0,G).rotation.z=.2;return G;}

Object.assign(BODY_FN,{
/* ---------- CLASSIC: the house kart, rebuilt with a sculpted shell, side pods, a velocity-stack engine and a proper wing ---------- */
classic(S,M,rc,idx){
  const shell=[[5.2,.95],[5.45,1.55],[4.6,2.05],[2.6,2.35],[1.2,2.6],[-.6,2.7],[-2.4,2.75],[-4.0,2.6],[-4.6,1.8],[-4.4,.9],[0,.75]];
  P3(kProf(shell,3.4,.42),M.paint,0,0,0,S);P3(kProf(shell,.62,.44),M.stripe,0,0,0,S);
  P3(kRBox(9.6,.36,5.0,.16),SH.carbon,.2,.78,0,S);
  /* cockpit opening rim */
  const cr=P3(new THREE.TorusGeometry(1,.14,10,40),SH.black,-.6,2.92,0,S);cr.rotation.x=Math.PI/2;cr.scale.set(1.9,1.25,1);
  /* nose: chrome grille ring with slats, twin pod lamps */
  kAdd(new THREE.TorusGeometry(.62,.1,10,32),SH.chrome,5.42,1.45,0,S,0,Math.PI/2);kAdd(new THREE.CircleGeometry(.6,28),cm('#111',.5),5.4,1.45,0,S,0,Math.PI/2);
  for(let i=-2;i<=2;i++)kAdd(kRBox(.06,.95,.08,.02),SH.chrome,5.45,1.45,i*.2,S);
  for(const s of [-1,1]){kAdd(kLathe([[0,0],[.34,-.05],[.38,-.6],[.3,-1.1],[0,-1.2]],18),M.dark,4.95,1.95,1.25*s,S);kLamp(S,4.98,1.95,1.25*s,.3);}
  /* front wing with end plates */
  P3(kProf([[6.15,.55],[5.9,.82],[5.0,.86],[4.7,.62]],6.4,.05),M.paint,0,0,0,S);P3(kProf([[5.95,.88],[5.4,1.08],[4.95,.9]],6.0,.04),M.stripe,0,0,0,S);
  for(const s of [-1,1])P3(kRBox(1.6,.9,.1,.08),M.dark,5.4,.9,3.25*s,S);
  /* side pods with intake vents and number plates */
  for(const s of [-1,1]){const pod=kAdd(kLathe([[0,2.1],[.48,1.9],[.62,1.2],[.62,-1.2],[.5,-1.8],[.28,-2.1]],24),M.paint,-.3,1.38,2.55*s,S,0,0,0,1,1,1.05);
    kVent(S,1.55,1.4,2.55*s,.12,.72,4,0,null,SH.chrome).rotation.y=Math.PI/2;kAdd(new THREE.TorusGeometry(.58,.05,8,28),SH.chrome,1.62,1.38,2.55*s,S,0,Math.PI/2);
    kRivets(S,SH.chrome,[-2.1,1.85,2.55*s+.42*s],[1.2,1.85,2.55*s+.42*s],7,.06);
    /* mirrors on stalks */
    P3(kTube([[1.2,2.55,1.35*s],[1.45,3.1,1.95*s],[1.4,3.35,2.35*s]],.06,12,6),SH.chrome,0,0,0,S);const mi=kAdd(kRBox(.25,.42,.72,.12),M.dark,1.42,3.38,2.4*s,S);kAdd(new THREE.PlaneGeometry(.6,.32),SH.lens,1.55,3.38,2.4*s,S,0,Math.PI/2);
    /* suspension: wishbones and chrome coil-overs */
    for(const y of [1.15,1.6])limb(KG.rod,SH.metal,[2.6,y,1.3*s],[3.15,y-.3,2.25*s],S);
    for(let i=0;i<5;i++)kAdd(KG.spring,SH.chrome,2.55,1.25+i*.15,1.8*s,S,Math.PI/2);
    for(let i=0;i<5;i++)kAdd(KG.spring,SH.chrome,-2.3,1.35+i*.15,2.05*s,S,Math.PI/2);
    P3(KG.tail,M.tailM,-4.5,2.05,1.4*s,S);}
  /* engine bay behind the seat: block, valve cover, four velocity stacks */
  P3(kRBox(1.9,1.0,1.7,.18),SH.metal,-3.15,3.05,0,S);P3(kRBox(1.6,.3,1.2,.14),M.stripe,-3.15,3.65,0,S);
  for(let i=0;i<4;i++){const z=-.66+i*.44;kAdd(kLathe([[.17,.0],[.17,-.5],[.24,-.62],[.27,-.66]],14),SH.chrome,-2.65,3.55,z,S,0,0,Math.PI/2+.25);}
  kAdd(new THREE.CylinderGeometry(.38,.38,.5,18),SH.chrome,-3.75,3.55,0,S,Math.PI/2);for(let i=0;i<5;i++)kAdd(new THREE.TorusGeometry(.4,.03,6,18),SH.metal,-3.75,3.55,-.2+i*.1,S);
  /* roll hoop with padding */
  P3(kTube([[-2.05,2.6,-1.1],[-2.15,4.3,-.95],[-2.2,4.75,0],[-2.15,4.3,.95],[-2.05,2.6,1.1]],.12,24,8),SH.chrome,0,0,0,S);kAdd(new THREE.CapsuleGeometry(.26,1.3,6,12),SH.seat,-2.15,4.6,0,S,Math.PI/2);
  /* swan-neck rear wing */
  P3(kProf([[-3.6,4.55],[-4.2,4.95],[-5.25,4.85],[-5.35,4.45],[-4.3,4.4]],5.4,.06),M.paint,0,0,0,S);P3(kProf([[-4.0,5.05],[-4.9,5.3],[-5.15,5.05],[-4.35,4.95]],5.2,.05),M.stripe,0,0,0,S);
  for(const s of [-1,1]){P3(kTube([[-3.4,3.0,.55*s],[-3.9,4.0,.62*s],[-4.4,4.75,.6*s]],.09,16,6),SH.metal,0,0,0,S);P3(kRBox(1.9,1.3,.1,.1),M.dark,-4.5,4.7,2.75*s,S);}
  /* diffuser fins, tow hook, fuel cap */
  for(let i=-2;i<=2;i++)P3(kRBox(1.0,.5,.08,.04),SH.carbon,-4.55,1.05,i*.62,S);kAdd(new THREE.TorusGeometry(.18,.06,6,14),SH.chrome,-4.75,1.0,0,S,0,Math.PI/2);
  kAdd(new THREE.CylinderGeometry(.22,.22,.08,18),SH.chrome,2.2,2.42,.8,S);
  const pipes=[exhaust(S,-4.75,2.25,.75),exhaust(S,-4.75,2.25,-.75)];
  kSeat(S,-1.25,2.4,SH.seat,1.9);addPlates(S,M,idx,rc,[[-.3,1.42,3.2,.6]]);
  return {rw:[-2.95,3.0,1.32],fw:[3.15,2.75,1.05],drv:[-.55,2.85],steer:[1.55,3.55],pipes,lo:[9.6,2.4,4.6,1.9],bubY:3.4,glY:10,top:7.2};},

/* ---------- ROCKET: a polished 1950s rocket on wheels, with portholes, rivets, three fins and glowing thrusters ---------- */
rocket(S,M,rc,idx){
  const hull=[[0,6.3],[.28,6.15],[.85,5.6],[1.35,4.6],[1.7,3.2],[1.85,1.4],[1.86,-.6],[1.75,-2.6],[1.5,-4.2],[1.2,-5.1]];
  const fus=kAdd(kLathe(hull,48),M.paint,0,2.35,0,S,0,0,0,1,1,1.12);
  kAdd(kLathe([[0,6.32],[.3,6.15],[.62,5.75],[.66,5.6],[0,5.55]],24),SH.chrome,0,2.35,0,S,0,0,0,1,1,1.12);
  /* panel seams and stripe bands */
  for(const [x,r,w,mat] of [[3.4,1.73,.32,M.stripe],[2.9,1.79,.06,SH.chrome],[-1.0,1.885,.06,SH.chrome],[-3.3,1.72,.32,M.stripe],[-3.75,1.66,.06,SH.chrome]])kAdd(kLathe([[r,x+w/2],[r+.03,x],[r,x-w/2]],48),mat,0,2.35,0,S,0,0,0,1,1,1.12);
  for(const x of [2.85,-.95])for(let i=0;i<16;i++){const a=i/16*Math.PI*2,r=x>0?1.78:1.89;if(Math.sin(a)<-.5)continue;kAdd(KB.rivet||(KB.rivet=new THREE.SphereGeometry(1,8,6,0,Math.PI*2,0,Math.PI/2)),SH.chrome,x,2.35+Math.sin(a)*r,Math.cos(a)*r*1.12,S,a-Math.PI/2,0,0,.07);}
  /* portholes */
  for(const s of [-1,1])for(const x of [2.0,.6]){kAdd(new THREE.TorusGeometry(.36,.09,8,24),SH.chrome,x,2.55,1.97*s,S);kAdd(new THREE.CircleGeometry(.33,20),SH.lens,x,2.55,1.975*s,S,0,s<0?Math.PI:0);}
  /* bubble canopy with ribs */
  kAdd(new THREE.SphereGeometry(1.2,32,16,0,Math.PI,0,Math.PI/2),kGlass(),.75,3.95,0,S,0,Math.PI/2,0,1.1,1.1,1.25);kAdd(new THREE.TorusGeometry(1.2,.09,8,32,Math.PI),SH.chrome,.75,3.95,0,S,-Math.PI/2,0,Math.PI/2,1.25,1.1,1);
  const cr=kAdd(new THREE.TorusGeometry(1.0,.16,8,40),SH.chrome,-.9,3.98,0,S,Math.PI/2);cr.scale.set(1.9,1.35,1);kAdd(new THREE.CircleGeometry(1,32),cm('#151112',.7),-.9,3.94,0,S,-Math.PI/2,0,0,1.85,1.3,1);
  /* tail fins (two side, one top) with chrome tips */
  const fin=[[1.6,0],[-3.6,0],[-5.0,0],[-5.6,2.9],[-4.4,3.1],[-1.6,.6]];
  for(const s of [-1,1]){kAdd(kProf(fin,.2,.07),M.stripe,0,2.4,1.45*s,S,-Math.PI/2*s);kAdd(new THREE.SphereGeometry(.22,12,8),SH.chrome,-5.0,2.4,(1.45+3.0)*s,S);}
  kAdd(kProf(fin,.2,.07),M.stripe,0,3.4,0,S,0,0,0,1,.75,1);kAdd(new THREE.SphereGeometry(.2,12,8),SH.chrome,-5.0,5.6,0,S);
  /* main thruster bell, glowing core, heat rings */
  kAdd(kLathe([[1.15,-5.05],[1.25,-5.2],[1.6,-6.2],[1.48,-6.25],[1.08,-5.4],[.9,-5.3]],36),SH.metal,0,2.35,0,S,0,0,0,1,1,1.05);
  kAdd(new THREE.CircleGeometry(1.3,32),SH.glowC,-6.05,2.35,0,S,0,-Math.PI/2);kAdd(new THREE.CircleGeometry(.7,24),SH.glowO,-6.0,2.35,0,S,0,-Math.PI/2);
  for(let i=0;i<3;i++)kAdd(new THREE.TorusGeometry(1.28+i*.12,.05,6,36),SH.chrome,-5.35-i*.3,2.35,0,S,0,Math.PI/2);
  /* side boosters on struts */
  for(const s of [-1,1]){const z=3.75*s;kAdd(kLathe([[0,1.6],[.35,1.3],[.52,.6],[.55,-1.2],[.62,-1.5],[.55,-1.6]],24),M.paint,-3.0,2.6,z,S);
    kAdd(new THREE.CircleGeometry(.48,20),SH.glowC,-4.62,2.6,z,S,0,-Math.PI/2);kAdd(new THREE.TorusGeometry(.56,.05,6,24),SH.chrome,-3.6,2.6,z,S,0,Math.PI/2);
    kAdd(kProf([[-2.2,0],[-4.4,0],[-4.6,1.2],[-3.9,1.2]],.12,.04),M.stripe,0,2.6,z,S,-Math.PI/2*s,0,0);
    P3(kTube([[-2.4,2.4,1.6*s],[-2.8,2.55,2.8*s],[-3.0,2.6,3.3*s]],.11,10,8),SH.chrome,0,0,0,S);P3(kTube([[-3.9,2.3,1.5*s],[-3.9,2.5,2.8*s],[-3.6,2.6,3.3*s]],.11,10,8),SH.chrome,0,0,0,S);}
  /* antenna with blinking bulb, nose lamps */
  P3(kTube([[-2.4,4.1,0],[-2.7,5.4,0],[-2.95,6.6,0]],.05,10,6),SH.chrome,0,0,0,S);kAdd(new THREE.SphereGeometry(.2,14,10),SH.glowO,-2.97,6.7,0,S);
  for(const s of [-1,1])kLamp(S,5.15,2.05,.72*s,.28);
  for(const s of [-1,1])P3(KG.tail,M.tailM,-5.0,3.2,1.0*s,S);
  kSeat(S,-1.2,3.25,SH.seat,1.6);
  return {rw:[-3.0,3.0,1.2],fw:[3.2,2.3,1.0],drv:[-.4,3.55],steer:[1.35,4.15],pipes:[[-6.4,2.35,0],[-4.75,2.6,3.75],[-4.75,2.6,-3.75]],lo:[11.5,2.6,3.6,2.3],bubY:3.6,glY:10.5,top:7.6};},

/* ---------- BRICK OVEN: a wood-fired oven on a timber cart, iron door, ember glow, chimney, logs and a peel ---------- */
oven(S,M,rc,idx){
  const wood=cm('#8a5a34',.75),woodD=cm('#5e3a1e',.8),iron=cm('#2a2624',.45,.6),copper=cm('#c8763a',.28,.85);
  /* timber deck: planks with dark seams and iron corner brackets */
  for(let i=0;i<7;i++){const z=-2.25+i*.75;P3(kRBox(9.8,.34,.7,.08),i%2?wood:woodD,0,1.25,z,S);}
  for(const s of [-1,1])P3(kRBox(9.9,.5,.24,.08),M.paint,0,1.0,2.55*s,S);
  for(const x of [-4.6,4.6])for(const s of [-1,1]){P3(kRBox(.5,.6,.5,.08),iron,x,1.25,2.45*s,S);kRivets(S,SH.chrome,[x-.18,1.4,2.72*s],[x+.18,1.4,2.72*s],2,.06);}
  /* oven base, brick dome, copper band, mortar lip */
  P3(kRBox(5.6,.9,4.6,.25),M.paint,-2.2,1.85,0,S);P3(kRBox(5.7,.14,4.7,.06),copper,-2.2,2.32,0,S);
  const dome=kAdd(new THREE.SphereGeometry(2.6,40,20,0,Math.PI*2,0,Math.PI/2),M.brick,-2.4,2.38,0,S,0,0,0,1.02,1.04,.92);
  kAdd(new THREE.TorusGeometry(2.62,.13,8,48),copper,-2.4,2.42,0,S,Math.PI/2,0,0,1.02,.92,1);
  /* arched mouth: brick arch, iron door frame, hinged door ajar, embers inside */
  kAdd(new THREE.TorusGeometry(1.15,.32,10,24,Math.PI),M.brick,-4.9,2.4,0,S,0,Math.PI/2);
  kAdd(new THREE.CircleGeometry(1.0,24,0,Math.PI),SH.glowO,-4.95,2.42,0,S,0,-Math.PI/2);
  for(let i=0;i<9;i++)kAdd(new THREE.SphereGeometry(.13+Math.random()*.08,8,6),i%3?SH.glowO:SH.glowC,-4.75,2.48+Math.random()*.15,(Math.random()-.5)*1.4,S);
  const door=new THREE.Group();door.position.set(-5.05,2.4,1.1);door.rotation.y=-.9;S.add(door);P3(kRBox(.12,1.05,1.0,.06),iron,0,.5,-.5,door);kAdd(new THREE.TorusGeometry(.18,.04,6,14),SH.chrome,-.08,.55,-.75,door,0,Math.PI/2);
  for(const y of [2.55,3.25])kAdd(new THREE.CylinderGeometry(.06,.06,.3,8),iron,-5.0,y,1.12,S);
  /* chimney with spark cap */
  kAdd(new THREE.CylinderGeometry(.42,.5,2.6,18),copper,-1.4,5.3,0,S);kAdd(new THREE.TorusGeometry(.5,.07,6,20),SH.chrome,-1.4,4.4,0,S,Math.PI/2);
  kAdd(new THREE.ConeGeometry(.85,.55,18,1,true),iron,-1.4,6.95,0,S);for(let i=0;i<6;i++){const a=i/6*Math.PI*2;limb(KG.rod,iron,[-1.4+Math.cos(a)*.45,6.6,Math.sin(a)*.45],[-1.4+Math.cos(a)*.7,6.75,Math.sin(a)*.7],S);}
  /* thermometer dial on the dome */
  kAdd(new THREE.CylinderGeometry(.42,.42,.12,24),SH.chrome,-.1,3.5,0,S,0,0,Math.PI/2+.5);kAdd(new THREE.CircleGeometry(.34,20),SH.white,-.05,3.53,0,S,0,Math.PI/2,-.5);
  kAdd(kRBox(.05,.28,.04,.01),cm('#c0301c',.4),-.02,3.55,0,S,0,0,-.5);
  /* front: cab hood with grille, lanterns */
  const hood=[[2.3,1.45],[5.1,1.45],[5.35,2.1],[4.9,2.95],[3.2,3.25],[2.3,3.25]];P3(kProf(hood,4.0,.22),M.paint,0,0,0,S);P3(kProf(hood,.6,.24),M.stripe,0,0,0,S);
  kVent(S,5.32,2.05,0,1.6,.9,5,Math.PI/2,null,SH.chrome);
  for(const s of [-1,1]){const L=new THREE.Group();L.position.set(5.0,3.2,1.55*s);S.add(L);P3(kRBox(.5,.6,.5,.08),iron,0,0,0,L);P3(new THREE.BoxGeometry(.42,.48,.42),SH.light,0,.0,0,L);kAdd(new THREE.ConeGeometry(.38,.3,4),iron,0,.45,0,L,0,Math.PI/4);
    kAdd(new THREE.TorusGeometry(.14,.03,6,12),iron,0,.66,0,L);}
  hrx(P3(KG.bumper,iron,5.45,1.05,0,S)).scale.set(1,1,1.05);
  /* firewood rack on the right, peel on the left */
  for(let i=0;i<5;i++){const y=1.75+(i%3)*.36,z=2.9+(i>2?.32:0),x=.6+(i%2)*.25;kAdd(new THREE.CylinderGeometry(.17,.17,2.6,10),woodD,x,y,z,S,0,0,Math.PI/2);kAdd(new THREE.CircleGeometry(.15,10),cm('#c8a070',.8),x+1.31,y,z,S,0,Math.PI/2);}
  for(const x of [-.6,1.9])P3(kRBox(.12,1.3,.12,.03),iron,x,2.1,3.2,S);
  P3(kRBox(4.2,.08,.18,.04),wood,1.0,2.0,-2.92,S).rotation.z=.05;kAdd(new THREE.CylinderGeometry(.95,.95,.06,24),cm('#b07a46',.7),3.4,2.13,-2.95,S,Math.PI/2);
  for(const s of [-1,1])P3(KG.tail,M.tailM,-5.0,1.6,2.1*s,S);
  const pipes=[exhaust(S,-4.6,1.25,1.6),exhaust(S,-4.6,1.25,-1.6)];
  kSeat(S,1.05,2.5,cm('#6a3a1e',.7),2.1);addPlates(S,M,idx,rc,[[1.8,1.55,2.72,.65]]);
  return {rw:[-3.1,3.25,1.4],fw:[3.4,3.1,1.2],wz:1.2,drv:[1.6,2.75],steer:[3.35,3.6],pipes,lo:[10,3,4.8,2.6],bubY:3.6,bubS:1.05,glY:10.5,top:7.2,smoke:[-1.4,7.2,0]};},

/* ---------- PRONTO: a bubbly little delivery van with a stack of pizza boxes on the roof ---------- */
delivery(S,M,rc,idx){
  const card=cm('#d8b48a',.85),cardD=cm('#b8916a',.85),sauce=cm('#c53b22',.4);
  /* chassis and skirt */
  P3(kRBox(9.6,.5,4.8,.22),M.dark,-.2,1.2,0,S);
  /* rounded nose with a friendly face: big lamps, a smiling grille, a little chrome brow */
  const nose=[[5.15,1.35],[5.35,2.3],[4.7,3.05],[3.0,3.3],[1.6,3.25],[1.6,1.35]];P3(kProf(nose,4.4,.35),M.paint,0,0,0,S);P3(kProf(nose,.7,.37),M.stripe,0,0,0,S);
  for(const s2 of [-1,1]){kLamp(S,4.95,2.45,1.45*s2,.46);kAdd(new THREE.TorusGeometry(.5,.07,8,24),M.stripe,5.0,2.45,1.45*s2,S,0,Math.PI/2);kAdd(new THREE.TorusGeometry(.55,.08,6,20,Math.PI*.8),SH.chrome,5.0,2.62,1.45*s2,S,0,Math.PI/2,Math.PI*.1);}
  kAdd(new THREE.TorusGeometry(.7,.13,8,24,Math.PI),SH.black,5.32,1.95,0,S,Math.PI,Math.PI/2,0);
  hrx(P3(KG.bumper,SH.chrome,5.4,1.2,0,S));
  /* low windscreen in a chrome frame, cab sides with round mirrors */
  kAdd(kRBox(.1,1.0,3.6,.3),kGlass(),2.0,3.75,0,S,0,0,-.35);P3(kTube([[1.7,3.25,-1.85],[2.1,4.25,-1.8],[2.1,4.25,1.8],[1.7,3.25,1.85]],.08,24,6),SH.chrome,0,0,0,S);
  for(const s2 of [-1,1]){P3(kProf([[1.7,1.35],[1.7,3.25],[-.8,3.0],[-.9,1.35]],.25,.1),M.paint,0,0,2.2*s2,S);
    P3(kTube([[1.8,3.3,2.2*s2],[2.15,3.75,2.65*s2]],.05,6,6),SH.chrome,0,0,0,S);kAdd(new THREE.CylinderGeometry(.3,.3,.1,18),SH.chrome,2.2,3.85,2.75*s2,S,0,0,Math.PI/2);kAdd(new THREE.CircleGeometry(.26,18),SH.lens,2.26,3.85,2.75*s2,S,0,Math.PI/2);}
  /* insulated cargo box: rounded, with a door seam, handle, latches and a slice decal */
  P3(kRBox(4.4,3.0,4.6,.5),M.paint,-3.0,2.95,0,S);P3(kRBox(4.5,.32,4.7,.12),M.stripe,-3.0,2.0,0,S);P3(kRBox(4.5,.18,4.7,.08),M.stripe,-3.0,4.25,0,S);
  P3(kRBox(.06,2.3,3.2,.03),M.dark,-5.22,3.05,0,S);P3(kRBox(.12,.14,1.2,.06),SH.chrome,-5.25,3.25,0,S);for(const z of [-1.6,1.6])P3(kRBox(.16,.5,.22,.06),SH.chrome,-5.24,3.1,z,S);
  for(const s2 of [-1,1]){const sl=kAdd(KG.slice,SH.cheese,-3.0,2.6,2.31*s2,S,0,s2>0?0:Math.PI,-Math.PI/2,.2,.2,.06);
    for(const [dx,dy] of [[-.25,.12],[.3,.25],[0,-.3]])kAdd(new THREE.CylinderGeometry(.15,.15,.04,14),sauce,-3.0+dx,2.6+dy,2.35*s2,S,Math.PI/2);
    kRivets(S,SH.chrome,[-4.9,4.0,2.32*s2],[-1.1,4.0,2.32*s2],6,.05);}
  /* stack of pizza boxes strapped on top, and the light-up slice sign */
  for(let i=0;i<3;i++){const b=new THREE.Group();b.position.set(-3.0,4.6+i*.44,0);b.rotation.y=(i-1)*.1;S.add(b);P3(kRBox(3.4,.4,3.4,.06),i%2?cardD:card,0,0,0,b);P3(kRBox(3.2,.02,3.2,.01),sauce,0,.21,0,b);P3(kRBox(1.3,.02,.55,.01),SH.white,0,.225,0,b);}
  for(const x of [-3.8,-2.2])P3(kRBox(.22,1.55,3.75,.05),cm('#2a2420',.7),x,5.05,0,S);
  const sign=new THREE.Group();sign.position.set(-3.0,6.35,0);S.add(sign);kAdd(KG.slice,SH.cheese,0,.1,0,sign,0,Math.PI/2,0,.3,.3,.25);P3(kRBox(.2,.6,.2,.05),SH.metal,0,-.35,0,sign);
  for(const [y,z] of [[.7,.3],[.95,-.2],[.45,-.35]])kAdd(new THREE.CylinderGeometry(.13,.13,.08,14),sauce,.12,y,z,sign,0,0,Math.PI/2);
  for(const s2 of [-1,1])P3(kRBox(.12,.7,.45,.1),M.tailM,-5.22,2.15,1.8*s2,S);hrx(P3(KG.bumper,SH.chrome,-5.45,1.2,0,S));
  const pipes=[exhaust(S,-4.6,1.0,1.3)];
  kSeat(S,.15,2.0,SH.seat,2.0);addPlates(S,M,idx,rc,[[3.4,2.2,2.35,.55]]);
  return {rw:[-3.0,2.95,1.25],fw:[3.2,2.95,1.2],wz:1.15,drv:[.85,2.45],steer:[2.4,3.35],pipes,lo:[10,4.2,4.8,2.9],bubY:3.8,bubS:1.15,glY:11.5,top:8.2};},

/* ---------- SLICER: a long low kart built around a giant chrome pizza cutter ---------- */
cutter(S,M,rc,idx){
  /* spine: the cutter's handle, with rubber grip rings and a bolster */
  kAdd(kLathe([[0,4.0],[.45,3.8],[.62,3.0],[.7,-1.5],[.8,-3.6],[.7,-4.6],[0,-4.8]],32),M.paint,0,2.1,0,S,0,0,0,1,1,1.25);
  for(let i=0;i<6;i++)kAdd(new THREE.TorusGeometry(.74,.07,8,28),SH.black,-1.5-i*.45,2.1,0,S,0,Math.PI/2,0,1,1.25,1);
  kAdd(new THREE.CylinderGeometry(.85,.85,.55,24),SH.chrome,3.75,2.1,0,S,0,0,Math.PI/2,1,1,1.25);
  /* the blade: a big chrome disc in a fork at the nose */
  const bl=new THREE.Group();bl.position.set(5.3,2.15,0);S.add(bl);kAdd(new THREE.CylinderGeometry(1.75,1.75,.12,48),SH.chrome,0,0,0,bl,Math.PI/2);kAdd(new THREE.CylinderGeometry(1.5,1.5,.16,48),SH.disc,0,0,0,bl,Math.PI/2);
  kAdd(new THREE.CylinderGeometry(.42,.42,.6,20),M.stripe,0,0,0,bl,Math.PI/2);for(let i=0;i<6;i++){const a=i/6*Math.PI*2;kAdd(new THREE.CylinderGeometry(.08,.08,.64,8),SH.chrome,Math.cos(a)*.28,Math.sin(a)*.28,0,bl,Math.PI/2);}
  for(const s of [-1,1])P3(kProf([[3.7,1.6],[3.7,2.65],[5.3,2.45],[5.5,2.15],[5.3,1.85]],.14,.05),M.paint,0,0,.42*s,S);
  /* low floor pan and side pods shaped like blade guards */
  P3(kRBox(9.2,.3,4.4,.14),SH.carbon,-.2,.8,0,S);
  for(const s of [-1,1]){P3(kProf([[3.0,.95],[2.4,1.85],[-2.5,2.05],[-4.3,1.55],[-4.4,.95]],.9,.18),M.paint,0,0,1.85*s,S);P3(kProf([[2.6,1.75],[-2.5,1.95],[-2.6,1.75],[2.4,1.6]],.95,.06),M.stripe,0,0,1.85*s,S);
    kVent(S,-.4,1.35,2.33*s,2.4,.45,4,0,null,SH.chrome);kRivets(S,SH.chrome,[-3.8,1.9,2.32*s],[2.0,1.9,2.32*s],8,.05);
    for(const y of [1.15,1.5])limb(KG.rod,SH.metal,[2.6,y,1.4*s],[3.1,y-.25,2.3*s],S);for(let i=0;i<4;i++)kAdd(KG.spring,SH.chrome,-2.4,1.3+i*.16,2.0*s,S,Math.PI/2);
    P3(KG.tail,M.tailM,-4.45,1.35,1.4*s,S);}
  /* low windscreen and head fairing */
  kAdd(kRBox(.08,.75,1.7,.2),SH.lens,1.5,3.0,0,S,0,0,-.55);P3(kProf([[-1.8,2.6],[-2.4,3.6],[-3.4,3.3],[-3.9,2.6]],1.0,.2),M.paint,0,0,0,S);
  /* rear: a wide flat wing like a cheese slice, twin pipes */
  P3(kProf([[-3.6,3.5],[-4.0,3.85],[-5.0,3.8],[-5.05,3.5]],5.0,.05),M.stripe,0,0,0,S);for(const s of [-1,1])P3(kTube([[-3.4,2.3,.5*s],[-3.8,3.0,.6*s],[-4.2,3.55,.6*s]],.08,12,6),SH.metal,0,0,0,S);
  for(const s of [-1,1])P3(kRBox(1.4,.9,.08,.06),M.dark,-4.4,3.5,2.5*s,S);
  for(const s of [-1,1])kLamp(S,3.55,1.5,1.0*s,.26);
  const pipes=[exhaust(S,-4.55,1.55,.55),exhaust(S,-4.55,1.55,-.55)];
  kSeat(S,-.9,2.05,SH.seat,1.7);addPlates(S,M,idx,rc,[[-1.0,1.55,2.36,.55]]);
  return {rw:[-3.0,3.0,1.25],fw:[2.9,2.75,1.0],wz:1.1,drv:[-.25,2.45],steer:[1.4,3.1],pipes,lo:[11.5,2.2,4.4,1.8],bubY:3.2,glY:9.6,top:6.6};},

/* ---------- GOUDA: a wedge of cheese with a waxed rind, holes all over and a cracker wing ---------- */
wedge(S,M,rc,idx){
  const cheese=cm('#f0b52e',.4,0,.4),hole=cm('#b47a1c',.65),cracker=cm('#d8a456',.8),crackerD=cm('#b07a36',.8);
  /* the wedge: tall at the back, sharp at the nose; a waxed rind (the player's colour) wraps the back and sides */
  const wedge=[[5.4,1.0],[5.2,1.35],[-3.9,3.95],[-4.4,3.7],[-4.5,1.1],[-4.2,.85]];
  P3(extr(wedge,4.0,.3),cheese,0,0,0,S);
  P3(kRBox(.5,3.0,4.55,.2),M.paint,-4.35,2.45,0,S);for(const s of [-1,1])P3(kRBox(9.6,.42,.2,.08),M.paint,.45,1.08,2.1*s,S);
  P3(extr([[5.0,1.32],[-3.8,3.95],[-3.9,4.12],[5.0,1.48]],4.2,.04),M.stripe,0,0,0,S);
  /* holes: recessed discs with darker walls, on the sides and the top slope */
  const holes=[[3.0,1.4,.42],[1.2,1.85,.55],[-1.0,2.45,.4],[-2.7,2.55,.62],[-.2,1.55,.3],[-3.2,1.55,.35],[2.0,1.15,.25]];
  for(const s of [-1,1])for(const [x,y,r] of holes){kAdd(new THREE.CylinderGeometry(r,r*.8,.12,22),hole,x,y,2.27*s,S,Math.PI/2);kAdd(new THREE.TorusGeometry(r,.06,6,22),cheese,x,y,2.31*s,S);}
  for(const [x,z,r] of [[2.4,.9,.35],[.4,-.8,.45],[-1.9,.6,.32],[-2.9,-1.1,.4]]){const y=1.35+(5.2-x)/9.1*2.6+.28;kAdd(new THREE.CylinderGeometry(r,r*.8,.1,20),hole,x,y,z,S,0,0,.28);}
  /* cracker rear wing with docking holes, on toothpick struts with olives */
  P3(kRBox(1.9,.18,5.4,.08),cracker,-4.6,5.0,0,S).rotation.z=.12;for(let i=0;i<10;i++)kAdd(new THREE.CylinderGeometry(.06,.06,.2,8),crackerD,-4.6+((i%2)-.5)*.8,5.08,-2.2+Math.floor(i/2)*1.1,S);
  for(const s of [-1,1]){P3(kTube([[-4.2,3.7,1.3*s],[-4.5,4.95,1.4*s]],.06,6,6),cm('#e8d2a6',.7),0,0,0,S);kAdd(new THREE.SphereGeometry(.28,14,10),cm('#3a4a1a',.3),-4.35,4.35,1.35*s,S,0,0,0,1,1.25,1);kAdd(new THREE.SphereGeometry(.1,10,8),cm('#c53b22',.4),-4.35,4.62,1.35*s,S);}
  /* nose: a chrome splitter, slim lamps in the rind */
  P3(kProf([[5.9,.7],[5.6,.95],[4.4,.95],[4.4,.7]],4.6,.05),SH.chrome,0,0,0,S);for(const s of [-1,1])kLamp(S,5.1,1.12,1.6*s,.22);
  for(const s of [-1,1])P3(KG.tail,M.tailM,-4.65,2.0,1.6*s,S);
  for(const s of [-1,1])for(const y of [1.15,1.5])limb(KG.rod,SH.metal,[2.6,y,1.4*s],[3.1,y-.25,2.35*s],S);
  const pipes=[exhaust(S,-4.75,1.35,.9),exhaust(S,-4.75,1.35,-.9)];
  kSeat(S,-1.3,2.15,SH.seat,1.8);addPlates(S,M,idx,rc,[[-2.5,3.1,2.42,.6]]);
  return {rw:[-3.0,3.0,1.3],fw:[3.1,2.8,1.05],drv:[-.6,2.55],steer:[1.3,3.4],pipes,lo:[10,2.8,4.6,2.2],bubY:3.5,glY:10,top:7.4};},

/* ---------- TOMATINO: a round tomato bubble car with a leafy crown and a stalk antenna ---------- */
tomato(S,M,rc,idx){
  const leaf=cm('#3f9a35',.45,0,.3),leafD=cm('#2c6e24',.5),stalk=cm('#4a7a2a',.55);
  /* lobed tomato body: a sphere with gentle ribs pushed in */
  const g=new THREE.SphereGeometry(3.0,56,32);const p=g.attributes.position;for(let i=0;i<p.count;i++){const x=p.getX(i),y=p.getY(i),z=p.getZ(i),a=Math.atan2(z,x),rib=1-.045*Math.pow(Math.abs(Math.cos(a*3)),.6)*(1-Math.abs(y)/3);p.setXYZ(i,x*rib*1.45,y*.86,z*rib*1.12);}g.computeVertexNormals();
  P3(g,M.paint,-.2,3.15,0,S);
  /* skirt, bumpers and wheel spats */
  P3(kRBox(8.6,.5,4.4,.24),M.dark,-.2,1.05,0,S);hrx(P3(KG.bumper,SH.chrome,4.25,1.25,0,S)).scale.set(1,1,.8);hrx(P3(KG.bumper,SH.chrome,-4.6,1.25,0,S)).scale.set(1,1,.8);
  /* bubble windscreen opening and cabin */
  const ws=kAdd(new THREE.SphereGeometry(1.7,32,16,0,Math.PI*2,0,Math.PI/2),kGlass(),1.2,4.55,0,S,0,0,-.5,1.25,.9,1.15);
  kAdd(new THREE.TorusGeometry(1.7,.1,8,40),SH.chrome,1.2,4.55,0,S,Math.PI/2,-.5,0,1.25,1.15,1);
  /* green calyx crown: five pointed leaves and a curly stalk with a bud lamp */
  const lf=new THREE.Shape();lf.moveTo(0,-.35);lf.quadraticCurveTo(1.4,-.45,2.4,0);lf.quadraticCurveTo(1.4,.45,0,.35);lf.closePath();const lg=new THREE.ExtrudeGeometry(lf,{depth:.08,bevelEnabled:true,bevelThickness:.04,bevelSize:.04,bevelSegments:2,curveSegments:12});
  for(let i=0;i<5;i++){const a=i/5*Math.PI*2+.3,m=P3(lg,i%2?leaf:leafD,-1.6,5.68,0,S);m.rotation.set(Math.PI/2,0,0);m.rotation.order='YXZ';m.rotation.y=a;m.rotation.x=Math.PI/2+.38;}
  P3(kTube([[-1.6,5.6,0],[-1.7,6.4,0],[-2.2,6.9,.1],[-2.6,6.7,.2]],.13,16,8),stalk,0,0,0,S);kAdd(new THREE.SphereGeometry(.24,14,10),SH.glowO,-2.68,6.62,.2,S);
  /* cheeky face up front: big round lamps with chrome lids, little smile grille */
  for(const s of [-1,1]){kLamp(S,3.85,2.75,1.25*s,.42);kAdd(new THREE.TorusGeometry(.45,.06,6,20,Math.PI),SH.chrome,3.95,2.95,1.25*s,S,0,Math.PI/2,0);}
  kAdd(new THREE.TorusGeometry(.6,.1,8,24,Math.PI),SH.black,4.15,2.15,0,S,Math.PI,Math.PI/2,0);
  /* side highlights: a soft sheen stripe and round porthole doors */
  for(const s of [-1,1]){kAdd(new THREE.TorusGeometry(.95,.09,8,32),SH.chrome,-.6,3.05,3.35*s,S);kAdd(new THREE.CircleGeometry(.88,28),SH.lens,-.6,3.05,3.36*s,S,0,s<0?Math.PI:0);
    P3(KG.tail,M.tailM,-4.35,2.4,1.3*s,S);}
  const pipes=[exhaust(S,-4.4,1.35,.9)];
  addPlates(S,M,idx,rc,[[1.8,2.5,3.1,.6]]);
  return {rw:[-2.75,3.0,1.2],fw:[2.75,3.0,1.2],wz:1.15,drv:[.3,4.3],steer:[1.95,4.95],pipes,lo:[9,5,6.5,3.2],bubY:4.2,bubS:1.2,glY:12,top:8.6,noCockpit:0};}
});
BODIES.push(
  {id:'delivery',name:'Pronto',desc:'A bubbly delivery van with dinner stacked on the roof. Heavy and sure-footed, slow to wind up.',st:[0,-1,0,2,1]},
  {id:'cutter',name:'Slicer',desc:'Built around a giant pizza cutter. Long, low and razor quick once it gets going.',st:[2,0,1,-1,-2]},
  {id:'wedge',name:'Gouda',desc:'A wedge of cheese with a cracker wing. Darts into corners, light on its feet.',st:[0,1,2,-1,-1]},
  {id:'tomato',name:'Tomatino',desc:'A round, bouncy tomato bubble car. Rolls over the rough stuff, a little lazy on the straights.',st:[-1,1,0,0,2]});

/* ---------- imported car models (pre-simplified and baked to compact binary; geometry is shared by every kart that uses it) ---------- */
const CAR_PACKS={"formula":{"h":{"meta":[{"n":"b_vc","v":5830,"i":21240},{"n":"b_paint","v":4072,"i":18123},{"n":"b_tail","v":62,"i":180},{"n":"l_vc","v":460,"i":2046},{"n":"l_paint","v":313,"i":1701},{"n":"l_tail","v":3,"i":3},{"n":"w0","v":2001,"i":6705},{"n":"w1","v":2240,"i":7050},{"n":"w2","v":2284,"i":7212},{"n":"w3","v":1975,"i":6732}],"wheels":[{"c":[3.657,0.887,1.939],"r":0.886,"f":1},{"c":[-4.854,0.891,1.842],"r":0.886,"f":0},{"c":[-4.854,0.891,-1.842],"r":0.886,"f":0},{"c":[3.657,0.886,-1.939],"r":0.886,"f":1}]}},"gt":{"h":{"meta":[{"n":"b_vc","v":1717,"i":13917},{"n":"b_paint","v":7313,"i":26997},{"n":"b_glass","v":166,"i":561},{"n":"b_light","v":165,"i":1803},{"n":"b_tail","v":53,"i":231},{"n":"l_vc","v":283,"i":2472},{"n":"l_paint","v":426,"i":2640},{"n":"l_glass","v":35,"i":90},{"n":"l_light","v":20,"i":162},{"n":"l_tail","v":3,"i":3},{"n":"w0","v":2520,"i":8661},{"n":"w1","v":2877,"i":9402},{"n":"w2","v":2876,"i":9402},{"n":"w3","v":2529,"i":8691}],"wheels":[{"c":[3.282,0.868,2.05],"r":0.866,"f":1},{"c":[-3.001,0.872,2.02],"r":0.872,"f":0},{"c":[-3.001,0.872,-2.02],"r":0.871,"f":0},{"c":[3.282,0.867,-2.05],"r":0.867,"f":1}]}},"hyper":{"h":{"meta":[{"n":"b_vc","v":2714,"i":12345},{"n":"b_paint","v":3116,"i":17943},{"n":"b_glass","v":245,"i":1194},{"n":"b_tail","v":327,"i":900},{"n":"b_light","v":454,"i":1389},{"n":"l_vc","v":336,"i":1410},{"n":"l_paint","v":497,"i":2115},{"n":"l_glass","v":38,"i":150},{"n":"l_light","v":25,"i":117},{"n":"w0","v":1179,"i":6693},{"n":"w1","v":1161,"i":6705},{"n":"w2","v":1139,"i":6612},{"n":"w3","v":1196,"i":6759}],"wheels":[{"c":[-3.623,0.977,2.188],"r":0.953,"f":0},{"c":[3.204,0.929,2.082],"r":0.929,"f":1},{"c":[3.204,0.929,-2.005],"r":0.929,"f":1},{"c":[-3.623,0.975,-2.045],"r":0.953,"f":0}]}},"roadster":{"h":{"meta":[{"n":"b_vc","v":4782,"i":16218},{"n":"b_glass","v":196,"i":600},{"n":"b_paint","v":3366,"i":17997},{"n":"b_light","v":192,"i":1071},{"n":"b_tail","v":75,"i":429},{"n":"l_vc","v":425,"i":1659},{"n":"l_glass","v":38,"i":60},{"n":"l_paint","v":391,"i":1797},{"n":"l_tail","v":11,"i":39},{"n":"w0","v":3296,"i":8268},{"n":"w1","v":3186,"i":7920},{"n":"w2","v":3197,"i":7974},{"n":"w3","v":3175,"i":7953}],"wheels":[{"c":[-2.254,0.78,1.338],"r":0.78,"f":0},{"c":[2.876,0.78,1.338],"r":0.78,"f":1},{"c":[-2.254,0.78,-1.338],"r":0.78,"f":0},{"c":[2.876,0.78,-1.338],"r":0.78,"f":1}]}},"tourer":{"h":{"meta":[{"n":"b_glass","v":112,"i":591},{"n":"b_paint","v":8511,"i":20976},{"n":"b_vc","v":5715,"i":21906},{"n":"b_light","v":285,"i":900},{"n":"b_tail","v":55,"i":240},{"n":"l_glass","v":34,"i":177},{"n":"l_paint","v":247,"i":1851},{"n":"l_vc","v":513,"i":2397},{"n":"w0","v":1330,"i":6768},{"n":"w1","v":1416,"i":6588},{"n":"w2","v":1416,"i":6585},{"n":"w3","v":1338,"i":6831}],"wheels":[{"c":[5.339,1.098,1.729],"r":1.093,"f":1},{"c":[-4.563,1.115,1.763],"r":1.115,"f":0},{"c":[-4.563,1.115,-1.763],"r":1.115,"f":0},{"c":[5.339,1.098,-1.73],"r":1.093,"f":1}]}},"concept":{"h":{"meta":[{"n":"b_paint","v":6370,"i":31497},{"n":"b_vc","v":2523,"i":12984},{"n":"b_glass","v":392,"i":1797},{"n":"b_light","v":250,"i":900},{"n":"b_tail","v":205,"i":897},{"n":"l_paint","v":735,"i":3039},{"n":"l_vc","v":326,"i":1215},{"n":"l_glass","v":59,"i":174},{"n":"l_tail","v":24,"i":81},{"n":"w0","v":2293,"i":10491},{"n":"w1","v":2238,"i":10554},{"n":"w2","v":2200,"i":10527},{"n":"w3","v":2239,"i":10551}],"wheels":[{"c":[3.513,0.849,2.315],"r":0.846,"f":1},{"c":[-3.743,0.906,2.363],"r":0.906,"f":0},{"c":[-3.743,0.906,-2.363],"r":0.906,"f":0},{"c":[3.513,0.849,-2.315],"r":0.846,"f":1}]}},"interceptor":{"h":{"meta":[{"n":"b_vc","v":8908,"i":15192},{"n":"b_paint","v":5560,"i":20997},{"n":"b_blue","v":92,"i":168},{"n":"b_tail","v":297,"i":696},{"n":"b_light","v":639,"i":1365},{"n":"b_glass","v":216,"i":708},{"n":"l_vc","v":205,"i":1251},{"n":"l_paint","v":394,"i":2073},{"n":"l_blue","v":24,"i":36},{"n":"l_light","v":14,"i":60},{"n":"l_glass","v":42,"i":90},{"n":"w0","v":2498,"i":6588},{"n":"w1","v":2513,"i":6651},{"n":"w2","v":2513,"i":6651},{"n":"w3","v":2498,"i":6588}],"wheels":[{"c":[-3.476,0.893,2.015],"r":0.89,"f":0},{"c":[3.276,0.852,2.159],"r":0.852,"f":1},{"c":[3.275,0.853,-2.16],"r":0.852,"f":1},{"c":[-3.476,0.892,-2.016],"r":0.89,"f":0}]}},"monster":{"h":{"meta":[{"n":"b_glass","v":477,"i":894},{"n":"b_paint","v":2074,"i":6012},{"n":"b_vc","v":7770,"i":15708},{"n":"l_glass","v":20,"i":30},{"n":"l_paint","v":777,"i":1656},{"n":"l_vc","v":666,"i":2268},{"n":"w0","v":969,"i":2949},{"n":"w1","v":791,"i":2511},{"n":"w2","v":970,"i":2826},{"n":"w3","v":785,"i":2445}],"wheels":[{"c":[-3.86,1.655,-2.466],"r":1.655,"f":0},{"c":[4.098,1.655,-2.554],"r":1.653,"f":1},{"c":[-3.861,1.655,2.554],"r":1.654,"f":0},{"c":[4.096,1.655,2.554],"r":1.652,"f":1}]}},"muscle":{"h":{"meta":[{"n":"b_tail","v":586,"i":1494},{"n":"b_light","v":439,"i":1194},{"n":"b_vc","v":3842,"i":10635},{"n":"b_paint","v":7344,"i":26997},{"n":"b_glass","v":428,"i":1497},{"n":"l_tail","v":28,"i":189},{"n":"l_light","v":31,"i":117},{"n":"l_vc","v":372,"i":1995},{"n":"l_paint","v":481,"i":2667},{"n":"l_glass","v":41,"i":147},{"n":"w0","v":3865,"i":8541},{"n":"w1","v":3885,"i":8610},{"n":"w2","v":3867,"i":8559},{"n":"w3","v":3876,"i":8577}],"wheels":[{"c":[3.603,0.897,2.009],"r":0.897,"f":1},{"c":[-3.451,0.909,2.01],"r":0.909,"f":0},{"c":[3.603,0.897,-2.009],"r":0.897,"f":1},{"c":[-3.451,0.909,-2.01],"r":0.909,"f":0}]}},"wheelset":{"h":{"meta":[{"n":"w0","v":2621,"i":15777},{"n":"w1","v":2910,"i":15525},{"n":"w2","v":2886,"i":15264},{"n":"w3","v":3177,"i":15096},{"n":"w4","v":3806,"i":15951}],"wheels":[]}},"gokart":{"h":{"meta":[{"n":"b_vc","v":2704,"i":9744},{"n":"b_paint","v":3307,"i":14658},{"n":"l_vc","v":585,"i":1722},{"n":"l_paint","v":450,"i":1803},{"n":"w0","v":1312,"i":5328},{"n":"w1","v":1312,"i":5328},{"n":"w2","v":1292,"i":5136},{"n":"w3","v":1292,"i":5136}],"wheels":[{"c":[-5.859,1.459,5.027],"r":1.459,"f":0},{"c":[-5.859,1.459,-5.027],"r":1.459,"f":0},{"c":[3.864,1.266,4.585],"r":1.121,"f":1},{"c":[3.864,1.266,-4.585],"r":1.121,"f":1}]}},"chariot":{"h":{"meta":[{"n":"b_vc","v":8840,"i":10272},{"n":"b_paint","v":4050,"i":4419},{"n":"l_vc","v":559,"i":1923},{"n":"l_paint","v":436,"i":1512},{"n":"w0","v":2629,"i":2964},{"n":"w1","v":2624,"i":2964},{"n":"w2","v":1474,"i":1698},{"n":"w3","v":1428,"i":1689}],"wheels":[{"c":[5.471,2.497,4.477],"r":2.423,"f":1},{"c":[5.471,2.497,-4.477],"r":2.423,"f":1},{"c":[-2.395,1.097,2.775],"r":1.097,"f":0},{"c":[-2.395,1.097,-2.775],"r":1.097,"f":0}]}},"hatch":{"h":{"meta":[{"n":"b_paint","v":6882,"i":23994},{"n":"b_vc","v":3763,"i":8409},{"n":"b_light","v":458,"i":900},{"n":"b_tail","v":92,"i":564},{"n":"b_glass","v":465,"i":1194},{"n":"l_paint","v":963,"i":2106},{"n":"l_vc","v":263,"i":1191},{"n":"l_light","v":25,"i":81},{"n":"l_tail","v":26,"i":180},{"n":"l_glass","v":32,"i":126},{"n":"w0","v":1672,"i":5793},{"n":"w1","v":1674,"i":5796},{"n":"w2","v":1707,"i":5958},{"n":"w3","v":1708,"i":5955}],"wheels":[{"c":[-3.342,0.864,1.896],"r":0.864,"f":0},{"c":[3.471,0.864,1.896],"r":0.864,"f":1},{"c":[-3.342,0.864,-1.911],"r":0.864,"f":0},{"c":[3.471,0.864,-1.911],"r":0.864,"f":1}]}},"coupe":{"h":{"meta":[{"n":"b_tail","v":641,"i":1512},{"n":"b_light","v":751,"i":2061},{"n":"b_vc","v":3476,"i":8559},{"n":"b_paint","v":7310,"i":25497},{"n":"b_glass","v":237,"i":840},{"n":"l_tail","v":28,"i":57},{"n":"l_light","v":43,"i":147},{"n":"l_vc","v":253,"i":1407},{"n":"l_paint","v":396,"i":2541},{"n":"l_glass","v":54,"i":90},{"n":"w0","v":2236,"i":5691},{"n":"w1","v":2229,"i":5688},{"n":"w2","v":2236,"i":5691},{"n":"w3","v":2232,"i":5691}],"wheels":[{"c":[-3.3,0.909,2.067],"r":0.909,"f":0},{"c":[3.644,0.909,2.067],"r":0.909,"f":1},{"c":[-3.3,0.909,-2.067],"r":0.909,"f":0},{"c":[3.644,0.909,-2.067],"r":0.909,"f":1}]}},"scissor":{"h":{"meta":[{"n":"b_vc","v":3563,"i":17811},{"n":"b_glass","v":399,"i":1200},{"n":"b_tail","v":167,"i":852},{"n":"b_light","v":541,"i":1116},{"n":"b_paint","v":5964,"i":26976},{"n":"l_vc","v":418,"i":2100},{"n":"l_glass","v":26,"i":117},{"n":"l_tail","v":21,"i":90},{"n":"l_paint","v":572,"i":2661},{"n":"w0","v":1926,"i":6867},{"n":"w1","v":1925,"i":6885},{"n":"w2","v":1964,"i":6894},{"n":"w3","v":1969,"i":6900}],"wheels":[{"c":[-3.654,0.895,2.073],"r":0.893,"f":0},{"c":[-3.654,0.895,-2.073],"r":0.893,"f":0},{"c":[3.096,0.83,2.176],"r":0.83,"f":1},{"c":[3.096,0.83,-2.176],"r":0.83,"f":1}]}},"suv":{"h":{"meta":[{"n":"b_vc","v":5970,"i":17076},{"n":"b_glass","v":314,"i":1374},{"n":"b_paint","v":5136,"i":23997},{"n":"b_light","v":376,"i":546},{"n":"b_tail","v":144,"i":711},{"n":"l_vc","v":429,"i":1569},{"n":"l_glass","v":38,"i":189},{"n":"l_paint","v":700,"i":2397},{"n":"l_tail","v":31,"i":156},{"n":"w0","v":1515,"i":5043},{"n":"w1","v":1517,"i":5145},{"n":"w2","v":1541,"i":5202},{"n":"w3","v":1537,"i":5223}],"wheels":[{"c":[-3.41,1.045,2.152],"r":1.045,"f":0},{"c":[4.248,1.045,2.152],"r":1.045,"f":1},{"c":[-3.407,1.045,-2.152],"r":1.045,"f":0},{"c":[4.251,1.045,-2.152],"r":1.045,"f":1}]}},"formula_hq":{"h":{"meta":[{"n":"b_vc","v":13756,"i":53205},{"n":"b_paint","v":9189,"i":45402},{"n":"b_tail","v":133,"i":450}],"wheels":[{"c":[3.657,0.887,1.939],"r":0.886,"f":1},{"c":[-4.854,0.891,1.842],"r":0.886,"f":0},{"c":[-4.854,0.891,-1.842],"r":0.886,"f":0},{"c":[3.657,0.886,-1.939],"r":0.886,"f":1}]}},"gt_hq":{"h":{"meta":[{"n":"b_vc","v":8317,"i":36126},{"n":"b_paint","v":15654,"i":67497},{"n":"b_glass","v":757,"i":2247},{"n":"b_light","v":730,"i":5133},{"n":"b_tail","v":247,"i":504}],"wheels":[{"c":[3.282,0.868,2.05],"r":0.866,"f":1},{"c":[-3.001,0.872,2.02],"r":0.872,"f":0},{"c":[-3.001,0.872,-2.02],"r":0.871,"f":0},{"c":[3.282,0.867,-2.05],"r":0.867,"f":1}]}},"hyper_hq":{"h":{"meta":[{"n":"b_vc","v":6352,"i":31326},{"n":"b_paint","v":15704,"i":67479},{"n":"b_glass","v":573,"i":2997},{"n":"b_tail","v":617,"i":2247},{"n":"b_light","v":898,"i":3000}],"wheels":[{"c":[-3.623,0.977,2.188],"r":0.953,"f":0},{"c":[3.204,0.929,2.082],"r":0.929,"f":1},{"c":[3.204,0.929,-2.005],"r":0.929,"f":1},{"c":[-3.623,0.975,-2.045],"r":0.953,"f":0}]}},"tourer_hq":{"h":{"meta":[{"n":"b_glass","v":663,"i":1494},{"n":"b_paint","v":18095,"i":52482},{"n":"b_vc","v":20105,"i":61995},{"n":"b_light","v":641,"i":2250},{"n":"b_tail","v":186,"i":597}],"wheels":[{"c":[5.339,1.098,1.729],"r":1.093,"f":1},{"c":[-4.563,1.115,1.763],"r":1.115,"f":0},{"c":[-4.563,1.115,-1.763],"r":1.115,"f":0},{"c":[5.339,1.098,-1.73],"r":1.093,"f":1}]}},"concept_hq":{"h":{"meta":[{"n":"b_paint","v":14721,"i":78744},{"n":"b_vc","v":7434,"i":33594},{"n":"b_glass","v":904,"i":4497},{"n":"b_light","v":486,"i":2250},{"n":"b_tail","v":456,"i":2244}],"wheels":[{"c":[3.513,0.849,2.315],"r":0.846,"f":1},{"c":[-3.743,0.906,2.363],"r":0.906,"f":0},{"c":[-3.743,0.906,-2.363],"r":0.906,"f":0},{"c":[3.513,0.849,-2.315],"r":0.846,"f":1}]}},"interceptor_hq":{"h":{"meta":[{"n":"b_vc","v":11387,"i":22353},{"n":"b_paint","v":11359,"i":25272},{"n":"b_blue","v":92,"i":168},{"n":"b_tail","v":582,"i":1500},{"n":"b_light","v":1136,"i":2994},{"n":"b_glass","v":216,"i":708}],"wheels":[{"c":[-3.476,0.893,2.015],"r":0.89,"f":0},{"c":[3.276,0.852,2.159],"r":0.852,"f":1},{"c":[3.275,0.853,-2.16],"r":0.852,"f":1},{"c":[-3.476,0.892,-2.016],"r":0.89,"f":0}]}},"gokart_hq":{"h":{"meta":[{"n":"b_vc","v":4836,"i":21009},{"n":"b_paint","v":4457,"i":21162}],"wheels":[{"c":[-5.859,1.459,5.027],"r":1.459,"f":0},{"c":[-5.859,1.459,-5.027],"r":1.459,"f":0},{"c":[3.864,1.266,4.585],"r":1.121,"f":1},{"c":[3.864,1.266,-4.585],"r":1.121,"f":1}]}},"hatch_hq":{"h":{"meta":[{"n":"b_paint","v":9131,"i":29916},{"n":"b_vc","v":16205,"i":34485},{"n":"b_light","v":792,"i":1734},{"n":"b_tail","v":316,"i":1830},{"n":"b_glass","v":928,"i":2994}],"wheels":[{"c":[-3.342,0.864,1.896],"r":0.864,"f":0},{"c":[3.471,0.864,1.896],"r":0.864,"f":1},{"c":[-3.342,0.864,-1.911],"r":0.864,"f":0},{"c":[3.471,0.864,-1.911],"r":0.864,"f":1}]}},"scissor_hq":{"h":{"meta":[{"n":"b_vc","v":14024,"i":44982},{"n":"b_glass","v":843,"i":2994},{"n":"b_tail","v":1614,"i":2976},{"n":"b_light","v":1815,"i":3747},{"n":"b_paint","v":14056,"i":67494}],"wheels":[{"c":[-3.654,0.895,2.073],"r":0.893,"f":0},{"c":[-3.654,0.895,-2.073],"r":0.893,"f":0},{"c":[3.096,0.83,2.176],"r":0.83,"f":1},{"c":[3.096,0.83,-2.176],"r":0.83,"f":1}]}},"suv_hq":{"h":{"meta":[{"n":"b_vc","v":17161,"i":47013},{"n":"b_glass","v":1860,"i":3747},{"n":"b_paint","v":12001,"i":59997},{"n":"b_light","v":1558,"i":2652},{"n":"b_tail","v":706,"i":1212}],"wheels":[{"c":[-3.41,1.045,2.152],"r":1.045,"f":0},{"c":[4.248,1.045,2.152],"r":1.045,"f":1},{"c":[-3.407,1.045,-2.152],"r":1.045,"f":0},{"c":[4.251,1.045,-2.152],"r":1.045,"f":1}]}}};
const CAR_CLS=['paint','dark','stripe','tail','light','glass','carbon','metal','rubber','seat','chrome','rim','disc','caliper','blue','gunmetal','green','red','bluem','bronze','white'];
/* physically based finish per part: colour, roughness, metalness, clearcoat */
const CAR_PBR={paint:['#ffffff',.36,.5,1],dark:['#161618',.36,.25,1],stripe:['#ffffff',.36,.5,1],tail:['#ff2a1a',.4,0,0],light:['#ffffff',.2,0,0],glass:['#0b0d10',.05,0,1],
  carbon:['#161618',.36,.25,1],metal:['#76777d',.32,.9,0],rubber:['#121212',.9,0,0],seat:['#1c1918',.8,0,0],chrome:['#e9e9ee',.1,1,0],rim:['#b5b7be',.24,.95,0],disc:['#58595d',.45,.85,0],caliper:['#c8321e',.35,.2,.8],blue:['#2a5bff',.3,0,0],gunmetal:['#3b3e44',.26,.9,.4],green:['#3f9a1a',.34,.6,.8],red:['#c0180c',.3,.5,.9],bluem:['#1d7fe6',.22,.85,.6],bronze:['#8a6232',.3,.95,.3],white:['#eeeeee',.3,0,.9]};
const CAR_COL=Object.fromEntries(Object.entries(CAR_PBR).map(([k,v])=>[k,v[0]]));
const carPbrTex=(()=>{const d=new Uint8Array(32*4);CAR_CLS.forEach((n,i)=>{const p=CAR_PBR[n];d[i*4]=p[3]*255;d[i*4+1]=p[1]*255;d[i*4+2]=p[2]*255;d[i*4+3]=255;});
  const t=new THREE.DataTexture(d,32,1,THREE.RGBAFormat);t.magFilter=t.minFilter=THREE.NearestFilter;t.generateMipmaps=false;t.needsUpdate=true;return t;})();
const CARGEO=new Set();SH.carVC=new THREE.MeshPhysicalMaterial({vertexColors:true,roughness:1,metalness:1,roughnessMap:carPbrTex,metalnessMap:carPbrTex,clearcoat:1,clearcoatMap:carPbrTex,clearcoatRoughness:.08,envMapIntensity:1.1});SHSET.add(SH.carVC);
function carGeos(id){const p=CAR_PACKS[id];if(p.g)return p.g;const bin=p.b?new Uint8Array(p.b):Uint8Array.from(atob(p.d),c=>c.charCodeAt(0)),buf=bin.buffer,cc=CAR_CLS.map(n=>new THREE.Color(CAR_COL[n]));let o=0;const g={};
  for(const m of p.h.meta){const v=m.v,pos=new Int16Array(buf,o,v*3);o+=v*6;const nrm=new Int8Array(buf,o,v*3);o+=v*3;const cls=new Uint8Array(buf,o,v);o+=v;const ao=new Uint8Array(buf,o,v);o+=v;if(o%2)o++;const idx=new Uint16Array(buf,o,m.i);o+=m.i*2;while(o%4)o++;
    const Pp=new Float32Array(v*3),Nn=new Float32Array(v*3);for(let i=0;i<v*3;i++){Pp[i]=pos[i]/1000;Nn[i]=nrm[i]/127;}
    const geo=new THREE.BufferGeometry();geo.setAttribute('position',new THREE.BufferAttribute(Pp,3));geo.setAttribute('normal',new THREE.BufferAttribute(Nn,3));
    const isVC=m.n.endsWith('vc')||m.n[0]==='w';if(isVC||m.n.endsWith('paint')){const C=new Float32Array(v*3),U=new Float32Array(v*2);for(let i=0;i<v;i++){const c=isVC?cc[cls[i]]:cc[0],a=ao[i]/255;C[i*3]=c.r*a;C[i*3+1]=c.g*a;C[i*3+2]=c.b*a;U[i*2]=(cls[i]+.5)/32;U[i*2+1]=.5;}geo.setAttribute('color',new THREE.BufferAttribute(C,3));if(isVC)geo.setAttribute('uv',new THREE.BufferAttribute(U,2));}
    geo.setIndex(new THREE.BufferAttribute(new Uint16Array(idx),1));geo.computeBoundingSphere();CARGEO.add(geo);g[m.n]=geo;}
  p.d=null;p.b=null;p.g=g;return g;}
let HQB=false;let LODM=0,LODF=200;
function carBody(id,M,B){const g=carGeos(HQB&&CAR_PACKS[id+'_hq']?id+'_hq':id);M.carPaint=new THREE.MeshPhysicalMaterial({color:M.paint.color.clone(),vertexColors:true,metalness:.5,roughness:.34,clearcoat:1,clearcoatRoughness:.04,envMapIntensity:1.2});
  M.blue=new THREE.MeshStandardMaterial({color:'#2a5bff',emissive:'#2a5bff',emissiveIntensity:2});const mats={paint:M.carPaint,tail:M.tailM,light:SH.carLight,glass:SH.carGlass,vc:SH.carVC,blue:M.blue};
  for(const k in g){if(!k.startsWith('b_'))continue;const me=new THREE.Mesh(g[k],mats[k.slice(2)]);me.castShadow=k!=='b_glass';me.receiveShadow=true;B.add(me);if(k==='b_paint')M.paintMesh=me;}}
Object.assign(BODY_FN,{
  hatch(S,M,rc,idx,B){carBody('hatch',M,B);return {car:'hatch',fit:{roof:FITQ.hatch[0],belt:FITQ.hatch[1],lean:.2,smax:.3},belt:FITQ.hatch[1],numPos:[.2,1.2],rw:[-3.34,1.9,.864],fw:[3.47,1.9,.864],wz:1.3,drv:[FITQ.hatch[2],FITQ.hatch[3],-.8],drvS:.3,noCockpit:1,pipes:[[-5.85,.7,0]],bubY:2.6,bubS:1.1,glY:8.3,top:3.7};},
  suv(S,M,rc,idx,B){carBody('suv',M,B);return {car:'suv',fit:{roof:FITQ.suv[0],belt:FITQ.suv[1],lean:.12,smax:.34},belt:FITQ.suv[1],numPos:[.2,1.7],rw:[-3.41,2.15,1.045],fw:[4.25,2.15,1.045],wz:1.3,drv:[FITQ.suv[2],FITQ.suv[3],-.8],drvS:.34,noCockpit:1,pipes:[[-6.65,.75,.95],[-6.65,.75,-.95]],bubY:3.3,bubS:1.3,glY:9.6,top:4.9};},
  coupe(S,M,rc,idx,B){carBody('coupe',M,B);return {car:'coupe',fit:{roof:FITQ.coupe[0],belt:FITQ.coupe[1],lean:.3,smax:.3},belt:FITQ.coupe[1],numPos:[.2,1.2],rw:[-3.3,2.07,.909],fw:[3.64,2.07,.909],wz:1.3,drv:[FITQ.coupe[2],FITQ.coupe[3],-.8],drvS:.3,noCockpit:1,pipes:[[-6.05,.75,.8],[-6.05,.75,-.8]],bubY:2.6,bubS:1.15,glY:8.2,top:3.5};},
  scissor(S,M,rc,idx,B){carBody('scissor',M,B);return {car:'scissor',fit:{roof:FITQ.scissor[0],belt:FITQ.scissor[1],lean:.42,smax:.27},belt:FITQ.scissor[1],numPos:[.1,1.0],rw:[-3.65,2.07,.893],fw:[3.1,2.18,.83],wz:1.3,drv:[FITQ.scissor[2],FITQ.scissor[3],-.75],drvS:.27,noCockpit:1,pipes:[[-6.15,1.25,0]],bubY:2.3,bubS:1.1,glY:7.6,top:2.8};},
  gokart(S,M,rc,idx,B){carBody('gokart',M,B);return {car:'gokart',ow:1,belt:2,numPos:[4.6,1.6],rw:[-5.86,5.03,1.459],fw:[3.86,4.58,1.121],wz:1.2,drv:[-1.8,1.05,0],drvS:.56,noCockpit:1,pipes:[[-7.6,1.6,1.6]],bubY:3.6,bubS:1.3,glY:10,top:7};},
  chariot(S,M,rc,idx,B){carBody('chariot',M,B);return {car:'chariot',ow:1,belt:2,numPos:[2,2],rw:[-2.4,2.78,1.097],fw:[5.47,4.48,2.42],wz:1.2,drv:[0,2,0],drvS:.55,noCockpit:1,pipes:[[-7.6,2.6,1.4],[-7.6,2.6,-1.4]],bubY:4,bubS:1.35,glY:11,top:8};},
  monster(S,M,rc,idx,B){carBody('monster',M,B);return {car:'monster',ow:1,fit:{roof:5.8,belt:4.6,lean:.12,smax:.36},belt:4.6,numPos:[.6,3.6],rw:[-3.86,2.55,1.655],fw:[4.1,2.55,1.653],wz:1.35,drv:[-.7,3.6,-.85],drvS:.36,noCockpit:1,pipes:[[-7.1,2.2,.7],[-7.1,2.2,-.7]],bubY:4.2,bubS:1.45,glY:11,top:6.6};},
  muscle(S,M,rc,idx,B){carBody('muscle',M,B);return {car:'muscle',fit:{roof:3.3,belt:2.45,lean:.25,smax:.3},belt:2.45,numPos:[.3,1.35],rw:[-3.45,2.01,.909],fw:[3.6,2.01,.897],wz:1.3,drv:[-.7,.75,-.82],drvS:.3,noCockpit:1,pipes:[[-6.15,.72,.6],[-6.15,.72,-.6]],bubY:2.6,bubS:1.1,glY:8.2,top:3.7};},
  hyper(S,M,rc,idx,B){carBody('hyper',M,B);return {car:'hyper',fit:{open:1,rim:1.6,s:.32,lean:.3},belt:1.55,numPos:[.2,1.0],rw:[-3.62,2.1,.953],fw:[3.2,2.04,.929],wz:1.3,drv:[.1,.6,-.8],drvS:.3,noCockpit:1,pipes:[[-5.4,.95,0]],bubY:2.4,bubS:1.05,glY:8,top:3.3};},
  roadster(S,M,rc,idx,B){carBody('roadster',M,B);return {car:'roadster',fit:{open:1,rim:1.85,s:.27},belt:1.75,numPos:[.4,1.15],rw:[-2.25,1.34,.78],fw:[2.88,1.34,.78],wz:1.1,drv:[-1.0,.72,.7],drvS:.34,noCockpit:1,pipes:[[-4.5,.55,.5]],bubY:2.4,bubS:.9,glY:7.6,top:3.6};},
  tourer(S,M,rc,idx,B){carBody('tourer',M,B);return {car:'tourer',fit:{roof:4.35,belt:3.0,lean:0,smax:.32},belt:3.0,numPos:[-.6,2.2],rw:[-4.56,1.76,1.115],fw:[5.34,1.73,1.093],wz:1.1,drv:[-1.2,1.35,.75],drvS:.4,noCockpit:1,pipes:[[-6.8,.9,.7]],bubY:3.0,bubS:1.2,glY:9.8,top:5};},
  concept(S,M,rc,idx,B){carBody('concept',M,B);return {car:'concept',fit:{roof:2.58,belt:1.72,lean:.4,smax:.28},belt:1.72,numPos:[.3,1.1],rw:[-3.74,2.36,.906],fw:[3.51,2.31,.846],wz:1.3,drv:[1.0,.5,0],drvS:.3,noCockpit:1,pipes:[[-6.1,1.0,0]],bubY:2.4,bubS:1.1,glY:8,top:3.1};},
  interceptor(S,M,rc,idx,B){carBody('interceptor',M,B);return {car:'interceptor',fit:{roof:2.8,belt:2.05,lean:.35,smax:.27},belt:2.05,numPos:[.2,1.25],flash:1,rw:[-3.48,2.02,.89],fw:[3.28,2.16,.852],wz:1.3,drv:[0,.55,-.8],drvS:.32,noCockpit:1,pipes:[[-5.6,.9,.4],[-5.6,.9,-.4]],bubY:2.5,bubS:1.05,glY:8,top:3.3};},
  formula(S,M,rc,idx,B){carBody('formula',M,B);return {car:'formula',ow:1,fit:{open:1,rim:1.75,s:.36},belt:1.15,numPos:[-.9,1.25],rw:[-4.852,1.841,.885],fw:[3.655,1.938,.886],wz:1.3,drv:[.35,.7,0],drvS:.47,noCockpit:1,pipes:[[-6.55,1.15,0]],bubY:2.6,bubS:1.15,glY:8.6,top:3.8};},
  gt(S,M,rc,idx,B){carBody('gt',M,B);return {car:'gt',fit:{open:1,rim:1.8,s:.4},belt:1.63,numPos:[.35,1.05],rw:[-3.005,2.023,.873],fw:[3.286,2.052,.868],wz:1.3,drv:[.25,.5,-.85],drvS:.5,noCockpit:1,pipes:[[-5.95,.85,.9],[-5.95,.85,-.9]],bubY:2.7,bubS:1.1,glY:8.6,top:4.2};}});
/* ---------- liveries: multi-colour themes painted procedurally onto the car bodies ---------- */
const LIVERIES=[
  {id:'pep',cat:'pizza',name:'Pepperoni Racer',pat:1,A:'#c8261b',B:'#fff4dc',C:'#2a1a14',m:.45,r:.3},
  {id:'marg',cat:'pizza',name:'Margherita',pat:3,A:'#2f9a3e',B:'#f4efe4',C:'#d6301e',m:.35,r:.3},
  {id:'mid',cat:'super',name:'Midnight Carbon',pat:10,A:'#0d0e12',B:'#24262b',C:'#d9a84a',m:.6,r:.24},
  {id:'flame',cat:'street',name:'Wood-Fire Flames',pat:4,A:'#121214',B:'#ff4a12',C:'#ffd24a',m:.5,r:.26},
  {id:'check',cat:'classic',name:'Checkered Flag',pat:5,A:'#f4f4f2',B:'#111214',C:'#e0452c',m:.3,r:.3},
  {id:'wave',cat:'wild',name:'Ocean Wave',pat:6,A:'#2f7fd8',B:'#0d2f5a',C:'#f4f4f2',m:.5,r:.28},
  {id:'camo',cat:'street',name:'Basil Camo',pat:7,A:'#55703c',B:'#2f4a26',C:'#9a9a62',m:.05,r:.62},
  {id:'sunset',cat:'wild',name:'Sunset Fade',pat:8,A:'#ff8a1f',B:'#6d2bb0',C:'#ffffff',m:.55,r:.26},
  {id:'neon',cat:'wild',name:'Neon Night',pat:9,A:'#160c2a',B:'#ff3fa4',C:'#3ff0ff',m:.4,r:.3},
  {id:'mozz',cat:'pizza',name:'Liquid Mozz',pat:1,A:'#d9dce2',B:'#ff8fb8',C:'#ffffff',m:1,r:.12},
  {id:'skyorange',cat:'endure',name:'Sky & Orange',pat:15,A:'#8ec8e8',B:'#ff7a1a',C:'#1b2a3a',m:.35,r:.3,num:1},
  {id:'riviera',cat:'endure',name:'Riviera Stripes',pat:16,A:'#f4f4f2',B:'#0f2a5c',C:'#d6301e',m:.35,r:.28},
  {id:'french',cat:'classic',name:'French Blue',pat:12,A:'#1f4fa8',B:'#f4f4f2',C:'#f4f4f2',m:.4,r:.28,num:1},
  {id:'rosso',cat:'f1',name:'Rosso Corsa',pat:11,A:'#c8101a',B:'#f7d21a',C:'#141416',m:.4,r:.26,num:1},
  {id:'silver',cat:'f1',name:'Silver Arrow',pat:2,A:'#c7cbd1',B:'#16181c',C:'#00c2a8',m:.95,r:.16},
  {id:'papaya',cat:'f1',name:'Papaya',pat:11,A:'#ff7f11',B:'#2f7fd8',C:'#141416',m:.35,r:.28,num:1},
  {id:'retro',cat:'classic',name:'70s Stripes',pat:16,A:'#f3e6c6',B:'#7a2a12',C:'#ff8a1f',m:.25,r:.34},
  {id:'diag',cat:'street',name:'Truck Racing',pat:17,A:'#f7c948',B:'#111214',C:'#e0452c',m:.35,r:.3,num:1},
  {id:'scallop',cat:'street',name:'Hot Rod Scallops',pat:18,A:'#1a1c22',B:'#7b2fd8',C:'#f7c948',m:.6,r:.22},
  {id:'desert',cat:'street',name:'Desert Runner',pat:19,A:'#d8b47a',B:'#1d2a36',C:'#e0452c',m:.2,r:.45,num:1},
  {id:'pixel',cat:'wild',name:'Digital Camo',pat:20,A:'#7a8a6a',B:'#3f4a36',C:'#c9c2a0',m:.05,r:.6},
  {id:'bolt',cat:'wild',name:'Lightning',pat:21,A:'#101216',B:'#f7d21a',C:'#f4f4f2',m:.45,r:.26},
  {id:'bull',cat:'f1',name:'Midnight Charger',pat:11,A:'#0b1a3e',B:'#d6301e',C:'#f7c948',m:.4,r:.26,num:1},
  {id:'verdant',cat:'f1',name:'British Racing',pat:2,A:'#00594f',B:'#0b0c0e',C:'#c8f000',m:.55,r:.22},
  {id:'pinkblue',cat:'f1',name:'Pink & Blue',pat:11,A:'#f598c3',B:'#2a5bff',C:'#141416',m:.4,r:.26,num:1},
  {id:'blackgold',cat:'f1',name:'Black & Gold',pat:26,A:'#0d0d0f',B:'#d9a84a',C:'#d9a84a',m:.45,r:.22,num:1},
  {id:'mantis',cat:'super',name:'Verde Mantis',pat:25,A:'#77c41b',B:'#111214',C:'#f4f4f2',m:.55,r:.2},
  {id:'giallo',cat:'super',name:'Giallo',pat:26,A:'#ffcc00',B:'#111214',C:'#111214',m:.45,r:.22},
  {id:'chrome',cat:'super',name:'Chrome Fade',pat:27,A:'#7f8794',B:'#eef1f5',C:'#2a2d33',m:1,r:.1},
  {id:'hexcarbon',cat:'super',name:'Hex Carbon',pat:28,A:'#16171b',B:'#2c2e34',C:'#e0452c',m:.35,r:.28},
  {id:'blunotte',cat:'super',name:'Blu Notte',pat:25,A:'#1f3fbf',B:'#0a0b10',C:'#ffffff',m:.65,r:.18},
  {id:'hybrid',cat:'endure',name:'Hybrid Prototype',pat:24,A:'#f4f4f2',B:'#e0452c',C:'#111214',m:.35,r:.28,num:1},
  {id:'nightracer',cat:'endure',name:'24 Hour Night',pat:9,A:'#0b0d14',B:'#ff2f8f',C:'#ffd24a',m:.4,r:.26,num:1},
  {id:'lemansgold',cat:'endure',name:'Gold Endurance',pat:15,A:'#101114',B:'#d9a84a',C:'#f4f4f2',m:.45,r:.24,num:1},
  {id:'tiger',cat:'street',name:'Tiger',pat:22,A:'#ff8a1f',B:'#141414',C:'#f4f4f2',m:.3,r:.3},
  {id:'raid',cat:'street',name:'Rally Raid',pat:19,A:'#f4f4f2',B:'#e0452c',C:'#2f7fd8',m:.25,r:.38,num:1},
  {id:'halftone',cat:'street',name:'Halftone',pat:23,A:'#f7c948',B:'#1a1c22',C:'#e0452c',m:.3,r:.3},
  {id:'aurora',cat:'wild',name:'Aurora',pat:8,A:'#20e3b2',B:'#5a2bd8',C:'#ffffff',m:.6,r:.2},
  {id:'candy',cat:'wild',name:'Candy Cane',pat:9,A:'#f4f4f2',B:'#e0452c',C:'#3f9a35',m:.3,r:.26},
  {id:'hawaiian',cat:'pizza',name:'Hawaiian',pat:3,A:'#f7c948',B:'#ff7a9a',C:'#3f9a35',m:.3,r:.3},
  {id:'fourcheese',cat:'pizza',name:'Four Cheese',pat:20,A:'#f6d36b',B:'#f4ead2',C:'#e7b84a',m:.15,r:.45},
  {id:'gp',name:'Grand Prix',only:'formula',pat:11,A:'#0b1b3a',B:'#f7c948',C:'#e0452c',m:.4,r:.28,num:1},
  {id:'endure',name:'Endurance',only:'gt',pat:9,A:'#f4f4f2',B:'#e0452c',C:'#2f7fd8',m:.35,r:.3,num:1},
  {id:'volt',name:'Electric',only:'hyper',pat:2,A:'#c9ced6',B:'#101216',C:'#3ff0ff',m:.85,r:.2},
  {id:'heritage',name:'Heritage Green',only:'roadster',pat:12,A:'#1f4a32',B:'#f4ecd6',C:'#f4ecd6',m:.35,r:.34,num:1},
  {id:'royal',name:'Royal Two-Tone',only:'tourer',pat:2,A:'#5a1424',B:'#101012',C:'#d9a84a',m:.45,r:.28},
  {id:'stealth',name:'Stealth Matte',only:'concept',pat:13,A:'#3a3d42',B:'#ff7a1a',C:'#151619',m:.15,r:.72},
  {id:'pursuit',name:'Pursuit',only:'interceptor',pat:14,A:'#101114',B:'#f4f4f2',C:'#2a5bff',m:.45,r:.28},
  {id:'pizzeria',name:'Pizzeria',only:'classic',pat:0,A:'#2f9a3e',B:'#f4efe4',C:'#d6301e',m:.3,r:.3},
  {id:'mud',name:'Mud Pit',only:'monster',pat:0,A:'#6b4a2a',B:'#f7c948',C:'#2a1c12',m:.1,r:.6},
  {id:'space',name:'Space Race',only:'rocket',pat:0,A:'#f4f4f2',B:'#2f7fd8',C:'#1a1b22',m:.4,r:.3},
  {id:'woodfire',name:'Wood-Fired',only:'oven',pat:0,A:'#1a1412',B:'#ff8a1f',C:'#5a3a24',m:.2,r:.5},
  {id:'f_night',name:'Night Race',only:'formula',pat:24,A:'#101216',B:'#ff2d6a',C:'#f4f4f2',m:.5,r:.24,dec:3,word:5},
  {id:'f_papaya',name:'Papaya Works',only:'formula',pat:23,A:'#ff7a12',B:'#1f9be8',C:'#101216',m:.4,r:.26,dec:4,word:6,num:1},
  {id:'gt_gulfish',name:'Sky & Orange',only:'gt',pat:2,A:'#7ec4ea',B:'#ff7a1a',C:'#1a1b22',m:.35,r:.28,dec:5,word:2,num:1},
  {id:'gt_rally',name:'Rally Spec',only:'gt',pat:16,A:'#f4f4f2',B:'#1d3f80',C:'#e0452c',m:.3,r:.32,dec:2,word:0},
  {id:'hy_aurora',name:'Aurora Volt',only:'hyper',pat:25,A:'#0c1420',B:'#3ff0ff',C:'#b26bff',m:.7,r:.2,dec:7,word:5},
  {id:'hy_lava',name:'Lava Core',only:'hyper',pat:4,A:'#141012',B:'#ff4a12',C:'#ffd23a',m:.5,r:.26,dec:1,word:-1},
  {id:'rd_cream',name:'Seaside Cream',only:'roadster',pat:22,A:'#f1e6c8',B:'#c8261b',C:'#2a2a2a',m:.25,r:.32,dec:0,word:1},
  {id:'rd_racing',name:'Club Racer',only:'roadster',pat:1,A:'#1d3f80',B:'#f4f4f2',C:'#e0452c',m:.35,r:.3,dec:5,word:6,num:1},
  {id:'tr_gold',name:'Gilded Age',only:'tourer',pat:26,A:'#141414',B:'#d9a84a',C:'#5a1424',m:.6,r:.24,dec:6,word:-1},
  {id:'tr_ivory',name:'Ivory Saloon',only:'tourer',pat:2,A:'#efe8d6',B:'#2a3a2a',C:'#b08a4a',m:.3,r:.3,dec:6,word:3},
  {id:'cn_neon',name:'Neon Blade',only:'concept',pat:21,A:'#0e0f12',B:'#41ff8a',C:'#18191d',m:.3,r:.32,dec:3,word:5},
  {id:'cn_pearl',name:'Pearl Shard',only:'concept',pat:28,A:'#f2f3f6',B:'#9aa4b8',C:'#2a2d33',m:.7,r:.18,dec:4,word:-1},
  {id:'ic_sheriff',name:'Sheriff',only:'interceptor',pat:2,A:'#f4f4f2',B:'#101114',C:'#d9a84a',m:.4,r:.28,dec:2,word:7},
  {id:'ic_ghost',name:'Ghost Unit',only:'interceptor',pat:13,A:'#2a2d33',B:'#7f8a99',C:'#101114',m:.2,r:.65,dec:6,word:-1},
  {id:'mu_stripes',name:'Twin Stripe',only:'muscle',pat:1,A:'#1d3f80',B:'#f4f4f2',C:'#101216',m:.45,r:.26,dec:2,word:0},
  {id:'mu_hugger',name:'Grabber Orange',only:'muscle',pat:12,A:'#ff6a12',B:'#101216',C:'#f4f4f2',m:.4,r:.28,dec:1,word:5,num:1},
  {id:'mu_shadow',name:'Shadow Black',only:'muscle',pat:24,A:'#0f1012',B:'#c8261b',C:'#2a2c30',m:.55,r:.22,dec:3,word:-1},
  {id:'mt_bigfoot',name:'Big Wheel Blue',only:'monster',pat:4,A:'#1d3f80',B:'#ffd23a',C:'#101216',m:.3,r:.32,dec:1,word:0},
  {id:'mt_dino',name:'Pizza Rex',only:'monster',pat:22,A:'#3f9a35',B:'#f7c948',C:'#1a1b14',m:.2,r:.4,dec:0,word:3},
  {id:'gk_team',name:'Kart Team',only:'gokart',pat:16,A:'#f4f4f2',B:'#e0452c',C:'#1d3f80',m:.3,r:.3,dec:4,word:6,num:1},
  {id:'gk_lime',name:'Lime Sprint',only:'gokart',pat:23,A:'#9be22a',B:'#101216',C:'#f4f4f2',m:.3,r:.3,dec:3,word:5},
  {id:'gk_basil',name:'Basil Cup',only:'gokart',pat:3,A:'#2f9a3e',B:'#f4efe4',C:'#d6301e',m:.25,r:.32,dec:0,word:1,num:1},
  {id:'ch_brass',name:'Brass Furnace',only:'chariot',pat:20,A:'#b07a30',B:'#ffd88a',C:'#3a2414',m:.75,r:.26,dec:7,word:1},
  {id:'ch_royal',name:'Royal Chariot',only:'chariot',pat:26,A:'#3a1450',B:'#d9a84a',C:'#1a0f20',m:.5,r:.26,dec:6,word:-1},
  {id:'cl_retro',name:'Retro Diner',only:'classic',pat:22,A:'#7ec4ea',B:'#f4f4f2',C:'#e0452c',m:.3,r:.3},
  {id:'rk_mars',name:'Red Planet',only:'rocket',pat:4,A:'#c8261b',B:'#ffd23a',C:'#1a1b22',m:.4,r:.3},
  {id:'ov_stone',name:'Stone Hearth',only:'oven',pat:20,A:'#8a7f72',B:'#ff8a1f',C:'#3a322c',m:.1,r:.7},
  {id:'sunset',cat:'street',name:'Sunset Fade',pat:25,A:'#ff6a3a',B:'#ffd23a',C:'#5a1a6a',m:.45,r:.24,dec:2,word:0},
  {id:'arctic',cat:'endure',name:'Arctic Camo',pat:4,A:'#e8eef4',B:'#9fb3c8',C:'#3a4a5a',m:.15,r:.55,dec:5,word:5},
  {id:'racingred',cat:'super',name:'Corsa Red',pat:2,A:'#c8100c',B:'#f4f4f2',C:'#101012',m:.55,r:.22,dec:2,word:-1},
  {id:'teal',cat:'f1',name:'Teal Arrow',pat:23,A:'#0aa6a0',B:'#101216',C:'#f4f4f2',m:.5,r:.24,dec:4,word:6,num:1},
  {id:'lowrider',cat:'street',name:'Lowrider Candy',pat:26,A:'#7a1aa8',B:'#ffd23a',C:'#ff4fa8',m:.7,r:.18,dec:2,word:7},
  {id:'graffiti',cat:'wild',name:'Street Art',pat:21,A:'#1d1f24',B:'#ff4fa8',C:'#3ff0ff',m:.3,r:.4,dec:3,word:4},
  {id:'calzone',cat:'pizza',name:'Calzone Gold',pat:20,A:'#e2a64a',B:'#fff2c8',C:'#8a4a1a',m:.25,r:.4,dec:0,word:2},
  {id:'veggie',cat:'pizza',name:'Garden Veggie',pat:22,A:'#3f9a35',B:'#ff6a3a',C:'#f7c948',m:.25,r:.35,dec:0,word:3},
  {id:'hb_rally',name:'Rally Sedan',only:'hatch',pat:16,A:'#f4f4f2',B:'#e0452c',C:'#1d3f80',m:.3,r:.3,dec:2,word:0,num:1},
  {id:'hb_lime',name:'Lime Rush',only:'hatch',pat:12,A:'#9bdc28',B:'#101216',C:'#f4f4f2',m:.4,r:.28,dec:1,word:5},
  {id:'hb_city',name:'City Pop',only:'hatch',pat:22,A:'#2fb4ff',B:'#ffd23a',C:'#1a1b22',m:.3,r:.3,dec:7,word:1},
  {id:'sv_onyx',name:'Black Tie',only:'suv',pat:24,A:'#0f1012',B:'#c9ced6',C:'#2a2c30',m:.65,r:.18,dec:6,word:-1},
  {id:'sv_pearl',name:'Pearl Estate',only:'suv',pat:2,A:'#f2f1ec',B:'#d9a84a',C:'#2a2d33',m:.6,r:.2,dec:4,word:3},
  {id:'sv_safari',name:'Safari',only:'suv',pat:9,A:'#c8a46a',B:'#3a5a2a',C:'#2a2116',m:.25,r:.45,dec:5,word:2},
  {id:'cp_racing',name:'Racing Green',only:'coupe',pat:1,A:'#123a24',B:'#d9a84a',C:'#0c1410',m:.55,r:.22,dec:6,word:-1},
  {id:'cp_bordeaux',name:'Bordeaux',only:'coupe',pat:26,A:'#4a0e1c',B:'#e8dcc0',C:'#16080c',m:.6,r:.2,dec:4,word:3},
  {id:'cp_silver',name:'Silver Arrow',only:'coupe',pat:2,A:'#c9ced6',B:'#1d3f80',C:'#2a2d33',m:.85,r:.16,dec:2,word:0,num:1},
  {id:'sc_verde',name:'Verde Strike',only:'scissor',pat:21,A:'#6fe02a',B:'#101216',C:'#18191d',m:.45,r:.24,dec:3,word:5},
  {id:'sc_inferno',name:'Inferno',only:'scissor',pat:4,A:'#ff5a12',B:'#141012',C:'#ffd23a',m:.5,r:.24,dec:1,word:-1},
  {id:'sc_hex',name:'Carbon Hex',only:'scissor',pat:13,A:'#22252b',B:'#ffb21a',C:'#0e0f12',m:.3,r:.5,dec:7,word:2,num:1}];
const livOf=id=>LIVERIES.find(l=>l.id===id)||null;
const LIV_CATS=[['all','All'],['sig','\u2605 Signature'],['f1','Formula'],['super','Supercar'],['endure','Endurance'],['classic','Classic'],['street','Street & Truck'],['wild','Wild'],['pizza','Pizza']];let livCat='all';
const liveriesFor=bodyId=>LIVERIES.filter(l=>!l.only||l.only===bodyId);
const decTex=(()=>{const W=1024,H=256,c=cnv(W,H),g=c.getContext('2d'),C=128;g.lineJoin='round';
  const ink=(f)=>{g.save();f();g.restore();};
  const cell=(i,row,draw)=>{g.save();g.translate(i*C+C/2,row*C+C/2);draw();g.restore();};
  const fillS=(path)=>{g.lineWidth=10;g.strokeStyle='rgb(0,0,0)';g.stroke(path);g.fillStyle='rgb(255,255,255)';g.fill(path);};
  // row 0: emblems (white shape, dark outline)
  cell(0,0,()=>{const p=new Path2D();p.moveTo(0,-50);p.lineTo(44,40);p.quadraticCurveTo(0,58,-44,40);p.closePath();fillS(p);g.fillStyle='rgb(0,0,0)';for(const [x,y] of [[0,-8],[-14,22],[16,24]]){g.beginPath();g.arc(x,y,8,0,7);g.fill();}});/* pizza slice */
  cell(1,0,()=>{const p=new Path2D();p.moveTo(-40,48);p.bezierCurveTo(-56,0,-10,-10,-14,-56);p.bezierCurveTo(10,-30,4,-6,22,-26);p.bezierCurveTo(30,-4,58,10,40,48);p.closePath();fillS(p);});/* flame */
  cell(2,0,()=>{const p=new Path2D();for(let i=0;i<10;i++){const a=i/10*Math.PI*2-Math.PI/2,r=i%2?22:54;i?p.lineTo(Math.cos(a)*r,Math.sin(a)*r):p.moveTo(Math.cos(a)*r,Math.sin(a)*r);}p.closePath();fillS(p);});/* star */
  cell(3,0,()=>{const p=new Path2D();p.moveTo(12,-56);p.lineTo(-30,6);p.lineTo(-2,6);p.lineTo(-14,56);p.lineTo(32,-10);p.lineTo(4,-10);p.closePath();fillS(p);});/* bolt */
  cell(4,0,()=>{const p=new Path2D();for(const o of [-34,0,34]){p.moveTo(o-14,-40);p.lineTo(o+18,0);p.lineTo(o-14,40);p.lineTo(o-2,40);p.lineTo(o+30,0);p.lineTo(o-2,-40);p.closePath();}fillS(p);});/* chevrons */
  cell(5,0,()=>{const p=new Path2D();p.arc(0,0,52,0,7);fillS(p);g.fillStyle='rgb(0,0,0)';for(let r=0;r<4;r++)for(let q=0;q<4;q++)if((r+q)%2)g.fillRect(-32+q*16,-32+r*16,16,16);});/* checker roundel */
  cell(6,0,()=>{const p=new Path2D();p.moveTo(0,-56);p.lineTo(46,-36);p.quadraticCurveTo(48,30,0,58);p.quadraticCurveTo(-48,30,-46,-36);p.closePath();fillS(p);g.fillStyle='rgb(0,0,0)';g.font='900 40px system-ui,sans-serif';g.textAlign='center';g.textBaseline='middle';g.fillText('CR',0,4);});/* crest */
  cell(7,0,()=>{const p=new Path2D();p.arc(0,0,50,0,7);p.arc(0,0,30,0,7,true);fillS(p);const q=new Path2D();for(let i=0;i<8;i++){const a=i/8*Math.PI*2;q.moveTo(Math.cos(a)*30,Math.sin(a)*30);q.lineTo(Math.cos(a+.2)*12,Math.sin(a+.2)*12);q.lineTo(Math.cos(a-.2)*12,Math.sin(a-.2)*12);q.closePath();}fillS(q);});/* turbine */
  // row 1: word marks (original names only)
  const words=['CRUST RUSH','OVEN 9','DOUGH BROS','EXTRA CHEESE','HOT SLICE','TURBO CRUST','PIZZA GP','MOZZ MOTORS'];
  words.forEach((w,i)=>cell(i,1,()=>{g.font='italic 900 30px system-ui,sans-serif';g.textAlign='center';g.textBaseline='middle';let f=30;while(g.measureText(w).width>118&&f>12){f--;g.font='italic 900 '+f+'px system-ui,sans-serif';}g.lineWidth=6;g.strokeStyle='rgb(0,0,0)';g.strokeText(w,0,0);g.fillStyle='rgb(255,255,255)';g.fillText(w,0,0);}));
  const t=T2(c,0,0,true);t.userData.shared=true;return t;})();
const hashS=s=>{let h=7;for(const c of s)h=(h*31+c.charCodeAt(0))>>>0;return h;};
const numTex=(()=>{const c=cnv(512,64),g=c.getContext('2d');g.fillStyle='#fff';g.font='bold 54px "Arial Black",Impact,sans-serif';g.textAlign='center';g.textBaseline='middle';for(let i=0;i<8;i++)g.fillText(String(i+1),32+i*64,36);const t=T2(c);t.userData.shared=true;return t;})();
const CHAR_MET={pep:[2.7,6.45],basil:[3.45,7.2],olive:[3.25,6.4],mozz:[2.95,6.1],chili:[3.45,6.8],shroom:[2.15,5.65],pineapple:[3.05,7.0],anchovy:[4.55,6.3]};
const LIV_VERT='varying vec3 vLivP;varying vec3 vLivN;\n';
const LIV_FRAG=`varying vec3 vLivP;varying vec3 vLivN;uniform vec3 uLA;uniform vec3 uLB;uniform vec3 uLC;uniform float uLPat;uniform vec4 uLBox;uniform float uLBelt;uniform float uLNum;uniform vec2 uLNumPos;uniform sampler2D uLNumTex;uniform sampler2D uLDec;uniform vec3 uLDecI;
float lh(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}
float ln2(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);return mix(mix(lh(i),lh(i+vec2(1,0)),f.x),mix(lh(i+vec2(0,1)),lh(i+vec2(1,1)),f.x),f.y);}
float lfbm(vec2 p){return .55*ln2(p)+.3*ln2(p*2.1)+.15*ln2(p*4.3);}
`;
const LIV_BODY=`
  vec3 lp=vLivP,lnn=normalize(vLivN);float lu=(lp.x-uLBox.x)/(uLBox.y-uLBox.x),laz=abs(lp.z)/uLBox.z,lside=step(.55,abs(lnn.z));float livR=-1.;
  vec3 lc=uLA;int lpat=int(uLPat+.5);
  if(lpat==1){float s=step(.07,laz)*step(laz,.2);lc=mix(uLA,uLB,s);lc=mix(lc,uLC,step(lp.y,uLBelt*.42));}
  else if(lpat==2){float t=smoothstep(uLBelt-.03,uLBelt+.03,lp.y);lc=mix(uLB,uLA,t);lc=mix(lc,uLC,1.-smoothstep(.02,.06,abs(lp.y-uLBelt)));}
  else if(lpat==3){float a=smoothstep(.62,.68,lu),b=smoothstep(.3,.36,lu);lc=mix(uLC,mix(uLB,uLA,a),b);}
  else if(lpat==4){float n=lfbm(vec2(lp.y*1.4,lp.z*1.1+lp.x*.15));float reach=.3+.32*n+.07*sin(lp.y*6.+lp.z*4.);float f=smoothstep(1.-reach-.02,1.-reach+.02,lu);
    float core=smoothstep(1.-reach*.55-.02,1.-reach*.55+.02,lu);lc=mix(uLA,mix(uLB,uLC,core),f*step(lp.y,uLBox.w*.92));}
  else if(lpat==5){float band=step(uLBelt-.42,lp.y)*step(lp.y,uLBelt+.06);float ch=mod(floor(lp.x*2.3)+floor(lp.y*2.3),2.);lc=mix(uLA,mix(uLA,uLB,ch),band*lside);
    lc=mix(lc,uLC,lside*(1.-smoothstep(.02,.05,abs(lp.y-(uLBelt+.1)))));}
  else if(lpat==6){float w=uLBelt-.2+.22*sin(lp.x*1.15+1.3);lc=lp.y<w?uLB:uLA;lc=mix(lc,uLC,1.-smoothstep(.03,.07,abs(lp.y-w)));}
  else if(lpat==7){float n=lfbm(vec2(lp.x*.42,lp.z*.42)+lp.y*.35);lc=n<.42?uLA:(n<.6?uLB:uLC);livR=.62;}
  else if(lpat==8){lc=mix(uLB,uLA,smoothstep(.12,.88,lu));lc=mix(lc,uLC,lside*(1.-smoothstep(.02,.05,abs(lp.y-uLBelt))));}
  else if(lpat==9){float d=fract((lp.x+lp.y*1.15)*.16);float mid=step(.22,lu)*step(lu,.8);lc=mix(uLA,uLB,lside*mid*step(d,.11));lc=mix(lc,uLC,lside*mid*step(.14,d)*step(d,.19));}
  else if(lpat==10){float lo=step(lp.y,uLBelt);float wv=mod(floor(lp.x*7.)+floor(lp.y*7.+lp.z*7.),2.);lc=mix(uLA,mix(uLB,uLB*1.7,wv),lo);livR=lo>.5?.22:-1.;lc=mix(lc,uLC,1.-smoothstep(.015,.04,abs(lp.y-uLBelt)));}
  else if(lpat==11){lc=mix(uLA,uLB,step(laz,.13)*step(.28,lu));lc=mix(lc,uLC,step(.82,lu)*step(lp.y,uLBelt*.85));}
  else if(lpat==12){float s=step(.05,laz)*step(laz,.1)+step(.14,laz)*step(laz,.19);lc=mix(uLA,uLB,s*step(.6,lnn.y));}
  else if(lpat==13){livR=.72;lc=mix(uLA,uLC,step(lp.y,uLBelt*.45));lc=mix(lc,uLB,lside*(1.-smoothstep(.015,.04,abs(lp.y-uLBelt*.62))));}
  else if(lpat==14){float m=step(.27,lu)*step(lu,.7);lc=mix(uLA,uLB,m*step(lp.y,uLBelt+.05));lc=mix(lc,uLC,lside*(1.-smoothstep(.03,.06,abs(lp.y-uLBelt*.72))));}
  else if(lpat==15){float s=step(laz,.17),bd=step(.17,laz)*step(laz,.21);lc=mix(mix(uLA,uLB,s),uLC,bd);float sb=lside*step(uLBelt-.42,lp.y)*step(lp.y,uLBelt-.12);lc=mix(lc,uLB,sb);}
  else if(lpat==16){float d=uLBelt-.05-lp.y-.45*(1.-lu);float s1=step(0.,d)*step(d,.13),s2=step(.16,d)*step(d,.25),s3=step(.28,d)*step(d,.37);vec3 mid=mix(uLB,vec3(1.),.45);
    lc=mix(uLA,uLB,s1*lside);lc=mix(lc,mid,s2*lside);lc=mix(lc,uLC,s3*lside);}
  else if(lpat==17){float k=lu*1.25+lp.y/uLBox.w*.85;lc=k>1.15?uLB:uLA;lc=mix(lc,uLC,1.-smoothstep(.02,.05,abs(k-1.15)));}
  else if(lpat==18){float zig=abs(fract(lp.y*1.2+abs(lp.z)*.9)-.5)*2.;float edge=1.-(.24+.22*zig);float f=step(edge,lu);lc=mix(uLA,uLB,f);lc=mix(lc,uLC,1.-smoothstep(.0,.025,abs(lu-edge)));}
  else if(lpat==19){lc=lp.y<uLBelt-.25?uLA:uLB;lc=mix(lc,uLC,1.-smoothstep(.04,.07,abs(lp.y-(uLBelt-.25))));float blk=lside*step(mod(floor(lp.x*.8),3.),.5)*step(uLBelt-.62,lp.y)*step(lp.y,uLBelt-.38);lc=mix(lc,vec3(.95),blk);}
  else if(lpat==20){vec2 q=floor(vec2(lp.x,lp.z+lp.y*1.3)*1.6);float n=lh(q)*.6+lh(floor(q/2.)+7.)*.4;lc=n<.45?uLA:(n<.72?uLB:uLC);livR=.6;}
  else if(lpat==21){float y0=uLBelt-.28+.2*(abs(fract(lp.x*.42)-.5)*4.-1.);float dd=abs(lp.y-y0);lc=mix(uLA,uLB,lside*step(dd,.1));lc=mix(lc,uLC,lside*step(.1,dd)*step(dd,.14));}
  else if(lpat==22){float n=lfbm(vec2(lp.x*.35,lp.y*.6+lp.z*.35));float st=sin(lp.x*2.6+n*7.+abs(lp.z)*.6);lc=mix(uLA,uLB,smoothstep(.55,.62,st)*(.4+.6*smoothstep(.2,.5,n)));}
  else if(lpat==23){vec2 g2=vec2(lp.x,lp.y+lp.z*.6)*2.2;vec2 c2=fract(g2)-.5;float rr=length(c2),lim=.48*(1.-lu);lc=mix(uLA,uLB,step(rr,lim));lc=mix(lc,uLC,lside*(1.-smoothstep(.02,.05,abs(lp.y-uLBelt))));}
  else if(lpat==24){float a2=fract(lp.x*.32-abs(lp.y-(uLBelt-.25))*.55);float band=step(abs(lp.y-(uLBelt-.25)),.42)*lside;lc=mix(uLA,uLB,band*step(a2,.28));lc=mix(lc,uLC,band*step(.28,a2)*step(a2,.36));}
  else if(lpat==25){float k2=lu+lp.y/uLBox.w*.35;lc=k2>.62?uLA:uLB;lc=mix(lc,uLC,1.-smoothstep(.006,.016,abs(k2-.62)));}
  else if(lpat==26){float t1=abs(lp.y-uLBelt),t2=abs(laz-.55);float pin=(1.-smoothstep(.015,.03,t1))*lside+(1.-smoothstep(.006,.014,t2))*step(.6,lnn.y);lc=mix(uLA,uLB,clamp(pin,0.,1.));}
  else if(lpat==27){float t3=clamp(lp.y/uLBox.w,0.,1.);lc=mix(uLA,uLB,smoothstep(.15,.9,t3));lc=mix(lc,uLC,lside*(1.-smoothstep(.015,.035,abs(lp.y-uLBelt*.5))));}
  else if(lpat==28){vec2 h=vec2(lp.x,lp.y+lp.z)*2.4;h.y*=1.1547;h.x+=step(1.,mod(h.y,2.))*.5;vec2 f2=abs(fract(h)-.5);float e=max(f2.x*1.5+f2.y,f2.y*2.)*.9;lc=mix(uLB,uLA,smoothstep(.62,.7,e));lc=mix(lc,uLC,lside*(1.-smoothstep(.015,.035,abs(lp.y-uLBelt))));livR=.3;}
  if(uLNum>-.5&&abs(lnn.z)>.6){vec2 d=vec2(lp.x-uLNumPos.x,lp.y-uLNumPos.y);float r=length(d);if(r<.72){lc=r<.6?vec3(.95):uLB;
    if(r<.6){float tx=d.x/1.2*(lp.z>0.?1.:-1.)+.5,ty=d.y/1.2+.5;float a=texture2D(uLNumTex,vec2((uLNum+clamp(tx,0.,1.))/8.,clamp(ty,0.,1.))).a;lc=mix(lc,vec3(.06),a);}}}
  if(abs(lnn.z)>.55){float sd=lp.z>0.?1.:-1.,L=uLBox.y-uLBox.x;
    if(uLDecI.x>-.5){vec2 c0=uLNum>-.5?vec2(uLBox.x+L*.3,uLNumPos.y):uLNumPos;float S=uLDecI.z;vec2 q=vec2((lp.x-c0.x)/S*sd+.5,(lp.y-c0.y)/S+.5);
      if(q.x>0.&&q.x<1.&&q.y>0.&&q.y<1.){vec4 t=texture2D(uLDec,vec2((uLDecI.x+q.x)/8.,.5+q.y*.5));lc=mix(lc,mix(uLC,uLB,t.r),t.a);}}
    if(uLDecI.y>-.5){vec2 c1=vec2(uLBox.x+L*(uLNum>-.5?.62:.26),uLBelt*.62);float S=L*.2;vec2 q=vec2((lp.x-c1.x)/S*sd+.5,(lp.y-c1.y)/(S*.32)+.5);
      if(q.x>0.&&q.x<1.&&q.y>.12&&q.y<.88){q.y=.5+(q.y-.5)*.3;vec4 t=texture2D(uLDec,vec2((uLDecI.y+q.x)/8.,q.y*.5));lc=mix(lc,mix(uLC*.6,uLB,t.r),t.a*.95);}}}
  diffuseColor.rgb*=lc;
`;
function liveryMaterial(lv,box,belt,numIdx,numPos){
  const mat=new THREE.MeshPhysicalMaterial({color:'#ffffff',vertexColors:true,metalness:Math.min(lv.m,lv.id==='chrome'?.85:.62),roughness:lv.r,clearcoat:lv.r<.6?1:.2,clearcoatRoughness:.05,envMapIntensity:1.2});
  const U={uLA:{value:new THREE.Color(lv.A)},uLB:{value:new THREE.Color(lv.B)},uLC:{value:new THREE.Color(lv.C)},uLPat:{value:lv.pat},uLBox:{value:new THREE.Vector4(box[0],box[1],box[2],box[3])},
    uLBelt:{value:belt},uLNum:{value:lv.num?numIdx:-1},uLNumPos:{value:new THREE.Vector2(numPos[0],numPos[1])},uLNumTex:{value:numTex},uLDec:{value:decTex},
    uLDecI:{value:new THREE.Vector3(lv.dec??(hashS(lv.id)%9===8?-1:hashS(lv.id)%8),lv.word??(hashS(lv.id+'w')%3===0?-1:hashS(lv.id+'w')%8),(box[1]-box[0])*.11)}};
  mat.onBeforeCompile=sh=>{Object.assign(sh.uniforms,U);
    sh.vertexShader=LIV_VERT+sh.vertexShader.replace('#include <begin_vertex>','#include <begin_vertex>\n vLivP=position;vLivN=normal;');
    sh.fragmentShader=LIV_FRAG+sh.fragmentShader.replace('#include <color_fragment>','#include <color_fragment>\n'+LIV_BODY).replace('#include <roughnessmap_fragment>','#include <roughnessmap_fragment>\n if(livR>=0.)roughnessFactor=livR;');};
  mat.customProgramCacheKey=()=>'livery2';return mat;}
const carBox={};
function carDims(id){if(carBox[id])return carBox[id];const g=carGeos(id),p=g.b_paint.attributes.position.array;let x0=1e9,x1=-1e9,zw=0,yt=0;
  for(let i=0;i<p.length;i+=3){x0=Math.min(x0,p[i]);x1=Math.max(x1,p[i]);zw=Math.max(zw,Math.abs(p[i+2]));yt=Math.max(yt,p[i+1]);}return carBox[id]=[x0,x1,zw,yt];}

function chuteTex(a){const c=cnv(512,32),g=c.getContext('2d');for(let i=0;i<12;i++){g.fillStyle=i%2?'#fff4dc':a;g.fillRect(i*512/12,0,512/12+1,32);}const t=T2(c);t.userData.kart=true;return t;}
function gores(n,cols){const c=cnv(512,256),g=c.getContext('2d');for(let i=0;i<n;i++){g.fillStyle=cols[i%cols.length];g.fillRect(i*512/n,0,512/n+1,256);}
  g.fillStyle='rgba(0,0,0,.18)';for(let i=0;i<n;i++)g.fillRect(i*512/n-1,0,2,256);g.fillStyle='rgba(255,255,255,.35)';g.fillRect(0,250,512,6);
  for(let y=40;y<250;y+=60){g.fillStyle='rgba(0,0,0,.08)';g.fillRect(0,y,512,2);}const t=T2(c);t.userData.kart=true;return t;}
function buildGlider(type,M,rc){const G=new THREE.Group(),A=new THREE.Group();G.add(A);let anchors;
  const pc=M.paint.color.getStyle(),sc=M.stripe.color.getStyle(),dk=M.dark.color.getStyle(),metal=SH.metal,rope=SH.rope;
  const cloth=(cols,n)=>new THREE.MeshStandardMaterial({map:gores(n||12,cols),roughness:.62,side:THREE.DoubleSide});
  if(type==='chute'){/* round canopy: 12 gores, apex vent, skirt band, risers and a harness ring */
    const d=P3(new THREE.SphereGeometry(5,36,14,0,Math.PI*2,.12,Math.PI*.3),cloth([pc,'#fff4dc']),0,-1.2,0,A);d.scale.set(1.15,.75,1);
    P3(new THREE.SphereGeometry(5,24,4,0,Math.PI*2,0,.12),cloth([sc]),0,-1.2,0,A).scale.set(1.15,.75,1);
    {const t=P3(new THREE.TorusGeometry(4.85,.14,8,48),M.dark,0,.25,0,A);t.rotation.x=Math.PI/2;t.scale.set(1.15,1,1);}
    for(let i=0;i<12;i++){const a=i/12*Math.PI*2;limb(KG.rod,rope,[Math.cos(a)*4.85*1.15,.25,Math.sin(a)*4.85],[0,-3.4,0],A);}
    const r=P3(new THREE.TorusGeometry(.5,.12,8,20),metal,0,-3.4,0,A);r.rotation.x=Math.PI/2;anchors=[[0,-3.4,.4],[0,-3.4,.4]];}
  else if(type==='para'){/* ram-air: curved cells with open mouths, ribs and cascading lines */
    const W=13,cells=9;for(let i=0;i<cells;i++){const x0=-W/2+i*W/cells,a=(i+.5)/cells-.5,y=-Math.abs(a)*a*0+(-a*a*5),cm=i%2?M.stripe:M.paint;
      const c=P3(new THREE.BoxGeometry(4.6,.9,W/cells*.96),cm,0,y,x0+W/cells/2,A);c.rotation.x=a*1.1;
      P3(new THREE.BoxGeometry(4.6,.95,.05),M.dark,0,y,x0,A).rotation.x=a*1.1;P3(new THREE.PlaneGeometry(W/cells*.85,.8),SH.black||M.dark,2.31,y,x0+W/cells/2,A).rotation.y=Math.PI/2;}
    for(let i=0;i<cells;i++){const z=-W/2+(i+.5)*W/cells,a=(i+.5)/cells-.5,y=-a*a*5;for(const x of [-1.6,1.6])limb(KG.rod,rope,[x,y-.4,z],[0,-4.2,z*.12],A);}
    anchors=[[0,-4.2,.6],[0,-4.2,.6]];}
  else if(type==='hang'){/* delta wing: sail, keel tube, leading edges, control bar */
    const sh=new THREE.Shape();sh.moveTo(5.5,0);sh.lineTo(-3.2,7.2);sh.quadraticCurveTo(-2.2,0,-3.2,-7.2);sh.closePath();
    const s=P3(new THREE.ExtrudeGeometry(sh,{depth:.06,bevelEnabled:false}),cloth([pc,sc,pc],6),0,0,0,A);s.rotation.x=-Math.PI/2;
    limb(KG.rod,metal,[5.5,.1,0],[-3.4,.1,0],A);for(const z of [-1,1])limb(KG.rod,metal,[5.5,.1,0],[-3.2,.1,7.2*z],A);limb(KG.rod,metal,[1,.1,-3.6],[1,.1,3.6],A);
    for(const z of [-1,1])limb(KG.rod,metal,[1,0,0],[.2,-3.2,1.8*z],A);limb(KG.rod,metal,[.2,-3.2,-1.8],[.2,-3.2,1.8],A);
    P3(new THREE.BoxGeometry(.6,.6,.6),M.dark,5.5,.2,0,A);anchors=[[.2,-3.2,1],[.2,-3.2,1]];}
  else if(type==='twin'){/* two smaller round canopies on a spreader bar */
    for(const z of [-1,1]){const d=P3(new THREE.SphereGeometry(3.4,28,10,0,Math.PI*2,0,Math.PI*.42),cloth(z>0?[pc,'#fff4dc']:[sc,'#fff4dc'],10),0,-.6,z*3.6,A);d.scale.set(1,.75,1);
      const t=P3(new THREE.TorusGeometry(3.3,.11,8,36),M.dark,0,.2,z*3.6,A);t.rotation.x=Math.PI/2;for(let i=0;i<8;i++){const a=i/8*Math.PI*2;limb(KG.rod,rope,[Math.cos(a)*3.3,.2,z*3.6+Math.sin(a)*3.3],[0,-2.6,z*1.6],A);}}
    limb(KG.rod,metal,[0,-2.6,-1.6],[0,-2.6,1.6],A);anchors=[[0,-2.6,1.4],[0,-2.6,1.4]];}
  else if(type==='balloon'){/* puffy dough envelope with a wicker basket ring */
    const env=P3(lumpy(new THREE.SphereGeometry(4.6,32,22),.06,1.4,1.2),new THREE.MeshStandardMaterial({color:'#ecc88a',roughness:.75}),0,1.6,0,A);env.scale.set(1,1.12,1);
    for(let i=0;i<8;i++){const a=i/8*Math.PI*2,b=P3(new THREE.TorusGeometry(4.65,.12,6,40,Math.PI),M.paint,0,1.6,0,A);b.rotation.set(0,a,Math.PI/2);b.scale.set(1,1.12,1);}
    const bs=P3(new THREE.CylinderGeometry(1.4,1.2,1.1,16,1,true),new THREE.MeshStandardMaterial({color:'#9a6a3a',roughness:.85,side:THREE.DoubleSide}),0,-3.2,0,A);
    for(let i=0;i<4;i++){const a=i/4*Math.PI*2+.78;limb(KG.rod,rope,[Math.cos(a)*3.2,-1.6,Math.sin(a)*3.2],[Math.cos(a)*1.3,-2.7,Math.sin(a)*1.3],A);}
    anchors=[[0,-3.6,.6],[0,-3.6,.6]];}
  else if(type==='umbrella'){/* striped patio umbrella with ribs, scalloped valance and a wooden pole */
    const cn=P3(new THREE.ConeGeometry(6,2.2,16,1,true),cloth([pc,'#fff4dc'],16),0,0,0,A);cn.material.side=THREE.DoubleSide;
    for(let i=0;i<16;i++){const a=i/16*Math.PI*2;limb(KG.rod,SH.metal,[0,1.1,0],[Math.cos(a)*6,-1.1,Math.sin(a)*6],A);
      const v=P3(new THREE.CircleGeometry(.62,10,0,Math.PI),i%2?M.paint:M.stripe,Math.cos(a+.2)*5.95,-1.3,Math.sin(a+.2)*5.95,A);v.lookAt(0,-1.3,0);v.rotation.z=Math.PI;}
    limb(KG.rod,new THREE.MeshStandardMaterial({color:'#8a5a30',roughness:.6}),[0,1.6,0],[0,-4.2,0],A).scale.x*=3;P3(new THREE.SphereGeometry(.4,12,8),SH.chrome||metal,0,1.4,0,A);anchors=[[0,-4.2,.5],[0,-4.2,.5]];}
  else if(type==='wing'){const sl=extr([[4.8,0],[-2.6,5.6],[-2.6,-5.6]],.32,.1);const w=P3(sl,SH.cheese,0,0,0,A);w.rotation.x=-Math.PI/2;
    hrx(P3(KG.crust,SH.crust,-2.7,0,0,A)).scale.set(.55,2.25,.55);[[0,0],[-1.4,2.6],[-1.4,-2.6],[1.8,0]].forEach(([x,z])=>P3(KG.topD,SH.pep,x,.32,z,A).scale.set(1.5,1,1.5));
    for(let i=0;i<9;i++)P3(KG.topD,SH.basil,-1+Math.random()*3,.33,(Math.random()-.5)*5,A).scale.set(.5,1,.9);
    limb(KG.rod,metal,[1.5,-.2,0],[-2.2,-.2,0],A);anchors=[[1.5,0,2.2],[-2.2,0,4.2]];}
  else if(type==='leaf'){const sh=new THREE.Shape();sh.moveTo(0,-7.2);sh.quadraticCurveTo(4.6,-2.2,0,7.2);sh.quadraticCurveTo(-4.6,-2.2,0,-7.2);
    const l=P3(new THREE.ExtrudeGeometry(sh,{depth:.22,bevelEnabled:true,bevelThickness:.1,bevelSize:.12,bevelSegments:2,curveSegments:16}),SH.basil,0,0,0,A);l.rotation.x=-Math.PI/2;
    const vein=new THREE.MeshStandardMaterial({color:'#86cf70',roughness:.5});limb(KG.rod,vein,[0,.42,-7],[0,.42,7],A);for(const z of [-4,-1.5,1,3.5])for(const s of [-1,1])limb(KG.rod,vein,[0,.4,z],[1.9*s,.36,z+1.8],A);
    for(let i=0;i<6;i++)P3(new THREE.SphereGeometry(.18,8,6),new THREE.MeshStandardMaterial({color:'#bfe9ff',roughness:.05,transparent:true,opacity:.8}),(Math.random()-.5)*2,.45,(Math.random()-.5)*8,A);anchors=[[1.8,0,2.6],[-1.8,0,2.6]];}
  else if(type==='box'){P3(new THREE.BoxGeometry(7.6,.34,8.4),SH.card,0,0,0,A);P3(new THREE.BoxGeometry(7.2,.05,8.0),SH.cardIn,0,-.19,0,A);
    P3(new THREE.CylinderGeometry(2.4,2.4,.06,32),SH.pep,0,.2,0,A);P3(new THREE.CylinderGeometry(1.8,1.8,.08,32),SH.cheese,0,.22,0,A);
    for(const s of [-1,1])P3(new THREE.BoxGeometry(7.6,1.0,.25),SH.card,0,-.55,4.1*s,A);for(const s of [-1,1])P3(new THREE.BoxGeometry(.25,1,8.4),SH.card,3.8*s,-.55,0,A);
    for(let i=0;i<5;i++)P3(KG.topD,SH.pep,(Math.random()-.5)*2.4,.27,(Math.random()-.5)*2.4,A).scale.set(.9,1,.9);anchors=[[3.4,-.4,3.4],[-3.4,-.4,3.4]];}
  if(['chute','para','twin','balloon','umbrella'].includes(type)){for(const s of [-1,1])limb(KG.stalk,rope,[anchors[0][0],anchors[0][1],anchors[0][2]*s],[0,-4.9,.9*s],A);}
  else
  for(const [x,y,z] of anchors)for(const s of [-1,1])limb(KG.stalk,SH.rope,[x,y,z*s],[x*.15,-4.6,.8*s],A);
  bake(A,false);return G;}
/* tyres get wider with size, but only up to a point: giant wheels stay chunky instead of turning into drums */
const tyreR=R=>Math.min(R,1.35);
/* cabin fits for the newer cars: [roof, beltline, seat x, seat floor] */
const FITQ={hatch:[3.42,2.3,.6,1.15],suv:[4.7,3.1,.3,1.55],coupe:[3.05,2.25,.3,1.1],scissor:[2.6,1.75,.6,.45]};
const _tw={};function packTyreW(car,wi,full){const k=car+wi+(full?'f':'');if(_tw[k])return _tw[k];const a=carGeos(car)['w'+wi].attributes.position;let R=0;for(let i=0;i<a.count;i++)R=Math.max(R,Math.hypot(a.getX(i),a.getY(i)));let z0=1e9,z1=-1e9;for(let i=0;i<a.count;i++)if(full||Math.hypot(a.getX(i),a.getY(i))>R*.86){z0=Math.min(z0,a.getZ(i));z1=Math.max(z1,a.getZ(i));}return _tw[k]=Math.max(.3,z1-z0);}
function buildKart(spec){HQB=spec.hq!==0;
  const rc=RACERS[spec.ri],idx=spec.ri,body=BODIES[spec.b],gd=GLIDERS[spec.g];let wt=WHEELS[spec.w];let lv=spec.t?livOf(spec.t):null;if(lv&&lv.only&&lv.only!==body.id)lv=null;const col=lv?lv.A:(PAINTS[spec.p]||rc.color);
  const paint=new THREE.MeshPhysicalMaterial({color:col,roughness:.38,metalness:.12,clearcoat:1,clearcoatRoughness:.08,envMapIntensity:1});
  const M={paint,dark:new THREE.MeshStandardMaterial({color:lv?lv.C:shade(col,-.45),roughness:.4,metalness:.3}),stripe:new THREE.MeshStandardMaterial({color:lv?lv.B:(rc.stripe===col?rc.top:rc.stripe),roughness:.3,metalness:.1}),
    tailM:new THREE.MeshStandardMaterial({color:'#ff2a1a',emissive:'#ff1a0a',emissiveIntensity:.8})};
  if(body.id==='oven'){M.brick=new THREE.MeshStandardMaterial({map:brickT,color:new THREE.Color('#ffffff').lerp(new THREE.Color(col),.3),roughness:.85});}
  const topM=new THREE.MeshStandardMaterial({color:rc.top,roughness:.42}),irisM=new THREE.MeshStandardMaterial({color:rc.iris,roughness:.2});
  const g=new THREE.Group(),tilt=new THREE.Group();g.add(tilt);const B=new THREE.Group();tilt.add(B);const S=new THREE.Group();B.add(S);
  const cfg=BODY_FN[body.id](S,M,rc,idx,B);if(cfg.car&&wt.pack===cfg.car)wt=WHEELS[0];/* a truck's own tyres are its standard wheels */if(!cfg.noCockpit)addCockpit(S,cfg,rc);bake(S,true,true);
  if(cfg.car&&lv&&M.paintMesh){const old=M.paintMesh.material;M.paintMesh.material=liveryMaterial(lv,carDims(cfg.car),cfg.belt||1.5,idx,cfg.numPos||[0,1]);old.dispose();}
  const L=cfg.rw[2]*(wt.r-1),wz=(cfg.wz||1)*wt.wz;B.position.y=L;
  /* oversized or wider wheels are pushed out past the bodywork so they never cut into it */
  const bodyPts=[];B.traverse(o=>{if(o.isMesh&&o.geometry&&o.material!==SH.carGlass)bodyPts.push(o.geometry.attributes.position.array);});
  /* slide the wheel outwards only until no bodywork sits inside the tyre's swept disc (the hub area is allowed, that's where it bolts on) */
  const clearZ=(x0,R,z,Wn,r0,zN,W0)=>{for(let it=0;it<4;it++){let m=-1;const lo=z-Wn/2,hi=z+Wn/2;
      for(const a of bodyPts)for(let i=0;i<a.length;i+=3){const dx=a[i]-x0,dy=a[i+1]+L-R,rr=Math.sqrt(dx*dx+dy*dy);if(rr>R*.96||rr<R*.34)continue;const az=Math.abs(a[i+2]);
        if(rr<r0*1.02&&az>zN-W0/2-.15&&az<zN+W0/2+.15)continue;/* brakes and suspension that live inside the original wheel */
        if(az>lo&&az<hi&&az>m)m=az;}
      if(m<0)break;z=m+Wn/2+.04;}return z;};
  const wheelZ=(w,f,s,R)=>{const q=cfg.car?CAR_PACKS[cfg.car].h.wheels.find(q=>Math.sign(q.c[2])===s&&q.f===f):null;if(q&&wt.id==='standard')return q.c[2];
    const Wn=1.44*tyreR(R)/1.32*wz;let W0,zIn,zOut,zN=w[1];
    if(q){W0=packTyreW(cfg.car,CAR_PACKS[cfg.car].h.wheels.indexOf(q),cfg.ow);zN=Math.abs(q.c[2]);zOut=zN+W0/2;zIn=zN-W0/2;}else{W0=1.44*tyreR(w[2])/1.32*(cfg.wz||1);zIn=w[1]-W0/2;zOut=w[1]+W0/2;}
    /* cars: the outer face stays flush with the original tyre; open-wheel karts: the inner face stays on the hub */
    let z=q&&!cfg.ow?zOut-Wn/2:zIn+Wn/2;
    if(R>w[2]*1.02||Wn>W0*1.02)z=Math.min(clearZ(w[0],R,z,Wn,w[2],zN,W0),z+W0*(q?.22:.5)+Math.max(0,R-w[2])*.6);return z*s;};
  const wheels=[],front=[];
  for(const [w,f] of [[cfg.rw,0],[cfg.fw,1]])for(const s of [-1,1]){const R=w[2]*wt.r,yaw=new THREE.Group();yaw.position.set(w[0],R,wheelZ(w,f,s,R));g.add(yaw);
    const zN=w[1],zW=Math.abs(yaw.position.z),Wh=1.44*tyreR(R)/1.32*wz;if(zW-Wh/2>zN-.05){const len=zW-Wh/2-(zN-.4),ad=new THREE.Mesh(KG.axle,SH.metal);ad.rotation.x=Math.PI/2;ad.scale.set(R*.9,len/5.6,R*.9);ad.position.z=-s*(Wh/2+len/2);ad.castShadow=true;yaw.add(ad);}
    const spin=new THREE.Group();yaw.add(spin);let wh;if(cfg.car&&wt.id==='standard'){const cg=carGeos(cfg.car),wi=CAR_PACKS[cfg.car].h.wheels.findIndex(q=>Math.sign(q.c[2])===s&&q.f===f);wh=new THREE.Mesh(cg['w'+wi],SH.carVC);wh.castShadow=false;}/* detailed rims cost a lot in the shadow pass for an invisible gain */else{wh=buildWheel(wt.id,s,M);wh.scale.set(R/1.32,R/1.32,tyreR(R)/1.32*wz);}spin.add(wh);wheels.push({spin,r:R});if(f)front.push(yaw);}
  for(const w of wheels){const yw=w.spin.parent;if(yw&&yw.parent===g)tilt.add(yw);}
  const drv=new THREE.Group();drv.rotation.y=Math.PI/2;(spec.hq===0?lowDetail:f=>f())(()=>buildDriver(drv,rc,topM,irisM));
  {const db=new THREE.Box3();drv.updateMatrixWorld(true);db.setFromObject(drv);cfg.dzc=(db.min.x+db.max.x)/2;}
  if(cfg.fit){const F=cfg.fit,[e,h]=CHAR_MET[rc.name.toLowerCase()]||[2.8,6.4],cl=Math.cos(F.lean||0),fl=cfg.drv[1];let sc,y0;
    if(F.open){sc=F.s;y0=F.rim+.45-e*sc;}
    else{const eyeT=F.belt+.2,top=F.roof-.07;sc=Math.min(F.smax||.3,(top-fl)/(h*cl));y0=Math.min(eyeT-e*sc*cl,top-h*sc*cl);y0=Math.max(y0,fl-.12);}
    cfg.drvS=sc;cfg.drv=[cfg.drv[0],y0,cfg.drv[2]||0];cfg.lean=F.lean||0;}
  const sc0=cfg.drvS||.62,dx=cfg.fit?-(cfg.dzc||0)*sc0:0;
  const dlean=new THREE.Group();dlean.position.set(cfg.drv[0]+dx,cfg.drv[1],cfg.drv[2]||0);dlean.rotation.z=cfg.lean||0;B.add(dlean);
  drv.scale.setScalar(sc0);dlean.add(drv);
  const flames=[];for(const [x,y,z] of cfg.pipes){const f=hrz(new THREE.Mesh(KG.flame,flameMat));f.position.set(x-1.27,y,z);B.add(f);const fi=hrz(new THREE.Mesh(KG.flameIn,flameInMat));fi.position.set(x-.77,y,z);B.add(fi);flames.push(f,fi);}
  flames.forEach(f=>f.visible=false);
  const lo=new THREE.Group(),lb=new THREE.Group();lb.position.y=L;lo.add(lb);if(cfg.car){const cg=carGeos(cfg.car),lm={paint,tail:M.tailM,light:SH.light,glass:SH.glass,vc:SH.carbon,blue:SH.light};for(const k in cg)if(k.startsWith('l_'))lb.add(new THREE.Mesh(cg[k],lm[k.slice(2)]));}else{const [ll,lh,lw,ly]=cfg.lo;P3(new THREE.BoxGeometry(ll,lh,lw),paint,0,ly,0,lb);}
  for(const [w] of [[cfg.rw],[cfg.fw]])for(const s of [-1,1]){const R=w[2]*wt.r;hrx(P3(KG.loWheel,SH.rubber,w[0],R-L,w[1]*s,lb)).scale.set(R/1.32,wz*tyreR(R)/R,R/1.32);}
  const ldl=new THREE.Group();ldl.position.set(cfg.drv[0]+dx,cfg.drv[1],cfg.drv[2]||0);ldl.rotation.z=cfg.lean||0;lb.add(ldl);const ld=new THREE.Group();ld.rotation.set(0,Math.PI/2,0);ld.scale.setScalar(sc0);ldl.add(ld);loDriver(ld,rc);
  bake(lo,false,true);lo.visible=false;g.add(lo);
  /* imported cars: the light far-distance model casts the shadow, so the detailed body and driver skip the shadow pass */
  if(cfg.car){lo.traverse(o=>{if(o.isMesh)o.castShadow=false;});const sp=lo.clone();sp.visible=true;sp.traverse(o=>{if(o.isMesh){o.material=SHADOW_ONLY;o.castShadow=true;o.receiveShadow=false;}});g.add(sp);
    B.traverse(o=>{if(o.isMesh)o.castShadow=false;});}
  const bub=new THREE.Mesh(KG.bubble,bubbleMat);bub.position.set(0,cfg.bubY+L,0);bub.scale.setScalar(cfg.bubS||1);bub.visible=false;g.add(bub);
  {const cl=new THREE.Group();for(let i=0;i<3;i++){const c=itemProto('clove').clone(),a=i/3*Math.PI*2;c.position.set(Math.cos(a)*5.3,Math.sin(a*2)*1.2,Math.sin(a)*5.3);c.rotation.set(.5,a,.3);c.scale.setScalar(1.1);cl.add(c);}bub.add(cl);bub.userData.cl=cl;}
  const ice=itemProto('icebox').clone();ice.position.copy(bub.position);ice.scale.setScalar(cfg.bubS||1);ice.visible=false;g.add(ice);
  const gl=buildGlider(gd.id,M,rc);gl.position.y=cfg.glY+L;gl.visible=false;gl.scale.setScalar(.01);tilt.add(gl);
  const fxP=cfg.pipes.map(([x,y,z])=>new THREE.Vector3(x-.4,y+L,z)),rz=cfg.rw[1]+.3,fxL=[new THREE.Vector3(cfg.rw[0]-.5,.35,rz),new THREE.Vector3(cfg.rw[0]-.5,.35,-rz)];
  return {g,tilt,wheels,front,flames,drv,drvY:0,sf:body.sf||1,axF:cfg.fw[0]*KS*(body.sf||1),axR:cfg.rw[0]*KS*(body.sf||1),axW:Math.max(cfg.fw[1],cfg.rw[1])*KS*(body.sf||1),ice,iceS:cfg.bubS||1,tailM:M.tailM,lo,bub,gl,ga:0,fxP,fxL,flash:cfg.flash?M.blue:null,top:(cfg.top+L)*(body.sf||1),smoke:cfg.smoke?new THREE.Vector3(cfg.smoke[0],cfg.smoke[1]+L,cfg.smoke[2]):null,spec};
}
function disposeModel(m){m.g.traverse(o=>{if(o.geometry&&!KGSET.has(o.geometry)&&!CARGEO.has(o.geometry))o.geometry.dispose();if(o.material){const ms=Array.isArray(o.material)?o.material:[o.material];
  for(const mt of ms){if(SHSET.has(mt)||mt.userData.shared||mt===bubbleMat||mt===bubRushMat||mt===flameMat||mt===flameInMat)continue;if(mt.map&&mt.map.userData.kart)mt.map.dispose();mt.dispose();}}});}
const modelCache=new Map();
const specKey=s=>[s.ri,s.b,s.w,s.g,s.p,s.t||'',s.hq===0?0:1].join('.');
function getModel(spec){const key=specKey(spec);let m=modelCache.get(key);if(!m){m=buildKart(spec);m.g.rotation.order='YZX';m.g.scale.setScalar(KS*m.sf);if(!spec.hq){m.g.updateMatrixWorld(true);const ws=new THREE.Vector3();m.g.traverse(o=>{if(!o.isMesh||!o.castShadow)return;const g=o.geometry;if(!g.boundingSphere)g.computeBoundingSphere();o.getWorldScale(ws);if(g.boundingSphere.radius*Math.max(ws.x,ws.y,ws.z)<9)o.castShadow=false;});}if(!spec.hq){try{buildMid(m);}catch(e){console.warn('mid',e);}}m.g.visible=false;scene.add(m.g);modelCache.set(key,m);}return m;}

/* merge meshes for the mid-distance kart: plain materials collapse into a few shared vertex-coloured ones (colour moves into the vertices) */
const MIDM=new Map();const _mc=new THREE.Color();
function midMerge(S){S.updateMatrixWorld(true);const B=new Map();
  const texd=mt=>['map','roughnessMap','metalnessMap','normalMap','emissiveMap','clearcoatMap','alphaMap','aoMap'].some(k=>mt[k]);
  for(const o of S.children){const mt=o.material;const em=mt.emissive&&mt.emissiveIntensity>0&&(mt.emissive.r+mt.emissive.g+mt.emissive.b)>0;
    const plain=(mt.isMeshStandardMaterial)&&!mt.transparent&&!texd(mt)&&!em&&mt.onBeforeCompile===THREE.Material.prototype.onBeforeCompile;
    const key=plain?'P|0|'+(mt.roughness<.5?.35:.75)+'|'+(mt.metalness>.5?1:0):mt.uuid;
    if(!B.has(key))B.set(key,{plain,mt,list:[]});B.get(key).list.push(o);}
  while(S.children.length)S.remove(S.children[0]);
  for(const [key,bk] of B){let mat=bk.mt;if(bk.plain){mat=MIDM.get(key);if(!mat){const [_,cc,r,m]=key.split('|');const o={vertexColors:true,roughness:+r,metalness:+m};mat=+cc?new THREE.MeshPhysicalMaterial(Object.assign(o,{clearcoat:1,clearcoatRoughness:.1})):new THREE.MeshStandardMaterial(o);SHSET.add(mat);MIDM.set(key,mat);}}
    let n=0;const gs=bk.list.map(o=>{const g=o.geometry.index?o.geometry.toNonIndexed():o.geometry.clone();g.applyMatrix4(o.matrixWorld);n+=g.attributes.position.count;return [g,o];});
    const P=new Float32Array(n*3),N=new Float32Array(n*3),U=new Float32Array(n*2),C=new Float32Array(n*3);let off=0,hasC=false;
    for(const [g,o] of gs){const c=g.attributes.position.count;P.set(g.attributes.position.array,off*3);N.set(g.attributes.normal.array,off*3);if(g.attributes.uv)U.set(g.attributes.uv.array.subarray(0,c*2),off*2);
      const ca=g.attributes.color,mc=o.material.color||_mc.set(1,1,1),mul=bk.plain;if(ca||mul)hasC=true;
      for(let i=0;i<c;i++){const r=ca?ca.getX(i):1,gg=ca?ca.getY(i):1,b=ca?ca.getZ(i):1;C[(off+i)*3]=r*(mul?mc.r:1);C[(off+i)*3+1]=gg*(mul?mc.g:1);C[(off+i)*3+2]=b*(mul?mc.b:1);}off+=c;g.dispose();}
    const mg=new THREE.BufferGeometry();mg.setAttribute('position',new THREE.BufferAttribute(P,3));mg.setAttribute('normal',new THREE.BufferAttribute(N,3));mg.setAttribute('uv',new THREE.BufferAttribute(U,2));if(hasC&&(bk.plain||mat.vertexColors))mg.setAttribute('color',new THREE.BufferAttribute(C,3));mg.computeBoundingSphere();
    const me=new THREE.Mesh(mg,mat);me.castShadow=bk.list.some(o=>o.castShadow);me.receiveShadow=true;S.add(me);}}

/* rivals at middle distance: the whole kart (body, driver, wheels) merged into a few meshes, so each costs ~4 draws instead of ~35 */
function buildMid(m){const g=m.g;g.updateMatrixWorld(true);const skip=new Set();[m.lo,m.bub,m.ice,m.gl,...(m.flames||[]),...m.wheels.map(w=>w.spin)].forEach(o=>o&&o.traverse(x=>skip.add(x)));
  let sp=false;const src=[];g.traverse(o=>{if(!o.isMesh||skip.has(o))return;if(o.material===SHADOW_ONLY){sp=true;return;}let p=o,vis=true;while(p&&p!==g){if(!p.visible){vis=false;break;}p=p.parent;}if(vis)src.push(o);});
  const inv=new THREE.Matrix4().copy(m.tilt.matrixWorld).invert(),S=new THREE.Group(),keep=[];
  for(const o of src){const mt=o.material,mm=new THREE.Matrix4().multiplyMatrices(inv,o.matrixWorld);
    const special=Array.isArray(mt)||mt===m.tailM||mt===m.flash||mt.onBeforeCompile!==THREE.Material.prototype.onBeforeCompile||mt.customProgramCacheKey!==THREE.Material.prototype.customProgramCacheKey;
    const c=new THREE.Mesh(o.geometry,mt);c.matrixAutoUpdate=false;c.matrix.copy(mm);mm.decompose(c.position,c.quaternion,c.scale);c.castShadow=!sp&&o.castShadow;c.receiveShadow=true;
    (special?keep:S.children).push(c);if(!special)c.parent=S;}
  midMerge(S);const mid=new THREE.Group();
  for(const c of [...S.children])mid.add(c);for(const c of keep){c.parent=null;mid.add(c);}
  if(!sp)mid.traverse(o=>{if(o.isMesh&&o.geometry.boundingSphere&&o.geometry.boundingSphere.radius>3)o.castShadow=true;});
  mid.visible=false;m.tilt.add(mid);m.mid=mid;m.midSrc=src;m.midOn=false;
  for(const w of m.wheels){const sp=w.spin,ms=[];sp.updateMatrixWorld(true);sp.traverse(o=>{if(o.isMesh&&o.visible)ms.push(o);});if(ms.length<2)continue;
    const iv=new THREE.Matrix4().copy(sp.matrixWorld).invert(),S2=new THREE.Group();
    for(const o of ms){const c=new THREE.Mesh(o.geometry,o.material);c.matrixAutoUpdate=false;c.matrix.multiplyMatrices(iv,o.matrixWorld);c.castShadow=false;S2.children.push(c);c.parent=S2;}
    midMerge(S2);for(const o of ms)o.parent.remove(o);for(const c of [...S2.children]){c.parent=null;c.castShadow=false;sp.add(c);}}}
function setMid(m,on){if(m.midOn===on)return;m.midOn=on;m.mid.visible=on;for(const o of m.midSrc)o.visible=!on;}
function pruneModels(keep){if(modelCache.size<=22)return;for(const [k,m] of modelCache){if(keep.has(m))continue;scene.remove(m.g);disposeModel(m);modelCache.delete(k);if(modelCache.size<=14)break;}}

/* ================= PARTICLES ================= */
function particleSystem(max,blending,tex){
  const geo=new THREE.BufferGeometry(),pos=new Float32Array(max*3),col=new Float32Array(max*3),size=new Float32Array(max),alpha=new Float32Array(max);
  geo.setAttribute('position',new THREE.BufferAttribute(pos,3));geo.setAttribute('pcolor',new THREE.BufferAttribute(col,3));geo.setAttribute('psize',new THREE.BufferAttribute(size,1));geo.setAttribute('palpha',new THREE.BufferAttribute(alpha,1));
  const mat=new THREE.ShaderMaterial({uniforms:{map:{value:T2(tex)},scale:{value:400}},transparent:true,depthWrite:false,blending,
    vertexShader:'attribute vec3 pcolor;attribute float psize;attribute float palpha;varying vec3 vC;varying float vA;uniform float scale;void main(){vC=pcolor;vA=palpha;vec4 mv=modelViewMatrix*vec4(position,1.);gl_PointSize=psize*scale/max(.5,-mv.z);gl_Position=projectionMatrix*mv;}',
    fragmentShader:'uniform sampler2D map;varying vec3 vC;varying float vA;void main(){vec4 t=texture2D(map,gl_PointCoord);float a=t.a*vA;if(a<.01)discard;gl_FragColor=vec4(vC*t.rgb,a);\n#include <encodings_fragment>\n}'});
  const pts=new THREE.Points(geo,mat);pts.frustumCulled=false;pts.renderOrder=5;scene.add(pts);
  const P=[];for(let i=0;i<max;i++)P.push({l:0,ml:1,x:0,y:0,z:0,vx:0,vy:0,vz:0,s0:1,s1:1,r:1,g:1,b:1,gr:0,dr:0});
  let next=0;const tc=new THREE.Color();
  return {mat,spawn(x,y,z,vx,vy,vz,color,s0,s1,life,grav,drag){const p=P[next];next=(next+1)%max;p.x=x;p.y=y;p.z=z;p.vx=vx;p.vy=vy;p.vz=vz;tc.set(color);p.r=tc.r;p.g=tc.g;p.b=tc.b;p.s0=s0;p.s1=s1;p.l=p.ml=life;p.gr=grav||0;p.dr=drag||0;},
    clear(){for(const p of P)p.l=0;},
    update(dt){for(let i=0;i<max;i++){const p=P[i];if(p.l<=0){alpha[i]=0;continue;}p.l-=dt;const k=Math.max(0,1-p.dr*dt);p.vx*=k;p.vy=p.vy*k-p.gr*dt;p.vz*=k;p.x+=p.vx*dt;p.y+=p.vy*dt;p.z+=p.vz*dt;
      const f=Math.max(0,p.l/p.ml);pos[i*3]=p.x;pos[i*3+1]=p.y;pos[i*3+2]=p.z;col[i*3]=p.r;col[i*3+1]=p.g;col[i*3+2]=p.b;size[i]=p.s1+(p.s0-p.s1)*f;alpha[i]=Math.min(1,f*1.6);}
      geo.attributes.position.needsUpdate=geo.attributes.pcolor.needsUpdate=geo.attributes.psize.needsUpdate=geo.attributes.palpha.needsUpdate=true;}};
}
const FXA=particleSystem(560,THREE.AdditiveBlending,TX.spark),FXN=particleSystem(260,THREE.NormalBlending,TX.smoke);
const SPARKC=['#fff1c8','#ffe066','#ff9a1f','#ff3b1a'];
function burst(x,y,z,n,cols,spd,size){for(let i=0;i<n;i++){const a=Math.random()*Math.PI*2,u=Math.random();FXA.spawn(x,y,z,Math.cos(a)*spd*u,spd*(.4+Math.random()*.8),Math.sin(a)*spd*u,cols[i%cols.length],size,size*.3,.6+Math.random()*.4,60,1.5);}}

/* ================= WORLD ================= */
let shakeImp=0;function shake(a){if(!CFG.shake)return;shakeImp=Math.min(1.6,shakeImp+a);}
let world=null,animators=[],boxes=[],pads=[],sky=null,ramps=[],obstacles=[],rollers=[],simTime=0;
const THEMES={
  kitchen:{exposure:1.0,bg:'#3a1c10',fog:['#4a2414',1300,5200],hemi:['#fff1dc','#6b3a1e',.8],sun:['#fff0d8',2.3],dir:[.55,1,.35],env:['#fff6e4','#ffb26a','#7a3a1c','#1e0e08'],roadDark:false},
  bay:{exposure:1.0,bg:'#f1a982',fog:['#f0b08c',2600,11000],hemi:['#ffe2c4','#2d6a7a',.9],sun:['#ffd6a8',2.6],dir:[.8,.45,.25],sky:['#3c6db4','#ffb48a','#2a6f86'],env:['#9cc4ff','#ffc39a','#2e7b8f','#0d3442'],roadDark:false},
  freezer:{exposure:1.05,bg:'#cfe3f5',fog:['#d8e9f7',1700,9500],hemi:['#eef6ff','#7f9fbf',.95],sun:['#ffffff',2.1],dir:[.5,1,.3],sky:['#6fa6de','#eaf5ff','#b9d0e6'],env:['#cfe6ff','#ffffff','#9db8d4','#5a7590'],roadDark:false},
  night:{exposure:1.3,bg:'#0d1024',fog:['#121633',1500,8000],hemi:['#6a7fc8','#140c1c',.55],sun:['#b8ccff',1.05],dir:[-.5,1,.45],sky:['#03040c','#232c5c','#0a0c18'],env:['#2a3a7a','#3a3a6a','#120c1c','#05050a'],roadDark:true}
};
function envFrom(cols,spots){const c=cnv(512,256),g=c.getContext('2d'),gr=g.createLinearGradient(0,0,0,256);gr.addColorStop(0,cols[0]);gr.addColorStop(.42,cols[1]);gr.addColorStop(.55,cols[2]);gr.addColorStop(1,cols[3]);g.fillStyle=gr;g.fillRect(0,0,512,256);
  (spots||[]).forEach(([x,y,r,col])=>{const rg=g.createRadialGradient(x,y,0,x,y,r);rg.addColorStop(0,col);rg.addColorStop(1,'rgba(0,0,0,0)');g.fillStyle=rg;g.fillRect(x-r,y-r,r*2,r*2);});
  const t=new THREE.CanvasTexture(c);t.encoding=THREE.sRGBEncoding;t.mapping=THREE.EquirectangularReflectionMapping;const rt=pmrem.fromEquirectangular(t);t.dispose();return rt.texture;}
function skyDome(cols,sdir,sunCol){const mat=new THREE.ShaderMaterial({side:THREE.BackSide,depthWrite:false,
  uniforms:{top:{value:new THREE.Color(cols[0])},hor:{value:new THREE.Color(cols[1])},bot:{value:new THREE.Color(cols[2])},sunDir:{value:sdir.clone()},sunCol:{value:new THREE.Color(sunCol)}},
  vertexShader:'varying vec3 vW;void main(){vW=normalize(position);gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}',
  fragmentShader:'uniform vec3 top,hor,bot,sunCol,sunDir;varying vec3 vW;void main(){vec3 d=normalize(vW);float h=d.y;vec3 c=h>0.?mix(hor,top,pow(clamp(h,0.,1.),.5)):mix(hor,bot,clamp(-h*5.,0.,1.));float s=max(dot(d,normalize(sunDir)),0.);c+=sunCol*(pow(s,900.)*6.+pow(s,10.)*.35);gl_FragColor=vec4(c,1.);\n#include <tonemapping_fragment>\n#include <encodings_fragment>\n}'});
  const m=new THREE.Mesh(new THREE.SphereGeometry(9000,48,24),mat);m.frustumCulled=false;m.renderOrder=-1;return m;}
function disposeWorld(){if(!world)return;world.traverse(o=>{if(o.geometry)o.geometry.dispose();const ms=o.material?(Array.isArray(o.material)?o.material:[o.material]):[];
  ms.forEach(m=>{if(m===pepMat||SHSET.has(m)||m.userData.shared)return;for(const k of ['map','emissiveMap','normalMap','roughnessMap'])if(m[k]&&!m[k].userData.shared)m[k].dispose();if(m.uniforms&&m.uniforms.map&&m.uniforms.map.value)m.uniforms.map.value.dispose();m.dispose();});});scene.remove(world);world=null;}
function wm(c,o){return new THREE.MeshStandardMaterial(Object.assign({color:c,roughness:.6},o||{}));}
function put(geo,mat,x,y,z,parent,cast){const m=new THREE.Mesh(geo,mat);m.position.set(x||0,y||0,z||0);(parent||world).add(m);m.receiveShadow=true;m.castShadow=cast!==false;return m;}
function strip(j0,j1,o0,o1,y,mat,vLen,cast,tone){const pos=[],uv=[],idx=[],col=tone?[]:null;const cnt=j1-j0,M=Math.max(1,Math.round(Math.abs(o1-o0)/9)),W=M+1;
  for(let k=0;k<=cnt;k++){const j=((j0+k)%N+N)%N,p=track[j],v=(k*T.L/N)/vLen;
    for(let m=0;m<=M;m++){const o=o0+(o1-o0)*m/M,x=p.x+p.nx*o,z=p.y+p.ny*o;pos.push(x,y+groundAt(x,z),z);uv.push(m/M,v);if(col){const t=tone(x,z,o);col.push(t,t,t);}}
    if(k<cnt)for(let m=0;m<M;m++){const a=k*W+m;idx.push(a,a+1,a+W,a+1,a+W+1,a+W);}}
  const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(pos,3));g.setAttribute('uv',new THREE.Float32BufferAttribute(uv,2));g.setIndex(idx);if(col)g.setAttribute('color',new THREE.Float32BufferAttribute(col,3));g.computeVertexNormals();
  const m=new THREE.Mesh(g,mat);m.receiveShadow=true;m.castShadow=!!cast;m.userData.noLift=true;world.add(m);return m;}

function rampTex(){const c=cnv(256,256),g=c.getContext('2d');const gr=g.createLinearGradient(0,0,256,0);gr.addColorStop(0,'#8f2112');gr.addColorStop(.5,'#e0452c');gr.addColorStop(1,'#8f2112');g.fillStyle=gr;g.fillRect(0,0,256,256);
  g.fillStyle='#ffe066';for(let i=0;i<3;i++){const y=i*84+14;g.beginPath();g.moveTo(128,y);g.lineTo(196,y+44);g.lineTo(196,y+66);g.lineTo(128,y+22);g.lineTo(60,y+66);g.lineTo(60,y+44);g.closePath();g.fill();}
  for(let y=0;y<256;y+=32){g.fillStyle='#fff4dc';g.fillRect(0,y,22,16);g.fillRect(234,y+16,22,16);g.fillStyle='#1b0f0b';g.fillRect(0,y+16,22,16);g.fillRect(234,y,22,16);}return c;}
function meatTex(){const c=cnv(256,256),g=c.getContext('2d');g.fillStyle='#6b3a22';g.fillRect(0,0,256,256);for(let i=0;i<900;i++){g.fillStyle=rnd()<.5?'rgba(40,18,8,.55)':'rgba(150,90,60,.5)';g.beginPath();g.arc(rnd()*256,rnd()*256,1+rnd()*5,0,7);g.fill();}
  for(let i=0;i<120;i++){g.fillStyle='#3f7a2a';g.fillRect(rnd()*256,rnd()*256,3,1.5);}return c;}
/* ================= SHORTCUTS: secret side paths that cut across a bend ================= */
let SHORTS=[];const SCW=19;
function nearSC(x,y,r){for(const sc of SHORTS)for(const p of sc.pts)if((p.x-x)**2+(p.y-y)**2<r*r)return true;return false;}
function findShortcuts(def){SHORTS=[];const cd=(a,b)=>{const d=Math.abs(a-b)%N;return Math.min(d,N-d);};
  const bx=def.boxes.map(f=>Math.floor(f*N)),bad=j=>{j=((j%N)+N)%N;const p=track[j];if(p.open||p.wall||p.pond)return true;if(cd(j,0)<45)return true;if(bx.some(b=>cd(b,j)<22))return true;
    if(loopNear(j,45))return true;if(ramps.some(r=>cd(r.j,j)<14))return true;if(pads.some(p2=>cd(p2.j,j)<10))return true;return false;};
  const inSpan=(a,b,j)=>{let d=j-a;if(d<0)d+=N;return d<=((b-a+N)%N);};
  const cands=[];
  for(let a=0;a<N;a+=3){if(bad(a))continue;for(let k=60;k<=420;k+=4){const b=(a+k)%N,pa=track[a],pb=track[b];if(bad(b))continue;
    let ok=true;for(let o=-6;o<=6;o+=2)if(bad(a+o)||bad(b+o)){ok=false;break;}if(!ok)continue;
    if(LOOPS.some(L=>inSpan(a,b,L.j)))continue;if(GLIDE&&inSpan(a,b,GLIDE.rj))continue;if(inSpan(a,b,0))continue;
    const dx=pb.x-pa.x,dy=pb.y-pa.y,D=Math.hypot(dx,dy),TL=k*T.L/N;if(D<110||D>950||D>TL*.8||TL-D<170||TL-D>900)continue;
    const s=Math.sign(dx*pa.nx+dy*pa.ny);if(!s||Math.sign(-dx*pb.nx-dy*pb.ny)!==s)continue;
    cands.push({a,b,k,s,save:TL-D});}}
  cands.sort((x,y)=>Math.abs(x.save-520)-Math.abs(y.save-520));
  for(const c of cands){if(SHORTS.length>=2)break;if(SHORTS.some(o=>cd(o.a,c.a)<N/5||cd(o.b,c.b)<N/5||inSpan(o.a,o.b,c.a)||inSpan(c.a,c.b,o.a)))continue;
    const sc=makePath(c);if(sc)SHORTS.push(sc);}}
function scNear(x,y,th,f,a,b){const t2=th*th;for(let j=0;j<N;j+=2){if(f<.18||f>.82){let da=Math.abs(j-a)%N,db=Math.abs(j-b)%N;da=Math.min(da,N-da);db=Math.min(db,N-db);if((f<.18&&da<30)||(f>.82&&db<30))continue;}
  const p=track[j];if((p.x-x)**2+(p.y-y)**2<t2)return true;}return false;}
function makePath(c){const pa=track[c.a],pb=track[c.b],s=c.s,o=WALLD-10;
  const S=[pa.x+pa.nx*s*o,pa.y+pa.ny*s*o],E=[pb.x+pb.nx*s*o,pb.y+pb.ny*s*o],D=Math.hypot(E[0]-S[0],E[1]-S[1]),h=Math.min(90,D*.32);
  const c1=[S[0]+(pa.tx*.55+pa.nx*s*.85)*h,S[1]+(pa.ty*.55+pa.ny*s*.85)*h],c2=[E[0]+(-pb.tx*.55+pb.nx*s*.85)*h,E[1]+(-pb.ty*.55+pb.ny*s*.85)*h];
  const pts=[],M=200;let L=0,prev=null;const raw=[];
  for(let i=0;i<=M;i++){const t=i/M,u=1-t,x=u*u*u*S[0]+3*u*u*t*c1[0]+3*u*t*t*c2[0]+t*t*t*E[0],y=u*u*u*S[1]+3*u*u*t*c1[1]+3*u*t*t*c2[1]+t*t*t*E[1];if(prev)L+=Math.hypot(x-prev[0],y-prev[1]);raw.push([x,y,L]);prev=[x,y];}
  const n=Math.max(8,Math.round(L/8));let r=0;for(let i=0;i<=n;i++){const tl=L*i/n;while(r<M&&raw[r+1][2]<tl)r++;const A=raw[r],B=raw[Math.min(M,r+1)],f=B[2]>A[2]?(tl-A[2])/(B[2]-A[2]):0;pts.push({x:A[0]+(B[0]-A[0])*f,y:A[1]+(B[1]-A[1])*f});}
  for(let i=0;i<pts.length;i++){const q=pts[Math.min(pts.length-1,i+1)],p0=pts[Math.max(0,i-1)];let tx=q.x-p0.x,ty=q.y-p0.y;const l=Math.hypot(tx,ty)||1;tx/=l;ty/=l;Object.assign(pts[i],{tx,ty,nx:-ty,ny:tx});}
  if(c.k*T.L/N-L<110||c.k*T.L/N-L>620)return null;
  for(let i=0;i<pts.length;i++){const p=pts[i];if(Math.hypot(p.x,p.y)>RIM-SCW-20)return null;if(GLIDE&&pitAt(p.x,p.y)>.5)return null;
    if(scNear(p.x,p.y,WALLD+SCW+5,i/(pts.length-1),c.a,c.b))return null;
    if(LOOPS.some(L=>Math.hypot(p.x-L.p.x,p.y-L.p.y)<(L.full?240:160)))return null;
    for(let j=1;j<pts.length-1;j++){/* sharp kinks */}
    if(obstacles.some(ob=>Math.hypot(ob.x-p.x,ob.y-p.y)<ob.r+SCW+4))return null;
    if(SHORTS.some(o=>o.pts.some(q=>Math.hypot(q.x-p.x,q.y-p.y)<SCW*2+30)))return null;}
  for(let i=1;i<pts.length-1;i++){const a=pts[i-1],b=pts[i+1];if(a.tx*b.tx+a.ty*b.ty<.9)return null;}
  return {a:c.a,b:c.b,s,pts,n:pts.length,L,save:c.k*T.L/N-L};}
function buildShortcut(sc,def){const th=def.theme,road=new THREE.MeshStandardMaterial({map:T2(TX.crust,1,1),color:th==='freezer'?'#e8f2fb':th==='night'?'#9a8a7a':'#e6c79a',roughness:.85});
  const P=sc.pts,pos=[],uv=[],idx=[];let v=0;
  for(let i=0;i<P.length;i++){const p=P[i],vv=i*8/30;for(const sd of [-1,1]){const x=p.x+p.nx*SCW*sd,z=p.y+p.ny*SCW*sd;pos.push(x,groundAt(x,z)+.12,z);uv.push(sd<0?0:1.4,vv);}if(i<P.length-1){const a=i*2;idx.push(a,a+1,a+2,a+1,a+3,a+2);}}
  const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(pos,3));g.setAttribute('uv',new THREE.Float32BufferAttribute(uv,2));g.setIndex(idx);g.computeVertexNormals();
  const m=new THREE.Mesh(g,road);m.receiveShadow=true;m.userData.noLift=true;world.add(m);
  /* low rails of bread sticks along both sides, with a gap at each end */
  const wp=[],wc=[],cA=new THREE.Color('#c98b4e'),cB=new THREE.Color('#e2b070'),cK=new THREE.Color('#5a3a20'),H=3.4,TH=2;
  const tri=(a,b,c,cl)=>{for(const q of [a,b,c]){wp.push(q[0],q[1],q[2]);wc.push(cl.r,cl.g,cl.b);}},quad=(a,b,c,d,cl)=>{tri(a,b,c,cl);tri(a,c,d,cl);};
  for(const sd of [-1,1])for(let i=2;i<P.length-3;i++){const p=P[i],q=P[i+1],at=(pt,o,hh)=>{const x=pt.x+pt.nx*o*sd,z=pt.y+pt.ny*o*sd;return [x,groundAt(x,z)+hh,z];},cl=(i>>1)%2?cA:cB;
    quad(at(p,SCW+1,-.4),at(q,SCW+1,-.4),at(q,SCW+1,H),at(p,SCW+1,H),cl);quad(at(p,SCW+1,H),at(q,SCW+1,H),at(q,SCW+1+TH,H),at(p,SCW+1+TH,H),cA);quad(at(p,SCW+1+TH,H),at(q,SCW+1+TH,H),at(q,SCW+1+TH,-.4),at(p,SCW+1+TH,-.4),cK);}
  const wg=new THREE.BufferGeometry();wg.setAttribute('position',new THREE.Float32BufferAttribute(wp,3));wg.setAttribute('color',new THREE.Float32BufferAttribute(wc,3));wg.computeVertexNormals();
  const wm2=new THREE.Mesh(wg,new THREE.MeshStandardMaterial({vertexColors:true,roughness:.6,side:THREE.DoubleSide}));wm2.castShadow=true;wm2.receiveShadow=true;wm2.userData.noLift=true;world.add(wm2);
  /* little lanterns marking the secret entrance */
  const glow=new THREE.MeshBasicMaterial({color:'#9dff7a',toneMapped:false}),pole=wm('#3a2a20',{roughness:.6});
  for(const end of [0,P.length-1])for(const sd of [-1,1]){const p=P[end],x=p.x+p.nx*(SCW+4)*sd,z=p.y+p.ny*(SCW+4)*sd,gy=groundAt(x,z);
    const g2=new THREE.Group();g2.position.set(x,gy,z);g2.userData.noLift=true;world.add(g2);put(new THREE.CylinderGeometry(.5,.6,9,8),pole,0,4.5,0,g2);put(new THREE.SphereGeometry(1.4,12,8),glow,0,9.6,0,g2,false);}
  /* a few herb tufts and crumbs on the path edges so it reads as a hidden trail */
  for(let i=4;i<P.length-4;i+=3)for(const sd of [-1,1])if(rnd()<.6){const p=P[i],x=p.x+p.nx*(SCW+6+rnd()*6)*sd,z=p.y+p.ny*(SCW+6+rnd()*6)*sd;const b=put(new THREE.SphereGeometry(2+rnd()*1.5,8,6),wm('#3f8a35',{roughness:.5}),x,groundAt(x,z)+1,z);b.scale.y=.6;b.userData.noLift=true;}}
/* per-step: karts on a shortcut follow its own path for progress and walls */
function scStep(k){if(!SHORTS.length)return;
  if(k.sc){const sc=k.sc,P=sc.pts;let bi=k.scI,bd=1e18;for(let i=Math.max(0,k.scI-3);i<=Math.min(sc.n-1,k.scI+6);i++){const d=(P[i].x-k.x)**2+(P[i].y-k.y)**2;if(d<bd){bd=d;bi=i;}}k.scI=bi;
    const p=P[bi],along=(k.x-p.x)*p.tx+(k.y-p.y)*p.ty,off=(k.x-p.x)*p.nx+(k.y-p.y)*p.ny;
    const ni=sc.a+Math.round(bi/(sc.n-1)*((sc.b-sc.a+N)%N)),nidx=ni%N;let di=nidx-k.idx;if(di>N/2)di-=N;if(di<-N/2)di+=N;k.prog+=di;k.idx=nidx;
    if((bi>=sc.n-1&&along>0)||(bi>=sc.n-3&&Math.abs(off)>SCW-4)){k.sc=null;k.idx=sc.b;return;}
    if(bi<=2&&(along<-2||Math.abs(off)>SCW+2)){k.sc=null;k.idx=sc.a;return;}
    const lim=SCW-3.5;if(Math.abs(off)>lim&&bi>2&&bi<sc.n-3){const sg=Math.sign(off),ov=Math.abs(off)-lim,nx=p.nx*sg,ny=p.ny*sg;k.x-=nx*ov;k.y-=ny*ov;
      const vx=Math.cos(k.ma),vy=Math.sin(k.ma),dot=vx*nx+vy*ny;if(dot>0){k.speed*=1-.2*dot;const tx=vx-dot*nx,ty=vy-dot*ny;if(Math.hypot(tx,ty)>.05){const na=Math.atan2(ty,tx);k.ma=na;k.a+=angDiff(na,k.a)*.5;}}}
    return;}
  for(const sc of SHORTS){let dj=k.idx-sc.a;if(dj>N/2)dj-=N;if(dj<-N/2)dj+=N;if(Math.abs(dj)>9)continue;const P=sc.pts;
    const pj=track[k.idx],lat=((k.x-pj.x)*pj.nx+(k.y-pj.y)*pj.ny)*sc.s,mouth=Math.abs(dj)<=4&&lat>WALLD-16;
    for(let i=0;i<8;i++){const p=P[i],off=(k.x-p.x)*p.nx+(k.y-p.y)*p.ny,al=(k.x-p.x)*p.tx+(k.y-p.y)*p.ty;
      if((Math.abs(off)<SCW-1&&Math.abs(al)<9||mouth&&Math.abs(off)<SCW+4&&Math.abs(al)<12)&&Math.cos(k.ma)*p.tx+Math.sin(k.ma)*p.ty>-.1){k.sc=sc;k.scI=i;if(k===player&&!sc.found){sc.found=true;showBanner('Shortcut!',1);SFX.ring();}return;}}}}

function glideTex(){const c=cnv(256,256),g=c.getContext('2d');const gr=g.createLinearGradient(0,0,256,0);gr.addColorStop(0,'#0e4f7a');gr.addColorStop(.5,'#2fb4ff');gr.addColorStop(1,'#0e4f7a');g.fillStyle=gr;g.fillRect(0,0,256,256);
  g.fillStyle='#ffffff';for(let i=0;i<3;i++){const y=i*84+14;g.beginPath();g.moveTo(128,y);g.lineTo(196,y+44);g.lineTo(196,y+66);g.lineTo(128,y+22);g.lineTo(60,y+66);g.lineTo(60,y+44);g.closePath();g.fill();}
  for(let y=0;y<256;y+=32){g.fillStyle='#fff4dc';g.fillRect(0,y,22,16);g.fillRect(234,y+16,22,16);g.fillStyle='#7fe8ff';g.fillRect(0,y+16,22,16);g.fillRect(234,y,22,16);}return c;}
function glideSignTex(){const c=cnv(512,96),g=c.getContext('2d');const gr=g.createLinearGradient(0,0,0,96);gr.addColorStop(0,'#1a6fa8');gr.addColorStop(1,'#0b3352');g.fillStyle=gr;g.fillRect(0,0,512,96);
  g.strokeStyle='#7fe8ff';g.lineWidth=6;g.strokeRect(6,6,500,84);g.fillStyle='#fff4dc';g.font='bold 58px "Arial Black",Impact,sans-serif';g.textAlign='center';g.textBaseline='middle';g.fillText('GLIDE',256,52);
  g.fillStyle='#7fe8ff';for(const s of [-1,1]){g.beginPath();g.moveTo(256+s*120,30);g.lineTo(256+s*200,48);g.lineTo(256+s*120,66);g.lineTo(256+s*150,48);g.closePath();g.fill();}return c;}

/* the road surface carried up and around a built-in loop, with glowing chevrons down the middle */
function loopDeckMat(def){const c=cnv(256,512),g=c.getContext('2d');const dark=def.theme==='night';g.fillStyle=dark?'#24262c':'#3b3e44';g.fillRect(0,0,256,512);
  for(let i=0;i<5000;i++){const v=40+Math.random()*50;g.fillStyle='rgb('+v+','+v+','+(v+4)+')';g.fillRect(Math.random()*256,Math.random()*512,1.5,1.5);}
  g.fillStyle='#f2f2ee';g.fillRect(6,0,10,512);g.fillRect(240,0,10,512);g.fillStyle='#ff8a1f';for(let y=0;y<512;y+=128){g.beginPath();g.moveTo(96,y+90);g.lineTo(128,y+40);g.lineTo(160,y+90);g.lineTo(144,y+90);g.lineTo(128,y+64);g.lineTo(112,y+90);g.closePath();g.fill();}
  const t=T2(c,1,1);t.wrapT=THREE.RepeatWrapping;return new THREE.MeshStandardMaterial({map:t,emissive:'#ff6a1a',emissiveMap:(()=>{const e=cnv(256,512),ge=e.getContext('2d');ge.fillStyle='#000';ge.fillRect(0,0,256,512);ge.drawImage(c,0,0);ge.globalCompositeOperation='multiply';ge.fillStyle='#ff8a1f';ge.fillRect(0,0,256,512);return T2(e,1,1);})(),emissiveIntensity:.25,roughness:.6,envMapIntensity:.5,side:THREE.DoubleSide});}
/* low walls that narrow the road into the loop's entry lane */
function buildFunnel(L,def){const pos=[],col=[],cA=new THREE.Color(def.theme==='night'?'#3a6fd8':'#d6301e'),cB=new THREE.Color('#f4efe4'),H=4.6;
  const tri=(a,b,c,cl)=>{for(const v of [a,b,c]){pos.push(v[0],v[1],v[2]);col.push(cl.r,cl.g,cl.b);}};
  for(const side of ['flo','fhi'])for(let o=-56;o<0;o++){const p=track[(L.j+o+N)%N],q=track[(L.j+o+1+N)%N];if(p[side]===undefined||q[side]===undefined)continue;
    const at=(pt,h)=>{const l=pt[side],X=pt.x+pt.nx*l,Z=pt.y+pt.ny*l;return [X,groundAt(X,Z)+h,Z];};const a0=at(p,-.5),a1=at(p,H),b0=at(q,-.5),b1=at(q,H),cl=((o>>2)%2)?cA:cB;tri(a0,b0,b1,cl);tri(a0,b1,a1,cl);}
  const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(pos,3));g.setAttribute('color',new THREE.Float32BufferAttribute(col,3));g.computeVertexNormals();
  const m=new THREE.Mesh(g,new THREE.MeshStandardMaterial({vertexColors:true,roughness:.5,side:THREE.DoubleSide}));m.castShadow=true;m.receiveShadow=true;m.userData.noLift=true;world.add(m);}
function buildGlide(def){const G=GLIDE,gt=T2(glideTex());
  const topM=new THREE.MeshStandardMaterial({map:gt,emissive:'#2fa8ff',emissiveMap:gt,emissiveIntensity:.35,roughness:.4}),sideM=new THREE.MeshStandardMaterial({map:T2(TX.crust,1,1),roughness:.7,side:THREE.DoubleSide});
  const r={j:G.rj,len:4*T.L/N,w:CURB+2,h:16,glide:true};ramps.push(r);buildRamp(r,topM,sideM);
  const nx=-G.uy,ny=G.ux,VW=G.W+70,crustM=new THREE.MeshStandardMaterial({map:T2(TX.crust,1,1),roughness:.75,side:THREE.DoubleSide});
  const face=(p,dir)=>{const pos=[],uv=[];const at=vv=>{const x=p.x+nx*vv-G.ux*dir*.8,z=p.y+ny*vv-G.uy*dir*.8,top=groundAt(x,z)+.1;let l=Math.min(1,(VW-Math.abs(vv))/70);l=l*l*(3-2*l);return [x,top,z,top-G.D*l-3];};
    for(let v=-VW;v<VW;v+=10){const A=at(v),B=at(v+10),ua=v/40,ub=(v+10)/40;pos.push(A[0],A[1],A[2],B[0],B[1],B[2],B[0],B[3],B[2],A[0],A[1],A[2],B[0],B[3],B[2],A[0],A[3],A[2]);
      uv.push(ua,0,ub,0,ub,(B[1]-B[3])/40,ua,0,ub,(B[1]-B[3])/40,ua,(A[1]-A[3])/40);}
    const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(pos,3));g.setAttribute('uv',new THREE.Float32BufferAttribute(uv,2));g.computeVertexNormals();const m=new THREE.Mesh(g,crustM);m.receiveShadow=true;m.userData.noLift=true;world.add(m);};
  face(G.p,1);face(track[G.j1],-1);
  const pc={kitchen:['#c53b22','#7d1d0e'],bay:['#157f9b','#0b4a5c'],night:['#4a34c8','#3a1aff'],freezer:['#9fe0ff','#3a9adf']}[def.theme];
  const pcv=cnv(256,256),pg2=pcv.getContext('2d');pg2.fillStyle=pc[0];pg2.fillRect(0,0,256,256);for(let i=0;i<70;i++){const x=rnd()*256,y=rnd()*256,r=4+rnd()*16;pg2.fillStyle=rnd()<.5?'rgba(0,0,0,.18)':'rgba(255,255,255,.16)';pg2.beginPath();pg2.arc(x,y,r,0,7);pg2.fill();pg2.strokeStyle='rgba(255,255,255,.25)';pg2.lineWidth=2;pg2.beginPath();pg2.arc(x,y,r*.6,0,7);pg2.stroke();}
  const ptx=T2(pcv,G.L/90,(2*G.W+40)/90),poolM=new THREE.MeshStandardMaterial({map:ptx,emissive:pc[1],emissiveIntensity:.3,roughness:.12,metalness:.1});
  const pool=new THREE.Mesh(new THREE.PlaneGeometry(G.L+10,2*G.W+40),poolM);pool.rotation.set(-Math.PI/2,0,-Math.atan2(G.uy,G.ux));pool.position.set(G.p.x+G.ux*G.L/2,(G.long?Math.min(G.y0,G.y1):G.y)-G.D+5,G.p.y+G.uy*G.L/2);pool.userData.noLift=true;world.add(pool);
  animators.push((t,dt)=>{poolM.emissiveIntensity=.25+Math.sin(t*2)*.1;ptx.offset.x+=dt*.03;ptx.offset.y+=dt*.02;});
  // rings placed on the path a typical glide takes
  const sp=150,tg=G.long?[.12,.27,.42,.57,.72,.87]:[.3,.55,.8],hs=[];let u=0,y=G.y+16,vy=55+sp*.08,ti=0;while(u<G.L&&ti<tg.length){const dt=1/60;vy-=70*dt;if(vy<-15)vy+=(-15-vy)*Math.min(1,dt*4);u+=sp*dt;y+=vy*dt;if(u>=G.L*tg[ti]){hs.push(Math.max(y,G.y+14));ti++;}}
  const ringM=new THREE.MeshBasicMaterial({color:'#7fe8ff',toneMapped:false}),ringG=new THREE.TorusGeometry(15,1.1,10,44);G.rings=[];
  tg.forEach((f,i)=>{if(G.long)hs[i]=glideY(G.p.x+G.ux*G.L*f,G.p.y+G.uy*G.L*f)+10+(1-f)*14;const lat=[0,-12,12][i%3],x=G.p.x+G.ux*G.L*f+nx*lat,z=G.p.y+G.uy*G.L*f+ny*lat,yy=(hs[i]||G.y+30)+4;
    const m=new THREE.Mesh(ringG,ringM);m.position.set(x,yy,z);m.rotation.y=Math.atan2(G.ux,G.uy);m.userData.noLift=true;world.add(m);G.rings.push({x,y:yy,z,m});});
  animators.push(t=>{G.rings.forEach((r,i)=>r.m.scale.setScalar(1+Math.sin(t*4+i)*.05));});
  const sg=new THREE.Group();sg.userData.noLift=true;world.add(sg);const sgp=track[(G.rj-3+N)%N],gy=groundAt(sgp.x,sgp.y),postM=wm('#1a3b52',{metalness:.5,roughness:.35});
  for(const sd of [-1,1]){const x=sgp.x+sgp.nx*(CURB+8)*sd,z=sgp.y+sgp.ny*(CURB+8)*sd;put(new THREE.CylinderGeometry(2.4,2.8,34,14),postM,x,gy+17,z,sg);put(new THREE.SphereGeometry(2.8,14,10),ringM,x,gy+35,z,sg);}
  const st=T2(glideSignTex()),stM=new THREE.MeshStandardMaterial({map:st,emissive:'#ffffff',emissiveMap:st,emissiveIntensity:.35,roughness:.5}),dk=wm('#0b3352');
  const bn=new THREE.Mesh(new THREE.BoxGeometry(2*CURB+22,12,1.6),[dk,dk,dk,dk,stM,stM]);bn.position.set(sgp.x,gy+29,sgp.y);bn.rotation.y=-Math.PI/2-sgp.ang;bn.castShadow=true;sg.add(bn);}
function buildRamp(r,topM,sideM){const K=4,pos=[],uv=[],spos=[],P=[];
  for(let k=0;k<=K;k++){const p=track[(r.j+k)%N],h=r.h*k/K;const gp=(x,hh,z)=>[x,hh+groundAt(x,z),z],lx=p.x-p.nx*r.w,lz=p.y-p.ny*r.w,rx=p.x+p.nx*r.w,rz=p.y+p.ny*r.w;P.push({L:gp(lx,h,lz),R:gp(rx,h,rz),L0:gp(lx,-1,lz),R0:gp(rx,-1,rz),v:k/K});}
  const push=(arr,...vs)=>vs.forEach(v=>arr.push(v[0],v[1],v[2]));
  for(let k=0;k<K;k++){const a=P[k],b=P[k+1];push(pos,a.L,a.R,b.L,a.R,b.R,b.L);uv.push(0,a.v,1,a.v,0,b.v,1,a.v,1,b.v,0,b.v);
    push(spos,a.L0,a.L,b.L,a.L0,b.L,b.L0,a.R0,b.R,a.R,a.R0,b.R0,b.R);}
  const e=P[K];push(spos,e.L0,e.R0,e.R,e.L0,e.R,e.L);
  const tg=new THREE.BufferGeometry();tg.setAttribute('position',new THREE.Float32BufferAttribute(pos,3));tg.setAttribute('uv',new THREE.Float32BufferAttribute(uv,2));tg.computeVertexNormals();
  const sg=new THREE.BufferGeometry();sg.setAttribute('position',new THREE.Float32BufferAttribute(spos,3));const su=new Float32Array(spos.length/3*2);for(let i=0;i<su.length/2;i++){su[i*2]=(spos[i*3]+spos[i*3+2])*.03;su[i*2+1]=spos[i*3+1]*.1;}
  sg.setAttribute('uv',new THREE.BufferAttribute(su,2));sg.computeVertexNormals();
  const tm=new THREE.Mesh(tg,topM),sm=new THREE.Mesh(sg,sideM);tm.castShadow=sm.castShadow=true;tm.receiveShadow=sm.receiveShadow=true;tm.userData.noLift=sm.userData.noLift=true;world.add(tm);world.add(sm);}
const OBST={
  kitchen:()=>{const wood=new THREE.MeshStandardMaterial({color:'#6e3f1f',roughness:.35}),metal=wm('#d4d8db',{metalness:1,roughness:.2}),pr0=new THREE.Group();
    P3(new THREE.CylinderGeometry(5.6,6.6,4,24),metal,0,2,0,pr0);P3(new THREE.CylinderGeometry(5,6,16,24),wood,0,12,0,pr0);P3(new THREE.CylinderGeometry(6.2,6.2,1.6,24),metal,0,20.6,0,pr0);
    P3(new THREE.SphereGeometry(5,24,16),wood,0,23,0,pr0);P3(new THREE.SphereGeometry(1.7,12,8),metal,0,28,0,pr0);bake(pr0);return ()=>pr0.clone();},
  bay:()=>{const wood=wm('#8a5a32',{roughness:.6}),band=wm('#3a2414',{roughness:.5}),leaf=wm('#3f9a35',{roughness:.45}),pr0=new THREE.Group();
    const prof=[[0,0],[5.6,0],[6.4,6],[6.6,12],[6.4,18],[5.6,22],[0,22]].map(([x,y])=>new THREE.Vector2(x,y));P3(new THREE.LatheGeometry(prof,28),wood,0,0,0,pr0);
    for(const y of [4,11,18]){const t=P3(new THREE.TorusGeometry(6.5,.45,8,28),band,0,y,0,pr0);t.rotation.x=Math.PI/2;}
    for(let i=0;i<7;i++){const a=i/7*Math.PI*2,l=P3(new THREE.ConeGeometry(1.6,10,6),leaf,Math.cos(a)*2,27,Math.sin(a)*2,pr0);l.rotation.set(Math.sin(a)*.6,0,-Math.cos(a)*.6);}bake(pr0);return ()=>pr0.clone();},
  freezer:()=>{const ice=wm('#cdeeff',{roughness:.05,metalness:.2}),metal=wm('#aab4c0',{metalness:.9,roughness:.25}),pr0=new THREE.Group();
    P3(new THREE.CylinderGeometry(5.4,6.4,24,8),ice,0,12,0,pr0);for(const y of [3,21])P3(new THREE.TorusGeometry(6,.7,8,24),metal,0,y,0,pr0).rotation.x=Math.PI/2;P3(new THREE.OctahedronGeometry(4.5,0),ice,0,28,0,pr0);bake(pr0);return ()=>pr0.clone();},
  night:()=>{const metal=wm('#2a2c38',{metalness:.7,roughness:.35}),glow=new THREE.MeshBasicMaterial({color:'#7fd0ff',toneMapped:false}),pr0=new THREE.Group();
    P3(new THREE.CylinderGeometry(5,6,24,24),metal,0,12,0,pr0);P3(new THREE.SphereGeometry(5,24,12,0,Math.PI*2,0,Math.PI/2),metal,0,24,0,pr0);
    for(const y of [8,18]){const t=P3(new THREE.TorusGeometry(5.6,.6,8,28),glow,0,y,0,pr0);t.rotation.x=Math.PI/2;}bake(pr0);return ()=>pr0.clone();}
};
const CELL=560;
function lowPoly(g){const p=g.parameters||{},T=g.type;let n=null;
  if(T==='SphereGeometry'&&(p.widthSegments>12||p.heightSegments>8))n=new THREE.SphereGeometry(p.radius,Math.min(12,p.widthSegments),Math.min(8,p.heightSegments),p.phiStart,p.phiLength,p.thetaStart,p.thetaLength);
  else if(T==='CylinderGeometry'&&p.radialSegments>14)n=new THREE.CylinderGeometry(p.radiusTop,p.radiusBottom,p.height,14,1,p.openEnded);
  else if(T==='TorusGeometry'&&(p.radialSegments>8||p.tubularSegments>18))n=new THREE.TorusGeometry(p.radius,p.tube,Math.min(8,p.radialSegments),Math.min(18,p.tubularSegments),p.arc);
  if(n){g.dispose();return n;}return g;}
function chunkInst(geo,mat,items,opt){opt=opt||{};if(!items.length){geo.dispose();return;}
  if(DBK&&canVC(mat)&&!opt.inst){const t=tplOf([[lowPoly(geo),mat.color]]);for(const it of items)dbAddM(t,it.m,it.c,!opt.noLift);geo.dispose();mat.dispose();return;}
  const cells=new Map();
  for(const it of items){const k=Math.floor(it.x/CELL)+','+Math.floor(it.z/CELL);if(!cells.has(k))cells.set(k,[]);cells.get(k).push(it);}
  geo.computeBoundingSphere();const br=geo.boundingSphere.radius*(opt.maxScale||1)+(opt.extra||0);
  for(const [k,list] of cells){const [cx,cz]=k.split(',').map(Number);const g=new THREE.BufferGeometry();for(const n in geo.attributes)g.setAttribute(n,geo.attributes[n]);if(geo.index)g.setIndex(geo.index);
    g.boundingSphere=new THREE.Sphere(new THREE.Vector3((cx+.5)*CELL,opt.cy||0,(cz+.5)*CELL),CELL*.71+br);
    const im=new THREE.InstancedMesh(g,mat,list.length);list.forEach((it,i)=>{if(!opt.noLift){const gy=groundAt(it.x,it.z);if(gy)it.m.elements[13]+=gy;}im.setMatrixAt(i,it.m);if(it.c)im.setColorAt(i,it.c);});
    im.castShadow=!!opt.cast;im.receiveShadow=opt.receive!==false;world.add(im);}}
let curRev=false;
/* ================= TRACK IDENTITY: every track gets its own sky, light and landmarks, even within a theme ================= */
let VAR=0,CURID='';
const VARLOOK={
  basil:{bg:'#2a1a12',fog:['#3a2418',2200,8200],hemi:['#fff4e2','#5a3020',.85],sun:['#ffe8c8',2.0],exposure:1.0},
  oven:{bg:'#1a0904',fog:['#3a1406',1200,5200],hemi:['#ffb070','#3a1004',.8],sun:['#ffa458',1.7],dir:[.3,1,.2],exposure:1.06},
  spiral:{bg:'#28323a',fog:['#3a4450',2000,7600],hemi:['#eef4ff','#5a4a40',.9],sun:['#fff6e8',2.1],exposure:1.0},
  lagoon:{fog:['#bfe6ff',3200,14000],hemi:['#e8f6ff','#2d8aa0',1.0],sun:['#fffaf0',2.7],dir:[.4,1,.3],pano:'sky_beach',water:'#22b6c4'},
  calzone:{fog:['#cfe6ff',3200,13000],hemi:['#eaf4ff','#3a7a5a',.95],sun:['#fff2dc',2.6],dir:[.6,.8,.2],pano:'sky_anime',water:'#1f8fb0'},
  tour:{fog:['#c9dcff',3000,13000],hemi:['#eef4ff','#4a8a5a',.95],sun:['#ffffff',2.5],dir:[.3,1,.5],pano:'sky_mc',water:'#2a74b8'},
  mozz:{fog:['#1a0e2a',1600,8400],hemi:['#9a7ad8','#1a0c1c',.62],sun:['#e0c8ff',1.1],pano:'sky_nebula'},
  napoli:{bg:'#1a1030',fog:['#2a1838',1500,8000],hemi:['#ffb0c8','#1a0c1c',.62],sun:['#ffc890',1.15],dir:[.8,.35,.3],sky:['#120a2a','#ff7a5a','#1a0c20']},
  moon:{fog:['#0a2228',1300,7000],hemi:['#7fe0e8','#0a1418',.62],sun:['#a8fff4',1.0],dir:[.2,1,.4],pano:'sky_cave'},
  burn:{bg:'#cfe0ec',fog:['#d4e4ef',2600,8600],hemi:['#eef8ff','#7f98ae',.78],sun:['#f4fbff',1.5],exposure:.9},
  glacier:{bg:'#0a1430',fog:['#14224a',1800,10000],hemi:['#8fb0ff','#1a2440',.5],sun:['#bcd4ff',.95],dir:[-.4,.9,.3],sky:['#040a1e','#1a3a6a','#0a1a30'],exposure:.95},
  peak:{fog:['#ffd2b8',2400,11000],hemi:['#ffe0d0','#7a8fb0',.9],sun:['#ffb888',2.3],dir:[.9,.32,.2],sky:['#5a7ad0','#ffb48a','#d0a0b0']}};
function panoSky(name,tint,rot){const m=new THREE.MeshBasicMaterial({map:propTex(name),side:THREE.BackSide,fog:false,depthWrite:false,toneMapped:false,color:tint||'#ffffff'});
  const s=new THREE.Mesh(new THREE.SphereGeometry(9000,64,32),m);s.renderOrder=-1;s.frustumCulled=false;s.rotation.y=rot||0;return s;}
const ROD=new THREE.CylinderGeometry(1,1,1,8);function vRod(mat,a,b,parent,r){const m=limb(ROD,mat,a,b,parent);m.scale.x=m.scale.z=r||3;m.castShadow=false;return m;}
/* bake a scenery group into a few merged meshes, but keep sprites, points and anything flagged keep (animated) as live objects */
function safeBake(S){S.updateMatrixWorld(true);const keep=[];S.traverse(o=>{if(o!==S&&(o.userData.keep||o.isSprite||o.isPoints))keep.push(o);});
  const top=keep.filter(o=>{let p=o.parent;while(p&&p!==S){if(keep.includes(p))return false;p=p.parent;}return true;});
  top.forEach(o=>{o.matrixWorld.decompose(o.position,o.quaternion,o.scale);o.parent.remove(o);world.add(o);o.userData.noLift=true;});bake(S,false);}
const VG=()=>{const g=new THREE.Group();g.userData.noLift=true;world.add(g);return g;};
const atA=(a,d)=>[Math.cos(a)*d,Math.sin(a)*d];
function glowSprite(col,size,op,parent,x,y,z){const s=new THREE.Sprite(new THREE.SpriteMaterial({map:T2(TX.glow),color:col,transparent:true,opacity:op??.6,depthWrite:false,blending:THREE.AdditiveBlending,toneMapped:false}));s.scale.setScalar(size);s.position.set(x||0,y||0,z||0);(parent||world).add(s);return s;}
function vLathe(pts,seg){return new THREE.LatheGeometry(pts.map(([x,y])=>new THREE.Vector2(x,y)),seg||32);}
function texCanvas(w,h,f){const c=cnv(w,h);f(c.getContext('2d'),w,h);return c;}
/* a window in a room wall that looks out onto one of the sky panoramas */
function roomWindow(parent,a,Rw,y,w,h,sky,frameCol){const g=new THREE.Group();const [x,z]=atA(a,Rw-8);g.position.set(x,y,z);g.lookAt(0,y,0);parent.add(g);
  const base=propTex(sky),t=new THREE.Texture(base.image);t.encoding=THREE.sRGBEncoding;{const up=()=>t.needsUpdate=true;if(base.image.complete&&base.image.naturalWidth)up();else base.image.addEventListener('load',up);}t.repeat.set(.18,.42);t.offset.set((a/(Math.PI*2))%1,.3);t.wrapS=THREE.RepeatWrapping;
  put(new THREE.PlaneGeometry(w,h),new THREE.MeshBasicMaterial({map:t,toneMapped:false,fog:false}),0,0,0,g,false);
  const fm=wm(frameCol||'#f3ead8',{roughness:.5});for(const yy of [-h/2,0,h/2])put(new THREE.BoxGeometry(w+40,20,30),fm,0,yy,10,g,false);for(const xx of [-w/2,0,w/2])put(new THREE.BoxGeometry(20,h+20,30),fm,xx,0,10,g,false);return g;}
function roomShell(R,o){const Rw=o.Rw||R+1700,fy=o.floorY??-60,H=o.H||2200,g=VG();
  const fl=put(new THREE.PlaneGeometry(Rw*2.4,Rw*2.4),o.floor,0,fy,0,g,false);fl.rotation.x=-Math.PI/2;fl.receiveShadow=true;
  put(new THREE.CylinderGeometry(Rw,Rw,H,120,1,true),o.wall,0,fy+H/2,0,g,false);
  const ce=put(new THREE.CircleGeometry(Rw,80),o.ceil,0,fy+H,0,g,false);ce.rotation.x=Math.PI/2;return {g,Rw,fy,H};}
function stripeWall(c1,c2,band){return texCanvas(512,512,(g,w,h)=>{g.fillStyle=c1;g.fillRect(0,0,w,h);for(let x=0;x<w;x+=64){g.fillStyle=c2;g.fillRect(x,0,26,h);}
  g.fillStyle='rgba(255,255,255,.12)';for(let y=20;y<h;y+=64)for(let x=45;x<w;x+=64){g.beginPath();g.arc(x,y,6,0,7);g.fill();}if(band){g.fillStyle=band;g.fillRect(0,h*.62,w,26);g.fillStyle='rgba(0,0,0,.25)';g.fillRect(0,h*.62+26,w,4);}});}
/* ---------------- KITCHEN ROOMS ---------------- */
function roomDining(R,L1,L2){/* the pizza is served on a long dining table: the track runs across the tablecloth */
  const gingham=texCanvas(256,256,(g,w,h)=>{g.fillStyle='#fff8ee';g.fillRect(0,0,w,h);g.fillStyle='rgba(200,38,27,.55)';for(let i=0;i<8;i++){g.fillRect(i*32,0,16,h);g.fillRect(0,i*32,w,16);}});
  const clothT=T2(gingham,40,40),wallT=T2(stripeWall('#2f5a3a','#2a5034','#c9a86a'),48,4);
  const Rt=R+1100,floorY=-760,{g:S}=roomShell(R,{Rw:R+2700,floorY,H:3200,floor:new THREE.MeshStandardMaterial({map:T2(woodTex(),30,30),roughness:.55}),wall:new THREE.MeshStandardMaterial({map:wallT,side:THREE.BackSide,roughness:.85}),ceil:wm('#f4ead8',{roughness:.9})});
  const cloth=new THREE.MeshStandardMaterial({map:clothT,roughness:.9}),top=put(new THREE.CylinderGeometry(Rt,Rt,30,120),cloth,0,-75,0,S,false);top.receiveShadow=true;
  const sk=T2(gingham,60,6);put(new THREE.CylinderGeometry(Rt+10,Rt+60,560,120,1,true),new THREE.MeshStandardMaterial({map:sk,roughness:.95,side:THREE.DoubleSide}),0,-370,0,S,false);
  const chairW=wm('#5a3420',{roughness:.6}),seatC=wm('#8a1f1a',{roughness:.7});
  for(let i=0;i<12;i++){const a=i/12*Math.PI*2,[x,z]=atA(a,Rt+330),c=new THREE.Group();c.position.set(x,floorY,z);c.lookAt(0,floorY,0);S.add(c);
    put(new THREE.BoxGeometry(300,40,280),seatC,0,330,0,c,false);for(const [lx,lz] of [[-120,-110],[120,-110],[-120,110],[120,110]])put(new THREE.BoxGeometry(26,330,26),chairW,lx,165,lz,c,false);
    put(new THREE.BoxGeometry(300,520,30),chairW,0,610,-140,c,false);put(new THREE.BoxGeometry(220,300,20),seatC,0,620,-125,c,false);}
  const glass=new THREE.MeshPhysicalMaterial({color:'#eaf6ff',roughness:.02,metalness:0,clearcoat:1,transparent:true,opacity:.28,envMapIntensity:1.6,side:THREE.DoubleSide}),wine=new THREE.MeshPhysicalMaterial({color:'#6a0f1c',roughness:.1,clearcoat:1,transparent:true,opacity:.85});
  const silver=wm('#d8dce2',{metalness:1,roughness:.18}),plate=wm('#fbfaf6',{roughness:.25}),wax=wm('#fff2d6',{roughness:.6}),gold=wm('#c9a050',{metalness:1,roughness:.25});
  const T=VG();const onT=(a,d)=>{const [x,z]=atA(a,d);return [x,-60,z];};
  for(const [a,d] of [[.4,R+260],[2.2,R+520],[4.4,R+330]]){const [x,y,z]=onT(a,d);put(vLathe([[0,0],[130,0],[130,8],[20,20],[16,260],[60,300],[150,420],[160,620],[150,620],[140,430],[60,320],[0,310]],40),glass,x,y,z,T,false);
    put(vLathe([[0,320],[60,330],[138,430],[150,520],[0,520]],40),wine,x,y,z,T,false);}
  for(const [a,d] of [[1.2,R+300],[3.3,R+260],[5.5,R+380]]){const [x,y,z]=onT(a,d);put(new THREE.CylinderGeometry(110,130,40,32),gold,x,y+20,z,T,false);put(new THREE.CylinderGeometry(40,40,380,24),wax,x,y+230,z,T,false);
    const f=put(new THREE.ConeGeometry(18,60,12),new THREE.MeshBasicMaterial({color:'#ffd27a',toneMapped:false}),x,y+450,z,T,false);f.userData.keep=true;const gs=glowSprite('#ffb84a',260,.55,T,x,y+460,z);animators.push(t=>{const k=1+Math.sin(t*13+x)*.08+Math.random()*.05;f.scale.set(1,k,1);gs.material.opacity=.45+Math.random()*.15;});}
  for(const [a,d] of [[.9,R+640],[2.8,R+700],[3.9,R+620],[5.0,R+700]]){const [x,y,z]=onT(a,d);put(new THREE.CylinderGeometry(300,260,20,48),plate,x,y+10,z,T,false);put(new THREE.TorusGeometry(260,14,8,48),plate,x,y+22,z,T,false).rotation.x=Math.PI/2;
    const ang=-a;const fk=put(new THREE.BoxGeometry(30,8,420),silver,x+Math.cos(ang)*360,y+6,z+Math.sin(ang)*360,T,false);fk.rotation.y=-ang;const kn=put(new THREE.BoxGeometry(40,8,440),silver,x-Math.cos(ang)*360,y+6,z-Math.sin(ang)*360,T,false);kn.rotation.y=-ang;}
  {const [x,y,z]=onT(1.9,R+380);put(new THREE.CylinderGeometry(70,70,260,24),wm('#f4f4f2'),x,y+130,z,T,false);put(new THREE.SphereGeometry(70,24,12,0,Math.PI*2,0,Math.PI/2),silver,x,y+260,z,T,false);
    put(new THREE.CylinderGeometry(70,70,260,24),wm('#1a1a1a'),x+190,y+130,z,T,false);put(new THREE.SphereGeometry(70,24,12,0,Math.PI*2,0,Math.PI/2),silver,x+190,y+260,z,T,false);}
  {const [x,y,z]=onT(4.9,R+420);put(new THREE.TorusGeometry(200,40,12,40),wm('#b07a44',{roughness:.7}),x,y+40,z,T,false).rotation.x=Math.PI/2;for(let i=0;i<6;i++)put(new THREE.SphereGeometry(90,20,14),wm('#e2b06a',{roughness:.7}),x+(rnd()-.5)*200,y+90,z+(rnd()-.5)*200,T,false).scale.set(1.5,.7,1);}
  safeBake(T);
  const CH=new THREE.Group();CH.position.y=1900;S.add(CH);put(new THREE.TorusGeometry(520,26,12,64),gold,0,0,0,CH,false).rotation.x=Math.PI/2;put(new THREE.CylinderGeometry(8,8,600,8),gold,0,300,0,CH,false);
  for(let i=0;i<14;i++){const a=i/14*Math.PI*2;put(new THREE.SphereGeometry(30,14,10),new THREE.MeshBasicMaterial({color:'#fff1c4',toneMapped:false}),Math.cos(a)*520,40,Math.sin(a)*520,CH,false);glowSprite('#ffd890',220,.45,CH,Math.cos(a)*520,40,Math.sin(a)*520);}
  for(const a of [.3,1.9,3.5,5.1])roomWindow(S,a,R+2700,900,820,1100,'sky_anime','#e8dcc0');
  const curt=wm('#7a1a1a',{roughness:.85,side:THREE.DoubleSide});for(const a of [.3,1.9,3.5,5.1])for(const sd of [-1,1]){const [x,z]=atA(a+sd*.19,R+2680);const c=put(new THREE.PlaneGeometry(300,1500),curt,x,900,z,S,false);c.lookAt(0,900,0);}
  for(const a of [1.1,2.7,4.3,5.9]){const [x,z]=atA(a,R+2690),f=new THREE.Group();f.position.set(x,1000,z);f.lookAt(0,1000,0);S.add(f);put(new THREE.BoxGeometry(600,440,20),gold,0,0,0,f,false);
    put(new THREE.PlaneGeometry(540,380),new THREE.MeshStandardMaterial({map:T2(texCanvas(256,180,(g,w,h)=>{g.fillStyle=['#2a4a6a','#6a3a2a','#3a5a3a','#5a4a2a'][Math.floor(a)%4];g.fillRect(0,0,w,h);g.fillStyle='#e2b06a';g.beginPath();g.arc(w/2,h/2,60,0,7);g.fill();g.fillStyle='#c8261b';for(let i=0;i<7;i++){g.beginPath();g.arc(w/2+Math.cos(i)*34,h/2+Math.sin(i*1.7)*30,10,0,7);g.fill();}})),roughness:.6}),0,0,12,f,false);}
  safeBake(S);
  if(L1){const g=new THREE.Group();g.position.set(L1[0],0,L1[1]);world.add(g);put(new THREE.CylinderGeometry(22,28,140,24),wm('#1a1a1a',{roughness:.3}),0,70,0,g);put(new THREE.SphereGeometry(26,20,14),silver,0,150,0,g);put(new THREE.CylinderGeometry(6,6,30,10),silver,0,180,0,g);bake(g);animators.push((t,dt)=>{g.rotation.y+=dt*.5;});}
  if(L2){const ol=put(new THREE.TorusGeometry(40,18,24,48),wm('#2a2230',{roughness:.15,metalness:.15}),L2[0],58,L2[1]);animators.push((t,dt)=>{ol.rotation.y+=dt*.4;});}}
function roomOven(R,L1,L2){/* racing inside the wood-fired oven itself */
  const fb=texCanvas(512,256,(g,w,h)=>{g.fillStyle='#2a1208';g.fillRect(0,0,w,h);for(let r=0;r<8;r++)for(let i=-1;i<5;i++){const x=i*128+(r%2?64:0),y=r*32,v=rnd();g.fillStyle=v<.33?'#6a2a14':v<.66?'#7a3418':'#55210f';g.fillRect(x+3,y+3,122,26);g.fillStyle='rgba(255,140,60,'+(.04+rnd()*.12)+')';g.fillRect(x+3,y+3,122,6);}
    for(let i=0;i<80;i++){g.fillStyle='rgba(0,0,0,'+(.15+rnd()*.3)+')';g.beginPath();g.arc(rnd()*w,rnd()*h,4+rnd()*30,0,7);g.fill();}});
  const S=VG(),Rw=R+1800,fl=put(new THREE.PlaneGeometry(Rw*2.2,Rw*2.2),new THREE.MeshStandardMaterial({map:T2(slateTex(),80,80),color:'#9a6a48',roughness:.9}),0,-60,0,S,false);fl.rotation.x=-Math.PI/2;
  const dome=put(new THREE.SphereGeometry(Rw,96,32,0,Math.PI*2,0,Math.PI/2),new THREE.MeshStandardMaterial({map:T2(fb,40,14),side:THREE.BackSide,roughness:.95,emissive:'#3a0e02',emissiveIntensity:.35}),0,-60,0,S,false);dome.scale.y=.6;
  {const mouth=new THREE.Group();const [x,z]=atA(0,Rw-30);mouth.position.set(x,-60,z);mouth.lookAt(0,-60,0);S.add(mouth);
    const kv=texCanvas(512,256,(g,w,h)=>{const gr=g.createLinearGradient(0,0,0,h);gr.addColorStop(0,'#ffe2b0');gr.addColorStop(1,'#c88a5a');g.fillStyle=gr;g.fillRect(0,0,w,h);g.fillStyle='rgba(90,50,30,.5)';for(let i=0;i<6;i++)g.fillRect(i*90+10,h*.45,60,h*.55);g.fillStyle='rgba(255,255,255,.4)';g.fillRect(0,h*.3,w,6);});
    const sh=new THREE.Shape();sh.moveTo(-700,0);sh.lineTo(-700,500);sh.absarc(0,500,700,Math.PI,0,true);sh.lineTo(700,0);sh.closePath();
    put(new THREE.ShapeGeometry(sh,24),new THREE.MeshBasicMaterial({map:T2(kv),toneMapped:false,fog:false}),0,0,0,mouth,false);glowSprite('#ffd6a0',2200,.25,mouth,0,600,200);}
  const fires=[],logM=wm('#4a2a16',{roughness:.9}),ember=new THREE.MeshStandardMaterial({color:'#ff5a14',emissive:'#ff3a08',emissiveIntensity:2.2,roughness:.6}),flameM=new THREE.MeshBasicMaterial({color:'#ffb040',transparent:true,opacity:.85,blending:THREE.AdditiveBlending,depthWrite:false,toneMapped:false});
  for(const a of [Math.PI*.8,Math.PI,Math.PI*1.2]){const [x,z]=atA(a,Rw*.78),g=new THREE.Group();g.position.set(x,-60,z);g.userData.keep=true;S.add(g);
    put(new THREE.SphereGeometry(420,28,12),ember,0,-300,0,g,false).scale.set(1,.85,1);for(let i=0;i<7;i++){const l=put(new THREE.CylinderGeometry(55,60,700,12),logM,(rnd()-.5)*300,80+i*30,(rnd()-.5)*300,g,false);l.rotation.set(Math.PI/2,rnd()*3,rnd()*.5);}
    for(let i=0;i<5;i++){const f=put(new THREE.ConeGeometry(120,600,12,1,true),flameM,(rnd()-.5)*260,330,(rnd()-.5)*260,g,false);f.userData.p=rnd()*6;fires.push(f);}
    glowSprite('#ff7a2a',1800,.5,g,0,300,0);}
  animators.push(t=>{fires.forEach(f=>{const k=.8+.35*Math.sin(t*7+f.userData.p)+Math.random()*.15;f.scale.set(1,k,1);f.position.y=270+k*80;});ember.emissiveIntensity=2+Math.sin(t*3)*.3;});
  {const n=500,pos=new Float32Array(n*3),vel=[];for(let i=0;i<n;i++){const a=Math.PI*(.75+rnd()*.5),[x,z]=atA(a,Rw*(.6+rnd()*.3));pos[i*3]=x;pos[i*3+1]=rnd()*1200;pos[i*3+2]=z;vel.push(40+rnd()*120);}
    const gg=new THREE.BufferGeometry();gg.setAttribute('position',new THREE.BufferAttribute(pos,3));const pm=new THREE.PointsMaterial({color:'#ffa040',size:4,sizeAttenuation:false,transparent:true,opacity:.9,blending:THREE.AdditiveBlending,depthWrite:false});const P=new THREE.Points(gg,pm);P.frustumCulled=false;world.add(P);
    animators.push((t,dt)=>{for(let i=0;i<n;i++){pos[i*3+1]+=vel[i]*dt;pos[i*3]+=Math.sin(t+i)*dt*20;if(pos[i*3+1]>1300)pos[i*3+1]=-40;}gg.attributes.position.needsUpdate=true;});}
  {const coal=new THREE.InstancedMesh(new THREE.DodecahedronGeometry(1,0),new THREE.MeshStandardMaterial({color:'#1a1210',roughness:.9,emissive:'#ff3a08',emissiveIntensity:.0}),160),m4=new THREE.Matrix4(),q=new THREE.Quaternion(),c=new THREE.Color();
    for(let i=0;i<160;i++){const a=rnd()*6.28,[x,z]=atA(a,R+120+rnd()*900),s=12+rnd()*30;q.setFromEuler(new THREE.Euler(rnd()*3,rnd()*3,0));m4.compose(new THREE.Vector3(x,-60+s*.4,z),q,new THREE.Vector3(s,s*.7,s));coal.setMatrixAt(i,m4);coal.setColorAt(i,c.setHSL(.04,.6,rnd()<.25?.45:.08));}
    coal.frustumCulled=false;world.add(coal);}
  safeBake(S);
  if(L1){const g=new THREE.Group();g.position.set(L1[0],0,L1[1]);world.add(g);const w=wm('#b07a44',{roughness:.6});put(new THREE.CylinderGeometry(90,90,8,40),w,0,140,0,g).rotation.x=1.2;put(new THREE.CylinderGeometry(8,10,320,12),w,0,60,-120,g).rotation.x=-.4;bake(g);}
  if(L2){const ol=put(new THREE.TorusGeometry(40,18,24,48),wm('#2a2230',{roughness:.15,metalness:.15}),L2[0],58,L2[1]);animators.push((t,dt)=>{ol.rotation.y+=dt*.4;});}}
function roomParty(R,L1,L2){/* a pizza party on the living-room rug */
  const wallT=T2(stripeWall('#bcd6ea','#b2cde2','#ffffff'),44,4),rugT=T2(texCanvas(512,512,(g,w,h)=>{const cols=['#e0452c','#f7c948','#2f7fd8','#3f9a35','#fff4dc'];for(let r=8;r>0;r--){g.fillStyle=cols[r%5];g.beginPath();g.arc(w/2,h/2,r*31,0,7);g.fill();}}));
  const {g:S,Rw}=roomShell(R,{Rw:R+1900,H:2400,floor:new THREE.MeshStandardMaterial({map:T2(woodTex(),28,28),roughness:.5}),wall:new THREE.MeshStandardMaterial({map:wallT,side:THREE.BackSide,roughness:.85}),ceil:wm('#fbfaf6',{roughness:.9})});
  const rug=put(new THREE.CircleGeometry(R+700,96),new THREE.MeshStandardMaterial({map:rugT,roughness:.95}),0,-59,0,S,false);rug.rotation.x=-Math.PI/2;
  {const [x,z]=atA(.2,R+1250),g=new THREE.Group();g.position.set(x,-60,z);g.lookAt(0,-60,0);S.add(g);const fab=wm('#2a8a8a',{roughness:.85}),cush=wm('#34a0a0',{roughness:.8});
    put(new THREE.BoxGeometry(1700,300,600),fab,0,150,0,g,false);for(const sd of [-1,1])put(new THREE.BoxGeometry(220,520,640),fab,sd*960,260,0,g,false);put(new THREE.BoxGeometry(1700,600,200),fab,0,560,-260,g,false);
    for(const sd of [-1,0,1]){put(new THREE.BoxGeometry(540,120,520),cush,sd*560,360,30,g,false);put(new THREE.BoxGeometry(220,220,60),wm(['#f7c948','#e0452c','#fff4dc'][sd+1]),sd*560,520,-150,g,false).rotation.z=sd*.1;}}
  {const [x,z]=atA(Math.PI+.2,R+1400),g=new THREE.Group();g.position.set(x,-60,z);g.lookAt(0,-60,0);S.add(g);put(new THREE.BoxGeometry(1500,380,420),wm('#6b3f22'),0,190,0,g,false);
    put(new THREE.BoxGeometry(1700,980,60),wm('#111114',{roughness:.3,metalness:.4}),0,980,0,g,false);
    const tv=texCanvas(512,288,(c,w,h)=>{const gr=c.createLinearGradient(0,0,0,h);gr.addColorStop(0,'#5aa0ff');gr.addColorStop(.55,'#ffd4a0');gr.addColorStop(.56,'#c8321e');gr.addColorStop(1,'#7a1a10');c.fillStyle=gr;c.fillRect(0,0,w,h);c.fillStyle='#fff';c.font='900 52px system-ui';c.textAlign='center';c.fillText('CRUST RUSH',w/2,70);c.fillStyle='#ffd23a';for(let i=0;i<5;i++){c.fillRect(w/2-4,170+i*24,8,14);}c.fillStyle='#e0452c';c.fillRect(w/2-30,230,60,34);});
    put(new THREE.PlaneGeometry(1620,900),new THREE.MeshBasicMaterial({map:T2(tv),toneMapped:false}),0,980,32,g,false);glowSprite('#9fc8ff',2400,.2,g,0,980,120);}
  {const [x,z]=atA(2.1,R+1500),g=new THREE.Group();g.position.set(x,-60,z);S.add(g);put(new THREE.CylinderGeometry(120,140,30,24),wm('#2a2a2a'),0,15,0,g,false);put(new THREE.CylinderGeometry(10,10,1300,10),wm('#c9a050',{metalness:1,roughness:.3}),0,650,0,g,false);
    put(new THREE.CylinderGeometry(160,260,300,24,1,true),wm('#f4e8cc',{roughness:.8,side:THREE.DoubleSide}),0,1330,0,g,false);glowSprite('#ffe0a0',900,.35,g,0,1250,0);}
  const fan=new THREE.Group();fan.position.y=2240;fan.userData.keep=true;S.add(fan);put(new THREE.CylinderGeometry(70,90,80,20),wm('#f4f4f2'),0,0,0,fan,false);for(let i=0;i<5;i++){const b=put(new THREE.BoxGeometry(700,10,140),wm('#8a5a30'),Math.cos(i*1.257)*380,-20,Math.sin(i*1.257)*380,fan,false);b.rotation.y=-i*1.257;}
  animators.push((t,dt)=>{fan.rotation.y+=dt*1.6;});
  for(const a of [1.2,4.0,5.2])roomWindow(S,a,Rw,1100,900,1000,'sky_mc','#ffffff');
  const B=VG(),bal=[];for(let i=0;i<16;i++){const a=rnd()*6.28,[x,z]=atA(a,R+250+rnd()*900),h=300+rnd()*500,col=['#e0452c','#f7c948','#2f7fd8','#3f9a35','#ff6fae','#9a5ad8'][i%6];
    const g=new THREE.Group();g.position.set(x,-60+h,z);B.add(g);put(new THREE.SphereGeometry(80,24,18),new THREE.MeshPhysicalMaterial({color:col,roughness:.2,clearcoat:1}),0,0,0,g,false).scale.y=1.18;put(new THREE.ConeGeometry(14,24,8),wm(col),0,-96,0,g,false).rotation.x=Math.PI;
    put(new THREE.CylinderGeometry(1.5,1.5,h-100,4),wm('#ffffff'),0,-(h-100)/2-100,0,g,false);g.userData.p=rnd()*6;g.userData.y=-60+h;bal.push(g);}
  animators.push(t=>{bal.forEach(g=>{g.position.y=g.userData.y+Math.sin(t*1.2+g.userData.p)*14;g.rotation.z=Math.sin(t*.8+g.userData.p)*.06;});});
  {const cups=VG();for(const [a,d,c] of [[.9,R+300,'#e0452c'],[2.6,R+340,'#2f7fd8'],[3.8,R+290,'#3f9a35'],[5.6,R+330,'#f7c948']]){const [x,z]=atA(a,d);put(new THREE.CylinderGeometry(80,60,260,28),wm(c,{roughness:.4}),x,70,z,cups,false);put(new THREE.CylinderGeometry(84,84,20,28),wm('#ffffff'),x,200,z,cups,false);put(new THREE.CylinderGeometry(8,8,240,8),wm('#ffffff'),x+20,280,z,cups,false).rotation.z=.2;}
    const [x,z]=atA(4.7,R+420),ctl=new THREE.Group();ctl.position.set(x,-30,z);ctl.rotation.y=.6;cups.add(ctl);put(new THREE.BoxGeometry(320,50,160),wm('#2a2a33',{roughness:.4}),0,0,0,ctl,false);for(const sd of [-1,1])put(new THREE.SphereGeometry(90,20,14),wm('#2a2a33',{roughness:.4}),sd*170,-6,30,ctl,false).scale.y=.45;
    for(const [bx,bz,c] of [[90,-20,'#e0452c'],[120,10,'#3f9a35'],[60,10,'#2f7fd8']])put(new THREE.CylinderGeometry(14,14,18,12),wm(c),bx,30,bz,ctl,false);bake(cups,false);}
  safeBake(S);
  if(L1){const g=new THREE.Group();g.position.set(L1[0],0,L1[1]);world.add(g);for(let i=0;i<5;i++){const a=i/5*6.28;put(new THREE.SphereGeometry(30,18,14),new THREE.MeshPhysicalMaterial({color:['#e0452c','#f7c948','#2f7fd8','#3f9a35','#ff6fae'][i],roughness:.2,clearcoat:1}),Math.cos(a)*30,190+i*6,Math.sin(a)*30,g).scale.y=1.2;}
    put(new THREE.CylinderGeometry(1,1,180,4),wm('#fff'),0,90,0,g);put(new THREE.BoxGeometry(30,20,30),wm('#c8261b'),0,10,0,g);animators.push((t,dt)=>{g.rotation.y+=dt*.3;});}
  if(L2){const ol=put(new THREE.TorusGeometry(40,18,24,48),wm('#2a2230',{roughness:.15,metalness:.15}),L2[0],58,L2[1]);animators.push((t,dt)=>{ol.rotation.y+=dt*.4;});}}
/* ---------------- BAY EXTRAS ---------------- */
function sailboat(g,x,z,s,col){const b=new THREE.Group();b.position.set(x,-14,z);b.scale.setScalar(s);b.rotation.y=rnd()*6;g.add(b);put(new THREE.BoxGeometry(160,30,50),wm('#f4f4f2'),0,10,0,b,false);put(new THREE.ConeGeometry(25,40,4),wm('#f4f4f2'),95,10,0,b,false).rotation.z=-Math.PI/2;
  put(new THREE.CylinderGeometry(2.5,2.5,220,6),wm('#6b4a2a'),0,130,0,b,false);const sh=new THREE.Shape();sh.moveTo(0,0);sh.lineTo(0,190);sh.lineTo(110,0);sh.closePath();put(new THREE.ShapeGeometry(sh),wm(col,{side:THREE.DoubleSide,roughness:.7}),4,30,0,b,false);b.userData.p=rnd()*6;return b;}
function bayExtras(R,L1){const v=VAR,G=VG(),boats=[];
  if(v===1){/* lighthouse cape, pier and beach huts */
    const [lx,lz]=atA(1.1,R+900),lh=new THREE.Group();lh.position.set(lx,-14,lz);G.add(lh);put(new THREE.SphereGeometry(260,24,10,0,Math.PI*2,0,Math.PI/2),wm('#7a7068',{roughness:.95}),0,-40,0,lh,false);
    for(let i=0;i<6;i++)put(new THREE.CylinderGeometry(70-i*6,76-i*6,90,24),wm(i%2?'#f4f4f2':'#c8261b',{roughness:.5}),0,120+i*90,0,lh,false);
    put(new THREE.CylinderGeometry(48,48,70,16),new THREE.MeshPhysicalMaterial({color:'#fff6c8',emissive:'#ffe080',emissiveIntensity:1.5,transparent:true,opacity:.8}),0,700,0,lh,false);put(new THREE.ConeGeometry(60,70,16),wm('#2a2a2a'),0,770,0,lh,false);
    const beam=new THREE.Mesh(new THREE.ConeGeometry(120,1600,16,1,true),new THREE.MeshBasicMaterial({color:'#fff4c0',transparent:true,opacity:.12,blending:THREE.AdditiveBlending,depthWrite:false,side:THREE.DoubleSide,fog:false}));beam.geometry.translate(0,-800,0);beam.rotation.z=Math.PI/2;const bp=new THREE.Group();bp.position.y=700;bp.add(beam);lh.add(bp);animators.push((t,dt)=>{bp.rotation.y+=dt*.8;});
    const [px,pz]=atA(2.6,R+500),pier=new THREE.Group();pier.position.set(px,-14,pz);pier.lookAt(0,-14,0);G.add(pier);for(let i=0;i<14;i++){put(new THREE.BoxGeometry(160,10,46),wm('#9a6a3a',{roughness:.8}),0,24,-200-i*48,pier,false);if(i%3===0)for(const sd of [-1,1])put(new THREE.CylinderGeometry(8,8,60,8),wm('#6b4a2a'),sd*74,0,-200-i*48,pier,false);}
    const hutC=['#ff6fae','#2fd0ff','#f7c948','#3f9a35','#ff8a1f'];for(let i=0;i<5;i++){const [hx,hz]=atA(2.9+i*.09,R+420),h=new THREE.Group();h.position.set(hx,-14,hz);h.lookAt(0,-14,0);G.add(h);put(new THREE.BoxGeometry(90,90,80),wm(hutC[i]),0,45,0,h,false);put(new THREE.ConeGeometry(70,50,4),wm('#fff4dc'),0,115,0,h,false).rotation.y=Math.PI/4;}
    for(let i=0;i<5;i++){const [x,z]=atA(rnd()*6.28,R+1100+rnd()*1600);boats.push(sailboat(G,x,z,1.4+rnd(),['#fff4dc','#e0452c','#2f7fd8','#f7c948'][i%4]));}}
  if(v===2){/* a smoking volcano island and drifting hot-air balloons */
    const [vx,vz]=atA(.5,R+3800),vg=new THREE.Group();vg.position.set(vx,-20,vz);G.add(vg);put(new THREE.ConeGeometry(1700,1500,48,6,true),wm('#5a4a3a',{roughness:.95}),0,730,0,vg,false);put(new THREE.ConeGeometry(1900,260,48),wm('#3f8a35',{roughness:.9}),0,110,0,vg,false);
    const lava=new THREE.MeshStandardMaterial({color:'#ff5a14',emissive:'#ff3a08',emissiveIntensity:2.4});put(new THREE.CylinderGeometry(260,300,40,32),lava,0,1440,0,vg,false);for(let i=0;i<5;i++){const a=i/5*6.28+.3,s=put(new THREE.BoxGeometry(40,900,30),lava,Math.cos(a)*700,1000,Math.sin(a)*700,vg,false);s.lookAt(0,1000,0);s.rotateX(-.85);}
    glowSprite('#ff7a2a',1800,.45,vg,0,1500,0);const smk=[],sm=new THREE.SpriteMaterial({map:cloudTex(),color:'#5a5450',transparent:true,opacity:.6,depthWrite:false,fog:false});for(let i=0;i<10;i++){const s=new THREE.Sprite(sm.clone());s.userData.p=i/10;vg.add(s);smk.push(s);}
    animators.push((t,dt)=>{smk.forEach(s=>{const k=(t*.05+s.userData.p)%1;s.position.set(Math.sin(k*5)*200,1500+k*1800,Math.cos(k*3)*150);s.scale.set(500+k*1500,300+k*900,1);s.material.opacity=.6*(1-k);});lava.emissiveIntensity=2.2+Math.sin(t*2)*.3;});
    for(let i=0;i<6;i++){const [x,z]=atA(i/6*6.28+.4,R+1400+rnd()*1800),b=new THREE.Group();b.position.set(x,700+rnd()*700,z);G.add(b);const tx=T2(stripeTex(['#e0452c','#2f7fd8','#f7c948','#3f9a35','#ff6fae','#9a5ad8'][i],'#fff4dc',12));
      put(new THREE.SphereGeometry(120,24,18),new THREE.MeshStandardMaterial({map:tx,roughness:.6}),0,0,0,b,false).scale.y=1.2;put(new THREE.BoxGeometry(50,40,50),wm('#8a5a30'),0,-200,0,b,false);for(const [sx,sz] of [[-20,-20],[20,-20],[-20,20],[20,20]])vRod(wm('#3a2a1a'),[sx*2.5,-110,sz*2.5],[sx,-180,sz],b,1.5);
      b.userData.p=rnd()*6;b.userData.y=b.position.y;animators.push(t=>{b.position.y=b.userData.y+Math.sin(t*.4+b.userData.p)*40;b.rotation.y+=.0015;});}}
  if(v===3){/* seaside amusement pier: ferris wheel, coaster and carousel */
    const [fx,fz]=atA(1.2,R+1300),fw=new THREE.Group();fw.position.set(fx,-14,fz);fw.lookAt(0,-14,0);G.add(fw);const st=wm('#f4f4f2',{metalness:.4,roughness:.4});for(const sd of [-1,1])for(const lr of [-1,1])vRod(st,[lr*260,0,sd*60],[0,620,sd*60],fw,12);
    const wheel=new THREE.Group();wheel.position.y=620;fw.add(wheel);put(new THREE.TorusGeometry(540,10,8,80),wm('#e0452c',{metalness:.3}),0,0,0,wheel,false);for(let i=0;i<16;i++){const a=i/16*6.28;vRod(st,[0,0,0],[Math.cos(a)*540,Math.sin(a)*540,0],wheel,4);}
    const cars=[];for(let i=0;i<12;i++){const a=i/12*6.28,c=put(new THREE.BoxGeometry(60,60,70),wm(['#f7c948','#2f7fd8','#3f9a35','#ff6fae'][i%4]),Math.cos(a)*540,Math.sin(a)*540-40,0,wheel,false);cars.push(c);}
    const lights=[];for(let i=0;i<48;i++){const a=i/48*6.28;lights.push(Math.cos(a)*545,Math.sin(a)*545,8);}const lg=new THREE.BufferGeometry();lg.setAttribute('position',new THREE.Float32BufferAttribute(lights,3));wheel.add(new THREE.Points(lg,new THREE.PointsMaterial({color:'#fff1a0',size:5,sizeAttenuation:false})));
    animators.push((t,dt)=>{wheel.rotation.z+=dt*.12;cars.forEach(c=>c.rotation.z=-wheel.rotation.z);});
    const [cx,cz]=atA(3.9,R+1500),cs=new THREE.Group();cs.position.set(cx,-14,cz);G.add(cs);const pts=[];for(let i=0;i<=64;i++){const a=i/64*6.28;pts.push(new THREE.Vector3(Math.cos(a)*700,140+Math.sin(a*3)*110+Math.cos(a*5)*50,Math.sin(a)*380));}
    const crv=new THREE.CatmullRomCurve3(pts,true);put(new THREE.TubeGeometry(crv,200,14,8,true),wm('#2f7fd8',{metalness:.4,roughness:.35}),0,0,0,cs,false);for(let i=0;i<24;i++){const p=crv.getPoint(i/24);put(new THREE.CylinderGeometry(6,6,p.y,6),st,p.x,p.y/2,p.z,cs,false);}
    const train=put(new THREE.BoxGeometry(80,40,40),wm('#e0452c'),0,0,0,cs,false);animators.push(t=>{const k=(t*.06)%1,p=crv.getPoint(k),q2=crv.getPoint((k+.01)%1);train.position.set(p.x,p.y+26,p.z);train.lookAt(q2.x,q2.y+26,q2.z);});
    const [ux,uz]=atA(2.4,R+700),cr=new THREE.Group();cr.position.set(ux,-14,uz);G.add(cr);put(new THREE.CylinderGeometry(220,230,30,32),wm('#f4f4f2'),0,15,0,cr,false);put(new THREE.ConeGeometry(260,160,24),new THREE.MeshStandardMaterial({map:T2(stripeTex('#e0452c','#fff4dc',12)),roughness:.6}),0,300,0,cr,false);put(new THREE.CylinderGeometry(20,20,200,12),wm('#c9a050',{metalness:1,roughness:.3}),0,120,0,cr,false);
    const horses=[];for(let i=0;i<8;i++){const a=i/8*6.28,h=put(new THREE.BoxGeometry(50,40,20),wm(['#fff4dc','#ffd23a'][i%2]),Math.cos(a)*170,90,Math.sin(a)*170,cr,false);horses.push(h);}animators.push((t,dt)=>{cr.rotation.y+=dt*.4;horses.forEach((h,i)=>h.position.y=90+Math.sin(t*3+i)*14);});
    for(let i=0;i<4;i++){const [x,z]=atA(rnd()*6.28,R+1000+rnd()*1500);boats.push(sailboat(G,x,z,1.3+rnd(),['#e0452c','#fff4dc','#3f9a35','#2f7fd8'][i]));}}
  if(boats.length)animators.push(t=>{boats.forEach(b=>{b.position.y=-14+Math.sin(t*1.1+b.userData.p)*4;b.rotation.z=Math.sin(t*.9+b.userData.p)*.06;});});}
/* ---------------- NIGHT EXTRAS ---------------- */
function nightExtras(R,L1){const v=VAR,G=VG();
  if(v===1){/* a pizza-delivery saucer over the observatory hill */
    const [ux,uz]=atA(.8,R+1100),u=new THREE.Group();u.position.set(ux,520,uz);G.add(u);put(new THREE.SphereGeometry(200,40,12),wm('#c9ced6',{metalness:.9,roughness:.2}),0,0,0,u,false).scale.y=.22;
    put(new THREE.SphereGeometry(80,24,14,0,Math.PI*2,0,Math.PI/2),new THREE.MeshPhysicalMaterial({color:'#a8f0ff',roughness:.05,transparent:true,opacity:.55,clearcoat:1}),0,20,0,u,false);
    const rl=[];for(let i=0;i<12;i++){const a=i/12*6.28,b=put(new THREE.SphereGeometry(10,10,8),new THREE.MeshBasicMaterial({color:'#7fffb0',toneMapped:false}),Math.cos(a)*190,-8,Math.sin(a)*190,u,false);rl.push(b);}
    const bm=new THREE.Mesh(new THREE.ConeGeometry(160,560,24,1,true),new THREE.MeshBasicMaterial({color:'#9fffcf',transparent:true,opacity:.14,blending:THREE.AdditiveBlending,depthWrite:false,side:THREE.DoubleSide}));bm.position.y=-300;u.add(bm);
    animators.push((t,dt)=>{u.rotation.y+=dt*.6;u.position.y=520+Math.sin(t*.8)*30;rl.forEach((b,i)=>b.material.color.setHSL(((t*.3+i/12)%1),1,.65));});
    for(const [a,d] of [[.6,R+1500],[1.0,R+1800]]){const [x,z]=atA(a,d),o=new THREE.Group();o.position.set(x,-60,z);G.add(o);put(new THREE.CylinderGeometry(160,170,200,32),wm('#e8e8ee'),0,100,0,o,false);
      put(new THREE.SphereGeometry(160,32,16,0,Math.PI*2,0,Math.PI/2),wm('#c9ced6',{metalness:.7,roughness:.3}),0,200,0,o,false);put(new THREE.BoxGeometry(40,170,330),wm('#141418'),0,280,0,o,false).rotation.z=.5;glowSprite('#ffe9a0',200,.4,o,0,120,170);}
    const [tx,tz]=atA(5.4,R+1700),tw=new THREE.Group();tw.position.set(tx,-60,tz);G.add(tw);const st=wm('#8a8f99',{metalness:.6});for(let i=0;i<3;i++){const a=i/3*6.28;vRod(st,[Math.cos(a)*90,0,Math.sin(a)*90],[0,1200,0],tw,8);}
    for(let k=0;k<8;k++)put(new THREE.TorusGeometry(90-k*10,3,4,3),st,0,k*140,0,tw,false).rotation.x=Math.PI/2;const blink=put(new THREE.SphereGeometry(16,10,8),new THREE.MeshBasicMaterial({color:'#ff3a2a',toneMapped:false}),0,1210,0,tw,false);animators.push(t=>{blink.visible=Math.sin(t*4)>0;});}
  if(v===2){/* night market: pagodas, lantern strings and sky lanterns */
    for(let i=0;i<4;i++){const [x,z]=atA(i/4*6.28+.6,R+900+(i%2)*500),p=new THREE.Group();p.position.set(x,-60,z);p.rotation.y=rnd()*6;G.add(p);
      for(let k=0;k<5;k++){const w=320-k*50,y=k*170;put(new THREE.BoxGeometry(w*.7,150,w*.7),wm('#5a1a1a',{roughness:.7}),0,y+75,0,p,false);put(new THREE.ConeGeometry(w*.75,70,4,1),wm('#1a1a22',{roughness:.6}),0,y+180,0,p,false).rotation.y=Math.PI/4;
        put(new THREE.TorusGeometry(w*.53,4,4,4),new THREE.MeshBasicMaterial({color:'#ff4fa8',toneMapped:false}),0,y+150,0,p,false).rotation.set(Math.PI/2,0,Math.PI/4);}
      glowSprite('#ff6aa8',700,.25,p,0,500,0);}
    const ln=[];for(let k=0;k<26;k++){const a0=k/26*6.28,a1=(k+1)/26*6.28,r=R+160;for(let i=0;i<10;i++){const f=i/10,a=a0+(a1-a0)*f,[x,z]=atA(a,r);ln.push(x,90-Math.sin(f*Math.PI)*40,z);}}
    const lg=new THREE.BufferGeometry();lg.setAttribute('position',new THREE.Float32BufferAttribute(ln,3));const lm=new THREE.PointsMaterial({color:'#ffb050',size:7,sizeAttenuation:false,toneMapped:false});const LP=new THREE.Points(lg,lm);LP.frustumCulled=false;G.add(LP);
    animators.push(t=>{lm.color.setHSL(.07+Math.sin(t*.7)*.03,1,.6);});
    const n=60,pos=new Float32Array(n*3);for(let i=0;i<n;i++){const [x,z]=atA(rnd()*6.28,R+300+rnd()*2500);pos[i*3]=x;pos[i*3+1]=rnd()*2500;pos[i*3+2]=z;}const sg=new THREE.BufferGeometry();sg.setAttribute('position',new THREE.BufferAttribute(pos,3));
    const SL=new THREE.Points(sg,new THREE.PointsMaterial({color:'#ffc070',size:9,sizeAttenuation:false,transparent:true,opacity:.9,fog:false}));SL.frustumCulled=false;G.add(SL);animators.push((t,dt)=>{for(let i=0;i<n;i++){pos[i*3+1]+=dt*(20+(i%5)*8);if(pos[i*3+1]>2600)pos[i*3+1]=0;}sg.attributes.position.needsUpdate=true;});}
  if(v===3){/* a glowing crystal cave on the moon */
    const cols=['#3ff0ff','#c86bff','#5affb0','#ff6ad8'],cm2=cols.map(c=>new THREE.MeshStandardMaterial({color:c,emissive:c,emissiveIntensity:1.4,roughness:.15,metalness:.1,transparent:true,opacity:.9}));
    for(let k=0;k<26;k++){const [x,z]=atA(rnd()*6.28,R+150+rnd()*1600),g=new THREE.Group();g.position.set(x,-60,z);G.add(g);const m=cm2[k%4];const n=3+(rnd()*4|0);
      for(let i=0;i<n;i++){const h=60+rnd()*220,c=put(new THREE.OctahedronGeometry(1,0),m,(rnd()-.5)*60,h*.45,(rnd()-.5)*60,g,false);c.scale.set(h*.16,h*.6,h*.16);c.rotation.set((rnd()-.5)*.6,rnd()*3,(rnd()-.5)*.6);}if(k%3===0)glowSprite(cols[k%4],420,.3,g,0,100,0);}
    const rock=wm('#2a3438',{roughness:.95});for(let k=0;k<30;k++){const [x,z]=atA(rnd()*6.28,R+300+rnd()*2400),h=200+rnd()*700;put(new THREE.ConeGeometry(40+h*.15,h,8),rock,x,-60+h/2,z,G,false);}
    for(let k=0;k<14;k++){const [x,z]=atA(rnd()*6.28,R+150+rnd()*900),s=.6+rnd();put(new THREE.CylinderGeometry(10*s,14*s,80*s,10),wm('#e8f4f0'),x,-60+40*s,z,G,false);put(new THREE.SphereGeometry(50*s,20,10,0,Math.PI*2,0,Math.PI/2),new THREE.MeshStandardMaterial({color:'#3ff0ff',emissive:'#1ad0e0',emissiveIntensity:1.2,roughness:.4}),x,-60+80*s,z,G,false).scale.y=.6;}
    const n=300,pos=new Float32Array(n*3);for(let i=0;i<n;i++){const [x,z]=atA(rnd()*6.28,rnd()*(R+800));pos[i*3]=x;pos[i*3+1]=rnd()*500;pos[i*3+2]=z;}const sg=new THREE.BufferGeometry();sg.setAttribute('position',new THREE.BufferAttribute(pos,3));
    const SP=new THREE.Points(sg,new THREE.PointsMaterial({color:'#9ffff0',size:3,sizeAttenuation:false,transparent:true,opacity:.8,blending:THREE.AdditiveBlending,depthWrite:false}));SP.frustumCulled=false;G.add(SP);animators.push((t,dt)=>{for(let i=0;i<n;i++){pos[i*3+1]+=dt*6;if(pos[i*3+1]>520)pos[i*3+1]=0;}sg.attributes.position.needsUpdate=true;});}}
/* ---------------- FREEZER EXTRAS ---------------- */
function freezerExtras(R,L1){const v=VAR;
  if(v===1){/* inside a giant freezer */
    const pan=texCanvas(512,512,(g,w,h)=>{g.fillStyle='#d6e2ea';g.fillRect(0,0,w,h);for(let x=0;x<w;x+=128){const gr=g.createLinearGradient(x,0,x+128,0);gr.addColorStop(0,'#b8c8d4');gr.addColorStop(.5,'#eef4f8');gr.addColorStop(1,'#b8c8d4');g.fillStyle=gr;g.fillRect(x+4,0,120,h);}
      for(let i=0;i<300;i++){g.fillStyle='rgba(255,255,255,'+(.2+rnd()*.5)+')';g.beginPath();g.arc(rnd()*w,rnd()*h,1+rnd()*4,0,7);g.fill();}});
    const {g:S,Rw,fy,H}=roomShell(R,{Rw:R+1800,H:2300,floor:new THREE.MeshStandardMaterial({map:T2(pan,30,30),color:'#eef6fb',roughness:.35,metalness:.3}),wall:new THREE.MeshStandardMaterial({map:T2(pan,40,4),side:THREE.BackSide,roughness:.4,metalness:.5}),ceil:wm('#e6eef4',{roughness:.5,metalness:.3})});
    for(let i=0;i<6;i++){const a=i/6*6.28,[x,z]=atA(a,R*.6),b=put(new THREE.BoxGeometry(900,30,90),new THREE.MeshBasicMaterial({color:'#f4fbff',toneMapped:false}),x,fy+H-20,z,S,false);b.rotation.y=-a;glowSprite('#e8f6ff',900,.2,S,x,fy+H-120,z);}
    const fT=T2(frozenTex()),side=new THREE.MeshStandardMaterial({map:fT,roughness:.6}),top=wm('#dfeefa',{roughness:.7}),wire=wm('#c8d0d8',{metalness:.9,roughness:.3});
    for(let s=0;s<8;s++){const a=s/8*6.28+.2,[x,z]=atA(a,Rw-260),sh=new THREE.Group();sh.position.set(x,fy,z);sh.lookAt(0,fy,0);S.add(sh);
      for(const y of [300,800,1300]){put(new THREE.BoxGeometry(900,12,380),wire,0,y,0,sh,false);for(let k=0;k<3;k++){const b=new THREE.Mesh(new THREE.BoxGeometry(260,90,300),[side,side,top,top,side,side]);b.position.set(-290+k*290,y+51+(rnd()<.5?92:0),0);sh.add(b);}}
      for(const xx of [-450,450])put(new THREE.BoxGeometry(14,1500,14),wire,xx,750,170,sh,false);}
    const tubC=['#ff9ac0','#9a6a3a','#fff4dc','#7fd0ff'];for(let i=0;i<6;i++){const [x,z]=atA(i/6*6.28+.6,R+500+rnd()*500),s=1+rnd()*.5;put(new THREE.CylinderGeometry(160*s,140*s,260*s,32),wm(tubC[i%4],{roughness:.5}),x,fy+130*s,z,S,false);put(new THREE.CylinderGeometry(166*s,166*s,30*s,32),wm('#ffffff',{roughness:.4}),x,fy+275*s,z,S,false);
      for(let k=0;k<5;k++)put(new THREE.SphereGeometry(30*s,10,8),wm(tubC[(i+1)%4]),x+(rnd()-.5)*160*s,fy+300*s,z+(rnd()-.5)*160*s,S,false);}
    for(let i=0;i<3;i++){const [x,z]=atA(i*2.1+1.3,R+380),tr=new THREE.Group();tr.position.set(x,fy,z);tr.rotation.y=rnd()*3;S.add(tr);put(new THREE.BoxGeometry(500,40,220),new THREE.MeshPhysicalMaterial({color:'#bfe6ff',roughness:.1,transparent:true,opacity:.6}),0,20,0,tr,false);
      for(let a2=0;a2<6;a2++)for(let b2=0;b2<2;b2++)put(new THREE.BoxGeometry(70,60,80),new THREE.MeshPhysicalMaterial({color:'#e8f8ff',roughness:.05,transparent:true,opacity:.75,clearcoat:1}),-200+a2*80,60,-50+b2*100,tr,false);}
    safeBake(S);}
  if(v===2){/* aurora night with an ice castle */
    const auroraT=T2(texCanvas(256,256,(g,w,h)=>{const gr=g.createLinearGradient(0,h,0,0);gr.addColorStop(0,'rgba(80,255,170,0)');gr.addColorStop(.15,'rgba(80,255,170,.9)');gr.addColorStop(.6,'rgba(120,120,255,.5)');gr.addColorStop(1,'rgba(200,90,255,0)');g.fillStyle=gr;g.fillRect(0,0,w,h);}));
    const rib=[];for(let i=0;i<3;i++){const geo=new THREE.PlaneGeometry(10000,1800,80,1),m=new THREE.Mesh(geo,new THREE.MeshBasicMaterial({map:auroraT,transparent:true,opacity:.55,blending:THREE.AdditiveBlending,depthWrite:false,side:THREE.DoubleSide,fog:false,toneMapped:false}));
      const a=i*1.9+.5,[x,z]=atA(a,6500);m.position.set(x,2600+i*300,z);m.lookAt(0,2600,0);m.userData.base=geo.attributes.position.array.slice();m.userData.p=i*2;world.add(m);rib.push(m);}
    animators.push(t=>{rib.forEach(m=>{const p=m.geometry.attributes.position,b=m.userData.base;for(let k=0;k<p.count;k++){const x=b[k*3];p.setZ(k,Math.sin(x*.0009+t*.5+m.userData.p)*500+Math.sin(x*.0023+t*.8)*200);}p.needsUpdate=true;m.material.opacity=.45+.15*Math.sin(t*.6+m.userData.p);});});
    const sgp=[];for(let i=0;i<900;i++){const u=rnd(),vv=rnd()*.85+.12,th=u*6.28,ph=Math.acos(1-vv);sgp.push(Math.cos(th)*Math.sin(ph)*8500,Math.cos(ph)*8500,Math.sin(th)*Math.sin(ph)*8500);}const sg=new THREE.BufferGeometry();sg.setAttribute('position',new THREE.Float32BufferAttribute(sgp,3));const stars=new THREE.Points(sg,new THREE.PointsMaterial({color:'#ffffff',size:2,sizeAttenuation:false,fog:false}));stars.frustumCulled=false;world.add(stars);
    const G=VG(),ice=new THREE.MeshPhysicalMaterial({color:'#bfe6ff',roughness:.08,metalness:.05,transparent:true,opacity:.82,clearcoat:1,emissive:'#3a7ac8',emissiveIntensity:.25});const [cx,cz]=atA(2.4,R+1700),c=new THREE.Group();c.position.set(cx,-60,cz);c.lookAt(0,-60,0);G.add(c);
    put(new THREE.BoxGeometry(900,300,500),ice,0,150,0,c,false);for(const [x,z,h] of [[-450,-250,700],[450,-250,700],[-450,250,560],[450,250,560],[0,0,1000]]){put(new THREE.CylinderGeometry(90,110,h,16),ice,x,h/2,z,c,false);put(new THREE.ConeGeometry(120,260,16),ice,x,h+130,z,c,false);}glowSprite('#7fb8ff',1400,.3,c,0,400,0);
    for(let i=0;i<5;i++){const [x,z]=atA(i*1.1+3.6,R+500+rnd()*500),s=.8+rnd()*.6;put(new THREE.SphereGeometry(140*s,24,12,0,Math.PI*2,0,Math.PI/2),wm('#f4fbff',{roughness:.7}),x,-60,z,G,false);const d=put(new THREE.CylinderGeometry(60*s,60*s,110*s,16,1,false,0,Math.PI),wm('#e8f2fa'),x+Math.cos(i)*120*s,-60+55*s,z+Math.sin(i)*120*s,G,false);d.rotation.z=Math.PI/2;glowSprite('#ffb060',200*s,.5,G,x+Math.cos(i)*140*s,-30,z+Math.sin(i)*140*s);}
    safeBake(G);}
  if(v===3){/* sunrise ski resort: gondola lift and chalets */
    const G=VG(),[ax,az]=atA(.9,R+700),[bx,bz]=atA(.4,R+3600),A=new THREE.Vector3(ax,40,az),B=new THREE.Vector3(bx,1500,bz),st=wm('#4a4f58',{metalness:.6});
    for(const P of [A,B]){const t=new THREE.Group();t.position.set(P.x,-60,P.z);G.add(t);put(new THREE.BoxGeometry(120,P.y+160,120),wm('#7a5a3a'),0,(P.y+160)/2,0,t,false);put(new THREE.BoxGeometry(260,80,180),wm('#c8261b'),0,P.y+200,0,t,false);}
    for(let k=1;k<6;k++){const P=A.clone().lerp(B,k/6);put(new THREE.CylinderGeometry(14,18,P.y+120,8),st,P.x,(P.y+120)/2-60,P.z,G,false);}
    for(const off of [-30,30]){const d=B.clone().sub(A),L=d.length(),c=put(new THREE.CylinderGeometry(2.5,2.5,L,4),wm('#222222'),0,0,0,G,false);c.position.copy(A).add(B).multiplyScalar(.5);c.position.y+=40;c.position.x+=off;c.quaternion.setFromUnitVectors(new THREE.Vector3(0,1,0),d.normalize());}
    const gond=[];for(let i=0;i<10;i++){const g=new THREE.Group();G.add(g);put(new THREE.BoxGeometry(70,70,60),wm(['#e0452c','#f7c948','#2f7fd8'][i%3],{roughness:.4}),0,-70,0,g,false);put(new THREE.CylinderGeometry(2,2,60,4),st,0,-20,0,g,false);g.userData.k=i/10;gond.push(g);}
    animators.push(t=>{gond.forEach(g=>{const k=(g.userData.k+t*.02)%1,up=k<.5,f=up?k*2:2-k*2,P=A.clone().lerp(B,f);g.position.set(P.x+(up?-30:30),P.y+40,P.z);});});
    const smk=[];for(let i=0;i<6;i++){const [x,z]=atA(1.3+i*.12,R+600+(i%2)*260),c=new THREE.Group();c.position.set(x,-60,z);c.lookAt(0,-60,0);G.add(c);put(new THREE.BoxGeometry(260,200,220),wm('#8a5a30',{roughness:.8}),0,100,0,c,false);
      const rf=put(new THREE.CylinderGeometry(10,180,140,4,1),wm('#f4fbff',{roughness:.7}),0,270,0,c,false);rf.rotation.y=Math.PI/4;rf.scale.set(1.15,1,.9);
      for(const sd of [-1,1])put(new THREE.PlaneGeometry(50,60),new THREE.MeshBasicMaterial({color:'#ffd27a',toneMapped:false}),sd*60,110,111,c,false);put(new THREE.BoxGeometry(40,120,40),wm('#5a5a5a'),70,320,0,c,false);
      const s=new THREE.Sprite(new THREE.SpriteMaterial({map:cloudTex(),color:'#e8e8ee',transparent:true,opacity:.5,depthWrite:false}));s.userData.p=rnd();c.add(s);smk.push(s);}
    animators.push(t=>{smk.forEach(s=>{const k=(t*.12+s.userData.p)%1;s.position.set(70+k*40,390+k*260,0);s.scale.set(80+k*220,60+k*160,1);s.material.opacity=.5*(1-k);});});}}

function varLook(def){const L=VARLOOK[def.id];if(!L)return;if(L.fog){scene.fog=new THREE.Fog(L.fog[0],L.fog[1],L.fog[2]);scene.background=new THREE.Color(L.bg||L.fog[0]);}else if(L.bg)scene.background=new THREE.Color(L.bg);
  if(L.hemi){hemi.color.set(L.hemi[0]);hemi.groundColor.set(L.hemi[1]);hemi.intensity=L.hemi[2];}if(L.sun){sun.color.set(L.sun[0]);sun.intensity=L.sun[1];}if(L.dir)sunDir.set(L.dir[0],L.dir[1],L.dir[2]).normalize();if(L.exposure)renderer.toneMappingExposure=L.exposure;}

/* per-map light balance on top of each theme: bright daytime maps had so much sky fill that everything went flat and pale */
let GROUND_DIM=1;
const LOOKBAL={kitchen:{fill:.8,exp:.95,con:.03,sat:.05},bay:{fill:.82,exp:.96,con:.03,sat:.06},freezer:{fill:.76,exp:.92,con:.04,sat:.08},night:{fill:1,exp:1,con:.02,sat:.03,ground:.8},
  lagoon:{fill:.82,exp:.95},calzone:{fill:.84,exp:.96},tour:{fill:.84,exp:.96},burn:{fill:.8,exp:.96},peak:{fill:.86,exp:.97},oven:{fill:.9,exp:1,ground:.85},moon:{ground:.6},mozz:{ground:.68},napoli:{ground:.7},glacier:{ground:.72},basil:{fill:.86,exp:.98},spiral:{fill:.86,exp:.97}};
function balanceLook(def){const T0=LOOKBAL[def.theme]||{},M0=LOOKBAL[def.id]||{};const fill=M0.fill??T0.fill??1,exp=M0.exp??T0.exp??1;
  hemi.intensity*=fill;renderer.toneMappingExposure*=exp;GROUND_DIM=M0.ground??T0.ground??1;const G=POST.grade;G.con=(G.con||1)+(T0.con||0);G.sat=(G.sat||1)+(T0.sat||0);}
function varSky(def){const L=VARLOOK[def.id];if(!L||!(L.pano||L.sky))return;if(sky)world.remove(sky);sky=L.pano?panoSky(L.pano,L.tint,L.rot):skyDome(L.sky,sunDir,L.sun?L.sun[0]:'#ffffff');world.add(sky);}

/* ================= MOVING HAZARDS: slow traffic, a level-crossing train, wandering critters, pools and drive-through city blocks ================= */
const HZSET={margherita:['walk','pool'],basil:['walk','pool'],oven:['walk','pool'],spiral:['traffic','walk'],
  bay:['traffic','city'],lagoon:['pool','walk'],calzone:['train','walk'],tour:['traffic','train'],
  peaks:['traffic','city'],mozz:['walk','pool'],napoli:['traffic','city'],moon:['walk','pool'],
  frosty:['walk','pool'],burn:['traffic','pool'],glacier:['pool','train'],peak:['train','walk']};
let HAZ={traffic:[],train:null,walk:[],pool:[],city:[]};
const segL=()=>T.L/N;
function trackAt(s,lat){const n=N,i=Math.floor(((s%n)+n)%n),f=s-Math.floor(s),p=track[i],q=track[(i+1)%n];const x=p.x+(q.x-p.x)*f,y=p.y+(q.y-p.y)*f,nx=p.nx+(q.nx-p.nx)*f,ny=p.ny+(q.ny-p.ny)*f;
  return {x:x+nx*lat,y:y+ny*lat,ang:lerpA(p.ang,q.ang,f),i};}
const segBad=j=>{j=((j%N)+N)%N;const p=track[j];if(p.open)return true;if(loopNear(j,26))return true;if(GLIDE&&j>GLIDE.rj-8&&j<GLIDE.j1+8)return true;return false;};
function hzMat(c,o){return new THREE.MeshStandardMaterial(Object.assign({color:c,roughness:.5},o||{}));}
/* --- traffic: real car bodies cruising the track well below race pace --- */
function mkTraffic(car,col){const M={paint:new THREE.MeshStandardMaterial({color:col}),dark:hzMat('#222'),stripe:hzMat('#eee'),tailM:new THREE.MeshStandardMaterial({color:'#ff2a1a',emissive:'#ff1a0a',emissiveIntensity:1})};
  const g=new THREE.Group(),B=new THREE.Group();g.add(B);HQB=false;carBody(car,M,B);const cg=carGeos(car),hw=CAR_PACKS[car].h.wheels,wh=[];
  hw.forEach((w,i)=>{const sp=new THREE.Group();sp.position.set(w.c[0],w.c[1],w.c[2]);const m=new THREE.Mesh(cg['w'+i],SH.carVC);sp.add(m);g.add(sp);wh.push({sp,r:w.r});});
  B.traverse(o=>{if(o.isMesh){o.castShadow=o.material!==SH.carGlass;}});g.scale.setScalar(KS*1.05);g.rotation.order='YZX';g.userData.noLift=true;world.add(g);return {g,wh,len:Math.max(...hw.map(w=>Math.abs(w.c[0])))*KS*1.05+4};}
function buildTraffic(def){const cars=def.theme==='kitchen'?['hatch','gt','muscle']:def.theme==='freezer'?['suv','hatch','tourer']:['suv','hatch','coupe','muscle','tourer'];
  const cols=['#e8e4da','#2a5bff','#c8261b','#1a1b22','#f7c948','#3f9a35','#9aa4b8'],n=3;
  for(let i=0;i<n;i++){const car=cars[i%cars.length],m=mkTraffic(car,cols[(i*3+def.R)%cols.length]);const s0=N*(.22+i*.27);
    HAZ.traffic.push({m,s:s0,s0,lat:[-32,30,0][i%3],latT:[-32,30,0][i%3],laneT:3+i*2,v:BASE_MAX*.38,x:0,y:0,ang:0,hide:false});}}
/* --- train: crosses the road just past a jump ramp, so the jump carries you over it --- */
function buildTrain(def){let best=null;for(const r of ramps){if(r.glide)continue;for(const off of [15,14,16,13]){const jc=(r.j+off)%N;if(segBad(jc))continue;const p=track[jc];
    const ux=p.nx,uy=p.ny,span=RW+300;let ok=true;for(const sd of [-1,1]){const ex=p.x+ux*span*sd,ey=p.y+uy*span*sd;if(Math.hypot(ex,ey)>def.R-80){ok=false;break;}
      for(let t=RW+60;t<=span;t+=30){const x=p.x+ux*t*sd,y=p.y+uy*t*sd;if(nearTrack(x,y,CURB+30)){ok=false;break;}}if(!ok)break;}
    if(ok){best={j:jc,p,ux,uy,span,rj:r.j};r.train=true;break;}}if(best)break;}
  if(!best)return;const {p,ux,uy,span}=best,G=new THREE.Group();G.userData.noLift=true;world.add(G);
  /* rails and sleepers */
  const rail=hzMat('#8a8f99',{metalness:.8,roughness:.3}),wood=hzMat('#5a3a22',{roughness:.85}),ang=Math.atan2(uy,ux);
  for(let t=-span;t<=span;t+=7){const x=p.x+ux*t,y=p.y+uy*t,gy=groundAt(x,y);const sl=put(new THREE.BoxGeometry(3,1,22),wood,x,gy+.5,y,G,false);sl.rotation.y=-ang;}
  for(const o of [-6.5,6.5]){const pts=[];for(let t=-span;t<=span;t+=10){const x=p.x+ux*t-uy*o,y=p.y+uy*t+ux*o;pts.push(new THREE.Vector3(x,groundAt(x,y)+1.4,y));}
    put(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts),Math.ceil(span/5),.7,6,false),rail,0,0,0,G,false);}
  /* tunnel portals at both ends */
  const stone=hzMat('#7a6a5a',{roughness:.9}),dark=new THREE.MeshBasicMaterial({color:'#050403'});
  for(const sd of [-1,1]){const x=p.x+ux*span*sd,y=p.y+uy*span*sd,g=new THREE.Group();g.position.set(x,groundAt(x,y),y);g.rotation.y=-ang+(sd>0?Math.PI:0);G.add(g);
    put(new THREE.BoxGeometry(14,46,46),stone,0,23,0,g);put(new THREE.BoxGeometry(2,32,26),dark,-7.2,16,0,g,false);put(new THREE.BoxGeometry(70,70,90),new THREE.MeshStandardMaterial({color:def.theme==='freezer'?'#e8f2fa':def.theme==='bay'?'#5a8a4a':'#6b4a32',roughness:.95}),28,22,0,g);}
  /* crossing signals */
  const lamps=[];for(const sd of [-1,1]){const q=track[(best.j-sd*3+N)%N],o=(CURB+8)*sd,x=q.x+q.nx*o,y=q.y+q.ny*o,g=new THREE.Group();g.position.set(x,groundAt(x,y),y);G.add(g);
    put(new THREE.CylinderGeometry(.8,.9,26,8),hzMat('#e8e8ee'),0,13,0,g);const xb=put(new THREE.BoxGeometry(1,2.4,16),hzMat('#ffffff'),0,24,0,g);xb.rotation.set(0,-q.ang,.7);const xb2=put(new THREE.BoxGeometry(1,2.4,16),hzMat('#ffffff'),0,24,0,g);xb2.rotation.set(0,-q.ang,-.7);
    for(const lo of [-2.4,2.4]){const l=new THREE.Mesh(new THREE.SphereGeometry(1.3,12,8),new THREE.MeshBasicMaterial({color:'#401010',toneMapped:false}));l.position.set(-Math.sin(-q.ang)*lo,19,-Math.cos(-q.ang)*lo);g.add(l);lamps.push(l);}}
  /* the train: a loco and three wagons painted in pizza colours */
  const T0=new THREE.Group();T0.userData.noLift=true;world.add(T0);const TS=.78;const body=hzMat('#c8261b',{metalness:.3,roughness:.4}),cream=hzMat('#fff4dc'),blk=hzMat('#1a1a1a',{metalness:.5}),gold=hzMat('#d9a84a',{metalness:.8,roughness:.3});
  const cars=[];for(let c=0;c<4;c++){const g=new THREE.Group();T0.add(g);const L=c===0?34:28;
    if(c===0){put(new THREE.CylinderGeometry(7,7,22,20),body,-2,12,0,g).rotation.z=Math.PI/2;put(new THREE.BoxGeometry(12,18,14),body,11,13,0,g);put(new THREE.BoxGeometry(13,2,16),blk,11,22.5,0,g);put(new THREE.CylinderGeometry(2.2,3,8,12),blk,-8,22,0,g);put(new THREE.ConeGeometry(6,6,14),gold,-15,12,0,g).rotation.z=Math.PI/2;
      const hl=new THREE.Mesh(new THREE.SphereGeometry(2,10,8),new THREE.MeshBasicMaterial({color:'#fff2b0',toneMapped:false}));hl.position.set(-17,12,0);g.add(hl);}
    else{put(new THREE.BoxGeometry(L-3,14,15),c%2?cream:body,0,12,0,g);put(new THREE.BoxGeometry(L-1,2,17),blk,0,19.5,0,g);const crust=put(new THREE.CylinderGeometry(6.5,6.5,L-6,18,1,false,0,Math.PI),hzMat('#e2b06a',{roughness:.7}),0,19.5,0,g);crust.rotation.z=Math.PI/2;}
    for(const wx of [-L/2+6,L/2-6])for(const wz of [-6,6]){const w=put(new THREE.CylinderGeometry(3.2,3.2,1.6,14),blk,wx,3.6,wz,g);w.rotation.x=Math.PI/2;}
    put(new THREE.BoxGeometry(L-2,3,13),blk,0,5,0,g);g.scale.setScalar(TS);cars.push({g,L:L*TS});}
  let tot=0;cars.forEach(c=>{c.off=tot+c.L/2;tot+=c.L+1.6;});
  HAZ.train={p,ux,uy,span,cars,len:tot,t:0,dir:1,state:'wait',wait:3+Math.random()*3,pos:-span-tot,lamps,j:best.j,v:120,gap:0,bell:0};}
/* --- walkers: little themed critters that wander across the road; touching one spins you out --- */
function mkWalker(theme,i){const g=new THREE.Group();g.userData.noLift=true;world.add(g);const eyeW=new THREE.MeshStandardMaterial({color:'#ffffff',roughness:.2}),eyeB=new THREE.MeshStandardMaterial({color:'#111111',roughness:.2});const legs=[];let H=12;
  const eyes=(y,z,r,sp)=>{for(const s of [-1,1]){put(new THREE.SphereGeometry(r,12,10),eyeW,z,y,s*sp,g,false);put(new THREE.SphereGeometry(r*.5,8,6),eyeB,z+r*.7,y,s*sp,g,false);}};
  if(theme==='kitchen'){const m=hzMat('#7a4528',{roughness:.8});put(new THREE.DodecahedronGeometry(7,1),m,0,10,0,g);eyes(12,5,2,2.6);put(new THREE.BoxGeometry(1,1,5),hzMat('#2a1408'),6.8,15,0,g).rotation.x=.3;
    for(const s of [-1,1]){const l=new THREE.Group();l.position.set(0,4,s*3.5);g.add(l);put(new THREE.CylinderGeometry(1.2,1.2,6,8),hzMat('#5a3018'),0,-3,0,l);put(new THREE.SphereGeometry(1.8,8,6),hzMat('#5a3018'),1,-6,0,l);legs.push(l);}
    put(new THREE.SphereGeometry(1.4,8,6),hzMat('#3f8a35'),0,17,0,g);}
  else if(theme==='bay'){const m=hzMat('#e0452c',{roughness:.45});const b=put(new THREE.SphereGeometry(7,20,12),m,0,6,0,g);b.scale.set(.8,.5,1.2);eyes(11,2,1.6,2.2);
    for(const s of [-1,1]){const c=new THREE.Group();c.position.set(6,6,s*7);g.add(c);put(new THREE.SphereGeometry(3,12,8),m,2,0,0,c).scale.set(1.4,.8,.8);legs.push(c);
      for(let k=0;k<3;k++){const l=new THREE.Group();l.position.set(-3+k*3,4,s*6);g.add(l);put(new THREE.CylinderGeometry(.6,.4,6,6),m,0,-2,s*1.5,l).rotation.x=s*.6;legs.push(l);}}H=10;}
  else if(theme==='night'){const m=hzMat('#5aff8a',{roughness:.35,emissive:'#1a7a3a',emissiveIntensity:.5});put(new THREE.SphereGeometry(6,18,14),m,0,13,0,g).scale.y=1.25;put(new THREE.CylinderGeometry(3,4,8,12),m,0,5,0,g);
    put(new THREE.SphereGeometry(3.2,12,10),eyeW,5,15,0,g,false);put(new THREE.SphereGeometry(1.6,8,6),eyeB,7.4,15,0,g,false);
    for(const s of [-1,1]){put(new THREE.CylinderGeometry(.4,.4,6,6),m,0,22,s*2,g).rotation.x=s*.4;put(new THREE.SphereGeometry(1.1,8,6),new THREE.MeshBasicMaterial({color:'#ffef5a',toneMapped:false}),0,25,s*3.2,g,false);
      const l=new THREE.Group();l.position.set(0,2,s*2.5);g.add(l);put(new THREE.CylinderGeometry(1,1,4,8),m,0,-1,0,l);legs.push(l);}H=16;}
  else{const sn=hzMat('#f6fbff',{roughness:.6});put(new THREE.SphereGeometry(7,18,14),sn,0,7,0,g);put(new THREE.SphereGeometry(5,18,14),sn,0,16,0,g);put(new THREE.SphereGeometry(3.6,16,12),sn,0,23,0,g);
    eyes(24,3,.9,1.3);put(new THREE.ConeGeometry(.9,4,8),hzMat('#ff8a1f'),4.5,23,0,g).rotation.z=-Math.PI/2;put(new THREE.CylinderGeometry(3.4,3.4,1,16),hzMat('#c8261b'),0,26,0,g);put(new THREE.CylinderGeometry(2.4,2.6,4,16),hzMat('#c8261b'),0,28,0,g);
    for(const s of [-1,1]){const a=new THREE.Group();a.position.set(0,17,s*4.5);g.add(a);put(new THREE.CylinderGeometry(.4,.3,8,5),hzMat('#5a3a22'),0,0,s*3,a).rotation.x=s*1.1;legs.push(a);}H=20;}
  g.traverse(o=>{if(o.isMesh)o.castShadow=true;});return {g,legs,H};}
function buildWalkers(def,ctx){const n=5;for(let i=0;i<n;i++){const j0=Math.floor((i+.5)*N/n+(rnd()-.5)*N*.06)%N;let j=j0;for(let t=0;t<40&&(Math.min(j,N-j)<50||segBad(j)||ramps.some(r=>Math.min(Math.abs(r.j-j),N-Math.abs(r.j-j))<12));t++)j=(j+3)%N;
    const w=mkWalker(def.theme,i);HAZ.walk.push({...w,j,lat:(rnd()-.5)*RW*1.6,latT:0,along:0,v:14+rnd()*10,ph:rnd()*6,pause:rnd()*2,x:0,y:0,face:0,hitT:0});}}
/* --- pools: sunken liquid patches that eat one side of the road; fall in and you are fished out a moment later --- */
const POOLLOOK={kitchen:['#4a3a04','#140c00','olive oil'],bay:['#04405e','#011522','water'],night:['#0a2480','#02061a','water'],freezer:['#0e4a70','#021422','icy water']};
const POOLBY={basil:['#3a0410','#0e0104','wine'],oven:['#e03a06','#3a0802','lava'],moon:['#22a018','#021a06','acid'],mozz:['#5a1aa0','#10041e','goo']};
function buildPools(def,ctx){const {pick,farFrom,used}=ctx,look=POOLBY[def.id]||POOLLOOK[def.theme],n=3;
  for(let i=0;i<n;i++){const b=pick(Math.floor((i+.62)*N/n),j=>!segBad(j)&&farFrom(j,22)&&!SHORTS.some(sc=>[sc.a,sc.b].some(e=>Math.min(Math.abs(e-j),N-Math.abs(e-j))<10)));if(b==null)continue;used.push(b);
    const p=track[b],sd=(p.bend>0?1:p.bend<0?-1:(i%2?1:-1))*(i===1?-1:1),lat=sd*36,rx=34,rz=24,x=p.x+p.nx*lat,y=p.y+p.ny*lat,gy=Math.max(groundAt(x,y),surfH(x,y,b));
    const g=new THREE.Group();g.position.set(x,gy,y);g.rotation.y=-p.ang;g.userData.noLift=true;world.add(g);
    const lava=look[2]==='lava'||look[2]==='acid'||look[2]==='goo';
    const surf=new THREE.MeshStandardMaterial({color:look[0],roughness:.32,metalness:0,envMapIntensity:.25,emissive:lava?look[0]:'#000000',emissiveIntensity:lava?.9:0,polygonOffset:true,polygonOffsetFactor:-4});
    const disc=put(new THREE.CircleGeometry(1,48),surf,0,.35,0,g,false);disc.rotation.x=-Math.PI/2;disc.scale.set(rx,rz,1);
    const edge=put(new THREE.RingGeometry(.9,1.04,48),new THREE.MeshBasicMaterial({color:'#120804',polygonOffset:true,polygonOffsetFactor:-5}),0,.38,0,g,false);edge.rotation.x=-Math.PI/2;edge.scale.set(rx,rz,1);
    const deep=put(new THREE.CircleGeometry(1,40),new THREE.MeshBasicMaterial({color:look[1],transparent:true,opacity:.55,depthWrite:false,polygonOffset:true,polygonOffsetFactor:-5}),0,.4,0,g,false);deep.rotation.x=-Math.PI/2;deep.scale.set(rx*.6,rz*.6,1);
    const rim=put(new THREE.TorusGeometry(1,.07,6,48),hzMat(def.theme==='freezer'?'#e8f6ff':'#c98b4e',{roughness:.7}),0,.5,0,g,false);rim.rotation.x=Math.PI/2;rim.scale.set(rx,rz,14);
    if(def.theme==='freezer')for(let k=0;k<10;k++){const a=k/10*Math.PI*2,c=put(new THREE.OctahedronGeometry(2.5+rnd()*2,0),hzMat('#dff4ff',{roughness:.05,metalness:.1}),Math.cos(a)*rx,1.5,Math.sin(a)*rz,g);c.rotation.set(rnd(),rnd(),rnd());}
    if(lava){const gl=new THREE.Sprite(new THREE.SpriteMaterial({map:T2(TX.glow),color:look[0],transparent:true,opacity:.35,depthWrite:false,blending:THREE.AdditiveBlending}));gl.scale.set(rx*2.2,14,1);gl.position.y=5;gl.material.opacity=.18;g.add(gl);}
    const bub=[];for(let k=0;k<6;k++){const m=put(new THREE.SphereGeometry(1.2,8,6),new THREE.MeshStandardMaterial({color:look[0],roughness:.1,transparent:true,opacity:.8}),0,.6,0,g,false);m.userData.p=rnd()*3;m.userData.a=rnd()*6.28;m.userData.r=rnd()*.7;bub.push(m);}
    animators.push(t=>{surf.emissiveIntensity=lava?.8+Math.sin(t*2+i)*.2:0;bub.forEach(m=>{const k=((t*.6+m.userData.p)%1);m.position.set(Math.cos(m.userData.a)*rx*m.userData.r,.6+k*1.5,Math.sin(m.userData.a)*rz*m.userData.r);m.scale.setScalar(k<.85?.4+k:(1-k)*8);});});
    HAZ.pool.push({j:b,x,y,lat,ang:p.ang,tx:p.tx,ty:p.ty,nx:p.nx,ny:p.ny,rx,rz,name:look[2]});
    obstacles.push({x,y,r:24,h:0,j:b,lat,poolR:rx,ghost:true});}}
/* --- drive-through city blocks: little buildings on both kerbs joined by a bridge over the road --- */
function buildCity(def,ctx){const {pick,farFrom,used,straight}=ctx,night=def.theme==='night';
  const wT=T2(windowTex(),1,2),bm=(c)=>new THREE.MeshStandardMaterial({color:c,emissive:'#ffffff',emissiveMap:wT,emissiveIntensity:night?1.1:.25,roughness:.6});
  const cols=night?['#2a2440','#1d2a44','#3a1d2a']:['#e8c8a0','#c8d8e8','#e0a080','#d8e0c0'];
  for(let i=0;i<3;i++){const b=pick(Math.floor((i+.4)*N/3),j=>!segBad(j)&&straight(j,8,.25)&&farFrom(j,20));if(b==null)continue;used.push(b);const p=track[b],G=new THREE.Group();G.position.set(p.x,groundAt(p.x,p.y),p.y);G.rotation.y=-p.ang;G.userData.noLift=true;world.add(G);
    const H=60+rnd()*30,len=70;HAZ.city.push(b);
    for(const sd of [-1,1]){const z=sd*(WALLD+24);for(let k=0;k<3;k++){const h=H*(.7+rnd()*.6),w=len/3-2,bx=-len/2+w/2+k*(w+2);
        put(new THREE.BoxGeometry(w,h,34),bm(cols[(i+k)%cols.length]),bx,h/2,z,G);put(new THREE.BoxGeometry(w+2,2,36),hzMat('#3a3a44'),bx,h+1,z,G);
        if(k===1){const aw=put(new THREE.BoxGeometry(w-4,1,10),hzMat(['#e0452c','#2f7fd8','#3f9a35'][i%3]),bx,14,z-sd*20,G);aw.rotation.x=sd*.3;}}}
    /* bridge with a glowing sign over the road */
    put(new THREE.BoxGeometry(len*.6,12,2*(WALLD+24)),bm(cols[i%cols.length]),0,H*.75,0,G);
    const sc=signTex([['PIZZA ST','DOUGH AVE','CHEESE BLVD'][i],['DRIVE THRU','NO PARKING','ONE WAY'][i]],'#1a1030','#ffe36b',night?'#ff4fa8':'#2fd0ff');
    for(const sd of [-1,1]){const sg=put(new THREE.PlaneGeometry(40,12),new THREE.MeshBasicMaterial({map:sc,toneMapped:false}),sd*(len*.3+.2),H*.75,0,G,false);sg.rotation.y=sd>0?Math.PI/2:-Math.PI/2;}
    const string=[];for(let k=0;k<14;k++){const z=-WALLD+k*(2*WALLD/13);string.push(new THREE.Vector3(len*.32,H*.62-Math.sin(k/13*Math.PI)*6,z));}
    const lg=new THREE.BufferGeometry().setFromPoints(string);G.add(new THREE.Points(lg,new THREE.PointsMaterial({color:'#ffd27a',size:5,sizeAttenuation:false,toneMapped:false})));
    safeBake(G);}}
/* ================= PONDS =================
   A pond sits right beside the road on a straight. Along it the edge barrier is gone, so a wide line or a
   shove sends you over the ledge and into the water; three seconds later you are put back on the road. */
let PONDS=[];
const POND={SX:7.4,SZ:5.4,SY:2.6,WR:9.6,GR:12.4};
function planPonds(def){PONDS=[];for(let j=0;j<N;j++)track[j].pond=0;if(!(HZSET[def.id]||[]).includes('pool'))return;
  const cd=(a,b)=>{const d=Math.abs(a-b)%N;return Math.min(d,N-d);},segL=T.L/N,ax=POND.WR*POND.SX,az=POND.WR*POND.SZ,lat0=CURB+POND.GR*POND.SZ;
  const span=Math.ceil(ax*1.15/segL)+2;
  const ok=(j,sd)=>{if(cd(j,0)<span+60)return false;if(loopNear(j,span+50))return false;if(GLIDE){const g0=GLIDE.rj-10,g1=GLIDE.j1+10;for(let o=-span;o<=span;o+=3){const q=(j+o+N)%N;if(q>=g0&&q<=g1)return false;}}
    for(let o=-span-4;o<=span+4;o+=2){const p=track[(j+o+N)%N];if(Math.abs(p.bend)>.3||p.wall===sd||p.open)return false;}
    if(PONDS.some(q=>cd(q.j,j)<N/4))return false;
    const p=track[j],cx=p.x+p.nx*lat0*sd,cy=p.y+p.ny*lat0*sd;if(Math.hypot(cx,cy)>def.R-az*1.6-60)return false;
    /* nothing else of the track may come near the pond */
    for(let i=0;i<N;i+=2){if(cd(i,j)<span+12)continue;const q=track[i];if(Math.hypot(q.x-cx,q.y-cy)<Math.max(ax,az)*1.25+CURB+20)return false;}
    return true;};
  for(const f of [.36,.7]){let best=null,bs=1e9;
    for(let d=0;d<N*.2&&!best;d+=2){for(const s of [1,-1]){const j=(Math.floor(f*N)+s*d+N)%N;for(const sd of [1,-1]){if(!ok(j,sd))continue;
          const p=track[j],cx=p.x+p.nx*lat0*sd,cy=p.y+p.ny*lat0*sd;let hv=0;for(const [u,v] of [[0,0],[ax,0],[-ax,0],[0,az],[0,-az]])hv+=Math.abs(groundAt(cx+p.tx*u+p.nx*v*sd,cy+p.ty*u+p.ny*v*sd));
          if(hv<bs){bs=hv;best={j,sd};}}}}
    if(!best)continue;const p=track[best.j],sd=best.sd,cx=p.x+p.nx*lat0*sd,cy=p.y+p.ny*lat0*sd;
    PONDS.push({j:best.j,sd,x:cx,y:cy,ang:p.ang,tx:p.tx,ty:p.ty,nx:p.nx*sd,ny:p.ny*sd,ax,az,span});
    FLATS.push({x:cx,y:cy,k:1/(2*120*120)});FLATS.push({x:cx+p.tx*ax*.6,y:cy+p.ty*ax*.6,k:1/(2*90*90)});FLATS.push({x:cx-p.tx*ax*.6,y:cy-p.ty*ax*.6,k:1/(2*90*90)});
    for(let o=-span;o<=span;o++)track[(best.j+o+N)%N].pond=sd;}}
const inPond=(x,y,m)=>{for(const q of PONDS){const dx=x-q.x,dy=y-q.y,u=dx*q.tx+dy*q.ty,v=dx*q.nx+dy*q.ny;if((u/(q.ax+(m||0)))**2+(v/(q.az+(m||0)))**2<1)return q;}return null;};
function buildPonds(def){if(!PONDS.length)return;const G=propGeos('pond'),look=def.id==='oven'?POOLBY.oven:def.theme==='freezer'?['#3f8fb0','#0a2a3a','icy water']:def.theme==='night'?['#1d5f8a','#041a2a','water']:['#2e8c9a','#06303a','water'],hot=look[2]==='lava'||look[2]==='acid'||look[2]==='goo';
  const frz=def.theme==='freezer';
  const baseM=new THREE.MeshStandardMaterial({map:propTex('tex_pond'),roughness:.85,envMapIntensity:.4});
  const grassM=new THREE.MeshStandardMaterial({map:propTex('tex_pondgrass'),color:frz?'#cfe4ee':'#ffffff',roughness:.9,envMapIntensity:.3,side:THREE.DoubleSide,alphaTest:.3});
  const rockM=new THREE.MeshStandardMaterial({vertexColors:true,roughness:.8});
  const waterM=new THREE.MeshStandardMaterial({color:look[0],roughness:hot?.5:.08,metalness:hot?0:.25,envMapIntensity:hot?.2:1.1,emissive:hot?look[0]:'#000000',emissiveIntensity:hot?.85:0});
  const waveM=new THREE.MeshBasicMaterial({color:hot?'#ffd27a':'#e8fbff',transparent:true,opacity:.35,depthWrite:false});
  for(const q of PONDS){const g=new THREE.Group();g.position.set(q.x,groundAt(q.x,q.y),q.y);g.rotation.y=-Math.atan2(q.ty,q.tx)+(q.sd<0?Math.PI:0);g.userData.noLift=true;world.add(g);
    const inner=new THREE.Group();inner.scale.set(POND.SX,POND.SY,POND.SZ);g.add(inner);
    const add=(geo,mat,cast)=>{const m=new THREE.Mesh(geo,mat);m.receiveShadow=true;m.castShadow=!!cast;inner.add(m);return m;};
    add(G.pond_base,baseM);add(G.pond_grass,grassM);add(G.pond_rock,rockM,true);const w=add(G.pond_water,waterM);w.renderOrder=1;const wv=add(G.pond_wave,waveM);wv.renderOrder=2;
    /* the water fills the basin all the way to the rim so it reads as a deep pond from the road */
    w.position.y=.18;
    /* warning posts at both ends of the open stretch */
    const postM=hzMat('#f4efe4',{roughness:.5}),stripeM=hzMat(def.theme==='night'?'#3a6fd8':'#d6301e',{roughness:.5});
    for(const e of [-1,1]){const jj=(q.j+e*q.span+N)%N,p=track[jj],o=(WALLD+1)*q.sd,x=p.x+p.nx*o,y=p.y+p.ny*o,gy=groundAt(x,y);
      put(new THREE.CylinderGeometry(1.6,1.8,10,10),postM,x,gy+5,y,world);put(new THREE.CylinderGeometry(1.7,1.7,2.4,10),stripeM,x,gy+7.4,y,world);}
    let t0=Math.random()*6;animators.push((t)=>{wv.scale.setScalar(1+.06*Math.sin(t*1.3+t0));waveM.opacity=.22+.14*Math.sin(t*1.7+t0);if(hot)waterM.emissiveIntensity=.7+.2*Math.sin(t*2+t0);});}}
function pondFall(k,q){if(k.sink!=null)return;k.sink=3;k.sinkP=q;k.sinkT=0;k.speed*=.3;k.drift=0;k.boost=0;k.charge=0;k.item2=k.item2;
  const look=curMapId()==='oven'?POOLBY.oven:['#7fd8ff'];burst(k.x,(k.wy||0)+2,k.y,36,[look[0],'#ffffff'],80,3.2);spawnRing(k.x,(k.wy||0)+.6,k.y,'#e8fbff',50,.7);
  SFX.bump(near(k));if(k===player)showBanner('Splash!',1.4);if(k===camT)shake(.6);}
function pondRespawn(k){const q=k.sinkP,j=(k.idx-5+N)%N,p=track[j],lat=q?-q.sd*18:0;let di=j-k.idx;if(di>N/2)di-=N;if(di<-N/2)di+=N;k.prog+=di;k.idx=j;
  k.x=k.px=p.x+p.nx*lat;k.y=k.py=p.y+p.ny*lat;k.a=k.ma=k.pa=k.pma=p.ang;k.speed=BASE_MAX*.3;k.wy=k.pwy=k.lastG=groundAt(k.x,k.y);k.wvy=0;k.air=false;k.spin=0;k.inv=1.8;k.z=k.pz=0;k.sink=null;k.sinkP=null;k.sc=null;
  if(k===camT)camSnap=true;spawnRing(k.x,k.wy+.6,k.y,'#7fe8ff',40,.6);}
function pondTick(dt){for(const k of karts){if(k.sink!=null){k.sink-=dt;k.sinkT+=dt;k.speed*=Math.pow(.02,dt);if(k.sink<=0)pondRespawn(k);continue;}
    if(!PONDS.length||k.air||k.loop||k.glide||k.z>3)continue;const q=inPond(k.x,k.y,-5);if(q)pondFall(k,q);}}

function buildHazards(def,R,ctx){HAZ={traffic:[],train:null,walk:[],pool:[],city:[]};const set=HZSET[def.id]||[];
  for(const k of set){try{({traffic:buildTraffic,train:buildTrain,walk:buildWalkers,pool:buildPonds,city:buildCity})[k](def,ctx);}catch(e){console.warn('hazard',k,e);}}}
function resetHazards(){for(const c of HAZ.traffic){c.s=c.s0;c.lat=c.latT;}if(HAZ.train){HAZ.train.state='wait';HAZ.train.wait=2+Math.random()*2;HAZ.train.pos=-HAZ.train.span-HAZ.train.len;}}
function hzBump(k,x,y,r,kind){const dx=k.x-x,dy=k.y-y,d=Math.hypot(dx,dy)||1;if(d>=r)return false;const ov=r-d;k.x+=dx/d*ov;k.y+=dy/d*ov;
  if(kind){spinOut(k,kind,1);return true;}if(k.inv>0)return true;k.speed*=.55;k.inv=.35;if(k===camT)shake(.6);SFX.bump(near(k));burst(k.x,6,k.y,10,['#fff4dc','#ffe066'],40,2.2);return true;}
function poolFall(k,pl){if(k.inv>0&&k.sink==null)return;k.sink=.7;k.sinkP=pl;k.speed*=.25;k.drift=0;k.boost=0;k.charge=0;burst(k.x,2,k.y,24,[POOLBY[curMapId()]?.[0]||'#7fd8ff','#ffffff'],60,2.6);SFX.bump(near(k));if(k===player)showBanner('Splash!',1.2);if(k===camT)shake(.5);}
const curMapId=()=>MAPS[mapIdx]?MAPS[mapIdx].id:'';
function poolRespawn(k){const j=(k.idx-6+N)%N,p=track[j],lat=k.sinkP?-Math.sign(k.sinkP.lat)*20:0;let di=j-k.idx;if(di>N/2)di-=N;if(di<-N/2)di+=N;k.prog+=di;k.idx=j;
  k.x=k.px=p.x+p.nx*lat;k.y=k.py=p.y+p.ny*lat;k.a=k.ma=k.pa=k.pma=p.ang;k.speed=BASE_MAX*.35;k.wy=k.pwy=k.lastG=groundAt(k.x,k.y);k.wvy=0;k.air=false;k.spin=0;k.inv=1.6;k.z=k.pz=0;k.sink=null;k.sc=null;
  if(k===camT){camSnap=true;}spawnRing(k.x,k.wy+.6,k.y,'#7fe8ff',40,.6);}
function updateHazards(dt){if(state==='menu'&&!HAZ.traffic.length&&!HAZ.train&&!HAZ.walk.length)return;const racing=state==='race'||state==='menu';
  /* traffic */
  for(const c of HAZ.traffic){if(racing)c.s+=c.v*dt/segL();c.laneT-=dt;if(c.laneT<=0){c.laneT=4+Math.random()*5;c.latT=[-34,-12,12,34][Math.floor(Math.random()*4)];}c.lat+=(c.latT-c.lat)*Math.min(1,dt*.6);
    const P=trackAt(c.s,c.lat);c.x=P.x;c.y=P.y;c.ang=P.ang;c.i=P.i;c.hide=segBad(P.i);if(c.hide)continue;const fx=Math.cos(c.ang),fy=Math.sin(c.ang),hl=c.m.len*.55;
    for(const k of karts){if(k.loop||k.z>12||k.sink!=null)continue;for(const o of [-hl,0,hl])if(hzBump(k,c.x+fx*o,c.y+fy*o,15))break;}}
  /* train */
  const tr=HAZ.train;if(tr){if(tr.state==='wait'){tr.wait-=dt;if(tr.wait<=0){tr.state='run';tr.dir=Math.random()<.5?1:-1;tr.pos=-tr.span-tr.len;}}
    else{tr.pos+=tr.v*dt;if(tr.pos>tr.span+10){tr.state='wait';tr.wait=4+Math.random()*5;}}
    if(tr.state==='run')for(const c of tr.cars){const t=(tr.pos+tr.len-c.off)*tr.dir,x=tr.p.x+tr.ux*t,y=tr.p.y+tr.uy*t;c.t=t;
      for(const k of karts){if(k.loop||k.z>14||k.sink!=null)continue;const dx=k.x-x,dy=k.y-y,u=dx*tr.ux+dy*tr.uy,v=dy*tr.ux-dx*tr.uy;if(Math.abs(u)<c.L/2+6&&Math.abs(v)<12){const sg=Math.sign(v)||1;k.x+=-tr.uy*sg*(14-Math.abs(v));k.y+=tr.ux*sg*(14-Math.abs(v));spinOut(k,'wheel',1);}}}}
  /* walkers */
  for(const w of HAZ.walk){if(w.pause>0){w.pause-=dt;}else{if(Math.abs(w.lat-w.latT)<2){w.latT=(Math.random()*2-1)*(RW+8);w.pause=.4+Math.random()*1.8;}else w.lat+=Math.sign(w.latT-w.lat)*w.v*dt;}
    w.along=Math.sin(simTime*.3+w.ph)*3;const P=trackAt(w.j+w.along,w.lat);w.x=P.x;w.y=P.y;w.face=P.ang+(w.pause>0?Math.sin(simTime+w.ph)*.6:Math.sign(w.latT-w.lat)*Math.PI/2);
    for(const k of karts){if(k.loop||k.z>w.H*.8||k.sink!=null)continue;if((k.x-w.x)**2+(k.y-w.y)**2<15*15&&k.inv<=0){spinOut(k,'meat',1);w.pause=1.2;w.hitT=.6;}}}
  pondTick(dt);
  for(const k of karts){if(k.sink!=null)continue;
    if(k.air||k.loop||k.glide||k.z>2)continue;for(const pl of HAZ.pool){const dx=k.x-pl.x,dy=k.y-pl.y,u=dx*pl.tx+dy*pl.ty,v=dx*pl.nx+dy*pl.ny;if((u/(pl.rx-4))**2+(v/(pl.rz-4))**2<1){poolFall(k,pl);break;}}}}
function renderHazards(time,dt){for(const c of HAZ.traffic){const g=c.m.g;g.visible=!c.hide;if(c.hide)continue;g.position.set(c.x,groundAt(c.x,c.y),c.y);g.rotation.set(0,-c.ang,0);for(const w of c.m.wh)w.sp.rotation.z-=c.v*dt/(w.r*KS*1.05);}
  const tr=HAZ.train;if(tr){const on=tr.state==='run'||(tr.state==='wait'&&tr.wait<1.5);tr.lamps.forEach((l,i)=>l.material.color.set(on&&((Math.floor(time*3)+i)%2)?'#ff2a1a':'#401010'));
    if(on&&state==='race'){tr.bell-=dt;if(tr.bell<=0){tr.bell=.55;const d=Math.hypot(camera.position.x-tr.p.x,camera.position.z-tr.p.y);if(d<500)tone(1250,.12,'triangle',.02*(1-d/500),0,0,.2);}}
    for(const c of tr.cars){const vis=tr.state==='run'&&Math.abs(c.t||9e9)<tr.span-6;c.g.visible=vis;if(!vis)continue;const x=tr.p.x+tr.ux*c.t,y=tr.p.y+tr.uy*c.t;c.g.position.set(x,groundAt(x,y)+1.6,y);c.g.rotation.y=-Math.atan2(tr.uy,tr.ux)+(tr.dir>0?Math.PI:0);}}
  for(const w of HAZ.walk){w.g.position.set(w.x,groundAt(w.x,w.y)+Math.abs(Math.sin(time*9+w.ph))*(w.pause>0?.3:1.6),w.y);w.g.rotation.y=-w.face;w.legs.forEach((l,i)=>{l.rotation.z=Math.sin(time*10+i*Math.PI)*(w.pause>0?.15:.7);});
    if(w.hitT>0){w.hitT-=dt;w.g.rotation.z=Math.sin(time*40)*.3;}else w.g.rotation.z=0;}
  for(const k of karts){if(k.sink!=null){k.m.g.position.y-=(1-k.sink/.7)*14;}}}

const trainRamp=k=>ramps.some(r=>r.train&&((k.idx-r.j+N)%N)<8);

function loadMap(mi,rev){
  const def=MAPS[mi],th=THEMES[def.theme];seed=1000+mi*7919;CURID=def.id;VAR=Math.max(0,MAPS.filter(m=>m.theme===def.theme).indexOf(def));TUNNEL=null;curRev=!!rev;
  T=makeTrack(def,curRev);track=T.pts;N=T.N;RIM=def.R-38;buildGrid();
  for(let j=0;j<N;j++){const b=track[j].bend;if(Math.abs(b)>.42){const sd=-Math.sign(b);for(let o=-7;o<=7;o++)track[(j+o+N)%N].wall=sd;}}
  SHORTS=[];makeHills(def);
  if(GLIDE)for(let j=GLIDE.rj-3;j<=GLIDE.j1+3;j++)track[(j+N)%N].open=true;
  disposeWorld();for(const k in PROPT)if(/^(sky_|tex_space|tex_mount|tex_skyline|tex_riverbed)/.test(k))PROPT[k].dispose();world=new THREE.Group();scene.add(world);animators=[];boxes=[];pads=[];FXA.clear();FXN.clear();
  const R=def.R;
  renderer.toneMappingExposure=th.exposure;Object.assign(POST.grade,{kitchen:{sat:.9,con:1.02,tint:[1.01,1,.99],vig:.24,bloom:.32,thr:2.4},bay:{sat:.9,con:1.02,tint:[1.01,1,.99],vig:.2,bloom:.28,thr:2.6},freezer:{sat:.94,con:1.03,tint:[.99,1,1.01],vig:.18,bloom:.25,thr:3.0},night:{sat:.9,con:1.03,tint:[1,1,1],vig:.28,bloom:.42,thr:1.8}}[def.theme]||{});
  scene.fog=new THREE.Fog(th.fog[0],th.fog[1],th.fog[2]);scene.background=new THREE.Color(th.bg);
  hemi.color.set(th.hemi[0]);hemi.groundColor.set(th.hemi[1]);hemi.intensity=th.hemi[2];rimL.color.set(def.theme==='night'?'#8a6bff':def.theme==='kitchen'?'#ffd0a0':'#a8ccff');rimL.intensity=def.theme==='night'?.9:.55;
  sun.color.set(th.sun[0]);sun.intensity=th.sun[1];sunDir.set(th.dir[0],th.dir[1],th.dir[2]).normalize();varLook(def);balanceLook(def);
  if(scene.environment)scene.environment.dispose();
  scene.environment=envFrom(th.env,def.theme==='kitchen'?[[128,40,30,'#ffffff'],[384,40,30,'#ffffff'],[256,140,40,'#ff8a2a']]:def.theme==='freezer'?[[256,50,50,'#ffffff'],[100,120,20,'#dff2ff']]:def.theme==='bay'?[[380,110,40,'#fff2d0']]:[[100,60,10,'#bcd0ff'],[300,130,16,'#ffd27a'],[420,130,16,'#ffd27a']]);
  sky=null;if(th.sky){sky=skyDome(th.sky,sunDir,def.theme==='bay'?'#ffd9a0':def.theme==='freezer'?'#ffffff':'#c8d8ff');world.add(sky);}

  const cheeseT=T2(cheeseTile(),R/110,R/110);
  cheeseT.repeat.set(1,1);world.add(terrainMesh(R,new THREE.MeshStandardMaterial({map:cheeseT,color:new THREE.Color().setScalar(GROUND_DIM),roughness:.62,envMapIntensity:.35})));
  put(new THREE.CylinderGeometry(R+2,R+10,60,200,1,true),new THREE.MeshStandardMaterial({map:T2(TX.crust,60,1),roughness:.75}),0,-30,0,world,false);
  const rim=put(new THREE.TorusGeometry(R-16,17,20,260),new THREE.MeshStandardMaterial({map:T2(TX.crust,90,1),roughness:.7}),0,5,0,world,false);rim.rotation.x=Math.PI/2;
  sauceTile(th.roadDark);// keeps the seeded scenery layout stable
  const SJ0=GLIDE?GLIDE.j1:0,SJ1=GLIDE?GLIDE.j0+N:N;
  buildRoad(def,SJ0,SJ1);
  strip(SJ0,SJ1,CURB,CURB+9,.04,wm('#c98b4e',{map:T2(TX.crust,1,1),roughness:.8}),60);strip(SJ0,SJ1,-CURB-9,-CURB,.04,wm('#c98b4e',{map:T2(TX.crust,1,1),roughness:.8}),60);
  (function(){const pos=[],col=[],cR=new THREE.Color('#e0452c'),cW=new THREE.Color('#fff4dc'),H=KERB_H;
    const tri=(a,b,c,cl)=>{for(const v of [a,b,c]){pos.push(v[0],v[1],v[2]);col.push(cl.r,cl.g,cl.b);}};const quad=(a,b,c,d,cl)=>{tri(a,b,c,cl);tri(a,c,d,cl);};
    for(const s of [-1,1])for(let j=0;j<N;j++){if(GLIDE&&j>=GLIDE.j0&&j<GLIDE.j1)continue;const p=track[j],q=track[(j+1)%N],cl=((j>>1)%2)?cR:cW;
      const at=(pt,o,h)=>{const X=pt.x+pt.nx*o*s,Z=pt.y+pt.ny*o*s;return [X,h+groundAt(X,Z),Z];};
      const pi0=at(p,RW,0),pi1=at(p,RW+.6,H),pm=at(p,RW+6.5,H*.75),po=at(p,CURB,.05),qi0=at(q,RW,0),qi1=at(q,RW+.6,H),qm=at(q,RW+6.5,H*.75),qo=at(q,CURB,.05);
      quad(pi0,qi0,qi1,pi1,cl);quad(pi1,qi1,qm,pm,cl);quad(pm,qm,qo,po,cl);}
    const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(pos,3));g.setAttribute('color',new THREE.Float32BufferAttribute(col,3));g.computeVertexNormals();
    const m=new THREE.Mesh(g,new THREE.MeshStandardMaterial({vertexColors:true,roughness:.45,side:THREE.DoubleSide}));m.receiveShadow=true;m.castShadow=true;m.userData.noLift=true;world.add(m);})();
  const buildBarrier=(function(){const pos=[],col=[],H=4.6,TH=2.6,th=THEMES[def.theme],cA=new THREE.Color(def.theme==='night'?'#3a6fd8':def.theme==='freezer'?'#4aa8e8':'#d6301e'),cB=new THREE.Color('#f4efe4'),cT=new THREE.Color('#c98b4e'),cK=new THREE.Color('#3a2a20');
    const tri=(a,b,c,cl)=>{for(const v of [a,b,c]){pos.push(v[0],v[1],v[2]);col.push(cl.r,cl.g,cl.b);}},quad=(a,b,c,d,cl)=>{tri(a,b,c,cl);tri(a,c,d,cl);};
    for(const s of [-1,1])for(let j=0;j<N;j++){const p=track[j],q=track[(j+1)%N];if(p.open||q.open)continue;if(p.wall===s&&q.wall===s)continue;if(p.pond===s||q.pond===s)continue;if(SHORTS.some(sc=>sc.s===s&&[sc.a,sc.b].some(e=>{const d=Math.abs(j-e)%N;return Math.min(d,N-d)<=3;})))continue;
      const at=(pt,o,h)=>{const X=pt.x+pt.nx*o*s,Z=pt.y+pt.ny*o*s;return [X,h+groundAt(X,Z),Z];},cl=((j>>2)%2)?cA:cB;
      const pi0=at(p,WALLD,-.5),pi1=at(p,WALLD,H),po1=at(p,WALLD+TH,H),po0=at(p,WALLD+TH,-.5),qi0=at(q,WALLD,-.5),qi1=at(q,WALLD,H),qo1=at(q,WALLD+TH,H),qo0=at(q,WALLD+TH,-.5);
      if(s>0){quad(pi0,qi0,qi1,pi1,cl);quad(pi1,qi1,qo1,po1,cT);quad(po1,qo1,qo0,po0,cK);}else{quad(pi0,pi1,qi1,qi0,cl);quad(pi1,po1,qo1,qi1,cT);quad(po1,po0,qo0,qo1,cK);}}
    const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(pos,3));g.setAttribute('color',new THREE.Float32BufferAttribute(col,3));g.computeVertexNormals();
    const m=new THREE.Mesh(g,new THREE.MeshStandardMaterial({vertexColors:true,roughness:.5,side:THREE.DoubleSide}));m.castShadow=true;m.receiveShadow=true;m.userData.noLift=true;world.add(m);});
  strip(N-1,N+1,-RW,RW,.09,new THREE.MeshStandardMaterial({map:T2(checkerTex()),roughness:.5}),16);
  (function(){const s=track[0],ang=s.ang,bm=new THREE.MeshStandardMaterial({map:T2(TX.crust,1,6),roughness:.65});const g=new THREE.Group();world.add(g);
    for(const side of [-1,1]){const x=s.x+s.nx*(CURB+10)*side,y=s.y+s.ny*(CURB+10)*side;put(new THREE.CylinderGeometry(3.4,4,40,20),bm,x,20,y,g);put(new THREE.SphereGeometry(3.7,18,12),bm,x,40,y,g);put(new THREE.CylinderGeometry(6,6,2,20),wm('#7d1d0e'),x,1,y,g);}
    const bt=T2(bannerC),bmF=new THREE.MeshStandardMaterial({map:bt,roughness:.55}),dk=wm('#1b0f0b');
    const b=new THREE.Mesh(new THREE.BoxGeometry(2*CURB+26,14,1.8),[dk,dk,dk,dk,bmF,bmF]);b.position.set(s.x,33,s.y);b.rotation.y=-Math.PI/2-ang;b.castShadow=true;g.add(b);
    if(document.fonts)document.fonts.ready.then(()=>{drawBanner();bt.needsUpdate=true;});})();
  (function(){const fR=new THREE.MeshStandardMaterial({map:T2(chevTex(1)),roughness:.45}),fL=new THREE.MeshStandardMaterial({map:T2(chevTex(-1)),roughness:.45}),postM=wm('#c98b4e',{roughness:.7}),edge=wm('#7d1d0e');let last=-99;
    const bg=new THREE.BoxGeometry(.9,8,17),pg=new THREE.CylinderGeometry(.55,.55,9,10);
    for(let j=0;j<N;j++){const bend=track[j].bend;if(Math.abs(bend)<.7||j-last<20)continue;
      const p=track[(j+3)%N],side=-Math.sign(bend),x=p.x+p.nx*(CURB+26)*side,y=p.y+p.ny*(CURB+26)*side;if(Math.hypot(x,y)>R-60||nearTrack(x,y,CURB+18))continue;last=j;
      const g=new THREE.Group();g.position.set(x,0,y);g.rotation.y=-p.ang;world.add(g);
      const bd=new THREE.Mesh(bg,[edge,bend>0?fR:fL,edge,edge,edge,edge]);bd.position.y=9;bd.castShadow=true;g.add(bd);
      put(pg,postM,0,4.5,-6,g);put(pg,postM,0,4.5,6,g);}})();
  (function(){const tex=T2(padTex(),1,1);const mat=new THREE.MeshStandardMaterial({map:tex,emissive:'#ff6a1a',emissiveMap:tex,emissiveIntensity:1.1,roughness:.3,transparent:true});
    const boxIdx=def.boxes.map(f=>Math.floor(f*N));const cand=[];
    for(let j=30;j<N-30;j++){let ok=true;for(let o=-14;o<=14;o+=2)if(Math.abs(track[(j+o+N)%N].bend)>.18){ok=false;break;}if(ok&&!boxIdx.some(b=>Math.abs(b-j)<24)&&!(GLIDE&&j>GLIDE.rj-40&&j<GLIDE.j1+24)&&!(loopNear(j,45)))cand.push(j);}
    for(let i=0;i<3&&cand.length;i++){const target=Math.floor((i+.3)*N/3);let best=null,bd=1e9;for(const c of cand){const d=Math.abs(c-target);if(d<bd&&!pads.some(p=>Math.abs(p.j-c)<N/6)){bd=d;best=c;}}
      if(best==null)continue;const lat=[-22,0,22][i%3];pads.push({j:best,lat});strip(best-2,best+2,lat-16,lat+16,.1,mat,32);}
    for(const L of LOOPS)if(L.full){const lat=L.lat0;pads.push({j:(L.j-12+N)%N,lat});strip(L.j-14,L.j-10,lat-17,lat+17,.1,mat,32);}
    animators.push((t,dt)=>{tex.offset.y-=dt*1.6;});})();
  ramps=[];obstacles=[];rollers=[];
  const used=[0,...def.boxes.map(f=>Math.floor(f*N)),...pads.map(p=>p.j),...LOOPS.flatMap(L=>L.full?[L.j,L.j-20,L.j-40,L.j-56,L.j+15]:[L.j])];if(GLIDE)for(let j=GLIDE.rj-18;j<=GLIDE.j1+14;j+=6)used.push(j);
  const farFrom=(j,gap)=>used.every(u=>{let d=Math.abs(u-j);d=Math.min(d,N-d);return d>gap;});
  const straight=(j,w,lim)=>{for(let o=-w;o<=w;o+=2)if(Math.abs(track[(j+o+N)%N].bend)>lim)return false;return true;};
  const pick=(target,ok)=>{let best=null,bd=1e9;for(let j=30;j<N-30;j++){if(!ok(j))continue;let d=Math.abs(j-target);d=Math.min(d,N-d);if(d<bd){bd=d;best=j;}}return best;};
  (function(){const topM=new THREE.MeshStandardMaterial({map:T2(rampTex()),roughness:.45}),sideM2=new THREE.MeshStandardMaterial({map:T2(TX.crust,1,1),roughness:.7,side:THREE.DoubleSide});
    for(let i=0;i<3;i++){const b=pick(Math.floor((i+.55)*N/3),j=>straight(j,12,.3)&&farFrom(j,40));if(b==null)continue;used.push(b);const r={j:b,len:4*T.L/N,w:RW-3,h:6};ramps.push(r);buildRamp(r,topM,sideM2);}})();
  if(GLIDE)buildGlide(def);
  (function(){const make=OBST[def.theme]();const pats=[[29],[-29],[-36,36],[31],[-31],[-36,36],[26],[-26]];
    for(let i=0;i<pats.length;i++){const b=pick(Math.floor((i+.3)*N/pats.length),j=>straight(j,8,.4)&&farFrom(j,26));if(b==null)continue;used.push(b);const p=track[b];
      for(const lat of pats[i]){const x=p.x+p.nx*lat,y=p.y+p.ny*lat,g=make();g.position.set(x,0,y);g.rotation.y=rnd()*6;world.add(g);obstacles.push({x,y,r:6,h:26,j:b,lat});}}})();
  (function(){const mm=new THREE.MeshStandardMaterial({map:T2(meatTex()),roughness:.65}),mg=new THREE.SphereGeometry(8,36,24);
    for(let i=0;i<2;i++){const b=pick(Math.floor((i*.5+.3)*N),j=>straight(j,10,.3)&&farFrom(j,30));if(b==null)continue;used.push(b);const m=put(mg,mm,0,8,0);rollers.push({j:b,m,x:track[b].x,y:track[b].y,lat:0,ph:i*2.1});}})();
  for(const LOOP of LOOPS){const p=LOOP.p,g0=LOOP.g0,SEG=128,W=LOOP.W||15,pos=[],uv=[],idx=[],eL=[],eR=[];
    for(let i=0;i<=SEG;i++){const th=i/SEG*Math.PI*2,sx=LOOPR*Math.sin(th),hg=LOOPR*(1-Math.cos(th)),lat=LOOP.lat0+LOOP.shift*i/SEG;
      for(const sd of [-1,1]){const l=lat+sd*W,X=p.x+p.tx*sx+p.nx*l,Z=p.y+p.ty*sx+p.ny*l;pos.push(X,g0+hg+.35,Z);uv.push(sd<0?0:1,i/SEG*9);(sd<0?eL:eR).push(new THREE.Vector3(X,g0+hg+1.6,Z));}
      if(i<SEG){const a=i*2;idx.push(a,a+1,a+2,a+1,a+3,a+2);}}
    const lg=new THREE.BufferGeometry();lg.setAttribute('position',new THREE.Float32BufferAttribute(pos,3));lg.setAttribute('uv',new THREE.Float32BufferAttribute(uv,2));lg.setIndex(idx);lg.computeVertexNormals();
    const lt=T2(padTex(),1,1),lm=new THREE.Mesh(lg,LOOP.full?loopDeckMat(def):new THREE.MeshStandardMaterial({map:lt,emissive:'#ff6a1a',emissiveMap:lt,emissiveIntensity:.9,roughness:.35,side:THREE.DoubleSide}));if(LOOP.full)buildFunnel(LOOP,def);lm.castShadow=lm.receiveShadow=true;lm.userData.noLift=true;world.add(lm);
    animators.push((t,dt)=>{lt.offset.y-=dt*2.2;});
    const railM=wm('#f7c948',{metalness:.6,roughness:.25});for(const e of [eL,eR]){const tm=new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(e),160,1.1,8,false),railM);tm.castShadow=true;tm.userData.noLift=true;world.add(tm);}
    const top=new THREE.Vector3(p.x,g0+2*LOOPR,p.y),bm=wm('#3a3a44',{metalness:.6,roughness:.35}),G=new THREE.Group();G.userData.noLift=true;world.add(G);
    for(const sd of [-1,1]){const bx=p.x+p.nx*(RW+16)*sd,bz=p.y+p.ny*(RW+16)*sd;limb(new THREE.CylinderGeometry(1.8,2.4,1,10),bm,[bx,g0-2,bz],[top.x+p.nx*(W+3)*sd,top.y,top.z+p.ny*(W+3)*sd],G);
      put(new THREE.CylinderGeometry(5,6,3,14),bm,bx,g0,bz,G);obstacles.push({x:bx,y:bz,r:4,h:60,j:LOOP.j,lat:(RW+16)*sd});}
    G.children.forEach(c=>c.castShadow=true);}
  const sideM=new THREE.MeshStandardMaterial({map:T2(TX.side),roughness:.5}),lidM=new THREE.MeshStandardMaterial({map:T2(TX.lid),roughness:.45}),botM=wm('#cdbb94');
  const rr=new THREE.Shape(),BW=3.5,BC=.9;rr.moveTo(-BW+BC,-BW);rr.lineTo(BW-BC,-BW);rr.quadraticCurveTo(BW,-BW,BW,-BW+BC);rr.lineTo(BW,BW-BC);rr.quadraticCurveTo(BW,BW,BW-BC,BW);rr.lineTo(-BW+BC,BW);rr.quadraticCurveTo(-BW,BW,-BW,BW-BC);rr.lineTo(-BW,-BW+BC);rr.quadraticCurveTo(-BW,-BW,-BW+BC,-BW);
  const ibBase=new THREE.ExtrudeGeometry(rr,{depth:1.1,bevelEnabled:true,bevelThickness:.16,bevelSize:.16,bevelSegments:3,curveSegments:6});ibBase.rotateX(-Math.PI/2);ibBase.translate(0,-.95,0);
  const ibLid=new THREE.ExtrudeGeometry(rr,{depth:.4,bevelEnabled:true,bevelThickness:.14,bevelSize:.2,bevelSegments:3,curveSegments:6});ibLid.rotateX(-Math.PI/2);ibLid.translate(0,.4,0);
  const ibSeam=new THREE.BoxGeometry(6.95,.34,6.95),seamM=new THREE.MeshBasicMaterial({color:'#ffcf6a',toneMapped:false}),seam2=new THREE.MeshBasicMaterial({color:'#fff1b0',toneMapped:false});
  const capT=(src)=>{const t=T2(src,1/7.4,1/7.4);t.offset.set(.5,.5);return t;},iSide=new THREE.MeshPhysicalMaterial({map:T2(TX.side,1/6.5,1/1.4),roughness:.5,clearcoat:.4}),iLid=new THREE.MeshPhysicalMaterial({map:capT(TX.lid),roughness:.45,clearcoat:.5});
  const iBoxGeo=new THREE.BoxGeometry(7,1.9,7),ringGeo=new THREE.TorusGeometry(5.8,.32,10,40),glowGeo=new THREE.CircleGeometry(6,32);
  const ringMat=new THREE.MeshBasicMaterial({color:'#ffe9a0',transparent:true,opacity:.9,toneMapped:false}),glowMat=new THREE.MeshBasicMaterial({map:T2(TX.glow),color:'#ffd24a',transparent:true,opacity:.5,depthWrite:false,blending:THREE.AdditiveBlending,toneMapped:false});
  const lid2=cnv(256,256),lg2=lid2.getContext('2d');lg2.fillStyle='#ffd54a';lg2.fillRect(0,0,256,256);lg2.strokeStyle='#b8860b';lg2.lineWidth=14;lg2.strokeRect(10,10,236,236);lg2.fillStyle='#7d1d0e';lg2.font='bold 130px Arial Black,Impact,sans-serif';lg2.textAlign='center';lg2.textBaseline='middle';lg2.fillText('x2',128,138);
  const dSide=new THREE.MeshPhysicalMaterial({color:'#ffd54a',metalness:.6,roughness:.25,clearcoat:1,map:T2(TX.side,1/6.5,1/1.4)}),dLid=new THREE.MeshPhysicalMaterial({map:capT(lid2),metalness:.45,roughness:.28,clearcoat:1}),ring2=new THREE.MeshBasicMaterial({color:'#ffd24a',transparent:true,opacity:.95,toneMapped:false});
  def.boxes.concat(LOOPS.filter(L=>L.full).map(L=>((L.j-66+N)%N)/N)).forEach((f,gi)=>{const p=track[Math.floor(f*N)];[-36,-12,12,36].forEach((o,i)=>{const x=p.x+p.nx*o,y=p.y+p.ny*o,dbl=i===(gi%2?1:2);
    const m=new THREE.Group();for(const [g2,mm] of [[ibBase,dbl?[dSide,dSide]:[iSide,iSide]],[ibLid,dbl?[dLid,dSide]:[iLid,iSide]],[ibSeam,dbl?seam2:seamM]]){const me=new THREE.Mesh(g2,mm);me.castShadow=mm!==seamM&&mm!==seam2;me.receiveShadow=true;m.add(me);}world.add(m);const ring=new THREE.Mesh(ringGeo,dbl?ring2:ringMat);world.add(ring);
    const gl=new THREE.Mesh(glowGeo,glowMat);gl.rotation.x=-Math.PI/2;gl.position.set(x,.3,y);world.add(gl);boxes.push({x,y,r:0,sv:gi*4+i,m,ring,gl,gy:groundAt(x,y),dbl});});});
  animators.push(t=>{glowMat.opacity=.35+Math.sin(t*4)*.15;});

  findShortcuts(def);for(const sc of SHORTS){used.push(sc.a,sc.b);buildShortcut(sc,def);}buildBarrier();
  DBK=new Map();const placed=[];for(const q of PONDS)placed.push([q.x,q.y,Math.max(q.ax,q.az)*1.35]);for(const sc of SHORTS)for(const p of sc.pts)placed.push([p.x,p.y,SCW+14]);const area=Math.min(3.2,(R/512)*(R/512)*.55);
  const spots=[];for(let x=-R+150;x<=R-150;x+=40)for(let y=-R+150;y<=R-150;y+=40){if(Math.hypot(x,y)>R-170)continue;if(nearSC(x,y,140))continue;const d=minTrackDist(x,y);if(d>150)spots.push([x,y,d]);}
  spots.sort((a,b)=>b[2]-a[2]);const L1=spots[0]||[0,0,160];const L2=spots.find(s=>Math.hypot(s[0]-L1[0],s[1]-L1[1])>450)||null;
  placed.push([L1[0],L1[1],95]);if(L2)placed.push([L2[0],L2[1],70]);
  function scatter(geo,mat,count,make,overlap){count=Math.max(1,Math.round(count*area));const q=new THREE.Quaternion(),e=new THREE.Euler(),p=new THREE.Vector3(),s=new THREE.Vector3(),m4=new THREE.Matrix4();let n=0,tries=0,ms=1;const items=[];
    while(n<count&&tries<count*40){tries++;const o=make(),rad=o.rad,a=rnd()*Math.PI*2,r=Math.sqrt(rnd())*(R-60-rad),x=Math.cos(a)*r,y=Math.sin(a)*r;
      if(nearTrack(x,y,CURB+12+rad)||nearSC(x,y,SCW+6+rad)||inPond(x,y,rad+30))continue;if(overlap&&placed.some(([px,py,pr])=>(px-x)**2+(py-y)**2<(pr+rad+4)**2))continue;
      p.set(x,o.y||0,y);e.set(o.rx||0,o.ry||0,o.rz||0);q.setFromEuler(e);s.set(o.sx,o.sy,o.sz);m4.compose(p,q,s);items.push({x,z:y,m:m4.clone()});ms=Math.max(ms,o.sx,o.sy,o.sz);n++;if(overlap)placed.push([x,y,rad]);}
    chunkInst(geo,mat,items,{maxScale:ms});}
  const TOP={
    pep:()=>scatter(new THREE.CylinderGeometry(1,1,1,28),pepMat,48,()=>{const r=10+rnd()*7;return{rad:r,sx:r,sy:1.4,sz:r,y:.7,rx:(rnd()-.5)*.08,rz:(rnd()-.5)*.08};},true),
    olive:()=>scatter(new THREE.TorusGeometry(1,.45,14,30),wm('#2a2230',{roughness:.22,metalness:.1}),36,()=>{const r=4.5+rnd()*2.5;return{rad:r*1.4,sx:r,sy:r,sz:r,y:r*.45,rx:Math.PI/2,rz:rnd()*3};},true),
    mush:()=>{const sh=new THREE.Shape();sh.moveTo(-.35,-1);sh.lineTo(.35,-1);sh.lineTo(.35,0);sh.lineTo(1,0);sh.absarc(0,0,1,0,Math.PI,false);sh.lineTo(-.35,0);sh.closePath();
      return scatter(new THREE.ExtrudeGeometry(sh,{depth:.3,bevelEnabled:true,bevelThickness:.08,bevelSize:.08,bevelSegments:2,curveSegments:16}),wm('#dcc7a2',{roughness:.55}),26,()=>{const r=7+rnd()*3;return{rad:r,sx:r,sy:r,sz:1.6,y:0,rx:-Math.PI/2,rz:rnd()*6};},true);},
    basil:()=>scatter(new THREE.SphereGeometry(1,18,12),wm('#3f8a35',{roughness:.4}),36,()=>{const r=7+rnd()*4;return{rad:r,sx:r,sy:1.1,sz:r*.5,y:.6,ry:rnd()*6,rz:.06};},true),
    tomato:()=>scatter(new THREE.CylinderGeometry(1,1,1,32),wm('#d63a26',{roughness:.3}),18,()=>{const r=8+rnd()*3;return{rad:r,sx:r,sy:1.2,sz:r,y:.6};},true),
    blob:()=>scatter(new THREE.SphereGeometry(1,16,10),wm('#f8d363',{roughness:.3}),110,()=>{const r=6+rnd()*12;return{rad:r*.6,sx:r,sy:1.5+rnd()*1.5,sz:r*(.6+rnd()*.4),y:0,ry:rnd()*6};},false),
    pine:()=>{const sh=new THREE.Shape();sh.moveTo(-1,0);sh.lineTo(1,0);sh.lineTo(.6,1.3);sh.lineTo(-.6,1.3);sh.closePath();
      return scatter(new THREE.ExtrudeGeometry(sh,{depth:.9,bevelEnabled:true,bevelThickness:.12,bevelSize:.12,bevelSegments:2}),wm('#f6d33c',{roughness:.3}),60,()=>{const r=5+rnd()*2.5;return{rad:r*1.1,sx:r,sy:r,sz:r,y:0,rx:-Math.PI/2,rz:rnd()*6};},true);},
    ham:()=>scatter(new THREE.BoxGeometry(1,1,1),wm('#e88a86',{roughness:.45}),60,()=>{const a=7+rnd()*5,b=5+rnd()*4;return{rad:Math.max(a,b)*.7,sx:a,sy:1.6,sz:b,y:.8,ry:rnd()*6};},true),
    jal:()=>scatter(new THREE.TorusGeometry(1,.35,10,24),wm('#4c9a2a',{roughness:.3}),24,()=>{const r=4+rnd()*2;return{rad:r*1.3,sx:r,sy:r,sz:r,y:r*.35,rx:Math.PI/2};},true),
    ice:()=>scatter(new THREE.OctahedronGeometry(1,0),wm('#bfe6ff',{roughness:.06,metalness:.15,flatShading:true}),40,()=>{const r=5+rnd()*8;return{rad:r,sx:r*.8,sy:r*1.4,sz:r*.8,y:r*.6,rx:(rnd()-.5)*.6,ry:rnd()*6,rz:(rnd()-.5)*.6};},true),
    sausage:()=>scatter(new THREE.DodecahedronGeometry(1,1),wm('#7a4528',{roughness:.6}),60,()=>{const r=3+rnd()*2.5;return{rad:r,sx:r,sy:r*.7,sz:r,y:r*.4,ry:rnd()*6,rx:rnd()};},true)
  };
  ({kitchen:['pep','olive','mush','basil','tomato','blob'],bay:['pine','ham','olive','jal','blob'],night:['pep','pep','olive','sausage','basil','blob'],freezer:['pep','olive','mush','ice','ice','blob']})[def.theme].forEach(k=>TOP[k]());
  (def.theme==='kitchen'?([buildKitchen,roomDining,roomOven,roomParty][VAR]||buildKitchen):{bay:buildBay,night:buildNight,freezer:buildFreezer}[def.theme])(R,L1,L2);
  if(VAR>0){const X={bay:bayExtras,night:nightExtras,freezer:freezerExtras}[def.theme];if(X)X(R,L1);}varSky(def);
  decorate(def,R,{used,pick,straight,farFrom,placed});
  detail(def,R,{used,pick,straight,farFrom,placed});
  buildHazards(def,R,{used,pick,straight,farFrom,placed});try{buildDressing(def,{used,pick,straight,farFrom,placed});}catch(e){console.warn('dressing',e);}
  world.updateMatrixWorld(true);{const ws=new THREE.Vector3();world.traverse(o=>{if(!o.isMesh||o.isInstancedMesh||!o.castShadow)return;const g=o.geometry;if(!g.boundingSphere)g.computeBoundingSphere();o.getWorldScale(ws);if(g.boundingSphere.radius*Math.max(ws.x,ws.y,ws.z)<14)o.castShadow=false;});}
  for(const o of world.children){if(o.userData.noLift||o.isInstancedMesh||o.isPoints||o===sky)continue;if(Math.abs(o.position.x)<1&&Math.abs(o.position.z)<1)continue;o.position.y+=groundAt(o.position.x,o.position.z);}
  buildMiniBase();
}

function flagTex(){const c=cnv(128,80),g=c.getContext('2d');g.fillStyle='#e0452c';g.fillRect(0,0,128,80);g.fillStyle='#f7c948';g.beginPath();g.moveTo(64,10);g.lineTo(36,70);g.lineTo(92,70);g.closePath();g.fill();
  g.fillStyle='#b8311c';[[58,48],[70,56],[64,34]].forEach(([x,y])=>{g.beginPath();g.arc(x,y,5,0,7);g.fill();});for(let i=0;i<8;i++){g.fillStyle=i%2?'#fff4dc':'#1b0f0b';g.fillRect(i*16,0,16,6);g.fillRect(i*16,74,16,6);}return c;}
/* ================= STATIC DETAIL (baked once per track, merged per area, never animated) ================= */
const DCELL=420;let detailChunks=[];
const DG=(()=>{const g={box:new THREE.BoxGeometry(1,1,1),cyl:new THREE.CylinderGeometry(1,1,1,10),cyl6:new THREE.CylinderGeometry(1,1,1,6),cone:new THREE.ConeGeometry(1,1,10),cone6:new THREE.ConeGeometry(1,1,6),
  sph:new THREE.SphereGeometry(1,10,7),sphL:new THREE.SphereGeometry(1,6,4),hemi:new THREE.SphereGeometry(1,12,5,0,Math.PI*2,0,Math.PI/2),ico:new THREE.IcosahedronGeometry(1,0),ico1:new THREE.IcosahedronGeometry(1,1),
  dod:new THREE.DodecahedronGeometry(1,0),tor:new THREE.TorusGeometry(1,.42,8,16),plane:new THREE.PlaneGeometry(1,1),disc:new THREE.CircleGeometry(1,10),cap:new THREE.CapsuleGeometry(.5,1,4,8)};
  g.potL=new THREE.LatheGeometry([[0,0],[.7,0],[.82,.1],[1,.95],[1.1,1],[1.1,1.12],[0,1.12]].map(([x,y])=>new THREE.Vector2(x,y)),12);
  g.bottleL=new THREE.LatheGeometry([[0,0],[.5,0],[.5,1.2],[.42,1.45],[.17,1.75],[.17,2.2],[0,2.2]].map(([x,y])=>new THREE.Vector2(x,y)),12);
  g.millL=new THREE.LatheGeometry([[0,0],[.55,0],[.6,.15],[.42,.7],[.5,1.3],[.38,1.75],[.12,1.95],[0,2]].map(([x,y])=>new THREE.Vector2(x,y)),12);
  const w=new THREE.Shape();w.moveTo(0,0);w.lineTo(1,0);w.lineTo(0,.8);w.closePath();g.wedge=new THREE.ExtrudeGeometry(w,{depth:1,bevelEnabled:false});g.wedge.translate(-.35,0,-.5);
  const st=new THREE.Shape();for(let i=0;i<10;i++){const a=i/10*Math.PI*2,r=i%2?.4:1;st[i?'lineTo':'moveTo'](Math.cos(a)*r,Math.sin(a)*r);}g.star=new THREE.ExtrudeGeometry(st,{depth:.25,bevelEnabled:true,bevelSize:.08,bevelThickness:.08,bevelSegments:1});
  return g;})();
function tplOf(list){const P=[],N=[],C=[],GP=[],GC=[],m=new THREE.Matrix4(),q=new THREE.Quaternion(),e=new THREE.Euler(),v=new THREE.Vector3(),n=new THREE.Vector3(),nm=new THREE.Matrix3(),sv=new THREE.Vector3();let rad=0,h=0;
  for(const [g0,col,p,r,s,glow] of list){const g=g0.index?g0.toNonIndexed():g0;const pa=g.attributes.position,na=g.attributes.normal,vc=col==null?g.attributes.color:null,c=new THREE.Color(col==null?'#ffffff':col);
    m.compose(v.set(...(p||[0,0,0])),q.setFromEuler(e.set(...(r||[0,0,0]))),sv.set(...(Array.isArray(s)?s:[s||1,s||1,s||1])));nm.getNormalMatrix(m);
    for(let i=0;i<pa.count;i++){v.fromBufferAttribute(pa,i).applyMatrix4(m);(glow?GP:P).push(v.x,v.y,v.z);rad=Math.max(rad,Math.hypot(v.x,v.z));h=Math.max(h,v.y);
      if(glow)GC.push(c.r,c.g,c.b);else{n.fromBufferAttribute(na,i).applyMatrix3(nm).normalize();N.push(n.x,n.y,n.z);if(vc)C.push(vc.getX(i),vc.getY(i),vc.getZ(i));else C.push(c.r,c.g,c.b);}}
    if(g!==g0)g.dispose();}
  return {P:new Float32Array(P),N:new Float32Array(N),C:new Float32Array(C),GP:new Float32Array(GP),GC:new Float32Array(GC),rad,h};}
let DBK=null;
function dbAdd(t,x,z,ry,s,tint,yOff,blob){const y=groundAt(x,z)+(yOff||0),key=Math.floor(x/DCELL)+','+Math.floor(z/DCELL);let c=DBK.get(key);if(!c){c={L:[],nv:0,ng:0,nb:0};DBK.set(key,c);}
  c.L.push([t,x,y,z,ry||0,s||1,tint||null,blob!==false]);c.nv+=t.P.length/3;c.ng+=t.GP.length/3;if(blob!==false)c.nb++;}
function dbAddM(t,m,tint,lift){const e=m.elements,x=e[12],z=e[14],y=e[13]+(lift?groundAt(x,z):0),key=Math.floor(x/DCELL)+','+Math.floor(z/DCELL);let c=DBK.get(key);if(!c){c={L:[],nv:0,ng:0,nb:0};DBK.set(key,c);}
  c.L.push([t,x,y,z,0,1,tint||null,false,m]);c.nv+=t.P.length/3;c.ng+=t.GP.length/3;}
const _nm3=new THREE.Matrix3();
function dbFlush(){const mat=new THREE.MeshStandardMaterial({vertexColors:true,roughness:.62,metalness:.04}),gmat=new THREE.MeshBasicMaterial({vertexColors:true,toneMapped:false}),
    bmat=new THREE.MeshBasicMaterial({vertexColors:true,transparent:true,depthWrite:false,polygonOffset:true,polygonOffsetFactor:-2,polygonOffsetUnits:-2});
  const BS=12;detailChunks=[];
  for(const [key,c] of DBK){const P=new Float32Array(c.nv*3),N=new Float32Array(c.nv*3),C=new Float32Array(c.nv*3),GP=new Float32Array(c.ng*3),GC=new Float32Array(c.ng*3),BP=new Float32Array(c.nb*BS*9),BC=new Float32Array(c.nb*BS*12);
    let o=0,og=0,ob=0;
    for(const [t,x,y,z,ry,s,tint,blob,mm] of c.L){const cs=Math.cos(ry),sn=Math.sin(ry),tr=tint?tint.r:1,tg=tint?tint.g:1,tb=tint?tint.b:1;
      if(mm){const e=mm.elements;_nm3.getNormalMatrix(mm);const n=_nm3.elements;
        for(let i=0;i<t.P.length;i+=3){const px=t.P[i],py=t.P[i+1],pz=t.P[i+2];P[o]=e[0]*px+e[4]*py+e[8]*pz+x;P[o+1]=e[1]*px+e[5]*py+e[9]*pz+y;P[o+2]=e[2]*px+e[6]*py+e[10]*pz+z;
          const nx=t.N[i],ny=t.N[i+1],nz=t.N[i+2];let a=n[0]*nx+n[3]*ny+n[6]*nz,b=n[1]*nx+n[4]*ny+n[7]*nz,d=n[2]*nx+n[5]*ny+n[8]*nz;const l=Math.hypot(a,b,d)||1;N[o]=a/l;N[o+1]=b/l;N[o+2]=d/l;
          C[o]=t.C[i]*tr;C[o+1]=t.C[i+1]*tg;C[o+2]=t.C[i+2]*tb;o+=3;}continue;}
      for(let i=0;i<t.P.length;i+=3){const px=t.P[i],py=t.P[i+1],pz=t.P[i+2];P[o]=x+(px*cs+pz*sn)*s;P[o+1]=y+py*s;P[o+2]=z+(-px*sn+pz*cs)*s;
        const nx=t.N[i],nz=t.N[i+2];N[o]=nx*cs+nz*sn;N[o+1]=t.N[i+1];N[o+2]=-nx*sn+nz*cs;C[o]=t.C[i]*tr;C[o+1]=t.C[i+1]*tg;C[o+2]=t.C[i+2]*tb;o+=3;}
      for(let i=0;i<t.GP.length;i+=3){const px=t.GP[i],py=t.GP[i+1],pz=t.GP[i+2];GP[og]=x+(px*cs+pz*sn)*s;GP[og+1]=y+py*s;GP[og+2]=z+(-px*sn+pz*cs)*s;GC[og]=t.GC[i];GC[og+1]=t.GC[i+1];GC[og+2]=t.GC[i+2];og+=3;}
      if(blob){const r=Math.max(2,t.rad*s*1.15),yy=y+.35;for(let k=0;k<BS;k++){const a0=k/BS*Math.PI*2,a1=(k+1)/BS*Math.PI*2,b=ob*9+k*9,bc=ob*12+k*12;
          BP.set([x,yy,z,x+Math.cos(a1)*r,yy,z+Math.sin(a1)*r,x+Math.cos(a0)*r,yy,z+Math.sin(a0)*r],b);BC.set([0,0,0,.26,0,0,0,0,0,0,0,0],bc);}ob++;}}
    const cx=(+key.split(',')[0]+.5)*DCELL,cz=(+key.split(',')[1]+.5)*DCELL,sph=new THREE.Sphere(new THREE.Vector3(cx,0,cz),DCELL*.75+60),ms=[];
    const mk=(geo,m,cast)=>{geo.boundingSphere=sph.clone();const me=new THREE.Mesh(geo,m);me.receiveShadow=m===mat;me.castShadow=m===mat;me.userData.noLift=true;me.matrixAutoUpdate=false;me.updateMatrix();world.add(me);ms.push(me);};
    {const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.BufferAttribute(P,3));g.setAttribute('normal',new THREE.BufferAttribute(N,3));g.setAttribute('color',new THREE.BufferAttribute(C,3));mk(g,mat);}
    if(c.ng){const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.BufferAttribute(GP,3));g.setAttribute('color',new THREE.BufferAttribute(GC,3));mk(g,gmat);}
    if(c.nb){const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.BufferAttribute(BP,3));g.setAttribute('color',new THREE.BufferAttribute(BC,4));mk(g,bmat);}
    detailChunks.push({x:cx,z:cz,ms,vis:true});}
  DBK=null;let acc3=0;
  animators.push((t,dt)=>{acc3+=dt;if(acc3<.2)return;acc3=0;const D=(QUAL[qKey].detail||1500)*({near:.65,normal:1,far:1.5}[CFG.detail]||1)*(LADV.det?.8:1)+DCELL*.7,cx=camera.position.x,cz=camera.position.z;
    const sh=qKey!=='fast';for(const ch of detailChunks){const d2=(ch.x-cx)**2+(ch.z-cz)**2,v=ch.vis?d2<(D*1.08)**2:d2<D*D;if(v!==ch.vis||ch.sh!==sh){ch.vis=v;ch.sh=sh;for(const m of ch.ms){m.visible=v;if(m.receiveShadow)m.castShadow=sh;}}}});}
function detailLib(th){const T=tplOf,L={};
  const pal=['#e0452c','#f7c948','#2f7fd8','#3f9a35','#ff8a1f','#7b4bd8','#ff6fae','#fff4dc'];
  L.cone=T([[DG.cone,'#ff6a1a',[0,3,0],0,[1.6,6,1.6]],[DG.cyl,'#ffffff',[0,3.4,0],0,[1.02,1,1.02]],[DG.box,'#ff6a1a',[0,.25,0],0,[4,.5,4]]]);
  L.tires=(()=>{const a=[];for(let i=0;i<3;i++)a.push([DG.tor,i%2?'#e0452c':'#1d1a19',[0,1.25+i*2.3,0],[Math.PI/2,0,0],[3,3,2.6]]);a.push([DG.tor,'#fff4dc',[0,1.25+3*2.3,0],[Math.PI/2,0,0],[3,3,2.6]]);return T(a);})();
  L.barrel=T([[DG.cyl,'#c53b22',[0,4,0],0,[3,8,3]],[DG.cyl,'#7d1d0e',[0,1.6,0],0,[3.12,.5,3.12]],[DG.cyl,'#7d1d0e',[0,6.4,0],0,[3.12,.5,3.12]],[DG.cyl,'#f7c948',[0,8.05,0],0,[2.6,.15,2.6]]]);
  L.crate=T([[DG.box,'#a8743e',[0,3,0],0,[6,6,6]],...[[0,3,3.02,0],[0,3,-3.02,0],[3.02,3,0,1],[-3.02,3,0,1]].map(([x,y,z,r])=>[DG.box,'#7a4f26',[x,y,z],[0,r?Math.PI/2:0,.78],[.8,8,.25]]),[DG.box,'#7a4f26',[0,6.02,0],0,[6.1,.25,1]]]);
  L.lamp=T([[DG.cyl,'#3a3a44',[0,14,0],0,[.7,28,.7]],[DG.cyl,'#2a2a33',[0,.6,0],0,[2,1.2,2]],[DG.box,'#3a3a44',[3,27.6,0],0,[6.5,.6,.6]],[DG.box,'#2a2a33',[6,27,0],0,[2.6,1.2,1.8]],[DG.box,'#fff2c8',[6,26.3,0],0,[2.2,.3,1.4],1]]);
  L.barrier=T([[DG.box,'#e8e2d8',[0,2.2,0],0,[12,4.4,2.4]],[DG.box,'#e0452c',[-3,2.6,0],0,[3,4.5,2.5]],[DG.box,'#e0452c',[3,2.6,0],0,[3,4.5,2.5]],[DG.box,'#d6cfc4',[0,.4,0],0,[12.6,.8,3.4]]]);
  L.bush=T([[DG.ico1,'#3f8a35',[0,3,0],0,[5,4,5]],[DG.ico1,'#4f9e3e',[3,2.4,1.5],0,[3.4,3,3.4]],[DG.ico1,'#367a2e',[-2.6,2.2,-1.6],0,[3.2,2.8,3.2]],[DG.ico1,'#5aa848',[.6,5.2,-.4],0,[2.6,2.4,2.6]]]);
  L.rock=T([[DG.dod,'#8f8577',[0,2.4,0],[.3,.5,.2],[5,3.6,4.2]],[DG.dod,'#a1978a',[4,1.4,2],[.6,.1,.4],[2.6,2,2.4]],[DG.dod,'#7d7468',[-3.4,1.2,-2],[.1,.9,.5],[2.2,1.8,2]]]);
  L.fans=(()=>{const a=[];for(let i=0;i<7;i++){const x=(i-3)*3.4+(rnd()-.5),z=(i%2)*3.2,c=pal[(rnd()*pal.length)|0],sk=['#f6c548','#e8b68a','#a8714a','#7a4a2a'][(rnd()*4)|0];
    a.push([DG.cyl6,c,[x,2.6,z],0,[1.2,4.2,1.1]],[DG.sphL,sk,[x,5.6,z],0,1.25],[DG.cyl6,c,[x-1.3,5,z],[0,0,.5],[.35,2.4,.35]],[DG.cyl6,c,[x+1.3,5,z],[0,0,-.5],[.35,2.4,.35]]);}
    a.push([DG.box,'#8a7f74',[0,.4,1.6],0,[26,.8,8]]);return T(a);})();
  L.flake=T([[DG.disc,'#4f9e3e',[0,.25,0],[-Math.PI/2,0,0],[1.6,1,1]]]);
  L.crumb=T([[DG.ico,'#d9a55a',[0,.6,0],0,[1.2,.8,1.1]]]);
  L.arch=(()=>{const a=[[new THREE.TorusGeometry(CURB+14,4.2,8,28,Math.PI),'#c98b4e',[0,0,0],0,1],[new THREE.TorusGeometry(CURB+14,4.6,6,28,Math.PI),'#e0452c',[0,0,0],0,[1,1,.35]]];
    for(const s of [-1,1])a.push([DG.cyl,'#7d1d0e',[s*(CURB+14),2,0],0,[7,4,7]]);return T(a);})();
  if(th==='kitchen'){
    L.pot=T([[DG.potL,'#c8643a',[0,0,0],0,[5,6,5]],[DG.cyl,'#4a2c1a',[0,6.4,0],0,[5,.3,5]],[DG.ico1,'#3f9a35',[0,10,0],0,[6,4,6]],[DG.ico1,'#4fae42',[2.4,12.4,1],0,[3.4,2.6,3.4]],[DG.ico1,'#358a2e',[-2.4,11.6,-1.2],0,[3.2,2.6,3.2]],[DG.ico1,'#5abd4c',[0,14.2,0],0,[2.6,2,2.6]]]);
    L.mill=T([[DG.millL,'#6e3f1f',[0,0,0],0,[3.4,9,3.4]],[DG.sph,'#d8d8dc',[0,18.4,0],0,1.2]]);
    L.shaker=T([[DG.cyl,'#eef3f6',[0,5,0],0,[2.6,10,2.6]],[DG.hemi,'#c9ced3',[0,10,0],0,[2.6,2.2,2.6]],[DG.cyl,'#c9ced3',[0,10,0],0,[2.65,.6,2.65]]]);
    L.bottle=T([[DG.bottleL,'#3c7a2a',[0,0,0],0,[3.2,6,3.2]],[DG.cyl,'#2a1c10',[0,13.6,0],0,[.9,1.4,.9]],[DG.box,'#f3e3b4',[0,4.5,2.6],0,[3,3.4,.2]]]);
    L.garlic=T([[DG.sph,'#f4ecdc',[0,3,0],0,[4,3.4,4]],[DG.sph,'#ece0ca',[2.2,2.6,1],0,[2.4,2.6,2.4]],[DG.sph,'#ece0ca',[-2,2.6,-1.2],0,[2.4,2.6,2.4]],[DG.cone6,'#e3d4b8',[0,7,0],0,[1,2.4,1]]]);
    L.mush=T([[DG.cyl,'#efe2c8',[0,2.6,0],0,[1.8,5.2,1.8]],[DG.hemi,'#b98a5c',[0,5,0],0,[5,3.4,5]],[DG.cyl,'#e8dcc4',[0,5,0],0,[4.9,.3,4.9]]]);
    L.cheese=T([[DG.wedge,'#f7c948',[0,0,0],[0,0,0],[12,8,8]],[DG.disc,'#d9a52a',[1,2.4,4.02],0,1.1],[DG.disc,'#d9a52a',[-1.6,1.2,4.02],0,.8],[DG.disc,'#d9a52a',[-.8,4,4.02],0,.7]]);
    L.jar=T([[DG.cyl,'#c53b22',[0,4,0],0,[3,8,3]],[DG.cyl,'#e8e2d8',[0,8.6,0],0,[3.1,1.2,3.1]],[DG.box,'#fff4dc',[0,4,3.02],0,[3.4,3,.1]]]);
    L.plates=T([[DG.cyl,'#f4f1ea',[0,.5,0],0,[7,1,7]],[DG.cyl,'#f4f1ea',[0,1.6,0],0,[6.6,1,6.6]],[DG.cyl,'#2f7fd8',[0,2.2,0],0,[6.7,.15,6.7]],[DG.cyl,'#f4f1ea',[0,2.7,0],0,[6.6,1,6.6]]]);
    L.props=['pot','pot','mill','shaker','bottle','garlic','garlic','mush','mush','cheese','jar','plates','crate','barrel'];L.ground=['flake','crumb'];}
  if(th==='bay'){
    L.palm=(()=>{const a=[];let x=0,y=0;for(let k=0;k<7;k++){const nx=x+k*.5,ny=y+6;a.push([DG.cyl6,k%2?'#8a6a44':'#7a5c3a',[(x+nx)/2,(y+ny)/2,0],[0,0,-.08],[1.6-k*.08,6.4,1.6-k*.08]]);x=nx;y=ny;}
      for(let k=0;k<7;k++){const ang=k/7*Math.PI*2;a.push([DG.sphL,'#2f8a35',[x+Math.cos(ang)*8,y-1.5,Math.sin(ang)*8],[0,-ang,-.4],[10,.6,2.6]]);}a.push([DG.sph,'#6b4a2a',[x,y-1,0],0,1.6]);return T(a);})();
    L.hut=T([[DG.box,'#fff4dc',[0,6,0],0,[14,12,12]],[DG.box,'#2a7fd8',[0,6,6.05],0,[14,12,.1]],[DG.cone,'#e0452c',[0,15,0],[0,Math.PI/4,0],[12,6,12]],[DG.box,'#6b3a1e',[0,3.5,6.1],0,[4,7,.2]]]);
    L.surf=T([[DG.cap,'#ff6fae',[0,7,0],[0,0,.15],[2.6,10,.7]],[DG.cap,'#fff4dc',[0,7,.1],[0,0,.15],[.6,10.4,.72]]]);
    L.castle=T([[DG.box,'#e8c88a',[0,2.5,0],0,[12,5,12]],...[[-5,-5],[5,-5],[-5,5],[5,5]].flatMap(([x,z])=>[[DG.cyl,'#e2bf7d',[x,4.5,z],0,[2.2,9,2.2]],[DG.cone,'#d9b26e',[x,10.5,z],0,[2.6,3,2.6]]]),[DG.box,'#e0452c',[0,10,0],0,[.2,4,2.6]]]);
    L.starfish=T([[DG.star,'#ff8a1f',[0,.3,0],[-Math.PI/2,0,0],3.2]]);
    L.ball=T([[DG.sph,'#ffffff',[0,3,0],0,3],[DG.sph,'#e0452c',[0,3,0],0,[3.05,3.05,1.2]],[DG.sph,'#2a7fd8',[0,3,0],0,[1.2,3.05,3.05]]]);
    L.tower=T([...[[-3,-3],[3,-3],[-3,3],[3,3]].map(([x,z])=>[DG.box,'#fff4dc',[x,7,z],0,[.8,14,.8]]),[DG.box,'#e0452c',[0,15,0],0,[9,4,9]],[DG.cone,'#fff4dc',[0,20,0],[0,Math.PI/4,0],[8,4,8]],[DG.box,'#e8e2d8',[0,8,4.5],[.5,0,0],[3,.4,10]]]);
    L.shell=T([[DG.hemi,'#f6d3c4',[0,0,0],0,[2.2,1.4,2.6]]]);
    const PG=n=>propGeos(n)[n];L.treeA=T([[PG('tree_round1'),null,[0,0,0],0,1.15]]);L.treeB=T([[PG('tree_round2'),null,[0,0,0],0,1.0]]);L.shrub=T([[PG('tree_shrub'),null,[0,0,0],0,1.6]]);
    L.props=['palm','palm','hut','surf','castle','starfish','ball','tower','rock','treeA','treeB','treeA','shrub','shrub','crate'];L.ground=['shell','starfish'];}
  if(th==='night'){
    L.neon=T([[new THREE.TorusGeometry(10,.7,6,24,Math.PI),'#ff4fa8',[0,2,0],0,1,1],[DG.box,'#20222c',[-10,1,0],0,[2,2,2]],[DG.box,'#20222c',[10,1,0],0,[2,2,2]]]);
    L.block=(()=>{const a=[[DG.box,'#1d2033',[0,18,0],0,[22,36,18]],[DG.box,'#262a40',[0,36.6,0],0,[23,1.2,19]]];for(let r=0;r<5;r++)for(let c=0;c<4;c++)if(rnd()<.6)a.push([DG.box,rnd()<.5?'#ffd27a':'#9fc8ff',[-7.5+c*5,6+r*6.4,9.05],0,[2.6,3.4,.1],1]);return T(a);})();
    L.drum=T([[DG.cyl,'#2f6fd8',[0,4,0],0,[3,8,3]],[DG.cyl,'#1d3f80',[0,2.4,0],0,[3.1,.5,3.1]],[DG.cyl,'#1d3f80',[0,5.6,0],0,[3.1,.5,3.1]]]);
    L.post=T([[DG.cyl,'#2a2a33',[0,6,0],0,[.8,12,.8]],[DG.sph,'#7fd0ff',[0,12.6,0],0,1.4,1]]);
    L.props=['block','neon','drum','drum','crate','rock','post','post','barrel'];L.ground=['crumb'];}
  if(th==='freezer'){
    L.cubes=T([[DG.box,'#cdeeff',[0,3,0],[0,.3,0],6],[DG.box,'#b8e2ff',[4,2.6,3],[0,.9,0],5.2],[DG.box,'#e2f5ff',[1.6,8,1],[.2,.5,.1],4.6]]);
    L.snowman=T([[DG.sph,'#f6fbff',[0,4.5,0],0,5],[DG.sph,'#f6fbff',[0,11,0],0,3.6],[DG.sph,'#f6fbff',[0,16,0],0,2.6],[DG.cone,'#ff8a1f',[0,16,2.4],[Math.PI/2,0,0],[.5,2.4,.5]],[DG.sph,'#1d1a19',[-.9,16.8,2.2],0,.35],[DG.sph,'#1d1a19',[.9,16.8,2.2],0,.35],[DG.cyl,'#e0452c',[0,13.9,0],0,[2.9,.9,2.9]]]);
    L.pine=T([[DG.cyl6,'#6b4a2a',[0,2.5,0],0,[1.2,5,1.2]],[DG.cone,'#2f6a4a',[0,9,0],0,[7,9,7]],[DG.cone,'#eef6ff',[0,10.6,0],0,[6,6,6]],[DG.cone,'#2f6a4a',[0,14.5,0],0,[5,7,5]],[DG.cone,'#f6fbff',[0,17,0],0,[3.6,4,3.6]]]);
    L.pop=T([[DG.box,'#e6d2a8',[0,2.6,0],0,[.7,5.2,.4]],[DG.cap,'#ff6fae',[0,8.4,0],0,[3.4,6,1.8]],[DG.cap,'#7b4bd8',[0,10.4,0],0,[3.45,2,1.85]]]);
    L.peas=T([[DG.sph,'#5fb648',[0,2,0],0,2],[DG.sph,'#4fa53c',[3,1.8,1],0,1.8],[DG.sph,'#6cc356',[-2.4,1.8,1.6],0,1.8],[DG.sph,'#5fb648',[.6,1.8,-2.8],0,1.8],[DG.sph,'#58b043',[.4,4.6,.2],0,1.7]]);
    {const snowC=(g,amt)=>{const c=g.clone(),ca=c.attributes.color,na=c.attributes.normal;for(let i=0;i<ca.count;i++){const up=Math.max(0,na.getY(i)),k=Math.min(1,Math.max(0,(up-.25)*2))*amt;ca.setXYZ(i,ca.getX(i)+(.92-ca.getX(i))*k,ca.getY(i)+(.95-ca.getY(i))*k,ca.getZ(i)+(1-ca.getZ(i))*k);}return c;};
      L.pineA=T([[snowC(propGeos('tree_pine1').tree_pine1,.75),null,[0,0,0],0,1.15]]);L.pineB=T([[snowC(propGeos('tree_pine2').tree_pine2,.75),null,[0,0,0],0,1.2]]);}
    L.props=['cubes','cubes','snowman','pineA','pineB','pineA','pine','pop','peas','crate','rock'];L.ground=['crumb'];}
  return L;}
function detail(def,R,ctx){const {pick,straight,farFrom,placed,used}=ctx,th=def.theme,L=detailLib(th);
  const okPt=(x,z,rad,inner)=>{if(Math.hypot(x,z)>R-70-rad)return false;if(nearTrack(x,z,CURB+(inner==null?14:inner)+rad))return false;if(GLIDE&&pitAt(x,z)>1)return false;
    for(const o of obstacles)if((o.x-x)**2+(o.y-z)**2<(o.r+rad+4)**2)return false;return !placed.some(([px,py,pr])=>(px-x)**2+(py-z)**2<(pr+rad+3)**2);};
  const area=Math.min(3.2,(R/512)*(R/512)*.55);
  /* themed props, in little clusters so the pizza reads as busy rather than sprinkled */
  const nC=Math.round(46*area);
  for(let c=0,tries=0;c<nC&&tries<nC*30;tries++){const a=rnd()*6.283,r=Math.sqrt(rnd())*(R-120),cx=Math.cos(a)*r,cz=Math.sin(a)*r;if(!okPt(cx,cz,30,10))continue;c++;
    const n=2+((rnd()*4)|0),kind=L.props[(rnd()*L.props.length)|0];
    for(let k=0;k<n;k++){const t=L[k===0?kind:L.props[(rnd()*L.props.length)|0]],s=.75+rnd()*.6,x=cx+(rnd()-.5)*60,z=cz+(rnd()-.5)*60,rad=t.rad*s;if(!okPt(x,z,rad,8))continue;placed.push([x,z,rad]);dbAdd(t,x,z,rnd()*6.283,s);}}
  for(let i=0,tries=0;i<Math.round(70*area)&&tries<4000;tries++){const kind=['bush','rock','bush'][(rnd()*3)|0],t=L[kind],s=.7+rnd()*.8,a=rnd()*6.283,r=Math.sqrt(rnd())*(R-90),x=Math.cos(a)*r,z=Math.sin(a)*r,rad=t.rad*s;if(!okPt(x,z,rad,6))continue;placed.push([x,z,rad]);dbAdd(t,x,z,rnd()*6.283,s);i++;}
  /* ground sprinkles: herbs and crumbs, too small to need shadows */
  for(let i=0,tries=0;i<Math.round(700*area)&&tries<20000;tries++){const a=rnd()*6.283,r=Math.sqrt(rnd())*(R-80),x=Math.cos(a)*r,z=Math.sin(a)*r;if(nearTrack(x,z,CURB+12)||(GLIDE&&pitAt(x,z)>1))continue;
    dbAdd(L[L.ground[(rnd()*L.ground.length)|0]],x,z,rnd()*6.283,.6+rnd()*.9,null,0,false);i++;}
  /* trackside: lamps on straights, cones at the apex of bends, tyre stacks behind the outside walls, fans along the straights */
  let lastLamp=-99,lastCone=-99,lastFan=-99,lastTire=-99;
  for(let j=0;j<N;j++){const p=track[j],b=p.bend;if(GLIDE&&j>GLIDE.rj-25&&j<GLIDE.j1+25)continue;if(loopNear(j,30))continue;
    if(Math.abs(b)<.18&&j-lastLamp>26){const sd=(j>>4)%2?1:-1,off=(WALLD+9)*sd,x=p.x+p.nx*off,z=p.y+p.ny*off;if(okPt(x,z,3,16)&&!nearTrack(x,z,WALLD+5)){lastLamp=j;placed.push([x,z,4]);dbAdd(th==='night'?L.lamp:L.lamp,x,z,-p.ang+(sd>0?Math.PI/2:-Math.PI/2),1);obstacles.push({x,y:z,r:1.5,h:30,j,lat:off});}}
    if(Math.abs(b)>.55&&j-lastCone>14){const sd=-Math.sign(b),off=(CURB+6)*sd,x=p.x+p.nx*off,z=p.y+p.ny*off;if(!nearTrack(x,z,CURB+3)){lastCone=j;for(let k=0;k<3;k++){const xx=x+p.tx*(k-1)*9,zz=z+p.ty*(k-1)*9;dbAdd(L.cone,xx,zz,rnd()*6,1);}}}
    if(p.wall&&j-lastTire>9){const off=(CURB+24)*p.wall,x=p.x+p.nx*off,z=p.y+p.ny*off;if(okPt(x,z,4,18)){lastTire=j;placed.push([x,z,4]);dbAdd(L.tires,x,z,rnd()*6,1);}}
    if(Math.abs(b)<.25&&j-lastFan>55&&!p.wall){const sd=(j>>5)%2?-1:1,off=(CURB+46)*sd,x=p.x+p.nx*off,z=p.y+p.ny*off;if(okPt(x,z,16,30)){lastFan=j;placed.push([x,z,16]);dbAdd(L.fans,x,z,-p.ang+(sd>0?Math.PI:0),1);
      }}}
  /* crust arches over the track */
  for(let i=0;i<2;i++){const b=pick(Math.floor((i+.42)*N/2),j=>straight(j,14,.2)&&farFrom(j,30)&&!(GLIDE&&j>GLIDE.rj-40&&j<GLIDE.j1+30));if(b==null)continue;used.push(b);
    for(let k=-2;k<=2;k++){const p=track[(b+k*5+N)%N],gy=Math.max(groundAt(p.x+p.nx*(CURB+14),p.y+p.ny*(CURB+14)),groundAt(p.x-p.nx*(CURB+14),p.y-p.ny*(CURB+14)));
      dbAdd(L.arch,p.x,p.y,-p.ang-Math.PI/2,1,null,gy-groundAt(p.x,p.y),false);
      for(const s of [-1,1])obstacles.push({x:p.x+p.nx*(CURB+14)*s,y:p.y+p.ny*(CURB+14)*s,r:6,h:90,j:(b+k*5+N)%N,lat:(CURB+14)*s});}}
  dbFlush();}

function decorate(def,R,ctx){const {used,pick,straight,farFrom,placed}=ctx,th=def.theme,q=new THREE.Quaternion(),e=new THREE.Euler(),m4=new THREE.Matrix4(),V=(x,y,z)=>new THREE.Vector3(x,y,z),ONE=V(1,1,1);
  const M=(x,y,z,ry,s)=>{q.setFromEuler(e.set(0,ry||0,0));return new THREE.Matrix4().compose(V(x,y,z),q.clone(),s?(s.isVector3?s:V(s,s,s)):ONE);};
  const free=(rad,inner)=>{for(let t=0;t<80;t++){const a=rnd()*Math.PI*2,r=Math.sqrt(rnd())*(R-70-rad),x=Math.cos(a)*r,y=Math.sin(a)*r;if(nearTrack(x,y,CURB+(inner||16)+rad))continue;if(placed.some(([px,py,pr])=>(px-x)**2+(py-y)**2<(pr+rad+4)**2))continue;placed.push([x,y,rad]);return [x,y];}return null;};
  /* barrier walls of dough balls on the outside of bends */
  const bI=[],cA=new THREE.Color(th==='night'?'#3a6fd8':th==='freezer'?'#4aa8e8':'#e0452c'),cB=new THREE.Color(th==='night'||th==='freezer'?'#e4ecff':'#fff4dc');
  for(let j=0;j<N;j++){const p=track[j];if(!p.wall)continue;const o=(CURB+11)*p.wall,x=p.x+p.nx*o,z=p.y+p.ny*o;for(let r=0;r<2;r++)bI.push({x,z,m:M(x,3.8+r*6.6,z),c:(j+r)%2?cA:cB});}
  chunkInst(new THREE.SphereGeometry(3.8,14,10),new THREE.MeshStandardMaterial({roughness:.45}),bI,{cast:true,extra:10});
  /* overhead banner gantries */
  const gm=new THREE.MeshStandardMaterial({map:T2(bannerC),roughness:.5}),pm=wm('#3a3a44',{metalness:.6,roughness:.35}),dk=wm('#1b0f0b');
  for(let i=0;i<3;i++){const b=pick(Math.floor((i+.18)*N/3),j=>straight(j,6,.35)&&farFrom(j,14)&&!track[j].wall);if(b==null)continue;used.push(b);const p=track[b],g=new THREE.Group();g.position.set(p.x,0,p.y);g.rotation.y=-Math.PI/2-p.ang;world.add(g);
    for(const sd of [-1,1]){put(new THREE.BoxGeometry(2.6,36,2.6),pm,sd*(CURB+6),18,0,g);obstacles.push({x:p.x+p.nx*sd*(CURB+6),y:p.y+p.ny*sd*(CURB+6),r:2.5,h:40,j:b,lat:sd*(CURB+6)});}
    put(new THREE.BoxGeometry(2*CURB+16,3,3),pm,0,35,0,g);const bn=new THREE.Mesh(new THREE.BoxGeometry(2*CURB-10,11,1),[dk,dk,dk,dk,gm,gm]);bn.position.y=27;bn.castShadow=true;g.add(bn);}
  /* grandstand with cheering fans at the start */
  (function(){const p=track[0],sd=p.wall===-1?1:-1;for(let zz=-130;zz<=130;zz+=26)for(const off of [CURB+38,CURB+95]){const x=p.x+p.nx*off*sd-p.tx*zz,y=p.y+p.ny*off*sd-p.ty*zz;if(nearTrack(x,y,CURB+20)||Math.hypot(x,y)>R-60)return;}
    const g=new THREE.Group();g.position.set(p.x,0,p.y);g.rotation.y=-Math.PI/2-p.ang;world.add(g);const st=wm('#9a8f86',{roughness:.8}),roof=new THREE.MeshStandardMaterial({map:T2(stripeTex('#e0452c','#fff4dc',24)),roughness:.6,side:THREE.DoubleSide});
    for(let t=0;t<4;t++)put(new THREE.BoxGeometry(12,6+t*6,250),st,sd*(CURB+44+t*12),(6+t*6)/2,0,g);
    put(new THREE.BoxGeometry(60,1.6,258),roof,sd*(CURB+62),44,0,g);for(const zz of [-122,0,122])put(new THREE.CylinderGeometry(1,1,44,8),pm,sd*(CURB+89),22,zz,g);
    const fans=[],cols=RACERS.map(r=>new THREE.Color(r.color));for(let t=0;t<4;t++)for(let i=0;i<32;i++)fans.push({x:sd*(CURB+44+t*12)+(rnd()-.5)*3,y:6+t*6,z:-118+i*7.6+(rnd()-.5)*2,ph:rnd()*6,c:cols[(rnd()*8)|0]});
    const bodyG=new THREE.CylinderGeometry(1.5,1.9,4.6,8),headG=new THREE.SphereGeometry(1.6,10,8);
    const bi=new THREE.InstancedMesh(bodyG,new THREE.MeshStandardMaterial({roughness:.6}),fans.length),hi=new THREE.InstancedMesh(headG,wm('#f6c548',{roughness:.5}),fans.length);
    fans.forEach((f,i)=>bi.setColorAt(i,f.c));g.add(bi);g.add(hi);bi.castShadow=hi.castShadow=false;bi.frustumCulled=hi.frustumCulled=false;
    let acc2=0;const upd=t=>{fans.forEach((f,i)=>{const b=Math.max(0,Math.sin(t*6+f.ph))*.9;m4.makeTranslation(f.x,f.y+2.3+b,f.z);bi.setMatrixAt(i,m4);m4.makeTranslation(f.x,f.y+6.2+b,f.z);hi.setMatrixAt(i,m4);});bi.instanceMatrix.needsUpdate=hi.instanceMatrix.needsUpdate=true;};
    upd(0);animators.push((t,dt)=>{acc2+=dt;if(acc2<.033)return;acc2=0;if((camera.position.x-p.x)**2+(camera.position.z-p.y)**2<700*700)upd(t);});})();
  /* flags along the straights */
  const poles=[],flags=[];for(let j=24;j<N;j+=36){const sd=(Math.floor(j/36)%2)?1:-1,p=track[j],off=(WALLD+12)*sd,x=p.x+p.nx*off,z=p.y+p.ny*off;
    if(obstacles.some(o=>(o.x-x)**2+(o.y-z)**2<500)||nearTrack(x,z,CURB+12)||nearSC(x,z,SCW+8))continue;poles.push({x,z,m:M(x,13,z)});flags.push({x,z,m:M(x-p.tx*5.5,22,z-p.ty*5.5,-p.ang)});}
  chunkInst(new THREE.CylinderGeometry(.55,.7,26,8),pm,poles,{cast:true,extra:14});
  chunkInst(new THREE.PlaneGeometry(10,6.4),new THREE.MeshStandardMaterial({map:T2(flagTex()),roughness:.6,side:THREE.DoubleSide}),flags,{cast:true,extra:24});
  /* theme props on the pizza */
  if(th==='kitchen'){const st=[],cp=[],tm=[];for(let i=0;i<34;i++){const sp=free(14);if(!sp)break;const s=.8+rnd()*.7,ry=rnd()*6;st.push({x:sp[0],z:sp[1],m:M(sp[0],9*s,sp[1],ry,s)});cp.push({x:sp[0],z:sp[1],m:M(sp[0],17*s,sp[1],ry,s)});}
    chunkInst(new THREE.CylinderGeometry(4,5,18,14),wm('#f1e6d0',{roughness:.6}),st,{cast:true,maxScale:1.5});
    chunkInst(new THREE.SphereGeometry(12,20,10,0,Math.PI*2,0,Math.PI/2),wm('#9c7650',{roughness:.5}),cp,{cast:true,maxScale:1.5});
    for(let i=0;i<46;i++){const sp=free(6);if(!sp)break;tm.push({x:sp[0],z:sp[1],m:M(sp[0],5,sp[1],0,1)});}
    chunkInst(new THREE.SphereGeometry(5.5,18,12),wm('#d9301c',{roughness:.2}),tm,{cast:true});
    const metal=wm('#dfe3e6',{metalness:1,roughness:.15});const AT=a=>[Math.cos(a)*(R+260),Math.sin(a)*(R+260)];
    {const [x,z]=AT(.15),g=new THREE.Group();g.position.set(x,-56,z);g.rotation.y=.9;world.add(g);put(new THREE.BoxGeometry(260,6,26),metal,0,0,0,g);put(new THREE.BoxGeometry(120,5,60),metal,190,0,0,g);for(let i=0;i<4;i++)put(new THREE.BoxGeometry(110,4,8),metal,300,0,-24+i*16,g);bake(g);}
    {const [x,z]=AT(.45),g=new THREE.Group();g.position.set(x,-56,z);g.rotation.y=1.2;world.add(g);put(new THREE.BoxGeometry(240,8,30),wm('#3a2414',{roughness:.4}),0,0,0,g);put(new THREE.BoxGeometry(260,3,46),metal,250,0,0,g);bake(g);}
    for(const [a,c] of [[3.5,'#fff4dc'],[3.62,'#2a2230']]){const [x,z]=AT(a),g=new THREE.Group();g.position.set(x,-60,z);world.add(g);put(new THREE.CylinderGeometry(40,46,160,32),wm(c,{roughness:.3}),0,80,0,g);put(new THREE.SphereGeometry(40,32,16,0,Math.PI*2,0,Math.PI/2),metal,0,160,0,g);bake(g);}}
  if(th==='bay'){const trunkM=wm('#8a6a44',{roughness:.8}),leafM=wm('#2f8a35',{roughness:.5,side:THREE.DoubleSide}),leafG=new THREE.SphereGeometry(1,12,6),trunkG=new THREE.CylinderGeometry(2.6,3,1,10);
    for(let i=0;i<18;i++){const sp=free(20,22);if(!sp)break;const g=new THREE.Group();g.position.set(sp[0],0,sp[1]);g.rotation.y=rnd()*6;world.add(g);const h=55+rnd()*35,lean=(rnd()-.5)*.6;let px=0,py=0;
      for(let k=0;k<6;k++){const ny=py+h/6,nx=px+lean*(k/6)*h/6;limb(trunkG,trunkM,[px,py,0],[nx,ny,0],g);px=nx;py=ny;}
      for(let k=0;k<7;k++){const a=k/7*Math.PI*2,l=new THREE.Mesh(leafG,leafM);l.scale.set(18,1,4);l.position.set(px+Math.cos(a)*14,py-3,Math.sin(a)*14);l.rotation.set(0,-a,-.35);g.add(l);}bake(g);}
    const um=new THREE.MeshStandardMaterial({map:T2(stripeTex('#2a7fd8','#fff4dc',12)),roughness:.6,side:THREE.DoubleSide});
    for(let i=0;i<12;i++){const sp=free(16);if(!sp)break;const g=new THREE.Group();g.position.set(sp[0],0,sp[1]);world.add(g);put(new THREE.CylinderGeometry(.6,.6,22,6),wm('#eeeeee'),0,11,0,g);put(new THREE.ConeGeometry(16,6,12,1,true),um,0,22,0,g);
      put(new THREE.BoxGeometry(14,.6,7),wm(['#e0452c','#f7c948','#2f9a3e'][i%3],{roughness:.8}),9,.4,6,g).rotation.y=rnd();bake(g);}
    const bu=[],cR=new THREE.Color('#e0452c'),cW=new THREE.Color('#fff4dc');for(let i=0;i<60;i++){const a=i/60*Math.PI*2+rnd()*.05,d=R+60+rnd()*40,x=Math.cos(a)*d,z=Math.sin(a)*d;bu.push({x,z,m:M(x,-12,z),c:i%2?cR:cW});}
    chunkInst(new THREE.SphereGeometry(5,14,10),new THREE.MeshStandardMaterial({roughness:.35}),bu,{});
    for(let i=0;i<3;i++){const a=i*2.1+.5,d=R+380+i*120,g=new THREE.Group();g.position.set(Math.cos(a)*d,-14,Math.sin(a)*d);g.rotation.y=-a;world.add(g);
      const hs=new THREE.Shape();hs.moveTo(-40,0);hs.lineTo(30,0);hs.quadraticCurveTo(60,0,70,14);hs.lineTo(-40,14);hs.closePath();const hull=put(new THREE.ExtrudeGeometry(hs,{depth:28,bevelEnabled:true,bevelSize:2,bevelThickness:2}),wm('#fff4dc',{roughness:.4}),0,-4,-14,g);
      put(new THREE.BoxGeometry(30,14,22),wm('#2a7fd8',{roughness:.4}),-10,17,0,g);put(new THREE.CylinderGeometry(1,1,60,8),wm('#8a6a44'),10,40,0,g);bake(g);
      animators.push(t=>{g.position.y=-14+Math.sin(t*1.2+i)*1.5;g.rotation.z=Math.sin(t*.9+i)*.03;});}}
  if(th==='freezer'){const pe=[],cr=[];for(let i=0;i<60;i++){const sp=free(6);if(!sp)break;pe.push({x:sp[0],z:sp[1],m:M(sp[0],4.5,sp[1],0,1)});}
    chunkInst(new THREE.SphereGeometry(4.5,14,10),wm('#5fb648',{roughness:.35}),pe,{cast:true});
    for(let i=0;i<26;i++){const sp=free(16);if(!sp)break;for(let k=0;k<4;k++){const s=5+rnd()*7;q.setFromEuler(e.set((rnd()-.5)*.7,rnd()*6,(rnd()-.5)*.7));cr.push({x:sp[0],z:sp[1],m:new THREE.Matrix4().compose(V(sp[0]+(rnd()-.5)*14,s*1.1,sp[1]+(rnd()-.5)*14),q.clone(),V(s,s*2.2,s))});}}
    chunkInst(new THREE.OctahedronGeometry(1,0),new THREE.MeshStandardMaterial({color:'#a8dcff',roughness:.05,metalness:.2,flatShading:true}),cr,{cast:true,maxScale:26});}
  if(th==='night'){const tp=[],tf=[];for(let j=10;j<N;j+=22){const sd=(Math.floor(j/22)%2)?-1:1,p=track[j];if(p.wall!==sd)continue;const off=(CURB+38)*sd,x=p.x+p.nx*off,z=p.y+p.ny*off;if(nearTrack(x,z,CURB+30))continue;tp.push({x,z,m:M(x,8,z)});tf.push({x,z,m:M(x,18,z)});}
    chunkInst(new THREE.CylinderGeometry(1,1.4,16,8),wm('#2a2a33',{metalness:.6,roughness:.4}),tp,{cast:true,extra:10});
    const flameM=new THREE.MeshBasicMaterial({color:'#ffb347',toneMapped:false});chunkInst(new THREE.ConeGeometry(2.4,6,10),flameM,tf,{receive:false,extra:10});
    animators.push(t=>{flameM.color.setHSL(.08+Math.sin(t*12)*.015,1,.6+Math.sin(t*17)*.05);});
    const bo=[];for(let i=0;i<60;i++){const s=8+rnd()*16,sp=free(s);if(!sp)break;q.setFromEuler(e.set(rnd(),rnd()*6,rnd()));bo.push({x:sp[0],z:sp[1],m:new THREE.Matrix4().compose(V(sp[0],s*.35,sp[1]),q.clone(),V(s,s*.75,s))});}
    chunkInst(new THREE.DodecahedronGeometry(1,0),new THREE.MeshStandardMaterial({map:T2(TX.crust,1,1),roughness:.85,flatShading:true}),bo,{cast:true,maxScale:24});
    (function(){const p=track[Math.floor(N*.5)],sd=p.wall===1?-1:1,x=p.x+p.nx*(CURB+70)*sd,z=p.y+p.ny*(CURB+70)*sd;if(nearTrack(x,z,CURB+40))return;const c=cnv(512,128),g2=c.getContext('2d');g2.fillStyle='#0b0d18';g2.fillRect(0,0,512,128);
      g2.font='72px Bungee, "Arial Black", Impact, sans-serif';g2.textAlign='center';g2.textBaseline='middle';g2.shadowColor='#ff3b8a';g2.shadowBlur=18;g2.fillStyle='#ff6fb0';g2.fillText('CRUST RUSH',256,64);
      const g=new THREE.Group();g.position.set(x,0,z);g.rotation.y=-Math.PI/2-p.ang;world.add(g);for(const s2 of [-1,1])put(new THREE.BoxGeometry(2,40,2),wm('#2a2a33'),s2*44,20,0,g);
      put(new THREE.BoxGeometry(96,26,2),new THREE.MeshStandardMaterial({color:'#0b0d18',emissive:'#ffffff',emissiveMap:T2(c),emissiveIntensity:1.4,map:T2(c)}),0,48,0,g);bake(g,false);})();}
}
function snowTex(){const S=1024,c=cnv(S,S),g=c.getContext('2d');g.fillStyle='#eef5fb';g.fillRect(0,0,S,S);for(let i=0;i<900;i++){const x=rnd()*S,y=rnd()*S,r=4+rnd()*26,a=rnd()*3,col=rnd()<.5?'200,220,238':'255,255,255';wrap9(S,S,(ox,oy)=>{g.fillStyle='rgba('+col+',.45)';g.beginPath();g.ellipse(x+ox,y+oy,r,r*.6,a,0,7);g.fill();});}return c;}
function frozenTex(){const c=cnv(256,256),g=c.getContext('2d');g.fillStyle='#2a7fd8';g.fillRect(0,0,256,256);g.fillStyle='#fff4dc';g.fillRect(0,80,256,96);g.fillStyle='#e0452c';g.font='bold 34px Arial Black,Impact,sans-serif';g.textAlign='center';g.fillText('FROZEN',128,124);g.fillText('PIZZA',128,162);
  for(let i=0;i<60;i++){g.fillStyle='rgba(255,255,255,.5)';g.beginPath();g.arc(rnd()*256,rnd()*256,1+rnd()*3,0,7);g.fill();}return c;}
function buildFreezer(R,L1,L2){
  const ground=put(new THREE.PlaneGeometry(40000,40000),new THREE.MeshStandardMaterial({map:T2(snowTex(),110,110),roughness:.85}),0,-60,0,world,false);ground.rotation.x=-Math.PI/2;if(VAR===1)ground.visible=false;
  const q=new THREE.Quaternion(),m4=new THREE.Matrix4(),e=new THREE.Euler();
  if(VAR!==1){mountainRing({r0:R+1300,r1:R+4800,h:1500,cols:['#dfeaf4','#a9bfd4','#5f7388','#ffffff'],base:-60,seed:4,snow:.5,rough:.7});mountainModels(7,R+1500,R+2300,1.25,.9,'#dfe8f4');}
  if(VAR!==1){forest(ring(120,R+140,R+1300,(x,z)=>[rnd()<.5?'tree_pine1':'tree_pine2',x,z,2.4+rnd()*2.2]),-60,.8);mountainRing({r0:8200,r1:13000,h:3200,cols:['#b9cde0','#8fa6bf','#5d6f84','#ffffff'],base:-60,seed:9,snow:.45,rough:.7});cloudRing(12,9500,1900,'#ffffff',.8);}
  const fT=T2(frozenTex()),side=new THREE.MeshStandardMaterial({map:fT,roughness:.6}),top=wm('#dfeefa',{roughness:.7});
  for(let i=0;i<7;i++){const a=i/7*Math.PI*2+.3,D=R+320+rnd()*400,b=new THREE.Mesh(new THREE.BoxGeometry(320,140,240),[side,side,top,top,side,side]);b.position.set(Math.cos(a)*D,10,Math.sin(a)*D);b.rotation.y=rnd()*6;b.receiveShadow=true;world.add(b);}
  const iceM=new THREE.MeshStandardMaterial({color:'#bfe6ff',roughness:.04,metalness:.1,transparent:true,opacity:.82});
  for(let i=0;i<6;i++){const a=i/6*Math.PI*2+.8,D=R+250+rnd()*500,s=90+rnd()*80,c=put(new THREE.BoxGeometry(s,s,s),iceM,Math.cos(a)*D,-60+s/2,Math.sin(a)*D,world,false);c.rotation.set(rnd()*.3,rnd()*6,rnd()*.3);}
  const cg=new THREE.Group();cg.position.set(L1[0],0,L1[1]);world.add(cg);for(let i=0;i<7;i++){const s=18+rnd()*26,o=put(new THREE.OctahedronGeometry(s,0),new THREE.MeshStandardMaterial({color:'#a8dcff',roughness:.05,metalness:.2,flatShading:true}),(rnd()-.5)*50,s*.9,(rnd()-.5)*50,cg);o.scale.y=1.8;o.rotation.set((rnd()-.5)*.5,rnd()*6,(rnd()-.5)*.5);}bake(cg);
  animators.push((t,dt)=>{cg.rotation.y+=dt*.15;});
  if(L2){const sg=new THREE.Group();sg.position.set(L2[0],0,L2[1]);world.add(sg);const dough=wm('#f3dfb4',{roughness:.65});put(new THREE.SphereGeometry(30,28,20),dough,0,26,0,sg);put(new THREE.SphereGeometry(22,28,20),dough,0,68,0,sg);put(new THREE.SphereGeometry(15,24,16),dough,0,100,0,sg);
    for(const y of [60,72])put(new THREE.SphereGeometry(3,10,8),wm('#2d6b27'),0,y,21,sg);put(new THREE.ConeGeometry(3.5,16,10),wm('#ff8a1f'),0,100,18,sg).rotation.x=Math.PI/2;
    for(const sx of [-5,5])put(new THREE.SphereGeometry(2.4,10,8),wm('#111111'),sx,105,13,sg);put(new THREE.CylinderGeometry(14,16,4,24),wm('#e0452c'),0,113,0,sg);put(new THREE.CylinderGeometry(9,10,16,24),wm('#e0452c'),0,122,0,sg);bake(sg);}
  const SN=1400,sp=new Float32Array(SN*3);for(let i=0;i<SN;i++){sp[i*3]=(Math.random()-.5)*900;sp[i*3+1]=Math.random()*320;sp[i*3+2]=(Math.random()-.5)*900;}
  const sgeo=new THREE.BufferGeometry();sgeo.setAttribute('position',new THREE.BufferAttribute(sp,3));const snow=new THREE.Points(sgeo,new THREE.PointsMaterial({color:'#ffffff',size:2.2,transparent:true,opacity:.85,depthWrite:false}));snow.frustumCulled=false;world.add(snow);
  animators.push((t,dt)=>{for(let i=0;i<SN;i++){let y=sp[i*3+1]-dt*(26+(i%7)*3);if(y<0)y+=320;sp[i*3+1]=y;sp[i*3]+=Math.sin(t*.8+i)*dt*4;}sgeo.attributes.position.needsUpdate=true;snow.position.set(camera.position.x,camera.position.y-160,camera.position.z);});
}
/* ================= BACKDROP DETAIL: sculpted mountain rings, clouds, kitchen dressing ================= */
function bnoise(x,y){const i=Math.floor(x),j=Math.floor(y),f=x-i,g=y-j,h=(a,b)=>{const s=Math.sin(a*127.1+b*311.7)*43758.5453;return s-Math.floor(s);},u=f*f*(3-2*f),v=g*g*(3-2*g);
  return (h(i,j)*(1-u)+h(i+1,j)*u)*(1-v)+(h(i,j+1)*(1-u)+h(i+1,j+1)*u)*v;}
function ridge(x,y,oct){let a=0,amp=.55,fr=1,w=1;for(let o=0;o<oct;o++){let n=1-Math.abs(bnoise(x*fr,y*fr)*2-1);n*=n;a+=n*amp*w;w=Math.min(1,n*1.6);fr*=2.05;amp*=.5;}return a;}
/* a ring of real terrain around the arena: ridged noise, coloured by height and steepness */
function mountainRing(o){const {r0,r1,h,cols,base=-60,seed=1,AS=280,RS=22,snow=.72,rough=.95}=o;const pos=[],col=[],idx=[],C=cols.map(c=>new THREE.Color(c)),tmp=new THREE.Color();
  const H=(a,t)=>{const x=Math.cos(a)*(3+seed),y=Math.sin(a)*(3+seed);const env=Math.sin(Math.PI*Math.pow(t,.85));const n=ridge(x*1.4+t*1.7,y*1.4+t*2.3+seed,5);const peaks=.35+.65*bnoise(a*3.1+seed,seed*.7);return env*n*peaks;};
  for(let i=0;i<=RS;i++){const t=i/RS,r=r0+(r1-r0)*t;for(let k=0;k<=AS;k++){const a=k/AS*Math.PI*2,hh=H(a,t)*h;pos.push(Math.cos(a)*r,base+hh,Math.sin(a)*r);}}
  for(let i=0;i<RS;i++)for(let k=0;k<AS;k++){const p=i*(AS+1)+k;idx.push(p,p+AS+1,p+1,p+1,p+AS+1,p+AS+2);}
  const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(pos,3));g.setIndex(idx);g.computeVertexNormals();const nr=g.attributes.normal;
  for(let v=0;v<pos.length/3;v++){const y=(pos[v*3+1]-base)/h,sl=1-nr.getY(v),n=bnoise(pos[v*3]*.004,pos[v*3+2]*.004);
    tmp.copy(C[0]).lerp(C[1],Math.min(1,Math.max(0,y*2.2+n*.3)));tmp.lerp(C[2],Math.min(1,Math.max(0,(Math.min(sl,1)-.18)*2.4)));if(C[3]&&y>snow-.08*n)tmp.lerp(C[3],Math.max(0,Math.min(1,(y-snow+.08*n)*7*Math.max(0,1-sl*.9))));col.push(tmp.r,tmp.g,tmp.b);}
  g.setAttribute('color',new THREE.Float32BufferAttribute(col,3));
  const m=new THREE.Mesh(g,new THREE.MeshStandardMaterial({vertexColors:true,roughness:rough,flatShading:false}));m.receiveShadow=false;m.castShadow=false;m.userData.noLift=true;m.frustumCulled=false;world.add(m);return m;}
let _cloudT=null;
function cloudTex(){if(_cloudT)return _cloudT;const c=cnv(512,256),g=c.getContext('2d');for(let i=0;i<46;i++){const x=60+rnd()*392,y=150-Math.abs(x-256)*.18-rnd()*60,r=26+rnd()*58;
    const gr=g.createRadialGradient(x,y,0,x,y,r);gr.addColorStop(0,'rgba(255,255,255,.95)');gr.addColorStop(.55,'rgba(255,255,255,.55)');gr.addColorStop(1,'rgba(255,255,255,0)');g.fillStyle=gr;g.beginPath();g.arc(x,y,r,0,7);g.fill();}
  for(let i=0;i<30;i++){const x=80+rnd()*352,y=170+rnd()*30,r=20+rnd()*40,gr=g.createRadialGradient(x,y,0,x,y,r);gr.addColorStop(0,'rgba(150,165,190,.35)');gr.addColorStop(1,'rgba(150,165,190,0)');g.fillStyle=gr;g.beginPath();g.arc(x,y,r,0,7);g.fill();}
  _cloudT=T2(c);_cloudT.userData.shared=true;return _cloudT;}
function cloudRing(n,dist,y,tint,op){const mat=new THREE.MeshBasicMaterial({map:cloudTex(),color:tint||'#ffffff',transparent:true,opacity:op||.9,depthWrite:false,fog:false});const grp=new THREE.Group();grp.userData.noLift=true;
  for(let i=0;i<n;i++){const a=i/n*Math.PI*2+rnd()*.3,d=dist*(.8+rnd()*.4),w=1400+rnd()*1600,m=new THREE.Mesh(new THREE.PlaneGeometry(w,w*.5),mat);m.position.set(Math.cos(a)*d,y+rnd()*700,Math.sin(a)*d);m.lookAt(0,m.position.y,0);grp.add(m);}
  world.add(grp);animators.push((t,dt)=>{grp.rotation.y+=dt*.004;});return grp;}
function moonTex(){const S=512,c=cnv(S,S),g=c.getContext('2d');const gr=g.createRadialGradient(S*.42,S*.4,S*.05,S/2,S/2,S/2);gr.addColorStop(0,'#fbfcff');gr.addColorStop(.85,'#d9deea');gr.addColorStop(1,'#b8bfd0');g.fillStyle=gr;g.beginPath();g.arc(S/2,S/2,S/2-2,0,7);g.fill();
  for(let i=0;i<70;i++){const x=S/2+(rnd()-.5)*S*.85,y=S/2+(rnd()-.5)*S*.85;if(Math.hypot(x-S/2,y-S/2)>S*.45)continue;const r=4+rnd()*rnd()*46;g.fillStyle='rgba(120,128,150,'+(.12+rnd()*.2)+')';g.beginPath();g.arc(x,y,r,0,7);g.fill();g.strokeStyle='rgba(255,255,255,.18)';g.lineWidth=2;g.beginPath();g.arc(x-1,y-1,r,Math.PI*.9,Math.PI*1.7);g.stroke();}
  return T2(c);}
/* kitchen dressing: tall windows of daylight, shelves of jars and tins, hanging copper pans */
function kitchenDressing(R){const W=R+1700,shelfM=wm('#6e4527',{roughness:.6}),frame=wm('#f3ead8',{roughness:.5}),sky=new THREE.MeshBasicMaterial({color:'#bfe3ff',toneMapped:false,fog:false}),sun=new THREE.MeshBasicMaterial({color:'#fff6d8',toneMapped:false,transparent:true,opacity:.18,depthWrite:false,blending:THREE.AdditiveBlending,fog:false});
  const g=new THREE.Group();g.userData.noLift=true;world.add(g);const S=new THREE.Group();g.add(S);
  for(const a of [0.15,1.75,3.3,4.9]){const x=Math.cos(a)*(W-6),z=Math.sin(a)*(W-6),w=new THREE.Group();w.position.set(x,520,z);w.lookAt(0,520,0);S.add(w);
    put(new THREE.PlaneGeometry(520,620),sky,0,0,0,w,false);for(const yy of [-310,0,310])put(new THREE.BoxGeometry(560,22,30),frame,0,yy,8,w,false);for(const xx of [-270,0,270])put(new THREE.BoxGeometry(22,640,30),frame,xx,0,8,w,false);
    const beam=put(new THREE.PlaneGeometry(520,1600),sun,0,-560,500,w,false);beam.rotation.x=-1.0;}
  const jarCols=['#d6301e','#3f9a35','#f7c948','#2f7fd8','#f4efe4','#c98b4e','#7a2a12'],J=[],q=new THREE.Quaternion(),m4=new THREE.Matrix4(),v=new THREE.Vector3(),sc=new THREE.Vector3(),cc=new THREE.Color();
  for(let s=0;s<14;s++){const a=s/14*Math.PI*2+.45;if([0.15,1.75,3.3,4.9].some(b=>Math.abs(((a-b+Math.PI*3)%(Math.PI*2))-Math.PI)<.3))continue;for(const yy of [260,520,780]){
    const x=Math.cos(a)*(W-40),z=Math.sin(a)*(W-40),sh=put(new THREE.BoxGeometry(600,14,80),shelfM,x,yy,z,S,false);sh.lookAt(0,yy,0);
    for(let k=0;k<9;k++){const o=-260+k*65+(rnd()-.5)*12,tx=-Math.sin(a),tz=Math.cos(a),hh=50+rnd()*70,rr=18+rnd()*10;q.setFromAxisAngle(v.set(0,1,0),rnd()*6);
      m4.compose(v.set(x+tx*o-Math.cos(a)*6,yy+7+hh/2,z+tz*o-Math.sin(a)*6),q,sc.set(rr,hh,rr));J.push([m4.clone(),cc.set(jarCols[(rnd()*jarCols.length)|0]).clone()]);}}}
  const jm=new THREE.InstancedMesh(new THREE.CylinderGeometry(1,1,1,14),new THREE.MeshStandardMaterial({roughness:.25,metalness:.15}),J.length);J.forEach(([m,c],i)=>{jm.setMatrixAt(i,m);jm.setColorAt(i,c);});jm.frustumCulled=false;g.add(jm);
  const lids=new THREE.InstancedMesh(new THREE.CylinderGeometry(1.05,1.05,1,14),wm('#d8d8de',{metalness:.9,roughness:.25}),J.length);J.forEach(([m],i)=>{const e=m.elements,h=e[5];m4.copy(m);m4.elements[5]=6;m4.elements[13]=e[13]+h/2+3;lids.setMatrixAt(i,m4);});lids.frustumCulled=false;g.add(lids);
  const cop=wm('#c46a3a',{metalness:1,roughness:.28}),rail=wm('#3a3a44',{metalness:.8,roughness:.3});
  for(const a of [.95,2.55,4.1,5.65]){const x=Math.cos(a)*(W-90),z=Math.sin(a)*(W-90),pg=new THREE.Group();pg.position.set(x,1100,z);pg.lookAt(0,1100,0);S.add(pg);put(new THREE.CylinderGeometry(6,6,700,10),rail,0,0,0,pg,false).rotation.z=Math.PI/2;
    for(let k=0;k<5;k++){const xo=-280+k*140,r=60+rnd()*40;put(new THREE.CylinderGeometry(2,2,90,6),rail,xo,-45,0,pg,false);const pan=put(new THREE.CylinderGeometry(r,r*.85,r*.35,28),cop,xo,-100-r,0,pg,false);pan.rotation.x=Math.PI/2;
      put(new THREE.BoxGeometry(14,r*.9,8),rail,xo,-100-r*.1,0,pg,false);}}
  bake(S,false,true);}

function buildKitchen(R,L1,L2){
  const table=put(new THREE.PlaneGeometry(R*14,R*14),new THREE.MeshStandardMaterial({map:T2(woodTex(),R*14/500,R*14/500),roughness:.55,envMapIntensity:.5}),0,-60,0,world,false);table.rotation.x=-Math.PI/2;
  put(new THREE.CylinderGeometry(R+1700,R+1700,2200,120,1,true),new THREE.MeshStandardMaterial({map:T2(brickTex(),70,9),side:THREE.BackSide,roughness:.9}),0,1040,0,world,false);
  const ceil=put(new THREE.CircleGeometry(R+1700,80),new THREE.MeshStandardMaterial({map:T2(woodTex(),10,10),roughness:.8}),0,2140,0,world,false);ceil.rotation.x=Math.PI/2;
  const fires=[];
  for(let i=0;i<4;i++){const a=i*Math.PI/2+.4,Dd=R+1250,g=new THREE.Group();g.position.set(Math.cos(a)*Dd,-60,Math.sin(a)*Dd);g.lookAt(0,-60,0);world.add(g);
    const bm=new THREE.MeshStandardMaterial({map:T2(brickTex(),6,2),roughness:.9}),S=new THREE.Group();g.add(S);
    put(new THREE.CylinderGeometry(330,340,110,48),bm,0,55,0,S);put(new THREE.SphereGeometry(320,48,24,0,Math.PI*2,0,Math.PI/2),bm,0,110,0,S);
    put(new THREE.CylinderGeometry(55,60,520,24),bm,0,420,-190,S);put(new THREE.CircleGeometry(120,36,0,Math.PI),wm('#120806'),0,110,321,S);
    put(new THREE.TorusGeometry(126,13,12,36,Math.PI),wm('#5c2a17',{roughness:.8}),0,110,318,S);bake(S,false);
    const fm=new THREE.MeshStandardMaterial({color:'#ff7a22',emissive:'#ff6a1a',emissiveIntensity:2});fires.push(fm);
    put(new THREE.CircleGeometry(92,36,0,Math.PI),fm,0,110,323,g,false);put(new THREE.CircleGeometry(48,24,0,Math.PI),new THREE.MeshBasicMaterial({color:'#ffd36b',toneMapped:false}),0,110,324,g,false);}
  animators.push(t=>{fires.forEach((f,i)=>f.emissiveIntensity=2+Math.sin(t*9+i*2)*.4+Math.random()*.2);});
  {const K=new THREE.Group();world.add(K);const at=(a,d,y)=>[Math.cos(a)*d,y,Math.sin(a)*d];
    const wood=wm('#c08a52',{roughness:.6}),dark=wm('#6b3f22',{roughness:.6}),can=wm('#c8321e',{metalness:.6,roughness:.3}),tin=wm('#cfd2d6',{metalness:.95,roughness:.25}),box=wm('#e8d6b0',{roughness:.8}),boxT=wm('#b8311c',{roughness:.7}),flour=wm('#f3ecdd',{roughness:.95}),cheese=wm('#f7c948',{roughness:.5});
    /* rolling pin */{const g=new THREE.Group();g.position.set(...at(1.2,R+420,-60+38));g.rotation.y=-1.2;K.add(g);put(new THREE.CylinderGeometry(36,36,520,40),wood,0,0,0,g).rotation.z=Math.PI/2;for(const sd of [-1,1])put(new THREE.CylinderGeometry(14,14,160,20),dark,sd*330,0,0,g).rotation.z=Math.PI/2;}
    /* tomato cans */for(let i=0;i<5;i++){const a=2.6+i*.05,d=R+380+(i%2)*90,y=i<3?0:120;const c=put(new THREE.CylinderGeometry(55,55,120,36),can,...at(a,d,-60+60+y),K);put(new THREE.CylinderGeometry(56,56,10,36),tin,c.position.x,c.position.y+64,c.position.z,K);put(new THREE.CylinderGeometry(56,56,10,36),tin,c.position.x,c.position.y-64,c.position.z,K);}
    /* pizza box tower */for(let i=0;i<7;i++){const b=put(new THREE.BoxGeometry(260,26,260),box,...at(4.1,R+460,-60+13+i*27),K);b.rotation.y=i*.07;const l=put(new THREE.BoxGeometry(150,1,60),boxT,b.position.x,b.position.y+13.6,b.position.z,K);l.rotation.y=b.rotation.y;}
    /* flour sack */{const s=put(new THREE.SphereGeometry(150,32,20),flour,...at(5.3,R+430,-60+110),K);s.scale.set(1,1.3,.8);put(new THREE.CylinderGeometry(40,90,70,24),flour,s.position.x,s.position.y+190,s.position.z,K);}
    /* cheese wedge */{const sh=new THREE.Shape();sh.moveTo(0,0);sh.lineTo(300,0);sh.lineTo(0,140);sh.closePath();const w=put(new THREE.ExtrudeGeometry(sh,{depth:180,bevelEnabled:true,bevelSize:6,bevelThickness:6,bevelSegments:2}),cheese,...at(.2,R+400,-60),K);w.rotation.y=-.2;
      for(let i=0;i<6;i++)put(new THREE.SphereGeometry(10+rnd()*14,14,10),wm('#d9a62a',{roughness:.6}),w.position.x+30+rnd()*150,w.position.y+20+rnd()*60,w.position.z+20+rnd()*120,K);}
    /* olive oil bottle */{const o=put(new THREE.CylinderGeometry(60,70,320,32),new THREE.MeshPhysicalMaterial({color:'#7c8a1e',roughness:.1,transmission:.0,clearcoat:1,transparent:true,opacity:.85}),...at(3.3,R+400,-60+160),K);put(new THREE.CylinderGeometry(22,30,90,20),new THREE.MeshPhysicalMaterial({color:'#7c8a1e',roughness:.1,clearcoat:1,transparent:true,opacity:.85}),o.position.x,o.position.y+200,o.position.z,K);put(new THREE.CylinderGeometry(24,24,30,20),wm('#2a2a2a'),o.position.x,o.position.y+255,o.position.z,K);}
    K.traverse(o=>{if(o.isMesh){o.castShadow=false;o.receiveShadow=true;}});bake(K,false);}
  for(let i=0;i<7;i++){const a=i/7*Math.PI*2,Dd=R*.55,g=new THREE.Group();g.position.set(Math.cos(a)*Dd,0,Math.sin(a)*Dd);world.add(g);
    put(new THREE.CylinderGeometry(1.5,1.5,900,6),wm('#222222'),0,1690,0,g,false);
    put(new THREE.ConeGeometry(70,60,32,1,true),wm('#b8311c',{roughness:.35,metalness:.3,side:THREE.DoubleSide}),0,1215,0,g,false);
    put(new THREE.SphereGeometry(20,20,14),new THREE.MeshBasicMaterial({color:'#fff2c8',toneMapped:false}),0,1190,0,g,false);}
  const AT=(a,r)=>[Math.cos(a)*r,Math.sin(a)*r];
  function tomato(a,r,s){const [x,y]=AT(a,r),g=new THREE.Group();g.position.set(x,-60,y);g.scale.setScalar(s);world.add(g);
    put(new THREE.SphereGeometry(80,48,32),new THREE.MeshStandardMaterial({color:'#d9301c',roughness:.2}),0,68,0,g).scale.y=.85;
    for(let i=0;i<6;i++){const l=put(new THREE.ConeGeometry(10,44,6),wm('#3f8a35',{roughness:.5}),Math.cos(i)*18,132,Math.sin(i)*18,g);l.rotation.set(Math.sin(i)*1.3,0,-Math.cos(i)*1.3);}
    put(new THREE.CylinderGeometry(4,6,22,8),wm('#2d6b27'),0,142,0,g);bake(g);}
  kitchenDressing(R);tomato(.9,R+300,1.6);tomato(1.15,R+520,1.2);tomato(4.1,R+260,1.4);
  (function(){const [x,y]=AT(2.2,R+380);const sh=new THREE.Shape();sh.moveTo(0,0);sh.lineTo(420,0);sh.lineTo(0,210);sh.closePath();
    const w=put(new THREE.ExtrudeGeometry(sh,{depth:250,bevelEnabled:true,bevelSize:8,bevelThickness:8,bevelSegments:3}),wm('#f5c443',{roughness:.4}),x,-60,y);w.rotation.y=1.2;
    for(let i=0;i<10;i++){const h=put(new THREE.SphereGeometry(14+rnd()*18,18,12),wm('#d9a12c',{roughness:.5}),0,0,0,w);h.position.set(40+rnd()*200,14+rnd()*80,rnd()<.5?-4:258);}})();
  (function(){const [x,y]=AT(3.1,R+330),g=new THREE.Group();g.position.set(x,-14,y);g.rotation.y=.6;world.add(g);
    const b=put(new THREE.CylinderGeometry(46,46,640,48),wm('#e3c08f',{roughness:.5}),0,0,0,g);b.rotation.z=Math.PI/2;
    for(const s of [-1,1]){const h=put(new THREE.CylinderGeometry(18,22,140,24),wm('#b07a46',{roughness:.45}),s*390,0,0,g);h.rotation.z=Math.PI/2;}bake(g);})();
  function boxStack(a,r,n,rot){const [x,y]=AT(a,r),lid=new THREE.MeshStandardMaterial({map:T2(TX.lid),roughness:.8}),side=new THREE.MeshStandardMaterial({map:T2(TX.side),roughness:.85}),bot=wm('#cdbb94');
    for(let i=0;i<n;i++){const b=new THREE.Mesh(new THREE.BoxGeometry(340,36,340),[side,side,lid,bot,side,side]);b.position.set(x,-42+i*37,y);b.rotation.y=rot+(rnd()-.5)*.25;b.receiveShadow=true;world.add(b);}}
  boxStack(5.3,R+320,6,.3);boxStack(5.65,R+700,3,1.1);
  function shroom(a,r,s){const [x,y]=AT(a,r),g=new THREE.Group();g.position.set(x,-60,y);g.scale.setScalar(s);world.add(g);
    put(new THREE.CylinderGeometry(30,38,110,28),wm('#f1e6d0',{roughness:.65}),0,55,0,g);put(new THREE.SphereGeometry(90,40,20,0,Math.PI*2,0,Math.PI/2),wm('#9c7650',{roughness:.55}),0,100,0,g).scale.y=.65;bake(g);}
  shroom(2.7,R+260,1.3);shroom(2.85,R+520,.9);
  const cut=new THREE.Group();cut.position.set(L1[0],0,L1[1]);cut.rotation.y=rnd()*6;world.add(cut);const wheel=new THREE.Group();wheel.position.y=78;cut.add(wheel);
  put(new THREE.CylinderGeometry(76,76,4,96),wm('#e6eaee',{metalness:1,roughness:.12}),0,0,0,wheel).rotation.x=Math.PI/2;
  put(new THREE.CylinderGeometry(15,15,14,32),wm('#8c8f93',{metalness:.9,roughness:.25}),0,0,0,wheel).rotation.x=Math.PI/2;
  put(new THREE.BoxGeometry(8,52,18),wm('#8c8f93',{metalness:.8,roughness:.3}),0,100,0,cut);
  put(new THREE.CylinderGeometry(11,13,150,28),new THREE.MeshStandardMaterial({color:'#d6402a',roughness:.3}),0,190,0,cut);
  put(new THREE.SphereGeometry(13,24,16),new THREE.MeshStandardMaterial({color:'#d6402a',roughness:.3}),0,266,0,cut);
  animators.push((t,dt)=>{wheel.rotation.z+=dt*.6;});
  if(L2){const ol=put(new THREE.TorusGeometry(40,18,24,48),wm('#2a2230',{roughness:.15,metalness:.15}),L2[0],58,L2[1]);animators.push((t,dt)=>{ol.rotation.y+=dt*.4;});}
}
function buildBay(R,L1,L2){
  const wn=T2(waterNormal(),90,90,true);
  const water=put(new THREE.PlaneGeometry(40000,40000),new THREE.MeshStandardMaterial({color:'#157f9b',roughness:.06,metalness:.25,normalMap:wn,normalScale:new THREE.Vector2(.55,.55),envMapIntensity:1.3}),0,-14,0,world,false);water.rotation.x=-Math.PI/2;{const L=VARLOOK[CURID];if(L&&L.water)water.material.color.set(L.water);}
  animators.push((t,dt)=>{wn.offset.x+=dt*.01;wn.offset.y+=dt*.006;});
  const sandM=new THREE.MeshStandardMaterial({map:T2(sandTex(),6,6),roughness:.9}),trunkM=wm('#8a6a44',{roughness:.8}),leafM=wm('#2f8a35',{roughness:.5,side:THREE.DoubleSide});
  const leafG=new THREE.SphereGeometry(1,12,6),trunkG=new THREE.CylinderGeometry(4,4.6,1,10),nutG=new THREE.SphereGeometry(5,10,8),nutM=wm('#5a3a1e');
  function palm(parent,x,y0,z,h,lean){const g=new THREE.Group();g.position.set(x,y0,z);g.rotation.y=rnd()*6;parent.add(g);let px=0,py=0;const seg=8;
    for(let i=0;i<seg;i++){const ny=py+h/seg,nx=px+lean*(i/seg)*h/seg;const m=limb(trunkG,trunkM,[px,py,0],[nx,ny,0],g);m.scale.x=m.scale.z=1-i*.06;px=nx;py=ny;}
    for(let i=0;i<8;i++){const a=i/8*Math.PI*2,l=new THREE.Mesh(leafG,leafM);l.scale.set(38,1.5,7);l.position.set(px+Math.cos(a)*30,py-6,Math.sin(a)*30);l.rotation.set(0,-a,-.35);g.add(l);}
    P3(nutG,nutM,px+3,py-5,2,g);}
  const islandTrees=[];for(let i=0;i<9;i++){const a=i/9*Math.PI*2+rnd()*.3,Dd=R+500+rnd()*1400,x=Math.cos(a)*Dd,z=Math.sin(a)*Dd,rad=180+rnd()*220,g=new THREE.Group();g.position.set(x,-14,z);world.add(g);
    put(new THREE.SphereGeometry(rad,40,16),sandM,0,-rad*.82,0,g);const n=2+Math.floor(rnd()*3);for(let k=0;k<n;k++)palm(g,(rnd()-.5)*rad*.7,rad*.12,(rnd()-.5)*rad*.7,160+rnd()*120,(rnd()-.5)*.8);bake(g);
    for(let k=0;k<3;k++){const tx=x+(rnd()-.5)*rad*.9,tz=z+(rnd()-.5)*rad*.9;if(Math.hypot(tx-x,tz-z)<rad*.5)islandTrees.push([rnd()<.6?'tree_round1':'tree_round2',tx,tz,4.5+rnd()*3,rnd()*6.28,-14+rad*.18-3]);}}
  forest(islandTrees,0,0);
  if(VAR===0||VAR===2){const a=.9+Math.PI*.95,Dd=R+1500,cx=Math.cos(a)*Dd,cz=Math.sin(a)*Dd,G=propGeos('waterfall'),wg=new THREE.Group();wg.position.set(cx,-30,cz);wg.rotation.y=-a-Math.PI/2;wg.scale.setScalar(64);wg.userData.noLift=true;world.add(wg);
    Object.keys(G).forEach(k=>{const m=new THREE.Mesh(G[k],new THREE.MeshStandardMaterial({map:propTex('tex_'+k),roughness:.92,envMapIntensity:.35}));m.receiveShadow=false;wg.add(m);});
    const rb=propGeos('riverbed').cobble,rm=new THREE.MeshStandardMaterial({map:propTex('tex_riverbed'),roughness:.8,envMapIntensity:.5});for(let i=0;i<5;i++){const m=new THREE.Mesh(rb,rm);const t=(i-2)*330;m.position.set(cx+Math.cos(a+Math.PI/2)*t*.3-Math.cos(a)*(600+i*60),-22,cz+Math.sin(a+Math.PI/2)*t*.3-Math.sin(a)*(600+i*60));m.scale.set(45,30,45);m.rotation.y=rnd()*6;m.userData.noLift=true;world.add(m);}
    const mist=new THREE.Mesh(new THREE.PlaneGeometry(900,420),new THREE.MeshBasicMaterial({map:T2(TX.glow),color:'#ffffff',transparent:true,opacity:.28,depthWrite:false}));mist.position.set(cx-Math.cos(a)*420,90,cz-Math.sin(a)*420);mist.lookAt(0,90,0);world.add(mist);animators.push(t=>{mist.material.opacity=.22+.08*Math.sin(t*1.7);});}
  if(VAR===0){const a=.9,Dd=R+3000,cx=Math.cos(a)*Dd,cz=Math.sin(a)*Dd;const land=put(new THREE.CylinderGeometry(1,1,1,64),sandM,cx,-26,cz,world,false);land.scale.set(1500,24,1050);land.rotation.y=-a;
    const city=new THREE.Mesh(propGeos('city').city,new THREE.MeshStandardMaterial({vertexColors:true,roughness:.6,metalness:.1,envMapIntensity:.8}));city.position.set(cx,-14,cz);city.rotation.y=-a+Math.PI/2;city.scale.setScalar(1.05);city.userData.noLift=true;world.add(city);
    forest(ring(26,0,1,()=>0).map((_,i)=>{const t=rnd()*6.283,r=1100+rnd()*260;return ['tree_round'+(1+(i%2)),cx+Math.cos(t)*r,cz+Math.sin(t)*r*.7,5+rnd()*3];}),-14,0);}
  const im=new THREE.InstancedMesh(new THREE.ConeGeometry(1,1,24),wm('#3d7a6a',{roughness:.9}),22),q=new THREE.Quaternion(),m4=new THREE.Matrix4();
  if(VAR===0||VAR===2){mountainRing({r0:5600,r1:10500,h:2400,cols:['#3d7a3c','#6a8f4c','#7d7468','#f4f6fa'],base:-40,seed:2,snow:.78});mountainModels(6,R+2300,R+3200,1.5,0,'#ffffff');mountainRing({r0:10700,r1:14500,h:3600,cols:['#56809a','#6a8fa8','#7f97ab','#eef4fb'],base:-40,seed:5,snow:.7});cloudRing(16,9000,1500,'#fff4ea',.92);}
  const pg=new THREE.Group();pg.position.set(L1[0],0,L1[1]);world.add(pg);
  put(new THREE.CylinderGeometry(50,56,16,40),wm('#e9d29a',{roughness:.8}),0,8,0,pg);
  put(new THREE.SphereGeometry(52,48,32),new THREE.MeshStandardMaterial({map:T2(pineTex(),3,2),roughness:.35}),0,86,0,pg).scale.set(1,1.4,1);
  for(let i=0;i<12;i++){const a=i/12*Math.PI*2,l=put(new THREE.ConeGeometry(9,80-(i%3)*12,8),wm('#3f9a35',{roughness:.45}),Math.cos(a)*12,180,Math.sin(a)*12,pg);l.rotation.set(Math.sin(a)*.55,0,-Math.cos(a)*.55);}
  bake(pg);animators.push((t,dt)=>{pg.rotation.y+=dt*.25;});
  if(L2){const ug=new THREE.Group();ug.position.set(L2[0],0,L2[1]);world.add(ug);put(new THREE.CylinderGeometry(3,3,120,10),wm('#eeeeee'),0,60,0,ug);
    put(new THREE.ConeGeometry(90,40,16,1,true),new THREE.MeshStandardMaterial({map:T2(stripeTex('#e0452c','#fff4dc',16)),roughness:.6,side:THREE.DoubleSide}),0,120,0,ug);
    put(new THREE.BoxGeometry(70,4,30),wm('#2a7fd8'),30,10,40,ug);bake(ug);}
}
function buildNight(R,L1,L2){TUNNEL=null;
  const ground=put(new THREE.PlaneGeometry(40000,40000),new THREE.MeshStandardMaterial({map:T2(slateTex(),120,120),roughness:.75}),0,-60,0,world,false);ground.rotation.x=-Math.PI/2;
  {if(sky)world.remove(sky);const sm=new THREE.MeshBasicMaterial({map:propTex('tex_space'),side:THREE.BackSide,fog:false,depthWrite:false,toneMapped:false,color:'#c9cde0'});sky=new THREE.Mesh(new THREE.SphereGeometry(9000,64,32),sm);sky.renderOrder=-1;sky.frustumCulled=false;sky.rotation.y=1.2;world.add(sky);}
  const sg=new THREE.BufferGeometry(),sp=[];for(let i=0;i<500;i++){const u=rnd(),v=rnd()*.9+.08,th=u*Math.PI*2,ph=Math.acos(1-v);sp.push(Math.cos(th)*Math.sin(ph)*8500,Math.cos(ph)*8500,Math.sin(th)*Math.sin(ph)*8500);}
  sg.setAttribute('position',new THREE.Float32BufferAttribute(sp,3));const stars=new THREE.Points(sg,new THREE.PointsMaterial({color:'#ffffff',size:2,sizeAttenuation:false,fog:false,transparent:true,opacity:.9}));stars.frustumCulled=false;world.add(stars);
  const moon=new THREE.Mesh(new THREE.SphereGeometry(300,48,24),new THREE.MeshBasicMaterial({map:moonTex(),color:'#ffffff',fog:false,toneMapped:false}));moon.lookAt(0,0,0);moon.position.copy(sunDir).multiplyScalar(8000);world.add(moon);if(VAR===1||VAR===3)moon.visible=false;if(VAR===2){moon.scale.setScalar(2.4);moon.position.copy(sunDir).multiplyScalar(7600);}if(VAR===3)stars.visible=false;
  const q=new THREE.Quaternion(),m4=new THREE.Matrix4(),e=new THREE.Euler();
  mountainRing({r0:R+900,r1:R+3400,h:900,cols:['#2a1c18','#4a2e20','#3a2c2a'],base:-60,seed:3,rough:.85});mountainRing({r0:7600,r1:12000,h:2200,cols:['#141a30','#1d2442','#2a3150','#dfe6ff'],base:-60,seed:7,snow:.86});
  const wT=T2(windowTex(),1,2),bM=new THREE.MeshStandardMaterial({color:'#1a1d2c',emissive:'#ffffff',emissiveMap:wT,emissiveIntensity:1.2,roughness:.6});
  if(VAR!==3){const sk=new THREE.InstancedMesh(propGeos('skyline').skyline,new THREE.MeshStandardMaterial({map:propTex('tex_skyline'),emissiveMap:propTex('tex_skyline_e'),emissive:'#ffffff',emissiveIntensity:1.5,roughness:.7}),7),qq=new THREE.Quaternion(),mm=new THREE.Matrix4();
    for(let i=0;i<7;i++){const a=i/7*Math.PI*2+.35,Dd=6200+rnd()*900;qq.setFromEuler(new THREE.Euler(0,-a-Math.PI/2+(rnd()-.5)*.4,0));mm.compose(new THREE.Vector3(Math.cos(a)*Dd,-60,Math.sin(a)*Dd),qq,new THREE.Vector3(.85,.75+rnd()*.35,.85));sk.setMatrixAt(i,mm);}
    sk.frustumCulled=false;sk.userData.noLift=true;world.add(sk);}
  TUNNEL=(VAR===0||VAR===2)?placeTunnel(420):null;
  if(VAR!==3){const signs=[['CRUST RUSH','RACE NIGHT','#1a1030','#ffe36b','#ff4fa8'],['HOT SLICES','OPEN 24/7','#0f1a33','#ffffff','#2fd0ff'],['EXTRA CHEESE','NOW 2 FOR 1','#2a0f12','#ffd36b','#ff7a2a'],['PEPPERONI','PALACE','#10241a','#eaffd6','#62ff8a'],['DOUGH BROS','HAND TOSSED','#221030','#fff0f6','#c86bff'],['OVEN 9','WOOD FIRED','#2a1608','#ffe3b0','#ffb02a']];
    for(let i=0;i<9;i++){const a=i/9*Math.PI*2+.15,Dd=R+260+rnd()*380,x=Math.cos(a)*Dd,z=Math.sin(a)*Dd,sg=signs[i%signs.length],g=new THREE.Group();g.position.set(x,-60,z);g.lookAt(0,-60,0);world.add(g);
      const pole=wm('#2a2a33',{metalness:.7,roughness:.4});put(new THREE.CylinderGeometry(4,5,170,10),pole,-60,85,-6,g,false);put(new THREE.CylinderGeometry(4,5,170,10),pole,60,85,-6,g,false);
      put(new THREE.BoxGeometry(250,128,6),wm('#15161c',{metalness:.5,roughness:.5}),0,220,-4,g,false);
      const bd=put(new THREE.PlaneGeometry(240,120),new THREE.MeshBasicMaterial({map:signTex([sg[0],sg[1]],sg[2],sg[3],sg[4]),toneMapped:false}),0,220,0,g,false);
      const gl=put(new THREE.PlaneGeometry(420,260),new THREE.MeshBasicMaterial({map:T2(TX.glow),color:sg[4],transparent:true,opacity:.35,depthWrite:false,blending:THREE.AdditiveBlending,toneMapped:false}),0,220,-8,g,false);gl.renderOrder=2;}}
  if(VAR===0){const beamM=new THREE.MeshBasicMaterial({color:'#bcd6ff',transparent:true,opacity:.08,depthWrite:false,blending:THREE.AdditiveBlending,side:THREE.DoubleSide,fog:false});const bg=new THREE.ConeGeometry(160,4200,24,1,true);bg.translate(0,-2100,0);bg.rotateX(Math.PI);
    const beams=[];for(let i=0;i<4;i++){const a=i/4*Math.PI*2+.7,b=new THREE.Mesh(bg,beamM);b.position.set(Math.cos(a)*5600,-40,Math.sin(a)*5600);b.userData.ph=rnd()*6;world.add(b);beams.push(b);}
    animators.push(t=>{beams.forEach((b,i)=>{b.rotation.set(.45+Math.sin(t*.31+b.userData.ph)*.25,0,Math.sin(t*.23+i)*.5);});});}
  if(VAR!==3){const n=40,pos=new Float32Array(n*3),pts=[];for(let i=0;i<n;i++)pts.push({r:2600+rnd()*3200,h:500+rnd()*900,w:(rnd()<.5?-1:1)*(.012+rnd()*.03),a:rnd()*6.28});
    const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.BufferAttribute(pos,3));const pm=new THREE.PointsMaterial({color:'#ff5a4a',size:5,sizeAttenuation:false,fog:false,transparent:true,opacity:.95});const P=new THREE.Points(g,pm);P.frustumCulled=false;world.add(P);
    animators.push((t,dt)=>{for(let i=0;i<n;i++){const o=pts[i];o.a+=o.w*dt;pos[i*3]=Math.cos(o.a)*o.r;pos[i*3+1]=o.h;pos[i*3+2]=Math.sin(o.a)*o.r;}g.attributes.position.needsUpdate=true;pm.opacity=.55+.4*(Math.sin(t*6)>0?1:0);});}
  const bim=new THREE.InstancedMesh(new THREE.BoxGeometry(1,1,1),bM,18);for(let i=0;i<18;i++){const a=i/18*Math.PI*2+.2,Dd=4300+rnd()*800,h=300+rnd()*700,w=160+rnd()*200;q.setFromEuler(e.set(0,-a,0));m4.compose(new THREE.Vector3(Math.cos(a)*Dd,h/2-60,Math.sin(a)*Dd),q,new THREE.Vector3(w,h,w));bim.setMatrixAt(i,m4);}bim.frustumCulled=false;world.add(bim);
  if(VAR===3)bim.visible=false;const lamps=[];for(let j=0;j<N;j+=15){const side=(Math.floor(j/15)%2)?1:-1,p=track[j],lo=p.wall===side?CURB+26:CURB+16,x=p.x+p.nx*lo*side,y=p.y+p.ny*lo*side;if(nearTrack(x,y,CURB+8))continue;lamps.push({p,side,x,y});}
  const LN=Math.max(1,lamps.length);
  const poleI=new THREE.InstancedMesh(new THREE.CylinderGeometry(.8,1.1,30,10),wm('#3a3a44',{metalness:.7,roughness:.35}),LN),
    headI=new THREE.InstancedMesh(new THREE.BoxGeometry(10,1.6,3.4),wm('#2a2a33',{metalness:.6,roughness:.4}),LN),
    bulbI=new THREE.InstancedMesh(new THREE.BoxGeometry(7,.6,2.4),new THREE.MeshBasicMaterial({color:'#fff1c4',toneMapped:false}),LN),
    glowI=new THREE.InstancedMesh(new THREE.PlaneGeometry(1,1),new THREE.MeshBasicMaterial({map:T2(TX.glow),color:'#ffcf7a',transparent:true,opacity:.55,depthWrite:false,blending:THREE.AdditiveBlending,toneMapped:false}),LN);
  [poleI,headI,bulbI,glowI].forEach(m=>m.count=lamps.length);
  const one=new THREE.Vector3(1,1,1);
  lamps.forEach((l,i)=>{const ang=Math.atan2(-l.p.ny*l.side,-l.p.nx*l.side);q.identity();const lg=groundAt(l.x,l.y);m4.compose(new THREE.Vector3(l.x,15+lg,l.y),q,one);poleI.setMatrixAt(i,m4);
    q.setFromEuler(e.set(0,-ang,0));const hx=l.x-l.p.nx*l.side*4,hy=l.y-l.p.ny*l.side*4;m4.compose(new THREE.Vector3(hx,30+lg,hy),q,one);headI.setMatrixAt(i,m4);m4.compose(new THREE.Vector3(hx,29.1+lg,hy),q,one);bulbI.setMatrixAt(i,m4);
    q.setFromEuler(e.set(-Math.PI/2,0,0));{const gx=l.p.x+l.p.nx*l.side*(RW-8),gz=l.p.y+l.p.ny*l.side*(RW-8);m4.compose(new THREE.Vector3(gx,.4+groundAt(gx,gz),gz),q,new THREE.Vector3(115,115,1));}glowI.setMatrixAt(i,m4);});
  [poleI,headI,bulbI,glowI].forEach(m=>{m.frustumCulled=false;world.add(m);});poleI.castShadow=headI.castShadow=true;
  const dots=[];for(let j=0;j<N;j+=3)for(const s of [-1,1]){const p=track[j];dots.push([p.x+p.nx*(CURB+2)*s,p.y+p.ny*(CURB+2)*s]);}
  const dotM=new THREE.MeshBasicMaterial({color:'#7fd0ff',toneMapped:false}),dI=new THREE.InstancedMesh(new THREE.SphereGeometry(.7,8,6),dotM,dots.length);
  dots.forEach(([x,y],i)=>{m4.makeTranslation(x,1.2+groundAt(x,y),y);dI.setMatrixAt(i,m4);});dI.frustumCulled=false;world.add(dI);
  animators.push(t=>{dotM.color.setHSL(.55+Math.sin(t*.5)*.05,1,.7);});
  const cg=new THREE.Group();cg.position.set(L1[0],0,L1[1]);world.add(cg);put(new THREE.CylinderGeometry(60,70,18,40),wm('#2a2a33',{metalness:.5,roughness:.4}),0,9,0,cg);
  const red=new THREE.MeshStandardMaterial({color:'#e0261a',roughness:.15});
  const curve=new THREE.CatmullRomCurve3([new THREE.Vector3(-60,40,0),new THREE.Vector3(-30,95,0),new THREE.Vector3(20,120,0),new THREE.Vector3(60,90,0),new THREE.Vector3(75,40,0)]);
  put(new THREE.TubeGeometry(curve,64,22,24,false),red,0,0,0,cg);put(new THREE.SphereGeometry(22,24,16),red,-60,40,0,cg);
  put(new THREE.ConeGeometry(22,40,24),red,80,24,0,cg).rotation.z=Math.PI+.3;put(new THREE.CylinderGeometry(6,8,30,12),wm('#3f9a35'),-72,58,0,cg).rotation.z=.7;
  bake(cg);animators.push((t,dt)=>{cg.rotation.y+=dt*.3;});
  if(L2){const tg=new THREE.Group();tg.position.set(L2[0],0,L2[1]);world.add(tg);for(let i=0;i<8;i++){const d=put(new THREE.CylinderGeometry(30,30,6,40),pepMat,(rnd()-.5)*8,4+i*7,(rnd()-.5)*8,tg);d.rotation.y=rnd()*6;}bake(tg);}
}

/* ================= GAME STATE ================= */
let karts=[],player=null,camT=null,projectiles=[],hazards=[],state='menu',cd=0,raceTime=0,finishCount=0,lastCd=0,resultsAt=0,lapShown=1,camSnap=true,acc=0,alpha=1;
let selected=(+(store.get('crust-driver')||0)||0)%8,mapIdx=(+(store.get('crust-map')||0)||0)%MAPS.length,clsKey=store.get('crust-cls')||'medium',mode=store.get('crust-mode')||'gp',cupIdx=(+(store.get('crust-cup')||0)||0)%CUPS.length,gp=null,raceDone=false;if(!CLASSES[clsKey])clsKey='medium';if(mode!=='gp'&&mode!=='single')mode='gp';
const aiKey=()=>CLASSES[clsKey].ai;
const cam={a:0,look:new THREE.Vector3(),base:new THREE.Vector3(),roll:0,gp:0,gr:0,sx:0,oy:0,vy:0,pvz:0,pspd:0,F:new THREE.Vector3(),U:new THREE.Vector3(),P:new THREE.Vector3()};
function makeKart(ri,slot,isPlayer,diff,build){
  const back=4+Math.floor(slot/2)*3,idx=(N-back)%N,p=track[idx],lat=slot%2?19:-19;
  const sk=diff.skill[0]+Math.random()*(diff.skill[1]-diff.skill[0]);
  const spec={ri,b:build.b,w:build.w,g:build.g,p:build.p,t:build.t||'',hq:slot===4?1:0},m=getModel(spec);m.ga=0;m.gl.visible=false;
  const k={r:RACERS[ri],ri,m,spec,col:PAINTS[build.p]||RACERS[ri].color,sm:statMods(build),glide:false,gRings:0,x:p.x+p.nx*lat,y:p.y+p.ny*lat,a:p.ang,ma:p.ang,speed:0,steer:0,drift:0,charge:0,boost:0,spin:0,inv:0,z:0,zv:0,pen:1,brake:0,acc:0,sf:2,
    gripT:0,item:null,item2:null,pend:[],roll:0,shield:0,rush:0,frozen:0,idx,prog:idx-N,finished:false,finishTime:0,place:0,isPlayer,auto:!isPlayer,wrongT:0,fx:0,air:false,onRamp:false,trick:false,trickT:0,pd:false,
    ai:{lane:lat,laneTarget:lat,laneT:1+Math.random()*3,skill:sk,itemDelay:0,inBend:false}};
  k.wy=k.lastG=groundAt(k.x,k.y);k.pwy=k.wy;k.wvy=0;k.gRate=0;k.loop=null;k.loopTh=0;k.pth=0;k.px=k.x;k.py=k.y;k.pa=k.a;k.pma=k.ma;k.pz=0;k.rx=k.x;k.ry=k.y;k.rz=k.wy;k.rg=k.wy;k.rma=k.ma;return k;
}
function resetRace(demo){
  const diff=DIFFS[demo?'normal':aiKey()];
  const others=RACERS.map((_,i)=>i).filter(i=>demo||i!==selected);
  for(let i=others.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[others[i],others[j]]=[others[j],others[i]];}
  karts=[];for(let s=0;s<8;s++){if(!demo&&s===4)karts.push(makeKart(selected,s,true,diff,playerBuild));else{const ri=others.shift();karts.push(makeKart(ri,s,false,diff,cpuBuilds[ri]));}}
  const keep=new Set(karts.map(k=>k.m));modelCache.forEach(m=>{m.g.visible=keep.has(m);});pruneModels(keep);
  player=demo?null:karts[4];camT=karts[4];
  for(const k of karts){if(k.cutM)k.cutM.forEach(m=>scene.remove(m));}if(typeof sauceFx==='function'&&_sauceEl)sauceFx(false);projectiles.forEach(p=>scene.remove(p.mesh));hazards.forEach(h=>scene.remove(h.mesh));projectiles=[];hazards=[];
  boxes.forEach(b=>b.r=0);resetHazards();raceTime=0;finishCount=0;lapShown=1;resultsAt=0;cam.a=camT.ma;camSnap=true;acc=0;camera.up.set(0,1,0);standCache=standings();
  warmScene();
}
/* upload every texture and buffer and compile every shader before the lights go green, so nothing hitches the first time it scrolls into view */
let _warmG=null;
function warmScene(){try{if(!_warmG){_warmG=new THREE.Group();for(const k of Object.keys(ITEM_BUILD)){try{_warmG.add(itemProto(k).clone());}catch(e){}}}
  scene.add(_warmG);const saved=[];scene.traverse(o=>{saved.push(o,o.visible,o.frustumCulled);o.visible=true;o.frustumCulled=false;});
  renderer.compile(scene,camera);const sm=renderer.shadowMap.autoUpdate;renderer.shadowMap.needsUpdate=true;
  const rt=_warmRT||(_warmRT=new THREE.WebGLRenderTarget(64,64));renderer.setRenderTarget(rt);renderer.render(scene,camera);renderer.setRenderTarget(null);
  for(let i=0;i<saved.length;i+=3){saved[i].visible=saved[i+1];saved[i].frustumCulled=saved[i+2];}scene.remove(_warmG);renderer.shadowMap.needsUpdate=true;}catch(e){console.warn('warm',e);}}
let _warmRT=null;
let standCache=[];
function standings(){return karts.slice().sort((a,b)=>a.finished&&b.finished?a.place-b.place:a.finished?-1:b.finished?1:b.prog-a.prog);}
const ROLL=[{pepperoni:25,oil:22,trio:10,garlic:12,dough:8,flour:15,chili:8},
  {pepperoni:14,oil:10,trio:14,garlic:10,dough:14,flour:12,chili:16,freezer:4,wheel:3,rush:3},
  {chili:22,dough:12,trio:12,flour:8,garlic:8,rush:14,wheel:12,freezer:12}];
function rollItem(pos){const f=pos/7,t=ROLL[f<.2?0:f<.62?1:2];let sum=0;for(const k in t)sum+=t[k];let r=Math.random()*sum;for(const k in t){r-=t[k];if(r<=0)return k;}return 'chili';}

/* ---------- input ---------- */
const keys={left:false,right:false,drift:false,brake:false};let itemQueued=null;
const KEYMAP={ArrowLeft:'left',KeyA:'left',ArrowRight:'right',KeyD:'right',ArrowDown:'brake',KeyS:'brake',Space:'brake',ShiftLeft:'brake',ShiftRight:'brake'};
addEventListener('keydown',e=>{if(e.target.closest&&e.target.closest('.overlay'))return;const k=KEYMAP[e.code];
  if(k){keys[k]=true;e.preventDefault();}
  else if(e.code==='KeyX'||e.code==='KeyE'||e.code==='Enter'){if(!e.repeat)itemQueued='fwd';e.preventDefault();}
  else if(e.code==='KeyZ'||e.code==='KeyQ'){if(!e.repeat)itemQueued='fwd2';e.preventDefault();}
  else if(e.code==='KeyV'){if(!e.repeat)itemQueued='fwd2';e.preventDefault();}
  else if(e.code==='KeyP'||e.code==='Escape'){togglePause();}});
addEventListener('keyup',e=>{const k=KEYMAP[e.code];if(k)keys[k]=false;});
addEventListener('blur',()=>{keys.left=keys.right=keys.brake=false;if(window.__clearInput)window.__clearInput();});
(function(){const zone=document.getElementById('tzone'),zl=zone.children[0],zr=zone.children[1],act=new Map();
  function upd(){let l=0,r=0;for(const s of act.values()){if(s==='l')l++;else r++;}keys.left=l>0;keys.right=r>0;zl.classList.toggle('on',l>0);zr.classList.toggle('on',r>0);}
  const side=e=>e.clientX<window.innerWidth/2?'l':'r';
  zone.addEventListener('pointerdown',e=>{if(e.pointerType==='touch')return;e.preventDefault();try{zone.setPointerCapture(e.pointerId);}catch(_){}act.set(e.pointerId,side(e));upd();});
  zone.addEventListener('pointermove',e=>{if(e.pointerType==='touch')return;if(act.has(e.pointerId)){act.set(e.pointerId,side(e));upd();}});
  const end=e=>{if(e.pointerType==='touch')return;act.delete(e.pointerId);upd();};zone.addEventListener('pointerup',end);zone.addEventListener('pointercancel',end);zone.addEventListener('lostpointercapture',end);
  const brakes=new Set(),bEls=[document.getElementById('brakeL'),document.getElementById('brakeR')];
  for(const b of bEls){b.addEventListener('pointerdown',e=>{if(e.pointerType==='touch'){e.preventDefault();return;}e.preventDefault();e.stopPropagation();try{b.setPointerCapture(e.pointerId);}catch(_){}brakes.add(e.pointerId);keys.brake=true;b.classList.add('on');});
    const up=e=>{if(e.pointerType==='touch')return;brakes.delete(e.pointerId);keys.brake=brakes.size>0;b.classList.remove('on');};b.addEventListener('pointerup',up);b.addEventListener('pointercancel',up);b.addEventListener('lostpointercapture',up);}
  for(const [bid,sl] of [['itemBtn',''],['itemBtn2','2']]){const ib=document.getElementById(bid);let sy=0,down=false;
  ib.addEventListener('pointerdown',e=>{e.preventDefault();e.stopPropagation();try{ib.setPointerCapture(e.pointerId);}catch(_){}sy=e.clientY;down=true;ib.classList.add('fwd');});
  ib.addEventListener('pointermove',e=>{if(!down)return;const dy=e.clientY-sy;ib.classList.toggle('back',dy>26);ib.classList.toggle('fwd',dy<=26);});
  ib.addEventListener('pointerup',e=>{if(!down)return;down=false;itemQueued='fwd'+sl;ib.classList.remove('fwd','back');});
  ib.addEventListener('pointercancel',()=>{down=false;ib.classList.remove('fwd','back');});}
  /* touch: every touch event rebuilds steering and braking from e.touches, the browser's list of fingers actually on the screen */
  const steerT=new Set(),brakeT=new Map(),itemT=new Set();
  function fromTouches(list){const live=new Set();for(const t of list)live.add(t.identifier);
    for(const id of [...steerT])if(!live.has(id))steerT.delete(id);for(const id of [...brakeT.keys()])if(!live.has(id))brakeT.delete(id);for(const id of [...itemT])if(!live.has(id))itemT.delete(id);
    let l=0,r=0;for(const t of list)if(steerT.has(t.identifier)){if(t.clientX<window.innerWidth/2)l++;else r++;}
    tl=l;tr=r;keys.left=l>0||ml;keys.right=r>0||mr;zl.classList.toggle('on',keys.left);zr.classList.toggle('on',keys.right);
    const bOn=new Set(brakeT.values());bEls.forEach(b=>b.classList.toggle('on',bOn.has(b)));keys.brake=brakeT.size>0||brakes.size>0;}
  let tl=0,tr=0,ml=false,mr=false;
  const onTouch=e=>{if(e.type==='touchstart'){for(const t of e.changedTouches){const el=t.target&&t.target.closest?t.target:null;if(!el||el.closest('.overlay'))continue;
      const bb=el.closest('#brakeL,#brakeR');if(bb){brakeT.set(t.identifier,bb);continue;}if(el.closest('#itemBtn,#itemBtn2')){itemT.add(t.identifier);continue;}if(el.closest('#pauseBtn')||el.closest('#abilBtn'))continue;if(el.closest('#tzone'))steerT.add(t.identifier);}}
    const had=steerT.size||brakeT.size||itemT.size;fromTouches(e.touches);if((had||steerT.size||brakeT.size||itemT.size)&&e.cancelable&&state!=='menu')e.preventDefault();};
  /* no iOS magnifier, text selection, callout or pinch-zoom during play */
  const inGame=e=>e.target&&e.target.closest&&e.target.closest('#stage');
  for(const ev of ['selectstart','contextmenu','gesturestart','gesturechange','dblclick'])document.addEventListener(ev,e=>{if(inGame(e)||ev.startsWith('gesture'))e.preventDefault();},{passive:false});
  for(const ev of ['touchstart','touchmove','touchend','touchcancel'])document.addEventListener(ev,onTouch,{passive:false,capture:true});
  window.__clearInput=()=>{steerT.clear();brakeT.clear();act.clear();brakes.clear();fromTouches([]);upd();keys.left=keys.right=keys.brake=false;bEls.forEach(b=>b.classList.remove('on'));zl.classList.remove('on');zr.classList.remove('on');};
  document.addEventListener('visibilitychange',()=>{if(document.hidden)window.__clearInput();});
  document.querySelectorAll('#stage button,.tz').forEach(b=>b.addEventListener('contextmenu',e=>e.preventDefault()));})();
function playerInput(){const it=itemQueued;itemQueued=null;if(it&&it.endsWith('2')&&player&&player.item2&&!(player.roll>0)){const t=player.item;player.item=player.item2;player.item2=t;}return {steer:(keys.right?1:0)-(keys.left?1:0),brake:keys.brake,mul:1,use:!!it,back:!!it&&it.startsWith('back')};}

/* ---------- audio ---------- */
let ac=null,master=null,eng=null,eng2=null,engGain=null,muted=store.get('crust-muted')==='1';
/* phones suspend or interrupt audio (calls, other apps, lock screen); any touch brings it back */
['pointerdown','pointerup','touchend','click','keydown'].forEach(ev=>document.addEventListener(ev,()=>{if(!ac&&booted&&ev!=='pointerdown')initAudio();if(ac&&(ac.state==='suspended'||ac.state==='interrupted'))ac.resume().catch(()=>{});},{passive:true,capture:true}));
document.addEventListener('visibilitychange',()=>{if(!document.hidden&&ac&&ac.state!=='running')ac.resume().catch(()=>{});});
function initAudio(){if(ac)return;try{if(navigator.audioSession)navigator.audioSession.type='playback';}catch(e){}/* game sound plays like media, even with the ringer switch on silent */try{ac=new (window.AudioContext||window.webkitAudioContext)();
  /* bus: everything -> gentle compressor -> speakers, with a small room reverb send so effects sound full instead of dry beeps */
  const comp=ac.createDynamicsCompressor();comp.threshold.value=-12;comp.knee.value=6;comp.ratio.value=12;comp.attack.value=.002;comp.release.value=.14;comp.connect(ac.destination);
  const trim=ac.createGain();trim.gain.value=.8;trim.connect(comp);master=ac.createGain();master.gain.value=CFG.vol/100;master.connect(trim);
  const len=Math.floor(ac.sampleRate*1.3),ir=ac.createBuffer(2,len,ac.sampleRate);for(let c=0;c<2;c++){const d=ir.getChannelData(c);for(let i=0;i<len;i++){const t=i/len;d[i]=(Math.random()*2-1)*Math.pow(1-t,3.2)*(i<ac.sampleRate*.012?i/(ac.sampleRate*.012):1);}}
  const conv=ac.createConvolver();conv.buffer=ir;revBus=ac.createGain();revBus.gain.value=.22;const rhp=ac.createBiquadFilter();rhp.type='highpass';rhp.frequency.value=260;revBus.connect(rhp);rhp.connect(conv);conv.connect(master);
  /* engine: a harmonic-rich firing pulse (not a smooth drone), chopped by the cylinder beat and band-limited so it reads as a little kart motor */
  const H=28,re=new Float32Array(H+1),im=new Float32Array(H+1);for(let n=1;n<=H;n++){im[n]=(n%2?1:.6)*Math.pow(n,-.95)*(n===1?.55:n===3?1.25:1);re[n]=(n%4===2?.25:0)/n;}const wave=ac.createPeriodicWave(re,im);
  eng=ac.createOscillator();eng.setPeriodicWave(wave);eng2=ac.createOscillator();eng2.setPeriodicWave(wave);eng2.detune.value=-11;
  const am=ac.createGain();am.gain.value=.68;engAM=ac.createOscillator();engAM.type='triangle';const amd=ac.createGain();amd.gain.value=.32;engAM.connect(amd);amd.connect(am.gain);
  const hp=ac.createBiquadFilter();hp.type='highpass';hp.frequency.value=90;hp.Q.value=.6;engLP=ac.createBiquadFilter();engLP.type='lowpass';engLP.frequency.value=1100;engLP.Q.value=.8;
  const pk=ac.createBiquadFilter();pk.type='peaking';pk.frequency.value=1500;pk.Q.value=1.1;pk.gain.value=4;engGain=ac.createGain();engGain.gain.value=0;const g2=ac.createGain();g2.gain.value=.45;
  eng.connect(am);eng2.connect(g2);g2.connect(am);am.connect(hp);hp.connect(pk);pk.connect(engLP);engLP.connect(engGain);engGain.connect(master);eng.start();eng2.start();engAM.start();engSub=null;engIn=hp;initSfx();}catch(e){ac=null;}}
let noiseBuf=null,skidGain=null,skidFilt=null,revBus=null,engLP=null,engSub=null,driftT=0,engAM=null,engIn=null,engNG=null,voices=0;
/* never more than a couple of dozen effect voices at once: piles of overlapping sounds are what made the audio crackle */
function vOK(d,delay){if(voices>=22)return false;voices++;setTimeout(()=>{voices--;},((d||.3)+(delay||0))*1000+140);return true;}
function initSfx(){try{const n=ac.sampleRate*2;noiseBuf=ac.createBuffer(1,n,ac.sampleRate);const d=noiseBuf.getChannelData(0);
  /* pink-ish noise: warmer than white, so whooshes and impacts don't hiss */
  let b0=0,b1=0,b2=0;for(let i=0;i<n;i++){const w=Math.random()*2-1;b0=.99765*b0+w*.099046;b1=.963*b1+w*.2965164;b2=.57*b2+w*1.0526913;d[i]=(b0+b1+b2+w*.1848)*.22;}
  /* drift: a soft rubbery hiss with a slow chatter, low-passed so it never turns shrill */
  const src=ac.createBufferSource();src.buffer=noiseBuf;src.loop=true;skidFilt=ac.createBiquadFilter();skidFilt.type='bandpass';skidFilt.frequency.value=900;skidFilt.Q.value=.7;
  const lp=ac.createBiquadFilter();lp.type='lowpass';lp.frequency.value=2200;skidGain=ac.createGain();skidGain.gain.value=0;const am=ac.createGain();am.gain.value=.75;const lfo=ac.createOscillator();lfo.frequency.value=11;const lg=ac.createGain();lg.gain.value=.25;lfo.connect(lg);lg.connect(am.gain);lfo.start();
  src.connect(skidFilt);skidFilt.connect(lp);lp.connect(am);am.connect(skidGain);skidGain.connect(master);src.start();
  if(engIn){const ns=ac.createBufferSource();ns.buffer=noiseBuf;ns.loop=true;const bp=ac.createBiquadFilter();bp.type='bandpass';bp.frequency.value=2400;bp.Q.value=.9;engNG=ac.createGain();engNG.gain.value=.12;ns.connect(bp);bp.connect(engNG);engNG.connect(engIn);ns.start();}}catch(e){}}
/* one voice = two slightly detuned oscillators through a lowpass that rounds off the edges, with a soft attack */
function tone(f,d,type,v,f2,delay,rev){if(!ac||muted||v<=.001)return;if(!vOK(d,delay))return;const t=ac.currentTime+(delay||0),g=ac.createGain(),lp=ac.createBiquadFilter();lp.type='lowpass';lp.frequency.setValueAtTime(Math.min(16000,f*(type==='sine'?20:5)),t);lp.Q.value=.5;
  for(const dt of [-6,6]){const o=ac.createOscillator();o.type=type||'sine';o.detune.value=dt;o.frequency.setValueAtTime(f,t);if(f2)o.frequency.exponentialRampToValueAtTime(f2,t+d*.9);o.connect(lp);o.start(t);o.stop(t+d+.08);}
  g.gain.setValueAtTime(.0001,t);g.gain.exponentialRampToValueAtTime(v*.6,t+.008);g.gain.setTargetAtTime(.0001,t+.02,d/4);lp.connect(g);g.connect(master);if(revBus&&rev!==0){const s=ac.createGain();s.gain.value=rev||.6;g.connect(s);s.connect(revBus);}}
function noise(d,v,type,f1,f2,delay,q,rev){if(!ac||muted||!noiseBuf||v<=.001)return;if(!vOK(d,delay))return;const t=ac.currentTime+(delay||0),s=ac.createBufferSource(),fl=ac.createBiquadFilter(),g=ac.createGain();s.buffer=noiseBuf;fl.type=type||'lowpass';fl.Q.value=q||1;
  fl.frequency.setValueAtTime(f1,t);if(f2)fl.frequency.exponentialRampToValueAtTime(f2,t+d);g.gain.setValueAtTime(.0001,t);g.gain.exponentialRampToValueAtTime(v*1.6,t+.006);g.gain.exponentialRampToValueAtTime(.0001,t+d);s.connect(fl);fl.connect(g);g.connect(master);
  if(revBus&&rev!==0){const r=ac.createGain();r.gain.value=rev||.5;g.connect(r);r.connect(revBus);}s.start(t,Math.random()*1.2);s.stop(t+d+.05);}
/* a pitched thump with a fast downward sweep: the body of every impact */
function thump(f,d,v,delay){if(!ac||muted||v<=.001)return;if(!vOK(d,delay))return;const t=ac.currentTime+(delay||0),o=ac.createOscillator(),g=ac.createGain();o.type='sine';o.frequency.setValueAtTime(f,t);o.frequency.exponentialRampToValueAtTime(Math.max(30,f*.35),t+d);
  g.gain.setValueAtTime(.0001,t);g.gain.exponentialRampToValueAtTime(v,t+.004);g.gain.exponentialRampToValueAtTime(.0001,t+d);o.connect(g);g.connect(master);o.start(t);o.stop(t+d+.05);}
/* bell: inharmonic partials for sparkly pickups and rings */
function bell(f,d,v,delay){[[1,1],[2.76,.45],[5.4,.22],[8.9,.1]].forEach(([m,a])=>tone(f*m,d*(1.1-a*.3),'sine',v*a,0,delay,.8));}
function near(k){if(k===camT)return 1;const d=Math.hypot(k.x-camera.position.x,k.y-camera.position.z);return Math.max(0,1-d/380)*.6;}
const SFX={
  hop(){noise(.07,.035,'bandpass',1800,900,0,1.2,0);thump(220,.07,.05);},
  tier(n){bell(660+n*200,.35,.045);noise(.18,.025,'highpass',5000,9000,0,1,.4);},
  boost(n){noise(.9,.16,'bandpass',220,2600,0,1.1,.6);noise(.5,.07,'lowpass',400,120,0,1,0);tone(110,.7,'sawtooth',.035,330+(n||1)*60,0,.3);bell(880,.25,.025,.04);},
  pad(){noise(.6,.12,'bandpass',400,3400,0,1.3,.6);tone(260,.4,'triangle',.04,1040,0,.5);},
  pickup(){[784,988,1175,1568].forEach((f,i)=>bell(f,.5,.04,i*.045));noise(.35,.04,'highpass',4000,9000,.05,1,.6);},
  ready(){bell(1047,.3,.035);bell(1568,.4,.035,.08);},
  tick(){tone(1700+Math.random()*300,.03,'triangle',.012,0,0,0);},
  throwF(){noise(.32,.11,'bandpass',600,2600,0,1.6,.3);thump(180,.08,.05);},
  throwB(){noise(.32,.11,'bandpass',2400,500,0,1.6,.3);thump(140,.08,.05);},
  chili(){SFX.boost(2);noise(.5,.08,'lowpass',900,200,.05,1,.2);},
  hit(v,kind){thump(150,.45,.22*v);noise(.6,.22*v,'lowpass',3200,140,0,1,.5);noise(.12,.1*v,'highpass',2500,6000,0,1,.3);
    if(kind==='oil'){noise(.5,.08*v,'bandpass',600,200,.05,3,.4);}for(let i=0;i<4;i++)tone(780-i*120,.12,'triangle',.022*v,520-i*90,.2+i*.08,.6);},
  land(v){thump(110,.22,.2*v);noise(.22,.12*v,'lowpass',900,90,0,1,.2);},
  bump(v){thump(140,.14,.12*v);noise(.12,.12*v,'lowpass',1400,120,0,1,.2);noise(.05,.05*v,'highpass',3000,6000,0,1,0);},
  trick(){noise(.36,.08,'bandpass',500,3000,0,1.5,.4);bell(988,.3,.035,.1);},
  lap(final){[0,4,7,12].forEach((st,i)=>bell(523*Math.pow(2,st/12)*(final?1.5:1),.45,.045,i*.1));},
  count(go){if(go){[523,659,784,1047].forEach((f,i)=>tone(f,.6,'triangle',.05,0,i*.015,.7));thump(90,.3,.12);}else{tone(440,.28,'triangle',.06,0,0,.6);thump(80,.15,.06);}},
  garlic(v){[523,659,784,1047].forEach((f,i)=>bell(f*1.5,.5,.03*v,i*.05));noise(.6,.04*v,'highpass',3000,7000,0,1,.6);},
  freeze(){noise(.8,.1,'highpass',3000,9000,0,1,.8);[2093,1760,1568,1319].forEach((f,i)=>bell(f,.45,.03,i*.06));},
  wheel(v){tone(130,1.3,'sawtooth',.03*v,390,0,.4);noise(1.1,.07*v,'bandpass',700,2400,0,3,.4);},
  boom(v){if(v<=0)return;thump(90,.7,.3*v);noise(1.1,.3*v,'lowpass',2200,80,0,1,.7);noise(.15,.1*v,'highpass',2000,5000,0,1,.4);},
  clash(v){if(v<=0)return;thump(260,.18,.12*v);noise(.25,.14*v,'bandpass',2600,700,0,1.4,.5);bell(1319,.25,.03*v,.02);},
  glide(){noise(1.1,.12,'bandpass',260,1600,0,1,.6);tone(392,.6,'triangle',.035,784,0,.7);tone(587,.6,'triangle',.03,1175,.12,.7);},
  ring(){[1047,1319,1568].forEach((f,i)=>bell(f,.35,.035,i*.05));},
  finish(){[523,659,784,1047,1319].forEach((f,i)=>bell(f,.8,.05,i*.13));noise(1.4,.05,'highpass',4000,8000,.5,1,.8);}
};
function beep(f,d,type,v){tone(f,d||.12,type==='square'?'triangle':(type||'triangle'),(v||.05)*1.2,0,0,.3);}

/* ---------- simulation ---------- */
function sparkWall(k,nx,ny){const x=k.x+nx*9,y=k.y+ny*9,gy=(k.wy||0)+3;for(let i=0;i<10;i++)FXA.spawn(x,gy,y,(Math.random()-.5)*40-nx*30,10+Math.random()*25,(Math.random()-.5)*40-ny*30,i%2?'#ffd36b':'#ffffff',1.6,.3,.3,60,1);}
/* the road is drawn as flat quads between sample points; on dips that surface sits above the smooth height
   function, which made karts sink. This returns the height of the surface you actually see. */
const ROAD_M=()=>Math.max(1,Math.round(2*RW/9));
function surfH(x,z,j0){let j=-1,t=0;for(let d=0;d<=8&&j<0;d++)for(const sg of d?[1,-1]:[1]){const jj=(((j0+d*sg)%N)+N)%N,p=track[jj],q=track[(jj+1)%N],sx=q.x-p.x,sz=q.y-p.y,L2=sx*sx+sz*sz||1,tt=((x-p.x)*sx+(z-p.y)*sz)/L2;if(tt>=-.001&&tt<=1.001){j=jj;t=clamp(tt,0,1);break;}}
  if(j<0||(GLIDE&&j>=GLIDE.j0-1&&j<GLIDE.j1+1))return groundAt(x,z);const p=track[j],q=track[(j+1)%N],nx=p.nx+(q.nx-p.nx)*t,ny=p.ny+(q.ny-p.ny)*t,cx=p.x+(q.x-p.x)*t,cz=p.y+(q.y-p.y)*t,l=(x-cx)*nx+(z-cz)*ny,la=Math.abs(l);
  if(la>RW)return groundAt(x,z)+(la<CURB?kerbH(la):0);const M=ROAD_M(),u=(l+RW)/(2*RW)*M,mi=Math.min(M-1,Math.max(0,Math.floor(u))),fm=u-mi,o0=-RW+2*RW*mi/M,o1=-RW+2*RW*(mi+1)/M,h=(pt,o)=>groundAt(pt.x+pt.nx*o,pt.y+pt.ny*o);
  return (1-t)*((1-fm)*h(p,o0)+fm*h(p,o1))+t*((1-fm)*h(q,o0)+fm*h(q,o1))+.06;}
const KERB_H=.45;function kerbH(la){const u=la-RW;return u<.6?KERB_H*u/.6:u<6.5?KERB_H*(1-.25*(u-.6)/5.9):KERB_H*.75+(.05-KERB_H*.75)*(u-6.5)/(CURB-RW-6.5);}
function lateral(k){const p=track[k.idx];return (k.x-p.x)*p.nx+(k.y-p.y)*p.ny;}
function aiInput(k,dt){
  const ai=k.ai,diff=DIFFS[player?aiKey():'normal'];ai.laneT-=dt;if(ai.laneT<=0){ai.laneT=1.5+Math.random()*3;ai.laneTarget=(Math.random()*2-1)*36;}
  let avoid=false;for(const o of obstacles){let dj=o.j-k.idx;if(dj<0)dj+=N;if(dj>1&&dj<28&&Math.abs(ai.lane-o.lat)<o.r+15){ai.laneTarget=clamp(o.lat>0?o.lat-o.r-22:o.lat+o.r+22,-42,42);ai.laneT=Math.max(ai.laneT,1.2);avoid=true;}}
  for(const c of HAZ.traffic){if(c.hide)continue;let dj=c.i-k.idx;if(dj<0)dj+=N;if(dj>1&&dj<24&&Math.abs(ai.lane-c.lat)<28){ai.laneTarget=clamp(c.lat>0?c.lat-32:c.lat+32,-44,44);ai.laneT=Math.max(ai.laneT,1);avoid=true;}}
  for(const w of HAZ.walk){let dj=w.j-k.idx;if(dj<0)dj+=N;if(dj>1&&dj<14&&Math.abs(ai.lane-w.lat)<20&&Math.random()<.6){ai.laneTarget=clamp(w.lat>0?w.lat-26:w.lat+26,-44,44);avoid=true;}}
  for(const LOOP of LOOPS){let dl=LOOP.j-k.idx;if(dl<0)dl+=N;if(dl>1&&dl<70){ai.laneTarget=LOOP.lat0;avoid=true;}}
  if(GLIDE){let dg=GLIDE.rj-k.idx;if(dg<0)dg+=N;if(dg>0&&dg<60){ai.laneTarget=clamp(ai.laneTarget,-28,28);avoid=true;}}
  ai.lane+=(ai.laneTarget-ai.lane)*Math.min(1,dt*(avoid?2.8:.8));
  const tp=track[(k.idx+9+Math.floor(Math.max(0,k.speed)/32))%N];
  let des=Math.atan2(tp.y+tp.ny*ai.lane-k.y,tp.x+tp.nx*ai.lane-k.x);
  if(k.sc){const P=k.sc.pts,q=P[Math.min(k.sc.n-1,k.scI+4)];des=Math.atan2(q.y-k.y,q.x-k.x);}
  else for(const sc of SHORTS){let dj=k.idx-sc.a;if(dj>N/2)dj-=N;if(dj<-N/2)dj+=N;
    if(dj>-62&&dj<-48&&ai.scSeen!==sc){ai.scSeen=sc;ai.pick=Math.random()<({easy:.25,normal:.5,hard:.8}[player?aiKey():'normal']||.5)?sc:null;}
    if(ai.pick===sc){if(dj>-16&&dj<6){const q=sc.pts[2];des=Math.atan2(q.y-k.y,q.x-k.x);}else if(dj>=-40&&dj<=-16){ai.lane+=(sc.s*48-ai.lane)*Math.min(1,dt*2);}else if(dj>=6)ai.pick=null;}}
  const steer=clamp(angDiff(des,k.a)*2.6+(k.sauceT>0?Math.sin(simTime*5+k.ri)*.55:0),-1,1);
  const bend=Math.abs(angDiff(track[(k.idx+18)%N].ang,track[k.idx].ang));
  let mul=k.isPlayer?.97:ai.skill;
  if(player&&!k.isPlayer&&state==='race'){const d=k.prog-player.prog;mul*=d>30?diff.ahead:d<-30?diff.behind:1;}
  mul*=1-Math.min(.3,Math.max(0,(bend-.6)*diff.corner));
  const inBend=bend>.9;if(ai.inBend&&!inBend&&Math.random()<diff.boost)k.boost=Math.max(k.boost,.55);ai.inBend=inBend;
  let use=false,back=false;
  if(k.item){ai.itemDelay-=dt;if(ai.itemDelay<=0){use=true;const st=standCache,i=st.indexOf(k),ah=st[i-1],bh=st[i+1];
    const aClose=!!ah&&(ah.prog-k.prog)<14,bClose=!!bh&&(k.prog-bh.prog)<12;
    const it=k.item;if(it==='oil'||it==='flour')back=!(aClose&&Math.random()<.35);else if(it==='pepperoni'||it==='trio'||it==='dough')back=bClose&&!aClose;
    if((it==='garlic')&&!bClose&&!aClose&&Math.random()<.5){use=false;ai.itemDelay=.6;}
    if(k.item==='pepperoni'&&!aClose&&!bClose&&Math.random()<.6){use=false;ai.itemDelay=.5;}}}
  return {steer,drift:false,brake:false,mul,use,back};
}
function land(k){if(k===camT)shake(.55);const tr=k.trick;k.trick=false;if(tr){k.boost=Math.max(k.boost,.8);if(k===player)SFX.boost(1);}else SFX.land(near(k));
  for(let i=0;i<10;i++){const a=Math.random()*Math.PI*2;FXN.spawn(k.x+Math.cos(a)*4,1,k.y+Math.sin(a)*4,Math.cos(a)*18,4+Math.random()*6,Math.sin(a)*18,'#f2e3c4',3,9,.7,-1,2);}}
const rings=[];
function initRings(){const g=new THREE.RingGeometry(.82,1,56);for(let i=0;i<12;i++){const m=new THREE.Mesh(g,new THREE.MeshBasicMaterial({color:'#ffffff',transparent:true,opacity:0,depthWrite:false,blending:THREE.AdditiveBlending,side:THREE.DoubleSide,toneMapped:false}));m.visible=false;m.rotation.x=-Math.PI/2;scene.add(m);rings.push({m,t:0,life:1,size:1,flat:true});}}
let ringI=0;function spawnRing(x,y,z,col,size,life,flat){const r=rings[ringI++%rings.length];r.m.material.color.set(col);r.m.position.set(x,y,z);r.t=0;r.life=life;r.size=size;r.flat=flat!==false;r.m.visible=true;r.m.rotation.set(r.flat?-Math.PI/2:0,0,0);}
function updRings(dt){for(const r of rings){if(!r.m.visible)continue;r.t+=dt;const f=r.t/r.life;if(f>=1){r.m.visible=false;continue;}const e=1-Math.pow(1-f,3);r.m.scale.setScalar(.5+r.size*e);r.m.material.opacity=(1-f)*.9;if(!r.flat)r.m.lookAt(camera.position);}}
const HITC={flour:['#ffffff','#f6f1e6','#e9dfc8'],wheel:['#ff3b1a','#ffe066','#ffffff'],garlic:['#7fe07a','#f4ecdc','#ffffff'],pep:['#ff3b1a','#b8311c','#ffe066','#fff4dc'],dough:['#fff4dc','#f3dfb4','#ffe066'],oil:['#ffd24a','#e0b22a','#fff2b0'],meat:['#7a4528','#ff9a1f','#fff4dc'],lob:['#ffd24a','#e0b22a','#fff2b0']};
function loopStep(k,dt){const L=k.loop;k.speed=Math.max(k.speed,BASE_MAX*1.18);L.th+=k.speed*dt/LOOPR;const th=Math.min(L.th,Math.PI*2),p=L.p,sx=LOOPR*Math.sin(th),hg=LOOPR*(1-Math.cos(th)),lat=L.lat0+L.shift*th/(Math.PI*2);
  k.x=p.x+p.tx*sx+p.nx*lat;k.y=p.y+p.ty*sx+p.ny*lat;k.wy=L.g0+hg+.35;k.z=hg;k.loopTh=th;k.a=k.ma=p.ang;k.drift=0;k.steer*=.9;k.air=false;
  if(L.th>=Math.PI*2){k.loop=null;k.loopTh=0;k.pth=0;k.boost=Math.max(k.boost,1.5);k.wvy=0;k.gRate=0;k.lastG=groundAt(k.x,k.y);k.wy=k.lastG;k.z=0;if(k===camT)shake(.5);if(k===player)SFX.boost(3);}}

/* shields: one or two garlic layers that stay until something hits you; each layer stops one item or special */
function addShield(k,n){k.shL=Math.min(2,(k.shL||0)+n);const gy=(k.wy||0)+7;spawnRing(k.x,(k.wy||0)+.6,k.y,'#7fe07a',44,.6);burst(k.x,gy,k.y,24,['#7fe07a','#f4ecdc','#ffffff'],60,2.4);
  if(k===player){showBanner(k.shL>1?'Double shield':'Shield up',1.1);SFX.garlic(1);}else if(near(k)>0)SFX.garlic(near(k));}
function absorb(k){if(!(k.shL>0))return false;k.shL--;k.absT=.6;k.inv=Math.max(k.inv||0,.6);const gy=(k.wy||0)+7;
  burst(k.x,gy,k.y,40,['#7fe07a','#f4ecdc','#ffffff'],110,3.2);spawnRing(k.x,gy,k.y,'#c8ffc0',60,.5);if(k===camT)shake(.35);
  if(k===player){showBanner(k.shL>0?'Shield blocked! 1 left':'Shield blocked!',1.2);SFX.garlic(1);}else if(near(k)>0)SFX.garlic(near(k));return true;}
function spinOut(k,kind,world){if(k.inv>0||k.shield>0||k.rush>0||k.ghostT>0||k.absT>0)return;if(!world&&absorb(k))return;if(k===camT)shake(1.1);k.spin=1.1*(1.25-.25*k.sm.wgt);k.inv=1.9;k.speed*=.3;k.drift=0;k.charge=0;k.boost=0;if(!k.air&&!k.loop){k.air=true;k.big=false;k.airT=0;k.wvy=(k.gRate||0)+40;}
  const cols=HITC[kind]||['#fff4dc','#ffe066','#ff3b1a'],y=6*KS;burst(k.x,y,k.y,34,cols,70,3.4);
  for(let i=0;i<12;i++){const a=i/12*Math.PI*2;FXA.spawn(k.x,y,k.y,Math.cos(a)*90,8,Math.sin(a)*90,'#ffffff',2.4,.3,.35,0,4);}
  for(let i=0;i<8;i++){const a=Math.random()*Math.PI*2;FXN.spawn(k.x+Math.cos(a)*3,2,k.y+Math.sin(a)*3,Math.cos(a)*14,6+Math.random()*8,Math.sin(a)*14,kind==='dough'?'#fff4dc':'#d8d0c4',4,14,.9,-2,1.5);}
  FXA.spawn(k.x,y,k.y,0,0,0,'#ffffff',30,6,.18,0,0);
  spawnRing(k.x,.6,k.y,cols[0],34,.55);spawnRing(k.x,y,k.y,'#ffffff',20,.35,false);
  SFX.hit(near(k),kind);if(k===player){hitfx.classList.add('on');setTimeout(()=>hitfx.classList.remove('on'),70);}}
function boxFx(b,k){const cols=['#ffe066','#e0452c','#fff4dc','#7fd0ff','#3f9a35'];burst(b.x,7,b.y,40,cols,85,2.6);
  for(let i=0;i<16;i++){const a=Math.random()*Math.PI*2,u=.4+Math.random()*.6;FXA.spawn(b.x,7,b.y,Math.cos(a)*50*u,40+Math.random()*50,Math.sin(a)*50*u,i%2?'#f5ead2':'#d6402a',3,1.5,.9,90,.6);}
  FXA.spawn(b.x,7,b.y,0,0,0,'#fff6c8',40,8,.22,0,0);spawnRing(b.x,.5,b.y,'#ffd24a',26,.5);spawnRing(b.x,7,b.y,'#ffffff',14,.3,false);
  if(k===player)SFX.pickup();else{const v=near(k);if(v>0)tone(1319,.1,'triangle',.04*v);}}
const projGeo={flour:new THREE.SphereGeometry(3.2,18,14),wheel:new THREE.CylinderGeometry(7,7,1.4,40),pep:new THREE.CylinderGeometry(2.8,2.8,.7,36),dough:new THREE.SphereGeometry(2.6,28,20),oil:new THREE.CircleGeometry(9,40),lob:new THREE.SphereGeometry(2.2,20,14)};
const projMat={flour:new THREE.MeshStandardMaterial({color:'#f6f1e6',roughness:.85}),wheel:new THREE.MeshStandardMaterial({color:'#e6eaee',metalness:1,roughness:.12,emissive:'#ff2a1a',emissiveIntensity:.25}),dough:new THREE.MeshStandardMaterial({color:'#f3dfb4',roughness:.65}),oil:new THREE.MeshStandardMaterial({color:'#e0b22a',roughness:.04,metalness:.2,transparent:true,opacity:.9})};
/* ================= ITEM MODELS (built once, cloned per throw; shared geometry and materials) ================= */
const IMAT={},imat=(k,o)=>IMAT[k]||(IMAT[k]=new THREE.MeshPhysicalMaterial(o));
const lathe=(pts,seg)=>new THREE.LatheGeometry(pts.map(([r,y])=>new THREE.Vector2(r,y)),seg||32);
function vcol(geo,fn){const p=geo.attributes.position,c=new Float32Array(p.count*3),col=new THREE.Color();for(let i=0;i<p.count;i++){fn(p.getX(i),p.getY(i),p.getZ(i),col);c[i*3]=col.r;c[i*3+1]=col.g;c[i*3+2]=col.b;}geo.setAttribute('color',new THREE.BufferAttribute(c,3));return geo;}
function lumpy(geo,amp,f,seed){const p=geo.attributes.position,v=new THREE.Vector3();for(let i=0;i<p.count;i++){v.fromBufferAttribute(p,i);const n=Math.sin(v.x*f+seed)*Math.sin(v.y*f*1.3+seed*2.1)*Math.sin(v.z*f*.9+seed*3.3)+.5*Math.sin(v.x*f*2.3+v.z*f*1.7+seed);v.multiplyScalar(1+amp*n);p.setXYZ(i,v.x,v.y,v.z);}geo.computeVertexNormals();return geo;}
const nz3=(x,y,z)=>Math.sin(x*1.7+y*.3)*Math.sin(y*2.1+z*.7)*Math.sin(z*1.9+x*.5);
function IMesh(geo,mat,p,s,r,parent){const m=new THREE.Mesh(geo,mat);if(p)m.position.set(p[0],p[1],p[2]);if(s!=null)Array.isArray(s)?m.scale.set(s[0],s[1],s[2]):m.scale.setScalar(s);if(r)m.rotation.set(r[0],r[1],r[2]);m.castShadow=true;m.receiveShadow=true;parent.add(m);return m;}
const ITEM_BUILD={
  pep(){const G=new THREE.Group(),c1=new THREE.Color('#b3241a'),c2=new THREE.Color('#5e1009'),c3=new THREE.Color('#d0402a');
    const g=vcol(lathe([[0,.3],[1.7,.33],[2.4,.44],[2.78,.38],[2.9,.16],[2.84,-.12],[2.5,-.3],[0,-.3]],44),(x,y,z,c)=>{const r=Math.hypot(x,z),n=nz3(x*2,y,z*2);c.copy(c1).lerp(c3,.35+.35*n);if(r>2.45)c.lerp(c2,Math.min(1,(r-2.45)/.45));});
    IMesh(g,imat('pepvc',{vertexColors:true,roughness:.34,clearcoat:.8,clearcoatRoughness:.25}),null,null,null,G);
    const fat=imat('pepfat',{color:'#ec9a82',roughness:.4,clearcoat:.6}),sg=new THREE.SphereGeometry(1,10,6);
    [[.6,.5,.38],[-1,.3,.32],[.2,-1.2,.3],[1.4,-.6,.26],[-.4,1.4,.28],[-1.5,-.9,.24],[1.6,.9,.22]].forEach(([x,z,s])=>{IMesh(sg,fat,[x,.36,z],[s,.06,s*.85],[0,x*3,0],G);IMesh(sg,fat,[-z*.8,-.31,x*.8],[s*.9,.05,s*.8],null,G);});
    return G;},
  dough(){const G=new THREE.Group(),a=new THREE.Color('#ecc88a'),b=new THREE.Color('#fbf5e6'),d=new THREE.Color('#c99a58');
    const g=vcol(lumpy(new THREE.SphereGeometry(2.6,40,28),.07,2.6,1.3),(x,y,z,c)=>{const n=nz3(x*1.4,y*1.4,z*1.4),m=nz3(x*3.1+2,y*3.1,z*3.1);c.copy(a).lerp(d,Math.max(0,-n)*.6);if(m>.72)c.lerp(b,.55);});
    IMesh(g,imat('doughvc',{vertexColors:true,roughness:.78,sheen:.6,sheenRoughness:.6,sheenColor:new THREE.Color('#ffffff')}),null,null,null,G);
    const k=imat('doughknot',{color:'#e8c07c',roughness:.75});IMesh(new THREE.TorusGeometry(.7,.32,10,20),k,[0,2.45,0],null,[Math.PI/2,0,0],G);return G;},
  oil(){const G=new THREE.Group(),sh=new THREE.Shape(),N=48;for(let i=0;i<=N;i++){const a=i/N*Math.PI*2,r=9*(1+.16*Math.sin(3*a+.4)+.09*Math.sin(7*a+1.2)+.05*Math.sin(13*a));const x=Math.cos(a)*r,y=Math.sin(a)*r;i?sh.lineTo(x,y):sh.moveTo(x,y);}
    const pm={roughness:.03,metalness:.15,clearcoat:1,clearcoatRoughness:.02,transparent:true,envMapIntensity:1.7,polygonOffset:true,polygonOffsetFactor:-2,polygonOffsetUnits:-2};
    const base=IMesh(new THREE.ShapeGeometry(sh,4),imat('oilA',Object.assign({color:'#c8901a',opacity:.93},pm)),null,null,[-Math.PI/2,0,0],G);base.castShadow=false;
    const hi=IMesh(new THREE.ShapeGeometry(sh,4),imat('oilB',Object.assign({color:'#f4d464',opacity:.55,emissive:'#6b4a08',emissiveIntensity:.25},pm)),[1.2,.04,-.8],[.55,.55,1],[-Math.PI/2,0,.4],G);hi.castShadow=false;
    const bub=imat('oilbub',{color:'#ffe9a0',roughness:.02,clearcoat:1,transparent:true,opacity:.7}),hs=new THREE.SphereGeometry(1,14,8,0,Math.PI*2,0,Math.PI/2);
    [[3,2,.5],[-4,-2.5,.38],[-1.5,4,.3],[5,-3,.28],[-5.5,1.5,.42]].forEach(([x,z,s])=>IMesh(hs,bub,[x,.02,z],s,null,G).castShadow=false);
    const ol=imat('olive',{color:'#4c6a24',roughness:.25,clearcoat:.8}),pim=imat('pim',{color:'#d6301e',roughness:.4});
    for(const [x,z,r] of [[-2.6,-4.4,.6],[3.8,3.2,2.2]]){IMesh(new THREE.SphereGeometry(1,16,12),ol,[x,.75,z],[1.25,.8,.9],[0,r,0],G);IMesh(new THREE.CylinderGeometry(.35,.35,.3,12),pim,[x+Math.cos(r)*1.2,.75,z-Math.sin(r)*1.2],null,[0,r,Math.PI/2],G);}
    return G;},
  lob(){const G=new THREE.Group(),B=new THREE.Group();B.position.y=-2.4;G.add(B);
    IMesh(lathe([[0,.25],[.95,.25],[1.05,.4],[1.05,2.9],[.9,3.4],[.42,4.0],[.36,4.7],[.42,4.8],[0,4.8]],28),imat('bottle',{color:'#3d7a2e',roughness:.05,metalness:0,clearcoat:1,transparent:true,opacity:.55,envMapIntensity:1.6}),null,null,null,B);
    IMesh(lathe([[0,.32],[.88,.32],[.95,.45],[.95,2.4],[0,2.4]],24),imat('oilin',{color:'#d9a21c',roughness:.2,emissive:'#5a3a04',emissiveIntensity:.35}),null,null,null,B);
    IMesh(new THREE.CylinderGeometry(.34,.3,.7,14),imat('cork',{color:'#b98a5c',roughness:.85}),[0,5.05,0],null,null,B);
    IMesh(new THREE.CylinderGeometry(1.08,1.08,1.3,28,1,true),imat('label',{color:'#f3e6c6',roughness:.6,side:THREE.DoubleSide}),[0,1.8,0],null,null,B);
    IMesh(new THREE.CylinderGeometry(1.09,1.09,.22,28,1,true),imat('labelb',{color:'#2f6a2a',roughness:.5,side:THREE.DoubleSide}),[0,2.25,0],null,null,B);
    IMesh(new THREE.SphereGeometry(.32,12,8),imat('oliveL',{color:'#4c6a24',roughness:.25,clearcoat:.8}),[0,1.75,1.08],[1,.75,.4],null,B);return G;},
  flour(){const G=new THREE.Group(),S=new THREE.Group();S.position.y=-2.8;G.add(S);const a=new THREE.Color('#f2e9d6'),b=new THREE.Color('#d9ccb0');
    const g=vcol(lumpy(lathe([[0,0],[2.5,0],[3.05,.55],[3.2,2.1],[2.95,3.3],[1.7,4.25],[.95,4.6],[1.05,5.0],[1.4,5.55],[0,5.7]],36),.05,2.2,.7),(x,y,z,c)=>{c.copy(a).lerp(b,.5+.5*nz3(x*4,y*4,z*4));});
    IMesh(g,imat('sack',{vertexColors:true,roughness:.95,sheen:.8,sheenRoughness:.8,sheenColor:new THREE.Color('#ffffff')}),null,null,null,S);
    IMesh(new THREE.TorusGeometry(1.0,.16,8,24),imat('twine',{color:'#7a5230',roughness:.9}),[0,4.62,0],null,[Math.PI/2,0,0],S);
    IMesh(new THREE.CylinderGeometry(3.24,3.18,1.3,36,1,true),imat('sackband',{color:'#c8321e',roughness:.8,side:THREE.DoubleSide}),[0,2.0,0],null,null,S);
    IMesh(new THREE.CylinderGeometry(3.26,3.2,.25,36,1,true),imat('sackband2',{color:'#f7c948',roughness:.7,side:THREE.DoubleSide}),[0,2.0,0],null,null,S);
    const pf=imat('puff',{color:'#ffffff',roughness:1});[[0,6.0,0,.7],[.5,5.8,.3,.45],[-.4,5.85,-.3,.5]].forEach(([x,y,z,s])=>IMesh(new THREE.SphereGeometry(1,10,8),pf,[x,y,z],s,null,S));return G;},
  wheel(){const G=new THREE.Group(),D=new THREE.Group();D.name='disc';D.rotation.x=Math.PI/2;G.add(D);
    IMesh(lathe([[0,.2],[5.4,.2],[6.5,.09],[7.0,0],[6.5,-.09],[5.4,-.2],[0,-.2]],56),imat('blade',{color:'#e9ecef',metalness:1,roughness:.12,envMapIntensity:1.5}),null,null,null,D);
    IMesh(new THREE.TorusGeometry(6.95,.08,6,56),new THREE.MeshBasicMaterial({color:'#ff4a24',toneMapped:false}),null,null,[Math.PI/2,0,0],D).castShadow=false;
    IMesh(new THREE.CylinderGeometry(1.5,1.5,1.0,24),imat('hub',{color:'#2a2a30',metalness:.8,roughness:.35}),null,null,null,D);
    for(let i=0;i<6;i++){const a=i/6*Math.PI*2;IMesh(new THREE.CylinderGeometry(.22,.22,1.2,8),imat('bolt',{color:'#d8d8de',metalness:1,roughness:.2}),[Math.cos(a)*.95,0,Math.sin(a)*.95],null,null,D);}
    for(let i=0;i<3;i++){const a=i/3*Math.PI*2+.3;IMesh(new THREE.BoxGeometry(3.6,.42,.9),imat('hub',{}),[Math.cos(a)*3.4,0,Math.sin(a)*3.4],null,[0,-a,0],D);}
    const red=imat('guard',{color:'#d6301e',roughness:.35,clearcoat:.8});IMesh(new THREE.TorusGeometry(7.45,.5,10,40,Math.PI*.8),red,null,null,[0,0,Math.PI*.1],G);
    for(const s of [-1,1])IMesh(new THREE.BoxGeometry(1.2,6.5,.25),red,[-1.2,2.6,s*.62],null,[0,0,.5],G);
    const h=IMesh(new THREE.CylinderGeometry(.75,.9,8,16),imat('handle',{color:'#8a5a32',roughness:.55,clearcoat:.4}),[-4.6,7.6,0],null,[0,0,.62],G);
    IMesh(new THREE.SphereGeometry(.95,14,10),red,[-7.0,11.0,0],null,null,G);
    const gl=new THREE.Mesh(new THREE.CircleGeometry(9,28),new THREE.MeshBasicMaterial({map:T2(TX.glow),color:'#ff4a24',transparent:true,opacity:.5,depthWrite:false,blending:THREE.AdditiveBlending,toneMapped:false}));gl.rotation.x=-Math.PI/2;gl.position.y=-6.85;G.add(gl);
    return G;},
  clove(){const G=new THREE.Group(),m=imat('clove',{vertexColors:true,roughness:.5,clearcoat:.4}),c1=new THREE.Color('#f6efe2'),c2=new THREE.Color('#b98ab8');
    IMesh(vcol(lathe([[0,-1],[.55,-.85],[.8,-.3],[.7,.4],[.35,1.1],[.08,1.6],[0,1.65]],18),(x,y,z,c)=>{c.copy(c1).lerp(c2,Math.max(0,(y-.2)/1.6)*(.6+.4*Math.sin(Math.atan2(z,x)*5)));}),m,null,[1,1,.75],null,G);return G;},
  bulb(){const G=new THREE.Group(),m=imat('bulbvc',{vertexColors:true,roughness:.5,clearcoat:.4}),c1=new THREE.Color('#f6efe2'),c2=new THREE.Color('#c39ac4');
    const lobe=vcol(lathe([[0,-1.2],[.7,-1.0],[1.0,-.3],[.9,.5],[.45,1.25],[0,1.5]],18),(x,y,z,c)=>{c.copy(c1).lerp(c2,Math.max(0,(y+.2)/1.7)*.7*(.5+.5*Math.sin(Math.atan2(z,x)*4)));});
    for(let i=0;i<8;i++){const a=i/8*Math.PI*2;IMesh(lobe,m,[Math.cos(a)*.75,0,Math.sin(a)*.75],[1,1,.8],[Math.sin(a)*.3,-a,-Math.cos(a)*.3],G);}
    IMesh(lobe,m,[0,.15,0],[1.1,1.1,1.1],null,G);IMesh(new THREE.ConeGeometry(.35,1.4,10),imat('neck',{color:'#e7dcc6',roughness:.7}),[0,1.9,0],null,null,G);
    for(let i=0;i<7;i++){const a=i/7*Math.PI*2;IMesh(new THREE.CylinderGeometry(.05,.03,.8,4),imat('root',{color:'#a8875c',roughness:.9}),[Math.cos(a)*.35,-1.45,Math.sin(a)*.35],null,[Math.sin(a)*.6,0,-Math.cos(a)*.6],G);}return G;},
  chili(){const G=new THREE.Group(),g=lathe([[0,0],[.22,.25],[.5,.8],[.85,1.8],[1.15,2.9],[1.35,4.0],[1.38,4.6],[1.2,5.05],[0,5.15]],28),p=g.attributes.position;
    for(let i=0;i<p.count;i++){const y=p.getY(i),b=Math.max(0,3.6-y);p.setX(i,p.getX(i)+b*b*.12);}g.computeVertexNormals();
    IMesh(g,imat('chili',{color:'#d3221a',roughness:.18,clearcoat:1,clearcoatRoughness:.08}),[0,-2.5,0],null,null,G);
    const gr=imat('stem',{color:'#3b8a2c',roughness:.45});IMesh(new THREE.SphereGeometry(1,16,10),gr,[0,2.75,0],[1.25,.35,1.15],null,G);
    IMesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3([new THREE.Vector3(0,2.8,0),new THREE.Vector3(.1,3.5,0),new THREE.Vector3(.6,3.9,0)]),8,.2,8),gr,null,null,null,G);return G;},
  rush(){const G=new THREE.Group(),card=imat('card',{color:'#c9a06a',roughness:.85}),top=imat('cardtop',{color:'#e9d2a4',roughness:.8});
    IMesh(new THREE.BoxGeometry(6,1.3,6),card,[0,0,0],null,null,G);IMesh(new THREE.BoxGeometry(5.6,.06,5.6),top,[0,.68,0],null,null,G);
    IMesh(new THREE.BoxGeometry(6.04,.3,6.04),imat('cardred',{color:'#d6301e',roughness:.6}),[0,.2,0],null,null,G);
    const bolt=new THREE.Shape();bolt.moveTo(.4,2.2);bolt.lineTo(-1.2,-.2);bolt.lineTo(.1,-.2);bolt.lineTo(-.5,-2.2);bolt.lineTo(1.3,.5);bolt.lineTo(0,.5);bolt.closePath();
    IMesh(new THREE.ExtrudeGeometry(bolt,{depth:.25,bevelEnabled:true,bevelSize:.06,bevelThickness:.06,bevelSegments:1}),imat('bolty',{color:'#ffd24a',roughness:.3,emissive:'#ff9a1f',emissiveIntensity:.5}),[0,.75,0],null,[-Math.PI/2,0,.3],G);
    const fl=new THREE.MeshBasicMaterial({color:'#ff7a1a',transparent:true,opacity:.9,toneMapped:false,blending:THREE.AdditiveBlending,depthWrite:false});
    for(const z of [-1.6,1.6]){const f=IMesh(new THREE.ConeGeometry(.8,4.5,14,1,true),fl,[-5.2,0,z],null,[0,0,Math.PI/2],G);f.castShadow=false;}return G;},
  freezer(){const G=new THREE.Group(),ice=imat('icecr',{color:'#7fc8ff',roughness:.04,metalness:.1,clearcoat:1,transparent:true,opacity:.82,emissive:'#3a8adf',emissiveIntensity:.25,flatShading:true});
    [[0,.6,0,1.6,3.2,0],[1.4,.0,.5,1,2,-.6],[-1.3,.1,-.4,1.1,2.3,.6],[.4,-.2,-1.3,.9,1.7,.3],[-.5,-.3,1.2,.8,1.5,-.4]].forEach(([x,y,z,w,h,r])=>IMesh(new THREE.OctahedronGeometry(1,0),ice,[x,y,z],[w,h,w],[r,r*2,r*.5],G));
    IMesh(new THREE.IcosahedronGeometry(1.2,0),imat('icecore',{color:'#ffffff',roughness:.2,emissive:'#9fdcff',emissiveIntensity:.8,flatShading:true}),[0,.3,0],null,null,G);return G;},
  trio(){const G=new THREE.Group();for(let i=0;i<3;i++){const p=itemProto('pep').clone();p.position.set((i-1)*2.2,i*.15,(i-1)*-.6);p.rotation.set(1.1,0,(i-1)*.35);G.add(p);}return G;},
  pepperoni(){return itemProto('pep').clone();},garlic(){return itemProto('bulb').clone();},garlic2(){const G=new THREE.Group();for(const [x,z,r] of [[-1.6,0,-.25],[1.6,.4,.25]]){const b=itemProto('bulb').clone();b.position.set(x,0,z);b.rotation.y=r;b.scale.setScalar(.85);G.add(b);}return G;},
  icebox(){const G=new THREE.Group(),ice=imat('iceshell',{color:'#cdeeff',roughness:.05,metalness:.05,clearcoat:1,transparent:true,opacity:.48,depthWrite:false,emissive:'#4a9adf',emissiveIntensity:.2,flatShading:true});
    IMesh(new THREE.IcosahedronGeometry(1,1),ice,null,[6.4,3.9,4.2],null,G).castShadow=false;
    [[4.2,2.4,1.6,.42],[-3.8,2.6,-1.5,.36],[.8,3.6,2.2,.32],[-1.4,3.7,-1.9,.34]].forEach(([x,y,z,s])=>IMesh(new THREE.OctahedronGeometry(1,0),ice,[x,y,z],[s*1.3,s*2.2,s*1.3],[x*.1,0,-x*.08],G).castShadow=false);return G;}
};
const ITEM_PROTO={};function itemProto(k){if(!ITEM_PROTO[k]){const o=ITEM_BUILD[k]();o.traverse(m=>{if(m.geometry)KGSET.add(m.geometry);if(m.material)SHSET.add(m.material);});ITEM_PROTO[k]=o;}return ITEM_PROTO[k];}
/* garlic shield and rush aura: fresnel glow bubble */
function bubbleShader(c1,c2){return new THREE.ShaderMaterial({uniforms:{uC:{value:new THREE.Color(c1)},uC2:{value:new THREE.Color(c2)},uT:{value:0}},transparent:true,depthWrite:false,blending:THREE.AdditiveBlending,
  vertexShader:'varying vec3 vN;varying vec3 vV;varying vec3 vP;void main(){vec4 mv=modelViewMatrix*vec4(position,1.);vN=normalize(normalMatrix*normal);vV=normalize(-mv.xyz);vP=position;gl_Position=projectionMatrix*mv;}',
  fragmentShader:'uniform vec3 uC;uniform vec3 uC2;uniform float uT;varying vec3 vN;varying vec3 vV;varying vec3 vP;void main(){float f=pow(1.-abs(dot(normalize(vN),normalize(vV))),2.4);float b=.5+.5*sin(vP.y*1.6-uT*4.+sin(vP.x*1.1+uT*1.3)*1.4);float hx=.5+.5*sin(vP.x*3.+vP.z*3.)*sin(vP.y*3.4-uT*2.);float a=f*.95+.04+(b*.08+hx*.05)*(.3+f);gl_FragColor=vec4(mix(uC,uC2,f)*a,a);}'});}
/* render each item model once into a small transparent image for the HUD (difference matte: black and white passes) */
function renderItemIcons(){const S=256,ps=new THREE.Scene(),penv=envFrom(THEMES.kitchen.env,[[128,40,40,'#ffffff'],[384,40,40,'#ffffff'],[256,140,40,'#ff8a2a']]);ps.environment=penv;
  ps.add(new THREE.HemisphereLight('#fff6e6','#5a3a24',.55));const dl=new THREE.DirectionalLight('#ffffff',1.9);dl.position.set(6,12,9);ps.add(dl);const rl=new THREE.DirectionalLight('#9fd0ff',1.6);rl.position.set(-8,3,-6);ps.add(rl);const kl=new THREE.DirectionalLight('#fff0d6',1.1);kl.position.set(-5,9,10);ps.add(kl);const bl=new THREE.DirectionalLight('#ffb070',1.2);bl.position.set(2,-2,-10);ps.add(bl);
  const pc=new THREE.PerspectiveCamera(28,1,.1,200);const prevPR=renderer.getPixelRatio();renderer.setPixelRatio(1);renderer.setSize(S,S,false);const prevExp=renderer.toneMappingExposure;renderer.toneMappingExposure=.92;
  const view={chili:[[1,.4,.9],0,1],pepperoni:[[.4,1,.9],0,1],oil:[[0,0,0],0,1,'lob'],dough:[[0,0,0],0,1],trio:[[.2,1,.8],0,1],garlic:[[0,0,0],0,1],flour:[[0,0,0],0,1],wheel:[[0,0,0],0,1],rush:[[.9,1,.6],0,1],freezer:[[0,0,0],0,1]};
  const ca=cnv(S,S),cb=cnv(S,S),out=cnv(S,S),ga=ca.getContext('2d'),gb=cb.getContext('2d'),go=out.getContext('2d');
  for(const k of ITEM_KEYS){const src=k==='oil'?'lob':k==='pepperoni'?'pepperoni':k;const o=itemProto(src).clone();o.traverse(m=>{if(m.isMesh&&m.material&&m.material.blending===THREE.AdditiveBlending)m.visible=false;});
    if(k==='pepperoni')o.rotation.set(1.05,0,.2);if(k==='oil')o.rotation.set(0,0,-.5);if(k==='wheel')o.rotation.y=.35;if(k==='rush')o.rotation.set(.35,-.6,0);if(k==='chili')o.rotation.set(0,.4,-.5);if(k==='flour')o.rotation.y=.6;
    ps.add(o);o.updateMatrixWorld(true);const bb=new THREE.Box3().setFromObject(o),c=bb.getCenter(new THREE.Vector3()),r=bb.getSize(new THREE.Vector3()).length()*.5;
    pc.position.set(c.x+r*1.15,c.y+r*1.0,c.z+r*2.15);pc.lookAt(c);pc.updateMatrixWorld();
    ps.background=new THREE.Color('#000000');renderer.render(ps,pc);ga.clearRect(0,0,S,S);ga.drawImage(renderer.domElement,0,0,S,S);
    ps.background=new THREE.Color('#ffffff');renderer.render(ps,pc);gb.clearRect(0,0,S,S);gb.drawImage(renderer.domElement,0,0,S,S);ps.remove(o);
    const A=ga.getImageData(0,0,S,S),Bd=gb.getImageData(0,0,S,S),O=go.createImageData(S,S);
    for(let i=0;i<A.data.length;i+=4){const al=Math.max(0,Math.min(255,255-((Bd.data[i]-A.data[i])+(Bd.data[i+1]-A.data[i+1])+(Bd.data[i+2]-A.data[i+2]))/3));const f=al>0?255/al:0;
      O.data[i]=Math.min(255,A.data[i]*f);O.data[i+1]=Math.min(255,A.data[i+1]*f);O.data[i+2]=Math.min(255,A.data[i+2]*f);O.data[i+3]=al;}
    {const sc=cnv(S,S),sg=sc.getContext('2d');sg.putImageData(O,0,0);go.clearRect(0,0,S,S);const gr=go.createRadialGradient(S/2,S*.86,2,S/2,S*.86,S*.36);gr.addColorStop(0,'rgba(0,0,0,.5)');gr.addColorStop(1,'rgba(0,0,0,0)');go.save();go.translate(S/2,S*.86);go.scale(1,.28);go.translate(-S/2,-S*.86);go.fillStyle=gr;go.fillRect(0,0,S,S);go.restore();go.drawImage(sc,0,0);}
    try{SVG[k]='<img class="iimg" alt="" src="'+out.toDataURL('image/png')+'">';}catch(e){}}
  penv.dispose();renderer.setPixelRatio(prevPR);renderer.toneMappingExposure=prevExp;
  for(const k of ITEM_KEYS){const el=document.getElementById('h-'+k);if(el)el.innerHTML=SVG[k]+'<span><b>'+HELP[k][0]+'.</b> '+HELP[k][1]+'</span>';}}
const ITEM_GLOW={pep:'#ff5a2a',dough:'#ffe2a0',lob:'#c9e86a',oil:'#e8b23a',flour:'#ffffff',wheel:'#ff3b1a'};let _haloG=null;
function itemMesh(type){const o=itemProto(type).clone();if(ITEM_GLOW[type]&&type!=='oil'){if(!_haloG){_haloG=new THREE.PlaneGeometry(1,1);KGSET.add(_haloG);}
    const h=new THREE.Sprite(new THREE.SpriteMaterial({map:T2(TX.glow),color:ITEM_GLOW[type],transparent:true,opacity:.55,depthWrite:false,blending:THREE.AdditiveBlending,toneMapped:false}));h.scale.setScalar(type==='wheel'?26:14);h.renderOrder=3;o.add(h);}if(type==='wheel')o.userData.disc=o.getObjectByName('disc');scene.add(o);return o;}
/* ================= EXTRA ITEMS (15 more, 25 in total) ================= */
const NEWITEMS={
  jalapeno:['Jalapeño Triple','Three quick green boosts. Tap once for each.','#4fd02a'],
  meatball:['Bowling Meatball','A heavy meatball that rolls straight and bowls over everyone in its path. Bounces off the crust.','#9a5a32'],
  torpedo:['Anchovy Torpedo','A fast homing fish that hunts the racer directly ahead.','#8fc8e8'],
  shroom:['Spring Shroom','A huge springy jump with a burst of speed. Hop clean over traps and hazards.','#e05a3a'],
  magnet:['Pizza Magnet','Locks onto the racer ahead and reels you in fast.','#ff3b3b'],
  cutter:['Cutter Orbit','Three pizza cutters spin around your kart. Anyone who touches them spins out.','#d8dde3'],
  sauce:['Sauce Splat','Splatters sauce over every racer ahead, smearing their view and their steering.','#d8301c'],
  heat:['Heat Wave','A blast of oven heat that knocks back and shrinks every rival for a few seconds.','#ff7a1a'],
  bomb:['Calzone Bomb','Lobbed ahead, it blows up in a big blast a moment later.','#e2b06a'],
  forks:['Fork Spikes','Scatters forks across the road behind you. Drive over them and you spin.','#c9ced6'],
  ghost:['Ghost Pepper','Fade out for a few seconds: nothing can hit you, and you steal the leader’s item.','#e8f6ff'],
  cannon:['Pizza Cannon','Fires you down the track at huge speed, ploughing through anyone in the way.','#ffd23a'],
  twister:['Dough Twister','A spinning dough tornado that rolls down the track and tosses racers into the air.','#f3dfb4'],
  swap:['Topping Swap','Trade places with the racer right ahead of you.','#b26bff'],
  boxes:['Box Barricade','Drops a wall of pizza boxes across the road behind you.','#c98b4e']};
const NOBACK=['chili','garlic','wheel','rush','freezer','jalapeno','torpedo','shroom','magnet','cutter','sauce','heat','forks','ghost','cannon','twister','swap','boxes'];
const ITEM_COL={chili:'#ff5a1a',pepperoni:'#ff6a3a',oil:'#e8c040',dough:'#ffe2a0',trio:'#ff6a3a',garlic:'#e8fff0',flour:'#ffffff',wheel:'#ff3b1a',rush:'#7fe8ff',freezer:'#bfe6ff'};
NEWITEMS.garlic2=['Double Garlic Shield','Two garlic layers that stay on until you are hit. Each layer blocks one item or special ability.','#b8ffb0'];
for(const k in NEWITEMS){ITEM_COL[k]=NEWITEMS[k][2];if(!ITEM_KEYS.includes(k))ITEM_KEYS.push(k);HELP[k]=[NEWITEMS[k][0],NEWITEMS[k][1]];
  SVG[k]='<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="8" fill="'+NEWITEMS[k][2]+'"/></svg>';}
/* new odds: the leaders get defensive tools, the pack gets attacks, the back of the field gets the big catch-up items */
ROLL[0]={pepperoni:18,oil:15,trio:8,garlic:10,garlic2:4,dough:6,flour:10,chili:6,forks:12,boxes:10,meatball:9,bomb:7,jalapeno:4,cutter:4};
ROLL[1]={pepperoni:9,oil:6,trio:9,garlic:7,garlic2:3,dough:9,flour:6,chili:9,freezer:3,wheel:2,rush:2,jalapeno:8,meatball:7,torpedo:8,shroom:6,cutter:6,sauce:5,bomb:6,forks:4,magnet:5,ghost:3,twister:4,swap:3};
ROLL[2]={chili:10,dough:7,trio:6,rush:8,wheel:8,freezer:6,jalapeno:10,torpedo:7,magnet:9,cannon:7,heat:4,sauce:6,ghost:5,twister:5,swap:6,shroom:4};
/* ---------- models ---------- */
Object.assign(ITEM_BUILD,{
  jalapeno(){const G=new THREE.Group(),g=lathe([[0,-2.6],[.5,-2.4],[.9,-1.6],[1.05,0],[1,1.4],[.85,2.2],[.4,2.6],[0,2.65]],28);const p=g.attributes.position;
    for(let i=0;i<p.count;i++){const y=p.getY(i),b=.12*y*y;p.setX(i,p.getX(i)+b);}g.computeVertexNormals();vcol(g,(x,y,z,c)=>c.set('#3f9a2a').lerp(new THREE.Color('#6fd04a'),.3+.3*nz3(x*3,y*2,z*3)));
    const m=IMesh(g,imat('x_jalvc',{vertexColors:true,roughness:.25,clearcoat:1,clearcoatRoughness:.15}),[0,0,0],null,[0,0,.25],G);
    IMesh(new THREE.CylinderGeometry(.22,.32,1.2,10),imat('x_stem',{color:'#4f7a2a',roughness:.6}),[.65,3,0],null,[0,0,-.5],G);
    for(let i=0;i<3;i++)IMesh(new THREE.SphereGeometry(.42,12,10),imat('x_jalspark',{color:'#ffe066',emissive:'#ffcc33',emissiveIntensity:1.2}),[1.6,-1+i*1.1,.9],null,null,G);return G;},
  meatball(){const G=new THREE.Group(),a=new THREE.Color('#7a4528'),b=new THREE.Color('#3a1e10');const g=vcol(lumpy(new THREE.IcosahedronGeometry(3,4),.09,2.2,4.1),(x,y,z,c)=>{const n=nz3(x*1.8,y*1.8,z*1.8);c.copy(a).lerp(b,Math.max(0,n)*.8);});
    IMesh(g,imat('x_meatvc',{vertexColors:true,roughness:.7,clearcoat:.4,clearcoatRoughness:.5}),null,null,null,G);const h=imat('x_herb',{color:'#3f8a35',roughness:.5});
    for(let i=0;i<14;i++){const u=Math.random()*6.28,v=Math.acos(2*Math.random()-1);IMesh(new THREE.BoxGeometry(.5,.12,.3),h,[3*Math.sin(v)*Math.cos(u),3*Math.cos(v),3*Math.sin(v)*Math.sin(u)],null,[u,v,0],G);}return G;},
  torpedo(){const G=new THREE.Group(),body=vcol(lathe([[0,-3.4],[.6,-3],[1.25,-1.6],[1.4,0],[1.15,1.6],[.6,2.8],[0,3.2]],28),(x,y,z,c)=>c.set(x>0?'#cfe2f0':'#5a7a96').lerp(new THREE.Color('#9ec4dc'),.5+.3*Math.sin(y*3)));
    const b=IMesh(body,imat('x_fishvc',{vertexColors:true,metalness:.6,roughness:.25,clearcoat:1}),null,null,[0,0,Math.PI/2],G);
    const fin=imat('x_fin',{color:'#4a6a86',roughness:.4,side:THREE.DoubleSide});const tail=new THREE.Shape();tail.moveTo(0,0);tail.lineTo(-1.8,1.6);tail.lineTo(-1.2,0);tail.lineTo(-1.8,-1.6);tail.closePath();
    IMesh(new THREE.ShapeGeometry(tail),fin,[-3.1,0,0],null,null,G);IMesh(new THREE.ConeGeometry(.6,1.4,3),fin,[0,1.5,0],[.3,1,1],null,G);
    for(const s of [-1,1]){IMesh(new THREE.SphereGeometry(.42,12,10),imat('x_fisheye',{color:'#ffffff',roughness:.1}),[2.1,.45,s*.75],null,null,G);IMesh(new THREE.SphereGeometry(.22,10,8),imat('x_pupil',{color:'#111111'}),[2.4,.5,s*.85],null,null,G);}
    IMesh(new THREE.CylinderGeometry(.5,.5,.3,10),imat('x_prop',{color:'#d9a84a',metalness:1,roughness:.25}),[-2.6,0,0],null,[0,0,Math.PI/2],G);return G;},
  shroom(){const G=new THREE.Group();const cap=vcol(new THREE.SphereGeometry(2.8,32,16,0,Math.PI*2,0,Math.PI/2),(x,y,z,c)=>{c.set('#d8321e');});IMesh(cap,imat('x_capvc',{vertexColors:true,roughness:.35,clearcoat:.8}),[0,1.4,0],[1,.8,1],null,G);
    for(let i=0;i<7;i++){const u=i/7*6.28+.3,v=.45+(i%3)*.3;IMesh(new THREE.SphereGeometry(.55,10,8),imat('x_spot',{color:'#fff8ec',roughness:.5}),[2.6*Math.sin(v)*Math.cos(u),1.4+2.2*Math.cos(v),2.6*Math.sin(v)*Math.sin(u)],[1,.4,1],null,G);}
    IMesh(new THREE.CylinderGeometry(1,1.2,2,20),imat('x_stemw',{color:'#f6ecd8',roughness:.6}),[0,.4,0],null,null,G);
    for(let i=0;i<4;i++)IMesh(new THREE.TorusGeometry(1,.16,8,20),imat('x_spring',{color:'#c9ced6',metalness:1,roughness:.2}),[0,-.8-i*.5,0],null,[Math.PI/2,0,i*.2],G);return G;},
  magnet(){const G=new THREE.Group();IMesh(new THREE.TorusGeometry(2.2,.8,14,28,Math.PI),imat('x_magred',{color:'#d8241a',roughness:.3,clearcoat:1}),[0,.6,0],null,[0,0,0],G);
    for(const s of [-1,1]){IMesh(new THREE.CylinderGeometry(.82,.82,1.8,18),imat('x_magred',{}),[s*2.2,-.3,0],null,null,G);IMesh(new THREE.CylinderGeometry(.84,.84,.9,18),imat('x_magtip',{color:'#e8ecf0',metalness:1,roughness:.15}),[s*2.2,-1.6,0],null,null,G);}
    for(let i=0;i<3;i++)IMesh(new THREE.TorusGeometry(.9+i*.6,.06,6,24,Math.PI*.6),imat('x_zap',{color:'#7fe8ff',emissive:'#7fe8ff',emissiveIntensity:1.5}),[0,-2.4-i*.4,0],null,[Math.PI/2,0,Math.PI*1.2],G);return G;},
  cutter(){const G=new THREE.Group();IMesh(new THREE.CylinderGeometry(2.4,2.4,.24,40),imat('x_blade',{color:'#f2f5f8',metalness:.7,roughness:.22,clearcoat:1}),[0,0,0],null,[Math.PI/2,0,0],G).name='disc';
    IMesh(new THREE.CylinderGeometry(.7,.7,.5,16),imat('x_hub',{color:'#9aa4b0',metalness:1,roughness:.3}),[0,0,0],null,[Math.PI/2,0,0],G);IMesh(new THREE.BoxGeometry(.6,3.6,.6),imat('x_handle',{color:'#d8301c',roughness:.3,clearcoat:1}),[0,-2.8,0],null,[0,0,.3],G);
    IMesh(new THREE.BoxGeometry(.5,.9,.9),imat('x_fork',{color:'#9aa4b0',metalness:1,roughness:.3}),[-.1,-1.1,0],null,null,G);return G;},
  sauce(){const G=new THREE.Group();IMesh(lathe([[0,-2.6],[1.6,-2.6],[1.8,-2.2],[1.8,1.2],[1.2,2],[.5,2.4],[0,2.4]],28),imat('x_bottle',{color:'#d8301c',roughness:.25,clearcoat:1}),null,null,null,G);
    IMesh(new THREE.ConeGeometry(.45,1.6,14),imat('x_nozzle',{color:'#f4f4f2',roughness:.4}),[0,3.1,0],null,null,G);IMesh(new THREE.CylinderGeometry(1.85,1.85,1.2,28),imat('x_label',{color:'#fff4dc',roughness:.5}),[0,-.4,0],null,null,G);
    for(let i=0;i<3;i++)IMesh(new THREE.SphereGeometry(.4-i*.08,10,8),imat('x_drip',{color:'#b8200e',roughness:.1,clearcoat:1}),[.5*i,4+i*.7,0],null,null,G);return G;},
  heat(){const G=new THREE.Group();IMesh(new THREE.SphereGeometry(1.9,24,18),imat('x_core',{color:'#ffb23a',emissive:'#ff6a12',emissiveIntensity:1.6,roughness:.4}),null,null,null,G);
    const fl=imat('x_flame',{color:'#ff5a14',emissive:'#ff3a08',emissiveIntensity:1.4,roughness:.5});for(let i=0;i<7;i++){const a=i/7*6.28;const c=IMesh(new THREE.ConeGeometry(.8,3.2,10),fl,[Math.cos(a)*1.4,1+Math.sin(i*2)*.4,Math.sin(a)*1.4],null,null,G);c.lookAt(Math.cos(a)*4,4,Math.sin(a)*4);c.rotateX(Math.PI/2);}return G;},
  bomb(){const G=new THREE.Group();const g=vcol(new THREE.SphereGeometry(2.6,32,20,0,Math.PI*2,0,Math.PI*.62),(x,y,z,c)=>c.set('#e2b06a').lerp(new THREE.Color('#a8682a'),Math.max(0,nz3(x*2,y*2,z*2))*.7));
    IMesh(g,imat('x_calzvc',{vertexColors:true,roughness:.65}),[0,-.4,0],[1.25,1,.85],null,G);IMesh(new THREE.TorusGeometry(2.6,.32,8,40),imat('x_crimp',{color:'#c8883e',roughness:.6}),[0,-.9,0],[1.25,.85,1],[Math.PI/2,0,0],G);
    IMesh(new THREE.CylinderGeometry(.14,.14,1.6,6),imat('x_fuse',{color:'#3a2a1a'}),[0,2.6,0],null,[0,0,.3],G);IMesh(new THREE.SphereGeometry(.45,10,8),imat('x_spark',{color:'#fff2a0',emissive:'#ffcc33',emissiveIntensity:3}),[.3,3.4,0],null,null,G);return G;},
  forks(){const G=new THREE.Group(),m=imat('x_steel',{color:'#d8dde3',metalness:1,roughness:.18});for(let i=0;i<3;i++){const f=new THREE.Group();f.rotation.set(Math.PI/2,0,i*2.1);f.position.y=i*.25;G.add(f);
      IMesh(new THREE.BoxGeometry(.5,4,.2),m,[0,-1.6,0],null,null,f);IMesh(new THREE.BoxGeometry(1.4,.5,.2),m,[0,.6,0],null,null,f);for(let t=0;t<4;t++)IMesh(new THREE.ConeGeometry(.12,1.6,6),m,[-.55+t*.37,1.6,0],null,null,f);}return G;},
  ghost(){const G=new THREE.Group();const g=lathe([[0,3],[1.4,2.6],[2.1,1.4],[2.2,-.6],[2.4,-1.8],[0,-1.2]],32);const p=g.attributes.position;for(let i=0;i<p.count;i++){const y=p.getY(i);if(y<-1){const a=Math.atan2(p.getZ(i),p.getX(i));p.setY(i,y+Math.sin(a*6)*.4);}}g.computeVertexNormals();
    IMesh(g,imat('x_ghostb',{color:'#f6fbff',roughness:.3,transmission:.0,transparent:true,opacity:.9,emissive:'#bfe6ff',emissiveIntensity:.25}),null,null,null,G);
    for(const s of [-1,1])IMesh(new THREE.SphereGeometry(.38,10,8),imat('x_geye',{color:'#1a1a2a'}),[1.6,1.4,s*.7],[.6,1.3,1],null,G);IMesh(new THREE.SphereGeometry(.35,10,8),imat('x_gmouth',{color:'#d8301c'}),[1.9,.4,0],[.5,1,1.2],null,G);
    IMesh(new THREE.ConeGeometry(.6,1.6,10),imat('x_gpep',{color:'#ff5a14',roughness:.3,clearcoat:1}),[0,3.4,0],null,[0,0,.4],G);return G;},
  cannon(){const G=new THREE.Group();IMesh(lathe([[1.6,-3],[1.9,-2.6],[1.6,2.2],[1.9,2.6],[1.9,3.2],[1.3,3.2],[1.3,-2.4],[0,-2.4]],28),imat('x_barrel',{color:'#26282c',metalness:.8,roughness:.3}),[0,.6,0],null,[0,0,-1.2],G);
    IMesh(new THREE.TorusGeometry(1.75,.28,8,28),imat('x_band',{color:'#d8301c',roughness:.3}),[0,.6,0],null,[Math.PI/2,0,-1.2],G).rotation.set(0,0,0);
    for(const s of [-1,1])IMesh(new THREE.CylinderGeometry(1.4,1.4,.5,20),imat('x_cwheel',{color:'#8a5a30',roughness:.6}),[-.6,-1.4,s*1.9],null,[Math.PI/2,0,0],G);
    IMesh(new THREE.SphereGeometry(.9,14,10),imat('x_cball',{color:'#ffd23a',emissive:'#ff9a1f',emissiveIntensity:.6}),[2.9,2.4,0],null,null,G);return G;},
  twister(){const G=new THREE.Group();const m=imat('x_dough2',{color:'#f3dfb4',roughness:.7,transparent:true,opacity:.9});for(let i=0;i<9;i++){IMesh(new THREE.TorusGeometry(.6+i*.33,.32,8,24),m,[Math.sin(i*1.1)*.3,-3+i*.75,Math.cos(i*1.1)*.3],null,[Math.PI/2,0,0],G);}
    IMesh(new THREE.ConeGeometry(.6,1.4,12),m,[0,-3.7,0],null,[Math.PI,0,0],G);return G;},
  swap(){const G=new THREE.Group(),m=imat('x_swapm',{color:'#9a4ae0',emissive:'#6a2ab0',emissiveIntensity:.5,roughness:.3,clearcoat:1});for(const s of [0,1]){const g=new THREE.Group();g.rotation.z=s*Math.PI;G.add(g);
      IMesh(new THREE.TorusGeometry(2.2,.45,12,28,Math.PI*.8),m,[0,0,0],null,[0,0,.25],g);IMesh(new THREE.ConeGeometry(.95,1.6,16),m,[-2.15,-.35,0],null,[0,0,Math.PI*.95],g);}
    IMesh(new THREE.SphereGeometry(.8,14,10),imat('x_swapc',{color:'#ffe066',emissive:'#ffb21a',emissiveIntensity:.8}),null,null,null,G);return G;},
  boxes(){const G=new THREE.Group(),lid=new THREE.MeshStandardMaterial({map:T2(TX.lid),roughness:.8}),side=new THREE.MeshStandardMaterial({map:T2(TX.side),roughness:.85}),bot=new THREE.MeshStandardMaterial({color:'#cdbb94',roughness:.9});
    for(let i=0;i<3;i++){const b=new THREE.Mesh(new THREE.BoxGeometry(4.6,.7,4.6),[side,side,lid,bot,side,side]);b.position.y=i*.75;b.rotation.y=i*.18;b.castShadow=true;G.add(b);}return G;}});
/* ---------- sounds: every item gets its own voice ---------- */
Object.assign(SFX,{
  jalapeno(){noise(.5,.12,'bandpass',300,3200,0,1.4,.5);tone(196,.5,'sawtooth',.03,520,0,.3);noise(.3,.05,'highpass',5000,9000,.05,1,.3);},
  meatball(v){thump(70,.5,.18*v);noise(1.2,.09*v,'lowpass',260,90,0,1,.3);tone(55,1,'sine',.05*v,48,0,.2);},
  torpedo(v){tone(420,.8,'triangle',.035*v,1300,0,.4);noise(.6,.06*v,'bandpass',900,3200,0,2,.3);},
  shroom(){tone(180,.35,'sine',.07,720,0,.5);tone(360,.3,'triangle',.03,1100,.05,.5);thump(120,.12,.06);},
  magnet(){for(let i=0;i<5;i++)tone(220+i*30,.18,'square',.012,440+i*60,i*.08,.3);noise(.8,.04,'bandpass',1200,2400,0,8,.4);},
  cutter(){[1568,2093,2637].forEach((f,i)=>tone(f,.4,'triangle',.02,f*1.2,i*.04,.6));noise(.3,.06,'highpass',4000,9000,0,1,.4);},
  sauce(v){noise(.45,.14*v,'lowpass',900,180,0,2,.3);thump(160,.2,.08*v);noise(.2,.06*v,'bandpass',1400,500,.12,4,.2);},
  heat(){thump(55,1.2,.25);noise(1.4,.18,'lowpass',1800,90,0,1,.8);noise(.9,.06,'highpass',2500,6000,.1,1,.6);tone(90,1.2,'sawtooth',.03,45,0,.3);},
  fuse(v){noise(.5,.04*v,'highpass',5000,8000,0,1,.1);},
  forks(v){for(let i=0;i<6;i++)bell(2400+Math.random()*1800,.12,.018*v,i*.03);},
  ghost(){[0,7,12].forEach((st,i)=>tone(330*Math.pow(2,st/12),1.1,'sine',.025,220*Math.pow(2,st/12),i*.06,.9));noise(1.2,.03,'bandpass',600,1200,0,6,.8);},
  cannon(){thump(60,.8,.35);noise(1,.25,'lowpass',2400,100,0,1,.6);noise(1.2,.12,'bandpass',400,2600,.1,1.2,.5);},
  twister(v){noise(2.2,.1*v,'bandpass',300,900,0,3,.5);noise(2.2,.05*v,'bandpass',900,500,.2,5,.5);},
  swap(){tone(300,.5,'sine',.05,1200,0,.6);tone(1200,.5,'sine',.04,300,.08,.6);noise(.5,.04,'highpass',3000,7000,0,1,.5);},
  boxes(v){for(let i=0;i<3;i++){thump(150-i*15,.12,.09*v,i*.07);noise(.1,.06*v,'lowpass',900,300,i*.07,1,.1);}},
  ability(){[523,784,1047,1568].forEach((f,i)=>bell(f,.6,.045,i*.06));noise(.8,.08,'highpass',3000,9000,0,1,.8);thump(100,.3,.12);}});
/* ---------- helpers ---------- */
function fireItem(k,it,back){const a=k.item,b=k.item2,d=k.ai.itemDelay;k.item=it;k.item2=null;useItem(k,back,true);k.item=a;k.item2=b;k.ai.itemDelay=d;}
function kartAhead(k){const st=standCache,i=st.indexOf(k);return i>0?st[i-1]:null;}
function itemFx(k,col,n){const gy=(k.wy||0)+7;spawnRing(k.x,(k.wy||0)+.6,k.y,col,40,.5);spawnRing(k.x,gy,k.y,'#ffffff',22,.3,false);burst(k.x,gy,k.y,n||30,[col,'#ffffff','#ffe066'],90,3);FXA.spawn(k.x,gy,k.y,0,0,0,col,40,8,.22,0,0);}
function blast(x,y,r,owner,kind,col){const gy=groundAt(x,y);for(const k of karts){if(k===owner&&kind!=='self')continue;if(k.loop)continue;if((k.x-x)**2+(k.y-y)**2<r*r){spinOut(k,kind==='self'?'pep':kind);if(!k.air&&k.shield<=0&&k.ghostT<=0&&!(k.absT>0)){k.air=true;k.big=true;k.airT=0;k.wvy=55;}}}
  burst(x,gy+6,y,60,[col,'#ffe066','#ffffff','#ff5a14'],140,4.2);for(let n=0;n<24;n++){const a=Math.random()*6.28,u=.3+Math.random()*.7;FXN.spawn(x+Math.cos(a)*6,gy+4,y+Math.sin(a)*6,Math.cos(a)*70*u,14+Math.random()*30,Math.sin(a)*70*u,'#5a4a3a',9,28,1.4,-3,1.2);}
  spawnRing(x,gy+.8,y,col,r*1.3,.7);spawnRing(x,gy+8,y,'#ffffff',r,.4,false);FXA.spawn(x,gy+8,y,0,0,0,'#fff2c8',70,12,.25,0,0);SFX.boom(near({x,y})||.3);if(Math.hypot(x-camera.position.x,y-camera.position.z)<160)shake(.9);}
const TRAIL={pep:'#ff7a3a',dough:'#ffe2a0',lob:'#c9e86a',flour:'#ffffff',torp:'#9fd8ff',meat2:'#c8784a',bomb:'#ffcc33',twist:'#f3dfb4'};
/* ---------- using the new items ---------- */
function useItem2(k,it,back){const ca=Math.cos(k.a),sa=Math.sin(k.a),st=standCache,i=st.indexOf(k),col=ITEM_COL[it]||'#ffe066',v=near(k);
  if(it==='jalapeno'){k.boost=Math.max(k.boost,1.05);k.jalN=(k.jalN||3)-1;if(k.jalN>0){k.item2=k.item;k.item='jalapeno';}else k.jalN=0;itemFx(k,col,24);if(k===player){SFX.jalapeno();shake(.35);}}
  else if(it==='meatball'){const dir=back?-1:1,sp=back?160:230+Math.max(0,k.speed)*.55;projectiles.push({type:'meat2',custom:1,x:k.x+ca*12*dir,y:k.y+sa*12*dir,vx:ca*sp*dir,vy:sa*sp*dir,t:7,owner:k,safe:.4,b:0,hits:0,roll:0,mesh:itemMesh('meatball')});SFX.meatball(v||.2);}
  else if(it==='torpedo'){const tg=kartAhead(k),sp=360+Math.max(0,k.speed);projectiles.push({type:'torp',custom:1,x:k.x+ca*12,y:k.y+sa*12,vx:ca*sp,vy:sa*sp,t:6,owner:k,safe:.3,b:0,target:tg,mesh:itemMesh('torpedo')});SFX.torpedo(v||.3);}
  else if(it==='shroom'){k.air=true;k.big=true;k.airT=0;k.wvy=78;k.boost=Math.max(k.boost,.9);k.drift=0;itemFx(k,col,30);if(v>0)SFX.shroom();if(k===player)shake(.4);}
  else if(it==='magnet'){k.magT=2.6;k.magTg=kartAhead(k);itemFx(k,col,20);if(v>0)SFX.magnet();}
  else if(it==='cutter'){k.cutT=8;k.cutA=0;if(!k.cutM){k.cutM=[0,1,2].map(()=>{const m=itemProto('cutter').clone();m.scale.setScalar(1.1);scene.add(m);return m;});}k.cutM.forEach(m=>m.visible=true);itemFx(k,col,24);if(v>0)SFX.cutter();}
  else if(it==='sauce'){for(let j=0;j<i;j++){const o=st[j];if(o.shield>0||o.ghostT>0||o.loop||o.absT>0)continue;if(absorb(o))continue;o.sauceT=4;burst(o.x,(o.wy||0)+8,o.y,26,['#d8301c','#a8180a','#ff6a3a'],70,3.2);spawnRing(o.x,(o.wy||0)+.6,o.y,'#d8301c',24,.5);if(o===player){sauceFx(true);SFX.sauce(1);}}
    itemFx(k,col,26);if(v>0)SFX.sauce(v);}
  else if(it==='heat'){for(const o of karts){if(o===k||o.loop||o.shield>0||o.ghostT>0||o.absT>0)continue;if(absorb(o))continue;o.shrinkT=3.2;o.speed*=.6;spinOut(o,'pep');}heatFlash();SFX.heat();itemFx(k,col,40);}
  else if(it==='bomb'){if(back)projectiles.push({type:'bomb',custom:1,x:k.x-Math.cos(k.ma)*16,y:k.y-Math.sin(k.ma)*16,vx:0,vy:0,t:1.6,fuse:1.6,owner:k,safe:9,b:0,landed:true,mesh:itemMesh('bomb')});
    else{const sp=Math.max(0,k.speed)+160;projectiles.push({type:'bomb',custom:1,x:k.x+ca*8,y:k.y+sa*8,vx:ca*sp,vy:sa*sp,t:.75+1.1,t0:.75,fuse:1.1,owner:k,safe:9,b:0,landed:false,mesh:itemMesh('bomb')});}if(v>0)SFX.throwF();}
  else if(it==='forks'){const p=track[k.idx];for(const o of [-22,0,22]){const x=k.x-Math.cos(k.ma)*22+p.nx*o,y=k.y-Math.sin(k.ma)*22+p.ny*o;hazards.push({x,y,t:25,born:0,owner:k,armed:false,kind:'forks',mesh:itemMesh('forks')});}if(v>0)SFX.forks(v);}
  else if(it==='ghost'){k.ghostT=4.5;const ld=st[0];if(ld&&ld!==k&&ld.item&&!absorb(ld)){const got=ld.item;ld.item=ld.item2;ld.item2=null;if(!k.item)k.item=got;else if(!k.item2)k.item2=got;if(ld===player)showBanner('Item stolen!',1.2);}
    itemFx(k,'#bfe6ff',30);if(v>0)SFX.ghost();}
  else if(it==='cannon'){k.cannonT=2.6;k.rush=2.6;k.boost=Math.max(k.boost,2.6);k.drift=0;itemFx(k,col,50);if(k===player){SFX.cannon();shake(1.2);}else if(v>0)SFX.cannon();}
  else if(it==='twister'){projectiles.push({type:'twist',custom:1,x:k.x+ca*16,y:k.y+sa*16,vx:0,vy:0,t:9,owner:k,safe:.6,b:0,prog:k.prog+3,lat:lateral(k),ph:Math.random()*6,mesh:itemMesh('twister')});if(v>0)SFX.twister(v);}
  else if(it==='swap'){const o=kartAhead(k);if(o&&!o.loop&&!k.loop&&!o.finished&&o.prog-k.prog<N*.35&&!absorb(o)){for(const f of ['x','y','px','py','a','ma','pa','pma','idx','prog','wy','pwy','lastG','sc','scI','speed']){const t=k[f];k[f]=o[f];o[f]=t;}
      for(const q of [k,o]){spawnRing(q.x,(q.wy||0)+.6,q.y,'#b26bff',40,.6);burst(q.x,(q.wy||0)+8,q.y,30,['#b26bff','#ffe066','#ffffff'],80,3);}if(k===camT||o===camT)camSnap=true;if(o===player)showBanner('Swapped!',1);}
    if(v>0||o===player)SFX.swap();}
  else if(it==='boxes'){const p=track[k.idx];for(const o of [-30,0,30]){const x=k.x-Math.cos(k.ma)*26+p.nx*o,y=k.y-Math.sin(k.ma)*26+p.ny*o;hazards.push({x,y,t:22,born:0,owner:k,armed:false,kind:'boxes',mesh:itemMesh('boxes')});}if(v>0)SFX.boxes(v);}}
/* ---------- the custom projectiles and status effects, run every physics step ---------- */
function itemsProj(p,dt){p.t-=dt;p.safe-=dt;
  if(p.type==='twist'){p.prog+=dt*Math.max(14,BASE_MAX*.72/(T.L/N));p.lat=Math.sin(simTime*1.6+p.ph)*(RW*.75);const P=trackAt(p.prog,p.lat);p.x=P.x;p.y=P.y;
    for(const k of karts){if(k.loop||(k===p.owner&&p.safe>0))continue;if((k.x-p.x)**2+(k.y-p.y)**2<20*20&&k.inv<=0){spinOut(k,'flour');if(!k.air&&k.shield<=0&&k.ghostT<=0&&!(k.absT>0)){k.air=true;k.big=true;k.airT=0;k.wvy=65;}}}
    return p.t<=0;}
  if(p.type==='torp'&&p.target&&!p.target.finished){const tg=p.target,des=Math.atan2(tg.y-p.y,tg.x-p.x);let cur=Math.atan2(p.vy,p.vx);cur+=clamp(angDiff(des,cur),-7*dt,7*dt);let sp=Math.hypot(p.vx,p.vy);const want=Math.max(380,Math.abs(tg.speed||0)*1.35+90);sp+=(want-sp)*Math.min(1,dt*3);p.vx=Math.cos(cur)*sp;p.vy=Math.sin(cur)*sp;}
  if(p.type==='bomb'){if(!p.landed){if(p.t<=p.fuse){p.landed=true;p.vx=p.vy=0;}}else{p.vx*=.9;p.vy*=.9;}if(p.t<=0){blast(p.x,p.y,48,null,'pep','#ff9a1f');return true;}if(p.landed&&Math.random()<.5)SFX.fuse(near({x:p.x,y:p.y})*.6);}
  p.x+=p.vx*dt;p.y+=p.vy*dt;const d=Math.hypot(p.x,p.y);if(d>RIM){const nx=p.x/d,ny=p.y/d,dot=p.vx*nx+p.vy*ny;p.vx-=2*dot*nx;p.vy-=2*dot*ny;p.x=nx*(RIM-1);p.y=ny*(RIM-1);if(++p.b>4)p.t=0;}
  if(p.type==='bomb')return false;
  const R=p.type==='meat2'?22:16;
  for(const k of karts){if(k.loop||(k===p.owner&&p.safe>0)||k.ghostT>0)continue;if((k.x-p.x)**2+(k.y-p.y)**2<R*R&&k.inv<=0){spinOut(k,p.type==='meat2'?'meat':'pep');if(p.type==='meat2'){p.hits++;if(p.hits>=3)return true;const sp=Math.hypot(p.vx,p.vy);p.vx*=.85;p.vy*=.85;if(sp<60)return true;}else return true;}}
  for(const h of hazards){if((h.x-p.x)**2+(h.y-p.y)**2<R*R*.6){h.t=0;if(p.type!=='meat2')return true;}}
  return p.t<=0;}
function itemsTick(dt){for(const k of karts){
    if(k.magT>0){k.magT-=dt;const tg=k.magTg;if(tg&&!tg.finished){const dx=tg.x-k.x,dy=tg.y-k.y,dd=Math.hypot(dx,dy)||1;if(dd<26)k.magT=0;else{k.boost=Math.max(k.boost,.12);const des=Math.atan2(dy,dx);k.ma+=clamp(angDiff(des,k.ma),-1.4*dt,1.4*dt);k.speed=Math.max(k.speed,Math.min(BASE_MAX*1.75,Math.abs(tg.speed||0)+130));}}else k.magT=0;}
    if(k.cutT>0){k.cutT-=dt;k.cutA=(k.cutA||0)+dt*5.5;for(let b=0;b<3;b++){const a=k.cutA+b*2.094,bx=k.x+Math.cos(a)*15,by=k.y+Math.sin(a)*15;
        for(const o of karts){if(o===k||o.loop)continue;if((o.x-bx)**2+(o.y-by)**2<12*12&&o.inv<=0)spinOut(o,'wheel');}
        for(const p of projectiles){if(p.owner!==k&&(p.x-bx)**2+(p.y-by)**2<11*11){p.t=0;p.dead=1;burst(bx,8,by,14,['#ffffff','#d8dde3'],60,2);}}}
      if(k.cutT<=0&&k.cutM)k.cutM.forEach(m=>m.visible=false);}
    if(k.ghostT>0)k.ghostT-=dt;if(k.sauceT>0){k.sauceT-=dt;if(k===player&&k.sauceT<=0)sauceFx(false);}if(k.shrinkT>0)k.shrinkT-=dt;if(k.cannonT>0)k.cannonT-=dt;}}
function itemsRender(time,dt){for(const p of projectiles){const col=TRAIL[p.type];if(!col)continue;const m=p.mesh.position;
    if(p.type==='meat2'){p.roll=(p.roll||0)+Math.hypot(p.vx,p.vy)*dt/3;p.mesh.position.set(p.x,groundAt(p.x,p.y)+4.5,p.y);p.mesh.rotation.set(0,-Math.atan2(p.vy,p.vx),-p.roll);if(Math.random()<.5)FXN.spawn(p.x,groundAt(p.x,p.y)+1,p.y,(Math.random()-.5)*16,6,(Math.random()-.5)*16,'#c8a878',4,10,.6,-2,1.5);continue;}
    if(p.type==='torp'){p.mesh.position.set(p.x,groundAt(p.x,p.y)+4,p.y);p.mesh.rotation.set(Math.sin(time*20)*.15,-Math.atan2(p.vy,p.vx),0);}
    if(p.type==='bomb'){const f=p.landed?1:1-(p.t-p.fuse)/p.t0;const gy=groundAt(p.x,p.y);p.mesh.position.set(p.x,gy+3+(p.landed?0:Math.sin(Math.PI*Math.min(1,f))*18),p.y);p.mesh.rotation.y+=dt*3;const pul=p.landed?1+Math.sin(time*(8+(1.6-p.t)*16))*.12:1;p.mesh.scale.setScalar(pul);
      FXA.spawn(m.x,m.y+5,m.z,(Math.random()-.5)*20,30,(Math.random()-.5)*20,'#ffcc33',1.8,.2,.3,60,1);continue;}
    if(p.type==='twist'){const gy=groundAt(p.x,p.y);p.mesh.position.set(p.x,gy+6,p.y);p.mesh.rotation.y+=dt*14;p.mesh.scale.setScalar(2.2+Math.sin(time*7)*.15);for(let n=0;n<2;n++){const a=Math.random()*6.28;FXN.spawn(p.x+Math.cos(a)*8,gy+2+Math.random()*12,p.y+Math.sin(a)*8,-Math.sin(a)*40,10,Math.cos(a)*40,'#f3e6c8',5,12,.7,0,1);}continue;}
    FXA.spawn(m.x+(Math.random()-.5)*1.2,m.y+(Math.random()-.5)*1.2,m.z+(Math.random()-.5)*1.2,(Math.random()-.5)*6,2,(Math.random()-.5)*6,col,p.type==='flour'?3:2.4,.2,.35,0,2);}
  for(const k of karts){const m=k.m;
    if(k.cutT>0&&k.cutM){for(let b=0;b<3;b++){const a=k.cutA+b*2.094,mm=k.cutM[b];mm.position.set(k.rx+Math.cos(a)*15,(k.rz||0)+5,k.ry+Math.sin(a)*15);mm.rotation.set(0,-a,time*25);if(Math.random()<.4)FXA.spawn(mm.position.x,mm.position.y,mm.position.z,0,0,0,'#e8f4ff',2,.2,.25,0,0);}}
    const sc=k.shrinkT>0?.62:1;if(m.g.userData.s!==sc){m.g.userData.s=sc;m.g.scale.setScalar(KS*m.sf*sc);}
    if(k.ghostT>0){m.tilt.visible=Math.floor(time*24)%3!==0;if(Math.random()<.5)FXA.spawn(k.rx+(Math.random()-.5)*10,(k.rz||0)+6,k.ry+(Math.random()-.5)*10,0,8,0,'#cfe8ff',3,.3,.4,0,0);}
    else if(!m.isFar&&!m.tilt.visible)m.tilt.visible=true;
    if(k.magT>0&&k.magTg){if(Math.random()<.8){const t=Math.random(),x=k.rx+(k.magTg.rx-k.rx)*t,z=k.ry+(k.magTg.ry-k.ry)*t;FXA.spawn(x,(k.rz||0)+6,z,0,0,0,'#ff5a5a',2.6,.3,.2,0,0);}}
    if(k.cannonT>0&&Math.random()<.9){const a=Math.random()*6.28;FXA.spawn(k.rx-Math.cos(k.rma)*10,(k.rz||0)+5,k.ry-Math.sin(k.rma)*10,Math.cos(a)*20,10,Math.sin(a)*20,'#ffcc33',5,.4,.4,0,1);FXN.spawn(k.rx-Math.cos(k.rma)*12,(k.rz||0)+4,k.ry-Math.sin(k.rma)*12,0,6,0,'#8a7a6a',5,16,.8,-2,1);}
    if(k.sauceT>0&&Math.random()<.3)FXN.spawn(k.rx,(k.rz||0)+3,k.ry,(Math.random()-.5)*10,2,(Math.random()-.5)*10,'#b8200e',2.5,1,.6,30,1);}}
/* sauce smears on the player's screen */
let _sauceEl=null;function sauceFx(on){if(!_sauceEl){_sauceEl=document.createElement('div');_sauceEl.className='saucefx';let h='';for(let i=0;i<9;i++){const x=10+Math.random()*80,y=10+Math.random()*70,s=10+Math.random()*16;h+='<i style="left:'+x+'%;top:'+y+'%;width:'+s+'vmin;height:'+s*0.8+'vmin;transform:rotate('+Math.random()*360+'deg)"></i>';}_sauceEl.innerHTML=h;stage.appendChild(_sauceEl);}
  _sauceEl.classList.toggle('on',on);}
function heatFlash(){const e=document.createElement('div');e.className='heatfx';stage.appendChild(e);setTimeout(()=>e.remove(),900);if(player)shake(.8);}

/* ================= CHARACTER ABILITIES: a special move that recharges every 30 seconds ================= */
const ABIL={pep:['Pepperoni Storm','Fires a fan of six spinning pepperoni slices ahead.','#ff5a2a'],
  basil:['Pesto Rush','A long, fresh burst of speed that ignores the slow cheese.','#3fd06a'],
  olive:['Slick Trail','Leaves a trail of olive-oil slicks behind for the pack to slide on.','#c8b23a'],
  mozz:['Melt Shield','Wraps the kart in stretchy cheese that blocks every hit for a while.','#fff4c0'],
  chili:['Fire Trail','A fiery boost that leaves burning flames behind on the road.','#ff3a12'],
  shroom:['Mega Shroom','Grows huge and unstoppable, flattening anyone in the way.','#c8a06a'],
  pineapple:['Spiky Shockwave','A spiky blast that spins out every racer nearby.','#ffd23a'],
  anchovy:['School of Fish','Launches three homing anchovies at the racers ahead.','#8fc8e8']};
const ABIL_TIME=30;
const abilKey=k=>k.r.name.toLowerCase();
function useAbility(k){const id=abilKey(k),A=ABIL[id];if(!A||k.abC<1||k.loop||k.finished)return;k.abC=0;const st=standCache,i=st.indexOf(k),v=near(k);
  itemFx(k,A[2],50);spawnRing(k.x,(k.wy||0)+.6,k.y,A[2],70,.8);if(k===player){SFX.ability();showBanner(A[0],1.4);shake(.6);abilFlash(A[2]);}else if(v>0)SFX.ability();
  if(id==='pep'){fireItem(k,'trio',false);k.abQ=[[.25,()=>fireItem(k,'trio',false)]];}
  else if(id==='basil'){k.boost=Math.max(k.boost,2.8);k.abFx=2.8;k.abCol=A[2];if(k===player)SFX.boost(3);}
  else if(id==='olive'){k.abQ=[0,.3,.6,.9].map(t=>[t,()=>hazards.push({x:k.x-Math.cos(k.ma)*22,y:k.y-Math.sin(k.ma)*22,t:25,born:0,owner:k,armed:false,mesh:itemMesh('oil')})]);}
  else if(id==='mozz'){k.shield=7;if(v>0)SFX.garlic(v||.3);}
  else if(id==='chili'){k.boost=Math.max(k.boost,2.2);k.fireT=2.2;k.abFx=2.2;k.abCol=A[2];if(k===player)SFX.chili();}
  else if(id==='shroom'){k.rush=4;k.boost=Math.max(k.boost,1.5);k.megaT=4;k.drift=0;}
  else if(id==='pineapple'){blast(k.x,k.y,80,k,'pep','#ffd23a');k.inv=Math.max(k.inv,.6);}
  else if(id==='anchovy'){for(let j=1;j<=3;j++){const tg=st[i-j];const sp=360+Math.max(0,k.speed),an=k.a+(j-2)*.25;projectiles.push({type:'torp',custom:1,x:k.x+Math.cos(an)*12,y:k.y+Math.sin(an)*12,vx:Math.cos(an)*sp,vy:Math.sin(an)*sp,t:6,owner:k,safe:.3,b:0,target:tg||null,mesh:itemMesh('torpedo')});}SFX.torpedo(v||.4);}}
function abilityTick(dt){for(const k of karts){if(state==='race'&&!k.finished&&k.abC<1){k.abC=Math.min(1,(k.abC||0)+dt/ABIL_TIME);if(k===player&&k.abC>=1){SFX.ready();abilBtn&&abilBtn.classList.add('ready');}}
    if(k.abQ&&k.abQ.length){for(const q of k.abQ)q[0]-=dt;while(k.abQ.length&&k.abQ[0][0]<=0)k.abQ.shift()[1]();}
    if(k.fireT>0){k.fireT-=dt;k.fireAcc=(k.fireAcc||0)+dt;if(k.fireAcc>.12){k.fireAcc=0;hazards.push({x:k.x-Math.cos(k.ma)*16,y:k.y-Math.sin(k.ma)*16,t:2.2,born:0,owner:k,armed:false,kind:'fire',mesh:fireMesh()});}}
    if(k.megaT>0)k.megaT-=dt;if(k.abFx>0)k.abFx-=dt;
    /* rivals fire their ability when it makes sense */
    if(!k.isPlayer&&k.abC>=1&&state==='race'){k.abWait=(k.abWait==null?1+Math.random()*4:k.abWait)-dt;if(k.abWait<=0){const id=abilKey(k),st=standCache,i=st.indexOf(k);let go=true;
      if(id==='pineapple')go=karts.some(o=>o!==k&&(o.x-k.x)**2+(o.y-k.y)**2<70*70);else if(id==='anchovy'||id==='pep')go=i>0;else if(id==='olive')go=i<st.length-1;
      if(go){useAbility(k);k.abWait=null;}else k.abWait=.8;}}}}
let _fireProto=null;function fireMesh(){if(!_fireProto){_fireProto=new THREE.Group();for(let i=0;i<3;i++){const c=new THREE.Mesh(KG.flame,flameMat);c.scale.set(3,3+i,3);c.position.set((i-1)*2.5,3,0);_fireProto.add(c);}
    const ci=new THREE.Mesh(KG.flameIn,flameInMat);ci.scale.set(3,3,3);ci.position.y=2;_fireProto.add(ci);}const o=_fireProto.clone();scene.add(o);return o;}
function abilityRender(time,dt){for(const k of karts){const m=k.m;if(k.megaT>0){const s=1+.45*Math.min(1,(4-k.megaT)*4,k.megaT*4);m.g.scale.setScalar(KS*m.sf*s);m.g.userData.s=-1;}
    if(k.abFx>0&&Math.random()<.9){FXA.spawn(k.rx-Math.cos(k.rma)*9+(Math.random()-.5)*6,(k.rz||0)+3+Math.random()*4,k.ry-Math.sin(k.rma)*9+(Math.random()-.5)*6,(Math.random()-.5)*14,8,(Math.random()-.5)*14,k.abCol||'#ffe066',3.4,.3,.45,0,1);}}
  for(const h of hazards)if(h.kind==='fire'){h.mesh.scale.setScalar(Math.max(.01,Math.min(1,h.t*1.4))*(1+Math.sin(time*20+h.x)*.1));if(Math.random()<.3)FXA.spawn(h.x,groundAt(h.x,h.y)+4,h.y,0,26,0,'#ff7a1a',3,.3,.4,0,0);}
  if(player&&abilBtn){const c=player.abC||0,rd=c>=.999;if(rd!==abilBtn.classList.contains('ready')||Math.abs(c-(abilBtn._c??-1))>.004){abilBtn._c=c;abilBtn.style.setProperty('--ab',(rd?100:c*100).toFixed(1)+'%');abilBtn.classList.toggle('ready',rd);}}}
let abilBtn=null,abilQueued=false;
function abilFlash(col){const e=document.createElement('div');e.className='abilfx';e.style.setProperty('--c',col);stage.appendChild(e);setTimeout(()=>e.remove(),900);}
function setupAbilityHud(){abilBtn=document.getElementById('abilBtn');if(!abilBtn)return;
  const go=e=>{e.preventDefault();e.stopPropagation();abilQueued=true;};abilBtn.addEventListener('pointerdown',go);
  addEventListener('keydown',e=>{if((e.code==='KeyC'||e.code==='KeyR')&&!e.repeat&&!(e.target.closest&&e.target.closest('.overlay'))){abilQueued=true;e.preventDefault();}});}
function abilityHudFor(ri){if(!abilBtn)return;const A=ABIL[RACERS[ri].name.toLowerCase()];abilBtn.style.setProperty('--ac',A?A[2]:'#ffe066');abilBtn.style.backgroundImage=PORTRAITS[ri]?'url('+PORTRAITS[ri]+')':'';abilBtn.setAttribute('aria-label','Use special ability: '+(A?A[0]:''));abilBtn._c=-1;abilBtn.classList.remove('ready');}

/* ================= RACE INTRO: three short cinematic shots of the track before the countdown ================= */
let introT=0,introSkip=false;const INTRO_SHOT=2.4,INTRO_N=3;
function startIntro(){introT=0;introSkip=false;state='intro';stage.classList.add('cinema');const m=MAPS[mapIdx],ci=$('cine');ci.hidden=false;ci.classList.remove('out');void ci.offsetWidth;ci.classList.add('on');
  $('cineName').textContent=m.name;$('cineSub').textContent=(gp?CUPS[gp.cup].name+' · Race '+(gp.race+1)+' of 4':'Single race')+' · '+CLASSES[clsKey].label;$('cineSkip').hidden=false;}
function endIntro(){stage.classList.remove('cinema');const ci=$('cine');ci.classList.remove('on');ci.classList.add('out');setTimeout(()=>{ci.hidden=true;},450);state='countdown';cd=3.4;lastCd=4;camSnap=true;acc=0;}
function introCam(dt){const t=introT,sh=Math.min(INTRO_N-1,Math.floor(t/INTRO_SHOT)),f=Math.min(1,(t-sh*INTRO_SHOT)/INTRO_SHOT),e=f*f*(3-2*f),gl=(x,z)=>groundAt(x,z);
  const P=(s,lat)=>trackAt(s,lat);
  if(sh===0){/* low dolly down the road ahead of the start, like riding along at eye level */
    const s=22+e*16,a=P(s,0),b=P(s+22,0);camera.position.set(a.x,gl(a.x,a.y)+10+e*3,a.y);camera.lookAt(b.x,gl(b.x,b.y)+8,b.y);}
  else if(sh===1){/* a crane shot drifting across the starting grid from the side */
    const g=P(N-6,0),q=track[(N-6)%N],side=1,off=110-e*20,along=-40+e*80;const cx=g.x+q.nx*off*side+q.tx*along,cz=g.y+q.ny*off*side+q.ty*along;camera.position.set(cx,gl(cx,cz)+40-e*10,cz);camera.lookAt(g.x+q.tx*10,gl(g.x,g.y)+4,g.y+q.ty*10);}
  else{/* swing in from in front of your kart to the chase camera */
    const k=player||camT,fx=Math.cos(k.ma),fy=Math.sin(k.ma),gy=gl(k.x,k.y),a0=Math.PI*(1-e),d=34-e*6,h=7+e*4;const dx=Math.cos(k.ma+a0),dz=Math.sin(k.ma+a0);
    camera.position.set(k.x-dx*d,gy+h,k.y-dz*d);camera.lookAt(k.x+fx*8*e,gy+5,k.y+fy*8*e);}
  camera.up.set(0,1,0);if(Math.abs(camera.fov-58)>.1){camera.fov=58;camera.updateProjectionMatrix();}snapSun(camera.position.x,gl(camera.position.x,camera.position.z),camera.position.z);}

/* ================= TRACK DRESSING: string lights over the road and chevron boards on the bends ================= */
function chevronTex(dir,night){const c=cnv(256,96),g=c.getContext('2d');g.fillStyle=night?'#1a1030':'#c8261b';g.fillRect(0,0,256,96);g.strokeStyle='#ffffff';g.lineWidth=5;g.strokeRect(4,4,248,88);
  g.fillStyle=night?'#ffe36b':'#fff4dc';for(let i=0;i<3;i++){const x=50+i*72;g.beginPath();if(dir>0){g.moveTo(x-22,16);g.lineTo(x+16,48);g.lineTo(x-22,80);g.lineTo(x-8,80);g.lineTo(x+30,48);g.lineTo(x-8,16);}else{g.moveTo(x+22,16);g.lineTo(x-16,48);g.lineTo(x+22,80);g.lineTo(x+8,80);g.lineTo(x-30,48);g.lineTo(x+8,16);}g.closePath();g.fill();}
  const t=new THREE.CanvasTexture(c);t.encoding=THREE.sRGBEncoding;t.anisotropy=maxAniso;return t;}
function buildDressing(def,ctx){const {pick,straight,farFrom,used}=ctx,night=def.theme==='night',G=new THREE.Group();G.userData.noLift=true;world.add(G);
  const post=wm('#3a3a44',{metalness:.6,roughness:.4}),texL=chevronTex(-1,night),texR=chevronTex(1,night);
  const signM=d=>new THREE.MeshStandardMaterial({map:d>0?texR:texL,roughness:.5,emissive:'#ffffff',emissiveMap:d>0?texR:texL,emissiveIntensity:night?.9:.12});const mR=signM(1),mL=signM(-1);
  let last=-99;for(let j=0;j<N;j+=2){const p=track[j];if(Math.abs(p.bend)<.6||j-last<34||segBad(j))continue;const sd=-Math.sign(p.bend),q=track[(j-10+N)%N];
    if(SHORTS.some(sc=>[sc.a,sc.b].some(e=>Math.min(Math.abs(e-j),N-Math.abs(e-j))<14)))continue;last=j;
    for(let n=0;n<2;n++){const r=track[(j-4+n*6+N)%N],o=(WALLD+10)*sd,x=r.x+r.nx*o,z=r.y+r.ny*o;if(nearTrack(x,z,WALLD-2))continue;const g=new THREE.Group();g.position.set(x,groundAt(x,z),z);g.rotation.y=-q.ang-Math.PI/2;G.add(g);
      put(new THREE.BoxGeometry(1.4,22,1.4),post,-12,11,0,g);put(new THREE.BoxGeometry(1.4,22,1.4),post,12,11,0,g);const b=put(new THREE.BoxGeometry(34,13,1),[post,post,post,post,sd>0?mL:mR,post],0,20,0,g);}}
  /* string lights and pennants across the straights */
  const rope=wm('#2a2a33',{roughness:.6}),pole=wm('#5a3a22',{roughness:.7}),bulbs=[],flagP=[],flagC=[],cols=['#e0452c','#f7c948','#2f7fd8','#3f9a35','#fff4dc'].map(c=>new THREE.Color(c));
  for(let i=0;i<7;i++){const b=pick(Math.floor((i+.25)*N/7),j=>!segBad(j)&&straight(j,6,.35)&&farFrom(j,10)&&!PONDS.some(q=>Math.min(Math.abs(q.j-j),N-Math.abs(q.j-j))<q.span+8));if(b==null)continue;const p=track[b],H=34+(i%2)*8,half=WALLD+4;
    const ends=[-1,1].map(s=>{const x=p.x+p.nx*half*s,z=p.y+p.ny*half*s;return [x,groundAt(x,z),z];});if(ends.some(([x,,z])=>nearTrack(x,z,WALLD-4)))continue;
    for(const [x,y,z] of ends)put(new THREE.CylinderGeometry(1,1.3,H+2,8),pole,x,y+H/2,z,G);
    const pts=[];for(let k=0;k<=24;k++){const f=k/24,x=ends[0][0]+(ends[1][0]-ends[0][0])*f,z=ends[0][2]+(ends[1][2]-ends[0][2])*f,y=ends[0][1]+(ends[1][1]-ends[0][1])*f+H-Math.sin(f*Math.PI)*9;pts.push(new THREE.Vector3(x,y,z));if(k%2===0&&k>0&&k<24)bulbs.push(x,y-1.2,z);
      if(i%2===1&&k%2===1){flagP.push([x,y,z,p.ang]);flagC.push(cols[k%cols.length]);}}
    put(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts),40,.35,5,false),rope,0,0,0,G,false);}
  safeBake(G);
  if(bulbs.length){const bg=new THREE.BufferGeometry();bg.setAttribute('position',new THREE.Float32BufferAttribute(bulbs,3));const bm=new THREE.PointsMaterial({color:'#fff1b0',size:2.6,sizeAttenuation:true,toneMapped:false});const B=new THREE.Points(bg,bm);B.userData.noLift=true;world.add(B);
    const gl=new THREE.PointsMaterial({map:T2(TX.glow),color:'#ffcf6a',size:9,sizeAttenuation:true,transparent:true,opacity:night?.7:.35,depthWrite:false,blending:THREE.AdditiveBlending,toneMapped:false});const B2=new THREE.Points(bg,gl);B2.userData.noLift=true;world.add(B2);}
  if(flagP.length){const tri=new THREE.BufferGeometry();tri.setAttribute('position',new THREE.Float32BufferAttribute([-2.2,0,0,2.2,0,0,0,-5,0],3));tri.computeVertexNormals();const fm=new THREE.MeshStandardMaterial({side:THREE.DoubleSide,roughness:.7});
    const I=new THREE.InstancedMesh(tri,fm,flagP.length),m4=new THREE.Matrix4(),q=new THREE.Quaternion();flagP.forEach(([x,y,z,a],n)=>{q.setFromEuler(new THREE.Euler(0,-a,0));m4.compose(new THREE.Vector3(x,y-.6,z),q,new THREE.Vector3(1,1,1));I.setMatrixAt(n,m4);I.setColorAt(n,flagC[n]);});
    I.userData.noLift=true;I.frustumCulled=false;world.add(I);animators.push(t=>{I.rotation.x=0;});}}

const DROPS=['oil','forks','boxes'];
function useItem(k,back){
  back=DROPS.includes(k.item);const it=k.item;if(it==='garlic'||it==='garlic2'){k.item=k.item2;k.item2=null;addShield(k,it==='garlic2'?2:1);return;}k.item=k.item2;k.item2=null;{const col=ITEM_COL[it]||'#ffe066',gy=(k.wy||0)+7;if(k===player)shake(.18);
    FXA.spawn(k.x,gy,k.y,0,0,0,col,30,8,.18,0,0);spawnRing(k.x,(k.wy||0)+.6,k.y,col,26,.35);for(let n=0;n<10;n++){const a=Math.random()*6.28;FXA.spawn(k.x,gy,k.y,Math.cos(a)*40,15+Math.random()*25,Math.sin(a)*40,col,2.2,.4,.3,40,1);}}if(k.item)k.ai.itemDelay=.6+Math.random()*1.6;if(NEWITEMS[it]){useItem2(k,it,back);return;}const ca=Math.cos(k.a),sa=Math.sin(k.a),st=standCache,i=st.indexOf(k);
  if(it==='chili'){k.boost=Math.max(k.boost,1.4);}
  else if(it==='pepperoni'){if(back)projectiles.push({type:'pep',x:k.x-ca*10,y:k.y-sa*10,vx:-ca*240,vy:-sa*240,t:4,owner:k,safe:.3,b:0,mesh:itemMesh('pep')});
    else{const v=300+Math.max(0,k.speed);projectiles.push({type:'pep',x:k.x+ca*10,y:k.y+sa*10,vx:ca*v,vy:sa*v,t:4,owner:k,safe:.3,b:0,mesh:itemMesh('pep')});}}
  else if(it==='oil'){if(back)hazards.push({x:k.x-Math.cos(k.ma)*24,y:k.y-Math.sin(k.ma)*24,t:30,born:0,owner:k,armed:false,mesh:itemMesh('oil')});
    else{const v=Math.max(0,k.speed)+150;projectiles.push({type:'lob',x:k.x+ca*8,y:k.y+sa*8,vx:ca*v,vy:sa*v,t:.6,t0:.6,owner:k,safe:9,b:0,mesh:itemMesh('lob')});}}
  else if(it==='dough'){const tg=back?(st[i+1]||null):(i>0?st[i-1]:null),dir=back?-1:1,v=back?280:300+Math.max(0,k.speed)*.5;
    projectiles.push({type:'dough',x:k.x+ca*10*dir,y:k.y+sa*10*dir,vx:ca*v*dir,vy:sa*v*dir,t:6,owner:k,safe:.3,target:tg,b:0,mesh:itemMesh('dough')});}
  else if(it==='trio'){for(const off of [-.17,0,.17]){const an=k.a+off+(back?Math.PI:0),v=back?240:300+Math.max(0,k.speed);projectiles.push({type:'pep',x:k.x+Math.cos(an)*12,y:k.y+Math.sin(an)*12,vx:Math.cos(an)*v,vy:Math.sin(an)*v,t:4,owner:k,safe:.35,b:0,mesh:itemMesh('pep')});}}
  else if(it==='garlic'){k.shield=6;}
  else if(it==='flour'){if(back)projectiles.push({type:'flour',x:k.x-Math.cos(k.ma)*18,y:k.y-Math.sin(k.ma)*18,vx:0,vy:0,t:.3,t0:.3,owner:k,safe:9,b:0,mesh:itemMesh('flour')});
    else{const v=Math.max(0,k.speed)+170;projectiles.push({type:'flour',x:k.x+ca*10,y:k.y+sa*10,vx:ca*v,vy:sa*v,t:.75,t0:.75,owner:k,safe:9,b:0,mesh:itemMesh('flour')});}}
  else if(it==='wheel'){projectiles.push({type:'wheel',x:k.x,y:k.y,vx:0,vy:0,t:16,owner:k,safe:9,b:0,target:st[0]===k?null:st[0],prog:k.prog+2,lat:lateral(k),spin:0,dir:k.a,mesh:itemMesh('wheel')});}
  else if(it==='rush'){k.rush=3.2;k.boost=Math.max(k.boost,3.2);k.drift=0;}
  else if(it==='freezer'){for(let j=0;j<i;j++){const o=st[j];if(o.shield>0||o.rush>0||o.loop||o.absT>0)continue;if(absorb(o))continue;o.frozen=2.8;burst(o.x,o.rz||o.wy,o.y,18,['#bfe6ff','#ffffff','#7fd0ff'],50,2.6);spawnRing(o.x,(o.wy||0)+.6,o.y,'#8fd8ff',26,.5);}spawnRing(k.x,(k.wy||0)+.6,k.y,'#bfe6ff',60,.7);}
  if(it==='chili'||it==='rush'){if(k===player)SFX.chili();}else if(it==='garlic'){if(near(k)>0)SFX.garlic(near(k));}else if(it==='freezer'){SFX.freeze();}else if(it==='wheel'){SFX.wheel(near(k)||.4);}else if(near(k)>0)(back?SFX.throwB:SFX.throwF)();
}
function stepKart(k,inp,dt){
  k.inv=Math.max(0,k.inv-dt);if(k.trickT>0)k.trickT-=dt;
  const dPress=inp.brake&&!k.pd;k.pd=inp.brake;if(k.gripT>0)k.gripT-=dt;
  if(k.loop){loopStep(k,dt);return;}
  if(k.air&&k.big&&dPress&&!k.trick){k.trick=true;k.trickT=.45;if(k===player)SFX.trick();}
  const lat=Math.abs(lateral(k)),sm=k.sm;let tp=lat<RW?1:lat<CURB?.86+.02*sm.off:clamp(.58+.06*sm.off,.4,.82);if(k.glide)tp=1;if(k.sc)tp=.96;if(k.boost>0)tp=Math.max(tp,.93);k.sf=k.sc?1:lat<RW?2:lat<CURB?1:0;
  k.pen+=(tp-k.pen)*Math.min(1,dt*(tp<k.pen?3.5:6));
  let max=BASE_MAX*inp.mul*k.pen*sm.spd*(k.glide?k.gair||1:1);if(k.boost>0){k.bAge=(k.pBoost>0?(k.bAge||0)+dt:0);max*=1.58;k.boost-=dt;}else k.bAge=9;k.pBoost=k.boost;if(k.dWant>0)k.dWant-=dt;if(k.shield>0){k.shield-=dt;max*=1.08;}if(k.absT>0)k.absT-=dt;if(k.rush>0){k.rush-=dt;max*=1.12;k.pen=Math.max(k.pen,.95);}if(k.cannonT>0)max*=1.22;if(k.shrinkT>0)max*=.78;if(k.sauceT>0)max*=.93;if(k.frozen>0){k.frozen-=dt;max*=.55;}
  const v0=k.speed;
  if(k.spin>0){k.spin-=dt;k.a+=14*dt;k.speed+=(0-k.speed)*Math.min(1,2.5*dt);if(k.spin<=0){k.spin=0;k.a=k.ma;}k.brake=0;}
  else{
    const rate=inp.steer===0?5:(k.steer!==0&&Math.sign(inp.steer)!==Math.sign(k.steer)?7:3.2);
    k.steer+=clamp(inp.steer-k.steer,-rate*dt,rate*dt);
    if(!inp.brake)k.bLock=false;if(dPress&&!k.air&&Math.abs(k.speed)>55)k.bLock=true;
    k.brake+=((inp.brake&&!k.drift&&!k.bLock?1:0)-k.brake)*Math.min(1,dt*9);
    if(k.brake>.04){if(k.speed>2)k.speed-=200*k.brake*dt;else k.speed=Math.max(-55,k.speed-100*k.brake*dt);}
    else if(k.speed<max){const f=1-.72*clamp(k.speed/max,0,1);k.speed=Math.min(max,k.speed+(ACCEL*sm.acc*(k.boost>0?2.8:1)*f+(k.speed<0?220:0))*dt);}
    else k.speed+=(max-k.speed)*Math.min(1,dt*1.5);
    if(!k.air){const ca=Math.cos(k.ma),sa=Math.sin(k.ma),sl=(groundAt(k.x+ca*5,k.y+sa*5)-groundAt(k.x-ca*5,k.y-sa*5))/10;k.speed-=sl*165*dt;}
    const sp=Math.abs(k.speed),dir=(k.speed<0?-1:1)*(k.air&&k.big?.35:1);
    const hs=clamp((sp-40)/(BASE_MAX-40),0,1),lo=sp<1?0:Math.min(1,sp/35),tfN=lo*(1-.66*hs)*((k.isPlayer&&!k.auto)?1:1.4)*sm.hnd,tfD=lo*(1-.4*hs)*sm.hnd;
    let dRel=false;if(dPress&&k.drift&&!k.air)dRel=true;else{if(dPress&&!k.drift)k.dWant=.6;if(k.dWant>0&&inp.brake)k.dWant=Math.max(k.dWant,.12);
      if(k.dWant>0&&!k.drift&&!k.air&&sp>55&&!(k.boost>0&&k.bAge<.8)){k.dWant=0;k.drift=1;k.charge=0;k.dAmt=0;k.tier=0;k.dTime=0;k.sT=0;k.air=true;k.big=false;k.airT=0;k.wvy=(k.gRate||0)+18;if(k===player)SFX.hop();}}
    if(k.drift&&!dRel){k.dTime+=dt;const sl=Math.abs(angDiff(k.a,k.ma));if(k.dTime>.45&&Math.abs(k.steer)<.3&&sl<.14){k.sT+=dt;if(k.sT>.3)dRel=true;}else k.sT=0;}
    if(k.drift){
      if(dRel||sp<35){const tier=k.charge>2.6?3:k.charge>1.6?2:k.charge>.8?1:0;
        if(tier){k.boost=Math.max(k.boost,[0,.55,.9,1.3][tier]);k.pBoost=k.boost;k.bAge=9;if(k===player)SFX.boost(tier);if(k===camT)shake(.15+tier*.05);}k.drift=0;k.charge=0;k.gripT=.5;}
      else{k.dAmt=Math.min(1,(k.dAmt||0)+dt*1.75);const da=k.dAmt*k.dAmt*(3-2*k.dAmt);k.a+=k.steer*TURN*(tfN+(tfD-tfN)*da)*dt*dir;k.speed-=3*dt;k.charge+=dt*(.5+1*Math.abs(k.steer))*(.35+.65*da);
        const tr=k.charge>2.6?3:k.charge>1.6?2:k.charge>.8?1:0;if(tr>(k.tier||0)){k.tier=tr;if(k===player)SFX.tier(tr);}}
    }else k.a+=k.steer*TURN*tfN*dt*dir;
    {const dA=k.dAmt||0,da=dA*dA*(3-2*dA);k.ma+=angDiff(k.a,k.ma)*Math.min(1,(k.drift?9-5*da:k.gripT>0?5:9)*dt);const sl=angDiff(k.a,k.ma);if(Math.abs(sl)>.5)k.ma=k.a-Math.sign(sl)*.5;}
  }
  k.acc+=((k.speed-v0)/dt-k.acc)*Math.min(1,dt*6);
  k.x+=Math.cos(k.ma)*k.speed*dt;k.y+=Math.sin(k.ma)*k.speed*dt;
  scStep(k);
  {const pj=track[k.idx],lt=(k.x-pj.x)*pj.nx+(k.y-pj.y)*pj.ny,sg=lt<0?-1:1,lim=pj.wall===sg?CURB+7:pj.pond===sg?CURB+2*POND.GR*POND.SZ+30:WALLD-3.5;if(!pj.open&&!k.glide&&!k.loop&&!k.sc&&lt*sg>lim&&!SHORTS.some(sc=>sc.s===sg&&lt*sg<WALLD+30&&Math.min(Math.abs(k.idx-sc.a)%N,N-Math.abs(k.idx-sc.a)%N)<=3)){const ov=lt*sg-lim,nx=pj.nx*sg,ny=pj.ny*sg;k.x-=nx*ov;k.y-=ny*ov;
    const vx=Math.cos(k.ma),vy=Math.sin(k.ma),dot=vx*nx+vy*ny;if(dot>0){if(k===camT&&dot>.3)shake(.25);k.speed*=1-.22*dot;const tx=vx-dot*nx,ty=vy-dot*ny;if(Math.hypot(tx,ty)>.05){const na=Math.atan2(ty,tx);k.ma=na;k.a+=angDiff(na,k.a)*.5;}if(dot>.45&&k.wallT<=0){k.wallT=.35;if(k===player)SFX.bump(.7);sparkWall(k,nx,ny);}}}}
  {const pj=track[k.idx];if(pj.flo!==undefined&&!k.loop&&!k.glide&&!k.sc){const lt=(k.x-pj.x)*pj.nx+(k.y-pj.y)*pj.ny;let ov=0,sg=0;if(lt<pj.flo){ov=pj.flo-lt;sg=-1;}else if(lt>pj.fhi){ov=lt-pj.fhi;sg=1;}
    if(ov>0){const nx=pj.nx*sg,ny=pj.ny*sg;k.x-=nx*ov;k.y-=ny*ov;const vx=Math.cos(k.ma),vy=Math.sin(k.ma),dot=vx*nx+vy*ny;if(dot>0){k.speed*=1-.15*dot;const tx=vx-dot*nx,ty=vy-dot*ny;if(Math.hypot(tx,ty)>.05){const na=Math.atan2(ty,tx);k.ma=na;k.a+=angDiff(na,k.a)*.5;}if(dot>.45&&k.wallT<=0){k.wallT=.35;if(k===player)SFX.bump(.6);sparkWall(k,nx,ny);}}}}}
  if(k.wallT>0)k.wallT-=dt;
  const d=Math.hypot(k.x,k.y);if(d>RIM){const nx=k.x/d,ny=k.y/d;k.x=nx*RIM;k.y=ny*RIM;const vx=Math.cos(k.ma),vy=Math.sin(k.ma),dot=vx*nx+vy*ny;
    if(dot>0){if(k===camT&&dot>.25)shake(.3);k.speed*=1-.35*dot;const tx=vx-dot*nx,ty=vy-dot*ny;if(Math.hypot(tx,ty)>.05){const na=Math.atan2(ty,tx);k.ma=na;k.a+=angDiff(na,k.a)*.6;}}}
  let G=groundAt(k.x,k.y),onR=false,gR=false;
  if(!k.sc&&!(GLIDE&&k.idx>=GLIDE.j0&&k.idx<GLIDE.j1)){const la=Math.abs(lateral(k));if(la>RW&&la<CURB)G+=kerbH(la);}
  for(const r of ramps){const p0=track[r.j],dx=k.x-p0.x,dy=k.y-p0.y,al=dx*p0.tx+dy*p0.ty;if(al<0||al>r.len)continue;if(Math.abs(dx*p0.nx+dy*p0.ny)>r.w)continue;const hh=r.h*al/r.len;if(k.wy<=G+hh+1.5){G+=hh;onR=true;gR=!!r.glide;}}
  const rate=(G-(k.lastG===undefined?G:k.lastG))/dt;k.lastG=G;
  if(k.air&&!k.glide&&k.onGlide&&!gR&&k.speed>20){startGlide(k);k.wvy=Math.max(30,k.wvy);}
  if(k.air){k.airT+=dt;if(k.glide){k.wvy-=70*dt;const sk=-(k.gsink||15);if(k.wvy<sk)k.wvy+=(sk-k.wvy)*Math.min(1,dt*4);if(GLIDE){const gyy=glideY(k.x,k.y);if(G<gyy-20&&k.wy<gyy+6&&k.wvy<0)k.wvy*=.8;}glideRings(k);}else k.wvy-=(k.big?(k.wvy>0?80:110):260)*dt;
    k.wy+=k.wvy*dt;if(k.wy<=G){k.wy=G;k.air=false;if(k.big||k.glide)land(k);k.big=false;k.glide=false;k.wvy=rate;k.gRate=rate;}}
  else if(k.onRamp&&!onR&&k.speed>20){k.air=true;k.big=true;k.airT=0;k.wvy=32+Math.min(Math.max(0,k.speed),BASE_MAX*1.6)*.05+(trainRamp(k)?16:0);k.speed=Math.max(k.speed,BASE_MAX*.9);k.trick=false;k.drift=0;
    if(k.onGlide)startGlide(k);
    k.wy+=k.wvy*dt;}
  else if(rate<k.gRate-260*dt*1.1&&k.speed>60){k.air=true;k.big=(k.gRate-rate)>55;k.airT=0;k.wvy=Math.min(k.gRate,42);k.wy+=k.wvy*dt;}
  else{k.wy=G;k.gRate=rate;}
  k.onRamp=onR;k.onGlide=gR;k.z=Math.max(0,k.wy-G);
  if(GLIDE&&k.wy<glideY(k.x,k.y)-32&&pitAt(k.x,k.y)>25){respawn(k);return;}
  for(const o of obstacles){const dx=k.x-o.x,dy=k.y-o.y,d2=dx*dx+dy*dy,rr=o.r+8.5;if(d2<rr*rr&&k.z<o.h){const dd=Math.sqrt(d2)||.01,nx=dx/dd,ny=dy/dd;k.x=o.x+nx*rr;k.y=o.y+ny*rr;
    const vx=Math.cos(k.ma),vy=Math.sin(k.ma),dot=vx*nx+vy*ny;if(dot<0){k.speed*=1+.5*dot;const tx=vx-dot*nx,ty=vy-dot*ny;if(Math.hypot(tx,ty)>.05){const na=Math.atan2(ty,tx);k.ma=na;k.a+=angDiff(na,k.a)*.6;}
      if(-dot>.3){if(k===camT)shake(.5);burst(o.x+nx*o.r,6,o.y+ny*o.r,8,['#fff4dc','#ffe066'],30,2);SFX.bump(near(k));}}}}
  if(inp.use&&k.item&&k.spin<=0)useItem(k,inp.back);
  if(k.roll>0){k.roll-=dt;if(k.roll<=0){while(k.pend.length){const it=k.pend.shift();if(!k.item)k.item=it;else if(!k.item2)k.item2=it;}const df=DIFFS[player?aiKey():'normal'];k.ai.itemDelay=df.delay[0]+Math.random()*(df.delay[1]-df.delay[0]);if(k===player){SFX.ready();itemBtn.classList.remove('pop');void itemBtn.offsetWidth;itemBtn.classList.add('pop');}}}
  const oIdx=k.idx;let best=k.idx,bd=1e18;if(!k.sc)for(let o=-12;o<=20;o++){const j=(k.idx+o+N)%N,p=track[j],dd=(p.x-k.x)**2+(p.y-k.y)**2;if(dd<bd){bd=dd;best=j;}}
  let di=best-k.idx;if(di>N/2)di-=N;if(di<-N/2)di+=N;k.prog+=di;k.idx=best;
  for(const LOOP of LOOPS)if(!k.air&&k.speed>50&&k.spin<=0&&!k.loop){let d0=oIdx-LOOP.j,d1=k.idx-LOOP.j;if(d0>N/2)d0-=N;if(d0<-N/2)d0+=N;if(d1>N/2)d1-=N;if(d1<-N/2)d1+=N;
    if(d0<0&&d1>=0){const lt=lateral(k);if(LOOP.full||Math.abs(lt-LOOP.lat0)<17){k.loop={th:0,p:LOOP.p,lat0:LOOP.full?clamp(lt,LOOP.lat0-LOOP.W+4,LOOP.lat0+LOOP.W-4):LOOP.lat0,shift:LOOP.shift,g0:LOOP.g0};k.drift=0;if(k===player)SFX.pad();}}}
  for(const pd of pads){let dj=k.idx-pd.j;if(dj>N/2)dj-=N;if(dj<-N/2)dj+=N;if(Math.abs(dj)<=2&&Math.abs(lateral(k)-pd.lat)<16&&k.boost<.9){k.boost=Math.max(k.boost,1.0);if(k===camT)shake(.25);if(k===player)SFX.pad();}}
}
function startGlide(k){const gd=GLIDERS[k.spec.g];k.air=true;k.glide=true;k.big=false;k.trick=false;k.drift=0;k.speed=Math.max(k.speed,BASE_MAX*.85);k.wvy=55+k.speed*.08;k.gRings=0;k.gsink=gd.sink;k.gair=gd.air;if(k===player){SFX.glide();showBanner('Glide!',.9);}}
function glideRings(k){const G=GLIDE;if(!G||!G.rings)return;for(let i=0;i<G.rings.length;i++){if(k.gRings&(1<<i))continue;const r=G.rings[i],dx=k.x-r.x,dz=k.y-r.z,al=dx*G.ux+dz*G.uy;if(Math.abs(al)>7)continue;
  if(Math.abs(dz*G.ux-dx*G.uy)<15&&Math.abs(k.wy+4-r.y)<15){k.gRings|=1<<i;k.boost=Math.max(k.boost,.7);spawnRing(r.x,r.y,r.z,'#7fe8ff',30,.5,false);if(k===player){SFX.ring();shake(.15);}}}}
function respawn(k){const j=(GLIDE.rj-24+N)%N,p=track[j];let di=j-k.idx;if(di>N/2)di-=N;if(di<-N/2)di+=N;k.prog+=di;k.idx=j;
  k.x=k.px=p.x;k.y=k.py=p.y;k.a=k.ma=k.pa=k.pma=p.ang;k.speed=BASE_MAX*.5;k.wy=k.pwy=k.lastG=groundAt(p.x,p.y);k.wvy=0;k.gRate=0;k.air=false;k.big=false;k.glide=false;k.onRamp=k.onGlide=false;
  k.drift=0;k.charge=0;k.boost=0;k.spin=0;k.inv=2;k.z=k.pz=0;if(k===camT){camSnap=true;shake(.4);}if(k===player){showBanner('Oops!',1.2);SFX.bump(1);}spawnRing(p.x,k.wy+.6,p.y,'#7fe8ff',40,.6);}
function update(dt){
  standCache=standings();simTime+=dt;
  for(const r of rollers){const p=track[r.j];r.lat=Math.sin(simTime*1.05+r.ph)*(RW+6);r.x=p.x+p.nx*r.lat;r.y=p.y+p.ny*r.lat;
    for(const k of karts){if(!k.loop&&k.z<14&&(k.x-r.x)**2+(k.y-r.y)**2<306)spinOut(k,'meat',1);}}
  updateHazards(dt);itemsTick(dt);abilityTick(dt);if(abilQueued){abilQueued=false;if(player&&state==='race')useAbility(player);}
  for(const k of karts){k.px=k.x;k.py=k.y;k.pa=k.a;k.pma=k.ma;k.pz=k.z;k.pwy=k.wy;k.pth=k.loopTh||0;const inp=(k.isPlayer&&!k.auto&&!(k.rush>0))?playerInput():aiInput(k,dt);if(k.rush>0)inp.use=false;stepKart(k,inp,dt);}
  for(let i=0;i<karts.length;i++)for(let j=i+1;j<karts.length;j++){const a=karts[i],b=karts[j];const dx=b.x-a.x,dy=b.y-a.y,d2=dx*dx+dy*dy;
    if(d2<361&&d2>0&&!a.loop&&!b.loop){const sa2=a.shield>0||a.rush>0,sb2=b.shield>0||b.rush>0;if(sa2&&!sb2)spinOut(b,'garlic');else if(sb2&&!sa2)spinOut(a,'garlic');const d=Math.sqrt(d2),p=(19-d)/2,nx=dx/d,ny=dy/d,wa=a.sm.wgt,wb=b.sm.wgt,ra=1.6*wb/(wa+wb),rb=1.6*wa/(wa+wb);a.x-=nx*p*ra;a.y-=ny*p*ra;b.x+=nx*p*rb;b.y+=ny*p*rb;if(wa>wb*1.15)b.speed*=.992;else if(wb>wa*1.15)a.speed*=.992;
      if(a.boost>0&&b.boost<=0)b.speed*=.97;else if(b.boost>0&&a.boost<=0)a.speed*=.97;}}
  for(const b of boxes){if(b.r>0){b.r-=dt;continue;}for(const k of karts){if((k.x-b.x)**2+(k.y-b.y)**2<270){b.r=4;burst(b.x,6,b.y,26,['#ffe066','#e0452c','#fff4dc','#7fd0ff'],60,2.4);
    const cap=2-(k.item?1:0)-(k.item2?1:0)-k.pend.length,give=Math.min(cap,b.dbl?2:1);for(let g2=0;g2<give;g2++)k.pend.push(rollItem(standCache.indexOf(k)));if(give>0&&k.roll<=0)k.roll=k===player?1.1:.5;boxFx(b,k);break;}}}
  /* two items from different racers that meet cancel out, so a slice dropped behind you can stop whatever is chasing you */
  for(let i=projectiles.length-1;i>=0;i--){const a=projectiles[i];if(a.type==='flour'||a.type==='lob')continue;for(let j=i-1;j>=0;j--){const b=projectiles[j];if(b.owner===a.owner||b.type==='flour'||b.type==='lob')continue;
      const r=(a.type==='wheel'||b.type==='wheel')?20:15;if((a.x-b.x)**2+(a.y-b.y)**2<r*r){const gy=groundAt(a.x,a.y)+6;burst((a.x+b.x)/2,gy,(a.y+b.y)/2,26,['#ffe066','#ff8a1f','#ffffff'],90,3);spawnRing((a.x+b.x)/2,gy-5,(a.y+b.y)/2,'#ffcf6a',30,.4);SFX.clash(near({x:a.x,y:a.y}));a.t=0;b.t=0;a.dead=b.dead=1;break;}}}
  for(let i=projectiles.length-1;i>=0;i--){const p=projectiles[i];if(p.dead){scene.remove(p.mesh);projectiles.splice(i,1);continue;}if(p.custom){if(itemsProj(p,dt)){scene.remove(p.mesh);projectiles.splice(i,1);}continue;}p.t-=dt;p.safe-=dt;
    if(p.type==='dough'&&p.target){const tg=p.target,dd=Math.hypot(tg.x-p.x,tg.y-p.y),des=Math.atan2(tg.y-p.y,tg.x-p.x);let cur=Math.atan2(p.vy,p.vx);const tr=dd<70?9:5.5;cur+=clamp(angDiff(des,cur),-tr*dt,tr*dt);
      /* a homing dough ball always closes the gap: it runs comfortably faster than whoever it is chasing */
      let v=Math.hypot(p.vx,p.vy);const want=Math.max(300,Math.abs(tg.speed||0)*1.22+70);v+=(want-v)*Math.min(1,dt*3);p.vx=Math.cos(cur)*v;p.vy=Math.sin(cur)*v;}
    p.x+=p.vx*dt;p.y+=p.vy*dt;
    const d=Math.hypot(p.x,p.y);if(d>RIM){const nx=p.x/d,ny=p.y/d,dot=p.vx*nx+p.vy*ny;p.vx-=2*dot*nx;p.vy-=2*dot*ny;p.x=nx*(RIM-1);p.y=ny*(RIM-1);if(++p.b>3)p.t=0;}
    if(p.type==='wheel'){const tg=p.target;p.spin+=dt*22;
      if(tg&&!tg.loop&&tg.prog-p.prog>5){p.prog+=dt*Math.max(450/8,Math.abs(tg.speed||0)/(T.L/N)*1.35+18);const j=((Math.floor(p.prog)%N)+N)%N,q=track[j];p.lat+=(0-p.lat)*Math.min(1,dt*2);const nx=q.x+q.nx*p.lat,ny=q.y+q.ny*p.lat;p.dir=Math.atan2(ny-p.y,nx-p.x);p.x=nx;p.y=ny;}
      else if(tg&&!tg.loop){const dx=tg.x-p.x,dy=tg.y-p.y,dd=Math.hypot(dx,dy)||1,v=Math.max(520,Math.abs(tg.speed||0)*1.5+90)*dt;p.dir=Math.atan2(dy,dx);p.x+=dx/dd*Math.min(v,dd);p.y+=dy/dd*Math.min(v,dd);
        if(dd<16){spinOut(tg,'wheel');if(tg.inv>1.8)tg.speed*=.5;spawnRing(tg.x,(tg.wy||0)+.6,tg.y,'#ff3b1a',60,.7);burst(tg.x,(tg.wy||0)+8,tg.y,40,['#ff3b1a','#ffe066','#ffffff'],110,4);p.t=0;}}
      else if(!tg){p.prog+=dt*450/8;const j=((Math.floor(p.prog)%N)+N)%N,q=track[j];p.x=q.x;p.y=q.y;}
      if(p.t<=0){scene.remove(p.mesh);projectiles.splice(i,1);}continue;}
    if(p.type==='flour'){if(p.t<=0){const fy=groundAt(p.x,p.y);for(const k of karts){if(k===p.owner||k.loop)continue;if((k.x-p.x)**2+(k.y-p.y)**2<38*38)spinOut(k,'flour');}
        for(let n=0;n<26;n++){const a=Math.random()*Math.PI*2,u=.3+Math.random()*.7;FXN.spawn(p.x+Math.cos(a)*6,fy+4,p.y+Math.sin(a)*6,Math.cos(a)*60*u,10+Math.random()*24,Math.sin(a)*60*u,'#f6f1e6',8,26,1.4,-3,1.2);}
        spawnRing(p.x,fy+.8,p.y,'#ffffff',50,.6);FXA.spawn(p.x,fy+6,p.y,0,0,0,'#ffffff',46,10,.2,0,0);SFX.boom(near({x:p.x,y:p.y}));if(Math.hypot(p.x-camera.position.x,p.y-camera.position.z)<120)shake(.5);
        scene.remove(p.mesh);projectiles.splice(i,1);}continue;}
    if(p.type==='lob'){if(p.t<=0&&overPit(p.x,p.y)){scene.remove(p.mesh);projectiles.splice(i,1);continue;}if(p.t<=0){hazards.push({x:p.x,y:p.y,t:30,born:0,owner:p.owner,armed:false,mesh:itemMesh('oil')});scene.remove(p.mesh);projectiles.splice(i,1);}continue;}
    let hit=false;for(const k of karts){if(k.loop||(k===p.owner&&p.safe>0))continue;if((k.x-p.x)**2+(k.y-p.y)**2<200&&k.inv<=0){spinOut(k,p.type);hit=true;break;}}
    for(const h of hazards){if((h.x-p.x)**2+(h.y-p.y)**2<100){h.t=0;hit=true;}}
    if(hit||p.t<=0){scene.remove(p.mesh);projectiles.splice(i,1);}}
  for(let i=hazards.length-1;i>=0;i--){const h=hazards[i];if(h.born===0&&overPit(h.x,h.y))h.t=0;h.t-=dt;h.born+=dt;
    if(!h.armed&&(!h.owner||(h.owner.x-h.x)**2+(h.owner.y-h.y)**2>34*34))h.armed=true;
    for(const k of karts){if(k.loop||(k===h.owner&&!h.armed))continue;if((k.x-h.x)**2+(k.y-h.y)**2<200&&k.inv<=0){spinOut(k,'oil');h.t=0;break;}}
    if(h.t<=0){scene.remove(h.mesh);hazards.splice(i,1);}}
  for(const k of karts){if(state==='race'&&!k.finished&&k.prog>=LAPS*N){k.finished=true;k.finishTime=raceTime;k.place=++finishCount;if(k===player)onPlayerFinish();}}
  if(state==='race')raceTime+=dt;
}

/* ================= RENDER ================= */
const tv=new THREE.Vector3(),tv2=new THREE.Vector3(),v2=new THREE.Vector2();
function syncKart(k,dt,time){
  const m=k.m,x=k.px+(k.x-k.px)*alpha,y=k.py+(k.y-k.py)*alpha,z=k.pwy+(k.wy-k.pwy)*alpha,a=lerpA(k.pa,k.a,alpha);k.rx=x;k.ry=y;k.rz=z;k.rma=lerpA(k.pma,k.ma,alpha);
  const lth=k.loopTh?(k.pth>0?k.pth+(k.loopTh-k.pth)*alpha:k.loopTh):0;k.rth=lth;{let rg=groundAt(x,y);if(GLIDE){const gyy=glideY(x,y);if(rg<gyy-20)rg=Math.min(z,gyy);}k.rg=rg;}
  m.g.position.set(x,z,y);
  if(!lth){if(!k.air){const ca=Math.cos(a),sa=Math.sin(a),fF=Math.max(6,m.axF||6),fR=Math.min(-6,m.axR||-6),fW=Math.max(5,m.axW||5),J=k.idx,hF=surfH(x+ca*fF,y+sa*fF,J),hB=surfH(x+ca*fR,y+sa*fR,J),hL=surfH(x-sa*fW,y+ca*fW,J),hRt=surfH(x+sa*fW,y-ca*fW,J),hC=surfH(x,y,J),
      sF=(hF-hB)/(fF-fR),sR=(hL-hRt)/(2*fW),ff=Math.min(1,16*dt),mid=hB+(hF-hB)*(-fR)/(fF-fR),base=Math.max(hC,mid,(hL+hRt)/2);m.g.position.y=k.onRamp||k.z>.4?Math.max(z,base):clamp(base,z-1.2,z+6);
    m.tp=(m.tp||0)+(Math.atan(sF)-(m.tp||0))*ff;m.tr=(m.tr||0)+(-Math.atan(sR)-(m.tr||0))*ff;}else{m.tp=(m.tp||0)*.97;m.tr=(m.tr||0)*.97;}m.g.rotation.set(m.tr,-a,m.tp);}
  else m.g.rotation.set(0,-a,lth);
  if(k.sink!=null)m.g.position.y-=Math.min(14,(k.sinkT||0)*22);
  const cd2=(x-camera.position.x)**2+(y-camera.position.z)**2,far=k!==camT&&cd2>(m.isFar?LODF-20:LODF)**2;if(m.mid){const md=k!==camT&&!far;setMid(m,md);}if(far!==m.isFar){m.isFar=far;m.tilt.visible=!far;m.lo.visible=far;for(const w of m.wheels)w.spin.parent.visible=!far;}
  {const nh=k!==camT&&cd2<196;if(m.g.visible===nh)m.g.visible=!nh;}/* a rival right on top of the camera would fill the screen: hide it until it moves away */
  if(m.ice){const fz=k.frozen>0;if(fz!==m.ice.visible)m.ice.visible=fz;if(fz){m.ice.scale.setScalar(m.iceS*Math.min(1,.25+(2.8-k.frozen)*6)*(k.frozen<.25?k.frozen*4:1));m.ice.rotation.y=Math.sin(time*1.5)*.05;}}
  {const gt=k.glide?1:0;m.ga+=(gt-m.ga)*Math.min(1,dt*(gt?5:8));const gv=m.ga>.02;if(gv!==m.gl.visible)m.gl.visible=gv;if(gv){m.gl.scale.setScalar(m.ga);m.gl.rotation.set(-k.steer*.18,0,Math.sin(time*2.2+k.ri)*.06);}}
  if(far)return;
  const f=Math.min(1,8*dt);if(k.trickT>0){m.tilt.rotation.x=(1-k.trickT/.45)*Math.PI*2;m.trickOn=true;}else{if(m.trickOn){m.tilt.rotation.x=0;m.trickOn=false;}m.tilt.rotation.x+=(((k.drift?k.steer*.08*(k.dAmt||0):0)+k.steer*.04)-m.tilt.rotation.x)*f;}
  m.tilt.rotation.z+=(clamp(k.acc*.0006,-.07,.05)-m.tilt.rotation.z)*f;
  for(const w of m.wheels)w.spin.rotation.z-=k.speed*dt/(w.r*KS);
  for(const fw of m.front)fw.rotation.y=-k.steer*.42;
  m.drv.rotation.x=-k.steer*.14;m.drv.position.y=m.drvY+Math.sin(time*18+k.ri)*.03*Math.min(1,Math.abs(k.speed)/100);
  m.tailM.emissiveIntensity=m.flash?(Math.floor(time*7+k.ri)%2?3.2:.4):.8+k.brake*3;if(m.flash)m.flash.emissiveIntensity=Math.floor(time*7+k.ri)%2?.3:3.2;
  {const shOn=(k.shield>0&&(k.shield>1.2||Math.floor(time*10)%2===0))||k.shL>0,ruOn=k.rush>0;if(m.bub.userData.cl)m.bub.userData.cl.visible=!(k.shL===1&&!(k.shield>0));m.bub.visible=shOn||ruOn;if(m.bub.visible){m.bub.material=shOn?bubbleMat:bubRushMat;if(m.bub.userData.cl)m.bub.userData.cl.visible=shOn;m.bub.rotation.y+=dt*(shOn?2:4);}}
  if(k.frozen>0&&Math.random()<.5)FXA.spawn(x+(Math.random()-.5)*10,z+8*KS,y+(Math.random()-.5)*10,0,-6,0,'#bfe6ff',2.4,.6,.5,0,0);
  if(k.shield>0&&Math.random()<.4)FXA.spawn(x+(Math.random()-.5)*12,z+2+Math.random()*10,y+(Math.random()-.5)*12,0,8,0,'#7fe07a',1.8,.4,.5,0,0);
  const on=k.boost>0;for(const fl of m.flames){fl.visible=on;if(on)fl.scale.set(1,.8+Math.random()*.5,1);}
  if(k.spin>0){for(let i=0;i<3;i++){const an=time*9+i*2.094;FXA.spawn(x+Math.cos(an)*4.5*KS,z+(m.top+2.3)*KS,y+Math.sin(an)*4.5*KS,0,0,0,'#ffe066',2.2,1.2,.07,0,0);}}
  if((x-camera.position.x)**2+(y-camera.position.z)**2>260*260)return;
  k.fx+=dt*60;const n=Math.min(4,Math.floor(k.fx));k.fx-=Math.floor(k.fx);
  for(let i=0;i<n;i++){
    if(k.drift&&k.charge>.3){const tier=k.charge>2.6?3:k.charge>1.6?2:k.charge>.8?1:0;for(const v of m.fxL){tv.copy(v);m.g.localToWorld(tv);FXA.spawn(tv.x,tv.y+.3,tv.z,(Math.random()-.5)*24-Math.cos(k.ma)*20,12+Math.random()*26,(Math.random()-.5)*24-Math.sin(k.ma)*20,SPARKC[tier],tier?1.5:1,.3,.28,70,1);}
      if(i%3===0){tv.copy(m.fxL[Math.random()<.5?0:1]);m.g.localToWorld(tv);FXN.spawn(tv.x,tv.y+.6,tv.z,(Math.random()-.5)*6,4+Math.random()*4,(Math.random()-.5)*6,'#f2ebe0',2.5,8,.8,-2,1.5);}}
    if(on&&i%2===0){for(const v of m.fxP){tv.copy(v);m.g.localToWorld(tv);FXA.spawn(tv.x,tv.y,tv.z,-Math.cos(k.ma)*30+(Math.random()-.5)*6,(Math.random()-.2)*6,-Math.sin(k.ma)*30+(Math.random()-.5)*6,Math.random()<.5?'#ff7a1a':'#ffd36b',2.2,.4,.25,0,2);}}
    if(m.smoke&&i===0&&Math.random()<.3){tv.copy(m.smoke);m.g.localToWorld(tv);FXN.spawn(tv.x,tv.y,tv.z,(Math.random()-.5)*4,8+Math.random()*6,(Math.random()-.5)*4,'#9a918a',2.5,9,1.4,-1,1.5);}
    if(k.glide&&i%2===0){FXA.spawn(x+(Math.random()-.5)*14,z+(m.top-1)*KS*Math.random(),y+(Math.random()-.5)*14,-Math.cos(k.ma)*70,0,-Math.sin(k.ma)*70,'#e8f8ff',1.4,.35,.25,0,0);}
    if(k.sf===0&&!k.air&&Math.abs(k.speed)>60&&i%3===0){tv.copy(m.fxL[Math.random()<.5?0:1]);m.g.localToWorld(tv);FXN.spawn(tv.x,tv.y+.5,tv.z,(Math.random()-.5)*10,5+Math.random()*6,(Math.random()-.5)*10,'#f2cf6a',2,7,.7,-1,1.5);}
  }
}

/* soft contact shadow under each kart: one instanced draw for the whole field */
let CSH=null;const _cm=new THREE.Matrix4(),_cq=new THREE.Quaternion(),_ce=new THREE.Euler(0,0,0,'YZX'),_cv=new THREE.Vector3(),_cs=new THREE.Vector3();
function contactShadows(){if(!karts.length)return;if(!CSH||CSH.count<karts.length){if(CSH){scene.remove(CSH);}
    const c=cnv(128,128),g=c.getContext('2d'),gr=g.createRadialGradient(64,64,4,64,64,62);gr.addColorStop(0,'rgba(0,0,0,.62)');gr.addColorStop(.55,'rgba(0,0,0,.34)');gr.addColorStop(1,'rgba(0,0,0,0)');g.fillStyle=gr;g.fillRect(0,0,128,128);
    const t=new THREE.CanvasTexture(c);const geo=new THREE.PlaneGeometry(1,1);geo.rotateX(-Math.PI/2);
    CSH=new THREE.InstancedMesh(geo,new THREE.MeshBasicMaterial({map:t,transparent:true,depthWrite:false,polygonOffset:true,polygonOffsetFactor:-6,polygonOffsetUnits:-6,toneMapped:false}),12);CSH.frustumCulled=false;CSH.renderOrder=1;scene.add(CSH);}
  let n=0;for(const k of karts){const m=k.m;if(!m||!m.g.visible||k.sink!=null||k.loop||k.rth)continue;const gy=k.rg??groundAt(k.rx,k.ry),h=Math.max(0,m.g.position.y-gy);if(h>40)continue;
    const f=1-Math.min(1,h/40),L=(m.axF-m.axR+10)*1.05||22,W=(m.axW*2+6)*1.1||16,sc=.7+.6*(1-f);
    _ce.set(m.tr||0,-k.rma,m.tp||0);_cq.setFromEuler(_ce);_cv.set(k.rx,gy+.25,k.ry);_cs.set(L*sc*f+.001,1,W*sc*f+.001);_cm.compose(_cv,_cq,_cs);CSH.setMatrixAt(n++,_cm);}
  CSH.count=n;CSH.instanceMatrix.needsUpdate=true;}
function render(time,dt){
  bubbleMat.uniforms.uT.value=time;bubRushMat.uniforms.uT.value=time;
  for(const k of karts)syncKart(k,dt,time);
  try{contactShadows();}catch(e){}
  if(state==='race')recTick();ghostTick();
  if(camT){cam.a=lerpA(cam.a,camT.rma,1-Math.exp(-5.5*dt));
    const ex=Math.max(0,(camT.m.top||7.2)-7.2)*KS;const CL=CFG.cam!=='far';let dist=(CL?26:39)+(camT.boost>0?(CL?5:4):0)+ex*1.1,h=(CL?11:15.6)+ex*.8;if(state==='countdown'&&!CL){const f=clamp((cd-.4)/3,0,1);dist+=80*f*f;h+=50*f*f;}
    const fx=Math.cos(cam.a),fy=Math.sin(cam.a),cy=camT.glide?camT.rz-4:camT.rg+(camT.rz-camT.rg)*.45;tv2.set(camT.rx-fx*dist,cy+h,camT.ry-fy*dist);
    tv.set(camT.rx+fx*(CL?32:21),cy+(CL?6.2:5.5)+ex*.5,camT.ry+fy*(CL?32:21));
    const inLoop=camT.rth>0;
    if(inLoop){const p=(camT.loop||LOOPS[0]).p,ct=Math.cos(camT.rth),st=Math.sin(camT.rth);cam.F.set(p.tx*ct,st,p.ty*ct).normalize();cam.U.set(-p.tx*st,ct,-p.ty*st);cam.P.set(camT.rx,camT.rz,camT.ry);
      tv2.copy(cam.P).addScaledVector(cam.F,-30).addScaledVector(cam.U,13);tv.copy(cam.P).addScaledVector(cam.F,16).addScaledVector(cam.U,3);
      cam.base.lerp(tv2,1-Math.exp(-16*dt));cam.look.lerp(tv,1-Math.exp(-18*dt));camera.up.lerp(cam.U,1-Math.exp(-12*dt)).normalize();cam.a=p.ang;}
    else{camera.up.lerp(UPV,1-Math.exp(-8*dt)).normalize();
    if(camSnap){cam.base.copy(tv2);cam.look.copy(tv);camSnap=false;}
    else{cam.base.lerp(tv2,1-Math.exp(-12*dt));cam.look.lerp(tv,1-Math.exp(-16*dt));}}
    const spn=Math.min(1.4,Math.abs(camT.speed)/BASE_MAX);let amp=.03+.09*spn+(camT.sf===0&&spn>.25?.32:camT.sf===1&&spn>.25?.12:0)+(camT.boost>0?(CL?.24:.12):0)+(camT.z>0&&!camT.air?0:0)+shakeImp;
    shakeImp*=Math.exp(-6*dt);{const bo=camT.boost>0;if(bo&&!cam.bo&&state==='race')shake(.75);cam.bo=bo;}if(state==='countdown')amp=.02;if(RM)amp*=.25;if(!CFG.shake)amp=0;
    const n1=Math.sin(time*29)*.5+Math.sin(time*47.3+1.3)*.3+Math.sin(time*11.7+.7)*.2,n2=Math.sin(time*33.1+2)*.5+Math.sin(time*53+.4)*.3+Math.sin(time*9.3+1.1)*.2,n3=Math.sin(time*26.7+4)*.5+Math.sin(time*41+2.2)*.5;
    let G=CFG.shake?(RM?.35:1):0;if(state==='countdown'||inLoop||!dt)G=0;
    {const m=camT.m,ff=k=>1-Math.exp(-k*dt);
      /* pitch follows the slope under the kart, plus a nod when speeding up or braking */
      const acc=dt>0?(camT.speed-cam.pspd)/dt:0;cam.pspd=camT.speed;cam.gp+=(((m.tp||0)*.4-clamp(acc*.00016,-.035,.035))*G-cam.gp)*ff(6);
      /* roll leans with the ground camber and into the turn */
      cam.gr+=(((m.tr||0)*.5-camT.steer*.04-(camT.drift?camT.steer*.035*(camT.dAmt||0):0))*G-cam.gr)*ff(5);
      /* the camera swings slightly out of the turn, like it hangs on a boom */
      cam.sx+=(camT.steer*2.4*spn*G-cam.sx)*ff(3);
      /* a sprung vertical mount: drops on landings, lifts on take-off, wobbles over bumps */
      const vz=dt>0?(camT.rz-cam.pvz)/dt:0;cam.pvz=camT.rz;const f=(-cam.oy*55-cam.vy*9)+clamp(-vz*.9,-40,40)*G*(camT.air?.25:1);cam.vy+=f*dt;cam.oy+=cam.vy*dt;cam.oy=clamp(cam.oy,-2.6,2.6);}
    const rx=Math.sin(cam.a),rz=-Math.cos(cam.a);
    camera.position.set(cam.base.x+n1*amp*.3-rx*cam.sx,cam.base.y+n2*amp*.35+cam.oy,cam.base.z+n3*amp*.3-rz*cam.sx);
    camera.lookAt(cam.look.x,cam.look.y+cam.oy*.45,cam.look.z);camera.rotateX(-cam.gp);
    cam.roll=cam.gr;camera.rotateZ(cam.roll+n3*amp*.006);
    const hf=(camT.boost>0?(CL?112:100):(CL?92:90))*Math.PI/180,vf=clamp(2*Math.atan(Math.tan(hf/2)/camera.aspect)*180/Math.PI,52,100);
    if(Math.abs(camera.fov-vf)>.05){camera.fov+=(vf-camera.fov)*Math.min(1,5*dt);camera.updateProjectionMatrix();}
    snapSun(camT.rx+Math.cos(cam.a)*80,camT.rg,camT.ry+Math.sin(cam.a)*80);}
  if(state==='intro')introCam(dt);if(sky)sky.position.copy(camera.position);rimL.position.set(camera.position.x-sunDir.x*400,camera.position.y+260,camera.position.z-sunDir.z*400);rimL.target.position.set(camera.position.x,camera.position.y-40,camera.position.z);
  for(const b of boxes){const vis=b.r<=0||b.r<.35;b.m.visible=b.ring.visible=b.gl.visible=vis;if(!vis)continue;
    const s=b.r>0?1-b.r/.35:1,bob=Math.sin(time*3+b.sv)*.8;b.m.position.set(b.x,b.gy+6.5+bob,b.y);b.m.rotation.set(.3,time*1.6+b.sv,.18);b.m.scale.setScalar(Math.max(.01,s)*(b.dbl?1.25:1));
    b.ring.position.set(b.x,b.gy+6.5+bob,b.y);b.ring.rotation.set(Math.PI/2+Math.sin(time*2+b.sv)*.35,0,time);b.ring.scale.setScalar(Math.max(.01,s)*(b.dbl?1.25:1));}
  for(const p of projectiles){let pg=groundAt(p.x,p.y);if(GLIDE){const gyy=glideY(p.x,p.y);if(pg<gyy-20)pg=gyy+6;}if(p.type==='wheel'){p.mesh.position.set(p.x,pg+7,p.y);p.mesh.rotation.y=-p.dir;p.mesh.userData.disc.rotation.set(Math.PI/2,p.spin,0);if(Math.random()<.6)FXA.spawn(p.x,pg+1,p.y,(Math.random()-.5)*30,10+Math.random()*20,(Math.random()-.5)*30,'#ffb347',1.6,.3,.25,60,1);continue;}if(p.type==='flour'){const f=1-p.t/p.t0;p.mesh.position.set(p.x,pg+3.4+Math.sin(Math.PI*f)*20,p.y);p.mesh.rotation.y+=dt*6;p.mesh.rotation.z=Math.sin(f*Math.PI*2)*.5;continue;}if(p.type==='lob'){const f=1-p.t/p.t0;p.mesh.position.set(p.x,pg+2+Math.sin(Math.PI*f)*16,p.y);}else p.mesh.position.set(p.x,pg+2.7,p.y);if(p.type==='pep')p.mesh.rotation.y+=dt*16;else p.mesh.rotation.z-=dt*8;}
  for(const h of hazards){h.mesh.position.set(h.x,groundAt(h.x,h.y)+.12,h.y);h.mesh.rotation.y=h.born*.05;h.mesh.scale.setScalar(Math.max(.01,Math.min(1,h.born*5)));}
  renderHazards(time,dt);itemsRender(time,dt);abilityRender(time,dt);for(const r of rollers){const p=track[r.j];r.m.position.set(r.x,groundAt(r.x,r.y)+8,r.y);tv.set(p.tx,0,p.ty);r.m.quaternion.setFromAxisAngle(tv,-r.lat/8);}
  for(const an of animators)an(time,dt);
  FXA.update(dt);FXN.update(dt);updRings(dt);
  const bh=renderer.getDrawingBufferSize(v2).y,sc=bh/(2*Math.tan(camera.fov*Math.PI/360));FXA.mat.uniforms.scale.value=sc;FXN.mat.uniforms.scale.value=sc;
  render.n=(render.n||0)+1;renderer.shadowMap.needsUpdate=qKey!=='fast'||render.n%2===0;/* half-rate shadows made moving shadows judder */
  if(qKey!=='fast'&&CFG.post!==false&&!LADV.np){try{postRender();}catch(e){console.warn('post',e);CFG.post=false;renderer.setRenderTarget(null);renderer.render(scene,camera);}}else renderer.render(scene,camera);
}

/* ================= HUD ================= */
const $=id=>document.getElementById(id);
const mini=$('mini'),mctx=mini.getContext('2d'),miniBase=cnv(300,300);
function buildMiniBase(){const m=miniBase.getContext('2d'),sc=140/T.R,sc2=sc;m.clearRect(0,0,300,300);
  m.fillStyle='rgba(22,12,9,.55)';m.beginPath();m.arc(150,150,148,0,7);m.fill();m.strokeStyle='rgba(247,201,72,.6)';m.lineWidth=5;m.beginPath();m.arc(150,150,142,0,7);m.stroke();
  m.lineJoin='round';m.strokeStyle='#fff4dc';m.lineWidth=16;pathTrack(m,track,sc,150,150);m.stroke();m.strokeStyle='#c53b22';m.lineWidth=11;m.stroke();
  if(SHORTS.length){m.save();m.setLineDash([5,7]);m.strokeStyle='rgba(157,255,122,.55)';m.lineWidth=5;m.lineCap='round';for(const sc of SHORTS){m.beginPath();sc.pts.forEach((p,i)=>i?m.lineTo(150+p.x*sc2,150+p.y*sc2):m.moveTo(150+p.x*sc2,150+p.y*sc2));m.stroke();}m.restore();m.lineCap='butt';}
  if(GLIDE){m.strokeStyle='#7fe8ff';m.lineWidth=12;m.lineCap='round';m.beginPath();for(let j=GLIDE.rj;j<=GLIDE.j1;j++){const p=track[j%N];j===GLIDE.rj?m.moveTo(150+p.x*sc,150+p.y*sc):m.lineTo(150+p.x*sc,150+p.y*sc);}m.stroke();m.lineCap='butt';}
  const s=track[0];m.fillStyle='#fff4dc';m.beginPath();m.arc(150+s.x*sc,150+s.y*sc,7,0,7);m.fill();}
let lastPos='',lastLap='',lastItem='',lastTimeStr='',lastSpd=-1,bannerT=0,hintShown=false;
const posNum=$('posNum'),posSuf=$('posSuf'),hudLap=$('hudLap'),hudTime=$('hudTime'),itemIcon=$('itemIcon'),itemBtn=$('itemBtn'),ihint=$('ihint'),banner=$('banner'),wrong=$('wrong'),spd=$('spd'),speedfx=$('speedfx');
const brkEls=[$('brakeL'),$('brakeR')],hitfx=$('hitfx'),slot2El=$('slot2'),frostfx=$('frostfx'),gVal=$('gVal'),gCh=$('gCh'),gauge=$('gauge'),lapBars=[...document.querySelectorAll('#lapBars i')];
const suf=n=>n===1?'st':n===2?'nd':n===3?'rd':'th';
const fmt=t=>{const m=Math.floor(t/60),s=t-m*60;return m+':'+(s<10?'0':'')+s.toFixed(2);};
function showBanner(txt,dur){banner.textContent=txt;banner.classList.remove('pop');void banner.offsetWidth;banner.classList.add('pop');bannerT=dur;}
function hud(dt,time){
  if(bannerT>0){bannerT-=dt;if(bannerT<=0)banner.textContent='';}
  if(!player)return;hud.pf=(hud.pf||0)+1;if(hud.pf%3===0)for(const k of karts){if(!k.pm)continue;const f=Math.max(0,Math.min(1,(k.finished?LAPS*N:k.prog)/(LAPS*N)));const v=(f*100).toFixed(1);if(k.pm._v!==v){k.pm._v=v;k.pm.style.left='calc(8px + (100% - 16px)*'+f.toFixed(4)+')';}}
  const pos=standCache.indexOf(player)+1;if(pos&&String(pos)!==lastPos){lastPos=String(pos);posNum.textContent=pos;posSuf.textContent=suf(pos);}
  const lap=clamp(Math.floor(Math.max(0,player.prog)/N)+1,1,LAPS);const ls=lap+'/'+LAPS;if(ls!==lastLap){lastLap=ls;hudLap.textContent=ls;lapBars.forEach((b,i)=>b.classList.toggle('on',i<lap));}
  if(state==='race'&&!player.finished&&lap>lapShown){lapShown=lap;const sp=recLap(lap);showBanner((lap===LAPS?'Final lap':'Lap '+lap)+(sp?' · '+sp:''),sp?2.2:1.6);SFX.lap(lap===LAPS);}
  const ts=fmt(player.finished?player.finishTime:raceTime);if(ts!==lastTimeStr){lastTimeStr=ts;hudTime.textContent=ts;}
  const sv=Math.round(Math.max(0,player.speed)*(CFG.units==='kmh'?1.062:.66));if(sv!==lastSpd){lastSpd=sv;spd.textContent=sv;gVal.style.strokeDasharray=Math.min(100,Math.max(0,player.speed)/(BASE_MAX*1.58)*100).toFixed(1)+' 100';}
  const chg=player.drift?Math.min(100,player.charge/2.6*100):0,tierN=player.drift?(player.tier||0):0;if(Math.abs(chg-(hud.ch||0))>.8||tierN!==hud.tn){hud.ch=chg;hud.tn=tierN;gCh.style.strokeDasharray=chg.toFixed(1)+' 100';gCh.style.stroke=['#fff4dc','#ffe066','#ff9a1f','#ff3b1a'][tierN];}
  const bst=player.boost>0;if(bst!==hud.bst){hud.bst=bst;gauge.classList.toggle('boost',bst);}
  speedfx.classList.toggle('on',player.boost>0&&state==='race');frostfx.classList.toggle('on',player.frozen>0);
  const dr=!!player.drift;if(dr!==hud.dr){hud.dr=dr;brkEls.forEach(b=>b.classList.toggle('drifting',dr));}
  const rk=ITEM_KEYS[Math.floor(time*14)%ITEM_KEYS.length],rl=player.roll>0,s1=player.item||(rl?rk:''),s2=player.item2||(rl&&(player.item||player.pend.length>1)?rk:''),ik=s1+'|'+s2;
  if(ik!==lastItem){lastItem=ik;itemBtn.classList.toggle('rolling',rl);itemBtn.classList.toggle('has',!!player.item&&!rl);
    itemIcon.innerHTML=s1?SVG[s1]:'<span class="empty"></span>';slot2El.innerHTML=s2?SVG[s2]:'<span class="empty"></span>';$('itemBtn2').classList.toggle('has',!!player.item2&&!rl);if(rl)SFX.tick();
    const canBack=!!player.item&&!NOBACK.includes(player.item);if(canBack&&!hintShown){ihint.classList.add('show');hintShown=true;setTimeout(()=>ihint.classList.remove('show'),4000);}}
  const tr=track[player.idx];const back=state==='race'&&!player.sc&&!player.finished&&player.spin<=0&&player.speed>15&&(Math.cos(player.ma)*tr.tx+Math.sin(player.ma)*tr.ty)<-.4;
  player.wrongT=back?player.wrongT+dt:0;wrong.hidden=player.wrongT<.8;
  hud.mf=(hud.mf||0)+1;if(hud.mf%3||true)return;
  mctx.clearRect(0,0,300,300);mctx.drawImage(miniBase,0,0);const sc=140/T.R;
  for(const k of karts){if(k===player)continue;mctx.fillStyle=k.col;mctx.strokeStyle='#160c09';mctx.lineWidth=3;mctx.beginPath();mctx.arc(150+k.rx*sc,150+k.ry*sc,8,0,7);mctx.fill();mctx.stroke();}
  mctx.fillStyle='#fff4dc';mctx.beginPath();mctx.arc(150+player.rx*sc,150+player.ry*sc,13,0,7);mctx.fill();mctx.fillStyle=player.col;mctx.beginPath();mctx.arc(150+player.rx*sc,150+player.ry*sc,8.5,0,7);mctx.fill();
}

/* ================= MENU / FLOW ================= */
const menu=$('menu'),results=$('results'),pauseOv=$('pauseOv'),resList=$('resList'),resTitle=$('resTitle'),resSub=$('resSub');
function goFullscreen(){const el=document.documentElement;try{const p=el.requestFullscreen?el.requestFullscreen({navigationUI:'hide'}):(el.webkitRequestFullscreen?el.webkitRequestFullscreen():null);
  if(p&&p.then)p.then(()=>{try{if(screen.orientation&&screen.orientation.lock)screen.orientation.lock('landscape').catch(()=>{});}catch(e){}}).catch(()=>{});}catch(e){}}
function buildProg(){const el=$('tbProg');if(!el)return;el.querySelectorAll('i,.tb-lap').forEach(n=>n.remove());for(let l=1;l<LAPS;l++){const t=document.createElement('span');t.className='tb-lap';t.style.left='calc(8px + (100% - 16px)*'+(l/LAPS).toFixed(4)+')';t.innerHTML='<b>L'+(l+1)+'</b>';el.appendChild(t);}for(const k of karts){const n=document.createElement('i');if(k===player)n.className='me';n.style.setProperty('--c',k.r.color);if(PORTRAITS[k.ri])n.style.backgroundImage='url('+PORTRAITS[k.ri]+')';el.appendChild(n);k.pm=n;}}
let _abSetup=false;function startRace(){if(!_abSetup){_abSetup=true;setupAbilityHud();const ci=$('cine');ci.addEventListener('pointerdown',e=>{e.preventDefault();introSkip=true;});addEventListener('keydown',()=>{if(state==='intro')introSkip=true;});}if(window.__clearInput)window.__clearInput();initAudio();if(ac&&ac.state==='suspended')ac.resume();goFullscreen();
  menu.hidden=true;results.hidden=true;pauseOv.hidden=true;resetRace(false);state='countdown';cd=3.4;lastCd=4;stage.classList.remove('demo');raceDone=false;
  buildProg();ghostStart();{const r=loadRecs()[recKey()],e=$('hudPB');if(e){e.hidden=!r;if(r)e.textContent='Best '+fmt(r.t);}}lastPos=lastLap=lastItem=lastTimeStr='';lastSpd=-1;hud.ch=-1;hud.bst=null;hud.dr=null;banner.textContent='';hintShown=false;itemQueued=null;}
const paint=()=>new Promise(r=>requestAnimationFrame(()=>setTimeout(r,0)));
let raceLoading=false;
async function goRace(mi){if(raceLoading)return;raceLoading=true;const rev=!!CLASSES[clsKey].rev,L=$('raceLd'),bar=$('rlBar'),txt=$('rlTxt'),m=MAPS[mi];
  const step=async(p,t)=>{bar.style.width=p+'%';if(t)txt.textContent=t;await paint();};
  try{$('rlBg').style.backgroundImage=MAP_SHOTS[m.id]?'url('+shotURL(m.id,'h')+')':'';$('rlName').textContent=m.name;$('rlSub').textContent=(gp?CUPS[gp.cup].name+' · race '+(gp.race+1)+' of 4':'Single race')+' · '+CLASSES[clsKey].label;
    L.classList.remove('out');L.hidden=false;state='loading';await step(8,'Rolling out the dough…');
    if(mi!==mapIdx||rev!==curRev){mapIdx=mi;loadMap(mi,rev);}await step(45,'Spreading the sauce…');
    /* wait for every sky and texture image to finish decoding */
    await Promise.all(Object.values(PROPT).map(t=>t.image&&t.image.decode&&!t.image.complete?t.image.decode().catch(()=>{}):null));await step(60,'Seating the racers…');
    BASE_MAX=BASE0*CLASSES[clsKey].mul;startRace();state='loading';await step(78,'Firing up the oven…');
    /* draw a few real frames at full size so every shader, texture, shadow and glow buffer is ready before the lights */
    try{const wg=new THREE.Group();for(const kk of ITEM_KEYS){try{const o=itemProto(kk);if(o)wg.add(o.clone());}catch(e){}}scene.add(wg);renderer.compile(scene,camera);scene.remove(wg);}catch(e){}
    fit();for(let i=0;i<3;i++){render(0,1/60);renderer.shadowMap.needsUpdate=true;try{if(qKey!=='fast')postRender();else{renderer.setRenderTarget(null);renderer.render(scene,camera);}}catch(e){}await paint();}
    await step(100,'Ready!');}catch(e){console.warn('race load',e);}
  perfSum=perfN=perfT=0;slowN=fastN=0;abilityHudFor(selected);startIntro();last=performance.now();acc=0;
  L.classList.add('out');setTimeout(()=>{L.hidden=true;},320);raceLoading=false;}
function startGP(){gp={cup:cupIdx,race:0,pts:new Array(8).fill(0),last:new Array(8).fill(0)};goRace(CUP_TRACKS[cupIdx][0]);}
function startFromMenu(){cpuBuilds=RACERS.map(randomBuild);if(mode==='gp')startGP();else{gp=null;goRace(mapIdx);}}
function finalizeRace(){if(raceDone)return;raceDone=true;const st=standings();for(const k of st){if(!k.finished){k.finished=true;k.place=++finishCount;k.est=true;k.finishTime=raceTime+Math.max(0,LAPS*N-k.prog)*8/Math.max(60,BASE_MAX*.85);}}
  if(gp){gp.last.fill(0);for(const k of karts){const pt=PTS[k.place-1]||0;gp.pts[k.ri]+=pt;gp.last[k.ri]=pt;}}}
function toMenu(){gp=null;menuStep='home';document.querySelectorAll('#menu .step').forEach(e=>e.hidden=e.dataset.step!=='home');BASE_MAX=BASE0;if(curRev)loadMap(mapIdx,false);state='menu';results.hidden=true;pauseOv.hidden=true;menu.hidden=false;resetRace(true);stage.classList.add('demo');wrong.hidden=true;banner.textContent='';speedfx.classList.remove('on');refreshMenu();}
/* ================= RECORDS: race history, personal bests and a ghost of your best run ================= */
const REC_HZ=10,REC_MAX=6000;let recBuf=null,recT=0,recLaps=[],ghost=null,ghostRun=null,lastRun=null;
const recKey=()=>MAPS[mapIdx].id+'|'+clsKey;
function loadRecs(){try{return JSON.parse(store.get('crust-recs')||'{}')||{};}catch(e){return {};}}
function loadHist(){try{return JSON.parse(store.get('crust-hist')||'[]')||[];}catch(e){return [];}}
function packI16(arr){const i16=new Int16Array(arr.length);for(let i=0;i<arr.length;i++)i16[i]=Math.max(-32767,Math.min(32767,Math.round(arr[i])));const u8=new Uint8Array(i16.buffer);let b='';for(let i=0;i<u8.length;i+=8192)b+=String.fromCharCode.apply(null,u8.subarray(i,i+8192));return btoa(b);}
function unpackI16(s){const b=atob(s),u8=new Uint8Array(b.length);for(let i=0;i<b.length;i++)u8[i]=b.charCodeAt(i);return new Int16Array(u8.buffer);}
const wrapA=a=>Math.atan2(Math.sin(a),Math.cos(a));
/* record the player's kart 10 times a second while racing */
function recTick(){if(!recBuf||!player||player.finished)return;const g=player.m.g;while(recT<=raceTime&&recBuf.length<REC_MAX*6){recBuf.push(g.position.x*4,g.position.y*4,g.position.z*4,wrapA(g.rotation.x)*10000,wrapA(g.rotation.y)*10000,wrapA(g.rotation.z)*10000);recT+=1/REC_HZ;}}
/* the ghost: your own kart from your best run, see-through, replaying that run */
function ghostStart(){recBuf=[];recT=0;recLaps=[];lastRun=null;
  if(ghost){if(ghost.g.parent)ghost.g.parent.remove(ghost.g);ghost.mats.forEach(m=>m.dispose());ghost=null;}ghostRun=null;
  if(!CFG.ghost)return;const R=loadRecs()[recKey()];if(!R||!R.g)return;
  try{const d=unpackI16(R.g);ghostRun={d,n:d.length/6,t:R.t,laps:R.laps||[]};
    const m=buildKart(Object.assign({},R.spec||{ri:selected,b:playerBuild.b,w:playerBuild.w,g:playerBuild.g,p:playerBuild.p,t:playerBuild.t||''},{hq:0}));m.g.rotation.order='YZX';m.g.scale.setScalar(KS*m.sf);
    const mats=[],sw=new Map();m.g.traverse(o=>{if(!o.isMesh)return;o.castShadow=false;o.receiveShadow=false;const one=x=>{if(!sw.has(x)){const c=x.clone();c.transparent=true;c.opacity=.36;c.depthWrite=false;if(c.emissive)c.emissive.set('#3a6aff'),c.emissiveIntensity=.35;sw.set(x,c);mats.push(c);}return sw.get(x);};o.material=Array.isArray(o.material)?o.material.map(one):one(o.material);});
    if(m.gl)m.gl.visible=false;m.g.renderOrder=2;m.g.visible=false;world.add(m.g);m.g.userData.noLift=true;ghost={g:m.g,mats};}catch(e){ghost=null;ghostRun=null;}}
function ghostTick(){if(!ghost||!ghostRun)return;const t=state==='race'?raceTime:0,f=t*REC_HZ,i=Math.floor(f),d=ghostRun.d;
  if(i>=ghostRun.n-1||(state!=='race'&&state!=='countdown')){ghost.g.visible=false;return;}const u=f-i,a=i*6,b=a+6;ghost.g.visible=true;
  ghost.g.position.set((d[a]+(d[b]-d[a])*u)/4,(d[a+1]+(d[b+1]-d[a+1])*u)/4,(d[a+2]+(d[b+2]-d[a+2])*u)/4);
  ghost.g.rotation.set(lerpA(d[a+3]/1e4,d[b+3]/1e4,u),lerpA(d[a+4]/1e4,d[b+4]/1e4,u),lerpA(d[a+5]/1e4,d[b+5]/1e4,u));
  const near=(ghost.g.position.x-camera.position.x)**2+(ghost.g.position.z-camera.position.z)**2<30*30;ghost.mats.forEach(m=>m.opacity=near?.16:.36);}
/* lap splits against your best run */
function recLap(lap){if(!recBuf)return null;recLaps.push(raceTime);if(!ghostRun||!ghostRun.laps[lap-2])return null;const d=raceTime-ghostRun.laps[lap-2];return (d<0?'−':'+')+Math.abs(d).toFixed(2)+'s vs best';}
function saveRun(){if(!player||!recBuf)return;const t=player.finishTime,key=recKey(),recs=loadRecs(),old=recs[key],pb=!old||t<old.t;
  lastRun={t,old:old?old.t:null,pb,place:player.place};
  if(pb){recs[key]={t,d:Date.now(),place:player.place,dr:selected,laps:recLaps.slice(),spec:{ri:selected,b:playerBuild.b,w:playerBuild.w,g:playerBuild.g,p:playerBuild.p,t:playerBuild.t||''},g:packI16(recBuf)};
    let s=JSON.stringify(recs);/* keep storage in check: drop the oldest ghosts if it ever gets large */
    if(s.length>3e6){const ks=Object.keys(recs).filter(k=>k!==key&&recs[k].g).sort((a,b)=>recs[a].d-recs[b].d);while(s.length>3e6&&ks.length){delete recs[ks.shift()].g;s=JSON.stringify(recs);}}store.set('crust-recs',s);}
  const h=loadHist();h.unshift({m:MAPS[mapIdx].id,c:clsKey,t,p:player.place,d:Date.now(),dr:selected,pb});store.set('crust-hist',JSON.stringify(h.slice(0,60)));recBuf=null;}
function pbLine(){if(!lastRun)return '';if(lastRun.pb)return lastRun.old==null?'<span class="pbn">First time logged · '+fmt(lastRun.t)+'</span>':'<span class="pbn">New personal best! '+fmt(lastRun.t)+' (−'+(lastRun.old-lastRun.t).toFixed(2)+'s)</span>';
  return '<span class="pbo">Personal best '+fmt(lastRun.old)+' · +'+(lastRun.t-lastRun.old).toFixed(2)+'s</span>';}
const fmtDate=d=>{const x=new Date(d);return x.toLocaleDateString(undefined,{month:'short',day:'numeric'});};
let recCls=null;
function renderRecords(){if(!recCls)recCls=clsKey;const recs=loadRecs(),hist=loadHist();
  $('recCls').innerHTML=Object.keys(CLASSES).map(k=>'<button data-c="'+k+'" aria-pressed="'+(k===recCls)+'">'+CLASSES[k].label+'</button>').join('');
  $('recCls').querySelectorAll('button').forEach(b=>b.onclick=()=>{recCls=b.dataset.c;renderRecords();});
  $('recBest').innerHTML=MAPS.map((m,i)=>{const r=recs[m.id+'|'+recCls];return '<li><img alt="" src="'+shotURL(m.id,'h')+'"><span class="nm">'+m.name+'</span>'+(r?'<span class="tm">'+fmt(r.t)+'</span><span class="dt">'+RACERS[r.dr].name+' · '+fmtDate(r.d)+'</span>':'<span class="tm none">—</span><span class="dt">No time yet</span>')+'</li>';}).join('');
  $('recHist').innerHTML=hist.length?hist.map(h=>{const m=MAPS.find(x=>x.id===h.m);return '<li><span class="pl">'+h.p+suf(h.p)+'</span><span class="nm">'+(m?m.name:h.m)+'<small>'+(CLASSES[h.c]?CLASSES[h.c].label:h.c)+' · '+RACERS[h.dr].name+' · '+fmtDate(h.d)+'</small></span><span class="tm">'+fmt(h.t)+(h.pb?'<em>PB</em>':'')+'</span></li>';}).join(''):'<li class="empty">Finish a race and it will show up here.</li>';}

function onPlayerFinish(){saveRun();player.auto=true;showBanner('Finish!',2.4);SFX.finish();resultsAt=2.4;}
const TROPHY=c=>'<svg class="trophy" viewBox="0 0 24 24"><path d="M7 3h10v4.5a5 5 0 0 1-10 0z" fill="'+c+'"/><path d="M7 5H4a3 3 0 0 0 3 4.2M17 5h3a3 3 0 0 1-3 4.2" stroke="'+c+'" stroke-width="1.6" fill="none"/><rect x="10.5" y="12" width="3" height="5" fill="'+c+'"/><rect x="7" y="17" width="10" height="3.4" rx="1" fill="#8a5f42"/></svg>';
function renderResults(){renderResults0();const pl=pbLine();if(pl)resSub.innerHTML=resSub.textContent.replace(/[<>&]/g,'')+'<br>'+pl;}
function renderResults0(){finalizeRace();const st=standings();const me=player.place||st.indexOf(player)+1,cl=CLASSES[clsKey].label;
  const row=(k,i,right,extra)=>'<li class="'+(k===player?'me':'')+'"><span class="pl">'+(i+1)+'</span><span class="sw" style="background:'+k.r.color+'"></span><span>'+k.r.name+(k===player?' (you)':'')+'</span><span class="tm">'+(extra||'')+right+'</span></li>';
  resList.innerHTML=st.map((k,i)=>row(k,i,(k.est?'~':'')+fmt(k.finishTime))).join('');
  const gb=$('gpBox'),tr=$('trophy');tr.hidden=true;
  if(gp){gb.hidden=false;const fin=gp.race>=3;$('gpLabel').textContent=CUPS[gp.cup].name+' · race '+(gp.race+1)+' of 4';
    const order=karts.slice().sort((a,b)=>gp.pts[b.ri]-gp.pts[a.ri]);$('gpList').innerHTML=order.map((k,i)=>row(k,i,gp.pts[k.ri]+' pts','<span class="add">+'+gp.last[k.ri]+'</span>')).join('');
    if(fin){const cp=order.indexOf(player)+1;resTitle.textContent=cp===1?'You won the '+CUPS[gp.cup].name+'!':cp+suf(cp)+' in the '+CUPS[gp.cup].name;if(cp<=3){tr.innerHTML=TROPHY(['#ffd54a','#d8dde3','#e09a5a'][cp-1]);tr.hidden=false;}
      resSub.textContent='Final standings · '+cl+' class';$('againBtn').textContent='Play this cup again';$('toMenuBtn').textContent='Back to menu';}
    else{resTitle.textContent=me===1?'1st place!':me+suf(me)+' place';resSub.textContent=MAPS[mapIdx].name+' · '+cl+' class';$('againBtn').textContent='Next race';$('toMenuBtn').textContent='Quit to menu';}}
  else{gb.hidden=true;resTitle.textContent=me===1?'1st place!':me+suf(me)+' place';resSub.textContent=MAPS[mapIdx].name+' · '+cl+' class';$('againBtn').textContent='Race again';$('toMenuBtn').textContent='Change track or driver';}}
function togglePause(){if(window.__clearInput)window.__clearInput();if(state==='race'||state==='countdown'){pauseOv._prev=state;state='paused';pauseOv.hidden=false;if(engGain)engGain.gain.value=0;}
  else if(state==='paused'){state=pauseOv._prev;pauseOv.hidden=true;last=performance.now();}}
$('startBtn').onclick=startFromMenu;$('againBtn').onclick=()=>{if(gp){if(gp.race>=3)startGP();else{gp.race++;goRace(CUP_TRACKS[gp.cup][gp.race]);}}else goRace(mapIdx);};$('restartBtn').onclick=()=>{if(gp)gp.pts.forEach((v,i)=>gp.pts[i]=v);startRace();};
$('toMenuBtn').onclick=toMenu;$('quitBtn').onclick=toMenu;$('resumeBtn').onclick=togglePause;$('pauseBtn').addEventListener('pointerup',e=>{e.preventDefault();togglePause();});
const setOv=$('setOv'),howOv=$('howOv'),fpsEl=$('fpsEl');let setFrom=null;
const BOOLK=['shadows','showfps','shake','mini','ghost','music'];
const cfgVal=k=>k==='sound'?!muted:k==='stats'?statsOn:CFG[k];
function openSettings(from){setFrom=from;from.hidden=true;setOv.hidden=false;setOv.scrollTop=0;refreshSettings();}
function closeSettings(){setOv.hidden=true;(setFrom||menu).hidden=false;refreshMenu();}
function fillGuide(){const gi=$('guideItems'),ga=$('guideAbil');if(!gi||gi.dataset.done)return;gi.dataset.done=1;
  gi.innerHTML=ITEM_KEYS.map(k=>'<li><span class="gi">'+(SVG[k]||'')+'</span><span><b>'+HELP[k][0]+'</b>'+(DROPS.includes(k)?'<em class="dr">drop</em>':'')+'<small>'+HELP[k][1]+'</small></span></li>').join('');
  ga.innerHTML=RACERS.map((r,i)=>{const A=ABIL[r.name.toLowerCase()];if(!A)return '';return '<li><span class="gi pt" style="--c:'+A[2]+';'+(PORTRAITS[i]?'background-image:url('+PORTRAITS[i]+')':'')+'"></span><span><b>'+A[0]+'</b><em>'+r.name+'</em><small>'+A[1]+'</small></span></li>';}).join('');}
function refreshSettings(){try{fillGuide();}catch(e){}document.querySelectorAll('#setOv .seg[data-k]').forEach(sg=>{const v=cfgVal(sg.dataset.k),sv=typeof v==='boolean'?(v?'1':'0'):String(v);sg.querySelectorAll('button').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.v===sv)));});
  $('volR').value=CFG.vol;$('volO').textContent=CFG.vol;$('mvolR').value=CFG.mvol;$('mvolO').textContent=CFG.mvol;refreshMenu();}
function applySettings(){if(renderer.shadowMap.enabled!==CFG.shadows){renderer.shadowMap.enabled=CFG.shadows;scene.traverse(o=>{if(o.material)(Array.isArray(o.material)?o.material:[o.material]).forEach(m=>m.needsUpdate=true);});}
  if(master)master.gain.value=CFG.vol/100;$('spdU').textContent=CFG.units==='kmh'?'KM/H':'MPH';lastSpd=-1;mini.hidden=true;}
document.querySelectorAll('#setOv .seg[data-k] button').forEach(b=>b.onclick=()=>{const k=b.parentNode.dataset.k,v=b.dataset.v;
  if(k==='sound'){muted=v==='0';store.set('crust-muted',muted?'1':'0');}
  else if(k==='stats'){statsOn=v==='1';store.set('crust-stats',statsOn?'1':'0');}
  else{CFG[k]=BOOLK.includes(k)?v==='1':v;saveCfg();}
  applySettings();refreshSettings();});
$('volR').oninput=e=>{CFG.vol=+e.target.value;$('volO').textContent=CFG.vol;if(master)master.gain.value=CFG.vol/100;saveCfg();};
$('mvolR').oninput=e=>{CFG.mvol=+e.target.value;$('mvolO').textContent=CFG.mvol;saveCfg();};
$('setReset').onclick=()=>{Object.assign(CFG,CFG_DEF);saveCfg();muted=false;store.set('crust-muted','0');statsOn=true;store.set('crust-stats','1');qKey=COARSE?'balanced':'sharp';store.set('crust-q',qKey);applyQuality();applySettings();refreshSettings();};
$('setBtn').onclick=()=>openSettings(menu);$('pauseSetBtn').onclick=()=>openSettings(pauseOv);$('setDone').onclick=closeSettings;
$('howBtn').onclick=()=>{menu.hidden=true;howOv.hidden=false;howOv.scrollTop=0;};$('recBtn').onclick=()=>{recCls=clsKey;renderRecords();menu.hidden=true;$('recOv').hidden=false;$('recOv').scrollTop=0;};$('recDone').onclick=()=>{$('recOv').hidden=true;menu.hidden=false;};$('howDone').onclick=()=>{howOv.hidden=true;menu.hidden=false;};
addEventListener('keydown',e=>{if(e.code!=='Escape')return;if(!setOv.hidden)closeSettings();else if(!howOv.hidden)$('howDone').onclick();else if(!$('recOv').hidden)$('recDone').onclick();else if(garageOpen)closeGarage();else if(state==='race'||state==='countdown'||state==='paused')togglePause();});
document.addEventListener('visibilitychange',()=>{if(document.hidden&&(state==='race'||state==='countdown'))togglePause();});
document.querySelectorAll('#clsSeg button').forEach(b=>b.onclick=()=>{clsKey=b.dataset.c;store.set('crust-cls',clsKey);refreshMenu();});
document.querySelectorAll('#modeSeg button').forEach(b=>b.onclick=()=>{mode=b.dataset.m;store.set('crust-mode',mode);if(mode==='gp'){const t=CUP_TRACKS[cupIdx][0];if(t!==mapIdx){mapIdx=t;loadMap(t,false);resetRace(true);}}refreshMenu();});
document.querySelectorAll('#qual button').forEach(b=>b.onclick=()=>{qKey=b.dataset.q;store.set('crust-q',qKey);applyQuality();refreshMenu();});
function applyQuality(){const q=QUAL[qKey];renderer.shadowMap.type=q.soft?THREE.PCFSoftShadowMap:THREE.PCFShadowMap;sun.shadow.mapSize.set(q.sm,q.sm);if(sun.shadow.map){sun.shadow.map.dispose();sun.shadow.map=null;}
  scene.traverse(o=>{if(o.material)(Array.isArray(o.material)?o.material:[o.material]).forEach(m=>m.needsUpdate=true);});pr=Math.min(DPR,q.start);capPR=Math.min(DPR,q.cap);raisedAt=-1;ladBest=0;{const v=+store.get(ladKey());applyLad(v>0?v:0,false);}fit();}
let menuStep='home';
function goStep(st){menuStep=st;if(st==='home')requestAnimationFrame(fitLogo);if(st==='kart'){document.querySelectorAll('#menu .step').forEach(e=>e.hidden=e.dataset.step!=='driver');openGarage();return;}document.querySelectorAll('#menu .step').forEach(e=>e.hidden=e.dataset.step!==st);menu.hidden=false;refreshMenu();}
function refreshMenu(){requestAnimationFrame(fitLogo);document.querySelectorAll('#qual button').forEach(b=>b.setAttribute('aria-pressed',b.dataset.q===qKey));$('qualNote').textContent=QUAL[qKey].note;document.querySelectorAll('#clsSeg button').forEach(b=>b.setAttribute('aria-pressed',b.dataset.c===clsKey));$('clsNote').textContent=CLASSES[clsKey].note;document.querySelectorAll('#modeSeg button').forEach(b=>b.setAttribute('aria-pressed',b.dataset.m===mode));
  $('cups').hidden=mode!=='gp';$('maps').hidden=mode==='gp';$('trackLabel').textContent=mode==='gp'?'Cup':'Track';$('startBtn').textContent=mode==='gp'?'Start Grand Prix':'Start race';document.querySelectorAll('.cupc').forEach((x,j)=>x.setAttribute('aria-pressed',j===cupIdx));
  document.querySelectorAll('.card').forEach((x,j)=>x.setAttribute('aria-pressed',j===selected));$('buildSum').textContent=buildSummary();document.querySelectorAll('.mapc').forEach((x,j)=>x.setAttribute('aria-pressed',j===mapIdx));updateDriverDetail();updateTrackDetail();}
const CARDCOL={kitchen:['#5a2e18','#c98b4e','#f3c046'],bay:['#157f9b','#c98b4e','#f3c046'],night:['#121633','#7a5232','#d8a83a'],freezer:['#8fbde6','#c98b4e','#f3dc8a']};
function drawTrackThumb(g,m,tk,cx,cy,rad,bg){const cl=CARDCOL[m.theme];if(bg){const gr=g.createLinearGradient(cx-rad*1.7,cy-rad*1.1,cx-rad*1.7,cy+rad*1.1);gr.addColorStop(0,cl[0]);gr.addColorStop(1,shade(cl[0],-.4));g.fillStyle=gr;g.fillRect(cx-bg[0]/2,cy-bg[1]/2,bg[0],bg[1]);}
  const sc=(rad*.95)/m.R;g.fillStyle=cl[1];g.beginPath();g.arc(cx,cy,rad,0,7);g.fill();g.fillStyle=cl[2];g.beginPath();g.arc(cx,cy,rad*.92,0,7);g.fill();
  g.lineJoin='round';g.strokeStyle='#fff4dc';g.lineWidth=Math.max(3,rad*.1);pathTrack(g,tk.pts,sc,cx,cy);g.stroke();g.strokeStyle='#c53b22';g.lineWidth=Math.max(2,rad*.065);g.stroke();}
const MAP_SHOTS={"margherita":{"h":"assets/shots/margherita-h.6ce3ada66e.jpg","m":"assets/shots/margherita-m.b4a457a59e.jpg","a":"assets/shots/margherita-a.63fa4045d9.jpg","i":{"len":9338,"glide":true,"loop":true,"ramps":4,"shorts":1,"tunnel":false,"surf":["marble","planks","sauce"]}},"bay":{"h":"assets/shots/bay-h.5c6925bf30.jpg","m":"assets/shots/bay-m.f78814aad2.jpg","a":"assets/shots/bay-a.e8b4db14ba.jpg","i":{"len":10492,"glide":true,"loop":true,"ramps":4,"shorts":2,"tunnel":false,"surf":["brick","asphalt"]}},"peaks":{"h":"assets/shots/peaks-h.cb9a6599d0.jpg","m":"assets/shots/peaks-m.4671308761.jpg","a":"assets/shots/peaks-a.1d210edbf1.jpg","i":{"len":10352,"glide":true,"loop":true,"ramps":4,"shorts":1,"tunnel":true,"surf":["sauce","asphalt","cobble"]}},"frosty":{"h":"assets/shots/frosty-h.6471d76ac7.jpg","m":"assets/shots/frosty-m.a7ad14050c.jpg","a":"assets/shots/frosty-a.7008fa84b6.jpg","i":{"len":8240,"glide":true,"loop":true,"ramps":4,"shorts":1,"tunnel":false,"surf":["cobble","ice"]}},"basil":{"h":"assets/shots/basil-h.191aa8d2b4.jpg","m":"assets/shots/basil-m.48f2a902c0.jpg","a":"assets/shots/basil-a.3df943014b.jpg","i":{"len":8948,"glide":true,"loop":true,"ramps":4,"shorts":0,"tunnel":false,"surf":["planks","sauce"]}},"lagoon":{"h":"assets/shots/lagoon-h.81d45edf5e.jpg","m":"assets/shots/lagoon-m.14563e7ab0.jpg","a":"assets/shots/lagoon-a.37dbae5165.jpg","i":{"len":9470,"glide":true,"loop":true,"ramps":4,"shorts":2,"tunnel":false,"surf":["asphalt","planks","brick"]}},"mozz":{"h":"assets/shots/mozz-h.ba70f9f0d3.jpg","m":"assets/shots/mozz-m.5d83dc561b.jpg","a":"assets/shots/mozz-a.67273baaec.jpg","i":{"len":7719,"glide":true,"loop":true,"ramps":4,"shorts":1,"tunnel":false,"surf":["asphalt","cobble","sauce"]}},"burn":{"h":"assets/shots/burn-h.f6dabab80e.jpg","m":"assets/shots/burn-m.4f65928d9c.jpg","a":"assets/shots/burn-a.92f7910956.jpg","i":{"len":8457,"glide":true,"loop":true,"ramps":4,"shorts":2,"tunnel":false,"surf":["ice","asphalt","cobble"]}},"oven":{"h":"assets/shots/oven-h.2077fa2220.jpg","m":"assets/shots/oven-m.039387c5be.jpg","a":"assets/shots/oven-a.2ca3d2d284.jpg","i":{"len":9146,"glide":true,"loop":true,"ramps":4,"shorts":1,"tunnel":false,"surf":["planks","sauce","marble"]}},"calzone":{"h":"assets/shots/calzone-h.e5d49dacb8.jpg","m":"assets/shots/calzone-m.4954e29f9e.jpg","a":"assets/shots/calzone-a.3c215fa317.jpg","i":{"len":8995,"glide":true,"loop":true,"ramps":4,"shorts":1,"tunnel":false,"surf":["brick","asphalt","planks"]}},"napoli":{"h":"assets/shots/napoli-h.1b8256ba7e.jpg","m":"assets/shots/napoli-m.2db935db3e.jpg","a":"assets/shots/napoli-a.697c353c0c.jpg","i":{"len":8467,"glide":true,"loop":true,"ramps":4,"shorts":1,"tunnel":true,"surf":["sauce","asphalt"]}},"glacier":{"h":"assets/shots/glacier-h.d4a319f7d7.jpg","m":"assets/shots/glacier-m.749ed07a41.jpg","a":"assets/shots/glacier-a.18530639c1.jpg","i":{"len":8214,"glide":true,"loop":true,"ramps":4,"shorts":0,"tunnel":false,"surf":["ice","asphalt","cobble"]}},"spiral":{"h":"assets/shots/spiral-h.333d0a8af9.jpg","m":"assets/shots/spiral-m.7aa3bf22d4.jpg","a":"assets/shots/spiral-a.0b498fc09c.jpg","i":{"len":8704,"glide":true,"loop":true,"ramps":4,"shorts":2,"tunnel":false,"surf":["marble","planks","sauce"]}},"tour":{"h":"assets/shots/tour-h.e063e40ed0.jpg","m":"assets/shots/tour-m.10faa0decc.jpg","a":"assets/shots/tour-a.dfebfdcb40.jpg","i":{"len":9354,"glide":true,"loop":true,"ramps":4,"shorts":1,"tunnel":false,"surf":["asphalt","planks","brick"]}},"moon":{"h":"assets/shots/moon-h.7f7974a10f.jpg","m":"assets/shots/moon-m.bcd1682a6c.jpg","a":"assets/shots/moon-a.87128032f5.jpg","i":{"len":9426,"glide":true,"loop":true,"ramps":4,"shorts":1,"tunnel":false,"surf":["sauce","asphalt"]}},"peak":{"h":"assets/shots/peak-h.186d4aea66.jpg","m":"assets/shots/peak-m.4003974e0a.jpg","a":"assets/shots/peak-a.d8b995f958.jpg","i":{"len":9412,"glide":true,"loop":true,"ramps":4,"shorts":2,"tunnel":false,"surf":["ice","asphalt","cobble"]}}};
const shotURL=(id,k)=>MAP_SHOTS[id]?texSrc(MAP_SHOTS[id][k]):'';
const THEME_NAME={kitchen:'Pizzeria kitchen',bay:'Seaside bay',night:'Night city',freezer:'Freezer'};
const MAP_BLURB={kitchen:'Racing across a giant pizza on the pizzeria counter, past the wood-fired ovens and shelves of jars.',bay:'A sunny harbour lap with palm islands, a waterfall cliff and the city across the water.',night:'Neon billboards, searchlights and a glowing tunnel under a deep-space sky.',freezer:'Snowy pines, frozen mountains and slippery packed ice.'};
function updateTrackDetail(){const el=$('trkDetail');if(!el)return;
  if(mode==='gp'){const ts=CUP_TRACKS[cupIdx];el.innerHTML='<span class="sub">'+(CLASSES[clsKey].label||'')+' · 4 races</span><h3>'+CUPS[cupIdx].name+'</h3><div class="cuplist">'+ts.map(t=>'<div><img alt="" src="'+shotURL(MAPS[t].id,'h')+'"><span>'+MAPS[t].name+'</span></div>').join('')+'</div><p>Race all four tracks. Points for every finish decide the trophy.</p>';return;}
  const m=MAPS[mapIdx],sh=MAP_SHOTS[m.id],inf=sh?sh.i:null;let chips='<em class="y">'+THEME_NAME[m.theme]+'</em>';
  if(inf){chips+='<em>'+(inf.len/1000).toFixed(1)+' km lap</em>'+(inf.glide?'<em>Glide jump</em>':'')+(inf.loop?'<em>Loop</em>':'')+(inf.tunnel&&m.theme==='night'?'<em>Tunnel</em>':'')+(inf.shorts?'<em>'+inf.shorts+' shortcut'+(inf.shorts>1?'s':'')+'</em>':'')+'<em>'+inf.ramps+' ramps</em>'+inf.surf.map(x=>'<em>'+(ROAD_SURF[x]?ROAD_SURF[x].name:x)+'</em>').join('');}
  {const r=loadRecs()[m.id+'|'+clsKey];if(r)chips='<em class="y">Best '+fmt(r.t)+'</em>'+chips;}
  el.innerHTML='<img class="hero" alt="" src="'+shotURL(m.id,'h')+'"><div class="thumbs"><img alt="" src="'+shotURL(m.id,'m')+'"><img alt="" src="'+shotURL(m.id,'a')+'"></div><span class="sub">'+CUPS[m.cup].name+'</span><h3>'+m.name+'</h3><div class="chips2">'+chips+'</div><p>'+MAP_BLURB[m.theme]+'</p>';}
function buildMapCards(){const wrap=$('maps'),cw=$('cups'),thumbs=MAPS.map(m=>makeTrack(m,false));
  MAPS.forEach((m,i)=>{const b=document.createElement('button');b.className='mapc';b.id='map-'+m.id;let c;if(MAP_SHOTS[m.id]){c=new Image();c.alt='';c.decoding='async';c.loading='lazy';c.src=shotURL(m.id,'h');}else{c=cnv(200,125);drawTrackThumb(c.getContext('2d'),m,thumbs[i],100,62.5,56,[200,125]);}
    const bar=document.createElement('i');bar.style.background=CUPS[m.cup].col;const n=document.createElement('b');n.textContent=m.name;b.append(c,bar,n);
    b.onclick=()=>{if(mapIdx===i)return;mapIdx=i;store.set('crust-map',i);refreshMenu();setTimeout(()=>{loadMap(mapIdx,false);resetRace(true);},30);};wrap.appendChild(b);});
  CUPS.forEach((cp,ci)=>{const b=document.createElement('button');b.className='cupc';b.id='cup-'+ci;const c=cnv(220,220),g=c.getContext('2d');g.fillStyle='#1e110b';g.fillRect(0,0,220,220);
    CUP_TRACKS[ci].forEach((ti,k)=>{const x=55+(k%2)*110,y=55+Math.floor(k/2)*110;drawTrackThumb(g,MAPS[ti],thumbs[ti],x,y,46,[108,108]);});
    g.strokeStyle=cp.col;g.lineWidth=6;g.strokeRect(3,3,214,214);const n=document.createElement('b');n.textContent=cp.name;const mos=document.createElement('div');mos.className='mos';mos.innerHTML=CUP_TRACKS[ci].map(t=>'<img alt="" src="'+shotURL(MAPS[t].id,'h')+'">').join('');b.append(c,mos,n);b.style.boxShadow='inset 0 0 0 3px '+cp.col;
    b.onclick=()=>{cupIdx=ci;store.set('crust-cup',ci);const t=CUP_TRACKS[ci][0];if(t!==mapIdx){mapIdx=t;loadMap(t,false);resetRace(true);}refreshMenu();};cw.appendChild(b);});}
const BIOS=[['Pep','The fiery leader of the pack. Loves a tight racing line and a crispy edge.','Pizza peel'],['Basil','Cool, fresh and always calm on the last lap. Never panics in a pack.','Ripe tomato'],
 ['Olive','Smooth as olive oil through every corner. A master of the long drift.','Olive oil'],['Mozz','Stretchy, sunny and impossible to shake off your bumper.','Cheese wedge'],
 ['Chili','Hot-headed and always flat out. Saves nothing for the finish.','Hot sauce'],['Shroom','Small, earthy and sneaky on the shortcuts. Knows every hidden trail.','Rolling pin'],
 ['Pineapple','Divisive but fearless. Loves big jumps and bigger arguments.','Pizza boxes'],['Anchovy','Slippery, salty and fast in a straight line. Swims through traffic.','Pizza cutter']];
function portraitProp(i,P){const m=(c,r,me)=>new THREE.MeshStandardMaterial({color:c,roughness:r??.5,metalness:me||0}),wood=m('#b07a44',.6),steel=m('#d8dce2',.25,.9);
  if(i===0){const pe=new THREE.Group();P3(new THREE.CylinderGeometry(2.6,2.6,.12,40),wood,0,0,0,pe);const h=P3(new THREE.CylinderGeometry(.22,.26,5.5,12),wood,0,0,-4.8,pe);h.rotation.x=Math.PI/2;pe.rotation.set(-1.25,0,.25);pe.position.set(-3.3,3.2,-1.6);P.add(pe);}
  if(i===1){const t=P3(new THREE.SphereGeometry(1.6,28,20),m('#d6301e',.3),3.4,1.5,1,P);t.scale.y=.85;for(let k=0;k<5;k++){const l=P3(new THREE.ConeGeometry(.25,1.2,6),m('#3f9a35'),3.4+Math.cos(k*1.26)*.5,3,1+Math.sin(k*1.26)*.5,P);l.rotation.z=Math.cos(k*1.26)*1.2;l.rotation.x=Math.sin(k*1.26)*1.2;}}
  if(i===2){const g=new THREE.MeshPhysicalMaterial({color:'#7c8a1e',roughness:.08,clearcoat:1,transparent:true,opacity:.85});P3(new THREE.CylinderGeometry(1,1.1,4.2,24),g,3.3,2.4,.8,P);P3(new THREE.CylinderGeometry(.35,.5,1.2,16),g,3.3,5,.8,P);P3(new THREE.CylinderGeometry(.38,.38,.4,16),m('#2a2a2a'),3.3,5.8,.8,P);}
  if(i===3){const sh=new THREE.Shape();sh.moveTo(0,0);sh.lineTo(4,0);sh.lineTo(0,2);sh.closePath();const w=P3(new THREE.ExtrudeGeometry(sh,{depth:2.4,bevelEnabled:true,bevelSize:.12,bevelThickness:.12,bevelSegments:2}),m('#f7c948',.45),1.8,.2,-.4,P);w.rotation.y=-.5;for(let k=0;k<5;k++)P3(new THREE.SphereGeometry(.22+Math.random()*.15,10,8),m('#d9a62a'),2.6+Math.random()*1.6,.6+Math.random()*.8,.4+Math.random()*1.2,P);}
  if(i===4){P3(new THREE.CylinderGeometry(.9,.9,3.2,20),m('#c8100c',.25),3.2,1.8,1,P);P3(new THREE.CylinderGeometry(.35,.6,1,16),m('#c8100c',.25),3.2,3.9,1,P);P3(new THREE.CylinderGeometry(.4,.4,.6,16),m('#f4f4f2'),3.2,4.6,1,P);P3(new THREE.CylinderGeometry(.95,.95,1.2,20),m('#f7c948'),3.2,2,1,P);}
  if(i===5){const rp=new THREE.Group();const b=P3(new THREE.CylinderGeometry(.6,.6,5,24),wood,0,0,0,rp);b.rotation.z=Math.PI/2;for(const sd of [-1,1]){const h=P3(new THREE.CylinderGeometry(.22,.22,1.6,12),m('#6b3f22'),sd*3.2,0,0,rp);h.rotation.z=Math.PI/2;}rp.position.set(.5,.75,2.4);rp.rotation.y=.4;P.add(rp);}
  if(i===6){for(let k=0;k<4;k++){const bx=P3(new THREE.BoxGeometry(3.6,.5,3.6),m('#e8d6b0',.8),3.4,.3+k*.52,-.4,P);bx.rotation.y=k*.12;P3(new THREE.BoxGeometry(2,.02,.8),m('#b8311c'),3.4,.56+k*.52,-.4,P).rotation.y=k*.12;}}
  if(i===7){const cu=new THREE.Group();const wh=P3(new THREE.CylinderGeometry(1.5,1.5,.18,40),steel,0,0,0,cu);wh.rotation.x=Math.PI/2;P3(new THREE.BoxGeometry(.5,3.6,.4),m('#e0452c',.4),0,-2.2,0,cu);cu.position.set(3.2,3.2,.6);cu.rotation.z=-.35;P.add(cu);}}
const PORTRAITS=[];
function buildRoster(){const r=$('roster');
  const ps=new THREE.Scene();ps.background=new THREE.Color('#25150f');const penv=envFrom(THEMES.kitchen.env,[[128,40,40,'#ffffff'],[384,40,40,'#ffffff']]);ps.environment=penv;
  ps.add(new THREE.HemisphereLight('#fff1d6','#6b3a1e',.8));const dl=new THREE.DirectionalLight('#fff0d8',2.2);dl.position.set(10,20,12);ps.add(dl);
  const rim=new THREE.DirectionalLight('#9fd0ff',1.6);rim.position.set(-8,6,-10);ps.add(rim);const warm=new THREE.PointLight('#ffb070',1.2,40);warm.position.set(6,2,8);ps.add(warm);
  const PW=560,PH=380,pc=new THREE.PerspectiveCamera(26,PW/PH,.1,200);pc.position.set(0,5.4,21);pc.lookAt(0,4.1,0);
  renderer.shadowMap.autoUpdate=false;renderer.setPixelRatio(1);renderer.setSize(PW*2,PH*2,false);renderer.toneMappingExposure=1.05;
  const plM=new THREE.MeshStandardMaterial({color:'#e2b06a',roughness:.75}),saM=new THREE.MeshStandardMaterial({color:'#b8321d',roughness:.45}),chM=new THREE.MeshStandardMaterial({color:'#f6d36b',roughness:.4});
  RACERS.forEach((rc,i)=>{const b=document.createElement('button');b.className='card';b.id='driver-'+i;const c=cnv(PW*2,PH*2);
    const P=new THREE.Group();ps.add(P);P3(new THREE.CylinderGeometry(5.4,5.8,1,48),plM,0,-.5,0,P);P3(new THREE.CylinderGeometry(4.9,4.9,.12,48),saM,0,.06,0,P);P3(new THREE.CylinderGeometry(4.3,4.3,.14,48),chM,0,.12,0,P);
    const D=new THREE.Group();D.position.set(-.3,.2,0);D.rotation.set(0,.42+(i%2?.18:-.05),(i%3-1)*.07);P.add(D);buildDriver(D,rc);portraitProp(i,P);P.rotation.y=-.25;
    try{const g=c.getContext('2d');g.scale(2,2);g.imageSmoothingQuality='high';const gr=g.createRadialGradient(PW/2,PH*.42,10,PW/2,PH*.5,PH*.7);gr.addColorStop(0,shade(rc.color,-.25));gr.addColorStop(1,'#140a06');g.fillStyle=gr;g.fillRect(0,0,PW,PH);
      ps.background=null;renderer.setClearColor(0x000000,0);renderer.render(ps,pc);g.drawImage(renderer.domElement,0,0,PW,PH);}catch(e){}
    ps.remove(P);P.traverse(o=>{if(o.geometry&&!KGSET.has(o.geometry))o.geometry.dispose();});PORTRAITS[i]=c.toDataURL('image/jpeg',.9);
    const im=new Image();im.alt='';im.src=PORTRAITS[i];const n=document.createElement('b');n.textContent=rc.name;b.append(im,n);
    b.onclick=()=>{selected=i;store.set('crust-driver',i);refreshMenu();};r.appendChild(b);});
  renderer.setClearColor(0x000000,1);penv.dispose();renderer.shadowMap.autoUpdate=false;}
function fitLogo(){document.querySelectorAll('.home-brand .logo').forEach(el=>{el.style.fontSize='';const p=el.parentElement;if(!p||!p.clientWidth)return;const w=el.scrollWidth,a=p.clientWidth-4;if(w>a){const fs=parseFloat(getComputedStyle(el).fontSize);el.style.fontSize=Math.floor(fs*a/w)+'px';}});}
addEventListener('resize',()=>setTimeout(fitLogo,60));
function updateDriverDetail(){const el=$('drvDetail');if(!el||!PORTRAITS[selected])return;const B=BIOS[selected];el.innerHTML='<img class="hero" alt="" src="'+PORTRAITS[selected]+'"><span class="sub">Favourite prop · '+B[2]+'</span>'+(ABIL[RACERS[selected].name.toLowerCase()]?'<div class="abil"><i style="background:'+ABIL[RACERS[selected].name.toLowerCase()][2]+';color:'+ABIL[RACERS[selected].name.toLowerCase()][2]+'"></i><div><b>'+ABIL[RACERS[selected].name.toLowerCase()][0]+'</b> <span>'+ABIL[RACERS[selected].name.toLowerCase()][1]+'</span></div></div>':'')+'<h3>'+B[0]+'</h3><p>'+B[1]+'</p>';}

/* ================= GARAGE ================= */
const garage=$('garage');let gR=null,gS=null,gC=null,gModel=null,garageOpen=false,gRot=.6,gDrag=null,gW=0,gH=0;
function partChips(st){const out=[];st.forEach((v,i)=>{if(v)out.push('<em class="'+(v>0?'up':'dn')+'">'+(v>0?'+':'−')+Math.abs(v)+' '+STAT_SHORT[i]+'</em>');});return out.length?out.join(''):'<em class="nt">NEUTRAL</em>';}
function saveBuild(){store.set('crust-build',JSON.stringify(playerBuild));}
function buildSummary(){const lv=playerBuild.t&&livOf(playerBuild.t);return BODIES[playerBuild.b].name+(lv?' · '+lv.name:'')+' · '+WHEELS[playerBuild.w].name+' · '+GLIDERS[playerBuild.g].name+(statsOn?'':' · stats off');}
function buildGarage(){
  const mk=(wrap,list,key,idx)=>list.forEach((p,j)=>{const i=idx?idx[j]:j;const b=document.createElement('button');b.type='button';b.className='part';b.dataset.i=i;
    b.innerHTML='<b>'+p.name+'</b><span class="pd">'+p.desc+'</span><span class="chips">'+partChips(p.st)+'</span>';b.onclick=()=>{playerBuild[key]=i;if(key==='b'&&playerBuild.t&&!liveriesFor(BODIES[i].id).some(l=>l.id===playerBuild.t))playerBuild.t='';saveBuild();refreshGarage(true);};wrap.appendChild(b);});
  {const ki=[],ci=[];BODIES.forEach((p,i)=>(CAR_BODIES.includes(p.id)?ci:ki).push(i));mk($('pKart'),ki.map(i=>BODIES[i]),'b',ki);mk($('pCar'),ci.map(i=>BODIES[i]),'b',ci);}mk($('pWheel'),WHEELS,'w');mk($('pGlider'),GLIDERS,'g');$('pGlider').addEventListener('click',()=>{gGlT=3.2;});
  PAINTS.forEach((c,i)=>{const b=document.createElement('button');b.type='button';b.className='pw'+(c?'':' drv');b.dataset.i=i;b.setAttribute('aria-label',PAINT_NAMES[i]);b.title=PAINT_NAMES[i];if(c)b.style.background=c;
    b.onclick=()=>{playerBuild.p=i;playerBuild.t='';saveBuild();refreshGarage(true);};$('pPaint').appendChild(b);});
  $('gStats').innerHTML=STAT_NAMES.map(n=>'<div class="st-row"><span>'+n+'</span><span class="st-bar">'+'<i></i>'.repeat(7)+'</span><span class="st-d"></span></div>').join('');
  document.querySelectorAll('#statSeg button').forEach(b=>b.onclick=()=>{statsOn=b.dataset.s==='1';store.set('crust-stats',statsOn?'1':'0');refreshGarage(false);});
  $('gDone').onclick=()=>{if(gBig){setBig(false);return;}closeGarage();goStep('track');};$('garageBtn').onclick=()=>goStep('kart');$('gBack').onclick=()=>{if(gBig){setBig(false);return;}closeGarage();goStep('driver');};
  $('toDriver').onclick=()=>goStep('driver');document.querySelectorAll('#menu .st-back').forEach(b=>b.onclick=()=>goStep(b.dataset.back));
  document.querySelectorAll('.g-tabs button').forEach(t=>t.onclick=()=>{gTab=t.dataset.tab;if(gTab==='glider')gGlT=3.2;refreshGarage(false);});
  const cv=$('gCan'),PT=new Map();let pinch0=0,zoom0=1,tap=null;
  cv.addEventListener('pointerdown',e=>{PT.set(e.pointerId,{x:e.clientX,y:e.clientY});try{cv.setPointerCapture(e.pointerId);}catch(_){}
    if(PT.size===1){gDrag={x:e.clientX,y:e.clientY,r:gRot,p:gPitch};tap={x:e.clientX,y:e.clientY,t:performance.now()};}
    else if(PT.size===2){const [a,b]=[...PT.values()];pinch0=Math.hypot(a.x-b.x,a.y-b.y);zoom0=gZoom;gDrag=null;tap=null;}});
  cv.addEventListener('pointermove',e=>{if(!PT.has(e.pointerId))return;PT.set(e.pointerId,{x:e.clientX,y:e.clientY});
    if(PT.size===2&&pinch0>0){const [a,b]=[...PT.values()];gZoom=clamp(zoom0*pinch0/Math.max(1,Math.hypot(a.x-b.x,a.y-b.y)),.32,1.5);return;}
    if(gDrag){gRot=gDrag.r+(e.clientX-gDrag.x)*.011;if(gBig)gPitch=clamp(gDrag.p+(e.clientY-gDrag.y)*.006,-.12,1.1);if(tap&&Math.hypot(e.clientX-tap.x,e.clientY-tap.y)>7)tap=null;}});
  const up=e=>{PT.delete(e.pointerId);if(PT.size<2)pinch0=0;if(tap&&!gBig&&performance.now()-tap.t<350)setBig(true);tap=null;if(!PT.size)gDrag=null;};
  cv.addEventListener('pointerup',up);cv.addEventListener('pointercancel',up);
  cv.addEventListener('wheel',e=>{e.preventDefault();gZoom=clamp(gZoom*Math.exp(e.deltaY*.0012),.32,1.5);if(!gBig&&e.deltaY<0)setBig(true);},{passive:false});
  $('gZoomBtn').onclick=()=>setBig(!gBig);}
let gBig=false,gZoom=1,gPitch=0,gZc=1,gPc=0;
function setBig(v){gBig=v;$('gView').classList.toggle('big',v);gW=gH=0;if(!v){gZoom=1;gPitch=0;}$('gZoomBtn').setAttribute('aria-label',v?'Close inspect view':'Inspect kart');}
const CAR_BODIES=['hyper','roadster','formula','gt','tourer','concept','interceptor','muscle','monster','hatch','suv','coupe','scissor'];let gTab='kart';
function refreshGarage(rebuild){
  document.querySelectorAll('.g-tabs button').forEach(t=>t.setAttribute('aria-selected',String(t.dataset.tab===gTab)));document.querySelectorAll('.g-panel').forEach(p=>p.hidden=p.dataset.panel!==gTab);
  {const lv=playerBuild.t&&livOf(playerBuild.t),it=(gTab==='kart'||gTab==='car')?BODIES[playerBuild.b]:gTab==='wheel'?WHEELS[playerBuild.w]:gTab==='glider'?GLIDERS[playerBuild.g]:null;
   $('gDesc').innerHTML=it?'<b>'+it.name+'.</b> '+it.desc:lv?'<b>'+lv.name+'.</b> '+(lv.only?'A signature theme made for the '+BODIES[playerBuild.b].name+'.':'A multi-colour livery.')+' Pick a solid colour to go back to plain paint.':gTab==='theme'?'Multi-colour liveries. Themes marked ★ are made for the '+BODIES[playerBuild.b].name+'.':'<b>'+PAINT_NAMES[playerBuild.p]+'.</b> Solid paint. The Theme tab has full multi-colour liveries.';}
  [['pKart','b'],['pCar','b'],['pWheel','w'],['pGlider','g']].forEach(([id,k])=>$(id).querySelectorAll('button').forEach(b=>b.setAttribute('aria-pressed',String(+b.dataset.i===playerBuild[k]))));
  $('pPaint').querySelectorAll('button').forEach(b=>b.setAttribute('aria-pressed',String(!playerBuild.t&&+b.dataset.i===playerBuild.p)));
  const bid=BODIES[playerBuild.b].id,tw=$('pTheme');tw.innerHTML='';
  const fc=$('pThemeCats');if(fc&&!fc.childElementCount)LIV_CATS.forEach(([k,n])=>{const b=document.createElement('button');b.type='button';b.dataset.c=k;b.textContent=n;b.onclick=()=>{livCat=k;refreshGarage(false);};fc.appendChild(b);});
  if(fc)fc.querySelectorAll('button').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.c===livCat)));
  for(const lv of liveriesFor(bid).filter(l=>livCat==='all'||(livCat==='sig'?l.only:(l.cat===livCat)))){const b=document.createElement('button');b.type='button';b.className='theme';b.setAttribute('aria-pressed',String(playerBuild.t===lv.id));
    b.innerHTML='<i style="background:linear-gradient(135deg,'+lv.A+' 0 46%,'+lv.B+' 46% 62%,'+lv.C+' 62% 72%,'+lv.A+' 72%)"></i><b>'+(lv.only?'★ ':'')+lv.name+'</b>';
    b.onclick=()=>{playerBuild.t=lv.id;saveBuild();refreshGarage(true);};tw.appendChild(b);}
  const ds=$('pPaint').querySelector('.drv');if(ds)ds.style.background=RACERS[selected].color;
  const st=sumStats(playerBuild);
  $('gStats').querySelectorAll('.st-row').forEach((r,i)=>{const v=clamp(3+st[i],0,6);r.querySelectorAll('i').forEach((c,j)=>{c.classList.toggle('on',j<=v);c.classList.toggle('mid',j===3);});
    const d=r.querySelector('.st-d');d.textContent=st[i]?(st[i]>0?'+':'−')+Math.abs(st[i]):'0';d.className='st-d'+(st[i]>0?' up':st[i]<0?' dn':'');});
  $('gStats').classList.toggle('off',!statsOn);
  document.querySelectorAll('#statSeg button').forEach(b=>b.setAttribute('aria-pressed',String((b.dataset.s==='1')===statsOn)));
  $('statNote').textContent=statsOn?'Parts change how your kart drives, and CPU karts use their parts too. Each strength comes with a drawback.':'Stats are off. Every kart drives the same and parts only change the look.';
  $('gName').textContent=RACERS[selected].name+'’s '+BODIES[playerBuild.b].name;
  $('buildSum').textContent=buildSummary();
  if(rebuild&&garageOpen)setPreview();}
function setPreview(){if(!gR)return;if(gModel){gS.remove(gModel.g);disposeModel(gModel);gModel=null;}
  gModel=buildKart(Object.assign({ri:selected},playerBuild));gModel.g.scale.setScalar(gModel.sf);gModel.g.traverse(o=>{if(o.isMesh){o.castShadow=true;}});gS.add(gModel.g);gModel.pga=gGlT>0?1:0;
  {gModel.gl.visible=false;gModel.g.rotation.y=0;gModel.g.updateMatrixWorld(true);const bb=new THREE.Box3(),tb=new THREE.Box3();gModel.g.traverseVisible(o=>{if(o.isMesh&&o.geometry){if(!o.geometry.boundingBox)o.geometry.computeBoundingBox();tb.copy(o.geometry.boundingBox).applyMatrix4(o.matrixWorld);bb.union(tb);}});gModel.rad=bb.getSize(new THREE.Vector3()).length()*.5;gModel.cy=(bb.min.y+bb.max.y)/2;}}
let gGlT=0;
function frameGarageCam(ga,dt){gZc+=(gZoom-gZc)*Math.min(1,(dt||.016)*10);gPc+=(gPitch-gPc)*Math.min(1,(dt||.016)*10);const rad=(gModel.rad||8)+ga*3,ty=(gModel.cy||3)+ga*3.5,vh=15*Math.PI/180,hh=Math.atan(Math.tan(vh)*(gC.aspect||1.6)),d=rad/Math.sin(Math.min(vh,hh))*(gBig?.95:1.02)*gZc,el=.22+gPc,hz=Math.cos(el)*d,sh=gBig?0:rad*.34*Math.min(1,(gC.aspect||1)/1.3);
  gC.position.set(hz*.756-sh*.654,ty+Math.sin(el)*d,hz*.654+sh*.756);gC.lookAt(-sh*.654,ty-(gBig?0:rad*.24),sh*.756);}
function openGarage(){garageOpen=true;menu.hidden=true;garage.hidden=false;
  if(!gR){try{gR=new THREE.WebGLRenderer({canvas:$('gCan'),antialias:true,alpha:true,powerPreference:'high-performance'});gR.setClearColor(0x000000,0);gR.outputEncoding=THREE.sRGBEncoding;gR.toneMapping=THREE.ACESFilmicToneMapping;gR.toneMappingExposure=1.05;
    gS=new THREE.Scene();gS.environment=envFrom(THEMES.kitchen.env,[[128,40,40,'#ffffff'],[384,40,40,'#ffffff'],[256,140,40,'#ff8a2a']]);
    gS.add(new THREE.HemisphereLight('#fff1d6','#6b3a1e',.75));const dl=new THREE.DirectionalLight('#fff0d8',2.4);dl.position.set(10,22,12);dl.castShadow=true;dl.shadow.mapSize.set(1024,1024);Object.assign(dl.shadow.camera,{left:-12,right:12,top:12,bottom:-12,near:1,far:60});dl.shadow.bias=-.0005;gS.add(dl);gR.shadowMap.enabled=true;gR.shadowMap.type=THREE.PCFSoftShadowMap;
    const fl=new THREE.Mesh(new THREE.CircleGeometry(15.5,64),new THREE.MeshStandardMaterial({color:'#3a2216',roughness:.85}));fl.rotation.x=-Math.PI/2;fl.receiveShadow=true;gS.add(fl);
    const rg=new THREE.Mesh(new THREE.RingGeometry(14.3,15,64),new THREE.MeshBasicMaterial({color:'#f7c948',toneMapped:false}));rg.rotation.x=-Math.PI/2;rg.position.y=.03;gS.add(rg);
    gC=new THREE.PerspectiveCamera(30,1.6,.1,500);}catch(e){gR=null;}}
  gW=gH=0;gTab=CAR_BODIES.includes(BODIES[playerBuild.b].id)?'car':'kart';refreshGarage(true);garage.scrollTop=0;}
function closeGarage(){if(gBig){setBig(false);return;}garageOpen=false;garage.hidden=true;menu.hidden=false;if(gModel){gS.remove(gModel.g);disposeModel(gModel);gModel=null;}refreshMenu();}
function renderGarage(dt){if(!gR||!gModel)return;const c=gR.domElement,w=c.clientWidth,h=c.clientHeight;if(!w||!h)return;
  if(w!==gW||h!==gH){gW=w;gH=h;gR.setPixelRatio(Math.min(DPR,2));gR.setSize(w,h,false);gC.aspect=w/h;gC.updateProjectionMatrix();}
  if(!gDrag&&!RM&&!gBig)gRot+=dt*.4;gModel.g.rotation.y=gRot;for(const wl of gModel.wheels)wl.spin.rotation.z-=dt*2.5;
  gGlT-=dt;gModel.pga+=((gGlT>0?1:0)-gModel.pga)*Math.min(1,dt*5);const ga=gModel.pga;gModel.gl.visible=ga>.02;gModel.gl.scale.setScalar(Math.max(.01,ga));
  gModel.gl.rotation.z=Math.sin(performance.now()/700)*.05;frameGarageCam(ga*ga*(3-2*ga),dt);gR.render(gS,gC);}


/* screen pass: the scene renders into a multisampled HDR buffer, bright highlights bloom at quarter resolution,
   then one final pass tone-maps (ACES), grades and vignettes. Skipped entirely on the Fast setting. */
const POST={rt:null,b1:null,b2:null,b3:null,b4:null,w:0,h:0,qs:null,qc:null,q:null,M:{},grade:{sat:1.08,con:1.06,tint:[1,1,1],vig:.28,bloom:.55,thr:.85}};
function postMat(frag,u){return new THREE.ShaderMaterial({uniforms:u,vertexShader:'varying vec2 vUv;void main(){vUv=uv;gl_Position=vec4(position.xy,0.,1.);}',fragmentShader:frag,depthTest:false,depthWrite:false,toneMapped:false});}
function postInit(){if(POST.qs)return;POST.qs=new THREE.Scene();POST.qc=new THREE.OrthographicCamera(-1,1,1,-1,0,1);const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute([-1,-1,0,3,-1,0,-1,3,0],3));g.setAttribute('uv',new THREE.Float32BufferAttribute([0,0,2,0,0,2],2));
  POST.q=new THREE.Mesh(g);POST.q.frustumCulled=false;POST.qs.add(POST.q);
  POST.M.bright=postMat('uniform sampler2D tex;uniform float thr;uniform vec2 px;varying vec2 vUv;void main(){vec3 c=vec3(0.);for(int i=0;i<4;i++){vec2 o=vec2(i==1||i==3?1.:-1.,i>1?1.:-1.)*px;c+=texture2D(tex,vUv+o).rgb;}c*=.25;float l=dot(c,vec3(.2126,.7152,.0722));c*=smoothstep(thr,thr*1.6+.4,l);gl_FragColor=vec4(min(c,vec3(8.)),1.);}',{tex:{value:null},thr:{value:.85},px:{value:new THREE.Vector2()}});
  POST.M.blur=postMat('uniform sampler2D tex;uniform vec2 dir;varying vec2 vUv;void main(){vec3 c=texture2D(tex,vUv).rgb*.227027;c+=(texture2D(tex,vUv+dir*1.3846).rgb+texture2D(tex,vUv-dir*1.3846).rgb)*.316216;c+=(texture2D(tex,vUv+dir*3.2308).rgb+texture2D(tex,vUv-dir*3.2308).rgb)*.070270;gl_FragColor=vec4(c,1.);}',{tex:{value:null},dir:{value:new THREE.Vector2()}});
  POST.M.final=postMat(`uniform sampler2D tex,b1,b2;uniform float exposure,bloom,sat,con,vig,aspect;uniform vec3 tint;varying vec2 vUv;
    vec3 RRT(vec3 v){vec3 a=v*(v+.0245786)-.000090537;vec3 b=v*(.983729*v+.4329510)+.238081;return a/b;}
    vec3 aces(vec3 c){const mat3 I=mat3(.59719,.07600,.02840,.35458,.90834,.13383,.04823,.01566,.83777);const mat3 O=mat3(1.60475,-.10208,-.00327,-.53108,1.10813,-.07276,-.07367,-.00605,1.07602);c*=exposure/.6;c=I*c;c=RRT(c);c=O*c;return clamp(c,0.,1.);}
    vec3 srgb(vec3 c){return mix(c*12.92,1.055*pow(c,vec3(1./2.4))-.055,step(vec3(.0031308),c));}
    void main(){vec3 c=texture2D(tex,vUv).rgb+(texture2D(b1,vUv).rgb*.65+texture2D(b2,vUv).rgb*.6)*bloom;c=aces(c*tint);
      float l=dot(c,vec3(.2126,.7152,.0722));c=mix(vec3(l),c,sat);c=clamp((c-.5)*con+.5,0.,1.);
      vec2 d=(vUv-.5)*vec2(aspect,1.);c*=1.-vig*smoothstep(.35,1.05,length(d));
      gl_FragColor=vec4(srgb(c),1.);}`,{tex:{value:null},b1:{value:null},b2:{value:null},exposure:{value:1},bloom:{value:.55},sat:{value:1.08},con:{value:1.06},vig:{value:.28},aspect:{value:1},tint:{value:new THREE.Vector3(1,1,1)}});}
function postSize(w,h){const msN=LADV.ms===0?0:pr>=1.25?2:4;if(POST.w===w&&POST.h===h&&POST.rt&&POST.ms===msN)return;POST.ms=msN;POST.w=w;POST.h=h;for(const k of ['rt','b1','b2','b3','b4'])if(POST[k])POST[k].dispose();
  const ht=renderer.capabilities.isWebGL2?THREE.HalfFloatType:THREE.UnsignedByteType,opt={type:ht,depthBuffer:false};
  POST.rt=new THREE.WebGLRenderTarget(w,h,{type:ht,samples:renderer.capabilities.isWebGL2?msN:0});POST.pr=pr;
  const w4=Math.max(1,w>>2),h4=Math.max(1,h>>2),w8=Math.max(1,w>>3),h8=Math.max(1,h>>3);
  POST.b1=new THREE.WebGLRenderTarget(w4,h4,opt);POST.b2=new THREE.WebGLRenderTarget(w4,h4,opt);POST.b3=new THREE.WebGLRenderTarget(w8,h8,opt);POST.b4=new THREE.WebGLRenderTarget(w8,h8,opt);}
function pass(mat,target){POST.q.material=mat;renderer.setRenderTarget(target);renderer.render(POST.qs,POST.qc);}
function postRender(){postInit();const sz=renderer.getDrawingBufferSize(v2);postSize(sz.x,sz.y);const M=POST.M,G=POST.grade;
  renderer.setRenderTarget(POST.rt);renderer.render(scene,camera);
  M.bright.uniforms.tex.value=POST.rt.texture;M.bright.uniforms.thr.value=G.thr;M.bright.uniforms.px.value.set(1/sz.x,1/sz.y);pass(M.bright,POST.b1);
  const bl=(a,b,w,h)=>{M.blur.uniforms.tex.value=a.texture;M.blur.uniforms.dir.value.set(1/w,0);pass(M.blur,b);M.blur.uniforms.tex.value=b.texture;M.blur.uniforms.dir.value.set(0,1/h);pass(M.blur,a);};
  bl(POST.b1,POST.b2,POST.b1.width,POST.b1.height);M.blur.uniforms.tex.value=POST.b1.texture;M.blur.uniforms.dir.value.set(.5/POST.b1.width,0);pass(M.blur,POST.b3);bl(POST.b3,POST.b4,POST.b3.width,POST.b3.height);bl(POST.b3,POST.b4,POST.b3.width,POST.b3.height);
  const F=M.final.uniforms;F.tex.value=POST.rt.texture;F.b1.value=POST.b1.texture;F.b2.value=POST.b3.texture;F.exposure.value=renderer.toneMappingExposure;F.bloom.value=G.bloom;F.sat.value=G.sat;F.con.value=G.con;F.vig.value=G.vig;F.aspect.value=sz.x/sz.y;F.tint.value.set(...G.tint);
  pass(M.final,null);}
function fit(){const w=stage.clientWidth,h=stage.clientHeight;if(!w||!h)return;renderer.setPixelRatio(pr);renderer.setSize(w,h,false);camera.aspect=w/h;camera.updateProjectionMatrix();}

/* ================= BOOT ================= */
let booted=false;
async function loadExt(step){const X=window.CR_EXT;if(!X)return;let buf;
  try{const r=await fetch(X.geo);if(!r.ok)throw new Error(r.status);const tot=+r.headers.get('content-length')||X.size;
    if(r.body&&r.body.getReader){const rd=r.body.getReader(),u=new Uint8Array(X.size);let o=0,lastP=-1;
      for(;;){const {done,value}=await rd.read();if(done)break;if(o+value.length>u.length)throw new Error('size');u.set(value,o);o+=value.length;const p=Math.floor(o/X.size*100);if(p>=lastP+4){lastP=p;await step(2+8*o/X.size,'Loading karts and props… '+p+'%');}}
      if(o!==X.size)throw new Error('short');buf=u.buffer;}
    else buf=await r.arrayBuffer();}
  catch(e){const t=document.getElementById('ldTxt');if(t)t.textContent='Could not load the game files. Check your connection and reload.';throw e;}
  for(const [kind,id,o,n] of X.ofs){const tgt=kind==='c'?CAR_PACKS[id]:PROP_PACKS[id];if(tgt)tgt.b=buf.slice(o,o+n);}}
async function boot(){const ld=document.getElementById('loader'),bar=document.getElementById('ldBar'),txt=document.getElementById('ldTxt');
  /* while the page and engine download, the bar creeps forward on its own; from here every step is real work */
  const W0=()=>{const w=bar.getBoundingClientRect().width,t=bar.parentNode.getBoundingClientRect().width;return t?w/t*100:0;};let cur=Math.max(3,W0());bar.classList.add('live');bar.style.width=cur+'%';const span=100-cur;
  const step=async(p,t)=>{cur=Math.max(cur,(100-span)+span*p/100);bar.style.width=cur.toFixed(1)+'%';if(t)txt.textContent=t;await new Promise(r=>requestAnimationFrame(()=>setTimeout(r,0)));};
  await loadExt(step);
  await step(12,'Kneading the dough…');cpuBuilds=RACERS.map(randomBuild);initRings();
  await step(22,'Drawing the tracks…');buildMapCards();
  await step(34,'Seating the drivers…');buildRoster();
  await step(48,'Plating the items…');try{renderItemIcons();}catch(e){}
  await step(56,'Opening the garage…');buildGarage();
  {const ids=Object.keys(CAR_PACKS).filter(k=>!k.endsWith('_hq'));for(let i=0;i<ids.length;i++){await step(60+14*i/ids.length,i?null:'Tuning the karts…');carGeos(ids[i]);}}
  await step(74,'Building the track…');if(mode==='gp')mapIdx=CUP_TRACKS[cupIdx][0];loadMap(mapIdx,false);fit();refreshMenu();
  if(window.ResizeObserver)new ResizeObserver(fit).observe(stage);else addEventListener('resize',fit);
  applySettings();
  await step(88,'Lining up the grid…');resetRace(true);
  await step(96,'Firing up the oven…');try{renderer.compile(scene,camera);}catch(e){}
  booted=true;bar.style.width='100%';menu.hidden=false;last=performance.now();setTimeout(()=>{ld.classList.add('done');setTimeout(()=>ld.remove(),600);},120);}

let last=performance.now(),resTick=0,perfT=0,perfN=0,perfSum=0,raisedAt=-1;
let bestDt=1;const HZ=[1/165,1/144,1/120,1/90,1/75,1/60,1/50,1/30];
const _sA=new THREE.Vector3(),_sB=new THREE.Vector3(),_sT=new THREE.Vector3();
function snapSun(x,y,z){const sc=sun.shadow.camera,tx=(sc.right-sc.left)/sun.shadow.mapSize.x;_sA.set(0,1,0).cross(sunDir).normalize();_sB.copy(sunDir).cross(_sA).normalize();
  _sT.set(x,y,z);const a=Math.round(_sT.dot(_sA)/tx)*tx,b=Math.round(_sT.dot(_sB)/tx)*tx,c=Math.round(_sT.dot(sunDir)/4)*4;
  _sT.copy(_sA).multiplyScalar(a).addScaledVector(_sB,b).addScaledVector(sunDir,c);sun.target.position.copy(_sT);sun.position.copy(_sT).addScaledVector(sunDir,500);}
/* Frame-rate ladder. When frames run long the game steps down one rung at a time, cheapest-looking change first;
   when it has headroom for a while it steps back up. The last steady rung is remembered for the next session. */
const LADS=[{p:0},{p:0,lod:1},{p:.15,lod:1},{p:.15,ms:0,lod:1},{p:.15,ms:0,sm:.5,lod:1},{p:.3,ms:0,sm:.5,lod:1,det:1},{p:.5,ms:0,sm:.5,lod:1,det:1},{p:9,ms:0,sm:.5,lod:1,det:1},{p:9,ms:0,sm:.5,lod:1,det:1,np:1}];
let LAD=0,ladBest=0,LADV=LADS[0];
function ladKey(){return 'crust-lad-'+qKey;}
function applyLad(n,save){LAD=clamp(n,0,LADS.length-1);LADV=LADS[LAD];const q=QUAL[qKey],fl=Math.min(DPR,q.floor);
  const np=Math.max(fl,Math.min(DPR,q.start)-LADV.p);if(Math.abs(np-pr)>.01){pr=np;fitPending=true;}
  const sm=Math.max(512,Math.round(q.sm*(LADV.sm||1)));if(sun.shadow.mapSize.x!==sm){sun.shadow.mapSize.set(sm,sm);if(sun.shadow.map){sun.shadow.map.dispose();sun.shadow.map=null;}}
  LODM=0;LODF=LADV.lod?150:200;if(save)store.set(ladKey(),String(LAD));}
function adaptQuality(dt,time){perfSum+=dt;perfN++;perfT+=dt;if(perfT<1)return;const avg=perfSum/perfN;perfT=perfSum=perfN=0;
  bestDt=Math.min(bestDt*1.01,avg);let P=1/60;for(const h of HZ)if(h>=bestDt*.93){P=h;break;}if(CFG.fps==='60')P=Math.max(P,1/60);
  if(state!=='race'&&state!=='countdown')return;
  slowN=avg>P*1.1?slowN+1:0;fastN=avg<P*1.03?fastN+1:0;
  if((slowN>=2||(slowN>=1&&avg>P*1.5))&&LAD<LADS.length-1){if(raisedAt>0&&time-raisedAt<12)ladBest=LAD+1;applyLad(LAD+(avg>P*1.6&&LAD<4?2:1),true);droppedAt=time;slowN=0;}
  else if(fastN>=10&&LAD>ladBest&&time-droppedAt>25){applyLad(LAD-1,true);raisedAt=time;fastN=0;}}
let slowN=0,fastN=0,droppedAt=-99,fitPending=false;
{const v=+store.get(ladKey());if(v>0)applyLad(v,false);}
let lastFrameT=0,fpsN=0,fpsT=0;
/* ================= MUSIC =================
   Every song is composed on the fly by a small synth sequencer: drums, bass, chords, arpeggio and a lead line.
   Each track has its own tempo, key, mode, groove and instruments; the melodies come from a seeded generator,
   so a song is always the same each time you hear it. Two menu songs take turns. */
const MODES={major:[0,2,4,5,7,9,11],minor:[0,2,3,5,7,8,10],dorian:[0,2,3,5,7,9,10],mixo:[0,2,4,5,7,9,10],harm:[0,2,3,5,7,8,11],lydian:[0,2,4,6,7,9,11]};
const KITS={
  four:{k:'x...x...x...x...',s:'....x.......x...',h:'..x...x...x...x.',g:'x.x.x.x.x.x.x.x.'},
  disco:{k:'x...x...x...x...',s:'....x.......x...',h:'x.x.x.x.x.x.x.x.',o:'..x...x...x...x.'},
  rock:{k:'x.....x.x.......',s:'....x.......x...',h:'x.x.x.x.x.x.x.x.'},
  drive:{k:'x...x.x.x...x.x.',s:'....x.......x..x',h:'x.x.x.x.x.x.x.x.',o:'..............x.'},
  brk:{k:'x..x..x...x.....',s:'....x..x....x..x',h:'x.xxx.xxx.xxx.xx'},
  half:{k:'x.........x.....',s:'........x.......',h:'x.x.x.x.x.x.x.x.'},
  calyp:{k:'x..x..x.x..x..x.',s:'...x...x...x..x.',h:'xxxxxxxxxxxxxxxx'},
  swing:{k:'x.......x.......',s:'....x.......x...',r:'x...x.x.x...x.x.'},
  chip:{k:'x...x...x...x...',s:'....x.......x...',h:'..x...x...x...x.'},
  gallop:{k:'x.xx..x.x.xx..x.',s:'....x.......x...',h:'x.x.x.x.x.x.x.x.',o:'......x.......x.'}};
const BASSP={eighth:'r.r.r.r.r.r.r.r.',octave:'r.R.r.R.r.R.r.R.',synco:'r..r..r...r.r...',pump:'r.rrr.rrr.rrr.rr',half:'r.......r.......',calyp:'r..r..f.r..r..f.',drive:'rrr.rrr.rrr.rrfR',funk:'r..R..r.f.r.R...',walk:'w...w...w...w...',root:'r...........f...'};
/* bpm, key (0=C), mode, chord degrees per bar for parts A and B, groove, bass line, sounds */
const SONGS={
  menu1:{n:'Dough Rising',bpm:94,key:5,mode:'major',A:[0,5,3,4],B:[3,4,2,5],kit:'half',bass:'synco',lead:'tri',pad:'warm',arp:'up8',swing:.18,seed:11,sev:1,dens:.45},
  menu2:{n:'Slice of Sunshine',bpm:116,key:2,mode:'major',A:[0,4,5,3],B:[3,0,4,4],kit:'four',bass:'octave',lead:'square',pad:'warm',arp:'pluck',swing:0,seed:23,dens:.55},
  margherita:{bpm:148,key:0,mode:'major',A:[0,3,4,0],B:[5,3,1,4],kit:'drive',bass:'eighth',lead:'square',pad:'bright',arp:'up16',swing:0,seed:101,dens:.6},
  bay:{bpm:156,key:9,mode:'mixo',A:[0,6,3,0],B:[3,3,0,4],kit:'rock',bass:'drive',lead:'surf',pad:'none',arp:'strum',swing:0,seed:102,dens:.65},
  peaks:{bpm:138,key:4,mode:'minor',A:[0,5,6,4],B:[3,4,0,0],kit:'drive',bass:'pump',lead:'saw',pad:'dark',arp:'up16',swing:0,seed:103,dens:.55},
  frosty:{bpm:126,key:7,mode:'major',A:[0,2,3,4],B:[5,2,3,4],kit:'four',bass:'octave',lead:'bell',pad:'glass',arp:'updown16',swing:0,seed:104,sev:1,dens:.5},
  basil:{bpm:108,key:2,mode:'dorian',A:[0,3,0,3],B:[6,3,4,4],kit:'brk',bass:'funk',lead:'square',pad:'warm',arp:'none',swing:.22,seed:105,sev:1,dens:.6},
  lagoon:{bpm:118,key:5,mode:'major',A:[0,3,4,0],B:[3,0,4,4],kit:'calyp',bass:'calyp',lead:'marimba',pad:'none',arp:'pluck',swing:.08,seed:106,dens:.7},
  mozz:{bpm:124,key:10,mode:'dorian',A:[0,0,3,4],B:[5,3,6,4],kit:'disco',bass:'octave',lead:'saw',pad:'strings',arp:'none',swing:0,seed:107,sev:1,dens:.5},
  burn:{bpm:166,key:4,mode:'harm',A:[0,0,5,4],B:[3,5,4,4],kit:'gallop',bass:'pump',lead:'saw',pad:'dark',arp:'up16',swing:0,seed:108,dens:.62},
  oven:{bpm:104,key:3,mode:'major',A:[1,4,0,5],B:[3,2,1,4],kit:'swing',bass:'walk',lead:'tri',pad:'ep',arp:'none',swing:.33,seed:109,sev:1,dens:.5},
  calzone:{bpm:112,key:1,mode:'minor',A:[0,5,2,6],B:[3,4,0,0],kit:'four',bass:'eighth',lead:'saw',pad:'dark',arp:'up16',swing:0,seed:110,sev:1,dens:.45},
  napoli:{bpm:172,key:9,mode:'harm',A:[0,0,4,4],B:[3,0,4,0],kit:'chip',bass:'eighth',lead:'square',pad:'none',arp:'updown16',swing:0,seed:111,dens:.75},
  glacier:{bpm:100,key:11,mode:'lydian',A:[0,1,0,1],B:[5,4,3,4],kit:'half',bass:'half',lead:'bell',pad:'glass',arp:'up8',swing:0,seed:112,sev:1,dens:.4},
  spiral:{bpm:176,key:0,mode:'major',A:[0,5,3,4],B:[0,3,4,4],kit:'chip',bass:'octave',lead:'pulse',pad:'none',arp:'updown16',swing:0,seed:113,dens:.7},
  tour:{bpm:146,key:7,mode:'mixo',A:[0,6,3,0],B:[3,6,0,4],kit:'rock',bass:'eighth',lead:'surf',pad:'none',arp:'strum',swing:0,seed:114,dens:.6},
  moon:{bpm:116,key:8,mode:'minor',A:[0,6,5,6],B:[3,4,5,4],kit:'half',bass:'synco',lead:'sine',pad:'space',arp:'up16',swing:0,seed:115,sev:1,dens:.42},
  peak:{bpm:152,key:2,mode:'minor',A:[0,5,2,6],B:[3,4,5,4],kit:'drive',bass:'pump',lead:'saw',pad:'strings',arp:'up16',swing:0,seed:116,dens:.58}};
const MENU_SONGS=['menu1','menu2'];
/* form: intro 4 bars (drums+chords), A 8, B 8, A 8, break 4 (chords+arp), then back to A */
const FORM=[['I',4],['A',8],['B',8],['A2',8],['X',4]];
const MUS={on:false,gain:null,bus:null,key:null,want:null,song:null,t:0,step:0,bar:0,fadeT:0,menuI:0,menuBars:0,noise:null,mel:null};
function mrand(seed){let a=seed>>>0;return ()=>{a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296;};}
const mtof=m=>440*Math.pow(2,(m-69)/12);
/* scale degree (can run past 7) -> midi note */
function deg(S,d,oct){const sc=MODES[S.mode],o=Math.floor(d/7),i=((d%7)+7)%7;return 12*(oct+o)+S.key+sc[i];}
function progAt(S,sec,b){const P=sec==='B'?S.B:S.A;return P[b%P.length];}
/* lead melody: one 2-bar motif per part, repeated on the next chord, answered, then resolved */
function buildMelody(S){const R=mrand(S.seed*7919+3),M={};
  for(const sec of ['A','B']){const bars=[];
    const rhy=[];for(let i=0;i<32;i++){const strong=i%4===0,p=strong?S.dens+.25:i%2===0?S.dens:S.dens*.35;rhy.push(R()<p);}rhy[0]=true;
    const shape=[];let d=0;for(let i=0;i<32;i++){d+=R()<.5?(R()<.5?1:-1):(R()<.3?(R()<.5?2:-2):0);d=Math.max(-3,Math.min(5,d));shape.push(d);}
    const holdR=[];for(let i=0;i<32;i++)holdR.push(R()<.35);
    for(let b=0;b<8;b++){const ph=Math.floor(b/2),inP=b%2,notes=[];
      for(let s=0;s<16;s++){const i=inP*16+s;if(!rhy[i])continue;
        const ch=progAt(S,sec,b);let dd=ch+shape[i]+(ph===2?2:0);
        if(s%4===0){const ct=[ch,ch+2,ch+4,ch+7];dd=ct.reduce((a,c)=>Math.abs(c-dd)<Math.abs(a-dd)?c:a,ct[0]);}
        if(ph===3&&inP===1&&s>=8){if(s===8)dd=ch+(sec==='A'?7:4);else continue;}
        let len=1;while(len<6&&s+len<16&&!rhy[inP*16+s+len]&&holdR[i])len++;
        notes.push([s,dd,len]);}
      bars.push(notes);}
    M[sec]=bars;}
  return M;}
function musNoise(){if(MUS.noise)return MUS.noise;const n=ac.sampleRate*1,b=ac.createBuffer(1,n,ac.sampleRate),d=b.getChannelData(0);for(let i=0;i<n;i++)d[i]=Math.random()*2-1;return MUS.noise=b;}
function musInit(){if(MUS.bus||!ac||!master)return;MUS.gain=ac.createGain();MUS.gain.gain.value=0;MUS.gain.connect(master);MUS.bus=ac.createGain();MUS.bus.gain.value=.34;MUS.bus.connect(MUS.gain);
  MUS.rev=ac.createGain();MUS.rev.gain.value=.5;MUS.bus.connect(MUS.rev);if(typeof revBus!=='undefined'&&revBus)MUS.rev.connect(revBus);
  MUS.dly=ac.createDelay(1);MUS.fb=ac.createGain();MUS.fb.gain.value=.28;MUS.dlyIn=ac.createGain();MUS.dlyIn.gain.value=.22;MUS.dlyIn.connect(MUS.dly);MUS.dly.connect(MUS.fb);MUS.fb.connect(MUS.dly);MUS.dly.connect(MUS.bus);}
function env(g,t,a,peak,d,sus,rel,end){g.gain.setValueAtTime(0,t);g.gain.linearRampToValueAtTime(peak,t+a);g.gain.setTargetAtTime(peak*sus,t+a,d);g.gain.setTargetAtTime(0,end,rel);}
function voice(f,t,dur,o){const os=ac.createOscillator(),g=ac.createGain();os.type=o.w||'square';os.frequency.setValueAtTime(f,t);if(o.det)os.detune.value=o.det;
  let last=os;if(o.lp){const lp=ac.createBiquadFilter();lp.type='lowpass';lp.frequency.setValueAtTime(o.lp,t);if(o.lpEnv){lp.frequency.setValueAtTime(o.lp*o.lpEnv,t);lp.frequency.setTargetAtTime(o.lp,t,o.lpT||.08);}lp.Q.value=o.q||.7;last.connect(lp);last=lp;}
  if(o.vib){const v=ac.createOscillator(),vg=ac.createGain();v.frequency.value=o.vib;vg.gain.value=f*.012;v.connect(vg);vg.connect(os.frequency);v.start(t+.12);v.stop(t+dur+.6);}
  if(o.fm){const m=ac.createOscillator(),mg=ac.createGain();m.frequency.value=f*o.fm;mg.gain.setValueAtTime(f*(o.fmA||2),t);mg.gain.setTargetAtTime(0,t,o.fmT||.15);m.connect(mg);mg.connect(os.frequency);m.start(t);m.stop(t+dur+.6);}
  last.connect(g);env(g,t,o.a||.005,o.v,o.d||.1,o.s===undefined?.6:o.s,o.r||.05,t+dur);g.connect(o.to||MUS.bus);if(o.send)g.connect(MUS.dlyIn);os.start(t);os.stop(t+dur+(o.r||.05)*6+.05);}
function hit(t,type,v){const N=musNoise();
  if(type==='k'){const o=ac.createOscillator(),g=ac.createGain();o.frequency.setValueAtTime(140,t);o.frequency.exponentialRampToValueAtTime(42,t+.11);g.gain.setValueAtTime(v,t);g.gain.exponentialRampToValueAtTime(.001,t+.32);o.connect(g);g.connect(MUS.bus);o.start(t);o.stop(t+.35);return;}
  const s=ac.createBufferSource();s.buffer=N;s.playbackRate.value=type==='chip'?.5:1;const f=ac.createBiquadFilter(),g=ac.createGain();
  if(type==='s'){f.type='bandpass';f.frequency.value=1900;f.Q.value=.8;g.gain.setValueAtTime(v,t);g.gain.exponentialRampToValueAtTime(.001,t+.17);
    const o=ac.createOscillator(),og=ac.createGain();o.type='triangle';o.frequency.setValueAtTime(210,t);o.frequency.exponentialRampToValueAtTime(150,t+.06);og.gain.setValueAtTime(v*.6,t);og.gain.exponentialRampToValueAtTime(.001,t+.08);o.connect(og);og.connect(MUS.bus);o.start(t);o.stop(t+.1);}
  else if(type==='r'){f.type='bandpass';f.frequency.value=5200;f.Q.value=1.6;g.gain.setValueAtTime(v,t);g.gain.exponentialRampToValueAtTime(.001,t+.35);}
  else{f.type='highpass';f.frequency.value=7200;const dd=type==='o'?.22:.045;g.gain.setValueAtTime(v,t);g.gain.exponentialRampToValueAtTime(.001,t+dd);}
  s.connect(f);f.connect(g);g.connect(MUS.bus);s.start(t,Math.random()*.5);s.stop(t+.4);}
const LEADS={square:{w:'square',lp:2600,v:.07,d:.15,s:.55,vib:5.5,send:1},tri:{w:'triangle',v:.15,d:.2,s:.6,vib:5,send:1},saw:{w:'sawtooth',lp:2200,lpEnv:2,q:2,v:.07,d:.2,s:.6,vib:5.2,send:1},
  surf:{w:'sawtooth',lp:1700,q:3,v:.08,d:.12,s:.5,vib:7,send:1},bell:{w:'sine',fm:3.5,fmA:3,fmT:.25,v:.14,d:.35,s:.25,r:.3,send:1},marimba:{w:'sine',fm:4,fmA:1.4,fmT:.05,v:.17,d:.12,s:0,r:.08},
  pulse:{w:'square',v:.06,d:.08,s:.7},sine:{w:'sine',v:.15,d:.3,s:.7,vib:4.5,send:1,a:.03}};
const PADS={warm:{w:'triangle',v:.05,a:.25,lp:1400},bright:{w:'sawtooth',v:.022,a:.05,lp:2400},dark:{w:'sawtooth',v:.026,a:.4,lp:900},glass:{w:'sine',v:.05,a:.3,fm:2,fmA:.6,fmT:1},
  strings:{w:'sawtooth',v:.024,a:.5,lp:1600},ep:{w:'sine',v:.06,a:.01,fm:1,fmA:1.2,fmT:.3},space:{w:'sawtooth',v:.022,a:.9,lp:1100}};
/* one sixteenth note of the current song */
function musStep(S,t,secName,barIn,s16){const sec=secName==='A2'?'A':secName==='X'||secName==='I'?'A':secName;const ch=progAt(S,sec,barIn),sixt=60/S.bpm/4;
  const K=KITS[S.kit],drums=secName!=='X'||barIn>=2,full=secName!=='I'||barIn>=2;
  if(drums){if(K.k&&K.k[s16]==='x')hit(t,'k',.85);if(K.s&&K.s[s16]==='x'&&full)hit(t,S.kit==='chip'?'chip':'s',S.kit==='swing'?.2:.38);
    if(K.h&&K.h[s16]==='x')hit(t,'h',(s16%4===0?.11:.07)*(S.kit==='calyp'?.7:1));if(K.o&&K.o[s16]==='x')hit(t,'o',.08);if(K.r&&K.r[s16]==='x')hit(t,'r',.07);
    if(barIn%4===3&&s16>=12&&secName!=='I'&&full)hit(t,'s',.16+.05*(s16-12));}
  /* bass */
  const bp=BASSP[S.bass][s16];if(bp!=='.'&&(secName!=='X'||barIn>=2)){let n=deg(S,ch,3);if(bp==='R')n+=12;else if(bp==='f')n=deg(S,ch+4,3);
    else if(bp==='w'){const nx=progAt(S,sec,barIn+1),q=s16/4;n=q===0?deg(S,ch,3):q===1?deg(S,ch+2,3):q===2?deg(S,ch+4,3):deg(S,nx,3)+(Math.random()<.5?-1:1);}
    const len=S.bass==='half'?sixt*7:S.bass==='walk'?sixt*3.6:bp==='r'&&S.bass==='synco'?sixt*2.6:sixt*.9;
    voice(mtof(n),t,len,{w:S.bass==='walk'?'triangle':'sawtooth',lp:S.bass==='walk'?900:420,lpEnv:2.4,lpT:.06,q:4,v:S.bass==='walk'?.2:.13,d:.12,s:.65});}
  /* chords: sustained pad on the bar, or strummed */
  if(s16===0&&S.pad!=='none'){const P=PADS[S.pad],dur=sixt*16;const tones=[ch,ch+2,ch+4].concat(S.sev?[ch+6]:[]);
    for(const d of tones){const f=mtof(deg(S,d,5));voice(f,t,dur*.96,{w:P.w,v:P.v,a:P.a,d:.6,s:.8,r:.3,lp:P.lp,fm:P.fm,fmA:P.fmA,fmT:P.fmT,det:-6});if(P.w==='sawtooth')voice(f,t,dur*.96,{w:P.w,v:P.v,a:P.a,d:.6,s:.8,r:.3,lp:P.lp,det:7});}}
  if(S.arp==='strum'&&(s16%4===0||s16===14||s16===6)){for(const [i,d] of [ch,ch+4,ch+7].entries())voice(mtof(deg(S,d,4)),t+i*.012,sixt*1.5,{w:'sawtooth',lp:1500,lpEnv:2,q:1,v:.035,d:.08,s:.3});}
  /* arpeggio */
  const ar=S.arp;if(ar!=='none'&&ar!=='strum'&&full){const every=ar==='up8'||ar==='pluck'?2:1;if(s16%every===0){const i=Math.floor(s16/every);const seq=[0,2,4,7];let d;
      if(ar==='updown16'){const p=[0,2,4,7,9,7,4,2];d=ch+p[i%8];}else if(ar==='pluck'){d=ch+seq[(i*3+barIn)%4];}else d=ch+seq[i%4];
      voice(mtof(deg(S,d,ar==='pluck'?5:6)),t,sixt*(every*.8),{w:ar==='pluck'?'triangle':'square',lp:ar==='pluck'?3000:2200,v:ar==='pluck'?.06:.025,d:.06,s:.2,send:ar!=='pluck'});}}
  /* lead */
  if((secName==='A'||secName==='A2'||secName==='B')&&MUS.mel){const bar=MUS.mel[sec][barIn%8];for(const [s,dd,len] of bar)if(s===s16){const L=LEADS[S.lead];
      voice(mtof(deg(S,dd+(secName==='A2'&&barIn>=4?2:0),6)),t,sixt*len*.92,Object.assign({},L));}}}
function musSet(key){if(key===MUS.want)return;MUS.want=key;if(!ac||!MUS.gain)return;const T=ac.currentTime;MUS.gain.gain.cancelScheduledValues(T);MUS.gain.gain.setValueAtTime(MUS.gain.gain.value,T);MUS.gain.gain.linearRampToValueAtTime(0,T+.45);MUS.fadeT=T+.5;}
function musStart(key){const S=SONGS[key]||SONGS.menu1;MUS.key=key;MUS.song=S;MUS.mel=buildMelody(S);MUS.sec=0;MUS.bar=0;MUS.step=0;MUS.menuBars=0;MUS.t=ac.currentTime+.08;
  const T=ac.currentTime;MUS.gain.gain.cancelScheduledValues(T);MUS.gain.gain.setValueAtTime(0,T);MUS.gain.gain.linearRampToValueAtTime(1,T+.6);}
function musTick(){if(!ac||!master)return;musInit();if(!MUS.bus)return;
  const playing=state==='race'||state==='countdown'||state==='intro'||state==='paused'||state==='loading';let want=playing?(SONGS[MAPS[mapIdx].id]?MAPS[mapIdx].id:'margherita'):MENU_SONGS[MUS.menuI%MENU_SONGS.length];
  if(muted||CFG.music===false)want=null;musSet(want);
  {const mv=(CFG.mvol==null?45:CFG.mvol)/100,race=state==='race'||state==='countdown';MUS.bus.gain.setTargetAtTime(mv*(state==='paused'?.18:state==='loading'?.3:race?.42:.55),ac.currentTime,.15);}
  const T=ac.currentTime;if(MUS.key!==MUS.want){if(T<MUS.fadeT)return;if(!MUS.want){MUS.key=null;MUS.song=null;return;}musStart(MUS.want);}
  if(!MUS.song)return;const S=MUS.song;if(MUS.t<T-.2)MUS.t=T+.05;/* fell behind (tab hidden): skip ahead instead of playing a burst */
  while(MUS.t<T+.22){const sixt=60/S.bpm/4,sw=MUS.step%2===1?sixt*S.swing*.66:0;const [nm,len]=FORM[MUS.sec];
    musStep(S,MUS.t+sw,nm,MUS.bar,MUS.step);MUS.t+=sixt;MUS.step++;
    if(MUS.step>=16){MUS.step=0;MUS.bar++;MUS.menuBars++;if(MUS.bar>=len){MUS.bar=0;MUS.sec++;if(MUS.sec>=FORM.length)MUS.sec=1;}
      if(!playing&&MUS.menuBars>=60&&FORM[MUS.sec][0]==='A'&&MUS.bar===0){MUS.menuI++;}}}}

(()=>{try{const f=document.getElementById('fpsEl'),st=document.getElementById('stage');if(f&&st)st.appendChild(f);}catch(e){}})();
function frame(now){
  if(!booted){requestAnimationFrame(frame);return;}
  if(CFG.fps==='60'&&now-lastFrameT<13.5){requestAnimationFrame(frame);return;}lastFrameT=now;
  fpsN++;if(now-fpsT>500){const show=CFG.showfps&&state!=='menu';fpsEl.hidden=!show;if(show)fpsEl.textContent=Math.round(fpsN*1000/(now-fpsT))+' FPS';fpsN=0;fpsT=now;}
  let dt=(now-last)/1000;last=now;if(dt>.1)dt=.1;if(dt<0)dt=0;const time=now/1000;
  if(state==='menu'||state==='race'){acc+=dt;let n=0;while(acc>=STEP&&n<12){update(STEP);acc-=STEP;n++;}if(n>=12)acc=0;alpha=acc/STEP;
    if(state==='race'){if(resultsAt>0){resultsAt-=dt;if(resultsAt<=0){results.hidden=false;renderResults();}}}}
  else if(state==='intro'){alpha=1;introT+=dt;if(introSkip||introT>=INTRO_SHOT*INTRO_N)endIntro();}
  else if(state==='countdown'){alpha=1;cd-=dt;const n=Math.ceil(cd-.4);if(n!==lastCd&&n>=1&&n<=3){lastCd=n;showBanner(String(n),.9);SFX.count(false);}
    if(cd<=.4){state='race';showBanner('Go!',1);SFX.count(true);acc=0;}standCache=standings();}
  if(state!=='paused'){if(garageOpen)renderGarage(dt);else{if(fitPending){fitPending=false;fit();}if(state!=='loading'){render(time,dt);adaptQuality(dt,time);}}}
  hud(dt,time);
  try{musTick();}catch(e){console.warn('music',e);CFG.music=false;}
  if(ac&&eng){const on=!muted&&(state==='race'||state==='countdown')&&!!player;
    if(skidGain){const dr=on&&player.drift&&!player.air,c=player?Math.min(1,player.charge/2.6):0;driftT=dr?driftT+dt:0;const fat=1-.45*Math.min(1,Math.max(0,driftT-1.2)/2.5);/* long drifts settle down instead of droning */
      skidGain.gain.setTargetAtTime(dr?(.022+.022*c)*fat:0,ac.currentTime,dr?.09:.05);skidFilt.frequency.setTargetAtTime(760+c*520,ac.currentTime,.15);}
    const sp=player?Math.max(0,player.speed):0,bst=player&&player.boost>0,r=Math.min(1.3,sp/(BASE_MAX||170)),GT=[0,.2,.42,.64,.86,1.31];let gi=0;while(gi<4&&r>GT[gi+1])gi++;
    const rpm=Math.min(1.12,.3+.7*Math.min(1,(r-GT[gi])/(GT[gi+1]-GT[gi]))+(bst?.12:0)),ef=24+rpm*58+gi*4,T0=ac.currentTime;/* gears: revs climb, then drop at each shift like a real motor */
    eng.frequency.setTargetAtTime(ef,T0,.05);eng2.frequency.setTargetAtTime(ef*1.006,T0,.05);if(engAM)engAM.frequency.setTargetAtTime(ef*.5,T0,.05);
    if(engLP)engLP.frequency.setTargetAtTime(650+rpm*1500+(bst?500:0),T0,.08);if(engNG)engNG.gain.setTargetAtTime(.06+rpm*.12,T0,.1);engGain.gain.setTargetAtTime(on?.0065+.0055*rpm:0,T0,.06);}
  requestAnimationFrame(frame);
}
boot();
requestAnimationFrame(frame);
})();
