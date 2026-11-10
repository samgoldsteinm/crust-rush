class_name WebNet
extends Node
## Cross-play with the browser version (web NET, protocol 97). The web game finds friends and races through public MQTT
## brokers (a room code is a topic; every player listens on a topic of their own), so a PC speaking the same messages can
## join a room a browser made. Joining works like the web's: the host runs the real race; this PC drives its own kart
## straight away from your controls, sends them numbered to the host, and when the host's copy of the kart comes back it
## takes that and replays the controls the host hasn't seen yet, so steering is instant. Everything else is drawn as the
## host sends it. PC-to-PC races (ENet) are separate and unchanged.

const PROTO := 97
const TOP := "crustrush/v2/"
const BROKERS := ["wss://broker.emqx.io:8084/mqtt", "wss://broker.hivemq.com:8884/mqtt", "wss://test.mosquitto.org:8081/mqtt"]
const STEP := 1.0 / 120.0
## the web kart record (NET_REM): the first 8 always, the rest only when not at rest
const REM := ["x", "y", "a", "ma", "z", "wy", "speed", "steer", "drift", "charge", "boost", "spin", "air", "glide", "loopTh", "onRamp", "rush", "shL",
	"shield", "mzH", "sink", "sinkT", "trickK", "trickT", "frozen", "acc", "brake", "dAmt", "fx", "prog", "finished", "place", "finishTime", "inv", "big",
	"ghostT", "shrinkT", "absT", "idx", "gRings", "trick", "bPk", "fTier", "megaT", "pestoT", "flatT", "chiliT", "oilT", "burnT", "est", "oliveT"]
const ZB := ["air", "glide", "onRamp", "finished", "big", "trick", "est"]
const ZN := ["shL", "sink", "sinkT", "trickK", "dAmt", "ghostT", "shrinkT", "absT", "bPk", "fTier", "megaT", "pestoT", "flatT", "chiliT", "oilT", "burnT", "oliveT"]
## web kart fields the PC must never take from the network (they belong to this machine's own set-up)
const KEEP := ["ri", "is_player", "human", "peer", "remote", "auto", "sf", "events", "sm_spd", "sm_acc", "sm_hnd", "sm_off", "sm_wgt", "base_max", "glider_sink", "glider_air"]

signal changed(msg: String)

var main      # the game (main.gd)
var role := ""            # "" or "guest"
var my_id := ""
var mqs: Array = []
var chan := {}            # the link to the host: peer, top, mq, last_in, last_out
var chans := {}           # hosting: relay id -> a friend's link (as chan, plus pid: their number in the room)
var gone := {}
var next_id := 1
var loaded_ids := {}
var in_q := {}            # pid -> their numbered controls waiting [seq, steer, brake, ev, ab, mul, nb]
var in_s := {}            # pid -> the buffer's state
var acks := {}            # pid -> the last control played
var sn := 0
var h_sig := ""
var tick_n := 0
var knock_room := ""
var knock_until := 0
var knock_next := 0
var code := ""
var me := 0
var pl: Array = []
var host_tk := ""
var name_ := "Player"
var ready_ := false
var cfg := {}
var rk := 0
var go := false
var loaded := false
var t2 := 0               # the 2-second chores
# the race
var seq := 0
var hist: Array = []      # [seq, inp]
var out_q: Array = []     # [seq, steer, brake, ev, ab, mul, nb]
var unack: Array = []
var ack_rx := 0
var last_fl := 0
var last_sn := 0
var snap_at := 0
var snap_dt := 0.05
var host_gs := ""
var host_away := false
var ping_ms := -1.0
var ev_q := ""            # an item press waiting to go with the next control step
var ab_q := 0
var fresh := true
var bytes_in := 0
var bytes_out := 0
var fixes := 0

static var _map := {}      # web field -> [pc field, type]


static func rid() -> String:
	var s := ""
	var al := "abcdefghijkmnpqrstuvwxyz23456789"
	for i in 12:
		s += al[randi() % al.length()]
	return s


static func _now() -> int:
	return Time.get_ticks_msec()


func active() -> bool:
	return role != ""


func racing() -> bool:
	return role == "guest" and not cfg.is_empty()


## hosting a race for browser friends right now
func hosting() -> bool:
	return role == "host" and not cfg.is_empty()


# ---------------------------------------------------------------- transport (web NetRelay)

func _brokers() -> Array:
	var e := OS.get_environment("CR_BROKERS")
	if e != "":
		return Array(e.split(","))
	return BROKERS


func _start_relay() -> void:
	my_id = rid()
	mqs.clear()
	for u in _brokers():
		var m := Mqtt.new(String(u), "cr-" + my_id + "-" + rid().substr(0, 4), _got)
		m.sub(TOP + "p/" + my_id)
		m.start()
		mqs.append(m)


func _send(m: Dictionary, dup := false) -> void:
	_send_to(chan, m, dup)


func _send_to(ch: Dictionary, m: Dictionary, dup := false, raw := false) -> void:
	if ch.is_empty():
		return
	var s := JSON.stringify(m if raw else {"f": my_id, "d": m})
	bytes_out += s.length()
	ch["last_out"] = _now()
	var sent: Mqtt = null
	var cm: Mqtt = ch.get("mq")
	if cm != null and cm.ok and cm.pub(ch["top"], s):
		sent = cm
	else:
		for q in mqs:
			if (q as Mqtt).pub(ch["top"], s):
				ch["mq"] = q
				sent = q
				break
	# controls also go through a second server: whichever copy lands first is used
	if dup and sent != null:
		for q in mqs:
			if q != sent and (q as Mqtt).ok:
				(q as Mqtt).pub(chan["top"], s)
				break


