class_name WebNet
extends Node
## Cross-play with the browser version (web NET, protocol 97). The web game finds friends and races through public MQTT
## brokers (a room code is a topic; every player listens on a topic of their own), so a PC speaking the same messages can
## join a room a browser made. Joining works like the web's: the host runs the real race; this PC drives its own kart
## straight away from your controls, sends them numbered to the host, and when the host's copy of the kart comes back it
## takes that and replays the controls the host hasn't seen yet, so steering is instant. Everything else is drawn as the
## host sends it. PC-to-PC races (ENet) are separate and unchanged.

const PROTO := 109
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
var pend_map := ""        # hosting: the track picked for the next race (web NET.pendMap), "" while choosing
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
var hz0 := false            # the hazards' clock has its start from the host
var world_hit := false      # this step a roller, a walker or the train got your kart (on your own screen)
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
	# a direct link (WebRTC) carries everything once it's open: race pictures, controls and hits on the fast channel
	# (a lost packet is skipped, the next one has fresh data), the rest on the ordered one; the relay is the fallback
	if not raw and _rtc_send(ch, m):
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
	_rtc_poll(now)
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
	_rtc_guest_tick(now)
	if now - int(chan.get("last_out", 0)) > 1500:
		_send({"t": "hb"})
	# 20 s of silence ends a race in progress; while anyone is still loading the track (a browser can go quiet for a
	# long while building it) the web's 3 minutes apply
	var lim := 20000 if (go and main != null and main.state in ["race", "countdown"] and not host_away) else 180000
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
	_rtc_turn()
	rtc_n = 0
	rtc_next = 0
	knock_room = TOP + "r/" + code
	knock_until = _now() + 40000
	knock_next = 0
	changed.emit("Looking for room %s… This can take a few seconds." % code)


func _on_open() -> void:
	_send({"t": "hello", "name": name_, "v": PROTO})
	# as on the web: in the room first, then choose a driver and kart and tap Ready
	ready_ = false
	_send_pick()
	changed.emit("")


## the guest is done in the garage (or goes back to change): tell the host
func set_ready(r: bool) -> void:
	ready_ = r
	_send_pick()
	changed.emit("")


## hosting: everyone in the room has tapped Ready
func all_ready() -> bool:
	for p in pl:
		if int(p["id"]) != 0 and not bool(p.get("ready", false)):
			return false
	return true


func _send_pick() -> void:
	if role != "guest" or chan.is_empty() or main == null:
		return
	_send({"t": "pick", "ri": int(main.sel["ri"]), "build": KartBuilder.web_build(main._my_build()), "ready": ready_})


