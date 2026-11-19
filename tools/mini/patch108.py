"""Patch 108 (web v244): the Standard wheels are called Stock, and they have a stat effect of their own.
The owner: "for standard wheels instead of standard call them stock and give the stock wheels a some kind of stat change effect as well".
- WHEELS[0] (id 'standard' kept: builds, the PC and every saved kart refer to it): name 'Stock', st [-1,0,0,0,1] (spd, acc, hnd, wgt,
  off: like every other wheel type, the changes add up to 0): all-season factory tyres, at home on rough ground, a touch slower flat out.
  The only other off-road wheels are Monster (+2) and Hover (+1).
- The help line no longer calls Classic on Standard wheels "the neutral build".
- NET_PROTO 123 (a wheel's stats changed; PC pc97).
Run once, after patch 107: tools/py.cmd tools/mini/patch108.py"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'patch 108' not in s, 'already patched'


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:90])
    s = s.replace(a, b)


rep("{id:'standard',name:'Standard',desc:'Neutral all-round tires.',st:[0,0,0,0,0],r:1,wz:1},",
    "{id:'standard',name:'Stock',desc:'All-season factory tires: sure-footed on rough ground, a touch slower flat out.',st:[-1,0,0,0,1],r:1,wz:1},/* (patch 108) */")
rep("Each part trades strengths for drawbacks, and Classic with Standard wheels is the neutral build.", "Each part trades strengths for drawbacks.")
rep("const NET_PROTO=122;", "const NET_PROTO=123;/* (123: web v244, Stock wheels have stats) */")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patch 108 applied')
