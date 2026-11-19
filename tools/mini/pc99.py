"""PC: Last Slice Standing on a 30 s clock, and the eliminated rank last (web v246, patch 111): online version 124.
- race.gd _ahead: an eliminated kart counted as finished and sorted ahead of everyone still racing, so each one out moved every
  driver back a place (web standings() sorts them last). Now: finished winners first, then the racing, then the eliminated.
- race.gd _lss_tick: every 30 s of race time the last kart is out; at two left, the other one wins on that elimination.
- main.gd: LAPS 99 in LSS (a safety net); "out at 1:30" in results; "lap N" (no total) for a kart still racing.
- hud.gd: lap number alone, no lap bars or lap marks, "Next out 17s" (red for the last 5 s) in place of the time; the tracker puts
  each kart by its gap to the leader and leaves the eliminated out.
- menu.gd: mode note. webnet.gd: PROTO 124.
    py.cmd tools/mini/pc99.py      (once, after pc98)"""
G = 'D:/crust-rush/godot/scripts/'


def rep(f, a, b, n=1):
    p = G + f
    s = open(p, encoding='utf-8', newline='').read()
    assert s.count(a) == n, (f, s.count(a), a[:80])
    s = s.replace(a, b)
    open(p, 'w', encoding='utf-8', newline='').write(s)


# ---- race.gd
rep('race.gd', """	if a.finished:
		return true
	if b.finished:
		return false
	return a.prog > b.prog""", """	if a.finished:
		return not a.elim   # (pc99) the eliminated after everyone still racing
	if b.finished:
		return b.elim
	return a.prog > b.prog""")
rep('race.gd', "## Last Slice Standing: each time the leader starts a new lap, whoever is last is out; the last kart racing wins (web lssTick)",
    "## Last Slice Standing: every LSS_EVERY s whoever is last is out; the last kart racing wins (web lssTick, patch 111)")
rep('race.gd', "func _lss_tick() -> void:", """const LSS_EVERY := 30.0


## when the next one is out: (number out + 1) x 30 s, so a guest counts down to the same moment (web lssNext)
func lss_next() -> float:
	var n := 0
	for k in karts:
		if k.elim:
			n += 1
	return (n + 1) * LSS_EVERY


func _lss_tick() -> void:""")
rep('race.gd', """	var lap := int(floor(float(lead.prog) / T.N))
	if lap > lss_lap and lap < T.LAPS:
		lss_lap = lap
		var last: Kart = act[0]
		for k in act:
			if k.prog < last.prog:
				last = k
		_lss_elim(last, act.size(), true)""", """	if race_time >= lss_next():
		lss_lap += 1
		var last: Kart = act[0]
		for k in act:
			if k.prog < last.prog:
				last = k
		_lss_elim(last, act.size(), true)
		if act.size() == 2:
			var w: Kart = act[1] if act[0] == last else act[0]
			w.finished = true
			w.finish_time = race_time
			w.place = 1
			lss_done = true
			fx.append({"t": "lss_win", "k": w})""")

# ---- main.gd
rep('main.gd', 'T.LAPS = maxi(2, race.karts.size() - 1) if race.mode == "lss" else T.laps0',
    'T.LAPS = 99 if race.mode == "lss" else T.laps0   # (pc99: LSS goes by the clock; 99 is a safety net)')
rep('main.gd', 'rtxt = ("out on lap %d" % k.elim_lap) if k.elim else', 'rtxt = ("out at " + _mmss(k.finish_time)) if k.elim else')
rep('main.gd', 'rt = "out on lap %d" % k.elim_lap', 'rt = "out at " + _mmss(k.finish_time)')
rep('main.gd', 'rt = "racing · lap %d of %d" % [mini(T.LAPS, int(floor(maxf(0.0, float(k.prog)) / T.N)) + 1), T.LAPS]',
    'rt = "racing · " + _lap_of(k)')
rep('main.gd', 'info += "lap %d of %d" % [mini(T.LAPS, int(floor(maxf(0.0, float(k.prog)) / T.N)) + 1), T.LAPS]',
    'info += _lap_of(k)')
rep('main.gd', "\nfunc _fin_start(", """
## (pc99) "lap 2 of 3"; in Last Slice Standing (no lap total) "lap 2"
func _lap_of(k: Kart) -> String:
	var lp := mini(T.LAPS, int(floor(maxf(0.0, float(k.prog)) / T.N)) + 1)
	return ("lap %d" % lp) if race != null and race.mode == "lss" else ("lap %d of %d" % [lp, T.LAPS])


func _mmss(t: float) -> String:
	return "%d:%02d" % [int(t / 60.0), int(fmod(t, 60.0))]


func _fin_start(""")

# ---- hud.gd
rep('hud.gd', 'var lap_txt := "%d/%d" % [me.lap() if me else 1, T.LAPS if T else 3]',
    'var lap_txt := ("%d" % (me.lap() if me else 1)) if race != null and race.mode == "lss" else "%d/%d" % [me.lap() if me else 1, T.LAPS if T else 3]')
rep('hud.gd', """		for lp in range(1, T.LAPS):
			var fx := lx0""", """		var lss := race.mode == "lss"
		for lp in range(1, 0 if lss else T.LAPS):
			var fx := lx0""")
rep('hud.gd', """		for k in race.karts:
			var f := clampf((total if k.finished else float(k.prog)) / total, 0.0, 1.0)""", """		for k in race.karts:
			if k.elim and k != hk:
				continue   # (pc99) out: off the tracker
			var f := clampf((total if k.finished else float(k.prog)) / total, 0.0, 1.0)
			if lss:
				f = float(posmod(k.prog, T.N)) / T.N   # where it is on its current lap (web patch 111)""")
rep('hud.gd', """	var lap := me.lap()
	for i in T.LAPS:""", """	var lap := me.lap()
	var lss := race != null and race.mode == "lss"
	for i in (0 if lss else T.LAPS):""")
rep('hud.gd', """	_text(f_bold, _fmt(me.finish_time if me.finished else race.race_time), lx + 10.0, ly + 4.0 + lb * 1.15 + 1.0, tsz, CHEESE,""",
    """	var tstr := _fmt(me.finish_time if me.finished else race.race_time)
	var tcol := CHEESE
	if lss and not me.finished:
		var left := maxi(0, int(ceil(race.lss_next() - race.race_time)))
		tstr = "Next out %ds" % left
		if race.state == "race" and left <= 5:
			tcol = Color("#ff5a4a")
	_text(f_bold, tstr, lx + 10.0, ly + 4.0 + lb * 1.15 + 1.0, tsz, tcol,""")

# ---- menu.gd, webnet.gd
rep('menu.gd', '"Last Slice Standing: each time the leader completes a lap, the racer in last place is out. Seven laps, one slice left."',
    '"Last Slice Standing: every 30 seconds, the racer in last place is out. Keep racing until one slice is left."')
rep('webnet.gd', 'const PROTO := 123   # (', 'const PROTO := 124   # (124: web v246, Last Slice Standing on a 30 s clock; ')
print('pc99 applied')