func leave(tell := true) -> void:
	if role == "guest" and tell and not chan.is_empty():
		_send({"t": "bye"})
	if role == "host" and tell:
		for f in chans:
			_send_to(chans[f], {"f": my_id, "c": "bye"}, false, true)
	for f in chans:
		_rtc_close(chans[f])
	_rtc_close(chan)
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
	pend_map = ""
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
		"tst":
			# the host says one of your items or traps got someone (web hitNote)
			if (d.get("rk") == null or int(d["rk"]) == rk) and main != null and main.state == "race" and main.race != null:
				var vi := int(d.get("v", -1))
				if vi >= 0 and vi < main.race.karts.size():
					main.show_hit_toast(String(d.get("ty", "")), main.race.karts[vi])
		"rtc":
			_rtc_answer(d)
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
	hz0 = false
	world_hit = false
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
		var bd = kd.get("build", {})
		if who == me and role == "guest":
			bd = main._my_build()   # the host was sent the web stand-in for a PC-only livery: this PC draws its own
		slots[s] = {"ri": int(kd.get("ri", 0)), "peer": who + 1 if who >= 0 else 0, "own": who == me, "build": bd, "name": String(kd.get("name", ""))}
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
	# (the clock's reading and whether a roller, a walker or the train got this kart, with the control they go with)
	hist.append([seq, i2, main.race.sim_time, world_hit])
	world_hit = false
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
	var nfx: int = main.race.fx.size()
	for h in hist:
		k.step(h[1], STEP)
		if h.size() > 3 and bool(h[3]):
			main.race.spin_out(k, "meat", true)     # the world hit this side already showed: the host will find the same
	main.race.fx.resize(nfx)
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
	# the shared clock (rollers, traffic, the train, walkers; web the same). It runs a little ahead of the host's, by
	# exactly the time this PC's controls take to be played there: the host says which control it played last (ack) and
	# what its clock read then, and this side knows what its own clock read when it made that control. The two are kept
	# equal, so the world you drive through is the world the host tests your kart against.
	var st := float(d.get("st", 0.0))
	var he_st := -1.0
	if main.state == "race" and mine != null and not mine.finished and d.get("ack") != null:
		var ak := int(d["ack"])
		for h in hist:
			if int(h[0]) == ak:
				he_st = float(h[2]) if h.size() > 2 else -1.0
				break
	if he_st >= 0.0:
		var e := st - he_st
		race.sim_time += e if absf(e) > 0.3 else e * 0.1
	elif absf(race.sim_time - st) > 0.12:
		race.sim_time = st
	if host_gs == "countdown":
		race.haz_t0 = st
		hz0 = true
	elif host_gs == "race" and not hz0:
		race.haz_t0 = st - float(d.get("rt", 0.0))
		hz0 = true
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
			var hd := {"id": int(r[0]), "x": float(r[13]) if r.size() > 14 else float(r[2]), "y": float(r[14]) if r.size() > 14 else float(r[4]), "t": 9.0, "born": 1.0,
				"armed": r.size() <= 14 or int(r[12]) != 0, "owner": race.karts[int(r[11])] if r.size() > 14 and r[11] != null and int(r[11]) >= 0 and int(r[11]) < race.karts.size() else null}
			hd["ny"] = float(r[3]) - 0.12   # the height the host drew it at: the road it lies on
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
	# the route: "peer" when every link is direct (a host with browser friends counts each), "relay" otherwise
	var direct := _dc_open(chan.get("dc")) if role == "guest" else not chans.is_empty()
	if role == "host":
		for f in chans:
			direct = direct and _dc_open((chans[f] as Dictionary).get("dc"))
	var o := {"rtt": roundi(maxf(0.0, ping_ms)), "out": bytes_out, "in": bytes_in, "fixes": fixes, "route": "peer" if direct else "relay"}
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
	_rtc_turn()
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
	_rtc_close(ch)
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
	if main != null and pend_map != "":
		tk = String(main._map_info(pend_map).get("name", ""))
	elif main != null and not cfg.is_empty():
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
		"rtc":
			_rtc_host(ch, d)


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
		var lim := 20000 if (go and main != null and main.state in ["race", "countdown"]) else 180000
		if now - int(ch.get("last_in", now)) > lim:
			_drop(ch)
	if now - t2 > 2000:
		t2 = now
		if not cfg.is_empty() and not go:
			for ch2 in guests_open():
				if not loaded_ids.has(int(ch2["pid"])):
					_send_to(ch2, {"t": "load", "cfg": _wire_cfg(cfg)})


## the race set-up as the browsers get it: the PC's own liveries swapped for their nearest web ones
func _wire_cfg(c: Dictionary) -> Dictionary:
	var o := c.duplicate(true)
	for kq in o.get("karts", []):
		if kq is Dictionary and (kq as Dictionary).has("build"):
			(kq as Dictionary)["build"] = KartBuilder.web_build((kq as Dictionary)["build"])
	return o


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
	var info: Dictionary = main._map_info(pend_map if pend_map != "" else main.map_id)
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
		_send_to(ch, {"t": "load", "cfg": _wire_cfg(cfg)})
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
	var n := 4 if q.size() > 120 else (3 if q.size() > 40 else (2 if q.size() > int(st["T"]) * 2 + 4 else 1))
	# more waiting than the buffer needs (left over from a slow moment, a burst over the relay): play it down gently, an
	# extra control every sixth step, so a friend's controls don't stay a quarter second late for the rest of the race
	if n == 1 and q.size() > int(st["T"]) + 3:
		st["dr"] = int(st.get("dr", 0)) + 1
		if int(st["dr"]) % 6 == 0:
			return 2
	return n


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


