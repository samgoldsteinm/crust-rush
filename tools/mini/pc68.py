"""The PC side of web patches 64, 65 (coins) and 68 (developer options), online version 120.
    py.cmd tools/mini/pc68.py      (once; edits D:/crust-rush/godot/scripts)
- web patch 64: race.itm_used, set when the player uses an item (race.use_item) or takes one into hold (hold_item); the leaderboard's
  "no items" is race.noitm or not race.itm_used. (On the PC the specials fire their pepperoni etc. directly, never through use_item.)
- web patch 65's coins for a race: main._race_pay at the player's finish (the Sandbox save's coins), "+N coins" under the results.
- web patch 68: the developer options. race.dev (the race settings in force: off line yours, in a room the host's cfg "dev"), race.dev_all
  (in a room: every kart), race.dev_local (this device, off line only). Applied exactly as the web: k.sm_* (spd/acc/hnd/wgt x, off +),
  the drift tier boost x, the fall (260) x, ability charge x / always ready, rival skill x, the moving hazards (traffic, train, walk)
  left out of _setup_haz; on this device fly (kart._dev_fly; G / the left stick press; I, K, Page Up/Down, the stick up/down), invincible
  (spin_out), always this item (roll_item), unlimited pepperoni, game speed (Engine.time_scale), field of view, the HUD. The DEVELOPER
  cheat code and Settings > More's Developer rows; user://dev.json. webnet: PROTO 120 and cfg "dev" from the host.
"""
G = 'D:/crust-rush/godot/scripts/'
# the style shop's catalogue (web patch 65 TRIMS, GLOWS, LIGHTS, SMOKES: keep the same order, a build stores indices) and what is owned
STYLE_GD = """## (load it by path: preload("res://scripts/style.gd"); a new class_name is not known until the editor rebuilds its cache)
## The style shop (web patch 65): one colour list for trim, accent and interior; underglow; headlight colours; tyre smoke.
## Each {n, h (null = stock, "rainbow" cycles), p price (0 free), m metallic, r roughness}. KEEP the web's order: a build's "st" holds
## indices and travels online. Owned ones in user://own.json as the web's ids ("tr5", "gl3"...); the purse is the Sandbox save's coins.
const TRIMS := [{"n": "Stock", "h": null, "p": 0}, {"n": "Black", "h": "#111214", "p": 0}, {"n": "White", "h": "#f2f2f0", "p": 0}, {"n": "Silver", "h": "#b8bcc4", "p": 0, "m": 1},
	{"n": "Red", "h": "#c40c0c", "p": 60}, {"n": "Orange", "h": "#ff5a00", "p": 60}, {"n": "Yellow", "h": "#ffc400", "p": 60}, {"n": "Green", "h": "#2fae0c", "p": 60},
	{"n": "Blue", "h": "#0b49c9", "p": 60}, {"n": "Purple", "h": "#5317ad", "p": 80}, {"n": "Pink", "h": "#ff2c84", "p": 80}, {"n": "Tan leather", "h": "#a8703e", "p": 120},
	{"n": "Neon green", "h": "#7dff2a", "p": 150}, {"n": "Neon blue", "h": "#2ae8ff", "p": 150}, {"n": "Gunmetal", "h": "#3b3e44", "p": 150, "m": 1},
	{"n": "Bronze", "h": "#8a6232", "p": 250, "m": 1}, {"n": "Gold", "h": "#d4a838", "p": 400, "m": 1}, {"n": "Chrome", "h": "#e9e9ee", "p": 600, "m": 1, "r": 0.08}]
const GLOWS := [{"n": "Off", "h": null, "p": 0}, {"n": "Ice blue", "h": "#3fc8ff", "p": 0}, {"n": "Purple", "h": "#a040ff", "p": 200}, {"n": "Red", "h": "#ff2a2a", "p": 200},
	{"n": "Green", "h": "#3dff6a", "p": 200}, {"n": "Pink", "h": "#ff3fb4", "p": 250}, {"n": "Amber", "h": "#ffa020", "p": 250}, {"n": "White", "h": "#e8f0ff", "p": 250}, {"n": "Rainbow", "h": "rainbow", "p": 800}]
const LIGHTS := [{"n": "Halogen", "h": "#fff2d6", "p": 0}, {"n": "Xenon white", "h": "#eef3ff", "p": 0}, {"n": "Ice blue", "h": "#9fd8ff", "p": 150}, {"n": "Yellow", "h": "#ffd75a", "p": 150},
	{"n": "Purple", "h": "#c49bff", "p": 300}, {"n": "Green", "h": "#9dffb0", "p": 300}, {"n": "Red", "h": "#ff7a6a", "p": 300}]
const SMOKES := [{"n": "White", "h": "#f2ebe0", "p": 0}, {"n": "Black", "h": "#2a2a2e", "p": 300}, {"n": "Blue", "h": "#2a6cff", "p": 350}, {"n": "Red", "h": "#ff3020", "p": 350},
	{"n": "Purple", "h": "#9a40ff", "p": 350}, {"n": "Green", "h": "#3ad84a", "p": 350}, {"n": "Yellow", "h": "#ffd22a", "p": 350}, {"n": "Pink", "h": "#ff4fb8", "p": 400}, {"n": "Rainbow", "h": "rainbow", "p": 900}]
## slot -> [id prefix, list] (trim, accent and interior share one list: buying a colour unlocks it for all three)
const SLOTS := {"tr": ["tr", TRIMS], "ac": ["tr", TRIMS], "in": ["tr", TRIMS], "gl": ["gl", GLOWS], "hl": ["hl", LIGHTS], "sm": ["sm", SMOKES]}
const PATH := "user://own.json"
const Sandbox := preload("res://scripts/sandbox.gd")   # (by its file: a fresh checkout has no class list)


static func owned() -> Dictionary:
	var o := {}
	if FileAccess.file_exists(PATH):
		var j = JSON.parse_string(FileAccess.get_file_as_string(PATH))
		if j is Array:
			for x in j:
				o[String(x)] = true
	return o


static func _put(o: Dictionary) -> void:
	var f := FileAccess.open(PATH, FileAccess.WRITE)
	if f:
		f.store_string(JSON.stringify(o.keys()))


static func is_owned(slot: String, i: int) -> bool:
	var L: Array = SLOTS[slot][1]
	if i < 0 or i >= L.size() or int(L[i]["p"]) == 0:
		return true
	return owned().has(String(SLOTS[slot][0]) + str(i))


## web styleBuy: false when the purse is short
static func buy(slot: String, i: int) -> bool:
	if is_owned(slot, i):
		return true
	var it: Dictionary = SLOTS[slot][1][i]
	var sv: Dictionary = Sandbox.load_save()
	if int(sv.get("c", 0)) < int(it["p"]):
		return false
	sv["c"] = int(sv["c"]) - int(it["p"])
	Sandbox.keep()
	var o := owned()
	o[String(SLOTS[slot][0]) + str(i)] = true
	_put(o)
	return true


static func own_all() -> void:
	var o := owned()
	for slot in ["tr", "gl", "hl", "sm"]:
		for i in (SLOTS[slot][1] as Array).size():
			o[String(SLOTS[slot][0]) + str(i)] = true
	_put(o)


## a build's style entry (0 = stock / off / the first)
static func pick(build: Dictionary, slot: String) -> Dictionary:
	var st = build.get("st")
	var i := int((st as Dictionary).get(slot, 0)) if st is Dictionary else 0
	var L: Array = SLOTS[slot][1]
	return L[clampi(i, 0, L.size() - 1)]
"""


