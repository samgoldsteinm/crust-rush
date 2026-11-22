"""pc120: two-player split screen on the PC (Single race, Grand Prix, Balloon Battle; off line).
Player 1 on top, player 2 below. Each half is a SubViewport over the same world with its own camera, grade and HUD.
Player 2's kart is race.player2, driven by race.p2_inp from a controller (the last one plugged in). main.gd's camera, HUD and
input code run a second time with player 2's state swapped in (P_VARS / _p_swap), so the halves behave the same.
Menu: Players 1 / 2 on the home screen; with 2, a "Player 2: choose a driver" screen comes before the track.
    python tools/mini/pc120.py"""
G = 'D:/crust-rush/godot/scripts/'


def patch(fn, reps):
    p = G + fn
    s = open(p, encoding='utf-8', newline='').read()
    for a, b in reps:
        assert s.count(a) == 1, (fn, s.count(a), a[:90])
        s = s.replace(a, b)
    open(p, 'w', encoding='utf-8', newline='').write(s)
    return s


# ---------------------------------------------------------------- race.gd
patch('race.gd', [
    ("var player: Kart\n",
     "var player: Kart\n"
     "var player2: Kart = null   # split screen (pc120): the second person's kart, driven by p2_inp\n"
     "var p2_inp := {\"steer\": 0.0, \"brake\": false, \"nb\": false, \"mul\": 1.0, \"use\": false, \"back\": false, \"hold\": false, \"hold_sl\": 1, \"release\": null, \"look\": false}\n"),
    ("\tkarts.clear()\n\tplayer = null\n", "\tkarts.clear()\n\tplayer = null\n\tplayer2 = null\n"),
    ("\t\telif k.is_player and not bool(k.ai.get(\"auto\", false)) and not (k.rush > 0.0 and not (k.mega_t > 0.0) and not (k.pesto_t > 0.0)):\n\t\t\tinp = player_inp\n",
     "\t\telif k == player2 and not bool(k.ai.get(\"auto\", false)) and not (k.rush > 0.0 and not (k.mega_t > 0.0) and not (k.pesto_t > 0.0)):\n"
     "\t\t\tinp = p2_inp   # (pc120: split screen's second player)\n"
     "\t\t\tif bool(p2_inp.get(\"ability\", false)):\n"
     "\t\t\t\tuse_ability(k, bool(p2_inp.get(\"look\", false)))\n"
     "\t\telif k.is_player and not bool(k.ai.get(\"auto\", false)) and not (k.rush > 0.0 and not (k.mega_t > 0.0) and not (k.pesto_t > 0.0)):\n\t\t\tinp = player_inp\n"),
])

# ---------------------------------------------------------------- view.gd
patch('view.gd', [
    ("var me: Kart\n", "var me: Kart\nvar me2: Kart = null   # split screen's second player (pc120): never hidden for being close to the camera\n"),
    ("g.visible = not (k != me and _near_cam(x, y, 14.0)) and not k.elim", "g.visible = not (k != me and k != me2 and _near_cam(x, y, 14.0)) and not k.elim"),
    ("(k == me and i % 3 == 0", "((k == me or k == me2) and i % 3 == 0"),
])

