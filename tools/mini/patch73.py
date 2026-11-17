"""Patch 73 (web v222): a Rims colour row, and colour combos.
The owner: "trim also shouldnt change the rim color we should jsut have a color section for rims" and "in the color section make a few
combos that look good that the player can pre select or buy using coins. in these combos that you can buy there will be colors that maybe
you cant afford yet in a section but you can still use it in the combo for a cheaper price. the tradeoff is its only for the specific
piece its assigned to in the combo".
- STYLE.rm (Rims): the trim colour list (one purchase unlocks a colour for trim, accent, interior and rims). rimVC(st) repaints a wheel's
  metal classes (metal, chrome, rim, gunmetal, bronze, steel) with it, metal or satin as the colour is; on a car's own wheels and on the
  pack wheels. Trim never touches wheels.
- COMBOS: a full look (paint, trim, accent, interior, rims, underglow, headlights, smoke). Two free; the rest cost less than their parts.
  Bought ones are kept as 'cb<i>' in crust-own; comboAllows(slot,i): an owned combo with that piece in that slot, so the piece is usable in
  that slot only (styleOwned checks it; the start-up check of patch 70 too). A combo picked sets the whole look (no livery).
  KEEP THE ORDER of COMBOS (ids by index) and the PC's style.gd the same.
Nothing that moves a kart: online stays 120.
Run once: py.cmd tools/mini/patch73.py"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'patch 73' not in s, 'already patched'


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:90])
    s = s.replace(a, b)


rep("const STYLE={tr:['tr',TRIMS],ac:['tr',TRIMS],in:['tr',TRIMS],gl:['gl',GLOWS],hl:['hl',LIGHTS],sm:['sm',SMOKES]};",
    "const STYLE={tr:['tr',TRIMS],ac:['tr',TRIMS],in:['tr',TRIMS],rm:['tr',TRIMS],gl:['gl',GLOWS],hl:['hl',LIGHTS],sm:['sm',SMOKES]};/* (patch 73: rm, the rims) */\n"
    "/* (patch 73) colour combos: p a paint (PAINTS), st the style; $ the price (0 free). KEEP THE ORDER (owned ones are 'cb'+index), the PC's style.gd the same */\n"
    "const COMBOS=[{n:'Stealth',p:8,st:{tr:1,ac:1,in:1,rm:1,gl:0,hl:1,sm:0},$:0},{n:'Track Day',p:1,st:{tr:1,ac:2,in:1,rm:3,gl:0,hl:1,sm:0},$:0},\n"
    "  {n:'Arctic',p:9,st:{tr:3,ac:13,in:2,rm:3,gl:1,hl:2,sm:0},$:350},{n:'Midnight Neon',p:8,st:{tr:14,ac:13,in:1,rm:14,gl:1,hl:2,sm:2},$:450},\n"
    "  {n:'Toxic',p:4,st:{tr:1,ac:12,in:12,rm:1,gl:4,hl:5,sm:5},$:500},{n:'Miami',p:7,st:{tr:2,ac:13,in:2,rm:2,gl:5,hl:1,sm:7},$:550},\n"
    "  {n:'Inferno',p:2,st:{tr:1,ac:4,in:4,rm:15,gl:3,hl:3,sm:3},$:600},{n:'Royal Gold',p:6,st:{tr:16,ac:16,in:11,rm:16,gl:2,hl:0,sm:4},$:650},\n"
    "  {n:'Chrome King',p:8,st:{tr:17,ac:17,in:1,rm:17,gl:7,hl:1,sm:1},$:900},{n:'Spectrum',p:5,st:{tr:1,ac:10,in:1,rm:17,gl:8,hl:4,sm:8},$:1200}];\n"
    "function comboOwned(i){const c=COMBOS[i];return !!c&&(!c.$||styleCheat()||ownedSet().has('cb'+i));}\n"
    "function comboAllows(slot,i){for(let j=0;j<COMBOS.length;j++){const c=COMBOS[j];if(c.$&&(c.st[slot]|0)===i&&i&&ownedSet().has('cb'+j))return true;}return false;}\n"
    "function comboBuy(i){const c=COMBOS[i],sv=sbSave();if(!c||comboOwned(i))return true;if((sv.c||0)<c.$)return false;sv.c-=c.$;sbKeep();const o=ownedSet();o.add('cb'+i);store.set('crust-own',JSON.stringify([...o]));return true;}")
rep("function styleOwned(slot,i){const [g,L]=STYLE[slot];if(styleCheat())return true;/* (patch 70: UNLOCK) */return !L[i]||!L[i].$||ownedSet().has(g+i);}",
    "function styleOwned(slot,i){const [g,L]=STYLE[slot];if(styleCheat())return true;/* (patch 70: UNLOCK) */return !L[i]||!L[i].$||ownedSet().has(g+i)||comboAllows(slot,i);/* (patch 73: a combo's piece, in its own slot) */}")
rep("if(i&&L[i]&&L[i].$&&!o.has(g+i)){st[sl]=0;ch=true;}", "if(i&&L[i]&&L[i].$&&!o.has(g+i)&&!comboAllows(sl,i)){st[sl]=0;ch=true;}")
# the rims' material
rep("const _hgF={};function hoverGlowFor(id){",
    "/* (patch 73) the rims' colour: a wheel's metal classes (metal 7, chrome 10, rim 11, gunmetal 15, bronze 19, steel 21) repainted, metal or satin */\n"
    "const _rvc={};function rimVC(st,ds){const r=TRIMS[(st&&st.rm)|0];if(!r||!r.h)return null;const key=(st.rm|0)+(ds?'d':'');if(_rvc[key])return _rvc[key];const m=SH.carVC.clone();if(ds)m.side=THREE.DoubleSide;\n"
    "  const U={uR:{value:new THREE.Color(r.h)},uRM:{value:new THREE.Vector2(r.m?.95:.3,r.m?(r.r||.2):.38)}};\n"
    "  m.onBeforeCompile=sh=>{Object.assign(sh.uniforms,U);sh.fragmentShader='uniform vec3 uR;uniform vec2 uRM;\\n'+sh.fragmentShader.replace('#include <color_fragment>','#include <color_fragment>\\n'\n"
    "    +'float rCi=floor(vUv.x*32.);float rMx=max(vColor.r,max(vColor.g,vColor.b));float rG=0.;\\n'\n"
    "    +'if(abs(rCi-7.)<.1||abs(rCi-10.)<.1||abs(rCi-11.)<.1||abs(rCi-15.)<.1||abs(rCi-19.)<.1||abs(rCi-21.)<.1){diffuseColor.rgb=uR*clamp(rMx/.7,.45,1.15);rG=1.;}').replace('#include <metalnessmap_fragment>','#include <metalnessmap_fragment>\\n'\n"
    "    +'if(rG==1.){metalnessFactor=uRM.x;roughnessFactor=uRM.y;}');};\n"
    "  m.customProgramCacheKey=()=>'carvc-rim';SHSET.add(m);return _rvc[key]=m;}\n"
    "const _hgF={};function hoverGlowFor(id){")
rep("const M={paint,dark:new THREE.MeshStandardMaterial(", "const M={rimM:rimVC(stOf(spec)),rimW:rimVC(stOf(spec),1),paint,dark:new THREE.MeshStandardMaterial(")
rep("wh=new THREE.Mesh(cg['w'+wi],SH.carVC);", "wh=new THREE.Mesh(cg['w'+wi],M.rimM||SH.carVC);/* (patch 73: the rims' colour) */", 2)
rep("const m=new THREE.Mesh(packWheelGeo(wd.pack,wd.g,side),wd.pack==='wheelset'?wheelVC():SH.carVC);",
    "const m=new THREE.Mesh(packWheelGeo(wd.pack,wd.g,side),wd.pack==='wheelset'?(M&&M.rimW||wheelVC()):(M&&M.rimM||SH.carVC));/* (patch 73) */")
# the garage: the combos, the Rims row
rep("  w.innerHTML='<p class=\"g-sub style-coins\">Style shop · <b>'+coins+'</b> coins</p>'+row('tr','Trim')+row('ac','Accent')+row('in','Interior')+row('gl','Underglow')+row('hl','Headlights')+row('sm','Tyre smoke');",
    "  const chip=h=>'<i style=\"display:inline-block;width:14px;height:14px;border-radius:50%;margin-right:-4px;box-shadow:0 0 0 2px #1a1210;background:'+(h==='rainbow'?'conic-gradient(#ff3030,#ffd22a,#3dff6a,#2ae8ff,#a040ff,#ff3030)':h||'#333')+'\"></i>';\n"
    "  const cards=COMBOS.map((c,i)=>{const own=comboOwned(i),on=playerBuild.p===c.p&&!playerBuild.t&&Object.keys(c.st).every(k=>(st[k]|0)===c.st[k]);/* (patch 73) */\n"
    "    return '<button type=\"button\" class=\"combo\" data-c=\"'+i+'\" aria-pressed=\"'+on+'\" style=\"display:flex;flex-direction:column;gap:5px;align-items:flex-start;padding:8px 10px;border-radius:12px;border:2px solid '+(on?'#f7c948':'rgba(255,244,220,.14)')+';background:rgba(0,0,0,.28);color:#fff4dc;font:inherit;cursor:pointer;min-width:0\">'\n"
    "      +'<b style=\"font-size:13px\">'+c.n+'</b><span>'+[PAINTS[c.p],TRIMS[c.st.tr].h,TRIMS[c.st.ac].h,TRIMS[c.st.rm].h,GLOWS[c.st.gl].h].map(chip).join('')+'</span><small style=\"opacity:.8\">'+(own?(c.$?'Owned':'Free'):c.$+' coins')+'</small></button>';}).join('');\n"
    "  w.innerHTML='<p class=\"g-sub style-coins\">Style shop · <b>'+coins+'</b> coins</p><p class=\"g-sub\">Combos</p><div class=\"combos\" style=\"display:grid;grid-template-columns:repeat(auto-fill,minmax(118px,1fr));gap:8px\">'+cards+'</div>'+row('tr','Trim')+row('ac','Accent')+row('in','Interior')+row('rm','Rims')+row('gl','Underglow')+row('hl','Headlights')+row('sm','Tyre smoke');\n"
    "  w.querySelectorAll('button.combo').forEach(b=>b.onclick=()=>{const i=+b.dataset.c,c=COMBOS[i];\n"
    "    if(!comboOwned(i)){const have=sbSave().c||0;if(have<c.$){achToast(null,'<b>'+c.n+'</b> costs '+c.$+' coins. You have '+have+'. Earn coins by racing and in Sandbox.');return;}\n"
    "      if(styleAsk!=='cb'+i){styleAsk='cb'+i;achToast(null,'Tap <b>'+c.n+'</b> again to buy it for '+c.$+' coins. Its colours are yours for the parts it puts them on.');return;}styleAsk=null;comboBuy(i);try{SFX.ready();}catch(e){}}\n"
    "    playerBuild.p=c.p;playerBuild.t='';playerBuild.st=Object.assign({},c.st);saveBuild();refreshGarage(true);});")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patch 73 applied')