def rep(f, a, b, n=1):
    p = G + f
    s = open(p, encoding='utf-8', newline='').read()
    assert s.count(a) == n, (f, s.count(a), a[:80])
    s = s.replace(a, b)
    open(p, 'w', encoding='utf-8', newline='').write(s)


# ---------------------------------------------------------------- webnet
rep('webnet.gd', "const PROTO := 119   # (", "const PROTO := 120   # (120: web v219 patch 68, the host's developer options in cfg \"dev\"; ")
rep('webnet.gd', '"karts": ks, "ni": main.all_items_off()}', '"karts": ks, "ni": main.all_items_off(), "dev": main.dev_pack()}')

# ---------------------------------------------------------------- race
rep('race.gd', "var noitm := false", """var itm_used := false       # the player used an item this race (web patch 64: a race without one counts as No items)
var dev := {}                # the developer options' race settings in force (web patch 68): off line yours, in a room the host's cfg "dev"
var dev_all := false         # in a room they apply to every kart; off line only to yours
var dev_local := {}          # this device's own (off line only): fly, invincible, always this item, unlimited pepperoni
var noitm := false""")
rep('race.gd', """	k.ai = {"lane": lat, "lane_target": lat, "lane_t": 1.0 + rng.randf() * 3.0, "skill": sk, "item_delay": 0.0, "in_bend": false, "auto": not is_player}
	return k""", """	k.ai = {"lane": lat, "lane_target": lat, "lane_t": 1.0 + rng.randf() * 3.0, "skill": sk, "item_delay": 0.0, "in_bend": false, "auto": not is_player}
	dev_kart(k)
	if not dev.is_empty() and not is_player:
		k.ai["skill"] = float(k.ai["skill"]) * float(dev.get("cpu", 1.0))
	return k


## web devFor / devKart (patch 68): a kart's race settings (in a room every kart's, off line only yours)
func dev_for(k: Kart) -> Dictionary:
	return dev if not dev.is_empty() and (dev_all or k.is_player) else {}


func dev_mul(k: Kart, key: String) -> float:
	var D := dev_for(k)
	return float(D.get(key, 1.0)) if not D.is_empty() else 1.0


func dev_kart(k: Kart) -> void:
	var D := dev_for(k)
	if D.is_empty():
		return
	k.sm_spd *= float(D.get("spd", 1.0))
	k.sm_acc *= float(D.get("acc", 1.0))
	k.sm_hnd *= float(D.get("hnd", 1.0))
	k.sm_wgt *= float(D.get("wgt", 1.0))
	k.sm_off += float(D.get("off", 0.0))


func _dev_ab(k: Kart) -> float:
	var D := dev_for(k)
	if D.is_empty():
		return 1.0
	return 1e6 if int(D.get("abilReady", 0)) == 1 else float(D.get("abil", 1.0))""")
