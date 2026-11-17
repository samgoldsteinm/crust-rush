"""Patch 70 (web v221): the UNLOCK cheat code opens the whole style shop too.
The owner: "Make the unlock cheat code unlock everything in the game without affecting actual earnings so the different trim colors and
underglow etc the different karts that cost coins all those should be unlocked when using the unlock code but shouldn't effect actual
game achievements or stats"
- styleOwned() is true for everything while CHEAT is on: every trim / accent / interior colour, underglow, headlight colour and tyre smoke
  can be picked, and styleBuy() then charges nothing and records nothing (crust-own and the coins are untouched).
- CHEAT is for this session only (as the liveries: livLocked), so at start-up a style in the saved build that is not really owned goes
  back to the free default (index 0). Other players' styles online are theirs and are never touched.
- Karts and cars are not sold for coins (their reward liveries and items are Awards, which UNLOCK already opened).
Nothing that moves a kart: the online version stays 120.
Run once: py.cmd tools/mini/patch70.py"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'patch 70' not in s, 'already patched'


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:90])
    s = s.replace(a, b)


rep("function styleOwned(slot,i){const [g,L]=STYLE[slot];return !L[i]||!L[i].$||ownedSet().has(g+i);}",
    "function styleOwned(slot,i){const [g,L]=STYLE[slot];if(styleCheat())return true;/* (patch 70: UNLOCK) */return !L[i]||!L[i].$||ownedSet().has(g+i);}\n"
    "function styleCheat(){try{return CHEAT;}catch(e){return false;}}/* (CHEAT is declared further down) */\n"
    "/* (patch 70) the UNLOCK code lasts one session: a saved style that was only picked under it goes back to the free default */\n"
    "{const st=playerBuild&&playerBuild.st;if(st&&typeof st==='object'){const o=ownedSet();let ch=false;for(const sl in STYLE){const i=st[sl]|0,[g,L]=STYLE[sl];if(i&&L[i]&&L[i].$&&!o.has(g+i)){st[sl]=0;ch=true;}}if(ch)try{store.set('crust-build',JSON.stringify(playerBuild));}catch(e){}}}")
rep("m.textContent='Unlocked! Every achievement, livery, car, track and reward item is open until you close the game. Your real progress is untouched.';",
    "m.textContent='Unlocked! Every achievement, livery, car, track, reward item and everything in the style shop is open until you close the game. No coins are spent and your real progress is untouched.';")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patch 70 applied')
