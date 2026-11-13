class_name Menu
extends Control
## The web game's menus, rebuilt to look the same: home (mode, speed class, tools, Choose driver,
## Play with friends), driver select, track select (cups and track cards), and the overlays (How to
## play, Records, Awards, Settings, Best setup, Play with friends). Drawn over the live track like the
## web's demo view. Sizes are the web's CSS pixels times its zoom at 1280x720 (Z).

signal go(opts: Dictionary)          # start a race: {mode, cls, ri, map, cup}
signal net_ready                     # in a friends' room: the guest is done in the garage (web: Ready)
signal net_track(map: String)        # in a friends' room: the host has picked the track
signal net_room                      # back to the room's lobby
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
const CUPS := [["Margherita Cup", "#f7c948"], ["Supreme Cup", "#3f9a35"], ["Deep Dish Cup", "#e0452c"], ["Meat Lover's Cup", "#b06a3c"], ["Neon Cup", "#3ff0ff"], ["Miniature Mayhem Cup", "#ff6a12"]]

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
var _gzoom := 1.0             # web gZoom: the camera's distance (1 = the normal framing, .32 right up close, 1.5 far)
var _gzc := 1.0               # the distance eased towards _gzoom
var _gpitch := 0.0            # web gPitch: extra height above the usual .22 rad (dragging up and down in the inspect view)
var _gpc := 0.0
var _gbig := false            # web gBig: the full-screen inspect view
var _gtap := Vector2(-1, -1)  # where a press on the preview started (a click without a drag opens the inspect view)
var _gtap_t := 0
var _g_hide: Array = []       # what the inspect view hides: the header, the parts list, the stats
var _g_hint: Control
var _g_insp: Button
var _g_next: Control
var liv_cat := "all"           # the livery list's category (web livCat)
var favs := {}                 # body id -> favourite livery ids (web isFav), saved with the settings
var _thumbs: LivThumbs         # the livery pictures (scripts/liv_thumbs.gd), kept for the session
var _g_list: ScrollContainer   # the garage's parts or livery list
var _g_keep := {}              # the list's place across a rebuild: tab, category, scroll, the highlighted card
var _liv_order := {"key": "", "ids": []}   # the All list's order for this visit (a new favourite stays put until you come back)
## the web's livery categories (LIV_CATS)
const LIV_CATS := [["all", "All"], ["fav", "♥ Favourites"], ["sig", "★ Signature"], ["f1", "Formula"], ["super", "Supercar"], ["endure", "Endurance"],
	["classic", "Classic"], ["street", "Street & Truck"], ["wild", "Wild"], ["pizza", "Pizza"], ["kustom", "Kustom Shop"], ["reward", "★ Rewards"]]
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
var modal_kind := ""
var net := ""                  # in a friends' room (web rooms): "", "guest" or "host"; the steps then lead back to the room
var default_focus: Control = null


## keyboard or controller: the first move puts the focus on the screen's main button
func _input(ev: InputEvent) -> void:
	if not visible:
		return
	if ev is InputEventMouseButton or ev is InputEventMouseMotion:
		return
	var nav := ev.is_action_pressed("ui_up") or ev.is_action_pressed("ui_down") or ev.is_action_pressed("ui_left") or ev.is_action_pressed("ui_right")
	var acc := ev.is_action_pressed("ui_accept")
	var fo := get_viewport().gui_get_focus_owner()
	# nothing (or something no longer on screen) has the focus: give it to this screen's main button. A move only
	# shows where the focus is; A (or Enter) then goes on to press that button, so A is never swallowed
	# up or down with nothing further that way to move the border to (a long page of text, the bottom of a list):
	# the page scrolls instead, as on the web, so the d-pad and the left stick can reach everything
	var vdir := fresh_vdir(ev)
	if vdir != 0:
		nav_scroll.call_deferred(modal if modal != null else screens.get(cur), get_viewport().gui_get_focus_owner(), vdir)
	if ev is InputEventJoypadButton or ev is InputEventJoypadMotion:
		if nav or acc:
			_pad_mode = true
	elif ev is InputEventKey:
		_pad_mode = false
	var lost := fo == null or not fo.is_visible_in_tree() or (modal != null and not modal.is_ancestor_of(fo))
	if (nav or acc) and lost:
		# as the web's controller: with nothing highlighted, a move or A only puts the yellow border on the screen
		# (on your current pick when the screen has one); A then picks what's highlighted, and the screen's
		# button (Build kart, Start race) is pressed only when the border is on it
		var tgt := _focus_target()
		if tgt != null:
			tgt.grab_focus()
			get_viewport().set_input_as_handled()
	# X on a controller (or F) favourites the highlighted livery, or the one on the car (web)
	if cur == "garage" and modal == null and g_tab == "theme" and not _gbig:
		var xk := (ev is InputEventJoypadButton and (ev as InputEventJoypadButton).pressed and (ev as InputEventJoypadButton).button_index == JOY_BUTTON_X) \
			or (ev is InputEventKey and (ev as InputEventKey).pressed and not (ev as InputEventKey).echo and (ev as InputEventKey).keycode == KEY_F)
		if xk:
			var f2 := get_viewport().gui_get_focus_owner()
			var fid := String(f2.get_meta("liv")) if f2 != null and f2.has_meta("liv") else String(build.get("t", ""))
			if fid != "":
				_toggle_fav(fid)
				get_viewport().set_input_as_handled()
				return
	# the bumpers go from garage tab to garage tab (Karts, Cars, Bikes, Wheels, Glider, Theme); the border stays on the tabs
	if cur == "garage" and modal == null and not _gbig and ev is InputEventJoypadButton and (ev as InputEventJoypadButton).pressed:
		var jb := ev as InputEventJoypadButton
		if jb.button_index == JOY_BUTTON_LEFT_SHOULDER or jb.button_index == JOY_BUTTON_RIGHT_SHOULDER:
			_pad_mode = true
			var tabs := _garage_tabs()
			var ti := tabs.find(g_tab)
			var ni := clampi(ti + (1 if jb.button_index == JOY_BUTTON_RIGHT_SHOULDER else -1), 0, tabs.size() - 1)
			if ni != ti:
				g_tab = tabs[ni]
				_focus_after = "s:gtab:" + g_tab
				open("garage")
			get_viewport().set_input_as_handled()
			return
	if ev.is_action_pressed("ui_cancel"):
		if modal != null:
			close_modal()
		elif cur == "driver":
			open("home")
		elif cur == "garage":
			if _gbig:
				_set_big(false)
			else:
				open("driver")
		elif cur == "track":
			open("garage" if KartBuilder.ready() else "driver")
		get_viewport().set_input_as_handled()
var _seg_groups := {}
var _pad_mode := false          # the controller (or keys) was used last: screens open with the border showing
var sel_focus: Control = null   # this screen's current pick (driver, track, cup), where the border starts
var _focus_after := ""          # a control to put the border back on after the screen is rebuilt (its key)


const TAB_NAMES := {"kart": "Karts", "car": "Cars", "bike": "Bikes", "wheel": "Wheels", "glider": "Glider", "theme": "Theme"}


## the garage's tabs for the current body (a bike's wheels are its own: no Wheels tab)
func _garage_tabs() -> Array:
	var bd: Dictionary = KartBuilder.info["bodies"][int(build["b"])] if KartBuilder.ready() else {}
	var t := ["kart", "car", "bike"]
	if not bool(bd.get("bike", false)):
		t.append("wheel")
	t.append_array(["glider", "theme"])
	return t


## where the highlight goes when nothing has it: the open pop-up's first button, else this screen's current pick,
## else its main button
func _focus_target() -> Control:
	if modal != null:
		return _first_focusable(modal)
	if sel_focus != null and is_instance_valid(sel_focus) and sel_focus.is_visible_in_tree():
		return sel_focus
	if default_focus != null and is_instance_valid(default_focus) and default_focus.is_visible_in_tree():
		return default_focus
	return _first_focusable(screens.get(cur))


## the first button (or other control that takes the focus) showing under a node, in reading order
static func _first_focusable(n: Node) -> Control:
	if n == null or not is_instance_valid(n):
		return null
	if n is Control and (n as Control).focus_mode == Control.FOCUS_ALL and (n as Control).is_visible_in_tree() and not (n is Button and (n as Button).disabled):
		return n as Control
	for c in n.get_children():
		var f := _first_focusable(c)
		if f != null:
			return f
	return null


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
			normal.shadow(Vector2(0, 10), 26.0, Color(0.88, 0.27, 0.17, 0.24)).shadow(Vector2(0, 5), 0.0, SAUCE_DARK)
			hover = box([[0.0, Color("#ffab45")], [0.55, Color("#ec5537")], [1.0, Color("#d03a16")]], 135.0, 14.0, Color(0, 0, 0, 0), 0.0, pad)
			hover.shadow(Vector2(0, 10), 26.0, Color(0.88, 0.27, 0.17, 0.32)).shadow(Vector2(0, 5), 0.0, SAUCE_DARK)
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
			normal.shadow(Vector2(0, 4), 12.0, Color(0.88, 0.27, 0.17, 0.32))
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


