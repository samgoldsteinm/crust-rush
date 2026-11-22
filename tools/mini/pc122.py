"""pc122: split screen, player 2's own kart and engine.
- Player 2's garage: after their driver, "garage2" opens the same garage editing player 2's build (menu.g_p2: build and ri are
  swapped with p2_build and p2_ri while it is open, and swapped back when another screen opens). Saved as sel p2_build; the race
  seats player 2 with it (make_cfg prefs). A new driver for player 2 starts from that driver's own kart.
- Player 2's engine: a second Sfx (sfx2) driven by player 2's kart in their HUD pass.
    python tools/mini/pc122.py"""
G = 'D:/crust-rush/godot/scripts/'


def patch(fn, reps):
    p = G + fn
    s = open(p, encoding='utf-8', newline='').read()
    for a, b in reps:
        assert s.count(a) == 1, (fn, s.count(a), a[:90])
        s = s.replace(a, b)
    open(p, 'w', encoding='utf-8', newline='').write(s)


patch('menu.gd', [
    ("var p2_pad := -1 ", "var p2_build := {}      # player 2's kart (pc122)\nvar g_p2 := false       # the garage is editing player 2's kart\nvar _g_save := {}       # player 1's build and driver while it does\nvar p2_pad := -1 "),
    ("\tif name_ == \"track\" and _two_up() and cur != \"driver2\" and cur != \"track\":\n\t\tname_ = \"driver2\"\n",
     "\tif name_ == \"track\" and _two_up() and cur != \"driver2\" and cur != \"track\" and not g_p2:\n\t\tname_ = \"driver2\"\n"
     "\t# player 2's garage (pc122): the garage itself, with player 2's kart and driver swapped in until another screen opens\n"
     "\tif name_ == \"garage2\":\n"
     "\t\tname_ = \"garage\"\n"
     "\t\tif not g_p2:\n"
     "\t\t\tg_p2 = true\n"
     "\t\t\t_g_save = {\"build\": build, \"ri\": ri}\n"
     "\t\t\tbuild = p2_build.duplicate() if not p2_build.is_empty() else build.duplicate()\n"
     "\t\t\tri = p2_ri\n"
     "\t\t\t_g_keep = {}\n"
     "\telif g_p2 and name_ != \"garage\":\n"
     "\t\tg_p2 = false\n"
     "\t\tp2_build = build.duplicate()\n"
     "\t\tbuild = _g_save[\"build\"]\n"
     "\t\tri = int(_g_save[\"ri\"])\n"
     "\t\t_g_keep = {}\n"),
    ("\t\tv.add_child(_step_head(\"‹ Back\", \"garage\" if three else \"driver\", \"Split screen\", \"Player 2: choose a driver\", \"CHOOSE TRACK  ›\", func(): open(\"track\")))\n",
     "\t\tv.add_child(_step_head(\"‹ Back\", \"garage\" if three else \"driver\", \"Split screen\", \"Player 2: choose a driver\", \"BUILD KART  ›\" if three else \"CHOOSE TRACK  ›\", func(): open(\"garage2\" if three else \"track\")))\n"),
    ("\tback.pressed.connect(func(): open(\"driver\"))\n\th.add_child(back)\n\tvar tv := vbox(0)\n\ttv.add_child(label(\"GARAGE\", f_disp, 30.0, CHEESE, SAUCE_DARK, Vector2(0, 3)))\n\ttv.add_child(label(\"STEP 2 OF 3\", f_bold, 9.0, MUTED))\n",
     "\tback.pressed.connect(func(): open(\"driver2\" if g_p2 else \"driver\"))\n\th.add_child(back)\n\tvar tv := vbox(0)\n"
     "\ttv.add_child(label(\"PLAYER 2 · GARAGE\" if g_p2 else \"GARAGE\", f_disp, 30.0, CHEESE, SAUCE_DARK, Vector2(0, 3)))\n"
     "\ttv.add_child(label(\"SPLIT SCREEN\" if g_p2 else \"STEP 2 OF 3\", f_bold, 9.0, MUTED))\n"),
    ("func _build_changed() -> void:\n\tsetting_changed.emit(\"build\", build.duplicate())\n",
     "func _build_changed() -> void:\n\tif g_p2:\n\t\tp2_build = build.duplicate()\n\tsetting_changed.emit(\"p2_build\" if g_p2 else \"build\", build.duplicate())\n"),
])