rep('race.gd', "			k.ab_c = minf(1.0, k.ab_c + dt / ABIL_TIME)", "			k.ab_c = minf(1.0, k.ab_c + dt / ABIL_TIME * _dev_ab(k))")
rep('race.gd', "func roll_item(pos: int) -> String:\n", "func roll_item(pos: int) -> String:\n\tif String(dev_local.get(\"item\", \"\")) != \"\":\n\t\treturn String(dev_local[\"item\"])   # (web patch 68: always this item)\n")
rep('race.gd', """func use_item(k: Kart, back_in: bool) -> void:
	var it := k.item
	if it == "":
		return""", """func use_item(k: Kart, back_in: bool) -> void:
	var it := k.item
	if it == "":
		return
	if k.is_player:
		itm_used = true   # (web patch 64)""")
rep('race.gd', '	k.held = {"it": it, "sl": sl, "t": 0.0}', '	k.held = {"it": it, "sl": sl, "t": 0.0}\n\tif k.is_player:\n\t\titm_used = true   # (web patch 64: holding one is using it)')
rep('race.gd', """func _setup_haz() -> void:
	traffic.clear()
	for c in T.haz.get("traffic", []):""", """func _setup_haz() -> void:
	# (web patch 68: a moving hazard switched off in the developer options is never built)
	var hz: Dictionary = dev.get("hz", {}) if dev.get("hz") is Dictionary else {}
	traffic.clear()
	for c in (T.haz.get("traffic", []) if int(hz.get("traffic", 1)) != 0 else []):""")
rep('race.gd', '	for w in T.haz.get("walk", []):', '	for w in (T.haz.get("walk", []) if int(hz.get("walk", 1)) != 0 else []):')
rep('race.gd', '	var tr = T.haz.get("train")', '	var tr = T.haz.get("train") if int(hz.get("train", 1)) != 0 else null')
rep('race.gd', "func spin_out(k: Kart, kind: String, world := false, force := false) -> bool:\n",
    "func spin_out(k: Kart, kind: String, world := false, force := false) -> bool:\n\tif k.is_player and int(dev_local.get(\"inv\", 0)) == 1:\n\t\treturn false   # (web patch 68: invincible)\n")