## a slider (the web's input[type=range] in .vol): a sauce-orange filled track, a round cream knob and the value
## beside it, e.g. "75%". Calls on_change(value) as it moves.
func slider(lo: float, hi: float, step: float, val: float, fmt: String, on_change: Callable) -> HBoxContainer:
	var row := hbox(12)
	var sl := HSlider.new()
	sl.min_value = lo
	sl.max_value = hi
	sl.step = step
	sl.value = val
	sl.focus_mode = Control.FOCUS_ALL
	sl.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	sl.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	sl.custom_minimum_size = Vector2(z(200), z(28))
	sl.mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
	var trk := StyleBoxFlat.new()
	trk.bg_color = Color(1, 0.957, 0.863, 0.14)
	trk.set_corner_radius_all(zi(4))
	trk.content_margin_top = z(4)
	trk.content_margin_bottom = z(4)
	var fill := StyleBoxFlat.new()
	fill.bg_color = Color("#ff7a24")
	fill.set_corner_radius_all(zi(4))
	fill.content_margin_top = z(4)
	fill.content_margin_bottom = z(4)
	var fill_hi := fill.duplicate() as StyleBoxFlat
	fill_hi.bg_color = Color("#ff9a3a")
	sl.add_theme_stylebox_override("slider", trk)
	sl.add_theme_stylebox_override("grabber_area", fill)
	sl.add_theme_stylebox_override("grabber_area_highlight", fill_hi)
	sl.add_theme_icon_override("grabber", _knob(false))
	sl.add_theme_icon_override("grabber_highlight", _knob(true))
	sl.add_theme_icon_override("grabber_disabled", _knob(false))
	var foc := StyleBoxFlat.new()
	foc.draw_center = false
	foc.border_color = CHEESE
	foc.set_border_width_all(zi(2))
	foc.set_corner_radius_all(zi(8))
	foc.expand_margin_left = z(6)
	foc.expand_margin_right = z(6)
	foc.expand_margin_top = z(2)
	foc.expand_margin_bottom = z(2)
	sl.add_theme_stylebox_override("focus", foc)
	row.add_child(sl)
	var out := label(fmt % val, f_bold, 15.0, CREAM)
	out.custom_minimum_size.x = z(56)
	out.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	row.add_child(out)
	sl.value_changed.connect(func(v):
		out.text = fmt % v
		on_change.call(v))
	return row


var _knobs := {}
func _knob(hi: bool) -> Texture2D:
	if _knobs.has(hi):
		return _knobs[hi]
	var n := zi(22) * 2
	var img := Image.create(n, n, false, Image.FORMAT_RGBA8)
	var c := Vector2(n, n) / 2.0 - Vector2(0.5, 0.5)
	for y in n:
		for x in n:
			var d := Vector2(x, y).distance_to(c)
			var r := n * 0.5 - 2.0
			var a := clampf(r - d + 0.5, 0.0, 1.0)
			var col := Color("#fff4dc") if d < r - 3.0 else (Color("#ff9a3a") if hi else Color("#e0452c"))
			col.a = a
			img.set_pixel(x, y, col)
	img.resize(zi(22), zi(22), Image.INTERPOLATE_LANCZOS)
	var t := ImageTexture.create_from_image(img)
	_knobs[hi] = t
	return t


func icon_tex(name_: String) -> Texture2D:
	var p := "res://assets/ui/ic_%s.svg" % name_
	return load(p) if ResourceLoader.exists(p) else null


## a segmented control (.seg): options [[key, text]], the chosen key, called with the new key
func seg(group: String, options: Array, chosen: String, on_pick: Callable, size_css := 15.0, pad_y := 10.0, pad_x := 4.0) -> PanelContainer:
	var pc := PanelContainer.new()
	var st := glass(14.0, Vector4(4, 4, 4, 4))
	pc.add_theme_stylebox_override("panel", st)
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", zi(4))
	pc.add_child(row)
	var btns := {}
	for o in options:
		var key: String = o[0]
		var b := button(String(o[1]), "seg_on" if key == chosen else "seg_off", size_css, Vector4(pad_x, pad_y, pad_x, pad_y))
		b.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		b.set_meta("seg", group + ":" + key)
		b.pressed.connect(func():
			_seg_select(group, key)
			on_pick.call(key))
		row.add_child(b)
		btns[key] = b
	_seg_groups[group] = {"btns": btns, "size": size_css, "pad": pad_y, "padx": pad_x}
	return pc


func _seg_select(group: String, key: String) -> void:
	var g: Dictionary = _seg_groups[group]
	for k in g["btns"]:
		var b: Button = g["btns"][k]
		var px := float(g.get("padx", 4.0))
		var nb := button(b.text, "seg_on" if k == key else "seg_off", float(g["size"]), Vector4(px, float(g["pad"]), px, float(g["pad"])))
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
func logo(text: String, size_css: float, fit := false) -> Control:
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
	# the logo shrinks to the room it has (down to 60%) rather than pushing the screen wider than the window: at
	# 1280 x 720 its full width plus the home panel ran the panel off the right edge
	if not fit:
		return holder
	var nat := c.custom_minimum_size
	holder.custom_minimum_size = Vector2(nat.x * 0.6, nat.y + z(6))
	holder.resized.connect(func():
		var k := clampf(holder.size.x / maxf(1.0, nat.x), 0.6, 1.0)
		c.scale = Vector2(k, k)
		sh.scale = Vector2(k, k)
		var hy := (nat.y + z(6)) * k
		if absf(holder.custom_minimum_size.y - hy) > 0.5:
			holder.custom_minimum_size.y = hy)
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
	if name_ != "garage" or cur != "garage":
		# coming into the garage (not rebuilding it after a change): the normal view, the list freshly sorted
		_liv_order = {"key": "", "ids": []}
		_gbig = false
		_gzoom = 1.0
		_gpitch = 0.0
	# rebuilding the screen you're on (a tab, a category, On/Off): the border stays on what you pressed. It's your
	# cursor, so it only moves when you move it
	if name_ == cur and _focus_after == "":
		var fo := get_viewport().gui_get_focus_owner()
		if fo != null and is_ancestor_of(fo):
			_focus_after = _ctl_key(fo)
	cur = name_
	bg.set_blur(name_ == "garage")
	sel_focus = null
	default_focus = null
	var restoring := name_ == "garage" and not _g_keep.is_empty()
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
	# a screen taller than the window scrolls: wheel, right stick, and the controller's focus pulls it along
	var wrap := scroll_wrap(s)
	screens[name_] = wrap
	add_child(wrap)
	visible = true
	var fa := _focus_after
	_focus_after = ""
	if fa != "" and not (restoring and fa.begins_with("g:")):
		_focus_key.call_deferred(fa)
	elif _pad_mode and not restoring:
		_pad_focus.call_deferred()


## a control's key, to find its twin after a rebuild: a card's gkey, or a segmented button's group and option
static func _ctl_key(c: Control) -> String:
	if c.has_meta("gkey"):
		return "g:" + String(c.get_meta("gkey"))
	if c.has_meta("seg"):
		return "s:" + String(c.get_meta("seg"))
	return ""


func _focus_key(k: String) -> void:
	var scr: Node = screens.get(cur)
	if scr != null:
		for c in scr.find_children("*", "", true, false):
			if c is Control and (c as Control).focus_mode != Control.FOCUS_NONE and _ctl_key(c as Control) == k and (c as Control).is_visible_in_tree():
				(c as Control).grab_focus()
				return
	if _pad_mode:
		_pad_focus()


## the menu is showing again (a track loaded behind it): with the controller in use, the border goes back on
func pad_refocus() -> void:
	if _pad_mode:
		_pad_focus.call_deferred()


func _pad_focus() -> void:
	var t := _focus_target()
	if t != null and is_instance_valid(t) and t.is_inside_tree():
		t.grab_focus()


## `content` in a scroll area filling its parent: when it fits it fills the area exactly as before; when it
## is taller (a small window, a long list) the mouse wheel and the right stick scroll it, and moving the
## highlight with the d-pad or the left stick scrolls the highlighted button into view
static func scroll_wrap(content: Control) -> ScrollContainer:
	var sc := ScrollContainer.new()
	sc.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	sc.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	sc.follow_focus = true
	content.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	content.size_flags_vertical = Control.SIZE_EXPAND_FILL
	sc.add_child(content)
	return sc


static var _stick_acc := 0.0

