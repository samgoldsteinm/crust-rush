extends Node
## World leaderboards and usernames on the PC (web v207 tools/mini/patch44.py, v209 patch47: the No items boards). The owner's Supabase
## project, read and written with its publishable key only (public by design; the database's functions check everything):
##   name_free(p_name), claim_name(p_token, p_name), whoami(p_token), submit_run(... p_solo [, p_noitems]); the view best_runs.
## A player is a random token kept on this PC (Settings > More > Username > Account code moves it to another device) and a name.
## Every finished race (not Last Slice, Balloon Battle or Sandbox, not the automatic drives) goes on a queue kept on disk and is sent
## when there is a name and a connection, so races off line count too. Boards: a track, a speed class, With rivals / Alone / No items,
## the top 20 (each player's best). Child of main ("Lb"); main.menu shows the sheets "lbname" and "lb" (built here).

const URL := "https://ymlfwrwrewxxsazylprf.supabase.co"
const KEY := "sb_publishable_K_widd5Q0EyMhUm7JVuv_Q_FWXc0CQZ"
const CLS := {"small": "easy", "medium": "medium", "large": "hard", "reverse": "mirror"}
const CLS_LABEL := {"small": "50cc", "medium": "100cc", "large": "200cc", "reverse": "Reverse"}
const CFG_PATH := "user://leaderboard.cfg"

var main: Node
var token := ""
var name_ := ""
var queue: Array = []
var busy := false
# the board on show
var b_map := ""
var b_name := ""
var b_cls := "medium"
var b_kind := "rivals"      # rivals | alone | ni
var b_rows = null           # null: loading; Array: the rows
var b_err := ""
var b_seq := 0
var name_back := ""         # the sheet to go back to after the username sheet ("set", "lb" or "")
var _name_seq := 0


func _ready() -> void:
	_load()
	flush()


func _load() -> void:
	var cf := ConfigFile.new()
	cf.load(CFG_PATH)
	token = String(cf.get_value("lb", "token", ""))
	name_ = String(cf.get_value("lb", "name", ""))
	var q = cf.get_value("lb", "queue", [])
	queue = q if q is Array else []
	if token.length() < 32:
		var c := Crypto.new()
		token = c.generate_random_bytes(20).hex_encode()
		_save()


func _save() -> void:
	var cf := ConfigFile.new()
	cf.set_value("lb", "token", token)
	cf.set_value("lb", "name", name_)
	cf.set_value("lb", "queue", queue.slice(maxi(0, queue.size() - 40)))
	cf.save(CFG_PATH)


## one request to the board: [ok, data, message, from the server (not a lost connection)]
func _http(method: int, path: String, body = null) -> Array:
	var h := HTTPRequest.new()
	h.timeout = 15.0
	add_child(h)
	var headers := PackedStringArray(["apikey: " + KEY, "Content-Type: application/json"])
	var err := h.request(URL + path, headers, method, "" if body == null else JSON.stringify(body))
	if err != OK:
		h.queue_free()
		return [false, null, "no connection", false]
	var r: Array = await h.request_completed
	h.queue_free()
	if int(r[0]) != HTTPRequest.RESULT_SUCCESS:
		return [false, null, "no connection", false]
	var txt := (r[3] as PackedByteArray).get_string_from_utf8()
	var data = JSON.parse_string(txt) if txt.strip_edges() != "" else null
	var code := int(r[1])
	if code < 200 or code >= 300:
		var msg := "HTTP %d" % code
		if data is Dictionary and (data as Dictionary).has("message"):
			msg = String(data["message"])
		return [false, data, msg, true]
	return [true, data, "", true]


func rpc_call(fn: String, body: Dictionary) -> Array:
	return await _http(HTTPClient.METHOD_POST, "/rest/v1/rpc/" + fn, body)


static func map_key(id: String) -> String:
	return id.substr(0, 24)


## a finished race, on the queue, then sent (main._progress_finish)
func run(map_id: String, cls: String, t: float, driver: String, kart: String, solo: bool, ni: bool) -> void:
	if not CLS.has(cls) or t <= 0.0:
		return
	queue.append({"map": map_key(map_id), "cls": CLS[cls], "ms": int(round(t * 1000.0)), "drv": driver.substr(0, 16), "kart": kart.substr(0, 32), "solo": solo, "ni": ni})
	_save()
	flush()


func flush() -> void:
	if busy or name_ == "":
		return
	busy = true
	while not queue.is_empty():
		var r: Dictionary = queue[0]
		var body := {"p_token": token, "p_map": r["map"], "p_cls": r["cls"], "p_time_ms": int(r["ms"]), "p_driver": r["drv"], "p_kart": r["kart"], "p_platform": "pc", "p_ver": "pc", "p_solo": bool(r["solo"])}
		if bool(r.get("ni", false)):
			body["p_noitems"] = true
		var res: Array = await rpc_call("submit_run", body)
		if res[0]:
			queue.pop_front()
			_save()
		elif res[3] and String(res[2]).find("no player") < 0:
			queue.pop_front()   # a run the board refuses is dropped; a missing player or no connection waits
			_save()
		else:
			break
	busy = false


