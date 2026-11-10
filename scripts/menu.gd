class_name Menu
extends Control
## The web game's menus, rebuilt to look the same: home (mode, speed class, tools, Choose driver,
## Play with friends), driver select, track select (cups and track cards), and the overlays (How to
## play, Records, Awards, Settings, Best setup, Play with friends). Drawn over the live track like the
## web's demo view. Sizes are the web's CSS pixels times its zoom at 1280x720 (Z).

signal go(opts: Dictionary)          # start a race: {mode, cls, ri, map, cup}
signal host_online
signal join_online(addr: String)
signal leave_online
signal start_online
signal setting_changed(key: String, value)
signal modal_closed

const Z := 1.18
const CHEESE := Color("#f7c948")
const CREAM := Color("#fff4dc")
const SAUCE := Color("#e0452c")
const SAUCE_DARK := Color("#7d1d0e")
const MUTED := Color("#c2a58c")
const OVEN := Color("#160c09")
const OVEN2 := Color("#25150f")

const MODES := [["gp", "Grand Prix"], ["single", "Single race"], ["lss", "Last Slice"]]
const CLASSES := [["small", "50cc"], ["medium", "100cc"], ["large", "200cc"], ["reverse", "Reverse"]]
const CLS_NOTE := {"small": "50cc: a relaxed speed for learning the tracks.", "medium": "100cc: the standard race speed.", "large": "200cc: much faster karts and sharper rivals.", "reverse": "Every track runs backwards at 200cc speed."}
const MODE_NOTE := {"lss": "Last Slice Standing: each time the leader completes a lap, the racer in last place is out. Seven laps, one slice left."}
const CUPS := [["Margherita Cup", "#f7c948"], ["Supreme Cup", "#3f9a35"], ["Deep Dish Cup", "#e0452c"], ["Meat Lover's Cup", "#b06a3c"]]

var f_disp: Font
var f_bold: Font
var f_semi: Font
var f_med: Font

var mode := "gp"
var cls := "medium"
var ri := 1
var build := {"b": 0, "w": 0, "g": 0, "p": 0, "t": ""}   # the kart build (web playerBuild)
var g_tab := "kart"
var g_hint := ""
var stats_on := true
var _gview: SubViewport
var _gkart: Node3D
var _gturn: Node3D
var _grot := 0.6
var _gcam: Camera3D
var _grad := 8.0
var _gcy := 3.0
var _gasp := 0.0
var _gdrag := false
var map_id := "bay"
var cup := 0
var maps: Array = []           # from main.maps: {id, name, mi, theme, cup}
var roster := {}               # main.roster
var portraits := {}
var racers_info: Array = []    # [{name, color, ...}] from the track's racer list
var online_note := ""
var net_role := ""

var bg: Control
var screens := {}
var cur := ""
var modal: Control = null
var default_focus: Control = null


## keyboard or controller: the first move puts the focus on the screen's main button
func _input(ev: InputEvent) -> void:
	if not visible:
		return
	if ev is InputEventMouseButton or ev is InputEventMouseMotion:
		return
	var nav := ev.is_action_pressed("ui_up") or ev.is_action_pressed("ui_down") or ev.is_action_pressed("ui_left") or ev.is_action_pressed("ui_right") or ev.is_action_pressed("ui_accept")
	if nav and get_viewport().gui_get_focus_owner() == null and default_focus != null and is_instance_valid(default_focus):
		default_focus.grab_focus()
		get_viewport().set_input_as_handled()
	if ev.is_action_pressed("ui_cancel"):
		if modal != null:
			close_modal()
		elif cur == "driver":
			open("home")
		elif cur == "garage":
			open("driver")
		elif cur == "track":
			open("garage" if KartBuilder.ready() else "driver")
		get_viewport().set_input_as_handled()
var _seg_groups := {}


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	f_disp = load("res://assets/fonts/Bungee-Regular.ttf")
	f_bold = load("res://assets/fonts/ChakraPetch-Bold.ttf")
	f_semi = load("res://assets/fonts/ChakraPetch-SemiBold.ttf")
	f_med = load("res://assets/fonts/ChakraPetch-Medium.ttf")
	bg = _Backdrop.new()
	bg.blur = false
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	bg.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(bg)


func z(v: float) -> float:
	return v * Z


func zi(v: float) -> int:
	return int(round(v * Z))


# ---------------------------------------------------------------- building blocks

class _Backdrop extends Control:
	## .overlay: a warm dark wash over the live track (darker at the bottom), an orange glow top-left, a red one bottom-right
	var dim := 1.0
	var blur := true
	var _br: ColorRect
	## the overlays (garage, pop-ups, pause) blur what is behind them; the menu screens don't
	func set_blur(on: bool) -> void:
		blur = on
		if _br != null:
			_br.visible = on
	func _ready() -> void:
		# backdrop-filter: blur(6px): the track behind is drawn soft, under the wash
		if true:
			var br := ColorRect.new()
			_br = br
			br.visible = blur
			br.show_behind_parent = true
			br.mouse_filter = Control.MOUSE_FILTER_IGNORE
			br.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
			var sm := ShaderMaterial.new()
			sm.shader = load("res://shaders/backdrop_blur.gdshader")
			br.material = sm
			add_child(br)
			resized.connect(func():
				sm.set_shader_parameter("lod", clampf(3.0 + log(maxf(1.0, size.y) / 720.0) / log(2.0), 2.0, 4.5)))
	func _draw() -> void:
		var r := get_rect()
		var w := r.size.x
		var h := r.size.y
		var top := Color(22.0 / 255.0, 11.0 / 255.0, 7.0 / 255.0, minf(1.0, 0.72 * dim))
		var bot := Color(10.0 / 255.0, 5.0 / 255.0, 3.0 / 255.0, minf(1.0, 0.9 * dim))
		draw_polygon(PackedVector2Array([Vector2(0, 0), Vector2(w, 0), Vector2(w, h), Vector2(0, h)]), PackedColorArray([top, top, bot, bot]))
		_glow(Vector2(w * 0.2, 0), w * 0.55, Color(1, 0.54, 0.12, 0.16 * dim))
		_glow(Vector2(w * 0.9, h), w * 0.5, Color(0.88, 0.27, 0.17, 0.16 * dim))

	func _glow(c: Vector2, rad: float, col: Color) -> void:
		var n := 40
		var pts := PackedVector2Array([c])
		var cols := PackedColorArray([col])
		for i in n + 1:
			var a := TAU * i / n
			pts.append(c + Vector2(cos(a), sin(a) * 0.6) * rad)
			cols.append(Color(col.r, col.g, col.b, 0.0))
		for i in n:
			draw_polygon(PackedVector2Array([pts[0], pts[i + 1], pts[i + 2]]), PackedColorArray([cols[0], cols[i + 1], cols[i + 2]]))


class _Lock extends Control:
	## the padlock on a reward livery not won yet
	func _draw() -> void:
		var w := size.x
		var h := size.y
		var c := Color("#fff4dc")
		draw_rect(Rect2(w * 0.2, h * 0.44, w * 0.6, h * 0.46), c)
		draw_arc(Vector2(w * 0.5, h * 0.42), w * 0.2, PI, TAU, 16, c, maxf(1.5, w * 0.1), true)


class _Line extends Control:
	## the fading rule after a section label (.label::after)
	func _draw() -> void:
		var y := size.y / 2.0
		var n := 16
		for i in n:
			var f0 := float(i) / n
			draw_line(Vector2(size.x * f0, y), Vector2(size.x * (f0 + 1.0 / n), y), Color(1, 0.957, 0.863, 0.18 * (1.0 - f0)), 1.0)


func label(text: String, font: Font, size_css: float, col: Color, shadow := Color(0, 0, 0, 0), sh_off := Vector2(0, 2)) -> Label:
	var l := Label.new()
	l.text = text
	var ls := LabelSettings.new()
	ls.font = font
	ls.font_size = zi(size_css)
	ls.font_color = col
	if shadow.a > 0.0:
		ls.shadow_color = shadow
		ls.shadow_offset = sh_off * Z
		ls.shadow_size = 0
	l.label_settings = ls
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return l


func para(text: String, size_css: float, col: Color, width_css: float) -> Label:
	var l := label(text, f_med, size_css, col)
	l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	l.custom_minimum_size.x = z(width_css)
	l.label_settings.line_spacing = z(size_css * 0.45) - z(size_css) * 0.2
	return l


func section_label(text: String) -> Control:
	var h := HBoxContainer.new()
	h.add_theme_constant_override("separation", zi(10))
	var l := label(text.to_upper(), f_bold, 12.0, MUTED)
	l.label_settings.font_size = zi(12)
	h.add_child(l)
	var ln := _Line.new()
	ln.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	ln.custom_minimum_size.y = z(12)
	ln.mouse_filter = Control.MOUSE_FILTER_IGNORE
	h.add_child(ln)
	return h


func box(cols: Array, ang: float, r: float, border := Color(0, 0, 0, 0), bw := 0.0, pad := Vector4(0, 0, 0, 0)) -> CssBox:
	var b := CssBox.make(cols, ang, r, border, bw, pad * Z)
	b.scale = Z
	return b


## a soft glass card: .mapc, .card, .seg, .ghost (linear-gradient(160deg, rgba(255,244,220,.07), rgba(255,244,220,.015)), 1px border)
func glass(r: float, pad := Vector4(0, 0, 0, 0)) -> CssBox:
	var b := box([Color(1, 0.957, 0.863, 0.07), Color(1, 0.957, 0.863, 0.015)], 160.0, r, Color(1, 0.957, 0.863, 0.12), 1.0, pad)
	b.inset_top = Color(1, 1, 1, 0.05)
	return b


