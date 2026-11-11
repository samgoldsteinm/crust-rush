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
# "you got them" (web hitToast): the item you used, an arrow and the portraits of whoever it hit, bottom centre
var ht_key := ""
var ht_t := 0.0
var ht_in := 0.0
var ht_who: Array = []          # [portrait texture or null, ring colour]
var ht_icon: Texture2D = null
var ht_col := Color.WHITE       # an ability's colour when it has no icon
# an item heading your way (web #incoming): its icon in a pulsing ring, an arrow toward it
var inc_icon: Texture2D = null
var inc_col := Color.WHITE
var inc_ang := 0.0
var inc_near := 0.0
var inc_on := false
var hitfx_t := 0.0
var abfx_t := 0.0
var abfx_col := Color.WHITE
var heat_t := 0.0
var kmh := false
var pb_text := ""
var td := {}              # the TESTING cheat: {on, show, sec, take, skip} (web #tdTag / #tdBar)
var td_take_r := Rect2()
var td_skip_r := Rect2()         # under the lap time: your best on this track and class (web #hudPB)
var fps_on := false
var sauce_a := 0.0        # the sauce smears on the screen (web .saucefx): on at once, fading over 1.6 s
var sauce_blobs: Array = []
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
	texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
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


func hit_toast(key: String, icon: Texture2D, col: Color, portrait: Texture2D, ring: Color) -> void:
	var same := ht_t > 0.4 and key == ht_key
	ht_key = key
	ht_icon = icon
	ht_col = col
	if not same:
		ht_who.clear()
		ht_in = 0.22
	for w in ht_who:
		if w[0] == portrait and w[1] == ring:
			ht_t = 1.9
			return
	ht_who.append([portrait, ring])
	ht_t = 1.9


func toast(text: String, dur := 1.2) -> void:
	toast_text = text
	toast_t = dur


## sauce on the screen: soft-edged red splats, darker at the rim
func _draw_sauce() -> void:
	var vs := get_viewport_rect().size
	var vmin := minf(vs.x, vs.y)
	for b in sauce_blobs:
		var c := Vector2(float(b[0]) * vs.x, float(b[1]) * vs.y)
		var r := float(b[2]) * vmin * 0.5
		var rot := float(b[3])
		for ring in 5:
			var f := 1.0 - float(ring) / 5.0
			var col := Color(0.94, 0.31, 0.2).lerp(Color(0.47, 0.04, 0.02), f)
			var pts := PackedVector2Array()
			for i in 28:
				var an := TAU * i / 28.0
				var wob := 1.0 + 0.08 * sin(an * 3.0 + rot) + 0.05 * sin(an * 5.0 - rot)
				pts.append(c + Vector2(cos(an), sin(an) * 0.8).rotated(rot) * r * f * wob)
			draw_colored_polygon(pts, Color(col.r, col.g, col.b, 0.92 * sauce_a))


func hit_flash() -> void:
	hitfx_t = 0.6


## web heatFlash: the edges glow oven-orange and fade over 0.9 s
func heat_flash() -> void:
	heat_t = 0.9


## web sauceFx(true): nine splats of sauce, placed at random each race
func sauce_on() -> void:
	if sauce_blobs.is_empty():
		for i in 9:
			sauce_blobs.append([0.10 + randf() * 0.80, 0.10 + randf() * 0.70, 0.10 + randf() * 0.16, randf() * TAU])
	sauce_a = 1.0


## web abilFlash: the screen's edges glow in the ability's colour (an inset 30px + 120px blur shadow) and fade over 0.9 s
func abil_flash(c: Color) -> void:
	abfx_t = 0.9
	abfx_col = c


# ---------------------------------------------------------------- per frame

func tick(dt: float) -> void:
	t += dt
	if banner_t > 0.0:
		banner_t -= dt
		if banner_t <= 0.0:
			banner_text = ""
	if toast_t > 0.0:
		toast_t -= dt
	if ht_t > 0.0:
		ht_t -= dt
	if ht_in > 0.0:
		ht_in -= dt
	if hitfx_t > 0.0:
		hitfx_t -= dt
	if abfx_t > 0.0:
		abfx_t -= dt
	if heat_t > 0.0:
		heat_t -= dt
	if me != null and me.sauce_t > 0.0 and sauce_a > 0.0:
		sauce_a = 1.0
	elif sauce_a > 0.0:
		sauce_a = maxf(0.0, sauce_a - dt / 1.6)
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
	var pb_size := clampf(2.2 * _vmin(), 11.0, 14.0)
	if pb_text != "":
		lap_h += pb_size * 1.2
		row_w = maxf(row_w, f_bold.get_string_size(pb_text, HORIZONTAL_ALIGNMENT_LEFT, -1, int(pb_size)).x)
	var bar_h := maxf(pos_size * 0.85, lap_h)
	var tb_x := x0 + pos_w + 12.0
	var tb_w := tl_w - pos_w - lap_w - 24.0
	return {"x0": x0, "w": tl_w, "y0": 12.0, "h": bar_h, "pos_size": pos_size, "suf_size": suf_size, "num": num, "num_w": num_w,
		"tb_x": tb_x, "tb_w": tb_w, "lap_x": tb_x + tb_w + 12.0, "lap_w": lap_w, "lap_h": lap_h, "lap_big": lap_big, "time_size": time_size, "lap_txt": lap_txt, "pb_size": pb_size}


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


