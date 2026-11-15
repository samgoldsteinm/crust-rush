extends Control
## Sandbox's world map and fast travel (web tools/mini/sandbox.js: sbMap, sbMapDraw, sbMapPins, sbMapPick, SB_WORLD,
## SB_SPOT, SB_LAND). Opened while driving with M or Select, or with Map under Resume in the pause menu.
## The picture: the house from above as it really is (where each of its four places sits, in metres, the garden wall
## along y = 0), and below and beside it the twenty tracks of the wider world, each a round place with its own lap
## drawn in it, grouped in their five countries, with a line for every passage. Names are plain labels; the chequered
## pins are the fast-travel points, one at the start line of every place this copy of the game has. Picking a pin looks
## closely at that place (its lap, the blue arrow where you are, a purple ring at each of its tunnels) and offers the
## journey; going there is the same warp as a passage.
## It lives in main.gd's pause panel while it is open, so the game is stopped under it and the controller's cursor
## (scripts/pad_cursor.gd) reaches its buttons. Loaded by its path (no class name).

const M := 347.0     # web SB_M: units to the metre in the house
const WORLD := {     # web SB_WORLD: [name, box x0 x1 y0 y1, fill]
	"backyard": ["BACK GARDEN", [-13.9, 11.6, 0.0, 7.0], "#4d8a3c"],
	"kitchen": ["KITCHEN", [-9.0, -5.0, -4.8, 0.0], "#d9d3c6"],
	"bedroom": ["BEDROOM", [-2.0, 2.0, -4.8, 0.0], "#c9a877"],
	"garage": ["GARAGE", [5.5, 9.5, -4.8, 0.0], "#b9bbbd"]}
const WORLD_MORE := [["HALL", [-5.0, -2.0, -4.8, 0.0]], ["", [2.0, 5.5, -4.8, 0.0]]]
const SPOT := {"margherita": [7.5, -12.5], "basil": [16, -12.5], "oven": [7.5, -20.5], "spiral": [16, -20.5], "bay": [-1, -12.5], "lagoon": [-9.5, -12.5], "calzone": [-9.5, -20.5], "tour": [-1, -20.5],
	"mozz": [24.5, -12.5], "napoli": [33, -12.5], "moon": [33, -4.3], "peaks": [24.5, -4.3], "frosty": [24.5, -20.5], "burn": [33, -20.5], "glacier": [41.5, -20.5], "peak": [50, -20.5], "holo": [41.5, -12.5], "grid": [50, -12.5], "laser": [58.5, -12.5], "synth": [58.5, -20.5]}
const SPOT_R := 3.1
const SPOT_RAD := {"margherita": 1700, "bay": 1850, "peaks": 1750, "frosty": 1750, "basil": 1800, "lagoon": 1850, "mozz": 1800, "burn": 1800, "oven": 1900, "calzone": 1900, "napoli": 1850, "glacier": 1900,
	"spiral": 1900, "tour": 1950, "moon": 1900, "peak": 1950, "grid": 2778, "laser": 2840, "holo": 2660, "synth": 2850}   # each track's world radius (web MAPS[..].R), for a place this copy does not have
const NEON := ["grid", "laser", "holo", "synth"]
const LAND := [["Kitchen Country", "#3d3423", [[3.3, 20.2, -24.6, -8.4]], [11.75, -8.95]], ["The Bay", "#1f3d4a", [[-13.7, 3.2, -24.6, -8.4]], [-5.25, -8.95]], ["The Old Town", "#40332f", [[20.3, 37.2, -16.6, -0.2]], [28.75, -0.75]],
	["The Freezer Range", "#2b3f52", [[20.3, 54.2, -25.7, -16.7]], [37.25, -25.1]], ["The Neon District", "#141a33", [[37.3, 62.6, -16.6, -8.4], [54.3, 62.6, -25.7, -16.6]], [49.9, -8.95]]]