func button(text: String, kind: String, size_css := 15.0, pad := Vector4(16, 12, 16, 12)) -> Button:
	var b := Button.new()
	b.text = text
	b.focus_mode = Control.FOCUS_ALL
	b.mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
	var font: Font = f_bold
	var fc := CREAM
	var normal: CssBox
	var hover: CssBox
	var pressed: CssBox
	match kind:
		"cta":
			font = f_disp
			# linear-gradient(135deg,#ff9a2a 0%,#e0452c 55%,#c4300f 100%); 0 5px 0 sauce-dark, 0 12px 30px rgba(224,69,44,.35)
			normal = box([[0.0, Color("#ff9a2a")], [0.55, Color("#e0452c")], [1.0, Color("#c4300f")]], 135.0, 14.0, Color(0, 0, 0, 0), 0.0, pad)
			normal.shadow(Vector2(0, 12), 30.0, Color(0.88, 0.27, 0.17, 0.3)).shadow(Vector2(0, 5), 0.0, SAUCE_DARK)
			hover = box([[0.0, Color("#ffab45")], [0.55, Color("#ec5537")], [1.0, Color("#d03a16")]], 135.0, 14.0, Color(0, 0, 0, 0), 0.0, pad)
			hover.shadow(Vector2(0, 12), 30.0, Color(0.88, 0.27, 0.17, 0.4)).shadow(Vector2(0, 5), 0.0, SAUCE_DARK)
			pressed = box([[0.0, Color("#ff9a2a")], [0.55, Color("#e0452c")], [1.0, Color("#c4300f")]], 135.0, 14.0, Color(0, 0, 0, 0), 0.0, pad + Vector4(0, 3, 0, -3))
			pressed.shadow(Vector2(0, 2), 0.0, SAUCE_DARK)
		"ghost":
			normal = glass(12.0, pad)
			hover = box([Color(1, 0.957, 0.863, 0.12), Color(1, 0.957, 0.863, 0.04)], 160.0, 12.0, Color(1, 0.957, 0.863, 0.22), 1.0, pad)
			pressed = box([Color(1, 0.957, 0.863, 0.05), Color(1, 0.957, 0.863, 0.01)], 160.0, 12.0, Color(1, 0.957, 0.863, 0.18), 1.0, pad)
		"icon":
			normal = box([Color(1, 0.957, 0.863, 0.09), Color(1, 0.957, 0.863, 0.02)], 160.0, 12.0, Color(1, 0.957, 0.863, 0.16), 1.0, pad)
			hover = box([Color(1, 0.957, 0.863, 0.15), Color(1, 0.957, 0.863, 0.05)], 160.0, 12.0, Color(1, 0.957, 0.863, 0.26), 1.0, pad)
			pressed = box([Color(1, 0.957, 0.863, 0.06), Color(1, 0.957, 0.863, 0.01)], 160.0, 12.0, Color(1, 0.957, 0.863, 0.2), 1.0, pad)
		"pill":
			normal = box([Color(1, 0.54, 0.12, 0.22), Color(0.88, 0.27, 0.17, 0.12)], 135.0, 999.0, Color(1, 0.54, 0.12, 0.45), 1.0, pad)
			hover = box([Color(1, 0.54, 0.12, 0.32), Color(0.88, 0.27, 0.17, 0.2)], 135.0, 999.0, Color(1, 0.54, 0.12, 0.6), 1.0, pad)
			pressed = normal
		"seg_on":
			normal = box([Color("#ff8a1f"), Color("#e0452c")], 135.0, 9.0, Color(0, 0, 0, 0), 0.0, pad)
			normal.shadow(Vector2(0, 4), 14.0, Color(0.88, 0.27, 0.17, 0.4))
			hover = normal
			pressed = normal
		_:   # seg_off
			fc = MUTED
			normal = box([Color(0, 0, 0, 0)], 180.0, 9.0, Color(0, 0, 0, 0), 0.0, pad)
			hover = box([Color(1, 0.957, 0.863, 0.06)], 180.0, 9.0, Color(0, 0, 0, 0), 0.0, pad)
			pressed = hover
	b.add_theme_stylebox_override("normal", normal)
	b.add_theme_stylebox_override("hover", hover)
	b.add_theme_stylebox_override("pressed", pressed)
	b.add_theme_stylebox_override("hover_pressed", pressed)
	b.add_theme_stylebox_override("focus", box([Color(0, 0, 0, 0)], 180.0, 12.0, CHEESE, 3.0))
	b.add_theme_stylebox_override("disabled", normal)
	b.add_theme_font_override("font", font)
	b.add_theme_font_size_override("font_size", zi(size_css))
	for st in ["font_color", "font_hover_color", "font_pressed_color", "font_focus_color", "font_hover_pressed_color"]:
		b.add_theme_color_override(st, fc if kind != "seg_off" or st == "font_color" else CREAM)
	if kind == "cta":
		b.add_theme_constant_override("outline_size", 0)
	return b


func icon_tex(name_: String) -> Texture2D:
	var p := "res://assets/ui/ic_%s.svg" % name_
	return load(p) if ResourceLoader.exists(p) else null


## a segmented control (.seg): options [[key, text]], the chosen key, called with the new key
func seg(group: String, options: Array, chosen: String, on_pick: Callable, size_css := 15.0, pad_y := 10.0) -> PanelContainer:
	var pc := PanelContainer.new()
	var st := glass(14.0, Vector4(4, 4, 4, 4))
	pc.add_theme_stylebox_override("panel", st)
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", zi(4))
	pc.add_child(row)
	var btns := {}
	for o in options:
		var key: String = o[0]
		var b := button(String(o[1]), "seg_on" if key == chosen else "seg_off", size_css, Vector4(4, pad_y, 4, pad_y))
		b.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		b.pressed.connect(func():
			_seg_select(group, key)
			on_pick.call(key))
		row.add_child(b)
		btns[key] = b
	_seg_groups[group] = {"btns": btns, "size": size_css, "pad": pad_y}
	return pc


func _seg_select(group: String, key: String) -> void:
	var g: Dictionary = _seg_groups[group]
	for k in g["btns"]:
		var b: Button = g["btns"][k]
		var nb := button(b.text, "seg_on" if k == key else "seg_off", float(g["size"]), Vector4(4, float(g["pad"]), 4, float(g["pad"])))
		for st in ["normal", "hover", "pressed", "hover_pressed"]:
			b.add_theme_stylebox_override(st, nb.get_theme_stylebox(st))
		for c in ["font_color", "font_hover_color", "font_pressed_color", "font_focus_color", "font_hover_pressed_color"]:
			b.add_theme_color_override(c, nb.get_theme_color(c))
		nb.free()


func vbox(sep_css: float) -> VBoxContainer:
	var v := VBoxContainer.new()
	v.add_theme_constant_override("separation", zi(sep_css))
	return v


func hbox(sep_css: float) -> HBoxContainer:
	var h := HBoxContainer.new()
	h.add_theme_constant_override("separation", zi(sep_css))
	return h


func panel(st: StyleBox) -> PanelContainer:
	var p := PanelContainer.new()
	p.add_theme_stylebox_override("panel", st)
	return p


## the logo: Bungee in the web's cheese-to-sauce gradient with a dark red drop
func logo(text: String, size_css: float) -> Control:
	var c := _GradLabel.new()
	c.text = text
	c.font = f_disp
	c.size_px = z(size_css)
	c.custom_minimum_size = Vector2(f_disp.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, int(z(size_css))).x + z(8), z(size_css) * 1.05)
	var m := ShaderMaterial.new()
	m.shader = load("res://shaders/gradtext.gdshader")
	m.set_shader_parameter("c0", Color("#fff6cf"))
	m.set_shader_parameter("c1", Color("#f7c948"))
	m.set_shader_parameter("c2", Color("#ff8a1f"))
	m.set_shader_parameter("c3", Color("#e0452c"))
	m.set_shader_parameter("stops", Vector3(0.40, 0.75, 1.0))
	m.set_shader_parameter("y0", z(size_css) * 0.06)
	m.set_shader_parameter("y1", z(size_css) * 0.84)
	c.material = m
	c.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var holder := Control.new()
	holder.custom_minimum_size = c.custom_minimum_size + Vector2(0, z(6))
	holder.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var sh := _ShadowLabel.new()
	sh.text = text
	sh.font = f_disp
	sh.size_px = z(size_css)
	sh.position = Vector2(0, z(4))
	sh.size = c.custom_minimum_size
	sh.mouse_filter = Control.MOUSE_FILTER_IGNORE
	holder.add_child(sh)
	c.size = c.custom_minimum_size
	holder.add_child(c)
	return holder


class _GradLabel extends Control:
	var text := ""
	var font: Font
	var size_px := 40.0
	func _draw() -> void:
		draw_string(font, Vector2(0, size_px * 0.86), text, HORIZONTAL_ALIGNMENT_LEFT, -1, int(size_px), Color.WHITE)


class _ShadowLabel extends Control:
	var text := ""
	var font: Font
	var size_px := 40.0
	func _draw() -> void:
		# drop-shadow(0 12px 24px rgba(0,0,0,.4)) as a few soft layers, then the hard dark red drop
		for i in 4:
			draw_string(font, Vector2(0, size_px * 0.86 + 6.0 + i * 3.0), text, HORIZONTAL_ALIGNMENT_LEFT, -1, int(size_px), Color(0, 0, 0, 0.07))
		draw_string(font, Vector2(0, size_px * 0.86), text, HORIZONTAL_ALIGNMENT_LEFT, -1, int(size_px), Color(125.0 / 255, 29.0 / 255, 14.0 / 255, 0.95))


# ---------------------------------------------------------------- screens

func open(name_: String) -> void:
	close_modal()
	for k in screens:
		(screens[k] as Control).queue_free()
	screens.clear()
	cur = name_
	bg.set_blur(name_ == "garage")
	var s: Control
	match name_:
		"home":
			s = _home()
		"driver":
			s = _driver()
		"track":
			s = _track()
		"garage":
			s = _garage()
		_:
			s = _home()
	screens[name_] = s
	add_child(s)
	visible = true


func _screen_root() -> MarginContainer:
	var m := MarginContainer.new()
	m.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	m.add_theme_constant_override("margin_left", zi(14))
	m.add_theme_constant_override("margin_right", zi(14))
	m.add_theme_constant_override("margin_top", zi(12))
	m.add_theme_constant_override("margin_bottom", zi(10))
	return m


