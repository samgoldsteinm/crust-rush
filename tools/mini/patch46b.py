"""Patch 46b (web v208): the username sheet never stays over a race or Sandbox.
The first-launch sheet (patch 44) opens on the menu 2.5 s after start-up; a friend's room can start a race or Sandbox for you while it is
open (the host's 'load' or 'sbgo'), and the game then ran behind it (seen in tools/neon/sbnet.py's pictures). Any start of a race or a
place now closes it; it is offered again the next time the game is opened.
Run once: py.cmd tools/mini/patch46b.py"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'patch 46b' not in s, 'already patched'
a = "async function goRace(mi){if(raceLoading)return;"
assert s.count(a) == 1
s = s.replace(a, "async function goRace(mi){if(raceLoading)return;{const ov=document.getElementById('lbNameOv');if(ov&&!ov.hidden)ov.hidden=true;}/* (patch 46b) */")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patch 46b applied')
