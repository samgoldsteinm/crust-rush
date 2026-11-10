class_name Hud
extends Control
## The race HUD, drawn to match the web game's (its CSS, at the same sizes): position and progress
## bar along the top, lap box, pause button, two glass item slots on the right, the Special and
## Rear buttons on the left, the speed gauge and the drift pedals at the bottom, banners in the middle.
## Sizes are worked out in CSS pixels exactly like the web's clamp()/vmin rules, then scaled by `s`.

const CHEESE := Color("#f7c948")
const CREAM := Color("#fff4dc")
const SAUCE := Color("#e0452c")
const SAUCE_DARK := Color("#7d1d0e")
const MUTED := Color("#c2a58c")
const SPARK_TIER := [Color("#fff4dc"), Color("#ffe066"), Color("#ff9a1f"), Color("#ff3b1a")]

var race: Race
var me: Kart
var T: TrackData
var icons := {}
var portraits := {}
var racer_cols: Array = []

var f_disp: Font
var f_bold: Font
var f_semi: Font
var s := 1.0          # CSS px -> screen px
var W := 1280.0       # screen size in CSS px
var H := 720.0
var t := 0.0

var banner_text := ""
var banner_t := 0.0
var banner_kind := ""   # "" (big), "md", "sm"
var pos_txt: GradText
var banner_txt: GradText
var steer_dir := 0      # touch-zone arrows light up
var braking := false
var look := false
var pad_mode := false
var wrong_t := 0.0
var toast_text := ""
var toast_t := 0.0
var hitfx_t := 0.0
var show_touch := true

var _ibtn_tex: ImageTexture
var _abtn_tex: ImageTexture


class GradText extends Control:
	var text := ""
	var font: Font
	var size_px := 40.0
	var spacing := 0.0
	func _draw() -> void:
		if text == "" or font == null:
			return
		draw_string(font, Vector2(0, size_px * 0.8), text, HORIZONTAL_ALIGNMENT_LEFT, -1, int(size_px), Color.WHITE)


func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	set_anchors_preset(Control.PRESET_FULL_RECT)
	f_disp = load("res://assets/fonts/Bungee-Regular.ttf")
	f_bold = load("res://assets/fonts/ChakraPetch-Bold.ttf")
	f_semi = load("res://assets/fonts/ChakraPetch-SemiBold.ttf")
	pos_txt = _grad_text([Color("#fff6cf"), Color("#f7c948"), Color("#ff8a1f"), Color("#e0452c")], Vector3(0.42, 0.78, 1.0))
	banner_txt = _grad_text([Color("#fff8d8"), Color("#f7c948"), Color("#ff8a1f"), Color("#e0452c")], Vector3(0.45, 0.80, 1.0))
	_ibtn_tex = _glass_tex(false)
	_abtn_tex = _glass_tex(true)


func _grad_text(cols: Array, stops: Vector3) -> GradText:
	var g := GradText.new()
	g.font = f_disp
	g.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var m := ShaderMaterial.new()
	m.shader = load("res://shaders/gradtext.gdshader")
	m.set_shader_parameter("c0", cols[0])
	m.set_shader_parameter("c1", cols[1])
	m.set_shader_parameter("c2", cols[2])
	m.set_shader_parameter("c3", cols[3])
	m.set_shader_parameter("stops", stops)
	g.material = m
	add_child(g)
	return g


## the item slot's glass: dark brown core, warm glow from below, a soft highlight on top, a gloss streak
static func _glass_tex(plain: bool) -> ImageTexture:
	var N := 192
	var img := Image.create(N, N, false, Image.FORMAT_RGBA8)
	var core0 := Color("#4a2616")
	var core1 := Color("#120805")
	for y in N:
		for x in N:
			var u := (x + 0.5) / N
			var v := (y + 0.5) / N
			var d := Vector2(u - 0.5, v - 0.5).length()
			if d > 0.5:
				img.set_pixel(x, y, Color(0, 0, 0, 0))
				continue
			# radial-gradient(circle at 50% 35%, #4a2616, #120805 72%)
			var r0 := Vector2(u - 0.5, v - 0.35).length() / 0.72 / 0.92
			var c := core0.lerp(core1, clampf(r0 / 0.72, 0.0, 1.0))
			if not plain:
				# radial-gradient(circle at 50% 120%, rgba(255,170,60,.35), transparent 55%)
				var r1 := Vector2(u - 0.5, v - 1.2).length() / 0.92
				var a1 := 0.35 * clampf(1.0 - r1 / 0.55, 0.0, 1.0)
				c = c.lerp(Color(1.0, 0.667, 0.235), a1)
				# radial-gradient(circle at 50% 22%, rgba(255,255,255,.22), transparent 34%)
				var r2 := Vector2(u - 0.5, v - 0.22).length() / 0.92
				var a2 := 0.22 * clampf(1.0 - r2 / 0.34, 0.0, 1.0)
				c = c.lerp(Color.WHITE, a2)
				# gloss: an ellipse across the top (left 18%, right 18%, top 7%, height 22%)
				var gx := (u - 0.5) / 0.32
				var gy := (v - 0.18) / 0.11
				if gx * gx + gy * gy < 1.0:
					var g := clampf(1.0 - (v - 0.07) / 0.22, 0.0, 1.0)
					c = c.lerp(Color.WHITE, 0.55 * g * 0.5)
			# inset shadow at the bottom edge
			var edge := clampf((d - 0.38) / 0.12, 0.0, 1.0) * clampf((v - 0.5) * 2.0, 0.0, 1.0)
			c = c.lerp(Color.BLACK, 0.5 * edge)
			var aa := clampf((0.5 - d) * N, 0.0, 1.0)
			c.a = aa
			img.set_pixel(x, y, c)
	img.generate_mipmaps()
	return ImageTexture.create_from_image(img)