func _got(_topic: String, text: String, q: Mqtt) -> void:
	var d = JSON.parse_string(text)
	if not (d is Dictionary) or String(d.get("f", "")) == my_id or String(d.get("f", "")) == "":
		return
	var f := String(d["f"])
	var c := String(d.get("c", ""))
	if role == "host":
		_got_host(f, c, d, q, text)
		return
	if c == "ok":
		if knock_room != "" and chan.is_empty():
			knock_room = ""
			chan = {"peer": f, "top": TOP + "p/" + f, "mq": q, "last_in": _now(), "last_out": 0}
			_on_open()
		return
	if chan.is_empty() or f != String(chan["peer"]):
		return
	chan["last_in"] = _now()
	var cm: Mqtt = chan.get("mq")
	if cm == null or not cm.ok:
		chan["mq"] = q
	if c == "bye":
		_lost("The host closed the room.")
		return
	if d.has("d") and d["d"] is Dictionary:
		bytes_in += text.length()
		_recv(d["d"])


## every frame: the servers, the knock, heartbeats, the controls going out
func poll() -> void:
	if role == "":
		return
	for q in mqs:
		(q as Mqtt).poll()
	var now := _now()
	if role == "host":
		_poll_host(now)
		return
	if knock_room != "":
		var any_ok := false
		var all_failed := true
		for q in mqs:
			any_ok = any_ok or (q as Mqtt).ok
			all_failed = all_failed and (q as Mqtt).failed
		if all_failed:
			_lost("Could not reach the multiplayer servers. Check your internet connection and try again.")
			return
		if now > knock_until:
			_lost("Could not find room %s. Check the code, and make sure the host still has the room screen open." % code)
			return
		if any_ok and now >= knock_next:
			knock_next = now + 1000
			var s := JSON.stringify({"f": my_id, "c": "knock"})
			for q in mqs:
				(q as Mqtt).pub(knock_room, s)
		return
	if chan.is_empty():
		return
	if now - int(chan.get("last_out", 0)) > 1500:
		_send({"t": "hb"})
	var lim := 20000 if (main != null and main.state in ["race", "countdown"] and not host_away) else 180000
	if now - int(chan.get("last_in", now)) > lim:
		_lost("Lost the connection. Check that everyone is online with the game open.")
		return
	if now - t2 > 2000:
		t2 = now
		_send({"t": "pg", "ts": now})
		if not cfg.is_empty() and not go:
			if loaded:
				_send({"t": "loaded"})
		elif cfg.is_empty():
			_send_pick()
	_flush()


# ---------------------------------------------------------------- the room

## join a browser friend's room by its four-letter code
func join(room: String, nm: String) -> void:
	leave(false)
	code = room.strip_edges().to_upper()
	if code.length() < 4:
		changed.emit("Enter the 4-letter room code.")
		return
	name_ = nm.substr(0, 14)
	role = "guest"
	_start_relay()
	knock_room = TOP + "r/" + code
	knock_until = _now() + 40000
	knock_next = 0
	changed.emit("Looking for room %s… This can take a few seconds." % code)


func _on_open() -> void:
	_send({"t": "hello", "name": name_, "v": PROTO})
	ready_ = true
	_send_pick()
	changed.emit("")


func _send_pick() -> void:
	if role != "guest" or chan.is_empty() or main == null:
		return
	_send({"t": "pick", "ri": int(main.sel["ri"]), "build": main._my_build(), "ready": ready_})


func leave(tell := true) -> void:
	if role == "guest" and tell and not chan.is_empty():
		_send({"t": "bye"})
	if role == "host" and tell:
		for f in chans:
			_send_to(chans[f], {"f": my_id, "c": "bye"}, false, true)
	chans = {}
	gone = {}
	for q in mqs:
		(q as Mqtt).close()
	mqs.clear()
	chan = {}
	role = ""
	knock_room = ""
	cfg = {}
	pl = []
	host_tk = ""
	go = false
	loaded = false


func _lost(msg: String) -> void:
	var was_race: bool = not cfg.is_empty()
	leave(false)
	if main != null:
		main._web_lost(msg, was_race)
	changed.emit(msg)


func _recv(d: Dictionary) -> void:
	var t := String(d.get("t", ""))
	match t:
		"lobby":
			pl = d.get("pl", [])
			me = int(d.get("you", 0))
			code = String(d.get("code", code))
			host_tk = String(d["tk"]) if d.get("tk") != null else ""
			changed.emit("")
		"full":
			_lost(String(d.get("why", "This room is full.")))
		"load":
			var c: Dictionary = d.get("cfg", {})
			if not cfg.is_empty() and String(c.get("id", "")) != "" and String(c.get("id", "")) == String(cfg.get("id", "")):
				return
			_begin_load(c)
		"go":
			_go()
		"away":
			host_away = true
		"back":
			host_away = false
		"s":
			_snap(d)
		"menu":
			cfg = {}
			go = false
			loaded = false
			if main != null:
				main._web_menu()
			changed.emit("")
		"hit":
			if (d.get("rk") == null or int(d["rk"]) == rk) and main != null and main.state == "race" and main.kart != null and not main.kart.finished and d.get("me") is Dictionary and int(d.get("ack", 0)) >= ack_rx:
				ack_rx = int(d.get("ack", 0))
				_reconcile(d["me"], ack_rx)
				NetLog.ev("hit", 0)
		"po":
			var r := float(_now() - int(d.get("ts", _now())))
			ping_ms = r if ping_ms < 0.0 else ping_ms * 0.6 + r * 0.4


static func _rk_of(id: String) -> int:
	var h := 7
	for ch in id:
		h = (h * 31 + ch.unicode_at(0)) % 997
	return h + 1


func _begin_load(c: Dictionary) -> void:
	cfg = c
	rk = _rk_of(String(c.get("id", "")))
	seq = 0
	hist.clear()
	out_q.clear()
	unack.clear()
	ack_rx = 0
	last_sn = 0
	host_gs = ""
	go = false
	loaded = false
	fresh = true
	fixes = 0
	if main == null:
		return
	var err: String = main._web_load(c)
	if err != "":
		_send({"t": "quit"})
		_lost(err)
		return
	loaded = true
	_send({"t": "loaded"})


func _go() -> void:
	if go or cfg.is_empty():
		return
	go = true
	if main != null:
		main._web_go()


