"""Patch 69 (web v220): a key to restart the race, confirmed by pressing it again.
The owner: "add a keybind for restarting the race on keyboard you tap it once to bring up a menu confirming you want to restart and then
you hit the button the player has binded and it will confirm the restart of the race. this way the player can quickly tap the button
twice and restart."
KB action 'restart' (Settings > Controls, default Backspace). In a race off line (not in a room, not Sandbox, not a battle): the first
press pauses and shows #rstOv ("Restart the race?"); the same key again, or its Restart button, restarts (the pause menu's Restart:
startRace); Esc or Keep racing closes it and the race goes on. The PC the same (keys.gd 'restart', main.gd).
Run once: py.cmd tools/mini/patch69.py"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'patch 69' not in s, 'already patched'


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:90])
    s = s.replace(a, b)


rep("['flydown','Fly down (developer)']];", "['flydown','Fly down (developer)'],['restart','Restart the race (press twice)']];")
rep("fly:['KeyG'],flyup:['KeyI','PageUp'],flydown:['KeyK','PageDown']};", "fly:['KeyG'],flyup:['KeyI','PageUp'],flydown:['KeyK','PageDown'],restart:['Backspace']};")
rep("else if(a==='fly'){if(!e.repeat)devFlyToggle();e.preventDefault();}",
    "else if(a==='fly'){if(!e.repeat)devFlyToggle();e.preventDefault();}else if(a==='restart'){if(!e.repeat)rstKey();e.preventDefault();}")
rep('<div id="pauseOv" class="overlay" hidden>',
    '<div id="rstOv" class="overlay" hidden>\n  <div class="panel rst-panel"><h2 class="res-title">Restart the race?</h2><p id="rstTxt" class="rst-txt"></p>\n'
    '    <div class="row"><button id="rstGo" class="cta" type="button">Restart</button><button id="rstNo" class="ghost" type="button">Keep racing</button></div></div>\n</div>\n\n'
    '<div id="pauseOv" class="overlay" hidden>')
rep("$('restartBtn').onclick=()=>{if(gp)gp.pts.forEach((v,i)=>gp.pts[i]=v);startRace();};",
    "$('restartBtn').onclick=()=>{if(gp)gp.pts.forEach((v,i)=>gp.pts[i]=v);startRace();};\n"
    "/* (patch 69) the restart key: once asks (and pauses), again restarts; off line races only */\n"
    "function rstOk(){return (state==='race'||state==='countdown'||state==='paused')&&!NET.cfg&&!NET.role&&!SBX&&!BATTLE;}\n"
    "function rstKey(){const o=$('rstOv');if(!o)return;if(!o.hidden){rstGo();return;}if(!rstOk())return;if(state==='race'||state==='countdown')togglePause();$('pauseOv').hidden=true;/* (the question alone, not the pause menu under it) */"
    "$('rstTxt').textContent='Press '+kbList('restart')+' again to start over, or Esc to keep racing.';o.hidden=false;try{$('rstGo').focus();}catch(e){}}\n"
    "function rstGo(){$('rstOv').hidden=true;$('pauseOv').hidden=true;$('restartBtn').onclick();}\n"
    "function rstNo(){$('rstOv').hidden=true;if(state==='paused')togglePause();}\n"
    "$('rstGo').onclick=rstGo;$('rstNo').onclick=rstNo;")
rep("addEventListener('keydown',e=>{if(e.code!=='Escape')return;if(!setOv.hidden)closeSettings();",
    "addEventListener('keydown',e=>{if(e.code!=='Escape')return;if(!$('rstOv').hidden){rstNo();return;}/* (patch 69) */if(!setOv.hidden)closeSettings();")
# the key must work while the confirm box is up (keydown ignores events inside an overlay: the box's buttons hold the focus)
rep("addEventListener('keydown',e=>{if(e.target.closest&&e.target.closest('.overlay'))return;const a=KEYC[e.code];",
    "addEventListener('keydown',e=>{if(KEYC[e.code]==='restart'&&!$('rstOv').hidden&&!e.repeat){e.preventDefault();rstGo();return;}if(e.target.closest&&e.target.closest('.overlay'))return;const a=KEYC[e.code];")
rep(".cheat-msg{margin:4px 0 0;font-size:13px;min-height:1.2em}", ".cheat-msg{margin:4px 0 0;font-size:13px;min-height:1.2em}\n#rstOv{z-index:60}.rst-txt{margin:6px 0 14px;color:var(--muted)}")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patch 69 applied')