## a CSS linear-gradient(180deg, ...) box with rounded corners, drawn as thin horizontal slices
## stops: [[offset 0..1, Color], ...]; rt/rb: top and bottom corner radii (CSS px)
func _vgrad(x: float, y: float, w: float, h: float, rt: float, rb: float, stops: Array) -> void:
	var rows := maxi(2, int(ceil(h * s)))
	var dy := h / rows
	for i in rows:
		var yy := y + i * dy
		var f := (i + 0.5) / rows
		var col: Color = stops[0][1]
		for j in range(1, stops.size()):
			var a: Array = stops[j - 1]
			var b: Array = stops[j]
			if f <= float(b[0]):
				col = (a[1] as Color).lerp(b[1], clampf((f - float(a[0])) / maxf(1e-4, float(b[0]) - float(a[0])), 0.0, 1.0))
				break
			col = b[1]
		# the inset of the rounded corners at this row
		var ins := 0.0
		var ym := yy + dy * 0.5 - y
		if ym < rt:
			var d := rt - ym
			ins = rt - sqrt(maxf(0.0, rt * rt - d * d))
		elif ym > h - rb:
			var d2 := ym - (h - rb)
			ins = rb - sqrt(maxf(0.0, rb * rb - d2 * d2))
		draw_rect(Rect2(_p(Vector2(x + ins, yy)), Vector2(w - 2.0 * ins, dy + 0.02) * s), col)


## just the border (and outer shadow) of a rounded box
func _rborder(x: float, y: float, w: float, h: float, border: Color, bw: float, rt: float, rb: float) -> void:
	var sb := StyleBoxFlat.new()
	sb.draw_center = false
	sb.border_color = border
	sb.set_border_width_all(maxi(1, int(round(bw * s))))
	sb.corner_radius_top_left = int(rt * s)
	sb.corner_radius_top_right = int(rt * s)
	sb.corner_radius_bottom_left = int(rb * s)
	sb.corner_radius_bottom_right = int(rb * s)
	sb.anti_aliasing = true
	draw_style_box(sb, Rect2(_p(Vector2(x, y)), Vector2(w, h) * s))


## a cubic Bezier as points (for the SVG icons)
static func _bez(p0: Vector2, p1: Vector2, p2: Vector2, p3: Vector2, n := 12) -> PackedVector2Array:
	var out := PackedVector2Array()
	for i in n + 1:
		var u := float(i) / n
		var v := 1.0 - u
		out.append(p0 * v * v * v + p1 * 3.0 * v * v * u + p2 * 3.0 * v * u * u + p3 * u * u * u)
	return out


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
	if sauce_a > 0.0:
		_draw_sauce()
	if bool(td.get("on", false)):
		_draw_td()
	if fps_on:
		_text(f_bold, "%d fps" % Engine.get_frames_per_second(), 10.0, 5.0, 12.0, Color(1, 1, 1, 0.72), HORIZONTAL_ALIGNMENT_LEFT, -1.0, Color(0, 0, 0, 0.45), Vector2(0, 1), 1.0)
	if heat_t > 0.0:
		var hv := get_viewport_rect().size
		var ha := clampf(heat_t / 0.9, 0.0, 1.0)
		for i in 18:
			var f := float(i) / 18.0
			draw_rect(Rect2(Vector2.ZERO, hv).grow(-f * hv.y * 0.42), Color(1.0, 0.43, 0.08, 0.55 * ha * (1.0 - f) * 0.16), false, hv.y * 0.025)
	if abfx_t > 0.0:
		var u := 1.0 - clampf(abfx_t / 0.9, 0.0, 1.0)
		var op := (1.0 - u) * (1.0 - u)
		var vs2 := get_viewport_rect().size
		var bw := 7.0
		for i in 22:
			var d := (float(i) + 0.5) * bw
			var al := op / (1.0 + exp(1.702 * (d - 30.0) / 60.0))
			draw_rect(Rect2(Vector2.ZERO, vs2).grow(-(d * s)), Color(abfx_col.r, abfx_col.g, abfx_col.b, al), false, bw * s)
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
	_draw_incoming(vmin)
	_draw_hit_toast(btn)
	# toast (bottom centre)
	if toast_t > 0.0 and toast_text != "":
		var ts := 18.0
		var tw2 := f_bold.get_string_size(toast_text, HORIZONTAL_ALIGNMENT_LEFT, -1, int(ts * s)).x / s
		var a2 := clampf(toast_t / 0.25, 0.0, 1.0)
		var y2 := H - 14.0 - (btn * 0.35 + 12.0) - 46.0
		_rbox(W / 2.0 - tw2 / 2.0 - 20.0, y2, tw2 + 40.0, 46.0, Color(14.0 / 255, 7.0 / 255, 4.0 / 255, 0.55 * a2), Color(1, 0.957, 0.863, 0.3 * a2), 1.0, 23.0)
		_text(f_bold, toast_text, W / 2.0 - tw2 / 2.0, y2 + 12.0, ts, Color(CREAM.r, CREAM.g, CREAM.b, a2))


