class_name Mdns
extends RefCounted
## Looks up a browser's hidden local address on the local network (multicast DNS, one question and one answer).
##
## Browsers don't hand out their local Wi-Fi address for a direct link: they write a made-up name in its place
## (1f47...d8bf.local) and answer for that name only on the local network. The PC's WebRTC library can't always
## look such names up (on Windows it usually can't), so on the same Wi-Fi the direct route was never tried and the
## race went through the TURN relay. Asking the network ourselves gives the link the real address.
##
## The question is a "legacy unicast" one (sent from an ordinary port), so the browser's device answers straight
## back to that port (RFC 6762 6.7). Windows' firewall lets such answers in (a reply to a multicast question).

const GROUP := "224.0.0.251"
const PORT := 5353


## the question: the name's A record (its IPv4 address), class IN with the "answer me directly" bit
static func query(name: String, qid: int) -> PackedByteArray:
	var b := PackedByteArray([(qid >> 8) & 255, qid & 255, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0])
	for label in name.trim_suffix(".").split(".", false):
		var u := label.to_utf8_buffer()
		b.append(u.size())
		b.append_array(u)
	b.append(0)
	b.append_array(PackedByteArray([0, 1, 0x80, 1]))
	return b


## a name in a DNS message (labels, possibly pointing back into the message): [name, offset after it] or ["", -1]
static func _name(p: PackedByteArray, off: int) -> Array:
	var labels := PackedStringArray()
	var after := -1
	var guard := 0
	while off < p.size() and guard < 64:
		guard += 1
		var l: int = p[off]
		if l == 0:
			off += 1
			return [".".join(labels), after if after >= 0 else off]
		if (l & 0xC0) == 0xC0:
			if off + 1 >= p.size():
				return ["", -1]
			if after < 0:
				after = off + 2
			off = ((l & 0x3F) << 8) | int(p[off + 1])
			continue
		if off + 1 + l > p.size():
			return ["", -1]
		labels.append(p.slice(off + 1, off + 1 + l).get_string_from_utf8())
		off += 1 + l
	return ["", -1]


## the IPv4 address given for `want` in an answer, or ""
static func parse_a(p: PackedByteArray, want: String) -> String:
	if p.size() < 12 or (int(p[2]) & 0x80) == 0:
		return ""     # not an answer
	var qd := (int(p[4]) << 8) | int(p[5])
	var rr := ((int(p[6]) << 8) | int(p[7])) + ((int(p[8]) << 8) | int(p[9])) + ((int(p[10]) << 8) | int(p[11]))
	var off := 12
	for i in qd:
		var q := _name(p, off)
		off = int(q[1])
		if off < 0:
			return ""
		off += 4
	var w := want.trim_suffix(".").to_lower()
	for i in rr:
		var r := _name(p, off)
		off = int(r[1])
		if off < 0 or off + 10 > p.size():
			return ""
		var typ := (int(p[off]) << 8) | int(p[off + 1])
		var rdl := (int(p[off + 8]) << 8) | int(p[off + 9])
		off += 10
		if off + rdl > p.size():
			return ""
		if typ == 1 and rdl == 4 and String(r[0]).to_lower() == w:
			return "%d.%d.%d.%d" % [p[off], p[off + 1], p[off + 2], p[off + 3]]
		off += rdl
	return ""


## the candidates in a description whose address is such a name: [[mid, m-line index, "candidate:...", name], ...]
static func hidden(sdp: String) -> Array:
	var out: Array = []
	var mid := ""
	var mline := -1
	for ln in sdp.replace("\r\n", "\n").split("\n", false):
		if ln.begins_with("m="):
			mline += 1
			mid = ""
		elif ln.begins_with("a=mid:"):
			mid = ln.substr(6).strip_edges()
		elif ln.begins_with("a=candidate:"):
			var tk := ln.strip_edges().split(" ")
			if tk.size() > 7 and tk[4].to_lower().ends_with(".local") and tk[2].to_lower() == "udp":
				out.append([mid, maxi(mline, 0), ln.strip_edges().substr(2), tk[4]])
	return out


## the same candidate with the real address in place of the name
static func with_ip(cand: String, ip: String) -> String:
	var tk := cand.split(" ")
	if tk.size() > 4:
		tk[4] = ip
	return " ".join(tk)


## this PC's addresses on local networks (home Wi-Fi and Ethernet ranges), at most four
static func local_ipv4() -> Array:
	var out: Array = []
	for a in IP.get_local_addresses():
		var s := String(a)
		if s.count(".") != 3:
			continue
		var p := s.split(".")
		var b := int(p[1])
		if p[0] == "10" or (p[0] == "192" and p[1] == "168") or (p[0] == "172" and b >= 16 and b <= 31):
			if not out.has(s):
				out.append(s)
	return out.slice(0, 4)


## the usual broadcast address of a home network address (its /24), or "" for an address that isn't one
static func broadcast_of(addr: String) -> String:
	var p := addr.split(".")
	if p.size() != 4 or addr == "0.0.0.0":
		return ""
	return "%s.%s.%s.255" % [p[0], p[1], p[2]]