func _home() -> Control:
	var root := _screen_root()
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", zi(36))
	row.alignment = BoxContainer.ALIGNMENT_CENTER
	root.add_child(row)
	# brand: logo, tag line, Best setup
	var brand := vbox(12)
	brand.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	brand.size_flags_stretch_ratio = 1.1
	brand.alignment = BoxContainer.ALIGNMENT_CENTER
	row.add_child(brand)
	brand.add_child(logo("CRUST RUSH", 82.0))
	var tag := para("Kart racing on giant pizzas. Pick a mode, choose your driver, build your ride and drift your way to the trophy.", 15.0, MUTED, 340.0)
	tag.size_flags_horizontal = Control.SIZE_SHRINK_BEGIN
	brand.add_child(tag)
	var tips := button("Best setup for your device", "pill", 14.0, Vector4(14, 9, 14, 9))
	tips.icon = icon_tex("tips")
	tips.expand_icon = false
	tips.add_theme_constant_override("icon_max_width", zi(18))
	tips.add_theme_constant_override("h_separation", zi(8))
	tips.size_flags_horizontal = Control.SIZE_SHRINK_BEGIN
	tips.pressed.connect(func(): show_modal("tips"))
	brand.add_child(tips)
	# the panel
	var pnl := panel(glass(20.0, Vector4(18, 18, 18, 18)))
	(pnl.get_theme_stylebox("panel") as CssBox).colors = PackedColorArray([Color(1, 0.957, 0.863, 0.07), Color(1, 0.957, 0.863, 0.02)])
	pnl.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	pnl.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	row.add_child(pnl)
	var col := vbox(14)
	pnl.add_child(col)
	var s1 := vbox(8)
	s1.add_child(section_label("Mode"))
	var mode_note := para(MODE_NOTE.get(mode, ""), 13.0, MUTED, 300.0)
	mode_note.visible = MODE_NOTE.has(mode)
	s1.add_child(seg("mode", MODES, mode, func(k):
		mode = k
		mode_note.text = MODE_NOTE.get(k, "")
		mode_note.visible = MODE_NOTE.has(k)
		setting_changed.emit("mode", k), 15.0, 10.0))
	s1.add_child(mode_note)
	col.add_child(s1)
	var s2 := vbox(8)
	s2.add_child(section_label("Speed class"))
	var cls_note := para(CLS_NOTE.get(cls, ""), 13.0, MUTED, 300.0)
	s2.add_child(seg("cls", CLASSES, cls, func(k):
		cls = k
		cls_note.text = CLS_NOTE.get(k, "")
		setting_changed.emit("cls", k), 14.0, 10.0))
	s2.add_child(cls_note)
	col.add_child(s2)
	var tools := hbox(8)
	for t in [["how", "How to play"], ["rec", "Records"], ["ach", "Awards"], ["set", "Settings"]]:
		var b := button(String(t[1]), "icon", 14.0, Vector4(10, 10, 10, 10))
		b.icon = icon_tex(String(t[0]))
		b.add_theme_constant_override("icon_max_width", zi(20))
		b.add_theme_constant_override("h_separation", zi(8))
		b.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		var key: String = t[0]
		b.pressed.connect(func(): show_modal(key))
		tools.add_child(b)
	col.add_child(tools)
	var cta := button("CHOOSE DRIVER  ›", "cta", 22.0, Vector4(16, 16, 16, 16))
	cta.pressed.connect(func(): open("driver"))
	col.add_child(cta)
	var mp := button("Play with friends", "ghost", 15.0, Vector4(16, 12, 16, 12))
	mp.pressed.connect(func(): show_modal("mp"))
	col.add_child(mp)
	default_focus = cta
	return root


func _driver() -> Control:
	var root := _screen_root()
	var v := vbox(8)
	root.add_child(v)
	var three := KartBuilder.ready()
	v.add_child(_step_head("‹ Back", "home", "Step 1 of 3" if three else "Step 1 of 2", "Choose your driver", "BUILD KART  ›" if three else "CHOOSE TRACK  ›", func(): open("garage" if three else "track")))
	var body := hbox(14)
	body.size_flags_vertical = Control.SIZE_EXPAND_FILL
	v.add_child(body)
	var grid := GridContainer.new()
	grid.columns = 4
	grid.add_theme_constant_override("h_separation", zi(10))
	grid.add_theme_constant_override("v_separation", zi(10))
	grid.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	grid.size_flags_vertical = Control.SIZE_EXPAND_FILL
	grid.size_flags_stretch_ratio = 1.55
	body.add_child(grid)
	var detail := panel(glass(18.0, Vector4(12, 12, 12, 12)))
	detail.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	body.add_child(detail)
	var dv := vbox(10)
	detail.add_child(dv)
	var show_detail := func(i: int):
		for c in dv.get_children():
			c.queue_free()
		var info: Dictionary = racers_info[i] if i < racers_info.size() else {}
		var pic := _Portrait.new()
		pic.tex = portraits.get(i)
		pic.radius = z(14)
		pic.size_flags_vertical = Control.SIZE_EXPAND_FILL
		pic.custom_minimum_size = Vector2(0, z(220))
		dv.add_child(pic)
		dv.add_child(label(("Favourite prop · " + String(info.get("prop", ""))).to_upper(), f_bold, 11.0, MUTED))
		var ab := panel(glass(12.0, Vector4(28, 10, 12, 10)))
		var rt := RichTextLabel.new()
		rt.bbcode_enabled = true
		rt.fit_content = true
		rt.scroll_active = false
		rt.add_theme_font_override("normal_font", f_med)
		rt.add_theme_font_override("bold_font", f_bold)
		rt.add_theme_font_size_override("normal_font_size", zi(12))
		rt.add_theme_font_size_override("bold_font_size", zi(13))
		rt.add_theme_color_override("default_color", MUTED)
		rt.text = "[b][color=#fff4dc]%s[/color][/b] %s" % [String(info.get("ability", "")), String(info.get("ability_desc", ""))]
		ab.add_child(rt)
		var dot := _Dot.new()
		dot.col = Color(String(info.get("ability_col", "#ff5a2a")))
		dot.position = Vector2(z(10), z(30))
		ab.add_child(dot)
		dv.add_child(ab)
		dv.add_child(label(String(info.get("name", "Racer")).to_upper(), f_disp, 24.0, CHEESE, SAUCE_DARK, Vector2(0, 3)))
		dv.add_child(para(String(info.get("bio", "")), 13.0, CREAM, 380.0))
	for i in racers_info.size():
		var info: Dictionary = racers_info[i]
		var card := _driver_card(i, info)
		card.pressed.connect(func():
			ri = i
			show_detail.call(i)
			setting_changed.emit("ri", i)
			for c in grid.get_children():
				_mark_card(c as Button, int(c.get_meta("i")) == ri, true))
		card.focus_entered.connect(func():
			if ri != i:
				card.pressed.emit())
		grid.add_child(card)
	show_detail.call(ri)
	return root


class _Portrait extends Control:
	## a portrait clipped to a rounded rectangle (object-fit: cover), with a dark fade at the bottom
	var tex: Texture2D
	var radius := 14.0
	var corners := Vector4(-1, -1, -1, -1)   # per corner (tl, tr, br, bl); -1 = use radius
	var fade := false
	var label := ""
	var font: Font
	var font_px := 14.0
	func _draw() -> void:
		var r := Rect2(Vector2.ZERO, size)
		if tex == null:
			draw_rect(r, Color("#2a1810"))
			return
		var ta := float(tex.get_width()) / tex.get_height()
		var ra := size.x / maxf(1.0, size.y)
		var src := Rect2(0, 0, tex.get_width(), tex.get_height())
		if ta > ra:
			var w := tex.get_height() * ra
			src = Rect2((tex.get_width() - w) / 2.0, 0, w, tex.get_height())
		else:
			var h := tex.get_width() / ra
			src = Rect2(0, (tex.get_height() - h) * 0.3, tex.get_width(), h)
		# rounded corners: draw the picture as a polygon with matching UVs
		var rc := Vector4.ONE * radius if corners.x < 0.0 else corners
		var pts := CssBox.outline(r, rc)
		var uvs := PackedVector2Array()
		for p in pts:
			uvs.append(Vector2((src.position.x + p.x / size.x * src.size.x) / tex.get_width(), (src.position.y + p.y / size.y * src.size.y) / tex.get_height()))
		draw_colored_polygon(pts, Color.WHITE, uvs, tex)
		if fade:
			var n := 12
			for i in n:
				var f := float(i) / n
				var y0 := size.y * (0.72 + 0.28 * f)
				draw_rect(Rect2(radius * 0.3 * f, y0, size.x - radius * 0.6 * f, size.y * 0.28 / n + 1.0), Color(0.06, 0.03, 0.02, 0.15 + 0.6 * f))
		if label != "" and font != null:
			draw_string(font, Vector2(font_px * 0.5, size.y - font_px * 0.55) + Vector2(0, 1), label, HORIZONTAL_ALIGNMENT_LEFT, size.x - font_px, int(font_px), Color(0, 0, 0, 0.8))
			draw_string(font, Vector2(font_px * 0.5, size.y - font_px * 0.55), label, HORIZONTAL_ALIGNMENT_LEFT, size.x - font_px, int(font_px), Color("#fff4dc"))


class _Dot extends Control:
	var col := Color.RED
	func _draw() -> void:
		draw_circle(Vector2.ZERO, 6.0 * 1.18, col)
		draw_circle(Vector2.ZERO, 9.0 * 1.18, Color(col.r, col.g, col.b, 0.25))


func _driver_card(i: int, info: Dictionary) -> Button:
	var b := Button.new()
	b.set_meta("i", i)
	b.custom_minimum_size = Vector2(z(120), z(200))
	b.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	b.size_flags_vertical = Control.SIZE_EXPAND_FILL
	b.mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
	_mark_card(b, i == ri, true)
	var pic := _Portrait.new()
	pic.tex = portraits.get(i)
	pic.radius = z(12)
	pic.fade = true
	pic.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	pic.offset_left = z(3)
	pic.offset_top = z(3)
	pic.offset_right = -z(3)
	pic.offset_bottom = -z(3)
	pic.mouse_filter = Control.MOUSE_FILTER_IGNORE
	b.add_child(pic)
	var l := label(String(info.get("name", "")).to_upper(), f_disp, 15.0, CREAM, Color(0, 0, 0, 0.7), Vector2(0, 2))
	l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	l.set_anchors_and_offsets_preset(Control.PRESET_BOTTOM_WIDE)
	l.offset_top = -z(30)
	l.offset_bottom = -z(6)
	b.add_child(l)
	return b


