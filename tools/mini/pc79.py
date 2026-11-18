"""The PC side of web patch 79 (v223): a race with a cheat on does not count towards records (UNLOCK and looks still count).
    py.cmd tools/mini/pc79.py      (once, after pc78; edits D:/crust-rush/godot/scripts)
main.gd race_taint: false at a race's (re)start; set for good in _physics_process while the countdown or race runs with auto-drive
(TESTING, test_drive) on or _dev_alt() (race.dev: yours off line, the host's in a room; dev_here(): this device; 'on', 'fov', 'hud'
left out). A tainted finish: no Ach.record (best, recent races), no world leaderboard run; the results say why; coins and achievements
as before. A Sandbox mission done with one on (act.cheat) sets no best time (sandbox_acts.gd finish).
"""
G = 'D:/crust-rush/godot/scripts/'


def rep(f, a, b, n=1):
    p = G + f
    s = open(p, encoding='utf-8', newline='').read()
    assert s.count(a) == n, (f, s.count(a), a[:80])
    s = s.replace(a, b)
    open(p, 'w', encoding='utf-8', newline='').write(s)


rep('main.gd', '''var race_pay := 0       # coins paid for this race (web patch 65 racePay)
''', '''var race_pay := 0       # coins paid for this race (web patch 65 racePay)
var race_taint := false   # (pc79, web RTAINT) this race used auto-drive or a developer setting: it does not count towards records


## (pc79, web devAlt) a developer setting in force that changes the game (not its looks: field of view, the HUD)
func _dev_alt() -> bool:
	for D in [race.dev if race != null else {}, dev_here()]:
		for k in DEV_DEF:
			if k in ["on", "fov", "hud"] or not (D as Dictionary).has(k):
				continue
			if _dev_ne(D[k], DEV_DEF[k]):
				return true
	return false


func _dev_ne(a, b) -> bool:
	if b is Dictionary:
		for k in b:
			if a is Dictionary and (a as Dictionary).has(k) and _dev_ne(a[k], b[k]):
				return true
		return false
	if b is String:
		return String(a if a != null else "") != b
	return absf(float(a) - float(b)) > 1e-6
''')
rep('main.gd', '''	was_last = false
	last_run = {}
	found_sc = {}''', '''	was_last = false
	last_run = {}
	race_taint = false
	found_sc = {}''')
rep('main.gd', '''	if state == "menu":
		return
	bb_dt = dt''', '''	if state == "menu":
		return
	if (state == "race" or state == "countdown") and (test_drive or _dev_alt()):   # (pc79)
		race_taint = true
		var SA = preload("res://scripts/sandbox_acts.gd")
		if not SA.act.is_empty():
			SA.act["cheat"] = true
	bb_dt = dt''')
rep('main.gd', '''	last_run = Ach.record(map_id, cls, kart.finish_time, kart.place, kart.ri, _my_build(), run)
	# the world leaderboard (scripts/lb.gd): every race counts, on line or off; alone = no other kart on the grid; no items = race.noitm
	if lb != null and not test_drive and race.mode == "":''', '''	if race_taint:
		last_run = {"cheat": true}   # (pc79) not counted: no best, no recent race, no leaderboard run
	else:
		last_run = Ach.record(map_id, cls, kart.finish_time, kart.place, kart.ri, _my_build(), run)
	# the world leaderboard (scripts/lb.gd): every race counts, on line or off; alone = no other kart on the grid; no items = race.noitm
	if lb != null and not test_drive and not race_taint and race.mode == "":''')
rep('main.gd', '''		var pbt := ""
		if bool(lr["pb"]):''', '''		var pbt := ""
		if lr.has("cheat"):
			pbt = "Not counted for records: auto-drive or developer options were on"   # (pc79)
		elif bool(lr["pb"]):''')
rep('main.gd', '''		v.add_child(menu.label(pbt, menu.f_bold, 15.0, Color("#7fe07a") if bool(lr["pb"]) else Color("#c2a58c")))''',
    '''		v.add_child(menu.label(pbt, menu.f_bold, 15.0, Color("#7fe07a") if bool(lr.get("pb", false)) else Color("#c2a58c")))''')
rep('sandbox_acts.gd', '''		if not r.has("best") or sc < float(r["best"]):''', '''		if not bool(A.get("cheat", false)) and (not r.has("best") or sc < float(r["best"])):   # (pc79: no best with a cheat on)''')
print('pc79 applied')
