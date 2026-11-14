extends Node
## The controller's cursor (scripts/pad_cursor.gd), the parts a headless run can check: it is in the tree after the menus (so it
## hears input first), it knows a menu is up, the pointer can be put on a button and the A button's press reaches that button as a
## mouse click, and the focus (the yellow ring) is let go once the controller is in use. Prints PADCUR PASS / FAIL.
## (The stick itself needs a real controller: Input.get_joy_axis has nothing to read here.)

func _ready() -> void:
	var main: Node = load("res://scenes/main.tscn").instantiate()
	add_child(main)
	for i in 30:
		await get_tree().process_frame
	var bad := 0
	var pc = main.get_node_or_null("PadCursor")
	var top: Node = main.menu
	while top.get_parent() != main:
		top = top.get_parent()
	var ok1: bool = pc != null and pc.get_index() > top.get_index() and pc.ui_up()   # after the menus in the tree = before them for input
	print("PADCUR in place, last child, a menu is up: ", ok1, " index ", pc.get_index() if pc != null else -1, " of ", main.get_child_count(), " ui ", pc.ui_up() if pc != null else false, " menu ", main.menu != null and main.menu.visible, " state ", main.state, " after: ", main.get_child(main.get_child_count() - 1).name)
	bad += 0 if ok1 else 1
	if pc != null:
		# the first plain button showing in the menu
		var target: Button = null
		var stack: Array = [main.menu]
		while not stack.is_empty() and target == null:
			var n: Node = stack.pop_back()
			if n is Button and (n as Button).is_visible_in_tree() and not (n as Button).disabled and (n as Button).get_global_rect().size.x > 40.0 and (n as Button).text != "":
				target = n
			for c in n.get_children():
				stack.append(c)
		var hit := [false]
		if target != null:
			target.pressed.connect(func(): hit[0] = true)
			pc._move_to(target.get_global_rect().get_center())
			await get_tree().process_frame
			await get_tree().process_frame
			var a := InputEventJoypadButton.new()
			a.button_index = JOY_BUTTON_A
			a.pressed = true
			Input.parse_input_event(a)
			await get_tree().process_frame
			await get_tree().process_frame
			var b := InputEventJoypadButton.new()
			b.button_index = JOY_BUTTON_A
			b.pressed = false
			Input.parse_input_event(b)
			for i in 6:
				await get_tree().process_frame
		var fo := get_viewport().gui_get_focus_owner()
		var ok2: bool = target != null and hit[0]
		print("PADCUR A on '", target.text if target != null else "?", "' pressed it: ", ok2, "; focus owner after: ", fo)
		bad += 0 if ok2 else 1
		var ok3: bool = fo == null or fo is LineEdit
		print("PADCUR no focus ring left: ", ok3)
		bad += 0 if ok3 else 1
	print("PADCUR PASS" if bad == 0 else "PADCUR FAIL")
	get_tree().quit(0 if bad == 0 else 1)
