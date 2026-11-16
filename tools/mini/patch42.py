"""Patch 42 (web v205; Sandbox only): a hollow on a pizza that could not be driven out of.
The owner, 2026-11-16, with a picture on Oven Rush Raceway: "I also just fell into this little dip and couldn't drive out an invisible border
was blocking me from getting out". sbBlocked counted a drawn thing (Sandbox's collision is read from what is drawn) as in the way when its
top stood more than a step (SB_STEP 5.5) above the KART. On a slope the cheese and pepperoni discs lying on the ground ahead stand that high
above the kart only because the hill rises; a hollow ringed with them was a cage. Now on a pizza (kind 'open', not in a passage) a drawn
thing counts from the higher of the kart and the ground under that point. Real walls stand far above both. The PC: sandbox.gd blocked().
Measured (scratch/dip_find.js: 200 random spots off the road on Oven Rush, can a kart drive out in any of six directions in 1.7 s): one
trapped before, none after. Made in crust-rush.html by hand; this applies it if it is missing.
Run: py.cmd tools/mini/patch42.py"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
if '(patch 42)' in s:
    print('patch 42 already in')
else:
    a = "for(let i=0;i<n;i++)if(S[i][0]>wy+SB_STEP&&S[i][1]<wy+SB_HEAD)return true;return false;}"
    assert s.count(a) == 1
    s = s.replace(a, "/* (patch 42) on a pizza a drawn thing counts by how far it stands above the ground it lies on */const base=SB.kind==='open'&&!SB.inG?Math.max(wy,groundAt(x,z)):wy;"
                     "for(let i=0;i<n;i++)if(S[i][0]>base+SB_STEP&&S[i][1]<wy+SB_HEAD)return true;return false;}")
    open(p, 'w', encoding='utf-8', newline='').write(s)
    print('patch 42 applied')