func _mark_card(b: Button, on: bool, tall := false) -> void:
	var r := 14.0
	var st := glass(r, Vector4(8, 8, 8, 8))
	if on:
		st = box([Color(1, 0.54, 0.12, 0.12), Color(0.88, 0.27, 0.17, 0.08)], 160.0, r, CHEESE, 3.0, Vector4(8, 8, 8, 8))
		st.shadow(Vector2(0, 0), 16.0, Color(0.97, 0.79, 0.28, 0.4))
	var hv := st
	if not on:
		hv = box([Color(1, 0.957, 0.863, 0.12), Color(1, 0.957, 0.863, 0.04)], 160.0, r, Color(1, 0.957, 0.863, 0.3), 1.5, Vector4(8, 8, 8, 8))
	b.add_theme_stylebox_override("normal", st)
	b.add_theme_stylebox_override("hover", hv)
	b.add_theme_stylebox_override("pressed", st)
	b.add_theme_stylebox_override("hover_pressed", st)
	b.add_theme_stylebox_override("focus", box([Color(0, 0, 0, 0)], 180.0, r, Color(1, 0.957, 0.863, 0.6), 2.0))


func _step_head(back_text: String, back_to: String, small: String, title: String, next_text: String, on_next: Callable) -> Control:
	var h := hbox(14)
	var back := button(back_text, "ghost", 15.0, Vector4(16, 12, 16, 12))
	back.pressed.connect(func(): open(back_to))
	h.add_child(back)
	var t := vbox(0)
	t.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	t.add_child(label(small, f_bold, 12.0, MUTED))
	t.add_child(label(title.to_upper(), f_disp, 26.0, CHEESE, SAUCE_DARK, Vector2(0, 3)))
	h.add_child(t)
	var nxt := button(next_text, "cta", 19.0, Vector4(20, 12, 20, 12))
	nxt.pressed.connect(on_next)
	h.add_child(nxt)
	default_focus = nxt
	return h


func _track() -> Control:
	var root := _screen_root()
	var v := vbox(8)
	root.add_child(v)
	var cls_label := ""
	for c in CLASSES:
		if c[0] == cls:
			cls_label = c[1]
	var gp := mode == "gp"
	var three := KartBuilder.ready()
	var small := ("Step 3 of 3 · " + build_summary()) if three else ("Step 2 of 2 · " + cls_label)
	if mode == "lss":
		small += " · Last Slice"
	v.add_child(_step_head("‹ Kart" if three else "‹ Driver", "garage" if three else "driver", small, "Cup" if gp else "Track", "START GRAND PRIX" if gp else "START RACE", func(): _go()))
	var body := hbox(16)
	body.size_flags_vertical = Control.SIZE_EXPAND_FILL
	v.add_child(body)
	var detail := panel(glass(18.0, Vector4(14, 14, 14, 14)))
	detail.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	var dv := vbox(8)
	detail.add_child(dv)
	var grid := GridContainer.new()
	grid.columns = 2 if gp else 4
	grid.add_theme_constant_override("h_separation", zi(12))
	grid.add_theme_constant_override("v_separation", zi(12))
	grid.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	grid.size_flags_vertical = Control.SIZE_EXPAND_FILL
	var left: Control = grid
	if not gp:
		var sc := ScrollContainer.new()
		sc.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
		sc.add_child(grid)
		left = sc
	left.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	left.size_flags_vertical = Control.SIZE_EXPAND_FILL
	left.size_flags_stretch_ratio = 1.45
	body.add_child(left)
	body.add_child(detail)
	var show_detail := func():
		for c in dv.get_children():
			c.queue_free()
		if gp:
			dv.add_child(label((cls_label + " · 4 races").to_upper(), f_bold, 11.0, MUTED))
			dv.add_child(label(String(CUPS[cup][0]).to_upper(), f_disp, 24.0, CHEESE, SAUCE_DARK, Vector2(0, 3)))
			var g2 := GridContainer.new()
			g2.columns = 2
			g2.add_theme_constant_override("h_separation", zi(8))
			g2.add_theme_constant_override("v_separation", zi(8))
			g2.size_flags_vertical = Control.SIZE_EXPAND_FILL
			for id in _cup_tracks(cup):
				var pic := _Portrait.new()
				pic.tex = _shot(id, "h")
				pic.radius = z(10)
				pic.fade = true
				pic.label = String(_map(id).get("name", id))
				pic.font = f_bold
				pic.font_px = z(11)
				pic.size_flags_horizontal = Control.SIZE_EXPAND_FILL
				pic.size_flags_vertical = Control.SIZE_EXPAND_FILL
				g2.add_child(pic)
			dv.add_child(g2)
			dv.add_child(para("Race all four tracks. Points for every finish decide the trophy.", 13.0, CREAM, 360.0))
		else:
			var m := _map(map_id)
			var ci := int(m.get("cup", -1))
			dv.add_child(label((cls_label + " · " + (CUPS[ci][0] if ci >= 0 and ci < CUPS.size() else "Special track")).to_upper(), f_bold, 11.0, MUTED))
			dv.add_child(label(String(m.get("name", map_id)).to_upper(), f_disp, 24.0, CHEESE, SAUCE_DARK, Vector2(0, 3)))
			var pic2 := _Portrait.new()
			pic2.tex = _shot(map_id, "h")
			pic2.radius = z(12)
			pic2.size_flags_vertical = Control.SIZE_EXPAND_FILL
			dv.add_child(pic2)
			var pic3 := _Portrait.new()
			pic3.tex = _shot(map_id, "a")
			pic3.radius = z(12)
			pic3.size_flags_vertical = Control.SIZE_EXPAND_FILL
			dv.add_child(pic3)
	if gp:
		for ci in CUPS.size():
			var card := _cup_card(ci)
			card.pressed.connect(func():
				cup = ci
				var ts := _cup_tracks(ci)
				if not ts.is_empty():
					map_id = ts[0]
				setting_changed.emit("cup", ci)
				setting_changed.emit("map", map_id)
				show_detail.call()
				for c in grid.get_children():
					_mark_card(c as Button, int(c.get_meta("cup")) == cup))
			grid.add_child(card)
	else:
		for m in maps:
			var id: String = m["id"]
			var card2 := _map_card(m)
			card2.pressed.connect(func():
				map_id = id
				setting_changed.emit("map", id)
				show_detail.call()
				for c in grid.get_children():
					_mark_card(c as Button, String(c.get_meta("id")) == map_id))
			grid.add_child(card2)
	show_detail.call()
	return root


func _cup_tracks(ci: int) -> Array:
	var out: Array = []
	for m in maps:
		if int(m.get("cup", -1)) == ci:
			out.append(String(m["id"]))
	return out


## a cup: the four tracks' pictures in a square mosaic with the cup's name across the bottom
func _cup_card(ci: int) -> Button:
	var b := Button.new()
	b.set_meta("cup", ci)
	b.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	b.size_flags_vertical = Control.SIZE_EXPAND_FILL
	b.custom_minimum_size = Vector2(z(150), z(120))
	b.mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
	_mark_card(b, ci == cup)
	var g := GridContainer.new()
	g.columns = 2
	g.add_theme_constant_override("h_separation", 0)
	g.add_theme_constant_override("v_separation", 0)
	g.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	g.offset_left = z(1)
	g.offset_top = z(1)
	g.offset_right = -z(1)
	g.offset_bottom = -z(1)
	g.mouse_filter = Control.MOUSE_FILTER_IGNORE
	b.add_child(g)
	var ts := _cup_tracks(ci)
	var rr := z(13)
	for k in 4:
		var pic := _Portrait.new()
		pic.tex = _shot(ts[k], "h") if k < ts.size() else null
		pic.corners = [Vector4(rr, 0, 0, 0), Vector4(0, rr, 0, 0), Vector4(0, 0, 0, rr), Vector4(0, 0, rr, 0)][k]
		pic.fade = k >= 2
		pic.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		pic.size_flags_vertical = Control.SIZE_EXPAND_FILL
		pic.mouse_filter = Control.MOUSE_FILTER_IGNORE
		g.add_child(pic)
	var l := label(String(CUPS[ci][0]).to_upper(), f_disp, 19.0, CREAM, Color(0, 0, 0, 0.75), Vector2(0, 2))
	l.set_anchors_and_offsets_preset(Control.PRESET_BOTTOM_WIDE)
	l.offset_left = z(12)
	l.offset_top = -z(34)
	l.offset_bottom = -z(8)
	b.add_child(l)
	return b


func _map(id: String) -> Dictionary:
	for m in maps:
		if m["id"] == id:
			return m
	return {"id": id, "name": id}


func _shot(id: String, kind: String) -> Texture2D:
	var p := "res://assets/shots/%s-%s.jpg" % [id, kind]
	return load(p) if ResourceLoader.exists(p) else null


func _map_card(m: Dictionary) -> Button:
	var b := Button.new()
	var id: String = m["id"]
	b.set_meta("id", id)
	b.custom_minimum_size = Vector2(z(140), z(92))
	b.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	b.mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
	_mark_card(b, id == map_id)
	var pic := _Portrait.new()
	pic.tex = _shot(id, "h")
	pic.radius = z(12)
	pic.fade = true
	pic.label = String(m.get("name", id))
	pic.font = f_bold
	pic.font_px = z(12)
	pic.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	pic.offset_left = z(2)
	pic.offset_top = z(2)
	pic.offset_right = -z(2)
	pic.offset_bottom = -z(2)
	pic.mouse_filter = Control.MOUSE_FILTER_IGNORE
	b.add_child(pic)
	return b


func _go() -> void:
	go.emit({"mode": mode, "cls": cls, "ri": ri, "map": map_id, "cup": cup, "build": build.duplicate()})


# ---------------------------------------------------------------- garage (web: the Garage overlay)