## the right stick scrolls the list or page under the highlight (or the biggest one showing), as on the web
static func stick_scroll(root: Node, dt: float) -> void:
	var ry := 0.0
	for p in Input.get_connected_joypads():
		var a := Input.get_joy_axis(p, JOY_AXIS_RIGHT_Y)
		if absf(a) > absf(ry):
			ry = a
	if absf(ry) < 0.25 or root == null or not is_instance_valid(root):
		_stick_acc = 0.0
		return
	var sc := _scroll_target(root)
	if sc == null:
		return
	_stick_acc += signf(ry) * (absf(ry) - 0.25) / 0.75 * dt * 1500.0
	var step := int(_stick_acc)
	if step != 0:
		sc.scroll_vertical += step
		_stick_acc -= step


static var _axis_dir := {}

## an up or down that is a new push: the d-pad, a key, or the left stick crossing into up or down. A stick held over
## sends a stream of motion events that all read as "down"; only the first moves the highlight, and the rest mustn't
## each scroll the page (that made the stick move the highlight and slide the page at the same time)
static func fresh_vdir(ev: InputEvent) -> int:
	var vdir := 1 if ev.is_action_pressed("ui_down") else (-1 if ev.is_action_pressed("ui_up") else 0)
	if ev is InputEventJoypadMotion:
		var jm := ev as InputEventJoypadMotion
		var key := "%d:%d" % [jm.device, jm.axis]
		var dz := InputMap.action_get_deadzone("ui_down") if InputMap.has_action("ui_down") else 0.5
		var d := (1 if jm.axis_value > 0.0 else -1) if absf(jm.axis_value) >= dz else 0
		var was: int = _axis_dir.get(key, 0)
		_axis_dir[key] = d
		if d == 0 or d == was:
			return 0
	return vdir


## a stick crossing into a direction on its axis: -1 or 1 once per push, 0 otherwise (shares fresh_vdir's memory)
static func fresh_axis(jm: InputEventJoypadMotion) -> int:
	var key := "%d:%d" % [jm.device, jm.axis]
	var d := (1 if jm.axis_value > 0.0 else -1) if absf(jm.axis_value) >= 0.5 else 0
	var was: int = _axis_dir.get(key, 0)
	_axis_dir[key] = d
	return d if d != was else 0


## after an up/down press: if the highlight didn't move (the end of a list, a page of text), scroll the page under it
## (or the biggest one showing) a step. While the highlight moves, its scroll area keeps it in view (follow_focus), so
## the page slides along with it as it reaches the bottom or the top
static func nav_scroll(root: Node, before: Control, dir: int) -> void:
	if root == null or not is_instance_valid(root) or not (root is Control) or not (root as Control).is_inside_tree():
		return
	var now := (root as Control).get_viewport().gui_get_focus_owner()
	if now != before:
		return
	var sc := _scroll_target(root)
	if sc == null:
		return
	sc.scroll_vertical += int(dir * maxf(80.0, sc.size.y * 0.4))


static func _can_scroll(sc: ScrollContainer) -> bool:
	var bar := sc.get_v_scroll_bar()
	return sc.is_visible_in_tree() and sc.vertical_scroll_mode != ScrollContainer.SCROLL_MODE_DISABLED and bar.max_value - bar.page > 1.0


static func _scroll_target(root: Node) -> ScrollContainer:
	var f: Control = (root as Control).get_viewport().gui_get_focus_owner() if root is Control else null
	if f != null and root.is_ancestor_of(f):
		var n: Node = f.get_parent()
		while n != null and n != root.get_parent():
			if n is ScrollContainer and _can_scroll(n as ScrollContainer):
				return n as ScrollContainer
			n = n.get_parent()
	var best: ScrollContainer = null
	var best_a := 0.0
	var stack: Array = [root]
	while not stack.is_empty():
		var n: Node = stack.pop_back()
		if n is ScrollContainer and _can_scroll(n as ScrollContainer):
			var a := (n as Control).size.x * (n as Control).size.y
			if a > best_a:
				best_a = a
				best = n
		stack.append_array(n.get_children())
	return best


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
	brand.add_child(logo("CRUST RUSH", 82.0, true))
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
	# which build this is, small in the corner, so an old copy is easy to spot
	var bi := build_info()
	if bi != "":
		var stamp := label(bi, f_med, 10.0, Color(1, 0.957, 0.863, 0.35))
		stamp.set_anchors_and_offsets_preset(Control.PRESET_BOTTOM_RIGHT)
		stamp.grow_horizontal = Control.GROW_DIRECTION_BEGIN
		stamp.grow_vertical = Control.GROW_DIRECTION_BEGIN
		stamp.offset_right = -z(4)
		stamp.offset_bottom = -z(2)
		stamp.mouse_filter = Control.MOUSE_FILTER_IGNORE
		var layer := Control.new()
		layer.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
		layer.mouse_filter = Control.MOUSE_FILTER_IGNORE
		layer.add_child(stamp)
		root.add_child(layer)
		# a newer build on the download page: say so here (an old copy still running, or a zip unpacked while the
		# game was open so Windows kept the old CrustRush.exe, otherwise looks like the game going back a version)
		var up := button("A newer version is out  ·  Download page", "ghost", 13.0, Vector4(12, 6, 12, 6))
		up.set_anchors_and_offsets_preset(Control.PRESET_BOTTOM_RIGHT)
		up.grow_horizontal = Control.GROW_DIRECTION_BEGIN
		up.grow_vertical = Control.GROW_DIRECTION_BEGIN
		up.offset_right = -z(6)
		up.offset_bottom = -z(18)
		up.focus_mode = Control.FOCUS_NONE
		up.pressed.connect(func(): OS.shell_open(PC_PAGE))
		up.visible = _behind()
		layer.add_child(up)
		_upd_btn = up
		_check_update()
	return root


const PC_PAGE := "https://samgoldsteinm.github.io/crust-rush/pc.html"
const PC_BUILD_URL := "https://github.com/samgoldsteinm/crust-rush/releases/download/pc/pc-build.json"
static var _latest := ""          # the build on the download page, once known
var _upd_req: HTTPRequest = null
var _upd_btn: Button = null


static func _own_build() -> String:
	var t := FileAccess.get_file_as_string("res://assets/build.json")
	var d = JSON.parse_string(t) if t != "" else null
	return String((d as Dictionary).get("build", "")) if d is Dictionary else ""


static func _behind() -> bool:
	var me := _own_build()
	return me != "" and _latest != "" and _latest != me


## once a session: which build the download page has (a small file the PC build publishes with the zip)
func _check_update() -> void:
	if _latest != "" or _upd_req != null or _own_build() == "":
		return
	_upd_req = HTTPRequest.new()
	_upd_req.timeout = 8.0
	add_child(_upd_req)
	# a computer that reaches the web through a proxy says so in HTTPS_PROXY ("http://host:port")
	var px := OS.get_environment("HTTPS_PROXY")
	if px.begins_with("http://") and px.count(":") == 2:
		var hp := px.trim_prefix("http://").trim_suffix("/").split(":")
		if hp[0].find("@") < 0:
			_upd_req.set_https_proxy(hp[0], int(hp[1]))
	_upd_req.request_completed.connect(func(res: int, code_: int, _h: PackedStringArray, body: PackedByteArray):
		if res == HTTPRequest.RESULT_SUCCESS and code_ == 200:
			var d = JSON.parse_string(body.get_string_from_utf8())
			if d is Dictionary:
				_latest = String((d as Dictionary).get("build", ""))
		_upd_req.queue_free()
		_upd_req = null
		if _upd_btn != null and is_instance_valid(_upd_btn):
			_upd_btn.visible = _behind())
	if _upd_req.request(PC_BUILD_URL) != OK:
		_upd_req.queue_free()
		_upd_req = null


## "PC build 1a2b3c4d · 2026-11-11" from assets/build.json (written by the PC build), or "" in the editor
static func build_info() -> String:
	var t := FileAccess.get_file_as_string("res://assets/build.json")
	var d = JSON.parse_string(t) if t != "" else null
	if not (d is Dictionary):
		return ""
	return "PC build %s · %s" % [String(d.get("build", "?")), String(d.get("date", ""))]