const LINKS := {"margherita": ["garage", "basil", "oven", "bay"], "basil": ["margherita", "mozz", "spiral"], "oven": ["margherita", "spiral"], "spiral": ["oven", "basil", "frosty"], "frosty": ["spiral", "burn"], "burn": ["frosty", "glacier"], "glacier": ["burn", "peak"], "peak": ["glacier", "synth"],
	"mozz": ["basil", "napoli"], "napoli": ["mozz", "moon", "holo"], "moon": ["napoli", "peaks"], "peaks": ["moon"], "calzone": ["tour", "lagoon"], "tour": ["calzone"], "lagoon": ["calzone", "bay"], "bay": ["lagoon", "margherita"],
	"synth": ["peak", "laser"], "holo": ["napoli", "grid"], "laser": ["synth", "grid"], "grid": ["holo", "laser"]}
## the house's own passages (web SB_REG[..].gates): [id, wall, place along it, to, the gate there, label, plain]
const HOUSE_GATES := {
	"bedroom": [["b_k", "W", -48.0, "kitchen", "k_b", "KITCHEN", false], ["b_g", "E", 22.0, "garage", "ga_b", "GARAGE", false]],
	"kitchen": [["k_g", "E", 118.0, "backyard", "g_k", "GARDEN", false], ["k_b", "E", -45.0, "bedroom", "b_k", "BEDROOM", false]],
	"garage": [["ga_b", "W", 132.0, "bedroom", "b_g", "BEDROOM", false], ["garage>margherita", "S", 0.0, "margherita", "margherita>garage", "MARGHERITA RING", true]],
	"backyard": [["g_k", "S", -3.4, "kitchen", "k_g", "KITCHEN", false]]}
const VIEW := [-14.8, 63.1, -26.3, 7.9]     # the whole map: x from, x to, y from, y to (web SBM.view)

var main: Node
var menu
var sb
var maps: Array
var here := ""
var kart: Kart
var zoom := ""                 # the place looked at closely ("" = the whole world)
var pick := ""
var canvas: Control
var pins: Array = []           # {id, b: Button, at: [x, y], name}
var say: Label
var b_go: Button
var b_no: Button
var b_me: Button
var _cards := {}               # id -> the place's card (kind, name, R, start, lap), for the places this copy has


func setup(main_: Node, menu_, sb_, maps_: Array, here_: String, kart_: Kart) -> void:
	main = main_
	menu = menu_
	sb = sb_
	maps = maps_
	here = here_
	kart = kart_
	for m in maps:
		if m.get("sb") is Dictionary and not bool(m.get("battle", false)):
			var c: Dictionary = (m["sb"] as Dictionary).duplicate()
			c["track"] = String(m.get("name", m["id"]))
			_cards[String(m["id"])] = c
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	var bg := ColorRect.new()
	bg.color = Color(0.05, 0.03, 0.02, 0.82)
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(bg)
	var cc := CenterContainer.new()
	cc.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(cc)
	var pnl: PanelContainer = menu.panel(menu.glass(18.0, Vector4(16, 14, 16, 14)))
	cc.add_child(pnl)
	var v: VBoxContainer = menu.vbox(8)
	pnl.add_child(v)
	var head: HBoxContainer = menu.hbox(12)
	head.add_child(menu.label("Map", menu.f_disp, 24.0, Color("#f7c948"), Color("#7d1d0e"), Vector2(0, 3)))
	var wh: Label = menu.label(String(sb.title), menu.f_bold, 14.0, Color("#c2a58c"))
	wh.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	head.add_child(wh)
	head.add_child(menu.label("M or Select: close", menu.f_semi, 12.0, Color("#c2a58c")))
	v.add_child(head)
	# the picture, in the map's own shape, as large as the window allows
	var vs := get_viewport_rect().size if is_inside_tree() else Vector2(1280, 720)
	if main != null:
		vs = main.get_viewport().get_visible_rect().size
	var asp := (float(VIEW[3]) - float(VIEW[2])) / (float(VIEW[1]) - float(VIEW[0]))
	var w := minf(vs.x * 0.92, vs.y * 0.66 / asp)
	canvas = Control.new()
	canvas.custom_minimum_size = Vector2(w, w * asp)
	canvas.clip_contents = true
	canvas.draw.connect(_draw_map)
	v.add_child(canvas)
	var row: HBoxContainer = menu.hbox(10)
	say = menu.label("", menu.f_bold, 14.0, Color("#fff4dc"))
	say.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	say.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	say.custom_minimum_size.x = w * 0.4
	row.add_child(say)
	b_me = menu.button("Where am I?", "ghost", 14.0, Vector4(12, 9, 12, 9))
	b_me.pressed.connect(func(): _pick(here))
	row.add_child(b_me)
	b_go = menu.button("Travel here", "cta", 17.0, Vector4(18, 10, 18, 10))
	b_go.pressed.connect(func():
		if pick != "":
			main._sb_map_travel(pick))
	row.add_child(b_go)
	b_no = menu.button("World map", "ghost", 14.0, Vector4(12, 9, 12, 9))
	b_no.pressed.connect(func(): _pick(""))
	row.add_child(b_no)
	var back: Button = menu.button("Back", "ghost", 14.0, Vector4(12, 9, 12, 9))
	back.pressed.connect(func(): main._sb_map(false))
	row.add_child(back)
	v.add_child(row)
	_make_pins()
	_pick("")
	var first: Button = null
	for q in pins:
		if String(q["id"]) == here:
			first = q["b"]
	if first == null and not pins.is_empty():
		first = pins[0]["b"]
	if first != null:
		first.grab_focus.call_deferred()


