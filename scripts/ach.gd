class_name Ach
## Lifetime goals that unlock the reward liveries and the award items (web ACH / ACHS), and the personal
## bests and recent races shown under Records (web crust-recs / crust-hist). Saved in user://.

const PATH := "user://progress.json"

## id, name, what to do, the counter it watches, how many, the reward livery, the award item
const LIST := [
	["first_win", "First Slice", "Win a race.", "wins", 1, "r_mozz", ""],
	["podium10", "Podium Regular", "Finish in the top three 10 times.", "podiums", 10, "r_circuit", "meatball"],
	["drift50", "Spark Artist", "Fire 50 boosts from the hottest (third level) drift sparks.", "drift3", 50, "r_tiger", "twister"],
	["loops25", "Loop Legend", "Ride all the way round 25 loops.", "loops", 25, "r_vortex", "freezer"],
	["items100", "Topping Thrower", "Use 100 items.", "items", 100, "r_party", "bomb"],
	["glide60", "Sky Chef", "Spend a total of 60 seconds gliding.", "glide", 60, "r_topo", ""],
	["shield10", "Garlic Guardian", "Let a shield block 10 hits.", "blocks", 10, "r_prism", ""],
	["routes15", "Road Less Travelled", "Take 15 shortcuts or side routes.", "routes", 15, "r_holo", ""],
	["comeback", "Comeback Kid", "Win a race after dropping to last place.", "comebacks", 1, "r_heritage", ""],
	["tour16", "World Tour", "Finish a race on every track.", "tracks", 0, "r_galaxy", ""],
	["cup", "Cup Runneth Over", "Win a Grand Prix cup.", "cups", 1, "r_champ", ""],
	["cup200", "Big Cheese", "Win a Grand Prix cup at 200cc or in Reverse.", "cupsHard", 1, "r_lava", ""],
	["races50", "Marathon Chef", "Finish 50 races.", "races", 50, "r_rings", ""],
	["wins10", "Ten Slices", "Win 10 races.", "wins", 10, "r_weave", ""],
	["rev1", "Wrong Way Round", "Win a race in Reverse.", "revWins", 1, "r_dazzle", ""],
	["loops100", "Dizzy Dough", "Ride all the way round 100 loops.", "loops", 100, "r_rainbow", ""],
	["drivers4", "Team Players", "Win races with 4 different drivers.", "drivers", 4, "r_splash", ""],
	["drift200", "Sparks Fly", "Fire 200 boosts from the hottest drift sparks.", "drift3", 200, "r_shatter", ""],
	["perfect", "Clean Sweep", "Win all four races of a Grand Prix cup.", "perfects", 1, "r_gold", ""],
	["cups4", "Grand Slam", "Win all four Grand Prix cups.", "cupset", 4, "r_prismc", ""],
]
const ITEM_NAMES := {"meatball": "Bowling Meatball", "twister": "Dough Twister", "freezer": "Freezer Blast", "bomb": "Calzone Bomb"}

static var d := {}             # {s: counters, u: {id: unix time}, t: tracks, c: cups, dr: drivers, recs: {}, hist: []}
static var n_tracks := 17
static var fresh: Array = []   # achievements won since the last look (for the toast)
static var _dirty := false
static var cheat := false      # the UNLOCK code: everything open until the game closes; real progress untouched


static func _load() -> void:
	if not d.is_empty():
		return
	d = {"s": {}, "u": {}, "t": [], "c": [], "dr": [], "recs": {}, "hist": []}
	if FileAccess.file_exists(PATH):
		var j = JSON.parse_string(FileAccess.get_file_as_string(PATH))
		if typeof(j) == TYPE_DICTIONARY:
			for k in d:
				if j.has(k) and typeof(j[k]) == typeof(d[k]):
					d[k] = j[k]


static func save() -> void:
	_load()
	var f := FileAccess.open(PATH, FileAccess.WRITE)
	if f:
		f.store_string(JSON.stringify(d))
	_dirty = false


static func unlocked(id: String) -> bool:
	_load()
	return cheat or (d["u"] as Dictionary).has(id)


## is a livery a reward that isn't won yet (web livLocked)
static func liv_locked(lv: Dictionary) -> bool:
	var l = lv.get("lock")
	return l != null and String(l) != "" and not unlocked(String(l))


static func need(a: Array) -> int:
	return n_tracks if String(a[3]) == "tracks" else int(a[4])