# ---------------------------------------------------------------- menu.gd
patch('menu.gd', [
    ("var cpus := 7 ", "var players := 1       # split screen (pc120): 1, or 2 on one screen\nvar p2_ri := -1         # player 2's driver\n"
     "var p2_pad := -1        # player 2's controller (a device id; -1: the last one plugged in)\nvar p2_guid := \"\"\n"
     "var _pad_wait: Label = null   # waiting for a press on player 2's controller\nvar cpus := 7 "),
    ("func _input(ev: InputEvent) -> void:\n\tif not visible:\n\t\treturn\n",
     "func _input(ev: InputEvent) -> void:\n\tif not visible:\n\t\treturn\n"
     "\t# choosing player 2's controller: the next button pressed on any controller makes it theirs; Esc cancels\n"
     "\tif _pad_wait != null:\n"
     "\t\tif ev is InputEventJoypadButton and (ev as InputEventJoypadButton).pressed:\n"
     "\t\t\tp2_pad = (ev as InputEventJoypadButton).device\n"
     "\t\t\tp2_guid = Input.get_joy_guid(p2_pad)\n"
     "\t\t\tsetting_changed.emit(\"p2_pad\", p2_pad)\n"
     "\t\t\tsetting_changed.emit(\"p2_guid\", p2_guid)\n"
     "\t\t\t_pad_wait = null\n"
     "\t\t\tget_viewport().set_input_as_handled()\n"
     "\t\t\topen.call_deferred(cur)\n"
     "\t\t\treturn\n"
     "\t\tif ev is InputEventKey and (ev as InputEventKey).pressed and (ev as InputEventKey).keycode == KEY_ESCAPE:\n"
     "\t\t\t_pad_wait = null\n"
     "\t\t\tget_viewport().set_input_as_handled()\n"
     "\t\t\topen.call_deferred(cur)\n"
     "\t\t\treturn\n"
     "\t\tif ev is InputEventJoypadMotion:\n"
     "\t\t\treturn\n"),
    ("\tclose_modal()\n\tfor k in screens:\n",
     "\t# two players: player 2 picks a driver before the track (pc120)\n"
     "\tif name_ == \"track\" and _two_up() and cur != \"driver2\" and cur != \"track\":\n"
     "\t\tname_ = \"driver2\"\n"
     "\tclose_modal()\n\tfor k in screens:\n"),
    ("\t\t\"driver\":\n\t\t\ts = _driver()\n", "\t\t\"driver\":\n\t\t\ts = _driver()\n\t\t\"driver2\":\n\t\t\ts = _driver(true)\n"),
    ("func _driver() -> Control:", "func _driver(p2 := false) -> Control:"),
    ("\tv.add_child(_step_head(\"‹ Sandbox\" if shop else (\"‹ Room\" if net != \"\" else \"‹ Back\"), \"home\", \"Step 1 of 3\" if three else \"Step 1 of 2\", \"Choose your driver\", nx_t, nx_f))\n",
     "\tif p2:\n"
     "\t\tif p2_ri < 0 or p2_ri == ri or p2_ri >= racers_info.size():\n"
     "\t\t\tp2_ri = (ri + 1) % maxi(1, racers_info.size())\n"
     "\t\t\tsetting_changed.emit(\"p2_ri\", p2_ri)\n"
     "\t\tv.add_child(_step_head(\"‹ Back\", \"garage\" if three else \"driver\", \"Split screen\", \"Player 2: choose a driver\", \"CHOOSE TRACK  ›\", func(): open(\"track\")))\n"
     "\t\t# which controller is player 2's: Choose, then press a button on it. Player 1 has the keyboard and every other controller\n"
     "\t\tvar crow := hbox(12)\n"
     "\t\tvar pd := pad_for_p2(p2_pad, p2_guid)\n"
     "\t\tvar ptxt := \"No controller is plugged in\" if pd < 0 else (\"%s (controller %d)\" % [Input.get_joy_name(pd), Input.get_connected_joypads().find(pd) + 1] + (\"\" if (pd == p2_pad or p2_guid != \"\") else \", the last one plugged in\"))\n"
     "\t\tvar cl := label((\"Player 2's controller · \" + ptxt).to_upper(), f_bold, 12.0, CREAM)\n"
     "\t\tcl.size_flags_horizontal = Control.SIZE_EXPAND_FILL\n"
     "\t\tcl.vertical_alignment = VERTICAL_ALIGNMENT_CENTER\n"
     "\t\tvar cbtn := button(\"Choose controller\", \"ghost\", 14.0, Vector4(14, 8, 14, 8))\n"
     "\t\tcbtn.pressed.connect(func():\n"
     "\t\t\t_pad_wait = cl\n"
     "\t\t\tcl.text = \"PRESS A BUTTON ON PLAYER 2'S CONTROLLER  (ESC: CANCEL)\")\n"
     "\t\tcrow.add_child(cl)\n"
     "\t\tcrow.add_child(cbtn)\n"
     "\t\tv.add_child(crow)\n"
     "\t\tv.add_child(para(\"Player 1 drives with the keyboard and every other controller. Player 2 races this driver's own kart.\", 13.0, MUTED, 900.0))\n"
     "\telse:\n"
     "\t\tv.add_child(_step_head(\"‹ Sandbox\" if shop else (\"‹ Room\" if net != \"\" else \"‹ Back\"), \"home\", \"Step 1 of 3\" if three else \"Step 1 of 2\", \"Choose your driver\", nx_t, nx_f))\n"),
    ("\t\tcard.pressed.connect(func():\n\t\t\tri = i\n\t\t\tshow_detail.call(i)\n\t\t\tsetting_changed.emit(\"ri\", i)\n\t\t\tfor c in grid.get_children():\n\t\t\t\t_mark_card(c as Button, int(c.get_meta(\"i\")) == ri, true))\n\t\tgrid.add_child(card)\n\t\tif i == ri:\n\t\t\tsel_focus = card\n\tshow_detail.call(ri)\n",
     "\t\tcard.pressed.connect(func():\n"
     "\t\t\tif p2:\n\t\t\t\tp2_ri = i\n\t\t\t\tsetting_changed.emit(\"p2_ri\", i)\n"
     "\t\t\telse:\n\t\t\t\tri = i\n\t\t\t\tsetting_changed.emit(\"ri\", i)\n"
     "\t\t\tshow_detail.call(i)\n"
     "\t\t\tvar on_i := p2_ri if p2 else ri\n"
     "\t\t\tfor c in grid.get_children():\n\t\t\t\t_mark_card(c as Button, int(c.get_meta(\"i\")) == on_i, true))\n"
     "\t\tgrid.add_child(card)\n"
     "\t\tif p2:\n\t\t\t_mark_card(card, i == p2_ri, true)\n"
     "\t\tif i == (p2_ri if p2 else ri):\n\t\t\tsel_focus = card\n"
     "\tshow_detail.call(p2_ri if p2 else ri)\n"),
    ("\tcol.add_child(s3)\n",
     "\tcol.add_child(s3)\n"
     "\t# two players on one screen (pc120): off line, in a race, a Grand Prix or a battle\n"
     "\tif net == \"\" and not shop and (mode == \"gp\" or mode == \"single\" or mode == \"bb\"):\n"
     "\t\tvar s5 := vbox(8)\n"
     "\t\ts5.add_child(section_label(\"Players\"))\n"
     "\t\tvar pl_note := para(\"\", 13.0, MUTED, 300.0)\n"
     "\t\tvar pl_upd := func():\n"
     "\t\t\tvar pn := Input.get_connected_joypads().size()\n"
     "\t\t\tpl_note.text = \"Just you\" if players == 1 else (\"Split screen: player 2 drives with a controller\" + (\"\" if pn > 0 else \" (plug one in)\"))\n"
     "\t\ts5.add_child(seg(\"players\", [[\"1\", \"1 player\"], [\"2\", \"2 players\"]], str(players), func(k):\n"
     "\t\t\tplayers = int(k)\n"
     "\t\t\tpl_upd.call()\n"
     "\t\t\tsetting_changed.emit(\"players\", players), 14.0, 10.0))\n"
     "\t\tpl_upd.call()\n"
     "\t\ts5.add_child(pl_note)\n"
     "\t\tcol.add_child(s5)\n"),
    ("func _go() -> void:\n",
     "## player 2's controller now: the one chosen if it is plugged in (by id, else by its kind), else the last one plugged in\n"
     "static func pad_for_p2(want: int, guid: String) -> int:\n"
     "\tvar pads := Input.get_connected_joypads()\n"
     "\tif pads.has(want):\n\t\treturn want\n"
     "\tif guid != \"\":\n\t\tfor j in pads:\n\t\t\tif Input.get_joy_guid(j) == guid:\n\t\t\t\treturn int(j)\n"
     "\treturn int(pads[pads.size() - 1]) if not pads.is_empty() else -1\n\n\n"
     "## two players on one screen (pc120)\n"
     "func _two_up() -> bool:\n"
     "\treturn players == 2 and net == \"\" and not shop and (mode == \"gp\" or mode == \"single\" or mode == \"bb\")\n\n\n"
     "func _go() -> void:\n"),
])

