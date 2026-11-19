"""PC: web patch 96 (v231): records from before the speed change are "Old rules".
    py.cmd tools/mini/pc91.py      (once, after pc90; edits ach.gd, main.gd, menu.gd, lb.gd)
The PC's change (godot 4ddd3cd) was 2026-11-17 06:08:16 UTC = 1794895696 (its records' d is in seconds); the web's 05:54:34 UTC.
An old-rules best still shows, tagged; a run under today's rules becomes the best even when slower (the old one kept as prev).
"""
G = 'D:/crust-rush/godot/scripts/'


def rep(f, a, b, n=1):
    p = G + f
    s = open(p, encoding='utf-8', newline='').read()
    assert s.count(a) == n, (f, s.count(a), a[:80])
    s = s.replace(a, b)
    open(p, 'w', encoding='utf-8', newline='').write(s)


rep('ach.gd', '''	var old: Dictionary = recs.get(key, {})
	var pb := old.is_empty() or t < float(old.get("t", 1e9))
	if pb:
		recs[key] = {"t": t, "d": int(Time.get_unix_time_from_system()), "place": place, "dr": ri, "spec": spec}''',
    '''	var old0: Dictionary = recs.get(key, {})
	# (pc91, web patch 96) a best from before the speed change is not the bar to beat: it is kept as prev
	var old: Dictionary = {} if old_rules(old0) else old0
	var prev = {"t": old0["t"], "d": old0.get("d", 0), "dr": old0.get("dr", 0)} if old_rules(old0) else old0.get("prev")
	var pb := old.is_empty() or t < float(old.get("t", 1e9))
	if pb:
		recs[key] = {"t": t, "d": int(Time.get_unix_time_from_system()), "place": place, "dr": ri, "spec": spec}
		if prev != null:
			recs[key]["prev"] = prev''')
rep('ach.gd', '''static func best(map_id: String, cls: String) -> Dictionary:''',
    '''## (pc91, web patch 96 RULES_T_PC) the speed rules changed (web v216 / this PC build): a record set before is "old rules"
const RULES_T := 1794895696
static func old_rules(r: Dictionary) -> bool:
	return not r.is_empty() and int(r.get("d", 0)) < RULES_T


static func best(map_id: String, cls: String) -> Dictionary:''')
rep('main.gd', '''	hud.pb_text = ("Best " + Hud._fmt(float(best["t"]))) if not best.is_empty() else ""''',
    '''	hud.pb_text = (("Old-rules best " if Ach.old_rules(best) else "Best ") + Hud._fmt(float(best["t"]))) if not best.is_empty() else ""   # (pc91)''')
rep('menu.gd', '''		tv.add_child(label((_racer_name(int(r["dr"])) + " · " + fmt_date(int(r["d"]))) if not r.is_empty() else "No time yet", f_med, 12.0, MUTED))''',
    '''		var sub := (_racer_name(int(r["dr"])) + " · " + fmt_date(int(r["d"]))) if not r.is_empty() else "No time yet"
		if Ach.old_rules(r):
			sub += " · OLD RULES"   # (pc91, web patch 96)
		elif not r.is_empty() and r.get("prev") is Dictionary:
			sub += " · old rules " + fmt_time(float(r["prev"]["t"]))
		tv.add_child(label(sub, f_med, 12.0, MUTED))''')
rep('lb.gd', '''best_runs?select=name,driver,kart,platform,time_ms&map=''', '''best_runs?select=name,driver,kart,platform,time_ms,created_at&map=''')
rep('lb.gd', '''			nv.add_child(M.label("%s · %s" % [String(rd.get("driver", "")), String(rd.get("kart", ""))], M.f_med, 12.0, Color("#c2a58c")))''',
    '''			nv.add_child(M.label("%s · %s%s" % [String(rd.get("driver", "")), String(rd.get("kart", "")), "  ·  OLD RULES" if _old(rd) else ""], M.f_med, 12.0, Color("#c2a58c")))''')
rep('lb.gd', '''func board_panel() -> Control:''',
    '''## (pc91, web patch 96 lbOld) a world-board run from before the speed change (web 05:54:34 UTC, PC 06:08:16 UTC on 17 Nov)
func _old(rd: Dictionary) -> bool:
	var s := String(rd.get("created_at", ""))
	if s.length() < 19:
		return false
	var t := Time.get_unix_time_from_datetime_string(s.substr(0, 19))
	return t < (1794895696 if String(rd.get("platform", "")) == "pc" else 1794894874)


func board_panel() -> Control:''')
print('pc91 applied')