# ---------------------------------------------------------------- the boards

## a track's board (Records: a track card)
func open_board(map_id: String, map_name: String, cls: String) -> void:
	b_map = map_id
	b_name = map_name
	b_cls = cls if CLS.has(cls) else "medium"
	b_kind = "rivals"
	_fetch()
	main.menu.lb_title = map_name
	main.menu.show_modal("lb")


func _fetch() -> void:
	b_seq += 1
	var my := b_seq
	b_rows = null
	b_err = ""
	var f := ("&noitems=eq.true" if b_kind == "ni" else "&solo=eq.%s&noitems=eq.false" % ("true" if b_kind == "alone" else "false"))
	var q := "/rest/v1/best_runs?select=name,driver,kart,platform,time_ms&map=eq.%s&cls=eq.%s%s&order=time_ms.asc,created_at.asc&limit=20" % [map_key(b_map).uri_encode(), CLS[b_cls], f]
	var res: Array = await _http(HTTPClient.METHOD_GET, q)
	if my != b_seq:
		return
	if res[0] and res[1] is Array:
		b_rows = res[1]
	else:
		b_rows = []
		b_err = "Cannot reach the leaderboard right now."
	if main.menu.modal_kind == "lb":
		main.menu.show_modal("lb")


func board_panel() -> Control:
	var M = main.menu
	var v: VBoxContainer = M.vbox(12)
	var tools: HBoxContainer = M.hbox(10)
	var co: Array = []
	for k in ["small", "medium", "large", "reverse"]:
		co.append([k, CLS_LABEL[k]])
	tools.add_child(M.seg("lbcls", co, b_cls, func(k):
		b_cls = k
		_fetch()
		M.show_modal("lb"), 14.0, 8.0))
	tools.add_child(M.seg("lbkind", [["rivals", "With rivals"], ["alone", "Alone"], ["ni", "No items"]], b_kind, func(k):
		b_kind = k
		_fetch()
		M.show_modal("lb"), 14.0, 8.0))
	v.add_child(tools)
	var list: VBoxContainer = M.vbox(6)
	if b_rows == null:
		list.add_child(M.label("Loading...", M.f_med, 15.0, Color("#c2a58c")))
	elif b_err != "":
		list.add_child(M.label(b_err, M.f_med, 15.0, Color("#c2a58c")))
	elif (b_rows as Array).is_empty():
		list.add_child(M.label("No times yet. Be the first!", M.f_med, 15.0, Color("#c2a58c")))
	else:
		var i := 0
		for r in b_rows:
			i += 1
			var rd: Dictionary = r
			var mine := name_ != "" and String(rd.get("name", "")).to_lower() == name_.to_lower()
			var card: PanelContainer = M.panel(M.glass(10.0, Vector4(12, 6, 12, 6)) if not mine else M.box([Color(0.97, 0.79, 0.28, 0.2), Color(0.88, 0.27, 0.17, 0.14)], 135.0, 10.0, Color(0.97, 0.79, 0.28, 0.6), 1.0, Vector4(12, 6, 12, 6)))
			var h: HBoxContainer = M.hbox(12)
			card.add_child(h)
			var pl: Label = M.label(str(i), M.f_disp, 18.0, Color("#f7c948"))
			pl.custom_minimum_size.x = M.z(34)
			h.add_child(pl)
			var nv: VBoxContainer = M.vbox(0)
			nv.size_flags_horizontal = Control.SIZE_EXPAND_FILL
			nv.add_child(M.label("%s  ·  %s" % [String(rd.get("name", "")), "PC" if String(rd.get("platform", "")) == "pc" else "WEB"], M.f_bold, 15.0, Color("#fff4dc")))
			nv.add_child(M.label("%s · %s" % [String(rd.get("driver", "")), String(rd.get("kart", ""))], M.f_med, 12.0, Color("#c2a58c")))
			h.add_child(nv)
			h.add_child(M.label(_fmt(float(rd.get("time_ms", 0)) / 1000.0), M.f_bold, 16.0, Color("#fff4dc")))
			list.add_child(card)
	v.add_child(list)
	var foot: HBoxContainer = M.hbox(10)
	if name_ != "":
		foot.add_child(M.label("You race as " + name_ + ".", M.f_med, 14.0, Color("#c2a58c")))
	else:
		foot.add_child(M.label("Pick a username to put your times here.", M.f_med, 14.0, Color("#c2a58c")))
		var pb: Button = M.button("Pick a username", "ghost", 14.0, Vector4(12, 8, 12, 8))
		pb.pressed.connect(func(): open_name("lb"))
		foot.add_child(pb)
	v.add_child(foot)
	return v


