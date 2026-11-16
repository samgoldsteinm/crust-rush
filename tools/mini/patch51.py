"""Patch 51 (web v212): a key for Sandbox's Back to the track.
The owner: "add a keybind option for keyboard for the reset to the nearest track spot on sandbox. right now its only accessible from the
settings menu but for keyboard we should make it bindable like the other keys". A new keyboard action 'sbback' (Settings > Controls,
like every other key; T by default, a key nothing else uses): in Sandbox, driving, it pauses and asks the same question as the pause
menu's Back to the track button (sbBackAsk), so a stray press never moves you. The PC has the same action (scripts/keys.gd).
Run once: py.cmd tools/mini/patch51.py"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'patch 51' not in s, 'already patched'


def rep(a, b):
    global s
    assert s.count(a) == 1, (s.count(a), a[:90])
    s = s.replace(a, b)


rep("['look','Look back'],['pause','Pause']];", "['look','Look back'],['pause','Pause'],['sbback','Back to the track (Sandbox)']];/* (patch 51: sbback) */")
rep("look:['KeyF'],pause:['KeyP']};", "look:['KeyF'],pause:['KeyP'],sbback:['KeyT']};")
rep("else if(a==='ability'){if(!e.repeat)abilQueued=true;e.preventDefault();}",
    "else if(a==='ability'){if(!e.repeat)abilQueued=true;e.preventDefault();}"
    "else if(a==='sbback'){if(!e.repeat&&SBX&&state==='race'&&!SB.trav){togglePause();sbBackAsk(true);}e.preventDefault();}/* (patch 51) */")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patch 51 applied')
