## Sandbox: things to do and Easter eggs (web v199 tools/mini/activities.js; the owner's brief, section 5). The same table of
## activities and eggs as the web; WHERE each marker and egg stands comes from the web's export of the place (T.sb "acts", "egg":
## sbExport), so the two agree. One activity can be under way at a time, across places (a delivery goes through tunnels): it is
## kept here, static, not in the place's Sandbox object, which is made again in every place.
## Nothing here moves a kart: it reads the kart and pays coins into the shared save (sandbox.gd save: "c", "a", "e").
extends RefCounted

const ACTS := {
	"del_spiral": {"kind": "deliver", "at": "margherita", "to": "spiral", "T": 210.0, "coins": 60, "par": 150.0, "name": "Pizza delivery",
		"goal": "Take the pizza to the start line of Sauce Spiral", "tip": "Safe: through Basil Boulevard. Quicker: through the Oven Rush Raceway, past the flames."},
	"del_bedroom": {"kind": "deliver", "at": "kitchen", "to": "bedroom", "T": 120.0, "coins": 40, "par": 75.0, "name": "Snack delivery",
		"goal": "Take the snack to the start line of Bedroom Blitz", "tip": "Through the hall: the garage door is the long way round."},
	"drift_marg": {"kind": "drift", "at": "margherita", "need": 8.0, "T": 30.0, "coins": 30, "name": "Drift challenge", "goal": "Drift for 8 seconds in all, in 30 seconds", "tip": "Out on the open pizza there is room for long drifts."},
	"drift_bay": {"kind": "drift", "at": "bay", "need": 10.0, "T": 35.0, "coins": 35, "name": "Harbour drift", "goal": "Drift for 10 seconds in all, in 35 seconds", "tip": ""},
	"air_yard": {"kind": "air", "at": "backyard", "need": 5.0, "T": 45.0, "coins": 35, "name": "Jump challenge", "goal": "Be in the air for 5 seconds in all, in 45 seconds", "tip": "The ramps on the track send you highest."},
	"air_spiral": {"kind": "air", "at": "spiral", "need": 4.0, "T": 45.0, "coins": 30, "name": "Jump challenge", "goal": "Be in the air for 4 seconds in all, in 45 seconds", "tip": ""},
}
const EGGS := {"cat": "a cat asleep in the sun", "shell": "a seashell washed up on the crust", "snowman": "a very small snowman", "robot": "a lost little robot",
	"duck": "the rubber duck from the bath", "meatball": "a meatball that got away", "wrench": "the wrench everyone was looking for", "gnome": "a garden gnome, hiding"}

static var act := {}         # the one under way: {id, a, t, v, first}
static var retry := ""       # an activity to start once a Retry's fast travel has arrived
static var ended := {}       # how the last one ended, for main.gd to show: {id, a, why, pay, t, best, par}; main clears it

var sb                       # the place's Sandbox (sandbox.gd)
var marks: Array = []        # {id, a, x, y, z, j}
var near := {}               # the marker the kart stands in ({} none)
var egg := {}                # {id, name, x, y, z, ry, found, hop}


func setup(sb_, d: Dictionary) -> void:
	sb = sb_
	for m in d.get("acts", []):
		var md: Dictionary = m
		var aid := String(md.get("id", ""))
		if ACTS.has(aid):
			marks.append({"id": aid, "a": ACTS[aid], "x": float(md["x"]), "y": float(md["y"]), "z": float(md["z"]), "j": int(md.get("j", 0))})
	var e = d.get("egg")
	if e is Dictionary and EGGS.has(String(e.get("id", ""))):
		var eid := String(e["id"])
		egg = {"id": eid, "name": EGGS[eid], "x": float(e["x"]), "y": float(e["y"]), "z": float(e["z"]), "ry": float(e.get("ry", 0.0)),
			"found": (sb.save.get("e", {}) as Dictionary).has(eid), "hop": 0.0}
	# a challenge is done where it starts (a delivery goes on)
	if not act.is_empty() and String(act["a"]["kind"]) != "deliver" and String(act["a"]["at"]) != String(sb.id):
		finish("left")


static func done_before(aid: String) -> Dictionary:
	var a = Sandbox_save().get("a", {})
	return (a as Dictionary).get(aid, {}) if a is Dictionary else {}


static func Sandbox_save() -> Dictionary:
	return load("res://scripts/sandbox.gd").load_save()


## what the offer says: [title, the line under it]
func offer() -> Array:
	if near.is_empty():
		return []
	var a: Dictionary = near["a"]
	var r := done_before(String(near["id"]))
	var first := r.is_empty() or int(r.get("n", 0)) == 0
	var pay := int(a["coins"]) if first else int(round(float(a["coins"]) / 2.0))
	var goal := String(a["goal"]) + (" within " + clock(float(a["T"])) if String(a["kind"]) == "deliver" else "") + "."
	return ["%s: %d coins%s" % [a["name"], pay, "" if first else " (done before)"], goal]


static func clock(s: float) -> String:
	var n := maxi(0, int(ceil(s)))
	return "%d:%02d" % [n / 60, n % 60]


func start(aid: String) -> void:
	if not act.is_empty() or not ACTS.has(aid):
		return
	var r := done_before(aid)
	act = {"id": aid, "a": ACTS[aid], "t": 0.0, "v": 0.0, "first": r.is_empty() or int(r.get("n", 0)) == 0}
	ended = {}
	near = {}
	sb.race.fx.append({"t": "sb_act", "text": "%s: %s" % [ACTS[aid]["name"], String(ACTS[aid]["goal"]).to_lower()], "tip": ACTS[aid]["tip"]})