## web .hittoast (the pointer-fine size): a dark pill, the item, a cheese arrow, round portraits ringed in each
## victim's colour; it slides up in and stays 1.9 s
func _draw_hit_toast(btn: float) -> void:
	if ht_t <= 0.0 or ht_who.is_empty():
		return
	var a := clampf(ht_t / 0.2, 0.0, 1.0)
	var slide := clampf(ht_in / 0.22, 0.0, 1.0)
	a *= 1.0 - slide
	var isz := 54.0
	var psz := 50.0
	var gap := 12.0
	var aw := 22.0
	var w := 20.0 + isz + gap + aw + gap + ht_who.size() * psz + (ht_who.size() - 1) * 4.0 + 20.0
	var h := 10.0 + isz + 10.0
	var x0 := W / 2.0 - w / 2.0
	var y0 := H - (btn * 0.35 + 12.0) - h + slide * 14.0
	_rbox(x0, y0, w, h, Color(14.0 / 255, 7.0 / 255, 4.0 / 255, 0.55 * a), Color(1, 0.957, 0.863, 0.3 * a), 1.0, h / 2.0)
	var cx := x0 + 20.0
	var cy := y0 + h / 2.0
	if ht_icon != null:
		draw_texture_rect(ht_icon, Rect2(_p(Vector2(cx, cy - isz / 2.0)), Vector2(isz, isz) * s), false, Color(1, 1, 1, a))
	else:
		draw_circle(_p(Vector2(cx + isz / 2.0, cy)), isz * 0.35 * s, Color(ht_col.r, ht_col.g, ht_col.b, a), true, -1.0, true)
	cx += isz + gap
	_text(f_bold, "▶", cx, cy - 13.0, aw, Color(CHEESE.r, CHEESE.g, CHEESE.b, a))
	cx += aw + gap
	for wv in ht_who:
		var c := _p(Vector2(cx + psz / 2.0, cy))
		var rc: Color = wv[1]
		draw_circle(c, (psz / 2.0 + 2.0) * s, Color(rc.r, rc.g, rc.b, a), true, -1.0, true)
		draw_circle(c, psz / 2.0 * s, Color(42.0 / 255, 24.0 / 255, 16.0 / 255, a), true, -1.0, true)
		var pt: Texture2D = wv[0]
		if pt != null:
			# background-size 230%, position 50% 26%: the face, cropped into the circle
			var tw := float(pt.get_width())
			var th := float(pt.get_height())
			var src_w := tw / 2.3
			var src := Rect2((tw - src_w) * 0.5, (th - src_w * th / tw) * 0.26, src_w, src_w * th / tw)
			var pts := PackedVector2Array()
			var uvs := PackedVector2Array()
			for k in 28:
				var an := TAU * k / 28.0
				var d := Vector2(cos(an), sin(an))
				pts.append(c + d * psz / 2.0 * s)
				var u := Vector2(0.5, 0.5) + d * 0.5
				uvs.append(Vector2((src.position.x + u.x * src.size.x) / tw, (src.position.y + u.y * src.size.y) / th))
			draw_colored_polygon(pts, Color(1, 1, 1, a), uvs, pt)
		cx += psz + 4.0


## web #incoming: bottom 26% of the screen, 13vmin across (56-84 px); a cream disc ringed in the item's colour, its
## icon, and an arrow pointing where it is coming from (straight down: right behind you); it pulses faster as it closes
func _draw_incoming(vmin: float) -> void:
	if not inc_on or inc_icon == null:
		return
	var sz := clampf(13.0 * vmin, 56.0, 84.0)
	var per := 0.6 - 0.45 * inc_near
	var ph := 0.5 + 0.5 * sin(t * TAU / maxf(0.15, per * 2.0))
	var sc := lerpf(0.92, 1.1, ph)
	var c := Vector2(W / 2.0, H - H * 0.26 - sz / 2.0)
	var r := sz / 2.0 * sc
	var pc := _p(c)
	draw_circle(pc, (r + 7.0) * s, Color(20.0 / 255, 10.0 / 255, 6.0 / 255, 0.55), true, -1.0, true)
	draw_circle(pc, (r + 4.0) * s, inc_col, true, -1.0, true)
	for i in 6:
		var f := float(i) / 6.0
		draw_circle(pc, r * (1.0 - f * 0.28) * s, Color(1, 0.957 + 0.043 * f, 0.863 + 0.137 * f, 0.85 + 0.1 * f), true, -1.0, true)
	var isz := r * 2.0 * 0.72
	draw_texture_rect(inc_icon, Rect2(_p(c - Vector2(isz, isz) / 2.0), Vector2(isz, isz) * s), false)
	# the arrow on the rim, pointing out toward the threat
	var dir := Vector2(cos(inc_ang), sin(inc_ang))
	var tip := c + dir * (r + 22.0)
	var base := c + dir * (r + 8.0)
	var side := Vector2(-dir.y, dir.x) * 10.0
	draw_colored_polygon(PackedVector2Array([_p(tip), _p(base + side), _p(base - side)]), inc_col)


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
	# linear-gradient(160deg, rgba(40,22,14,.78), rgba(14,7,4,.62)), 0 8px 20px rgba(0,0,0,.28)
	_rbox(lx, ly + 2.0, lw, lh, Color(0, 0, 0, 0), Color(0, 0, 0, 0), 0.0, 12.0, 10.0, Color(0, 0, 0, 0.26))
	_vgrad(lx, ly, lw, lh, 12.0, 12.0, [[0.0, Color(40.0 / 255, 22.0 / 255, 14.0 / 255, 0.78)], [1.0, Color(14.0 / 255, 7.0 / 255, 4.0 / 255, 0.62)]])
	_vgrad(lx + 6.0, ly + 1.0, lw - 12.0, 1.0, 0.0, 0.0, [[0.0, Color(1, 1, 1, 0.08)], [1.0, Color(1, 1, 1, 0.08)]])
	_rborder(lx, ly, lw, lh, Color(1, 0.957, 0.863, 0.16), 1.0, 12.0, 12.0)
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
	if pb_text != "":
		var pbs: float = tb["pb_size"]
		_text(f_bold, pb_text, lx + 10.0, ly + 4.0 + lb * 1.15 + 1.0 + tsz * 1.2, pbs, Color(1, 0.957, 0.863, 0.75), HORIZONTAL_ALIGNMENT_LEFT, -1.0, Color(0, 0, 0, 0.7), Vector2(0, 2))