func banner(text: String, dur: float, kind := "") -> void:
	banner_text = text
	banner_t = dur
	banner_kind = kind


func toast(text: String, dur := 1.2) -> void:
	toast_text = text
	toast_t = dur


func hit_flash() -> void:
	hitfx_t = 0.6


# ---------------------------------------------------------------- per frame

func tick(dt: float) -> void:
	t += dt
	if banner_t > 0.0:
		banner_t -= dt
		if banner_t <= 0.0:
			banner_text = ""
	if toast_t > 0.0:
		toast_t -= dt
	if hitfx_t > 0.0:
		hitfx_t -= dt
	var vs := get_viewport_rect().size
	# like the browser's device-pixel ratio: the screen's scale setting (96 dpi = 1)
	s = clampf(float(DisplayServer.screen_get_dpi()) / 96.0, 1.0, 3.0) if DisplayServer.get_name() != "headless" else 1.0
	W = vs.x / s
	H = vs.y / s
	_place_texts()
	queue_redraw()
	pos_txt.queue_redraw()
	banner_txt.queue_redraw()


func _vmin() -> float:
	return minf(W, H) / 100.0


func _btn() -> float:
	return clampf(15.0 * _vmin(), 62.0, 104.0)


func _hud_top() -> float:
	return clampf(0.15 * H, 58.0, 96.0)


static func _ord_suffix(n: int) -> String:
	if n % 100 >= 11 and n % 100 <= 13:
		return "th"
	return ["th", "st", "nd", "rd", "th", "th", "th", "th", "th", "th"][n % 10]


func _pos_num() -> int:
	if me == null or race == null:
		return 1
	return me.place if me.finished else race.position_of(me)


func _top_bar() -> Dictionary:
	var tl_w := minf(minf(0.66 * W, 680.0), W - _btn() * 2.4 - 60.0)
	var x0 := 16.0 + (W - 32.0 - tl_w) / 2.0
	var pos_size := clampf(9.0 * _vmin(), 30.0, 58.0)
	var suf_size := clampf(3.2 * _vmin(), 13.0, 22.0)
	var lap_big := clampf(3.6 * _vmin(), 15.0, 22.0)
	var time_size := clampf(2.6 * _vmin(), 11.0, 15.0)
	var num := str(_pos_num())
	var num_w := f_disp.get_string_size(num, HORIZONTAL_ALIGNMENT_LEFT, -1, int(pos_size)).x
	var suf_w := maxf(f_disp.get_string_size(_ord_suffix(_pos_num()).to_upper(), HORIZONTAL_ALIGNMENT_LEFT, -1, int(suf_size)).x, f_bold.get_string_size("OF 8", HORIZONTAL_ALIGNMENT_LEFT, -1, 10).x + 4.0)
	var pos_w := num_w + 6.0 + suf_w
	var lap_txt := "%d/%d" % [me.lap() if me else 1, T.LAPS if T else 3]
	var row_w := f_bold.get_string_size("LAP", HORIZONTAL_ALIGNMENT_LEFT, -1, 10).x + 4.0 + 8.0 + f_disp.get_string_size(lap_txt, HORIZONTAL_ALIGNMENT_LEFT, -1, int(lap_big)).x + 8.0 + 3 * 10.0 + 2 * 3.0
	var lap_w := maxf(row_w, 80.0) + 20.0
	var lap_h := 4.0 + lap_big * 1.15 + 1.0 + time_size * 1.2 + 5.0
	var bar_h := maxf(pos_size * 0.85, lap_h)
	var tb_x := x0 + pos_w + 12.0
	var tb_w := tl_w - pos_w - lap_w - 24.0
	return {"x0": x0, "w": tl_w, "y0": 12.0, "h": bar_h, "pos_size": pos_size, "suf_size": suf_size, "num": num, "num_w": num_w,
		"tb_x": tb_x, "tb_w": tb_w, "lap_x": tb_x + tb_w + 12.0, "lap_w": lap_w, "lap_h": lap_h, "lap_big": lap_big, "time_size": time_size, "lap_txt": lap_txt}


func _place_texts() -> void:
	var tb := _top_bar()
	pos_txt.font = f_disp
	pos_txt.text = String(tb["num"])
	pos_txt.size_px = float(tb["pos_size"]) * s
	var py := float(tb["y0"]) + (float(tb["h"]) - float(tb["pos_size"]) * 0.85) / 2.0 - float(tb["pos_size"]) * 0.08
	pos_txt.position = Vector2(float(tb["x0"]), py) * s
	pos_txt.size = Vector2(float(tb["num_w"]) + 10.0, float(tb["pos_size"])) * s
	var m: ShaderMaterial = pos_txt.material
	m.set_shader_parameter("y0", pos_txt.size_px * 0.05)
	m.set_shader_parameter("y1", pos_txt.size_px * 0.82)
	pos_txt.visible = race != null and race.state != "countdown" or (race != null and me != null)
	# banner
	var bsize := clampf(0.2 * H, 48.0, 110.0)
	var btop := 0.28 * H
	if banner_kind == "md":
		bsize = clampf(10.0 * _vmin(), 34.0, 76.0)
		btop = 0.16 * H
	elif banner_kind == "sm":
		bsize = clampf(4.4 * _vmin(), 18.0, 32.0)
		btop = 0.13 * H
	banner_txt.text = banner_text
	banner_txt.size_px = bsize * s
	var bw := f_disp.get_string_size(banner_text, HORIZONTAL_ALIGNMENT_LEFT, -1, int(bsize * s)).x
	banner_txt.position = Vector2(W * s / 2.0 - bw / 2.0, btop * s)
	banner_txt.size = Vector2(bw + 4.0, bsize * s * 1.1)
	var bm: ShaderMaterial = banner_txt.material
	bm.set_shader_parameter("y0", bsize * s * 0.08)
	bm.set_shader_parameter("y1", bsize * s * 0.82)
	banner_txt.visible = banner_text != ""