## the web cfg as the PC's: who sits in which grid slot with which kart
func pc_cfg(c: Dictionary) -> Dictionary:
	var slots: Array = []
	for s in 8:
		slots.append({"ri": -1, "peer": 0, "own": false})
	for kq in c.get("karts", []):
		var kd: Dictionary = kq
		var s := int(kd.get("slot", 0))
		if s < 0 or s > 7:
			continue
		var who := int(kd.get("who", -1))
		slots[s] = {"ri": int(kd.get("ri", 0)), "peer": who + 1 if who >= 0 else 0, "own": who == me, "build": kd.get("build", {}), "name": String(kd.get("name", ""))}
	return {"seed": 1, "slots": slots, "cls": String(c.get("cls", "medium"))}


# ---------------------------------------------------------------- the race: this PC's own kart

## one 120 Hz step while racing: your controls drive your kart here at once and go to the host numbered
func step(dt: float, inp: Dictionary) -> void:
	var k: Kart = main.kart
	var hr := host_gs == "race" and not host_away and _now() - snap_at < 1300
	if main.state != "race" or k == null or k.finished or not hr:
		return
	var ev := ev_q
	ev_q = ""
	var ab := ab_q
	ab_q = 0
	var stq := snappedf(float(inp["steer"]), 0.01)
	var mq := 0 if float(inp["mul"]) == 0.0 else 1
	var i2 := {"steer": stq, "brake": bool(inp["brake"]), "nb": bool(inp["nb"]), "mul": float(mq), "use": false, "back": false, "hold": false, "hold_sl": 1, "release": null}
	seq += 1
	hist.append([seq, i2])
	if hist.size() > 480:
		hist.pop_front()
	out_q.append([seq, stq, 1 if bool(inp["brake"]) else 0, ev if ev != "" else 0, ab, mq, 1 if bool(inp["nb"]) else 0])
	k._save_prev()
	k.step(i2, dt)


## relay: every message repeats every control the host hasn't confirmed, so a lost one costs nothing
func _flush() -> void:
	if role != "guest" or chan.is_empty() or cfg.is_empty():
		return
	var now := _now()
	if out_q.is_empty() and not (not unack.is_empty() and now - last_fl > 120):
		return
	if now - last_fl < 40:
		return
	last_fl = now
	unack.append_array(out_q)
	out_q.clear()
	var i := 0
	while i < unack.size() and int(unack[i][0]) <= ack_rx:
		i += 1
	if i > 0:
		unack = unack.slice(i)
	if unack.size() > 72:
		unack = unack.slice(unack.size() - 72)
	if unack.is_empty():
		return
	var v: Array = []
	var x: Array = []
	for j in unack.size():
		var e: Array = unack[j]
		v.append((roundi(float(e[1]) * 100.0) + 100) * 8 + (4 if int(e[6]) != 0 else 0) + (2 if int(e[2]) != 0 else 0) + (0 if int(e[5]) == 0 else 1))
		if (e[3] is String and String(e[3]) != "") or int(e[4]) != 0:
			x.append([j, e[3] if e[3] is String else 0, 1 if int(e[4]) != 0 else 0])
	_send({"t": "in", "rk": rk, "s": int(unack[0][0]), "v": v, "x": x, "ls": last_sn}, true)


# ---------------------------------------------------------------- the race: what the host sends

static func _snake(s: String) -> String:
	var o := ""
	for ch in s:
		if ch != ch.to_lower():
			o += "_" + ch.to_lower()
		else:
			o += ch
	return o


static func _field(f: String) -> Array:
	if _map.is_empty():
		var props := {}
		for p in Kart.new().get_property_list():
			if int(p["usage"]) & PROPERTY_USAGE_SCRIPT_VARIABLE:
				props[String(p["name"])] = int(p["type"])
		_map["__props"] = props
	if _map.has(f):
		return _map[f]
	var props2: Dictionary = _map["__props"]
	var sn := _snake(f)
	var r: Array = []
	if props2.has(sn) and not sn in KEEP and props2[sn] in [TYPE_FLOAT, TYPE_INT, TYPE_BOOL, TYPE_STRING]:
		r = [sn, props2[sn]]
	_map[f] = r
	return r


static func _put(k: Kart, f: String, v) -> void:
	var m := _field(f)
	if m.is_empty():
		return
	var pf: String = m[0]
	match int(m[1]):
		TYPE_FLOAT:
			k.set(pf, float(v) if (v is float or v is int or v is bool) else 0.0)
		TYPE_INT:
			k.set(pf, int(v) if (v is float or v is int or v is bool) else 0)
		TYPE_BOOL:
			k.set(pf, bool(v) if v != null else false)
		TYPE_STRING:
			k.set(pf, String(v) if v is String else "")


static func _dec(a: Array) -> Array:
	var v: Array = []
	for f in REM:
		v.append(false if f in ZB else (null if f in ZN else 0))
	for j in mini(8, a.size()):
		v[j] = a[j]
	var i := 8
	while i + 1 < a.size():
		var ix := int(a[i])
		if ix >= 0 and ix < v.size():
			v[ix] = a[i + 1]
		i += 2
	return v


func _loop_state(i: int, th: float, lat0) -> Dictionary:
	var T: TrackData = main.T
	if i < 0 or i >= T.loops.size():
		return {}
	var L: Dictionary = T.loops[i]
	return {"th": th, "p": L["p"], "lat0": float(lat0) if lat0 != null else float(L.get("lat0", 0.0)), "shift": float(L["shift"]), "g0": float(L["g0"]), "j": int(L["j"]), "full": bool(L["full"])}