# ---------------------------------------------------------------- places on the map

## a spot of a place (the karts' own x and z there) on the map (web sbMapAt)
func at(id: String, x: float, z: float) -> Variant:
	match id:
		"backyard":
			return [x / M - 0.75, 3.5 - z / M]
		"kitchen":
			return [-7.0 + x / M, -2.4 - z / M]
		"bedroom":
			return [x / M, -2.4 - z / M]
		"garage":
			return [7.5 + x / M, -2.4 - z / M]
	if not SPOT.has(id):
		return null
	var c: Array = SPOT[id]
	var rad := float((_cards.get(id, {}) as Dictionary).get("R", SPOT_RAD.get(id, 1900)))
	var s := SPOT_R / maxf(1.0, rad)
	return [float(c[0]) + x * s, float(c[1]) - z * s]


## one of the house's passages on the map (web sbMapGate)
func house_gate(id: String, gid: String) -> Variant:
	if not HOUSE_GATES.has(id):
		return null
	var b: Array = WORLD[id][1]
	for d in HOUSE_GATES[id]:
		if String(d[0]) != gid:
			continue
		var p := float(d[2])
		if id != "backyard":
			var y := (float(b[2]) + float(b[3])) / 2.0 + p / 100.0
			var x := (float(b[0]) + float(b[1])) / 2.0 + p / 100.0
			match String(d[1]):
				"E":
					return [float(b[1]), y]
				"W":
					return [float(b[0]), y]
				"N":
					return [x, float(b[3])]
			return [x, float(b[2])]
		match String(d[1]):
			"S":
				return [p, float(b[2])]
			"N":
				return [p, float(b[3])]
			"E":
				return [float(b[1]), p]
		return [float(b[0]), p]
	return null


## a place's tunnels on the map: [x, y, where it leads]. The house's are known from its plan; a track's own are known
## while you are on it, and remembered from then on (the save's g); a place not yet visited has none (web sbMapGates)
func tunnels(id: String) -> Array:
	var o: Array = []
	if WORLD.has(id):
		for d in HOUSE_GATES.get(id, []):
			if _cards.has(String(d[3])):
				var a = house_gate(id, String(d[0]))
				if a != null:
					o.append([a[0], a[1], String(d[5])])
		return o
	var l: Array = []
	if id == here:
		for g in sb.gates:
			l.append([float(g["x"]), float(g["z"]), String(g["label"])])
	else:
		var sv: Dictionary = sb.load_save()
		l = (sv.get("g", {}) as Dictionary).get(id, [])
	for g2 in l:
		var a2 = at(id, float(g2[0]), float(g2[1]))
		if a2 != null:
			o.append([a2[0], a2[1], String(g2[2])])
	return o


