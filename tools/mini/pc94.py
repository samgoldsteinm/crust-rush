"""PC: web patch 102 (v235): a held part (the Street Cruiser's fender halves, calipers) never takes the Rims colour.
    py.cmd tools/mini/pc94.py      (once, after pc93; edits kart_builder.gd)"""
p = 'D:/crust-rush/godot/scripts/kart_builder.gd'
s = open(p, encoding='utf-8', newline='').read()
a = '\tc["rimre"] = re\n'
assert s.count(a) == 1
s = s.replace(a, '\tc["rimre"] = re\n\tc["rimc"] = null   # (pc94: held paint keeps the paint, not the rims colour)\n')
open(p, 'w', encoding='utf-8', newline='').write(s)
print('pc94 applied')
