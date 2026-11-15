"""Patch 33 (web v198): Settings gets a "Kart stats" tab that says what each stat does to the driving, in plain numbers.
The owner, 2026-11-15, after asking what off-road and weight do: "You should add that into a category on settings so players can
understand the stats better if they want".
Words only: nothing here moves a kart. The numbers are the engine's (statMods, patch32; the off-road share in the kart step; the
bump push and the spin time in the collision and spinOut code). If any of those change, change this page too, and the PC's
copy in godot/scripts/main.gd (_stats_help).
Run once: py.cmd tools/mini/patch33.py"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'data-cat="stats"' not in s, 'already patched'


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:80])
    s = s.replace(a, b)


rep('<button type="button" role="tab" data-tab="guide">Items &amp; specials</button>',
    '<button type="button" role="tab" data-tab="guide">Items &amp; specials</button><button type="button" role="tab" data-tab="stats">Kart stats</button>')
ROWS = [
    ('Speed', 'Top speed. Each bar is about 1.5%: full is 9% faster than the middle, empty 9% slower.'),
    ('Acceleration', 'How fast you get up to top speed, from the start and after a hit or a wall. Each bar is about 6%: full is 36% quicker, empty 36% slower.'),
    ('Handling', 'How sharply the kart turns, in normal steering and in a drift. Each bar is about 3%: full turns 20% sharper, empty 20% wider.'),
    ('Weight', 'Only matters against other karts. In a bump the heavier kart is pushed aside less (full against empty: about a third as far), and a kart over 15% lighter also loses a little speed while they touch. A heavier kart also recovers sooner from an item hit: a spin lasts 0.97 s at full, 1.1 s in the middle, 1.23 s at empty. It does not change speed, turning or jumps.'),
    ('Off-road', 'Only matters with your wheels off the road. Off it every kart is held to a share of its top speed: on grass, sand, dirt or the floor beside a toy track 80% at full, 58% in the middle, 40% at empty; on the kerb 93%, 86%, 79%. On the road, gliding, on a shortcut lane or with a boost it does nothing (a boost always keeps at least 93%).'),
]
rows = ''.join('<div class="set-row"><div class="set-t"><b>%s</b><small>%s</small></div></div>' % r for r in ROWS)
SEC = ('<section class="set-group stats-help" data-cat="stats"><h3 class="label">Kart stats</h3>'
       '<p class="g-note">Every stat has 12 bars; 6 is the middle, a normal kart. The vehicle sets the starting bars, and each +1 or '
       '&minus;1 on the wheels and the glider is exactly one bar more or less: they add up, and the bars stop at 0 and 12. What the garage '
       'shows is exactly how the kart drives. Kart stats can be switched off under Gameplay, so every kart drives the same.</p>'
       + rows + '</section>\n    ')
rep('    <section class="set-group guide" data-cat="guide"><h3 class="label">Items</h3>',
    '    ' + SEC + '<section class="set-group guide" data-cat="guide"><h3 class="label">Items</h3>')
rep('.set-row .seg button{padding:8px 4px;font-size:14px}',
    '.set-row .seg button{padding:8px 4px;font-size:14px}\n.stats-help .set-row{grid-template-columns:1fr}.stats-help .g-note{margin:0 0 6px;font-size:12.5px;line-height:1.45;color:rgba(255,244,220,.72)}')
# Sandbox's speed slider (web v197) stayed on the screen over the pause sheet and Settings: nothing redraws it while the game is stopped,
# so the three places that open or close one of them ask it to look again
rep("function togglePause(){", "function togglePause(){try{setTimeout(()=>{if(typeof sbSpdUi==='function')sbSpdUi();},0);}catch(e){}")
rep("function openSettings(from,tab){setFrom=from;", "function openSettings(from,tab){setTimeout(()=>{if(typeof sbSpdUi==='function')sbSpdUi();},0);setFrom=from;")
rep("function closeSettings(){setOv.hidden=true;", "function closeSettings(){setOv.hidden=true;if(typeof sbSpdUi==='function')sbSpdUi();")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patched')
