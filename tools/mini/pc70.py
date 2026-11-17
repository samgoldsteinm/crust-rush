"""The PC side of web patch 70 (v221): the UNLOCK code opens the whole style shop, for this session, spending nothing.
    py.cmd tools/mini/pc70.py      (once; edits D:/crust-rush/godot/scripts)
- style.gd is_owned(): true for everything while Ach.cheat is on (so buy() charges nothing and records nothing in user://own.json).
- main.gd _load_settings: a style in the saved build that is paid and not really owned goes back to 0 (the code lasts one session).
"""
G = 'D:/crust-rush/godot/scripts/'


def rep(f, a, b, n=1):
    p = G + f
    s = open(p, encoding='utf-8', newline='').read()
    assert s.count(a) == n, (f, s.count(a), a[:80])
    s = s.replace(a, b)
    open(p, 'w', encoding='utf-8', newline='').write(s)


rep('style.gd', """static func is_owned(slot: String, i: int) -> bool:
	var L: Array = SLOTS[slot][1]
""", """static func is_owned(slot: String, i: int) -> bool:
	if Ach.cheat:
		return true   # (web patch 70: the UNLOCK code; nothing is bought or written down)
	var L: Array = SLOTS[slot][1]
""")
rep('main.gd', """	var bb = cf.get_value("menu", "build", {})
	if bb is Dictionary:
		sel["build"] = bb
""", """	var bb = cf.get_value("menu", "build", {})
	if bb is Dictionary:
		# (web patch 70) the UNLOCK code lasts one session: a style picked only under it goes back to the free default
		var stv = bb.get("st")
		if stv is Dictionary and not Ach.cheat:
			var S := preload("res://scripts/style.gd")
			for sl in (stv as Dictionary).keys():
				if S.SLOTS.has(sl) and not S.is_owned(String(sl), int(stv[sl])):
					stv[sl] = 0
		sel["build"] = bb
""")
rep('main.gd', 'cheat_msg = "Unlocked! Every achievement, livery, car, track and reward item is open until you close the game. Your real progress is untouched."',
    'cheat_msg = "Unlocked! Every achievement, livery, car, track, reward item and everything in the style shop is open until you close the game. No coins are spent and your real progress is untouched."')
print('pc70 applied')