## the host's full copy of a kart (web netKScal) onto ours
func _apply_full(k: Kart, S: Dictionary) -> void:
	for f in S:
		if f in ["pend", "loopI", "loopT", "loopL", "heldIt", "heldSl", "scK"]:
			continue
		_put(k, String(f), S[f])
	var pe: Array[String] = []
	for it in S.get("pend", []):
		if it is String:
			pe.append(it)
	k.pend = pe
	var li := int(S.get("loopI", -1))
	if li >= 0:
		var L := _loop_state(li, float(S.get("loopT", 0.0)), S.get("loopL"))
		if k.loop.is_empty() or int(k.loop.get("j", -1)) != int(L.get("j", -2)):
			k.loop = L
		else:
			k.loop["th"] = float(S.get("loopT", 0.0))
			k.loop["lat0"] = float(L["lat0"])
	else:
		k.loop = {}
	k.sc = int(S.get("scK", -1))
	var hi = S.get("heldIt")
	if hi is String and String(hi) != "":
		if k.held.is_empty() or String(k.held.get("it", "")) != String(hi):
			k.held = {"it": hi, "sl": int(S.get("heldSl", 1)), "t": 0.0}
	else:
		k.held = {}


## the host's copy of our kart: take it, then replay quietly every control the host hasn't played yet
func _reconcile(S: Dictionary, ack: int) -> void:
	var k: Kart = main.kart
	var ox := k.x
	var oy := k.y
	_apply_full(k, S)
	var keep: Array = []
	for h in hist:
		if int(h[0]) > ack:
			keep.append(h)
	hist = keep
	for h in hist:
		k.step(h[1], STEP)
	k.events.clear()
	var e := Vector2(ox - k.x, oy - k.y).length()
	if e > 3.0:
		fixes += 1
		if e > 12.0:
			NetLog.ev("fix", roundi(e))
	# small corrections slide in over the next frames instead of jumping
	if e < 60.0:
		k.ox += k.x - ox
		k.oy += k.y - oy
	else:
		k._save_prev()


func _snap(d: Dictionary) -> void:
	if d.get("rk") != null and rk != 0 and int(d["rk"]) != rk:
		return
	var n := int(d.get("n", 0))
	if n > 0 and n <= last_sn:
		return
	if n > 0:
		last_sn = n
	if float(d.get("ack", 0)) > ack_rx:
		ack_rx = int(d["ack"])
	NetLog.got_snap()
	_dump(d)
	host_away = false
	var now := _now()
	if snap_at > 0:
		snap_dt = lerpf(snap_dt, clampf((now - snap_at) / 1000.0, 1.0 / 60.0, 0.25), 0.2)
	snap_at = now
	host_gs = String(d.get("gs", host_gs))
	if main == null or cfg.is_empty() or main.race == null:
		return
	if not go and host_gs in ["countdown", "race"] and loaded:
		_go()
	var race: Race = main.race
	var mine: Kart = main.kart
	if host_gs == "race" and main.state == "countdown":
		main._web_race_on()
	if absf(race.race_time - float(d.get("rt", 0.0))) > 0.25:
		race.race_time = float(d.get("rt", 0.0))
	race.sim_time = maxf(race.sim_time, float(d.get("st", 0.0)) - 0.2)
	var kc: Array = d.get("kc", [])
	for i in mini(kc.size(), race.karts.size()):
		var k: Kart = race.karts[i]
		if k == mine and not mine.finished:
			continue
		var r: Array = kc[i]
		var v := _dec(r[0])
		k.ox = k.x
		k.oy = k.y
		k.owy = k.wy
		k.oa = k.a
		k.oma = k.ma
		k.o_th = k.loop_th
		k.o_loop = not k.loop.is_empty()
		for j in REM.size():
			_put(k, REM[j], v[j])
		var li := int(r[1]) if r.size() > 1 and r[1] != null else -1
		var lp = r[3] if r.size() > 3 else null
		if li >= 0 and lp is Array:
			k.loop = _loop_state(li, float(lp[0]), lp[1])
			k.loop_th = maxf(0.0001, float(lp[0]))
		else:
			k.loop = {}
			k.loop_th = 0.0
		var hi = r[2] if r.size() > 2 else null
		if k != mine:
			if hi is String and String(hi) != "":
				if k.held.is_empty() or String(k.held.get("it", "")) != String(hi):
					k.held = {"it": hi, "sl": 1, "t": 0.0}
			else:
				k.held = {}
		if fresh or Vector2(k.x - k.ox, k.y - k.oy).length() > 120.0:
			k._save_prev()
	fresh = false
	# item boxes, thrown items and traps
	# the web counts the boxes on train wagons too; the PC's own list leaves them out
	var bx: Array = d.get("b", [])
	var T0: TrackData = main.T
	var bi := 0
	for i in mini(bx.size(), T0.boxes.size()):
		if bool((T0.boxes[i] as Dictionary).get("train", false)):
			continue
		if bi < race.boxes.size():
			race.boxes[bi]["r"] = float(bx[i]) / 20.0
		bi += 1
	var old := {}
	for p in race.projectiles:
		old[p["id"]] = p
	race.projectiles.clear()
	for q in d.get("p", []):
		var r: Array = q
		if r.size() < 10 or int(r[9]) == 0:
			continue
		var id := int(r[0])
		var x := float(r[15]) if r.size() > 16 else float(r[2])
		var y := float(r[16]) if r.size() > 16 else float(r[4])
		var prev = old.get(id)
		var ty := String(r[10]) if r.size() > 10 and r[10] is String else String(r[1])
		var tg := int(r[13]) if r.size() > 13 else -1
		var ow := int(r[14]) if r.size() > 14 else -1
		race.projectiles.append({"id": id, "type": ty, "x": x, "y": y, "px": prev["x"] if prev != null else x, "py": prev["y"] if prev != null else y,
			"vx": float(r[11]) if r.size() > 11 else 0.0, "vy": float(r[12]) if r.size() > 12 else 0.0, "t": 1.0, "t0": 1.0, "ph": "", "pt": 0.0, "dir": 0.0, "spin": 0.0,
			"age": 1.0, "storm": false, "landed": true, "fuse": 0.0, "owner": race.karts[ow] if ow >= 0 and ow < race.karts.size() else null,
			"target": race.karts[tg] if tg >= 0 and tg < race.karts.size() else null})
	if d.has("h"):
		race.hazards.clear()
		for q in d.get("h", []):
			var r: Array = q
			if r.size() < 10 or int(r[9]) == 0:
				continue
			var hd := {"id": int(r[0]), "x": float(r[13]) if r.size() > 14 else float(r[2]), "y": float(r[14]) if r.size() > 14 else float(r[4]), "t": 9.0, "born": 1.0}
			var hk := String(r[10]) if r.size() > 10 and r[10] is String else "oil"
			if hk == "olive":
				hd["olive"] = true
			elif hk != "oil":
				hd["kind"] = hk
			race.hazards.append(hd)
	# our own kart: the host's copy, with the controls it hasn't played yet on top
	var S = d.get("me")
	if S is Dictionary and mine != null:
		if not mine.finished:
			_reconcile(S, ack_rx)
		else:
			_apply_full(mine, S)
	race.stand = race.standings()