func _driver() -> Control:
	var root := _screen_root()
	var v := vbox(8)
	root.add_child(v)
	var three := KartBuilder.ready()
	var nx_t := "BUILD KART  ›" if three else ("READY  ›" if net == "guest" else "CHOOSE TRACK  ›")
	var nx_f := func():
		if three:
			open("garage")
		elif net == "guest":
			net_ready.emit()
		else:
			open("track")
	v.add_child(_step_head("‹ Room" if net != "" else "‹ Back", "home", "Step 1 of 3" if three else "Step 1 of 2", "Choose your driver", nx_t, nx_f))
	if net != "":
		var hb0: Control = v.get_child(v.get_child_count() - 1)
		var back0 := hb0.get_child(0) as Button
		for cn in back0.pressed.get_connections():
			back0.pressed.disconnect(cn["callable"])
		back0.pressed.connect(func(): net_room.emit())
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
		# the colour dot sits in the box's left padding, level with the first line (the box lays its children over
		# the text area, so the dot is drawn back out to the left of it)
		var dot := _Dot.new()
		dot.col = Color(String(info.get("ability_col", "#ff5a2a")))
		dot.at = Vector2(-z(14), z(9))
		dot.mouse_filter = Control.MOUSE_FILTER_IGNORE
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
		grid.add_child(card)
		if i == ri:
			sel_focus = card
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
			# one smooth darkening over the lower part, following the rounded bottom corners (strips laid edge to
			# edge, never overlapping: overlapping see-through strips showed as lines)
			var n := 24
			var rr := (Vector4.ONE * radius if corners.x < 0.0 else corners)
			var fp := PackedVector2Array()
			var cols := PackedColorArray()
			for i in n + 1:
				var f := float(i) / n
				var y := size.y * (0.6 + 0.4 * f)
				var dl := 0.0
				var dr := 0.0
				var yb := size.y - y
				if yb < rr.w:
					dl = rr.w - sqrt(maxf(0.0, rr.w * rr.w - (rr.w - yb) * (rr.w - yb)))
				if yb < rr.z:
					dr = rr.z - sqrt(maxf(0.0, rr.z * rr.z - (rr.z - yb) * (rr.z - yb)))
				fp.append(Vector2(dl, y))
				fp.append(Vector2(size.x - dr, y))
				var a := 0.78 * f * f * (3.0 - 2.0 * f)
				cols.append(Color(0.06, 0.03, 0.02, a))
				cols.append(Color(0.06, 0.03, 0.02, a))
			var idx := PackedInt32Array()
			for i in n:
				idx.append_array([i * 2, i * 2 + 1, i * 2 + 2, i * 2 + 1, i * 2 + 3, i * 2 + 2])
			RenderingServer.canvas_item_add_triangle_array(get_canvas_item(), idx, fp, cols)
		if label != "" and font != null:
			draw_string(font, Vector2(font_px * 0.5, size.y - font_px * 0.55) + Vector2(0, 1), label, HORIZONTAL_ALIGNMENT_LEFT, size.x - font_px, int(font_px), Color(0, 0, 0, 0.8))
			draw_string(font, Vector2(font_px * 0.5, size.y - font_px * 0.55), label, HORIZONTAL_ALIGNMENT_LEFT, size.x - font_px, int(font_px), Color("#fff4dc"))


class _Dot extends Control:
	var col := Color.RED
	var at := Vector2.ZERO
	func _draw() -> void:
		draw_circle(at, 9.0 * 1.18, Color(col.r, col.g, col.b, 0.25), true, -1.0, true)
		draw_circle(at, 5.0 * 1.18, col, true, -1.0, true)


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
	var fr := box([Color(0, 0, 0, 0)], 180.0, r, CHEESE, 3.0)
	fr.grow = 4.0
	b.add_theme_stylebox_override("focus", fr)


## a list inside a scroll area, with room round it for the yellow border (it's drawn just outside a card, and the
## scroll area cut it off on the first column and the top row)
func _ring_room(c: Control) -> MarginContainer:
	var m := MarginContainer.new()
	for k in ["margin_left", "margin_top", "margin_right", "margin_bottom"]:
		m.add_theme_constant_override(k, zi(6))
	m.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	m.add_child(c)
	return m


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
	if net == "host":
		gp = false
	v.add_child(_step_head("‹ Kart" if three else "‹ Driver", "garage" if three else "driver", small, "Cup" if gp else "Track", "SET TRACK  ›" if net == "host" else ("START GRAND PRIX" if gp else "START RACE"), func():
		if net == "host":
			net_track.emit(map_id)
		else:
			_go()))
	var body := hbox(16)
	body.size_flags_vertical = Control.SIZE_EXPAND_FILL
	v.add_child(body)
	var detail := panel(glass(18.0, Vector4(14, 14, 14, 14)))
	detail.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	var dv := vbox(8)
	detail.add_child(dv)
	var grid := GridContainer.new()
	grid.columns = 3 if gp else 4   # five cups: three across, two down
	grid.add_theme_constant_override("h_separation", zi(12))
	grid.add_theme_constant_override("v_separation", zi(12))
	grid.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	grid.size_flags_vertical = Control.SIZE_EXPAND_FILL
	var left: Control = grid
	if not gp:
		var sc := ScrollContainer.new()
		sc.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
		sc.add_child(_ring_room(grid))
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
			if ci == cup:
				sel_focus = card
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
			if id == map_id:
				sel_focus = card2
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


## a vehicle's own stats as values (out of 12; 6 is the middle), for the body cards
func _value_chips(bars: Array) -> HFlowContainer:
	var f := HFlowContainer.new()
	f.add_theme_constant_override("h_separation", zi(4))
	f.add_theme_constant_override("v_separation", zi(4))
	f.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var short: Array = KartBuilder.info.get("statShort", ["SPD", "ACC", "HND", "WGT", "OFF"])
	for i in bars.size():
		var v := int(bars[i])
		var pc := panel(box([Color(1, 0.957, 0.863, 0.1)], 180.0, 5.0, Color(0, 0, 0, 0), 0.0, Vector4(5, 1, 5, 1)))
		pc.mouse_filter = Control.MOUSE_FILTER_IGNORE
		pc.add_child(label(String(short[i]) + " " + str(v), f_bold, 9.5, CREAM))
		f.add_child(pc)
	return f


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


