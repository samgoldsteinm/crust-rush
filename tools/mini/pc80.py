"""The PC side of web patch 80 (v223): gold, silver and bronze trims brighter and shinier, the same numbers as the web's TRIMS.
    py.cmd tools/mini/pc80.py      (once, after pc79; edits D:/crust-rush/godot/scripts/style.gd)
The 14 new solid paints reach the PC through the export (glbexport.js copies PAINTS / PAINT_NAMES into garage.json). The garage
reflections fix is web only: the PC garage already reflects its own studio (studio_neutral.gdshader).
"""
G = 'D:/crust-rush/godot/scripts/'


def rep(f, a, b, n=1):
    p = G + f
    s = open(p, encoding='utf-8', newline='').read()
    assert s.count(a) == n, (f, s.count(a), a[:80])
    s = s.replace(a, b)
    open(p, 'w', encoding='utf-8', newline='').write(s)


rep('style.gd', '{"n": "Silver", "h": "#b8bcc4", "p": 0, "m": 1}', '{"n": "Silver", "h": "#c9ccd2", "p": 0, "m": 1, "r": 0.16}')
rep('style.gd', '{"n": "Bronze", "h": "#8a6232", "p": 250, "m": 1}, {"n": "Gold", "h": "#d4a838", "p": 400, "m": 1}',
    '{"n": "Bronze", "h": "#b5763f", "p": 250, "m": 1, "r": 0.26}, {"n": "Gold", "h": "#e3b448", "p": 400, "m": 1, "r": 0.18}')
print('pc80 applied')
