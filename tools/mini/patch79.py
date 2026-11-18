"""Patch 79 (web v223): a race with a cheat on does not count towards records; the UNLOCK code and looks (colours, field of view, the
HUD) still count. The owner: "make any race using cheat codes not count towards records unless its the unlock cheat code. using
different colored cars shouldnt not make the race count but dev options alter the core function of the game".
RTAINT: false when a race starts (ghostStart); set for good, every frame of the countdown and race (hud), while auto-drive (the TESTING
code) is on or devAlt() finds a developer setting in force that is not its default (race settings from devR(): yours off line, the
host's in a room; this device's from devLocal()); 'on', 'fov' and 'hud' are left out (looks only). A tainted race: no personal best,
no world leaderboard run, no history line; the results say why. A Sandbox mission done with one on (A.cheat) sets no best time.
Coins and achievements are unchanged.
Run once, after patch 78: py.cmd tools/mini/patch79.py"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'patch 79' not in s, 'already patched'


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:90])
    s = s.replace(a, b)


rep("function devLocal(){", "/* (patch 79) a developer setting in force that changes the game (not its looks: field of view, the HUD) */\n"
    "function devAlt(){const ne=(a,b)=>b&&typeof b==='object'?Object.keys(b).some(k=>a&&a[k]!==undefined&&ne(a[k],b[k])):typeof b==='string'?String(a||'')!==b:+a!==+b;\n"
    "  return [devR(),devLocal()].some(D=>D&&Object.keys(DEVDEF).some(k=>k!=='on'&&k!=='fov'&&k!=='hud'&&D[k]!==undefined&&ne(D[k],DEVDEF[k])));}\n"
    "let RTAINT=false;/* (patch 79) this race used auto-drive or a developer setting: it does not count towards records */\n"
    "function devLocal(){")
rep("function ghostStart(){recBuf=[];recT=0;recLaps=[];lastRun=null;", "function ghostStart(){recBuf=[];recT=0;recLaps=[];lastRun=null;RTAINT=false;")
rep("function hud(dt,time){try{tdTick();}catch(e){}",
    "function hud(dt,time){try{tdTick();}catch(e){}try{if(!RTAINT&&player&&(state==='race'||state==='countdown')&&(TD.on||devAlt()))RTAINT=true;}catch(e){}")
rep("function saveRun(){if(!player||!recBuf)return;const t=player.finishTime,key=recKey(),recs=loadRecs(),old=recs[key],pb=!old||t<old.t;",
    "function saveRun(){if(!player||!recBuf)return;const t=player.finishTime,key=recKey(),recs=loadRecs(),old=recs[key];\n"
    "  if(RTAINT){lastRun={t,old:old?old.t:null,pb:false,place:player.place,cheat:true};recBuf=null;return;}/* (patch 79) not counted */const pb=!old||t<old.t;")
rep("function pbLine(){if(!lastRun)return '';",
    "function pbLine(){if(!lastRun)return '';if(lastRun.cheat)return '<span class=\"pbo\">Not counted for records: auto-drive or developer options were on</span>';")
rep("function sbActTick(k,dt){const A=SBA.act;", "function sbActTick(k,dt){const A=SBA.act;try{if(A&&!A.cheat&&(TD.on||devAlt()))A.cheat=1;}catch(e){}/* (patch 79) */")
rep("if(!r.best||sc<r.best){r.best=+sc.toFixed(1);best=r.n>0;}", "if(!A.cheat&&(!r.best||sc<r.best)){r.best=+sc.toFixed(1);best=r.n>0;}/* (patch 79: no best with a cheat on) */")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patch 79 applied')