# ---------------------------------------------------------------- kart
rep('kart.gd', "				boost = maxf(boost, _drift_boost(tr))", "				boost = maxf(boost, _drift_boost(tr) * (race.dev_mul(self, \"drift\") if race != null else 1.0))")
rep('kart.gd', "			wvy -= ((80.0 if wvy > 0.0 else 110.0) if big else 260.0) * dt", "			wvy -= ((80.0 if wvy > 0.0 else 110.0) if big else 260.0) * dt * (race.dev_mul(self, \"grav\") if race != null else 1.0)")
rep('kart.gd', "var spin := 0.0", "var spin := 0.0\nvar fly := false          # flying (web patch 68, the developer options: devFly)")
rep('kart.gd', """func step(inp: Dictionary, dt: float) -> void:
	_save_prev()""", """func step(inp: Dictionary, dt: float) -> void:
	_save_prev()
	if fly and race != null and int(race.dev_local.get("fly", 0)) == 1:
		_dev_fly(inp, dt)
		return""")
rep('kart.gd', "static func _drift_boost(t: int) -> float:", """## web devFly (patch 68): no road, no walls; the throttle flies forward, the brake backs off, "flyup" climbs (-1..1); never below the ground
func _dev_fly(inp: Dictionary, dt: float) -> void:
	air = true
	loop = {}
	drift = 0
	spin = 0.0
	charge = 0.0
	var thr := -0.45 if bool(inp["brake"]) else (1.0 if float(inp.get("mul", 1.0)) > 0.0 else 0.0)
	speed += (thr * 300.0 - speed) * minf(1.0, dt * 1.5)
	steer = float(inp["steer"])
	a += steer * 2.1 * dt
	ma = a
	var up := clampf(float(inp.get("flyup", 0.0)), -1.0, 1.0)
	wvy += (up * 150.0 - wvy) * minf(1.0, dt * 4.0)
	x += cos(a) * speed * dt
	y += sin(a) * speed * dt
	wy += wvy * dt
	var g := T.ground(x, y)
	if wy < g + 1.0:
		wy = g + 1.0
		if wvy < 0.0:
			wvy = 0.0
	z = 0.0


static func _drift_boost(t: int) -> float:""")

# ---------------------------------------------------------------- keys
rep('keys.gd', '["lights", "Headlights (Sandbox)"]]', '["lights", "Headlights (Sandbox)"], ["fly", "Fly (developer)"], ["flyup", "Fly up (developer)"], ["flydown", "Fly down (developer)"]]')
rep('keys.gd', '"sbback": [KEY_T], "lights": [KEY_L]}', '"sbback": [KEY_T], "lights": [KEY_L], "fly": [KEY_G], "flyup": [KEY_I, KEY_PAGEUP], "flydown": [KEY_K, KEY_PAGEDOWN]}')