## how far between the last two snapshots the other karts are drawn
func alpha() -> float:
	return clampf(float(_now() - snap_at) / 1000.0 / maxf(0.016, snap_dt), 0.0, 1.0)


## an item press or the special, sent with the next control step (web ev / ab)
func press(it: String, back: bool) -> void:
	if it == "ability":
		ab_q = 2 if back else 1
	elif it != "":
		ev_q = it + ("B" if back and it.begins_with("fwd") else "")


## you left the race for the menu: the host's computer takes your kart; you stay in the room
func quit_race() -> void:
	if role == "guest" and not chan.is_empty():
		_send({"t": "quit"})
	cfg = {}
	go = false
	loaded = false


## for the network log's rows
func stats() -> Dictionary:
	var o := {"rtt": roundi(maxf(0.0, ping_ms)), "out": bytes_out, "in": bytes_in, "fixes": fixes}
	bytes_out = 0
	bytes_in = 0
	fixes = 0
	return o


var _dumped := {}


## testing (CR_XDUMP): keep a few of the host's snapshots to read back
func _dump(d: Dictionary) -> void:
	var path := OS.get_environment("CR_XDUMP")
	if path == "":
		return
	for key in ["me", "p", "h"]:
		if not _dumped.has(key) and d.has(key) and not (d[key] is Array and (d[key] as Array).is_empty()):
			_dumped[key] = true
			var f := FileAccess.open(path, FileAccess.READ_WRITE if FileAccess.file_exists(path) else FileAccess.WRITE)
			if f != null:
				f.seek_end()
				f.store_line(JSON.stringify(d))


# ---------------------------------------------------------------- hosting a room for browser friends (web netHost)

const ALPHA := "ABCDEFGHJKMNPQRSTUVWXYZ23456789"
const SLOTS := [4, 3, 5, 2]
## the web kart's own scalar fields that matter to its driving (what web netKScal sends a friend about their kart)
const SCAL := ["x", "y", "a", "ma", "speed", "steer", "drift", "charge", "boost", "spin", "inv", "z", "zv", "pen", "brake", "acc", "gripT", "dHold", "item",
	"item2", "roll", "shield", "mzH", "rush", "frozen", "idx", "prog", "finished", "finishTime", "place", "air", "onRamp", "trick", "trickT", "pd", "glide",
	"gRings", "wy", "lastG", "wvy", "gRate", "loopTh", "pBoost", "bAge", "bPk", "tier", "dAmt", "dTime", "sT", "dWant", "dLatch", "big", "airT", "gH", "gTr",
	"trickN", "trickK", "onGlide", "wallT", "bLock", "est", "shL", "absT", "oilT", "abC", "fireT", "fireAcc", "megaT", "flatT", "flatImm", "pestoT", "chiliT",
	"oliveT", "abFx", "burnT", "jalN", "magT", "cutT", "cutA", "ghostT", "sauceT", "shrinkT", "cannonT", "autoT", "fTier", "elim", "elimLap"]


## make a room browsers (and other PCs on the browser route) can join with its code
func host(nm: String) -> void:
	leave(false)
	role = "host"
	name_ = nm.substr(0, 14)
	_start_relay()
	code = ""
	for i in 4:
		code += ALPHA[randi() % ALPHA.length()]
	for q in mqs:
		(q as Mqtt).sub(TOP + "r/" + code)
	me = 0
	next_id = 1
	pl = [{"id": 0, "name": name_, "ready": true, "ri": int(main.sel["ri"]) if main != null else 0}]
	changed.emit("")


func guests_open() -> Array:
	var out: Array = []
	for f in chans:
		if bool((chans[f] as Dictionary).get("open", false)):
			out.append(chans[f])
	return out


func _got_host(f: String, c: String, d: Dictionary, q: Mqtt, text: String) -> void:
	if c == "knock":
		if gone.has(f):
			return
		if not chans.has(f):
			chans[f] = {"peer": f, "top": TOP + "p/" + f, "mq": q, "last_in": _now(), "last_out": 0, "open": false, "pid": 0}
		var ch: Dictionary = chans[f]
		q.pub(String(ch["top"]), JSON.stringify({"f": my_id, "c": "ok"}))
		if not bool(ch.get("acc", false)):
			ch["acc"] = true
			_knocked(ch)
		return
	if not chans.has(f):
		return
	var ch2: Dictionary = chans[f]
	ch2["last_in"] = _now()
	var cm: Mqtt = ch2.get("mq")
	if cm == null or not cm.ok:
		ch2["mq"] = q
	if c == "bye":
		_drop(ch2)
		return
	if d.has("d") and d["d"] is Dictionary:
		bytes_in += text.length()
		_recv_host(ch2, d["d"])


func _knocked(ch: Dictionary) -> void:
	if guests_open().size() >= 3 or (not cfg.is_empty() and main != null and main.state != "menu"):
		_send_to(ch, {"t": "full", "why": "This room is full (4 racers)." if guests_open().size() >= 3 else "A race is already running. Try again when it ends."})
		ch["closing"] = _now() + 600
		return
	ch["pid"] = next_id
	next_id += 1
	ch["open"] = true
	pl.append({"id": int(ch["pid"]), "name": "Player %d" % int(ch["pid"]), "ready": false, "ri": 0, "build": null, "peer": ch["peer"]})
	_lobby_sync()