func build_summary() -> String:
	if not KartBuilder.ready():
		return ""
	var I: Dictionary = KartBuilder.info
	var bd: Dictionary = I["bodies"][int(build["b"])]
	var lv := KartBuilder.livery(String(build.get("t", "")))
	var wd := KartBuilder.wheel_of(build)
	return String(bd["name"]) + (" · " + String(lv["name"]) if not lv.is_empty() else "") + " · " + String(wd["name"]) + (" (built in)" if bool(bd.get("bike", false)) else "") + " · " + String(I["gliders"][int(build["g"])]["name"])


func _chips(st: Array) -> HFlowContainer:
	var f := HFlowContainer.new()
	f.add_theme_constant_override("h_separation", zi(4))
	f.add_theme_constant_override("v_separation", zi(4))
	f.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var short: Array = KartBuilder.info.get("statShort", ["SPD", "ACC", "HND", "WGT", "OFF"])
	var any := false
	for i in st.size():
		var v := int(st[i])
		if v == 0:
			continue
		any = true
		var up := v > 0
		var pc := panel(box([Color(0.25, 0.55, 0.2, 0.45) if up else Color(0.6, 0.18, 0.12, 0.45)], 180.0, 5.0, Color(0, 0, 0, 0), 0.0, Vector4(5, 1, 5, 1)))
		pc.mouse_filter = Control.MOUSE_FILTER_IGNORE
		var l := label(("+" if up else "−") + str(absi(v)) + " " + String(short[i]), f_bold, 9.5, Color("#b8f0a8") if up else Color("#ffb4a0"))
		pc.add_child(l)
		f.add_child(pc)
	if not any:
		var pc2 := panel(box([Color(1, 0.957, 0.863, 0.1)], 180.0, 5.0, Color(0, 0, 0, 0), 0.0, Vector4(5, 1, 5, 1)))
		pc2.mouse_filter = Control.MOUSE_FILTER_IGNORE
		pc2.add_child(label("NEUTRAL", f_bold, 9.5, CREAM))
		f.add_child(pc2)
	return f


func _part_card(name_: String, st: Array, on: bool, dense: bool) -> Button:
	var b := Button.new()
	b.custom_minimum_size = Vector2(z(110 if dense else 140), z(48 if dense else 74))
	b.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	b.mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
	_mark_card(b, on)
	var v := vbox(4)
	v.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	v.offset_left = z(10)
	v.offset_top = z(8)
	v.offset_right = -z(8)
	v.offset_bottom = -z(6)
	v.mouse_filter = Control.MOUSE_FILTER_IGNORE
	b.add_child(v)
	var l := label(name_, f_bold, 12.0 if dense else 14.0, CHEESE if on else CREAM)
	l.text_overrun_behavior = TextServer.OVERRUN_TRIM_ELLIPSIS
	v.add_child(l)
	v.add_child(_chips(st))
	return b


func _garage() -> Control:
	var root := _screen_root()
	var I: Dictionary = KartBuilder.info
	var v := vbox(10)
	root.add_child(v)
	# header: back, title, tabs, next
	var h := hbox(14)
	var back := button("‹ Driver", "ghost", 15.0, Vector4(16, 10, 16, 10))
	back.pressed.connect(func(): open("driver"))
	h.add_child(back)
	var tv := vbox(0)
	tv.add_child(label("GARAGE", f_disp, 30.0, CHEESE, SAUCE_DARK, Vector2(0, 3)))
	tv.add_child(label("STEP 2 OF 3", f_bold, 9.0, MUTED))
	h.add_child(tv)
	var sp := Control.new()
	sp.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	h.add_child(sp)
	var is_bike := bool(I["bodies"][int(build["b"])].get("bike", false))
	var tabs := [["kart", "Karts"], ["car", "Cars"], ["bike", "Bikes"], ["glider", "Glider"], ["colour", "Colour"], ["theme", "Theme"]]
	if not is_bike:
		tabs.insert(3, ["wheel", "Wheels"])
	elif g_tab == "wheel":
		g_tab = "bike"
	h.add_child(seg("gtab", tabs, g_tab, func(k):
		g_tab = k
		open("garage"), 14.0, 6.0))
	var sp2 := Control.new()
	sp2.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	h.add_child(sp2)
	var nxt := button("CHOOSE TRACK  ›", "cta", 19.0, Vector4(20, 10, 20, 10))
	nxt.pressed.connect(func(): open("track"))
	h.add_child(nxt)
	default_focus = nxt
	v.add_child(h)
	var body := hbox(14)
	body.size_flags_vertical = Control.SIZE_EXPAND_FILL
	v.add_child(body)
	# the 3D preview
	var view := panel(box([Color(0, 0, 0, 0), Color(0, 0, 0, 0)], 180.0, 18.0, Color(1, 0.957, 0.863, 0.12), 1.0, Vector4(1, 1, 1, 1)))
	view.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	view.size_flags_stretch_ratio = 1.15
	view.clip_contents = true
	body.add_child(view)
	var vbg := ColorRect.new()
	vbg.mouse_filter = Control.MOUSE_FILTER_IGNORE
	vbg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	var vsm := ShaderMaterial.new()
	vsm.shader = load("res://shaders/gview_bg.gdshader")
	vbg.material = vsm
	vbg.resized.connect(func():
		vsm.set_shader_parameter("size_px", vbg.size)
		vsm.set_shader_parameter("radius_px", z(17.0)))
	view.add_child(vbg)
	var svc := SubViewportContainer.new()
	svc.stretch = true
	svc.mouse_filter = Control.MOUSE_FILTER_STOP
	view.add_child(svc)
	_gview = SubViewport.new()
	_gview.own_world_3d = true
	_gview.transparent_bg = true
	_gview.msaa_3d = Viewport.MSAA_4X
	svc.add_child(_gview)
	_garage_scene()
	svc.gui_input.connect(func(ev):
		if ev is InputEventMouseButton:
			_gdrag = (ev as InputEventMouseButton).pressed and (ev as InputEventMouseButton).button_index == MOUSE_BUTTON_LEFT
		elif ev is InputEventMouseMotion and _gdrag:
			_grot += (ev as InputEventMouseMotion).relative.x * 0.01)
	var over := vbox(0)
	over.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	over.mouse_filter = Control.MOUSE_FILTER_IGNORE
	view.add_child(over)
	var mg := MarginContainer.new()
	for k2 in ["margin_left", "margin_top", "margin_right", "margin_bottom"]:
		mg.add_theme_constant_override(k2, zi(12))
	mg.mouse_filter = Control.MOUSE_FILTER_IGNORE
	mg.size_flags_vertical = Control.SIZE_EXPAND_FILL
	over.add_child(mg)
	var ov := vbox(0)
	ov.mouse_filter = Control.MOUSE_FILTER_IGNORE
	mg.add_child(ov)
	var rn: String = String(racers_info[ri]["name"]) if ri < racers_info.size() else ""
	ov.add_child(label((rn + "'s " + String(I["bodies"][int(build["b"])]["name"])).to_upper(), f_disp, 19.0, CHEESE, SAUCE_DARK, Vector2(0, 2)))
	var fill := Control.new()
	fill.size_flags_vertical = Control.SIZE_EXPAND_FILL
	fill.mouse_filter = Control.MOUSE_FILTER_IGNORE
	ov.add_child(fill)
	ov.add_child(_stats_box())
	# the parts
	var side := vbox(8)
	side.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	body.add_child(side)
	var desc := ""
	var sc := ScrollContainer.new()
	sc.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	sc.size_flags_vertical = Control.SIZE_EXPAND_FILL
	var grid := GridContainer.new()
	grid.add_theme_constant_override("h_separation", zi(8))
	grid.add_theme_constant_override("v_separation", zi(8))
	grid.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	sc.add_child(grid)
	match g_tab:
		"kart", "car", "bike":
			var dense := g_tab == "car"
			grid.columns = 4 if dense else 3
			for i in (I["bodies"] as Array).size():
				var bd: Dictionary = I["bodies"][i]
				var cat := "bike" if bool(bd.get("bike", false)) else ("car" if bool(bd.get("car", false)) else "kart")
				if cat != g_tab:
					continue
				var c := _part_card(String(bd["name"]), bd["st"], i == int(build["b"]), dense)
				var bi := i
				c.pressed.connect(func():
					build["b"] = bi
					if String(build.get("t", "")) != "":
						var ok := false
						for l in KartBuilder.liveries_for(String(I["bodies"][bi]["id"])):
							if l["id"] == build["t"]:
								ok = true
						if not ok:
							build["t"] = ""
					_build_changed())
				grid.add_child(c)
			var cb: Dictionary = I["bodies"][int(build["b"])]
			desc = "[b][color=#fff4dc]%s.[/color][/b] %s" % [cb["name"], cb["desc"]]
		"wheel", "glider":
			var list: Array = I["wheels"] if g_tab == "wheel" else I["gliders"]
			var key := "w" if g_tab == "wheel" else "g"
			grid.columns = 3
			for i in list.size():
				var pd: Dictionary = list[i]
				var c2 := _part_card(String(pd["name"]), pd["st"], i == int(build[key]), false)
				var pi := i
				c2.pressed.connect(func():
					build[key] = pi
					_build_changed())
				grid.add_child(c2)
			var cp: Dictionary = list[int(build[key])]
			desc = "[b][color=#fff4dc]%s.[/color][/b] %s" % [cp["name"], cp["desc"]]
		"colour":
			grid.columns = 5
			var paints: Array = I["paints"]
			var pn: Array = I["paintNames"]
			for i in paints.size():
				var sw := Button.new()
				sw.custom_minimum_size = Vector2(z(64), z(64))
				sw.tooltip_text = String(pn[i])
				var col := Color(String(paints[i])) if paints[i] != null else Color(String(I["racers"][ri]["color"]))
				var on := i == int(build["p"]) and String(build.get("t", "")) == ""
				var st := box([col], 180.0, 32.0, CHEESE if on else Color(1, 0.957, 0.863, 0.3), 3.0 if on else 1.5)
				for s2 in ["normal", "hover", "pressed", "hover_pressed", "focus"]:
					sw.add_theme_stylebox_override(s2, st)
				var pi2 := i
				sw.pressed.connect(func():
					build["p"] = pi2
					build["t"] = ""
					_build_changed())
				grid.add_child(sw)
			desc = "[b][color=#fff4dc]%s.[/color][/b] One colour all over the kart." % pn[int(build["p"])]
		"theme":
			grid.columns = 4
			var none := _livery_card({"id": "", "name": "No theme", "A": "#5a4a40", "B": "#5a4a40", "C": "#5a4a40"}, String(build.get("t", "")) == "")
			none.pressed.connect(func():
				build["t"] = ""
				_build_changed())
			grid.add_child(none)
			for l in KartBuilder.liveries_for(String(I["bodies"][int(build["b"])]["id"])):
				var locked := Ach.liv_locked(l)
				var lc := _livery_card(l, String(l["id"]) == String(build.get("t", "")))
				var lid := String(l["id"])
				if locked:
					# a reward livery not won yet: shown with a lock; a tap says how to win it
					lc.modulate = Color(1, 1, 1, 0.55)
					var lk := _Lock.new()
					lk.custom_minimum_size = Vector2(z(16), z(16))
					lk.set_anchors_and_offsets_preset(Control.PRESET_TOP_RIGHT)
					lk.offset_left = -z(22)
					lk.offset_top = z(5)
					lk.offset_right = -z(6)
					lk.offset_bottom = z(21)
					lk.mouse_filter = Control.MOUSE_FILTER_IGNORE
					lc.add_child(lk)
					var an := ""
					for a in Ach.LIST:
						if String(a[0]) == String(l["lock"]):
							an = "[b][color=#fff4dc]%s[/color][/b]: %s" % [String(a[1]), String(a[2])]
					var hint := "[b][color=#fff4dc]%s[/color][/b] unlocks with %s" % [String(l["name"]), an if an != "" else "an achievement"]
					lc.pressed.connect(func():
						g_hint = hint
						open("garage"))
				else:
					lc.pressed.connect(func():
						build["t"] = lid
						_build_changed())
				grid.add_child(lc)
			desc = "Multi-colour liveries. Some are made for one body only."
			if g_hint != "":
				desc = g_hint
				g_hint = ""
	var rt := RichTextLabel.new()
	rt.bbcode_enabled = true
	rt.fit_content = true
	rt.scroll_active = false
	rt.add_theme_font_override("normal_font", f_med)
	rt.add_theme_font_override("bold_font", f_bold)
	rt.add_theme_font_size_override("normal_font_size", zi(12))
	rt.add_theme_font_size_override("bold_font_size", zi(12))
	rt.add_theme_color_override("default_color", MUTED)
	rt.text = desc
	side.add_child(rt)
	side.add_child(sc)
	return root