# ---------------------------------------------------------------- main: the state, the race start, coins, the cheat, settings, each frame
rep('main.gd', "var hl_mode = null", """# ---- the developer options (web patch 68): DEVELOPER unlocks them; user://dev.json
const DEV_DEF := {"on": 1, "spd": 1.0, "acc": 1.0, "hnd": 1.0, "wgt": 1.0, "off": 0.0, "drift": 1.0, "grav": 1.0, "abil": 1.0, "abilReady": 0, "cpu": 1.0,
	"hz": {"traffic": 1, "train": 1, "walk": 1, "pool": 1, "city": 1}, "speed": 1.0, "fov": 58.0, "hud": 1, "fly": 0, "inv": 0, "item": "", "infPep": 0}
var dev_u := false
var dev := {}
var _dev_l3 := false
var race_pay := 0       # coins paid for this race (web patch 65 racePay)


func _dev_load() -> void:
	dev = DEV_DEF.duplicate(true)
	var f := FileAccess.open("user://dev.json", FileAccess.READ)
	if f != null:
		var d = JSON.parse_string(f.get_as_text())
		if d is Dictionary:
			dev_u = bool((d as Dictionary).get("u", false))
			for k in DEV_DEF:
				if (d as Dictionary).has(k):
					dev[k] = d[k]
			var hz: Dictionary = DEV_DEF["hz"].duplicate()
			if d.get("hz") is Dictionary:
				hz.merge(d["hz"], true)
			dev["hz"] = hz


func _dev_save() -> void:
	var d := dev.duplicate(true)
	d["u"] = dev_u
	var f := FileAccess.open("user://dev.json", FileAccess.WRITE)
	if f != null:
		f.store_string(JSON.stringify(d))


## web devR (off line) / devLocal / devPack
func dev_race() -> Dictionary:
	return dev if dev_u and int(dev.get("on", 1)) == 1 else {}


func dev_here() -> Dictionary:
	return dev if dev_u and int(dev.get("on", 1)) == 1 and net_role == "" and web.role == "" else {}


func dev_pack():
	var D := dev_race()
	if D.is_empty():
		return null
	return {"spd": D["spd"], "acc": D["acc"], "hnd": D["hnd"], "wgt": D["wgt"], "off": D["off"], "drift": D["drift"], "grav": D["grav"], "abil": D["abil"],
		"abilReady": 1 if int(D["abilReady"]) == 1 else 0, "cpu": D["cpu"], "hz": (D["hz"] as Dictionary).duplicate()}


func _dev_frame() -> void:
	var D := dev_here()
	var racing := race != null and state == "race"
	Engine.time_scale = float(D.get("speed", 1.0)) if (racing and not D.is_empty()) else 1.0
	if hud_race != null and racing:
		var show := D.is_empty() or int(D.get("hud", 1)) == 1
		if hud_race.modulate.a != (1.0 if show else 0.0):
			hud_race.modulate.a = 1.0 if show else 0.0
	if D.is_empty() or not racing or kart == null:
		return
	if int(D.get("infPep", 0)) == 1 and not kart.finished and kart.item == "" and kart.held.is_empty():
		kart.item = "pepperoni"
	if int(D.get("fly", 0)) != 1 and kart.fly:
		kart.fly = false
	var pads := Input.get_connected_joypads()
	var l3 := pads.size() > 0 and Input.is_joy_button_pressed(pads[0], JOY_BUTTON_LEFT_STICK)
	if l3 and not _dev_l3:
		_dev_fly_toggle()
	_dev_l3 = l3


func _dev_fly_toggle() -> void:
	var D := dev_here()
	if D.is_empty() or int(D.get("fly", 0)) != 1 or kart == null or state != "race":
		return
	kart.fly = not kart.fly
	if kart.fly:
		kart.wvy = 0.0
		kart.spin = 0.0
	_toast("Flying" if kart.fly else "Landing")


func _dev_fly_axis() -> float:
	var up := (1.0 if Keys.held("flyup") else 0.0) - (1.0 if Keys.held("flydown") else 0.0)
	var pads := Input.get_connected_joypads()
	if pads.size() > 0:
		var ay := Input.get_joy_axis(pads[0], JOY_AXIS_LEFT_Y)
		if absf(ay) > 0.2:
			up -= ay
	return clampf(up, -1.0, 1.0)


## web racePay (patch 65): coins for a finished race, into the Sandbox save's purse
func _race_pay() -> void:
	if race == null or kart == null or kart.est or race_pay != 0:
		return
	var n := race.karts.size()
	var p := kart.place if kart.place > 0 else n
	var cm: float = {"small": 1.0, "medium": 1.2, "large": 1.5, "reverse": 1.5}.get(String(sel["cls"]), 1.0)
	var amt := int(round((8.0 + maxf(0.0, n - p) * 3.0 + (10.0 if p == 1 else (5.0 if p == 2 else (2.0 if p == 3 else 0.0)))) * cm)) if n > 1 else 6
	var sv := Sandbox.load_save()
	sv["c"] = int(sv.get("c", 0)) + amt
	Sandbox.keep()
	race_pay = amt


var hl_mode = null""")
rep('main.gd', """	race = Race.new()
	# Sandbox: only when it was asked for""", """	race = Race.new()
	race_pay = 0
	# the developer options' race settings (web patch 68): in a room the host's (cfg "dev", every kart), off line yours (your kart only)
	var wcfg: Dictionary = web.cfg if (web.role != "" and not web.cfg.is_empty()) else cfg
	if not bg and (web.role != "" or net_role != "") and not wcfg.is_empty():
		race.dev = (wcfg["dev"] as Dictionary).duplicate(true) if wcfg.get("dev") is Dictionary else {}
		race.dev_all = true
	elif not bg and cfg.is_empty():
		race.dev = dev_race().duplicate(true)
	race.dev_local = dev_here().duplicate(true) if (not bg and cfg.is_empty()) else {}
	# Sandbox: only when it was asked for""")