func _part_card(name_: String, st: Array, on: bool, dense: bool, values := false) -> Button:
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
	v.add_child(_value_chips(st) if values else _chips(st))
	# the card grows to fit when its chips wrap onto a second row (they ran into the card below)
	var base_h := z(48 if dense else 74)
	v.minimum_size_changed.connect(func():
		var need := maxf(base_h, v.get_combined_minimum_size().y + z(14))
		if absf(b.custom_minimum_size.y - need) > 0.5:
			b.custom_minimum_size.y = need)
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
	var tabs := [["kart", "Karts"], ["car", "Cars"], ["bike", "Bikes"], ["glider", "Glider"], ["theme", "Theme"]]
	if g_tab == "colour":
		g_tab = "theme"
	tabs.assign(_garage_tabs().map(func(k): return [k, TAB_NAMES[k]]))
	if is_bike and g_tab == "wheel":
		g_tab = "bike"
	h.add_child(seg("gtab", tabs, g_tab, func(k):
		g_tab = k
		open("garage"), 15.0, 8.0, 12.0))
	var sp2 := Control.new()
	sp2.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	h.add_child(sp2)
	# in a friends' room the guest is done here (web: the garage's Ready); the host goes on to pick the track
	var nxt := button("READY  ›" if net == "guest" else "CHOOSE TRACK  ›", "cta", 19.0, Vector4(20, 10, 20, 10))
	nxt.pressed.connect(func():
		if net == "guest":
			net_ready.emit()
		else:
			open("track"))
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
	# the 3D preview is drawn at the screen's own pixels (a SubViewportContainer draws at the menu's 1280-wide
	# layout size, which a 1440p screen then doubled: a soft, blocky car)
	var svc := TextureRect.new()
	svc.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	svc.stretch_mode = TextureRect.STRETCH_SCALE
	svc.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
	svc.mouse_filter = Control.MOUSE_FILTER_STOP
	svc.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	view.add_child(svc)
	_gview = SubViewport.new()
	_gview.own_world_3d = true
	_gview.transparent_bg = true
	_gview.msaa_3d = Viewport.MSAA_8X
	_gview.screen_space_aa = Viewport.SCREEN_SPACE_AA_FXAA
	_gview.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	_gview.size = Vector2i(16, 16)
	svc.add_child(_gview)
	svc.texture = _gview.get_texture()
	svc.resized.connect(func():
		var px := _px_scale()
		_gview.size = Vector2i(maxi(16, int(svc.size.x * px)), maxi(16, int(svc.size.y * px))))
	_garage_scene()
	# as the web's garage: drag to turn it (and, in the inspect view, tilt); a click without a drag opens the
	# full-screen inspect view; the wheel zooms (rolling it forward opens the inspect view too)
	svc.gui_input.connect(func(ev):
		if ev is InputEventMouseButton:
			var mb := ev as InputEventMouseButton
			if mb.button_index == MOUSE_BUTTON_LEFT:
				_gdrag = mb.pressed
				if mb.pressed:
					_gtap = mb.position
					_gtap_t = Time.get_ticks_msec()
				elif _gtap.x >= 0.0 and not _gbig and Time.get_ticks_msec() - _gtap_t < 350:
					_set_big(true)
				if not mb.pressed:
					_gtap = Vector2(-1, -1)
			elif mb.pressed and (mb.button_index == MOUSE_BUTTON_WHEEL_UP or mb.button_index == MOUSE_BUTTON_WHEEL_DOWN):
				var up := mb.button_index == MOUSE_BUTTON_WHEEL_UP
				_gzoom = clampf(_gzoom * exp((-0.12 if up else 0.12) * maxf(1.0, mb.factor)), 0.32, 1.5)
				if up and not _gbig:
					_set_big(true)
		elif ev is InputEventMagnifyGesture:
			_gzoom = clampf(_gzoom / (ev as InputEventMagnifyGesture).factor, 0.32, 1.5)
		elif ev is InputEventMouseMotion and _gdrag:
			var mm := ev as InputEventMouseMotion
			_grot += mm.relative.x * 0.011
			if _gbig:
				_gpitch = clampf(_gpitch + mm.relative.y * 0.006, -0.12, 1.1)
			if _gtap.x >= 0.0 and mm.position.distance_to(_gtap) > z(7):
				_gtap = Vector2(-1, -1))
	# the inspect button in the top-right corner (web .g-zoom), in a free layer so the panel doesn't stretch it
	var zl := Control.new()
	zl.mouse_filter = Control.MOUSE_FILTER_IGNORE
	zl.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	view.add_child(zl)
	var insp := button("", "icon", 15.0, Vector4(0, 0, 0, 0))
	var ist := box([Color(20.0 / 255, 10.0 / 255, 6.0 / 255, 0.55)], 180.0, 12.0, Color(1, 0.957, 0.863, 0.2), 1.0, Vector4(0, 0, 0, 0))
	var ish := box([Color(40.0 / 255, 22.0 / 255, 12.0 / 255, 0.7)], 180.0, 12.0, Color(1, 0.957, 0.863, 0.35), 1.0, Vector4(0, 0, 0, 0))
	for s3 in ["normal", "pressed"]:
		insp.add_theme_stylebox_override(s3, ist)
	for s3 in ["hover", "hover_pressed"]:
		insp.add_theme_stylebox_override(s3, ish)
	insp.set_anchors_and_offsets_preset(Control.PRESET_TOP_RIGHT)
	insp.offset_left = -z(10) - z(38)
	insp.offset_right = -z(10)
	insp.offset_top = z(10)
	insp.offset_bottom = z(10) + z(38)
	insp.tooltip_text = "Inspect: full screen (mouse wheel or left stick to zoom, triggers to spin)"
	var corners := _Corners.new()
	corners.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	corners.mouse_filter = Control.MOUSE_FILTER_IGNORE
	insp.add_child(corners)
	insp.pressed.connect(func(): _set_big(not _gbig))
	zl.add_child(insp)
	_g_insp = insp
	# the inspect view's hint (web .g-hint)
	var hpill := PanelContainer.new()
	hpill.add_theme_stylebox_override("panel", box([Color(20.0 / 255, 10.0 / 255, 6.0 / 255, 0.5)], 180.0, 999.0, Color(0, 0, 0, 0), 0.0, Vector4(10, 5, 10, 5)))
	hpill.mouse_filter = Control.MOUSE_FILTER_IGNORE
	hpill.add_child(label("Drag to turn and tilt  ·  mouse wheel or left stick to zoom  ·  triggers spin  ·  B or Esc closes", f_semi, 12.0, Color(1, 0.957, 0.863, 0.75)))
	var hrow := HBoxContainer.new()
	hrow.alignment = BoxContainer.ALIGNMENT_CENTER
	hrow.mouse_filter = Control.MOUSE_FILTER_IGNORE
	hrow.set_anchors_and_offsets_preset(Control.PRESET_BOTTOM_WIDE)
	hrow.offset_top = -z(14) - z(28)
	hrow.offset_bottom = -z(14)
	hrow.add_child(hpill)
	zl.add_child(hrow)
	_g_hint = hrow
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
	var stb := _stats_box()
	ov.add_child(stb)
	# the parts
	var side := vbox(8)
	side.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	body.add_child(side)
	_g_hide = [h, side, stb]
	_g_next = nxt
	var desc := ""
	var sc := ScrollContainer.new()
	sc.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	sc.size_flags_vertical = Control.SIZE_EXPAND_FILL
	sc.follow_focus = true
	_g_list = sc
	var above: Control = null      # the livery categories, between the description and the list
	var grid := GridContainer.new()
	grid.add_theme_constant_override("h_separation", zi(8))
	grid.add_theme_constant_override("v_separation", zi(8))
	grid.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	sc.add_child(_ring_room(grid))
	match g_tab:
		"kart", "car", "bike":
			var dense := g_tab == "car"
			grid.columns = 4 if dense else 3
			for i in (I["bodies"] as Array).size():
				var bd: Dictionary = I["bodies"][i]
				var cat := "bike" if bool(bd.get("bike", false)) else ("car" if bool(bd.get("car", false)) else "kart")
				if cat != g_tab:
					continue
				var c := _part_card(String(bd["name"]), KartBuilder.base_bars({"b": i, "w": 0, "g": 0}), i == int(build["b"]), dense, true)
				c.set_meta("gkey", "b:%d" % i)
				c.set_meta("part", ["b", i])
				_preview_on(c, "b", i)
				if i == int(build["b"]):
					sel_focus = c
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
				c2.set_meta("gkey", "%s:%d" % [key, i])
				c2.set_meta("part", [key, i])
				_preview_on(c2, key, i)
				if i == int(build[key]):
					sel_focus = c2
				var pi := i
				c2.pressed.connect(func():
					build[key] = pi
					_build_changed())
				grid.add_child(c2)
			var cp: Dictionary = list[int(build[key])]
			desc = "[b][color=#fff4dc]%s.[/color][/b] %s" % [cp["name"], cp["desc"]]
		"theme":
			grid.columns = 3
			var bid := String(I["bodies"][int(build["b"])]["id"])
			var cur_t := String(build.get("t", ""))
			var all_l := KartBuilder.list_for(bid, cur_t)
			var fl: Array = favs.get(bid, [])
			# the categories that have something for this body (Favourites and All always)
			var chips := HFlowContainer.new()
			chips.add_theme_constant_override("h_separation", zi(7))
			chips.add_theme_constant_override("v_separation", zi(7))
			for cq in LIV_CATS:
				var ck := String(cq[0])
				var n := 0
				for l in all_l:
					if _in_cat(l, ck, fl):
						n += 1
				if n == 0 and ck != "all" and ck != "fav":
					continue
				var chip := button(String(cq[1]), "seg_on" if ck == liv_cat else "ghost", 13.5, Vector4(15, 7, 15, 7))
				chip.set_meta("gkey", "cat:" + ck)
				chip.pressed.connect(func():
					liv_cat = ck
					_g_keep = {"tab": "theme", "cat": ck, "scroll": 0, "focus": "cat:" + ck}
					open("garage"))
				chips.add_child(chip)
			above = chips
			var shown: Array = []
			for l in all_l:
				if _in_cat(l, liv_cat, fl):
					shown.append(l)
			if liv_cat == "all":
				var okey := bid + "|all"
				if String(_liv_order["key"]) == okey:
					# the same visit: keep the order the list already has, so a card doesn't jump away when it's favourited
					var pos := {}
					var ids: Array = _liv_order["ids"]
					for i in ids.size():
						pos[String(ids[i])] = i
					shown.sort_custom(func(x, y): return int(pos.get(String(x["id"]), 100000)) < int(pos.get(String(y["id"]), 100000)))
				else:
					# favourites first, as on the web
					var fv: Array = []
					var rest: Array = []
					for l in shown:
						(fv if fl.has(String(l["id"])) else rest).append(l)
					shown = fv + rest
				_liv_order = {"key": okey, "ids": shown.map(func(l): return String(l["id"]))}
				var none := _livery_card({"id": "", "name": "No theme", "A": "#5a4a40", "B": "#5a4a40", "C": "#5a4a40"}, cur_t == "", false)
				if cur_t == "":
					sel_focus = none
				none.pressed.connect(func():
					build["t"] = ""
					_build_changed())
				grid.add_child(none)
			if _thumbs != null:
				_thumbs.clear_queue()
			for l in shown:
				var lid := String(l["id"])
				var locked := Ach.liv_locked(l)
				var lc := _livery_card(l, lid == cur_t, fl.has(lid))
				if lid == cur_t:
					sel_focus = lc
				if locked:
					# a reward livery not won yet: shown with a lock; a tap says how to win it
					lc.modulate = Color(1, 1, 1, 0.55)
					var lk := _Lock.new()
					lk.custom_minimum_size = Vector2(z(16), z(16))
					lk.set_anchors_and_offsets_preset(Control.PRESET_TOP_LEFT)
					lk.offset_left = z(9)
					lk.offset_top = z(9)
					lk.offset_right = z(25)
					lk.offset_bottom = z(25)
					lk.mouse_filter = Control.MOUSE_FILTER_IGNORE
					lc.add_child(lk)
					var an := ""
					for a2 in Ach.LIST:
						if String(a2[0]) == String(l["lock"]):
							an = "[b][color=#fff4dc]%s[/color][/b]: %s" % [String(a2[1]), String(a2[2])]
					var hint := "[b][color=#fff4dc]%s[/color][/b] unlocks with %s" % [String(l["name"]), an if an != "" else "an achievement"]
					lc.pressed.connect(func():
						g_hint = hint
						_g_keep = _place()
						open("garage"))
				else:
					lc.pressed.connect(func():
						build["t"] = lid
						_build_changed())
				grid.add_child(lc)
			if shown.is_empty():
				var bname := String(I["bodies"][int(build["b"])]["name"])
				var em := para(("No favourites for the %s yet. Click the heart on any livery, or press X on a controller, to keep it here." % bname) if liv_cat == "fav" else "Nothing here for this body.", 13.0, MUTED, 420.0)
				grid.add_child(em)
			var lv := KartBuilder.livery(cur_t)
			var bn := String(I["bodies"][int(build["b"])]["name"])
			if not lv.is_empty():
				desc = "[b][color=#fff4dc]%s.[/color][/b] %s Pick No theme to go back to plain paint. The heart (or X on a controller) keeps it in Favourites." % [String(lv["name"]), ("A signature theme made for the %s." % bn) if lv.get("only") != null else "A multi-colour livery."]
			else:
				desc = "Multi-colour liveries. Themes marked ★ are made for the %s. The heart (or X on a controller) keeps one in Favourites." % bn
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
	if above != null:
		side.add_child(above)
	side.add_child(sc)
	_apply_big()
	if not _g_keep.is_empty() and String(_g_keep.get("tab", "")) == g_tab:
		_restore_place.call_deferred(_g_keep)
	_g_keep = {}
	return root