## the window on one place: the whole of it with a margin, in the picture's own shape (web sbMapView)
func view_of(id: String) -> Array:
	var asp := (float(VIEW[3]) - float(VIEW[2])) / (float(VIEW[1]) - float(VIEW[0]))
	var cx: float
	var cy: float
	var w: float
	var h: float
	if WORLD.has(id):
		var b: Array = WORLD[id][1]
		cx = (float(b[0]) + float(b[1])) / 2.0
		cy = (float(b[2]) + float(b[3])) / 2.0
		w = float(b[1]) - float(b[0])
		h = float(b[3]) - float(b[2])
	else:
		cx = float(SPOT[id][0])
		cy = float(SPOT[id][1])
		w = SPOT_R * 2.0
		h = w
	var hh := maxf(h * 0.5 * 1.3, w * 0.5 * 1.3 * asp)
	return [cx - hh / asp, cx + hh / asp, cy - hh, cy + hh]


func _view() -> Array:
	return view_of(zoom) if zoom != "" else VIEW


# ---------------------------------------------------------------- pins and picking (web sbMapPins, sbMapPick)

func _make_pins() -> void:
	for id in WORLD.keys() + SPOT.keys():
		if not _cards.has(id):
			continue   # a place this copy of the game does not have: drawn, but nowhere to travel to
		var c: Dictionary = _cards[id]
		var st: Array = c.get("start", [0, 0])
		var a = at(id, float(st[0]), float(st[1]))
		if a == null:
			continue
		var b := Button.new()
		b.flat = true
		b.focus_mode = Control.FOCUS_ALL
		b.mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
		b.custom_minimum_size = Vector2(30, 30)
		b.size = Vector2(30, 30)
		b.tooltip_text = "Travel to " + String(c["track"])
		for sn in ["normal", "hover", "pressed", "focus", "disabled"]:
			b.add_theme_stylebox_override(sn, StyleBoxEmpty.new())
		var pid: String = id
		b.draw.connect(func(): _draw_pin(b, pid, String(c["track"])))
		b.pressed.connect(func(): _pick("" if zoom == pid else pid))
		b.focus_entered.connect(b.queue_redraw)
		b.focus_exited.connect(b.queue_redraw)
		b.mouse_entered.connect(b.queue_redraw)
		b.mouse_exited.connect(b.queue_redraw)
		canvas.add_child(b)
		pins.append({"id": id, "b": b, "at": a, "name": String(c["track"])})
	# the mechanic's shop (web v200): a pin of its own in the garage
	if _cards.has("garage"):
		var sa = at("garage", 205.0, -443.0)
		if sa != null:
			var sbn := Button.new()
			sbn.flat = true
			sbn.focus_mode = Control.FOCUS_ALL
			sbn.custom_minimum_size = Vector2(30, 30)
			sbn.size = Vector2(30, 30)
			sbn.tooltip_text = "Travel to the mechanic's shop"
			for sn in ["normal", "hover", "pressed", "focus", "disabled"]:
				sbn.add_theme_stylebox_override(sn, StyleBoxEmpty.new())
			sbn.draw.connect(func(): _draw_pin(sbn, "shop", "Mechanic"))
			sbn.pressed.connect(func(): _pick("shop"))
			sbn.focus_entered.connect(sbn.queue_redraw)
			sbn.focus_exited.connect(sbn.queue_redraw)
			canvas.add_child(sbn)
			pins.append({"id": "shop", "b": sbn, "at": sa, "name": "Mechanic"})


