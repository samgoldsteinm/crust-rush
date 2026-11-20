"""PC: the lap box holds its best-time line. The owner: "the hud for the lap time and where it says old rules time is messed up
the words run off the edge". The box's width was taken before the best-time line was measured, so "Old-rules best 4:27.02"
ran out of it. Now it is measured first.
    python tools/mini/pc111.py      (once, after pc110)"""
p = 'D:/crust-rush/godot/scripts/hud.gd'
s = open(p, encoding='utf-8', newline='').read()
assert 'pc111' not in s
a = """	var lap_w := maxf(row_w, 80.0) + 20.0
	var lap_h := 4.0 + lap_big * 1.15 + 1.0 + time_size * 1.2 + 5.0
	var pb_size := clampf(2.2 * _vmin(), 11.0, 14.0)
	if pb_text != "":
		lap_h += pb_size * 1.2
		row_w = maxf(row_w, f_bold.get_string_size(pb_text, HORIZONTAL_ALIGNMENT_LEFT, -1, int(pb_size)).x)
"""
b = """	var lap_h := 4.0 + lap_big * 1.15 + 1.0 + time_size * 1.2 + 5.0
	var pb_size := clampf(2.2 * _vmin(), 11.0, 14.0)
	if pb_text != "":
		lap_h += pb_size * 1.2
		row_w = maxf(row_w, f_bold.get_string_size(pb_text, HORIZONTAL_ALIGNMENT_LEFT, -1, int(pb_size)).x)
	var lap_w := maxf(row_w, 80.0) + 20.0   # (pc111) after the best-time line is measured, so it fits
"""
assert s.count(a) == 1
s = s.replace(a, b)
open(p, 'w', encoding='utf-8', newline='').write(s)
print('pc111 applied')