## does livery `l` belong in category `c` (web: fav, sig = made for this body, or its own category)
func _in_cat(l: Dictionary, c: String, fl: Array) -> bool:
	match c:
		"all":
			return true
		"fav":
			return fl.has(String(l["id"]))
		"sig":
			return l.get("only") != null
	return String(l.get("cat", "")) == c


## where the list is and which card is highlighted, to come back to after the garage rebuilds
func _place() -> Dictionary:
	var fo := get_viewport().gui_get_focus_owner()
	var ok := _g_list != null and is_instance_valid(_g_list)
	var o := {"tab": g_tab, "cat": liv_cat, "scroll": _g_list.scroll_vertical if ok else 0,
		"focus": String(fo.get_meta("gkey")) if fo != null and fo.has_meta("gkey") else ""}
	if ok and fo != null and _g_list.is_ancestor_of(fo):
		# where the highlighted card sits in the list's window: it goes back to the same spot
		o["off"] = fo.get_global_rect().position.y - _g_list.get_global_rect().position.y
	return o


func _restore_place(k: Dictionary) -> void:
	# two frames: the new list has its size, so the scroll can go back to where it was
	await get_tree().process_frame
	await get_tree().process_frame
	if _g_list == null or not is_instance_valid(_g_list):
		return
	var same := String(k.get("cat", "")) == liv_cat
	var want := int(k.get("scroll", 0))
	if same:
		_g_list.scroll_vertical = want
	var key := String(k.get("focus", ""))
	var scr: Node = screens.get("garage")
	var target: Control = null
	if key != "" and scr != null:
		for c in scr.find_children("*", "Button", true, false):
			if c.has_meta("gkey") and String(c.get_meta("gkey")) == key and (c as Control).is_visible_in_tree():
				target = c as Control
				break
	if target == null:
		return
	# the list would scroll itself to the highlight on its own: hold that off, put the highlighted card back at
	# the same spot in the window, and only scroll to it if it isn't on screen there (a favourite moved to the top)
	_g_list.follow_focus = false
	target.grab_focus()
	await get_tree().process_frame
	if not is_instance_valid(_g_list) or not is_instance_valid(target):
		return
	if same:
		var lr := _g_list.get_global_rect()
		if k.has("off") and _g_list.is_ancestor_of(target):
			var cy := target.get_global_rect().position.y - lr.position.y + float(_g_list.scroll_vertical)
			_g_list.scroll_vertical = int(round(cy - float(k["off"])))
		else:
			_g_list.scroll_vertical = want
		var cr := target.get_global_rect()
		if cr.position.y < lr.position.y - 1.0 or cr.end.y > lr.end.y + 1.0:
			_g_list.ensure_control_visible(target)
	await get_tree().process_frame
	if is_instance_valid(_g_list):
		_g_list.follow_focus = true


## a livery in or out of this body's favourites (web toggleFav)
func _toggle_fav(id: String) -> void:
	if id == "":
		return
	var bid := String(KartBuilder.info["bodies"][int(build["b"])]["id"])
	var arr: Array = (favs.get(bid, []) as Array).duplicate()
	if arr.has(id):
		arr.erase(id)
	else:
		arr.append(id)
	favs[bid] = arr
	setting_changed.emit("favs", favs.duplicate(true))
	_g_keep = _place()
	open("garage")


## the inspect view: the preview fills the screen (the header, the parts and the stats step aside), it stops
## turning by itself, the camera centres on the car and dragging tilts as well as turns (web setBig)
func _set_big(v: bool) -> void:
	if v == _gbig:
		return
	_gbig = v
	if not v:
		_gzoom = 1.0
		_gpitch = 0.0
	_apply_big()


func _apply_big() -> void:
	for n in _g_hide:
		if n != null and is_instance_valid(n):
			(n as Control).visible = not _gbig
	if _g_hint != null and is_instance_valid(_g_hint):
		_g_hint.visible = _gbig
	if _g_insp != null and is_instance_valid(_g_insp):
		_g_insp.tooltip_text = "Close the inspect view (B or Esc)" if _gbig else "Inspect: full screen (mouse wheel or left stick to zoom, triggers to spin)"
		var c := _g_insp.get_child(0)
		if c is _Corners:
			(c as _Corners).inward = _gbig
			(c as Control).queue_redraw()
		default_focus = _g_insp if _gbig else (_g_next as Control)
		if _gbig:
			_g_insp.grab_focus.call_deferred()
		elif _g_insp.has_focus() and _g_next != null and is_instance_valid(_g_next):
			(_g_next as Control).grab_focus.call_deferred()
	_gasp = 0.0


## the inspect button's four corner marks: pointing out (open) or in (close), as the web's icon
class _Corners extends Control:
	var inward := false
	func _draw() -> void:
		var s := minf(size.x, size.y) * 20.0 / 38.0
		var o := (size - Vector2(s, s)) * 0.5
		var k := s / 24.0
		var w := maxf(1.5, 2.4 * k)
		var col := Color("#fff4dc")
		# web paths: out M4 9V4h5 M20 9V4h-5 M4 15v5h5 M20 15v5h-5; in M9 4v5H4 M15 4v5h5 M9 20v-5H4 M15 20v-5h5
		var lines: Array = [[[4, 9], [4, 4], [9, 4]], [[20, 9], [20, 4], [15, 4]], [[4, 15], [4, 20], [9, 20]], [[20, 15], [20, 20], [15, 20]]]
		if inward:
			lines = [[[9, 4], [9, 9], [4, 9]], [[15, 4], [15, 9], [20, 9]], [[9, 20], [9, 15], [4, 15]], [[15, 20], [15, 15], [20, 15]]]
		for l in lines:
			var pts := PackedVector2Array()
			for p in l:
				pts.append(o + Vector2(float(p[0]), float(p[1])) * k)
			draw_polyline(pts, col, w, true)
			for p2 in pts:
				draw_circle(p2, w * 0.5, col)


