"""PC: the home, driver and track screens laid out as the web's (after pc107's sizes): at most 1240 wide (the web's .wiz max-width,
in its zoomed pixels) and centred, so on a big window they no longer run edge to edge; and the logo sized as the web's
.home-brand .logo, min(clamp(34px, 6.4vw, 96px), 17vh) in CSS pixels, so it fills its half as the web's does.
    python tools/mini/pc108.py      (once, after pc107)"""
p = 'D:/crust-rush/godot/scripts/menu.gd'
s = open(p, encoding='utf-8', newline='').read()
assert 'pc107' in s and 'pc108' not in s


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:80])
    s = s.replace(a, b)


rep("	var ch_ := absf(nz - Z) > 0.004\n	Z = nz\n",
    "	var ch_ := absf(nz - Z) > 0.004\n	Z = nz\n	_css = Vector2(cw, ch)   # (pc108)\n")
rep("var Z := 1.18   # (pc107)", "var _css := Vector2(1280, 720)   # (pc108) the window in the web's CSS pixels\nvar Z := 1.18   # (pc107)")

rep("""func _screen_root() -> MarginContainer:
	var m := MarginContainer.new()
	m.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	m.add_theme_constant_override("margin_left", zi(14))
	m.add_theme_constant_override("margin_right", zi(14))
""", """func _screen_root(maxw := 0.0) -> MarginContainer:
	var m := MarginContainer.new()
	m.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	# (pc108) the web's steps stop at 1240 wide (.wiz max-width) and sit in the middle
	var side := float(zi(14))
	if maxw > 0.0:
		side = maxf(side, (get_viewport_rect().size.x - z(maxw)) * 0.5)
	m.add_theme_constant_override("margin_left", int(side))
	m.add_theme_constant_override("margin_right", int(side))
""")
rep("""func _home() -> Control:
	var root := _screen_root()""", """func _home() -> Control:
	var root := _screen_root(1240.0)""")
rep("""func _driver() -> Control:
	var root := _screen_root()""", """func _driver() -> Control:
	var root := _screen_root(1240.0)""")
rep("""func _track() -> Control:
	var root := _screen_root()""", """func _track() -> Control:
	var root := _screen_root(1240.0)""")
rep('	brand.add_child(logo("CRUST RUSH", 82.0, true))\n',
    '	brand.add_child(logo("CRUST RUSH", minf(clampf(_css.x * 0.064, 34.0, 96.0), _css.y * 0.17), true))   # (pc108) the web\'s size\n')
open(p, 'w', encoding='utf-8', newline='').write(s)
print('pc108 applied')
