"""Patch 18 (web v179): a toy track waits for its Blender-built models before the room is built.
The room models are packs that download after the menu is up; a race started straight away used to get the code-built
stand-ins for the whole race. Now the loading screen holds for them, ten seconds at most, and only off line (an online
race must not wait on one player's download). Run once: py.cmd tools/mini/patch18.py"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
a = "    if(mi!==mapIdx||rev!==curRev){mapIdx=mi;loadMap(mi,rev);}await step(45,'Spreading the sauce…');"
assert s.count(a) == 1, s.count(a)
b = """    if(m.toy&&!NET.role&&typeof PROP_PACKS!=='undefined'&&(mi!==mapIdx||rev!==curRev)){/* a toy room's models are built in Blender and arrive after the menu: hold the loading screen for them (10 s at most; never on line) */
      const late=()=>Object.keys(PROP_PACKS).some(k=>k.startsWith('toy_')&&k.endsWith('_hq')&&!(PROP_PACKS[k].b||PROP_PACKS[k].d)),t0=performance.now();
      while(late()&&performance.now()-t0<10000){await step(8+Math.min(34,(performance.now()-t0)/300),'Setting out the room…');await new Promise(r=>setTimeout(r,120));}}
"""
s = s.replace(a, b + a)
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patched')