rep('main.gd', "race.karts.size() == 1, race.noitm)", "race.karts.size() == 1, race.noitm or not race.itm_used)   # (web patch 64: no item used counts too)")
rep('main.gd', """	Ach.n_tracks = maxi(1, _n_tracks())   # (the tracks there are to race on""", """	_race_pay()
	Ach.n_tracks = maxi(1, _n_tracks())   # (the tracks there are to race on""")
rep('main.gd', """		v.add_child(menu.label(pbt, menu.f_bold, 15.0, Color("#7fe07a") if bool(lr["pb"]) else Color("#c2a58c")))""",
    """		v.add_child(menu.label(pbt, menu.f_bold, 15.0, Color("#7fe07a") if bool(lr["pb"]) else Color("#c2a58c")))
	if race_pay > 0:
		v.add_child(menu.label("+%d coins" % race_pay, menu.f_bold, 15.0, Color("#7fe07a")))   # (web patch 65)""")
rep('main.gd', """	var c := code.strip_edges().to_upper()
	if c == "UNLOCK":""", """	var c := code.strip_edges().to_upper()
	if c == "DEVELOPER":
		dev_u = not dev_u
		_dev_save()
		cheat_ok = true
		cheat_msg = "Developer options unlocked: they are just below this box. Enter DEVELOPER again to hide them." if dev_u else "Developer options hidden."
		sfx.play("lap", 0.8, 1.2)
	elif c == "UNLOCK":""")
rep('main.gd', """			cb.pressed.connect(go)
			ce.text_submitted.connect(go)
	return v""", """			cb.pressed.connect(go)
			ce.text_submitted.connect(go)
			if dev_u:
				_dev_rows(c, on_off)
	return v


## Settings > More: the developer rows (web devUI, the same table)
func _dev_rows(c: Control, on_off: Array) -> void:
	c.add_child(menu.section_label("Developer"))
	# (sliders show their raw value: shares as percentages, the field of view in degrees)
	var sl := func(lab: String, key: String, lo: float, hi: float, step: float, unit := "%") -> Array:
		var v: float = float(dev[key])
		if unit == "°":
			return [lab, "", "dev_" + key, {"lo": lo, "hi": hi, "step": step, "fmt": "%d°", "mul": 1.0}, v]
		return [lab, "", "dev_" + key, {"lo": lo * 100.0, "hi": hi * 100.0, "step": step * 100.0, "fmt": "%+d%%" if unit == "+" else "%d%%", "mul": 0.01}, v]
	var tg := func(lab: String, key: String) -> Array:
		var v: int = int(dev["hz"][key.substr(3)]) if key.begins_with("hz.") else int(dev[key])
		return [lab, "", "dev_" + key, on_off, str(v)]
	c.add_child(_set_rows([["Developer options", "Every setting below; off puts the game back to normal without losing them.", "dev_on", on_off, str(int(dev["on"]))]]))
	c.add_child(menu.para("Race settings: yours off line (your vehicle only). In a room you host they go to everyone's karts at the start of each race; a guest's are not used there.", 13.0, Color("#c2a58c"), 720.0))
	c.add_child(_set_rows([sl.call("Top speed", "spd", 0.5, 2.0, 0.05), sl.call("Acceleration", "acc", 0.25, 3.0, 0.05), sl.call("Handling", "hnd", 0.25, 3.0, 0.05),
		sl.call("Weight", "wgt", 0.4, 2.5, 0.05), sl.call("Off-road grip", "off", -1.0, 2.0, 0.1, "+"), sl.call("Drift boost", "drift", 0.0, 3.0, 0.1), sl.call("Gravity", "grav", 0.2, 2.0, 0.05),
		sl.call("Ability charge speed", "abil", 0.25, 10.0, 0.25), tg.call("Ability always ready", "abilReady"), sl.call("Rival skill", "cpu", 0.5, 1.5, 0.05)]))
	c.add_child(menu.para("Mobs and obstacles: the moving hazards, on the tracks that have them. Also sent to everyone in a room you host.", 13.0, Color("#c2a58c"), 720.0))
	c.add_child(_set_rows([tg.call("Traffic", "hz.traffic"), tg.call("Trains", "hz.train"), tg.call("Walkers", "hz.walk")]))
	c.add_child(menu.para("This device (off line only).", 13.0, Color("#c2a58c"), 720.0))
	c.add_child(_set_rows([sl.call("Game speed", "speed", 0.25, 2.0, 0.05), sl.call("Field of view", "fov", 40.0, 100.0, 1.0, "°"), tg.call("Show the HUD", "hud"),
		tg.call("Flying (left stick press, or G)", "fly"), tg.call("Invincible", "inv"), tg.call("Unlimited pepperoni", "infPep")]))
	var ir := menu.hbox(20)
	var il := menu.label("Always this item", menu.f_bold, 16.0, Color("#fff4dc"))
	il.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	ir.add_child(il)
	var ob := OptionButton.new()
	ob.add_item("Normal boxes")
	ob.set_item_metadata(0, "")
	var its: Array = Race.ITEM_POWER.keys()
	for i in its.size():
		ob.add_item(String(ITEM_NAMES.get(its[i], Ach.ITEM_NAMES.get(its[i], its[i]))))
		ob.set_item_metadata(i + 1, String(its[i]))
		if String(its[i]) == String(dev["item"]):
			ob.select(i + 1)
	ob.item_selected.connect(func(ix):
		dev["item"] = String(ob.get_item_metadata(ix))
		_dev_save())
	ir.add_child(ob)
	c.add_child(ir)
	var br := menu.hbox(10)
	for b in [["+1000 coins", "coins"], ["Unlock the style shop", "shop"], ["Reset all", "reset"]]:
		var bt := menu.button(String(b[0]), "ghost", 14.0, Vector4(14, 8, 14, 8))
		var what := String(b[1])
		bt.pressed.connect(func():
			if what == "coins":
				var sv := Sandbox.load_save()
				sv["c"] = int(sv.get("c", 0)) + 1000
				Sandbox.keep()
				_toast("+1000 coins · %d now" % int(sv["c"]))
			elif what == "shop":
				preload(\"res://scripts/style.gd\").own_all()
				_toast("The whole style shop is yours")
			else:
				dev = DEV_DEF.duplicate(true)
				_dev_save()
				menu.show_modal("set"))
		br.add_child(bt)
	c.add_child(br)


func _dev_set(key: String, val: String) -> void:
	var v = float(val)
	if key.begins_with("hz."):
		(dev["hz"] as Dictionary)[key.substr(3)] = int(v)
	elif key in ["on", "abilReady", "hud", "fly", "inv", "infPep"]:
		dev[key] = int(v)
	else:
		dev[key] = v
	_dev_save()
	# racing alone: a vehicle setting at once (web devSet -> devKart)
	if race != null and kart != null and state == "race" and net_role == "" and web.role == "":
		race.dev = dev_race().duplicate(true)
		race.dev_local = dev_here().duplicate(true)""")