func _drop(ch: Dictionary) -> void:
	var f := String(ch["peer"])
	if not chans.has(f):
		return
	chans.erase(f)
	gone[f] = true
	var pid := int(ch.get("pid", 0))
	var nm := "A racer"
	for i in range(pl.size() - 1, -1, -1):
		if int(pl[i]["id"]) == pid and pid > 0:
			nm = String(pl[i]["name"])
			pl.remove_at(i)
	# a friend who drops mid-race hands their kart to the computer
	if main != null and main.race != null and pid > 0:
		for k in main.race.karts:
			if (k as Kart).peer == pid + 1:
				(k as Kart).web = false
				(k as Kart).remote = false
				(k as Kart).ai["auto"] = true
		if main.state in ["race", "countdown"]:
			main._show_center(nm + " left", 1.6)
	NetLog.ev("leave", pid)
	_lobby_sync()


func _lobby_sync() -> void:
	var lst: Array = []
	for p in pl:
		lst.append({"id": p["id"], "name": p["name"], "ready": p["ready"], "ri": p["ri"]})
	var tk = null
	if main != null and not cfg.is_empty():
		tk = String(main._map_info(main.map_id).get("name", ""))
	for ch in guests_open():
		_send_to(ch, {"t": "lobby", "pl": lst, "you": int(ch["pid"]), "code": code, "tk": tk})
	changed.emit("")


func _player(pid: int) -> Dictionary:
	for p in pl:
		if int(p["id"]) == pid:
			return p
	return {}


func _recv_host(ch: Dictionary, d: Dictionary) -> void:
	var pid := int(ch.get("pid", 0))
	var P := _player(pid)
	match String(d.get("t", "")):
		"hello":
			if int(d.get("v", 0)) != PROTO:
				_send_to(ch, {"t": "full", "why": "You and the host have different versions of the game. Both close the game, open it again so it updates, then try again."})
				ch["closing"] = _now() + 600
				return
			if not P.is_empty():
				P["name"] = String(d.get("name", P["name"])).substr(0, 14)
			_lobby_sync()
		"pick":
			if not P.is_empty():
				P["ri"] = int(d.get("ri", 0))
				P["build"] = d.get("build")
				P["ready"] = bool(d.get("ready", false))
			_lobby_sync()
		"loaded":
			loaded_ids[pid] = true
			_maybe_go()
		"in":
			if d.get("rk") != null and int(d["rk"]) != rk:
				return
			_take_inputs(pid, d)
		"quit":
			if main != null and main.race != null:
				for k in main.race.karts:
					if (k as Kart).peer == pid + 1:
						(k as Kart).web = false
						(k as Kart).remote = false
						(k as Kart).ai["auto"] = true
			if not P.is_empty():
				P["ready"] = false
			_lobby_sync()
		"bye":
			_drop(ch)
		"pg":
			_send_to(ch, {"t": "po", "ts": d.get("ts", 0)})


func _poll_host(now: int) -> void:
	for f in chans.keys():
		var ch: Dictionary = chans[f]
		if ch.has("closing") and now > int(ch["closing"]):
			_drop(ch)
			continue
		if not bool(ch.get("open", false)):
			continue
		if now - int(ch.get("last_out", 0)) > 1500:
			_send_to(ch, {"t": "hb"})
		var lim := 20000 if (main != null and main.state in ["race", "countdown"]) else 180000
		if now - int(ch.get("last_in", now)) > lim:
			_drop(ch)
	if now - t2 > 2000:
		t2 = now
		if not cfg.is_empty() and not go:
			for ch2 in guests_open():
				if not loaded_ids.has(int(ch2["pid"])):
					_send_to(ch2, {"t": "load", "cfg": cfg})


## the grid: you in slot 4, friends next to you, the computer in the rest (web netBuildCfg)
func _build_cfg(mi: int) -> Dictionary:
	var humans: Array = [{"id": 0, "ri": int(main.sel["ri"]), "build": main._my_build(), "name": name_}]
	for ch in guests_open():
		var P := _player(int(ch["pid"]))
		if not P.is_empty():
			humans.append(P)
	var used := {}
	for h in humans:
		used[int(h["ri"])] = true
	var others: Array = []
	var builds := {}
	for q in main.roster.get("racers", []):
		var ri := int((q as Dictionary).get("ri", 0))
		builds[ri] = (q as Dictionary).get("build", {})
		if not used.has(ri):
			others.append(ri)
	others.shuffle()
	var ks: Array = []
	var taken := {}
	for i in mini(humans.size(), 4):
		var h: Dictionary = humans[i]
		var slot: int = SLOTS[i]
		taken[slot] = true
		var b = h.get("build")
		if not (b is Dictionary) or (b as Dictionary).is_empty():
			b = builds.get(int(h["ri"]), {})
		ks.append({"slot": slot, "ri": int(h["ri"]), "build": b, "who": int(h["id"]), "name": String(h.get("name", ""))})
	for s in 8:
		if taken.has(s):
			continue
		var ri2: int = others.pop_front() if not others.is_empty() else s
		ks.append({"slot": s, "ri": ri2, "build": builds.get(ri2, {}), "who": -1})
	ks.sort_custom(func(a, b): return int(a["slot"]) < int(b["slot"]))
	var cls := String(main.sel["cls"])
	if cls == "reverse":
		cls = "large"
	return {"mi": mi, "cls": cls, "mode": "lss" if String(main.sel.get("mode", "")) == "lss" else "single", "gp": null, "karts": ks}