func _draw_pin(b: Button, id: String, nm: String) -> void:
	var c := b.size / 2.0
	var r := 12.0
	if id == "shop":
		# the mechanic's shop: a blue disc with a cream rim (a place to go, not a track)
		b.draw_circle(c, r, Color("#2a5bd7"))
		b.draw_arc(c, r + 1.5, 0.0, TAU, 40, Color("#fff4dc"), 3.0, true)
		b.draw_line(c + Vector2(-5, 5), c + Vector2(5, -5), Color.WHITE, 3.0, true)
		b.draw_circle(c + Vector2(5, -5), 3.0, Color.WHITE)
		if id == pick or b.has_focus() or b.is_hovered():
			b.draw_arc(c, r + 6.0, 0.0, TAU, 40, Color("#39d0ff"), 3.0, true)
		var f0: Font = menu.f_bold
		var tw0 := f0.get_string_size(nm, HORIZONTAL_ALIGNMENT_LEFT, -1, 11).x
		b.draw_string_outline(f0, Vector2(c.x - tw0 / 2.0, b.size.y + 13.0), nm, HORIZONTAL_ALIGNMENT_LEFT, -1, 11, 4, Color(0, 0, 0, 0.85))
		b.draw_string(f0, Vector2(c.x - tw0 / 2.0, b.size.y + 13.0), nm, HORIZONTAL_ALIGNMENT_LEFT, -1, 11, Color.WHITE)
		return
	# a chequered disc with a gold rim; a blue ring when it is the one picked, pointed at or focused
	b.draw_circle(c, r, Color("#fbf6ea"))
	for i in range(-2, 2):
		for j in range(-2, 2):
			var p := c + Vector2(float(i) * 6.0, float(j) * 6.0)
			if posmod(i + j, 2) == 0 and (p + Vector2(3.0, 3.0) - c).length() < r - 2.5:
				b.draw_rect(Rect2(p, Vector2(6.0, 6.0)), Color("#141210"))
	b.draw_arc(c, r + 1.5, 0.0, TAU, 40, Color("#ffd45a"), 3.0, true)
	if id == pick or b.has_focus() or b.is_hovered():
		b.draw_arc(c, r + 6.0, 0.0, TAU, 40, Color("#39d0ff"), 3.0, true)
	var f: Font = menu.f_bold
	var tw := f.get_string_size(nm, HORIZONTAL_ALIGNMENT_LEFT, -1, 11).x
	var ty := -6.0 if id == "backyard" else b.size.y + 13.0
	b.draw_string_outline(f, Vector2(c.x - tw / 2.0, ty), nm, HORIZONTAL_ALIGNMENT_LEFT, -1, 11, 4, Color(0, 0, 0, 0.85))
	b.draw_string(f, Vector2(c.x - tw / 2.0, ty), nm, HORIZONTAL_ALIGNMENT_LEFT, -1, 11, Color.WHITE)


func _pick(id: String) -> void:
	pick = id
	zoom = id
	if id == "shop":
		zoom = "garage"
		say.text = "Mechanic's shop, in the garage: drive in to change your driver and kart"
		b_go.visible = true
		b_no.visible = true
		b_me.visible = true
		b_go.text = "Travel here"
		b_go.grab_focus.call_deferred()
		_place_pins()
		canvas.queue_redraw()
		return
	if id != "":
		var c: Dictionary = _cards.get(id, {})
		var is_here := id == here
		var n := tunnels(id).size()
		say.text = String(c.get("track", id)) + " · " + String(c.get("name", "")).split(" · ")[0] + (" · you are here (the blue arrow)" if is_here else "") \
			+ (" · the purple rings are its tunnels" if n > 0 else " · its tunnels show once you have been there")
		b_go.visible = true
		b_no.visible = true
		b_me.visible = not is_here
		b_go.text = "To the start line" if is_here else "Travel here"
		b_go.grab_focus.call_deferred()
	else:
		say.text = "Pick a chequered pin to look closer at a place and travel to it. Every place can also be driven to."
		b_go.visible = false
		b_no.visible = false
		b_me.visible = _cards.has(here)
	_place_pins()
	canvas.queue_redraw()


func _place_pins() -> void:
	var V := _view()
	var s := canvas.custom_minimum_size.x / (float(V[1]) - float(V[0]))
	for q in pins:
		var b: Button = q["b"]
		b.position = Vector2((float(q["at"][0]) - float(V[0])) * s, (float(V[3]) - float(q["at"][1])) * s) - b.size / 2.0
		b.visible = zoom == "" or String(q["id"]) == zoom or (String(q["id"]) == "shop" and zoom == "garage")
		b.queue_redraw()


# ---------------------------------------------------------------- the picture (web sbMapDraw)

