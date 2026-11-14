class_name PadCursor
extends Node
## The controller's cursor in the menus (web v194, tools/mini/patch29.py). The owner: "instead of the yellow boxes on controller it
## should just be an on screen cursor and mouse ... the mouse will be controlled with the left stick and make scrolling a right stick
## function as well"; held against the top or bottom of something that scrolls, it scrolls it.
##
## While a menu, the pause sheet or the results are up, the LEFT STICK (and the D-pad) moves the real mouse pointer, and A is the
## mouse's left button at the pointer (held, it drags: a slider follows the stick). So everything that works with a mouse works
## with a controller, and nothing is ringed in yellow: the focus a screen gives its main button when it opens only tells the
## pointer where to start, and is then let go. B (back), Start, the bumpers and the right stick's scrolling are the menus' own,
## as before. A keyboard still walks the focus from button to button.
## This node is the last child of main, so it sees every input before the menus do and takes the stick, the D-pad and A.

var main: Node
var _pad := false          # the controller was the last thing used (not the keyboard)
var _held := false         # A is down: the mouse button is down
var _since_click := 99.0
var _edge := 0.0           # what is left over of an edge scroll, in pixels
var pos := Vector2(-1, -1) # where the pointer is (kept here: the last place it was put, or the real mouse moved it to)
const DEAD := 0.16


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS


func ui_up() -> bool:
	if main == null or bool(main.get("spec_on")):
		return false
	var m = main.get("menu")
	if m != null and (m as Control).visible:
		return true
	for nm in ["panel_pause", "panel_results"]:
		var p = main.get(nm)
		if p != null and (p as Control).visible:
			return true
	return false


func _input(ev: InputEvent) -> void:
	if ev is InputEventMouseMotion:
		pos = (ev as InputEventMouseMotion).position
		return
	if ev is InputEventKey and (ev as InputEventKey).pressed:
		_pad = false
		return
	if not (ev is InputEventJoypadButton or ev is InputEventJoypadMotion):
		return
	if not ui_up():
		if _held:
			_button(false)
		return
	if ev is InputEventJoypadMotion:
		var jm := ev as InputEventJoypadMotion
		if jm.axis == JOY_AXIS_LEFT_X or jm.axis == JOY_AXIS_LEFT_Y:
			if absf(jm.axis_value) > DEAD:
				_pad = true
			get_viewport().set_input_as_handled()     # the stick is the pointer's: it does not walk the focus
		return
	var jb := ev as InputEventJoypadButton
	match jb.button_index:
		JOY_BUTTON_DPAD_UP, JOY_BUTTON_DPAD_DOWN, JOY_BUTTON_DPAD_LEFT, JOY_BUTTON_DPAD_RIGHT:
			_pad = true
			get_viewport().set_input_as_handled()
		JOY_BUTTON_A:
			_pad = true
			get_viewport().set_input_as_handled()
			if jb.pressed != _held:
				_button(jb.pressed)


## the mouse's left button, at the pointer
func _button(down: bool) -> void:
	_held = down
	_since_click = 0.0
	var vp := get_viewport()
	var e := InputEventMouseButton.new()
	e.button_index = MOUSE_BUTTON_LEFT
	e.pressed = down
	e.button_mask = MOUSE_BUTTON_MASK_LEFT if down else 0
	if pos.x < 0.0:
		pos = vp.get_mouse_position()
	e.position = vp.get_final_transform() * pos     # (an event handed to Input is in the window's own pixels; the menus' places are the viewport's)
	e.global_position = e.position
	Input.parse_input_event(e)


func _process(dt: float) -> void:
	_since_click += dt
	if not ui_up():
		return
	var vp := get_viewport()
	var size := vp.get_visible_rect().size
	# the stick, faster the further it is pushed; the D-pad, a steady walk
	var v := Vector2.ZERO
	for j in Input.get_connected_joypads():
		var a := Vector2(Input.get_joy_axis(j, JOY_AXIS_LEFT_X), Input.get_joy_axis(j, JOY_AXIS_LEFT_Y))
		var m := a.length()
		if m > DEAD:
			var f := minf(1.0, (m - DEAD) / (1.0 - DEAD))
			v += a / m * (200.0 + 1300.0 * f * f)
		var d := Vector2(float(Input.is_joy_button_pressed(j, JOY_BUTTON_DPAD_RIGHT)) - float(Input.is_joy_button_pressed(j, JOY_BUTTON_DPAD_LEFT)), float(Input.is_joy_button_pressed(j, JOY_BUTTON_DPAD_DOWN)) - float(Input.is_joy_button_pressed(j, JOY_BUTTON_DPAD_UP)))
		v += d * 430.0
	v *= clampf(minf(size.x, size.y) / 720.0, 0.7, 2.2)
	if _pad:
		# a screen that has just opened gave its main button the focus: the pointer starts there, and the focus (its yellow ring) is let go.
		# A box being typed in keeps it.
		var fo := vp.gui_get_focus_owner()
		if fo != null and not (fo is LineEdit or fo is TextEdit):
			if _since_click > 0.35 and not _held and fo.is_visible_in_tree():
				_move_to(fo.get_global_rect().get_center())
			if not _held:
				vp.gui_release_focus()
	if v == Vector2.ZERO:
		return
	_pad = true
	if pos.x < 0.0:
		pos = vp.get_mouse_position()
	var to := (pos + v * dt).clamp(Vector2(2, 2), size - Vector2(3, 3))
	_move_to(to)
	# held against the top or bottom of what scrolls under it, the pointer scrolls it
	var sc := _scroller(vp.gui_get_hovered_control())
	if sc != null:
		var r := sc.get_global_rect()
		var zone := maxf(36.0, size.y * 0.075)
		var top := maxf(0.0, r.position.y)
		var bot := minf(size.y, r.end.y)
		var pull := 0.0
		if v.y > 0.0 and to.y > bot - zone:
			pull = 260.0 + 1100.0 * clampf((to.y - (bot - zone)) / zone, 0.0, 1.0)
		elif v.y < 0.0 and to.y < top + zone:
			pull = -(260.0 + 1100.0 * clampf((top + zone - to.y) / zone, 0.0, 1.0))
		if pull != 0.0:
			_edge += pull * dt
			var whole := int(_edge)
			if whole != 0:
				sc.scroll_vertical += whole
				_edge -= float(whole)
		else:
			_edge = 0.0


func _move_to(to: Vector2) -> void:
	var vp := get_viewport()
	var was := pos if pos.x >= 0.0 else to
	pos = to
	if Input.mouse_mode != Input.MOUSE_MODE_VISIBLE:
		Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	vp.warp_mouse(to)
	var e := InputEventMouseMotion.new()        # (the pointer's move as the menus hear it: what is under it lights up, a held slider follows)
	var xf := vp.get_final_transform()
	e.position = xf * to
	e.global_position = e.position
	e.relative = xf.basis_xform(to - was)
	e.button_mask = MOUSE_BUTTON_MASK_LEFT if _held else 0
	Input.parse_input_event(e)


func _scroller(c: Control) -> ScrollContainer:
	var n: Node = c
	while n != null:
		if n is ScrollContainer and (n as ScrollContainer).get_v_scroll_bar().max_value > (n as ScrollContainer).size.y + 4.0:
			return n as ScrollContainer
		n = n.get_parent()
	return null