## a livery swatch: the three colours in diagonal bands, the name, as on the web's theme cards
func _livery_card(l: Dictionary, on: bool) -> Button:
	var b := Button.new()
	b.custom_minimum_size = Vector2(z(108), z(64))
	b.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	b.mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
	_mark_card(b, on)
	var v := vbox(4)
	v.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	v.offset_left = z(5)
	v.offset_top = z(5)
	v.offset_right = -z(5)
	v.offset_bottom = -z(4)
	v.mouse_filter = Control.MOUSE_FILTER_IGNORE
	b.add_child(v)
	var stripe := _Bands.new()
	stripe.cols = [Color(String(l["A"])), Color(String(l["B"])), Color(String(l["C"]))]
	stripe.custom_minimum_size.y = z(20)
	stripe.mouse_filter = Control.MOUSE_FILTER_IGNORE
	v.add_child(stripe)
	var nl := label(String(l["name"]), f_bold, 11.0, CHEESE if on else CREAM)
	nl.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	v.add_child(nl)
	return b


class _Bands extends Control:
	var cols: Array = []
	func _draw() -> void:
		if cols.size() < 3:
			return
		var w := size.x
		var h := size.y
		var r := 6.0
		var pts := CssBox.outline(Rect2(Vector2.ZERO, size), Vector4(r, r, r, r))
		draw_colored_polygon(pts, cols[0])
		# two slanted bands like the web's swatch
		for k in 2:
			var x0 := w * (0.5 + 0.17 * k)
			var poly := PackedVector2Array([Vector2(x0, h), Vector2(x0 + h * 0.6, 0), Vector2(x0 + h * 0.6 + w * 0.12, 0), Vector2(x0 + w * 0.12, h)])
			draw_colored_polygon(poly, cols[1 + k])


func _stats_box() -> Control:
	var p := panel(box([Color(0.06, 0.03, 0.02, 0.72)], 180.0, 12.0, Color(1, 0.957, 0.863, 0.12), 1.0, Vector4(10, 8, 10, 8)))
	p.size_flags_horizontal = Control.SIZE_SHRINK_BEGIN
	p.custom_minimum_size.x = z(200)
	var v := vbox(4)
	p.add_child(v)
	var hh := hbox(8)
	var sl := label("STATS", f_bold, 10.0, MUTED)
	sl.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	hh.add_child(sl)
	var sg := seg("stats", [["1", "On"], ["0", "Off"]], "1" if stats_on else "0", func(k):
		stats_on = k == "1"
		setting_changed.emit("stats", stats_on)
		open("garage"), 11.0, 3.0)
	sg.custom_minimum_size.x = z(100)
	hh.add_child(sg)
	v.add_child(hh)
	var names: Array = KartBuilder.info.get("statNames", ["Speed", "Accel", "Handling", "Weight", "Off-road"])
	var bars := KartBuilder.stat_bars(build) if stats_on else [6, 6, 6, 6, 6]
	for i in 5:
		var r := hbox(6)
		var n := label(String(names[i]).to_upper(), f_bold, 8.5, MUTED)
		n.custom_minimum_size.x = z(64)
		r.add_child(n)
		var dots := _Dots.new()
		dots.n = int(bars[i])
		dots.custom_minimum_size = Vector2(z(100), z(8))
		dots.size_flags_vertical = Control.SIZE_SHRINK_CENTER
		r.add_child(dots)
		v.add_child(r)
	return p


class _Dots extends Control:
	var n := 6
	func _draw() -> void:
		var step := size.x / 12.0
		for i in 12:
			var c := Vector2(step * (i + 0.5), size.y / 2.0)
			draw_circle(c, step * 0.32, Color("#f7a72e") if i < n else Color(1, 0.957, 0.863, 0.16))


func _build_changed() -> void:
	setting_changed.emit("build", build.duplicate())
	open("garage")


## the preview stage: a round board under the kart, a key light, the kart turning slowly
func _garage_scene() -> void:
	# the web's garage stage: a hemisphere fill and a warm key light with soft shadows, a dark crust-brown
	# floor disc with a cheese-yellow ring, ACES at exposure 1.05, over the panel's own background
	var w3 := Node3D.new()
	_gview.add_child(w3)
	var env := WorldEnvironment.new()
	var e := Environment.new()
	e.background_mode = Environment.BG_CLEAR_COLOR
	var sky := Sky.new()
	var skm := ShaderMaterial.new()
	skm.shader = load("res://shaders/sky.gdshader")
	skm.set_shader_parameter("top_col", Color("#fff1d6"))
	skm.set_shader_parameter("hor_col", Color("#ffd9a8"))
	skm.set_shader_parameter("bot_col", Color("#6b3a1e"))
	skm.set_shader_parameter("sun_col", Color("#ff8a2a"))
	sky.sky_material = skm
	sky.radiance_size = Sky.RADIANCE_SIZE_64
	e.sky = sky
	e.ambient_light_source = Environment.AMBIENT_SOURCE_SKY
	e.ambient_light_sky_contribution = 1.0
	e.ambient_light_energy = 0.75
	e.reflected_light_source = Environment.REFLECTION_SOURCE_SKY
	e.tonemap_mode = Environment.TONE_MAPPER_ACES
	e.tonemap_white = 16.0
	e.tonemap_exposure = 1.05 * (1.0 / 0.6) / 1.8
	env.environment = e
	w3.add_child(env)
	var sun := DirectionalLight3D.new()
	sun.light_energy = 2.4
	sun.light_color = Color("#fff0d8")
	sun.shadow_enabled = true
	sun.shadow_blur = 1.5
	sun.directional_shadow_mode = DirectionalLight3D.SHADOW_ORTHOGONAL
	sun.directional_shadow_max_distance = 60.0
	w3.add_child(sun)
	sun.look_at_from_position(Vector3(10, 22, 12), Vector3.ZERO, Vector3.UP)
	_gcam = Camera3D.new()
	_gcam.fov = 30.0
	w3.add_child(_gcam)
	var fl := MeshInstance3D.new()
	var disc := CylinderMesh.new()
	disc.top_radius = 15.5
	disc.bottom_radius = 15.5
	disc.height = 0.02
	disc.radial_segments = 64
	disc.rings = 1
	fl.mesh = disc
	var fm := StandardMaterial3D.new()
	fm.albedo_color = Color("#3a2216")
	fm.roughness = 0.85
	fl.material_override = fm
	fl.position.y = -0.01
	w3.add_child(fl)
	var rg := MeshInstance3D.new()
	rg.mesh = View._flat_ring(14.3, 15.0)
	var rm := StandardMaterial3D.new()
	rm.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	rm.albedo_color = Color("#f7c948")
	rm.cull_mode = BaseMaterial3D.CULL_DISABLED
	rg.material_override = rm
	rg.position.y = 0.03
	rg.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	w3.add_child(rg)
	_gturn = Node3D.new()
	w3.add_child(_gturn)
	var built := KartBuilder.build(build, ri)
	_grad = 8.0
	_gcy = 3.0
	if not built.is_empty():
		_gkart = built["node"]
		_gturn.add_child(_gkart)
		var sc := float((built["meta"] as Dictionary).get("scale", 1.76)) / 1.76
		_gturn.scale = Vector3.ONE * sc
		# frame the camera on the kart's bounds, as the web does (gModel.rad, gModel.cy)
		var bb := AABB()
		var first := true
		for mi in _gkart.find_children("*", "MeshInstance3D", true, false):
			var m := mi as MeshInstance3D
			if not m.is_visible_in_tree() or m.mesh == null:
				continue
			var ab := (_gturn.transform * _gkart.transform * _rel_xf(m, _gkart)) * m.mesh.get_aabb()
			bb = ab if first else bb.merge(ab)
			first = false
		if not first:
			_grad = bb.size.length() * 0.5
			_gcy = bb.position.y + bb.size.y * 0.5
	_frame_garage_cam()