## start a race for everyone in the room on the track you picked (web netHostStart)
func host_start() -> String:
	if role != "host" or main == null:
		return "Host a room first."
	var info: Dictionary = main._map_info(main.map_id)
	if info.is_empty() or int(info.get("mi", 99)) >= 99:
		return "Pick one of the web game's tracks first."
	cfg = _build_cfg(int(info["mi"]))
	cfg["id"] = rid()
	rk = _rk_of(String(cfg["id"]))
	loaded_ids = {0: true}
	in_q = {}
	in_s = {}
	acks = {}
	sn = 0
	h_sig = ""
	tick_n = 0
	go = false
	for ch in guests_open():
		_send_to(ch, {"t": "load", "cfg": cfg})
	var err: String = main._web_host_load(pc_cfg(cfg))
	if err != "":
		cfg = {}
		return err
	_lobby_sync()
	_maybe_go()
	return ""


func _maybe_go() -> void:
	if role != "host" or cfg.is_empty() or go:
		return
	for ch in guests_open():
		if not loaded_ids.has(int(ch["pid"])):
			return
	go = true
	for ch2 in guests_open():
		_send_to(ch2, {"t": "go"})
	if main != null:
		main._web_go()


## back to the room after a race (web toMenu: netAll menu)
func host_menu() -> void:
	if role != "host":
		return
	cfg = {}
	go = false
	for ch in guests_open():
		_send_to(ch, {"t": "menu"})
	_lobby_sync()


func _take_inputs(pid: int, d: Dictionary) -> void:
	var q: Array = in_q.get(pid, [])
	in_q[pid] = q
	var done := int(acks.get(pid, 0))
	var A: Array = []
	if d.get("a") is Array:
		A = d["a"]
	else:
		var s0 := int(d.get("s", 0))
		var v: Array = d.get("v", [])
		for i in v.size():
			var n := int(v[i])
			A.append([s0 + i, float(floori(n / 8.0) - 100) / 100.0, (n >> 1) & 1, 0, 0, n & 1, (n >> 2) & 1])
		for x in d.get("x", []):
			var xi := int(x[0])
			if xi >= 0 and xi < A.size():
				A[xi][3] = x[1]
				A[xi][4] = x[2]
	for e in A:
		var sq := int(e[0])
		if sq <= done:
			continue
		var last := int(q[q.size() - 1][0]) if not q.is_empty() else 0
		if sq > last:
			q.append(e)
		else:
			var have := false
			for y in q:
				if int(y[0]) == sq:
					have = true
					break
			if not have:
				q.append(e)
				q.sort_custom(func(a, b): return int(a[0]) < int(b[0]))


## how many of a friend's controls to play this step: a small buffer sized to the link's jitter absorbs bursts (web netSteps)
func _steps(pid: int) -> int:
	var q: Array = in_q.get(pid, [])
	in_q[pid] = q
	if not in_s.has(pid):
		in_s[pid] = {"wait": true, "T": 6, "ok": 0, "gap": 0}
	var st: Dictionary = in_s[pid]
	var lo := 4
	var hi := 32
	st["T"] = clampi(int(st["T"]), lo, hi)
	if q.size() > 720:
		q = q.slice(q.size() - int(st["T"]))
		in_q[pid] = q
	var nx := int(acks.get(pid, 0)) + 1
	if not q.is_empty() and int(q[0][0]) > nx:
		if int(st["gap"]) == 0:
			st["gap"] = _now()
		if _now() - int(st["gap"]) < 400 and q.size() < int(st["T"]) * 3 + 30:
			return 0
	st["gap"] = 0
	if bool(st["wait"]):
		if q.size() < int(st["T"]):
			return 0
		st["wait"] = false
	if q.is_empty():
		st["wait"] = true
		st["T"] = mini(hi, int(st["T"]) + 1)
		st["ok"] = 0
		return 0
	st["ok"] = int(st["ok"]) + 1
	if int(st["ok"]) > 600 and int(st["T"]) > lo:
		st["T"] = int(st["T"]) - 1
		st["ok"] = 0
	return 4 if q.size() > 120 else (3 if q.size() > 40 else (2 if q.size() > int(st["T"]) * 2 + 4 else 1))


## before each race step: queue every friend's controls for their kart
func host_pre() -> void:
	if main == null or main.race == null or main.state != "race":
		return
	for k in main.race.karts:
		var kk: Kart = k
		if not kk.web or not kk.remote:
			continue
		var pid := kk.peer - 1
		var n := _steps(pid)
		var q: Array = in_q.get(pid, [])
		for i in n:
			while q.size() > 1 and int(q[0][0]) <= int(acks.get(pid, 0)):
				q.pop_front()
			if q.is_empty():
				break
			var e: Array = q.pop_front()
			acks[pid] = int(e[0])
			NetLog.got_input(pid + 1)
			kk.web_q.append([float(e[1]), int(e[2]) != 0, int(e[6]) != 0, 0.0 if int(e[5]) == 0 else 1.0, String(e[3]) if e[3] is String else "", int(e[4]) if not (e[4] is String) else 0])


## after each race step: tell a friend at once when their kart was hit, and send everyone a picture 20 times a second
func host_post() -> void:
	if main == null or main.race == null:
		return
	if main.state == "race":
		_hit_push()
	tick_n += 1
	if tick_n % 6 == 0:
		_snapshot()


func _sig(k: Kart) -> int:
	return (1 if k.spin > 0.0 else 0) | (2 if k.flat_t > 0.0 else 0) | (4 if k.frozen > 0.0 else 0) | (8 if k.oil_t > 0.0 else 0) | (16 if k.shrink_t > 0.0 else 0) | (32 if k.sauce_t > 0.0 else 0) | (128 if k.burn_t > 0.0 else 0)


var _hit := {}


func _hit_push() -> void:
	for k in main.race.karts:
		var kk: Kart = k
		if not kk.web or not kk.remote or kk.finished:
			continue
		var sg := _sig(kk)
		var was: Array = _hit.get(kk, [0, 0.0])
		var dropped: bool = float(was[1]) > 80.0 and kk.speed < float(was[1]) * 0.55
		_hit[kk] = [sg, kk.speed]
		if (sg & ~int(was[0])) != 0 or dropped:
			for ch in guests_open():
				if int(ch["pid"]) == kk.peer - 1:
					_send_to(ch, {"t": "hit", "rk": rk, "me": _scal(kk), "ack": int(acks.get(kk.peer - 1, 0))})
					NetLog.ev("hit-push", kk.peer - 1)