patch('main.gd', [
    # player 2's kart goes to the race with them
    ("{2: {\"ri\": int(sel.get(\"p2_ri\", -1))}})", "{2: {\"ri\": int(sel.get(\"p2_ri\", -1)), \"build\": sel.get(\"p2_build\", {}) if sel.get(\"p2_build\") is Dictionary else {}}})"),
    ("\tfor k in [\"players\", \"p2_ri\", \"p2_pad\", \"p2_guid\"]:", "\tfor k in [\"players\", \"p2_ri\", \"p2_pad\", \"p2_guid\", \"p2_build\"]:"),
    ("\t\tif k == \"favs\" or k == \"players\" or k == \"p2_ri\" or k == \"p2_guid\":\n\t\t\t_save_settings()\n",
     "\t\tif k == \"p2_ri\":\n"
     "\t\t\t# a new driver for player 2 starts from that driver's own kart (pc122)\n"
     "\t\t\tsel[\"p2_build\"] = _p2_default(int(v))\n"
     "\t\t\tmenu.p2_build = (sel[\"p2_build\"] as Dictionary).duplicate()\n"
     "\t\tif k == \"favs\" or k == \"players\" or k == \"p2_ri\" or k == \"p2_guid\" or k == \"p2_build\":\n\t\t\t_save_settings()\n"),
    ("\tmenu.p2_pad = int(sel.get(\"p2_pad\", -1))\n",
     "\tmenu.p2_pad = int(sel.get(\"p2_pad\", -1))\n"
     "\tmenu.p2_build = (sel[\"p2_build\"] as Dictionary).duplicate() if (sel.get(\"p2_build\") is Dictionary and not (sel[\"p2_build\"] as Dictionary).is_empty()) else _p2_default(int(sel.get(\"p2_ri\", -1)))\n"),
    # player 2's engine
    ("\tif not _in_p2:   # (the engine you hear is player 1's)\n\t\tsfx.drive(",
     "\tif _in_p2 and sfx2 != null:\n\t\tsfx2.silent = sfx.silent\n\t\tsfx2.drive(absf(k.speed) / k.base_max, true, k.boost > 0.0, k.drift != 0 and not k.air, k.tier, state != \"countdown\" and state != \"results\" and state != \"menu\" and not paused)\n"
     "\telif not _in_p2:\n\t\tsfx.drive("),
    ("\tview.me2 = kart2\n\tp2 = {}\n",
     "\tview.me2 = kart2\n"
     "\tif sfx2 == null:\n\t\tsfx2 = Sfx.new()\n\t\tadd_child(sfx2)\n"
     "\tsfx2.set_body(String(kart2.info.get(\"body\", \"\")))\n"
     "\tp2 = {}\n"),
    ("\tsplit_live = false\n\tkart2 = null\n\tview.me2 = null\n",
     "\tsplit_live = false\n\tkart2 = null\n\tview.me2 = null\n"
     "\tif sfx2 != null:\n\t\tsfx2.drive(0.0, false, false, false, 0, false)   # (player 2's engine stops)\n"),
    ("var _sv_sync_t := 0.0\n",
     "var _sv_sync_t := 0.0\nvar sfx2: Sfx = null           # player 2's engine (pc122)\n\n\n"
     "## a driver's own kart (the build the web game gives that driver), for player 2\n"
     "func _p2_default(ri: int) -> Dictionary:\n"
     "\tfor q in roster.get(\"racers\", []):\n"
     "\t\tif int((q as Dictionary).get(\"ri\", -1)) == ri and (q as Dictionary).get(\"build\") is Dictionary:\n"
     "\t\t\treturn ((q as Dictionary)[\"build\"] as Dictionary).duplicate()\n"
     "\treturn {\"b\": 0, \"w\": 0, \"g\": 0, \"p\": 0, \"t\": \"\"}\n"),
])
print('pc122 applied')