## a node's transform relative to an ancestor
static func _rel_xf(n: Node3D, top: Node3D) -> Transform3D:
	var xf := Transform3D.IDENTITY
	var c: Node = n
	while c != null and c != top:
		if c is Node3D:
			xf = (c as Node3D).transform * xf
		c = c.get_parent()
	return xf


## web frameGarageCam (no glider unfolded, normal zoom): fit the kart's bounding sphere in a 30 degree view, raised .22 rad
func _frame_garage_cam() -> void:
	if _gcam == null or not is_instance_valid(_gcam):
		return
	var asp := 1.6
	if _gview != null and _gview.size.y > 0:
		asp = float(_gview.size.x) / float(_gview.size.y)
	var vh := deg_to_rad(15.0)
	var hh := atan(tan(vh) * asp)
	var d := _grad / sin(minf(vh, hh)) * 0.84
	var el := 0.22
	var hz := cos(el) * d
	var sh := _grad * 0.34 * minf(1.0, asp / 1.3)
	_gcam.near = maxf(0.5, minf(d - _grad * 1.6, d * 0.25))
	_gcam.far = maxf(200.0, d * 8.0)
	_gcam.look_at_from_position(Vector3(hz * 0.756 - sh * 0.654, _gcy + sin(el) * d, hz * 0.654 + sh * 0.756), Vector3(-sh * 0.654, _gcy - _grad * 0.16, sh * 0.756), Vector3.UP)


func _process(dt: float) -> void:
	if _gturn != null and is_instance_valid(_gturn) and cur == "garage":
		if not _gdrag:
			_grot += dt * 0.4
		_gturn.rotation.y = _grot
		var a := float(_gview.size.x) / maxf(1.0, float(_gview.size.y))
		if absf(a - _gasp) > 0.01:
			_gasp = a
			_frame_garage_cam()


# ---------------------------------------------------------------- overlays

func close_modal(keep_keys := false) -> void:
	if not keep_keys:
		Keys.wait = []     # a key box left waiting stops waiting when its screen closes
	if modal != null:
		modal.queue_free()
		modal = null
		for k in screens:
			(screens[k] as Control).visible = true
		modal_closed.emit()


func show_modal(kind: String) -> void:
	close_modal(kind == "set")
	var m := Control.new()
	m.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	m.mouse_filter = Control.MOUSE_FILTER_STOP
	var dim := _Backdrop.new()
	dim.dim = 1.25
	dim.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	m.add_child(dim)
	var root := _screen_root()
	m.add_child(root)
	# centred column: the web's sheets are 760 CSS px wide (Records and Awards use the whole width)
	var widths := {"how": 760.0, "set": 760.0, "tips": 760.0, "mp": 560.0}
	var row := HBoxContainer.new()
	root.add_child(row)
	var v := vbox(14)
	v.size_flags_vertical = Control.SIZE_EXPAND_FILL
	if widths.has(kind):
		var l := Control.new()
		l.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		row.add_child(l)
		v.custom_minimum_size.x = z(float(widths[kind]))
		row.add_child(v)
		var r := Control.new()
		r.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		row.add_child(r)
	else:
		v.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		row.add_child(v)
	if kind == "mp":
		var sp := Control.new()
		sp.size_flags_vertical = Control.SIZE_EXPAND_FILL
		sp.size_flags_stretch_ratio = 0.5
		v.add_child(sp)
	var titles := {"how": "How to play", "rec": "Records", "ach": "Achievements", "set": "Settings", "tips": "Best setup", "mp": "Play with friends"}
	var head := hbox(14)
	var tl := label(String(titles.get(kind, "")).to_upper(), f_disp, 44.0, CHEESE, SAUCE_DARK, Vector2(0, 4))
	tl.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	head.add_child(tl)
	var done := button("DONE" if kind != "mp" else "✕", "cta" if kind != "mp" else "ghost", 19.0, Vector4(28, 10, 28, 10) if kind != "mp" else Vector4(14, 8, 14, 8))
	done.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	done.pressed.connect(close_modal)
	head.add_child(done)
	v.add_child(head)
	var content: Control = _modal_body(kind)
	content.size_flags_vertical = Control.SIZE_EXPAND_FILL if kind != "mp" else Control.SIZE_SHRINK_BEGIN
	v.add_child(content)
	if kind == "mp":
		var sp2 := Control.new()
		sp2.size_flags_vertical = Control.SIZE_EXPAND_FILL
		v.add_child(sp2)
	modal = m
	add_child(m)
	for k in screens:
		(screens[k] as Control).visible = false
	default_focus = done


var modal_builders := {}   # kind -> Callable returning a Control (set by main for settings and online)
var rec_cls := ""
const CLS_LABEL := {"small": "50cc", "medium": "100cc", "large": "200cc", "reverse": "Reverse"}


static func fmt_time(t: float) -> String:
	if t < 0.0:
		return "--:--.--"
	return "%d:%05.2f" % [int(t) / 60, fmod(t, 60.0)]


static func fmt_date(unix: int) -> String:
	var dt := Time.get_datetime_dict_from_unix_time(unix)
	var mon: String = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"][clampi(int(dt["month"]) - 1, 0, 11)]
	return "%s %d" % [mon, int(dt["day"])]


func _racer_name(i: int) -> String:
	return String(racers_info[i]["name"]) if i >= 0 and i < racers_info.size() else "?"


## web #records: personal bests for every track at one speed class, and the latest races
func _records() -> Control:
	if rec_cls == "":
		rec_cls = cls
	var row := hbox(22)
	var left := vbox(10)
	left.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	left.size_flags_stretch_ratio = 1.9
	row.add_child(left)
	var lh := hbox(12)
	var sl := section_label("Personal bests")
	sl.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	lh.add_child(sl)
	var opts: Array = []
	for k in ["small", "medium", "large", "reverse"]:
		opts.append([k, CLS_LABEL[k]])
	lh.add_child(seg("reccls", opts, rec_cls, func(k):
		rec_cls = k
		show_modal("rec"), 14.0, 6.0))
	left.add_child(lh)
	var sc := ScrollContainer.new()
	sc.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	sc.size_flags_vertical = Control.SIZE_EXPAND_FILL
	left.add_child(sc)
	var g := GridContainer.new()
	g.columns = 3
	g.add_theme_constant_override("h_separation", zi(8))
	g.add_theme_constant_override("v_separation", zi(8))
	g.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	sc.add_child(g)
	var ms := maps.duplicate()
	ms.sort_custom(func(a, b): return int(a.get("mi", 0)) < int(b.get("mi", 0)))
	for m in ms:
		var id := String(m["id"])
		var r := Ach.best(id, rec_cls)
		var card := panel(glass(10.0, Vector4(6, 6, 10, 6)))
		card.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		var h := hbox(10)
		card.add_child(h)
		var pic := _Portrait.new()
		pic.tex = _shot(id, "h")
		pic.radius = 6.0
		pic.custom_minimum_size = Vector2(z(60), z(40))
		h.add_child(pic)
		var tv := vbox(0)
		tv.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		var nm := label(String(m.get("name", id)), f_bold, 14.0, Color("#fff4dc"))
		nm.text_overrun_behavior = TextServer.OVERRUN_TRIM_ELLIPSIS
		nm.clip_text = true
		tv.add_child(nm)
		tv.add_child(label((_racer_name(int(r["dr"])) + " · " + fmt_date(int(r["d"]))) if not r.is_empty() else "No time yet", f_med, 12.0, MUTED))
		h.add_child(tv)
		var tm := label(fmt_time(float(r["t"])) if not r.is_empty() else "–", f_bold, 14.0, CHEESE if not r.is_empty() else MUTED)
		tm.size_flags_vertical = Control.SIZE_SHRINK_BEGIN
		h.add_child(tm)
		g.add_child(card)
	var right := vbox(10)
	right.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	row.add_child(right)
	right.add_child(section_label("Recent races"))
	var hs := ScrollContainer.new()
	hs.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	hs.size_flags_vertical = Control.SIZE_EXPAND_FILL
	right.add_child(hs)
	var hl := vbox(6)
	hl.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	hs.add_child(hl)
	var hist := Ach.history()
	if hist.is_empty():
		var e := panel(glass(10.0, Vector4(12, 10, 12, 10)))
		e.add_child(label("Finish a race and it will show up here.", f_med, 15.0, MUTED))
		hl.add_child(e)
	var names := {}
	for m2 in maps:
		names[String(m2["id"])] = String(m2.get("name", m2["id"]))
	for hq in hist:
		var hd: Dictionary = hq
		var hc := panel(glass(10.0, Vector4(12, 7, 12, 7)))
		var hh := hbox(10)
		hc.add_child(hh)
		var pl := int(hd.get("p", 0))
		hh.add_child(label("%d%s" % [pl, ["th", "st", "nd", "rd"][pl if pl < 4 and pl > 0 else 0] if not (pl >= 11 and pl <= 13) else "th"], f_disp, 16.0, CHEESE))
		var hv := vbox(0)
		hv.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		hv.add_child(label(String(names.get(String(hd.get("m", "")), hd.get("m", ""))), f_bold, 14.0, Color("#fff4dc")))
		hv.add_child(label("%s · %s · %s" % [String(CLS_LABEL.get(String(hd.get("c", "")), hd.get("c", ""))), _racer_name(int(hd.get("dr", 0))), fmt_date(int(hd.get("d", 0)))], f_med, 11.0, MUTED))
		hh.add_child(hv)
		hh.add_child(label(fmt_time(float(hd.get("t", 0.0))) + ("  PB" if bool(hd.get("pb", false)) else ""), f_bold, 14.0, Color("#7fe07a") if bool(hd.get("pb", false)) else Color("#fff4dc")))
		hl.add_child(hc)
	return row


