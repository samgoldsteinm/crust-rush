"""Patch 29 (web v194): the controller has an on-screen cursor in the menus.
The owner, 2026-11-14: "instead of the yellow boxes on controller it should just be an on screen cursor and mouse. the scroll function should
work the same as the on screen mouse moves to the bottom of the screen the screen will scroll down and same thing for up. this way the user
has total control of what they click on. the mouse will be controlled with the left stick and make scrolling a right stick function as well
even though it also works with the mouse".
  - Menus, the pause menu, results, the garage, Settings, the Sandbox map: an arrow the LEFT STICK moves (the D-pad too, at a steady pace).
    A presses whatever is under it. B is still Back, Start still pauses.
  - The RIGHT STICK scrolls whatever scrolls under the arrow. Held against the top or bottom (or the sides) of a box that scrolls, the arrow
    scrolls it that way: faster the nearer the edge.
  - What is under the arrow lights up a little (as a mouse's hover does). No yellow focus ring any more: padNav does nothing.
  - A new screen puts the arrow on its main button, so a run of A presses still goes straight through the menus.
  - A slider under the arrow: D-pad left and right move it. A list box (a select): A steps to its next choice.
  - The garage's big view: the right stick zooms (the left stick used to; it is the arrow's now).
  - A real mouse moving hides the arrow; the stick brings it back.
Run once: py.cmd tools/mini/patch29.py"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'function padCursor' not in s, 'already patched'


def rep(a, b, n=1):
    global s
    if s.count(a) == 0 and '\n' in a: a = a.replace('\n', '\r\n'); b = b.replace('\n', '\r\n')
    assert s.count(a) == n, (s.count(a), a[:80])
    s = s.replace(a, b)


CUR = r"""/* ---- the controller's cursor (web v194; patch29.py has the owner's words) ---- */
const PAD_CLICK='button,a[href],input,select,label,summary,[tabindex]:not([tabindex="-1"]),.mapc,.cupc,[role=button]';
function padCurEl(){let e=PAD.cur;if(!e){e=PAD.cur=document.createElement('div');e.id='padCur';e.hidden=true;e.style.cssText='position:fixed;left:0;top:0;width:30px;height:30px;margin:-3px 0 0 -3px;z-index:2147483000;pointer-events:none;will-change:transform;filter:drop-shadow(0 2px 3px rgba(0,0,0,.65))';
    e.innerHTML='<svg viewBox="0 0 30 30" width="30" height="30"><path d="M3 2 L3 23 L8.8 17.8 L13 27 L16.8 25.3 L12.6 16.2 L20.5 16.2 Z" fill="#fff" stroke="#1b0f0b" stroke-width="2.2" stroke-linejoin="round"/></svg>';document.body.appendChild(e);
    const st=document.createElement('style');st.textContent='#padCur[hidden]{display:none}.padhover{filter:brightness(1.2) saturate(1.1)}';document.head.appendChild(st);
    addEventListener('mousemove',ev=>{if(ev.isTrusted&&PAD.curOn&&(Math.abs(ev.movementX)+Math.abs(ev.movementY))>1){PAD.curOn=false;padCurShow();}},true);}return e;}