## a livery card: your kart drawn in it (scripts/liv_thumbs.gd; the web's three-colour swatch shows until the picture
## is ready, then stays as a thin strip under it), the name (★ = made for this body) and the favourite heart
func _livery_card(l: Dictionary, on: bool, fav: bool) -> Button:
	var b := Button.new()
	b.custom_minimum_size = Vector2(z(150), z(118))
	b.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	b.mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
	b.focus_mode = Control.FOCUS_ALL
	var lid := String(l["id"])
	b.set_meta("gkey", "t:" + lid)
	b.set_meta("liv", lid)
	_mark_card(b, on)
	var v := vbox(3)
	v.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	v.offset_left = z(5)
	v.offset_top = z(5)
	v.offset_right = -z(5)
	v.offset_bottom = -z(5)
	v.mouse_filter = Control.MOUSE_FILTER_IGNORE
	b.add_child(v)
	var pic := Control.new()
	pic.size_flags_vertical = Control.SIZE_EXPAND_FILL
	pic.mouse_filter = Control.MOUSE_FILTER_IGNORE
	pic.clip_contents = true
	v.add_child(pic)
	var bands := _Bands.new()
	bands.cols = [Color(String(l["A"])), Color(String(l["B"])), Color(String(l["C"]))]
	bands.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	bands.mouse_filter = Control.MOUSE_FILTER_IGNORE
	bands.modulate.a = 0.85
	pic.add_child(bands)
	var tr := TextureRect.new()
	tr.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	tr.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	tr.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
	tr.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	tr.mouse_filter = Control.MOUSE_FILTER_IGNORE
	pic.add_child(tr)
	if KartBuilder.ready():
		if _thumbs == null:
			_thumbs = LivThumbs.new()
			add_child(_thumbs)
		_thumbs.set_px(_px_scale())
		_thumbs.want(build, ri, lid, func(tex: Texture2D):
			if is_instance_valid(tr) and is_instance_valid(bands):
				tr.texture = tex
				# the swatch steps back to a strip of the three colours under the car
				bands.set_anchors_and_offsets_preset(Control.PRESET_BOTTOM_WIDE)
				bands.offset_top = -z(5)
				bands.offset_bottom = 0.0
				tr.modulate.a = 0.0
				tr.create_tween().tween_property(tr, "modulate:a", 1.0, 0.18))
	var row := hbox(4)
	row.mouse_filter = Control.MOUSE_FILTER_IGNORE
	v.add_child(row)
	var nl := label(("★ " if l.get("only") != null else "") + String(l["name"]), f_bold, 11.0, CHEESE if on else CREAM)
	nl.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	nl.clip_text = true
	nl.text_overrun_behavior = TextServer.OVERRUN_TRIM_ELLIPSIS
	row.add_child(nl)
	if lid != "":
		var hb := Button.new()
		hb.flat = true
		hb.focus_mode = Control.FOCUS_NONE
		hb.custom_minimum_size = Vector2(z(18), z(16))
		hb.mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
		hb.tooltip_text = ("Remove %s from favourites" if fav else "Add %s to favourites") % String(l["name"])
		var ht := _Heart.new()
		ht.on = fav
		ht.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
		ht.mouse_filter = Control.MOUSE_FILTER_IGNORE
		hb.add_child(ht)
		hb.pressed.connect(func(): _toggle_fav(lid))
		row.add_child(hb)
	return b


## the favourite heart (web .fav): filled cheese-yellow when it's a favourite, an outline when not
class _Heart extends Control:
	var on := false
	func _draw() -> void:
		var s := minf(size.x, size.y)
		var o := (size - Vector2(s, s)) * 0.5
		var k := s / 24.0
		# two lobes and a point (web path: M12 20.5 4.2 13 A4.9 4.9 0 0 1 12 6.6 A4.9 4.9 0 0 1 19.8 13 z)
		var pts := PackedVector2Array()
		pts.append(o + Vector2(12, 20.5) * k)
		for i in 15:
			var a := deg_to_rad(135.0 + 180.0 * float(i) / 14.0)
			pts.append(o + (Vector2(8.3, 10.0) + Vector2(cos(a), sin(a)) * 4.6) * k)
		for i in 15:
			var a := deg_to_rad(225.0 + 180.0 * float(i) / 14.0)
			pts.append(o + (Vector2(15.7, 10.0) + Vector2(cos(a), sin(a)) * 4.6) * k)
		var col := Color("#f7c948") if on else Color(1, 0.957, 0.863, 0.55)
		if on:
			draw_colored_polygon(pts, col)
		var closed := pts.duplicate()
		closed.append(pts[0])
		draw_polyline(closed, col, maxf(1.2, 1.6 * k), true)


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
	var p := panel(box([Color(0.06, 0.03, 0.02, 0.72)], 180.0, 12.0, Color(1, 0.957, 0.863, 0.12), 1.0, Vector4(12, 10, 12, 10)))
	p.size_flags_horizontal = Control.SIZE_SHRINK_BEGIN
	p.mouse_filter = Control.MOUSE_FILTER_PASS
	var v := vbox(5)
	p.add_child(v)
	var hh := hbox(10)
	var sl := label("STATS", f_bold, 10.0, MUTED)
	sl.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	sl.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	hh.add_child(sl)
	var sg := seg("stats", [["1", "On"], ["0", "Off"]], "1" if stats_on else "0", func(k):
		stats_on = k == "1"
		setting_changed.emit("stats", stats_on)
		open("garage"), 11.0, 3.0)
	sg.custom_minimum_size.x = z(104)
	sg.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	hh.add_child(sg)
	v.add_child(hh)
	var names: Array = KartBuilder.info.get("statNames", ["Speed", "Accel", "Handling", "Weight", "Off-road"])
	var rows := GridContainer.new()
	rows.columns = 3
	rows.add_theme_constant_override("h_separation", zi(8))
	rows.add_theme_constant_override("v_separation", zi(5))
	v.add_child(rows)
	_st_rows = []
	for i in 5:
		var n := label(String(names[i]).to_upper(), f_bold, 9.0, MUTED)
		n.custom_minimum_size.x = z(66)
		n.size_flags_vertical = Control.SIZE_SHRINK_CENTER
		rows.add_child(n)
		var dots := _Dots.new()
		dots.custom_minimum_size = Vector2(z(120), z(10))
		dots.size_flags_vertical = Control.SIZE_SHRINK_CENTER
		rows.add_child(dots)
		var d := label("0", f_bold, 12.0, CREAM)
		d.custom_minimum_size.x = z(24)
		d.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
		d.size_flags_vertical = Control.SIZE_SHRINK_CENTER
		rows.add_child(d)
		_st_rows.append([dots, d])
	p.modulate.a = 1.0 if stats_on else 0.55
	_stats_show({})
	return p


var _st_rows: Array = []


## the stats box for your build, and (with `prev` a build) what changing to it would do: the bars it adds in green,
## the ones it takes away in red, and the change in the column (web: the value against the middle bar)
func _stats_show(prev: Dictionary) -> void:
	if _st_rows.is_empty() or not KartBuilder.ready():
		return
	# the vehicle's own stats are its bars (orange); what the wheels and glider add shows in green, what they take
	# away in red, and the column gives that change (blank when they change nothing). A highlighted part shows
	# the build it would make.
	var b := prev if not prev.is_empty() else build
	var base := KartBuilder.base_bars(b)
	var tot := KartBuilder.stat_bars(b)
	for i in mini(5, _st_rows.size()):
		var r: Array = _st_rows[i]
		if not is_instance_valid(r[0]):
			return
		var dots := r[0] as _Dots
		dots.n = int(base[i])
		dots.p = int(tot[i])
		dots.queue_redraw()
		var dl := r[1] as Label
		var ch := int(tot[i]) - int(base[i])
		dl.text = (("+" if ch > 0 else "−") + str(absi(ch))) if ch != 0 else ""
		dl.add_theme_color_override("font_color", Color("#8ff08a") if ch > 0 else Color("#ff9a88"))


## a part card shows what it would do to the stats while it's highlighted or under the mouse
func _preview_on(c: Control, key: String, idx: int) -> void:
	var on := func():
		var b := build.duplicate()
		b[key] = idx
		_stats_show(b)
	var off := func():
		var f := get_viewport().gui_get_focus_owner() if is_inside_tree() else null
		if f != null and f.has_meta("part") and f != c:
			return
		_stats_show({})
	c.focus_entered.connect(on)
	c.mouse_entered.connect(on)
	c.focus_exited.connect(off)
	c.mouse_exited.connect(func():
		var f := get_viewport().gui_get_focus_owner() if is_inside_tree() else null
		if f != null and f.has_meta("part") and is_instance_valid(f):
			var pk: Array = f.get_meta("part")
			var b := build.duplicate()
			b[String(pk[0])] = int(pk[1])
			_stats_show(b)
		else:
			_stats_show({}))


class _Dots extends Control:
	## the web's .st-bar: 12 bars, the middle one ringed; with a preview, bars gained in green and lost in red
	var n := 6
	var p := 6
	func _draw() -> void:
		var step := size.x / 12.0
		var rr := minf(step * 0.36, size.y * 0.5)
		for i in 12:
			var c := Vector2(step * (i + 0.5), size.y / 2.0)
			var col := Color(1, 0.957, 0.863, 0.14)
			if i < mini(n, p):
				col = Color("#f7a72e")
			elif i < p:
				col = Color("#6fe06a")
			elif i < n:
				col = Color(1, 0.42, 0.33, 0.85)
			if i == 5:
				draw_circle(c, rr + maxf(1.0, rr * 0.35), Color(1, 0.957, 0.863, 0.45), false, maxf(1.0, rr * 0.25), true)
			draw_circle(c, rr, col, true, -1.0, true)


