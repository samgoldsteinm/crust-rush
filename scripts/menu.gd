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
		elif cur == "track":
			open("driver")
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
	func _draw() -> void:
		var r := get_rect()
		var w := r.size.x
		var h := r.size.y
		var top := Color(0.16, 0.07, 0.04, 0.66 * dim)
		var bot := Color(0.06, 0.025, 0.015, 0.8 * dim)
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
	var s: Control
	match name_:
		"home":
			s = _home()
		"driver":
			s = _driver()
		"track":
			s = _track()
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
	v.add_child(_step_head("‹ Back", "home", "Step 1 of 2", "Choose your driver", "CHOOSE TRACK  ›", func(): open("track")))
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
	var fade := false
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
		var pts := CssBox.outline(r, Vector4.ONE * radius)
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
	var v := vbox(10)
	root.add_child(v)
	var cls_label := ""
	for c in CLASSES:
		if c[0] == cls:
			cls_label = c[1]
	v.add_child(_step_head("‹ Driver", "driver", "Step 2 of 2 · " + cls_label, "Grand Prix" if mode == "gp" else "Track", "START RACE", func(): _go()))
	var body := hbox(16)
	body.size_flags_vertical = Control.SIZE_EXPAND_FILL
	v.add_child(body)
	var left := vbox(10)
	left.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	left.size_flags_stretch_ratio = 1.5
	body.add_child(left)
	var detail := panel(glass(18.0, Vector4(14, 14, 14, 14)))
	detail.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	body.add_child(detail)
	var dv := vbox(10)
	detail.add_child(dv)
	var cups_row := hbox(8)
	left.add_child(cups_row)
	var grid := GridContainer.new()
	grid.columns = 4
	grid.add_theme_constant_override("h_separation", zi(10))
	grid.add_theme_constant_override("v_separation", zi(10))
	var sc := ScrollContainer.new()
	sc.size_flags_vertical = Control.SIZE_EXPAND_FILL
	sc.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	sc.add_child(grid)
	grid.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	left.add_child(sc)
	var refresh: Callable
	var show_detail := func(id: String):
		for c in dv.get_children():
			c.queue_free()
		var m := _map(id)
		var tr := TextureRect.new()
		tr.texture = _shot(id, "h")
		tr.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		tr.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_COVERED
		tr.custom_minimum_size = Vector2(z(300), z(170))
		dv.add_child(tr)
		dv.add_child(label(String(m.get("name", id)).to_upper(), f_disp, 22.0, CHEESE, SAUCE_DARK))
		var ci := int(m.get("cup", -1))
		dv.add_child(label(CUPS[ci][0] if ci >= 0 and ci < CUPS.size() else "Special track", f_bold, 13.0, MUTED))
		if mode == "gp" and ci >= 0:
			var names := PackedStringArray()
			for mm in maps:
				if int(mm.get("cup", -1)) == ci:
					names.append(String(mm["name"]))
			dv.add_child(para("Four races: " + ", ".join(names) + ". Points after every race; the most points wins the cup.", 13.0, MUTED, 280.0))
	refresh = func():
		for c in grid.get_children():
			c.queue_free()
		for m in maps:
			var id: String = m["id"]
			if mode == "gp" and int(m.get("cup", -1)) != cup:
				continue
			var card := _map_card(m)
			card.pressed.connect(func():
				map_id = id
				setting_changed.emit("map", id)
				show_detail.call(id)
				for c in grid.get_children():
					_mark_card(c as Button, String(c.get_meta("id")) == map_id))
			grid.add_child(card)
	for ci in CUPS.size():
		var cb := button(String(CUPS[ci][0]), "seg_on" if ci == cup else "seg_off", 14.0, Vector4(12, 8, 12, 8))
		cb.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		cb.pressed.connect(func():
			cup = ci
			if mode == "gp":
				for mm in maps:
					if int(mm.get("cup", -1)) == ci:
						map_id = String(mm["id"])
						break
			setting_changed.emit("cup", ci)
			open("track"))
		cups_row.add_child(cb)
	refresh.call()
	show_detail.call(map_id)
	return root


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
	b.custom_minimum_size = Vector2(z(150), z(112))
	b.mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
	_mark_card(b, id == map_id)
	var v := vbox(4)
	v.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	v.mouse_filter = Control.MOUSE_FILTER_IGNORE
	b.add_child(v)
	var tr := TextureRect.new()
	tr.texture = _shot(id, "h")
	tr.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	tr.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_COVERED
	tr.size_flags_vertical = Control.SIZE_EXPAND_FILL
	tr.mouse_filter = Control.MOUSE_FILTER_IGNORE
	v.add_child(tr)
	var l := label(String(m.get("name", id)), f_bold, 13.0, CREAM)
	l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	l.text_overrun_behavior = TextServer.OVERRUN_TRIM_ELLIPSIS
	v.add_child(l)
	return b


func _go() -> void:
	go.emit({"mode": mode, "cls": cls, "ri": ri, "map": map_id, "cup": cup})


# ---------------------------------------------------------------- overlays

func close_modal() -> void:
	if modal != null:
		modal.queue_free()
		modal = null
		for k in screens:
			(screens[k] as Control).visible = true


func show_modal(kind: String) -> void:
	close_modal()
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


func _modal_body(kind: String) -> Control:
	if modal_builders.has(kind):
		return (modal_builders[kind] as Callable).call()
	var sc := ScrollContainer.new()
	sc.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	var g := GridContainer.new()
	g.columns = 2
	g.add_theme_constant_override("h_separation", zi(14))
	g.add_theme_constant_override("v_separation", zi(14))
	g.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	sc.add_child(g)
	var items: Array = HOW_TO if kind == "how" else (TIPS if kind == "tips" else [["", "Coming to the PC version soon."]])
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


const HOW_TO := [
	["Driving.", "Your kart accelerates on its own. Steer with the arrow keys, A and D, or the left stick. Hold the Drift / Brake key (Space, S or Down; LT on a controller) to brake or reverse when you're slow."],
	["Hazards.", "Some tracks have slow traffic to weave through, critters that spin you out, pools that swallow karts (you get fished out a moment later) and a train crossing. Hit the ramp before the crossing to jump the train."],
	["Drift.", "At speed, tap Drift once to start drifting. It stays on by itself. Steer to guide the slide. Straighten out too much and the drift ends on its own, or tap Drift again to end it. Sparks go yellow, orange, then red, and ending the drift gives you a boost."],
	["Awards.", "Achievements track your racing across every session: wins, podiums, drift boosts, loops, glide time and more."],
	["Items.", "You can hold two, side by side. X or Enter uses the first, Z the second: traps drop onto the road behind you, everything else fires forward. Hold F (X on a controller) to look back; items fire backwards while you look."],
	["Chili Boost.", "A burst of speed that works even on the cheese."],
]

const TIPS := [
	["Pick a graphics preset.", "Pause, then Graphics: Ultra on a gaming PC, High on most others, Low on older laptops."],
	["Frame rate.", "The PC version runs at your monitor's rate. Choose 60 fps in the pause menu if it feels uneven."],
	["Full screen.", "F11 switches between full screen and a window."],
]
