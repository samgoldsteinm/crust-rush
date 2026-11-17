"""The PC side of web patch 69 (v220): a key to restart the race, Backspace by default (Settings > Controls).
    py.cmd tools/mini/pc69.py      (once; edits D:/crust-rush/godot/scripts)
The first press pauses and asks "Restart the race?" (in place of the pause menu); the same key again restarts, as the pause menu's
Restart race does; Esc, P or Start (any pause toggle) answers Keep racing and resumes. Off line races only: never in a room (the host
runs it), Sandbox or Balloon Battle. Nothing that moves a kart: the online version stays 120.
"""
G = 'D:/crust-rush/godot/scripts/'


def rep(f, a, b, n=1):
    p = G + f
    s = open(p, encoding='utf-8', newline='').read()
    assert s.count(a) == n, (f, s.count(a), a[:80])
    s = s.replace(a, b)
    open(p, 'w', encoding='utf-8', newline='').write(s)


# ---------------------------------------------------------------- keys
rep('keys.gd', '["pause", "Pause"], ', '["pause", "Pause"], ["restart", "Restart the race (press twice)"], ')
rep('keys.gd', '"pause": [KEY_P], ', '"pause": [KEY_P], "restart": [KEY_BACKSPACE], ')

# ---------------------------------------------------------------- main
rep('main.gd', """func _toggle_pause() -> void:
	if state == "results" or state == "menu":
		return
""", """func _toggle_pause() -> void:
	if state == "results" or state == "menu":
		return
	if rst_ui != null:
		_rst_no()   # "Restart the race?" is up: Esc / P / Start answer Keep racing
		return
""")
rep('main.gd', """## "Back to the track?": a small sheet over the pause menu;""", """## The restart key (web patch 69, Backspace by default): the first press pauses and asks, the same key again restarts.
## Off line races only (never a room, Sandbox or Balloon Battle). Esc / P / Start, or Keep racing, resume the race.
var rst_ui: Control = null
func _rst_ok() -> bool:
	return (state == "race" or state == "countdown") and net_role == "" and race != null and race.sb == null and T != null and not T.battle \\
		and not (menu != null and menu.visible) and sb_go.is_empty()


func _rst_key() -> void:
	if rst_ui != null:
		_rst_go()
		return
	if not _rst_ok():
		return
	paused = true
	panel_pause.visible = true
	var dim := Control.new()
	dim.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	dim.mouse_filter = Control.MOUSE_FILTER_STOP
	for c in panel_pause.get_children():
		c.queue_free()   # (the pause menu is not shown under it: web rstKey hides pauseOv)
	panel_pause.add_child(dim)
	var v := _sheet(dim, 440.0)
	v.add_child(menu.label("Restart the race?", menu.f_disp, 30.0, Color("#fff4dc")))
	var t := menu.label("Press %s again to restart." % Keys.list("restart"), menu.f_med, 17.0, Color("#fff4dc"))
	t.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	t.custom_minimum_size = Vector2(380, 0)
	t.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	v.add_child(t)
	var row := menu.hbox(10)
	var yes := menu.button("Restart", "cta", 19.0, Vector4(14, 12, 14, 12))
	var no := menu.button("Keep racing", "ghost", 19.0, Vector4(14, 12, 14, 12))
	yes.pressed.connect(_rst_go)
	no.pressed.connect(_rst_no)
	row.add_child(yes)
	row.add_child(no)
	v.add_child(row)
	rst_ui = dim
	yes.grab_focus.call_deferred()


func _rst_go() -> void:
	if rst_ui != null:
		rst_ui.queue_free()
		rst_ui = null
	_restart()


func _rst_no() -> void:
	if rst_ui != null:
		rst_ui.queue_free()
		rst_ui = null
	paused = false
	panel_pause.visible = false


## "Back to the track?": a small sheet over the pause menu;""")
rep('main.gd', """				"pause":
					if not (menu != null and menu.visible):
						_toggle_pause()
""", """				"pause":
					if not (menu != null and menu.visible):
						_toggle_pause()
				"restart":
					_rst_key()   # (web patch 69)
""")
print('pc69 applied')
