"""PC: the menu as big as the web's, not bigger. The owner: "the menu screen on the pc is massive can we make it the same size as the web app".
Z (1.18, the web's zoom at 1280x720) was fixed while Godot's canvas stretch grows everything with the window (1.5x at 1080p), so a
1080p screen showed the menu at 1.77x where the web shows 1.32x. Now Z is worked out from the window: the web's zoom for that screen
(its @media steps: panels 1/1.18/1.32/1.6, the garage 1/1.25/1.45/1.75, in CSS pixels = window / Windows' scale) divided by the stretch.
Changing the window size rebuilds the open screen at the new size.
    python tools/mini/pc107.py      (once, after pc106)"""
p = 'D:/crust-rush/godot/scripts/menu.gd'
s = open(p, encoding='utf-8', newline='').read()
assert 'pc107' not in s, 'already patched'


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:80])
    s = s.replace(a, b)


rep("const Z := 1.18\n",
    "var Z := 1.18   # (pc107) set by _fit_z: the web's zoom for this screen over Godot's stretch\n")

rep("func z(v: float) -> float:\n",
    """## (pc107) the web's zoom for this window (its @media steps, in CSS pixels: the window over Windows' scale), over Godot's
## canvas stretch (window / 1280x720), so the menu is the size the web's is on the same screen
func _fit_z(scr: String) -> bool:
	var ws := Vector2(DisplayServer.window_get_size())
	if ws.x < 2.0 or ws.y < 2.0:
		return false
	var dpr := clampf(DisplayServer.screen_get_dpi() / 96.0, 1.0, 3.0)
	var cw := ws.x / dpr
	var ch := ws.y / dpr
	var wz := 1.0
	if scr == "garage":
		if cw >= 2400 and ch >= 1200:
			wz = 1.75
		elif cw >= 1800 and ch >= 900:
			wz = 1.45
		elif cw >= 1300 and ch >= 700:
			wz = 1.25
	else:
		if cw >= 2200 and ch >= 1100:
			wz = 1.6
		elif cw >= 1500 and ch >= 800:
			wz = 1.32
		elif cw >= 1100 and ch >= 620:
			wz = 1.18
	var st := minf(ws.x / 1280.0, ws.y / 720.0)
	var nz := clampf(wz * dpr / maxf(st, 0.1), 0.6, 1.6)
	var ch_ := absf(nz - Z) > 0.004
	Z = nz
	return ch_


func z(v: float) -> float:
""")

rep("""	bg.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(bg)
""", """	bg.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(bg)
	_fit_z("home")
	# (pc107) a new window size: the open screen again at the web's size for it
	get_viewport().size_changed.connect(func():
		if cur != "" and is_visible_in_tree() and modal == null and _fit_z(cur):
			open(cur))
""")

rep("""	cur = name_
	bg.set_blur(name_ == "garage")
""", """	cur = name_
	_fit_z(name_)   # (pc107)
	bg.set_blur(name_ == "garage")
""")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('pc107 applied')
