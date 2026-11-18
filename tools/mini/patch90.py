"""Patch 90 (web v227): more colour combos, some made for one kind of vehicle, and your own saved combos.
The owner: "Add more color combos and make some specific to the vehicle also make is that people can save their own custom color
combo and reuse it for any vehicle they want in the future".
- COMBOS 10..29 (appended: owned combos are 'cb'+index, KEEP THE ORDER; the PC's style.gd the same, pc86): ten for every vehicle,
  each with a calipers colour; ten with only: [body ids] (Pursuit for the Interceptor, Mud Slinger for the Monster Truck, Steam Baron
  for the Chariot, Pit Lane for the open-wheelers, Night Stint for the endurance racers, Grand Tour for the luxury cars, Pizza Rider
  for the bikes, Hypersonic for the hypercars, Cheese Wheel for the food karts, Heritage for the classics). A vehicle's own combos
  show first, marked with a star, only when that vehicle is in the garage.
- My combos (localStorage 'crust-mycombos', up to 12): "Save this look" keeps the paint, livery and every style slot under a name;
  tapping one puts it on whatever vehicle is in the garage (a livery made for another vehicle is left off: its colours stay; a style
  piece no longer owned is left at stock); the x deletes it (a second tap confirms).
Run once, after patch 89: tools/py.cmd tools/mini/patch90.py"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'patch 90' not in s, 'already patched'


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:90])
    s = s.replace(a, b)


rep("{n:'Chrome King',p:8,st:{tr:17,ac:17,in:1,rm:17,gl:7,hl:1,sm:1},$:900},{n:'Spectrum',p:5,st:{tr:1,ac:10,in:1,rm:17,gl:8,hl:4,sm:8},$:1200}];",
    "{n:'Chrome King',p:8,st:{tr:17,ac:17,in:1,rm:17,gl:7,hl:1,sm:1},$:900},{n:'Spectrum',p:5,st:{tr:1,ac:10,in:1,rm:17,gl:8,hl:4,sm:8},$:1200},\n"
    "  /* (patch 90) ten more for every vehicle, then ten made for one kind (only: its body ids) */\n"
    "  {n:'Blackout',p:23,st:{tr:1,ac:1,in:1,rm:1,cl:1,gl:0,hl:1,sm:1},$:200},{n:'Sunburst',p:11,st:{tr:1,ac:1,in:1,rm:1,cl:4,gl:6,hl:3,sm:6},$:350},\n"
    "  {n:'Racing Green',p:13,st:{tr:1,ac:16,in:11,rm:16,cl:16,gl:0,hl:0,sm:0},$:400},{n:'Sky Rocket',p:15,st:{tr:2,ac:5,in:1,rm:2,cl:5,gl:1,hl:1,sm:2},$:450},\n"
    "  {n:'Teal Wave',p:14,st:{tr:2,ac:2,in:2,rm:3,cl:5,gl:1,hl:2,sm:2},$:450},{n:'Copper Sunset',p:18,st:{tr:1,ac:6,in:11,rm:15,cl:6,gl:6,hl:3,sm:6},$:500},\n"
    "  {n:'Grape Soda',p:6,st:{tr:1,ac:10,in:9,rm:3,cl:10,gl:2,hl:4,sm:4},$:500},{n:'Lime Rush',p:12,st:{tr:1,ac:1,in:12,rm:1,cl:12,gl:4,hl:5,sm:5},$:500},\n"
    "  {n:'Ice Queen',p:22,st:{tr:3,ac:13,in:2,rm:17,cl:13,gl:1,hl:2,sm:0},$:550},{n:'Navy Brass',p:16,st:{tr:2,ac:16,in:11,rm:15,cl:16,gl:0,hl:0,sm:0},$:600},\n"
    "  {n:'Pursuit',p:23,st:{tr:2,ac:2,in:1,rm:3,cl:8,gl:0,hl:2,sm:0},$:400,only:['interceptor']},{n:'Mud Slinger',p:13,st:{tr:1,ac:6,in:1,rm:1,cl:6,gl:6,hl:3,sm:1},$:400,only:['monster']},\n"
    "  {n:'Steam Baron',p:18,st:{tr:15,ac:16,in:11,rm:15,cl:16,gl:6,hl:3,sm:0},$:500,only:['chariot']},{n:'Pit Lane',p:1,st:{tr:1,ac:2,in:1,rm:1,cl:4,gl:0,hl:1,sm:0},$:350,only:['formula','gokart','rollpin']},\n"
    "  {n:'Night Stint',p:16,st:{tr:1,ac:6,in:1,rm:1,cl:6,gl:1,hl:3,sm:0},$:450,only:['endur','retrogt','gt']},{n:'Grand Tour',p:17,st:{tr:17,ac:17,in:11,rm:17,cl:1,gl:0,hl:0,sm:0},$:600,only:['coupe','tourer','suv']},\n"
    "  {n:'Pizza Rider',p:2,st:{tr:1,ac:6,in:1,rm:1,cl:6,gl:0,hl:3,sm:3},$:400,only:['bike_moto','bike_mx','bike_neutron','bike_june','bike_rocket']},\n"
    "  {n:'Hypersonic',p:21,st:{tr:1,ac:13,in:1,rm:14,cl:13,gl:1,hl:2,sm:2},$:550,only:['hyper','skywing','megawatt','megagt','scissor','onyx','concept','slip']},\n"
    "  {n:'Cheese Wheel',p:3,st:{tr:4,ac:2,in:4,rm:2,cl:4,gl:6,hl:3,sm:6},$:350,only:['classic','wedge','tomato','delivery','cutter','oven','grater','comet','oilcan','rocket']},\n"
    "  {n:'Heritage',p:10,st:{tr:1,ac:2,in:11,rm:17,cl:1,gl:0,hl:0,sm:0},$:450,only:['muscle','roadster','hatch','interceptor']}];\n"
    "/* (patch 90) your own combos: the paint, livery and style, kept under a name, for any vehicle */\n"
    "const mEsc=s=>String(s).replace(/[<>&\"]/g,c=>({'<':'&lt;','>':'&gt;','&':'&amp;','\"':'&quot;'})[c]);const MYC_KEY='crust-mycombos';function myCombos(){try{const a=JSON.parse(store.get(MYC_KEY)||'[]');return Array.isArray(a)?a.filter(c=>c&&typeof c==='object'&&c.st&&typeof c.st==='object'):[];}catch(e){return [];}}\n"
    "function myCombosPut(a){try{store.set(MYC_KEY,JSON.stringify(a.slice(0,12)));}catch(e){}}")
# the combo cards: this vehicle's own first (starred), the rest; the Calipers colour in the chips
rep("  const cards=COMBOS.map((c,i)=>{const own=comboOwned(i),on=playerBuild.p===c.p&&!playerBuild.t&&Object.keys(c.st).every(k=>(st[k]|0)===c.st[k]);/* (patch 73) */",
    "  const bid=BODIES[playerBuild.b].id,order=COMBOS.map((c,i)=>i).filter(i=>!COMBOS[i].only||COMBOS[i].only.includes(bid)).sort((a,b)=>(COMBOS[b].only?1:0)-(COMBOS[a].only?1:0));/* (patch 90: this vehicle's own first) */\n"
    "  const cards=order.map(i=>{const c=COMBOS[i],own=comboOwned(i),on=playerBuild.p===c.p&&!playerBuild.t&&Object.keys(c.st).every(k=>(st[k]|0)===c.st[k]);/* (patch 73) */")
rep("      +'<b style=\"font-size:13px\">'+c.n+'</b><span>'+[PAINTS[c.p],TRIMS[c.st.tr].h,TRIMS[c.st.ac].h,TRIMS[c.st.rm].h,GLOWS[c.st.gl].h].map(chip).join('')+'</span>",
    "      +'<b style=\"font-size:13px\">'+(c.only?'\\u2605 ':'')+c.n+'</b><span>'+[PAINTS[c.p],TRIMS[c.st.tr].h,TRIMS[c.st.ac].h,TRIMS[c.st.rm].h,TRIMS[c.st.cl|0].h,GLOWS[c.st.gl].h].map(chip).join('')+'</span>")
# My combos: the cards, a save card
rep("+'</div>'+row('tr','Trim')+",
    "+'</div>'+myCards(st,chip)+row('tr','Trim')+")
rep("let styleAsk=null;function styleUI(){",
    "/* (patch 90) My combos: a card each (tap: wear it; x: delete, a second tap confirms) and a card to save the current look */\n"
    "function myCards(st,chip){const M=myCombos(),lvOf=t=>t?livOf(t):null;\n"
    "  const cs=M.map((c,i)=>{const on=playerBuild.p===c.p&&(playerBuild.t||'')===(c.t||'')&&Object.keys(STYLE).every(k=>(st[k]|0)===(c.st[k]|0)),lv=lvOf(c.t);\n"
    "    return '<div style=\"position:relative;min-width:0\"><button type=\"button\" class=\"combo myc\" data-m=\"'+i+'\" aria-pressed=\"'+on+'\" style=\"width:100%;display:flex;flex-direction:column;gap:5px;align-items:flex-start;padding:8px 26px 8px 10px;border-radius:12px;border:2px solid '+(on?'#f7c948':'rgba(255,244,220,.14)')+';background:rgba(0,0,0,.28);color:#fff4dc;font:inherit;cursor:pointer;min-width:0\">'\n"
    "      +'<b style=\"font-size:13px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:100%\">'+mEsc(c.n||'My combo')+'</b><span>'+[lv?lv.A:PAINTS[c.p],TRIMS[c.st.tr|0].h,TRIMS[c.st.ac|0].h,TRIMS[c.st.rm|0].h,TRIMS[c.st.cl|0].h,GLOWS[c.st.gl|0].h].map(chip).join('')+'</span><small style=\"opacity:.8\">'+(lv?mEsc(lv.name):'Saved')+'</small></button>'\n"
    "      +'<button type=\"button\" class=\"mydel\" data-d=\"'+i+'\" aria-label=\"Delete '+mEsc(c.n||'combo')+'\" title=\"Delete\" style=\"position:absolute;top:4px;right:4px;width:22px;height:22px;border-radius:50%;border:0;background:rgba(0,0,0,.45);color:#fff4dc;font:bold 13px/22px sans-serif;cursor:pointer;padding:0\">\\u00d7</button></div>';}).join('');\n"
    "  const sv=M.length<12?'<button type=\"button\" class=\"combo mysave\" style=\"display:flex;flex-direction:column;gap:4px;align-items:center;justify-content:center;padding:8px 10px;border-radius:12px;border:2px dashed rgba(255,244,220,.35);background:rgba(0,0,0,.18);color:#fff4dc;font:inherit;cursor:pointer;min-height:64px\"><b style=\"font-size:20px;line-height:1\">+</b><small>Save this look</small></button>':'';\n"
    "  return '<p class=\"g-sub\">My combos</p><div class=\"combos\" style=\"display:grid;grid-template-columns:repeat(auto-fill,minmax(118px,1fr));gap:8px\">'+cs+sv+'</div>';}\n"
    "function myWear(i){const c=myCombos()[i];if(!c)return;const b=BODIES[playerBuild.b],lv=c.t?livOf(c.t):null,lvOk=!!(lv&&(!lv.only||lv.only===b.id)&&!livLocked(lv));\n"
    "  const st={};let lost=0;for(const k in STYLE){const v=c.st[k]|0;if(v&&!styleOwned(k,v)){lost++;continue;}if(v)st[k]=v;}\n"
    "  playerBuild.p=Math.max(0,Math.min(PAINTS.length-1,c.p|0));playerBuild.t=lvOk?c.t:'';playerBuild.st=st;saveBuild();refreshGarage(true);\n"
    "  if(c.t&&!lvOk)achToast(null,'<b>'+mEsc(c.n||'Your combo')+'</b>: its livery is made for another vehicle, so its paint and colours went on.');else if(lost)achToast(null,'Some of <b>'+mEsc(c.n||'this combo')+'</b>\\u2019s colours are not yours yet: those parts are stock.');}\n"
    "function mySave(){const M=myCombos();if(M.length>=12){achToast(null,'You can keep 12 combos. Delete one first.');return;}let n='My look '+(M.length+1);\n"
    "  try{const q=window.prompt('Name this combo',n);if(q===null)return;n=String(q).trim().slice(0,24)||n;}catch(e){}\n"
    "  M.push({n,p:playerBuild.p|0,t:playerBuild.t||'',st:Object.assign({},playerBuild.st||{})});myCombosPut(M);achToast(null,'Saved <b>'+mEsc(n)+'</b>. Wear it on any vehicle from My combos.');styleUI();}\n"
    "let styleAsk=null;function styleUI(){")
rep("  w.querySelectorAll('button.combo').forEach(b=>b.onclick=()=>{const i=+b.dataset.c,c=COMBOS[i];",
    "  w.querySelectorAll('button.myc').forEach(b=>b.onclick=()=>myWear(+b.dataset.m));const msv=w.querySelector('button.mysave');if(msv)msv.onclick=mySave;\n"
    "  w.querySelectorAll('button.mydel').forEach(b=>b.onclick=e=>{e.stopPropagation();const i=+b.dataset.d,M=myCombos();if(!M[i])return;if(styleAsk!=='md'+i){styleAsk='md'+i;achToast(null,'Tap the \\u00d7 on <b>'+mEsc(M[i].n||'this combo')+'</b> again to delete it.');return;}styleAsk=null;M.splice(i,1);myCombosPut(M);styleUI();});\n"
    "  w.querySelectorAll('button.combo:not(.myc):not(.mysave)').forEach(b=>b.onclick=()=>{const i=+b.dataset.c,c=COMBOS[i];/* (patch 90: the shop's combos) */")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patch 90 applied')