func _draw_map() -> void:
	var cv := canvas
	var V := _view()
	var W := cv.custom_minimum_size.x
	var s := W / (float(V[1]) - float(V[0]))
	var X := func(x: float) -> float: return (x - float(V[0])) * s
	var Y := func(y: float) -> float: return (float(V[3]) - y) * s
	var rect := func(b: Array, fill, stroke = null, lw := 2.0) -> void:
		var r := Rect2(X.call(float(b[0])), Y.call(float(b[3])), (float(b[1]) - float(b[0])) * s, (float(b[3]) - float(b[2])) * s)
		if fill != null:
			cv.draw_rect(r, Color(String(fill)))
		if stroke != null:
			cv.draw_rect(r, Color(String(stroke)), false, lw)
	var f: Font = menu.f_bold
	var text := func(t: String, x: float, y: float, px: int, col: Color) -> void:
		var tw := f.get_string_size(t, HORIZONTAL_ALIGNMENT_LEFT, -1, px).x
		cv.draw_string(f, Vector2(x - tw / 2.0, y + px * 0.35), t, HORIZONTAL_ALIGNMENT_LEFT, -1, px, col)
	cv.draw_rect(Rect2(Vector2.ZERO, cv.size), Color("#22301f"))
	# the countries
	for l in LAND:
		for b in l[2]:
			rect.call(b, l[1])
		text.call(String(l[0]).to_upper(), X.call(float(l[3][0])), Y.call(float(l[3][1])), 12, Color(1, 1, 1, 0.55))
	# the house: the garden with its patio, the ground the rooms stand on, the rooms, the street in front
	rect.call(WORLD["backyard"][1], WORLD["backyard"][2])
	rect.call([-13.9, 11.6, 0.0, 1.6], "#cfc6b3")
	rect.call(WORLD["backyard"][1], null, "#6b4f33", 3.0)
	rect.call([-9.2, 9.7, -5.0, 0.0], "#8f6f5a")
	for m in WORLD_MORE:
		rect.call(m[1], "#b8ad9c", "#5b4636", 1.5)
	for id in ["kitchen", "bedroom", "garage"]:
		rect.call(WORLD[id][1], WORLD[id][2], "#5b4636", 2.0)
	rect.call([-14.6, 12.3, -6.3, -5.0], "#55585c")
	text.call("FRONT STREET", X.call(-4.0), Y.call(-5.65), 10, Color(1, 1, 1, 0.6))
	# the passages between the tracks, and the garage's door to Margherita Ring
	var seen := {}
	for a in LINKS:
		for b2 in LINKS[a]:
			var key: String = (a + "|" + b2) if a < b2 else (b2 + "|" + a)
			if seen.has(key):
				continue
			seen[key] = true
			var p = [7.5, -4.8] if b2 == "garage" else SPOT.get(b2)
			var q = SPOT.get(a)
			if p == null or q == null:
				continue
			cv.draw_dashed_line(Vector2(X.call(float(q[0])), Y.call(float(q[1]))), Vector2(X.call(float(p[0])), Y.call(float(p[1]))), Color(0.96, 0.93, 0.83, 0.75), 2.5, 6.0, true)
	for id in WORLD:
		for d in HOUSE_GATES.get(id, []):
			if bool(d[6]):
				continue
			var ga = house_gate(id, String(d[0]))
			if ga == null:
				continue
			if id < String(d[3]):
				var gb = house_gate(String(d[3]), String(d[4]))
				if gb != null:
					cv.draw_dashed_line(Vector2(X.call(ga[0]), Y.call(ga[1])), Vector2(X.call(gb[0]), Y.call(gb[1])), Color(0.08, 0.05, 0.03, 0.8), 2.0, 6.0, true)
	for id in WORLD:
		for d in HOUSE_GATES.get(id, []):
			if bool(d[6]):
				continue
			var ga2 = house_gate(id, String(d[0]))
			if ga2 != null:
				var c0 := Vector2(X.call(ga2[0]), Y.call(ga2[1]))
				cv.draw_circle(c0, 4.5, Color("#140c08"))
				cv.draw_arc(c0, 4.5, 0.0, TAU, 24, Color("#f3ead6"), 1.5, true)
	# the round places
	for id in SPOT:
		var c: Array = SPOT[id]
		var neon: bool = id in NEON
		var cc := Vector2(X.call(float(c[0])), Y.call(float(c[1])))
		cv.draw_circle(cc, SPOT_R * s, Color("#0b1020") if neon else (Color("#b3402a") if id == "spiral" else Color("#f0cf78")))
		cv.draw_arc(cc, SPOT_R * s, 0.0, TAU, 64, Color("#39d0ff") if neon else Color("#b9773a"), 2.0 if neon else 4.0, true)
		if not _cards.has(id):
			# (a place this copy of the game does not have: its name where its lap would be)
			text.call(id.to_upper(), cc.x, cc.y, 10, Color(1, 1, 1, 0.5) if neon else Color(0.2, 0.12, 0.06, 0.6))
	# the tracks: each place's own lap
	for id in WORLD.keys() + SPOT.keys():
		if not _cards.has(id):
			continue
		var lap: Array = (_cards[id] as Dictionary).get("lap", [])
		if lap.size() < 3:
			continue
		var pts := PackedVector2Array()
		for q2 in lap:
			var a3 = at(id, float(q2[0]), float(q2[1]))
			pts.append(Vector2(X.call(a3[0]), Y.call(a3[1])))
		pts.append(pts[0])
		var neon2: bool = id in NEON
		var toy: bool = WORLD.has(id)
		var cols: Array = [["#7a2a05", 0.36], ["#ff7a1e", 0.26]] if toy else ([["#0d3f55", 0.5], ["#59e0ff", 0.3]] if neon2 else [["#4a3423", 0.52], ["#8a8f96", 0.34]])
		for cw in cols:
			cv.draw_polyline(pts, Color(String(cw[0])), maxf(2.0, float(cw[1]) * s), true)
	# names: plain, never a button
	for id in WORLD:
		var b3: Array = WORLD[id][1]
		var yard: bool = id == "backyard"
		text.call(String(WORLD[id][0]), X.call((float(b3[0]) + float(b3[1])) / 2.0), Y.call(float(b3[3]) - 0.55 if yard else float(b3[2]) + 0.45), 14 if yard else 11, Color(1, 1, 1, 0.92) if yard else Color(0.12, 0.07, 0.04, 0.9))
	for m2 in WORLD_MORE:
		if String(m2[0]) != "":
			text.call(String(m2[0]), X.call((float(m2[1][0]) + float(m2[1][1])) / 2.0), Y.call((float(m2[1][2]) + float(m2[1][3])) / 2.0), 9, Color(0.12, 0.07, 0.04, 0.6))
	# the tunnels of the places whose tunnels are known: a purple ring; looked at closely, with where each leads
	for id in WORLD.keys() + SPOT.keys():
		if zoom != "" and id != zoom:
			continue
		for t in tunnels(id):
			var tc := Vector2(X.call(float(t[0])), Y.call(float(t[1])))
			var r := 9.0 if zoom != "" else 4.0
			cv.draw_circle(tc, r, Color("#1a0f33"))
			cv.draw_arc(tc, r, 0.0, TAU, 32, Color("#b58cff"), 4.0 if zoom != "" else 2.0, true)
			cv.draw_circle(tc, r * 0.35, Color.WHITE)
			if zoom != "":
				var tx := "TUNNEL TO " + String(t[2])
				var tw2 := f.get_string_size(tx, HORIZONTAL_ALIGNMENT_LEFT, -1, 12).x + 12.0
				var lx := clampf(tc.x, tw2 / 2.0 + 4.0, W - tw2 / 2.0 - 4.0)
				var ly := tc.y - r - 13.0 if tc.y > cv.size.y * 0.5 else tc.y + r + 13.0
				cv.draw_rect(Rect2(lx - tw2 / 2.0, ly - 10.0, tw2, 20.0), Color(0.08, 0.04, 0.16, 0.88))
				cv.draw_rect(Rect2(lx - tw2 / 2.0, ly - 10.0, tw2, 20.0), Color("#b58cff"), false, 1.5)
				text.call(tx, lx, ly, 12, Color("#f1e8ff"))
	# you: an arrow where you are, pointing the way you face
	if kart != null:
		var me = at(here, kart.x, kart.y)
		if me != null:
			var r2 := 14.0 if zoom != "" else 9.0
			var o := Vector2(X.call(me[0]), Y.call(me[1]))
			var rot := Transform2D(kart.ma, o)
			var shape := PackedVector2Array([rot * Vector2(r2 * 1.25, 0), rot * Vector2(-r2 * 0.8, r2 * 0.8), rot * Vector2(-r2 * 0.35, 0), rot * Vector2(-r2 * 0.8, -r2 * 0.8)])
			cv.draw_colored_polygon(shape, Color("#39d0ff"))
			shape.append(shape[0])
			cv.draw_polyline(shape, Color("#06222e"), 2.0, true)