## hosting: tell a browser friend that their item or trap got someone, so their screen shows it (web hitNote)
func send_toast(by: Kart, ty: String, vi: int) -> void:
	if vi < 0:
		return
	for ch in guests_open():
		if int(ch["pid"]) == by.peer - 1:
			_send_to(ch, {"t": "tst", "rk": rk, "ty": ty, "v": vi})


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
			hz.append([int(hd["id"]), "oil" if kind == "olive" else kind, snappedf(x2, 0.01), snappedf(race.haz_ground(hd) + 0.12, 0.01), snappedf(y2, 0.01), 0, 0, 0, 1, 1, kind,
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


# ---------------------------------------------------------------- direct links (the web's rtc*: WebRTC data channels)

## As the browser game does: once two players are in a room through the relay, the guest offers a direct WebRTC link
## (two data channels: "race", ordered, and "fast", unordered with no resends), set up through the relay itself in
## one message each way with every route already in it. On the same network the two talk straight to each other;
## across the internet the STUN servers find a route, and where none exists (carrier NAT on phones) a TURN server
## relays the link. When it opens, everything goes over it; if it never opens, the race runs on the relay as before.
## Needs the WebRTC add-on (addons/webrtc_native, fetched by the PC build); without it this stays switched off.
const RTC_STUN := [{"urls": ["stun:stun.l.google.com:19302", "stun:stun1.l.google.com:19302"]}, {"urls": ["stun:stun.cloudflare.com:3478"]}]
## Metered's credential-scoped key, meant for front-end use: it only fetches the TURN server list (web TURN_URL)
const TURN_URL := "https://crustrush.metered.live/api/v1/turn/credentials?apiKey=78d3e88ec5b76283810039412758f32e2c5a"
static var _turn: Array = []
static var _turn_at := -100000000
static var _rtc_avail := -1
var _turn_req: HTTPRequest = null
var rtc_n := 0
var rtc_next := 0
var _mdns: Array = []      # lookups of a browser's hidden local address (Mdns): the direct route on the same Wi-Fi


static func rtc_available() -> bool:
	if _rtc_avail < 0:
		_rtc_avail = 0
		if OS.get_environment("CR_NO_RTC") == "" and ClassDB.class_exists("WebRTCPeerConnection"):
			var p := WebRTCPeerConnection.new()
			if p.initialize({}) == OK:
				_rtc_avail = 1
			p.close()
	return _rtc_avail == 1


static func _dc_open(dc) -> bool:
	return dc is WebRTCDataChannel and (dc as WebRTCDataChannel).get_ready_state() == WebRTCDataChannel.STATE_OPEN


func _rtc_ice() -> Array:
	var a: Array = RTC_STUN.duplicate(true)
	for t in _turn:
		a.append(t)
	return a


## the TURN server list (kept 20 minutes), fetched as soon as a room opens so it's there when the offer is made
func _rtc_turn() -> void:
	if not rtc_available() or _turn_req != null or Time.get_ticks_msec() - _turn_at < 20 * 60000:
		return
	_turn_req = HTTPRequest.new()
	_turn_req.timeout = 4.0
	add_child(_turn_req)
	_turn_req.request_completed.connect(_turn_done)
	if _turn_req.request(TURN_URL) != OK:
		_turn_req.queue_free()
		_turn_req = null


func _turn_done(res: int, code_: int, _h: PackedStringArray, body: PackedByteArray) -> void:
	if res == HTTPRequest.RESULT_SUCCESS and code_ == 200:
		var j = JSON.parse_string(body.get_string_from_utf8())
		if j is Array:
			var out: Array = []
			for x in j:
				if x is Dictionary and str(x.get("urls", "")).find("turn") >= 0:
					var u = x["urls"]
					out.append({"urls": u if u is Array else [str(u)], "username": str(x.get("username", "")), "credential": str(x.get("credential", ""))})
			_turn = out
			_turn_at = Time.get_ticks_msec()
	if _turn_req != null:
		_turn_req.queue_free()
		_turn_req = null


## a fresh peer connection for a link; its description and routes are collected for the one setup message
func _rtc_new(ch: Dictionary, id) -> Dictionary:
	_rtc_close(ch)
	var pc := WebRTCPeerConnection.new()
	if pc.initialize({"iceServers": _rtc_ice()}) != OK:
		return {}
	var st := {"pc": pc, "id": id, "desc": "", "dtype": "", "cands": [], "t0": _now(), "sent": false, "t_sent": 0, "srflx": 0, "relay": 0, "answered": false}
	pc.session_description_created.connect(func(tp: String, sdp: String):
		pc.set_local_description(tp, sdp)
		st["desc"] = sdp
		st["dtype"] = tp)
	pc.ice_candidate_created.connect(func(mid: String, _i: int, cand: String):
		(st["cands"] as Array).append([mid, cand])
		if cand.find(" typ srflx") >= 0 and int(st["srflx"]) == 0:
			st["srflx"] = _now()
		if cand.find(" typ relay") >= 0 and int(st["relay"]) == 0:
			st["relay"] = _now())
	pc.data_channel_received.connect(func(dc: WebRTCDataChannel): _rtc_dc(ch, dc))
	ch["rtc"] = st
	return st


func _rtc_dc(ch: Dictionary, dc: WebRTCDataChannel) -> void:
	dc.write_mode = WebRTCDataChannel.WRITE_MODE_TEXT
	ch["dcF" if dc.get_label() == "fast" else "dc"] = dc


func _rtc_close(ch: Dictionary) -> void:
	if ch.is_empty():
		return
	for key in ["dc", "dcF"]:
		var dc = ch.get(key)
		if dc is WebRTCDataChannel:
			(dc as WebRTCDataChannel).close()
		ch.erase(key)
	var st = ch.get("rtc")
	if st is Dictionary and (st as Dictionary).get("pc") is WebRTCPeerConnection:
		var pc := (st as Dictionary)["pc"] as WebRTCPeerConnection
		pc.close()
		# the handlers hold the connection, and a connection never let go keeps the game from closing
		for sig in ["session_description_created", "ice_candidate_created", "data_channel_received"]:
			for c in pc.get_signal_connection_list(sig):
				pc.disconnect(sig, c["callable"])
		(st as Dictionary).erase("pc")
	ch.erase("rtc")
	for key in ["dc_up", "dcF_up"]:
		ch.erase(key)


func _exit_tree() -> void:
	for q in _mdns:
		for sk in q["socks"]:
			(sk[0] as PacketPeerUDP).close()
	_mdns.clear()
	for f in chans:
		_rtc_close(chans[f])
	_rtc_close(chan)


## the description with every route gathered so far written into it (the web sends one complete message each way)
static func _sdp_with(desc: String, cands: Array) -> String:
	var lines := desc.replace("\r\n", "\n").split("\n", false)
	var out := PackedStringArray()
	var mid := ""
	var in_media := false
	var flush := func(m: String) -> void:
		for c in cands:
			if String(c[0]) == m or m == "":
				var line := String(c[1])
				out.append(line if line.begins_with("a=") else "a=" + line)
		out.append("a=end-of-candidates")
	for ln in lines:
		if ln.begins_with("a=end-of-candidates") or ln.begins_with("a=candidate:"):
			continue
		if ln.begins_with("m="):
			if in_media:
				flush.call(mid)
			in_media = true
			mid = ""
		elif ln.begins_with("a=mid:"):
			mid = ln.substr(6)
		out.append(ln)
	if in_media:
		flush.call(mid)
	return "\r\n".join(out) + "\r\n"


## like the web's rtcGather: a public-address route is always waited for; both it and a TURN route, half a second more
static func _rtc_ready(st: Dictionary, now: int) -> bool:
	if String(st["desc"]) == "":
		return false
	var el := now - int(st["t0"])
	var pc: WebRTCPeerConnection = st["pc"]
	if pc.get_gathering_state() == WebRTCPeerConnection.GATHERING_STATE_COMPLETE:
		return true
	var sx := int(st["srflx"])
	var rl := int(st["relay"])
	if sx > 0 and rl > 0:
		return now - maxi(sx, rl) > 500 or el > 4000
	if sx > 0:
		return el > 1600
	if rl > 0:
		return el > 1800
	return el > (4000 if not _turn.is_empty() else 2500)


func _rtc_send(ch: Dictionary, m: Dictionary) -> bool:
	var t := String(m.get("t", ""))
	var dc = ch.get("dcF") if (t == "s" or t == "in" or t == "hit") and _dc_open(ch.get("dcF")) else ch.get("dc")
	if not _dc_open(dc):
		return false
	var s := JSON.stringify(m)
	if (dc as WebRTCDataChannel).put_packet(s.to_utf8_buffer()) != OK:
		return false
	bytes_out += s.length()
	ch["last_out"] = _now()
	return true


## every frame: the peer connections, the setup message when its routes are in, and what came over the links
func _rtc_poll(now: int) -> void:
	if _rtc_avail != 1:
		return
	if not _mdns.is_empty():
		_mdns_poll(now)
	var links: Array = chans.values() if role == "host" else ([chan] if not chan.is_empty() else [])
	for ch in links:
		var st = (ch as Dictionary).get("rtc")
		if not (st is Dictionary) or not ((st as Dictionary).get("pc") is WebRTCPeerConnection):
			continue
		var pc: WebRTCPeerConnection = st["pc"]
		pc.poll()
		if not bool(st["sent"]) and _rtc_ready(st, now):
			st["sent"] = true
			st["t_sent"] = now
			_send_to(ch, {"t": "rtc", "id": st["id"], "nat": "?", "sdp": {"type": String(st["dtype"]), "sdp": _sdp_with(String(st["desc"]), st["cands"])}})
		for key in ["dc", "dcF"]:
			var dc = (ch as Dictionary).get(key)
			if not (dc is WebRTCDataChannel):
				continue
			var d2 := dc as WebRTCDataChannel
			d2.poll()
			if d2.get_ready_state() == WebRTCDataChannel.STATE_OPEN and not bool((ch as Dictionary).get(key + "_up", false)):
				(ch as Dictionary)[key + "_up"] = true
				if key == "dc":
					NetLog.ev("direct-up", int((ch as Dictionary).get("pid", 0)))
					print("WEBNET direct link up (%s)" % role)
			while d2.get_available_packet_count() > 0:
				var pk := d2.get_packet()
				var j = JSON.parse_string(pk.get_string_from_utf8())
				if not (j is Dictionary):
					continue
				bytes_in += pk.size()
				(ch as Dictionary)["last_in"] = now
				if role == "host":
					if chans.has(String((ch as Dictionary)["peer"])):
						_recv_host(ch, j)
				else:
					_recv(j)
				if (role == "host" and not chans.has(String((ch as Dictionary)["peer"]))) or (role == "guest" and chan.is_empty()):
					return


## guest: offer a direct link, again every few seconds until one opens (up to 12 tries, as the web's rtcGuestStart)
func _rtc_guest_tick(now: int) -> void:
	if not rtc_available() or chan.is_empty() or _dc_open(chan.get("dc")):
		return
	var st = chan.get("rtc")
	if st is Dictionary:
		var pc: WebRTCPeerConnection = st["pc"]
		var cs := pc.get_connection_state()
		if cs == WebRTCPeerConnection.STATE_CONNECTED:
			return
		if bool(st["answered"]) and now - int(st["t_sent"]) < 14000:
			return     # answered and still finding a route: give it time
		if bool(st["sent"]) and not bool(st["answered"]) and now - int(st["t_sent"]) < 9000:
			return     # the answer is on its way over the relay (the host gathers its routes too)
		if not bool(st["sent"]) and now - int(st["t0"]) < 9000:
			return     # still gathering routes for this offer
	if now < rtc_next or rtc_n >= 12:
		return
	rtc_n += 1
	rtc_next = now + 3000
	var st2 := _rtc_new(chan, rtc_n)
	if st2.is_empty():
		return
	var pc2: WebRTCPeerConnection = st2["pc"]
	var dc := pc2.create_data_channel("race", {"ordered": true})
	var dcf := pc2.create_data_channel("fast", {"ordered": false, "maxRetransmits": 0})
	if dc != null:
		_rtc_dc(chan, dc)
	if dcf != null:
		_rtc_dc(chan, dcf)
	pc2.create_offer()


## guest: the host's answer to our offer
func _rtc_answer(d: Dictionary) -> void:
	var st = chan.get("rtc")
	if not (st is Dictionary) or d.get("id") == null or int(d["id"]) != int(st["id"]) or bool(st["answered"]):
		return
	var sdp = d.get("sdp")
	if not (sdp is Dictionary) or String(sdp.get("type", "")) != "answer":
		return
	st["answered"] = true
	st["t_sent"] = _now()
	(st["pc"] as WebRTCPeerConnection).set_remote_description("answer", String(sdp.get("sdp", "")))
	_mdns_start(st, String(sdp.get("sdp", "")))


## host: a browser guest offers a direct link; answer it (the answer is made as the offer is set)
func _rtc_host(ch: Dictionary, d: Dictionary) -> void:
	if not rtc_available() or _dc_open(ch.get("dc")):
		return
	var sdp = d.get("sdp")
	if not (sdp is Dictionary) or String(sdp.get("type", "")) != "offer":
		return
	var st := _rtc_new(ch, d.get("id"))
	if st.is_empty():
		return
	(st["pc"] as WebRTCPeerConnection).set_remote_description("offer", String(sdp.get("sdp", "")))
	_mdns_start(st, String(sdp.get("sdp", "")))


## the browser's local address is hidden behind a made-up name (xxxx.local) that libdatachannel can't look up on
## Windows, so on the same Wi-Fi only the TURN relay was left: ask the local network for each name (Mdns) and give
## the link the real address. Nothing else changes: the relay and TURN routes are still there if this finds nothing.
func _mdns_start(st: Dictionary, sdp: String) -> void:
	var by := {}
	for h in Mdns.hidden(sdp):
		var hn := String(h[3]).to_lower()
		if not by.has(hn):
			by[hn] = []
		(by[hn] as Array).append(h)
	if by.is_empty():
		return
	var addrs := Mdns.local_ipv4()
	for hn in by:
		# one socket per local network (a PC with a VPN or a virtual adapter has several; the question has to go out on
		# the Wi-Fi or Ethernet one): each sends the multicast question and, as a fallback, the same to its /24 broadcast
		var socks: Array = []
		for la in (addrs if not addrs.is_empty() else ["0.0.0.0"]):
			var udp := PacketPeerUDP.new()
			if udp.bind(0, String(la)) != OK:
				continue
			udp.set_broadcast_enabled(true)
			socks.append([udp, String(la)])
		if not socks.is_empty():
			_mdns.append({"st": st, "pc": st["pc"], "name": hn, "cands": by[hn], "socks": socks, "t0": _now(), "next": 0, "qid": randi() & 0xFFFF})
	NetLog.ev("mdns-ask", by.size())


func _mdns_poll(now: int) -> void:
	for i in range(_mdns.size() - 1, -1, -1):
		var q: Dictionary = _mdns[i]
		var st: Dictionary = q["st"]
		var live: bool = st.get("pc") == q["pc"]
		var ip := ""
		for sk in q["socks"]:
			var udp: PacketPeerUDP = sk[0]
			while udp.get_available_packet_count() > 0:
				var a := Mdns.parse_a(udp.get_packet(), String(q["name"]))
				if a != "" and not a.begins_with("0.") and not a.begins_with("127."):
					ip = a
		if ip != "" and live:
			var pc: WebRTCPeerConnection = q["pc"]
			for c in q["cands"]:
				pc.add_ice_candidate(String(c[0]), int(c[1]), Mdns.with_ip(String(c[2]), ip))
			NetLog.ev("mdns-found", (q["cands"] as Array).size())
			print("WEBNET local address found for a direct link (%s)" % role)
		if ip != "" or not live or now - int(q["t0"]) > 3500:
			if ip == "" and live:
				NetLog.ev("mdns-none", 1)
			for sk in q["socks"]:
				(sk[0] as PacketPeerUDP).close()
			_mdns.remove_at(i)
			continue
		if now >= int(q["next"]):
			q["next"] = now + 500
			var pk := Mdns.query(String(q["name"]), int(q["qid"]))
			for sk in q["socks"]:
				var udp: PacketPeerUDP = sk[0]
				udp.set_dest_address(Mdns.GROUP, Mdns.PORT)
				udp.put_packet(pk)
				var bc := Mdns.broadcast_of(String(sk[1]))
				if bc != "":
					udp.set_dest_address(bc, Mdns.PORT)
					udp.put_packet(pk)