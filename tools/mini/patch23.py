"""Patch 23 (web v191): Sandbox in every room of the house.
- The menu: in Sandbox the track list shows the places that have a Sandbox region (tools/mini/sandbox.js, SB_REG), so you can choose where to
  start until the doors between them are passages. `sbMenu()` (sandbox.js) does the showing and hiding; this patch calls it.
- The engine: a shortcut lane's own race rule (scStep) is off in Sandbox. A toy shortcut lies on the floor: in Sandbox it is just floor.
Run once: py.cmd tools/mini/patch23.py   (then inject_mini.py)"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'sbMenu()' not in s, 'already patched'


def rep(a, b):
    global s
    assert s.count(a) == 1, (s.count(a), a[:70])
    s = s.replace(a, b)


rep("function scStep(k){if(!SHORTS.length)return;", "function scStep(k){if(SBX||!SHORTS.length)return;")
rep("$('maps').hidden=mode==='gp'||mode==='bb'||mode==='sb';if($('mapsWrap'))$('mapsWrap').hidden=mode==='gp'||mode==='bb'||mode==='sb';$('trackLabel').textContent=mode==='gp'?'Cup':mode==='bb'?'Arena: Prep Table Showdown':mode==='sb'?'World: Home, the back garden':'Track';",
    "$('maps').hidden=mode==='gp'||mode==='bb';if($('mapsWrap'))$('mapsWrap').hidden=mode==='gp'||mode==='bb';$('trackLabel').textContent=mode==='gp'?'Cup':mode==='bb'?'Arena: Prep Table Showdown':mode==='sb'?'World: Home. Start in':'Track';sbMenu();")
rep("si=MAPS.findIndex(m=>m.id==='backyard'),want=mode==='bb'?bi:mode==='sb'?si:mapIdx===bi?0:mapIdx;",
    "si=SB_REG[MAPS[mapIdx].id]?mapIdx:MAPS.findIndex(m=>m.id==='backyard'),want=mode==='bb'?bi:mode==='sb'?si:mapIdx===bi?0:mapIdx;")
rep("if(mode==='sb'){const si=MAPS.findIndex(m=>m.id==='backyard');if(si>=0)mapIdx=si;}", "if(mode==='sb'&&!SB_REG[MAPS[mapIdx].id]){const si=MAPS.findIndex(m=>m.id==='backyard');if(si>=0)mapIdx=si;}")
rep("mn.textContent='Sandbox: drive anywhere, no race and no clock. Leave the track, cross the lawn, look behind things. Gold coins lead the way; six pepperoni coins are hidden in the garden. More of the house and the world beyond are on their way.';",
    "mn.textContent='Sandbox: drive anywhere, no race and no clock. Leave the track, go under the furniture, look behind things. Gold coins lead the way; pepperoni coins are hidden in every room. Choose where to start: the doors between the rooms, and the world beyond the house, are on their way.';")
open(p, 'w', encoding='utf-8', newline='').write(s)

p = 'D:/crust-rush/source/tools/mini/sandbox.js'
s = open(p, encoding='utf-8', newline='').read()
rep("/* ---- the track as ground: a grid of which lap points lie near each cell ---- */",
    "/* the menu in Sandbox: the track list shows only the places that have a region, and no cup tabs */\n"
    "function sbMenu(){const on=mode==='sb',cats=document.getElementById('mapCats'),ms=document.getElementById('maps');if(!ms)return;if(cats)cats.hidden=on;\n"
    "  if(on)ms.querySelectorAll('.mapc').forEach((b,i)=>{b.hidden=!SB_REG[MAPS[i].id];});else if(typeof setMapCat==='function'&&typeof mapCat!=='undefined'&&mapCat!=null)setMapCat(mapCatOf(MAPS[mapIdx]));}\n"
    "/* ---- the track as ground: a grid of which lap points lie near each cell ---- */")
rep("const SB_REG={", "const SB_REG={\n  /* the three rooms: their things are read from what is drawn (sbColumns), their coins along the track are laid by sbCoins; the rest is here */\n"
    "  bedroom:{name:'Home \\u00b7 Bedroom',lines:[],rings:[],rare:[]},\n  kitchen:{name:'Home \\u00b7 Kitchen',lines:[],rings:[],rare:[]},\n  garage:{name:'Home \\u00b7 Garage',lines:[],rings:[],rare:[]},")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patched')
