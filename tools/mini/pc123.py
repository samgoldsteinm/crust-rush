"""pc123: split screen, player 2 plays like a normal game: the race's events (items, hits, shields, boosts, toasts, battle banners)
are drained a second time from player 2's side (P_VARS swapped in: their camera's shakes and flashes, their HUD's toasts), with
the sounds they would hear. Sounds player 1's pass already played as loud this step are not played again (Sfx.dedupe), so
sounds near both karts do not double. No stats or awards from player 2's pass. Replaces pc120's _p2_events.
    python tools/mini/pc123.py"""
G = 'D:/crust-rush/godot/scripts/'


def patch(fn, reps):
    p = G + fn
    s = open(p, encoding='utf-8', newline='').read()
    for a, b in reps:
        assert s.count(a) == 1, (fn, s.count(a), a[:90])
        s = s.replace(a, b)
    open(p, 'w', encoding='utf-8', newline='').write(s)


patch('sfx.gd', [
    ("var silent := false ",
     "var dedupe := {}                  # split screen (pc123): name -> loudest this step in player 1's pass\n"
     "var second := false               # player 2's pass: a sound already played as loud is not played again\n"
     "var silent := false "),
    ("func play(name_: String, vol := 1.0, pitch := 1.0) -> void:\n\tif silent or not bank.has(name_) or vol <= 0.01:\n\t\treturn\n",
     "func play(name_: String, vol := 1.0, pitch := 1.0) -> void:\n\tif silent or not bank.has(name_) or vol <= 0.01:\n\t\treturn\n"
     "\tif second:\n"
     "\t\tif float(dedupe.get(name_, -1.0)) >= vol * 0.85:\n\t\t\treturn\n"
     "\t\tvol = sqrt(maxf(0.0, vol * vol - pow(float(dedupe.get(name_, 0.0)), 2.0)))   # (only what is missing: the two add up to player 2's loudness)\n"
     "\telse:\n"
     "\t\tdedupe[name_] = maxf(float(dedupe.get(name_, 0.0)), vol)\n"),
])

patch('main.gd', [
    ("\tif split_live and kart2 != null:\n\t\t_p2_events()\n\t_drain_events()\n",
     "\tsfx.dedupe.clear()\n\tvar two_up := split_live and kart2 != null\n\t_keep_ev = two_up   # (player 2's pass reads the same events, then they are cleared)\n"
     "\t_drain_events()\n\t_keep_ev = false\n\tif two_up:\n\t\t_p2_drain()\n"),
    ("\t\t\t\tif mine:\n\t\t\t\t\tsfx.play(\"ready\", 0.8)\n\t\tk.events.clear()\n",
     "\t\t\t\tif mine:\n\t\t\t\t\tsfx.play(\"ready\", 0.8)\n\t\tif not _keep_ev:\n\t\t\tk.events.clear()\n"),
    ("\t\t\tsfx.play(\"ready\")\n\trace.fx.clear()\n",
     "\t\t\tsfx.play(\"ready\")\n\tif not _keep_ev:\n\t\trace.fx.clear()\n"),
    ("\tfor k in race.karts:\n\t\tfor e in k.events:\n\t\t\tview.kart_event(k, e)\n",
     "\tfor k in race.karts:\n\t\tfor e in k.events:\n\t\t\tif not _in_p2:\n\t\t\t\tview.kart_event(k, e)\n"),
    ("## player 2's laps and finish, on their own half\n",
     "## the race's events again from player 2's side (pc123): their shakes, flashes, toasts and sounds; no stats or awards\n"
     "var _keep_ev := false   # player 1's pass leaves the events for player 2's\n\n\n"
     "func _p2_drain() -> void:\n"
     "\tvar st: Dictionary = stats.duplicate(true)\n"
     "\tvar ad := auto_drive\n"
     "\t_p_swap()\n"
     "\t_in_p2 = true\n"
     "\tauto_drive = true\n"
     "\tsfx.second = true\n"
     "\t_drain_events()\n"
     "\tsfx.second = false\n"
     "\tauto_drive = ad\n"
     "\t_in_p2 = false\n"
     "\t_p_swap()\n"
     "\tstats = st\n\n\n"
     "## player 2's laps and finish, on their own half\n"),
])
print('pc123 applied')
