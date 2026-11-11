class_name NetLog
## The network log (web NETLOG): a row every second of an online race (round trip, lost packets, snapshot flow,
## frame rate, data in and out) plus events, saved for the last 6 races so a laggy race can be read back afterwards
## (Settings > More > Network log, with Copy). Reading only: nothing here changes the race.

const PATH := "user://netlog.json"
const KEEP := 6

static var on := false
static var rows: Array = []
static var evs: Array = []
static var t0 := 0
static var last := 0
static var role := ""
static var map_id := ""
static var quality := ""
static var fps_n := 0
static var fps_t := 0
static var f_t := 0
# counters for the current second
static var snaps := 0          # friend: snapshots received
static var late := 0           # friend: gaps over 100 ms between snapshots
static var snap_at := 0
static var sent := {}          # host: snapshots sent, per friend
static var inputs := {}        # host: control updates received, per friend
static var quiet := false
static var players: Array = []


static func _now() -> int:
	return Time.get_ticks_msec()


static func start(r: String, map: String, q: String, names: Array) -> void:
	players = names.duplicate()
	rows = []
	evs = []
	t0 = _now()
	last = 0
	role = r
	map_id = map
	quality = q
	fps_n = 0
	fps_t = t0
	f_t = 0
	snaps = 0
	late = 0
	snap_at = 0
	sent = {}
	inputs = {}
	quiet = false
	on = true


## an event: (t, kind, detail); the same event again within a second counts up instead
static func ev(kind: String, x = 0) -> void:
	if not on or evs.size() > 400:
		return
	var t := snappedf((_now() - t0) / 1000.0, 0.1)
	if not evs.is_empty():
		var l: Array = evs[evs.size() - 1]
		if String(l[1]) == kind and str(l[2]) == str(x) and t - float(l[0]) < 1.0:
			if l.size() < 4:
				l.append(1)
			l[3] = int(l[3]) + 1
			return
	evs.append([t, kind, x])


## every drawn frame: counts the frame rate, and a gap over 250 ms is logged as a stall with the game's state
static func frame(state: String) -> void:
	if not on:
		return
	fps_n += 1
	var now := _now()
	if f_t > 0 and now - f_t > 250:
		ev("stall", "%s %dms" % [state, now - f_t])
	f_t = now


## friend: a snapshot came in from the host
static func got_snap() -> void:
	if not on:
		return
	var now := _now()
	snaps += 1
	if snap_at > 0 and now - snap_at > 100:
		late += 1
		if now - snap_at > 300:
			ev("late", now - snap_at)
	if quiet:
		quiet = false
		ev("host-back", now - snap_at)
	snap_at = now


static func sent_snap(peers: Array) -> void:
	if not on:
		return
	for id in peers:
		sent[id] = int(sent.get(id, 0)) + 1


static func got_input(id: int) -> void:
	if on:
		inputs[id] = int(inputs.get(id, 0)) + 1


static func _pstat(pp: ENetPacketPeer, s: int) -> float:
	return float(pp.get_statistic(s)) if pp != null else 0.0


## once a second: one row of numbers
static func tick(mp: MultiplayerPeer, peers: Array, web := {}) -> void:
	if not on:
		return
	var now := _now()
	if now - last < 1000:
		return
	last = now
	var t := roundi((now - t0) / 1000.0)
	var fps := roundi(fps_n * 1000.0 / maxf(1.0, float(now - fps_t)))
	fps_n = 0
	fps_t = now
	var kb_out := 0
	var kb_in := 0
	var em := mp as ENetMultiplayerPeer
	if em != null and em.host != null:
		kb_out = roundi(em.host.pop_statistic(ENetConnection.HOST_TOTAL_SENT_DATA) / 1024.0)
		kb_in = roundi(em.host.pop_statistic(ENetConnection.HOST_TOTAL_RECEIVED_DATA) / 1024.0)
	var row: Array
	if not web.is_empty():
		# a browser friend's room (the relay): round trip by ping, big position fixes in place of lost packets
		if snap_at > 0 and now - snap_at > 1000 and not quiet:
			quiet = true
			ev("host-quiet", now - snap_at)
		row = [t, fps, String(web.get("route", "relay")), int(web.get("rtt", 0)), int(web.get("fixes", 0)), 0, snaps, late, roundi(int(web.get("out", 0)) / 1024.0), roundi(int(web.get("in", 0)) / 1024.0)]
		snaps = 0
		late = 0
	elif role == "client":
		var pp: ENetPacketPeer = em.get_peer(1) if em != null else null
		if snap_at > 0 and now - snap_at > 1000 and not quiet:
			quiet = true
			ev("host-quiet", now - snap_at)
		row = [t, fps, "direct", roundi(_pstat(pp, ENetPacketPeer.PEER_ROUND_TRIP_TIME)),
			roundi(_pstat(pp, ENetPacketPeer.PEER_PACKET_LOSS) * 100.0 / ENetPacketPeer.PACKET_LOSS_SCALE),
			roundi(_pstat(pp, ENetPacketPeer.PEER_ROUND_TRIP_TIME_VARIANCE)), snaps, late, kb_out, kb_in]
		snaps = 0
		late = 0
	else:
		row = [t, fps, kb_out, kb_in]
		for id in peers:
			var pp: ENetPacketPeer = em.get_peer(int(id)) if em != null else null
			row.append([int(id), "direct", roundi(_pstat(pp, ENetPacketPeer.PEER_ROUND_TRIP_TIME)), int(sent.get(id, 0)),
				roundi(_pstat(pp, ENetPacketPeer.PEER_PACKET_LOSS) * 100.0 / ENetPacketPeer.PACKET_LOSS_SCALE),
				roundi(_pstat(pp, ENetPacketPeer.PEER_ROUND_TRIP_TIME_VARIANCE)), int(inputs.get(id, 0))])
		sent = {}
		inputs = {}
	rows.append(row)
	if rows.size() > 900:
		stop([])