func _build_changed() -> void:
	setting_changed.emit("build", build.duplicate())
	_g_keep = _place()
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
	# a warm studio with soft-box lights, for clean reflections in the paint, glass and chrome
	var skm := ShaderMaterial.new()
	skm.shader = load("res://shaders/studio_sky.gdshader")
	sky.sky_material = skm
	sky.radiance_size = Sky.RADIANCE_SIZE_256
	e.sky = sky
	e.ambient_light_source = Environment.AMBIENT_SOURCE_SKY
	e.ambient_light_sky_contribution = 1.0
	e.ambient_light_energy = 0.55
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


## web frameGarageCam (no glider unfolded): fit the kart's bounding sphere in a 30 degree view, raised .22 rad; set off to
## one side (the stats panel) and looking a little low in the normal view, centred in the inspect view; zoom and tilt eased
func _frame_garage_cam(dt := 0.0) -> void:
	if _gcam == null or not is_instance_valid(_gcam):
		return
	var e := 1.0 if dt <= 0.0 else minf(1.0, dt * 10.0)
	_gzc += (_gzoom - _gzc) * e
	_gpc += (_gpitch - _gpc) * e
	var asp := 1.6
	if _gview != null and _gview.size.y > 0:
		asp = float(_gview.size.x) / float(_gview.size.y)
	var vh := deg_to_rad(15.0)
	var hh := atan(tan(vh) * asp)
	var d := _grad / sin(minf(vh, hh)) * (0.95 if _gbig else 0.84) * _gzc
	var el := 0.22 + _gpc
	var hz := cos(el) * d
	var sh := 0.0 if _gbig else _grad * 0.34 * minf(1.0, asp / 1.3)
	_gcam.near = maxf(0.5, minf(d - _grad * 1.6, d * 0.25))
	_gcam.far = maxf(200.0, d * 8.0)
	_gcam.look_at_from_position(Vector3(hz * 0.756 - sh * 0.654, _gcy + sin(el) * d, hz * 0.654 + sh * 0.756), Vector3(-sh * 0.654, _gcy - (0.0 if _gbig else _grad * 0.16), sh * 0.756), Vector3.UP)


## screen pixels for one unit of the menus' layout (2 on a 1440p screen)
func _px_scale() -> float:
	var vr := get_viewport().get_visible_rect().size
	var ws := Vector2(DisplayServer.window_get_size()) if DisplayServer.get_name() != "headless" else vr
	return clampf(ws.y / maxf(1.0, vr.y), 1.0, 4.0)


func _process(dt: float) -> void:
	if visible and not (cur == "garage" and modal == null and _gbig):
		stick_scroll(modal if modal != null else self, dt)
	if _gturn != null and is_instance_valid(_gturn) and cur == "garage":
		if not _gdrag and not _gbig:
			_grot += dt * 0.4
		# a controller: the triggers spin it (right one way, left the other; analog, so press harder to spin faster);
		# the bumpers go from tab to tab (in _input); in the inspect view the left stick's up and down zoom
		if modal == null:
			var sp := 0.0
			var zy := 0.0
			for j in Input.get_connected_joypads():
				var r := Input.get_joy_axis(j, JOY_AXIS_TRIGGER_RIGHT)
				var l := Input.get_joy_axis(j, JOY_AXIS_TRIGGER_LEFT)
				if absf(r - l) > absf(sp):
					sp = r - l
				var ay := Input.get_joy_axis(j, JOY_AXIS_LEFT_Y)
				if absf(ay) > absf(zy):
					zy = ay
			if absf(sp) > 0.05:
				_grot += sp * dt * 2.6
			if _gbig and absf(zy) > 0.18:
				var z2 := signf(zy) * (absf(zy) - 0.18) / 0.82
				_gzoom = clampf(_gzoom * exp(z2 * dt * 1.6), 0.32, 1.5)
		_gturn.rotation.y = _grot
		_frame_garage_cam(dt)


# ---------------------------------------------------------------- overlays

## `swap`: another sheet takes its place straight away (Settings rebuilding itself after a change), so nobody is told
## it closed: told, a race's pause menu would hide the menu under the new sheet
func close_modal(keep_keys := false, swap := false) -> void:
	if not keep_keys:
		Keys.wait = []     # a key box left waiting stops waiting when its screen closes
	if modal != null:
		modal.queue_free()
		modal = null
		for k in screens:
			(screens[k] as Control).visible = true
		if not swap:
			modal_kind = ""
			modal_closed.emit()


## every control in a sheet that can take the highlight, in order
static func _focusables(n: Node, out: Array) -> void:
	if n is Control and (n as Control).focus_mode == Control.FOCUS_ALL and (n as Control).is_visible_in_tree():
		out.append(n)
	for c in n.get_children():
		_focusables(c, out)


static func _ctl_text(c: Control) -> String:
	return (c as Button).text if c is Button else c.get_class()


func show_modal(kind: String) -> void:
	# the same sheet shown again (a friends' room updating itself every few seconds, Settings after a change): the
	# highlight is your cursor, so it stays on the button it was on, and the page stays scrolled where it was
	var keep_i := -1
	var keep_t := ""
	var keep_scroll := -1
	if modal != null and modal_kind == kind and is_instance_valid(modal):
		var fo := get_viewport().gui_get_focus_owner()
		if fo != null and modal.is_ancestor_of(fo):
			var L: Array = []
			_focusables(modal, L)
			keep_i = L.find(fo)
			keep_t = _ctl_text(fo)
		for c in modal.get_children():
			if c is ScrollContainer:
				keep_scroll = (c as ScrollContainer).scroll_vertical
	_show_modal(kind)
	if modal == null:
		return
	if keep_scroll > 0:
		for c in modal.get_children():
			if c is ScrollContainer:
				var sc := c as ScrollContainer
				(func():
					if is_instance_valid(sc):
						sc.scroll_vertical = keep_scroll).call_deferred()
	if keep_i >= 0:
		var L2: Array = []
		_focusables(modal, L2)
		if L2.is_empty():
			return
		# the same place in the sheet; if the list changed (a racer joined), the nearest button with the same words
		var pick: Control = L2[mini(keep_i, L2.size() - 1)]
		if _ctl_text(pick) != keep_t:
			var bd := 1 << 30
			for j in L2.size():
				if _ctl_text(L2[j]) == keep_t and absi(j - keep_i) < bd:
					bd = absi(j - keep_i)
					pick = L2[j]
		pick.grab_focus()
		if pick is LineEdit:
			(pick as LineEdit).caret_column = (pick as LineEdit).text.length()


func _show_modal(kind: String) -> void:
	close_modal(kind == "set", true)
	modal_kind = kind
	var m := Control.new()
	m.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	m.mouse_filter = Control.MOUSE_FILTER_STOP
	var dim := _Backdrop.new()
	dim.dim = 1.25
	dim.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	m.add_child(dim)
	var root := _screen_root()
	m.add_child(scroll_wrap(root))
	# centred column: the web's sheets are 760 CSS px wide (Records and Awards use the whole width)
	var widths := {"how": 760.0, "set": 760.0, "tips": 760.0, "mp": 560.0, "netlog": 760.0}
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
	var titles := {"how": "How to play", "rec": "Records", "ach": "Achievements", "set": "Settings", "tips": "Best setup", "mp": "Play with friends", "netlog": "Network log"}
	var head := hbox(14)
	var tl := label(String(titles.get(kind, "")).to_upper(), f_disp, 44.0, CHEESE, SAUCE_DARK, Vector2(0, 4))
	tl.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	head.add_child(tl)
	var done := button("DONE" if kind != "mp" else "✕", "cta" if kind != "mp" else "ghost", 19.0, Vector4(28, 10, 28, 10) if kind != "mp" else Vector4(14, 8, 14, 8))
	done.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	if kind == "netlog" and netlog_back != "":
		# opened from Settings: Done goes back there
		var back := netlog_back
		done.pressed.connect(func(): show_modal(back))
	else:
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
	default_focus = _first_focusable(content)
	if default_focus == null:
		default_focus = done


var netlog_back := ""      # the sheet the network log was opened from ("set"), so Done returns there
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
	["Pick a graphics preset.", "Settings, Graphics: Ultra on a gaming PC, Balanced on most others, Fast on older laptops. PC extras adds longer, softer shadows and bounce light on Ultra; turn it off for a few more frames."],
	["Frame rate.", "The PC version runs at your monitor's rate. Choose 60 fps in Settings, Graphics if it feels uneven."],
	["Full screen.", "F11 switches between full screen and a window."],
]