func _racer_col(k: Kart) -> Color:
	if k.ri < racer_cols.size():
		return racer_cols[k.ri]
	return Color.WHITE


func _draw_glow(c: Vector2, r: float, col: Color, a: float) -> void:
	for i in 6:
		var f := float(i) / 6.0
		draw_circle(_p(c), (r + f * 8.0) * s, Color(col.r, col.g, col.b, a * 0.12 * (1.0 - f)), true, -1.0, true)


func _marker(k: Kart, x: float, y: float, r: float, ring: float, ring_col: Color) -> void:
	_soft_shadow(Vector2(x, y), r + ring, 1.5, 3.0, 0.35)
	draw_circle(_p(Vector2(x, y)), (r + ring) * s, ring_col, true, -1.0, true)
	draw_circle(_p(Vector2(x, y)), r * s, Color("#2a1810"), true, -1.0, true)
	var tex: Texture2D = portraits.get(k.ri)
	if tex != null:
		# background-size 230%, centred at 50% 26%: the face fills the disc
		var src := _bg_src(tex, 2.3, 0.26)
		_disc_tex(tex, Vector2(x, y), r, src)


## the part of a portrait a round button shows with the web's `background-size: <k*100>%; background-position: 50% <py>`:
## the picture is scaled to k times the button's width (its height follows its own shape), so the button shows a
## square of the picture's width / k. (Scaling both sides by k squashed the wide portraits: the special button's face.)
static func _bg_src(tex: Texture2D, k: float, py: float) -> Rect2:
	var tw := float(tex.get_width())
	var th := float(tex.get_height())
	var side := minf(tw / k, th)
	return Rect2((tw - side) * 0.5, (th - side) * py, side, side)


## a soft drop shadow under a round button (the web's box-shadow 0 <off>px <blur>px): rings fading out, no hard edge
func _soft_shadow(c: Vector2, r: float, off: float, blur: float, a: float) -> void:
	var n := 10
	for i in n:
		var f := float(i) / float(n - 1)
		draw_circle(_p(c + Vector2(0, off)), (r - blur * 0.35 + blur * 1.1 * f) * s, Color(0, 0, 0, a / float(n) * 1.6 * (1.0 - f * 0.5)), true, -1.0, true)


## a portrait cut to a circle (the web's border-radius: 50% with a background image)
func _disc_tex(tex: Texture2D, c: Vector2, r: float, src: Rect2) -> void:
	var n := 40
	var pts := PackedVector2Array()
	var uvs := PackedVector2Array()
	var tw := float(tex.get_width())
	var th := float(tex.get_height())
	for i in n:
		var a := TAU * i / n
		var d := Vector2(cos(a), sin(a))
		pts.append(_p(c + d * r))
		uvs.append(Vector2((src.position.x + (0.5 + 0.5 * d.x) * src.size.x) / tw, (src.position.y + (0.5 + 0.5 * d.y) * src.size.y) / th))
	draw_polygon(pts, PackedColorArray([Color.WHITE]), uvs, tex)


