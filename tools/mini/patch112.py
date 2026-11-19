"""Patch 112 (web v246): the finish's driver close-up looks down into the cockpit from a front three-quarter.
The owner: "make sure in the cinematic camera shot you can see the drivers face from the side angle. Currently the angle sits too low next
to the car and you can't see the characters face". The camera sat 1.2-2.4 above the head and swung round to 0.54 pi (past side-on), so on
cars the door and sill hid the driver (scratch/paint/fin_3.png).
- Swing from 0.14 pi to 0.36 pi off the nose (it ends facing the driver's face from the front quarter, never behind the shoulder).
- Height: about half the radius above the head (looking down ~25 deg into the cockpit), never under 3 above it.
- PC: tools/mini/pc100.py.
Run once, after patch 111: python tools/mini/patch112.py"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'patch 112' not in s, 'already patched'


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:90])
    s = s.replace(a, b)


rep("a=h+FIN.side*(.2+.34*ez(u))*Math.PI,R=(13-2.5*u)*(BODIES[playerBuild.b]&&BODIES[playerBuild.b].sf||1);/* from ahead of the driver round to the side */",
    "a=h+FIN.side*(.14+.22*ez(u))*Math.PI,R=(14-2*u)*(BODIES[playerBuild.b]&&BODIES[playerBuild.b].sf||1),up=Math.max(3,R*.58);"
    "/* (patch 112) from ahead of the driver round to the front quarter, looking down into the cockpit so the face shows over the door */")
rep("camera.position.set(hd.x+Math.cos(a)*R,Math.max(hd.y+2.4-1.2*u,groundAt(",
    "camera.position.set(hd.x+Math.cos(a)*R,Math.max(hd.y+up,groundAt(")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patch 112 applied')
