"""Patch 56 (web v214): in Balloon Battle a controller's item button throws at once.
The owner (a picture: a pepperoni lying behind the kart): "when playing balloon battle as the guest throwing items is slow and also a copy of
the item gets dropped behind you on the ground. remove the item that gets dropped on the ground and make the item throw less delayed".
On a controller a holdable item (pepperoni, dough, flour) was taken in hand on the press, trailing behind the kart, and thrown only on
letting go: that trailing item was the "copy on the ground", and the wait for the release (plus, for a friend, a trip to the host and
back) the delay. In a battle the press now throws it (as a key does); races keep holding behind as a shield. The PC the same (main.gd).
Run once: py.cmd tools/mini/patch56.py"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'patch 56' not in s, 'already patched'
a = "else if(it&&HOLDABLE[it]){itemQueued='hold'+suf;PAD.hold[sl]=1;}"
assert s.count(a) == 1
s = s.replace(a, "else if(it&&HOLDABLE[it]&&mode!=='bb'){itemQueued='hold'+suf;PAD.hold[sl]=1;}/* (patch 56: a battle throws on the press) */")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patch 56 applied')
