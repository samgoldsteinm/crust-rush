"""Patch 31 (web v197): Balloon Battle with lives and elimination: the engine's side of it (the rules are in tools/mini/battle.js).
The owner, 2026-11-14: "you start with 5 then after those are popped you have 3 then after the 3 are popped you get 1 after that is
popped you are eliminated".
An eliminated player watches the rest with the engine's spectating (made for Last Slice Standing and online races); these are the places
where that code asked "is this Last Slice Standing?":
  standings()      in a battle the order is bbRank (drivers still in by points, then the eliminated, the last one out highest)
  specTargets      a driver still in a battle can be watched
  specCanWatch     ...and so the results sheet offers Watch while a battle is still on
  specExit         the bar's Results button in a battle is "Skip to results": bbSkip plays the rest of the round out at once
  specEnter, specCam   no "Track cameras" in a battle (they stand round a lap; the arena has none): chase and blimp only
  specLabel        under the watched driver's name: balloons and points (bbSpecInfo), not a lap
  the results row  bbResRow: the points, and "out" for the eliminated
  the menu's note  the new rules
Everything is behind BATTLE&&!SBX (Sandbox's free driving switches BATTLE on for its ground and walls; it has no round).
Run once: py.cmd tools/mini/patch31.py"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'bbResRow(k)' not in s.split('/*MINI-END*/')[1], 'already patched'


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:80])
    s = s.replace(a, b)


rep("function standings(){return", "function standings(){if(BATTLE&&!SBX)return bbRank();/* (a battle has no lap to be ahead on: tools/mini/patch31.py) */return")
rep("const live=k=>!k.finished&&(!!k.netName||mode==='lss');", "const live=k=>!k.finished&&(!!k.netName||mode==='lss'||(BATTLE&&!SBX));")
rep("function specCanWatch(){return !!((NET.cfg||mode==='lss')&&state==='race'", "function specCanWatch(){return !!((NET.cfg||mode==='lss'||(BATTLE&&!SBX))&&state==='race'")
rep("function specExit(toResults=true){if(!SPEC.on)return;", "function specExit(toResults=true){if(!SPEC.on)return;if(toResults&&BATTLE&&!SBX&&bbSkip())return;/* a battle still on: the rest of it is played out at once, then the results come by themselves */")
rep("SPEC.on=true;SPEC.i=0;SPEC.mode=SPEC.mode||0;", "SPEC.on=true;SPEC.i=0;SPEC.mode=SPEC.mode||0;if(BATTLE&&!SBX&&SPEC.mode===1)SPEC.mode=0;")
rep("function specCam(){if(!SPEC.on)return;SPEC.mode=(SPEC.mode+1)%SPEC_MODES.length;", "function specCam(){if(!SPEC.on)return;SPEC.mode=(SPEC.mode+1)%SPEC_MODES.length;if(BATTLE&&!SBX&&SPEC.mode===1)SPEC.mode=2;")
rep("$('specInfo').textContent=pl+suf(pl)+' place · '+(k.finished?", "$('specInfo').textContent=BATTLE&&!SBX?bbSpecInfo(k):pl+suf(pl)+' place · '+(k.finished?")
rep("BATTLE?(k.bbS||0)+((k.bbS||0)===1?' point':' points'):", "BATTLE?bbResRow(k):")
rep("Balloon Battle: three minutes on the prep table. Everybody starts with three balloons. Pop a rival\\'s balloon with a pepperoni for a point; lose all of yours and you come back with three and half your points. Most points wins.",
    "Balloon Battle: everybody starts with five balloons. Pop a rival\\'s balloon with a pepperoni for a point. Lose all five and you come back with three, then with one; lose that one and you are out. The last driver left wins.")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patched')
