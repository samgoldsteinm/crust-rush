class_name Mqtt
extends RefCounted
## A minimal MQTT 3.1.1 client over a secure WebSocket (web NetMQ): connect, subscribe, publish (QoS 0), keep-alive and
## automatic reconnects. The web game finds and talks to friends through public MQTT brokers; this lets the PC version
## use the very same ones, so a PC can join a room made in a browser.

var url := ""
var id := ""
var subs := {}
var ok := false
var dead := false
var failed := false        # never connected after several tries
var ever_ok := false
var on_msg: Callable       # (topic: String, text: String, from: Mqtt)
var ws: WebSocketPeer = null
var buf := PackedByteArray()
var pid := 1
var tries := 0
var retry_at := 0
var conn_at := 0
var last_in := 0
var last_ping := 0
var opened := false


func _init(u: String, client_id: String, cb: Callable) -> void:
	url = u
	id = client_id
	on_msg = cb


static func _now() -> int:
	return Time.get_ticks_msec()


func start() -> void:
	_connect()


func _connect() -> void:
	if dead:
		return
	ws = WebSocketPeer.new()
	ws.supported_protocols = PackedStringArray(["mqtt"])
	ws.inbound_buffer_size = 1 << 21
	ws.outbound_buffer_size = 1 << 21
	ws.max_queued_packets = 4096
	opened = false
	ok = false
	buf = PackedByteArray()
	conn_at = _now()
	if ws.connect_to_url(url) != OK:
		_lost()


func _lost() -> void:
	if ws != null:
		ws.close()
	ws = null
	ok = false
	if dead:
		return
	if not ever_ok and tries > 5:
		failed = true
		return
	retry_at = _now() + mini(500 * (1 << mini(tries, 4)), 5000)
	tries += 1


## call every frame: reads what arrived, keeps the link alive, reconnects
func poll() -> void:
	if dead:
		return
	if ws == null:
		if not failed and retry_at > 0 and _now() >= retry_at:
			retry_at = 0
			_connect()
		return
	ws.poll()
	var st := ws.get_ready_state()
	var now := _now()
	if st == WebSocketPeer.STATE_OPEN:
		if not opened:
			opened = true
			_raw(0x10, [PackedByteArray([0, 4, 77, 81, 84, 84, 4, 2, 0, 30]), _str(id)])
		while ws.get_available_packet_count() > 0:
			last_in = now
			_feed(ws.get_packet())
		if not ok and now - conn_at > 9000:
			_lost()
			return
		if ok and now - last_in > 10000 and now - last_ping > 10000:
			last_ping = now
			_raw(0xC0, [])
		if ok and now - last_in > 40000:
			_lost()
	elif st == WebSocketPeer.STATE_CLOSED:
		_lost()
	elif st == WebSocketPeer.STATE_CONNECTING and now - conn_at > 9000:
		_lost()


static func _str(s: String) -> PackedByteArray:
	var b := s.to_utf8_buffer()
	var o := PackedByteArray([b.size() >> 8, b.size() & 255])
	o.append_array(b)
	return o


func _raw(h: int, parts: Array) -> bool:
	if ws == null or ws.get_ready_state() != WebSocketPeer.STATE_OPEN:
		return false
	var n := 0
	for p in parts:
		n += (p as PackedByteArray).size()
	var o := PackedByteArray([h])
	var x := n
	while true:
		var d := x % 128
		x = x / 128
		if x > 0:
			d |= 128
		o.append(d)
		if x == 0:
			break
	for p in parts:
		o.append_array(p)
	return ws.send(o) == OK


func _feed(chunk: PackedByteArray) -> void:
	buf.append_array(chunk)
	var b := buf
	var i := 0
	while true:
		if b.size() - i < 2:
			break
		var ln := 0
		var m := 1
		var j := i + 1
		var c := 0
		var bad := false
		while true:
			if j >= b.size():
				bad = true
				break
			c = b[j]
			j += 1
			ln += (c & 127) * m
			m *= 128
			if (c & 128) == 0:
				break
		if bad or j + ln > b.size():
			break
		var typ := b[i] >> 4
		var qos := (b[i] >> 1) & 3
		var body := b.slice(j, j + ln)
		i = j + ln
		if typ == 2:
			if body.size() > 1 and body[1] == 0:
				ok = true
				ever_ok = true
				tries = 0
				for t in subs:
					_sub_send(String(t))
			else:
				id = "cr-" + WebNet.rid()
				_lost()
				return
		elif typ == 3 and body.size() >= 2:
			var tl := (body[0] << 8) | body[1]
			var topic := body.slice(2, 2 + tl).get_string_from_utf8()
			var p := 2 + tl + (2 if qos > 0 else 0)
			if on_msg.is_valid():
				on_msg.call(topic, body.slice(p).get_string_from_utf8(), self)
	buf = b.slice(i)


func _sub_send(t: String) -> void:
	pid = pid % 65000 + 1
	_raw(0x82, [PackedByteArray([pid >> 8, pid & 255]), _str(t), PackedByteArray([0])])


func sub(t: String) -> void:
	subs[t] = true
	if ok:
		_sub_send(t)


func pub(t: String, s: String) -> bool:
	if not ok:
		return false
	return _raw(0x30, [_str(t), s.to_utf8_buffer()])


## back from a stall: reconnect right away
func kick() -> void:
	if dead:
		return
	if ws == null:
		tries = 0
		failed = false
		_connect()


func close() -> void:
	if ws != null:
		_raw(0xE0, [])
		ws.close()
	ws = null
	ok = false
	dead = true
