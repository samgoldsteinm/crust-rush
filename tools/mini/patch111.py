"""Patch 111 (web v246): Last Slice Standing on a clock; the eliminated leave the race tracker.
The owner: "when a player is eliminated they are sent to the end of the race and so everyone ends up getting moved back a place ... The
game is showing their logo at the end of the race on the race tracker ... instead of making it one person eliminated every lap make it
1 person every 30 seconds".
- Every LSS_EVERY (30) s of race time the kart in last place is out; when two are left the one still in wins on that elimination.
  The next one is due at (number out + 1) x 30 s, so a guest (who only hears 'elim') counts down to the same moment.
- No lap total in LSS (LAPS 99, a safety net only): the HUD shows the lap number alone and "Next out 17s" in place of the lap time,
  red for the last 5 s. Lap bars hidden.
- Race tracker in LSS: each logo sits where its kart is on its current lap; the eliminated are hidden (they were drawn
  at the finish, which looked like they had jumped ahead).
- Results: "out at 1:30" in place of "out on lap N". Mode note rewritten.
- NET_PROTO 124: the rules changed, an older host would still go by laps.
- PC: tools/mini/pc99.py.
Run once, after patch 110: tools/py.cmd tools/mini/patch111.py"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'patch 111' not in s, 'already patched'


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:90])
    s = s.replace(a, b)


# race start: no lap total; tracker logos shown again; lap bars hidden in LSS
rep("LAPS=mode==='lss'?Math.max(2,karts.length-1):(MAPS[mapIdx].laps||3);lssLap=0;for(const k of karts){k.elim=false;k.elimLap=0;",
    "LAPS=mode==='lss'?99:(MAPS[mapIdx].laps||3);/* (patch 111: LSS goes by the clock, 99 is only a safety net) */lssLap=0;"
    "{const lb=$('lapBars');if(lb)lb.style.display=mode==='lss'?'none':'';}"
    "for(const k of karts){k.elim=false;k.elimLap=0;if(k.pm){k.pm._h=false;k.pm.style.visibility='';}")

# the rule
rep("/* ---- Last Slice Standing: every time the leader completes a lap, the kart in last place is out; the leader's final lap crowns the winner and",
    "/* ---- Last Slice Standing (patch 111): every 30 s the kart in last place is out; when two are left, the one still in wins. (Before: one per lap.)")
rep("let lssLap=0;", "let lssLap=0;const LSS_EVERY=30;function lssNext(){let n=0;for(const k of karts)if(k.elim)n++;return (n+1)*LSS_EVERY;}")
rep("  const lap=Math.floor(lead.prog/N);if(lap>lssLap&&lap<LAPS){lssLap=lap;const last=act.slice().sort((a,b)=>a.prog-b.prog)[0];lssElim(last,act.length,true);}}",
    "  if(raceTime>=lssNext()){lssLap++;const last=act.slice().sort((a,b)=>a.prog-b.prog)[0];lssElim(last,act.length,true);"
    "if(act.length===2){const w=act[0]===last?act[1]:act[0];w.finished=true;w.finishTime=raceTime;w.place=1;if(NET.role==='host')netAll({t:'elim',idx:w.idx,place:1,win:1});lssWin(w);}}}")

# HUD: tracker, lap, countdown
rep("if(hud.pf%3===0)for(const k of karts){if(!k.pm)continue;const f=Math.max(0,Math.min(1,(k.finished?LAPS*N:k.prog)/(LAPS*N)));",
    "if(hud.pf%3===0){const lss=mode==='lss';for(const k of karts){if(!k.pm)continue;"
    "const hid=!!k.elim;if(k.pm._h!==hid){k.pm._h=hid;k.pm.style.visibility=hid?'hidden':'';}if(hid)continue;"
    "const f=lss?(((k.prog%N)+N)%N)/N:Math.max(0,Math.min(1,(k.finished?LAPS*N:k.prog)/(LAPS*N)));")
rep("if(k.pm._v!==v){k.pm._v=v;k.pm.style.transform='translateX('+v+'px)';}}\n",
    "if(k.pm._v!==v){k.pm._v=v;k.pm.style.transform='translateX('+v+'px)';}}}\n")
rep("const ls=lap+'/'+LAPS;", "const ls=mode==='lss'?String(lap):lap+'/'+LAPS;")
rep("const ts=fmt(player.finished?player.finishTime:raceTime);",
    "let ts;if(mode==='lss'&&!player.finished&&!BATTLE){const left=Math.max(0,Math.ceil(lssNext()-raceTime));ts='Next out '+left+'s';"
    "const red=state==='race'&&left<=5;if(hudTime._r!==red){hudTime._r=red;hudTime.style.color=red?'#ff5a4a':'';}}"
    "else{ts=fmt(player.finished?player.finishTime:raceTime);if(hudTime._r){hudTime._r=false;hudTime.style.color='';}}")

# tracker: no lap marks in LSS
rep("el.querySelectorAll('i,.tb-lap').forEach(n=>n.remove());for(let l=1;l<LAPS;l++){",
    "el.querySelectorAll('i,.tb-lap').forEach(n=>n.remove());for(let l=1;l<(mode==='lss'?0:LAPS);l++){")

# results and the mode note
rep("mode==='lss'?(k.elim?'out on lap '+k.elimLap:",
    "mode==='lss'?(k.elim?'out at '+Math.floor(k.finishTime/60)+':'+String(Math.floor(k.finishTime%60)).padStart(2,'0'):")
rep("mn.textContent='Last Slice Standing: each time the leader completes a lap, the racer in last place is out. Seven laps, one slice left.';",
    "mn.textContent='Last Slice Standing: every 30 seconds, the racer in last place is out. Keep racing until one slice is left.';")

rep("const NET_PROTO=123;", "const NET_PROTO=124;/* (124: web v246, Last Slice Standing on a 30 s clock) */")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patch 111 applied')
