"""Patch 65 (web v218): the style shop (trim, accent and interior colours, underglow, headlight colour, tyre smoke) and coins for races.
The owner: "in the color section in garage add the ability to make different parts of the car different colors like trim pieces etc and
the interior ... a glow feature so the car has different colored ambient light coming from the bottom ... different headlight colors
and possibly wheel smoke that has different colors ... a few default free options ... tire smoke should have to be unlocked through the
shop with coins ... in offline and online races in sandbox add coins as well"; then "the colors for trim pieces should cost coins as
well, some can be free but the rest should cost coins with certain colors costing more than others". With photos of under-car LED
light (a neon pool of light on the ground under the sills, brightest at the body's edge) and coloured burnout smoke (thick, billowing,
rolling out from the rear tyres and hanging in the air).

The catalogue (STYLE): TRIMS (one list for trim, accent and interior; buying a colour unlocks it for all three), GLOWS, LIGHTS, SMOKES.
Each entry {n name, h colour ('rainbow' cycles), $ price, m metallic}; price 0 is free. Owned ones in store 'crust-own'; the wallet is
the Sandbox coins (sbSave().c). The choice is playerBuild.st = {tr, ac, in, gl, hl, sm} (indices; 0 = stock), sent with the build
(online players see it: a build travels whole), part of the model cache key.
How each shows:
  trim / accent / interior  karts: their own dark and stripe materials, seats swapped for the interior colour; car bodies (their
                            colours are baked per vertex by part class): styleVC, the shared car material cloned with a shader step
                            that repaints the trim classes (dark, carbon, gunmetal), accent (stripe, caliper, red) and seats, keeping
                            the baked shading, and gives a metallic trim its finish;
  underglow                 an additive pool of light on the ground shaped like the body (the hover glow's silhouette, in white so it
                            takes any colour; a soft rounded shape for the code-built karts), wider than the body like the photos,
                            stronger in the dark (Sandbox's clock, night tracks); 'rainbow' cycles;
  headlights                the lenses (car bodies) and Sandbox's headlight beam;
  tyre smoke                the drift smoke and new launch smoke (a hard start from slow) in the chosen colour, bigger, thicker and
                            longer-lived than before (FXN 260 -> 420 particles).
Coins for races: racePay at the player's finish (onPlayerFinish: every race, off line, on line, Sandbox's start-line races): 8 + 3 a
place beaten, +10 / +5 / +2 for a podium, x the class (1, 1.2, 1.5); 6 for a run alone. Shown under the results ("+N coins").
CPU karts sometimes wear a glow or smoke (randomBuild), for show.
Run once: py.cmd tools/mini/patch65.py"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'patch 65' not in s, 'already patched'


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:90])
    s = s.replace(a, b)


# ---------------------------------------------------------------- the catalogue, ownership, the wallet
rep("function randomBuild(){", r"""/* (patch 65) the style shop: trim / accent / interior colours (one list), underglow, headlight colours, tyre smoke */
const TRIMS=[{n:'Stock',h:null,$:0},{n:'Black',h:'#111214',$:0},{n:'White',h:'#f2f2f0',$:0},{n:'Silver',h:'#b8bcc4',$:0,m:1},{n:'Red',h:'#c40c0c',$:60},{n:'Orange',h:'#ff5a00',$:60},
  {n:'Yellow',h:'#ffc400',$:60},{n:'Green',h:'#2fae0c',$:60},{n:'Blue',h:'#0b49c9',$:60},{n:'Purple',h:'#5317ad',$:80},{n:'Pink',h:'#ff2c84',$:80},{n:'Tan leather',h:'#a8703e',$:120},
  {n:'Neon green',h:'#7dff2a',$:150},{n:'Neon blue',h:'#2ae8ff',$:150},{n:'Gunmetal',h:'#3b3e44',$:150,m:1},{n:'Bronze',h:'#8a6232',$:250,m:1},{n:'Gold',h:'#d4a838',$:400,m:1},{n:'Chrome',h:'#e9e9ee',$:600,m:1,r:.08}];
const GLOWS=[{n:'Off',h:null,$:0},{n:'Ice blue',h:'#3fc8ff',$:0},{n:'Purple',h:'#a040ff',$:200},{n:'Red',h:'#ff2a2a',$:200},{n:'Green',h:'#3dff6a',$:200},{n:'Pink',h:'#ff3fb4',$:250},
  {n:'Amber',h:'#ffa020',$:250},{n:'White',h:'#e8f0ff',$:250},{n:'Rainbow',h:'rainbow',$:800}];