static func _r3(v) -> Variant:
	if v is float:
		return snappedf(v, 0.01)
	return v


static func _r5(v) -> Variant:
	if v is float:
		return snappedf(v, 0.00001)
	return v


## one kart field, the web's name, from ours
func _val(k: Kart, f: String) -> Variant:
	var m := _field(f)
	if m.is_empty():
		return null if f in ZN else (false if f in ZB else 0)
	var v = k.get(String(m[0]))
	if f in ["item", "item2"] and String(v) == "":
		return null
	if f in ZN and (v is float or v is int) and float(v) == 0.0:
		return null
	return v


func _rem(k: Kart) -> Array:
	var v: Array = []
	for f in REM:
		v.append(_r3(_val(k, f)))
	var o := v.slice(0, 8)
	for j in range(8, v.size()):
		var z = false if REM[j] in ZB else (null if REM[j] in ZN else 0)
		if v[j] != z and not (v[j] is float and z is int and float(v[j]) == float(z)):
			o.append(j)
			o.append(v[j])
	var li := _loop_i(k)
	return [o, li, String(k.held.get("it", "")) if not k.held.is_empty() else null, [snappedf(float(k.loop.get("th", 0.0)), 0.01), snappedf(float(k.loop.get("lat0", 0.0)), 0.01)] if not k.loop.is_empty() else null]


func _loop_i(k: Kart) -> int:
	if k.loop.is_empty():
		return -1
	var T: TrackData = main.T
	for i in T.loops.size():
		if int(T.loops[i]["j"]) == int(k.loop.get("j", -9)):
			return i
	return -1


## everything a friend's own screen needs to put their kart exactly where the host has it (web netKScal)
func _scal(k: Kart) -> Dictionary:
	var o := {}
	for f in SCAL:
		var m := _field(f)
		if m.is_empty():
			continue
		var v = k.get(String(m[0]))
		if f in ["item", "item2"] and String(v) == "":
			v = null
		o[f] = _r5(v)
	o["pend"] = Array(k.pend)
	o["loopI"] = _loop_i(k)
	o["loopT"] = snappedf(float(k.loop.get("th", 0.0)), 0.00001) if not k.loop.is_empty() else 0
	o["loopL"] = snappedf(float(k.loop.get("lat0", 0.0)), 0.00001) if not k.loop.is_empty() else 0
	o["scK"] = k.sc
	o["heldIt"] = String(k.held.get("it", "")) if not k.held.is_empty() else null
	o["heldSl"] = int(k.held.get("sl", 0)) if not k.held.is_empty() else 0
	return o


func _snapshot() -> void:
	var race: Race = main.race
	var T: TrackData = main.T
	sn += 1
	var gs := "countdown" if main.state == "countdown" else ("results" if main.state == "results" else "race")
	var kc: Array = []
	for k in race.karts:
		kc.append(_rem(k))
	var pp: Array = []
	for p in race.projectiles:
		var pd: Dictionary = p
		var x := float(pd["x"])
		var y := float(pd["y"])
		var ow = pd.get("owner")
		var tg = pd.get("target")
		pp.append([int(pd["id"]), String(pd["type"]), snappedf(x, 0.01), snappedf(T.ground(x, y) + 4.0, 0.01), snappedf(y, 0.01), 0, 0, 0, 1, 1, String(pd["type"]),
			snappedf(float(pd.get("vx", 0.0)), 0.01), snappedf(float(pd.get("vy", 0.0)), 0.01), race.karts.find(tg) if tg != null else -1, race.karts.find(ow) if ow != null else -1, snappedf(x, 0.01), snappedf(y, 0.01)])
	var bx: Array = []
	var bi := 0
	for tb in T.boxes:
		if bool((tb as Dictionary).get("train", false)):
			bx.append(0)
			continue
		var r := float(race.boxes[bi]["r"]) if bi < race.boxes.size() else 0.0
		bx.append(roundi(r * 20.0) if r > 0.0 else 0)
		bi += 1
	var base := {"t": "s", "n": sn, "rk": rk, "st": snappedf(race.sim_time, 0.01), "rt": snappedf(race.race_time, 0.01), "gs": gs, "kc": kc, "p": pp, "b": bx, "fx": []}
	var ids := PackedStringArray()
	for h in race.hazards:
		ids.append(str(h["id"]))
	var hs := ",".join(ids)
	if hs != h_sig or sn % 3 == 0:
		h_sig = hs
		var hz: Array = []
		for h in race.hazards:
			var hd: Dictionary = h
			var kind := "olive" if bool(hd.get("olive", false)) else String(hd.get("kind", "oil"))
			var x2 := float(hd["x"])
			var y2 := float(hd["y"])
			hz.append([int(hd["id"]), "oil" if kind == "olive" else kind, snappedf(x2, 0.01), snappedf(T.ground(x2, y2), 0.01), snappedf(y2, 0.01), 0, 0, 0, 1, 1, kind,
				race.karts.find(hd.get("owner")) if hd.get("owner") != null else -1, 1, snappedf(x2, 0.01), snappedf(y2, 0.01)])
		base["h"] = hz
	NetLog.sent_snap(guests_open().map(func(c): return int(c["pid"]) + 1))
	for ch in guests_open():
		var pid := int(ch["pid"])
		var mine: Kart = null
		for k in race.karts:
			if (k as Kart).peer == pid + 1:
				mine = k
		var o := base.duplicate()
		o["mi"] = race.karts.find(mine) if mine != null else -1
		o["ack"] = int(acks.get(pid, 0))
		o["sd"] = 1
		if mine != null:
			o["me"] = _scal(mine)
		_send_to(ch, o)