# ---------------------------------------------------------------- drawing helpers

func _p(v: Vector2) -> Vector2:
	return v * s


func _rbox(x: float, y: float, w: float, h: float, bg: Color, border: Color, bw: float, r: float, shadow := 0.0, shadow_col := Color(0, 0, 0, 0.3), rb := -1.0) -> void:
	var sb := StyleBoxFlat.new()
	sb.bg_color = bg
	sb.border_color = border
	sb.set_border_width_all(int(round(bw * s)))
	sb.corner_radius_top_left = int(r * s)
	sb.corner_radius_top_right = int(r * s)
	var r2 := r if rb < 0.0 else rb
	sb.corner_radius_bottom_left = int(r2 * s)
	sb.corner_radius_bottom_right = int(r2 * s)
	sb.anti_aliasing = true
	if shadow > 0.0:
		sb.shadow_color = shadow_col
		sb.shadow_size = int(shadow * s)
		sb.shadow_offset = Vector2(0, shadow * 0.4 * s)
	draw_style_box(sb, Rect2(_p(Vector2(x, y)), Vector2(w, h) * s))


func _text(font: Font, txt: String, x: float, y: float, size: float, col: Color, align := HORIZONTAL_ALIGNMENT_LEFT, width := -1.0, shadow := Color(0, 0, 0, 0), sh_off := Vector2(0, 2), letter := 0.0) -> void:
	# y is the text's top; baseline sits ~0.8em below
	var fs := int(round(size * s))
	var base := _p(Vector2(x, y + size * 0.8))
	if letter != 0.0:
		var w_total := 0.0
		for ch in txt:
			w_total += font.get_string_size(ch, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x + letter * s
		var cx := base.x
		if align == HORIZONTAL_ALIGNMENT_CENTER:
			cx = base.x + (width * s - w_total) / 2.0
		elif align == HORIZONTAL_ALIGNMENT_RIGHT:
			cx = base.x + width * s - w_total
		for ch in txt:
			if shadow.a > 0.0:
				draw_string(font, Vector2(cx, base.y) + sh_off * s, ch, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, shadow)
			draw_string(font, Vector2(cx, base.y), ch, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, col)
			cx += font.get_string_size(ch, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x + letter * s
		return
	if shadow.a > 0.0:
		draw_string(font, base + sh_off * s, txt, align, width * s if width > 0.0 else -1.0, fs, shadow)
	draw_string(font, base, txt, align, width * s if width > 0.0 else -1.0, fs, col)


func _ring(c: Vector2, r: float, w: float, col: Color) -> void:
	draw_arc(_p(c), r * s, 0.0, TAU, 64, col, w * s, true)


func _chevron(cx: float, cy: float, size: float, right: bool, alpha: float) -> void:
	# svg: M15 4 7 12l8 8 in a 24 box, stroke 3.2, round
	var k := size / 24.0
	var pts := PackedVector2Array()
	if right:
		pts = [Vector2(9, 4), Vector2(17, 12), Vector2(9, 20)]
	else:
		pts = [Vector2(15, 4), Vector2(7, 12), Vector2(15, 20)]
	var out := PackedVector2Array()
	for p in pts:
		out.append(_p(Vector2(cx - size / 2.0 + p.x * k, cy - size / 2.0 + p.y * k)))
	draw_polyline(out + PackedVector2Array(), Color(0, 0, 0, 0.35 * alpha / 0.22 * 0.22), 3.2 * k * s + 2.0, true)
	draw_polyline(out, Color(CREAM.r, CREAM.g, CREAM.b, alpha), 3.2 * k * s, true)


func _draw() -> void:
	if race == null or me == null or T == null:
		return
	var vmin := _vmin()
	var btn := _btn()
	var top := _hud_top()
	# red flash at the edges after a hit
	if hitfx_t > 0.0:
		var a := clampf(hitfx_t / 0.6, 0.0, 1.0) * 0.6
		var vs := get_viewport_rect().size
		for i in 10:
			var f := float(i) / 10.0
			draw_rect(Rect2(Vector2(0, 0), vs).grow(-f * vs.y * 0.25), Color(0.88, 0.16, 0.08, a * 0.12 * (1.0 - f)), false, vs.y * 0.025)
	# touch steering arrows
	if show_touch:
		var az := clampf(7.0 * vmin, 30.0, 48.0)
		_chevron(18.0 + az / 2.0, H / 2.0, az, false, 0.85 if steer_dir < 0 else 0.22)
		_chevron(W - 18.0 - az / 2.0, H / 2.0, az, true, 0.85 if steer_dir > 0 else 0.22)
	_draw_top_bar()
	_draw_pause()
	_draw_items(btn, top)
	_draw_special(btn, top)
	_draw_gauge(btn)
	if show_touch:
		_draw_pedals(btn)
	# banner shadow (the gradient text itself is a child drawn on top)
	if banner_text != "":
		var bsize := banner_txt.size_px / s
		var off := 2.0 if banner_kind == "sm" else 6.0
		var col := Color(90.0 / 255.0, 20.0 / 255.0, 8.0 / 255.0, 0.9) if banner_kind == "sm" else Color(125.0 / 255.0, 29.0 / 255.0, 14.0 / 255.0, 0.95)
		draw_string(f_disp, banner_txt.position + Vector2(0, bsize * s * 0.8 + off * s), banner_text, HORIZONTAL_ALIGNMENT_LEFT, -1, int(bsize * s), col)
	# wrong way
	if wrong_t > 0.8:
		var ws := clampf(5.0 * vmin, 20.0, 40.0)
		var tw := f_disp.get_string_size("WRONG WAY", HORIZONTAL_ALIGNMENT_LEFT, -1, int(ws * s)).x / s
		_rbox(W / 2.0 - tw / 2.0 - 18.0, 0.52 * H - 6.0, tw + 36.0, ws + 12.0, Color("#d63a1e"), Color(0, 0, 0, 0), 0.0, 12.0, 12.0, Color(224.0 / 255, 69.0 / 255, 44.0 / 255, 0.45))
		_text(f_disp, "WRONG WAY", W / 2.0 - tw / 2.0, 0.52 * H, ws, CREAM)
	# toast (bottom centre)
	if toast_t > 0.0 and toast_text != "":
		var ts := 18.0
		var tw2 := f_bold.get_string_size(toast_text, HORIZONTAL_ALIGNMENT_LEFT, -1, int(ts * s)).x / s
		var a2 := clampf(toast_t / 0.25, 0.0, 1.0)
		var y2 := H - 14.0 - (btn * 0.35 + 12.0) - 46.0
		_rbox(W / 2.0 - tw2 / 2.0 - 20.0, y2, tw2 + 40.0, 46.0, Color(14.0 / 255, 7.0 / 255, 4.0 / 255, 0.55 * a2), Color(1, 0.957, 0.863, 0.3 * a2), 1.0, 23.0)
		_text(f_bold, toast_text, W / 2.0 - tw2 / 2.0, y2 + 12.0, ts, Color(CREAM.r, CREAM.g, CREAM.b, a2))


func _draw_top_bar() -> void:
	var tb := _top_bar()
	var x0: float = tb["x0"]
	var y0: float = tb["y0"]
	var h: float = tb["h"]
	var mid := y0 + h / 2.0
	var ps: float = tb["pos_size"]
	# position number shadow (the gradient digits are a child control)
	var py := y0 + (h - ps * 0.85) / 2.0 - ps * 0.08
	draw_string(f_disp, _p(Vector2(x0, py + ps * 0.8 + 3.0)), String(tb["num"]), HORIZONTAL_ALIGNMENT_LEFT, -1, int(ps * s), Color(125.0 / 255, 29.0 / 255, 14.0 / 255, 0.95))
	var sx := x0 + float(tb["num_w"]) + 6.0
	var ss: float = tb["suf_size"]
	_text(f_disp, _ord_suffix(_pos_num()).to_upper(), sx, py + 3.0, ss, CHEESE, HORIZONTAL_ALIGNMENT_LEFT, -1.0, SAUCE_DARK, Vector2(0, 2))
	_text(f_bold, "OF %d" % race.karts.size(), sx + 1.0, py + 3.0 + ss + 2.0, 9.5, Color(1, 0.957, 0.863, 0.65), HORIZONTAL_ALIGNMENT_LEFT, -1.0, Color(0, 0, 0, 0), Vector2.ZERO, 9.5 * 0.14)
	# progress bar with a marker per racer
	var tx: float = tb["tb_x"]
	var tw: float = tb["tb_w"]
	if tw > 40.0:
		var lx0 := tx + 8.0
		var lx1 := tx + tw - 8.0
		_rbox(lx0 - 2.0, mid - 2.5 - 2.0, lx1 - lx0 + 4.0, 9.0, Color(10.0 / 255, 20.0 / 255, 40.0 / 255, 0.6), Color(0, 0, 0, 0), 0.0, 4.0, 3.0, Color(0, 0, 0, 0.4))
		var steps := 24
		for i in steps:
			var f0 := float(i) / steps
			var c := Color(47.0 / 255, 127.0 / 255, 216.0 / 255, 0.9).lerp(Color(127.0 / 255, 208.0 / 255, 1.0, 0.9), f0)
			var rx := lx0 + (lx1 - lx0) * f0
			draw_rect(Rect2(_p(Vector2(rx, mid - 2.5)), Vector2((lx1 - lx0) / steps + 0.5, 5.0) * s), c)
		# lap marks
		for lp in range(1, T.LAPS):
			var fx := lx0 + (lx1 - lx0) * float(lp) / T.LAPS
			_rbox(fx - 1.5, mid - 8.0, 3.0, 16.0, CREAM, Color(10.0 / 255, 20.0 / 255, 40.0 / 255, 0.7), 1.5, 2.0)
			_text(f_bold, "L%d" % (lp + 1), fx - 12.0, mid + 5.0, 9.0, CREAM, HORIZONTAL_ALIGNMENT_CENTER, 24.0, Color(0, 0, 0, 0.9), Vector2(0, 1))
		# chequered flags at both ends
		for fx2 in [tx, tx + tw - 14.0]:
			_rbox(fx2 - 2.0, mid - 9.0, 18.0, 18.0, Color(0, 0, 0, 0.4), Color(0, 0, 0, 0), 0.0, 4.0)
			for qy in 2:
				for qx in 2:
					draw_rect(Rect2(_p(Vector2(fx2 + qx * 7.0, mid - 7.0 + qy * 7.0)), Vector2(7, 7) * s), Color("#111111") if (qx + qy) % 2 == 0 else Color.WHITE)
		var total := float(T.LAPS * T.N)
		var mine_x := 0.0
		for k in race.karts:
			var f := clampf((total if k.finished else float(k.prog)) / total, 0.0, 1.0)
			var mx := lx0 + f * (lx1 - lx0)
			if k == me:
				mine_x = mx
				continue
			_marker(k, mx, mid, 10.0, 2.0, _racer_col(k))
		_draw_glow(Vector2(mine_x, mid), 14.0 + 6.0, CHEESE, 0.5)
		_marker(me, mine_x, mid, 14.0, 3.0, CHEESE)
	# lap box
	var lx: float = tb["lap_x"]
	var lw: float = tb["lap_w"]
	var lh: float = tb["lap_h"]
	var ly := mid - lh / 2.0
	_rbox(lx, ly, lw, lh, Color(29.0 / 255, 15.0 / 255, 9.0 / 255, 0.72), Color(1, 0.957, 0.863, 0.16), 1.0, 12.0, 10.0, Color(0, 0, 0, 0.28))
	var lb: float = tb["lap_big"]
	var lab_w := f_bold.get_string_size("LAP", HORIZONTAL_ALIGNMENT_LEFT, -1, int(10 * s)).x / s + 4.0
	_text(f_bold, "LAP", lx + 10.0, ly + 4.0 + (lb * 1.15 - 10.0) / 2.0, 10.0, MUTED, HORIZONTAL_ALIGNMENT_LEFT, -1.0, Color(0, 0, 0, 0), Vector2.ZERO, 1.6)
	var lt: String = tb["lap_txt"]
	_text(f_disp, lt, lx + 10.0 + lab_w + 8.0, ly + 4.0 + lb * 0.08, lb, CREAM)
	var bx := lx + 10.0 + lab_w + 8.0 + f_disp.get_string_size(lt, HORIZONTAL_ALIGNMENT_LEFT, -1, int(lb * s)).x / s + 8.0
	var lap := me.lap()
	for i in T.LAPS:
		var on := i < lap
		var c2 := Color(1, 0.957, 0.863, 0.18)
		if on:
			c2 = CHEESE.lerp(Color("#ff8a1f"), 0.5)
		_rbox(bx + i * 13.0, ly + 4.0 + lb * 0.575 - 2.5, 10.0, 5.0, c2, Color(0, 0, 0, 0), 0.0, 3.0)
	var tsz: float = tb["time_size"]
	_text(f_bold, _fmt(me.finish_time if me.finished else race.race_time), lx + 10.0, ly + 4.0 + lb * 1.15 + 1.0, tsz, CHEESE, HORIZONTAL_ALIGNMENT_LEFT, -1.0, Color(0, 0, 0, 0.7), Vector2(0, 2), tsz * 0.02)


func _racer_col(k: Kart) -> Color:
	if k.ri < racer_cols.size():
		return racer_cols[k.ri]
	return Color.WHITE


func _draw_glow(c: Vector2, r: float, col: Color, a: float) -> void:
	for i in 6:
		var f := float(i) / 6.0
		draw_circle(_p(c), (r + f * 8.0) * s, Color(col.r, col.g, col.b, a * 0.12 * (1.0 - f)))


func _marker(k: Kart, x: float, y: float, r: float, ring: float, ring_col: Color) -> void:
	draw_circle(_p(Vector2(x, y + 1.5)), (r + ring + 1.0) * s, Color(0, 0, 0, 0.35))
	draw_circle(_p(Vector2(x, y)), (r + ring) * s, ring_col)
	draw_circle(_p(Vector2(x, y)), r * s, Color("#2a1810"))
	var tex: Texture2D = portraits.get(k.ri)
	if tex != null:
		# background-size 230%, centred at 50% 26%: the face fills the disc
		var src := Rect2(tex.get_width() * (0.5 - 0.5 / 2.3), tex.get_height() * (0.26 - 0.26 / 2.3), tex.get_width() / 2.3, tex.get_height() / 2.3)
		draw_texture_rect_region(tex, Rect2(_p(Vector2(x - r, y - r)), Vector2(2 * r, 2 * r) * s), src)


func _draw_pause() -> void:
	var c := Vector2(W - 16.0 - 22.0, 12.0 + 22.0)
	draw_circle(_p(c + Vector2(0, 3)), 24.0 * s, Color(0, 0, 0, 0.15))
	draw_circle(_p(c), 22.0 * s, Color(29.0 / 255, 15.0 / 255, 9.0 / 255, 0.75))
	_ring(c, 21.5, 1.0, Color(1, 0.957, 0.863, 0.2))
	var k := 16.0 / 10.0
	for bx in [1.5, 6.0]:
		_rbox(c.x - 8.0 + bx * k, c.y - 8.0 + 1.0 * k, 2.5 * k, 8.0 * k, CREAM, Color(0, 0, 0, 0), 0.0, 0.6 * k)


func _slot_state(sl: int) -> Dictionary:
	var k := me
	var rl := k.roll > 0.0
	var keys: Array = icons.keys()
	var rk: String = keys[int(floor(t * 14.0)) % keys.size()] if keys.size() > 0 else ""
	var s1: String = k.item if k.item != "" else (rk if rl else "")
	var s2: String = k.item2 if k.item2 != "" else (rk if rl and (k.item != "" or k.pend.size() > 1) else "")
	var held_sl := 0
	if not k.held.is_empty():
		held_sl = int(k.held["sl"])
		var free: String = k.item if k.item != "" else (rk if rl else "")
		if held_sl == 1:
			s1 = String(k.held["it"])
			s2 = free
		else:
			s2 = String(k.held["it"])
			s1 = free
	var it := s1 if sl == 1 else s2
	return {"it": it, "rolling": rl and sl == 1, "has": it != "" and not rl and held_sl != sl, "held": held_sl == sl}


func _draw_items(btn: float, top: float) -> void:
	var size := btn * 0.94
	var right := maxf(8.0, btn * 0.12)
	var y := 12.0 + top + 24.0
	for sl in [1, 2]:
		var st := _slot_state(sl)
		var x := W - 16.0 - right - size
		if sl == 2:
			x -= size + 12.0
		var c := Vector2(x + size / 2.0, y + size / 2.0)
		var a := 1.0 if (sl == 1 or bool(st["has"])) else 0.72
		var ring := Color(1, 0.957, 0.863, 0.85)
		if st["rolling"]:
			ring = CHEESE
			_draw_glow(c, size / 2.0 + 3.0, CHEESE, 0.4)
		elif st["has"]:
			ring = CHEESE
			_draw_glow(c, size / 2.0 + 3.0, CHEESE, 0.45 + 0.25 * (0.5 + 0.5 * sin(t * TAU / 1.2)))
		elif st["held"]:
			ring = Color(1, 0.957, 0.863, 0.35)
		draw_circle(_p(c + Vector2(0, 10)), (size / 2.0 + 4.0) * s, Color(0, 0, 0, 0.18 * a))
		draw_circle(_p(c), (size / 2.0 + 5.0) * s, Color(20.0 / 255, 10.0 / 255, 6.0 / 255, 0.55 * a))
		draw_circle(_p(c), (size / 2.0 + 3.0) * s, Color(ring.r, ring.g, ring.b, ring.a * a))
		draw_texture_rect(_ibtn_tex, Rect2(_p(c - Vector2(size, size) / 2.0), Vector2(size, size) * s), false, Color(1, 1, 1, a))
		var it: String = st["it"]
		if it != "" and icons.has(it):
			var isz := size * 0.62 * 1.18
			var ia := 0.38 if st["held"] else 1.0
			draw_texture_rect(icons[it], Rect2(_p(c - Vector2(isz, isz) / 2.0 + Vector2(0, 2)), Vector2(isz, isz) * s), false, Color(0, 0, 0, 0.35 * ia * a))
			draw_texture_rect(icons[it], Rect2(_p(c - Vector2(isz, isz) / 2.0), Vector2(isz, isz) * s), false, Color(1, 1, 1, ia * a))
			if st["held"]:
				_text(f_bold, "HELD", c.x - 30.0, y + size + 5.0, 10.0, Color(1, 0.957, 0.863, 0.75), HORIZONTAL_ALIGNMENT_CENTER, 60.0, Color(0, 0, 0, 0.8), Vector2(0, 1), 1.2)
		else:
			# empty: a faint dashed rounded square
			var e := size * 0.6
			_dashed_box(c - Vector2(e, e) / 2.0, e, 10.0, Color(1, 0.957, 0.863, (0.35 if sl == 1 else 0.3) * a))
		if pad_mode:
			_badge(Vector2(x + size - 6.0, y + size - 6.0), "A" if sl == 1 else "B", Color("#2f9a3e") if sl == 1 else Color("#d63a26"))


func _dashed_box(p: Vector2, w: float, r: float, col: Color) -> void:
	var pts := PackedVector2Array()
	var n := 40
	for i in n + 1:
		var u := float(i) / n
		var per := 4.0 * (w - 2.0 * r) + TAU * r
		var d := u * per
		pts.append(_rr_point(p, w, r, d))
	for i in range(0, n, 2):
		draw_line(_p(pts[i]), _p(pts[i + 1]), col, 2.0 * s, true)


static func _rr_point(p: Vector2, w: float, r: float, d: float) -> Vector2:
	var side := w - 2.0 * r
	var arc := PI / 2.0 * r
	var segs := [side, arc, side, arc, side, arc, side, arc]
	var i := 0
	while i < 8 and d > segs[i]:
		d -= segs[i]
		i += 1
	i = i % 8
	match i:
		0:
			return p + Vector2(r + d, 0)
		1:
			var a := -PI / 2.0 + d / r
			return p + Vector2(w - r, r) + Vector2(cos(a), sin(a)) * r
		2:
			return p + Vector2(w, r + d)
		3:
			var a2 := d / r
			return p + Vector2(w - r, w - r) + Vector2(cos(a2), sin(a2)) * r
		4:
			return p + Vector2(w - r - d, w)
		5:
			var a3 := PI / 2.0 + d / r
			return p + Vector2(r, w - r) + Vector2(cos(a3), sin(a3)) * r
		6:
			return p + Vector2(0, w - r - d)
		_:
			var a4 := PI + d / r
			return p + Vector2(r, r) + Vector2(cos(a4), sin(a4)) * r


func _badge(c: Vector2, txt: String, col: Color) -> void:
	draw_circle(_p(c), 10.0 * s, Color(1, 1, 1, 0.85))
	draw_circle(_p(c), 8.5 * s, col)
	_text(f_disp, txt, c.x - 10.0, c.y - 5.5, 10.0, Color.WHITE, HORIZONTAL_ALIGNMENT_CENTER, 20.0)


func _draw_special(btn: float, top: float) -> void:
	# the Special (ability) button and the Rear (look back) button, top left
	var size := btn * 0.95
	var x := maxf(8.0, btn * 0.12) + 16.0
	var y := 12.0 + top
	var c := Vector2(x + size / 2.0, y + size / 2.0)
	draw_circle(_p(c + Vector2(0, 10)), (size / 2.0 + 3.0) * s, Color(0, 0, 0, 0.2))
	_ring(c, size / 2.0 + 6.0 - 1.5, 3.0, Color(1, 1, 1, 0.14))
	draw_circle(_p(c), (size / 2.0 + 3.0) * s, Color(1, 0.957, 0.863, 0.35))
	draw_circle(_p(c), size / 2.0 * s, Color("#2a1810"))
	var tex: Texture2D = portraits.get(me.ri)
	if tex != null:
		var src := Rect2(tex.get_width() * (0.5 - 0.5 / 2.1), tex.get_height() * (0.28 - 0.28 / 2.1), tex.get_width() / 2.1, tex.get_height() / 2.1)
		draw_texture_rect_region(tex, Rect2(_p(c - Vector2(size, size) / 2.0), Vector2(size, size) * s), src)
	draw_circle(_p(c), size / 2.0 * s, Color(10.0 / 255, 5.0 / 255, 3.0 / 255, 0.55))
	var lw := f_disp.get_string_size("SPECIAL", HORIZONTAL_ALIGNMENT_LEFT, -1, int(11 * s)).x / s + 12.0
	_rbox(c.x - lw / 2.0, y + size - 7.0, lw, 15.0, Color(14.0 / 255, 7.0 / 255, 4.0 / 255, 0.85), Color(0, 0, 0, 0), 0.0, 8.0)
	_text(f_disp, "SPECIAL", c.x - lw / 2.0, y + size - 5.5, 11.0, CREAM, HORIZONTAL_ALIGNMENT_CENTER, lw, Color(0, 0, 0, 0), Vector2.ZERO, 0.66)
	if pad_mode:
		_badge(Vector2(x + size - 6.0, y + size - 6.0), "Y", Color("#e0a91a"))
	# rear-view button
	var ry := 12.0 + top + size + 20.0
	var rh := btn * 0.62
	var lb := look
	_rbox(x, ry, size, rh, Color(140.0 / 255, 220.0 / 255, 1.0, 0.32) if lb else Color(14.0 / 255, 7.0 / 255, 4.0 / 255, 0.34), Color("#bfe9ff") if lb else Color(1, 0.957, 0.863, 0.38), 1.5, 14.0, 7.0, Color(0, 0, 0, 0.25))
	# mirror icon: a rounded rectangle with a curved arrow
	var mw := size * 0.58
	var mh := mw * 0.48
	var mx := x + (size - mw) / 2.0
	var my := ry + rh / 2.0 - mh / 2.0 - 6.0
	_rbox(mx, my, mw, mh, Color(0, 0, 0, 0), CREAM, 2.0, mh * 0.35)
	draw_arc(_p(Vector2(mx + mw / 2.0, my + mh * 0.75)), mw * 0.22 * s, PI * 1.1, PI * 1.9, 12, Color(CREAM.r, CREAM.g, CREAM.b, 0.9), 2.0 * s, true)
	_text(f_disp, "REAR", x, my + mh + 4.0, 9.0, Color(1, 0.957, 0.863, 0.8), HORIZONTAL_ALIGNMENT_CENTER, size, Color(0, 0, 0, 0), Vector2.ZERO, 1.26)
	if pad_mode:
		_badge(Vector2(x + size - 6.0, ry + rh - 6.0), "X", Color("#2a7fd8"))


func _draw_gauge(btn: float) -> void:
	var gw := clampf(17.0 * _vmin(), 80.0, 112.0)
	var gh := gw * 84.0 / 120.0
	var gx := 16.0 + btn * 1.25 + 70.0
	var gy := H - 14.0 - gh
	var k := gw / 120.0
	var c := Vector2(gx + 60.0 * k, gy + 50.0 * k)
	var a0 := deg_to_rad(150.0)
	var sweep := deg_to_rad(240.0)
	# track and value
	draw_arc(_p(c), 46.0 * k * s, a0, a0 + sweep, 48, Color(20.0 / 255, 10.0 / 255, 6.0 / 255, 0.6), 9.0 * k * s, true)
	var ga := clampf(maxf(0.0, me.speed) / (me.base_max * 1.58), 0.0, 1.0)
	if ga > 0.005:
		var n := 32
		var boost := me.boost > 0.0
		for i in n:
			var f0 := float(i) / n * ga
			var f1 := float(i + 1) / n * ga
			var col := Color("#9ae8ff") if boost else _gauge_col(f0 + (f1 - f0) * 0.5)
			draw_arc(_p(c), 46.0 * k * s, a0 + sweep * f0, a0 + sweep * f1 + 0.01, 3, col, 7.0 * k * s, true)
		draw_circle(_p(c + Vector2(cos(a0), sin(a0)) * 46.0 * k), 3.5 * k * s, _gauge_col(0.0) if not boost else Color("#9ae8ff"))
		var ae := a0 + sweep * ga
		draw_circle(_p(c + Vector2(cos(ae), sin(ae)) * 46.0 * k), 3.5 * k * s, _gauge_col(ga) if not boost else Color("#9ae8ff"))
	# inner ring: drift charge
	draw_arc(_p(c), 36.0 * k * s, a0, a0 + sweep, 40, Color(1, 0.957, 0.863, 0.1), 3.0 * k * s, true)
	if me.drift != 0:
		var ch := minf(1.0, me.charge / 2.6)
		if ch > 0.005:
			draw_arc(_p(c), 36.0 * k * s, a0, a0 + sweep * ch, 32, SPARK_TIER[clampi(me.tier, 0, 3)], 3.0 * k * s, true)
	# number
	var ns := clampf(5.0 * _vmin(), 20.0, 32.0)
	var num := str(int(round(maxf(0.0, me.speed) * 0.66)))
	var top := gy + gh * 0.38
	var nw := f_disp.get_string_size(num, HORIZONTAL_ALIGNMENT_LEFT, -1, int(ns * s)).x / s
	_rbox(c.x - maxf(nw, ns * 0.7) / 2.0 - 6.0, top - 2.0, maxf(nw, ns * 0.7) + 12.0, ns + 2.0, Color(20.0 / 255, 10.0 / 255, 6.0 / 255, 0.55), Color(0, 0, 0, 0), 0.0, 6.0)
	_text(f_disp, num, gx, top, ns, CREAM, HORIZONTAL_ALIGNMENT_CENTER, gw, Color(0, 0, 0, 0.7), Vector2(0, 2))
	_text(f_bold, "MPH", gx, top + ns + 2.0, 9.0, MUTED, HORIZONTAL_ALIGNMENT_CENTER, gw, Color(0, 0, 0, 0), Vector2.ZERO, 1.8)


static func _gauge_col(f: float) -> Color:
	if f < 0.5:
		return Color("#ffe9a0").lerp(Color("#ff9a1f"), f / 0.5)
	return Color("#ff9a1f").lerp(Color("#e0452c"), (f - 0.5) / 0.5)


func _draw_pedals(btn: float) -> void:
	var pw := btn * 1.85
	var ph := btn * 0.92
	var y := H - 14.0 + 6.0 - ph
	var drifting := me.drift != 0 or me.d_latch
	for side in [0, 1]:
		var x := 16.0 + 4.0 if side == 0 else W - 16.0 - 4.0 - pw
		var bg := Color(30.0 / 255, 15.0 / 255, 9.0 / 255, 0.34)
		var bd := Color(1, 0.957, 0.863, 0.34)
		if drifting:
			bg = Color("#ff8a1f")
			bd = CREAM
		elif braking:
			bg = Color(224.0 / 255, 69.0 / 255, 44.0 / 255, 0.5)
		if drifting:
			_draw_glow_rect(x, y, pw, ph, Color(1, 0.48, 0.1), 0.5)
		_rbox(x, y, pw, ph, bg, bd, 1.5, 16.0, 8.0, Color(0, 0, 0, 0.3), 10.0)
		# a soft top sheen
		_rbox(x + 1.5, y + 1.5, pw - 3.0, ph * 0.35, Color(1, 1, 1, 0.07), Color(0, 0, 0, 0), 0.0, 14.0, 0.0, Color(0, 0, 0, 0), 2.0)
		var cy := y + ph / 2.0
		var dw := f_disp.get_string_size("DRIFT", HORIZONTAL_ALIGNMENT_LEFT, -1, int(15 * s)).x / s
		var bw := f_bold.get_string_size("BRAKE", HORIZONTAL_ALIGNMENT_LEFT, -1, int(9 * s)).x / s + 9.0 * 0.14 * 5.0
		var icon := 22.0
		var total := icon + 6.0 + dw + 6.0 + bw
		var tx := x + (pw - total) / 2.0
		# drift icon: a curved arrow
		var ic := Vector2(tx + icon / 2.0, cy)
		var icol := Color.WHITE if drifting else CHEESE
		draw_arc(_p(ic + Vector2(icon * 0.1, icon * 0.3)), icon * 0.42 * s, PI * 1.0, PI * 1.6, 10, icol, 2.6 * s, true)
		var tip := ic + Vector2(icon * 0.1, icon * 0.3) + Vector2(cos(PI * 1.6), sin(PI * 1.6)) * icon * 0.42
		draw_line(_p(tip), _p(tip + Vector2(-5, -1)), icol, 2.6 * s, true)
		draw_line(_p(tip), _p(tip + Vector2(-1, 5)), icol, 2.6 * s, true)
		_text(f_disp, "DRIFT", tx + icon + 6.0, cy - 15.0 * 0.45, 15.0, Color.WHITE if drifting else CREAM, HORIZONTAL_ALIGNMENT_LEFT, -1.0, Color(0, 0, 0, 0.6), Vector2(0, 2), 0.6)
		_text(f_bold, "BRAKE", tx + icon + 6.0 + dw + 6.0, cy - 9.0 * 0.45, 9.0, Color("#5a2206") if drifting else MUTED, HORIZONTAL_ALIGNMENT_LEFT, -1.0, Color(0, 0, 0, 0.6), Vector2(0, 1), 1.26)
		if pad_mode:
			_badge(Vector2(x + pw - 16.0, y + ph - 16.0), "LT", Color("#555555"))


func _draw_glow_rect(x: float, y: float, w: float, h: float, col: Color, a: float) -> void:
	for i in 5:
		var g := float(i + 1) * 3.0
		_rbox(x - g, y - g, w + 2.0 * g, h + 2.0 * g, Color(col.r, col.g, col.b, a * 0.1 * (1.0 - float(i) / 5.0)), Color(0, 0, 0, 0), 0.0, 16.0 + g)


## screen rectangles for clicks and touches
func pedal_rect(side: int) -> Rect2:
	var btn := _btn()
	var pw := btn * 1.85
	var ph := btn * 0.92
	var y := H - 14.0 + 6.0 - ph
	var x := 16.0 + 4.0 if side == 0 else W - 16.0 - 4.0 - pw
	return Rect2(Vector2(x, y) * s, Vector2(pw, ph) * s)


func pause_rect() -> Rect2:
	return Rect2(Vector2(W - 16.0 - 44.0, 12.0) * s, Vector2(44, 44) * s)


func item_rect(sl: int) -> Rect2:
	var btn := _btn()
	var size := btn * 0.94
	var x := W - 16.0 - maxf(8.0, btn * 0.12) - size
	if sl == 2:
		x -= size + 12.0
	return Rect2(Vector2(x, 12.0 + _hud_top() + 24.0) * s, Vector2(size, size) * s)


static func _fmt(tm: float) -> String:
	var m := int(tm / 60.0)
	var sec := tm - m * 60.0
	return "%d:%05.2f" % [m, sec]
