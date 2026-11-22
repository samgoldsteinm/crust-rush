"""PC: no fog. The owner, on pc117's volumetric fog: "Let's remove the fog it doesn't look good". The setting is gone and the
fog is always off (HdLook.fog stays, unused, called with off so an Environment never keeps it on).
    python tools/mini/pc119.py      (once, after pc118)"""
p = 'D:/crust-rush/godot/scripts/main.gd'
s = open(p, encoding='utf-8', newline='').read()
assert 'pc119' not in s


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:80])
    s = s.replace(a, b)


rep("""				["Fog and light rays", "Real air: a light haze in each track's colour that the sun and the headlights shine through, with rays where trees and buildings break the light. Ultra only.", "fog", on_off, "1" if fog_on else "0"],
""", "")
rep("""var fog_on := true          # (pc117) Settings > Fog and light rays (Ultra)
""", """var fog_on := false         # (pc117; pc119: removed, the owner: "it doesn't look good") always off
""")
rep("""		HdLook.fog(env, T, fog_on and ultra)
""", """		HdLook.fog(env, T, false)   # (pc119) no fog
""")
rep('"light_mode", "fog_on", "ssr_on"', '"light_mode", "ssr_on"', 2)
open(p, 'w', encoding='utf-8', newline='').write(s)
print('pc119 applied')
