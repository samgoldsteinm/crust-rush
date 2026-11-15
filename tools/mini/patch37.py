"""Patch 37 (web v202, ONLINE VERSION 113): the drivers' special abilities evened out.
The owner, 2026-11-15, after asking which abilities were too strong or too weak: "Let's commit those changes".
- Pineapple (Spiky Shockwave): radius 260 -> 150; still goes through ability boosts and Delivery Rush, but karts in the air (and gliding)
  and karts still blinking after a hit are safe, and a shield (Mozz's cheese or the garlic) is popped without a spin.
- Anchovy (School of Fish): a held item stops a fish, as it stops any other item.
- Shroom (Mega Shroom): 5.5 s -> 4.5 s; squashed 3 s -> 2 s.
- Mozz (Melt Shield): the speed burst 0.7 s -> 2 s (and the Shockwave only pops the shield, above).
- Olive (Slick Trail): slicks catch a wider circle (r 14.1 -> 17.9, drawn 25% bigger), and a 1.2 s boost as the trail starts.
- Pep (Pepperoni Storm): slices fly 15% faster, and the first wall bounce bends a slice (at most about 30 degrees) toward the
  nearest racer ahead of it within 420.
The PC has the same in race.gd / view.gd / webnet.gd. Run once: py.cmd tools/mini/patch37.py"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'patch 37' not in s, 'already patched'


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:90])
    s = s.replace(a, b)


# Pineapple: what the forced hit goes through
rep("if(force){if(k.loop)return false;k.shield=0;k.mzH=0;k.absT=0;}",
    "if(force){if(k.loop||k.air||k.glide||k.inv>0)return false;/* (patch 37) the Shockwave misses karts in the air and anyone blinking after a hit, and only pops a shield */"
    "if(k.shield>0||k.shL>0){k.shield=0;k.mzH=0;k.shL=0;k.absT=.6;const gy=(k.wy||0)+7;burst(k.x,gy,k.y,30,['#fbf5e6','#fff2cf','#ffd23a'],90,2.8);spawnRing(k.x,gy,k.y,'#ffd23a',50,.45);if(k===player){SFX.clash(.7);shake(.3);}return false;}k.absT=0;}")
rep("blast(k.x,k.y,260,k,'pep','#ffd23a',true);", "blast(k.x,k.y,150,k,'pep','#ffd23a',true);")
# Anchovy: a held item stops a fish
rep("if(tg.air&&!tg.glide){/* hopped", "if(absorbHeld(tg)){p.pop=1;return true;}/* (patch 37) a held item stops the fish */if(tg.air&&!tg.glide){/* hopped")
# Shroom
rep("const ABIL_TIME=30,MEGA_T=5.5,PESTO_T=5.9;", "const ABIL_TIME=30,MEGA_T=4.5,PESTO_T=5.9;")
rep("const FLAT_T=3;function megaCrush", "const FLAT_T=2;function megaCrush")
# Mozz
rep("k.shield=7;k.mzH=3;k.boost=Math.max(k.boost,.7);", "k.shield=7;k.mzH=3;k.boost=Math.max(k.boost,2);")
# Olive: wider slicks (host and a friend's claim), drawn bigger, and a boost as the trail starts
rep("if((k.x-h.x)**2+(k.y-h.y)**2<200&&k.inv<=0&&sameLvl(k,h)){/* only karts on the trap's own level */",
    "if((k.x-h.x)**2+(k.y-h.y)**2<(h.olive?320:200)&&k.inv<=0&&sameLvl(k,h)){/* only karts on the trap's own level */")
rep("if((k.x-px)**2+(k.y-py)**2>=200)continue;", "if((k.x-px)**2+(k.y-py)**2>=(id[0]==='h'&&m.hk==='olive'?320:200))continue;")
rep("const up=kind==='forks'?1.9:kind==='boxes'?1.3:1.2;", "const up=kind==='forks'?1.9:kind==='boxes'?1.3:kind==='olive'?1.5:1.2;")
rep("e.position.y=.22;r.position.y=.26;", "if(kind==='olive'){e.scale.setScalar(1.27);r.scale.setScalar(1.27);}e.position.y=.22;r.position.y=.26;")
rep("k.oliveT=k.abFx=OLIVE_T-(10-SLICKN)*.25;", "k.oliveT=k.abFx=OLIVE_T-(10-SLICKN)*.25;k.boost=Math.max(k.boost,1.2);")
# Pep: faster slices, and the first bounce bends toward a racer ahead
rep("P.storm=1;P.hp=3;P.wb=0;P.t=8;", "P.storm=1;P.hp=3;P.wb=0;P.t=8;P.vx*=1.15;P.vy*=1.15;")
rep("p.vx-=2*dot*nx;p.vy-=2*dot*ny;p.x-=nx*ov;p.y-=ny*ov;p.rl-=sg*ov;",
    "p.vx-=2*dot*nx;p.vy-=2*dot*ny;p.x-=nx*ov;p.y-=ny*ov;p.rl-=sg*ov;if(!p.hm){p.hm=1;pepAim(p);}")
rep("function pepWall(p){",
    "/* (patch 37) a storm slice's first wall bounce turns it, at most .5 rad, toward the nearest racer ahead of it */"
    "function pepAim(p){const sp=Math.hypot(p.vx,p.vy)||1,ux=p.vx/sp,uy=p.vy/sp;let best=null,bd=420*420;"
    "for(const k of karts){if(k===p.owner||k.loop||k.finished)continue;const dx=k.x-p.x,dy=k.y-p.y,d2=dx*dx+dy*dy;if(d2>=bd)continue;const d=Math.sqrt(d2)||1;if((dx*ux+dy*uy)/d<.6)continue;best=k;bd=d2;}"
    "if(!best)return;const cur=Math.atan2(uy,ux),na=cur+clamp(angDiff(Math.atan2(best.y-p.y,best.x-p.x),cur),-.5,.5);p.vx=Math.cos(na)*sp;p.vy=Math.sin(na)*sp;}\nfunction pepWall(p){")
# the descriptions
rep("Each slice ricochets between the track walls and off anything it hits (spinning out racers, smashing items) and vanishes on its third hit.",
    "Each slice ricochets between the track walls and off anything it hits (spinning out racers, smashing items) and vanishes on its third hit. The first bounce bends a slice toward the nearest racer ahead of it.")
rep("Drops ten slicks, and nothing can touch you while you lay them;", "Drops ten wide slicks with a quick boost, and nothing can touch you while you lay them;")
rep("blocks every hit for a while, with a quick burst of speed.", "blocks three hits for a while, with two seconds of extra speed. A Spiky Shockwave only pops it, with no spin.")
rep("They stay squashed and slow for 3 seconds.", "They stay squashed and slow for 2 seconds.")
rep("A huge spiky blast that spins out every racer anywhere near you, even in the air. The only hit in the game that goes through shields, ability boosts, Delivery Rush and the blink after a hit.",
    "A spiky blast that spins out every racer close to you. It goes through ability boosts and Delivery Rush, and pops a shield without a spin. Karts in the air, and anyone still blinking after a hit, are safe.")
rep("They always reach their target, but a well-timed hop dodges one.", "They always reach their target, but a well-timed hop dodges one and an item held behind you stops one.")
rep("/* force: the Spiky Shockwave, the one hit nothing protects against — not an ability boost, not a shield, not the blink after a hit, not Delivery Rush */",
    "/* force: the Spiky Shockwave: through ability boosts and Delivery Rush; a shield is popped instead (patch 37) */")
rep("const NET_PROTO=112;", "const NET_PROTO=113;")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patched')