const LIGHTS=[{n:'Halogen',h:'#fff2d6',$:0},{n:'Xenon white',h:'#eef3ff',$:0},{n:'Ice blue',h:'#9fd8ff',$:150},{n:'Yellow',h:'#ffd75a',$:150},{n:'Purple',h:'#c49bff',$:300},{n:'Green',h:'#9dffb0',$:300},{n:'Red',h:'#ff7a6a',$:300}];
const SMOKES=[{n:'White',h:'#f2ebe0',$:0},{n:'Black',h:'#2a2a2e',$:300},{n:'Blue',h:'#2a6cff',$:350},{n:'Red',h:'#ff3020',$:350},{n:'Purple',h:'#9a40ff',$:350},{n:'Green',h:'#3ad84a',$:350},
  {n:'Yellow',h:'#ffd22a',$:350},{n:'Pink',h:'#ff4fb8',$:400},{n:'Rainbow',h:'rainbow',$:900}];
const STYLE={tr:['tr',TRIMS],ac:['tr',TRIMS],in:['tr',TRIMS],gl:['gl',GLOWS],hl:['hl',LIGHTS],sm:['sm',SMOKES]};
function ownedSet(){try{return new Set(JSON.parse(store.get('crust-own')||'[]'));}catch(e){return new Set();}}
function styleOwned(slot,i){const [g,L]=STYLE[slot];return !L[i]||!L[i].$||ownedSet().has(g+i);}
function styleBuy(slot,i){const [g,L]=STYLE[slot],it=L[i],sv=sbSave();if(!it||styleOwned(slot,i))return true;if(sv.c<it.$)return false;sv.c-=it.$;sbKeep();const o=ownedSet();o.add(g+i);store.set('crust-own',JSON.stringify([...o]));return true;}
function stOf(sp){return (sp&&sp.st)||{};}
function rainbowC(t,o){return new THREE.Color().setHSL(((t*.12+(o||0))%1+1)%1,1,.55);}
function styleHL(sp){const i=stOf(sp).hl|0;return (LIGHTS[i]||LIGHTS[0]).h;}
function smokeC(k){const it=SMOKES[stOf(k.spec).sm|0]||SMOKES[0];return it.h==='rainbow'?'#'+rainbowC(performance.now()/1000,k.ri*.13).getHexString():it.h;}
function randomBuild(){""")
rep("let playerBuild=(()=>{try{const b=JSON.parse(store.get('crust-build')||'null');if(validBuild(b))return b;}catch(e){}return {b:0,w:0,g:0,p:0};})();",
    "let playerBuild=(()=>{try{const b=JSON.parse(store.get('crust-build')||'null');if(validBuild(b))return b;}catch(e){}return {b:0,w:0,g:0,p:0};})();\n"
    "/* (patch 65) CPU karts sometimes wear a glow or coloured smoke, for show (they need not own it) */setTimeout(()=>{const rb=randomBuild;randomBuild=function(){const b=rb();if(Math.random()<.3)b.st={gl:Math.floor(Math.random()*GLOWS.length),sm:Math.random()<.5?Math.floor(Math.random()*SMOKES.length):0};return b;};},0);")

# ---------------------------------------------------------------- the model: materials, glow
rep("    tailM:new THREE.MeshStandardMaterial({color:'#ff2a1a',emissive:'#ff1a0a',emissiveIntensity:.8})};\n",
    "    tailM:new THREE.MeshStandardMaterial({color:'#ff2a1a',emissive:'#ff1a0a',emissiveIntensity:.8})};\n"
    "  {/* (patch 65) the style: trim and accent on the kart's own materials; the car bodies' shared parts get styled copies */const st=stOf(spec),t=TRIMS[st.tr|0],a=TRIMS[st.ac|0],hl=st.hl|0;"
    "if(t&&t.h){M.dark.color.set(t.h);M.dark.metalness=t.m?.9:.3;M.dark.roughness=t.r||(t.m?.22:.4);}if(a&&a.h){M.stripe.color.set(a.h);if(a.m){M.stripe.metalness=.9;M.stripe.roughness=a.r||.22;}}"
    "M.vcM=styleVC(st);if(hl){M.lightM=SH.carLight.clone();M.lightM.emissive.set(LIGHTS[hl].h);M.lightM.emissiveIntensity=.7;M.lightM.color.set(LIGHTS[hl].h);}}\n")
rep("const mats={paint:M.carPaint,tail:M.tailM,light:SH.carLight,glass:SH.carGlass,vc:SH.carVC,blue:M.blue};",
    "const mats={paint:M.carPaint,tail:M.tailM,light:M.lightM||SH.carLight,glass:SH.carGlass,vc:M.vcM||SH.carVC,blue:M.blue};/* (patch 65: styled copies) */")
# the glow under the body, the interior colour on the code-built karts' seats
a = s.index("if(cfg.hover){const hg=hoverGlowFor(cfg.car),")
e = s.index("cfg.glow=pl;}", a) + len("cfg.glow=pl;}")
s = s[:e] + ("\n  {/* (patch 65) underglow: a pool of light on the ground shaped like the body; and the interior colour on a code-built kart's seats */const st=stOf(spec),gi=st.gl|0,ii=st.in|0;"
             "if(ii&&TRIMS[ii]&&TRIMS[ii].h){const im=new THREE.MeshStandardMaterial({color:TRIMS[ii].h,roughness:TRIMS[ii].m?.25:.6,metalness:TRIMS[ii].m?.8:0});g.traverse(o=>{if(o.isMesh&&o.material===SH.seat)o.material=im;});}"
             "if(gi&&GLOWS[gi]&&GLOWS[gi].h&&!cfg.hover){const hg=cfg.car?ugTexFor(cfg.car):null,W=hg?hg.w*1.5:(cfg.fw[0]-cfg.rw[0]+2*Math.max(cfg.rw[2],cfg.fw[2])+3)*1.45,H=hg?hg.h*2:(2*Math.max(cfg.fw[1],cfg.rw[1])+2.6)*1.9,/* (wider than the body: the pool spreads past the sills, as in the photos) */"
             "gm=new THREE.MeshBasicMaterial({map:hg?hg.t:ugGenericT(),color:GLOWS[gi].h==='rainbow'?'#ff3030':GLOWS[gi].h,transparent:true,opacity:.8,depthWrite:false,blending:THREE.AdditiveBlending,toneMapped:false}),"
             "pl=new THREE.Mesh(new THREE.PlaneGeometry(W,H),gm);pl.rotation.x=-Math.PI/2;pl.position.set(hg?hg.cx:(cfg.fw[0]+cfg.rw[0])/2,.22,hg?hg.cz:0);pl.renderOrder=2;g.add(pl);g.userData.ug={pl,rb:GLOWS[gi].h==='rainbow'};}}") + s[e:]
rep("const _hgF={};function hoverGlowFor(id){",
    r"""/* (patch 65) the underglow's shapes: a car body's silhouette glow (hoverGlowFor) recoloured white so the glow takes any colour, and a soft
   rounded pool for the code-built karts: a bright line just inside the edge (the LED strips) fading out across the ground */
const _ugF={};function ugTexFor(id){if(_ugF[id]!==undefined)return _ugF[id];const h=hoverGlowFor(id);if(!h)return _ugF[id]=null;try{const src=h.t.image,c=cnv(src.width,src.height),x=c.getContext('2d');x.drawImage(src,0,0);
  const im=x.getImageData(0,0,c.width,c.height),D=im.data;for(let i=0;i<D.length;i+=4){const a=D[i+3]/255;D[i]=D[i+1]=D[i+2]=255;D[i+3]=Math.round(255*Math.min(1,a*1.15));}x.putImageData(im,0,0);
  const t=new THREE.CanvasTexture(c);return _ugF[id]={t,w:h.w,h:h.h,cx:h.cx,cz:h.cz};}catch(e){return _ugF[id]=null;}}
let _ugG=null;function ugGenericT(){if(_ugG)return _ugG;const W=128,H=64,c=cnv(W,H),x=c.getContext('2d'),im=x.createImageData(W,H),D=im.data;
  for(let z=0;z<H;z++)for(let q=0;q<W;q++){const u=Math.abs(q+.5-W/2)/(W/2),v=Math.abs(z+.5-H/2)/(H/2),d=Math.max(0,Math.pow(Math.pow(u,6)+Math.pow(v,6),1/6)),
    ring=Math.exp(-Math.pow((d-.72)/.13,2)),fill=d<.72?.55:Math.max(0,1-(d-.72)/.28)*.55,a=Math.min(1,ring*.9+fill)*(d<1?1:0);const i=(z*W+q)*4;D[i]=D[i+1]=D[i+2]=255;D[i+3]=Math.round(255*a);}
  x.putImageData(im,0,0);return _ugG=new THREE.CanvasTexture(c);}
/* (patch 65) a car body's styled copy of the shared part material: its trim classes (dark, carbon, gunmetal), accent classes (stripe,
   caliper, red) and seats repainted in the chosen colours; the baked shading kept (the vertex colour over the class's own colour) */
const _svc={};function styleVC(st){const t=TRIMS[st.tr|0],a=TRIMS[st.ac|0],n=TRIMS[st.in|0];if(!(t&&t.h)&&!(a&&a.h)&&!(n&&n.h))return null;const key=[st.tr|0,st.ac|0,st.in|0].join('.');if(_svc[key])return _svc[key];
  const m=SH.carVC.clone(),C=h=>new THREE.Color(h||'#000000'),base=c=>{const x=new THREE.Color(CAR_COL[c]);return Math.max(.004,x.r,x.g,x.b);},
    U={uT:{value:C(t.h)},uA:{value:C(a.h)},uI:{value:C(n.h)},uOn:{value:new THREE.Vector3(t.h?1:0,a.h?1:0,n.h?1:0)},uB:{value:new THREE.Vector3(base('dark'),base('stripe'),base('seat'))},
      uTM:{value:new THREE.Vector4(t.m?.9:.25,t.m?(t.r||.22):.4,n.m?.85:0,n.m?.25:.6)}};
  m.onBeforeCompile=sh=>{Object.assign(sh.uniforms,U);sh.fragmentShader='uniform vec3 uT,uA,uI,uOn,uB;uniform vec4 uTM;\n'+sh.fragmentShader.replace('#include <color_fragment>','#include <color_fragment>\n'
    +'float sCi=floor(vUv.x*32.);float sMx=max(vColor.r,max(vColor.g,vColor.b));float sG=0.;\n'
    +'if(uOn.x>.5&&(abs(sCi-1.)<.1||abs(sCi-6.)<.1||abs(sCi-15.)<.1)){diffuseColor.rgb=uT*clamp(sMx/uB.x,.3,1.2);sG=1.;}\n'
    +'else if(uOn.y>.5&&(abs(sCi-2.)<.1||abs(sCi-13.)<.1||abs(sCi-17.)<.1)){diffuseColor.rgb=uA*clamp(sMx/uB.y,.3,1.2);sG=2.;}\n'
    +'else if(uOn.z>.5&&abs(sCi-9.)<.1){diffuseColor.rgb=uI*clamp(sMx/uB.z,.3,1.2);sG=3.;}').replace('#include <metalnessmap_fragment>','#include <metalnessmap_fragment>\n'
    +'if(sG==1.){metalnessFactor=uTM.x;roughnessFactor=uTM.y;}else if(sG==3.){metalnessFactor=uTM.z;roughnessFactor=uTM.w;}');};
  m.customProgramCacheKey=()=>'carvc-style';SHSET.add(m);return _svc[key]=m;}
const _hgF={};function hoverGlowFor(id){""")
rep("const specKey=s=>[s.ri,s.b,s.w,s.g,s.p,s.t||'',s.hq===0?0:1,s.u||0].join('.');",
    "const specKey=s=>[s.ri,s.b,s.w,s.g,s.p,s.t||'',s.hq===0?0:1,s.u||0,s.st?JSON.stringify(s.st):''].join('.');/* (patch 65: the style) */")
rep("u:build.u||0},m=getModel(spec)", "u:build.u||0,st:build.st||null},m=getModel(spec)")

# ---------------------------------------------------------------- each frame: the glow breathes with the dark; rainbow cycles
rep("if(m.hglow)m.hglow.material.opacity=.55+Math.sin(time*9+k.ri)*.12+(k.boost>0?.3:0);}",
    "if(m.hglow)m.hglow.material.opacity=.55+Math.sin(time*9+k.ri)*.12+(k.boost>0?.3:0);}\n"
    "  {const ug=m.g.userData.ug;if(ug){/* (patch 65) the underglow: brighter in the dark */const L=SBX&&typeof sbClockF==='function'?sbClockF().L:(MAPS[mapIdx]&&MAPS[mapIdx].theme==='night'?1:0);ug.pl.material.opacity=.5+.5*L+(k.boost>0?.15:0);if(ug.rb)ug.pl.material.color.copy(rainbowC(time,k.ri*.13));}}")

# ---------------------------------------------------------------- tyre smoke: the chosen colour, thicker; and launch smoke
rep("if(i%3===0){tv.copy(m.fxL[Math.random()<.5?0:1]);m.g.localToWorld(tv);FXN.spawn(tv.x,tv.y+.6,tv.z,(Math.random()-.5)*6,4+Math.random()*4,(Math.random()-.5)*6,'#f2ebe0',2.5,8,.8,-2,1.5);}}",
    "if(i%2===0){/* (patch 65) tyre smoke in the chosen colour: thick, rolling up and out, hanging a while */const sc=smokeC(k);for(const v of m.fxL){tv.copy(v);m.g.localToWorld(tv);FXN.spawn(tv.x,tv.y+.8,tv.z,(Math.random()-.5)*9-Math.cos(k.ma)*6,5+Math.random()*6,(Math.random()-.5)*9-Math.sin(k.ma)*6,sc,3.6,15,1.25,-1.5,1.2);}}}\n"
    "    if(!k.air&&!k.drift&&k.speed>3&&k.speed<48&&(k.acc||0)>30&&i%2===0&&(k===camT||Math.random()<.4)){/* (patch 65) a hard launch from slow: smoke off the rear tyres */const sc=smokeC(k);for(const v of m.fxL){tv.copy(v);m.g.localToWorld(tv);FXN.spawn(tv.x,tv.y+.6,tv.z,(Math.random()-.5)*8-Math.cos(k.ma)*12,3+Math.random()*5,(Math.random()-.5)*8-Math.sin(k.ma)*12,sc,3,13,1.1,-1.5,1.4);}}")
rep("FXN=particleSystem(260,THREE.NormalBlending,TX.smoke)", "FXN=particleSystem(420,THREE.NormalBlending,TX.smoke)/* (patch 65: thicker tyre smoke) */")

# ---------------------------------------------------------------- Sandbox's headlight beam in the chosen colour
rep("function sbNightFrame(time){const Nn=SBC.night;if(!Nn||!SBC.rec||!SBX)return;const L=sbClockF().L,on=L>.02;",
    "function sbNightFrame(time){const Nn=SBC.night;if(!Nn||!SBC.rec||!SBX)return;const L=sbClockF().L,on=L>.02;"
    "try{const hc=styleHL(player&&player.spec);if(Nn.spot&&Nn._hc!==hc){Nn._hc=hc;Nn.spot.color.set(hc==='#fff2d6'?'#eef3ff':hc);}}catch(e){}/* (patch 65: the headlight colour) */")

# ---------------------------------------------------------------- coins for a finished race
rep("/* (patch 47) */ITMUSED=false;", "/* (patch 47) */ITMUSED=false;RPAY=0;RDEMO=!!demo;")
rep("let NOITM=false,ITMUSED=false;", "let NOITM=false,ITMUSED=false,RPAY=0,RDEMO=false;/* (patch 65: coins paid for this race) */")
rep("if(mode!=='lss')saveRun();try{achFinish();}catch(e){}",
    "if(mode!=='lss')saveRun();try{racePay();}catch(e){console.warn('pay',e);}try{achFinish();}catch(e){}")
rep("function pbLine(){",
    "/* (patch 65) coins for a finished race: 8, 3 more for each kart beaten, a podium bonus, times the class; 6 for a run alone */\n"
    "function racePay(){if(!player||player.est||RDEMO||RPAY)return;const n=karts.length,p=player.place||n,cm={small:1,medium:1.2,large:1.5,reverse:1.5}[clsKey]||1;"
    "const amt=n>1?Math.round((8+Math.max(0,n-p)*3+(p===1?10:p===2?5:p===3?2:0))*cm):6;const sv=sbSave();sv.c=(sv.c||0)+amt;sbKeep();RPAY=amt;}\n"
    "function payLine(){return RPAY?'<span class=\"pbn\">+'+RPAY+' coins</span>':'';}\n"
    "function pbLine(){")
rep("const pl=pbLine();if(pl)resSub.innerHTML=", "const pl=[pbLine(),payLine()].filter(Boolean).join('<br>');if(pl)resSub.innerHTML=", 2)

# ---------------------------------------------------------------- the garage: the style shop under the paint swatches
rep('<div class="swatches" id="pPaint"></div>', '<div class="swatches" id="pPaint"></div><div id="pStyle" class="style-shop"></div>')
rep("  $('pPaint').querySelectorAll('button').forEach(b=>b.setAttribute('aria-pressed',String(!playerBuild.t&&+b.dataset.i===playerBuild.p)));",
    "  $('pPaint').querySelectorAll('button').forEach(b=>b.setAttribute('aria-pressed',String(!playerBuild.t&&+b.dataset.i===playerBuild.p)));try{styleUI();}catch(e){console.warn('style',e);}")
rep("function refreshGarage(rebuild){", r"""/* (patch 65) the style shop: a row of swatches per slot; a locked one shows its price; a first tap on it asks, a second buys */
let styleAsk=null;function styleUI(){const w=$('pStyle');if(!w)return;const st=playerBuild.st||{},coins=sbSave().c||0;
  const sw=(slot,it,i)=>{const own=styleOwned(slot,i),on=(st[slot]|0)===i,h=it.h;let bg=h==='rainbow'?'conic-gradient(#ff3030,#ffd22a,#3dff6a,#2ae8ff,#a040ff,#ff3030)':!h?'repeating-linear-gradient(45deg,#3a2a22 0 6px,#2a1c16 6px 12px)':it.m?'linear-gradient(135deg,#fff 0%,'+h+' 40%,'+h+' 60%,#222 100%)':h;
    if(slot==='gl'&&h&&h!=='rainbow')bg='radial-gradient(circle at 50% 70%,'+h+' 0 30%,#1a1210 75%)';
    return '<button type="button" class="pw sty'+(own?'':' buy')+'" data-s="'+slot+'" data-i="'+i+'" aria-pressed="'+on+'" title="'+it.n+(own?'':' · '+it.$+' coins')+'" aria-label="'+it.n+(own?'':', '+it.$+' coins')+'" style="background:'+bg+'">'+(own?'':'<span class="pr">'+it.$+'</span>')+'</button>';};
  const row=(slot,title)=>'<p class="g-sub">'+title+'</p><div class="swatches">'+STYLE[slot][1].map((it,i)=>sw(slot,it,i)).join('')+'</div>';
  w.innerHTML='<p class="g-sub style-coins">Style shop · <b>'+coins+'</b> coins</p>'+row('tr','Trim')+row('ac','Accent')+row('in','Interior')+row('gl','Underglow')+row('hl','Headlights')+row('sm','Tyre smoke');
  w.querySelectorAll('button.sty').forEach(b=>b.onclick=()=>{const slot=b.dataset.s,i=+b.dataset.i,it=STYLE[slot][1][i];
    if(!styleOwned(slot,i)){const have=sbSave().c||0;if(have<it.$){achToast(null,'<b>'+it.n+'</b> costs '+it.$+' coins. You have '+have+'. Earn coins by racing and in Sandbox.');return;}
      if(styleAsk!==slot+i){styleAsk=slot+i;achToast(null,'Tap <b>'+it.n+'</b> again to buy it for '+it.$+' coins');return;}styleAsk=null;styleBuy(slot,i);try{SFX.ready();}catch(e){}}
    playerBuild.st=Object.assign({},playerBuild.st||{},{[slot]:i});saveBuild();refreshGarage(true);});}
function refreshGarage(rebuild){""")
rep(".swatches{display:flex;flex-wrap:wrap;gap:10px}",
    ".swatches{display:flex;flex-wrap:wrap;gap:10px}\n.style-shop{margin-top:10px}.style-shop .g-sub{margin-top:14px}.style-coins b{color:var(--cheese)}\n"
    ".pw.sty .pr{position:absolute;left:50%;bottom:-7px;transform:translateX(-50%);font-size:10px;font-weight:800;line-height:1;padding:2px 4px;border-radius:6px;background:#2a140a;color:var(--cheese);border:1px solid rgba(247,201,72,.5)}\n"
    ".pw.sty.buy{opacity:.88}")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patch 65 applied')