## the objective bar: [title, line, fraction 0..1, hurry] or [] when nothing is under way
static func bar() -> Array:
	if act.is_empty():
		return []
	var a: Dictionary = act["a"]
	var left := float(a["T"]) - float(act["t"])
	var places := {"spiral": "Sauce Spiral", "bedroom": "Bedroom Blitz"}
	if String(a["kind"]) == "deliver":
		return [a["name"], "To %s · %s left" % [places.get(String(a["to"]), String(a["to"])), clock(left)], maxf(0.0, left / float(a["T"])), left < 15.0]
	return [a["name"], "%s%.1f / %d s · %s left" % ["Drifting " if String(a["kind"]) == "drift" else "In the air ", float(act["v"]), int(a["need"]), clock(left)], minf(1.0, float(act["v"]) / float(a["need"])), left < 15.0]


func tick(k: Kart, dt: float) -> void:
	if act.is_empty():
		near = {}
		for m in marks:
			if (k.x - float(m["x"])) ** 2 + (k.y - float(m["z"])) ** 2 < 26.0 * 26.0 and absf(k.wy - float(m["y"])) < 12.0:
				near = m
				break
	else:
		var a: Dictionary = act["a"]
		act["t"] = float(act["t"]) + dt
		var kind := String(a["kind"])
		if kind == "drift" and k.drift != 0 and not k.air and absf(k.speed) > 40.0:
			act["v"] = float(act["v"]) + dt
		elif kind == "air" and k.air and k.loop.is_empty():
			act["v"] = float(act["v"]) + dt
		if kind != "deliver" and float(act["v"]) >= float(a["need"]):
			finish("done")
		elif kind == "deliver" and String(sb.id) == String(a["to"]) and sb.has_flag and (k.x - float(sb.flag[0])) ** 2 + (k.y - float(sb.flag[2])) ** 2 < 30.0 * 30.0 and absf(k.wy - float(sb.flag[1])) < 12.0:
			finish("done")
		elif float(act["t"]) >= float(a["T"]):
			finish("time")
	# the egg: drive up to it
	if not egg.is_empty():
		if float(egg["hop"]) > 0.0:
			egg["hop"] = maxf(0.0, float(egg["hop"]) - dt)
		if not bool(egg["found"]) and (k.x - float(egg["x"])) ** 2 + (k.y - float(egg["z"])) ** 2 < 18.0 * 18.0 and absf(k.wy - float(egg["y"])) < 14.0:
			egg["found"] = true
			egg["hop"] = 0.8
			var sv: Dictionary = sb.save
			if not (sv.get("e") is Dictionary):
				sv["e"] = {}
			(sv["e"] as Dictionary)[String(egg["id"])] = 1
			sv["c"] = int(sv.get("c", 0)) + 25
			var n := 0
			for eid in EGGS:
				if (sv["e"] as Dictionary).has(eid):
					n += 1
			sb.keep()
			sb.race.fx.append({"t": "sb_egg", "text": "Easter egg %d/%d: %s · +25" % [n, EGGS.size(), egg["name"]], "x": egg["x"], "y": egg["z"], "h": egg["y"]})


## 'done', 'time', 'cancel' (fast travel, a race from the start line), 'left' (a challenge's place left, or Sandbox); quiet: no panel
static func finish(why: String, quiet := false) -> void:
	if act.is_empty():
		return
	var A := act
	act = {}
	var a: Dictionary = A["a"]
	var sv: Dictionary = Sandbox_save()
	var pay := 0
	var best := false
	if why == "done":
		if not (sv.get("a") is Dictionary):
			sv["a"] = {}
		var all: Dictionary = sv["a"]
		var r: Dictionary = all.get(String(A["id"]), {"n": 0})
		pay = int(a["coins"]) if bool(A["first"]) else int(round(float(a["coins"]) / 2.0))
		var sc := float(A["t"])
		if not r.has("best") or sc < float(r["best"]):
			best = int(r.get("n", 0)) > 0
			r["best"] = snappedf(sc, 0.1)
		r["n"] = int(r.get("n", 0)) + 1
		all[String(A["id"])] = r
		if String(a["kind"]) == "deliver" and sc <= float(a["par"]):
			pay += int(round(float(a["coins"]) / 3.0))
		sv["c"] = int(sv.get("c", 0)) + pay
		load("res://scripts/sandbox.gd").keep()
	if quiet:
		return
	ended = {"id": A["id"], "a": a, "why": why, "pay": pay, "t": float(A["t"]), "best": best, "par": why == "done" and String(a["kind"]) == "deliver" and float(A["t"]) <= float(a["par"])}


## the end panel's words: [title, line]
static func end_words(o: Dictionary) -> Array:
	var a: Dictionary = o["a"]
	var why := String(o["why"])
	var t: String = {"done": "Delivered!" if String(a["kind"]) == "deliver" else "Challenge done!", "time": "Out of time", "cancel": "Delivery ended", "left": "Challenge ended"}[why]
	var line := ""
	if why == "done":
		line = "+%d coins%s · %s%s" % [o["pay"], " (quick delivery bonus)" if bool(o["par"]) else "", clock(float(o["t"])), " · a new best" if bool(o["best"]) else ""]
	elif why == "cancel":
		line = "Fast travel or a race ends a delivery: the pizza has to go by road."
	elif why == "left":
		line = "A challenge is done where it starts."
	else:
		line = "The pizza went cold." if String(a["kind"]) == "deliver" else "So close: try again."
	return [t, line]
