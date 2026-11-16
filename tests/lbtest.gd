extends Node
## The world leaderboard on the PC (scripts/lb.gd), reading only (nothing is written to the real board): a Records card clicked opens
## the track's board, the board loads (With rivals, then No items), the board and the username sheet build, and name_free answers.
## Prints LBPC PASS / FAIL.

var main: Node


func _ready() -> void:
	main = load("res://scenes/main.tscn").instantiate()
	main.auto_drive = true   # (no username sheet on its own)
	add_child(main)
	for i in 60:
		await get_tree().process_frame
	var bad := 0
	var lb = main.lb
	print("LBPC token %d chars, name '%s', queue %d" % [lb.token.length(), lb.name_, lb.queue.size()])
	if lb.token.length() < 32:
		bad += 1
	main._to_menu("")
	for i in 20:
		await get_tree().process_frame
	print("LBPC menu tracks %d" % main.menu.maps.size())
	main.menu.show_modal("rec")
	await get_tree().process_frame
	# a click on the first track card
	var card: Control = null
	for c in main.menu.modal.find_children("*", "PanelContainer", true, false):
		if (c as Control).mouse_default_cursor_shape == Control.CURSOR_POINTING_HAND and (c as Control).gui_input.get_connections().size() > 0:
			card = c
			break
	if card == null:
		var n1 := 0
		var n2 := 0
		for c in main.menu.modal.find_children("*", "Control", true, false):
			if (c as Control).mouse_default_cursor_shape == Control.CURSOR_POINTING_HAND:
				n1 += 1
				if c is PanelContainer:
					n2 += 1
		print("LBPC no clickable card (hand cursor %d, of them panels %d, modal %s)" % [n1, n2, main.menu.modal_kind])
		bad += 1
	else:
		var e := InputEventMouseButton.new()
		e.button_index = MOUSE_BUTTON_LEFT
		e.pressed = false
		card.gui_input.emit(e)
	for i in 300:
		await get_tree().process_frame
		if main.menu.modal_kind == "lb" and lb.b_rows != null:
			break
	print("LBPC board open %s for %s (%s), rows %s, error '%s'" % [main.menu.modal_kind == "lb", lb.b_map, lb.b_cls, str(lb.b_rows.size()) if lb.b_rows != null else "null", lb.b_err])
	if main.menu.modal_kind != "lb" or lb.b_rows == null or lb.b_err != "":
		bad += 1
	lb.b_kind = "ni"
	lb._fetch()
	for i in 300:
		await get_tree().process_frame
		if lb.b_rows != null:
			break
	print("LBPC No items board rows %s, error '%s'" % [str(lb.b_rows.size()) if lb.b_rows != null else "null", lb.b_err])
	if lb.b_rows == null or lb.b_err != "":
		bad += 1
	var r: Array = await lb.rpc_call("name_free", {"p_name": "zz_pc_probe_name"})
	print("LBPC name_free answered %s %s" % [r[0], r[1]])
	if not r[0]:
		bad += 1
	main.menu.show_modal("lbname")
	await get_tree().process_frame
	print("LBPC username sheet %s" % (main.menu.modal_kind == "lbname"))
	if main.menu.modal_kind != "lbname":
		bad += 1
	print("LBPC %s" % ("PASS" if bad == 0 else "FAIL"))
	get_tree().quit(0 if bad == 0 else 1)