function padCurShow(){const e=padCurEl();e.hidden=!PAD.curOn;if(!PAD.curOn&&PAD.hov){PAD.hov.classList.remove('padhover');PAD.hov=null;}}
function padCurOff(){if(PAD.curOn){PAD.curOn=false;padCurShow();}PAD.cScope=null;}
/* the nearest thing above el that scrolls along the axis ('Y' or 'X') */
function padScroller(el,ax){const can=q=>q&&(ax==='Y'?q.scrollHeight>q.clientHeight+4:q.scrollWidth>q.clientWidth+4)&&/(auto|scroll)/.test(getComputedStyle(q)['overflow'+ax]);let q=el;while(q&&q!==document.body&&q!==document.documentElement&&!can(q))q=q.parentElement;return can(q)?q:null;}
function padCursor(gp,M,ax,ay,pr,edge,now){const dt=Math.min(.05,Math.max(0,(now-(PAD.cT||now))/1000));PAD.cT=now;const W=innerWidth,H=innerHeight;if(PAD.cx==null){PAD.cx=W/2;PAD.cy=H/2;}
  /* a new screen: the arrow starts on its main button */
  {const sc=padScope();if(sc!==PAD.cScope){PAD.cScope=sc;const b=[...sc.querySelectorAll('.cta')].find(padVisible)||[...sc.querySelectorAll('button')].find(padVisible);if(b){const r=b.getBoundingClientRect();if(r.width&&r.bottom>8&&r.top<H-8){PAD.cx=clamp(r.left+r.width/2,2,W-3);PAD.cy=clamp(r.top+r.height/2,2,H-3);}}}}
  let el=PAD.curOn?document.elementFromPoint(PAD.cx,PAD.cy):null,hit=el&&el.closest?el.closest(PAD_CLICK):null;if(hit&&hit.disabled)hit=null;
  const slider=!!hit&&hit.tagName==='INPUT'&&hit.type==='range';
  /* the stick: faster the further it is pushed; the D-pad: a steady walk (on a slider its left and right move the slider) */
  const dz=.16,m=Math.hypot(ax,ay);let vx=0,vy=0;if(m>dz){const f=Math.min(1,(m-dz)/(1-dz)),sp=(200+1300*f*f)*clamp(Math.min(W,H)/720,.7,1.6);vx=ax/m*sp;vy=ay/m*sp;}
  const dl=pr(M.LEFT),dr=pr(M.RIGHT);if(slider&&(dl||dr)){if(now>(PAD.slT||0)){PAD.slT=now+110;const st=+hit.step||1,v=clamp((+hit.value)+(dr?st:-st),+hit.min||0,hit.max===''?100:+hit.max);if(v!==+hit.value){hit.value=v;hit.dispatchEvent(new Event('input',{bubbles:true}));hit.dispatchEvent(new Event('change',{bubbles:true}));}}}
  else vx+=((dr?1:0)-(dl?1:0))*430;vy+=((pr(M.DOWN)?1:0)-(pr(M.UP)?1:0))*430;
  if(vx||vy){if(!PAD.curOn){PAD.curOn=true;padCurShow();}PAD.cx=clamp(PAD.cx+vx*dt,2,W-3);PAD.cy=clamp(PAD.cy+vy*dt,2,H-3);}
  const e=padCurEl();if(e.hidden===PAD.curOn)padCurShow();e.style.transform='translate('+PAD.cx.toFixed(1)+'px,'+PAD.cy.toFixed(1)+'px)';
  if(hit!==PAD.hov){if(PAD.hov)PAD.hov.classList.remove('padhover');PAD.hov=hit;if(hit)hit.classList.add('padhover');}
  /* scrolling: the right stick; and the arrow held against an edge of whatever scrolls under it (the whole screen, a list, the map) */
  {const base=el||padScope(),sy=padScroller(base,'Y'),sx=padScroller(base,'X'),ry=gp.axes[3]||0,rx=gp.axes[2]||0,big=typeof garageOpen!=='undefined'&&garageOpen&&gBig;
    if(!big&&Math.abs(ry)>.2){const d=ry*Math.abs(ry)*1700*dt;if(sy)sy.scrollBy(0,d);else padScroll(d);}
    if(!big&&Math.abs(rx)>.3&&sx)sx.scrollBy(rx*Math.abs(rx)*1700*dt,0);
    if(PAD.curOn){const z=Math.max(36,H*.075),pull=(d)=>(260+1100*clamp(d/z,0,1))*dt;
      if(sy){const r=sy.getBoundingClientRect(),t=Math.max(0,r.top),b=Math.min(H,r.bottom);if(vy>0&&PAD.cy>b-z)sy.scrollBy(0,pull(PAD.cy-(b-z)));else if(vy<0&&PAD.cy<t+z)sy.scrollBy(0,-pull(t+z-PAD.cy));}
      else if(vy>0&&PAD.cy>H-z)padScroll(pull(PAD.cy-(H-z)));else if(vy<0&&PAD.cy<z)padScroll(-pull(z-PAD.cy));
      if(sx){const r=sx.getBoundingClientRect(),l=Math.max(0,r.left),q=Math.min(W,r.right);if(vx>0&&PAD.cx>q-z)sx.scrollBy(pull(PAD.cx-(q-z)),0);else if(vx<0&&PAD.cx<l+z)sx.scrollBy(-pull(l+z-PAD.cx),0);}}}
  /* A: press what is under the arrow */
  if(edge(M.A)){if(!PAD.curOn){PAD.curOn=true;padCurShow();el=document.elementFromPoint(PAD.cx,PAD.cy);hit=el&&el.closest?el.closest(PAD_CLICK):null;if(hit&&hit.disabled)hit=null;}
    if(hit){if(hit.tagName==='SELECT'){hit.selectedIndex=(hit.selectedIndex+1)%hit.options.length;hit.dispatchEvent(new Event('change',{bubbles:true}));}else{try{if(hit.focus)hit.focus({preventScroll:true});}catch(err){}if(!(hit.tagName==='INPUT'&&hit.type==='range'))hit.click();}}}}
