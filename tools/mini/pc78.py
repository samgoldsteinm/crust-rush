"""The PC side of web patch 78 (v222): no underglow on bikes; karts' underglow under their frame (the owner: "on karts and bikes it
doesn't look good. Remove the under glow feature for bikes and fix the size of the under glow for the karts").
    py.cmd tools/neon/ugtable.py   (a build with patch 78 served)   then   py.cmd tools/mini/pc78.py   (once, after pc77)
view.gd UG_P from tools/neon/ug_params.json again (the karts' numbers changed; bikes have none); _style_view makes no glow or lights for a
bike; menu.gd: no garage glow and no Underglow row for a bike.
"""
import json, re
G = 'D:/crust-rush/godot/scripts/'
T = json.load(open('D:/crust-rush/source/tools/neon/ug_params.json', encoding='utf-8'))
assert not any(k.startswith('bike_') for k in T) and 'gokart' in T, 'run tools/neon/ugtable.py on a build with patch 78 first'


def rep(f, a, b, n=1):
    p = G + f
    s = open(p, encoding='utf-8', newline='').read()
    assert s.count(a) == n, (f, s.count(a), a[:80])
    s = s.replace(a, b)
    open(p, 'w', encoding='utf-8', newline='').write(s)


p = G + 'view.gd'
s = open(p, encoding='utf-8', newline='').read()
assert '(pc78)' not in s, 'already applied'
m = re.search(r'^const UG_P := \{\n.*?^\}\n', s, re.S | re.M)
assert m and '"gokart"' in m.group(0)
body = ',\n'.join('\t"%s": [%s]' % (k, ', '.join(repr(float(x)) for x in T[k])) for k in sorted(T))
s = s[:m.start()] + '## (pc78) karts under their frame; bikes have no underglow\nconst UG_P := {\n' + body + '\n}\n' + s[m.end():]
open(p, 'w', encoding='utf-8', newline='').write(s)

rep('view.gd', '''	if gi["h"] == null or float(meta.get("hover", 0.0)) > 0.0:
		return
	var col := Color("#ff3030")''', '''	if gi["h"] == null or float(meta.get("hover", 0.0)) > 0.0 or bool(meta.get("bike", false)):   # (pc78: none on a bike)
		return
	var col := Color("#ff3030")''')
rep('menu.gd', '''		if gl["h"] != null:
			# (pc77)''', '''		if gl["h"] != null and not bool((built["meta"] as Dictionary).get("bike", false)):   # (pc78: none on a bike)
			# (pc77)''')
rep('menu.gd', '''		var slot := String(row[0])
		outer.add_child(section_label(String(row[1])))''', '''		var slot := String(row[0])
		if slot == "gl" and bool((KartBuilder.info["bodies"][int(build["b"])] as Dictionary).get("bike", false)):
			continue   # (pc78) a bike has no underglow
		outer.add_child(section_label(String(row[1])))''')
print('pc78 applied')
