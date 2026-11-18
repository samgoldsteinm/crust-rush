## (load it by path: preload("res://scripts/style.gd"); a new class_name is not known until the editor rebuilds its cache)
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
const SLOTS := {"tr": ["tr", TRIMS], "ac": ["tr", TRIMS], "in": ["tr", TRIMS], "rm": ["tr", TRIMS], "gl": ["gl", GLOWS], "hl": ["hl", LIGHTS], "sm": ["sm", SMOKES]}
const PATH := "user://own.json"
## web patch 73's colour combos: p a paint (the garage's paint list), st the style; p price (0 free). KEEP THE WEB'S ORDER ("cb" + index)
const COMBOS := [{"n": "Stealth", "p": 8, "st": {"tr": 1, "ac": 1, "in": 1, "rm": 1, "gl": 0, "hl": 1, "sm": 0}, "c": 0},
	{"n": "Track Day", "p": 1, "st": {"tr": 1, "ac": 2, "in": 1, "rm": 3, "gl": 0, "hl": 1, "sm": 0}, "c": 0},
	{"n": "Arctic", "p": 9, "st": {"tr": 3, "ac": 13, "in": 2, "rm": 3, "gl": 1, "hl": 2, "sm": 0}, "c": 350},
	{"n": "Midnight Neon", "p": 8, "st": {"tr": 14, "ac": 13, "in": 1, "rm": 14, "gl": 1, "hl": 2, "sm": 2}, "c": 450},
	{"n": "Toxic", "p": 4, "st": {"tr": 1, "ac": 12, "in": 12, "rm": 1, "gl": 4, "hl": 5, "sm": 5}, "c": 500},
	{"n": "Miami", "p": 7, "st": {"tr": 2, "ac": 13, "in": 2, "rm": 2, "gl": 5, "hl": 1, "sm": 7}, "c": 550},
	{"n": "Inferno", "p": 2, "st": {"tr": 1, "ac": 4, "in": 4, "rm": 15, "gl": 3, "hl": 3, "sm": 3}, "c": 600},
	{"n": "Royal Gold", "p": 6, "st": {"tr": 16, "ac": 16, "in": 11, "rm": 16, "gl": 2, "hl": 0, "sm": 4}, "c": 650},
	{"n": "Chrome King", "p": 8, "st": {"tr": 17, "ac": 17, "in": 1, "rm": 17, "gl": 7, "hl": 1, "sm": 1}, "c": 900},
	{"n": "Spectrum", "p": 5, "st": {"tr": 1, "ac": 10, "in": 1, "rm": 17, "gl": 8, "hl": 4, "sm": 8}, "c": 1200}]


static func combo_owned(i: int) -> bool:
	if i < 0 or i >= COMBOS.size():
		return false
	return int(COMBOS[i]["c"]) == 0 or Ach.cheat or owned().has("cb%d" % i)


## a bought combo's piece, in its own slot only (web comboAllows)
static func combo_allows(slot: String, i: int) -> bool:
	if i == 0:
		return false
	var o := owned()
	for j in COMBOS.size():
		var c: Dictionary = COMBOS[j]
		if int(c["c"]) > 0 and int((c["st"] as Dictionary).get(slot, 0)) == i and o.has("cb%d" % j):
			return true
	return false


static func combo_buy(i: int) -> bool:
	if combo_owned(i):
		return true
	var sv: Dictionary = Sandbox.load_save()
	if int(sv.get("c", 0)) < int(COMBOS[i]["c"]):
		return false
	sv["c"] = int(sv["c"]) - int(COMBOS[i]["c"])
	Sandbox.keep()
	var o := owned()
	o["cb%d" % i] = true
	_put(o)
	return true
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
	if Ach.cheat:
		return true   # (web patch 70: the UNLOCK code; nothing is bought or written down)
	var L: Array = SLOTS[slot][1]
	if i < 0 or i >= L.size() or int(L[i]["p"]) == 0:
		return true
	return owned().has(String(SLOTS[slot][0]) + str(i)) or combo_allows(slot, i)   # (pc72: a combo's piece)


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
