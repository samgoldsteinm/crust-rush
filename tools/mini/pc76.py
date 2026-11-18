"""The PC side of web patch 76 (v222): the delivery arrow takes the quickest drivable way (the owner: "make it point to the quickest route
that is driveable to finish the mission. so if you have to go through a tunnel first it will point to the tunnel").
    py.cmd tools/mini/pc76.py      (once, after pc74; edits D:/crust-rush/godot/scripts/main.gd; reads source/build/sb_cost.json)
main.gd SB_COST (the same table as the web's), _sb_route_next(sb, to): a shortest-path search over (place, gate you came in by) from the
kart (its live gates here: along the lap on a road place, else straight across x1.15) to the destination's start line, worked out
twice a second; _sb_next_hop (fewest places) only when the table has no entry.
"""
import json
G = 'D:/crust-rush/godot/scripts/'
C = json.load(open('D:/crust-rush/source/tools/neon/sb_cost.json', encoding='utf-8'))


def rep(f, a, b, n=1):
    p = G + f
    s = open(p, encoding='utf-8', newline='').read()
    assert s.count(a) == n, (f, s.count(a), a[:80])
    s = s.replace(a, b)
    open(p, 'w', encoding='utf-8', newline='').write(s)


rep('main.gd', """var _sb_hops := {}
""", """var _sb_hops := {}
## (pc76, web SB_COST from tools/neon/sbcost.py) each place's driving distances: "a>b" from the gate to a to the gate to b, "@flag" the start line
const SB_COST := """ + json.dumps(C, separators=(', ', ': ')) + """
var _sb_rt := {}


## (pc76, web sbRouteNext) the first place on the quickest drivable way to `to`'s start line; "" when the table does not know it
func _sb_route_next(sb, to: String) -> String:
	var now := Time.get_ticks_msec()
	if not _sb_rt.is_empty() and String(_sb_rt["to"]) == to and String(_sb_rt["reg"]) == String(sb.id) and now - int(_sb_rt["t"]) < 500:
		return String(_sb_rt["v"])
	var v := ""
	if SB_COST.has(to):
		var T0: TrackData = T
		var road := String(sb.kind) == "road"
		var kj := 0
		var cum: Array = []
		if road:
			cum.append(0.0)
			for j in range(1, T0.N + 1):
				cum.append(float(cum[j - 1]) + Vector2(T0.px[j % T0.N] - T0.px[j - 1], T0.py[j % T0.N] - T0.py[j - 1]).length())
			var bd := 1e18
			for j in range(0, T0.N, 2):
				var d := Vector2(T0.px[j] - kart.x, T0.py[j] - kart.y).length_squared()
				if d < bd:
					bd = d
					kj = j
		var Q: Array = []
		for g in sb.gates:
			var c := 0.0
			if road and int(g.get("j", -1)) >= 0:
				var L: float = cum[T0.N]
				var dd: float = absf(float(cum[kj]) - float(cum[int(g["j"])]))
				c = minf(dd, L - dd)
			else:
				c = Vector2(float(g["x"]) - kart.x, float(g["z"]) - kart.y).length() * 1.15
			Q.append({"r": String(g["to"]), "f": String(sb.id), "c": c, "first": String(g["to"])})
		var seen := {}
		var best := {}
		while not Q.is_empty():
			Q.sort_custom(func(a, b): return float(a["c"]) < float(b["c"]))
			var q: Dictionary = Q.pop_front()
			var key := String(q["r"]) + "|" + String(q["f"])
			if seen.has(key):
				continue
			seen[key] = true
			if not best.is_empty() and float(q["c"]) >= float(best["c"]):
				break
			var T: Dictionary = SB_COST.get(String(q["r"]), {})
			if String(q["r"]) == to:
				var c2 := float(q["c"]) + float(T.get(String(q["f"]) + ">@flag", 0.0))
				if best.is_empty() or c2 < float(best["c"]):
					best = {"c": c2, "first": q["first"]}
				continue
			for kk in T:
				var ab := String(kk).split(">")
				if ab[0] != String(q["f"]) or ab[1] == "@flag" or not Sandbox.has_place(ab[1]):
					continue
				Q.append({"r": ab[1], "f": String(q["r"]), "c": float(q["c"]) + float(T[kk]), "first": q["first"]})
		if not best.is_empty():
			v = String(best["first"])
	_sb_rt = {"to": to, "reg": String(sb.id), "t": now, "v": v}
	return v
""")
rep('main.gd', """		var hop := _sb_next_hop(String(sb.id), to)""", """		var hop := _sb_route_next(sb, to)   # (pc76: the quickest drivable way)
		if hop == "":
			hop = _sb_next_hop(String(sb.id), to)""")
print('pc76 applied')