# ---------------------------------------------------------------- main.gd
p = G + 'main.gd'
s = open(p, encoding='utf-8', newline='').read()
# the grade's per-frame settings become a function, run for each half
a0 = "\t# post: edge flash, speed streaks while boosting\n"
a1 = "\tpost_mat.set_shader_parameter(\"tm\", time)\n\t_hud(dt)\n"
assert s.count(a0) == 1 and s.count(a1) == 1
i0 = s.index(a0); i1 = s.index(a1)
block = s[i0:i1] + "\tpost_mat.set_shader_parameter(\"tm\", time)\n"
s = s[:i0] + ("\t_post_tick(dt)\n\t_hud(dt)\n"
              "\tif split_live and kart2 != null and view.views.has(kart2):\n\t\t_p2_pass(dt)\n") + s[i1 + len(a1):]
POST_FN = "\n\n## the grade's per-frame settings (edge flash, boost streaks, motion blur); split screen runs it for each half\nfunc _post_tick(dt: float) -> void:\n" + block

SPLIT = '''

# ---------------------------------------------------------------- split screen (pc120)
## Two players on one screen: player 1 on top, player 2 below. Each half is a SubViewport over the same world with its own
## camera, grade (post) and HUD. Player 2's kart is race.player2, driven by race.p2_inp from the controller p2_pad. The camera,
## HUD and input code is the one-player code run a second time with player 2's state swapped in (P_VARS, _p_swap).
const P_VARS := ["kart", "hud", "cam", "post_mat", "cam_a", "cam_base", "cam_look", "cam_sb", "cam_sa", "cam_snap", "shake_imp", "cam_gp",
	"cam_gr", "cam_sx", "cam_oy", "cam_vy", "cam_pvz", "cam_pspd", "cam_occ", "cam_lb", "cam_bo", "cam_up", "bb_cam_f", "look_back", "aim_back",
	"spec_k", "pad_held", "pad_hold", "item_queued", "pad_used_at", "last_lap", "shown_finish", "edge_c", "edge_a", "edge_t", "spd_fx", "mb_fx",
	"fin_punch", "inc_beep", "roll_tick"]
var split_live := false
var kart2: Kart = null
var hud2: Hud = null
var cam2: Camera3D = null
var post2: ColorRect = null
var p2 := {}                  # player 2's copy of P_VARS while player 1's are in place
var p2_pad := -1              # player 2's controller
var _in_p2 := false           # the code is running for player 2 now
var sv_layer: CanvasLayer = null
var sv_ports: Array = []      # the two halves (SubViewport)
var sv_hud: Array = []        # each half's HUD holder
var sv_post: Array = []       # each half's grade layer
var cam_home: Node = null     # where the camera, the grade and the HUD live with one player
var post_home: Node = null
var _sv_sync_t := 0.0


func _p_swap() -> void:
	for n in P_VARS:
		var a = get(n)
		set(n, p2[n])
		p2[n] = a


## a race started from the menu with Players 2 (CR_SPLIT=1 for the tests), off line, with a controller for player 2
func _split_want() -> bool:
	var forced := OS.get_environment("CR_SPLIT") == "1"
	if not (forced or int(sel.get("players", 1)) == 2):
		return false
	if net_role != "" or web.role != "" or not ["gp", "single", "bb"].has(String(sel.get("mode", ""))):
		return false
	if Input.get_connected_joypads().is_empty() and not forced:
		_toast("Plug in a controller for player 2", 2.4)
		return false
	return true


## the controller this player drives with: player 2 their own, player 1 the first of the others
func _my_pad() -> int:
	var pads := Input.get_connected_joypads()
	if _in_p2:
		return p2_pad if pads.has(p2_pad) else -1
	for j in pads:
		if not (split_live and int(j) == p2_pad):
			return int(j)
	return -1


func _sv_sync() -> void:
	var r := get_viewport()
	for sv in sv_ports:
		for pn in ["msaa_3d", "screen_space_aa", "use_taa", "use_debanding", "scaling_3d_mode", "scaling_3d_scale", "fsr_sharpness", "mesh_lod_threshold",
				"use_occlusion_culling", "positional_shadow_atlas_size", "anisotropic_filtering_level", "texture_mipmap_bias"]:
			if pn in r and pn in sv:
				(sv as SubViewport).set(pn, r.get(pn))


func _split_start() -> void:
	# player 2's controller: the one chosen on the menu's player 2 screen, else the last one plugged in
	p2_pad = Menu.pad_for_p2(int(sel.get("p2_pad", -1)), String(sel.get("p2_guid", "")))
	if sv_layer == null:
		sv_layer = CanvasLayer.new()
		sv_layer.layer = -2
		add_child(sv_layer)
		var bg := ColorRect.new()
		bg.color = Color(0.03, 0.02, 0.02)
		bg.set_anchors_preset(Control.PRESET_FULL_RECT)
		bg.mouse_filter = Control.MOUSE_FILTER_IGNORE
		sv_layer.add_child(bg)
		var box := VBoxContainer.new()
		box.set_anchors_preset(Control.PRESET_FULL_RECT)
		box.add_theme_constant_override("separation", 4)
		box.mouse_filter = Control.MOUSE_FILTER_IGNORE
		sv_layer.add_child(box)
		for i in 2:
			var c := SubViewportContainer.new()
			c.stretch = true
			c.size_flags_vertical = Control.SIZE_EXPAND_FILL
			c.size_flags_horizontal = Control.SIZE_EXPAND_FILL
			c.mouse_filter = Control.MOUSE_FILTER_IGNORE
			box.add_child(c)
			var sv := SubViewport.new()
			sv.audio_listener_enable_3d = false
			c.add_child(sv)
			var pl := CanvasLayer.new()
			pl.layer = -1
			sv.add_child(pl)
			var hl := CanvasLayer.new()
			hl.layer = 1
			sv.add_child(hl)
			var holder := Control.new()
			holder.set_anchors_preset(Control.PRESET_FULL_RECT)
			holder.mouse_filter = Control.MOUSE_FILTER_IGNORE
			hl.add_child(holder)
			sv_ports.append(sv)
			sv_post.append(pl)
			sv_hud.append(holder)
		cam2 = Camera3D.new()
		(sv_ports[1] as SubViewport).add_child(cam2)
		post2 = ColorRect.new()
		post2.set_anchors_preset(Control.PRESET_FULL_RECT)
		post2.mouse_filter = Control.MOUSE_FILTER_IGNORE
		(sv_post[1] as CanvasLayer).add_child(post2)
		hud2 = Hud.new()
		(sv_hud[1] as Control).add_child(hud2)
	sv_layer.visible = true
	var w := get_viewport().find_world_3d()
	for sv in sv_ports:
		(sv as SubViewport).world_3d = w
	_sv_sync()
	_sv_sync_t = 1.0
	# player 1's camera, grade and HUD move into the top half
	cam_home = cam.get_parent()
	post_home = post.get_parent()
	cam.reparent(sv_ports[0], false)
	post.reparent(sv_post[0], false)
	hud.reparent(sv_hud[0], false)
	cam.make_current()
	cam2.near = cam.near
	cam2.far = cam.far
	cam2.fov = cam.fov
	cam2.attributes = cam.attributes
	cam2.environment = cam.environment
	cam2.cull_mask = cam.cull_mask
	cam2.compositor = cam.compositor
	cam2.make_current()
	post2.material = post_mat.duplicate()
	hud2.kmh = hud.kmh
	hud2.show_touch = false
	hud2.race = race
	hud2.me = kart2
	hud2.T = T
	hud2.icons = icons
	hud2.portraits = portraits
	hud2.racer_cols = hud.racer_cols
	hud2.pb_text = ""
	hud2.banner("", 0.0)
	view.me2 = kart2
	p2 = {}
	for n in P_VARS:
		var a = get(n)
		p2[n] = a.duplicate() if (a is Array or a is Dictionary) else a
	p2["kart"] = kart2
	p2["hud"] = hud2
	p2["cam"] = cam2
	p2["post_mat"] = post2.material
	p2["spec_k"] = null
	p2["cam_a"] = kart2.ma
	p2["cam_snap"] = true
	p2["shake_imp"] = 0.0
	p2["item_queued"] = ""
	p2["last_lap"] = 1
	p2["shown_finish"] = false
	p2["look_back"] = false
	p2["aim_back"] = false
	p2["pad_held"] = [false, false, false]
	p2["pad_hold"] = [0, 0, 0]
	p2["pad_used_at"] = Time.get_ticks_msec()
	get_viewport().disable_3d = true   # (the halves draw the world; the window itself only shows them)
	split_live = true


func _split_stop() -> void:
	if not split_live:
		return
	split_live = false
	kart2 = null
	view.me2 = null
	cam.reparent(cam_home, false)
	post.reparent(post_home, false)
	hud.reparent(hud_race, false)
	hud_race.move_child(hud, 0)
	cam.make_current()
	sv_layer.visible = false
	get_viewport().disable_3d = false


func _p2_input() -> Dictionary:
	_p_swap()
	_in_p2 = true
	var o := _input_state()
	_in_p2 = false
	_p_swap()
	return o


## player 2's own shakes and hit flash (the rest of the race's events are drained once, for player 1)
func _p2_events() -> void:
	for e in kart2.events:
		if String(e).begins_with("boost"):
			p2["shake_imp"] = minf(1.6, float(p2["shake_imp"]) + 0.2)
	for ed in race.fx:
		if ed is Dictionary and String((ed as Dictionary).get("t", "")) == "spin" and (ed as Dictionary).get("k") == kart2:
			p2["shake_imp"] = minf(1.6, float(p2["shake_imp"]) + 1.1)
			hud2.hit_flash()


## player 2's laps and finish, on their own half
func _p2_checks() -> void:
	if race.mode == "lss" or race.mode == "bb" or race.mode == "sb":
		return
	if kart2.finished and not bool(p2["shown_finish"]):
		p2["shown_finish"] = true
		kart2.ai["auto"] = true
		hud2.banner("Finish!", 2.4, "md")
		sfx.play("finish")
	var lp := kart2.lap()
	if lp != int(p2["last_lap"]) and not kart2.finished:
		p2["last_lap"] = lp
		hud2.banner("Final lap" if lp == T.LAPS else "Lap %d" % lp, 1.4, "sm")
		sfx.play("lap", 0.8, 1.2 if lp == T.LAPS else 1.0)


func _show_both(t: String, dur: float, kind := "md") -> void:
	_show_center(t, dur, kind)
	if split_live and hud2 != null:
		hud2.banner(t, dur, kind)


## player 2's camera, grade and HUD: player 1's code with player 2's state swapped in
func _p2_pass(dt: float) -> void:
	_sv_sync_t -= dt
	if _sv_sync_t <= 0.0:
		_sv_sync_t = 1.0
		_sv_sync()
	var sp := sun.global_position
	_p_swap()
	_in_p2 = true
	var v: Dictionary = view.views[kart]
	_camera(dt, float(v["rx"]), float(v["ry"]), float(v["rz"]), float(v["rma"]))
	_post_tick(dt)
	_hud(dt)
	_in_p2 = false
	_p_swap()
	sun.global_position = sp
'''