func _draw_pause() -> void:
	var c := Vector2(W - 16.0 - 22.0, 12.0 + 22.0)
	_soft_shadow(c, 22.0, 3.0, 8.0, 0.18)
	draw_circle(_p(c), 22.0 * s, Color(29.0 / 255, 15.0 / 255, 9.0 / 255, 0.75), true, -1.0, true)
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
		_soft_shadow(c, size / 2.0 + 3.0, 8.0, 18.0, 0.22 * a)
		draw_circle(_p(c), (size / 2.0 + 5.0) * s, Color(20.0 / 255, 10.0 / 255, 6.0 / 255, 0.55 * a), true, -1.0, true)
		draw_circle(_p(c), (size / 2.0 + 3.0) * s, Color(ring.r, ring.g, ring.b, ring.a * a), true, -1.0, true)
		draw_texture_rect(_ibtn_tex, Rect2(_p(c - Vector2(size, size) / 2.0), Vector2(size, size) * s), false, Color(1, 1, 1, a))
		var it: String = st["it"]
		if it != "" and icons.has(it):
			var isz := size * 0.62 * 1.18
			var ia := 0.38 if st["held"] else 1.0
			draw_texture_rect(icons[it], Rect2(_p(c - Vector2(isz, isz) / 2.0 + Vector2(0, 2)), Vector2(isz, isz) * s), false, Color(0, 0, 0, 0.35 * ia * a))
			draw_texture_rect(icons[it], Rect2(_p(c - Vector2(isz, isz) / 2.0), Vector2(isz, isz) * s), false, Color(1, 1, 1, ia * a))
			if st["held"]:
				_text(f_bold, "HELD", c.x - 30.0, y + size + 5.0, 10.0, Color(1, 0.957, 0.863, 0.75), HORIZONTAL_ALIGNMENT_CENTER, 60.0, Color(0, 0, 0, 0.8), Vector2(0, 1), 1.2)
		# (empty: just the round slot; the web's faint dashed square inside is left out)
		if pad_mode:
			_badge(Vector2(x + size - 6.0, y + size - 6.0), "A" if sl == 1 else "B", Color("#3fa641") if sl == 1 else Color("#d93a2f"))


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


