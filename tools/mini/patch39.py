"""Patch 39 (web v203, with patch 38; ONLINE VERSION 114): two changes to the specials from patch 37.
The owner, 2026-11-15: "make the pineapple go through the garlic shield but not the mozz shield ... make anchovy not blockable
instead let's go with the 2 anchovies instead of 3".
- Pineapple (Spiky Shockwave): only Mozz's Melt Shield (shield with mzH) is popped without a spin; garlic cloves (shL) no longer stop it:
  the kart spins and keeps its cloves (as before patch 37).
- Anchovy (School of Fish): two fish (the next two ahead, or two behind), not three; nothing blocks one any more: no held item (patch 37
  undone), and a Mozz shield is cleared before the hit so the forced spin goes through it. A hop still dodges, and a kart blinking after a
  hit or under an ability boost is still safe, as before.
The PC has the same in race.gd. Run once: py.cmd tools/mini/patch39.py"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'patch 39' not in s, 'already patched'


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:90])
    s = s.replace(a, b)


rep("and only pops a shield */if(k.shield>0||k.shL>0){k.shield=0;k.mzH=0;k.shL=0;k.absT=.6;",
    "and only pops a Mozz shield (patch 39: garlic no longer stops it) */if(k.shield>0&&k.mzH>0){k.shield=0;k.mzH=0;k.absT=.6;")
rep("if(absorbHeld(tg)){p.pop=1;return true;}/* (patch 37) a held item stops the fish */", "")
rep("if(tg===player)hitBy(p);p.pop=1;if(spinOut(tg,'pep',true)){",
    "if(tg===player)hitBy(p);p.pop=1;tg.shield=0;tg.mzH=0;/* (patch 39) nothing blocks a fish: a Mozz shield goes */if(spinOut(tg,'pep',true)){")
rep("if(id==='anchovy'){for(let j=1;j<=3;j++){const tg=st[back?i+j:i-j];/* looking back: the three behind you */",
    "if(id==='anchovy'){for(let j=1;j<=2;j++){const tg=st[back?i+j:i-j];/* (patch 39: two, was three) looking back: the two behind you */")
rep("an=k.a+(back?Math.PI:0)+(j-2)*.25;", "an=k.a+(back?Math.PI:0)+(j-1.5)*.25;")
rep("A spiky blast that spins out every racer close to you. It goes through ability boosts and Delivery Rush, and pops a shield without a spin.",
    "A spiky blast that spins out every racer close to you. It goes through garlic, ability boosts and Delivery Rush; a Mozz Melt Shield pops without a spin.")
rep("Launches three anchovies that hunt down the next three racers ahead, or the three behind you if you launch them looking back. They always reach their target, but a well-timed hop dodges one and an item held behind you stops one.",
    "Launches two anchovies that hunt down the next two racers ahead, or the two behind you if you launch them looking back. Nothing blocks them, not even a shield; only a well-timed hop dodges one.")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patch 39 applied')
