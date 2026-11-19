"""PC: Stock wheels with stats (web v244, patch 108): online version 123. The wheel's name and stats come from the export (garage.json).
    py.cmd tools/mini/pc97.py      (once, after pc96; edits webnet.gd)"""
G = 'D:/crust-rush/godot/scripts/'


def rep(f, a, b, n=1):
    p = G + f
    s = open(p, encoding='utf-8', newline='').read()
    assert s.count(a) == n, (f, s.count(a), a[:80])
    s = s.replace(a, b)
    open(p, 'w', encoding='utf-8', newline='').write(s)


rep('webnet.gd', 'const PROTO := 122   # (122:', 'const PROTO := 123   # (123: web v244, Stock wheels have stats; 122:')
print('pc97 applied')