rep('main.gd', """func _apply_setting(key: String, val: String) -> void:
	match key:""", """func _apply_setting(key: String, val: String) -> void:
	if key.begins_with("dev_"):
		_dev_set(key.substr(4), val)
		return
	match key:""")
rep('main.gd', """func _process(dt: float) -> void:
	if web != null:
		web.poll()""", """func _process(dt: float) -> void:
	if web != null:
		web.poll()
	_dev_frame()""")
rep('main.gd', """				if act == "lights" and racing:""", """				if act == "fly" and racing:
					_dev_fly_toggle()   # (web patch 68)
					return
				if act == "lights" and racing:""")
rep('main.gd', """	var o := {"steer": clampf(steer, -1.0, 1.0), "brake": brake, "nb": nb, "mul": mul, "use": false, "back": false, "hold": false, "hold_sl": 1, "release": null, "look": aim_back}""",
    """	var o := {"steer": clampf(steer, -1.0, 1.0), "brake": brake, "nb": nb, "mul": mul, "use": false, "back": false, "hold": false, "hold_sl": 1, "release": null, "look": aim_back,
		"flyup": _dev_fly_axis() if kart != null and kart.fly else 0.0}""")
rep('main.gd', """func _load_settings() -> void:
	var cf := ConfigFile.new()""", """func _load_settings() -> void:
	_dev_load()   # (web patch 68: the developer options keep their own file)
	var cf := ConfigFile.new()""")
open(G + 'style.gd', 'w', encoding='utf-8', newline='').write(STYLE_GD)
print('pc68 applied')