## web #achievements: twenty lifetime goals, each with its reward livery and progress
func _achievements() -> Control:
	var v := vbox(12)
	var top := hbox(10)
	top.add_child(label(str(Ach.n_unlocked()), f_disp, 22.0, CHEESE))
	top.add_child(label("of %d unlocked" % Ach.LIST.size(), f_semi, 17.0, Color("#fff4dc")))
	if Ach.cheat:
		var ct := panel(box([Color("#ff6a3d"), Color("#ff6a3d")], 180.0, 6.0, Color(0, 0, 0, 0), 0.0, Vector4(8, 2, 8, 2)))
		ct.add_child(label("CHEAT ON", f_bold, 11.0, Color("#fff4dc")))
		ct.size_flags_vertical = Control.SIZE_SHRINK_CENTER
		top.add_child(ct)
	var note := label("Every achievement unlocks a reward livery. The full pattern paints onto car bodies; karts take its colours.", f_med, 13.0, MUTED)
	note.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	top.add_child(note)
	v.add_child(top)
	var sc := ScrollContainer.new()
	sc.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	sc.size_flags_vertical = Control.SIZE_EXPAND_FILL
	v.add_child(sc)
	var g := GridContainer.new()
	g.columns = 4
	g.add_theme_constant_override("h_separation", zi(14))
	g.add_theme_constant_override("v_separation", zi(14))
	g.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	sc.add_child(g)
	for a in Ach.LIST:
		var won := Ach.unlocked(String(a[0]))
		var lv := KartBuilder.livery(String(a[5])) if KartBuilder.ready() else {}
		var card := panel(box([Color(1, 0.957, 0.863, 0.06), Color(1, 0.957, 0.863, 0.015)], 160.0, 16.0, Color(0.97, 0.79, 0.28, 0.6) if won else Color(1, 0.957, 0.863, 0.12), 1.0, Vector4(0, 0, 0, 0)))
		card.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		var cv := vbox(0)
		card.add_child(cv)
		# the reward: its colours as a swatch, its name on a tag, a padlock until won
		var sw := _LivSwatch.new()
		sw.cols = [Color(String(lv.get("A", "#5a4a40"))), Color(String(lv.get("B", "#5a4a40"))), Color(String(lv.get("C", "#5a4a40")))]
		sw.radius = z(16.0)
		sw.custom_minimum_size = Vector2(0, z(150))
		cv.add_child(sw)
		var tag := panel(box([Color(0.07, 0.035, 0.02, 0.82), Color(0.07, 0.035, 0.02, 0.82)], 180.0, 6.0, Color(0, 0, 0, 0), 0.0, Vector4(8, 3, 8, 3)))
		tag.add_child(label(String(lv.get("name", a[5])).to_upper(), f_bold, 11.0, CHEESE))
		tag.position = Vector2(z(12), z(150) - z(32))
		sw.add_child(tag)
		if not won:
			var lk := _Lock.new()
			lk.position = Vector2(0, z(14))
			lk.size = Vector2(z(16), z(16))
			lk.mouse_filter = Control.MOUSE_FILTER_IGNORE
			sw.lock = lk
			sw.add_child(lk)
		var body := vbox(4)
		var mg := MarginContainer.new()
		for k2 in ["margin_left", "margin_right"]:
			mg.add_theme_constant_override(k2, zi(14))
		mg.add_theme_constant_override("margin_top", zi(10))
		mg.add_theme_constant_override("margin_bottom", zi(14))
		mg.add_child(body)
		cv.add_child(mg)
		body.add_child(label(String(a[1]), f_bold, 18.0, Color("#fff4dc")))
		var dl := label(String(a[2]), f_med, 13.0, MUTED)
		dl.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		body.add_child(dl)
		if String(a[6]) != "":
			var rt := RichTextLabel.new()
			rt.bbcode_enabled = true
			rt.fit_content = true
			rt.scroll_active = false
			rt.add_theme_font_override("normal_font", f_med)
			rt.add_theme_font_override("bold_font", f_bold)
			rt.add_theme_font_size_override("normal_font_size", zi(13))
			rt.add_theme_font_size_override("bold_font_size", zi(13))
			rt.add_theme_color_override("default_color", MUTED)
			rt.text = "Also unlocks the [b][color=#fff4dc]%s[/color][/b] item" % String(Ach.ITEM_NAMES.get(String(a[6]), a[6]))
			body.add_child(rt)
		var nd := Ach.need(a)
		var val := float(nd) if Ach.cheat else minf(Ach.value(a), float(nd))
		var bar := _Bar.new()
		bar.f = val / maxf(1.0, float(nd))
		bar.custom_minimum_size = Vector2(0, z(7))
		body.add_child(bar)
		var shown := ("%d:%02d" % [int(val) / 60, int(val) % 60]) if String(a[3]) == "glide" else str(int(val))
		var need_s := ("%d:%02d" % [nd / 60, nd % 60]) if String(a[3]) == "glide" else str(nd)
		var won_txt := "Unlocked by cheat code" if Ach.cheat and not (Ach.d["u"] as Dictionary).has(String(a[0])) else "Unlocked"
		body.add_child(label((won_txt if won else "%s / %s" % [shown, need_s]), f_med, 12.0, Color("#7fe07a") if won else MUTED))
		g.add_child(card)
	return v


class _LivSwatch extends Control:
	## a reward livery's colours, diagonal, rounded at the top (the web shows the livery painted on a car)
	var cols: Array = []
	var radius := 16.0
	var lock: Control = null
	func _draw() -> void:
		var r := Rect2(Vector2.ZERO, size)
		var pts := CssBox.outline(r, Vector4(radius, radius, 0, 0))
		var pc := PackedColorArray()
		for p in pts:
			var t := clampf((p.x / maxf(1.0, size.x) + p.y / maxf(1.0, size.y)) * 0.5, 0.0, 1.0)
			var c: Color = cols[0].lerp(cols[1], clampf(t / 0.6, 0.0, 1.0)) if t < 0.6 else cols[1].lerp(cols[2], (t - 0.6) / 0.4)
			pc.append(c)
		draw_polygon(pts, pc)
		if lock != null:
			lock.position = Vector2(size.x - lock.size.x - 14.0 * size.y / 150.0, 14.0 * size.y / 150.0)
			draw_circle(lock.position + lock.size / 2.0, lock.size.x * 0.95, Color(0.07, 0.035, 0.02, 0.8))


class _Bar extends Control:
	## a progress bar: dark track, cheese-yellow fill
	var f := 0.0
	func _draw() -> void:
		var r := size.y / 2.0
		draw_rect(Rect2(r, 0, size.x - 2.0 * r, size.y), Color(1, 0.957, 0.863, 0.1))
		draw_circle(Vector2(r, r), r, Color(1, 0.957, 0.863, 0.1))
		draw_circle(Vector2(size.x - r, r), r, Color(1, 0.957, 0.863, 0.1))
		if f > 0.001:
			var w := maxf(2.0 * r, size.x * clampf(f, 0.0, 1.0))
			draw_rect(Rect2(r, 0, w - 2.0 * r, size.y), Color("#f7c948"))
			draw_circle(Vector2(r, r), r, Color("#f7c948"))
			draw_circle(Vector2(w - r, r), r, Color("#f7c948"))


func _modal_body(kind: String) -> Control:
	if modal_builders.has(kind):
		return (modal_builders[kind] as Callable).call()
	if kind == "rec":
		return _records()
	if kind == "ach":
		return _achievements()
	var sc := ScrollContainer.new()
	sc.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	var g := GridContainer.new()
	g.columns = 2
	g.add_theme_constant_override("h_separation", zi(14))
	g.add_theme_constant_override("v_separation", zi(14))
	g.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	sc.add_child(g)
	var items: Array = how_to() if kind == "how" else (TIPS if kind == "tips" else [["", "Coming to the PC version soon."]])
	for it in items:
		var card := panel(glass(16.0, Vector4(16, 14, 16, 14)))
		card.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		var rt := RichTextLabel.new()
		rt.bbcode_enabled = true
		rt.fit_content = true
		rt.scroll_active = false
		rt.add_theme_font_override("normal_font", f_med)
		rt.add_theme_font_override("bold_font", f_bold)
		rt.add_theme_font_size_override("normal_font_size", zi(15))
		rt.add_theme_font_size_override("bold_font_size", zi(15))
		rt.add_theme_color_override("default_color", MUTED)
		rt.text = ("[b][color=#fff4dc]%s[/color][/b] " % it[0] if String(it[0]) != "" else "") + String(it[1])
		rt.custom_minimum_size.x = z(380)
		card.add_child(rt)
		g.add_child(card)
	return sc


## How to play (the keys named are your current ones)
static func how_to() -> Array:
	return [
		["Driving.", "Your kart accelerates on its own. Steer with %s and %s, or the left stick. Hold the Drift / Brake key (%s; LT on a controller) to brake or reverse when you're slow." % [Keys.list("left"), Keys.list("right"), Keys.list("brake")]],
		["Hazards.", "Some tracks have slow traffic to weave through, critters that spin you out, pools that swallow karts (you get fished out a moment later) and a train crossing. Hit the ramp before the crossing to jump the train."],
		["Drift.", "At speed, tap Drift once to start drifting. It stays on by itself. Steer to guide the slide. Straighten out too much and the drift ends on its own, or tap Drift again to end it. Sparks go yellow, orange, then red, and ending the drift gives you a boost."],
		["Awards.", "Achievements track your racing across every session: wins, podiums, drift boosts, loops, glide time and more."],
		["Items.", "You can hold two, side by side. %s uses the first, %s the second: traps drop onto the road behind you, everything else fires forward. Hold %s (X on a controller) to look back; items fire backwards while you look." % [Keys.list("item1"), Keys.list("item2"), Keys.list("look")]],
		["Chili Boost.", "A burst of speed that works even on the cheese."],
	]

const TIPS := [
	["Pick a graphics preset.", "Pause, then Graphics: Ultra on a gaming PC, High on most others, Low on older laptops."],
	["Frame rate.", "The PC version runs at your monitor's rate. Choose 60 fps in the pause menu if it feels uneven."],
	["Full screen.", "F11 switches between full screen and a window."],
]