static func _fmt(t: float) -> String:
	var m := int(t / 60.0)
	return "%d:%05.2f" % [m, t - m * 60.0]


# ---------------------------------------------------------------- the username sheet

func open_name(back := "") -> void:
	name_back = back
	main.menu.show_modal("lbname")


func _close_name() -> void:
	if name_back != "":
		main.menu.show_modal(name_back)
	else:
		main.menu.close_modal()


func name_panel() -> Control:
	var M = main.menu
	var v: VBoxContainer = M.vbox(12)
	v.add_child(M.para("Your name on the world leaderboards and in online rooms. 3 to 16 letters, numbers, spaces, _ . or -.", 15.0, Color("#c2a58c"), 520.0))
	var ed := LineEdit.new()
	ed.text = name_
	ed.max_length = 16
	ed.placeholder_text = "Username"
	ed.add_theme_font_override("font", M.f_semi)
	ed.add_theme_font_size_override("font_size", M.zi(18))
	ed.custom_minimum_size = Vector2(M.z(420), M.z(44))
	v.add_child(ed)
	var msg: Label = M.label("", M.f_med, 14.0, Color("#c2a58c"))
	v.add_child(msg)
	var say := func(t: String, c: String):
		msg.text = t
		msg.add_theme_color_override("font_color", Color("#8be08b") if c == "ok" else (Color("#ff8a7a") if c == "bad" else Color("#c2a58c")))
	var re := RegEx.new()
	re.compile("^[A-Za-z0-9_ .-]{3,16}$")
	ed.text_changed.connect(func(t: String):
		var nm := t.strip_edges()
		_name_seq += 1
		var my := _name_seq
		if nm == "":
			say.call("", "")
			return
		if re.search(nm) == null:
			say.call("3 to 16 letters, numbers, spaces, _ . or -", "bad")
			return
		if nm.to_lower() == name_.to_lower():
			say.call("That is your name now", "ok")
			return
		say.call("Checking...", "")
		await get_tree().create_timer(0.35).timeout
		if my != _name_seq:
			return
		var res: Array = await rpc_call("name_free", {"p_name": nm})
		if my != _name_seq or not is_instance_valid(msg):
			return
		if not res[0]:
			say.call("Cannot reach the leaderboard right now", "bad")
		elif res[1] == true:
			say.call("Available", "ok")
		else:
			say.call("Taken: try another", "bad"))
	var row: HBoxContainer = M.hbox(10)
	var later: Button = M.button("Not now", "ghost", 15.0, Vector4(16, 10, 16, 10))
	later.pressed.connect(_close_name)
	row.add_child(later)
	var ok: Button = M.button("Save", "cta", 15.0, Vector4(22, 10, 22, 10))
	ok.pressed.connect(func():
		var nm := ed.text.strip_edges()
		if re.search(nm) == null:
			say.call("3 to 16 letters, numbers, spaces, _ . or -", "bad")
			return
		say.call("Saving...", "")
		var res: Array = await rpc_call("claim_name", {"p_token": token, "p_name": nm})
		if not is_instance_valid(msg):
			return
		if res[0]:
			name_ = String(res[1]) if res[1] is String and String(res[1]) != "" else nm
			_save()
			say.call("Saved", "ok")
			flush()
			await get_tree().create_timer(0.5).timeout
			_close_name()
		else:
			say.call("Taken: try another" if String(res[2]).find("taken") >= 0 else "Cannot reach the leaderboard right now. Try again later.", "bad"))
	row.add_child(ok)
	v.add_child(row)
	# the same username on another device
	v.add_child(M.section_label("Already have a username on another device?"))
	v.add_child(M.para("Paste its account code (Settings > More > Username > Account code there):", 13.0, Color("#c2a58c"), 520.0))
	var crow: HBoxContainer = M.hbox(10)
	var ced := LineEdit.new()
	ced.custom_minimum_size = Vector2(M.z(360), M.z(40))
	ced.add_theme_font_size_override("font_size", M.zi(14))
	crow.add_child(ced)
	var cb: Button = M.button("Use this code", "ghost", 14.0, Vector4(12, 8, 12, 8))
	cb.pressed.connect(func():
		var c := ced.text.strip_edges().to_lower()
		var hx := RegEx.new()
		hx.compile("^[0-9a-f]{32,64}$")
		if hx.search(c) == null:
			say.call("That is not an account code", "bad")
			return
		var res: Array = await rpc_call("whoami", {"p_token": c})
		if not is_instance_valid(msg):
			return
		if not res[0]:
			say.call("Cannot reach the leaderboard right now", "bad")
		elif not (res[1] is String) or String(res[1]) == "":
			say.call("No username has that code", "bad")
		else:
			token = c
			name_ = String(res[1])
			_save()
			ed.text = name_
			say.call("Welcome back, " + name_, "ok")
			flush())
	crow.add_child(cb)
	v.add_child(crow)
	return v