"""
rep("function padNav(dir){document.body.classList.add('padnav');", CUR + "function padNav(dir){return;/* (web v194: the controller has a cursor; nothing is ringed in yellow any more) */document.body.classList.add('padnav');")
# the menus' branch of padPoll: the cursor instead of walking between buttons
rep("    const zs=garageOpen&&gBig;/* full-screen garage: the left stick's up/down zooms instead of moving between buttons */const dir=(pr(M.UP)||!zs&&ay<-.6)?'u':(pr(M.DOWN)||!zs&&ay>.6)?'d':(dl||ax<-.6)?'l':(dr||ax>.6)?'r':'';\n"
    "    if(dir&&now>PAD.navT){PAD.navT=now+(PAD.navDir===dir?140:260);PAD.navDir=dir;padNav(dir);}else if(!dir){PAD.navT=0;PAD.navDir='';}\n"
    "    {const ry=gp.axes[3]||0;if(Math.abs(ry)>.25)padScroll(ry*22);}\n"
    "    if(edge(M.A)){const el=document.activeElement;if(el&&el!==document.body&&el.click){padRemember(el);el.click();}else padNav('d');}\n"
    "    padRestore();\n",
    "    document.body.classList.remove('padnav');padCursor(gp,M,ax,ay,pr,edge,now);\n")
rep("    if(garageOpen&&edge(M.X)){const el=document.activeElement,f=el&&el.classList&&el.classList.contains('theme')?el.querySelector('.fav'):null;\n      if(f){padRemember(el);f.click();}else",
    "    if(garageOpen&&edge(M.X)){const el=PAD.hov&&PAD.hov.closest?PAD.hov.closest('.theme'):null,f=el?el.querySelector('.fav'):null;\n      if(f){f.click();}else")
rep("if(gBig){const dz2=.18,zy=Math.abs(ay)<dz2?0:Math.sign(ay)*(Math.abs(ay)-dz2)/(1-dz2);", "if(gBig){const dz2=.18,ay2=gp.axes[3]||0,zy=Math.abs(ay2)<dz2?0:Math.sign(ay2)*(Math.abs(ay2)-dz2)/(1-dz2);/* (the right stick: the left one is the cursor's) */")
rep("PAD.back=false;document.body.classList.remove('padnav','pad');}return;}", "PAD.back=false;document.body.classList.remove('padnav','pad');}padCurOff();return;}")
# racing: no cursor
rep("  if(racing){document.body.classList.remove('padnav');", "  if(racing){document.body.classList.remove('padnav');padCurOff();")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patched')