## the race ended (or was left): saved with the newest first, the last 6 kept. The racers are the ones at the
## start, unless more are known now.
static func stop(names: Array) -> void:
	if not on:
		return
	on = false
	if names.size() > players.size():
		players = names.duplicate()
	var e := {"when": Time.get_datetime_string_from_system(false, true), "map": map_id, "role": "guest" if role == "client" else "host",
		"players": players, "quality": quality, "ua": "PC (%s) Godot %s" % [OS.get_name(), Engine.get_version_info().get("string", "")],
		"secs": roundi((_now() - t0) / 1000.0), "rows": rows, "evs": evs}
	var l := load_all()
	l.push_front(e)
	while l.size() > KEEP:
		l.pop_back()
	var f := FileAccess.open(PATH, FileAccess.WRITE)
	if f != null:
		f.store_string(JSON.stringify(l))


static func load_all() -> Array:
	if not FileAccess.file_exists(PATH):
		return []
	var v = JSON.parse_string(FileAccess.get_file_as_string(PATH))
	return v if v is Array else []


static func clear() -> void:
	if FileAccess.file_exists(PATH):
		DirAccess.remove_absolute(ProjectSettings.globalize_path(PATH))


static func _col(r: Array, i: int) -> Array:
	var out: Array = []
	for q in r:
		if q is Array and (q as Array).size() > i and typeof(q[i]) in [TYPE_INT, TYPE_FLOAT]:
			out.append(float(q[i]))
	return out


static func _mx(a: Array) -> int:
	var m := 0.0
	for x in a:
		m = maxf(m, float(x))
	return roundi(m)


static func _av(a: Array) -> int:
	if a.is_empty():
		return 0
	var s := 0.0
	for x in a:
		s += float(x)
	return roundi(s / a.size())


static func _med(a: Array) -> int:
	if a.is_empty():
		return 0
	var b := a.duplicate()
	b.sort()
	return roundi(float(b[b.size() >> 1]))


static func _sum(a: Array) -> int:
	var s := 0.0
	for x in a:
		s += float(x)
	return roundi(s)


## a readable summary of one saved log (web netLogText), then every row and the events
static func text(e: Dictionary) -> String:
	var g := String(e.get("role", "")) == "guest"
	var r: Array = e.get("rows", [])
	var pl: Array = e.get("players", [])
	var relay := false
	for q in r:
		if q is Array and (q as Array).size() > 2 and str(q[2]) == "relay":
			relay = true
			break
	var h := "Crust Rush network log · %s · %s · %s · %s · %d s · %s\nplayers: %s\ndevice: %s\n" % [
		String(e.get("when", "")).replace("T", " ").substr(0, 16), e.get("map", "?"), e.get("role", "?"), e.get("quality", "?"),
		int(e.get("secs", 0)), "PC in a browser room, through the relay" if relay else "PC, direct connection", ", ".join(PackedStringArray(pl)), e.get("ua", "?")]
	if g and relay:
		var rt2 := _col(r, 3)
		h += "round trip: median %d ms, worst %d ms · big position fixes %d · late snapshots %d · snapshots a second: median %d · fps avg %d\n" % [
			_med(rt2), _mx(rt2), _sum(_col(r, 4)), _sum(_col(r, 7)), _med(_col(r, 6)), _av(_col(r, 1))]
		h += "rows: t fps route rtt fixes - snaps late KBout KBin\n"
	elif g:
		var rt := _col(r, 3)
		var loss := _col(r, 4)
		var lt := _col(r, 7)
		h += "round trip: median %d ms, worst %d ms · lost packets: worst %d%% · late snapshots %d · snapshots a second: median %d · fps avg %d\n" % [
			_med(rt), _mx(rt), _mx(loss), _sum(lt), _med(_col(r, 6)), _av(_col(r, 1))]
		h += "rows: t fps route rtt lossPct jitter snaps late KBout KBin\n"
	else:
		var fr := {}
		for q in r:
			for i in range(4, (q as Array).size()):
				var f: Array = q[i]
				if not fr.has(f[0]):
					fr[f[0]] = {"rt": [], "loss": [], "inp": []}
				fr[f[0]]["rt"].append(float(f[2]))
				fr[f[0]]["loss"].append(float(f[4]))
				fr[f[0]]["inp"].append(float(f[6]))
		for id in fr:
			var o: Dictionary = fr[id]
			h += "friend %d: round trip median %d ms, worst %d ms · lost packets worst %d%% · control updates a second: median %d, lowest %d\n" % [
				int(id), _med(o["rt"]), _mx(o["rt"]), _mx(o["loss"]), _med(o["inp"]), roundi((o["inp"] as Array).min() if not (o["inp"] as Array).is_empty() else 0)]
		h += "fps avg %d\nrows: t fps KBout KBin then per friend [id route rtt snapsSent lossPct jitter controlUpdates]\n" % _av(_col(r, 1))
	var lines := PackedStringArray()
	for q in r:
		lines.append(JSON.stringify(_ints(q)))
	h += "\n".join(lines) + "\nevents (t kind detail count): " + JSON.stringify(_ints(e.get("evs", [])))
	return h


## saved numbers come back as floats: whole ones print as whole numbers again
static func _ints(v):
	if v is Array:
		var out: Array = []
		for x in v:
			out.append(_ints(x))
		return out
	if typeof(v) == TYPE_FLOAT and is_equal_approx(v, roundf(v)) and absf(v) < 1e15:
		return int(v)
	return v
