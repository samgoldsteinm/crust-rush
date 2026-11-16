"""Patch 47 (web v209, NET_PROTO 116): races without items, and their own world board.
The owner: "make a section in records next to with rivals and alone that is a without items section that shows records for games without
items", then: "the game always forces at least one item to be on. when you turn items off the item boxes should just disappear. this way
players can attempt to set personal bests where everything is fair. you should be able to turn items [off on]line as well. the game will
pull from the hosts selected options".
- The item guide no longer keeps one item on. Every item off = NO ITEMS: itemsOff(). The menu also has Items: On / Off (under Computer
  racers): Off switches every item off, On puts the guide back to its defaults. One setting, two places (ITEMSET, 'crust-items').
- NOITM (this race) is set by resetRace: never for the menu's demo race, Last Slice, Balloon Battle or Sandbox; off line from
  itemsOff(); on line from the host's choice, cfg.ni (netBuildCfg). While it is on the item boxes are not drawn and give nothing (the
  host's box loop and a guest's predicted pickups are skipped). Specials (the drivers' abilities) still work: they are not items. The
  host already chooses every rolled item (rollItem runs on the host), so its item guide applies to everyone; cfg.ni adds the boxes.
- cfg.ni is a new race field: NET_PROTO 116 (the PC must send and read it too).
- the world board: runs.noitems (lb_schema_noitems.sql, run once in the SQL editor; it keeps every time). The view puts a no-items run
  on its own board and gives it solo = null, so the older boards (solo=eq.true/false) never show it. A run without items is sent with
  p_noitems; any other run is sent exactly as before. With only some items off a run counts on the usual boards, as before.
- the leaderboard sheet: With rivals | Alone | No items.
Run once: py.cmd tools/mini/patch47.py"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'patch 47' not in s, 'already patched'


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:80])
    s = s.replace(a, b)


# the menu's switch (the same setting as the item guide)
rep('<p class="seg-note" id="cpuNote"></p></section>',
    '<p class="seg-note" id="cpuNote"></p></section>\n        <section id="itmSec"><h2 class="label">Items</h2><div class="seg seg2" id="itmSeg"><button type="button" data-i="1">On</button>'
    '<button type="button" data-i="0">Off</button></div><p class="seg-note" id="itmNote"></p></section>')
rep("let CPUS=(()=>{",
    "/* races without items (patch 47): every item switched off in the guide; NOITM is this race's (set by resetRace) */\n"
    "let NOITM=false;function itemsOff(){return !ITEM_LIST.some(itemOn);}\n"
    "function itmNote(){const e=$('itmNote'),sec=$('itmSec');if(!e)return;if(sec)sec.hidden=mode==='lss'||mode==='bb'||mode==='sb';"
    "document.querySelectorAll('#itmSeg button').forEach(b=>b.setAttribute('aria-pressed',String((b.dataset.i==='0')===itemsOff())));"
    "e.textContent=(NET.role==='guest'?'The host chooses. ':NET.role==='host'?'Your friends race with yours. ':'')+(itemsOff()?'No item boxes: just driving. Times go on the No items leaderboards'"
    ":ITEM_LIST.every(k=>!itemUnlocked(k)||itemOn(k))?'Item boxes on the track':'Item boxes on the track (some items switched off in the guide)');}\n"
    "let CPUS=(()=>{")
rep("document.querySelectorAll('#cpuSeg button').forEach(b=>b.onclick=()=>{CPUS=clamp(CPUS+(+b.dataset.d),0,7);store.set('crust-cpus',String(CPUS));refreshMenu();});",
    "document.querySelectorAll('#cpuSeg button').forEach(b=>b.onclick=()=>{CPUS=clamp(CPUS+(+b.dataset.d),0,7);store.set('crust-cpus',String(CPUS));refreshMenu();});"
    "document.querySelectorAll('#itmSeg button').forEach(b=>b.onclick=()=>{if(b.dataset.i==='0'){for(const k of ITEM_LIST)ITEMSET[k]=false;}else if(itemsOff())ITEMSET={};"
    "saveItemSet();if(typeof renderItemSet==='function')renderItemSet();refreshMenu();});")
rep("{const v=$('cpuVal');if(v)v.textContent=String(CPUS);const n=$('cpuNote');if(n)n.textContent=cpuNote();}",
    "{const v=$('cpuVal');if(v)v.textContent=String(CPUS);const n=$('cpuNote');if(n)n.textContent=cpuNote();}itmNote();")

# the guide no longer keeps one item on
rep("if(on&&ITEM_LIST.filter(itemOn).length<=1)return;/* keep at least one item */ITEMSET[k]=!on;saveItemSet();renderItemSet();}",
    "ITEMSET[k]=!on;saveItemSet();renderItemSet();if(typeof refreshMenu==='function'&&state==='menu')refreshMenu();}/* (patch 47: every item may be off: no item boxes) */")

# this race; on line the host's choice
rep("ssPending=null;fit();}\n  warmScene();\n}",
    "ssPending=null;fit();}\n  NOITM=!demo&&mode!=='lss'&&mode!=='bb'&&mode!=='sb'&&(NET.cfg?!!NET.cfg.ni:!NET.role&&itemsOff());/* (patch 47) */\n  warmScene();\n}")
rep("ks.sort((a,b)=>a.slot-b.slot);return {mi,cls:clsKey,mode,gp:gp?JSON.parse(JSON.stringify(gp)):null,karts:ks};}",
    "ks.sort((a,b)=>a.slot-b.slot);return {mi,cls:clsKey,mode,gp:gp?JSON.parse(JSON.stringify(gp)):null,karts:ks,ni:itemsOff()};}")
rep("const NET_PROTO=115;", "const NET_PROTO=116;/* (patch 47: cfg.ni, a race without items) */")
rep("for(const b of boxes){if(b.r>0){b.r-=dt;continue;}for(const k of karts){if(BOXCD&&k.boxT>simTime)continue;",
    "if(!NOITM)for(const b of boxes){if(b.r>0){b.r-=dt;continue;}for(const k of karts){if(BOXCD&&k.boxT>simTime)continue;")
rep("if(state==='race'&&!k.finished)for(const b of boxes){if(b.r>0||b.pr>simTime",
    "if(state==='race'&&!k.finished&&!NOITM)for(const b of boxes){if(b.r>0||b.pr>simTime")
rep("const br=b.r>0?b.r:(b.pr>simTime?1:0)",
    "const br=NOITM?1:b.r>0?b.r:(b.pr>simTime?1:0)")

# the world board
rep("solo:karts.length===1,at:Date.now()});lbSaveQ(q);lbFlush();}",
    "solo:karts.length===1,ni:NOITM,at:Date.now()});lbSaveQ(q);lbFlush();}")
rep("p_platform:'web',p_ver:ver||'web',p_solo:!!r.solo});q.shift();lbSaveQ(q);}",
    "p_platform:'web',p_ver:ver||'web',p_solo:!!r.solo,...(r.ni?{p_noitems:true}:{})});q.shift();lbSaveQ(q);}")
rep("'&cls=eq.'+cls+'&solo=eq.'+(solo?'true':'false')+'&order=",
    "'&cls=eq.'+cls+(solo==='ni'?'&noitems=eq.true':'&solo=eq.'+(solo?'true':'false')+'&noitems=eq.false')+'&order=")
rep('<div class="seg seg2" id="lbSolo"><button data-s="0">With rivals</button><button data-s="1">Alone</button></div>',
    '<div class="seg seg3" id="lbSolo"><button data-s="0">With rivals</button><button data-s="1">Alone</button><button data-s="2">No items</button></div>')
rep("b.onclick=()=>{lbSt.solo=b.dataset.s==='1';lbDraw();}",
    "b.onclick=()=>{lbSt.solo=b.dataset.s==='2'?'ni':b.dataset.s==='1';lbDraw();}")
rep("b.setAttribute('aria-pressed',String((b.dataset.s==='1')===lbSt.solo))",
    "b.setAttribute('aria-pressed',String(b.dataset.s==='2'?lbSt.solo==='ni':(b.dataset.s==='1')===lbSt.solo))")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patch 47 applied')
