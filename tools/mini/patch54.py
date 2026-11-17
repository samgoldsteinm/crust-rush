"""Patch 54 (web v214): the headlights come on only when it is properly dark, and a key switches them by hand.
The owner: "make the headlights only turn on when it reaches a certain level of darkness in sandbox. for pc add a keybind for turning it on
or off manually as well". By themselves the headlights now come on between L .5 and .8 of the clock's lamp level (late dusk), not from
the first dimming; the on-track rule (patch 49) still applies. Keyboard action 'lights' "Headlights (Sandbox)", L by default (Settings >
Controls): pressing it switches them on or off by hand (SB.hl true / false; on by hand they also stay on along a lit track); the choice
holds until the game is closed. The PC has the same (scripts/keys.gd "lights").
Run once: py.cmd tools/mini/patch54.py"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'patch 54' not in s, 'already patched'


def rep(a, b):
    global s
    assert s.count(a) == 1, (s.count(a), a[:90])
    s = s.replace(a, b)


rep("sp.intensity=on?24*L*Nn.hf:0;sp.visible=true;",
    "{const hon=SB.hl==null?Math.min(1,Math.max(0,(L-.5)/.3)):(SB.hl?1:0),hf=SB.hl===true?1:Nn.hf;sp.intensity=24*Math.max(L,.45)*hon*hf;}sp.visible=true;/* (patch 54: dark enough, or by hand) */")
rep("['sbback','Back to the track (Sandbox)']];", "['sbback','Back to the track (Sandbox)'],['lights','Headlights (Sandbox)']];")
rep("sbback:['KeyT']};", "sbback:['KeyT'],lights:['KeyL']};")
rep("else if(a==='sbback'){",
    "else if(a==='lights'){if(!e.repeat&&SBX){const now=SB.hl==null?(sbClockF().L>.65):SB.hl;SB.hl=!now;showBanner(SB.hl?'Headlights on':'Headlights off',1.1,'sm');}e.preventDefault();}/* (patch 54) */else if(a==='sbback'){")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patch 54 applied')