R = [
    ("var aim_back := false ", "var aim_back := false "),  # (anchor check only)
    ("\tvar typing := get_viewport().gui_get_focus_owner() is LineEdit\n", "\tvar typing := _in_p2 or get_viewport().gui_get_focus_owner() is LineEdit   # (player 2 has no keyboard)\n"),
    ("\tvar pads := Input.get_connected_joypads()\n\tif pads.size() > 0:\n\t\tvar j: int = pads[0]\n\t\tvar ax := Input.get_joy_axis(j, JOY_AXIS_LEFT_X)\n",
     "\tvar j: int = _my_pad()   # (pc120: with two players each has their own)\n\tif j >= 0:\n\t\tvar ax := Input.get_joy_axis(j, JOY_AXIS_LEFT_X)\n"),
    ("\t# touch\n\tvar l := false\n\tvar r := false\n\tfor k in touches:\n", "\t# touch\n\tvar l := false\n\tvar r := false\n\tfor k in ({} if _in_p2 else touches):\n"),
    ("\trace.update(dt, _input_state())\n\t_drain_events()\n",
     "\tif split_live and kart2 != null:\n\t\trace.p2_inp = _p2_input()\n\trace.update(dt, _input_state())\n\tif split_live and kart2 != null:\n\t\t_p2_events()\n\t_drain_events()\n"),
    ("\t\tif after != before and after > 0:\n\t\t\t_show_center(str(after), 0.9)\n", "\t\tif after != before and after > 0:\n\t\t\t_show_both(str(after), 0.9)\n"),
    ("\t\t\t\t_show_center(\"Go!\", 1.0)\n", "\t\t\t\t_show_both(\"Go!\", 1.0)\n"),
    ("\t\t_finish_check()\n\t\t# the race is over once every person has finished", "\t\t_finish_check()\n\t\tif split_live and kart2 != null:\n\t\t\t_p2_checks()\n\t\t# the race is over once every person has finished"),
    ("\tif spec_on or kart == null or race == null or race.mode == \"lss\"", "\tif split_live or spec_on or kart == null or race == null or race.mode == \"lss\""),
    ("func _spec_enter() -> void:\n", "func _spec_enter() -> void:\n\tif split_live:\n\t\treturn   # (split screen: each half stays on its own kart)\n"),
    ("\t_spec_tick(dt)\n\tvar k := kart\n\thud.fps_on = fps_counter\n", "\tif not _in_p2:\n\t\t_spec_tick(dt)\n\tvar k := kart\n\thud.fps_on = fps_counter\n"),
    ("\tif lbl_info.visible:\n\t\tvar vr := get_viewport().get_viewport_rid()", "\tif lbl_info.visible and not _in_p2:\n\t\tvar vr := get_viewport().get_viewport_rid()"),
    ("\tsfx.drive(absf(k.speed) / k.base_max,", "\tif not _in_p2:   # (the engine you hear is player 1's)\n\t\tsfx.drive(absf(k.speed) / k.base_max,"),
    ("\tif k.roll > 0.0 and not paused:\n\t\troll_tick -= dt", "\tif k.roll > 0.0 and not paused and not _in_p2:\n\t\troll_tick -= dt"),
    ("\tif test_drive and kart != null and race != null and state == \"race\" and not kart.finished and spec_k == null and race.mode != \"bb\" and race.mode != \"sb\":\n\t\thud.td = race.td_tick(kart)",
     "\tif not _in_p2 and test_drive and kart != null and race != null and state == \"race\" and not kart.finished and spec_k == null and race.mode != \"bb\" and race.mode != \"sb\":\n\t\thud.td = race.td_tick(kart)"),
    ("\t\tvar jb := ev as InputEventJoypadButton\n\t\tif jb.pressed:\n\t\t\tpad_used_at = Time.get_ticks_msec()\n",
     "\t\tvar jb := ev as InputEventJoypadButton\n"
     "\t\tif jb.pressed and split_live and kart2 != null and jb.device == p2_pad:\n"
     "\t\t\t# split screen: player 2's controller (its stick, triggers and item buttons are read in _input_state)\n"
     "\t\t\tp2[\"pad_used_at\"] = Time.get_ticks_msec()\n"
     "\t\t\tif jb.button_index == JOY_BUTTON_Y and state == \"race\" and not paused:\n\t\t\t\tp2[\"item_queued\"] = \"ability\"\n"
     "\t\t\tif jb.button_index == JOY_BUTTON_START:\n\t\t\t\tif state == \"results\":\n\t\t\t\t\t_results_primary()\n"
     "\t\t\t\telif not (menu != null and menu.visible):\n\t\t\t\t\t_toggle_pause()\n\t\t\treturn\n"
     "\t\tif jb.pressed:\n\t\t\tpad_used_at = Time.get_ticks_msec()\n"),
    ("\thud_race.visible = true\n\t_clear_race_nodes()\n", "\thud_race.visible = true\n\t_split_stop()\n\t_clear_race_nodes()\n"),
    ("\tif cfg.is_empty():\n\t\trace.setup(T, roster, pri, 0, String(sel[\"cls\"]), _my_build(), cpu_n)\n\telse:\n",
     "\tvar two := not bg and cfg.is_empty() and _split_want()\n"
     "\tif two:\n"
     "\t\t# split screen (pc120): two people in the middle of the grid, as an online room seats them\n"
     "\t\tvar cf := race.make_cfg(roster, pri, [1, 2], (randi() & 0x7fffffff) + 1, String(sel[\"cls\"]), _my_build(), {2: {\"ri\": int(sel.get(\"p2_ri\", -1))}})\n"
     "\t\tRace.trim_cpus(cf, cpu_n)\n"
     "\t\trace.setup_cfg(T, roster, cf, 1)\n"
     "\telif cfg.is_empty():\n\t\trace.setup(T, roster, pri, 0, String(sel[\"cls\"]), _my_build(), cpu_n)\n\telse:\n"),
    ("\tkart = race.player\n\trace.net_on = net_role != \"\" or web.role != \"\"\n",
     "\tkart = race.player\n"
     "\tkart2 = null\n"
     "\tif two:\n\t\tfor k in race.karts:\n\t\t\tif k.peer == 2:\n\t\t\t\tkart2 = k\n"
     "\t\tif kart2 != null:\n\t\t\tkart2.remote = false\n\t\t\tkart2.is_player = true\n\t\t\tkart2.ai[\"auto\"] = auto_drive\n\t\t\trace.player2 = kart2\n"
     "\trace.net_on = net_role != \"\" or web.role != \"\"\n"),
    ("\telif race.mode == \"lss\" or auto_drive:\n\t\tghost.start({}, false, kart.ri, {})\n\t\tghost.recording = not auto_drive\n",
     "\telif race.mode == \"lss\" or auto_drive or kart2 != null:   # (split screen: no ghost on either half)\n\t\tghost.start({}, false, kart.ri, {})\n\t\tghost.recording = not auto_drive and kart2 == null\n"),
    ("\t\thud.racer_cols.append(Color.html(String((r as Dictionary)[\"color\"])))\n\tstate = \"countdown\"\n",
     "\t\thud.racer_cols.append(Color.html(String((r as Dictionary)[\"color\"])))\n\tif kart2 != null:\n\t\t_split_start()\n\tstate = \"countdown\"\n"),
    ("\t_show_center(\"3\", 0.9)\n\n\nfunc _show_center", "\t_show_both(\"3\", 0.9)\n\n\nfunc _show_center"),
    ("\tfor k in [\"mode\", \"cls\", \"ri\", \"cup\"]:\n\t\tsel[k] = cf.get_value(\"menu\", k, sel[k])\n",
     "\tfor k in [\"mode\", \"cls\", \"ri\", \"cup\"]:\n\t\tsel[k] = cf.get_value(\"menu\", k, sel[k])\n"
     "\tfor k in [\"players\", \"p2_ri\", \"p2_pad\", \"p2_guid\"]:   # (pc120: split screen's choices)\n"
     "\t\tif cf.has_section_key(\"menu\", k):\n\t\t\tsel[k] = cf.get_value(\"menu\", k)\n"),
    ("\t\tsel[k] = v\n\t\tif k == \"favs\":\n\t\t\t_save_settings()\n",
     "\t\tsel[k] = v\n\t\tif k == \"favs\" or k == \"players\" or k == \"p2_ri\" or k == \"p2_guid\":\n\t\t\t_save_settings()\n"),
    ("\tmenu.cpus = clampi(int(sel.get(\"cpus\", 7)), 0, 7)\n",
     "\tmenu.cpus = clampi(int(sel.get(\"cpus\", 7)), 0, 7)\n\tmenu.players = clampi(int(sel.get(\"players\", 1)), 1, 2)\n\tmenu.p2_ri = int(sel.get(\"p2_ri\", -1))\n"
     "\tmenu.p2_pad = int(sel.get(\"p2_pad\", -1))\n\tmenu.p2_guid = String(sel.get(\"p2_guid\", \"\"))\n"),
]
for a, b in R:
    assert s.count(a) == 1, ('main.gd', s.count(a), a[:90])
    s = s.replace(a, b)
s = s.rstrip('\n') + '\n' + POST_FN.rstrip('\n') + '\n' + SPLIT
open(p, 'w', encoding='utf-8', newline='').write(s)
print('pc120 applied')