## a controller button badge (web .ph): a 20 px disc in the button's colour with a 1.5 px white rim and a soft drop
## shadow, the letter in Bungee centred on it (dark on the yellow Y)
func _badge(c: Vector2, txt: String, col: Color) -> void:
	_soft_shadow(c, 10.0, 2.0, 6.0, 0.5)
	draw_circle(_p(c), 10.0 * s, Color(1, 1, 1, 0.85), true, -1.0, true)
	draw_circle(_p(c), 8.5 * s, col, true, -1.0, true)
	var fs := int(round(10.0 * s))
	var ink := Color("#1a0c06") if txt == "Y" else Color.WHITE
	var tw := f_disp.get_string_size(txt, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
	# the baseline half a capital below the centre (Bungee's capitals are about .72 of the size)
	draw_string(f_disp, _p(c) + Vector2(-tw * 0.5, float(fs) * 0.36), txt, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, ink)


func _draw_special(btn: float, top: float) -> void:
	# the Special (ability) button and the Rear (look back) button, top left
	var size := btn * 0.95
	var x := maxf(8.0, btn * 0.12) + 16.0
	var y := 12.0 + top
	var c := Vector2(x + size / 2.0, y + size / 2.0)
	# web .abtn: the driver's face, a charge ring in the ability's colour (conic, from the top), lit up when ready
	var ac := Color(String(Race.ABIL.get(me.racer_name.to_lower(), ["", "", "#ffe066"])[2]))
	var chg := clampf(me.ab_c, 0.0, 1.0)
	var ready := chg >= 0.999
	_soft_shadow(c, size / 2.0 + 3.0, 8.0, 18.0, 0.24)
	if ready:
		var pulse := 0.6 + 0.4 * sin(t * TAU)
		_draw_glow(c, size / 2.0 + 4.0, ac, 0.55 * pulse)
	var R := size / 2.0 + 6.0
	var rw := R * 0.123
	_ring(c, R - rw / 2.0, rw, Color(1, 1, 1, 0.14))
	if chg > 0.002:
		draw_arc(_p(c), (R - rw / 2.0) * s, -PI / 2.0, -PI / 2.0 + TAU * chg, maxi(8, int(64 * chg)), ac, rw * s, true)
	draw_circle(_p(c), (size / 2.0 + 3.0) * s, ac if ready else Color(1, 0.957, 0.863, 0.35), true, -1.0, true)
	draw_circle(_p(c), size / 2.0 * s, Color("#2a1810"), true, -1.0, true)
	var tex: Texture2D = portraits.get(me.ri)
	if tex != null:
		var src := _bg_src(tex, 2.1, 0.28)
		_disc_tex(tex, c, size / 2.0, src)
	if not ready:
		draw_circle(_p(c), size / 2.0 * s, Color(10.0 / 255, 5.0 / 255, 3.0 / 255, 0.55), true, -1.0, true)
	var lw := f_disp.get_string_size("SPECIAL", HORIZONTAL_ALIGNMENT_LEFT, -1, int(11 * s)).x / s + 12.0
	_rbox(c.x - lw / 2.0, y + size - 7.0, lw, 15.0, ac if ready else Color(14.0 / 255, 7.0 / 255, 4.0 / 255, 0.85), Color(0, 0, 0, 0), 0.0, 8.0)
	_text(f_disp, "SPECIAL", c.x - lw / 2.0, y + size - 5.5, 11.0, Color("#1a0c06") if ready else CREAM, HORIZONTAL_ALIGNMENT_CENTER, lw, Color(0, 0, 0, 0), Vector2.ZERO, 0.66)
	if pad_mode:
		_badge(Vector2(x + size - 6.0, y + size - 6.0), "Y", Color("#e0b020"))
	# rear-view button
	var ry := 12.0 + top + size + 20.0
	var rh := btn * 0.62
	var lb := look
	_rbox(x, ry, size, rh, Color(140.0 / 255, 220.0 / 255, 1.0, 0.32) if lb else Color(14.0 / 255, 7.0 / 255, 4.0 / 255, 0.34), Color("#bfe9ff") if lb else Color(1, 0.957, 0.863, 0.38), 1.5, 14.0, 7.0, Color(0, 0, 0, 0.25))
	# the mirror (svg 48x30): blue glass in a cream frame, a reflection arc, two glints, the stem
	var mw := size * 0.58
	var k := mw / 48.0
	var mh := 30.0 * k
	var mx := x + (size - mw) / 2.0
	var my := ry + (rh - (mh + 1.0 + 9.0)) / 2.0
	_rbox(mx + 2.0 * k, my + 3.0 * k, 44.0 * k, 22.0 * k, Color(140.0 / 255, 220.0 / 255, 1.0, 0.55), CREAM, 2.4 * k, 7.0 * k)
	var arc := PackedVector2Array()
	for i in 13:
		var u := float(i) / 12.0
		var q := Vector2(8, 20) * (1.0 - u) * (1.0 - u) + Vector2(24, 6) * 2.0 * u * (1.0 - u) + Vector2(40, 20) * u * u
		arc.append(_p(Vector2(mx, my) + q * k))
	draw_polyline(arc, Color(1, 1, 1, 0.7), 2.0 * k * s, true)
	draw_line(_p(Vector2(mx, my) + Vector2(14, 8) * k), _p(Vector2(mx, my) + Vector2(8, 18) * k), Color(1, 1, 1, 0.55), 2.0 * k * s, true)
	draw_line(_p(Vector2(mx, my) + Vector2(20, 8) * k), _p(Vector2(mx, my) + Vector2(11, 23) * k), Color(1, 1, 1, 0.55), 2.0 * k * s, true)
	_rbox(mx + 20.0 * k, my + 25.0 * k, 8.0 * k, 4.0 * k, CREAM, Color(0, 0, 0, 0), 0.0, 1.5 * k)
	_text(f_disp, "REAR", x, my + mh + 1.0, 9.0, Color(1, 0.957, 0.863, 0.8), HORIZONTAL_ALIGNMENT_CENTER, size, Color(0, 0, 0, 0), Vector2.ZERO, 1.26)
	if pad_mode:
		_badge(Vector2(x + size - 6.0, ry + rh - 6.0), "X", Color("#2f7fd8"))


func _draw_gauge(btn: float) -> void:
	var gw := clampf(17.0 * _vmin(), 80.0, 112.0)
	var gh := gw * 84.0 / 120.0
	var gx := (16.0 + btn * 1.25 + 70.0) if show_touch else 14.0
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
		draw_circle(_p(c + Vector2(cos(a0), sin(a0)) * 46.0 * k), 3.5 * k * s, _gauge_col(0.0) if not boost else Color("#9ae8ff"), true, -1.0, true)
		var ae := a0 + sweep * ga
		draw_circle(_p(c + Vector2(cos(ae), sin(ae)) * 46.0 * k), 3.5 * k * s, _gauge_col(ga) if not boost else Color("#9ae8ff"), true, -1.0, true)
	# inner ring: drift charge
	draw_arc(_p(c), 36.0 * k * s, a0, a0 + sweep, 40, Color(1, 0.957, 0.863, 0.1), 3.0 * k * s, true)
	if me.drift != 0:
		var ch := minf(1.0, me.charge / 2.6)
		if ch > 0.005:
			draw_arc(_p(c), 36.0 * k * s, a0, a0 + sweep * ch, 32, SPARK_TIER[clampi(me.tier, 0, 3)], 3.0 * k * s, true)
	# number
	var ns := clampf(5.0 * _vmin(), 20.0, 32.0)
	var num := str(int(round(maxf(0.0, me.speed) * 0.66 * (1.609 if kmh else 1.0))))
	var top := gy + gh * 0.38
	var nw := f_disp.get_string_size(num, HORIZONTAL_ALIGNMENT_LEFT, -1, int(ns * s)).x / s
	_rbox(c.x - maxf(nw, ns * 0.7) / 2.0 - 6.0, top - 2.0, maxf(nw, ns * 0.7) + 12.0, ns + 2.0, Color(20.0 / 255, 10.0 / 255, 6.0 / 255, 0.55), Color(0, 0, 0, 0), 0.0, 6.0)
	_text(f_disp, num, gx, top, ns, CREAM, HORIZONTAL_ALIGNMENT_CENTER, gw, Color(0, 0, 0, 0.7), Vector2(0, 2))
	_text(f_bold, "KM/H" if kmh else "MPH", gx, top + ns + 2.0, 9.0, Color(1, 0.957, 0.863, 0.85), HORIZONTAL_ALIGNMENT_CENTER, gw, Color(0, 0, 0, 0.9), Vector2(0, 1), 1.8)


static func _gauge_col(f: float) -> Color:
	if f < 0.5:
		return Color("#ffe9a0").lerp(Color("#ff9a1f"), f / 0.5)
	return Color("#ff9a1f").lerp(Color("#e0452c"), (f - 0.5) / 0.5)


func _draw_pedals(btn: float) -> void:
	# CSS: .brk (wide translucent pedal, 16px/10px corners), .brk.on (pressed), .brk.drifting (orange, glowing)
	var pw := btn * 1.85
	var ph := btn * 0.92
	var y := H - 14.0 + 6.0 - ph
	var drifting := me.drift != 0 or me.d_latch
	for side in [0, 1]:
		var x := 16.0 + 4.0 if side == 0 else W - 16.0 - 4.0 - pw
		var yy := y
		var stops: Array = [[0.0, Color(1, 1, 1, 0.1)], [0.4, Color(30.0 / 255, 15.0 / 255, 9.0 / 255, 0.34)], [1.0, Color(14.0 / 255, 7.0 / 255, 4.0 / 255, 0.42)]]
		var bd := Color(1, 0.957, 0.863, 0.34)
		if drifting:
			stops = [[0.0, Color("#ffe39a")], [0.48, Color("#ff8a1f")], [1.0, Color("#c4300f")]]
			bd = CREAM
			# box-shadow: 0 0 0 3px rgba(255,154,31,.3), 0 0 24px rgba(255,122,26,.5); ::before glow pulsing (.55 s)
			var pulse := 0.25 + 0.75 * (0.5 + 0.5 * sin(t * PI / 0.55))
			_draw_glow_rect(x, yy, pw, ph, Color(1, 0.48, 0.1), 0.5 + 0.35 * pulse)
			_rborder(x - 3.0, yy - 3.0, pw + 6.0, ph + 6.0, Color(1, 154.0 / 255, 31.0 / 255, 0.3), 3.0, 19.0, 13.0)
		elif braking:
			stops = [[0.0, Color(1, 1, 1, 0.14)], [0.4, Color(224.0 / 255, 69.0 / 255, 44.0 / 255, 0.5)], [1.0, Color(160.0 / 255, 40.0 / 255, 20.0 / 255, 0.6)]]
			yy += 2.0
		else:
			# 0 6px 16px rgba(0,0,0,.25)
			_rbox(x, yy + 2.0, pw, ph, Color(0, 0, 0, 0), Color(0, 0, 0, 0), 0.0, 16.0, 8.0, Color(0, 0, 0, 0.22), 10.0)
		_vgrad(x, yy, pw, ph, 16.0, 10.0, stops)
		# inset 0 -6px 12px rgba(0,0,0,.25): darker towards the bottom edge
		_vgrad(x, yy + ph - 14.0, pw, 14.0, 0.0, 10.0, [[0.0, Color(0, 0, 0, 0)], [1.0, Color(0, 0, 0, 0.22)]])
		# ::after: a soft sheen across the top
		_vgrad(x + pw * 0.14, yy + ph * 0.07, pw * 0.72, ph * 0.1, ph * 0.04, ph * 0.04, [[0.0, Color(1, 1, 1, 0.22)], [1.0, Color(1, 1, 1, 0)]])
		_rborder(x, yy, pw, ph, bd, 1.5, 16.0, 10.0)
		# contents in a row, centred: icon (26), 8, DRIFT, 8, BRAKE
		var cy := yy + ph / 2.0
		var fs := clampf(2.4 * _vmin(), 11.0, 15.0)
		var dw := _str_w(f_disp, "DRIFT", fs, fs * 0.04)
		var bw := _str_w(f_bold, "BRAKE", 9.0, 9.0 * 0.14)
		var icon := clampf(3.8 * _vmin(), 16.0, 26.0)
		var total := icon + 8.0 + dw + 8.0 + bw
		var tx := x + (pw - total) / 2.0
		var icol := Color.WHITE if drifting else CHEESE
		_drift_icon(tx, cy - icon / 2.0, icon, side == 1, icol)
		_text(f_disp, "DRIFT", tx + icon + 8.0, cy - fs * 0.5, fs, Color.WHITE if drifting else CREAM, HORIZONTAL_ALIGNMENT_LEFT, -1.0, Color(0, 0, 0, 0.6), Vector2(0, 2), fs * 0.04)
		_text(f_bold, "BRAKE", tx + icon + 8.0 + dw + 8.0, cy - 9.0 * 0.5, 9.0, Color("#5a2206") if drifting else MUTED, HORIZONTAL_ALIGNMENT_LEFT, -1.0, Color(0, 0, 0, 0.0 if drifting else 0.6), Vector2(0, 1), 9.0 * 0.14)
		if pad_mode:
			_badge(Vector2(x + pw - 16.0, yy + ph - 16.0), "LT", Color("#555555"))


func _str_w(font: Font, txt: String, size: float, letter := 0.0) -> float:
	return font.get_string_size(txt, HORIZONTAL_ALIGNMENT_LEFT, -1, int(round(size * s))).x / s + letter * txt.length()


## the drift pedal's arrow (svg 24x24: M4 17c5 0 8-3 10-9 / M11 7l3.5 1 1-3.5), mirrored on the right pedal
func _drift_icon(x: float, y: float, size: float, mirror: bool, col: Color) -> void:
	var k := size / 24.0
	var curve := _bez(Vector2(4, 17), Vector2(9, 17), Vector2(12, 14), Vector2(14, 8))
	var head := PackedVector2Array([Vector2(11, 7), Vector2(14.5, 8), Vector2(15.5, 4.5)])
	for pts in [curve, head]:
		var out := PackedVector2Array()
		var sh := PackedVector2Array()
		for p in pts:
			var q := Vector2(24.0 - p.x if mirror else p.x, p.y)
			out.append(_p(Vector2(x, y) + q * k))
			sh.append(_p(Vector2(x, y) + q * k + Vector2(0, 2)))
		draw_polyline(sh, Color(0, 0, 0, 0.35), 2.6 * k * s, true)
		draw_polyline(out, col, 2.6 * k * s, true)
		for e in [0, out.size() - 1]:
			draw_circle(out[e], 1.3 * k * s, col, true, -1.0, true)


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


func special_rect() -> Rect2:
	var btn := _btn()
	var size := btn * 0.95
	var x := maxf(8.0, btn * 0.12) + 16.0
	return Rect2(Vector2(x, 12.0 + _hud_top()) * s, Vector2(size, size) * s)


## web .tdtag (AUTO-DRIVE at the top) and .tdbar (the shortcut choice at the bottom)
func _draw_td() -> void:
	var tag := "AUTO-DRIVE"
	var tw := f_bold.get_string_size(tag, HORIZONTAL_ALIGNMENT_LEFT, -1, int(11 * s)).x / s + 11 * 0.12 * tag.length() + 18.0
	_rbox(W / 2.0 - tw / 2.0, 6.0, tw, 21.0, Color(0.184, 0.604, 0.227, 0.85), Color(0, 0, 0, 0), 0.0, 8.0)
	_text(f_bold, tag, W / 2.0 - tw / 2.0, 11.0, 11.0, Color.WHITE, HORIZONTAL_ALIGNMENT_CENTER, tw, Color(0, 0, 0, 0), Vector2.ZERO, 11 * 0.12)
	td_take_r = Rect2()
	td_skip_r = Rect2()
	if not bool(td.get("show", false)):
		return
	var lab := "Shortcut in "
	var secs := str(int(td.get("sec", 0)))
	var lab2 := " s"
	var fz := 13.0
	var bw1 := f_bold.get_string_size("Take shortcut", HORIZONTAL_ALIGNMENT_LEFT, -1, int(14 * s)).x / s + 28.0
	var bw2 := f_bold.get_string_size("Ignore shortcut", HORIZONTAL_ALIGNMENT_LEFT, -1, int(14 * s)).x / s + 28.0
	var lw := (f_bold.get_string_size(lab + secs + lab2, HORIZONTAL_ALIGNMENT_LEFT, -1, int(fz * s)).x) / s + 8.0
	var w := 10.0 + lw + 8.0 + bw1 + 8.0 + bw2 + 10.0
	var h := 44.0 + 16.0
	var x := W / 2.0 - w / 2.0
	var y := H - 14.0 - h
	_rbox(x, y, w, h, Color(0.086, 0.055, 0.035, 0.86), Color(0, 0, 0, 0), 0.0, 18.0, 24.0, Color(0, 0, 0, 0.35))
	var tx := x + 10.0 + 4.0
	var ty := y + h / 2.0 - fz * 0.6
	_text(f_bold, lab, tx, ty, fz, CREAM)
	var w1 := f_bold.get_string_size(lab, HORIZONTAL_ALIGNMENT_LEFT, -1, int(fz * s)).x / s
	_text(f_bold, secs, tx + w1, ty, fz, Color("#9dff7a"))
	var w2 := f_bold.get_string_size(secs, HORIZONTAL_ALIGNMENT_LEFT, -1, int(fz * s)).x / s
	_text(f_bold, lab2, tx + w1 + w2, ty, fz, CREAM)
	var bx := x + 10.0 + lw + 8.0
	var by := y + 8.0
	for i in 2:
		var bwi := bw1 if i == 0 else bw2
		var on := bool(td.get("take" if i == 0 else "skip", false))
		if on:
			_rbox(bx - 4.0, by - 4.0, bwi + 8.0, 52.0, Color(0, 0, 0, 0), Color("#ffd24a"), 3.0, 15.0)
		_rbox(bx, by, bwi, 44.0, Color("#2f9a3a") if i == 0 else Color(1, 0.957, 0.863, 0.12), Color(0, 0, 0, 0), 0.0, 12.0)
		_text(f_bold, "Take shortcut" if i == 0 else "Ignore shortcut", bx, by + 22.0 - 14.0 * 0.6, 14.0, Color.WHITE if i == 0 else CREAM, HORIZONTAL_ALIGNMENT_CENTER, bwi)
		var r := Rect2(Vector2(bx, by) * s, Vector2(bwi, 44.0) * s)
		if i == 0:
			td_take_r = r
		else:
			td_skip_r = r
		bx += bwi + 8.0


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