static func value(a: Array) -> float:
	_load()
	match String(a[3]):
		"tracks":
			return float((d["t"] as Array).size())
		"drivers":
			return float((d["dr"] as Array).size())
		"cupset":
			return float((d["c"] as Array).size())
	return float((d["s"] as Dictionary).get(String(a[3]), 0.0))


static func n_unlocked() -> int:
	_load()
	return LIST.size() if cheat else (d["u"] as Dictionary).size()


## new ones reached: mark them won and remember them for the toast
static func check() -> void:
	_load()
	var got := false
	for a in LIST:
		if not (d["u"] as Dictionary).has(String(a[0])) and value(a) >= need(a) and not cheat:
			d["u"][String(a[0])] = int(Time.get_unix_time_from_system())
			fresh.append(a)
			got = true
	if got:
		save()


static func add(key: String, v := 1.0) -> void:
	_load()
	d["s"][key] = float((d["s"] as Dictionary).get(key, 0.0)) + v
	_dirty = true
	check()


static func flush() -> void:
	if _dirty:
		save()


## the player finished a race (web achFinish)
static func race_done(place: int, was_last: bool, cls: String, ri: int, map_id: String, in_gp: Dictionary) -> void:
	_load()
	var s: Dictionary = d["s"]
	s["races"] = float(s.get("races", 0.0)) + 1.0
	if place == 1:
		s["wins"] = float(s.get("wins", 0.0)) + 1.0
		if was_last:
			s["comebacks"] = float(s.get("comebacks", 0.0)) + 1.0
		if cls == "reverse":
			s["revWins"] = float(s.get("revWins", 0.0)) + 1.0
		if not (d["dr"] as Array).has(ri):
			(d["dr"] as Array).append(ri)
	elif not in_gp.is_empty():
		in_gp["ach_lost"] = true
	if place <= 3:
		s["podiums"] = float(s.get("podiums", 0.0)) + 1.0
	if not (d["t"] as Array).has(map_id):
		(d["t"] as Array).append(map_id)
	save()
	check()


## a Grand Prix finished (web achCup)
static func cup_done(gp: Dictionary, cup_place: int, cls: String) -> void:
	_load()
	if gp.is_empty() or bool(gp.get("ach_done", false)):
		return
	gp["ach_done"] = true
	if cup_place == 1:
		var cup := int(gp.get("cup", 0))
		if not (d["c"] as Array).has(cup):
			(d["c"] as Array).append(cup)
		if not bool(gp.get("ach_lost", false)):
			d["s"]["perfects"] = float((d["s"] as Dictionary).get("perfects", 0.0)) + 1.0
		add("cups")
		if cls == "large" or cls == "reverse":
			add("cupsHard")
	save()


# ---------------------------------------------------------------- records

## a finished run: a new personal best when faster (or the first), and the recent races list.
## Returns {t, old (or -1), pb}.
static func record(map_id: String, cls: String, t: float, place: int, ri: int, spec: Dictionary, run := {}) -> Dictionary:
	_load()
	var key := map_id + "|" + cls
	var recs: Dictionary = d["recs"]
	var old: Dictionary = recs.get(key, {})
	var pb := old.is_empty() or t < float(old.get("t", 1e9))
	if pb:
		recs[key] = {"t": t, "d": int(Time.get_unix_time_from_system()), "place": place, "dr": ri, "spec": spec}
		# the best-run ghost and its lap times
		for k2 in run:
			recs[key][k2] = run[k2]
		# keep the save in check: drop the oldest ghosts if it ever gets large (web saveRun)
		var size := JSON.stringify(recs).length()
		if size > 3000000:
			var ks: Array = recs.keys().filter(func(k3): return k3 != key and (recs[k3] as Dictionary).has("g"))
			ks.sort_custom(func(a, b): return float(recs[a].get("d", 0)) < float(recs[b].get("d", 0)))
			while size > 3000000 and not ks.is_empty():
				(recs[ks.pop_front()] as Dictionary).erase("g")
				size = JSON.stringify(recs).length()
	var h: Array = d["hist"]
	h.push_front({"m": map_id, "c": cls, "t": t, "p": place, "d": int(Time.get_unix_time_from_system()), "dr": ri, "pb": pb})
	while h.size() > 60:
		h.pop_back()
	save()
	return {"t": t, "old": float(old.get("t", -1.0)) if not old.is_empty() else -1.0, "pb": pb}


static func best(map_id: String, cls: String) -> Dictionary:
	_load()
	return (d["recs"] as Dictionary).get(map_id + "|" + cls, {})


static func history() -> Array:
	_load()
	return d["hist"]
